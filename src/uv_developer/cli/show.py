"""Show command."""

from __future__ import annotations

import pathlib as pl

import cyclopts

from uv_developer.check import load_source_entries
from uv_developer.utils.paths import find_upwards
from uv_developer.utils.render import print_sources_table

app: cyclopts.App = cyclopts.App(name="show")


@app.default()
def show(pyproject: pl.Path = pl.Path("pyproject.toml")) -> None:
    """Show the current [tool.uv.sources] local path overrides and their state.

    `pyproject` is searched for in the current directory and its parents,
    the same way `uv` locates a project root.
    """
    resolved_pyproject = find_upwards(pyproject, pl.Path.cwd())
    if not resolved_pyproject.is_file():
        msg = f"Could not find {resolved_pyproject}"
        raise SystemExit(msg)

    print(f"Checking {resolved_pyproject}")

    entries = load_source_entries(resolved_pyproject)
    if not entries:
        print("No local path sources found under [tool.uv.sources].")
        return

    print_sources_table(entries)
