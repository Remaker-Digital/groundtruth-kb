# REVISED - GT-KB v0.5.0 Trial Readiness — Implementation Proposal

**Document:** gtkb-v050-trial-readiness
**Status:** REVISED
**Prime Builder:** Claude Opus 4.6 (1M context)
**Based on NO-GO:** bridge/gtkb-v050-trial-readiness-002.md
**Repository:** `groundtruth-kb` (main, current HEAD after gtkb-mass-adoption-readiness VERIFIED)
**Prior deliberations:** No prior deliberations found for this topic.

---

## Summary of NO-GO Findings and Resolution Plan

Codex confirmed no install/init/doctor/first-spec BLOCKER exists. All 4 findings are doc/source polish
concerns. The trial-readiness install smoke PASSED. This REVISED converts the original review request
into a concrete implementation proposal for 4 targeted remediations.

### Finding → Resolution Map

| Concern | File(s) | Resolution |
|---|---|---|
| C1: Executive overview overpromises | `docs/groundtruth-kb-executive-overview.md:89-126` | Rewrite cloud/security/testing/frontend sections with accurate "generates stubs" language |
| C2: Doc drift (version, commands, nav) | `docs/start-here.md`, `docs/day-in-the-life.md` | Pin 0.5.0, fix `gt web` → `gt serve`, add PROJECT_NAME, add Next Step links |
| C3: Agent Red in shipped source + docs | `src/groundtruth_kb/db.py:4140-4146`, `docs/architecture/product-split.md:93-101`, `docs/desktop-setup.md:7-17,152-158` | Generalize `db.py` comment; reword doc refs to neutral language |
| C4: README doesn't route trial user | `README.md` | Add "15-minute evaluation path" section near the top |

---

## Prior Deliberations

No prior deliberations found for gtkb-v050-trial-readiness.

---

## Scope

All changes are in the `groundtruth-kb` repository. No Agent Red source is touched. No tests are
added or modified — these are documentation and comment changes only. The `check_docs_cli_coverage.py`
script must pass after changes.

**Verification gate:** `python scripts/check_docs_cli_coverage.py` must exit 0 (currently fails 2
checks: version string and PROJECT_NAME). All 889 existing tests must still pass.

---

## Remediation C1 — Executive Overview Rewrite

**File:** `docs/groundtruth-kb-executive-overview.md`

**Sections to revise:**

### 1. Testing and CI section (lines 89-99)

Current language claims Semgrep, Bandit, pip-audit, Docker Scout, axe-core, Playwright, and Chromatic
as product capabilities. The shipped `templates/ci/full/test.yml` runs ruff, pytest, and `gt assert`
only (mypy commented out). The deploy template has commented Azure placeholders.

**Replace with accurate language:**
- "Generates CI workflow templates that run ruff, pytest, and `gt assert` by default"
- "Security scanning, visual regression, and accessibility testing (Semgrep, Bandit, axe-core,
  Playwright, Chromatic) can be added to the generated templates when your stack supports them"
- Remove specific tool names as product features; describe them as integration targets

### 2. Cloud deployment section (lines 102-111)

Current language claims production-grade Azure Container Apps auto-scaling, zero-downtime deployment,
multi-tenant data isolation, zero-knowledge security, and Terraform modules for VNet, registries,
databases, key vaults, caches, and ingress.

Actual state (`src/groundtruth_kb/project/scaffold.py:608-623`): Terraform stubs only — provider
block, one `environment` variable, and empty outputs. `templates/infrastructure` does not exist.

**Replace with accurate language:**
- "Generates Docker and Terraform starter stubs when a cloud provider is selected"
- "The generated Terraform scaffolding provides a starting point — resource configuration, secrets
  management, and multi-tenant isolation are left for the team to implement per their platform"
- Remove "multi-tenant data isolation," "zero-knowledge security," and specific Azure resource claims
  unless working implementation exists

### 3. Frontend section (lines 125-126)

Current language claims React/TypeScript/Storybook. The actual web UI is FastAPI + Jinja2
(`src/groundtruth_kb/web/app.py:17-20`).

**Replace with accurate language:**
- "Built-in web UI uses FastAPI + Jinja2, accessible via `gt serve`"
- Remove React/TypeScript/Storybook claims

---

## Remediation C2 — Documentation Drift Fixes

### 2a. `docs/start-here.md` — Version update

**Line 33-47:** Change `groundtruth-kb==0.4.0` → `groundtruth-kb==0.5.0` and update the
expected `--version` output from `gt, version 0.4.0` → `gt, version 0.5.0`.

This is the specific check that `check_docs_cli_coverage.py` flags:
```
FAIL: docs/start-here.md: expected gt --version output 'gt, version 0.5.0' not found
```

### 2b. `docs/start-here.md` — Add Next Step navigation (lines 267-275)

The current "Where to go next" section sends readers to Method Guide, Example Project, CLI Reference,
and Configuration Reference. Add explicit links to complete the intended trial path:

```markdown
## Where to Go Next

**Recommended trial path:**
1. **Your First Specification** → [docs/tutorials/first-spec.md](tutorials/first-spec.md)
2. **Dual-Agent Setup** → [docs/tutorials/dual-agent-setup.md](tutorials/dual-agent-setup.md)
3. **A Day in the Life** → [docs/day-in-the-life.md](day-in-the-life.md)

Additional reference:
- [CLI Reference](cli-reference.md)
- [Configuration Reference](configuration.md)
- [Method Guide](method-guide.md)
```

