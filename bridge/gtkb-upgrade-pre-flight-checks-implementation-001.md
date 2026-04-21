NEW

# GT-KB Upgrade Pre-Flight Checks — Implementation Bridge (C2)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S300 late / S301 carryover window)
**Authorizing chain:**
- `bridge/post-phase-a-prioritization-004.md` (GO'd plan, Tier 2 item 4)
- `bridge/gtkb-upgrade-pre-flight-checks-002.md` (Scope GO, 2026-04-18; 5 conditions)
- `bridge/gtkb-rollback-receipts-016.md` (VERIFIED; Phase 3 delivered Area 5.1 + removed .bak)
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md` (VERIFIED; Area 5 catalog source)

## Summary

Implements the three Area-5 pre-flight checks scoped in `gtkb-upgrade-pre-flight-checks-001.md` and GO'd at `-002`:

- **5.2 — Bridge in-flight awareness** (`bridge/INDEX.md`-aware WARN-only action)
- **5.3 — Malformed-settings halt** (raise in `execute_upgrade`, not `plan_upgrade`)
- **5.6 — Scaffold coverage delta report** (read-only enumerator, no `scaffold_project` call against the adopter)

All 5 scope-GO conditions from `-002` are carried forward into this implementation bridge.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, DA searched before drafting:

- **DELIB-0563** — Non-Disruptive Upgrade Certification Proposal (Codex INSIGHTS). Original Area 5 framework.
- **DELIB-0729** — `gtkb-non-disruptive-upgrade-investigation` thread-compressed harvest. Direct source for Area 5 sub-areas.
- **DELIB-S300-001** — v0.6.1 bundle scope owner decision (relevant because the C2 work should not regress v0.6.1 artifact tracking).
- **No prior C2-implementation DELIB found.** This is the first implementation bridge in this thread.

## Cross-NO-GO Discipline Carry-Forward (per `-013` pattern)

Scope GO `-002` raised 5 conditions. This implementation bridge preserves each:

| Condition | Discharged by |
|-----------|----------------|
| C1 — No WARN/INFO as `skip` actions | §1 (typed action surface: `warning`, `informational`) |
| C2 — Dry-run keeps malformed-settings diagnostic; halt only at apply | §2 (`MalformedSettingsError` raised in `execute_upgrade` only) |
| C3 — In-flight detector uses LATEST status per `Document:` entry | §3 (`_check_bridge_inflight` parses top status line per Document block only) |
| C4 — Scaffold coverage delta is read-only, deterministic | §4 (pure enumerator module; no `scaffold_project` call against adopter) |
| C5 — Scope Area 5 only; Area 6 settings-merge deferred | This implementation bridge explicitly scopes out Area 6 |

## 1. Typed Action Surface (C1 discharge)

Extend `UpgradeAction.action` `Literal` in `src/groundtruth_kb/project/upgrade.py`:

```python
action: Literal[
    "update", "add", "skip",
    "merge-event-hooks", "append-gitignore",
    # NEW in C2 — non-mutating pre-flight rows
    "warning",         # 5.2 in-flight bridges; adopter sees it, --force cannot mutate
    "informational",   # 5.6 scaffold-coverage delta; adopter-visible, zero writes ever
]
```

Executor contract: `_apply_file_actions` MUST early-return for `warning` and `informational` actions regardless of `--force`. These actions never map to a template path, never stage a file, and never trigger a git operation.

**Mandatory regression test:**
```python
def test_warning_and_informational_actions_never_mutate_even_with_force():
    """--apply --force must not touch files for pre-flight warning/info actions."""
    # Synthesize a WarningAction + InformationalAction; call execute_upgrade(force=True).
    # Assert: zero files modified, zero staging actions, zero git calls.
```

## 2. Malformed `settings.json` — halt in `execute_upgrade` (C2 discharge)

Add to `src/groundtruth_kb/project/upgrade.py`:

```python
class MalformedSettingsError(RuntimeError):
    """Adopter's .claude/settings.json is not valid JSON. Apply is refused."""
```

Flow change:
- `plan_upgrade` **unchanged** — still emits a `skip` action with reason `"Malformed JSON — manual repair required"`. Dry-run output continues to show this row.
- `execute_upgrade` — BEFORE `_require_git_repo` / `_require_clean_tree` / receipt resolution / branch creation, scan `actions` for a `skip` action on `.claude/settings.json` with `"Malformed JSON"` in the reason. If found, raise `MalformedSettingsError`.
- `cli.py:project_upgrade` — catch `MalformedSettingsError`, print the adopter-facing message, exit with code `4` (distinct from `2` precondition and `3` merge failure).

**Tests:**
- `test_dry_run_still_prints_malformed_settings_action` — prove dry-run diagnostic is preserved.
- `test_apply_raises_malformed_settings_error_before_any_git_operation` — prove no branch/receipt/merge ever starts.
- `test_cli_malformed_settings_exits_with_code_4` — CLI wrapper exits cleanly.

## 3. In-Flight Bridge Detector (C3 discharge)

New function in `src/groundtruth_kb/project/upgrade.py` (or a new module `project/preflight.py` if we prefer isolation):

```python
def _check_bridge_inflight(target: Path) -> list[UpgradeAction]:
    """Emit a 'warning' action if any bridge/INDEX.md Document has a latest
    status of NEW / REVISED / GO (non-terminal).

    Parses by 'Document:' entry. ONLY the first status line under each
    Document heading is considered. VERIFIED and NO-GO are terminal and
    silent. Tolerates comment lines (<!-- ... -->) and whitespace between
    entries.
    """
```

CLI surface: add `--ignore-inflight-bridges` to `gt project upgrade` so CI/automation can suppress this check deterministically.

**Tests** (must include historical-older-status-under-terminal-latest cases):
- `test_latest_verified_above_older_new_is_silent` — entry with VERIFIED on top and NEW further down returns no warning.
- `test_latest_no_go_above_older_revised_is_silent` — entry with NO-GO on top and REVISED further down returns no warning.
- `test_latest_new_warns` / `test_latest_revised_warns` / `test_latest_go_warns` — non-terminal latest → warning.
- `test_multiple_entries_report_only_those_with_non_terminal_latest` — multi-document parse correctness.
- `test_ignore_flag_suppresses` — `--ignore-inflight-bridges` path is silent.

## 4. Scaffold Coverage Delta (C4 discharge)

New module `src/groundtruth_kb/project/preflight.py` with a **pure enumerator** function:

```python
def enumerate_scaffold_outputs(profile: str, options: dict[str, Any]) -> set[str]:
    """Return the set of target paths that `gt project init --profile <profile>`
    would produce. Pure function — makes NO writes, runs NO `scaffold_project`
    invocation against an adopter target. Sources:
    
    - registry rows (managed-artifacts.toml + scaffold-ownership.toml) filtered
      by profile via existing `artifacts_for_scaffold(profile)`;
    - scaffold's known non-registry outputs (base docs, bridge bootstrap,
      pyproject sections) enumerated from `scaffold._iter_non_registry_outputs`
      (new helper — extracts the path list from the existing scaffold paths
      without calling the writer).
    """
```

Coverage delta check:
- Compute `enumerate_scaffold_outputs(profile)` minus `{a.target_path for a in artifacts_for_upgrade(profile)}`.
- For each path in the delta, emit an `informational` action saying "created by scaffold; not tracked by upgrade."

**Tests** (must cover all 3 profiles):
- `test_enumerator_no_writes_against_target` — run against an existing project tree and assert `git status --short` is byte-identical before/after.
- `test_local_only_coverage_delta` / `test_dual_agent_coverage_delta` / `test_dual_agent_webapp_coverage_delta` — each profile's delta list is deterministic and matches the known non-registry outputs.

## 5. Integration + CLI

Both `_check_bridge_inflight` and the scaffold-coverage-delta check are called from `plan_upgrade` BEFORE the existing missing-file / drift / registration checks. Their outputs (`warning` / `informational` actions) append to the same `actions` list.

`cli.py:project_upgrade`:
- `--ignore-inflight-bridges` flag (default `False`) threaded through to `plan_upgrade`.
- Dry-run output labels them `[WARNING]` and `[INFORMATIONAL]` respectively, matching the existing `[ADD]`, `[MERGE-EVENT-HOOKS]`, `[APPEND-GITIGNORE]` style.

## 6. Tests Summary

~15 new tests total across:
- `tests/test_upgrade.py` — typed-action no-mutation regression + malformed-settings halt.
- `tests/test_preflight.py` (new) — bridge-inflight detector tests + scaffold-enumerator tests + coverage-delta tests.

Full suite must remain green (expected ~1371 tests after +15).

## 7. Out of Scope

- **Area 5.1** — branch name / unpushed-commits policy. Phase 3 delivered the clean-tree gate. Further branch/remote policy needs owner input.
- **Area 5.4** — obsolete (no .bak writes exist post-Phase-3).
- **Area 5.5** — profile change detection requires profile-history metadata that doesn't exist yet in the registry/profile model. Separate future bridge.
- **Area 6** — settings-merge surface (beyond malformed-halt). Separate future bridge per `-002` C5.

## 8. Zero Agent Red Writes

Per adopter-rule: all infrastructure in GT-KB product. Agent Red inherits via future `gt project upgrade --apply` after VERIFIED.

## 9. Next Step

Codex review of this implementation bridge. On GO, Prime (or autonomous headless per the fast-iterate posture) implements + tests + post-impl report.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
