# ============================================================================
# 模块：profile.py —— 用户个人信息 / 安全 / 会话 / 统计 查询接口集合
# ----------------------------------------------------------------------------
# 文件作用：向已登录用户提供四类"只读"查询：
#   GET /user/profile         —— 个人资料概览（含账户安全状态）；
#   GET /profile/security     —— 账户安全相关信息（失败次数/锁定状态等）；
#   GET /profile/sessions     —— 当前有效会话统计（按"未撤销且未过期的
#                                刷新令牌"计算在线会话数）；
#   GET /profile/statistics   —— 用户统计信息（当前实现含注册天数等占位项）。
# 涉及的安全机制：
#   1) 所有路由均要求 JWT（jwt_auth_required），用户身份由中间件注入 g.user，
#      接口只返回"当前登录用户本人"的数据；
#   2) 响应刻意不返回 password_hash 等敏感字段，只暴露必要资料；
#   3) rate_limit 按用户限流（各接口每用户每分钟 10~30 次），防高频探测；
#   4) 资料访问行为写入安全审计日志（db.log_security_event）。
# 调用的工具函数：db.is_user_locked、db.log_security_event、db.Session /
#                 db.RefreshToken（活跃会话查询）、my_bcrypt（备用导入）。
# ============================================================================
from flask import Blueprint, request, jsonify, g
from app.utils import db, my_bcrypt
from app.middleware import jwt_auth_required, rate_limit
from datetime import datetime

# 创建蓝图
user = Blueprint('profile', __name__)


# ----------------------------------------------------------------------------
# get_profile：个人资料查询（GET /user/profile）
# 作用：返回当前登录用户的公开资料（user_id/username/role/活跃状态/创建与
#       更新时间），并附带账户安全状态（失败次数、是否锁定、解锁时间）。
# 入参：无（身份来自 JWT 中间件注入的 g.user）
# 返回：code=0 + data=user_profile；异常时 code=500。
# 说明：password_hash 等敏感字段不在此返回，防止信息泄露。
# ----------------------------------------------------------------------------
@user.route('/user/profile', methods=['GET'])
@jwt_auth_required
@rate_limit(max_requests=30, window_seconds=60, per_user=True)
def get_profile():
    """
    获取当前登录用户的个人信息
    需要JWT认证
    """
    try:
        # 从g对象中获取用户信息（由JWT中间件注入）
        current_user = g.user

        # 构建用户信息响应（排除敏感信息）
        # 只挑选需要展示的公开字段，密码哈希等敏感字段不进入响应体
        user_profile = {
            'user_id': current_user.id,
            'username': current_user.username,
            'role': current_user.role,
            'is_active': current_user.is_active,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
            'updated_at': current_user.updated_at.isoformat() if current_user.updated_at else None
        }

        # 添加权限信息（如果存在）
        # 若账号带有 permissions 权限集合则一并返回，供前端控制菜单/操作
        if current_user.permissions:
            user_profile['permissions'] = current_user.permissions

        # 添加账户安全状态信息
        # failed_attempts 为累计失败次数；is_locked 反映是否处于锁定状态；
        # lock_until 为自动解锁时间（未锁定则为 None）
        user_profile['security_status'] = {
            'failed_attempts': current_user.failed_attempts or 0,
            'is_locked': db.is_user_locked(current_user),
            'lock_until': current_user.lock_until.isoformat() if current_user.lock_until else None
        }

        # 记录安全事件（可选，用于审计）
        # 每次查看资料写入一条 PROFILE_ACCESS 审计日志
        db.log_security_event(
            event_type='PROFILE_ACCESS',
            username=current_user.username,
            details='用户查看个人信息'
        )

        return jsonify({
            'code': 0,
            'message': '获取用户信息成功',
            'data': user_profile,
            'time': datetime.now()
        })

    except Exception as e:
        # 异常兜底：任何查询错误统一返回 500
        print(f"获取用户信息时出现错误: {e}")
        return jsonify({
            'code': 500,
            'error': '服务器错误',
            'message': '获取用户信息时出现错误',
            'time': datetime.now()
        }), 500


