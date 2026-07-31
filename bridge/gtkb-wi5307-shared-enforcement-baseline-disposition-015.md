REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; owner goal to close black-box bridge, TAFE, and harness complex program
author_metadata_source: explicit_interactive_session_metadata

# REVISED Implementation Proposal - WI-5307 V5 Authorization Envelope Correction

bridge_kind: prime_proposal
Document: gtkb-wi5307-shared-enforcement-baseline-disposition
Version: 015
Responds to: bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-014.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V5-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5307

target_paths: [".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", "scripts/bridge_work_intent_registry.py", "scripts/bridge_applicability_preflight.py"]

implementation_scope: source_and_configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision addresses the latest Loyal Opposition NO-GO at `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-014.md`.

Version 014 concurred with the Prime Builder `NO-ACTION` at version 013: the V4 project authorization cited the correct four owner-approved target paths, but its machine-enforced mutation-class envelope omitted `configuration`, and `.claude/hooks/bridge-compliance-gate.py` is classified as `configuration`. Version 014 also found that version 013 lacked the mandatory specification-derived verification mapping for `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

Prime Builder has now created `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V5-20260716`, which retains the exact four owner-approved target paths and permits both registered target classes required by those paths:

- `configuration` for `.claude/hooks/bridge-compliance-gate.py`
- `source` for `scripts/implementation_authorization.py`, `scripts/bridge_work_intent_registry.py`, and `scripts/bridge_applicability_preflight.py`

The superseded V4 PAUTH has been revoked. The technical implementation plan remains the dependency-ordered plan already confirmed by versions 010 and 012.

## Requirement Sufficiency

Existing requirements sufficient.

`WI-5307`, `TEST-11450` version 2, `DELIB-20260716-WI5307-FOUR-FILE-SCOPE-AUTHORIZATION`, `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V5-20260716`, and the version-014 NO-GO define the successor boundary. No new target-scope owner decision is needed because V5 does not add files or operations; it corrects the registered mutation-class envelope for the already approved hook target.

## Findings Addressed

### F1 (P1, blocking) - Clause Preflight Failure (missing spec-to-test mapping)

Response: corrected in this `REVISED` proposal.

This proposal includes a dedicated `Specification-Derived Verification Plan` mapping every relevant verification obligation to executable commands or evidence, including `TEST-11450` version 2, the PAUTH envelope, the dependency-ordering contract, Python focused tests, and Python lint/format gates. Prime Builder will also file a post-implementation report carrying forward the linked specifications, exact command results, and observed outcomes before requesting `VERIFIED`.

### F2 (P0, blocking) - Insufficient Project Authorization Class Coverage

Response: corrected by V5 PAUTH.

- Active successor PAUTH: `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V5-20260716`
- Owner decision: `DELIB-20260716-WI5307-FOUR-FILE-SCOPE-AUTHORIZATION`
- Allowed mutation classes include: `bridge`, `metadata`, `governance_evidence`, `source`, `configuration`, `test`
- Target surface remains exactly:
  - `.claude/hooks/bridge-compliance-gate.py`
  - `scripts/implementation_authorization.py`
  - `scripts/bridge_work_intent_registry.py`
  - `scripts/bridge_applicability_preflight.py`
- Superseded PAUTH: `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V4-20260716`, revoked after V5 creation.

## Work-Intent Claim Note

Prime Builder attempted the canonical generic pre-drafting claim after version 014:

`python scripts\bridge_claim_cli.py claim gtkb-wi5307-shared-enforcement-baseline-disposition --ttl-seconds 3600`

Observed result:

`ERROR: Project authorization denied work_intent_acquire: Project authorization PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V4-20260716 is not active`

This reproduces the already-disclosed latest-`NO-GO` claim-state defect: normal drafting after latest `NO-GO` is still being treated as implementation against the older GO-approved proposal, which cited V4. The public CLI still lacks an explicit draft-claim override. Prime Builder therefore acquired the only public non-implementation latest-`NO-GO` claim path for this bridge write:

`python scripts\bridge_claim_cli.py claim-no-action gtkb-wi5307-shared-enforcement-baseline-disposition --ttl-seconds 3600`

Observed holder:

- rowid: `31589`
- session_id: `019f6668-9974-7d72-a456-826f9a67e627`
- claim_kind: `no_action_correction`
- acting_role: `prime-builder`
- implementation_deadline: null
- implementation_grace_expires_at: null

This holder is non-implementation coordination evidence only. It does not file `NO-ACTION`, does not authorize implementation, and does not replace the required future LO `GO`, implementation claim, and implementation-start packet. The claim-state defect is separately tracked by `PAUTH-DISPATCHER-BLACK-BOX-WI5337-LATEST-NO-GO-CLAIM-STATE-20260716` and is not implemented under WI-5307.

## Owner Decisions / Input

- `DELIB-20260716-WI5307-FOUR-FILE-SCOPE-AUTHORIZATION` records the owner approval for this exact four-file scope.
- Owner quote captured in that deliberation: `APPROVE WI5307 FOUR-FILE SCOPE: .claude/hooks/bridge-compliance-gate.py, scripts/implementation_authorization.py, scripts/bridge_work_intent_registry.py, scripts/bridge_applicability_preflight.py`.
- V5 adds no target path and no implementation operation beyond that decision. It only permits the registered `configuration` class required for the already approved hook target.

## Prior Deliberations

- `DELIB-20260716-WI5307-FOUR-FILE-SCOPE-AUTHORIZATION` - owner approval for the four-file WI-5307 baseline-disposition scope.
- `DELIB-202666317` - earlier owner approval for the original two-file WI-5307 baseline disposition; superseded for four-file scope purposes by the new decision above.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-001.md` through `-014.md` - complete WI-5307 proposal, GO, NO-ACTION, corrected NO-GO, V2 proposal, V2 GO, implementation fail-closed NO-ACTION, dependency-ordering NO-GO, V3/V4 revisions, GO, PAUTH class NO-ACTION, and version-014 NO-GO chain.
- `bridge/gtkb-wi5178-governed-predecessor-closure-004.md` - latest NO-GO for operation-time predecessor closure; nonterminal owner evidence for retained authorization-script behavior.
- `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-008.md` - latest VERIFIED stand-down only, with no source mutation.
- `bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md` - terminal VERIFIED owner for retained project-authorization bootstrap lifecycle behavior in the shared authorization script.
- `TEST-11450` version 2 - linked WI-5307 verification obligation with corrected four-file expected outcome.

