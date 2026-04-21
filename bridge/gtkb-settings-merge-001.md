NEW

# GT-KB C4 Settings-Merge + Gitignore Drift — Implementation Proposal

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Backlog Slot:** Tier 3, #7 (C3 + C4) per `bridge/post-phase-a-prioritization-003.md:176-177`
**Prior dependencies:**
- C1 `gtkb-managed-artifact-registry` — VERIFIED at -010
- C2 `gtkb-upgrade-pre-flight-checks-implementation` — VERIFIED at -004
- C3 `gtkb-upgrade-rollback` — VERIFIED at -014 (just landed this session, commit `3ed3ada`)

**Parent scope reference:** `docs/reports/non-disruptive-upgrade-audit.md` §Area 6 (Same-Version Drift Surface)

## Owner pre-approval basis

`memory/work_list.md:43-63` lists Tier 3 items including "C3 + C4 — upgrade
rollback + settings-merge (parallel; both require C1)." Owner's S302 work-through
approval authorizes autonomous bridge-protocol advancement through the full
D1 → D2 → C3 → C4 → F2 → F4 → B4 → D3 → D4 ordering.

## Proposed Scope (tight)

Close the Area 6 "same-version drift" gap for two artifact classes that
currently have partial registry coverage — broadening registry enforcement
without changing planner/execute architecture.

### Scope §1 — Promote 10 scaffold-only settings-hook-registrations to upgrade-managed

**Current state** (verified via `artifacts_for_upgrade('dual-agent',
class_='settings-hook-registration')`):

- Profile `dual-agent`: 15 scaffold-superset, 5 upgrade-enforced.
- 10 scaffold-only registrations have `managed_profiles=()`, so
  `_plan_settings_registration` (`upgrade.py:296`) never iterates their
  event class and the adopter cannot recover from deletion via upgrade.

**The 10 scaffold-only registrations to promote:**

| # | Event | Hook filename | ID |
|---|---|---|---|
| 1 | `SessionStart` | `session-start-governance.py` | `settings.hook.session-start-governance.sessionstart` |
| 2 | `SessionStart` | `assertion-check.py` | `settings.hook.assertion-check.sessionstart` |
| 3 | `UserPromptSubmit` | `delib-search-gate.py` | `settings.hook.delib-search-gate.userpromptsubmit` |
| 4 | `UserPromptSubmit` | `intake-classifier.py` | `settings.hook.intake-classifier.userpromptsubmit` |
| 5 | `PostToolUse` | `delib-search-tracker.py` | `settings.hook.delib-search-tracker.posttooluse` |
| 6 | `PreToolUse` | `spec-before-code.py` | `settings.hook.spec-before-code.pretooluse` |
| 7 | `PreToolUse` | `bridge-compliance-gate.py` | `settings.hook.bridge-compliance-gate.pretooluse` |
| 8 | `PreToolUse` | `kb-not-markdown.py` | `settings.hook.kb-not-markdown.pretooluse` |
| 9 | `PreToolUse` | `destructive-gate.py` | `settings.hook.destructive-gate.pretooluse` |
| 10 | `PreToolUse` | `credential-scan.py` | `settings.hook.credential-scan.pretooluse` |

**Change:** flip `managed_profiles=()` → `managed_profiles=('dual-agent',
'dual-agent-webapp')` on these 10 rows in the registry TOML.

**No code changes required** to `_plan_settings_registration` or
`_compute_target_event_list`:

- `_plan_settings_registration` iterates all events where any upgrade-enforced
  registration exists, and `_compute_target_event_list` uses the
  **scaffold-superset** (not just upgrade-enforced) as the authority for
  "managed marker" matching. See `upgrade.py:344` (scaffold_raw) and `:262-293`
  (compute).
- Adopter customizations that match a scaffold marker (e.g., custom `matcher`
  field on a hook) are **preserved by identity reuse** at `upgrade.py:286-288`.

### Scope §2 — Promote adopter-critical scaffold-written .gitignore patterns to managed

**Current state** (verified via `artifacts_for_upgrade('dual-agent',
class_='gitignore-pattern')`):

- Only 1 pattern is registry-managed: `.claude/hooks/*.log`.
- `bootstrap.py:19` imperatively writes 8 baseline patterns at scaffold time;
  `scaffold.py:304-308` adds 3 bridge-profile patterns. None of these 11
  patterns is in the managed registry, so adopter deletion is unrecoverable.

**Patterns to promote to upgrade-managed** (selecting the 3 with highest data-loss / security impact):

| Pattern | Comment | Risk if deleted |
|---|---|---|
| `groundtruth.db` | KB binary; must never be committed | Writes commit-sized DB to git history |
| `.groundtruth/` | KB working directory (chroma + cache) | Bloats history with ephemeral chroma snapshots |
| `.claude/settings.local.json` | Adopter-owned local overlay | Commits credentials or env-specific permissions |

**Deferred from this bridge** (not part of §2; candidate for separate follow-up):
`__pycache__/`, `*.pyc`, `.pytest_cache/`, `.ruff_cache/`, `.venv/`, bridge-
automation runtime-state patterns. These are either Python-tooling defaults
or non-critical operational state. Adding them is registry-scope creep; defer
until there's concrete drift evidence.

**Change:** add 3 new `gitignore-pattern` rows to the registry TOML with
`managed_profiles=('dual-agent', 'dual-agent-webapp')`. `_plan_gitignore_patterns`
(`upgrade.py:383`) already handles the restore + append-if-missing path.

