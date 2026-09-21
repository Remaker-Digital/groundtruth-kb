from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

LF_POLICY_PATHS = (
    ".gitattributes",
    ".agents/skills/gtkb-spec-intake/SKILL.md",
    ".agents/skills/gtkb-spec-intake/helpers/spec_intake.py",
    ".claude/skills/gtkb-spec-intake/SKILL.md",
    ".cursor/skills/gtkb-spec-intake/SKILL.md",
    ".agent/skills/gtkb-spec-intake/SKILL.md",
    ".goose/skills/gtkb-spec-intake/SKILL.md",
    ".harness-baseline-configuration/hooks/destructive-gate.py",
    ".harness-baseline-configuration/rules/operating-model.md",
)


def test_generated_and_scaffold_artifacts_resolve_to_lf() -> None:
    result = subprocess.run(
        ["git", "check-attr", "text", "eol", "--", *LF_POLICY_PATHS],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    attrs: dict[tuple[str, str], str] = {}
    for line in result.stdout.splitlines():
        path, attr, value = line.split(": ", 2)
        attrs[(path.replace("\\", "/"), attr)] = value

    for path in LF_POLICY_PATHS:
        assert attrs[(path, "text")] == "set"
        assert attrs[(path, "eol")] == "lf"
