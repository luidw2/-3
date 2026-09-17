"""
ca.py —— 自建 CA（证书颁发机构）初始化模块

在“数字证书登录”流程中的位置：
    本模块承担“CA 初始化 / 签发端”的角色，通过调用系统 openssl 命令完成两类工作：
      1. generate_rootCA()   ：生成基于国密 SM2 算法 + SM3 摘要的自签名“根 CA”
                               （根私钥 ca_sm2.key + 根证书 ca_sm2.crt）；
      2. generate_serverCA() ：生成 RSA 体系的 CA 材料，并为“服务端证书”生成私钥 /
                               CSR，再用该 RSA CA 按扩展配置签发服务端证书 server.crt。
    完成初始化后，客户端数字证书由 ca_client.py 等模块调用 CA 材料签发，
    对应课程设计中“根 CA -> 服务端证书 -> 客户端证书”证书链的建立环节。
说明：本文件中的证书文件路径基于 certs 目录结构约定
      （certs/rootCA、certs/server、certs/client），与 ca_path.py 的路径配置配合使用。
"""
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, UTC, timedelta
import os
import subprocess
# 确保certificates目录存在

# 证书目录约定统一放在 certs/ 下：以本文件所在目录向上两级拼接得到
# （本文件位于 app/utils/，向上两级即后端项目根目录下的 certs/）
current_dir = os.path.dirname(__file__)
certs_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'certs'))

# uploads：与证书目录同级的“用户上传文件”目录（不影响证书逻辑，仅作路径约定）
uploads_dir = os.path.join(certs_dir, 'uploads')
'''

certs_dir = r'E:\Python\综设1重构-flask+vue-sm2尝试\综设1重构-flask+vue\后端flask\app\certs'
os.makedirs(certs_dir, exist_ok=True)

rootCA_dir = os.path.join(certs_dir, 'rootCA')
os.makedirs(rootCA_dir, exist_ok=True)

server_dir = os.path.join(certs_dir, 'server')
os.makedirs(server_dir, exist_ok=True)

client_dir = os.path.join(certs_dir, 'client')
os.makedirs(client_dir, exist_ok=True)
'''


# ==================== 密钥 / 证书 / 扩展配置文件路径 ====================
# 约定目录结构（需在运行环境中预先就位，可参考 ca_path.py 的环境变量配置）：
#   certs/rootCA —— 根 CA 目录；certs/server —— 服务端证书目录；certs/client —— 客户端证书目录
# 文件含义：
#   ca_sm2.key / ca_sm2.crt  ：SM2 国密根 CA 私钥与自签名根证书（用于签发客户端证书、验链）
#   ca_rsa.key / ca_rsa.crt  ：RSA 根 CA 私钥与自签名证书（本文件中用于签发服务端证书）
#   server.key / server.csr / server.crt ：服务端私钥、证书签名请求、最终证书
#   server_ext.cnf           ：签发服务端证书时附加的扩展配置（密钥用途 / SAN 等）
#   client.conf              ：客户端证书扩展配置文件（由客户端证书签发流程使用）
ca_sm2_key_path = os.path.join(rootCA_dir, "ca_sm2.key")
ca_sm2_cert_path = os.path.join(rootCA_dir, "ca_sm2.crt")

ca_rsa_key_path = os.path.join(server_dir, "ca_rsa.key")
ca_rsa_cert_path = os.path.join(server_dir, "ca_rsa.crt")
server_key_path = os.path.join(server_dir, "server.key")
server_csr_path = os.path.join(server_dir, "server.csr")
server_cert_path = os.path.join(server_dir, "server.crt")
server_ext_cnf_path = os.path.join(server_dir, "server_ext.cnf")

