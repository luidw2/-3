# -*- coding: utf-8 -*-
"""
===============================================================================
 audit_events.py —— 审计事件字典（安全审计日志的"事件类型"权威清单）
===============================================================================
【作用】
    本项目把"关键操作留痕"统一落到 security_event 表（见 app/utils/db.py 的
    SecurityEvent 模型与 log_security_event 函数）。为避免事件类型字符串
    散落各处导致拼写不一、难以统计，本文件集中登记全部合法事件类型：
    - AUDIT_EVENTS：{事件类型: 说明} 字典，既是代码校验依据，
      也是答辩交付物《审计事件字典》的机器可读版本（可用脚本导出为文档）；
    - 新增埋点时先在此登记，再通过 app/utils/audit_log.py 的 log_audit()
      写入，log_audit 会对未登记类型给出提示，保证字典与代码一致。

【记录约定】
    每条审计记录包含：event_type（本字典登记的类型）、username（操作者，
    后台操作为 admin/auditor 的账号名，前台操作为 user/seller 用户名）、
    details（描述：操作对象、结果等）、created_at（自动时间戳）。
===============================================================================
"""

# ============================================================================
# 事件类型分组说明（前缀即域）：
#   ACCOUNT_*  前台账号生命周期（注册/更新/注销）
#   USER_* / PROFILE_* / CART_*   前台用户行为（登录/登出/资料/购物车）
#   PRODUCT_*  商品行为
#   PAY_*      支付回调
#   STAFF_*    后台账号认证链路（登录两步/TOTP/恢复码/登出）
#   TOTP_*     TOTP 绑定管理
#   ADMIN_*    管理员管理操作（用户/商家/商品）
#   AUDITOR_*  审计员行为（查看/导出）
#   PERMISSION_DENIED  越权/无权访问被拒绝
# ============================================================================
AUDIT_EVENTS = {
    # ---------- 前台账号（user/seller）----------
    'ACCOUNT_CREATE_SUCCESS': '前台账号创建成功（用户或商家注册）',
    'ACCOUNT_CREATE_FAILED': '前台账号创建失败',
    'ACCOUNT_UPDATE_SUCCESS': '前台账号信息更新成功（含改密）',
    'ACCOUNT_UPDATE_FAILED': '前台账号信息更新失败',
    'ACCOUNT_DELETION_SUCCESS': '前台账号删除成功（注销）',
    'ACCOUNT_DELETION_FAILED': '前台账号删除失败',
    'ACCOUNT_DELETION_ATTEMPT': '前台账号注销尝试（任一步校验未通过）',
    'ACCOUNT_DELETION_STARTED': '前台账号注销流程开始（校验通过）',
    'ACCOUNT_DELETION_ERROR': '前台账号注销流程异常',
    'USER_LOGIN_OK': '前台用户登录成功（user/seller 密码登录）',
    'USER_LOGIN_FAILED': '前台用户登录失败（密码错误）',
    'USER_LOGOUT': '前台用户主动登出',
    'PROFILE_ACCESS': '个人资料被访问',
    'PROFILE_UPDATE': '个人资料更新',
    'CART_VIEW': '购物车被访问',

    # ---------- 商品 / 支付 ----------
    'PRODUCT_CREATE': '商品创建成功',
    'PRODUCT_DELETE': '商品删除（预留）',
    'PAY_CALLBACK_SUCCESS': '支付异步回调成功（订单置为已支付）',

    # ---------- 后台账号（staff：admin / auditor）认证链路 ----------
    'STAFF_LOGIN_OK': '后台账号登录成功（密码通过，含未绑定TOTP直登与TOTP通过）',
    'STAFF_LOGIN_FAILED': '后台账号登录失败（密码错误）',
    'STAFF_LOGIN_STEP1': '后台账号密码验证通过，等待第二步TOTP/恢复码',
    'STAFF_TOTP_FAILED': '后台登录 TOTP 动态码验证失败',
    'STAFF_TOTP_REPLAY': '后台登录动态码重放被拒绝',
    'STAFF_RECOVERY_FAILED': '后台登录恢复码校验失败',
    'RECOVERY_USED': '一次性恢复码被使用（登录成功）',
    'STAFF_LOGOUT': '后台账号退出登录',

    # ---------- TOTP 绑定管理 ----------
    'TOTP_BIND_OK': 'TOTP 绑定成功（动态码验证通过后加密落库）',
    'TOTP_BIND_FAILED': 'TOTP 绑定确认失败（动态码错误）',

    # ---------- 后台账号（staff）管理（管理员对 staff 自身的增删改） ----------
    'STAFF_CREATE': '后台账号创建',
    'STAFF_UPDATE': '后台账号字段更新',
    'STAFF_DELETE': '后台账号删除',

    # ---------- 管理员管理操作 ----------
    'ADMIN_USER_DISABLE': '管理员禁用用户账号',
    'ADMIN_USER_ENABLE': '管理员启用用户账号',
    'ADMIN_USER_DELETE': '管理员删除用户账号',
    'ADMIN_SELLER_DISABLE': '管理员禁用商家账号',
    'ADMIN_SELLER_ENABLE': '管理员启用商家账号',
    'ADMIN_SELLER_DELETE': '管理员删除商家账号',
    'ADMIN_PRODUCT_DELETE': '管理员删除商品',

    # ---------- 审计员行为 ----------
    'AUDITOR_VIEW': '审计员查看审计日志/安全事件',
    'AUDITOR_EXPORT': '审计员导出审计日志',

    # ---------- 访问控制 ----------
    'PERMISSION_DENIED': '越权/无权访问被拒绝（角色不符等）',
}

# 便捷：按前缀分组（用于生成《审计事件字典》文档时的分组渲染）
def group_events(events: dict = AUDIT_EVENTS) -> dict:
    """把事件字典按“_”前缀分组：{'ACCOUNT': [...], 'STAFF': [...]}"""
    groups = {}
    for code in events:
        prefix = code.split('_', 1)[0]
        groups.setdefault(prefix, []).append(code)
    return groups
