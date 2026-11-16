import re
from datetime import datetime
from typing import Any, Dict, List


class RequirementAnalysisAgent:
    """Analyzes raw natural-language event requirements into structured event metadata."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def analyze(self, raw_requirement: str, submitted_event_type: str = None) -> Dict[str, Any]:
        if not raw_requirement or not raw_requirement.strip():
            raise ValueError('Event requirement cannot be empty.')

        text = raw_requirement.strip()
        event_type = self._infer_event_type(text, submitted_event_type)
        parsed = {
            'event_name': self._infer_event_name(text, event_type),
            'event_type': event_type,
            'description': text,
            'objective': self._infer_objective(text),
            'participants': self._extract_participants(text),
            'budget': self._extract_budget(text),
            'event_date': self._extract_date(text),
            'location': self._extract_location(text),
            'duration': self._extract_duration(text),
            'required_resources': self._infer_resources(text),
            'special_requirements': self._infer_special_requirements(text),
            'missing_fields': [],
            'assumptions': [],
        }

        parsed['missing_fields'] = self._find_missing_fields(parsed)
        parsed['assumptions'] = self._get_assumptions(parsed)

        return parsed

    def _infer_event_type(self, text: str, submitted_event_type: str = None) -> str:
        if submitted_event_type and submitted_event_type.strip():
            return submitted_event_type.strip()

        normalized = text.lower()
        keywords = {
            'Technical Workshop': ['workshop', 'training', 'bootcamp', 'hands-on'],
            'Hackathon': ['hackathon', 'coding challenge', 'hack'],
            'Seminar': ['seminar', 'talk', 'guest lecture'],
            'Conference': ['conference', 'summit'],
            'College Fest': ['fest', 'cultural fest', 'college fest'],
            'Cultural Event': ['cultural', 'dance', 'music', 'theatre', 'festival'],
            'Sports Event': ['sports', 'tournament', 'match', 'football', 'cricket'],
            'Webinar': ['webinar', 'online webinar', 'virtual session'],
        }

        for event_type, keywords_list in keywords.items():
            if any(keyword in normalized for keyword in keywords_list):
                return event_type

        return 'Custom Event'

    def _infer_event_name(self, text: str, event_type: str) -> str:
        clean = text.strip()
        if not clean:
            return f'{event_type} Event'

        match = re.search(r'(?i)(?:plan|organize|create|host)\s+(?:a\s+)?(.+?)(?:\s+for\s+\d+|\s+with\s+budget|\s+in\s+\w+|$)', clean)
        if match:
            candidate = match.group(1).strip()
            if candidate:
                return candidate.title()

        return f'{event_type} Event'

    def _infer_objective(self, text: str) -> str:
        lowered = text.lower()
        if 'workshop' in lowered:
            return 'To provide structured learning and hands-on learning experience for attendees.'
        if 'hackathon' in lowered:
            return 'To encourage innovative problem-solving and rapid project development.'
        if 'seminar' in lowered:
            return 'To share knowledge and engage the audience through expert presentations.'
        if 'conference' in lowered:
            return 'To bring together participants for networking, knowledge exchange, and keynote sessions.'
        if 'fest' in lowered or 'cultural' in lowered:
            return 'To celebrate creativity, talent, and community engagement through a festive program.'
        return 'To deliver a successful and well-organized event experience for the target audience.'

    def _extract_participants(self, text: str) -> int:
        patterns = [
            r'(?:for|with)\s+(\d+)\s+(?:students|participants|people|attendees|guests)',
            r'(?:for|with)\s+(\d+)\s+(?:engineering\s+)?students',
            r'\b(\d+)\s+participants\b',
            r'\b(\d+)\s+students\b',
            r'\b(\d+)\s+people\b',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return 0

    def _extract_budget(self, text: str) -> float:
        patterns = [
            r'(?:budget(?:\s*(?:of|is))?|total\s+budget|available\s+budget)\s*[:=]?\s*₹?\s*([0-9,]+(?:\.[0-9]+)?)',
            r'(?:budget(?:\s*(?:of|is))?|total\s+budget|available\s+budget)\s*[:=]?\s*rs\.?\s*([0-9,]+(?:\.[0-9]+)?)',
            r'₹\s*([0-9,]+(?:\.[0-9]+)?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cleaned = match.group(1).replace(',', '')
                return float(cleaned)

        return 0.0

    def _extract_date(self, text: str):
        date_patterns = [
            r'\b(\d{4}-\d{2}-\d{2})\b',
            r'\b(\d{2}/\d{2}/\d{4})\b',
            r'\b(\d{1,2}\s+[A-Za-z]+\s+\d{4})\b',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                candidate = match.group(1)
                try:
                    return datetime.strptime(candidate, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        return datetime.strptime(candidate, '%d/%m/%Y').date()
                    except ValueError:
                        try:
                            return datetime.strptime(candidate, '%d %B %Y').date()
                        except ValueError:
                            pass

        return None

    def _extract_location(self, text: str) -> str:
        match = re.search(r'\b(?:in|at|near|location)\s+([A-Za-z][A-Za-z\s\-]+?)(?:\s+with|\s+for|\s+on|$)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return 'Not specified'

    def _extract_duration(self, text: str) -> str:
        duration_match = re.search(r'(\d+(?:\.\d+)?)\s*(day|days|hour|hours|week|weeks|month|months)', text, re.IGNORECASE)
        if duration_match:
            value = duration_match.group(1)
            unit = duration_match.group(2)
            return f'{value} {unit}'

        if 'two-day' in text.lower():
            return '2 days'
        if 'one-day' in text.lower():
            return '1 day'

        return 'Not specified'

    def _infer_resources(self, text: str) -> List[str]:
        resources = []
        resource_map = {
            'projector': ['projector', 'screen'],
            'microphones': ['microphone', 'mic'],
            'laptops': ['laptop', 'computer'],
            'internet': ['wifi', 'internet', 'network'],
            'chairs': ['chairs', 'seating'],
            'tables': ['tables', 'desk'],
            'backup power': ['power backup', 'ups', 'generator'],
            'food': ['food', 'snacks', 'refreshments'],
        }

        lowered = text.lower()
        for resource, keywords in resource_map.items():
            if any(keyword in lowered for keyword in keywords):
                resources.append(resource.title())

        if not resources:
            resources = ['Venue', 'Lighting', 'Registration Desk']

        return resources

    def _infer_special_requirements(self, text: str) -> List[str]:
        requirements = []
        special_keywords = {
            'registration form': ['registration form', 'register'],
            'speaker support': ['speaker', 'guest speaker', 'mentor'],
            'live streaming': ['live stream', 'streaming'],
            'accessibility': ['wheelchair', 'accessibility'],
            'hybrid mode': ['hybrid', 'online and offline'],
            'parking': ['parking'],
        }

        lowered = text.lower()
        for requirement, keywords in special_keywords.items():
            if any(keyword in lowered for keyword in keywords):
                requirements.append(requirement)

        return requirements

    def _find_missing_fields(self, parsed: Dict[str, Any]) -> List[str]:
        missing = []
        if not parsed.get('event_name'):
            missing.append('event_name')
        if not parsed.get('event_type'):
            missing.append('event_type')
        if not parsed.get('event_date'):
            missing.append('event_date')
        if not parsed.get('location') or parsed.get('location') == 'Not specified':
            missing.append('location')
        if not parsed.get('participants') or parsed.get('participants') <= 0:
            missing.append('participants')
        if not parsed.get('budget') or parsed.get('budget') <= 0:
            missing.append('budget')
        if not parsed.get('duration') or parsed.get('duration') == 'Not specified':
            missing.append('duration')
        return missing

    def _get_assumptions(self, parsed: Dict[str, Any]) -> List[str]:
        assumptions = []
        if parsed.get('location') == 'Not specified':
            assumptions.append('Location was not provided; defaulting to a local venue based on organizer preference.')
        if parsed.get('participants') in (None, 0):
            assumptions.append('Participant count was not specified; assuming a small planning capacity.')
        if parsed.get('budget') in (None, 0):
            assumptions.append('Budget was not specified; using a conservative planning estimate.')
        if parsed.get('duration') in (None, 'Not specified'):
            assumptions.append('Event duration was not provided; using a standard session duration.')
        return assumptions

    def fallback_plan(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'analysis_status': 'fallback',
            'message': 'Using rule-based planning fallback because no external LLM API is configured.',
            'event_data': event_data,
        }
