# GT-KB Adoption Gap Closure — Revised Implementation Plan

**Status:** REVISED
**Prime Builder:** Claude Sonnet 4.6 (auto-spawn)
**Author session:** S296 (auto-spawn)
**Scope:** Close adoption gaps for GroundTruth-KB developer-preview readiness
**Repository:** `groundtruth-kb` @ `31fe2c4` (main)
**Depends on:** `gtkb-mass-adoption-readiness-012` VERIFIED (MVP landed at `12fd083`)
**Addresses:** NO-GO at `bridge/gtkb-adoption-gap-closure-008.md`

---

## NO-GO Response Summary (from -008)

Both findings addressed:

| Finding | Severity | Resolution in this revision |
|---------|----------|-----------------------------|
| F1 — G3 contradicts itself on CI defaults (tristate + profile-default vs. default-on exit criterion) | P1 | Chose **current default-on semantics** per Codex recommendation. `--include-ci` default is `True`; profile's `includes_ci` field determines which CI tier to generate, not whether CI is generated. Tristate design removed. `scaffold.py` uses `options.include_ci` directly. Exit criteria updated consistently. |
| F2 — Proposed `minimal` CI tier inherits Docker/pytest steps that don't match `local-only` generated artifacts | P1 | Defined profile-aligned CI tier contents based on each profile's actual generated files. `minimal` has no Docker/pytest. `standard` has no Docker. `full` (`dual-agent-webapp`) additionally generates `src/__init__.py`, `pyproject.toml` stub, and `requirements.txt` stub so Docker build steps are not broken out-of-box. Alignment tests added. |

---

## Prior Deliberations

- `DELIB-GTKB-INIT-POSTURE`: `gt init` = Layer 1; `gt project init` = scaffold entry point.
- `DELIB-GTKB-TOKEN-POSTURE`: GT-KB may not manage auth tokens; docs + doctor pointers only.
- `DELIB-0474`: Staged execution; productized gating required before stable claims.
- `DELIB-0633`: GT-KB is "promising but still alpha"; not proven as a repeatable multi-project platform.
- `DELIB-0211`, `DELIB-0472`, `DELIB-0184`, `DELIB-0601`, `DELIB-0229`: Mass-adoption readiness context.
- `bridge/gtkb-mass-adoption-readiness-012.md`: MVP VERIFIED — bridge INDEX scaffolding, provider templates, doctor accuracy, bridge rule templates landed.
- `bridge/gtkb-adoption-gap-closure-006.md`, `-008.md`: Prior NO-GOs. `-008` rejected tristate design due to internal contradiction; rejected existing CI templates for `minimal` tier due to artifact mis-alignment.

---

## Context (unchanged)

The owner asked whether GT-KB is ready for mass adoption. The answer is no. The correct framing, consistent with DELIB-0633 and prior NO-GO F4, is: **GT-KB can achieve "developer preview" / "beta candidate" readiness** via the gaps below. "Mass adoption" follows a successful field trial (G5), not the completion of docs/CI/bridge work alone.

---

## Revised Gap Baseline (against `31fe2c4`)

Each gap is classified as **ABSENT** (nothing exists) or **PRESENT BUT INSUFFICIENT** (exists; specific delta needed).

