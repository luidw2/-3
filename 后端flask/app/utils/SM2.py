import subprocess
import tempfile
from dotenv import load_dotenv
import os
from gmssl import sm2 as gmssl_sm2, func
import re
import base64
'''
注意
sm2使用byte的格式
这里输入的所有的明文都要是byte格式
使用函数时注意转换格式

'''

# =============================================================================
# 模块说明：SM2 国密非对称密码算法封装（本项目通过 OpenSSL 命令行实现）
# -----------------------------------------------------------------------------
# 在项目中的用途（依据后端真实调用点，以代码为准）：
#   1) 密钥生成：app/utils/generate_sm2_key.py 首次运行时调用 generate_sm2_keypair()
#      生成商户 SM2 公私钥对并落盘到 certs/sm2_key/ 目录；
#   2) 签名：app/api/v1/pay.py 读取商户 SM2 私钥，调用 sm2_sign 对
#      “订单号|金额|商户号|时间戳”原文签名，生成带签名的支付链接供(模拟)银行验签；
#   3) 数字信封解密：app/api/v1/callback.py 与 app/api/v1/pay_return.py 读取商户
#      SM2 私钥，调用 sm2_decrypt 解开银行用 SM2 公钥加密的 SM4 会话密钥与 IV，
#      再配合 SM4 解密支付结果数据体（sm2_encrypt 为配对的反向操作）。
# -----------------------------------------------------------------------------
# 实现方式说明：本模块并未自行实现椭圆曲线点运算等 SM2 底层数学逻辑，而是通过
# subprocess 调用系统 OpenSSL（版本需支持 SM2，路径由环境变量 OPENSSL_PATH 提供）
# 完成密钥生成 / 公钥加密 / 私钥解密 / SM3-SM2 签名与验签；所有中间文件都放在
# tempfile 临时目录中，函数返回前自动清理，不向项目目录落盘任何文件。
# 数据约定：明文/密文/签名一律使用 bytes；密钥为 PEM 格式文本字符串。
# =============================================================================
# OpenSSL 路径配置
load_dotenv()

OPENSSL_PATH = os.getenv('OPENSSL_PATH')


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
    # 拼装成异常抛出，方便上层调用处定位是哪一步、因什么原因失败
    if result.returncode != 0:
        error_msg = f"OpenSSL命令执行失败: {' '.join(args)}\n错误: {result.stderr.strip()}"
        raise Exception(error_msg)
    # 执行成功：返回 stdout 文本（命令没有文本输出时为空字符串）
    return result.stdout

