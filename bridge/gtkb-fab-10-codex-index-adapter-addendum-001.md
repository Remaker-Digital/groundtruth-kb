NEW

bridge_kind: prime_proposal
Document: gtkb-fab-10-codex-index-adapter-addendum
Version: 001
Author: prime-builder (Codex, harness A) - interactive owner session
Date: 2026-06-12
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

No KB mutation: this addendum changes a Codex hook adapter and focused tests only; no `groundtruth.db` write.

---

# FAB-10 Codex INDEX Adapter Addendum

## Summary

FAB-10's GO'd proposal requires HYG-039 protection for the Codex adapter path, but the approved target list
does not include the adapter script that actually decides which `apply_patch` bridge writes are forwarded
to the canonical bridge-compliance gate.

This addendum authorizes the missing adapter change only:

- Update `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py` so Codex `apply_patch` edits to
  `bridge/INDEX.md` are forwarded to `.claude/hooks/bridge-compliance-gate.py`, just like versioned bridge
  files are today.
- Add focused tests under `platform_tests/scripts/**`.

The existing FAB-10 GO remains valid for the already-scoped trigger, live gate, doctor, hook config, and
platform test paths. This addendum does not change FAB-10's design or expand helper-only CAS writes, which
remain out of scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` is the canonical bridge workflow state and must be protected from malformed writes.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook parity requires the apply-patch adapter to enforce the same bridge-compliance gate as Claude Write/Edit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the addendum cites concrete governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification remains spec-derived.
- `GOV-STANDING-BACKLOG-001` - WI-4422 remains the governed backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all paths are in-root under `E:\GT-KB`.

## Prior Deliberations

- `DELIB-FAB10-REMEDIATION-20260610` - owner selected INDEX well-formedness lint now, helper-only writes later.
- `bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-001.md` - original FAB-10 proposal requiring gate + Codex adapter + doctor INDEX lint.
- `bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-002.md` - LO GO constrained implementation to listed target paths.

## Owner Decisions / Input

No new owner decision is required. This addendum implements the already-selected HYG-039 Codex adapter portion by adding the adapter script that the original target list omitted.

## Scope Gap Evidence

Implementation target-path preflight for the required adapter script fails against the GO'd FAB-10 scope:

- Command: `python scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-fab-10-dispatch-telemetry-claim-contract --candidate-paths .codex\gtkb-hooks\bridge-compliance-gate-apply-patch-adapter.py --json`
- Result: `verdict: out_of_scope_drift`
- Out-of-scope candidate: `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`

Live source inspection confirms the adapter currently forwards only versioned `bridge/*-NNN.md` files, so `bridge/INDEX.md` patches are not passed to the canonical gate.

## Proposed Implementation

1. Extend the Codex apply-patch bridge-compliance adapter's bridge-target predicate to include `bridge/INDEX.md`.
2. Add a focused regression test that a malformed `bridge/INDEX.md` apply-patch payload is rejected through the adapter path.
3. Keep the adapter delegating all substantive validation to `.claude/hooks/bridge-compliance-gate.py`; do not duplicate INDEX parsing logic in the Codex adapter.

## Out Of Scope

- Changing `.codex/hooks.json` registration unless the existing adapter registration is missing.
- Helper-only CAS-protected INDEX writes.
- Any change to retired OS poller or retired smart poller behavior.
- Any MemBase/KB mutation.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Adapter test proves malformed `bridge/INDEX.md` patch content reaches the canonical gate and is blocked. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Adapter remains a thin Codex-to-canonical-gate bridge; versioned bridge file behavior remains covered. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report includes focused pytest, ruff, and format evidence. |

## Acceptance Criteria

1. LO returns GO for the addendum.
2. Codex apply-patch edits to `bridge/INDEX.md` are forwarded to the canonical bridge-compliance gate.
3. Malformed INDEX content that the live gate rejects is also rejected through the Codex adapter path.
4. Focused tests and lint pass.

## Risk and Rollback

Risk is low: the adapter remains a thin dispatcher to the canonical gate and adds one file path to the existing bridge-target predicate. Rollback is a file-level revert of the adapter predicate and focused test.
