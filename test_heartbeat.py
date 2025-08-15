#!/usr/bin/env python3
"""
心跳检测功能测试脚本
"""

import os
import sys
import time
import requests
import logging
from threading import Thread

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_TIMEOUT = 30  # 测试超时时间（秒）

def test_basic_health_check():
    """测试基础健康检查"""
    logger.info("测试基础健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                logger.info("✓ 基础健康检查测试通过")
                return True
            else:
                logger.error(f"✗ 基础健康检查测试失败: 返回状态为 {data.get('status')}")
                return False
        else:
            logger.error(f"✗ 基础健康检查测试失败: HTTP状态码 {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ 基础健康检查测试失败: {e}")
        return False

def test_detailed_health_check():
    """测试详细健康检查"""
    logger.info("测试详细健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health/detailed", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                logger.info("✓ 详细健康检查测试通过")
                logger.info(f"  监控的服务数量: {data.get('summary', {}).get('total_services', 0)}")
                logger.info(f"  健康的服务数量: {data.get('summary', {}).get('healthy_services', 0)}")
                return True
            else:
                logger.warning(f"⚠ 详细健康检查测试: 返回状态为 {data.get('status')}")
                logger.info(f"  监控的服务数量: {data.get('summary', {}).get('total_services', 0)}")
                logger.info(f"  健康的服务数量: {data.get('summary', {}).get('healthy_services', 0)}")
                return True  # 部分服务不健康是正常的
        else:
            logger.error(f"✗ 详细健康检查测试失败: HTTP状态码 {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ 详细健康检查测试失败: {e}")
        return False

def test_service_health_check():
    """测试特定服务健康检查"""
    logger.info("测试特定服务健康检查...")
    services = ['main_service', 'login_page']
    
    all_passed = True
    for service in services:
        try:
            response = requests.get(f"{BASE_URL}/health/service/{service}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ 服务 {service} 健康检查: {data.get('status', 'unknown')}")
            elif response.status_code == 503:
                logger.warning(f"⚠ 服务 {service} 健康检查: 不健康")
            else:
                logger.error(f"✗ 服务 {service} 健康检查失败: HTTP状态码 {response.status_code}")
                all_passed = False
        except Exception as e:
            logger.error(f"✗ 服务 {service} 健康检查失败: {e}")
            all_passed = False
    
    return all_passed

def test_heartbeat_control():
    """测试心跳检测控制"""
    logger.info("测试心跳检测控制...")
    
    # 测试获取心跳状态
    try:
        response = requests.get(f"{BASE_URL}/admin/heartbeat/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✓ 获取心跳状态成功")
            logger.info(f"  心跳检测启用: {data.get('heartbeat_enabled', False)}")
            logger.info(f"  心跳检测运行中: {data.get('heartbeat_running', False)}")
            logger.info(f"  检查间隔: {data.get('check_interval', 0)}秒")
            logger.info(f"  最大重试次数: {data.get('max_retries', 0)}")
        else:
            logger.error(f"✗ 获取心跳状态失败: HTTP状态码 {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ 获取心跳状态失败: {e}")
        return False
    
    # 测试启动心跳检测
    try:
        response = requests.post(f"{BASE_URL}/admin/heartbeat/start", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.info("✓ 启动心跳检测成功")
            else:
                logger.warning(f"⚠ 启动心跳检测: {data.get('message', 'Unknown error')}")
        else:
            logger.error(f"✗ 启动心跳检测失败: HTTP状态码 {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ 启动心跳检测失败: {e}")
        return False
    
    # 等待一段时间让心跳检测运行
    logger.info("等待心跳检测运行...")
    time.sleep(5)
    
    # 测试停止心跳检测
    try:
        response = requests.post(f"{BASE_URL}/admin/heartbeat/stop", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.info("✓ 停止心跳检测成功")
            else:
                logger.warning(f"⚠ 停止心跳检测: {data.get('message', 'Unknown error')}")
        else:
            logger.error(f"✗ 停止心跳检测失败: HTTP状态码 {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ 停止心跳检测失败: {e}")
        return False
    
    return True

def test_login_page():
    """测试登录页面"""
    logger.info("测试登录页面...")
    try:
        response = requests.get(f"{BASE_URL}/login", timeout=10)
        if response.status_code == 200:
            content = response.text
            required_elements = [
                'OpenAI代理服务',
                '请输入密码登录',
                'password',
                'login-form'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                logger.error(f"✗ 登录页面缺少必要元素: {missing_elements}")
                return False
            else:
                logger.info("✓ 登录页面测试通过")
                return True
        else:
            logger.error(f"✗ 登录页面测试失败: HTTP状态码 {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ 登录页面测试失败: {e}")
        return False


def wait_for_service():
    """等待服务启动"""
    logger.info("等待服务启动...")
    start_time = time.time()
    
    while time.time() - start_time < TEST_TIMEOUT:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                logger.info("服务已启动")
                return True
        except:
            pass
        
        time.sleep(1)
    
    logger.error("等待服务启动超时")
    return False

def run_tests():
    """运行所有测试"""
    logger.info("开始心跳检测功能测试...")
    
    # 等待服务启动
    if not wait_for_service():
        logger.error("服务启动失败，测试终止")
        return False
    
    # 运行测试
    tests = [
        test_basic_health_check,
        test_detailed_health_check,
        test_service_health_check,
        test_heartbeat_control,
        test_login_page
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"测试 {test.__name__} 执行失败: {e}")
            failed += 1
        
        print()  # 空行分隔测试结果
    
    # 输出测试结果摘要
    logger.info("=" * 50)
    logger.info("测试结果摘要:")
    logger.info(f"通过: {passed}")
    logger.info(f"失败: {failed}")
    logger.info(f"总计: {passed + failed}")
    logger.info("=" * 50)
    
    if failed == 0:
        logger.info("🎉 所有测试通过！")
        return True
    else:
        logger.error("❌ 部分测试失败")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)