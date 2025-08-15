"""
应用配置
"""

import os
from datetime import timedelta

class Config:
    """
    基础配置类
    """
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:////data/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI API配置
    OPENAI_API_BASE_URL = os.getenv('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
    
    # 应用配置
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Key轮询配置
    KEY_ROTATION_INTERVAL = 1  # 每次请求轮询一次
    
    # 统计配置
    STATS_CACHE_TIMEOUT = 300  # 统计数据缓存时间（秒）
    
    # 聊天配置
    CHAT_MAX_HISTORY = 100  # 最大聊天历史记录数
    CHAT_TIMEOUT = 30  # 聊天请求超时时间（秒）
    
    # 登录验证配置
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWD', 'ts-123456')  # 管理员密码，默认为 ts-123456
    
    # 心跳检测配置
    HEARTBEAT_ENABLED = os.getenv('HEARTBEAT_ENABLED', 'True').lower() == 'true'  # 是否启用心跳检测
    HEARTBEAT_CHECK_INTERVAL = int(os.getenv('HEARTBEAT_CHECK_INTERVAL', '300'))  # 心跳检测间隔（秒）
    HEARTBEAT_MAX_RETRIES = int(os.getenv('HEARTBEAT_MAX_RETRIES', '3'))  # 最大重试次数
    HEARTBEAT_RESTART_COOLDOWN = int(os.getenv('HEARTBEAT_RESTART_COOLDOWN', '300'))  # 重启冷却时间（秒）
    HEARTBEAT_AUTO_START = os.getenv('HEARTBEAT_AUTO_START', 'True').lower() == 'true'  # 是否自动启动心跳检测

class DevelopmentConfig(Config):
    """
    开发环境配置
    """
    DEBUG = True

class ProductionConfig(Config):
    """
    生产环境配置
    """
    DEBUG = False

class TestingConfig(Config):
    """
    测试环境配置
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}