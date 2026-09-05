"""Base REST client for OSS systems."""

from __future__ import annotations

import httpx
import structlog

from tele2_configurator.config import settings

logger = structlog.get_logger(__name__)


class RestClient:
    """Minimal HTTP client exposing create/update/delete for an OSS endpoint."""

    def __init__(self, base_url: str, headers: dict[str, str] | None = None) -> None:
        self._base_url = base_url
        self._headers = headers or {}
        self._client = httpx.AsyncClient(timeout=30.0)

    def _url(self, path: str) -> str:
        return f"{self._base_url.rstrip('/')}/{path.lstrip('/')}"

    async def create(self, resource_type: str, payload: dict[str, object]) -> dict[str, object]:
        response = await self._client.post(
            self._url(resource_type), headers=self._headers, json=payload
        )
        response.raise_for_status()
        logger.info("oss_create", resource=resource_type)
        return dict(response.json())

    async def update(
        self, resource_type: str, resource_id: str, payload: dict[str, object]
    ) -> dict[str, object]:
        url = self._url(f"{resource_type}/{resource_id}")
        response = await self._client.put(url, headers=self._headers, json=payload)
        response.raise_for_status()
        logger.info("oss_update", resource=resource_type, id=resource_id)
        return dict(response.json())

    async def delete(self, resource_type: str, resource_id: str) -> dict[str, object]:
        url = self._url(f"{resource_type}/{resource_id}")
        response = await self._client.delete(url, headers=self._headers)
        response.raise_for_status()
        logger.info("oss_delete", resource=resource_type, id=resource_id)
        return dict(response.json())

    async def aclose(self) -> None:
        await self._client.aclose()


class NokiaNspClient(RestClient):
    def __init__(self) -> None:
        super().__init__(
            settings.nokia_nsp_url,
            headers={
                "Authorization": "Basic ",  # TODO: implement token acquisition
                "Content-Type": "application/json",
            },
        )


class TmForumClient(RestClient):
    def __init__(self) -> None:
        super().__init__(
            settings.tmforum_url,
            headers={"Authorization": "Bearer ", "Content-Type": "application/json"},
        )


class Tele2CustomApiClient(RestClient):
    def __init__(self) -> None:
        super().__init__(
            settings.custom_api_url,
            headers={"X-API-Key": settings.custom_api_key, "Content-Type": "application/json"},
        )


def get_client(system: str) -> RestClient:
    clients: dict[str, RestClient] = {
        "nokia_nsp": NokiaNspClient(),
        "tmforum": TmForumClient(),
        "custom_api": Tele2CustomApiClient(),
    }
    if system not in clients:
        raise ValueError(f"Unknown OSS system: {system}")
    return clients[system]
