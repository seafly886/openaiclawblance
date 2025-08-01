"""
Key轮询工具
"""

import threading
from typing import Optional, List
from app.models.key import Key
from app.services.key_service import KeyService

class KeyRotation:
    """
    Key轮询管理类
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """
        单例模式
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(KeyRotation, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        初始化Key轮询管理器
        """
        if self._initialized:
            return
        
        self._current_index = 0
        self._keys_cache = []
        self._cache_lock = threading.Lock()
        self._initialized = True
    
    def refresh_keys_cache(self):
        """
        刷新Key缓存
        """
        with self._cache_lock:
            self._keys_cache = KeyService.get_active_keys()
            # 如果当前索引超出范围，重置为0
            if self._current_index >= len(self._keys_cache):
                self._current_index = 0
    
    def get_next_key(self) -> Optional[Key]:
        """
        获取下一个可用的Key（轮询算法）
        """
        self.refresh_keys_cache()
        
        if not self._keys_cache:
            return None
        
        with self._cache_lock:
            # 获取当前Key
            key = self._keys_cache[self._current_index]
            
            # 更新索引，循环使用
            self._current_index = (self._current_index + 1) % len(self._keys_cache)
            
            return key
    
    def get_least_used_key(self) -> Optional[Key]:
        """
        获取使用次数最少的Key
        """
        active_keys = KeyService.get_active_keys()
        if not active_keys:
            return None
        
        return min(active_keys, key=lambda k: k.usage_count)
    
    def get_random_key(self) -> Optional[Key]:
        """
        随机获取一个可用的Key
        """
        import random
        active_keys = KeyService.get_active_keys()
        if not active_keys:
            return None
        
        return random.choice(active_keys)
    
    def get_key_by_strategy(self, strategy: str = 'round_robin') -> Optional[Key]:
        """
        根据策略获取Key
        """
        if strategy == 'round_robin':
            return self.get_next_key()
        elif strategy == 'least_used':
            return self.get_least_used_key()
        elif strategy == 'random':
            return self.get_random_key()
        else:
            # 默认使用轮询算法
            return self.get_next_key()
    
    def get_active_keys_count(self) -> int:
        """
        获取活跃Key的数量
        """
        self.refresh_keys_cache()
        return len(self._keys_cache)
    
    def reset_rotation(self):
        """
        重置轮询索引
        """
        with self._cache_lock:
            self._current_index = 0
    
    def force_refresh(self):
        """
        强制刷新Key缓存并重置轮询索引
        """
        with self._cache_lock:
            self.refresh_keys_cache()
            self._current_index = 0

# 全局Key轮询实例
key_rotation = KeyRotation()