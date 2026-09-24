"""
这是模拟客户端的文件
客户端的私钥应该在客户本地，客户生成key和csr
csr交给服务端，服务器根据csr和client_ext.cnf文件生成client.crt，将crt给客户端
客户端收到服务端返回的证书后，结合自己的私钥和根CA证书，打包为PFX文件。
将pfx导入浏览器
"""

# 【本模块在“数字证书登录”流程中的位置】
# 本文件是“客户端证书申请 / 打包”环节的实现（由后端模拟客户端执行完整流程）：
#   用户申请数字证书 → 本模块生成 SM2 密钥对与 CSR → 服务端(CA)签发证书 →
#   本模块把“私钥 + 证书 + 根CA证书”打包为 PFX 文件返回 → 用户把 PFX 导入浏览器，
#   之后浏览器在登录时携带该客户端证书完成身份认证（服务端校验见
#   ca_client_crt_yanzheng.py）。
# 说明：真实场景中客户端私钥应只在用户本机生成，此处为教学演示统一由后端代为生成。
import os
import subprocess
import tempfile
from typing import Optional

"""
注意，用360浏览器edg?不行
"""

# 演示用证书根目录：与项目实际证书存放位置一致（app/certs，内含 rootCA/server/client 子目录）。
# 以当前源码文件为基准，不依赖机器的盘符或启动时的工作目录。
# 以下 ensure 目录存在，供本模块直接读写证书文件
# 确保certificates目录存在
certs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'certs'))
os.makedirs(certs_dir, exist_ok=True)

rootCA_dir = os.path.join(certs_dir, 'rootCA')
os.makedirs(rootCA_dir, exist_ok=True)

server_dir = os.path.join(certs_dir, 'server')
os.makedirs(server_dir, exist_ok=True)

client_dir = os.path.join(certs_dir, 'client')
os.makedirs(client_dir, exist_ok=True)



# 根 CA 密钥 / 证书路径（SM2 与 RSA 两套并存；实际签发客户端证书时使用 SM2 那一套，
# 见文件末尾调用示例 generate_client_cert(..., ca_sm2_cert_path, ca_sm2_key_path, ...)）
ca_sm2_key_path = os.path.join(rootCA_dir, "ca_sm2.key")
ca_sm2_cert_path = os.path.join(rootCA_dir, "ca_sm2.crt")
ca_rsa_key_path = os.path.join(rootCA_dir, "ca_rsa.key")
ca_rsa_cert_path = os.path.join(rootCA_dir, "ca_rsa.crt")

# 客户端证书的扩展配置文件路径（签发客户端证书时用 -extfile 附加，
# 声明证书的密钥用途 / 证书类型等扩展项，约束其只能作为“客户端证书”使用）
client_ext_cnf_test_path = os.path.join(client_dir, "client_ext.cnf")

