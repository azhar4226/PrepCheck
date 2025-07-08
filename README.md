# PrepCheck - UGC NET Exam Preparation Platform

PrepCheck is a comprehensive web application designed for UGC NET exam preparation with AI-powered question generation, practice tests, mock tests, and advanced analytics.

## 🚀 Features

### For Students

- **User Authentication**: Secure JWT-based login/registration system
- **UGC NET Practice Tests**: Chapter-wise practice with customizable difficulty
- **Mock Test Simulation**: Full UGC NET mock tests with Paper 1 + Paper 2 flow
- **Intelligent Question Bank**: AI-verified questions with detailed explanations
- **Performance Analytics**: Chapter-wise analysis, strengths/weaknesses identification
- **Progress Tracking**: Long-term performance trends and improvement tracking
- **Study Recommendations**: AI-powered personalized study suggestions

### For Administrators

- **User Management**: View and manage all registered users
- **Subject Management**: Create and organize UGC NET subjects and chapters
- **Question Bank Management**: Full CRUD operations for questions with verification
- **AI Question Generation**: Generate questions automatically using Google Gemini AI
- **AI Verification System**: Automatic verification of AI-generated questions
- **Test Analytics Dashboard**: Monitor platform usage and user performance
- **CSV Export**: Export user data and test results

## 🛠 Tech Stack

### Backend

- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM with PostgreSQL/SQLite support
- **Celery** - Asynchronous task processing
- **Redis** - Message broker and caching
- **Google Gemini AI** - AI-powered question generation and verification
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

### UGC NET Test Flow

1. **Register/Login** - Create account or login
2. **Select Subject** - Choose UGC NET Paper 2 subject (Computer Science, Mathematics, etc.)
3. **Practice Tests** - Select chapters and configure difficulty for focused practice
4. **Mock Tests** - Take full UGC NET simulation with Paper 1 + Paper 2
5. **View Results** - Detailed analytics with chapter-wise performance and study recommendations

### API Testing

```bash
# Test API endpoints
./test-api.sh
```

## 📊 AI Question Generation & Verification System

PrepCheck includes an advanced AI system that generates and verifies UGC NET questions:

### Question Generation
- **Subject-specific Generation**: Questions tailored to UGC NET subjects and chapters
- **Difficulty Control**: Generate questions with specific difficulty levels (Easy/Medium/Hard)
- **Syllabus Alignment**: Questions aligned with UGC NET syllabus and weightage
- **Multiple Sources**: AI-generated, previous year, and manually curated questions

### Verification System
- **Real-time Verification**: Questions are verified as they're generated
- **Confidence Scoring**: Each question receives a confidence score
- **Manual Override**: Administrators can manually approve/reject questions
- **Retry Mechanism**: Failed verifications can be retried with different parameters
- **Comprehensive Logging**: Full audit trail of verification processes

### Question Bank Features
- **Smart Categorization**: Questions organized by chapters, difficulty, and source
- **Performance Tracking**: Track question performance and success rates
- **Duplicate Detection**: Automatic detection and prevention of duplicate questions
- **Usage Analytics**: Track question usage patterns and effectiveness

## 🔧 Configuration

### Environment Variables

Key environment variables to configure:

- `GOOGLE_API_KEY`: Google Gemini AI API key for question generation
- `SECRET_KEY`: Flask application secret key
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string for background tasks
- `MAIL_SERVER`: SMTP server for email notifications

## 📚 API Documentation

### Authentication Endpoints

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Authenticate user and get token
- `GET /api/auth/profile` - Get user profile information
- `PUT /api/auth/profile` - Update user profile
- `DELETE /api/auth/delete` - Delete user account

### Subject and Chapter Endpoints

- `GET /api/subjects` - List all available subjects
- `GET /api/subjects/{id}` - Get subject details
- `GET /api/subjects/{id}/chapters` - List chapters for a subject
- `GET /api/chapters/{id}` - Get chapter details and topics

