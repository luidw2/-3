# ============================================================================
# 模块：staff_totp.py —— 后台账号 TOTP 绑定管理接口
# ----------------------------------------------------------------------------
# 文件作用：管理员/审计员账号"绑定 TOTP 软令牌"的完整流程：
#   setup   —— 生成新的 TOTP secret，返回 otpauth URI（认证器扫码/手动录入）
#               与一次性恢复码明文（仅本次展示）；
#   confirm —— 用户输入认证器中的动态码，服务端校验通过后才把 secret 加密
#               落库并启用 totp_enabled。
# 绑定后，该账号下次登录必须走"密码 + 动态码"两步（见 staff_login.py）。
# 注册路由（蓝图 staff_totp）：
#   POST /api/staff/totp/setup      生成绑定材料
#   POST /api/staff/totp/confirm    确认绑定（校验动态码后落库）
# 说明：本文件同时提供 TOTP secret 的 SM4 加密落库 / 解密读取函数
#       （encrypt_totp_secret / decrypt_totp_secret），供 staff_login.py
#       第二步登录时解密使用 —— 加解密逻辑集中在此，避免两处维护。
# ============================================================================
import json
import os
from datetime import datetime

from flask import Blueprint, request, jsonify, g

from app.middleware import rate_limit, jwt_auth_required, staff_required
from app.utils import db, SM4, totp, audit_log

user = Blueprint('staff_totp', __name__)

# 二维码 / otpauth URI 中展示的"机构名"（认证器 App 里显示的名字）
ISSUER = 'SafeShop'


# ----------------------------------------------------------------------------
# build_response：统一 JSON 响应封装（与其它蓝图一致）
# ----------------------------------------------------------------------------
def build_response(code, message='', data=None, error=None, status=200):
    payload = {
        'code': code,
        'message': message,
        'error': error,
        'data': data,
        'time': datetime.utcnow().isoformat() + 'Z'
    }
    return jsonify(payload), status


# ----------------------------------------------------------------------------
# _sm4_key：读取加密 TOTP secret 用的 SM4 密钥
# 密钥来自 .env 的 SM4_KEY（32 位十六进制 = 16 字节），与支付数字信封
# 共用同一密钥管理体系；不硬编码在代码里。
# ----------------------------------------------------------------------------
def _sm4_key():
    key_hex = os.getenv('SM4_KEY', '')
    if len(key_hex) != 32:
        raise RuntimeError('环境变量 SM4_KEY 缺失或长度不正确（应为16字节的十六进制串）')
    return bytes.fromhex(key_hex)


# ----------------------------------------------------------------------------
# encrypt_totp_secret：SM4-CBC 加密 TOTP secret 用于落库
# 说明：CBC 模式每次加密使用随机 IV（16 字节），存储格式为
#       iv.hex() + ':' + 密文.hex() —— 即使两次加密同一 secret 密文也不同，
#       且解密时 IV 与密文一起从库中读出即可。
# 参数：secret 明文 Base32 密钥字符串
# 返回：可落库的加密存储串
# ----------------------------------------------------------------------------
def encrypt_totp_secret(secret: str) -> str:
    iv = os.urandom(16)
    cipher = SM4.sm4_encrypt(_sm4_key(), iv, secret.encode('utf-8'))
    return iv.hex() + ':' + cipher.hex()


def decrypt_totp_secret(stored: str) -> str:
    """读取并解密库中的 TOTP secret，返回明文 Base32 密钥字符串"""
    iv_hex, cipher_hex = stored.split(':', 1)
    plain = SM4.sm4_decrypt(_sm4_key(), bytes.fromhex(iv_hex), bytes.fromhex(cipher_hex))
    return plain.decode('utf-8')


# ----------------------------------------------------------------------------
# 生成 TOTP 绑定材料（POST /api/staff/totp/setup）
# 权限：登录态的后台账号（管理员或审计员）
# 返回：secret（Base32，供认证器手动录入）、otpauth_uri（供生成二维码）、
#       recovery_codes（一次性恢复码明文 —— 只在本接口返回这一次）
# 说明：此步不落库；用户确认（confirm）校验动态码通过后才持久化。
# ----------------------------------------------------------------------------
@user.route('/api/staff/totp/setup', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60, per_ip=True)
@jwt_auth_required
@staff_required
def totp_setup():
    staff = db.get_staff_by_id(g.user.id)
    if not staff:
        return build_response(404, '账号不存在', status=404)
    if staff.totp_enabled:
        return build_response(400, '该账号已绑定 TOTP，如需重绑请先解绑', status=400)

    # 生成随机 Base32 密钥与标准 otpauth URI（认证器扫码添加）
    secret = totp.generate_secret()
    uri = totp.get_otpauth_uri(staff.username, secret, issuer=ISSUER)
    # 同时生成一次性恢复码（明文仅此一次下发）
    recovery_codes = totp.generate_recovery_codes()

    return build_response(0, '生成绑定材料成功，请在认证器中添加后回填动态码确认', data={
        'secret': secret,
        'otpauth_uri': uri,
        'recovery_codes': recovery_codes,
    })


# ----------------------------------------------------------------------------
# 确认绑定（POST /api/staff/totp/confirm）
# 入参：secret（setup 返回的那一个）、code（认证器中当前显示的 6 位动态码）
# 流程：用动态码证明"用户已把该 secret 成功导入认证器" → SM4 加密落库 →
#       记录恢复码哈希 → totp_enabled=True → 写 TOTP_BIND_OK 审计。
# 失败：动态码错误返回 400（不落库，可重新尝试）。
# ----------------------------------------------------------------------------
@user.route('/api/staff/totp/confirm', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60, per_ip=True)
@jwt_auth_required
@staff_required
def totp_confirm():
    data = request.get_json() or {}
    secret = (data.get('secret') or '').strip()
    code = (data.get('code') or '').strip()

    if not secret or not code:
        return build_response(400, 'secret 与动态码不能为空', error='参数缺失', status=400)

    # 用 setup 下发的 secret 校验用户输入的动态码（±1 步时间窗容差）
    ok, _ = totp.verify_totp(secret, code, window=1)
    if not ok:
        audit_log.log_audit('TOTP_BIND_FAILED', g.user.username,
                            'TOTP绑定确认失败：动态码验证未通过（未落库）')
        return build_response(400, '动态码验证失败，请确认认证器显示的是当前动态码', status=400)

    staff = db.get_staff_by_id(g.user.id)
    if not staff:
        return build_response(404, '账号不存在', status=404)

    # 生成恢复码并只保存其 SHA-256 哈希（明文不落库）
    recovery_codes = totp.generate_recovery_codes()
    hashes = totp.hash_recovery_codes(recovery_codes)

    # 加密 secret + 启用 TOTP + 存恢复码哈希（audit=False，统一由下方 TOTP_BIND_OK 留痕）
    db.update_staff(
        staff.id,
        totp_secret_enc=encrypt_totp_secret(secret),
        totp_enabled=True,
        recovery_hashes=json.dumps(hashes),
        audit=False,
    )
    audit_log.log_audit('TOTP_BIND_OK', staff.username,
                          f'账号 {staff.username} 完成 TOTP 绑定，生成 {len(recovery_codes)} 个恢复码')
    # 恢复码明文只在绑定成功这一刻返回给前端展示一次（库中只存哈希）
    return build_response(0, 'TOTP 绑定成功', data={
        'totp_enabled': True,
        'recovery_codes': recovery_codes,
        'recovery_code_count': len(recovery_codes),
    })
