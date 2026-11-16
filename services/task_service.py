from datetime import datetime
from typing import Dict, List, Optional

from database.database import db
from models.dependency import TaskDependency
from models.task import Task


class TaskService:
    """Service for task state management, dependency checks, and updates."""

    VALID_STATUS = ['Pending', 'In Progress', 'Completed', 'Blocked']
    VALID_PRIORITY = ['Low', 'Medium', 'High']

    @staticmethod
    def parse_deadline(value):
        if value in (None, ''):
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            cleaned = value.replace('Z', '+00:00')
            try:
                return datetime.fromisoformat(cleaned)
            except ValueError:
                try:
                    return datetime.strptime(cleaned, '%Y-%m-%d')
                except ValueError:
                    return None
        return value

    def get_event_tasks(self, event_id: int) -> List[Task]:
        return Task.query.filter_by(event_id=event_id).order_by(Task.deadline.asc().nullslast()).all()

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        return db.session.get(Task, task_id)

    def create_task(self, event_id: int, payload: Dict) -> Task:
        task = Task(
            event_id=event_id,
            title=payload.get('title', 'Untitled Task'),
            description=payload.get('description'),
            category=payload.get('category', 'General'),
            priority=payload.get('priority', 'Medium'),
            status=payload.get('status', 'Pending'),
            deadline=self.parse_deadline(payload.get('deadline')),
            estimated_cost=payload.get('estimated_cost', 0.0),
            completion_notes=payload.get('completion_notes'),
        )
        db.session.add(task)
        db.session.commit()
        return task

    def update_task(self, task_id: int, payload: Dict) -> Task:
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f'Task {task_id} not found.')

        for key, value in payload.items():
            if key == 'deadline':
                value = self.parse_deadline(value)
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)

        task.updated_at = datetime.utcnow()
        db.session.commit()
        return task

    def delete_task(self, task_id: int) -> None:
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f'Task {task_id} not found.')

        TaskDependency.query.filter(
            (TaskDependency.task_id == task_id) | (TaskDependency.depends_on_task_id == task_id)
        ).delete(synchronize_session=False)
        db.session.delete(task)
        db.session.commit()

    def add_dependency(self, task_id: int, depends_on_task_id: int) -> TaskDependency:
        if task_id == depends_on_task_id:
            raise ValueError('A task cannot depend on itself.')

        if self._creates_cycle(task_id, depends_on_task_id):
            raise ValueError('Circular dependency detected.')

        existing = TaskDependency.query.filter_by(task_id=task_id, depends_on_task_id=depends_on_task_id).first()
        if existing:
            return existing

        dependency = TaskDependency(task_id=task_id, depends_on_task_id=depends_on_task_id)
        db.session.add(dependency)
        db.session.commit()
        return dependency

    def remove_dependency(self, task_id: int, depends_on_task_id: int) -> None:
        dependency = TaskDependency.query.filter_by(task_id=task_id, depends_on_task_id=depends_on_task_id).first()
        if dependency:
            db.session.delete(dependency)
            db.session.commit()

    def can_complete_task(self, task_id: int) -> bool:
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        prereqs = TaskDependency.query.filter_by(task_id=task_id).all()
        for dep in prereqs:
            parent = self.get_task_by_id(dep.depends_on_task_id)
            if parent is None or parent.status != 'Completed':
                return False
        return True

    def mark_task_status(self, task_id: int, status: str, completion_notes: str = None) -> Task:
        if status not in self.VALID_STATUS:
            raise ValueError('Invalid task status.')

        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f'Task {task_id} not found.')

        if status == 'Completed' and not self.can_complete_task(task_id):
            raise ValueError('Task cannot be completed because a prerequisite task is not complete.')

        if completion_notes is not None:
            task.completion_notes = completion_notes

        task.status = status
        task.updated_at = datetime.utcnow()
        db.session.commit()
        return task

    def get_task_metrics(self, event_id: int) -> Dict[str, int]:
        tasks = self.get_event_tasks(event_id)
        return {
            'total': len(tasks),
            'completed': sum(1 for task in tasks if task.status == 'Completed'),
            'pending': sum(1 for task in tasks if task.status == 'Pending'),
            'in_progress': sum(1 for task in tasks if task.status == 'In Progress'),
            'blocked': sum(1 for task in tasks if task.status == 'Blocked'),
            'overdue': sum(1 for task in tasks if task.deadline and task.status != 'Completed' and task.deadline < datetime.utcnow()),
            'completion_percentage': round((sum(1 for task in tasks if task.status == 'Completed') / len(tasks) * 100), 2) if tasks else 0,
        }

    def get_blocked_tasks(self, event_id: int) -> List[Task]:
        tasks = self.get_event_tasks(event_id)
        blocked = []
        for task in tasks:
            if not self.can_complete_task(task.id) and task.status != 'Completed':
                blocked.append(task)
        return blocked

    def _creates_cycle(self, task_id: int, depends_on_task_id: int) -> bool:
        if task_id == depends_on_task_id:
            return True

        visited = set()
        stack = [depends_on_task_id]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            deps = TaskDependency.query.filter_by(task_id=current).all()
            for dep in deps:
                if dep.depends_on_task_id == task_id:
                    return True
                stack.append(dep.depends_on_task_id)

        return False

    def update_priority(self, task_id: int, priority: str) -> Task:
        if priority not in self.VALID_PRIORITY:
            raise ValueError('Invalid task priority.')

        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f'Task {task_id} not found.')

        task.priority = priority
        task.updated_at = datetime.utcnow()
        db.session.commit()
        return task
