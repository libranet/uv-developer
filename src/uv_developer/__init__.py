"""uv_developer.

[tool.uv.sources]
# enable temporary local path overrides for development, but never commit
# the key name must match the actual normalized project.name in pyproject.toml.

# git clone git@github.com:libranet/sitecustomize-entrypoints.git .deps/sitecustomize-entrypoints
# sitecustomize-entrypoints = { path = ".deps2/sitecustomize-entrypoints", editable = true }

# git clone https://github.com/libranet/libranet-logging .deps/libranet-logging
# libranet-logging = { path = ".deps/libranet-logging", editable = true }


"""

from uv_developer.about import (
    authors as __author__,
)
from uv_developer.about import (
    license_ as __license__,
)
from uv_developer.about import (
    version as __version__,
)

__all__: list[str] = [
    "__author__",
    "__license__",
    "__version__",
]
