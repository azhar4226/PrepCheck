from datetime import datetime, timedelta
import calendar

def send_daily_reminders():
    """Send daily reminders to inactive users and notify about new mock tests"""
    try:
        # Import here to avoid circular import
        from app import create_app, db
        from app.models.models import User, UGCNetMockTest, UGCNetMockAttempt
        from app.utils.email_service import send_email
        
        with create_app().app_context():
            # Find inactive users (no login in last 3 days)
            three_days_ago = datetime.utcnow() - timedelta(days=3)
            inactive_users = User.query.filter(
                User.is_admin == False,
                User.is_active == True,
                User.last_login < three_days_ago
            ).all()
            
            # Find users who haven't attempted mock tests recently
            reminders_sent = 0
            for user in inactive_users:
                last_attempt = UGCNetMockAttempt.query.filter_by(
                    user_id=user.id
                ).order_by(UGCNetMockAttempt.started_at.desc()).first()
                
                if not last_attempt or last_attempt.started_at < three_days_ago:
                    if send_inactivity_reminder(user):
                        reminders_sent += 1
            
            # Notify about new mock tests (created in last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            new_mock_tests = UGCNetMockTest.query.filter(
                UGCNetMockTest.created_at >= yesterday,
                UGCNetMockTest.is_active == True
            ).all()
            
            notifications_sent = 0
            if new_mock_tests:
                active_users = User.query.filter_by(
                    is_admin=False, is_active=True
                ).all()
                
                for user in active_users:
                    if send_new_quiz_notification(user, new_mock_tests):
                        notifications_sent += 1
                    
            return f"Sent reminders to {reminders_sent} inactive users and notified {notifications_sent} users about {len(new_mock_tests)} new mock tests"
        
    except Exception as e:
        return f"Error sending daily reminders: {str(e)}"

def send_monthly_reports():
    """Send monthly activity reports to all users and admin"""
    try:
        # Import here to avoid circular import  
        from app import create_app, db
        from app.models.models import User
        from app.utils.email_service import send_email
        
        with create_app().app_context():
            # Get current month data
            now = datetime.utcnow()
            first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Send user reports
            users = User.query.filter_by(is_admin=False, is_active=True).all()
            user_reports_sent = 0
            
            for user in users:
                monthly_data = get_user_monthly_data(user, first_day, now)
                if send_user_monthly_report(user, monthly_data):
                    user_reports_sent += 1
            
            # Send admin report
            admin_data = get_admin_monthly_data(first_day, now)
            admin_users = User.query.filter_by(is_admin=True, is_active=True).all()
            admin_reports_sent = 0
            
            for admin in admin_users:
                if send_admin_monthly_report(admin, admin_data):
                    admin_reports_sent += 1
                
            return f"Sent monthly reports to {user_reports_sent} users and {admin_reports_sent} admins"
        
    except Exception as e:
        return f"Error sending monthly reports: {str(e)}"

