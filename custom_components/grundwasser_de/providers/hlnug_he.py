"""Hesse groundwater provider (HLNUG, GruSchu / Wasserviewer).

Backed by the state's open **ArcGIS REST** services (no token, CC-BY 4.0):

* **stations** — ``gruschu/gruschu_mst_ga/MapServer/0`` (fields ``ID``,
  ``MESSTELLENNAME``, point geometry). ArcGIS does the radius query natively
  (``geometry`` + ``distance``) and returns WGS84 when asked (``outSR=4326``).
* **time series** — ``wasserviewer/Auswertung/MapServer/22``
  (``V_GWM_WASSERSTAND_NN``, m ü. NN), joined by ``GWM_ID == station.ID``;
  ``MESSDATUM`` is epoch-milliseconds, ``MESSWERT`` the level.

Stations without an NN series (springs/galleries, GOK-only wells) return value
``None`` — the runtime safety net, same as the other providers.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from aiohttp import ClientSession

from ..api import haversine_km
from ._arcgis import escape_like, query_features
from .base import Provider, ProviderReading, ProviderStation

DOMAIN = "hlnug_he"
LABEL = "Hessen (HLNUG)"

_ARCGIS = "https://geodienste-umwelt.hessen.de/arcgis/rest/services"
STATIONS_URL = f"{_ARCGIS}/gruschu/gruschu_mst_ga/MapServer/0/query"
SERIES_NN_URL = f"{_ARCGIS}/wasserviewer/Auswertung/MapServer/22/query"

UNIT = "m"  # m ü. NN.
ATTRIBUTION = (
    "Datenbasis: Hessisches Landesamt für Naturschutz, Umwelt und Geologie "
    "(HLNUG) – GruSchu (CC BY 4.0)"
)
_HISTORY_LIMIT = 400


# --------------------------------------------------------------------------- #
# Pure helpers (unit-tested against tests/fixtures/hlnug_he/*).
# --------------------------------------------------------------------------- #
def parse_series(features: list[dict]) -> list[tuple[datetime, float]]:
    """Parse ArcGIS ``MESSDATUM``/``MESSWERT`` rows into chronological pairs."""
    samples: list[tuple[datetime, float]] = []
    for feature in features:
        attrs = feature.get("attributes") or {}
        ms, value = attrs.get("MESSDATUM"), attrs.get("MESSWERT")
        if ms is None or not isinstance(value, (int, float)):
            continue
        when = datetime.fromtimestamp(ms / 1000, tz=UTC).replace(tzinfo=None)
        samples.append((when, float(value)))
    samples.sort(key=lambda s: s[0])
    return samples


def _to_station(feature: dict, distance_km: float | None = None) -> ProviderStation:
    attrs = feature.get("attributes") or {}
    geom = feature.get("geometry") or {}
    number = str(attrs.get("ID"))
    return ProviderStation(
        provider=DOMAIN,
        station_id=number,
        name=(attrs.get("MESSTELLENNAME") or "").strip() or number,
        latitude=geom.get("y"),
        longitude=geom.get("x"),
        distance_km=distance_km,
    )


# --------------------------------------------------------------------------- #
# Provider
# --------------------------------------------------------------------------- #
class HlnugHeProvider(Provider):
    """Groundwater provider backed by Hesse's HLNUG ArcGIS REST services."""

    domain = DOMAIN
    label = LABEL

    def __init__(self, session: ClientSession) -> None:
        """Initialise with a shared aiohttp session."""
        self._session = session

    async def async_search_radius(
        self, latitude: float, longitude: float, radius_km: float
    ) -> list[ProviderStation]:
        """Return stations within ``radius_km`` (native ArcGIS radius query)."""
        features = await query_features(
            self._session,
            STATIONS_URL,
            {
                "geometry": f"{longitude},{latitude}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "outSR": "4326",
                "distance": radius_km * 1000,
                "units": "esriSRUnit_Meter",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "ID,MESSTELLENNAME",
                "returnGeometry": "true",
            },
        )
        matches: list[ProviderStation] = []
        for station in (_to_station(f) for f in features):
            if station.latitude is None or station.longitude is None:
                continue
            station.distance_km = haversine_km(
                latitude, longitude, station.latitude, station.longitude
            )
            matches.append(station)
        matches.sort(key=lambda s: s.distance_km or 0.0)
        return matches

    async def async_search_query(self, query: str) -> list[ProviderStation]:
        """Return stations whose name or id matches ``query``."""
        needle = escape_like(query.strip())
        where = f"UPPER(MESSTELLENNAME) LIKE UPPER('%{needle}%')"
        if needle.isdigit():
            where = f"{where} OR ID = {needle}"
        features = await query_features(
            self._session,
            STATIONS_URL,
            {
                "where": where,
                "outSR": "4326",
                "outFields": "ID,MESSTELLENNAME",
                "returnGeometry": "true",
            },
        )
        return sorted(
            (_to_station(f) for f in features), key=lambda s: s.name
        )

    async def async_fetch(self, station: ProviderStation) -> ProviderReading:
        """Return the latest reading and recent history for ``station``."""
        features: list[dict[str, Any]] = []
        if station.station_id.isdigit():
            features = await query_features(
                self._session,
                SERIES_NN_URL,
                {
                    "where": f"GWM_ID = {station.station_id}",
                    "outFields": "MESSDATUM,MESSWERT",
                    "returnGeometry": "false",
                    "orderByFields": "MESSDATUM DESC",
                    "resultRecordCount": _HISTORY_LIMIT,
                },
                paginate=False,
            )
        history = parse_series(features)
        latest_ts, latest_value = history[-1] if history else (None, None)
        return ProviderReading(
            value=latest_value,
            unit=UNIT,
            timestamp=latest_ts,
            history=history,
            attribution=ATTRIBUTION,
        )
