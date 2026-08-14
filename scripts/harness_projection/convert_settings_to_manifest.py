"""Convert the baseline's inherited hook registration file to a neutral manifest.

Phase A structural conversion (STRUCTURAL_CONVERT class) under
bridge/gtkb-baseline-correction-and-goose-projector-slice-1 (GO at -004).
Reads the baseline's `settings.json` (a single harness's registration schema)
and emits `hooks/manifest.toml`, the harness-neutral registration surface the
projector renders into each harness's native form.

Neutralization mapping:

- Event names become neutral lifecycle events:
  PreToolUse -> pre_tool_use, PostToolUse -> post_tool_use,
  UserPromptSubmit -> prompt_submit, SessionStart -> session_start,
  Stop -> turn_end.
- Matcher strings become intent tokens the projector maps to each harness's
  tool vocabulary: file-write tools -> "file_write", shell tools ->
  "shell_exec", read tools -> "read_access", empty matcher -> "all".
- Command strings keep only the hook script's basename; the projector renders
  the interpreter, path prefix, and env-var syntax natively per harness.

The source `settings.json` and workstation-specific `settings.local.json` are
removed from the baseline after conversion (C1/C2 of the lens-reconciliation
decisions): the manifest is the baseline artifact, per-harness registration
files are projector outputs.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE = PROJECT_ROOT / ".harness-baseline-configuration"

EVENT_MAP = {
    "PreToolUse": "pre_tool_use",
    "PostToolUse": "post_tool_use",
    "UserPromptSubmit": "prompt_submit",
    "SessionStart": "session_start",
    "Stop": "turn_end",
}

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit", "Delete", "Move", "Copy"}
SHELL_TOOLS = {"Bash", "PowerShell"}
READ_TOOLS = {"Read", "Grep", "Glob"}


def matcher_to_intents(matcher: str) -> list[str]:
    if not matcher:
        return ["all"]
    tools = set(matcher.split("|"))
    intents: list[str] = []
    if tools & WRITE_TOOLS:
        intents.append("file_write")
    if tools & SHELL_TOOLS:
        intents.append("shell_exec")
    if tools & READ_TOOLS:
        intents.append("read_access")
    unmapped = tools - WRITE_TOOLS - SHELL_TOOLS - READ_TOOLS
    for tool in sorted(unmapped):
        intents.append(f"tool:{tool}")
    return intents or ["all"]


def script_basename(command: str) -> str | None:
    match = re.search(r"hooks[/\\]([\w.-]+\.py)", command)
    return match.group(1) if match else None


def main() -> int:
    settings_path = BASELINE / "settings.json"
    if not settings_path.is_file():
        print("settings.json already converted/removed", file=sys.stderr)
        return 0
    settings = json.loads(settings_path.read_text(encoding="utf-8-sig"))
    lines: list[str] = [
        "# Neutral hook-registration manifest - GT-KB harness baseline",
        "#",
        "# Rendered by the harness projector into each harness's native",
        "# registration form (per-harness event names, matcher vocabulary,",
        "# interpreter and path syntax). Scripts live in the baseline hooks/",
        "# directory and are projected alongside this manifest.",
        "#",
        "# schema: [[hook]] event = neutral lifecycle event; intents = neutral",
        "# tool-intent tokens; script = hook script basename under hooks/;",
        "# blocking = whether the harness must honor a deny result;",
        "# timeout_seconds = advisory execution bound.",
        "",
        "schema_version = 1",
        "",
    ]
    count = 0
    unmapped: list[str] = []
    for event, groups in (settings.get("hooks") or {}).items():
        neutral_event = EVENT_MAP.get(event)
        if neutral_event is None:
            unmapped.append(event)
            continue
        for group in groups:
            intents = matcher_to_intents(str(group.get("matcher") or ""))
            for hook in group.get("hooks") or []:
                script = script_basename(str(hook.get("command") or ""))
                if script is None:
                    unmapped.append(f"{event}: {str(hook.get('command'))[:80]}")
                    continue
                lines.append("[[hook]]")
                lines.append(f'event = "{neutral_event}"')
                lines.append(f"intents = {json.dumps(intents)}")
                lines.append(f'script = "{script}"')
                lines.append(f"blocking = {str(neutral_event in {'pre_tool_use', 'turn_end'}).lower()}")
                timeout = hook.get("timeout")
                if timeout:
                    lines.append(f"timeout_seconds = {int(timeout)}")
                lines.append("")
                count += 1
    manifest_path = BASELINE / "hooks" / "manifest.toml"
    manifest_path.write_text("\n".join(lines), encoding="utf-8")
    settings_path.unlink()
    local = BASELINE / "settings.local.json"
    local_removed = False
    if local.is_file():
        local.unlink()
        local_removed = True
    print(
        json.dumps(
            {
                "manifest": str(manifest_path.relative_to(PROJECT_ROOT)),
                "hooks_converted": count,
                "unmapped": unmapped,
                "settings_json_removed": True,
                "settings_local_removed": local_removed,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
