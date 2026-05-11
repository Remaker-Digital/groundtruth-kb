NEW

# Deliberation Archive Harvest Catch-Up (S327-S341)

bridge_kind: implementation_proposal
Document: gtkb-da-harvest-catchup
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Claim

The session-start doctor reports `[FAIL] DA harvest coverage: 0.00% (0/81) below ERROR threshold 80.0%`. Direct live probe confirms the gap is much larger than the doctor's 81-row sample suggests:

- **DA current rows:** 1554 (probed via `sqlite3 groundtruth.db ... SELECT COUNT(*) FROM deliberations`).
- **LO INSIGHTS files in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`:** 708 unharvested.
- **Resolved owner decisions in `memory/pending-owner-decisions.md`:** 521.
- **Bridge files total:** 2650 (across ~366 threads per session memory; ~291 uncovered per S341 hygiene audit).

This proposal runs the existing harvester at `scripts/harvest_session_deliberations.py` to close the LO-INSIGHTS + bridge-thread portion of the gap (~998 sources). Owner-decision ingestion (521 sources) is **out of scope** because the existing harvester doesn't recognize that source type; it will be addressed in a follow-on thread once the LO/bridge harvest baseline is established.

The harvester is incremental and content-hash deduped, so the operation is idempotent and resumable. Default mode is dry-run; `--apply` is required to mutate. A formal-artifact-approval packet is required because `harvest_session_deliberations.py` matches the FORMAL_MUTATION_PATTERNS in `.claude/hooks/formal-artifact-approval-gate.py:54`.

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

- `bridge/deliberation-archive-completion-008.md` - session-harvest base implementation; cited in `scripts/harvest_session_deliberations.py:34` as the GO chain anchor.
- `bridge/gtkb-da-harvest-coverage-implementation-005.md` - thread-level compression + JSON summary extension; cited in `scripts/harvest_session_deliberations.py:35`.
- `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-010.md` - VERIFIED Phase 3; established the glossary as the DA read surface (downstream Phase 4-6 work depends on a complete DA).
- `bridge/gtkb-scaffold-upgrade-tier-a-011.md` - S341 post-impl report's Finding F1 surfaced GOV-ARTIFACT-APPROVAL-001 as a salience gap; this proposal cites it explicitly to avoid the same gap.

## Owner Decisions / Input

This proposal depends on owner approval per the AUQ-only enforcement stack (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md` VERIFIED). Authorizing AskUserQuestion evidence:

- **AUQ "How would you like to approach the hygiene plan?" - "Start with Phase 1 (DA harvest) now (Recommended)"** (S341, 2026-05-11): authorizes filing of this proposal and the Phase 1 work scope.

Outstanding owner decisions before VERIFIED:

- **At impl time:** owner must approve the formal-artifact-approval packet that authorizes the `--apply` run (the gate is path-matched and fires regardless of `--apply` vs dry-run; packet covers both). Prime will surface the packet for owner inspection via AskUserQuestion before the `--apply` invocation.

## Scope

### IN SCOPE
- Dry-run `python scripts/harvest_session_deliberations.py` (default mode; no KB mutation) to confirm pre-state and exact source counts.
- Generate a deliberation-class formal-artifact-approval packet covering the harvest invocation. Packet records the AUQ + hygiene-plan scope authorization.
- `python scripts/harvest_session_deliberations.py --apply --json-output .gtkb-state/da-harvest-catchup/summary.json` to ingest the LO INSIGHTS + bridge-thread gap.
- Doctor re-run verifying DA coverage rises from 0/81 ERROR to >= 80% PASS.
- Post-impl summary JSON archived under `.gtkb-state/da-harvest-catchup/` for audit.

### OUT OF SCOPE
- Owner-decision ingestion (521 resolved decisions in `memory/pending-owner-decisions.md`). The harvester at `scripts/harvest_session_deliberations.py` does NOT currently recognize this source type. Closing this gap requires either (a) extending the harvester to read pending-owner-decisions.md, or (b) authoring a separate ingestion script. Owner-decision ingestion is deferred to a follow-on bridge thread `gtkb-da-owner-decision-harvest-001` to be filed after this proposal completes.
- Compressed thread-level harvest via `--thread-level`. Default v1 behavior (file-level only) is retained per `scripts/harvest_session_deliberations.py:772`.
- DA schema changes, harvest-pipeline refactors, or new source-type registrations.
- Retroactive content-redaction passes against already-ingested DELIB rows.

## Files Expected To Change

