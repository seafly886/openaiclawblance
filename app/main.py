#!/usr/bin/env python3
"""
OpenAI代理服务启动文件
"""

import os
from dotenv import load_dotenv
from app import create_app
from a2wsgi import ASGIMiddleware

# 加载环境变量
load_dotenv()

# 创建Flask应用
flask_app = create_app()

# 使用a2wsgi将Flask应用转换为ASGI应用
app = ASGIMiddleware(flask_app)

if __name__ == '__main__':
    # 获取配置
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    # 使用uvicorn启动应用
    import uvicorn
    uvicorn.run("app.main:app", host=host, port=port, reload=debug)