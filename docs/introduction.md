# Introduction

Many Python projects depend on other, related packages. Sometimes you need to work on one of
those dependencies at the same time as the project that consumes it: fixing a bug upstream while
you are in the middle of using it downstream.

The usual fix is to point `[tool.uv.sources]` at a local, editable checkout of the dependency
while you work:

```toml
[tool.uv.sources]
my-dependency = { path = "../my-dependency", editable = true }
```

That works, but it is easy to forget to undo it. If a local `path` override slips into a commit,
`uv.lock` resolves against it, and CI has no idea what `../my-dependency` is supposed to be -- the
build breaks on any machine that does not have your local checkout. `uv` has no built-in workflow
for "temporarily go editable, then guarantee I did not commit that."

## What uv-developer does

`uv-developer` manages that workflow for you:

- `uv-developer toggle` flips every local-path entry under `[tool.uv.sources]` between commented
  (off) and active (on) in one command, optionally cloning the dependency first if it is not
  checked out yet.
- `uv-developer show` reports the current state of every entry without changing anything.
- `uv-developer check` fails (for CI or a pre-commit hook) if a local or editable path ever makes
  it into `uv.lock`, so an override left active by accident is caught before it is merged.

## How it recognizes an entry

`uv-developer` does not run a full TOML parser against `[tool.uv.sources]`; it edits it as text,
line by line, so the file keeps its comments and formatting. An entry's leading `#` characters
are what encode its state:

| Prefix | Meaning                                                |
| ------ | ------------------------------------------------------ |
| none   | active: `uv` resolves this package from the local path |
| `#`    | off: a normal, togglable entry                         |
| `##`   | pinned off: `toggle on` always skips it                |

A `# git clone ...` comment placed directly above an entry lets `toggle on` clone the dependency
automatically the first time, if the local path does not exist yet. See [Usage](usage.md) for
how pinning and cloning work in full.

See [Installation](installation.md) to add `uv-developer` to a project, and [Usage](usage.md) for
the full command reference.