# 生成“客户端数字证书”主流程（模拟“客户端 → CA 申请 / 签发 / 打包”全过程）：
#   第 1 步：按角色给用户名加前缀（role_用户名），并写入证书 CN 字段，实现“一人一证”区分；
#   第 2 步：在临时目录中生成 SM2 私钥与证书签名请求 CSR；
#   第 3 步：调用 openssl 用根 CA 证书 + 私钥为 CSR 签发 X.509 客户端证书（国密 SM2/SM3）；
#   第 4 步：把“私钥 + 证书 + 根CA证书”打包成 PKCS#12(PFX) 文件并读取为字节流返回。
# 参数：username —— 用户名（将被加角色前缀写入证书 CN）；
#       ca_cert_path / ca_key_path —— 用于签发的根 CA 证书与私钥路径；
#       client_ext_cnf_path —— 客户端证书扩展配置文件（密钥用途 / 证书类型等）；
#       days —— 证书有效期（默认 365 天）；password —— PFX 导出口令（默认 '123456'）；
#       role —— 证书归属角色：'user'（普通用户）/ 'seller'（商家）
# 返回：成功返回 PFX 字节流（供前端下载后导入浏览器）；任一步 openssl 失败返回 None
def generate_client_cert(
    username: str,
    ca_cert_path: str,
    ca_key_path: str,
    client_ext_cnf_path: str,
    days: int = 365,
    password: str = '123456',
    role: str = 'user',
) -> Optional[bytes]:
    # 全部中间产物（私钥 / CSR / 证书 / PFX）都在临时目录中生成，
    # 函数退出后临时目录自动清理，客户端证书只在内存与最终返回的 PFX 字节流中存在
    with tempfile.TemporaryDirectory() as tmpdir:
        # 按角色重命名用户名（user_张三 / seller_李四），使证书 CN 能区分用户与商家；
        # 后续登录验证时据此从 CN 还原出纯用户名（见 ca_client_crt_yanzheng.py）
        if role == 'user':
            username = f"{role}_{username}"
        elif role == 'seller':
            username = f"{role}_{username}"
        else:
            raise ValueError(f"没有{role}这个角色")

        # 定义临时文件路径
        client_key_path = os.path.join(tmpdir, f"{username}.key")
        client_csr_path = os.path.join(tmpdir, f"{username}.csr")
        client_cert_path = os.path.join(tmpdir, f"{username}.crt")
        client_pfx_path = os.path.join(tmpdir, f"{username}.pfx")
        #1.生成客户端SM2私钥
        # 命令：openssl ecparam -name SM2 -genkey -out 客户端私钥
        # —— 生成国密 SM2 椭圆曲线密钥对（客户端私钥，只在本函数内使用，最终打进 PFX）
        try:
                subprocess.run([
                        'openssl', 'ecparam', '-name', 'SM2', '-genkey', '-out', client_key_path
                    ], check=True)

                #2. 生成客户端CSR
                # 命令：openssl req -new —— 用私钥生成证书签名请求(CSR)：
                # 内含公钥与主体信息(CN=user_用户名、emailAddress=…)，但不含私钥，
                # 因此可安全地把 CSR 交给 CA(服务端)去签发证书
                subprocess.run([
                        'openssl', 'req', '-new', '-key', client_key_path,
                        '-out', client_csr_path,
                        '-subj', f'/C=CN/ST=Sichuan/L=Chengdu/O=UESTC/CN={username}/emailAddress=zhangsan@uestc.edu.cn'
                    ], check=True)
                #.4 使用根CA签发客户端证书
                # 命令：openssl x509 -req -CA 根CA证书 -CAkey 根CA私钥 ...
                # —— 即“CA 用自己私钥为 CSR 签名”，把请求转换成真正的 X.509 客户端证书：
                #   -CAcreateserial 维护证书序列号文件；-days 指定有效期；
                #   -sm3 国密摘要算法；-extfile/-extensions 附加客户端证书扩展
                #   （来自 client_ext.cnf：密钥用途 / 证书类型 / 约束等，
                #     约束该证书只能作为客户端证书使用，不能用于签发下级证书）
                subprocess.run([
                    'openssl', 'x509', '-req', '-in', client_csr_path,
                    '-CA', ca_cert_path, '-CAkey', ca_key_path,
                    '-CAcreateserial', '-out', client_cert_path, '-days', f'{days}',
                    '-sm3', '-extfile', client_ext_cnf_path, '-extensions', 'v3_req'
                ], check=True)

    #打包成pfx格式
    # 命令：openssl pkcs12 -export —— 把“客户端私钥(-inkey) + 客户端证书(-in) +
    # 根CA证书(-certfile)”打包成 PKCS#12(PFX) 容器，-password pass:xxx 为 PFX 设置口令；
    # 生成的 PFX 可导入浏览器“个人证书”，登录时浏览器即携带该证书完成客户端认证
                subprocess.run([
                    'openssl', 'pkcs12', '-export',
                    '-out', client_pfx_path,
                    '-inkey', client_key_path,
                    '-in', client_cert_path,
                    '-certfile', ca_cert_path,
                    '-password', f'pass:{password}'
                ], check=True)

                # 读取 PFX 文件的字节流并返回给上层（由接口转成文件下载给用户）
                with open(client_pfx_path, 'rb') as f:
                    pfx_data = f.read()
                return pfx_data

        # openssl 命令执行失败（返回码非 0）：打印命令信息与错误输出，返回 None
        except subprocess.CalledProcessError as e:
                print(f"OpenSSL命令失败: {e}")
                if e.stderr:
                    print(f"错误输出: {e.stderr.decode()}")
                return None
        # 其它异常（如临时文件读写失败）统一捕获，避免把内部异常抛给上层
        except Exception as e:
                print(f"生成证书过程中发生异常: {e}")
                return None
'''使用示例
if __name__ == '__main__':
    print(generate_client_cert('zhangsan',ca_sm2_cert_path,ca_sm2_key_path,client_ext_cnf_test_path,200,'123456'))
'''
