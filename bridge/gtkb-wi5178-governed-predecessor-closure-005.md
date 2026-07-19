REVISED
# WI-5178 Governed PAUTH Enforcement Predecessor Closure

bridge_kind: prime_proposal
Document: gtkb-wi5178-governed-predecessor-closure
Version: 005
Responds to: bridge/gtkb-wi5178-governed-predecessor-closure-004.md
Author: Prime Builder (Codex, harness A)
Date: 2026-07-15 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6d5c-2017-7d43-902e-b74483f50fff
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop Prime Builder execution worker; user-bounded bridge-only NO-GO revisions

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-WI5178-PREDECESSOR-CLOSURE-20260715
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5178

target_paths: [".gitattributes", "config/governance/project-authorization-operation-taxonomy.toml", "groundtruth-kb/src/groundtruth_kb/governance/project_authorization_envelope.py", "groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py", "groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", "scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "scripts/dispatcher_runtime.py", "scripts/implementation_start_gate.py", "scripts/check_project_authorization_operation_time_enforcement.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py", "platform_tests/scripts/test_go_impl_claim_timebox.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_work_intent_auto_extend.py", "platform_tests/scripts/test_worker_packet_authorization_envelope.py"]

implementation_scope: source, test, configuration, repository metadata, and governed WI-5178 closure evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Dependency Closure And Fresh GO Request

Prime Builder accepts version 004's dependency ordering. The sole operational
blocker is now closed: `bridge/gtkb-wi5249-prime-no-action-claim-filer-008.md`
is latest `VERIFIED`, MemBase records `WI-5249` resolved, and that verdict
confirms the version 007 stand-down explicitly withdrew the prior aggregate
implementation attempt as an active shared dirty-path claim, including
`platform_tests/scripts/test_bridge_work_intent_registry.py`.

No substantive implementation-plan change is requested or implied. This
revision re-requests independent review of the unchanged version 001 plan and
preserves all 24 targets, hunk-level reconstruction, foreign-owner exclusions,
PAUTH, owner decision, specification links, and verification matrix. A fresh
GO, `go_implementation` claim, and successful implementation-start packet
remain mandatory; any remaining peer-report collision, PAUTH denial, target
drift, or hunk-ownership ambiguity fails closed.

## Summary

Establish a governed, WI-5178-only implementation chain for the permanent project-authorization operation-time evaluator and its proposal, claim, packet, and implementation-start integrations. The current shared worktree contains an unapproved partial substrate across these surfaces. This proposal does not bless that aggregate dirty state. After independent `GO`, Prime Builder must reconstruct an exact WI-5178 candidate from the current committed baseline plus only attributable WI-5178 hunks, complete the missing evaluator/check surfaces, repair the known adjacent regressions, and prove `PAUTH-OP-A1` through `PAUTH-OP-A9` before reporting implementation.

The end state is a focused verified commit that allows WI-5178 to close on its own evidence. It does not claim that WI-5187 is already verified and does not absorb WI-5184 terminal-kind actionability, WI-5249 NO-ACTION filing, WI-5255 telemetry provenance, WI-5277 quarantine disposition, or any other concurrent work. WI-5249 remains latest `NO-GO` until this predecessor, WI-5184, and WI-5277 satisfy their separate governed conditions.

## Current Baseline And Attribution Boundary

- WI-5178 is live at version 3, `open`, `backlogged`, and previously `unapproved`; the new PAUTH is active but no implementation authority exists without this thread receiving `GO`.
- The active owner decision is `DELIB-202666316`. It authorizes this PAUTH and proposal while preserving the bridge, claim, implementation-start, verification, report, and terminal finalization gates.
- WI-5187 remains open and `bridge/gtkb-modernization-wi5187-minimal-git-binding-substrate-004.md` is latest `NO-GO`; no supersession-by-WI-5187 closure is asserted.
- `bridge/gtkb-wi5249-prime-no-action-claim-filer-006.md` identifies current foreign substrate and four adjacent failures. This proposal accepts those findings and gives the PAUTH operation-time portion its own owner, tests, report, and verdict path.
- The live `groundtruth.db` passes normal and immutable `PRAGMA quick_check`, but the committed `HEAD:groundtruth.db` blob is malformed. This proposal excludes `groundtruth.db` from `target_paths`; no DB binary replacement, staging, or commit is authorized.
- The implementation candidate must be built from hunk-level ownership evidence. Whole-file copying from the shared worktree is prohibited. Any hunk whose ownership is ambiguous fails closed and remains excluded pending a separately governed disposition.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - primary requirement; requires one fail-closed evaluator and equivalent enforcement at proposal, work-intent, packet, and start boundaries with assertions `PAUTH-OP-A1` through `PAUTH-OP-A9`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - defines append-only PAUTH fields, currentness, inclusion/exclusion, mutation-class, and forbidden-operation semantics.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires current owner-backed project authorization before implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - this PAUTH cannot substitute for independent `GO`, claim, packet, start, report, or verification.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5249 must remain non-startable until its governed predecessors are terminal; this proposal does not rely on prose to create immediate downstream actionability.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this proposal to the exact PAUTH, project, WI, and target list.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete links to every governing requirement and no phantom citations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed specification-derived evidence against the exact isolated candidate.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves Prime/LO status authority and the append-only numbered bridge chain.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - requires attributable author and session metadata on every chain entry.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps WI-5178 implementation, tests, report, verdict, and lifecycle evidence durable and separate from adjacent work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the implementation and closure claim to be backed by linked artifacts rather than chat inference.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - permits lifecycle closure only after the implementation and verification artifacts establish completion.
- `GOV-STANDING-BACKLOG-001` - preserves separate visibility for WI-5184, WI-5249, WI-5255, and WI-5277.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all targets and evidence remain inside `E:\GT-KB` and outside Agent Red.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires the Codex helper-mediated proposal path and parity-preserving hook behavior.
- `ADR-CROSS-HARNESS-PARITY-001` - requires one authorization decision contract across supported harness routes rather than harness-local policy forks.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - hard-gates the per-harness behavioral disposition for the live hook and shared evaluator changes.

## Prior Deliberations

- `DELIB-202666316` - current owner authorization for a WI-5178-only PAUTH and bounded closure proposal; protected work still requires independent `GO` and the remaining gates.
- `DELIB-202666152` - earlier unified-foundation direction transferred the permanent evaluator into WI-5187 and conditioned WI-5178 supersession on WI-5187 verification. That condition is not satisfied, so this proposal uses the newer owner-authorized WI-5178 evidence path and does not claim historical supersession.
- `bridge/gtkb-modernization-wi5187-minimal-git-binding-substrate-004.md` - current WI-5187 `NO-GO`, confirming that WI-5187 cannot yet close WI-5178.
- `bridge/gtkb-wi5249-prime-no-action-claim-filer-006.md` - independent finding that the dirty worktree commingles WI-5178, WI-5184, WI-5249, and WI-5277 ownership and cannot be finalized through WI-5249.
- `bridge/gtkb-wi5138-database-incident-recovery-evidence-002.md` - accepts live row-level DB recovery evidence while prohibiting an inferred conventional DB commit.
- `WI-5178` version 3 and `TEST-11341` - current work-item and linked-test carriers for the fail-closed authorization envelope.

The incorrect `DELIB-202666082` operation-time citation from the superseded WI-5249 revision is deliberately not reused; live DA readback showed it belongs to unrelated root-boundary work.

## Owner Decisions / Input

- Owner message: `AUTHORIZE WI-5178 GOVERNED PREDECESSOR CLOSURE`.
- Governed capture: `DELIB-202666316`, formal approval packet `.groundtruth/formal-artifact-approvals/2026-07-15-DELIB-202666316.json`.
- Active authorization: `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-WI5178-PREDECESSOR-CLOSURE-20260715`, version 1.
- The decision authorizes PAUTH creation and this proposal. It does not authorize protected mutation until an independent Loyal Opposition session writes `GO` for this exact version.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` fully defines the evaluator inputs, deterministic precedence, four mandatory enforcement points, decision evidence, currentness behavior, and nine executable assertion groups. The supporting PAUTH envelope, project authorization, dependency ordering, bridge linkage, verification, artifact lifecycle, provenance, and isolation specifications provide the remaining closure contract.

The primary DCL currently names two not-yet-present source paths: `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_envelope.py` and `scripts/check_project_authorization_operation_time_enforcement.py`. They are explicit targets here so implementation cannot declare completion while leaving the formal evaluator/check surface unresolved. No formal requirement mutation is proposed.

## Cross-Harness Disposition

- **Claude Code:** `.claude/hooks/bridge-compliance-gate.py` remains the live enforcement surface and must stay byte-identical to `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` after LF normalization. Claude proposal writes must receive the same PAUTH decision and stable reason code as the shared evaluator.
- **Codex:** the governed non-bypass bridge writer continues to invoke the live Claude gate in audit mode. Codex receives the same evaluator, taxonomy, target classification, denial precedence, and recovery evidence; no Codex-only bypass or weaker compatibility path is allowed.
- **Cursor and Antigravity:** both consume the shared GT-KB scripts, project-authorization records, and generated hook/template contract. No harness-local policy fork is added; claim, packet, and start requests must resolve through the same canonical evaluator.
- **API, Goose, and provider-backed headless harnesses:** shared proposal, dispatcher continuation, work-intent, packet, and start services use the same taxonomy and decision envelope. Provider transport differences do not alter authorization semantics.
- **Waivers:** none. Every applicable harness route must preserve behavioral parity, and an unavailable or unresolvable route fails closed rather than receiving a typed exception.

## Implementation Plan After GO

1. Acquire a fresh `go_implementation` claim for this thread and run `scripts/implementation_authorization.py begin` against this exact proposal. Require the registered taxonomy, exact 24 targets, current PAUTH version, and envelope hash to pass.
2. Capture current committed hashes and produce a WI-5178 hunk manifest for every dirty target. Reconstruct the candidate from `HEAD` plus only hunks attributable to the PAUTH evaluator and its cross-gate integrations. Exclude all ambiguous or foreign hunks.
3. Complete the permanent taxonomy/evaluator, proposal-filing, work-intent, packet, and implementation-start integrations. Create the two DCL-named missing paths and retain strict hook/template parity, including stable LF handling through the narrow `.gitattributes` rule.
4. Correct only WI-5178-owned fixtures and regressions. Do not implement terminal non-implementation kind semantics, NO-ACTION filing, telemetry attribution, quarantine policy, or unrelated dispatcher behavior.
5. Run the complete verification matrix below against the exact candidate. File a post-implementation report with hunk manifest, hashes, test output, preflights, and explicit foreign-work exclusions.
6. Permit lifecycle closure only after independent `VERIFIED` finalizes the focused implementation/report/verdict transaction. Do not stage or commit `groundtruth.db` through this thread.

## Spec-Derived Verification Plan

| Requirement | Executed evidence required before report |
| --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, `PAUTH-OP-A1` through `PAUTH-OP-A9` | `python scripts/check_project_authorization_operation_time_enforcement.py`; `python -m groundtruth_kb.cli assert --spec DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; all outer assertions must be PASS with no partial or unavailable evidence. |
| Taxonomy and envelope determinism | `python -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short`; unknown operations/classes and unregistered forbidden names deny, forbidden precedence wins, and bounded requests allow. |
| Proposal filing and hook parity | `python -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -q --tb=short`; manual and create-missing-state PAUTHs enforce equivalent target/operation bounds and live/template hook bytes match. |
| Work-intent acquisition | `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_go_impl_claim_timebox.py -q --tb=short`; denied claims are side-effect free and valid bounded claims retain behavior. |
| Packet and start currentness | `python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_work_intent_auto_extend.py platform_tests/scripts/test_worker_packet_authorization_envelope.py -q --tb=short`; ID/version/hash/target/session changes deny before effect. |
| Dispatcher continuation uses the same claim semantics | `python -m pytest platform_tests/scripts/test_dispatcher_runtime_work_intent.py -q --tb=short`; continuation cannot bypass the canonical evaluator. |
| Known adjacent regressions | Rerun the exact WI-5249 adjacent command covering claim CLI, timebox, auto-extend, and start-gate modules; require zero failures rather than the prior `4 failed, 229 passed`. |
| Hunk ownership and target bounds | Generate an exact hunk manifest from `HEAD`; verify every changed path is in `target_paths`, every changed hunk maps to WI-5178, and no WI-5184/WI-5249/WI-5255/WI-5277 hunk is present. |
| Static quality | `python -m ruff check` and `python -m ruff format --check` over every Python target; `git diff --check` over the exact candidate. |
| Governance | Applicability and clause preflights pass on this proposal and the implementation report; the report cites the active PAUTH, exact start packet, executed commands, and all foreign-work exclusions. |

## Acceptance Criteria

- The exact 24-path claim and implementation-start packet pass against the then-current PAUTH and repository state.
- Every `PAUTH-OP-A1` through `PAUTH-OP-A9` assertion passes on the same candidate.
- Proposal, claim, packet, and start surfaces use the same canonical evaluator and stable reason codes.
- The known adjacent suite has zero failures.
- Live/template hook parity and LF stability pass without unrelated formatting churn.
- The implementation report proves a hunk-isolated WI-5178 candidate and excludes WI-5184, WI-5249, WI-5255, WI-5277, and all other foreign work.
- No DB binary, credential, dispatcher topology, external system, push, release, deployment, destructive cleanup, or unrelated shared-worktree mutation occurs.
- WI-5178 is closed only by the governed post-VERIFIED lifecycle path with terminal evidence, not by this proposal or owner message alone.

## Risk / Rollback

The dominant risk is absorbing unapproved same-path work from the heavily dirty shared worktree. Hunk-level reconstruction, exact pre-start hashes, the 24-path upper bound, foreign-owner exclusions, and fail-closed ambiguity handling contain that risk. The second risk is weakening valid PAUTH workflows while adding denial checks; cross-gate parity and positive bounded fixtures are mandatory. The third risk is line-ending churn in the hook pair; the narrow `.gitattributes` rule and byte-parity test must contain it.

Rollback is a focused revert of the independently VERIFIED WI-5178 commit. Append-only PAUTH, decision, proposal, report, verdict, and audit evidence remain intact. No rollback may replace the live DB with the malformed committed DB blob.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered entry for `gtkb-wi5178-governed-predecessor-closure`. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - this closes a fail-closed authorization enforcement defect and its exact cross-gate regressions without adding a new product feature.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
