# ================================================================
# 模块：update_product —— 商品更新（编辑）接口（后端 Flask 视图）
#
# 作用：
#   商家编辑“自己发布”的商品。先校验商品存在且归属当前商家，再解析前端
#   表单提交的新字段并逐项校验；可选地替换商品图片（新图落盘前先删除旧图
#   文件），最后调用数据库层更新记录并返回统一的 JSON 响应。
#
# 路由与 HTTP 方法：
#   PUT /product/update/<int:product_id> —— 更新指定 ID 的商品
#   （<int:product_id> 由 Flask 的 URL 转换器自动转为整数作为路径参数）
#
# 权限要求：
#   - jwt_auth_required：必须携带有效 JWT 登录凭证；
#   - seller_required：当前登录用户必须是“商家(seller)”角色；
#   - 业务层二次校验：只有商品归属商家本人（seller_id 与 g.user_id 一致）
#     才允许编辑。
#
# 涉及的工具 / 数据库函数：
#   app.utils.db.get_product_by_id —— 查商品，用于存在性与归属判断
#   app.utils.db.update_product    —— 按商品 ID + 卖家 ID 更新字段
#                                     （数据库层内部还会再次校验卖家身份）
#   werkzeug secure_filename / os —— 新图片保存与旧图片文件删除
# ================================================================
from flask import Blueprint, request, jsonify, g, current_app
from datetime import datetime, timezone
import os
from werkzeug.utils import secure_filename

from app.middleware import rate_limit, jwt_auth_required, seller_required
from app.utils import db


user = Blueprint('update_product', __name__)


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


# ------------------------------------------------------------------
# 视图函数：update_product —— 更新（编辑）商品
# 请求格式：multipart/form-data 表单字段
#   name（必填）、price（必填，非负整数，单位：分）、status（必填，
#   只能取 active/inactive）、description（可选）、image（可选，新图片文件）
# 流程：查商品 → 归属校验 → 解析并校验表单 → 可选换图（删旧图、存新图）
#       → 调数据库更新 → 返回结果
# 返回值：成功 code=0；失败按情况返回 404（商品不存在）、400（参数缺失/
#         格式非法）、403（非本人商品 / 更新失败）、500（服务器异常）
# ------------------------------------------------------------------
@user.route('/product/update/<int:product_id>', methods=['PUT'])
@jwt_auth_required
@seller_required
@rate_limit(max_requests=100, window_seconds=60, per_user=True)
def update_product(product_id):
    """
    编辑商品
    需要JWT认证，且只有商品对应的商家可以编辑商品
    """
    try:
        # 先查商品：确认记录存在，并取回原 seller_id / image_url，
        # 供归属校验与“是否需要删除旧图”的判断使用
        # 获取商品信息
        product = db.get_product_by_id(product_id)
        if not product:
            return build_response(
                code=404,
                error='商品不存在',
                message='商品不存在或已被删除',
                status=404
            )

        # 数据级权限校验：商品的归属商家必须等于当前登录用户，
        # 防止商家 A 越权编辑商家 B 发布的商品
        # 检查权限：只有商品对应的商家可以编辑商品
        if product.seller_id != g.user_id:
            return build_response(
                code=403,
                error='权限不足',
                message='只有商品对应的商家可以编辑商品',
                status=403
            )

        # 解析前端提交的表单字段（与创建接口相同的表单格式）。
        # 说明：这是“整体提交”式更新——name/price/status 必填，
        # description 可空，image 为可选的新图片文件字段
        # 处理 multipart/form-data 格式的请求
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        status = request.form.get('status')

        # 参数校验：任一必填项缺失或取值非法时立即返回 400，
        # 提前拦截坏数据，避免把脏数据传进数据库层
        # 验证参数
        if not name:
            return build_response(
                code=400,
                error='参数缺失',
                message='商品名称不能为空',
                status=400
            )
        if price is None:
            return build_response(
                code=400,
                error='参数缺失',
                message='商品价格不能为空',
                status=400
            )
        try:
            price = int(price)
        except ValueError:
            return build_response(
                code=400,
                error='参数错误',
                message='商品价格必须是整数',
                status=400
            )
        # 与创建接口一致：价格不允许为负数，最终以“分”为单位入库
        if price < 0:
            return build_response(
                code=400,
                error='参数错误',
                message='商品价格必须大于等于0',
                status=400
            )
        if status not in ['active', 'inactive']:
            return build_response(
                code=400,
                error='参数错误',
                message='商品状态必须是active或inactive',
                status=400
            )

        # 处理文件上传
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # 确保上传目录存在
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                # 换图处理：原商品已绑定图片（image_url 非空）时，先尝试把
                # 磁盘上的旧图文件删除，避免上传新图后残留旧文件；
                # 删除失败只打印日志后继续（不影响主流程）
                # 删除旧照片
                if product.image_url:
                    old_image_path = os.path.join(current_app.root_path, product.image_url.lstrip('/'))
                    if os.path.exists(old_image_path):
                        try:
                            os.remove(old_image_path)
                            print(f"旧照片已删除: {old_image_path}")
                        except Exception as e:
                            print(f"删除旧照片失败: {e}")
                
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

        # 执行更新：把商品 ID、当前登录用户 ID（seller_id，供数据库层做
        # 归属校验）以及本次提交的各字段整体传入。
        # 说明：未上传新图时 image_url 为 None，数据库层会把传入的允许字段
        # 逐一写回（含显式为 None 的字段）
        # 更新商品
        updated_product = db.update_product(
            product_id=product_id,
            seller_id=g.user_id,
            name=name,
            description=description,
            price=price,
            status=status,
            image_url=image_url
        )
        # 更新失败（商品不存在或归属不一致，数据库层返回 None），按 403 返回
        if not updated_product:
            return build_response(
                code=403,
                error='更新失败',
                message='更新商品失败，可能是权限不足或商品不存在',
                status=403
            )

        # 业务成功：code=0，更新接口无需回传商品数据，前端可自行刷新列表
        return build_response(
            code=0,
            message='更新商品成功'
        )

    # 兜底异常处理：打印错误便于排查，并统一返回 500 响应
    except Exception as e:
        print(f"更新商品时出现错误: {e}")
        return build_response(
            code=500,
            error='服务器错误',
            message=f'更新商品时出现错误: {str(e)}',
            status=500
        )
