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
flask_app = create_app()

# WSGI到ASGI的适配器
class WSGI2ASGI:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await send({"type": "http.response.start", "status": 404})
            await send({"type": "http.response.body", "body": b"Not Found"})
            return
        
        # 将ASGI调用转换为WSGI调用
        body = b""
        more_body = True
        
        while more_body:
            message = await receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
                more_body = message.get("more_body", False)
        
        # 模拟WSGI环境
        environ = {
            "REQUEST_METHOD": scope["method"],
            "PATH_INFO": scope["path"],
            "QUERY_STRING": scope["query_string"].decode(),
            "SERVER_NAME": scope["server"][0],
            "SERVER_PORT": str(scope["server"][1]),
            "SERVER_PROTOCOL": "HTTP/1.1",
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": scope["scheme"],
            "wsgi.input": type("", (), {"read": lambda: body})(),
            "wsgi.errors": None,
            "wsgi.multithread": True,
            "wsgi.multiprocess": False,
            "wsgi.run_once": False,
        }
        
        # 添加HTTP头
        for name, value in scope["headers"]:
            key = name.decode().upper().replace("-", "_")
            if key not in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                key = f"HTTP_{key}"
            environ[key] = value.decode()
        
        # 收集响应
        response_status = ""
        response_headers = []
        
        def start_response(status, headers, exc_info=None):
            nonlocal response_status, response_headers
            response_status = status
            response_headers = headers
        
        # 调用WSGI应用
        result = self.wsgi_app(environ, start_response)
        
        # 发送响应头
        status_code = int(response_status.split()[0])
        headers = [(name.encode(), value.encode()) for name, value in response_headers]
        await send({"type": "http.response.start", "status": status_code, "headers": headers})
        
        # 发送响应体
        for chunk in result:
            if chunk:
                await send({"type": "http.response.body", "body": chunk})
        
        if hasattr(result, "close"):
            result.close()
        
        await send({"type": "http.response.body", "body": b""})

# 创建ASGI应用
app = WSGI2ASGI(flask_app)

if __name__ == '__main__':
    # 获取配置
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    # 使用uvicorn启动应用
    import uvicorn
    uvicorn.run("app.main:app", host=host, port=port, reload=debug)