# ============================================================================
# 模块：staff_login.py —— 后台账号（管理员 / 审计员）登录接口
# ----------------------------------------------------------------------------
# 文件作用：实现后台账号（staff 表，角色 admin/auditor）的登录认证链路。
#           与前台 user/seller 登录的最大区别：后台账号启用 TOTP 双因素后，
#           登录是"两步"的 —— 第一步密码验证只签发 5 分钟有效的"预登录令牌"
#           (step_token)，第二步必须提供认证器动态码 / 恢复码才能拿到正式 token。
# 注册路由（蓝图 staff_login，挂载于应用根路径）：
#   POST /api/staff/login             第一步：用户名 + 密码
#   POST /api/staff/login/totp        第二步：动态码（含时间窗容差与防重放）
#   POST /api/staff/login/recovery    第二步（备选）：一次性恢复码
#   GET  /api/staff/me                当前后台账号信息（前端刷新恢复登录态）
#   POST /api/staff/logout            退出登录（前端清除 token）
# 涉及的安全机制：
#   1) bcrypt 密码比对 + failed_attempts/lock_until 防暴力破解（staff 专用计数函数）；
#   2) TOTP 时间窗(±1 步)失步处理 + last_totp_step 防重放（见 login/totp 视图）；
#   3) 一次性恢复码（哈希入库、命中即删）；
#   4) 登录失败/成功均写审计日志（security_event 表），供审计员查询。
# 说明：后台账号暂不签发 refresh token（刷新令牌表按 user/seller 设计），
#       如需长时间会话可后续扩展 staff_refresh_token 表。
# ============================================================================
import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from flask import Blueprint, request, jsonify, g

from app.middleware import rate_limit, jwt_auth_required, staff_required
from app.utils import db, my_bcrypt, auth, totp, audit_log
# TOTP secret 的解密函数定义在 staff_totp.py（加密落库与解密读取放在同一处维护）
from app.api.staff.staff_totp import decrypt_totp_secret

user = Blueprint('staff_login', __name__)

# step_token（预登录令牌）有效期：分钟。密码通过后须在该时间内完成第二步
STEP_TOKEN_TTL_MIN = 5


# ----------------------------------------------------------------------------
# build_response：统一的 JSON 响应封装（与 v1 各蓝图一致）
# code=0 表示业务成功；非 0 为业务错误码；status 为 HTTP 状态码
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
# 签发"预登录"令牌（第二步 TOTP/恢复码 专用的临时凭证）
# 作用：第一步密码验证通过后签发；只允许访问 /api/staff/login/totp 与
#       /api/staff/login/recovery，5 分钟后自动失效，避免密码通过后
#       直接下发正式 token 造成"绕过 TOTP"。
# 参数：staff 后台账号对象
# 返回：JWT 字符串（typ='step'）
# ----------------------------------------------------------------------------
def _issue_step_token(staff):
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(staff.id),
        'username': staff.username,
        'role': staff.role,
        'typ': 'step',  # 类型区分：避免把 step_token 当 access token 用
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(minutes=STEP_TOKEN_TTL_MIN)).timestamp()),
        'jti': secrets.token_urlsafe(16),
    }
    return jwt.encode(payload, auth.JWT_SECRET, algorithm=auth.JWT_ALG)


def _verify_step_token(step_token):
    """校验预登录令牌：验签 + 过期 + 类型必须为 step；失败返回 None"""
    try:
        payload = jwt.decode(step_token, auth.JWT_SECRET, algorithms=[auth.JWT_ALG])
        if payload.get('typ') != 'step':
            return None
        return payload
    except Exception:
        return None


def _issue_access_token(staff, totp_ok: bool = False):
    """为后台账号签发正式 access token。
    复用 auth.generate_access_token：它按鸭子类型读取 id/username/role/
    permissions 属性，Staff 对象字段一致，可直接使用；密码登录无证书，
    cert_thumbprint 传 None。
    totp_ok=True 表示该令牌是"密码 + TOTP/恢复码"**两步验证通过后**签发的：
    admin/auditor 接口只接受 totp_ok=True 的令牌（见 permissions.py 的
    admin_required / auditor_required）；仅凭密码（含未绑定直登）签发的令牌
    totp_ok=False，无法使用任何后台功能，只能走绑定流程。"""
    return auth.generate_access_token(staff, None, extra_claims={'totp_ok': totp_ok})


