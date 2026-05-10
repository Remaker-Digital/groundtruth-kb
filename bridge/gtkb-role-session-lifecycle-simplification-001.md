# GT-KB Role And Session Lifecycle Simplification Proposal

## Summary

This proposal simplifies the visible role/session model without changing the core Prime Builder and Loyal Opposition protocol.

The current runtime model is mostly correct: durable operating roles attach to persistent harness IDs, while each session has a focus and uses role-required capabilities. The implementation should make that model explicit in the active narrative and startup surfaces:

- Keep `prime-builder` and `loyal-opposition` as the only normal durable operating roles.
- Treat `acting-prime-builder` as historical/provenance language, not a third normal assignable role.
- Introduce `session lane` as non-authority metadata for work types such as research, architecture, quality engineering, operations/release, documentation, and governance stewardship.
- Remove active-looking wording that says `.claude/rules/prime-builder-role.md` is the current role record.

No implementation is included in this proposal.

## Target Paths

Target paths for the proposed implementation:

- `.claude/rules/prime-builder-role.md`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/operating-role.md`
- `.claude/rules/canonical-terminology.md`
- `AGENTS.md`
- `scripts/session_self_initialization.py`
- `tests/scripts/test_session_self_initialization.py`
- `tests/scripts/test_check_harness_parity.py`
- `config/agent-control/system-interface-map.toml`
- `config/agent-control/harness-capability-registry.toml` only if implementation discovers registry wording needs lane-neutral clarification

Protected narrative-artifact note: `.claude/rules/*.md`, `AGENTS.md`, and `memory/work_list.md` are protected narrative-artifact surfaces under `config/governance/narrative-artifact-approval.toml`. Implementation must not write protected narrative artifacts unless the required approval-packet evidence is present.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed through the file bridge and must preserve `bridge/INDEX.md` as canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specifications and maps tests to them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation verification must map role/session behavior claims back to concrete tests and parity checks.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all proposed files are GT-KB platform or governance artifacts under `E:\GT-KB`; no live dependency, verification target, or generated artifact may be sourced from outside the project root.
- `.claude/rules/file-bridge-protocol.md` - defines proposal, review, implementation report, and verification flow.
- `.claude/rules/codex-review-gate.md` - requires bridge review before implementation and requires substantive specification linkage.
- `.claude/rules/operating-model.md` - defines the Prime Builder to Loyal Opposition implementation lifecycle.
- `.claude/rules/operating-role.md` - defines durable harness identity and role assignment semantics.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - role/session terminology changes are durable governance-facing artifacts, not casual wording edits.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserve durable artifacts and explicit lifecycle states.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - role/session terminology changes cross the artifact lifecycle threshold.
- `GOV-ARTIFACT-APPROVAL-001` - formal/narrative authority changes require owner-visible approval evidence when in protected scope.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - protected artifact writes must satisfy the approval hook/evidence model.
- `GOV-SESSION-SELF-INITIALIZATION-001` - startup must disclose role/governance stance correctly.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` - Prime Builder startup focus choices must remain role-correct and not be shown in Loyal Opposition mode.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` - any new canonical term should be placed where agents already read terminology.
- `.claude/rules/canonical-terminology.md` - glossary source for harness, harness identity, role assignment, Prime Builder, Loyal Opposition, session scope, and proposed session lane terminology.
- `config/governance/narrative-artifact-approval.toml` - protected narrative-artifact path and packet schema authority.

## Prior Deliberations

- `DELIB-0830`, `DELIB-0831`, and `DELIB-0832` - role portability and durable harness identity decisions cited by the glossary entries for harness and role assignment.
- `DELIB-S324-PB-INTERROGATION-DIRECTIVE` - Prime Builder interrogative default, relevant because role text must not suggest blind owner-claim acceptance.
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` - session scope and placement framing, relevant because session lane should be placed on an already-read startup/glossary path rather than introduced as an out-of-band convention.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` and `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - current Codex hook parity stance, relevant to any startup/hook wording changes.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-09-14-20-ROLE-SESSION-LIFECYCLE-REVIEW.md` - direct advisory report that identified the simplification opportunity.
- `memory/work_list.md` token-reduction and primer-consolidation entries around role-conditional primers - relevant prior planned direction, but this proposal intentionally keeps the first implementation smaller than full primer consolidation.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-0840` — seed=search; owner_conversation; Owner decision: fresh sessions must self-initialize with role, dashboard, priori
- DA: `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` — seed=search; owner_conversation; Prime Builder / Loyal Opposition Role-Definition Assessment (S310)
- DA: `DELIB-0943` — seed=search; bridge_thread; GTKB-GOV-OWNER-DECISION-SURFACING Slice 1 Verification
- DA: `DELIB-1140` — seed=search; bridge_thread; Bridge thread: gtkb-session-overlay-baseline-implementation (6 versions, VERIFIE
- DA: `DELIB-0944` — seed=search; bridge_thread; GTKB-GOV-OWNER-DECISION-SURFACING Slice 1 Review

## Problem Statement

The active implementation has a clearer role model than some of the visible artifacts now express.

Current runtime facts:

- `harness-state/harness-identities.json` assigns persistent harness IDs.
- `harness-state/role-assignments.json` is the live role source of truth.
- `scripts/harness_roles.py` resolves roles from that map and self-corrects if no Prime Builder exists.
- `scripts/session_self_initialization.py` renders role-specific startup behavior from role profiles.
- `config/agent-control/harness-capability-registry.toml` binds capabilities to `prime-builder`, `loyal-opposition`, or both.

Current visible-artifact drift:

- `.claude/rules/prime-builder-role.md` still calls itself the current role record, which conflicts with `harness-state/role-assignments.json`.
- `acting-prime-builder` remains visible as a role profile even though normal role assignment is now `prime-builder` or `loyal-opposition`.
- Startup and rule text do not yet clearly separate operating role from session focus, work subject, and session lane.
- The project has lifecycle lanes such as research, operations, quality engineering, and documentation, but the durable role model should not expand unless those lanes need separate authority.

## Proposed Change

### Slice A - Role Authority Wording Cleanup

Update active narrative surfaces so they consistently state:

- The live role assignment source is `harness-state/role-assignments.json`.
- `.claude/rules/prime-builder-role.md` and `.claude/rules/loyal-opposition.md` are behavior contracts for their roles, not role assignment records.
- `.claude/rules/operating-role.md` is human-readable guidance for the role-assignment system, not a competing role source.
- No markdown rule file can override the durable role assignment map.

### Slice B - Acting Prime Builder Classification

Classify `acting-prime-builder` as historical/provenance language unless the owner explicitly creates a new authority model.

Implementation may choose one of two low-risk paths:

1. Keep the `acting-prime-builder` code path only as compatibility/provenance wording, with tests proving normal role assignment cannot set it through role-switch commands.
2. Retire it from startup `ROLE_PROFILES` and preserve historical references in documentation only.

Preferred path: option 1 if removal would create unnecessary churn; option 2 if test updates show the profile is no longer needed.

### Slice C - Session Lane Terminology

Add a glossary and startup terminology clarification:

- `operating role`: authority-bearing harness role, currently `prime-builder` or `loyal-opposition`.
- `session lane`: non-authority work classification inside a session, such as research, architecture, implementation, quality engineering, operations/release, documentation, or governance stewardship.
- `session focus`: owner-facing startup selection or custom task mapping.
- `work subject/session scope`: root and write-boundary context.

Explicit rule: session lanes inherit authority from the current operating role. A quality-engineering lane in Loyal Opposition remains read-mostly verification; a quality-engineering lane in Prime Builder may create tests and implementation artifacts within approved scope.

### Slice D - Startup And Test Alignment

Update startup rendering and tests only as needed to avoid implying that lanes are durable roles. Prime Builder focus options may reference lanes, but Loyal Opposition still does not present the Prime focus menu.

## Non-Goals

- Do not change the live role assignment records except through the existing owner-directed role switch path.
- Do not add research, operations, quality engineering, documentation, architecture, or governance as durable operating roles.
- Do not weaken the Prime Builder to Loyal Opposition bridge protocol.
- Do not change bridge statuses or status ownership.
- Do not modify MemBase specifications unless a separate approved formal-artifact path is used.
- Do not perform full primer consolidation in this proposal.
- Do not re-enable retired OS pollers or the retired smart poller.

## Owner Decisions / Input

Owner-visible input in this session:

- The owner reviewed the Loyal Opposition role/session lifecycle recommendation and said: "That is a well-considered proposal. Thank you."
- Codex replied that this would be treated as positive feedback, not formal approval to mutate role artifacts.
- The owner then said: "Please proceed."

Interpretation: this authorizes filing this bridge proposal. It does not authorize protected narrative-artifact writes, formal artifact mutation, deployment, or bypassing the bridge review/verification cycle. Implementation must collect any required protected-artifact approval packet before writing protected narrative artifacts.

## Implementation Plan

1. Inventory all active references that call a markdown file the role source of truth or imply `acting-prime-builder` is a normal durable role.
2. Draft minimal wording changes to `.claude/rules/prime-builder-role.md`, `.claude/rules/acting-prime-builder.md`, `.claude/rules/operating-role.md`, `AGENTS.md`, and `.claude/rules/canonical-terminology.md`.
3. Generate required narrative-artifact approval packet evidence for every protected narrative artifact that will be edited, using the full proposed content and the final target paths.
4. Update `scripts/session_self_initialization.py` only if startup wording or tests require a code-level distinction between operating role and session lane.
5. Update tests to assert that role assignment remains sourced from `harness-state/role-assignments.json`, that `acting-prime-builder` is not presented as a normal durable role, and that session lane wording does not appear as a role map value.
6. Run targeted tests and parity checks.
7. File an implementation report carrying forward spec links, approval-packet evidence, file changes, and test results.

## Test And Verification Plan

Required before implementation report:

- `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short`
- `python -m pytest tests/scripts/test_check_harness_parity.py -q --tb=short`
- `python scripts/check_harness_parity.py --all --markdown`
- `python scripts/check_codex_hook_parity.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-session-lifecycle-simplification`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-session-lifecycle-simplification`

If protected narrative artifacts are modified and staged, also run:

- `python scripts/check_narrative_artifact_evidence.py`

Verification expectations:

- No file other than `harness-state/role-assignments.json` claims to be the current role record.
- `prime-builder` and `loyal-opposition` remain the only normal durable operating roles.
- `acting-prime-builder` is either retired from active startup profile usage or explicitly marked historical/provenance only.
- Session lanes are described as non-authority classifications that inherit the current operating role's permissions.
- Harness parity remains PASS.

## Risk And Rollback

Risks:

- Over-editing role files could accidentally weaken Prime Builder or Loyal Opposition authority boundaries.
- Removing `acting-prime-builder` too aggressively could break historical tests or startup expectations.
- Editing protected narrative artifacts without approval-packet evidence would violate the narrative-artifact approval gate.

Rollback:

- Revert narrative wording and startup/test changes in a scoped rollback commit.
- Leave `harness-state/role-assignments.json` untouched unless a separate owner-directed role-switch operation is requested.
- If `acting-prime-builder` retirement causes regressions, restore it as a historical compatibility alias and add tests proving it is not a normal role-switch target.

## Recommended Commit Type

Recommended commit type after implementation: `docs:` if changes are limited to role/rule wording and tests; `refactor:` if `scripts/session_self_initialization.py` role-profile logic is materially changed.
