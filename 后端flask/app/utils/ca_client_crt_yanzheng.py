"""
ca_client_crt_yanzheng.py —— 客户端数字证书“验证 / 解析”模块

在“数字证书登录”流程中的位置：
    用户使用浏览器导入的 PFX 客户端证书登录时，服务端调用本模块对证书进行“体检”，
    按顺序完成以下几项校验与信息提取：
      1. verify_certificate_format() —— 证书格式校验（必须是合法 X.509 证书，PEM/DER）；
      2. verify_certificate_chain()  —— 信任链认证（用根 CA 证书验证证书链可追溯）；
      3. is_certificate_valid()      —— 有效期认证（当前时间是否落在证书有效期内）；
      4. extract_cn_from_cert()      —— 提取证书 CN 字段，还原出登录用户名；
      5. extract_cert_thumbprint()   —— 提取证书 SHA-256 指纹（用于与 JWT 绑定）。
    辅助函数 extract_cert_from_pfx() 先从 PKCS#12(PFX) 容器中取出“客户端证书本体”(PEM)。
实现说明：python cryptography 库不支持 SM2 算法，
    因此信任链校验改由调用外部命令 openssl verify 完成（见文件内注释）。
"""
from cryptography.exceptions import UnsupportedAlgorithm
import subprocess
import tempfile
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import datetime
from app.utils import db

'''
信任链认证用openssl verify -CAfile rootCA.crt client_zhangsan.crt
因为库函数不支持sm2算法
'''

# 校验① 证书格式验证（X.509）：
# 作用：确认用户提交的 PFX 能解出合法证书，且证书本身可被解析为 X.509 证书。
# 参数：pfx_data —— PFX 文件字节流；password —— PFX 口令
# 返回：格式合法返回 True；格式非法抛出 ValueError（附失败原因）
# 证书格式验证（X.509）
def verify_certificate_format(pfx_data: bytes,password:str) -> bool:
    """
    证书格式验证（X.509）
    Args:
        cert_data: 证书文件内容（PEM 或 DER 编码的字节串）
    Returns:
        成功返回 True，失败抛出 ValueError 并说明原因
    """
    # 尝试按 PEM 加载
    cert_data = extract_cert_from_pfx(pfx_data, password)

    # 先尝试按 PEM 文本格式解析证书；失败再尝试 DER 二进制格式
    try:
        x509.load_pem_x509_certificate(cert_data, default_backend())
        return True
    except UnsupportedAlgorithm:
        # 如果仅因为算法不支持（如 SM2 曲线）而无法深度解析，仍认为格式正确
        return True
    except ValueError:
        # 不是 PEM 格式，尝试按 DER 加载
        try:
            x509.load_der_x509_certificate(cert_data, default_backend())
            return True
        except UnsupportedAlgorithm:
            # DER 格式下若仍仅因算法(SM2)不支持而无法深度解析，也按格式正确处理
            return True
        except Exception as e:
            raise ValueError(f"证书格式无效（DER 解析失败）: {e}")
    except Exception as e:
        raise ValueError(f"证书格式无效（PEM 解析失败）: {e}")

# 校验② 信任链认证（证书链验证）：
# 作用：验证客户端证书确实由“受信任的根 CA”签发，即证书链能追溯到根证书。
# 实现：把“客户端证书”与“根 CA 证书”分别写入临时文件后，调用外部命令
#       openssl verify -CAfile <根CA证书> <客户端证书> 完成验证。
# 参数：pfx_data —— 客户端 PFX 字节流；root_ca_pem —— 根 CA 证书(PEM 字节流)；
#       password —— PFX 口令
# 返回：链验证通过返回 True；失败抛出 ValueError（含 openssl 错误信息，例如
#       “error 2 ... unable to get issuer certificate”表示找不到签发者、链断裂）
#信任链认证
def verify_certificate_chain(pfx_data: bytes, root_ca_pem: bytes,password:str) -> bool:
    """
    信任链认证
    Args:
        cert_pem: 客户端证书内容（PEM 格式字节串）
        root_ca_pem: 根 CA 证书内容（PEM 格式字节串）
    Returns:
        验证通过返回 True，失败抛出 ValueError 并说明原因
    """
    cert_pem = extract_cert_from_pfx(pfx_data, password)

    with tempfile.NamedTemporaryFile(mode='wb', suffix='.crt', delete=False) as cert_file:
        cert_file.write(cert_pem)
        cert_path = cert_file.name

    with tempfile.NamedTemporaryFile(mode='wb', suffix='.crt', delete=False) as ca_file:
        ca_file.write(root_ca_pem)
        ca_path = ca_file.name
    try:
        # 执行 openssl verify 命令
        # 用 openssl 对“客户端证书”做签名与证书链校验（因 cryptography 不支持 SM2）：
        # verify 会用 -CAfile 指定的根 CA 重建证书链并校验各级签名
        # -CAfile 指定根 CA 证书，验证证书链
        cmd = ['openssl', 'verify', '-CAfile', ca_path, cert_path]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            # 校验失败：openssl 返回码非 0，从 stderr/stdout 提取具体错误原因
            # 提取错误信息（例如 "error 2 at 1 depth lookup:unable to get issuer certificate"）
            error_msg = result.stderr.strip() or result.stdout.strip()
            raise ValueError(f"信任链验证失败: {error_msg}")

        return True
    finally:
        # 清理临时文件（无论成败都删除，不留敏感证书残留在磁盘）
        # 清理临时文件
        Path(cert_path).unlink(missing_ok=True)
        Path(ca_path).unlink(missing_ok=True)

