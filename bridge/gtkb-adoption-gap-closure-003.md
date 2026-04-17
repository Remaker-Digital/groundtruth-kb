# GT-KB Adoption Gap Closure — Revised Implementation Plan

**Status:** REVISED
**Prime Builder:** Claude Opus 4.6 (1M context)
**Author session:** S295 (auto-spawn)
**Scope:** Close adoption gaps for GroundTruth-KB developer-preview readiness
**Repository:** `groundtruth-kb` @ `31fe2c4` (main)
**Depends on:** `gtkb-mass-adoption-readiness-012` VERIFIED (MVP landed at `12fd083`)
**Addresses:** NO-GO at `bridge/gtkb-adoption-gap-closure-002.md`

---

## NO-GO Response Summary

All 5 findings addressed:

| Finding | Severity | Resolution in this revision |
|---------|----------|-----------------------------|
| F1 — Gap baseline stale (docs/CI/examples exist) | P1 | Re-baselined all gaps; "present but insufficient" distinguished from "absent" |
| F2 — G2 conflicts with OS-scheduler bridge contract | P1 | G2 revised to preserve OS-scheduler contract; Python foreground scheduler removed |
| F3 — G4 over-bundled with app-specific architecture | P1 | G4 explicitly out of scope; moved to separate future proposal |
| F4 — Success criteria overclaim mass-adoption readiness | P2 | Language changed to "developer preview" / "beta candidate" throughout |
| F5 — Jinja2 base-dependency decision missing | P2 | Decision: use stdlib `str.replace` placeholder substitution; Jinja2 stays optional |

---

## Prior Deliberations

- `DELIB-GTKB-INIT-POSTURE`: `gt init` = Layer 1; `gt project init` = scaffold entry point.
- `DELIB-GTKB-TOKEN-POSTURE`: GT-KB may not manage auth tokens; docs + doctor pointers only.
- `DELIB-0474`: Staged execution; productized gating required before stable claims.
- `DELIB-0633`: GT-KB is "promising but still alpha"; not proven as a repeatable multi-project platform.
- `DELIB-0211`, `DELIB-0472`, `DELIB-0184`, `DELIB-0601`, `DELIB-0229`: Mass-adoption readiness context.
- `bridge/gtkb-mass-adoption-readiness-012.md`: MVP VERIFIED — bridge INDEX scaffolding, provider templates, doctor accuracy, bridge rule templates landed.

---

## Revised Context

The owner asked whether GT-KB is ready for mass adoption. The answer is no. The correct framing, consistent with DELIB-0633 and prior NO-GO F4, is: **GT-KB can achieve "developer preview" / "beta candidate" readiness** via the gaps below. "Mass adoption" follows a successful field trial (G5), not the completion of docs/CI/bridge work alone.

---

## Revised Gap Baseline (against `31fe2c4`)

Each gap is classified as **ABSENT** (nothing exists) or **PRESENT BUT INSUFFICIENT** (exists; specific delta needed).

| # | Gap | Classification | What exists | What is missing |
|---|-----|----------------|-------------|-----------------|
| **G1** | Adopter documentation | **PRESENT BUT INSUFFICIENT** | `docs/bootstrap.md` (getting-started guide); `docs/start-here.md` (scaffold walkthrough); `examples/task-tracker/WALKTHROUGH.md` (non-Agent-Red example) | `bootstrap.md:12` references Agent Red deployment topology; no "Your First Specification" tutorial; no dual-agent setup guide for new developers; no auth troubleshooting doc |
| **G2** | Cross-platform bridge | **PRESENT BUT INSUFFICIENT** | OS-scheduler contract documented in `docs/method/12-file-bridge-automation.md`; generated `templates/bridge-os-poller-setup-prompt.md`; `templates/rules/bridge-essential.md` explicitly says bridge scheduler commands are not implemented in this release | Mac/Linux OS-scheduler setup instructions absent; `gt project doctor` does not check bridge freshness; no auth troubleshooting pointer from doctor |
| **G3** | GitHub CI templates | **PRESENT BUT INSUFFICIENT** | `templates/ci/build.yml`, `deploy.yml`, `test.yml`; `scaffold.py:322-328` copies all `templates/ci/*.yml` into `.github/workflows/`; `--no-include-ci` flag exists | Templates use static Agent Red project name; no stdlib placeholder substitution for project name/Python version/package name; no Dependabot or CodeRabbit integration config option |
| **G4** | ZK + multi-tenant patterns | **OUT OF SCOPE** | See below | — |
| **G5** | Second customer validation | **PRESENT BUT INSUFFICIENT** | `examples/task-tracker/WALKTHROUGH.md` is a non-Agent-Red example inside the source tree | Not an independent install-from-release proof; no structured friction report; no time-to-green-doctor target; no field trial acceptance criteria |

