"""Tests for uv_developer.check."""

from uv_developer.check import find_matching_local_lock_sources
from uv_developer.models import LocalSourcePackage, SourceEntry


def _source_entry(package: str, rel_path: str) -> SourceEntry:
    return SourceEntry(
        idx=0,
        line=f'{package} = {{ path = "{rel_path}", editable = true }}',
        package=package,
        rel_path=rel_path,
        is_active=True,
        pinned=False,
        clone_cmd=None,
    )


def _lock_source(name: str, source_value: str) -> LocalSourcePackage:
    return LocalSourcePackage(name=name, source_type="editable", source_value=source_value, line_no=1)


def test_find_matching_local_lock_sources_skips_unrelated_entries() -> None:
    """Test a lock entry that matches neither package name nor path is left out."""
    source_entries = [_source_entry("demo-lib", ".deps/demo-lib")]
    lock_sources = [
        _lock_source("demo-lib", ".deps/demo-lib"),
        _lock_source("unrelated", ".deps/unrelated"),
    ]

    matches = find_matching_local_lock_sources(source_entries, lock_sources)

    assert [match.name for match in matches] == ["demo-lib"]


def test_find_matching_local_lock_sources_matches_on_normalized_path() -> None:
    """Test a lock entry matches by path even when the package name differs."""
    source_entries = [_source_entry("demo-lib", "./.deps/demo-lib/")]
    lock_sources = [_lock_source("renamed-demo-lib", ".deps/demo-lib")]

    matches = find_matching_local_lock_sources(source_entries, lock_sources)

    assert [match.name for match in matches] == ["renamed-demo-lib"]
