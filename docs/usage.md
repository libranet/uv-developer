# Usage

`uv-developer` manages `[tool.uv.sources]` local path overrides in `pyproject.toml`: it toggles
them on and off, optionally clones the referenced repo, shows their current state, and checks
that no override ever reaches a commit. See [Introduction](introduction.md) for the problem this
solves.

Every command locates `pyproject.toml` (and, for `check uv-lock`, `uv.lock`) by searching the
current directory and its parents, the same way `uv` locates a project root, unless you pass
`--pyproject`/`--lockfile` explicitly.

## uv-developer toggle

```console
uv-developer toggle [ACTION] [--pyproject PATH]
```

With no `ACTION`, auto-toggles: if any local source is active, switches all of them off;
otherwise switches all of them on. `ACTION` accepts `on` / `enable` / `1` and `off` / `disable`
/ `0` as explicit targets.

When switching a source on, if the local path it points at has no `pyproject.toml` yet,
`uv-developer` looks for a `# git clone ...` comment directly above the source entry and runs it
to clone the dependency first:

```toml
[tool.uv.sources]
# git clone https://github.com/libranet/libranet-logging .deps/libranet-logging
# libranet-logging = { path = ".deps/libranet-logging", editable = true }
```

If that comment is missing and the path does not exist, `toggle` does not fail the whole run --
it prints a warning and still activates the entry, leaving the clone to you.

`toggle` always prints the resulting `[tool.uv.sources]` state as a table, followed by a one-line
summary of whether anything changed:

```console
$ uv-developer toggle on
              [tool.uv.sources]
                   .                .
  Editable Package | Development Path | Status
 ------------------+-------------------+--------
  demo-lib         | .deps/demo-lib    | on

Updated /path/to/pyproject.toml
```

If everything was already in the requested state, the file is left untouched and the summary
reads `No changes in /path/to/pyproject.toml` instead.

### Pinning an entry off

A double-commented `##` entry is parsed and reported like any other entry, but `toggle on`
always skips it -- useful when you have several optional sources and only want some of them
swept up by the bulk on/off toggle. Edit it back to a single `#` by hand to make it togglable
again.

```toml
[tool.uv.sources]
demo-lib = { path = ".deps/demo-lib", editable = true }

# git clone https://example.invalid/rarely-used.git .deps/rarely-used
## rarely-used = { path = ".deps/rarely-used", editable = true }
```

`show` and `toggle` report a pinned entry with a `##` prefix on its package name and a
`pinned off` status.

## uv-developer show

```console
uv-developer show [--pyproject PATH]
```

Prints the current `[tool.uv.sources]` entries as the same table `toggle` prints, without
changing anything. Use it to check the current state before deciding whether to toggle.

## uv-developer check

```console
uv-developer check [--pyproject PATH] [--lockfile PATH]
```

Exits with status `1` if `uv.lock` resolved any package from a local or editable path declared
in `[tool.uv.sources]`. Intended for CI and as a pre-commit hook, so a local override never ships
to a machine where the path does not exist.

- `uv-developer check pyproject-toml` -- report the local path sources declared in
  `pyproject.toml`, without checking `uv.lock`.
- `uv-developer check uv-lock` -- check only `uv.lock` against the sources declared in
  `pyproject.toml`.

Running `uv-developer check` with no subcommand runs both.

### As a pre-commit hook

```yaml
repos:
  - repo: https://github.com/libranet/uv-developer
    rev: vX.Y.Z
    hooks:
      - id: uv-developer-check
```

See [Installation](installation.md) for the full setup.
