from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple


class PlanningAgent:
    """Transforms parsed event requirements into a structured, dependency-aware task plan."""

    CATEGORY_TEMPLATES = {
        'Venue Management': [
            {
                'title': 'Finalize venue requirements',
                'description': 'Define seating, room layout, and venue needs for the event.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': []
            },
            {
                'title': 'Estimate seating capacity',
                'description': 'Confirm guest capacity and arrange seating plan based on participant count.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Finalize venue requirements']
            },
            {
                'title': 'Book venue',
                'description': 'Reserve the venue and confirm booking dates and contractual details.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Finalize venue requirements', 'Estimate seating capacity']
            },
            {
                'title': 'Confirm venue facilities',
                'description': 'Check power, Wi-Fi, stage, and accessibility facilities before final setup.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Book venue']
            },
        ],
        'Schedule Management': [
            {
                'title': 'Create event timetable',
                'description': 'Design the session schedule with opening, keynote, breaks, and closing segments.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': []
            },
            {
                'title': 'Allocate session durations',
                'description': 'Divide time slots between activities and manage transition intervals.',
                'priority': 'Medium',
                'estimated_cost': 0.0,
                'dependencies': ['Create event timetable']
            },
            {
                'title': 'Plan opening and closing ceremonies',
                'description': 'Prepare event flow for welcome, introductions, and closing remarks.',
                'priority': 'Medium',
                'estimated_cost': 0.0,
                'dependencies': ['Create event timetable']
            },
            {
                'title': 'Schedule breaks and refreshment gaps',
                'description': 'Insert short breaks and rest periods to keep attendees engaged.',
                'priority': 'Medium',
                'estimated_cost': 0.0,
                'dependencies': ['Allocate session durations']
            },
        ],
        'Resource Management': [
            {
                'title': 'List required equipment',
                'description': 'Identify equipment such as projectors, microphones, laptops, and backup power.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': []
            },
            {
                'title': 'Arrange AV equipment',
                'description': 'Secure projectors, audio systems, and screen equipment for the event day.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['List required equipment', 'Book venue']
            },
            {
                'title': 'Ensure internet and connectivity',
                'description': 'Confirm network coverage, Wi-Fi access, and backup connectivity for digital activities.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['List required equipment']
            },
            {
                'title': 'Plan seating and furniture setup',
                'description': 'Arrange chairs, tables, stage layout, and registration space for smooth flow.',
                'priority': 'Medium',
                'estimated_cost': 0.0,
                'dependencies': ['Book venue']
            },
        ],
        'Budget Management': [
            {
                'title': 'Create budget breakdown',
                'description': 'Estimate venue, food, equipment, marketing, and contingency expenses.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': []
            },
            {
                'title': 'Track venue and logistics cost',
                'description': 'Monitor and approve venue and logistics related expenses.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Create budget breakdown', 'Book venue']
            },
            {
                'title': 'Set contingency reserve',
                'description': 'Maintain emergency buffer for last-minute requirements or cancellations.',
                'priority': 'Medium',
                'estimated_cost': 0.0,
                'dependencies': ['Create budget breakdown']
            },
            {
                'title': 'Review expenditure before event day',
                'description': 'Validate total spending and ensure it remains within the approved budget.',
                'priority': 'Medium',
                'estimated_cost': 0.0,
                'dependencies': ['Track venue and logistics cost', 'Set contingency reserve']
            },
        ],
        'Speaker and Guest Coordination': [
            {
                'title': 'Identify speaker requirements',
                'description': 'List expertise, session topics, and required support for speakers and guests.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': []
            },
            {
                'title': 'Prepare speaker invitations',
                'description': 'Send formal invitations and agenda summaries to speakers.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Identify speaker requirements']
            },
            {
                'title': 'Confirm speaker availability',
                'description': 'Track confirmations and finalise speaking commitments.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Prepare speaker invitations']
            },
            {
                'title': 'Share final speaker schedule',
                'description': 'Publish the final speaker lineup and schedule to the team and audience.',
                'priority': 'Medium',
                'estimated_cost': 0.0,
                'dependencies': ['Confirm speaker availability']
            },
        ],
        'Publicity and Marketing': [
            {
                'title': 'Create promotional poster',
                'description': 'Design posters and digital assets to advertise the event.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': []
            },
            {
                'title': 'Prepare social media campaign',
                'description': 'Schedule posts and announcements across key social channels.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Create promotional poster']
            },
            {
                'title': 'Publish event details',
                'description': 'Share date, time, venue, and registration information with the target audience.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Prepare social media campaign', 'Book venue']
            },
            {
                'title': 'Promote registrations',
                'description': 'Drive participants to register and track responses to marketing efforts.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Publish event details']
            },
        ],
        'Participant Management': [
            {
                'title': 'Create registration form',
                'description': 'Prepare an online or offline form to collect participant details.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': []
            },
            {
                'title': 'Open registrations',
                'description': 'Launch the registration process and announce the call for participation.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Create registration form', 'Publish event details']
            },
            {
                'title': 'Track participant registrations',
                'description': 'Monitor registrations and manage attendee data accurately.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Open registrations']
            },
            {
                'title': 'Prepare attendance sheet',
                'description': 'Create final attendee tracking sheets for on-site event operations.',
                'priority': 'Medium',
                'estimated_cost': 0.0,
                'dependencies': ['Track participant registrations']
            },
        ],
        'Communication Management': [
            {
                'title': 'Send invitations',
                'description': 'Notify participants, speakers, and organizers about the event details.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Publish event details']
            },
            {
                'title': 'Send registration confirmations',
                'description': 'Confirm registration acceptance and provide important instructions.',
                'priority': 'Medium',
                'estimated_cost': 0.0,
                'dependencies': ['Open registrations']
            },
            {
                'title': 'Send reminders',
                'description': 'Send reminder messages to confirm attendance and event logistics.',
                'priority': 'Medium',
                'estimated_cost': 0.0,
                'dependencies': ['Send invitations', 'Send registration confirmations']
            },
            {
                'title': 'Share final event instructions',
                'description': 'Provide event-day instructions including time, venue, and arrival guidance.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Send reminders', 'Confirm venue facilities']
            },
        ],
        'Food and Refreshments': [
            {
                'title': 'Estimate food requirements',
                'description': 'Forecast the number of meals, snacks, and beverages required.',
                'priority': 'Medium',
                'estimated_cost': 0.0,
                'dependencies': ['Track participant registrations']
            },
            {
                'title': 'Plan refreshments schedule',
                'description': 'Arrange food timings and service flow during the event.',
                'priority': 'Medium',
                'estimated_cost': 0.0,
                'dependencies': ['Estimate food requirements', 'Create event timetable']
            },
            {
                'title': 'Coordinate food vendors',
                'description': 'Confirm delivery, budget, and service quality with food suppliers.',
                'priority': 'Medium',
                'estimated_cost': 0.0,
                'dependencies': ['Estimate food requirements']
            },
        ],
        'Final Preparation': [
            {
                'title': 'Run final venue check',
                'description': 'Verify the venue setup, logistics, and event readiness before the event.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Confirm venue facilities', 'Arrange AV equipment']
            },
            {
                'title': 'Test equipment and connectivity',
                'description': 'Check microphones, projectors, online connection, and backup systems.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Arrange AV equipment', 'Ensure internet and connectivity']
            },
            {
                'title': 'Prepare final event checklist',
                'description': 'Review all deliverables, staffing, materials, and logistics in one checklist.',
                'priority': 'High',
                'estimated_cost': 0.0,
                'dependencies': ['Run final venue check', 'Test equipment and connectivity']
            },
        ],
    }

    def generate_plan(self, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not event_data:
            raise ValueError('Event data is required to generate plan.')

        event_date = self._coerce_date(event_data.get('event_date'))
        participants = int(event_data.get('participants') or 0)
        budget = float(event_data.get('budget') or 0)

        tasks: List[Dict[str, Any]] = []
        created_titles: set = set()

        for category, templates in self.CATEGORY_TEMPLATES.items():
            for template in templates:
                title = template['title']
                if title in created_titles:
                    continue
                created_titles.add(title)

                task = {
                    'title': title,
                    'description': template['description'],
                    'category': category,
                    'priority': self._adjust_priority(template['priority'], participants, budget),
                    'status': 'Pending',
                    'deadline': self._build_deadline(event_date, category, len(tasks)),
                    'estimated_cost': self._estimate_cost(category, participants, budget),
                    'dependencies': template.get('dependencies', []),
                    'completion_notes': '',
                }
                tasks.append(task)

        return tasks

    def _coerce_date(self, value):
        if value is None:
            return datetime.utcnow().date() + timedelta(days=30)
        if isinstance(value, str):
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return value

    def _adjust_priority(self, base_priority: str, participants: int, budget: float) -> str:
        if base_priority == 'High':
            return 'High'
        if participants > 150 or budget > 50000:
            return 'High'
        if participants > 60 or budget > 20000:
            return 'Medium'
        return 'Low'

    def _estimate_cost(self, category: str, participants: int, budget: float) -> float:
        estimates = {
            'Venue Management': 0.2,
            'Schedule Management': 0.05,
            'Resource Management': 0.22,
            'Budget Management': 0.05,
            'Speaker and Guest Coordination': 0.08,
            'Publicity and Marketing': 0.1,
            'Participant Management': 0.07,
            'Communication Management': 0.06,
            'Food and Refreshments': 0.12,
            'Final Preparation': 0.05,
        }

        base_share = estimates.get(category, 0.05)
        if budget and budget > 0:
            return round(budget * base_share, 2)
        if participants:
            return round(participants * 7.5, 2)
        return 0.0

    def _build_deadline(self, event_date, category: str, index: int):
        if event_date is None:
            base = datetime.utcnow().date() + timedelta(days=21)
        else:
            base = event_date

        days_before_event = {
            'Venue Management': 21,
            'Schedule Management': 18,
            'Resource Management': 17,
            'Budget Management': 14,
            'Speaker and Guest Coordination': 12,
            'Publicity and Marketing': 10,
            'Participant Management': 12,
            'Communication Management': 7,
            'Food and Refreshments': 6,
            'Final Preparation': 2,
        }

        lead_days = days_before_event.get(category, 7)
        deadline = datetime.combine(base, datetime.min.time()) - timedelta(days=lead_days + (index % 3))
        return deadline


if __name__ == '__main__':
    agent = PlanningAgent()
    sample = {
        'event_name': 'AI Workshop',
        'event_type': 'Technical Workshop',
        'participants': 100,
        'budget': 25000,
        'event_date': '2026-12-10',
        'location': 'Bengaluru',
        'duration': '1 day',
        'description': 'Plan a technical workshop for 100 students in Bengaluru with a budget of INR 25000.'
    }
    plan = agent.generate_plan(sample)
    print('Generated tasks:', len(plan))
    for task in plan[:5]:
        print(task['title'], '-', task['category'], '-', task['priority'])
