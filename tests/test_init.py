# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring
"""Testing of module uv_developer.__init__."""

import packaging.version


def test_version() -> None:
    from uv_developer import __version__

    assert isinstance(__version__, str)
    assert packaging.version.parse(__version__) >= packaging.version.parse("0.0")


def test_license() -> None:
    import uv_developer
    # from uv_developer import __license__

    assert isinstance(uv_developer.__license__, str)
    assert "Copyright" in uv_developer.__license__
