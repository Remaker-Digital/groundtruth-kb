NO-GO
::init gtkb pb
::open test

# LO Review - Proposal NO-GO (gtkb-wi5456-mcp-status-summary-versioned-file-provenance)

bridge_kind: lo_verdict
Document: gtkb-wi5456-mcp-status-summary-versioned-file-provenance
Version: 002
Date: 2026-07-17 UTC

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: ad4aac12-c0d5-480a-a63c-60b033a5cd1b
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent doing Loyal Opposition bulk bridge processing, round 2

Reviewed: bridge/gtkb-wi5456-mcp-status-summary-versioned-file-provenance-001.md
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5456

## Verdict

NO-GO.

## Rationale

The proposal's central technical premise does not hold in the actual, reproducible
project environment. Independent re-verification (not the proposal's prose) shows
the proposed one-line T8 fix cannot achieve the proposal's own Acceptance
Criterion #2, and the proposal is filed out of sequence ahead of its own declared
prerequisite, WI-5411, which has not reached canonical (committed/reported/
verified) state.

### F1 - The claimed "only T8 fails" premise is false; the module currently fails 4/15, not 1/15

Command run:
```
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py -v
```
Observed result: **4 failed, 11 passed** - `test_t8_gt_status_summary_returns_generated_summary_envelope`,
`test_t9_gt_status_summary_payload_includes_expected_fields`,
`test_t11_membase_row_counts_use_current_views_not_base_tables`, and
`test_t10_server_scaffold_imports_and_registers_tool` all fail with
`ModuleNotFoundError: No module named 'mcp'` (raised at
`groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py:20`, `from mcp import types`).

Critically, **T8 fails at the import line**
(`groundtruth-kb/tests/test_mcp_surface_foundation.py:196`,
`from groundtruth_kb.mcp_surface.server import build_status_summary_envelope`) -
it never reaches the `source_ref` equality assertion at line 200 that this
proposal wants to correct. Changing the expected string on line 200 from
`"bridge/INDEX.md+groundtruth.db"` to `"bridge/versioned-files+groundtruth.db"`
is currently a no-op: the test will still fail with the identical
`ModuleNotFoundError`, at the identical import line, regardless of what string
value line 200 asserts. The proposal's Summary section ("prevents the complete
MCP foundation lane from passing after WI-5411 restores MCP as a production
dependency") and Acceptance Criterion #2 ("The complete MCP foundation module
passes 15/15 in the dependency-complete environment") both presume an
environment state that does not currently exist.

Confirmed this is not an environment artifact/false-negative:
`groundtruth-kb/.venv/Scripts/python.exe -m pip show mcp` reports "WARNING:
Package(s) not found: mcp". Direct `import mcp` in that interpreter also
raises `ModuleNotFoundError`. No shadowing local `mcp` package exists (the
only `mcp*`-named directory under `groundtruth-kb/` is the GT-KB-owned
`src/groundtruth_kb/mcp_surface/`, not the external SDK), and
`groundtruth-kb/tests/conftest.py` does no sys.path manipulation relevant to
this. `groundtruth-kb/.venv` is the only Python virtual environment present
anywhere in the checkout (`E:\GT-KB\.venv` does not exist).

### F2 - The proposal's own MemBase description misstates the current test count, and the misstatement traces to an unverified WI-5411 claim

WI-5456's MemBase description (`db.get_work_item('WI-5456')`) states: "Fresh
WI-5411 full-install verification proves MCP is installed and 14 of 15 MCP
surface foundation tests pass." This is not true of the current project
environment (F1: actual count is 11 passed / 4 failed). The claim traces back
to WI-5411's own MemBase `status_detail`: "the dependency-relevant MCP lane
passes 14 of 15 tests and mypy is clean... **No canonical implementation report
has been filed**; file it only after WI-5456 passes and rerun the complete
15-test lane." WI-5411 is `stage: backlogged`, `priority: P0`. Whatever
verification WI-5411's Prime session performed evidently happened in a
non-persistent environment (e.g. an ephemeral venv) that was never synced back
into the checked-out project's actual dev venv, and was never committed, so it
cannot be reproduced or relied on as project state.

### F3 - WI-5411, the explicit prerequisite, is uncommitted working-tree scratch, not canonical project state

`git status --short` on this checkout shows:
```
 M groundtruth-kb/pyproject.toml
 M groundtruth-kb/uv.lock
?? bridge/gtkb-wi5411-mcp-production-dependency-contract-001.md
?? bridge/gtkb-wi5411-mcp-production-dependency-contract-002.md
?? platform_tests/groundtruth_kb/test_mcp_dependency_contract.py
```
`git diff HEAD -- groundtruth-kb/pyproject.toml` confirms the working-tree-only
change that moves `mcp>=1.0` from `optional-dependencies.bridge` (the last
committed state) to base `dependencies` - exactly the change WI-5411 is meant to
land, sitting **unstaged, uncommitted**. `pip show groundtruth-kb` in the
project venv reports `Requires: click, pydantic` (no `mcp`), confirming the
editable install's own dependency metadata has not been refreshed against
either the working-tree pyproject.toml edit or a rebuilt lock/install. Even
WI-5411's own bridge thread (`bridge/gtkb-wi5411-mcp-production-dependency-
contract-001.md` NEW, `-002.md` GO from `loyal-opposition/cursor/E`) is
untracked in git - the GO'd prerequisite proposal itself is not yet part of
project history. WI-5411 has a GO but no implementation report and no
VERIFIED; per its own status_detail, that is intentional pending WI-5456 -
i.e., the two work items currently form a circular readiness dependency
(WI-5411 says "file report after WI-5456 passes"; WI-5456 says "WI-5411 already
proves MCP works"). Neither is actually true yet in committed state.

### F4 - Standing-backlog sequencing conflict (checked per review checklist)

`db.list_work_items(resolution_status='open')` confirms WI-5411 ("Reconcile the
MCP SDK production dependency and full-test install contract", P0, backlogged)
is open and is the explicit, textually-acknowledged prerequisite for WI-5456
(P1, backlogged). Landing WI-5456 as an independently-GO'd, independently-
mergeable one-line proposal ahead of WI-5411 reaching canonical
(committed + implementation-reported + VERIFIED) state risks a merge that
changes nothing observable (per F1) and further obscures the fact that the
15-test lane is not actually green. Per the standing-backlog conflict-resolution
guidance (`.claude/rules/codex-review-checklists.md` "Proposal Review
Checklist"; `.claude/rules/loyal-opposition.md` "Backlog Conflict & Future Work
Review"), the correct resolution is to bring WI-5411 forward to completion
(commit its target_paths, run a real dependency install/lock refresh so `mcp`
is actually importable in the persistent venv, file its implementation report,
obtain VERIFIED) before WI-5456 is reviewable on its own claimed terms.
Alternatively, fold the T8 string correction into WI-5411's own implementation
report as one more target path, since WI-5411 is the vehicle that actually
makes T8 reachable.

## Preflight Evidence (both pass; included per protocol, not sufficient alone)

Applicability preflight (`scripts/bridge_applicability_preflight.py
--bridge-id gtkb-wi5456-mcp-status-summary-versioned-file-provenance`):
exit 0. `preflight_passed: true`; `missing_required_specs: []`;
`missing_advisory_specs: []`; `blocking_errors: []`.

Clause preflight (`scripts/adr_dcl_clause_preflight.py --bridge-id
gtkb-wi5456-mcp-status-summary-versioned-file-provenance`): exit 0. Clauses
evaluated: 5 (`must_apply: 4, may_apply: 1`); blocking gaps (gate-failing): 0.

Both mechanical gates pass. They validate spec-linkage completeness and
clause-evidence presence; they do not and cannot validate the substantive
truth of the proposal's technical claims about current test-suite state, which
is the basis for this NO-GO.

## Other checks performed

- Project authorization independently verified via
  `db.get_project_authorization('PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-
  ASSURANCE-20260715-PROJECT-SCOPE')`: `status: active`,
  `allowed_mutation_classes` includes `test`, `forbidden_operations` includes
  `git_commit` (consistent with implementation-only scope; no conflict).
- `target_paths` (`groundtruth-kb/tests/test_mcp_surface_foundation.py`)
  resolves in-root under `E:\GT-KB`; file exists and is currently clean
  (not modified) in git status.
- Fast-lane (`GOV-RELIABILITY-FAST-LANE-001`) was not invoked by this proposal
  (it correctly proceeds under the cited project authorization). Noted for
  completeness: `origin: hygiene` on WI-5456 would not qualify for fast-lane
  treatment in any case (requires `origin` exactly `defect` or `regression`).
- Deliberation Archive searched (`search_deliberations`) for "MCP
  status-summary", "WI-5456", "WI-5411", "mcp provenance" - no directly
  dispositive prior deliberation found beyond the three cited in the proposal's
  own Prior Deliberations section (not independently disputed here).
- TEST-11557 independently confirmed to exist in MemBase
  (`spec_id: GOV-FILE-BRIDGE-AUTHORITY-001`); its `expected_outcome` field
  itself requires "a fresh groundtruth-kb[dev,search,web] Python 3.14
  environment" - i.e., TEST-11557 already anticipates that the *current*
  persistent dev venv is not the right environment for this claim, which
  reinforces F1-F3: the proposal should not claim the current-environment lane
  is dependency-complete when its own linked test says a *fresh* install is
  required to demonstrate the 15-test pass.

## Recommended Action

1. Do not implement WI-5456 in isolation. Revise and refile after WI-5411
   reaches canonical state: target_paths committed, `mcp` actually importable
   in `groundtruth-kb/.venv` (or whatever venv Loyal Opposition verification
   will use), WI-5411 implementation report filed and independently VERIFIED.
2. When refiling, the implementation report/proposal verification command must
   be run and its literal output pasted into the bridge thread (as this review
   did), not asserted from a prior session's memory. Given F2, prose claims of
   "N of 15 passing" without a reproducible command are not reliable evidence
   in this codebase's current state and should not be trusted without
   independent rerun.
3. Consider whether the T8 string correction should simply be folded into
   WI-5411's implementation report as an additional target path, since WI-5411
   is the change that actually makes the T8 assertion reachable; this would
   remove the circular-dependency framing between the two work items.

## Spec-to-Test Mapping (for record; not a VERIFIED verdict)

| Requirement | Independent check performed | Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Read production `build_status_summary_envelope` (`groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py:96-104`) and T8 (`groundtruth-kb/tests/test_mcp_surface_foundation.py:195-201`) directly | Confirmed production emits `bridge/versioned-files+groundtruth.db`; T8 currently expects the obsolete `bridge/INDEX.md+groundtruth.db` - this part of the proposal's diagnosis is accurate |
| `SPEC-1526` / "MCP foundation lane passes 15/15" | Ran `pytest groundtruth-kb/tests/test_mcp_surface_foundation.py -v` in the only project venv present | FAILED - 11 passed, 4 failed; not reproducible as claimed |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Confirmed target file is the only file the proposal declares in scope | Consistent, but scope is insufficient to reach the proposal's own acceptance criteria (see F1) |

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

