"""Tests for the NIWIS config and options flow."""

from __future__ import annotations

import re

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.niwis.const import (
    CONF_QUERY,
    CONF_RADIUS,
    CONF_STATIONS,
    DOMAIN,
)


@pytest.fixture(autouse=True)
def _german_location(hass: HomeAssistant) -> None:
    """Place the HA instance in Germany so radius search finds stations."""
    hass.config.latitude = 49.5
    hass.config.longitude = 10.5


async def test_radius_flow_creates_entry(
    hass: HomeAssistant, mock_niwis_api: AiohttpClientMocker
) -> None:
    """A full radius-based flow creates an entry with the picked stations."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.MENU

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "radius"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "radius"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_RADIUS: 500}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "select"

    # Pick one known station number.
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_STATIONS: ["DESM_DEBY16607001"]}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    stations = result["data"][CONF_STATIONS]
    assert len(stations) == 1
    assert stations[0]["nummer"] == "DESM_DEBY16607001"
    # Surface station covers both surface measurement types.
    assert set(stations[0]["messgroessen"]) == {"WASSERSTAND", "ABFLUSS"}


async def test_query_flow_finds_station(
    hass: HomeAssistant, mock_niwis_api: AiohttpClientMocker
) -> None:
    """Search by name returns matching stations."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "query"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_QUERY: "Inkofen"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "select"


async def test_cannot_connect_shows_error(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """API errors surface as a form error, not a crash."""
    aioclient_mock.get(re.compile(r".*/karte/messstelle/.*"), status=500)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "radius"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_RADIUS: 500}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_single_instance_only(
    hass: HomeAssistant, mock_niwis_api: AiohttpClientMocker
) -> None:
    """A second config flow aborts (single hub instance)."""
    MockConfigEntry(domain=DOMAIN, unique_id=DOMAIN).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
