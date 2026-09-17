# ================================================================
# 模块：create_product —— 商品创建接口（后端 Flask 视图）
#
# 作用：
#   接收商家以 multipart/form-data 表单提交的商品信息（商品名称、价格、
#   描述、状态以及可选的商品图片），依次完成参数校验、图片保存、数据库
#   写入，最后把结果包装成统一的 JSON 响应返回给前端。
#
# 路由与 HTTP 方法：
#   POST /product/create —— 创建一条商品
#
# 权限要求：
#   - jwt_auth_required：必须先携带有效 JWT 登录凭证（认证中间件会把
#     当前登录用户信息写入 g，供视图读取）；
#   - seller_required：当前登录用户必须是“商家(seller)”角色；
#   - rate_limit：接口限流保护（每 60 秒窗口内每用户最多 100 次请求）。
#
# 涉及的工具 / 数据库函数：
#   app.middleware：jwt_auth_required / seller_required / rate_limit
#   app.utils.db.create_product —— 把商品记录写入数据库（价格单位：分）
#   werkzeug.utils.secure_filename + os + current_app —— 图片文件落盘
# ================================================================
from flask import Blueprint, request, jsonify, g, current_app
from datetime import datetime
import os
from werkzeug.utils import secure_filename

from app.middleware import rate_limit, jwt_auth_required, seller_required
from app.utils import db


user = Blueprint('create_product', __name__)


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
# 视图函数：create_product —— 创建商品
# 请求格式：multipart/form-data 表单字段
#   name（必填）、price（必填，非负整数，单位：分）、
#   description（可选）、status（可选，默认 active，只能取 active/inactive）、
#   image（可选，图片文件上传字段）
# 处理流程：解析表单 → 参数校验 → 可选图片落盘 → 写入数据库 → 返回结果
# 返回值：成功 code=0 且 data 为完整商品信息；
#         失败按情况返回 400（参数缺失/价格或状态不合法）、500（服务器错误）
# ------------------------------------------------------------------
@user.route('/product/create', methods=['POST'])
@jwt_auth_required
@seller_required
@rate_limit(max_requests=100, window_seconds=60, per_user=True)
def create_product():
    """
    创建商品
    需要JWT认证，且只有商家可以创建商品
    """
    try:
        # 处理 multipart/form-data 格式的请求
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        status = request.form.get('status', 'active')

        # 必填项校验：all() 要求列表内元素都为“真”，即名称与价格必须同时提供
        if not all([name, price]):
            return build_response(
                code=400,
                error='参数缺失',
                message='商品名称和价格为必填项',
                status=400
            )

        # 价格格式校验：价格必须以“分”为单位的非负整数（1 元 = 100 分）。
        # 利用 int() 转换抛异常 + 负数时手动 raise，把所有非法价格统一拦截
        # 验证价格格式
        try:
            price = int(price)
            if price < 0:
                raise ValueError
        except (ValueError, TypeError):
            return build_response(
                code=400,
                error='参数错误',
                message='价格必须是非负整数（单位：分）',
                status=400
            )

        # 验证状态
        if status not in ['active', 'inactive']:
            return build_response(
                code=400,
                error='参数错误',
                message='商品状态必须是 active 或 inactive',
                status=400
            )

        # 处理可选图片上传：请求体中不携带 image 字段、或文件名为空时，
        # 不执行上传逻辑，image_url 保持 None（该商品没有图片）
        # 处理文件上传
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # 确保上传目录存在
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                # 生成安全的文件名
                filename = secure_filename(file.filename)
                # 为避免文件名冲突，添加时间戳
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{filename}"
                
                # 保存文件
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                # 生成访问路径
                image_url = f"/static/uploads/{filename}"

        # 创建商品：把前面解析并校验通过的字段写入数据库
        # seller_id 取自已登录用户（认证中间件设置的 g.user_id），
        # 从源头保证新商品归属当前商家本人，而不是信任前端传入
        # 创建商品
        product = db.create_product(
            seller_id=g.user_id,
            name=name,
            price=price,
            description=description,
            status=status,
            image_url=image_url
        )

        # 数据库层返回空对象说明写入未成功（如字段约束不满足），按 500 返回
        if not product:
            return build_response(
                code=500,
                error='创建失败',
                message='创建商品失败，请稍后重试',
                status=500
            )

        # 构建响应数据：把 ORM 商品对象转换为前端可用的字典
        # （时间字段转 ISO 字符串，避免直接序列化 datetime 对象）
        # 构建响应数据
        product_data = {
            'id': product.id,
            'seller_id': product.seller_id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'status': product.status,
            'image_url': product.image_url,
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'updated_at': product.updated_at.isoformat() if product.updated_at else None
        }

        # 业务成功：code=0，data 中回传刚创建商品的完整信息（含自增 id、时间戳）
        return build_response(
            code=0,
            message='创建商品成功',
            data=product_data
        )

    # 兜底异常处理：任何未预料的异常（含图片保存失败等）都会走到这里，
    # 打印错误信息便于排查，并统一返回 500，保证接口不会直接崩溃
    except Exception as e:
        print(f"创建商品时出现错误: {e}")
        return build_response(
            code=500,
            error='服务器错误',
            message=f'创建商品时出现错误: {str(e)}',
            status=500
        )
