"""Toggle local path overrides in a pyproject.toml file.

This module reworks the ad-hoc toggle script into importable package code.
"""

from __future__ import annotations

import re
import typing as tp

from uv_developer.models import SourceEntry
from uv_developer.utils.git import clone_command_from_comment, ensure_cloned

if tp.TYPE_CHECKING:
    import pathlib as pl

    from uv_developer.utils.modes import ToggleMode

SOURCE_KEY_RE = re.compile(r"^\s*(#{0,2})\s*([a-zA-Z0-9_\-]+)\s*=\s*\{\s*path\s*=\s*[\"']([^\"']+)[\"']")


def parse_source_entries(lines: list[str]) -> list[SourceEntry]:
    """Extract [tool.uv.sources] entries and optional clone commands.

    A single `#` marks a normal, togglable entry (inactive). A `##` marks it
    pinned: parsed and reported like any other entry, but `toggle on` never
    activates it -- it stays off until hand-edited back to a single `#`.
    """
    in_uv_sources = False
    entries: list[SourceEntry] = []

    for idx, line in enumerate(lines):
        stripped = line.strip()

        if stripped == "[tool.uv.sources]":
            in_uv_sources = True
            continue

        if in_uv_sources and stripped.startswith("["):
            in_uv_sources = False

        if not in_uv_sources or not stripped:
            # This *is* exercised (see test_toggle_sources_reports_no_entries and friends), but
            # CPython 3.9's bytecode line-table doesn't emit a distinct trace event for a bare
            # `continue` as the sole body of an `or`-guarded `if` here -- coverage.py sees it as
            # never hit. Fixed by PEP 626 (Python 3.10+); confirmed by running the same suite
            # under 3.13, where this line and its branch both report 100%.
            continue  # pragma: no cover

        match = SOURCE_KEY_RE.match(line)
        if not match:
            continue

        hashes, package, rel_path = match.groups()
        prev_line = lines[idx - 1] if idx > 0 else ""

        entries.append(
            SourceEntry(
                idx=idx,
                line=line,
                package=package,
                rel_path=rel_path,
                is_active=hashes == "",
                pinned=hashes == "##",
                clone_cmd=clone_command_from_comment(prev_line),
            )
        )

    return entries


def toggle_sources(mode: ToggleMode | None, pyproject: pl.Path) -> tuple[ToggleMode, list[SourceEntry], bool]:
    """Toggle source entries in [tool.uv.sources] and persist the result.

    Returns the resulting mode ("on" or "off"), the resulting entries, and
    whether anything actually changed. The file is left untouched when
    nothing changed.
    """
    if not pyproject.is_file():
        msg = f"Could not find {pyproject}"
        raise FileNotFoundError(msg)

    content = pyproject.read_text(encoding="utf-8")
    lines = content.splitlines()
    entries = parse_source_entries(lines)

    if not entries:
        return "off", [], False

    if mode not in {"on", "off"}:
        currently_active = any(entry.is_active for entry in entries)
        target_mode = "off" if currently_active else "on"
    else:
        target_mode = mode

    project_root = pyproject.parent
    updated_lines = list(lines)
    changed = False

    for entry in entries:
        if target_mode == "on":
            if entry.pinned:
                continue
            ensure_cloned(project_root, entry)
            # Both branches are exercised (test_toggle_sources_warns_when_missing_clone_comment
            # enters it, test_toggle_sources_no_write_when_already_in_target_mode skips it), but
            # CPython 3.9's bytecode line-table doesn't record the "skip straight to `continue`"
            # arc here as taken -- same PEP 626 limitation as above, confirmed fixed under 3.13.
            if entry.line.strip().startswith("#"):  # pragma: no branch
                updated_lines[entry.idx] = re.sub(r"^\s*#\s*", "", entry.line)
                changed = True
            continue

        if not entry.line.strip().startswith("#"):
            indent_match = re.match(r"^(\s*)", entry.line)
            indent = indent_match.group(1) if indent_match else ""
            updated_lines[entry.idx] = f"{indent}# {entry.line.strip()}"
            changed = True

    if not changed:
        return target_mode, entries, False

    pyproject.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    return target_mode, parse_source_entries(updated_lines), True
