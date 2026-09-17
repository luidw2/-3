"""
模块：模拟银行支付 —— 同步回跳页面（pay_return.py）
====================================================
功能：用户在「模拟银行」确认支付后，银行除了异步回调本项目(callback.py)之外，
      还会把用户浏览器【重定向(回跳)】到本接口 /pay/return 渲染结果页：
      · 支付成功 → 渲染成功页 pay_success.html（展示订单号/流水号/支付金额/账户余额）；
      · 支付失败或校验不通过 → 渲染失败页 pay_error.html（展示错误原因）。

与 callback.py 的分工（讲解重点）：
  · callback.py  是「银行服务器 → 本项目服务器」的异步通知，真正负责把订单置为 paid；
  · pay_return.py 是「银行 → 用户浏览器」的同步回跳，只做结果展示、不改数据库，
    因为浏览器回跳可以被伪造 —— 订单最终状态一律以异步回调/数据库为准。

数据流：银行重定向 → 本接口（GET/POST 携带数字信封密文）
      → 商户 SM2 私钥拆信封 → SM4 解出支付结果明文 → 校验状态/订单/金额
      → 渲染 pay_success.html 或 pay_error.html 返回给浏览器。
"""
import json
import os

from flask import Blueprint, request, jsonify, g, render_template
from datetime import datetime

from app.middleware import rate_limit
from app.utils import db, my_bcrypt, auth
from app.middleware import jwt_auth_required, user_required, rate_limit

from app.utils import SM2, SM4
from app.utils.db import Session, SecurityEvent,Order

# 创建蓝图：pay_return 蓝图承载「支付结果回跳页」接口
user = Blueprint('pay_return', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 商户 SM2 私钥：用于拆开银行回跳携带的数字信封（SM2 解出 SM4 会话密钥后再解业务密文）
MERCHANT_PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "certs", "sm2_key", "merchant_private.pem")

