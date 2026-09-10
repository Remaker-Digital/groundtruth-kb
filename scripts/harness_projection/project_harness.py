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
    default   render the projection into the harness config directory and
              delete profile leftover_paths / leftover_trees
    --dry-run print the plan (files that would be written/removed), write nothing
    --validate render in memory and refuse gaps without requiring installed output
    --check   compare current projection against a fresh render; report write
              drift and leftover files that still exist; exit 1 on any
              difference, 0 when clean

The engine renders these surface classes from the baseline:
    skills/   full SKILL.md bodies (plus reference files), token-substituted,
              stamped after frontmatter
    rules/    all baseline rules, token-substituted, stamped
    hooks/    hook scripts token-substituted + the harness-native hook
              registration rendered from hooks/manifest.toml
    routing   the selected provider's models and routes from routing.toml
    ownership .projection-manifest.json listing every produced path, so
              cleanup and --check can distinguish managed from unmanaged files

Unresolved neutral tokens fail the render (fail closed) - a token the profile
cannot substitute is a projector gap, never silent passthrough.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import tomlkit
import yaml

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
    """Fail closed if any planned write or remove path is inside the baseline tree."""
    blocked = sorted(rel for rel in list(plan.writes) + list(plan.removes) if is_baseline_destination(rel))
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


VENV_INTERPRETER_DIR = "groundtruth-kb/.venv/Scripts"


def projected_interpreter(*, windowless: bool, project_dir_var: str | None = None) -> str:
    """Return the interpreter token for a projected hook registration.

    Never emits a bare interpreter name. On Windows a bare ``python``,
    ``python3`` or ``pythonw`` can resolve to a Microsoft Store app-execution
    alias which prints a diagnostic and exits 0. The harness reads exit 0 as a
    successful hook run, so a registration that never executed reports success
    and the whole governance gate stack fails open silently: no credential
    scan, no destructive-operation gate, no implementation-start
    authorization, no source-of-truth read discipline.

    The emitted token is a PATH, never a bare name, so the OS never performs
    a PATH lookup and the Store alias can never be selected. When the
    harness profile declares a project-directory variable the token is
    runtime-expanded to an absolute path; otherwise it is project-root
    relative, matching how that profile already emits its script paths.

    Deliberately performs NO host discovery: no filesystem existence probe,
    no checkout-root interpolation, no ``sys.executable`` fallback. Output
    bytes derive only from the baseline and the profile, so two generations
    from identical declared inputs are byte-identical on any checkout -- the
    reproducibility contract in ``GOV-HARNESS-NEUTRAL-BASELINE-001``. An
    earlier revision embedded host-absolute literals and violated it; see F3
    of ``gtkb-wi5606-hook-interpreter-resolution-002``.

    Source: advisory ``gtkb-advisory-hook-interpreter-fail-open-20260823``.
    """
    name = "pythonw.exe" if windowless else "python.exe"
    relative = f"{VENV_INTERPRETER_DIR}/{name}"
    if project_dir_var:
        return f"${project_dir_var}/{relative}"
    return relative


_JUNK_NAMES = frozenset({".ds_store", "thumbs.db"})
_JUNK_SUFFIXES = {".pyc", ".pyo", ".pyd", ".lock"}
# Projector-produced ownership manifest. If one appears under the baseline it is
# output that has leaked into source, never projectable configuration (WI-7112).
_PROJECTION_OUTPUT_NAMES = frozenset({".projection-manifest.json"})


def harness_config_dir_names() -> frozenset[str]:
    """Basenames of every registered harness config directory, lowercased.

    Derived from the profile registry rather than hardcoded, so a nested harness
    tree under the baseline is recognized for every registered harness instead of
    only the one that happened to be observed (WI-7112).
    """
    try:
        profiles = load_profiles()
    except Exception:  # noqa: BLE001 - registry unreadable must not crash the filter
        return frozenset()
    names = set()
    for profile in (profiles.get("harnesses") or {}).values():
        config_dir = (profile or {}).get("config_dir")
        if config_dir:
            names.add(Path(str(config_dir)).name.lower())
    return frozenset(names)


