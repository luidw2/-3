"""
频率限制中间件
功能：防护暴力攻击，限制请求频率
防护威胁：暴力攻击（暴力破解、DDoS等）

保护什么：
- 登录/验证码等接口被脚本高频轮询（撞库、爆破密码）；
- 单个 IP / 单个账号在短时间内刷爆接口，拖垮服务（简易 DoS）。
怎么工作（滑动时间窗口算法 + 多粒度标识，答辩按步骤讲）：
1) 为每个客户端维护一条“时间戳记录”：_rate_limit_store[identifier] 只保留
   当前时间窗口(window_seconds)内的请求时刻；
2) 窗口内请求数达到上限 max_requests 即拒绝放行，返回 429 并告知
   retry_after（还需等待多少秒）；未超限则记录本次请求时间戳并放行；
3) 限流粒度可配置：per_user=True 按登录用户计数（user:id，防账号维度爆破），
   默认 per_ip=True 按客户端 IP 计数（防单 IP 高频刷量）；
4) 并发安全：进程内用 threading.Lock 保证“清理-计数-写入”三步原子执行。

存储说明：默认使用进程内存 + 线程锁，课程设计演示足够；
若部署为多进程/多实例，内存计数互不共享会失效，生产应换成 Redis 等集中式存储。
"""

from functools import wraps
from flask import request, jsonify, g
from datetime import datetime, timedelta
from collections import defaultdict
import time
import threading

# 内存存储（生产环境建议使用Redis）
# 数据结构：identifier(如 "ip:127.0.0.1") -> 该客户端在窗口内的请求时间戳列表
_rate_limit_store = defaultdict(list)
# 进程内互斥锁：保证并发请求下“读计数-判断-写入”不互相覆盖
_lock = threading.Lock()


def _get_client_identifier():
    """
    获取客户端标识符
    优先使用IP地址，如果存在用户ID则使用用户ID

    返回值示例："ip:127.0.0.1" 或 "user:3"
    （供 rate_limit 在“既非纯按用户、也非纯按 IP”的兜底分支使用）
    """
    # 已经过 JWT 认证（g 中有 user_id）时按用户计数，否则退回按客户端 IP 计数
    if hasattr(g, 'user_id'):
        return f"user:{g.user_id}"
    return f"ip:{request.remote_addr}"


def _cleanup_old_entries(identifier: str, window_seconds: int):
    """清理过期的请求记录"""
    # 滑动时间窗口的核心操作：剔除窗口外的旧时间戳
    # （保留条件 = 距今小于窗口长度），既保证计数准确，也防止记录无限增长
    current_time = time.time()
    _rate_limit_store[identifier] = [
        timestamp for timestamp in _rate_limit_store[identifier]
        if current_time - timestamp < window_seconds
    ]


