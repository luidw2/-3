"""
TOTP (RFC 6238) 工具模块
使用标准库实现，不依赖第三方包（二维码生成需前端配合）
"""

import secrets
import base64
import hashlib
import hmac
import struct
import time
from typing import Tuple, List, Optional


# ---------- 密钥生成 ----------
def generate_secret(length: int = 20) -> str:
    """
    生成符合 RFC 6238 的 Base32 编码密钥
    :param length: 随机字节长度，默认 20 (160位)
    :return: Base32 字符串（不包含填充 '='）
    """
    raw = secrets.token_bytes(length)
    # 使用 base64.b32encode，然后去除填充字符 '='
    secret = base64.b32encode(raw).decode('utf-8').rstrip('=')
    return secret


# ---------- OTP 算法 ----------
def _dynamic_truncation(hmac_result: bytes) -> int:
    """动态截断：从 HMAC 结果中提取 31 位整数"""
    offset = hmac_result[-1] & 0xf
    binary = struct.unpack('>I', hmac_result[offset:offset + 4])[0]
    return binary & 0x7fffffff  # 去掉符号位


def totp_code(secret: str, t: Optional[int] = None) -> str:
    """
    计算指定时间步的 TOTP 6 位码
    :param secret: Base32 密钥
    :param t: 时间步（默认当前时间步 floor(now/30)）
    :return: 6 位数字字符串
    """
    if t is None:
        t = int(time.time() // 30)
    # 将密钥解码为字节
    try:
        key = base64.b32decode(secret + '=' * (8 - len(secret) % 8))  # 补齐 '=' 到8的倍数
    except Exception:
        # 若 secret 不含填充且长度不对，手动补齐
        padding = 8 - (len(secret) % 8)
        if padding != 8:
            secret += '=' * padding
        key = base64.b32decode(secret)
    # 时间步转为 8 字节大端整数
    msg = struct.pack('>Q', t)
    # HMAC-SHA1
    h = hmac.new(key, msg, hashlib.sha1).digest()
    # 动态截断取模
    code_int = _dynamic_truncation(h) % 1000000
    return f'{code_int:06d}'


# ---------- 验证（带时间窗口） ----------
def verify_totp(secret: str, code: str, window: int = 1) -> Tuple[bool, int]:
    """
    验证 TOTP 码，允许时间窗口偏移
    :param secret: Base32 密钥
    :param code: 用户输入的 6 位码
    :param window: 允许的步数偏差（通常 1，即 ±30 秒）
    :return: (是否成功, 命中的时间步)
             若失败，返回 (False, -1)
             若成功，返回 (True, 命中时间步)
    """
    current_step = int(time.time() // 30)
    for offset in range(-window, window + 1):
        t = current_step + offset
        if totp_code(secret, t) == code:
            return True, t
    return False, -1


# ---------- 恢复码 ----------
def generate_recovery_codes(n: int = 8, code_length: int = 10) -> List[str]:
    """
    生成 n 个恢复码，每个由字母数字组成
    :param n: 数量
    :param code_length: 每个恢复码的长度
    :return: 明文恢复码列表
    """
    alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # 避免混淆字符
    codes = []
    for _ in range(n):
        code = ''.join(secrets.choice(alphabet) for _ in range(code_length))
        codes.append(code)
    return codes


def hash_recovery_codes(plain_codes: List[str]) -> List[str]:
    """
    对恢复码列表进行 SHA-256 哈希（用于入库）
    :param plain_codes: 明文恢复码列表
    :return: 十六进制哈希字符串列表
    """
    return [hashlib.sha256(code.encode('utf-8')).hexdigest() for code in plain_codes]


def verify_recovery_code(plain_code: str, hashed_list: List[str]) -> bool:
    """
    验证单个恢复码是否匹配哈希列表中的某一项
    （通常匹配后需从数据库中删除该哈希）
    """
    h = hashlib.sha256(plain_code.encode('utf-8')).hexdigest()
    return h in hashed_list


# ---------- 辅助：生成 OTP Auth URI（用于二维码） ----------
def get_otpauth_uri(username: str, secret: str, issuer: str = "DSH") -> str:
    """
    生成标准的 otpauth:// URI，用于生成二维码
    :param username: 用户名
    :param secret: Base32 密钥
    :param issuer: 机构名称（显示在 App 中）
    :return: URI 字符串
    """
    # 对用户名和 issuer 进行 URL 编码（处理特殊字符）
    import urllib.parse
    encoded_user = urllib.parse.quote(username)
    encoded_issuer = urllib.parse.quote(issuer)
    # 格式: otpauth://totp/Issuer:Username?secret=SECRET&issuer=Issuer
    uri = f"otpauth://totp/{encoded_issuer}:{encoded_user}?secret={secret}&issuer={encoded_issuer}"
    return uri

"""
if __name__ == "__main__":
    import time as time_module

    print("=== TOTP 动态码监测（每30秒变化一次）===")

    # 1. 生成一次密钥（固定）
    secret = generate_secret()
    print(f"固定密钥: {secret}")
    print("(可将此密钥或下方URI导入验证器App)")

    # 生成一次URI（仅用于展示）
    uri = get_otpauth_uri("admin1", secret, issuer="MyShop")
    print(f"OTPAuth URI: {uri}\n")

    print("开始监测动态码（每2秒检查一次），变化时打印...")
    last_code = None
    try:
        while True:
            current_code = totp_code(secret)  # 基于当前时间步
            if current_code != last_code:
                current_time = time_module.strftime("%Y-%m-%d %H:%M:%S", time_module.localtime())
                print(f"[{current_time}] 新动态码: {current_code}")
                last_code = current_code
            time_module.sleep(2)  # 避免频繁检查
    except KeyboardInterrupt:
        print("\n监测已停止。")
"""
