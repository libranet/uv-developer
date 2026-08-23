# uv-developer

_The name is a pun on [mr.developer], the zc.buildout extension that solved the same
"toggle a dependency to a local checkout while developing" problem for buildout-based projects._

[![PyPI](https://img.shields.io/pypi/v/uv-developer.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/uv-developer.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/uv-developer)][pypi status]
[![License](https://img.shields.io/pypi/l/uv-developer)][license]

[![Read the documentation at https://uv-developer.readthedocs.io/](https://img.shields.io/readthedocs/uv-developer/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/libranet/uv-developer/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/libranet/uv-developer/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)][ruff]

## Features

- Toggle `[tool.uv.sources]` local path overrides in `pyproject.toml` on and off in one command.
- Auto-clones a dependency from a `# git clone ...` comment the first time you switch it on.
- Pin a rarely-used override off with `##` so a bulk `toggle on` never sweeps it up.
- `check` fails CI or a pre-commit hook if a local/editable path ever reaches `uv.lock`.

See [Introduction] for the full problem this solves.

## Requirements

- Python >= 3.9
- [uv]

## Installation

You can install _uv-developer_ via [pip] from [PyPI]:

```console
pip install uv-developer
```

See [Installation] for adding it as a project dependency or a pre-commit hook.

## Usage

Please see the [Command-line Reference] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_uv-developer_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@libranet]'s [Kickstart Python Project] template.

<!-- github-only -->

[@libranet]: https://github.com/libranet
[codecov]: https://app.codecov.io/gh/libranet/uv-developer
[command-line reference]: https://uv-developer.readthedocs.io/en/latest/usage.html
[contributor guide]: https://github.com/libranet/uv-developer/blob/main/docs/contributing.md
[file an issue]: https://github.com/libranet/uv-developer/issues
[installation]: https://uv-developer.readthedocs.io/en/latest/installation.html
[introduction]: https://uv-developer.readthedocs.io/en/latest/introduction.html
[kickstart python project]: https://github.com/libranet/kickstart-python-project
[license]: https://github.com/libranet/uv-developer/blob/main/docs/license.md
[mr.developer]: https://github.com/fschulze/mr.developer
[pip]: https://pip.pypa.io/
[pre-commit]: https://github.com/pre-commit/pre-commit
[pypi]: https://pypi.org/
[pypi status]: https://pypi.org/project/uv-developer/
[read the docs]: https://uv-developer.readthedocs.io/
[ruff]: https://github.com/astral-sh/ruff
[tests]: https://github.com/libranet/uv-developer/actions?workflow=Tests
[uv]: https://docs.astral.sh/uv/