| # | Gap | Classification | What exists | What is missing |
|---|-----|----------------|-------------|-----------------|
| **G1** | Adopter documentation | **PRESENT BUT INSUFFICIENT** | `docs/bootstrap.md` (getting-started guide); `docs/start-here.md` (scaffold walkthrough); `examples/task-tracker/WALKTHROUGH.md` (non-Agent-Red example) | `bootstrap.md:12` references Agent Red deployment topology; no "Your First Specification" tutorial; no dual-agent setup guide for new developers; no auth troubleshooting doc |
| **G2** | Cross-platform bridge | **PRESENT BUT INSUFFICIENT** | OS-scheduler contract documented in `docs/method/12-file-bridge-automation.md`; generated `templates/bridge-os-poller-setup-prompt.md`; `templates/rules/bridge-essential.md` explicitly says bridge scheduler commands are not implemented in this release | Mac/Linux OS-scheduler setup instructions absent; `gt project doctor` does not check bridge freshness; no auth troubleshooting pointer from doctor; **no status-file path/schema contract in generated templates or inventory** |
| **G3** | GitHub CI templates | **PRESENT BUT INSUFFICIENT** | `templates/ci/build.yml`, `deploy.yml`, `test.yml`; `scaffold.py:322-328` copies all `templates/ci/*.yml` into `.github/workflows/`; `--no-include-ci` flag exists | **Workflows are not profile-tiered**; existing templates assume Docker/pytest/pyproject that most profiles do not generate; `--no-include-ci` does not currently override `dual-agent-webapp`'s `includes_ci=True`; no `{{PACKAGE_NAME}}` or `{{PYTHON_VERSION}}` placeholders |
| **G4** | ZK + multi-tenant patterns | **OUT OF SCOPE** | See below | — |
| **G5** | Second customer validation | **PRESENT BUT INSUFFICIENT** | `examples/task-tracker/WALKTHROUGH.md` is a non-Agent-Red example inside the source tree | Not an independent install-from-release proof; no structured friction report; no time-to-green-doctor target; no field trial acceptance criteria |

### G4 — Explicitly Out of Scope

G4 (zero-knowledge profiles, multi-tenant profiles, Azure Terraform modules) is removed from this proposal per prior NO-GO Finding 3. A separate bridge proposal `gtkb-advanced-profiles-001.md` should be created when the owner decides to scope that work.

---

## Revised Phased Implementation Plan

### Phase G1: Adopter Documentation (unchanged from -007)

**Goal:** A developer who has never seen Agent Red can self-serve from documentation alone. Fix existing Agent Red contamination; add the two missing tutorial documents.

**Existing surface to fix:**

| File | What to fix |
|------|-------------|
| `docs/bootstrap.md` | Remove `L12` Agent Red topology reference; replace with generic "your project" framing |
| `docs/start-here.md` | Verify no Agent Red-specific references remain; confirm scaffold output references are accurate |
| `examples/task-tracker/WALKTHROUGH.md` | Verify accuracy against current CLI; no changes expected |

**New documents to add (delta only):**

| WI | Deliverable | Scope |
|----|-------------|-------|
| G1.1 | **"Your First Specification" tutorial** | `docs/tutorials/first-spec.md`. GOV-01 spec-first workflow using a concrete non-Agent-Red example. Creates a spec, a work item, links a test, runs assertions. Links to `examples/task-tracker` as the living reference. |
| G1.2 | **"Dual-Agent Setup Guide"** | `docs/tutorials/dual-agent-setup.md`. Configure Prime + Loyal Opposition with `gt project init --profile dual-agent`; start the OS-scheduler bridge (per platform); proposal/review cycle; reach VERIFIED. References auth troubleshooting doc (G1.3) per DELIB-GTKB-TOKEN-POSTURE. |
| G1.3 | **Auth troubleshooting guide** | `docs/troubleshooting/auth.md`. "Bridge says AUTH FAILURE" → provider-specific re-auth steps → Claude Desktop / ANTHROPIC_API_KEY / Codex token refresh. GT-KB provides documentation only; no token management per DELIB-GTKB-TOKEN-POSTURE. |

**mkdocs.yml integration:** Confirm `tutorials/` and `troubleshooting/` nav sections exist or add them.

**Phase G1 exit criteria:**
- `mkdocs build --strict` exits 0.
- The following command returns zero matches in adopter-facing docs:
  ```
  rg -ni "agent red|agent-red|agent\.red|agentred|customer engagement|shopify|tenant remaker" \
      docs/bootstrap.md docs/start-here.md docs/tutorials docs/troubleshooting docs/reference
  ```
  Note: `Remaker Digital` copyright notices and `Remaker-Digital/groundtruth-kb` repository links are **not** banned by this criterion. `docs/method/` (maintainer-facing) is excluded from the check.
- `examples/task-tracker/WALKTHROUGH.md` exercises all steps described in the dual-agent setup guide without referencing Agent Red.

---

### Phase G2: Cross-Platform Bridge (unchanged from -007)

**Goal:** A developer on macOS or Linux can follow documented steps to start the bridge OS scheduler. This phase improves generated docs and doctor checks, not the runtime model.

