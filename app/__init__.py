"""
Flask应用初始化
"""

import os
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
    
    # 配置应用
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:////data/app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['OPENAI_API_BASE_URL'] = os.getenv('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
    
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
    from app.routes import key_routes, model_routes, chat_routes, stats_routes
    app.register_blueprint(key_routes.bp)
    app.register_blueprint(model_routes.bp)
    app.register_blueprint(chat_routes.bp)
    app.register_blueprint(stats_routes.bp)
    
    # 注册静态文件路由
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    # 健康检查接口
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'OpenAI代理服务运行正常'})
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '页面不存在'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': '服务器内部错误'}), 500
    
    return app