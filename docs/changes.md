# Changelog

All notable changes to this project will be documented anti-chronologically in this file.

## 0.2 (2026-11-03)

- Drop support for Python 3.9 and 3.10 (both end-of-life); `requires-python` is now `>=3.11`.
  Removes the 3.9-only workarounds (`tp.Optional` for cyclopts, coverage pragmas for the
  pre-PEP 626 line table), targets ruff at `py311`, and defaults `.python-version` to 3.11.

## 0.1.1 (2026-11-03)

Maintenance release: no changes to the package code or its runtime dependencies.

- Widen the build-backend cap to `uv_build>=0.10,<0.14.0`.

- Replace Dependabot with Renovate. Non-major updates auto-merge once CI passes, `uv.lock` gets
  a monthly lock-file maintenance run, and `cyclopts` is held at `<4` (cyclopts 4 makes
  `App.__call__` always `sys.exit()`, which breaks the CLI tests).

- Upgrade all locked dependencies within the `exclude-newer = "10 days"` window, including
  ruff 0.17.2, ty 0.0.91, prek 0.5.9 and mutmut 3.8.0. The lock records `exclude-newer-span`
  again, so CI installs from it instead of re-resolving (which failed on Python 3.14 / 3.15).

- Upgrade the docs toolchain: sphinx 9.2, myst-parser 5, sphinx-click 6 and furo 2025.

- Default `.python-version` to Python 3.10.

- CI: bump the pinned GitHub Actions (setup-uv, upload/download-artifact, codecov,
  gh-action-pypi-publish, zizmor-action) and mark the `setup-just` steps with an inline zizmor
  ignore, since just is pinned via `env.JUST_VERSION` (clears code-scanning alerts #1, #3, #9).

## 0.1 (2026-08-23)

- Package created by \[Wouter Vanden Hove <wouter@libranet.eu>\]
