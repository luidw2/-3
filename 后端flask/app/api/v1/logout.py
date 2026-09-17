# ============================================================================
# 模块：logout.py —— 用户登出 / 销户前置信息接口
# ----------------------------------------------------------------------------
# 文件作用：
#   1) logout：登出当前账号 —— 撤销数据库中该用户签发的全部刷新令牌，
#      使其后续无法再用旧刷新令牌续期，实现"下线"；只撤销登录态，
#      不删除账号数据（真正销户在 delete.py）；
#   2) get_deletion_status：向前端返回一组"账户删除"的说明文案
#      （删除影响、前置条件等），供销户确认页面展示。
# 注册路由：
#   POST /user/logout              —— 用户登出（需 JWT）
#   GET  /account/deletion/status  —— 获取销户说明信息（需 JWT）
# 涉及的安全机制：
#   1) jwt_auth_required 鉴权装饰器：两接口都要求携带有效 JWT，中间件解析
#      后把当前用户对象注入 Flask 的 g 对象（g.user）；
#   2) 刷新令牌集中撤销（db.revoke_all_tokens_for_user）——一次性使该用户
#      已签发的全部 refresh_token 失效；
#   3) 安全审计日志（db.log_security_event）——登出行为留痕，便于追溯。
# 调用的工具函数：db.revoke_all_tokens_for_user、db.log_security_event。
# ============================================================================
from flask import Blueprint,  jsonify, g
from app.utils import db
from app.middleware import jwt_auth_required
from datetime import datetime

# 创建蓝图 - 使用正确的蓝图名称
user = Blueprint('logout', __name__)


# ----------------------------------------------------------------------------
# logout：用户登出视图函数（POST /user/logout）
# 作用：撤销当前用户全部刷新令牌，使已签发的 access_token 在自然过期后无法
#       再通过刷新令牌换新，从而结束当前登录会话（登出）。
# 入参：无（当前用户由 JWT 中间件注入 g.user）
# 返回：code=0 登出成功；异常时 code=500 服务器错误。
# 说明：登出只撤销令牌、不删除账号；账号数据保留，可随时重新登录。
# ----------------------------------------------------------------------------
@user.route('/user/logout', methods=['POST'])
@jwt_auth_required
def logout():
    """
    用户登出功能 - 注销当前会话
    与销户不同，这只是登出当前登录状态
    """
    try:
        # g.user 由 jwt_auth_required 中间件校验令牌后注入，代表当前登录用户
        current_user = g.user

        # 注销用户的所有刷新令牌
        # 撤销数据库中该用户全部 refresh_token：此后旧令牌无法续期换新，
        # 配合 access_token 的短期有效性，即实现整个账号"下线"。
        db.revoke_all_tokens_for_user(current_user.id)

        # 记录安全事件
        # 将"用户主动登出"写入安全审计日志，便于追溯登录/登出行为
        db.log_security_event(
            event_type='USER_LOGOUT',
            username=current_user.username,
            details='用户主动登出'
        )

        return jsonify({
            'code': 0,
            'message': '登出成功',
            'time': datetime.now()
        })

    except Exception as e:
        # 异常兜底：登出失败不阻断前端流程，返回 500 便于排查
        print(f"登出过程中出现错误: {e}")
        return jsonify({
            'code': 500,
            'error': '服务器错误',
            'message': '登出过程中出现错误',
            'time': datetime.now()
        }), 500


# ----------------------------------------------------------------------------
# get_deletion_status：销户说明信息查询（GET /account/deletion/status）
# 作用：返回一组固定的提示文案，向用户说明删除账户不可逆、将清除哪些数据、
#       以及需要满足的前置条件（当前密码验证 + 输入确认文本
#       'DELETE_MY_ACCOUNT'），供销户页做二次确认展示。
# 入参：无；返回：code=0 + data(warning/effects/requirements)。
# 说明：本接口只返回静态文案、不执行任何删除动作；
#       真正的销户逻辑见 delete.py 的 /user/delete 接口。
# ----------------------------------------------------------------------------
@user.route('/account/deletion/status', methods=['GET'])
@jwt_auth_required
def get_deletion_status():
    """
    获取账户删除状态信息
    提供关于账户删除的影响和后果的信息
    """
    current_user = g.user

    return jsonify({
        'code': 0,
        'message': '账户删除相关信息',
        'data': {
            # 删除不可逆的醒目警告
            'warning': '此操作不可逆！',
            # 删除会造成的具体影响清单
            'effects': [
                '所有个人数据将被永久删除',
                '所有登录会话将立即失效',
                '账户无法恢复',
                '相关业务数据可能会被匿名化处理'
            ],
            # 执行删除前必须满足的前置条件
            'requirements': [
                '需要提供当前密码验证',
                '需要输入确认文本 "DELETE_MY_ACCOUNT"',
                '操作后立即生效'
            ]
        },
        'time': datetime.now()
    })
