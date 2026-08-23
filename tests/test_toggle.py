"""Tests for uv_developer.toggle."""

import pathlib as pl
import subprocess

import pytest

from uv_developer.toggle import parse_source_entries, toggle_sources
from uv_developer.utils.modes import normalize_toggle_mode


def test_normalize_toggle_mode() -> None:
    """Test normalization for action values."""
    assert normalize_toggle_mode(None) is None
    assert normalize_toggle_mode("on") == "on"
    assert normalize_toggle_mode("enable") == "on"
    assert normalize_toggle_mode("1") == "on"
    assert normalize_toggle_mode("off") == "off"
    assert normalize_toggle_mode("disable") == "off"
    assert normalize_toggle_mode("0") == "off"
    assert normalize_toggle_mode("something-else") is None


def test_parse_source_entries_collects_clone_comment() -> None:
    """Test parser keeps package, path and optional clone command."""
    lines = [
        "[tool.uv.sources]",
        "# git clone https://example.invalid/demo.git .deps/demo",
        '# demo = { path = ".deps/demo", editable = true }',
    ]

    entries = parse_source_entries(lines)
    assert len(entries) == 1

    entry = entries[0]
    assert entry.package == "demo"
    assert entry.rel_path == ".deps/demo"
    assert entry.is_active is False
    assert entry.pinned is False
    assert entry.clone_cmd == "git clone https://example.invalid/demo.git .deps/demo"


def test_parse_source_entries_detects_pinned() -> None:
    """Test a double-commented `##` entry is parsed as pinned, not active."""
    lines = [
        "[tool.uv.sources]",
        '## demo = { path = ".deps/demo", editable = true }',
    ]

    entries = parse_source_entries(lines)
    assert len(entries) == 1

    entry = entries[0]
    assert entry.package == "demo"
    assert entry.is_active is False
    assert entry.pinned is True


def test_parse_source_entries_stops_at_next_section() -> None:
    """Test entries after [tool.uv.sources] ends (a new `[...]` header) are ignored."""
    lines = [
        "[tool.uv.sources]",
        'demo = { path = ".deps/demo", editable = true }',
        "[tool.other]",
        'not-a-source = { path = ".deps/not-a-source", editable = true }',
    ]

    entries = parse_source_entries(lines)

    assert [entry.package for entry in entries] == ["demo"]


def test_toggle_sources_reports_no_entries(tmp_path: pl.Path) -> None:
    """Test empty [tool.uv.sources] section is handled gracefully, with no write."""
    pyproject = tmp_path / "pyproject.toml"
    original = "[project]\nname='demo'\nversion='0.1.0'\n"
    pyproject.write_text(original, encoding="utf-8")

    mode, entries, changed = toggle_sources(mode=None, pyproject=pyproject)

    assert mode == "off"
    assert entries == []
    assert changed is False
    assert pyproject.read_text(encoding="utf-8") == original


