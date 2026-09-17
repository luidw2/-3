"""
JWT 认证中间件
功能：验证令牌有效性，提取用户信息
防护威胁：未授权访问

保护什么：
- 只允许“持有合法 JWT 令牌”的请求访问受保护接口，拦截伪造令牌、过期令牌、
  以及账号已被删除/禁用却仍拿着旧令牌越权的请求。
怎么工作（无状态认证，答辩按步骤讲）：
- 客户端登录后获得 access token，之后每次请求在 Authorization 请求头
  携带 `Bearer <token>`；
- 本装饰器按五步处理：取请求头 -> 解析 Bearer 格式 -> 验签并判断过期
  (verify_access_token) -> 回查数据库确认账号仍存在且未被禁用 -> 把身份
  信息写入 g 对象；
- 注入的 g.user_id / g.role / g.permissions 随后会被视图函数以及权限、
  限流等其它中间件读取，形成“先认证、后授权”的完整防护链路。
"""

from functools import wraps
from flask import request, jsonify, g
from app.utils import auth
import app.utils.db as db


def jwt_auth_required(f):
    """
    JWT认证装饰器
    验证请求中的JWT令牌，提取用户信息并注入到g对象中

    使用方法：
    @user.route('/protected', methods=['GET'])
    @jwt_auth_required
    def protected_route():
        user_id = g.user_id
        username = g.username
        ...

    参数:
        f: 被装饰的视图函数（由 Flask 路由自动传入）

    何时返回 401（任一条件命中即拒绝，视图函数不会被执行）：
    1. 请求缺少 Authorization 请求头；
    2. Authorization 不是 "Bearer <token>" 格式（无空格分隔，或类型不是 bearer）；
    3. 令牌验签失败 / 被篡改 / 已过期（verify_access_token 返回空值）；
    4. 令牌对应的账号已被删除或 is_active=False（被封禁/注销）。
    认证全部通过时：把用户信息注入 g 对象后调用 f(*args, **kwargs) 并返回其结果。

    与其它装饰器的配合（答辩常被问到）：
    - 应把本装饰器写在角色权限装饰器(seller_required / user_required)的
      “外层（上方）”，保证先执行认证、注入 g.role，再执行角色判断；
      若顺序写反，角色装饰器执行时 g 中还没有 role，接口会被误判为无权限。
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取令牌
        # 补充说明（第 1 步）：Authorization 是 HTTP 标准认证请求头，
        # 本项目约定值为 "Bearer <token>"
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({
                'code': 401,
                'error': '未授权访问',
                'message': '缺少Authorization头部',
                'time': None
            }), 401

        # 检查Bearer格式
        # 补充说明（第 2 步）：按空格把请求头拆成“类型 + 令牌”两段，例如
        # "Bearer eyJhbGciOi..." -> token_type="Bearer", token="eyJhbGciOi..."
        try:
            token_type, token = auth_header.split(' ', 1)
            if token_type.lower() != 'bearer':
                # 类型必须是 bearer（大小写不敏感），其它类型一律视为格式错误
                return jsonify({
                    'code': 401,
                    'error': '未授权访问',
                    'message': '令牌格式错误，应使用Bearer格式',
                    'time': None
                }), 401
        except ValueError:
            # 请求头里没有空格分隔符，说明不是合法的 Bearer 格式
            return jsonify({
                'code': 401,
                'error': '未授权访问',
                'message': 'Authorization头部格式错误',
                'time': None
            }), 401

        # 验证令牌
        # 补充说明（第 3 步）：verify_access_token 内部用服务端密钥校验签名并
        # 检查 exp 过期时间；返回空值即代表“伪造 / 被篡改 / 已过期”，统一按 401 拒绝
        payload = auth.verify_access_token(token)
        if not payload:
            return jsonify({
                'code': 401,
                'error': '未授权访问',
                'message': '令牌无效或已过期',
                'time': None
            }), 401

        # 第 4 步：二次校验账号状态（实现“封禁/注销立即生效”的关键一步）
        # 即使 token 验签通过，账号被删除或禁用(is_active=False)也一律拒绝，
        # 防止改密/封号之后旧令牌仍能继续访问受保护接口
        # 验证用户或卖家是否仍然活跃
        user_id = int(payload.get('sub'))
        role = payload.get('role')

        # 依据令牌里声明的角色回查对应数据表：
        # seller 查卖家表；admin / auditor 查后台 staff 表；其余(user)查用户表。
        # 以数据库最新状态为准（封禁/注销立即生效的关键）
        if role == 'seller':
            user_or_seller = db.get_seller_by_id(user_id)
        elif role in ('admin','auditor'):
            user_or_seller = db.get_staff_by_id(user_id)
        else:
            user_or_seller = db.get_user_by_id(user_id)

        if not user_or_seller or not user_or_seller.is_active:
            return jsonify({
                'code': 401,
                'error': '未授权访问',
                'message': '用户已被禁用',
                'time': None
            }), 401

        # 将用户信息注入到Flask的g对象中，供路由函数使用
        # 补充说明（第 5 步）：g 是 Flask 的“单次请求级”上下文：本次请求内全局可读、
        # 请求结束即销毁，不会在多个请求之间串数据；后续权限装饰器依赖 g.role、
        # 用户维度限流依赖 g.user_id，都由这里统一注入
        g.user_id = user_id
        g.username = payload.get('username')
        g.role = role
        g.permissions = payload.get('perms')
        g.user = user_or_seller
        # totp_ok：令牌签发时是否已完成“密码 + TOTP/恢复码”两步验证（后台账号专用）。
        # 只有两步登录签发的令牌该值为 True；未绑定 TOTP 的账号即使拿到密码登录令牌，
        # 也因 totp_ok=False 无法调用管理/审计接口（见 permissions.admin_required）
        g.totp_ok = bool(payload.get('totp_ok'))

        # 校验全部通过：放行，调用真正的视图函数并原样返回其响应
        return f(*args, **kwargs)

    return decorated_function
