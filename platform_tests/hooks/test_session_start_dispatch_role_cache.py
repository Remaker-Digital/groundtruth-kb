"""Regression tests for SessionStart role-scoped startup-disclosure cache writing.

Slice 1 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
(bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-003.md,
Codex GO at -004).

Governing specifications:

- ``ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`` Decision 2: both the ``-pb`` and
  ``-lo`` startup-disclosure caches are generated unconditionally regardless of
  the harness's durable role set, so the UserPromptSubmit init-keyword matcher's
  keyword-keyed cache lookup succeeds for either role.
- ``DCL-SESSION-ROLE-RESOLUTION-001``: durable role is the authority for headless
  dispatch routing only; it is NOT consulted when generating interactive
  startup-disclosure caches. Assertion 8 requires the Claude and Codex
  SessionStart dispatchers to implement the same behavior.
- ``SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`` v2 / ``DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`` v2.

The two SessionStart dispatchers (``.claude/hooks`` and ``.codex/gtkb-hooks``)
carry byte-similar implementations of ``_write_role_scoped_startup_relay_caches``;
every behavioral test is parameterized over both to assert parity.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Both dispatcher source files share the filename ``session_start_dispatch.py``;
# they are loaded under distinct synthetic module names so the two
# implementations can be imported side by side for parity assertions.
_DISPATCHERS = {
    "claude": REPO_ROOT / ".claude" / "hooks" / "session_start_dispatch.py",
    "codex": REPO_ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py",
}

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_dispatcher(harness: str) -> ModuleType:
    path = _DISPATCHERS[harness]
    spec = importlib.util.spec_from_file_location(f"_test_session_start_dispatch_{harness}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# A synthetic owner-visible startup disclosure whose post-marker body resolves
# to the ``pb`` (Prime Builder) primary mode via ``_startup_body_role_mode``.
_PB_PRIMARY_DISCLOSURE = (
    "wrapper preamble\n"
    "## User-Visible Startup Message\n"
    "# GroundTruth-KB Fresh Session Startup\n\n"
    "## Startup Disclosure\n\n"
    "- Role being assumed: Prime Builder\n"
)


def _fake_render(role_profile: str) -> str:
    """Deterministic stand-in for ``_render_role_startup_report``.

    Returns a minimal disclosure body whose role label matches the requested
    profile, so the test is hermetic (no dependency on the full startup
    service render path).
    """
    label = "Loyal Opposition" if role_profile == "loyal-opposition" else "Prime Builder"
    return f"# GroundTruth-KB Fresh Session Startup\n\n## Startup Disclosure\n\n- Role being assumed: {label}\n"


def _isolate(
    module: ModuleType,
    tmp_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    durable_roles: frozenset[str],
    render=_fake_render,
) -> None:
    """Redirect cache writes to ``tmp_dir`` and stub external dependencies.

    ``durable_roles`` seeds what ``_resolve_own_role_set`` would return. The
    Slice 1 change must IGNORE it for cache generation; stubbing it to a
    singleton is how the tests prove the writer no longer consults durable role.
    """
    tmp_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(module, "OUT_DIR", tmp_dir)
    monkeypatch.setattr(module, "_persistent_harness_id", lambda: "TEST-ID")
    monkeypatch.setattr(module, "_resolve_own_role_set", lambda *a, **k: frozenset(durable_roles))
    monkeypatch.setattr(module, "_render_role_startup_report", render)


@pytest.fixture(params=sorted(_DISPATCHERS))
def dispatcher(request: pytest.FixtureRequest) -> ModuleType:
    return _load_dispatcher(request.param)


@pytest.mark.parametrize(
    "durable_roles",
    [frozenset({"pb"}), frozenset({"lo"}), frozenset({"pb", "lo"}), frozenset()],
    ids=["durable-pb-only", "durable-lo-only", "durable-both", "durable-empty"],
)
def test_both_role_caches_written_regardless_of_durable_role(
    dispatcher: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    durable_roles: frozenset[str],
) -> None:
    """Both -pb and -lo caches exist no matter what the durable role set is.

    Core proof of the Slice 1 fix: with ``durable_roles == {pb}`` (harness B's
    singleton), the old loop never produced the ``-lo`` cache. The new loop
    iterates the full mode vocabulary, so both caches are always written.
    """
    _isolate(dispatcher, tmp_path, monkeypatch, durable_roles=durable_roles)

    dispatcher._write_role_scoped_startup_relay_caches(_PB_PRIMARY_DISCLOSURE)

    pb_cache = tmp_path / "last-user-visible-startup-pb.md"
    lo_cache = tmp_path / "last-user-visible-startup-lo.md"
    assert pb_cache.is_file(), "primary (pb) startup-disclosure cache missing"
    assert lo_cache.is_file(), "alternate (lo) startup-disclosure cache missing"
    assert (tmp_path / "last-user-visible-startup-pb.meta.json").is_file()
    assert (tmp_path / "last-user-visible-startup-lo.meta.json").is_file()


def test_metadata_role_mode_fields_match_cache(
    dispatcher: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Each metadata sidecar records the role_mode/role_profile of its cache."""
    _isolate(dispatcher, tmp_path, monkeypatch, durable_roles=frozenset({"pb"}))

    dispatcher._write_role_scoped_startup_relay_caches(_PB_PRIMARY_DISCLOSURE)

    pb_meta = json.loads((tmp_path / "last-user-visible-startup-pb.meta.json").read_text(encoding="utf-8"))
    lo_meta = json.loads((tmp_path / "last-user-visible-startup-lo.meta.json").read_text(encoding="utf-8"))

    assert pb_meta["role_mode"] == "pb"
    assert pb_meta["role_profile"] == "prime-builder"
    assert lo_meta["role_mode"] == "lo"
    assert lo_meta["role_profile"] == "loyal-opposition"

    # Sidecar integrity: byte_length + sha256 describe the on-disk cache body.
    import hashlib

    lo_body = (tmp_path / "last-user-visible-startup-lo.md").read_text(encoding="utf-8")
    lo_bytes = lo_body.encode("utf-8")
    assert lo_meta["byte_length"] == len(lo_bytes)
    assert lo_meta["sha256"] == hashlib.sha256(lo_bytes).hexdigest()


