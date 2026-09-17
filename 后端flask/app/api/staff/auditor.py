# ============================================================================
# 模块：auditor.py —— 审计员业务接口（后台审计蓝图 auditor）
# ----------------------------------------------------------------------------
# 文件作用：实现权限矩阵中"审计员"角色的全部能力（**只读**）：
#   - 分页查看安全审计日志 / 安全事件（可过滤事件类型与时间范围）；
#   - 导出审计日志为 CSV 文件。
# 权限边界（最小权限）：审计员不能管理用户、修改商品、处理订单或支付 ——
#   所有接口都只读 security_event 表，且接口本身挂 @auditor_required，
#   用 admin 的 token 调这里同样会被 403 拒绝（角色互不越权）。
# 说明：审计员自己的"查看/导出"行为也要写日志（任务书要求可追溯）。
# 注册路由（蓝图 auditor）：
#   GET /api/auditor/events    分页/过滤查询审计日志
#   GET /api/auditor/export    导出审计日志 CSV
# ============================================================================
import csv
import io
from datetime import datetime

from flask import Blueprint, request, Response, jsonify, g

from app.middleware import rate_limit, jwt_auth_required, auditor_required
from app.utils import db, audit_log

user = Blueprint('auditor', __name__)


# ----------------------------------------------------------------------------
# build_response：统一 JSON 响应封装（与其它蓝图一致）
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


def _filters():
    """从查询参数中取出事件过滤条件（均可空）"""
    return (request.args.get('event_type') or None,
            request.args.get('start') or None,
            request.args.get('end') or None)


# ----------------------------------------------------------------------------
# 分页查询审计日志（GET /api/auditor/events）
# 查询参数：page、page_size、event_type、start、end（时间范围，YYYY-MM-DD 或
#          YYYY-MM-DD HH:MM:SS）
# 返回：db.query_security_events 的分页结构
# ----------------------------------------------------------------------------
@user.route('/api/auditor/events', methods=['GET'])
@rate_limit(max_requests=60, window_seconds=60, per_ip=True)
@jwt_auth_required
@auditor_required
def auditor_list_events():
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 20, type=int), 200)
    event_type, start, end = _filters()

    res = db.query_security_events(page=page, page_size=page_size,
                                   event_type=event_type, start=start, end=end)
    # 审计员“查看”行为同样留痕（课件要求：查看/导出都记录）
    audit_log.log_audit('AUDITOR_VIEW', g.username,
                        f'审计员 {g.username} 查看审计日志 page={page} '
                        f'共 {res["total"]} 条(event_type={event_type})')
    return build_response(0, 'ok', data=res)


# ----------------------------------------------------------------------------
# 导出审计日志 CSV（GET /api/auditor/export）
# 说明：以附件形式返回 CSV；审计员的导出动作本身也记录一条 AUDITOR_EXPORT
#       审计日志（记录操作人与导出的记录数），实现"审计行为本身可审计"。
# ----------------------------------------------------------------------------
@user.route('/api/auditor/export', methods=['GET'])
@rate_limit(max_requests=10, window_seconds=60, per_ip=True)
@jwt_auth_required
@auditor_required
def auditor_export():
    event_type, start, end = _filters()
    # 导出不考虑分页：取全量（上限保护用较大的 page_size）
    res = db.query_security_events(page=1, page_size=100000,
                                   event_type=event_type, start=start, end=end)

    # 组装 CSV 文本
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['id', 'event_type', 'username', 'details', 'created_at'])
    for e in res['events']:
        writer.writerow([e['id'], e['event_type'], e['username'],
                         e['details'], e['created_at']])
    csv_text = buf.getvalue()

    # 记录审计员的导出行为
    audit_log.log_audit('AUDITOR_EXPORT', g.username,
                          f'审计员导出审计日志 {res["total"]} 条'
                          f'（event_type={event_type}, start={start}, end={end}）')

    filename = f'audit_events_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return Response(
        csv_text,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )
