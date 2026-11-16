from datetime import datetime
from typing import Any, Dict, List


class DashboardService:
    """Calculates dashboard metrics and summary views for event progress."""

    def summarize_event(self, event_data: Dict[str, Any], tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(tasks)
        completed = sum(1 for task in tasks if task.get('status') == 'Completed')
        pending = sum(1 for task in tasks if task.get('status') == 'Pending')
        in_progress = sum(1 for task in tasks if task.get('status') == 'In Progress')
        blocked = sum(1 for task in tasks if task.get('status') == 'Blocked')
        overdue = 0

        for task in tasks:
            deadline = task.get('deadline')
            if not deadline or task.get('status') == 'Completed':
                continue
            try:
                due = datetime.fromisoformat(deadline)
            except ValueError:
                continue
            if due < datetime.utcnow():
                overdue += 1

        return {
            'total_events': 1,
            'total_tasks': total,
            'completed_tasks': completed,
            'pending_tasks': pending,
            'overdue_tasks': overdue,
            'in_progress_tasks': in_progress,
            'blocked_tasks': blocked,
            'completion_percentage': round((completed / total) * 100, 2) if total else 0,
            'event_name': event_data.get('event_name') or 'Untitled Event',
            'event_type': event_data.get('event_type') or 'Custom Event',
        }

    def task_distribution(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        categories = {}
        for task in tasks:
            category = task.get('category', 'General')
            categories[category] = categories.get(category, 0) + 1

        return [
            {'label': label, 'value': value}
            for label, value in sorted(categories.items())
        ]

    def priority_distribution(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        distribution = {'High': 0, 'Medium': 0, 'Low': 0}
        for task in tasks:
            priority = task.get('priority', 'Medium')
            if priority in distribution:
                distribution[priority] += 1
        return [
            {'label': 'High', 'value': distribution['High']},
            {'label': 'Medium', 'value': distribution['Medium']},
            {'label': 'Low', 'value': distribution['Low']},
        ]

    def upcoming_deadlines(self, tasks: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        pending = [task for task in tasks if task.get('status') != 'Completed' and task.get('deadline')]
        upcoming = []
        for task in pending:
            try:
                deadline = datetime.fromisoformat(task['deadline'])
            except ValueError:
                continue
            upcoming.append({'title': task.get('title'), 'deadline': deadline, 'priority': task.get('priority')})

        upcoming.sort(key=lambda item: item['deadline'])
        return upcoming[:limit]
