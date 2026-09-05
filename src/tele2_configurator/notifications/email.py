"""Email notifications via SMTP."""

from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

import structlog

from tele2_configurator.config import settings

logger = structlog.get_logger(__name__)


def send_email(subject: str, body: str, to: str) -> None:
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.email_from
    msg["To"] = to

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg)

    logger.info("email_sent", to=to, subject=subject)
