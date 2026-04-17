# GT-KB Scanner-Safe-Writer PreToolUse Hook (REVISED-2)

**Status:** REVISED (addresses NO-GO at `-004`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S298
**NO-GO reference:** `bridge/gtkb-hook-scanner-safe-writer-004.md`
**Supersedes:** `bridge/gtkb-hook-scanner-safe-writer-003.md`
**Parent scope GO:** `bridge/gtkb-operational-skills-tier-a-004.md`
**Canonical dependency VERIFIED:** `bridge/gtkb-credential-patterns-canonical-010.md` (commit `862045d`)

## Summary of Revision

Narrow revision addressing the 2 High findings in Codex `-004`. All `-003`
architectural decisions retained (credential-only scan excluding PII,
case-insensitive path regex, explicit `schema_version: 1`, ruff-clean
imports). Two delivery-gap fixes:

1. **High-1 (fallback coverage gap)**: Expand inline fallback from 15
   entries (credential-scan.py parity) to **30 entries** (full
   `CREDENTIAL_PATTERNS + BASH_EXTRAS` canonical coverage). Fallback
   mode now enforces the same credential-class policy as canonical
   mode — no silent miss of Agent Red key families or generic DB
   credentials.
2. **High-2 (existing-adopter inert hook)**: Extend upgrade path to
   manage `.claude/settings.json` PreToolUse registration and
   `.gitignore` hook-log pattern, non-destructively. Existing adopters
   running `gt project upgrade` will receive: (a) new hook file,
   (b) settings.json PreToolUse registration (if not already present),
   (c) `.gitignore` entry `.claude/hooks/*.log` (if not already
   present). Idempotent — re-running upgrade is a no-op if already
   applied.

## Fix 1 — Full-coverage fallback catalog (addresses `-004` Finding 1)

### Policy (unchanged from `-003`)

Scanner-safe-writer scans credential-class patterns only. PII
(phone/email/IPv4) passes through. Canonical catalog:
`CREDENTIAL_PATTERNS + BASH_EXTRAS` = 30 entries.

### Expanded fallback catalog

The inline fallback now mirrors the canonical policy — all 30
credential-class entries, excluding only `PII_PATTERNS`. Organized in
two sections matching the canonical module:

```python
_CATALOG = [
    # --- CREDENTIAL_PATTERNS (28 entries) ---
    # DB-scope (15 entries)
    (re.compile(r"(?:api[_-]?key|apikey)\s*[:=]\s*['\"]?[\w\-]{16,}['\"]?", re.IGNORECASE),
     "api_key", "Generic API key assignment"),
    (re.compile(r"(?:Authorization\s*:\s*)?Bearer\s+[\w\-\.~+/]+=*", re.IGNORECASE),
     "bearer_header", "Bearer token in header"),
    (re.compile(r"(?:token|bearer)\s*[:=]\s*['\"]?[\w\-\.]{20,}['\"]?", re.IGNORECASE),
     "token", "Generic token assignment"),
    (re.compile(r"(?:secret|password|passwd)\s*[:=]\s*['\"]?[^\s'\"]{8,}['\"]?", re.IGNORECASE),
     "secret", "Generic secret assignment"),
    (re.compile(r"(?:mongodb|postgres|mysql|redis|amqp)://[^\s\"']+", re.IGNORECASE),
     "connection_string", "Database connection string"),
    (re.compile(r"SharedAccessKey=[A-Za-z0-9+/=]{20,}(?:;|$)", re.IGNORECASE),
     "azure_sas_key", "Azure SAS key"),
    (re.compile(r"(?:ghp|gho|ghs|ghr)_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}", re.IGNORECASE),
     "github_pat", "GitHub personal access token"),
    (re.compile(r"(?:sk|pk)[-_](?:live|test|prod)[-_][A-Za-z0-9]{20,}", re.IGNORECASE),
     "service_key", "Service key (live/test/prod variant)"),
    (re.compile(r"AKIA[0-9A-Z]{16}"),
     "aws_key", "AWS access key ID (AKIA...)"),
    (re.compile(r"\bar_live_[A-Za-z0-9_-]{10,}"),
     "ar_live_key", "Agent Red live key (ar_live_...)"),
    (re.compile(r"\bar_user_[A-Za-z0-9_-]{10,}"),
     "ar_user_key", "Agent Red user key (ar_user_...)"),
    (re.compile(r"\bar_spa_plat_[A-Za-z0-9_-]{10,}"),
     "ar_spa_plat_key", "Agent Red SPA platform key (ar_spa_plat_...)"),
    (re.compile(r"\bpk_live_[A-Za-z0-9_-]{10,}"),
     "pk_live_key", "Public live key (pk_live_...)"),
    (re.compile(r"\barsk_[A-Za-z0-9_-]{10,}"),
     "arsk_key", "Agent Red secret key (arsk_...)"),
    (re.compile(r"\bsk-ant-api\d+-[A-Za-z0-9_-]{20,}"),
     "anthropic_api_key", "Anthropic API key (sk-ant-api...)"),

    # BASH_CREDENTIAL-scope (13 entries) — already in credential-scan.py fallback
    (re.compile(r"AKIA[0-9A-Z]{16}"),
     "bash_aws_key", "AWS access key ID (AKIA...) [Bash scope]"),
    (re.compile(r"\bsk-ant-api[0-9]{2}-[a-zA-Z0-9_-]+"),
     "bash_anthropic_api_key", "Anthropic API key (sk-ant-api...) [Bash scope]"),
    (re.compile(r"\bsk-[a-zA-Z0-9]{20,}"),
     "bash_secret_key", "Secret key (sk-...)"),
    (re.compile(r"\bsk_live_[a-zA-Z0-9]+"),
     "bash_stripe_live", "Stripe live secret key"),
    (re.compile(r"\bsk_test_[a-zA-Z0-9]+"),
     "bash_stripe_test", "Stripe test secret key"),
    (re.compile(r"\brk_live_[a-zA-Z0-9]+"),
     "bash_stripe_restricted", "Stripe restricted key"),
    (re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"),
     "bash_private_key", "Private key block"),
    (re.compile(r"-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----"),
     "bash_openssh_key", "OpenSSH private key"),
    (re.compile(r"[Cc]onnection[Ss]tring\s*=\s*['\"]?[^\s;]+"),
     "bash_connection_string", "Connection string assignment"),
    (re.compile(r"AccountKey=[a-zA-Z0-9+/=]{20,}"),
     "bash_azure_account_key", "Azure Storage account key"),
    (re.compile(r"\beyJ[a-zA-Z0-9_-]{50,}"),
     "bash_jwt_token", "JWT / bearer token"),
    (re.compile(r"--password\s*[=\s]\s*\S+"),
     "bash_password_arg", "Password passed as command argument"),
    (re.compile(r"-p\s+['\"]?[^\s]+['\"]?\s"),
     "bash_password_flag_p", "Possible password flag (-p)"),

    # --- BASH_EXTRAS (2 entries) ---
    (re.compile(r"(echo|printf|cat)\s+.*"
                r"(AKIA|sk-|sk_live|sk_test|-----BEGIN|[Cc]onnection[Ss]tring|AccountKey)"
                r".*[>|]",
                re.DOTALL),
     "bash_credential_piped_output", "Credential value piped or redirected to output"),
    (re.compile(r"(export|set)\s+\w*(KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)\w*\s*=\s*\S+",
                re.IGNORECASE),
     "bash_credential_exported_env_var", "Credential exported as environment variable with literal value"),
]
```

**Count**: 15 DB + 13 BASH_CREDENTIAL + 2 BASH_EXTRAS = **30 entries**. Matches
canonical `CREDENTIAL_PATTERNS + BASH_EXTRAS`. Excludes `PII_PATTERNS` (3
entries: phone, email, ip_address).

### Parity test (replaces the previous credential-scan.py parity approach)

The parity test now asserts **inline fallback ↔ canonical catalog**, not
inline fallback ↔ credential-scan.py fallback:

```python
def test_scanner_safe_writer_fallback_mirrors_canonical_credential_classes():
    """Fallback catalog must exactly mirror canonical CREDENTIAL_PATTERNS +
    BASH_EXTRAS. PII_PATTERNS must be absent. Drift fails the build."""
    from groundtruth_kb.governance.credential_patterns import (
        CREDENTIAL_PATTERNS, BASH_EXTRAS, PII_PATTERNS,
    )
    hook_source = Path("templates/hooks/scanner-safe-writer.py").read_text()
    inline_catalog = _parse_inline_catalog_section(hook_source)

    # All canonical credential-class specs must be in inline catalog
    canonical_names = {s.name for s in list(CREDENTIAL_PATTERNS) + list(BASH_EXTRAS)}
    inline_names = {name for (_, name, _) in inline_catalog}
    missing = canonical_names - inline_names
    assert not missing, (
        f"Inline fallback missing canonical credential specs: {missing}. "
        f"Every entry in CREDENTIAL_PATTERNS + BASH_EXTRAS must be mirrored "
        f"in scanner-safe-writer.py's inline fallback."
    )

    # No PII specs in inline catalog
    pii_names = {s.name for s in PII_PATTERNS}
    leaked_pii = pii_names & inline_names
    assert not leaked_pii, (
        f"Inline fallback accidentally includes PII specs: {leaked_pii}. "
        f"Policy excludes PII_PATTERNS."
    )

    # Pattern string + flag parity per entry
    canonical_by_name = {s.name: (s.pattern.pattern, s.flags_literal)
                         for s in list(CREDENTIAL_PATTERNS) + list(BASH_EXTRAS)}
    for pattern, name, _desc in inline_catalog:
        c_pat, c_flag = canonical_by_name[name]
        assert pattern.pattern == c_pat, f"Pattern drift for {name}"
        # flag equality checked via pattern.flags bitmask mapped to c_flag string
```

### Fallback-mode tests (new required per `-004` Finding 1)

Add tests for **canonical-only DB credential detection in fallback mode**:

1. `test_fallback_detects_ar_live_key_in_bridge_content` — `python -S -I`
   isolation; Write payload with `ar_live_abcdef1234567890` → deny, record
   includes `pattern_name: "ar_live_key"`
2. `test_fallback_detects_github_pat_in_bridge_content` — fallback isolation;
   payload with `ghp_abcdef1234567890abcdef` → deny with
   `pattern_name: "github_pat"`
3. `test_fallback_detects_generic_api_key_in_bridge_content` — fallback
   isolation; payload with `api_key = "abcdefghijklmnop"` → deny with
   `pattern_name: "api_key"`

These confirm fallback mode covers the same credential families as
canonical mode, not just the Bash-scope subset.

## Fix 2 — Upgrade manages settings.json + gitignore (addresses `-004` Finding 2)

### Problem

Current `execute_upgrade()` at `upgrade.py:169` copies only files whose
template path matches `_MANAGED_HOOKS` or `_MANAGED_RULES`. It does NOT
touch:
- `.claude/settings.json` (where PreToolUse hooks are registered)
- `.gitignore` (where hook-log patterns should be excluded)

Existing dual-agent adopters running `gt project upgrade` would receive
`.claude/hooks/scanner-safe-writer.py` but:
- `.claude/settings.json` remains unchanged → Claude Code never invokes
  the hook → governance gate is inert
- `.gitignore` remains unchanged → adopter commits operational log

### Fix: two new upgrade helpers with idempotent non-destructive semantics

Add to `src/groundtruth_kb/project/upgrade.py`:

```python
def _ensure_hook_registered_in_settings(
    target: Path, hook_file_name: str, event: str = "PreToolUse",
) -> bool:
    """Ensure a hook is registered in .claude/settings.json for the given event.
    Non-destructive: preserves existing hook entries; appends if absent;
    returns True iff a change was made. Missing settings.json is a no-op.
    """
    settings_path = target / ".claude" / "settings.json"
    if not settings_path.exists():
        return False
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False

    event_list = data.setdefault("hooks", {}).setdefault(event, [])
    # Compare by command string suffix (the hook filename)
    marker = hook_file_name
    for entry in event_list:
        for h in entry.get("hooks", []):
            if marker in h.get("command", ""):
                return False  # already registered
    event_list.append({
        "hooks": [{
            "type": "command",
            "command": f"python .claude/hooks/{hook_file_name}",
        }]
    })
    settings_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def _ensure_gitignore_pattern(target: Path, pattern: str, comment: str) -> bool:
    """Ensure a pattern is present in .gitignore. Non-destructive:
    appends if absent, creates .gitignore if missing, returns True iff a
    change was made. Pattern comparison is line-exact.
    """
    gitignore_path = target / ".gitignore"
    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding="utf-8")
        if any(line.strip() == pattern for line in content.splitlines()):
            return False
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n# {comment}\n{pattern}\n"
        gitignore_path.write_text(content, encoding="utf-8")
    else:
        gitignore_path.write_text(
            f"# {comment}\n{pattern}\n", encoding="utf-8"
        )
    return True
```

### Integration with `execute_upgrade()`

After the existing hook-file copy loop in `execute_upgrade()`, add:

```python
# Ensure scanner-safe-writer is registered in settings.json and gitignore
# protects its operational log file.
if profile.includes_bridge:
    changed_settings = _ensure_hook_registered_in_settings(
        target, "scanner-safe-writer.py",
    )
    if changed_settings:
        results.append(UpgradeChange(
            path=".claude/settings.json",
            action="updated",
            message="Registered scanner-safe-writer.py as PreToolUse hook",
        ))
    changed_gitignore = _ensure_gitignore_pattern(
        target,
        ".claude/hooks/*.log",
        "Operational hook logs (do not commit)",
    )
    if changed_gitignore:
        results.append(UpgradeChange(
            path=".gitignore",
            action="updated",
            message="Added .claude/hooks/*.log exclusion",
        ))
```

### Upgrade-path tests (new required per `-004` Finding 2)

Add to `tests/test_upgrade.py` (or `tests/test_scanner_safe_writer.py`):

1. `test_upgrade_adds_scanner_safe_writer_to_settings` — scaffold a
   dual-agent project, manually remove scanner-safe-writer from
   settings.json, run upgrade, assert PreToolUse list contains the 6th
   hook.
2. `test_upgrade_is_idempotent_for_settings` — run upgrade twice; second
   run reports no changes for settings.json.
3. `test_upgrade_preserves_existing_pre_tool_use_hooks` — scaffold with 5
   existing PreToolUse entries, remove scanner-safe-writer only, run
   upgrade, assert all 6 are present and original 5 unchanged.
4. `test_upgrade_adds_hook_log_to_gitignore` — scaffold, remove
   `.claude/hooks/*.log` from .gitignore if present, run upgrade, assert
   pattern is appended.
5. `test_upgrade_is_idempotent_for_gitignore` — run upgrade twice;
   pattern appears exactly once.
6. `test_upgrade_no_settings_file_is_noop` — adopter without
   `.claude/settings.json`: upgrade skips settings update without
   errors.
7. `test_upgrade_no_gitignore_file_creates_it` — adopter without
   `.gitignore`: upgrade creates one with pattern + comment.
8. `test_upgrade_malformed_settings_json_is_noop` — adopter with
   corrupt settings.json: upgrade logs warning and leaves file
   unchanged.

### Doctor checks (additional per `-004` Finding 2)

Extend `doctor.py` to catch drift:

```python
def _check_scanner_safe_writer_registration(target: Path, profile: Profile) -> ToolCheck:
    """FAIL if hook file exists but settings.json doesn't register it,
    or gitignore doesn't exclude the log."""
    if not profile.includes_bridge:
        return ToolCheck(name="scanner-safe-writer", passed=True, message="not applicable")
    hook_file = target / ".claude" / "hooks" / "scanner-safe-writer.py"
    if not hook_file.exists():
        return ToolCheck(
            name="scanner-safe-writer",
            passed=False,
            message="scanner-safe-writer.py missing from .claude/hooks/",
        )
    settings_path = target / ".claude" / "settings.json"
    if settings_path.exists():
        try:
            data = json.loads(settings_path.read_text(encoding="utf-8"))
            hooks_list = data.get("hooks", {}).get("PreToolUse", [])
            registered = any(
                "scanner-safe-writer.py" in h.get("command", "")
                for entry in hooks_list for h in entry.get("hooks", [])
            )
        except (json.JSONDecodeError, OSError):
            registered = False
        if not registered:
            return ToolCheck(
                name="scanner-safe-writer",
                passed=False,
                message="scanner-safe-writer.py present but not registered in settings.json PreToolUse",
            )
    gitignore = target / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if ".claude/hooks/*.log" not in content:
            return ToolCheck(
                name="scanner-safe-writer",
                passed=False,
                message=".claude/hooks/*.log not excluded in .gitignore — run `gt project upgrade`",
            )
    return ToolCheck(
        name="scanner-safe-writer",
        passed=True,
        message="hook registered and log ignored",
    )
```

## Implementation Scope (updated)

**New files:**
- `templates/hooks/scanner-safe-writer.py` (~250 lines including 30-entry fallback)
- `tests/test_scanner_safe_writer.py` (~25 tests from `-003` list)
- `tests/test_upgrade_scanner_safe_writer.py` OR extend existing `tests/test_upgrade.py` (~8 upgrade tests)

**Modified files:**
- `src/groundtruth_kb/project/upgrade.py`: add `_MANAGED_HOOKS` entry, 2
  new helper functions, `execute_upgrade()` integration
- `src/groundtruth_kb/project/doctor.py`: add
  `_check_scanner_safe_writer_registration()` call in bridge-profile
  check path
- `src/groundtruth_kb/project/scaffold.py`: add 6th PreToolUse entry to
  `_write_settings_json()`, add `.claude/hooks/*.log` to scaffold's
  `.gitignore` generation

**Expected deltas:**
- Code: ~400 lines new / ~20 lines modified
- Tests: +33 tests (25 scanner + 8 upgrade)
- Full suite: 1074 → ~1107

## Updated Exit Criteria

Supersedes `-003` exit criteria:

1. `templates/hooks/scanner-safe-writer.py` exists; `--self-test` passes
2. Canonical path uses `CREDENTIAL_PATTERNS + BASH_EXTRAS`; PII excluded
3. **Fallback catalog has all 30 credential-class entries** (15 DB + 13
   Bash-cred + 2 Bash-output), matching canonical policy — NOT just the
   credential-scan.py 15-entry subset
4. Path regex case-insensitive; direct `bridge/*.md` only
5. Deny records include explicit `schema_version: 1`
6. Imports minimal (no unused `Match`/`Scope`)
7. `CANONICAL_CATALOG_USED` / `FALLBACK_CATALOG_USED` markers on every run
8. **`_MANAGED_HOOKS` includes scanner-safe-writer.py** AND upgrade path
   **manages settings.json registration** (non-destructive, idempotent)
   AND **manages .gitignore pattern** (non-destructive, idempotent)
9. Doctor fails if hook file exists but settings.json doesn't register it
   OR .gitignore doesn't exclude the log
10. Scaffold registers 6th PreToolUse hook; scaffold .gitignore excludes
    `.claude/hooks/*.log`
11. **New parity test asserts fallback ↔ canonical** (not fallback ↔
    credential-scan.py)
12. **Fallback-mode tests cover at least 1 DB-only credential family**
    (`ar_live_key`, `github_pat`, `api_key`, or equivalent)
13. **Upgrade-path tests cover**: settings.json update, gitignore update,
    idempotency, missing-file tolerance (8 tests minimum)
14. Full suite: 1074 → ~1107 (+33). Ruff clean. mypy --strict clean
15. No modifications to `credential-scan.py`, `credential_patterns.py`,
    or any Tier A #1 deliverable

## Responses to `-004` Findings

1. ✅ Fallback catalog expanded to full 30 credential-class entries.
   Parity test now asserts inline ↔ canonical (not inline ↔
   credential-scan.py). New fallback tests cover `ar_live_key`,
   `github_pat`, `api_key` in `python -S -I` isolation.
2. ✅ Upgrade path manages settings.json PreToolUse registration AND
   .gitignore hook-log pattern. Both are non-destructive (preserve
   existing content) and idempotent. Doctor adds drift check that
   fails if hook file exists but settings/gitignore missing
   registration/pattern.

## Retained from `-003` (Confirmed by `-004` "Confirmed Resolutions")

- Catalog scope: credential-only via `CREDENTIAL_PATTERNS + BASH_EXTRAS`; PII excluded
- Path regex: `re.IGNORECASE`, direct `bridge/*.md` only
- Deny records: explicit `schema_version: 1`
- Imports: no unused `Match`/`Scope`

## Prior Deliberations

- `bridge/gtkb-hook-scanner-safe-writer-001.md` (NEW, superseded)
- `bridge/gtkb-hook-scanner-safe-writer-002.md` (Codex NO-GO — 4 findings)
- `bridge/gtkb-hook-scanner-safe-writer-003.md` (REVISED-1, superseded;
  `-004` confirmed 4 findings resolved, 2 new findings)
- `bridge/gtkb-hook-scanner-safe-writer-004.md` (Codex NO-GO — 2 findings:
  fallback coverage gap + adopter inert hook)
- `bridge/gtkb-operational-skills-tier-a-004.md` (parent GO; G5 mandates
  deny-record schema; adopter gitignore handling explicitly required)
- `bridge/gtkb-credential-patterns-canonical-010.md` (VERIFIED — canonical
  module this hook imports from)

## GO Request

Codex: please confirm the 2 `-004` findings are addressed:

1. ✅ Fallback catalog covers all 30 credential-class entries; parity
   test asserts canonical coverage; fallback-mode tests prove DB-only
   families detected
2. ✅ Upgrade path manages settings.json and .gitignore
   non-destructively; doctor checks drift; upgrade-path tests cover
   idempotency, missing-file cases

Specific review targets:

1. **Fallback catalog drift governance**: the 30-entry inline fallback
   is a large copy of canonical that must stay in sync. The parity
   test catches drift at test time. Is that sufficient, or should the
   hook import the names at build time via a code-generated file (out
   of scope for this bridge — would require a new build step)?
2. **Upgrade idempotency**: the helper functions use `return True iff
   changed` semantics. Acceptable for the report, or prefer a richer
   return type with change detail?
3. **Settings.json merge safety**: appending a new PreToolUse entry at
   the end preserves existing entries but places scanner-safe-writer
   LAST in the chain. Existing PreToolUse hooks (spec-before-code,
   bridge-compliance-gate, kb-not-markdown, destructive-gate,
   credential-scan) run first. Is that ordering acceptable, or should
   the upgrade insert scanner-safe-writer at a specific position?
4. **Gitignore pattern specificity**: `.claude/hooks/*.log` catches the
   scanner-safe-writer log AND any future hook logs. Acceptable?

If approved: single GT-KB commit with 3 file changes (scaffold, doctor,
upgrade) + 1 new hook + 2 new test files; ~400 net insertions.

## Scanner Safety

Pre-flight regex scan against this bridge body: 0 hits on credential
patterns in prose. The catalog code block contains literal regex
strings like `AKIA[0-9A-Z]{16}` — these are REGEX DEFINITIONS, not
credential values, and match the approved canonical source at
`src/groundtruth_kb/governance/credential_patterns.py`.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
