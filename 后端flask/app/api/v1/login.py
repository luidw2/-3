# ============================================================================
# 模块：login.py —— 用户登录接口（账号密码登录）
# ----------------------------------------------------------------------------
# 文件作用：接收前端提交的 用户名 / 密码 / 角色 参数完成身份认证；认证通过后
#           签发 JWT 双令牌（访问令牌 access_token + 刷新令牌 refresh_token），
#           供前端后续请求携带以通过接口鉴权。
# 注册路由：POST /user/login（蓝图 'login'，挂载于应用 /api/v1 前缀下）
# 涉及的安全/加密机制：
#   1) Bcrypt 密码哈希比对（my_bcrypt.compare_password）——密码不以明文落库；
#   2) 登录失败计数与账户锁定（record_failed_login / is_user_locked /
#      reset_failed_login）——连续失败达到阈值自动锁定，抵御在线猜解；
#   3) IP 级限流（rate_limit：每 IP 每分钟最多 100 次请求）——防暴力破解；
#   4) JWT 双令牌签发（auth.generate_access_token / generate_refresh_token）。
# 调用的工具函数：
#   db.get_user_by_username / db.get_seller_by_seller_name（普通用户与商家两表查找）、
#   db.is_user_locked / db.record_failed_login / db.reset_failed_login、
#   my_bcrypt.compare_password、auth.generate_access_token / auth.generate_refresh_token。
# ============================================================================
from flask import Blueprint, request, jsonify
from datetime import datetime

from app.middleware import rate_limit
from app.utils import db, my_bcrypt, auth

user = Blueprint('login', __name__)


# ----------------------------------------------------------------------------
# build_response：统一的 JSON 响应封装工具函数（本蓝图内复用）
# 参数：code    —— 业务返回码（约定 0=业务成功，非 0=各类业务错误码），
#       message —— 给前端展示的提示文字，
#       error   —— 错误类型说明，
#       data    —— 业务数据（成功时携带令牌、用户信息等），
#       status  —— HTTP 状态码（默认 200）。
# 返回：Flask Response，响应体统一附带 UTC 时间戳 time 字段，便于前端排查。
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
# login：账号密码登录视图函数（POST /user/login）
# 处理流程：解析并校验参数 → 定位账号（先查 User 表再查 Seller 表）→
#           锁定状态检查 → 角色一致性检查 → Bcrypt 密码比对 →
#           成功则清零失败计数并签发 JWT 双令牌；失败则累计失败次数。
# 入参（JSON body）：username 用户名、password 密码、role 角色(user/seller)
# 返回码：0=登录成功；400 参数缺失；404 用户不存在；423 账户锁定；
#         429 角色错误；401 密码错误。
# 安全说明：密码错误分支调用 record_failed_login 累计失败次数，配合
#           rate_limit 的 IP 限流共同构成对暴力破解的防护。
# ----------------------------------------------------------------------------
@user.route('/user/login', methods=['POST'])
@rate_limit(max_requests=100, window_seconds=60, per_ip=True)
def login():
    # 注：下方遗留的 """ """ 为早期"表单传参"版本的旧说明（已过时），
    # 新版已改为解析 JSON 请求体，此处保留仅供对照参考、不影响任何逻辑。
    """
    role = request.form.get('role')
    name = request.form.get('name')
    password = request.form.get('pwd')
    :return:
    """
    # 解析前端提交的 JSON 请求体（为空时兜底为空字典），取出登录三要素
    data = request.get_json() or {}
    name = data.get('username')
    password = data.get('password')
    role = data.get('role')

    # 必填项校验：用户名与密码缺一不可，缺失直接返回 400
    if not name or not password:
        return build_response(
            code=400,
            error='参数缺失',
            message='用户名和密码不能为空',
            status=400
        )


    # —— 第一步：定位账号 ——
    # 平台同时存在"普通用户(User)"与"商家(Seller)"两类账号，共用此登录入口；
    # 因此先按用户名查 User 侧，未命中再查 Seller 侧。
    # 先检查用户是否存在
    user_ = db.get_user_by_username(name)
    if not user_:
        # 再检查商家是否存在
        user_ = db.get_seller_by_seller_name(name)
    
    # 两处都未命中：用户名不存在，返回 404
    if user_ is None:
        return build_response(
            code=404,
            error='登录失败',
            message='用户不存在',
            status=404
        )

    # 锁定检查：若此前失败次数达到阈值，账户进入锁定状态，期间拒绝登录
    if db.is_user_locked(user_):
        return build_response(
            code=423,
            error='登录失败',
            message='账户已经锁定',
            status=423
        )

    submitted_role = role

    # 确定用户实际的角色
    # 用 isinstance 判断命中的记录是 User 还是 Seller 模型实例，据此得到
    # 服务端"认定的真实角色"与展示名/ID，供角色比对与签发令牌使用。
    if isinstance(user_, db.User):
        actual_role = user_.role  # 'user'
        display_name = user_.username
        user_id = user_.id
    else:  # Seller 实例
        actual_role = 'seller'
        display_name = user_.username
        user_id = user_.id

    # 检查角色是否匹配
    # 前端提交的角色必须与服务端真实角色一致，防止普通用户以商家身份登录、
    # 绕过不同角色的权限边界（角色不符按登录失败处理）。
    if submitted_role != actual_role:
        return build_response(
            code=429,
            error='登录失败',
            message='角色错误',
            status=429
        )


    # —— 第二步：密码校验与令牌签发 ——
    # Bcrypt 哈希比对：以输入密码计算后与库中哈希比较，一致即通过
    if my_bcrypt.compare_password(user_.password, password):
        # 登录成功：清零历史失败次数（解除失败记录与锁定标记）
        db.reset_failed_login(user_)
        # 签发 JWT 双令牌：access_token 供业务接口鉴权，refresh_token 用于
        # 过期后换新；密码登录无证书，证书指纹参数传 None
        #（"证书 + 令牌"绑定的证书登录见 cert_login.py 模块）
        access = auth.generate_access_token(user_, None)
        refresh = auth.generate_refresh_token(user_)
        # 审计留痕：前台账号登录成功（记录账号、角色与账号ID）
        db.log_security_event('USER_LOGIN_OK', user_.username,
                              f'前台账号登录成功 (role={actual_role}, id={user_id})')
        return build_response(
            code=0,
            message='登录成功',
            data={
                'access_token': access,
                'refresh_token': refresh,
                'user_id': user_.id,
                'username': user_.username,
                'role': user_.role,
            }
        )

    # —— 密码错误分支 ——
    # 记录一次失败（连续失败达阈值将自动锁定账户），并返回 401 密码错误
    db.record_failed_login(user_)
    # 审计留痕：前台账号登录失败（密码错误）
    db.log_security_event('USER_LOGIN_FAILED', user_.username,
                          f'前台账号登录失败：密码错误 (role={actual_role})')
    return build_response(
        code=401,
        error='登录失败',
        message='密码错误',
        status=401
    )
