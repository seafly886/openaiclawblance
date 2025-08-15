#!/usr/bin/env python3
"""
OpenAI代理服务启动文件
"""

import os
import signal
import sys
import logging
from dotenv import load_dotenv
from app import create_app
from app.services.heartbeat_service import heartbeat_service

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
logger = logging.getLogger(__name__)

# 创建Flask应用
app = create_app()

def signal_handler(sig, frame):
    """信号处理函数，用于优雅地关闭应用"""
    logger.info("接收到关闭信号，正在停止心跳检测服务...")
    heartbeat_service.stop()
    logger.info("心跳检测服务已停止")
    sys.exit(0)

# 注册信号处理函数
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    # 获取配置
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    heartbeat_enabled = os.getenv('HEARTBEAT_ENABLED', 'True').lower() == 'true'
    heartbeat_auto_start = os.getenv('HEARTBEAT_AUTO_START', 'True').lower() == 'true'
    
    logger.info(f"启动OpenAI代理服务，监听地址: {host}:{port}")
    logger.info(f"心跳检测功能: {'启用' if heartbeat_enabled else '禁用'}")
    
    # 如果启用了心跳检测且配置为自动启动，则启动心跳检测服务
    if heartbeat_enabled and heartbeat_auto_start:
        logger.info("自动启用心跳检测服务")
        success = heartbeat_service.start()
        if success:
            logger.info("心跳检测服务启动成功")
        else:
            logger.warning("心跳检测服务启动失败")
    
    try:
        # 使用Flask自带的服务器启动应用
        app.run(host=host, port=port, debug=debug, use_reloader=False)
    except KeyboardInterrupt:
        logger.info("接收到键盘中断信号")
    finally:
        # 确保心跳检测服务被停止
        heartbeat_service.stop()
        logger.info("应用已关闭")