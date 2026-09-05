"""AI ticket analyzer — converts a Jira ticket into a structured config plan."""

from __future__ import annotations

import json

import structlog
from openai import AsyncOpenAI

from tele2_configurator.agent.prompts import ANALYZER_SYSTEM_PROMPT
from tele2_configurator.config import settings
from tele2_configurator.models import ConfigPlan, Ticket

logger = structlog.get_logger(__name__)


async def analyze_ticket(ticket: Ticket) -> ConfigPlan | None:
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    ticket_text = (
        f"Ticket: {ticket.key}\n"
        f"Summary: {ticket.summary}\n"
        f"Description:\n{ticket.description}\n"
        f"Labels: {', '.join(ticket.labels)}\n"
    )

    try:
        logger.info("analyzing_ticket", ticket=ticket.key)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": ANALYZER_SYSTEM_PROMPT},
                {"role": "user", "content": ticket_text},
            ],
        )
    except Exception:
        logger.exception("openai_call_failed", ticket=ticket.key)
        return None

    content = response.choices[0].message.content or ""
    try:
        raw = json.loads(content)
        plan = ConfigPlan(ticket_key=ticket.key, **raw)
        logger.info("plan_generated", ticket=ticket.key, actions=len(plan.actions))
        return plan
    except Exception:
        logger.exception("plan_parse_failed", ticket=ticket.key, content=content)
        return None