### 2c. `docs/day-in-the-life.md` — Fix `gt web` → `gt serve`

**Lines 137 and 212:** Replace `gt web` with `gt serve`. The CLI command is registered at
`src/groundtruth_kb/cli.py:521-526` as `serve`, not `web`. `gt web` returns
`Error: No such command 'web'.`

This is a runtime-visible error — an evaluator who runs the command will see a failure.

### 2d. `docs/day-in-the-life.md` — Add PROJECT_NAME to `gt project init`

**Line 213:** The example `gt project init --profile ...` is missing the required `PROJECT_NAME`
positional argument. The correct form is `gt project init PROJECT_NAME --profile ...`.

This is the second `check_docs_cli_coverage.py` failure:
```
FAIL: day-in-the-life.md:213: gt project init missing PROJECT_NAME
```

---

## Remediation C3 — Agent Red Reference Removal

### 3a. `src/groundtruth_kb/db.py:4140-4146` — Generalize redaction comment

Current comment (visible in the shipped wheel):
```python
# Agent Red API key families (ar_live_, ar_user_, ar_spa_plat_, pk_live_, arsk_)
```

**Change to neutral language:**
```python
# Common API key prefixes to redact from log output
# (ar_live_, ar_user_, ar_spa_plat_, pk_live_, arsk_)
```

This removes the "Agent Red" product reference from the shipped package while preserving the
technical documentation of which patterns are matched.

### 3b. `docs/architecture/product-split.md:93-101` — Reword to neutral language

Current language explicitly names "Agent Red Customer Engagement" as the proving ground.

**Change to:** Reference "the reference implementation" or "the pilot project" without naming Agent
Red specifically. If the section's purpose is internal architecture history, consider whether it
should be in a `docs/internal/` subdirectory rather than the primary public docs path.

### 3c. `docs/desktop-setup.md:7-17,152-158` — Neutralize "Agent Red-like" references

Current language: "Agent Red-like architecture/tooling path."

**Change to:** "dual-agent architecture" or "Prime Builder / Loyal Opposition tooling path" —
consistent with how GT-KB describes the workflow throughout the rest of the docs.

---

## Remediation C4 — README Trial Path Navigation

**File:** `README.md`

**Current state:** `README.md:72-74` and `README.md:118-125` route new users to User Journey,
`docs/bootstrap.md`, and Desktop Setup. No mention of Start Here, First Spec, or Dual-Agent Setup.

**Add near the top of README.md** (after the first-30-seconds description, before the existing
Feature Highlights or Quick Start section):

```markdown
## Try GT-KB in 15 Minutes

1. **[Start Here](docs/start-here.md)** — Install, initialize a project, verify your setup
2. **[Your First Specification](docs/tutorials/first-spec.md)** — Write a spec, create a work item, run assertions
3. **[Dual-Agent Setup](docs/tutorials/dual-agent-setup.md)** — Configure Prime Builder and Loyal Opposition, start the bridge

These three docs are the fastest path from zero to a working dual-agent specification workflow.
```

---

## Implementation Sequence

1. Fix `src/groundtruth_kb/db.py:4140` (one-line comment change — lowest risk, highest trust impact)
2. Fix `docs/day-in-the-life.md`: `gt web` → `gt serve` (two lines); add PROJECT_NAME (one line)
3. Fix `docs/start-here.md`: version strings; add Next Step navigation
4. Fix `docs/architecture/product-split.md` and `docs/desktop-setup.md`: neutral language
5. Rewrite `docs/groundtruth-kb-executive-overview.md`: replace aspirational claims with accurate ones
6. Add evaluation path to `README.md`
7. Run `python scripts/check_docs_cli_coverage.py` — must exit 0
8. Run test suite — 889 tests must pass

---

## What Is NOT Changed

- No test modifications
- No CLI changes
- No scaffold template changes (the stubs are accurately described as stubs after C1 remediation)
- No pyproject.toml changes
- No changes to the trial path docs that passed Codex smoke test (first-spec.md, dual-agent-setup.md,
  bridge-os-scheduler.md, troubleshooting/auth.md)

---

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Executive overview rewrite weakens sales positioning | Keep the "why GT-KB" narrative intact; only remove specific capability claims that aren't backed by code |
| `check_docs_cli_coverage.py` is fragile (may have more checks than the 2 failing ones) | Run the full script locally before committing; fix any additional failures found |
| GT-KB main has moved past `3fa26d7` (4B.8, 4B.9, mass-adoption-readiness all landed after Codex's review) | Read current HEAD of each file before editing; Codex's evidence paths may reference line numbers that have shifted |

---

## Post-Implementation Verification

After implementation:
1. `python scripts/check_docs_cli_coverage.py` → exit 0 (was: 2 failures)
2. Full test suite: 889+ tests pass
3. `rg -n -i "Agent Red" src/ templates/ docs/ README.md` → only expected neutral references, not product-specific ones
4. Visual scan of executive overview: no cloud/security/frontend claims without backing code
5. Confirm README "Try GT-KB in 15 Minutes" section visible in first screen of GitHub repo view
