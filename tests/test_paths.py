"""Tests for uv_developer.utils.paths."""

import pathlib as pl

import pytest

from uv_developer.utils.paths import find_upwards, normalize_rel_path


def test_normalize_rel_path_strips_leading_dot_and_trailing_slash() -> None:
    """Test comparable relative paths are normalized without changing semantics."""
    assert normalize_rel_path("./demo/") == "demo"
    assert normalize_rel_path("demo") == "demo"


def test_find_upwards_returns_file_in_start_dir(tmp_path: pl.Path) -> None:
    """Test the file is found directly in the start directory."""
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")

    found = find_upwards(pl.Path("pyproject.toml"), tmp_path)

    assert found == tmp_path / "pyproject.toml"


def test_find_upwards_searches_parent_directories(tmp_path: pl.Path) -> None:
    """Test the file is located by walking up from a nested subdirectory."""
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    nested = tmp_path / "src" / "pkg"
    nested.mkdir(parents=True)

    found = find_upwards(pl.Path("pyproject.toml"), nested)

    assert found == tmp_path / "pyproject.toml"


def test_find_upwards_leaves_absolute_paths_unchanged(tmp_path: pl.Path) -> None:
    """Test an absolute path is returned as-is, without searching."""
    absolute = tmp_path / "elsewhere" / "pyproject.toml"

    found = find_upwards(absolute, tmp_path)

    assert found == absolute


def test_find_upwards_falls_back_to_start_when_not_found(tmp_path: pl.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test a missing file resolves against `start`, for a clean "not found" error.

    Forces `Path.is_file` to always report "missing", regardless of the real filesystem --
    this project's own `.env` points `TMPDIR` at a directory *inside* the repo (see
    `.env.template`), so without this, `tmp_path` fixtures can end up nested under a real
    ancestor `pyproject.toml`, which would make the upward search find that instead.
    """
    monkeypatch.setattr(pl.Path, "is_file", lambda self: False)  # noqa: ARG005
    nested = tmp_path / "src" / "pkg"
    nested.mkdir(parents=True)

    found = find_upwards(pl.Path("pyproject.toml"), nested)

    assert found == nested / "pyproject.toml"