### G4 — Explicitly Out of Scope

G4 (zero-knowledge profiles, multi-tenant profiles, Azure Terraform modules) is removed from this proposal per NO-GO Finding 3. Reasons:

1. The current profile surface is `local-only`, `dual-agent`, `dual-agent-webapp`; adding ZK/multi-tenant profiles requires a separate design decision.
2. Generated Terraform containing security-sensitive scaffolds risks being mistaken for working cryptographic architecture.
3. Bundling app-specific Agent Red patterns into a generic toolkit requires a separate owner-scoped proposal with explicit generated-file inventory and security disclaimers.

A separate bridge proposal `gtkb-advanced-profiles-001.md` should be created when owner decides to scope that work.

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
- `grep -ri "agent.red\|remaker" docs/` returns zero matches in adopter-facing docs (`bootstrap.md`, `start-here.md`, `tutorials/`, `troubleshooting/`, `reference/`). Methodology docs under `docs/method/` are excluded from this check (they are maintainer-facing).
- `examples/task-tracker/WALKTHROUGH.md` exercises all steps described in the dual-agent setup guide without referencing Agent Red.

---

### Phase G2: Cross-Platform Bridge (OS-scheduler contract preserved)

**Goal:** A developer on macOS or Linux can follow documented steps to start the bridge OS scheduler. The Python foreground scheduler proposed in `-001` is removed. The OS-scheduler contract is the reliability boundary per `docs/method/12-file-bridge-automation.md` and `templates/bridge-os-poller-setup-prompt.md`. This phase improves the generated docs and doctor checks, not the runtime model.

**Rationale for preserving OS-scheduler contract:**
The generated `templates/rules/bridge-essential.md` explicitly states bridge scheduler commands are not implemented in this release. `docs/method/12-file-bridge-automation.md:50/116/251/264` makes the OS scheduler the reliability boundary. The generated `templates/bridge-os-poller-setup-prompt.md:42-43` directs adopters to the OS scheduler. Replacing this with a package-owned `gt bridge start` foreground process changes the bridge ownership, failure model, and generated documentation in a way that requires an explicit owner decision. That decision is not in scope here.

| WI | Deliverable | Scope |
|----|-------------|-------|
| G2.1 | **Cross-platform OS scheduler guide** | `docs/tutorials/bridge-os-scheduler.md`. Platform-specific instructions for cron (macOS/Linux) and Task Scheduler (Windows) to run the bridge poller every 3 minutes. Covers the `bridge-os-poller-setup-prompt.md` generated artifact and how to use it. |
| G2.2 | **Doctor bridge freshness check** | Extend `gt project doctor` (`doctor.py:487-537`) to: read `claude-scan-status.json` and `codex-scan-status.json` if present; check age against 4-minute WARN and 10-minute ALARM thresholds (same as `poller-freshness.py` logic); report actionable next steps including pointer to `docs/tutorials/bridge-os-scheduler.md` for setup and `docs/troubleshooting/auth.md` for auth failures. If status files are absent, report "bridge not yet started" rather than failing. |
| G2.3 | **Doctor bridge tests** | Add tests for the new doctor bridge-freshness checks using `tmp_path` for status files. Fresh-file → OK, 5-minute-old file → WARN, 15-minute-old file → ALARM, missing file → "not started". |

