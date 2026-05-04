NO-GO

# Loyal Opposition Review - Requirements Collection Hook Revised Proposal

**Document:** `gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04`
**Reviewed file:** `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-003.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-05-04
**Verdict:** NO-GO

## Claim

The revised proposal resolves the two prior NO-GO findings, and the mechanical applicability preflight passes. It is still not ready for GO because the implementation plan depends on project-level `spec-classifier.py` activation in `.claude/settings.json`, but the live tracked settings file does not register that hook and the proposal inconsistently treats registration as already present.

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04
```

Observed result:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
operative_file: bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-003.md
packet_hash: sha256:291606d64712f175364638556cb344bf0c235f2d22f3c88158cf66872018e738
```

## Evidence Reviewed

- Live `bridge/INDEX.md` latest status for this document: `REVISED`.
- Proposal: `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-003.md`.
- Prior NO-GO: `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-002.md`.
- File bridge protocol: `.claude/rules/file-bridge-protocol.md`.
- Live tracked settings: `.claude/settings.json`.
- Local workstation settings: `.claude/settings.local.json`.
- Existing hook: `.claude/hooks/spec-classifier.py`.
- Live MemBase spot-checks for `GOV-REQUIREMENTS-COLLECTION-HOOK-001`, `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001`, `GOV-SPEC-CAPTURE-TRANSPARENCY-001`, and `IPR-REQUIREMENTS-COLLECTION-HOOK-001`.

## Prior NO-GO Closure

Prior F1 is closed: the revised proposal removes the phantom `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` from blocking spec linkage and cites `GOV-SPEC-CAPTURE-TRANSPARENCY-001`.

Prior F2 is closed: the revised proposal no longer claims `IPR-REQUIREMENTS-COLLECTION-HOOK-001` must be created from scratch and instead proposes an append-only v2 update/promote path for the existing record.

## Findings

### F1 - Blocking - Hook registration plan contradicts live tracked settings and the proposal's own acceptance criteria

**Evidence:** The revised proposal says application-placement compliance includes `.claude/settings.json` as "already registered" at line 41. It later requires test coverage for `settings.json` registration at line 82, defines `test_hook_registered_in_claude_settings` as "hook in `.claude/settings.json` UserPromptSubmit" at line 152, and maps the amended DCL location requirement to that test at line 176.

The live tracked `.claude/settings.json` only registers `.claude/hooks/owner-decision-tracker.py --mode user-prompt-submit` under `UserPromptSubmit` and has no `spec-classifier.py` entry. `.claude/settings.local.json` does register `spec-classifier.py`, but that file is workstation-local and not the tracked project-level hook configuration. The proposal's final "Project Root Boundary Compliance" file list also omits `.claude/settings.json` from the actual change list, despite the acceptance criteria depending on it.

**Risk / impact:** If Prime implements exactly as proposed, the tracked project-level hook may remain inert even while tests are written against a registration condition that is not in the implementation scope. That undermines the stated AUQ-only spec-creation invariant because the reminder hook will not reliably fire in fresh clones or shared harness contexts. It also makes the post-implementation `test_hook_registered_in_claude_settings` either fail or pass against the wrong file, depending on how the test is written.

**Required action:** Revise the proposal to make hook activation unambiguous. Either:

1. explicitly add `.claude/settings.json` UserPromptSubmit registration for `.claude/hooks/spec-classifier.py` to the implementation scope, final file-change list, acceptance criteria, and rollback plan; or
2. explicitly choose `.claude/settings.local.json` as the activation surface, justify why local-only activation satisfies the amended DCL/GOV, and update the tests, doctor invariant, and risk analysis accordingly.

Given the proposal frames this as project governance enforcement, option 1 appears to be the stronger path.

## Passing Evidence

- Mechanical applicability preflight passes with no missing required or advisory specs.
- Prior phantom-spec and duplicate-IPR findings are substantively addressed.
- Planned paths remain inside `E:\GT-KB`; no live dependency outside the project root was identified.
- The no-LLM regex-gate scope is supported by the cited owner-direction narrative in the revised proposal.

## Required Revision

Submit `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-005.md` that:

1. Corrects the `.claude/settings.json` registration contradiction.
2. Includes the chosen settings file in the explicit implementation file list and rollback plan.
3. Aligns `test_hook_registered_in_claude_settings` and `_check_spec_classifier_settings_registered` with the chosen activation surface.
4. Re-runs and includes the applicability preflight output.

## Decision Needed From Owner

None for this NO-GO.
