import os
from typing import Any, Dict, List

import requests


class AIService:
    """Handles optional LLM integration with a safe fallback for local execution."""

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY') or os.getenv('GEMINI_API_KEY') or os.getenv('LLM_API_KEY')
        self.endpoint = os.getenv('LLM_API_URL')
        self.model = os.getenv('LLM_MODEL', 'gpt-4o-mini')

    def generate_chat_response(self, event: Dict[str, Any], tasks: List[Dict[str, Any]], user_message: str) -> str:
        question = (user_message or '').strip()
        if not question:
            return 'Please ask a valid question about the event plan.'

        if self.api_key and self.endpoint:
            try:
                response = self._call_llm(event, tasks, question)
                if response:
                    return response
            except Exception:
                pass

        return self._fallback_response(event, tasks, question)

    def _call_llm(self, event: Dict[str, Any], tasks: List[Dict[str, Any]], user_message: str) -> str:
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an event planning assistant. Use the provided event data and tasks to answer clearly.'
                },
                {
                    'role': 'user',
                    'content': f"Event context: {event}\nTasks: {tasks}\nQuestion: {user_message}"
                }
            ],
            'temperature': 0.4,
        }

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

        response = requests.post(self.endpoint, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        if 'choices' in data and data['choices']:
            return data['choices'][0]['message']['content'].strip()
        return ''

    def _fallback_response(self, event: Dict[str, Any], tasks: List[Dict[str, Any]], user_message: str) -> str:
        question = user_message.lower()
        pending = [task for task in tasks if str(task.get('status')) == 'Pending']
        high = [task for task in pending if str(task.get('priority')) == 'High']
        overdue = []

        for task in tasks:
            deadline = task.get('deadline')
            if deadline and str(task.get('status')) != 'Completed':
                try:
                    from datetime import datetime
                    due = datetime.fromisoformat(deadline)
                    if due < datetime.utcnow():
                        overdue.append(task)
                except ValueError:
                    continue

        if 'remaining' in question or 'unfinished' in question or 'pending' in question:
            if pending:
                names = ', '.join(task.get('title', 'Untitled task') for task in pending[:5])
                return f"{len(pending)} tasks are still pending. Focus on: {names}."
            return 'No pending tasks remain. The plan is complete.'

        if 'next' in question or 'what should i do' in question or 'priority' in question:
            if high:
                return f"Your next priority should be '{high[0].get('title')}' because it is high-priority and still pending."
            if pending:
                return f"Your next priority should be '{pending[0].get('title')}' because it is the earliest urgent action in the plan."
            return 'There is no critical pending task. You can review final preparations and confirm readiness.'

        if 'participants' in question or 'increase' in question:
            return 'The event requirements have changed. Revisit venue capacity, seating, refreshments, equipment scale, and the budget to match the updated attendee count.'

        if overdue:
            return f"Deadline risk detected: '{overdue[0].get('title')}' is overdue. Review and complete it immediately."

        if event.get('participants', 0) and int(event.get('participants')) > 100:
            return 'The attendee count is high. Review venue capacity, seating, food estimates, and equipment needs before final execution.'

        if tasks and len(tasks) > 0:
            completed = sum(1 for task in tasks if str(task.get('status')) == 'Completed')
            return f"Currently {completed} of {len(tasks)} tasks are complete. Continue the pending and high-priority items to keep the plan on track."

        return 'The event is ready for planning. Add a requirement and generate the task plan to start.'