def test_render_failure_skips_alternate_cache_silently(
    dispatcher: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the alternate-role render returns None, the primary cache is still
    written and no exception propagates."""
    _isolate(
        dispatcher,
        tmp_path,
        monkeypatch,
        durable_roles=frozenset({"pb"}),
        render=lambda role_profile: None,
    )

    dispatcher._write_role_scoped_startup_relay_caches(_PB_PRIMARY_DISCLOSURE)

    assert (tmp_path / "last-user-visible-startup-pb.md").is_file()
    assert not (tmp_path / "last-user-visible-startup-lo.md").exists()


def test_preexisting_caches_overwritten(
    dispatcher: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stale caches from a prior session are replaced cleanly."""
    _isolate(dispatcher, tmp_path, monkeypatch, durable_roles=frozenset({"pb"}))
    stale = tmp_path / "last-user-visible-startup-lo.md"
    stale.write_text("STALE CONTENT FROM A PRIOR SESSION", encoding="utf-8")

    dispatcher._write_role_scoped_startup_relay_caches(_PB_PRIMARY_DISCLOSURE)

    refreshed = stale.read_text(encoding="utf-8")
    assert "STALE CONTENT" not in refreshed
    assert "Role being assumed: Loyal Opposition" in refreshed


def test_parity_both_dispatchers_produce_identical_cache_set(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The Claude and Codex dispatchers emit the same cache filename set.

    Asserts DCL-SESSION-ROLE-RESOLUTION-001 assertion 8 (parity between
    harnesses) at the cache-generation layer.
    """
    produced: dict[str, set[str]] = {}
    for harness in sorted(_DISPATCHERS):
        module = _load_dispatcher(harness)
        out_dir = tmp_path / harness
        # Each dispatcher gets its own monkeypatch context so the module-global
        # OUT_DIR patches do not leak across the loop iterations.
        with monkeypatch.context() as mp:
            _isolate(module, out_dir, mp, durable_roles=frozenset({"pb"}))
            module._write_role_scoped_startup_relay_caches(_PB_PRIMARY_DISCLOSURE)
        produced[harness] = {p.name for p in out_dir.glob("last-user-visible-startup-*.md")}

    assert (
        produced["claude"]
        == produced["codex"]
        == {
            "last-user-visible-startup-pb.md",
            "last-user-visible-startup-lo.md",
        }
    )
