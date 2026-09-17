"""WI-7318 absence assertions: the startup disclosure is never cached.

Compact Operating Guidance section 9 requires startup disclosures to be
generated in real time and forbids caching them. Two caching tiers previously
violated that: a per-harness disclosure cache written from ``scripts/`` into
generated projection trees (also a section 8 violation), and a TTL-validated
session-packet cache under a forbidden state directory.

Grep-count-is-zero is the only check that cannot pass while the defect
persists, so these assertions are deliberately census-shaped rather than
behavioural: a future change that reintroduces either cache fails here even if
it keeps every other test green.
"""

from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# The artifact family the disclosure cache used. Split so this file does not
# itself match the census it runs.
_CACHE_STEM = "last-user-visible" + "-startup"

# The producer surfaces this change was authorized to modify. Scoped to the
# declared target paths on purpose: the GO binds implementation strictly to
# them, so this census asserts what the change controls. Two files outside the
# bound still name the artifact family -- ``hygiene/auto_resolve.py`` and
# ``project/artifact_membership_reconciliation.py`` -- but both only CLASSIFY
# it as disposable runtime output. Neither reads nor writes a cache, and both
# are needed to reclaim the stale artifacts, so they are correct as they stand.
_PRODUCER_PATHS = ("scripts/workstream_focus.py",)


def test_no_producer_names_the_disclosure_cache() -> None:
    """No producer surface reads, writes or names the disclosure cache."""
    offenders: list[str] = []
    for rel in _PRODUCER_PATHS:
        path = PROJECT_ROOT / rel
        if not path.is_file():
            continue
        if _CACHE_STEM in path.read_text(encoding="utf-8"):
            offenders.append(rel)
    assert offenders == [], f"producers still reference the disclosure cache: {offenders}"


def test_the_deleted_cache_bootstrapper_stays_deleted() -> None:
    """The projection-to-projection cache seeder must not return.

    It copied a cached disclosure out of one harness projection into another,
    wrote a forbidden state path, hardcoded vendor names, and asserted role
    authority from cache metadata.
    """
    assert not (PROJECT_ROOT / "scripts" / "_bootstrap_cursor_startup_cache.py").exists()


def test_no_producer_writes_the_packet_cache() -> None:
    """The session-packet cache under the forbidden state directory is gone."""
    offenders: list[str] = []
    for rel in _PRODUCER_PATHS:
        path = PROJECT_ROOT / rel
        if not path.is_file():
            continue
        if "session-envelope/packet-cache" in path.read_text(encoding="utf-8"):
            offenders.append(rel)
    assert offenders == [], f"producers still reference the packet cache: {offenders}"


def test_relay_renders_rather_than_reading_a_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """The relay obtains its disclosure from the renderer, not from disk."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("wf_under_test", PROJECT_ROOT / "scripts" / "workstream_focus.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert not hasattr(module, "_startup_relay_pointer"), "cache-reading relay entry point survives"
    assert hasattr(module, "_startup_disclosure"), "real-time disclosure entry point missing"

    calls: list[str | None] = []
    body = "# GroundTruth-KB Fresh Session Startup\n\n## Startup Disclosure\n\nbody"

    def _render(root, *, role_mode=None):
        calls.append(role_mode)
        return body

    monkeypatch.setattr(module, "_render_startup_disclosure_bounded", _render)
    first = module._startup_disclosure(PROJECT_ROOT, role_mode="pb")
    second = module._startup_disclosure(PROJECT_ROOT, role_mode="pb")

    assert first is not None and second is not None
    assert first["body"] == body
    assert calls == ["pb", "pb"], "each relay must render; a second call must not be served from memory"
