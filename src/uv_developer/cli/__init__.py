"""uv_developer.cli."""

from __future__ import annotations

import cyclopts

from uv_developer.about import version
from uv_developer.cli.check import app as app_check
from uv_developer.cli.show import app as app_show
from uv_developer.cli.toggle import app as app_toggle

app: cyclopts.App = cyclopts.App(name="uv-developer", version=version)

# Change the group of "--help" and "--version" to the implicitly created "Admin" group.
app["--help"].group = "Admin"
app["--version"].group = "Admin"

# register subcommands
app.command(obj=app_check)
app.command(obj=app_show)
app.command(obj=app_toggle)
