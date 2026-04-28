"""Fixture C evidence runner for bridge gtkb-da-governance-completeness-implementation-015 §7 item 9.

Builds a fresh adopter project whose .claude/settings.json has, for both
UserPromptSubmit and PostToolUse, all target managed hooks present in correct
registry relative order plus one adopter-owned entry interleaved inside the
managed block. PreToolUse and SessionStart are fully populated in scaffold
order (zero merge-event-hooks actions expected for those events).

Drives the upgrade machinery directly via the same plan_upgrade /
execute_upgrade Python API the CLI uses (and the test suite exercises). This
sidesteps Windows console-encoding quirks observed with subprocess + click,
without changing the code path under test (the CLI is a 12-line wrapper
around plan_upgrade + execute_upgrade).

Output is written to evidence/fixture_c_evidence.txt for inclusion in the
post-implementation bridge report (-017).
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from groundtruth_kb import __version__, get_templates_dir
from groundtruth_kb.project.managed_registry import artifacts_for_scaffold
from groundtruth_kb.project.upgrade import (
    _NON_MUTATING_ACTION_KINDS,
    execute_upgrade,
    plan_upgrade,
)


def _build_event_entry(filename: str) -> dict[str, object]:
    return {"hooks": [{"type": "command", "command": f"python .claude/hooks/{filename}"}]}


def _registry_filenames_by_event() -> dict[str, list[str]]:
    by_event: dict[str, list[str]] = {}
    for art in artifacts_for_scaffold("dual-agent", class_="settings-hook-registration"):
        event = getattr(art, "event", None)
        filename = getattr(art, "hook_filename", None)
        if isinstance(event, str) and isinstance(filename, str):
            by_event.setdefault(event, []).append(filename)
    return by_event


def _materialize_managed_files(target: Path) -> None:
    """Copy every scaffold-managed file (hooks, rules, skills, helpers) to the
    target. This eliminates the ~17 ``add`` actions a bare fixture would
    produce, isolating the merge-event-hooks signal in the dry-run output."""
    templates = get_templates_dir()
    for class_name in ("hook", "rule", "skill", "skill-helper"):
        for art in artifacts_for_scaffold("dual-agent", class_=class_name):
            template_path = getattr(art, "template_path", None)
            target_path = getattr(art, "target_path", None)
            if not isinstance(template_path, str) or not isinstance(target_path, str):
                continue
            src = templates / template_path
            dest = target / target_path
            if src.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def _materialize_pyproject(target: Path) -> None:
    """Create a minimal pyproject.toml so the informational pre-flight row that
    references it does not clutter the evidence; the row is informational and
    non-mutating regardless, but a real adopter would have this file."""
    (target / "pyproject.toml").write_text(
        '[project]\nname = "fixture-c-evidence"\nversion = "0.0.0"\n', encoding="utf-8"
    )


def _write_settings_with_interleaved_fixture_c(target: Path) -> None:
    by_event = _registry_filenames_by_event()
    hooks: dict[str, list[object]] = {
        "PreToolUse": [_build_event_entry(fn) for fn in by_event.get("PreToolUse", [])],
        "SessionStart": [_build_event_entry(fn) for fn in by_event.get("SessionStart", [])],
    }

    ups = by_event.get("UserPromptSubmit", [])
    ups_entries: list[object] = []
    if ups:
        ups_entries.append(_build_event_entry(ups[0]))
        if len(ups) >= 2:
            ups_entries.append(_build_event_entry(ups[1]))
        ups_entries.append(_build_event_entry("custom-ups.py"))
        ups_entries.extend(_build_event_entry(fn) for fn in ups[2:])
    hooks["UserPromptSubmit"] = ups_entries

    pto = by_event.get("PostToolUse", [])
    pto_entries: list[object] = []
    if pto:
        pto_entries.append(_build_event_entry(pto[0]))
        pto_entries.append(_build_event_entry("custom-post.py"))
        pto_entries.extend(_build_event_entry(fn) for fn in pto[1:])
    hooks["PostToolUse"] = pto_entries

    settings_dir = target / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)
    (settings_dir / "settings.json").write_text(json.dumps({"hooks": hooks}, indent=2) + "\n", encoding="utf-8")


def _write_minimal_toml(target: Path) -> None:
    (target / "groundtruth.toml").write_text(
        f'[project]\nprofile = "dual-agent"\nversion = "{__version__}"\n', encoding="utf-8"
    )


def _setup_git(target: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial fixture C state"], cwd=target, check=True)


def _format_action(action: object) -> str:
    a = getattr(action, "action", "?")
    f = getattr(action, "file", "?")
    r = getattr(action, "reason", "")
    e = getattr(action, "event", "")
    suffix = f" [event={e}]" if a == "merge-event-hooks" else ""
    return f"  [{a.upper()}] {f} - {r}{suffix}"


def main() -> int:
    out_lines: list[str] = []
    out_lines.append("=== Fixture C Evidence ===")
    out_lines.append("Bridge: gtkb-da-governance-completeness-implementation-015 sec.7 item 9")
    out_lines.append(f"groundtruth_kb __version__: {__version__}")

    by_event = _registry_filenames_by_event()
    out_lines.append("\nRegistry order by event:")
    for ev, fns in sorted(by_event.items()):
        out_lines.append(f"  {ev}:")
        for fn in fns:
            out_lines.append(f"    {fn}")

    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        _write_minimal_toml(target)
        _materialize_pyproject(target)
        _materialize_managed_files(target)
        _write_settings_with_interleaved_fixture_c(target)
        (target / ".gitignore").write_text(".claude/hooks/*.log\n", encoding="utf-8")
        _setup_git(target)

        out_lines.append("\n--- Pre-upgrade .claude/settings.json (fixture C) ---")
        out_lines.append((target / ".claude" / "settings.json").read_text(encoding="utf-8"))

        out_lines.append("\n--- plan_upgrade(target)  [== `gt project upgrade --dry-run`] ---")
        actions = plan_upgrade(target)
        merge_actions = [a for a in actions if a.action == "merge-event-hooks"]
        non_merge = [a for a in actions if a.action != "merge-event-hooks"]
        out_lines.append(f"Total actions emitted: {len(actions)}")
        out_lines.append(f"merge-event-hooks actions: {len(merge_actions)}")
        for a in merge_actions:
            out_lines.append(_format_action(a))
        if non_merge:
            out_lines.append(f"\nOther actions (not subject of this evidence): {len(non_merge)}")
            for a in non_merge:
                out_lines.append(_format_action(a))

        # Mirror CLI filter: drop pre-flight informational/warning rows before apply.
        mutating = [a for a in actions if a.action not in _NON_MUTATING_ACTION_KINDS]

        out_lines.append("\n--- execute_upgrade(target, mutating)  [== `gt project upgrade --apply`] ---")
        results = execute_upgrade(target, mutating, force=False)
        merged_lines = [r for r in results if "MERGED" in r]
        out_lines.append(f"Total result lines: {len(results)}")
        out_lines.append(f"MERGED lines: {len(merged_lines)}")
        for r in merged_lines:
            out_lines.append(f"  {r}")
        non_merge_results = [r for r in results if "MERGED" not in r]
        if non_merge_results:
            out_lines.append(f"\nOther result lines: {len(non_merge_results)}")
            for r in non_merge_results:
                out_lines.append(f"  {r}")

        out_lines.append("\n--- Post-upgrade .claude/settings.json ---")
        out_lines.append((target / ".claude" / "settings.json").read_text(encoding="utf-8"))

        out_lines.append("\n--- plan_upgrade(target)  [second pass - idempotence proof] ---")
        second_actions = plan_upgrade(target)
        second_merge = [a for a in second_actions if a.action == "merge-event-hooks"]
        out_lines.append(f"Total second-pass actions: {len(second_actions)}")
        out_lines.append(f"second-pass merge-event-hooks actions: {len(second_merge)}")
        if second_merge:
            for a in second_merge:
                out_lines.append(_format_action(a))
        second_non_merge = [a for a in second_actions if a.action != "merge-event-hooks"]
        if second_non_merge:
            out_lines.append(f"\nOther second-pass actions (non-merge): {len(second_non_merge)}")
            for a in second_non_merge:
                out_lines.append(_format_action(a))

        # Final structural assertions on the post-apply file.
        post = json.loads((target / ".claude" / "settings.json").read_text(encoding="utf-8"))
        ups_post = [h["command"] for entry in post["hooks"]["UserPromptSubmit"] for h in entry["hooks"]]
        pto_post = [h["command"] for entry in post["hooks"]["PostToolUse"] for h in entry["hooks"]]
        pre_post = [h["command"] for entry in post["hooks"]["PreToolUse"] for h in entry["hooks"]]
        ses_post = [h["command"] for entry in post["hooks"]["SessionStart"] for h in entry["hooks"]]
        out_lines.append("\n--- Structural assertions ---")
        out_lines.append(f"UserPromptSubmit final order ({len(ups_post)} entries):")
        for cmd in ups_post:
            out_lines.append(f"    {cmd}")
        out_lines.append(f"PostToolUse final order ({len(pto_post)} entries):")
        for cmd in pto_post:
            out_lines.append(f"    {cmd}")
        out_lines.append(f"PreToolUse final order ({len(pre_post)} entries) - must be unchanged:")
        for cmd in pre_post:
            out_lines.append(f"    {cmd}")
        out_lines.append(f"SessionStart final order ({len(ses_post)} entries) - must be unchanged:")
        for cmd in ses_post:
            out_lines.append(f"    {cmd}")

    evidence_dir = Path(__file__).parent.parent / "evidence"
    evidence_dir.mkdir(exist_ok=True)
    out_path = evidence_dir / "fixture_c_evidence.txt"
    out_path.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"Wrote evidence to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
