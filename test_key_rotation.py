#!/usr/bin/env python3
"""
测试Key轮询功能的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.key_rotation import KeyRotation
from app.services.key_service import KeyService
from app.models.key import Key
from app import create_app, db

def test_key_rotation():
    """测试Key轮询功能"""
    print("开始测试Key轮询功能...")
    
    # 创建应用上下文
    app = create_app()
    with app.app_context():
        # 初始化KeyRotation实例
        key_rotation = KeyRotation()
        
        # 获取所有活跃的key
        active_keys = KeyService.get_active_keys()
        print(f"当前活跃的Key数量: {len(active_keys)}")
        
        if not active_keys:
            print("没有找到活跃的Key，无法测试轮询功能")
            return
        
        # 显示每个key的使用次数
        print("\n当前Key使用情况:")
        for key in active_keys:
            print(f"Key {key.id} ({key.name}): 使用次数 = {key.usage_count}")
        
        # 测试轮询算法
        print("\n测试加权轮询算法 (选择20次):")
        key_selection_count = {key.id: 0 for key in active_keys}
        
        for i in range(20):
            selected_key = key_rotation.get_key_by_strategy('weighted_round_robin')
            if selected_key:
                key_selection_count[selected_key.id] += 1
                print(f"第{i+1}次选择: Key {selected_key.id} ({selected_key.name})")
        
        # 显示选择结果
        print("\n加权轮询选择结果统计:")
        for key_id, count in key_selection_count.items():
            key = next((k for k in active_keys if k.id == key_id), None)
            if key:
                print(f"Key {key_id} ({key.name}): 被选择 {count} 次 (原始使用次数: {key.usage_count})")
        
        # 测试普通轮询算法
        print("\n测试普通轮询算法 (选择20次):")
        key_rotation.reset_rotation()  # 重置轮询索引
        key_selection_count_rr = {key.id: 0 for key in active_keys}
        
        for i in range(20):
            selected_key = key_rotation.get_key_by_strategy('round_robin')
            if selected_key:
                key_selection_count_rr[selected_key.id] += 1
                print(f"第{i+1}次选择: Key {selected_key.id} ({selected_key.name})")
        
        # 显示选择结果
        print("\n普通轮询选择结果统计:")
        for key_id, count in key_selection_count_rr.items():
            key = next((k for k in active_keys if k.id == key_id), None)
            if key:
                print(f"Key {key_id} ({key.name}): 被选择 {count} 次")
        
        # 测试最少使用算法
        print("\n测试最少使用算法:")
        least_used_key = key_rotation.get_key_by_strategy('least_used')
        if least_used_key:
            print(f"最少使用的Key: Key {least_used_key.id} ({least_used.name}), 使用次数: {least_used_key.usage_count}")
        
        # 测试随机算法
        print("\n测试随机算法 (选择5次):")
        for i in range(5):
            random_key = key_rotation.get_key_by_strategy('random')
            if random_key:
                print(f"第{i+1}次随机选择: Key {random_key.id} ({random_key.name})")
        
        print("\n测试完成!")

def simulate_key_usage():
    """模拟Key使用情况"""
    print("\n模拟Key使用情况...")
    
    app = create_app()
    with app.app_context():
        # 获取所有活跃的key
        active_keys = KeyService.get_active_keys()
        
        if not active_keys:
            print("没有找到活跃的Key")
            return
        
        # 模拟一些key被使用多次
        print("模拟Key使用...")
        for i in range(5):
            # 给第一个key增加使用次数
            if active_keys:
                key = active_keys[0]
                key.update_usage()
                print(f"Key {key.id} 使用次数增加到: {key.usage_count}")
        
        # 显示更新后的使用情况
        print("\n更新后的Key使用情况:")
        for key in active_keys:
            print(f"Key {key.id} ({key.name}): 使用次数 = {key.usage_count}")

if __name__ == "__main__":
    try:
        # 模拟一些使用情况
        simulate_key_usage()
        
        # 测试轮询功能
        test_key_rotation()
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()