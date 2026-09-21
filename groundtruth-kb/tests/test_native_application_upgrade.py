"""Native application upgrade and recovery over the host baseline and registered repository.

Retained duties of the retired registry/receipt upgrade engine: preview by
default, staged replacement of managed files only, malformed input refused
before any effect, interleaved unmanaged hook registrations preserved, retired
outputs removed and never resurrected, recovery from the application's own Git
history. No receipts, no implicit commit, no canonical writes.

Cache declaration duty (entry 124, N-31 follow-up): a registry that predates the
scaffold's ``.groundtruth-chroma`` declaration gains exactly that entry so the
confined ``chroma regenerate`` accepts the cache again; an entry already present
is preserved byte-for-byte; a conflicting declaration is refused, never
reclassified.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

from groundtruth_kb.isolation.app_root_minimization import validate_app_root_minimization
from groundtruth_kb.project.application_upgrade import (
    LocalWorkError,
    MalformedInputError,
    UpgradeOptions,
    apply_upgrade,
    plan_upgrade,
    projected_harnesses,
    recover,
    recovery_plan,
)
from groundtruth_kb.project.chroma import CacheTargetError, regenerate

# Every case runs for a host at a plain location and at a nested location with a space (M04 second host location).
pytestmark = [
    pytest.mark.integration,
    pytest.mark.timeout(300),
    pytest.mark.parametrize("native_app_authority", ["first-host", "relocated location/second host"], indirect=True),
]
HOOK = ".githooks/reference-transaction"
SETTINGS = ".claude/settings.json"
CACHE = ".groundtruth-chroma"
# The scaffold's declaration of the disposable search cache (RUNTIME_TOP_LEVEL_ENTRIES): what an upgraded registry
# must carry for the confined regeneration to accept the cache.
CACHE_ENTRY = {
    "name": CACHE,
    "type": "DIR",
    "classification": "generated_output",
    "purpose": "Derived search cache rebuilt from the configured authority",
}


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def _options(host, name="Alpha", harnesses=()):
    return UpgradeOptions(
        application=name,
        project_id="PROJECT-" + name,
        gt_kb_root=host.host,
        authority_url=host.client.url,
        harnesses=tuple(harnesses),
    )


def _initialized(host, name="Alpha", harness="claude"):
    """An initialized, committed application with one projected harness."""
    host.stage_baseline()
    target = host.scaffold(name, harnesses=(harness,))
    (target / "README.md").write_text("# Alpha App\n\nAdopter customization kept through upgrades.\n", encoding="utf-8")
    head = host.commit_all(target)
    return target, head


def _cli(host, *args: str, expect: int = 0):
    result = host.invoke(
        "project", "upgrade", "Alpha", "--project-id", "PROJECT-Alpha", "--host-root", str(host.host), *args
    )
    assert result.exit_code == expect, result.output
    return json.loads(result.output) if "--json" in args else result.output


def test_fresh_application_is_current_and_bare_invocation_previews(native_application) -> None:
    target, head = _initialized(native_application)
    assert projected_harnesses(native_application.host, target) == ("claude",)
    plan = plan_upgrade(_options(native_application))
    assert plan.harnesses == ("claude",) and plan.changes == ()
    assert {action.action for action in plan.actions} == {"unchanged"}
    preview = _cli(native_application, "--json")
    assert preview["status"] == "preview" and preview["changes"] == 0
    assert preview["canonical_writes"] == 0 and preview["commits"] == 0
    assert _git(target, "rev-parse", "HEAD") == head and _git(target, "status", "--porcelain") == ""
    usage = native_application.invoke(
        "project",
        "upgrade",
        "Alpha",
        "--project-id",
        "PROJECT-Alpha",
        "--host-root",
        str(native_application.host),
        "--apply",
        "--recover",
    )
    assert usage.exit_code == 2 and "mutually exclusive" in usage.output


def test_upgrade_registers_the_managed_top_level_entries_it_installs(native_application) -> None:
    """A registry that predates the managed hook and projections gains their entries and passes the root check."""
    import json

    from groundtruth_kb.isolation.app_root_minimization import validate_app_root_minimization

    target, _head = _initialized(native_application)
    registry = target / ".gtkb-app-isolation.json"
    payload = json.loads(registry.read_text(encoding="utf-8"))
    own = {
        "name": "vendor-notes.md",
        "type": "FILE",
        "classification": "authoritative_input",
        "purpose": "Application-owned",
    }
    (target / "vendor-notes.md").write_text("owned\n", encoding="utf-8")
    payload["top_level_artifacts"] = [
        e for e in payload["top_level_artifacts"] if e["name"] not in {".githooks", ".claude"}
    ] + [own]
    registry.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    _git(target, "add", "-A")
    _git(target, "commit", "-qm", "Registry from before the managed hook and projections")
    assert not validate_app_root_minimization(target, project_root=native_application.host).ok
    preview = _cli(native_application, "--json")
    assert [(a["path"], a["action"]) for a in preview["actions"] if a["action"] != "unchanged"] == [
        (".gtkb-app-isolation.json", "replace")
    ]
    applied = _cli(native_application, "--apply", "--json")
    assert applied["written"] == [".gtkb-app-isolation.json"] and applied["commits"] == 0
    merged = json.loads(registry.read_text(encoding="utf-8"))["top_level_artifacts"]
    names = [e["name"] for e in merged]
    assert own in merged and names == sorted(names, key=str.casefold)
    assert {e["name"]: e["classification"] for e in merged if e["name"] in {".githooks", ".claude"}} == {
        ".githooks": "generated_output",
        ".claude": "generated_output",
    }
    assert validate_app_root_minimization(target, project_root=native_application.host).ok
    assert _cli(native_application, "--json")["changes"] == 0
    registry.write_text("{not json", encoding="utf-8")
    refused = _cli(native_application, "--json", expect=1)
    assert refused["status"] == "refused" and registry.read_text(encoding="utf-8") == "{not json"


def test_repaired_registry_is_recoverable_before_it_is_committed(native_application) -> None:
    """Recovery restores the registry the upgrade merged entries into; HEAD and application-owned files stay."""
    target, _head = _initialized(native_application)
    registry = target / ".gtkb-app-isolation.json"
    payload = json.loads(registry.read_text(encoding="utf-8"))
    payload["top_level_artifacts"] = [
        e for e in payload["top_level_artifacts"] if e["name"] not in {".githooks", ".claude"}
    ] + [{"name": "vendor-notes.md", "type": "FILE", "classification": "authoritative_input", "purpose": "Owned"}]
    (target / "vendor-notes.md").write_text("owned\n", encoding="utf-8")
    registry.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    _git(target, "add", "-A")
    _git(target, "commit", "-qm", "Registry from before the managed hook and projections")
    committed = _git(target, "rev-parse", "HEAD")
    committed_registry = registry.read_bytes()
    host_registry = (native_application.host / "applications" / "registry.toml").read_bytes()
    assert _cli(native_application, "--apply", "--json")["written"] == [".gtkb-app-isolation.json"]
    assert registry.read_bytes() != committed_registry and _git(target, "rev-parse", "HEAD") == committed
    assert recovery_plan(_options(native_application))["restore"] == [".gtkb-app-isolation.json"]
    restored = _cli(native_application, "--recover", "--json")
    assert restored["status"] == "restored" and restored["restore"] == [".gtkb-app-isolation.json"]
    assert registry.read_bytes() == committed_registry
    assert _git(target, "rev-parse", "HEAD") == committed and _git(target, "status", "--porcelain") == ""
    assert (target / "vendor-notes.md").read_text(encoding="utf-8") == "owned\n"
    assert (native_application.host / "applications" / "registry.toml").read_bytes() == host_registry
    assert _cli(native_application, "--recover", "--json")["status"] == "current"
    assert _cli(native_application, "--json")["changes"] == 1, "the repair is offered again after recovery"


def test_missing_managed_hook_is_restored_without_receipts_or_commits(native_application) -> None:
    target, head = _initialized(native_application)
    (target / HOOK).unlink()
    _git(target, "commit", "-qam", "Remove the hook by mistake")
    preview = _cli(native_application, "--json")
    assert [(a["path"], a["action"]) for a in preview["actions"] if a["action"] != "unchanged"] == [(HOOK, "add")]
    assert not (target / HOOK).exists(), "preview has no effect"
    applied = _cli(native_application, "--apply", "--json")
    assert applied["status"] == "applied" and applied["written"] == [HOOK] and applied["removed"] == []
    assert (target / HOOK).read_bytes() == (native_application.host / HOOK).read_bytes()
    assert not (target / ".claude/upgrade-receipts").exists()
    assert _git(target, "log", "--oneline").count("\n") == 1, "no implicit commit"
    assert "Adopter customization" in (target / "README.md").read_text(encoding="utf-8")


def test_drifted_managed_file_needs_recoverable_history_before_replacement(native_application) -> None:
    target, head = _initialized(native_application)
    (target / HOOK).write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    with pytest.raises(LocalWorkError, match="uncommitted local work"):
        apply_upgrade(plan_upgrade(_options(native_application)))
    assert (target / HOOK).read_text(encoding="utf-8") == "#!/bin/sh\nexit 0\n"
    refused = _cli(native_application, "--apply", "--json", expect=2)
    assert refused["error"]["code"] == "checkout_has_local_work"
    committed = native_application.commit_all(target, "Local hook edit")
    applied = _cli(native_application, "--apply", "--json")
    assert applied["written"] == [HOOK]
    assert (target / HOOK).read_bytes() == (native_application.host / HOOK).read_bytes()
    assert _git(target, "diff", "--name-only", "HEAD").splitlines() == [HOOK]
    assert _git(target, "rev-parse", "HEAD") == committed
    restored = recover(_options(native_application))
    assert restored["status"] == "restored" and restored["restore"] == [HOOK]
    assert (target / HOOK).read_text(encoding="utf-8") == "#!/bin/sh\nexit 0\n"
    assert _git(target, "status", "--porcelain") == ""
    again = _cli(native_application, "--recover", "--json")
    assert again["status"] == "current" and again["restore"] == []


def test_interleaved_unmanaged_registrations_survive_a_baseline_change(native_application) -> None:
    target, _head = _initialized(native_application)
    settings_path = target / SETTINGS
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    custom_group = {"matcher": "Write", "hooks": [{"type": "command", "command": "python tools/adopter_lint.py"}]}
    settings["hooks"]["PreToolUse"].insert(1, custom_group)
    settings["hooks"]["Notification"] = [{"hooks": [{"type": "command", "command": "python tools/notify.py"}]}]
    settings["permissions"] = {"allow": ["Bash(python tools/*)"]}
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    manifest = native_application.host / ".harness-baseline-configuration/hooks/manifest.toml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace("timeout_seconds = 5\n", "timeout_seconds = 7\n", 1),
        encoding="utf-8",
    )
    plan = plan_upgrade(_options(native_application))
    settings_action = next(action for action in plan.actions if action.path == SETTINGS)
    assert settings_action.action == "replace" and settings_action.preserved_entries == 2
    result = apply_upgrade(plan)
    assert SETTINGS in result["written"] and result["preserved_entries"] == 2
    merged = json.loads(settings_path.read_text(encoding="utf-8"))
    assert merged["permissions"] == {"allow": ["Bash(python tools/*)"]}
    assert merged["hooks"]["Notification"] == settings["hooks"]["Notification"]
    pre = merged["hooks"]["PreToolUse"]
    assert custom_group in pre
    managed = [group for group in pre if group != custom_group]
    assert managed and all(
        ".harness-baseline-configuration/hooks" in json.dumps(group) or "scripts/" in json.dumps(group)
        for group in managed
    )
    assert any('"timeout": 7' in json.dumps(group) for group in managed)
    assert pre.count(custom_group) == 1 and len(pre) == len(managed) + 1
    assert plan_upgrade(_options(native_application)).changes == ()


def test_malformed_registration_refuses_before_any_effect(native_application) -> None:
    target, _head = _initialized(native_application)
    (target / SETTINGS).write_text("{not json", encoding="utf-8")
    (target / HOOK).unlink()
    _git(target, "commit", "-qam", "Drop the hook")
    with pytest.raises(MalformedInputError):
        plan_upgrade(_options(native_application))
    refused = _cli(native_application, "--apply", "--json", expect=4)
    assert refused["error"]["code"] == "malformed_input"
    assert not (target / HOOK).exists(), "nothing is written when an input is malformed"
    assert (target / SETTINGS).read_text(encoding="utf-8") == "{not json"


def test_retired_projection_output_is_removed_and_never_resurrected(native_application) -> None:
    target, _head = _initialized(native_application)
    manifest_path = target / ".claude/.projection-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    retired = target / ".claude/hooks/workstream-focus.py"
    retired.parent.mkdir(parents=True, exist_ok=True)
    retired.write_text("# retired hook that a previous projection produced\n", encoding="utf-8")
    manifest["paths"].append(".claude/hooks/workstream-focus.py")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    plan = plan_upgrade(_options(native_application))
    assert [(a.path, a.action) for a in plan.changes if a.action == "remove"] == [
        (".claude/hooks/workstream-focus.py", "remove")
    ]
    result = apply_upgrade(plan)
    assert result["removed"] == [".claude/hooks/workstream-focus.py"] and not retired.exists()
    assert plan_upgrade(_options(native_application)).changes == ()
    assert not retired.exists()


def test_uninitialized_or_foreign_application_is_refused(native_application) -> None:
    native_application.stage_baseline()
    with pytest.raises(ValueError, match="gt project init"):
        plan_upgrade(_options(native_application, "Beta"))
    target, _head = _initialized(native_application)
    with pytest.raises(ValueError, match="registered for this application"):
        plan_upgrade(UpgradeOptions("Alpha", "PROJECT-Beta", native_application.host, native_application.client.url))
    plan = recovery_plan(_options(native_application))
    assert plan["restore"] == [] and SETTINGS in plan["derived"]
    assert (target / HOOK).is_file()


# --- cache declaration (entry 124) ----------------------------------------------------------------------------------


def _entries(target: Path) -> list[dict]:
    return json.loads((target / ".gtkb-app-isolation.json").read_text(encoding="utf-8"))["top_level_artifacts"]


def _commit_registry(target: Path, entries: list[dict], message: str) -> bytes:
    """Commit the application's registry with exactly ``entries`` and return the committed bytes."""
    registry = target / ".gtkb-app-isolation.json"
    payload = {**json.loads(registry.read_text(encoding="utf-8")), "top_level_artifacts": entries}
    registry.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    _git(target, "add", "-A")
    _git(target, "commit", "-qm", message)
    return registry.read_bytes()