# ----------------------------------------------------------------------------
# get_security_info：账户安全信息查询（GET /profile/security）
# 作用：返回与登录安全相关的状态字段（失败次数、是否锁定、解锁时间）。
#       last_login / password_changed_at 目前为占位(None)，
#       需要后续扩展数据模型记录登录历史后才能填充真实值。
# 入参：无；返回：code=0 + data=security_info；异常时 code=500。
# ----------------------------------------------------------------------------
@user.route('/profile/security', methods=['GET'])
@jwt_auth_required
@rate_limit(max_requests=10, window_seconds=60, per_user=True)
def get_security_info():
    """
    获取用户安全相关信息
    包括登录历史、安全事件等（需要扩展数据库模型）
    """
    try:
        current_user = g.user

        # 这里可以添加获取安全相关信息的逻辑
        # 例如：登录历史、密码修改记录、安全事件等
        # （当前实现为演示骨架，last_login / password_changed_at 为占位）

        security_info = {
            'user_id': current_user.id,
            'username': current_user.username,
            'last_login': None,  # 需要扩展数据库模型来存储这些信息
            'password_changed_at': None,
            'failed_login_attempts': current_user.failed_attempts or 0,
            'account_locked': db.is_user_locked(current_user),
            'lock_until': current_user.lock_until.isoformat() if current_user.lock_until else None
        }

        return jsonify({
            'code': 0,
            'message': '获取安全信息成功',
            'data': security_info,
            'time': datetime.now()
        })

    except Exception as e:
        print(f"获取安全信息时出现错误: {e}")
        return jsonify({
            'code': 500,
            'error': '服务器错误',
            'message': '获取安全信息时出现错误',
            'time': datetime.now()
        }), 500


# ----------------------------------------------------------------------------
# get_active_sessions：当前有效会话查询（GET /profile/sessions）
# 作用：把刷新令牌表(refresh_token)中 属于当前用户 + 未被撤销(revoked=False)
#       + 尚未过期(expires_at > 当前时间) 的记录视为"有效会话"，返回会话数量
#       与每个会话的创建/过期时间，用于展示登录设备/会话概览。
# 入参：无；返回：code=0 + data{active_sessions, sessions}；异常时 code=500。
# 说明：本模块只读查询令牌表，不做任何撤销操作；撤销见 logout/delete。
# ----------------------------------------------------------------------------
@user.route('/profile/sessions', methods=['GET'])
@jwt_auth_required
@rate_limit(max_requests=10, window_seconds=60, per_user=True)
def get_active_sessions():
    """
    获取用户当前活跃的会话信息
    基于refresh_token表查询
    """
    try:
        current_user = g.user

        # 查询用户的活跃刷新令牌
        # 开启一个独立数据库会话，按 用户ID + 未撤销 + 未过期 过滤刷新令牌
        with db.Session() as session:
            active_tokens = session.query(db.RefreshToken).filter(
                db.RefreshToken.user_id == current_user.id,
                db.RefreshToken.revoked == False,
                db.RefreshToken.expires_at > datetime.utcnow()
            ).all()

        # 逐条提取会话的创建/过期时间，组装为列表
        sessions = []
        for token in active_tokens:
            sessions.append({
                'created_at': token.created_at.isoformat() if token.created_at else None,
                'expires_at': token.expires_at.isoformat() if token.expires_at else None
            })

        return jsonify({
            'code': 0,
            'message': '获取会话信息成功',
            'data': {
                'active_sessions': len(sessions),   # 当前有效会话总数
                'sessions': sessions
            },
            'time': datetime.now()
        })

    except Exception as e:
        # 异常兜底：查询出错返回 500
        print(f"获取会话信息时出现错误: {e}")
        return jsonify({
            'code': 500,
            'error': '服务器错误',
            'message': '获取会话信息时出现错误',
            'time': datetime.now()
        }), 500


# ----------------------------------------------------------------------------
# get_user_statistics：用户统计信息查询（GET /profile/statistics）
# 作用：返回用户维度的统计骨架；其中 account_age_days 已按注册时间(created_at)
#       计算"注册天数"，total_logins / last_activity 等字段留待业务扩展填充。
# 入参：无；返回：code=0 + data=statistics；异常时 code=500。
# ----------------------------------------------------------------------------
@user.route('/profile/statistics', methods=['GET'])
@jwt_auth_required
@rate_limit(max_requests=10, window_seconds=60, per_user=True)
def get_user_statistics():
    """
    获取用户统计信息
    需要根据实际业务需求扩展
    """
    try:
        current_user = g.user

        # 这里可以添加用户相关的统计信息
        # 例如：注册天数、活动次数等（当前为可扩展骨架）

        statistics = {
            'user_id': current_user.id,
            'account_age_days': None,  # 需要计算
            'last_activity': None,
            'total_logins': None
        }

        # 计算账户年龄（如果created_at存在）
        # 注册天数 = 当前 UTC 时间 - 注册时间(created_at)，取整天数
        if current_user.created_at:
            from datetime import datetime
            account_age = datetime.utcnow() - current_user.created_at
            statistics['account_age_days'] = account_age.days

        return jsonify({
            'code': 0,
            'message': '获取统计信息成功',
            'data': statistics,
            'time': datetime.now()
        })

    except Exception as e:
        print(f"获取统计信息时出现错误: {e}")
        return jsonify({
            'code': 500,
            'error': '服务器错误',
            'message': '获取统计信息时出现错误',
            'time': datetime.now()
        }), 500
