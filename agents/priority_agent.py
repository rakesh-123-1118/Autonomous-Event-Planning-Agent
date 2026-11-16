from datetime import datetime
from typing import Dict, List


class PriorityManagementAgent:
    """Determines task urgency based on deadline, status, and importance."""

    def rank_tasks(self, tasks: List[Dict]) -> List[Dict]:
        ranked = []
        for task in tasks:
            score = self._score_task(task)
            ranked.append({**task, '_priority_score': score})

        return sorted(ranked, key=lambda t: t['_priority_score'], reverse=True)

    def _score_task(self, task: Dict) -> int:
        score = 0
        if task.get('priority') == 'High':
            score += 30
        elif task.get('priority') == 'Medium':
            score += 15
        else:
            score += 5

        if task.get('status') == 'Blocked':
            score += 25
        elif task.get('status') == 'Pending':
            score += 15
        elif task.get('status') == 'In Progress':
            score += 5

        deadline = task.get('deadline')
        if deadline:
            try:
                deadline_dt = datetime.fromisoformat(deadline)
            except ValueError:
                deadline_dt = None
            if deadline_dt:
                days_left = (deadline_dt - datetime.utcnow()).days
                if days_left <= 0:
                    score += 30
                elif days_left <= 3:
                    score += 20
                elif days_left <= 7:
                    score += 10

        return score

    def recommend_next_action(self, tasks: List[Dict]) -> str:
        if not tasks:
            return 'There are no active tasks for the event right now.'

        top = self.rank_tasks(tasks)[0]
        return f"Prioritize '{top.get('title')}' because it is a {top.get('priority')} priority task with the most urgent current status."
