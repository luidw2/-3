"""
===============================================================================
 db.py —— 数据访问层（Data Access Layer）模块
===============================================================================
【模块作用】
    本文件是电商课程设计项目后端的数据访问层，集中封装了对 MySQL 数据库的全部访问：
    (1) 定义了与数据库表一一对应的 ORM 模型类（User、Seller、Staff、Product、RefreshToken、
        SecurityEvent、Cart、CartItem、Order、OrderItem）；
    (2) 提供了针对各表的业务函数（用户/商家注册管理、商品管理、购物车、订单、登录
        安全控制、刷新令牌管理、安全审计日志等）。
    上层 API 路由（如 api/v1/*.py）只调用本文件提供的函数，不直接书写 SQL，从而把
    "业务逻辑"与"数据库访问细节"解耦 —— 这是答辩讲解分层架构时的重要切入点。

【数据库连接方式】
    1. 采用 SQLAlchemy ORM + pymysql 驱动连接 MySQL，连接串格式为
       mysql+pymysql://user:pass@host:port/dbname；
    2. 连接参数（主机、端口、账号、密码、库名、字符集）全部从 .env 环境变量读取，
       避免把数据库口令硬编码在源码中，体现安全配置规范；
    3. create_engine 配置了数据库连接池：
       - pool_size=10      池内常驻 10 个连接
       - max_overflow=20   高峰期最多再临时创建 20 个连接（应对突发流量）
       - pool_recycle=1800 连接空闲 30 分钟后回收，防止被 MySQL 的
                           wait_timeout 超时机制提前断开
       - pool_timeout=30   等不到空闲连接时最多等待 30 秒
       - pool_pre_ping=True 每次取出连接前先 ping 校验，自动剔除失效连接
    4. Session = sessionmaker(bind=engine)：业务函数统一用 with Session() as session
       打开"独立会话"，用完自动关闭，互不干扰。

【表结构与用途一览】
    - user          前台普通用户账户表（含账号、密码、角色、权限、登录失败锁定字段）
    - seller        商家账户表（字段与 user 相似，另含地址、电话）
    - staff         后台账号表（管理员/审计员：角色、TOTP 加密密钥、恢复码哈希等）
    - product       商品表（价格以"分"为单位整数存储避免浮点误差，外键关联卖家）
    - cart / cart_item      购物车表与购物车明细表（1 用户 - 1 购物车 - N 商品项）
    - order / order_item    订单表与订单明细表（结算时从购物车生成，1 订单 - N 明细）
    - refresh_token 刷新令牌表（持久化双 Token 方案中的 refresh token，支持吊销）
    - security_event 安全审计日志表（登录、账户增删改、商品创建等关键操作留痕）

【重要安全设计（课程设计安全功能点）】
    1. 密码加密存储：user/seller 表的 password 字段保存的是 bcrypt 加盐哈希后的
       密文，不存明文 —— 注册时由上层 my_bcrypt.bcrypt_password() 加密后传入，
       本文件内更新密码（update_user / update_seller）也会先加密再入库；
    2. 登录防暴力破解：failed_attempts（连续失败次数）+ lock_until（锁定截止时间）
       两个字段实现"连续输错 N 次自动锁定一段时间"；计数更新用 SELECT ... FOR UPDATE
       （with_for_update 行锁）防止并发登录下计数错乱；
    3. 会话/刷新令牌管理：refresh token 持久化到 refresh_token 表，既支持单个令牌
       吊销（退出登录），也支持改密/封号后一次性吊销某账号全部令牌（revoke_*）；
    4. 越权访问防护：删除/更新商品需校验 seller_id 归属、购物车项与订单操作需校验
       user_id 归属，防止普通用户操作他人数据（答辩常问的"越权"问题）；
    5. 审计日志：账户创建/删除/更新、商品创建等写操作都会写入 security_event 表，
       形成"操作留痕、可审计"的安全闭环。

【统一编码模式（事务/异常处理）】
    绝大多数函数遵循同一模板：with Session() as session 打开会话 → try 内执行
    增删改查并 session.commit() 提交事务 → except 中 session.rollback() 回滚，
    保证"要么全部成功、要么全部不生效"；同时用 print 打印成功/失败日志便于调试。
===============================================================================
"""
import os
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, Boolean, Text, ForeignKey, func
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, backref, joinedload
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from app.utils import my_bcrypt
from typing import Optional, List, Any
# 加载环境变量
from dotenv import load_dotenv
load_dotenv()  # 这行代码会读取 .env 文件中的变量

# 获取静态文件目录路径
current_dir = os.path.dirname(__file__)
print(f"当前文件目录: {current_dir}")
static_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'static'))
print(f"静态文件目录: {static_dir}")
uploads_dir = os.path.join(static_dir, 'uploads')
print(f"上传文件目录: {uploads_dir}")

Base = declarative_base()

# 现在可以从环境变量中获取值了
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD', )
DB_NAME = os.getenv('DB_NAME')
DB_CHARSET = os.getenv('DB_CHARSET')

# 创建连接字符串
database_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建数据库引擎[citation:3][citation:7]
engine = create_engine(database_url,#连接池管理
                       pool_size=10,  # 根据服务器负载调整[citation:7]
                       max_overflow=20,  # 应对突发流量[citation:7]
                       pool_recycle=1800,  # 回收时间小于数据库的wait_timeout[citation:1][citation:7]
                       pool_timeout=30,  # 避免长时间等待连接[citation:7]
                       pool_pre_ping=True  # 确保连接有效[citation:1]
                       )

# 定义一个数据模型类，对应数据库中的 'users' 表
# ===== 表 user：普通用户账户表 =====
# 用途：存放前台注册用户（role 默认 'user'）的账号信息，一条记录对应一个用户。
# 关键字段：
#   - username   用户名，唯一约束（unique=True），是登录与重名检查的依据
#   - password   登录密码，存 bcrypt 加密后的密文（创建由上层加密传入，更新时本文件加密）
#   - role / permissions  角色标识（'user'/'seller'）与权限列表（JSON 字符串，可空）
#   - is_active  账号启用状态（禁用后应拒绝登录/操作）
#   - failed_attempts / lock_until  连续登录失败次数、锁定截止时间（防暴力破解）
#   - created_at / updated_at  创建、更新时间（数据库自动维护）
class User(Base):
    __tablename__ = 'user'  # 对应数据库中的user表[citation:9]

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(500), nullable=False, unique=True)  # 用户名字段
    password = Column(String(100), nullable=False)  # 密码字段[citation:10]
    is_active = Column(Boolean, nullable=False, default=True)
    role = Column(String(50), nullable=False, default='user')
    permissions = Column(Text, nullable=True)  # 可存储JSON字符串
    failed_attempts = Column(Integer, nullable=False, default=0)
    lock_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

# ===== 表 seller：商家账户表 =====
# 用途：存放卖家账号，字段设计基本复刻 user 表（密码同样存加密密文、含锁定字段），
#       另加地址、电话用于卖家资料展示；与商品表是一对多关系（seller 1 - N product）。
# 关键字段：username/password/role/permissions/is_active/failed_attempts/lock_until
#           含义同 User；address、phone 为商家联系信息（可空）。
class Seller(Base):
    __tablename__ = 'seller'  # 对应数据库中的user表[citation:9]

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(500), nullable=False, unique=True)  # 用户名字段
    password = Column(String(100), nullable=False)  # 密码字段[citation:10]
    address = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    role = Column(String(50), nullable=False, default='seller')
    permissions = Column(Text, nullable=True)  # 可存储JSON字符串
    failed_attempts = Column(Integer, nullable=False, default=0)
    lock_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

# ===== 表 staff：后台账号表（管理员 / 审计员） =====
# 用途：存放系统后台账号 —— 管理员(role='admin')负责用户/商家账号与商品的管理，
#       审计员(role='auditor')只读审计日志与安全事件；与前台 user/seller 账户表
#       完全分离，配合 JWT 角色校验实现互不越权。
# 关键字段：
#   - role                  'admin'（管理员）/ 'auditor'（审计员），登录与授权依据
#   - totp_secret_enc       TOTP 共享密钥经 SM4 加密后的密文（Hex 字符串），为空表示未绑定
#   - totp_enabled          TOTP 是否已绑定启用（启用后后台登录必须走"密码 + 动态码"两步）
#   - recovery_hashes       一次性恢复码的 SHA-256 哈希列表（JSON 字符串）；
#                            明文恢复码只在绑定时向用户展示一次，库中永不留存明文
#   - last_totp_step        最近一次 TOTP 验证成功的时间步（防重放：拒绝小于等于该步的重复码）
#   - failed_attempts / lock_until  登录失败锁定，防暴力破解（策略与 user/seller 一致）
class Staff(Base):
    __tablename__ = 'staff'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(500), nullable=False, unique=True)  # 后台登录名
    password = Column(String(100), nullable=False)               # bcrypt 加密密文
    role = Column(String(50), nullable=False, default='admin')   # 'admin' | 'auditor'
    permissions = Column(Text, nullable=True)                    # 权限列表 JSON（兼容 auth.py 签发令牌）
    is_active = Column(Boolean, nullable=False, default=True)    # 禁用后旧令牌立即失效
    failed_attempts = Column(Integer, nullable=False, default=0)
    lock_until = Column(DateTime, nullable=True)
    totp_secret_enc = Column(Text, nullable=True)                # SM4 加密后的 TOTP secret
    totp_enabled = Column(Boolean, nullable=False, default=False)
    recovery_hashes = Column(Text, nullable=True)                # JSON 数组 [sha256, ...]
    last_totp_step = Column(BigInteger, nullable=True)           # 最近成功时间步（防重放）
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

