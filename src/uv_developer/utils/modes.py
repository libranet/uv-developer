"""Mode normalization helpers."""

from __future__ import annotations

import typing as tp

ToggleMode = tp.Literal["on", "off"]


def normalize_toggle_mode(action: str | None) -> ToggleMode | None:
    """Normalize action aliases to "on", "off", or None (auto-toggle)."""
    if action is None:
        return None

    lowered = action.lower()
    if lowered in {"on", "enable", "true", "1"}:
        return "on"
    if lowered in {"off", "disable", "false", "0"}:
        return "off"
    return None
