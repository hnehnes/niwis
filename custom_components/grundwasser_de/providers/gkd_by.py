"""Bayern groundwater provider (GKD Bayern / Bayerisches Landesamt für Umwelt).

Backed by the public **Gewässerkundlicher Dienst Bayern** portal
(``www.gkd.bayern.de``), no login. Two product pages cover the state's
groundwater level network:

* *Oberes Grundwasser-Stockwerk* (``gwo``, ~1960 stations) and
* *Tiefere Grundwasser-Stockwerke* (``gwt``, ~250 stations).

Each product's overview page embeds a Leaflet map ``"pointer"`` JSON array with,
per station, its id (``p``), name (``n``), the detail-page ``uri``, **WGS84**
``lat``/``lon`` and the current ``w`` (Grundwasserstand in *m ü. NN*). So:

* **search** — one GET per product page yields every station with coordinates
  and its current value; no coordinate conversion is needed (the portal serves
  WGS84 directly, so this provider needs no offline bundle).
* **fetch** — the per-station ``…/messwerte`` detail page carries the current
  value plus a short "letzte 12 Monate" daily table (~8 recent days), parsed to
  a chronological series. This stays a lightweight per-station request; the
  full history download center (``enqueue_download``) is intentionally not used.

Data licence: CC BY 4.0, attribution "Datenquelle: Bayerisches Landesamt für
Umwelt, www.lfu.bayern.de".

Docs: https://www.gkd.bayern.de/de/grundwasser/oberesstockwerk
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Any

from aiohttp import ClientError, ClientSession

from ..api import haversine_km
from .base import Provider, ProviderError, ProviderReading, ProviderStation

_LOGGER = logging.getLogger(__name__)

DOMAIN = "gkd_by"
LABEL = "Bayern (GKD)"

BASE_URL = "https://www.gkd.bayern.de"
#: The two GW-Stockwerk product pages; each embeds a full station ``pointer`` JSON.
_PRODUCT_URLS = (
    f"{BASE_URL}/de/grundwasser/oberesstockwerk",
    f"{BASE_URL}/de/grundwasser/tieferestockwerke",
)
UNIT = "m"  # Grundwasserstand in m ü. NN (≈ m ü. NHN), matching the other providers.
ATTRIBUTION = (
    "Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de "
    "(GKD Bayern, CC BY 4.0)"
)

_USER_AGENT = (
    "Mozilla/5.0 (compatible; homeassistant-grundwasser-de/0.1; "
    "+https://github.com/hnehnes/niwis)"
)
_TIMEOUT = 60

#: marker of the embedded Leaflet ``pointer`` array on a product overview page.
_POINTER_KEY = '"pointer":'

#: a ``Datum``/``Grundwasserstand`` row in the detail page's daily table.
_ROW_RE = re.compile(
    r"<td[^>]*>\s*(\d{2}\.\d{2}\.\d{4})\s*</td>\s*"
    r"<td[^>]*>\s*([0-9.,\-]+)\s*</td>"
)
#: the detail page's explicit "current value" line (precise timestamp with time).
_LATEST_VALUE_RE = re.compile(
    r"Grundwasserstand \[m[^\]]*\]:\s*<strong[^>]*>\s*([0-9.,\-]+)"
)
_LATEST_TS_RE = re.compile(
    r"Letzter Messwert vom\s*<strong[^>]*>\s*(\d{2}\.\d{2}\.\d{4}(?:\s+\d{2}:\d{2})?)"
)


# --------------------------------------------------------------------------- #
# Pure helpers (no I/O – unit-tested against tests/fixtures/gkd_by/*).
# --------------------------------------------------------------------------- #
def _to_float(raw: Any) -> float | None:
    """Parse a German-formatted number (``"348,48"``) to float, else ``None``."""
    if raw is None:
        return None
    text = str(raw).strip().replace(",", ".")
    if not text or text == "-":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _parse_coord(raw: Any) -> float | None:
    """Parse a coordinate; the GKD map treats ``lat``/``lon`` < 1 as missing."""
    value = _to_float(raw)
    if value is None or value < 1:
        return None
    return value


def _parse_dt(raw: Any) -> datetime | None:
    """Parse ``dd.mm.yyyy`` or ``dd.mm.yyyy HH:MM`` to a datetime, else ``None``."""
    if not raw:
        return None
    text = str(raw).strip()
    for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def extract_pointer(html: str) -> list[dict]:
    """Return the embedded Leaflet ``pointer`` array, or ``[]`` if absent."""
    idx = html.find(_POINTER_KEY)
    if idx < 0:
        return []
    start = html.find("[", idx)
    if start < 0:
        return []
    try:
        data, _ = json.JSONDecoder().raw_decode(html, start)
    except ValueError:
        return []
    return data if isinstance(data, list) else []


def pointer_records(html: str) -> list[dict]:
    """Parse a product page's ``pointer`` into ``{station_id, name, uri, …}`` dicts."""
    records: list[dict] = []
    for item in extract_pointer(html):
        pid = item.get("p")
        if pid is None:
            continue
        records.append(
            {
                "station_id": str(pid),
                "name": (item.get("n") or "").strip() or f"Messstelle {pid}",
                "uri": item.get("uri") or "",
                "lat": _parse_coord(item.get("lat")),
                "lon": _parse_coord(item.get("lon")),
                "value": _to_float(item.get("w")),
                "timestamp": _parse_dt(item.get("d")),
            }
        )
    return records


