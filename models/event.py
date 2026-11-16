from datetime import datetime

from database.database import db


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(150), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.Date, nullable=True)
    location = db.Column(db.String(200), nullable=True)
    participants = db.Column(db.Integer, nullable=True, default=0)
    budget = db.Column(db.Float, nullable=True, default=0.0)
    duration = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = db.relationship('Task', backref='event', lazy=True, cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='event', lazy=True, cascade='all, delete-orphan')
    activity_logs = db.relationship('EventActivityLog', backref='event', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'event_name': self.event_name,
            'event_type': self.event_type,
            'description': self.description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'location': self.location,
            'participants': self.participants,
            'budget': self.budget,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
