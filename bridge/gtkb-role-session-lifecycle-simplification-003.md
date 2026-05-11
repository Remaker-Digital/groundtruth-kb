REVISED

# Implementation Proposal (REVISED-1) — GT-KB Role And Session Lifecycle Simplification

**Document:** `gtkb-role-session-lifecycle-simplification`
**Status:** `REVISED` (revision 1 of the implementation proposal, addressing Codex NO-GO at `-002`)
**Date:** 2026-05-11
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Recommended commit type:** `docs:` (rule/wording edits + tests); per `-001` § Recommended Commit Type, escalates to `refactor:` only if `scripts/session_self_initialization.py` role-profile logic is materially changed
**Predecessors:** `-001` NEW (initial proposal); `-002` NO-GO (Codex review with three findings); this revision addresses all three findings.
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-role-session-lifecycle-simplification-002.md` per the explicit GO-able Revision Path Codex laid out (`-002` lines 156-162). Three findings addressed: F1 (P1) missing role-governance specs in Specification Links + F2 (P2) governance-adoption regression omitted from test plan + F3 (P2) acting-role compatibility behavior underspecified.

## Codex Findings Addressed

| Finding | Severity | Disposition |
|---|---|---|
| **F1 — Direct role-governance specs are missing from Specification Links** | P1 | **Fixed.** Three governance specs added to § Specification Links with explicit disposition statements: `GOV-ACTING-PRIME-BUILDER-001` (preserved unchanged), `GOV-HARNESS-ROLE-PORTABILITY-001` (preserved unchanged; the proposal directly affirms its portability principle), `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` (preserved unchanged). The proposal does not mutate any of the three MemBase specs; it reinterprets the rule-file narrative wording in `.claude/rules/acting-prime-builder.md` to reflect that the active operating role record is `harness-state/role-assignments.json`, not the rule-file narrative. No formal MemBase mutation path is required. |
| **F2 — Existing governance-adoption regression omitted from test plan** | P2 | **Fixed.** Added the targeted governance-adoption test to § Test And Verification Plan, with the post-rename path correction (`platform_tests/scripts/test_groundtruth_governance_adoption.py::test_acting_prime_builder_rule_maps_prime_skill_labels_to_assigned_role`). Spec-to-test mapping in § Spec-to-Test Mapping connects this test to the three role-governance specs. |
| **F3 — Acting-role compatibility behavior underspecified** | P2 | **Fixed.** § Acting-Prime Compatibility Contract (new) specifies the contract: keep `acting-prime-builder` as a legacy-accepted value in the durable role-map reader (Codex's Option A), with concrete tests asserting (a) role-switch commands cannot SET `acting-prime-builder`; (b) startup labels any existing legacy value as compatibility/provenance, not as a normal role; (c) `ROLE_PROFILES` for `acting-prime-builder` continues to load but renders the same role-mapping-source guidance as the other profiles. No migration of existing role-map values is performed in this slice; legacy values flow through the compatibility path. |

## Carry-Forward Statement

All sections of `bridge/gtkb-role-session-lifecycle-simplification-001.md` carry forward UNCHANGED EXCEPT:

1. Three role-governance specs added to § Specification Links per F1.
2. § Spec-to-Test Mapping (new) added per F2.
3. Governance-adoption regression test added to § Test And Verification Plan per F2.
4. § Acting-Prime Compatibility Contract (new) added per F3.
5. Test-file path references updated to post-rename `platform_tests/scripts/` paths (renamed in commit `a641f622`).
6. Status line changes from NEW to REVISED.
7. New § Codex Findings Addressed (above) and § Carry-Forward Statement (this section).

Specifically carried forward unchanged:

- Summary, Target Paths, Problem Statement, Proposed Change (Slices A/B/C/D), Non-Goals, Owner Decisions / Input, Implementation Plan, Risk And Rollback (with note about new compatibility-contract risk row).

## Specification Links

Re-cited explicitly per `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`. The three new role-governance citations (per F1) appear at the top so reviewers can find them quickly. All cross-cutting and protocol specs carry forward from `-001`.

- `GOV-ACTING-PRIME-BUILDER-001` v1 (verified, governance) — "Codex acts as Prime Builder while canonical Prime Builder is unavailable." **Disposition: PRESERVED unchanged.** The MemBase spec text remains as is. The proposal reinterprets `.claude/rules/acting-prime-builder.md` narrative wording to clarify that the active operating role for any harness is read from `harness-state/role-assignments.json`, not from the rule-file narrative. The historical/provenance framing of acting-Prime in the rule file is consistent with the MemBase spec's "while canonical Prime Builder is unavailable" condition — both describe a compatibility/legacy state, not an authoritative third role. No formal MemBase mutation is performed; the spec row at `groundtruth.db` is untouched.
- `GOV-HARNESS-ROLE-PORTABILITY-001` v1 (verified, governance) — "Prime Builder and Loyal Opposition are portable harness-assigned roles." **Disposition: PRESERVED unchanged.** The proposal directly affirms the portability principle: any harness can take either role; role assignment attaches to harness ID via `harness-state/role-assignments.json`. The "operating role" terminology clarification in Slice C aligns with this spec's portability framing.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` v1 (verified, governance) — "GT-KB installs must prepare capable harnesses for Prime Builder and Loyal Opposition roles." **Disposition: PRESERVED unchanged.** The proposal does not modify install-configuration requirements. The clarification that `harness-state/role-assignments.json` is the role record source (not `.claude/rules/prime-builder-role.md`) is consistent with this spec's two-role install model.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal is filed through the file bridge and must preserve `bridge/INDEX.md` as canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites governing specifications and maps tests to them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — implementation verification maps role/session behavior claims back to concrete tests and parity checks; § Spec-to-Test Mapping provides the mapping.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all proposed files are GT-KB platform or governance artifacts within `E:\GT-KB`; no live dependency, verification target, or generated artifact may be sourced from outside the project root. The proposal touches only in-root paths; no live dependency on Agent Red or other separate-project artifacts.
- `.claude/rules/file-bridge-protocol.md` — defines proposal, review, implementation report, and verification flow.
- `.claude/rules/codex-review-gate.md` — requires bridge review before implementation and substantive specification linkage.
- `.claude/rules/operating-model.md` — defines the Prime Builder to Loyal Opposition implementation lifecycle.
- `.claude/rules/operating-role.md` — defines durable harness identity and role assignment semantics.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — role/session terminology changes are durable governance-facing artifacts, not casual wording edits.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserve durable artifacts and explicit lifecycle states.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — role/session terminology changes cross the artifact lifecycle threshold.
- `GOV-ARTIFACT-APPROVAL-001` — formal/narrative authority changes require owner-visible approval evidence when in protected scope.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — protected artifact writes must satisfy the approval hook/evidence model.
- `GOV-SESSION-SELF-INITIALIZATION-001` — startup must disclose role/governance stance correctly.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` — Prime Builder startup focus choices must remain role-correct and not be shown in Loyal Opposition mode.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — any new canonical term should be placed where agents already read terminology.
- `.claude/rules/canonical-terminology.md` — glossary source for harness, harness identity, role assignment, Prime Builder, Loyal Opposition, session scope, and proposed session lane terminology.
- `config/governance/narrative-artifact-approval.toml` — protected narrative-artifact path and packet schema authority.
- `bridge/gtkb-role-session-lifecycle-simplification-001.md` — predecessor NEW proposal.
- `bridge/gtkb-role-session-lifecycle-simplification-002.md` — Codex NO-GO triggering this REVISED-1.

## Prior Deliberations

Carried forward from `-001` with additions:

- `DELIB-0830`, `DELIB-0831`, and `DELIB-0832` — role portability and durable harness identity decisions. `DELIB-0831` directly grounds `GOV-HARNESS-ROLE-PORTABILITY-001`.
- `DELIB-S324-PB-INTERROGATION-DIRECTIVE` — Prime Builder interrogative default.
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` — session scope and placement framing.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` and `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` — current Codex hook parity stance.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-09-14-20-ROLE-SESSION-LIFECYCLE-REVIEW.md` — direct advisory report.
- **Codex NO-GO at `bridge/gtkb-role-session-lifecycle-simplification-002.md` (2026-05-09)** — surfaced F1/F2/F3 addressed in this REVISED-1.
- `DELIB-S310-ROLE-DEFINITION-ASSESSMENT` — prior role-definition assessment (helper-search surfaced; relevant context).
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` — role-intent/startup role-confusion context.
- `DELIB-0896` / `DELIB-1165` — durable-role bridge-poller separation thread context.

## Owner Decisions / Input

Carried forward from `-001` § Owner Decisions / Input (verbatim):

> Owner-visible input in this session:
> - The owner reviewed the Loyal Opposition role/session lifecycle recommendation and said: "That is a well-considered proposal. Thank you."
> - Codex replied that this would be treated as positive feedback, not formal approval to mutate role artifacts.
> - The owner then said: "Please proceed."
>
> Interpretation: this authorizes filing this bridge proposal. It does not authorize protected narrative-artifact writes, formal artifact mutation, deployment, or bypassing the bridge review/verification cycle. Implementation must collect any required protected-artifact approval packet before writing protected narrative artifacts.

Additional owner input at S340 (2026-05-11): owner explicitly directed Prime Builder to revise this thread to add the three missing spec citations identified by Codex F1, alongside the broader F2/F3 fixes Codex laid out in the GO-able Revision Path. This REVISED-1 is the direct consequence; no additional per-finding owner decisions are required for review.

The protected narrative-artifact approval-packet requirement carries forward unchanged: implementation must collect approval-packet evidence for `.claude/rules/*.md` and `AGENTS.md` writes per `config/governance/narrative-artifact-approval.toml`.

## Problem Statement

(Carry-forward from `-001` unchanged.)

The active implementation has a clearer role model than some of the visible artifacts now express. Runtime facts: `harness-state/harness-identities.json` assigns persistent harness IDs; `harness-state/role-assignments.json` is the live role source of truth; `scripts/harness_roles.py` resolves roles from that map; `scripts/session_self_initialization.py` renders role-specific startup; `config/agent-control/harness-capability-registry.toml` binds capabilities to `prime-builder`/`loyal-opposition`/both. Visible-artifact drift: `.claude/rules/prime-builder-role.md` still calls itself the current role record; `acting-prime-builder` remains visible as a role profile; startup and rule text do not clearly separate operating role from session focus/work subject/session lane.

## Proposed Change

(Slices A/B/C/D carry forward from `-001` unchanged.)

### Slice A — Role Authority Wording Cleanup

Update active narrative surfaces to consistently state: live role assignment source is `harness-state/role-assignments.json`; `.claude/rules/prime-builder-role.md` and `.claude/rules/loyal-opposition.md` are behavior contracts (not assignment records); `.claude/rules/operating-role.md` is human-readable guidance (not a competing role source); no markdown rule file can override the durable role assignment map.

### Slice B — Acting Prime Builder Classification

Classify `acting-prime-builder` as historical/provenance language. Implementation per the compatibility contract in § Acting-Prime Compatibility Contract below (Codex's Option A from `-002` F3 recommendation).

### Slice C — Session Lane Terminology

Add glossary and startup terminology clarification distinguishing `operating role` (authority-bearing harness role; `prime-builder` or `loyal-opposition`), `session lane` (non-authority work classification — research, architecture, implementation, quality engineering, operations/release, documentation, governance stewardship), `session focus` (owner-facing startup selection), and `work subject/session scope` (root + write-boundary context). Explicit rule: session lanes inherit authority from the current operating role.

### Slice D — Startup And Test Alignment

Update startup rendering and tests only as needed to avoid implying lanes are durable roles. Prime Builder focus options may reference lanes; Loyal Opposition still does not present the Prime focus menu.

## Acting-Prime Compatibility Contract

Per Codex `-002` F3 Recommended Action option (a), this revision selects the **legacy-accepted compatibility path** for `acting-prime-builder`. The contract:

### Behavior

1. **Role-switch commands cannot SET `acting-prime-builder`.** `scripts/harness_roles.py`'s role-assignment command (and any future role-switch UI) MUST reject `acting-prime-builder` as a target role. Only `prime-builder` and `loyal-opposition` are valid SET targets.

2. **Existing `acting-prime-builder` values in `harness-state/role-assignments.json` ARE read but labeled legacy.** If the durable role-map already contains `acting-prime-builder` for a harness ID (because that value was set in a prior session or by an explicit owner-directed legacy-role-switch operation), `scripts/harness_roles.py` reads it as a valid current role for that harness — preserving backward compatibility — but startup rendering MUST label it as "compatibility/provenance" not "active operating role."

3. **`scripts/session_self_initialization.py`'s `ROLE_PROFILES['acting-prime-builder']` profile continues to load.** Its `role_mapping_source` continues to reference `.claude/rules/acting-prime-builder.md` for narrative continuity. Startup rendering for the acting-Prime profile MUST explicitly state the compatibility/provenance interpretation: this profile reflects a historical authority arrangement (Codex-as-acting-Prime when canonical Prime Builder was unavailable) and is not a new role-switch target.

4. **No migration of existing role-map values is performed in this slice.** Legacy values flow through the compatibility path unchanged. If a future owner directive requests retirement of the compatibility path, that becomes a separate bridge proposal.

### Spec-derived tests for the contract

- **T-compat-1:** `scripts/harness_roles.py` set-role rejects `acting-prime-builder` as a target. Pytest function in `platform_tests/scripts/test_harness_roles.py` (or new test file). Linked spec: `GOV-HARNESS-ROLE-PORTABILITY-001` (two-role canonical set).
- **T-compat-2:** `scripts/harness_roles.py` reads an existing `acting-prime-builder` value without raising. Linked spec: `GOV-ACTING-PRIME-BUILDER-001` (legacy compatibility framing).
- **T-compat-3:** Startup rendering for the `acting-prime-builder` profile contains the compatibility/provenance label. Pytest function in `platform_tests/scripts/test_session_self_initialization.py`. Linked spec: `GOV-SESSION-SELF-INITIALIZATION-001` (correct disclosure).
- **T-compat-4:** `ROLE_PROFILES` enumeration in `scripts/session_self_initialization.py` retains the `acting-prime-builder` profile (test asserts the profile is loadable and references the rule file). Linked spec: `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` (install-time profile set).

## Non-Goals

(Carry-forward from `-001` unchanged.)

- Do not change live role assignment records except through existing owner-directed role-switch path.
- Do not add research/operations/quality engineering/documentation/architecture/governance as durable operating roles.
- Do not weaken the Prime Builder to Loyal Opposition bridge protocol.
- Do not change bridge statuses or status ownership.
- **Do not modify any of the three role-governance MemBase specs** (`GOV-ACTING-PRIME-BUILDER-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`). Their disposition is PRESERVED unchanged per F1.
- Do not perform full primer consolidation in this proposal.
- Do not re-enable retired OS pollers or the retired smart poller.

## Implementation Plan

(Carry-forward from `-001` with additions for F3.)

1. Inventory all active references that call a markdown file the role source of truth or imply `acting-prime-builder` is a normal durable role.
2. Draft minimal wording changes to `.claude/rules/prime-builder-role.md`, `.claude/rules/acting-prime-builder.md`, `.claude/rules/operating-role.md`, `AGENTS.md`, and `.claude/rules/canonical-terminology.md`. Preserve the three role-governance specs' meaning per F1 dispositions.
3. Generate required narrative-artifact approval packet evidence for every protected narrative artifact that will be edited.
4. Update `scripts/session_self_initialization.py` to add the compatibility/provenance label for the `acting-prime-builder` profile per § Acting-Prime Compatibility Contract.
5. Update `scripts/harness_roles.py` to reject `acting-prime-builder` as a SET target while continuing to accept it as a READ value (per F3 contract).
6. Update tests in `platform_tests/scripts/` (renamed from `tests/scripts/` per commit `a641f622`) per § Test And Verification Plan.
7. Run targeted tests and parity checks.
8. File an implementation report carrying forward spec links, approval-packet evidence, file changes, and test results.

## Spec-to-Test Mapping

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Spec | Verifies | Test |
|---|---|---|
| `GOV-ACTING-PRIME-BUILDER-001` | Existing rule-file narrative references the spec; legacy role-map values are read correctly | `test_acting_prime_builder_rule_maps_prime_skill_labels_to_assigned_role` (existing) + T-compat-2 (new) |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | Portability principle preserved; role-switch only accepts portable roles (`prime-builder`/`loyal-opposition`) | T-compat-1 (new) + existing `test_harness_roles.py` role-switch coverage |
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` | Install-time role-profile set unchanged | T-compat-4 (new) + existing `test_session_self_initialization.py` ROLE_PROFILES coverage |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Startup disclosure correctly labels operating role and compatibility/provenance states | T-compat-3 (new) + existing `test_session_self_initialization.py` |
| `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` | Prime Builder startup focus options remain role-correct | Existing `test_session_self_initialization.py` Prime-focus-menu coverage |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge thread reflects canonical workflow state | `bridge/INDEX.md` entry visible in this revision |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Specification linkage complete | Applicability + clause preflights pass on this `-003` (run post-write) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Spec-to-test mapping present | This § Spec-to-Test Mapping |

## Test And Verification Plan

Required before implementation report (post-rename paths per commit `a641f622`):

- `python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short` (if file exists at new path; otherwise the existing harness-parity script invocation below covers it)
- **`python -m pytest platform_tests/scripts/test_groundtruth_governance_adoption.py::test_acting_prime_builder_rule_maps_prime_skill_labels_to_assigned_role -q --tb=short` (NEW in REVISED-1 per F2)** — this is the load-bearing regression that protects the role-governance MemBase spec references in `.claude/rules/acting-prime-builder.md`. Must remain green after the wording cleanup.
- `python -m pytest platform_tests/scripts/test_harness_roles.py -q --tb=short` (covers T-compat-1, T-compat-2 per F3 contract)
- `python scripts/check_harness_parity.py --all --markdown`
- `python scripts/check_codex_hook_parity.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-session-lifecycle-simplification`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-session-lifecycle-simplification`

If protected narrative artifacts are modified and staged, also run:

- `python scripts/check_narrative_artifact_evidence.py`

### Verification expectations

- No file other than `harness-state/role-assignments.json` claims to be the current role record.
- `prime-builder` and `loyal-opposition` remain the only normal durable operating roles.
- `acting-prime-builder` is legacy-accepted on READ, rejected on SET, and labeled compatibility/provenance in startup rendering (per § Acting-Prime Compatibility Contract).
- All three role-governance MemBase specs (`GOV-ACTING-PRIME-BUILDER-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`) remain unchanged (no row mutations in `groundtruth.db`).
- The existing governance-adoption regression test continues to pass without modification (per F2 — the test asserts the DELIB and GOV references in `.claude/rules/acting-prime-builder.md`; the wording cleanup must preserve those references).
- Session lanes are described as non-authority classifications that inherit the current operating role's permissions.
- Harness parity remains PASS.

## Risk And Rollback

(Carry-forward from `-001` with one new risk row for F3 compatibility contract.)

### Risks

- Over-editing role files could accidentally weaken Prime Builder or Loyal Opposition authority boundaries.
- Removing `acting-prime-builder` too aggressively could break historical tests or startup expectations. **Mitigated by the legacy-accepted compatibility contract per F3.**
- Editing protected narrative artifacts without approval-packet evidence would violate the narrative-artifact approval gate.
- **NEW (per F3):** The compatibility contract could be misimplemented such that `acting-prime-builder` becomes settable through some indirect path (e.g., editing `harness-state/role-assignments.json` directly bypasses the role-switch command). Mitigation: T-compat-1 asserts the role-switch command rejects the target; direct file edits are the owner's responsibility per the existing role-switch governance (no new gate added for direct file edits, which is a separate concern outside this slice's scope).

### Rollback

- Revert narrative wording and startup/test changes in a scoped rollback commit.
- Leave `harness-state/role-assignments.json` untouched unless a separate owner-directed role-switch operation is requested.
- If `acting-prime-builder` legacy-accepted compatibility causes regressions, restore the prior behavior (accepting it as a normal role-switch target) and document the regression as a separate bridge thread.

## Recommended Commit Type

(Carry-forward from `-001`.) `docs:` if changes are limited to role/rule wording and tests; `refactor:` if `scripts/session_self_initialization.py` role-profile logic is materially changed.

## Pre-Filing Applicability Preflight

Will be rerun after this REVISED-1 is written and INDEX is updated. Expected outcome: pass (this revision adds three governance spec citations and content patterns that should match the existing detection regex set; the cross-cutting specs from `-001`'s passing preflight are all carried forward).

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-session-lifecycle-simplification
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-session-lifecycle-simplification
```

Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, `Blocking gaps (gate-failing): 0`.

## Result

`REVISED` — awaiting Codex review per `-002`'s GO-able Revision Path.

Codex review obligations per `.claude/rules/codex-review-gate.md` and `-002`'s § GO-able Revision Path checklist:

1. Confirm the three role-governance specs are now cited in § Specification Links with explicit disposition statements (F1).
2. Confirm the spec-to-test mapping connects the three specs to concrete tests (F1 + F2).
3. Confirm the existing governance-adoption regression test is in § Test And Verification Plan (F2).
4. Confirm § Acting-Prime Compatibility Contract specifies behavior for durable role-map reads, not only role-switch commands (F3).
5. Confirm protected narrative-artifact approval-packet requirement is preserved (`-002` § Confirmations item 4).
6. Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-session-lifecycle-simplification`.
7. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-session-lifecycle-simplification`.
8. Issue `GO` if all five revision-path items are satisfied and preflights pass; otherwise `NO-GO` with specific finding.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