**OS-scheduler contract rationale:** The generated `templates/rules/bridge-essential.md` explicitly states bridge scheduler commands are not implemented in this release. `docs/method/12-file-bridge-automation.md:50/116/251/264` makes the OS scheduler the reliability boundary. Replacing this with a package-owned foreground process requires a separate owner decision and proposal.

#### G2 Status-File Contract

The doctor bridge freshness check reads JSON status files written by the deployed OS-scheduler pollers. The contract below is derived from the Agent Red reference implementation (`independent-progress-assessments/bridge-automation/logs/` + `.claude/hooks/poller-freshness.py`).

**File locations (relative to project root):**

| Agent | Path |
|-------|------|
| Claude (Prime) | `independent-progress-assessments/bridge-automation/logs/claude-scan-status.json` |
| Codex (Loyal Opposition) | `independent-progress-assessments/bridge-automation/logs/codex-scan-status.json` |

**Required JSON schema (both files):**

```json
{
  "updatedAtUtc": "2026-04-15T14:30:00Z",
  "state": "clear",
  "message": "Optional human-readable status string (≤ 60 chars)"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `updatedAtUtc` | ISO 8601 UTC string | Yes | Written by the poller on every scan cycle; doctor uses **only this field** for age calculation |
| `state` | string (opaque) | Yes | **Opaque display string — doctor must not fail on unknown values.** Known values from Agent Red reference: `"clear"`, `"attention"`, `"running"`, `"completed"`, `"skipped"`, `"error"`. Doctor displays the value as-is; freshness is based exclusively on `updatedAtUtc`. |
| `message` | string | No | Truncated to 60 chars by doctor display |

**Freshness thresholds:**

| Age | Status reported |
|-----|-----------------|
| < 4 min | OK |
| 4–10 min | WARN |
| > 10 min | ALARM |
| File absent | "not started" (per-agent, not a failure) |
| `updatedAtUtc` missing or unparseable | ALARM |

**Deliverables:**

| WI | Deliverable | Scope |
|----|-------------|-------|
| G2.1 | **Cross-platform OS scheduler guide** | `docs/tutorials/bridge-os-scheduler.md`. Platform-specific cron (macOS/Linux) and Task Scheduler (Windows) instructions to run the bridge poller every 3 minutes. Covers the `bridge-os-poller-setup-prompt.md` generated artifact and the status-file contract above. |
| G2.2 | **Doctor bridge freshness check** | Extend `gt project doctor` (`doctor.py:487-537`) to: (a) resolve status-file paths relative to project root; (b) read `updatedAtUtc` from JSON; (c) compute age and report OK/WARN/ALARM/not-started per the thresholds above; (d) display `state` string as-is without validating against a closed enum; (e) emit pointer to `docs/tutorials/bridge-os-scheduler.md` when bridge is not started; (f) emit pointer to `docs/troubleshooting/auth.md` on ALARM. |
| G2.3 | **Doctor bridge tests** | Tests using `tmp_path` status files: fresh file (< 4 min) → OK, 5-min-old file → WARN, 15-min-old file → ALARM, missing file → "not started", missing `updatedAtUtc` field → ALARM, unknown `state` value (e.g., `"running"`, `"completed"`) → no error raised (display passthrough). Run on Ubuntu + Windows + macOS CI. |
| G2.4 | **Template and inventory updates** | Update `templates/bridge-os-poller-setup-prompt.md` and `BRIDGE-INVENTORY.md` per the status-file contract above so generated projects know what the poller must produce. |

**Phase G2 exit criteria:**
- `gt project doctor` reports bridge status (OK/WARN/ALARM/not-started) based on `updatedAtUtc` JSON field.
- `gt project doctor` displays `state` value as-is; does not raise error on unknown values.
- `gt project doctor` provides pointer to `docs/tutorials/bridge-os-scheduler.md` when bridge is not started.
- Doctor bridge tests pass on all three platform CI runners (Ubuntu + Windows + macOS).
- `templates/bridge-os-poller-setup-prompt.md` and `BRIDGE-INVENTORY.md` document the status-file path and schema contract.

---

### Phase G3: GitHub CI Template Profile-Tiering (revised from -007)

**Goal:** Generated CI workflows from `gt project init` are tiered to the selected profile (minimal / standard / full), contain correct package-name and Python-version substitutions, and are aligned with the files each profile actually generates. `--no-include-ci` always suppresses all CI regardless of profile.

#### G3.1 — CI Default Rule (replaces tristate design from -007)

**Chosen rule: current default-on semantics.** This resolves the -008 Finding 1 contradiction.

| Scenario | Behavior |
|----------|----------|
| User passes `--include-ci` | CI generated; tier determined by profile |
| User passes `--no-include-ci` | No CI generated for any profile |
| User passes neither flag (default) | **CI generated** (default `include_ci=True`); tier determined by profile |

**Implementation:**
- `ScaffoldOptions.include_ci` default remains `True`.
- `--include-ci / --no-include-ci` CLI flags remain as-is. No tristate required.
- `scaffold.py:92` fix:
  ```python
  # Before (profile can force CI even when user said --no-include-ci):
  include_ci = options.include_ci or profile.includes_ci

  # After (user flag always wins; profile selects tier, not whether CI is generated):
  include_ci = options.include_ci
  ```
- The profile's `includes_ci` field is **repurposed** as the tier-selection signal: `True` → `full` tier, `False` → `minimal` or `standard` based on `includes_bridge`.
- Tier selection table:

  | Profile | `includes_ci` | `includes_bridge` | `includes_docker` | CI tier |
  |---------|--------------|-------------------|-------------------|---------|
  | `local-only` | `False` | `False` | `False` | `minimal` |
  | `dual-agent` | `False` | `True` | `False` | `standard` |
  | `dual-agent-webapp` | `True` | `True` | `True` | `full` |

- `_copy_ci_templates(target, profile)` receives the profile and selects the correct subdirectory: `templates/ci/minimal/`, `templates/ci/standard/`, or `templates/ci/full/`.

**Documentation update:** `docs/reference/cli.md` and `docs/start-here.md` must state:
1. CI is generated by default for all profiles.
2. `--no-include-ci` suppresses CI regardless of profile.
3. The CI tier (minimal/standard/full) is chosen based on profile capabilities.

#### G3.2 — Profile-Aligned CI Tier Contents (new in -009)

This resolves -008 Finding 2. Tier contents are defined based on what each profile actually generates.

**What each profile generates (empirically verified by Codex review -008):**

| Profile | Dockerfile | `src/` | `tests/` | `pyproject.toml` | `requirements.txt` |
|---------|-----------|--------|----------|------------------|--------------------|
| `local-only` | No | No | No | No | No |
| `dual-agent` | No | No | No | No | No |
| `dual-agent-webapp` | Yes | **No*** | No | **No*** | No |

> *`dual-agent-webapp` currently generates a Dockerfile that references `COPY src/` and `COPY pyproject.toml` but does not generate those files. This proposal adds stub generation for `dual-agent-webapp` (see G3.2d below).

**Tier definitions:**

**`minimal` tier** (for `local-only`):
- `test.yml` only — no `build.yml`, no `deploy.yml`
- Steps: checkout → install `groundtruth-kb[dev]` → `ruff check .` (lint) → `gt --config groundtruth.toml assert` (GT assertions)
- No Docker steps, no pytest, no mypy, no coverage (none of those artifacts exist in a `local-only` project)
- `{{PYTHON_VERSION}}` placeholder in `setup-python` step; `{{PACKAGE_NAME}}` not needed (no package install)

**`standard` tier** (for `dual-agent`):
- `test.yml` only — no `build.yml`, no `deploy.yml`
- Steps: checkout → install `groundtruth-kb[dev]` → `ruff check .` → `gt --config groundtruth.toml assert`
- Advisory block included as YAML comment block (not active steps):
  ```yaml
  # --- Uncomment when you add src/ and tests/ to this project ---
  # - name: Run tests
  #   run: pytest tests/ -v --tb=short
  # - name: Type check
  #   run: mypy src/
  ```
- `{{PYTHON_VERSION}}` placeholder in `setup-python` step

**`full` tier** (for `dual-agent-webapp`):
- `build.yml`, `deploy.yml`, and `test.yml`
- `test.yml` steps: checkout → install deps → `ruff check .` → `pytest tests/ -v --tb=short` → `gt assert` → optional mypy
- `build.yml`: Docker build/push using `docker/build-push-action` (relies on Dockerfile + stubs added by G3.2d)
- `deploy.yml`: manual workflow_dispatch deploy (unchanged from current template)
- `{{PACKAGE_NAME}}` placeholder in pip install step (e.g., `pip install -e ".[dev]"`)
- `{{PYTHON_VERSION}}` placeholder in setup-python step

**G3.2d — `dual-agent-webapp` scaffold stub generation:**

To make `full`-tier Docker CI non-broken out-of-the-box, `scaffold_project()` must generate minimal Python stubs for `dual-agent-webapp`:

| File | Content |
|------|---------|
| `src/__init__.py` | Empty stub (`# {{PROJECT_NAME}} application package`) |
| `pyproject.toml` | Minimal PEP 517 stub with `[project]` name = `{{PACKAGE_NAME}}`, version = `"0.1.0"`, `requires-python = ">=3.11"` |
| `requirements.txt` | Comment-only stub (`# Add your runtime dependencies here`) |

