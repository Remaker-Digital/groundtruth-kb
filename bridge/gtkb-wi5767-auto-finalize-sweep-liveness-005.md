REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb353-983b-7383-b57e-3b9fc6410af5
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; manual bridge filing; dispatcher configuration and activation excluded
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5767-auto-finalize-sweep-liveness
Version: 005
Date: 2026-07-30 America/Los_Angeles
Responds to: bridge/gtkb-wi5767-auto-finalize-sweep-liveness-004.md

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5767

target_paths: ["scripts/auto_finalize_sweep.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", ".claude/skills/gtkb-bridge-propose/helpers/write_bridge.py", "platform_tests/scripts/test_doctor_auto_finalize_sweep_liveness.py", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py", "platform_tests/skills/test_bridge_propose_helper.py"]

# WI-5767 — Revised executable proposal: auto-finalize sweep liveness and bridge-writer help surface

## Revision Claim

This revision addresses LO NO-GO `-004` before any implementation: all three
behavior-calibration decisions are now durable owner decisions, the cited
program authorization is active at version 5 and covers the complete target
cohort, and shared-target ownership has been rechecked. It re-proposes the
same six-file bounded repair as `-001`; it does not implement it.

The active `PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM` is
version 5, status `active`, and permits `source`, `test`, `test_addition`,
`configuration`, `metadata`, `governance_evidence`, and `bridge` mutation
classes. It continues to forbid dispatcher mutation, external-system
mutation, credential lifecycle, push, history rewrite, deployment, release,
and destructive cleanup. This revision itself makes no dispatcher/TAFE
activation, routing, eligibility, configuration, or runtime change.

Work-intent claim: draft claim row `34994`, held by this Prime Builder session
for `gtkb-wi5767-auto-finalize-sweep-liveness` before substantive drafting.
The claim authorizes this proposal filing only. A fresh independent LO GO,
implementation claim, and implementation-start packet remain mandatory before
any protected target mutation.

## Findings Addressed

`bridge/gtkb-wi5767-auto-finalize-sweep-liveness-004.md` required a REVISED
proposal with closed owner decisions, an authorization covering the full
cohort, and an ownership re-check. This document supplies each:

1. `DELIB-202667698` closes OD-A with the owner-selected zero-drain liveness
   window of 20 recent sweep audit entries.
2. `DELIB-202667699` closes OD-B with the owner-selected interim `WARN`
   severity for an unattributed finalizing commit until WI-5763 provides
   finalizer trailers and durable audit evidence.
3. `DELIB-202667700` closes OD-C with a module-constant cutoff at this
   change's landing date, avoiding retrospective findings for pre-capability
   commits.
4. The active program PAUTH v5 now includes `configuration`, which covers the
   managed `write_bridge.py` helper as well as the existing source and test
   classes. It therefore removes the exact executable-authority denial found
   in `-003` and accepted by `-004`.
5. A scoped status and claim check immediately before this revision found one
   foreign staged change in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
   and no active claim for this thread. The staged hunk changes the separate
   skill-rename sweep's subprocess decoding behavior, not this proposal's
   intended new liveness check. It remains untouched. If it is still present
   after a future GO, implementation must re-check ownership and rebase this
   additive payload, wrapper, and registration on the then-current file; it
   must neither discard nor overwrite that staged work.

## Problem and Proposed Change

The auto-finalization sweep records a sustained zero-finalization condition
while terminal VERIFIED bridge work remains in the WI-4871 backlog, but the
doctor has no deterministic liveness assertion. The governed bridge writer
helper also has an import-only direct-invocation surface that silently exits
successfully, leaving `--help` empty. The prior chain established the defect
and its bounded remedy; this revision adopts its previously-open calibration
values as owner decisions.

1. `scripts/auto_finalize_sweep.py` adds opt-in `--probe`, which runs the
   existing dry-run classification and emits a JSON summary without committing
   or writing `finalize`/`error` audit actions. Its append-only audit rows gain
   a best-effort actor block (`source`, available session identifiers, and
   process id); missing identifiers remain fail-soft. The registered Stop-hook
   path, stdin drain, exit-zero behavior, disable environment flag, and both
   registrations remain unchanged.
2. `doctor.py` adds a self-contained payload, wrapper, and registration for
   `auto_finalize_sweep_liveness`. It reports:
   - FAIL `sweep-liveness-zero-drain` when the WI-4871 backlog is non-empty
     and the latest 20 audit rows contain zero `finalize` actions;
   - WARN `sweep-not-observing-backlog` when the backlog exists but recent
     audit evidence is insufficient or stale; and
   - WARN `unattributed-finalizing-commit` only for finalizing commits after
     this change's landing-date cutoff that have neither matching sweep audit
     evidence nor `GTKB-Finalization-*` trailers.
   The check uses the sweep probe rather than duplicate eligibility logic;
   unavailable logs or git degrade safely as described by the finding class.
3. `.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py` gains a
   `main()` / `__main__` usage guard. `--help` or `-h` exits 0 and documents
   its import-only public functions, version-1-only contract, and governed
   append/verdict filing routes. Any other direct invocation writes usage to
   stderr and exits 2. Import behavior and public function signatures stay
   unchanged.

The finalizer's write-side trailers and durable finalization audit entries are
explicitly outside this thread: WI-5763 owns `write_verdict.py` and the sweep
rule; WI-5694 owns packet-expiry-recovery actor schema. This slice only makes
the corresponding doctor detection visible at the owner-approved interim
WARN severity. It does not enable or alter dispatcher/TAFE.

## Ownership Re-check

The pre-filing ownership check found no live WI-5767 claim and no modifications
to the other five declared targets. `doctor.py` is a convergence surface with
the foreign staged hunk described above; later implementation must serialize
with its owner and rerun the scoped status/claim check immediately before
implementation start. This proposal cannot take over, reset, stage, or modify
that existing hunk.

## Cross-Harness Disposition

`scripts/auto_finalize_sweep.py` is shared by the Claude and Codex Stop-hook
registrations. Its hook behavior and registration surfaces are not targets;
the explicit probe behaves identically under either harness. The managed
bridge-writer helper is a single canonical source used across harnesses, so
its direct-help behavior is identical by construction. `doctor.py` and all
tests are harness-neutral. No parity waiver is requested.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `SPEC-1830`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-10`, `GOV-12`, `SPEC-1662` (`GOV-18`), and `GOV-15`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: every declared target is an
  in-root platform surface; no application or external placement is involved.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: the check reads append-only audit
  evidence, reports rather than fixes, and exposes stalled terminal-verdict
  lifecycle state without changing it.
- `GOV-STANDING-BACKLOG-001`: WI-5767 is the visible backlog authority for
  this bounded correction; no bulk backlog operation is in scope.

## Prior Deliberations

- `DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709`: controlling earlier
  zero-finalize diagnosis without a durable assertion.
- `DELIB-202667531`, `DELIB-202667533` (including AT-01 and AT-04), and
  `DELIB-202667534`: Advisory Corrections authorization, finalizer-lane
  boundary, and WI-5767 disposition.
- `DELIB-20266278`: owner authorization of the sweep program.
- `DELIB-202667698`, `DELIB-202667699`, and `DELIB-202667700`: closed
  owner decisions for OD-A, OD-B, and OD-C, respectively.
- Source advisory chain:
  `bridge/gtkb-lo-auto-finalize-sweep-zero-success-advisory-001.md` and
  `bridge/gtkb-lo-auto-finalize-sweep-zero-success-advisory-002.md`.

## Owner Decisions / Input

No owner decision remains open for this proposal.

- **OD-A — `DELIB-202667698`:** The zero-drain liveness window is the latest
  20 audit entries, with the existing environment override retained.
- **OD-B — `DELIB-202667699`:** The unattributed-finalizing-commit detection
  is `WARN` until WI-5763 lands attributable trailers and durable audit
  entries. This avoids falsely failing governed finalization during the
  capability gap.
- **OD-C — `DELIB-202667700`:** The requirement starts at this change's
  landing date through a module constant; historical commits are not
  retrospectively flagged.

These decisions select behavior only. They do not substitute for a fresh LO
GO, exact implementation claim, start packet, target-ownership re-check,
independent VERIFIED, or the PAUTH's forbidden-operation boundaries.

## Requirement Sufficiency

Existing requirements are sufficient. The program PAUTH v5 supplies the
previously absent execution class without changing its dispatcher prohibition.
The bridge, project-authorization, cross-harness parity, fresh-source, and
spec-derived-testing requirements determine the remaining gates. No new
requirement or owner choice is needed before review.

## Verification Plan

| Requirement group | Behavioral evidence |
| --- | --- |
| Bridge authority, project authorization, and fresh-source rules | Applicability and clause preflights against this revision; fresh GO, claim, and start packet before edits. |
| Cross-harness parity and hook fallback | Existing dual-registration test remains green; probe test confirms no registration or hook-path mutation. |
| Deterministic services, SPEC-1830, GOV-10, SPEC-1662 | New doctor fixtures assert the exact FAIL/WARN/PASS finding kinds, liveness window, payload histogram, cutoff, exit codes, and stream routing. |
| GOV-12 and spec-derived testing | New liveness test module lands with the payload, and existing sweep/helper suites gain the paired behavioral tests. |
| GOV-15 and cross-cutting mechanical enforcement | Probe makes no commit or finalizing audit write; attribution tripwire remains a detection-only WARN until the owning writer lane lands. |

Planned tests are:

1. New `platform_tests/scripts/test_doctor_auto_finalize_sweep_liveness.py`:
   zero-drain FAIL, healthy-drain PASS, empty-backlog PASS, stale-log WARN,
   and post-cutoff unattributed-commit WARN plus trailer/audit exemptions.
2. `platform_tests/hooks/test_auto_finalize_verified_verdicts.py`: probe
   emits JSON without commit or finalization audit mutation; appended rows
   contain the fail-soft actor context.
3. `platform_tests/skills/test_bridge_propose_helper.py`: help exits 0 on
   stdout with import-only routing; bare direct invocation exits 2 on stderr
   without changing import behavior.
4. Run the three suites with pytest, then `ruff check` and `ruff format
   --check` on changed Python files. Record one bounded live doctor payload
   invocation in the implementation report; it may legitimately show the
   new FAIL until the terminal backlog drains.

## Acceptance Criteria

1. Doctor distinguishes non-empty-backlog zero-drain FAIL, stale/insufficient
   observation WARN, and healthy or empty-backlog PASS using the selected
   20-entry default.
2. Probe is read-only and the normal Stop-hook path remains fail-soft,
   exit-zero, and dual-registered without configuration changes.
3. Audit actor context is additive and best-effort; post-landing-date
   unattributed finalizing commits surface as WARN until the owning finalizer
   lane supplies trailers and durable audit evidence.
4. Direct bridge-writer help has the documented exit codes and streams while
   imports and public helpers remain compatible.
5. The complete targeted test plan and lint/format checks pass, the foreign
   `doctor.py` hunk remains preserved, and no dispatcher/TAFE state or
   configuration is changed.

## Pre-Filing Preflight Subsection

Applicability and mandatory-clause preflights will be run on this exact draft
before filing. A blocking result aborts publication; this document must not be
manually copied into `bridge/`.

## Risk And Rollback

Risk is low to medium: the repair adds an opt-in probe, append-only audit
metadata, an additive doctor check, and a module-entry help guard. The doctor
will intentionally show a FAIL when the selected zero-drain condition and
backlog coexist. `doctor.py` has a foreign staged convergence hunk, mitigated
by preserving it and serializing/rebasing only after fresh GO. Rollback after
an independently verified implementation is a scoped revert of the three
source/helper changes and test deltas; no data migration, dispatcher change,
credential change, deployment, release, or destructive cleanup is involved.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