def build_response(code, message='', data=None, error=None, status=200):
    """统一的接口响应封装函数：保证所有接口返回结构一致，方便前端/网关统一解析。

    :param code:    业务状态码（200 成功 / 400 业务异常 / 500 服务器异常）
    :param message: 提示信息
    :param data:    业务数据
    :param error:   错误说明
    :param status:  HTTP 状态码，默认 200
    :return: (jsonify(payload), status)
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

# 同步「回跳」页面路由：用户确认支付后，模拟银行把浏览器重定向到本地址渲染结果页。
# （与 callback.py 的异步回调不同：本路由走用户浏览器、支持 GET/POST、只展示不改库）
#异步回调路由
@user.route('/pay/return', methods=['GET','POST'])
@rate_limit(max_requests=100, window_seconds=60, per_ip=True)
def pay_return():
    """同步回跳页面接口（GET /pay/return 或 POST /pay/return），渲染支付结果页。

    作用：用户在「模拟银行」确认支付(成功/失败/取消)后，银行把用户浏览器重定向回本接口；
          本接口用商户 SM2 私钥解开随请求带回的数字信封，取出支付结果明文，据此渲染：
          · 支付成功 → pay_success.html（展示订单号/流水号/支付金额/银行账户余额）；
          · 支付失败或校验不通过 → pay_error.html（展示错误原因）。
    取参差异：GET —— 参数在 URL 查询串(request.args)，便于演示时地址栏直接回跳；
              POST —— 参数在表单体(request.form)，对应银行页面「表单自动提交」场景。
    设计说明：与 callback.py 不同，本接口只做「结果展示」，不修改数据库订单状态 ——
              订单真正置为 paid 由异步回调 callback.py 完成；
              因为浏览器回跳可以被伪造，页面展示永远以「异步回调 + 数据库」的最终状态为准。
    """
    try:
            # 银行回跳可能以 GET（浏览器地址栏跳转）或 POST（页面表单自动提交）两种方式
            # 携带加密参数，两种方式参数位置不同，需要按请求方法分别解析
            if request.method == 'GET':
                # GET 请求：从 URL 参数获取
                encrypted_key = request.args.get('encrypted_key')
                iv = request.args.get('iv')
                data = request.args.get('data')
            else:
                 # POST 请求：从表单获取（银行提交的是表单，不是 JSON！）
                encrypted_key = request.form.get('encrypted_key')
                iv = request.form.get('iv')
                data = request.form.get('data')
            # 1. 解密数字信封，得到支付结果：银行用「商户公钥加密 SM4 会话密钥」做成数字信封，
            #    只有商户 SM2 私钥能拆开 —— 所以第一步是读取商户私钥文件
            with open(MERCHANT_PRIVATE_KEY_PATH, 'r') as f:
                sm2_private_key = f.read()



            # 2. 把数字信封的三个密文段(十六进制字符串)还原为字节：
            #    encrypted_key/iv 是被 SM2 加密的 SM4 会话密钥与初始向量
            sm4_key = bytes.fromhex(encrypted_key)
            sm4_iv = bytes.fromhex(iv)

            # 3. 拆开信封（非对称解密）：用商户 SM2 私钥解出真正的 SM4 会话密钥与 IV
            SM4_key = SM2.sm2_decrypt(sm2_private_key, sm4_key)
            SM4_iv = SM2.sm2_decrypt(sm2_private_key, sm4_iv)

            # 4. 对称解密业务密文：用 SM4 会话密钥解出支付结果的明文
            encrypted_data = bytes.fromhex(data)
            plain = SM4.sm4_decrypt(SM4_key, SM4_iv, encrypted_data)

            # 5. 明文是 JSON 字符串 → 解析成字典，得到银行回传的「支付结果」
            result = json.loads(plain.decode('utf-8'))


            # 6. 提取关键字段

            order_id = result['order_id']                 # 商户订单号 → 对应本地订单表主键 id
            transaction_id = result['transaction_id']     # 银行侧交易流水号（成功页展示）
            status = result['status']  # 预期 'success'
            amount = int(result['amount'])               # 支付金额：转成整数便于与订单金额比对
            balance = int(result.get('balance', 0))      # 银行账户余额：成功页展示，缺省按 0
            timestamp=result['timestamp']                # 银行侧支付时间戳
            print(order_id)
            print(transaction_id)
            print(status)
            print(amount)
            print(balance)
            print(timestamp)

            # 支付结果非 success（失败/取消等）→ 渲染错误页，提示具体状态
            if status != 'success':
                print(f"支付状态异常: {status}")
                return render_template('pay_error.html', error_message='支付状态异常')

            # 打开数据库会话，核对本地订单（本接口只做只读校验，不修改订单状态）
            with Session() as session:
                # 1. 根据 order_id 查询本地订单
                order = session.query(Order).filter_by(id=int(order_id)).first()
                # 本地无此订单 → 渲染错误页
                if not order:
                    print(f"订单不存在: {order_id}")
                    return render_template('pay_error.html', error_message='订单不存在')

                # 2. 幂等处理：如果订单已支付，直接返回成功页面
                #    —— 用户可能重复到达本页/银行重复回跳；订单状态以数据库为准，
                #       已 paid 说明异步回调已处理过这笔支付，直接展示成功结果即可
                if order.status == 'paid':
                    print(f"订单已支付，忽略重复回调: {order_id}")
                    return render_template('pay_success.html',
                                           order_id=order_id,
                                           transaction_id=transaction_id,
                                           amount=amount,
                                           balance=balance)

                # 3. 金额校验（防止金额被篡改）：银行回传金额必须等于本地订单金额，
                #    不一致说明数据被篡改或异常 → 渲染错误页而不是成功页
                if order.total_price != amount:
                    print(f"金额不匹配: 订单金额={order.total_price}, 支付金额={amount}")
                    return render_template('pay_error.html', error_message='金额不匹配')



            # 校验通过（订单存在、金额一致）→ 渲染支付成功页。
            # 注意：此处不修改订单状态 —— 真正的置 paid 由 callback.py 的异步回调完成，
            #       本接口仅是给用户浏览器看的「结果展示页」
            return render_template('pay_success.html',
                                   order_id=order_id,
                                   transaction_id=transaction_id,
                                   amount=amount,
                                   balance=balance)


    except Exception as e:
            # 兜底：解密/查库/校验任一步出错 → 渲染通用失败页（不外泄具体异常细节）
            print(f"异步回调解密失败: {e}")
            # 异常时也要返回响应（支付网关可能根据状态码决定重试）
            return render_template('pay_error.html', error_message='支付结果验证失败')
