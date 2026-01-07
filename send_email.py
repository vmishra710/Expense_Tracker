import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tasks.exceptions import RetryableEmailError, PermanentEmailError


# load .env from project root
load_dotenv()

EMAIL_HOST=os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT=int(os.getenv("EMAIL_PORT", 587))
EMAIL=os.getenv("EMAIL")
APP_PASSWORD=os.getenv("APP_PASSWORD")

def send_email(to_email: str, subject: str, html_body: str) -> None:
    """
    Synchronous helper to send an HTML email via Gmail SMTP (STARTTLS).
    This runs inside Celery worker (blocking I/O is fine there).
    """
    if not EMAIL or not APP_PASSWORD:
        raise RuntimeError("EMAIL / APP_PASSWORD not set in environment (.env)")

    msg = MIMEMultipart()
    msg["From"]=EMAIL
    msg["To"]=to_email
    msg["Subject"]=subject
    msg.attach(MIMEText(html_body, "html"))

    # Connect via TLS (STARTTLS) on port 587
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()

        try:
            server.login(EMAIL, APP_PASSWORD)
            server.sendmail(EMAIL, to_email, msg.as_string())

        except smtplib.SMTPAuthenticationError:
            raise PermanentEmailError("Invalid SMTP credentials")

        except smtplib.SMTPException as exc:
            raise RetryableEmailError(f"SMTP error: {str(exc)}")

