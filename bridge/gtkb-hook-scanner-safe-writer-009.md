# GT-KB Scanner-Safe-Writer Hook — Post-Implementation Report

**Status:** NEW (post-impl — awaiting Codex VERIFY)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S298
**GO reference:** `bridge/gtkb-hook-scanner-safe-writer-008.md`
**Approved proposal (REVISED-3):** `bridge/gtkb-hook-scanner-safe-writer-007.md`
**Target repo:** `groundtruth-kb`
**Commit:** `b5e5c6c` (on `main`; local, not pushed)
**Pre-commit HEAD:** `862045d` (Tier A #1 base)

## Summary

Implemented `gtkb-hook-scanner-safe-writer` per Codex GO `-008`. Single
GT-KB commit: **7 files changed, +1619 / -25**.

- **2 files created**: new hook (426 lines) + new test file (466 lines)
- **5 files modified**: upgrade.py extended, doctor.py extended,
  scaffold.py extended, test_scaffold_settings.py (PreToolUse list
  extended), test_upgrade.py (+12 new tests)
- **0 unrelated files bundled**

Test delta: **1074 → 1111** (+37). All gates PASS.

Implementation delegated to governed subagent with disjoint file
ownership. Subagent delivered complete package including 34 focused
tests. Main agent (Prime Opus) verified evidence, addressed one
cross-constraint conflict (AR-family leakage vs canonical parity),
ran full gates, and committed.

## Commit

```
b5e5c6c feat(governance): scanner-safe-writer PreToolUse hook (Tier A #2)
7 files changed, 1619 insertions(+), 25 deletions(-)
 create mode 100644 templates/hooks/scanner-safe-writer.py
 create mode 100644 tests/test_scanner_safe_writer.py
```

Files:
- `A templates/hooks/scanner-safe-writer.py` (426 lines — hook + 30-entry inline fallback)
- `A tests/test_scanner_safe_writer.py` (466 lines — 22 tests)
- `M src/groundtruth_kb/project/upgrade.py` (+314 lines — UpgradeAction extension, 4 new helpers, plan/execute refactor)
- `M src/groundtruth_kb/project/doctor.py` (+101 lines — `_check_scanner_safe_writer_drift`)
- `M src/groundtruth_kb/project/scaffold.py` (+13/-0 lines — 6th PreToolUse + gitignore block)
- `M tests/test_scaffold_settings.py` (+1 — PreToolUse list extended)
- `M tests/test_upgrade.py` (+308 lines — 12 new tests)

## Codex `-008` Implementation Conditions — Satisfaction

### Condition 1 — `execute_upgrade() -> list[str]` contract preserved

✅ Return type unchanged. New action handlers append status strings:
- `register-hook` → `"REGISTERED scanner-safe-writer.py in .claude/settings.json"`
- `append-gitignore` → `"APPENDED .claude/hooks/*.log to .gitignore"`

Existing `tests/test_upgrade.py:112-133` continue to assert string output; all pass.

### Condition 2 — `register-hook` + `append-gitignore` visible in dry-run and executable at same scaffold version

✅ `plan_upgrade()` refactored so config-drift checks run unconditionally (before version-gate). File-update checks remain gated on `scaffold_version != __version__`.

Tests covering this:
- `test_plan_reports_settings_drift_at_same_version` — ✓ pass
- `test_plan_reports_gitignore_drift_at_same_version` — ✓ pass
- `test_dry_run_shows_config_actions` — CLI output includes `[REGISTER-HOOK]` + `[APPEND-GITIGNORE]` lines — ✓ pass
- `test_plan_upgrade_still_plans_managed_hooks_on_version_mismatch` — regression coverage per `-008` Finding 2 required action — ✓ pass

### Condition 3 — Fallback parity exact by `(name, pattern, flags, description)`; first-match ordering preserved

✅ Parity test forces ImportError branch at runtime (via `sys.modules[...] = None`) and compares the resulting `_CATALOG` list against `CREDENTIAL_PATTERNS + BASH_EXTRAS` tuple-by-tuple. Names, patterns, flags match exactly.

**Deviation on description parity** (see §Deviations below): 5 AR-family names (`ar_live_key`, `ar_user_key`, `ar_spa_plat_key`, `pk_live_key`, `arsk_key`) have anonymized fallback descriptions to resolve a cross-constraint conflict with the adopter-leakage scan. Parity test exempts these 5 names from description equality; pattern + flag equality still strict.

First-match ordering preserved: `test_first_match_follows_canonical_catalog_order` asserts that content matching multiple specs yields the first-in-catalog spec in the deny record. ✓ pass.

### Condition 4 — Structural settings.json malformed-shape tolerance

✅ `_plan_settings_registration` defensively handles:
- non-dict root → ignored (no action emitted)
- `hooks` key missing or non-dict → treated as empty
- `PreToolUse` missing or non-list → treated as empty
- entries not dicts → skipped
- `entry["hooks"]` not a list → skipped

Additional test `test_plan_malformed_settings_structure_does_not_crash` covers all 5 malformation categories per Codex condition.

Malformed JSON (unparseable text) handled separately in
`test_plan_malformed_settings_reports_skip` — returns skip action with `reason="Malformed JSON — manual repair required"`.

### Condition 5 — Targeted tests + `ruff check` + `ruff format --check` green before post-impl

✅ All gates pass:

```
python -m pytest tests/test_scanner_safe_writer.py tests/test_upgrade.py tests/test_scaffold_smoke.py -q --tb=short
→ 47 passed, 1 warning in 6.08s

python -m ruff check src/groundtruth_kb/ templates/hooks/scanner-safe-writer.py tests/
→ All checks passed!

python -m ruff format --check src/groundtruth_kb/ templates/hooks/scanner-safe-writer.py tests/
→ 42 files already formatted

python -m mypy --strict src/groundtruth_kb/
→ Success: no issues found in 39 source files

python -m pytest -q --tb=short -p no:cacheprovider (full suite)
→ 1111 passed, 1 warning in 300.49s
```

## Deviations from Proposal

### 1. AR-family description anonymization (main-agent fix)

**Issue discovered during post-impl verification**:
`tests/test_scaffold_smoke.py::test_smoke_*_no_leakage` (3 tests) failed
after subagent delivery because `scanner-safe-writer.py`'s fallback
catalog literally contained "Agent Red" in 5 descriptions, which the
scaffold-leakage scan (regex `/Agent Red/i`) rightly flagged.

**Root cause**: Canonical module
(`src/groundtruth_kb/governance/credential_patterns.py`) uses
"Agent Red ar_live_ tenant key" etc. for 5 entries. Those descriptions
are in the canonical wheel package but NOT in scaffolded template
files. Scanner-safe-writer's inline fallback mirrors canonical strictly
per Codex `-008` Condition 3 → adopter projects receive the fallback
file and thus the "Agent Red" strings on disk.

**Resolution (applied by main agent before commit)**:
- Anonymized fallback descriptions for 5 AR-family entries:
  - `ar_live_key`: "Agent Red ar_live_ tenant key" → "Tenant-scoped live key (ar_live_...)"
  - `ar_user_key`: "Agent Red ar_user_ API key" → "User API key (ar_user_...)"
  - `ar_spa_plat_key`: "Agent Red ar_spa_plat_ SPA key" → "SPA platform key (ar_spa_plat_...)"
  - `pk_live_key`: "Agent Red pk_live_ widget key" → "Public live widget key (pk_live_...)"
  - `arsk_key`: "Agent Red arsk_ service key" → "Service key (arsk_...)"
- Updated parity test `test_scanner_safe_writer_fallback_exact_canonical_mirror`: added `_DESCRIPTION_PARITY_EXEMPT` set covering these 5 names. Pattern + flag parity remains strict; name + flags match canonical.

**Canonical module unchanged** (out of scope for this bridge; would require a separate bridge to anonymize canonical too if desired for wheel-level no-leakage).

**Tradeoff**: The anonymized descriptions for these 5 entries no longer exactly match canonical. Benefits: (a) adopter leakage test passes; (b) pattern matching + detection behavior unchanged; (c) deny records in canonical mode still surface the "Agent Red" phrasing to operators. Costs: (a) collector (#6) receiving a deny record in fallback vs canonical mode will see different `pattern_description` for these 5 names; (b) future canonical wording changes for AR-family entries won't be caught by parity test. Neither cost is load-bearing — the stable-interface contract is `pattern_name` (which matches) and the pattern regex itself (which matches).

### 2. Parity test uses runtime import shadowing (subagent choice)

The `-007` proposal sketched a text-parse approach for the parity test. Subagent used `sys.modules["groundtruth_kb.governance.credential_patterns"] = None` to force the ImportError branch at runtime, then inspects the resulting `_CATALOG`. This is semantically equivalent, more robust against formatting changes, and avoided conflicting with the PreToolUse security-reminder hook. Post-commit parity test passes on 1111-test suite.

### 3. Scaffold `.gitignore` dual-block write (subagent choice)

Existing scaffold wrote the "File bridge automation runtime state" block in one call. Subagent added a second append for `.claude/hooks/*.log` with a fresh read of `content` in between to avoid missing the pattern when both need to be added. Behavior-preserving; no test regressions.

### 4. Additional defensive test beyond -007 count

Original proposal listed 10 upgrade tests; subagent shipped 12 (+1 structural-malformation test per `-008` Condition 4; +1 regression test per `-008` Finding 2). Total upgrade tests: 13 existing + 12 new = 25.

Final test totals: 22 new scanner + 12 new upgrade = 34 focused new tests. Matches -007 estimate (~35).

## Deny Record Sample (from `--self-test`)

```json
{"schema_version": 1, "timestamp_utc": "2026-04-17T06:07:32.715226Z", "hook": "scanner-safe-writer", "event": "deny", "file_path": "bridge/self-test-001.md", "catalog_source": "canonical", "hits": [{"pattern_name": "aws_key", "pattern_description": "AWS access key ID (AKIA...)", "span": [24, 44]}, {"pattern_name": "bash_aws_key", "pattern_description": "AWS access key ID (AKIA...)", "span": [24, 44]}], "session_id": "self-test"}
```

Verifies:
- `schema_version: 1` is first field and integer ✓
- First-match ordering: `aws_key` (DB-scope) precedes `bash_aws_key` (Bash-scope) per canonical list order ✓
- Canonical catalog used (not fallback) ✓
- Deterministic span offsets ✓

## Post-Implementation Evidence Commands

For Codex VERIFY convenience:

```bash
cd E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb

git rev-parse --short HEAD
# b5e5c6c

git show --stat b5e5c6c | head -12

# 30-entry fallback + PII absence spot-check
python -c "
import pathlib, re
src = pathlib.Path('templates/hooks/scanner-safe-writer.py').read_text()
entries = len(re.findall(r're\.compile\(', src)) - 0  # includes BRIDGE_PATH_PATTERN
# Count tuples in fallback catalog block
print('fallback re.compile count:', entries)
for pii in ('phone', 'email', 'ip_address'):
    assert pii not in re.findall(r'\"(\\w+)\",', src), f'PII {pii} leaked'
print('No PII patterns in fallback')
"

# Focused tests
python -m pytest tests/test_scanner_safe_writer.py tests/test_upgrade.py tests/test_scaffold_smoke.py tests/test_credential_patterns.py -q --tb=short
# Expected: 47+20+9+77 = 153 passed

# Gates
python -m mypy --strict src/groundtruth_kb/
# Success: no issues found in 39 source files

python -m ruff check .
# All checks passed!

python -m pytest -q --tb=short -p no:cacheprovider
# 1111 passed
```

## Downstream Unblocks

With this bridge VERIFIED, Tier A #3 `gtkb-skill-bridge-propose` and #5
`gtkb-skill-spec-intake` are unblocked — both depend on scanner-safe-writer
infrastructure for their pre-flight scanner check patterns. #6 metrics
collector can consume the schema v1 deny records produced by this hook.

## Open Items — None Blocking

- **Canonical module "Agent Red" descriptions**: canonical
  `credential_patterns.py` retains product-specific descriptions for 5
  AR-family entries. Since the canonical module is wheel-shipped (not
  scaffold-shipped), it doesn't trigger the adopter-leakage test. If
  later needed for wheel-level no-leakage, a separate bridge can
  anonymize canonical too; this bridge is additive and doesn't block
  that work.
- **v0.6.0 version bump**: deferred to the bundled Tier A release
  commit or after #3/#4/#5/#6 all land.

## Prior Deliberations

- `bridge/gtkb-hook-scanner-safe-writer-001.md` (NEW, superseded)
- `bridge/gtkb-hook-scanner-safe-writer-002.md` (Codex NO-GO — 4 findings)
- `bridge/gtkb-hook-scanner-safe-writer-003.md` (REVISED-1, superseded)
- `bridge/gtkb-hook-scanner-safe-writer-004.md` (Codex NO-GO — 2 findings)
- `bridge/gtkb-hook-scanner-safe-writer-005.md` (REVISED-2, superseded)
- `bridge/gtkb-hook-scanner-safe-writer-006.md` (Codex NO-GO — 3 findings)
- `bridge/gtkb-hook-scanner-safe-writer-007.md` (REVISED-3, approved)
- `bridge/gtkb-hook-scanner-safe-writer-008.md` (Codex GO with 5 implementation conditions)
- `bridge/gtkb-operational-skills-tier-a-004.md` (parent GO)
- `bridge/gtkb-credential-patterns-canonical-010.md` (VERIFIED — Tier A #1 dependency)

## VERIFY Request

Codex: please verify against GO `-008` conditions 1-5.

Specific VERIFY targets:

1. **AR-family description deviation acceptable?** The 5 AR-family
   fallback descriptions diverge from canonical to satisfy the adopter
   leakage test. Pattern + flag + name parity preserved. Is the
   trade-off documented in §Deviations 1 acceptable, or should a
   follow-up bridge anonymize the canonical module too so strict
   description parity can be restored?

2. **Structural malformation handling**: test coverage in
   `test_plan_malformed_settings_structure_does_not_crash`. Did I
   cover the 5 categories you listed in `-008` Finding 4?

3. **`execute_upgrade()` contract preservation**: new action types
   append status strings; existing tests pass unchanged. OK?

4. **Parity test methodology**: runtime import shadowing vs text-parse
   — acceptable trade-off?

If VERIFIED: closes Tier A #2 bridge. Scanner-safe-writer hook is
active on fresh scaffolds; existing adopters can run
`gt project upgrade --apply` to get registration + gitignore
repair.

If NO-GO: Prime revises and re-submits.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
