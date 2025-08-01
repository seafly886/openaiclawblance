"""
使用统计数据模型
"""

from datetime import datetime
from app import db

class UsageStat(db.Model):
    """
    Key使用统计数据模型
    """
    __tablename__ = 'usage_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    key_id = db.Column(db.Integer, db.ForeignKey('keys.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=True)
    model = db.Column(db.String(100), nullable=False)
    usage_count = db.Column(db.Integer, nullable=False, default=0)
    last_used = db.Column(db.DateTime, nullable=True)
    total_tokens = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f'<UsageStat {self.id}: Key {self.key_id} - {self.model}>'
    
    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            'id': self.id,
            'key_id': self.key_id,
            'model_id': self.model_id,
            'model': self.model,
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'total_tokens': self.total_tokens
        }
    
    def update_usage(self, tokens_used=0):
        """
        更新使用统计
        """
        self.usage_count += 1
        self.total_tokens += tokens_used
        self.last_used = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def get_or_create(key_id, model, model_id=None):
        """
        获取或创建使用统计记录
        """
        stat = UsageStat.query.filter_by(key_id=key_id, model=model).first()
        if not stat:
            stat = UsageStat(key_id=key_id, model=model, model_id=model_id)
            db.session.add(stat)
            db.session.commit()
        return stat