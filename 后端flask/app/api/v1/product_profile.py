# ================================================================
# 模块：product_profile —— 商品列表查询接口（分页 + 条件过滤）
#
# 作用：
#   按不同角色提供两类商品列表查询：
#     1. 商家查询“自己发布”的商品（/seller/products/profile）；
#     2. 普通用户查询全部商品（/user/products/profile）。
#   两者均支持分页与过滤参数，返回统一 JSON 结构，供前端“商品管理页”
#   与“用户浏览商品页”复用。
#
# 路由与 HTTP 方法（均为 GET，查询条件走 URL 查询串）：
#   GET /seller/products/profile —— 商家查询自己的商品
#   GET /user/products/profile   —— 用户查询所有商品
#
# 权限要求：
#   - jwt_auth_required：两个接口都必须携带有效 JWT 登录凭证；
#   - seller_required：商家接口仅允许 seller（商家）角色访问；
#   - user_required：用户接口仅允许 user（普通用户）角色访问。
#
# 涉及的工具 / 数据库函数：
#   app.middleware：jwt_auth_required / seller_required / user_required
#   app.utils.db.get_seller_products_paginated —— 商家分页查询自己的商品
#   app.utils.db.get_all_products_paginated    —— 用户分页查询全部商品
# ================================================================
# 假设蓝图名为 product_bp，注册在 app/__init__.py 中
from datetime import datetime, timezone

from flask import Blueprint, request, g, jsonify
from app.middleware import jwt_auth_required, seller_required,user_required
from app.utils import db

user = Blueprint('product', __name__)

# 统一响应封装函数：所有接口返回固定结构 {code, message, error, data, time}。
# 约定 code=0 表示业务成功；HTTP 状态码由参数 status 控制（400 参数错误、
# 403 无权限 / 404 资源不存在 / 500 服务器错误等），便于前端统一处理。
def build_response(code, message='', data=None, error=None, status=200):
    payload = {
        'code': code,
        'message': message,
        'error': error,
        'data': data,
        'time': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }
    return jsonify(payload), status

# ---------- 商家查询自己的商品（只能查自己发布的） ----------
# ------------------------------------------------------------------
# 视图函数：get_seller_products —— 商家查询自己发布的商品
# 请求：GET /seller/products/profile
# 查询参数：page（页码，默认 1）、size（每页条数，默认 20，上限 100）、
#           status（可选，active/inactive 状态过滤）、
#           keyword（可选，按商品名称模糊搜索）
# 权限与范围：JWT 登录 + seller 商家角色；seller_id 取自已登录用户，
#             因此永远只能查到“自己”发布的商品
# 返回值：成功 code=0，data 为分页结构 {items, total, page, size, pages}；
#         异常统一返回 500
# ------------------------------------------------------------------
@user.route('/seller/products/profile', methods=['GET'])
@jwt_auth_required
@seller_required
def get_seller_products():
    """
    商家查询自己发布的商品列表（支持分页和过滤）
    查询参数：
        page: 页码，默认1
        size: 每页数量，默认20
        status: 状态过滤（active/inactive）
        keyword: 商品名称关键词搜索
    """
    try:
        # 获取当前登录商家ID（由 @jwt_auth_required 设置）
        seller_id = g.user_id

        # 解析查询参数：request.args 即 URL 中 “?” 之后的查询串；
        # 每个参数都给出默认值，并用 type=int 指定类型转换
        # 解析查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('size', 20, type=int)
        status = request.args.get('status', None, type=str)
        keyword = request.args.get('keyword', None, type=str)

        # 参数兜底修正：页码最小为 1；每页条数限制在 1~100，
        # 越界时回退到默认 20，防止超大 size 拖垮数据库查询
        # 参数校验
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20

        # 调用数据库分页查询函数，把过滤条件与分页参数交给数据库层拼装；
        # 返回结构：items（当前页商品对象）、total、page、per_page、pages
        # 调用数据库函数
        result = db.get_seller_products_paginated(
            seller_id=seller_id,
            page=page,
            per_page=per_page,
            status=status,
            name_keyword=keyword
        )

        # 格式化输出：把 ORM 商品对象逐条转成前端需要字段的字典
        # （datetime 转 ISO 字符串；seller 关联缺失时兜底显示“未知商家”）
        # 格式化输出
        items_data = []
        for product in result['items']:
            items_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'status': product.status,
                'seller_id': product.seller_id,
                'seller_name': product.seller.username if product.seller else '未知商家',
                'image_url': product.image_url,
                'created_at': product.created_at.isoformat() if product.created_at else None,
                'updated_at': product.updated_at.isoformat() if product.updated_at else None
            })

        # 业务成功：code=0；data 内为分页返回结构——
        # items 当前页商品列表、total 总条数、page 当前页码、
        # size 每页条数、pages 总页数
        return build_response(
            code=0,
            message='查询成功',
            data={
                'items': items_data,
                'total': result['total'],
                'page': result['page'],
                'size': result['per_page'],
                'pages': result['pages']
            }
        )

    except Exception as e:
        print(f"商家查询商品失败: {e}")
        import traceback
        traceback.print_exc()
        return build_response(
            code=500,
            error='服务器错误',
            message=f'查询商品时出现错误: {str(e)}',
            status=500
        )


