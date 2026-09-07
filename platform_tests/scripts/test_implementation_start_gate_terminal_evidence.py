"""Consumer-layer terminal-evidence tests for WI-5694 cycle 2.

Per ``bridge/gtkb-wi5694-verification-workflow-packet-consultation-001.md``
(GO at ``-002``). Cycle 1 added the read-only evidence API
``assess_packet_terminal_evidence``; this module locks the behavior of its only
live Loyal Opposition verification consumer, the PreToolUse implementation-start
gate, against owner decision ``DELIB-202667723`` (AUQ evidence
``AUQ-20260730-PACKET-EXPIRY-AUTHORITY-MODEL``).

T1-T4 are the four owner-mandated regression cases applied at the CONSUMER
layer; T5-T6 lock the clearance's own corridor and protected-target bounds.

Every test uses an isolated ``tmp_path`` project root with fixture bridge
chains, fixture packet files, and fixture work-intent registry state. The live
store and the live MemBase are never touched.
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from groundtruth_kb.db import KnowledgeDB

ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = ROOT / "config" / "governance" / "project-authorization-operation-taxonomy.toml"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import implementation_authorization as auth  # noqa: E402
from scripts import implementation_start_gate as gate  # noqa: E402

HELPER = gate.VERIFICATION_FINALIZATION_HELPER_PATH
EXEMPTION_PATTERN_ID = "verification-finalization-terminal-evidence"
APPROVED_TARGETS = ["scripts/sample.py", "platform_tests/scripts/test_sample.py"]


@pytest.fixture(autouse=True)
def _isolate_session_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Clear ambient session identity and route audit rows into the fixture root."""
    for name in auth.gtkb_session_id.BRIDGE_WORK_INTENT_ORDER:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "fixture")
    monkeypatch.setenv("GTKB_GATE_DENIALS_PATH", str(tmp_path / "gate-denials.jsonl"))


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _proposal_body(slug: str, target_paths: list[str]) -> str:
    return "\n".join(
        [
            "NEW",
            "",
            f"author_identity: prime-builder/fixture-{slug}",
            f"author_session_context_id: fixture-proposal-session-{slug}",
            "bridge_kind: implementation_proposal",
            f"Document: {slug}",
            "Version: 001",
            "",
            "# Implementation Proposal",
            "",
            f"target_paths: {json.dumps(target_paths)}",
            "Project Authorization: PAUTH-AUTH",
            "Project: PROJECT-AUTH",
            "Work Item: WI-AUTH-001",
            "",
            "## Specification Links",
            "",
            "- `GOV-FILE-BRIDGE-AUTHORITY-001`",
            "- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`",
            "- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`",
            "",
            "## Requirement Sufficiency",
            "",
            "Existing requirements sufficient - linked rules cover this implementation.",
            "",
            "## Specification-Derived Verification Plan",
            "",
            "| Test ID | Requirement | Verification |",
            "|---|---|---|",
            "| T-gate | GOV-FILE-BRIDGE-AUTHORITY-001 | pytest |",
            "",
        ]
    )