These stubs satisfy the Dockerfile's `COPY src/` and `COPY pyproject.toml` requirements. The adopter replaces them with real code.

**No changes to `templates/project/Dockerfile`** — the existing template is already correct given the stubs.

#### G3.3 — Placeholder Sources (unchanged from -007)

**`{{PACKAGE_NAME}}`** is derived as a deterministic slug from `ScaffoldOptions.project_name`:

```python
def _package_name_slug(project_name: str) -> str:
    """Derive a PEP 508–compatible package name from project_name."""
    return re.sub(r"[^a-z0-9]+", "-", project_name.lower()).strip("-")
```

**`{{PYTHON_VERSION}}`** is a new `ScaffoldOptions` field with a fixed initial default of `"3.11"`. No `--python-version` CLI flag. Adopters edit the generated workflow directly.

```python
python_version: str = "3.11"
```

#### G3.4 — Integration Config Templates (unchanged from -007)

| Component | Change required |
|-----------|----------------|
| `cli.py` | Add `--integrations / --no-integrations` flag (default: `False`) to `project init` |
| `ScaffoldOptions` | Add `integrations: bool = False` field |
| `scaffold.py` | When `integrations=True`, copy `templates/ci/integrations/dependabot.yml` and `.coderabbitai.yaml` with `{{PROJECT_NAME}}` substitution |
| Docs | Document `--integrations/--no-integrations` under `gt project init` in `docs/reference/cli.md` |
| Tests | Test `--integrations` generates correct files; without flag, files are absent |

