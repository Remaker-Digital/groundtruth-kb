NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Auth-gate Requirement Sufficiency parser escapes pre-impl review surfaces

bridge_kind: prime_proposal
Document: gtkb-auth-gate-requirement-sufficiency-parser-surfaces
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3454

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The GT-KB Requirement-Sufficiency contract is enforced by TWO independent regex implementations that can disagree, so a proposal can pass the pre-GO Write-time gate yet be rejected by the post-GO implementation-start parser. The Write-time gate (`.claude/hooks/bridge-compliance-gate.py` `_requirement_sufficiency_section_gap`, via `REQUIREMENT_SUFFICIENCY_OPERATIVE_STATES`) recognizes only two strict literal operative phrasings, while the impl-start parser (`scripts/implementation_authorization.py` `requirement_sufficiency_state`, via the bounded `REQUIREMENT_SUFFICIENCY_RE` / `REQUIREMENT_GAP_RE` plus the `REQUIREMENT_SUFFICIENCY_PHRASES` literal list) classifies a broader vocabulary. Because the two surfaces are not derived from one classifier, a Requirement-Sufficiency section whose opener phrasing the impl-start parser will reject as `unrecognized`/`gap` is not reliably caught at filing/GO time; it escapes the bridge-compliance-gate Write hook, the clause preflight, and Codex substantive review, and only surfaces as an `AuthorizationError` at `implementation_authorization.py begin` activation time (post-GO), forcing a wasted REVISED round.

## Defect / Reproduction

Observed incident (origin of WI-3454): on bridge thread `gtkb-project-completion-scanner-addressing-thread-fix` the Requirement-Sufficiency section opener escaped pre-impl review despite a Codex GO at `-008`, and only failed at impl-start in S372; REVISED-4 (`-009`) was required purely to restate the opener phrase. None of the three pre-impl surfaces caught it: the bridge-compliance-gate Write hook (`_requirement_sufficiency_section_gap`) only verifies that one of two strict literal operative phrasings is present (it checks section existence + a narrow operative-state regex, not the broader vocabulary the impl-start parser accepts); the clause preflight checks evidence patterns, not this section's opener; and Codex review inspects substance, not the parser regex.

Reproduction (logical): author an implementation proposal (NEW/REVISED, `bridge_kind: prime_proposal`, with `target_paths`) whose `## Requirement Sufficiency` section opens with a concrete statement the impl-start parser does NOT classify as `sufficient` (for example a free-form opener that omits the strict literal token). The Write-time gate's `REQUIREMENT_SUFFICIENCY_OPERATIVE_STATES` either accepts a phrasing the impl-start parser rejects, or the two surfaces simply classify differently; the proposal passes filing and can receive GO. Then run `python scripts/implementation_authorization.py begin --bridge-id gtkb-...`: `requirement_sufficiency_state` returns `unrecognized` (or `gap`), and `create_authorization_packet` raises `AuthorizationError`. Expected: the Write-time gate accepts/rejects EXACTLY what the impl-start parser will accept/reject, so any opener the impl-start parser would reject is surfaced at filing time (before GO), not post-GO.

Root cause: duplicated, drift-prone classification logic. The fix removes the duplication by making the Write-time gate consult the same bounded classifier semantics the impl-start parser uses, eliminating the divergence that lets opener phrasings escape pre-impl review. This is the WI's path (B) realized as de-duplication (single shared classifier), which is the lowest-behavior-change option among the WI's candidate paths.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/hooks/bridge-compliance-gate.py`, `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, `platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge protocol's GO/VERIFIED discipline is the authority being undermined; a Requirement-Sufficiency defect that surfaces only post-GO means GO was granted on a proposal the impl-start gate will reject, so the gate must enforce the contract before GO.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the Requirement-Sufficiency section is a durable proposal artifact; this fix keeps its filing-time validation consistent with its activation-time validation so the artifact's accepted state is stable across the lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing specs for the Requirement-Sufficiency enforcement surfaces (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives tests from the cited specs and runs them against both hook copies (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `SPEC-AUQ-POLICY-ENGINE-001` - governing spec for the FAB-14 / HYG-046 Requirement-Sufficiency classifier (`requirement_sufficiency_state`); the Write-time gate must agree with that canonical classifier rather than maintain a second, narrower vocabulary.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to GT-KB platform hook surfaces and platform tests; no adopter/application surface is touched and no application-placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-3454 is a standing-backlog work item (origin=defect, P2) under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` are a byte-identical hook pair; this fix edits BOTH copies in lockstep to preserve template/active parity per the parity contract.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the Requirement-Sufficiency state remains an artifact-backed proposal property validated identically at every gate, not re-derived per surface.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the filing-time enforcement trigger with the activation-time lifecycle state it is meant to anticipate.

