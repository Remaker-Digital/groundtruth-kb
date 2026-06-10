NEW

# Per-Session Pytest Basetemp Isolation to Eliminate Parallel-Session ACL Contamination (WI-3469)

bridge_kind: prime_proposal
Document: gtkb-pytest-basetemp-session-isolation
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Implements: GOV-FILE-BRIDGE-AUTHORITY-001; WI-3469
Project Authorization: PAUTH-WI-3469-PYTEST-BASETEMP-ISOLATION-001
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-3469
target_paths: ["conftest.py", "platform_tests/scripts/test_pytest_basetemp_isolation.py"]
Recommended commit type: fix:
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 86d7f8a9-b8da-4284-b937-60eb056adda0
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

## Claim

GT-KB has no central pytest basetemp configuration, so concurrent sessions collide on a shared temp parent and contaminate it with per-process ACLs, producing intermittent permission failures. This is the defect WI-3469 names: "Reclaim `.pytest-tmp/` from ACL contamination by parallel-session python processes."

Evidence:

- `pyproject.toml:8-15` is the only root pytest configuration (`[tool.pytest.ini_options]`). It sets `testpaths` (line 9) and `addopts = "-v --tb=short --strict-markers --timeout=30"` (line 15) but sets **no `basetemp`** and **no `cache_dir`**. With no `basetemp`, pytest defaults its temp root to the OS temp directory (the per-user `pytest-of-<user>` dir). When that OS path is unreachable in a sandbox or already ACL-locked by another process, fixture setup fails — observed repeatedly in bridge reports, e.g. `bridge/gtkb-axis-2-scoping-terminal-classifier-fix-002.md:142-143` ("the sandbox could not access" the OS pytest temp) and `bridge/gtkb-approval-gate-readonly-flag-skip-006.md:122` ("Initial pytest runs without `--basetemp` hit a sandbox temp-permission error").
- The current workaround is for every session to pass an ad-hoc `--basetemp=<in-root path>` on the command line. Because there is no shared convention, parallel sessions reuse **the same literal path** — e.g. an in-root `.tmp\pytest` (`bridge/active-workspace-declaration-slice-1-007.md:74`, `-009.md:172`) and an in-root `.pytest-tmp\<name>` (`bridge/gtkb-axis-2-scoping-terminal-classifier-fix-004.md:128`). pytest **wipes and recreates** an explicit `--basetemp` on each run; when two sessions target the same parent at once, one session's running python processes hold ACLs/handles on subtrees the other session is trying to remove or recreate, and the second run fails.
- There is **no root `conftest.py`** at the project root (a repo-wide conftest glob finds only subtree conftests under `platform_tests/scripts/`, `groundtruth-kb/tests/`, and `applications/Agent_Red/tests/`). So no current surface namespaces the basetemp per session/process; the collision window is structural.

Impact, concretely: this contamination is what forced the S377 §4 broad-pytest verification waiver — 13 parallel-contamination failures — recorded as `DELIB-S377-SLICE7PRIME-PYTEST-CONTAMINATION-WAIVER`. Until parallel sessions stop sharing a basetemp parent, broad pytest verification remains unreliable and waiver-prone.

This proposal adds the minimal fix: a root `conftest.py` whose `pytest_configure` hook, **only when no explicit `--basetemp` was supplied**, points pytest's basetemp at a per-process-unique subdirectory under the in-root `.pytest-tmp/` parent (namespaced by PID plus a short random suffix). Each parallel session/process then gets its own basetemp parent, so they cannot collide on ACLs. The `.pytest-tmp/` parent is already git-ignored (`.gitignore:79`, `.pytest-*/`). It adds no CLI, no API, no new requirement, and changes no test's behavior — it only relocates where temp dirs are rooted when the caller did not already choose.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — `bridge/INDEX.md` remains canonical workflow state; this proposal is filed and reviewed through the file bridge and changes no bridge mechanism. Source governing specification for the bridge-protocol surface this proposal travels on. (MemBase: present, v1.)
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — the in-root placement decision and the platform root-boundary rule. The fix roots every pytest temp directory under the in-root `.pytest-tmp/` parent (computed from the project root) and writes no out-of-root path, satisfying the in-root placement constraint; the test asserts the computed parent resolves inside the project root. (MemBase: present, v1.)
- GOV-RELIABILITY-FAST-LANE-001 — governs small single-concern defect fixes with no new behavior; this proposal's defect-removal shape maps to those criteria, though the operative authorization is the dedicated PAUTH below. (MemBase: present, v1.)
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification and maps proposed tests to them. (MemBase: present, v1.)
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation; the Spec-To-Test Mapping carries this forward to the post-implementation report. (MemBase: present, v1.)
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — the fix is preserved as durable artifacts (proposal, deliberation, report) with traceability to WI-3469 (advisory). (MemBase: present, v1.)

