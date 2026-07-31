REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; approval_policy=never; sandbox=danger-full-access

bridge_kind: prime_proposal
Document: gtkb-wi5764-wi5370-fabricated-closure-correction
Version: 005
Date: 2026-07-30 UTC
Responds to: bridge/gtkb-wi5764-wi5370-fabricated-closure-correction-004.md

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5764
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

target_paths: ["groundtruth.db", "scripts/claimed_file_operation_preflight.py", ".claude/skills/gtkb-verify/helpers/write_verdict.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "groundtruth-kb/src/groundtruth_kb/bridge/verdict_filing.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", ".claude/rules/file-bridge-protocol.md", ".groundtruth/formal-artifact-approvals/**", "platform_tests/skills/test_claimed_file_operation_verification.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py", "platform_tests/groundtruth_kb/test_doctor_claimed_file_operations.py"]

# WI-5764 — Fresh Recovery Proposal for Fabricated-Closure Correction and Claimed-File-Operation Verification

Scope confirmation: this filing performs no MemBase mutation and no
`groundtruth.db` write. The thread's implementation work does include one
append-only MemBase work-item amendment, so `kb_mutation_in_scope` is true and
`groundtruth.db` is declared as a target. This filing performs no
approval-evidence work. The later implementation may touch only the exact target cohort above, after a fresh
independent GO, an exact work-intent claim, a passing implementation-start
packet, resolution of every declared path collision, and the required
per-artifact approval packet for the protected rule-file postimage.

The parent project is active and WI-5764 is an active project member. The
controlling PROGRAM authorization is the active, list-free whole-project PAUTH
v5. It supplies `source`, `test`, `test_addition`, `configuration`, `metadata`,
`governance_evidence`, and `bridge` classes for project members, including
WI-5764, without using per-work-item approval as authority. The older
WI-5764-specific recovery PAUTH remains append-only historical evidence of the
owner's recovery intent, but is non-controlling under the owner's project-only
approval model.

## Revision Claim

This revision replaces the non-executable authority reviewed at v001/v002.
It addresses v004 with fresh authority and durable owner decisions rather than
retroactively splicing authority into the old GO:

1. PROGRAM PAUTH v5, issued under `DELIB-202667533` plus the owner-approved
   2026-07-30 class-scope correction, is the fresh whole-project authority
   required by v004. It permits `source`, `test`, `test_addition`,
   `configuration`, `metadata`, `governance_evidence`, and `bridge`, while
   forbidding dispatcher mutation, external-system mutation, credential
   lifecycle, push, history rewrite, deployment, release, and destructive
   cleanup. `DELIB-202667696` remains supporting recovery-intent evidence, not
   a standalone implementation approval.
2. OD-A through OD-D are no longer open. `DELIB-202667688` through
   `DELIB-202667693` durably select every implementation fork.
3. The exact target cohort remains declared, but implementation is serialized
   behind current shared-worktree ownership. In particular,
   `groundtruth-kb/src/groundtruth_kb/project/doctor.py` and
   `platform_tests/skills/test_verified_finalization_validation_hardening.py`
   are already staged by another lane and must not be modified until that
   ownership clears. The finalizer and rule targets also overlap WI-5763 and
   must serialize behind its disposition. WI-5765 has since advanced through
   REVISED v005 and GO v006 to Prime NO-ACTION v007; it no longer holds a live
   implementation claim, but its current bridge disposition must still be
   respected. These lanes must land, release, or be explicitly dispositioned
   before WI-5764 claims implementation.
4. No partial implementation is authorized from this filing. If the collision
   set does not clear, Prime Builder files a role-correct operational
   correction rather than taking over staged paths.

## Problem and Fresh Evidence

The controlling v001 problem statement remains accurate and is incorporated
by reference without rewriting history. The WI-5370 implementation report
claimed that a 2,146-byte bridge carrier was copied to an archive, verified by
SHA-256/Git blob, and then deleted. Fresh review found the archive absent and
the allegedly deleted live bridge carrier still present at 1,293 bytes. The
certifying VERIFIED did not test that physical claim, and the false closure
was later re-affirmed in MemBase. Existing finalizer, compliance-gate, and
doctor checks do not mechanically verify file operations claimed in an
implementation report.

The correction preserves all historical bridge versions. It never creates a
retroactive lookalike archive and never rewrites the fabricated report.

## Executable Design

### Slice 1 — Append-only WI-5370 forensic annotation

Apply the owner-selected annotate-and-supersede form through the governed
backlog amend surface:

- retain WI-5370's terminal state;
- append a new version whose forensic annotation states that the claimed
  archive-then-delete operation did not execute;
- cite the live physical evidence, the original report/verdict chain, and
  WI-5764 as the corrective carrier;
- record the owner-selected formal waiver of late archive creation; and
- preserve every earlier work-item and bridge version.

This is an append-only MemBase mutation during implementation, not during this
filing. The implementation report must record the exact governed command and
postimage evidence. No bridge file is edited, moved, or deleted.

### Slice 2 — Deterministic claimed-file-operation guard

Create `scripts/claimed_file_operation_preflight.py` exposing
`validate_claimed_file_operations(report_body, project_root)`.

The owner-selected extraction contract is:

- a structured `## File Operations` implementation-report section with one
  row per create, move, archive, or delete claim, including path and optional
  size/SHA-256; and
- a narrow compatibility heuristic for the incident's archive-then-delete,
  byte-count, and SHA-256 prose pattern.

Verification is fail closed at both approved layers:

- created/archived paths must exist;
- deleted/removed paths must be absent;
- stated byte sizes and SHA-256 values must match current tree bytes; and
- mismatches deny VERIFIED with a path-specific reason.

Wire the same validator into the governed VERIFIED finalization path and the
direct-verdict compliance gate. Mirror the active hook byte-for-byte to
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`.

WI-5763 owns finalizer relocation. If WI-5763 lands first, wire the acceptance
check into `groundtruth_kb.bridge.verdict_filing` and keep
`write_verdict.py` as the governed delegating alias. If it has not landed,
this implementation must wait; it must not create a second finalization
engine or silently select a temporary call site.

### Slice 3 — Read-only historical audit and regression coverage

Add a doctor payload/wrapper that enumerates claimed-file-operation mismatches
across historical terminal VERIFIED threads. The audit is read-only: it emits
findings for later owner triage and mutates neither bridge history nor MemBase.

Add/extend the declared fixture-based tests. No test may read from or mutate
the live MemBase or live bridge.

## Cross-Harness Disposition

The active compliance hook and packaged template must remain byte-identical.
The checker and doctor are harness-neutral in-root platform services.

`.claude/rules/file-bridge-protocol.md` is a protected narrative artifact. Its
normative `## File Operations` / claimed-operation-verification subsection may
be written only after a full-content formal-artifact approval packet is
generated, validated, presented to the owner, and approved through the
governed packet path. Target declaration and project authorization do not
substitute for that packet. The rule-file edit is also sequenced after the
WI-5763 edit to the same artifact.

No dispatcher/TAFE configuration or runtime is touched or activated.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge audit-trail and VERIFIED finalization authority.
- GOV-DOCUMENT-AUTHOR-PROVENANCE-001 — physical evidence and provenance must be truthful.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — terminal verification must derive from executable evidence.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — finalizer and write-time defense in depth.
- DCL-CROSS-HARNESS-ENFORCEMENT-001 and ADR-CODEX-HOOK-PARITY-FALLBACK-001 — active-hook/template parity.
- GOV-08 and GOV-STANDING-BACKLOG-001 — append-only MemBase correction through the governed backlog authority.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, and DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — preserve history and explicit lifecycle transitions.
- GOV-ARTIFACT-APPROVAL-001 and DCL-ARTIFACT-APPROVAL-HOOK-001 — per-artifact approval for the protected rule postimage.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001, and DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 — project-bound implementation authority and operation-time class enforcement.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 — implementation and verification re-read the current tree and MemBase state.
- GOV-10, GOV-12, SPEC-1662, GOV-15, and GOV-17 — behavioral tests, work-item-driven coverage, no autonomous test fixes, and reviewed automation changes.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — all targets are in-root platform artifacts.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 and DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 — proposal linkage.

## Prior Deliberations

- `DELIB-202667531` and `DELIB-202667534` — corrections-project authority and advisory disposition to WI-5764.
- `DELIB-202667533` — AT-01 finalizer ordering and AT-04 program context.
- `DELIB-202667687` — owner approval to process WI-5764 through the governed implementation flow.
- `DELIB-202667688` — OD-A: annotate-and-supersede.
- `DELIB-202667689` — OD-B: formally waive late phantom-archive creation.
- `DELIB-202667690` — OD-C1: fail closed at finalizer and compliance-gate layers.
- `DELIB-202667691` — OD-C2: structured `## File Operations` plus narrow incident-pattern heuristic.
- `DELIB-202667692` — OD-C3: platform-side enforcement only; Cursor behavior follow-up is separate work.
- `DELIB-202667693` — OD-D: read-only historical doctor audit.
- `DELIB-202667696` — owner-approved comprehensive recovery scope and fresh-review path; retained as decision evidence rather than per-WI implementation approval.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — current project-only authority interpretation: project members inherit the active list-free PAUTH; WI-specific approval is non-controlling.
- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE` — atomic truthful finalization requirement.
- WI-5729 v2 — append-only forensic-correction precedent.
- Source advisory: `bridge/gtkb-wi5370-fabricated-archive-closure-advisory-001.md`.

## Owner Decisions / Input

All implementation-shaping decisions are durable and closed:

- OD-A: annotate-and-supersede; retain terminal WI-5370 state.
- OD-B: formally waive retrospective archive creation.
- OD-C1: blocking/fail-closed enforcement at both layers.
- OD-C2: structured declarations plus the narrow incident heuristic.
- OD-C3: platform acceptance enforcement only; no Cursor behavior work here.
- OD-D: read-only historical doctor audit.
- Recovery authority: use active list-free PROGRAM PAUTH v5 and obtain a fresh
  independent review; do not treat the historical singleton PAUTH as
  implementation approval.
- Project-authority interpretation:
  `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD`.

No new owner decision is required for review. The protected rule postimage
still requires its separate full-content packet approval at implementation
time, and path ownership must be clear before implementation starts.

## Requirement Sufficiency

Existing requirements and the durable owner decisions above are sufficient.
No requirement fork remains. The later protected rule subsection documents
the new mechanical contract and is itself governed by the formal-artifact
packet; it is not a precondition for reviewing this proposal.

## Spec-Derived Test Plan

1. `test_guard_rejects_nonexistent_claimed_operation`: declared and prose
   incident variants with absent archive / still-present delete target are
   denied by the checker, finalizer, and compliance gate.
2. `test_guard_accepts_verified_operations`: truthful existence, absence,
   size, and SHA-256 claims pass all layers.
3. `test_record_correction_roundtrip_annotate`: a WI-5370-shaped fixture is
   amended append-only; earlier versions remain readable; terminal state is
   retained; forensic reason and archive waiver are present.
4. `test_doctor_claimed_file_operation_sweep`: one fabricated and one
   truthful terminal fixture yield exactly one finding; tree and fixture DB
   bytes are unchanged.
5. `test_compliance_gate_template_parity`: active hook and template remain
   byte-identical.
6. Run the complete existing validation-hardening suite to prove no regression
   in ordinary VERIFIED acceptance/finalization.

Commands:

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_claimed_file_operation_verification.py platform_tests/groundtruth_kb/test_doctor_claimed_file_operations.py platform_tests/skills/test_verified_finalization_validation_hardening.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check <all changed Python files>`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <all changed Python files>`
- hook/template byte comparison and `git diff --check`.

## Acceptance Criteria

1. A contradictory claimed file operation blocks direct and finalizer-driven
   VERIFIED acceptance with a path-specific diagnostic; truthful reports pass.
2. WI-5370 receives one append-only forensic annotation retaining terminal
   state and recording the archive waiver; no bridge history is changed.
3. The doctor reports historical mismatches read-only and creates no automatic
   remediation or work items.
4. Hook/template parity and all declared behavioral tests pass.
5. The protected rule edit has a validated, owner-approved full-content packet
   before mutation.
6. WI-5763/WI-5765 and the two staged target overlaps are resolved before the
   implementation claim and start packet; no foreign staged hunk is overwritten.
7. No dispatcher/TAFE, external system, credential, push, history rewrite,
   deployment, release, or destructive-cleanup operation occurs.

## Findings Addressed

### F1 — Earlier authority omitted required classes

Response: fresh proposal cites the owner-approved, list-free PROGRAM PAUTH v5,
which now includes configuration and metadata. It does not alter or
retroactively repair v001/v002, and it does not rely on the historical
WI-specific PAUTH as controlling approval.

### F2 — OD-A through OD-D were open

Response: exact owner-decision records are cited and their selected outcomes
are incorporated into one design.

### F3 — Shared staged targets and adjacent-lane overlap

Response: exact serialization preconditions are acceptance criteria. Current
foreign changes are preserved and implementation fails closed until ownership
is isolated.

### F4 — Protected artifact approval

Response: full-content packet generation/validation/owner approval remains a
hard per-artifact precondition.

## Risk and Rollback

Risk is MEDIUM-LOW. The guard is additive but intentionally fail closed, so a
parser false positive can block VERIFIED. Fixture coverage pins both incident
and truthful cases. The doctor is read-only. The MemBase correction is
append-only. Concurrency risk is contained by refusing to start while target
paths are staged or claimed elsewhere.

Rollback is slice-local: revert checker/wire-in/test/doctor changes; use a
later append-only MemBase amendment if the forensic annotation itself needs
correction; never rewrite bridge or MemBase history. No schema migration,
dispatcher change, or external rollback is involved.

Recommended commit type: fix

## Pre-Filing Preflight Subsection

Before filing, run the applicability packet, mandatory-clause preflight,
candidate compliance audit, credential scan, and exact work-intent claim.
Filing stops on any blocking gap. Implementation remains prohibited until the
fresh independent GO and implementation-start packet exist.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
