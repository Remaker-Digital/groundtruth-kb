REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627-wi5307-v3-revision
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; owner goal to close black-box bridge, TAFE, and harness complex program
author_metadata_source: explicit_interactive_session_metadata

# REVISED Implementation Proposal - WI-5307 Shared Enforcement Dependency-Surface Disposition

bridge_kind: prime_proposal
Document: gtkb-wi5307-shared-enforcement-baseline-disposition
Version: 009
Responds to: bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-008.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V3-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5307

target_paths: [".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", "scripts/bridge_work_intent_registry.py", "scripts/bridge_applicability_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision addresses the latest Loyal Opposition dependency-ordering NO-GO at `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-008.md`. The version-005/V2 proposal and version-006 GO were valid on authorization vocabulary, but the implementation attempt proved that the two-file target boundary was not executable: clearing nonterminal entry points from `scripts/implementation_authorization.py` breaks importer contracts in `scripts/bridge_work_intent_registry.py` and `scripts/bridge_applicability_preflight.py`.

Prime Builder has created `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V3-20260716`, revoked the superseded V2 two-file PAUTH, and now proposes the exact four-file dependency surface required by `DCL-PROJECT-DEPENDENCY-ORDERING-001`. This proposal authorizes only baseline disposition work for WI-5307. It does not authorize WI-5166, WI-5178, WI-5254, WI-5237, WI-5255, WI-5268 feature completion, dispatcher topology/routing mutation, unrelated runtime mutation, deployment, credential lifecycle, destructive cleanup, git push, or git history rewrite.

## Requirement Sufficiency

Existing requirements sufficient.

`WI-5307`, `TEST-11450`, `DELIB-202666317`, `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V3-20260716`, and the corrected NO-GO at `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-008.md` define the successor boundary. The only scope change is dependency-ordering expansion from the failed two-file implementation envelope to the four files required to either clear or retain the shared authorization entry points without breaking their governed callers.

## Findings Addressed

### F1 (P1, blocking) - Version 006 GO is non-executable under the two-file target boundary

Response: corrected by expanding the proposal and PAUTH target surface to include the dependent importer files named in the corrected NO-GO. The successor implementation will jointly classify these files:

- `.claude/hooks/bridge-compliance-gate.py`
- `scripts/implementation_authorization.py`
- `scripts/bridge_work_intent_registry.py`
- `scripts/bridge_applicability_preflight.py`

The implementation rule is explicit: retained hunks must have terminal owning bridge evidence, and nonterminal foreign hunks must be cleared or isolated so the repository remains importable and the WI-5268 clean-baseline precondition can be assessed without hidden dependency breakage.

The current live state confirms the scope change is necessary: `.claude/hooks/bridge-compliance-gate.py` has no current diff, `scripts/implementation_start_gate.py` has no current diff, while `scripts/implementation_authorization.py`, `scripts/bridge_work_intent_registry.py`, and `scripts/bridge_applicability_preflight.py` contain the coupled entry-point/importer changes cited by LO. The hook file remains in scope only because it was in the original WI-5307 clean-baseline target and must stay clean through final verification.

## Owner Decisions / Input

- `DELIB-202666317` records the owner approval for the bounded WI-5307 shared enforcement baseline disposition so WI-5268 can later start from a clean baseline.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-008.md` records that no new owner decision is required for this successor because exact-target, no-bypass, and dependency-ordering requirements deterministically require the four-file dependency surface.

## Prior Deliberations

- `DELIB-202666317` - owner approval for the WI-5307 shared enforcement baseline disposition.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-001.md` through `-008.md` - complete WI-5307 proposal, GO, NO-ACTION, corrected NO-GO, V2 proposal, V2 GO, implementation fail-closed NO-ACTION, and corrected dependency-ordering NO-GO chain.
- `bridge/gtkb-wi5178-governed-predecessor-closure-004.md` - latest NO-GO for operation-time predecessor closure; cited by LO as nonterminal owner evidence for retained authorization-script behavior.
- `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-008.md` - latest VERIFIED stand-down only; cited by LO as bridge-only evidence that does not itself terminally own source mutation.
- `bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md` - terminal VERIFIED owner for retained project-authorization bootstrap lifecycle behavior in the shared authorization script.
- `TEST-11450` - linked WI-5307 verification obligation: the blocking files must match committed HEAD or have independently VERIFIED owning bridge evidence before WI-5268 protected mutation.

## Scope Changes

Changed from the version-005/V2 two-file target set to the V3 four-file dependency surface:

- Added `scripts/bridge_work_intent_registry.py` because it imports and calls `validate_bridge_project_authorization_operation`.
- Added `scripts/bridge_applicability_preflight.py` because it imports and calls `validate_structured_pauth_spec_amendment`.
- Kept `scripts/implementation_authorization.py` because it owns the shared entry points under disposition.
- Kept `.claude/hooks/bridge-compliance-gate.py` because it was part of the original WI-5307 clean-baseline target and must remain clean.

Explicitly excluded: `scripts/implementation_start_gate.py`, because it is clean relative to committed HEAD and is not required for the dependency correction identified in version 008.

## Cross-Harness Disposition

This proposal touches `.claude/hooks/bridge-compliance-gate.py`, a harness-surface file. The intended disposition is baseline preservation, not a new harness behavior rollout.

| Harness / surface | Disposition |
| --- | --- |
| Claude Code / `.claude/hooks/bridge-compliance-gate.py` | Keep clean relative to committed HEAD unless a terminal owning bridge artifact is discovered before implementation. No new Claude-only hook behavior is proposed. |
| Codex / `.codex/hooks.json`, `.codex/gtkb-hooks/**`, `.codex/skills/**` | No target mutation. Existing Codex parity surfaces remain unchanged. |
| Cursor, Antigravity, Ollama, OpenRouter, provider headless workers | No target mutation. This baseline-disposition slice does not add or remove provider harness behavior. |

If implementation discovers a required harness-behavior change rather than a baseline cleanup, Prime Builder will stop and file a separate proposal with explicit parity scope instead of expanding this WI-5307 cleanup in place.

## Implementation Plan

After LO GO, Prime Builder will acquire a fresh implementation claim and run `scripts/implementation_authorization.py begin` for this bridge thread. The implementation will:

1. Reconfirm the four target files and `scripts/implementation_start_gate.py` with `git status --short`.
2. Classify every retained delta in the three dirty target files by owning bridge evidence.
3. Preserve only hunks with independently terminal owning evidence, including the WI-5279 bootstrap lifecycle behavior where still required.
4. Clear or isolate nonterminal WI-5178 and WI-5254 source-level behavior across the shared entry points and importers so imports do not break and nonterminal behavior is not silently retained.
5. Keep `.claude/hooks/bridge-compliance-gate.py` clean relative to committed HEAD unless a later independently terminal owning artifact is discovered before implementation.
6. File a post-implementation report that maps the result to `TEST-11450`, includes clean-baseline evidence, and states whether any retained hunk is backed by terminal bridge evidence.

The implementation will not use direct black-box internals mutation, deployment, credential lifecycle, git push, history rewrite, or unrelated dispatcher/runtime mutation.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Specification-Derived Verification Plan

| Specification / Test | Verification command or evidence | Expected result |
| --- | --- | --- |
| `TEST-11450`, `GOV-WORK-TREE-HYGIENE-001` | `git status --short -- .claude/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py scripts/bridge_work_intent_registry.py scripts/bridge_applicability_preflight.py scripts/implementation_start_gate.py` | Only terminal-owned retained deltas remain; clean files are clean; `scripts/implementation_start_gate.py` remains clean. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Import and focused regression checks for `scripts/implementation_authorization.py`, `scripts/bridge_work_intent_registry.py`, and `scripts/bridge_applicability_preflight.py` | Importer contracts do not call missing entry points; any retained entry point has terminal owning evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | `python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short --timeout=300` | Focused PAUTH, implementation-start, work-intent, and applicability-preflight tests pass. |
| Bridge proposal governance specs | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5307-shared-enforcement-baseline-disposition-009.md --json` | `preflight_passed: true`, `missing_required_specs: []`, `blocking_errors: []`. |
| ADR/DCL clause gate | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5307-shared-enforcement-baseline-disposition-009.md` | Exit code 0; no blocking gaps. |
| Python quality gates | `python -m ruff check scripts/implementation_authorization.py scripts/bridge_work_intent_registry.py scripts/bridge_applicability_preflight.py` and `python -m ruff format --check scripts/implementation_authorization.py scripts/bridge_work_intent_registry.py scripts/bridge_applicability_preflight.py` | Lint and format pass on changed Python targets. |

## Pre-Filing Preflight Subsection

Prime Builder ran the candidate-content applicability preflight and ADR/DCL clause preflight against this completed draft before live filing.

Applicability preflight:

- command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5307-shared-enforcement-baseline-disposition-009.md --json`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

Clause preflight:

- command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5307-shared-enforcement-baseline-disposition-009.md`
- clauses evaluated: 5
- must_apply: 3
- may_apply: 2
- not_applicable: 0
- evidence gaps in must_apply clauses: 0
- blocking gaps: 0
- exit code: 0

Loyal Opposition should rerun both mandatory checks against the operative bridge file before GO.

## Acceptance Criteria

- The live bridge proposal cites `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V3-20260716` and the four exact target paths.
- The superseded V2 PAUTH is revoked and the active V3 PAUTH includes `WI-5307` plus dependency-ordering specs.
- LO can issue GO without re-looping into the two-file importer dependency failure.
- After implementation, `TEST-11450` can be evaluated without hidden nonterminal importer dependencies.

## Risk And Rollback

Risk: clearing nonterminal shared authorization behavior may expose tests or callers that were accidentally relying on unverified behavior. Mitigation: the expanded target surface lets the implementation adjust the importers and entry points together instead of leaving missing symbols.

Rollback: before implementation, rollback is to leave this REVISED proposal unapproved. After implementation, rollback is a normal scoped revert of the approved four target files plus any filed implementation report, with the bridge thread remaining non-terminal until LO accepts the corrected state.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
