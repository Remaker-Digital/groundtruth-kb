NO-GO

# GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY - Codex Review of 005

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-05-02
**Reviewed proposal:** `bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-005.md`

## Claim Reviewed

Prime revised the proposal to implement `add_status_line()` in both the packaged
template helper and the live `.claude` helper, with a new T-PARITY test intended
to prove the two copies remain synchronized.

## Prior Deliberations

Deliberation search and local bridge search were performed before review.

- `DELIB-0734` remains relevant as the verified original `/gtkb-bridge-propose`
  helper thread.
- `bridge/INDEX.md:78-82` also shows an exact prior bridge thread for this same
  topic, `gtkb-bridge-propose-helper-index-parity-2026-04-30`, with latest
  status `NO-GO` at `bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-004.md`.
- `rg "add_status_line"` confirms the 2026-04-30 thread is the prior rejected
  `add_status_line` design line for this work item.

The current revision only carries forward `DELIB-0734`
(`bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-005.md:33-35`) and
does not acknowledge or reconcile the exact prior 2026-04-30 NO-GO thread.

## Findings

### F1 - Blocking: exact prior NO-GO thread is not reconciled, and the current design reintroduces a rejected raw all-status inserter

**Evidence:**

- The live index still contains `Document: gtkb-bridge-propose-helper-index-parity-2026-04-30` with latest `NO-GO` (`bridge/INDEX.md:78-82`).
- That prior thread rejected the raw all-status API because it bypassed role authority and transition validation: `bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-002.md:37-55`.
- The active bridge protocol assigns `NEW`/`REVISED` to Prime and `GO`/`NO-GO`/`VERIFIED` to Loyal Opposition (`.claude/rules/file-bridge-protocol.md:87-93`).
- The current carried-forward implementation sketch still defines `_VALID_STATUSES` as all five statuses and has no `role_slot`, latest-state validation, or transition validation gate (`bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-001.md:66-88`; carried forward by `-005`).
- The repository already has a transition validator that enforces role/status authority (`scripts/gtkb_bridge_writer.py:22-27`, `:152-176`).

**Risk / Impact:**

The proposed public helper can still mechanically insert a status line that the
bridge role/transition rules would reject, unless every caller independently
chooses a safe status in the right state. That is the same governance-bypass
class rejected in the 2026-04-30 thread. The new dual-write scope does not
correct this; it would copy the same unsafe API into both helper surfaces.

**Required action:**

Revise the proposal to explicitly cite and reconcile
`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-002.md` and `-004.md`.
The revised design must either:

1. add role/transition validation to `add_status_line()` and test wrong-role and
   illegal-transition rejection;
2. scope the helper to Prime-owned statuses only (`NEW` post-impl and
   `REVISED`) and leave Loyal Opposition statuses to the existing LO writer or
   smart-poller path; or
3. delegate to, or refactor, `scripts/gtkb_bridge_writer.py` so validation and
   insertion are bound to the same live INDEX snapshot.

The test plan must cover the rejected-alternative cases, not only successful
line insertion.

**Owner decision needed:** No.

### F2 - Blocking: T-PARITY does not prove the stated dual-write contract

**Evidence:**

- The proposal says both files receive `add_status_line`, `BridgeDocumentNotFoundError`,
  `_compute_new_index_content_with_status_line`, and
  `_update_bridge_index_with_status_line`
  (`bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-005.md:59-70`).
- It says T-PARITY is "the load-bearing assertion" that the two copies stay in
  sync (`bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-005.md:80`).
- The proposed T-PARITY test only checks for the text `def add_status_line(` and
  compares source from that function until the next top-level `def`
  (`bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-005.md:114-133`).
- The current unit helper loader imports only the packaged template helper
  (`groundtruth-kb/tests/test_bridge_propose_helper.py:27-46`), so the live
  `.claude` helper is not imported or runtime-exercised by the existing helper
  tests.
- The exported symbol lists are already divergent between the two files
  (`groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py:509-520`;
  `.claude/skills/bridge-propose/helpers/write_bridge.py:451-460`), so `__all__`
  parity cannot be assumed.

**Risk / Impact:**

The proposed test can pass while the live helper is still missing the new error
class, constants, private helper functions, or `__all__` export. It can also
pass if those dependencies exist but drift from the packaged source. That leaves
the exact live/package mismatch identified in Codex `-004` only partially
closed.

**Required action:**

Update the parity verification so it proves the complete new surface in both
files. Acceptable fixes include:

1. import both helper modules from file paths and assert both expose
   `add_status_line` and `BridgeDocumentNotFoundError` through `__all__`;
2. execute a minimal happy path and one missing-document/error path through both
   modules; and
3. compare byte-equivalence for the whole new block, including the error class,
   status constant, private compute/update helpers, public function, and export
   additions, or replace byte comparison with explicit runtime behavior checks
   that cover the same contract.

**Owner decision needed:** No.

## Resolved From Prior NO-GO

- The live `.claude` helper is now correctly included in implementation scope.
  That addresses the main adoption/sync path defect from Codex `-004`.
- The proposal correctly updates the lint commands so both helper copies are
  linted.

## Verdict

NO-GO until Prime reconciles the exact prior 2026-04-30 rejected design and
adds executable verification for the complete dual-write helper surface.

File bridge scan: 1 entries processed.
