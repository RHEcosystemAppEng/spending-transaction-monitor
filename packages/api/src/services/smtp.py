import logging
import os
import smtplib
from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from db.models import AlertNotification

logger = logging.getLogger(__name__)

class EmailNotification(BaseModel):
    to_emails: List[EmailStr]
    subject: str
    body: str
    html_body: Optional[str] = None
    from_email: Optional[str] = None
    reply_to: Optional[str] = None

class SMTPConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str
    from_email: str
    reply_to_email: str
    use_tls: bool = True
    use_ssl: bool = False

smtp_config = {
    "host": os.getenv("SMTP_HOST"),
    "port": os.getenv("SMTP_PORT"),
    "username": os.getenv("SMTP_USERNAME"),
    "password": os.getenv("SMTP_PASSWORD"),
    "from_email": os.getenv("SMTP_FROM_EMAIL"),
    "reply_to_email": os.getenv("SMTP_REPLY_TO_EMAIL"),
    "use_tls": os.getenv("SMTP_USE_TLS") or True,
    "use_ssl": os.getenv("SMTP_USE_SSL") or False
}

async def send_smtp_notification(
    notification: AlertNotification,
):
    """Send email notification"""
    
    try:
        user_email_result = await session.execute(select(User.email).where(User.id == payload.userId))
        user_email = user_result.scalar_one_or_none()
        if not user_email:
            raise HTTPException(status_code=404, detail="User email not found")

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = notification.title
        msg['From'] = smtp_config.from_email or smtp_config.username

        if smtp_config.reply_to_email:
            msg['Reply-To'] = smtp_config.reply_to_email
        
        # Add plain text body
        text_part = MIMEText(notification.message, 'plain')
        msg.attach(text_part)
        
        # Add HTML body if provided
        # if notification.html_body:
        #     html_part = MIMEText(notification.html_body, 'html')
        #     msg.attach(html_part)
        
        # Connect to SMTP server
        if smtp_config.use_ssl:
            server = smtplib.SMTP_SSL(smtp_config.host, smtp_config.port)
        else:
            server = smtplib.SMTP(smtp_config.host, smtp_config.port)
            if smtp_config.use_tls:
                server.starttls()
        
        server.login(smtp_config.username, smtp_config.password)
        
        # Send email
        try:
            msg['To'] = user_email
            server.send_message(msg)
            logger.info(f"Email sent successfully to {user_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {user_email}: {str(e)}")

        server.quit()

        finished_at = datetime.now()

        return AlertNotification(
            id=notification.id,
            userId=notification.userId,
            alertRuleId=notification.alertRuleId,
            transactionId=notification.transactionId,
            title=notification.title,
            message=notification.message,
            notificationMethod=notification.notificationMethod,
            status=notification.status,
            sentAt=finished_at,
            deliveredAt=finished_at,
            readAt=None,
            createdAt=finished_at,
            updatedAt=finished_at,
        )
        
    except Exception as e:
        logger.error(f"Failed to send notifications: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send notifications: {str(e)}"
        )
