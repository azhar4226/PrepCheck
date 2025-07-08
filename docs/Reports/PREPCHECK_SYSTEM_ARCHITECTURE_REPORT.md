# PrepCheck System Architecture Report

## Executive Summary

PrepCheck is a comprehensive web-based exam preparation platform designed for multi-user environments with AI-powered question generation, focusing primarily on UGC NET examination preparation. The system provides both practice tests and full mock examinations with detailed analytics, performance tracking, and adaptive learning features.

## 1. System Overview

### 1.1 Project Vision
PrepCheck serves as a modern, scalable exam preparation platform that combines traditional question banks with AI-generated content to provide comprehensive learning experiences. The system transitioned from a generic quiz platform to a specialized UGC NET preparation tool.

### 1.2 Core Features
- **User Management**: Role-based authentication (Admin/Student)
- **Question Bank**: Comprehensive question repository with AI verification
- **Practice Tests**: Chapter-wise focused practice sessions
- **Mock Tests**: Full UGC NET simulation with Paper 1 & Paper 2
- **AI Integration**: Google Gemini AI for question generation and verification
- **Analytics**: Performance tracking, progress monitoring, and recommendations
- **Real-time Updates**: Background task processing with Celery

### 1.3 Technology Stack

#### Backend
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Task Queue**: Celery with Redis
- **AI Integration**: Google Gemini API
- **Email**: Flask-Mail for notifications

#### Frontend
- **Framework**: Vue.js 3 with Composition API
- **Routing**: Vue Router 4
- **Styling**: Bootstrap 5 with custom CSS
- **Charts**: Chart.js for analytics visualization
- **HTTP Client**: Axios for API communication

#### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (reverse proxy)
- **Message Broker**: Redis
- **File Storage**: Local file system with configurable paths

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  Vue.js Frontend (Port 3000)                                   │
│  ├── Views (Pages)                                             │
│  ├── Components (Reusable)                                     │
│  ├── Services (API Communication)                              │
│  ├── Router (Navigation)                                       │
│  └── Composables (Shared Logic)                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  Nginx Reverse Proxy                                           │
│  ├── Static File Serving                                       │
│  ├── Request Routing                                           │
│  ├── Load Balancing                                            │
│  └── SSL Termination                                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  Flask Backend (Port 8000)                                     │
│  ├── Controllers (API Endpoints)                               │
│  ├── Services (Business Logic)                                 │
│  ├── Models (Data Layer)                                       │
│  ├── Middleware (Auth, CORS, etc.)                             │
│  └── Extensions (JWT, Mail, etc.)                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  SQLAlchemy ORM                                                 │
│  ├── Database (SQLite/PostgreSQL)                              │
│  ├── Migrations (Alembic)                                      │
│  ├── Models (User, Subject, Question, etc.)                    │
│  └── Relationships (Foreign Keys, Joins)                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                          │
├─────────────────────────────────────────────────────────────────┤
│  ├── Google Gemini AI (Question Generation)                    │
│  ├── Redis (Task Queue & Caching)                              │
│  ├── Celery Workers (Background Tasks)                         │
│  ├── SMTP Server (Email Notifications)                         │
│  └── File System (Uploads & Static Files)                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow Architecture

```
┌─────────────┐    HTTP/HTTPS    ┌─────────────┐    SQL Queries    ┌─────────────┐
│   Browser   │ ────────────────▶│   Flask     │ ────────────────▶ │  Database   │
│   (Vue.js)  │                  │   Backend   │                   │ (SQLAlchemy)│
└─────────────┘                  └─────────────┘                   └─────────────┘
       │                                │                                  │
       │                                │                                  │
       ▼                                ▼                                  ▼
┌─────────────┐    WebSocket/SSE  ┌─────────────┐    Task Queue     ┌─────────────┐
│Real-time UI │ ◀────────────────│   Celery    │ ◀────────────────│    Redis    │
│   Updates   │                  │   Workers   │                   │   Message   │
└─────────────┘                  └─────────────┘                   │   Broker    │
                                         │                          └─────────────┘
                                         │
                                         ▼
                                 ┌─────────────┐
                                 │  External   │
                                 │   APIs      │
                                 │ (Gemini AI) │
                                 └─────────────┘
```

