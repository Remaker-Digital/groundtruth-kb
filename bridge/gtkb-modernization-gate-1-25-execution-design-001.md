NEW

# Governance Review - Gate 1.25 Assurance Bootstrap Execution Design

bridge_kind: governance_advisory
Document: gtkb-modernization-gate-1-25-execution-design
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-07-10 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3618-1eea-7252-b02b-a3b9b6401bf7
author_model: GPT-5 family (Codex)
author_model_version: not exposed by harness
author_model_configuration: Codex desktop, default collaboration mode, interactive Prime Builder

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION
Work Item: WI-5137

target_paths: []
implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## Claim

Prime Builder requests independent review of the exact Gate 1.25 execution design before any implementation authorization exists.

This is a terminal governance review. It defines the future proposal boundaries, dependencies, tests, and non-impairment obligations for WI-5178, WI-5153, WI-5152, and WI-5166. It does not file an implementation proposal, create or cite an active PAUTH, authorize a work-intent claim, or permit protected mutation.

## Requirement Sufficiency

New or revised requirement required before implementation.

The existing formal carriers are sufficient to review the substantive Gate 1.25 design, but the current implementation-authorization path does not enforce PAUTH allowed mutation classes or forbidden operations. WI-5178 and its linked TEST-11341 must repair that mechanical gap, or an owner-approved alternative must explicitly disposition it, before ordinary automated Gate 1.25 implementation can begin.

This requirement-gap statement is intentional. Together with canonical terminal `bridge_kind: governance_advisory` and `target_paths: []`, it keeps a later `GO` off the Prime implementation surface and makes any attempted implementation-authorization packet fail closed.

## Readiness Correction

The owner approved the original Gate 1.25 readiness packet as `DELIB-202666080`, content hash `2B50B4596E4D3FD5C492AD0E534DB21700B70E30E10F967E406EDD6CDD3ADC63`.

The pre-activation audit then proved that the packet's proposed readiness-only PAUTHs would not mechanically enforce their declared `allowed_mutation_classes` or `forbidden_operations`. The audit is preserved at `.gtkb-state/decision-packets/gate-1-25-preactivation-enforcement-audit.md`.

This review preserves the approved applicability contract, exact 28-assertion map, child outcomes, target-path design, acceptance commands, rollback, and WI-5158 hold. It replaces only the unsafe readiness mechanism:

- no readiness PAUTH is created;
- no dispatchable implementation proposal is filed;
- one terminal governance review evaluates the complete design;
- actual PAUTH and child proposal creation move into a later content-hashed execution-activation decision.

## Program Order

1. WI-5178 enforces PAUTH allowed-mutation and forbidden-operation bounds at bridge filing, implementation-packet creation, work-intent acquisition, and implementation start.
2. WI-5153 makes assertion evaluation fail closed and provides scoped applicability execution.
3. WI-5152 implements the exact WI-5158 28-assertion registry and source-linked projection.
4. WI-5166 implements parsed intuitiveness and non-impairment proposal, activation, verification, and closure gates.
5. The integrated Gate 1.25 suite runs and each child receives independent implementation verification.
6. WI-5156 remains a separate control-plane work item for mechanically recording the broader project dependency graph and implementation order.
7. WI-5158 remains `NO-ACTION` until Gate 1.25 is verified, currentness blockers are resolved, and a substantive `REVISED` proposal receives fresh independent review.

WI-5152 and WI-5166 may be designed in parallel after WI-5153. Their protected implementation may overlap only when exact claims are disjoint. Shared hook, registry, database, and integration mutations remain serialized.

## Scoped-Assertion Applicability Contract

Applicability and evaluation result are separate dimensions.

- `MUST_APPLY`: the assertion applies to the named work item and gate; current executable evidence must produce `PASS`.
- `DEFERRED_TO`: the assertion remains program-applicable but is owned by a current successor WI with project membership, gate, and owner-approved charter provenance. It is never counted as a full-carrier pass.
- `NOT_APPLICABLE`: allowed only by an explicit governed rule with provenance. Missing evidence cannot infer it.
- Unclassified, stale, contradictory, or unresolvable applicability produces `UNASSESSED` and blocks.

