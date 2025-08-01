"""
数据库连接和初始化工具
"""

import os
import json
from datetime import datetime
from app import db
from app.models.key import Key
from app.models.usage_stats import UsageStat
from app.models.model import Model
from app.models.chat_history import ChatHistory

def init_database():
    """
    初始化数据库，创建所有表
    """
    try:
        db.create_all()
        print("数据库表创建成功")
        return True
    except Exception as e:
        print(f"数据库表创建失败: {e}")
        return False

def seed_database():
    """
    初始化数据库种子数据
    """
    try:
        # 检查是否已有数据
        if Model.query.count() > 0:
            print("数据库已有数据，跳过种子数据初始化")
            return True
        
        # 初始化一些常见的OpenAI模型
        models_data = [
            {
                "model_name": "gpt-3.5-turbo",
                "description": "GPT-3.5 Turbo模型，适用于大多数对话任务",
                "capabilities": json.dumps({
                    "max_tokens": 4096,
                    "supports_chat": True,
                    "supports_completion": False
                })
            },
            {
                "model_name": "gpt-4",
                "description": "GPT-4模型，更强大的对话能力",
                "capabilities": json.dumps({
                    "max_tokens": 8192,
                    "supports_chat": True,
                    "supports_completion": False
                })
            },
            {
                "model_name": "gpt-4-32k",
                "description": "GPT-4 32K模型，支持更长上下文",
                "capabilities": json.dumps({
                    "max_tokens": 32768,
                    "supports_chat": True,
                    "supports_completion": False
                })
            },
            {
                "model_name": "text-davinci-003",
                "description": "Text Davinci 003模型，适用于文本生成任务",
                "capabilities": json.dumps({
                    "max_tokens": 4097,
                    "supports_chat": False,
                    "supports_completion": True
                })
            }
        ]
        
        for model_data in models_data:
            model = Model(
                model_name=model_data["model_name"],
                description=model_data["description"],
                capabilities=model_data["capabilities"]
            )
            db.session.add(model)
        
        db.session.commit()
        print("数据库种子数据初始化成功")
        return True
    except Exception as e:
        print(f"数据库种子数据初始化失败: {e}")
        db.session.rollback()
        return False

def get_database_info():
    """
    获取数据库信息
    """
    try:
        info = {
            "keys_count": Key.query.count(),
            "models_count": Model.query.count(),
            "usage_stats_count": UsageStat.query.count(),
            "chat_history_count": ChatHistory.query.count(),
            "active_keys_count": Key.query.filter_by(status='active').count(),
            "total_usage_count": sum(key.usage_count for key in Key.query.all())
        }
        return info
    except Exception as e:
        print(f"获取数据库信息失败: {e}")
        return None

def cleanup_old_records(days=30):
    """
    清理旧记录
    """
    try:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 清理旧的聊天历史记录
        old_chat_history = ChatHistory.query.filter(ChatHistory.timestamp < cutoff_date).all()
        for record in old_chat_history:
            db.session.delete(record)
        
        db.session.commit()
        print(f"清理了 {len(old_chat_history)} 条旧记录")
        return True
    except Exception as e:
        print(f"清理旧记录失败: {e}")
        db.session.rollback()
        return False