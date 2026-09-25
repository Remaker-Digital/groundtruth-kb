"""Read-only conformance against the canonical baseline and projector.

This checks derivation and installed output. Actual hook invocation and workflow
readiness need separate executed qualification; no role or waiver registry is used.

Owner ruling D15 as amended by R3 (D34, 2026-09-19, M15 rulings R1-R15): a
projection is the minimum a host's limitation requires - registrations and
pointers, never copies. Every planned write is classified through the projector's
own ``classify_write`` so the two never diverge: REGISTRATION (the native hook
registration and the declared native config.toml), OWNERSHIP (the
``<config_dir>/.projection-manifest.json`` bookkeeping file, the R15 (a)
exemption) or POINTER (a skill pointer stub or a declared ``[pointer_files]``
entry); anything else is ``unclassified_output``. Skill bodies, rules and hook
scripts are read in place from ``.agents/skills`` and
``.harness-baseline-configuration/{rules,hooks}``. The root ``AGENTS.md`` and the
``[root_pointers]`` files (R1 option B) are tracked authored sources outside the
projector's output; this checker pins their bytes (``declared_pointer_drift``) in
both modes, so the doctor conformance check and the release-candidate gate refuse
a pointer that grows back into a canon carrier.

A target owns its configuration root plus any declared ``extra_output_roots``
(owner ruling D52: Goose discovers its hook plugin only at
``.agents/plugins/<name>/``). Writes, removals, declared paths and the installed
unmanaged-output walk are confined to those owned roots; an owned root may not be
redirected, overlap another target's owned roots, or overlap ``.agents/skills``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shlex
import stat
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE = ".harness-baseline-configuration"
SKILLS_ROOT = ".agents/skills"
HOOKS_ROOT = ".harness-baseline-configuration/hooks"
INSTRUCTION_FILE = "AGENTS.md"
ENGINE = "scripts/harness_projection/project_harness.py"
# The projector surface this checker relies on; a projector without it is unavailable, not a pass.
ENGINE_SURFACE = (
    "load_profiles",
    "resolve_source_roots",
    "build_plan",
    "classify_write",
    "skill_fields",
    "frontmatter_block",
    "is_projection_junk",
)
SKILLS_DISCOVERY = frozenset({"agents_skills", "pointer_stubs"})
WRITE_CLASSES = ("registration", "ownership", "pointer")
IDENTITY_FLAG = "--harness"
TOKEN_RE = re.compile(r"\{\{[A-Z_]+\}\}")
TEXT_SUFFIXES = frozenset({".md", ".py", ".toml", ".json", ".yaml", ".yml", ".txt"})
# Source trees read in place by every host, so no neutral {{TOKEN}} may remain in
# them. Skills, rules and hooks are read in place without token substitution.
TOKEN_RESIDUE_SCOPES = (SKILLS_ROOT, HOOKS_ROOT, f"{BASELINE}/rules")


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


def _windows_commands(value: Any):
    """Windows-specific registrations (``commandWindows``), which Codex prefers on Windows."""
    if isinstance(value, dict):
        if isinstance(value.get("commandWindows"), str):
            yield value["commandWindows"]
        for child in value.values():
            yield from _windows_commands(child)
    elif isinstance(value, list):
        for child in value:
            yield from _windows_commands(child)


def _unescape_powershell(command: str) -> str:
    """Inverse of the projector's expansion-safe escape, so one contract checks both renderings."""
    return command.replace("`$", "$").replace("``", "`")


def _arguments(command: str) -> list[str]:
    """Quote-stripped, slash-normalized argument list of a registered command."""
    return [part.strip("\"'").replace("\\", "/") for part in shlex.split(command, posix=False)]


def _references_script(command: str, rel: str, project_dir_var: str) -> bool:
    """Match a complete path argument, never a basename or a substring."""
    return any(part in {rel, f"${project_dir_var}/{rel}"} for part in _arguments(command))


