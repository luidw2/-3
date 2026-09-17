import subprocess
import tempfile
from dotenv import load_dotenv
import os

# =============================================================================
# 模块说明：SM4 国密对称分组密码算法封装（本项目通过 OpenSSL 命令行实现）
# -----------------------------------------------------------------------------
# 在项目中的用途（依据后端真实调用点，以代码为准）：
#   支付结果“数字信封”的数据体加解密 —— 商户后端在
#   app/api/v1/callback.py、app/api/v1/pay_return.py 中先用 SM2 私钥
#   (调用 SM2.sm2_decrypt)解出 SM4 会话密钥 key 与初始向量 IV，再调用本模块的
#   sm4_decrypt 还原被 SM4 加密的支付结果 JSON 明文；sm4_encrypt 与
#   generate_sm4_key 是与之配对的对称操作(密钥由系统安全随机源生成)，
#   可在模拟银行侧/演示中复用。
# -----------------------------------------------------------------------------
# 实现方式说明：本模块不自行实现 SM4 的 S 盒、密钥扩展、轮函数等底层逻辑，
# 而是通过 subprocess 调用系统 OpenSSL 的 `enc -sm4-cbc` 完成加解密：
#   - sm4-cbc：CBC 分组链接工作模式(分组 16 字节，需要 16 字节初始向量 IV)；
#   - 密钥经 `-pass file:<密钥文件>` 参数提供给 enc 命令，IV 以十六进制经 `-iv`
#     参数传入(见各函数代码中的参数注释)；
#   所有中间文件位于 tempfile 临时目录，函数返回前自动清理。
# 数据约定：key / IV / 明文 / 密文一律为 bytes。
# =============================================================================
# OpenSSL 路径配置
load_dotenv()

OPENSSL_PATH = os.getenv('OPENSSL_PATH')

# —— run_openssl_command：统一执行 OpenSSL 子进程命令的辅助函数。
#    入参 args(list[str])：传给 OpenSSL 的参数列表(不含可执行文件本身)
#    返回 str：命令成功时的 stdout 文本；失败(返回码非 0)时抛出异常
#    内部步骤：subprocess 运行并捕获输出 → 检查返回码 → 非0抛异常 / 0返回stdout
def run_openssl_command(args):
    """
    运行OpenSSL命令并返回结果
    """
    # —— subprocess.run：以独立进程执行 [OpenSSL可执行文件] + args，
    #     capture_output=True 捕获命令的 stdout/stderr，text=True 表示按文本读取
    result = subprocess.run(
        [OPENSSL_PATH] + args,
        capture_output=True,
        text=True
    )
    # OpenSSL 约定：返回码 0 表示命令成功；非 0 时把“完整命令 + stderr 错误信息”
    # 拼装成异常抛出，方便上层调用处定位失败原因
    if result.returncode != 0:
        error_msg = f"OpenSSL命令执行失败: {' '.join(args)}\n错误: {result.stderr.strip()}"
        raise Exception(error_msg)
    # 执行成功：返回 stdout 文本（命令没有文本输出时为空字符串）
    return result.stdout

# —— generate_sm4_key：生成 SM4 会话密钥与初始向量。
#    返回 (key, iv) 二元组，均为 16 字节 bytes —— 注意上方 docstring 只写了 key，
#    实际代码同时返回 IV，调用处按二元组解包使用即可
#    内部步骤：os.urandom(16) 分别从系统安全随机源取 key 与 IV
def generate_sm4_key():
    """
    生成SM4密钥
    
    Returns:
        bytes: 16字节的SM4密钥
    """
    # os.urandom(16)：从操作系统安全随机源取出 16 字节
    # 生成16字节随机密钥
    key = os.urandom(16)
    # SM4-CBC 模式需要 16 字节初始向量 IV，一并随机生成
    # (每次加密都重新生成 IV 可避免相同明文产生相同密文)
    my_iv = os.urandom(16)
    # 实际返回 (key, iv) 二元组，调用处按此解包
    return key, my_iv

