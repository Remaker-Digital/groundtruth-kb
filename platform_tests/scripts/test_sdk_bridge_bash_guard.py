from __future__ import annotations

from pathlib import Path

import pytest

from scripts.sdk_bridge_bash_guard import bridge_bash_mutation_reason, protected_bridge_paths

REPO_ROOT = Path(__file__).resolve().parents[2]


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
    assert "gt bridge deliver" in reason
    assert "exact next-artifact claim" in reason


@pytest.mark.parametrize(
    "command",
    [
        'python scripts/ollama_harness.py -p "review"',
        'python scripts/alibaba_cloud_studio_harness.py -p "review"',
        'python scripts/qualification_harness.py -p "review"',
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