# ===== 表 product：商品表 =====
# 用途：存放卖家发布的商品，一个卖家可拥有多个商品。
# 关键字段：
#   - name / description  商品名称与文字描述
#   - price    单价，以"分"为单位用整数存储，避免浮点数精度误差（答辩可重点讲）
#   - status   商品状态：'active' 上架 / 'inactive' 下架，商品列表查询按它过滤
#   - seller_id 所属卖家外键（FK -> seller.id，ondelete='CASCADE' 随卖家级联删除）
#   - image_url 商品图片路径；删除商品时本文件会同步删除磁盘上的图片文件
class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # 以分为单位存储，避免浮点误差，也可用 Numeric
    status = Column(String(20), nullable=False, default='active')  # active/inactive 或上架/下架
    seller_id = Column(Integer, ForeignKey('seller.id', ondelete='CASCADE'), nullable=False)
    image_url = Column(String(500), nullable=True)  # 存储商品照片路径
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # 关系：一个卖家可以有多个商品
    seller = relationship('Seller', backref=backref('products', cascade='all'))



# ===== 表 refresh_token：刷新令牌表 =====
# 用途：持久化"双 Token 方案"中的 refresh token（刷新令牌），供刷新 access token 时
#       校验合法性；通过 revoked 字段实现主动吊销 —— 退出登录、改密后作废旧会话等。
# 关键字段：user_id / seller_id（两个外键二选一，表示令牌属于用户还是商家，均可空）、
#           token（令牌字符串，唯一）、expires_at（过期时间）、revoked（是否已吊销）。
class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=True)  # 改为可空
    seller_id = Column(Integer, ForeignKey('seller.id', ondelete='CASCADE'), nullable=True)  # 新增
    token = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # 关系映射
    user = relationship('User', backref=backref('refresh_tokens', cascade='all, delete-orphan'))
    seller = relationship('Seller', backref=backref('refresh_tokens', cascade='all, delete-orphan'))

# ===== 表 security_event：安全审计日志表 =====
# 用途：集中记录安全相关事件（登录成功/失败、账户创建/删除/更新、商品创建等），
#       便于事后审计追责，也是课程设计"安全日志留痕"功能的落点。
# 关键字段：event_type 事件类型（如 ACCOUNT_CREATE_SUCCESS / LOGIN_FAILED 等）、
#           username 操作涉及的账号、details 事件详情文本、created_at 自动记录时间。
class SecurityEvent(Base):#安全日志
    __tablename__ = 'security_event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(100), nullable=False)
    username = Column(String(500), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())#自动记录时间


# ===== 表 cart：购物车表 =====
# 用途：购物车与用户一一对应（user_id 带 unique=True 唯一约束，保证一人一车）；
#       车内具体商品存放在明细表 cart_item。通过关系 user.cart 与 cart.items 关联。
# 关键字段：user_id 唯一外键（FK -> user.id，级联删除）。
class Cart(Base):
    __tablename__ = 'cart'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # 关系：用户和购物车一对一
    user = relationship('User', backref=backref('cart', uselist=False, cascade='all, delete-orphan'))


# ===== 表 cart_item：购物车明细表 =====
# 用途：记录某张购物车内的商品条目（cart 1 - N cart_item）。同一商品在购物车中
#       只保留一条记录，再次加入时累加 quantity（见 add_to_cart）。
# 关键字段：cart_id（所属购物车外键）、product_id（商品外键）、product_name（商品名
#           冗余快照，省去每次联表查询）、quantity（数量，默认 1）。
class CartItem(Base):
    __tablename__ = 'cart_item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey('cart.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # 关系：购物车和商品项一对多
    cart = relationship('Cart', backref=backref('items', cascade='all, delete-orphan'))
    product = relationship('Product', backref=backref('cart_items', cascade='all'))


# ===== 表 order：订单表 =====
# 用途：用户从购物车结算后生成订单，一个用户可拥有多笔订单。
# 关键字段：user_id 外键、status 订单状态（pending 待支付 / paid 已支付 / shipped
#           已发货 / completed 已完成 / cancelled 已取消，默认 pending）、
#           total_price 订单总金额（分）。与明细表 order_item 一对多（order.items）。
class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    status = Column(String(20), nullable=False, default='pending')
    total_price = Column(Integer, nullable=False, default=0)

    items = relationship('OrderItem', backref='order', cascade='all, delete-orphan', lazy='dynamic')

# ===== 表 order_item：订单明细表 =====
# 用途：记录一笔订单所包含的商品快照（order 1 - N order_item）。下单时把商品名、
#       单价、图片等信息"快照"存入明细，即使日后商品被修改或删除，历史订单仍能
#       完整展示（答辩可提"订单快照"设计思想）。
# 关键字段：order_id（所属订单）、product_id（商品外键，仅作关联）、product_name
#           名称快照、price 单价快照、quantity 数量、subtotal 小计=单价×数量、
#           image_url 图片快照。
class OrderItem(Base):
    __tablename__ = 'order_item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    product_name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False, default=0)
    quantity = Column(Integer, nullable=False, default=1)
    subtotal = Column(Integer, nullable=False, default=0)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


Session = sessionmaker(bind=engine)

# ============================================================
# 初始化数据库表结构
# 作用：根据上面定义的全部 ORM 模型（Base.metadata）在 MySQL 中建表，
#       表已存在则保持原样，不存在才创建 —— 幂等操作。
# 说明：由 run.py 在应用启动时调用一次，实现"启动即建表"。
# ============================================================
def init_db():#若表存在，则不变，不存在则创建，要放到run.py中
    Base.metadata.create_all(engine)


####创建用户
# ============================================================
# 创建用户
# 作用：向 user 表插入一条普通用户记录（INSERT）。
# 参数：username 用户名；password 密码 —— 按 register.py 的调用约定此处传入的已是
#       my_bcrypt.bcrypt_password() 加密后的密文，本函数只负责原样入库；
#       email 参数声明但未入库（预留）；role 角色，默认 'user'；
#       permissions_json 权限 JSON 字符串（可空）。
# 返回：成功返回新用户自增 id；失败（异常，如用户名重复触发唯一约束）返回 None。
# 事务/审计：无论成功失败都写 security_event（ACCOUNT_CREATE_SUCCESS / FAILED）
#            审计日志；异常时 session.rollback() 回滚。
# ============================================================
def create_user(username, password, email=None, role='user', permissions_json=None):
    user_info = {
        'username': username,
        'role': role,
    }
    with Session() as session:
        try:
            user = User(
                username=username,
                password=password,
                role=role,
                permissions=permissions_json,
            )
            session.add(user)
            session.commit()
            print(f"用户 {username} 创建成功，ID: {user.id}")

            user_info['id'] = user.id
            log_security_event(
                event_type='ACCOUNT_CREATE_SUCCESS',
                username=username,  # 使用保存的用户信息
                details=f'用户账户已成功创建 - 用户信息: {user_info}'
            )

            return user.id
        except Exception as e:
            session.rollback()
            print(f"创建用户失败: {e}")

            log_security_event(
                event_type='ACCOUNT_CREATE_FAILED',
                username=username,  # 使用保存的用户信息
                details=f'用户账户创建失败 - 用户信息: {user_info}'
            )

            return None
############

###############
# ============================================================
# 按用户名查询用户
# 作用：登录校验、注册重名检查等场景使用；SQL 等价于
#       SELECT * FROM user WHERE username=? LIMIT 1。
# 参数：username 用户名。
# 返回：User ORM 对象（含全部字段），查不到返回 None。
# ============================================================
def get_user_by_username(username):
    """根据用户名查询用户[citation:3]"""
    with Session() as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            return user
        else:
            return None
##############


# ============================================================
# 按 ID 查询用户
# 作用：按主键 id 查询单个用户（主键查询效率最高），供登录后按令牌中的
#       user_id 反查用户信息、更新/删除前定位记录等场景使用。
# 参数：user_id 用户 ID。
# 返回：User 对象；不存在返回 None。
# ============================================================
def get_user_by_id(user_id: int):
    with Session() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            return user
        else:
            return None


# ============================================================
# 删除用户
# 作用：按 id 删除 user 表中的用户记录。
# 参数：user_id 目标用户 ID。
# 返回：成功返回 True；用户不存在或删除异常返回 False。
# 主要步骤：
#   1) 按 id 查询用户，不存在直接返回 False；
#   2) 手工删除该用户名下的刷新令牌（refresh_token），确保其登录态全部作废；
#   3) 删除用户本体（购物车/订单等关联数据由外键 ondelete='CASCADE' 级联清理）；
#   4) 提交后写 ACCOUNT_DELETION_SUCCESS 审计日志。
# 事务/异常：失败时 rollback；except 中用 'user' in locals() 判断是否已查到用户，
#            防止异常发生在查询之前时误用未定义的 user 变量。
# ============================================================
def delete_user(user_id):
    """删除用户"""
    with Session() as session:
        try:
            # 先获取用户信息用于日志记录
            user = session.query(User).filter_by(id=user_id).first()
            if   not user:
                print(f"用户 ID: {user_id} 不存在")
                return False

            # 记录用户信息用于审计
            user_info = {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }

            # 1. 先删除相关的刷新令牌
            session.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()

            # 2. 删除用户
            session.delete(user)
            session.commit()

            print(f"用户 ID: {user_id} 删除成功")

            # 记录安全事件（在提交后）
            log_security_event(
                event_type='ACCOUNT_DELETION_SUCCESS',
                username=user.username,  # 使用保存的用户信息
                details=f'用户账户已成功删除 - 用户信息: {user_info}'
            )
            return True

        except Exception as e:
            session.rollback()
            print(f"删除用户失败: {e}")

            # 记录失败事件
            if 'user' in locals():#检查变量 user 是否在当前局部作用域中定义 。

                log_security_event(
                    event_type='ACCOUNT_DELETION_FAILED',
                    username=user.username,
                    details=f'数据库删除操作失败: {str(e)}'
                )

            return False

