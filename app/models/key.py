"""
Key数据模型
"""

from datetime import datetime
from app import db

class Key(db.Model):
    """
    OpenAI Key数据模型
    """
    __tablename__ = 'keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key_value = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, inactive, error
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used = db.Column(db.DateTime, nullable=True)
    usage_count = db.Column(db.Integer, nullable=False, default=0)
    
    # 关联关系
    usage_stats = db.relationship('UsageStat', backref='key', lazy=True, cascade='all, delete-orphan')
    chat_history = db.relationship('ChatHistory', backref='key', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Key {self.id}: {self.name or self.key_value[:8]}...>'
    
    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            'id': self.id,
            'key_value': self.key_value,
            'name': self.name,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count
        }
    
    def update_usage(self):
        """
        更新使用统计
        """
        self.usage_count += 1
        self.last_used = datetime.utcnow()
        db.session.commit()
    
    def set_status(self, status):
        """
        设置Key状态
        """
        if status in ['active', 'inactive', 'error']:
            self.status = status
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False