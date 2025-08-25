#!/usr/bin/env python3
"""
简单的Key轮询测试脚本
"""

import sys
import os

# 模拟Key类
class MockKey:
    def __init__(self, id, name, usage_count=0):
        self.id = id
        self.name = name
        self.usage_count = usage_count
        self.status = 'active'
    
    def __repr__(self):
        return f'<Key {self.id}: {self.name}>'

# 模拟KeyService
class MockKeyService:
    @staticmethod
    def get_active_keys():
        # 模拟从API响应中获取的keys
        return [
            MockKey(1, "01", 23),
            MockKey(2, "02", 3),
            MockKey(3, "03", 1),
            MockKey(4, "04", 0),
            MockKey(5, "05", 0),
            MockKey(6, "06", 0),
            MockKey(7, "07", 0),
            MockKey(8, "08", 0),
            MockKey(9, "09", 0),
            MockKey(10, "10", 0),
            MockKey(11, "11", 0),
            MockKey(12, "12", 0),
            MockKey(13, "13", 0),
        ]

# 简化的KeyRotation类（只包含我们修复的核心逻辑）
class SimpleKeyRotation:
    def __init__(self):
        self._current_index = 0
        self._keys_cache = []
        self._cache_lock = None  # 简化测试，不使用锁
        self._last_refresh_time = 0
        self._cache_ttl = 300  # 缓存有效期5分钟
        
        # 初始化时加载缓存
        self.force_refresh()
    
    def refresh_keys_cache(self):
        """
        刷新Key缓存（修复后的版本）
        """
        import time
        current_time = time.time()
        
        # 只有在缓存过期时才刷新
        if current_time - self._last_refresh_time > self._cache_ttl:
            self._keys_cache = MockKeyService.get_active_keys()
            self._last_refresh_time = current_time
            # 如果当前索引超出范围，重置为0
            if self._current_index >= len(self._keys_cache):
                self._current_index = 0
    
    def get_next_key(self):
        """
        获取下一个可用的Key（轮询算法）
        """
        # 确保缓存已初始化
        if not self._keys_cache:
            self.force_refresh()
        
        if not self._keys_cache:
            return None
        
        # 获取当前Key
        key = self._keys_cache[self._current_index]
        
        # 更新索引，循环使用
        self._current_index = (self._current_index + 1) % len(self._keys_cache)
        
        return key
    
    def get_weighted_round_robin_key(self):
        """
        获取基于使用次数加权的轮询Key
        """
        self.refresh_keys_cache()
        if not self._keys_cache:
            return None
        
        # 计算总使用次数
        total_usage = sum(key.usage_count for key in self._keys_cache)
        
        # 如果所有key都未被使用过，使用普通轮询
        if total_usage == 0:
            key = self._keys_cache[self._current_index]
            self._current_index = (self._current_index + 1) % len(self._keys_cache)
            return key
        
        # 计算权重（使用次数越少，权重越高）
        weights = []
        for key in self._keys_cache:
            # 权重 = 总使用次数 - 当前key使用次数 + 1（确保权重为正）
            weight = total_usage - key.usage_count + 1
            weights.append(weight)
        
        # 根据权重选择key
        import random
        key = random.choices(self._keys_cache, weights=weights)[0]
        return key
    
    def force_refresh(self):
        """
        强制刷新Key缓存并重置轮询索引
        """
        import time
        self._keys_cache = MockKeyService.get_active_keys()
        self._last_refresh_time = time.time()
        self._current_index = 0
    
    def reset_rotation(self):
        """
        重置轮询索引
        """
        self._current_index = 0

def test_key_rotation():
    """测试Key轮询功能"""
    print("=== Key轮询功能测试 ===\n")
    
    # 初始化KeyRotation实例
    key_rotation = SimpleKeyRotation()
    
    # 获取所有活跃的key
    active_keys = MockKeyService.get_active_keys()
    print(f"当前活跃的Key数量: {len(active_keys)}")
    
    # 显示每个key的使用次数
    print("\n当前Key使用情况:")
    for key in active_keys:
        print(f"Key {key.id} ({key.name}): 使用次数 = {key.usage_count}")
    
    # 测试普通轮询算法
    print("\n=== 测试普通轮询算法 (选择20次) ===")
    key_rotation.reset_rotation()  # 重置轮询索引
    key_selection_count_rr = {key.id: 0 for key in active_keys}
    
    for i in range(20):
        selected_key = key_rotation.get_next_key()
        if selected_key:
            key_selection_count_rr[selected_key.id] += 1
            print(f"第{i+1}次选择: Key {selected_key.id} ({selected_key.name})")
    
    # 显示选择结果
    print("\n普通轮询选择结果统计:")
    for key_id, count in key_selection_count_rr.items():
        key = next((k for k in active_keys if k.id == key_id), None)
        if key:
            print(f"Key {key_id} ({key.name}): 被选择 {count} 次")
    
    # 测试加权轮询算法
    print("\n=== 测试加权轮询算法 (选择20次) ===")
    key_selection_count_wr = {key.id: 0 for key in active_keys}
    
    for i in range(20):
        selected_key = key_rotation.get_weighted_round_robin_key()
        if selected_key:
            key_selection_count_wr[selected_key.id] += 1
            print(f"第{i+1}次选择: Key {selected_key.id} ({selected_key.name})")
    
    # 显示选择结果
    print("\n加权轮询选择结果统计:")
    for key_id, count in key_selection_count_wr.items():
        key = next((k for k in active_keys if k.id == key_id), None)
        if key:
            print(f"Key {key_id} ({key.name}): 被选择 {count} 次 (原始使用次数: {key.usage_count})")
    
    # 分析结果
    print("\n=== 结果分析 ===")
    print("普通轮询算法应该均匀分布，每个key被选择的次数应该相近")
    print("加权轮询算法应该优先选择使用次数少的key")
    
    # 找出使用次数最少的key
    min_usage_key = min(active_keys, key=lambda k: k.usage_count)
    print(f"\n使用次数最少的Key: {min_usage_key.id} ({min_usage_key.name}), 使用次数: {min_usage_key.usage_count}")
    print(f"该Key在加权轮询中被选择了 {key_selection_count_wr[min_usage_key.id]} 次")
    
    # 找出使用次数最多的key
    max_usage_key = max(active_keys, key=lambda k: k.usage_count)
    print(f"使用次数最多的Key: {max_usage_key.id} ({max_usage_key.name}), 使用次数: {max_usage_key.usage_count}")
    print(f"该Key在加权轮询中被选择了 {key_selection_count_wr[max_usage_key.id]} 次")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_key_rotation()