"""
应用工厂模块 —— Flask “应用工厂模式”的组装入口

create_app(config_name) 负责把一个可运行的 Flask 应用“拼装”出来。
课程设计讲解可把它当作“整站组装清单”，按顺序展开：
1) 创建 Flask 实例（指定静态目录与模板目录）；
2) 注册安全响应头中间件 security_headers(app)：应用级中间件，全局生效；
3) 加载配置：按环境(development/production)从 config.config 取配置对象；
4) 配置 CORS 跨域（开发/生产差异化策略，见 _configure_cors）；
5) 初始化数据库连接（app.utils.db.init_db）；
6) 注册全部业务蓝图（登录注册/个人中心/商品/购物车/订单支付）。
说明：各接口的 JWT 认证、角色权限、限流、参数校验等防护，是以“装饰器”
形式在蓝图内部视图函数上使用的（装饰器实现见 app.middleware 包），
本文件只负责把承载这些接口的蓝图统一挂载到应用上。
"""

import os

from flask_cors import CORS
# 业务蓝图模块：app.api.v1 下每个模块内部都导出一个名为 user 的 Blueprint 实例，
# 下面 create_app 中统一把全部蓝图挂载到应用上
from app.api.v1 import (login, register, profile, logout, delete,
                        update, cert_login, create_product, product_profile,
                        delete_product, update_product,add_to_shopping_car,
                        shopping_cart_profile,order,pay,callback,pay_return)
# 后台账号体系蓝图（app.api.staff）：管理员/审计员的登录(TOTP 两步)、
# TOTP 绑定、管理员管理接口、审计员查询导出接口
from app.api.staff import staff_login, staff_totp, admin, auditor
from app.utils import db
from flask import render_template
# 配置字典：{环境名: 配置类}，按 config_name 选出一份写入 app.config
from config.config import config_dic
# 批量导入 app.middleware 包对外公开的全部安全中间件装饰器
# （JWT 认证 / 参数校验 / 限流 / 权限等，供蓝图视图层使用）
from app.middleware import*
from flask import Flask, request, redirect
# ProxyFix：若把应用部署到反向代理(如 Nginx)之后，可借助它把
# “真实客户端 IP / 是否 HTTPS”写回请求，使 request.is_secure 与按 IP 限流
# 在代理场景下依然准确；当前 create_app 未显式挂载（预留），按部署需要启用
from werkzeug.middleware.proxy_fix import ProxyFix
from app.middleware import security_headers
# 运行日志配置（访问日志 + 滚动文件 backend.log）
from app.utils.logging_config import setup_logging

# 定位当前文件所在目录，向上找到项目根目录，再拼接出模板目录：
# template_dir 会在创建 Flask 实例时作为 template_folder 传入，
# 供服务端需要渲染页面/回调页的场景使用
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
template_dir = os.path.join(project_root, 'templates')


