"""The shared effect gate refuses agent reads, searches, listings, prints and writes of credential material (c117).

Owner decision after the 2026-09-26 M13 host I incident ("Fix first: c117"): a review agent read production's
PostgreSQL service and password files while trying to run a test, and their contents reached its model provider. The
refusal comes before binding and scope, so every case here is decided without an authority, a binding or a claim.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from groundtruth_kb.bridge import effect_gate

ROOT = Path(__file__).resolve().parents[2]


def _decision(tool: str, tool_input: dict) -> dict:
    return effect_gate.gate_decision(
        {
            "tool_name": tool,
            "tool_input": tool_input,
            "session_id": "ctx-credential-test",
        }
    )


REFUSED_READS = [
    (
        "Read",
        {"file_path": "E:/GT-KB/infrastructure/postgresql/credentials/pg_service.conf"},
    ),
    (
        "Read",
        {"file_path": "E:\\GT-KB\\infrastructure\\postgresql\\credentials\\admin.pgpass"},
    ),
    ("Read", {"file_path": "C:/Users/owner/AppData/Roaming/postgresql/pgpass.conf"}),
    ("Read", {"file_path": ".env.local"}),
    ("Read", {"file_path": "config/.env"}),
    ("Read", {"file_path": "memory/topics/reference_openai_api_key.md"}),
    ("Grep", {"pattern": "password", "path": "infrastructure/postgresql/credentials"}),
    ("Glob", {"pattern": "**/*.pgpass"}),
    ("Glob", {"pattern": "**/pg_service.conf"}),
    ("view_file", {"AbsolutePath": "E:/GT-KB/.env.production"}),
    # Goose's adapter forwards its read-only tools under their namespaced names.
    ("developer__tree", {"path": "infrastructure/postgresql/credentials"}),
    ("developer__search", {"pattern": "**/*.pgpass"}),
]


@pytest.mark.parametrize(("tool", "tool_input"), REFUSED_READS)
def test_reads_and_searches_of_credential_material_are_refused_before_any_binding(tool, tool_input):
    decision = _decision(tool, tool_input)
    assert decision["decision"] == "block", decision
    assert decision["reason_code"] == "credential_material_protected", decision
    assert "credential material" in decision["reason"]


ALLOWED_READS = [
    ("Read", {"file_path": "README.md"}),
    ("developer__tree", {"path": "docs"}),
    ("Read", {"file_path": ".env.example"}),
    ("Read", {"file_path": ".env.integration.example"}),
    ("Read", {"file_path": "docs/credentials.md"}),
    ("Read", {"file_path": "groundtruth-kb/.venv/Scripts/python.exe"}),
    ("Grep", {"pattern": "credentials", "path": "docs"}),
    ("Glob", {"pattern": "**/*.py"}),
]


@pytest.mark.parametrize(("tool", "tool_input"), ALLOWED_READS)
def test_every_other_read_passes(tool, tool_input):
    assert _decision(tool, tool_input) == {}


REFUSED_COMMANDS = [
    (
        "Get-Content E:\\GT-KB\\infrastructure\\postgresql\\credentials\\pg_service.conf",
        "pg_service.conf",
    ),
    (
        "Get-Content 'E:\\GT-KB\\infrastructure\\postgresql\\credentials\\admin.pgpass'",
        "admin.pgpass",
    ),
    (
        "Get-ChildItem 'E:\\GT-KB' -Recurse -Include pg_service.conf,pgpass.conf",
        "pg_service.conf",
    ),
    ("cat .env.local", ".env.local"),
    (
        "$env:PGSERVICEFILE='E:\\GT-KB\\infrastructure\\postgresql\\credentials\\pg_service.conf'; python -m pytest x",
        "credentials",
    ),
    (
        'pwsh -Command "Get-Content E:\\x\\credentials\\authority.pgpass"',
        "authority.pgpass",
    ),
    ("Get-ChildItem Env:PG*", "environment listing"),
    ("gci env:", "environment listing"),
    ("dir env:\\", "environment listing"),
    ("printenv", "environment listing"),
    ("env | sort", "environment listing"),
    ("[System.Environment]::GetEnvironmentVariables()", "environment listing"),
    ('python -c "import os; print(os.environ)"', "environment listing"),
    ('node -e "console.log(process.env)"', "environment listing"),
    ("Write-Output $env:GTKB_OPENROUTER_API_KEY", "GTKB_OPENROUTER_API_KEY"),
    ("echo $OPENAI_API_KEY", "OPENAI_API_KEY"),
    ("echo %PGPASSWORD%", "PGPASSWORD"),
    ("[Environment]::GetEnvironmentVariable('GITHUB_TOKEN')", "GITHUB_TOKEN"),
    (
        "python -c \"import os; print(os.getenv('AWS_SECRET_ACCESS_KEY'))\"",
        "AWS_SECRET_ACCESS_KEY",
    ),
]


@pytest.mark.parametrize(("command", "named"), REFUSED_COMMANDS)
def test_shell_access_to_credential_material_is_refused_before_any_binding(command, named):
    decision = _decision("Bash", {"command": command})
    assert decision.get("reason_code") == "credential_material_protected", decision
    assert named in decision["reason"]


ALLOWED_COMMANDS = [
    "Get-Content README.md",
    "git status --porcelain",
    "Write-Output $env:PATH",
    "$env:GTKB_RUN_POSTGRES_INTEGRATION='1'",
    "foreach ($key in @('a')) { $key }",
    "Select-String -Path docs\\*.md -Pattern credentials",
    "set -e",
    "Set-Location docs",
    "python -c \"import os; print(os.environ['HOME'])\"",
]


@pytest.mark.parametrize("command", ALLOWED_COMMANDS)
def test_ordinary_shell_commands_name_no_credential_material(command):
    assert effect_gate._credential_material_access({"tool_name": "Bash", "tool_input": {"command": command}}) is None


def test_writes_are_judged_by_their_target_not_their_content():
    """A document may mention credential files; a write is refused only when its target is credential material."""
    mention = {
        "file_path": "docs/operations.md",
        "content": "The service file is pg_service.conf; never read .env.local.",
    }
    assert effect_gate._credential_material_access({"tool_name": "Write", "tool_input": mention}) is None
    written = _decision("Write", {"file_path": ".env.local", "content": "A=1"})
    assert written["reason_code"] == "credential_material_protected"
    edited = _decision(
        "Edit",
        {
            "file_path": "infrastructure/postgresql/credentials/pg_service.conf",
            "old_string": "a",
            "new_string": "b",
        },
    )
    assert edited["reason_code"] == "credential_material_protected"


def test_a_patch_that_touches_credential_material_is_refused():
    patch = "*** Begin Patch\n*** Update File: .env.local\n@@\n-A=1\n+A=2\n*** End Patch\n"
    assert _decision("apply_patch", {"input": patch})["reason_code"] == "credential_material_protected"


def _hook(payload: dict, cwd: Path) -> dict:
    done = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts" / "implementation_start_gate.py")],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        cwd=cwd,
    )
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


def test_the_registered_hook_script_denies_a_credential_read_natively_and_allows_other_reads(
    tmp_path,
):
    """The script every host registers for read events emits the host-facing deny for a credential read."""
    base = {
        "cwd": str(tmp_path),
        "session_id": "ctx-credential-test",
        "tool_name": "Read",
    }
    denied = _hook(
        {
            **base,
            "tool_input": {"file_path": "infrastructure/postgresql/credentials/pg_service.conf"},
        },
        tmp_path,
    )
    assert denied["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "credential material" in denied["hookSpecificOutput"]["permissionDecisionReason"]
    assert _hook({**base, "tool_input": {"file_path": "README.md"}}, tmp_path) == {}
