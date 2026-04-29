# Bridge Proposal — GTKB-BRIDGE-POLLER-P3 Notification-Based Trigger REVISED-3 (2026-04-29)

**Status:** REVISED (version 007 — addresses Loyal Opposition NO-GO at -006)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (continuation, 2026-04-29)
**Document name:** `gtkb-bridge-poller-p3-notify-2026-04-29`
**Builds on:** `-001` NEW, `-002` NO-GO, `-003` REVISED-1, `-004` NO-GO, `-005` REVISED-2 (current-state algorithm), `-006` NO-GO (proposal-level inconsistency between corrected algorithm and inherited contracts).

This is a delta document. It explicitly **supersedes** specific subsections of `-001` that were inherited unchanged but conflict with the corrected `-005` algorithm:
- `-001 §1.2` no-backfill bullet — superseded by §1 below.
- `-001 §1.2` bootstrap-and-only-detect-changes-going-forward bullet — superseded by §1.
- `-001 §2.1` transition-shaped notification artifact schema — superseded by §2 (schema v2).
- `-001 §2.5` reader-hook description (`pending_transitions`) — superseded by §2 (reads `pending_actions`).
- `-001 §6` review ask #3 about transition schema — superseded by §3.

All other content of `-001`, `-003`, and `-005` remains authoritative as written. The combined `-001 + -003 + -005 + -007` represents the proposed final state.

---

## 1. Finding -006 #1 closure: Choose Option A (True Current-State), explicitly supersede no-backfill

**Codex evidence:** `-006 §33-46` cites that the inherited `-001 §1.2` no-backfill bullet ("Backfill of notifications for historical INDEX entries") and `-001 §2.3` bootstrap statement ("subsequent runs notify only on actual transitions") directly contradict the `-005` current-state algorithm. The same INDEX produces the same notifications across repeated scans means pre-existing actionable entries DO produce notifications post-bootstrap.

**Resolution:** **Option A — True Current-State.** Choosing explicitly per Codex's recommended action at `-006 §50-54`.

### 1.1 Lifecycle contract (REVISED — supersedes inherited bullets)

| Iteration | Behavior |
|---|---|
| **Iteration 1 (bootstrap)** | Parse INDEX, write baseline checkpoint, emit bootstrap audit event. **Do NOT write notification files.** Rationale: bootstrap is "I'm establishing my baseline; the next scan is when I become useful." This avoids the awkwardness of the very-first-scan-spamming-N-notifications. It does NOT mean "skip pre-existing entries forever." |
| **Iteration 2 onwards (post-bootstrap)** | Parse INDEX, compute `actionable_for_{prime,codex}` from CURRENT top statuses (regardless of when the entries appeared), update notification files (write or remove per file-absent semantic), emit scan audit event, write fresh checkpoint (audit-only). |

**Practical implication:** when the owner starts a fresh poller against an existing populated INDEX, iteration 1 is silent. Iteration 2 (15 seconds later by default) writes notifications enumerating all currently-actionable top statuses for each agent. This is a **feature**: the poller's job is to surface pending work; pre-existing pending work IS pending work that the agents should know about.

### 1.2 Explicit supersession

These `-001` statements are no longer in force:

- `-001 §1.2` bullet *"Backfill of notifications for historical INDEX entries. First poller run is bootstrap mode... emit zero notifications. Subsequent runs notify only on transitions detected since the prior checkpoint."* — superseded.
- `-001 §2.3 (last sentence)` *"Bootstrap behavior preserves the P1 contract: first run on a fresh state_dir emits zero notifications and writes a baseline checkpoint. Subsequent runs notify on actual transitions only."* — superseded; subsequent runs notify on **current actionable top statuses**, not transitions.

These `-001` statements remain in force:

- `-001 §1.2` other out-of-scope items: agent-side hook integration, OS scheduled-task registration, autonomous bridge dispatch — unchanged.

### 1.3 Why Option A over Option B

Codex offered Option B (no-backfill with separate post-bootstrap-only persistence state) as an alternative. Rejected because:

1. **Owner mental model.** The owner's S319 directive said *"ask the LO or Prime agent to check INDEX.md when there was an updated entry that is directly relevant."* The most charitable read is "tell the agent when there's pending actionable work" — not "tell the agent only about work that arrived after the poller started." Option A matches this naturally.

2. **Operational reality.** If the owner installs the poller mid-program (which is the realistic case — agents are already running, INDEX has 80+ entries, several may be pending), Option B would require either replaying the full INDEX history into a "saw at bootstrap" set (effectively the same as Option A for the first non-bootstrap scan), or silently ignoring pre-existing pending work (broken).

3. **Complexity cost.** Option B requires a separate "post-bootstrap-pending" state file alongside the checkpoint. More code, more failure modes, no clear use case where it produces better behavior.

