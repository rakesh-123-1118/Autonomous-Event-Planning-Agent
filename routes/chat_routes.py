from flask import Blueprint, jsonify, request

from models.event import Event
from models.task import Task
from services.ai_service import AIService

bp = Blueprint('chat', __name__)


@bp.route('/api/chat/<int:event_id>', methods=['POST'])
def chat(event_id):
    payload = request.get_json(silent=True) or {}
    user_question = payload.get('message', '').strip()

    event = Event.query.get_or_404(event_id)
    tasks = Task.query.filter_by(event_id=event_id).all()

    if not user_question:
        return jsonify({'answer': 'Please enter a question about the event plan.'}), 400

    task_data = [
        {
            'title': task.title,
            'status': task.status,
            'priority': task.priority,
            'deadline': task.deadline.isoformat() if task.deadline else None,
            'category': task.category,
        }
        for task in tasks
    ]

    answer = AIService().generate_chat_response(event.to_dict(), task_data, user_question)
    return jsonify({'answer': answer}), 200
