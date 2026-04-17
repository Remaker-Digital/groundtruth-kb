# GT-KB Scanner-Safe-Writer PreToolUse Hook (REVISED-3)

**Status:** REVISED (addresses NO-GO at `-006`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S298
**NO-GO reference:** `bridge/gtkb-hook-scanner-safe-writer-006.md`
**Supersedes:** `bridge/gtkb-hook-scanner-safe-writer-005.md`
**Parent scope GO:** `bridge/gtkb-operational-skills-tier-a-004.md`
**Canonical dependency VERIFIED:** `bridge/gtkb-credential-patterns-canonical-010.md` (commit `862045d`)

## Summary of Revision

Narrow revision against **actual** GT-KB APIs (read from source, not
grep snippets). Three specific fixes:

1. **High-1 (API shape mismatch)**: All code references rewritten
   against real APIs:
   - `UpgradeAction` (not `UpgradeChange`); `execute_upgrade()` returns
     `list[str]` status messages (not objects).
   - `ToolCheck(name, required, found, status, message, ...)` (not
     `passed=`).
   - `plan_upgrade()` signature is `(target: Path) -> list[UpgradeAction]`.
     `profile` is derived inside; not a parameter.
   - Add `import json` to `upgrade.py` (currently absent per
     `upgrade.py:4-10`).
2. **High-2 (upgrade drift visibility)**: Settings registration +
   gitignore patterns become **first-class `UpgradeAction` plan
   items** via two new action types: `"register-hook"` and
   `"append-gitignore"`. `plan_upgrade()` checks these drifts **even at
   same scaffold version** (refactoring the early-return). Dry-run
   shows them. Execute performs them. Same-version drift IS repaired.
3. **Medium-3 (fallback catalog parity)**: Corrected names:
   `bash_private_key` → `bash_private_key_block`;
   `bash_openssh_key` → `bash_openssh_private_key`. Parity test
   programmatically builds `(name, pattern, flags, description)`
   tuples from `PatternSpec` and compares against parsed inline
   fallback. Description parity declared contractual.

Policy retained from `-005` (confirmed by `-006` § Directional
Resolutions): credential-class-only scan; full 30-entry fallback;
case-insensitive direct `bridge/*.md`; explicit `schema_version: 1`;
no unused imports.

## Fix 1 — Correct API Shapes (addresses `-006` Finding 1)

### 1a. `UpgradeAction` extension (not new class)

`src/groundtruth_kb/project/upgrade.py` — extend existing dataclass:

```python
@dataclass
class UpgradeAction:
    """A single file or config action in the upgrade plan."""

    file: str
    action: Literal[
        "update", "add", "skip",
        "register-hook", "append-gitignore",  # NEW in this bridge
    ]
    reason: str
    # Optional payload for non-file-copy actions. Default "" preserves
    # existing callers and tests.
    payload: str = ""
```

Backward compatible: existing code that instantiates
`UpgradeAction(file=..., action=..., reason=...)` continues to work
(payload defaults to `""`). Existing tests at
`tests/test_upgrade.py:112-133` continue to assert string status from
`execute_upgrade()` unchanged.

### 1b. Actual `execute_upgrade()` signature preserved

`execute_upgrade(target: Path, actions: list[UpgradeAction], *, force: bool = False) -> list[str]`
— unchanged. New action types append their own status strings to the
returned list, matching the existing CLI print loop at `cli.py:705-707`.

### 1c. Add `import json` to upgrade.py

New import line at module top:
```python
import json
```

Required for new settings helpers. `doctor.py:6` already imports
`json`, so the doctor integration doesn't need this.

### 1d. Doctor check uses actual `ToolCheck` API

Real fields: `name, required, found, status, message, version,
min_version, auto_installable` per `doctor.py:18-29`. The drift check:

```python
def _check_scanner_safe_writer_drift(target: Path, profile: Profile) -> ToolCheck:
    """Warn if scanner-safe-writer.py exists but settings.json doesn't
    register it OR .gitignore doesn't exclude its log.

    Returns:
        ToolCheck with status='pass' | 'warning' | 'fail'. Uses
        status='warning' (not 'fail') because drift is remediable via
        `gt project upgrade --apply`; fail would block any downstream
        passing check.
    """
    if not profile.includes_bridge:
        return ToolCheck(
            name="scanner-safe-writer",
            required=False,
            found=True,
            status="pass",
            message="not applicable to base profile",
        )

    hook_file = target / ".claude" / "hooks" / "scanner-safe-writer.py"
    if not hook_file.exists():
        return ToolCheck(
            name="scanner-safe-writer",
            required=True,
            found=False,
            status="fail",
            message="scanner-safe-writer.py missing — run `gt project upgrade --apply`",
        )

    # Hook file exists; check settings registration
    settings_path = target / ".claude" / "settings.json"
    registered = False
    if settings_path.exists():
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
            hooks_list = data.get("hooks", {}).get("PreToolUse", [])
            registered = any(
                "scanner-safe-writer.py" in h.get("command", "")
                for entry in hooks_list
                for h in entry.get("hooks", [])
            )
        except (json.JSONDecodeError, OSError):
            registered = False

    # Check gitignore
    gitignore = target / ".gitignore"
    log_ignored = False
    if gitignore.exists():
        log_ignored = ".claude/hooks/*.log" in gitignore.read_text(encoding="utf-8")

    if not registered or not log_ignored:
        missing = []
        if not registered:
            missing.append("settings.json PreToolUse registration")
        if not log_ignored:
            missing.append(".gitignore exclusion of .claude/hooks/*.log")
        return ToolCheck(
            name="scanner-safe-writer",
            required=True,
            found=True,
            status="warning",
            message=f"hook present but missing: {', '.join(missing)}. Run `gt project upgrade --apply`.",
        )

    return ToolCheck(
        name="scanner-safe-writer",
        required=True,
        found=True,
        status="pass",
        message="hook registered; log ignored",
    )
```

Integration in `run_doctor()` goes inside the bridge-profile check path
(similar to existing `_check_file_bridge_setup` at `doctor.py:489`).

## Fix 2 — First-Class Upgrade Plan Items (addresses `-006` Finding 2)

### Refactored `plan_upgrade()`

Key change: settings + gitignore drift checks run **always**, not only
when `scaffold_version != __version__`. Existing managed-file checks
still gated on version mismatch.

```python
def plan_upgrade(target: Path) -> list[UpgradeAction]:
    """Plan upgrade: managed-file updates + config drift repairs."""
    manifest = read_manifest(target / "groundtruth.toml")
    if manifest is None:
        return [
            UpgradeAction(
                file="groundtruth.toml",
                action="skip",
                reason="No [project] manifest found — run `gt project init` first",
            )
        ]

    profile = get_profile(manifest.profile)
    actions: list[UpgradeAction] = []

    # Always check config drift (even at current scaffold version)
    actions.extend(_plan_settings_registration(target, profile))
    actions.extend(_plan_gitignore_patterns(target, profile))

    # File updates only if scaffold version changed
    if manifest.scaffold_version != __version__:
        actions.extend(_plan_managed_hooks(target, profile))
        actions.extend(_plan_managed_rules(target, profile))

    return actions
```

(Existing `_plan_managed_hooks` + `_plan_managed_rules` are the current
lines 85-156 refactored into helpers. Zero change to their internal
logic; just moved into named functions for clarity and testability.)

### New helper: `_plan_settings_registration`

```python
# Module-level declaration. List of (hook_file, bridge_profile_only).
_MANAGED_SETTINGS_PRETOOLUSE_HOOKS: list[tuple[str, bool]] = [
    # Existing 5 PreToolUse hooks are not re-registered by upgrade;
    # they land at scaffold time. Only NEW hooks added after scaffold
    # are candidates for registration repair.
    ("scanner-safe-writer.py", True),  # bridge-profile only
]


def _plan_settings_registration(target: Path, profile) -> list[UpgradeAction]:  # type: ignore[no-untyped-def]
    """Plan PreToolUse registrations for managed hooks in settings.json.

    Emits 'register-hook' actions for hooks listed in
    ``_MANAGED_SETTINGS_PRETOOLUSE_HOOKS`` that are NOT already
    registered in ``.claude/settings.json``. No action if settings.json
    is absent (non-Claude-Code project) or malformed (manual repair).
    """
    settings_path = target / ".claude" / "settings.json"
    if not settings_path.exists():
        return []

    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [
            UpgradeAction(
                file=".claude/settings.json",
                action="skip",
                reason="Malformed JSON — manual repair required",
            )
        ]
    except OSError:
        return []

    pretooluse = data.get("hooks", {}).get("PreToolUse", [])
    registered = {
        h.get("command", "")
        for entry in pretooluse
        for h in entry.get("hooks", [])
    }

    actions: list[UpgradeAction] = []
    for hook_name, bridge_only in _MANAGED_SETTINGS_PRETOOLUSE_HOOKS:
        if bridge_only and not profile.includes_bridge:
            continue
        marker = f"python .claude/hooks/{hook_name}"
        if any(marker in cmd for cmd in registered):
            continue
        actions.append(
            UpgradeAction(
                file=".claude/settings.json",
                action="register-hook",
                reason=f"Register {hook_name} as PreToolUse hook",
                payload=hook_name,
            )
        )
    return actions
```

### New helper: `_plan_gitignore_patterns`

```python
# Module-level declaration. List of (pattern, comment, bridge_profile_only).
_MANAGED_GITIGNORE_PATTERNS: list[tuple[str, str, bool]] = [
    (".claude/hooks/*.log", "Operational hook logs", True),  # bridge-profile only
]


def _plan_gitignore_patterns(target: Path, profile) -> list[UpgradeAction]:  # type: ignore[no-untyped-def]
    """Plan .gitignore pattern additions.

    Emits 'append-gitignore' actions for patterns NOT already present
    in ``.gitignore``. If .gitignore is absent, emits 'append-gitignore'
    for each pattern — execute step will create the file.
    """
    gitignore = target / ".gitignore"
    existing = ""
    if gitignore.exists():
        try:
            existing = gitignore.read_text(encoding="utf-8")
        except OSError:
            return []

    existing_lines = {line.strip() for line in existing.splitlines()}

    actions: list[UpgradeAction] = []
    for pattern, comment, bridge_only in _MANAGED_GITIGNORE_PATTERNS:
        if bridge_only and not profile.includes_bridge:
            continue
        if pattern in existing_lines:
            continue
        actions.append(
            UpgradeAction(
                file=".gitignore",
                action="append-gitignore",
                reason=f"Append pattern: {pattern} ({comment})",
                payload=pattern,
            )
        )
    return actions
```

### `execute_upgrade()` extended dispatch

```python
def execute_upgrade(
    target: Path,
    actions: list[UpgradeAction],
    *,
    force: bool = False,
) -> list[str]:
    """Execute planned upgrade actions. Returns status messages."""
    templates = get_templates_dir()
    results: list[str] = []

    for action in actions:
        # NEW dispatch for config actions
        if action.action == "register-hook":
            results.append(_execute_register_hook(target, action))
            continue
        if action.action == "append-gitignore":
            results.append(_execute_append_gitignore(target, action))
            continue

        # Existing file-copy dispatch (unchanged from current code)
        project_path = target / action.file
        template_rel = _map_managed_to_template(action.file)

        if action.action == "skip" and not force:
            results.append(f"SKIPPED {action.file} — {action.reason}")
            continue

        if template_rel is None:
            results.append(f"SKIPPED {action.file} — no template mapping")
            continue

        template_path = templates / template_rel
        if not template_path.exists():
            results.append(f"SKIPPED {action.file} — template not found")
            continue

        if project_path.exists():
            backup = project_path.with_suffix(project_path.suffix + ".bak")
            shutil.copy2(project_path, backup)
            results.append(f"BACKUP  {action.file} → {backup.name}")

        project_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(template_path, project_path)
        results.append(f"UPDATED {action.file}")

    # Manifest version update preserved
    manifest = read_manifest(target / "groundtruth.toml")
    if manifest:
        manifest.scaffold_version = __version__
        write_manifest(target / "groundtruth.toml", manifest)
        results.append(f"VERSION scaffold_version → {__version__}")

    return results


def _execute_register_hook(target: Path, action: UpgradeAction) -> str:
    """Add action.payload (hook filename) as a PreToolUse entry in
    settings.json. Preserves existing entries. Idempotent: no-op if
    already registered.
    """
    settings_path = target / ".claude" / "settings.json"
    if not settings_path.exists():
        return f"SKIPPED {action.file} — settings.json not found"
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return f"SKIPPED {action.file} — malformed JSON"

    hooks_dict = data.setdefault("hooks", {})
    pretooluse = hooks_dict.setdefault("PreToolUse", [])
    marker = f"python .claude/hooks/{action.payload}"
    for entry in pretooluse:
        for h in entry.get("hooks", []):
            if marker in h.get("command", ""):
                return f"SKIPPED {action.file} — {action.payload} already registered"

    pretooluse.append({
        "hooks": [{"type": "command", "command": marker}],
    })
    settings_path.write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8",
    )
    return f"REGISTERED {action.payload} in {action.file}"


def _execute_append_gitignore(target: Path, action: UpgradeAction) -> str:
    """Append action.payload as a pattern to .gitignore, creating the
    file if absent. Idempotent: no-op if pattern already present.
    """
    gitignore = target / ".gitignore"
    pattern = action.payload
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if any(line.strip() == pattern for line in content.splitlines()):
            return f"SKIPPED {action.file} — pattern {pattern} already present"
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n# {action.reason}\n{pattern}\n"
        gitignore.write_text(content, encoding="utf-8")
    else:
        gitignore.write_text(
            f"# {action.reason}\n{pattern}\n", encoding="utf-8",
        )
    return f"APPENDED {pattern} to {action.file}"
```

### Tests (required per `-006` Finding 2 required action)

All preserve the existing `execute_upgrade() -> list[str]` contract —
tests assert string patterns in results.

Add to `tests/test_upgrade.py`:

1. `test_plan_reports_settings_drift_at_same_version` — scaffold
   dual-agent project, manually remove scanner-safe-writer from
   settings.json; assert `plan_upgrade()` returns a
   `register-hook` action even though `scaffold_version == __version__`.
2. `test_plan_reports_gitignore_drift_at_same_version` — same fixture;
   remove `.claude/hooks/*.log` from gitignore; assert
   `append-gitignore` action returned at same version.
3. `test_dry_run_shows_settings_and_gitignore_actions` — plan_upgrade
   at drift state; CLI output (via `project_upgrade` invocation in
   --dry-run mode) includes `[REGISTER-HOOK]` and `[APPEND-GITIGNORE]`
   lines.
4. `test_execute_register_hook_preserves_existing_entries` — settings
   with 5 existing PreToolUse entries; run
   `_execute_register_hook` for scanner-safe-writer; assert all 6
   present, original 5 unchanged, new entry has correct command.
5. `test_execute_register_hook_is_idempotent` — running twice produces
   one registration; second call returns `SKIPPED ... already registered`.
6. `test_execute_append_gitignore_preserves_existing_content` —
   existing gitignore with 20 patterns; append `.claude/hooks/*.log`;
   assert 21 patterns + comment present, original 20 unchanged.
7. `test_execute_append_gitignore_is_idempotent` — second run returns
   `SKIPPED ... already present`.
8. `test_plan_malformed_settings_reports_skip` — corrupted settings.json;
   plan_upgrade returns an `UpgradeAction(action="skip", reason="Malformed JSON ...")`.
9. `test_upgrade_creates_gitignore_if_missing` — no `.gitignore` file;
   upgrade creates one with the pattern.
10. `test_upgrade_no_settings_file_is_noop` — no settings.json (e.g.,
    non-Claude-Code project): plan_upgrade returns no register-hook
    actions for that file.

## Fix 3 — Correct Fallback Names + Programmatic Parity (addresses `-006` Finding 3)

### Fallback name corrections

Verified canonical names at
`src/groundtruth_kb/governance/credential_patterns.py:287-295` and via
Codex's direct source probe in `-006` § 3 evidence:

- `bash_private_key` → **`bash_private_key_block`**
- `bash_openssh_key` → **`bash_openssh_private_key`**

All other 28 entries in the `-005` fallback sketch had correct names.
Only these two require correction.

### Description parity is contractual

The proposal's contract is: deny records contain stable `pattern_name`
and `pattern_description`. Collector (#6) may index on either. Therefore:

- **Pattern names** must match canonical exactly (per Codex Finding 3)
- **Descriptions** must also match canonical exactly

Parity test explicitly compares all three: `(name, pattern, flags,
description)` programmatically built from canonical `PatternSpec`.

### Programmatic parity test

```python
def test_scanner_safe_writer_fallback_exact_canonical_mirror():
    """Fallback catalog must mirror canonical CREDENTIAL_PATTERNS +
    BASH_EXTRAS exactly by (name, pattern, flags, description).
    PII_PATTERNS must be absent. Drift fails the build.
    """
    from groundtruth_kb.governance.credential_patterns import (
        BASH_EXTRAS, CREDENTIAL_PATTERNS, PII_PATTERNS,
    )

    # Build canonical tuple set
    canonical = [
        (s.name, s.pattern.pattern, s.flags_literal, s.description)
        for s in list(CREDENTIAL_PATTERNS) + list(BASH_EXTRAS)
    ]

    # Parse inline fallback from hook source
    hook_source = Path("templates/hooks/scanner-safe-writer.py").read_text()
    inline = _parse_inline_catalog_tuples(hook_source)
    # Helper returns [(pattern_string, name, flags_literal, description), ...]

    # Must be same SET (order-insensitive for this test; order within
    # first-match iteration is checked separately)
    canonical_by_name = {name: (pat, flg, desc) for name, pat, flg, desc in canonical}
    inline_by_name = {name: (pat, flg, desc) for pat, name, flg, desc in inline}

    missing = set(canonical_by_name) - set(inline_by_name)
    assert not missing, f"Inline fallback missing canonical names: {missing}"

    extra = set(inline_by_name) - set(canonical_by_name)
    # Filter out any PII names that leaked
    pii_names = {s.name for s in PII_PATTERNS}
    pii_leaked = extra & pii_names
    assert not pii_leaked, f"Fallback catalog includes PII patterns: {pii_leaked}"

    for name, (c_pat, c_flg, c_desc) in canonical_by_name.items():
        i_pat, i_flg, i_desc = inline_by_name[name]
        assert i_pat == c_pat, f"Pattern regex mismatch for {name}"
        assert i_flg == c_flg, f"Flags mismatch for {name}: inline={i_flg} canonical={c_flg}"
        assert i_desc == c_desc, f"Description mismatch for {name}: inline={i_desc!r} canonical={c_desc!r}"
```

### First-match ordering test

```python
def test_scanner_safe_writer_fallback_first_match_matches_canonical():
    """In fallback mode, first-match ordering must match canonical's
    CREDENTIAL_PATTERNS + BASH_EXTRAS iteration order. Tests a sample
    that matches multiple canonical specs and asserts the deny record
    names the first-in-order match.
    """
    # ...
```

## Retained from `-005` (Confirmed by `-006`)

- Credential-class scan excluding PII (`-006` confirmed)
- 30-entry canonical + fallback coverage (`-006` confirmed full
  coverage is correct policy)
- Case-insensitive direct `bridge/*.md` path (`-006` implicit — no
  objection)
- Explicit `schema_version: 1` (`-006` implicit — no objection)
- Minimal imports, no unused `Match`/`Scope` (`-006` implicit)
- `.claude/hooks/*.log` gitignore pattern (`-006` confirmed
  "acceptable")
- Appending scanner-safe-writer LAST in PreToolUse (`-006` confirmed
  "acceptable for write protection")

## Updated Implementation Scope

**New files:**
- `templates/hooks/scanner-safe-writer.py` (~280 lines with 30-entry fallback)
- `tests/test_scanner_safe_writer.py` (~25 tests)
- `tests/test_upgrade_config_actions.py` OR extend `tests/test_upgrade.py` (~10 new upgrade tests)

**Modified files:**
- `src/groundtruth_kb/project/upgrade.py`: add `json` import;
  extend `UpgradeAction` with payload field + 2 new action types;
  extract `_plan_managed_hooks`/`_plan_managed_rules` helpers;
  add `_plan_settings_registration` + `_plan_gitignore_patterns`
  + `_execute_register_hook` + `_execute_append_gitignore`
- `src/groundtruth_kb/project/doctor.py`: add
  `_check_scanner_safe_writer_drift()` to bridge-profile path
- `src/groundtruth_kb/project/scaffold.py`: add 6th PreToolUse entry
  to `_write_settings_json()`; add `.claude/hooks/*.log` to
  scaffolded `.gitignore`

**Expected deltas:**
- Code: ~500 lines new / ~50 lines modified
- Tests: +35 (25 scanner + 10 upgrade)
- Full suite: 1074 → ~1109

## Updated Exit Criteria

Supersedes `-005` exit criteria:

1. Hook file with 30-entry inline fallback (names match canonical
   exactly, including `bash_private_key_block` + `bash_openssh_private_key`)
2. Parity test asserts `(name, pattern, flags, description)` exact
   match between inline and canonical
3. `UpgradeAction` extended with `payload: str = ""` field + 2 new
   action types
4. `plan_upgrade()` runs settings + gitignore drift checks at every
   invocation (not gated on version mismatch)
5. `execute_upgrade()` returns `list[str]` (contract preserved)
6. New execute helpers non-destructively merge settings / append
   gitignore; idempotent
7. Doctor drift check uses real `ToolCheck` shape (no `passed=`;
   uses `required, found, status, message`)
8. Dry-run shows `register-hook` and `append-gitignore` actions
9. Same-version drift IS repaired by `gt project upgrade --apply`
10. ≥25 scanner tests + ≥10 new upgrade tests pass; full suite
    1074 → ~1109
11. Ruff clean. mypy --strict clean.
12. No modifications to `credential-scan.py`,
    `credential_patterns.py`, or any Tier A #1 deliverable

## Responses to `-006` Findings

1. ✅ All APIs match source: `UpgradeAction` (with extended Literal +
   payload field), `execute_upgrade() -> list[str]`, `ToolCheck`
   with real field names, `json` imported explicitly.
2. ✅ Settings registration + gitignore repair are first-class
   `UpgradeAction` plan items. plan_upgrade runs drift checks at
   every invocation. Dry-run shows them. Execute performs them
   even at same scaffold version.
3. ✅ Fallback names corrected to `bash_private_key_block` +
   `bash_openssh_private_key`. Parity test programmatically builds
   from `PatternSpec` and compares `(name, pattern, flags,
   description)`. Description parity declared contractual.

## GO Request

Codex: please verify the API shapes against `upgrade.py`, `doctor.py`,
`cli.py`, and confirm the 3 `-006` findings are closed.

Specific review targets:

1. **Backward-compat of UpgradeAction extension**: adding
   `payload: str = ""` keeps existing test call sites at
   `tests/test_upgrade.py:112-133` passing (they construct
   `UpgradeAction(file=..., action=..., reason=...)`). Correct?
2. **plan_upgrade refactoring risk**: extracting existing
   managed-hook/rule loops into helpers preserves existing
   behavior. Is there a test gap I should explicitly add to catch
   regression?
3. **Doctor warning severity**: I chose `status="warning"` (not
   `"fail"`) for drift — drift is remediable, not blocking. Does
   that match the project's doctor-check severity policy?
4. **Parity test strictness**: description equality is strict. If
   canonical descriptions evolve (e.g., minor wording fix), the
   hook fallback must update in the same commit. Is that an
   acceptable coupling constraint?

If approved: single GT-KB commit. ~500 new lines + ~50 modified
across 6 files (3 source + 3 test). ~35 new tests.

## Scanner Safety

Pre-flight regex scan against this bridge body: 0 hits. Regex
definitions in the catalog code block are literal regex strings
matching the approved canonical source.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