def _carries_identity(command: str, rel: str, project_dir_var: str, harness: str) -> bool:
    """The exact pair ``--harness <profile name>`` follows the hook path argument (R10)."""
    arguments = _arguments(command)
    targets = {rel, f"${project_dir_var}/{rel}"}
    positions = [index for index, part in enumerate(arguments) if part in targets]
    if not positions:
        return False
    return any(
        arguments[index] == IDENTITY_FLAG and arguments[index + 1] == harness
        for index in range(positions[0] + 1, len(arguments) - 1)
    )


def _registration_events(profile: dict, registration: dict) -> dict:
    """Read the selected native registration shape without event aliases."""
    if profile.get("hooks_projection") == "antigravity_hooks_json":
        return registration.get("gtkb", {})
    return registration.get("hooks", {})


def _issue(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _pointer_line(name: str) -> str:
    """The stub body line that hands the host to the one skills source (stub contract item 3)."""
    return f"Read and follow `{SKILLS_ROOT}/{name}/SKILL.md`"


def _stub_body(text: str) -> str:
    """The stub text after its closing frontmatter delimiter (skill_fields validated the block)."""
    lines = text.removeprefix("﻿").splitlines()
    return "\n".join(lines[lines.index("---", 1) + 1 :])


def _declared_file_issues(root: Path, rel: str, expected: bytes | None, declaration: str) -> list[dict[str, str]]:
    """Pin a tracked authored file: present, unredirected, regular and (when declared) byte-exact."""
    path = root / rel
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return [_issue("declared_pointer_drift", rel, f"missing; declared by {declaration}")]
    reparse = getattr(metadata, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    if stat.S_ISLNK(metadata.st_mode) or reparse or path.resolve() != path:
        return [_issue("declared_pointer_drift", rel, f"redirected; declared by {declaration}")]
    if not stat.S_ISREG(metadata.st_mode):
        return [_issue("declared_pointer_drift", rel, f"not a regular file; declared by {declaration}")]
    if expected is not None and path.read_bytes() != expected:
        return [_issue("declared_pointer_drift", rel, f"bytes differ from {declaration}")]
    return []


def _root_pointer_issues(root: Path, profiles: dict) -> list[dict[str, str]]:
    """R1 option B: each declared root pointer carries exactly its bytes; AGENTS.md is their target."""
    declared = profiles.get("root_pointers")
    if not isinstance(declared, dict) or not declared:
        raise ValueError("profiles.toml declares no [root_pointers]")
    issues = []
    for key, value in declared.items():
        rel = _relative(key)
        if len(rel.parts) != 1 or str(rel) == INSTRUCTION_FILE or not isinstance(value, str):
            raise ValueError(f"Invalid [root_pointers] declaration: {key!r}")
        issues.extend(_declared_file_issues(root, str(rel), value.encode("utf-8"), "profiles.toml [root_pointers]"))
    issues.extend(_declared_file_issues(root, INSTRUCTION_FILE, None, "the [root_pointers] target (R1 option B)"))
    return issues


def _token_residue_issues(root: Path, engine) -> list[dict[str, str]]:
    """No neutral token may remain in a source tree that hosts read in place."""
    issues = []
    for scope in TOKEN_RESIDUE_SCOPES:
        base = root / scope
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES or engine.is_projection_junk(path, base):
                continue
            rel = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8", errors="surrogateescape")
            for number, line in enumerate(text.splitlines(), 1):
                tokens = TOKEN_RE.findall(line)
                if tokens:
                    message = "Neutral token remains in a source read in place: " + ", ".join(tokens)
                    issues.append(_issue("baseline_token_residue", f"{rel}:{number}", message))
    return issues


def _owned_roots(profile: dict) -> list[PurePosixPath]:
    """The target's configuration root plus any declared extra output roots (owner ruling D52), in declaration order."""
    extra = profile.get("extra_output_roots") or []
    if not isinstance(extra, list):
        raise ValueError("extra_output_roots must be a list of repository-relative directories")
    return [_relative(profile["config_dir"]), *(_relative(value) for value in extra)]


def _installed_issues(root: Path, owned: list[PurePosixPath], plan) -> list[dict[str, str]]:
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
    for owned_root in owned:
        for parent, dirs, files in os.walk(root / str(owned_root), followlinks=False):
            for name in list(dirs):
                path = Path(parent) / name
                if path.resolve() != path:
                    dirs.remove(name)
                    issues.append(
                        _issue("redirected_output", path.relative_to(root).as_posix(), "Redirected directory")
                    )
            for name in files:
                rel = (Path(parent) / name).relative_to(root).as_posix()
                if rel not in plan.writes and not any(PurePosixPath(rel).is_relative_to(p) for p in plan.removes):
                    issues.append(
                        _issue("unmanaged_output", rel, "Unmanaged bytes require classification; preserve them")
                    )
    return issues


def _check_target(root: Path, engine, profiles: dict, harness: str, installed: bool) -> dict[str, Any]:
    issues = []
    classes = dict.fromkeys(WRITE_CLASSES, 0)
    result = {"status": "fail", "files": 0, "skills": 0, "classes": classes, "issues": issues}
    try:
        profile = profiles["harnesses"][harness]
        if profile.get("status") == "profile_pending":
            raise ValueError("The declared target has no implemented renderer")
        config_dir = _relative(profile["config_dir"])
        owned = _owned_roots(profile)
        for owned_root in owned:
            if (root / str(owned_root)).resolve() != root / str(owned_root):
                raise ValueError(f"The selected output root is redirected: {owned_root}")
            skills = PurePosixPath(SKILLS_ROOT)
            if owned_root.is_relative_to(skills) or skills.is_relative_to(owned_root):
                raise ValueError(f"An output root overlaps the canonical skills root: {owned_root}")
        for other_name, other in profiles["harnesses"].items():
            if other_name == harness:
                continue
            for other_root in _owned_roots(other):
                for owned_root in owned:
                    if owned_root.is_relative_to(other_root) or other_root.is_relative_to(owned_root):
                        raise ValueError(f"Output roots overlap: {harness}, {other_name}")
        discovery = profile.get("skills_discovery")
        if discovery not in SKILLS_DISCOVERY:
            raise ValueError("skills_discovery must be 'agents_skills' or 'pointer_stubs'")
        if discovery == "pointer_stubs" and not profile.get("skills_stub_dir"):
            raise ValueError("pointer_stubs requires skills_stub_dir")
        pointer_files = profile.get("pointer_files") or {}
        if not isinstance(pointer_files, dict):
            raise ValueError("pointer_files must be a table of relative path -> exact text")
        declared = {key: profile[key] for key in ("skills_stub_dir", "hooks_json_path") if profile.get(key)}
        for key, value in pointer_files.items():
            if not isinstance(value, str):
                raise ValueError(f"pointer_files value for {key!r} must be text")
            declared[f"pointer_files.{key}"] = f"{config_dir}/{_relative(key)}"
        for key, value in declared.items():
            if not any(_relative(value).is_relative_to(owned_root) for owned_root in owned):
                raise ValueError(f"{key} escapes this target's output roots")
        plan = engine.build_plan(harness)
        issues.extend(_issue("projector_gap", ENGINE, gap) for gap in plan.gaps)
        for rel in plan.writes:
            if not any(_relative(rel).is_relative_to(owned_root) for owned_root in owned):
                raise ValueError(f"Planned effect escapes the selected target: {rel}")
        exact_retired = {_relative(rel) for rel in profile.get("leftover_paths", [])}
        active_roots = [owned_root for row in profiles["harnesses"].values() for owned_root in _owned_roots(row)]
        for rel in plan.removes:
            path = _relative(rel)
            if any(path.is_relative_to(owned_root) for owned_root in owned):
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

        # Classification pass (the ruling's acceptance clause): every write is a
        # registration, the ownership manifest or a declared pointer - or a defect.
        named_profile = {**profile, "name": harness}
        for rel in sorted(plan.writes):
            write_class = engine.classify_write(rel, named_profile)
            if write_class in classes:
                classes[write_class] += 1
            else:
                issues.append(_issue("unclassified_output", rel, "Not a registration, ownership manifest or pointer"))

        skills_root = root / SKILLS_ROOT
        expected: dict[str, str] = {}
        for path in sorted(skills_root.glob("*/SKILL.md")):
            if engine.is_projection_junk(path, skills_root):
                continue
            name = path.parent.name
            source_rel = f"{SKILLS_ROOT}/{name}/SKILL.md"
            text = path.read_text(encoding="utf-8", errors="surrogateescape").removeprefix("﻿")
            if engine.skill_fields(text)["name"] != name:
                issues.append(_issue("skill_identity", source_rel, "Skill name differs from its directory"))
            expected[name] = engine.frontmatter_block(text)
        if not expected:
            issues.append(_issue("empty_baseline", SKILLS_ROOT, "No canonical skills were found"))
        if discovery == "pointer_stubs":
            stub_dir = str(_relative(profile["skills_stub_dir"])) + "/"
            observed = {}
            for rel, text in plan.writes.items():
                parts = rel[len(stub_dir) :].split("/") if rel.startswith(stub_dir) else []
                if len(parts) == 2 and parts[1] == "SKILL.md":
                    observed[parts[0]] = text
            for name in sorted(set(expected) - set(observed)):
                issues.append(_issue("missing_skill", f"{stub_dir}{name}/SKILL.md", "The projector omitted this skill"))
            for name in sorted(set(observed) - set(expected)):
                issues.append(_issue("extra_skill", f"{stub_dir}{name}/SKILL.md", "No canonical skill for this stub"))
            for name in sorted(set(expected) & set(observed)):
                rel, stub = f"{stub_dir}{name}/SKILL.md", observed[name]
                if engine.skill_fields(stub)["name"] != name:
                    issues.append(_issue("skill_identity", rel, "Projected identity differs from the canonical skill"))
                if engine.frontmatter_block(stub) != expected[name]:
                    issues.append(_issue("skill_frontmatter_drift", rel, "Frontmatter is not the source block"))
                if _pointer_line(name) not in _stub_body(stub):
                    issues.append(_issue("skill_stub_body", rel, "Stub body lacks the pointer line"))
            result["skills"] = len(observed)
        else:
            message = "The host reads .agents/skills natively; no skill output is projected"
            for rel in sorted(rel for rel in plan.writes if rel.startswith(f"{config_dir}/skills/")):
                issues.append(_issue("unexpected_skill_copy", rel, message))
            result["skills"] = 0

        for rel, text in plan.writes.items():
            if rel.endswith(".json"):
                json.loads(text)
            elif rel.endswith(".toml"):
                tomllib.loads(text)
            elif rel.endswith(".py"):
                compile(text, rel, "exec")
        for key, value in pointer_files.items():
            rel = f"{config_dir}/{_relative(key)}"
            planned = plan.writes.get(rel)
            if planned is None:
                issues.append(_issue("declared_pointer_drift", rel, "missing from the projector's plan"))
            elif planned != value:
                issues.append(_issue("declared_pointer_drift", rel, "planned bytes differ from [pointer_files]"))
            if installed:
                issues.extend(_declared_file_issues(root, rel, value.encode("utf-8"), "profiles.toml [pointer_files]"))

        base = root / BASELINE
        manifest = tomllib.loads((base / profiles["baseline"]["hook_manifest"]).read_text(encoding="utf-8"))
        registration_path = profile.get("hooks_json_path")
        registration = json.loads(plan.writes[registration_path]) if registration_path in plan.writes else {}
        if profile.get("hooks_projection") == "native_cwd_hooks_json":
            # Codex HooksFile (0.156.1) rejects unknown root fields before loading any handler.
            if not isinstance(registration, dict) or set(registration) - {"description", "hooks"}:
                raise ValueError("Codex hooks.json accepts only description and hooks root fields")
            description = registration.get("description")
            if description is not None and not isinstance(description, str):
                raise ValueError("Codex hooks.json description must be a string or null")
            if not isinstance(registration.get("hooks", {}), dict):
                raise ValueError("Codex hooks.json hooks must be an object")
        project_dir_var = profile["project_dir_var"]
        for hook in manifest.get("hook", []):
            script = str(_relative(hook["script"]))
            shared = hook.get("script_root") == "project_scripts"
            rel = f"scripts/{script}" if shared else f"{HOOKS_ROOT}/{script}"
            source = root / rel
            if not source.is_file() or source.resolve() != source:
                issues.append(_issue("missing_hook_source", rel, "Declared hook source is missing or redirected"))
            events = profile.get("hook_events", {}).get(hook["event"], [])
            events = [events] if isinstance(events, str) else events
            if not events:
                issues.append(_issue("missing_hook_event", rel, "No declared native event for this hook"))
            for event in events:
                registered = _registration_events(profile, registration).get(event, [])
                commands = list(_commands(registered))
                referencing = [command for command in commands if _references_script(command, rel, project_dir_var)]
                if not referencing:
                    issues.append(_issue("missing_hook_registration", rel, f"No exact hook path argument at {event}"))
                elif not all(_carries_identity(command, rel, project_dir_var, harness) for command in referencing):
                    issues.append(_issue("missing_identity_argument", rel, f"No '--harness {harness}' at {event}"))
                # Codex prefers commandWindows on Windows, so drift there would silently replace what the ordinary
                # command declares: it must unescape to exactly one of them and carry the same identity (D46).
                for windows_command in _windows_commands(registered):
                    plain = _unescape_powershell(windows_command)
                    if not _references_script(plain, rel, project_dir_var):
                        continue
                    if plain not in commands:
                        issues.append(
                            _issue("windows_registration_drift", rel, f"commandWindows differs from command at {event}")
                        )
                    elif not _carries_identity(plain, rel, project_dir_var, harness):
                        issues.append(
                            _issue(
                                "missing_identity_argument",
                                rel,
                                f"No '--harness {harness}' at {event} (commandWindows)",
                            )
                        )
        if installed:
            issues.extend(_installed_issues(root, owned, plan))
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
        "sources": {"baseline": BASELINE, "skills": SKILLS_ROOT, "hooks": HOOKS_ROOT, "projector": ENGINE},
    }
    try:
        engine = _load_projector(root)
        missing = [name for name in ENGINE_SURFACE if not callable(getattr(engine, name, None))]
        if missing:
            raise ValueError("The projector lacks the checker's contract surface: " + ", ".join(missing))
        profiles = engine.load_profiles()
        engine.resolve_source_roots(root, profiles["baseline"])
        names = sorted(profiles["harnesses"]) if harness == "all" else [harness]
        if not names or any(name not in profiles["harnesses"] for name in names):
            raise ValueError(f"Unknown or empty declared target selection: {harness}")
        for name in names:
            report["harnesses"][name] = _check_target(root, engine, profiles, name, installed)
        # Root-scoped obligations are reported once, not once per selected target.
        report["issues"].extend(_root_pointer_issues(root, profiles))
        report["issues"].extend(_token_residue_issues(root, engine))
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
        counts = ", ".join(f"{cls} {target.get('classes', {}).get(cls, 0)}" for cls in WRITE_CLASSES)
        lines.append(f"- {name}: {target['status']}; {target['files']} files ({counts}), {target['skills']} skills")
        lines.extend(f"  - {i['code']}: {i['path']}: {i['message']}" for i in target["issues"])
    lines.extend(f"- {i['code']}: {i['path']}: {i['message']}" for i in report["issues"])
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
