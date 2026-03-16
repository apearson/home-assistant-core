"""Tests for Nest fan duration config entities."""

from typing import Any

import pytest

from homeassistant.components.nest.const import DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from .common import DEVICE_ID, CreateDevice, PlatformSetup


@pytest.fixture
def platforms() -> list[str]:
    """Fixture to specify platforms to test."""
    return ["number", "select"]


@pytest.fixture
def device_traits() -> dict[str, Any]:
    """Fixture that sets default traits used for devices."""
    return {"sdm.devices.traits.Info": {"customName": "My Thermostat"}}


async def test_fan_duration_number_updates_options(
    hass: HomeAssistant,
    setup_platform: PlatformSetup,
    create_device: CreateDevice,
) -> None:
    """Test updating fan duration via the config number entity."""
    create_device.create(
        {
            "sdm.devices.traits.Fan": {
                "timerMode": "OFF",
                "timerTimeout": "2019-05-10T03:22:54Z",
            },
            "sdm.devices.traits.ThermostatHvac": {
                "status": "OFF",
            },
            "sdm.devices.traits.ThermostatMode": {
                "availableModes": ["HEAT", "COOL", "HEATCOOL", "OFF"],
                "mode": "HEAT",
            },
        }
    )
    await setup_platform()

    number_entity_id = "number.my_thermostat_fan_duration"
    preset_entity_id = "select.my_thermostat_fan_duration_preset"

    number_state = hass.states.get(number_entity_id)
    assert number_state is not None
    assert number_state.state == "43200"

    preset_state = hass.states.get(preset_entity_id)
    assert preset_state is not None
    assert preset_state.state == "Max (15 hours)"

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    await hass.services.async_call(
        "number",
        "set_value",
        {
            ATTR_ENTITY_ID: number_entity_id,
            "value": 901,
        },
        blocking=True,
    )

    assert entry.options == {"fan_duration_by_device": {DEVICE_ID: 901}}

    number_state = hass.states.get(number_entity_id)
    assert number_state is not None
    assert number_state.state == "901"

    preset_state = hass.states.get(preset_entity_id)
    assert preset_state is not None
    assert preset_state.state == "Custom"


async def test_fan_duration_select_updates_options(
    hass: HomeAssistant,
    setup_platform: PlatformSetup,
    create_device: CreateDevice,
) -> None:
    """Test updating fan duration via the preset select entity."""
    create_device.create(
        {
            "sdm.devices.traits.Fan": {
                "timerMode": "OFF",
                "timerTimeout": "2019-05-10T03:22:54Z",
            },
            "sdm.devices.traits.ThermostatHvac": {
                "status": "OFF",
            },
            "sdm.devices.traits.ThermostatMode": {
                "availableModes": ["HEAT", "COOL", "HEATCOOL", "OFF"],
                "mode": "HEAT",
            },
        }
    )
    await setup_platform()

    number_entity_id = "number.my_thermostat_fan_duration"
    preset_entity_id = "select.my_thermostat_fan_duration_preset"

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    await hass.services.async_call(
        "select",
        "select_option",
        {
            ATTR_ENTITY_ID: preset_entity_id,
            "option": "30 minutes",
        },
        blocking=True,
    )

    assert entry.options == {"fan_duration_by_device": {DEVICE_ID: 1800}}

    number_state = hass.states.get(number_entity_id)
    assert number_state is not None
    assert number_state.state == "1800"

    preset_state = hass.states.get(preset_entity_id)
    assert preset_state is not None
    assert preset_state.state == "30 minutes"
