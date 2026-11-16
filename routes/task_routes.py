from flask import Blueprint, jsonify, request

from database.database import db
from models.task import Task
from models.dependency import TaskDependency
from services.task_service import TaskService

bp = Blueprint('tasks', __name__)


@bp.route('/api/events/<int:event_id>/tasks', methods=['GET'])
def list_tasks(event_id):
    tasks = Task.query.filter_by(event_id=event_id).all()
    return jsonify([task.to_dict() for task in tasks]), 200


@bp.route('/api/events/<int:event_id>/tasks', methods=['POST'])
def create_task(event_id):
    data = request.get_json(silent=True) or {}
    try:
        task = Task(
            event_id=event_id,
            title=data.get('title'),
            description=data.get('description'),
            category=data.get('category', 'General'),
            priority=data.get('priority', 'Medium'),
            status=data.get('status', 'Pending'),
            deadline=TaskService.parse_deadline(data.get('deadline')),
            estimated_cost=data.get('estimated_cost', 0.0),
            completion_notes=data.get('completion_notes'),
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': str(exc)}), 400


@bp.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict()), 200


@bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json(silent=True) or {}

    for key in ['title', 'description', 'category', 'priority', 'status', 'estimated_cost', 'completion_notes']:
        if key in data:
            setattr(task, key, data[key])

    if 'deadline' in data:
        task.deadline = TaskService.parse_deadline(data.get('deadline'))

    db.session.commit()
    return jsonify(task.to_dict()), 200


@bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'}), 200


@bp.route('/api/tasks/<int:task_id>/status', methods=['POST'])
def update_task_status(task_id):
    data = request.get_json(silent=True) or {}
    status = data.get('status')
    completion_notes = data.get('completion_notes')
    service = TaskService()

    try:
        task = service.mark_task_status(task_id, status, completion_notes)
        return jsonify(task.to_dict()), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


@bp.route('/api/tasks/<int:task_id>/dependencies', methods=['GET'])
def get_dependencies(task_id):
    deps = TaskDependency.query.filter_by(task_id=task_id).all()
    return jsonify([dep.to_dict() for dep in deps]), 200


@bp.route('/api/tasks/<int:task_id>/dependencies', methods=['POST'])
def add_dependency(task_id):
    data = request.get_json(silent=True) or {}
    depends_on_task_id = data.get('depends_on_task_id')
    try:
        dep = TaskService().add_dependency(task_id, depends_on_task_id)
        return jsonify(dep.to_dict()), 201
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