# 内部大致步骤：临时目录 → 依次尝试 3 种命令写法生成私钥 → 由私钥导出公钥 PEM
#               → 读回两段 PEM 文本并返回 (私钥, 公钥)
def generate_sm2_keypair():
    """
    使用 OpenSSL 生成 SM2 公私钥对

    Returns:
        tuple: (私钥, 公钥) - 均为PEM格式字符串
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        private_key_path = os.path.join(tmpdir, 'sm2_private.pem')
        public_key_path = os.path.join(tmpdir, 'sm2_public.pem')
        
        # 尝试使用不同命令格式生成密钥，为了兼容性
        # 不同 OpenSSL 版本对 SM2 密钥生成的语法支持不完全一致，故按序尝试三种写法：
        #   1) genpkey -algorithm SM2 —— 新版 OpenSSL(3.x) 的通用生成方式；
        #   2) ecparam -name sm2p256v1 -genkey —— 老版本按命名曲线 sm2p256v1 生成私钥；
        #   3) ec -genkey -name sm2p256v1 —— 兼容性兜底写法
        for cmd_args in [
            ['genpkey', '-algorithm', 'SM2', '-out', private_key_path],
            ['ecparam', '-name', 'sm2p256v1', '-genkey', '-out', private_key_path],
            ['ec', '-genkey', '-name', 'sm2p256v1', '-out', private_key_path]
        ]:
            try:
                run_openssl_command(cmd_args)
                break                 # 某一种写法成功生成后立即跳出循环
            except:
                continue              # 当前写法失败(不支持/报错)则换下一种再试
        else:
            # for 循环“没有被 break 中断”才会走到 else：说明三种写法全部失败
            raise Exception("无法生成SM2密钥对，请确保OpenSSL支持SM2")
        
        #通过命令和私钥 导出公钥
        # pkey -pubout：读取私钥文件，从其中解析出密钥对后以 PEM 格式导出公钥文件
        run_openssl_command([
            'pkey', '-in', private_key_path, '-pubout', '-out', public_key_path
        ])
        
        # 读取密钥：PEM 是带 BEGIN/END 标记的 Base64 文本外壳，故用文本模式 'r' 读回；
        # 临时目录在函数返回时会被自动清理，真正返回给调用方的只是内存中的 PEM 字符串
        with open(private_key_path, 'r') as f:
            private_key = f.read()
        with open(public_key_path, 'r') as f:
            public_key = f.read()
        
    return private_key, public_key

# —— sm2_encrypt：SM2 公钥加密（加密方使用对方公钥）。内部大致步骤：
#    临时目录 → 写入公钥 PEM 与明文文件 → pkeyutl -encrypt 公钥加密
#    （依次尝试带/不带 -id 两种参数写法）→ 读回密文(bytes)
def sm2_encrypt(public_key, plaintext):
    """
    使用SM2公钥加密数据

    Args:
        public_key (str): PEM格式的SM2公钥
        plaintext (bytes): 要加密的明文数据

    Returns:
        bytes: 加密后的数据
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        public_key_path = os.path.join(tmpdir, 'sm2_public.pem')
        plaintext_path = os.path.join(tmpdir, 'plaintext.txt')
        ciphertext_path = os.path.join(tmpdir, 'ciphertext.bin')
        
        # 写入文件：公钥为 PEM 文本按 'w' 写；明文是字节串按 'wb' 二进制写
        with open(public_key_path, 'w') as f:
            f.write(public_key)
        with open(plaintext_path, 'wb') as f:
            f.write(plaintext)
        
        # 尝试不同加密参数
        # pkeyutl -encrypt：OpenSSL 的通用非对称加密子命令；-pubin 表示提供的是公钥文件；
        #   带 -sm2 模式时 OpenSSL 需要用户标识 -id（此处用的是 SM2 流程约定默认标识
        #   1234567812345678）。部分 OpenSSL 版本行为略有差异，故依次尝试
        #   “带 -id”与“不带 -id”两种写法，任一成功即停止。
        for cmd_args in [
            ['pkeyutl', '-encrypt', '-in', plaintext_path, 
             '-out', ciphertext_path, '-inkey', public_key_path, '-pubin', 
             '-sm2', '-id', '1234567812345678'],
            ['pkeyutl', '-encrypt', '-in', plaintext_path, 
             '-out', ciphertext_path, '-inkey', public_key_path, '-pubin']
        ]:
            try:
                run_openssl_command(cmd_args)
                break                # 加密成功则跳出
            except:
                continue             # 失败则换第二种写法
        else:
            # 两种写法都失败时抛出异常（for-else：循环未被 break 中断才会走到 else）
            raise Exception("无法执行SM2加密")
        
        # 读取加密结果：SM2 密文是二进制数据，按 'rb' 读出字节串返回
        with open(ciphertext_path, 'rb') as f:
            ciphertext = f.read()
        
    return ciphertext