# ============================================================
# 更新用户信息（动态字段更新）
# 作用：按 id 找到用户，把 kwargs 中给出的字段动态写入 user 表（改用户名、密码、
#       角色、权限、启用状态等）。
# 参数：user_id 目标用户 ID；kwargs 形如 username='xx'、password='xx' 的字段字典。
# 返回：更新成功返回该 User 对象；用户不存在或出错返回 None。
# 主要步骤：
#   1) 按 id 查询用户；
#   2) 遍历 kwargs：先用 hasattr 校验 User 是否有该属性，避免写入不存在的列；
#      其中 password 字段先经 my_bcrypt.bcrypt_password() 加密再赋值 —— 保证
#      任何改密路径都不会把明文写进数据库；
#   3) 刷新 updated_at 时间戳，commit 提交；
#   4) 写 ACCOUNT_UPDATE_SUCCESS / FAILED 审计日志。
# 事务/异常：出错时 rollback 回滚全部改动。
# ============================================================
def update_user(user_id, **kwargs):
    """更新用户信息"""
    with Session() as session:  # 创建数据库会话
        try:
            # 1. 查找用户
            user = session.query(User).filter_by(id=user_id).first()

            if user:  # 如果找到了用户
                # 2. 动态更新字段
                for key, value in kwargs.items():
                    if hasattr(user, key):  # 检查用户对象是否有这个属性. **kwargs (关键字参数)
                        if key == 'password':
                            a = my_bcrypt.bcrypt_password(value)
                            value = a
                        setattr(user, key, value)  # 设置属性值,user.key = value
                    else :
                        print(f"未找到{key}属性")

                user.updated_at = datetime.utcnow()
                # 4. 提交到数据库
                session.commit()
                print(f"用户 ID: {user_id} 更新成功")
                user_info = {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role,
                }
                log_security_event(
                    event_type='ACCOUNT_UPDATE_SUCCESS',
                    username=user.username,
                    details=f'用户更新成功: {user_info}'
                )

                return user
            else:
                print(f"用户 ID: {user_id} 不存在")
                return None
        except Exception as e:
            session.rollback()  # 出错时回滚
            print(f"更新用户失败: {e}")
            log_security_event(
                event_type='ACCOUNT_UPDATE_FAILED',
                username=user.username,
                details=f'用户更新失败: {user_info}'
            )
            return None
#

####创建商家
# ============================================================
# 创建商家
# 作用：向 seller 表插入一条商家记录（卖家注册接口调用），业务逻辑与 create_user
#       对称，只是操作对象从 User 换成 Seller。
# 参数：seller_name 商家名（存 username 字段）；password 密码密文（上层已加密）；
#       role 默认 'seller'；permissions_json 权限 JSON（可空）。
# 返回：成功返回 True；失败（异常）返回 None。
# 事务/审计：成功/失败都写 ACCOUNT_CREATE_SUCCESS / FAILED 审计日志，且日志中的
#            username 记作 role+商家名（如 seller+xxx），用于区分用户与商家账户；
#            异常时 rollback 回滚。
# ============================================================
def create_seller(seller_name, password, role='seller', permissions_json=None):
    with Session() as session:
        try:
            seller = Seller(
                username=seller_name,
                password=password,
                role=role,
                permissions=permissions_json,
            )
            session.add(seller)
            session.commit()
            print(f"商家 {seller_name} 创建成功，ID: {seller.id}")

            seller_info = {
                'id': seller.id,
                'username': seller.username,
                'role': seller.role,
            }
            log_security_event(
                event_type='ACCOUNT_CREATE_SUCCESS',
                username=role+seller_name,  # 使用保存的用户信息
                details=f'商家账户已成功创建 - 商家信息: {seller_info}'
            )

            return True
        except Exception as e:
            session.rollback()
            print(f"创建商家失败: {e}")

            log_security_event(
                event_type='ACCOUNT_CREATE_FAILED',
                username=role+seller_name,  # 使用保存的用户信息
                details=f'商家账户创建失败 - 商家信息: {seller_info}'
            )

            return None
############


###############
# ============================================================
# 按商家名查询商家
# 作用：商家登录、重名检查使用；SQL 等价于
#       SELECT * FROM seller WHERE username=? LIMIT 1。
# 参数：seller_name 商家名。
# 返回：Seller 对象；不存在返回 None。
# ============================================================
def get_seller_by_seller_name(seller_name):
    """根据用户名查询用户[citation:3]"""
    with Session() as session:
        seller = session.query(Seller).filter_by(username=seller_name).first()
        if seller:
            return seller
        else:
            return None


# ============================================================
# 按 ID 查询商家
# 作用：按主键 id 查询商家记录，供商家登录后取信息、商品归属校验等场景使用。
# 参数：seller_id 商家 ID。
# 返回：Seller 对象；不存在返回 None。
# ============================================================
def get_seller_by_id(seller_id: int):
    with Session() as session:
        seller = session.query(Seller).filter_by(id=seller_id).first()
        if seller:
            return seller
        else:
            return None
##############

# ============================================================
# 删除商家
# 作用：按 id 删除 seller 表记录；与 delete_user 逻辑对称。
# 参数：seller_id 目标商家 ID。
# 返回：成功返回 True；不存在或异常返回 False。
# 主要步骤：查商家 → 删除其名下刷新令牌 → 删除商家本体（商品等由外键级联删除）
#           → 提交并写 ACCOUNT_DELETION_SUCCESS 审计日志。
# 事务/异常：失败回滚；except 中用 'seller' in locals() 防止引用未定义变量。
# ============================================================
def delete_seller(seller_id):
    """删除用户"""
    with Session() as session:
        try:
            # 先获取用户信息用于日志记录
            seller = session.query(Seller).filter_by(id=seller_id).first()
            if   not seller:
                print(f"商家 ID: {seller_id} 不存在")
                return False

            # 记录用户信息用于审计
            seller_info = {
                'id': seller.id,
                'username': seller.username,
                'role': seller.role
            }

            # 1. 先删除相关的刷新令牌
            session.query(RefreshToken).filter(RefreshToken.seller_id == seller_id).delete()

            # 2. 删除用户
            session.delete(seller)
            session.commit()

            print(f"用户 ID: {seller_id} 删除成功")

            # 记录安全事件（在提交后）
            log_security_event(
                event_type='ACCOUNT_DELETION_SUCCESS',
                username=seller.username,  # 使用保存的用户信息
                details=f'商家账户已成功删除 - 商家信息: {seller_info}'
            )
            return True

        except Exception as e:
            session.rollback()
            print(f"删除商家失败: {e}")

            # 记录失败事件
            if 'seller' in locals():#检查变量 user 是否在当前局部作用域中定义 。

                log_security_event(
                    event_type='ACCOUNT_DELETION_FAILED',
                    username=seller.username,
                    details=f'数据库删除操作失败: {str(e)}'
                )

            return False

# ============================================================
# 更新商家信息（动态字段更新）
# 作用：按 id 找到商家，把 kwargs 中给出的字段动态写入 seller 表，逻辑与
#       update_user 对称。
# 参数：seller_id 目标商家 ID；kwargs 要修改的字段（含 password 时为改密）。
# 返回：成功返回 Seller 对象；不存在或出错返回 None。
# 主要步骤：按 id 查询 → hasattr 校验字段 → password 字段先 bcrypt 加密再赋值 →
#           刷新 updated_at → commit → 写 ACCOUNT_UPDATE_SUCCESS / FAILED 审计日志。
# 事务/异常：出错时 rollback 回滚。
# ============================================================
def update_seller(seller_id, **kwargs):
    """更新商家信息"""
    with Session() as session:  # 创建数据库会话
        try:
            # 1. 查找用户
            seller = session.query(Seller).filter_by(id=seller_id).first()

            if seller:  # 如果找到了用户
                # 2. 动态更新字段
                for key, value in kwargs.items():
                    if hasattr(seller, key):  # 检查用户对象是否有这个属性. **kwargs (关键字参数)
                        if key == 'password':
                            a = my_bcrypt.bcrypt_password(value)
                            value = a
                        setattr(seller, key, value)  # 设置属性值,user.key = value
                    else :
                        print(f"未找到{key}属性")

                seller.updated_at = datetime.utcnow()
                # 4. 提交到数据库
                session.commit()
                print(f"商家 ID: {seller_id} 更新成功")
                user_info = {
                    'id': seller.id,
                    'username': seller.username,
                    'role': seller.role,
                }
                log_security_event(
                    event_type='ACCOUNT_UPDATE_SUCCESS',
                    username=seller.username,
                    details=f'商家更新成功: {user_info}'
                )

                return seller
            else:
                print(f"商家 ID: {seller_id} 不存在")
                return None
        except Exception as e:
            session.rollback()  # 出错时回滚
            print(f"更新商家失败: {e}")
            log_security_event(
                event_type='ACCOUNT_UPDATE_FAILED',
                username=seller.username,
                details=f'商家更新失败: {user_info}'
            )
            return None
#联合检查姓名在两个表中有没有
# ============================================================
# 联合检查用户名是否已存在（注册防重名）
# 作用：分别查询 user 与 seller 两张表，只要任一表存在同名记录就返回 True。
# 必要性：本项目用户(user)与商家(seller)是两张独立账户表，若只在单表查重，
#         会出现用户与商家相互"重名"绕过唯一性校验的问题 —— 这是双账户表
#         结构下必须做联合查重的原因。
# 参数：username 待检查的用户名。
# 返回：布尔值；True 表示该用户名已被占用。
# ============================================================
def username_exists_anywhere(username: str) -> bool:
    """检查用户名是否在 user 表或 seller 表中存在"""
    with Session() as session:
        user_exists = session.query(User).filter(User.username == username).first() is not None
        seller_exists = session.query(Seller).filter(Seller.username == username).first() is not None
        return user_exists or seller_exists


# ============================================================
# 后台账号(staff)函数组：管理员 / 审计员账号的增查改删与登录防爆破
# 说明：staff 是与前台 user/seller 分离的独立账户体系（管理员 role='admin'，
#       审计员 role='auditor'），由后台认证接口（app/api/v1/staff_auth.py）
#       通过本组函数访问；password 一律存 bcrypt 密文；TOTP 相关字段
#       （totp_secret_enc / totp_enabled / recovery_hashes / last_totp_step）
#       由 TOTP 绑定与登录接口读写。
# 提示：锁定状态判断可直接复用上面的 is_user_locked(staff)（它只读实例的
#       lock_until 字段，与表无关）；本组另提供 staff 专用的失败计数函数。
# ============================================================
def create_staff(username, password, role='admin'):
    """创建后台账号（管理员/审计员）。
    密码在本函数内先 bcrypt 加密再入库；用户名重复时返回 None。"""
    with Session() as session:
        try:
            # 用户名唯一性检查：重复则拒绝创建
            if session.query(Staff).filter(Staff.username == username).first():
                print(f"后台账号已存在: {username}")
                return None
            staff = Staff(
                username=username,
                password=my_bcrypt.bcrypt_password(password),  # 明文密码在此加密
                role=role,
            )
            session.add(staff)
            session.commit()
            print(f"后台账号 {username} 创建成功，ID: {staff.id}，角色: {role}")
            # 审计留痕：后台账号创建属于关键操作
            log_security_event(
                event_type='STAFF_CREATE',
                username=username,
                details=f'创建后台账号: {username} (role={role})'
            )
            return staff
        except Exception as e:
            session.rollback()
            print(f"创建后台账号失败: {e}")
            return None


