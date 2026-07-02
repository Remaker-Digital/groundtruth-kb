NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-build-20260702-ops-dispatcher-modernization
author_model: GPT-5
author_model_version: 2026-07-02
author_model_configuration: Codex desktop; E:/GT-KB; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb; build envelope PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION

# Implementation Proposal - WI-4957 Hook Scope Amendment

bridge_kind: prime_proposal
Document: gtkb-ops-lifecycle-protocol-foundation-hook-scope-amendment
Version: 001
Date: 2026-07-02 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-LIFECYCLE-PROTOCOL-FOUNDATION-WI-4957
Project: PROJECT-GTKB-OPS-LIFECYCLE-PROTOCOL-FOUNDATION
Work Item: WI-4957

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py"]

implementation_scope: source+hook+tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Scope amendment for `WI-4957`: authorize the live and template bridge-compliance gate surfaces needed for `NO-ACTION` status-token recognition, plus focused hook regression coverage.

The approved foundation proposal `bridge/gtkb-ops-lifecycle-protocol-foundation-001.md` and GO verdict `bridge/gtkb-ops-lifecycle-protocol-foundation-002.md` make `NO-ACTION` a required implementation deliverable. The GO verdict also identifies an implementation-time blocker: `.claude/hooks/bridge-compliance-gate.py` must recognize `NO-ACTION`, but that hook path was omitted from the approved proposal's `target_paths`. This amendment closes only that authorization gap. It does not broaden runtime dispatcher behavior, implement production ranking, or change the broader `WI-4957` scope.

## Claim

Prime Builder proposes a narrow, dependency-enabling amendment for the `WI-4957` OPS lifecycle/protocol foundation. Without this amendment, the implementation cannot reach VERIFIED because the hook that validates bridge status tokens would still reject the new `NO-ACTION` token required by the OPS consolidation model.

## Requirement Sufficiency

Existing requirements sufficient.

The owner-approved OPS Dispatcher Modernization Wave 1 decisions and active `PAUTH-PROJECT-GTKB-OPS-LIFECYCLE-PROTOCOL-FOUNDATION-WI-4957` authorize bounded source, hook, and test work after Loyal Opposition GO. This amendment uses the same work item and project authorization, but narrows the target paths to the hook/token gap called out by Loyal Opposition.

## In-Root Placement Evidence

All target paths are inside `E:/GT-KB`:

- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py`

No Agent Red application source, external archive, deployment surface, or credential file is in scope.

## Architecture Alignment Ledger

| Alignment Axis | Evidence |
| --- | --- |
| OPS consolidation | Supports the consolidation decision that `NO-ACTION` is a first-class PB-authored bridge status. |
| Dispatcher daemon architecture | Keeps status-token validation in the bridge compliance gate and does not add harness-to-harness OPS messaging. |
| Lifecycle-first / scoring-last precedence | This is lifecycle/protocol enablement only; lane scoring and production ranking remain out of scope. |
| Portfolio reconciliation | The portfolio-control lane `gtkb-dispatcher-portfolio-reconciliation` is latest `NEW` at filing time, so this proposal limits itself to an already-identified blocker from the `WI-4957` GO verdict and leaves broader duplicate-project/stale-WI disposition to `WI-4960`. |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge status-token authority, role-correct bridge lifecycle, and numbered-file filing must remain intact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this amendment preserves the implementation blocker as a governed bridge artifact rather than an implicit workspace change.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this implementation proposal includes project authorization, project, work item, and target-path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites concrete governing specifications instead of placeholder links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map the `NO-ACTION` hook change to executed tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the proposal keeps the newly required `NO-ACTION` lifecycle state explicit and reviewable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is maintained across the GO finding, this amendment, the focused implementation report, and verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation files remain in the GT-KB platform root and out of Agent Red application source.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - status validation supports dispatcher-controlled bridge lifecycle decisions without adding harness-side target decisions.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher remains the control plane; this amendment only enables bridge token recognition required by that control plane.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex/Claude hook parity remains relevant because both live and template hook surfaces must recognize the same canonical token.
- `ADR-CROSS-HARNESS-PARITY-001` - harness-surface changes require behavioral parity analysis rather than assuming one harness-specific hook is isolated.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - proposals touching harness-surface paths must include a concrete cross-harness disposition.

## Prior Deliberations

- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` - owner selected actual governed project/work-item/bridge proposal creation for the OPS Dispatcher Modernization Wave 1 work.
- `DELIB-20260702-DISPATCH-OPS-WAVE1-CHILD-PROPOSALS-EMBED-FORMALIZATION` - Wave 1 child proposals embed the formalization required for implementation.
- `DELIB-HARNESS-OPS-NO-ACTION-FIRST-CLASS-BRIDGE-STATUS-20260702` - `NO-ACTION` is a first-class bridge status token.
- `DELIB-HARNESS-NO-ACTION-LO-ACTIONABLE-BRIDGE-ROUTING-20260702` - latest `NO-ACTION` routes to Loyal Opposition and is never Prime Builder implementation-dispatchable.
- `DELIB-HARNESS-NO-ACTION-PRIOR-GO-NONDISPATCHABLE-SUBSEQUENT-GO-FRESH-AUTHORITY-20260702` - `NO-ACTION` makes the prior GO non-dispatchable and requires fresh corrected GO authority.
- `bridge/gtkb-ops-lifecycle-protocol-foundation-002.md` - Loyal Opposition GO finding P2 explicitly identified the missing `NO-ACTION` bridge-compliance-gate registration as an implementation-time gate.

