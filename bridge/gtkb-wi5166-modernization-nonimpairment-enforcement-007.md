REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6d5c-2017-7d43-902e-b74483f50fff
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop Prime Builder execution worker; user-bounded bridge-only NO-GO revisions

# Revised Implementation Proposal - WI-5166 First Non-Impairment Enforcement Slice

bridge_kind: prime_proposal
Document: gtkb-wi5166-modernization-nonimpairment-enforcement
Version: 007
Responds to: bridge/gtkb-wi5166-modernization-nonimpairment-enforcement-006.md
Revises: bridge/gtkb-wi5166-modernization-nonimpairment-enforcement-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5166
target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "scripts/check_modernization_nonimpairment.py", "platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py", "platform_tests/scripts/test_modernization_nonimpairment.py"]

## Dependency Closure And Fresh GO Request

Prime Builder accepts version 006's dependency ordering. The sole operational
blocker is now closed: `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-008.md`
is latest `VERIFIED`, MemBase records `WI-5254` resolved, and that verdict
confirms the version 007 stand-down explicitly withdrew WI-5254's active shared
dirty-path claim over `.claude/hooks/bridge-compliance-gate.py`.

No substantive implementation-plan change is requested or implied. This
revision re-requests independent review of the unchanged bounded version 003
proposal and preserves the exact five targets, named-hunk attribution,
foreign-hunk exclusions, first-slice non-completion boundary, specifications,
and verification matrix. A fresh GO, claim, and successful implementation-start
packet remain mandatory; any remaining peer-report collision or ownership
ambiguity fails closed.

## Revision Claim

This is the first bounded WI-5166 enforcement slice, not completion of WI-5166. It adds the structured proposal-disposition gate, a deterministic report-only activation-evidence evaluator, and focused tests while preserving the exact IP-1 through IP-4 implementation and mixed-hunk boundaries from version 001. A VERIFIED outcome for this slice must not resolve, close, or otherwise represent completion of WI-5166.

## Requirement Sufficiency

Existing requirements are sufficient for this first slice. They do not establish that this slice completes the work item. The remaining closure-gate, thirteen-suite orchestration, and separately owned worker-loading enforcement remain explicit below.

## In-Root Placement Evidence

