from __future__ import annotations

import pytest

from scripts.sdk_bridge_bash_guard import bridge_bash_mutation_reason, protected_bridge_paths


@pytest.mark.parametrize(
    "command",
    [
        "Get-Content bridge/INDEX.md",
        "git diff -- bridge/example-001.md",
        "python -c \"from pathlib import Path; print(Path('bridge/INDEX.md').read_text())\"",
    ],
)
def test_read_only_bridge_references_are_allowed(command: str) -> None:
    assert bridge_bash_mutation_reason(command) is None


@pytest.mark.parametrize(
    "command",
    [
        "echo GO > bridge/INDEX.md",
        "Set-Content bridge/example-001.md 'GO'",
        "Move-Item tmp.md bridge/example-001.md",
        "python -c \"from pathlib import Path; Path('bridge/example-001.md').write_text('GO')\"",
        "python -c \"import os; os.replace('tmp.md', r'E:\\GT-KB\\bridge\\INDEX.md')\"",
        "git restore -- bridge/INDEX.md",
    ],
)
def test_bridge_mutation_shapes_are_denied(command: str) -> None:
    reason = bridge_bash_mutation_reason(command)

    assert reason is not None
    assert "Bash bridge artifact mutation denied" in reason
    assert "guarded Write/Edit" in reason


def test_protected_paths_are_deduplicated_and_preserve_first_spelling() -> None:
    paths = protected_bridge_paths("type bridge\\INDEX.md; echo x > bridge/INDEX.md")

    assert paths == ("bridge\\INDEX.md",)