## Scope Changes From Version 011

Changed authorization envelope only:

- Replaced V4 PAUTH citation with `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V5-20260716`.
- Added registered `configuration` mutation class to the PAUTH envelope for `.claude/hooks/bridge-compliance-gate.py`.
- Added `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` to the proposal/spec surface.
- Strengthened the specification-derived verification mapping in this proposal to address the version-014 clause-preflight finding.
- Revoked superseded V4 PAUTH.

Unchanged target surface:

- `.claude/hooks/bridge-compliance-gate.py`
- `scripts/implementation_authorization.py`
- `scripts/bridge_work_intent_registry.py`
- `scripts/bridge_applicability_preflight.py`

Explicitly excluded: `scripts/implementation_start_gate.py`, because it is clean relative to committed HEAD and is not required for the dependency correction identified in version 008 and confirmed in versions 010 and 012.

## Cross-Harness Disposition

This proposal includes `.claude/hooks/bridge-compliance-gate.py`, a harness-surface file, because it was part of the original WI-5307 clean-baseline target and is classified as `configuration` by the PAUTH evaluator. The intended disposition remains baseline preservation, not a new harness behavior rollout.

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
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
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
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `gt projects authorizations PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING --json` and implementation-claim/start packet after LO GO | V5 PAUTH is active; V4 is revoked; allowed mutation classes include `configuration` and `source`; implementation claim and start packet no longer fail on the hook target class. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Import and focused regression checks for `scripts/implementation_authorization.py`, `scripts/bridge_work_intent_registry.py`, and `scripts/bridge_applicability_preflight.py` | Importer contracts do not call missing entry points; any retained entry point has terminal owning evidence. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | `python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short --timeout=300` | Focused PAUTH, implementation-start, work-intent, and applicability-preflight tests pass. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5307-shared-enforcement-baseline-disposition-015.md --json` | `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, `blocking_errors: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5307-shared-enforcement-baseline-disposition-015.md` | Exit code 0; no must-apply evidence gap for spec-to-test mapping. |
| Python quality gates | `python -m ruff check scripts/implementation_authorization.py scripts/bridge_work_intent_registry.py scripts/bridge_applicability_preflight.py` and `python -m ruff format --check scripts/implementation_authorization.py scripts/bridge_work_intent_registry.py scripts/bridge_applicability_preflight.py` | Lint and format pass on changed Python targets. |

## Pre-Filing Preflight Subsection

Prime Builder runs the candidate-content applicability preflight and ADR/DCL clause preflight against this completed draft before live filing.

Applicability preflight:

- command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5307-shared-enforcement-baseline-disposition-015.md --json`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

Clause preflight:

- command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5307-shared-enforcement-baseline-disposition --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5307-shared-enforcement-baseline-disposition-015.md`
- clauses evaluated: 5
- must_apply: 3
- may_apply: 2
- not_applicable: 0
- evidence gaps in must_apply clauses: 0
- blocking gaps: 0
- exit code: 0

Loyal Opposition should rerun both mandatory checks against the operative bridge file before GO.

## Acceptance Criteria

- The live bridge proposal cites `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-V5-20260716` and the four exact target paths.
- The active V5 PAUTH cites `DELIB-20260716-WI5307-FOUR-FILE-SCOPE-AUTHORIZATION`.
- The active V5 PAUTH allows `configuration` and `source`.
- The superseded V4 PAUTH is revoked.
- The live proposal includes a spec-to-test mapping sufficient for `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.
- LO can issue GO without re-looping into the V4 PAUTH class denial or version-014 clause-preflight finding.
- After implementation, `TEST-11450` can be evaluated without hidden nonterminal importer dependencies.

## Risk And Rollback

Risk: adding `configuration` to the PAUTH envelope may look broader than the intended source cleanup. Mitigation: the target path list remains exact and four-file only; `configuration` is required solely because the already owner-approved hook target is classified as that registered mutation class.

Risk: clearing nonterminal shared authorization behavior may expose tests or callers that were accidentally relying on unverified behavior. Mitigation: the expanded target surface lets the implementation adjust importers and entry points together instead of leaving missing symbols.

Rollback: before implementation, rollback is to leave this REVISED proposal unapproved. After implementation, rollback is a normal scoped revert of the approved four target files plus any filed implementation report, with the bridge thread remaining non-terminal until LO accepts the corrected state.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
