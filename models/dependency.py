from database.database import db


class TaskDependency(db.Model):
    __tablename__ = 'task_dependencies'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    depends_on_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

    task = db.relationship(
        'Task',
        foreign_keys=[task_id],
        backref=db.backref('dependency_links', lazy='dynamic', foreign_keys=[task_id], overlaps='dependencies'),
        overlaps='dependencies'
    )
    prerequisite = db.relationship(
        'Task',
        foreign_keys=[depends_on_task_id],
        backref=db.backref('prerequisite_links', lazy='dynamic', foreign_keys=[depends_on_task_id], overlaps='prerequisites'),
        overlaps='prerequisites'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'depends_on_task_id': self.depends_on_task_id,
        }
