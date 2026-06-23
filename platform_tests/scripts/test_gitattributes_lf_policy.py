from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

LF_POLICY_PATHS = (
    ".gitattributes",
    ".codex/skills/bridge-propose/SKILL.md",
    ".codex/skills/bridge-propose/helpers/write_bridge.py",
    ".codex/skills/MANIFEST.json",
    ".claude/skills/bridge-propose/SKILL.md",
    ".agent/skills/verify/SKILL.md",
    ".api-harness/skills/verify/SKILL.md",
    "config/agent-control/harness-capability-registry.toml",
    "groundtruth-kb/templates/hooks/bridge-compliance-gate.py",
    "groundtruth-kb/templates/skills/bridge-propose/SKILL.md",
    "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py",
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
