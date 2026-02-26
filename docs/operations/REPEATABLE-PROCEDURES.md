# Repeatable Procedures — Specification

This document defines what a Repeatable Procedure is, how to create one, and how to maintain one. All procedures referenced here are operational SOPs (Standard Operating Procedures) that must be executable with consistent results across sessions and operators.

> **Audience:** AI assistants (Claude) and human operators.
> **Authority:** This specification is referenced from `CLAUDE.md` and governs all files tagged as Repeatable Procedures.

---

## 1. What Is a Repeatable Procedure

A Repeatable Procedure is a document that describes a fixed sequence of steps to accomplish an operational task. It is designed to produce the same outcome every time it is executed, regardless of which session or operator runs it.

A Repeatable Procedure is **not**:
- Prose guidance or best practices (use docs for that)
- A troubleshooting guide (those are reactive; procedures are proactive)
- A one-time migration script (those are versioned artifacts, not living SOPs)

### Identified Repeatable Procedures

| Procedure | File | Status |
|-----------|------|--------|
| Production deployment | `scripts/deploy/upgrade.ps1` | Active |
| Production rollback | `scripts/deploy/rollback.ps1` | Active |
| Tenant initialization | `docs/operations/initialization-procedure.md` | Active |
| Non-disruptive upgrade verification | `docs/operations/upgrade-verification-procedure.md` | Active |
| Tenant provisioning (seed script) | `scripts/seed_tenant.py` | Active |
| Admin UI test | `docs/operations/ui-test-procedure.md` | Active |
| Unit test suite | *(inline — see Section 5)* | Active |
| Production regression suite | *(inline — see Section 5)* | Active |
| Azure environment setup | `docs/operations/CATASTROPHIC-RECOVERY-RUNBOOK.md` | Active |
| AGNTCY platform adoption | `docs/operations/agntcy-platform-adoption-procedure.md` | Active |
| Build & deploy (staging/production) | `docs/operations/build-deploy-procedure.md` | Active |
| Admin UI lint (a11y) | *(inline — see Section 5)* | Active |
| External URL reachability | `docs/operations/external-url-reachability-procedure.md` | Active |
| Chrome-automated UI test | `docs/operations/chrome-ui-test-procedure.md` | Active |
| Load testing | `docs/operations/load-test-procedure.md` | Active |
| Tenant isolation verification | `docs/operations/tenant-isolation-test-procedure.md` | Active |
| API security & penetration testing | `docs/operations/api-security-test-procedure.md` | Active |
| Rate limiting & DoS resilience | `docs/operations/rate-limit-test-procedure.md` | Active |
| Conversation quality regression | `docs/operations/conversation-quality-test-procedure.md` | Active |
| Resilience & failover testing | `docs/operations/resilience-failover-test-procedure.md` | Active |
| Data integrity & backup verification | `docs/operations/data-integrity-test-procedure.md` | Active |
| Session wrap-up | `docs/operations/session-wrap-up-procedure.md` | Active |

> **Cross-procedure dependencies:**
> - *Build & deploy* must be executed before *Non-disruptive upgrade verification*, *Production regression suite*, and any other procedure that requires a fresh deployment. All 4 build targets (3 admin SPAs + widget) must pass the freshness gate before ACR build.
> - *Admin UI test* depends on *Tenant initialization*. After initialization, all post-conditions (Steps 2-5) must pass before the UI test pre-flight will pass.
> - *Chrome-automated UI test* depends on *Tenant initialization* (same dependency as manual UI test). Also depends on *External URL reachability* Group 1 + Group 2 passing.
> - *External URL reachability* has no initialization dependency — can run as a standalone health check after any deployment.
> - *Non-disruptive upgrade verification* wraps *Build & deploy* with pre/post data integrity checks.
> - *Tenant initialization* is destructive. Use *Non-disruptive upgrade verification* when existing data must be preserved.
> - *Load testing* depends on production being healthy and Locust being installed. Uses existing `tests/performance/locustfile.py`.
> - *Tenant isolation verification* depends on both tenants (remaker-digital-001 and test-customer-001) being seeded with data.
> - *API security & penetration testing* depends on production being healthy. Creates `tests/security/test_live_penetration.py`.
> - *Rate limiting & DoS resilience* depends on both tenants being accessible. Intentionally exhausts rate limits — wait 60s before running other live tests.
> - *Conversation quality regression* depends on NATS being connected (AI pipeline functional). Cannot run if chat is unavailable.
> - *Resilience & failover testing* does NOT require all dependencies to be healthy — it tests behavior under degradation.
> - *Data integrity & backup verification* depends on Azure CLI access and Cosmos DB being accessible.

