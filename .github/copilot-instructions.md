# PrepCheck - AI Agent Instructions

## Project Overview
PrepCheck is a UGC NET exam preparation platform with a Flask backend and Vue.js frontend. The system uses AI (Google Gemini) for question generation and verification.

## Architecture

### Backend (`/backend`)
- Flask application with modular blueprint structure
- Celery for async tasks (question generation, verification)
- Redis for caching and message broker
- JWT authentication for API security
- SQLAlchemy ORM with migrations using Alembic

### Frontend (`/frontend`)
- Vue.js 3 SPA with Vue Router
- Bootstrap 5 for UI components
- Chart.js for analytics visualization
- Vite for development and build

## Key Development Workflows

### Local Development
1. Start development environment:
```bash
./dev-setup.sh  # Checks prerequisites and starts Docker containers
```

2. Watch for container startup issues in:
- `backend/app.log`
- `frontend/dev_server.pid`

### Database Changes
1. Create migration:
```bash
cd backend
flask db migrate -m "description"
flask db upgrade
```

### Testing
- Backend tests: `cd test && python -m pytest`
- Add test questions: Use scripts in `/test` (e.g., `add_cs_questions.py`)

## Project Conventions

### API Structure
- REST endpoints under `/api/v1/`
- Authentication required except for `/auth/` endpoints
- Response format:
```json
{
  "status": "success|error",
  "data": {},
  "message": "Optional message"
}
```

### File Organization
- Backend blueprints in `backend/app/`
- Frontend components in `frontend/src/components/`
- Shared types in `frontend/src/types/`

### State Management
- User session in Vue Router auth guard
- Vuex store for global state
- Local storage for persistent auth tokens

## Integration Points
- Google Gemini AI: Configure via `GEMINI_API_KEY` in `.env`
- Redis: Required for Celery tasks and caching
- PostgreSQL: Primary database (SQLite in development)

## Common Gotchas
- Redis must be running for Celery tasks
- Frontend dev server needs write access to `dev_server.pid`
- AI question generation rate limits apply

For detailed documentation, see `/docs/` directory.
