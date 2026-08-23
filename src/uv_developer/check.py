"""Utilities to validate that uv.lock does not contain local path sources."""

from __future__ import annotations

import re
import typing as tp

from uv_developer.models import LocalSourcePackage, SourceEntry
from uv_developer.toggle import parse_source_entries
from uv_developer.utils.paths import normalize_rel_path

if tp.TYPE_CHECKING:
    import pathlib as pl

PACKAGE_START_RE = re.compile(r"^\s*\[\[package\]\]\s*$")
PACKAGE_NAME_RE = re.compile(r'^\s*name\s*=\s*"([^"]+)"\s*$')
SOURCE_LOCAL_RE = re.compile(r'^\s*source\s*=\s*\{[^}]*\b(path|editable)\s*=\s*"([^"]+)"')


def load_source_entries(pyproject: pl.Path) -> list[SourceEntry]:
    """Return the local path sources declared in pyproject.toml."""
    pyproject_lines = pyproject.read_text(encoding="utf-8").splitlines()
    return parse_source_entries(pyproject_lines)


def load_local_lock_sources(lockfile: pl.Path) -> list[LocalSourcePackage]:
    """Return the local path sources declared in uv.lock."""
    lock_lines = lockfile.read_text(encoding="utf-8").splitlines()
    matches: list[LocalSourcePackage] = []

    in_package = False
    current_name: str | None = None

    for idx, line in enumerate(lock_lines, start=1):
        if PACKAGE_START_RE.match(line):
            in_package = True
            current_name = None
            continue

        if not in_package:
            continue

        name_match = PACKAGE_NAME_RE.match(line)
        if name_match and current_name is None:
            current_name = name_match.group(1)
            continue

        source_match = SOURCE_LOCAL_RE.match(line)
        if source_match and current_name is not None:
            source_type, source_value = source_match.groups()
            matches.append(
                LocalSourcePackage(
                    name=current_name,
                    source_type=source_type,
                    source_value=source_value,
                    line_no=idx,
                )
            )

    return matches


def find_matching_local_lock_sources(
    source_entries: list[SourceEntry], lock_sources: list[LocalSourcePackage]
) -> list[LocalSourcePackage]:
    """Return uv.lock entries that match [tool.uv.sources] package/path entries."""
    source_packages = {entry.package for entry in source_entries}
    source_paths = {normalize_rel_path(entry.rel_path) for entry in source_entries}

    matches: list[LocalSourcePackage] = []

    for lock_source in lock_sources:
        normalized_source = normalize_rel_path(lock_source.source_value)

        if lock_source.name in source_packages or normalized_source in source_paths:
            matches.append(lock_source)

    return matches
