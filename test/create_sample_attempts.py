from app import create_app
from app import db
from app.models import User, Quiz, QuizAttempt
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    # Get existing users and quizzes
    users = User.query.filter_by(is_admin=False).all()
    quizzes = Quiz.query.all()
    
    if not users:
        print("No users found. Creating a test user...")
        from werkzeug.security import generate_password_hash
        test_user = User(
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            full_name='Test User'
        )
        db.session.add(test_user)
        db.session.commit()
        users = [test_user]
    
    if not quizzes:
        print("No quizzes found. Please create some quizzes first.")
        exit()
    
    print(f"Found {len(users)} users and {len(quizzes)} quizzes")
    
    # Create sample quiz attempts over the last 7 days
    attempts_created = 0
    
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        attempts_per_day = random.randint(2, 8)
        
        for j in range(attempts_per_day):
            user = random.choice(users)
            quiz = random.choice(quizzes)
            
            # Generate random score (weighted towards higher scores)
            score = random.choices(
                range(40, 101),
                weights=[1]*20 + [2]*20 + [3]*21,  # Higher weight for scores 80-100
                k=1
            )[0]
            
            # Random time for the day
            attempt_time = date.replace(
                hour=random.randint(8, 20),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            
            # Check if attempt already exists for this user/quiz/day
            existing = QuizAttempt.query.filter(
                QuizAttempt.user_id == user.id,
                QuizAttempt.quiz_id == quiz.id,
                QuizAttempt.started_at >= date.date(),
                QuizAttempt.started_at < date.date() + timedelta(days=1)
            ).first()
            
            if not existing:
                attempt = QuizAttempt(
                    user_id=user.id,
                    quiz_id=quiz.id,
                    started_at=attempt_time,
                    completed_at=attempt_time + timedelta(minutes=random.randint(10, 45)),
                    score=score,
                    is_completed=True
                )
                db.session.add(attempt)
                attempts_created += 1
    
    db.session.commit()
    print(f"✅ Created {attempts_created} sample quiz attempts over the last 7 days")
    
    # Print summary
    total_attempts = QuizAttempt.query.filter_by(is_completed=True).count()
    high_scorers = QuizAttempt.query.filter(
        QuizAttempt.score >= 80,
        QuizAttempt.is_completed == True
    ).count()
    
    print(f"📊 Analytics Summary:")
    print(f"   - Total completed attempts: {total_attempts}")
    print(f"   - High scorers (80%+): {high_scorers}")
    print(f"   - Average score: {sum([a.score for a in QuizAttempt.query.filter_by(is_completed=True).all() if a.score]) / max(1, QuizAttempt.query.filter_by(is_completed=True).count()):.1f}%")