---

## 2. Structure of a Repeatable Procedure

Every Repeatable Procedure must contain these sections, in order:

### 2.1 Header

```
# [Procedure Name]
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: YYYY-MM-DD
# Last corrected: YYYY-MM-DD — [one-line description of correction]
```

The `Last verified` date is updated each time the procedure is executed successfully without corrections. The `Last corrected` date is updated each time the procedure itself is modified due to a defect discovered during execution.

### 2.2 Variables Block

All environment-specific values must be declared as named variables at the top of the procedure. No literal values may appear in step commands — only variable references.

```
VARIABLES:
  ACR_NAME          = acragentredeastus
  ACR_LOGIN_SERVER  = acragentredeastus.azurecr.io
  RESOURCE_GROUP    = Agent-Red
  CONTAINER_APP     = agent-red-api-gateway
  PROD_URL          = https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
  PROJECT_ROOT      = E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
```

**Rule:** If a value appears in more than one step, it must be a variable. If a variable value changes, it is updated in exactly one place (the variables block), not throughout the document.

### 2.3 Preconditions

A checklist of conditions that must be true before the procedure begins. Each precondition has a verification command.

```
PRECONDITIONS:
  [ ] Azure CLI authenticated          — az account show
  [ ] ACR accessible                   — az acr show --name $ACR_NAME
  [ ] Production healthy               — curl $PROD_URL/health → 200
  [ ] Admin UI builds exist            — ls admin/standalone/dist/index.html
```

**Rule:** If any precondition fails, the procedure does not start. No "proceed anyway" option.

### 2.4 Steps

Numbered steps, each containing:
- **Action:** The exact command to run (using variable references)
- **Expected output:** What success looks like (specific string, exit code, or status)
- **Verification gate:** A command that confirms the step succeeded before proceeding
- **Failure branch:** What to do if the step fails (retry, abort, or skip with justification)

```
STEP 3: Build and push Docker image
  ACTION:    az acr build --registry $ACR_NAME --image $IMAGE_NAME:$VERSION .
  EXPECTED:  ACR build status = "Succeeded"
  VERIFY:    az acr task list-runs --registry $ACR_NAME --top 1 --query "[0].status" -o tsv
  ON FAIL:   Check ACR portal for build logs. Do not proceed.
```

### 2.5 Postconditions

A checklist of conditions that must be true after the procedure completes. These constitute the acceptance criteria.

```
POSTCONDITIONS:
  [ ] /health returns 200              — curl $PROD_URL/health
  [ ] /ready returns 200               — curl $PROD_URL/ready
  [ ] New image is serving             — az containerapp show ... --query "...image"
```

### 2.6 Known Failure Modes

A table of failures encountered during previous executions, classified as either **procedure defects** or **environment transients**.

```
KNOWN FAILURE MODES:
  | Failure | Classification | Resolution |
  |---------|---------------|------------|
  | az acr build UnicodeEncodeError on Windows | Environment (Windows encoding) | Use az acr task list-runs to verify instead of relying on log stream |
  | Resource group name mismatch | Procedure defect (corrected 2026-02-14) | Variable block updated from rg-agentred-eastus to Agent-Red |
```

---

## 3. Error Handling During Execution

When executing a Repeatable Procedure and an error occurs:

### 3.1 Classification

Determine whether the error is a **procedure defect** or an **environment transient**:

| Type | Definition | Examples |
|------|-----------|----------|
| **Procedure defect** | The procedure itself is wrong — a variable is stale, a step is missing, an assumption is invalid | Wrong resource group name, missing prerequisite step, outdated command syntax |
| **Environment transient** | The environment is temporarily unavailable or behaving unexpectedly, but the procedure is correct | Network timeout, Azure service briefly unavailable, rate limiting |

### 3.2 Response

- **Procedure defect:** Fix the issue to unblock execution, AND update the procedure document before continuing. Record the correction in the `Last corrected` header and add an entry to the Known Failure Modes table.
- **Environment transient:** Retry the step. If it fails again after a reasonable wait, document the transient in the Known Failure Modes table for awareness but do not modify the procedure steps.

### 3.3 Behavioral Rule for AI Assistants

> When following a Repeatable Procedure and encountering an error, treat the error as informative. Focus on correcting the procedure first, not just fixing the immediate issue. The goal is that the next execution will not encounter the same error.

