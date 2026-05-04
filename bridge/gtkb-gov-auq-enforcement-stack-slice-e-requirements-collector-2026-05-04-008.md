GO

# Loyal Opposition Review - Requirements Collection Hook REVISED-3 Proposal

**Document:** `gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04`
**Reviewed file:** `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-007.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-05-04
**Verdict:** GO

## Claim

REVISED-3 closes the remaining Codex hook parity defect from `-006`, preserves the already-closed prior findings, and satisfies the mandatory bridge applicability preflight. The proposal is ready for Prime Builder implementation.

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04
```

Observed result:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
operative_file: bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-007.md
packet_hash: sha256:8e71a59c81ae94f57d1d3f21f93975ad68b176ea72e58adb2478ca928155feed
```

## Evidence Reviewed

- Live `bridge/INDEX.md` latest status for this document before review: `REVISED`.
- Full bridge audit trail for this document: `-001` through `-007`.
- Proposal under review: `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-007.md`.
- Prior NO-GO: `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-006.md`.
- File bridge protocol: `.claude/rules/file-bridge-protocol.md`.
- Live tracked settings: `.claude/settings.json`.
- Codex hook intent file: `.codex/hooks.json`.
- Existing hook: `.claude/hooks/spec-classifier.py`.
- Existing formal approval packets for `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001`, `GOV-REQUIREMENTS-COLLECTION-HOOK-001`, `IPR-REQUIREMENTS-COLLECTION-HOOK-001`, and Codex hook parity acknowledgement `DELIB-0836`.
- Role/parity rule: `.claude/rules/acting-prime-builder.md`.

## Prior NO-GO Closure

Prior `-002` findings remain closed: REVISED-3 cites `GOV-SPEC-CAPTURE-TRANSPARENCY-001` instead of the phantom `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`, and it treats existing `IPR-REQUIREMENTS-COLLECTION-HOOK-001` as an append-only v2 update rather than a new record.

Prior `-004` F1 remains closed: REVISED-3 keeps tracked `.claude/settings.json` UserPromptSubmit registration in implementation scope, file list, acceptance criteria, rollback, test mapping, and doctor coverage.

Prior `-006` F1 is closed: REVISED-3 adds `.codex/hooks.json` forward-compatible UserPromptSubmit registration for `.claude/hooks/spec-classifier.py`, includes `.codex/hooks.json` in the implementation file list and rollback path, and adds `test_hook_registered_in_codex_hooks_json` plus `_check_spec_classifier_codex_parity` coverage. This matches the live DCL/IPR parity obligation while respecting `ADR-CODEX-HOOK-PARITY-FALLBACK-001` / `DELIB-0836` by treating `.codex/hooks.json` as hook intent on Windows, not a live interception boundary.

## Passing Evidence

- Mechanical applicability preflight passes with no missing required or advisory specifications.
- The proposal's specification links cover the amended DCL/GOV, transparency governance, owner-decision surfacing, formal-artifact approval, bridge authority, spec-linkage, spec-derived verification, application-placement boundary, and Codex hook parity constraints.
- The Owner Decisions / Input section is non-empty and enumerates the S332 AUQ/directive evidence that authorizes the no-LLM regex-gate pivot.
- Planned implementation paths remain inside `E:\GT-KB`; no `applications/` content is in scope.
- The proposed tests and doctor checks now cover both harness activation surfaces: tracked `.claude/settings.json` and forward-compatible `.codex/hooks.json`.
- The no-LLM regex-gate direction remains aligned with the cited owner directive and avoids new API-key or parallel API-spend dependency.

## Conditions For Post-Implementation Verification

Prime's implementation report must carry forward the linked specifications and include spec-derived evidence for:

- DCL/GOV v2 amendment packets and MemBase updates.
- `IPR-REQUIREMENTS-COLLECTION-HOOK-001` v2 append/update.
- `.claude/hooks/spec-classifier.py` trigger and AUQ-invariant behavior.
- Tracked `.claude/settings.json` registration.
- `.codex/hooks.json` forward-compatible parity registration.
- The 13 proposed tests and the 4 doctor invariants.
- `applications/` remaining untouched.

## Decision Needed From Owner

None for this GO.
