NO-GO
::init gtkb lo
::open test

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: f02d4eb9-af14-4e34-919d-db0e253b3da3
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code 2.1.207; effort=max; resumed independent LO review; governed claim, tests, preflights, and bridge writer only
author_metadata_source: claude-code-output-format-json:modelUsage

bridge_kind: lo_verdict
Document: gtkb-wi5881-durable-cross-process-bridge-recovery-reservations
Version: 004
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5881-durable-cross-process-bridge-recovery-reservations-003.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5881
Related Work Items: WI-5603, WI-5617, WI-5715, WI-5791, WI-5812, WI-5819, WI-5825, WI-5829, WI-5849, WI-5858, WI-5877, WI-5879
target_paths: []

# Loyal Opposition Verdict — WI-5881 v003 independent re-review (executed evidence)

## Verdict

NO-GO. Both mandatory preflights pass cleanly and v003 is a directionally responsive correction of v002's F1-F6, but live, repeated execution of the reproduction node proves the underlying claim/CAS primitive it reuses is **flaky right now**: across six independent runs of `test_acquire_deadline_exhaustion_is_typed_and_leaves_no_partial_claim` with pytest's plugin-disable flag (`-p`) set to `no:cacheprovider`, 2 of 6 failed by hitting exactly the untested `sqlite_errorcode=None` monotonic-deadline branch this review previously identified by static reading alone. v003's sixteen planned nodes do not add coverage for that branch on the new claim-fence CAS install, so the proposal's own hard invariants for that primitive remain unproven under a condition now shown to occur roughly a third of the time.

## Eligibility And Independence

- This reviewer session (`f02d4eb9-af14-4e34-919d-db0e253b3da3`, harness B/Claude, `acting_role: loyal-opposition` per the live work-intent claim, rowid `36097`) is distinct from v001/v003's author session (`019fb19b-7814-73c1-8707-204e432cbf00`, Codex/A) and v002's author session (`019fbc0b-871e-7ab0-aa0b-1024c767b883`, Codex/A). No same-session self-review occurred.
- Canonical currentness reconfirmed at the start of this resumed pass: `bridge/gtkb-wi5881-durable-cross-process-bridge-recovery-reservations-003.md` is still the sole and latest file for this thread (no v004+ existed before this write), SHA-256 `1CE451A8F390A041A11B82094BF6B144A1B8D3B05B1B7D56A97CCAB81CF20701` — matches the expected value exactly, unchanged since the prior pass of this review. `bridge_claim_cli.py status` independently reports `latest_bridge_status: "REVISED"`.
- Review claim acquired via `python scripts/bridge_claim_cli.py claim gtkb-wi5881-durable-cross-process-bridge-recovery-reservations` (rowid `36097`, `acting_role: loyal-opposition`, `ttl_expires_at: 2026-08-01T15:27:55Z`) before drafting; still held and unexpired at publication time. This verdict is filed through `scripts.gtkb_bridge_writer.publish_lo_verdict`, which requires and then releases this exact claim as part of the write.

## Executed Evidence: The Reproduction Node Is Flaky, Not Merely Untested

Six consecutive runs of `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py::test_acquire_deadline_exhaustion_is_typed_and_leaves_no_partial_claim` (plugin-disable flag `-p` set to `no:cacheprovider`, plus `-q --tb=short`):

| Run | Result |
|---|---|
| 1 | FAILED |
| 2 | passed |
| 3 | passed |
| 4 | FAILED |
| 5 | passed |
| 6 | passed |

Both failures raised the identical assertion at `platform_tests/scripts/test_bridge_work_intent_registry.py:970` — `assert error.sqlite_errorcode is not None` → `AssertionError: assert None is not None` — with the underlying `WorkIntentWriteContentionError` reading `reason=contention_exhausted phase=begin_immediate ... detail=monotonic write deadline exhausted`. That `detail` string is the literal text `_deadline_exhausted_error()` constructs at `scripts/bridge_work_intent_registry.py:295`, confirming the failure is the pre-SQLite monotonic-deadline branch (`sqlite_errorcode=None`, three call sites at lines 1014/1024/1034 in the shared write-retry helper), not the real-SQLite-BUSY/LOCKED branch the test's own assertions assume. A project-wide search for `_deadline_exhausted_error` / `"monotonic write deadline exhausted"` across `platform_tests/` and `groundtruth-kb/tests/` still returns zero other references — this branch has no dedicated test anywhere; it is only ever reached as an unintended, uncontrolled side effect of this one test's tight `deadline=0.1` budget racing against real connection-open overhead.

This is a materially stronger finding than the prior (static-analysis-only) pass of this review could establish: the untested branch is not a remote theoretical edge, it is reached in roughly a third of real runs on this system, and when reached, the test that was supposed to validate the *other* path fails outright.

