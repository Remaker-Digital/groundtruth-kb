REVISED

bridge_kind: prime_proposal
Project Authorization: PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4214

Document: gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces
Version: 015
Supersedes: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-013.md
Responds-To: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-014.md (NO-GO)
Author: Prime Builder (Codex automation, harness A, acting Prime Builder for Keep Working PB)
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Recommended commit type: fix

author_identity: Codex Prime Builder automation
author_harness_id: A
author_session_context_id: 019e90d7-cd53-76b0-aba2-addddbb61ff8
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation, PowerShell, project root E:\GT-KB
author_role_authority_basis: Owner automation prompt "Keep Working PB" explicitly assigns Prime Builder work for this run. Durable registry still records harness A as Loyal Opposition, so this revision is limited to Prime-actionable bridge work and does not review this session's own artifacts.
author_metadata_source: live bridge INDEX scan, automation prompt, bridge_claim_cli claim record, and live thread show output.

# Slice 3 REVISED -015 - five-site startup test alignment

## Revision Note

This revision closes Codex NO-GO `-014` P1. The runtime-fix direction from
`-013` remains intact: `scripts/session_self_initialization.py::operating_role_path()`
should prefer `harness-state/harness-registry.json` when no explicit compat
path applies, while preserving the `GTKB_ROLE_ASSIGNMENTS_PATH` env override,
explicit `role_record_path`, and mirror fallback for project roots that do not
have a registry.

The defect in `-013` was the affected-test inventory, not the runtime design.
`-013` listed four assertion sites, but `-014` showed a fifth live assertion in
the startup `additionalContext` path. This revision updates the proposal,
test-sync inventory, target rationale, and verification plan to cover all five
affected assertion sites.

## Finding Response

### P1 - Proposal misses a fifth affected startup role-source assertion

Accepted. The fifth assertion is affected because
`_display_role_mapping_source()` calls `operating_role_path(...,
prefer_local=False)` for the same `REPO_ROOT` startup path. After the proposed
runtime change, that display source becomes
`harness-state/harness-registry.json`, so the additionalContext assertion must
be aligned with the same registry source as the other non-env-override tests.

Corrected affected-test inventory:

- `platform_tests/scripts/test_session_self_initialization.py:155`: startup model governance inventory currently checks for `role-assignments.json`; proposed alignment checks for `harness-registry.json`.
- `platform_tests/scripts/test_session_self_initialization.py:366`: durable operating-role discovery currently checks for `role-assignments.json`; proposed alignment checks for `harness-registry.json`.
- `platform_tests/scripts/test_session_self_initialization.py:584`: in-root authority path resolver currently equals `role-assignments.json`; proposed alignment equals `harness-registry.json`.
- `platform_tests/scripts/test_session_self_initialization.py:856`: Loyal Opposition role profile bridge disclosure currently equals `harness-state/role-assignments.json`; proposed alignment equals `harness-state/harness-registry.json`.
- `platform_tests/scripts/test_session_self_initialization.py:1690`: generated startup additionalContext currently contains `Role mapping source: harness-state/role-assignments.json`; proposed alignment contains `Role mapping source: harness-state/harness-registry.json`.

The env-override compatibility assertion around line 497 remains explicitly
unchanged. It sets `GTKB_ROLE_ASSIGNMENTS_PATH` to a temporary mirror fixture,
so the env override continues to win and the test continues to prove the
compatibility path.

## Implementation Claim

Close the Slice 3 startup role-source contradiction by aligning the dynamic
startup resolver with the already-landed static registry metadata. After the
implementation:

- normal startup display paths use `harness-state/harness-registry.json`;
- explicit `role_record_path` and `GTKB_ROLE_ASSIGNMENTS_PATH` remain higher
  precedence compatibility paths;
- project roots without a registry still fall back to the legacy mirror path;
- all five non-env-override startup test assertions are updated together; and
- the targeted regression suite still exercises the env-override compatibility
  path without changing its assertion.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` - registry as canonical role source-of-truth.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - startup/source reporting must not use a stale source-of-truth.
- `ADR-ROLE-STATUS-ORTHOGONALITY-001` - role/status orthogonality model.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - role-set schema authority.
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` - dispatch role semantics.
- `GOV-STANDING-BACKLOG-001` - WI-4214 backlog linkage.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization and target-path envelope.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol and INDEX canonicality.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - five affected assertion sites map to the linked requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project-linkage headers.
- `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, and `DCL-ARTIFACT-APPROVAL-HOOK-001` - narrative-artifact packet evidence is carried forward from the already-landed Slice 3 root-surface edits.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - every target path is under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact-oriented bridge governance.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` - startup reports the live registry path rather than a stale mirror source.
- `GOV-08` - MemBase-backed registry state remains the role source-of-truth.

## Owner Decisions / Input

- Owner AskUserQuestion on 2026-06-04 in session `029e1d12`: owner selected
  "Runtime fix + correct 4-site test alignment" for the runtime resolver path,
  preserving `L497` env-override compatibility. The fifth assertion was not
  known at that moment; this revision is the same runtime path plus the
  additional affected assertion found by LO.
- Owner AskUserQuestion on 2026-06-04 in session `029e1d12`: owner selected
  "Cite SLICE-1 PAUTH + note bridge-protocol path is operative", acknowledging
  the PAUTH scope-summary tension and standing on the `-008` GO trail plus
  explicit LO validation as operative authorization evidence.
- Owner AskUserQuestion on 2026-06-03 in session `a47d634f`: owner selected
  "Drive Slice 3 to VERIFIED".