### Question Bank Endpoints

- `GET /api/questions` - List questions (with filters)
- `GET /api/questions/{id}` - Get question details
- `POST /api/questions/verify` - Submit a question for AI verification
- `POST /api/questions/generate` - Generate new questions for a chapter

### Practice Test Endpoints

- `GET /api/practice-tests` - List user's practice tests
- `POST /api/practice-tests` - Create a new practice test
- `GET /api/practice-tests/{id}` - Get practice test details
- `POST /api/practice-tests/{id}/attempt` - Start a new practice test attempt

### Mock Test Endpoints

- `GET /api/mock-tests` - List available mock tests
- `GET /api/mock-tests/{id}` - Get mock test details
- `POST /api/mock-tests/{id}/attempt` - Start a new mock test attempt

### Test Attempt Endpoints

- `GET /api/attempts` - List user's test attempts
- `GET /api/attempts/{id}` - Get attempt details
- `POST /api/attempts/{id}/submit` - Submit answers for an attempt
- `GET /api/attempts/{id}/analysis` - Get performance analysis for an attempt

For detailed request/response formats and examples, refer to the Swagger documentation available at `/api/docs` when running the application.

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

### UGC NET System Testing

```bash
# Test complete UGC NET workflow
cd test
python final_ugc_net_test.py
```

### End-to-End Testing

```bash
./test-api.sh
```

## 🏗️ System Architecture

### Data Flow

The PrepCheck system follows a layered architecture with clear separation of concerns:

1. **Client Layer**: Vue.js frontend handling user interactions and UI rendering
2. **API Layer**: RESTful endpoints for client-server communication
3. **Service Layer**: Core business logic and AI processing pipeline
4. **Data Access Layer**: Database operations via SQLAlchemy ORM
5. **External Services**: Google Gemini AI, Redis, email services

### Database Schema

Key entities in the PrepCheck database:

- **User**: Authentication and profile information
- **Subject**: UGC NET subjects (Computer Science, Mathematics, etc.)
- **Chapter**: Subject chapters and topic organization
- **Question**: Question bank with metadata, difficulty, and verification status
- **PracticeTest**: User-configured chapter-specific practice tests
- **MockTest**: Complete UGC NET simulation tests
- **TestAttempt**: User's test attempts with performance metrics
- **AIVerification**: AI verification history and confidence scores

#### Key Relationships

- User → TestAttempt: One-to-many relationship tracking all test attempts by a user
- Subject → Chapter: One-to-many hierarchical organization of subject material
- Chapter → Question: One-to-many association of questions to their respective chapters
- Question → TestAttempt: Many-to-many through attempt_questions junction table
- PracticeTest → Chapter: Many-to-many allowing tests to cover multiple chapters
- MockTest → Subject: Tests are organized by their relevant subject

For a complete visual representation of the database schema, refer to the entity-relationship diagrams in `docs/Reports/PREPCHECK_SYSTEM_DIAGRAMS.md`.

### Microservices

- **Web Server**: Main Flask application
- **Celery Worker**: Background task processing for AI operations
- **Redis**: Message broker and caching layer
- **PostgreSQL**: Primary database for production

### AI Processing Pipeline

PrepCheck leverages Google Gemini AI for:

1. **Question Generation**: Creating high-quality UGC NET questions based on subject and chapter specifications
2. **Answer Verification**: Validating user answers against expected solutions with detailed explanation
3. **Question Validation**: Ensuring generated questions meet quality standards and UGC NET format
4. **Performance Analytics**: Analyzing user performance patterns to provide personalized feedback

The AI processing flow:
- Request submitted through API → Queued in Redis → Processed by Celery worker → Results stored in database → Response returned to user

## 📦 Deployment

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

**PrepCheck** - Empowering UGC NET aspirants through intelligent assessment and personalized learning analytics.
