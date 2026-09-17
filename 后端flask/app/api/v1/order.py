"""
模块：订单接口（order）
======================
功能：提供「下单」与「订单查询」两类接口，共三条路由：
  1) POST /user/create_order              —— 根据当前用户购物车内容创建一笔订单（结算）；
  2) GET  /user/profile_order             —— 分页查询当前用户的订单列表（个人中心「我的订单」）；
  3) GET  /user/profile_order/<order_id>  —— 查询某一笔订单的详情（须属于当前用户）。

设计说明：
  · 业务逻辑集中在数据访问层(db 模块)：db.create_order / db.get_user_orders /
    db.get_order_detail（事务、明细、归属校验等细节在 db 层完成），
    本模块只做「读参数 → 调 db → 统一响应」的接口层封装；
  · 订单状态约定：下单成功初始为 pending（待支付），后续由支付回调模块
    app/api/v1/callback.py 在模拟银行支付成功后改为 paid（已支付）；
  · 下单成功后返回的订单信息中带有 order_id 与金额，前端据此进入
    app/api/v1/pay.py 的「生成支付链接」流程发起模拟支付。
"""
from flask import Blueprint, request, jsonify, g
from datetime import datetime

from app.middleware import rate_limit
from app.utils import db, my_bcrypt, auth
from app.middleware import jwt_auth_required, user_required, rate_limit

# 创建蓝图：order 蓝图承载下单与订单查询路由
user = Blueprint('order', __name__)

def build_response(code, message='', data=None, error=None, status=200):
    """统一的接口响应封装函数：保证所有接口返回结构一致，方便前端统一解析。

    :param code:    业务状态码（200 成功 / 400 参数或业务错误 / 404 资源不存在 / 500 服务器异常）
    :param message: 展示给前端的提示信息
    :param data:    成功时的业务数据（如订单信息、订单列表）
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


@user.route('/user/create_order', methods=['POST'])
@rate_limit(max_requests=100, window_seconds=60, per_ip=True)
@jwt_auth_required
@user_required
def create_order():
    """创建订单接口：前端在购物车页点「去结算 / 提交订单」时调用（POST /user/create_order）。

    数据流：前端(带JWT登录态) → 本接口从登录态取 user_id
          → db.create_order(user_id)：在数据访问层把当前用户的购物车结算生成一笔订单
            （订单初始状态为待支付 pending；订单明细、事务等具体逻辑在 db 层完成）
          → 返回订单信息；前端随后可用其中的 order_id 进入模拟支付流程(pay.py)。
    返回：成功 200，data 为订单信息 order_info（订单号、金额、状态等）；
          购物车为空或商品不可下单 → 400；发生异常 → 500。
    """
    try:
        # 获取当前用户ID（由登录中间件解析 JWT 后写入 g.user.id，不信任前端传参）
        user_id = g.user.id
        
        # 调用创建订单函数：在数据访问层完成下单（订单与明细生成、清空购物车，事务在 db 层内）
        order_info = db.create_order(user_id)
        
        # db 层返回空 → 下单失败（购物车为空 / 商品不存在等）→ 返回业务错误 400
        if not order_info:
            return build_response(400, message='创建订单失败，购物车为空或商品不存在')
        
        # 下单成功：把订单信息回传前端 —— 后续「模拟支付」接口(pay.py)就靠其中的 order_id 定位订单
        return build_response(200, message='订单创建成功', data=order_info)
    except Exception as e:
        # 异常兜底：数据库/事务出错统一返回 500（error 字段便于开发阶段排查）
        return build_response(500, message='服务器内部错误', error=str(e))

@user.route('/user/profile_order', methods=['GET'])
@rate_limit(max_requests=100, window_seconds=60, per_ip=True)
@jwt_auth_required
@user_required
def get_user_orders():
    """分页查询当前用户的订单列表：个人中心「我的订单」页调用（GET /user/profile_order）。

    查询串参数：page —— 页码，默认 1；page_size —— 每页条数，默认 10。
    返回：成功 200，data 为订单列表数据；列表为空 / 查询失败 → 400；异常 → 500。
    """
    try:
        user_id = g.user.id   # 当前登录用户：只能查自己的订单
        page = request.args.get('page', 1, type=int)             # 页码，默认第 1 页
        page_size = request.args.get('page_size', 10, type=int)  # 每页条数，默认 10 条
        
        # 调用数据访问层做分页查询（只查当前用户自己的订单）
        orders = db.get_user_orders(user_id, page, page_size)
        
        # 查询结果为空 → 视为业务失败返回 400（前端据此提示「暂无订单」）
        if not orders:
            return build_response(400, message='获取订单列表失败')
        
        # 查询成功：把订单列表数据返回前端渲染
        return build_response(200, message='获取订单列表成功', data=orders)
    except Exception as e:
        # 异常兜底：查询出错统一返回 500
        return build_response(500, message='服务器内部错误', error=str(e))

@user.route('/user/profile_order/<int:order_id>', methods=['GET'])
@rate_limit(max_requests=100, window_seconds=60, per_ip=True)
@jwt_auth_required
@user_required
def get_order_detail(order_id):
    """查询单笔订单详情接口：个人中心「订单详情」页调用（GET /user/profile_order/<order_id>）。

    :param order_id: 路径参数 —— 要查看详情的订单 ID
    说明：查询时同时传入当前 user_id，db 层会校验订单归属，
          防止用户越权查看他人订单（例如手改 URL 中的 order_id 试探）。
    返回：成功 200 返回订单详情数据；订单不存在或不属于当前用户 → 400；异常 → 500。
    """
    try:
        user_id = g.user.id   # 当前登录用户ID
        
        # 调用数据访问层查询订单详情（内部会校验该订单确实属于当前用户）
        order_detail = db.get_order_detail(order_id, user_id)
        
        # 查不到该订单，或订单不属于当前用户 → 返回业务错误 400
        if not order_detail:
            return build_response(400, message='订单不存在或不属于该用户')
        
        # 成功：把订单详情返回前端展示
        return build_response(200, message='获取订单详情成功', data=order_detail)
    except Exception as e:
        # 异常兜底：查询出错统一返回 500
        return build_response(500, message='服务器内部错误', error=str(e))

