"""
模块：购物车查询 / 修改（shopping_cart_profile）
================================================
功能：本模块提供两个与购物车展示、修改相关的接口：
  1) GET  /user/shopping_cart_profile —— 查询当前用户的购物车（含商品信息与合计金额）；
  2) PUT  /user/shopping_cart_update/<product_id> —— 修改某商品的购买数量，
     数量传 0 时表示把该商品移出购物车（即删除对应条目）。

说明：两个接口都要求用户已登录（@jwt_auth_required / @user_required），
      通过 g.user_id / g.username 区分当前用户，保证「只能查看/操作自己的购物车」；
      购物车单价与合计金额一律以服务端商品表价格为准（不信任前端计算值）。
"""
from flask import Blueprint, request, jsonify, g
from datetime import datetime

from app.middleware import rate_limit
from app.utils import db, my_bcrypt, auth
from app.middleware import jwt_auth_required, user_required, rate_limit

# 创建蓝图：本文件的购物车接口都注册在 user 蓝图下
user = Blueprint('shopping_cart_profile', __name__)


def build_response(code, message='', data=None, error=None, status=200):
    """统一的接口响应封装函数：保证所有接口返回结构一致，方便前端统一解析。

    :param code:    业务状态码（200 成功 / 400 参数或业务错误 / 404 资源不存在 / 500 服务器异常）
    :param message: 展示给前端的提示信息
    :param data:    成功时的业务数据（如购物车条目、商品信息等）
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


@user.route('/user/shopping_cart_profile', methods=['GET'])
@rate_limit(max_requests=100, window_seconds=60, per_ip=True)
@jwt_auth_required
@user_required
def get_shopping_cart():
    """查询当前用户购物车接口：前端进入「购物车」页面时调用（GET /user/shopping_cart_profile）。

    数据流：前端 → 按当前登录用户(g.user_id)查出其所有购物车条目，
          并连同商品信息一起返回 → 前端渲染商品列表并展示合计金额。
    返回：data.items —— 条目数组，每条含 cart_item_id/product_id/商品名/单价/图片/
                      数量/小计 subtotal/available(商品是否仍上架)/创建更新时间；
          data.total_items —— 条目总数；data.total_price —— 购物车合计金额。
          查询出错时返回业务码 500。
    """
    try:
        # 使用优化后的查询方法，一次性加载所有商品信息
        # （联表把「购物车条目 + 对应商品」一次查出，避免逐条查商品造成 N+1 查询问题）
        cart_items = db.get_cart_items_with_products(g.user_id)

        items_data = []     # 处理后待返回的条目列表（ORM 对象需转成纯字典才可 JSON 序列化）
        total_price = 0     # 购物车合计金额（逐条累加小计得到）
        for item in cart_items:
            # item 是购物车条目对象；item.product 是通过 ORM 关系取到的关联商品对象
            product = item.product
            # 商品可能已下架/被删(product 为 None)：单价按 0 处理，前端可用 available 字段提示
            price = product.price if product else 0
            subtotal = price * item.quantity    # 小计 = 单价 × 数量
            total_price += subtotal             # 累加到合计金额

            # 组装单条购物车条目的返回数据：
            #   金额全部以服务端商品表为准（单价 price、小计 subtotal、合计 total_price，
            #   不信任前端计算值）；时间字段转为 isoformat 字符串保证可 JSON 序列化；
            #   available 表示商品是否仍存在（false 时前端应禁止对该条目下单）
            item_info = {
                'cart_item_id': item.id,
                'product_id': item.product_id,
                'product_name': item.product_name,
                'quantity': item.quantity,
                'price': price,                                # 单价（来自商品表）
                'image_url': product.image_url if product else None,
                'subtotal': subtotal,                          # 小计
                'available': product is not None,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None
            }
            items_data.append(item_info)   # 加入待返回列表

        # 可选：记录审计日志 —— 记录「谁在何时查看了购物车」，便于安全审计追溯
        db.log_security_event('CART_VIEW', g.username, f'购物车含{len(items_data)}件商品')
        # 返回成功：条目列表 + 条目总数 + 合计金额（合计由后端累加，前端只做展示）
        return build_response(
            code=200,
            message='获取购物车成功',
            data={
                'items': items_data,
                'total_items': len(items_data),
                'total_price': total_price
            }
        )
    except Exception as e:
        # 异常兜底：查询出错统一返回 500（不给用户暴露具体异常细节）
        return build_response(
            code=500,
            error='获取失败',
            message='服务器内部错误',
            status=500
        )


@user.route('/user/shopping_cart_update/<int:product_id>', methods=['PUT'])
@rate_limit(max_requests=100, window_seconds=60, per_ip=True)
@jwt_auth_required
@user_required
def update_shopping_cart(product_id):
    """修改购物车商品数量接口：前端在购物车页「改数量 / 删除商品」时调用（PUT /user/shopping_cart_update/<product_id>）。

    修改规则：quantity 必须是 >=0 的整数 ——
        quantity > 0：把该商品在购物车中的数量更新为新值；
        quantity == 0：等价于「把该商品移出购物车」（删除对应购物车条目）。
    :param product_id: 路径参数 —— 要修改数量的商品 ID
    返回：删除/更新成功 200；缺少 quantity 或数量非法 → 400；
          购物车中无此商品 → 404；删除失败 501、更新失败 502；其他异常 500。
    """
    try:
        # 打印一行请求日志：课程演示时便于在控制台观察每一次修改请求
        print(f"收到更新购物车请求，product_id: {product_id}, user_id: {g.user_id}")

        # 获取请求体中的数量
        data = request.get_json()
        if not data or 'quantity' not in data:
            print("缺少数量参数")
            return build_response(
                code=400,
                error='参数错误',
                message='缺少数量参数',
                status=400
            )

        quantity = data['quantity']
        print(f"请求数量: {quantity}")

        # 验证数量是否为整数且大于等于0：数量非法直接拒绝，避免脏数据写入数据库
        if not isinstance(quantity, int) or quantity < 0:
            print("数量参数无效")
            return build_response(
                code=400,
                error='参数错误',
                message='数量必须是大于等于0的整数',
                status=400
            )

        # 查找购物车中的商品项（按「当前用户 + 商品ID」定位，确保改的是自己的购物车条目）
        cart_item = db.get_cart_item_by_user_and_product(g.user_id, product_id)
        print(f"查找购物车商品项结果: {cart_item}")

        # 购物车里没有该商品 → 返回 404（资源不存在）
        if not cart_item:
            print("购物车中不存在该商品")
            return build_response(
                code=404,
                error='商品不存在',
                message='购物车中不存在该商品',
                status=404
            )

        print(f"找到购物车商品项，cart_item_id: {cart_item.id}, product_id: {cart_item.product_id}, 当前数量: {cart_item.quantity}")

        # 更新商品数量：quantity==0 表示「移除商品」，其余值表示改为新数量
        if quantity == 0:
            # 如果数量为0，删除商品
            print(f"准备删除商品，cart_item_id: {cart_item.id}")
            result = db.remove_from_cart(g.user_id, cart_item.id)
            if result:
                print("商品删除成功")
                return build_response(
                    code=200,
                    message='商品从购物车删除成功'
                )
            else:
                print("商品删除失败")
                # 删除失败：返回 501（表示服务器内部错误，区别于正常业务失败）
                return build_response(
                    code=501,
                    error='删除失败',
                    message='服务器内部错误',
                    status=501
                )
        else:
            # 更新数量
            print(f"准备更新商品数量，cart_item_id: {cart_item.id}, 新数量: {quantity}")
            updated_item = db.update_cart_item_quantity(g.user_id, cart_item.id, quantity)
            print(f"更新商品数量结果: {updated_item}")

            if updated_item:
                # 确保返回的数据是可序列化的
                print("更新成功，准备返回响应")
                return build_response(
                    code=200,
                    message='购物车商品数量更新成功',
                    data={
                        'cart_item_id': updated_item['id'],
                        'product_id': updated_item['product_id'],
                        'quantity': updated_item['quantity']
                    }
                )
            else:
                print("更新失败")
                # 更新失败：返回 502（表示服务器内部错误）
                return build_response(
                    code=502,
                    error='更新失败',
                    message='服务器内部错误',
                    status=502
                )
    except Exception as e:
        # 异常兜底：打印完整堆栈便于排查问题，并向前端返回 500
        import traceback
        print(f"发生异常: {str(e)}")
        traceback.print_exc()
        return build_response(
            code=500,
            error='更新失败',
            message=f'服务器内部错误: {str(e)}',
            status=500
        )

