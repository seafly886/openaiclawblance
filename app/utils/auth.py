"""
登录验证工具
"""

from functools import wraps
from flask import session, redirect, url_for, request, jsonify
import os

def login_required(f):
    """
    登录验证装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查会话中是否有登录标志
        if 'logged_in' not in session or not session.get('logged_in'):
            # 如果是API请求，返回JSON错误
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'message': '需要登录才能访问此接口'
                }), 401
            # 否则重定向到登录页面
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def check_password(password):
    """
    检查密码是否正确
    """
    from app.config import Config
    return password == Config.ADMIN_PASSWORD