# —— sm2_decrypt：SM2 私钥解密（与 sm2_encrypt 配对，持私钥一方解密）。内部大致步骤：
#    临时目录 → 写入私钥 PEM 与密文文件 → pkeyutl -decrypt 私钥解密
#    （依次尝试带/不带 -id 两种参数写法）→ 读回明文(bytes)
def sm2_decrypt(private_key, ciphertext):
    """
    使用SM2私钥解密数据

    Args:
        private_key (str): PEM格式的SM2私钥
        ciphertext (bytes): 要解密的数据

    Returns:
        bytes: 解密后的明文数据
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        private_key_path = os.path.join(tmpdir, 'sm2_private.pem')
        ciphertext_path = os.path.join(tmpdir, 'ciphertext.bin')
        plaintext_path = os.path.join(tmpdir, 'plaintext.txt')
        
        # 写入文件：私钥为 PEM 文本按 'w' 写；待解密密文是字节串按 'wb' 二进制写
        with open(private_key_path, 'w') as f:
            f.write(private_key)
        with open(ciphertext_path, 'wb') as f:
            f.write(ciphertext)
        
        # 尝试不同解密参数
        # pkeyutl -decrypt：用私钥解密；与加密侧一样先试“带 -id”写法，
        # 失败再试“不带 -id”的简化写法（解密的写法须与加密时保持一致才能解出）
        for cmd_args in [
            ['pkeyutl', '-decrypt', '-in', ciphertext_path, 
             '-out', plaintext_path, '-inkey', private_key_path, 
             '-sm2', '-id', '1234567812345678'],
            ['pkeyutl', '-decrypt', '-in', ciphertext_path, 
             '-out', plaintext_path, '-inkey', private_key_path]
        ]:
            try:
                run_openssl_command(cmd_args)
                break                # 解密成功则跳出
            except:
                continue             # 失败则换第二种写法
        else:
            # 两种写法均失败：抛出异常（for-else：循环未被 break 中断）
            raise Exception("无法执行SM2解密")
        
        # 读取解密结果：解密还原出的原始明文(字节串)，按 'rb' 读回返回
        with open(plaintext_path, 'rb') as f:
            plaintext = f.read()
        
    return plaintext

# —— sm2_sign：SM2 私钥签名（内部以 SM3 作为消息摘要，即 SM3-with-SM2 签名）。
#    内部大致步骤：临时目录 → 写入私钥 PEM 与待签数据文件 → dgst -sign -sm3 完成签名
#    → 读回签名(bytes)
def sm2_sign(private_key, data):
    """
    使用SM2私钥对数据进行签名

    Args:
        private_key (str): PEM格式的SM2私钥
        data (bytes): 要签名的数据

    Returns:
        bytes: 签名结果
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        private_key_path = os.path.join(tmpdir, 'sm2_private.pem')
        data_path = os.path.join(tmpdir, 'data.txt')
        signature_path = os.path.join(tmpdir, 'signature.bin')
        
        # 写入文件：私钥为 PEM 文本按 'w' 写；待签名数据是字节串按 'wb' 写
        with open(private_key_path, 'w') as f:
            f.write(private_key)
        with open(data_path, 'wb') as f:
            f.write(data)
        
        # 执行签名
        # dgst -sign + -sm3：OpenSSL 先用 SM3 对 data 文件取消息摘要，
        # 再用 SM2 私钥完成签名，签名结果(二进制)写入 signature 文件
        run_openssl_command([
            'dgst', '-sign', private_key_path, 
            '-out', signature_path, '-sm3', data_path
        ])
        
        # 读取签名：签名结果是二进制，按 'rb' 读出字节串返回
        with open(signature_path, 'rb') as f:
            signature = f.read()
        
    return signature