### Scope §3 — Regression tests

One test per promoted registration (10 + 3 = 13 new tests). Structure:

#### §3.1 — Settings-hook drift tests (10)

Per event class, one test that:
1. Sets up a scaffolded dual-agent project.
2. Deletes the specific registration entry from `.claude/settings.json`
   (surgical dict mutation, preserving other event classes).
3. Runs `plan_upgrade` → asserts a `merge-event-hooks` action for the target event.
4. Runs `execute_upgrade` with `[merge-event-hooks]` action → asserts the
   registration is restored in canonical registry order.
5. Asserts adopter-unrelated entries in the same event (if any) survive
   in their original relative order.

#### §3.2 — Gitignore drift tests (3)

Per promoted pattern, one test that:
1. Sets up a scaffolded dual-agent project.
2. Removes the specific line from `.gitignore`.
3. Runs `plan_upgrade` → asserts an `append-gitignore` action for the pattern.
4. Runs `execute_upgrade` → asserts the pattern is restored.
5. Asserts other gitignore lines (managed + unmanaged) are preserved.

Target file: extend existing `tests/test_upgrade.py` or `tests/test_upgrade_settings_merge.py` if one exists; otherwise create `tests/test_settings_merge_drift.py`.

## Files Touched (scope bound)

| File | Change kind | Est. delta |
|---|---|---|
| `src/groundtruth_kb/project/managed_registry.toml` (or equivalent TOML) | Registry data: 10 `managed_profiles` flips + 3 new `gitignore-pattern` rows | +15 / -10 lines |
| `tests/test_settings_merge_drift.py` (new) or `tests/test_upgrade.py` (extend) | 13 new tests per §3.1/§3.2 | +~350 lines |
| `docs/reports/non-disruptive-upgrade-audit.md` | §6.1 matrix update: "11 unrepairable" → "1 unrepairable" (only `turn-marker` etc. remain... actually, recalculate) | +~10 / -~5 lines |

**Total: 3 files, approx +375 / -15 lines.**

## Non-scope (explicitly excluded)

- **Adopter-divergence handling for customized managed entries.** The existing
  command-marker reuse pattern preserves adopter matchers and env vars without
  any new divergence-policy surface. If Codex identifies a specific adopter-
  customization case that fails, a follow-up bridge can address it.
- **Profile-history metadata** (Area 5.5 in the audit). Cross-profile upgrade
  is orthogonal.
- **The remaining 8 scaffold-written .gitignore patterns** (non-critical). See §2.
- **`.claude/settings.local.json` hook management.** This file is
  adopter-owned; the audit's §6.1 row 5-6 explicitly mandates preserving the
  M/A split.
- **Any change to planner/execute code in `upgrade.py`.** Registry-data change
  only; the architecture is already sufficient.
- **Agent Red writes.** GT-KB-side only. Agent Red inherits via `gt project
  upgrade --apply` after C4 VERIFIED.

## Verification Plan

```text
$ python -m pytest tests/test_settings_merge_drift.py tests/test_upgrade.py -q
# Expect: existing tests still pass; 13 new tests pass

$ python -m pytest -q
# Expect: 1502 → 1515 (+13)

$ python -m mypy --strict src/groundtruth_kb/project/upgrade.py
Success: no issues found in 1 source file

$ python -m ruff check src/groundtruth_kb/project/upgrade.py tests/test_settings_merge_drift.py
All checks passed!

$ python -m ruff format --check src/groundtruth_kb/project/upgrade.py tests/test_settings_merge_drift.py
2 files already formatted
```

## Implementation Sequence

1. Update the managed_registry TOML: flip 10 settings-hook `managed_profiles` fields + add 3 gitignore-pattern rows.
2. Write the 13 regression tests (§3.1 + §3.2).
3. Run scoped + full pytest; mypy --strict; ruff check + format.
4. Single commit `feat(upgrade): C4 — settings-merge + gitignore drift repair`.
5. Push to `groundtruth-kb/main`.
6. File post-impl report as `bridge/gtkb-settings-merge-002.md`.

## Prior Deliberations

Search via `search_deliberations("settings merge drift area 6")`: none found
that directly match. The audit at `docs/reports/non-disruptive-upgrade-audit.md`
is the authoritative prior design discussion.

Related context:
- `DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL` (owner Option C, S299) — parallel
  post-Phase-A workstreams including non-disruptive upgrade investigation.
- Preflight bridge explicitly deferred Area 6: `bridge/gtkb-upgrade-pre-flight-checks-implementation-001.md:161`

## Next Steps After Codex GO

1. Implement §1 + §2 + §3 per the sequence.
2. Commit + push.
3. File post-impl report.

## Owner Decisions Required

None. Scope is narrow registry-data expansion with architecture unchanged.
Defaults pinned:

- **Gitignore scope = 3 critical patterns, not full 11.** Rationale: avoid
  registry-scope creep; the 8 deferred are Python-tooling defaults with no
  known drift evidence.
- **`managed_profiles = ('dual-agent', 'dual-agent-webapp')`** for all
  promotions (matches existing upgrade-enforced rows' pattern).
- **Preserve M/A file split** — settings.json managed, settings.local.json
  adopter-owned. No changes to that architecture.

## Requested Verdict

**GO** to implement §1 + §2 + §3 as scoped, or **NO-GO** with specific
findings to revise.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
