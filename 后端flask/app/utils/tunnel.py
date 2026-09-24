# -*- coding: utf-8 -*-
"""
app/utils/tunnel.py —— 安全隧道（课堂 Demo）
=============================================================================
线上报文（整个请求体就是一个 JSON，两个字段都是 base64）：

    请求: {"env":  "base64( SM2加密(后端公钥, keyblob) )",
           "data": "base64( SM4-CBC(会话密钥, IV, 明文JSON) )"}
    响应: 同样两个字段，信封改用前端公钥加密

    keyblob = {"key","iv","nonce","ts"}  ← 只有持对应私钥的一方能拆开

服务端拆包就四步：拆 JSON → 拆信封(SM2) → 校验时间戳 + nonce → 解密 data(SM4)

为什么 nonce / ts 要放在信封里面：它们是防重放用的（同一个包重发要能拒掉）。
放在明文位置，攻击者重放时改成新的就绕过去了；放进信封里改不动。

自测：在本目录（后端flask）执行  .venv\\Scripts\\python.exe -m app.utils.tunnel
=============================================================================
"""

import base64
import json
import os
import threading
import time

from dotenv import load_dotenv

from . import SM2, SM4

load_dotenv()

# =============================================================================
# 密钥（来自 .env）：Vue 侧一对、Flask 侧一对
# =============================================================================
VUE_PUBLIC_KEY = os.getenv('SM2_VUE_PUBLIC_KEY')          # 后端给前端回包时，用前端公钥封信封
VUE_PRIVATE_KEY = os.getenv('SM2_VUE_PRIVATE_KEY')        # 自测用（浏览器里由 JS 持有）
FLASK_PUBLIC_KEY = os.getenv('SM2_FLASK_PUBLIC_KEY')      # 前端给后端发请求时，用后端公钥封信封
FLASK_PRIVATE_KEY = os.getenv('SM2_FLASK_PRIVATE_KEY')    # 后端拆请求信封时用

# =============================================================================
# 协议常量与参数
# =============================================================================
FIELD_ENV = 'env'        # 报文里放 SM2 信封的字段
FIELD_DATA = 'data'      # 报文里放 SM4 密文的字段

TS_WINDOW_MS = int(os.getenv('TUNNEL_TS_WINDOW_MS', '300000'))   # 时间窗 ±5 分钟
NONCE_TTL_S = int(os.getenv('TUNNEL_NONCE_TTL_S', '600'))        # nonce 记住 10 分钟

# 错误码 -> HTTP 状态码（装饰器直接拿来构造响应）
ERR_PACK = 'TUNNEL_BAD_PACKET'
ERR_UNWRAP = 'TUNNEL_UNWRAP_FAILED'
ERR_TS = 'TUNNEL_TS_EXPIRED'
ERR_REPLAY = 'TUNNEL_REPLAY'
ERR_BODY = 'TUNNEL_BODY_DECRYPT_FAILED'
HTTP_STATUS = {ERR_PACK: 400, ERR_UNWRAP: 400, ERR_TS: 401, ERR_REPLAY: 409, ERR_BODY: 400}


class TunnelError(Exception):
    """隧道校验失败。装饰器里这样用：

        except tunnel.TunnelError as e:
            return jsonify(e.to_dict()), e.http_status
    """

    def __init__(self, code, message=''):
        self.code = code
        self.http_status = HTTP_STATUS.get(code, 400)
        self.message = message or code
        super().__init__(f'[{code}] {self.message}')

    def to_dict(self):
        return {'code': self.code, 'message': self.message}


# =============================================================================
# 一、SM4 加密 body（要求 1）
# =============================================================================
def seal_body(body: bytes, key: bytes, iv: bytes) -> bytes:
    """SM4 加密 body，返回密文的 base64（线上形态）。

    实测与 OpenSSL / 前端 sm-crypto 结果逐字节相同：
        key = iv = 000102030405060708090a0b0c0d0e0f，明文 "AAAAAAA"
        -> 38601c5b95f1c60be75f7e103a0e0a74
    """
    return base64.b64encode(SM4.sm4_encrypt_raw(key, iv, body))


def open_body(body_b64, key: bytes, iv: bytes) -> bytes:
    """把 base64 的密文还原成明文；没有 body 就当空明文（GET 类接口）。

    解不开时统一报 TUNNEL_BODY_DECRYPT_FAILED，不把底层异常细节暴露出去。
    """
    if isinstance(body_b64, str):
        body_b64 = body_b64.encode('ascii', errors='ignore')
    if not body_b64:
        return b''
    try:
        return SM4.sm4_decrypt_raw(key, iv, base64.b64decode(body_b64))
    except Exception:
        raise TunnelError(ERR_BODY, 'SM4 解密失败（密钥不匹配或密文损坏）')


