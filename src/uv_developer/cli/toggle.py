"""Toggle command."""

from __future__ import annotations

import pathlib as pl
import typing as tp  # `X | None` breaks cyclopts' runtime introspection on Python 3.9

import cyclopts

from uv_developer.toggle import toggle_sources
from uv_developer.utils.modes import normalize_toggle_mode
from uv_developer.utils.paths import find_upwards
from uv_developer.utils.render import print_sources_table

app: cyclopts.App = cyclopts.App(name="toggle")


@app.default()
def toggle(action: tp.Optional[str] = None, pyproject: pl.Path = pl.Path("pyproject.toml")) -> None:  # noqa: UP045
    """Toggle [tool.uv.sources] local path overrides in pyproject.toml.

    By default (no action), the command auto-toggles:
    - if any local source is active, switches all to off
    - otherwise switches all to on

    `pyproject` is searched for in the current directory and its parents,
    the same way `uv` locates a project root.
    """
    mode = normalize_toggle_mode(action)
    resolved_pyproject = find_upwards(pyproject, pl.Path.cwd())

    try:
        _, entries, changed = toggle_sources(mode=mode, pyproject=resolved_pyproject)
    except FileNotFoundError as err:
        raise SystemExit(str(err)) from err

    print_sources_table(entries)
    print(f"Updated {resolved_pyproject}" if changed else f"No changes in {resolved_pyproject}")
