"""Shared helper of the OpenRouter harness tests (owner ruling D23: no test module imports another test module).

Moved verbatim from ``test_openrouter_harness.py`` (``make_root``) so that ``test_openrouter_harness_gtkb_key.py``
shares it without importing a test module. Not collected; defines no test.
"""

from __future__ import annotations

from pathlib import Path

from scripts import openrouter_harness as orh


def make_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("Shared root instructions.\n", encoding="utf-8")
    (root / orh.ROUTING_CONFIG_PATH.parent).mkdir(parents=True)
    (root / orh.NATIVE_HOOK_SETTINGS_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / orh.ROUTING_CONFIG_PATH.parent / "hooks").mkdir(parents=True)
    (root / orh.NATIVE_HOOK_SETTINGS_PATH).write_text('{"hooks": {}}', encoding="utf-8")
    (root / "scripts").mkdir()
    for guard in {*orh.BRIDGE_WRITE_GUARDS, *orh.BRIDGE_EDIT_GUARDS, *orh.WRITE_EDIT_GUARDS, *orh.BASH_GUARDS}:
        path = root / guard
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("print('{}')\n", encoding="utf-8")
    (root / orh.ROUTING_CONFIG_PATH).write_text(
        """
schema_version = 1

[models.fixture-full]
model_id = "deepseek/fixture-model"
provider = "openrouter"
tool_calling_supported = true
allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]

[routing.openrouter]
default_model = "fixture-full"
timeout_seconds = 900
session_timeout_seconds = 3600
max_turns = 600
""".strip()
        + "\n",
        encoding="utf-8",
    )
    for name in ("gtkb-bridge", "gtkb-proposal-review", "gtkb-verify"):
        relative = Path(".agents") / "skills" / name / "SKILL.md"
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((Path(__file__).resolve().parents[2] / relative).read_bytes())
    return root
