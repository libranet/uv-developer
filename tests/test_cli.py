"""Tests for module uv_developer.cli."""

import pathlib as pl

import pytest


def _write_pyproject(pyproject: pl.Path, source_line: str) -> None:
    pyproject.write_text(
        f'[project]\nname = "demo"\nversion = "0.1.0"\n\n[tool.uv.sources]\n{source_line}\n',
        encoding="utf-8",
    )


def _write_uv_lock(lockfile: pl.Path, package_name: str, source_line: str) -> None:
    lockfile.write_text(
        "\n".join(
            [
                "version = 1",
                "",
                "[[package]]",
                f'name = "{package_name}"',
                'version = "0.1.0"',
                source_line,
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_cli_help(tmp_path: pl.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Test that the root command shows help without a default action."""
    from uv_developer.cli import app

    monkeypatch.chdir(tmp_path)
    app([])

    out = capsys.readouterr().out
    assert "Usage: uv-developer COMMAND" in out
    assert "toggle" in out


def test_app_version(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that --version flag works."""
    from uv_developer.about import version
    from uv_developer.cli import app

    # Invoke the app with --version flag
    app(["--version"])

    captured = capsys.readouterr()
    assert str(version) in captured.out


def test_cli_enable_with_alias(tmp_path: pl.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test that 'enable' alias activates commented source entries."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    dep_dir = tmp_path / ".deps" / "demo-lib"
    dep_dir.mkdir(parents=True)
    (dep_dir / "pyproject.toml").write_text("[project]\nname='demo-lib'\n", encoding="utf-8")

    _write_pyproject(pyproject, '# demo-lib = { path = ".deps/demo-lib", editable = true }')

    app(["toggle", "enable", "--pyproject", str(pyproject)])

    content = pyproject.read_text(encoding="utf-8")
    assert 'demo-lib = { path = ".deps/demo-lib", editable = true }' in content
    assert '# demo-lib = { path = ".deps/demo-lib", editable = true }' not in content

    out = capsys.readouterr().out
    assert f"Updated {pyproject}" in out
    assert "demo-lib" in out
    assert "on" in out


def test_cli_toggle_missing_pyproject_exits(tmp_path: pl.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test toggle exits cleanly when no pyproject.toml can be found anywhere upwards.

    Forces `Path.is_file` to always report "missing", regardless of the real filesystem --
    this project's own `.env` points `TMPDIR` at a directory *inside* the repo (see
    `.env.template`), so without this, `tmp_path` can end up nested under a real ancestor
    `pyproject.toml`, which would make the upward search find that instead.
    """
    from uv_developer.cli import app

    monkeypatch.setattr(pl.Path, "is_file", lambda self: False)  # noqa: ARG005
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        app(["toggle"])

    assert "Could not find" in str(exc_info.value.code)


def test_cli_toggle_reports_no_changes(tmp_path: pl.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test toggling to the mode that's already active reports no changes."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    dep_dir = tmp_path / ".deps" / "demo-lib"
    dep_dir.mkdir(parents=True)
    (dep_dir / "pyproject.toml").write_text("[project]\nname='demo-lib'\n", encoding="utf-8")

    _write_pyproject(pyproject, 'demo-lib = { path = ".deps/demo-lib", editable = true }')

    app(["toggle", "enable", "--pyproject", str(pyproject)])

    out = capsys.readouterr().out
    assert f"No changes in {pyproject}" in out
    assert f"Updated {pyproject}" not in out
    # the table is shown regardless of whether anything changed
    assert "demo-lib" in out
    assert "on" in out


def test_cli_toggle_finds_pyproject_in_parent_dir(
    tmp_path: pl.Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test toggle locates pyproject.toml from a subdirectory, without --pyproject."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    dep_dir = tmp_path / ".deps" / "demo-lib"
    dep_dir.mkdir(parents=True)
    (dep_dir / "pyproject.toml").write_text("[project]\nname='demo-lib'\n", encoding="utf-8")

    _write_pyproject(pyproject, '# demo-lib = { path = ".deps/demo-lib", editable = true }')

    subdir = tmp_path / "sub" / "sub"
    subdir.mkdir(parents=True)
    monkeypatch.chdir(subdir)

    app(["toggle", "enable"])

    content = pyproject.read_text(encoding="utf-8")
    assert 'demo-lib = { path = ".deps/demo-lib", editable = true }' in content

    out = capsys.readouterr().out
    assert f"Updated {pyproject}" in out
    assert "demo-lib" in out


def test_no_local_uv_sources_ok_when_registry_sources(tmp_path: pl.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """check-uv-lock should pass when lockfile has only registry sources."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    lockfile = tmp_path / "uv.lock"

    _write_pyproject(pyproject, 'demo-lib = { path = ".deps/demo-lib", editable = true }')
    _write_uv_lock(lockfile, "demo-lib", 'source = { registry = "https://pypi.org/simple" }')

    app(["check", "uv-lock", "--pyproject", str(pyproject), "--lockfile", str(lockfile)])
    out = capsys.readouterr().out
    assert f"OK: {lockfile} does not contain local path sources from [tool.uv.sources]." in out


def test_no_local_uv_sources_fails_when_local_source_matches_pyproject(
    tmp_path: pl.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """check-uv-lock should fail for local source from tool.uv.sources."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    lockfile = tmp_path / "uv.lock"

    _write_pyproject(pyproject, 'demo-lib = { path = ".deps/demo-lib", editable = true }')
    _write_uv_lock(lockfile, "demo-lib", 'source = { editable = ".deps/demo-lib" }')

    with pytest.raises(SystemExit) as exc_info:
        app(["check", "uv-lock", "--pyproject", str(pyproject), "--lockfile", str(lockfile)])

    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert f"ERROR: {lockfile} contains local path sources from [tool.uv.sources]:" in out
    assert "demo-lib" in out


def test_check_pyproject_toml_reports_sources(tmp_path: pl.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """check-pyproject-toml should report declared local path sources."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    _write_pyproject(pyproject, 'demo-lib = { path = ".deps/demo-lib", editable = true }')

    app(["check", "pyproject-toml", "--pyproject", str(pyproject)])

    out = capsys.readouterr().out
    assert f"OK: {pyproject} contains local path sources from [tool.uv.sources]:" in out
    assert "demo-lib" in out


def test_check_pyproject_toml_reports_no_sources(tmp_path: pl.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """check-pyproject-toml should report cleanly when there are no local path sources."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"\nversion = "0.1.0"\n\n[tool.uv.sources]\n', encoding="utf-8")

    app(["check", "pyproject-toml", "--pyproject", str(pyproject)])

    out = capsys.readouterr().out
    assert f"OK: {pyproject} does not contain local path sources from [tool.uv.sources]." in out


def test_check_pyproject_toml_missing_file_exits(tmp_path: pl.Path) -> None:
    """check-pyproject-toml should exit cleanly when pyproject.toml can't be found."""
    from uv_developer.cli import app

    missing = tmp_path / "pyproject.toml"

    with pytest.raises(SystemExit):
        app(["check", "pyproject-toml", "--pyproject", str(missing)])


def test_check_uv_lock_missing_pyproject_exits(tmp_path: pl.Path) -> None:
    """check-uv-lock should exit cleanly when pyproject.toml can't be found."""
    from uv_developer.cli import app

    missing_pyproject = tmp_path / "pyproject.toml"
    lockfile = tmp_path / "uv.lock"
    _write_uv_lock(lockfile, "demo-lib", 'source = { registry = "https://pypi.org/simple" }')

    with pytest.raises(SystemExit):
        app(["check", "uv-lock", "--pyproject", str(missing_pyproject), "--lockfile", str(lockfile)])


def test_check_uv_lock_missing_lockfile_exits(tmp_path: pl.Path) -> None:
    """check-uv-lock should exit cleanly when uv.lock can't be found."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    missing_lockfile = tmp_path / "uv.lock"
    _write_pyproject(pyproject, 'demo-lib = { path = ".deps/demo-lib", editable = true }')

    with pytest.raises(SystemExit):
        app(["check", "uv-lock", "--pyproject", str(pyproject), "--lockfile", str(missing_lockfile)])


def test_wrapper_check_runs_both_checks(tmp_path: pl.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Check should run the pyproject and uv.lock checks together."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    lockfile = tmp_path / "uv.lock"

    _write_pyproject(pyproject, 'demo-lib = { path = ".deps/demo-lib", editable = true }')
    _write_uv_lock(lockfile, "demo-lib", 'source = { registry = "https://pypi.org/simple" }')

    app(["check", "--pyproject", str(pyproject), "--lockfile", str(lockfile)])

    out = capsys.readouterr().out
    assert f"OK: {pyproject} contains local path sources" in out
    assert f"OK: {lockfile} does not contain local path sources" in out


def test_show_reports_current_state(tmp_path: pl.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Show should report the current [tool.uv.sources] entries as a table."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    _write_pyproject(pyproject, 'demo-lib = { path = ".deps/demo-lib", editable = true }')

    app(["show", "--pyproject", str(pyproject)])

    out = capsys.readouterr().out
    assert f"Checking {pyproject}" in out
    assert "demo-lib" in out
    assert "on" in out


def test_show_reports_no_sources(tmp_path: pl.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Show should report cleanly when there are no local path sources."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"\nversion = "0.1.0"\n\n[tool.uv.sources]\n', encoding="utf-8")

    app(["show", "--pyproject", str(pyproject)])

    out = capsys.readouterr().out
    assert f"Checking {pyproject}" in out
    assert "No local path sources found under [tool.uv.sources]." in out


def test_show_renders_pinned_entry(tmp_path: pl.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Show should render a `##`-pinned entry with its "pinned off" status."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    _write_pyproject(pyproject, '## demo-lib = { path = ".deps/demo-lib", editable = true }')

    app(["show", "--pyproject", str(pyproject)])

    out = capsys.readouterr().out
    assert "## demo-lib" in out
    assert "pinned off" in out


def test_show_renders_inactive_entry(tmp_path: pl.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Show should render a commented-out, non-pinned entry with its "off" status."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    _write_pyproject(pyproject, '# demo-lib = { path = ".deps/demo-lib", editable = true }')

    app(["show", "--pyproject", str(pyproject)])

    out = capsys.readouterr().out
    assert "# demo-lib" in out
    assert "off" in out


def test_cli_toggle_with_empty_sources_section_prints_no_table(
    tmp_path: pl.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test toggle on an empty [tool.uv.sources] section reports no changes and no table."""
    from uv_developer.cli import app

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"\nversion = "0.1.0"\n\n[tool.uv.sources]\n', encoding="utf-8")

    app(["toggle", "--pyproject", str(pyproject)])

    out = capsys.readouterr().out
    assert f"No changes in {pyproject}" in out


def test_show_missing_pyproject_exits(tmp_path: pl.Path) -> None:
    """Show should exit cleanly when pyproject.toml can't be found."""
    from uv_developer.cli import app

    missing = tmp_path / "pyproject.toml"

    with pytest.raises(SystemExit):
        app(["show", "--pyproject", str(missing)])
