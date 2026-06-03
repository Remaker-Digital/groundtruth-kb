"""Tests for ``gt bridge revise`` Slice-1 logic (WI-3429).

Covers the spec-derived verification plan from
``bridge/gtkb-bridge-revise-cli-slice-1-001.md``:

- byte-identical carry-forward (GOV-08)
- citation_add / target_paths_add idempotent appends
- version bump = max(on-disk, INDEX) + 1
- carry-forward source is the latest NEW/REVISED, never a verdict
- atomic REVISED INDEX line (GOV-FILE-BRIDGE-AUTHORITY-001)
- Slice-2 fix-classes fail closed
- --dry-run writes nothing
- preflight subprocesses are re-run

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

from groundtruth_kb import bridge_revise as br

_REPO_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------
# Pure transform tests (no helpers / filesystem needed)
# --------------------------------------------------------------------------


def test_content_carryforward_only_is_byte_identical() -> None:
    body = "REVISED\n\n# X\n\nVersion: 001\n\n## Specification Links\n\n- `GOV-08`\n"
    assert br._apply_content_carryforward_only(body) == body


def test_citation_add_appends_and_is_idempotent() -> None:
    body = "NEW\n\n## Specification Links\n\n- `GOV-08` — existing.\n\n## Next Section\n"
    out = br._apply_citation_add(body, add_citations=["GOV-15"])
    assert "GOV-15" in out
    assert out.count("## Specification Links") == 1
    # Adding an already-present id is a no-op.
    assert br._apply_citation_add(out, add_citations=["GOV-08"]) == out


def test_citation_add_requires_args() -> None:
    with pytest.raises(br.BridgeReviseError):
        br._apply_citation_add("body", add_citations=[])


def test_target_paths_add_appends_and_is_idempotent() -> None:
    body = "NEW\n\n## target_paths\n\n- `a/b.py`\n\n## Next Section\n"
    out = br._apply_target_paths_add(body, add_target_paths=["c/d.py"])
    assert "`c/d.py`" in out
    assert br._apply_target_paths_add(out, add_target_paths=["a/b.py"]) == out


def test_target_paths_add_requires_args() -> None:
    with pytest.raises(br.BridgeReviseError):
        br._apply_target_paths_add("body", add_target_paths=[])


def test_bump_version_and_provenance() -> None:
    body = "NEW\n\nVersion: 002\n\n# body\n"
    out = br._bump_version_and_provenance(body, 3, Path("bridge/x-002.md"), "fix-no-go-002-F1")
    assert "Version: 003" in out
    assert "Version: 002" not in out
    assert "revise: fix-no-go-002-F1" in out
    assert "bridge/x-002.md" in out


# --------------------------------------------------------------------------
# Version / carry-forward source resolution
# --------------------------------------------------------------------------


def _make_bridge(tmp_path: Path, slug: str, versions_status: list[tuple[int, str]]) -> Path:
    """Create a tmp bridge/ with INDEX block + version files (newest-first input)."""
    bridge = tmp_path / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    index_lines = ["# Bridge Index", "", f"Document: {slug}"]
    for ver, status in versions_status:
        (bridge / f"{slug}-{ver:03d}.md").write_text(
            f"{status}\n\n# {slug}\n\nVersion: {ver:03d}\n\n## Specification Links\n\n- `GOV-08`\n"
            "\n## target_paths\n\n- `existing/path.py`\n",
            encoding="utf-8",
        )
        index_lines.append(f"{status}: bridge/{slug}-{ver:03d}.md")
    (bridge / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    return bridge


def test_version_bump_is_max_plus_one(tmp_path: Path) -> None:
    slug = "demo-thread"
    bridge = _make_bridge(tmp_path, slug, [(2, "NO-GO"), (1, "NEW")])
    index_text = (bridge / "INDEX.md").read_text(encoding="utf-8")
    assert br.next_version(slug, index_text, bridge) == 3


def test_carryforward_source_skips_verdict(tmp_path: Path) -> None:
    slug = "demo-thread"
    bridge = _make_bridge(tmp_path, slug, [(2, "NO-GO"), (1, "NEW")])
    index_text = (bridge / "INDEX.md").read_text(encoding="utf-8")
    src = br.find_carryforward_source(slug, index_text, bridge)
    # The NEW (-001), not the top-of-stack NO-GO (-002).
    assert src.name == f"{slug}-001.md"


def test_carryforward_source_raises_when_no_prime_version(tmp_path: Path) -> None:
    slug = "verdict-only"
    bridge = _make_bridge(tmp_path, slug, [(2, "NO-GO")])
    index_text = (bridge / "INDEX.md").read_text(encoding="utf-8")
    with pytest.raises(br.BridgeReviseError):
        br.find_carryforward_source(slug, index_text, bridge)


# --------------------------------------------------------------------------
# Orchestration (revise) — fail-closed + dry-run + full write
# --------------------------------------------------------------------------


def test_deferred_fix_classes_rejected() -> None:
    for fc in br.SLICE_2_FIX_CLASSES:
        with pytest.raises(br.BridgeReviseError, match="Slice-2"):
            br.revise("slug", "reason", fc)


def test_unknown_fix_class_rejected() -> None:
    with pytest.raises(br.BridgeReviseError):
        br.revise("slug", "reason", "not_a_real_class")


def test_reason_required() -> None:
    with pytest.raises(br.BridgeReviseError):
        br.revise("slug", "   ", "citation_add")


@pytest.fixture
def stub_helpers(monkeypatch):
    """Monkeypatch _load_helpers with a hermetic stub.

    compose_index_update uses the REAL write_bridge implementation so the
    INDEX-insertion behavior is genuinely exercised; the rest is stubbed.
    """
    helper_dir = _REPO_ROOT / ".claude" / "skills" / "bridge-propose" / "helpers"
    if str(helper_dir) not in sys.path:
        sys.path.insert(0, str(helper_dir))
    scripts_dir = _REPO_ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    import write_bridge as real_wb

    def fake_atomic(index_path, mutate, *, state_dir, **_kw):
        text = Path(index_path).read_text(encoding="utf-8")
        new = mutate(text)
        Path(index_path).write_text(new, encoding="utf-8")
        return new

    fake_wb = types.SimpleNamespace(
        scan_credential_hits=lambda content: [],
        handle_hits_abort_or_redact=lambda body, hits, mode: body,
        compose_index_update=real_wb.compose_index_update,
        resolve_work_intent_session_id=lambda: "test-session",
        _acquire_bridge_work_intent=lambda slug, sid, project_root: object(),
        _release_bridge_work_intent=lambda reg, slug, sid, project_root: None,
    )
    monkeypatch.setattr(br, "_load_helpers", lambda project_root: (fake_wb, fake_atomic))
    monkeypatch.setattr(br, "_rerun_preflights", lambda slug, project_root: {"applicability": "stub", "clause": "stub"})
    return fake_wb


def test_dry_run_writes_nothing(tmp_path: Path, stub_helpers) -> None:
    slug = "demo-thread"
    bridge = _make_bridge(tmp_path, slug, [(1, "NEW")])
    index_before = (bridge / "INDEX.md").read_text(encoding="utf-8")
    res = br.revise(slug, "add GOV-15", "citation_add", add_citations=["GOV-15"], dry_run=True, project_root=tmp_path)
    assert res.dry_run is True
    assert res.written is False
    assert not (bridge / f"{slug}-002.md").exists()
    assert (bridge / "INDEX.md").read_text(encoding="utf-8") == index_before
    assert "GOV-15" in res.new_content
    assert res.index_status_line == f"REVISED: bridge/{slug}-002.md"


def test_full_revise_writes_file_and_index_line(tmp_path: Path, stub_helpers) -> None:
    slug = "demo-thread"
    bridge = _make_bridge(tmp_path, slug, [(1, "NEW")])
    res = br.revise(
        slug,
        "fix-no-go-002-F1",
        "target_paths_add",
        add_target_paths=["c/d.py"],
        project_root=tmp_path,
    )
    assert res.written is True
    new_file = bridge / f"{slug}-002.md"
    assert new_file.exists()
    content = new_file.read_text(encoding="utf-8")
    assert "`c/d.py`" in content
    assert "Version: 002" in content
    assert "revise: fix-no-go-002-F1" in content
    index_text = (bridge / "INDEX.md").read_text(encoding="utf-8")
    assert f"REVISED: bridge/{slug}-002.md" in index_text
    # The REVISED line is prepended above the prior NEW line in the same block.
    assert index_text.index(f"REVISED: bridge/{slug}-002.md") < index_text.index(f"NEW: bridge/{slug}-001.md")


def test_content_carryforward_preserves_body_except_version(tmp_path: Path, stub_helpers) -> None:
    slug = "demo-thread"
    bridge = _make_bridge(tmp_path, slug, [(1, "NEW")])
    source = (bridge / f"{slug}-001.md").read_text(encoding="utf-8")
    res = br.revise(slug, "reclobber", "content_carryforward_only", dry_run=True, project_root=tmp_path)
    # Every source line except the Version line is preserved verbatim.
    src_nonversion = [ln for ln in source.splitlines() if not ln.startswith("Version:")]
    out_nonversion = [ln for ln in res.new_content.splitlines() if not ln.startswith("Version:")]
    for ln in src_nonversion:
        assert ln in out_nonversion


def test_revise_reruns_both_preflights(tmp_path: Path, monkeypatch) -> None:
    """Full write path issues both preflight subprocesses (GO condition 5)."""
    slug = "demo-thread"
    _make_bridge(tmp_path, slug, [(1, "NEW")])

    helper_dir = _REPO_ROOT / ".claude" / "skills" / "bridge-propose" / "helpers"
    for p in (str(_REPO_ROOT), str(_REPO_ROOT / "scripts"), str(helper_dir)):
        if p not in sys.path:
            sys.path.insert(0, p)
    import write_bridge as real_wb

    def fake_atomic(index_path, mutate, *, state_dir, **_kw):
        text = Path(index_path).read_text(encoding="utf-8")
        Path(index_path).write_text(mutate(text), encoding="utf-8")

    fake_wb = types.SimpleNamespace(
        scan_credential_hits=lambda content: [],
        handle_hits_abort_or_redact=lambda body, hits, mode: body,
        compose_index_update=real_wb.compose_index_update,
        resolve_work_intent_session_id=lambda: "test-session",
        _acquire_bridge_work_intent=lambda slug, sid, project_root: object(),
        _release_bridge_work_intent=lambda reg, slug, sid, project_root: None,
    )
    monkeypatch.setattr(br, "_load_helpers", lambda project_root: (fake_wb, fake_atomic))

    invoked: list[str] = []

    def fake_run(args, **_kw):
        invoked.append(" ".join(str(a) for a in args))
        return types.SimpleNamespace(returncode=0, stdout="preflight_passed: true\nBlocking gaps (gate-failing): 0\n")

    monkeypatch.setattr(br.subprocess, "run", fake_run)

    res = br.revise(slug, "fix", "content_carryforward_only", project_root=tmp_path)
    assert res.written is True
    joined = "\n".join(invoked)
    assert "bridge_applicability_preflight.py" in joined
    assert "adr_dcl_clause_preflight.py" in joined
    assert set(res.preflight_summaries) == {"applicability", "clause"}