This means:
1. Do not silently work around a procedure defect — flag it and update the document
2. Do not modify the procedure for a transient — note it but leave the steps unchanged
3. After correcting a procedure defect, re-execute from the corrected step to verify the fix

---

## 4. Maintenance

### 4.1 When to Update a Procedure

- After every execution that reveals a defect (mandatory)
- After infrastructure changes that affect variables (e.g., resource group renamed)
- During quarterly review (recommended)

### 4.2 When NOT to Update a Procedure

- After a successful execution with no issues (only update `Last verified` date)
- For one-time workarounds that won't recur
- For environment transients that resolved on retry

### 4.3 Version Control

Procedures are version-controlled in git alongside the codebase. Changes to procedures follow the same commit practices as code changes.

---

## 5. Inline Procedure Definitions

Some procedures are short enough to define inline rather than in separate files. These still follow the structure above but are embedded in this document.

### Unit Test Suite

```
PROCEDURE: Run Unit Test Suite (Thermal-Safe)
TYPE: Repeatable Procedure
LAST VERIFIED: 2026-02-22
LAST CORRECTED: 2026-02-22 — Thermal-safe batched execution with pytest-xdist (S74)

VARIABLES:
  PROJECT_ROOT = E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
  EXPECTED_MIN_PASS = 4000
  EXPECTED_MAX_SKIP = 10
  EXPECTED_FAILURES = 0
  XDIST_WORKERS = 4
  COOLDOWN_SECONDS = 30

PRECONDITIONS:
  [ ] Python 3.12+ available             — python --version
  [ ] pytest installed                    — python -m pytest --version
  [ ] pytest-xdist installed             — python -m pytest --co -n 0 (should not error)
  [ ] pytest-timeout installed           — verify in pytest --version output
  [ ] Working directory is PROJECT_ROOT  — pwd

STEPS:
  STEP 1: Run thermal-safe batched test suite
    ACTION:    .\scripts\run-tests-thermal-safe.ps1 -Workers $XDIST_WORKERS -CoolDown $COOLDOWN_SECONDS -SkipLive
    EXPECTED:  Exit code 0, "OVERALL: PASS" summary line
    VERIFY:    Sum of passed counts across all batches >= $EXPECTED_MIN_PASS
               Sum of failed counts == $EXPECTED_FAILURES
    ON FAIL:   Identify which batch failed. Re-run that batch in isolation:
               .\scripts\run-tests-thermal-safe.ps1 -Batch <batch-name> -Workers 2

  STEP 1-ALT: Run tests without thermal safety (CI/cold environments only)
    ACTION:    python -m pytest tests/ --ignore=tests/integration --ignore=tests/regression --ignore=tests/performance -n auto --timeout=30 -q --tb=short
    EXPECTED:  Exit code 0, "N passed, M skipped" summary line
    VERIFY:    Parse summary line: passed >= $EXPECTED_MIN_PASS,
               skipped <= $EXPECTED_MAX_SKIP, failed == $EXPECTED_FAILURES
    NOTE:      Use ONLY when thermal limits are not a concern (CI runners, cold ambient)

POSTCONDITIONS:
  [ ] All tests passed (0 failures)
  [ ] Pass count >= $EXPECTED_MIN_PASS (currently ~4,574 as of session 74)
  [ ] Skip count <= $EXPECTED_MAX_SKIP (currently 5)
  [ ] No BSOD or thermal shutdown during test execution

KNOWN FAILURE MODES:
  | Failure | Classification | Resolution |
  |---------|---------------|------------|
  | Heat-related BSOD during test run | Environment transient | Reduce -Workers to 2, increase -CoolDown to 60. If persistent, check CPU cooler and ambient temperature. |
  | pytest-xdist "no such option: -n" | Procedure defect (missing dep) | pip install pytest-xdist>=3.5.0 |
  | Test timeout (>30s) on a unit test | Procedure defect (test is broken) | Investigate the specific test. Unit tests should complete in <5s. |
  | Azure integration test fails (RBAC) | Environment transient | Unrelated to unit tests; skip with -k "not azure_integration" |
  | Count drift between sessions | Procedure defect (if significant) | Count may vary ±50 due to test collection changes during refactoring. Update EXPECTED_MIN_PASS if sustained. |
```

### Admin UI Lint (Accessibility)

