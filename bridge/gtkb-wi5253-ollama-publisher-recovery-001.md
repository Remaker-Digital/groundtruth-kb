NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: GPT-5
author_model_version: GPT-5 Codex desktop 2026-07-15
author_model_configuration: Codex desktop interactive Prime Builder; ::init gtkb pb; governed bridge proposal filing; reasoning high

# Defect-Fix Proposal - WI-5253 Ollama D Publisher Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5253-ollama-publisher-recovery
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5253-OLLAMA-PUBLISHER-RECOVERY-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5253

target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_harness.py"]

## Claim

Prime Builder proposes a bounded defect-fix slice for `WI-5253`: repair the Ollama D bridge-verdict publisher recovery path so a recovery turn that receives non-publisher tool calls does not strand dispatcher-produced Loyal Opposition work with only zero-stdout/no-progress failure evidence.

## Defect / Reproduction

Live fleet reconciliation found repeated genuine Ollama D dispatcher runs that entered bridge-verdict publisher recovery and then failed without publishing a governed verdict:

- `2026-07-15T02-32-53Z-loyal-opposition-D-66f3e2` on `gtkb-wi5241-wi5219-pauth-registered-vocabulary`
- `2026-07-15T02-39-27Z-loyal-opposition-D-5910d9` on `gtkb-wi5241-wi5219-pauth-registered-vocabulary`
- `2026-07-15T02-40-33Z-loyal-opposition-D-52177f` on `gtkb-wi5241-wi5219-pauth-registered-vocabulary`
- `2026-07-15T03-33-25Z-loyal-opposition-D-4d3aff` on `gtkb-wi5229-binary-verified-finalizer-hunk-patch`

Observed failure signature: exit code `1`, `stop_reason=no_progress_loop`, zero stdout, and stderr containing `ollama_harness: bridge verdict publisher recovery received non-publisher tool call` or `repeated bridge verdict publisher failures before completion`.

Current source evidence:

- `scripts/ollama_harness.py` increments `bridge_recovery_turns` after missing or failed `PublishBridgeVerdict` output, then narrows `active_tools` to `PublishBridgeVerdict` only while recovery is active.
- In that same recovery branch, a later tool call whose name is not `PublishBridgeVerdict` raises `OllamaHarnessError("bridge verdict publisher recovery received non-publisher tool call")` immediately.
- Existing focused tests cover successful recovery after a missing `verdict_path` and fail-closed repeated publisher failures, but they do not require the non-publisher recovery fallback to be diagnostic, bounded, and useful to dispatcher reporting.

WI-5224 prevents false successful completion when no governed verdict exists, and WI-5216 covers older provider verdict-denial loops. WI-5253 is the D-specific follow-on for the current publisher-recovery failure mode. The sibling cloud-provider/H variant remains separately tracked by WI-5245.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `DCL-OLLAMA-TOOL-PARITY-GATE-001`, `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` already define the needed behavior: Ollama D must use the governed tool surface, preserve author/session provenance, publish bridge verdicts only through the governed path, and fail closed with diagnostic evidence instead of false completion or silent stranded work. No new or revised specification is required before implementation.

## In-Root Placement Evidence

All proposed target paths are inside `E:\GT-KB`:

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - requires onboarded harnesses to meet the bridge review capability floor with governed tool use and diagnostic failure behavior.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - governs the Ollama guarded tool surface, including fail-closed parity behavior.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` - requires Ollama-authored bridge artifacts and dispatcher evidence to preserve correct author/session metadata.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs bridge proposal, GO, implementation report, and verification lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires implementation proposals to cite concrete governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires final verification to execute spec-derived tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires Project Authorization, Project, Work Item, and target path metadata.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires implementation-start checks to enforce PAUTH scope at operation time.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH is not a bridge bypass and implementation still requires GO plus start authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires preserving discovered defects and evidence as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - supports turning observed operational failure into governed WI/test/proposal flow.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - supports lifecycle progression from defect observation to work item, linked test, PAUTH, proposal, implementation, and verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps the repair in GT-KB platform paths, not adopter application scope.
- `GOV-STANDING-BACKLOG-001` - supports preserving the uncovered defect as active backlog work.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - relevant because Codex files this proposal through the Codex non-bypass bridge helper path.

## Prior Deliberations

- `DELIB-202666204` - owner decision authorizing WI-5253 governed proposal and implementation flow.
- `DELIB-202666171` - WI-5210 provider LO governed verdict publication verification context.
- `DELIB-20264376` - prior Ollama dispatch-failure hardening verification context.
- `DELIB-20261075` - earlier Ollama dispatch reliability investigation identifying silent verdict-production failures and prompt/tool-loop weaknesses.
- `DELIB-202666173` - sibling H/cloud-provider publisher recovery defect context, kept separate from this D-specific slice.

## Owner Decisions / Input

- `DELIB-202666204` records the active owner fleet directive and authorizes the WI-5253 governed PAUTH/proposal path.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5253-OLLAMA-PUBLISHER-RECOVERY-20260715` is active for `WI-5253` and allows `source` and `test` mutations only.

