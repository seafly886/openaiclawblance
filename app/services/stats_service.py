"""
统计服务
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models.key import Key
from app.models.model import Model
from app.models.usage_stats import UsageStat
from app.models.chat_history import ChatHistory

class StatsService:
    """
    统计服务类
    """
    
    @staticmethod
    def get_database_info() -> Dict[str, Any]:
        """
        获取数据库基本信息
        """
        try:
            info = {
                'keys_count': Key.query.count(),
                'models_count': Model.query.count(),
                'usage_stats_count': UsageStat.query.count(),
                'chat_history_count': ChatHistory.query.count(),
                'active_keys_count': Key.query.filter_by(status='active').count(),
                'total_usage_count': sum(key.usage_count for key in Key.query.all())
            }
            return info
        except Exception as e:
            raise Exception(f"获取数据库信息失败: {str(e)}")
    
    @staticmethod
    def get_overview_stats() -> Dict[str, Any]:
        """
        获取系统概览统计
        """
        try:
            # 获取数据库基本信息
            db_info = StatsService.get_database_info()
            
            # 获取每个模型的使用次数
            model_usage = db.session.query(
                Model.model_name,
                func.sum(UsageStat.usage_count).label('total_usage'),
                func.sum(UsageStat.total_tokens).label('total_tokens')
            ).join(
                UsageStat, Model.model_name == UsageStat.model
            ).group_by(
                Model.model_name
            ).all()
            
            # 获取每个Key的使用次数
            key_usage = db.session.query(
                Key.id,
                Key.name,
                Key.status,
                Key.usage_count,
                Key.last_used
            ).all()
            
            # 获取最近的聊天记录
            recent_chats = ChatHistory.query.order_by(ChatHistory.timestamp.desc()).limit(10).all()
            
            # 获取过去24小时的使用统计
            yesterday = datetime.utcnow() - timedelta(days=1)
            daily_usage = db.session.query(
                func.count(ChatHistory.id).label('request_count'),
                func.sum(ChatHistory.tokens_used).label('tokens_used')
            ).filter(
                ChatHistory.timestamp >= yesterday
            ).first()
            
            # 获取过去7天的使用统计
            week_ago = datetime.utcnow() - timedelta(days=7)
            weekly_usage = db.session.query(
                func.count(ChatHistory.id).label('request_count'),
                func.sum(ChatHistory.tokens_used).label('tokens_used')
            ).filter(
                ChatHistory.timestamp >= week_ago
            ).first()
            
            return {
                'database_info': db_info,
                'model_usage': [
                    {
                        'model_name': item.model_name,
                        'total_usage': item.total_usage or 0,
                        'total_tokens': item.total_tokens or 0
                    } for item in model_usage
                ],
                'key_usage': [
                    {
                        'id': item.id,
                        'name': item.name,
                        'status': item.status,
                        'usage_count': item.usage_count,
                        'last_used': item.last_used.isoformat() if item.last_used else None
                    } for item in key_usage
                ],
                'recent_chats': [chat.to_dict() for chat in recent_chats],
                'daily_usage': {
                    'request_count': daily_usage.request_count or 0,
                    'tokens_used': daily_usage.tokens_used or 0
                },
                'weekly_usage': {
                    'request_count': weekly_usage.request_count or 0,
                    'tokens_used': weekly_usage.tokens_used or 0
                }
            }
        except Exception as e:
            raise Exception(f"获取系统概览统计失败: {str(e)}")
    
    @staticmethod
    def get_usage_stats(period: str = 'all') -> Dict[str, Any]:
        """
        获取使用统计
        """
        try:
            # 获取总体使用统计
            total_usage = db.session.query(
                func.sum(UsageStat.usage_count).label('total_usage'),
                func.sum(UsageStat.total_tokens).label('total_tokens'),
                func.count(UsageStat.id).label('total_requests')
            ).first()
            
            # 获取按模型分组的统计
            model_stats = db.session.query(
                Model.model_name,
                func.sum(UsageStat.usage_count).label('usage_count'),
                func.sum(UsageStat.total_tokens).label('tokens_used'),
                func.count(UsageStat.id).label('request_count')
            ).join(
                UsageStat, Model.model_name == UsageStat.model
            ).group_by(
                Model.model_name
            ).all()
            
            # 获取按Key分组的统计
            key_stats = db.session.query(
                Key.id,
                Key.name,
                func.sum(UsageStat.usage_count).label('usage_count'),
                func.sum(UsageStat.total_tokens).label('tokens_used'),
                func.count(UsageStat.id).label('request_count')
            ).join(
                UsageStat, Key.id == UsageStat.key_id
            ).group_by(
                Key.id, Key.name
            ).all()
            
            # 根据时间段获取额外统计
            time_stats = {}
            if period in ['daily', 'weekly', 'monthly']:
                if period == 'daily':
                    start_time = datetime.utcnow() - timedelta(days=1)
                elif period == 'weekly':
                    start_time = datetime.utcnow() - timedelta(days=7)
                else:  # monthly
                    start_time = datetime.utcnow() - timedelta(days=30)
                
                period_usage = db.session.query(
                    func.count(ChatHistory.id).label('request_count'),
                    func.sum(ChatHistory.tokens_used).label('tokens_used')
                ).filter(
                    ChatHistory.timestamp >= start_time
                ).first()
                
                time_stats = {
                    'period': period,
                    'request_count': period_usage.request_count or 0,
                    'tokens_used': period_usage.tokens_used or 0
                }
            
            return {
                'total_usage': {
                    'total_usage': total_usage.total_usage or 0,
                    'total_tokens': total_usage.total_tokens or 0,
                    'total_requests': total_usage.total_requests or 0
                },
                'model_stats': [
                    {
                        'model_name': item.model_name,
                        'usage_count': item.usage_count or 0,
                        'tokens_used': item.tokens_used or 0,
                        'request_count': item.request_count or 0
                    } for item in model_stats
                ],
                'key_stats': [
                    {
                        'key_id': item.id,
                        'key_name': item.name,
                        'usage_count': item.usage_count or 0,
                        'tokens_used': item.tokens_used or 0,
                        'request_count': item.request_count or 0
                    } for item in key_stats
                ],
                'time_stats': time_stats
            }
        except Exception as e:
            raise Exception(f"获取使用统计失败: {str(e)}")
    
    @staticmethod
    def get_key_stats(key_id: int) -> Dict[str, Any]:
        """
        获取Key统计
        """
        try:
            key = Key.query.get(key_id)
            if not key:
                return {}
            
            # 获取Key的模型使用分布
            model_distribution = db.session.query(
                Model.model_name,
                UsageStat.usage_count,
                UsageStat.total_tokens
            ).join(
                UsageStat, Model.model_name == UsageStat.model
            ).filter(
                UsageStat.key_id == key_id
            ).all()
            
            # 获取Key的每日使用趋势
            daily_trends = []
            for i in range(7):  # 获取过去7天的数据
                day_start = datetime.utcnow() - timedelta(days=i+1)
                day_end = datetime.utcnow() - timedelta(days=i)
                
                day_usage = db.session.query(
                    func.count(ChatHistory.id).label('request_count'),
                    func.sum(ChatHistory.tokens_used).label('tokens_used')
                ).filter(
                    ChatHistory.key_id == key_id,
                    ChatHistory.timestamp >= day_start,
                    ChatHistory.timestamp < day_end
                ).first()
                
                daily_trends.append({
                    'date': day_start.strftime('%Y-%m-%d'),
                    'request_count': day_usage.request_count or 0,
                    'tokens_used': day_usage.tokens_used or 0
                })
            
            # 反转列表，使日期从早到晚
            daily_trends.reverse()
            
            return {
                'key_info': key.to_dict(),
                'model_distribution': [
                    {
                        'model_name': item.model_name,
                        'usage_count': item.usage_count,
                        'tokens_used': item.total_tokens
                    } for item in model_distribution
                ],
                'daily_trends': daily_trends
            }
        except Exception as e:
            raise Exception(f"获取Key统计失败: {str(e)}")
    
    @staticmethod
    def get_model_stats(model_name: str) -> Dict[str, Any]:
        """
        获取模型统计
        """
        try:
            model = Model.query.filter_by(model_name=model_name).first()
            if not model:
                return {}
            
            # 获取模型的Key使用分布
            key_distribution = db.session.query(
                Key.id,
                Key.name,
                UsageStat.usage_count,
                UsageStat.total_tokens
            ).join(
                UsageStat, Key.id == UsageStat.key_id
            ).filter(
                UsageStat.model == model_name
            ).all()
            
            # 获取模型的每日使用趋势
            daily_trends = []
            for i in range(7):  # 获取过去7天的数据
                day_start = datetime.utcnow() - timedelta(days=i+1)
                day_end = datetime.utcnow() - timedelta(days=i)
                
                day_usage = db.session.query(
                    func.count(ChatHistory.id).label('request_count'),
                    func.sum(ChatHistory.tokens_used).label('tokens_used')
                ).filter(
                    ChatHistory.model == model_name,
                    ChatHistory.timestamp >= day_start,
                    ChatHistory.timestamp < day_end
                ).first()
                
                daily_trends.append({
                    'date': day_start.strftime('%Y-%m-%d'),
                    'request_count': day_usage.request_count or 0,
                    'tokens_used': day_usage.tokens_used or 0
                })
            
            # 反转列表，使日期从早到晚
            daily_trends.reverse()
            
            return {
                'model_info': model.to_dict(),
                'key_distribution': [
                    {
                        'key_id': item.id,
                        'key_name': item.name,
                        'usage_count': item.usage_count,
                        'tokens_used': item.total_tokens
                    } for item in key_distribution
                ],
                'daily_trends': daily_trends
            }
        except Exception as e:
            raise Exception(f"获取模型统计失败: {str(e)}")
    
    @staticmethod
    def get_hourly_usage(hours: int = 24) -> List[Dict[str, Any]]:
        """
        获取每小时使用统计
        """
        try:
            hourly_stats = []
            now = datetime.utcnow()
            
            for i in range(hours):
                hour_start = now - timedelta(hours=i+1)
                hour_end = now - timedelta(hours=i)
                
                hour_usage = db.session.query(
                    func.count(ChatHistory.id).label('request_count'),
                    func.sum(ChatHistory.tokens_used).label('tokens_used')
                ).filter(
                    ChatHistory.timestamp >= hour_start,
                    ChatHistory.timestamp < hour_end
                ).first()
                
                hourly_stats.append({
                    'hour': hour_start.strftime('%Y-%m-%d %H:00'),
                    'request_count': hour_usage.request_count or 0,
                    'tokens_used': hour_usage.tokens_used or 0
                })
            
            # 反转列表，使时间从早到晚
            hourly_stats.reverse()
            
            return hourly_stats
        except Exception as e:
            raise Exception(f"获取每小时使用统计失败: {str(e)}")

# 全局统计服务实例
stats_service = StatsService()