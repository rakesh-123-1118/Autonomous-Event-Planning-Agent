from datetime import datetime
from typing import Any, Dict, List


class RecommendationAgent:
    """Generates recommendations from current event/task state."""

    def generate_recommendations(self, event_data: Dict[str, Any], tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        recommendations: List[Dict[str, Any]] = []

        if not tasks:
            return [{
                'text': 'No tasks have been created yet. Generate the initial event plan to begin planning.',
                'priority': 'Medium',
                'is_resolved': False,
            }]

        pending_tasks = [task for task in tasks if task.get('status') == 'Pending']
        overdue = []
        high_priority = [task for task in pending_tasks if task.get('priority') == 'High']

        for task in tasks:
            deadline = task.get('deadline')
            if not deadline or task.get('status') == 'Completed':
                continue
            try:
                due = datetime.fromisoformat(deadline)
            except ValueError:
                continue
            if due < datetime.utcnow():
                overdue.append(task)

        if overdue:
            top = overdue[0]
            recommendations.append({
                'text': f"Deadline risk detected: '{top.get('title')}' is overdue. Prioritize this task immediately.",
                'priority': 'High',
                'is_resolved': False,
            })

        if high_priority:
            recommendation_text = f"There are {len(high_priority)} high-priority tasks still pending. Focus on completing them before lower-priority work."
            recommendations.append({
                'text': recommendation_text,
                'priority': 'High',
                'is_resolved': False,
            })

        if pending_tasks:
            no_of_pending = len(pending_tasks)
            recommendations.append({
                'text': f"{no_of_pending} task(s) are still pending. Review the next highest-impact tasks and complete the most urgent ones.",
                'priority': 'Medium',
                'is_resolved': False,
            })

        completion_ratio = sum(1 for t in tasks if t.get('status') == 'Completed') / len(tasks)
        if completion_ratio < 0.5:
            recommendations.append({
                'text': 'Progress is below 50%. Complete the core planning tasks before final preparation begins.',
                'priority': 'High',
                'is_resolved': False,
            })

        if event_data.get('participants', 0) and int(event_data.get('participants')) > 100:
            recommendations.append({
                'text': 'Participant count is high. Review seating, refreshments, venue capacity, and equipment scale-up requirements.',
                'priority': 'Medium',
                'is_resolved': False,
            })

        if not recommendations:
            recommendations.append({
                'text': 'The event plan is on track. Keep monitoring task completion and upcoming deadlines.',
                'priority': 'Low',
                'is_resolved': True,
            })

        return recommendations

    def build_event_recommendation_text(self, event_name: str, tasks: List[Dict[str, Any]]) -> str:
        pending = [task for task in tasks if task.get('status') == 'Pending']
        if not pending:
            return f"All tasks for {event_name} are complete. The event is ready for final review."
        return f"The next recommended focus for {event_name} is to complete the pending tasks that are still blocking progress and causing deadline risk."
