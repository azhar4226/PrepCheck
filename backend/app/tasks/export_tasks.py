from celery import Celery
import pandas as pd
import os
from datetime import datetime

# Create a dummy celery instance for decoration
celery = Celery('PrepCheck')

@celery.task(bind=True)
def export_admin_data(self, export_type='all'):
    """Export admin data to CSV"""
    try:
        # Import here to avoid circular import
        from app import create_app, db
        from app.models import User, QuizAttempt, Quiz
        
        with create_app().app_context():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_dir = 'exports'
            os.makedirs(export_dir, exist_ok=True)
            
            files_created = []
            
            if export_type in ['users', 'all']:
                # Export users data
                users = User.query.filter_by(is_admin=False).all()
                users_data = []
                
                for user in users:
                    user_dict = user.to_dict()
                    # Add quiz statistics
                    total_attempts = QuizAttempt.query.filter_by(
                        user_id=user.id, is_completed=True
                    ).count()
                    
                    avg_score = 0
                    if total_attempts > 0:
                        attempts = QuizAttempt.query.filter_by(
                            user_id=user.id, is_completed=True
                        ).all()
                        total_percentage = sum(
                            (attempt.score / attempt.total_marks) * 100 
                            for attempt in attempts 
                            if attempt.total_marks > 0
                        )
                        avg_score = round(total_percentage / len(attempts), 2)
                    
                    user_dict.update({
                        'total_attempts': total_attempts,
                        'average_score': avg_score
                    })
                    users_data.append(user_dict)
                
                df_users = pd.DataFrame(users_data)
                users_file = f'{export_dir}/users_{timestamp}.csv'
                df_users.to_csv(users_file, index=False)
                files_created.append(users_file)
                
                self.update_state(
                    state='PROGRESS',
                    meta={'status': 'Users data exported', 'current': 1, 'total': 3}
                )
            
            if export_type in ['quizzes', 'all']:
                # Export quizzes data
                quizzes = Quiz.query.all()
                quizzes_data = []
                
                for quiz in quizzes:
                    quiz_dict = quiz.to_dict()
                    # Add attempt statistics
                    total_attempts = QuizAttempt.query.filter_by(
                        quiz_id=quiz.id, is_completed=True
                    ).count()
                    
                    avg_score = 0
                    if total_attempts > 0:
                        attempts = QuizAttempt.query.filter_by(
                            quiz_id=quiz.id, is_completed=True
                        ).all()
                        total_percentage = sum(
                            (attempt.score / attempt.total_marks) * 100 
                            for attempt in attempts 
                            if attempt.total_marks > 0
                        )
                        avg_score = round(total_percentage / len(attempts), 2)
                    
                    quiz_dict.update({
                        'total_attempts': total_attempts,
                        'average_score': avg_score
                    })
                    quizzes_data.append(quiz_dict)
                
                df_quizzes = pd.DataFrame(quizzes_data)
                quizzes_file = f'{export_dir}/quizzes_{timestamp}.csv'
                df_quizzes.to_csv(quizzes_file, index=False)
                files_created.append(quizzes_file)
                
                self.update_state(
                    state='PROGRESS',
                    meta={'status': 'Quizzes data exported', 'current': 2, 'total': 3}
                )
            
            if export_type in ['attempts', 'all']:
                # Export quiz attempts data
                attempts = QuizAttempt.query.filter_by(is_completed=True).all()
                attempts_data = []
                
                for attempt in attempts:
                    attempt_dict = attempt.to_dict()
                    attempt_dict.update({
                        'user_email': attempt.user.email,
                        'user_name': attempt.user.full_name,
                        'subject_name': attempt.quiz.chapter.subject.name,
                        'chapter_name': attempt.quiz.chapter.name
                    })
                    attempts_data.append(attempt_dict)
                
                df_attempts = pd.DataFrame(attempts_data)
                attempts_file = f'{export_dir}/quiz_attempts_{timestamp}.csv'
                df_attempts.to_csv(attempts_file, index=False)
                files_created.append(attempts_file)
                
                self.update_state(
                    state='PROGRESS',
                    meta={'status': 'Quiz attempts exported', 'current': 3, 'total': 3}
                )
            
            # Create a zip file if multiple files
            if len(files_created) > 1:
                import zipfile
                zip_file = f'{export_dir}/admin_export_{timestamp}.zip'
                with zipfile.ZipFile(zip_file, 'w') as zipf:
                    for file in files_created:
                        zipf.write(file, os.path.basename(file))
                        os.remove(file)  # Remove individual files
                return f'/api/admin/download/{os.path.basename(zip_file)}'
            else:
                return f'/api/admin/download/{os.path.basename(files_created[0])}'
                
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

@celery.task(bind=True)
def export_user_data(self, user_id):
    """Export user's quiz history to CSV"""
    try:
        # Import here to avoid circular import
        from app import create_app, db
        from app.models import User, QuizAttempt
        
        with create_app().app_context():
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_dir = 'exports'
            os.makedirs(export_dir, exist_ok=True)
            
            # Get user's quiz attempts
            attempts = QuizAttempt.query.filter_by(
                user_id=user_id, is_completed=True
            ).order_by(QuizAttempt.completed_at.desc()).all()
            
            attempts_data = []
            for attempt in attempts:
                attempt_dict = attempt.to_dict()
                attempt_dict.update({
                    'subject_name': attempt.quiz.chapter.subject.name,
                    'chapter_name': attempt.quiz.chapter.name,
                    'quiz_title': attempt.quiz.title
                })
                attempts_data.append(attempt_dict)
            
            df_attempts = pd.DataFrame(attempts_data)
            filename = f'user_{user_id}_quiz_history_{timestamp}.csv'
            filepath = f'{export_dir}/{filename}'
            df_attempts.to_csv(filepath, index=False)
            
            return f'/api/user/download/{filename}'
            
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
