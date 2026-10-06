r"""
后端 Flask 启动入口 —— 本地开发模式（127.0.0.1，HTTPS，无内网穿透）

启动方式（在 后端flask 目录下执行）：
    .venv\Scripts\python.exe run.py

启动后后端以 HTTPS 监听本机 127.0.0.1:5000：
    - 前端 dev server 在本机通过 https://127.0.0.1:5000 调用接口（见前端 src/request.js
      与前端 .env 的 VITE_API_BASE_URL）；
    - 证书为 app/certs/server/server.crt（自签，SAN 含 localhost 与 127.0.0.1），
      浏览器/抓包工具首次访问会有证书警告，选择继续或把证书导入受信任根即可；
    - 不对外网开放，也无需启动 cpolar 等内网穿透工具。

证书说明：
    仓库最初只提交了 server.crt，对应私钥 server.key 与 CA 私钥未入库，
    原 HTTPS 链路无法在其他机器上恢复。当前 server.key/server.crt 为本地
    重新生成的自签证书（不影响安全隧道的国密加解密功能）。

若将来需要局域网/公网访问：
    1. 把下方 host 改为 '0.0.0.0'（监听所有网卡）并放行防火墙 5000 端口；
    2. 启动 cpolar 等隧道工具，将 127.0.0.1:5000 映射为公网域名；
    3. 把前端 .env 中的 VITE_API_BASE_URL 换成对应地址。
"""
import os

from app.__init__ import create_app

# create_app(config_name)：按名称加载 config/config.py 中对应的配置类
# 'development' → DevelopmentConfig（DEBUG=True，CORS 仅放行本机前端 5173 端口）
app = create_app('development')

# HTTPS 证书路径：以源码位置定位后端根目录，不依赖启动命令时的工作目录
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SSL_CERT = os.path.join(_BASE_DIR, 'app', 'certs', 'server', 'server.crt')
SSL_KEY = os.path.join(_BASE_DIR, 'app', 'certs', 'server', 'server.key')

if __name__ == '__main__':
    # host='127.0.0.1'：只监听本机回环地址（本地开发默认，安全）
    # port=5000       ：后端端口，必须与前端 .env 的 VITE_API_BASE_URL 一致
    # ssl_context     ：启用 HTTPS，满足第4周验收“HTTPS 保持启用”
    app.run(host='127.0.0.1', port=5000, debug=True,
            ssl_context=(SSL_CERT, SSL_KEY))
