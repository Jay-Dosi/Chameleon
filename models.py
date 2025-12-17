from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AttackLog(db.Model):
    __tablename__ = 'attack_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    request_method = db.Column(db.String(10))
    endpoint = db.Column(db.String(500))
    payload_data = db.Column(db.Text, nullable=True)
    ai_response_sent = db.Column(db.Text)
    user_agent = db.Column(db.String(500))
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': self.ip_address,
            'request_method': self.request_method,
            'endpoint': self.endpoint,
            'payload_data': self.payload_data,
            'ai_response_sent': self.ai_response_sent,
            'user_agent': self.user_agent
        }