# =============================================================================
# 二、Nonce 与时间窗（要求 3）
# =============================================================================
def check_ts(ts_ms, now_ms=None, window_ms=None):
    """时间窗校验：|现在 - ts| 不超过允许窗口才算新鲜。

    返回实际偏移量（毫秒），便于排查前后端时钟不同步。
    """
    window_ms = TS_WINDOW_MS if window_ms is None else int(window_ms)
    now_ms = int(time.time() * 1000) if now_ms is None else int(now_ms)
    drift_ms = now_ms - int(ts_ms)
    if abs(drift_ms) > window_ms:
        raise TunnelError(ERR_TS, f'时间戳超出窗口 ±{window_ms}ms（drift={drift_ms}ms）')
    return drift_ms


# nonce 表：nonce -> 过期时刻（进程内存，单机 Demo 够用；多进程部署要换 Redis）
_used_nonces = {}
_nonce_lock = threading.Lock()


def check_nonce(nonce: str, now: float = None) -> bool:
    """nonce 一次性校验：第一次用返回 True，重复出现返回 False（说明是重放）。

    简单起见，校验通过就顺手登记（同一个包再发一次必然被打回）。
    """
    now = time.time() if now is None else now
    with _nonce_lock:
        # 先清掉过期的，避免字典无限增长
        for n in [n for n, exp in _used_nonces.items() if exp <= now]:
            del _used_nonces[n]
        if nonce in _used_nonces:
            return False
        _used_nonces[nonce] = now + NONCE_TTL_S
        return True


# =============================================================================
# 三、报文打包 / 拆包
# =============================================================================
def pack(envelope: bytes, data_b64: bytes) -> bytes:
    """把信封和密文打包成整个 body：{"env": "...", "data": "..."}。"""
    return json.dumps({
        FIELD_ENV: base64.b64encode(envelope).decode('ascii'),
        FIELD_DATA: data_b64.decode('ascii'),
    }).encode('utf-8')


def unpack(body) -> tuple:
    """从 body 里取出 (信封 bytes, 密文 base64 bytes)。

    任何格式问题（不是 JSON、缺字段、base64 非法）都报 TUNNEL_BAD_PACKET。
    """
    if isinstance(body, (bytes, bytearray)):
        try:
            body = bytes(body).decode('utf-8')
        except UnicodeDecodeError:
            raise TunnelError(ERR_PACK, '请求体不是 UTF-8 文本')
    try:
        obj = json.loads(body)
        envelope = base64.b64decode(obj[FIELD_ENV])
        data_b64 = obj[FIELD_DATA].encode('ascii')
    except Exception:
        raise TunnelError(ERR_PACK,
                          f'不是合法的隧道包（需要 {FIELD_ENV} 和 {FIELD_DATA} 两个字段）')
    return envelope, data_b64


# =============================================================================
# 四、封包 / 拆包（总入口）
# =============================================================================
def _seal(plaintext: bytes, public_key_hex: str, now_ms=None) -> bytes:
    """封包：生成会话密钥/nonce/ts → SM2 封信封（要求 2）→ SM4 加密 → 打包。"""
    blob = {
        'key': os.urandom(16).hex(),      # 一次性 SM4 会话密钥
        'iv': os.urandom(16).hex(),       # SM4-CBC 初始向量
        'nonce': os.urandom(16).hex(),    # 一次性票号（防重放）
        'ts': int(time.time() * 1000) if now_ms is None else int(now_ms),
    }
    key, iv = bytes.fromhex(blob['key']), bytes.fromhex(blob['iv'])
    # 用对方公钥把 keyblob 封成信封 —— 这就是"SM2 封装会话密钥"
    envelope = SM2.gmssl_sm2_encrypt_raw(public_key_hex, json.dumps(blob).encode('utf-8'))
    return pack(envelope, seal_body(plaintext, key, iv))


def _open(body, private_key_hex: str, now_ms=None) -> bytes:
    """拆包：拆 JSON → 拆信封(SM2) → 校验时间戳 + nonce → 解密 data(SM4)。"""
    envelope, data_b64 = unpack(body)

    # 拆信封 + 取出 keyblob（任何一步出错都算信封无效）
    try:
        blob = json.loads(SM2.gmssl_sm2_decrypt_raw(private_key_hex, envelope).decode('utf-8'))
        key = bytes.fromhex(blob['key'])
        iv = bytes.fromhex(blob['iv'])
        nonce = blob['nonce']
        ts = blob['ts']
    except Exception:
        raise TunnelError(ERR_UNWRAP, 'SM2 拆封失败（私钥不匹配或信封损坏）')

    check_ts(ts, now_ms)
    if not check_nonce(nonce):
        raise TunnelError(ERR_REPLAY, 'nonce 重复（重放请求）')
    return open_body(data_b64, key, iv)


def seal_request(plaintext: bytes, now_ms=None, public_key_hex=None) -> bytes:
    """客户端 -> 服务端：把明文封成整个请求体。用后端公钥封信封。"""
    return _seal(plaintext, public_key_hex or FLASK_PUBLIC_KEY, now_ms)