def test_toggle_sources_warns_when_missing_clone_comment(tmp_path: pl.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test enabling without clone metadata warns but still enables the entry."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name='demo'
version='0.1.0'

[tool.uv.sources]
# demo = { path = ".deps/demo", editable = true }
""",
        encoding="utf-8",
    )

    mode, entries, changed = toggle_sources(mode="on", pyproject=pyproject)

    assert mode == "on"
    assert changed is True
    assert [entry.package for entry in entries] == ["demo"]
    assert entries[0].is_active is True

    content = pyproject.read_text(encoding="utf-8")
    assert 'demo = { path = ".deps/demo", editable = true }' in content
    assert '# demo = { path = ".deps/demo", editable = true }' not in content

    out = capsys.readouterr().out
    assert "WARNING: no '# git clone ...' comment found above 'demo'; leaving as-is." in out


def test_toggle_sources_auto_clones_missing_path(tmp_path: pl.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test enabling runs the recorded git clone command when the path is absent."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name='demo'
version='0.1.0'

[tool.uv.sources]
# git clone https://example.invalid/demo.git .deps/demo
# demo = { path = ".deps/demo", editable = true }
""",
        encoding="utf-8",
    )

    calls: list[tuple[list[str], bool, pl.Path]] = []

    def fake_run(args: list[str], *, check: bool, cwd: pl.Path) -> subprocess.CompletedProcess[str]:
        calls.append((args, check, cwd))
        target_dir = cwd / ".deps/demo"
        target_dir.mkdir(parents=True)
        (target_dir / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
        return subprocess.CompletedProcess(args=args, returncode=0)

    monkeypatch.setattr("uv_developer.utils.git.subprocess.run", fake_run)

    mode, entries, changed = toggle_sources(mode="on", pyproject=pyproject)

    assert mode == "on"
    assert changed is True
    assert [entry.package for entry in entries] == ["demo"]
    assert calls == [(["git", "clone", "https://example.invalid/demo.git", ".deps/demo"], True, tmp_path)]


def test_toggle_sources_skips_pinned_entries(tmp_path: pl.Path) -> None:
    """Test `toggle on` enables regular entries but leaves `##`-pinned ones alone."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name='demo'
version='0.1.0'

[tool.uv.sources]
# demo = { path = ".deps/demo", editable = true }
## rarely-used = { path = ".deps/rarely-used", editable = true }
""",
        encoding="utf-8",
    )
    (tmp_path / ".deps" / "demo").mkdir(parents=True)
    (tmp_path / ".deps" / "demo" / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    mode, entries, changed = toggle_sources(mode="on", pyproject=pyproject)

    assert mode == "on"
    assert changed is True

    by_package = {entry.package: entry for entry in entries}
    assert by_package["demo"].is_active is True
    assert by_package["demo"].pinned is False
    assert by_package["rarely-used"].is_active is False
    assert by_package["rarely-used"].pinned is True

    content = pyproject.read_text(encoding="utf-8")
    assert 'demo = { path = ".deps/demo", editable = true }' in content
    assert '## rarely-used = { path = ".deps/rarely-used", editable = true }' in content
    # a pinned entry's target directory is never touched -- no clone attempted
    assert not (tmp_path / ".deps" / "rarely-used").exists()


def test_toggle_sources_auto_toggle_turns_off_when_active(tmp_path: pl.Path) -> None:
    """Test auto-toggle (mode=None) switches an active entry off."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name='demo'
version='0.1.0'

[tool.uv.sources]
demo = { path = ".deps/demo", editable = true }
""",
        encoding="utf-8",
    )

    mode, entries, changed = toggle_sources(mode=None, pyproject=pyproject)

    assert mode == "off"
    assert changed is True
    assert entries[0].is_active is False


def test_toggle_sources_auto_toggle_turns_on_when_inactive(tmp_path: pl.Path) -> None:
    """Test auto-toggle (mode=None) switches an inactive entry on."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name='demo'
version='0.1.0'

[tool.uv.sources]
# demo = { path = ".deps/demo", editable = true }
""",
        encoding="utf-8",
    )
    (tmp_path / ".deps" / "demo").mkdir(parents=True)
    (tmp_path / ".deps" / "demo" / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    mode, entries, changed = toggle_sources(mode=None, pyproject=pyproject)

    assert mode == "on"
    assert changed is True
    assert entries[0].is_active is True


def test_toggle_sources_disables_active_entries(tmp_path: pl.Path) -> None:
    """Test `toggle off` comments out active entries and leaves already-off ones alone."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name='demo'
version='0.1.0'

[tool.uv.sources]
active-lib = { path = ".deps/active-lib", editable = true }
# inactive-lib = { path = ".deps/inactive-lib", editable = true }
""",
        encoding="utf-8",
    )

    mode, entries, changed = toggle_sources(mode="off", pyproject=pyproject)

    assert mode == "off"
    assert changed is True

    by_package = {entry.package: entry for entry in entries}
    assert by_package["active-lib"].is_active is False
    assert by_package["inactive-lib"].is_active is False

    content = pyproject.read_text(encoding="utf-8")
    assert '# active-lib = { path = ".deps/active-lib", editable = true }' in content
    assert '# inactive-lib = { path = ".deps/inactive-lib", editable = true }' in content


def test_toggle_sources_no_write_when_already_in_target_mode(tmp_path: pl.Path) -> None:
    """Test forcing a mode that's already active makes no changes and doesn't touch the file."""
    pyproject = tmp_path / "pyproject.toml"
    original = """[project]
name='demo'
version='0.1.0'

[tool.uv.sources]
demo = { path = ".deps/demo", editable = true }
"""
    pyproject.write_text(original, encoding="utf-8")
    (tmp_path / ".deps" / "demo").mkdir(parents=True)
    (tmp_path / ".deps" / "demo" / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    mode, entries, changed = toggle_sources(mode="on", pyproject=pyproject)

    assert mode == "on"
    assert changed is False
    assert [entry.package for entry in entries] == ["demo"]
    assert pyproject.read_text(encoding="utf-8") == original

    content = pyproject.read_text(encoding="utf-8")
    assert 'demo = { path = ".deps/demo", editable = true }' in content
    assert '# demo = { path = ".deps/demo", editable = true }' not in content