## 3. Database Schema

### 3.1 Entity Relationship Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│      Users      │     │    Subjects     │     │    Chapters     │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │     │ id (PK)         │
│ email           │     │ name            │     │ name            │
│ password_hash   │     │ description     │     │ description     │
│ full_name       │     │ subject_code    │     │ subject_id (FK) │
│ is_admin        │     │ paper_type      │     │ weightage_p1    │
│ profile_data    │     │ total_marks_p1  │     │ weightage_p2    │
│ created_at      │     │ total_marks_p2  │     │ chapter_order   │
│ ...             │     │ ...             │     │ ...             │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                        │                        │
         │                        │                        │
         │                        └──────────┐             │
         │                                   │             │
         │                                   ▼             │
         │                        ┌─────────────────┐      │
         │                        │ QuestionBank    │      │
         │                        ├─────────────────┤      │
         │                        │ id (PK)         │      │
         │                        │ question_text   │      │
         │                        │ option_a        │      │
         │                        │ option_b        │      │
         │                        │ option_c        │      │
         │                        │ option_d        │      │
         │                        │ correct_option  │      │
         │                        │ explanation     │      │
         │                        │ paper_type      │      │
         │                        │ difficulty      │      │
         │                        │ chapter_id (FK) │◀─────┘
         │                        │ verified_by(FK) │
         │                        │ ...             │
         │                        └─────────────────┘
         │                                   │
         │                                   │
         │                 ┌─────────────────┴─────────────────┐
         │                 │                                   │
         │                 ▼                                   ▼
         │        ┌─────────────────┐                ┌─────────────────┐
         │        │UGCNetMockTests  │                │UGCNetMockAttempt│
         │        ├─────────────────┤                ├─────────────────┤
         │        │ id (PK)         │                │ id (PK)         │
         │        │ title           │                │ user_id (FK)    │◀─┐
         │        │ subject_id (FK) │                │ mock_test_id(FK)│  │
         │        │ paper_type      │                │ status          │  │
         │        │ total_questions │                │ score           │  │
         │        │ time_limit      │                │ percentage      │  │
         │        │ weightage_config│                │ start_time      │  │
         │        │ ...             │                │ end_time        │  │
         │        └─────────────────┘                │ answers_data    │  │
         │                                           │ analytics       │  │
         │                                           │ ...             │  │
         │                                           └─────────────────┘  │
         │                                                                │
         │                                                                │
         │                 ┌─────────────────┐                           │
         │                 │UGCNetPractice   │                           │
         │                 │Attempts         │                           │
         │                 ├─────────────────┤                           │
         │                 │ id (PK)         │                           │
         │                 │ user_id (FK)    │◀──────────────────────────┘
         │                 │ subject_id (FK) │
         │                 │ title           │
         │                 │ paper_type      │
         │                 │ practice_type   │
         │                 │ selected_chaps  │
         │                 │ total_questions │
         │                 │ status          │
         │                 │ score           │
         │                 │ percentage      │
         │                 │ questions_data  │
         │                 │ answers_data    │
         │                 │ analytics       │
         │                 │ ...             │
         │                 └─────────────────┘
         │
         └─────────────────┐
                           │
                           ▼
                  ┌─────────────────┐
                  │ StudyMaterials  │
                  ├─────────────────┤
                  │ id (PK)         │
                  │ title           │
                  │ description     │
                  │ content         │
                  │ material_type   │
                  │ file_path       │
                  │ chapter_id (FK) │
                  │ created_by (FK) │
                  │ ...             │
                  └─────────────────┘
