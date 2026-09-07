"""W0.4: pre-verdict executability check - regression tests.

Covers: the checker's exit-0/5 contract with named gaps, the write_verdict.py
GO-refusal wiring, the writer NO-ACTION validation, and the unfilled-placeholder
gate in bridge-compliance-gate.py.

Authority: bridge/gtkb-w0-executable-go-pre-verdict-validation-001.md (GO at -002).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_CHECKER = _ROOT / "scripts/pre_verdict_executability_check.py"


def _run_checker(slug: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_CHECKER), "--bridge-id", slug, "--json"],
        cwd=_ROOT,
        capture_output=True,
        text=True,
    )


def test_checker_returns_zero_or_five_with_gap_list() -> None:
    # The checker must return 0 (executable) or 5 (gaps) with machine-readable JSON.
    r = _run_checker("gtkb-w0-executable-go-pre-verdict-validation")
    assert r.returncode in (0, 5), f"unexpected exit {r.returncode}: {r.stdout}"
    data = json.loads(r.stdout)
    assert "executable" in data
    assert isinstance(data["gaps"], list)


def test_checker_resolves_nonexistent_thread_to_exit_two() -> None:
    r = subprocess.run(
        [sys.executable, str(_CHECKER), "--bridge-id", "gtkb-no-such-thread-xyz", "--json"],
        cwd=_ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 2


def test_placeholder_gate_new_file_denies() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location("bcg_ut", _ROOT / ".claude/hooks/bridge-compliance-gate.py")
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    sys.modules["bcg_ut"] = m
    spec.loader.exec_module(m)

    # New versioned file with an unfilled placeholder outside fenced code -> block.
    assert (
        m._unfilled_placeholder_violation(
            str(_ROOT / "bridge/gtkb-x-w04-test-001.md"),
            "NEW\n\n## Section\n\nplaceholder_OPEN_ITEM text",
        )
        is True
    )

    # Placeholder inside a fenced code block -> allow (no false block).
    assert (
        m._unfilled_placeholder_violation(
            str(_ROOT / "bridge/gtkb-x-w04-test-002.md"),
            "NEW\n\n```\nplaceholder_OPEN_ITEM\n```\n",
        )
        is False
    )


def test_placeholder_gate_clean_content_allows() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location("bcg_ut2", _ROOT / ".claude/hooks/bridge-compliance-gate.py")
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    sys.modules["bcg_ut2"] = m
    spec.loader.exec_module(m)

    assert (
        m._unfilled_placeholder_violation(
            str(_ROOT / "bridge/gtkb-x-w04-test-003.md"),
            "NEW\n\n## Section\n\nSubstantive content with no placeholder.\n",
        )
        is False
    )


def test_writer_no_action_requires_prior_verdict() -> None:
    import sys as _s

    _s.path.insert(0, str(_ROOT))
    _s.path.insert(0, str(_ROOT / "scripts"))
    # A first-version NO-ACTION write (no prior LO GO/NO-GO) must raise.
    import tempfile

    import gtkb_bridge_writer as w

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        try:
            w.write_bridge_file(
                "gtkb-x-w04-noaction-001",
                1,
                "NO-ACTION\n\n## Section\n",
                root,
                author_metadata={
                    "author_identity": "prime-builder/test",
                    "author_harness_id": "P",
                    "author_session_context_id": "pb-session-1",
                    "author_model": "test",
                    "author_model_version": "test",
                    "author_model_configuration": "test",
                },
            )
            raise AssertionError("expected NO-ACTION write to fail")
        except (w.BridgeTransitionError, w.BridgeComplianceError):
            pass


def test_gate_a_metadata_only_targets_do_not_require_pauth() -> None:
    """WI-6130: Gate A must NOT report pauth_metadata_missing for metadata-only targets.

    The canonical packet-free implementation-start path treats only
    configuration/source/test as protected (PROJECT_AUTHORIZATION_REQUIRED_MUTATION_CLASSES).
    A proposal touching groundtruth.db / .groundtruth/* is metadata-only and
    must not require a Project Authorization row at the pre-verdict gate.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("pvec_ut", _ROOT / "scripts/pre_verdict_executability_check.py")
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    sys.modules["pvec_ut"] = m
    spec.loader.exec_module(m)

    metadata_only_with_pauth = 'NEW\nProject Authorization: PAUTH-PROJECT-X-001\ntarget_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/sample.json"]\n'
    metadata_only_without_pauth = (
        'NEW\ntarget_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/sample.json"]\n'
    )

    assert m._gate_a(metadata_only_with_pauth) == []
    assert m._gate_a(metadata_only_without_pauth) == []


def test_gate_a_protected_targets_without_pauth_still_fail() -> None:
    """WI-6130 control: source/test/config targets without PAUTH must still fail closed."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("pvec_ut2", _ROOT / "scripts/pre_verdict_executability_check.py")
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    sys.modules["pvec_ut2"] = m
    spec.loader.exec_module(m)

    source_no_pauth = 'NEW\ntarget_paths: ["scripts/foo.py", "platform_tests/test_foo.py", "config/bar.toml"]\n'

    gaps = m._gate_a(source_no_pauth)
    assert any(g["code"] == "pauth_metadata_missing" for g in gaps)


def test_gate_d_expired_claim_does_not_block_verification() -> None:
    """WI-6144: an expired/TTL-lapsed claim is treated as absent and does not
    emit claim_held_by_foreign_session, so independent verification can pass."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("pvec_ut3", _ROOT / "scripts/pre_verdict_executability_check.py")
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    sys.modules["pvec_ut3"] = m
    spec.loader.exec_module(m)

    import json as _json

    # Mock the claim-status subprocess to return an expired foreign-session claim.
    expired_claim = {
        "session_id": "G-2026-08-09T21-46-39Z",
        "expired": True,
        "ttl_expires_at": "2026-08-09T23:56:21Z",
    }
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv

        class R:
            returncode = 0
            stdout = _json.dumps(expired_claim)
            stderr = ""

        return R()

    original_run = m.subprocess.run
    m.subprocess.run = fake_run
    try:
        # Verification context (draft_body is None -> drafting=False). Content
        # includes the bounded Requirement Sufficiency phrase so only the claim
        # axis is exercised.
        content = "NEW\n\n## Requirement Sufficiency\n\nExisting requirements are sufficient.\n"
        gaps = m._gate_d("gtkb-wi5812-goose-author-metadata-attestation", content, "G-2026-08-10T07-27-46Z")
    finally:
        m.subprocess.run = original_run

    assert not any(g["code"] == "claim_held_by_foreign_session" for g in gaps), gaps


def test_gate_d_foreign_claim_blocks_only_drafting() -> None:
    """WI-6144: a live foreign-session claim blocks drafting but not verification."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("pvec_ut4", _ROOT / "scripts/pre_verdict_executability_check.py")
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    sys.modules["pvec_ut4"] = m
    spec.loader.exec_module(m)

    import json as _json

    live_claim = {"session_id": "G-OTHER-SESSION", "expired": False}

    def fake_run(argv, **kwargs):
        class R:
            returncode = 0
            stdout = _json.dumps(live_claim)
            stderr = ""

        return R()

    original_run = m.subprocess.run
    m.subprocess.run = fake_run
    try:
        content = "NEW\n\n## Requirement Sufficiency\n\nExisting requirements are sufficient.\n"
        # Drafting context blocks a live foreign claim.
        drafting_gaps = m._gate_d("gtkb-x", content, "G-MINE", drafting=True)
        # Verification context does not.
        verify_gaps = m._gate_d("gtkb-x", content, "G-MINE", drafting=False)
    finally:
        m.subprocess.run = original_run

    assert any(g["code"] == "claim_held_by_foreign_session" for g in drafting_gaps), drafting_gaps
    assert not any(g["code"] == "claim_held_by_foreign_session" for g in verify_gaps), verify_gaps