def get_staff_by_username(username):
    """按用户名查询后台账号（后台登录第一步定位账号用），未找到返回 None。"""
    with Session() as session:
        return session.query(Staff).filter(Staff.username == username).first()


def get_staff_by_id(staff_id: int):
    """按 ID 查询后台账号（JWT 认证中间件按 role 回查账号状态用），未找到返回 None。"""
    with Session() as session:
        return session.query(Staff).filter(Staff.id == staff_id).first()


def update_staff(staff_id: int, audit: bool = True, **kwargs):
    """动态更新后台账号字段（角色 / 启用状态 / TOTP 字段等）。
    与 update_user 同策略：hasattr 校验字段是否存在，password 若传入会先
    bcrypt 加密再落库。
    参数：audit 默认 True（成功时写 STAFF_UPDATE 审计）；TOTP 步序号等
    高频/内聚更新可传 audit=False，由调用方记录更精确的审计事件。"""
    with Session() as session:
        try:
            staff = session.query(Staff).filter_by(id=staff_id).first()
            if not staff:
                print(f"后台账号 ID: {staff_id} 不存在")
                return None
            for key, value in kwargs.items():
                if hasattr(staff, key):  # 只更新模型真实存在的列
                    if key == 'password':
                        value = my_bcrypt.bcrypt_password(value)  # 改密同样先加密
                    setattr(staff, key, value)
                else:
                    print(f"Staff 无 {key} 属性，已跳过")
            staff.updated_at = datetime.utcnow()
            session.commit()
            print(f"后台账号 ID: {staff_id} 更新成功")
            if audit:  # audit=False 时跳过通用审计，避免高频更新刷屏审计日志
                log_security_event(
                    event_type='STAFF_UPDATE',
                    username=staff.username,
                    details=f'更新后台账号: {staff.id} - {staff.username}'
                )
            return staff
        except Exception as e:
            session.rollback()
            print(f"更新后台账号失败: {e}")
            return None


def delete_staff(staff_id: int) -> bool:
    """删除后台账号；成功返回 True，账号不存在或异常返回 False。"""
    with Session() as session:
        try:
            staff = session.query(Staff).filter_by(id=staff_id).first()
            if not staff:
                print(f"后台账号 ID: {staff_id} 不存在")
                return False
            username = staff.username
            session.delete(staff)
            session.commit()
            log_security_event(
                event_type='STAFF_DELETE',
                username=username,
                details=f'删除后台账号: {staff_id} - {username}'
            )
            return True
        except Exception as e:
            session.rollback()
            print(f"删除后台账号失败: {e}")
            return False


def record_staff_failed_login(staff, max_attempts: int = 10, lock_minutes: int = 1):
    """记录后台账号一次登录失败（防暴力破解）。
    逻辑与 record_failed_login 相同，但固定操作 staff 表；用 with_for_update()
    行锁避免并发登录下失败计数错乱。"""
    with Session() as session:
        try:
            db_staff = session.query(Staff).filter_by(id=staff.id).with_for_update().one()
            db_staff.failed_attempts = (db_staff.failed_attempts or 0) + 1
            if db_staff.failed_attempts >= max_attempts:
                db_staff.lock_until = datetime.utcnow() + timedelta(minutes=lock_minutes)
                db_staff.failed_attempts = 0
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"后台账号登录错误记录失败: {e}")


def reset_staff_failed_login(staff):
    """后台账号登录成功后清零失败次数并解除锁定（操作 staff 表）。"""
    with Session() as session:
        try:
            db_staff = session.query(Staff).filter_by(id=staff.id).with_for_update().one()
            db_staff.failed_attempts = 0
            db_staff.lock_until = None
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"后台账号重置失败计数失败: {e}")



# ---------- 创建商品 ----------
# ============================================================
# 创建商品
# 作用：向 product 表插入一件商品（INSERT），发布成功后写 PRODUCT_CREATE 审计日志。
# 参数：seller_id 发布商品的卖家 ID；name 商品名；price 单价（单位：分）；
#       description 商品描述、image_url 商品图片路径（可空）；
#       status 商品状态，默认 'active'（上架）。
# 返回：成功返回 Product 对象（含自增 id）；异常回滚并返回 None。
# ============================================================
def create_product(seller_id: int, name: str, price: int,
                   description: Optional[str] = None,
                   status: str = 'active',
                   image_url: Optional[str] = None) -> Optional[Product]:
    """
    创建商品
    :param seller_id: 卖家ID
    :param name: 商品名称
    :param price: 价格（单位：分）
    :param description: 商品描述（可选）
    :param status: 商品状态，默认为 'active'（上架）
    :param image_url: 商品照片路径（可选）
    :return: 创建成功的 Product 对象，失败返回 None
    """
    with Session() as session:
        try:
            product = Product(
                seller_id=seller_id,
                name=name,
                description=description,
                price=price,
                status=status,
                image_url=image_url
            )
            session.add(product)
            session.commit()
            print(f"商品 '{name}' 创建成功，ID: {product.id}")

            log_security_event(
                event_type='PRODUCT_CREATE',
                username=f'seller_{seller_id}',
                details=f'创建商品: {product.id} - {name}'
            )

            return product
        except Exception as e:
            session.rollback()
            print(f"创建商品失败: {e}")
            return None


# ---------- 查询商品 ----------
# ============================================================
# 按商品 ID 查询单个商品
# 作用：主键查询 product 表，供商品详情页展示、加购/下单前校验商品是否存在等场景。
# 参数：product_id 商品 ID。
# 返回：Product 对象；不存在或查询异常返回 None。
# ============================================================
def get_product_by_id(product_id: int) -> Optional[Product]:
    """根据商品ID查询单个商品"""
    with Session() as session:
        try:
            return session.query(Product).filter_by(id=product_id).first()
        except Exception as e:
            print(f"查询商品失败 (ID={product_id}): {e}")
            return None


# ============================================================
# 查询某卖家的全部商品
# 作用：卖家后台"我的商品"列表使用；SQL 按 seller_id 过滤并
#       ORDER BY created_at DESC（新发布商品排前面）。
# 参数：seller_id 卖家 ID。
# 返回：Product 对象列表；异常返回空列表。
# ============================================================
def get_products_by_seller(seller_id: int) -> list[Product] :
    """查询指定卖家的所有商品"""
    with Session() as session:
        try:
            return session.query(Product).filter_by(seller_id=seller_id).order_by(Product.created_at.desc()).all()
        except Exception as e:
            print(f"查询卖家商品失败 (seller_id={seller_id}): {e}")
            return []


# ============================================================
# 查询全部"上架中"商品
# 作用：商城前台商品浏览使用 —— 只返回 status='active' 的商品（已下架商品对买家
#       不可见），按创建时间倒序排列。
# 返回：Product 列表；异常返回空列表。
# ============================================================
def get_all_products() -> list[Product]:
    """查询所有上架商品"""
    with Session() as session:
        try:
            return session.query(Product).filter_by(status='active').order_by(Product.created_at.desc()).all()
        except Exception as e:
            print(f"查询商品列表失败: {e}")
            return []


# ============================================================
# 更新商品信息（带卖家归属校验 —— 防越权关键函数）
# 作用：卖家修改自己商品的名称/描述/价格/状态/图片路径。
# 参数：product_id 商品 ID；seller_id 当前操作卖家的 ID（权限校验用）；
#       kwargs 允许更新的字段。
# 返回：成功返回更新后的 Product；商品不存在、无权操作或异常返回 None。
# 安全要点：
#   - 校验商品.seller_id == seller_id，防止卖家 A 篡改卖家 B 的商品；
#   - 更新字段走白名单 {'name','description','price','status','image_url'}，
#     白名单之外的键一律拒绝，避免任意字段注入式更新。
# 事务/异常：失败时 rollback 回滚。
# ============================================================
def update_product(product_id: int, seller_id: int, **kwargs) -> Optional[Product]:
    """
    更新商品信息（需校验卖家身份）
    :param product_id: 商品ID
    :param seller_id: 当前操作用户的卖家ID（用于权限校验）
    :param kwargs: 要更新的字段（name, description, price, status）
    :return: 更新后的 Product 对象，失败或无权操作返回 None
    """
    with Session() as session:
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            if not product:
                print(f"商品不存在 (ID={product_id})")
                return None

            # ✅ 新增：校验卖家身份
            if product.seller_id != seller_id:
                print(f"权限拒绝：卖家 {seller_id} 无权修改商品 {product_id}（属于卖家 {product.seller_id}）")
                return None

            allowed_fields = {'name', 'description', 'price', 'status', 'image_url'}
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(product, key, value)
                else:
                    print(f"警告：字段 '{key}' 不允许更新或不存在")

            session.commit()
            print(f"商品 ID={product_id} 更新成功")
            return product

        except Exception as e:
            session.rollback()
            print(f"更新商品失败: {e}")
            return None

