# ============================================================================
# 模块：cert_login.py —— 基于国密 SM2 客户端证书的登录接口
# ----------------------------------------------------------------------------
# 文件作用：接收前端上传的 PFX 客户端证书 + 证书口令 + 角色，以"证书"替代
#           "密码"完成身份认证：
#           依次校验 证书格式(口令可打开) → 证书有效期 → 证书链(信任 CA 根)
#           → 从证书 CN 提取用户名并定位账号 → 账户锁定检查 → 提取证书指纹
#           → 签发 JWT 双令牌（访问令牌与证书指纹绑定）。
# 注册路由：POST /user/certLogin（multipart/form-data 上传）
# 涉及的安全/加密机制：
#   1) 国密 SM2 证书体系：证书由 CA 在注册时签发（见 register.py），登录时：
#      verify_certificate_format —— 校验 PFX 格式与私钥口令是否正确；
#      is_certificate_valid      —— 校验证书时间有效性（是否过期）；
#      verify_certificate_chain  —— 以 CA 根证书为信任锚点校验证书链与签名，
#                                    防止使用伪造/自签证书登录；
#   2) 身份绑定：从证书主体 CN 字段解析用户名（注册发证时写入用户名），
#      再与数据库中的 User / Seller 记录对应；
#   3) 证书指纹绑定令牌：extract_cert_thumbprint 提取证书指纹，随
#      access_token 一同签发，形成"证书 + 令牌"绑定；
#   4) 账户锁定检查 + IP 级限流（rate_limit：每 IP 每分钟最多 100 次）。
# 调用的工具函数：
#   ca_client_crt_yanzheng.verify_certificate_format / is_certificate_valid /
#   verify_certificate_chain / extract_cn_from_cert / extract_cert_thumbprint、
#   db.get_user_by_username / get_seller_by_seller_name / is_user_locked、
#   auth.generate_access_token / generate_refresh_token。
#   信任链校验所用的 CA 根证书路径：config.ca_path.ca_sm2_cert_path。
# ============================================================================
# app/api/v1/cert_login.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.middleware import rate_limit
from app.utils import db, auth,ca_client_crt_yanzheng
from config.ca_path import ca_sm2_cert_path

user = Blueprint('cert_login', __name__)


# ----------------------------------------------------------------------------
# build_response：统一的 JSON 响应封装工具函数（本蓝图内复用）
# 参数：code=业务返回码（0 成功 / 非 0 各类业务错误）、message=提示文字、
#       error=错误类型、data=业务数据、status=HTTP 状态码（默认 200）。
# 返回：Flask Response，响应体统一附带 UTC 时间戳 time 字段。
# ----------------------------------------------------------------------------
def build_response(code, message='', data=None, error=None, status=200):
    payload = {
        'code': code,
        'message': message,
        'error': error,
        'data': data,
        'time': datetime.utcnow().isoformat() + 'Z'
    }
    return jsonify(payload), status


# ----------------------------------------------------------------------------
# cert_login：证书登录视图函数（POST /user/certLogin）
# 处理流程：读取上传证书与口令 → 格式/有效期/信任链三级证书校验 →
#           解析 CN 定位账号 → 锁定状态检查 → 提取证书指纹 →
#           签发绑定证书指纹的 JWT 双令牌。
# 入参（multipart/form-data）：
#     cert     —— 上传的 PFX 客户端证书文件
#     password —— PFX 私钥保护口令
#     role     —— 期望登录的身份角色(user/seller)
# 返回码：0=登录成功(含双令牌与证书指纹)；400 未上传证书；401 证书格式/口令
#         错误；402 证书过期；403 证书链校验失败；404 账号不存在；
#         423 账户锁定；500 校验过程内部异常。
# 说明：证书登录属于"无密码登录"，安全性建立在 私钥保密 + CA 信任链校验 +
#       访问令牌绑定证书指纹 三层之上。
# ----------------------------------------------------------------------------
@user.route('/user/certLogin', methods=['POST'])
@rate_limit(max_requests=100, window_seconds=60, per_ip=True)
def cert_login():
    # 证书登录请求体为 multipart/form-data：cert 为 PFX 证书文件字段
    # 获取上传的证书文件
    cert = request.files['cert']
    cert_file = cert.read()                          # 读取证书文件的二进制内容
    password = request.form.get('password')          # PFX 私钥保护口令
    role = request.form.get('role')                  # 期望登录的角色(user/seller)

    if not cert_file:
        # 文件内容为空：说明未正确上传证书
        return build_response(
            code=400,
            error='参数缺失',
            message='请上传证书文件',
            status=400
        )

    try:
        # —— 第一级：证书格式校验 ——
        # 尝试用口令解析 PFX：格式不合法或口令错误都会在此返回 401
        # 验证证书
        if not ca_client_crt_yanzheng.verify_certificate_format(cert_file, password):
            return build_response(
                code=401,
                error='格式认证失败',
                message='证书格式验证失败',
                status=401
            )

        # —— 第二级：证书有效期校验 ——
        # 检查证书时间是否在有效期内，过期证书一律拒绝登录
        if not ca_client_crt_yanzheng.is_certificate_valid(cert_file,password):
            return build_response(
                code=402,
                error='时间认证失败',
                message='证书过期',
                status=402
            )

        # —— 第三级：证书信任链校验 ——
        # 读取 CA 根证书(公钥证书)作为信任锚点
        with open(ca_sm2_cert_path, 'rb') as f:
            root_ca_pem = f.read()
        # 用 CA 根证书公钥验证客户端证书的签发链与签名，防止伪造/冒用证书
        if not ca_client_crt_yanzheng.verify_certificate_chain(cert_file,root_ca_pem,password):
            return build_response(
                code=403,
                error='信任链认证失败',
                message='证书信任链验证失败',
                status=403
            )


        # 提取用户名
        # 从证书主体 CN 字段解析用户名（用户名在注册发证时写入证书主体）
        username = ca_client_crt_yanzheng.extract_cn_from_cert(cert_file,password,role)
        # 先检查用户是否存在
        user_ = db.get_user_by_username(username)
        if not user_:
            # 再检查商家是否存在
            user_ = db.get_seller_by_seller_name(username)

        # User / Seller 都未命中：证书合法但账号不存在，拒绝登录
        if not user_:
            return build_response(
                code=404,
                error='认证失败',
                message=f'不存在用户{username}',
                status=404
            )

        # 锁定检查：被锁定账号即使持有合法证书也拒绝登录
        if db.is_user_locked(user_):
            return build_response(
                code=423,
                error='认证失败',
                message='账户已经锁定',
                status=423
            )
        # 提取证书指纹：用于绑定到访问令牌，标识本次登录所使用的证书
        cert_thum = ca_client_crt_yanzheng.extract_cert_thumbprint(cert_file, password)

        # 生成 JWT 令牌
        # 三级校验全部通过：签发双令牌；access_token 携带证书指纹，
        # 后续可校验"证书身份"与令牌的一致性
        access = auth.generate_access_token(user_,cert_thum)
        refresh = auth.generate_refresh_token(user_)

        return build_response(
            code=0,
            message='登录成功',
            data={
                'access_token': access,
                'refresh_token': refresh,
                'user_id': user_.id,
                'username': user_.username,
                'cert_thumbprint': cert_thum,   # 返回证书指纹供前端留存/展示
            }
        )

    except Exception as e:
        # 异常兜底：证书处理中的任何未预期错误统一返回 500
        return build_response(
            code=500,
            error='认证失败',
            message=f'证书验证过程中发生错误: {str(e)}',
            status=500
        )
