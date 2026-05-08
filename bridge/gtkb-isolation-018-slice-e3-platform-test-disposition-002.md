NO-GO

# Loyal Opposition Review - gtkb-isolation-018-slice-e3-platform-test-disposition-001

**Reviewed file:** `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-001.md`
**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Reviewed:** 2026-05-07 06:23 America/Los_Angeles

## Summary

The E.3 decision-gate shape is correct, and Option A still looks like the
better default if the platform/app split is meant to survive 18.J. It cannot
receive GO yet because the proposed platform-test inventory materially
undercounts `tests/scripts/` platform tests. That bad inventory changes the
Option A vs. Option B trade-off and would give the owner a decision prompt based
on incorrect scope.

## Findings

### F1 - `tests/scripts/` platform-test inventory is materially undercounted

The proposal says `tests/scripts/` contains "19 platform-related files of 69
total" and that "50 of 69 `tests/scripts/` files are NOT platform-related" and
therefore migrate with E.1. The listed subset is not comprehensive. Live review
shows many unlisted `tests/scripts/` files directly test GT-KB platform scripts,
workflows, bridge behavior, harness state, governance, dashboard generation, or
wrap scanners.

Examples of unlisted platform tests:

```text
tests/scripts/test_adr_dcl_clause_preflight.py
tests/scripts/test_bridge_applicability_preflight.py
tests/scripts/test_bridge_automation_role_authority.py
tests/scripts/test_bridge_notify_reader.py
tests/scripts/test_check_dev_environment_inventory_drift.py
tests/scripts/test_check_environment_isolation.py
tests/scripts/test_groundtruth_kb_tests_workflow.py
tests/scripts/test_gtkb_bridge_writer.py
tests/scripts/test_harness_identity.py
tests/scripts/test_harness_roles.py
tests/scripts/test_wrap_capture_transcript.py
tests/scripts/test_wrap_scan_consistency.py
```

These are not Agent Red product tests. Several directly compute `REPO_ROOT =
Path(__file__).resolve().parents[2]` and then load root platform assets. For
example:

```text
tests/scripts/test_adr_dcl_clause_preflight.py:31 SCRIPT_PATH = REPO_ROOT / "scripts" / "adr_dcl_clause_preflight.py"
tests/scripts/test_bridge_applicability_preflight.py:15 SCRIPT_PATH = REPO_ROOT / "scripts" / "bridge_applicability_preflight.py"
tests/scripts/test_groundtruth_kb_tests_workflow.py:10 WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "groundtruth-kb-tests.yml"
tests/scripts/test_gtkb_bridge_writer.py:27 from scripts.gtkb_bridge_writer import ...
tests/scripts/test_harness_identity.py:8 from scripts.harness_identity import ...
tests/scripts/test_harness_roles.py:37 role_path = tmp_path / "harness-state" / "role-assignments.json"
```

If those files migrate under `applications/Agent_Red/tests/scripts/` without
parent-depth rewrites, `parents[2]` resolves to `applications/Agent_Red`, not
the GT-KB root, and root platform script/workflow/harness references break. If
they remain at root under Option A, the Option A stay-set is much larger than
the proposal states.

**Required correction:** Recompute and enumerate the platform/app disposition
for every `tests/scripts/*.py` file, not just `.claude`-referencing files. The
revised proposal should include a table with each of the 69 files marked
`STAYS_PLATFORM`, `MIGRATES_AGENT_RED`, or `UNCERTAIN`, with a one-line reason
for every `UNCERTAIN` entry. The AUQ should be based on those corrected counts.

### F2 - The proposed coverage test only detects one class of platform test

`T-list-coverage-1` uses this detector:

```text
grep -lE "Path\(__file__\)\.resolve\(\)\.parents\[[0-9]\] / \"\\.claude\"" tests/ -r
```

That only catches tests that walk to `.claude/`. It misses platform tests that
load root `scripts/*.py`, `.github/workflows/*.yml`, `harness-state/`,
`groundtruth_kb`, bridge files, dashboard artifacts, and wrap-scan tooling.

**Required correction:** Replace or supplement `T-list-coverage-1` with a
broader inventory method that catches root-platform dependencies, including at
least:

```text
parents[N] + scripts/
imports from scripts.*
.github/workflows/
harness-state/
bridge/
groundtruth_kb platform modules
docs/gtkb-dashboard or dashboard platform artifacts
memory/ and wrap-scan platform artifacts
```

The revised test should make the E.3 report prove that no `tests/scripts/`
platform test is silently sent into the Agent Red app tree under Option A.

### F3 - Option A/Option B trade-off counts need recalculation

Because the platform-test set is undercounted, the proposal's implementation
impact numbers are unreliable:

- Option A is not "~32 files stay at root" unless the corrected inventory proves
  it.
- Option B is not "~25 platform-test files get a one-shot parents rewrite"
  unless the corrected inventory proves it.
- E.1's moved-file estimate under Option A depends on this corrected split.

**Required correction:** Revise the Option A and Option B count estimates after
the full `tests/scripts/` disposition table is built. If many or most
`tests/scripts/` files are platform tests, state that plainly before asking the
owner to choose.

## Evidence Reviewed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-e3-platform-test-disposition`
  passed against operative file
  `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-001.md`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-018-slice-e3-platform-test-disposition`
  reported one advisory Slice-1 evidence gap for the root-boundary clause.
- `git ls-files -- 'tests/scripts/*.py'` returns 69 Python files.
- Comparing the proposal's explicit `tests/scripts/` list against live
  `tests/scripts/*.py` leaves 53 unlisted files, including many obvious platform
  tests.
- Targeted reference checks found unlisted tests loading root `scripts/`,
  `.github/workflows`, `harness-state`, bridge, and `groundtruth_kb` surfaces.

## Applicability Preflight

- packet_hash: `sha256:788ac08a47477554f1a75af00c478ed33de96605dcc3e5fa859ce0a52f5a3252`
- bridge_document_name: `gtkb-isolation-018-slice-e3-platform-test-disposition`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-001.md`
- operative_file: `bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Advisory Clause Preflight

- Bridge id: `gtkb-isolation-018-slice-e3-platform-test-disposition`
- Operative file: `bridge\gtkb-isolation-018-slice-e3-platform-test-disposition-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 1
- Slice 1 mode: advisory; this report does not block NO-GO.

| Clause | Spec | Applicability | Evidence found | Severity |
|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | no | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking |

## Result

Please revise as
`bridge/gtkb-isolation-018-slice-e3-platform-test-disposition-003.md`.
The revision should keep the E.3 decision structure but replace the
`tests/scripts/` inventory and Option A/Option B counts with a complete
file-by-file platform/app disposition.
