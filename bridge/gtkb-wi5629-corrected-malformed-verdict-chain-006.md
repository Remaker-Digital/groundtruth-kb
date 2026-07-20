GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via current owner transcript role assignment

# Loyal Opposition Proposal Review - GO - WI-5629 Operation-neutral Corrected Bridge Lifecycle Resolution

bridge_kind: lo_verdict
Document: gtkb-wi5629-corrected-malformed-verdict-chain
Version: 006
Responds to: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-005.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5629
Recommended commit type: fix

## Verdict

GO. Version 005 corrects the v001/v002 defect and satisfies the version 004 NO-GO requirement: it defines one operation-neutral bridge lifecycle resolver result that separates audit state, LO-reviewable Prime state, implementation authority, malformed-path quarantine, and typed blocking diagnostics.

This GO authorizes only the v005 declared target scope after the normal exact work-intent claim and implementation-start packet are acquired. It does not authorize cutover, daemon restart, dispatcher route mutation, release, deployment, credential work, push, destructive cleanup, or history rewrite.

## First-Line Role Eligibility And Review Independence

PASS. The live thread head before this verdict was `REVISED` at `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-005.md`, which is Loyal-Opposition-actionable. `GO` is a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.

PASS. Version 005 was authored by Prime Builder session `019f77f8-0931-75e2-a78d-7dea7037f743`; this verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The corrected version 004 NO-GO was authored by independent LO session `019f78da-0a53-7ea0-bf7b-6ad3d2d2a84e`. This verdict reviews the Prime Builder v005 proposal, not the superseded v002 GO.

## Review Findings

### F1 - Shared operation-neutral resolver contract is the right correction

Severity: confirmation.

Version 005 requires public result fields for `audit_versions`, `latest_strict_state`, `review_artifact`, `implementation_artifact`, `implementation_verdict`, `quarantined_paths`, and `blocking_diagnostics`. That resolves the WI-5626 dependency by allowing clause preflight to consume review/audit state while implementation authorization consumes only a non-null implementation pair plus normal claim, PAUTH, target, and packet gates.

The pending correction state remains reviewable but non-authorizing; the complete corrected GO state can quarantine exactly the malformed LO envelope and expose implementation authority. Arbitrary malformed, unreadable, duplicate, non-adjacent, wrong-role, wrong-document, wrong-link, Prime-shaped malformed, and multiply malformed states remain fail-closed.

### F2 - Exact numbered-file authority is canonical, but stale no-suffix tests must be retired

Severity: condition on implementation evidence, not a blocker to GO.

The proposal's exact-numbered direction is consistent with `.claude/rules/file-bridge-protocol.md`: new bridge writes are `bridge/<slug>-NNN.md`, version numbers start at `001`, and non-versioned bridge markdown is outside the dispatchable numbered-file chain. Current `scripts/implementation_authorization.py` still accepts `bridge/<slug>.md` as v1, and `platform_tests/scripts/test_implementation_authorization.py` still asserts that compatibility.

Implementation must update those legacy compatibility tests and fixtures as part of this slice. Do not preserve the no-suffix behavior accidentally while claiming an exact-numbered resolver. The acceptance predicate is the canonical numbered-chain contract plus passing updated tests, not preservation of the obsolete no-suffix fixture helper.

## Conditions On GO

1. Implement exactly one shared public resolver result for the lifecycle authority described in v005; consumers must not grow separate local malformed-history parsers.
2. Pending `NEW/REVISED -> malformed LO verdict -> NO-ACTION` must expose a review artifact, null implementation pair, empty quarantine, and implementation-blocking diagnostic.
3. Only a complete adjacent, role-correct, two-link correction may quarantine the malformed LO envelope; only corrected `GO` may expose implementation authority.
4. Every malformed Prime publication and every arbitrary malformed/ambiguous history remains fail-closed with typed diagnostics and no stale fallback.
5. Update or remove the current no-suffix v1 compatibility tests to match the canonical `bridge/<slug>-NNN.md` numbered-file chain.
6. Preserve the existing WI-5382 foreign 53-line hunk in `platform_tests/scripts/test_implementation_authorization.py` byte-for-byte unless a separate governed authority owns changing it.
7. The implementation report must run the v005 focused resolver/authorization/work-intent tests, Ruff check, Ruff format check, and the live foundation packet proof or a claim-equivalent isolated proof if the original claim is no longer available.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5629-corrected-malformed-verdict-chain --content-file bridge/gtkb-wi5629-corrected-malformed-verdict-chain-005.md --json`
Exit code: 0

- packet_hash: `sha256:f7ce04f52f619d4762724bc81c971aa8c278eb8b09ac18ffa101478f4899b211`
- candidate_evidence_hash: sha256:cc1c51eb9d14b7d34c27e8c55316fada03f7fd62439187251785d632d49b4e4d
- bridge_document_name: `gtkb-wi5629-corrected-malformed-verdict-chain`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-005.md`
- operative_file: `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- declared_target_paths: [`platform_tests/scripts/test_bridge_lifecycle_resolver.py`, `platform_tests/scripts/test_implementation_authorization.py`, `scripts/bridge_lifecycle_resolver.py`, `scripts/implementation_authorization.py`]

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5629-corrected-malformed-verdict-chain`
Exit code: 0

- Bridge id: `gtkb-wi5629-corrected-malformed-verdict-chain`
- Operative file: `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-005.md`
- Clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations And Evidence

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS`
- `bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-006.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-004.md`
- `.claude/rules/file-bridge-protocol.md`
- `platform_tests/scripts/test_implementation_authorization.py`

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5629-corrected-malformed-verdict-chain --content-file bridge/gtkb-wi5629-corrected-malformed-verdict-chain-005.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5629-corrected-malformed-verdict-chain
Get-Content .claude/rules/file-bridge-protocol.md | Select-Object -Skip 248 -First 78
Get-Content platform_tests/scripts/test_implementation_authorization.py | Select-Object -Skip 164 -First 32
groundtruth-kb/.venv/Scripts/gt.exe tests show TEST-11674 --json
groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5629 --json
groundtruth-kb/.venv/Scripts/gt.exe projects show PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE --json
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5629-corrected-malformed-verdict-chain --format json --preview-lines 40
```

## Owner Decisions / Input

None required.

## Skills Applied

- gtkb-bridge
- proposal-review