def send_inactivity_reminder(user):
    """Send inactivity reminder email to user"""
    try:
        from app.utils.email_service import send_email
        
        subject = "Don't forget your PrepCheck practice! 📚"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #007bff; margin: 0;">PrepCheck</h1>
                    <p style="color: #666; margin: 5px 0;">Your Exam Preparation Partner</p>
                </div>
                
                <h2 style="color: #333;">Hi {user.full_name}!</h2>
                
                <p style="color: #555; line-height: 1.6;">
                    We noticed you haven't been active on PrepCheck lately. Don't let your momentum slip away! 
                    Consistent practice is key to exam success.
                </p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #007bff; margin-top: 0;">Ready to get back on track?</h3>
                    <ul style="color: #555; line-height: 1.6;">
                        <li>Take a quick quiz to refresh your memory</li>
                        <li>Check out new quizzes that have been added</li>
                        <li>Review your past performance</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/dashboard" 
                       style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Continue Learning
                    </a>
                </div>
                
                <p style="color: #888; font-size: 12px; text-align: center; margin-top: 30px;">
                    If you no longer wish to receive these reminders, you can update your preferences in your account settings.
                </p>
            </div>
        </body>
        </html>
        """
        
        return send_email(user.email, subject, html_content)
    except Exception as e:
        print(f"Error sending inactivity reminder to {user.email}: {str(e)}")
        return False

def send_new_quiz_notification(user, new_mock_tests):
    """Send notification about new UGC NET mock tests"""
    try:
        from app.utils.email_service import send_email
        
        subject = f"🎯 {len(new_mock_tests)} New UGC NET Mock Test{'s' if len(new_mock_tests) > 1 else ''} Available!"
        
        test_list = ""
        for test in new_mock_tests[:5]:  # Show max 5 tests
            test_list += f"""
            <li style="margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                <strong>{test.title}</strong><br>
                <span style="color: #666; font-size: 14px;">
                    {test.subject.name} • {test.total_questions} Questions • {test.time_limit} minutes
                </span>
            </li>
            """
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #007bff; margin: 0;">PrepCheck</h1>
                    <p style="color: #666; margin: 5px 0;">New Content Alert!</p>
                </div>
                
                <h2 style="color: #333;">Hi {user.full_name}!</h2>
                
                <p style="color: #555; line-height: 1.6;">
                    Great news! We've added {len(new_mock_tests)} new UGC NET mock test{'s' if len(new_mock_tests) > 1 else ''} 
                    for you to practice with:
                </p>
                
                <ul style="list-style: none; padding: 0;">
                    {test_list}
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/ugc-net" 
                       style="background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Explore New Mock Tests
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return send_email(user.email, subject, html_content)
    except Exception as e:
        print(f"Error sending new mock test notification to {user.email}: {str(e)}")
        return False

def get_user_monthly_data(user, start_date, end_date):
    """Get user's monthly activity data"""
    try:
        from app.models.models import UGCNetMockAttempt
        
        attempts = UGCNetMockAttempt.query.filter(
            UGCNetMockAttempt.user_id == user.id,
            UGCNetMockAttempt.is_completed == True,
            UGCNetMockAttempt.completed_at >= start_date,
            UGCNetMockAttempt.completed_at < end_date
        ).all()
        
        total_attempts = len(attempts)
        total_score = sum(attempt.marks_obtained for attempt in attempts)
        total_possible = sum(attempt.total_marks for attempt in attempts)
        avg_percentage = round((total_score / total_possible) * 100, 2) if total_possible > 0 else 0
        
        # Time spent
        total_time = sum(attempt.time_taken or 0 for attempt in attempts)
        
        return {
            'total_attempts': total_attempts,
            'avg_percentage': avg_percentage,
            'total_time_minutes': round(total_time / 60, 2) if total_time else 0,
            'best_score': round(max((attempt.score / attempt.total_marks) * 100 for attempt in attempts), 2) if attempts else 0,
            'subjects_practiced': len(set(attempt.quiz.chapter.subject.name for attempt in attempts))
        }
    except Exception as e:
        print(f"Error getting user monthly data: {str(e)}")
        return {
            'total_attempts': 0,
            'avg_percentage': 0,
            'total_time_minutes': 0,
            'best_score': 0,
            'subjects_practiced': 0
        }

def get_admin_monthly_data(start_date, end_date):
    """Get admin's monthly system data"""
    try:
        from app.models.models import User, UGCNetMockAttempt
        
        new_users = User.query.filter(
            User.is_admin == False,
            User.created_at >= start_date,
            User.created_at < end_date
        ).count()
        
        total_attempts = UGCNetMockAttempt.query.filter(
            UGCNetMockAttempt.is_completed == True,
            UGCNetMockAttempt.completed_at >= start_date,
            UGCNetMockAttempt.completed_at < end_date
        ).count()
        
        active_users = User.query.filter(
            User.is_admin == False,
            User.last_login >= start_date
        ).count()
        
        return {
            'new_users': new_users,
            'total_attempts': total_attempts,
            'active_users': active_users,
            'month_name': calendar.month_name[start_date.month],
            'year': start_date.year
        }
    except Exception as e:
        print(f"Error getting admin monthly data: {str(e)}")
        return {
            'new_users': 0,
            'total_attempts': 0,
            'active_users': 0,
            'month_name': calendar.month_name[datetime.now().month],
            'year': datetime.now().year
        }