def rate_limit(max_requests: int = 10, window_seconds: int = 60,
               per_user: bool = False, per_ip: bool = True):
    """
    频率限制装饰器
    限制指定时间窗口内的请求次数

    Args:
        max_requests: 最大请求次数
        window_seconds: 时间窗口（秒）
        per_user: 是否按用户限制（需要JWT认证）
        per_ip: 是否按IP限制

    使用方法：
    @user.route('/api', methods=['POST'])
    @rate_limit(max_requests=5, window_seconds=60)
    def api_endpoint():
        ...

    行为与返回码（答辩讲解用）：
    - 窗口内未超限：放行并调用视图函数，同时给响应追加三个限流响应头
      X-RateLimit-Limit / X-RateLimit-Remaining / X-RateLimit-Reset，
      把“限额 / 剩余次数 / 窗口重置时间”告知客户端，便于前端做友好提示；
    - 窗口内已超限：不再调用视图函数，直接返回 429（请求过于频繁），
      响应体 message 提示 retry_after 秒后重试，并携带 retry_after 字段；
    - 按用户限流(per_user=True)时必须先经过 JWT 认证注入 g.user_id；
      若未认证，代码会自动退回按 IP 计数（见 decorated_function 的分支逻辑）。

    与视图/其它装饰器的配合：
    一般把本装饰器与 jwt_auth_required 一起用于登录等敏感接口，
    per_user 维度依赖 g.user_id，故要求 jwt_auth_required 在其外层先执行。
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 确定本次请求要计数的标识（可能同时存在多个维度）
            identifiers = []

            # 根据配置确定限制标识符
            # 优先级说明：per_user 生效的前提是已认证(存在 g.user_id)；
            # 否则退回 per_ip；两者都关闭时用 _get_client_identifier() 自动兜底
            if per_user and hasattr(g, 'user_id'):
                identifiers.append(f"user:{g.user_id}")
            elif per_ip:
                identifiers.append(f"ip:{request.remote_addr}")
            else:
                identifiers.append(_get_client_identifier())

            current_time = time.time()
            blocked = False
            remaining = max_requests

            # 加锁后再做“清理-计数-记录”，保证并发请求下计数操作原子执行
            with _lock:
                for identifier in identifiers:
                    # 清理过期记录
                    _cleanup_old_entries(identifier, window_seconds)

                    # 获取当前时间窗口内的请求次数
                    requests_in_window = len(_rate_limit_store[identifier])

                    if requests_in_window >= max_requests:
                        # 窗口内次数已达上限：标记阻塞，并计算下次可请求的时间
                        blocked = True
                        # 计算下次允许请求的时间
                        # retry_after = 最老记录距离窗口结束还差多少秒（+1 向上取整）
                        oldest_request = min(_rate_limit_store[identifier])
                        retry_after = int(window_seconds - (current_time - oldest_request)) + 1
                        remaining = 0
                        break
                    else:
                        # 记录本次请求
                        # 未超限：把本次请求时间戳追加进记录，并更新剩余次数
                        _rate_limit_store[identifier].append(current_time)
                        remaining = max_requests - requests_in_window - 1

            if blocked:
                # 命中限流：本次请求不放行、也不会计入记录，返回 429 提示稍后重试
                return jsonify({
                    'code': 429,
                    'error': '请求过于频繁',
                    'message': f'请求频率过高，请在 {retry_after} 秒后重试',
                    'time': None,
                    'retry_after': retry_after
                }), 429

            # 放行路径：视图函数已执行完毕，下面把限流信息附加到响应上
            # 添加响应头
            response = f(*args, **kwargs)
            if isinstance(response, tuple):
                response_obj = response[0]
                status_code = response[1] if len(response) > 1 else 200
            else:
                response_obj = response
                status_code = 200

            # 如果是Response对象，添加限流头部
            # X-RateLimit-* 系列头把限额/剩余/重置时间写给客户端，
            # 配合前端倒计时或“剩余次数”展示，也便于监控排查
            if hasattr(response_obj, 'headers'):
                response_obj.headers['X-RateLimit-Limit'] = str(max_requests)
                response_obj.headers['X-RateLimit-Remaining'] = str(remaining)
                response_obj.headers['X-RateLimit-Reset'] = str(int(current_time + window_seconds))

            return response

        return decorated_function

    return decorator


def get_rate_limit_status(identifier: str, max_requests: int, window_seconds: int) -> dict:
    """获取频率限制状态（用于监控和调试）

    作用：对外提供某个 identifier 当前的计数快照（已请求次数/剩余次数/窗口等），
    供管理/监控接口查询限流策略是否生效，不影响实际限流逻辑。
    """
    with _lock:
        _cleanup_old_entries(identifier, window_seconds)
        requests_count = len(_rate_limit_store[identifier])
        return {
            'identifier': identifier,
            'requests': requests_count,
            'limit': max_requests,
            'remaining': max(0, max_requests - requests_count),
            'window_seconds': window_seconds
        }
