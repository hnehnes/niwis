"""Minimal async client for ArcGIS REST ``MapServer``/``FeatureServer`` queries.

Several state groundwater portals expose their data as public, unauthenticated
ArcGIS REST services (Hesse, Saxony, Saarland, …). This helper wraps the
``/<layer>/query`` endpoint: it builds the request, follows ArcGIS result paging
(``exceededTransferLimit`` → ``resultOffset``), and returns the raw feature list
(``[{"attributes": {...}, "geometry": {...}}, …]``).

Requesting ``outSR=4326`` returns geometry already in WGS84, so callers need no
coordinate transformation.
"""

from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ClientSession

from .base import ProviderError

_TIMEOUT = 60
_PAGE_SIZE = 1000
_MAX_FEATURES = 5000


def escape_like(value: str) -> str:
    """Escape a user string for safe use inside an ArcGIS SQL ``LIKE`` literal."""
    return value.replace("'", "''").replace("%", "").replace("_", "")


async def query_features(
    session: ClientSession,
    url: str,
    params: dict[str, Any],
    *,
    paginate: bool = True,
    max_features: int = _MAX_FEATURES,
) -> list[dict]:
    """Run an ArcGIS ``query`` and return its features, following paging.

    ``params`` is merged with ``f=json``; do not pre-set ``resultOffset``.
    """
    features: list[dict] = []
    offset = 0
    while True:
        page = {"f": "json", **params}
        if paginate:
            page.setdefault("resultRecordCount", _PAGE_SIZE)
            page["resultOffset"] = offset
        try:
            async with session.get(url, params=page, timeout=_TIMEOUT) as resp:
                if resp.status != 200:
                    raise ProviderError(f"ArcGIS HTTP {resp.status}")
                payload = await resp.json(content_type=None)
        except (TimeoutError, ClientError) as err:
            raise ProviderError(f"ArcGIS request failed: {err}") from err
        if isinstance(payload, dict) and payload.get("error"):
            message = (payload["error"] or {}).get("message", "unknown")
            raise ProviderError(f"ArcGIS error: {message}")

        batch = payload.get("features") or []
        features.extend(batch)
        if (
            not paginate
            or not payload.get("exceededTransferLimit")
            or not batch
            or len(features) >= max_features
        ):
            break
        offset += len(batch)
    return features