def test_registry_that_predates_the_cache_declaration_gains_exactly_that_entry(native_application) -> None:
    """A registry lacking the scaffold's cache entry gains it and nothing else; regeneration then accepts the cache."""
    target, _head = _initialized(native_application)
    registry = target / ".gtkb-app-isolation.json"
    scaffolded = registry.read_bytes()
    predating = [entry for entry in _entries(target) if entry["name"] != CACHE]
    assert len(predating) == len(_entries(target)) - 1, "the scaffold declares the cache"
    committed = _commit_registry(target, predating, "Registry from before the search cache was declared")
    with pytest.raises(CacheTargetError, match=re.escape(f"top-level entry '{CACHE}' is not declared")):
        regenerate(target, dry_run=True)
    preview = _cli(native_application, "--json")
    assert [(a["path"], a["action"]) for a in preview["actions"] if a["action"] != "unchanged"] == [
        (".gtkb-app-isolation.json", "replace")
    ]
    assert registry.read_bytes() == committed, "preview has no effect"
    applied = _cli(native_application, "--apply", "--json")
    assert applied["written"] == [".gtkb-app-isolation.json"] and applied["commits"] == 0
    merged = _entries(target)
    assert [entry for entry in merged if entry["name"] != CACHE] == predating
    assert [entry for entry in merged if entry["name"] == CACHE] == [CACHE_ENTRY]
    assert registry.read_bytes() == scaffolded, "the merged registry is byte-identical to the scaffold's declaration"
    assert validate_app_root_minimization(target, project_root=native_application.host).ok
    assert _cli(native_application, "--json")["changes"] == 0
    accepted = regenerate(target, dry_run=True)
    assert accepted.status == "would-regenerate" and accepted.chroma_path == (target / CACHE).resolve()


