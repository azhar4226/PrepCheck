# PrepCheck Development Guide

This guide contains detailed information for developers working o2.
**Configure environment variables**

## Root .env file

   ```env PrepCheck project.

## 📁 Project Structure

### Backend Structure

```text
backend/
├── app/
│   ├── controllers/        # API route handlers
│   │   ├── auth_controller.py      # Authentication endpoints
│   │   ├── user_controller.py      # User management
│   │   ├── admin_controller.py     # Admin operations
│   │   ├── quiz_controller.py      # Quiz operations
│   │   ├── ai_controller.py        # AI quiz generation & verification
│   │   ├── analytics_controller.py # Analytics endpoints
│   │   └── notifications_controller.py # Notification management
│   ├── models/             # Database models
│   │   └── models.py       # SQLAlchemy models
│   ├── services/           # Business logic
│   │   └── ai_service.py   # Google Gemini AI integration
│   ├── tasks/              # Celery background tasks
│   │   ├── verification_tasks.py   # AI verification tasks
│   │   ├── export_tasks.py         # Data export tasks
│   │   └── notification_tasks.py   # Email notification tasks
│   └── utils/              # Utility functions
│       ├── email_service.py        # Email functionality
│       └── seed_data.py            # Database seeding
├── migrations/             # Alembic database migrations
├── config/                 # Configuration files
├── instance/               # Instance-specific files (database)
├── app.py                 # Flask application entry point
├── celery_app.py          # Celery configuration
└── requirements.txt       # Python dependencies
```

### Frontend Structure

```text
frontend/
├── src/
│   ├── components/         # Reusable Vue components
│   │   ├── QuizResults.vue         # Quiz results display
│   │   └── NotificationsDropdown.vue # Notification dropdown
│   ├── views/              # Page components
│   │   ├── auth/           # Authentication pages
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   ├── user/           # User pages
│   │   │   ├── Dashboard.vue
│   │   │   ├── Profile.vue
│   │   │   └── History.vue
│   │   ├── quiz/           # Quiz pages
│   │   │   ├── Browse.vue
│   │   │   └── Taking.vue
│   │   └── admin/          # Admin pages
│   │       ├── Dashboard.vue
│   │       ├── UserManagement.vue
│   │       ├── SubjectManagement.vue
│   │       ├── QuizManagement.vue
│   │       ├── AIQuizGenerator.vue
│   │       └── Analytics.vue
│   ├── router/             # Vue Router configuration
│   ├── services/           # API services
│   │   ├── api.js          # API client
│   │   └── utils.js        # Utility functions
│   ├── composables/        # Vue composition functions
│   │   └── useAuth.js      # Authentication composable
│   ├── App.vue            # Root component
│   └── main.js            # Application entry point
├── public/                 # Static assets
├── package.json           # Node.js dependencies
└── vite.config.js         # Vite configuration
```

## 🚀 Development Setup

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.8+** (for local development)
- **Node.js 16+** (for frontend development)
- **Redis** (for Celery tasks)
- **PostgreSQL or SQLite** (database)

### Environment Configuration

1. **Copy environment files**

   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   ```

2. **Configure environment variables**

**Root .env file:**

```env
COMPOSE_PROJECT_NAME=prepcheck
NODE_ENV=development
```

**Backend .env file:**

   ```env
   # Flask Configuration
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=development
   FLASK_DEBUG=True

   # Database
   DATABASE_URL=sqlite:///instance/prepcheck.db
   # For PostgreSQL: postgresql://user:password@localhost/prepcheck

   # Google AI
   GOOGLE_API_KEY=your-google-api-key

   # Redis
   REDIS_URL=redis://localhost:6379/0

   # Email Configuration
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password

   # Admin User
   ADMIN_EMAIL=admin@prepcheck.com
   ADMIN_PASSWORD=admin123
   ```

### Development with Docker (Recommended)

1. **Start all services**

   ```bash
   docker-compose up -d
   ```

2. **View logs**

   ```bash
   docker-compose logs -f
   ```

3. **Stop services**

   ```bash
   docker-compose down
   ```

### Local Development Setup

#### Backend Setup

1. **Create virtual environment**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize database**

   ```bash
   flask db upgrade
   python -c "from app.utils.seed_data import seed_database; seed_database()"
   ```

4. **Start backend server**

   ```bash
   python app.py
   ```

5. **Start Celery worker (separate terminal)**

   ```bash
   celery -A celery_worker.celery worker --loglevel=info
   ```

