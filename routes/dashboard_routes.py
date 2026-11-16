from flask import Blueprint, jsonify

from models.event import Event
from models.task import Task
from services.dashboard_service import DashboardService

bp = Blueprint('dashboard', __name__)


@bp.route('/api/dashboard/<int:event_id>', methods=['GET'])
def dashboard(event_id):
    event = Event.query.get_or_404(event_id)
    tasks = Task.query.filter_by(event_id=event_id).all()
    task_data = [
        {
            'title': task.title,
            'status': task.status,
            'priority': task.priority,
            'category': task.category,
            'deadline': task.deadline.isoformat() if task.deadline else None,
        }
        for task in tasks
    ]
    dashboard_service = DashboardService()
    summary = dashboard_service.summarize_event(event.to_dict(), task_data)
    summary['task_distribution'] = dashboard_service.task_distribution(task_data)
    summary['priority_distribution'] = dashboard_service.priority_distribution(task_data)
    summary['upcoming_deadlines'] = dashboard_service.upcoming_deadlines(task_data)
    return jsonify(summary), 200
