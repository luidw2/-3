r"""
后端 Flask 启动入口 —— 本地开发模式（127.0.0.1，无内网穿透）

启动方式（在 后端flask 目录下执行）：
    .venv\Scripts\python.exe run.py

启动后后端服务只监听本机 127.0.0.1:5000：
    - 前端 dev server 在本机通过 http://127.0.0.1:5000 调用接口（见前端 src/request.js）
    - 不对外网开放，也无需再启动 cpolar 等内网穿透工具

若将来需要局域网/公网访问：
    1. 把下方 host 改回 '0.0.0.0'（监听所有网卡）并放行防火墙 5000 端口；
    2. 启动 cpolar 等隧道工具，将 127.0.0.1:5000 映射为公网域名；
    3. 把前端 src/request.js 中的 API_BASE_URL 换成对应的公网地址。
"""
from app.__init__ import create_app

# create_app(config_name)：按名称加载 config/config.py 中对应的配置类
# 'development' → DevelopmentConfig（DEBUG=True，CORS 仅放行本机前端 5173 端口）
app = create_app('development')

if __name__ == '__main__':
    # host='127.0.0.1'：只监听本机回环地址（本地开发默认，安全）
    # host='0.0.0.0'  ：监听所有网卡（配合内网穿透/局域网部署时才需要）
    # port=5000       ：后端端口，必须与前端 src/request.js 的 API_BASE_URL 保持一致
    app.run(host='127.0.0.1', port=5000, debug=True)