#### Frontend Setup

1. **Install dependencies**

   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**

   ```bash
   npm run dev
   ```

## 🏗️ Architecture Overview

### Database Models

#### Core Models

- **User**: User accounts with role-based permissions
- **Subject**: Quiz categories and subjects
- **Chapter**: Subject subdivisions
- **Quiz**: Quiz definitions with metadata
- **Question**: Individual quiz questions with AI verification
- **QuizAttempt**: User quiz submissions and results

#### AI Verification Fields

Questions include verification fields:

- `ai_verified`: Boolean verification status
- `verification_confidence`: AI confidence score (0.0-1.0)
- `verification_metadata`: JSON metadata from verification
- `verification_attempts`: Number of verification attempts
- `manual_override`: Manual approval by admin

### API Architecture

#### Authentication Flow

1. User submits credentials to `/api/auth/login`
2. Server validates and returns JWT token
3. Client includes token in `Authorization: Bearer <token>` header
4. Server validates token on protected routes

#### AI Quiz Generation Flow

1. Admin submits quiz parameters to `/api/ai/generate-quiz`
2. Backend calls Google Gemini AI API
3. Generated quiz stored as draft
4. Background verification task started via Celery
5. Questions verified individually with confidence scoring
6. Admin reviews and publishes verified quiz

### Background Tasks

#### Celery Tasks

- **verification_tasks.py**
  - `verify_and_store_quiz_task`: Verify entire quiz
  - `verify_single_question_task`: Verify individual questions

- **export_tasks.py**
  - `export_admin_data`: Export user and quiz data
  - `export_user_data`: Export user-specific data

- **notification_tasks.py**
  - `send_daily_reminders`: Daily study reminders
  - `send_monthly_reports`: Monthly progress reports

## 🧪 Testing

### Backend Testing

```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Testing

```bash
cd frontend
npm run test
```

### API Testing Script

```bash
./test-api.sh
```

## 🐛 Debugging

### Backend Debugging

1. **Enable debug mode**

   ```env
   FLASK_DEBUG=True
   ```

2. **View application logs**

   ```bash
   docker-compose logs backend
   ```

3. **Database inspection**

   ```bash
   # Connect to database container
   docker-compose exec backend python
   >>> from app import db
   >>> from app.models import User, Quiz, Question
   >>> User.query.all()
   ```

### Frontend Debugging

1. **Vue DevTools**: Install browser extension
2. **Console logging**: Check browser console
3. **Network tab**: Monitor API calls

### Celery Task Debugging

```bash
# View Celery worker logs
docker-compose logs celery

# Monitor task queues
docker-compose exec backend celery -A celery_worker.celery inspect active
```

## 📝 Code Style & Standards

### Python (Backend)

- **PEP 8** compliance
- **Type hints** where appropriate
- **Docstrings** for functions and classes
- **Error handling** with try/catch blocks

### JavaScript (Frontend)

- **ESLint** configuration
- **Vue 3 Composition API** preferred
- **Async/await** for API calls
- **Component naming**: PascalCase

### Database

- **Migration files** for schema changes
- **Indexing** for frequently queried fields
- **Foreign key constraints** properly defined

## 🚀 Deployment

### Production Deployment

1. **Environment setup**

   ```bash
   # Production environment variables
   NODE_ENV=production
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

2. **Build and deploy**

   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

### Database Migrations

```bash
# Create new migration
docker-compose exec backend flask db migrate -m "Description"

# Apply migrations
docker-compose exec backend flask db upgrade
```

### Monitoring

- **Application logs**: `docker-compose logs`
- **Database performance**: Monitor query execution
- **Celery tasks**: Monitor task completion rates
- **Redis memory**: Monitor Redis usage

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Issues

```bash
# Check database container
docker-compose ps database

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Celery Task Issues

```bash
# Restart Celery worker
docker-compose restart celery

# Clear task queue
docker-compose exec backend celery -A celery_worker.celery purge
```

#### Frontend Build Issues

```bash
# Clear npm cache
npm cache clean --force

# Rebuild node_modules
rm -rf node_modules package-lock.json
npm install
```

## 📚 Additional Resources

- **Flask Documentation**: <https://flask.palletsprojects.com/>
- **Vue.js Documentation**: <https://vuejs.org/>
- **Celery Documentation**: <https://docs.celeryproject.org/>
- **Google AI Documentation**: <https://ai.google.dev/>

---

For specific implementation details, check the inline code comments and docstrings.
