"""
模块：模拟银行支付 —— 异步回调（callback.py）
==============================================
功能：接收「模拟银行」在用户确认支付后，通过 异步回调 方式推送过来的
      支付结果通知，并更新本地订单状态为已支付(paid)。
      银行端通知采用【数字信封】加密：银行先用商户公钥加密 SM4 会话密钥
      (encrypted_key/iv)，再用该 SM4 密钥加密业务数据 data，
      商户后端收到后用商户 SM2 私钥解开信封、取出 SM4 密钥，再解出明文业务数据。

整体数据流（讲解用）：
  用户在模拟银行页确认支付成功
   → 银行异步 POST /api/pay/callback（本文件，请求体为数字信封密文）
   → ① SM2 私钥解出 SM4 会话密钥  ② SM4 解密业务密文  ③ 解析明文 JSON
   → 校验支付状态为 success → 校验订单存在 → 幂等判断(已 paid 则忽略)
   → 金额比对(银行实扣 == 本地订单金额) → 订单状态置 paid 并 commit
   → 记录安全审计事件(SecurityEvent) → 应答 200 告知银行「已收到」，避免银行重试

设计说明：本回调由银行服务器直接调用（不经过用户浏览器、不要求登录态），
          安全性完全依赖「数字信封解密 + 订单归属查询 + 金额校验 + 幂等判断」。
"""
import json
import os

from flask import Blueprint, request, jsonify,g
from datetime import datetime

from app.middleware import rate_limit
from app.utils import db, my_bcrypt, auth
from app.middleware import jwt_auth_required, user_required, rate_limit

from app.utils import SM2, SM4
from app.utils.db import Session, SecurityEvent,Order

