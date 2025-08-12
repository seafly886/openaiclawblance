"""
登录验证路由
"""

from flask import Blueprint, request, jsonify, render_template_string, session, redirect, url_for
from app.utils.auth import check_password

# 创建蓝图
bp = Blueprint('auth_routes', __name__)

# 登录页面HTML模板
LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录验证</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            max-width: 400px;
            width: 100%;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        .login-title {
            text-align: center;
            margin-bottom: 30px;
            color: #343a40;
        }
        .login-logo {
            text-align: center;
            margin-bottom: 20px;
        }
        .login-logo i {
            font-size: 48px;
            color: #0d6efd;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-logo">
            <i class="bi bi-shield-lock"></i>
        </div>
        <h2 class="login-title">OpenAI代理服务</h2>
        <h4 class="text-center mb-4">请输入密码登录</h4>
        
        <div id="login-alert" class="alert alert-danger d-none" role="alert">
            密码错误，请重试
        </div>
        
        <form id="login-form">
            <div class="mb-3">
                <label for="password" class="form-label">密码</label>
                <input type="password" class="form-control" id="password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">登录</button>
        </form>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('login-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const password = document.getElementById('password').value;
            const alertDiv = document.getElementById('login-alert');
            
            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ password: password })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 登录成功，重定向到首页
                    window.location.href = '/';
                } else {
                    // 显示错误消息
                    alertDiv.classList.remove('d-none');
                    // 清空密码输入框
                    document.getElementById('password').value = '';
                }
            })
            .catch(error => {
                console.error('登录请求失败:', error);
                alertDiv.textContent = '登录请求失败，请重试';
                alertDiv.classList.remove('d-none');
            });
        });
    </script>
</body>
</html>
"""

@bp.route('/login')
def login():
    """
    登录页面
    """
    # 如果已经登录，重定向到首页
    if session.get('logged_in'):
        return redirect('/')
    return render_template_string(LOGIN_PAGE_HTML)

@bp.route('/api/login', methods=['POST'])
def api_login():
    """
    登录API
    """
    try:
        data = request.get_json()
        
        if not data or 'password' not in data:
            return jsonify({
                'success': False,
                'message': '缺少密码参数'
            }), 400
        
        password = data['password']
        
        # 验证密码
        if check_password(password):
            # 设置会话
            session['logged_in'] = True
            return jsonify({
                'success': True,
                'message': '登录成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '密码错误'
            }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500

@bp.route('/api/logout', methods=['POST'])
def api_logout():
    """
    登出API
    """
    try:
        # 清除会话
        session.pop('logged_in', None)
        return jsonify({
            'success': True,
            'message': '登出成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登出失败: {str(e)}'
        }), 500