# ============================================================
# 删除商品（带卖家归属校验）
# 作用：卖家删除自己的商品记录，并同步清理磁盘上对应的商品图片文件。
# 参数：product_id 商品 ID；seller_id 当前操作卖家 ID（权限校验用）。
# 返回：成功 True；商品不存在、无权操作或异常 False。
# 主要步骤：
#   1) 归属校验：商品属于该卖家才允许继续（防越权删除他人商品）；
#   2) 删除磁盘图片：应用根目录 = 本文件向上三级（app/utils/db.py → 项目根），
#      再拼上 image_url.lstrip('/') 得到完整图片路径，文件存在则 os.remove；
#   3) 删除 product 记录并 commit。
# 事务/异常：DB 删除失败 rollback；图片文件删除失败只打印日志，不阻断数据库删除
#            （图片删除是文件系统操作，本就不在数据库事务范围内）。
# ============================================================
def delete_product(product_id: int, seller_id: int) -> bool:
    """
    删除指定商品（需校验卖家身份）
    :param product_id: 商品ID
    :param seller_id: 当前操作用户的卖家ID（用于权限校验）
    :return: 删除成功返回 True，失败或无权操作返回 False
    """
    with Session() as session:
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            if not product:
                print(f"商品不存在 (ID={product_id})")
                return False

            # ✅ 新增：校验卖家身份
            if product.seller_id != seller_id:
                print(f"权限拒绝：卖家 {seller_id} 无权删除商品 {product_id}（属于卖家 {product.seller_id}）")
                return False

            # 删除商品图片
            if product.image_url:
                print(f"商品图片URL: {product.image_url}")
                # 参照update_product.py中的实现方式
                # 构建完整的文件路径
                # 获取应用根目录
                app_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                print(f"应用根目录: {app_root}")
                # 构建图片路径
                image_path = os.path.join(app_root, product.image_url.lstrip('/'))
                print(f"完整图片路径: {image_path}")
                
                if os.path.exists(image_path):
                    print(f"文件存在，准备删除")
                    try:
                        os.remove(image_path)
                        print(f"商品图片删除成功: {image_path}")
                    except Exception as e:
                        print(f"删除商品图片失败: {e}")
                else:
                    print(f"文件不存在: {image_path}")
                    # 尝试列出uploads目录中的文件
                    uploads_dir = os.path.join(app_root, 'static', 'uploads')
                    if os.path.exists(uploads_dir):
                        print(f"uploads目录中的文件: {os.listdir(uploads_dir)}")
                    else:
                        print(f"uploads目录不存在: {uploads_dir}")

            session.delete(product)
            session.commit()
            print(f"商品 ID={product_id} 删除成功")

            # 可选：记录安全事件
            # log_security_event(
            #     event_type='PRODUCT_DELETE',
            #     username=f'seller_{seller_id}',
            #     details=f'删除商品: {product_id} - {product.name}'
            # )

            return True

        except Exception as e:
            session.rollback()
            print(f"删除商品失败: {e}")
            return False

# ============================================================
# 批量删除某卖家的全部商品（谨慎使用，常用于注销卖家前的数据清理）
# 作用：先查出该卖家名下全部商品，逐个删除其磁盘图片，再批量删除 product 记录。
# 参数：seller_id 卖家 ID。
# 返回：被删除的商品数量；异常返回 0。
# 事务说明：所有 product 记录由同一条批量 DELETE 语句在同一个事务内删除，
#           出错时整体 rollback，数据库不会出现"删一半留一半"；
#           磁盘图片的删除发生在提交前，属于文件系统操作（不可回滚），
#           失败仅打印日志继续执行。
# ============================================================
def delete_products_by_seller(seller_id: int) -> int:
    """
    删除指定卖家的所有商品（谨慎使用）
    :return: 被删除的商品数量
    """
    with Session() as session:
        try:
            # 先获取所有要删除的商品
            products = session.query(Product).filter_by(seller_id=seller_id).all()
            count = len(products)
            
            # 删除商品图片
            app_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            for product in products:
                if product.image_url:
                    print(f"商品图片URL: {product.image_url}")
                    # 构建图片路径
                    image_path = os.path.join(app_root, product.image_url.lstrip('/'))
                    print(f"完整图片路径: {image_path}")
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                            print(f"商品图片删除成功: {image_path}")
                        except Exception as e:
                            print(f"删除商品图片失败: {e}")
                    else:
                        print(f"文件不存在: {image_path}")
            
            # 删除商品记录
            session.query(Product).filter_by(seller_id=seller_id).delete()
            session.commit()
            print(f"已删除卖家 ID={seller_id} 的 {count} 件商品")
            return count
        except Exception as e:
            session.rollback()
            print(f"批量删除商品失败: {e}")
            return 0


# ============================================================
# 获取全部商家
# 作用：查询 seller 表所有记录（管理员后台"查看用户和商家列表"用），
#       返回 ORM 对象而非字典，便于上层按需序列化。
# 返回：按创建时间倒序排列的 Seller 对象列表；异常返回空列表。
# ============================================================
def get_all_sellers():
    """获取所有Seller对象（而不是字典）"""
    with Session() as session:
        try:
            query = session.query(Seller)
            sellers = query.order_by(Seller.created_at.desc()).all()
            return sellers
        except Exception as e:
            print(f"获取商家对象列表失败: {e}")
            return []


# ============================================================
# 获取全部用户
# 作用：查询 user 表所有记录（管理后台用户管理列表用），返回 ORM 对象而非字典，
#       便于前端序列化时按需取字段。
# 返回：按创建时间倒序排列的 User 对象列表；异常返回空列表。
# ============================================================
def get_all_users():
    """获取所有User对象（而不是字典）"""
    with Session() as session:
        try:
            query = session.query(User)
            users = query.order_by(User.created_at.desc()).all()
            return users

        except Exception as e:
            print(f"获取用户对象列表失败: {e}")
            return []
###从0开始计



# ============================================================
# 判断账号当前是否处于锁定状态（登录前检查）
# 作用：lock_until 为空表示从未锁定（返回 False）；
#       否则用当前时间与 lock_until 比较：还没到解锁时间则判定仍锁定。
# 参数：user 传入 User/Seller 对象（含 lock_until 字段）。
# 返回：布尔值，True 表示账号仍在锁定期内，应拒绝登录。
# ============================================================
def is_user_locked(user) -> bool:
    if user.lock_until is None:
        return False
    return datetime.utcnow() < user.lock_until


# ============================================================
# 记录一次登录失败（防暴力破解核心函数）
# 作用：登录密码错误时把该账号 failed_attempts 加 1；当累计失败次数达到阈值
#       max_attempts 时，设置 lock_until = 当前时间 + lock_minutes，即锁定账号
#       lock_minutes 分钟（默认 10 次失败锁 1 分钟），并把计数清零等待下一轮。
# 参数：user 传入的对象用于判断身份归属（有 role='seller' 的查 Seller 表，否则查
#       User 表）；max_attempts 失败阈值；lock_minutes 锁定分钟数。
# 事务/并发：查询使用 with_for_update()（SELECT ... FOR UPDATE 行锁），多个并发
#            登录请求对同一账号计数时串行化，避免计数被并发覆盖 —— 安全细节，
#            答辩可重点展开。
# 异常：回滚并打印日志（登录主流程不受影响）。
# ============================================================
def record_failed_login(user, max_attempts: int = 10, lock_minutes: int = 1):
    with Session() as session:
        try:
            if hasattr(user, 'role') and user.role == 'seller':
                db_user = session.query(Seller).filter_by(id=user.id).with_for_update().one()
            else:
                db_user = session.query(User).filter_by(id=user.id).with_for_update().one()
            db_user.failed_attempts = (db_user.failed_attempts or 0) + 1
            if db_user.failed_attempts >= max_attempts:
                db_user.lock_until = datetime.utcnow() + timedelta(minutes=lock_minutes)
                db_user.failed_attempts = 0
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"登录错误记录失败: {e}")


# ============================================================
# 重置登录失败计数（登录成功时调用）
# 作用：账号登录成功或手动解锁后，把 failed_attempts 清零、lock_until 置空，
#       表示该账号恢复正常状态。
# 参数：user 传入登录成功的用户/商家对象（按 role 决定更新 Seller 或 User 表）。
# 事务/并发：同样使用 with_for_update() 行锁，保证与 record_failed_login
#            并发执行时的计数一致性；异常回滚并打印日志。
# ============================================================
def reset_failed_login(user):
    with Session() as session:
        try:
            if hasattr(user, 'role') and user.role == 'seller':
                db_user = session.query(Seller).filter_by(id=user.id).with_for_update().one()
            else:
                db_user = session.query(User).filter_by(id=user.id).with_for_update().one()
            db_user.failed_attempts = 0
            db_user.lock_until = None
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"重置失败登录计数错误: {e}")


# ============================================================
# 分页查询安全审计日志（审计员"查看/导出日志"用）
# 作用：按条件从 security_event 表分页查询安全事件，支持：
#       - event_type 精确匹配；
#       - start / end 时间范围过滤（'YYYY-MM-DD' 或 'YYYY-MM-DD HH:MM:SS'；
#         只给日期时 end 按“当天最后一刻”处理，即包含当天）。
# 参数：page 页码；page_size 每页条数；event_type / start / end 可空。
# 返回：dict {total, page, page_size, events:[{id,event_type,username,details,created_at}]}
# ============================================================
def query_security_events(page: int = 1, page_size: int = 20,
                          event_type: Optional[str] = None,
                          start: Optional[str] = None,
                          end: Optional[str] = None) -> dict:
    """分页查询安全审计日志（支持事件类型与时间范围过滤）"""
    with Session() as session:
        try:
            query = session.query(SecurityEvent)

            if event_type:
                query = query.filter(SecurityEvent.event_type == event_type)

            # 解析时间过滤条件（兼容“只给日期”的写法）
            if start:
                try:
                    start_dt = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    start_dt = datetime.strptime(start, '%Y-%m-%d')
                query = query.filter(SecurityEvent.created_at >= start_dt)
            if end:
                try:
                    end_dt = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    # 只给了日期：把当天 23:59:59.999 作为上界，保证包含当天记录
                    end_dt = datetime.strptime(end, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(SecurityEvent.created_at < end_dt)

            total = query.count()
            events = query.order_by(SecurityEvent.created_at.desc()) \
                          .offset((page - 1) * page_size) \
                          .limit(page_size) \
                          .all()

            return {
                'total': total,
                'page': page,
                'page_size': page_size,
                'events': [
                    {
                        'id': e.id,
                        'event_type': e.event_type,
                        'username': e.username,
                        'details': e.details,
                        'created_at': e.created_at.isoformat() if e.created_at else None,
                    }
                    for e in events
                ],
            }
        except Exception as e:
            print(f"查询安全审计日志失败: {e}")
            return {'total': 0, 'page': page, 'page_size': page_size, 'events': []}


# ============================================================
# 创建刷新令牌记录
# 作用：登录成功后把生成的 refresh token 持久化到 refresh_token 表（INSERT），
#       供后续"用 refresh token 换新 access token"时校验。
# 参数：user_id / seller_id 令牌归属（用户或商家，二选一）；
#       token 令牌字符串；expires_at 过期时间。
# 说明：失败时回滚并 raise —— 与多数函数"吞掉异常"不同，创建令牌失败属于关键
#       流程错误，主动抛出让上层感知登录/续期失败。
# ============================================================
def create_refresh_token(user_id=None, seller_id=None, token=None, expires_at=None):
    with Session() as session:
        try:
            rt = RefreshToken(
                user_id=user_id,
                seller_id=seller_id,
                token=token,
                expires_at=expires_at
            )
            session.add(rt)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"创建刷新令牌失败: {e}")
            raise


