"""
ca_path.py —— 证书文件路径 / 环境配置模块

在“数字证书登录”流程中的位置：
    集中管理 CA 与各类证书文件的“目录结构与文件名”，供 ca.py / ca_client.py 等
    证书相关模块 import 使用，避免各模块各自硬编码路径、维护混乱。
    证书根目录由环境变量 CERTS_DIR 指定（本项目中指向后端 certs 目录，
    其下按 rootCA / server / client 三个子目录存放根CA、服务端、客户端证书），
    各子目录名与文件名也均支持通过环境变量覆盖（getenv 第二参数为默认值）。
"""
# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# 以源码位置定位后端根目录，不依赖启动命令时的工作目录。
BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / '.env')

# 获取基础路径
# CERTS_DIR 可以是绝对路径，也可以是相对于后端根目录的路径。
# 默认使用项目内的 app/certs，便于项目在不同机器上直接运行。
configured_certs_dir = Path(os.getenv('CERTS_DIR', 'app/certs')).expanduser()
if not configured_certs_dir.is_absolute():
    configured_certs_dir = BACKEND_DIR / configured_certs_dir
certs_dir = str(configured_certs_dir.resolve())

# 确保目录存在
# （首次运行自动创建，避免后续写证书文件时找不到目录）
os.makedirs(certs_dir, exist_ok=True)

# 子目录完整路径
# rootCA(根CA证书) / server(服务端证书) / client(客户端证书) 三个子目录的语义；
# getenv 第二参数为默认子目录名，可用环境变量 ROOTCA_SUBDIR 等覆盖重命名
rootCA_dir = os.path.join(certs_dir, os.getenv('ROOTCA_SUBDIR', 'rootCA'))
server_dir = os.path.join(certs_dir, os.getenv('SERVER_SUBDIR', 'server'))
client_dir = os.path.join(certs_dir, os.getenv('CLIENT_SUBDIR', 'client'))

# 创建子目录（可选，保持原逻辑）
os.makedirs(rootCA_dir, exist_ok=True)
os.makedirs(server_dir, exist_ok=True)
os.makedirs(client_dir, exist_ok=True)

# 具体文件路径：
#   ca_sm2.key / ca_sm2.crt  —— SM2 国密根 CA 私钥与根证书（用于签发客户端证书 / 验链）
#   ca_rsa.key / ca_rsa.crt  —— RSA 根 CA 私钥与根证书（用于签发服务端证书）
#   client_ext_cnf_test_path —— 签发客户端证书时附加的扩展配置文件(密钥用途 / 证书类型等)
# 具体文件路径
ca_sm2_key_path = os.path.join(rootCA_dir, os.getenv('CA_SM2_KEY', 'ca_sm2.key'))
ca_sm2_cert_path = os.path.join(rootCA_dir, os.getenv('CA_SM2_CERT', 'ca_sm2.crt'))
ca_rsa_key_path = os.path.join(rootCA_dir, os.getenv('CA_RSA_KEY', 'ca_rsa.key'))
ca_rsa_cert_path = os.path.join(rootCA_dir, os.getenv('CA_RSA_CERT', 'ca_rsa.crt'))

client_ext_cnf_test_path = os.path.join(client_dir, os.getenv('CLIENT_EXT_CNF', 'client_ext.cnf'))

# 导出所有路径常量，其他模块通过 “from ca_path import *” 即可一次拿到全部证书路径
# 可选：导出所有路径，供其他模块使用
__all__ = [
    'certs_dir', 'rootCA_dir', 'server_dir', 'client_dir',
    'ca_sm2_key_path', 'ca_sm2_cert_path', 'ca_rsa_key_path', 'ca_rsa_cert_path',
    'client_ext_cnf_test_path'
]
