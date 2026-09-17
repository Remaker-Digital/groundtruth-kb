"""Read-only conformance against the canonical baseline and projector.

This checks derivation and installed output. Actual hook invocation and workflow
readiness need separate executed qualification; no role or waiver registry is used.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shlex
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE = ".harness-baseline-configuration"
ENGINE = "scripts/harness_projection/project_harness.py"


def _load_projector(root: Path):
    """Load the exact selected source; a cached module alias grants nothing."""
    path = root / ENGINE
    if path.resolve() != path or not path.is_file():
        raise ValueError(f"Missing or redirected projector source: {path}")
    spec = importlib.util.spec_from_file_location("_gtkb_parity_projector", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load projector: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses needs the freshly loaded module
    spec.loader.exec_module(module)
    return module


def _relative(value: Any) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError(f"Invalid repository-relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) == ".":
        raise ValueError(f"Invalid repository-relative path: {value!r}")
    return path


def _commands(value: Any):
    if isinstance(value, dict):
        if isinstance(value.get("command"), str):
            yield value["command"]
        for child in value.values():
            yield from _commands(child)
    elif isinstance(value, list):
        for child in value:
            yield from _commands(child)


def _references_script(command: str, rel: str, project_dir_var: str) -> bool:
    """Match a complete path argument, never a basename or a substring."""
    arguments = [part.strip("\"'").replace("\\", "/") for part in shlex.split(command, posix=False)]
    return any(part in {rel, f"${project_dir_var}/{rel}"} for part in arguments)


def _registration_events(profile: dict, registration: dict) -> dict:
    """Read the selected native registration shape without event aliases."""
    if profile.get("hooks_projection") == "antigravity_hooks_json":
        return registration.get("gtkb", {})
    return registration.get("hooks", {})


def _issue(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _installed_issues(root: Path, config_dir: str, plan) -> list[dict[str, str]]:
    issues = []
    for rel, content in plan.writes.items():
        path = root / rel
        if path.resolve() != path:
            issues.append(_issue("redirected_output", rel, "The output path is redirected"))
        elif not path.is_file():
            issues.append(_issue("missing_output", rel, "Regenerate this target from the canonical baseline"))
        elif path.read_bytes() != content.encode("utf-8", errors="surrogateescape"):
            issues.append(_issue("changed_output", rel, "Installed output differs from the current derivation"))
    for rel in plan.removes:
        path = root / rel
        if path.exists() or path.is_symlink():
            issues.append(_issue("retired_output", rel, "The projector identified stale generated output"))
    for parent, dirs, files in os.walk(root / config_dir, followlinks=False):
        for name in list(dirs):
            path = Path(parent) / name
            if path.resolve() != path:
                dirs.remove(name)
                issues.append(_issue("redirected_output", path.relative_to(root).as_posix(), "Redirected directory"))
        for name in files:
            rel = (Path(parent) / name).relative_to(root).as_posix()
            if rel not in plan.writes and not any(PurePosixPath(rel).is_relative_to(p) for p in plan.removes):
                issues.append(_issue("unmanaged_output", rel, "Unmanaged bytes require classification; preserve them"))
    return issues


def _check_target(root: Path, engine, profiles: dict, harness: str, installed: bool) -> dict[str, Any]:
    issues = []
    result = {"status": "fail", "files": 0, "skills": 0, "issues": issues}
    try:
        profile = profiles["harnesses"][harness]
        if profile.get("status") == "profile_pending":
            raise ValueError("The declared target has no implemented renderer")
        config_dir = _relative(profile["config_dir"])
        if (root / str(config_dir)).resolve() != root / str(config_dir):
            raise ValueError("The selected configuration root is redirected")
        for other_name, other in profiles["harnesses"].items():
            if other_name == harness:
                continue
            other_root = _relative(other["config_dir"])
            if config_dir.is_relative_to(other_root) or other_root.is_relative_to(config_dir):
                raise ValueError(f"Configuration roots overlap: {harness}, {other_name}")
        for key in ("skills_dir", "rules_dir", "hooks_dir", "hooks_json_path"):
            if profile.get(key) and not _relative(profile[key]).is_relative_to(config_dir):
                raise ValueError(f"{key} escapes this target's configuration root")
        plan = engine.build_plan(harness)
        issues.extend(_issue("projector_gap", ENGINE, gap) for gap in plan.gaps)
        for rel in plan.writes:
            if not _relative(rel).is_relative_to(config_dir):
                raise ValueError(f"Planned effect escapes the selected target: {rel}")
        exact_retired = {_relative(rel) for rel in profile.get("leftover_paths", [])}
        active_roots = [_relative(row["config_dir"]) for row in profiles["harnesses"].values()]
        for rel in plan.removes:
            path = _relative(rel)
            if path.is_relative_to(config_dir):
                continue
            # A moved target may retire its explicitly classified former files.
            # This does not permit writes outside its root, directory sweeps,
            # or removal in/above any currently registered target.
            if path not in exact_retired or any(
                path.is_relative_to(active) or active.is_relative_to(path) for active in active_roots
            ):
                raise ValueError(f"Planned removal escapes the selected target: {rel}")
            if (root / rel).is_dir():
                raise ValueError(f"Exact retired output is a directory: {rel}")
        result["files"] = len(plan.writes)

        base = root / BASELINE
        skill_root = base / "skills"
        expected_skills = {}
        for path in sorted(skill_root.rglob("SKILL.md")):
            if engine.is_projection_junk(path, skill_root):
                continue
            rel = path.relative_to(skill_root).as_posix()
            fields = engine.skill_fields(path.read_text(encoding="utf-8"))
            if fields["name"] != path.parent.name:
                issues.append(_issue("skill_identity", rel, "Skill name differs from its directory"))
            expected_skills[rel] = fields["name"]
        if not expected_skills:
            issues.append(_issue("empty_baseline", BASELINE, "No canonical skills were found"))
        destination = str(_relative(profile["skills_dir"])) + "/"
        observed = {
            rel[len(destination) :]: text
            for rel, text in plan.writes.items()
            if rel.startswith(destination) and rel.endswith("/SKILL.md")
        }
        for rel in sorted(set(expected_skills) - set(observed)):
            issues.append(_issue("missing_skill", rel, "The projector omitted a canonical skill"))
        for rel in sorted(set(observed) - set(expected_skills)):
            issues.append(_issue("extra_skill", rel, "Projected skill is absent from the canonical baseline"))
        for rel in set(expected_skills) & set(observed):
            if engine.skill_fields(observed[rel])["name"] != expected_skills[rel]:
                issues.append(_issue("skill_identity", rel, "Projected identity differs from the canonical skill"))
        result["skills"] = len(observed)

        for rel, text in plan.writes.items():
            if rel.endswith(".json"):
                json.loads(text)
            elif rel.endswith(".toml"):
                tomllib.loads(text)
            elif rel.endswith(".py"):
                compile(text, rel, "exec")
        manifest = tomllib.loads((base / profiles["baseline"]["hook_manifest"]).read_text(encoding="utf-8"))
        registration_path = profile.get("hooks_json_path")
        registration = json.loads(plan.writes[registration_path]) if registration_path in plan.writes else {}
        for hook in manifest.get("hook", []):
            script = str(_relative(hook["script"]))
            shared = hook.get("script_root") == "project_scripts"
            rel = f"scripts/{script}" if shared else f"{profile['hooks_dir']}/{script}"
            source = root / rel if shared else base / "hooks" / script
            if not source.is_file() or source.resolve() != source:
                issues.append(_issue("missing_hook_source", rel, "Declared hook source is missing or redirected"))
            if not shared and rel not in plan.writes:
                issues.append(_issue("missing_hook_output", rel, "The projector omitted a declared hook"))
            events = profile.get("hook_events", {}).get(hook["event"], [])
            events = [events] if isinstance(events, str) else events
            if not events:
                issues.append(_issue("missing_hook_event", rel, "No declared native event for this hook"))
            for event in events:
                commands = _commands(_registration_events(profile, registration).get(event, []))
                if not any(_references_script(command, rel, profile["project_dir_var"]) for command in commands):
                    issues.append(_issue("missing_hook_registration", rel, f"No exact hook path argument at {event}"))
        if installed:
            issues.extend(_installed_issues(root, str(config_dir), plan))
    except (KeyError, OSError, ValueError, SyntaxError, RuntimeError) as error:
        issues.append(_issue("invalid_projection", harness, str(error)))
    result["status"] = "fail" if issues else "pass"
    return result


def check_harness_parity(project_root: Path = PROJECT_ROOT, *, harness: str, installed: bool = True) -> dict[str, Any]:
    """Check explicitly selected targets; never infer a role or target from state."""
    root = project_root.resolve()
    report: dict[str, Any] = {
        "status": "fail",
        "mode": "installed" if installed else "derivation",
        "operational_readiness": "not_evaluated",
        "harnesses": {},
        "issues": [],
        "sources": {"baseline": BASELINE, "projector": ENGINE},
    }
    try:
        engine = _load_projector(root)
        profiles = engine.load_profiles()
        if profiles["baseline"]["root"] != BASELINE or (root / BASELINE).resolve() != root / BASELINE:
            raise ValueError("Use the canonical baseline without path redirection")
        names = sorted(profiles["harnesses"]) if harness == "all" else [harness]
        if not names or any(name not in profiles["harnesses"] for name in names):
            raise ValueError(f"Unknown or empty declared target selection: {harness}")
        for name in names:
            report["harnesses"][name] = _check_target(root, engine, profiles, name, installed)
    except (KeyError, OSError, ValueError, ImportError, SyntaxError, RuntimeError) as error:
        report["issues"].append(_issue("unavailable_projector", ENGINE, str(error)))
    if (
        report["harnesses"]
        and not report["issues"]
        and all(target["status"] == "pass" for target in report["harnesses"].values())
    ):
        report["status"] = "pass"
    return report


def format_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Harness Projection Conformance",
        "",
        f"Status: {report['status']} ({report['mode']})",
        "Actual hook invocation and workflow readiness: not evaluated.",
        "",
    ]
    for name, target in report["harnesses"].items():
        lines.append(f"- {name}: {target['status']}; {target['files']} files, {target['skills']} skills")
        lines.extend(f"  - {i['code']}: {i['path']}: {i['message']}" for i in target["issues"])
    lines.extend(f"- {i['code']}: {i['message']}" for i in report["issues"])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--harness")
    selection.add_argument(
        "--all", action="store_true", help="Check every declared target, including unimplemented ones."
    )
    parser.add_argument("--validate", action="store_true", help="Check derivation without requiring installed output.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args(argv)
    report = check_harness_parity(
        args.project_root, harness="all" if args.all else args.harness, installed=not args.validate
    )
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else format_markdown(report), end="\n")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
