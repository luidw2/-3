"""
auth.py —— 通用认证 / JWT 令牌工具模块

在“数字证书(CA)登录”流程中的位置：
    客户端数字证书通过服务端校验后，由本模块为用户签发会话令牌。
    generate_access_token() 会把“本次登录所用的客户端证书 SHA-256 指纹
    (cert_thumbprint)”写入 JWT 载荷，实现“令牌与数字证书绑定”；
    刷新令牌(refresh token)则用于访问令牌过期后重新换取新令牌，
    避免用户频繁重新持证登录。令牌相关的生成 / 校验 / 注销逻辑都集中在本模块。
"""
import os
import json
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from app.utils import db


# ---- JWT 相关配置（均允许通过环境变量覆盖，便于部署时更换，避免硬编码）----
# JWT_SECRET        ：HS256 对称签名密钥（生产环境务必用环境变量注入强随机值）
# ACCESS_TOKEN_TTL_MIN ：访问令牌有效期(分钟，默认 15)
# REFRESH_TOKEN_TTL_DAYS：刷新令牌有效期(天，默认 1)
JWT_SECRET = os.getenv('JWT_SECRET', 'dev-insecure-change-me')
JWT_ALG = 'HS256'
ACCESS_TOKEN_TTL_MIN = int(os.getenv('ACCESS_TOKEN_TTL_MIN', '15'))
REFRESH_TOKEN_TTL_DAYS = int(os.getenv('REFRESH_TOKEN_TTL_DAYS', '1'))


# 工具函数：返回当前 UTC 时间（JWT 的 iat/exp 统一以 UTC 为基准，避免时区换算错误）
def _now_utc():
    """返回当前 UTC 时间（带时区信息）。"""
    return datetime.now(timezone.utc)


# 生成“访问令牌”(access token，JWT)：
# 作用：证书登录校验通过后，为用户签发短期有效的 JWT，并把本次登录所用客户端证书的
#       SHA-256 指纹一并写入载荷，实现“令牌 <-> 证书”绑定，防止令牌被挪到他机使用。
# 参数：user            —— 用户对象（读取 id / username / role / permissions 等字段）
#       cert_thumbprint —— 本次登录客户端证书指纹字符串（可空，为空则 JWT 中不绑定证书）
#       extra_claims    —— 可选：调用方追加的自定义声明（如后台账号登录时写入
#                          totp_ok，表示“是否完成两步验证”，供授权层读取）
# 返回：经 HMAC-SHA256 签名后的 JWT 字符串
def generate_access_token(user, cert_thumbprint, extra_claims=None):
    # 有效期窗口：当前 UTC 时间 ~ 当前时间 + ACCESS_TOKEN_TTL_MIN 分钟
    now = _now_utc()
    exp = now + timedelta(minutes=ACCESS_TOKEN_TTL_MIN)
    # jti：令牌唯一 ID（secrets.token_urlsafe 生成高熵随机串），便于防重放与吊销追溯
    jti = secrets.token_urlsafe(16)
    # 用户权限：数据库字段 permissions 存的是 JSON 字符串，这里解析成列表对象再放进 JWT
    perms = user.permissions if user.permissions else None
    try:
        perms_obj = json.loads(perms) if perms else None
    except Exception:
        # JSON 解析失败（字段为空 / 内容损坏）时置为 None，不阻断签发流程
        perms_obj = None


    '''
    jwt和证书登录联动后要有的字段
    payload = {
    'sub': str(user.id),作用：用户唯一标识，通常为数据库中的用户 ID
    'username': user.username,作用：用户登录名（或显示名）
    'role': user.role,作用：用户角色（如 admin、user、guest）
    'perms': perms_obj,作用：用户的权限列表（如 ["read", "write", "delete"]）
    'iat': int(now.timestamp()),JWT 签发时间（Unix 时间戳）
    'exp': int(exp.timestamp()),作用：JWT 过期时间戳
    'jti': jti,JWT 唯一标识（通常为随机 UUID）
    'typ': 'access',  token 类型，如 access（访问令牌）或 refresh（刷新令牌）
  	"cert_thumbprint": "a1b2c3...（SHA-256指纹）"本次登录时客户端证书的 SHA-256 指纹（或证书序列号 + 颁发者 DN 的哈希）
    }
    '''

    # 组装 JWT 载荷：sub=用户ID、username=登录名、role=角色、perms=权限列表、
    # iat=签发时间、exp=过期时间、jti=唯一ID、typ=令牌类型；
    # 若本次登录携带了客户端证书指纹，则继续追加 cert_thumbprint 字段（见下方）
    payload = {
        'sub': str(user.id),
        'username': user.username,
        'role': user.role,
        'perms': perms_obj,
        'iat': int(now.timestamp()),
        'exp': int(exp.timestamp()),
        'jti': jti,
        'typ': 'access',
    }
    # 添加证书指纹
    if cert_thumbprint:
       payload['cert_thumbprint'] = cert_thumbprint

    # 追加调用方自定义声明（extra_claims，如后台账号的 totp_ok）：
    # 只在这里统一合并，保证所有令牌都经过同一组装逻辑
    if extra_claims:
        payload.update(extra_claims)

    # 使用 HMAC-SHA256（JWT_ALG）+ 共享密钥 JWT_SECRET 对载荷签名，得到最终 JWT 字符串
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return token


