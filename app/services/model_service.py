"""
模型管理服务
"""

import json
from typing import List, Optional, Dict, Any
from app import db
from app.models.model import Model
from app.models.usage_stats import UsageStat
from app.models.chat_history import ChatHistory
from app.services.openai_service import openai_service

class ModelService:
    """
    模型管理服务类
    """
    
    @staticmethod
    def get_all_models() -> List[Model]:
        """
        获取所有模型
        """
        return Model.query.all()
    
    @staticmethod
    def get_model_by_name(model_name: str) -> Optional[Model]:
        """
        根据名称获取模型
        """
        return Model.query.filter_by(model_name=model_name).first()
    
    @staticmethod
    def get_model_by_id(model_id: int) -> Optional[Model]:
        """
        根据ID获取模型
        """
        return Model.query.get(model_id)
    
    @staticmethod
    def create_model(model_name: str, description: str = '', capabilities: str = '') -> Model:
        """
        创建新模型
        """
        # 检查模型是否已存在
        existing_model = ModelService.get_model_by_name(model_name)
        if existing_model:
            raise ValueError('模型已存在')
        
        # 创建新模型
        new_model = Model(
            model_name=model_name,
            description=description,
            capabilities=capabilities
        )
        
        db.session.add(new_model)
        db.session.commit()
        
        return new_model
    
    @staticmethod
    def update_model(model_name: str, description: str = None, capabilities: str = None) -> Optional[Model]:
        """
        更新模型信息
        """
        model = ModelService.get_model_by_name(model_name)
        if not model:
            return None
        
        # 更新模型信息
        if description is not None:
            model.description = description
        if capabilities is not None:
            model.capabilities = capabilities
        
        db.session.commit()
        return model
    
    @staticmethod
    def delete_model(model_name: str) -> bool:
        """
        删除模型
        """
        model = ModelService.get_model_by_name(model_name)
        if not model:
            return False
        
        db.session.delete(model)
        db.session.commit()
        return True
    
    @staticmethod
    def get_model_stats(model_name: str) -> Dict[str, Any]:
        """
        获取模型统计信息
        """
        model = ModelService.get_model_by_name(model_name)
        if not model:
            return {}
        
        # 获取模型的详细统计信息
        stats = {
            'model_info': model.to_dict(),
            'usage_stats': [stat.to_dict() for stat in model.usage_stats],
            'chat_history_count': len(model.chat_history)
        }
        
        return stats
    
    @staticmethod
    def refresh_models() -> List[Model]:
        """
        从OpenAI API刷新模型列表
        """
        try:
            # 从OpenAI API获取最新模型列表
            openai_models = openai_service.get_models()
            
            # 更新数据库中的模型信息
            updated_models = []
            for model_data in openai_models.get('data', []):
                model_name = model_data.get('id')
                if model_name:
                    # 获取或创建模型记录
                    model = Model.get_or_create(
                        model_name=model_name,
                        description=f"OpenAI {model_name} 模型",
                        capabilities=json.dumps({
                            'owned_by': model_data.get('owned_by'),
                            'created': model_data.get('created'),
                            'permission': model_data.get('permission', []),
                            'supports_chat': True,  # 默认支持聊天
                            'supports_completion': True  # 默认支持文本完成
                        })
                    )
                    updated_models.append(model)
            
            return updated_models
        except Exception as e:
            raise Exception(f"刷新模型列表失败: {str(e)}")
    
    @staticmethod
    def get_models_summary() -> Dict[str, Any]:
        """
        获取模型摘要信息
        """
        try:
            total_models = Model.query.count()
            
            # 获取每个模型的使用次数
            model_usage = db.session.query(
                Model.model_name,
                db.func.sum(UsageStat.usage_count).label('total_usage'),
                db.func.sum(UsageStat.total_tokens).label('total_tokens')
            ).join(
                UsageStat, Model.model_name == UsageStat.model
            ).group_by(
                Model.model_name
            ).all()
            
            # 获取最常用的模型
            most_used_model = max(model_usage, key=lambda m: m.total_usage or 0) if model_usage else None
            
            # 获取总使用次数
            total_usage = sum(m.total_usage or 0 for m in model_usage)
            
            # 获取总token使用量
            total_tokens = sum(m.total_tokens or 0 for m in model_usage)
            
            return {
                'total_models': total_models,
                'model_usage': [
                    {
                        'model_name': item.model_name,
                        'total_usage': item.total_usage or 0,
                        'total_tokens': item.total_tokens or 0
                    } for item in model_usage
                ],
                'most_used_model': most_used_model.model_name if most_used_model else None,
                'total_usage': total_usage,
                'total_tokens': total_tokens
            }
        except Exception as e:
            raise Exception(f"获取模型摘要失败: {str(e)}")
    
    @staticmethod
    def get_model_capabilities(model_name: str) -> Dict[str, Any]:
        """
        获取模型能力信息
        """
        model = ModelService.get_model_by_name(model_name)
        if not model or not model.capabilities:
            return {}
        
        try:
            return json.loads(model.capabilities)
        except json.JSONDecodeError:
            return {}
    
    @staticmethod
    def is_model_available(model_name: str) -> bool:
        """
        检查模型是否可用
        """
        model = ModelService.get_model_by_name(model_name)
        return model is not None
    
    @staticmethod
    def get_chat_models() -> List[Model]:
        """
        获取支持聊天的模型列表
        """
        chat_models = []
        all_models = ModelService.get_all_models()
        
        for model in all_models:
            capabilities = ModelService.get_model_capabilities(model.model_name)
            if capabilities.get('supports_chat', False):
                chat_models.append(model)
        
        return chat_models
    
    @staticmethod
    def get_completion_models() -> List[Model]:
        """
        获取支持文本完成的模型列表
        """
        completion_models = []
        all_models = ModelService.get_all_models()
        
        for model in all_models:
            capabilities = ModelService.get_model_capabilities(model.model_name)
            if capabilities.get('supports_completion', False):
                completion_models.append(model)
        
        return completion_models

# 全局模型服务实例
model_service = ModelService()