def open_request(body, private_key_hex=None, now_ms=None) -> bytes:
    """服务端拆一次请求，返回明文 bytes。装饰器 @tunnel_required 调的就是它。"""
    return _open(body, private_key_hex or FLASK_PRIVATE_KEY, now_ms)


def seal_response(payload: bytes, now_ms=None, public_key_hex=None) -> bytes:
    """服务端 -> 客户端：把响应封成整个响应体。用前端公钥封信封。"""
    return _seal(payload, public_key_hex or VUE_PUBLIC_KEY, now_ms)


def open_response(body, private_key_hex=None, now_ms=None) -> bytes:
    """客户端拆一次响应（浏览器里由 sm-tunnel.js 实现，这里供 Python 自测用）。"""
    return _open(body, private_key_hex or VUE_PRIVATE_KEY, now_ms)


# =============================================================================
# 五、自测：python -m app.utils.tunnel
# =============================================================================
def _self_test():
    print('=' * 66)
    print('tunnel.py 自测（课堂 Demo 版）')
    print('=' * 66)
    print(f'时间窗 {TS_WINDOW_MS}ms | nonce 记忆 {NONCE_TTL_S}s')

    # 1) SM4 固定向量：同一个 key/iv/明文，结果每次都必须一样
    key, iv, plain = bytes(range(16)), bytes(range(16)), b'AAAAAAA'
    ct = SM4.sm4_encrypt_raw(key, iv, plain)
    expect = '38601c5b95f1c60be75f7e103a0e0a74'
    assert ct.hex() == expect, f'SM4 向量不符：{ct.hex()}'
    assert SM4.sm4_decrypt_raw(key, iv, ct) == plain
    print(f'[1] SM4 加解密      : {ct.hex()}（可复现，与 OpenSSL/sm-crypto 一致）')

    # 2) SM2 信封往返：明文 n 字节 -> 信封 97+n 字节
    msg = b'{"hello":"tunnel"}'
    env = SM2.gmssl_sm2_encrypt_raw(FLASK_PUBLIC_KEY, msg)
    assert len(env) == 97 + len(msg), f'信封长度 {len(env)}'
    assert SM2.gmssl_sm2_decrypt_raw(FLASK_PRIVATE_KEY, env) == msg
    print(f'[2] SM2 封装/拆封   : 明文 {len(msg)}B -> 信封 {len(env)}B（=97+明文）')

    # 3) 完整请求往返
    now = int(time.time() * 1000)
    data = {'username': 'zhangsan', 'password': '123456', 'role': 'user'}
    payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
    wire = seal_request(payload, now_ms=now)
    assert FIELD_ENV in json.loads(wire.decode()), '报文里应该有 env 字段'
    assert json.loads(open_request(wire, now_ms=now).decode('utf-8')) == data
    print(f'[3] 请求封包/拆封   : 整个 body {len(wire)}B（一个 JSON 两个 base64 字段），明文一致')

    # 4) 重放：同一个包发第二次必须被拒
    wire2 = seal_request(payload, now_ms=now)
    open_request(wire2, now_ms=now)                    # 第一次通过
    try:
        open_request(wire2, now_ms=now)                # 第二次应被拒
        raise AssertionError('重放竟然通过了')
    except TunnelError as e:
        assert e.code == ERR_REPLAY, e.code
        print(f'[4] nonce 重放      : 第二次 -> {e.code}（HTTP {e.http_status}）')

    # 5) 时间窗：±299 秒通过，±301 秒被拒
    wire3 = seal_request(payload, now_ms=now)
    for drift, should_pass in ((299000, True), (-299000, True),
                               (301000, False), (-301000, False)):
        try:
            open_request(wire3, now_ms=now + drift)
            ok = True
        except TunnelError as e:
            ok = (e.code != ERR_TS)
        assert ok == should_pass, f'drift={drift}ms 期望 {should_pass}，实际 {ok}'
        print(f'[5] 时间窗 {drift:+8d}ms : {"通过" if ok else "被拒"}')

    # 6) 格式不对的包（比如旧前端直接发的明文 JSON）
    try:
        open_request(json.dumps({'username': 'x', 'password': 'y'}).encode())
        raise AssertionError('非法包竟然通过了')
    except TunnelError as e:
        assert e.code == ERR_PACK, e.code
        print(f'[6] 非法报文        : -> {e.code}（HTTP {e.http_status}）')

    # 7) 响应方向
    resp = seal_response(b'{"code":0,"msg":"ok"}', now_ms=now)
    assert open_response(resp, now_ms=now) == b'{"code":0,"msg":"ok"}'
    print('[7] 响应封包/拆封   : 正常')

    print()
    print('全部通过。三个机制都可用：SM4 加密 Body、SM2 封装会话密钥、Nonce+时间窗。')


if __name__ == '__main__':
    _self_test()
