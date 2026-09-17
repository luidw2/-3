"""
参数验证中间件
功能：检查必填字段，防护XSS/SQL注入
防护威胁：注入攻击（XSS、SQL注入）

保护什么：
- 拦截把恶意载荷拼进请求参数的攻击：
  * SQL 注入：SELECT / UNION / EXEC 以及注释符(--、#、/*)、分号拼接语句等；
  * XSS：<script> 标签、javascript: 伪协议、onerror 等事件属性、iframe 等。
怎么工作（请求入口的“双层闸门”）：
1) 黑名单正则预检：SQL_INJECTION_PATTERNS / XSS_PATTERNS 命中即判定为可疑，
   sanitize_input 返回 None，由 validate_params 统一转成 400 拒绝请求；
2) 白名单式转义：未命中危险模式的文本再用 html.escape 做 HTML 实体转义，
   即使残留特殊字符也无法被浏览器当作可执行代码解析；对 dict/list 递归处理，
   因此能覆盖 JSON 请求体中任意深度的嵌套字段；
3) validate_params 装饰器把“取参 -> 必填检查 -> 清洗 -> 格式校验”串成固定流程，
   清洗后的数据挂到 request.validated_data，业务视图只读取“可信数据”，
   不再直接信任原始 request.json，实现“入口统一净化”。

设计说明（答辩补充）：正则拦截属于入口兜底；分层防御中 SQL 注入的根本防线
是数据访问层的参数化查询，XSS 的根本防线是输出端编码/前端框架转义，
本中间件负责在请求入口做第一道拦截，三层叠加才能构成完整防护。
"""

import re
import html
from functools import wraps
from flask import request, jsonify
from typing import List, Dict, Optional, Callable

# ============ 危险输入“黑名单”（入口层检测用） ============
# 只用于“事前检测”：命中即整体拒绝，防止恶意载荷进入业务层
# SQL注入关键词模式（更精确的模式，减少误报）
SQL_INJECTION_PATTERNS = [
    # SQL语句关键字组合（检测常见注入模式）
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\s+.*\s+FROM\b)",
    r"(\bUNION\s+SELECT\b)",
    r"(\bEXEC\s*\()",
    r"(\bEXECUTE\s*\()",
    # SQL注释和特殊字符组合
    r"(--|#|/\*).*(SELECT|INSERT|UPDATE|DELETE|DROP)",
    r"(;\s*(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER))",
    # 布尔逻辑注入
    r"(\b(OR|AND)\s+\d+\s*=\s*\d+\s*--)",
    r"(\b(OR|AND)\s+['\"]\w+['\"]\s*=\s*['\"]\w+['\"]\s*--)",
    # 存储过程调用
    r"(\bxp_\w+\s*\()",
    r"(\bsp_\w+\s*\()",
    # 危险字符组合
    r"('|\"|;)\s*(OR|AND|UNION|SELECT)",
]

# XSS攻击模式
XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe[^>]*>",
    r"<object[^>]*>",
    r"<embed[^>]*>",
    r"<img[^>]*onerror\s*=",
    r"<svg[^>]*onload\s*=",
]


def sanitize_input(data: any, max_length: int = 1000) -> any:
    """
    清理输入数据，防护XSS和SQL注入

    Args:
        data: 输入数据（字符串、字典、列表等）
        max_length: 最大长度限制

    Returns:
        清理后的数据，如果包含危险内容则返回None
        （None 是给调用方的“拒绝信号”：validate_params 看到 None 即返回 400，
         不会再把它交给业务层）

    补充说明（答辩讲解用）：
    - 长度超限(max_length)直接返回 None，防止超长载荷拖垮正则与存储；
    - 只对字符串做检测与转义；dict/list 走递归，保证 JSON 任意深度的
      嵌套字段都被同一条规则覆盖；
    - 检测在 html.escape 转义“之前”执行：若先转义再检测，恶意载荷变形后
      可能绕过正则，因此检测顺序本身就是一处防御细节；
    - 值为 None 的字段原样保留（见代码：值为 None 不视为“被清理掉”）。
    """
    if isinstance(data, str):
        original_data = data
        # 检查长度
        if len(data) > max_length:
            return None

        # 检查SQL注入模式（在转义前检查，不区分大小写）
        data_upper = data.upper()
        for pattern in SQL_INJECTION_PATTERNS:
            if re.search(pattern, data_upper, re.IGNORECASE):
                return None

        # 检查XSS模式（在转义前检查）
        for pattern in XSS_PATTERNS:
            if re.search(pattern, data, re.IGNORECASE):
                return None

        # HTML转义，防护XSS（但保留原始值用于存储，转义用于显示）
        # 注意：这里只进行基本的清理，实际存储时可能需要根据场景决定是否转义
        # 对于密码等敏感字段，不应该进行HTML转义
        sanitized = html.escape(data)

        return sanitized.strip()

    elif isinstance(data, dict):
        result = {}
        for key, value in data.items():
            sanitized_value = sanitize_input(value, max_length)
            if sanitized_value is None and value is not None:
                # 如果值被清理为None，说明包含危险内容
                return None
            result[key] = sanitized_value
        return result

    elif isinstance(data, list):
        result = []
        for item in data:
            sanitized_item = sanitize_input(item, max_length)
            if sanitized_item is None and item is not None:
                # 如果项被清理为None，说明包含危险内容
                return None
            result.append(sanitized_item)
        return result

    return data


