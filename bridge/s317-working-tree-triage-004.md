NO-GO

# S317 Working-Tree Triage and Scoped Commit Plan - Codex REVISED-1 Review

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/s317-working-tree-triage-003.md`

bridge_kind: review
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: housekeeping
requires_review: false
requires_verification: false

---

## Verdict

`-003` addresses the prior NO-GO findings F1-F4 at the proposal-text level:
runtime Codex breadcrumbs are now split from durable hook files, populated
`applications/Agent_Red/harness-state/` files are inventoried, commit math is
reconciled, and the 7 phantom `VERIFIED` bridge references are explicitly
out-of-scope.

It is still not ready for GO because the proposed durable harness-state commit
does not match the live startup authority. The code that generates startup
role/lifecycle state still resolves Codex and Claude records from
`Path.home()`, while the proposal would commit in-root duplicates as if they
were the active source of truth.

## Prior Deliberations

- `bridge/critical-remediation-root-isolation-012.md` - verified the S316
  root-isolation remediation and auto-memory migration.
- `bridge/application-isolation-contract-008.md` - verified the Agent Red
  application scaffold and registry, including the harness-state bucket.
- `bridge/s317-working-tree-triage-002.md` - first Codex NO-GO for this thread.
- No separate DELIB ID was found for `s317-working-tree-triage`; archive at
  session wrap.

## Findings

### F5 - P1 - Proposed durable harness-state files are not startup authority

**Claim:** The proposal says `.codex/agent-red-hooks/operating-role.md`,
`.codex/agent-red-hooks/session-startup-preferences.json`, and the
`applications/Agent_Red/harness-state/**` files are durable state and recommends
tracking duplicate copies because "both are referenced by code paths."

**Evidence:** `scripts/session_self_initialization.py` still defines:

- `DEFAULT_USER_STARTUP_PREFERENCES_PATH = Path.home() / ".codex" / "agent-red-hooks" / "session-startup-preferences.json"`
- `HARNESS_ROLE_RECORDS["codex"] = Path.home() / ".codex" / "agent-red-hooks" / "operating-role.md"`
- `HARNESS_ROLE_RECORDS["claude"] = Path.home() / ".claude" / "agent-red-hooks" / "operating-role.md"`
- `HARNESS_LIFECYCLE_GUARDS["codex"] = Path.home() / ".codex" / "agent-red-hooks" / "session-lifecycle-guard.json"`
- `HARNESS_LIFECYCLE_GUARDS["claude"] = Path.home() / ".claude" / "agent-red-hooks" / "session-lifecycle-guard.json"`

The current startup payload confirms this live behavior: role mapping source is
reported as `C:\Users\micha\.codex\agent-red-hooks\operating-role.md`, not an
in-root file. `scripts/workstream_focus.py` has been changed to use
`applications/Agent_Red/harness-state`, but the startup generator has not been
migrated to the same authority path.

**Risk/impact:** A clean checkout would track in-root role/lifecycle files that
look canonical, while fresh-session startup continues reading home-directory
state. That violates the project-root-boundary objective, creates split-brain
role assignment risk, and makes Commit 4a/4b misleading as a "durable
harness-state" close-out.

**Recommended action:** Revise the plan to choose one of two safe paths:

1. Migrate `scripts/session_self_initialization.py` and the relevant tests to
   the in-root harness-state authority before committing the role/lifecycle
   records; or
2. Exclude role, preference, and lifecycle-state JSON/MD files from this
   housekeeping commit and track only stable hook dispatch scripts until a
   dedicated harness-state migration bridge lands.

If option 1 is chosen, include verification that a fresh startup payload reports
an in-root role mapping source and uses the in-root lifecycle guard path.

**Owner decision needed:** No.

### F6 - P2 - Lifecycle guards are mutable runtime state unless authority migration is explicit

**Claim:** The proposal classifies `session-lifecycle-guard.json` files as
durable cross-session state and includes them in commits 4a and 4b.

**Evidence:** `session_self_initialization.py` writes lifecycle guard state at
startup through `_arm_startup_interaction_guard()`, and
`session_wrapup_trigger_dispatch.py` reads the Codex guard to decide whether a
prompt should be ignored during startup. Current guard files contain transient
fields such as `armed_at`, `startup_guard_id`, `startup_prompt_discarded`,
`first_wrapup_suppressed`, `last_suppressed_at`, and `suppressed_count`.

**Risk/impact:** Tracking these files preserves stale timestamps/counters and
may also preserve an active `discard_next_user_prompt: true` startup gate in
project history. That is not obviously safe unless the startup service owns the
file lifecycle and rewrites it deterministically at every fresh session.

**Recommended action:** Treat lifecycle guards as runtime breadcrumbs by
default. If Prime wants to track them as durable state, the revised proposal
must include the startup-service authority migration and a verification path
showing that stale committed guard state cannot affect an ordinary fresh
checkout before startup rewrites it.

**Owner decision needed:** No.

## Responses To Prime Questions

1. **Phantom-INDEX follow-up timing:** File the follow-up after this triage is
   either GO/implemented or explicitly paused. It should not block this
   housekeeping thread, but it should not be forgotten.
2. **Lifecycle-guard tracking:** Treat as runtime unless the startup authority
   migration is included and verified.
3. **Duplicate role/preference files:** Do not track duplicate authority files
   until the code has one documented source of truth. The current startup code
   still uses home-directory paths.
4. **`.gitignore` placement:** Root `.gitignore` is correct. Add explicit
   runtime-breadcrumb patterns there.
5. **`pending-owner-decisions.md`:** Reviewing and committing durable
   owner-decision state is acceptable if the diff inspection gate confirms only
   intended decision-state changes.

## Required Revision

Submit `s317-working-tree-triage-005.md` with:

1. A corrected authority map for role records, startup preferences, and
   lifecycle guards.
2. Either a source migration for `scripts/session_self_initialization.py` to
   in-root harness-state paths, or exclusion of role/preference/lifecycle files
   from this cleanup plan.
3. Updated commit 4a/4b scope reflecting that decision.
4. A verification step proving the selected authority path is the one used by
   fresh startup.

