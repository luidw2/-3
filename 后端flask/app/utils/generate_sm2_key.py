import os
import SM2

# =============================================================================
# 脚本：初始化/持久化“商户 SM2 公私钥对”
# -----------------------------------------------------------------------------
# 在项目中的用途（依据后端真实调用点）：
#   支付相关接口需要读取商户 SM2 私钥做签名与数字信封解密——
#     - app/api/v1/pay.py：读取 certs/sm2_key/merchant_private.pem 做支付链接签名；
#     - app/api/v1/callback.py、pay_return.py：读取同一私钥解密银行回传内容。
#   因此密钥必须持久化到磁盘且长期保持不变：本脚本负责一次性生成并落盘。
# -----------------------------------------------------------------------------
# 运行方式：在 app/utils 目录下直接执行 `python generate_sm2_key.py`。
# 幂等逻辑：只要私钥或公钥任一文件不存在，就重新生成一对完整密钥并写入；
#           若两个文件都已存在则直接跳过，避免重复覆盖旧密钥
#           （旧密钥一旦被覆盖，之前签发的支付链接将无法再被验证）。
# =============================================================================

# 私钥/公钥的落盘路径：相对本脚本所在目录，指向后端根目录下的 certs/sm2_key/
PRIVATE_PATH = "../certs/sm2_key/merchant_private.pem"
PUBLIC_PATH = "../certs/sm2_key/merchant_public.pem"

if not os.path.exists(PRIVATE_PATH) or not os.path.exists(PUBLIC_PATH):
    # 调用 SM2.py 中的封装：由 OpenSSL 生成 SM2 公私钥对，
    # 返回 (私钥PEM, 公钥PEM) 两段文本字符串
    sk, pk = SM2.generate_sm2_keypair()
    # certs/sm2_key 目录可能尚不存在：先递归创建；
    # exist_ok=True 表示目标目录已存在时也不报错
    os.makedirs(os.path.dirname(PRIVATE_PATH), exist_ok=True)
    # 以文本模式写入 PEM 格式的私钥与公钥文件
    with open(PRIVATE_PATH, 'w') as f:
        f.write(sk)
    with open(PUBLIC_PATH, 'w') as f:
        f.write(pk)