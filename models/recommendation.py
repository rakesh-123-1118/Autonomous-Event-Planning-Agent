from datetime import datetime

from database.database import db


class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    recommendation_text = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(50), nullable=False, default='Medium')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'recommendation_text': self.recommendation_text,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_resolved': self.is_resolved,
        }
