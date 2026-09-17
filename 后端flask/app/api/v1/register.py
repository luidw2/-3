# ============================================================================
# 模块：register.py —— 用户注册接口（账号 + 国密 SM2 客户端证书签发）
# ----------------------------------------------------------------------------
# 文件作用：接收前端提交的 用户名/密码/邮箱/角色/PFX证书口令，先做参数与
#           账号唯一性校验，再调用国密 CA 客户端工具为用户签发 SM2 数字
#           证书并打包为 PFX 文件返回给前端下载；证书签发成功后才创建账号
#           （普通用户会自动附带初始化购物车）。
# 注册路由：POST /user/register
# 涉及的安全/加密机制：
#   1) 国密 SM2 客户端证书签发与 PFX 打包（ca_client.generate_client_cert），
#      客户端私钥用用户提供的 pfx_password 保护，服务端不保存证书口令；
#   2) 密码不存明文，仅保存 Bcrypt 哈希（my_bcrypt.bcrypt_password）；
#   3) 用户名格式白名单校验（user_riger_yanzheng.validate_username）与
#      邮箱增强格式校验（email_iii.validate_email_enhanced）；
#   4) 用户名全局唯一性检查（db.username_exists_anywhere，普通用户/商家共用
#      命名空间，防重名）与角色白名单（user / seller）；
#   5) IP 级限流（rate_limit：每 IP 每分钟最多 100 次），防批量恶意注册。
# 调用的工具函数 / 常量：
#   ca_client.generate_client_cert、user_riger_yanzheng.validate_username、
#   email_iii.validate_email_enhanced、db.username_exists_anywhere /
#   create_user / create_cart / create_seller、my_bcrypt.bcrypt_password；
#   CA 相关路径常量来自 config.ca_path（ca_sm2_key_path、ca_sm2_cert_path、
#   client_ext_cnf_test_path）。
# ============================================================================
from flask import Blueprint, request, jsonify, send_file
import io
from datetime import datetime
from config.ca_path import ca_sm2_key_path, client_ext_cnf_test_path, ca_sm2_cert_path

from app.middleware import rate_limit
from app.utils import db, email_iii, my_bcrypt, user_riger_yanzheng
from app.utils import ca_client