**Jinja2 decision (unchanged):** Use stdlib `str.replace` for all placeholder substitution. No new base dependency.

#### G3.5 — Deliverables

| WI | Deliverable | Scope |
|----|-------------|-------|
| G3.1 | **Profile-tier CI template sets** | Create `templates/ci/minimal/`, `templates/ci/standard/`, `templates/ci/full/` subdirectories. Define tier contents per G3.2 above. Move existing `templates/ci/*.yml` to become the `full/` set as the starting point (with edits per tier definition). `scaffold.py:322-328` selects directory based on profile tier table. |
| G3.2 | **`dual-agent-webapp` stub generation** | Add generation of `src/__init__.py`, `pyproject.toml` stub, and `requirements.txt` stub to `scaffold.py` for `dual-agent-webapp` profile. |
| G3.3 | **`{{PACKAGE_NAME}}` and `{{PYTHON_VERSION}}` placeholders** | Add placeholders to each tier's `test.yml`. Add `ScaffoldOptions.python_version = "3.11"`. Wire through `_render_file()`. |
| G3.4 | **`--no-include-ci` precedence fix** | Change `scaffold.py:92` per G3.1. Update `docs/reference/cli.md` and `docs/start-here.md`. |
| G3.5 | **Integration config templates** | Create `templates/ci/integrations/` with `dependabot.yml` and `.coderabbitai.yaml`. Implement `--integrations` flag. |
| G3.6 | **CI template tests** | See G3.6 test matrix below. |

#### G3.6 — Test Matrix

Tests must verify:

