"""
安全响应头中间件
功能：设置安全HTTP头部
防护威胁：XSS、点击劫持、MIME类型嗅探等

保护什么 / 怎么工作（应用级中间件，答辩重点）：
- 安全头本质是“发给浏览器的防护指令”：即使后端接口本身安全，也通过 HTTP
  响应头要求浏览器收紧行为，从而缓解 XSS、点击劫持、MIME 嗅探、
  明文降级(HTTP)等客户端侧风险；
- 实现方式：security_headers(app) 在 Flask 应用上注册 app.after_request 钩子，
  使应用内“每一个响应”（含错误响应）在返回浏览器前都会自动补上安全头，
  业务视图无需各自处理，做到“一处配置、全局生效”。

安全头逐条对照（讲解时可展开）：
- Content-Security-Policy           内容安全策略(CSP)：限制可加载资源来源，防 XSS；
- X-Content-Type-Options            防 MIME 类型嗅探；
- X-Frame-Options + frame-ancestors 防点击劫持（禁止页面被 iframe 嵌套）；
- X-XSS-Protection                  老式浏览器内置 XSS 过滤器开关；
- Strict-Transport-Security         强制 HTTPS(HSTS)，防降级/中间人（仅 HTTPS 下发）；
- Referrer-Policy                   限制 Referer 携带范围，防路径信息泄露；
- Permissions-Policy                禁用定位/摄像头等敏感浏览器能力；
- Cache-Control/Pragma/Expires      对 /api/ 接口禁用缓存，防敏感数据残留本地。
"""

from flask import Flask, request, make_response


def security_headers(app: Flask):
    """
    安全响应头中间件
    为所有响应添加安全HTTP头部

    参数:
        app: Flask 应用实例

    返回:
        传入的同一个 app 实例（便于链式调用）；主要副作用是注册 after_request 钩子

    使用方法：
    app = Flask(__name__)
    security_headers(app)
    （本项目的调用点在应用工厂 app/__init__.py 的 create_app 内，
      配置一次即对全局所有响应生效）
    """

    @app.after_request
    def set_security_headers(response):
        """
        为每个响应添加安全头部
        （after_request 钩子：请求处理完成后、响应返回浏览器前自动执行）
        """
        # Content-Security-Policy: 内容安全策略，防护XSS攻击
        # CSP 白名单声明“允许加载哪些来源的资源”，防止页面被注入恶意脚本
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        # 指令速记（答辩）：
        # default-src 'self'：默认只允许加载本站资源；
        # script-src/style-src 额外放行内联代码，以兼容本项目前端(Vue)
        # 打包产物与开发模式的内联脚本；img-src 允许 https 图片与 data 图；
        # frame-ancestors 'none' 禁止被 iframe 嵌套，与下方 X-Frame-Options 双重防点击劫持。
        # 更严格的 CSP 可配合 nonce/hash 去掉 unsafe-inline，属于可选的加固方向。

        # X-Content-Type-Options: 防止MIME类型嗅探
        # 强制浏览器按响应头声明的 Content-Type 解析，禁止“猜类型”执行脚本
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # X-Frame-Options: 防护点击劫持攻击
        # DENY = 任何情况下都禁止本页面被其它站点用 iframe 嵌入
        response.headers['X-Frame-Options'] = 'DENY'

        # X-XSS-Protection: 启用浏览器XSS防护（虽然已过时，但仍有用）
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Strict-Transport-Security: 强制HTTPS（仅在HTTPS连接时设置）
        # HSTS 告知浏览器在 max-age 内只允许走 HTTPS；
        # 仅在 request.is_secure(当前是 HTTPS) 时下发，避免本地 http 调试
        # 被浏览器强制跳转 https 而无法联调
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains; preload'
            )

        # Referrer-Policy: 控制Referer头部信息
        # strict-origin-when-cross-origin：同源请求可带完整路径，
        # 跨域请求只携带源(origin)，减少把内部路径/参数泄露给第三方
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions-Policy: 控制浏览器功能权限（原Feature-Policy）
        # 直接禁用定位/麦克风/摄像头/支付等敏感能力，
        # 即使页面被 XSS 注入也无法擅自调用这些浏览器 API
        response.headers['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=()'
        )

        # Cache-Control: 控制缓存行为（对敏感数据禁用缓存）
        # 仅对 /api/ 开头的接口追加“禁止缓存”头：
        # 登录态、用户资料、订单等敏感响应不允许被浏览器/中间代理缓存到磁盘，
        # 防止下一个使用者读到上一个用户的私有数据（也符合“前后端分离 API 默认不缓存”）
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

        return response

    return app
