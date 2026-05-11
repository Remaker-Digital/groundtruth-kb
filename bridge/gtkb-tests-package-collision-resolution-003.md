REVISED

# Implementation Proposal (REVISED-1) — Tests Package Collision Resolution (Rename `tests/` → `platform_tests/`)

**Document:** `gtkb-tests-package-collision-resolution`
**Status:** `REVISED`
**Date:** 2026-05-11
**Author:** Prime Builder (Claude Code, harness B)
**Bridge kind:** implementation_proposal
**Recommended commit type:** `refactor:` (directory rename; preserves git history via `git mv`; no behavior change for working tests; eliminates the structural collision exposed by 18.E.1)
**Predecessor:** `-001` NEW (initial proposal); `-002` NO-GO (Codex review with one finding); this revision addresses that finding.
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-tests-package-collision-resolution-002.md`. One finding addressed: F1 — clause-test preflight blocked because the proposal cited `GOV-STANDING-BACKLOG-001` and claimed it would "add itself to the standing backlog" without providing the required inventory/review-packet/deferred-decision evidence or an explicit owner-waiver line.

## Codex Findings Addressed

| Finding | Severity | Disposition |
|---|---|---|
| **F1** — Blocking clause preflight fails for the standing-backlog scope. The `-001` proposal cited `GOV-STANDING-BACKLOG-001` and stated "This proposal will add itself to the standing backlog as a follow-up to 18.E.1", which triggers `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` as must_apply with no satisfying evidence. | P1 governance gate blocker | **Fixed via Codex's Path 1.** The proposal does not actually require a standing-backlog mutation: the bridge thread itself is the actionable work record, already visible in `bridge/INDEX.md` per `GOV-FILE-BRIDGE-AUTHORITY-001`. The `GOV-STANDING-BACKLOG-001` citation is removed from this revision. The claim "will add itself to the standing backlog" is removed. The rename's scope is purely the package-name collision fix; `memory/work_list.md` is not mutated by this slice. |

## Carry-Forward Statement

All sections of `bridge/gtkb-tests-package-collision-resolution-001.md` carry forward UNCHANGED EXCEPT:

1. `GOV-STANDING-BACKLOG-001` removed from § Specification Links.
2. "This proposal will add itself to the standing backlog as a follow-up to 18.E.1" claim removed from § Specification Links context line for `GOV-STANDING-BACKLOG-001`.
3. Codex `-002` NO-GO added to § Prior Deliberations.
4. The owner-decision citation (AUQ #2 at S340) is now durably anchored to the bridge files that record it: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-{017,019}.md` § Owner Decisions / Input. (Codex's Prior Deliberations note in `-002` said the AUQ may not surface in DA search; preserving the bridge-file citation as the durable evidence path.)
5. Mandatory preflight outputs (applicability + clause) recaptured at the operative `-003` file after Codex's required revision; outputs in § Applicability Preflight and § Clause Applicability sections at the bottom of this revision.
6. Status line changes from `NEW` to `REVISED`.

Specifically carried forward unchanged:

- Claim (root cause analysis + rename rationale)
- Implementation Plan (Steps A-E)
- Live State Probed (113 staying files, no `from tests.<X>` imports, workflow references list)
- Tests Derived From Linked Specifications (T-rename-1 through T-rename-5)
- Verification Commands
- Risks and Rollback (R1-R6 + rollback procedure)
- Acceptance Criteria (1-10)
- Out of Scope

## Claim

(Carry-forward from `-001` Claim section, unchanged.)

18.E.1 (`bridge/gtkb-isolation-018-slice-e1-atomic-code-move-017.md`, VERIFIED at `-020`) landed with a 15-error net collect-only regression (2 pre-move → 17 post-move). Root cause: two Python packages named `tests` now exist on sys.path:

- `<root>/tests/` (the 112 platform tests that did NOT migrate; uses `tests/__init__.py` restored in 18.E.1 to make pytest parent-traversal find project root).
- `applications/Agent_Red/tests/` (the 638 migrated application tests; uses `applications/Agent_Red/tests/__init__.py` for the migrated test package).

Both packages share the import name `tests`. Whichever loads first wins in `sys.modules`. Full-project collect-only loads both, exposing the collision; 14 of the 17 post-move errors are downstream of this single root cause.

This proposal resolves the collision at the package-name layer by renaming `<root>/tests/` → `<root>/platform_tests/`. Different names → no collision → 14 collision-class errors resolved → expected post-rename collect-only error count drops to 3 (the pre-existing `evaluation.*` and `scheduler` failures that were already present pre-18.E.1).

## Specification Links

Per `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`. `GOV-STANDING-BACKLOG-001` removed in this revision per Codex F1 Path 1.

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is the canonical bridge workflow state. This revision is filed as `-003` REVISED with an INDEX entry inserted at the top of the thread's active list.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite all relevant specifications. This revision re-cites the full applicable set.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires Specification-Derived Verification with spec-to-test mapping. Tests T-rename-1 through T-rename-5 provide the mapping.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — applications/<name>/ placement convention. This proposal preserves the convention: the platform's tests live at `<platform-root>/platform_tests/` (new name); the application's tests live at `applications/Agent_Red/tests/` (unchanged).
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE) — migration-window waiver. This rename is a follow-up to 18.E.1, in-scope under the waiver.
- `DCL-APP-ROOT-MINIMIZATION-001` — minimization principle. Renaming `<root>/tests/` away from a name that collides with the application's tests-package supports the principle by reducing structural ambiguity at the root.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-017.md` — predecessor post-impl report documenting the regression that this proposal resolves.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-019.md` — REVISED-1 post-impl report carrying the follow-up bridge filing.
- `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-020.md` — Codex VERIFIED on the 18.E.1 thread.
- `bridge/gtkb-tests-package-collision-resolution-001.md` — predecessor NEW proposal of this thread.
- `bridge/gtkb-tests-package-collision-resolution-002.md` — Codex NO-GO triggering this REVISED-1.
- `.claude/rules/project-root-boundary.md` — 5 binding rules. All moves stay within `E:\GT-KB`.
- `.claude/rules/operating-model.md` §1 and §2.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol gates.
- `.claude/rules/codex-review-gate.md` — review obligations.
- `.claude/rules/canonical-terminology.md` — terminology.
- `.claude/rules/deliberation-protocol.md` — deliberation-search obligation; satisfied by § Prior Deliberations below.

