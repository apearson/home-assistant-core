"""Number entities for Google Nest SDM."""

from __future__ import annotations

from google_nest_sdm.device import Device
from google_nest_sdm.device_traits import FanTrait
from google_nest_sdm.thermostat_traits import ThermostatHvacTrait

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import MAX_FAN_DURATION
from .device_info import NestDeviceInfo
from .fan_duration import fan_duration_from_options, update_options_with_fan_duration
from .types import NestConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NestConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Nest fan duration number entities."""

    def devices_added(devices: list[Device]) -> None:
        async_add_entities(
            NestFanDurationNumberEntity(device, entry)
            for device in devices
            if FanTrait.NAME in device.traits
            and ThermostatHvacTrait.NAME in device.traits
        )

    entry.runtime_data.register_devices_listener(devices_added)


class NestFanDurationNumberEntity(NumberEntity):
    """Nest thermostat fan timer duration in seconds."""

    _attr_has_entity_name = True
    _attr_name = "Fan duration"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 1
    _attr_native_max_value = MAX_FAN_DURATION
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS

    def __init__(self, device: Device, config_entry: NestConfigEntry) -> None:
        """Initialize fan duration number entity."""
        self._device = device
        self._config_entry = config_entry
        self._attr_unique_id = f"{device.name}-fan-duration"
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
    def native_value(self) -> float:
        """Return the fan duration in seconds."""
        return fan_duration_from_options(self._config_entry.options, self._device.name)

    async def async_set_native_value(self, value: float) -> None:
        """Set the fan duration in seconds."""
        if int(value) != value:
            raise ValueError("Fan duration must be in whole seconds")

        duration = int(value)
        self.hass.config_entries.async_update_entry(
            self._config_entry,
            options=update_options_with_fan_duration(
                self._config_entry.options, self._device.name, duration
            ),
        )
        self.async_write_ha_state()
