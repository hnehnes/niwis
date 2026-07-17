"""Tests for the Bayern (GKD) groundwater provider.

Pure helpers run against **real captured** GKD Bayern responses in
``tests/fixtures/gkd_by/`` (a trimmed product overview page embedding the
Leaflet ``pointer`` array, and a trimmed ``…/messwerte`` detail page); the async
methods run through a tiny fake session.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from custom_components.grundwasser_de.providers.base import ProviderStation
from custom_components.grundwasser_de.providers.gkd_by import (
    GkdByProvider,
    extract_pointer,
    parse_detail,
    pointer_records,
)

_FIXTURES = Path(__file__).parent / "fixtures" / "gkd_by"


def _load(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Pure helpers
# --------------------------------------------------------------------------- #
def test_extract_pointer_reads_embedded_array() -> None:
    """The embedded Leaflet ``pointer`` JSON is recovered from the page HTML."""
    pointer = extract_pointer(_load("landing_gwo.html"))
    assert [p["p"] for p in pointer] == ["16704", "16705", "18042", "19999"]


def test_pointer_records_parses_coords_and_value() -> None:
    """Records carry WGS84 coords, the German-comma value and a timestamp."""
    by_id = {r["station_id"]: r for r in pointer_records(_load("landing_gwo.html"))}
    kp95 = by_id["16704"]
    assert kp95["name"] == "München KP 95"
    assert kp95["lat"] == 48.1288
    assert kp95["lon"] == 11.5863
    assert kp95["value"] == 509.02
    assert kp95["timestamp"] == datetime(2026, 7, 16, 10, 0)
    assert kp95["uri"].endswith("muenchen-kp-95-16704/messwerte")


def test_pointer_records_drops_missing_coords_and_value() -> None:
    """A station at lat/lon < 1 with an empty value parses to ``None``s."""
    by_id = {r["station_id"]: r for r in pointer_records(_load("landing_gwo.html"))}
    empty = by_id["19999"]
    assert empty["lat"] is None
    assert empty["lon"] is None
    assert empty["value"] is None
    assert empty["timestamp"] is None


def test_parse_detail_current_value_and_series() -> None:
    """The detail page yields the current value (m ü. NN) and a daily series."""
    value, timestamp, history = parse_detail(_load("detail_16704.html"))
    assert value == 509.02
    assert timestamp == datetime(2026, 7, 16, 9, 0)
    assert len(history) == 8
    assert history[0] == (datetime(2026, 7, 9), 509.0)
    assert history[-1] == (datetime(2026, 7, 16), 509.02)
    assert all(a[0] <= b[0] for a, b in zip(history, history[1:], strict=False))


# --------------------------------------------------------------------------- #
# Provider (fake session)
# --------------------------------------------------------------------------- #
class _FakeResponse:
    def __init__(self, text: str) -> None:
        self._text = text
        self.status = 200

    async def __aenter__(self) -> _FakeResponse:
        return self

    async def __aexit__(self, *exc) -> None:
        return None

    async def text(self, **_: object) -> str:
        return self._text


class _FakeSession:
    """Serves the landing fixture for product pages, the detail fixture per station."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def get(self, url: str, **_: object) -> _FakeResponse:
        self.calls.append(url)
        if url.endswith("/messwerte"):
            return _FakeResponse(_load("detail_16704.html"))
        # both product overview pages resolve to the same trimmed landing fixture
        return _FakeResponse(_load("landing_gwo.html"))


async def test_search_radius_returns_nearby_stations() -> None:
    """Search around München returns the nearby stations, nearest first."""
    provider = GkdByProvider(_FakeSession())  # type: ignore[arg-type]
    stations = await provider.async_search_radius(48.14, 11.58, 10)
    ids = [s.station_id for s in stations]
    # both München stations within 10 km; Passau (~180 km) excluded; no-coords dropped
    assert ids == ["16704", "16705"]
    assert stations[0].provider == "gkd_by"
    assert stations[0].distance_km is not None and stations[0].distance_km < 2
    assert stations[0].extra["uri"].endswith("muenchen-kp-95-16704/messwerte")


async def test_search_query_matches_name() -> None:
    """A free-text query matches on station name."""
    provider = GkdByProvider(_FakeSession())  # type: ignore[arg-type]
    stations = await provider.async_search_query("passau")
    assert [s.station_id for s in stations] == ["18042"]


async def test_fetch_returns_latest_and_history() -> None:
    """Fetch uses the stored detail URL and returns the value (m ü. NN) + series."""
    provider = GkdByProvider(_FakeSession())  # type: ignore[arg-type]
    reading = await provider.async_fetch(
        ProviderStation(
            provider="gkd_by",
            station_id="16704",
            name="München KP 95",
            extra={"uri": "https://www.gkd.bayern.de/de/x/muenchen-kp-95-16704/messwerte"},
        )
    )
    assert reading.value == 509.02
    assert reading.unit == "m"
    assert reading.timestamp == datetime(2026, 7, 16, 9, 0)
    assert len(reading.history) == 8
    assert "Bayerisches Landesamt für Umwelt" in reading.attribution


async def test_fetch_resolves_uri_when_missing() -> None:
    """With no stored URL, fetch resolves it from the product pages (fallback)."""
    session = _FakeSession()
    provider = GkdByProvider(session)  # type: ignore[arg-type]
    reading = await provider.async_fetch(
        ProviderStation(provider="gkd_by", station_id="16704", name="x")
    )
    assert reading.value == 509.02
    # the fallback fetched a product page before the detail page
    assert any(u.endswith("/messwerte") for u in session.calls)
    assert any(
        "grundwasser" in u and not u.endswith("/messwerte") for u in session.calls
    )