# ----------------------------------------------------------------------------
# 第一步登录：用户名 + 密码（POST /api/staff/login）
# 入参：username、password
# 返回：need_totp=True  → 需第二步，携带 step_token；
#       need_totp=False → 账号尚未绑定 TOTP，直接返回 access_token
#                        （前端应引导进入绑定流程，totp_setup_required=True）
# ----------------------------------------------------------------------------
@user.route('/api/staff/login', methods=['POST'])
@rate_limit(max_requests=30, window_seconds=60, per_ip=True)
def staff_login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password')

    if not username or not password:
        return build_response(400, '用户名和密码不能为空', error='参数缺失', status=400)

    # 定位后台账号（只查 staff 表）
    staff = db.get_staff_by_username(username)
    # 账号不存在与密码错误统一提示，避免向攻击者暴露"账号是否存在"（防枚举）
    if not staff:
        return build_response(401, '用户名或密码错误', status=401)
    if not staff.is_active:
        return build_response(401, '账号已被禁用', status=401)
    # 连续失败锁定检查（复用通用判断：只读 lock_until 字段）
    if db.is_user_locked(staff):
        return build_response(423, '账号已锁定，请稍后再试', status=423)
    # bcrypt 密码比对：失败则累计失败次数（达阈值自动锁定）并写审计
    if not my_bcrypt.compare_password(staff.password, password):
        db.record_staff_failed_login(staff)
        audit_log.log_audit('STAFF_LOGIN_FAILED', username, f'后台账号密码错误: {username}')
        return build_response(401, '用户名或密码错误', status=401)

    # 密码通过：清零失败计数
    db.reset_staff_failed_login(staff)

    if staff.totp_enabled:
        # —— 已绑定 TOTP：只发预登录令牌，第二步校验动态码后才发正式 token ——
        audit_log.log_audit('STAFF_LOGIN_STEP1', username, f'后台账号密码通过，等待TOTP: {username}')
        return build_response(0, '密码验证通过，请输入动态码', data={
            'need_totp': True,
            'username': staff.username,
            'role': staff.role,
            'step_token': _issue_step_token(staff),
        })

    # —— 尚未绑定 TOTP：直接登录成功，但前端应强制先走 TOTP 绑定 ——
    audit_log.log_audit('STAFF_LOGIN_OK', username, f'后台账号登录成功(未绑定TOTP): {username}')
    return build_response(0, '登录成功', data={
        'need_totp': False,
        'totp_setup_required': True,  # 提示前端：该账号还差 TOTP 绑定
        'access_token': _issue_access_token(staff),
        'username': staff.username,
        'role': staff.role,
    })


# ----------------------------------------------------------------------------
# 第二步登录：TOTP 动态码（POST /api/staff/login/totp）
# 入参：step_token（第一步返回）、code（认证器当前 6 位动态码）
# 安全点：
#   1) 失步处理：verify_totp(window=1) 容忍前后 ±1 个时间步（约 ±30 秒）；
#   2) 防重放：动态码命中后返回其"时间步步号"，只接受比该账号上次成功步号
#      (last_totp_step) 更新的步 —— 同一时间步的动态码只能成功使用一次；
#   3) 校验失败/重放均写审计日志。
# ----------------------------------------------------------------------------
@user.route('/api/staff/login/totp', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60, per_ip=True)
def staff_login_totp():
    data = request.get_json() or {}
    step_token = data.get('step_token')
    code = (data.get('code') or '').strip()

    # 预登录令牌校验：无效/过期则要求重新走第一步
    payload = _verify_step_token(step_token)
    if not payload:
        return build_response(401, '预登录凭证无效或已过期，请重新登录', status=401)
    if not code or not code.isdigit() or len(code) != 6:
        return build_response(400, '动态码格式不正确（应为6位数字）', error='参数错误', status=400)

    staff = db.get_staff_by_id(int(payload['sub']))
    if not staff or not staff.is_active:
        return build_response(401, '账号不存在或已被禁用', status=401)
    if not staff.totp_enabled or not staff.totp_secret_enc:
        return build_response(400, '该账号未绑定TOTP，请先完成绑定', status=400)

    # 解密库中存储的 TOTP secret，再做时间窗校验
    secret = decrypt_totp_secret(staff.totp_secret_enc)
    ok, hit_step = totp.verify_totp(secret, code, window=1)
    if not ok:
        audit_log.log_audit('STAFF_TOTP_FAILED', staff.username, '后台登录动态码验证失败')
        return build_response(401, '动态码错误', status=401)

    # 防重放：命中步号必须严格大于历史成功步号
    if staff.last_totp_step is not None and hit_step <= staff.last_totp_step:
        audit_log.log_audit('STAFF_TOTP_REPLAY', staff.username,
                              f'后台登录动态码重放被拒绝 step={hit_step}')
        return build_response(401, '动态码已使用，请稍后重试', status=401)

    # 记录成功步号（audit=False：避免高频 STAFF_UPDATE 刷审计，登录成功审计见下）
    db.update_staff(staff.id, last_totp_step=hit_step, audit=False)
    audit_log.log_audit('STAFF_LOGIN_OK', staff.username, '后台账号登录成功(TOTP通过)')
    # totp_ok=True：两步验证通过，授予完整后台功能
    return build_response(0, '登录成功', data={
        'access_token': _issue_access_token(staff, totp_ok=True),
        'username': staff.username,
        'role': staff.role,
    })