| # | Test assertion |
|---|---------------|
| a | Generated workflows are valid YAML (`yaml.safe_load` succeeds) |
| b | `{{PACKAGE_NAME}}` resolves to the correct slug (no literal braces remain) |
| c | `{{PYTHON_VERSION}}` resolves to `"3.11"` (no literal braces remain) |
| d | `local-only` default → generates `minimal/test.yml` only; no `build.yml`, no `deploy.yml` |
| e | `dual-agent` default → generates `standard/test.yml` only; no `build.yml`, no `deploy.yml` |
| f | `dual-agent-webapp` default → generates `full/test.yml`, `build.yml`, `deploy.yml` |
| g | `--no-include-ci` with any profile → no `.github/workflows/` directory |
| h | `minimal/test.yml` contains no Docker steps, no pytest steps, no mypy steps |
| i | `standard/test.yml` contains no Docker steps; advisory pytest/mypy blocks are present only as comments |
| j | `full/test.yml` contains pytest steps; `build.yml` contains `docker/build-push-action` |
| k | `dual-agent-webapp` scaffold generates `src/__init__.py`, `pyproject.toml`, `requirements.txt` stubs |
| l | No hard-coded `"agent-red"` or `"remaker"` strings in any generated workflow |
| m | `--integrations` generates `dependabot.yml` and `.coderabbitai.yaml`; without flag, absent |

**Phase G3 exit criteria:**
- `gt project init my-project --profile local-only` generates `minimal` CI (`test.yml` only) by default.
- `gt project init my-project --profile dual-agent` generates `standard` CI (`test.yml` only) by default.
- `gt project init my-project --profile dual-agent-webapp` generates `full` CI (`test.yml` + `build.yml` + `deploy.yml`) by default.
- `gt project init my-project --profile dual-agent-webapp --no-include-ci` generates **no CI workflows** (flag overrides default).
- `gt project init my-project --profile local-only --no-include-ci` generates **no CI workflows**.
- `grep -i "agent.red\|remaker" .github/workflows/*.yml` in the generated project returns zero matches.
- `gt project init my-project --integrations` generates `dependabot.yml` and `.coderabbitai.yaml`; without `--integrations` these files are absent.
- `{{PACKAGE_NAME}}` resolves to slug of `project_name`; `{{PYTHON_VERSION}}` resolves to `"3.11"`.
- `minimal/test.yml` contains no Docker, pytest, or mypy steps.
- `standard/test.yml` contains no Docker steps; pytest/mypy present only as comments.
- `dual-agent-webapp` scaffold generates `src/__init__.py`, `pyproject.toml`, and `requirements.txt` stubs.
- CI template tests (a)–(m) all pass.
- `pip install groundtruth-kb` base install does not require Jinja2.

---

### Phase G5: Second Customer Field Trial (unchanged from -007)

**Goal:** Prove GT-KB works for a project that isn't Agent Red, via a structured field trial.

| WI | Deliverable | Scope |
|----|-------------|-------|
| G5.1 | **Field trial project** | A new internal project (not inside `groundtruth-kb/`) that installs GT-KB from PyPI (`pip install groundtruth-kb==<latest>`). Exercises: install → `gt project init` → first spec → first work item → first test → bridge setup via OS scheduler → first deliberation → `gt project doctor` green. Target operating systems: Windows (primary) and Ubuntu (CI). |
| G5.2 | **Field trial acceptance criteria** | Documented before G5.1 execution: (a) time-to-green-doctor ≤ 60 minutes from fresh checkout; (b) `gt project doctor` reports all checks OK; (c) at least one complete proposal/review/VERIFIED bridge thread; (d) no Agent Red knowledge required to complete steps (a)–(c); (e) `pip install groundtruth-kb` succeeds on Python 3.11+ on both platforms. |
| G5.3 | **Friction report** | Every point where the adopter journey was unclear, broken, or required Agent Red knowledge. Filed as work items. Format: item / symptom / root cause / suggested fix. |
| G5.4 | **Polish round** | Fix the top-5 friction items from G5.3. |

**Phase G5 exit criteria:**
- G5.2 acceptance criteria (a)–(e) all met.
- Friction report filed and top-5 WIs created.
- Polish round complete.

---

## Dependency Graph (unchanged)