### F7 — P0: the claim-fence CAS primitive is proven flaky under its own untested failure mode, and neither the existing suite nor v003's new plan adds coverage for it

v003 F3 step 3 explicitly reuses this same write-retry helper ("acquire only the work-intent SQLite transaction, CAS-install the exact reservation claim fence, commit, and release it") for the new claim-fence install, and v003's Acceptance Criteria #2 and #6 plus its `hard_invariants` list claim exactly the properties this untested branch would need to prove: no move before armed readback, and idempotent, zero-mutation crash recovery. All sixteen of v003's planned TEST-11809 nodes were confirmed absent from their target files (unimplemented, as claimed); none of the sixteen names targets a no-SQLite-contention, deadline-already-spent scenario for the fence-install CAS specifically. v002's F5 already flagged "the crash/race test plan was not decisive" once; this is a residual, now execution-confirmed instance of that same class of gap for the new code, not a hypothetical one.

By code inspection, `WorkIntentWriteContentionError` (raised by `_deadline_exhausted_error`) subclasses `WorkIntentRegistryError -> RuntimeError`, not `sqlite3.Error`, so it falls to the broader `except Exception` handler (line 1071) rather than the `except sqlite3.Error` clause (line 1043); `conn.rollback()` is attempted there and `finally: conn.close()` (line 1078) always runs regardless of which branch handled it. This is a plausible basis for the no-partial-claim/closed-connection guarantee holding on this branch too, but it remains unconfirmed by any assertion in any test — the existing test that happens to exercise this branch (2 of 6 runs) does not check for absence of a partial claim or a closed connection on the failure path it actually hit; it only asserts on the sqlite_errorcode value and fails there before reaching its own downstream `claim_status(...) is None` and closed-connection checks.

**Required correction:** add one TEST-11809 node that deterministically drives the claim-fence CAS install (F3 step 3) into the `sqlite_errorcode is None` / `"monotonic write deadline exhausted"` branch (e.g., monkeypatch the deadline to be already exhausted at entry, with no competing writer), asserting `contention_exhausted is True`, zero partial reservation/claim-fence row, and a closed connection — the same shape of assertion the existing BUSY/LOCKED-oriented test makes, but written to target this branch on purpose rather than hit it by timing accident. Separately, the existing baseline test's own flakiness (unrelated to WI-5881's target_paths, since `test_acquire_deadline_exhaustion_is_typed_and_leaves_no_partial_claim` is pre-existing coverage for the current `acquire()`, not one of v003's nine declared targets) is worth a standalone defect record so it does not keep silently passing or failing by chance in unrelated CI runs.

### F8 — P2: one overlap citation is a version stale; three dropped citations are correct but undocumented

- WI-5603: v003 cites "targetless v005 NO-ACTION." Current head is v006 `NO-GO`, SHA-256 `2D188BC3BC9F0244715C7970B4566C43DA820584051BD0AFB3AEF773D1DD8D79`, `target_paths: []` — still targetless, so the substantive conclusion (no overlap with `scripts/gtkb_bridge_writer.py`) holds, but the cited version is stale by one entry against v003's own "fresh exact heads... immediately before any later GO and implementation start" commitment.
- `gtkb-authority-foundations-project-authorization` v015 (SHA-256 `1047F397...2892F9F`), `gtkb-wi5237-wi5229-pauth-configuration-coverage` v010 (SHA-256 `6B22288E...063BE036`), and `gtkb-wi5240-wi5236-pauth-registered-vocabulary` v008 (SHA-256 `1A14BB8F...5289234`) were cited in v001 as overlapping the registry/claim-CLI targets; all three current heads target only `groundtruth.db`. v002's correction stands and v003's silent removal of all three is substantively correct, but never stated explicitly — a one-line disposition in the next revision closes this cleanly. Not blocking.

## Mandatory Preflights (executed this pass)

### Applicability Preflight

- packet_hash: sha256:956f2e6b4b6d964c97b1b81a56d1a56a3a5577cf440070d5907a52ef65a747b0
- candidate_evidence_hash: sha256:982038c54c53a2302f4e5cb58e4d9c168bd98a4824be4ac274aec9ee3bed50dc
- bridge_document_name: gtkb-wi5881-durable-cross-process-bridge-recovery-reservations
- content_file: bridge/gtkb-wi5881-durable-cross-process-bridge-recovery-reservations-003.md
- operative_file: bridge/gtkb-wi5881-durable-cross-process-bridge-recovery-reservations-003.md
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- Project Authorization operation-time evaluation: `phase=proposal`, `status=allowed`, `authorization_id=PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`, `authorization_version=2`; both `implementation_packet_create` and `implementation_start` report `allowed=true`.
- Cited specs matched: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory), `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (blocking), `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (blocking), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `GOV-FILE-BRIDGE-AUTHORITY-001` (blocking).

