REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 897cb58e-6705-4dfd-a4b3-d64941dbeeec
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

bridge_kind: prime_proposal
Document: gtkb-reconcile-included-work-item-ids-semantics
Version: 022 (REVISED)
Date: 2026-06-25 UTC
Responds-To: bridge/gtkb-reconcile-included-work-item-ids-semantics-021.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3510

target_paths: ["scripts/implementation_authorization.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", ".claude/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_project_authorization.py", "platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py", "platform_tests/scripts/test_pauth_included_wi_ids_gate_parity.py"]

# Substantive Implementation Proposal — Reconcile `included_work_item_ids` Gate Semantics (Restrictive)

## Revision Claim

The owner-decision blocker recorded through `-021` (GO, blocker-only) is now resolved.
This interactive Prime Builder session presented the `DELIB-2547` semantics AskUserQuestion
and the owner selected RESTRICTIVE semantics, captured as `DELIB-20266083`. The matching
design constraint `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` was presented for
formal approval, approved, and inserted into MemBase (version 1, status `specified`,
testability `automatable`). This REVISED converts the thread from a blocker record into a
substantive, implementation-ready proposal whose tests derive from the approved DCL.

## Requirement Sufficiency

Existing requirements sufficient.

- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` (approved + inserted 2026-06-25)
  defines the canonical restrictive semantics and the machine-checkable assertions A1–A4.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` governs the implementation-start
  authorization gate.

No new requirement is needed; this proposal implements the approved DCL.

## Problem / Current Divergence

For a cited `(authorization, project, work item)` with a non-empty `included_work_item_ids`
list, the two governance gates currently disagree:

- Implementation-start gate — `scripts/implementation_authorization.py`,
  `validate_project_authorization_row` (~L855–863): authorized when
  `work_item_id in included_items` OR `_work_item_in_project(...)` is true (additive / loose).
- Bridge Write-time gate — `bridge-compliance-gate.py`, `_wi_project_membership_gap`
  (~L1166–1191): blocks unless the work item is an active project member AND
  (the included list is empty OR the work item is listed) (restrictive / strict, with
  membership checked before exclusion).

The divergence is the friction `WI-3510` reconciles. `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
makes the included list the single authoritative scope at both gates.

## Proposed Implementation

### 1. Implementation-start gate — `scripts/implementation_authorization.py` (`validate_project_authorization_row`)

Replace the additive `not in included AND not member` test with restrictive semantics:

- If `work_item_id in excluded_items`: raise (excluded; unchanged, precedence preserved).
- Else if `included_items` is non-empty: authorized iff `work_item_id in included_items`;
  raise `AuthorizationError` ("not in the authorizing included_work_item_ids list") otherwise.
  Active project membership is no longer consulted when a list is present.
- Else (`included_items` empty): authorized iff `_work_item_in_project(...)`; raise otherwise.

Net effect: tightens the gate — a project member that is not listed is no longer
authorized when the authorization carries a non-empty list.

### 2. Bridge Write-time gate — `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (`_wi_project_membership_gap`)

Reorder and rewrite to match the restrictive truth table and exclusion precedence:

- Resolve the authorization row first; return existing authorization-not-found / inactive /
  expired tokens as today.
- Check `excluded_work_item_ids` first (precedence): return `wi-excluded-from-authorization`.
- If `included_work_item_ids` is non-empty: authoritative — return
  `wi-not-included-by-authorization` iff the work item is not listed; do NOT require an
  active project membership row.
- Else (empty list): fall back to active project membership — return
  `wi-not-found-in-project` / `wi-membership-inactive` as today.

The byte-identical activated copy `.claude/hooks/bridge-compliance-gate.py` is re-synced
from the template after the edit so the live hook reflects the change. No new condition
tokens are introduced; the docstring token order is updated to match.

### 3. Tests (spec-derived from DCL assertions A1–A4)

- `platform_tests/scripts/test_project_authorization.py`: add restrictive-semantics cases —
  non-empty list authorizes only listed WIs; member-not-listed now blocked; empty-list
  falls back to membership; excluded precedence.
- `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`: add
  restrictive-semantics cases — listed-but-not-member now authorized (no membership row
  required); member-not-listed blocked; empty-list requires membership; excluded precedence.
- `platform_tests/scripts/test_pauth_included_wi_ids_gate_parity.py` (new): assert the two
  gates produce the same authorize/block verdict across the `(member, listed)` truth table
  for non-empty and empty included lists (A4 parity).

## Specification Links

- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` — the approved constraint this proposal
  implements (assertions A1–A4).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — governs the implementation-start
  authorization gate; this proposal keeps "membership alone is not authorization" true.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only bridge state, status routing, work-intent
  claim, project-linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant
  specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — tests derive from the DCL assertions.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project Authorization / Project /
  Work Item metadata carried forward.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the change touches two
  enforcement gates (write-time + impl-start); both layers must agree.
- `GOV-STANDING-BACKLOG-001` — `WI-3510` is standing-backlog work under
  `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all paths and evidence remain inside `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the owner-significant authorization semantics is
  preserved as a governed DCL artifact, not only in gate code.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — implementation derives from durable artifacts
  (the approved DCL + owner-decision deliberation).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — touching divergent authorization semantics
  triggered specification capture (the new DCL) before implementation.
- `.claude/rules/file-bridge-protocol.md` — bridge lifecycle, mandatory gates.
- `.claude/rules/codex-review-gate.md` — pre-implementation review gate, requirement
  sufficiency.

## Spec-to-Test Mapping (Derived From DCL Assertions)

- A1 (impl-start restrictive) → `platform_tests/scripts/test_project_authorization.py`
  restrictive cases. Command: `python -m pytest platform_tests/scripts/test_project_authorization.py -q --tb=short`
- A2 (write-time restrictive) →
  `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py` restrictive
  cases. Command: `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py -q --tb=short`
- A3 (excluded precedence at both gates) → cases in both files above.
- A4 (gate parity across truth table) → `platform_tests/scripts/test_pauth_included_wi_ids_gate_parity.py`.
  Command: `python -m pytest platform_tests/scripts/test_pauth_included_wi_ids_gate_parity.py -q --tb=short`

## Prior Deliberations

- `DELIB-20266083` — owner AUQ decision (2026-06-25): restrictive — the list is the
  authoritative scope. Resolves the `DELIB-2547` deferral.
- `DELIB-2547` — S379 disposition "Reduce friction, keep gates"; deferred the directionality
  choice now resolved by `DELIB-20266083`.
- `DELIB-20265457` — owner AUQ authorizing the `PROJECT-GTKB-RELIABILITY-FIXES`
  non-fast-lane proposal batch including `WI-3510`.
- `bridge/gtkb-reconcile-included-work-item-ids-semantics-001.md` … `-021.md` — full
  NO-GO / REVISED blocker cycle plus the blocker-only GO at `-021`.

## Owner Decisions / Input

This proposal depends on two owner decisions captured this session through AskUserQuestion:

- AUQ `AUQ-2026-06-25-WI-3510-pauth-included-wi-ids-semantics` — semantics choice. Owner
  answer: "Restrictive — the `included_work_item_ids` list is the authoritative scope
  (empty list falls back to active project membership)." Recorded as `DELIB-20266083`.
- AUQ `AUQ-2026-06-25-DCL-PAUTH-INCLUDED-WIDS-RESTRICTIVE-approval` — formal artifact
  approval. Owner answer: "Approve & insert `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
  as presented." Approval packet:
  `.groundtruth/formal-artifact-approvals/2026-06-25-DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001.json`.

Carried-forward authorization:
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` authorizes autonomous
  bridge flow for the reliability batch including `WI-3510`.

## Verification Plan

After implementation:

- `python -m pytest platform_tests/scripts/test_project_authorization.py platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/scripts/test_pauth_included_wi_ids_gate_parity.py -q --tb=short`
- `python -m ruff check scripts/implementation_authorization.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/scripts/test_project_authorization.py platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/scripts/test_pauth_included_wi_ids_gate_parity.py`
- `python -m ruff format --check` on the same files.
- Confirm `.claude/hooks/bridge-compliance-gate.py` is byte-identical to the edited template
  after re-sync (`diff`).
- Run the DCL assertions: `gt assert` (or the kb-assert surface) to confirm A1–A4 register.

## Risk and Rollback

- Risk: tightening the impl-start gate could block an in-flight proposal whose WI is a
  project member but not in its PAUTH's non-empty included list. Mitigation: this is the
  intended restrictive behavior per `DELIB-20266083`; the 77 listed-but-non-member pairs in
  live data remain authorized (the change relaxes Write-time for exactly that class).
- Risk: editing the activated hook copy without re-syncing the template (or vice versa)
  leaves the live gate inconsistent with the tracked source. Mitigation: edit the template,
  re-sync the activated copy, and assert byte-identity in verification.
- Rollback: revert the gate edits and tests; append a further bridge version. No data
  migration is involved.

## Recommended Commit Type

`fix:` — reconciles divergent, partially-incorrect authorization-gate enforcement to a
single canonical semantics. No new capability surface is added.

## Pre-Filing Preflight Subsection

Candidate-content preflights are run on this draft before the live bridge Write:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-reconcile-included-work-item-ids-semantics --content-file .gtkb-state/bridge-revisions/drafts/gtkb-reconcile-included-work-item-ids-semantics-022.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-reconcile-included-work-item-ids-semantics --content-file .gtkb-state/bridge-revisions/drafts/gtkb-reconcile-included-work-item-ids-semantics-022.md
```

Expected clean result: `preflight_passed: true`, `missing_required_specs: []`; clause
preflight mandatory mode exit 0, blocking gaps 0. The Write-time bridge-compliance gate
reruns the applicability check on final content.
