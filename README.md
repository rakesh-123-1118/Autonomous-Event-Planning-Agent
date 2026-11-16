# Autonomous Event Planning Agent

A Flask-based event planning assistant that turns a natural-language event idea into a structured execution plan with tasks, dependencies, recommendations, a dashboard, and an AI chat interface.

## Features

- Natural-language event requirement parsing
- AI-style planning and task decomposition
- Dependency-aware task management
- Recommendation engine based on live task state
- SQLite-backed event and task persistence
- Dashboard summaries for planning progress
- Local AI fallback for environments without API keys

## Project Structure

- `app.py` – Flask app bootstrap and route registration
- `config.py` – environment and app configuration
- `agents/` – planning, requirement analysis, recommendation, and monitoring logic
- `services/` – planning, dashboard, task, and AI service layers
- `routes/` – Flask API and page endpoints
- `models/` – SQLAlchemy models for events, tasks, and recommendations
- `templates/` – HTML views
- `static/` – CSS and JavaScript assets
- `database/` – SQLite database files
- `tests/` – automated validation tests

## Quick Start

1. Open a terminal in the project folder.
2. Activate the virtual environment:

```powershell
.\ .venv\Scripts\Activate.ps1
```

If your shell treats the path incorrectly, use:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies (if needed):

```powershell
pip install -r requirements.txt
```

4. Start the app:

```powershell
python app.py
```

5. Open the app in a browser:

```text
http://127.0.0.1:5000
```

## Typical Workflow

1. Create a new event from the Create Event page.
2. Generate a plan from the event description.
3. Review the generated tasks and dependencies.
4. Manage task status from the Task Management page.
5. Monitor progress from the Dashboard.
6. Ask the AI assistant for next actions or remaining tasks.

## API Endpoints

- `POST /api/events` – create an event
- `GET /api/events` – list events
- `POST /api/events/<id>/generate-plan` – generate tasks for an event
- `GET /api/events/<id>/tasks` – list event tasks
- `POST /api/chat/<id>` – ask the assistant a planning question

## Testing

Run the automated checks with:

```powershell
pytest
```

## Notes

- The app falls back to local logic when no external AI provider is configured.
- SQLite stores the app state in `database/app.db` by default.
