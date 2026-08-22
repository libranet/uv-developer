"""uv.developer.cli.check.

Check commands for local path sources.

Usage:

    $ uv-developer check --help
    $ uv-developer check
    $ uv-developer check pyproject-toml
    $ uv-developer check uv-lock

"""

from __future__ import annotations

import pathlib as pl

import cyclopts

from uv_developer.check import (
    find_matching_local_lock_sources,
    load_local_lock_sources,
    load_source_entries,
)

# Imported at runtime (not under TYPE_CHECKING): cyclopts resolves this function's
# return annotation via typing.get_type_hints() when parsing CLI arguments, so the
# name must be resolvable in this module's namespace, not just to a type checker.
from uv_developer.models import SourceEntry  # noqa: TC001
from uv_developer.utils.paths import find_upwards

app: cyclopts.App = cyclopts.App(name="check")


@app.default()
def check(pyproject: pl.Path = pl.Path("pyproject.toml"), lockfile: pl.Path = pl.Path("uv.lock")) -> None:
    """Check both pyproject.toml and uv.lock."""
    check_pyproject_toml(pyproject=pyproject)
    check_uv_lock(pyproject=pyproject, lockfile=lockfile)


@app.command(name="pyproject-toml", sort_key=10)
def check_pyproject_toml(pyproject: pl.Path = pl.Path("pyproject.toml")) -> list[SourceEntry]:
    """Report the local path sources declared in pyproject.toml.

    `pyproject` is searched for in the current directory and its parents,
    the same way `uv` locates a project root.
    """
    pyproject = find_upwards(pyproject, pl.Path.cwd())
    if not pyproject.is_file():
        msg = f"Could not find {pyproject}"
        raise SystemExit(msg)

    entries = load_source_entries(pyproject)

    if not entries:
        print(f"OK: {pyproject} does not contain local path sources from [tool.uv.sources].")
        return []

    print(f"OK: {pyproject} contains local path sources from [tool.uv.sources]:")
    for entry in entries:
        print(f"- {entry.package}: path={entry.rel_path}")
    return entries


@app.command(name="uv-lock", sort_key=10)
def check_uv_lock(pyproject: pl.Path = pl.Path("pyproject.toml"), lockfile: pl.Path = pl.Path("uv.lock")) -> None:
    """Check that uv.lock does not contain local/editable uv sources.

    `pyproject` and `lockfile` are each searched for in the current directory
    and its parents, the same way `uv` locates a project root.
    """
    pyproject = find_upwards(pyproject, pl.Path.cwd())
    lockfile = find_upwards(lockfile, pl.Path.cwd())
    if not pyproject.is_file():
        msg = f"Could not find {pyproject}"
        raise SystemExit(msg)
    if not lockfile.is_file():
        msg = f"Could not find {lockfile}"
        raise SystemExit(msg)

    source_entries = load_source_entries(pyproject)
    lock_sources = load_local_lock_sources(lockfile)
    matches = find_matching_local_lock_sources(source_entries=source_entries, lock_sources=lock_sources)
    if not matches:
        print(f"OK: {lockfile} does not contain local path sources from [tool.uv.sources].")
        return

    print(f"ERROR: {lockfile} contains local path sources from [tool.uv.sources]:")
    for match in matches:
        print(f"- {match.name}: {match.source_type}={match.source_value} (line {match.line_no})")
    raise SystemExit(1)
