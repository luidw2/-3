# -*- coding: utf-8 -*-
"""快捷瓶颈分解脚本（只观察，不改业务代码）

在 后端flask 目录下运行：
    $env:TUNNEL_ENABLED='0'
    .\.venv\Scripts\python.exe docs\第8-9周性能基线\scripts\quick_breakdown.py

原理：用 monkeypatch 给登录链路的关键函数包一层计时，顺序打 5 次登录，
打印每段平均耗时，用于定位登录接口的瓶颈（bcrypt / 数据库 / 其它）。
说明：脚本会真实执行 5 次登录（会新增 5 条 refresh_token 与审计记录），属正常验证行为。
"""
import sys
import time

sys.path.insert(0, '.')

from app.__init__ import create_app
import app.utils.my_bcrypt as mb
import app.utils.db as db
import app.utils.auth as auth

stats = {}


def wrap(mod, name, label):
    """给 mod.name 包一层计时（函数不存在则跳过，便于新旧版本共用）。"""
    orig = getattr(mod, name, None)
    if orig is None:
        return

    def f(*a, **k):
        t0 = time.perf_counter()
        try:
            return orig(*a, **k)
        finally:
            stats.setdefault(label, []).append((time.perf_counter() - t0) * 1000)

    setattr(mod, name, f)


# 登录链路的各组件（优化前：reset/create_refresh/log_security 三次独立写库）
wrap(mb, 'compare_password', 'bcrypt 校验')
wrap(db, 'get_user_by_username', 'DB 查用户')
wrap(db, 'complete_login_success', 'DB 登录成功写合并(1 次事务)')
wrap(db, 'reset_failed_login', 'DB 重置失败计数(旧实现)')
wrap(db, 'create_refresh_token', 'DB 写 refresh_token(旧实现)')
wrap(db, 'log_security_event', 'DB 写审计(旧实现)')
# 令牌签发（纯计算，量级很小，列出便于完整核算）
wrap(auth, 'generate_access_token', 'access_token 签发')
wrap(auth, 'generate_refresh_token_value', 'refresh_token 生成(不落库)')

app = create_app('development')
client = app.test_client()
body = {"username": "user_1", "password": "123456", "role": "user"}

N = 5
t0 = time.perf_counter()
for _ in range(N):
    resp = client.post('/user/login', json=body)
    assert resp.status_code == 200, (resp.status_code, resp.data[:300])
total = (time.perf_counter() - t0) * 1000

print("\n================ 单请求耗时分解 ================")
print(f"{N} 次连续请求总耗时 {total:.0f}ms，平均单请求 {total/N:.1f}ms")
for label, vals in stats.items():
    print(f"  {label}: 平均 {sum(vals)/len(vals):.2f}ms（调用 {len(vals)} 次）")
print("===============================================\n")