All five targets are in `E:\GT-KB`; no external or adopter-application path is introduced.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-NONIMPAIRMENT-GOV-FORMALIZATION-RESULT`
- `DELIB-202666274`
- `DELIB-202666217`
- `DELIB-202666232`
- `DELIB-202665664`
- `DELIB-20265396`

## Owner Decisions / Input

No new owner decision is required. Existing project authorization covers this bounded slice but does not authorize a false completion claim.

## Findings Addressed

### [P1] Completion over-claim

Accepted. Every completion statement is replaced with first-slice language. The scope below identifies all known remaining WI-5166 obligations, and acceptance now expressly prohibits this slice's VERIFIED verdict from closing the work item.

## Proposed Scope

### IP-1 - Deterministic report-only evaluator

Adopt `scripts/check_modernization_nonimpairment.py` as a deterministic, non-activating evaluator that reads governed evidence and reports baseline/result/rollback/hard-invariant gaps.

### IP-2 - Structured proposal gate

Adopt only the three named `NONIMPAIRMENT_*` semantic hunks in each active/template hook: constants, concrete-value/disposition helpers, and the conditioned denial branch. Keep both copies byte-identical. Exclude every foreign applicability-preflight hunk and prohibit whole-file staging.

### IP-3 - Focused regressions and formatting

Adopt the two focused test modules, correct their bounded Ruff findings, and format only owned content while preserving foreign bytes and line endings.

### IP-4 - Exact evidence and finalization boundary

Record exact hashes, semantic patches, focused pytest/Ruff results, hook equality, and an owned-hunk manifest. Any later finalizer must apply only the exact owned patch after independent VERIFIED and separate mechanical authority.

## Remaining WI-5166 Scope (Out Of This Slice)

1. Wire the evaluator into verification and closure so missing hard-invariant evidence mechanically blocks both gates under GOV MUST (c).
2. Implement the thirteen-suite hard-invariant orchestrator spanning bridge, dispatcher, role, project, backlog, Git, skill, CLI, startup, activity, assertion, doctor, and governance regressions.
3. Complete superseded-worker-loading enforcement under GOV MUST (d), separately owned by WI-5154, then integrate its evidence into WI-5166 closure.
4. Only after those obligations are independently verified may WI-5166 itself be considered for resolution.

## Cross-Harness Disposition

All supported harnesses continue through the shared governed bridge filing path; the active Claude hook and packaged adopter hook remain byte-identical. The evaluator is report-only and cannot change routing, eligibility, dispatcher, harness, Git, database, or external state. Missing/malformed dispositions fail closed only for implementation proposals citing the governing non-impairment specification.

| Harness | Disposition | Rationale |
| --- | --- | --- |
| Claude Code | behavioral parity | The active `.claude/hooks/bridge-compliance-gate.py` receives the owned checks. |
| Codex | behavioral parity | Codex governed filing invokes the shared compliance path; no duplicate hook is needed. |
| Cursor | behavioral parity | Cursor-authored proposals use the shared bridge filing path. |
| Antigravity | behavioral parity | Antigravity-authored proposals use the shared bridge filing path. |
| Ollama | behavioral parity | Headless work remains bound to shared bridge artifacts and validation. |
| OpenRouter | behavioral parity | Provider-backed work remains bound to shared bridge artifacts and validation. |
| Alibaba | behavioral parity | Provider-backed work remains bound to shared bridge artifacts and validation. |
| Packaged adopters | behavioral parity | The packaged hook changes in lockstep and must remain byte-identical. |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5166 and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "canonical_authority": "The governed specification and project PAUTH remain authoritative; this first slice is enforcement evidence, not WI closure.",
  "primary_route": "Authors use the governed proposal scaffold and bridge filing CLI; the shared gate validates structured evidence.",
  "before_behavior": "Applicable modernization proposals could omit or partially populate non-impairment evidence.",
  "after_behavior": "Applicable proposals carry concrete structured evidence; incomplete evidence fails closed while remaining WI-5166 obligations stay open.",
  "self_descriptive_naming": "The disposition heading and field names state their enforcement purpose.",
  "obsolete_guidance_disposition": "Prose-only or partial disposition guidance is superseded by the structured contract.",
  "history_preservation": "Prior bridge history and foreign hook hunks remain unchanged; only exact owned hunks are eligible for later finalization.",
  "baseline": "Exact target hashes and excluded foreign hook hunks are recorded before protected implementation.",
  "expected_result": "Focused tests pass, active/template hooks match, and this slice remains explicitly non-closing for WI-5166.",
  "rollback": "Revert only the three owned hook hunks and three new files through separately governed exact mechanics.",
  "hard_invariants": [
    "no bridge bypass",
    "no foreign-hunk absorption",
    "no activation or routing mutation",
    "WI-5166 remains open after this slice",
    "independent VERIFIED before slice completion"
  ],
  "fail_closed_conditions": [
    "missing or malformed disposition",
    "placeholder values",
    "active/template mismatch",
    "baseline hash drift",
    "foreign hunk selected",
    "attempt to close WI-5166 from this slice"
  ],
  "essential_context_preservation": "Project, work-item, specification, deliberation, target-byte, foreign-ownership, and remaining-scope evidence remain explicit."
}
```

## Pre-Filing Preflight Subsection

- Preliminary completed-content applicability passed with no missing specs or blocking errors.
- Preliminary mandatory clause gate exited 0 with 4 must-apply clauses satisfied and 0 blocking gaps.
- The governed revision helper must rerun both gates against the final bytes before filing.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| Structured disposition | Run `platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py`; valid evidence passes and absent/malformed/duplicate/placeholder cases fail deterministically. |
| Report-only evidence evaluator | Run `platform_tests/scripts/test_modernization_nonimpairment.py`; complete evidence passes and missing/impaired invariants fail without mutation. |
| Active/template parity | Compare exact SHA-256 of both hook copies after applying only named hunks. |
| Mixed ownership | Inspect exact semantic and finalizer patches; no applicability-preflight hunk may be selected. |
| Python quality | Ruff lint and format-check all five targets. |
| Remaining-scope integrity | Implementation report and verdict must state that WI-5166 remains open and cannot be closed by this slice. |

## Acceptance Criteria

- IP-1 through IP-4 and the original five targets remain unchanged in technical scope.
- Structured non-impairment evidence is mechanically checked at proposal filing.
- The evaluator remains deterministic and report-only.
- Active/template hooks are byte-identical and foreign hunks remain excluded.
- Focused pytest and Ruff gates pass.
- A VERIFIED verdict closes only this first slice; it must not resolve or represent completion of WI-5166.
- Remaining closure wiring, thirteen-suite orchestration, and WI-5154 worker-loading evidence remain tracked prerequisites to WI-5166 completion.

## Risk And Rollback

The primary risks are foreign-hunk capture and later misuse of this slice's verdict as work-item closure. Exact patch boundaries and the explicit non-closure criterion fail closed on both. Rollback reverts only owned hook hunks and the three new files; bridge history remains append-only.

## Recommended Commit Type

`feat`
