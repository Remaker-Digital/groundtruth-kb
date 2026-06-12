NEW

bridge_kind: prime_proposal
Document: gtkb-fab-10-codex-index-adapter-addendum-sufficiency
Version: 001
Author: prime-builder (Codex, harness A) - interactive owner session
Date: 2026-06-12
Related-Bridge: bridge/gtkb-fab-10-codex-index-adapter-addendum-001.md
Related-Bridge: bridge/gtkb-fab-10-codex-index-adapter-addendum-002.md
Related-Bridge: bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-001.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4422
Project Authorization: PAUTH-FAB10-20260610

author_identity: prime-builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop, Prime Builder bridge queue processing

target_paths: [".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py", "platform_tests/scripts/**"]

No KB mutation: this corrective addendum changes one Codex hook adapter and focused tests only; it does not write groundtruth.db.

---

# FAB-10 Codex INDEX Adapter Addendum - Requirement Sufficiency Correction

## Summary

The FAB-10 Codex INDEX adapter addendum was reviewed and returned GO at `bridge/gtkb-fab-10-codex-index-adapter-addendum-002.md`, but the implementation-start gate refuses to mint the local authorization packet because the approved proposal omitted the mandatory `## Requirement Sufficiency` section.

This proposal is a narrow superseding authorization packet for the same already-reviewed implementation scope:

- update `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py` so Codex `apply_patch` edits to `bridge/INDEX.md` are forwarded to `.claude/hooks/bridge-compliance-gate.py`;
- add focused tests under `platform_tests/scripts/**`;
- preserve all original FAB-10 constraints: no helper-only CAS write migration, no retired poller restoration, no MemBase mutation, and no weakening of `bridge/INDEX.md` as canonical workflow state.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` is canonical bridge workflow state and must be protected from malformed writes.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook parity requires the apply-patch adapter to enforce the same bridge-compliance gate as Claude Write/Edit.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation-targeting bridge proposals require project authorization, project, and work item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal cites concrete governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification remains spec-derived.
- `GOV-STANDING-BACKLOG-001` - WI-4422 remains the governed backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all paths are in-root under `E:\GT-KB`.

## Prior Deliberations

- `DELIB-FAB10-REMEDIATION-20260610` - owner selected INDEX well-formedness lint now and helper-only INDEX writes later.
- `DELIB-20261697` - harvested Loyal Opposition GO for the original FAB-10 proposal.
- `bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-001.md` and `-002.md` - original FAB-10 proposal and GO verdict.
- `bridge/gtkb-fab-10-codex-index-adapter-addendum-001.md` and `-002.md` - narrow adapter addendum and GO verdict; the proposal is substantively approved but mechanically cannot start because it lacks `## Requirement Sufficiency`.

## Owner Decisions / Input

No new owner decision is required. This proposal preserves the owner-selected FAB-10 HYG-039 scope from `DELIB-FAB10-REMEDIATION-20260610` and the reviewed addendum scope at `bridge/gtkb-fab-10-codex-index-adapter-addendum-001.md` / `-002.md`.

## Requirement Sufficiency

Existing requirements sufficient. The implementation is governed by `GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DELIB-FAB10-REMEDIATION-20260610`. No new or revised requirement is needed before implementation; the only defect being corrected is missing proposal metadata required by the implementation-start gate.

## Scope Gap Evidence

Command already observed in this session:

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-fab-10-codex-index-adapter-addendum
```

Observed result:

```json
{"authorized": false, "error": "Approved proposal is missing ## Requirement Sufficiency"}
```

The original addendum GO also confirms the actual implementation target remains valid and narrow: `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py` plus focused tests under `platform_tests/scripts/**`.

## Proposed Implementation

1. Extend the Codex apply-patch bridge target predicate to include `bridge/INDEX.md` in addition to versioned bridge files.
2. Add a focused regression test proving a malformed `bridge/INDEX.md` apply-patch payload is rejected through the adapter path.
3. Keep the adapter as a thin dispatcher to `.claude/hooks/bridge-compliance-gate.py`; do not duplicate INDEX parsing policy in the Codex adapter.

## Code Quality Baseline

Changed Python files will be checked with `python -m py_compile`, focused `python -m pytest`, `ruff check`, and `ruff format --check` before a post-implementation report is filed. No baseline lowering, skip marker, or acceptance-threshold relaxation is proposed.

## Out Of Scope

- Changing `.codex/hooks.json` registration unless implementation finds the already-reviewed registration missing.
- Helper-only CAS-protected INDEX writes.
- Retired OS poller or retired smart poller behavior.
- Any MemBase or `groundtruth.db` mutation.
- Any unrelated FAB-10 dispatch-trigger, doctor, or Claude gate change already covered by the original FAB-10 proposal.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Adapter test proves malformed `bridge/INDEX.md` patch content reaches the canonical gate and is blocked. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Adapter remains a thin Codex-to-canonical-gate bridge; versioned bridge file behavior remains covered. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation authorization begins successfully from this GO'd proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report includes focused pytest, py_compile, ruff check, and ruff format evidence. |

## Acceptance Criteria

1. LO returns GO for this corrected addendum.
2. `python scripts\implementation_authorization.py begin --bridge-id gtkb-fab-10-codex-index-adapter-addendum-sufficiency` returns an authorization packet.
3. Codex apply-patch edits to `bridge/INDEX.md` are forwarded to the canonical bridge-compliance gate.
4. Malformed INDEX content that the live gate rejects is also rejected through the Codex adapter path.
5. Focused tests and lint pass.

## Risk and Rollback

Risk is low: the adapter remains a thin dispatcher to the canonical gate and adds one bridge path to the existing bridge-target predicate. Rollback is a file-level revert of the adapter predicate and focused test.

## Recommended Commit Type

`fix:` - repairs the missing Codex INDEX adapter enforcement path for the FAB-10 HYG-039 fix.
