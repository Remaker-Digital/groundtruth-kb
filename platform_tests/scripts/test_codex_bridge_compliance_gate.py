"""Codex bridge-compliance hook parity tests."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ADAPTER_PATH = REPO_ROOT / ".codex" / "gtkb-hooks" / "bridge-compliance-gate-bash-adapter.py"
CANONICAL_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
SKIPPED_PATH = REPO_ROOT / ".codex" / "gtkb-hooks" / "last-bridge-audit-skipped.json"
AUTHOR_METADATA = (
    "author_identity: Codex\n"
    "author_harness_id: A\n"
    "author_session_context_id: session-123\n"
    "author_model: GPT-5.5\n"
    "author_model_version: 5.5\n"
    "author_model_configuration: Extra High\n"
)


@pytest.fixture(autouse=True)
def manage_work_intent_claims():
    subprocess.run(
        ["python", "scripts/bridge_claim_cli.py", "claim", "test-codex-deny", "--session-id", "test"],
        cwd=str(REPO_ROOT),
        check=True,
    )
    subprocess.run(
        ["python", "scripts/bridge_claim_cli.py", "claim", "test-codex-allow", "--session-id", "test"],
        cwd=str(REPO_ROOT),
        check=True,
    )
    yield
    subprocess.run(
        ["python", "scripts/bridge_claim_cli.py", "release", "test-codex-deny", "--session-id", "test"],
        cwd=str(REPO_ROOT),
        check=False,
    )
    subprocess.run(
        ["python", "scripts/bridge_claim_cli.py", "release", "test-codex-allow", "--session-id", "test"],
        cwd=str(REPO_ROOT),
        check=False,
    )


def _load_adapter():
    spec = importlib.util.spec_from_file_location("bridge_compliance_gate_bash_adapter", ADAPTER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["bridge_compliance_gate_bash_adapter"] = module
    spec.loader.exec_module(module)
    return module


def test_codex_bridge_compliance_hook_is_configured() -> None:
    hooks = json.loads((REPO_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    commands = [
        hook["command"]
        for groups in hooks["hooks"].values()
        for group in groups
        for hook in group.get("hooks", [])
        if isinstance(hook.get("command"), str)
    ]

    assert ADAPTER_PATH.is_file()
    assert (REPO_ROOT / ".codex" / "gtkb-hooks" / "bridge-compliance-gate.cmd").is_file()
    assert (REPO_ROOT / ".codex" / "gtkb-hooks" / "bridge-compliance-audit.cmd").is_file()
    assert any("bridge-compliance-gate.cmd" in command for command in commands)
    assert any("bridge-compliance-audit.cmd" in command for command in commands)


def test_adapter_extracts_common_bash_bridge_write_patterns() -> None:
    adapter = _load_adapter()
    samples = [
        ("cat > bridge/example-thread-001.md <<'EOF'\nNEW\nEOF\n", "bridge/example-thread-001.md", "NEW\n"),
        ("printf 'NEW\\n' > bridge/example-thread-001.md", "bridge/example-thread-001.md", "NEW\n"),
        ("echo 'NEW' > bridge/example-thread-001.md", "bridge/example-thread-001.md", "NEW"),
        (
            "python -c \"from pathlib import Path; Path('bridge/example-thread-001.md').write_text('NEW')\"",
            "bridge/example-thread-001.md",
            "NEW",
        ),
        ("tee bridge/example-thread-001.md <<'EOF'\nNEW\nEOF\n", "bridge/example-thread-001.md", ""),
    ]

    for command, expected_path, expected_content in samples:
        path, content = adapter.extract_bridge_write(command)
        assert path == expected_path
        assert content == expected_content


def test_adapter_denies_non_compliant_bridge_write() -> None:
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "cat > bridge/test-codex-deny-001.md <<'EOF'\nNEW\n\n# Missing spec links\nEOF\n"},
        "cwd": str(REPO_ROOT),
        "session_id": "test",
    }

    result = subprocess.run(
        ["python", str(ADAPTER_PATH)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=10,
        check=False,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    reason = output["hookSpecificOutput"]["permissionDecisionReason"]
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "Specification Links" in reason


def test_adapter_allows_compliant_bridge_write() -> None:
    payload = {
        "tool_name": "Bash",
        "tool_input": {
            "command": (
                "cat > bridge/test-codex-allow-001.md <<'EOF'\n"
                "NO-GO\n"
                f"{AUTHOR_METADATA}\n"
                "## Findings\n\nReview finding.\nEOF\n"
            )
        },
        "cwd": str(REPO_ROOT),
        "session_id": "test",
    }

    result = subprocess.run(
        ["python", str(ADAPTER_PATH)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=10,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() in ("", "{}")


def test_adapter_writes_skipped_extraction_diagnostic() -> None:
    adapter = _load_adapter()
    if SKIPPED_PATH.exists():
        SKIPPED_PATH.unlink()

    assert adapter.extract_bridge_write("cat > bridge/test-skip-001.md <<'EOF'\nNEW\n") is None

    diagnostic = json.loads(SKIPPED_PATH.read_text(encoding="utf-8"))
    assert diagnostic["skipped"] is True
    assert "unclosed heredoc" in diagnostic["reason"]


def test_audit_only_detects_non_compliant_files_without_blocking(tmp_path) -> None:
    audit_path = tmp_path / "last-bridge-audit.json"
    target = REPO_ROOT / "bridge" / "test-audit-non-compliant-001.md"
    target.write_text("NEW\n\n# Missing spec links\n", encoding="utf-8")
    try:
        result = subprocess.run(
            [
                "python",
                str(CANONICAL_HOOK),
                "--audit-only",
                "--file-path",
                "bridge/test-audit-non-compliant-001.md",
                "--audit-output",
                str(audit_path),
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=10,
            check=False,
        )
    finally:
        target.unlink(missing_ok=True)

    assert result.returncode == 0
    diagnostic = json.loads(audit_path.read_text(encoding="utf-8"))
    assert diagnostic["preflight_passed"] is False
    assert diagnostic["decision"] == "deny"
    assert "Specification Links" in diagnostic["reason"]


def test_audit_only_accepts_compliant_files_without_blocking(tmp_path) -> None:
    audit_path = tmp_path / "last-bridge-audit.json"
    target = REPO_ROOT / "bridge" / "test-audit-compliant-002.md"
    target.write_text(
        "GO\n" + AUTHOR_METADATA + "\n"
        "## Applicability Preflight\n\n"
        "- packet_hash: `sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef`\n"
        "- missing_required_specs: []\n",
        encoding="utf-8",
    )
    try:
        result = subprocess.run(
            [
                "python",
                str(CANONICAL_HOOK),
                "--audit-only",
                "--file-path",
                "bridge/test-audit-compliant-002.md",
                "--audit-output",
                str(audit_path),
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=10,
            check=False,
        )
    finally:
        target.unlink(missing_ok=True)

    assert result.returncode == 0
    diagnostic = json.loads(audit_path.read_text(encoding="utf-8"))
    assert diagnostic["preflight_passed"] is True
    assert diagnostic["decision"] == "pass"