def create_app(config_name):
    """
    应用工厂函数：按配置名创建并返回一个配置完整的 Flask 应用实例

    参数:
        config_name: 运行环境名（config.config 中 config_dic 的键），
                     如 'development'（开发环境）/ 'production'（生产环境）

    返回:
        组装完成的 Flask 应用实例（由启动脚本持有并调用 app.run()）

    组装顺序（顺序即防护分层，讲解可对照代码逐条展开）：
    1. 创建 Flask 实例（指定静态资源目录与模板目录）；
    2. 挂载安全响应头中间件（security_headers(app)，注册 after_request 钩子）；
    3. 按环境加载配置对象；
    4. 配置 CORS 跨域策略；
    5. 初始化数据库；
    6. 注册全部业务蓝图。
    """
    # 创建Flask实例
    app = Flask(__name__, static_folder='static', template_folder=template_dir)

    # 应用级安全中间件：security_headers(app) 通过 app.after_request 注册钩子，
    # 使“每一个响应”在返回浏览器前自动补上 CSP / X-Frame-Options / 禁缓存等安全头
    security_headers(app)

    # 应用级运行日志：控制台 + 后端flask/logs/backend.log（含逐条请求访问日志）
    setup_logging(app)

    # 从 config_dic 取出与 config_name 对应的配置类并写入 app.config，
    # CORS_ORIGINS 等安全相关配置项在此之后即可被读取
    app.config.from_object(config_dic[config_name])#加载模式配置

    # CORS 跨域配置：开发环境放行面宽、生产环境收敛到白名单（见下方 _configure_cors）
    _configure_cors(app, config_name)

    # 初始化数据库：建立连接/表结构等（具体实现见 app.utils.db）
    db.init_db()

    # 根路由：仅用于快速验证服务已启动（浏览器访问 "/" 返回 Hello World）
    @app.route('/')
    def index():
        return "Hello, World!"

    # ==================== 注册全部业务蓝图 ====================
    # api_prefix：统一为蓝图加前缀（当前为空串，具体接口路径由各蓝图内部 route 决定）
    api_prefix = ''
    # 下面按业务域分组注册；接口级的安全防护（JWT 认证 / 角色权限 / 限流 /
    # 参数校验）以装饰器形式在各蓝图的视图函数上完成，不重复出现在本文件
    # —— 账号与认证域 ——
    # login：账号密码登录
    app.register_blueprint(login.user, url_prefix=api_prefix)
    # register：用户注册
    app.register_blueprint(register.user, url_prefix=api_prefix)
    # profile：用户信息查询
    app.register_blueprint(profile.user, url_prefix=api_prefix)
    # logout：退出登录
    app.register_blueprint(logout.user, url_prefix=api_prefix)
    # delete：注销账号
    app.register_blueprint(delete.user, url_prefix=api_prefix)
    # update：更新用户资料
    app.register_blueprint(update.user, url_prefix=api_prefix)
    # cert_login：数字证书登录（本项目引入 SM2 证书相关登录方式）
    app.register_blueprint(cert_login.user, url_prefix=api_prefix)
    # —— 商品域（卖家发布/管理商品，买家浏览商品） ——
    # create_product：发布商品（卖家操作）
    app.register_blueprint(create_product.user, url_prefix=api_prefix)
    # product_profile：商品信息查询
    app.register_blueprint(product_profile.user, url_prefix=api_prefix)
    # delete_product：删除商品（卖家操作）
    app.register_blueprint(delete_product.user, url_prefix=api_prefix)
    # update_product：更新商品（卖家操作）
    app.register_blueprint(update_product.user, url_prefix=api_prefix)
    # —— 购物车域 ——
    # add_to_shopping_car：把商品加入购物车
    app.register_blueprint(add_to_shopping_car.user, url_prefix=api_prefix)
    # shopping_cart_profile：购物车信息查询
    app.register_blueprint(shopping_cart_profile.user, url_prefix=api_prefix)
    # —— 订单与支付域 ——
    # order：订单创建/查询
    app.register_blueprint(order.user, url_prefix=api_prefix)
    # pay：发起支付
    app.register_blueprint(pay.user, url_prefix=api_prefix)
    # callback：支付异步回调（接收支付平台服务端发来的支付结果通知）
    app.register_blueprint(callback.user, url_prefix=api_prefix)
    # pay_return：支付完成后浏览器跳回本系统的返回处理
    app.register_blueprint(pay_return.user, url_prefix=api_prefix)
    # —— 后台账号域（staff：管理员 admin / 审计员 auditor） ——
    # staff_login：后台两步登录（密码 → TOTP/恢复码）、me、logout
    app.register_blueprint(staff_login.user, url_prefix=api_prefix)
    # staff_totp：后台账号 TOTP 绑定（setup 生成材料 / confirm 确认启用）
    app.register_blueprint(staff_totp.user, url_prefix=api_prefix)
    # admin：管理员业务接口（用户/商家账号与商品管理，@admin_required）
    app.register_blueprint(admin.user, url_prefix=api_prefix)
    # auditor：审计员业务接口（审计日志查看/导出，@auditor_required）
    app.register_blueprint(auditor.user, url_prefix=api_prefix)





    return app


#工厂函数
def _configure_cors(app, config_name):
    """配置 CORS 跨域设置

    参数:
        app: 已加载配置的 Flask 应用实例
        config_name: 环境名（'development' 走宽松策略，其它环境按生产收紧）

    讲解要点（为什么需要、如何与安全配合）：
    - 本项目前端(Vue)与后端 Flask 分开部署/联调，浏览器“同源策略”默认会拦截
      跨域 AJAX，CORS 的作用是告诉浏览器“哪些来源允许安全地调用本后端”；
    - origins 取自配置项 CORS_ORIGINS（白名单思路：只信任配置里列出的域名）；
    - supports_credentials=True：允许跨域请求携带凭证(Cookie 等)；
    - allow_headers 显式放行 Content-Type / Authorization：携带 JWT 的跨域请求
      会先发 OPTIONS 预检，若请求头不放行，浏览器会直接拦截，认证无从谈起；
    - 开发环境与生产环境使用不同的 methods 集合：生产环境收敛允许的方法，
      减小接口暴露面（开发环境多放行 OPTIONS，便于前后端联调）。
    """
    # 获取 CORS 配置
    cors_origins = app.config.get('CORS_ORIGINS', [])

    if config_name == 'development':
        # 开发环境：允许所有跨域请求
        CORS(app,
             origins=cors_origins,
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization','X-Custom-Header'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
        print(f"CORS 配置: 开发环境 - 允许所有域名跨域访问")
    else:
        # 生产环境：只允许指定域名
        CORS(app,
             origins=cors_origins,
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization','X-Custom-Header'],
             methods=['GET', 'POST', 'PUT', 'DELETE'])
        print(f"CORS 配置: 生产环境 - 允许的域名: {cors_origins}")
