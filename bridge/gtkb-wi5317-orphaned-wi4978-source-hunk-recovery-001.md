NEW

# WI-5317 Orphaned WI-4978 Source-Hunk Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5317-orphaned-wi4978-source-hunk-recovery
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-15 UTC

author_identity: Codex A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5.5
author_model_version: 5.5
author_model_configuration: Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5317

target_paths: ["scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Recover the exact source and test hunks that implement the already-reviewed
WI-4978 bridge-compliance-audit chokepoint but were never included in its
terminal commit. WI-4978 was marked resolved after a bridge-only finalization;
the implementation remains dirty and now prevents exact finalization of the
independently reviewed WI-5113 no-window changes in a shared test file.

This is a provenance and finalization repair, not a redesign. Independent
review will evaluate the current two-file implementation, and finalization will
include only the enumerated WI-4978 hunks. Foreign WI-5113 no-window hunks and
all managed helper projections are explicitly excluded.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires independent GO before protected
  source/test finalization and independent VERIFIED after implementation review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this
  implementation proposal to cite its governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the PAUTH,
  project, and work-item linkage above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the final review
  to map each applicable requirement to executed evidence.
- `GOV-WORK-TREE-HYGIENE-001` — requires dirty implementation to have explicit
  ownership and exact-scope disposition rather than broad absorption.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — requires the
  mandatory proposal requirements to be enforced at helper-managed write time.

## Prior Deliberations

- `DELIB-WI4589-SPLIT-COMMIT-RECOVERY-WAIVER-20260623` — Owner Decision: Approve split-commit recovery waiver for WI-4589
  establishes precedent for preserving foreign hunks while finalizing an exact
  owned subset; this proposal does not reuse that incident-specific waiver.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — established the proposal
  structure whose helper-path enforcement WI-4978 implements.

## Owner Decisions / Input

The owner authorized the full modernization project and directed Prime Builder
to inventory every dirty hunk, fix blockers, finalize independently verified
scopes with exact mechanical authority, and continue until the worktree is
clean. The active Tree Stabilization project PAUTH covers proposal filing,
source/test repair, evidence, and local exact-scope finalization while retaining
its listed mechanical exceptions. No additional owner decision is required to
request independent review of this bounded recovery.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-WORK-TREE-HYGIENE-001` supplies the
ownership/finalization rule, and
`GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` supplies the
behavioral requirement. No new requirement is introduced.

## Spec-Derived Verification Plan

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`:
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short`
  must pass, including fail-before-write behavior for malformed proposals and
  proposal-only-section exemptions for valid GO, NO-GO, and VERIFIED verdicts.
- `GOV-WORK-TREE-HYGIENE-001`:
  `git diff --check -- scripts/gtkb_bridge_writer.py platform_tests/scripts/test_gtkb_bridge_writer.py`
  must pass, and an independently inspected hunk manifest must classify every
  selected line as WI-4978 while excluding WI-5113 Git no-window changes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` and project-linkage DCLs:
  `python .claude/hooks/bridge-compliance-gate.py --audit-only` through the
  governed helper filing path must pass for this proposal, followed by valid
  independent GO/start and post-implementation VERIFIED evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:
  the implementation report and verdict must include the commands above and
  their observed results rather than relying on the old bridge-only verdict.

Exact WI-4978 hunk contract:

- `scripts/gtkb_bridge_writer.py`: add `BridgeComplianceError`, locate the
  canonical bridge-compliance gate, audit fully composed in-memory content via
  audit-only mode, fail closed on execution/output/decision errors, and run the
  audit before directory creation or exclusive file creation.
- `platform_tests/scripts/test_gtkb_bridge_writer.py`: add only the compliance
  error import, valid proposal/verdict fixture builders and reviewed-file
  fixture, gate-compatible updates to write tests, the malformed-proposal
  fail-before-write test, and valid-verdict exemption coverage.
- Exclude the `no_window_subprocess_kwargs` import, `_git` no-window forwarding,
  raw-Git-to-`_git` test rewrites, and every other staged or unstaged hunk.

## Risk / Rollback

The main risk is accidental absorption of WI-5113 lines from the commingled test
file or unrelated managed-helper drift. Finalization must therefore use an
independently verified hunk patch, not whole-file staging. A behavioral failure
could block all helper-managed bridge writes; the focused tests exercise both
deny and allow paths. Rollback is the single exact-scope recovery commit after
the shared worktree has a committed baseline; no foreign hunk may be reverted.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5317-orphaned-wi4978-source-hunk-recovery`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` because the recovered implementation closes a bypass in mandatory bridge
proposal validation and repairs its missing source finalization.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
