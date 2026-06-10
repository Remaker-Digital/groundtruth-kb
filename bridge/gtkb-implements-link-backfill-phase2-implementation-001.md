NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-29-implements-link-backfill-phase2-implementation
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

Project Authorization: PAUTH-WI-3462-PHASE2-IMPLEMENTS-BACKFILL-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3462
Implements: WI-3462

# Implementation Proposal - Phase-2 implements-link backfill tool + data mutation (WI-3462)

bridge_kind: prime_proposal
Document: gtkb-implements-link-backfill-phase2-implementation
Version: 001 (NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-29 UTC
Session: S372
Responds to GO: bridge/gtkb-implements-link-backfill-phase2-scoping-002.md
Recommended commit type: feat:

target_paths: ["scripts/backfill_implements_links.py", "platform_tests/scripts/test_backfill_implements_links.py", "groundtruth.db"]

## Summary

Implements the Phase-2 implements-link backfill design GO'd at
`bridge/gtkb-implements-link-backfill-phase2-scoping-002.md`. Adds a
deterministic, read-then-write tool that discovers each active-authorization
project's gating WIs, classifies projects (CLEAN / AMBIGUOUS / UNADDRESSED),
auto-links CLEAN projects' addressing threads via
`project_artifact_links` (`relationship='implements'`), resolves AMBIGUOUS
projects with the GO'd D3 rule (prefer non-scoping, non-superseded; AUQ fallback
for residual), and leaves UNADDRESSED projects untouched. This arms v4 project
auto-completion (`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4), which is
fail-safe-paused platform-wide until implements-links exist.

Authorized by the dedicated `PAUTH-WI-3462-PHASE2-IMPLEMENTS-BACKFILL-001`
(owner decision `DELIB-2510`), whose `allowed_mutation_classes` include
`project-artifact-link-insert` - the class the standing reliability PAUTH lacks.

## Owner Decisions / Input

- **S372 AUQ** = "Authorize dedicated PAUTH + proceed" - owner authorized a
  WI-3462-specific PAUTH permitting the `project_artifact_links` data mutation.
  Captured as `DELIB-2510` (owner_conversation, owner_decision) and realized as
  `PAUTH-WI-3462-PHASE2-IMPLEMENTS-BACKFILL-001` (active).
- **S372 AUQ (prior)** = "Phase-2 backfill" then "File scoping proposal now" -
  established the work and produced the scoping GO `-002`.
- Per the D3 rule, the implementation surfaces an owner AUQ ONLY if the
  refreshed discovery leaves a project genuinely ambiguous after the
  deterministic rule (none in the current discovery).

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (v4) - the implements-link completion semantics this backfill populates; must not change v4, only insert links.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + Work Item header present.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH-WI-3462-PHASE2-IMPLEMENTS-BACKFILL-001 supplies the project-artifact-link-insert mutation class; this proposal still goes through GO + impl-start packet + VERIFIED.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root; no `applications/**` mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the backfill produces durable bridge-thread->project implements traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - populating implements-links advances the project-completion lifecycle trigger.
- `GOV-STANDING-BACKLOG-001` - WI-3462 active under PROJECT-GTKB-RELIABILITY-FIXES.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic service, no hand-written data edits.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner AUQ is the fallback for residual ambiguity only.

## Requirement Sufficiency

Existing requirements sufficient. The implements-link completion semantics are defined by `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4 (VERIFIED this session) and unchanged here; this implementation only populates links to those semantics under the GO'd Phase-2 design. No new GOV/SPEC/ADR/DCL is required.

## KB Mutation Scope

YES - `project_artifact_links` inserts only. For each CLEAN project (and each D3-resolved AMBIGUOUS project), insert one `project_artifact_links` row per addressing thread (`artifact_type='bridge_thread'`, `relationship='implements'`, `status='active'`) via `db.add_project_artifact_link()`. Idempotent: re-runs skip threads already implements-linked to the project (no duplicate rows). No spec/work-item/deliberation mutation. `groundtruth.db` is in `target_paths`; the mutation class `project-artifact-link-insert` is authorized by PAUTH-WI-3462-PHASE2-IMPLEMENTS-BACKFILL-001.

## WI Citation Disclosure

Declares work for **WI-3462** only. WI-3365, WI-3248, WI-3247, WI-3443 may appear as discovery DATA (ambiguous-project gating WIs and the v4 lineage PAUTH id); none are implementation declarations.

## Prior Deliberations

- `DELIB-2510` - owner authorization for the dedicated PAUTH (this thread's authorizing decision).
- `DELIB-2503` - S373 scanner-fix vehicle + PAUTH owner-decision chain (v4 lineage).
- `bridge/gtkb-implements-link-backfill-phase2-scoping-002.md` (Codex GO) - the scoping GO this implementation realizes; its Follow-On Implementation Constraints are addressed below.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-017.md` (Codex VERIFIED) - the v4 thread whose fail-safe this arms.
- `bridge/gtkb-orphan-wi-membership-backfill-slice-2-scoping-002.md` (Codex GO) - the deterministic-backfill precedent pattern.

## Proposed Implementation

### IP-1: `scripts/backfill_implements_links.py` (deterministic tool)

A read-then-write service with three modes:

- `--report` (read-only): refreshes discovery live and prints the CLEAN /
  AMBIGUOUS / UNADDRESSED classification (the WI-3462 discovery, recomputed).
- `--apply` (mutating): refreshes discovery immediately before mutation, then
  inserts implements-links for CLEAN projects + D3-resolved AMBIGUOUS projects.
- default (no flag): equivalent to `--report` (safe default).

Internals reuse the v4 primitives to guarantee scanner/lifecycle parity:
`_implements_links_by_project()` (existing links, to skip), the all-status
thread->WI map (addressing-thread candidates), and
`_project_membership_work_item_ids()` (gating set). Classification logic is
byte-identical to the discovery captured in WI-3462.

D3 ambiguity resolution: for a gating WI mapping to >1 candidate thread, drop
threads whose slug ends in `-scoping` when a non-scoping sibling cites the WI,
and drop superseded threads (a thread whose later superseder cites the same WI)
when the superseder cites the WI. If exactly one candidate survives -> link it.
If >1 survive -> record the project in a `needs_owner_auq` list and DO NOT link
(fail-closed).

`--apply` is idempotent: a thread already implements-linked to a project (via
`current_project_artifact_links`) is skipped. Every insert uses
`db.add_project_artifact_link(project_id, 'bridge_thread', slug, changed_by,
change_reason, relationship='implements')`.

### IP-2: `platform_tests/scripts/test_backfill_implements_links.py`

Spec-derived tests over synthetic fixtures (isolated tmp_path DBs):
discovery classification, CLEAN auto-link, D3 resolution (scoping-vs-impl +
superseded-vs-superseder), residual-ambiguity fail-closed + surfaced,
UNADDRESSED untouched, idempotent rerun, and a no-cross-project-leak assertion
(reuse the thread #3 shape). Plus a v4-invariant test: a backfilled CLEAN
project does NOT auto-complete unless all its gating WIs are VERIFIED.

### IP-3: Apply pass + evidence

Run `--report` first (capture), then `--apply` (capture the inserted links),
then `--report` again (idempotency: second apply is a no-op). Capture the live
post-apply `current_project_artifact_links` count for the CLEAN projects. The
post-impl report records all three captures + the test/ruff results.

## Spec-to-Test Mapping

| Specification / Behavior | Test | Expected |
|---|---|---|
| Discovery classify CLEAN/AMBIGUOUS/UNADDRESSED | `test_classify_*` | PASS |
| CLEAN auto-link inserts correct implements rows | `test_clean_auto_link` | PASS |
| D3 resolves scoping-vs-impl + superseded-vs-superseder | `test_d3_resolution` | PASS |
| Residual ambiguity fails closed + surfaced (no link) | `test_residual_ambiguity_no_link` | PASS |
| UNADDRESSED untouched | `test_unaddressed_untouched` | PASS |
| Idempotent rerun (no duplicate links) | `test_idempotent_rerun` | PASS |
| No cross-project leak | `test_no_cross_project_leak` | PASS |
| v4 invariant: links alone do not complete an unfinished project | `test_links_do_not_complete_unfinished` | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` - filed; INDEX updated | this filing | PASS |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic (SQLite, no LLM) | inspection | PASS |

Verification commands:
- `python -m pytest platform_tests/scripts/test_backfill_implements_links.py -q --tb=short`
- `python -m ruff check scripts/backfill_implements_links.py platform_tests/scripts/test_backfill_implements_links.py`
- `python scripts/backfill_implements_links.py --report` (captured pre + post apply)

## Bridge Protocol Handling

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of its document block in `bridge/INDEX.md` (correct status for a fresh implementation proposal awaiting review). No prior version is deleted or rewritten; the version chain is append-only and `bridge/INDEX.md` remains the canonical workflow state (`GOV-FILE-BRIDGE-AUTHORITY-001` / CLAUSE-INDEX-IS-CANONICAL).

## Acceptance Criteria

- [ ] Codex GO on this implementation proposal.
- [ ] Implementation-start packet activated from the GO.
- [ ] IP-1 tool + IP-2 tests landed; all tests + ruff clean.
- [ ] `--apply` inserts implements-links for the CLEAN projects; idempotent on rerun.
- [ ] No project auto-completes whose gating WIs are not all VERIFIED (v4 invariant holds).
- [ ] Post-impl report with report/apply/report captures + test evidence.
- [ ] Codex VERIFIED.

## Risk and Rollback

Risk: moderate - first data mutation to `project_artifact_links` via the backfill. Mitigations: v4 still requires all gating WIs VERIFIED (links alone never complete an unfinished project); discovery refreshes live before mutation; D3 fails closed to AUQ; idempotent. Rollback: `project_artifact_links` is append-only/versioned - a wrong link is superseded with a `status` change (no destructive delete); the tool can emit the inserted link ids for targeted supersession.

## Loyal Opposition Asks

1. Confirm the `project-artifact-link-insert` mutation class + PAUTH-WI-3462-PHASE2-IMPLEMENTS-BACKFILL-001 (owner DELIB-2510) correctly authorize the data mutation.
2. Confirm the tool design (report/apply, refresh-before-mutation, idempotent, D3 fail-closed) satisfies the scoping GO's Follow-On Implementation Constraints.
3. Confirm target_paths (tool + test + groundtruth.db) are complete for the mutation surface.
4. Note any spec to add to Specification Links.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
