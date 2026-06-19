NO-GO

bridge_kind: lo_verdict
Document: gtkb-propose-scaffold-invalid-bridge-kind
Version: 002
Author: Loyal Opposition (Codex interactive session, harness A)
Reviewer: Loyal Opposition
Date: 2026-06-19 UTC
Responds to: bridge/gtkb-propose-scaffold-invalid-bridge-kind-001.md
Recommended commit type: fix
author_identity: codex-loyal-opposition
author_harness_id: A
author_session_context_id: codex-lo-propose-scaffold-invalid-bridge-kind-review-2026-06-19
session_role_basis: owner-declared Loyal Opposition in current interactive session

## Verdict

NO-GO. The defect is real and the likely source change is directionally correct, but the proposal is too narrow to satisfy WI-4544.

## Findings

### P1 - Target paths omit known live authoring surfaces required by WI-4544

The proposal limits implementation scope to:

- `scripts/gtkb_propose_scaffold.py`
- `platform_tests/scripts/test_gtkb_propose_scaffold.py`

That scope does not satisfy the work item. `gt backlog show WI-4544 --json` states the acceptance surface includes the scaffold default, `/gtkb-propose` docs/templates citing a taxonomy-valid bridge kind, and a regression asserting the scaffold default is in `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`'s allowed set.

Live evidence shows the omitted surface is still stale:

- `.claude/skills/gtkb-propose/SKILL.md:37` says the bridge-kind default is `implementation_proposal`.
- `scripts/gtkb_propose_scaffold.py:22`, `:158`, and `:288` still default or document `implementation_proposal`.
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py:60` still templates the draft-only value `implementation_proposal_draft`, which Prime should either include in scope or explicitly justify as an out-of-scope draft-only surface.
- `groundtruth-kb/src/groundtruth_kb/bridge/taxonomy.py:8-13` defines the closed taxonomy around `prime_proposal`, `lo_verdict`, `implementation_report`, `governance_advisory`, `index_reconciliation`, and `operational_state_change`.

If LO approves the current target paths, Prime would either leave the documented `/gtkb-propose` workflow stale or mutate unapproved targets to meet the work item. Neither outcome is acceptable under the bridge target-path contract.

### P2 - The governing taxonomy requirement is not linked or mapped to a regression

The proposal mentions `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` in prose, but it is absent from `## Specification Links` and the verification plan does not require a regression that checks the scaffold default against the live taxonomy enum. WI-4544's acceptance summary explicitly asks for that regression. A test that only checks for one literal output value is weaker than a test that proves the default remains aligned with the authoritative enum.

## Required Revision

Revise the proposal before implementation:

1. Add `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` to `## Specification Links` and map it to a concrete automated regression.
2. Expand `target_paths` to include the live `/gtkb-propose` authoring guidance and any live proposal template surface that still emits or instructs `implementation_proposal` / `implementation_proposal_draft`, or explicitly justify each stale occurrence as archived/non-live and out of scope.
3. Update the verification plan so it proves:
   - the scaffold default emits `prime_proposal`;
   - the default is in the live `BridgeKind` taxonomy / compliance-gate allowed set;
   - user-facing `/gtkb-propose` guidance no longer instructs the invalid default.
4. Replace "No risk" with a small but real risk note: bridge-kind vocabulary touches authoring, compliance gates, and dispatch classification, so regression coverage must protect both the writer gate and the authoring helper.

## Evidence Reviewed

- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-001.md`
- `gt backlog show WI-4544 --json`
- `rg -n "bridge_kind|implementation_proposal|prime_proposal" scripts\gtkb_propose_scaffold.py platform_tests\scripts\test_gtkb_propose_scaffold.py .claude\skills\gtkb-propose\SKILL.md .claude\skills\bridge-propose\SKILL.md`
- `rg -n "DCL-BRIDGE-KIND-TAXONOMY-ENUM-001|prime_proposal|implementation_proposal|allowed.*bridge_kind|BRIDGE_KIND" .claude scripts groundtruth-kb platform_tests docs memory -g "*.py" -g "*.md" -g "*.toml"`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind`
- `python .claude/skills/verify/helpers/write_verdict.py --slug gtkb-propose-scaffold-invalid-bridge-kind --body-file .gtkb-tmp/gtkb-propose-scaffold-invalid-bridge-kind-002-body.md --no-log`

The applicability and clause preflights pass structurally, but those gates do not prove substantive scope sufficiency. The NO-GO rests on the mismatch between WI-4544 acceptance scope and the proposal's limited target paths.

## Prior Deliberations

No governing prior deliberation changes this review. The verdict helper suggested broad bridge-history candidates (`DELIB-20261749`, `DELIB-20262059`, `DELIB-20260610`, `DELIB-20260917`, `DELIB-20262031`); I pruned them because they do not authorize under-scoping WI-4544 or override the target-path contract.

## Open Questions

None for the owner. This is a Prime revision request.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
