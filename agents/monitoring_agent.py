from datetime import datetime
from typing import Dict, List


class StateMonitoringAgent:
    """Monitors task completion, overdue items, and progress summaries."""

    def summarize_tasks(self, tasks: List[Dict]) -> Dict[str, int]:
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

        completion_pct = round((completed / total) * 100, 2) if total else 0

        return {
            'total_tasks': total,
            'completed_tasks': completed,
            'pending_tasks': pending,
            'in_progress_tasks': in_progress,
            'blocked_tasks': blocked,
            'overdue_tasks': overdue,
            'completion_percentage': completion_pct,
        }

    def identify_overdue(self, tasks: List[Dict]) -> List[Dict]:
        overdue = []
        for task in tasks:
            if task.get('status') == 'Completed':
                continue
            deadline = task.get('deadline')
            if not deadline:
                continue
            try:
                due = datetime.fromisoformat(deadline)
            except ValueError:
                continue
            if due < datetime.utcnow():
                overdue.append(task)
        return overdue

    def identify_pending(self, tasks: List[Dict]) -> List[Dict]:
        return [task for task in tasks if task.get('status') == 'Pending']
