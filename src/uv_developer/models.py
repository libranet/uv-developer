"""Shared domain models for uv_developer."""

from __future__ import annotations

import dataclasses as dc


@dc.dataclass(frozen=True)
class SourceEntry:
    """A [tool.uv.sources] entry and metadata needed to toggle it."""

    idx: int
    line: str
    package: str
    rel_path: str
    is_active: bool
    pinned: bool
    clone_cmd: str | None


@dc.dataclass(frozen=True)
class LocalSourcePackage:
    """A package entry in uv.lock resolved from a local path/editable source."""

    name: str
    source_type: str
    source_value: str
    line_no: int
