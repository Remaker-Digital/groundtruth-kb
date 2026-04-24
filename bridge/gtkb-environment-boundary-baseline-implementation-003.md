NEW

# GTKB Environment Boundary Baseline — Post-Implementation Report

bridge_kind: post_implementation_report
scope: protocol
work_item_ids: [GTKB-ISOLATION-011]
target_paths: [".dockerignore", "scripts/check_environment_isolation.py", "scripts/release_candidate_gate.py", "tests/scripts/test_check_environment_isolation.py", "tests/scripts/test_release_candidate_gate.py"]

## Summary

Implemented the Phase 3 environment-boundary baseline exactly as scoped in the
GO'd proposal (`bridge/gtkb-environment-boundary-baseline-implementation-002.md`):

1. New deterministic `scripts/check_environment_isolation.py` checker with
   human-readable text and `--json` output.
2. `.dockerignore` hardening to cover the four missing GT-KB
   governance/runtime surfaces (`.codex/`, `.groundtruth/`, `bridge/`,
   correctly-spelled `independent-progress-assessments/`). The legacy
   misspelled `independent-progress-assments/` entry was retained for
   defence-in-depth against stale path references.
3. Release-gate wiring in `scripts/release_candidate_gate.py`: new checker
   call inserted between `check_codex_hook_parity.py` and the pytest lane,
   and `tests/scripts/test_check_environment_isolation.py` added to the
   release-gate pytest target list.
4. Focused regression tests: 30-test module for the checker + one new
   ordering assertion extending `test_release_candidate_gate.py`.

Nothing was implemented outside scope: no `.devcontainer` / Codespaces
files, no workflow-file edits, no startup/hook guardrails, no service-boundary
logic, no overlay mechanics, no migration rehearsal, no packaging.

## Files Changed (Commit-Local Delta)

```
 .dockerignore                                |  7 ++++++
 scripts/release_candidate_gate.py            | 16 +++++++++----
 tests/scripts/test_release_candidate_gate.py | 34 +++++++++++++++++++++++++---
 3 files changed, 49 insertions(+), 8 deletions(-)
```

New untracked files in scope:

- `scripts/check_environment_isolation.py` (~310 LOC)
- `tests/scripts/test_check_environment_isolation.py` (~360 LOC, 30 tests)

Other modified paths currently present in `git status` are pre-existing
drift / sibling-workstream changes and are intentionally not part of this
slice (e.g., `scripts/check_codex_hook_parity.py`,
`scripts/session_self_initialization.py`,
`tests/scripts/test_codex_hook_parity.py`,
`tests/scripts/test_session_self_initialization.py`,
`tests/scripts/test_standing_backlog_harvest.py`,
`tests/scripts/test_groundtruth_governance_adoption.py`). This slice did
not touch them.

## Checker Contract (Delivered)

Command form matches proposal:

```powershell
python scripts/check_environment_isolation.py --json
```

JSON shape (live-repo run, redacted for brevity):

```json
{
  "cwd": "<absolute cwd>",
  "default_gtkb_dependency_mode": "released_package",
  "findings": [],
  "git_branch": "main",
  "git_remote": "https://github.com/Remaker-Digital/agent-red-customer-engagement.git",
  "repo_root": "<absolute repo root>"
}
```

Exit code 0 on zero `error` findings, 1 otherwise. `--root` flag added for
test ergonomics (does not change production behaviour; the release gate
invokes the checker without `--root`).

### Policy Rules Implemented

| Code | Severity | Surface | Trigger |
|------|----------|---------|---------|
| `DOCKERIGNORE_MISSING_FILE` | error | `.dockerignore` | file absent |
| `DOCKERIGNORE_MISSING_RULE` | error | `.dockerignore` | any of `.codex`, `.groundtruth`, `bridge`, `independent-progress-assessments`, `groundtruth.db`, `.groundtruth-chroma` not present |
| `DOCKERFILE_FORBIDDEN_COPY` | error | `Dockerfile` | `COPY` first segment matches any of `.claude`, `.codex`, `.groundtruth`, `bridge`, `independent-progress-assessments`, `groundtruth.db` |
| `COMPOSE_HOST_BIND_OUT_OF_APP` | error | `docker-compose.yml` | host bind path is absolute, starts with `..`, or contains `/../` |
| `COMPOSE_SOURCE_BIND_NOT_READONLY` | error | `docker-compose.yml` | bind starts with `./src`, `./app`, or `./scripts` and lacks `ro` option |
| `REQUIREMENTS_EDITABLE_GTKB_SIBLING` | error | `requirements*.txt` | uncommented `-e ...groundtruth-kb` line in any default requirement file |

### Probed Environment Metadata

- `cwd`, `repo_root`, `git_remote`, `git_branch` — obtained via targeted
  `git` subprocess calls that degrade to `null` on any failure (missing git
  binary, detached HEAD, no remote).
- `default_gtkb_dependency_mode` — derived from
  `requirements.txt`, `requirements-test.txt`, and `requirements-local.txt`;
  emitted as `released_package`, `editable_local`, or `missing`.

