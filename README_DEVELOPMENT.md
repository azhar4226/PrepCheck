# PrepCheck Development Guide

## 🚀 Latest Updates (January 2025)

### Completed Features ✅

#### 1. Advanced Analytics System
- **Backend Analytics Controller** (`/backend/app/controllers/analytics_controller.py`)
  - Analytics overview with performance metrics and user engagement
  - User-specific analytics with improvement trends
  - Quiz-specific analytics with question-wise analysis
  - Time-based analytics and daily trends
  - Subject performance tracking

- **Frontend Analytics Dashboard** (`/frontend/src/views/admin/Analytics.vue`)
  - Interactive dashboard with key metrics cards
  - Charts for data visualization
  - Subject performance breakdown
  - Top performers display
  - Detailed analytics tables

#### 2. Notifications System
- **Backend Notifications Controller** (`/backend/app/controllers/notifications_controller.py`)
  - User notification retrieval with achievement tracking
  - Mark as read functionality (individual and bulk)
  - Notification preferences management
  - Test notification capability
  - Study streak notifications
  - Performance-based notifications

- **Frontend Notifications Component** (`/frontend/src/components/NotificationsDropdown.vue`)
  - Real-time notification display with unread count badges
  - Auto-refresh every 30 seconds
  - Mark as read functionality
  - Different notification types with appropriate icons
  - Integrated into main navigation

#### 3. Enhanced Security & Configuration
- Updated `.env` file with secure development keys
- Blueprint architecture for modular code organization
- JWT authentication for all new endpoints

#### 4. API Extensions
- Extended API service with 10+ new endpoints
- Proper error handling and authentication checks
- RESTful design patterns

### System Architecture

```
PrepCheck/
├── backend/
│   ├── app/
│   │   ├── controllers/
│   │   │   ├── analytics_controller.py     # Analytics endpoints
│   │   │   └── notifications_controller.py # Notifications endpoints
│   │   └── __init__.py                     # Blueprint registration
│   └── .env                                # Environment configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── NotificationsDropdown.vue  # Notifications UI
│   │   ├── views/admin/
│   │   │   └── Analytics.vue               # Analytics dashboard
│   │   ├── services/
│   │   │   └── api.js                      # Extended API service
│   │   ├── router/
│   │   │   └── index.js                    # Updated routing
│   │   └── App.vue                         # Main app with notifications
└── docker-compose.yml                      # Container orchestration
```

## 🛠️ Development Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 16+ (for local frontend development)
- Git

### Quick Start

1. **Clone and navigate to the project:**
```bash
cd /Users/apple/Desktop/PrepCheck
```

2. **Start the backend services:**
```bash
docker compose up -d
```

3. **Start frontend development server:**
```bash
cd frontend
npm install
npm run serve
```

4. **Access the applications:**
- Frontend (dev): http://localhost:3001
- Frontend (prod): http://localhost
- Backend API: http://localhost:8000

### Testing the New Features

#### Admin Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@prepcheck.com",
    "password": "admin123"
  }'
```

#### Test Analytics
```bash
curl -X GET http://localhost:8000/api/analytics/overview \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Test Notifications
```bash
curl -X GET http://localhost:8000/api/notifications/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

curl -X POST http://localhost:8000/api/notifications/send-test \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🎯 Current Status

### ✅ Working Features
- **Authentication System**: Login/Register/JWT tokens
- **Quiz Management**: Admin can create/edit quizzes
- **User Dashboard**: Quiz taking and history
- **Analytics Dashboard**: Comprehensive metrics and charts
- **Notifications System**: Real-time notifications with badges
- **Admin Panel**: Full administrative controls
- **Docker Deployment**: Multi-container setup

### 🚧 Next Priority Features

#### 1. AI Quiz Generation
- Configure Gemini AI API
- Implement AI-powered quiz creation
- Topic-based question generation

#### 2. Real-time Features
- WebSocket implementation for live notifications
- Real-time user activity tracking
- Live quiz sessions

#### 3. Email Notifications
- SMTP configuration
- Email templates for notifications
- Scheduled digest emails

#### 4. Enhanced Security
- Rate limiting
- Input validation improvements
- CSRF protection

#### 5. Mobile Responsiveness
- PWA implementation
- Mobile-optimized UI
- Offline capability

## 📊 API Endpoints

### Analytics Endpoints
- `GET /api/analytics/overview` - System overview analytics
- `GET /api/analytics/user/<user_id>` - User-specific analytics
- `GET /api/analytics/quiz/<quiz_id>` - Quiz-specific analytics

### Notifications Endpoints
- `GET /api/notifications/` - Get user notifications
- `POST /api/notifications/<id>/read` - Mark notification as read
- `POST /api/notifications/mark-all-read` - Mark all as read
- `GET /api/notifications/preferences` - Get notification preferences
- `PUT /api/notifications/preferences` - Update preferences
- `POST /api/notifications/send-test` - Send test notification

### Existing Endpoints
- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration
- `GET /api/subjects/` - Get all subjects
- `GET /api/quizzes/` - Get quizzes
- `POST /api/quiz-attempts/` - Submit quiz attempt

## 🐛 Known Issues
- None currently reported

## 🔧 Development Notes

### Database Schema
The application uses SQLite for development. Key tables:
- `users` - User accounts
- `subjects` - Quiz subjects/categories
- `quizzes` - Quiz definitions
- `questions` - Quiz questions
- `quiz_attempts` - User quiz attempts
- `answers` - User answers

### Environment Variables
Key environment variables in `.env`:
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key
- `DATABASE_URL` - Database connection
- `GEMINI_API_KEY` - AI service (to be configured)

### Frontend State Management
- User authentication state in localStorage
- API service centralized in `src/services/api.js`
- Real-time updates via polling (30s intervals)

## 📝 Contributing

1. Create feature branches from main
2. Test all endpoints with provided curl commands
3. Ensure Docker containers rebuild successfully
4. Test frontend integration in browser
5. Update this documentation for new features

## 🚀 Deployment

The application is containerized and ready for production deployment. Update environment variables for production use and ensure proper security configurations.