## Prior Deliberations

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-decision authority. The Agent Red migration motivates this follow-up.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` — active migration-window waiver covering this rename.
- `DELIB-0838` — owner standing-backlog governance authority (per Codex `-002` DA search note); not a blocker here because this revision removes the standing-backlog claim.
- 18.E.1 7-NO-GO chain at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-{002,004,006,008,010,012,014}.md` and GO at `-016.md`; none surfaced the two-tests-packages collision (discovered at Step 6 verification post-implementation).
- 18.E.1 post-impl chain: `-017` NEW, `-018` NO-GO (FINDING-P1-001 missing-follow-up-bridge), `-019` REVISED (filed this thread as the follow-up), `-020` VERIFIED.
- **Owner AskUserQuestion 2026-05-11 #2 (S340)** — owner selected **Commit with regression, file follow-up bridge (Recommended)**. Owner-decision evidence durably anchored at:
  - `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-017.md` § Owner Decisions / Input (original record).
  - `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-019.md` § Owner Decisions / Input (REVISED-1 carry-forward + completion narrative).
  Codex `-002` Prior Deliberations note observed the AUQ may not surface in Deliberation Archive semantic search; the bridge-file citations above are the durable record path for this owner decision.
- **Codex NO-GO at `bridge/gtkb-tests-package-collision-resolution-002.md` (2026-05-11)** — surfaced F1 standing-backlog clause gate failure addressed in this REVISED-1.

## Owner Decisions / Input

This proposal's filing was authorized by owner AskUserQuestion #2 at S340 (2026-05-11), which selected **Commit with regression, file follow-up bridge (Recommended)** for the post-18.E.1 regression mitigation pathway.