# ============================================================
# 吊销单个刷新令牌（退出登录时调用）
# 作用：把指定 token 记录的 revoked 置为 True（软删除，不物理删除，保留审计线索），
#       之后该令牌便不能再用于刷新 access token。
# 参数：token 要吊销的令牌字符串。
# 说明：令牌不存在则静默跳过；异常回滚并打印日志。
# ============================================================
def revoke_refresh_token(token: str):
    with Session() as session:
        try:
            rt = session.query(RefreshToken).filter_by(token=token).first()
            if rt:
                rt.revoked = True
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"注销刷新令牌失败: {e}")


# ============================================================
# 吊销某用户全部有效刷新令牌（改密/封号/安全退出全部设备时调用）
# 作用：一次性把该用户所有 revoked=False 的令牌置为 True —— UPDATE 语句直接
#       按条件批量更新，无需先查出逐条修改。
# 参数：user_id 目标用户 ID。
# 说明：用于"修改密码后旧令牌全部失效"等安全场景，配合安全事件日志使用；
#       异常回滚并打印日志。
# ============================================================
def revoke_all_tokens_for_user(user_id: int):
    with Session() as session:
        try:
            session.query(RefreshToken).filter_by(user_id=user_id, revoked=False).update({RefreshToken.revoked: True})
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"注销用户所有刷新令牌失败: {e}")


# ============================================================
# 吊销某商家全部有效刷新令牌
# 作用：与 revoke_all_tokens_for_user 对称，针对 seller_id 批量吊销令牌，
#       供商家改密、账号被冻结等场景作废旧登录态。
# 参数：seller_id 目标商家 ID。
# 说明：异常回滚并打印日志。
# ============================================================
def revoke_all_tokens_for_seller(seller_id: int):
    with Session() as session:
        try:
            session.query(RefreshToken).filter_by(seller_id=seller_id, revoked=False).update({RefreshToken.revoked: True})
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"注销卖家所有刷新令牌失败: {e}")


# ============================================================
# 记录安全事件（安全审计的统一出口）
# 作用：向 security_event 表追加一条审计记录（INSERT），供登录监控、账户操作
#       留痕使用；本文件中 create/delete/update 系列函数都会调用它。
# 参数：event_type 事件类型（如 ACCOUNT_CREATE_SUCCESS / ACCOUNT_UPDATE_FAILED）；
#       username 涉及的账号；details 事件详情文本。
# 说明：审计失败不影响主业务流程（仅打印日志），避免"日志写不进导致业务失败"。
# ============================================================
def log_security_event(event_type: str, username: str, details: str):
    """记录安全相关事件到数据库。"""
    with Session() as session:
        try:
            event = SecurityEvent(event_type=event_type, username=username, details=details)
            session.add(event)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"记录安全事件失败: {e}")


# ---------- 购物车相关操作 ----------
# ============================================================
# 创建购物车（"首次加购"时自动建车）
# 作用：给用户建立一张购物车；若用户已有购物车则直接返回现有购物车（cart.user_id
#       有唯一约束，一人一车，不会重复建车）。
# 参数：user_id 用户 ID。
# 返回：Cart 对象；用户不存在或异常返回 None。
# 主要步骤：先验证用户存在 → 查是否已有购物车（有则直接返回）→ 新建并 commit。
# ============================================================
def create_cart(user_id: int) -> Optional[Cart]:
    """
    创建购物车
    :param user_id: 用户ID
    :return: 创建的Cart对象，失败返回None
    """
    with Session() as session:
        try:
            # 检查用户是否存在
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                print(f"用户不存在 (ID={user_id})")
                return None
            
            # 检查用户是否已有购物车
            existing_cart = session.query(Cart).filter_by(user_id=user_id).first()
            if existing_cart:
                print(f"用户已有购物车 (用户ID={user_id})")
                return existing_cart
            
            # 创建购物车
            cart = Cart(user_id=user_id)
            session.add(cart)
            session.commit()
            print(f"购物车创建成功 (用户ID={user_id})")
            return cart
        except Exception as e:
            session.rollback()
            print(f"创建购物车失败: {e}")
            return None


# ============================================================
# 按用户 ID 获取购物车
# 作用：根据 user_id 查询该用户的购物车对象（通过关系可再取 items 明细）。
# 参数：user_id 用户 ID。
# 返回：Cart 对象；不存在或异常返回 None。
# ============================================================
def get_cart_by_user_id(user_id: int) -> Optional[Cart]:
    """
    根据用户ID获取购物车（包含商品项）
    :param user_id: 用户ID
    :return: Cart对象，不存在返回None
    """
    with Session() as session:
        try:
            return session.query(Cart).filter_by(user_id=user_id).first()
        except Exception as e:
            print(f"获取购物车失败: {e}")
            return None


# ============================================================
# 添加商品到购物车（加购核心函数）
# 作用：向用户购物车加入指定数量的商品。
# 参数：user_id 用户 ID；product_id 商品 ID；quantity 数量（默认 1）。
# 返回：dict（含 cart_item 的 id / product_id / product_name / quantity）；
#       用户或商品不存在、异常时返回 None。
# 主要步骤：
#   1) 校验用户、商品都存在；
#   2) 获取购物车，没有则先创建（session.flush() 立即拿到 cart.id 以便插明细）；
#   3) 判断该商品是否已在车中：
#      - 已在 → 在原条目上累加数量（quantity += quantity）；
#      - 未在 → 新建 CartItem，商品名取商品表当前 name 冗余存储；
#   4) commit 后返回"可序列化的字典"（不直接返回 ORM 对象，方便 API 直接 JSON 化）。
# 事务/异常：异常回滚并返回 None。
# ============================================================
def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> Optional[dict]:
    """
    添加商品到购物车
    :param user_id: 用户ID
    :param product_id: 商品ID
    :param quantity: 商品数量
    :return: 包含购物车商品信息的字典，失败返回None
    """
    with Session() as session:
        try:
            # 检查用户是否存在
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                print(f"用户不存在 (ID={user_id})")
                return None
            
            # 检查商品是否存在
            product = session.query(Product).filter_by(id=product_id).first()
            if not product:
                print(f"商品不存在 (ID={product_id})")
                return None
            
            # 获取或创建购物车
            cart = session.query(Cart).filter_by(user_id=user_id).first()
            if not cart:
                cart = Cart(user_id=user_id)
                session.add(cart)
                session.flush()  # 获取cart.id
            
            # 检查商品是否已在购物车中
            existing_item = session.query(CartItem).filter_by(
                cart_id=cart.id,
                product_id=product_id
            ).first()
            
            if existing_item:
                # 更新数量
                existing_item.quantity += quantity
                session.commit()
                print(f"购物车商品数量更新成功 (购物车ID={cart.id}, 商品ID={product_id}, 数量={existing_item.quantity})")
                # 返回字典而不是对象
                return {
                    'id': existing_item.id,
                    'product_id': existing_item.product_id,
                    'product_name': existing_item.product_name,
                    'quantity': existing_item.quantity
                }
            else:
                # 添加新商品，使用从数据库获取的商品名称
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product_id,
                    product_name=product.name,
                    quantity=quantity
                )
                session.add(cart_item)
                session.commit()
                print(f"商品添加到购物车成功 (购物车ID={cart.id}, 商品ID={product_id})")
                # 返回字典而不是对象
                return {
                    'id': cart_item.id,
                    'product_id': cart_item.product_id,
                    'product_name': cart_item.product_name,
                    'quantity': cart_item.quantity
                }
        except Exception as e:
            session.rollback()
            print(f"添加商品到购物车失败: {e}")
            return None


# ============================================================
# 从购物车移除商品（带归属校验）
# 作用：删除购物车中的某一条商品项。
# 参数：user_id 用户 ID（归属校验：只能删自己的车）；cart_item_id 明细项 ID。
# 返回：删除成功 True；不存在 / 不属于该用户 / 异常 False。
# 主要步骤：CartItem JOIN Cart 后同时按 cart_item_id 与 Cart.user_id 过滤，
#           从 SQL 层面保证"只能操作本人购物车内的明细"（防越权删除）。
# ============================================================
def remove_from_cart(user_id: int, cart_item_id: int) -> bool:
    """
    从购物车移除商品
    :param user_id: 用户ID（用于归属校验）
    :param cart_item_id: 购物车商品项ID
    :return: 删除成功返回True，失败返回False
    """
    with Session() as session:
        try:
            cart_item = session.query(CartItem).join(Cart).filter(
                CartItem.id == cart_item_id,
                Cart.user_id == user_id
            ).first()
            if not cart_item:
                print(f"购物车商品项不存在或不属于该用户 (ID={cart_item_id}, 用户ID={user_id})")
                return False
            
            session.delete(cart_item)
            session.commit()
            print(f"商品从购物车移除成功 (ID={cart_item_id})")
            return True
        except Exception as e:
            session.rollback()
            print(f"从购物车移除商品失败: {e}")
            return False