## Owner Decisions / Input

- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` - owner decision evidence for creating actual project, WI, and bridge proposals.
- `PAUTH-PROJECT-GTKB-OPS-LIFECYCLE-PROTOCOL-FOUNDATION-WI-4957` - active project authorization covering bounded `WI-4957` bridge, source, hook, and test work after GO.

## Proposed Scope

- Add `NO-ACTION` to the live bridge-compliance gate recognized status vocabulary.
- Add `NO-ACTION` to the scaffold/template bridge-compliance gate recognized status vocabulary so future installs match the live hook.
- Add focused hook tests proving `NO-ACTION` is accepted as a canonical first-line bridge status token without weakening existing gates for malformed bridge files, ADVISORY template shape, DEFERRED owner-parking shape, GO/VERIFIED preflight evidence, or VERIFIED commit-finalization evidence.

## Cross-Harness Disposition

- Codex harness A: in scope for the proposal-authoring path because Codex uses this bridge-compliance gate audit path as its non-bypass bridge writer. The implementation must preserve the same canonical status vocabulary when the hook is exercised from Codex.
- Claude Code harness B: in scope because `.claude/hooks/bridge-compliance-gate.py` is the live Claude hook surface. The implementation must add `NO-ACTION` to the live hook without changing unrelated status gates.
- Template/scaffolded GT-KB installs: in scope because `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` must match the live hook for future installs. Focused tests must prove live/template behavior remains identical for the canonical status vocabulary.
- Cursor, OpenRouter, Ollama, and Antigravity harnesses: no direct hook/config mutation is proposed. The shared bridge status vocabulary must remain compatible when these harnesses produce or review bridge files through existing dispatcher/bridge surfaces; no waiver is requested.

## Out Of Scope

- Implementing dispatcher runtime routing for `NO-ACTION`.
- Implementing corrected GO fresh-authority behavior.
- Implementing quarantine, circuit breaker, diagnostic context, service logs, or audit records.
- Editing `.claude/rules/file-bridge-protocol.md` or `.claude/rules/canonical-terminology.md`; those remain in the parent `WI-4957` implementation scope and still require formal-artifact approval packets before mutation.
- Production deployment, credential lifecycle changes, Agent Red application source mutation, or production lane-scoring activation.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Focused hook tests prove `NO-ACTION` is accepted as a canonical first-line bridge status token and that unrecognized tokens still fail closed. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The filed amendment and implementation report preserve the GO blocker, target paths, and evidence as durable artifacts. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge applicability preflight proves this amendment carries valid project authorization, project, work item, and `target_paths` metadata. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability and ADR/DCL preflights prove required proposal specification links are present. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps the hook/token changes to executed `platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py` tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The acceptance criteria cover `NO-ACTION` as a recognized bridge lifecycle status while preserving fail-closed behavior for unknown statuses. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The implementation report ties the hook amendment back to the GO finding, OPS consolidation decisions, and verification outputs. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target-path and preflight checks prove every mutation remains under `E:/GT-KB` and no Agent Red application source is changed. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Tests and review confirm the amendment only enables token recognition and does not move dispatch decisions into harness-side code. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | The implementation leaves dispatcher daemon control-plane architecture unchanged; no direct harness-to-harness OPS messaging is introduced. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Live and template hook tests/parity checks confirm both hook copies recognize the same `NO-ACTION` token. |
| `ADR-CROSS-HARNESS-PARITY-001` | The implementation report records the disposition above and confirms no harness-specific waiver is needed. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `platform_tests/scripts/test_bridge_compliance_gate_disposition.py` remains green, proving harness-surface proposals carry concrete disposition and live/template hook parity is preserved. |

Minimum commands expected after implementation:

```text
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py -q --tb=short
python -m pytest platform_tests/scripts/test_bridge_compliance_gate_disposition.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ops-lifecycle-protocol-foundation-hook-scope-amendment
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ops-lifecycle-protocol-foundation-hook-scope-amendment
```

## Acceptance Criteria

- `NO-ACTION` bridge files are not rejected solely because the first non-blank line is `NO-ACTION`.
- Live hook and template hook status vocabularies remain in parity for the new token.
- Existing canonical token tests for `NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, `ADVISORY`, `DEFERRED`, and `WITHDRAWN` continue to pass.
- Unknown status-token bridge files still fail closed.
- This amendment does not implement production dispatcher behavior beyond hook/token recognition.

## Risks / Rollback

Risk is low to moderate. The change touches a protected hook that gates bridge file writes, so a token-list mistake could either reject valid bridge files or admit malformed ones. Mitigation is a narrow implementation and focused tests around accepted and rejected first-line statuses.

Rollback is a normal source/test revert of the three target files plus a follow-on bridge report. Bridge files remain append-only audit artifacts and must not be deleted.

## Files Expected To Change

- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py`

## Recommended Commit Type

`fix`
