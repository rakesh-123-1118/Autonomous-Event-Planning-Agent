from typing import Any, Dict, List, Optional

from agents.planning_agent import PlanningAgent
from agents.requirement_agent import RequirementAnalysisAgent


class EventPlanningOrchestrator:
    """Central orchestrator for event requirement analysis and plan generation."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.requirement_agent = RequirementAnalysisAgent(api_key=api_key)
        self.planning_agent = PlanningAgent()

    def run(self, raw_event_requirement: str, submitted_event_type: str = None) -> Dict[str, Any]:
        if not raw_event_requirement or not raw_event_requirement.strip():
            raise ValueError('Event requirement cannot be empty.')

        structured_event = self.requirement_agent.analyze(raw_event_requirement, submitted_event_type)
        plan = self.planning_agent.generate_plan(structured_event)

        result = {
            'event_analysis': structured_event,
            'plan': plan,
            'summary': {
                'task_count': len(plan),
                'categories': sorted({task['category'] for task in plan}),
                'high_priority_tasks': sum(1 for task in plan if task['priority'] == 'High'),
                'medium_priority_tasks': sum(1 for task in plan if task['priority'] == 'Medium'),
                'low_priority_tasks': sum(1 for task in plan if task['priority'] == 'Low'),
            },
        }

        return result

    def analyze_requirement(self, raw_event_requirement: str, submitted_event_type: str = None) -> Dict[str, Any]:
        return self.requirement_agent.analyze(raw_event_requirement, submitted_event_type)

    def generate_plan(self, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not event_data:
            raise ValueError('Event data is required to generate tasks.')
        return self.planning_agent.generate_plan(event_data)

    def build_event_context(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        context = {
            'event_name': event_data.get('event_name') or 'Untitled Event',
            'event_type': event_data.get('event_type') or 'Custom Event',
            'objective': event_data.get('objective') or 'Deliver a successful event experience.',
            'participants': event_data.get('participants') or 0,
            'budget': event_data.get('budget') or 0,
            'location': event_data.get('location') or 'Not specified',
            'duration': event_data.get('duration') or 'Not specified',
            'required_resources': event_data.get('required_resources') or [],
            'special_requirements': event_data.get('special_requirements') or [],
        }
        return context


if __name__ == '__main__':
    orchestrator = EventPlanningOrchestrator()
    result = orchestrator.run('Organize a technical workshop for 100 students in Bengaluru with a budget of ₹25,000.')
    print('Analysis keys:', sorted(result['event_analysis'].keys()))
    print('Task count:', result['summary']['task_count'])
    print('First task:', result['plan'][0]['title'])
