"""WI-5694 cycle-3 closure: finalization-layer expiry-alignment regression lock.

Per ``bridge/gtkb-wi5694-finalization-expiry-alignment-001.md`` (GO at ``-002``).

Locks the four owner-mandated regression cases from ``DELIB-202667723``
("terminal-evidence-sufficient": evidence at the time of the act, not ambient
state now) at the *finalization* layer -- the protected-commit authorization
stack that produced the wi5759/wi5758 finalization wedge -- plus a cross-layer
parity drift-lock (T5) binding the checker's inlined route-3 live-at-
implementation logic to the cycle-1 ``assess_packet_terminal_evidence`` API.

Both production surfaces are imported strictly read-only; this module modifies
no source. Every fixture is hermetic: isolated ``tmp_path`` project roots with
fixture git repositories, fixture bridge chains, and fixture schema-v3
finalized packets. The live repository store, live MemBase, live bridge chain,
and live work-intent registry are never touched, so concurrent workers mutating
the real tree cannot perturb these assertions.

Deliberately self-contained: no helper is imported from the sibling suites
(``test_check_protected_commit_authorization.py``,
``test_implementation_authorization_terminal_evidence.py``) because those files
are owned by other non-terminal bridge threads.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from scripts import implementation_authorization as impl_auth

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = REPO_ROOT / "scripts" / "check_protected_commit_authorization.py"

# Distinct sys.modules key so this module never clobbers the registration made
# by the checker's own suite when both run in one pytest session.
CHECKER_MODULE_NAME = "wi5694_closure_check_protected_commit_authorization"

FIXTURE_PROTECTED_PATHS = [
    "scripts/wi5694_closure_fixture_surface.py",
    "platform_tests/scripts/test_wi5694_closure_fixture_surface.py",
]


@pytest.fixture
def checker_module():
    """Load check_protected_commit_authorization.py without executing main()."""
    spec = importlib.util.spec_from_file_location(CHECKER_MODULE_NAME, CHECKER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[CHECKER_MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _iso(moment: datetime) -> str:
    return moment.isoformat().replace("+00:00", "Z")


def _author_block(role: str, session_id: str) -> str:
    return f"""author_identity: {role}/fixture
author_harness_id: A
author_session_context_id: {session_id}
author_model: fixture-model
author_model_version: fixture-model
author_model_configuration: wi5694-closure-fixture
"""


def _write_chain(
    root: Path,
    bridge_id: str,
    protected_paths: list[str],
    *,
    report_session: str = "pb-report-session",
    reviewer_session: str = "lo-verdict-session",
    through_verdict: bool = True,
) -> tuple[list[str], str, str]:
    """Write a proposal/GO/report/VERIFIED bridge chain; return the staged set.

    ``through_verdict=False`` stops at the GO so the chain's latest status is
    ``GO`` (``latest_is_go``) -- the state in which an implementation packet is
    still on the active-authority path.
    """
    (root / "bridge").mkdir(parents=True, exist_ok=True)
    proposal = f"bridge/{bridge_id}-001.md"
    go = f"bridge/{bridge_id}-002.md"
    report = f"bridge/{bridge_id}-003.md"
    verdict = f"bridge/{bridge_id}-004.md"
    selected_paths = [*protected_paths, report, verdict]

    (root / proposal).write_text(
        f"""NEW
{_author_block("prime-builder", "pb-proposal-session")}
# Proposal

Document: {bridge_id}
Version: 001

target_paths: {json.dumps(protected_paths)}
""",
        encoding="utf-8",
    )
    (root / go).write_text(
        f"""GO
{_author_block("loyal-opposition", "lo-go-session")}
# Verdict

Document: {bridge_id}
Version: 002
Responds to: {proposal}
""",
        encoding="utf-8",
    )
    if not through_verdict:
        return [*protected_paths], report, verdict
    (root / report).write_text(
        f"""NEW
{_author_block("prime-builder", report_session)}
# Implementation Report

bridge_kind: implementation_report
Document: {bridge_id}
Version: 003
Responds to: {go}
""",
        encoding="utf-8",
    )
    manifest = "\n".join(f"- `{path}`" for path in selected_paths)
    (root / verdict).write_text(
        f"""VERIFIED
{_author_block("loyal-opposition", reviewer_session)}
# Verification

bridge_kind: lo_verdict
Document: {bridge_id}
Version: 004
Responds to: {report}

## Commit Finalization Evidence