def send_user_monthly_report(user, data):
    """Send monthly report to user"""
    try:
        from app.utils.email_service import send_email
        
        subject = f"📊 Your PrepCheck Monthly Report - {calendar.month_name[datetime.now().month]}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #007bff; margin: 0;">PrepCheck</h1>
                    <p style="color: #666; margin: 5px 0;">Monthly Progress Report</p>
                </div>
                
                <h2 style="color: #333;">Hi {user.full_name}!</h2>
                
                <p style="color: #555; line-height: 1.6;">
                    Here's your learning progress for {calendar.month_name[datetime.now().month]}:
                </p>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0;">
                    <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; text-align: center;">
                        <h3 style="color: #1976d2; margin: 0; font-size: 36px;">{data['total_attempts']}</h3>
                        <p style="color: #1976d2; margin: 5px 0;">Quizzes Attempted</p>
                    </div>
                    
                    <div style="background-color: #e8f5e8; padding: 20px; border-radius: 10px; text-align: center;">
                        <h3 style="color: #388e3c; margin: 0; font-size: 36px;">{data['avg_percentage']}%</h3>
                        <p style="color: #388e3c; margin: 5px 0;">Average Score</p>
                    </div>
                    
                    <div style="background-color: #fff3e0; padding: 20px; border-radius: 10px; text-align: center;">
                        <h3 style="color: #f57c00; margin: 0; font-size: 36px;">{data['total_time_minutes']}</h3>
                        <p style="color: #f57c00; margin: 5px 0;">Minutes Practiced</p>
                    </div>
                    
                    <div style="background-color: #fce4ec; padding: 20px; border-radius: 10px; text-align: center;">
                        <h3 style="color: #c2185b; margin: 0; font-size: 36px;">{data['subjects_practiced']}</h3>
                        <p style="color: #c2185b; margin: 5px 0;">Subjects Covered</p>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/dashboard" 
                       style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Full Dashboard
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return send_email(user.email, subject, html_content)
    except Exception as e:
        print(f"Error sending monthly report to {user.email}: {str(e)}")
        return False

def send_admin_monthly_report(admin, data):
    """Send monthly report to admin"""
    try:
        from app.utils.email_service import send_email
        
        subject = f"📈 PrepCheck System Report - {data['month_name']} {data['year']}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #007bff; margin: 0;">PrepCheck Admin</h1>
                    <p style="color: #666; margin: 5px 0;">Monthly System Report</p>
                </div>
                
                <h2 style="color: #333;">System Overview - {data['month_name']} {data['year']}</h2>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin: 30px 0;">
                    <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; text-align: center;">
                        <h3 style="color: #1976d2; margin: 0; font-size: 32px;">{data['new_users']}</h3>
                        <p style="color: #1976d2; margin: 5px 0;">New Users</p>
                    </div>
                    
                    <div style="background-color: #e8f5e8; padding: 20px; border-radius: 10px; text-align: center;">
                        <h3 style="color: #388e3c; margin: 0; font-size: 32px;">{data['active_users']}</h3>
                        <p style="color: #388e3c; margin: 5px 0;">Active Users</p>
                    </div>
                    
                    <div style="background-color: #fff3e0; padding: 20px; border-radius: 10px; text-align: center;">
                        <h3 style="color: #f57c00; margin: 0; font-size: 32px;">{data['total_attempts']}</h3>
                        <p style="color: #f57c00; margin: 5px 0;">Quiz Attempts</p>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/admin/dashboard" 
                       style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Admin Dashboard
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return send_email(admin.email, subject, html_content)
    except Exception as e:
        print(f"Error sending admin monthly report to {admin.email}: {str(e)}")
        return False