def test_existing_cache_declaration_is_preserved_byte_for_byte(native_application) -> None:
    """A declared cache is never rewritten for its own sake; a rewrite for other entries carries it unchanged."""
    target, _head = _initialized(native_application)
    registry = target / ".gtkb-app-isolation.json"
    scaffolded = registry.read_bytes()
    assert [entry for entry in _entries(target) if entry["name"] == CACHE] == [CACHE_ENTRY]
    assert plan_upgrade(_options(native_application)).changes == () and registry.read_bytes() == scaffolded
    own = {**CACHE_ENTRY, "purpose": "Search cache; purpose text maintained by the application"}
    edited = [own if entry["name"] == CACHE else entry for entry in _entries(target) if entry["name"] != ".githooks"]
    _commit_registry(target, edited, "Own cache purpose; registry from before the managed hook was declared")
    block = "\n".join("    " + line for line in json.dumps(own, indent=2).splitlines())
    assert block in registry.read_text(encoding="utf-8")
    preview = _cli(native_application, "--json")
    assert [(a["path"], a["action"]) for a in preview["actions"] if a["action"] != "unchanged"] == [
        (".gtkb-app-isolation.json", "replace")
    ]
    applied = _cli(native_application, "--apply", "--json")
    assert applied["written"] == [".gtkb-app-isolation.json"]
    merged = _entries(target)
    assert [list(entry.items()) for entry in merged if entry["name"] == CACHE] == [list(own.items())]
    assert block in registry.read_text(encoding="utf-8"), "the application's cache entry is carried byte-for-byte"
    assert [entry for entry in merged if entry["name"] != ".githooks"] == edited
    assert {entry["name"] for entry in merged} == {entry["name"] for entry in edited} | {".githooks"}
    assert _cli(native_application, "--json")["changes"] == 0


