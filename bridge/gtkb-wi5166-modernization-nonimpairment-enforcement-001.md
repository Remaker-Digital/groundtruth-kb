NEW

# Implementation Proposal - Enforce modernization intuitiveness and non-impairment gates

bridge_kind: prime_proposal
Document: gtkb-wi5166-modernization-nonimpairment-enforcement
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex GPT-5 family
author_model_version: desktop-managed
author_model_configuration: Prime Builder, danger-full-access, approval-never

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5166

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "scripts/check_modernization_nonimpairment.py", "platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py", "platform_tests/scripts/test_modernization_nonimpairment.py"]

## Claim

Complete WI-5166 as a bounded, deterministic modernization non-impairment enforcement slice. The implementation adds one report-only evaluator, adds matching structured-disposition checks to the active and packaged bridge gates, and adds focused regression tests. The two tracked hook files contain concurrent foreign applicability-preflight changes; this proposal owns only the three non-impairment hunks named below and prohibits whole-file staging or finalization.

## Requirement Sufficiency

The requirement is sufficient for this slice. `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` defines the required structured disposition and fail-closed behavior, WI-5166 identifies deterministic enforcement as the outcome, and the project PAUTH authorizes source/test/bridge work while preserving independent GO, claim/start, VERIFIED, and mechanical finalization gates. No owner clarification is needed before independent review.

This proposal is filed as the next append-only numbered bridge file under `bridge/`; prior numbered bridge files are neither deleted nor rewritten.

## In-Root Placement Evidence

All five target paths are inside `E:\GT-KB`. The active gate remains under `.claude/hooks/`, the packaged adopter copy remains under `groundtruth-kb/templates/hooks/`, the evaluator remains under `scripts/`, and focused tests remain under `platform_tests/`.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires executable intuitiveness/non-impairment enforcement and concrete disposition evidence.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - requires cross-cutting modernization requirements to be checked mechanically rather than by prose convention alone.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO before protected implementation and independent VERIFIED before completion.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - binds the work to the active Assurance project PAUTH.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires the active PAUTH to remain valid at claim, start, and mutation time.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - limits mutation classes and preserves forbidden mechanical operations.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - requires the work item and project authorization to retain governing-spec linkage.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not replace proposal GO or matching claim/start evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the machine-readable project, PAUTH, and work-item headers above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires proposal scope and verification to derive from linked specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent review of specification-derived test evidence.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires deterministic, in-root, independently reproducible evidence.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - prevents this slice from absorbing concurrent foreign hook work.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires an explicit disposition for every supported harness when a harness surface changes.
- `ADR-CROSS-HARNESS-PARITY-001` - requires semantic parity without unnecessary duplicate implementation surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves the evaluator, tests, proposal, report, and verdict as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires the implementation report and independent VERIFIED transition before completion.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps proposal, implementation, evidence, and finalization traceable.

## Prior Deliberations

- `DELIB-202666274` - owner authorization for the complete modernization program at project scope, with bridge and independent-review gates preserved.
- `DELIB-202666217` - independent GO for the related WI-5163 report-only shadow-evaluation slice; establishes that report-only evaluators remain non-activating evidence.
- `DELIB-202666232` - independent GO for binary-aware hunk-patch finalization; relevant because the mixed hook files cannot be finalized whole.
- `DELIB-202665664` - evidence freshness and archival-boundary review; requires results to remain bound to exact source bytes.
- `DELIB-20265396` - prior VERIFIED bridge-compliance gate template parity decision; requires active/template behavior to remain identical.

## Owner Decisions / Input