## Authorization

This work is authorized by the dedicated project-scoped authorization `PAUTH-WI-3469-PYTEST-BASETEMP-ISOLATION-001` under project `PROJECT-GTKB-MAY29-HYGIENE`, grounded in owner decision `DELIB-2548` (recorded; MemBase confirms `DELIB-2548` present). The authorization's `allowed_mutation_classes` are `["source", "test_addition", "hook_upgrade"]`, which cover exactly the mutations this proposal requests: a new root `conftest.py` source file (the `pytest_configure` basetemp hook is a `source` + `hook_upgrade` change) and a new regression test (`test_addition`). No mutation outside those classes is requested. Per `.claude/rules/codex-review-gate.md`, this project authorization is additive to — not a replacement for — the bridge GO and the implementation-start packet: after Loyal Opposition records GO, Prime Builder runs `python scripts/implementation_authorization.py begin --bridge-id gtkb-pytest-basetemp-session-isolation` before any protected edit.

## Prior Deliberations

- `DELIB-S377-SLICE7PRIME-PYTEST-CONTAMINATION-WAIVER` (MemBase, present) — the S377 owner waiver of the §4 broad-pytest verification gate for Slice 7-prime, caused by 13 parallel-contamination failures. That waiver is the direct motivation for WI-3469: it accepted the contamination as a one-time exception while the structural fix was deferred to this work item. This proposal is that structural fix; landing it removes the standing need for contamination waivers on broad pytest runs.
- `bridge/gtkb-cross-harness-trigger-import-repair-001.md` (VERIFIED elsewhere) is the structural exemplar for a small single-concern reliability defect fix under a project authorization; this proposal mirrors its scope discipline (one concern, minimal surface, no new behavior).
- The many bridge reports that pass ad-hoc `--basetemp=<in-root>` (e.g. `bridge/active-workspace-declaration-slice-1-007.md`, `bridge/gtkb-axis-2-scoping-terminal-classifier-fix-004.md`, `bridge/gtkb-backlog-update-cli-slice-1-006.md:66` which explicitly recommends "Future automation should include an in-root `--basetemp`") are the accumulated symptom record. They each solved the OS-temp-unreachable half locally but did not address parallel-session collision on a shared in-root parent, which is what this proposal fixes once, centrally.

## Owner Decisions / Input

- 2026-05-31 (S381): via AskUserQuestion the owner approved authorizing WI-3469 for implementation, recorded as owner decision `DELIB-2548`. The decision is operationalized as the dedicated project authorization `PAUTH-WI-3469-PYTEST-BASETEMP-ISOLATION-001` (project `PROJECT-GTKB-MAY29-HYGIENE`, allowed mutation classes `["source", "test_addition", "hook_upgrade"]`).
- No further owner decision is required before GO. The implementation scope is bounded by the cited authorization; no formal-artifact-approval packet is required because this proposal creates no GOV/SPEC/PB/ADR/DCL artifact and touches no protected narrative file.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation. The defect is non-compliance with the implicit reliability expectation that the test suite can run concurrently across sessions without temp-directory contamination; the fix introduces no new capability and removes no behavior. Origin is `defect` (WI-3469 `origin=defect`, confirmed live in `work_items`); the basetemp hook fires only when the caller gave no `--basetemp`, and test outcomes are unchanged; the scope is one new root `conftest.py` plus one regression test.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability defect fix: one new root `conftest.py` and one new regression test. It is NOT a bulk standing-backlog operation — it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3469) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: Per-session basetemp isolation via a root `conftest.py`

