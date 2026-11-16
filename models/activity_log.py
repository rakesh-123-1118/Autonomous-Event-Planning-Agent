from datetime import datetime

from database.database import db


class EventActivityLog(db.Model):
    __tablename__ = 'event_activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    action = db.Column(db.String(200), nullable=False)
    previous_status = db.Column(db.String(50), nullable=True)
    new_status = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'task_id': self.task_id,
            'action': self.action,
            'previous_status': self.previous_status,
            'new_status': self.new_status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
