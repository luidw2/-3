# -*- coding: utf-8 -*-
"""
app/middleware/secure_tunnel.py —— 安全隧道装饰器（老师说的"拦截器/AOP"）
=============================================================================
用法和项目里其它中间件完全一样，挂在哪个接口上，哪个接口就走隧道：

    @user.route('/user/login', methods=['POST'])
    @rate_limit(max_requests=100, window_seconds=60, per_ip=True)
    @tunnel_required                      # ← 就加这一行
    def login():
        data = request.get_json()         # 照旧拿到明文，视图一行都不用改

它替视图做了两件事：
   进来：拆信封(SM2) → 校验 nonce/时间戳 → SM4 解密 → 把明文【回填】给 request
   出去：把视图返回的 JSON 用 SM4 加密 + 用前端公钥封信封，再发回去

没挂这个装饰器的接口完全不受影响（支付回调、静态图片、模板页面照旧走明文）。

按钮：环境变量 TUNNEL_ENABLED=0 可让装饰器变成"什么都不做"，
      接口立刻回到改造前的明文行为（方便抓对照包或排查问题）。
=============================================================================
"""

import io
import os
from functools import wraps

from flask import jsonify, make_response, request

from app.utils import tunnel

# 总开关：置 0 时装饰器退化成空装饰器，所有接口回到明文
TUNNEL_ENABLED = os.getenv('TUNNEL_ENABLED', '1') not in ('0', 'false', 'False')


def tunnel_required(f):
    """让被装饰的接口走安全隧道（拆请求 / 加响应）。"""
    if not TUNNEL_ENABLED:
        return f

    @wraps(f)
    def wrapper(*args, **kwargs):
        # ---------- 1) 拆包：拆信封 → 校验时间戳/nonce → 解密 ----------
        try:
            plaintext = tunnel.open_request(request.get_data())
        except tunnel.TunnelError as e:
            # 包不合法：这时还没有可信的会话密钥，没法加密响应，
            # 所以按明文 JSON 返回（前端按"响应里没有 env 字段"识别这种情况）
            return jsonify(e.to_dict()), e.http_status

        # ---------- 2) 把明文回填给 request，视图函数零改动 ----------
        # 注意 1：必须覆盖 request.stream，不能只改 wsgi.input ——
        #         request.stream 是 cached_property，上面 get_data() 已把它缓存成
        #         "装着密文的流"，只换 environ 里的 wsgi.input 不生效（实测拿到 None）
        request.stream = io.BytesIO(plaintext)
        # 注意 2：Content-Type 要一起改成 application/json，否则视图里的
        #         request.get_json() 会直接抛 415 Unsupported Media Type
        request.environ['CONTENT_LENGTH'] = str(len(plaintext))
        request.environ['CONTENT_TYPE'] = 'application/json'
        # 注意 3：清掉 Flask 对 body / json 的缓存，否则视图读到的还是旧密文
        request._cached_data = None
        request._cached_json = (Ellipsis, Ellipsis)

        # ---------- 3) 交给业务视图（login.py 等，代码不用改）----------
        resp = make_response(f(*args, **kwargs))

        # ---------- 4) 响应加密：SM4 + 用前端公钥封信封 ----------
        resp.set_data(tunnel.seal_response(resp.get_data()))
        resp.headers['Content-Type'] = 'application/json'
        return resp

    return wrapper