## Verification Commands (Executed)

### Checker, direct invocation

```
$ python scripts/check_environment_isolation.py --json
{
  "cwd": "E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement",
  "default_gtkb_dependency_mode": "released_package",
  "findings": [],
  "git_branch": "main",
  "git_remote": "https://github.com/Remaker-Digital/agent-red-customer-engagement.git",
  "repo_root": "E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement"
}
```

Exit code: 0. No `error` findings.

### Focused pytest

```
$ python -m pytest tests/scripts/test_check_environment_isolation.py \
                   tests/scripts/test_release_candidate_gate.py -q --tb=short
collected 38 items
tests\scripts\test_check_environment_isolation.py  ......................  [ 57%]
........                                                                 [ 78%]
tests\scripts\test_release_candidate_gate.py       ........              [100%]
============================= 38 passed in 0.78s ==============================
```

Ordering assertion in the new release-gate test confirms the intended
dispatch sequence at the `_python_gates()` level:

```
codex_hook_parity  <  check_environment_isolation  <  pytest
```

### Live-Repo Sanity Case

The checker was exercised against the live Agent Red repo (not just
tmp-path fixtures) via
`test_repository_passes_its_own_checker`. The test reports
zero `error` findings for the current tree, confirming that the
`.dockerignore` hardening in this slice closes all rules enforced by the
checker.

## Test Inventory

`tests/scripts/test_check_environment_isolation.py` (30 tests):

- `test_clean_tree_produces_no_findings` — golden-path zero-findings
- `test_missing_dockerignore_rule_is_reported`
- `test_missing_dockerignore_file_is_reported`
- `test_forbidden_dockerfile_copy_is_reported`
- `test_forbidden_copy_matches_unprefixed_segment`
- `test_dockerfile_allows_approved_copy_sources`
- `test_compose_rejects_host_bind_escaping_repo`
- `test_compose_rejects_absolute_host_bind`
- `test_compose_requires_source_bind_read_only`
- `test_compose_ignores_port_mappings_and_named_volumes`
- `test_detect_gtkb_mode_released`
- `test_detect_gtkb_mode_editable_sibling_is_reported`
- `test_detect_gtkb_mode_missing`
- `test_detect_gtkb_mode_ignores_commented_editable_line`
- `test_editable_line_without_other_gtkb_still_marks_editable`
- `test_build_report_populates_probe_fields`
- `test_build_report_degrades_when_git_unavailable`
- `test_json_output_shape`
- `test_main_exits_nonzero_on_error_finding`
- `test_git_probe_handles_missing_git_binary`
- `test_repository_passes_its_own_checker`
- `test_script_runs_as_cli`
- `test_repeated_probe_is_deterministic`
- `test_dockerignore_accepts_unslashed_entries`
- `test_dockerignore_ignores_comments_and_negations`
- plus 5 parameterized `test_first_path_segment_strips_prefixes` cases

`tests/scripts/test_release_candidate_gate.py`: added
`test_python_gate_runs_environment_isolation_before_pytest` asserting
the ordering `parity_index < env_index < pytest_index` and membership
of `tests/scripts/test_check_environment_isolation.py` in the pytest
target list.

## Compliance With Required Implementation Boundaries

Per -002 review:

| Boundary | Status |
|----------|--------|
| Limited to static env checks, `.dockerignore` hardening, release-gate visibility | Kept |
| No workflow-file edits, hook/subject enforcement, scoped-service logic, or overlay | Kept |
| Correctly-spelled `independent-progress-assessments/` added alongside misspelled legacy | Kept |

## Non-Scope Confirmation

Not touched (explicit out-of-scope list from the proposal):

- `.devcontainer/` / Codespaces files — not created.
- `.github/workflows/*` — not modified.
- `scripts/workstream_focus.py` and `.claude/hooks/workstream-focus.py` — not touched.
- `scripts/session_self_initialization.py` — not touched by this slice (the
  `M` entry in `git status` is pre-existing sibling-workstream drift).
- Overlay/promotion behaviour — not touched.
- Migration rehearsal, root moves, GT-KB packaging — not touched.

## Risk Assessment

- **Blast radius:** static-analysis-only script; no network calls, no
  writes outside stdout. `_git()` swallows `FileNotFoundError`,
  `TimeoutExpired`, `OSError` so the checker cannot crash the release
  gate on a host without git.
- **Release-gate additive wiring:** only adds one new command call
  between existing lanes; prior ordering invariants remain verified by the
  unchanged `test_python_gate_runs_codex_hook_parity_before_pytest` test.
- **False positives on `Dockerfile`:** `_COPY_PATTERN` intentionally accepts
  lines matching `COPY <src> <dst>` (one source token). Multi-source
  `COPY a b c /dst/` forms are not matched; acceptable for the current
  `Dockerfile` which uses single-source `COPY` throughout and consistent
  with the "initial static checks" scope.

## Requested Verdict

VERIFIED — the implementation lands the proposed Phase 3 baseline slice
in scope, all focused tests pass, and the live checker emits zero `error`
findings against the current tree.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
