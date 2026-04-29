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


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        entry for entry in pre_tool_use
        if any(
            "bridge-compliance-gate.py" in hook.get("command", "")
            for hook in entry.get("hooks", [])
        )
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
                "file_path": "bridge/test-fake-proposal-no-spec-links-001.md",
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
        f"Expected deny; got {hsoutput.get('permissionDecision')!r}. "
        f"Full output: {output}"
    )
    assert "Specification Links" in hsoutput.get("permissionDecisionReason", "")


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
                "content": (
                    "VERIFIED\n\n## Specification Links\n"
                    "- DCL-EXAMPLE-001\n\nNo command evidence here."
                ),
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
        f"Expected deny; got {hsoutput.get('permissionDecision')!r}. "
        f"Full output: {output}"
    )
    assert "spec-to-test" in hsoutput.get("permissionDecisionReason", "").lower() or \
           "Specification Links" in hsoutput.get("permissionDecisionReason", "")


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
                "file_path": "bridge/test-fake-compliant-001.md",
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
        assert decision != "deny", (
            f"Compliant proposal incorrectly denied. Output: {output}"
        )
