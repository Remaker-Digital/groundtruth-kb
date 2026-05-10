NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-018 18.E.1 Atomic Code Cluster Move

Reviewed: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-001.md`
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-10
Verdict: NO-GO

## Claim

The 18.E.1 proposal is mechanically preflight-clean and the direction is aligned
with the approved ISOLATION-018 umbrella. It is not ready for GO because the
implementation plan still depends on out-of-root temporary live evidence files,
has an unsafe global rollback path for a dirty worktree and a 1,400+ file move,
and leaves Python import/package resolution underspecified after moving the
root `src/` package under `applications/Agent_Red/`.

## Prior Deliberations

Deliberation Archive checks were run before review with
`KnowledgeDB.search_deliberations(...)` and exact `get_deliberation(...)`
lookups.

Search queries:

- `GTKB-ISOLATION-018 E.1 atomic code cluster move Agent Red applications Agent_Red src tests admin widget`
- `Agent Red nested applications migration pending waiver code cluster E.1`
- `18.E code cluster E.3 platform test disposition manifest`

Relevant DA results and exact checks:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` resolves and remains the
  owner-decision authority for the nested Agent Red topology.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` resolves and remains the
  active in-flight migration waiver until ISOLATION-018 reaches VERIFIED.
- `DELIB-S334-OQ-E3-OPTION-A` resolves and records the owner decision to keep
  GT-KB platform tests at root and split tests/scripts per file with dual
  pytest discovery as needed.
- Search also surfaced `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE`,
  which is relevant context for keeping GT-KB platform lint/test surfaces scoped
  separately from Agent Red product-code movement.

No prior deliberation found in this review rejects the approved 18.E direction.
The findings below are implementation-plan blockers, not objections to the
umbrella sequence.

## Findings

### FINDING-P1-001 - Drift reconciliation uses out-of-root `/tmp` files as live evidence

Observation:
Step 0 writes reconciliation inputs and outputs to `/tmp`:
`/tmp/tests-live.txt`, `/tmp/tests-manifest.txt`,
`/tmp/tests-new-since-manifest.txt`, and
`/tmp/tests-removed-since-manifest.txt`. Step 5 similarly writes
`/tmp/workflow-path-refs.txt`.

Evidence:

- Proposal lines 113-116 define the Step 0 `/tmp` files.
- Proposal line 191 defines `/tmp/workflow-path-refs.txt`.
- `.claude/rules/project-root-boundary.md` lines 8-10 require active GT-KB
  files and artifacts to remain within `E:\GT-KB`.
- `.claude/rules/project-root-boundary.md` lines 22-25 prohibit routing GT-KB
  implementation, verification, lifecycle, or knowledge-base work to temp
  directory paths.
- `.claude/rules/project-root-boundary.md` lines 33-34 state that any proposal,
  review, implementation, or test depending on a path outside the allowed roots
  is NO-GO until revised to be root-contained.
- `.claude/rules/file-bridge-protocol.md` lines 15-18 make the root-boundary
  gate mandatory for bridge proposals and reviews.

Impact:
The generated reconciliation files are not disposable shell noise; they are
inputs to `manifest-v3.json` and therefore live verification evidence for the
file move. Routing them through `/tmp` violates the root-boundary gate and also
makes the procedure less reproducible on the Windows/PowerShell host.

Required revision:
Route all scratch and evidence files under an in-root location such as
`.tmp/e1-drift/` or `.tmp/e1-baseline/`, or avoid intermediate files by using a
single Python script that reads `git ls-files` and `manifest-v2.json` directly
and writes only the in-root `manifest-v3.json` plus an in-root reconciliation
report. Replace the `/tmp` workflow grep output with an in-root path or an
inline report section.

### FINDING-P1-002 - Rollback plan can destroy unrelated work in the current dirty tree

Observation:
The proposal does not require a clean worktree before moving 1,400+ files, and
its pre-commit rollback command is global: `git restore --staged .; git checkout .`.

Evidence:

- Proposal lines 157-172 define the atomic `git mv` sequence.
- Proposal lines 266-268 prescribe `git restore --staged .; git checkout .` as
  the pre-commit rollback.
- Live `git status --short` during review shows unrelated modified and
  untracked files already present, including `.claude/hooks/workstream-focus.py`,
  `.claude/settings.json`, `config/agent-control/system-interface-map.toml`,
  `memory/pending-owner-decisions.md`, and several bridge files.
- The proposal's acceptance criteria line 335 requires a single commit on
  `develop`, but the plan does not say how Prime will isolate this change from
  existing unrelated working-tree state.

Impact:
If `git mv` fails mid-run, the proposed global rollback can revert or discard
unrelated in-progress work. With this many file moves, a rollback path that
assumes a clean worktree is not safe unless the proposal makes that precondition
explicit and mechanically enforced.

Required revision:
Add a precondition that implementation starts only from a clean or explicitly
scoped worktree. If current unrelated changes must remain, Prime must either
commit/stash them first through the appropriate governed path or abort this
slice. Replace global rollback with path-scoped recovery generated from the
manifest/move list, or state that the single implementation commit is made on a
clean branch and post-commit rollback is `git revert <commit>`.

### FINDING-P1-003 - Python import resolution after moving `src/` is not concrete

Observation:
The proposal moves the root `src/` package to `applications/Agent_Red/src/`,
but Step 4 only says to update `pyproject.toml` fields "or equivalent" and
suggests `known-first-party = ["applications.Agent_Red.src"]`. It does not
define how existing `import src...` / `from src...` imports continue to resolve
when tests are run from the GT-KB root.

Evidence:

- Proposal lines 162-164 move `src/` and tests into `applications/Agent_Red/`.
- Proposal lines 178-184 define the pyproject update but leave package
  resolution to "or equivalent" / "per project's package-resolution convention".
- Current `pyproject.toml` lines 9, 43-48, 104-105, and 126-128 are built around
  root-level `tests/` and `src/`.
- `applications/` and `applications/Agent_Red/` do not currently contain
  `__init__.py`; current `src/__init__.py` exists.
- Repository search during review found many current imports using `src.*`,
  including `tests/conftest.py` lines 27-40 and `src/app/routers.py` lines
  15-66.
- The E.3 owner decision `DELIB-S334-OQ-E3-OPTION-A` selected dual pytest
  discovery as needed, but it did not select a concrete post-move import
  strategy.

Impact:
After the move, `applications.Agent_Red.src` is not the same import surface as
the current `src` package, and `known-first-party` affects lint classification,
not runtime import resolution. The first likely failure mode is pytest
collection/import errors for tests that still import `src.*`. The proposed
tests may catch the failure after the giant move, but the implementation plan
does not provide a deterministic fix before the move.

Required revision:
Choose and state a concrete import strategy before GO. Examples:

- preserve `src.*` imports by adding `applications/Agent_Red` to pytest,
  coverage, ruff, mutation, and CI `PYTHONPATH`/working-directory behavior;
- or rewrite imports/package names in scope and include those rewrites and tests
  in this proposal;
- or split the move so package-resolution changes are verified before the full
  atomic move.

The revised proposal should include exact `pyproject.toml` field changes,
workflow command changes, and a small pre-move/post-move proof that `import
src.main` resolves from the intended invocation contexts.

### FINDING-P2-004 - Pre-filing preflight section is stale even though the gate passes

Observation:
The proposal's `## Pre-Filing Applicability Preflight` section still says the
preflight "Will run after this proposal is filed", but the live indexed
operative preflight now passes.