```

### 3.2 Key Database Models

#### User Model
- **Purpose**: Stores user accounts and profiles
- **Key Fields**: email, password_hash, full_name, is_admin, profile_data
- **Relationships**: Has many mock attempts, practice attempts, study materials

#### Subject Model
- **Purpose**: Represents exam subjects (e.g., Computer Science, English)
- **Key Fields**: name, subject_code, paper_type, total_marks
- **UGC NET Features**: Separate marks and duration for Paper 1 & Paper 2

#### Chapter Model
- **Purpose**: Subject subdivisions with weightage information
- **Key Fields**: name, subject_id, weightage_paper1, weightage_paper2
- **UGC NET Features**: Weightage system for question distribution

#### QuestionBank Model
- **Purpose**: Comprehensive question repository with AI verification
- **Key Fields**: question_text, options, correct_option, explanation, verification_data
- **AI Features**: Verification status, confidence scores, source tracking

#### UGCNetMockTest Model
- **Purpose**: Mock test configurations with weightage systems
- **Key Fields**: title, subject_id, paper_type, total_questions, weightage_config
- **Features**: Configurable question distribution and difficulty levels

#### UGCNetMockAttempt Model
- **Purpose**: Tracks user attempts at mock tests
- **Key Fields**: user_id, mock_test_id, score, percentage, analytics
- **Analytics**: Chapter-wise performance, time tracking, qualification status

#### UGCNetPracticeAttempt Model
- **Purpose**: Tracks focused practice sessions
- **Key Fields**: user_id, subject_id, selected_chapters, practice_type
- **Features**: Chapter selection, custom difficulty distribution

## 4. API Architecture

### 4.1 API Design Principles
- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Communication**: All requests and responses use JSON
- **JWT Authentication**: Stateless authentication with tokens
- **Error Handling**: Consistent error response format
- **CORS Support**: Cross-origin resource sharing enabled

### 4.2 API Endpoints Structure

```
/api/auth/
├── POST /register          # User registration
├── POST /login             # User authentication
├── POST /logout            # User logout
├── GET  /profile           # Get user profile
└── PUT  /profile           # Update user profile

/api/admin/
├── GET  /dashboard         # Admin dashboard stats
├── GET  /users             # List all users
├── POST /users             # Create new user
├── PUT  /users/:id         # Update user
├── DELETE /users/:id       # Delete user
├── GET  /subjects          # List subjects
├── POST /subjects          # Create subject
├── PUT  /subjects/:id      # Update subject
├── DELETE /subjects/:id    # Delete subject
└── GET  /analytics         # System analytics

/api/admin/question-bank/
├── GET    /                # List questions
├── POST   /                # Create question
├── PUT    /:id             # Update question
├── DELETE /:id             # Delete question
├── POST   /bulk-import     # Import questions
└── GET    /export          # Export questions

/api/ugc-net/
├── GET  /subjects          # List UGC NET subjects
├── GET  /subjects/:id/chapters # Get subject chapters
├── POST /practice-tests    # Create practice test
├── GET  /practice-tests/:id # Get practice test
├── POST /practice-tests/:id/start # Start practice test
├── PUT  /practice-tests/:id/submit # Submit practice test
├── POST /mock-tests        # Create mock test
├── GET  /mock-tests/:id    # Get mock test
├── POST /mock-tests/:id/start # Start mock test
└── PUT  /mock-tests/:id/submit # Submit mock test

/api/ai/
├── POST /generate-questions # Generate AI questions
├── GET  /verification/:id   # Check verification status
├── POST /verify-questions   # Verify question batch
└── GET  /ai-status          # AI service status

/api/user/
├── GET  /dashboard         # User dashboard
├── GET  /history           # Attempt history
├── GET  /analytics         # User analytics
├── GET  /profile           # User profile
└── PUT  /profile           # Update profile

/api/notifications/
├── GET  /                  # List notifications
├── POST /                  # Create notification
├── PUT  /:id/read          # Mark as read
└── DELETE /:id             # Delete notification
```

### 4.3 Authentication Flow

```
┌─────────────┐    1. Login Request    ┌─────────────┐
│   Client    │ ─────────────────────▶ │   Server    │
│  (Vue.js)   │                        │   (Flask)   │
└─────────────┘                        └─────────────┘
       │                                       │
       │                                       │ 2. Validate
       │                                       │ Credentials
       │                                       ▼
       │                                ┌─────────────┐
       │                                │  Database   │
       │                                └─────────────┘
       │                                       │
       │           3. JWT Token                │
       │ ◀─────────────────────────────────────┘
       │
       │    4. Store Token (localStorage)
       ▼