```
PROCEDURE: Run Admin UI Lint
TYPE: Repeatable Procedure
LAST VERIFIED: 2026-02-18

VARIABLES:
  PROJECT_ROOT = E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
  ADMIN_DIR    = $PROJECT_ROOT/admin

PRECONDITIONS:
  [ ] Node.js 18+ available               — node --version
  [ ] npm available                        — npm --version
  [ ] Dependencies installed               — ls $ADMIN_DIR/node_modules/.package-lock.json

STEPS:
  STEP 1: Run ESLint with jsx-a11y plugin
    ACTION:    cd $ADMIN_DIR && npx eslint --ext .tsx,.ts,.jsx,.js shared/ standalone/ provider/ shopify/ --max-warnings 50
    EXPECTED:  Exit code 0, warnings ≤ 50
    VERIFY:    Exit code 0
    ON FAIL:   Review a11y warnings. Errors must be fixed; warnings are advisory.

POSTCONDITIONS:
  [ ] No lint errors (only warnings allowed)
  [ ] jsx-a11y/click-events-have-key-events warnings ≤ 20
  [ ] All new components have aria-label on interactive elements

KNOWN FAILURE MODES:
  | Failure | Classification | Resolution |
  |---------|---------------|------------|
  | Module not found: eslint-plugin-jsx-a11y | Environment (deps) | Run npm install in $ADMIN_DIR |
  | Parser errors on .tsx files | Environment (deps) | Ensure @typescript-eslint/parser is installed |
```

### Production Regression Suite

```
PROCEDURE: Run Production Regression Suite
TYPE: Repeatable Procedure
LAST VERIFIED: 2026-02-17

VARIABLES:
  PROJECT_ROOT       = E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
  PROD_URL           = https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
  WIDGET_KEY         = (from .env.local PREVIEW_WIDGET_KEY; rotates on every re-seed)
  AGENTRED_API_KEY   = (superadmin user API key — must match .env.local SUPERADMIN_PREVIEW_API_KEY; rotates on every re-seed)
  TIER0_COUNT        = 17
  TIER1_COUNT        = 28
  TIER2_COUNT        = 10

PRECONDITIONS:
  [ ] Python 3.12+ available                    — python --version
  [ ] pytest + httpx installed                   — python -m pytest --version
  [ ] Production endpoint reachable              — curl $PROD_URL/health → 200
  [ ] AGENTRED_API_KEY set (for Tier 1 admin)    — echo $AGENTRED_API_KEY
  [ ] Credentials current (after re-seed)        — .env.local keys match seed output; Key Vault updated; revision restarted (see seed_tenant.py POST-SEED STEPS)

STEPS:
  STEP 1: Run Tier 0 (Blocking — rollback if any fail)
    ACTION:    PROD_URL=$PROD_URL WIDGET_KEY=$WIDGET_KEY python -m pytest tests/regression/test_upgrade_regression.py -x -q -m tier0 --tb=short
    EXPECTED:  17 passed, 0 failed
    VERIFY:    Exit code 0; summary line shows "$TIER0_COUNT passed"
    ON FAIL:   STOP. Rollback deployment immediately (scripts/deploy/rollback.ps1).

  STEP 2: Run Tier 1 (Pre-launch gate)
    ACTION:    PROD_URL=$PROD_URL WIDGET_KEY=$WIDGET_KEY AGENTRED_API_KEY=$AGENTRED_API_KEY python -m pytest tests/regression/test_upgrade_regression.py -x -q -m tier1 --tb=short
    EXPECTED:  20 passed, 0 failed (some may skip if AGENTRED_API_KEY not set)
    VERIFY:    Exit code 0; summary line shows passed >= 10
    ON FAIL:   Investigate. Do not cut traffic until resolved.

  STEP 3: Run Tier 2 (Performance smoke)
    ACTION:    PROD_URL=$PROD_URL python -m pytest tests/regression/test_upgrade_regression.py -x -q -m tier2 --tb=short
    EXPECTED:  10 passed, 0 failed
    VERIFY:    Exit code 0; all latency assertions within SLA
    ON FAIL:   Log performance regression. Does not block deployment.

POSTCONDITIONS:
  [ ] Tier 0: $TIER0_COUNT passed, 0 failed
  [ ] Tier 1: passed >= 10 (admin tests may skip without API key)
  [ ] Tier 2: passed >= 8 (performance tests informational)

KNOWN FAILURE MODES:
  | Failure | Classification | Resolution |
  |---------|---------------|------------|
  | NATS not ready (503 on chat endpoints) | Environment transient | Wait 30-60s after deployment for NATS warmup. Tests skip 503 gracefully. |
  | AGENTRED_API_KEY not set → Tier 1 skips | Environment (operator) | Set env var before running: $env:AGENTRED_API_KEY = "ar_user_..." |
  | Production unreachable → entire suite skips | Environment transient | conftest.py skips all tests if /health fails connectivity check |
  | Health P95 latency spike after deploy | Environment transient | Cold start. Re-run Tier 2 after 5 minutes. |
  | Tier 1 auth failures after re-seed (401/403) | Procedure defect (if .env.local not updated) | Re-seed generates new keys. Update .env.local, Key Vault, and restart revision per seed_tenant.py POST-SEED STEPS. |
```

