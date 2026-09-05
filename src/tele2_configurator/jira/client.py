"""Jira REST API client wrapper."""

from __future__ import annotations

import jira as jira_lib
import structlog

from tele2_configurator.config import settings
from tele2_configurator.models import Ticket

logger = structlog.get_logger(__name__)


class JiraClient:
    def __init__(self) -> None:
        self._client = jira_lib.JIRA(
            server=settings.jira_url,
            basic_auth=(settings.jira_username, settings.jira_api_token),
        )

    def get_inbox_tickets(self, project_key: str | None = None) -> list[Ticket]:
        project = project_key or settings.jira_project_key
        jql = f"project = {project} AND status = Inbox ORDER BY created ASC"
        issues = self._client.search_issues(jql, maxResults=25)
        return [self._to_ticket(issue) for issue in issues]

    def add_comment(self, ticket_key: str, body: str) -> None:
        self._client.add_comment(ticket_key, body)
        logger.info("jira_comment_added", ticket=ticket_key)

    def transition_ticket(self, ticket_key: str, transition_name: str) -> None:
        transitions = self._client.transitions(ticket_key)
        for t in transitions:
            if t["name"].lower() == transition_name.lower():
                self._client.transition_issue(ticket_key, t["id"])
                logger.info("jira_transition", ticket=ticket_key, transition=transition_name)
                return
        logger.warning("jira_transition_not_found", ticket=ticket_key, transition=transition_name)

    def attach_file(self, ticket_key: str, file_path: str) -> None:
        self._client.add_attachment(ticket_key, file_path)

    def _to_ticket(self, issue: jira_lib.Issue) -> Ticket:
        return Ticket(
            key=issue.key,
            summary=issue.fields.summary or "",
            description=issue.fields.description or "",
            status=str(issue.fields.status),
            assignee=str(issue.fields.assignee) if issue.fields.assignee else None,
            labels=issue.fields.labels or [],
        )
