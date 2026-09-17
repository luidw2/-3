"""
模块：加入购物车接口（add_to_shopping_car）
============================================
功能：接收前端「把某商品加入购物车」的请求，把 商品ID + 数量 写入当前登录用户的
      购物车数据表，并返回新建的购物车条目信息，供前端更新购物车角标/列表。

数据流：前端(Vue) → POST /user/add_to_shopping_car/<商品ID>
        → 登录态中间件(@jwt_auth_required / @user_required)校验 JWT
        → db.add_to_cart 写入购物车表 → 统一响应体返回前端

讲解要点：
  1) 用户身份不信任前端传参，而是从登录态取 g.user_id（由登录中间件解析 JWT 后
     写入 Flask 上下文对象 g），保证只能往「自己的购物车」里加商品；
  2) 接口带单IP限流(@rate_limit：每60秒最多100次)，防止脚本高频刷购物车；
  3) 成功/失败统一走 build_response 封装：200 成功 / 400 业务失败 / 500 服务器异常。
"""
from flask import Blueprint, request, jsonify,g
from datetime import datetime

from app.middleware import rate_limit
from app.utils import db, my_bcrypt, auth
from app.middleware import jwt_auth_required, user_required, rate_limit

# 创建蓝图：把本文件的路由注册到 user 蓝图下（路由前缀在应用初始化时统一挂载）
user = Blueprint('add_to_shopping_car', __name__)


def build_response(code, message='', data=None, error=None, status=200):
    """统一的接口响应封装函数：保证所有接口返回结构一致，方便前端统一解析。

    :param code:    业务状态码（200 成功 / 400 参数或业务错误 / 404 资源不存在 / 500 服务器异常）
    :param message: 展示给前端的提示信息
    :param data:    成功时的业务数据（本模块为新建的购物车条目）
    :param error:   失败时的错误说明
    :param status:  HTTP 状态码，默认 200
    :return: (jsonify(payload), status)，Flask 据此输出 JSON 响应
    """
    # 组装统一响应体，并附加服务器 UTC 时间戳便于联调排查
    payload = {
        'code': code,
        'message': message,
        'error': error,
        'data': data,
        'time': datetime.utcnow().isoformat() + 'Z'
    }
    return jsonify(payload), status


@user.route('/user/add_to_shopping_car/<int:product_id>', methods=['POST'])
@rate_limit(max_requests=100, window_seconds=60, per_ip=True)
@jwt_auth_required
@user_required
def add_to_shopping_car(product_id):
    """加入购物车接口：前端点击「加入购物车」时调用（POST /user/add_to_shopping_car/<product_id>）。

    :param product_id: 路径参数 —— 要加入购物车的商品 ID
    请求体(JSON)：quantity —— 购买数量，缺省时按 1 件处理
    返回：成功 200，data 含新建条目(cart_item_id/product_id/product_name/quantity)；
          商品或用户不存在 → 业务码 400；发生异常 → 500。
    """
    # 读取前端提交的 JSON 请求体；没有请求体时兜底为空字典，避免取不到字段
    data = request.get_json() or {}
    quantity = data.get('quantity', 1)   # 取购买数量，未传默认 1
    
    try:
        # 调用数据访问层：写入购物车表（内部会校验商品、用户是否存在并执行插入）
        cart_item = db.add_to_cart(g.user_id, product_id, quantity)
        # 返回值非空 → 插入成功
        if cart_item:
            # 成功分支：把新增的购物车条目信息返回给前端
            return build_response(
                code=200,
                message='商品添加到购物车成功',
                data={
                    'cart_item_id': cart_item['id'],
                    'product_id': cart_item['product_id'],
                    'product_name': cart_item['product_name'],
                    'quantity': cart_item['quantity']
                }
            )
        else:
            # 失败分支：返回空说明商品或用户不存在 → 业务错误码 400
            return build_response(
                code=400,
                error='添加失败',
                message='商品或用户不存在',
                status=400
            )
    except Exception as e:
        # 异常兜底：数据库异常等未知错误统一返回 500，error 字段带具体原因便于排查
        return build_response(
            code=500,
            error='添加失败',
            message=str(e),
            status=500
        )