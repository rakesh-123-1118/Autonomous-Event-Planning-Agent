from agents.planning_agent import PlanningAgent


class PlanningService:
    def __init__(self):
        self.agent = PlanningAgent()

    def generate_tasks(self, event_data):
        return self.agent.generate_plan(event_data)

    def build_task_summary(self, tasks):
        summary = {
            'total': len(tasks),
            'pending': sum(1 for task in tasks if task.get('status') == 'Pending'),
            'in_progress': sum(1 for task in tasks if task.get('status') == 'In Progress'),
            'completed': sum(1 for task in tasks if task.get('status') == 'Completed'),
            'blocked': sum(1 for task in tasks if task.get('status') == 'Blocked'),
        }
        return summary
