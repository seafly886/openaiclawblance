"""
聊天历史记录数据模型
"""

from datetime import datetime
from app import db

class ChatHistory(db.Model):
    """
    聊天历史记录数据模型
    """
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    key_id = db.Column(db.Integer, db.ForeignKey('keys.id'), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    request = db.Column(db.Text, nullable=False)  # JSON格式存储请求内容
    response = db.Column(db.Text, nullable=True)  # JSON格式存储响应内容
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tokens_used = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f'<ChatHistory {self.id}: Key {self.key_id} - {self.model}>'
    
    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            'id': self.id,
            'key_id': self.key_id,
            'model': self.model,
            'request': self.request,
            'response': self.response,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'tokens_used': self.tokens_used
        }
    
    @staticmethod
    def create_record(key_id, model, request, response=None, tokens_used=0):
        """
        创建聊天历史记录
        """
        chat_history = ChatHistory(
            key_id=key_id,
            model=model,
            request=request,
            response=response,
            tokens_used=tokens_used
        )
        db.session.add(chat_history)
        db.session.commit()
        return chat_history
    
    def update_response(self, response, tokens_used=0):
        """
        更新响应内容
        """
        self.response = response
        self.tokens_used = tokens_used
        db.session.commit()
    
    @staticmethod
    def get_recent_history(limit=50):
        """
        获取最近的聊天历史记录
        """
        return ChatHistory.query.order_by(ChatHistory.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_history_by_key(key_id, limit=50):
        """
        根据Key获取聊天历史记录
        """
        return ChatHistory.query.filter_by(key_id=key_id).order_by(ChatHistory.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_history_by_model(model, limit=50):
        """
        根据模型获取聊天历史记录
        """
        return ChatHistory.query.filter_by(model=model).order_by(ChatHistory.timestamp.desc()).limit(limit).all()