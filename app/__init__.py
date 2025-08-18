"""
Flask应用初始化
"""

import os
import logging
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化数据库
db = SQLAlchemy()

def create_app():
    """
    创建Flask应用实例
    """
    app = Flask(__name__, static_folder='static', static_url_path='')

    # 配置日志
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

    # 配置应用
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:////data/app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['OPENAI_API_BASE_URL'] = os.getenv('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 会话有效期1小时
    
    # 初始化数据库
    db.init_app(app)
    
    # 启用CORS
    CORS(app)
    
    # 创建数据库表和初始化种子数据
    with app.app_context():
        from app.utils.database import init_database, seed_database
        init_database()
        seed_database()
    
    # 注册蓝图
    from app.routes import key_routes, model_routes, chat_routes, stats_routes, auth_routes, health_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(key_routes.bp)
    app.register_blueprint(model_routes.bp)
    app.register_blueprint(chat_routes.bp)
    app.register_blueprint(stats_routes.bp)
    app.register_blueprint(health_routes.bp)
    
    # 注册静态文件路由
    @app.route('/')
    def index():
        from app.utils.auth import login_required
        return login_required(lambda: app.send_static_file('index.html'))()
    
    # 初始化心跳检测服务
    from app.services.heartbeat_service import heartbeat_service
    heartbeat_service.init_app(app)
    
    # 注意：before_first_request 装饰器在 Flask 2.3+ 中已被移除
    # 心跳检测服务现在在 app/main.py 中应用启动时直接初始化
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '页面不存在'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': '服务器内部错误'}), 500
    
    return app