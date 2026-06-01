"""GT-KB workspace activation tests for the hard-block bridge-compliance gate.

Verifies that the framework hook is correctly activated in this GT-KB
workspace and that it hard-blocks (emit_deny) non-compliant bridge writes.

Per ``bridge/gov-process-spec-precondition-2026-04-29-005.md`` REVISED-2 GO
at -006 + ``DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001``.A1 +
``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001``.A1.

These tests are scoped to GT-KB workspace activation only — they do NOT
duplicate the framework's own test suite at
``groundtruth-kb/tests/test_governance_hooks.py`` (56 passing, covers hook
behavior across all branches).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"
SETTINGS_JSON = REPO_ROOT / ".claude" / "settings.json"
AUTHOR_METADATA = (
    "author_identity: Codex\n"
    "author_harness_id: A\n"
    "author_session_context_id: session-123\n"
    "author_model: GPT-5.5\n"
    "author_model_version: 5.5\n"
    "author_model_configuration: Extra High\n"
)


def _file_sha256(path: Path) -> str:
    # Read as text and normalize CRLF to LF to prevent OS-specific hashing failures.
    content = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _run_hook(payload: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python", str(ACTIVE_HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(REPO_ROOT),
    )


def test_hook_file_exists_at_active_location() -> None:
    """Verifies bridge/gov-process-spec-precondition-2026-04-29-005.md §3
    test 1: .claude/hooks/bridge-compliance-gate.py exists.
    """
    assert ACTIVE_HOOK.exists(), f"Active hook missing at {ACTIVE_HOOK}"
    assert ACTIVE_HOOK.is_file()


def test_hook_matches_template_or_documented_divergence() -> None:
    """Verifies bridge/gov-process-spec-precondition-2026-04-29-005.md §3
    test 2: active hook matches template (Option A: byte-equal).
    """
    assert TEMPLATE_HOOK.exists(), f"Template hook missing at {TEMPLATE_HOOK}"
    active_hash = _file_sha256(ACTIVE_HOOK)
    template_hash = _file_sha256(TEMPLATE_HOOK)
    assert active_hash == template_hash, (
        f"Active hook (sha256: {active_hash}) does not match template "
        f"(sha256: {template_hash}). Per gov-process-spec-precondition "
        f"-005 §2.3 Option A, GT-KB workspace activates the framework "
        f"template byte-for-byte."
    )


def test_settings_json_registers_hook_for_write_and_edit() -> None:
    """Verifies bridge/gov-process-spec-precondition-2026-04-29-005.md §3
    test 3: .claude/settings.json registers the hook with Write+Edit matcher.
    """
    settings = json.loads(SETTINGS_JSON.read_text(encoding="utf-8"))
    pre_tool_use = settings.get("hooks", {}).get("PreToolUse", [])
    matching_entries = [
        entry
        for entry in pre_tool_use
        if any("bridge-compliance-gate.py" in hook.get("command", "") for hook in entry.get("hooks", []))
    ]
    assert matching_entries, "bridge-compliance-gate.py not registered in PreToolUse"
    assert len(matching_entries) == 1, "bridge-compliance-gate.py registered multiple times"
    matcher = matching_entries[0].get("matcher", "")
    assert "Write" in matcher, f"matcher missing Write: {matcher!r}"
    assert "Edit" in matcher, f"matcher missing Edit: {matcher!r}"


def test_proposal_lacking_spec_links_blocked_with_deny() -> None:
    """Verifies DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.A1:
    hook MUST hard-block (emit_deny) bridge proposals lacking concrete
    Specification Links section. Per bridge/gov-process-spec-precondition-
    2026-04-29-005.md §3 test 4 + REVISED-2 GO at -006.
    """
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                # Non-versioned bridge path (no -NNN): exempts the
                # GTKB-GOV-PROPOSAL-STANDARDS Slice 1 body-status-token rule
                # (versioned-only) so this fixture isolates the Specification
                # Links clause under test. Versioned-heading-first BLOCK behavior
                # is covered by test_bridge_compliance_gate_body_status_token.py.
                "file_path": "bridge/test-fake-proposal-no-spec-links.md",
                "content": "# Implementation Proposal\n\nDo a thing without citing any specs.",
            },
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )
    result = _run_hook(payload)
    assert result.returncode == 0, f"Hook exited non-zero: {result.stderr}"
    output = json.loads(result.stdout)
    hsoutput = output.get("hookSpecificOutput", {})
    assert hsoutput.get("hookEventName") == "PreToolUse"
    assert hsoutput.get("permissionDecision") == "deny", (
        f"Expected deny; got {hsoutput.get('permissionDecision')!r}. Full output: {output}"
    )
    assert "Specification Links" in hsoutput.get("permissionDecisionReason", "")


def _template_shaped_advisory_content() -> str:
    return f"""ADVISORY

{AUTHOR_METADATA}

bridge_kind: loyal_opposition_advisory
Document: test-advisory-report
Version: 001
Author: Loyal Opposition
Date: 2026-05-13 UTC

