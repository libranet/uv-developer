"""Git-related helpers."""

from __future__ import annotations

import re
import shlex
import subprocess
import typing as tp

if tp.TYPE_CHECKING:
    import pathlib as pl

    from uv_developer.models import SourceEntry

GIT_CLONE_RE = re.compile(r"^\s*#\s*(git\s+clone\s+.+)")


def clone_command_from_comment(line: str) -> str | None:
    """Extract a git clone command from a preceding comment line."""
    match = GIT_CLONE_RE.match(line)
    return match.group(1) if match else None


def ensure_cloned(project_root: pl.Path, entry: SourceEntry) -> None:
    """Best-effort: clone the local source path if a `# git clone ...` comment is present.

    The clone comment is optional. When it's missing and the path has no
    pyproject.toml yet, this only warns -- it never blocks toggling the entry on,
    since the developer may already be about to clone it by hand.
    """
    target_dir = project_root / entry.rel_path
    pyproject_file = target_dir / "pyproject.toml"

    if pyproject_file.is_file():
        return

    print(f"--> '{entry.package}' missing pyproject.toml at {entry.rel_path}")

    if not entry.clone_cmd:
        print(f"--> WARNING: no '# git clone ...' comment found above '{entry.package}'; leaving as-is.")
        return

    print(f"--> Auto-cloning repository: {entry.clone_cmd}")
    # shell=False: the command is parsed into argv rather than handed to a shell,
    # since it always matches GIT_CLONE_RE ("git clone ...") and never needs shell features.
    # The command itself is trusted, developer-authored content from pyproject.toml, not
    # external/untrusted input.
    subprocess.run(shlex.split(entry.clone_cmd), check=True, cwd=project_root)  # noqa: S603
