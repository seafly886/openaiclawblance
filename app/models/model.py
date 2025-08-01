"""
模型信息数据模型
"""

from datetime import datetime
from app import db

class Model(db.Model):
    """
    OpenAI模型信息数据模型
    """
    __tablename__ = 'models'
    
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    capabilities = db.Column(db.Text, nullable=True)  # JSON格式存储模型能力
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    usage_stats = db.relationship('UsageStat', backref='model_info', lazy=True)
    chat_history = db.relationship('ChatHistory', backref='model_info', lazy=True)
    
    def __repr__(self):
        return f'<Model {self.id}: {self.model_name}>'
    
    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            'id': self.id,
            'model_name': self.model_name,
            'description': self.description,
            'capabilities': self.capabilities,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_or_create(model_name, description=None, capabilities=None):
        """
        获取或创建模型记录
        """
        model = Model.query.filter_by(model_name=model_name).first()
        if not model:
            model = Model(
                model_name=model_name,
                description=description,
                capabilities=capabilities
            )
            db.session.add(model)
            db.session.commit()
        return model
    
    def update_info(self, description=None, capabilities=None):
        """
        更新模型信息
        """
        if description is not None:
            self.description = description
        if capabilities is not None:
            self.capabilities = capabilities
        self.updated_at = datetime.utcnow()
        db.session.commit()