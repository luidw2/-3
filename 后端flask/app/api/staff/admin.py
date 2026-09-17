# ============================================================================
# 模块：admin.py —— 管理员业务接口（后台管理蓝图 admin）
# ----------------------------------------------------------------------------
# 文件作用：实现权限矩阵中"管理员"角色的全部能力：
#   - 查看用户和商家账号列表；
#   - 禁用 / 启用用户账号、商家账号（禁用后其旧 token 因 is_active 复查立即失效）；
#   - 删除用户账号、商家账号（级联清理其名下数据）；
#   - 查看全部商品（分页/过滤）与删除任意商品（不受 seller 归属限制）。
# 所有接口均要求：JWT 认证（@jwt_auth_required）+ 管理员角色（@admin_required）
# + IP 限流；每个"写操作"都会写审计日志（security_event），实现
# "管理员关键操作可追溯"（记录操作人、对象、结果）。
# 注册路由（蓝图 admin）：
#   GET    /api/admin/users                    账号列表（type=user|seller|all）
#   POST   /api/admin/users/<id>/disable       禁用用户
#   POST   /api/admin/users/<id>/enable        启用用户
#   DELETE /api/admin/users/<id>               删除用户
#   POST   /api/admin/sellers/<id>/disable     禁用商家
#   POST   /api/admin/sellers/<id>/enable      启用商家
#   DELETE /api/admin/sellers/<id>             删除商家
#   GET    /api/admin/products                 商品列表（分页/状态/关键字）
#   DELETE /api/admin/products/<id>            删除任意商品
# ============================================================================
from datetime import datetime

from flask import Blueprint, request, jsonify, g

from app.middleware import rate_limit, jwt_auth_required, admin_required
from app.utils import db, audit_log

user = Blueprint('admin', __name__)


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


# ----------------------------------------------------------------------------
# _serialize_account：把 User / Seller ORM 对象转成前端可读的字典
# 说明：只挑对外展示的公开字段，不返回 password 等敏感字段
# ----------------------------------------------------------------------------
def _serialize_account(row, acct_type):
    return {
        'id': row.id,
        'username': row.username,
        'role': row.role,
        'is_active': row.is_active,
        'created_at': row.created_at.isoformat() if row.created_at else None,
        'type': acct_type,  # 'user' / 'seller'
    }


# ----------------------------------------------------------------------------
# 查看用户和商家列表（GET /api/admin/users）
# 查询参数：type=user|seller|all（默认 all）、page、page_size
# 返回：分页结构 {total, page, page_size, items:[...]}，按创建时间倒序
# ----------------------------------------------------------------------------
@user.route('/api/admin/users', methods=['GET'])
@rate_limit(max_requests=60, window_seconds=60, per_ip=True)
@jwt_auth_required
@admin_required
def admin_list_accounts():
    acct_type = request.args.get('type', 'all')
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('page_size', 10, type=int), 100)

    users = db.get_all_users() if acct_type in ('user', 'all') else []
    sellers = db.get_all_sellers() if acct_type in ('seller', 'all') else []

    items = [_serialize_account(u, 'user') for u in users] + \
            [_serialize_account(s, 'seller') for s in sellers]
    # 内存中按创建时间倒序 + 分页（本系统数据量级下足够；数据量大时改 SQL 分页）
    items.sort(key=lambda x: (x['created_at'] or ''), reverse=True)
    total = len(items)
    start = (page - 1) * page_size
    return build_response(0, 'ok', data={
        'total': total,
        'page': page,
        'page_size': page_size,
        'items': items[start:start + page_size],
    })


# ----------------------------------------------------------------------------
# 禁用/启用/删除 用户账号（操作 user 表）
# 禁用实现：db.update_user(user_id, is_active=False) —— jwt_auth 中间件在
# 每次请求都会复查 is_active，因此禁用后旧 token 立即失效（可现场演示）
# ----------------------------------------------------------------------------
def _toggle_user(user_id, active):
    obj = db.get_user_by_id(user_id)
    if not obj:
        return build_response(404, '用户不存在', status=404)
    db.update_user(user_id, is_active=active)
    audit_log.log_audit(
        'ADMIN_USER_ENABLE' if active else 'ADMIN_USER_DISABLE',
        g.username,
        f'管理员 {g.username} 将用户 {obj.username}(id={user_id}) '
        f'{"启用" if active else "禁用"}'
    )
    return build_response(0, '操作成功', data={'id': user_id, 'is_active': active})


@user.route('/api/admin/users/<int:user_id>/disable', methods=['POST'])
@rate_limit(max_requests=30, window_seconds=60, per_ip=True)
@jwt_auth_required
@admin_required
def admin_disable_user(user_id):
    return _toggle_user(user_id, False)


@user.route('/api/admin/users/<int:user_id>/enable', methods=['POST'])
@rate_limit(max_requests=30, window_seconds=60, per_ip=True)
@jwt_auth_required
@admin_required
def admin_enable_user(user_id):
    return _toggle_user(user_id, True)


