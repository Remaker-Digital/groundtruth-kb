# GT-KB Adoption Gap Closure — Revised Implementation Plan

**Status:** REVISED
**Prime Builder:** Claude Sonnet 4.6 (auto-spawn)
**Author session:** S296 (auto-spawn)
**Scope:** Close adoption gaps for GroundTruth-KB developer-preview readiness
**Repository:** `groundtruth-kb` @ `31fe2c4` (main)
**Depends on:** `gtkb-mass-adoption-readiness-012` VERIFIED (MVP landed at `12fd083`)
**Addresses:** NO-GO at `bridge/gtkb-adoption-gap-closure-004.md`

---

## NO-GO Response Summary (from -004)

All 3 findings addressed:

| Finding | Severity | Resolution in this revision |
|---------|----------|-----------------------------|
| F1 — G2 lacks portable bridge freshness contract (path, schema, freshness-source contradiction) | P1 | Status-file contract fully specified: paths, JSON schema, freshness source (`updatedAtUtc`), missing-file semantics; templates updates required |
| F2 — G3 baseline inaccurate; `--integrations` command surface incomplete | P1 | Baseline corrected to "generic, not profile-tiered"; profile-to-tier mapping defined; `--integrations` CLI surface enumerated (cli.py, ScaffoldOptions, scaffold summary, docs, tests) |
| F3 — G1 grep exit criterion overbroad (catches legitimate copyright) | P2 | Narrowed grep to Agent Red / downstream-product contamination only; `Remaker Digital` copyright and repo links are not banned |

---

## Prior Deliberations

- `DELIB-GTKB-INIT-POSTURE`: `gt init` = Layer 1; `gt project init` = scaffold entry point.
- `DELIB-GTKB-TOKEN-POSTURE`: GT-KB may not manage auth tokens; docs + doctor pointers only.
- `DELIB-0474`: Staged execution; productized gating required before stable claims.
- `DELIB-0633`: GT-KB is "promising but still alpha"; not proven as a repeatable multi-project platform.
- `DELIB-0211`, `DELIB-0472`, `DELIB-0184`, `DELIB-0601`, `DELIB-0229`: Mass-adoption readiness context.
- `bridge/gtkb-mass-adoption-readiness-012.md`: MVP VERIFIED — bridge INDEX scaffolding, provider templates, doctor accuracy, bridge rule templates landed.

---

## Context (unchanged from -003)

The owner asked whether GT-KB is ready for mass adoption. The answer is no. The correct framing, consistent with DELIB-0633 and prior NO-GO F4, is: **GT-KB can achieve "developer preview" / "beta candidate" readiness** via the gaps below. "Mass adoption" follows a successful field trial (G5), not the completion of docs/CI/bridge work alone.

---

## Revised Gap Baseline (against `31fe2c4`)

Each gap is classified as **ABSENT** (nothing exists) or **PRESENT BUT INSUFFICIENT** (exists; specific delta needed).

| # | Gap | Classification | What exists | What is missing |
|---|-----|----------------|-------------|-----------------|
| **G1** | Adopter documentation | **PRESENT BUT INSUFFICIENT** | `docs/bootstrap.md` (getting-started guide); `docs/start-here.md` (scaffold walkthrough); `examples/task-tracker/WALKTHROUGH.md` (non-Agent-Red example) | `bootstrap.md:12` references Agent Red deployment topology; no "Your First Specification" tutorial; no dual-agent setup guide for new developers; no auth troubleshooting doc |
| **G2** | Cross-platform bridge | **PRESENT BUT INSUFFICIENT** | OS-scheduler contract documented in `docs/method/12-file-bridge-automation.md`; generated `templates/bridge-os-poller-setup-prompt.md`; `templates/rules/bridge-essential.md` explicitly says bridge scheduler commands are not implemented in this release | Mac/Linux OS-scheduler setup instructions absent; `gt project doctor` does not check bridge freshness; no auth troubleshooting pointer from doctor; **no status-file path/schema contract in generated templates or inventory** |
| **G3** | GitHub CI templates | **PRESENT BUT INSUFFICIENT** | `templates/ci/build.yml`, `deploy.yml`, `test.yml`; `scaffold.py:322-328` copies all `templates/ci/*.yml` into `.github/workflows/`; `--no-include-ci` flag exists | **Workflows are generic and not profile-tiered**; generated `build.yml`/`deploy.yml` use `github.repository` for image naming (correct) but contain no package-name, Python-version, or test-layout placeholders; no profile-to-tier mapping; no `--integrations` option |
| **G4** | ZK + multi-tenant patterns | **OUT OF SCOPE** | See below | — |
| **G5** | Second customer validation | **PRESENT BUT INSUFFICIENT** | `examples/task-tracker/WALKTHROUGH.md` is a non-Agent-Red example inside the source tree | Not an independent install-from-release proof; no structured friction report; no time-to-green-doctor target; no field trial acceptance criteria |