Evaluation results remain `PASS`, `FAIL`, `PARTIAL`, `UNASSESSED`, and `NOT_APPLICABLE`. `SKIPPED` is an execution event, not a passing result. Exit code zero means aggregate `PASS` only. A scoped WI pass never promotes the full carrier while any `DEFERRED_TO` assertion remains incomplete.

Carrier-version or assertion-definition changes invalidate prior applicability and evaluation evidence.

## Exact WI-5158 Assertion Map

| Carrier | MUST_APPLY to WI-5158 | DEFERRED_TO | Conditional |
| --- | --- | --- | --- |
| ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001 v1 | GIT-ADR-A1, A2, A3, A4, A6, A7 | GIT-ADR-A5 -> WI-5159 | none |
| REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001 v1 | GIT-REQ-A1, A2, A3, A4, A6, A8 | GIT-REQ-A5 -> WI-5159; GIT-REQ-A7 -> WI-5160 | none |
| DCL-GIT-BRANCH-BINDING-PROMOTION-001 v2 | BRANCH-BIND-A1, A2, A3, A4, A5, A7, A8, A9 | BRANCH-BIND-A6 -> WI-5159 | none |
| GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 v1 | A1 proposal; A2 activation; A3 verification/closure | none | A4 is `NOT_APPLICABLE` only when a deterministic target-path and dependency check proves no active worker-loading route changes; otherwise `MUST_APPLY` or `UNASSESSED` |

Totals: 28 outer assertions; 23 `MUST_APPLY`; 4 `DEFERRED_TO`; 1 conditionally `NOT_APPLICABLE` with fail-closed proof.

## Future Child Proposal: WI-5178

Title: Enforce PAUTH allowed-mutation and forbidden-operation bounds at implementation start.

Formal authority:

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

Proposed future implementation paths:

```json
[".gitattributes","scripts/implementation_authorization.py","scripts/implementation_start_gate.py","scripts/dispatcher_runtime.py","groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py",".claude/hooks/bridge-compliance-gate.py","groundtruth-kb/templates/hooks/bridge-compliance-gate.py","platform_tests/scripts/test_implementation_authorization.py","platform_tests/scripts/test_implementation_start_gate.py","platform_tests/scripts/test_project_authorization.py","platform_tests/scripts/test_dispatcher_runtime_work_intent.py","platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py","platform_tests/groundtruth_kb/test_cli_bridge_propose.py","platform_tests/scripts/test_pauth_mutation_envelope_enforcement.py","groundtruth.db"]
```

Required outcomes:

- Proposal filing rejects source, test, configuration, KB, Git, dispatcher, or other targets not permitted by the cited PAUTH mutation classes.
- Any operation named by `forbidden_operations` fails regardless of allowed class.
- Implementation packets carry the PAUTH envelope and revalidate it against current PAUTH version and expiry.
- Dispatcher work-intent acquisition fails before a claim when the requested operation is outside the PAUTH envelope.
- A `["bridge", "metadata"]` filing PAUTH cannot authorize protected implementation.
- Included/excluded WI and specification behavior remains fail closed.
- Correctly bounded implementation PAUTHs retain legitimate behavior.
- `/.claude/hooks/bridge-compliance-gate.py text eol=lf` is recorded narrowly in `.gitattributes`, the live hook is normalized once, and live/template hook bytes remain identical after future checkouts.
- TEST-11341 becomes executable and passing before Gate 1.25 implementation PAUTH activation.

## Future Child Proposal: WI-5153

Title: Make assertion evaluation fail closed on unsupported, skipped, and partial entries.

Formal authority:

- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` v1
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` v1
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

Proposed future implementation paths:

```json
["groundtruth-kb/src/groundtruth_kb/assertions.py","groundtruth-kb/src/groundtruth_kb/assertion_schema.py","groundtruth-kb/src/groundtruth_kb/gates.py","groundtruth-kb/tests/test_assertions.py","groundtruth-kb/tests/test_assertion_schema.py","groundtruth-kb/tests/test_gates.py","scripts/check_artifact_evaluability.py","platform_tests/scripts/test_check_artifact_evaluability.py","groundtruth.db"]
```