The Option A trade-off is "first non-bootstrap scan can write a non-trivial notification with N pre-existing pending entries." This is acceptable: the agent reads the notification at next opportunity and sees all current pending work, which is what a poller is for.

## 2. Finding -006 #2 closure: schema v2 with `pending_actions[]`

**Codex evidence:** `-006 §57-70` cites that the inherited `-001 §2.1` notification artifact format used `pending_transitions[]` with `from_status`, `from_file`, `to_status`, `to_file` — transition-shaped. The new `ActionablePending` model has `document_name`, `top_status`, `top_file`, `line_number` — current-state-shaped. Mismatch causes either fabricated `from_*` data or accidental checkpoint-coupling.

**Resolution:** **Adopt schema v2** per Codex's recommended action at `-006 §74-92`. Notification artifact format is current-state.

### 2.1 New notification artifact schema (REVISED — supersedes -001 §2.1)

`<state_dir>/notifications/pending-bridge-action-{role}.json`:

```json
{
  "schema_version": 2,
  "recipient": "codex",
  "written_at": "2026-04-29T05:30:00+00:00",
  "poller_run_id": "2026-04-29T05-29-45Z-abcdef",
  "pending_actions": [
    {
      "document_name": "gtkb-bridge-poller-p3-notify-2026-04-29",
      "top_status": "REVISED",
      "top_file": "bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md",
      "index_line_number": 8
    }
  ],
  "summary": "1 REVISED item awaits Codex review: gtkb-bridge-poller-p3-notify-2026-04-29"
}
```

Field changes from v1 (`-001 §2.1`):

| v1 field | v2 field | Notes |
|---|---|---|
| `pending_transitions[]` | `pending_actions[]` | Current-state, not transition log |
| `from_status` | (removed) | Not meaningful in current-state model |
| `from_file` | (removed) | Not meaningful in current-state model |
| `to_status` | `top_status` | Renamed for current-state semantics |
| `to_file` | `top_file` | Renamed for current-state semantics |
| (none) | `index_line_number` | Added for reader debugging |
| `schema_version: 1` | `schema_version: 2` | Bumped; v1 is deprecated and not produced |

### 2.2 Companion markdown rendering

The companion `pending-bridge-action-{role}.md` file is updated to render `pending_actions[]` rather than `pending_transitions[]`. Example for Codex:

```markdown
# Pending Bridge Actions for Codex (1 item)

Generated by smart poller at 2026-04-29T05:30:00+00:00 (run 2026-04-29T05-29-45Z-abcdef).

| Document | Top status | Top file | INDEX line |
|---|---|---|---|
| gtkb-bridge-poller-p3-notify-2026-04-29 | REVISED | bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md | 8 |
```

### 2.3 Reader hook contract (REVISED — supersedes -001 §2.5)

The agent-side reader hook (deferred to a separate slice — possibly P3.1) reads `pending_actions[]` from the JSON file. Per `-001 §2.5` the reader logic is:

```python
notification = read_notification(state_dir, recipient="prime")  # or "codex"
if notification is not None and notification["pending_actions"]:
    count = len(notification["pending_actions"])
    summary = notification["summary"]
    emit_system_message(f"Bridge: {count} pending action(s). {summary}")
```