# 生成“刷新令牌”(refresh token，不透明随机串，非 JWT)：
# 作用：访问令牌过期后，凭刷新令牌可换取新访问令牌，从而延长登录会话，减少重复持证登录。
# 参数：user_or_seller —— 用户或卖家对象（用于把令牌记录到对应账户名下）
# 返回：刷新令牌字符串；签发同时把令牌与过期时间写入数据库（供校验与吊销）
def generate_refresh_token(user_or_seller):
    now = _now_utc()
    # 过期时间 = 当前 UTC 时间 + 可配置天数（默认 1 天）
    exp = now + timedelta(days=REFRESH_TOKEN_TTL_DAYS)
    # 随机生成 48 字节 url-safe 随机串作为刷新令牌
    # （不签名、不可猜测，安全性完全依赖随机熵，服务端只按数据库比对）
    token = secrets.token_urlsafe(48)
    
    if hasattr(user_or_seller, 'id'):
        if hasattr(user_or_seller, 'role') and user_or_seller.role == 'seller':
            # 卖家账户：令牌挂到 seller_id 名下；expires_at 去掉时区信息(naive)后连同令牌入库
            db.create_refresh_token(seller_id=user_or_seller.id, token=token, expires_at=exp.replace(tzinfo=None))
        else:
            # 普通用户账户：令牌挂到 user_id 名下
            db.create_refresh_token(user_id=user_or_seller.id, token=token, expires_at=exp.replace(tzinfo=None))
    # 把随机令牌串返回给上层保存（前端通常存入 httpOnly Cookie 或本地存储）
    return token


# 校验“访问令牌”：
# 作用：解码并验签前端传来的 JWT，同时强制要求令牌类型为 access。
# 参数：token —— 待校验的 JWT 字符串
# 返回：合法则返回载荷字典（含 sub / cert_thumbprint 等，供后续鉴权使用）；否则返回 None
def verify_access_token(token: str):
    try:
        # jwt.decode：自动验签并检查是否过期；签名错误 / 令牌过期都会抛异常被下方捕获
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        # 只接受 typ='access' 的令牌，防止 refresh 令牌被当作访问令牌使用
        if payload.get('typ') != 'access':
            return None
        return payload
    except Exception:
        # 任何异常（过期、签名不匹配、格式损坏）一律视为校验失败
        return None


# 用“刷新令牌”换取新的访问令牌：
# 作用：核对刷新令牌在数据库中是否存在、未被吊销且未过期，再为对应账户签发新 access token。
# 参数：refresh_token —— 前端提交的刷新令牌字符串
# 返回：成功返回新的 access token(JWT)；令牌无效 / 过期 / 账户停用等返回 None
def refresh_access_token(refresh_token: str):
    # 验证刷新令牌是否有效且未吊销
    session = db.Session()
    try:
        rt = session.query(db.RefreshToken).filter_by(token=refresh_token, revoked=False).first()
        if not rt:
            return None
        if rt.expires_at and datetime.utcnow() >= rt.expires_at:
            return None
        
        # 检查是用户还是卖家
        if rt.user_id:
            user_or_seller = session.query(db.User).filter_by(id=rt.user_id, is_active=True).first()
        elif rt.seller_id:
            user_or_seller = session.query(db.Seller).filter_by(id=rt.seller_id, is_active=True).first()
        else:
            return None
            
        if not user_or_seller:
            return None
            
        # 签发新访问令牌
        # 注：此处为“刷新”场景，调用时未传证书指纹 cert_thumbprint（源码如此，未作改动）
        access = generate_access_token(user_or_seller)
        return access
    finally:
        session.close()


# 注销单个刷新令牌（用户登出时调用）：
# 作用：调用 db 层把指定刷新令牌标记为已吊销(revoked)，使其立即失效。
# 参数：refresh_token —— 需要注销的刷新令牌字符串
def logout(refresh_token: str):
    # 注销单个刷新令牌
    db.revoke_refresh_token(refresh_token)


# 注销某账户名下的全部刷新令牌（如修改密码 / 安全事件后强制下线该账户所有会话）：
# 参数：user_id —— 用户 ID；seller_id —— 卖家 ID，二者按需传入其中一个
def logout_all(user_id=None, seller_id=None):
    # 注销用户或卖家所有刷新令牌
    if user_id:
        db.revoke_all_tokens_for_user(user_id)
    elif seller_id:
        db.revoke_all_tokens_for_seller(seller_id)