def validate_params(required_fields: List[str] = None,
                    field_validators: Dict[str, Callable] = None,
                    sanitize: bool = True):
    """
    参数验证装饰器
    检查必填字段，验证字段格式，清理输入数据

    Args:
        required_fields: 必填字段列表
        field_validators: 字段验证器字典，key为字段名，value为验证函数
        sanitize: 是否清理输入数据

    使用方法：
    @user.route('/api', methods=['POST'])
    @validate_params(required_fields=['username', 'password'],
                    field_validators={'email': validate_email})
    def api_endpoint():
        data = request.json
        username = data.get('username')
        ...

    返回码约定（答辩讲解用）：
    - 400：缺必填字段 / 清洗发现危险内容 / 字段格式校验失败或校验器抛异常，
      返回体统一为 code=400、error=参数验证失败，message 说明具体原因；
    - 全部通过：把清洗/校验后的数据挂到 request.validated_data，
      然后调用视图函数；视图内应统一从 request.validated_data 取参，
      不再信任原始请求数据。

    装饰器与视图的完整执行链：
    取参 -> 必填检查 -> （可选）输入清洗 -> 字段格式校验 -> 放行视图函数。
    """
    if required_fields is None:
        required_fields = []
    if field_validators is None:
        field_validators = {}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取请求数据
            # 取值策略：优先取 JSON 请求体（前端主要用 JSON），
            # 其次兼容表单(form)与查询参数(query string)两种携带方式
            if request.is_json:
                data = request.json or {}
            elif request.form:
                data = request.form.to_dict()
            else:
                data = request.args.to_dict()

            # 检查必填字段
            # 缺失、为 None、空字符串都视为“未提供”，收集后统一提示
            missing_fields = []
            for field in required_fields:
                if field not in data or data[field] is None or data[field] == '':
                    missing_fields.append(field)

            if missing_fields:
                return jsonify({
                    'code': 400,
                    'error': '参数验证失败',
                    'message': f'缺少必填字段: {", ".join(missing_fields)}',
                    'time': None
                }), 400

            # 清理输入数据
            # 清洗阶段：命中危险模式或超长时 sanitize_input 返回 None -> 400；
            # 清洗通过后整体覆盖原 data，保证后续校验与视图拿到的都是干净数据
            if sanitize:
                try:
                    sanitized_data = sanitize_input(data)
                    # 检查是否有数据被清理为None（表示包含危险内容）
                    if sanitized_data is None:
                        return jsonify({
                            'code': 400,
                            'error': '参数验证失败',
                            'message': '输入包含非法字符或存在安全风险',
                            'time': None
                        }), 400

                    # 检查必填字段是否被清理为None或为空
                    for field in required_fields:
                        if field not in sanitized_data or sanitized_data[field] is None or sanitized_data[field] == '':
                            # 如果原始数据中有值但清理后为空，说明包含危险内容
                            if field in data and data[field]:
                                return jsonify({
                                    'code': 400,
                                    'error': '参数验证失败',
                                    'message': f'字段 {field} 包含非法内容',
                                    'time': None
                                }), 400

                    data = sanitized_data
                except Exception as e:
                    return jsonify({
                        'code': 400,
                        'error': '参数验证失败',
                        'message': f'数据清理失败: {str(e)}',
                        'time': None
                    }), 400

            # 字段格式验证
            # 对配置了校验器的字段逐个调用校验函数；
            # 校验函数返回 False（或抛出异常）即判定格式不合法 -> 400
            for field, validator in field_validators.items():
                if field in data:
                    try:
                        if not validator(data[field]):
                            return jsonify({
                                'code': 400,
                                'error': '参数验证失败',
                                'message': f'字段 {field} 格式不正确',
                                'time': None
                            }), 400
                    except Exception as e:
                        return jsonify({
                            'code': 400,
                            'error': '参数验证失败',
                            'message': f'字段 {field} 验证失败: {str(e)}',
                            'time': None
                        }), 400

            # 将清理后的数据注入到request对象中
            # 校验与清洗全部通过后，把可信数据挂到 request.validated_data，
            # 视图函数统一从这里取值，避免每个视图各自重复校验一遍
            request.validated_data = data

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# 字符串长度校验器：返回 True 表示 value 是字符串且长度落在 [min_len, max_len]
# 区间内；常作为 field_validators 的值传给 validate_params
def validate_string_length(value: str, min_len: int = 1, max_len: int = 100) -> bool:
    """验证字符串长度"""
    if not isinstance(value, str):
        return False
    return min_len <= len(value) <= max_len


# 邮箱格式校验器：用正则对整串做匹配（^...$ 全串校验），
# 格式合法返回 True；校验失败时由 validate_params 统一返回 400
def validate_email_format(email: str) -> bool:
    """验证邮箱格式"""
    if not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# 用户名格式校验器：只允许字母、数字、下划线且长度为 3~20，
# 从格式层面杜绝特殊字符进入用户名（防注入/防乱码）
def validate_username_format(username: str) -> bool:
    """验证用户名格式（字母、数字、下划线，3-20个字符）"""
    if not isinstance(username, str):
        return False
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))