**Note on `gt bridge start` — owner decision required:** If the owner wants to implement package-owned `gt bridge start/status/stop` commands, a separate proposal must define: index-parser rules, lock semantics, dispatch-command contract for Prime/Codex, status-JSON schema and file locations, stop behavior, interaction with project-owned pollers, doctor/freshness acceptance tests, and confirm auth handling remains documentation-only. This phase does not implement that.

**Phase G2 exit criteria:**
- `gt project doctor` reports bridge status (OK/WARN/ALARM/not-started) based on scan-status file age.
- `gt project doctor` provides a pointer to `docs/tutorials/bridge-os-scheduler.md` when bridge is not started.
- Doctor bridge freshness tests pass on all three platform CI runners (Ubuntu + Windows + macOS).

---

### Phase G3: GitHub CI Template Parameterization (stdlib, no Jinja2 base dep)

**Goal:** Generated CI workflows from `gt project init` contain the correct project name, package name, and Python version, not hard-coded Agent Red values.

**Jinja2 decision:** Use stdlib `str.replace` placeholder substitution (same pattern as `scaffold.py:334-425`). Jinja2 stays as an optional `web` dependency. This avoids changing the base-install dependency posture. Workflow conditionals (security scan only in `full` profile) are handled by generating different source template files per profile tier, not by conditional template syntax.

**Existing surface to extend:**

| File | What to change |
|------|----------------|
| `templates/ci/build.yml` | Replace hard-coded Agent Red project/package name with `{{PROJECT_NAME}}` / `{{PACKAGE_NAME}}` placeholder |
| `templates/ci/test.yml` | Same placeholder substitution; add `{{PYTHON_VERSION}}` placeholder |
| `templates/ci/deploy.yml` | Same placeholder substitution |
| `scaffold.py:322-328` | After copying CI templates, run the existing `_render_file()` placeholder-substitution pass over `*.yml` files |

**New work:**

| WI | Deliverable | Scope |
|----|-------------|-------|
| G3.1 | **Profile-tier CI template sets** | Create `templates/ci/standard/` and `templates/ci/full/` subdirectories. `standard/` adds coverage + docstring + mypy to the `minimal/` base. `full/` adds security scan. Scaffold selects directory based on profile. The existing `templates/ci/*.yml` become the `minimal/` set. |
| G3.2 | **Integration config templates (optional flag)** | Add `templates/ci/integrations/` containing `dependabot.yml` and `.coderabbitai.yaml` with `{{PROJECT_NAME}}` placeholders. Scaffold generates these when `gt project init --integrations` is passed. No Dependabot/CodeRabbit generation by default. |
| G3.3 | **CI template tests** | Tests verify generated workflows: valid YAML (use `yaml.safe_load`), project name substituted correctly, correct tier, no hard-coded "agent-red" or "remaker" strings. |

**Phase G3 exit criteria:**
- `gt project init my-project --profile dual-agent-webapp` generates `.github/workflows/` with project-name-substituted YAML files.
- `grep -i "agent.red\|remaker" .github/workflows/*.yml` in the generated project returns zero matches.
- CI template tests pass.
- `pip install groundtruth-kb` base install does not require Jinja2.

---

### Phase G5: Second Customer Field Trial (criteria-first)

**Goal:** Prove GT-KB works for a project that isn't Agent Red, via a structured field trial. This defines the proof criteria; execution is the field trial itself.

**Revision from `-001`:** The existing `examples/task-tracker/WALKTHROUGH.md` is a non-Agent-Red example but it lives inside the source tree, not as an install-from-release proof. The second-customer proof must be an independent install from a published PyPI artifact.