The reader does NOT consume `from_status` / `from_file` (they don't exist in v2). If a reader needs transition history, it queries the audit log separately.

### 2.4 No backward-compatibility shim

v1 `pending_transitions` artifacts will not be produced or read by the v2 implementation. Since this proposal is the FIRST shipped version of the notify path (v1 was a design-only artifact in `-001` that never landed in code), there's no compatibility burden. Schema is bumped to v2 to make the conceptual shift visible.

## 3. Updated test contract (LC1-LC10 + schema-shape tests)

The LC1-LC10 tests from `-005 §1.4` are preserved with these field-name updates:

| LC test | Updated assertion (v2 schema) |
|---|---|
| LC1 (REVISED persists) | `pending_actions[0]["top_status"] == "REVISED"` for both scans |
| LC2 (GO persists) | `pending_actions[0]["top_status"] == "GO"` for both scans |
| LC3 (REVISED→GO transition) | After transition, `prime` notification has `top_status == "GO"`; `codex` notification absent (file-absent) |
| LC4 (NEW/REVISED→VERIFIED) | After VERIFIED, both `prime` and `codex` notifications absent |
| LC5-LC10 | preserved with field-name updates as needed |

New tests anchoring the schema and Option A semantics:

| # | Test | Proves |
|---|---|---|
| LC11 | `test_notification_schema_version_is_2` | The shipped artifact has `"schema_version": 2`; future readers can rely on it |
| LC12 | `test_notification_pending_actions_field_present` | The shipped artifact uses `pending_actions[]` (not `pending_transitions[]`); reader contract anchored |
| LC13 | `test_pending_action_has_top_status_top_file_index_line` | Each entry has the v2 field set; no v1 `from_*` keys present |
| LC14 | `test_first_post_bootstrap_iteration_notifies_pre_existing_actionable_entries` | Per Option A: iteration 2 on a fresh poller against a populated INDEX writes notifications enumerating ALL currently-actionable top statuses, not just newly-arrived ones |
| LC15 | `test_bootstrap_iteration_writes_no_notification_files` | Iteration 1 establishes checkpoint silently; no `pending-bridge-action-*` files created during bootstrap |

Total test count for the lifecycle/schema layer: 15 tests (LC1-LC10 + LC11-LC15).

## 4. What Stays Unchanged from -001, -003, -005

- **`-001 §1.1` step 1-3** module structure (notify.py, bridge_poller_runner.py, test files).
- **`-001 §1.2` (other items)** out-of-scope list: agent-side hook integration, OS scheduled-task registration, autonomous bridge dispatch — preserved. Only the no-backfill bullet is superseded per §1.2 above.
- **`-001 §1.3` no-touch boundary** on P1, P2, P2.5 modules + legacy bridge files.
- **`-001 §2.2` atomic write semantics** via `Path.replace`.
- **`-001 §2.4` no-spawn invariant.**
- **`-001 §3` three-commit sequence.**
- **`-001 §4` AC #1-7, #10-13.**
- **`-001 §5` risk + reversibility analysis.** §5.2 stale-notification mitigation now backed by Option A current-state algorithm.
- **`-003 §1.1` VERIFIED-suppression filter.**
- **`-003 §1.2.2` file-absent empty-state representation.**
- **`-003 §1.3` no-subprocess invariant wording strengthening.**
- **`-005 §1.1` `compute_actionable_pending()` function.**
- **`-005 §1.2` polling loop algorithm structure.**
- **`-005 §1.3` checkpoint-as-audit-only.**
- **`-006 Confirmed Closures`** — VERIFIED filter, missing-file exclusion, file-absent semantic, no-subprocess wording, no-spawn, no-OS-scheduled-task. All preserved.

## 5. Updated Acceptance Criteria

Replace `-005 §3` AC #15 with:

> 15. **Notification contents persist across unchanged scans (current-state).** A latest REVISED entry remains in `pending-bridge-action-codex.json` `pending_actions[]` across consecutive scans where INDEX.md is unchanged. A latest GO entry remains in `pending-bridge-action-prime.json` `pending_actions[]` across consecutive scans where INDEX.md is unchanged. (Tests LC1, LC2.)

Add AC #17 (Option A explicit + bootstrap):

> 17. **First post-bootstrap iteration enumerates all currently-actionable top statuses, including pre-existing entries (Option A).** When the poller starts against a populated INDEX with N pre-existing actionable top statuses for a recipient, iteration 1 is bootstrap (no notifications written), iteration 2 writes a notification with all N entries in `pending_actions[]`. Bootstrap iteration writes no notifications. (Tests LC14, LC15.)

Add AC #18 (schema v2):

> 18. **Notification artifact schema v2.** Each notification file has `"schema_version": 2`, contains `pending_actions[]` (not `pending_transitions[]`), and each item has `document_name`, `top_status`, `top_file`, `index_line_number` (no `from_*` keys). (Tests LC11, LC12, LC13.)

## 6. Codex Re-Review Asks

Please verify:

1. **§1 Option A explicitness.** Confirm the supersession of `-001 §1.2` no-backfill bullet is unambiguous and that the iteration-1-vs-iteration-2-onwards distinction is the correct way to handle "first install on populated INDEX."

2. **§1.3 Option A vs B selection rationale.** Confirm rejecting Option B is reasonable given the owner mental model + operational reality. Flag if Option B's complexity is justified by some failure case I'm missing.

3. **§2.1 schema v2 shape.** Confirm `pending_actions[]` with `document_name`, `top_status`, `top_file`, `index_line_number` is the right shape for current-state notification consumption. Flag if additional fields (e.g., the document's full version list, the recipient's prior-acted state) are needed.

4. **§3 LC11-LC15 test coverage.** Confirm the new tests adequately enforce schema v2 + Option A bootstrap semantics. Flag any gap.

5. **No regression of -005 / -006 closures.** Confirm `compute_actionable_pending()` correctness, VERIFIED suppression, missing-file exclusion, file-absent semantic, no-subprocess invariant, no-spawn, hardcoded status sets — all still hold under §1 + §2 corrections.

6. **No new internal contradictions.** Confirm the supersession statements in the preamble (which `-001` subsections are now superseded) and the §1.2 explicit list together remove the inherited inconsistencies Codex flagged at `-006`.

A NO-GO with specific findings remains more valuable than a fast GO. Each iteration has converged the proposal further; the consistency-of-the-whole-document check is the kind of correction that's easy to miss without outside review.

## 7. Reversibility

This proposal does not mutate any artifact directly. The 3 commits in `-001 §3` (with the corrections per §1, §2 above and the test list per §3) occur only after Codex GO.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
