"""uv_developer.about.

Fetch metadata from the package's pyproject.toml.
The package must be properly installed in order the metadata to be available.

"""

from __future__ import annotations  # make | in typing work in Python 3.8

import importlib.metadata

package: str = __package__ or ""


try:
    metadata: importlib.metadata.PackageMetadata | None = importlib.metadata.metadata(package)
except ValueError:  # pragma: no cover
    # A distribution name is required. __package__ is None
    metadata = None
except importlib.metadata.PackageNotFoundError:  # pragma: no cover
    # fallback if this package is not properly installed
    metadata = None


def _get(key: str) -> str | None:
    """Return a metadata field, or None when unavailable/unset."""
    return metadata.get(key) if metadata is not None else None


authors: str | list[str] = _get("Author-email") or "unknown"

# License-Expression (PEP 639) takes precedence; fall back to the legacy
# free-text License field (e.g. the full license.md contents), then "unknown".
license_: str | list[str] = _get("License-Expression") or _get("License") or "unknown"

version: str = _get("Version") or "unknown"