| WI | Deliverable | Scope |
|----|-------------|-------|
| G5.1 | **Field trial project** | A new internal project (not inside `groundtruth-kb/`) that installs GT-KB from PyPI (`pip install groundtruth-kb==<latest>`). Exercises the full adopter journey: install → `gt project init` → first spec → first work item → first test → bridge setup via OS scheduler → first deliberation → `gt project doctor` green. Target operating systems: Windows (primary) and Ubuntu (CI). |
| G5.2 | **Field trial acceptance criteria** | Documented before starting G5.1: (a) time-to-green-doctor ≤ 60 minutes from fresh checkout; (b) `gt project doctor` reports all checks OK; (c) at least one complete proposal/review/VERIFIED bridge thread; (d) no Agent Red knowledge required to complete steps (a)–(c); (e) `pip install groundtruth-kb` succeeds on Python 3.11+ on both platforms. |
| G5.3 | **Friction report** | Every point where the adopter journey was unclear, broken, or required Agent Red knowledge. Filed as work items. Format: item / symptom / root cause / suggested fix. |
| G5.4 | **Polish round** | Fix the top-5 friction items from G5.3. |

**Phase G5 exit criteria:**
- G5.2 acceptance criteria (a)–(e) all met.
- Friction report filed and top-5 WIs created.
- Polish round complete.

---

## Dependency Graph (revised)

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
| G1 doc delta | 3 new docs + 2 file fixes | Small | Mostly writing; fixes to `bootstrap.md` |
| G2 OS-scheduler | 1 new doc + doctor extension + tests | Small-medium | Doctor extension is the main code change |
| G3 CI templates | Template parameterization + tier dirs + integration configs + tests | Medium | Stdlib substitution only; no new dep |
| G5 field trial | External project + criteria + friction report + polish | Medium-large | Execution-dependent |

---

## Success Criteria (revised to "developer preview")

GroundTruth-KB achieves **developer preview** / **beta candidate** status when ALL of the following are true:

1. **Adopter self-service:** A developer on any platform runs `pip install groundtruth-kb`, follows the Getting Started guide, and has a working project with OS-scheduler bridge, specs, and tests — without reading Agent Red source code or asking the maintainer.
2. **Cross-platform bridge setup:** The OS-scheduler bridge setup guide covers Windows, macOS, and Linux.
3. **CI out of the box:** `gt project init` generates working GitHub CI workflows with correct project-name substitution and no Agent Red references.
4. **Doctor validates everything:** `gt project doctor` checks bridge freshness, provider CLI auth (pointer to troubleshooting doc), and `bridge/INDEX.md` presence.
5. **Second customer field trial:** At least one project other than Agent Red installs from PyPI and completes the full adopter journey per G5.2 acceptance criteria.
6. **Zero Agent Red references** in any adopter-facing documentation or generated template.
7. **All existing quality gates pass:** existing test count (814 at current main), ≥70% coverage, ≥85% docstrings, mypy --strict clean, ruff clean.

**"Mass adoption" is not claimed until the field trial (G5) proves the flow from a release artifact in a fresh project on at least two platforms.**

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| `bootstrap.md` Agent Red reference touches more than one paragraph | Low | Scope the fix to L12 per Codex evidence; run `grep` before and after |
| Stdlib placeholder substitution is insufficient for conditional CI blocks (security scan only in `full`) | Low | Handled by generating different template files per tier, not conditionals |
| Doctor bridge freshness check platform differences (file modification timestamps) | Medium | Use `os.stat().st_mtime` which is cross-platform; test on Ubuntu + Windows CI |
| Field trial reveals fundamental scaffold issues | High | G5 is deliberately last; findings feed back into G1–G3 as a follow-up round |
| `gt bridge start` demand from adopters | Medium | If needed, separate proposal; this plan documents the gap and defers the decision |

---

## Open Questions (reduced from original)

1. **G5 candidate project type.** Options: (a) new internal Remaker Digital project, (b) a standalone example published alongside GT-KB under `examples/` (but installed from PyPI independently). Recommendation: (a) — a real new internal project is a stronger adoption proof than another example in the source tree.

2. **`gt bridge start` — owner decision required.** If the owner wants package-owned bridge commands as described in original G2, a separate proposal is needed with the decision criteria listed in the G2 note above. This proposal does not include that work.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
