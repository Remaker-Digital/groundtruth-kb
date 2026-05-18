NEW

# Implementation Proposal — Relocate orphaned test_build_contract.py out of the platform test tree (WI-3371)

bridge_kind: implementation_proposal
Document: gtkb-test-build-contract-orphan-relocation
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S359

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3371

target_paths: ["platform_tests/test_host/test_build_contract.py", "applications/Agent_Red/tests/test_host/test_build_contract.py"]

This NEW proposal fixes a hard collection abort in the GT-KB platform test
suite. `platform_tests/test_host/test_build_contract.py` is an Agent Red test
stranded in the platform test tree; its module-level import raises
`ModuleNotFoundError`, which aborts the entire `pytest platform_tests/` run
before any test executes. The fix relocates the orphan to its correct home
alongside its sibling Agent Red test files. It is routed through the
reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`) under the standing
`PROJECT-GTKB-RELIABILITY-FIXES` authorization.

## Claim

`platform_tests/test_host/test_build_contract.py` line 123 runs a module-level
`from test_host.suites import SUITE_CONFIGS`. No `test_host` package exists
anywhere in the GT-KB checkout, so the import raises
`ModuleNotFoundError: No module named 'test_host'` at collection time. Because
the failure is a collection-time `ImportError`, pytest aborts the whole
`pytest platform_tests/` invocation with `Interrupted: 1 error during
collection` — no test under `platform_tests/` runs at all.

The file is an Agent Red test, not a GT-KB platform test. It was left behind by
the GTKB-ISOLATION-018 18.E.1 migration, which relocated its sibling Agent Red
`test_host` tests to `applications/Agent_Red/tests/test_host/`. Relocating this
one straggler to that same directory completes the missed migration and
removes the collection abort.

## Defect Evidence

- Reproduction (from `E:\GT-KB`): `python -m pytest platform_tests/ -q
  --collect-only` -> `ModuleNotFoundError: No module named 'test_host'`,
  `Interrupted: 1 error during collection`, `no tests collected`.
- `platform_tests/test_host/test_build_contract.py:123`:
  `from test_host.suites import SUITE_CONFIGS  # noqa: E402` — a module-level
  import executed at collection time. Lines 504/511/551/559/589/602 add
  in-method `from test_host.cosmos_writer import ...` imports.
- `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent` (line 21)
  resolves to `E:\GT-KB`; line 121 inserts it on `sys.path`. The import still
  fails because no `test_host/` package exists at the repository root or
  anywhere else: a `**/test_host/suites.py` glob returns nothing, and a search
  under `applications` for non-test `test_host` modules returns nothing. The
  `test_host` runtime package lives only in Agent Red's own repository, not in
  the `applications/Agent_Red/` snapshot.
- The file is an Agent Red artifact: its own header line 1 reads
  `# tests/test_host/test_build_contract.py`; its test classes validate Agent
  Red container-build and CI configuration consistency (Agent Red's container
  build definitions, its build-ignore file, the host-test CI workflow, and its
  test-requirements file) — none of which are GT-KB platform concerns.
- Git evidence of the orphaning:
  - `git log --follow --diff-filter=R -- applications/Agent_Red/tests/test_host/test_suites.py`
    -> `c1021ab0 refactor(isolation): 18.E.1 atomic code cluster move (1,423
    files)` — the 18.E.1 migration moved the sibling `test_host` test files
    from `tests/test_host/` to `applications/Agent_Red/tests/test_host/`.
  - `git log --follow -- platform_tests/test_host/test_build_contract.py` ->
    most recent move `a641f622 refactor(tests): rename tests/ to
    platform_tests/`; `git show --stat a641f622` shows
    `.../test_host/test_build_contract.py | 0` — a pure path rename. The orphan
    was never part of the 18.E.1 cluster move; it rode the later directory
    rename into `platform_tests/test_host/`.
- `applications/Agent_Red/tests/test_host/` already holds the sibling test
  files (`test_api.py`, `test_cosmos_writer.py`, `test_dispatch.py`,
  `test_dispatch_integration.py`, `test_runner.py`, `test_spa_contract.py`,
  `test_suites.py`) plus `__init__.py`. Each imports the same `test_host`
  package — `applications/Agent_Red/tests/test_host/test_suites.py:10` reads
  `from test_host.suites import SUITE_CONFIGS, SuiteConfig, get_suite,
  list_suites`. The relocated file lands beside identical-shape siblings.
- Scope confirmation: `python -m pytest platform_tests/ -q --collect-only
  --ignore=platform_tests/test_host/test_build_contract.py` collects 2454 tests
  with 0 errors — this one orphan is the sole collection blocker.