Add a new `conftest.py` at the project root. It defines a `pytest_configure(config)` hook that, only when the caller supplied no explicit `--basetemp` (detected via `config.option.basetemp` being falsy), sets `config.option.basetemp` to a per-process-unique path:

- Parent: the in-root `.pytest-tmp/` directory under the project root, computed from `conftest.py`'s own resolved location (`Path(__file__).resolve().parent / ".pytest-tmp"`). This parent is already git-ignored by `.gitignore:79` (`.pytest-*/`), so it never enters the index.
- Leaf: a subdirectory namespaced by the running process id plus a short random token, e.g. `session-<pid>-<6-hex>`. The PID makes parallel sessions (separate python processes) land in disjoint subtrees; the random token guards against PID reuse across sequential runs within the same parent.

The hook creates the parent directory if absent (`mkdir(parents=True, exist_ok=True)`) and assigns the per-session leaf as the basetemp. pytest then roots all `tmp_path` / `tmp_path_factory` allocations under that unique leaf. Because the assignment is conditional on no explicit `--basetemp`, every existing ad-hoc `--basetemp=<in-root>` invocation in current automation continues to behave exactly as today (the hook is a no-op when the caller already chose a basetemp). The hook touches nothing else: no markers, no fixtures, no collection behavior, no `cache_dir`.

The root `conftest.py` is intentionally minimal and does not import the heavy application fixtures; it is a configuration-only conftest, consistent with the shielding pattern already used at `platform_tests/scripts/conftest.py`.

### IP-2: Regression tests

Add `platform_tests/scripts/test_pytest_basetemp_isolation.py` covering:

- The `pytest_configure` hook, when given a config whose `option.basetemp` is unset/falsy, sets `option.basetemp` to a path **under the in-root `.pytest-tmp/` parent** and whose leaf name encodes the current PID.
- The hook is a **no-op when an explicit basetemp is already set**: given a config whose `option.basetemp` is already a chosen path, the hook leaves it unchanged (so existing `--basetemp=<in-root>` automation is preserved).
- **Two simulated concurrent sessions get distinct basetemp parents**: invoking the hook twice with two configs simulating two processes (distinct PIDs, or distinct random tokens) yields two different basetemp leaf paths that do not nest inside each other — proving parallel sessions cannot collide on the same subtree.
- The computed parent resolves inside the project root, satisfying the root-boundary rule.

The tests exercise the hook directly with lightweight config doubles (an object exposing `.option.basetemp`), so they do not spawn nested pytest processes and run fast under the suite's `--timeout=30`.

## Out Of Scope

- Changing `pyproject.toml:8-15` `addopts`, `testpaths`, or adding a `cache_dir` there — the fix is a conditional hook so it does not need to hard-code a basetemp into static config, and it must not override callers who already pass `--basetemp`.
- Removing or rewriting the existing ad-hoc `--basetemp` invocations in current bridge automation — they remain valid and the hook defers to them; a follow-on cleanup to standardize them is not part of this defect fix.
- The subtree conftests under `platform_tests/scripts/`, `groundtruth-kb/tests/`, and `applications/Agent_Red/tests/` — they are unchanged.
- Cleaning up previously-accumulated `.pytest-tmp/` / `.tmp/` contents — regenerable runtime state, not in scope for this source change.
- pytest-xdist worker isolation — parallel *sessions* are separate OS processes, not xdist workers, so PID-namespacing is the correct mechanism; xdist is not introduced.
- Any file outside `E:\GT-KB`. The basetemp parent is the in-root `.pytest-tmp/` directory; no out-of-root path is written.

## Files Expected To Change

- `conftest.py` (new, project root) — the `pytest_configure` hook that namespaces basetemp by PID under the in-root `.pytest-tmp/` parent when no explicit `--basetemp` was given (IP-1).
- `platform_tests/scripts/test_pytest_basetemp_isolation.py` (new) — regression coverage for IP-1, including the two-concurrent-sessions-distinct-parents case (IP-2).