Required outcomes:

- Unsupported required assertion types fail.
- Zero executable outer assertions produce `UNASSESSED`.
- Mixed complete/incomplete required arrays cannot pass.
- Required skipped children propagate `FAIL` or `PARTIAL` through composites.
- Prose/stored outer IDs, counts, and significant order reconcile.
- Current evidence carries subject, subject version/hash, evaluator version, execution time, scope, TTL/invalidation, and contradiction state.
- Scoped assertion execution applies the approved applicability contract without claiming a full-carrier pass.
- Existing fully executable assertions preserve legitimate results.
- TEST-11322 is corrected to cite the evaluability DCL and executable test surface through the separately approved test-record route.

Current red baseline:

- unsupported assertion types are currently skipped;
- skip records are currently marked `passed: true`;
- skipped composite children are discarded;
- zero executable assertions currently yield an overall passing result;
- TEST-11322 still cites the older cross-cutting GOV and has no executable test binding.

## Future Child Proposal: WI-5152

Title: Implement the WI-5158-scoped modernization hard-invariant registry and gate projection.

Formal authority:

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` v1
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` v1
- the four Git/non-impairment carriers in the exact map above
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

Proposed future implementation paths:

```json
["config/governance/modernization-hard-invariants.toml","config/governance/spec-applicability.toml","config/governance/adr-dcl-clauses.toml","scripts/check_modernization_invariant_registry.py","platform_tests/scripts/test_modernization_invariant_registry.py","platform_tests/scripts/test_bridge_applicability_preflight.py","platform_tests/scripts/test_adr_dcl_clause_preflight.py","groundtruth.db"]
```

Required outcomes:

- Exactly 28 WI-5158 slice entries are registered.
- Every entry links carrier ID/version, outer assertion ID, applicability, WI, gate, evaluator, current evidence identity, severity, and provenance.
- Results are generated, source-linked projections and are never editable authority.
- Missing evaluator, changed carrier version, stale evidence, missing successor, stale project membership, or contradictory applicability blocks.
- The full carrier cannot pass while any `DEFERRED_TO` assertion remains incomplete.
- Repeated runs produce identical normalized results.
- WI-5152 remains open for the broader all-94-handle Assurance charter.
- TEST-11321 is bound to the executable Gate 1.25 surface without claiming the broader charter complete.

The existing applicability and clause registries remain bridge discovery/review mechanisms. Their heuristic classification does not replace the formal outer-assertion-to-WI registry.

## Future Child Proposal: WI-5166

Title: Enforce modernization intuitiveness and non-impairment gates.

Formal authority:

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` v1
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` v1
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

Proposed future implementation paths:

```json
[".claude/hooks/bridge-compliance-gate.py","groundtruth-kb/templates/hooks/bridge-compliance-gate.py","scripts/check_modernization_nonimpairment.py","platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py","platform_tests/scripts/test_modernization_nonimpairment.py","platform_tests/scripts/test_bridge_compliance_gate_disposition.py","groundtruth.db"]
```

Required outcomes:

- Cross-cutting proposals require a parsed `Intuitiveness/Non-Impairment Disposition`.
- The disposition contains exactly one fenced JSON object with a supported schema version and fields for applicability/provenance, canonical authority, primary route, before/after behavior, self-descriptive naming, obsolete-guidance disposition, history preservation, baseline, expected result, rollback, hard invariants, fail-closed conditions, essential-context preservation, and an optional owner-tradeoff deliberation.
- Presence-only headings and placeholders fail.
- Activation evidence requires baseline, result, rollback, and hard-invariant evidence.
- Missing hard-invariant evidence blocks verification and closure.
- A4 is stage-aware and uses deterministic target/dependency proof. It does not duplicate WI-5154 global leakage scanning or WI-5168 context-freshness work.
- Live and template hook behavior remain identical.
- TEST-11335 is bound to the executable test surface.

## Intuitiveness/Non-Impairment Disposition

Canonical authority:

- Formal behavior comes from the cited MemBase carriers and owner decisions.
- This governance-review file is review evidence, not implementation authority.
- Future generated registries and reports are projections, not competing sources of truth.

Before:

- a readiness-only PAUTH appears bounded but its mutation and operation restrictions are not enforced;
- unsupported or incomplete assertion evidence can appear passing;
- WI-5158 lacks an explicit outer-assertion applicability map and parsed modernization disposition.

After the future implementations:

- workers encounter one mechanically enforced PAUTH boundary before proposal filing, work-intent claim, and implementation start;
- assertion results fail closed with explicit applicability and currentness;
- the 28-assertion WI-5158 slice is deterministic and source linked;
- cross-cutting proposals expose an obvious, parsed non-impairment disposition.

Obsolete guidance treatment:

- no old artifact is silently deleted or rewritten;
- historical bridge and deliberation records remain audit evidence;
- active worker-loading paths may not treat superseded guidance as current authority.

Baseline and expected result:

- the pre-activation audit and current red tests are preserved;
- every child must demonstrate before/after behavior and retain legitimate existing behavior;
- Gate 1.25 cannot pass by reducing coverage, disabling a capability, or reclassifying missing evidence as not applicable.

Rollback:

- each future child is isolated and separately reviewed;
- source rollback is a scoped revert of that child;
- append-only bridge, owner-decision, PAUTH, and verification evidence remains intact;
- no Git cleanup, history rewrite, dispatcher drain, release, or deployment is part of rollback.

Hard invariants:

- no implementation without active exact owner authority, independent GO, matching claim, and implementation-start evidence;
- no required unsupported, skipped, stale, contradictory, partial, or absent evidence may pass;
- no scoped pass may be represented as a full-carrier pass;
- no active worker route may load superseded authority;
- no WI-5158 Git mutation occurs before its separately reviewed and owner-hash-approved bootstrap manifest.

Fail-closed conditions:

- changed target occupancy, carrier version, PAUTH version, bridge state, claim, repository head, or test binding blocks execution until refreshed;
- unknown applicability, missing evaluator, invalid provenance, or unavailable current evidence blocks;
- overlap on `groundtruth.db`, hooks, registries, or integration surfaces serializes work.

## Cross-Harness Disposition

The governance review changes no harness surface.

Future WI-5178 and WI-5166 edits affect shared authorization and bridge-hook behavior consumed by multiple harnesses. Their implementation proposals must include live/template parity tests, Codex helper-path validation, and cross-harness non-regression evidence. No worker should receive dispatcher target-selection rules as role or behavior hints; explicit session-envelope role evidence remains authoritative for worker behavior.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires this discovered gate defect, owner correction, backlog item, review, and later execution state to remain explicit and durable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps the approved packet, failed pre-activation audit, superseding review, child proposals, and verification evidence in one traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires explicit pending, blocked, superseded, reviewed, implemented, and verified states instead of prose-only ambiguity.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded owner implementation authority without replacing bridge and implementation-start gates.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - defines the allowed/forbidden PAUTH envelope whose enforcement gap is WI-5178.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - supplies fail-closed result, currentness, and scoped-applicability semantics.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - requires cross-cutting obligations to become executable evidence.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - governs intuitiveness, baseline, rollback, hard invariants, and active worker-loading safety.
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` - supplies Git topology and lifecycle assertions.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` - supplies operational Git outcomes.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - supplies exact binding, fail-closed, bootstrap, and deferred-promotion assertions.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct, versioned bridge review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires substantive carrier linkage in future child proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires complete applicable spec-to-test evidence before VERIFIED.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - governs the later mechanical project-order path in WI-5156.
- `GOV-WORK-TREE-HYGIENE-001` - preserves isolated, attributable future work and blocks overlap assumptions.

## Prior Deliberations

- `DELIB-202666079` - inserts bounded Gate 1.25 before WI-5158.
- `DELIB-202666080` - approves the original content-hashed Gate 1.25 readiness packet.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-ASSURANCE-INVARIANT-PLAN` - establishes the assurance and hard-invariant plan.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-AUTHORITY-CARRIER-MATRIX` - maps modernization authority carriers.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-5-PILOT-AUTHORIZATION` - preserves the separately bounded WI-5158 pilot authority.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-5-EXECUTION-ENTRY-PACKET` - records the prior WI-5158 entry evidence that Gate 1.25 now corrects.