---

## 6. Creating a New Repeatable Procedure

When asked to create a new Repeatable Procedure:

1. Follow the structure in Section 2 exactly
2. Derive variables from the current known-good state (memory files, infrastructure)
3. Include verification gates after every step that can fail
4. Run the procedure once to validate it before marking it as "Active"
5. Record all errors encountered during the first run as Known Failure Modes

When the owner says "create a repeatable procedure for X" or "treat this as an SOP," this specification governs the result.

---

## 7. No Hardcoded Transient Values

> **Principle:** All transient keys, values, URLs, or other variables whose values change between builds, re-seeds, or tenant environments must **never** be hardcoded anywhere in code, test scripts, or documentation commands. In all cases, these values must be read from the tenant's secure configuration store (Cosmos DB / Azure Key Vault) or from `.env.local` at runtime.

### 7.1 What Is a Transient Value

A value is **transient** if any of these apply:

- It rotates when `seed_tenant.py` is re-run (API keys, widget keys, key hashes)
- It changes between environments (production URL, subscription ID, resource names)
- It expires or is revoked independently (Stripe keys, OAuth tokens, webhook secrets)
- It differs between tenants (tenant ID, shop domain, tier)

### 7.2 Approved Sources for Transient Values

| Source | When to Use |
|--------|-------------|
| `.env.local` | Local development, test scripts, CI runners |
| Azure Key Vault | Production runtime (Container App env refs) |
| Cosmos DB tenant/preferences documents | Tenant-scoped configuration at runtime |
| `os.environ` (populated from above) | Code that reads credentials |
| Repeatable Procedure Variables block | Declared once, referenced by name in steps |

### 7.3 Prohibited Patterns

```python
# WRONG — hardcoded credential that will silently rot after re-seed
WIDGET_KEY = "pk_live_c79a2bd0_d008012c"

# WRONG — hardcoded fallback that masks missing configuration
WIDGET_KEY = os.environ.get("WIDGET_KEY", "pk_live_c79a2bd0_d008012c")

# CORRECT — fail fast if credential is not configured
WIDGET_KEY = os.environ.get("PREVIEW_WIDGET_KEY", "")
if not WIDGET_KEY:
    sys.exit("ERROR: PREVIEW_WIDGET_KEY not set.")

# CORRECT — load from .env.local, then read from env
_env_local = Path(__file__).resolve().parent.parent / ".env.local"
# ... load loop ...
WIDGET_KEY = os.environ.get("PREVIEW_WIDGET_KEY", "")
```

### 7.4 Exceptions

- **Procedure Variables blocks** may declare the *current* value of a transient variable (Section 2.2), but must note that it rotates (e.g., `WIDGET_KEY = (from .env.local PREVIEW_WIDGET_KEY; rotates on every re-seed)`)
- **Unit test mock fixtures** may use obviously fake values (e.g., `arsk_test_starter_key_001`, `pk_live_invalid_key_00000000`) since they never hit real infrastructure
- **Documentation** may reference variable *patterns* (e.g., `pk_live_{tenant_hash}_{random}`) but must not embed actual live values in example commands

### 7.5 Enforcement

When creating or modifying code, test scripts, or documentation:

1. Search for any literal credential values before committing
2. Replace with environment variable reads or variable references
3. If a fallback default is required for graceful degradation, use an obviously invalid sentinel (e.g., empty string) and fail fast with a clear error message
4. Add the variable to `.env.local` if it isn't already there

### 7.6 Related Procedures

- `seed_tenant.py` POST-SEED STEPS — lists all locations that must be updated after re-seed
- `ui-test-procedure.md` Pre-flight — cross-references seed credential updates
- `REPEATABLE-PROCEDURES.md` Production Regression Suite — precondition for current credentials

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-25*
