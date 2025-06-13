# PrepCheck - Multi-User Exam Preparation App

PrepCheck is a comprehensive web application for exam preparation featuring AI-powered quiz generation, multi-user support, and advanced analytics.

## 🚀 Features

- **Multi-User Support**: Admin and user roles with secure authentication
- **AI-Powered Quizzes**: Generate quizzes using Google Gemini AI
- **Real-time Progress**: Track learning progress and performance analytics
- **Async Tasks**: Background processing with Celery and Redis
- **Email Notifications**: Automated email alerts and updates
- **Data Export**: CSV export functionality for results
- **Modern UI**: Responsive design with Vue.js and Bootstrap
- **PWA Support**: Progressive Web App capabilities

## 🛠 Tech Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **Celery** - Asynchronous task queue
- **Redis** - Message broker and caching
- **JWT** - Secure authentication
- **Gemini AI** - Quiz generation

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Bootstrap 5** - UI components and styling
- **Vite** - Build tool and dev server

## 📋 Prerequisites

- Docker and Docker Compose
- Git
- Gemini AI API key
- Email account for SMTP (Gmail recommended)

## 🚀 Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/azhar4226/PrepCheck.git
   cd PrepCheck
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and email credentials
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000

## 🔧 Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Initialize database
flask db upgrade

# Start development server
python app.py
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## 🌍 Environment Variables

Required environment variables (see `.env.example`):

- `GEMINI_API_KEY` - Your Google Gemini AI API key
- `MAIL_SERVER` - SMTP server (e.g., smtp.gmail.com)
- `MAIL_PORT` - SMTP port (e.g., 587)
- `MAIL_USERNAME` - Your email address
- `MAIL_PASSWORD` - Your email app password

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### Quizzes
- `GET /api/quizzes` - List all quizzes
- `POST /api/quizzes` - Create new quiz
- `GET /api/quizzes/{id}` - Get quiz details
- `POST /api/quizzes/{id}/submit` - Submit quiz answers

### Admin
- `GET /api/admin/users` - List all users
- `GET /api/admin/analytics` - Get system analytics
- `POST /api/admin/generate-quiz` - AI-powered quiz generation

## 🔒 Security Features

- JWT-based authentication
- Password hashing with Werkzeug
- CORS protection
- Input validation and sanitization
- Security headers in production

## 📱 PWA Features

- Offline capability
- App-like experience
- Push notifications support
- Responsive design for all devices

## 🐳 Docker Services

- **Frontend**: Nginx serving Vue.js app (Port 80)
- **Backend**: Flask API with Gunicorn (Port 8000)
- **Redis**: Message broker for Celery (Port 6379)
- **Celery**: Background task worker

## 📈 Monitoring and Logs

View application logs:
```bash
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f frontend
```

## 🛠 Production Deployment

1. **Set production environment variables**
2. **Use strong SECRET_KEY**
3. **Configure proper email credentials**
4. **Set up SSL/TLS certificates**
5. **Configure domain and DNS**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support and questions, please open an issue on GitHub.

---

**Built with ❤️ using Flask, Vue.js, and modern web technologies**