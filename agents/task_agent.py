from typing import Any, Dict, List


class TaskManagementAgent:
    """Responsible for task normalization and state transitions."""

    VALID_STATUS = ['Pending', 'In Progress', 'Completed', 'Blocked']
    VALID_PRIORITY = ['Low', 'Medium', 'High']

    def normalize_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task = dict(task)
        task['status'] = task.get('status', 'Pending')
        task['priority'] = task.get('priority', 'Medium')
        task['title'] = task.get('title', 'Untitled Task')
        task['category'] = task.get('category', 'General')
        if task['status'] not in self.VALID_STATUS:
            task['status'] = 'Pending'
        if task['priority'] not in self.VALID_PRIORITY:
            task['priority'] = 'Medium'
        return task

    def validate_task_state(self, task: Dict[str, Any]) -> bool:
        if not task.get('title'):
            return False
        return task.get('status') in self.VALID_STATUS

    def build_task_index(self, tasks: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        index = {}
        for task in tasks:
            task_id = task.get('id')
            if task_id is not None:
                index[int(task_id)] = task
        return index