## Source

Owner requested advisory review.

## Claim

This is advisory material, not an implementation proposal.

## Owner Decision Needed

None.

## Recommended Prime Action

Review and decide whether to convert, defer, or reject.

## Classification Slot

Axis-2 advisory.
"""


def test_template_shaped_advisory_without_spec_links_passes() -> None:
    """Verifies bridge/gtkb-bridge-advisory-status-001-013.md IP-12:
    a template-shaped first-line ADVISORY report is not treated as an
    implementation proposal requiring Specification Links.
    """
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "bridge/test-advisory-report-001.md",
                "content": _template_shaped_advisory_content(),
            },
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )

    result = _run_hook(payload)

    assert result.returncode == 0, result.stderr
    if result.stdout.strip():
        output = json.loads(result.stdout)
        decision = output.get("hookSpecificOutput", {}).get("permissionDecision")
        assert decision != "deny", f"Template-shaped ADVISORY incorrectly denied. Output: {output}"


def test_malformed_advisory_report_blocked_with_template_message() -> None:
    """Verifies bridge/gtkb-bridge-advisory-status-001-013.md IP-12:
    malformed first-line ADVISORY reports are denied with the ADVISORY
    template-specific message.
    """
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "bridge/test-advisory-report-001.md",
                "content": "ADVISORY\n\n## Claim\n\nMissing required template fields.",
            },
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )

    result = _run_hook(payload)

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    hsoutput = output.get("hookSpecificOutput", {})
    assert hsoutput.get("permissionDecision") == "deny"
    reason = hsoutput.get("permissionDecisionReason", "")
    assert "ADVISORY bridge reports must match" in reason
    assert "verified ADVISORY report template" in reason


def test_verified_lacking_spec_to_test_mapping_blocked_with_deny() -> None:
    """Verifies DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.A1:
    hook MUST hard-block (emit_deny) VERIFIED bridge reports lacking
    spec-to-test mapping or executed-test evidence. Per
    bridge/gov-process-spec-precondition-2026-04-29-005.md §3 test 5.
    """
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "bridge/test-fake-verified-no-tests-002.md",
                "content": ("VERIFIED\n\n## Specification Links\n- DCL-EXAMPLE-001\n\nNo command evidence here."),
            },
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )
    result = _run_hook(payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    hsoutput = output.get("hookSpecificOutput", {})
    assert hsoutput.get("permissionDecision") == "deny", (
        f"Expected deny; got {hsoutput.get('permissionDecision')!r}. Full output: {output}"
    )
    reason = hsoutput.get("permissionDecisionReason", "")
    assert "spec-to-test" in reason.lower() or "Specification Links" in reason or "Applicability Preflight" in reason


def test_go_lacking_applicability_preflight_blocked_with_deny() -> None:
    """GO verdicts must carry a clean Applicability Preflight packet so
    cross-cutting spec applicability is not only memory/judgment based.
    """
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "bridge/test-fake-go-no-preflight-002.md",
                "content": "GO\n\n## Findings\n\nNo blocking findings.",
            },
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )
    result = _run_hook(payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    hsoutput = output.get("hookSpecificOutput", {})
    assert hsoutput.get("permissionDecision") == "deny"
    assert "Applicability Preflight" in hsoutput.get("permissionDecisionReason", "")


def test_go_with_clean_applicability_preflight_passes() -> None:
    """A GO verdict with a generated clean preflight packet is not blocked by
    the applicability gate.
    """
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "bridge/test-fake-go-with-preflight-002.md",
                "content": (
                    "GO\n" + AUTHOR_METADATA + "\n"
                    "## Applicability Preflight\n\n"
                    "- packet_hash: `sha256:"
                    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef`\n"
                    "- missing_required_specs: []\n\n"
                    "## Findings\n\nNo blocking findings."
                ),
            },
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )
    result = _run_hook(payload)
    assert result.returncode == 0
    if result.stdout.strip():
        output = json.loads(result.stdout)
        decision = output.get("hookSpecificOutput", {}).get("permissionDecision")
        assert decision != "deny", f"Clean GO verdict incorrectly denied. Output: {output}"


def _pending_preflight_content(*, include_application_spec: bool) -> str:
    spec_lines = [
        "- GOV-FILE-BRIDGE-AUTHORITY-001",
        "- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
        "- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
    ]
    if include_application_spec:
        spec_lines.append("- ADR-ISOLATION-APPLICATION-PLACEMENT-001")
    return (
        "NEW\n" + AUTHOR_METADATA + "\n"
        "# Implementation Proposal\n\n"
        # bridge_kind: spec_intake (WI-3315 IP-3) makes this fixture exempt from
        # BOTH the WI-3314 project-metadata-presence gate AND the WI-3315
        # WI/project membership gate -- both live inside the
        # `not _bridge_kind_is_metadata_exempt` branch. The fixture then reaches
        # the pending applicability-preflight path (the behavior these tests
        # exist to exercise) without depending on live MemBase membership rows.
        "bridge_kind: spec_intake\n\n"
        'target_paths: ["applications/Agent_Red/src/app.py"]\n\n'
        # Placeholder project-linkage metadata; harmless under the bridge_kind
        # exemption above (retained for a minimal diff vs WI-3314 IP-8).
        "Project Authorization: PAUTH-TEST-PENDING-PREFLIGHT\n"
        "Project: PROJECT-TEST-PENDING-PREFLIGHT\n"
        "Work Item: WI-0000\n\n"
        "This proposal touches Agent Red application isolation.\n\n"
        "## Specification Links\n\n" + "\n".join(spec_lines) + "\n\n"
        "## Specification-Derived Verification\n\n"
        "Run `python -m pytest tests/example.py`.\n"
    )


def test_bridge_hook_blocks_write_when_pending_content_fails_preflight() -> None:
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "bridge/test-fake-pending-preflight-001.md",
                "content": _pending_preflight_content(include_application_spec=False),
            },
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )

    result = _run_hook(payload)

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    hsoutput = output.get("hookSpecificOutput", {})
    assert hsoutput.get("permissionDecision") == "deny"
    reason = hsoutput.get("permissionDecisionReason", "")
    assert "Pre-filing applicability preflight failed" in reason
    assert "ADR-ISOLATION-APPLICATION-PLACEMENT-001" in reason
    # NO-GO -006 F1: hook denial output must include the blocked file path
    # so operators can identify which Write was rejected.
    assert "bridge/test-fake-pending-preflight-001.md" in reason
    assert "file_path=" in reason


def test_bridge_hook_allows_write_when_pending_content_passes_preflight() -> None:
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "bridge/test-fake-pending-preflight-001.md",
                "content": _pending_preflight_content(include_application_spec=True),
            },
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )

    result = _run_hook(payload)

    assert result.returncode == 0, result.stderr
    if result.stdout.strip():
        output = json.loads(result.stdout)
        decision = output.get("hookSpecificOutput", {}).get("permissionDecision")
        assert decision != "deny", f"Compliant pending proposal incorrectly denied. Output: {output}"


def test_bridge_hook_does_not_claim_edit_applicability_preflight() -> None:
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "bridge/test-fake-pending-preflight-001.md",
                "content": _pending_preflight_content(include_application_spec=False),
            },
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )

    result = _run_hook(payload)

    assert result.returncode == 0, result.stderr
    if result.stdout.strip():
        output = json.loads(result.stdout)
        reason = output.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
        assert "Pre-filing applicability preflight failed" not in reason


def test_bridge_hook_preflight_has_no_cache_between_writes() -> None:
    failing_payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "bridge/test-fake-pending-preflight-001.md",
                "content": _pending_preflight_content(include_application_spec=False),
            },
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )
    passing_payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "bridge/test-fake-pending-preflight-001.md",
                "content": _pending_preflight_content(include_application_spec=True),
            },
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )

    failing = _run_hook(failing_payload)
    passing = _run_hook(passing_payload)

    assert json.loads(failing.stdout).get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
    if passing.stdout.strip():
        output = json.loads(passing.stdout)
        assert output.get("hookSpecificOutput", {}).get("permissionDecision") != "deny"


def test_bridge_hook_scratch_path_is_root_contained_and_removed() -> None:
    bridge_id = "test-fake-pending-preflight"
    scratch_dir = REPO_ROOT / ".tmp" / "bridge-preflight-hook"
    before = set(scratch_dir.glob(f"{bridge_id}-*.md")) if scratch_dir.exists() else set()
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": f"bridge/{bridge_id}-001.md",
                "content": _pending_preflight_content(include_application_spec=True),
            },
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )

    result = _run_hook(payload)

    assert result.returncode == 0, result.stderr
    after = set(scratch_dir.glob(f"{bridge_id}-*.md")) if scratch_dir.exists() else set()
    assert after == before


def test_compliant_proposal_passes() -> None:
    """Verifies the inverse: a compliant proposal with proper Specification
    Links section is NOT blocked. Per bridge/gov-process-spec-precondition-
    2026-04-29-005.md §3 test 6.
    """
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                # Non-versioned bridge path (see body-status-token note above):
                # isolates the Specification Links clause from the versioned-only
                # Slice 1 rule.
                "file_path": "bridge/test-fake-compliant.md",
                "content": (
                    "# Implementation Proposal\n\n"
                    "## Specification Links\n\n"
                    "- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001\n"
                    "- GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001\n"
                    "- .claude/rules/file-bridge-protocol.md\n"
                ),
            },
            "session_id": "test",
            "cwd": str(REPO_ROOT),
        }
    )
    result = _run_hook(payload)
    assert result.returncode == 0
    # Compliant proposal: hook should not deny.
    if result.stdout.strip():
        output = json.loads(result.stdout)
        decision = output.get("hookSpecificOutput", {}).get("permissionDecision")
        assert decision != "deny", f"Compliant proposal incorrectly denied. Output: {output}"
