# ============================================================================
# 模块：update.py —— 用户资料更新接口
# ----------------------------------------------------------------------------
# 文件作用：接收 PUT /user/update 请求，允许已登录用户更新本人资料；
#           更新前必须提供"当前密码"做 Bcrypt 复验（防止会话被冒用/越权修改）；
#           可更新字段采用白名单机制，仅允许 username / password。
# 注册路由：PUT /user/update
# 涉及的安全机制：
#   1) jwt_auth_required：仅允许携带有效 JWT 的当前用户修改本人资料；
#   2) 当前密码复验（my_bcrypt.compare_password，基于 Bcrypt 哈希比对）；
#   3) 字段白名单 allowed_fields：白名单之外的字段（如 role、email 等
#      敏感/关键属性）一律不采纳，防止越权篡改身份信息；
#   4) rate_limit(per_user=True)：按用户限流，每用户每分钟最多 100 次；
#   5) db.log_security_event：资料变更行为安全审计留痕。
# 调用的工具函数：db.update_user、db.log_security_event、my_bcrypt.compare_password。
# ============================================================================
from flask import Blueprint, request, jsonify, g
from app.utils import db, my_bcrypt
from app.middleware import jwt_auth_required, rate_limit
from datetime import datetime

# 创建蓝图
user = Blueprint('update', __name__)


# ----------------------------------------------------------------------------
# update_profile：用户资料更新视图函数（PUT /user/update）
# 处理流程：取当前用户与请求数据 → 空数据检查 → 校验提供 current_password →
#           Bcrypt 比对当前密码 → 按白名单提取待更新字段 → db.update_user
#           执行更新 → 成功写审计日志并返回。
# 入参（JSON body）：current_password 当前密码（必填，用于身份复验）、
#                   username / password 等白名单内的待更新字段（可省）。
# 返回：code=0 更新成功；400 无数据/缺当前密码/无有效更新字段；
#       401 当前密码错误；500 更新过程异常。
# 补充：password 等字段在数据层如何落库（哈希等）由 db.update_user 决定，
#       本视图层只负责白名单筛选与透传。
# ----------------------------------------------------------------------------
@user.route('/user/update', methods=['PUT'])
@jwt_auth_required
@rate_limit(max_requests=100, window_seconds=60, per_user=True)
def update_profile():
    """
    更新用户个人信息
    允许用户更新非敏感信息
    """
    try:
        # 获取当前用户
        # g.user 由 JWT 鉴权中间件注入，保证只能修改自己
        current_user = g.user

        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'error': '请求数据为空',
                'message': '请提供要更新的数据',
                'time': datetime.now()
            }), 400

        # 定义允许更新的字段（排除敏感字段）
        # 白名单机制：仅 username/password 可改，role、email 等一律不接受，
        # 防止越权修改关键属性
        allowed_fields = ['username', 'password']
        update_data = {}

        # 验证当前密码
        # 修改资料属于敏感操作：必须携带 current_password，防止令牌被盗后
        # 被冒名修改资料
        if 'current_password' not in data:
            return jsonify({
                'code': 400,
                'error': '缺少当前密码',
                'message': '请输入当前密码进行验证',
                'time': datetime.now()
            }), 400

        # 验证密码是否正确
        # Bcrypt 比对：输入密码与库中哈希一致才允许继续
        if not my_bcrypt.compare_password(current_user.password, data['current_password']):
            return jsonify({
                'code': 401,
                'error': '密码错误',
                'message': '当前密码错误，请重新输入',
                'time': datetime.now()
            }), 401

        # 仅提取请求中存在且非空的"白名单字段"，其余字段一律忽略
        for field in allowed_fields:
            if field in data and data[field] is not None:
                update_data[field] = data[field]

        # 如果没有可更新的字段
        # 请求里没有任何合法更新内容（例如只传了 current_password）
        if not update_data:
            return jsonify({
                'code': 400,
                'error': '无效的更新',
                'message': '没有提供有效的更新字段',
                'time': datetime.now()
            }), 400

        # 执行更新
        # 把筛选后的字段透传给 db 层做更新（哈希等落库细节由数据层处理）
        updated_user = db.update_user(current_user.id, **update_data)

        if updated_user:
            # 记录安全事件
            # 更新成功：把本次变更的字段写入审计日志，便于事后追溯
            db.log_security_event(
                event_type='PROFILE_UPDATE',
                username=current_user.username,
                details=f'用户更新个人信息: {list(update_data.keys())}'
            )

            return jsonify({
                'code': 0,
                'message': '更新用户信息成功',
                'data': {
                    'updated_fields': list(update_data.keys())
                },
                'time': datetime.now()
            })
        else:
            # 数据层更新未生效（返回空），统一按失败处理
            return jsonify({
                'code': 500,
                'error': '更新失败',
                'message': '更新用户信息时出现错误',
                'time': datetime.now()
            }), 500

    except Exception as e:
        # 异常兜底：记录日志并返回 500
        print(f"更新用户信息时出现错误: {e}")
        return jsonify({
            'code': 500,
            'error': '服务器错误',
            'message': '更新用户信息时出现错误',
            'time': datetime.now()
        }), 500