def is_projection_junk(path: Path, src_root: Path) -> bool:
    """Skip bytecode, lock files, projector output, and nested harness trees."""
    try:
        relative = path.relative_to(src_root)
    except ValueError:
        relative = path
    parts = {part.lower() for part in relative.parts}
    if "__pycache__" in parts:
        return True
    # A nested harness config directory under the baseline is another harness's
    # projected tree, not neutral source. Generalized over the registered set so
    # this is not true for one harness and silently false for the rest.
    if parts & harness_config_dir_names():
        return True
    if path.suffix.lower() in _JUNK_SUFFIXES:
        return True
    if path.name.lower() in _JUNK_NAMES:
        return True
    return path.name.lower() in _PROJECTION_OUTPUT_NAMES


def _native_events_for_hook(profile: dict, hook: dict, gaps: list[str]) -> list[str]:
    mapped = (profile.get("hook_events") or {}).get(hook["event"])
    if mapped is None:
        gaps.append(f"hook {hook.get('script')}: no native event for {hook.get('event')}")
        return []
    if isinstance(mapped, str):
        values = [mapped]
    elif isinstance(mapped, list):
        values = [str(item) for item in mapped if str(item).strip()]
    else:
        gaps.append(f"hook {hook.get('script')}: event mapping is not a string or list")
        return []
    events: list[str] = []
    seen: set[str] = set()
    for event in values:
        if event in seen:
            continue
        seen.add(event)
        events.append(event)
    return events


def _intent_matcher(profile: dict, hook: dict) -> str:
    matchers = profile.get("intent_matchers") or {}
    intents = hook.get("intents") or []
    if not intents or "all" in intents:
        return ""
    combined: list[str] = []
    seen: set[str] = set()
    for intent in intents:
        pattern = str(matchers.get(intent) or "")
        if not pattern or pattern in seen:
            continue
        seen.add(pattern)
        combined.append(pattern)
    return "|".join(combined)


def _projected_timeout(profile: dict, hook: dict) -> int | None:
    raw = hook.get("timeout_seconds")
    floor = int(profile.get("hook_timeout_floor_seconds") or 0)
    if raw is None:
        return floor if floor > 0 else None
    timeout_val = int(raw)
    if floor > 0:
        timeout_val = max(timeout_val, floor)
    return timeout_val


def _hook_command(profile: dict, hook: dict, tokens: dict[str, str], gaps: list[str]) -> str:
    windowless = bool(profile.get("windowless_hooks"))
    interpreter = projected_interpreter(windowless=windowless)
    if hook.get("script_root") == "project_scripts":
        target = f"scripts/{hook['script']}"
    else:
        target = f"{profile['hooks_dir']}/{hook['script']}"
    adapter = str(profile.get("stdin_adapter") or "").strip()
    if adapter:
        command = f'"{interpreter}" -B {adapter} {target}'
    else:
        command = f'"{interpreter}" -B {target}'
    for arg in hook.get("args", []):
        command += " " + substitute(arg, tokens, "hooks/manifest.toml", gaps)
    return command


def _is_bytecode_leftover(rel: str) -> bool:
    """Bytecode an importer wrote inside a projection root (test runs load the hooks).

    Write mode removes it; check mode reports it without failing, because it is
    regenerated by any test that imports a projected hook and carries no content
    (owner decision, 2026-09-07).
    """
    parts = rel.split("/")
    return "__pycache__" in parts or rel.endswith(tuple(_JUNK_SUFFIXES))