# ============================================================
# 更新购物车商品数量（带归属校验）
# 作用：修改车中某条商品项的数量。
# 参数：user_id 用户 ID（归属校验）；cart_item_id 明细项 ID；quantity 新数量。
# 返回：成功返回 dict（id / product_id / quantity）；失败返回 None。
# 边界处理：quantity <= 0 视为"删除该条目"（数量不能为非正数）；
#           JOIN Cart 校验归属，防止改他人购物车。
# ============================================================
def update_cart_item_quantity(user_id: int, cart_item_id: int, quantity: int) -> Optional[dict]:
    """
    更新购物车商品数量
    :param user_id: 用户ID（用于归属校验）
    :param cart_item_id: 购物车商品项ID
    :param quantity: 商品数量
    :return: 更新后的商品信息字典，失败返回None
    """
    with Session() as session:
        try:
            cart_item = session.query(CartItem).join(Cart).filter(
                CartItem.id == cart_item_id,
                Cart.user_id == user_id
            ).first()
            if not cart_item:
                print(f"购物车商品项不存在或不属于该用户 (ID={cart_item_id}, 用户ID={user_id})")
                return None
            
            if quantity <= 0:
                # 如果数量为0或负数，删除商品
                session.delete(cart_item)
                session.commit()
                print(f"购物车商品删除成功 (ID={cart_item_id})")
                return None
            
            cart_item.quantity = quantity
            session.commit()
            print(f"购物车商品数量更新成功 (ID={cart_item_id}, 数量={quantity})")
            # 返回可序列化的字典
            return {
                'id': cart_item.id,
                'product_id': cart_item.product_id,
                'quantity': cart_item.quantity
            }
        except Exception as e:
            session.rollback()
            print(f"更新购物车商品数量失败: {e}")
            return None

# ============================================================
# 获取用户购物车中的所有商品项
# 作用：购物车页面展示使用；借助 Cart.items 关系直接返回明细列表，
#       用户没有购物车时返回空列表。
# 参数：user_id 用户 ID。
# 返回：CartItem 列表（可能为空）；异常返回空列表。
# ============================================================
def get_cart_items(user_id: int) -> List[CartItem]:
    """
    获取用户购物车中的所有商品
    :param user_id: 用户ID
    :return: 购物车商品项列表
    """
    with Session() as session:
        try:
            cart = session.query(Cart).filter_by(user_id=user_id).first()
            if not cart:
                return []
            return cart.items
        except Exception as e:
            print(f"获取购物车商品失败: {e}")
            return []

# ============================================================
# 删除购物车（按购物车 ID）
# 作用：删除一张购物车记录；车中明细（cart_item）通过外键级联一并删除。
# 参数：cart_id 购物车 ID。
# 返回：成功 True；购物车不存在或异常 False。
# ============================================================
def delete_cart(cart_id: int) -> bool:
    """
    删除购物车
    :param cart_id: 购物车ID
    :return: 删除成功返回True，失败返回False
    """
    with Session() as session:
        try:
            cart = session.query(Cart).filter_by(id=cart_id).first()
            if not cart:
                print(f"购物车不存在 (ID={cart_id})")
                return False
            
            session.delete(cart)
            session.commit()
            print(f"购物车删除成功 (ID={cart_id})")
            return True
        except Exception as e:
            session.rollback()
            print(f"删除购物车失败: {e}")
            return False


# ============================================================
# 按用户 ID 删除购物车
# 作用：根据 user_id 找到并删除该用户的整张购物车，供注销账号清数据、
#       管理员清空用户购物车等场景使用（先由 user_id 反查 cart 再删）。
# 参数：user_id 用户 ID。
# 返回：成功 True；无购物车或异常 False。
# ============================================================
def delete_cart_by_user_id(user_id: int) -> bool:
    """
    根据用户ID删除购物车
    :param user_id: 用户ID
    :return: 删除成功返回True，失败返回False
    """
    with Session() as session:
        try:
            cart = session.query(Cart).filter_by(user_id=user_id).first()
            if not cart:
                print(f"用户购物车不存在 (用户ID={user_id})")
                return False
            
            session.delete(cart)
            session.commit()
            print(f"用户购物车删除成功 (用户ID={user_id})")
            return True
        except Exception as e:
            session.rollback()
            print(f"删除用户购物车失败: {e}")
            return False


# ============================================================
# 获取购物车明细（连带商品对象，购物车结算页用）
# 作用：一次查询同时取出购物车、其下所有明细项、以及每个明细关联的商品对象，
#       避免逐条查询商品造成 N+1 次数据库往返。
# 参数：user_id 用户 ID。
# 返回：CartItem 列表；无购物车时返回空列表。
# 实现要点：joinedload(Cart.items).joinedload(CartItem.product) 让 SQLAlchemy
#           用 LEFT JOIN 一次性把三层数据取回（预加载 eager loading）。
# ============================================================
def get_cart_items_with_products(user_id: int):
    with Session() as session:
        cart = session.query(Cart)\
            .options(joinedload(Cart.items).joinedload(CartItem.product))\
            .filter_by(user_id=user_id).first()
        return cart.items if cart else []

# ============================================================
# 按用户 + 商品查询购物车明细项
# 作用：判断某商品是否已在该用户购物车中（如"加入购物车"按钮的状态展示、
#       防重复加购）。
# 参数：user_id 用户 ID；product_id 商品 ID。
# 返回：CartItem 对象；无购物车或车中无此商品返回 None。
# ============================================================
def get_cart_item_by_user_and_product(user_id: int, product_id: int) -> Optional[CartItem]:
    """
    根据用户ID和商品ID获取购物车商品项
    :param user_id: 用户ID
    :param product_id: 商品ID
    :return: CartItem对象，不存在返回None
    """
    with Session() as session:
        try:
            # 先获取用户购物车
            cart = session.query(Cart).filter_by(user_id=user_id).first()
            if not cart:
                return None

            # 查找购物车中的商品项
            return session.query(CartItem).filter_by(
                cart_id=cart.id,
                product_id=product_id
            ).first()
        except Exception as e:
            print(f"获取购物车商品项失败: {e}")
            return None
#create_user('liu', 'm8846682')
#update_user(1, username = 'liu',password = 'm88423')


# ---------- 分页查询所有商品 ----------
# ============================================================
# 分页查询商品（支持多条件组合过滤 —— 商城列表/卖家后台通用）
# 作用：组装"动态 WHERE 条件"的分页 SELECT，实现页码 + 每页条数 + 状态 + 卖家 +
#       商品名模糊搜索的组合过滤，一次调用返回本页数据与分页元信息。
# 参数：page 页码（从 1 开始）；per_page 每页条数（默认 20）；status 状态过滤
#       （'active' 上架 / 'inactive' 下架）；seller_id 卖家过滤；
#       name_keyword 商品名称模糊搜索关键字。
# 返回：dict —— items（本页 Product 对象）、total（总条数）、page、per_page、
#       pages（总页数 = ceil(total/per_page)）；异常返回全 0 的空结构。
# 实现要点：
#   - joinedload(Product.seller) 预加载卖家信息，避免列表页逐条回查卖家（防 N+1）；
#   - 过滤条件按 if 判断逐个追加，实现"动态拼 SQL"；
#   - name_keyword 转成 LIKE '%关键字%' 做模糊匹配；
#   - 先 count() 统计总数，再用 offset((page-1)*per_page).limit(per_page) 截取本页。
# ============================================================
def get_all_products_paginated(
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    seller_id: Optional[int] = None,
    name_keyword: Optional[str] = None
) -> dict:
    """
    分页查询商品（支持过滤）
    :param page: 页码（从1开始）
    :param per_page: 每页数量
    :param status: 状态过滤（'active' / 'inactive'）
    :param seller_id: 卖家ID过滤
    :param name_keyword: 商品名称模糊搜索
    :return: 包含 items 和 total 的字典
    """
    with Session() as session:
        try:
            query = session.query(Product).options(joinedload(Product.seller))

            if status:
                query = query.filter(Product.status == status)
            if seller_id is not None:
                query = query.filter(Product.seller_id == seller_id)
            if name_keyword:
                query = query.filter(Product.name.like(f'%{name_keyword}%'))

            total = query.count()
            items = query.order_by(Product.created_at.desc()) \
                         .offset((page - 1) * per_page) \
                         .limit(per_page) \
                         .all()

            return {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
        except Exception as e:
            print(f"分页查询商品失败: {e}")
            return {'items': [], 'total': 0, 'page': page, 'per_page': per_page, 'pages': 0}


# ---------- 分页查询指定卖家的商品 ----------
# ============================================================
# 分页查询指定卖家的商品（卖家"我的商品"管理页）
# 作用：复用通用的 get_all_products_paginated，只是固定传入 seller_id，
#       得到只属于该卖家的分页商品列表（含状态、关键字过滤能力）。
# 参数：seller_id 卖家 ID；其余参数同 get_all_products_paginated。
# 返回：与 get_all_products_paginated 相同的 dict 结构。
# ============================================================
def get_seller_products_paginated(
    seller_id: int,
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    name_keyword: Optional[str] = None
) -> dict:
    """
    分页查询指定卖家的商品
    """
    return get_all_products_paginated(
        page=page,
        per_page=per_page,
        status=status,
        seller_id=seller_id,
        name_keyword=name_keyword
    )


# ---------- 订单相关操作 ----------
# ============================================================
# 从购物车生成订单（下单核心函数，含并发防护）
# 作用：把用户购物车中的商品"结算"成一笔订单：计算总价、生成 order 主表 +
#       order_item 明细（商品快照），并清空购物车 —— 整个过程在同一个事务内。
# 参数：user_id 下单用户 ID。
# 返回：订单信息 dict（order_id / user_id / total_price / status / created_at /
#       items 明细）；购物车为空、商品失效或异常返回 None。
# 主要步骤：
#   1) 查询购物车并 with_for_update() 加行锁 —— 防止并发请求把同一批购物车商品
#      重复生成多笔订单（并发安全，答辩可重点讲）；
#   2) 遍历购物车明细：按最新 price 计算 subtotal=price×quantity 并累加总价，
#      组装"订单商品快照"（商品不存在则放弃下单）；
#   3) 插入 Order（status='pending'），flush 先拿到 order.id；
#   4) 逐条插入 OrderItem —— 商品名/单价/小计/图片在此处"快照"存档，之后商品
#      改价或删除都不影响历史订单；
#   5) 删除购物车明细（清空购物车），最后 commit 一次性提交。
# 事务/异常：任一步出错整体 rollback，购物车数据保持原样不丢失。
# ============================================================
def create_order(user_id: int) -> Optional[dict]:
    """
    从购物车生成订单
    :param user_id: 用户ID
    :return: 订单信息字典，失败返回None
    """
    with Session() as session:
        try:
            # 获取用户购物车及其商品（加行锁防止并发重复下单）
            cart = session.query(Cart).filter_by(user_id=user_id).with_for_update().first()
            if not cart or not cart.items:
                print(f"购物车为空 (用户ID={user_id})")
                return None

            # 计算总金额并生成订单商品列表
            total_price = 0
            order_items = []
            for item in cart.items:
                # 检查商品是否存在
                product = session.query(Product).filter_by(id=item.product_id).first()
                if not product:
                    print(f"商品不存在 (ID={item.product_id})")
                    return None

                # 计算小计
                subtotal = product.price * item.quantity
                total_price += subtotal

                # 构建订单商品信息
                order_items.append({
                    'product_id': item.product_id,
                    'product_name': item.product_name,
                    'price': product.price,
                    'quantity': item.quantity,
                    'subtotal': subtotal,
                    'image_url': product.image_url
                })

            # 创建订单
            order = Order(
                user_id=user_id,
                total_price=total_price,
                status='pending'
            )
            session.add(order)
            session.flush()  # 获取order.id

            # 创建订单商品记录
            for item in order_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item['product_id'],
                    product_name=item['product_name'],
                    price=item['price'],
                    quantity=item['quantity'],
                    subtotal=item['subtotal'],
                    image_url=item['image_url']
                )
                session.add(order_item)

            # 清空购物车
            for item in cart.items:
                session.delete(item)

            session.commit()
            print(f"订单创建成功 (订单ID={order.id}, 用户ID={user_id})")

            # 返回订单信息
            return {
                'order_id': order.id,
                'user_id': order.user_id,
                'total_price': order.total_price,
                'status': order.status,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'items': order_items
            }
        except Exception as e:
            session.rollback()
            print(f"创建订单失败: {e}")
            return None