## Proposed Scope

1. Add focused regression coverage in `platform_tests/scripts/test_ollama_harness.py` for the observed recovery state: after a failed or incomplete `PublishBridgeVerdict` attempt, a subsequent non-publisher tool call must not produce an opaque zero-stdout no-progress exit with no useful dispatcher evidence.
2. Update `scripts/ollama_harness.py` so publisher recovery remains fail-closed but produces bounded, actionable diagnostics or drives the model back to `PublishBridgeVerdict` without accepting ungoverned bridge mutation.
3. Preserve the rule that bridge-review and verification routes are not complete until `PublishBridgeVerdict` succeeds.
4. Preserve the publisher-only final artifact path: no direct bridge file writes, no Write/Edit verdict filing, no dispatcher runtime JSON edits, no lease edits, and no eligibility reconfiguration.
5. Keep the implementation D/Ollama-specific. Do not merge the sibling H/cloud-provider repair into this slice unless a reviewer explicitly requires a shared abstraction in a later governed revision.

## Explicit Exclusions

- No direct edits to dispatcher runtime JSON, leases, locks, or active lease files.
- No dispatcher eligibility/configuration transaction.
- No direct harness-to-harness contact.
- No credential lifecycle action.
- No production deployment, release, git push, destructive cleanup, or unrelated worktree mutation.
- No source/test changes outside the two listed target paths.
- No reduction of D/F/H turn, operation, session, worker, or lease allowances.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | `python -m pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short` must include the new publisher-recovery regression and existing Ollama bridge-review behavior. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Regression must prove non-publisher fallback calls during publisher recovery cannot mutate bridge state through a non-governed tool path. |
| `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` | Existing metadata tests in `platform_tests/scripts/test_ollama_harness.py` must continue to pass, including dispatcher session id propagation into `PublishBridgeVerdict`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation must start only after GO, work-intent claim, and implementation-start authorization; final report must be a NEW bridge artifact for independent LO verification. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must include exact commands and observed pass/fail output for all focused tests. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Implementation-start packet must show only the PAUTH-covered target paths and allowed mutation classes `source` and `test`. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | PAUTH must not be treated as implementation permission without bridge GO and start authorization. |

Minimum command set expected after implementation:

- `python -m pytest platform_tests/scripts/test_ollama_harness.py -q --tb=short`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5253-ollama-publisher-recovery --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5253-ollama-publisher-recovery`

## Acceptance Criteria

1. A simulated Ollama D bridge-review run that enters publisher recovery and then receives a non-publisher tool call terminates through a bounded, diagnostic, governed path.
2. The repair does not falsely mark the dispatch complete unless `PublishBridgeVerdict` returns a successful `verdict_path`.
3. The repair does not permit Write/Edit/direct bridge mutation as a substitute for `PublishBridgeVerdict`.
4. Repeated publisher failures remain bounded and visible to dispatcher telemetry instead of becoming silent loops.
5. Existing successful publisher recovery after a missing `verdict_path` still passes.
6. Author/session metadata propagation for Ollama `PublishBridgeVerdict` remains intact.
7. All implementation changes are limited to `scripts/ollama_harness.py` and `platform_tests/scripts/test_ollama_harness.py`.

## Risks / Rollback

Risk: loosening recovery behavior could allow a non-publisher tool path to produce or mutate verdict artifacts. Mitigation: tests must assert that only `PublishBridgeVerdict` can complete the governed verdict path.

Risk: over-tightening recovery could keep D unavailable for substantive LO work. Mitigation: preserve successful recovery after incomplete publisher results and make any final failure diagnostic rather than opaque.

Risk: duplicating shared provider behavior could diverge from H/cloud-provider recovery. Mitigation: this slice stays D-specific; WI-5245 remains the sibling cloud-provider repair vehicle.

Rollback is a revert of the focused source/test implementation commit. Bridge files, PAUTH, work item, linked test, and deliberation records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`fix`
