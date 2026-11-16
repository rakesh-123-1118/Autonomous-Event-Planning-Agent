import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app, db


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

    with app.app_context():
        db.drop_all()
        db.create_all()

    with app.test_client() as test_client:
        yield test_client


def test_event_creation_and_plan_generation(client):
    response = client.post(
        '/api/events',
        json={
            'event_name': 'AI Workshop',
            'event_type': 'Technical Workshop',
            'description': 'Plan a technical workshop for 40 participants in Bengaluru with a budget of 18000.',
            'event_date': '2026-12-10',
            'location': 'Bengaluru',
            'participants': 40,
            'budget': 18000,
            'duration': '1 day',
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data['event_name'] == 'AI Workshop'
    assert data['event_date'] == '2026-12-10'

    event_id = data['id']
    plan_response = client.post(f'/api/events/{event_id}/generate-plan')

    assert plan_response.status_code == 200
    plan_data = plan_response.get_json()
    assert plan_data['status'] == 'success'
    assert plan_data['generated_tasks'] > 0

    tasks_response = client.get(f'/api/events/{event_id}/tasks')
    tasks = tasks_response.get_json()
    assert tasks_response.status_code == 200
    assert len(tasks) > 0


def test_event_creation_rejects_invalid_date(client):
    response = client.post(
        '/api/events',
        json={
            'event_name': 'Invalid Date Event',
            'event_type': 'Seminar',
            'description': 'A test event',
            'event_date': 'not-a-date',
        },
    )

    assert response.status_code == 400
    assert 'YYYY-MM-DD' in response.get_json()['error']


def test_chat_responds_with_pending_task_context(client):
    response = client.post(
        '/api/events',
        json={
            'event_name': 'Startup Meetup',
            'event_type': 'Seminar',
            'description': 'Plan a startup meetup for 25 attendees in Mumbai with a modest budget.',
            'location': 'Mumbai',
            'participants': 25,
            'budget': 12000,
            'duration': 'half day',
        },
    )

    event_id = response.get_json()['id']
    client.post(f'/api/events/{event_id}/generate-plan')

    chat_response = client.post(
        f'/api/chat/{event_id}',
        json={'message': 'What tasks are remaining?'},
    )

    assert chat_response.status_code == 200
    answer = chat_response.get_json()['answer']
    assert 'pending' in answer.lower() or 'remaining' in answer.lower()
