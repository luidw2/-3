"""
后端 Flask 配置模块（本地开发方案：全部运行在 127.0.0.1，无内网穿透）

- 运行入口 后端flask/run.py 通过 create_app('development') 加载 DevelopmentConfig；
- 各配置项优先从 后端flask/.env 读取（见下方 load_dotenv()），未配置时使用代码内默认值；
- CORS_ORIGINS 说明：后端(127.0.0.1:5000) 与前端 dev server(127.0.0.1:5173) 端口不同，
  浏览器里属于跨域请求，CORS 白名单放行的正是"前端页面的来源地址"；
  这里只保留本机地址，代表本项目只在 127.0.0.1 上本地运行、不对外提供服务。
"""
import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 环境变量（数据库、SM 密钥、JWT 密钥等）
class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    # MySQL 配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'user_management'

    DEBUG = False
    # CORS 配置
    CORS_ORIGINS = []  # 生产环境允许的域名列表



class DevelopmentConfig(Config):
    DEBUG = True
    # 开发环境：仅允许本机前端 dev server 跨域访问（本地开发，无内网穿透）
    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173'
    ]


class ProductionConfig(Config):
    DEBUG = False
    # 本地部署：前端同样运行在本机
    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://127.0.0.1:5173'
    ]


# 配置字典
config_dic = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
