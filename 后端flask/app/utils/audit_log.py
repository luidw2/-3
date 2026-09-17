# -*- coding: utf-8 -*-
"""
===============================================================================
 audit_log.py —— 安全审计日志的统一入口
===============================================================================
【作用】
    项目内所有"关键操作留痕"都通过本模块的 log_audit() 写入 security_event 表：
    - 事件类型必须已在 config/audit_events.py 的 AUDIT_EVENTS 字典中登记，
      未登记的会打印提示（防止新埋点漏登记导致《审计事件字典》与代码不一致）；
    - 记录字段与 db.log_security_event 一致：event_type / username(操作者) /
      details(描述) / created_at(自动)；
    - 业务模块统一写 `from app.utils import audit_log`，
      然后 `audit_log.log_audit('STAFF_LOGIN_OK', username, '...')`。
【与运行日志的区别】
    本模块写的是"数据库审计日志"（可被审计员角色查询/导出、长期留存）；
    程序运行/排障日志（访问日志、异常日志）走 logging，见 app/utils/
    logging_config.py —— 两者用途不同，不要混淆。
===============================================================================
"""
from config.audit_events import AUDIT_EVENTS
from app.utils import db


def log_audit(event_type: str, username: str, details: str = ''):
    """
    写入一条安全审计记录（统一入口，带事件类型登记校验）。

    参数:
        event_type: 审计事件类型，必须登记在 config/audit_events.py；
        username  : 操作者（后台操作为 admin/auditor 账号，前台为用户/商家名；
                    未登录上下文传 'anonymous'）；
        details   : 事件描述（操作对象、结果等，供审计员阅读）。
    返回: 无（写入失败时 db.log_security_event 内部已处理异常，不阻断业务）。
    """
    if event_type not in AUDIT_EVENTS:
        # 字典未登记：不阻断写入，但提示开发者补登记，保证字典完备
        print(f"[audit-log] 警告：事件类型 {event_type!r} 未在 "
              f"config/audit_events.py 中登记，请补充说明")
    db.log_security_event(event_type=event_type, username=username, details=details)