# 校验③ 有效日期认证（有效期校验）：
# 作用：判断客户端证书当前是否处于有效期内（notBefore <= now <= notAfter），
#       已过期或尚未生效的证书不允许用来登录。
# 参数：pfx_data —— 客户端 PFX 字节流；password —— PFX 口令
# 返回：当前时间在证书有效期内返回 True，否则 False；证书无法解析时抛出 ValueError
#有效日期认证
def is_certificate_valid(
        pfx_data: bytes,
        password:str
) -> bool:
    """
    有效日期认证
    :param cert_data: PEM 格式的证书内容，可以是 bytes 或 str
    :param cert_path: 证书文件路径（如果提供 cert_data，则忽略此参数）
    :return: True 如果在有效期内，否则 False
    :raises: ValueError 当无法解析证书时
    """
    # 获取证书内容
    cert_data = extract_cert_from_pfx(pfx_data, password)

    if cert_data is not None:
        if isinstance(cert_data, str):
            cert_data = cert_data.encode('utf-8')
    else:
        raise ValueError("必须提供 cert_data 或 cert_path")

    # 加载 PEM 证书
    cert = x509.load_pem_x509_certificate(cert_data, default_backend())

    # 解析扩展字段 notBefore / notAfter（证书有效期起点与终点）
    # 获取有效期起止时间（均为 UTC，无时区信息）
    not_before = cert.not_valid_before_utc  # cryptography >= 42.0.0
    not_after = cert.not_valid_after_utc
    # 旧版 cryptography 可使用 not_valid_before / not_valid_after（需自行处理时区）
    # 兼容写法：
    # if hasattr(cert, 'not_valid_before_utc'):
    #     not_before = cert.not_valid_before_utc
    # else:
    #     not_before = cert.not_valid_before.replace(tzinfo=datetime.timezone.utc)

    # 当前 UTC 时间与有效期比较（证书时间统一按 UTC 处理，避免时区不一致误判）
    now = datetime.datetime.now(datetime.timezone.utc)

    return not_before <= now <= not_after

# 信息提取① 从证书中提取 CN（Common Name）并还原出“纯用户名”：
# 作用：签发客户端证书时 CN 形如 “user_zhangsan”（前缀见 ca_client.py），
#       登录时据角色去掉 “user_/seller_” 前缀得到数据库中的用户名，
#       从而把“证书身份 <-> 系统账号”对应起来，完成证书登录的身份映射。
# 参数：pfx_data —— 客户端 PFX 字节流；password —— PFX 口令；
#       role —— 证书归属角色(user/seller)，用于剥掉 CN 上的对应前缀
# 返回：成功返回去掉前缀后的用户名；解析失败 / 无 CN 字段返回 None
#提取证书中的信息
def extract_cn_from_cert(pfx_data: bytes, password:str,role : str) -> str | None:
    """
    提取证书中的信息
    从PEM格式的证书字节流中提取CN（Common Name）。
    Args:
        pfx_data: PEM格式的pfx字节流，例如 b'-----BEGIN CERTIFICATE-----...'
    Returns:
        如果找到CN字段，返回其字符串值；否则返回None。
    """
    cert_pem = extract_cert_from_pfx(pfx_data, password)
    try:
        # 加载证书
        # （把 PEM 文本解析为 X.509 证书对象，之后可访问其 subject / 有效期 / 扩展等结构）
        cert = x509.load_pem_x509_certificate(cert_pem, default_backend())
        # 获取subject中所有CN属性
        # 按 OID(COMMON_NAME) 读取证书主体(subject)里的 CN 字段值
        cn_attributes = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)

        # 去掉 CN 上由签发流程加上的 “role_” 前缀，还原出原始用户名
        remove  = role + "_"
        result = cn_attributes[0].value.removeprefix(remove)

        if cn_attributes:
            return result
            #return cn_attributes[0].value
        else:
            return None
    except Exception as e:
        print(f"解析证书时出错: {e}")
        return None

'''
#
def if_cert_user_in_db(pfx_data: bytes, password:str) -> str | None:

    username = extract_cn_from_cert(pfx_data, password)
    user_ = db.get_user_by_username(username)
    if not user_:
        raise ValueError(f"不存在用户: {username}")
'''