┌─────────────┐    5. Authenticated    ┌─────────────┐
│ Local       │       Requests         │   Server    │
│ Storage     │ ─────────────────────▶ │ (Headers:   │
└─────────────┘                        │ Authorization)
                                       └─────────────┘
```

## 5. Frontend Architecture

### 5.1 Vue.js Application Structure

```
src/
├── main.js                 # Application entry point
├── App.vue                 # Root component
├── router/
│   └── index.js           # Route definitions
├── views/                 # Page components
│   ├── auth/              # Authentication pages
│   │   ├── Login.vue
│   │   └── Register.vue
│   ├── admin/             # Admin management
│   │   ├── Dashboard.vue
│   │   ├── UserManagement.vue
│   │   ├── SubjectManagement.vue
│   │   ├── QuestionManagement.vue
│   │   └── Analytics.vue
│   ├── ugc-net/           # UGC NET specific views
│   │   ├── Dashboard.vue
│   │   ├── TestGenerator.vue
│   │   ├── TestTaking.vue
│   │   └── TestResults.vue
│   └── user/              # User-specific views
│       ├── Dashboard.vue
│       ├── Profile.vue
│       └── History.vue
├── components/            # Reusable components
│   ├── common/           # Common UI components
│   │   ├── DataTable.vue
│   │   ├── Modal.vue
│   │   ├── Loading.vue
│   │   └── ErrorMessage.vue
│   ├── forms/            # Form components
│   │   ├── QuestionForm.vue
│   │   ├── SubjectForm.vue
│   │   └── UserForm.vue
│   └── charts/           # Chart components
│       ├── PerformanceChart.vue
│       ├── AnalyticsChart.vue
│       └── ProgressChart.vue
├── services/             # API services
│   ├── api.js            # Base API client
│   ├── adminService.js   # Admin API calls
│   ├── ugcNetService.js  # UGC NET API calls
│   ├── authService.js    # Authentication
│   └── userService.js    # User operations
├── composables/          # Vue 3 composables
│   ├── useAuth.js        # Authentication logic
│   ├── useApi.js         # API communication
│   ├── useNotifications.js # Notification system
│   └── useAnalytics.js   # Analytics data
└── assets/               # Static assets
    ├── styles/           # CSS files
    ├── images/           # Image assets
    └── icons/            # Icon assets
```

### 5.2 State Management

PrepCheck uses Vue 3's Composition API with composables for state management instead of Vuex:

```javascript
// useAuth.js - Authentication state
export function useAuth() {
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.is_admin || false)
  
  const login = async (credentials) => {
    // Login logic
  }
  
  const logout = () => {
    // Logout logic
  }
  
  return {
    user,
    isAuthenticated,
    isAdmin,
    login,
    logout
  }
}
```

### 5.3 Component Communication

```
┌─────────────────┐    Props    ┌─────────────────┐
│   Parent        │ ──────────▶ │   Child         │
│   Component     │             │   Component     │
└─────────────────┘             └─────────────────┘
         │                               │
         │                               │
         │              Events           │
         │ ◀─────────────────────────────┘
         │
         │    Provide/Inject (Global State)
         ▼
┌─────────────────┐             ┌─────────────────┐
│   Composable    │ ◀─────────▶ │   Composable    │
│   (useAuth)     │             │   (useApi)      │
└─────────────────┘             └─────────────────┘
```

## 6. Business Logic Flow

### 6.1 User Registration & Authentication Flow

```
┌─────────────┐
│   Start     │
└─────────────┘
       │
       ▼
┌─────────────┐
│ User visits │
│ /register   │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Fill form & │
│ submit      │
└─────────────┘
       │
       ▼