def apply_leftover_removes(plan: Plan, profile: dict) -> None:
    owned = set(plan.writes)
    seen: set[str] = set()
    leftovers = list(profile.get("leftover_paths") or []) + list(profile.get("leftover_trees") or [])
    for rel in leftovers:
        normalized = normalize_planned_rel(str(rel))
        if not normalized or normalized in seen or normalized in owned:
            continue
        seen.add(normalized)
        plan.removes.append(normalized)

    # WI-7685 class 1. Bytecode is an interpreter side effect of executing code
    # from inside the projection tree; it is never projector output, and it has
    # no readers.
    #
    # The `-B` flag above prevents it only where the projector controls the
    # command line. It cannot cover an importer the projector does not invoke,
    # and that is not hypothetical: `.cursor` was measured at zero surplus,
    # projected clean, and held `__pycache__/write_bridge.cpython-314.pyc`
    # within the hour, created by something importing a projected helper. A
    # projection run then reported "0 leftovers removed" because bytecode was
    # not a leftover. Prevention and cleanup are both required; either alone
    # leaves the property holding only most of the time.
    config_dir = str(profile.get("config_dir") or "").strip()
    if config_dir:
        projection_root = PROJECT_ROOT / config_dir
        manifest_path = projection_root / ".projection-manifest.json"
        if manifest_path.exists():
            try:
                if projection_root.is_symlink() or getattr(projection_root, "is_junction", lambda: False)():
                    raise ValueError("projection directory is linked; cleanup requires a local output directory")
                if manifest_path.is_symlink() or not manifest_path.resolve().is_relative_to(PROJECT_ROOT.resolve()):
                    raise ValueError("projection manifest is linked or outside the project root")
                previous = json.loads(manifest_path.read_text(encoding="utf-8"))
                if (
                    not isinstance(previous, dict)
                    or previous.get("engine") != "scripts/harness_projection/project_harness.py"
                    or previous.get("harness") != profile.get("name")
                    or previous.get("baseline_root") != BASELINE_ROOT_NAME
                    or not isinstance(previous.get("paths"), list)
                ):
                    raise ValueError("projection manifest does not describe this harness's generated outputs")
                for rel in previous["paths"]:
                    if (
                        not isinstance(rel, str)
                        or "\\" in rel
                        or ":" in rel
                        or ".." in PurePosixPath(rel).parts
                        or rel != PurePosixPath(rel).as_posix()
                        or not rel.startswith(config_dir + "/")
                    ):
                        raise ValueError("projection manifest contains a path outside this harness's output directory")
                    if rel in owned or rel in seen:
                        continue
                    target = PROJECT_ROOT / rel
                    if target.is_symlink() or not target.resolve().is_relative_to(projection_root.resolve()):
                        raise ValueError("retired output is linked or escapes this harness's output directory")
                    if target.exists() and not target.is_file():
                        raise ValueError("a retired output is not a file; directory cleanup requires explicit scope")
                    if target.is_file():
                        seen.add(rel)
                        plan.removes.append(rel)
            except (OSError, UnicodeError, ValueError) as error:
                plan.gaps.append(f"Cannot reconcile retired outputs for {profile.get('name')!r}: {error}")
        if projection_root.is_dir():
            stale = list(projection_root.rglob("__pycache__")) + list(projection_root.rglob("*.pyc"))
            for path in sorted(stale):
                if not path.exists():
                    continue
                normalized = normalize_planned_rel(path.relative_to(PROJECT_ROOT).as_posix())
                if not normalized or normalized in seen or normalized in owned:
                    continue
                seen.add(normalized)
                plan.removes.append(normalized)


def remove_planned_path(target: Path) -> bool:
    if target.is_symlink() or target.is_file():
        target.unlink()
        return True
    if target.is_dir():
        shutil.rmtree(target)
        return True
    return False


def _get_ruff_cmd() -> list[str]:
    venv_ruff = PROJECT_ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "ruff.exe"
    if venv_ruff.is_file():
        return [str(venv_ruff)]
    if shutil.which("ruff"):
        return ["ruff"]
    return [sys.executable, "-m", "ruff"]


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


def skill_fields(text: str) -> dict[str, str]:
    """Check required scalar identity fields without inferring a skill name."""
    lines = text.removeprefix("\ufeff").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("Missing opening skill frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("Missing closing skill frontmatter") from error
    try:
        parsed = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as error:
        raise ValueError("Invalid YAML skill frontmatter") from error
    if not isinstance(parsed, dict):
        raise ValueError("Skill frontmatter must be a mapping")
    if not all(isinstance(parsed.get(key), str) and parsed[key].strip() for key in ("name", "description")):
        raise ValueError("Skill name and description must be nonempty strings")
    fields = {}
    for line in lines[1:end]:
        if not line or line.startswith((" ", "\t", "#")):
            continue
        key, separator, value = line.partition(":")
        if not separator or key in fields:
            raise ValueError("Malformed or duplicate skill frontmatter field")
        fields[key] = value.strip().strip("\"'")
    if not all(fields.get(key) for key in ("name", "description")):
        raise ValueError("Skill name and description are required")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fields["name"]):
        raise ValueError("Skill name must be an exact lowercase slug")
    return fields