# ----------------------------------------------------------------------------
# 第二步登录（备选）：一次性恢复码（POST /api/staff/login/recovery）
# 用途：认证器不可用（手机丢失等）时，用绑定时下发的 10 个恢复码之一登录。
# 安全点：恢复码只以 SHA-256 哈希入库，命中后立即从列表删除 —— 每个恢复码
#         只能用一次；使用成功写 RECOVERY_USED 审计，并提示尽快重新绑定。
# ----------------------------------------------------------------------------
@user.route('/api/staff/login/recovery', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60, per_ip=True)
def staff_login_recovery():
    data = request.get_json() or {}
    step_token = data.get('step_token')
    code = (data.get('code') or '').strip().upper()

    payload = _verify_step_token(step_token)
    if not payload:
        return build_response(401, '预登录凭证无效或已过期，请重新登录', status=401)
    if not code:
        return build_response(400, '恢复码不能为空', error='参数错误', status=400)

    staff = db.get_staff_by_id(int(payload['sub']))
    if not staff or not staff.is_active:
        return build_response(401, '账号不存在或已被禁用', status=401)

    # 从库中取出恢复码哈希列表并校验
    hashes = json.loads(staff.recovery_hashes) if staff.recovery_hashes else []
    if not totp.verify_recovery_code(code, hashes):
        audit_log.log_audit('STAFF_RECOVERY_FAILED', staff.username, '恢复码校验失败')
        return build_response(401, '恢复码错误', status=401)

    # 一次性：移除本次使用掉的恢复码哈希
    code_hash = hashlib.sha256(code.encode('utf-8')).hexdigest()
    remaining = [h for h in hashes if h != code_hash]
    db.update_staff(staff.id, recovery_hashes=json.dumps(remaining), audit=False)
    audit_log.log_audit('RECOVERY_USED', staff.username, '使用恢复码登录成功')
    # totp_ok=True：恢复码本身即"第二因素"，授予完整后台功能
    return build_response(0, '登录成功，请尽快重新绑定TOTP', data={
        'access_token': _issue_access_token(staff, totp_ok=True),
        'username': staff.username,
        'role': staff.role,
    })


# ----------------------------------------------------------------------------
# 当前后台账号信息（GET /api/staff/me）
# 用途：前端刷新页面后凭 token 恢复登录态（路由守卫在 /admin*、/auditor* 下
#       调用它，而不是 user/seller 的 /user/profile —— 账号体系不同）
# 权限：jwt 认证 + 管理员/审计员（staff_required）
# ----------------------------------------------------------------------------
@user.route('/api/staff/me', methods=['GET'])
@jwt_auth_required
@staff_required
def staff_me():
    staff = db.get_staff_by_id(g.user.id)
    if not staff:
        return build_response(404, '账号不存在', status=404)
    return build_response(0, 'ok', data={
        'id': staff.id,
        'username': staff.username,
        'role': staff.role,
        'totp_enabled': staff.totp_enabled,
        'is_active': staff.is_active,
        'created_at': staff.created_at.isoformat() if staff.created_at else None,
    })


# ----------------------------------------------------------------------------
# 退出登录（POST /api/staff/logout）
# 说明：JWT 为无状态令牌，退出登录由前端清除本地 token 完成；
#       本接口只负责写审计留痕，便于"谁在何时退出"可追溯。
# ----------------------------------------------------------------------------
@user.route('/api/staff/logout', methods=['POST'])
@jwt_auth_required
@staff_required
def staff_logout():
    audit_log.log_audit('STAFF_LOGOUT', g.username, f'后台账号退出登录: {g.username}')
    return build_response(0, '已退出登录')
