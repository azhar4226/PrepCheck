import csv
import os
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def export_admin_data(export_type='analytics'):
    """Export admin data to CSV or JSON"""
    try:
        # Import here to avoid circular import
        from app import create_app, db
        from app.models.models import User, QuizAttempt, Quiz, Subject, Chapter
        
        with create_app().app_context():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_dir = 'exports'
            os.makedirs(export_dir, exist_ok=True)
            
            files_created = []
            
            if export_type == 'analytics':
                # Export analytics data as JSON
                analytics_data = {
                    'export_timestamp': timestamp,
                    'export_type': 'analytics',
                    'summary': {
                        'total_users': User.query.filter_by(is_admin=False).count(),
                        'total_quizzes': Quiz.query.filter_by(is_active=True).count(),
                        'total_attempts': QuizAttempt.query.filter_by(is_completed=True).count(),
                    },
                    'users': [],
                    'quiz_attempts': [],
                    'subject_performance': []
                }
                
                # Export user data
                users = User.query.filter_by(is_admin=False).all()
                for user in users:
                    user_attempts = QuizAttempt.query.filter_by(
                        user_id=user.id, 
                        is_completed=True
                    ).count()
                    user_avg_score = db.session.query(db.func.avg(QuizAttempt.score)).filter_by(
                        user_id=user.id,
                        is_completed=True
                    ).scalar() or 0
                    
                    analytics_data['users'].append({
                        'id': user.id,
                        'full_name': user.full_name,
                        'email': user.email,
                        'total_attempts': user_attempts,
                        'average_score': round(float(user_avg_score), 2),
                        'created_at': user.created_at.isoformat() if user.created_at else None,
                        'last_login': user.last_login.isoformat() if user.last_login else None
                    })
                
                # Export quiz attempts data
                attempts = QuizAttempt.query.filter_by(is_completed=True).order_by(
                    QuizAttempt.completed_at.desc()
                ).limit(100).all()  # Last 100 attempts
                
                for attempt in attempts:
                    analytics_data['quiz_attempts'].append({
                        'id': attempt.id,
                        'user_name': attempt.user.full_name if attempt.user else 'Unknown',
                        'quiz_title': attempt.quiz.title if attempt.quiz else 'Unknown',
                        'score': attempt.score,
                        'started_at': attempt.started_at.isoformat() if attempt.started_at else None,
                        'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None
                    })
                
                # Export subject performance
                subjects = Subject.query.filter_by(is_active=True).all()
                for subject in subjects:
                    subject_attempts = db.session.query(QuizAttempt).join(Quiz).join(Chapter).filter(
                        Chapter.subject_id == subject.id,
                        QuizAttempt.is_completed == True
                    ).all()
                    
                    if subject_attempts:
                        subject_scores = [attempt.score for attempt in subject_attempts if attempt.score is not None]
                        analytics_data['subject_performance'].append({
                            'subject_name': subject.name,
                            'total_attempts': len(subject_attempts),
                            'average_score': round(sum(subject_scores) / len(subject_scores), 2) if subject_scores else 0
                        })
                
                # Save as JSON
                json_file = f'{export_dir}/analytics_{timestamp}.json'
                with open(json_file, 'w') as f:
                    json.dump(analytics_data, f, indent=2, default=str)
                files_created.append(json_file)
                
                # Also create a CSV summary
                csv_file = f'{export_dir}/analytics_summary_{timestamp}.csv'
                with open(csv_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Metric', 'Value'])
                    writer.writerow(['Total Users', analytics_data['summary']['total_users']])
                    writer.writerow(['Total Quizzes', analytics_data['summary']['total_quizzes']])
                    writer.writerow(['Total Attempts', analytics_data['summary']['total_attempts']])
                    writer.writerow(['Export Date', timestamp])
                files_created.append(csv_file)
                
                # Generate PDF report
                pdf_file = f'{export_dir}/analytics_report_{timestamp}.pdf'
                pdf_generated = generate_pdf_report(analytics_data, pdf_file)
                if pdf_generated:
                    files_created.append(pdf_file)
            
            return {
                'status': 'success',
                'message': f'Export completed successfully. {len(files_created)} file(s) created.',
                'files_created': files_created,
                'export_type': export_type,
                'timestamp': timestamp
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': 'Export failed',
            'error': str(e)
        }

def export_user_data(user_id):
    """Export data for a specific user"""
    try:
        # Import here to avoid circular import
        from app import create_app, db
        from app.models.models import User, QuizAttempt
        
        with create_app().app_context():
            user = User.query.get(user_id)
            if not user:
                return {
                    'status': 'error',
                    'message': 'User not found',
                    'error': 'Invalid user ID'
                }
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_dir = 'exports'
            os.makedirs(export_dir, exist_ok=True)
            
            files_created = []
            
            # Export user's quiz attempts as CSV
            csv_file = f'{export_dir}/user_{user_id}_attempts_{timestamp}.csv'
            attempts = QuizAttempt.query.filter_by(user_id=user_id, is_completed=True).all()
            
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Quiz', 'Score', 'Started At', 'Completed At'])
                
                for attempt in attempts:
                    writer.writerow([
                        attempt.id,
                        attempt.quiz.title if attempt.quiz else 'Unknown',
                        attempt.score,
                        attempt.started_at.isoformat() if attempt.started_at else '',
                        attempt.completed_at.isoformat() if attempt.completed_at else ''
                    ])
            files_created.append(csv_file)
            
            # Generate PDF report for user
            pdf_file = f'{export_dir}/user_{user_id}_report_{timestamp}.pdf'
            pdf_generated = generate_user_pdf_report(user, attempts, pdf_file)
            if pdf_generated:
                files_created.append(pdf_file)
            
            return {
                'status': 'success',
                'message': f'User data export completed successfully. {len(files_created)} file(s) created.',
                'files_created': files_created,
                'timestamp': timestamp
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': 'User data export failed',
            'error': str(e)
        }

def generate_pdf_report(analytics_data, filename):
    """Generate a PDF report from analytics data"""
    try:
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        story.append(Paragraph("PrepCheck Analytics Report", title_style))
        story.append(Spacer(1, 20))
        
        # Export info
        export_info = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        story.append(Paragraph(export_info, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary Statistics
        story.append(Paragraph("Summary Statistics", styles['Heading2']))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Users', str(analytics_data['summary']['total_users'])],
            ['Total Quizzes', str(analytics_data['summary']['total_quizzes'])],
            ['Total Quiz Attempts', str(analytics_data['summary']['total_attempts'])]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Top Performers
        if analytics_data['users']:
            story.append(Paragraph("User Performance Overview", styles['Heading2']))
            user_data = [['User', 'Email', 'Attempts', 'Avg Score']]
            
            # Sort users by average score (descending) and take top 10
            sorted_users = sorted(analytics_data['users'], 
                                key=lambda x: x['average_score'], reverse=True)[:10]
            
            for user in sorted_users:
                user_data.append([
                    user['full_name'][:20] + ('...' if len(user['full_name']) > 20 else ''),
                    user['email'][:25] + ('...' if len(user['email']) > 25 else ''),
                    str(user['total_attempts']),
                    f"{user['average_score']:.1f}%"
                ])
            
            user_table = Table(user_data, colWidths=[2*inch, 2.5*inch, 1*inch, 1*inch])
            user_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            story.append(user_table)
            story.append(Spacer(1, 30))
        
        # Recent Quiz Attempts
        if analytics_data['quiz_attempts']:
            story.append(Paragraph("Recent Quiz Attempts", styles['Heading2']))
            attempts_data = [['User', 'Quiz', 'Score', 'Date']]
            
            for attempt in analytics_data['quiz_attempts'][:15]:  # Show last 15 attempts
                completed_date = attempt['completed_at']
                if completed_date:
                    try:
                        date_obj = datetime.fromisoformat(completed_date.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime('%m/%d/%Y')
                    except:
                        formatted_date = 'N/A'
                else:
                    formatted_date = 'N/A'
                
                attempts_data.append([
                    attempt['user_name'][:15] + ('...' if len(attempt['user_name']) > 15 else ''),
                    attempt['quiz_title'][:20] + ('...' if len(attempt['quiz_title']) > 20 else ''),
                    f"{attempt['score']:.1f}%" if attempt['score'] is not None else 'N/A',
                    formatted_date
                ])
            
            attempts_table = Table(attempts_data, colWidths=[1.8*inch, 2.2*inch, 1*inch, 1.5*inch])
            attempts_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            story.append(attempts_table)
            story.append(Spacer(1, 30))
        
        # Subject Performance
        if analytics_data['subject_performance']:
            story.append(Paragraph("Subject Performance", styles['Heading2']))
            subject_data = [['Subject', 'Total Attempts', 'Average Score']]
            
            for subject in analytics_data['subject_performance']:
                subject_data.append([
                    subject['subject_name'],
                    str(subject['total_attempts']),
                    f"{subject['average_score']:.1f}%"
                ])
            
            subject_table = Table(subject_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            subject_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            story.append(subject_table)
        
        # Build PDF
        doc.build(story)
        return True
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        return False

def generate_user_pdf_report(user, attempts, filename):
    """Generate a PDF report for a specific user"""
    try:
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        story.append(Paragraph("PrepCheck User Progress Report", title_style))
        story.append(Spacer(1, 20))
        
        # User Information
        user_info_style = ParagraphStyle(
            'UserInfo',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkgreen
        )
        story.append(Paragraph(f"User: {user.full_name}", user_info_style))
        story.append(Paragraph(f"Email: {user.email}", styles['Normal']))
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Summary Statistics
        total_attempts = len(attempts)
        if total_attempts > 0:
            scores = [attempt.score for attempt in attempts if attempt.score is not None]
            avg_score = sum(scores) / len(scores) if scores else 0
            max_score = max(scores) if scores else 0
            min_score = min(scores) if scores else 0
        else:
            avg_score = max_score = min_score = 0
        
        story.append(Paragraph("Performance Summary", styles['Heading2']))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Quiz Attempts', str(total_attempts)],
            ['Average Score', f"{avg_score:.1f}%"],
            ['Highest Score', f"{max_score:.1f}%"],
            ['Lowest Score', f"{min_score:.1f}%" if total_attempts > 0 else "N/A"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Quiz Attempts Detail
        if attempts:
            story.append(Paragraph("Quiz Attempts History", styles['Heading2']))
            attempts_data = [['Quiz Title', 'Score', 'Date Completed', 'Duration']]
            
            for attempt in sorted(attempts, key=lambda x: x.completed_at or datetime.min, reverse=True):
                completed_date = attempt.completed_at
                if completed_date:
                    try:
                        formatted_date = completed_date.strftime('%m/%d/%Y %I:%M %p')
                    except:
                        formatted_date = 'N/A'
                else:
                    formatted_date = 'N/A'
                
                # Calculate duration
                if attempt.started_at and attempt.completed_at:
                    try:
                        duration = attempt.completed_at - attempt.started_at
                        duration_str = f"{duration.seconds // 60}m {duration.seconds % 60}s"
                    except:
                        duration_str = 'N/A'
                else:
                    duration_str = 'N/A'
                
                quiz_title = attempt.quiz.title if attempt.quiz else 'Unknown Quiz'
                if len(quiz_title) > 25:
                    quiz_title = quiz_title[:22] + '...'
                
                attempts_data.append([
                    quiz_title,
                    f"{attempt.score:.1f}%" if attempt.score is not None else 'N/A',
                    formatted_date,
                    duration_str
                ])
            
            attempts_table = Table(attempts_data, colWidths=[2.5*inch, 1.2*inch, 1.8*inch, 1*inch])
            attempts_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left align quiz titles
            ]))
            story.append(attempts_table)
            story.append(Spacer(1, 30))
            
            # Subject Performance (if we can get subject data)
            subject_performance = {}
            for attempt in attempts:
                if attempt.quiz and attempt.quiz.chapter and attempt.quiz.chapter.subject:
                    subject_name = attempt.quiz.chapter.subject.name
                    if subject_name not in subject_performance:
                        subject_performance[subject_name] = {'scores': [], 'attempts': 0}
                    if attempt.score is not None:
                        subject_performance[subject_name]['scores'].append(attempt.score)
                    subject_performance[subject_name]['attempts'] += 1
            
            if subject_performance:
                story.append(Paragraph("Performance by Subject", styles['Heading2']))
                subject_data = [['Subject', 'Attempts', 'Average Score']]
                
                for subject, data in subject_performance.items():
                    avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
                    subject_data.append([
                        subject,
                        str(data['attempts']),
                        f"{avg_score:.1f}%"
                    ])
                
                subject_table = Table(subject_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                subject_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                ]))
                story.append(subject_table)
        else:
            story.append(Paragraph("No quiz attempts found for this user.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return True
        
    except Exception as e:
        print(f"User PDF generation error: {e}")
        return False