# ---------- 用户查询所有商品（需登录） ----------
# ------------------------------------------------------------------
# 视图函数：get_all_products —— 普通用户查询全部商品（浏览商品用）
# 请求：GET /user/products/profile
# 查询参数：page（页码，默认 1）、size（每页条数，默认 20，上限 100）、
#           status（可选，状态过滤）、seller_id（可选，按卖家过滤）、
#           keyword（可选，按商品名称模糊搜索）
# 权限：JWT 登录 + user 普通用户角色（商家角色不可访问本接口）
# 返回值：成功 code=0，data 为分页结构 {items, total, page, size, pages}；
#         异常统一返回 500
# ------------------------------------------------------------------
@user.route('/user/products/profile', methods=['GET'])
@jwt_auth_required
@user_required
def get_all_products():
    """
    用户查询所有商品（支持分页和过滤）
    查询参数：
        page: 页码，默认1
        size: 每页数量，默认20
        status: 状态过滤（active/inactive）
        seller_id: 卖家ID过滤（可选）
        keyword: 商品名称关键词搜索
    """
    # 与商家接口相同：从查询串解析分页/过滤参数（page/size/status/keyword），
    # 其中 seller_id（可选）为本接口特有的“按卖家过滤”参数
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('size', 20, type=int)
        status = request.args.get('status', None, type=str)
        seller_id = request.args.get('seller_id', None, type=int)
        keyword = request.args.get('keyword', None, type=str)

        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20

        # 调用数据库分页查询函数查询全部商品（支持状态、卖家、关键词过滤）；
        # 返回结构与商家接口一致：items/total/page/per_page/pages。
        # 下方循环随后把 items 逐条格式化为字典，再组装成上方的分页响应
        result = db.get_all_products_paginated(
            page=page,
            per_page=per_page,
            status=status,
            seller_id=seller_id,
            name_keyword=keyword
        )

        items_data = []
        for product in result['items']:
            items_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'status': product.status,
                'seller_id': product.seller_id,
                'seller_name': product.seller.username if product.seller else '未知商家',
                'image_url': product.image_url,
                'created_at': product.created_at.isoformat() if product.created_at else None,
                'updated_at': product.updated_at.isoformat() if product.updated_at else None
            })

        # 业务成功：code=0；data 内为分页返回结构——
        # items 当前页商品列表、total 总条数、page 当前页码、
        # size 每页条数、pages 总页数
        return build_response(
            code=0,
            message='查询成功',
            data={
                'items': items_data,
                'total': result['total'],
                'page': result['page'],
                'size': result['per_page'],
                'pages': result['pages']
            }
        )

    except Exception as e:
        print(f"用户查询商品失败: {e}")
        import traceback
        traceback.print_exc()
        return build_response(
            code=500,
            error='服务器错误',
            message=f'查询商品时出现错误: {str(e)}',
            status=500
        )