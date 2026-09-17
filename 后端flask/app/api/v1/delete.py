# ============================================================================
# 模块：delete.py —— 用户销户接口（永久删除账号）
# ----------------------------------------------------------------------------
# 文件作用：接收 DELETE /user/delete 请求，在通过 当前密码 + 用户名 +
#           'DELETE' 确认文本 三重校验后，撤销该账号全部刷新令牌并级联
#           删除用户及其关联数据（删除操作不可逆）。
# 注册路由：DELETE /user/delete
# 涉及的安全机制：
#   1) jwt_auth_required：必须携带有效 JWT，且只能删除当前登录账号本人；
#   2) validate_params 装饰器（参数校验 + 清洗）：
#      required_fields 强制提供 name / password / confirmation；
#      confirmation 必须等于确认文本 'DELETE'（防误触的显式确认机制）；
#      sanitize=True 对提交参数做清洗，降低注入类风险；
#   3) rate_limit(per_user=True)：按用户限流（每用户每分钟最多 100 次），
#      防止误触/恶意脚本重复触发删除请求；
#   4) my_bcrypt.compare_password：删除前再次校验当前密码（Bcrypt 比对）；
#   5) db.log_security_event：销户 尝试/开始/成功/异常 全程审计留痕。
# 调用的工具函数：
#   db.revoke_all_tokens_for_user、db.delete_user、db.log_security_event、
#   my_bcrypt.compare_password；参数校验来自 app.middleware 的
#   validate_params 与 validate_string_length。
# ============================================================================

from flask import Blueprint, request, jsonify, g
from app.utils import db, auth, my_bcrypt
from app.middleware import jwt_auth_required, validate_params, rate_limit
from app.middleware.param_validation import validate_string_length
from datetime import datetime

# 创建蓝图 - 使用正确的蓝图名称
user = Blueprint('delete', __name__)




# ----------------------------------------------------------------------------
# delete_account：用户销户视图函数（DELETE /user/delete）
# 处理流程：取"参数校验结果 + 当前登录用户" → Bcrypt 校验当前密码 →
#           校验提交用户名与登录用户名一致 → 撤销全部刷新令牌 →
#           db.delete_user 级联删除账号及相关记录 → 全程写审计日志。
# 入参（JSON body，由 validate_params 装饰器校验并清洗后存入
#      request.validated_data）：
#     name         —— 要删除的用户名（须与当前登录用户一致）
#     password     —— 当前登录密码（Bcrypt 复验）
#     confirmation —— 确认文本，装饰器强制其等于 'DELETE'
# 返回：code=0 删除成功；400 密码或用户名不正确；500 删除过程异常。
# 说明：本操作不可逆，所有前置校验通过后才真正执行数据库删除。
# ----------------------------------------------------------------------------
@user.route('/user/delete', methods=['DELETE'])
@jwt_auth_required
@validate_params(
    required_fields=['name','password', 'confirmation'],
    field_validators={
        'confirmation': lambda x: x == 'DELETE'   # 显式确认：必须输入 'DELETE'
    },
    sanitize=True                                 # 对参数统一清洗
)
@rate_limit(max_requests=100, window_seconds=60, per_user=True)
def delete_account():
    """
    用户销户功能 - 永久删除用户账户
    """
    # validated_data 是 validate_params 装饰器清洗、校验后的数据
    data = request.validated_data# type: ignore
    password = data.get('password')
    current_user = g.user   # 当前登录用户（JWT 中间件注入）

    # 验证用户密码
    # 删除属于高敏操作：先用 Bcrypt 比对当前密码，密码错误即拒绝并记录审计
    if not my_bcrypt.compare_password(current_user.password, password):
        db.log_security_event(
            event_type='ACCOUNT_DELETION_ATTEMPT',
            username=current_user.username,
            details='密码验证失败'
        )
        return jsonify({
            'code': 400,
            'error': '密码错误',
            'message': '提供的密码不正确，无法执行销户操作',
            'time': datetime.now()
        }), 400

    # 用户名一致性校验：提交的用户名必须与当前登录账号同名，防止误删他人账号
    if  data.get('name') != current_user.username:
        db.log_security_event(
            event_type='ACCOUNT_DELETION_ATTEMPT',
            username=current_user.username,
            details='用户名错误'
        )
        return jsonify({
            'code': 400,
            'error': '用户名错误',
            'message': '提供的用户名不正确，无法执行销户操作',
            'time': datetime.now()
        }), 400

    try:
        # 记录安全事件 - 开始销户
        db.log_security_event(
            event_type='ACCOUNT_DELETION_STARTED',
            username=current_user.username,
            details='用户发起账户删除请求'
        )

        # 1. 注销用户的所有刷新令牌
        # 先撤销刷新令牌，使已签发会话无法续期，防止删除过程中令牌被复用
        db.revoke_all_tokens_for_user(current_user.id)

        # 2. 执行用户删除操作（现在db.delete_user会处理相关记录和安全事件）
        # delete_user 在数据层级联清理该用户关联数据（购物车/令牌/业务记录等）
        deletion_success = db.delete_user(current_user.id)

        if deletion_success:
            # 删除成功：返回业务码 0
            return jsonify({
                'code': 0,
                'message': '账户删除成功',
                'details': '您的账户及相关数据已永久删除',
                'time': datetime.now()
            })
        else:
            # 数据层返回失败（如记录不存在等），统一提示稍后重试
            return jsonify({
                'code': 500,
                'error': '删除失败',
                'message': '账户删除过程中出现错误，请稍后重试',
                'time': datetime.now()
            }), 500

    except Exception as e:
        # 异常兜底：记录审计事件后返回 500，避免删除状态悬空
        db.log_security_event(
            event_type='ACCOUNT_DELETION_ERROR',
            username=current_user.username,
            details=f'删除过程中出现异常: {str(e)}'
        )

        print(f"销户过程中出现错误: {e}")
        return jsonify({
            'code': 500,
            'error': '服务器错误',
            'message': '销户过程中出现未知错误',
            'time': datetime.now()
        }), 500
