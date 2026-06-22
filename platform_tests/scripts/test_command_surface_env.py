"""Tests for the WI-4395 canonical in-root command-surface env helper.

Per ``bridge/gtkb-wi4395-uv-cache-command-surface-002.md`` (REVISED) and
``-003`` (Codex GO). Covers the proposal's Verification Plan: in-root pinning of
``UV_CACHE_DIR`` / ``TMP`` / ``TEMP``, reuse of the existing ``uv-cache`` GC
directory-name token (with a drift guard against the live retention config),
path-purity of the resolver, the denied/broken-default-cache regression, the
idempotent ``ensure`` behaviour, base-env merging, and the self-documenting CLI.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import command_surface_env as helper  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RETENTION_CONFIG = _REPO_ROOT / "config" / "governance" / "runtime-evidence-retention.toml"


def test_resolve_pins_uv_cache_in_root(tmp_path: Path) -> None:
    """UV_CACHE_DIR is pinned to <root>/.gtkb-state/uv-cache and stays in-root."""
    env = helper.resolve_command_surface_env(tmp_path)
    expected = tmp_path / ".gtkb-state" / "uv-cache"
    assert env["UV_CACHE_DIR"] == str(expected)
    assert Path(env["UV_CACHE_DIR"]).is_relative_to(tmp_path)
    # The canonical cache is the in-root location relative to the project root,
    # not the uv default user-profile cache (proven by the exact relative path so
    # the assertion is independent of where the test's tmp_path itself lives).
    assert Path(env["UV_CACHE_DIR"]).relative_to(tmp_path) == Path(".gtkb-state") / "uv-cache"


def test_resolve_pins_tmp_temp_in_root(tmp_path: Path) -> None:
    """TMP and TEMP both pin to the in-root command-surface temp directory."""
    env = helper.resolve_command_surface_env(tmp_path)
    expected = tmp_path / ".gtkb-state" / "uv-cache-tmp"
    assert env["TMP"] == str(expected)
    assert env["TEMP"] == str(expected)
    assert Path(env["TMP"]).is_relative_to(tmp_path)


def test_tmp_temp_share_one_dir(tmp_path: Path) -> None:
    """command_surface_dirs de-duplicates: uv-cache + one shared temp dir."""
    dirs = helper.command_surface_dirs(tmp_path)
    assert len(dirs) == 2
    names = {d.name for d in dirs}
    assert names == {"uv-cache", "uv-cache-tmp"}


def test_all_dirs_use_gc_recognized_tokens(tmp_path: Path) -> None:
    """Every pinned dir name contains a GC token (dedup vs HYG-054, no new name)."""
    for directory in helper.command_surface_dirs(tmp_path):
        assert helper.gc_recognized_token(directory.name) is not None, directory


def test_gc_tokens_match_live_retention_config() -> None:
    """Drift guard: the helper's GC token tuple equals the live retention config.

    If runtime-evidence-retention.toml ever drops the uv-cache token, the
    canonical cache would silently fall out of GC coverage -- this test surfaces
    that coupling instead.
    """
    data = tomllib.loads(_RETENTION_CONFIG.read_text(encoding="utf-8"))
    config_tokens = data["gtkb_state_gc"]["directory_name_tokens"]
    assert set(helper.GC_RECOGNIZED_TOKENS) == set(config_tokens)
    # The canonical uv cache token in particular must remain covered.
    assert "uv-cache" in config_tokens


def test_resolve_is_path_pure_no_io(tmp_path: Path) -> None:
    """resolve_* and command_surface_dirs touch no filesystem (path-pure)."""
    helper.resolve_command_surface_env(tmp_path)
    helper.command_surface_dirs(tmp_path)
    helper.gc_recognized_token("uv-cache")
    assert not (tmp_path / ".gtkb-state").exists()


def test_ensure_creates_dirs_idempotent(tmp_path: Path) -> None:
    """ensure creates the command-surface dirs; a second call is a no-op."""
    helper.ensure_command_surface_env(tmp_path, base_env={})
    dirs = helper.command_surface_dirs(tmp_path)
    for directory in dirs:
        assert directory.is_dir()
        (directory / "sentinel.txt").write_text("ok", encoding="utf-8")
    # Idempotent: a second call does not raise and preserves the dirs.
    helper.ensure_command_surface_env(tmp_path, base_env={})
    for directory in dirs:
        assert directory.is_dir()


def test_ensure_overrides_denied_default_cache(tmp_path: Path) -> None:
    """A denied/broken default UV_CACHE_DIR is replaced by an in-root writable one.

    This is the WI-4395 core regression: a base environment whose UV_CACHE_DIR
    points at an un-creatable path (under a regular file) must not be propagated;
    ensure_command_surface_env yields the in-root cache and that cache is
    writable.
    """
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")
    denied_cache = blocker / "uv" / "cache"  # cannot be created: 'blocker' is a file
    base_env = {"UV_CACHE_DIR": str(denied_cache), "TMP": str(denied_cache), "TEMP": str(denied_cache)}

    merged = helper.ensure_command_surface_env(tmp_path, base_env=base_env)

    in_root_cache = tmp_path / ".gtkb-state" / "uv-cache"
    assert merged["UV_CACHE_DIR"] == str(in_root_cache)
    assert merged["UV_CACHE_DIR"] != str(denied_cache)
    assert in_root_cache.is_dir()
    sentinel = in_root_cache / "probe.bin"
    sentinel.write_bytes(b"writable")
    assert sentinel.read_bytes() == b"writable"


def test_ensure_merges_base_env(tmp_path: Path) -> None:
    """Unrelated base_env keys survive; only the pinned keys are overridden."""
    base_env = {"FOO": "bar", "UV_CACHE_DIR": "stale-value"}
    merged = helper.ensure_command_surface_env(tmp_path, base_env=base_env)
    assert merged["FOO"] == "bar"
    assert merged["UV_CACHE_DIR"] == str(tmp_path / ".gtkb-state" / "uv-cache")


def test_ensure_does_not_mutate_process_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """ensure never mutates the live process environment."""
    monkeypatch.delenv("UV_CACHE_DIR", raising=False)
    helper.ensure_command_surface_env(tmp_path, base_env={})
    import os

    assert "UV_CACHE_DIR" not in os.environ


def test_main_prints_env(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI prints KEY=VALUE lines and returns 0 (read-only by default)."""
    rc = helper.main(["--project-root", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "UV_CACHE_DIR=" in out
    assert "TMP=" in out
    assert "TEMP=" in out
    # read-only default must not create the dirs
    assert not (tmp_path / ".gtkb-state").exists()


def test_main_ensure_creates_dirs(tmp_path: Path) -> None:
    """CLI --ensure creates the command-surface directories."""
    rc = helper.main(["--project-root", str(tmp_path), "--ensure"])
    assert rc == 0
    for directory in helper.command_surface_dirs(tmp_path):
        assert directory.is_dir()


def test_main_json_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI --format json emits valid JSON with the three pinned keys."""
    rc = helper.main(["--project-root", str(tmp_path), "--format", "json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert set(payload) == {"UV_CACHE_DIR", "TMP", "TEMP"}
    assert payload["UV_CACHE_DIR"] == str(tmp_path / ".gtkb-state" / "uv-cache")