def adapter_metadata_block(harness: str, source_rel: str, source_text: str) -> str:
    """Descriptive generation metadata; conformance compares the complete plan.

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


# A Windows native hook may receive cwd only on stdin. Resolve the common Git
# installation at runtime so clone-independent output needs no invented host
# environment variables or embedded checkout path. Hidden ProcessStartInfo
# preserves UTF-8 pipes; pythonw through a PowerShell pipeline loses stdout.
_NATIVE_CWD_BOOTSTRAP = "& { param([string]$adapterRel, [string]$hook, [string]$event, [int]$timeout) $ErrorActionPreference = 'Stop'; [Console]::InputEncoding = [Text.UTF8Encoding]::new($false); [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false); $process = $null; try { $raw = [Console]::In.ReadToEnd(); $native = ConvertFrom-Json -InputObject $raw; if (-not [IO.Path]::IsPathRooted($native.cwd)) { throw 'Missing native working directory' }; $common = & git -C $native.cwd rev-parse --path-format=absolute --git-common-dir 2>$null; if ($LASTEXITCODE -ne 0 -or @($common).Count -ne 1) { throw 'Cannot resolve GT-KB installation' }; $root = Split-Path -Parent $common; $python = Join-Path $root 'groundtruth-kb/.venv/Scripts/python.exe'; $adapter = Join-Path $root $adapterRel; if (-not (Test-Path -LiteralPath $python -PathType Leaf) -or -not (Test-Path -LiteralPath $adapter -PathType Leaf)) { throw 'GT-KB hook runtime is unavailable' }; $psi = [Diagnostics.ProcessStartInfo]::new(); $psi.FileName = $python; $psi.WorkingDirectory = $root; $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true; $psi.RedirectStandardInput = $true; $psi.RedirectStandardOutput = $true; $psi.RedirectStandardError = $true; $psi.StandardOutputEncoding = [Text.UTF8Encoding]::new($false); $psi.StandardErrorEncoding = [Text.UTF8Encoding]::new($false); $q = [char]34; $psi.Arguments = '-B '+$q+$adapter+$q+' --event '+$event+' --timeout '+($timeout - 1)+' '+$q+$hook+$q; foreach ($arg in $args) { if ($arg.Contains($q) -or $arg.EndsWith('\\')) { throw 'Unsupported hook argument quoting' }; $psi.Arguments += ' '+$q+$arg+$q }; $psi.EnvironmentVariables['PYTHONIOENCODING'] = 'utf-8'; $process = [Diagnostics.Process]::new(); $process.StartInfo = $psi; $null = $process.Start(); $stdout = $process.StandardOutput.ReadToEndAsync(); $stderr = $process.StandardError.ReadToEndAsync(); $process.StandardInput.Write($raw); $process.StandardInput.Close(); if (-not $process.WaitForExit($timeout * 1000)) { $process.Kill(); throw 'GT-KB hook adapter timed out' }; $text = $stdout.GetAwaiter().GetResult(); if ($process.ExitCode -ne 0 -or -not $text) { throw 'GT-KB hook adapter did not complete' }; $null = ConvertFrom-Json -InputObject $text; [Console]::Out.WriteLine($text) } catch { $reason = 'GT-KB native hook unavailable: ' + $_.Exception.Message; if ($event -eq 'PreToolUse') { @{hookSpecificOutput=@{hookEventName='PreToolUse'; permissionDecision='deny'; permissionDecisionReason=$reason}} | ConvertTo-Json -Compress } elseif ($event -eq 'Stop') { @{decision='block'; reason=$reason} | ConvertTo-Json -Compress } else { @{systemMessage=$reason} | ConvertTo-Json -Compress } } finally { if ($null -ne $process) { $process.Dispose() } } }"


def _native_cwd_hook_command(profile: dict, hook: dict, event: str, timeout: int, tokens: dict, gaps: list[str]) -> str:
    target = (
        f"scripts/{hook['script']}"
        if hook.get("script_root") == "project_scripts"
        else f"{profile['hooks_dir']}/{hook['script']}"
    )
    arguments = [profile["stdin_adapter"], target, event, str(max(2, timeout - 2))]
    arguments.extend(substitute(arg, tokens, "hooks/manifest.toml", gaps) for arg in hook.get("args", []))
    # Arguments cross cmd.exe quoting and then PowerShell's -Command parser.
    # Double quotes protect shell metacharacters; inner single-quoted literals
    # prevent PowerShell from interpreting them as expressions.
    if any('"' in arg or arg.endswith("\\") for arg in arguments):
        gaps.append("unsupported_native_hook_argument: embedded quote or trailing backslash")
        return ""
    quoted = ['"' + "'" + arg.replace("'", "''") + "'" + '"' for arg in arguments]
    return 'powershell.exe -NoProfile -NonInteractive -Command "' + _NATIVE_CWD_BOOTSTRAP + '" ' + " ".join(quoted)


def render_hooks_registration(
    profile: dict, manifest: dict, tokens: dict[str, str], gaps: list[str]
) -> tuple[str, str] | None:
    """Render the harness-native hook registration from the neutral manifest."""
    mode = profile.get("hooks_projection")
    if mode == "antigravity_hooks_json":
        adapter = str(profile["stdin_adapter"])
        adapter_path = PROJECT_ROOT / adapter
        if not adapter_path.is_file() or adapter_path.resolve() != adapter_path:
            gaps.append(f"Missing or redirected native hook adapter: {adapter}")
            return None
        events_out: dict[str, list[dict]] = {}
        for hook in manifest.get("hook", []):
            native_event = profile.get("hook_events", {}).get(hook["event"])
            if native_event is None:
                gaps.append(f"hook {hook['script']}: no native event for {hook['event']}")
                continue
            target = (
                f"scripts/{hook['script']}"
                if hook.get("script_root") == "project_scripts"
                else f"{profile['hooks_dir']}/{hook['script']}"
            )
            timeout = _projected_timeout(profile, hook) or 30
            interpreter = projected_interpreter(windowless=True)
            command = f'"{interpreter}" -B {adapter} --event {native_event} --timeout {max(1, timeout - 2)} {target}'
            for arg in hook.get("args", []):
                command += " " + substitute(arg, tokens, "hooks/manifest.toml", gaps)
            entry = {"type": "command", "command": command, "timeout": timeout}
            if native_event in {"PreToolUse", "PostToolUse"}:
                entry = {"matcher": _intent_matcher(profile, hook), "hooks": [entry]}
            events_out.setdefault(native_event, []).append(entry)
        return profile["hooks_json_path"], json.dumps({"gtkb": events_out}, indent=2) + "\n"
    if mode == "plugin_hooks_json":
        events: dict[str, list[dict]] = {}
        blocking_ok = set(profile.get("blocking_events", {}).get("supported", []))
        for hook in manifest.get("hook", []):
            native_event = profile.get("hook_events", {}).get(hook["event"])
            if native_event is None:
                gaps.append(f"hook {hook['script']}: no native event for {hook['event']}")
                continue
            interpreter = projected_interpreter(windowless=False)
            if hook.get("script_root") == "project_scripts":
                command = f'"{interpreter}" -B scripts/{hook["script"]}'
            else:
                command = f'"{interpreter}" -B {profile["hooks_dir"]}/{hook["script"]}'
            for arg in hook.get("args", []):
                command += " " + substitute(arg, tokens, "hooks/manifest.toml", gaps)
            entry: dict = {"command": command}
            timeout = _projected_timeout(profile, hook)
            if timeout is not None:
                entry["timeout"] = timeout
            if hook.get("blocking") and native_event in blocking_ok:
                entry["blocking"] = True
            events.setdefault(native_event, []).append(entry)
        payload = {
            "_comment": "PROJECTION, NOT CANONICAL - rendered from the baseline hooks/manifest.toml by the GT-KB projection engine; edit the baseline and re-project.",
            "hooks": events,
        }
        return profile["hooks_json_path"], json.dumps(payload, indent=2) + "\n"
    if mode in {"settings_json", "native_cwd_hooks_json"}:
        if mode == "native_cwd_hooks_json":
            adapter_path = PROJECT_ROOT / profile["stdin_adapter"]
            if not adapter_path.is_file() or adapter_path.resolve() != adapter_path:
                gaps.append(f"Missing or redirected native hook adapter: {profile['stdin_adapter']}")
                return None
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
            interpreter = projected_interpreter(windowless=True, project_dir_var=profile["project_dir_var"])
            command = f'"{interpreter}" -B "{script_path}"'
            for arg in hook.get("args", []):
                command += " " + substitute(arg, tokens, "hooks/manifest.toml", gaps)
            if mode == "native_cwd_hooks_json":
                command = _native_cwd_hook_command(
                    profile, hook, native_event, _projected_timeout(profile, hook) or 30, tokens, gaps
                )
            entry = {"type": "command", "command": command}
            timeout = _projected_timeout(profile, hook)
            if timeout is not None:
                entry["timeout"] = timeout
            group = {"matcher": matcher, "hooks": [entry]} if matcher else {"hooks": [entry]}
            events_out.setdefault(native_event, []).append(group)
        payload = {
            "_comment": "PROJECTION, NOT CANONICAL - rendered from the baseline hooks/manifest.toml by the GT-KB projection engine; edit the baseline and re-project.",
            "hooks": events_out,
        }
        return profile["hooks_json_path"], json.dumps(payload, indent=2) + "\n"
    if mode in {"hooks_json", "cursor_hooks_json"}:
        events_out: dict[str, list[dict]] = {}
        seen_keys: set[tuple[str, str, str]] = set()
        fail_closed_ok = set((profile.get("fail_closed_events") or {}).get("supported") or [])
        for hook in manifest.get("hook", []):
            for native_event in _native_events_for_hook(profile, hook, gaps):
                command = _hook_command(profile, hook, tokens, gaps)
                matcher = _intent_matcher(profile, hook)
                key = (native_event, command, matcher)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                entry: dict = {"command": command}
                timeout = _projected_timeout(profile, hook)
                if timeout is not None:
                    entry["timeout"] = timeout
                if matcher:
                    entry["matcher"] = matcher
                if (
                    hook.get("blocking")
                    and bool(profile.get("fail_closed_on_blocking"))
                    and native_event in fail_closed_ok
                ):
                    entry["failClosed"] = True
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


def render_provider_routing(profile: dict, baseline: Path) -> str:
    """Derive only the selected provider's models and routes from the baseline."""
    provider = profile["name"]
    source = baseline / "routing.toml"
    try:
        data = tomllib.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ProjectionError("canonical provider routing source is missing or unreadable") from exc
    models = data.get("models")
    routing = data.get("routing")
    if data.get("schema_version") != 1 or not isinstance(models, dict) or not isinstance(routing, dict):
        raise ProjectionError("canonical provider routing must contain schema 1, models and routing tables")
    selected = {key: row for key, row in models.items() if isinstance(row, dict) and row.get("provider") == provider}
    own = routing.get(provider)
    if not selected or not isinstance(own, dict):
        raise ProjectionError(f"canonical provider routing is incomplete for {provider}")
    skills = own.get("skills", {})
    if not isinstance(skills, dict) or any(not isinstance(value, str) for value in skills.values()):
        raise ProjectionError(f"canonical provider skill routing is invalid for {provider}")
    if any(not isinstance(key, str) or key not in selected for key in [own.get("default_model"), *skills.values()]):
        raise ProjectionError(f"canonical provider routing references an unconfigured {provider} model")
    return "# Generated from the canonical harness baseline; edit the source and re-project.\n" + tomlkit.dumps(
        {"schema_version": 1, "models": selected, "routing": {provider: own}}
    )


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
    deferred_rules = set(baseline_cfg.get("deferred_rules") or [])
    plan = Plan()

    surfaces = {}
    if profile.get("skills_dir"):
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
            if is_projection_junk(path, src_root):
                continue
            rel_in_surface = path.relative_to(src_root).as_posix()
            if src_name == "hooks" and rel_in_surface == "manifest.toml":
                continue  # the registration is rendered natively, below
            if src_name == "rules" and rel_in_surface in deferred_rules:
                # Activity-envelope deferral (WI-4949): these load on
                # ::open <activity>, read from the baseline. A harness rules
                # dir auto-loads wholesale, so projecting them here would
                # defeat the deferral and make it advisory only.
                plan.removes.append(f"{dst_root}/{rel_in_surface}")
                continue
            rel_out = f"{dst_root}/{rel_in_surface}"
            if path.suffix.lower() in TEXT_SUFFIXES:
                source_text = path.read_text(encoding="utf-8", errors="surrogateescape")
                text = substitute(source_text, tokens, rel_out, plan.gaps)
                if src_name == "skills" and rel_in_surface.endswith("SKILL.md"):
                    text = text.removeprefix("\ufeff")
                    try:
                        fields = skill_fields(text)
                        if fields["name"] != path.parent.name:
                            raise ValueError("Skill name differs from its directory")
                    except ValueError as error:
                        plan.gaps.append(f"{rel_out}: {error}")
                        continue
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
                # Fail closed on an artifact class the projector does not
                # recognize, naming the offending material (WI-7112). Silently
                # copying an unknown class through a latin-1 round-trip is how a
                # stray artifact reaches every registered harness at once, and a
                # gap that does not say WHAT was unrecognized reproduces the
                # diagnosis cost this guard exists to remove.
                offending = f"{baseline_cfg['root']}/{src_name}/{rel_in_surface}"
                artifact_class = path.suffix.lower() or path.name
                plan.gaps.append(
                    f"unrecognized artifact class '{artifact_class}' at {offending}; "
                    "classify it as projectable (extend TEXT_SUFFIXES) or as excluded "
                    "(extend is_projection_junk) - the projector will not guess"
                )
                continue

    if profile.get("routing_projection"):
        try:
            plan.writes[f"{profile['config_dir']}/routing.toml"] = render_provider_routing(profile, base)
        except ProjectionError as exc:
            plan.gaps.append(str(exc))

    manifest_path = base / baseline_cfg["hook_manifest"]
    if manifest_path.is_file():
        manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        valid_hooks = []
        for hook in manifest.get("hook", []):
            script = hook.get("script")
            relative = PurePosixPath(script) if isinstance(script, str) else PurePosixPath(".")
            if (
                not isinstance(script, str)
                or not script
                or str(relative) == "."
                or relative.is_absolute()
                or ".." in relative.parts
                or ":" in script
                or "\\" in script
                or hook.get("script_root") not in {None, "project_scripts"}
            ):
                plan.gaps.append(f"invalid_hook_source: {script!r}")
                continue
            source_root = PROJECT_ROOT / "scripts" if hook.get("script_root") == "project_scripts" else base / "hooks"
            source = source_root / str(relative)
            if not source.is_file() or source.resolve() != source:
                plan.gaps.append(f"missing_hook_source: {source.relative_to(PROJECT_ROOT).as_posix()}")
                continue
            valid_hooks.append(hook)
        rendered = render_hooks_registration(profile, {**manifest, "hook": valid_hooks}, tokens, plan.gaps)
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
    apply_leftover_removes(plan, profile)
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
    if mode == "validate":
        print(f"VALID {harness}: {len(plan.writes)} derivable files")
        return 0
    if mode == "dry-run":
        print(f"DRY-RUN plan for {harness}: {len(plan.writes)} files, {len(plan.removes)} leftovers")
        for rel in sorted(plan.writes):
            print("  write", rel)
        for rel in plan.removes:
            print("  remove", rel)
        return 0
    for rel in [*plan.writes, *plan.removes]:
        relative = PurePosixPath(rel)
        if relative.is_absolute() or ".." in relative.parts or ":" in rel:
            print(f"FAIL: projection output is outside the selected project: {rel}")
            return 2
        target = PROJECT_ROOT.resolve() / rel
        if target.resolve() != target:
            print(f"FAIL: projection output is redirected: {rel}")
            return 2
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
        bytecode: list[str] = []
        for rel in plan.removes:
            if (PROJECT_ROOT / rel).exists():
                (bytecode if _is_bytecode_leftover(rel) else drift).append(f"leftover: {rel}")
        print(f"CHECK {harness}: {len(drift)} drifted of {len(plan.writes)} managed")
        for d in drift:
            print("  -", d)
        for b in bytecode:
            print("  - (bytecode; removed on the next write)", b)
        return 1 if drift else 0
    for rel, content in plan.writes.items():
        target = PROJECT_ROOT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        encoded = content.encode("utf-8", errors="surrogateescape")
        descriptor, temporary = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
        tmp_target = Path(temporary)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(encoded)
            os.replace(tmp_target, target)
        finally:
            tmp_target.unlink(missing_ok=True)
    removed = 0
    for rel in plan.removes:
        if remove_planned_path(PROJECT_ROOT / rel):
            removed += 1
    print(f"PROJECTED {harness}: {len(plan.writes)} files, {removed} leftovers removed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harness", required=True)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--check", action="store_true")
    modes.add_argument(
        "--validate", action="store_true", help="Validate derivation without reading or writing installed output."
    )
    args = parser.parse_args()
    mode = "validate" if args.validate else "dry-run" if args.dry_run else "check" if args.check else "write"
    try:
        return run(args.harness, mode)
    except ProjectionError as exc:
        print(f"PROJECTION ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