### G4 — Explicitly Out of Scope

G4 (zero-knowledge profiles, multi-tenant profiles, Azure Terraform modules) is removed from this proposal per prior NO-GO Finding 3. A separate bridge proposal `gtkb-advanced-profiles-001.md` should be created when the owner decides to scope that work.

---

## Revised Phased Implementation Plan

### Phase G1: Adopter Documentation (delta from existing, not scratch)

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

### Phase G2: Cross-Platform Bridge (OS-scheduler contract preserved)

**Goal:** A developer on macOS or Linux can follow documented steps to start the bridge OS scheduler. This phase improves generated docs and doctor checks, not the runtime model.

**OS-scheduler contract rationale:** The generated `templates/rules/bridge-essential.md` explicitly states bridge scheduler commands are not implemented in this release. `docs/method/12-file-bridge-automation.md:50/116/251/264` makes the OS scheduler the reliability boundary. Replacing this with a package-owned foreground process requires a separate owner decision and proposal.

#### G2 Status-File Contract (new in -005)

The doctor bridge freshness check reads JSON status files written by the deployed OS-scheduler pollers. The contract below is derived from the Agent Red reference implementation (`independent-progress-assessments/bridge-automation/logs/` + `.claude/hooks/poller-freshness.py`).

**File locations (relative to project root):**

| Agent | Path |
|-------|------|
| Claude (Prime) | `independent-progress-assessments/bridge-automation/logs/claude-scan-status.json` |
| Codex (Loyal Opposition) | `independent-progress-assessments/bridge-automation/logs/codex-scan-status.json` |

These paths are the Agent Red convention. A generated project MUST follow the same relative paths so that `gt project doctor` can locate them without project-specific configuration.

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
| `updatedAtUtc` | ISO 8601 UTC string | Yes | Written by the poller on every scan cycle; doctor uses this field for age calculation |
| `state` | string | Yes | Convention: `"clear"`, `"attention"`, `"skipped"`, or `"error"` |
| `message` | string | No | Truncated to 60 chars by doctor display |

**Freshness source:** `updatedAtUtc` JSON field — **not** `os.stat().st_mtime`. The risk table in -003 incorrectly named `os.stat().st_mtime`; this revision corrects that. The Agent Red reference uses `datetime.fromisoformat(status["updatedAtUtc"].replace("Z", "+00:00"))` (`.claude/hooks/poller-freshness.py:176`).

**Freshness thresholds (matching Agent Red precedent):**

| Age | Status reported |
|-----|-----------------|
| < 4 min | OK |
| 4–10 min | WARN |
| > 10 min | ALARM |
| File absent | "not started" (per-agent, not a failure) |
| `updatedAtUtc` missing or unparseable | ALARM |

**Missing-file semantics:**
- If `claude-scan-status.json` is absent → doctor reports `claude: not started` for that agent; does not fail the overall check.
- If `codex-scan-status.json` is absent → doctor reports `codex: not started` for that agent.
- Both files absent → doctor reports "bridge not yet started" and provides a pointer to `docs/tutorials/bridge-os-scheduler.md`.
- Either file present but stale → WARN or ALARM (per thresholds above).

**Required template and inventory updates (G2.4):**

| Artifact | Required change |
|----------|-----------------|
| `templates/bridge-os-poller-setup-prompt.md` | Add requirement: the OS-scheduler poller script MUST write `independent-progress-assessments/bridge-automation/logs/{agent}-scan-status.json` on every scan cycle with the `updatedAtUtc`, `state`, and `message` fields defined above |
| `BRIDGE-INVENTORY.md` | Add status-file paths and schema reference so adopters know what the poller must produce |

**Deliverables:**

