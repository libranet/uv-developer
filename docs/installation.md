# Installation

## Requirements

- Python >= 3.9
- [uv](https://docs.astral.sh/uv/), to resolve and install the local-path overrides once
  `toggle` has enabled them

## As a project dependency

Add `uv-developer` as a dev dependency of the project whose `[tool.uv.sources]` you want to
manage:

```console
uv add --dev uv-developer
```

Or with pip, into whatever environment your tooling runs in:

```console
pip install uv-developer
```

Either way, this installs the `uv-developer` command. Confirm it is on your `PATH`:

```console
uv-developer --version
```

## As a pre-commit hook

`uv-developer check` is meant to run in CI and as a pre-commit hook, so a local
`[tool.uv.sources]` override never reaches a commit. Add it to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/libranet/uv-developer
    rev: vX.Y.Z
    hooks:
      - id: uv-developer-check
```

Replace `vX.Y.Z` with the released tag you want to pin to, then install the hook:

```console
pre-commit install
```

See [Usage](usage.md) for what `check` verifies and what a failure looks like.