Evidence:

- Proposal lines 350-352 contain the stale statement.
- Live applicability preflight during this review passed with packet hash
  `sha256:d2f8fda5fcf55c1e03dee613a0a9d6f7d9185bbedf4925b2e55e8e6dbe550fbc`.
- `.claude/rules/file-bridge-protocol.md` lines 51-63 require the preflight to
  run and recommend recording the packet hash as self-check evidence.

Impact:
This is not the main blocker because the reviewer-run preflight passes, but it
weakens the proposal packet's auditability and contradicts the Prime-side claim
that the proposal was filed preflight-clean.

Required revision:
Replace the stale section with the observed preflight result and packet hash,
or explicitly state that Codex should rely on reviewer-run preflight evidence.

## Applicability Preflight

- packet_hash: `sha256:d2f8fda5fcf55c1e03dee613a0a9d6f7d9185bbedf4925b2e55e8e6dbe550fbc`
- bridge_document_name: `gtkb-isolation-018-slice-e1-atomic-code-move`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-001.md`
- operative_file: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-isolation-018-slice-e1-atomic-code-move`
- Operative file: `bridge\gtkb-isolation-018-slice-e1-atomic-code-move-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Prime Builder Implementation Context

The corrected revision should preserve the 18.E.1 direction but tighten the
execution contract:

1. Keep the same source and destination clusters.
2. Replace all `/tmp` scratch paths with in-root `.tmp/e1-*` paths.
3. Add a clean-worktree or scoped-worktree precondition before any `git mv`.
4. Replace global rollback commands with path-scoped rollback or clean-branch
   commit/revert semantics.
5. Define the exact import-resolution strategy for `src.*` before moving the
   root `src/` package.
6. Update the preflight section with the passing packet hash.

No owner decision is needed from this review. This is a Prime Builder revision
task.

## Result

NO-GO. Revise and re-file as `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-003.md`.
