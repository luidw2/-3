"""
安全中间件模块
提供JWT认证、参数验证、频率限制和安全响应头等中间件

本文件是 middleware 包的“统一导出入口”：它本身不写中间件实现，只做集中导入与导出。
好处是业务蓝图只需一行 `from app.middleware import xxx` 即可使用某个装饰器，
应用工厂 app/__init__.py 也能用 `from app.middleware import *` 一次性拿到全部成员。

各导出成员职责速览（具体实现见对应子模块，答辩可逐个展开）：
- jwt_auth_required    JWT 认证装饰器：校验 Authorization 头中的 access token，
                       并把用户身份(user_id/role 等)注入 Flask 的 g 对象；
- validate_params      参数校验装饰器：必填字段检查 + 字段格式校验 + 输入清洗；
- sanitize_input       输入清洗函数：对字符串/字典/列表递归处理，
                       命中 SQL 注入 / XSS 危险模式时返回 None（拒绝信号）；
- rate_limit           频率限制装饰器：按 IP / 按用户做滑动时间窗口内的请求计数，
                       防暴力破解与刷接口；
- security_headers     安全响应头中间件（应用级）：注册 app.after_request 钩子，
                       统一给每个响应加 CSP/HSTS/禁缓存等安全头；
- seller_required      商家角色权限装饰器：要求 g.role == 'seller'，否则返回 403；
- user_required        普通用户角色权限装饰器：要求 g.role == 'user'，否则返回 403。
"""

# 集中导入各子模块对外公开的装饰器/函数，供全项目统一引用
from .jwt_auth import jwt_auth_required
from .param_validation import validate_params, sanitize_input
from .rate_limit import rate_limit
from .security_headers import security_headers
from .permissions import seller_required, user_required, admin_required, auditor_required, staff_required

# __all__ 声明 “from app.middleware import *” 实际导出的名字，
# 避免把子模块的内部符号一并暴露出去
__all__ = [
    'jwt_auth_required',
    'validate_params',
    'sanitize_input',
    'rate_limit',
    'security_headers',
    'seller_required',
    'user_required',
    'admin_required',
    'auditor_required',
    'staff_required'
]
