from pathlib import Path

from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from app.config import settings
from app.controllers import controller_log
from app.controllers.exceptions import CouldNotSentEmailException
from app.core.constants import PROJECT_NAME

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER=Path("./app/templates"),
)


async def sent_otp_in_email(background_tasks: BackgroundTasks, email: str, data: dict):
    """
    Send OTP to user email

    :param background_tasks: ``(BackgroundTasks)``: BackgroundTasks instance
    :param email: ``(str)``: User email
    :param data: ``(dict)``: Data to send in email

    :return: None

    :raises CouldNotSentEmailException: If it could not send email

    """
    try:
        message = MessageSchema(
            subject=f"OTP for {PROJECT_NAME}",
            recipients=[email],
            template_body=data,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)  # Create the connection server
        background_tasks.add_task(
            fm.send_message, message, template_name="email.html"
        )  # Send the email in background

    except Exception as e:
        controller_log.error(e, exc_info=1)

        raise CouldNotSentEmailException()