## Prior Deliberations

- `DELIB-20265324` - Loyal Opposition GO: Requirement-Sufficiency operative-precedence fix - prior fix to the operative-state matching logic this proposal further consolidates; establishes the precedent that the operative-state semantics are the contested surface.
- `DELIB-20261498` - Loyal Opposition Verdict - Project Completion Scanner Addressing-Thread Fix Implementation - the verdict thread (`gtkb-project-completion-scanner-addressing-thread-fix`) whose opener-phrase escape in S372 is the origin incident for WI-3454.
- `DELIB-20261020` - Loyal Opposition Verification - Impl-Auth and Impl-Start-Gate Parser Hygiene - sibling parser-hygiene verification for the `implementation_authorization.py` parser surface, confirming this module's classifier is the canonical one to align to.
- `DELIB-2105` - Bridge thread: gtkb-reliability-fast-lane (VERIFIED) - the reliability fast-lane authorization lineage under which PROJECT-GTKB-RELIABILITY-FIXES defect fixes are routed.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - the standing reliability fast-lane authorization that routes single-concern origin=defect fixes under PROJECT-GTKB-RELIABILITY-FIXES; cited as the project-membership authorization envelope for WI-3454.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work-item batch (P1/P2 first); WI-3454 is P2 and in scope.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing fast-lane direction (carried via the PAUTH above); see `## Fast-Lane Eligibility` below for a NON-FAST-LANE determination requiring an explicit owner AUQ on the path choice before implementation proceeds.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` (GO/VERIFIED discipline) and `SPEC-AUQ-POLICY-ENGINE-001` (the canonical Requirement-Sufficiency classifier) already establish that the same Requirement-Sufficiency contract governs both the filing-time gate and the activation-time parser; this fix makes the two surfaces enforce that single existing contract consistently. No new or revised requirement/specification is introduced. (NOTE: this sufficiency claim holds for the de-duplication / path-B-as-shared-classifier approach proposed here; if the owner selects WI path (A) "loosen the parser to accept more openers / treat any non-empty body as sufficient", that would relax the contract and would require a new/revised requirement — see `## Fast-Lane Eligibility`.)

## Proposed Scope

Minimal, behavior-preserving de-duplication so the Write-time gate accepts/rejects exactly what the impl-start parser accepts/rejects:

1. In `.claude/hooks/bridge-compliance-gate.py`, replace the gate's private operative-state classification inside `_requirement_sufficiency_section_gap` so that, after the existing presence/placeholder checks pass, the section body's operative state is derived from the SAME bounded classifier semantics used by `scripts/implementation_authorization.py` `requirement_sufficiency_state` (the FAB-14 / HYG-046 classifier governed by `SPEC-AUQ-POLICY-ENGINE-001`). Concretely: import the shared `requirement_sufficiency_state` (and its bounded regexes) from `implementation_authorization` when resolvable, with a vendored fail-soft fallback that mirrors the same bounded patterns (the hook already uses this import-or-fallback pattern for `bridge_author_metadata`, lines 39-58). Map the classifier result to the existing gap descriptors:
   - `sufficient` or `gap` (exactly one operative state) -> no gap (accept).
   - `unrecognized` -> the existing "no operative state ('Existing requirements sufficient' or 'New or revised requirement required before implementation')" descriptor.
   - the dual-state case (both states asserted) continues to be rejected with the existing "multiple operative states" descriptor (preserve WI-3439 verification NO-GO -008 behavior).
2. Apply the byte-identical change to `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` so the template/active hook parity invariant (`ADR-CODEX-HOOK-PARITY-FALLBACK-001`; `test_template_and_active_hook_byte_identical`) is preserved.
3. Extend `platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py` with regression tests (see verification plan) asserting that the Write-time gate now AGREES with `requirement_sufficiency_state` across the bounded vocabulary, and that the existing accept/reject/dual-state cases are unchanged.