user = Blueprint('register', __name__)


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
# register：用户注册视图函数（POST /user/register）
# 处理流程：解析并清洗参数 → 必填项与格式校验 → 用户名唯一性与角色校验 →
#           国密 CA 签发 SM2 客户端证书(PFX) → 证书就绪后创建账号 →
#           把 .pfx 文件以附件形式返回前端下载。
# 入参（JSON body）：username 用户名、password 密码、email 邮箱、
#       role 角色(user/seller)、certPassword PFX 私钥保护口令
# 返回：成功时以 send_file 返回 application/x-pkcs12 类型的 .pfx 下载文件；
#       失败时返回：400 参数缺失 / 422 用户名格式不合法 / 423 邮箱格式不合规 /
#       403 用户名已存在 / 440 角色非法 / 500 证书生成失败。
# 设计说明：采用"先发证、后建号"的顺序——证书生成失败时不建账号，避免出现
#           无证书的"孤儿账号"；证书口令仅用于保护客户端私钥。
# ----------------------------------------------------------------------------
@user.route('/user/register', methods=['POST'])
@rate_limit(max_requests=100, window_seconds=60, per_ip=True)
def register():
    # 解析注册请求的 JSON 请求体
    data = request.get_json() or {}

    name = data.get('username')
    password = data.get('password')
    email_user = data.get('email')
    role = data.get('role')
    #verification_code = data.get('verificationCode')   # 早期邮箱验证码字段（已弃用，见文件尾部注释块）
    pfx_password = data.get('certPassword')             # 用户自定义的 PFX 证书私钥保护口令

    # 文本类字段去除首尾空白，避免误输入空格导致校验或查重失真
    if isinstance(name, str):
        name = name.strip()
    if isinstance(email_user, str):
        email_user = email_user.strip()
    if isinstance(role, str):
        role = role.strip()

    # 必填项校验：用户名、密码、邮箱、角色、证书口令缺一不可
    # 注：下方提示文案沿用了早期"验证码"表述，实际必填项为 certPassword(证书口令)，
    #     仅提示文案未同步更新，不影响任何校验逻辑。
    if not all([name, password, email_user,role,pfx_password]):
        return build_response(
            code=400,
            error='参数缺失',
            message='邮箱、用户名、密码和验证码均为必填项',
            status=400
        )

    # 用户名格式白名单校验：4-20 位、英文字母开头、仅含字母/数字/下划线
    if not user_riger_yanzheng.validate_username(name):
        return build_response(
            code=422,
            error='注册失败',
            message='用户名必须为4-20位，并且以英文字母开头，只能包含字母、数字和下划线',
            status=422
        )

    # 邮箱格式校验（email_iii.validate_email_enhanced 内部按增强规则匹配）
    if not email_iii.validate_email_enhanced(email_user):
        return build_response(
            code=423,
            error='注册失败',
            message='邮箱格式不合规',
            status=423
        )

    # 用户名全局唯一性检查：普通用户与商家共用命名空间，重名一律拒绝
    if db.username_exists_anywhere(name):
        return build_response(
            code=403,
            error='用户名已经存在',
            message='用户名已经存在',
            status=403
        )
    # 角色白名单：只接受 'user'(普通用户) 或 'seller'(商家)
    elif role not in ['user', 'seller']:
        return build_response(
            code=440,
            error='注册失败',
            message='没有此种角色',
            status=440
        )


    # —— 第二步：国密 SM2 客户端证书签发 ——
    # 以 CA 根证书与 CA 私钥为签发凭证、参照客户端证书扩展配置文件，为
    # 用户签发 SM2 客户端数字证书并打包为 PFX（私钥受 pfx_password 保护）；
    # 签发/打包过程中抛出的任何异常都在下方 except 分支捕获并返回 500。
    try:
        pfx_cert_data = ca_client.generate_client_cert(
            name,                 # 证书主体信息取自用户名
            ca_sm2_cert_path,     # CA 根证书文件路径（签发者证书）
            ca_sm2_key_path,      # CA 私钥文件路径（签发签名用，仅服务端持有）
            client_ext_cnf_test_path,   # 客户端证书扩展配置（如用途/密钥用法）
            200,                  # 证书相关数值参数（如有效期等，具体含义见 ca_client 实现）
            pfx_password,         # 生成 PFX 时保护私钥的口令
            role,                 # 证书中携带的角色属性
        )
        # 4. 打包为 PFX（使用用户提供的密码）
    except Exception as e:
        return build_response(
            code=500,
            error='证书生成失败',
            message=str(e),
            status=500
        )

    # 生成结果为空说明签发失败，中止注册（发证失败即不建号）
    # 检查证书生成是否成功
    if pfx_cert_data is None:
        return build_response(
            code=500,
            error='证书生成失败',
            message='证书生成失败',
            status=500
        )

    # —— 第三步：证书就绪后创建账号 ——
    # 密码仅做 Bcrypt 哈希后入库，任何环节都不保存明文
    # 证书生成成功后，再创建用户
    hashed = my_bcrypt.bcrypt_password(password)

    if role == 'user':
        # 普通用户：写入 user 表，成功后为其初始化一个专属购物车
        user_id = db.create_user(name, hashed)
        if user_id:
            print(f"用户 {name} 注册成功，ID: {user_id}")
            # 创建购物车
            cart = db.create_cart(user_id)
            if cart:
                print(f"购物车创建成功")
            else:
                print(f"购物车创建失败，用户ID: {user_id}")
    elif role == 'seller':
        # 商家：写入 seller 表（商家账号不创建购物车）
        db.create_seller(name, hashed)
        print(f"卖家 {name} 注册成功")

    # 返回 .pfx 证书文件流给前端下载：以附件方式保存为 <用户名>.pfx
    return send_file(
        io.BytesIO(pfx_cert_data),       # 内存中的 PFX 二进制数据
        as_attachment=True,              # 触发浏览器"附件下载"行为
        download_name=f'{name}.pfx',     # 下载文件名
        mimetype='application/x-pkcs12'  # PKCS#12 证书容器的 MIME 类型
    )

# ----------------------------------------------------------------------------
# 说明：以下被 ''' ''' 包裹的是早期"邮箱验证码"注册流程的代码片段（已废弃），
#       当前注册方案改为"国密证书签发 + 直接建号"，此块仅作历史留档参考，
#       不在任何代码路径中执行。
# ----------------------------------------------------------------------------
'''
    try:
        email_iii.validate_verification_code(verification_code)
    except Exception as exc:
        return build_response(
            code=400,
            error='注册失败',
            message=f'验证码无效: {exc}',
            status=400
        )

    if not email_iii.verify_email(email_user, verification_code):
        return build_response(
            code=401,
            error='注册失败',
            message='验证码错误',
            status=401
        )
'''
