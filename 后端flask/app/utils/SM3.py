import os
from gmssl import sm3,func
'''
这里的明文是字符串形式
'''

# =============================================================================
# 模块说明：SM3 国密杂凑(哈希)算法工具封装（基于 gmssl 库）
# -----------------------------------------------------------------------------
# 在项目中的用途（依据后端代码）：
#   - app/api/v1/pay.py 通过 `from app.utils import ..., SM3` 导入了本模块；
#   - 与 SM2 的配套关系：SM2.py 调用 OpenSSL `dgst -sign -sm3` 做 SM2 签名时，
#     消息摘要一步使用的正是 SM3（代码中可见 -sm3 参数）；
#   - 本文件提供两类可直接复用的 SM3 摘要工具：
#       ① 带随机盐的“哈希 + 校验”（sm3_encrypt_with_salt / sm3_verify_with_salt），
#          适合口令等敏感数据的不可逆存储与比对：相同明文每次哈希结果不同，
#          加盐可避免“同口令同哈希”，并增大彩虹表攻击的成本；
#       ② 不带盐的普通摘要（sm3_encrypt），同一明文结果固定，属确定性哈希。
# -----------------------------------------------------------------------------
# 实现方式说明：本文件不自行实现 SM3 的消息填充、消息扩展与迭代压缩等底层逻辑，
# 而是调用 gmssl 库提供的 sm3.sm3_hash()；gmssl 的接口约定接收“字节值(0~255)列表”，
# 因此传入前须先用 func.bytes_to_list() 把字节串转换成整数列表。
# 数据约定：本模块明文参数一律为字符串(str)，与 SM2/SM4 模块的 bytes 约定不同。
# =============================================================================
# —— sm3_encrypt_with_salt：带随机盐的 SM3 哈希(同一明文每次结果都不同)。
#    入参 plaintext(str)：待哈希明文；返回 str：盐hex(32字符)+摘要hex(64字符) 拼串
#    内部大致步骤：生成 16 字节随机盐 → 盐 + 明文 utf-8 字节拼接待哈希数据 →
#                  sm3_hash 求摘要 → 把盐的 hex 拼在摘要前返回(自包含，可直接整体入库)
def sm3_encrypt_with_salt(plaintext):
    """
    使用SM3算法计算带盐值的哈希值
    
    Args:
        plaintext (str): 要计算哈希的明文
        
    Returns:
        str: 盐值（前32个字符）和哈希值（后64个字符）的组合
    """
    # 生成16字节随机盐值
    salt = os.urandom(16)
    # 将盐值转换为十六进制字符串
    salt_hex = salt.hex()
    # 组合盐值和明文：盐固定放在最前面(前 16 字节)，便于验证时按位置切回盐值
    salted_data = salt + plaintext.encode('utf-8')
    # 计算SM3哈希值：先经 func.bytes_to_list 把字节串转成 gmssl 需要的整数列表再求摘要；
    # 返回的 hash_value 是 64 个十六进制字符(32 字节摘要的 hex 表示)
    hash_value = sm3.sm3_hash(func.bytes_to_list(salted_data))
    # 返回盐值和哈希值的组合：整体 = 盐的 hex(固定 32 字符) + 摘要 hex(64 字符)，
    # 两者拼成一条自包含字符串，可直接整体存入数据库，无需为盐单独开字段
    return salt_hex + hash_value

# —— sm3_verify_with_salt：校验“明文”是否与“存储的带盐 SM3 哈希串”匹配。
#    入参 stored_hash(str)：sm3_encrypt_with_salt 生成的整串(前32字符盐hex + 后64字符摘要hex)
#         plaintext(str)：待校验的明文
#    返回 bool：True=匹配 / False=不匹配
#    内部大致步骤：从整串前 32 字符切回盐值 → 盐+明文重新拼装并求 SM3 摘要 →
#                  与整串后 64 字符比对是否一致
def sm3_verify_with_salt(stored_hash, plaintext):
    """
    验证带盐值的SM3哈希值
    Args:
        stored_hash (str): 存储的盐值和哈希值组合
        plaintext (str): 要验证的明文
    Returns:
        bool: 验证是否通过
    """
    # 提取盐值（前32个字符）：与 sm3_encrypt_with_salt 的拼接格式一一对应——
    # 前 32 个十六进制字符即当初随机盐(16 字节)的 hex 表示
    salt_hex = stored_hash[:32]
    # 把盐的 hex 文本还原成原始字节，以便按相同方式重新组合待哈希数据
    salt = bytes.fromhex(salt_hex)
    # 组合盐值和明文：盐在前 + 明文 utf-8 字节，与加密时的输入保持一致
    salted_data = salt + plaintext.encode('utf-8')
    # 计算SM3哈希值：对同一份输入重新求一次摘要
    hash_value = sm3.sm3_hash(func.bytes_to_list(salted_data))
    # 对比哈希值：用“重新计算的摘要”比对“存储串的后 64 字符”，一致则验证通过
    return stored_hash[32:] == hash_value


# 测试基本SM3哈希（无盐）
# —— sm3_encrypt：普通(无盐)SM3 摘要，同一明文每次结果都相同(确定性哈希)，
#    可用作课程设计演示，或对无需防猜解的敏感数据做完整性摘要。
#    入参 plaintext(str)：待哈希的明文字符串
#    返回 str：64 个十六进制字符的 SM3 摘要
#    内部步骤：utf-8 编码成字节串 → bytes_to_list 转整数列表 → sm3_hash 计算摘要
def sm3_encrypt(plaintext):
    # 字符串明文先按 UTF-8 编码为字节串
    b_plaintext = bytes(plaintext, 'utf-8')
    # bytes_to_list 把字节串逐字节拆成 0~255 的整数列表(gmssl 接口约定)，
    # sm3_hash 完成 SM3 摘要计算，返回 64 位十六进制摘要字符串
    hash_value = sm3.sm3_hash(func.bytes_to_list(b_plaintext))
    return hash_value

# 测试代码
if __name__ == '__main__':
    # 测试基本SM3哈希（无盐）
    print("基本SM3哈希测试：")
    hash1 = sm3_encrypt('hello world')
    hash2 = sm3_encrypt('hello world')
    print(f"第一次哈希: {hash1}")
    print(f"第二次哈希: {hash2}")
    print(f"两次哈希是否相同: {hash1 == hash2}")
    
    # 测试加盐SM3哈希
    print("\n加盐SM3哈希测试：")
    stored_hash1 = sm3_encrypt_with_salt('hello world')
    stored_hash2 = sm3_encrypt_with_salt('hello world')
    print(f"第一次加盐哈希: {stored_hash1}")
    print(f"第二次加盐哈希: {stored_hash2}")
    print(f"两次加盐哈希是否相同: {stored_hash1 == stored_hash2}")
    
    # 测试验证功能
    print("\n验证测试：")
    # 正确密码验证
    verify_result1 = sm3_verify_with_salt(stored_hash1, 'hello world')
    print(f"正确密码验证结果: {'成功' if verify_result1 else '失败'}")
    # 错误密码验证
    verify_result2 = sm3_verify_with_salt(stored_hash1, 'wrong password')
    print(f"错误密码验证结果: {'成功' if verify_result2 else '失败'}")
    