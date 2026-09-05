"""Notification coordinator — sends Jira comments and emails on plan/result."""

from __future__ import annotations

import structlog

from tele2_configurator.config import settings
from tele2_configurator.jira.client import JiraClient
from tele2_configurator.models import ConfigPlan, ExecutionResult
from tele2_configurator.notifications.email import send_email

logger = structlog.get_logger(__name__)

NOTIFY_EMAIL = "oss-team@tele2.se"


def notify_result(ticket_key: str, plan: ConfigPlan, result: ExecutionResult | None) -> None:
    client = JiraClient()

    if result is None:
        body = (
            f"🧪 **Dry-run complete** for {ticket_key}.\n"
            f"Planned {len(plan.actions)} action(s) on {plan.request_type.value}. "
            f"No changes applied."
        )
        client.add_comment(ticket_key, body)
        return

    if result.success:
        body = (
            f"✅ **Configuration executed successfully** for {ticket_key}.\n"
            f"Executed {result.executed_actions}/{len(plan.actions)} action(s)."
        )
        client.add_comment(ticket_key, body)
        if settings.smtp_host:
            send_email(
                f"[Auto-Config] ✅ {ticket_key} configuration applied",
                (
                    f"Successfully configured {ticket_key}.\n\n"
                    f"Actions executed: {result.executed_actions}"
                ),
                NOTIFY_EMAIL,
            )
    else:
        body = (
            f"❌ **Configuration failed** for {ticket_key}.\n"
            f"Errors: {', '.join(result.errors)}"
        )
        client.add_comment(ticket_key, body)
