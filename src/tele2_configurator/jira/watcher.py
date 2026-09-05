"""Jira ticket watcher — polls for inbox tickets and triggers processing."""

from __future__ import annotations

import asyncio

import structlog

from tele2_configurator.agent.analyzer import analyze_ticket
from tele2_configurator.config import settings
from tele2_configurator.jira.client import JiraClient
from tele2_configurator.notifications.notifier import notify_result
from tele2_configurator.oss.executor import execute_plan

logger = structlog.get_logger(__name__)


async def poll_once() -> None:
    client = JiraClient()
    tickets = client.get_inbox_tickets()
    logger.info("jira_poll", ticket_count=len(tickets))

    for ticket in tickets:
        logger.info("processing_ticket", ticket=ticket.key)

        plan = await analyze_ticket(ticket)
        if not plan:
            logger.warning("no_plan_generated", ticket=ticket.key)
            continue

        if settings.dry_run:
            status_line = "🧪 Dry-run — no changes."
        else:
            status_line = "⏳ Awaiting approval in dashboard..."
        client.add_comment(
            ticket.key,
            "🤖 **Auto-Configurator Analysis**\n\n"
            f"**Request type:** {plan.request_type.value}\n"
            f"**Summary:** {plan.summary}\n"
            f"**Planned actions:** {len(plan.actions)}\n"
            f"**Risks:** {', '.join(plan.risks) if plan.risks else 'None identified'}\n\n"
            f"{status_line}",
        )

        if settings.dry_run:
            client.transition_ticket(ticket.key, "In Progress")
            notify_result(ticket.key, plan, None)
            continue

        result = await execute_plan(plan)
        client.transition_ticket(ticket.key, "In Progress" if result.success else "Blocked")
        notify_result(ticket.key, plan, result)


async def run_watcher() -> None:
    logger.info("watcher_started", interval=settings.poll_interval, dry_run=settings.dry_run)
    while True:
        try:
            await poll_once()
        except Exception:
            logger.exception("poll_error")
        await asyncio.sleep(settings.poll_interval)
