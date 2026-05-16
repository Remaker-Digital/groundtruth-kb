REVISED

# Implementation Proposal - Agent Red Deployability Preservation Gate - Slice 1 (Partial): RC-Gate / Python-Gate / Frontend / Test-Collection Proofs (WI-3248)

bridge_kind: implementation_proposal
Document: gtkb-agent-red-deployability-preservation-gate
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH-P0-DEPLOYABILITY-GATE
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: WI-3248

target_paths: ["groundtruth-kb/src/groundtruth_kb/adoption/deployability_preservation_gate.py", "scripts/adopter_deployability_check.py", "platform_tests/scripts/test_adopter_deployability_check.py"]

This REVISED proposal implements `WI-3248` (P0) as an explicitly-partial Slice 1. It builds the
GT-KB-side preservation gate **for four of the seven owner-approved deployability proofs**; the
remaining three proofs are deferred to named follow-on threads (see Coverage and Deferral below).
The gate runs before any irreversible adopter migration / cutover / extraction / deletion /
restructuring and verifies the covered deployability proofs are intact.

## Revision Notes

This `-003` REVISED version addresses every finding in the `-002` NO-GO:

- **F1 (P1) — omits the SPEC-DEPLOY-* family.** Addressed. The `## Specification Links` section
  below now cites all seven `SPEC-DEPLOY-*` specs (`SPEC-DEPLOY-SOURCE-BUILD-001`,
  `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001`, `SPEC-DEPLOY-CONTAINER-BUILD-001`,
  `SPEC-DEPLOY-FRONTEND-BUNDLES-001`, `SPEC-DEPLOY-WORKFLOW-INPUTS-001`,
  `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001`, `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001`). A new
  `## Spec-to-Check Coverage Matrix` section maps each of the seven specs to a check (covered)
  or to a named follow-on thread (deferred). All seven were verified present in MemBase at
  `status='specified'` via the read-only `KnowledgeDB.get_spec()` API before filing.
- **F2 (P1) — proposed checks materially narrower than WI-3248 and the spec family.** Addressed
  by the second of the two options Codex offered: this proposal is **re-titled as an explicitly
  partial Slice 1**. The title, Claim, and the new `## Coverage and Deferral` section state which
  three `SPEC-DEPLOY-*` proofs are covered now, which four are intentionally deferred, the named
  follow-on threads, and the hard rule that no irreversible adopter work may proceed until the
  full preservation gate (all seven proofs) exists and passes.
- **F3 (P2) — `gt` command claim does not match target_paths.** Addressed. The
  `gt adopter deployability-check` command claim is **dropped**. This slice creates only the
  root script wrapper `scripts/adopter_deployability_check.py`. No package CLI registry file is
  in `target_paths` and no `gt` subcommand is claimed. Promotion to a first-class `gt` subcommand
  is named as a follow-on thread.
- **F4 (P2) — test target outside the current root pytest lane.** Addressed. The test file moved
  from `tests/scripts/test_adopter_deployability_check.py` to
  `platform_tests/scripts/test_adopter_deployability_check.py`. `target_paths`, the verification
  plan, and acceptance criteria all use the `platform_tests/scripts/` path, which is inside the
  configured `testpaths` (`pyproject.toml` `testpaths = ["platform_tests", "applications/Agent_Red/tests"]`).

## Claim