┌─────────────┐    No     ┌─────────────┐
│ Validate    │ ────────▶ │ Show error  │
│ input       │           │ message     │
└─────────────┘           └─────────────┘
       │ Yes                     │
       ▼                         │
┌─────────────┐                  │
│ Check email │                  │
│ uniqueness  │                  │
└─────────────┘                  │
       │                         │
       ▼                         │
┌─────────────┐    No             │
│ Email       │ ──────────────────┘
│ available?  │
└─────────────┘
       │ Yes
       ▼
┌─────────────┐
│ Hash        │
│ password    │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Create user │
│ in database │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Generate    │
│ JWT token   │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Return user │
│ data & token│
└─────────────┘
       │
       ▼
┌─────────────┐
│ Redirect to │
│ dashboard   │
└─────────────┘
```

### 6.2 UGC NET Practice Test Flow

```
┌─────────────┐
│ User selects│
│ UGC NET     │
│ Practice    │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Choose      │
│ Subject     │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Select      │
│ Chapters    │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Configure   │
│ Test        │
│ Parameters  │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Generate    │
│ Questions   │
│ (AI Service)│
└─────────────┘
       │
       ▼
┌─────────────┐
│ Create      │
│ Practice    │
│ Attempt     │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Display     │
│ Questions   │
│ Interface   │
└─────────────┘
       │
       ▼
┌─────────────┐
│ User        │
│ Answers     │
│ Questions   │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Auto-save   │
│ Progress    │
│ (Background)│
└─────────────┘
       │
       ▼
┌─────────────┐
│ Submit      │
│ Test        │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Calculate   │
│ Score &     │
│ Analytics   │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Generate    │
│ Performance │
│ Report      │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Store       │
│ Results &   │
│ Analytics   │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Display     │
│ Results     │
│ Page        │
└─────────────┘
```

### 6.3 AI Question Generation Flow

```
┌─────────────┐
│ Admin       │
│ requests    │
│ AI questions│
└─────────────┘
       │
       ▼
┌─────────────┐
│ Validate    │
│ parameters  │
│ (topic, etc)│
└─────────────┘
       │
       ▼
┌─────────────┐
│ Create      │
│ Celery task │
│ (background)│
└─────────────┘
       │
       ▼
┌─────────────┐
│ Generate    │
│ prompt for  │
│ Gemini AI   │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Call        │
│ Gemini API  │
└─────────────┘
       │
       ▼
┌─────────────┐    Error    ┌─────────────┐
│ Parse AI    │ ──────────▶ │ Log error & │
│ response    │             │ retry       │
└─────────────┘             └─────────────┘
       │ Success
       ▼
┌─────────────┐
│ Extract     │
│ questions   │
│ from JSON   │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Validate    │
│ question    │
│ format      │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Generate    │
│ content     │
│ hash        │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Store in    │
│ question    │
│ bank        │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Verify      │
│ questions   │
│ (AI)        │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Update      │
│ verification│
│ status      │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Notify      │
│ admin of    │
│ completion  │
└─────────────┘
```

## 7. Security Architecture

### 7.1 Authentication & Authorization

```
┌─────────────┐
│ User Login  │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Validate    │
│ Credentials │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Generate    │
│ JWT Token   │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Token       │
│ contains:   │
│ - User ID   │
│ - Role      │
│ - Expiry    │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Client      │
│ stores      │
│ token       │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Include     │
│ token in    │
│ API headers │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Server      │
│ validates   │
│ token       │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Authorize   │
│ based on    │
│ user role   │
└─────────────┘
```

### 7.2 Data Protection

- **Password Security**: Werkzeug password hashing
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **XSS Protection**: Vue.js automatic escaping
- **CSRF Protection**: JWT tokens prevent CSRF attacks
- **Input Validation**: Server-side validation for all inputs
- **File Upload Security**: Restricted file types and sizes

### 7.3 API Security

```python
# Example JWT protection decorator
@jwt_required()
def protected_endpoint():
    current_user = get_jwt_identity()
    return jsonify(message="Access granted")

