"""Bring an initialized application's managed files forward from the host baseline.

Managed outputs are the host's native reference-transaction hook and the
harness projections rendered by the supported projector for the registered
application; the artifact-boundary registry gains the declarations it lacks for
them and for the disposable search cache (a conflicting cache declaration is
refused, never reclassified). Application-owned files are never touched.
Preview is the default; apply performs staged replacement of managed paths
only, refusing before any effect when an input is malformed or a managed path
holds unrecoverable local work. Recovery uses the application's own Git
history: there are no receipts, no second authority and no implicit commit.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Literal
from urllib.parse import quote

from groundtruth_kb.authority_client import AuthorityClient
from groundtruth_kb.config import GTConfig, GTConfigError
from groundtruth_kb.isolation.registry_check import application_slot_path, load_application_catalog
from groundtruth_kb.isolation.validation import check_slot_markers
from groundtruth_kb.project.chroma import CHROMA_CLASSIFICATION, CHROMA_DIRNAME
from groundtruth_kb.project.scaffold import (
    ISOLATION_REGISTRY,
    RUNTIME_TOP_LEVEL_ENTRIES,
    _git,
    _hook_bytes,
    inherited_git_overrides,
    render_projection,
)

Action = Literal["add", "replace", "unchanged", "remove"]

# The scaffold's declaration of the disposable search cache: the only target ``gt project chroma regenerate``
# accepts, so a registry that predates it is brought forward with exactly this entry.
CACHE_DECLARATION: dict[str, str] = dict(
    zip(
        ("name", "type", "classification", "purpose"),
        next(entry for entry in RUNTIME_TOP_LEVEL_ENTRIES if entry[0] == CHROMA_DIRNAME),
        strict=True,
    )
)


class MalformedInputError(ValueError):
    """An existing managed input cannot be interpreted; nothing was changed."""

    code = "malformed_input"


class LocalWorkError(ValueError):
    """A managed path holds local work that Git history could not recover."""

    code = "checkout_has_local_work"


@dataclass(frozen=True)
class UpgradeOptions:
    application: str
    project_id: str
    gt_kb_root: Path
    authority_url: str
    harnesses: tuple[str, ...] = ()


@dataclass(frozen=True)
class UpgradeAction:
    path: str
    action: Action
    reason: str
    preserved_entries: int = 0

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "action": self.action,
            "reason": self.reason,
            "preserved_entries": self.preserved_entries,
        }


@dataclass(frozen=True)
class UpgradePlan:
    options: UpgradeOptions
    project: dict[str, Any]
    target: Path
    harnesses: tuple[str, ...]
    actions: tuple[UpgradeAction, ...]
    writes: dict[str, bytes]
    removes: tuple[str, ...]
    inputs: dict[Path, str]

    @property
    def changes(self) -> tuple[UpgradeAction, ...]:
        return tuple(action for action in self.actions if action.action != "unchanged")

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project["id"],
            "repository_ref": self.project["repository_ref"],
            "target": str(self.target),
            "harnesses": list(self.harnesses),
            "actions": [action.to_json_dict() for action in self.actions],
            "changes": len(self.changes),
        }


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _profiles(host: Path) -> dict[str, Any]:
    payload = tomllib.loads((host / "scripts/harness_projection/profiles.toml").read_text(encoding="utf-8"))
    return dict(payload["harnesses"])


def _baseline_hook_scripts(host: Path, profiles_payload: Path) -> set[str]:
    baseline = tomllib.loads(profiles_payload.read_text(encoding="utf-8"))["baseline"]
    manifest = host / baseline["root"] / baseline["hook_manifest"]
    if not manifest.is_file():
        return set()
    return {
        str(hook["script"])
        for hook in tomllib.loads(manifest.read_text(encoding="utf-8")).get("hook", [])
        if isinstance(hook.get("script"), str)
    }


def _baseline_hooks_root(profiles_payload: Path) -> str:
    """The baseline hooks directory every managed registration names (profiles.toml [baseline] hooks_root)."""
    baseline = tomllib.loads(profiles_payload.read_text(encoding="utf-8"))["baseline"]
    hooks_root = baseline.get("hooks_root")
    if not isinstance(hooks_root, str) or not hooks_root:
        raise ValueError("The host's harness profiles declare no baseline hooks_root")
    return hooks_root


def _selected_application(options: UpgradeOptions) -> tuple[dict[str, Any], Path]:
    host = options.gt_kb_root.absolute()
    if host.resolve(strict=True) != host or not host.is_dir():
        raise ValueError("Select an existing, unredirected platform host")
    if inherited_git_overrides():
        raise ValueError("Remove inherited Git repository/index/config overrides before application upgrade")
    project = AuthorityClient(options.authority_url).request(
        "GET", "/v1/projects/" + quote(options.project_id, safe="")
    )["project"]
    ref = project.get("repository_ref")
    if project.get("kind") != "project" or ref != "application:" + options.application:
        raise ValueError("Select the execution project registered for this application repository")
    target = application_slot_path(host, options.application)
    if options.application not in load_application_catalog(host):
        raise ValueError("Register the application before upgrading its files")
    checks = check_slot_markers(host, options.application)
    if not checks["consistent"] or not checks["app_toml_present"]:
        raise ValueError("The application marker must agree with its catalog entry")
    config_path = target / "groundtruth.toml"
    if not config_path.is_file():
        raise ValueError("The application is not initialized: use gt project init")
    try:
        config = GTConfig.load(config_path=config_path, discover=False)
    except (GTConfigError, OSError, ValueError) as error:
        raise MalformedInputError(f"groundtruth.toml cannot be read: {error}") from error
    if config.authority_url != options.authority_url:
        raise ValueError("The application configuration selects a different authority; reconcile it first")
    if not (target / ".git").is_dir() or Path(_git(target, "rev-parse", "--show-toplevel")).resolve() != target:
        raise ValueError("The application must be its own Git repository root; recovery uses its history")
    return dict(project), target


def projected_harnesses(host: Path, target: Path) -> tuple[str, ...]:
    """Harnesses previously projected into the application, by their ownership manifests."""
    found = []
    for name, profile in _profiles(host).items():
        config_dir = str(profile.get("config_dir") or "")
        if config_dir and (target / config_dir / ".projection-manifest.json").is_file():
            found.append(name)
    return tuple(found)


def _entry_is_managed(entry: Any, *, markers: tuple[str, ...]) -> bool:
    text = json.dumps(entry, sort_keys=True)
    return any(marker in text for marker in markers)


def _merge_hook_registration(
    existing_bytes: bytes, rendered: bytes, path: str, markers: tuple[str, ...]
) -> tuple[bytes, int]:
    """Replace managed registrations in place; keep the application's own entries where they are."""
    try:
        current = json.loads(existing_bytes.decode("utf-8"))
        wanted = json.loads(rendered.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise MalformedInputError(f"{path} is not valid JSON; repair it before upgrading") from error
    if not isinstance(current, dict) or not isinstance(wanted, dict):
        raise MalformedInputError(f"{path} must contain a JSON object")
    key = "gtkb" if "gtkb" in wanted else "hooks"
    current_events = current.get(key, {})
    wanted_events = wanted.get(key, {})
    if not isinstance(current_events, dict) or not isinstance(wanted_events, dict):
        raise MalformedInputError(f"{path} hook registrations must be an object keyed by event")
    merged_events: dict[str, list[Any]] = {}
    preserved = 0
    for event in list(current_events) + [event for event in wanted_events if event not in current_events]:
        existing_entries = current_events.get(event, [])
        rendered_entries = wanted_events.get(event, [])
        if not isinstance(existing_entries, list) or not isinstance(rendered_entries, list):
            raise MalformedInputError(f"{path} registrations for {event} must be lists")
        merged: list[Any] = []
        inserted = False
        for entry in existing_entries:
            if _entry_is_managed(entry, markers=markers):
                if not inserted:
                    merged.extend(rendered_entries)
                    inserted = True
                continue
            merged.append(entry)
            preserved += 1
        if not inserted:
            merged.extend(rendered_entries)
        if merged:
            merged_events[event] = merged
    result = {**{k: v for k, v in current.items() if k not in {key, "_comment", "version"}}, **wanted}
    result[key] = merged_events
    return (json.dumps(result, indent=2) + "\n").encode("utf-8"), preserved


def _merged_registry(target: Path, application: str, writes: dict[str, bytes]) -> bytes | None:
    """The application's artifact-boundary registry with every managed top-level entry present.

    Application-owned entries and their classifications are preserved; only entries the upgrade writes and the
    registry lacks are added, and the disposable search cache the scaffold declares (``.groundtruth-chroma``, DIR
    ``generated_output``, the only target ``gt project chroma regenerate`` accepts) when the registry predates it.
    A cache entry declared with another type or classification is a conflict the upgrade does not resolve: it is
    refused before any effect, never reclassified. A missing registry is not invented here (the doctor reports
    it); a malformed one is refused before any effect.
    """
    path = target / ISOLATION_REGISTRY
    if not path.exists():
        return None
    if path.resolve() != path or not path.is_file():
        raise MalformedInputError(f"{ISOLATION_REGISTRY} is redirected or is not a file")
    try:
        payload = json.loads(path.read_bytes().decode("utf-8"))
        entries = payload["top_level_artifacts"]
        assert isinstance(entries, list) and all(
            isinstance(e, dict) and isinstance(e.get("name"), str) for e in entries
        )
    except (ValueError, KeyError, TypeError, AssertionError) as error:
        raise MalformedInputError(f"{ISOLATION_REGISTRY} cannot be read: {error}") from error
    known = {entry["name"] for entry in entries}
    added = []
    declared = next((entry for entry in entries if entry["name"] == CHROMA_DIRNAME), None)
    if declared is None:
        added.append(dict(CACHE_DECLARATION))
        known.add(CHROMA_DIRNAME)
    elif declared.get("type") != CACHE_DECLARATION["type"] or declared.get("classification") != CHROMA_CLASSIFICATION:
        raise ValueError(
            f"{ISOLATION_REGISTRY} declares {CHROMA_DIRNAME} as {declared.get('type')} "
            f"{declared.get('classification')}, not the disposable search cache "
            f"({CACHE_DECLARATION['type']} {CHROMA_CLASSIFICATION}); reconcile it first"
        )
    for name in writes:
        top = name.split("/")[0]
        if top in known or top == ISOLATION_REGISTRY:
            continue
        known.add(top)
        purpose = (
            "Native project-commit hook maintained by gt project upgrade"
            if top == ".githooks"
            else "Harness configuration projected from the host baseline; regenerated by gt project upgrade"
        )
        added.append(
            {
                "name": top,
                "type": "DIR" if "/" in name else "FILE",
                "classification": "generated_output",
                "purpose": purpose,
            }
        )
    if not added:
        return None
    del application
    payload["top_level_artifacts"] = sorted(entries + added, key=lambda entry: str(entry["name"]).casefold())
    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def plan_upgrade(options: UpgradeOptions) -> UpgradePlan:
    """Compute managed-file actions for the application without any effect."""
    project, target = _selected_application(options)
    host = options.gt_kb_root
    inputs: dict[Path, str] = {
        host / "applications/registry.toml": _sha(host / "applications/registry.toml"),
        target / "application.toml": _sha(target / "application.toml"),
        target / "groundtruth.toml": _sha(target / "groundtruth.toml"),
    }
    writes: dict[str, bytes] = {".githooks/reference-transaction": _hook_bytes(host, inputs)}
    removes: list[str] = []
    profiles = _profiles(host)
    scripts = _baseline_hook_scripts(host, host / "scripts/harness_projection/profiles.toml")
    hooks_root = _baseline_hooks_root(host / "scripts/harness_projection/profiles.toml")
    harnesses = tuple(dict.fromkeys(options.harnesses)) or projected_harnesses(host, target)
    registrations: dict[str, tuple[str, ...]] = {}
    for harness in harnesses:
        profile = profiles.get(harness)
        if profile is None:
            raise ValueError(f"Unknown harness profile: {harness}")
        rendered = render_projection(host, harness, options.application)
        if rendered["gaps"]:
            raise ValueError("Projection gaps for " + harness + ": " + "; ".join(map(str, rendered["gaps"])))
        for name, text in rendered["writes"].items():
            body = text.encode("utf-8")
            if name in writes and writes[name] != body:
                raise ValueError("Projections disagree on " + name)
            writes[name] = body
        removes.extend(name for name in rendered["removes"] if name not in writes)
        for name, identity in rendered["inputs"].items():
            inputs[host / name] = identity
        hooks_path = profile.get("hooks_json_path")
        if isinstance(hooks_path, str) and hooks_path in writes:
            markers = tuple(
                marker for marker in (hooks_root, str(profile.get("stdin_adapter") or ""), *scripts) if marker
            )
            registrations[hooks_path] = markers
    registry = _merged_registry(target, options.application, writes)
    if registry is not None:
        writes[ISOLATION_REGISTRY] = registry
    actions: list[UpgradeAction] = []
    for name in sorted(writes):
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or ":" in name or "\\" in name:
            raise ValueError("Invalid managed output path: " + name)
        path = target / name
        if path.exists() and (path.resolve() != path or not path.is_file()):
            raise MalformedInputError(f"{name} is redirected or is not a file")
        if not path.exists():
            actions.append(UpgradeAction(name, "add", "managed file is missing"))
            continue
        current = path.read_bytes()
        if name in registrations:
            merged, preserved = _merge_hook_registration(current, writes[name], name, registrations[name])
            writes[name] = merged
            if merged == current:
                actions.append(UpgradeAction(name, "unchanged", "registrations already current", preserved))
            else:
                actions.append(UpgradeAction(name, "replace", "managed registrations differ", preserved))
            continue
        if current == writes[name]:
            actions.append(UpgradeAction(name, "unchanged", "already current"))
        elif name == ISOLATION_REGISTRY:
            actions.append(UpgradeAction(name, "replace", "managed top-level entries are missing from the registry"))
        else:
            actions.append(UpgradeAction(name, "replace", "managed bytes differ from the current baseline"))
    for name in dict.fromkeys(removes):
        path = target / name
        if path.exists():
            if path.resolve() != path:
                raise MalformedInputError(f"{name} is redirected")
            actions.append(UpgradeAction(name, "remove", "retired output is no longer produced"))
    return UpgradePlan(
        options, project, target, harnesses, tuple(actions), writes, tuple(dict.fromkeys(removes)), inputs
    )


def _local_work(target: Path, paths: list[str]) -> list[str]:
    """Managed paths whose current bytes are not recoverable from Git history."""
    if not paths:
        return []
    result = subprocess.run(
        [
            "git",
            "--no-optional-locks",
            "-C",
            str(target),
            "status",
            "--porcelain",
            "-z",
            "--untracked-files=all",
            "--",
            *paths,
        ],
        capture_output=True,
        timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", errors="replace").strip() or "Git status did not complete")
    unrecoverable = []
    entries = [entry for entry in result.stdout.decode("utf-8").split("\0") if entry]
    index = 0
    while index < len(entries):
        entry = entries[index]
        unrecoverable.append(entry[3:])
        # A rename record carries its original path as the following entry.
        index += 2 if entry[:2].strip().startswith("R") else 1
    return sorted(set(unrecoverable))


def apply_upgrade(plan: UpgradePlan) -> dict[str, Any]:
    """Replace managed files in place after revalidation; nothing else changes."""
    options = plan.options
    if plan.actions and any(_sha(path) != identity for path, identity in plan.inputs.items() if path.exists()):
        raise ValueError("Upgrade inputs changed; inspect a new preview before applying")
    fresh_project, target = _selected_application(options)
    if fresh_project != plan.project or target != plan.target:
        raise ValueError("The selected project changed; inspect a new preview before applying")
    changed = [action.path for action in plan.changes if action.action in {"replace", "remove"}]
    added = [action.path for action in plan.changes if action.action == "add"]
    blocking = _local_work(target, changed)
    if blocking:
        raise LocalWorkError(
            "Managed paths hold uncommitted local work that Git history cannot recover: " + ", ".join(blocking)
        )
    for name in added:
        if (target / name).exists():
            raise ValueError("A managed path appeared after the preview: " + name)
    written: list[str] = []
    removed: list[str] = []
    for action in plan.changes:
        path = target / action.path
        if action.action == "remove":
            path.unlink()
            removed.append(action.path)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        staged = Path(temporary)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(plan.writes[action.path])
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(staged, path)
        finally:
            staged.unlink(missing_ok=True)
        written.append(action.path)
    if any((target / name).read_bytes() != plan.writes[name] for name in written):
        raise ValueError("Managed files changed before readback; inspect the application")
    return {
        "status": "applied" if written or removed else "current",
        "target": str(target),
        "written": written,
        "removed": removed,
        "preserved_entries": sum(action.preserved_entries for action in plan.actions),
        "canonical_writes": 0,
        "commits": 0,
    }


def recovery_plan(options: UpgradeOptions) -> dict[str, Any]:
    """Report managed paths whose current bytes differ from the application's committed history.

    Committed managed files are restorable from HEAD, including the artifact-boundary
    registry the upgrade merges entries into. Derived projections that the
    application ignores in Git are regenerated by ``apply_upgrade`` instead; they
    are reported, never deleted.
    """
    _project, target = _selected_application(options)
    plan = plan_upgrade(options)
    managed_paths = set(plan.writes) | set(plan.removes)
    if (target / ISOLATION_REGISTRY).is_file():
        # The upgrade merges managed entries into the registry; once merged, the next plan no longer writes it, so
        # recovery names it explicitly: its committed bytes are the recovery point like any other managed file.
        managed_paths.add(ISOLATION_REGISTRY)
    managed = sorted(managed_paths)
    if not _git(target, "rev-parse", "--verify", "HEAD", required=False):
        return {"target": str(target), "head": None, "restore": [], "derived": managed}
    head = _git(target, "rev-parse", "HEAD")
    tracked = (
        set(_git(target, "ls-tree", "-r", "--name-only", "HEAD", "--", *managed).splitlines()) if managed else set()
    )
    differing = set(_local_work(target, managed))
    return {
        "target": str(target),
        "head": head,
        "restore": sorted(path for path in differing if path in tracked),
        "derived": sorted(path for path in managed if path not in tracked),
    }


def recover(options: UpgradeOptions) -> dict[str, Any]:
    """Restore committed managed paths from HEAD; application-owned files are untouched."""
    plan = recovery_plan(options)
    target = Path(plan["target"])
    if plan["head"] is None:
        raise ValueError("The application has no committed history to recover from")
    if plan["restore"]:
        _git(target, "checkout", "HEAD", "--", *plan["restore"])
    return {**plan, "status": "restored" if plan["restore"] else "current", "canonical_writes": 0, "commits": 0}