# —— sm2_verify：SM2 公钥验签（与 sm2_sign 配对，验签方持有签名者公钥）。
#    内部大致步骤：临时目录 → 写入公钥 PEM / 原始数据 / 待验签名三个文件 →
#    dgst -verify 校验 → 以命令退出码是否为 0 判断验证结果
def sm2_verify(public_key, data, signature):
    """
    使用SM2公钥验证签名

    Args:
        public_key (str): PEM格式的SM2公钥
        data (bytes): 原始数据
        signature (bytes): 签名数据

    Returns:
        bool: 验证是否通过
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        public_key_path = os.path.join(tmpdir, 'sm2_public.pem')
        data_path = os.path.join(tmpdir, 'data.txt')
        signature_path = os.path.join(tmpdir, 'signature.bin')
        
        # 写入文件：公钥(PEM 文本)、原始数据(二进制)、待验证的签名(二进制) 依次落盘
        with open(public_key_path, 'w') as f:
            f.write(public_key)
        with open(data_path, 'wb') as f:
            f.write(data)
        with open(signature_path, 'wb') as f:
            f.write(signature)
        
        # 执行验证
        # dgst -verify：用公钥验证 SM2 签名；-sm3 指明签名时所用的摘要是 SM3；
        # -out os.devnull：验证过程不需要查看 OpenSSL 的文本输出，直接丢弃，
        # 只需根据命令的退出码(returncode)判断验证结果
        result = subprocess.run([
            OPENSSL_PATH, 'dgst', '-verify', public_key_path, 
            '-out', os.devnull, '-sm3', '-signature', signature_path, data_path
        ], capture_output=True)
        
    # OpenSSL 约定：验签通过时退出码为 0、失败时非 0，这里直接映射成布尔值返回
    return result.returncode == 0




# =============================================================================
# 基于 gmssl 库的 SM2 接口（安全隧道专用，hex 密钥，裸格式）
# -----------------------------------------------------------------------------
# 与旧接口的分工：
#   旧接口（sm2_encrypt/sm2_decrypt）：PEM 密钥 + OpenSSL 命令行 + DER 格式
#                                       —— 银行联调继续用，一行都不动
#   新接口（本段）：hex 密钥 + gmssl 库 + 裸格式 04||x||y||C3||C2
#                                       —— 与前端 sm-crypto 完全兼容
# =============================================================================

from gmssl import sm2 as gmssl_sm2


def gmssl_sm2_generate_keypair():
    """
    使用 gmssl 库生成 SM2 十六进制密钥对（安全隧道专用）。

    Returns:
        tuple: (private_key_hex, public_key_hex)
               private_key_hex: 64 字符（32 字节）
               public_key_hex:  128 字符（x||y，无 04 前缀）
    """
    # 私钥：32 字节随机
    private_key_hex = os.urandom(32).hex()

    # 公钥：P = d * G，用 gmssl 内部的点乘
    sm2_crypt = gmssl_sm2.CryptSM2(public_key='', private_key=private_key_hex)
    public_key_hex = sm2_crypt._kg(
        int(private_key_hex, 16),
        gmssl_sm2.default_ecc_table['g']
    )
    return private_key_hex, public_key_hex


def gmssl_sm2_encrypt_raw(public_key_hex: str, plaintext: bytes) -> bytes:
    """
    SM2 加密，输出裸格式 04||x||y||C3||C2，与前端 sm-crypto 兼容。

    注：不同 gmssl 版本在 asn1=False 时的输出不一致：
        - 有的版本输出 04||x||y||C3||C2（97 + len(pt)）
        - 有的版本输出    x||y||C3||C2（96 + len(pt)）
        本函数统一为带 04 前缀的形式。
    """
    if public_key_hex.startswith('04'):
        public_key_hex = public_key_hex[2:]
    if len(public_key_hex) != 128:
        raise ValueError(f"公钥长度异常：{len(public_key_hex)}（应为 128）")

    sm2_crypt = gmssl_sm2.CryptSM2(
        public_key=public_key_hex,
        private_key='',
        asn1=False
    )
    raw = sm2_crypt.encrypt(plaintext)

    # —— 规范化：按长度判断是否缺 04 ——
    expected_with_prefix    = 97 + len(plaintext)
    expected_without_prefix = 96 + len(plaintext)

    if len(raw) == expected_without_prefix:
        raw = b'\x04' + raw
    elif len(raw) != expected_with_prefix:
        raise ValueError(
            f"密文长度异常：{len(raw)}，"
            f"期望 {expected_with_prefix} 或 {expected_without_prefix}"
        )
    return raw


def gmssl_sm2_decrypt_raw(private_key_hex: str, ciphertext: bytes) -> bytes:
    """
    SM2 解密，输入裸格式（可带或不带 04 前缀）。

    gmssl 在 asn1=False 时的 decrypt 期望输入不带 04，因此这里统一去掉。
    """
    if len(private_key_hex) != 64:
        raise ValueError(f"私钥长度异常：{len(private_key_hex)}（应为 64）")

    # —— 去掉 04 前缀（如果存在）——
    # 注意：如果密文恰好不带 04 而 x[0] 又是 0x04，会有 1/256 的误判概率。
    # 但因为我们的 encrypt_raw 总是输出带 04 的格式，前端 sm-crypto 也是，
    # 所以实际不会遇到裸 x[0]=0x04 的输入。
    if ciphertext.startswith(b'\x04') and len(ciphertext) >= 97:
        ciphertext = ciphertext[1:]

    sm2_crypt = gmssl_sm2.CryptSM2(
        public_key='',
        private_key=private_key_hex,
        asn1=False
    )
    return sm2_crypt.decrypt(ciphertext)


if __name__ == '__main__':
    try:
        # ============ 旧接口（OpenSSL + PEM + DER）============
        if not os.path.exists(OPENSSL_PATH or ""):
            print(f"错误: OpenSSL路径不存在: {OPENSSL_PATH}")
        else:
            print("=" * 60)
            print("【A】旧接口：OpenSSL + PEM + DER（银行联调用，未改）")
            print("=" * 60)

            sk_pem, pk_pem = generate_sm2_keypair()
            test_data = b"Hello, SM2!"

            der_ct = sm2_encrypt(pk_pem, test_data)
            print(f"DER 密文长度: {len(der_ct)}，首字节: 0x{der_ct[0]:02x}")
            der_pt = sm2_decrypt(sk_pem, der_ct)
            print(f"解密结果: {der_pt.decode()}")
            print(f"往返验证: {'✅' if der_pt == test_data else '❌'}")

        # ============ 新接口（gmssl 库 + hex + 裸格式）============
        print()
        print("=" * 60)
        print("【B】新接口：gmssl + hex + 裸格式（安全隧道）")
        print("=" * 60)

        priv_hex, pub_hex = gmssl_sm2_generate_keypair()
        print(f"私钥 hex（{len(priv_hex)} 字符）: {priv_hex}")
        print(f"公钥 hex（{len(pub_hex)} 字符）: {pub_hex}")

        test_data = b"Hello, SM2!"
        raw_ct = gmssl_sm2_encrypt_raw(pub_hex, test_data)
        print(f"\n裸密文长度: {len(raw_ct)}（应 = 97 + {len(test_data)} = {97 + len(test_data)}）")
        print(f"裸密文首字节: 0x{raw_ct[0]:02x}（应为 0x04）")
        print(f"裸密文前 20 字节: {raw_ct[:20].hex()}")

        raw_pt = gmssl_sm2_decrypt_raw(priv_hex, raw_ct)
        print(f"\n解密结果: {raw_pt.decode()}")
        print(f"往返验证: {'✅ 成功' if raw_pt == test_data else '❌ 失败'}")

        # 边界：多长度明文
        print("\n不同长度明文往返：")
        ok = 0
        for n in [1, 15, 16, 17, 32, 100, 1024]:
            msg = os.urandom(n)
            ct = gmssl_sm2_encrypt_raw(pub_hex, msg)
            pt = gmssl_sm2_decrypt_raw(priv_hex, ct)
            if pt == msg and len(ct) == 97 + n and ct[0] == 0x04:
                ok += 1
                print(f"  明文 {n:>5} 字节 → 密文 {len(ct):>5} 字节  ✅")
            else:
                print(f"  明文 {n:>5} 字节 → 密文 {len(ct):>5} 字节  ❌")
        print(f"通过: {ok}/7")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"错误: {e}")