def parse_detail(
    html: str,
) -> tuple[float | None, datetime | None, list[tuple[datetime, float]]]:
    """Parse a ``…/messwerte`` detail page.

    Returns ``(value, timestamp, history)``: the current value (from the explicit
    "Grundwasserstand [m ü. NN]:" line, which carries a precise timestamp) plus
    the recent daily table as a chronological ``(timestamp, value)`` series. Falls
    back to the newest table row if the explicit line is missing.
    """
    history: list[tuple[datetime, float]] = []
    for date_raw, value_raw in _ROW_RE.findall(html):
        value = _to_float(value_raw)
        when = _parse_dt(date_raw)
        if value is None or when is None:
            continue
        history.append((when, value))
    history.sort(key=lambda sample: sample[0])

    value_match = _LATEST_VALUE_RE.search(html)
    value = _to_float(value_match.group(1)) if value_match else None
    ts_match = _LATEST_TS_RE.search(html)
    timestamp = _parse_dt(ts_match.group(1)) if ts_match else None

    if value is None and history:
        timestamp, value = history[-1]
    elif value is not None and timestamp is None and history:
        timestamp = history[-1][0]
    return value, timestamp, history


# --------------------------------------------------------------------------- #
# Provider
# --------------------------------------------------------------------------- #
class GkdByProvider(Provider):
    """Groundwater provider backed by the GKD Bayern portal (LfU)."""

    domain = DOMAIN
    label = LABEL

    def __init__(self, session: ClientSession) -> None:
        """Initialise with a shared aiohttp session."""
        self._session = session

    # -- search ------------------------------------------------------------- #
    async def async_search_radius(
        self, latitude: float, longitude: float, radius_km: float
    ) -> list[ProviderStation]:
        """Return stations within ``radius_km``, nearest first, with coordinates."""
        matches: list[ProviderStation] = []
        for record in await self._load_all_stations():
            if record["lat"] is None or record["lon"] is None:
                continue
            distance = haversine_km(
                latitude, longitude, record["lat"], record["lon"]
            )
            if distance <= radius_km:
                matches.append(self._to_station(record, distance))
        matches.sort(key=lambda s: s.distance_km or 0.0)
        return matches

    async def async_search_query(self, query: str) -> list[ProviderStation]:
        """Return stations whose id or name contains ``query``."""
        needle = query.strip().casefold()
        matches = [
            self._to_station(record)
            for record in await self._load_all_stations()
            if needle in record["station_id"].casefold()
            or needle in record["name"].casefold()
        ]
        matches.sort(key=lambda s: s.name)
        return matches

    # -- fetch -------------------------------------------------------------- #
    async def async_fetch(self, station: ProviderStation) -> ProviderReading:
        """Return the latest reading and recent history for ``station``."""
        uri = station.extra.get("uri") or await self._resolve_uri(station.station_id)
        if not uri:
            raise ProviderError(
                f"GKD Bayern: no detail page for station {station.station_id}"
            )
        html = await self._get_text(uri)
        value, timestamp, history = parse_detail(html)
        return ProviderReading(
            value=value,
            unit=UNIT,
            timestamp=timestamp,
            history=history,
            attribution=ATTRIBUTION,
        )

    # -- internals ---------------------------------------------------------- #
    async def _load_all_stations(self) -> list[dict]:
        """Fetch both product pages and merge their ``pointer`` stations (de-duped)."""
        pages = await asyncio.gather(
            *(self._get_text(url) for url in _PRODUCT_URLS)
        )
        records: list[dict] = []
        seen: set[str] = set()
        for html in pages:
            for record in pointer_records(html):
                if record["station_id"] in seen:
                    continue
                seen.add(record["station_id"])
                records.append(record)
        return records

    async def _resolve_uri(self, station_id: str) -> str:
        """Look up a station's detail-page URL from the product pages (fallback)."""
        for record in await self._load_all_stations():
            if record["station_id"] == station_id:
                return record["uri"]
        return ""

    @staticmethod
    def _to_station(
        record: dict, distance_km: float | None = None
    ) -> ProviderStation:
        return ProviderStation(
            provider=DOMAIN,
            station_id=record["station_id"],
            name=record["name"],
            latitude=record["lat"],
            longitude=record["lon"],
            distance_km=distance_km,
            extra={"uri": record["uri"]},
        )

    async def _get_text(self, url: str) -> str:
        """GET a portal page and return its decoded text."""
        try:
            async with self._session.get(
                url,
                headers={"User-Agent": _USER_AGENT},
                timeout=_TIMEOUT,
            ) as resp:
                if resp.status != 200:
                    raise ProviderError(f"GKD Bayern HTTP {resp.status}")
                return await resp.text()
        except (TimeoutError, ClientError) as err:
            raise ProviderError(f"GKD Bayern request failed: {err}") from err