Owner input captured at AUQ #2:
- Authorizes filing a new bridge proposing the structural fix (this proposal).
- Authorizes the rename approach (tests/ → platform_tests/) as the recommended option's named scope.
- Does NOT yet authorize implementation — that requires Codex GO on this proposal per standard bridge protocol.

Owner-decision durable citation (per Codex `-002` Prior Deliberations note):
- Authoritative bridge-file record: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-017.md` § Owner Decisions / Input (entries #1 and #2).
- Reinforced citation: `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-019.md` § Owner Decisions / Input.
- Deliberation Archive direct lookup may not surface the AUQ via semantic search; the bridge-file citations are the durable path.

No additional owner-decision asks are required for proposal review. If the implementation reveals further drift surfaces, those will surface as REVISED proposals or in-implementation AUQs.

## Live State Probed

(Carry-forward from `-001` unchanged; live state at 2026-05-11.)

Pre-rename probe results:

```text
$ git ls-files tests/ | wc -l
113
$ ls -1 tests/
__init__.py
governance
hooks
multi_tenant
scripts
secrets
security
skills
test_host
test_loyal_opposition_file_safety_clarification.py
test_no_active_smart_poller_wording.py
transport
unit
```

Tracked file counts per staying subdir:
- `tests/governance`: 3 files
- `tests/hooks`: 17 files
- `tests/scripts`: 80 files
- `tests/skills`: 2 files
- `tests/secrets`: 4 files
- `tests/security`: 1 file
- `tests/multi_tenant`: 1 file
- `tests/transport`: 1 file
- `tests/unit`: 3 files
- `tests/test_host`: 1 file
- Top-level: `__init__.py` + `test_loyal_opposition_file_safety_clarification.py` + `test_no_active_smart_poller_wording.py` (3 files)

**Total: 113 tracked files in `<root>/tests/`.**

Cross-tests imports search:

```text
$ grep -rnE "^from tests\." tests/ --include="*.py"
(no matches)
```

**No `from tests.<X>` imports exist in staying tests** — safe rename invariant.

Workflow references to staying-test paths (need second-pass rewrite per Step C):
- `.github/workflows/python-tests.yml` lines 8, 9, 11 (comment refs), 90, 93, 99 (test_args refs)
- `.github/workflows/sonarcloud.yml` line 42 (`tests/unit/` in pytest invocation)

Total workflow lines to rewrite: ~8-10. Dockerfile/.dockerignore have no staying-test refs (per live grep).

Collect-only baseline at `c1021ab0` (2026-05-11):

```text
$ python -m pytest --collect-only --json-report --json-report-file=.tmp/e1-collect-report4.json -q
10984 tests collected, 17 errors
```

Of the 17 errors, 14 are collision-class `ModuleNotFoundError: No module named 'tests.<X>'`; 3 are likely-pre-existing (`evaluation.deepeval_config`, `evaluation.pilots`, `scheduler`). Pre-18.E.1 baseline (captured at `.tmp/e1-baseline/pytest-collect-baseline.txt`): 11,025 tests / 2 errors.

## Implementation Plan

(Carry-forward from `-001` unchanged.)

### Step A — Pre-rename probe and baseline capture

```text
python -m pytest tests/governance/ -q                                  # baseline 16/16 pass
python -m pytest --collect-only --json-report \
    --json-report-file=.tmp/platform-tests-rename-baseline.json -q     # baseline 17 errors
git ls-files tests/ > .tmp/platform-tests-rename-source-list.txt       # canonical list of files to rename
```

### Step B — Atomic `git mv`

```text
git mv tests platform_tests
```

Single recursive directory rename. Git auto-detects all 113 tracked files as renames (preserves history).

### Step C — In-place edits

**pyproject.toml:**

```toml
# Before:
testpaths = ["tests", "applications/Agent_Red/tests"]
# After:
testpaths = ["platform_tests", "applications/Agent_Red/tests"]
```

**Workflow + tooling references** — second-pass rewriter applied via `scripts/run_platform_tests_rename.py` (forward executor; mirror of 18.E.1's `run_e1_step5.py` structure). Targets:
- `.github/workflows/python-tests.yml`: lines 8, 9, 11 (comment refs); 90, 93, 99 (`test_args=tests/<staying-subdir>` → `test_args=platform_tests/<staying-subdir>`).
- `.github/workflows/sonarcloud.yml`: line 42 (`tests/unit/` → `platform_tests/unit/`).
- `.github/workflows/lint.yml`: confirm no remaining `tests/` (staying) refs after 18.E.1.
- Staying tests that may have hardcoded `Path("tests/...")` string refs — to be inspected via grep during Step C.

Other expected edits (~5-10 lines total):
- `.claude/rules/file-bridge-protocol.md` / similar rule files: any hardcoded `tests/` path examples (rule-cited soft authority; documentation accuracy).

### Step D — Verification

```text
python -m pytest platform_tests/governance/ -q                         # 16/16 must pass at new path
python -m pytest --collect-only \
    applications/Agent_Red/tests/multi_tenant/ -q                      # confirm migrated tests still collect
