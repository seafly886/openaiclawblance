"""
心跳检测服务模块
"""

import os
import time
import threading
import logging
import requests
import subprocess
import signal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from flask import current_app
from app import db

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
logger = logging.getLogger(__name__)

class HeartbeatService:
    """心跳检测服务类"""
    
    def __init__(self, app=None):
        """
        初始化心跳检测服务
        
        Args:
            app: Flask应用实例
        """
        self.app = app
        self.is_running = False
        self.heartbeat_thread = None
        self.failure_count = {}
        self.last_failure_time = {}
        
        # 从配置或环境变量中获取参数
        if app:
            self.max_retries = app.config.get('HEARTBEAT_MAX_RETRIES', 3)
            self.check_interval = app.config.get('HEARTBEAT_CHECK_INTERVAL', 30)
            self.restart_cooldown = app.config.get('HEARTBEAT_RESTART_COOLDOWN', 300)
            self.enabled = app.config.get('HEARTBEAT_ENABLED', True)
            self.auto_start = app.config.get('HEARTBEAT_AUTO_START', True)
        else:
            self.max_retries = int(os.getenv('HEARTBEAT_MAX_RETRIES', '3'))
            self.check_interval = int(os.getenv('HEARTBEAT_CHECK_INTERVAL', '30'))
            self.restart_cooldown = int(os.getenv('HEARTBEAT_RESTART_COOLDOWN', '300'))
            self.enabled = os.getenv('HEARTBEAT_ENABLED', 'True').lower() == 'true'
            self.auto_start = os.getenv('HEARTBEAT_AUTO_START', 'True').lower() == 'true'
        
        # 需要监控的服务和端点
        self.monitored_services = {
            'main_service': {
                'url': 'http://localhost:{port}/health',
                'description': '主服务健康检查',
                'critical': True
            },
            'login_page': {
                'url': 'http://localhost:{port}/login',
                'description': '管理登录页面',
                'critical': True
            }
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """
        初始化Flask应用
        
        Args:
            app: Flask应用实例
        """
        self.app = app
        port = app.config.get('PORT', 5000)
        
        # 更新URL中的端口
        for service in self.monitored_services.values():
            service['url'] = service['url'].format(port=port)
    
    def start(self):
        """启动心跳检测服务"""
        if not self.enabled:
            logger.info("心跳检测服务已禁用")
            return False
            
        if self.is_running:
            logger.warning("心跳检测服务已经在运行中")
            return False
        
        self.is_running = True
        self.heartbeat_thread = threading.Thread(target=self._run_heartbeat_checks, daemon=True)
        self.heartbeat_thread.start()
        logger.info("心跳检测服务已启动")
        return True
    
    def stop(self):
        """停止心跳检测服务"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        logger.info("心跳检测服务已停止")
    
    def _run_heartbeat_checks(self):
        """运行心跳检查的主循环"""
        while self.is_running:
            try:
                self._check_all_services()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"心跳检查过程中发生错误: {e}")
                time.sleep(self.check_interval)
    
    def _check_all_services(self):
        """检查所有监控的服务"""
        logger.debug("开始执行心跳检查")
        
        for service_name, service_info in self.monitored_services.items():
            try:
                is_healthy, response_time = self._check_service_health(service_info['url'])
                
                if is_healthy:
                    # 服务正常，重置失败计数
                    if service_name in self.failure_count:
                        logger.info(f"{service_info['description']} 已恢复正常")
                        del self.failure_count[service_name]
                    if service_name in self.last_failure_time:
                        del self.last_failure_time[service_name]
                else:
                    # 服务异常，增加失败计数
                    self.failure_count[service_name] = self.failure_count.get(service_name, 0) + 1
                    self.last_failure_time[service_name] = datetime.now()
                    
                    logger.warning(
                        f"{service_info['description']} 检查失败，"
                        f"失败次数: {self.failure_count[service_name]}/{self.max_retries}"
                    )
                    
                    # 如果达到最大重试次数且服务是关键的，尝试修复
                    if (self.failure_count[service_name] >= self.max_retries and 
                        service_info['critical']):
                        self._attempt_repair(service_name, service_info)
                        
            except Exception as e:
                logger.error(f"检查服务 {service_name} 时发生错误: {e}")
    
    def _check_service_health(self, url: str, timeout: int = 10) -> Tuple[bool, float]:
        """
        检查单个服务的健康状态
        
        Args:
            url: 服务URL
            timeout: 超时时间（秒）
            
        Returns:
            Tuple[bool, float]: (是否健康, 响应时间)
        """
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            response_time = time.time() - start_time
            
            # 检查HTTP状态码
            if response.status_code == 200:
                # 对于健康检查端点，验证响应内容
                if '/health' in url:
                    try:
                        data = response.json()
                        if data.get('status') == 'healthy':
                            return True, response_time
                        else:
                            logger.warning(f"健康检查端点返回非健康状态: {data}")
                            return False, response_time
                    except ValueError:
                        logger.warning("健康检查端点返回无效的JSON")
                        return False, response_time
                # 对于登录页面，检查页面内容
                elif '/login' in url:
                    return self._check_login_page_content(response, response_time)
                # 对于API端点，检查响应格式
                elif '/api/' in url or '/v1/' in url:
                    return self._check_api_response(response, response_time)
                else:
                    # 其他端点只要返回200就认为健康
                    return True, response_time
            else:
                logger.warning(f"服务返回非200状态码: {response.status_code}")
                return False, response_time
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"请求服务失败: {e}")
            return False, 0.0
    
    def _check_login_page_content(self, response, response_time: float) -> Tuple[bool, float]:
        """
        检查登录页面内容是否正确
        
        Args:
            response: HTTP响应对象
            response_time: 响应时间
            
        Returns:
            Tuple[bool, float]: (是否健康, 响应时间)
        """
        try:
            # 检查响应内容类型
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type:
                logger.warning("登录页面返回非HTML内容")
                return False, response_time
            
            # 检查页面内容
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
                logger.warning(f"登录页面缺少必要元素: {missing_elements}")
                return False, response_time
            
            return True, response_time
            
        except Exception as e:
            logger.error(f"检查登录页面内容时发生错误: {e}")
            return False, response_time
    
    def _check_api_response(self, response, response_time: float) -> Tuple[bool, float]:
        """
        检查API响应是否正确
        
        Args:
            response: HTTP响应对象
            response_time: 响应时间
            
        Returns:
            Tuple[bool, float]: (是否健康, 响应时间)
        """
        try:
            # 检查响应内容类型
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                logger.warning("API端点返回非JSON内容")
                return False, response_time
            
            # 尝试解析JSON
            try:
                data = response.json()
                
                # 检查是否是错误响应
                if 'error' in data:
                    logger.warning(f"API端点返回错误: {data['error']}")
                    return False, response_time
                
                # 检查是否是成功响应
                if 'success' in data and not data['success']:
                    logger.warning(f"API端点返回失败状态: {data.get('message', 'Unknown error')}")
                    return False, response_time
                
                return True, response_time
                
            except ValueError:
                logger.warning("API端点返回无效的JSON")
                return False, response_time
                
        except Exception as e:
            logger.error(f"检查API响应时发生错误: {e}")
            return False, response_time
    
    def _attempt_repair(self, service_name: str, service_info: Dict):
        """
        尝试修复服务
        
        Args:
            service_name: 服务名称
            service_info: 服务信息
        """
        logger.warning(f"尝试修复服务: {service_info['description']}")
        
        # 检查是否在冷却时间内
        if service_name in self.last_failure_time:
            time_since_last_failure = datetime.now() - self.last_failure_time[service_name]
            if time_since_last_failure.total_seconds() < self.restart_cooldown:
                logger.info(
                    f"服务 {service_name} 在冷却时间内，"
                    f"剩余冷却时间: {self.restart_cooldown - time_since_last_failure.total_seconds():.1f}秒"
                )
                return
        
        # 根据不同的服务类型采取不同的修复策略
        if service_name == 'main_service':
            self._repair_main_service()
        elif service_name == 'login_page':
            self._repair_login_service()
        else:
            # 默认修复策略
            self._default_repair_strategy(service_name, service_info)
    
    def _repair_main_service(self):
        """修复主服务"""
        logger.error("主服务健康检查失败，开始修复流程")
        
        # 首先检查数据库连接
        if not self._check_database_connection():
            logger.error("数据库连接失败，尝试重启服务")
            self._restart_service("数据库连接失败")
            return
        
        # 检查应用配置
        if not self._check_app_configuration():
            logger.error("应用配置检查失败，尝试重启服务")
            self._restart_service("应用配置检查失败")
            return
        
        # 如果以上检查都通过，但服务仍然不健康，则重启服务
        logger.error("主服务仍然不健康，尝试重启服务")
        self._restart_service("主服务健康检查失败")
    
    def _repair_login_service(self):
        """修复登录服务"""
        logger.error("登录页面不可用，开始修复流程")
        
        # 检查认证配置
        if not self._check_auth_configuration():
            logger.error("认证配置检查失败，尝试重启服务")
            self._restart_service("认证配置检查失败")
            return
        
        # 检查会话配置
        if not self._check_session_configuration():
            logger.error("会话配置检查失败，尝试重启服务")
            self._restart_service("会话配置检查失败")
            return
        
        # 如果以上检查都通过，但登录页面仍然不可用，则重启服务
        logger.error("登录页面仍然不可用，尝试重启服务")
        self._restart_service("登录页面不可用")
    
    
    def _default_repair_strategy(self, service_name: str, service_info: Dict):
        """默认修复策略"""
        logger.warning(f"使用默认修复策略处理服务: {service_name}")
        
        # 检查数据库连接
        if not self._check_database_connection():
            logger.error("数据库连接失败，尝试重启服务")
            self._restart_service("数据库连接失败")
            return
        
        # 默认情况下，重启服务
        self._restart_service(f"服务 {service_name} 不可用")
    
    def _check_app_configuration(self) -> bool:
        """检查应用配置"""
        try:
            with self.app.app_context():
                # 检查基本配置
                required_configs = [
                    'SECRET_KEY',
                    'SQLALCHEMY_DATABASE_URI',
                    'OPENAI_API_BASE_URL'
                ]
                
                for config_key in required_configs:
                    if not self.app.config.get(config_key):
                        logger.error(f"缺少必要配置: {config_key}")
                        return False
                
                return True
        except Exception as e:
            logger.error(f"检查应用配置时发生错误: {e}")
            return False
    
    def _check_auth_configuration(self) -> bool:
        """检查认证配置"""
        try:
            with self.app.app_context():
                # 检查管理员密码配置
                admin_password = self.app.config.get('ADMIN_PASSWORD')
                if not admin_password:
                    logger.error("缺少管理员密码配置")
                    return False
                
                # 检查会话配置
                session_lifetime = self.app.config.get('PERMANENT_SESSION_LIFETIME')
                if not session_lifetime:
                    logger.error("缺少会话有效期配置")
                    return False
                
                return True
        except Exception as e:
            logger.error(f"检查认证配置时发生错误: {e}")
            return False
    
    def _check_session_configuration(self) -> bool:
        """检查会话配置"""
        try:
            with self.app.app_context():
                # 检查会话密钥
                secret_key = self.app.config.get('SECRET_KEY')
                if not secret_key or secret_key == 'dev-secret-key':
                    logger.warning("使用默认会话密钥，存在安全风险")
                
                return True
        except Exception as e:
            logger.error(f"检查会话配置时发生错误: {e}")
            return False
    
    
    def _check_database_connection(self) -> bool:
        """
        检查数据库连接
        
        Returns:
            bool: 数据库是否连接正常
        """
        try:
            with self.app.app_context():
                # 执行简单的SQL查询测试数据库连接
                db.session.execute('SELECT 1')
                return True
        except Exception as e:
            logger.error(f"数据库连接检查失败: {e}")
            return False
    
    def _restart_service(self, reason: str):
        """
        重启服务
        
        Args:
            reason: 重启原因
        """
        try:
            logger.error(f"因 {reason} 准备重启服务")
            
            # 记录重启事件
            self._log_restart_event(reason)
            
            # 获取当前进程ID
            pid = os.getpid()
            
            # 在新线程中执行重启，避免阻塞当前线程
            def restart_in_thread():
                try:
                    # 给当前进程发送SIGTERM信号，优雅地关闭
                    if os.name == 'nt':  # Windows
                        # Windows下使用taskkill命令
                        subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
                    else:  # Unix/Linux
                        os.kill(pid, signal.SIGTERM)
                    
                    logger.info("服务重启信号已发送")
                except Exception as e:
                    logger.error(f"重启服务时发生错误: {e}")
            
            restart_thread = threading.Thread(target=restart_in_thread, daemon=True)
            restart_thread.start()
            
        except Exception as e:
            logger.error(f"重启服务时发生错误: {e}")
    
    def _log_restart_event(self, reason: str):
        """
        记录重启事件
        
        Args:
            reason: 重启原因
        """
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event': 'service_restart',
                'reason': reason,
                'failure_count': dict(self.failure_count),
                'pid': os.getpid()
            }
            
            # 记录到日志文件
            logger.error(f"服务重启事件: {log_entry}")
            
            # 如果可以，也记录到数据库
            try:
                with self.app.app_context():
                    from app.models.usage_stats import UsageStat
                    # 创建一个特殊的统计记录来标记重启事件
                    restart_stat = UsageStat(
                        stat_type='service_restart',
                        stat_value=1,
                        stat_date=datetime.now().date(),
                        additional_info=str(log_entry)
                    )
                    db.session.add(restart_stat)
                    db.session.commit()
            except Exception as e:
                logger.error(f"记录重启事件到数据库失败: {e}")
                
        except Exception as e:
            logger.error(f"记录重启事件时发生错误: {e}")
    
    def get_service_status(self) -> Dict:
        """
        获取所有服务的状态
        
        Returns:
            Dict: 服务状态信息
        """
        status = {}
        
        for service_name, service_info in self.monitored_services.items():
            is_healthy, response_time = self._check_service_health(service_info['url'])
            status[service_name] = {
                'description': service_info['description'],
                'healthy': is_healthy,
                'response_time': response_time,
                'critical': service_info['critical'],
                'failure_count': self.failure_count.get(service_name, 0),
                'last_failure': self.last_failure_time.get(service_name).isoformat() if service_name in self.last_failure_time else None
            }
        
        return status

# 创建全局心跳检测服务实例
heartbeat_service = HeartbeatService()