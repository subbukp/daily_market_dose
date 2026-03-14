import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    EMAIL_SENDER,
    EMAIL_PASSWORD,
    EMAIL_RECEIVERS,
    SMTP_SERVER,
    SMTP_PORT,
)


def send_email(subject: str, body_html: str):
    """Send an individual HTML email to each receiver — fully private, no BCC visible."""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        raise ValueError("EMAIL_SENDER and EMAIL_PASSWORD must be set in .env")
    if not EMAIL_RECEIVERS:
        raise ValueError("EMAIL_RECEIVERS must be set in .env (comma-separated)")

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        for receiver in EMAIL_RECEIVERS:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = EMAIL_SENDER
            msg["To"] = receiver
            msg.attach(MIMEText(body_html, "html"))

            server.sendmail(EMAIL_SENDER, [receiver], msg.as_string())

    count = len(EMAIL_RECEIVERS)
    print(f"   📧 Sent individually to {count} recipient{'s' if count > 1 else ''}")
