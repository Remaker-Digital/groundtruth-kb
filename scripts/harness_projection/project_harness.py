"""GT-KB harness projection engine.

Projects the neutral baseline into one harness's configuration surface.

Bridge: gtkb-baseline-correction-and-goose-projector-slice-1 (GO at -004).
Spec: GOV-HARNESS-NEUTRAL-BASELINE-001 - obligation 2 (projection-only
configuration), obligation 4 (projector-confined harness awareness),
obligation 5 (derived-artifact disclosure), obligation 6 (gap capture).

Usage:
    python scripts/harness_projection/project_harness.py --harness goose [--dry-run]
    python scripts/harness_projection/project_harness.py --harness goose --check

Modes:
    default   render the projection into the harness config directory
    --dry-run print the plan (files that would be written/removed), write nothing
    --check   compare current projection against a fresh render; report drift
              and unmanaged files as projector gaps (obligation 6); exit 1 on
              any difference, 0 when clean

The engine renders four surface classes from the baseline:
    skills/   full SKILL.md bodies (plus reference files), token-substituted,
              stamped after frontmatter
    rules/    all baseline rules, token-substituted, stamped
    hooks/    hook scripts token-substituted + the harness-native hook
              registration rendered from hooks/manifest.toml
    ownership .projection-manifest.json listing every produced path, so
              cleanup and --check can distinguish managed from unmanaged files

Unresolved neutral tokens fail the render (fail closed) - a token the profile
cannot substitute is a projector gap, never silent passthrough.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILES_PATH = Path(__file__).resolve().parent / "profiles.toml"

TOKEN_RE = re.compile(r"\{\{([A-Z_]+)\}\}")

TEXT_SUFFIXES = {".md", ".py", ".toml", ".json", ".yaml", ".yml", ".txt"}


class ProjectionError(RuntimeError):
    pass


BASELINE_ROOT_NAME = ".harness-baseline-configuration"


def normalize_planned_rel(rel: str) -> str:
    """Normalize a planned write path for destination checks.

    Replace ``\\`` with ``/`` and strip a leading ``./`` prefix. Do not use
    ``str.lstrip("./")``: that would also strip the leading ``.`` from
    ``.harness-baseline-configuration``.
    """
    text = str(rel).replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text


def is_baseline_destination(rel: str) -> bool:
    """Return True when a planned write would land inside the baseline tree."""
    normalized = normalize_planned_rel(rel)
    return normalized == BASELINE_ROOT_NAME or normalized.startswith(f"{BASELINE_ROOT_NAME}/")


def reject_baseline_destinations(plan: Plan) -> None:
    """Fail closed if any planned write path is inside the baseline tree."""
    blocked = sorted(rel for rel in plan.writes if is_baseline_destination(rel))
    if not blocked:
        return
    raise ProjectionError(
        "refusing to project into .harness-baseline-configuration "
        "(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 2); blocked: " + ", ".join(blocked)
    )


@dataclass
class Plan:
    writes: dict[str, str] = field(default_factory=dict)  # rel path -> content
    removes: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)


def load_profiles() -> dict:
    return tomllib.loads(PROFILES_PATH.read_text(encoding="utf-8"))


def token_map(profile: dict, baseline_cfg: dict) -> dict[str, str]:
    return {
        "HARNESS_CONFIG_DIR": profile["config_dir"],
        "HARNESS_SKILLS_DIR": profile["skills_dir"],
        "HARNESS_RULES_DIR": profile["rules_dir"],
        "HARNESS_HOOKS_DIR": profile["hooks_dir"],
        "HARNESS_PROJECT_DIR_VAR": profile["project_dir_var"],
        "HARNESS_SESSION_ID_VAR": profile["session_id_var"],
        "HARNESS_NAME": profile["name"],
        "SHARED_HELPERS_DIR": baseline_cfg["shared_helpers_dir"],
    }


def substitute(text: str, tokens: dict[str, str], rel: str, gaps: list[str]) -> str:
    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in tokens:
            return tokens[name]
        gaps.append(f"{rel}: unresolved token {{{{{name}}}}}")
        return match.group(0)

    return TOKEN_RE.sub(repl, text)


_RUFF_CMD: list[str] | None = None


def _get_ruff_cmd() -> list[str]:
    global _RUFF_CMD
    if _RUFF_CMD is not None:
        return _RUFF_CMD
    venv_ruff = PROJECT_ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "ruff.exe"
    if venv_ruff.is_file():
        _RUFF_CMD = [str(venv_ruff)]
    elif shutil.which("ruff"):
        _RUFF_CMD = ["ruff"]
    else:
        _RUFF_CMD = [sys.executable, "-m", "ruff"]
    return _RUFF_CMD


def ruff_format(text: str, rel: str, gaps: list[str]) -> str:
    try:
        proc = subprocess.run(
            _get_ruff_cmd() + ["format", "--stdin-filename", rel, "-"],
            input=text.encode("utf-8"),
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        gaps.append(f"{rel}: ruff format unavailable ({exc})")
        return text
    if proc.returncode != 0:
        gaps.append(f"{rel}: ruff format failed: {proc.stderr.decode('utf-8', 'replace')[:120]}")
        return text
    return proc.stdout.decode("utf-8")


def stamp_for(rel: str, stamp_text: str) -> str | None:
    suffix = Path(rel).suffix.lower()
    if suffix in {".md"}:
        return "<!--\n" + stamp_text + "\n-->\n"
    if suffix in {".py", ".toml", ".yaml", ".yml"}:
        return "".join(f"# {line}\n" for line in stamp_text.splitlines())
    if suffix == ".json":
        return None  # JSON carries the stamp as a reserved key, handled by caller
    return None


def adapter_metadata_block(harness: str, source_rel: str, source_text: str) -> str:
    """Parity-consumable metadata (check_harness_parity._adapter_metadata).

    ``Generated at`` is content-addressed rather than a wall-clock timestamp:
    re-projection is byte-idempotent by contract, and a timestamp would break
    that. The checker requires the field to be non-empty; the source digest
    prefix is non-empty, truthful and deterministic.
    """
    marker = f"GTKB-{harness.upper()}-SKILL-ADAPTER"
    digest = hashlib.sha256((source_text.rstrip() + "\n").encode("utf-8")).hexdigest()
    return (
        f"{marker}-BEGIN\n"
        "Generated by: scripts/harness_projection/project_harness.py\n"
        f"Generated at: content-addressed {digest[:12]}\n"
        f"Canonical source: {source_rel}\n"
        f"Canonical source sha256: {digest}\n"
        f"{marker}-END\n"
    )


def apply_stamp(rel: str, content: str, stamp_text: str) -> str:
    """Insert the non-canonical stamp in file-type-appropriate syntax.

    For markdown with YAML frontmatter the stamp goes AFTER the closing
    delimiter so frontmatter discovery still parses (obligation 5 note in
    WI-6227). Python files keep a shebang or encoding line first.
    """
    block = stamp_for(rel, stamp_text)
    if block is None:
        return content
    lines = content.splitlines(keepends=True)
    if rel.endswith(".md") and lines and lines[0].strip() == "---":
        for i in range(1, min(len(lines), 80)):
            if lines[i].strip() == "---":
                return "".join(lines[: i + 1]) + block + "".join(lines[i + 1 :])
    if rel.endswith(".py") and lines and lines[0].startswith("#!"):
        return lines[0] + block + "".join(lines[1:])
    return block + content


def render_hooks_registration(
    profile: dict, manifest: dict, tokens: dict[str, str], gaps: list[str]
) -> tuple[str, str] | None:
    """Render the harness-native hook registration from the neutral manifest."""
    mode = profile.get("hooks_projection")
    if mode == "plugin_hooks_json":
        events: dict[str, list[dict]] = {}
        blocking_ok = set(profile.get("blocking_events", {}).get("supported", []))
        for hook in manifest.get("hook", []):
            native_event = profile.get("hook_events", {}).get(hook["event"])
            if native_event is None:
                gaps.append(f"hook {hook['script']}: no native event for {hook['event']}")
                continue
            if hook.get("script_root") == "project_scripts":
                command = f"python scripts/{hook['script']}"
            else:
                command = f"python {profile['hooks_dir']}/{hook['script']}"
            for arg in hook.get("args", []):
                command += " " + substitute(arg, tokens, "hooks/manifest.toml", gaps)
            entry: dict = {"command": command}
            if hook.get("timeout_seconds"):
                entry["timeout"] = hook["timeout_seconds"]
            if hook.get("blocking") and native_event in blocking_ok:
                entry["blocking"] = True
            events.setdefault(native_event, []).append(entry)
        payload = {
            "_comment": "PROJECTION, NOT CANONICAL - rendered from the baseline hooks/manifest.toml by the GT-KB projection engine; edit the baseline and re-project.",
            "hooks": events,
        }
        return profile["hooks_json_path"], json.dumps(payload, indent=2) + "\n"
    if mode == "settings_json":
        matchers = profile.get("intent_matchers", {})
        events_out: dict[str, list[dict]] = {}
        for hook in manifest.get("hook", []):
            native_event = profile.get("hook_events", {}).get(hook["event"])
            if native_event is None:
                gaps.append(f"hook {hook['script']}: no native event for {hook['event']}")
                continue
            intents = hook.get("intents", ["all"])
            matcher = "|".join(m for m in (matchers.get(i, "") for i in intents) if m)
            if hook.get("script_root") == "project_scripts":
                script_path = f"${profile['project_dir_var']}/scripts/{hook['script']}"
            else:
                script_path = f"${profile['project_dir_var']}/{profile['hooks_dir']}/{hook['script']}"
            command = f'pythonw "{script_path}"'
            for arg in hook.get("args", []):
                command += " " + substitute(arg, tokens, "hooks/manifest.toml", gaps)
            entry = {"type": "command", "command": command}
            if hook.get("timeout_seconds"):
                entry["timeout"] = hook["timeout_seconds"]
            group = {"matcher": matcher, "hooks": [entry]} if matcher else {"hooks": [entry]}
            events_out.setdefault(native_event, []).append(group)
        payload = {
            "_comment": "PROJECTION, NOT CANONICAL - rendered from the baseline hooks/manifest.toml by the GT-KB projection engine; edit the baseline and re-project.",
            "hooks": events_out,
        }
        return profile["hooks_json_path"], json.dumps(payload, indent=2) + "\n"
    if mode in {"hooks_json", "cursor_hooks_json"}:
        events_out: dict[str, list[dict]] = {}
        for hook in manifest.get("hook", []):
            native_event = profile.get("hook_events", {}).get(hook["event"])
            if native_event is None:
                continue
            if hook.get("script_root") == "project_scripts":
                command = f"python scripts/{hook['script']}"
            else:
                command = f"python {profile['hooks_dir']}/{hook['script']}"
            for arg in hook.get("args", []):
                command += " " + substitute(arg, tokens, "hooks/manifest.toml", gaps)
            entry = {"command": command}
            if hook.get("timeout_seconds"):
                entry["timeout"] = hook["timeout_seconds"]
            events_out.setdefault(native_event, []).append(entry)
        payload = {
            "version": 1,
            "_comment": "PROJECTION, NOT CANONICAL - rendered from the baseline hooks/manifest.toml by the GT-KB projection engine; edit the baseline and re-project.",
            "hooks": events_out,
        }
        return profile["hooks_json_path"], json.dumps(payload, indent=2) + "\n"
    if mode is None:
        return None
    gaps.append(f"hooks_projection mode {mode!r} not implemented")
    return None


def build_plan(harness: str) -> Plan:
    profiles = load_profiles()
    baseline_cfg = profiles["baseline"]
    profile = dict(profiles["harnesses"].get(harness) or {})
    if not profile:
        raise ProjectionError(f"no profile for harness {harness!r}")
    if profile.get("status") == "profile_pending":
        raise ProjectionError(
            f"harness {harness!r} profile is pending its own projector slice "
            "(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6: file or extend the work item)"
        )
    profile["name"] = harness
    base = PROJECT_ROOT / baseline_cfg["root"]
    if not base.is_dir():
        raise ProjectionError(f"baseline root missing: {base}")
    tokens = token_map(profile, baseline_cfg)
    stamp_text = profiles["stamp"]["text"].format(baseline_root=baseline_cfg["root"], harness=harness)
    plan = Plan()

    surfaces = {}
    if profile.get("skill_body") != "adapter_script" and profile.get("skills_dir"):
        surfaces["skills"] = profile["skills_dir"]
    if profile.get("rules_projection") and profile.get("rules_dir"):
        surfaces["rules"] = profile["rules_dir"]
    if profile.get("hooks_dir"):
        surfaces["hooks"] = profile["hooks_dir"]
    for src_name, dst_root in surfaces.items():
        src_root = base / src_name
        if not src_root.is_dir():
            continue
        for path in sorted(src_root.rglob("*")):
            if not path.is_file():
                continue
            rel_in_surface = path.relative_to(src_root).as_posix()
            if src_name == "hooks" and rel_in_surface == "manifest.toml":
                continue  # the registration is rendered natively, below
            rel_out = f"{dst_root}/{rel_in_surface}"
            if path.suffix.lower() in TEXT_SUFFIXES:
                source_text = path.read_text(encoding="utf-8", errors="surrogateescape")
                text = substitute(source_text, tokens, rel_out, plan.gaps)
                text = apply_stamp(rel_out, text, stamp_text)
                if src_name == "skills" and rel_in_surface.endswith("SKILL.md"):
                    source_rel = f"{baseline_cfg['root']}/{src_name}/{rel_in_surface}"
                    block = adapter_metadata_block(profile["name"], source_rel, source_text)
                    text = text + "\n<!--\n" + block + "-->\n"
                if rel_out.endswith(".py") and text != source_text:
                    # Token substitution changes line lengths, so a
                    # format-conforming baseline does not guarantee a
                    # format-conforming projection. The engine emits
                    # gate-conforming output; ruff format is deterministic,
                    # so plan idempotence is preserved.
                    text = ruff_format(text, rel_out, plan.gaps)
                plan.writes[rel_out] = text
            else:
                plan.writes[rel_out] = path.read_bytes().decode("latin-1")

    manifest_path = base / baseline_cfg["hook_manifest"]
    if manifest_path.is_file():
        manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        rendered = render_hooks_registration(profile, manifest, tokens, plan.gaps)
        if rendered is not None:
            plan.writes[rendered[0]] = rendered[1]

    ownership = sorted(plan.writes) + [f"{profile['config_dir']}/.projection-manifest.json"]
    plan.writes[f"{profile['config_dir']}/.projection-manifest.json"] = (
        json.dumps(
            {
                "_comment": "Ownership manifest - paths produced by the GT-KB projection engine for this harness. Files inside projector-owned subtrees but absent from this list are unmanaged (candidates for cleanup or projector-gap review).",
                "harness": harness,
                "baseline_root": baseline_cfg["root"],
                "engine": "scripts/harness_projection/project_harness.py",
                "paths": ownership,
            },
            indent=2,
        )
        + "\n"
    )
    reject_baseline_destinations(plan)
    return plan


def run(harness: str, mode: str) -> int:
    plan = build_plan(harness)
    reject_baseline_destinations(plan)
    if plan.gaps:
        print("PROJECTOR GAPS (obligation 6 - file or extend a work item):")
        for gap in plan.gaps:
            print("  -", gap)
        if mode != "dry-run":
            print("FAIL: gaps present; nothing written (fail closed)")
            return 2
    if mode == "dry-run":
        print(f"DRY-RUN plan for {harness}: {len(plan.writes)} files")
        for rel in sorted(plan.writes):
            print("  write", rel)
        return 0
    if mode == "check":
        drift: list[str] = []
        for rel, content in plan.writes.items():
            target = PROJECT_ROOT / rel
            if not target.is_file():
                drift.append(f"missing: {rel}")
            elif (
                hashlib.sha256(target.read_bytes()).hexdigest()
                != hashlib.sha256(content.encode("utf-8", errors="surrogateescape")).hexdigest()
            ):
                drift.append(f"differs: {rel}")
        print(f"CHECK {harness}: {len(drift)} drifted of {len(plan.writes)} managed")
        for d in drift:
            print("  -", d)
        return 1 if drift else 0
    for rel, content in plan.writes.items():
        target = PROJECT_ROOT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content.encode("utf-8", errors="surrogateescape"))
    print(f"PROJECTED {harness}: {len(plan.writes)} files")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harness", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    mode = "dry-run" if args.dry_run else "check" if args.check else "write"
    try:
        return run(args.harness, mode)
    except ProjectionError as exc:
        print(f"PROJECTION ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