- Cosmetic note: the failing traceback frame shows
  `E:\GT-KB\tests\test_host\test_build_contract.py` (the pre-rename path)
  because `platform_tests/test_host/__pycache__/` holds a stale `.pyc` compiled
  before the `a641f622` rename, whose newer mtime makes Python load it. It is
  not a directory junction (`dir /AL` finds none; `tests/test_host/` does not
  exist). IP-1 removes the stale `__pycache__`.

## In-Root Placement Evidence

Both relocation paths are in-root under `E:\GT-KB`: the source
`platform_tests/test_host/test_build_contract.py` and the destination
`applications/Agent_Red/tests/test_host/test_build_contract.py`. This bridge
file is at
`E:\GT-KB\bridge\gtkb-test-build-contract-orphan-relocation-001.md`. No
out-of-root path is touched. The destination under `applications/Agent_Red/`
is the in-root home mandated for Agent Red files by the project-root-boundary
rule and `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — governs the reliability fast-lane this fix is routed through; defect-origin, no new behavior, small single-concern change.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner-decision record establishing the fast-lane (PROJECT-GTKB-RELIABILITY-FIXES plus the standing authorization plus the GOV spec).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; this proposal follows the NEW/GO/implement/report/VERIFIED workflow with `bridge/INDEX.md` as canonical state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every governing specification concretely in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Specification-Derived Verification Plan maps the WI-3371 requirement to an executable verification command.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the fix enforces the in-root placement contract: Agent Red test files belong under `applications/Agent_Red/`, not in the GT-KB platform test tree; both target paths and this bridge file are in-root under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` — WI-3371 is the tracked backlog work item; see Clause Scope Clarification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the fix is delivered as a durable, governed bridge-tracked change, not an undocumented patch.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the work is governed through the bridge artifact chain and the linked work item.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` (outcome `owner_decision`, S351) — established the reliability fast-lane under which this fix is routed; for an eligible defect fix no per-fix deliberation or formal-artifact-approval packet is required.
- A Deliberation Archive search (`search_deliberations` for `test_build_contract platform_tests collection orphan`, `isolation 18.E.1 test_host atomic move`, and `Agent Red test relocation platform tests`) returned no prior decision on this orphaned file. WI-3371 is a newly-discovered defect; no prior approach was proposed or rejected.

## Owner Decisions / Input

- 2026-05-18, owner decision via AskUserQuestion: presented with the diagnosis and three fix options — relocate the orphan to `applications/Agent_Red/tests/test_host/`, add an in-place `pytest.importorskip` skip-guard, or delete the file from the GT-KB checkout — the owner selected **relocate to Agent Red**. This proposal implements the selected option. The AskUserQuestion option text explicitly named the `applications/Agent_Red/tests/test_host/` destination, scoping the relocation into the Agent Red directory.
- Standing pre-approval: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-3371 by active project membership. Per `GOV-RELIABILITY-FAST-LANE-001`, no per-fix deliberation, per-fix project authorization, or formal-artifact-approval packet is required; the bridge proposal, Loyal Opposition review, and all safety gates remain in force.
- No blocking owner decision is pending. This proposal needs only a Loyal Opposition GO.

## Requirement Sufficiency

Existing requirements sufficient. WI-3371 ("Orphaned
platform_tests/test_host/test_build_contract.py aborts pytest platform_tests/
collection") is the operative requirement: the GT-KB platform test tree must
collect without an Agent Red test stranded in it, and Agent Red test files
must reside under `applications/Agent_Red/` per
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`. No new or revised specification is
required.

## Reliability Fast-Lane Eligibility

Per `GOV-RELIABILITY-FAST-LANE-001`:

- Origin is `defect` — a misplaced file whose import aborts platform test
  collection.
- No new public API, CLI, or behavior. IP-1 is a pure file relocation.
- No new or revised requirement or specification.
- Small and single-concern: one file relocated (0 net content lines — a pure
  rename) plus removal of one stale `__pycache__` directory. Well under the
  fast-lane ceiling of about 3 files / 150 net lines.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (WI-3371) is targeted; it is an active
member of `PROJECT-GTKB-RELIABILITY-FIXES` under the standing reliability
fast-lane authorization. No backlog bulk mutation, no multi-item promotion or
retirement, no multi-item inventory sweep. The reliability fast-lane
(`GOV-RELIABILITY-FAST-LANE-001`) waives the per-fix formal-artifact-approval
packet for an eligible defect fix; this proposal creates no GOV/ADR/DCL/SPEC
artifact and no Deliberation Archive record. WI-3371 was recorded in the
MemBase `work_items` backlog before this proposal was filed.

