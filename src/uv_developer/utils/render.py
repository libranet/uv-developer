"""Rich-based console rendering helpers for CLI output."""

from __future__ import annotations

import typing as tp

from rich import box
from rich.console import Console
from rich.table import Table

if tp.TYPE_CHECKING:
    from uv_developer.models import SourceEntry

# markup=False: cell content includes literal file paths, which could coincidentally
# contain "[...]" -- rich's default markup parsing would silently swallow that (see
# the "[tool.uv.sources]" output bug this project hit and fixed in cli/check.py).
# Styling below uses the `style=` kwarg on rows instead of inline markup tags, so this
# stays safe regardless.
console = Console(markup=False)


def print_sources_table(entries: list[SourceEntry]) -> None:
    """Print a table of the [tool.uv.sources] entries and their resulting state."""
    if not entries:
        return

    # A short, constant title -- unlike the long absolute pyproject.toml path tried
    # earlier, this can't wrap unpredictably across console widths.
    table = Table(title="[tool.uv.sources]", header_style="none", box=box.MINIMAL)
    table.add_column("Editable Package")
    table.add_column("Development Path")
    table.add_column("Status")

    for entry in entries:
        if entry.pinned:
            marker, status, status_style = "##", "pinned off", "yellow"
        elif entry.is_active:
            marker, status, status_style = "", "on", "bold green"
        else:
            marker, status, status_style = "#", "off", "dim"

        # mirrors the actual comment-marker prefix in pyproject.toml, so the table
        # reads the same way as the file itself.
        package = f"{marker} {entry.package}" if marker else entry.package
        table.add_row(package, entry.rel_path, status, style=status_style)

    console.print(table)
    print()