- Finalization helper: `fixture`
- Intended commit subject: `test: fixture`
- Same-transaction path set:
{manifest}
- Final commit SHA is emitted after commit creation.
""",
        encoding="utf-8",
    )
    return selected_paths, report, verdict


def _build_packet(
    bridge_id: str,
    protected_paths: list[str],
    *,
    expires_at: str,
    finalized_at: str,
    start_session: str = "pb-start-session",
    claim_session: str | None = None,
) -> dict[str, Any]:
    """Build a schema-v3 finalized implementation-start packet fixture.

    ``claim_session`` defaults to ``start_session``; passing a different value
    produces the embedded-claim-inconsistency shape used by T3(b).
    """
    project_authorization = {
        "id": "PAUTH-WI5694-FIXTURE",
        "project_id": "PROJECT-WI5694-FIXTURE",
        "work_item_id": "WI-FIXTURE",
        "proposal_project_id": "PROJECT-WI5694-FIXTURE",
        "version": 1,
        "normalized_envelope_hash": "fixture-envelope",
        "target_classifications": [{"path": path, "mutation_class": "source"} for path in protected_paths],
        "evaluator_id": "fixture-evaluator",
        "evaluator_version": "1",
        "evaluator_sha256": "fixture-evaluator-sha",
        "taxonomy_version": "1",
        "taxonomy_sha256": "fixture-taxonomy-sha",
    }
    packet: dict[str, Any] = {
        "bridge_id": bridge_id,
        "created_at": "2026-07-19T00:00:00Z",
        "expires_at": expires_at,
        "go_file": f"bridge/{bridge_id}-002.md",
        "latest_status": "GO",
        "project_authorization": project_authorization,
        "proposal_file": f"bridge/{bridge_id}-001.md",
        "schema_version": 2,
        "spec_links": ["GOV-FILE-BRIDGE-AUTHORITY-001"],
        "target_path_globs": list(protected_paths),
    }
    pre_start_hash = impl_auth.packet_hash(packet)
    packet["schema_version"] = 3
    packet["implementation_start"] = {
        "schema_version": 1,
        "bridge_id": bridge_id,
        "finalized_at": finalized_at,
        "session_id": start_session,
        "pre_start_packet_hash": pre_start_hash,
        "target_path_globs": list(protected_paths),
        "work_intent_claim": {
            "thread_slug": bridge_id,
            "session_id": claim_session if claim_session is not None else start_session,
            "claim_kind": "go_implementation",
            "acting_role": "prime-builder",
            "project_id": "PROJECT-WI5694-FIXTURE",
        },
        "worker_role_provenance": {
            "schema_version": 1,
            "session_id": start_session,
            "role": "prime-builder",
            "harness_id": "A",
        },
        "project_authorization_decision": {"allowed": True},
    }
    packet["packet_hash"] = impl_auth.packet_hash(packet)
    return packet


def _write_packet(root: Path, packet: dict[str, Any]) -> Path:
    by_bridge = root / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
    by_bridge.mkdir(parents=True, exist_ok=True)
    path = by_bridge / f"{packet['bridge_id']}.json"
    path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    return path


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True)


def _stage_transaction(root: Path, selected_paths: list[str], report: str, verdict: str) -> None:
    """Commit the proposal/GO predecessors, then stage the finalize transaction."""
    hooks = root / "empty-hooks"
    hooks.mkdir(exist_ok=True)
    _git(root, "init", "-q")
    proposal = report.replace("-003.md", "-001.md")
    go = report.replace("-003.md", "-002.md")
    _git(root, "add", "--", proposal, go)
    _git(
        root,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "-c",
        f"core.hooksPath={hooks}",
        "commit",
        "-qm",
        "fixture predecessors",
    )
    for rel_path in selected_paths:
        if rel_path in {report, verdict}:
            continue
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# staged implementation\n", encoding="utf-8")
    _git(root, "add", "--", *selected_paths)


def _neutralize_unrelated_gates(module, monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub the evidence gates that are orthogonal to packet-expiry semantics.

    These surfaces (compliance audit, verdict anchor preflight, review
    independence, live-GO packet enumeration, PAUTH operation-time validation)
    have their own dedicated coverage. Stubbing them keeps T1/T2 focused on the
    single variable under test: the packet's expiry-vs-implementation-time
    relationship.
    """
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])
    monkeypatch.setattr(module, "run_bridge_compliance_audit", lambda **kwargs: {"decision": "pass"})
    monkeypatch.setattr(module, "validate_verdict_evidence_anchors", lambda content, project_root: [])
    monkeypatch.setattr(module, "verdict_self_review_reason", lambda content, bridge_id, project_root, **kwargs: None)
    monkeypatch.setattr(
        module,
        "validate_packet_project_authorization_operation",
        lambda root, packet, *, requested_operations, target_paths: {
            "operation_time_decisions": [{"allowed": True}],
            "requested_operations": requested_operations,
            "target_paths": target_paths,
        },
    )


