"""
user_riger_yanzheng.py —— 用户注册信息校验模块（严格的注册前校验）

在“数字证书登录”流程中的位置：
    本模块是“账号注册环节”的前置安全校验工具：用户在申请 / 绑定数字证书之前
    需要先创建账号，本模块对“用户名、密码强度、文本内容(XSS)”做统一校验，
    从源头拦截格式非法或携带注入 / 脚本攻击载荷的账号数据，
    保证入库账号干净、可安全地与后续的证书绑定流程配合。
"""
import re

# 用户名校验：
# 作用：按规则校验注册用户名是否合法（非空、长度、字符集、保留名、注入/XSS 关键字）。
# 参数：username —— 待校验的用户名
# 返回：合法返回 True；任一检查不通过则打印原因并返回 False
def validate_username(username: str):
    """
    - 长度4-20个字符
    - 只能包含字母、数字、下划线
    - 必须以字母开头
    - 不能是保留名称
    """
    # 基础检查
    if not username or not isinstance(username, str):
        print("用户名不能为空")
        return False
    # 长度检查
    if len(username) < 4 or len(username) > 20:
        print("用户名长度必须为4-20个字符")
        return False
    # 字符白名单检查
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        print("用户名必须以字母开头，且只能包含字母、数字和下划线")
        return False
    # 保留名称检查
    reserved_names = {'admin', 'root', 'system', 'administrator', 'null', 'undefined'}
    if username.lower() in reserved_names:
        print("该用户名是保留名称")
        return False
    # 安全威胁检查:sql与xss
    # 黑名单正则分两类：1) SQL 注入关键字(--、;、/* */、select/insert/update/delete/drop/union)；
    #                  2) XSS 脚本特征(<script、</script、javascript:、onclick/onload、eval(/alert()
    security_patterns = [
        r'.*(\-\-|;|\/\*|\*\/|select|insert|update|delete|drop|union).*',
        r'.*(<script|<\/script|javascript:|onclick|onload|eval\(|alert\().*'
    ]


    for pattern in security_patterns:
        if re.match(pattern, username, re.IGNORECASE):
            print("用户名包含不安全内容")
            return False
    return True


# 密码强度校验：
# 作用：强制用户设置高强度密码（长度≥12、大写/小写/数字/特殊字符齐备、不含空白，
#       并拒绝常见弱口令与简单重复/递增序列）。
# 参数：password —— 待校验的密码明文
# 返回：强度达标返回 True；否则打印原因并返回 False
def validate_password_strength(password: str) -> bool:
    """
    密码强度验证：
    - 长度至少 12
    - 同时包含大写、小写、数字、特殊字符
    - 不允许空白字符
    - 拒绝常见弱密码与简单重复/递增序列
    """
    if not password or not isinstance(password, str):
        print("密码不能为空")
        return False

    if len(password) < 12:
        print("密码长度至少为12个字符")
        return False

    if re.search(r"\s", password):
        print("密码不能包含空白字符")
        return False

    has_upper = re.search(r"[A-Z]", password) is not None
    has_lower = re.search(r"[a-z]", password) is not None
    has_digit = re.search(r"[0-9]", password) is not None
    has_special = re.search(r"[^A-Za-z0-9]", password) is not None

    if not (has_upper and has_lower and has_digit and has_special):
        print("密码需包含大写、小写、数字和特殊字符")
        return False

    # 常见弱密码黑名单：常见口令 / 5 个以上重复字符(aaaaaa 等) / 纯递增、递减数字序列
    #（比对时忽略大小写）
    weak_patterns = [
        r"^(?:password|admin|qwerty|letmein|welcome|iloveyou|abc123|123456|123456789)$",
        r"^(.)\1{5,}$",               # 重复字符
        r"^(?:0123456789|9876543210)$", # 纯递增/递减序列
    ]
    for pat in weak_patterns:
        if re.match(pat, password, re.IGNORECASE):
            print("密码过于简单")
            return False

    return True


# XSS 安全检测（黑名单式快速校验）：
# 作用：校验昵称 / 备注等用户输入文本中是否携带脚本、事件属性、危险协议等 XSS 载荷。
# 参数：text —— 待检查的文本（None 视为安全）
# 返回：文本安全返回 True；检测到危险模式返回 False
def is_xss_safe(text: str) -> bool:
    """
    基础 XSS 防护检查（黑名单检测）。
    - 拦截 <script>、事件处理属性、javascript: 协议等模式
    - 可用于昵称、备注等富文本前的快速校验
    注：最终仍建议输出时做 HTML 转义/内容清洗。
    """
    if text is None:
        return True
    if not isinstance(text, str):
        return False

    # XSS 特征黑名单：成对的 <script> 标签、javascript: 协议、事件属性赋值(onload/onerror/
    # onclick 等)、<iframe> 嵌套、<img onerror>、<svg onload> 等典型注入形态
    patterns = [
        r"<\s*script[\s\S]*?>[\s\S]*?<\s*/\s*script\s*>",
        r"javascript:\s*",
        r"on(?:load|error|click|mouseover|focus|input|submit)\s*=",
        r"<\s*iframe[\s\S]*?>",
        r"<\s*img[\s\S]*?onerror\s*=",
        r"<\s*svg[\s\S]*?onload\s*=",
    ]

    lowered = text.lower()
    for pat in patterns:
        if re.search(pat, lowered, re.IGNORECASE):
            return False
    return True
