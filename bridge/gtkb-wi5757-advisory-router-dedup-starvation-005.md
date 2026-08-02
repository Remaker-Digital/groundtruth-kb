REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher/TAFE deliberately disabled

# WI-5757 Corrected Recovery Proposal — Readable Proposal/GO Ancestry

bridge_kind: prime_proposal
Document: gtkb-wi5757-advisory-router-dedup-starvation
Version: 005
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5757-advisory-router-dedup-starvation-004.md
Supersedes proposal premise: bridge/gtkb-wi5757-advisory-router-dedup-starvation-001.md
Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5757
target_paths: ["scripts/advisory_backlog_router.py", "platform_tests/scripts/test_advisory_backlog_router.py"]
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## First-Line Role Eligibility Check

PASS. Harness A is active as Prime Builder in the canonical harness projection,
the transcript-resolved session role is Prime Builder, and `REVISED` is a Prime
Builder status. This document requests an independent GO; it does not reuse or
author a Loyal Opposition verdict.

## Revision Claim

V004 correctly found that v001 was not mechanically readable as a proposal-kind
artifact because it omitted `bridge_kind`. This v005 is the replacement
proposal-kind carrier. It preserves the already-implemented exact two-file
behavior, records current byte-for-byte re-observation under the owner's exact-
reobservation decision, and establishes a new prospective proposal → GO →
report → VERIFIED cycle.

No source, test, candidate-store, MemBase, bridge history, dispatcher, or TAFE
mutation is proposed before a new independent GO. The prior v002 GO and expired
implementation packet are historical and must not be reused as current
authority.

## Findings Addressed

### F1 — Report lacks a GO-linked proposal-kind ancestor

RESOLVED FOR THE PROSPECTIVE CYCLE. This document declares
`bridge_kind: prime_proposal`. A future independent v006 GO must respond to
this exact v005. Only after that GO may Prime Builder acquire a new exact claim,
mint a fresh schema-v3 packet, and file a source-free v007 implementation report
responding to v006. Independent v008 review then verifies the exact committed
state. V001/v002 and the expired v003 packet are not used for that cycle.

## Exact Re-observed Implementation State

The approved implementation remains present by reference in custodial commit
`02e12e7b0e1a1172ea8acf1b9a99e2ee9b8e54af`. Current repository HEAD is
`75decbfa704fe50288aecbc5669def329a0825df`. Both targets are tracked, clean,
and exactly match the postimages described by v003.

| Target | Current SHA-256 | Current evidence |
| --- | --- | --- |
| `scripts/advisory_backlog_router.py` | `A67B74257C33C651A394A851D7CC3EE1BA367762C1D7FEC5BEF7FD3529868201` | clean; committed; versioned source key, legacy-compatible dedup, starvation signal |
| `platform_tests/scripts/test_advisory_backlog_router.py` | `C54B9D45EA1FE5E85813343CF4C2B906550C9B838DBD0ED0F95B5C586F6031FA` | clean; committed; 22 focused behavioral tests |

The custodial sweep is preserved as history and is not misrepresented as an
exact WI-5757 finalizer receipt. No history rewrite or recommit of already-
clean implementation bytes is requested.

## Proposed Recovery Scope

1. Reconfirm the exact existing behavior only: versioned advisory identity,
   bounded legacy compatibility, deterministic `starvation_signal`, and the
   fixture-rooted behavioral coverage already described in v003.
2. Preserve the completed historical single-writer backfill as evidence; do
   not rerun it as an implementation side effect during this recovery.
3. After independent GO, create fresh claim/start evidence for exactly the two
   target paths and file a source-free implementation report with current
   hashes, tests, and committed-state provenance.
4. Keep the two separately tracked concurrency defects outside this recovery:
   implementation-start orchestration is carried by WI-5790, and candidate-
   store writer atomicity remains its existing carrier.

## Scope Changes

No implementation behavior or target changes. The only change is the governed
artifact shape needed to make proposal-kind → matching GO ancestry readable
and to reconcile the already-committed exact postimages truthfully.

## Specification Links

- `GOV-STANDING-BACKLOG-001`
- `DCL-STANDING-BACKLOG-SCHEMA-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `SPEC-1830`
- `SPEC-1662`
- `GOV-10`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260801-EXACT-REOBSERVATION-RECOVERY-APPROVAL` — owner approval for
  byte-exact committed-state recovery without new implementation or history
  rewrite; linked to WI-5757.
- `DELIB-202667531` — owner-approved fix-class advisory corrections.
- `DELIB-202667534` — advisory corpus disposition table.
- `DELIB-202667532` — program sequencing and north-star scoring.
- `DELIB-202667523` — integrated parallel-operation program mandate and manual
  dispatcher operating model.
- `DELIB-20264768` and `DELIB-20265695` — prior review history for the router
  and skipped-existing behavior.

## Owner Decisions / Input

No new owner decision is required. The work item is an active member of the
owner-authorized Advisory Corrections project, and exact committed-state
re-observation is expressly approved by
`DELIB-20260801-EXACT-REOBSERVATION-RECOVERY-APPROVAL`. All ordinary independent
GO, claim, start, verification, and finalization gates remain mandatory.

## Requirement Sufficiency

Existing requirements are sufficient. This revision changes only ancestry and
current evidence, not router behavior. `GOV-STANDING-BACKLOG-001`,
`GOV-FILE-BRIDGE-AUTHORITY-001`, and the exact test mapping from v001/v003 fully
determine the expected implementation state.

## Verification Plan

| Governing requirement | Prospective evidence after v006 GO |
| --- | --- |
| Versioned advisory identity and legacy-compatible dedup | Re-run `platform_tests/scripts/test_advisory_backlog_router.py`; verify newer heads stage and identical legacy files do not duplicate. |
| Deterministic starvation visibility | Re-run result/JSON/last-scan/warning tests for the exact all-existing predicate. |
| Stage-only, bridge-read-only behavior | Re-run fixture bridge-byte preservation and no-MemBase-write tests; do not perform a new live backfill. |
| Code quality and target isolation | Ruff check/format, scoped status, SHA-256, blob, and diff observations on the exact pair. |
| Current authority | Fresh independent GO responding to v005, exact claim, schema-v3 packet, operation-time PAUTH, and two target validations. |

Current read-only baseline: 22/22 focused tests pass; Ruff check passes; Ruff
format check reports both files formatted; both target paths are clean.

## Acceptance Criteria

1. Independent LO GO responds to this exact proposal-kind v005.
2. A later PB report responds to that GO and carries a fresh live claim/start
   packet for exactly the two target paths.
3. Both committed target hashes remain exact and all 22 focused tests plus
   Ruff gates pass.
4. The recovery performs no new router/backfill/MemBase/dispatcher/TAFE side
   effect and makes no false exact-finalizer claim about the custodial sweep.
5. Only independent Loyal Opposition may issue the terminal verdict.

## Pre-Filing Preflight Subsection

The governed revision helper must run applicability and mandatory ADR/DCL
clause preflights against the final v005 candidate. Filing is prohibited on
any missing required/advisory specification, blocking error, evidence gap, or
blocking gap.

## Risk And Rollback

The main risk is accidentally treating the old v002 GO or expired packet as
authority. The explicit new-cycle sequence prevents that. If current target
bytes, project authority, or proposal/GO ancestry drift, the operation fails
closed and is corrected append-only. No source rollback is needed. Reset,
history rewrite, broad staging, candidate deletion, dispatcher/TAFE action,
push, deployment, credential action, and destructive cleanup remain out of
scope.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
