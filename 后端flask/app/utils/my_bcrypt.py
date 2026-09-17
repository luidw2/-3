import bcrypt

# 运行日志改用 logging（而不是 print）：print 直接写进程的 stdout 句柄，
# 一旦后端进程的 stdout 失效（例如控制台被关闭、输出管道被回收），
# print 会抛 OSError: [Errno 22] Invalid argument；而 logging 的 StreamHandler
# 内部会吞掉写入异常（logging.Handler.handleError），不会影响业务返回。
from app.utils.logging_config import get_logger

logger = get_logger(__name__)
# =============================================================================
# 模块说明：用户口令哈希封装（bcrypt，国际通用口令哈希算法）
# -----------------------------------------------------------------------------
# 在项目中的用途（依据后端真实调用点）：
#   - app/api/v1/register.py(约 114 行)：注册时用 bcrypt_password 生成口令哈希入库；
#   - app/utils/db.py(约 296/453 行)：新增用户/修改密码等写库操作同样加密口令；
#   - app/api/v1/login.py(88 行)：登录时用 compare_password 校验用户输入口令；
#   - app/api/v1/update.py、delete.py：改密、注销等场景再次校验当前口令。
# 原理简介（面向讲解）：bcrypt 内部自动生成随机盐并内置工作因子 cost
# (本文件取默认 12，见下方代码注释)，因此同一口令两次哈希结果不同、且难以用
# 彩虹表反查；哈希结果字符串自带盐与 cost 信息，checkpw 校验时自动解析，
# 无需为盐另开存储字段。
# 说明：bcrypt 不属于国密算法，本文件作为项目“口令哈希密码学工具”的一部分，
# 与 SM2/SM3/SM4 等国密模块并列使用、各司其职。
# =============================================================================
#密码加密
def bcrypt_password(password):#对password进行加密，返回可存储的字符串哈希
    # 用户输入的明文口令先按 UTF-8 编码成字节串（bcrypt 接口按字节处理）
    password_bytes = password.encode('utf-8')
    # 生成盐并哈希密码
    # gensalt()：自动生成随机盐并设定 cost 工作因子(行尾注释：默认复杂度为 12)；
    # cost 越大计算越慢，能有效抬高暴力破解的成本
    salt = bcrypt.gensalt()  # 默认复杂度为12
    # hashpw：用上述盐对明文口令做 bcrypt 哈希，结果中已包含盐与 cost 信息
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    # bcrypt 结果为字节串，解码成字符串后即可作为“可存储哈希”入库
    hashed_str = hashed_password.decode('utf-8')
    # 注意：不要把哈希本身写进日志/控制台（口令哈希属敏感数据，日志会被长期保留）
    logger.debug('bcrypt 口令哈希完成（cost 由 gensalt 默认值决定）')
    return hashed_str

#用户输入的密码验证
# —— compare_password：校验“用户本次输入的明文口令”是否与“库中存储的 bcrypt 哈希”匹配
#    入参 stored_hashed_password(str)：数据库中保存的 bcrypt 哈希串
#         input_plain_password(str)：用户输入的明文口令
#    返回 bool：True=口令匹配 / False=不匹配(存储串格式非法等异常也统一归为 False)
#    内部大致步骤：两端 utf-8 编码 → bcrypt.checkpw 比对 → 按结果打印提示并返回；
#                  任何异常落入 except 分支返回 False，保证接口不因脏数据而崩溃
def compare_password(stored_hashed_password,input_plain_password):# 用户输入的明文与数据库中存储的哈希比较
    # 注意（重要修复）：本函数曾在 try 与 except 两个分支里都用 print 输出结果。
    # print 会写入进程的 stdout 句柄，若该句柄已失效（后端进程的控制台被关闭、
    # 输出管道被回收等），print 自身会抛 OSError: [Errno 22] Invalid argument：
    #   1) 成功分支的 print 抛错 → 被下面的 except Exception 吞掉；
    #   2) except 分支紧接着又 print → 再次抛错且无人捕获 → 请求整体 500，
    #      连"密码正确"都会变成登录失败。
    # 因此这里统一改用 logging（写入失败会被 logging 内部吞掉），
    # 保证"口令校验"的结果不再受控制台/输出句柄状态影响。
    try:
        # 库中哈希与用户输入明文分别编码为字节串
        stored_bytes = stored_hashed_password.encode('utf-8')
        input_bytes = input_plain_password.encode('utf-8')
        # checkpw(明文, 哈希)：bcrypt 会自动从哈希串中解析出盐与 cost，重新计算后比对
        if bcrypt.checkpw(input_bytes, stored_bytes):
            logger.debug('口令校验通过')
            return True
        else:
            logger.debug('口令不匹配')
            return False
    except Exception:
        # 哈希串损坏/参数非法时会抛异常，这里统一按“校验失败”处理并返回 False。
        # 用 warning + exc_info 记录真实原因（如库中哈希格式非法），
        # 避免"脏数据"被静默当成密码错误、无从排查。
        logger.warning('口令校验异常（库中哈希可能已损坏或格式非法）', exc_info=True)
        return False

######################