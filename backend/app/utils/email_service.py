from flask_mail import Message
from app import mail
import logging

logger = logging.getLogger(__name__)

def send_email(to_email, subject, html_content, from_email=None):
    """Send email using Flask-Mail"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            html=html_content,
            sender=from_email or 'noreply@prepcheck.com'
        )
        
        mail.send(msg)
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def send_bulk_email(recipients, subject, html_content, from_email=None):
    """Send bulk emails"""
    try:
        with mail.connect() as conn:
            for recipient in recipients:
                msg = Message(
                    subject=subject,
                    recipients=[recipient],
                    html=html_content,
                    sender=from_email or 'noreply@prepcheck.com'
                )
                conn.send(msg)
        
        logger.info(f"Bulk email sent successfully to {len(recipients)} recipients")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send bulk email: {str(e)}")
        return False