- `DELIB-202666274` - the owner authorized all implementation work required for the modernization program at project scope; mechanical exceptions remain separately gated.
- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE` v3 - active project authorization for source, test, configuration, metadata, runtime-state, governance-evidence, and bridge work; Git commit/push/release/deploy and destructive cleanup remain forbidden.

## Proposed Scope

### IP-1 - Deterministic report-only evaluator

Adopt `scripts/check_modernization_nonimpairment.py` as the canonical deterministic evaluator for the frozen modernization non-impairment evidence. Preserve report-only behavior: it reads governed inputs, emits deterministic diagnostics, and performs no activation, routing, dispatcher, harness, Git, database, or external-system mutation.

### IP-2 - Structured proposal gate

Adopt exactly three semantic hunks in each hook copy:

1. the `NONIMPAIRMENT_*` constants immediately after `DISPOSITION_NONCONTENT_PREFIX_RE`;
2. `_nonimpairment_value_is_concrete` plus `_nonimpairment_disposition_gap` immediately after `_has_concrete_cross_harness_disposition_section`;
3. the `NONIMPAIRMENT_GOV_ID`-conditioned denial branch in `_deny_reason_for_content`.

The active and packaged hook copies must remain byte-identical after the bounded edit. The existing `_run_pending_applicability_preflight` `blocking_errors` change and the related `missing_required_specs` to `preflight` diagnostic change are explicitly foreign and excluded. No whole-file staging, replacement, or finalization of either hook is authorized by this proposal.

### IP-3 - Focused regressions and formatting

Adopt the two focused test modules. Correct the two assertion-order Ruff findings and format only the new evaluator/tests and the owned non-impairment hook hunks. Preserve all foreign bytes and line-ending state outside those hunks.

### IP-4 - Exact evidence and finalization boundary

The implementation report must record pre/post SHA-256 values, the semantic diff, focused pytest/Ruff results, active/template equality, and a patch manifest identifying only the owned hook hunks plus the three whole new files. Any later local commit requires independent VERIFIED and separate exact mechanical authority. A hunk-patch finalizer must start from `HEAD` and apply only the owned patch; broad `git add`, whole-file hook staging, staged-state reuse, push, deploy, release, and history rewrite are out of scope.

## Cross-Harness Disposition

| Harness | Disposition | Evidence / rationale |
|---|---|---|
| Claude Code | behavioral parity | The active `.claude/hooks/bridge-compliance-gate.py` receives the structured non-impairment check. |
| Codex | behavioral parity | The governed Codex non-bypass proposal writer invokes the same active gate in audit-only mode; no duplicate Codex hook is needed. |
| Cursor | behavioral parity | Cursor-authored governed proposals use the shared bridge filing and compliance path; no Cursor-specific implementation surface is introduced. |
| Antigravity | behavioral parity | Antigravity-authored governed proposals use the shared bridge filing and compliance path; no harness-local copy is required. |
| Ollama | behavioral parity | Headless proposal/review work remains bound to shared bridge artifacts and the shared compliance path; no model-specific implementation is required. |
| OpenRouter | behavioral parity | Headless proposal/review work remains bound to shared bridge artifacts and the shared compliance path; no provider-specific implementation is required. |
| Alibaba | behavioral parity | Headless proposal/review work remains bound to shared bridge artifacts and the shared compliance path; no provider-specific implementation is required. |
| Packaged adopters | behavioral parity | `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` is changed in lockstep and must remain byte-identical to the active hook. |

The change is policy-semantic, not provider-specific. Every applicable harness therefore receives the same behavior through the shared governed filing route or the byte-identical packaged hook, with no owner waiver required.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5166 and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "canonical_authority": "The governed specification and exact project PAUTH remain authoritative; the evaluator and hook are enforcement surfaces only.",
  "primary_route": "Authors use the governed proposal scaffold and bridge filing CLI; the gate validates the structured disposition during filing.",
  "before_behavior": "Cross-cutting modernization proposals could omit or partially populate non-impairment evidence and rely on reviewer discovery.",
  "after_behavior": "Applicable proposals carry one concrete structured disposition and incomplete or malformed evidence fails closed with an actionable diagnostic.",
  "self_descriptive_naming": "The Intuitiveness / Non-Impairment Disposition heading and field names state their purpose directly.",
  "obsolete_guidance_disposition": "No alternate route is introduced; prose-only or partial disposition guidance is superseded by the structured contract.",
  "history_preservation": "Existing proposals and verdict history remain unchanged; enforcement applies through governed filing and exact evidence bound to current bytes.",
  "baseline": "Current candidate bytes and the excluded foreign hook hunks are recorded by SHA-256 and semantic diff before implementation.",
  "expected_result": "Deterministic evaluator and proposal gate evidence pass focused tests while active/template parity and foreign bytes remain intact.",
  "rollback": "Revert only the three owned hook hunks and three added files through a separately governed exact patch; do not restore whole hook files.",
  "hard_invariants": ["no bridge bypass", "no foreign-hunk absorption", "no activation or routing mutation", "independent VERIFIED before completion"],
  "fail_closed_conditions": ["missing or malformed disposition", "placeholder values", "active/template mismatch", "baseline hash drift", "foreign hunk selected for finalization"],
  "essential_context_preservation": "Project/work-item/spec linkage, prior deliberations, exact target bytes, excluded foreign ownership, and verification commands remain in the proposal and report."
}
```