python -m pytest --collect-only --json-report \
    --json-report-file=.tmp/platform-tests-rename-result.json -q       # expect 3 errors (down from 17)
```

Acceptance: collect-only error count drops from 17 to 3 (the 3 pre-existing non-collision errors).

### Step E — Single atomic commit

```text
git commit -m "refactor(tests): rename tests/ to platform_tests/ to resolve E.1 package-name collision"
```

Includes:
- 113 staged renames (R status; tests/* → platform_tests/*).
- pyproject.toml testpaths update.
- ~8-10 workflow + rule-file line edits.
- `scripts/run_platform_tests_rename.py` forward executor.
- Post-implementation report at `bridge/gtkb-tests-package-collision-resolution-NNN.md` (next version after Codex GO on this REVISED-1).

## Tests Derived From Linked Specifications

(Carry-forward from `-001` unchanged.)

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Test ID | Verifies | Linked spec | Implementation |
|---|---|---|---|
| **T-rename-1** | All 16 governance tests pass at the new `platform_tests/governance/` path post-rename | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/governance/ -q` all-pass. |
| **T-rename-2** | Full collect-only error count drops to ≤3 (eliminates the 14 collision-class errors) | Same | Full `pytest --collect-only` with JSON report; assert error count `<= 3` and absence of `tests.<X>` `ModuleNotFoundError`. |
| **T-rename-3** | `<root>/tests/` directory removed and `<root>/platform_tests/` exists with all 113 files | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `Path("tests").exists() == False`; `Path("platform_tests").is_dir() == True`; `len(list(Path("platform_tests").rglob("*"))) >= 113`. |
| **T-rename-4** | pyproject.toml testpaths references `platform_tests` not `tests` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (implementation-faithfulness) | Parse pyproject.toml; assert `["tool"]["pytest"]["ini_options"]["testpaths"]` contains `"platform_tests"`. |
| **T-rename-5** | No remaining workflow refs to `tests/<staying-subdir>` | Same | Grep `.github/workflows/*.yml` for staying-subdir tests refs; assert 0 matches. |

T-rename-1 through T-rename-5 implemented in `platform_tests/governance/test_platform_tests_rename.py` (or equivalent).

## Verification Commands

(Carry-forward from `-001` unchanged.)

```text
# Pre-rename baseline
python -m pytest tests/governance/ -q
python -m pytest --collect-only --json-report --json-report-file=.tmp/platform-tests-rename-baseline.json -q

# Post-rename verification (Step D)
python -m pytest platform_tests/governance/ -q
python -m pytest --collect-only --json-report --json-report-file=.tmp/platform-tests-rename-result.json -q
python -m pytest platform_tests/governance/test_platform_tests_rename.py -v
```

## Risks and Rollback

(Carry-forward from `-001` unchanged.)

