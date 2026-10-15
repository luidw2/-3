r"""
后端 Flask 启动入口 —— 本地开发模式

启动方式（在 后端flask 目录下执行）：
    .venv\Scripts\python.exe run.py

监听地址由环境变量 FLASK_HOST 控制，默认只监听本机 127.0.0.1：
    - 默认（推荐）：前端 dev server 通过 Vite 同源代理访问后端
      （见前端 vite.config.js 的 server.proxy），浏览器看到的是同源请求，不触发跨域；
    - 需要让虚拟机/局域网直连时（例如 Kali 做 DAST 扫描），临时指定具体网卡：
        PowerShell:  $env:FLASK_HOST='0.0.0.0'; .venv\Scripts\python.exe run.py

实际部署形态建议：
    后端只监听 127.0.0.1，由 Nginx 等统一入口对外提供 HTTPS 并反向代理到 5000，
    即"对外只有一个入口、后端不直接面向网络"，应用层国密隧道是叠加在 HTTPS 之上。
"""
import os

from app.__init__ import create_app

# create_app(config_name)：按名称加载 config/config.py 中对应的配置类
# 'development' → DevelopmentConfig（DEBUG=True，CORS 仅放行本机前端 5173 端口）
app = create_app('development')

if __name__ == '__main__':
    # 默认只监听回环地址：后端不直接对外，符合实际部署形态
    # 需要局域网/虚拟机直连扫描时用环境变量临时打开，不要写死在代码里
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    # debug=False：关闭 Werkzeug 调试控制台，避免调试器暴露
    app.run(host=host, port=5000, debug=False)
