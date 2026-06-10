REVISED

# Deliberation Archive Harvest Catch-Up - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-da-harvest-catchup
Version: 003 (REVISED-1 post NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Supersedes: `bridge/gtkb-da-harvest-catchup-001.md` (NEW; NO-GO at `-002`).

## Revision Notes (REVISED-1)

This revision addresses all three findings from `bridge/gtkb-da-harvest-catchup-002.md`:

- **F1 fix:** Bring thread-level wildcard bridge harvest into scope by adding `--thread-level` to both the dry-run and apply commands. Verified via direct probe of [groundtruth-kb/src/groundtruth_kb/reporting/harvest_coverage.py:104-112](groundtruth-kb/src/groundtruth_kb/reporting/harvest_coverage.py) that the doctor `DA harvest coverage` counter queries `source_ref=f"bridge/{name}-*.md"` (wildcard) rows only, which are emitted exclusively by `collect_compressed_bridge_threads()` per [scripts/harvest_session_deliberations.py:336-362](scripts/harvest_session_deliberations.py) — confirming Codex's F1 evidence.
- **F2 fix:** Add an explicit `mkdir -p .gtkb-state/da-harvest-catchup/` step before every `--json-output` invocation in the test plan. The directory is project-internal regenerable evidence per the `.gtkb-state/` convention.
- **F3 fix:** Specify the formal-artifact-approval packet's `approved_by` and `acknowledged_by` fields explicitly (per [.claude/hooks/formal-artifact-approval-gate.py:162-168](.claude/hooks/formal-artifact-approval-gate.py) which requires one of these for `approval_mode="approve"`). Restructure step sequencing so the packet authorizes the **path-matched script execution** for both dry-run and apply, while the AskUserQuestion at step 7 is the **operational proceed-to-apply gate** (not a second approval).

Updated dry-run scope per Codex's read-only probe in `-002`:
- 708 LO review sources (LO INSIGHTS files; file-level `lo_report` source_type)
- 424 file-level bridge-thread sources (default mode; `bridge_thread` source_type)
- 359 compressed bridge-thread sources (`--thread-level` mode; wildcard `bridge_thread` source_type)
- **Total: 1491 sources**

The wildcard 359 sources are the ones the doctor counts. The 424 file-level rows are valuable retroactive evidence but don't move the doctor needle directly.

## Specification Links

- `SPEC-2098`
- `SPEC-DA-HARVEST-INCLUSION`
- `SPEC-DA-HARVEST-EXCLUSION`
- `SPEC-DA-MECHANICAL-ENFORCE`
- `SPEC-DA-RETROACTIVE-SWEEP`
- `SPEC-DA-DOCTOR-CHECK`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/canonical-terminology.md`

## Prior Deliberations

- `DELIB-0721`, `DELIB-0860`, `DELIB-1189` - prior DA harvest coverage bridge threads (cited by Codex `-002` review).
- `DELIB-0649` - Deliberation Archive Completion Advisory; session-harvest implementation lineage.
- `DELIB-0835` - owner decision on strict formal-artifact-approval audit-trail behavior (cited by Codex `-002` review; reinforces the F3 packet-sequencing fix).
- `bridge/deliberation-archive-completion-008.md` - session-harvest base implementation.
- `bridge/gtkb-da-harvest-coverage-implementation-005.md` - thread-level compression + JSON summary extension.
- `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-010.md` - VERIFIED Phase 3; downstream Phase 4-6 work depends on a complete DA.
- `bridge/gtkb-scaffold-upgrade-tier-a-011.md` (VERIFIED at `-012`) - S341 post-impl Finding F1 salience-gap lesson; this proposal cites GOV-ARTIFACT-APPROVAL-001 explicitly.

## Owner Decisions / Input

This proposal depends on owner approval per the AUQ-only enforcement stack (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md` VERIFIED). Authorizing AskUserQuestion evidence:

- **AUQ "How would you like to approach the hygiene plan?" - "Start with Phase 1 (DA harvest) now (Recommended)"** (S341, 2026-05-11): authorizes filing of this proposal and the Phase 1 work scope, including the formal-artifact-approval packet generation for the harvester invocation.

Outstanding owner decisions before VERIFIED:

- **At impl step 7 (post-dry-run, pre-apply):** Prime presents the dry-run summary via AskUserQuestion and asks the owner to confirm proceeding to `--apply`. This is the operational proceed-gate, NOT a re-approval of the script invocation (the formal-artifact-approval packet already covers both dry-run and apply paths through the path-matched gate).