client_ext_cnf_path = os.path.join(client_dir, "client.conf")
# 生成 SM2 国密“根 CA”（CA 体系中最顶层的信任锚）：
# 作用：一次性完成根 CA 初始化 —— 1) 生成 SM2 密钥对；2) 用该私钥自签名生成根证书。
#       根证书将用于客户端数字证书的签发与信任链验证（登录校验链的起点）。
# 返回：无；产物 ca_sm2.key / ca_sm2.crt 写入 rootCA 目录（命令失败时打印错误）
def generate_rootCA():
    """生成 CA 根证书和私钥"""
    '''
    1.生成 sm2 密钥对
    openssl ecparam -name SM2 -genkey -out ca_sm2.key
    '''
    try:
        # 实际执行上面的 openssl ecparam 命令：
        # openssl ecparam -name SM2 -genkey -out ca_sm2.key
        # —— 生成国密 SM2 椭圆曲线密钥对并写入私钥文件（CA 私钥，需妥善保管）
        subprocess.run([
            'openssl','ecparam','-name','SM2','-genkey','-out', ca_sm2_key_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"命令失败{e}")
    '''
    2. 生成根CA证书（自签名）
    openssl req -x509 -new -nodes 
    -key ca_sm2.key -days 3650 
    -out ca_sm2.crt 
    -subj "/C=CN/ST=Sichuan/L=Chengdu/O=UESTC/CN=MySecureECommerceCA" -sm3
    '''
    try:
        # 实际执行 openssl req -x509 -new -nodes ... -sm3：
        # —— 用根 CA 私钥“自签名”生成 X.509 根证书：
        #    -x509：直接输出自签名证书(而非 CSR)；-nodes：私钥不加密；
        #    -days 3650：有效期 10 年；-subj：证书主体信息(国家/省份/城市/机构/CN)；
        #    -sm3：使用国密摘要算法 SM3（与 SM2 配套组成国密体系）
        subprocess.run([
            'openssl','req', '-x509','-new','-nodes','-key',ca_sm2_key_path,
            '-days','3650','-out',ca_sm2_cert_path, '-subj',
            '/C=CN/ST=Sichuan/L=Chengdu/O=UESTC/CN=MySecureECommerceCA','-sm3'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{e}")

# 生成“服务端证书”全套材料（RSA 体系，与客户端证书使用的 SM2 体系分开维护）：
# 作用：
#   1) 生成 RSA 自签名 CA（ca_rsa.key/.crt）作为服务端证书的签发者；
#   2) 生成服务端私钥 server.key 与 CSR server.csr；
#   3) 写服务端扩展配置 server_ext.cnf（basicConstraints / keyUsage / extendedKeyUsage / SAN）；
#   4) 用 RSA CA 按扩展配置为 CSR 签发服务端证书 server.crt（有效期 365 天）。
# 返回：无；产物全部写入 certs/server 目录（命令失败时打印错误）
def generate_serverCA():
    """生成server所需的文件"""
    '''
    openssl genrsa -out ca_rsa.key 4096
    '''
    try:
        # 实际执行 openssl genrsa -out ca_rsa.key 4096
        # —— 生成 4096 位 RSA 私钥（作为 RSA CA 的私钥）
        subprocess.run([
            'openssl','genrsa','-out', ca_rsa_key_path,'4096'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"命令失败{e}")

    '''
    # 2. 生成根CA证书（自签名）
    openssl req -x509 -new -nodes 
    -key ca.key -sha256 -days 3650 
    -out ca.crt 
    -subj "/C=CN/ST=Sichuan/L=Chengdu/O=UESTC/CN=MySecureECommerceCA"
    '''
    try:
        # 实际执行 openssl req -x509 ... -sha256：
        # —— 用 RSA CA 私钥自签名生成根证书 ca_rsa.crt（-sha256 摘要，有效期 3650 天，
        #    主体信息与 SM2 根证书保持一致：MySecureECommerceCA）
        subprocess.run([
            'openssl','req', '-x509','-new','-nodes','-key',ca_rsa_key_path,
            '-sha256','-days','3650','-out',ca_rsa_cert_path,'-subj',
            '/C=CN/ST=Sichuan/L=Chengdu/O=UESTC/CN=MySecureECommerceCA'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{e}")

    '''
    3.生成服务端私钥
    openssl genrsa -out server.key 2048
    '''
    try:
        # 实际执行 openssl genrsa -out server.key 2048
        # —— 生成服务端 RSA 私钥（2048 位，供 HTTPS 服务端证书使用）
        subprocess.run([
            'openssl', 'genrsa', '-out',server_key_path, '2048'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{e}")
    '''
     4.生成服务端CSR
     openssl req -new -key server.key -out server.csr -subj
      "/C=CN/ST=Sichuan/L=Chengdu/O=UESTC/CN=localhost"
    '''
    try:
        # 实际执行 openssl req -new ...：
        # —— 用服务端私钥生成“证书签名请求”(CSR)：请求内含公钥与主体信息，
        #    主体 CN=localhost（本机部署场景，服务端证书 CN 使用 localhost）
        subprocess.run([
            'openssl', 'req', '-new','-key', server_key_path,
            '-out', server_csr_path, '-subj',
            '/C=CN/ST=Sichuan/L=Chengdu/O=UESTC/CN=localhost'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{e}")
    '''
    5.创建服务端扩展配置文件 server_ext.cnf
    内容：
[ req ]
req_extensions = v3_req
distinguished_name = req_distinguished_name

[ req_distinguished_name ]

[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = DNS:localhost, IP:127.0.0.1
    '''

    config_content = """[ req ]
    req_extensions = v3_req
    distinguished_name = req_distinguished_name

    [ req_distinguished_name ]

    [ v3_req ]
    basicConstraints = CA:FALSE
    keyUsage = nonRepudiation, digitalSignature, keyEncipherment
    extendedKeyUsage = serverAuth
    subjectAltName = DNS:localhost, IP:127.0.0.1
    """

    # 步骤 5（写文件）：把上面的 v3_req 扩展配置写入 server_ext.cnf，
    # 供第 6 步“用根 CA 签发服务端证书”时附加证书扩展属性：
    #   basicConstraints = CA:FALSE          —— 表明该证书不是 CA，不能再签发下级证书；
    #   keyUsage                           —— 声明密钥用途：数字签名 / 密钥加密 / 不可否认；
    #   extendedKeyUsage = serverAuth      —— 声明证书用途为“服务器身份认证(HTTPS)”；
    #   subjectAltName                     —— SAN 扩展：域名 localhost、IP 127.0.0.1。
    # 这些扩展是 X.509 v3 标准扩展，校验端通过解析扩展字段判断证书能否用于某场景。
    with open(server_ext_cnf_path, "w") as f:
        f.write(config_content)


    '''
    6使用根CA签发服务端证书
    openssl x509 -req -in server.csr 
    -CA C:\myCA\rootCA\ca.crt 
    -CAkey C:\myCA\rootCA\ca.key 
    -CAcreateserial -out server.crt -days 365 -sha256 
    -extfile server_ext.cnf -extensions v3_req
    '''
    try:
        # 步骤 6（签发）：openssl x509 -req —— 用根 CA 为服务端 CSR 签发证书：
        #   -in server.csr          ：读取待签发的证书请求；
        #   -CA / -CAkey            ：指定签发者(CA 证书及对应私钥)——即“CA 用自己私钥签名”；
        #   -CAcreateserial         ：自动生成并维护序列号文件(ca_rsa.srl)，确保证书序列号唯一；
        #   -days 365 / -sha256     ：证书有效期与摘要算法；
        #   -extfile/-extensions v3_req：附加上面步骤 5 的扩展配置(用途 / SAN 等)。
        # 签发完成后 server.key + server.crt 即为服务端可用的 HTTPS 证书对。
        subprocess.run([
        'openssl', 'x509', '-req' ,'-in',server_csr_path,
        '-CA', ca_rsa_cert_path,
        '-CAkey', ca_rsa_key_path,
        '-CAcreateserial','-out',server_cert_path,'-days', '365' ,'-sha256' ,
        '-extfile', server_ext_cnf_path, '-extensions','v3_req'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{e}")

# 直接运行本文件时：先初始化 SM2 根 CA，再生成 RSA 服务端证书全套材料
# （相当于“一键初始化 CA 与服务端证书”，正式环境由管理员手动执行一次即可）
if __name__ == '__main__':
    generate_rootCA()
    generate_serverCA()