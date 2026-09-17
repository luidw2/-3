# ================================================================
# 模块：delete_product —— 商品删除接口（后端 Flask 视图）
#
# 作用：
#   商家删除“自己发布”的某条商品。先按商品 ID 查出商品做存在性与归属
#   校验，再调用数据库层删除记录，并返回统一的 JSON 响应。
#
# 路由与 HTTP 方法：
#   DELETE /product/delete/<int:product_id> —— 删除指定 ID 的商品
#   （<int:product_id> 是 Flask 的 URL 变量转换器，会自动把路径片段转成
#   整数后作为参数传入视图函数）
#
# 权限要求：
#   - jwt_auth_required：必须携带有效 JWT 登录凭证；
#   - seller_required：当前登录用户必须是“商家(seller)”角色；
#   - 业务层二次校验：商品必须属于当前商家本人（product.seller_id 与
#     g.user_id 一致），防止越权删除他人商品。
#
# 涉及的工具 / 数据库函数：
#   app.utils.db.get_product_by_id —— 按 ID 查商品（用于存在性 + 归属判断）
#   app.utils.db.delete_product    —— 删除记录（数据库层会再次校验卖家身份，
#                                    并顺带清理磁盘上的商品图片文件）
# ================================================================
from flask import Blueprint, request, jsonify, g
from datetime import datetime

from app.middleware import rate_limit, jwt_auth_required, seller_required
from app.utils import db


user = Blueprint('delete_product', __name__)


# 统一响应封装函数：所有接口返回固定结构 {code, message, error, data, time}。
# 约定 code=0 表示业务成功；HTTP 状态码由参数 status 控制（400 参数错误、
# 403 无权限 / 404 资源不存在 / 500 服务器错误等），便于前端统一处理。
def build_response(code, message='', data=None, error=None, status=200):
    payload = {
        'code': code,
        'message': message,
        'error': error,
        'data': data,
        'time': datetime.utcnow().isoformat() + 'Z'
    }
    return jsonify(payload), status


# ------------------------------------------------------------------
# 视图函数：delete_product —— 删除商品
# 请求：DELETE /product/delete/<int:product_id>（无请求体，ID 走 URL 路径）
# 流程：按 product_id 查商品 → 不存在则返回 404 → 校验商品归属当前商家
#       （不匹配返回 403）→ 调用数据库删除 → 按结果返回成功或失败
# 返回值：成功 code=0；失败按情况返回 404（商品不存在）、
#         403（非本人商品 / 删除失败）、500（服务器异常）
# ------------------------------------------------------------------
@user.route('/product/delete/<int:product_id>', methods=['DELETE'])
@jwt_auth_required
@seller_required
@rate_limit(max_requests=100, window_seconds=60, per_user=True)
def delete_product(product_id):
    """
    删除商品
    需要JWT认证，且只有商品对应的商家可以删除商品
    """
    try:
        # 先按路径参数查商品：既判断“是否存在”，也取回其 seller_id
        # 供下一步的归属（越权）校验使用
        # 获取商品信息
        product = db.get_product_by_id(product_id)
        if not product:
            return build_response(
                code=404,
                error='商品不存在',
                message='商品不存在或已被删除',
                status=404
            )

        # 数据级权限校验：即使已通过 seller_required 的“商家角色”校验，
        # 仍需比较商品的归属商家与当前登录用户，防止越权删除他人商品
        # 检查权限：只有商品对应的商家可以删除商品
        if product.seller_id != g.user_id:
            return build_response(
                code=403,
                error='权限不足',
                message='只有商品对应的商家可以删除商品',
                status=403
            )

        # 真正执行删除：把当前登录用户 ID 一并传入，数据库层会再次校验
        # 商品归属，并顺带删除磁盘上的商品图片文件；成功返回 True
        # 删除商品
        success = db.delete_product(product_id, g.user_id)
        # 数据库层删除失败（如商品在两次查询之间已被删掉、或归属不一致），
        # 统一按 403 返回，避免向前端暴露内部细节
        if not success:
            return build_response(
                code=403,
                error='删除失败',
                message='删除商品失败，可能是权限不足或商品不存在',
                status=403
            )

        # 业务成功：code=0，删除操作无需回传数据，仅返回成功提示
        return build_response(
            code=0,
            message='删除商品成功'
        )

    # 兜底异常处理：打印错误便于排查，并统一返回 500 响应
    except Exception as e:
        print(f"删除商品时出现错误: {e}")
        return build_response(
            code=500,
            error='服务器错误',
            message=f'删除商品时出现错误: {str(e)}',
            status=500
        )
