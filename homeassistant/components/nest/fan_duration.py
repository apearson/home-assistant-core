"""Helpers for per-device Nest fan duration configuration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .const import CONF_FAN_DURATION_BY_DEVICE, DEFAULT_FAN_DURATION, MAX_FAN_DURATION

CUSTOM_FAN_DURATION_OPTION = "Custom"

FAN_DURATION_PRESET_OPTIONS: tuple[tuple[str, int], ...] = (
    ("15 minutes", 900),
    ("30 minutes", 1800),
    ("45 minutes", 2700),
    ("1 hour", 3600),
    ("2 hours", 7200),
    ("4 hours", 14400),
    ("8 hours", 28800),
    ("Max (15 hours)", MAX_FAN_DURATION),
)
FAN_DURATION_PRESET_TO_SECONDS = dict(FAN_DURATION_PRESET_OPTIONS)
FAN_DURATION_SECONDS_TO_PRESET = {
    duration: option for option, duration in FAN_DURATION_PRESET_OPTIONS
}


def fan_duration_from_options(options: Mapping[str, Any], nest_device_id: str) -> int:
    """Return the configured fan duration for a Nest device."""
    fan_duration_by_device = options.get(CONF_FAN_DURATION_BY_DEVICE)
    if not isinstance(fan_duration_by_device, dict):
        return DEFAULT_FAN_DURATION

    duration = fan_duration_by_device.get(nest_device_id)
    if not isinstance(duration, int) or duration < 1 or duration > MAX_FAN_DURATION:
        return DEFAULT_FAN_DURATION
    return duration


def update_options_with_fan_duration(
    options: Mapping[str, Any], nest_device_id: str, duration: int
) -> dict[str, Any]:
    """Return updated config entry options with a fan duration override."""
    if duration < 1 or duration > MAX_FAN_DURATION:
        raise ValueError(
            f"Fan duration must be in range [1, {MAX_FAN_DURATION}] seconds"
        )

    new_options: dict[str, Any] = dict(options)
    duration_by_device = new_options.get(CONF_FAN_DURATION_BY_DEVICE)
    if not isinstance(duration_by_device, dict):
        duration_by_device = {}
    else:
        duration_by_device = dict(duration_by_device)

    duration_by_device[nest_device_id] = duration
    new_options[CONF_FAN_DURATION_BY_DEVICE] = duration_by_device
    return new_options
