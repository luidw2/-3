# -*- coding: utf-8 -*-
"""
===============================================================================
 logging_config.py —— 后端运行日志（logging 落盘）配置
===============================================================================
【作用】
    与"数据库审计日志(audit_log)"互补：本模块负责程序运行期的日志输出，
    把访问/请求与业务日志同时写到控制台和后端flask/logs/backend.log：
    - backend.log    滚动日志文件（RotatingFileHandler，单文件上限 5MB，
                      保留最近 5 份），格式含时间/级别/来源/消息；
    - 请求访问日志   before_request/after_request 钩子，逐条记录
                     方法、路径、状态码、耗时、来源 IP —— 便于压测、
                     排障与"教师可复现"的访问证据；
    - 异常堆栈       由 logging 捕获（Flask 生产模式）或由代码 logger.exception
                      记录，方便按时间线排查。
【用法】
    - 应用工厂 create_app() 中调用 setup_logging(app)（一次性配置）；
    - 业务代码需要记运行日志时：
        from app.utils.logging_config import get_logger
        log = get_logger(__name__)
        log.info(...) / log.warning(...) / log.exception(...)
===============================================================================
"""
import logging
import os
import time
from logging.handlers import RotatingFileHandler

from flask import g, request

# 后端flask 根目录（本文件位于 后端flask/app/utils/ 下，向上三级）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 日志目录与文件：后端flask/logs/backend.log
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'backend.log')

# 日志格式：时间 | 级别 | 记录器名 | 消息
_LOG_FORMAT = '%(asctime)s | %(levelname)-7s | %(name)s | %(message)s'
_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_logger(name: str) -> logging.Logger:
    """获取（并惰性配置）名为 name 的应用日志器；控制台 + 滚动文件双输出"""
    logger = logging.getLogger(name)
    if not logger.handlers:  # 只配置一次，避免重复 handler
        logger.setLevel(logging.INFO)
        logger.addHandler(_file_handler())
        logger.addHandler(_console_handler())
        logger.propagate = False  # 不向根日志器重复传播
    return logger


def _file_handler() -> logging.Handler:
    os.makedirs(LOG_DIR, exist_ok=True)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024,
                                  backupCount=5, encoding='utf-8')
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
    handler.setLevel(logging.INFO)
    return handler


def _console_handler() -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    return handler


def setup_logging(app):
    """
    应用级日志配置：在 create_app() 中调用一次。
    1) 业务日志器 'app'（info 级别）→ 控制台 + backend.log；
    2) werkzeug 自带访问日志（控制台已有）额外追加写入 backend.log；
    3) 注册 before_request / after_request 钩子：
       每条请求记一行访问日志（方法/路径/状态码/耗时/来源 IP）。
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    file_h = _file_handler()

    # 业务日志器：模块内 get_logger 可复用
    app_log = logging.getLogger('app')
    if not app_log.handlers:
        app_log.setLevel(logging.INFO)
        app_log.addHandler(file_h)
        app_log.addHandler(_console_handler())
        app_log.propagate = False

    # werkzeug 访问日志：保留其默认控制台输出，同时追加到文件
    wz = logging.getLogger('werkzeug')
    if file_h not in wz.handlers:
        wz.addHandler(file_h)
    wz.setLevel(logging.INFO)

    # ---------- 请求级访问日志钩子 ----------
    @app.before_request
    def _record_start_time():
        # 记录请求开始时刻（perf_counter 高精度），供 after_request 计算耗时
        g._req_start = time.perf_counter()

    @app.after_request
    def _log_request(resp):
        try:
            dur_ms = round((time.perf_counter() - g._req_start) * 1000)
            app_log.info(
                'REQ %s %s -> %s (%sms) ip=%s',
                request.method, request.full_path.rstrip('?'),
                resp.status_code, dur_ms, request.remote_addr,
            )
        except Exception:  # 日志失败不影响业务响应
            pass
        return resp