Build a `python scripts/adopter_deployability_check.py --adopter-root <path>` root script wrapper
plus a `groundtruth_kb.adoption.deployability_preservation_gate` library function that runs
against a target adopter root and asserts the four Slice-1-covered proofs: (a) release-candidate
path is intact (RC-gate skill present + runnable in dry-run) — covers
`SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001` RC-gate clause; (b) Python language gate satisfied
(project's declared `python_requires` resolvable) — covers `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001`
Python-3.12 clause; (c) frontend build path intact (if applicable per project metadata) — covers
`SPEC-DEPLOY-FRONTEND-BUNDLES-001`; (d) test suite collects without errors — supporting check for
`SPEC-DEPLOY-EVIDENCE-FRESHNESS-001`. Returns PASS/FAIL/SKIP/WARN with per-check diagnostic. The
remaining `SPEC-DEPLOY-*` proofs (source build, container build, workflow inputs, maintain/enhance
smoke) are deferred to named follow-on threads.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`
satisfied.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - source spec cited by the WI; the gate is artifact-oriented governance over adopters.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness frames adopter deployability.
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` - adopter framework.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this proposal as a bridge artifact.
- `SPEC-AUQ-POLICY-ENGINE-001` - CLI surface (the root script wrapper).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root; the gate operates on adopter roots which may be under `applications/`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the post-implementation VERIFIED step to rest on executed spec-derived tests; the spec-to-test plan below maps every covered spec to a test.
- `GOV-STANDING-BACKLOG-001` - WI-3248 tracked in the standing backlog.
- `SPEC-DEPLOY-SOURCE-BUILD-001` - deployability proof: adopter source build path. Deferred to follow-on thread `gtkb-agent-red-deployability-preservation-gate-slice-2-source-container`.
- `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001` - deployability proof: release-candidate gate + Python 3.12 language gate. COVERED by Slice 1 checks (a) and (b).
- `SPEC-DEPLOY-CONTAINER-BUILD-001` - deployability proof: Docker/container build surfaces. Deferred to follow-on thread `gtkb-agent-red-deployability-preservation-gate-slice-2-source-container`.
- `SPEC-DEPLOY-FRONTEND-BUNDLES-001` - deployability proof: frontend/admin/widget build surfaces. COVERED by Slice 1 check (c).
- `SPEC-DEPLOY-WORKFLOW-INPUTS-001` - deployability proof: deployment workflow inputs/artifacts. Deferred to follow-on thread `gtkb-agent-red-deployability-preservation-gate-slice-3-workflow-maintain`.
- `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001` - deployability proof: safe maintain/enhance smoke path. Deferred to follow-on thread `gtkb-agent-red-deployability-preservation-gate-slice-3-workflow-maintain`.
- `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` - deployability proof: deployability evidence freshness. PARTIALLY COVERED by Slice 1 check (d) (test-collection freshness signal); full evidence-freshness aggregation deferred to follow-on thread `gtkb-agent-red-deployability-preservation-gate-slice-4-evidence-aggregation`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, and linked specs form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the WI triggers this implementation proposal and its tests.
- `.claude/rules/file-bridge-protocol.md` - bridge file naming, INDEX semantics, Specification Links and Owner Decisions / Input section requirements, Pre-Filing Preflight Subsection.
- `.claude/rules/codex-review-gate.md` - Counterpart Review Gate; this proposal seeks Codex GO before implementation.
- `.claude/rules/project-root-boundary.md` - all `target_paths` resolve inside `E:\GT-KB`.

## Spec-to-Check Coverage Matrix

| SPEC-DEPLOY-* spec | WI-3248 proof | Slice 1 disposition | Slice 1 check / deferral target |
|---|---|---|---|
| `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001` | release-candidate path + Python 3.12 gate | COVERED | checks (a) `check_rc_gate` + (b) `check_python_gate` |
| `SPEC-DEPLOY-FRONTEND-BUNDLES-001` | frontend/admin/widget build surfaces | COVERED | check (c) `check_frontend_build_path` |
| `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` | deployability evidence freshness | PARTIAL | check (d) `check_test_suite_collects` provides a test-collection freshness signal; full evidence-freshness aggregation deferred |
| `SPEC-DEPLOY-SOURCE-BUILD-001` | adopter source build path | DEFERRED | follow-on thread `gtkb-agent-red-deployability-preservation-gate-slice-2-source-container` |
| `SPEC-DEPLOY-CONTAINER-BUILD-001` | Docker/container build surfaces | DEFERRED | follow-on thread `gtkb-agent-red-deployability-preservation-gate-slice-2-source-container` |
| `SPEC-DEPLOY-WORKFLOW-INPUTS-001` | deployment workflow inputs/artifacts | DEFERRED | follow-on thread `gtkb-agent-red-deployability-preservation-gate-slice-3-workflow-maintain` |
| `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001` | maintain/enhance smoke path | DEFERRED | follow-on thread `gtkb-agent-red-deployability-preservation-gate-slice-3-workflow-maintain` |

## Coverage and Deferral

This Slice 1 is an **explicitly partial implementation of WI-3248**. WI-3248 and the
`SPEC-DEPLOY-*` family define a seven-proof deployability-preservation contract. Slice 1 covers
three proofs fully (RC-gate + Python gate, frontend bundles) and one partially (evidence
freshness, via test-collection signal). The four remaining proofs are deferred:

- **Slice 2 (source + container)** — `gtkb-agent-red-deployability-preservation-gate-slice-2-source-container`
  will cover `SPEC-DEPLOY-SOURCE-BUILD-001` and `SPEC-DEPLOY-CONTAINER-BUILD-001`.
- **Slice 3 (workflow + maintain/enhance)** — `gtkb-agent-red-deployability-preservation-gate-slice-3-workflow-maintain`
  will cover `SPEC-DEPLOY-WORKFLOW-INPUTS-001` and `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001`.
- **Slice 4 (evidence aggregation)** — `gtkb-agent-red-deployability-preservation-gate-slice-4-evidence-aggregation`
  will fully cover `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` by aggregating all proof results into a
  freshness-stamped evidence record, and will optionally promote the root script to a first-class
  `gt adopter deployability-check` subcommand under that thread's own `target_paths`.

**Hard gate on irreversible adopter work:** The Slice 1 gate is NOT sufficient to authorize any
irreversible adopter migration, cutover, extraction, deletion, or restructuring. Per WI-3248, the
full deployability-preservation gate (all seven proofs) must exist and PASS before any such work
proceeds. Slice 1's operational contract — documented in the library docstring and the CLI
`--help` text — states that the gate is `partial` and names the missing proofs, so a future
session cannot mistake a Slice-1 PASS for full deployability clearance. The library returns an
explicit `coverage="partial"` field alongside the per-check results to make the partial status
machine-detectable.

## Prior Deliberations

- `DELIB-S350-BATCH6-P0P1-AUTHORIZATION` - batch-6 owner authorization (P0/P1 amendment); confirms the owner authorized adding WI-3248 to PROJECT-GTKB-ADOPTER-EXPERIENCE as GT-KB platform scope.
- `DELIB-0319` - Agent Red deployability history: hard release paths and staging/prod promotion context relevant to the RC-gate proof.
- `DELIB-0327` - Agent Red deployability history: artifact-lane proof and release-path context relevant to the deployability proofs.

No prior deliberation waives the requirement to cite and map the `SPEC-DEPLOY-*` family; the
`-002` NO-GO and the prior local scoping review
(`bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-002.md`) both require it,
and this REVISED version satisfies that requirement.

## Owner Decisions / Input

This proposal depends on owner approval. The authorizing AskUserQuestion evidence:

- 2026-05-15 UTC, S350+: owner directive captured via AskUserQuestion (DELIB-S350-BATCH6-P0P1-AUTHORIZATION): "I authorize the remaining P0/P1. Please continue to parallelize the implementation proposals and work through the backlog." This authorizes WI-3248 as GT-KB platform scope under PROJECT-GTKB-ADOPTER-EXPERIENCE.
- Per-proposal Codex GO is required before implementation; this REVISED proposal seeks that GO.
- Re-titling Slice 1 as explicitly partial does not require a new owner decision: the partial
  scope is a within-WI implementation-sequencing choice, and the four deferred proofs remain
  tracked under WI-3248 and the named follow-on threads. If Loyal Opposition judges that the
  partial framing requires a fresh owner decision, NO-GO with that finding is the expected
  enforcement outcome.

## Requirement Sufficiency

Existing requirements sufficient. WI-3248's owner-approved packet
(`.groundtruth/formal-artifact-approvals/2026-05-05-wi-3248-agent-red-preservation-gate.json`)
specifies the seven deployability proofs, and the `SPEC-DEPLOY-*` family
(`.groundtruth/formal-artifact-approvals/2026-05-04-spec-deploy-family-batch.json`) formalizes
each proof as a `specified` specification. No new or revised requirement or specification is
created by this work; Slice 1 implements four of the seven existing `specified` specs and defers
the rest. If the deferred-proof follow-on threads reveal classification ambiguity not covered by
the existing specs, those threads will surface the gap as a candidate SPEC update through the
governed approval path.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/adoption/deployability_preservation_gate.py` - new gate library: `DeployabilityCheckResult` dataclass, `check_adopter_deployability(adopter_root)` returning the four covered checks plus a `coverage="partial"` marker, and the four `check_*` functions.
- `scripts/adopter_deployability_check.py` - new root script wrapper invoking the library; `--adopter-root <path>`, `--json`; exit 0 if all PASS/SKIP, non-zero if any FAIL; `--help` text states `partial` coverage and names the deferred proofs.
- `platform_tests/scripts/test_adopter_deployability_check.py` - new spec-derived test module (the seven tests in the verification plan below).

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. This proposal advances one P0 work item (WI-3248) and creates one library
file, one root script, and one test file. It performs no batch resolve, promote, or retire of
work items or specifications. References to "work item", "backlog", and "standing backlog"
describe the single work item WI-3248 and its governed filing path only. WI-3248 is a member of
`PROJECT-GTKB-ADOPTER-EXPERIENCE` per the `formal-artifact-approval` packet
`.groundtruth/formal-artifact-approvals/2026-05-15-batch6-p0p1-amendments.json`. The review-packet
inventory is this single bridge document covering the library + script + test file. Cited
evidence patterns: `inventory`, `formal-artifact-approval`.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow-state record. The REVISED
version is filed by inserting `REVISED: bridge/gtkb-agent-red-deployability-preservation-gate-003.md`
at the top of the existing `Document: gtkb-agent-red-deployability-preservation-gate` entry's
version list, above the `-002` NO-GO line. No prior bridge versions are deleted or rewritten.

## Proposed Scope

### IP-1: Deployability preservation gate library (Slice 1, partial)

`groundtruth-kb/src/groundtruth_kb/adoption/deployability_preservation_gate.py`:

```python
@dataclass
class DeployabilityCheckResult:
    name: str
    status: str  # PASS | FAIL | SKIP | WARN
    detail: str

@dataclass
class DeployabilityReport:
    coverage: str  # "partial" for Slice 1
    covered_specs: list[str]
    deferred_specs: list[str]
    results: list[DeployabilityCheckResult]

def check_adopter_deployability(adopter_root: Path) -> DeployabilityReport:
    return DeployabilityReport(
        coverage="partial",
        covered_specs=[
            "SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001",
            "SPEC-DEPLOY-FRONTEND-BUNDLES-001",
            "SPEC-DEPLOY-EVIDENCE-FRESHNESS-001",  # partial
        ],
        deferred_specs=[
            "SPEC-DEPLOY-SOURCE-BUILD-001",
            "SPEC-DEPLOY-CONTAINER-BUILD-001",
            "SPEC-DEPLOY-WORKFLOW-INPUTS-001",
            "SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001",
        ],
        results=[
            check_rc_gate(adopter_root),
            check_python_gate(adopter_root),
            check_frontend_build_path(adopter_root),
            check_test_suite_collects(adopter_root),
        ],
    )
```

Each sub-check is read-only / dry-run only - no actual builds or deploys. Returns FAIL with
diagnostic on broken state. The `coverage="partial"` field plus the explicit `covered_specs` /
`deferred_specs` lists make the partial status machine-detectable so no future session can treat
a Slice-1 PASS as full deployability clearance.

### IP-2: Root script wrapper (no `gt` subcommand)

`scripts/adopter_deployability_check.py`: root script wrapper.
`python scripts/adopter_deployability_check.py --adopter-root <path> [--json]`. Exit 0 if all
PASS or SKIP; non-zero if any FAIL. `--help` text states the gate is a `partial` Slice 1 and
names the four deferred proofs. No package CLI registry file is modified; no `gt` subcommand is
created in this slice.

### IP-3: Tests

`platform_tests/scripts/test_adopter_deployability_check.py` covers fixture adopter scenarios:
healthy adopter (all covered checks PASS), broken RC-gate (FAIL), missing Python requires (FAIL),
missing frontend (SKIP if no frontend declared), broken test suite (FAIL), CLI exit code, JSON
output schema including the `coverage`/`covered_specs`/`deferred_specs` fields.

## Specification-Derived Verification Plan

Each Slice-1-covered specification maps to at least one test. Tests live in the `target_paths`
test file `platform_tests/scripts/test_adopter_deployability_check.py`.

| Behavior | Test | Covers spec |
|---|---|---|
| Healthy adopter: all covered checks PASS | `test_healthy_adopter_all_pass` | `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001`, `SPEC-DEPLOY-FRONTEND-BUNDLES-001` |
| Broken RC-gate FAIL | `test_broken_rc_gate_fails` | `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001` (RC-gate clause) |
| Missing python_requires FAIL | `test_missing_python_gate_fails` | `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001` (Python-3.12 clause) |
| Missing frontend gracefully SKIP | `test_no_frontend_skip` | `SPEC-DEPLOY-FRONTEND-BUNDLES-001` |
| Broken test suite collection FAIL | `test_broken_test_collection_fails` | `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` (test-collection freshness signal) |
| CLI exit code reflects results | `test_cli_exit_code` | `SPEC-AUQ-POLICY-ENGINE-001` (CLI surface) |
| JSON output schema incl. `coverage`/`covered_specs`/`deferred_specs` | `test_cli_json_schema_partial_coverage` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (partial-coverage machine-detectable) |

Run: `python -m pytest platform_tests/scripts/test_adopter_deployability_check.py -v`.

Verification commands:

```
python -m pytest platform_tests/scripts/test_adopter_deployability_check.py -v --tb=short
python -m ruff check .
python -m ruff format --check .
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate
```

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; the 7 tests in `platform_tests/scripts/test_adopter_deployability_check.py` PASS.
- `ruff check` and `ruff format --check` are clean.
- The library `DeployabilityReport` carries `coverage="partial"` plus accurate `covered_specs` and `deferred_specs` lists.
- The CLI `--help` text states the gate is a partial Slice 1 and names the four deferred proofs.
- Both preflights PASS (`preflight_passed: true`, clause preflight exit 0).
- The gate is intended to be called BEFORE any adopter migration WI begins implementation; the partial-coverage marker prevents a Slice-1 PASS being mistaken for full deployability clearance. The operational contract is documented in the library docstring and CLI `--help`.

## Risks / Rollback

- Risk: a future session treats a partial Slice-1 PASS as full deployability clearance. Mitigation: the `coverage="partial"` field, the explicit `deferred_specs` list, and the CLI `--help` wording all surface the partial status; the Coverage and Deferral section states the hard gate on irreversible work.
- Risk: false-negative on healthy adopter (gate misclassifies). Mitigation: per-check diagnostic + WARN tier for edge cases.
- Risk: false-positive on broken adopter (gate passes broken state). Mitigation: clear FAIL conditions documented per check; spot-check against Agent Red's repository for the four covered proofs.
- Rollback: remove `groundtruth-kb/src/groundtruth_kb/adoption/deployability_preservation_gate.py`, `scripts/adopter_deployability_check.py`, and `platform_tests/scripts/test_adopter_deployability_check.py`. No MemBase rows are mutated by this slice.

## Recommended Commit Type

`feat` - new P0 governance gate library + root script + tests. Net-new capability surface (~150 LOC + tests).

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate`

```text
## Applicability Preflight

- packet_hash: `sha256:a6032e29876bd169479b0eae05411b792122b6f7c596de9aeb64d194c8c4d5c6`
- bridge_document_name: `gtkb-agent-red-deployability-preservation-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-agent-red-deployability-preservation-gate-003.md`
- operative_file: `bridge/gtkb-agent-red-deployability-preservation-gate-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

Result: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate`

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-agent-red-deployability-preservation-gate`
- Operative file: `bridge\gtkb-agent-red-deployability-preservation-gate-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

Result: exit 0; 5/5 `must_apply` clauses with evidence found; 0 blocking gaps.
