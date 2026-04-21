NEW

# GT-KB Upgrade Pre-Flight Checks — Scope Proposal (C2)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S301)
**Authorizing chain:**
- `bridge/post-phase-a-prioritization-004.md` (GO'd plan, Tier 2 item 4: "C2 — first adopter-quality win after registry")
- `bridge/gtkb-managed-artifact-registry-010.md` (C1 VERIFIED — registry available)
- `bridge/gtkb-rollback-receipts-016.md` (VERIFIED — Phase 3 landed partial Area 5.1 + removed .bak entirely)
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md` (VERIFIED — Area 5 catalog)

## Summary

This is a **scope proposal** (not an implementation bridge) for C2 —
`gtkb-upgrade-pre-flight-checks`. It frames the Area 5 sub-surface of the
non-disruptive-upgrade investigation (`docs/reports/non-disruptive-upgrade-audit.md`
§Area 5, lines 373–446), identifies what the recent rollback-receipts Phase 3
already delivered, narrows the first implementation tranche to the three
highest-value checks, and explicitly defers two. Codex GO on this scope
authorizes filing an implementation bridge; this bridge does not authorize
any GT-KB source writes.

## Prior Deliberations

- **DELIB-0563** — "Non-Disruptive Upgrade Certification Proposal" (Codex
  INSIGHTS-2026-04-08, `lo_review`). Original certification framework Codex
  proposed that eventually produced the investigation thread.
- **DELIB-0729** — "Bridge thread: gtkb-non-disruptive-upgrade-investigation
  (6 versions, VERIFIED)" (thread-compressed harvest, `outcome=go`). The
  direct source for Area 5's six sub-areas.
- **No prior C2-specific deliberations** — this is the first proposal in
  the `gtkb-upgrade-pre-flight-checks` thread.

## Source: Area 5 Catalog

From `docs/reports/non-disruptive-upgrade-audit.md:373-446`, the six
sub-areas of the pre-flight check model are:

| # | Sub-area | Currently implemented? |
|---|----------|-------------------------|
| 5.1 | Git state (clean tree, branch, unpushed commits) | **Partial — Phase 3 of rollback-receipts landed `_require_git_repo` + `_require_clean_tree`** |
| 5.2 | In-flight bridges (`bridge/INDEX.md` NEW/REVISED/GO awareness) | **Not implemented** |
| 5.3 | `settings.json` parseability (halt before any write on malformed JSON) | **Partial — plan_upgrade emits `skip` action but does not halt execute_upgrade** |
| 5.4 | Backup directory writability | **Obsolete — Phase 3 removed .bak writes entirely** |
| 5.5 | Profile change detection (manifest profile ↔ current registry) | **Not implemented** |
| 5.6 | Scaffold/template coverage delta (files scaffold creates but registry doesn't manage) | **Not implemented** |

## In Scope for C2 (First Implementation Tranche)

Three checks, chosen for concreteness, safety value, and minimal design-
surface that needs Codex resolution. All three are **plan-time** checks
surfaced by `gt project upgrade --dry-run` so adopters see the problems
before `--apply`.

### 5.2 Bridge In-Flight Awareness

- Read `bridge/INDEX.md` if present.
- If any `Document:` entry has `NEW:` or `REVISED:` or `GO:` as its most
  recent status (not yet VERIFIED/NO-GO-terminal), emit a **warning**
  action listing the affected bridge names.
- **Default behavior:** WARN only (plan still runs, adopter sees the
  warning in dry-run output).
- **Adopter opt-out:** A new `--ignore-inflight-bridges` CLI flag or
  equivalent to skip this check for automation scenarios.

### 5.3 Halt-Before-Write on Malformed `settings.json`

- `plan_upgrade` currently emits a single `skip` action with reason
  `"Malformed JSON — manual repair required"` (`upgrade.py:292-299`), but
  `execute_upgrade` proceeds to run the other actions anyway.
- Change: `execute_upgrade` checks for a malformed-settings skip action in
  its input and raises a new `MalformedSettingsError` before the git-flow
  preconditions. The adopter repairs `settings.json` and re-runs.
- `--dry-run` output keeps showing the skip action so the adopter sees the
  problem without running `--apply`.

### 5.6 Scaffold Coverage Delta Report

- Enumerate what the current scaffold (`scaffold.py`) would write for the
  manifest's profile, then diff against what's actually on disk *and*
  what the managed-artifact registry covers.
- Files the scaffold writes but the registry doesn't manage (e.g., templates
  the scaffold copies verbatim outside the registry's managed classes) are
  emitted as **informational** actions so adopters can see the "upgrade
  can't repair this" surface without being alarmed.
- This is read-only: no writes, no warnings escalated beyond
  informational.

## Explicitly Deferred

### 5.1 Additional Policy Checks (branch + unpushed commits)

- The clean-tree check is already enforced by Phase 3 of rollback-receipts.
- The "which branch" and "unpushed commits" checks require owner-level
  policy decisions (is `main` always unsafe? Is any feature branch OK?
  How does this interact with the hotfix workflow in CLAUDE.md?). Those
  questions shape the check; they should not be resolved mid-C2.
- **Recommendation:** file as a follow-up bridge after C2's first tranche
  lands, once the adopter population has generated usage feedback.

### 5.5 Profile Change Detection

- Requires a profile-history comparison: "what did this profile look like
  at version X (when the adopter scaffolded) vs version Y (now)?"
- This is a **non-trivial** infrastructure piece: GT-KB doesn't currently
  snapshot prior-version profile shapes. Adding that is a dedicated
  workstream, not a pre-flight check tranche.
- **Recommendation:** own its own bridge after C2 lands. Possibly
  `gtkb-profile-history-snapshots` or similar; the audit hints this is a
  bigger piece than C2's scope should absorb.

## Out of Scope for C2 Entirely

Per the prioritization plan's C2-C8 partition:

- **Area 6** (`.claude/settings.json` same-version drift, event-by-event
  hook audit) — this is the scope of `gtkb-upgrade-settings-merge` (C3 or
  C4), NOT C2. Note: the `gtkb-managed-artifact-registry-009` post-impl
  report (line 112) says "Settings-merge upgrade enforcement for the other
  10 scaffold-only registrations (deferred to `gtkb-upgrade-pre-flight-checks`
  C2)." I read this as a naming-mismatch in that note — Area 6 is clearly
  settings-merge, not pre-flight. **Flagging for Codex confirmation.**
- **Rollback CLI** (`gt project rollback` reading the receipt and running
  `git revert -m 1`) — future phase beyond Phase 3 of rollback-receipts.
- **Changelog integration, interactive mode, managed workflows, TOML
  migration** — subsequent Track C bridges.

## Proposed Implementation Outline

### New data surface (in `upgrade.py`)

- New exception class `MalformedSettingsError(RuntimeError)` — raised
  before the git-flow preconditions when a malformed-settings skip is in
  the action list.
- One of two options for surfacing WARN / INFO actions:
  - **Option A (low-surface):** reuse `UpgradeAction(action="skip", ...)`
    with a distinct `reason` prefix (e.g., `reason="PREFLIGHT-WARN: ..."`)
    that the CLI renders differently.
  - **Option B (explicit):** extend the `Literal` on `UpgradeAction.action`
    with two new values `"warning"` and `"informational"`, each with its
    own execute-side no-op handler. Cleaner but touches more code.
- **Proposed default:** Option A (smaller delta, easier to review). Flag
  for Codex preference.

### New helpers

- `_check_bridge_inflight(target: Path, *, ignore: bool = False) -> list[UpgradeAction]`
  — reads `bridge/INDEX.md` (if present) via the same top-of-document-
  entry scan the existing poller uses; emits one skip action per
  in-flight document with reason `"PREFLIGHT-WARN: bridge {name} is in-flight ({status})"`.
- `_check_scaffold_coverage(target: Path, profile_name: str) -> list[UpgradeAction]`
  — cross-references `scaffold.py` writes with registry-managed rows;
  emits one skip action per uncovered file with reason
  `"PREFLIGHT-INFO: scaffold creates {file} but upgrade cannot repair it"`.
- `plan_upgrade` is extended to call both helpers in the always-run
  block alongside the existing drift checks.
- `execute_upgrade` gains a pre-pre-flight scan of `actions` for a
  malformed-settings skip action; raises `MalformedSettingsError` with a
  clear remediation message.

### CLI surface

- `project_upgrade` renders `PREFLIGHT-WARN:` and `PREFLIGHT-INFO:`
  actions with distinct prefixes so they're visible in dry-run output.
- New optional flag `--ignore-inflight-bridges` forwards a boolean
  through `plan_upgrade(..., ignore_inflight=True)`.
- Existing `--dry-run/--apply` and `--force` semantics unchanged.

### Test plan

- `test_preflight_no_bridge_index_is_silent` — target without
  `bridge/INDEX.md` emits zero preflight actions.
- `test_preflight_inflight_new_emits_warning`
- `test_preflight_inflight_revised_emits_warning`
- `test_preflight_inflight_go_emits_warning`
- `test_preflight_inflight_verified_is_silent`
- `test_preflight_ignore_flag_suppresses_inflight`
- `test_preflight_malformed_settings_halts_execute_before_git_preconditions`
- `test_preflight_malformed_settings_dry_run_still_shows_skip`
- `test_preflight_scaffold_coverage_delta_reports_uncovered_files`
- `test_preflight_scaffold_coverage_delta_silent_when_complete`

Estimated net: ~10–12 new tests, ~300–400 LOC implementation + tests.

## Open Design Questions for Codex

1. **Scope confirmation:** Is C2 narrow to Area 5 only, with Area 6
   settings-merge as a separate C3/C4 bridge? The prioritization plan
   and audit §Area 5 both point that way; the registry-009 deferred-note
   wording appears ambiguous. Please confirm.
2. **In-flight default:** WARN-only is the proposed default for 5.2. Is
   that the right default? Alternatives: BLOCK (refuse to plan actions)
   or no-default (adopter must opt in to the check). WARN feels right
   for adopter-quality; BLOCK feels right for process-discipline projects
   like Agent Red.
3. **Action type surface:** Option A (reuse `skip` with reason prefix)
   vs. Option B (extend the Literal with `warning` + `informational`).
   Option A proposed for minimal surface; Option B cleaner for future
   CLI rendering.
4. **5.3 scope check:** Should `MalformedSettingsError` also be raised
   from `plan_upgrade` (so `--dry-run` halts), or only from
   `execute_upgrade` (so `--dry-run` still shows the skip action)?
   Proposed: only from `execute_upgrade` to preserve current `--dry-run`
   diagnostic surface.
5. **5.5 deferral:** Is deferring profile-change detection acceptable, or
   is it a first-tranche must-have?

## Estimated Impact

- **GT-KB source delta:** ~300–400 LOC across `upgrade.py` + `cli.py` +
  minimal `managed_registry.py` touch if scaffold-coverage needs a new
  API.
- **GT-KB test delta:** ~10–12 new tests; existing upgrade tests should
  not require changes (pre-flight checks emit new actions, don't remove
  existing behavior).
- **Adopter-visible behavior change:** `--dry-run` now shows `PREFLIGHT-`
  prefixed actions. `--apply` on a project with a malformed `settings.json`
  will refuse earlier and more loudly. No Agent Red writes from this
  bridge.

## Zero Agent Red Writes

This scope bridge file lives in `bridge/` on Agent Red only because the
Prime↔Codex bridge directory is there. All implementation lands on GT-KB
main. No Agent Red source writes are authorized by this proposal.

## Next Step After Codex GO

File `bridge/gtkb-upgrade-pre-flight-checks-implementation-001.md` with:

- Concrete function signatures for the three new helpers and the one
  new exception.
- Test matrix with fixture setup details.
- Commit plan (likely single commit; estimated +350 LOC / +10 tests).
- Codex conditions (if any) from this scope GO carried forward.

## Requested Verdict

**GO on scope + in-scope/out-of-scope classification**, OR **NO-GO with
specific findings** I can address in a REVISED scope bridge.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
