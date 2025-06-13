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
- **Analytics Dashboard**: Monitor platform usage and user performance
- **CSV Export**: Export user data and quiz results

### Technical Features
- **Real-time Processing**: Celery + Redis for background tasks
- **Email Notifications**: Automated email system for user engagement
- **Progressive Web App (PWA)**: Installable web application
- **Responsive Design**: Bootstrap-powered UI for all devices
- **RESTful API**: Clean and documented API architecture

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Background Tasks**: Celery + Redis
- **AI Integration**: Google Gemini API
- **Email**: Flask-Mail
- **Migration**: Flask-Migrate

### Frontend
- **Framework**: Vue.js 3 with Composition API
- **UI Components**: Bootstrap 5
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **PWA**: Manifest and Service Worker ready

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Redis Server
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/PrepCheck.git
   cd PrepCheck
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   # Create .env file in backend directory
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database Setup**
   ```bash
   flask db upgrade
   python seed_data.py  # Optional: Load sample data
   ```

6. **Start Redis Server**
   ```bash
   redis-server
   ```

7. **Start Celery Worker**
   ```bash
   celery -A app.celery worker --loglevel=info
   ```

8. **Run Flask Application**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

## 🚀 Usage

1. **Access the Application**
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8000

2. **Default Admin Account**
   - Email: admin@prepcheck.com
   - Password: admin123

3. **Default Test User**
   - Email: john@example.com
   - Password: password123

## 📁 Project Structure

```
PrepCheck/
├── backend/
│   ├── app/
│   │   ├── controllers/     # API endpoints
│   │   ├── models/          # Database models
│   │   ├── services/        # Business logic
│   │   └── utils/           # Helper functions
│   ├── migrations/          # Database migrations
│   ├── requirements.txt     # Python dependencies
│   └── app.py              # Flask application entry point
├── frontend/
│   ├── src/
│   │   ├── components/      # Vue components
│   │   ├── views/          # Page components
│   │   ├── services/       # API services
│   │   └── router/         # Vue Router configuration
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
└── docs/                   # Documentation
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///prepcheck.db

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key
```

## 🔒 Security Features

- JWT-based authentication with token expiration
- Password hashing using Werkzeug
- CORS configuration for cross-origin requests
- Input validation and sanitization
- SQL injection prevention through SQLAlchemy ORM

## 📊 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token

### User Endpoints
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile
- `GET /api/user/quiz-history` - Get user's quiz history

### Quiz Endpoints
- `GET /api/quizzes` - Get all quizzes
- `GET /api/quizzes/{id}` - Get specific quiz
- `POST /api/quizzes/{id}/submit` - Submit quiz answers

### Admin Endpoints
- `GET /api/admin/users` - Get all users
- `GET /api/admin/subjects` - Get all subjects
- `POST /api/admin/subjects` - Create new subject
- `POST /api/admin/generate-quiz` - AI-generated quiz

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 🚀 Deployment

### Production Environment Variables
Update your `.env` file for production:

```env
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://production-redis-host:6379/0
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Google Gemini AI for quiz generation
- Bootstrap team for the UI framework
- Vue.js community for the excellent framework
- Flask community for the backend framework

## 📞 Support

For support, email support@prepcheck.com or create an issue in this repository.

## 🔄 Changelog

### v1.0.0 (Current)
- Initial release with full functionality
- User authentication and management
- Quiz system with AI generation
- Admin dashboard and management tools
- PWA support and responsive design
