from datetime import datetime

from database.database import db


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(50), nullable=False, default='Medium')
    status = db.Column(db.String(50), nullable=False, default='Pending')
    deadline = db.Column(db.DateTime, nullable=True)
    estimated_cost = db.Column(db.Float, nullable=True, default=0.0)
    completion_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    dependencies = db.relationship(
        'TaskDependency',
        foreign_keys='TaskDependency.task_id',
        lazy=True,
        cascade='all, delete-orphan',
        overlaps='dependency_links,task'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'estimated_cost': self.estimated_cost,
            'completion_notes': self.completion_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