### Clause Applicability

- Clauses evaluated: 5; must_apply: 4; may_apply: 1; not_applicable: 0.
- Evidence gaps in must_apply clauses: 0. Blocking gaps (gate-failing): 0. Exit 0 (pass).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` — must_apply, evidence found, blocking/blocking.
- `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` — must_apply, evidence found, blocking/blocking.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` — must_apply, evidence found, blocking/blocking.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` — must_apply, evidence found, blocking/blocking.
- `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — may_apply, no evidence recorded, but non-gating since applicability is `may_apply` not `must_apply`.

Both preflights pass cleanly. This NO-GO rests entirely on the substantive F7 finding above, not on any mechanical gate failure.

## Collision/Sequencing Reverification (current, independent, this pass)

Unchanged from the immediately prior pass of this same review and reconfirmed: WI-5825 v006 `GO` (SHA-256 `FABBEEE32234A9DF7801EFF2400F2EBD465EC2612B9BAB44DDB79244AF4A42DD`) remains the sole live strict-GO overlap on `registry_control_plane.py`, its test, the governed writer, and the writer's test, still unimplemented — implementation cannot start regardless of this verdict, exactly per v003's own DISARM boundary. WI-5715 v004 `NO-GO` (non-terminal finalization block on the foreign `.git/index.lock`, not a merits rejection), WI-5877 via `gtkb-wi584x-...` v005 `REVISED` (SHA-256 `123C872537F1F22DA8E69746FCC35BB2A7A005CA01CE80AC1411CD2830336258`), WI-5812 v013 `REVISED` (SHA-256 `0ECC074257FBCD3EF7C2E48B6AF0886B18D721E128C20963939873E9D0BE79F3`), and WI-5879 v005 `REVISED` (SHA-256 `E91CB0A7467C068AD81C0D2D95A2E5D92DA43439379D5DBB377B22A7AC752EE4`) all hash-match v003's table exactly. The foreign `.git/index.lock` and all foreign dirty hunks (WI-5877's in `bridge_work_intent_registry.py`, WI-5715's in `registry_control_plane.py`/its test) were left untouched throughout this review.

## Nine-Target Hash Reverification

Unchanged and reconfirmed exact match to v003's declared table for all nine `target_paths` entries, including the two foreign-modified files (`bridge_work_intent_registry.py`, `registry_control_plane.py`) — my source reading in this and the prior pass was against this exact confirmed byte state, current at both passes of this review.

## Prior Deliberations

`DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT`, `DELIB-202667517`, `DELIB-202667724`, `DELIB-202667732`, `DELIB-202667722`, `DELIB-20265660`, `DELIB-20263296` — all already cited within this thread's own v001-v003 chain; none bears directly on the F7 flakiness finding, which is new to this review.

## Non-Impairment

This append-only NO-GO grants no implementation authority. It preserves bridge history, all claims other than the exact review lease this verdict releases on publication, all protected targets and existing foreign-dirty state, source/tests/database/dispatcher/TAFE/Git state beyond this one governed publication, and the foreign `.git/index.lock`. No implementation, protected-target edit, `.git/index.lock` action, dispatcher/TAFE/config mutation, staging, or commit occurred; the only mutations in this session are the work-intent claim lifecycle (acquire → this publication's release) and the governed bridge-writer publication of this verdict itself.

## Commands And Evidence Trail

- `python scripts/bridge_claim_cli.py claim gtkb-wi5881-durable-cross-process-bridge-recovery-reservations` → rowid `36097`, `acting_role: loyal-opposition`.
- `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py::test_acquire_deadline_exhaustion_is_typed_and_leaves_no_partial_claim` (with `-p` set to `no:cacheprovider`, plus `-q --tb=short|line`) x6 → FAILED, passed, passed, FAILED, passed, passed (see table above for exact failure text).
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5881-durable-cross-process-bridge-recovery-reservations` → `preflight_passed: true`, zero missing specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5881-durable-cross-process-bridge-recovery-reservations` → 0 blocking gaps, exit 0.
- `sha256sum` against v003 and all nine target files (unchanged from prior pass; reconfirmed byte-identical).
- Direct `Read` of `scripts/bridge_work_intent_registry.py` (lines 55-169, 225-345, 975-1089) and `platform_tests/scripts/test_bridge_work_intent_registry.py` (lines 941-979) underlying F7.
- Publication via `scripts.gtkb_bridge_writer.publish_lo_verdict` (this file), which validates the active claim, verdict/status/document/version/responds-to consistency, and releases the claim on success.

## Skills Applied

- gtkb-bridge
- gtkb-proposal-review

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
