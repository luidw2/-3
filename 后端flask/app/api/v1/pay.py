"""
模块：模拟支付 —— 支付链接生成（pay.py）
==========================================
功能：本模块是「模拟银行支付」教学流程在商户侧的第一步：
      用户在前端确认支付一笔订单时，后端读取【商户 SM2 私钥】，
      对「订单号|金额|商户号|时间戳」生成 SM2 数字签名，
      拼装出指向本机模拟银行(localhost:8080/pay)的支付链接 pay_url 返回给前端，
      前端浏览器跳转该链接，由「模拟银行」完成用户确认支付的动作。

整体数据流（讲解用）：
  前端点支付 → POST /api/pay/prepare（本文件）
    → 校验订单归属与状态(pending)
    → 用商户私钥 SM2 签名，生成带签名的 pay_url
    → 前端 location 跳转到模拟银行  http://localhost:8080/pay?order_id=...&sign=...
    → 用户在「银行」页确认支付
    → ① 银行异步回调本项目 /api/pay/callback（callback.py：解密数字信封、订单置 paid）
    → ② 银行把用户浏览器重定向回 /pay/return（pay_return.py：渲染成功/失败结果页）
相关模块：app/api/v1/callback.py（异步回调）、app/api/v1/pay_return.py（同步回跳页）。
"""
import time
import os

from flask import Blueprint, request, jsonify, g
from datetime import datetime

from app.middleware import rate_limit
from app.utils import db, my_bcrypt, auth,SM2,SM3
from app.middleware import jwt_auth_required, user_required, rate_limit

# 创建蓝图：pay 蓝图承载「生成支付链接」接口
user = Blueprint('pay', __name__)

# 商户号：本电商在「模拟银行」侧登记的商户标识，
# 银行凭它结合数字签名确认「这笔支付确实由本商户发起」
MERCHANT_ID = "ecommerce_001"

# 获取当前文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 商户 SM2 私钥路径：本项目用该私钥对支付参数签名；
# 配套的商户公钥证书预先提供给「模拟银行」，供银行侧验签使用
MERCHANT_PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "certs", "sm2_key", "merchant_private.pem")

# 模拟银行网关地址（本地开发）：
# 支付流程：prepare_payment 生成带 SM2 签名的支付链接 pay_url，
# 用户浏览器跳转到该地址完成"银行"侧支付；银行随后会异步回调本后端
# 的 /api/pay/callback（见 app/api/v1/callback.py）通知支付结果。
# 银行模拟器同样运行在本机，因此这里直接写 localhost:8080 即可；
# 若银行模拟器里曾配置旧的内网穿透(cpolar)回调域名，请一并改为
# http://127.0.0.1:5000/api/pay/callback
BANK_PAY_URL = "http://localhost:8080/pay"
# 签名原文模板：固定用「订单号|金额|商户号|时间戳」拼出待签名字符串。
# 银行验签时按相同规则重新拼接并校验 SM2 签名 —— 任一字段被篡改都会导致验签失败
SIGN_TEMPLATE = "{order_id}|{amount}|{merchant_id}|{timestamp}"


def build_response(code, message='', data=None, error=None, status=200):
    """统一的接口响应封装函数：保证所有接口返回结构一致，方便前端统一解析。

    :param code:    业务状态码（200 成功 / 400 参数或业务错误 / 404 资源不存在 / 500 服务器异常）
    :param message: 展示给前端的提示信息
    :param data:    成功时的业务数据
    :param error:   失败时的错误说明
    :param status:  HTTP 状态码，默认 200
    :return: (jsonify(payload), status)，Flask 据此输出 JSON 响应
    """
    # 组装统一响应体，并附加服务器 UTC 时间戳便于联调排查
    payload = {
        'code': code,
        'message': message,
        'error': error,
        'data': data,
        'time': datetime.utcnow().isoformat() + 'Z'
    }
    return jsonify(payload), status


