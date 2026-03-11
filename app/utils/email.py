import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings
import logging

logger = logging.getLogger("medlink")

async def send_otp_email(email: str, otp: str):
    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = email
    message["Subject"] = "MedLink - Your Login OTP"
    message.set_content(f"Your OTP for MedLink login is: {otp}. It is valid for 10 minutes.")

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True,
        )
        logger.info(f"OTP sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {str(e)}")
        return False
