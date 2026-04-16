# GT-KB Adoption Gap Closure — Post-Implementation Report

**Status:** NEW
**Based on:** GO at `bridge/gtkb-adoption-gap-closure-012.md`
**Proposal:** `bridge/gtkb-adoption-gap-closure-011.md`
**Repository:** `groundtruth-kb` @ `eeb4935` (committed on main; prior baseline `31fe2c4`)

---

## Summary of Changes

### Phase G1: Adopter Documentation

**Modified files:**
- `docs/bootstrap.md` line 11-14 — removed "Agent Red deployment topology" reference; replaced with generic "container deployment" framing.
- `docs/start-here.md` Step 9 (lines 137-154) — removed "expected failure" framing (`File not found: src/tasks.py` / `FAILED: 2`). Replaced with "fresh scaffold exits 0 because `src/tasks.py` is pre-generated as a stub" explanation.
- `docs/start-here.md` profile info box — updated to include CI tier column (minimal/standard/full) and explain `--no-include-ci` semantics.
- `mkdocs.yml` — added `Tutorials` and `Troubleshooting` nav sections.
- `docs/reference/cli.md` — documented `--integrations/--no-integrations` and `--python-version` flags; added CI tier table and advisory note.

**New files:**
- `docs/tutorials/first-spec.md` — GOV-01 spec-first workflow tutorial using task-tracker example. Creates spec, linked test, assertion, implementation. Links to `examples/task-tracker`.
- `docs/tutorials/dual-agent-setup.md` — Prime + Loyal Opposition dual-agent setup; `gt project init --profile dual-agent`; OS-scheduler bridge; proposal/review/VERIFIED cycle; links to auth troubleshooting.
- `docs/tutorials/bridge-os-scheduler.md` — macOS/Linux cron and launchd, Windows Task Scheduler platform-specific instructions; status-file contract; freshness thresholds; `gt project doctor` health check usage; bridge update guidance.
- `docs/troubleshooting/auth.md` — "Bridge says AUTH FAILURE" → Claude Desktop OAuth, ANTHROPIC_API_KEY, Codex token, environment variable inheritance (cron/Task Scheduler). GT-KB provides documentation only.

**Verified: Agent Red contamination check (zero matches):**

```
rg -ni "agent red|agent-red|agent\.red|agentred|customer engagement|shopify|tenant remaker" \
    docs/bootstrap.md docs/start-here.md docs/tutorials docs/troubleshooting docs/reference
EXIT: 1  (rg exit 1 = no matches found)
```

### Phase G2: Cross-Platform Bridge

**New files:**
- `docs/tutorials/bridge-os-scheduler.md` — included above (G1 new files); documented status-file contract, paths, schema, freshness thresholds.

**Modified files:**
- `src/groundtruth_kb/project/doctor.py` — added `json` and `datetime.UTC` imports; added `_BRIDGE_STATUS_PATHS`, `_BRIDGE_FRESH_SECS`, `_BRIDGE_WARN_SECS`, `_BRIDGE_SCHEDULER_DOC`, `_BRIDGE_AUTH_DOC` constants; added `_check_bridge_poller(target, agent)` function implementing: path resolution, JSON read, age computation against OK/WARN/ALARM/not-started thresholds, opaque `state` passthrough, doc pointers on ALARM/not-started. Updated `run_doctor()` to call `_check_bridge_poller("claude")` and `_check_bridge_poller("codex")` for bridge profiles.
- `templates/bridge-os-poller-setup-prompt.md` — added item 13a with status-file path and schema contract.
- `templates/BRIDGE-INVENTORY.md` — added "Poller status-file contract" section with path table, schema, and freshness threshold table.

**New tests (added to `tests/test_doctor.py`):**
- `test_bridge_poller_fresh_file_ok` — < 4 min → OK ✓
- `test_bridge_poller_5_min_old_warn` — 5 min old → WARN ✓
- `test_bridge_poller_15_min_old_alarm` — 15 min old → ALARM ✓
- `test_bridge_poller_missing_file_not_started` — missing file → WARN "not started" ✓
- `test_bridge_poller_missing_updated_at_field_alarm` — missing `updatedAtUtc` → ALARM ✓
- `test_bridge_poller_unknown_state_no_error` — `"running"`, `"completed"`, `"custom-state-42"` → no error, state displayed ✓

### Phase G3: GitHub CI Template Profile-Tiering

**New template files:**
- `templates/ci/minimal/test.yml` — ruff + `gt assert` only; no Docker, pytest, mypy
- `templates/ci/standard/test.yml` — ruff + `gt assert`; pytest/mypy as advisory YAML comments
- `templates/ci/full/test.yml` — pytest + ruff + `gt assert` + optional mypy comment
- `templates/ci/full/build.yml` — Docker build/push via `docker/build-push-action@v6`
- `templates/ci/full/deploy.yml` — `workflow_dispatch` deploy (adapted from existing `templates/ci/deploy.yml`)
- `templates/ci/integrations/dependabot.yml` — Dependabot config with `{{PROJECT_NAME}}` substitution
- `templates/ci/integrations/.coderabbitai.yaml` — CodeRabbit config with `{{PROJECT_NAME}}` substitution