## Owner Decisions / Input

- `DELIB-202666079` authorizes preparation of the Gate 1.25 package but no implementation.
- `DELIB-202666080` approves the exact applicability map, child scope, tests, order, rollback, and non-authorization boundary.
- A superseding activation-correction decision is required before this draft may be filed because the readiness-PAUTH mechanism in the approved packet failed pre-activation validation.
- A later content-hashed execution-activation decision is required before any actual PAUTH or implementation proposal is created.

## Specification-Derived Verification Plan

| Requirement | Readiness-review evidence | Future executable evidence |
| --- | --- | --- |
| PAUTH bounds are mechanical | Pre-activation audit plus WI-5178/TEST-11341 | PAUTH envelope and dispatcher/start-gate tests |
| Assertion evaluation fails closed | Current source and red-baseline evidence | WI-5153 targeted tests and `check_artifact_evaluability.py` |
| WI-5158 applicability is exact | 28-entry table and approved map | WI-5152 deterministic registry checker |
| Non-impairment is parsed and stage-aware | This substantive disposition | WI-5166 hook and checker tests |
| Governance review cannot start implementation | `bridge_kind: governance_advisory`, `target_paths: []`, requirement-gap state | bridge-kind taxonomy, terminal advisory, and implementation-packet rejection tests |
| WI-5158 remains held | live versioned bridge chain | future substantive REVISED plus fresh independent GO |

Readiness checks already executed:

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short -k "governance_review_gap"
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_project_authorization.py -q --tb=short -k "restrictive_included_list or append_only_and_visible"
```

Observed results: 5 passed; 2 passed; 2 passed.

Required integrated Gate 1.25 commands after future implementation:

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_pauth_mutation_envelope_enforcement.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_assertions.py groundtruth-kb/tests/test_assertion_schema.py groundtruth-kb/tests/test_gates.py platform_tests/scripts/test_check_artifact_evaluability.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_invariant_registry.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_nonimpairment.py platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py platform_tests/scripts/test_bridge_compliance_gate_disposition.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe scripts/check_artifact_evaluability.py --spec-id DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001 --work-item WI-5158 --gate verification --json
groundtruth-kb/.venv/Scripts/python.exe scripts/check_modernization_invariant_registry.py --work-item WI-5158 --gate verification --json
groundtruth-kb/.venv/Scripts/python.exe scripts/check_modernization_nonimpairment.py --bridge-id gtkb-modernization-wi5158-git-binding-bootstrap --gate proposal --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli assert --spec DCL-GIT-BRANCH-BINDING-PROMOTION-001 --work-item WI-5158 --gate verification --triggered-by gate-1.25
```

## Requested Loyal Opposition Disposition

Review whether this design is complete, mechanically non-actionable during readiness, properly ordered, and sufficient to prepare later execution activation.

- `GO` means the governance design is ready to support a later owner execution-activation decision.
- `GO` is terminal for this governance-review thread and is not implementation permission.
- `NO-GO` must identify the missing authority, requirement, target boundary, test, dependency, rollback, or non-impairment evidence.
- Do not write `VERIFIED` for implementation because no implementation exists.

## Risks / Rollback

Risk is low during readiness because the filed artifact would contain no active implementation target, PAUTH, claim, or start packet.

Rollback is a later `WITHDRAWN` or superseding governance-review record. Versioned bridge and owner-decision evidence remains append-only. No source, formal carrier, Git state, dispatcher state, or deployment state changes.

## Authority Boundary

This draft is non-dispatchable runtime state until separately approved and filed through the governed bridge writer. A later filed governance-review GO would approve design only. Neither this draft nor such a GO authorizes PAUTH creation, child proposal filing, work-intent claims, implementation-start packets, protected mutation, test-record mutation, Git actions, dispatcher controls, cleanup, release, or deployment.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