# Role-based access control
@admin_required
def admin_only_endpoint():
    return jsonify(message="Admin access granted")
```

## 8. Performance & Scalability

### 8.1 Performance Optimizations

- **Database Indexing**: Proper indexes on frequently queried fields
- **Query Optimization**: Efficient SQLAlchemy queries with eager loading
- **Caching**: Redis caching for frequently accessed data
- **Background Tasks**: Celery for heavy operations (AI generation)
- **Connection Pooling**: Database connection pooling
- **Static File Optimization**: Nginx serves static files directly

### 8.2 Scalability Considerations

```
┌─────────────┐    Load Balancer    ┌─────────────┐
│   Client    │ ─────────────────▶  │   Nginx     │
└─────────────┘                     └─────────────┘
                                           │
                                           ▼
                                  ┌─────────────┐
                                  │   Flask     │
                                  │ App Server  │
                                  │  (Multiple  │
                                  │ Instances)  │
                                  └─────────────┘
                                           │
                                           ▼
                                  ┌─────────────┐
                                  │  Database   │
                                  │  (Primary/  │
                                  │  Replica)   │
                                  └─────────────┘
```

### 8.3 Background Task Processing

```
┌─────────────┐    Task Queue    ┌─────────────┐
│   Flask     │ ───────────────▶ │    Redis    │
│   App       │                  │   Queue     │
└─────────────┘                  └─────────────┘
                                        │
                                        ▼
                                 ┌─────────────┐
                                 │   Celery    │
                                 │   Workers   │
                                 │ (Multiple   │
                                 │ Processes)  │
                                 └─────────────┘
                                        │
                                        ▼
                                 ┌─────────────┐
                                 │  External   │
                                 │   APIs      │
                                 │ (Gemini AI) │
                                 └─────────────┘
```

## 9. Deployment Architecture

### 9.1 Docker Container Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                         Docker Host                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Frontend  │  │   Backend   │  │   Celery    │              │
│  │  Container  │  │  Container  │  │  Container  │              │
│  │             │  │             │  │             │              │
│  │  Vue.js     │  │  Flask      │  │  Worker     │              │
│  │  Nginx      │  │  App        │  │  Process    │              │
│  │  Port 3000  │  │  Port 8000  │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │    Redis    │  │  Database   │                               │
│  │  Container  │  │  Volume     │                               │
│  │             │  │             │                               │
│  │  Message    │  │  SQLite/    │                               │
│  │  Broker     │  │  PostgreSQL │                               │
│  │  Port 6379  │  │             │                               │
│  └─────────────┘  └─────────────┘                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Production Deployment

```yaml
# docker-compose.yml structure
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
  
  backend:
    build: ./backend
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://...
    depends_on:
      - database
      - redis
  
  frontend:
    build: ./frontend
    environment:
      - NODE_ENV=production
      - VITE_API_URL=https://api.prepcheck.com
  
  celery:
    build: ./backend
    command: celery -A celery_app worker
    depends_on:
      - redis
      - database
  
  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data
  
  database:
    image: postgres:13
    environment:
      - POSTGRES_DB=prepcheck
      - POSTGRES_USER=prepcheck
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## 10. Monitoring & Logging

### 10.1 Application Monitoring

```
┌─────────────┐    Logs     ┌─────────────┐    Alerts    ┌─────────────┐
│   Flask     │ ──────────▶ │   Logging   │ ───────────▶ │   Admin     │
│   App       │             │   System    │              │   Dashboard │
└─────────────┘             └─────────────┘              └─────────────┘
       │                            │
       │                            │
       ▼                            ▼
┌─────────────┐             ┌─────────────┐
│   Celery    │             │   Log       │
│   Workers   │             │   Files     │
└─────────────┘             └─────────────┘
       │                            │
       │                            │
       ▼                            ▼
┌─────────────┐             ┌─────────────┐
│   Database  │             │   Metrics   │
│   Queries   │             │   Collection│
└─────────────┘             └─────────────┘
```

