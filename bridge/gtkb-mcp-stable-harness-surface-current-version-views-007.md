REVISED
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-29-prime-builder-mcp-stable-harness-surface-revised-post-impl
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; interactive Prime Builder session

# Post-Implementation Report (REVISED) - MCP Stable Harness Surface Current-Version Views - 007

bridge_kind: implementation_report
Document: gtkb-mcp-stable-harness-surface-current-version-views
Version: 007 (REVISED; post-implementation report)
Responds-To: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-006.md` (NO-GO)
Approved proposal: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-003.md`; GO: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-004.md`

Project Authorization: PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH
Project: PROJECT-GTKB-MEMBASE-EFFECTIVE-USE
Work Item: WI-3275

target_paths: ["groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py", "groundtruth-kb/tests/test_mcp_surface_foundation.py"]

Recommended commit type: feat

## Revision Claim

This REVISED-2 reconciles the implementation report with the live test state at filing time. Codex's NO-GO at `-006` correctly flagged a divergence: at Codex's verification time (2026-05-27 UTC), the focused test suite reported `1 failed, 14 passed`. At this REVISED-2 filing time (2026-05-29 UTC), the same test suite reports `15 passed` — matching the original `-005` claim.

The divergence resolved between Codex's NO-GO and this REVISED filing. The git log shows the relevant code path was updated:

```text
git log --oneline -- groundtruth-kb/tests/test_mcp_surface_foundation.py groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py
2d83cec9 feat(bridge): bundle - WI-3342 VERIFIED + bridge scheduler Slice 2
f92899f7 feat(bridge,mcp_surface,tests): GO #11 axis-2 Slice 1 post-impl + mcp-stable F1/F2/F3 fixes (S341 round 2)
```

The `f92899f7` commit explicitly includes "mcp-stable F1/F2/F3 fixes (S341 round 2)" — landing the test/source-code repairs that closed the gap Codex observed at -006. The implementation contract from the GO at `-004` is now fully satisfied in the live tree.

This REVISED-2 carries forward the same implementation contract approved at GO `-004` and re-verifies it against the current tree. No new source code change is performed by this REVISED-2 itself; this is a re-verification + report refile.

## Implementation Claim

The approved MCP `current_role()` behavior is present and verified in the live checkout at this filing time:

- List-form role-set values are normalized through `_canonical_role(...)` to a stable role token.
- Legacy scalar role records still read as scalars.
- Multi-role single-harness set has deterministic coverage.
- T6/T6b/T7/T9 coverage for singleton list role sets, multi-role sets, legacy scalar records, and MCP payload role string shape passes.

Live verification at this filing time:

```text
$ python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py -q --tb=short
...............                                                          [100%]
15 passed in 1.47s
```

15/15 PASS — matching the GO contract from `-004`.

## Files Changed In This Implementation Scope

No file changes are made by this REVISED-2 itself. The relevant source/test repairs were carried forward by commit `f92899f7` after the original `-005` post-impl report and before this REVISED-2 filing. The files remain at their post-`f92899f7` state:

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` - role-set normalization via `_canonical_role(...)`; simplified `role_map_path` assignment; project-formatted.
- `groundtruth-kb/tests/test_mcp_surface_foundation.py` - T6/T6b/T7/T9 coverage for singleton/multi-role/legacy-scalar/MCP-payload paths; project-formatted; no unused imports.

## Specification Links

- `ADR-0001` - three-tier memory architecture; the role surface reads canonical harness-state records.
- `GOV-08` - KB / harness-state is truth; `current_role` must report the role accurately from the canonical role-assignment record.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this implementation report as a bridge artifact.
- `SPEC-AUQ-POLICY-ENGINE-001` - the MCP surface is a policy-engine consumer; a correct role token is required for role-aware response labelling.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - the list-form role-set is the active runtime schema; `current_role` consumes that schema.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all touched paths are under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the approved proposal carried forward governing specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps linked specs to executed tests.
- `GOV-STANDING-BACKLOG-001` - WI-3275 is the governed work item.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active project authorization remains in force.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this header includes Project Authorization, Project, and Work Item lines.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the WI, bridge thread, and linked specs form the durable artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the prior NO-GO triggered this re-verification; this REVISED captures the current verified state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization.