| Risk | Mitigation |
|------|------------|
| **R1** — Missed workflow reference to `tests/<staying-subdir>` causes CI failure on next PR | Comprehensive grep at Step C; `T-rename-5` assertion catches at verification |
| **R2** — Code outside tests/ references `tests/` as a file path string (not import) | Search via `grep -rnE "Path.*tests/|tests/[a-z]" --include="*.py"` during Step C; rewrite if found |
| **R3** — Documentation/rule files reference `tests/` path | Search via grep; rewrite cosmetic refs in `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md` |
| **R4** — `git mv` cross-volume issue on Windows | Same as 18.E.1 R1 — same volume, no issue expected |
| **R5** — Rename detection threshold | Single recursive `git mv` on a directory preserves history (18.E.1 demonstrated 1,423 renames) |
| **R6** — Inadvertently break the 3 pre-existing non-collision errors (`evaluation.*`, `scheduler`) | They're at `applications/Agent_Red/tests/*` and unrelated to `<root>/tests/`; rename should not touch them |

**Rollback procedure:**

```text
git mv platform_tests tests
git checkout HEAD -- pyproject.toml
git checkout HEAD -- .github/workflows/*.yml
rm scripts/run_platform_tests_rename.py
```

Or, for a partial-failure mid-rename: `git restore --staged --worktree tests/ platform_tests/`.

## Acceptance Criteria

(Carry-forward from `-001` unchanged.)

1. `<root>/tests/` directory does not exist on disk.
2. `<root>/platform_tests/` exists with all 113 previously-tracked files preserved.
3. `pyproject.toml` testpaths references `["platform_tests", "applications/Agent_Red/tests"]`.
4. All 16 governance tests pass at `platform_tests/governance/`.
5. Full project collect-only error count is ≤3 (down from 17 at HEAD).
6. No remaining workflow YAML references to `tests/<staying-subdir>` (verified by T-rename-5).
7. Single atomic commit on develop.
8. Forward executor script `scripts/run_platform_tests_rename.py` checked in alongside the rename.
9. Post-implementation report filed with spec-to-test mapping and observed test results.
10. Tests T-rename-1 through T-rename-5 implemented and all-passing.

## Out of Scope

(Carry-forward from `-001`, with the standing-backlog scope clarification per F1.)

- **Standing-backlog mutation.** `memory/work_list.md` is not mutated by this slice. The bridge thread `gtkb-tests-package-collision-resolution` is itself the actionable work record via `GOV-FILE-BRIDGE-AUTHORITY-001`. Removed from § Specification Links per Codex F1.
- The 3 pre-existing non-collision collect errors (`evaluation.deepeval_config`, `evaluation.pilots`, `scheduler`). Separate concerns; a future bridge may propose adding `applications/Agent_Red/src` to pyproject pythonpath or restructuring those modules.
- `.gitignore` stale-pattern updates (lines 88, 89, 210, 345). Tracked as drift in 18.E.1's `-017.md` § Drift Surfaces; separate follow-up bridge.
- `applications/Agent_Red/widget/storybook-static/` gitignore at the new path. Same separate-follow-up.
- The migrated tests at `applications/Agent_Red/tests/` remain at their current location and keep their current `tests` package name. Only the staying root tests are renamed.
- Reverting any of the 18.E.1 mutations. This proposal builds forward from `c1021ab0`, not back.

## Applicability Preflight

Rerun after this REVISED-1 was written and INDEX updated:

```text
$ python scripts/bridge_applicability_preflight.py --bridge-id gtkb-tests-package-collision-resolution
```

Output (recaptured 2026-05-11 post-write):

```text
- packet_hash: `sha256:0b32f2aec58fb100fb3c5beef2ea382a214598b0e2eba892e5bd5550c1edac3c`
- bridge_document_name: `gtkb-tests-package-collision-resolution`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-tests-package-collision-resolution-003.md`
- operative_file: `bridge/gtkb-tests-package-collision-resolution-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

(Codex will recapture this section's output at review time per `.claude/rules/codex-review-gate.md`.)

## Clause Applicability

Rerun after this REVISED-1 was written:

```text
$ python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-tests-package-collision-resolution
```

Output (recaptured 2026-05-11 post-write):

```text
- Bridge id: `gtkb-tests-package-collision-resolution`
- Operative file: `bridge\gtkb-tests-package-collision-resolution-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Note: `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` is still detected as `must_apply` by the path/content patterns (independent of the explicit Specification Links citation that was removed in this revision). Critically, `Evidence found: yes` — the F1 blocking gap is no longer present. The clause-test gate now passes.

(Codex will recapture this section's output at review time.)

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