### 10.2 Error Handling

```python
# Global error handler
@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Unhandled error: {error}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': str(error) if app.debug else 'An error occurred'
    }), 500
```

## 11. Testing Strategy

### 11.1 Testing Pyramid

```
                    ┌─────────────┐
                    │   E2E Tests │
                    │   (Cypress) │
                    └─────────────┘
                          │
                   ┌─────────────┐
                   │Integration  │
                   │   Tests     │
                   │  (Pytest)   │
                   └─────────────┘
                          │
                   ┌─────────────┐
                   │   Unit      │
                   │   Tests     │
                   │ (Jest/PyTest)│
                   └─────────────┘
```

### 11.2 Test Categories

#### Backend Tests
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Database Tests**: Model and query testing
- **Service Tests**: Business logic testing

#### Frontend Tests
- **Component Tests**: Vue component testing
- **Service Tests**: API service testing
- **E2E Tests**: User workflow testing

## 12. Development Workflow

### 12.1 Git Workflow

```
┌─────────────┐    Feature    ┌─────────────┐    PR       ┌─────────────┐
│   Main      │    Branch     │   Feature   │   Review    │   Main      │
│   Branch    │ ────────────▶ │   Branch    │ ──────────▶ │   Branch    │
└─────────────┘               └─────────────┘             └─────────────┘
       │                             │                           │
       │                             │                           │
       ▼                             ▼                           ▼
┌─────────────┐               ┌─────────────┐             ┌─────────────┐
│  Production │               │Development  │             │  Production │
│  Deployment │               │   & Testing │             │  Deployment │
└─────────────┘               └─────────────┘             └─────────────┘
```

### 12.2 Development Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd PrepCheck

# Set up environment
cp .env.example .env
cp backend/.env.example backend/.env

# Start development environment
./dev-setup.sh

# Or manually
docker-compose up -d
```

## 13. Future Enhancements

### 13.1 Planned Features

1. **Mobile Application**: React Native mobile app
2. **Advanced Analytics**: Machine learning-based performance prediction
3. **Collaborative Features**: Study groups and peer learning
4. **Gamification**: Achievements, leaderboards, and rewards
5. **Multi-language Support**: International exam support
6. **Advanced AI**: Custom AI models for specific domains
7. **Video Integration**: Video explanations and tutorials
8. **Offline Mode**: Progressive Web App capabilities

### 13.2 Technical Improvements

1. **Microservices Architecture**: Break down monolithic structure
2. **GraphQL API**: More efficient data fetching
3. **Real-time Features**: WebSocket integration
4. **Advanced Caching**: Redis cluster and CDN integration
5. **Performance Monitoring**: APM tools integration
6. **Automated Testing**: CI/CD pipeline improvements
7. **Security Enhancements**: OAuth integration, 2FA
8. **Scalability**: Kubernetes deployment

## 14. Conclusion

PrepCheck represents a comprehensive, modern approach to exam preparation platforms. The system successfully combines traditional educational methodologies with cutting-edge AI technology to provide a personalized, efficient, and scalable learning experience.

### Key Strengths:
- **Modular Architecture**: Easy to maintain and extend
- **AI Integration**: Intelligent question generation and verification
- **User Experience**: Intuitive interface with detailed analytics
- **Scalability**: Docker-based deployment with background task processing
- **Security**: Robust authentication and data protection

### Architecture Benefits:
- **Separation of Concerns**: Clear boundaries between frontend, backend, and data layers
- **API-First Design**: RESTful architecture enables future mobile apps
- **Background Processing**: Celery ensures responsive user experience
- **Database Design**: Efficient schema supports complex educational workflows
- **Deployment Ready**: Docker containerization for production environments

The system is well-positioned for future growth and can serve as a foundation for various educational technology initiatives. The migration from generic quiz terminology to specialized UGC NET preparation demonstrates the platform's adaptability and focus on user needs.

---

*This document serves as a comprehensive guide for developers, administrators, and stakeholders working with the PrepCheck platform. It should be updated as the system evolves and new features are added.*