## Specification-Derived Verification Plan

| ID | Requirement | Verification | Passing evidence |
|---|---|---|---|
| SV-1 | Structured disposition parsing is deterministic and fail-closed. | `python -m pytest platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py -q --tb=short` | Valid payload passes; absent, malformed, duplicate, placeholder, and missing-field cases fail with stable diagnostics for both hook copies. |
| SV-2 | The report-only evaluator enforces frozen non-impairment evidence. | `python -m pytest platform_tests/scripts/test_modernization_nonimpairment.py -q --tb=short` | Complete evidence passes; missing or impaired invariants fail without mutation. |
| SV-3 | Active and packaged hooks remain identical. | SHA-256 both hook files after the bounded edit. | Hashes are equal. |
| SV-4 | Python quality gates pass. | `python -m ruff check` and `python -m ruff format --check` over the five target paths. | Both commands exit 0. |
| SV-5 | Foreign hook work is excluded. | Inspect the normalized semantic patch and finalizer patch manifest. | No `_run_pending_applicability_preflight` or `preflight=` diagnostic hunk is selected. |
| SV-6 | Completion is independently reproducible. | Independent LO reruns SV-1 through SV-5 from exact reported bytes. | VERIFIED names exact hashes, commands, outcomes, and hunk boundary. |

## Acceptance Criteria

- One concrete structured disposition is accepted; absent, malformed, duplicate, incomplete, or placeholder dispositions fail closed.
- The evaluator remains deterministic and report-only.
- The active and packaged hook copies are byte-identical.
- Focused pytest, Ruff check, and Ruff format check pass.
- Only the three named non-impairment hunks in each hook and the three new files are attributable to WI-5166.
- The foreign applicability-preflight hunks remain unstaged and uncommitted by this scope.
- Independent LO produces VERIFIED before the scope is treated as complete.
- Any finalizer uses exact hunk-patch mechanics and separate commit authority; no push, deployment, release, cleanup, or history rewrite occurs.

## Risks / Rollback

The primary risk is mixed ownership inside the two tracked hook files. Whole-file staging would absorb unrelated applicability-preflight work, so baseline drift or inability to select only the named hunks fails closed. A second risk is over-strict handling of historical proposals; the gate is conditioned on the governing modernization specification and tests preserve that boundary. Rollback is the inverse exact patch for only the owned hunks and three new files under a separately governed transaction.

## Current Candidate Evidence

- `.claude/hooks/bridge-compliance-gate.py`: SHA-256 `C30EA0A0C035AA75A9CEB56875EFEAC0A442E4D24680C6410B3E2268CE84AA87`, 100304 bytes.
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`: SHA-256 `C30EA0A0C035AA75A9CEB56875EFEAC0A442E4D24680C6410B3E2268CE84AA87`, 100304 bytes.
- `scripts/check_modernization_nonimpairment.py`: SHA-256 `6508147424EB25CACEAE361905CA13C120BB10FE343BC373E75CB70ACB27184C`, 5793 bytes.
- `platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py`: SHA-256 `999A22233F2C38E5E54A5E20976A287631CB270A4172E89F91D1F93531E55B2C`, 2945 bytes.
- `platform_tests/scripts/test_modernization_nonimpairment.py`: SHA-256 `3630EB3492B10B9F89E97EB56966C850DF40CBDB99AE079775A43F7D22B7F5B3`, 3337 bytes.
- Focused pytest: 16 passed in 0.23 seconds.
- Ruff check: two assertion-order findings in the focused hook test.
- Ruff format check: four files would be reformatted; implementation must bound formatting to owned content.

## Files Expected To Change

- `.claude/hooks/bridge-compliance-gate.py` - three named non-impairment hunks only.
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` - matching three named non-impairment hunks only.
- `scripts/check_modernization_nonimpairment.py` - whole new file.
- `platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py` - whole new file.
- `platform_tests/scripts/test_modernization_nonimpairment.py` - whole new file.

## Recommended Commit Type

`feat`