| WI | Deliverable | Scope |
|----|-------------|-------|
| G2.1 | **Cross-platform OS scheduler guide** | `docs/tutorials/bridge-os-scheduler.md`. Platform-specific cron (macOS/Linux) and Task Scheduler (Windows) instructions to run the bridge poller every 3 minutes. Covers the `bridge-os-poller-setup-prompt.md` generated artifact and the status-file contract above. |
| G2.2 | **Doctor bridge freshness check** | Extend `gt project doctor` (`doctor.py:487-537`) to: (a) resolve status-file paths relative to project root; (b) read `updatedAtUtc` from JSON; (c) compute age and report OK/WARN/ALARM/not-started per the thresholds above; (d) emit pointer to `docs/tutorials/bridge-os-scheduler.md` when bridge is not started; (e) emit pointer to `docs/troubleshooting/auth.md` on ALARM. |
| G2.3 | **Doctor bridge tests** | Tests using `tmp_path` status files: fresh file (< 4 min) → OK, 5-min-old file → WARN, 15-min-old file → ALARM, missing file → "not started", missing `updatedAtUtc` field → ALARM. Run on Ubuntu + Windows + macOS CI. |
| G2.4 | **Template and inventory updates** | Update `templates/bridge-os-poller-setup-prompt.md` and `BRIDGE-INVENTORY.md` per the table above so generated projects know what the poller must produce. |

**Note on `gt bridge start` — owner decision required:** If the owner wants package-owned bridge commands, a separate proposal is needed. This phase does not include that.

**Phase G2 exit criteria:**
- `gt project doctor` reports bridge status (OK/WARN/ALARM/not-started) based on `updatedAtUtc` JSON field in status files at the paths defined above.
- `gt project doctor` provides a pointer to `docs/tutorials/bridge-os-scheduler.md` when bridge is not started.
- Doctor bridge tests pass on all three platform CI runners (Ubuntu + Windows + macOS).
- `templates/bridge-os-poller-setup-prompt.md` and `BRIDGE-INVENTORY.md` document the status-file path and schema contract.

---

### Phase G3: GitHub CI Template Profile-Tiering (stdlib, no Jinja2 base dep)

**Goal:** Generated CI workflows from `gt project init` are tiered to the selected profile (minimal / standard / full) and contain correct package-name and Python-version substitutions.

**Corrected baseline (from -004 Finding 2):** The existing `templates/ci/*.yml` files do **not** contain static Agent Red project or package names. `build.yml` and `deploy.yml` use `github.repository` for image naming (which is correct and must be preserved). The real gap is:

1. Workflows are not profile-tiered — all profiles generate the same set of `.yml` files regardless of whether the project uses a full security scan, coverage gates, or mypy.
2. Generated workflows do not contain `{{PACKAGE_NAME}}` or `{{PYTHON_VERSION}}` placeholders, so test-layout and Python-version configuration is manual after scaffold.

**Profile-to-CI-tier mapping:**

| Profile | CI tier | Included workflow steps |
|---------|---------|------------------------|
| `local-only` | `minimal` | Build + basic lint |
| `dual-agent` | `standard` | Minimal + coverage threshold + mypy |
| `dual-agent-webapp` | `full` | Standard + security scan (Semgrep/Bandit) + Chromatic (optional) |

**Placeholder sources:**

| Placeholder | Source |
|-------------|--------|
| `{{PACKAGE_NAME}}` | `ScaffoldOptions.package_name` (already present in scaffold) |
| `{{PYTHON_VERSION}}` | `ScaffoldOptions.python_version` — new field, defaults to `"3.11"` |

**`--integrations` command surface (explicit enumeration):**

| Component | Change required |
|-----------|----------------|
| `cli.py` | Add `--integrations / --no-integrations` flag (default: `False`) to the `project init` command |
| `ScaffoldOptions` dataclass | Add `integrations: bool = False` field |
| `scaffold.py` | When `integrations=True`, copy `templates/ci/integrations/dependabot.yml` and `templates/ci/integrations/.coderabbitai.yaml` with `{{PROJECT_NAME}}` substitution |
| Scaffold summary output | Print line "  integrations: Dependabot + CodeRabbit" when `integrations=True` |
| Docs (`docs/reference/cli.md`) | Document `--integrations/--no-integrations` under `gt project init` |
| Tests | Add test cases for `--integrations` flag generating correct files (or not, when absent) |

**Jinja2 decision (unchanged from -003):** Use stdlib `str.replace` placeholder substitution. Jinja2 stays as an optional `web` dependency. Profile-tier conditionals are handled by generating different source template files per tier, not by conditional template syntax.

**Deliverables:**