# ============================================================
# 获取订单详情（带归属校验）
# 作用：按订单号查询一笔订单及其全部明细，供"订单详情页"展示。
# 参数：order_id 订单 ID；user_id 用户 ID（权限校验，只能看自己的订单）。
# 返回：订单详情 dict（含 items 明细列表）；订单不存在、不属于该用户或异常
#       返回 None。
# 实现要点：查询条件直接写 WHERE id=? AND user_id=? —— 归属校验内置在 SQL 中，
#           从根上防止越权查看他人订单；明细单独按 order_id 查出后组装成
#           可序列化的字典列表（含 ISO 格式时间）。
# ============================================================
def get_order_detail(order_id: int, user_id: int) -> Optional[dict]:
    """
    获取订单详情
    :param order_id: 订单ID
    :param user_id: 用户ID（用于权限验证）
    :return: 订单详情字典，失败返回None
    """
    with Session() as session:
        try:
            # 获取订单并验证归属
            order = session.query(Order).filter_by(id=order_id, user_id=user_id).first()
            if not order:
                print(f"订单不存在或不属于该用户 (订单ID={order_id}, 用户ID={user_id})")
                return None

            # 获取订单商品
            order_items = []
            for item in session.query(OrderItem).filter_by(order_id=order_id).all():
                order_items.append({
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_name': item.product_name,
                    'price': item.price,
                    'quantity': item.quantity,
                    'subtotal': item.subtotal,
                    'image_url': item.image_url,
                    'created_at': item.created_at.isoformat() if item.created_at else None
                })

            # 返回订单详情
            return {
                'order_id': order.id,
                'user_id': order.user_id,
                'total_price': order.total_price,
                'status': order.status,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'items': order_items
            }
        except Exception as e:
            print(f"获取订单详情失败: {e}")
            return None


# ============================================================
# 分页获取用户订单列表（"我的订单"页）
# 作用：按用户分页查询订单，并额外统计每笔订单包含的商品件数 item_count 一并返回，
#       避免前端拿到订单后还要逐单二次查询明细数量。
# 参数：user_id 用户 ID；page 页码（从 1 开始）；page_size 每页条数（默认 10）。
# 返回：dict —— total（订单总数）、page、page_size、orders（列表，每项含
#       order_id / total_price / status / item_count / created_at）；异常返回 None。
# 实现要点：
#   - 子查询：把 order_item 按 order_id 分组 count，得到"每单商品件数"；
#   - 主查询 LEFT JOIN 该子查询，并用 coalesce(..., 0) 兜底 —— 明细为空的订单
#     也显示 0 件而不是 NULL；
#   - ORDER BY created_at DESC 按时间倒序，offset/limit 完成分页。
# ============================================================
def get_user_orders(user_id: int, page: int = 1, page_size: int = 10) -> Optional[dict]:
    """
    获取用户订单列表
    :param user_id: 用户ID
    :param page: 页码
    :param page_size: 每页大小
    :return: 订单列表字典，失败返回None
    """
    with Session() as session:
        try:
            offset = (page - 1) * page_size

            total = session.query(Order).filter_by(user_id=user_id).count()

            item_count_subquery = session.query(
                OrderItem.order_id,
                func.count(OrderItem.id).label('item_count')
            ).group_by(OrderItem.order_id).subquery()

            orders = session.query(
                Order,
                func.coalesce(item_count_subquery.c.item_count, 0).label('item_count')
            ).outerjoin(
                item_count_subquery,
                Order.id == item_count_subquery.c.order_id
            ).filter(
                Order.user_id == user_id
            ).order_by(
                Order.created_at.desc()
            ).offset(offset).limit(page_size).all()

            order_list = []
            for order, item_count in orders:
                order_list.append({
                    'order_id': order.id,
                    'total_price': order.total_price,
                    'status': order.status,
                    'item_count': item_count,
                    'created_at': order.created_at.isoformat() if order.created_at else None
                })

            return {
                'total': total,
                'page': page,
                'page_size': page_size,
                'orders': order_list
            }
        except Exception as e:
            print(f"获取用户订单列表失败: {e}")
            return None


# ============================================================
# 更新订单状态（带归属校验与状态白名单）
# 作用：推进订单状态机（如用户付款、商家发货、用户确认收货等），把 status
#       更新为新状态。
# 参数：order_id 订单 ID；user_id 用户 ID（归属校验，只能改自己的订单）；
#       status 目标状态。
# 返回：更新后的订单信息 dict；订单不存在/不属于该用户/状态非法/异常返回 None。
# 处理逻辑：
#   - 归属校验 + 状态白名单 {'pending','paid','shipped','completed','cancelled'}，
#     防止任意字符串写入状态列（数据完整性控制）；
#   - 预留"取消待支付订单时回补商品库存"的分支：当前 Product 表尚无 stock 字段，
#     故仅遍历明细不做事（扩展占位，不产生副作用）；
#   - 校验通过后写入新状态并 commit。
# ============================================================
def update_order_status(order_id: int, user_id: int, status: str) -> Optional[dict]:
    """
    更新订单状态
    :param order_id: 订单ID
    :param user_id: 用户ID（用于权限验证）
    :param status: 新状态
    :return: 更新后的订单信息字典，失败返回None
    """
    with Session() as session:
        try:
            # 获取订单并验证归属
            order = session.query(Order).filter_by(id=order_id, user_id=user_id).first()
            if not order:
                print(f"订单不存在或不属于该用户 (订单ID={order_id}, 用户ID={user_id})")
                return None

            # 检查状态转换的合法性
            valid_statuses = ['pending', 'paid', 'shipped', 'completed', 'cancelled']
            if status not in valid_statuses:
                print(f"无效的订单状态: {status}")
                return None

            # 处理特殊状态
            if status == 'cancelled' and order.status == 'pending':
                # 恢复商品库存
                order_items = session.query(OrderItem).filter_by(order_id=order_id).all()
                for item in order_items:
                    product = session.query(Product).filter_by(id=item.product_id).first()
                    if product:
                        # 这里假设Product有stock字段，如果没有则跳过
                        pass

            # 更新状态
            order.status = status
            session.commit()
            print(f"订单状态更新成功 (订单ID={order_id}, 新状态={status})")

            # 返回更新后的订单信息
            return {
                'order_id': order.id,
                'status': order.status,
                'total_price': order.total_price,
                'created_at': order.created_at.isoformat() if order.created_at else None
            }
        except Exception as e:
            session.rollback()
            print(f"更新订单状态失败: {e}")
            return None


# ============================================================
# 取消订单（用户侧）
# 作用：取消自己的一笔订单。
# 参数：order_id 订单 ID；user_id 用户 ID（归属校验）。
# 返回：成功 True；订单不存在/不属于该用户/不是待支付状态/异常返回 False。
# 业务规则：只允许取消 status == 'pending'（待支付）的订单 —— 已进入支付流程
#           的订单不可直接取消，保证订单状态机的合法流转。
# ============================================================
def cancel_order(order_id: int, user_id: int) -> bool:
    """
    取消订单
    :param order_id: 订单ID
    :param user_id: 用户ID
    :return: 取消成功返回True，失败返回False
    """
    with Session() as session:
        try:
            # 获取订单并验证归属
            order = session.query(Order).filter_by(id=order_id, user_id=user_id).first()
            if not order:
                print(f"订单不存在或不属于该用户 (订单ID={order_id}, 用户ID={user_id})")
                return False

            # 检查订单状态
            if order.status != 'pending':
                print(f"只能取消待支付的订单 (订单ID={order_id}, 当前状态={order.status})")
                return False

            # 更新订单状态为已取消
            order.status = 'cancelled'
            session.commit()
            print(f"订单取消成功 (订单ID={order_id})")
            return True
        except Exception as e:
            session.rollback()
            print(f"取消订单失败: {e}")
            return False

