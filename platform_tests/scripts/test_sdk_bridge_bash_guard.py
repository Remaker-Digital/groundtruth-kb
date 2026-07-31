from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.sdk_bridge_bash_guard import bridge_bash_mutation_reason, protected_bridge_paths

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_BRIDGE_ADAPTERS = (
    (
        REPO_ROOT / ".codex" / "gtkb-hooks" / "bridge-compliance-gate-bash-adapter.py",
        REPO_ROOT / ".codex" / "gtkb-hooks" / "last-bridge-audit-skipped.json",
    ),
    (
        REPO_ROOT / ".codex" / "gtkb-hooks" / "wi-id-collision-gate-bash-adapter.py",
        REPO_ROOT / ".codex" / "gtkb-hooks" / "last-wi-id-collision-skipped.json",
    ),
)


def _load_adapter(path: Path):
    module_name = f"test_adapter_{path.stem.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _run_adapter(path: Path, command: str) -> subprocess.CompletedProcess[str]:
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "cwd": str(REPO_ROOT),
        "session_id": "test-codex-bridge-bash-adapter",
    }
    return subprocess.run(
        [sys.executable, str(path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=10,
        check=False,
    )


@pytest.mark.parametrize(
    "command",
    [
        "Get-Content bridge/example-001.md",
        "Get-Content bridge/INDEX.md",
        "git diff -- bridge/example-001.md",
        "python -c \"from pathlib import Path; print(Path('bridge/example-001.md').read_text())\"",
    ],
)
def test_read_only_bridge_references_are_allowed(command: str) -> None:
    assert bridge_bash_mutation_reason(command) is None


@pytest.mark.parametrize(
    "command",
    [
        "echo GO > bridge/example-001.md",
        "echo GO > bridge/INDEX.md",
        "Set-Content bridge/example-001.md 'GO'",
        "Set-Content bridge/INDEX.md 'GO'",
        "Move-Item tmp.md bridge/example-001.md",
        "python -c \"from pathlib import Path; Path('bridge/example-001.md').write_text('GO')\"",
        "python -c \"import os; os.replace('tmp.md', r'E:\\GT-KB\\bridge\\example-001.md')\"",
        "git restore -- bridge/example-001.md",
    ],
)
def test_bridge_mutation_shapes_are_denied(command: str) -> None:
    reason = bridge_bash_mutation_reason(command)

    assert reason is not None
    assert "Bash bridge artifact mutation denied" in reason
    assert "guarded Write/Edit" in reason


@pytest.mark.parametrize(
    "command",
    [
        'python scripts/ollama_harness.py -p "review"',
        'groundtruth-kb/.venv/Scripts/python.exe scripts/openrouter_harness.py -p "review"',
        r'& "E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe" scripts\ollama_harness.py -p "review"',
    ],
)
def test_sdk_harness_self_invocation_is_denied(command: str) -> None:
    reason = bridge_bash_mutation_reason(command)

    assert reason is not None
    assert "Bash SDK harness self-invocation denied" in reason
    assert "scripts/" in reason


@pytest.mark.parametrize(
    "command",
    [
        "Get-Content scripts/ollama_harness.py",
        "python -c \"print('scripts/ollama_harness.py')\"",
        "rg ollama_harness scripts",
    ],
)
def test_sdk_harness_benign_references_are_allowed(command: str) -> None:
    assert bridge_bash_mutation_reason(command) is None


def test_protected_paths_are_deduplicated_and_preserve_first_spelling() -> None:
    paths = protected_bridge_paths("type bridge\\example-001.md; echo x > bridge/example-001.md")

    assert paths == ("bridge\\example-001.md",)


@pytest.mark.parametrize(("adapter_path", "skipped_path"), CODEX_BRIDGE_ADAPTERS)
@pytest.mark.parametrize(
    "command",
    [
        "Get-Content bridge/example-001.md",
        "type bridge\\example-001.md",
        "git status -- bridge/example-001.md",
        "git add bridge/example-001.md",
        "git log -- bridge/example-001.md",
        "python -c \"from pathlib import Path; print(Path('bridge/example-001.md').read_text())\"",
    ],
)
def test_codex_bridge_bash_adapters_ignore_benign_bridge_references(
    adapter_path: Path, skipped_path: Path, command: str
) -> None:
    adapter = _load_adapter(adapter_path)
    skipped_path.unlink(missing_ok=True)

    assert adapter.extract_bridge_write(command) is None

    assert not skipped_path.exists()


@pytest.mark.parametrize(("adapter_path", "_skipped_path"), CODEX_BRIDGE_ADAPTERS)
@pytest.mark.parametrize(
    "command",
    [
        "Set-Content bridge/example-001.md 'GO'",
        "Move-Item tmp.md bridge/example-001.md",
        "git restore -- bridge/example-001.md",
        "python -c \"import os; os.replace('tmp.md', r'E:\\GT-KB\\bridge\\example-001.md')\"",
    ],
)
def test_codex_bridge_bash_adapters_fail_closed_for_unsupported_likely_writes(
    adapter_path: Path, _skipped_path: Path, command: str
) -> None:
    result = _run_adapter(adapter_path, command)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    hook_output = output["hookSpecificOutput"]
    assert hook_output["permissionDecision"] == "deny"
    assert "Unsupported likely bridge artifact write" in hook_output["permissionDecisionReason"]