def _write_chain(
    root: Path,
    slug: str,
    *,
    target_paths: list[str] | None = None,
    latest: str = "NEW",
) -> None:
    """Write ``-001`` NEW proposal, ``-002`` GO, and a post-GO ``-003`` version.

    ``latest`` selects the post-GO version status: ``NEW`` (a post-implementation
    report awaiting the terminal verdict -> chain state ``awaiting_review``),
    ``VERIFIED`` (terminal), or ``NONE`` (nothing after the GO).
    """
    bridge = root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    (bridge / f"{slug}-001.md").write_text(_proposal_body(slug, target_paths or APPROVED_TARGETS), encoding="utf-8")
    (bridge / f"{slug}-002.md").write_text(
        "\n".join(
            [
                "GO",
                f"author_identity: loyal-opposition/fixture-{slug}",
                f"author_session_context_id: fixture-review-session-{slug}",
                "bridge_kind: lo_verdict",
                f"Document: {slug}",
                "Version: 002",
                f"Responds to: bridge/{slug}-001.md",
                "",
                "# Verdict",
                "",
            ]
        ),
        encoding="utf-8",
    )
    if latest == "NONE":
        return
    (bridge / f"{slug}-003.md").write_text(
        "\n".join(
            [
                latest,
                f"author_identity: prime-builder/fixture-{slug}",
                f"author_session_context_id: fixture-report-session-{slug}",
                f"Document: {slug}",
                "Version: 003",
                f"Responds to: bridge/{slug}-002.md",
                "",
                "# Post-Implementation Report",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _iso(moment: datetime) -> str:
    return moment.isoformat().replace("+00:00", "Z")


def _write_packet(
    root: Path,
    slug: str,
    *,
    session_id: str = "session-lo",
    expires_at: datetime | None = None,
    finalized_at: datetime | None = None,
    with_impl_start: bool = True,
    target_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Write a schema-v3 named-cache packet whose hash matches its content."""
    now = datetime.now(UTC)
    expires = expires_at if expires_at is not None else now - timedelta(hours=2)
    finalized = finalized_at if finalized_at is not None else now - timedelta(hours=3)
    globs = target_paths or APPROVED_TARGETS
    packet: dict[str, Any] = {
        "bridge_id": slug,
        "created_at": _iso(now - timedelta(hours=4)),
        "expires_at": _iso(expires),
        "go_file": f"bridge/{slug}-002.md",
        "latest_status": "GO",
        "proposal_file": f"bridge/{slug}-001.md",
        "schema_version": 3,
        "spec_links": ["GOV-FILE-BRIDGE-AUTHORITY-001"],
        "target_path_globs": list(globs),
    }
    if with_impl_start:
        packet["implementation_start"] = {
            "bridge_id": slug,
            "finalized_at": _iso(finalized),
            "schema_version": 1,
            "session_id": session_id,
            "target_path_globs": list(globs),
        }
    packet["packet_hash"] = auth.packet_hash(packet)
    by_bridge = root / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
    by_bridge.mkdir(parents=True, exist_ok=True)
    (by_bridge / f"{slug}.json").write_text(json.dumps(packet, indent=2), encoding="utf-8")
    return packet


def _write_worker_session(root: Path, session_id: str) -> None:
    document = {
        "status": "open",
        "session_id": session_id,
        "harness_id": "T",
        "harness_name": "fixture",
        "worker_role_provenance": {
            "schema_version": 1,
            "session_id": session_id,
            "harness_id": "T",
            "harness_name": "fixture",
            "role": "prime-builder",
            "role_resolution_source": "test-fixture",
            "issued_at": "2026-07-31T00:00:00Z",
            "dispatch_run_id": None,
        },
    }
    path = root / "harness-state" / "fixture" / "session-envelopes" / f"{session_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")


def _claim(root: Path, slug: str, session_id: str = "session-lo") -> None:
    _write_worker_session(root, session_id)
    assert auth.bridge_work_intent_registry.acquire(slug, session_id, project_root=root)


def _corridor_command(
    slug: str,
    *,
    includes: list[str] | None = None,
    redirect: str | None = "writer_stdout.txt",
    finalize: bool = True,
    helper: str | None = None,
    slug_flag: bool = True,
) -> str:
    """Build the canonical finalization invocation.

    The default carries an output redirect because that is the shape that reaches
    the gate: without a redirect the command has no mutating signal at all and
    ``gate_decision`` returns ``{}`` before any clearance is consulted (see
    ``test_t4_corridor_without_redirect_is_not_a_mutating_command``).
    """
    parts = ["python", helper or HELPER]
    if slug_flag:
        parts += ["--slug", slug]
    parts += ["--body-file", "draft-body.md"]
    if finalize:
        parts.append("--finalize-verified")
    parts += ["--no-prepopulate", "--commit-message", "msg"]
    for include in includes if includes is not None else ["scripts/sample.py", f"bridge/{slug}-004.md"]:
        parts += ["--include", include]
    if redirect:
        parts += [">", redirect]
    return " ".join(parts)


def _payload(root: Path, command: str, session_id: str = "session-lo") -> dict[str, object]:
    return {
        "cwd": str(root),
        "session_id": session_id,
        "tool_name": "bash",
        "tool_input": {"command": command},
    }


def _exemptions(root: Path) -> list[dict[str, Any]]:
    path = root / "gate-denials.jsonl"
    if not path.is_file():
        return []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [row for row in rows if row.get("pattern_id") == EXEMPTION_PATTERN_ID]


def _ready_thread(
    root: Path,
    slug: str,
    *,
    session_id: str = "session-lo",
    claim_session: str | None = None,
    **packet_kwargs: Any,
) -> None:
    """Chain awaiting the terminal verdict, a packet, and a work-intent claim."""
    _write_chain(root, slug, latest="NEW")
    _write_packet(root, slug, session_id=session_id, **packet_kwargs)
    _claim(root, slug, claim_session or session_id)


# ---------------------------------------------------------------------------
# T1: expired-but-live-at-implementation ACCEPT (DELIB-202667723 case 1)
# ---------------------------------------------------------------------------


def test_t1_expired_but_live_at_implementation_clears_finalization(tmp_path: Path) -> None:
    """An expired-but-live-at-implementation, uncontested packet clears the
    canonical finalization command.

    The exemption-row assertions were removed when the gate's ``.gtkb-state``
    audit writer was deleted (owner AUQ 2026-09-05). Gate exemptions are no
    longer recorded anywhere, so only the clearance behavior is asserted here.
    """
    slug = "wi5694-t1"
    _ready_thread(tmp_path, slug)

    result = gate.gate_decision(_payload(tmp_path, _corridor_command(slug)))

    assert result == {}


def test_t1_evidence_api_agrees_with_the_consumer_decision(tmp_path: Path) -> None:
    """The clearance consumes the cycle-1 API rather than re-deriving expiry:
    the same fixture the gate clears is evidence-valid but not active-valid."""
    slug = "wi5694-t1-api"
    _ready_thread(tmp_path, slug)

    assessment = auth.assess_packet_terminal_evidence(tmp_path, slug)

    assert assessment["evidence_valid"] is True
    assert assessment["expired"] is True
    assert assessment["live_at_implementation"] is True
    assert assessment["active_valid"] is False
    assert gate.gate_decision(_payload(tmp_path, _corridor_command(slug))) == {}


# ---------------------------------------------------------------------------
# T2: expired-before-implementation REJECT (DELIB-202667723 case 2)
# ---------------------------------------------------------------------------


def test_t2a_finalized_after_expiry_is_blocked(tmp_path: Path) -> None:
    """finalized_at > expires_at: the packet was never live at implementation,
    so the corridor falls through to the unchanged fail-closed gate."""
    slug = "wi5694-t2a"
    now = datetime.now(UTC)
    _ready_thread(
        tmp_path,
        slug,
        expires_at=now - timedelta(hours=3),
        finalized_at=now - timedelta(hours=1),
    )

    result = gate.gate_decision(_payload(tmp_path, _corridor_command(slug)))

    assert result["decision"] == "block"
    assert "GTKB-IMPLEMENTATION-START-GATE" in result["reason"]
    assert _exemptions(tmp_path) == []


def test_t2b_missing_implementation_start_is_blocked(tmp_path: Path) -> None:
    """A packet with no durable implementation_start block never durably started,
    so it is not historical evidence and the corridor is blocked."""
    slug = "wi5694-t2b"
    _ready_thread(tmp_path, slug, with_impl_start=False)

    result = gate.gate_decision(_payload(tmp_path, _corridor_command(slug)))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


# ---------------------------------------------------------------------------
# T3: contested REJECT (DELIB-202667723 case 3)
# ---------------------------------------------------------------------------


def test_t3_contested_thread_is_blocked(tmp_path: Path) -> None:
    """An active claim from a session other than the packet's implementation
    session marks the thread contested; the corridor falls through."""
    slug = "wi5694-t3"
    _ready_thread(tmp_path, slug, session_id="session-prime", claim_session="session-lo")

    result = gate.gate_decision(_payload(tmp_path, _corridor_command(slug)))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


def test_t3_uncontested_control_clears(tmp_path: Path) -> None:
    """The identical fixture minus the competing claim clears, pinpointing the
    contested clause as the sole cause of the rejection above."""
    slug = "wi5694-t3-control"
    _ready_thread(tmp_path, slug, session_id="session-lo", claim_session="session-lo")

    assert gate.gate_decision(_payload(tmp_path, _corridor_command(slug))) == {}


def test_t3_registry_read_error_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A work-intent registry read error fails closed rather than clearing."""
    slug = "wi5694-t3-registry"
    _ready_thread(tmp_path, slug)

    def _boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError("registry unavailable")

    monkeypatch.setattr(gate.bridge_work_intent_registry, "current_holder", _boom)

    result = gate.gate_decision(_payload(tmp_path, _corridor_command(slug)))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


# ---------------------------------------------------------------------------
# T4: live unchanged (DELIB-202667723 case 4; WI-4532 invariant)
# ---------------------------------------------------------------------------


def _seed_project_authorization(root: Path) -> None:
    taxonomy_target = root / "config" / "governance" / TAXONOMY_PATH.name
    taxonomy_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TAXONOMY_PATH, taxonomy_target)
    db = KnowledgeDB(root / "groundtruth.db")
    try:
        db.insert_deliberation(
            "DELIB-PROJECT-AUTH",
            "owner_conversation",
            "Owner approved project authorization",
            "Owner approved project implementation scope.",
            "{}",
            "test",
            "seed project authorization decision",
            outcome="owner_decision",
        )
        db.insert_project("Authorized Project", "test", "seed project", id="PROJECT-AUTH", status="active")
        db.insert_work_item(
            "WI-AUTH-001",
            "Authorized work item",
            "new",
            "platform",
            "open",
            "test",
            "seed work item",
            stage="backlogged",
        )
        db.link_project_work_item("PROJECT-AUTH", "WI-AUTH-001", "test", "seed work item membership")
        db.insert_spec(
            id="SPEC-AUTH-SEED",
            title="Authorized seed specification",
            status="verified",
            changed_by="test",
            change_reason="seed spec for project authorization fixture",
        )
    finally:
        db.close()


def _apply_patch_payload(root: Path, target: str, session_id: str = "session-lo") -> dict[str, object]:
    return {
        "cwd": str(root),
        "session_id": session_id,
        "tool_name": "apply_patch",
        "tool_input": {"patch": f"*** Begin Patch\n*** Update File: {target}\n@@\n+pass\n*** End Patch\n"},
    }


def test_t4_live_packet_still_authorizes_ordinary_mutation(tmp_path: Path) -> None:
    """A live packet on a GO-latest chain authorizes an ordinary implementation
    mutation through validate_targets exactly as before this change."""
    slug = "wi5694-t4-live"
    _seed_project_authorization(tmp_path)
    _write_chain(tmp_path, slug, latest="NONE")
    packet = auth.create_authorization_packet(tmp_path, slug)
    auth.write_packet(tmp_path, packet)
    _claim(tmp_path, slug)

    result = gate.gate_decision(_apply_patch_payload(tmp_path, "scripts/sample.py"))

    assert result == {}
    assert _exemptions(tmp_path) == []


def test_wi7751_claimed_bridge_id_resolves_from_the_registry_not_a_packet(tmp_path: Path) -> None:
    """WI-7751 principal-risk guard: the resolved bridge id must be NON-EMPTY.

    The gate reads ``bridge_id`` from the work-intent registry now that the packet
    is retired. If that lookup silently returned ``""`` the three retained controls
    keyed on it -- the claim check and both concurrency checks -- would still be
    *called*, and would still appear to run, while checking nothing. Every one of
    them would degrade quietly rather than fail.

    This asserts the positive value rather than the absence of an error, because an
    empty-string regression raises nothing. It is the only assertion that catches it.
    """
    slug = "wi7751-claim-id"
    _ready_thread(tmp_path, slug)

    resolved = gate._claimed_bridge_id(tmp_path, "session-lo")

    assert resolved == slug
    assert resolved  # explicit non-empty guard: the regression this test exists for


def test_wi7751_claimed_bridge_id_fails_closed_without_a_claim(tmp_path: Path) -> None:
    """Non-vacuity control for the guard above.

    Without a claim the resolver returns ``""``. That is correct -- it is not a
    bootstrap id, so the claim check turns it into a denial -- but it proves the
    test above measures a real lookup rather than a constant.
    """
    slug = "wi7751-no-claim"
    _write_chain(tmp_path, slug, latest="NONE")

    assert gate._claimed_bridge_id(tmp_path, "session-lo") == ""
    assert gate._claimed_bridge_id(tmp_path, "") == ""


def test_t4_packet_expiry_no_longer_blocks_an_in_scope_mutation(tmp_path: Path) -> None:
    """WI-7751: expiry is retired, so an in-scope mutation proceeds.

    Before WI-7751 an expired packet blocked this mutation. That block came from
    the implementation-start packet, which ``GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001``
    v5 retires along with its expiry semantics ("authorization carries no scope,
    expiry, mutation-class, or forbidden-operation semantics"). The session holds a
    live claim on a GO'd chain and the target is inside the approved proposal's
    ``target_paths``, so every RETAINED control passes and the gate allows.

    The companion test below is the non-vacuity guard: it proves this allow comes
    from controls passing rather than from the gate having stopped checking.
    """
    slug = "wi5694-t4-expired"
    _ready_thread(tmp_path, slug)

    result = gate.gate_decision(_apply_patch_payload(tmp_path, "scripts/sample.py"))

    assert result == {}
    assert _exemptions(tmp_path) == []


def test_t4_out_of_scope_target_still_blocks_after_expiry_retirement(tmp_path: Path) -> None:
    """WI-7751 non-vacuity guard: change scope is RETAINED where expiry is not.

    Same fixture as the test above, differing only in the target. v5 retires the
    packet but keeps change scope -- "change scope is the implementation proposal's
    declared ``target_paths``" -- so a protected path outside the approved set must
    still be refused. Without this, the test above would be indistinguishable from
    a gate that had stopped enforcing anything on this path.
    """
    slug = "wi5694-t4-outofscope"
    _ready_thread(tmp_path, slug)

    result = gate.gate_decision(_apply_patch_payload(tmp_path, "scripts/not_an_approved_target.py"))

    assert result["decision"] == "block"
    assert "outside the approved proposal's target_paths" in result["reason"]
    assert _exemptions(tmp_path) == []


def test_t4_packet_expiry_no_longer_blocks_an_in_scope_shell_mutation(tmp_path: Path) -> None:
    """The shell surface of the test above; same retirement, same reasoning."""
    slug = "wi5694-t4-shell"
    _ready_thread(tmp_path, slug)

    result = gate.gate_decision(_payload(tmp_path, "Set-Content -Path scripts/sample.py -Value x"))

    assert result == {}
    assert _exemptions(tmp_path) == []


def test_t4_corridor_without_redirect_is_not_a_mutating_command(tmp_path: Path) -> None:
    """Scope note carried into the report: a bare finalization invocation carries
    no mutating signal, so the gate returns {} before any clearance is consulted.
    The clearance governs the shapes that DO reach the authorization path."""
    slug = "wi5694-t4-bare"
    _ready_thread(tmp_path, slug)
    command = _corridor_command(slug, redirect=None)

    assert gate._is_mutating_command(command) is False
    assert gate.gate_decision(_payload(tmp_path, command)) == {}
    assert _exemptions(tmp_path) == []


# ---------------------------------------------------------------------------
# T5: corridor-key discipline
# ---------------------------------------------------------------------------


def test_t5_chained_command_falls_through(tmp_path: Path) -> None:
    """Chaining disqualifies the corridor key so the command is blocked."""
    slug = "wi5694-t5-chain"
    _ready_thread(tmp_path, slug)
    command = _corridor_command(slug) + "; rm -rf scripts"

    result = gate.gate_decision(_payload(tmp_path, command))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


def test_t5_without_finalize_verified_falls_through(tmp_path: Path) -> None:
    """A helper invocation lacking --finalize-verified is not the corridor."""
    slug = "wi5694-t5-nofinalize"
    _ready_thread(tmp_path, slug)

    result = gate.gate_decision(_payload(tmp_path, _corridor_command(slug, finalize=False)))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


def test_t5_missing_slug_flag_falls_through(tmp_path: Path) -> None:
    """An explicit --slug is required; without it the corridor cannot bind."""
    slug = "wi5694-t5-noslug"
    _ready_thread(tmp_path, slug)

    result = gate.gate_decision(_payload(tmp_path, _corridor_command(slug, slug_flag=False)))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


def test_t5_slug_mismatching_the_claim_falls_through(tmp_path: Path) -> None:
    """A --slug that is not this session's claimed thread cannot clear."""
    slug = "wi5694-t5-mismatch"
    _ready_thread(tmp_path, slug)
    command = _corridor_command(slug).replace(f"--slug {slug}", "--slug some-other-thread")

    result = gate.gate_decision(_payload(tmp_path, command))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


def test_t5_missing_work_intent_claim_falls_through(tmp_path: Path) -> None:
    """With no work-intent claim the corridor cannot bind a thread."""
    slug = "wi5694-t5-noclaim"
    _write_chain(tmp_path, slug, latest="NEW")
    _write_packet(tmp_path, slug)

    result = gate.gate_decision(_payload(tmp_path, _corridor_command(slug)))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


def test_t5_non_canonical_helper_falls_through(tmp_path: Path) -> None:
    """Only the canonical verdict helper keys the corridor."""
    slug = "wi5694-t5-helper"
    _ready_thread(tmp_path, slug)
    command = _corridor_command(slug, helper="scripts/impostor_write_verdict.py")

    result = gate.gate_decision(_payload(tmp_path, command))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


def test_t5_terminal_chain_is_not_this_corridor(tmp_path: Path) -> None:
    """A terminal-VERIFIED chain belongs to the WI-4837 post-VERIFIED clearance;
    this pre-terminal corridor declines it."""
    slug = "wi5694-t5-terminal"
    _write_chain(tmp_path, slug, latest="VERIFIED")
    _write_packet(tmp_path, slug)
    _claim(tmp_path, slug)

    result = gate.gate_decision(_payload(tmp_path, _corridor_command(slug)))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


def test_t5_post_verified_clearance_behavior_is_unchanged(tmp_path: Path) -> None:
    """The WI-4837 staging clearance's own outcome is untouched by this change:
    direct `git add` still routes to the canonical Git lifecycle."""
    slug = "wi5694-t5-wi4837"
    _write_chain(tmp_path, slug, latest="VERIFIED")
    _claim(tmp_path, slug)

    result = gate.gate_decision(_payload(tmp_path, "git add scripts/sample.py"))

    assert result["decision"] == "block"
    assert result["reason_code"] == "direct_git_effect_requires_lifecycle"


# ---------------------------------------------------------------------------
# T6: protected-target bound
# ---------------------------------------------------------------------------


def test_t6_include_outside_approved_paths_falls_through(tmp_path: Path) -> None:
    """A declared --include outside (approved target_paths union chain files)
    disqualifies the whole command."""
    slug = "wi5694-t6-outside"
    _ready_thread(tmp_path, slug)
    command = _corridor_command(slug, includes=["scripts/sample.py", "scripts/unrelated.py"])

    result = gate.gate_decision(_payload(tmp_path, command))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


def test_t6_in_bound_variant_clears(tmp_path: Path) -> None:
    """The in-bound variant of the same command clears, isolating the bound as
    the sole cause of the rejection above."""
    slug = "wi5694-t6-inbound"
    _ready_thread(tmp_path, slug)
    command = _corridor_command(slug, includes=["scripts/sample.py", "platform_tests/scripts/test_sample.py"])

    assert gate.gate_decision(_payload(tmp_path, command)) == {}


def test_t6_foreign_bridge_chain_file_falls_through(tmp_path: Path) -> None:
    """Only the thread's OWN numbered chain files are in bound."""
    slug = "wi5694-t6-foreign"
    _ready_thread(tmp_path, slug)
    command = _corridor_command(slug, includes=["bridge/some-other-thread-004.md"])

    result = gate.gate_decision(_payload(tmp_path, command))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


def test_t6_include_escaping_project_root_falls_through(tmp_path: Path) -> None:
    """A declared target that escapes the project root fails closed."""
    slug = "wi5694-t6-escape"
    _ready_thread(tmp_path, slug)
    command = _corridor_command(slug, includes=["../outside.py"])

    result = gate.gate_decision(_payload(tmp_path, command))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


def test_t6_redirect_into_protected_path_falls_through(tmp_path: Path) -> None:
    """A finalization helper never legitimately redirects into a controlled
    artifact; such a redirect disqualifies the clearance outright."""
    slug = "wi5694-t6-redirect"
    _ready_thread(tmp_path, slug)
    command = _corridor_command(slug, redirect="scripts/sample.py")

    result = gate.gate_decision(_payload(tmp_path, command))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


def test_t6_no_declared_targets_falls_through(tmp_path: Path) -> None:
    """When the gate could not enumerate targets and the command declares none,
    there is nothing to bound and the clearance fails closed."""
    slug = "wi5694-t6-empty"
    _ready_thread(tmp_path, slug)
    command = _corridor_command(slug, includes=[])

    result = gate.gate_decision(_payload(tmp_path, command))

    assert result["decision"] == "block"
    assert _exemptions(tmp_path) == []


# ---------------------------------------------------------------------------
# Corridor parser unit coverage
# ---------------------------------------------------------------------------


def test_corridor_parser_accepts_canonical_shapes() -> None:
    """The corridor parser accepts the documented invocation forms, including a
    leading PowerShell call operator and an absolute interpreter path."""
    parsed = gate._verification_finalization_corridor(
        f"python {HELPER} --slug thread-a --finalize-verified --include scripts/a.py"
    )
    assert parsed == ("thread-a", ["scripts/a.py"])

    parsed_call_operator = gate._verification_finalization_corridor(
        f"& groundtruth-kb/.venv/Scripts/python.exe {HELPER} --slug thread-a "
        "--finalize-verified --include scripts/a.py --include scripts/b.py"
    )
    assert parsed_call_operator == ("thread-a", ["scripts/a.py", "scripts/b.py"])

    parsed_equals = gate._verification_finalization_corridor(
        f"python {HELPER} --slug=thread-b --finalize-verified --include=scripts/a.py"
    )
    assert parsed_equals == ("thread-b", ["scripts/a.py"])


def test_corridor_parser_rejects_disqualified_shapes() -> None:
    """Chaining, substitution, a non-python verb, a foreign script, a missing
    finalize flag, and a missing slug each disqualify the corridor key."""
    base = f"python {HELPER} --slug thread-a --finalize-verified --include scripts/a.py"
    assert gate._verification_finalization_corridor(base + " | tee out.txt") is None
    assert gate._verification_finalization_corridor(base + " && rm -rf scripts") is None
    assert gate._verification_finalization_corridor(base.replace("python", "node", 1)) is None
    assert gate._verification_finalization_corridor(base.replace(HELPER, "scripts/other.py", 1)) is None
    assert gate._verification_finalization_corridor(base.replace(" --finalize-verified", "", 1)) is None
    assert gate._verification_finalization_corridor(base.replace("--slug thread-a ", "", 1)) is None
    assert gate._verification_finalization_corridor(f"python {HELPER} --slug thread-a") is None
    assert gate._verification_finalization_corridor("") is None


def test_bridge_chain_file_matcher_is_slug_scoped() -> None:
    """The chain-file bound recognizes only this thread's numbered bridge files."""
    assert gate._is_bridge_chain_file("thread-a", "bridge/thread-a-004.md") is True
    assert gate._is_bridge_chain_file("thread-a", "bridge/thread-a-0004.md") is True
    assert gate._is_bridge_chain_file("thread-a", "bridge/thread-b-004.md") is False
    assert gate._is_bridge_chain_file("thread-a", "bridge/thread-a-004.txt") is False
    assert gate._is_bridge_chain_file("thread-a", "bridge/thread-a.md") is False
    assert gate._is_bridge_chain_file("thread-a", "scripts/thread-a-004.md") is False