Scope guard: the change is confined to the operative-state classification step AFTER the existing presence/placeholder/bridge_kind/target_paths gating; it does NOT alter when the gate fires (still `first_line in PROJECT_METADATA_STATUSES` + implementation-proposal bridge_kind + target_paths). The impl-start parser (`implementation_authorization.py`) is the canonical classifier and is NOT modified; this fix aligns the gate TO it. The WI's path (A) (relaxing the contract to accept arbitrary openers) is explicitly out of scope pending owner AUQ.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (contract enforced before GO) + `SPEC-AUQ-POLICY-ENGINE-001` (canonical classifier) | `test_write_gate_agrees_with_impl_start_on_bounded_sufficiency` | For each bounded sufficiency phrasing accepted by `requirement_sufficiency_state` (e.g. "Existing requirements are sufficient...", "Requirements remain sufficient.", "Existing owner direction and WI-4213 are sufficient."), the Write gate returns no gap (proposal is NOT denied). |
| `SPEC-AUQ-POLICY-ENGINE-001` (unrecognized opener must be caught at filing) | `test_write_gate_denies_unrecognized_opener_caught_by_impl_start` | A `## Requirement Sufficiency` section whose opener `requirement_sufficiency_state` classifies as `unrecognized` is DENIED by the Write gate (surfaced at filing time, not post-GO). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (no false-negative regression) | `test_write_gate_accepts_gap_state_unchanged` | The valid gap state ("New or revised requirement required before implementation.") is still accepted by the Write gate (matches impl-start `gap`), preserving existing behavior. |
| `SPEC-AUQ-POLICY-ENGINE-001` (exactly one operative state) | `test_write_gate_rejects_dual_state_unchanged` | A section asserting BOTH operative states is still DENIED with the "multiple operative states" descriptor (WI-3439 NO-GO -008 preserved). |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (template/active parity) | `test_template_and_active_hook_byte_identical` (existing, re-run) | The template hook and the `.claude/hooks` copy remain byte-identical after the change. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py -q --tb=short`
- `python -m ruff check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py`
- `python -m ruff format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py`

## Acceptance Criteria

1. The bridge-compliance-gate Write hook's Requirement-Sufficiency operative-state decision is derived from the same bounded classifier as `implementation_authorization.py` `requirement_sufficiency_state`; for any `## Requirement Sufficiency` section, the gate denies-at-filing exactly the openers the impl-start parser would reject post-GO.
2. The existing accept (sufficient / gap), dual-state reject, and bridge_kind/target_paths scoping behaviors are unchanged (no regression).
3. `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` remain byte-identical.
4. The derived tests pass; `ruff check` and `ruff format --check` are clean on all three changed files.

## Risks / Rollback

- Risk: the hook's import-of-`implementation_authorization` could fail in a partial install. Mitigation: use the established import-or-vendored-fallback pattern already present in the hook (lines 39-58 for `bridge_author_metadata`); the fallback mirrors the same bounded patterns so behavior is identical when the import is unavailable, and a parity/equivalence test pins the fallback to the canonical patterns.
- Risk: aligning the gate to the broader impl-start vocabulary could accept a phrasing previously denied at filing. Mitigation: this is the intended convergence (the impl-start parser is canonical); the dual-state rejection and presence/placeholder checks are preserved, and tests assert the gate is no more permissive than `requirement_sufficiency_state`.
- Risk: template/active drift if only one hook copy is edited. Mitigation: edit both in lockstep; `test_template_and_active_hook_byte_identical` fails closed on drift.
- Rollback: revert the operative-state classification change in both hook copies and remove the added tests; the change is a localized classification swap plus tests, fully reversible with no migration or schema change.

## Fast-Lane Eligibility

NON-FAST-LANE (fastlane_confirmed=false). The WI itself states the remedy has "two implementation paths (genuine tradeoff, requires AUQ before impl)": (A) loosen the parser / treat any non-empty body as sufficient unless the gap phrase is explicit, vs (B) move/duplicate the check into the Write-time gate so it surfaces at filing time, with combined A+B also viable. This proposal selects path (B) realized as de-duplication (lowest behavior change), but the A-vs-B selection is an unresolved owner decision, and path (A) would relax the Requirement-Sufficiency contract (a new/revised requirement). The reliability fast-lane requires no new/revised requirement and no behavior change beyond defect removal; the unresolved path choice and the contract-relaxation option in path (A) disqualify automatic fast-lane handling. REQUIRED before implementation: an owner AskUserQuestion confirming the path (recommended: B-as-de-duplication, as scoped here) per `.claude/rules/prime-builder-role.md` (AskUserQuestion as the Only Valid Owner-Decision Channel). Origin (defect), single-concern, and size (~3 files, well under the ~150-net-line guide) are all satisfied; only the AUQ-gated path choice blocks fast-lane.

## Files Expected To Change

- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py`

## Recommended Commit Type

`fix`