- **MemBase `deliberations` table:** +~900 to +1000 new DELIB-NNNN rows (998 sources minus any that fail content-hash validation or are filtered by exclusion rules per SPEC-DA-HARVEST-EXCLUSION).
- **ChromaDB at `.groundtruth-chroma/`:** corresponding semantic-index entries for each new DELIB.
- **`.gtkb-state/da-harvest-catchup/summary.json`:** machine-readable harvest summary (NEW; gitignored under `.gtkb-state/`).
- **`.groundtruth/formal-artifact-approvals/2026-05-11-da-harvest-catchup.json`:** approval packet (NEW; gitignored under `.groundtruth/formal-artifact-approvals/`).
- **`bridge/gtkb-da-harvest-catchup-002.md`:** post-impl report (NEW; this thread's `-002`).

No source-code mutations. No `groundtruth.toml` mutations. No `.claude/rules/*` mutations.

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-da-harvest-catchup` - expect PASS; record packet hash.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-da-harvest-catchup` - expect exit 0.

### Implementation

3. Capture pre-harvest DA size: `python -c "import sqlite3; print(sqlite3.connect('groundtruth.db').execute('SELECT COUNT(*) FROM deliberations').fetchone()[0])"` - expect 1554.
4. Capture pre-harvest doctor state: `python -c "from groundtruth_kb.cli import main; main(['project', 'doctor'])" 2>&1 | grep "DA harvest coverage"` - expect `0.00% (0/81) below ERROR threshold 80.0%`.
5. Generate formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-11-da-harvest-catchup.json` with required fields per `.claude/hooks/formal-artifact-approval-gate.py:60-73` (artifact_type=deliberation, source_ref=gtkb-da-harvest-catchup-001, full_content listing the harvest scope + AUQ evidence, full_content_sha256, approval_mode=approve, presented_to_user=true, transcript_captured=true, explicit_change_request citing AUQ + Codex GO chain, changed_by=prime-builder/claude-code, change_reason).
6. Dry-run with packet: `GTKB_FORMAL_APPROVAL_PACKET=<packet-path> python scripts/harvest_session_deliberations.py --verbose --json-output .gtkb-state/da-harvest-catchup/dry-run.json` - expect dry-run report with ~900-1000 "would_create" actions across `lo_report` and `bridge_thread` source types, near-zero errors.
7. AskUserQuestion: present the dry-run summary to owner; confirm to proceed.
8. Apply: `GTKB_FORMAL_APPROVAL_PACKET=<packet-path> python scripts/harvest_session_deliberations.py --apply --json-output .gtkb-state/da-harvest-catchup/apply.json` - expect new_inserts >= 900, exit_status=ok, no errors. Run time estimate: 2-10 minutes depending on ChromaDB embedding throughput.

### Post-implementation

9. Capture post-harvest DA size (same command as step 3) - expect 1554 + (new_inserts from step 8); approximately 2450-2550.
10. Capture post-harvest doctor state (same command as step 4) - expect DA harvest coverage at PASS (>= 80%).
11. Verify the apply.json summary: `python -c "import json; d=json.load(open('.gtkb-state/da-harvest-catchup/apply.json')); print('inserts:', d['new_inserts'], 'skipped:', d['skipped_existing'], 'errors:', d.get('errors', 0))"` - expect inserts >= 900, errors = 0.
12. Sample DELIB content for redaction: `python -c "import sqlite3; rows = sqlite3.connect('groundtruth.db').execute('SELECT id, source_type, source_ref FROM deliberations ORDER BY rowid DESC LIMIT 10').fetchall(); [print(r) for r in rows]"` - expect 10 newest DELIBs covering recent LO INSIGHTS or bridge VERIFIED threads.

### Spec-to-test mapping

| Spec | Verifying step |
|---|---|
| SPEC-2098 (DA feature) | Step 9 (DA row count grew) + step 12 (DELIBs exist by source_type). |
| SPEC-DA-HARVEST-INCLUSION | Step 8 new_inserts >= 900 (covers in-scope source types). |
| SPEC-DA-HARVEST-EXCLUSION | Step 8 skipped_existing > 0 (content-hash dedup against the 1554 pre-existing DELIBs). |
| SPEC-DA-MECHANICAL-ENFORCE | Step 8 exit_status = ok + step 11 errors = 0 (mechanical pipeline integrity). |
| SPEC-DA-RETROACTIVE-SWEEP | The catch-up itself IS a retroactive sweep for S327-S341 sessions. |
| SPEC-DA-DOCTOR-CHECK | Step 10 doctor PASS at >=80% coverage. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | This thread reaches VERIFIED through bridge/INDEX.md. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + this mapping. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Step 4 + step 10 (all activity inside `E:\GT-KB`). |
| GOV-ARTIFACT-APPROVAL-001 | Step 5 packet generated + step 6/8 packet referenced via `GTKB_FORMAL_APPROVAL_PACKET`. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Step 5 packet schema validated by gate at `.claude/hooks/formal-artifact-approval-gate.py:124-181`. |
| GOV-STANDING-BACKLOG-001 | Closes the standing-backlog "DA harvest gap" item flagged at doctor ERROR threshold. |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | Steps 9-11 capture governed evidence; doctor verifies release-gate impact. |

## Acceptance Criteria

- [ ] Dry-run reports >= 900 `would_create` actions across `lo_report` and `bridge_thread` source types.
- [ ] Formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-11-da-harvest-catchup.json` passes gate validation.
- [ ] Apply run completes with `exit_status=ok`, `errors=0`.
- [ ] DA row count post-apply equals pre-apply + new_inserts (no double-counting; no rows dropped).
- [ ] Doctor `DA harvest coverage` row transitions from FAIL (0.00%, 0/81) to PASS (>= 80%).
- [ ] Sample of 10 newest DELIBs covers recent LO INSIGHTS or VERIFIED bridge threads (no obvious harvest errors).
- [ ] `.gtkb-state/da-harvest-catchup/apply.json` is archived for audit.
- [ ] Post-impl report at `bridge/gtkb-da-harvest-catchup-002.md` filed for Codex VERIFIED.
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

### Risks

- **R1 (transaction integrity):** the harvester does not wrap the ~900-row apply in a single transaction. If the run aborts mid-flight (e.g., session interrupt), the DA will have a partial set of new rows. Mitigation: the harvester is content-hash deduped and idempotent, so re-running after interruption is safe. The `apply.json` records new_inserts for accurate post-mortem.
- **R2 (chroma embedding cost):** embedding ~900-1000 deliberation summaries through the local ChromaDB instance may take 2-10 minutes. Mitigation: not a correctness issue; just slow. The owner is informed of the time window before the apply run.
- **R3 (retroactive content-redaction):** older LO INSIGHTS may contain credential-shaped tokens that the current redactor doesn't catch. Mitigation: the redaction pass runs per-DELIB at ingest time using the canonical pattern catalog per `DELIB-0687` VERIFIED Credential Scan Narrowing; any survivors should be caught by `_AR_KEY_SURVIVOR_RE` in `scripts/harvest_session_deliberations.py:74`. Sample of the newest 10 DELIBs (step 12) is a manual spot check.
- **R4 (source_type drift):** some older LO INSIGHTS may have non-canonical formatting that confuses the harvester's source_type detection. Mitigation: the warning baseline at `scripts/harvest_warning_baseline.json` catches warning-count regressions; the harvest exits non-zero if warnings exceed baseline + `--loud-wrap`. This thread does NOT use `--loud-wrap` (default silent) but warnings are surfaced in the apply.json for review.
- **R5 (formal-artifact-approval-gate over-block):** the gate at `.claude/hooks/formal-artifact-approval-gate.py:54` path-matches the script name regardless of `--apply` vs dry-run. The packet is required for BOTH invocations. Mitigation: this proposal explicitly cites the gate (per S341 F1 lesson) and budgets the packet-generation step in the test plan.

### Rollback

If the apply run mints inserts that the owner later wishes to revert: `python -c "import sqlite3; c = sqlite3.connect('groundtruth.db'); c.execute(\"DELETE FROM deliberations WHERE rowid > 1554 AND changed_by = 'harvest_session_deliberations.py' AND changed_at >= '2026-05-11'\"); c.commit()"` is a clean revert path. The apply.json's new_inserts count + the changed_at timestamp + the changed_by attribution jointly anchor the revert. Re-running the harvester after the revert is idempotent.

For chroma rollback: regenerate the chroma index from MemBase after the revert (the chroma store is derived; no canonical state lives only there).

## Recommended Commit Type

`feat:` for the post-impl commit. Net-new canonical state (DA records that didn't previously exist). Matches the S333 audit's commit-discipline rule: do NOT use `chore:` for sweeping infrastructure work.

## Loyal Opposition Asks

1. Confirm the scope split between this thread (LO INSIGHTS + bridge threads, ~998 sources) and the follow-on thread (owner decisions, 521 sources) is the right boundary. Alternative: extend the harvester in this same thread to handle all three source types; tradeoff is wider scope + larger surface for review.
2. Confirm the formal-artifact-approval packet structure proposed in step 5 satisfies `GOV-ARTIFACT-APPROVAL-001` for a deliberation-class mutation that ingests many DELIBs in one operation. Alternative: require one packet per DELIB (heavy ceremony; rejected as impractical).
3. Confirm the dry-run -> AskUserQuestion -> apply gate (step 6 -> 7 -> 8) is sufficient owner-visibility before a ~900-row mutation. Alternative: require owner approval per source_type batch (more granular but slower).
4. Confirm acceptance criteria's "DA harvest coverage >= 80%" PASS is the right doctor target. The current ERROR threshold is 80%; raising to a stricter target (e.g., 95%) would require accounting for the owner-decision gap that this thread defers.

## Applicability Preflight

To be generated by Codex at GO/NO-GO time. Prime self-check expected to PASS.

## Clause Applicability

To be generated by Codex at GO/NO-GO time. Prime self-check expected to PASS (the proposal cites GOV-ARTIFACT-APPROVAL-001 + DCL-ARTIFACT-APPROVAL-HOOK-001 explicitly, addressing the S341 F1 salience gap).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