No existing tracked file is modified; `.gitignore:79` already covers the in-root `.pytest-*/` parent, so no `.gitignore` change is required.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| GOV-RELIABILITY-FAST-LANE-001 (defect removal; no new behavior) | Test: when no explicit `--basetemp` is set, the hook roots basetemp at a per-PID leaf under the in-root `.pytest-tmp/` parent; when an explicit basetemp is set, the hook is a no-op (existing automation preserved). |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 (in-root placement) | Test: the computed basetemp parent resolves inside the project root (`E:\GT-KB`); no out-of-root path is ever written. |
| WI-3469 (parallel-session contamination removed) | Test: two simulated concurrent sessions (distinct PID / token) receive two distinct, non-nesting basetemp leaf paths, so parallel sessions cannot collide on the same ACL-bearing subtree. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | This proposal cites every relevant governing specification (verified present in MemBase) and maps each to a test. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The change is bridge-reviewed; `bridge/INDEX.md` remains canonical and no bridge mechanism is altered. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed test commands and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/scripts/test_pytest_basetemp_isolation.py -q --tb=short`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-pytest-basetemp-session-isolation`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-pytest-basetemp-session-isolation`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] A new root `conftest.py` defines a `pytest_configure` hook that sets basetemp to a per-PID-unique leaf under the in-root `.pytest-tmp/` parent only when no explicit `--basetemp` was supplied.
- [ ] When an explicit `--basetemp` is supplied, the hook leaves it unchanged (existing automation byte-for-byte preserved); covered by a test.
- [ ] Two simulated concurrent sessions receive distinct, non-nesting basetemp parents; covered by a test.
- [ ] The computed basetemp parent resolves inside `E:\GT-KB`; no out-of-root path is written.
- [ ] No change to `pyproject.toml`, no change to the existing subtree conftests, no `.gitignore` change (the `.pytest-*/` ignore at `.gitignore:79` already covers the parent).
- [ ] `ruff check conftest.py platform_tests/scripts/test_pytest_basetemp_isolation.py` and `ruff format --check` of the same files pass.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Risk And Rollback

**Risk R1 (low): the root `conftest.py` changes collection or fixture behavior for the existing suite.** Mitigation: the conftest is configuration-only — a single `pytest_configure` hook that sets `config.option.basetemp`; it defines no fixtures, markers, or collection hooks, so it cannot alter which tests run or how they assert. A regression test asserts the no-op-when-explicit branch.

**Risk R2 (low): the per-session basetemp parent accumulates leftover subtrees over time.** Mitigation: the parent is the already-ignored `.pytest-tmp/`; pytest's own retention policy prunes old per-session roots, and the directory is regenerable runtime state outside canonical project scope. No canonical state is involved.

**Risk R3 (low): a caller relies on the default OS-temp basetemp location.** Mitigation: GT-KB's established practice (per the cited bridge reports and `bridge/gtkb-backlog-update-cli-slice-1-006.md:66`) is to keep pytest temp output in-root; relocating the default to the in-root parent aligns with that practice and the root-boundary rule. Callers who explicitly pass `--basetemp` are unaffected (the hook defers to them).

Rollback: the change is two new files. Deleting `conftest.py` and `platform_tests/scripts/test_pytest_basetemp_isolation.py` restores the prior (no-central-basetemp) behavior exactly. No data migration and no canonical-artifact mutation are involved.

## Loyal Opposition Asks

1. Confirm that a root `conftest.py` `pytest_configure` hook (conditional on no explicit `--basetemp`) is the right structural choice versus a static `cache_dir`/`basetemp` in `pyproject.toml` — the conditional hook is chosen so existing `--basetemp=<in-root>` automation is preserved unchanged.
2. Confirm PID-plus-random-token namespacing under the in-root `.pytest-tmp/` parent is sufficient to guarantee parallel sessions get disjoint subtrees, versus a stronger keying (e.g. a session-id env var).
3. Confirm the scope boundary: fix the default basetemp collision only, leaving the existing ad-hoc `--basetemp` invocations and any later standardization cleanup out of this defect-fix thread.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
