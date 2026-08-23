"""Path normalization helpers."""

from __future__ import annotations

import typing as tp

if tp.TYPE_CHECKING:
    import pathlib as pl


def normalize_rel_path(value: str) -> str:
    """Normalize comparable relative paths without changing semantics."""
    return value.removeprefix("./").rstrip("/")


def find_upwards(filename: pl.Path, start: pl.Path) -> pl.Path:
    """Locate `filename`, searching `start` and its parent directories.

    Mirrors how tools like `uv` and `git` locate a project file regardless of
    which subdirectory you invoke the command from: if `filename` isn't found
    relative to `start`, walk up through `start`'s parents looking for a
    same-named file. Absolute paths are returned unchanged (no search).

    Returns the first match, or `start / filename` if nothing was found --
    letting the caller raise a "not found" error against the path the user
    actually asked for.
    """
    if filename.is_absolute():
        return filename

    for directory in (start, *start.parents):
        candidate = directory / filename
        if candidate.is_file():
            return candidate

    return start / filename