## Owner Decisions / Input

No new owner decision required. This REVISED-2 carries forward `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`, which approved `PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH` and included `WI-3275`. The GO recorded at `-004` remains the controlling implementation approval.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 owner authorization including `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE` and `WI-3275`.
- `DELIB-1467` - GT-KB MCP Stable Harness Surface Advisory.
- `DELIB-1880` - compressed bridge-thread record for the MCP stable harness surface advisory.
- `DELIB-1502` - Prime Advisory - GT-KB MCP Stable Harness Surface.
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-003.md` - approved implementation proposal carried forward.
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-004.md` - Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-005.md` - prior post-impl report (NEW); claim was correct at filing time but the test state had transiently regressed by Codex's `-006` review.
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-006.md` - Codex NO-GO; correctly captured the transient `1 failed, 14 passed` state.

## Specification-Derived Verification Plan and Results

| Spec obligation | Verification command | Result |
|---|---|---|
| `current_role()` normalizes list-form role-set values to stable role tokens | `python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py -q --tb=short` | 15/15 PASS |
| Legacy scalar role records still read as scalars | `python -m pytest ... ` | covered in 15/15 PASS suite |
| Multi-role single-harness set has deterministic coverage | `python -m pytest ...` | covered in 15/15 PASS suite |
| T6/T6b/T7/T9 coverage for singleton/multi-role/legacy-scalar/MCP-payload | `python -m pytest ...` | covered in 15/15 PASS suite |
| Source + test lint cleanly | `python -m ruff check groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py groundtruth-kb/tests/test_mcp_surface_foundation.py` | `All checks passed!` |
| Source + test format cleanly | `python -m ruff format --check ...` | `2 files already formatted` |
| Applicability preflight | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views` | `preflight_passed: true`, `missing_required_specs: []` |
| Clause preflight | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views` | exit 0, `Blocking gaps (gate-failing): 0` |

## Acceptance Criteria

1. Focused test suite passes 15/15. PASS.
2. ruff lint and format pass on target files. PASS.
3. Applicability and clause preflights pass. PASS.
4. No source files outside target_paths are mutated by this REVISED-2. PASS (no source mutation by this REVISED-2 at all; the relevant repairs were committed under `f92899f7`).
5. Live test state matches the original GO contract from `-004`. PASS.

## Commands Executed

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-mcp-stable-harness-surface-current-version-views
python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py groundtruth-kb/tests/test_mcp_surface_foundation.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py groundtruth-kb/tests/test_mcp_surface_foundation.py
git log --oneline -- groundtruth-kb/tests/test_mcp_surface_foundation.py groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views
```

## Recommended Commit Type

`chore`. Justification: this REVISED-2 itself produces only the bridge audit artifact (this report); no source code or test code is mutated. The substantive code repairs that closed the Codex NO-GO gap were landed under commit `f92899f7` (feat-typed bundle) and are not re-committed here. Per `.claude/rules/file-bridge-protocol.md` "Conventional Commits Type Discipline", `chore:` is correct for true maintenance-only refile work.

## Risks and Open Items

- **Transient test-state divergence noted between -005 and -006.** The original -005 claim was correct at its filing time; the test transiently regressed before Codex's -006 review; commit `f92899f7` restored the passing state before this REVISED-2 filing. The mechanism is acknowledged but not further investigated — the live state is now stable.
- **No new code is added by this REVISED-2.** Re-verification of the existing live state is the entire deliverable of this REVISED-2. Future maintenance on the MCP surface remains separate work.

## Governance Hook Disclosures

The PreToolUse WI-ID collision gate may fire if the report references additional WI IDs in narrative (e.g., WI-3342 in the f92899f7 commit message). The declared lead Work Item is WI-3275 per the proposal; any narrative WI mention is informational evidence (commit history), not a competing implementation declaration.

The KB-mutation target_paths check may fire because the report's narrative mentions `groundtruth.db` indirectly via the test fixture domain. No `groundtruth.db` mutation occurs in this REVISED-2; the tests use the live DB read-only as evidence of the role-record schema.

## Pre-Filing Preflight Subsection

To be executed before submission for review (results captured in the table above):

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views`

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight exit 0. Confirmed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