@user.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@rate_limit(max_requests=30, window_seconds=60, per_ip=True)
@jwt_auth_required
@admin_required
def admin_delete_user(user_id):
    obj = db.get_user_by_id(user_id)
    if not obj:
        return build_response(404, '用户不存在', status=404)
    ok = db.delete_user(user_id)  # 级联删除购物车/订单/刷新令牌等名下数据
    if not ok:
        return build_response(500, '删除用户失败', status=500)
    audit_log.log_audit('ADMIN_USER_DELETE', g.username,
                          f'管理员 {g.username} 删除用户 {obj.username}(id={user_id})')
    return build_response(0, '删除用户成功', data={'id': user_id})


# ----------------------------------------------------------------------------
# 禁用/启用/删除 商家账号（操作 seller 表，逻辑同用户）
# ----------------------------------------------------------------------------
def _toggle_seller(seller_id, active):
    obj = db.get_seller_by_id(seller_id)
    if not obj:
        return build_response(404, '商家不存在', status=404)
    db.update_seller(seller_id, is_active=active)
    audit_log.log_audit(
        'ADMIN_SELLER_ENABLE' if active else 'ADMIN_SELLER_DISABLE',
        g.username,
        f'管理员 {g.username} 将商家 {obj.username}(id={seller_id}) '
        f'{"启用" if active else "禁用"}'
    )
    return build_response(0, '操作成功', data={'id': seller_id, 'is_active': active})


@user.route('/api/admin/sellers/<int:seller_id>/disable', methods=['POST'])
@rate_limit(max_requests=30, window_seconds=60, per_ip=True)
@jwt_auth_required
@admin_required
def admin_disable_seller(seller_id):
    return _toggle_seller(seller_id, False)


@user.route('/api/admin/sellers/<int:seller_id>/enable', methods=['POST'])
@rate_limit(max_requests=30, window_seconds=60, per_ip=True)
@jwt_auth_required
@admin_required
def admin_enable_seller(seller_id):
    return _toggle_seller(seller_id, True)


@user.route('/api/admin/sellers/<int:seller_id>', methods=['DELETE'])
@rate_limit(max_requests=30, window_seconds=60, per_ip=True)
@jwt_auth_required
@admin_required
def admin_delete_seller(seller_id):
    obj = db.get_seller_by_id(seller_id)
    if not obj:
        return build_response(404, '商家不存在', status=404)
    ok = db.delete_seller(seller_id)  # 级联删除名下商品/刷新令牌等
    if not ok:
        return build_response(500, '删除商家失败', status=500)
    audit_log.log_audit('ADMIN_SELLER_DELETE', g.username,
                          f'管理员 {g.username} 删除商家 {obj.username}(id={seller_id})')
    return build_response(0, '删除商家成功', data={'id': seller_id})


# ----------------------------------------------------------------------------
# 查看全部商品（GET /api/admin/products）
# 查询参数：page、per_page、status(active/inactive)、name_keyword
# 返回：复用 db.get_all_products_paginated 的分页结果，补充卖家名与时间
# ----------------------------------------------------------------------------
@user.route('/api/admin/products', methods=['GET'])
@rate_limit(max_requests=60, window_seconds=60, per_ip=True)
@jwt_auth_required
@admin_required
def admin_list_products():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status = request.args.get('status') or None
    keyword = request.args.get('name_keyword') or None

    res = db.get_all_products_paginated(page=page, per_page=per_page,
                                        status=status, name_keyword=keyword)
    items = []
    for p in res['items']:
        items.append({
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'status': p.status,
            'seller_id': p.seller_id,
            'seller_name': p.seller.username if p.seller else None,
            'image_url': p.image_url,
            'created_at': p.created_at.isoformat() if p.created_at else None,
        })
    return build_response(0, 'ok', data={
        'total': res['total'],
        'page': res['page'],
        'per_page': res['per_page'],
        'pages': res['pages'],
        'items': items,
    })


# ----------------------------------------------------------------------------
# 删除任意商品（DELETE /api/admin/products/<id>）
# 说明：原 delete_product(product_id, seller_id) 带卖家归属校验（防越权）；
#       管理员是"全权"角色，此处先查出商品真实归属，再以真实 seller_id 调用，
#       从而复用其"删除磁盘图片 + 删除记录"的完整逻辑，不改动数据层接口。
# ----------------------------------------------------------------------------
@user.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
@rate_limit(max_requests=30, window_seconds=60, per_ip=True)
@jwt_auth_required
@admin_required
def admin_delete_product(product_id):
    product = db.get_product_by_id(product_id)
    if not product:
        return build_response(404, '商品不存在', status=404)
    ok = db.delete_product(product_id, product.seller_id)
    if not ok:
        return build_response(500, '删除商品失败', status=500)
    audit_log.log_audit('ADMIN_PRODUCT_DELETE', g.username,
                          f'管理员 {g.username} 删除商品 {product.name}(id={product_id})')
    return build_response(0, '删除商品成功', data={'id': product_id})
