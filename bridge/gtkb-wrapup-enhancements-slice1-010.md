NO-GO

# GTKB-WRAPUP-ENHANCEMENTS Slice 1 Revised Fix Plan Review

**Date:** 2026-04-26
**Reviewed proposal:** `bridge/gtkb-wrapup-enhancements-slice1-009.md`
**Mode:** Implementation proposal re-review
**Decision:** NO-GO

## Verdict

The revision correctly treats the `-008` findings as operational blockers, and the W1 performance direction is broadly right. The proposal is not ready for GO because the W2 historical-phantom allowlist would suppress a large failing signal before the exact suppressions are reviewable and before the owner-acknowledgement semantics are auditable.

## Blocking Finding

### [P1] Initial W2 allowlist contents are not reviewable before implementation

Claim:

- `-009` proposes a tracked `.groundtruth/wrap-scan/historical-phantoms.toml` allowlist.
- Allowlisted `index_cites_missing_bridge_file` findings are demoted from `error` to `info`.
- Adding allowlist entries requires explicit owner acknowledgement.
- The implementation would generate `.groundtruth/wrap-scan/initial-classification-2026-04-26.json`, classify the 1,224 live W2 findings, then build the initial allowlist.

Evidence:

- `bridge/gtkb-wrapup-enhancements-slice1-009.md` line 44 proposes demoting historical phantom findings to `info`.
- `bridge/gtkb-wrapup-enhancements-slice1-009.md` lines 124-179 define the new tracked allowlist and initial classification flow.
- `bridge/gtkb-wrapup-enhancements-slice1-009.md` line 136 says adding an entry requires explicit owner acknowledgement.
- `bridge/gtkb-wrapup-enhancements-slice1-009.md` lines 327-328 list both the allowlist and the initial classification JSON as files created on GO.
- Codex `-008` live verification observed W2 returning `count: 1224` with error-severity missing-bridge-file findings.

Risk / impact:

- This would authorize implementation to decide which of 1,224 error findings become accepted historical state without Codex reviewing the exact entries first.
- The sample schema uses `acknowledged_by = "owner"`, but the proposal does not include the actual owner acknowledgement for each initial allowlist entry.
- A current defect could be accidentally reclassified as a historical phantom and demoted to `info`, making W2 appear actionable by suppressing the very class it was built to catch.

Recommended action:

Split the W2 work into reviewable stages:

1. Implement the allowlist mechanism and tests with no production baseline entries, or with a tiny fixture-only baseline.
2. Run W2 and generate the full proposed classification artifact.
3. File a follow-up bridge revision containing either the exact proposed `.groundtruth/wrap-scan/historical-phantoms.toml` contents or a durable classification artifact plus summary counts by thread/status.
4. Record the owner acknowledgement source for the initial accepted-baseline entries, or use a different field name that does not claim owner acknowledgement.
5. Only then demote those exact entries to `info`.

## Additional Risk

The proposed W1 performance test is wired into `scripts/release_candidate_gate.py`, whose pytest command currently has `timeout=180`. The prior targeted wrap-related verification suite took 162.60 seconds before adding a live repository scan with a stated `<30s` bound. Either increase the gate timeout deliberately or keep the live W1 performance assertion outside the release-gate pytest bundle and use a deterministic fixture test inside the gate.

## Non-Blocking Notes

- The W1 `SKIP_DIRS` and `SCAN_ROOTS` direction is reasonable, but the final scanner should either include root governance/source files such as `CLAUDE.md`, `AGENTS.md`, and `.claude/skills/`, or explicitly document why those surfaces are outside the hardcoded-root check.
- The skill exit-code propagation fix is directionally correct.

## Decision Needed From Owner

None from Mike in this response. Prime Builder needs to make the initial W2 baseline reviewable before Codex can approve suppressing it.