## Bridge INDEX Update Evidence

NEW filed at
`E:\GT-KB\bridge\gtkb-test-build-contract-orphan-relocation-001.md`; a new top
entry is prepended to canonical `E:\GT-KB\bridge\INDEX.md`. `bridge/INDEX.md`
remains the canonical bridge workflow state.

## Proposed Scope

### IP-1: Relocate the orphaned test file

`git mv platform_tests/test_host/test_build_contract.py
applications/Agent_Red/tests/test_host/test_build_contract.py`.

The move is content-preserving — the file body is not edited. The file's
`test_host` imports continue to be satisfied only from Agent Red's own
repository, exactly as for the sibling files already in that directory.
Relocation does not make the test *runnable* in the GT-KB checkout (the
`test_host` runtime package is not vendored here); it makes the test no
*worse* off than its siblings and removes it from the GT-KB platform
collection path. The file's stale header comment is left unchanged so the
relocated file matches its siblings, whose headers were likewise not rewritten
by the 18.E.1 move.

After the move, remove the stale bytecode-cache directory
`platform_tests/test_host/__pycache__/` and the then-empty
`platform_tests/test_host/` directory.

## Specification-Derived Verification Plan

This is a pure file relocation; no code behavior changes, so the spec-derived
verification is the platform-collection check, not a new unit test. Spec-to-
verification mapping (per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`):

| Requirement (WI-3371 / specs) | Behavior verified | Verification |
|---|---|---|
| `pytest platform_tests/` must collect without the orphan abort (WI-3371) | full-tree collection completes with 0 errors | `python -m pytest platform_tests/ -q --collect-only` exits 0, ~2454 tests collected, no `ModuleNotFoundError` |
| Agent Red test belongs under `applications/Agent_Red/` (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`) | the file resides beside its siblings post-move | `applications/Agent_Red/tests/test_host/test_build_contract.py` exists; `platform_tests/test_host/` no longer exists |

Verification command: `python -m pytest platform_tests/ -q --collect-only`.

## Acceptance Criteria

- IP-1 landed; `platform_tests/test_host/test_build_contract.py` no longer
  exists and `applications/Agent_Red/tests/test_host/test_build_contract.py`
  does; `platform_tests/test_host/` (and its stale `__pycache__`) is removed.
- `python -m pytest platform_tests/ -q --collect-only` completes with 0
  collection errors (~2454 tests collected).
- Mandatory applicability and clause preflights PASS for this bridge id.

## Risks / Rollback

- Risk: the relocated file still cannot *run* in the GT-KB checkout because the
  `test_host` runtime package is not vendored under `applications/Agent_Red/`.
  This is a pre-existing Agent Red-scoped condition shared by all sibling
  files; it is out of scope for this GT-KB platform reliability fix and is
  recorded under Observations. The fix introduces no new breakage class in
  `applications/Agent_Red/tests/test_host/` (already uniformly non-collectable
  there) and fully repairs `platform_tests/` collection.
- Risk: relocating a file into `applications/Agent_Red/` touches the Agent Red
  directory. Mitigation: the owner's AskUserQuestion selection explicitly named
  that destination; the destination is mandated by
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and the project-root-boundary rule;
  both paths are in-root under `E:\GT-KB`.
- Rollback: `git mv` the file back to `platform_tests/test_host/`. One
  relocation; fully reversible.

## Observations (Not in Scope)

Surfaced for the reviewer's record; not part of the WI-3371 fix scope:

- A regression guard could be added later — a static test under
  `platform_tests/` asserting no module there imports the `test_host` package —
  so a future stranded Agent Red `test_host` test is caught mechanically. It is
  excluded here to keep the fast-lane fix to a single concern; the reviewer may
  request folding it in if preferred.
- `applications/Agent_Red/tests/test_host/` is uniformly non-collectable in the
  GT-KB checkout: all sibling files import the `test_host` runtime package,
  which is not vendored under `applications/Agent_Red/`
  (`applications/Agent_Red/tests/conftest.py` provides FastAPI/Cosmos/NATS
  fixtures, not a `test_host` path). This is an Agent Red repository concern,
  separate from this GT-KB platform fix; it predates WI-3371 and is not
  regressed by it.
- `bridge/INDEX.md` is well over the ~200-line maintenance guideline stated in
  its own header. INDEX trimming is a separate housekeeping concern and is not
  bundled here.

## Recommended Commit Type

`fix:` — a defect repair. It restores `pytest platform_tests/` collection,
which the stranded orphan broke. The change is a pure file relocation; no new
product capability surface is added.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
