"""Select entities for Google Nest SDM."""

from __future__ import annotations

from google_nest_sdm.device import Device
from google_nest_sdm.device_traits import FanTrait
from google_nest_sdm.thermostat_traits import ThermostatHvacTrait

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .device_info import NestDeviceInfo
from .fan_duration import (
    CUSTOM_FAN_DURATION_OPTION,
    FAN_DURATION_PRESET_OPTIONS,
    FAN_DURATION_PRESET_TO_SECONDS,
    FAN_DURATION_SECONDS_TO_PRESET,
    fan_duration_from_options,
    update_options_with_fan_duration,
)
from .types import NestConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NestConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Nest fan duration preset select entities."""

    def devices_added(devices: list[Device]) -> None:
        async_add_entities(
            NestFanDurationPresetSelectEntity(device, entry)
            for device in devices
            if FanTrait.NAME in device.traits
            and ThermostatHvacTrait.NAME in device.traits
        )

    entry.runtime_data.register_devices_listener(devices_added)


class NestFanDurationPresetSelectEntity(SelectEntity):
    """Nest thermostat fan timer duration preset."""

    _attr_has_entity_name = True
    _attr_name = "Fan duration preset"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = [option for option, _ in FAN_DURATION_PRESET_OPTIONS] + [
        CUSTOM_FAN_DURATION_OPTION
    ]

    def __init__(self, device: Device, config_entry: NestConfigEntry) -> None:
        """Initialize fan duration preset select entity."""
        self._device = device
        self._config_entry = config_entry
        self._attr_unique_id = f"{device.name}-fan-duration-preset"
        self._attr_device_info = NestDeviceInfo(device).device_info

    async def async_added_to_hass(self) -> None:
        """Register for config entry option updates."""
        self.async_on_remove(
            self._config_entry.add_update_listener(self._handle_config_entry_update)
        )

    async def _handle_config_entry_update(
        self, hass: HomeAssistant, config_entry: NestConfigEntry
    ) -> None:
        """Handle config entry options update."""
        self.async_write_ha_state()

    @property
    def current_option(self) -> str:
        """Return the active preset option."""
        duration = fan_duration_from_options(
            self._config_entry.options, self._device.name
        )
        return FAN_DURATION_SECONDS_TO_PRESET.get(duration, CUSTOM_FAN_DURATION_OPTION)

    async def async_select_option(self, option: str) -> None:
        """Set a fan duration preset."""
        if option == CUSTOM_FAN_DURATION_OPTION:
            self.async_write_ha_state()
            return

        self.hass.config_entries.async_update_entry(
            self._config_entry,
            options=update_options_with_fan_duration(
                self._config_entry.options,
                self._device.name,
                FAN_DURATION_PRESET_TO_SECONDS[option],
            ),
        )
        self.async_write_ha_state()