def _approved_chain(module, bridge_id: str, protected_paths: list[str]):
    return module._ApprovedChain(
        proposal_path=f"bridge/{bridge_id}-001.md",
        go_path=f"bridge/{bridge_id}-002.md",
        report_path=f"bridge/{bridge_id}-003.md",
        target_paths=tuple(protected_paths),
    )


def _all_evidence_errors(result: dict[str, Any]) -> str:
    """Flatten every finding reason and evidence error into one search string."""
    parts: list[str] = []
    for finding in result.get("findings", []):
        parts.append(str(finding.get("reason", "")))
        parts.extend(str(error) for error in finding.get("evidence_errors", []))
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# T1 - DELIB-202667723 case 1: expired-but-live-at-implementation ACCEPT
# ---------------------------------------------------------------------------


def test_finalization_accepts_expired_but_live_packet_end_to_end(
    checker_module,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The wi5759 wedge shape clears the full commit-authorization stack.

    A packet that was live when implementation started but expired before the
    finalize-verified transaction reached the pre-commit gate must NOT be
    denied on ambient wall-clock expiry, and the cycle-1 evidence API must
    classify the same packet as valid historical evidence.
    """
    bridge_id = "gtkb-wi5694-closure-t1"
    selected_paths, report, verdict = _write_chain(tmp_path, bridge_id, FIXTURE_PROTECTED_PATHS)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    _neutralize_unrelated_gates(checker_module, monkeypatch)

    now = datetime.now(UTC)
    _write_packet(
        tmp_path,
        _build_packet(
            bridge_id,
            FIXTURE_PROTECTED_PATHS,
            expires_at=_iso(now - timedelta(hours=2)),
            finalized_at=_iso(now - timedelta(hours=3)),
        ),
    )

    result = checker_module.evaluate(tmp_path)

    assert result["status"] == "pass", _all_evidence_errors(result)
    assert {item["path"] for item in result["cleared"]} == set(FIXTURE_PROTECTED_PATHS)
    assert {item["evidence"] for item in result["cleared"]} == {"transaction_local_verified_manifest"}
    assert {item["source"] for item in result["cleared"]} == {bridge_id}

    evidence = impl_auth.assess_packet_terminal_evidence(tmp_path, bridge_id)

    assert evidence["evidence_valid"] is True, evidence["reasons"]
    assert evidence["expired"] is True
    assert evidence["live_at_implementation"] is True
    assert evidence["contested"] is False


# ---------------------------------------------------------------------------
# T2 - DELIB-202667723 case 2: expired-before-implementation REJECT
# ---------------------------------------------------------------------------


def test_finalization_rejects_never_live_packet_both_layers(
    checker_module,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A packet that expired *before* implementation started stays invalid.

    Terminal-evidence-sufficient relaxes ambient expiry only; it must not
    resurrect authority that never existed at the time of the act.
    """
    bridge_id = "gtkb-wi5694-closure-t2"
    selected_paths, report, verdict = _write_chain(tmp_path, bridge_id, FIXTURE_PROTECTED_PATHS)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    _neutralize_unrelated_gates(checker_module, monkeypatch)

    now = datetime.now(UTC)
    _write_packet(
        tmp_path,
        _build_packet(
            bridge_id,
            FIXTURE_PROTECTED_PATHS,
            expires_at=_iso(now - timedelta(hours=3)),
            finalized_at=_iso(now - timedelta(hours=1)),
        ),
    )

    result = checker_module.evaluate(tmp_path)

    assert result["status"] == "fail"
    assert "was not live at implementation" in _all_evidence_errors(result)
    # The staged implementation paths are denied. The staged VERIFIED verdict
    # file is denied too (its own transaction-local clearance collapsed with
    # the packet), so this is a superset check rather than an equality check.
    assert set(FIXTURE_PROTECTED_PATHS) <= {finding["path"] for finding in result["findings"]}
    assert result["cleared"] == []

    evidence = impl_auth.assess_packet_terminal_evidence(tmp_path, bridge_id)

    assert evidence["evidence_valid"] is False
    assert evidence["live_at_implementation"] is False
    assert any("not live at implementation" in reason.lower() for reason in evidence["reasons"])


# ---------------------------------------------------------------------------
# T3 - DELIB-202667723 case 3: contested REJECT
# ---------------------------------------------------------------------------


def test_contested_thread_fails_evidence_and_embedded_claim_floor(
    checker_module,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Contest rejection at the evidence API, plus the checker's claim floor.

    (a) The cycle-1 API rejects a packet whose thread is held by a different
    live session.

    (b) The checker enforces the packet's *embedded* claim/provenance
    consistency: a work-intent claim naming a session other than the
    implementation-start session is denied.

    RF-1 (declared open in the proposal): the checker does NOT consult the
    live work-intent registry for an active competing claim at finalization
    time. That gap is deliberately NOT asserted here as expected behavior --
    asserting it would ossify the gap. It is routed as a follow-on.
    """
    bridge_id = "gtkb-wi5694-closure-t3"
    _write_chain(tmp_path, bridge_id, FIXTURE_PROTECTED_PATHS)

    now = datetime.now(UTC)
    _write_packet(
        tmp_path,
        _build_packet(
            bridge_id,
            FIXTURE_PROTECTED_PATHS,
            expires_at=_iso(now + timedelta(hours=4)),
            finalized_at=_iso(now - timedelta(hours=1)),
            start_session="packet-owner-session",
        ),
    )

    # (a) API layer: an active competing claim from a different session.
    monkeypatch.setattr(
        impl_auth.bridge_work_intent_registry,
        "current_holder",
        lambda bridge_id, **kwargs: {"session_id": "competing-session", "bridge_id": bridge_id},
    )

    contested = impl_auth.assess_packet_terminal_evidence(tmp_path, bridge_id)

    assert contested["contested"] is True
    assert contested["evidence_valid"] is False
    assert any("contested" in reason.lower() for reason in contested["reasons"])

    # Same fixture, no competing holder -> uncontested and evidence-valid.
    monkeypatch.setattr(
        impl_auth.bridge_work_intent_registry,
        "current_holder",
        lambda bridge_id, **kwargs: None,
    )

    uncontested = impl_auth.assess_packet_terminal_evidence(tmp_path, bridge_id)

    assert uncontested["contested"] is False
    assert uncontested["evidence_valid"] is True, uncontested["reasons"]

    # (b) Checker floor: embedded claim session must equal the start session.
    _neutralize_unrelated_gates(checker_module, monkeypatch)
    _write_packet(
        tmp_path,
        _build_packet(
            bridge_id,
            FIXTURE_PROTECTED_PATHS,
            expires_at=_iso(now + timedelta(hours=4)),
            finalized_at=_iso(now - timedelta(hours=1)),
            start_session="packet-owner-session",
            claim_session="a-different-session",
        ),
    )
    chain = _approved_chain(checker_module, bridge_id, FIXTURE_PROTECTED_PATHS)

    packet, errors = checker_module._load_finalized_packet(tmp_path, bridge_id, chain, list(FIXTURE_PROTECTED_PATHS))

    assert packet is None
    assert any("claim session differs from start session" in error for error in errors), errors


# ---------------------------------------------------------------------------
# T4 - DELIB-202667723 case 4: live-packet behavior unchanged
# ---------------------------------------------------------------------------


def test_active_authority_expiry_hard_reject_unchanged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The WI-4532 active-authority expiry bound is deliberately NOT relaxed.

    Terminal-evidence semantics govern historical evidence only. The active
    mutation-gating path (``load_named_packet``) must still hard-reject an
    expired packet, and must still accept an unexpired one.
    """
    monkeypatch.setattr(
        impl_auth.bridge_work_intent_registry,
        "current_claimed_bridge_id",
        lambda session_id, project_root=None: None,
    )
    # PAUTH operation-time evaluation needs a seeded MemBase; it has its own
    # dedicated coverage and is orthogonal to the expiry invariant under test.
    monkeypatch.setattr(
        impl_auth,
        "validate_packet_project_authorization_operation",
        lambda root, packet, *, requested_operations, target_paths: {
            "operation_time_decisions": [{"allowed": True}],
        },
    )
    now = datetime.now(UTC)

    # Both fixtures stop at GO so the chain state is identical and expiry is
    # the single differing variable.
    expired_bridge = "gtkb-wi5694-closure-t4-expired"
    _write_chain(tmp_path, expired_bridge, FIXTURE_PROTECTED_PATHS, through_verdict=False)
    _write_packet(
        tmp_path,
        _build_packet(
            expired_bridge,
            FIXTURE_PROTECTED_PATHS,
            expires_at=_iso(now - timedelta(hours=2)),
            finalized_at=_iso(now - timedelta(hours=3)),
        ),
    )

    with pytest.raises(impl_auth.AuthorizationError, match="expired"):
        impl_auth.load_named_packet(tmp_path, expired_bridge)

    live_bridge = "gtkb-wi5694-closure-t4-live"
    _write_chain(tmp_path, live_bridge, FIXTURE_PROTECTED_PATHS, through_verdict=False)
    _write_packet(
        tmp_path,
        _build_packet(
            live_bridge,
            FIXTURE_PROTECTED_PATHS,
            expires_at=_iso(now + timedelta(hours=4)),
            finalized_at=_iso(now - timedelta(hours=1)),
        ),
    )

    loaded = impl_auth.load_named_packet(tmp_path, live_bridge)

    assert loaded["bridge_id"] == live_bridge


# ---------------------------------------------------------------------------
# T5 - cross-layer parity drift-lock (RF-2 mitigation)
# ---------------------------------------------------------------------------

# (expires stamp, finalized stamp, accepted, route-3 deny fragment for deny shapes).
# The deny fragment pins the denial to route 3's expiry/live-window clause, so a
# shape cannot register as "agreeing" because of an unrelated fixture defect.
PARITY_SHAPES = [
    pytest.param(timedelta(hours=-2), timedelta(hours=-3), True, None, id="expired_but_live"),
    pytest.param(
        timedelta(hours=-3),
        timedelta(hours=-1),
        False,
        "was not live at implementation",
        id="never_live",
    ),
    pytest.param(
        timedelta(hours=4),
        "not-a-timestamp",
        False,
        "finalized_at is unparseable",
        id="unparseable_finalized_at",
    ),
    pytest.param(
        "not-a-timestamp",
        timedelta(hours=-1),
        False,
        "invalid expiry",
        id="unparseable_expires_at",
    ),
    pytest.param(timedelta(hours=4), timedelta(hours=-1), True, None, id="live_unexpired"),
]


def _resolve_stamp(value: timedelta | str, now: datetime) -> str:
    return _iso(now + value) if isinstance(value, timedelta) else value


@pytest.mark.parametrize(("expires", "finalized", "accepted", "deny_fragment"), PARITY_SHAPES)
def test_route3_and_evidence_api_semantics_agree(
    checker_module,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    expires: timedelta | str,
    finalized: timedelta | str,
    accepted: bool,
    deny_fragment: str | None,
) -> None:
    """The checker's inlined route-3 logic and the cycle-1 API must agree.

    ``scripts/check_protected_commit_authorization.py`` implements the
    live-at-implementation (E2) classification inline rather than consuming
    ``assess_packet_terminal_evidence`` -- RF-2, a structural duplication forced
    by bridge-thread file ownership. Neither sibling suite crosses the layer
    boundary, so this parametrized parity check is the only guard against the
    two independent implementations of the same owner-decided semantics
    drifting apart silently.

    Parity is asserted at the classification level (accept vs deny per shape),
    not message-for-message, so either layer stays free to be refactored --
    including the eventual RF-2 consolidation.
    """
    bridge_id = "gtkb-wi5694-closure-t5"
    _write_chain(tmp_path, bridge_id, FIXTURE_PROTECTED_PATHS)
    _neutralize_unrelated_gates(checker_module, monkeypatch)
    monkeypatch.setattr(
        impl_auth.bridge_work_intent_registry,
        "current_holder",
        lambda bridge_id, **kwargs: None,
    )

    now = datetime.now(UTC)
    _write_packet(
        tmp_path,
        _build_packet(
            bridge_id,
            FIXTURE_PROTECTED_PATHS,
            expires_at=_resolve_stamp(expires, now),
            finalized_at=_resolve_stamp(finalized, now),
        ),
    )
    chain = _approved_chain(checker_module, bridge_id, FIXTURE_PROTECTED_PATHS)

    packet, checker_errors = checker_module._load_finalized_packet(
        tmp_path, bridge_id, chain, list(FIXTURE_PROTECTED_PATHS)
    )
    checker_accepted = packet is not None and not checker_errors

    evidence = impl_auth.assess_packet_terminal_evidence(tmp_path, bridge_id)
    api_accepted = evidence["evidence_valid"] is True

    assert checker_accepted is accepted, f"checker route 3 disagreed with the shape contract: {checker_errors}"
    assert api_accepted is accepted, f"evidence API disagreed with the shape contract: {evidence['reasons']}"
    if deny_fragment is not None:
        assert any(deny_fragment in error for error in checker_errors), (
            f"route-3 denial was not attributable to the expiry clause; got {checker_errors}"
        )
    assert checker_accepted == api_accepted, (
        "cross-layer drift: checker route 3 and assess_packet_terminal_evidence "
        f"classified the same packet differently (checker_errors={checker_errors}, "
        f"api_reasons={evidence['reasons']})"
    )
