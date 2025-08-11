#!/usr/bin/env python3
"""
OpenAI代理服务启动文件
"""

import os
from dotenv import load_dotenv
from app import create_app

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = create_app()

if __name__ == '__main__':
    # 获取配置
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    # 使用Flask自带的服务器启动应用
    app.run(host=host, port=port, debug=debug)