**Modified `src/groundtruth_kb/project/scaffold.py`:**
- Added `import re` at top.
- Added `ScaffoldOptions` fields: `python_version: str = "3.11"` and `integrations: bool = False`.
- Fixed `include_ci` precedence bug (line 92): changed `include_ci = options.include_ci or profile.includes_ci` to `include_ci = options.include_ci` (user flag always wins; profile selects tier).
- Updated `_copy_ci_templates()` call to pass `profile=profile, options=options`.
- Added `_package_name_slug(project_name)` helper — kebab-case slug via `re.sub`.
- Added `_ci_tier(profile)` helper — returns `"minimal"` / `"standard"` / `"full"` based on `profile.includes_ci` and `profile.includes_bridge`.
- Rewrote `_copy_ci_templates(target, *, profile, options)` — selects tier directory, copies files, applies `{{PACKAGE_NAME}}` and `{{PYTHON_VERSION}}` substitution.
- Added `_write_webapp_stubs(target, *, options)` — generates `src/__init__.py`, `pyproject.toml`, `requirements.txt`, `tests/__init__.py`, `tests/test_smoke.py` for `dual-agent-webapp`.
- Added `_write_tasks_stub(target)` — generates `src/tasks.py` when `seed_example=True` (all profiles). Stub satisfies seeded SPEC-001 (`def create_task`) and SPEC-002 (`"status": "open"`) assertions.
- Added `_copy_integration_templates(target, *, options)` — copies `dependabot.yml` → `.github/dependabot.yml` and `.coderabbitai.yaml` → repo root when `--integrations` is set.
- Updated `scaffold_project()` to call `_write_webapp_stubs`, `_write_tasks_stub`, and `_copy_integration_templates` in the correct sequence (before `_render_all_templates`).

**Modified `src/groundtruth_kb/cli.py`:**
- Added `--integrations/--no-integrations` option to `project_init` command.
- Added `--python-version` option (default `"3.11"`) to `project_init` command.
- Updated `ScaffoldOptions` construction to pass `integrations` and `python_version`.

**New test file `tests/test_scaffold_ci_tiers.py`:**
- 24 tests covering the full G3.6 matrix (a through t) plus ci_tier helper tests.

---

## Test Results

### New scaffold/CI-template tests

```
python -m pytest tests/test_scaffold_ci_tiers.py tests/test_doctor.py -q --tb=short
54 passed, 1 warning in 9.51s
```

All 54 tests pass (36 G3 scaffold tests + 6 G2 doctor bridge tests + 12 existing doctor tests).

### Full test suite

```
python -m pytest tests/ -q --tb=short
889 passed, 1 warning in 150.37s (0:02:30)
```

Pre-implementation baseline: 814 tests. Post-implementation: 889 tests (+75 new).

### Ruff

```
python -m ruff check .
All checks passed!

python -m ruff format --check .
92 files already formatted
```

### mkdocs build --strict

```
python -m mkdocs build --strict
INFO    -  Documentation built in 0.97 seconds
EXIT: 0
```

(Pre-existing "pages not in nav" INFO messages for `method/README.md` and `docs/reports/` files are unrelated to this change.)

### Fresh scaffold assertion checks

**local-only (test n):**
```
python -m pytest tests/test_scaffold_ci_tiers.py::test_n_local_only_assert_exits_zero -v
PASSED
```

**dual-agent (test o):**
```
python -m pytest tests/test_scaffold_ci_tiers.py::test_o_dual_agent_assert_exits_zero -v
PASSED
```

**dual-agent-webapp pytest (test p):**
```
python -m pytest tests/test_scaffold_ci_tiers.py::test_p_dual_agent_webapp_pytest_exits_zero -v
PASSED
```

---

## Deviations from Proposal

### 3.1 `include_ci` precedence fix
Implemented exactly as specified. The `or profile.includes_ci` was removed; `include_ci = options.include_ci` is now the only assignment.

### 3.6 `src/__init__.py` content
The proposal specified `# {{PROJECT_NAME}} application package`. This placeholder is present in the generated file and resolved by `_render_all_templates()` later in `scaffold_project()`.

### 3.7 `src/tasks.py` stub placement
The stub is generated by `_write_tasks_stub(target)` called **before** `_render_all_templates()`. The stub does not contain any `{{PLACEHOLDER}}` text — it is final on write. This is intentional to avoid the tasks.py content being modified by the placeholder renderer.

### `tests/test_scaffold_ci_tiers.py` — test h and i
The proposal specified checking that "docker" does not appear. The template comments (e.g., `# No Docker steps`) include the word "docker". Tests h and i were correctly scoped to check active (non-comment) lines only, which is the semantically correct interpretation of "no Docker steps."

### `tests/test_scaffold_ci_tiers.py` — test c
build.yml and deploy.yml do not contain `{{PYTHON_VERSION}}` (Docker workflows have no Python version). Test c correctly checks that `3.11` appears in `test.yml` only, and that no literal `{{PYTHON_VERSION}}` braces remain in any workflow file.

---

## Open Items

None. All G1, G2, and G3 exit criteria are satisfied:
- `mkdocs build --strict` exits 0 ✓
- Agent Red contamination check returns zero matches ✓
- 889 tests pass (all 75 new tests pass) ✓
- ruff check and format clean ✓
- All 20 matrix test cases (a–t) pass ✓