- S388 owner directive: complete the governed retirement before claiming
  registry sole authority.

No new owner input is required. This revision narrows to a test-inventory
correction discovered by Loyal Opposition and does not add a new implementation
class beyond the previously selected runtime-fix path.

## Requirement Sufficiency

Existing requirements sufficient. The change is still an implementation and
test-sync correction under the same registry source-of-truth requirements
cited by `-013`; no new or revised requirement is needed.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use generated or governed bridge text only; do not include credentials. | Credential scan before filing and commit. | |
| CQ-PATHS-001 | Yes | Keep every target under `E:\GT-KB` and inside declared `target_paths`. | Bridge preflight and implementation authorization validation. | |
| CQ-COMPLEXITY-001 | Yes | Keep runtime precedence logic local to `operating_role_path()` and preserve fallback branches. | Focused startup tests cover canonical and compat branches. | |
| CQ-CONSTANTS-001 | N/A | | | No new constants are proposed. |
| CQ-SECURITY-001 | Yes | Do not expand role-source resolution beyond existing in-root harness-state files and explicit env override. | Focused tests plus source review. | |
| CQ-DOCS-001 | Yes | Implementation report must carry forward this five-site scope correction. | Loyal Opposition bridge verification. | |
| CQ-TESTS-001 | Yes | Update all five affected assertions and preserve the env-override compatibility assertion. | Broad startup pytest lane and targeted role-source subset. | |
| CQ-LOGGING-001 | N/A | | | Proposal does not change runtime logging. |
| CQ-VERIFICATION-001 | Yes | Run focused tests plus ruff check and ruff format check on changed Python files. | Commands and observed results in implementation report. | |

## Prior Deliberations

- `DELIB-2750` - prior Loyal Opposition review of the role-assignments mirror Slice 1 seed repoint.
- `DELIB-2799` - owner continuation authorization for WI-4214 role-assignments mirror retirement Slice 1.
- `DELIB-20260629` - owner decision authorizing expansion of the role-rule-orthogonality mirror-retirement path.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` - role/status orthogonality and canonical registry model.
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-008.md` - GO on the Slice 3 scope-reconciliation proposal.
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-012.md` - prior NO-GO that required a runtime fix instead of test-only alignment.
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-014.md` - current NO-GO; this revision accepts and closes its fifth-assertion finding.

## target_paths

- `scripts/session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-015.md`
- `bridge/INDEX.md`
- `.gtkb-state/**`

All target paths are in root under `E:\GT-KB`. No MemBase mutation and no new
protected narrative-artifact edit are in scope for this revision.

## Spec-Derived Verification Plan

- `REQ-HARNESS-REGISTRY-001` plus `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: run `python -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short`; expected result is all collected tests pass, five affected assertion sites align to `harness-registry.json`, and the env-override compatibility assertion around line 497 remains unchanged.
- `DCL-REPORTING-SURFACE-FRESH-READ-001`: run `python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short -k "harness_role_assignment_map_is_startup_source_of_truth or startup_model_discovers_durable or startup_model_contains_role_governance or harness_local_authority_paths_resolve_in_root or loyal_opposition_role_profile_reports_active_bridge or startup_report_contains_generated_additional_context"`; expected result is targeted startup role-source tests pass under the new resolver and five-site test alignment.
- Slice 3 previously-landed root/sentinel surfaces: run `python -m pytest platform_tests/scripts/test_mirror_retirement_root_surfaces.py platform_tests/scripts/test_index_role_intent_sentinel.py -q --tb=short`; expected result is pass, proving the earlier root/sentinel retirement remains intact.
- Python lint and format gates: run `ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py` and `ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py`; expected result is both pass.
- `GOV-ARTIFACT-APPROVAL-001` carried-forward narrative evidence: run `python scripts/check_narrative_artifact_evidence.py --paths CLAUDE.md AGENTS.md`; expected result is pass.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: run `python scripts/implementation_authorization.py begin --bridge-id gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces`; expected result is authorization packet minted from latest GO and accepted target paths before implementation mutation.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces`; expected result is applicability preflight passes and clause preflight exits 0.

## Bridge INDEX Self-Check

This revision is filed under the existing document entry by inserting:

```text
REVISED: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-015.md
```

above `NO-GO: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-014.md`.
No prior bridge version is deleted or rewritten. `bridge/INDEX.md` remains the
canonical workflow state.

## Risk And Rollback

- Risk: there may be a sixth affected assertion. Mitigation: the revision uses
  LO's full grep evidence and the verification plan reruns both the broad
  session-startup test file and the targeted role-source subset.
- Risk: the targeted `-k` expression includes a name that has shifted. Mitigation:
  the broad file-level test command remains the primary gate; the targeted
  command is a focused diagnostic lane.
- Risk: PAUTH scope-summary wording remains narrower than the later bridge
  thread path. Mitigation: the owner already selected the bridge-protocol path
  as operative, and `-014` reconfirmed the PAUTH includes WI-4214 and allows
  source/test mutation classes.
- Rollback: because this revision is proposal-only, rollback is another
  append-only bridge revision. No source mutation is performed by this filing.

## Pre-Filing Preflight Confirmation

Candidate filing uses `.claude/skills/bridge/helpers/revise_bridge.py file`,
which runs `bridge_applicability_preflight.py --content-file` and
`adr_dcl_clause_preflight.py --content-file` before writing the live bridge
file or updating `bridge/INDEX.md`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.