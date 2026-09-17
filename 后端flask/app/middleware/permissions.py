"""
角色权限中间件 —— 基于角色的访问控制(RBAC)的“角色判断”环节（授权层）
功能：在已经通过 JWT 认证的前提下，进一步限制路由只允许指定角色访问
防护威胁：越权访问（普通用户调用商家专属接口、商家调用用户专属接口等）

讲解要点（保护什么、怎么工作、如何与视图配合）：
1) 本模块属于“授权层”，本身不校验令牌，只读取 jwt_auth_required 注入到
   g 对象的 role 字段，并与要求的角色字符串做比较；
2) 因此必须与 jwt_auth_required 搭配使用，且认证装饰器应写在角色装饰器的
   外层：先认证（注入 g.role），后授权（比较 g.role），顺序不可颠倒；
3) 判定结果：
   - 未经认证（g 上没有 role 属性）或角色不符 -> 返回 403（权限不足）；
   - 角色匹配 -> 放行，继续执行被装饰的视图函数；
4) 角色字符串约定：'user' = 普通用户，'seller' = 商家（来源为登录/认证时
   写入 token 的 role 声明，见 jwt_auth 中间件对 payload['role'] 的读取）；
5) 后台双因素强制（本次新增）：admin/auditor 接口除角色匹配外，还要求令牌带
   totp_ok=True —— 该声明只在“密码 + TOTP/恢复码”两步登录通过后才写入令牌
   （见 staff_login._issue_access_token）。因此未绑定 TOTP 的账号即使能登录，
   也无法调用任何管理/审计功能（只能访问 me/logout/TOTP 绑定接口）；
   jwt_auth 会把 payload['totp_ok'] 注入 g.totp_ok 供本层读取。
"""

from functools import wraps
from flask import g, jsonify, request
from datetime import datetime
from app.utils import audit_log


def _deny(message: str):
    """统一的 403 拒绝处理：返回 403 JSON，并对已认证用户的越权尝试写审计日志。
    说明：未认证(g 无 username)的访问一般由 jwt_auth 先行拦截，这里仅兜底。"""
    if hasattr(g, 'username'):
        audit_log.log_audit(
            'PERMISSION_DENIED',
            g.username,
            f'越权访问被拒绝: {request.method} {request.path} (role={getattr(g, "role", None)})'
        )
    return jsonify({
        'code': 403,
        'error': '权限不足',
        'message': message,
        'time': datetime.utcnow().isoformat() + 'Z'
    }), 403


def seller_required(f):
    """
    商家权限装饰器
    确保只有商家角色可以访问被装饰的路由

    参数:
        f: 被装饰的视图函数

    返回:
        包装后的视图函数：g.role == 'seller' 时返回原视图函数的结果；
        否则返回 403 JSON（提示“只有商家可以访问此接口”），不进入视图函数。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户角色
        # hasattr 判空：请求若未经过 jwt_auth_required，g 上不会有 role 属性，
        # 此时按“无权限”处理(403)，避免 AttributeError 直接抛给前端；
        # 角色不符时也返回 403，且提示文案不暴露接口内部细节
        if not hasattr(g, 'role') or g.role != 'seller':
            return jsonify({
                'code': 403,
                'error': '权限不足',
                'message': '只有商家可以访问此接口',
                'time': datetime.utcnow().isoformat() + 'Z'
            }), 403
        # 角色匹配：放行，调用真正的视图函数
        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    """
    用户权限装饰器
    确保只有用户角色可以访问被装饰的路由

    参数:
        f: 被装饰的视图函数

    返回:
        包装后的视图函数：g.role == 'user' 时返回原视图函数的结果；
        否则返回 403 JSON（提示“需要用户权限”），不进入视图函数。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户角色
        # 与 seller_required 同理：未认证(g 无 role)或角色不符时统一返回 403
        if not hasattr(g, 'role') or g.role != 'user':
            return jsonify({
                'code': 403,
                'error': '权限不足',
                'message': '需要用户权限',
                'time': datetime.utcnow().isoformat() + 'Z'
            }), 403
        # 角色匹配：放行，调用真正的视图函数
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    管理员权限装饰器
    确保只有管理员角色(role='admin')可以访问被装饰的路由（后台管理接口使用）

    参数:
        f: 被装饰的视图函数

    返回:
        包装后的视图函数：g.role == 'admin' 且已通过 TOTP 两步验证(g.totp_ok=True)
        时返回原视图函数的结果；否则返回 403 JSON，不进入视图函数。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 与 seller_required 同理：未认证(g 无 role)或角色不符时统一返回 403
        if not hasattr(g, 'role') or g.role != 'admin':
            return _deny('需要管理员权限')
        # 双因素强制：只有“密码 + TOTP/恢复码”两步登录签发的令牌才允许使用后台功能。
        # 未绑定 TOTP 的账号（密码直登）即使拿到令牌，此处也一律 403 ——
        # 必须先完成绑定，并用动态码重新登录（见前端绑定页“保存恢复码，去重新登录”）
        if not getattr(g, 'totp_ok', False):
            return _deny('请先完成TOTP绑定，再用“密码+动态码”重新登录')
        # 角色匹配且两步验证通过：放行，调用真正的视图函数
        return f(*args, **kwargs)
    return decorated_function


def auditor_required(f):
    """
    审计员权限装饰器
    确保只有审计员角色(role='auditor')可以访问被装饰的路由（审计日志查看/导出接口使用）

    参数:
        f: 被装饰的视图函数

    返回:
        包装后的视图函数：g.role == 'auditor' 且已通过 TOTP 两步验证(g.totp_ok=True)
        时返回原视图函数的结果；否则返回 403 JSON，不进入视图函数。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 与 seller_required 同理：未认证(g 无 role)或角色不符时统一返回 403
        if not hasattr(g, 'role') or g.role != 'auditor':
            return _deny('需要审计员权限')
        # 双因素强制：未完成 TOTP 两步验证的令牌不允许查看/导出审计日志（同 admin_required）
        if not getattr(g, 'totp_ok', False):
            return _deny('请先完成TOTP绑定，再用“密码+动态码”重新登录')
        # 角色匹配且两步验证通过：放行，调用真正的视图函数
        return f(*args, **kwargs)
    return decorated_function


def staff_required(f):
    """
    后台账号通用权限装饰器（管理员或审计员均可访问）
    说明：/api/staff/me、TOTP 绑定等接口对管理员(admin)与审计员(auditor)
          同时开放。若分别用 admin_required / auditor_required 会互相拦掉
          另一半角色，因此提供"admin 或 auditor"的复合判断。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'role') or g.role not in ('admin', 'auditor'):
            return _deny('需要后台账号权限')
        # 角色匹配：放行
        return f(*args, **kwargs)
    return decorated_function