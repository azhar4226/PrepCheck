# PrepCheck - Multi-User Exam Preparation Platform

PrepCheck is a comprehensive web application designed for multi-user exam preparation with AI-powered quiz generation, admin management, and real-time analytics.

## 🚀 Features

### For Students

- **User Authentication**: Secure JWT-based login/registration system
- **Interactive Quizzes**: Take quizzes with immediate feedback
- **Progress Tracking**: Monitor your performance and improvement over time
- **Subject Browse**: Explore quizzes by subjects and difficulty levels
- **Results History**: View detailed quiz results and analytics

### For Administrators

- **User Management**: View and manage all registered users
- **Subject Management**: Create, edit, and organize quiz subjects
- **Quiz Management**: Full CRUD operations for quizzes and questions
- **AI Quiz Generation**: Generate quizzes automatically using Google Gemini AI
- **AI Verification System**: Automatic verification of AI-generated questions
- **Analytics Dashboard**: Monitor platform usage and user performance
- **CSV Export**: Export user data and quiz results

## 🛠 Tech Stack

### Backend

- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM with PostgreSQL/SQLite support
- **Celery** - Asynchronous task processing
- **Redis** - Message broker and caching
- **Google Gemini AI** - AI-powered quiz generation
- **JWT** - JSON Web Token authentication
- **Alembic** - Database migrations

### Frontend

- **Vue.js 3** - Progressive JavaScript framework
- **Vue Router** - Client-side routing
- **Bootstrap 5** - CSS framework
- **Chart.js** - Interactive charts and analytics
- **Axios** - HTTP client

### Infrastructure

- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Web server and reverse proxy

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd PrepCheck
   ```

2. **Set up environment variables**

   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   # Edit .env files with your configuration
   ```

3. **Start the application**

   ```bash
   # Make setup script executable
   chmod +x dev-setup.sh
   
   # Run setup (checks prerequisites and starts containers)
   ./dev-setup.sh
   
   # Or manually with Docker Compose
   docker-compose up -d
   ```

4. **Access the application**

   - Frontend: <http://localhost:3000>
   - Backend API: <http://localhost:8000>
   - Admin login: <admin@prepcheck.com> / admin123

### API Testing

```bash
# Test API endpoints
./test-api.sh
```

## 📊 AI Verification System

PrepCheck includes an advanced AI verification system that automatically validates AI-generated quiz questions:

- **Real-time Verification**: Questions are verified as they're generated
- **Confidence Scoring**: Each question receives a confidence score
- **Manual Override**: Administrators can manually approve/reject questions
- **Retry Mechanism**: Failed verifications can be retried with different parameters
- **Comprehensive Logging**: Full audit trail of verification processes

## 🔧 Configuration

### Environment Variables

Key environment variables to configure:

- `GOOGLE_API_KEY`: Google Gemini AI API key
- `SECRET_KEY`: Flask application secret key
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `MAIL_SERVER`: SMTP server for email notifications

## 📝 API Documentation

### Authentication

All API endpoints require JWT authentication except login/register.

### Key Endpoints

- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration
- `GET /api/quiz/` - Get available quizzes
- `POST /api/quiz/{id}/attempt` - Submit quiz attempt
- `POST /api/ai/generate-quiz` - Generate AI quiz (Admin)
- `GET /api/ai/verification-status/{task_id}` - Check verification status

## 🧪 Testing

### Backend Testing

```bash
cd backend
python -m pytest tests/
```

### Frontend Testing

```bash
cd frontend
npm run test
```

### End-to-End Testing

```bash
./test-api.sh
```

## 📦 Deployment

### Docker Production

```bash
docker-compose -f docker-compose.yml up -d
```

### Manual Deployment

See `README_DEVELOPMENT.md` for detailed deployment instructions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions, please open an issue in the repository.

---

**PrepCheck** - Empowering education through intelligent assessment technology.