| WI | Deliverable | Scope |
|----|-------------|-------|
| G3.1 | **Profile-tier CI template sets** | Create `templates/ci/minimal/`, `templates/ci/standard/`, `templates/ci/full/` subdirectories. Move existing `templates/ci/*.yml` to become the `minimal/` set. Add coverage + mypy steps to `standard/`. Add security scan to `full/`. `scaffold.py:322-328` selects directory based on profile. |
| G3.2 | **PACKAGE_NAME and PYTHON_VERSION placeholders** | Add `{{PACKAGE_NAME}}` and `{{PYTHON_VERSION}}` to the test runner step in each tier's `test.yml`. Add `python_version: str = "3.11"` to `ScaffoldOptions`. Wire through `_render_file()` pass on copied `*.yml` files. |
| G3.3 | **Integration config templates (optional flag)** | Create `templates/ci/integrations/dependabot.yml` and `templates/ci/integrations/.coderabbitai.yaml` with `{{PROJECT_NAME}}` placeholders. Implement `--integrations / --no-integrations` CLI flag per the command-surface table above. |
| G3.4 | **CI template tests** | Tests verify generated workflows: valid YAML (`yaml.safe_load`), project name substituted where present, correct tier for each profile, no hard-coded "agent-red" or "remaker" strings, `{{PACKAGE_NAME}}` and `{{PYTHON_VERSION}}` resolved. |

**Phase G3 exit criteria:**
- `gt project init my-project --profile local-only` generates minimal CI; `--profile dual-agent-webapp` generates full CI with security scan.
- `grep -i "agent.red\|remaker" .github/workflows/*.yml` in the generated project returns zero matches.
- `gt project init my-project --integrations` generates `dependabot.yml` and `.coderabbitai.yaml`; without `--integrations` these files are absent.
- `{{PACKAGE_NAME}}` and `{{PYTHON_VERSION}}` are resolved in generated `test.yml`.
- CI template tests pass.
- `pip install groundtruth-kb` base install does not require Jinja2.

---

### Phase G5: Second Customer Field Trial (criteria-first)

**Goal:** Prove GT-KB works for a project that isn't Agent Red, via a structured field trial. This defines the proof criteria; execution is the field trial itself.

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
| G2 OS-scheduler | 1 new doc + doctor extension + tests + template/inventory updates | Small-medium | Doctor reads `updatedAtUtc` from JSON; 4 WIs including G2.4 |
| G3 CI templates | Tier dirs + placeholders + integrations flag + tests | Medium | Stdlib substitution only; no new dep |
| G5 field trial | External project + criteria + friction report + polish | Medium-large | Execution-dependent |

---

## Success Criteria (developer preview)

GroundTruth-KB achieves **developer preview** / **beta candidate** status when ALL of the following are true:

1. **Adopter self-service:** A developer on any platform runs `pip install groundtruth-kb`, follows the Getting Started guide, and has a working project with OS-scheduler bridge, specs, and tests — without reading Agent Red source code or asking the maintainer.
2. **Cross-platform bridge setup:** The OS-scheduler bridge setup guide covers Windows, macOS, and Linux; the generated poller template requires writing status files per the G2 schema.
3. **CI out of the box:** `gt project init` generates profile-tiered GitHub CI workflows with package-name and Python-version substitution; no Agent Red references.
4. **Doctor validates everything:** `gt project doctor` checks bridge freshness via `updatedAtUtc` JSON field, provides pointer to setup guide when not started, and pointer to auth troubleshooting on ALARM.
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
| Doctor bridge freshness check reads `updatedAtUtc` but poller script writes `st_mtime` only | Medium | G2.4 updates `templates/bridge-os-poller-setup-prompt.md` to require `updatedAtUtc` in generated poller output; doctor tests use `tmp_path` JSON files to verify schema |
| `ScaffoldOptions.python_version` default `"3.11"` becomes stale | Low | Default is user-overridable via `--python-version`; docs note the adopter should override for their project |
| Field trial reveals fundamental scaffold issues | High | G5 is deliberately last; findings feed back into G1–G3 as a follow-up round |
| `gt bridge start` demand from adopters | Medium | If needed, separate proposal; this plan documents the gap and defers the decision |

---

## Open Questions (unchanged from -003)

1. **G5 candidate project type.** Options: (a) new internal Remaker Digital project, (b) a standalone example published alongside GT-KB under `examples/` (but installed from PyPI independently). Recommendation: (a) — a real new internal project is a stronger adoption proof than another example in the source tree.

2. **`gt bridge start` — owner decision required.** If the owner wants package-owned bridge commands, a separate proposal is needed with the decision criteria listed in the G2 note above. This proposal does not include that work.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
