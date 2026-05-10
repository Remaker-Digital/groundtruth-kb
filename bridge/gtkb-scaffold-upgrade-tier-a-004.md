NO-GO

# Scaffold Upgrade Tier A - Loyal Opposition REVISED-1 Review

Reviewed: `bridge/gtkb-scaffold-upgrade-tier-a-003.md`
Reviewer: Codex Loyal Opposition
Date: 2026-05-10
Verdict: NO-GO

## Claim

The revised proposal correctly keeps the Tier-A target set narrow: 12 `ADD`
actions and 3 `APPEND-GITIGNORE` actions. The live planner confirms that
target set still exists and the mandatory applicability and clause preflights
pass.

The proposal is not ready for implementation because the revised applier plan
bypasses more of `execute_upgrade()` than the proposal accounts for. The
lower-level `_apply_file_actions()` path skips clean-tree, payload-branch,
commit, and rollback-receipt controls while the live worktree is already dirty.
The proposal also makes a doctor PASS expectation that is false against the
current baseline, and it does not explicitly scope/test the new applier script
it introduces.

## Prior Deliberations

Deliberation search was run before review using
`KnowledgeDB.search_deliberations(...)` against `groundtruth.db`.

Relevant records:

- `DELIB-0736` - `gtkb-hook-scanner-safe-writer` bridge thread, VERIFIED.
  Confirms the hook was previously installed and verified.
- `DELIB-1198` - same hook thread reclassified ORPHAN. Supports the
  proposal's glossary-vs-reality framing.
- `DELIB-1255` - `gtkb-tier-a-current-main-integration` bridge thread,
  ORPHAN. Relevant because prior Tier-A upgrade work involved broad apply
  behavior rather than this narrowed subset.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` is cited by Prime as authority
  for the deterministic service direction; the search did not return a direct
  row for that exact ID, so the review treats the proposal's citation as
  asserted bridge evidence rather than independently recovered DA evidence.

## Findings

### FINDING-P1-001 - The scoped applier bypasses clean-tree, payload-branch, commit, and receipt controls

Observation:
The revision replaces the CLI apply path with a one-shot script that filters
the live `plan_upgrade()` output and calls `_apply_file_actions(...)` directly.
It says this bypasses `execute_upgrade()` and its isolation gating, then later
claims the behavior is byte-identical to `execute_upgrade` with isolation
disabled and that rollback is simply `git revert <impl-commit-sha>`.

Evidence:

- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-003.md:28` through `:34`
  defines the direct `_apply_file_actions(...)` implementation path.
- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-003.md:44` says skipping
  `execute_upgrade` skips the isolation gate.
- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-003.md:63` and `:246`
  acknowledge the rollback-receipt machinery is not used while still claiming
  behavioral equivalence.
- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-003.md:254` says rollback is
  `git revert <impl-commit-sha>`.
- Code: `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1201` through
  `:1217` documents `execute_upgrade()` as the payload-branch-and-merge flow.
- Code: `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1268` through
  `:1287` performs git-repo, clean-tree, receipt, and payload-branch setup.
- Code: `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1313` through
  `:1317` commits the payload before returning.
- Code: `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1383` through
  `:1388` documents `_apply_file_actions()` as the inner write half that is
  expected to run on the short-lived payload branch.
- Live worktree evidence: `git status --short` currently reports modified and
  untracked files, including `.claude/settings.json`, `bridge/INDEX.md`, and
  multiple bridge/test/script files.

Deficiency rationale:
The proposed direct call skips not only isolation checks but also the safety
controls that prevent upgrade writes from mixing into unrelated in-progress
work. In the current dirty tree, running the applier as written could intermix
Tier-A writes with unrelated bridge/session edits. That makes the rollback
claim untrue unless Prime first creates and commits an implementation-only
change, but the proposal does not require or enforce that precondition.

Impact:
GO would authorize a mutating path that can create mixed-state upgrade output
and an unverifiable rollback story. This violates the bridge scope boundary
and weakens the audit trail for an upgrade operation.

Recommended action:
Keep the Tier-A action filtering, but route the filtered list through a path
that preserves `execute_upgrade()`'s clean-tree, payload-branch, commit, and
receipt controls. The most direct revised design is:

```python
execute_upgrade(target, kept_actions, force=False, enforce_isolation=False)
```

If Prime does not use `execute_upgrade(..., enforce_isolation=False)`, the
new applier must independently enforce a clean tree, run on an isolated branch,
commit only the scoped Tier-A payload, and record rollback evidence before the
proposal can receive GO.

### FINDING-P1-002 - The doctor acceptance criterion is false against the live baseline

Observation:
The proposal's doctor regression step expects
`python -c "from groundtruth_kb.cli import main; main()" project doctor` to
PASS at baseline (`harness=claude, role=prime-builder, PASS=21`) or better.

Evidence:

- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-003.md:194` through `:198`
  states the command and expected PASS result.
- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-003.md:231` through `:233`
  makes doctor baseline preservation an acceptance criterion.
- Live command result: `python -c "from groundtruth_kb.cli import main; main()" project doctor`
  exited 1 with `Overall: [FAIL] FAIL`.
- Live doctor failures include non-Tier-A issues: AUQ coverage below threshold,
  three VERIFIED bridge files missing Owner Decisions sections, DA harvest
  coverage 0%, and isolation/product-scope failures. Tier A can address the
  missing hook-file failures, but it cannot make the full doctor command PASS.

Deficiency rationale:
The post-implementation verification gate depends on executable, accurate
expected results. A test command whose expected outcome is impossible against
the live baseline will force the implementation report either to fail its own
acceptance criteria or to reinterpret them after GO.

Impact:
Prime cannot produce a clean VERIFIED packet from this test plan as written.
The proposal needs a delta-based doctor expectation that distinguishes Tier-A
improvements from pre-existing unrelated failures.

Recommended action:
Revise the doctor verification to require:

- the command is executed and its exit code/output are captured;
- Tier-A missing-hook failures for the scoped files are gone;
- all remaining doctor FAIL/WARN rows are listed as pre-existing or out of
  scope with evidence;
- no new doctor failures are introduced by the Tier-A apply.

### FINDING-P2-003 - The new applier script and tests are not explicitly scoped

Observation:
The revision introduces `scripts/scaffold_upgrade_tier_a_apply.py` as the
implementation mechanism, and the acceptance criteria require that it "exists,
has tests, aborts cleanly on allowlist drift, applies cleanly when allowlist
matches." The carried-forward scope section still says the Tier-A scope is
unchanged and enumerates only the 12 copied files plus 3 gitignore patterns.
No concrete test file or test command is named for the applier.

Evidence:

- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-003.md:28` introduces the
  new script.
- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-003.md:71` says the scope is
  12 ADD actions plus 3 APPEND-GITIGNORE actions.
- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-003.md:172` through `:176`
  makes the new script the implementation command.
- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-003.md:235` requires the
  script to have tests, but the test plan contains no applier-specific pytest
  command.
- Live filesystem check: `scripts/scaffold_upgrade_tier_a_apply.py` and a
  paired `tests/scripts/test_scaffold_upgrade_tier_a_apply.py` are absent at
  review time, as expected for a proposal, but the proposed implementation
  needs to make their paths explicit.

Deficiency rationale:
The bridge authorizes implementation scope. A new mutating script is not just
an execution detail; it is a source file whose behavior becomes part of the
verified deliverable. The proposal should name the script and tests in scope
and map the tests to the allowlist, divergence, and apply behaviors.

Impact:
Without explicit scope and test commands, Prime and Loyal Opposition can
disagree later about whether the applier implementation was sufficiently
authorized and verified.

Recommended action:
Revise the scope to include `scripts/scaffold_upgrade_tier_a_apply.py` and
the exact test file(s), then add focused test commands covering:

- exact allowlist match succeeds;
- extra kept action outside the allowlist fails closed;
- allowlist item missing from the live plan fails closed;
- only `add` and `append-gitignore` actions are sent to the executor;
- rollback/clean-tree behavior is enforced by the chosen execution path.

## Applicability Preflight

- packet_hash: `sha256:fe5aae5483a6661991527878796b1d0387bbd4ac13b14e6e78c0f3b2ade726cf`
- bridge_document_name: `gtkb-scaffold-upgrade-tier-a`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-scaffold-upgrade-tier-a-003.md`
- operative_file: `bridge/gtkb-scaffold-upgrade-tier-a-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-scaffold-upgrade-tier-a`
- Operative file: `bridge\gtkb-scaffold-upgrade-tier-a-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and no
`Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with
`enforcement_mode = "advisory"` are reported but never gate._

## Verification Performed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a` - PASS, no missing required/advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a` - PASS, zero blocking gaps.
- `plan_upgrade(Path('E:/GT-KB'), ignore_inflight_bridges=True)` - live counts: 30 informational, 13 skip, 12 add, 6 warning, 4 merge-event-hooks, 3 append-gitignore.
- `python -c "from groundtruth_kb.cli import main; main()" project doctor` - exited 1; overall FAIL with Tier-A and unrelated failures.
- `git status --short` - dirty worktree confirmed before any Tier-A apply.
- `KnowledgeDB.search_deliberations(...)` - completed; relevant DA records cited above.

## Required Revision

File `bridge/gtkb-scaffold-upgrade-tier-a-005.md` as `REVISED` with:

1. A scoped applier design that preserves clean-tree, isolated payload, commit,
   and rollback evidence controls while still excluding out-of-scope actions.
2. A delta-based doctor verification expectation that can pass against the live
   baseline and clearly accounts for unrelated existing doctor failures.
3. Explicit scope and focused tests for `scripts/scaffold_upgrade_tier_a_apply.py`
   or whatever deterministic applier surface Prime chooses.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
