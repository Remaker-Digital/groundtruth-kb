REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; owner goal to close black-box bridge, TAFE, and harness complex program
author_metadata_source: explicit_interactive_session_metadata

# REVISED Implementation Proposal - WI-5307 Shared Enforcement Four-File Authorization Correction

bridge_kind: prime_proposal
Document: gtkb-wi5307-shared-enforcement-baseline-disposition
Version: 011
Responds to: bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-010.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V4-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5307

target_paths: [".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", "scripts/bridge_work_intent_registry.py", "scripts/bridge_applicability_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision answers the latest Loyal Opposition NO-GO at `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-010.md`.

The version-010 verdict independently confirmed that the version-009 technical dependency-ordering plan is sound: a two-file cleanup breaks importer contracts in `scripts/bridge_work_intent_registry.py` and `scripts/bridge_applicability_preflight.py`, so the correct executable target surface is four files. The only blocking defect was owner-authorization evidence. Version 009 cited `DELIB-202666317`, which named only two files.

Prime Builder has now captured explicit owner approval for all four files as `DELIB-20260716-WI5307-FOUR-FILE-SCOPE-AUTHORIZATION`, updated `TEST-11450` to describe the four-file scope, created `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V4-20260716`, and revoked the superseded V3 PAUTH. The technical implementation plan remains the dependency-ordered plan LO already confirmed; this revision changes the authorization chain and test wording only.

## Requirement Sufficiency

Existing requirements sufficient.

`WI-5307`, `TEST-11450` version 2, `DELIB-20260716-WI5307-FOUR-FILE-SCOPE-AUTHORIZATION`, `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V4-20260716`, and the technical confirmation in `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-010.md` define the successor boundary. No new requirement or spec is needed before LO reviews this corrected proposal.

## Findings Addressed

### F1 (P1, blocking) - V3 authorization scope exceeds the cited owner decision

Response: corrected.

- Owner decision: `DELIB-20260716-WI5307-FOUR-FILE-SCOPE-AUTHORIZATION` records the exact owner message approving the four-file WI-5307 scope:
  - `.claude/hooks/bridge-compliance-gate.py`
  - `scripts/implementation_authorization.py`
  - `scripts/bridge_work_intent_registry.py`
  - `scripts/bridge_applicability_preflight.py`
- Project authorization: `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V4-20260716` is active and cites the new four-file owner decision.
- Supersession cleanup: `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V3-20260716` is revoked because it cited the earlier two-file decision.
- Test wording: `TEST-11450` version 2 now expects the four scoped shared-enforcement files to match committed HEAD or have independently VERIFIED owning bridge evidence before WI-5268 protected mutation starts.

No PAUTH vocabulary, dependency-ordering, target-path, or technical implementation-plan change is introduced beyond the evidence correction requested by version 010.

## Work-Intent Claim Note

Prime Builder attempted the canonical generic pre-drafting claim:

`python scripts\bridge_claim_cli.py claim gtkb-wi5307-shared-enforcement-baseline-disposition --ttl-seconds 3600`

Observed result:

`ERROR: Project authorization denied work_intent_acquire: Project authorization PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V2-20260716 is not active`

Root-cause observation: the current work-intent resolver treats a latest `NO-GO` thread with any prior `GO` as a `go_implementation` claim and validates the older approved proposal's PAUTH. For this thread that older approved proposal is version 005/006, which cites the now-revoked V2 PAUTH. That is not the desired behavior for a Prime-authored `REVISED` proposal after latest `NO-GO`; it should be a non-implementation drafting claim.

Because the bridge writer and compliance gate require an active same-session holder, and the public CLI does not expose an explicit draft-claim override, Prime Builder acquired the only available non-implementation latest-`NO-GO` claim path:

`python scripts\bridge_claim_cli.py claim-no-action gtkb-wi5307-shared-enforcement-baseline-disposition --ttl-seconds 3600`

Observed holder:

- rowid: `31575`
- session_id: `019f6668-9974-7d72-a456-826f9a67e627`
- claim_kind: `no_action_correction`
- acting_role: `prime-builder`
- implementation_deadline: null
- implementation_grace_expires_at: null

This claim is used only as non-implementation same-session holder evidence for this `REVISED` bridge write. It does not file `NO-ACTION`, does not authorize implementation, and does not replace the required future LO `GO` plus implementation-start packet. The claim-kind mismatch is disclosed here so Loyal Opposition can assess whether it is acceptable as a bridge-tooling workaround or should itself become a separate correction item.

## Owner Decisions / Input

- `DELIB-20260716-WI5307-FOUR-FILE-SCOPE-AUTHORIZATION` records the owner approval for this exact four-file scope.
- Owner quote captured in that deliberation: `APPROVE WI5307 FOUR-FILE SCOPE: .claude/hooks/bridge-compliance-gate.py, scripts/implementation_authorization.py, scripts/bridge_work_intent_registry.py, scripts/bridge_applicability_preflight.py`.
- This revision remains bounded to WI-5307 baseline disposition. Actual source or hook mutation still requires independent LO `GO`, a valid implementation claim, and an implementation-start packet.

## Prior Deliberations

- `DELIB-20260716-WI5307-FOUR-FILE-SCOPE-AUTHORIZATION` - owner approval for the four-file WI-5307 baseline-disposition scope.
- `DELIB-202666317` - earlier owner approval for the original two-file WI-5307 baseline disposition; superseded for four-file scope purposes by the new decision above.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-001.md` through `-010.md` - complete WI-5307 proposal, GO, NO-ACTION, corrected NO-GO, V2 proposal, V2 GO, implementation fail-closed NO-ACTION, dependency-ordering NO-GO, V3 proposal, and owner-authorization-scope NO-GO chain.
- `bridge/gtkb-wi5178-governed-predecessor-closure-004.md` - latest NO-GO for operation-time predecessor closure; nonterminal owner evidence for retained authorization-script behavior.
- `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-008.md` - latest VERIFIED stand-down only, with no source mutation.
- `bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md` - terminal VERIFIED owner for retained project-authorization bootstrap lifecycle behavior in the shared authorization script.
- `TEST-11450` version 2 - linked WI-5307 verification obligation with corrected four-file expected outcome.

## Scope Changes From Version 009

Changed evidence only:

- Replaced V3 PAUTH citation with `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V4-20260716`.
- Replaced the insufficient two-file owner-decision evidence with `DELIB-20260716-WI5307-FOUR-FILE-SCOPE-AUTHORIZATION`.
- Updated `TEST-11450` expected outcome from two-file wording to four-file wording.
- Revoked the superseded V3 PAUTH.

Unchanged technical target surface from version 009:

- `.claude/hooks/bridge-compliance-gate.py`
- `scripts/implementation_authorization.py`
- `scripts/bridge_work_intent_registry.py`
- `scripts/bridge_applicability_preflight.py`

Explicitly excluded: `scripts/implementation_start_gate.py`, because it is clean relative to committed HEAD and is not required for the dependency correction identified in version 008 and confirmed in version 010.

## Cross-Harness Disposition

This proposal includes `.claude/hooks/bridge-compliance-gate.py`, a harness-surface file, because it was part of the original WI-5307 clean-baseline target. The intended disposition remains baseline preservation, not a new harness behavior rollout.

| Harness / surface | Disposition |
| --- | --- |
| Claude Code / `.claude/hooks/bridge-compliance-gate.py` | Keep clean relative to committed HEAD unless a terminal owning bridge artifact is discovered before implementation. No new Claude-only hook behavior is proposed. |
| Codex / `.codex/hooks.json`, `.codex/gtkb-hooks/**`, `.codex/skills/**` | No target mutation. Existing Codex parity surfaces remain unchanged. |
| Cursor, Antigravity, Ollama, OpenRouter, provider headless workers | No target mutation. This baseline-disposition slice does not add or remove provider harness behavior. |

If implementation discovers a required harness-behavior change rather than a baseline cleanup, Prime Builder will stop and file a separate proposal with explicit parity scope instead of expanding this WI-5307 cleanup in place.

## Implementation Plan

After LO `GO`, Prime Builder will acquire a fresh implementation claim and run `scripts/implementation_authorization.py begin` for this bridge thread. The implementation will:

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
| `TEST-11450` version 2, `GOV-WORK-TREE-HYGIENE-001` | `git status --short -- .claude/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py scripts/bridge_work_intent_registry.py scripts/bridge_applicability_preflight.py scripts/implementation_start_gate.py` | Only terminal-owned retained deltas remain; clean files are clean; `scripts/implementation_start_gate.py` remains clean. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Import and focused regression checks for `scripts/implementation_authorization.py`, `scripts/bridge_work_intent_registry.py`, and `scripts/bridge_applicability_preflight.py` | Importer contracts do not call missing entry points; any retained entry point has terminal owning evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | `python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short --timeout=300` | Focused PAUTH, implementation-start, work-intent, and applicability-preflight tests pass. |
| Bridge proposal governance specs | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5307-shared-enforcement-baseline-disposition-011.md --json` | `preflight_passed: true`, `missing_required_specs: []`, `blocking_errors: []`. |
| ADR/DCL clause gate | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5307-shared-enforcement-baseline-disposition-011.md` | Exit code 0; no blocking gaps. |
| Python quality gates | `python -m ruff check scripts/implementation_authorization.py scripts/bridge_work_intent_registry.py scripts/bridge_applicability_preflight.py` and `python -m ruff format --check scripts/implementation_authorization.py scripts/bridge_work_intent_registry.py scripts/bridge_applicability_preflight.py` | Lint and format pass on changed Python targets. |

## Pre-Filing Preflight Subsection

Prime Builder runs the candidate-content applicability preflight and ADR/DCL clause preflight against this completed draft before live filing.

Applicability preflight:

- command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5307-shared-enforcement-baseline-disposition-011.md --json`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

Clause preflight:

- command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5307-shared-enforcement-baseline-disposition-011.md`
- clauses evaluated: 5
- must_apply: 3
- may_apply: 2
- not_applicable: 0
- evidence gaps in must_apply clauses: 0
- blocking gaps: 0
- exit code: 0

Loyal Opposition should rerun both mandatory checks against the operative bridge file before GO.

## Acceptance Criteria

- The live bridge proposal cites `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V4-20260716` and the four exact target paths.
- The active V4 PAUTH cites `DELIB-20260716-WI5307-FOUR-FILE-SCOPE-AUTHORIZATION`.
- The superseded V3 PAUTH is revoked.
- `TEST-11450` version 2 describes the four-file expected outcome.
- LO can issue GO without re-looping into the version-010 owner-authorization-scope defect or the earlier two-file importer dependency failure.
- After implementation, `TEST-11450` can be evaluated without hidden nonterminal importer dependencies.

## Risk And Rollback

Risk: clearing nonterminal shared authorization behavior may expose tests or callers that were accidentally relying on unverified behavior. Mitigation: the expanded target surface lets the implementation adjust importers and entry points together instead of leaving missing symbols.

Risk: the disclosed claim-kind workaround may itself be judged unacceptable by LO. Mitigation: it is non-implementation coordination evidence only, is disclosed in this proposal, and leaves the bridge thread non-implemented until LO records a valid GO.

Rollback: before implementation, rollback is to leave this REVISED proposal unapproved. After implementation, rollback is a normal scoped revert of the approved four target files plus any filed implementation report, with the bridge thread remaining non-terminal until LO accepts the corrected state.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