@user.route('/api/pay/prepare', methods=['POST'])
@rate_limit(max_requests=100, window_seconds=60, per_ip=True)
@jwt_auth_required
@user_required
def prepare_payment():
    """生成带签名的支付链接（POST /api/pay/prepare）——「模拟支付」流程的第一步。

    作用：前端确认支付某笔订单时调用；后端校验订单归属与状态(pending)后，
          用商户 SM2 私钥对关键交易要素签名，拼出指向「模拟银行」
          (BANK_PAY_URL，本机 localhost:8080/pay) 的支付链接 pay_url 返回前端，
          前端浏览器跳转 pay_url 即进入银行收银台完成支付。
    请求体(JSON)：order_id —— 待支付的本系统订单号
    返回：
      · 200 —— data.pay_url 支付链接（含 order_id/amount/merchant_id/timestamp/sign）
      · 400 —— 缺少 order_id，或订单状态不是待支付(pending)
      · 404 —— 订单不存在或不属于当前用户
      · 500 —— 服务器内部错误（读私钥 / 签名等环节失败）
    安全要点：金额一律取数据库订单金额（不信任前端传入，防止用户改金额）；
             timestamp 用于防重放；签名保证参数在传输过程中不被篡改。
    """
    try:
        # 1. 获取订单ID
        data = request.get_json()
        order_id = data.get('order_id')

        if not order_id:
            return jsonify({'code': 400, 'message': '订单ID不能为空'}), 400

        # 2. 查询订单（验证归属）
        order = db.get_order_detail(order_id, g.user.id)
        if not order:
            return jsonify({'code': 404, 'message': '订单不存在或无权访问'}), 404

        # 3. 检查订单状态：只有 待支付(pending) 的订单才允许发起支付；
        #    已支付或其他状态的订单直接拒绝 —— 防止对同一笔订单重复支付
        if order['status'] != 'pending':
            return jsonify({'code': 400, 'message': '订单状态不允许支付'}), 400

        # 4. 读取商户私钥：签名用商户私钥，验签用商户公钥（已预留在银行侧），
        #    公私钥成对才能保证「签名可验证、商户不可抵赖」
        with open(MERCHANT_PRIVATE_KEY_PATH, 'r') as f:
            private_key = f.read()

        # 5. 生成时间戳（防重放）：时间戳会随签名一起交给银行，
        #    银行可据此校验请求的新鲜度，过期或被重放的支付链接将被拒绝
        timestamp = str(int(time.time()))

        # 6. 构建签名原文：金额取数据库订单的 total_price（不信任前端传值），
        #    订单号/金额/商户号/时间戳按固定模板拼接成待签名串
        sign_raw = SIGN_TEMPLATE.format(
            order_id=str(order_id),
            amount=str(order['total_price']),
            merchant_id=MERCHANT_ID,
            timestamp=timestamp
        )

        # 7. SM2签名：用商户私钥对签名原文签名得到 sign ——
        #    银行用商户公钥验签成功后才受理这笔支付，从而证明：
        #    支付请求确实来自本商户，且参数（尤其是金额）未被中途篡改
        signature = SM2.sm2_sign(private_key, sign_raw.encode('utf-8'))

        # 8. 构建支付URL（GET方式传递参数）：订单号/金额/商户号/时间戳 + 签名(sign)
        #    拼成查询串附在银行地址后 —— 浏览器 GET 跳转即可把参数带给银行收银台，
        #    除 sign 外参数对银行是明文，数据的完整性由 SM2 签名保证
        pay_url = (f"{BANK_PAY_URL}?"
                   f"order_id={order_id}&"
                   f"amount={order['total_price']}&"
                   f"merchant_id={MERCHANT_ID}&"
                   f"timestamp={timestamp}&"
                   f"sign={signature.hex()}")
        print(pay_url)   # 控制台打印支付链接，方便课程演示时观察
        # 返回支付链接给前端：前端拿到 data.pay_url 即可跳转「模拟银行」收银台
        return jsonify({
            'code': 200,
            'message': '支付链接生成成功',
            'data': {
                'pay_url': pay_url,
                'order_id': order_id,
                'amount': order['total_price']
            }
        }), 200

    except Exception as e:
        print(str(e))   # 打印异常便于排查
        # 异常兜底：查询/读私钥/签名任一步出错，统一返回 500
        return jsonify({'code': 500, 'message': '服务器内部错误', 'error': str(e)}), 500
