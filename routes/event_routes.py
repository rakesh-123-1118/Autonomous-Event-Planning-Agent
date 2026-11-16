from datetime import date, datetime

from flask import Blueprint, jsonify, request

from agents.orchestrator import EventPlanningOrchestrator
from agents.recommendation_agent import RecommendationAgent
from database.database import db
from models.dependency import TaskDependency
from models.event import Event
from models.task import Task
from services.dashboard_service import DashboardService
from services.task_service import TaskService

bp = Blueprint('events', __name__)


def _parse_event_date(value):
    if value in (None, ''):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return datetime.strptime(value, '%Y-%m-%d').date()


@bp.route('/api/events', methods=['GET'])
def list_events():
    try:
        events = Event.query.order_by(Event.created_at.desc()).all()
        return jsonify([event.to_dict() for event in events]), 200
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@bp.route('/api/events', methods=['POST'])
def create_event():
    data = request.get_json(silent=True) or {}
    try:
        try:
            event_date = _parse_event_date(data.get('event_date'))
        except (TypeError, ValueError):
            return jsonify({'error': 'Event date must use YYYY-MM-DD format.'}), 400

        event_name = (data.get('event_name') or 'Untitled Event').strip()
        description = (data.get('description') or data.get('event_name') or 'Event planning requirement').strip()
        event = Event(
            event_name=event_name,
            event_type=data.get('event_type', 'Custom Event'),
            description=description,
            event_date=event_date,
            location=data.get('location'),
            participants=int(data.get('participants') or 0),
            budget=float(data.get('budget') or 0.0),
            duration=data.get('duration'),
        )
        db.session.add(event)
        db.session.commit()
        return jsonify(event.to_dict()), 201
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': str(exc)}), 400


@bp.route('/api/events/<int:event_id>/generate-plan', methods=['POST'])
def generate_event_plan(event_id):
    event = Event.query.get_or_404(event_id)
    try:
        requirement = event.description or f"Plan {event.event_name} in {event.location or 'the specified location'}"
        orchestrator = EventPlanningOrchestrator()
        analysis = orchestrator.analyze_requirement(requirement, event.event_type)

        event_data = {
            **analysis,
            'event_name': event.event_name,
            'event_type': event.event_type,
            'description': event.description,
            'event_date': event.event_date.isoformat() if event.event_date else None,
            'location': event.location,
            'participants': event.participants,
            'budget': event.budget,
            'duration': event.duration,
        }
        plan = orchestrator.generate_plan(event_data)

        existing_tasks = Task.query.filter_by(event_id=event_id).all()
        for task in existing_tasks:
            TaskDependency.query.filter(
                (TaskDependency.task_id == task.id) | (TaskDependency.depends_on_task_id == task.id)
            ).delete(synchronize_session=False)
            db.session.delete(task)
        db.session.commit()

        created_tasks = {}
        task_service = TaskService()

        for item in plan:
            task = task_service.create_task(event_id, {
                'title': item['title'],
                'description': item['description'],
                'category': item['category'],
                'priority': item['priority'],
                'status': item['status'],
                'deadline': item['deadline'].isoformat() if hasattr(item['deadline'], 'isoformat') else item['deadline'],
                'estimated_cost': item['estimated_cost'],
                'completion_notes': item.get('completion_notes', ''),
            })
            created_tasks[item['title']] = task

        for item in plan:
            task = created_tasks.get(item['title'])
            for dependency_name in item.get('dependencies', []):
                dependency_task = created_tasks.get(dependency_name)
                if task and dependency_task:
                    try:
                        task_service.add_dependency(task.id, dependency_task.id)
                    except ValueError:
                        pass

        return jsonify({'status': 'success', 'generated_tasks': len(plan), 'event_id': event_id}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': str(exc)}), 400


@bp.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict()), 200


@bp.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_json(silent=True) or {}
    event = Event.query.get_or_404(event_id)

    for key in ['event_name', 'event_type', 'description', 'location', 'participants', 'budget', 'duration']:
        if key in data:
            setattr(event, key, data[key])

    if 'event_date' in data:
        try:
            event.event_date = _parse_event_date(data['event_date'])
        except (TypeError, ValueError):
            db.session.rollback()
            return jsonify({'error': 'Event date must use YYYY-MM-DD format.'}), 400

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': str(exc)}), 400
    return jsonify(event.to_dict()), 200


@bp.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted'}), 200


@bp.route('/api/events/<int:event_id>/dashboard', methods=['GET'])
def get_dashboard(event_id):
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
    service = DashboardService()
    summary = service.summarize_event(event.to_dict(), task_data)
    return jsonify(summary), 200


@bp.route('/api/events/<int:event_id>/recommendations', methods=['GET'])
def get_recommendations(event_id):
    event = Event.query.get_or_404(event_id)
    tasks = Task.query.filter_by(event_id=event_id).all()
    task_data = [
        {
            'title': task.title,
            'status': task.status,
            'priority': task.priority,
            'deadline': task.deadline.isoformat() if task.deadline else None,
        }
        for task in tasks
    ]
    recommendations = RecommendationAgent().generate_recommendations(event.to_dict(), task_data)
    return jsonify(recommendations), 200