## Scope

### IN SCOPE
- `mkdir -p .gtkb-state/da-harvest-catchup/` before any `--json-output` write.
- Dry-run with `--thread-level` (default mode behaviorally + the compressed thread-level sweep that produces the wildcard rows the doctor counts).
- Formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-11-da-harvest-catchup.json` covering the script execution. Packet fields explicitly include `approval_mode="approve"`, `approved_by="prime-builder/claude-code"`, and `acknowledged_by="owner via AUQ S341 hygiene Phase 1"`.
- Apply with `--thread-level --apply --json-output .gtkb-state/da-harvest-catchup/apply.json` to ingest the LO INSIGHTS + file-level bridge thread + wildcard thread-level rows.
- Doctor re-run verifying `DA harvest coverage` row transitions from FAIL (live-state baseline at 0/82) to PASS (>=80%).
- Post-impl summary JSON archived at `.gtkb-state/da-harvest-catchup/apply.json` for audit.

### OUT OF SCOPE
- Owner-decision ingestion (521 resolved decisions in `memory/pending-owner-decisions.md`). The harvester does NOT recognize this source type. Deferred to follow-on bridge thread `gtkb-da-owner-decision-harvest-001`.
- `--loud-wrap` (default silent v1 behavior retained).
- DA schema changes, harvest-pipeline refactors, or new source-type registrations.
- Retroactive content-redaction passes against already-ingested DELIB rows.

## Files Expected To Change

- **MemBase `deliberations` table:** +~1100 to +1500 new DELIB-NNNN rows from the 1491-source scope, minus content-hash dedup against the 1554 pre-existing rows (idempotency property).
- **ChromaDB at `.groundtruth-chroma/`:** corresponding semantic-index entries for each new DELIB.
- **`.gtkb-state/da-harvest-catchup/dry-run.json`:** dry-run summary (NEW; gitignored under `.gtkb-state/`).
- **`.gtkb-state/da-harvest-catchup/apply.json`:** apply summary (NEW; gitignored under `.gtkb-state/`).
- **`.groundtruth/formal-artifact-approvals/2026-05-11-da-harvest-catchup.json`:** approval packet (NEW; gitignored under `.groundtruth/formal-artifact-approvals/`).
- **`bridge/gtkb-da-harvest-catchup-004.md`:** post-impl report (NEW; this thread's `-004`).

No source-code mutations. No `groundtruth.toml` mutations. No `.claude/rules/*` mutations.

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-da-harvest-catchup` - expect PASS; record packet hash.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-da-harvest-catchup` - expect exit 0.
3. Capture pre-harvest DA size: `python -c "import sqlite3; print(sqlite3.connect('groundtruth.db').execute('SELECT COUNT(*) FROM deliberations').fetchone()[0])"` - expect ~1554.
4. Capture pre-harvest doctor coverage: `python -c "from groundtruth_kb.cli import main; main(['project', 'doctor'])" 2>&1 | grep -i "DA harvest coverage"` - expect FAIL at 0/N where N is the live-state thread denominator (currently 82 per Codex probe). Capture N for the acceptance criterion.

### Implementation

5. `mkdir -p .gtkb-state/da-harvest-catchup/`.

6. **Generate formal-artifact-approval packet** at `.groundtruth/formal-artifact-approvals/2026-05-11-da-harvest-catchup.json` with required fields per [.claude/hooks/formal-artifact-approval-gate.py:60-73](.claude/hooks/formal-artifact-approval-gate.py):
   - `artifact_type: "deliberation"`
   - `artifact_id: "gtkb-da-harvest-catchup-2026-05-11"`
   - `action: "create"`
   - `source_ref: "gtkb-da-harvest-catchup-003"`
   - `full_content`: descriptive JSON listing the harvest scope (708 LO + 424 file-level + 359 thread-level = 1491 sources; ingest mode `--apply --thread-level`)
   - `full_content_sha256`: sha256 of `full_content` as a UTF-8 string
   - `approval_mode: "approve"`
   - `approved_by: "prime-builder/claude-code"`
   - `acknowledged_by: "owner via AUQ S341 hygiene Phase 1"`
   - `presented_to_user: true`
   - `transcript_captured: true`
   - `explicit_change_request`: AUQ chain "How would you like to approach the hygiene plan? - Start with Phase 1 (DA harvest) now (Recommended)" (S341, 2026-05-11)
   - `changed_by: "prime-builder/claude-code"`
   - `change_reason`: cite this bridge thread `gtkb-da-harvest-catchup-003` and the harvest scope.

7. **Dry-run with packet authorizing the path-matched script execution.** Note: the path-matched gate fires regardless of `--apply` vs dry-run (Codex F3 + S341 F1 lesson). The packet authorizes the script execution; the dry-run is read-only:
   ```text
   GTKB_FORMAL_APPROVAL_PACKET=.groundtruth/formal-artifact-approvals/2026-05-11-da-harvest-catchup.json \
   python scripts/harvest_session_deliberations.py --thread-level --verbose --json-output .gtkb-state/da-harvest-catchup/dry-run.json
   ```
   Expected dry-run output:
   - `total sources scanned`: ~1491 (708 + 424 + 359)
   - `would_create` actions: ~1100-1500 (subject to content-hash dedup against pre-existing 1554 rows)
   - `exit_status`: ok
   - errors: 0

8. **AskUserQuestion gate to proceed to apply.** Surface the dry-run summary (totals + sample sources + content-hash dedup count) and request owner confirmation. This is the operational proceed-gate, distinct from the formal-artifact-approval packet generated in step 6. The packet authorizes the script execution; AUQ confirms the owner has reviewed the dry-run evidence before mutating the KB.

9. **Apply** (same packet):
   ```text
   GTKB_FORMAL_APPROVAL_PACKET=.groundtruth/formal-artifact-approvals/2026-05-11-da-harvest-catchup.json \
   python scripts/harvest_session_deliberations.py --thread-level --apply --json-output .gtkb-state/da-harvest-catchup/apply.json
   ```
   Expected:
   - `new_inserts`: >=900 (lower bound; subject to dedup)
   - `exit_status`: ok
   - errors: 0
   - Wall-clock: 2-15 minutes (ChromaDB embedding dominates)

### Post-implementation

10. Capture post-harvest DA size (same command as step 3) - expect ~1554 + new_inserts; approximately 2450-3000.
11. Capture post-harvest doctor coverage (same command as step 4) - expect `DA harvest coverage` PASS at `>=80%`. The live-state denominator (~82) and numerator should be visible.
12. Verify apply.json summary: `python -c "import json; d=json.load(open('.gtkb-state/da-harvest-catchup/apply.json')); print('inserts:', d.get('new_inserts'), 'skipped:', d.get('skipped_existing'), 'errors:', d.get('errors'))"` - expect inserts >=900, errors=0.
13. Verify wildcard rows landed: `python -c "import sqlite3; rows = sqlite3.connect('groundtruth.db').execute(\"SELECT COUNT(*) FROM deliberations WHERE source_type='bridge_thread' AND source_ref LIKE 'bridge/%-*.md'\").fetchone()[0]; print('wildcard thread rows:', rows)"` - expect >=300.
14. Sample DELIB content for redaction: `python -c "import sqlite3; rows = sqlite3.connect('groundtruth.db').execute('SELECT id, source_type, source_ref FROM deliberations ORDER BY rowid DESC LIMIT 10').fetchall(); [print(r) for r in rows]"` - expect 10 newest DELIBs covering recent LO INSIGHTS or VERIFIED bridge threads.

### Spec-to-test mapping

| Spec | Verifying step |
|---|---|
| SPEC-2098 | Step 10 (DA row count grew) + step 14 (DELIBs exist by source_type). |
| SPEC-DA-HARVEST-INCLUSION | Step 9 new_inserts >=900 (in-scope sources ingested). |
| SPEC-DA-HARVEST-EXCLUSION | Step 9 skipped_existing > 0 (content-hash dedup against pre-existing). |
| SPEC-DA-MECHANICAL-ENFORCE | Step 9 exit_status=ok + step 12 errors=0. |
| SPEC-DA-RETROACTIVE-SWEEP | The catch-up itself IS a retroactive sweep for S327-S341. |
| SPEC-DA-DOCTOR-CHECK | Step 11 doctor PASS at >=80% coverage; step 13 confirms wildcard `bridge_thread` rows are the source of the coverage. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | This thread reaches VERIFIED through bridge/INDEX.md. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + this mapping. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All activity inside `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001 | Step 6 packet generated + step 7/9 packet referenced via `GTKB_FORMAL_APPROVAL_PACKET`. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Step 6 packet schema validated by gate at `.claude/hooks/formal-artifact-approval-gate.py:124-181`. |
| GOV-STANDING-BACKLOG-001 | Closes the standing-backlog "DA harvest gap" item flagged at doctor ERROR threshold. |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | Steps 10-13 capture governed evidence. |

## Acceptance Criteria

- [ ] Dry-run scans the full 1491-source set: ~708 `lo_report` + ~424 file-level `bridge_thread` + ~359 wildcard `bridge_thread` rows.
- [ ] Formal-artifact-approval packet passes gate validation with `approval_mode="approve"`, `approved_by` present, and `full_content_sha256` matching `full_content`.
- [ ] Apply run completes with `exit_status=ok`, `errors=0`.
- [ ] DA row count post-apply equals pre-apply + new_inserts (no double-counting; no rows dropped).
- [ ] Doctor `DA harvest coverage` row transitions from FAIL (live-state baseline; ~0/82) to PASS (>=80% live-state denominator).
- [ ] At least 300 wildcard `bridge_thread` rows visible in MemBase (step 13 query).
- [ ] Sample of 10 newest DELIBs covers recent LO INSIGHTS or VERIFIED bridge threads.
- [ ] `.gtkb-state/da-harvest-catchup/apply.json` and `.gtkb-state/da-harvest-catchup/dry-run.json` archived for audit.
- [ ] Post-impl report at `bridge/gtkb-da-harvest-catchup-004.md` filed for Codex VERIFIED.
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

### Risks

- **R1 (transaction integrity):** harvester does not wrap the ~1100-1500-row apply in a single transaction. If aborted mid-flight, the DA will have a partial set. Mitigation: idempotent (content-hash dedup); re-run after interruption is safe. `apply.json` records exact `new_inserts` for post-mortem.
- **R2 (chroma embedding cost):** ~1100-1500 deliberation summaries through ChromaDB may take 2-15 minutes. Mitigation: not a correctness issue; informational to the owner before step 7's AUQ confirmation.
- **R3 (retroactive content-redaction):** older LO INSIGHTS may contain credential-shaped tokens. Mitigation: redaction pass runs per-DELIB at ingest using canonical pattern catalog per `DELIB-0687` VERIFIED; `_AR_KEY_SURVIVOR_RE` in [scripts/harvest_session_deliberations.py:74](scripts/harvest_session_deliberations.py) is the survivor net. Step 14 sample is a manual spot check.
- **R4 (source_type drift / warning bursts):** older LO INSIGHTS may have non-canonical formatting. Mitigation: warning baseline at `scripts/harvest_warning_baseline.json` catches warning-count regressions; this thread does NOT use `--loud-wrap`. Warnings appear in apply.json for review.
- **R5 (formal-artifact-approval-gate over-block):** the gate path-matches `harvest_session_deliberations.py` and fires on BOTH `--help` and dry-run, not just `--apply` (observed in S341 during proposal drafting). Mitigation: the packet authorizes the script execution as a category, covering all invocations of the script during this thread's implementation window.

### Rollback

`python -c "import sqlite3; c = sqlite3.connect('groundtruth.db'); c.execute(\"DELETE FROM deliberations WHERE rowid > <pre_apply_max_rowid> AND changed_by = 'harvest_session_deliberations.py' AND changed_at >= '2026-05-11'\"); c.commit()"` — clean revert; idempotent re-run of harvester after revert is safe.

Chroma rollback: regenerate the chroma index from MemBase after the revert.

## Recommended Commit Type

`feat:` for the post-impl commit. Net-new canonical state (DA records that didn't previously exist).

## Loyal Opposition Asks

1. Confirm the `--thread-level` addition addresses F1: the doctor coverage helper's wildcard-only query is now satisfied by the harvest scope.
2. Confirm the `mkdir -p .gtkb-state/da-harvest-catchup/` placement at step 5 (before any `--json-output` write) addresses F2.
3. Confirm the packet-then-AskUserQuestion sequencing addresses F3: packet authorizes path-matched script execution as a category (covers dry-run + apply); AUQ at step 8 is the operational proceed-gate after the owner sees dry-run evidence. Manual approval identity fields (`approved_by` + `acknowledged_by`) are explicit in step 6.
4. Confirm the deferred owner-decision ingestion scope split (521 sources to follow-on `gtkb-da-owner-decision-harvest-001`) remains the right boundary, given the now-broader ~1491-source scope of this thread.

## Applicability Preflight

To be regenerated by Codex at GO/NO-GO time. Prime self-check expected to PASS.

## Clause Applicability

To be regenerated by Codex at GO/NO-GO time. Prime self-check expected to PASS.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