@pytest.mark.parametrize(
    "declared", [("DIR", "authoritative_input"), ("FILE", "generated_output")], ids=["reclassified", "retyped"]
)
def test_conflicting_cache_declaration_is_refused_not_reclassified(native_application, declared) -> None:
    """A cache entry declared with another type or classification is reported as a conflict; nothing is written."""
    artifact_type, classification = declared
    target, _head = _initialized(native_application)
    registry = target / ".gtkb-app-isolation.json"
    conflicting = [
        {**entry, "type": artifact_type, "classification": classification} if entry["name"] == CACHE else entry
        for entry in _entries(target)
    ]
    (target / HOOK).unlink()
    committed = _commit_registry(target, conflicting, "Cache declared as something other than the disposable cache")
    expected = f".gtkb-app-isolation.json declares {CACHE} as {artifact_type} {classification}, not the disposable"
    with pytest.raises(ValueError, match=re.escape(expected)) as info:
        plan_upgrade(_options(native_application))
    assert not isinstance(info.value, (MalformedInputError, LocalWorkError))
    refused = _cli(native_application, "--apply", "--json", expect=1)
    assert refused["status"] == "refused" and refused["error"]["code"] == "invalid_upgrade"
    assert expected in refused["error"]["message"] and "reconcile it first" in refused["error"]["message"]
    assert registry.read_bytes() == committed and not (target / HOOK).exists(), "nothing is written for a conflict"
    assert _git(target, "status", "--porcelain") == ""
    assert [entry for entry in _entries(target) if entry["name"] == CACHE] == [
        {**CACHE_ENTRY, "type": artifact_type, "classification": classification}
    ]
