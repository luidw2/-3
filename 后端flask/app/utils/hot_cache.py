# -*- coding: utf-8 -*-
"""
hot_cache.py —— 进程内 TTL 缓存（第 8-9 周性能优化）

用途：
    商品列表这类"热点读"接口会被大量重复访问。若每次请求都走
    "JWT 校验 → ORM 查询 → 序列化"，在 20 并发下会因 GIL 争用产生排队。
    本模块提供一个极简的线程安全 TTL 缓存：命中时直接返回已序列化好的
    响应数据，跳过整条数据库查询链路。

说明与限制：
    - 部署形态为单进程时（当前 `python run.py` / waitress 单实例）缓存有效；
      若改为多进程部署，每个进程各有一份缓存，命中率会按进程数下降；
    - 缓存条目带 TTL（默认 5 秒），期间列表数据可能滞后最多 TTL 秒，
      属可接受的一致性代价（商品列表本身不是强一致数据）。
"""
import os
import threading
import time


class TTLCache:
    """极简线程安全 TTL 缓存（dict + 过期时间戳 + 互斥锁）"""

    def __init__(self, ttl: float = 5.0, maxsize: int = 512):
        self.ttl = float(ttl)
        self.maxsize = int(maxsize)
        self._data = {}
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        """命中返回缓存值；未命中/已过期返回 None"""
        now = time.time()
        with self._lock:
            ent = self._data.get(key)
            if ent is not None and ent[0] > now:
                self.hits += 1
                return ent[1]
            if ent is not None:          # 已过期，顺手删除
                self._data.pop(key, None)
            self.misses += 1
            return None

    def set(self, key, value):
        """写入缓存（超出容量时先清理过期项，再淘汰最早写入的一项）"""
        now = time.time()
        with self._lock:
            if len(self._data) >= self.maxsize:
                expired = [k for k, (exp, _) in self._data.items() if exp <= now]
                for k in expired:
                    self._data.pop(k, None)
                if len(self._data) >= self.maxsize:
                    self._data.pop(next(iter(self._data)), None)
            self._data[key] = (now + self.ttl, value)

    def clear(self):
        with self._lock:
            self._data.clear()
            self.hits = 0
            self.misses = 0

    def stats(self) -> dict:
        with self._lock:
            total = self.hits + self.misses
            return {
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': (self.hits / total) if total else 0.0,
                'size': len(self._data),
                'ttl': self.ttl,
            }


# 商品列表热点缓存：TTL 默认 5 秒（压测/部署可通过 PRODUCT_CACHE_TTL 覆盖）
PRODUCT_LIST_CACHE = TTLCache(
    ttl=float(os.getenv('PRODUCT_CACHE_TTL', '5')),
    maxsize=512,
)