# 辅助函数：从 PKCS#12(PFX) 中提取“客户端证书本体”（PEM 格式）：
# 作用：浏览器导入的是 PFX（私钥 + 证书的打包容器），后续各项校验只针对“证书”部分，
#       故先用 openssl pkcs12 抽出证书（本函数只导证书、不导出私钥）。
# 参数：pfx_data —— PFX 字节流；password —— PFX 口令（默认 '123456'）
# 返回：客户端证书的 PEM 字节流；PFX 口令错误或格式损坏时抛出 ValueError
# 提取出pfx格式中的证书
def extract_cert_from_pfx(pfx_data: bytes, password: str = "123456") -> bytes:
    """从 PKCS#12 (PFX) 数据中提取第一个证书（PEM 格式）"""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pfx', delete=False) as pfx_file:
        pfx_file.write(pfx_data)
        pfx_path = pfx_file.name

    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pem', delete=False) as cert_file:
        cert_path = cert_file.name

    try:
        # openssl pkcs12 命令参数说明：
        #   -in pfx_path   ：读入 PFX 容器文件；
        #   -nokeys        ：只导出证书、不导出私钥（验证环节不需要私钥）；
        #   -clcerts       ：只提取客户端(叶子)证书，排除容器内附带的其他 CA 证书；
        #   -passin pass:口令：PFX 的读取口令；
        #   -out cert_path ：把提取出的证书以 PEM 文本格式写入临时文件
        cmd = [
            'openssl', 'pkcs12',
            '-in', pfx_path,
            '-nokeys', '-clcerts',
            '-passin', f'pass:{password}',
            '-out', cert_path
        ]
        subprocess.run(cmd, capture_output=True, check=True, text=True)
        # 读取并返回 PEM 证书字节流
        with open(cert_path, 'rb') as f:
            return f.read()
    except subprocess.CalledProcessError as e:
        raise ValueError(f"从 PFX 提取证书失败: {e.stderr}")
    finally:
        Path(pfx_path).unlink(missing_ok=True)
        Path(cert_path).unlink(missing_ok=True)

# 信息提取② 提取证书的 SHA-256 指纹：
# 作用：指纹 = 对证书内容做 SHA-256 摘要得到的定长标识（类似证书的“身份证号”）。
#       登录时把指纹写入 JWT 的 cert_thumbprint 字段，实现“令牌与证书绑定”，
#       也便于服务端追溯/比对用户使用的是哪张证书。
# 参数：pfx_data —— 客户端 PFX 字节流；password —— PFX 口令
# 返回：去掉冒号分隔符的大写十六进制指纹串（形如 A1B2C3…）；失败返回 None
#提取证书的 SHA-256 指纹
def extract_cert_thumbprint(pfx_data: bytes, password: str) -> str | None:
    """
    提取证书的 SHA-256 指纹
    :param pfx_data: PFX 格式的证书数据
    :param password: 证书密码
    :return: 证书指纹字符串，失败返回 None
    """
    try:
        # 使用现有的函数提取证书
        cert_pem = extract_cert_from_pfx(pfx_data, password)

        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pem', delete=False) as cert_file:
            cert_file.write(cert_pem)
            cert_path = cert_file.name

        # 计算证书指纹：openssl x509 -fingerprint -sha256 -noout
        # —— 只输出证书指纹(不输出证书全文)，-sha256 指定指纹摘要算法为 SHA-256
        result = subprocess.run([
            'openssl', 'x509', '-in', cert_path,
            '-fingerprint', '-sha256', '-noout'
        ], capture_output=True, text=True)

        if result.returncode != 0:
            return None

        # 解析指纹输出：openssl 输出形如 “sha256 Fingerprint=AA:BB:CC:...”，
        # 取 “=” 右侧部分并去掉 “:”，得到连续的大写十六进制指纹串
        # 解析指纹输出
        fingerprint = result.stdout.strip().split('=')[1].replace(':', '')
        return fingerprint

    except Exception:
        return None
    finally:
        if 'cert_path' in locals():
            Path(cert_path).unlink(missing_ok=True)


'''
使用示例
if __name__ == "__main__":
    with open(r"E:/Python/test_ca/certs/client/client_zhangsan.pfx", "rb") as f:
        cert_bytes = f.read()
    with open(r"E:/Python/test_ca/certs/rootCA/ca_sm2.crt", "rb") as f:
        root_ca = f.read()
    try:
        verify_certificate_format(cert_bytes,'123456')
        print("证书格式验证通过")
    except ValueError as e:
        print(f"验证失败: {e}")

    try:
        verify_certificate_chain(cert_bytes, root_ca,'123456')
        print("信任链验证通过")
    except ValueError as e:
        print(f"验证失败: {e}")
    try:
        valid = is_certificate_valid(pfx_data=cert_bytes,password="123456")
        print(f"证书时间: {valid}")
        # valid = is_certificate_valid(cert_path="E:\Python\\test_ca\certs\client\client_zhangsan.crt")
        # print(f"证书有效: {valid}")
        pass
    except ValueError as e:
        print(f"验证失败: {e}")

    try:
        print(f"证书CN字段信息：{extract_cn_from_cert(cert_bytes,'123456')}")
    except ValueError as e:
        print(f"验证失败: {e}")
'''