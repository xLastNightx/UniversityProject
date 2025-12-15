import aiosmtplib
from email.mime.text import MIMEText

async def send_email(to: str, subject: str, body: str):
    message = MIMEText(body, "html")
    message["From"] = "noreply@booking.local"
    message["To"] = to
    message["Subject"] = subject

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username="ваш-email@gmail.com",
        password="ваш-app-password"
    )