# —— sm4_encrypt：SM4-CBC 对称加密。内部大致步骤：临时目录 → 写 key 文件与明文文件
#    → openssl enc -sm4-cbc 加密(密钥经 -pass file 传入、IV 经 -iv 传入)
#    → 读回密文(bytes)
def sm4_encrypt(key,my_iv, plaintext):
    """
    使用SM4加密数据
    
    Args:
        key (bytes): 16字节的SM4密钥
        plaintext (bytes): 要加密的明文数据
        
    Returns:
        bytes: 加密后的数据
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # 写入密钥到临时文件：16 字节密钥以二进制形式写入 sm4.key，
        # 稍后通过 -pass file: 参数交给 OpenSSL enc 命令读取
        key_path = os.path.join(tmpdir, 'sm4.key')
        with open(key_path, 'wb') as f:
            f.write(key)
        
        # 写入明文到临时文件：明文是字节串，按二进制 'wb' 写入
        plaintext_path = os.path.join(tmpdir, 'plaintext.txt')
        with open(plaintext_path, 'wb') as f:
            f.write(plaintext)
        
        # 加密输出路径：规划密文输出文件位置
        ciphertext_path = os.path.join(tmpdir, 'ciphertext.bin')
        
        # 执行加密命令
        # openssl enc -sm4-cbc：调用 OpenSSL 做 SM4 的 CBC 模式加密(对称分组密码)；
        #   -in / -out：输入明文文件、输出密文文件；
        #   -pass file:<key 文件>：以文件方式把密钥内容提供给 enc 命令使用；
        #   -iv <hex>：以十六进制指定 16 字节初始向量(见行尾“16字节IV”注释)
        run_openssl_command([
            'enc', '-sm4-cbc', '-in', plaintext_path, 
            '-out', ciphertext_path, '-pass', f'file:{key_path}', 
            '-iv', my_iv.hex()  # 16字节IV
        ])
        
        # 读取加密结果：CBC 密文为二进制数据，按 'rb' 读出字节串返回
        with open(ciphertext_path, 'rb') as f:
            ciphertext = f.read()
        
    return ciphertext

# —— sm4_decrypt：SM4-CBC 对称解密（与 sm4_encrypt 配对）。内部大致步骤：临时目录
#    → 写 key 文件与密文文件 → openssl enc -d -sm4-cbc 解密(密钥与 IV 的传参与
#      加密时一致) → 读回明文(bytes)
def sm4_decrypt(key, my_iv,ciphertext):
    """
    使用SM4解密数据
    
    Args:
        key (bytes): 16字节的SM4密钥
        ciphertext (bytes): 要解密的数据
        
    Returns:
        bytes: 解密后的明文数据
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # 写入密钥到临时文件：16 字节密钥以二进制形式写入 sm4.key，
        # 稍后通过 -pass file: 参数交给 OpenSSL enc 命令读取
        key_path = os.path.join(tmpdir, 'sm4.key')
        with open(key_path, 'wb') as f:
            f.write(key)
        
        # 写入密文到临时文件：待解密的密文是二进制，按 'wb' 写入
        ciphertext_path = os.path.join(tmpdir, 'ciphertext.bin')
        with open(ciphertext_path, 'wb') as f:
            f.write(ciphertext)
        
        # 解密输出路径：规划解密后的明文输出文件位置
        plaintext_path = os.path.join(tmpdir, 'plaintext.txt')
        
        # 执行解密命令
        # openssl enc -d -sm4-cbc：-d 表示解密方向，其余参数与加密时一一对应
        # (输入密文文件、输出明文文件、密钥经 -pass file 传入、IV 经 -iv 传入)
        run_openssl_command([
            'enc', '-d', '-sm4-cbc', '-in', ciphertext_path, 
            '-out', plaintext_path, '-pass', f'file:{key_path}', 
            '-iv', my_iv.hex()  # 16字节IV
        ])
        
        # 读取解密结果：解密还原出的原始明文(字节串)，按 'rb' 读回返回
        with open(plaintext_path, 'rb') as f:
            plaintext = f.read()
        
    return plaintext

# 测试代码
if __name__ == '__main__':
    try:
        if not os.path.exists(OPENSSL_PATH):
            print(f"错误: OpenSSL路径不存在: {OPENSSL_PATH}")
        else:
            # 生成SM4密钥
            print("生成SM4密钥...")
            key ,my_iv= generate_sm4_key()
            print(f"密钥: {key.hex()}iv:{my_iv.hex()}")
            
            # 测试加解密
            test_data = b"Hello, SM4! This is a test message."
            print(f"\n测试数据: {test_data.decode()}")
            
            # 加密
            encrypted = sm4_encrypt(key, my_iv, test_data)
            print(f"加密结果: {encrypted.hex()}")
            
            # 解密
            decrypted = sm4_decrypt(key,my_iv, encrypted)
            print(f"解密结果: {decrypted.decode()}")
            print(f"加解密验证: {'成功' if decrypted == test_data else '失败'}")
            
    except Exception as e:
        print(f"错误: {e}")
        print(f"请确保OpenSSL路径正确: {OPENSSL_PATH}")
        print("请确保系统已安装支持SM4的OpenSSL版本（1.1.1及以上）")
