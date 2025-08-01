"""
Key管理服务
"""

import re
from typing import List, Optional, Dict, Any
from app import db
from app.models.key import Key
from app.models.usage_stats import UsageStat

class KeyService:
    """
    Key管理服务类
    """
    
    @staticmethod
    def validate_key_format(key_value: str) -> bool:
        """
        验证Key格式
        """
        # OpenAI API Key格式验证
        pattern = r'^sk-[a-zA-Z0-9]{48}$'
        return re.match(pattern, key_value) is not None
    
    @staticmethod
    def get_all_keys() -> List[Key]:
        """
        获取所有Key
        """
        return Key.query.all()
    
    @staticmethod
    def get_key_by_id(key_id: int) -> Optional[Key]:
        """
        根据ID获取Key
        """
        return Key.query.get(key_id)
    
    @staticmethod
    def get_key_by_value(key_value: str) -> Optional[Key]:
        """
        根据值获取Key
        """
        return Key.query.filter_by(key_value=key_value).first()
    
    @staticmethod
    def get_active_keys() -> List[Key]:
        """
        获取所有活跃的Key
        """
        return Key.query.filter_by(status='active').all()
    
    @staticmethod
    def create_key(key_value: str, name: str = '', status: str = 'active') -> Key:
        """
        创建新Key
        """
        # 验证Key格式
        if not KeyService.validate_key_format(key_value):
            raise ValueError('Invalid OpenAI API Key format')
        
        # 检查Key是否已存在
        existing_key = KeyService.get_key_by_value(key_value)
        if existing_key:
            raise ValueError('Key already exists')
        
        # 创建新Key
        new_key = Key(
            key_value=key_value,
            name=name,
            status=status
        )
        
        db.session.add(new_key)
        db.session.commit()
        
        return new_key
    
    @staticmethod
    def update_key(key_id: int, **kwargs) -> Optional[Key]:
        """
        更新Key信息
        """
        key = KeyService.get_key_by_id(key_id)
        if not key:
            return None
        
        # 更新Key信息
        if 'name' in kwargs:
            key.name = kwargs['name']
        if 'status' in kwargs:
            key.set_status(kwargs['status'])
        
        db.session.commit()
        return key
    
    @staticmethod
    def delete_key(key_id: int) -> bool:
        """
        删除Key
        """
        key = KeyService.get_key_by_id(key_id)
        if not key:
            return False
        
        db.session.delete(key)
        db.session.commit()
        return True
    
    @staticmethod
    def get_key_stats(key_id: int) -> Dict[str, Any]:
        """
        获取Key统计信息
        """
        key = KeyService.get_key_by_id(key_id)
        if not key:
            return {}
        
        # 获取Key的详细统计信息
        stats = {
            'key_info': key.to_dict(),
            'usage_stats': [stat.to_dict() for stat in key.usage_stats],
            'chat_history_count': len(key.chat_history)
        }
        
        return stats
    
    @staticmethod
    def get_next_available_key() -> Optional[Key]:
        """
        获取下一个可用的Key（简单的轮询算法）
        """
        active_keys = KeyService.get_active_keys()
        if not active_keys:
            return None
        
        # 简单的轮询算法：选择使用次数最少的Key
        return min(active_keys, key=lambda k: k.usage_count)
    
    @staticmethod
    def update_key_usage(key_id: int, model: str, tokens_used: int = 0) -> bool:
        """
        更新Key使用统计
        """
        key = KeyService.get_key_by_id(key_id)
        if not key:
            return False
        
        # 更新Key使用统计
        key.update_usage()
        
        # 更新模型使用统计
        # 首先获取模型ID
        from app.models.model import Model
        model_obj = Model.query.filter_by(model_name=model).first()
        model_id = model_obj.id if model_obj else None
        
        usage_stat = UsageStat.get_or_create(key_id, model, model_id)
        usage_stat.update_usage(tokens_used)
        
        return True
    
    @staticmethod
    def set_key_status(key_id: int, status: str) -> bool:
        """
        设置Key状态
        """
        key = KeyService.get_key_by_id(key_id)
        if not key:
            return False
        
        return key.set_status(status)
    
    @staticmethod
    def get_keys_summary() -> Dict[str, Any]:
        """
        获取Keys摘要信息
        """
        total_keys = Key.query.count()
        active_keys = Key.query.filter_by(status='active').count()
        inactive_keys = Key.query.filter_by(status='inactive').count()
        error_keys = Key.query.filter_by(status='error').count()
        total_usage = sum(key.usage_count for key in Key.query.all())
        
        return {
            'total_keys': total_keys,
            'active_keys': active_keys,
            'inactive_keys': inactive_keys,
            'error_keys': error_keys,
            'total_usage': total_usage
        }
    
    @staticmethod
    def test_key(key_id: int) -> Dict[str, Any]:
        """
        测试Key是否有效
        """
        key = KeyService.get_key_by_id(key_id)
        if not key:
            return {'valid': False, 'message': 'Key not found'}
        
        # 使用OpenAI服务测试Key
        from app.services.openai_service import openai_service
        test_result = openai_service.test_key(key)
        
        # 添加Key信息到结果中
        test_result['key_info'] = key.to_dict()
        
        # 更新Key状态
        if test_result['valid']:
            key.set_status('active')
        else:
            key.set_status('error')
        
        return test_result