# 创建蓝图：callback 蓝图承载「银行异步回调」接口（银行服务器 → 本项目服务器 的通知）
user = Blueprint('callback', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 商户 SM2 私钥：用于拆开银行发来的数字信封（SM2 非对称解密出 SM4 会话密钥，再解业务密文）
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

# 异步回调路由：银行在用户确认支付后，把加密的支付结果 POST 到本接口。
# 注意：这是「银行服务器 → 本项目服务器」的服务端间通知，不经过用户浏览器，
# 也不需要用户登录态 —— 安全性靠数字信封解密 + 金额校验 + 幂等判断保证。
#异步回调路由
@user.route('/api/pay/callback', methods=['POST'])
@rate_limit(max_requests=100, window_seconds=60, per_ip=True)
def callback():
    """处理模拟银行的「异步支付回调」，解密通知并把本地订单更新为已支付(paid)。

    入参(JSON 请求体，即数字信封的三个密文段，均为十六进制字符串)：
      encrypted_key —— 被 SM2(商户公钥)加密过的 SM4 会话密钥
      iv            —— 被 SM2 加密过的 SM4 初始向量
      data          —— 被 SM4 加密的支付结果密文
    解密后明文 JSON 含：order_id(本系统订单号)/transaction_id(银行流水号)
                        /status(预期 'success' 表示支付成功)/amount(支付金额)/timestamp。
    处理流程：拆数字信封 → 校验 status → 校验订单存在 → 幂等(已 paid 直接忽略)
              → 金额比对 → 订单置 paid 并 commit → 写安全审计事件 → 应答 200。
    应答约定：能「收到并处理完」就尽量回 200 —— 避免银行网关因 5xx 反复重试同一笔通知；
              （若在解密阶段就失败才返回 500 等待银行重试，此时幂等判断保证重试安全）
    """
    try:
            data = request.json  # 接收 JSON 格式的加密参数
            # 1. 解密数字信封，得到支付结果：银行用「商户公钥加密 SM4 会话密钥」做成数字信封，
            #    只有商户 SM2 私钥能拆开 —— 所以第一步是读取商户私钥文件
            with open(MERCHANT_PRIVATE_KEY_PATH, 'r') as f:
                sm2_private_key = f.read()



            # 2. 取出信封的两个密文段并还原为字节：
            #    encrypted_key 是被 SM2 加密的 SM4 会话密钥，iv 是被 SM2 加密的 SM4 初始向量
            sm4_key = bytes.fromhex(data.get('encrypted_key'))
            sm4_iv = bytes.fromhex(data.get('iv'))

            # 3. 拆开信封（非对称解密）：用商户 SM2 私钥解出真正的 SM4 会话密钥与 IV
            SM4_key = SM2.sm2_decrypt(sm2_private_key, sm4_key)
            SM4_iv = SM2.sm2_decrypt(sm2_private_key, sm4_iv)

            # 4. 对称解密业务密文：用解出的 SM4 会话密钥解密 data，得到支付结果的明文
            encrypted_data = bytes.fromhex(data.get('data'))
            plain = SM4.sm4_decrypt(SM4_key, SM4_iv, encrypted_data)

            # 5. 明文是 JSON 字符串 → 解析成字典，得到银行回传的「支付结果」
            result = json.loads(plain.decode('utf-8'))


            # 6. 提取关键字段

            order_id = result['order_id']                 # 商户订单号 → 对应本地订单表的主键 id
            transaction_id = result['transaction_id']     # 银行侧交易流水号（用于对账）
            status = result['status']  # 预期 'success'
            amount = result['amount']                     # 银行实扣金额（字符串，稍后转 int 做比对）
            timestamp=result['timestamp']                 # 银行侧支付时间戳
            print(order_id)
            print(transaction_id)
            print(status)
            print(amount)
            print(timestamp)

            # 支付结果不是 success：无需更新订单，仍应答 200 表示「已收到」，避免银行重试
            if status != 'success':
                print(f"支付状态异常: {status}")
                return build_response(200,'支付状态异常','支付状态异常')

            # 开启数据库会话(Session)：后续的查询订单/更新状态/记审计都在同一会话中完成，
            # with 语句保证会话最终会正常关闭（异常时自动回滚，不会留下半成品数据）
            with Session() as session:
                # 1. 根据 order_id 查询本地订单（order_id 是商户生成的订单号）
                order = session.query(Order).filter_by(id=int(order_id)).first()
                # 本地订单不存在：可能是异常或伪造通知，应答 200 忽略即可
                if not order:
                    print(f"订单不存在: {order_id}")
                    # 返回 200，避免支付网关重试
                    return build_response(200,'未找到订单','order is not found')

                # 2. 幂等处理：如果订单已支付，直接返回
                #    —— 支付网关可能因网络抖动重复推送同一笔回调；订单已是 paid 说明
                #       之前已处理过，这里直接应答成功，防止重复更新造成重复记账等副作用
                if order.status == 'paid':
                    print(f"订单已支付，忽略重复回调: {order_id}")
                    return build_response(200,'重复支付','already paid')

                # 3. 金额校验（防止金额被篡改）：银行实扣金额必须与本地订单金额完全一致，
                #    不一致说明金额被篡改或订单金额在支付期间发生变化 → 拒绝置为已支付
                #    （金额一律以服务端数据库的订单金额为准，不信任回调里的金额直接入账）
                if order.total_price != int(amount):
                    print(f"金额不匹配: 订单金额={order.total_price}, 支付金额={amount}")
                    # 可选：记录异常事件
                    return build_response(200,'金额错误','amount not match')

                # 4. 更新订单状态：订单由 待支付(pending) → 已支付(paid)，
                #    这是「支付成功」在业务侧的最终落库动作（等价真实电商中通知商户收款成功）
                order.status = 'paid'      # 修改 ORM 对象上的状态字段
                session.commit()           # 提交事务：把状态修改持久化到数据库

                # 5. 记录安全事件：向审计表写一条「支付回调成功」记录（含订单号与银行流水号），
                #    便于后续对账、追溯（username 字段此处存放的是订单所属用户ID）
                event = SecurityEvent(
                    event_type='PAY_CALLBACK_SUCCESS',
                    username=str(order.user_id),
                    details=f'订单 {order_id} 支付成功, 交易号 {transaction_id}'
                )
                session.add(event)     # 把审计事件对象加入当前会话
                session.commit()       # 再次提交：让审计记录随事务一并落库

            # 处理完成：应答 200 通知银行「回调已成功处理」，银行不会再重发这笔通知
            print(f"订单支付状态更新成功: {order_id}")
            return build_response(200,'success','success')


    except Exception as e:
            # 兜底：解密/查库/更新任一步出错都进入这里；返回 500 让银行网关稍后重试
            # —— 由于有上面的幂等判断，重试不会造成重复扣款/重复置为已支付
            print(f"异步回调解密失败: {e}")
            # 异常时也要返回响应（支付网关可能根据状态码决定重试）
            return build_response(500,'error',f'error{e}')