```
G1 (doc delta)        — no dependencies, can start immediately
G2 (OS-scheduler)     — no dependencies, can start in parallel with G1
G3 (CI templates)     — no hard dependency; can start in parallel (G1 CI references inform G3)
G5 (field trial)      — depends on G1 + G2 + G3 (adopter path must exist)
G4                    — OUT OF SCOPE (separate proposal)
```

Critical path: G1 + G2 + G3 (parallel) → G5

---

## Estimated Scope

| Phase | WIs | Est. size | Notes |
|-------|-----|-----------|-------|
| G1 doc delta | 3 new docs + 2 file fixes | Small | Mostly writing; fix to `bootstrap.md:12` |
| G2 OS-scheduler | 1 new doc + doctor extension + tests + template/inventory updates | Small-medium | Doctor reads `updatedAtUtc` from JSON; state is opaque display string; 4 WIs including G2.4 |
| G3 CI templates | Tier dirs + profiles + `--no-include-ci` fix + `webapp` stubs + placeholders + integrations flag + tests | Medium | Stdlib substitution only; no new dep; 6 WIs |
| G5 field trial | External project + criteria + friction report + polish | Medium-large | Execution-dependent |

---

## Success Criteria (developer preview)

GroundTruth-KB achieves **developer preview** / **beta candidate** status when ALL of the following are true:

1. **Adopter self-service:** A developer on any platform runs `pip install groundtruth-kb`, follows the Getting Started guide, and has a working project with OS-scheduler bridge, specs, and tests — without reading Agent Red source code or asking the maintainer.
2. **Cross-platform bridge setup:** The OS-scheduler bridge setup guide covers Windows, macOS, and Linux; the generated poller template requires writing status files per the G2 schema.
3. **CI out of the box:** `gt project init` generates profile-tiered GitHub CI workflows with correct tier contents for each profile's generated files; `--no-include-ci` always suppresses all CI regardless of profile; no Agent Red references.
4. **Doctor validates everything:** `gt project doctor` checks bridge freshness via `updatedAtUtc` JSON field, displays `state` as opaque string without failing on unknown values, provides pointer to setup guide when not started, and pointer to auth troubleshooting on ALARM.
5. **Second customer field trial:** At least one project other than Agent Red installs from PyPI and completes the full adopter journey per G5.2 acceptance criteria.
6. **Zero Agent Red contamination** in adopter-facing docs and generated templates (see G1 exit criterion for the exact check).
7. **All existing quality gates pass:** existing test count (814 at current main), ≥70% coverage, ≥85% docstrings, mypy --strict clean, ruff clean.

**"Mass adoption" is not claimed until the field trial (G5) proves the flow from a release artifact in a fresh project on at least two platforms.**

---

## Risk Assessment (updated)

| Risk | Severity | Mitigation |
|------|----------|------------|
| `bootstrap.md` Agent Red reference touches more than one paragraph | Low | Scope the fix to L12 per Codex evidence; run the narrowed `rg` check before and after |
| Stdlib placeholder substitution insufficient for conditional CI blocks | Low | Handled by generating different template files per tier, not conditionals |
| `dual-agent-webapp` stub generation changes scaffold output; existing tests may break | Low | Scope additions to `dual-agent-webapp` only; existing `local-only`/`dual-agent` scaffold tests unaffected. Add specific assertions for the new stubs. |
| `ScaffoldOptions.python_version` default `"3.11"` becomes stale | Low | Default is scaffold initial value only; adopters update in generated workflow directly |
| `--no-include-ci` precedence fix changes behavior for `dual-agent-webapp` adopters who relied on profile-forced CI | Low | The prior behavior (`options.include_ci or profile.includes_ci`) was arguably a bug. Docs update makes intent explicit. |
| Field trial reveals fundamental scaffold issues | High | G5 is deliberately last; findings feed back into G1–G3 as a follow-up round |

---

## Open Questions (unchanged from -007)

1. **G5 candidate project type.** Recommendation: a real new internal Remaker Digital project is a stronger adoption proof than another example in the source tree.

2. **`gt bridge start` — owner decision required.** If the owner wants package-owned bridge commands, a separate proposal is needed. This proposal does not include that work.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
