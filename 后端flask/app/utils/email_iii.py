"""
email_iii.py —— 邮箱验证码工具模块（注册/绑定环节的邮箱验证）

在“数字证书登录”流程中的位置：
    注册 / 绑定等环节的邮箱验证：用户填写邮箱后，由本模块生成 6 位纯数字验证码，
    并以“本地模拟”方式发送（打印到控制台，未接入真实 SMTP 邮件服务），
    验证码连同过期时间缓存在内存字典中；用户提交邮箱 + 验证码时，
    先做格式校验，再由 verify_email() 核对验证码是否正确、是否过期。
"""
import random
import string
from datetime import datetime, timedelta
import re
from typing import Optional
###########
# 生成纯数字验证码：
# 参数：length —— 验证码位数；返回：从 0-9 中随机抽取 length 位拼接而成的字符串
def generate_verification_code(length):
    """生成随机验证码"""
    verification_code = ''.join(random.choices(string.digits, k=length))
    return verification_code


# 内存验证码仓库：{邮箱: {"code": 验证码, "expire_at": 过期时间}}
# 说明：验证码保存在内存字典而非数据库，服务重启即清空，仅适用于演示/课程设计场景；
# CODE_TTL_MINUTES：验证码有效期（分钟），超时未使用则作废
EMAIL_CODE_STORE = {}
CODE_TTL_MINUTES = 10


# 发送邮箱验证码（本地模拟实现）：
# 作用：1) 生成 6 位验证码；2) 计算过期时间(当前 UTC + 10 分钟)并存入内存仓库；
#       3) 把“验证码已发送”打印到控制台（课程演示环境，未接真实邮件服务）。
# 参数：email —— 收件邮箱
# 返回：邮箱非空且已入库返回 True；邮箱为空返回 False
def send_verification_email(email):
    """发送验证邮件（本地模拟，存储验证码并打印提示）。"""

    if not email:
        print("错误：未提供邮箱地址")
        return False
    code = generate_verification_code(6)
    # 过期时间 = 当前(UTC)时间 + 有效期；连同验证码一起存入内存仓库，等待用户回填核对
    expire_at = datetime.utcnow() + timedelta(minutes=CODE_TTL_MINUTES)
    EMAIL_CODE_STORE[email] = {"code": code, "expire_at": expire_at}
    # 本地“模拟发送”：直接把验证码打印到控制台（答辩演示时可见；正式环境应替换为 SMTP 发送）
    print(f"验证码已发送到邮箱 {email}：{code}（{CODE_TTL_MINUTES} 分钟内有效）")
    return True


# 校验邮箱验证码：
# 作用：核对用户提交的“邮箱 + 验证码”：先比对万能码，再查内存仓库是否存在该邮箱记录、
#       是否过期，最后比对验证码是否一致。
# 参数：email —— 注册填写的邮箱；code —— 用户输入的验证码
# 返回：校验通过返回 True；验证码不存在 / 已过期 / 不匹配返回 False
def verify_email(email, code):
    """验证邮箱验证码。"""

    if code == '123456':
        # 万能验证码：仅供开发/演示阶段绕过邮箱验证（源码已标注“这段要删掉”），
        # 正式上线前必须删除，否则任何人均可用 123456 通过邮箱验证
        return True#这段要删掉


    # 从内存仓库中取出该邮箱的验证码记录
    data = EMAIL_CODE_STORE.get(email)
    if not data:
        print("验证码不存在或已过期")
        return False
    # 超过有效期：删掉过期记录并判定失败（验证码一次性、限时有效）
    if datetime.utcnow() > data["expire_at"]:
        EMAIL_CODE_STORE.pop(email, None)
        print("验证码已过期")
        return False
    # 验证码内容匹配：立即删除(一次性使用)并返回成功
    if data["code"] == code:
        EMAIL_CODE_STORE.pop(email, None)
        print("邮箱验证成功")
        return True
    print("验证码错误")
    return False
#############


# 增强版邮箱格式校验：
# 作用：按常见邮箱规则做格式合法性检查（基本正则、总长度、本地部分、域名部分）。
# 参数：email —— 待校验的邮箱地址
# 返回：格式合法返回 True；不合法打印原因并返回 False
def validate_email_enhanced(email: str) -> bool:
    """
    邮箱格式验证
    Args:
        email: 要验证的邮箱地址

    Returns:
        bool: 邮箱格式是否正确
    """
    if not email or not isinstance(email, str):
        print("邮箱不能为空")
        return False

    email = email.strip()

    # 基本格式检查
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        print("邮箱格式不正确")
        return False

    # 长度检查
    if len(email) > 254:
        print("邮箱地址过长")
        return False

    # 分割本地部分和域名
    parts = email.split('@')
    local_part = parts[0]
    domain = parts[1]

    # 本地部分检查
    if len(local_part) > 64:
        print("邮箱用户名部分过长")
        return False

    if local_part.startswith('.') or local_part.endswith('.'):
        print("邮箱用户名不能以点开头或结尾")
        return False

    if '..' in local_part:
        print("邮箱用户名不能包含连续的点")
        return False

    # 域名检查
    if domain.startswith('-') or domain.endswith('-'):
        print("域名不能以连字符开头或结尾")
        return False

    if '..' in domain:
        print("域名不能包含连续的点")
        return False

    # 如果通过所有检查，返回True
    return True


# 验证码“格式”校验（只查格式、不比内容）：
# 作用：确认用户提交的验证码是“6 位纯数字”，格式通过后再调用 verify_email 比对正确性。
# 参数：code —— 用户输入的验证码
# 返回：格式正确返回 True；否则打印原因并返回 False
def validate_verification_code(code: str) -> bool:
    """
    验证码格式验证
    Args:
        code: 要验证的验证码

    Returns:
        bool: 验证码格式是否正确
    """
    if not code or not isinstance(code, str):
        print("验证码不能为空")
        return False

    code = code.strip()

    # 检查长度
    if len(code) != 6:
        print("验证码必须是6位数字")
        return False

    # 检查是否为纯数字
    if not code.isdigit():
        print("验证码必须是纯数字")
        return False

    # 验证通过
    return True