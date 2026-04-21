# Agent Red GO-State Patch Queue - 2026-04-19

This file records patch-ready remediation work for the GO-state recovery plan.
It does not modify existing project files. Existing files require explicit file-specific owner approval before application.

## Application Status

- Patch Set 1: APPLIED and locally verified.
- Patch Set 2: PARTIALLY APPLIED through centralized startup guard, standalone-admin deployed fail-closed behavior, and restore-template env updates.
- Patch Set 3: APPLIED and locally verified.
- Patch Set 4: PARTIALLY APPLIED by deleting the generated secret manifest and ignoring future generated production gateway YAML. Credential rotation and any git-history purge remain external/blocking.
- Patch Set 5: NOT STARTED; owner launch-scope decision still required.
- Patch Set 6: APPLIED and locally verified through the Python/security release gate.

## Patch Set 1 - CI/Security Gate Recovery

### Target files requiring approval

1. `tests/unit/test_deploy_scaling.py`
2. `.github/workflows/security-scan.yml`

### Intent

- Restore the blocking Ruff E/F gate.
- Make the Security Scan workflow capable of seeing secrets outside `src/`.
- Make Docker Scout able to build the image that uses the private ACR base image.

### Proposed changes

#### 1. Remove unused pytest import

File: `tests/unit/test_deploy_scaling.py`

```diff
-import pytest
```

Expected verification:

```powershell
python -m ruff check src/ tests/ --select E,F
```

#### 2. Expand Security Scan trigger scope

File: `.github/workflows/security-scan.yml`

Add workflow path triggers for scripts and workflow/config changes:

```diff
   pull_request:
     paths:
       - 'src/**'
       - 'tests/**'
       - 'requirements*.txt'
       - 'pyproject.toml'
       - 'Dockerfile*'
+      - 'scripts/**'
+      - '.github/workflows/security-scan.yml'
   push:
     branches: [develop, 'hotfix/**']
     paths:
       - 'src/**'
+      - 'tests/**'
       - 'requirements*.txt'
+      - 'pyproject.toml'
+      - 'Dockerfile*'
+      - 'scripts/**'
+      - '.github/workflows/security-scan.yml'
```

#### 3. Scan full repository for secrets

File: `.github/workflows/security-scan.yml`

Replace Semgrep's `src/` target with repository-wide scanning and explicit excludes:

```diff
           semgrep --config p/python --config p/security-audit --config p/secrets \
             --json --output .quality/semgrep.json \
-            src/ || true
+            --exclude .git --exclude .venv --exclude node_modules \
+            --exclude "admin/**/node_modules" --exclude "widget/node_modules" \
+            . || true
           semgrep --config p/python --config p/security-audit --config p/secrets \
-            src/
+            --exclude .git --exclude .venv --exclude node_modules \
+            --exclude "admin/**/node_modules" --exclude "widget/node_modules" \
+            .
```

Note: this may surface additional true positives in docs/scripts. That is expected for release recovery.

#### 4. Add ACR login before Docker Scout build

File: `.github/workflows/security-scan.yml`

Reuse the same pattern already present in `build-api-gateway.yml` and `build-agent-containers.yml`:

```diff
       - name: Set up Docker
         uses: docker/setup-buildx-action@v3

+      - name: Login to ACR
+        uses: azure/docker-login@v2
+        with:
+          login-server: acragentredeastus.azurecr.io
+          username: ${{ secrets.ACR_USERNAME }}
+          password: ${{ secrets.ACR_PASSWORD }}
+
       - name: Build image for scanning
         run: docker build -t agent-red-scan:local . --no-cache
```

Expected verification:

```powershell
python -m ruff check src/ tests/ --select E,F
gh workflow run "Security Scan" --ref develop
```

## Patch Set 2 - Production Fail-Closed Configuration

### Target files requiring approval

1. `src/app/lifecycle.py`
2. `src/app/standalone_auth.py`
3. `src/multi_tenant/magic_link_auth.py`
4. `src/multi_tenant/tenant_recovery.py`
5. `src/multi_tenant/admin_mfa_auth.py`
6. `src/multi_tenant/mfa_totp.py`
7. `src/multi_tenant/widget_otp_verification.py`
8. `src/integrations/shopify_billing.py`
9. `src/integrations/stripe_checkout.py`
10. `src/integrations/stripe_packs.py`
11. `src/integrations/stripe_portal.py`

### Intent

- Fail startup in `staging` and `production` when required signing/admin/commerce/CORS values are missing or unsafe.
- Remove production reliance on static fallback secrets.
- Prevent localhost redirect URLs in production commerce flows.

### Proposed lifecycle guard

Add a startup handler near the existing fail-closed envelope encryption startup guard:

```python
def _is_deployed_environment() -> bool:
    return os.environ.get("ENVIRONMENT", "development").lower().strip() in {"staging", "production"}


def _require_env(name: str, *, min_length: int = 1, disallow_values: set[str] | None = None) -> None:
    value = os.environ.get(name, "").strip()
    if not value or len(value) < min_length or value in (disallow_values or set()):
        raise RuntimeError(f"{name} is required for {os.environ.get('ENVIRONMENT')} startup")


async def _startup_required_production_config() -> None:
    if not _is_deployed_environment():
        return

    for name in (
        "ADMIN_PREVIEW_PASSWORD",
        "ADMIN_SESSION_SECRET",
        "MAGIC_LINK_JWT_SECRET",
        "MFA_JWT_SECRET",
        "CUSTOMER_TOKEN_SECRET",
    ):
        _require_env(name, min_length=32)

    _require_env("APP_BASE_URL")
    if os.environ["APP_BASE_URL"].startswith(("http://localhost", "http://127.0.0.1")):
        raise RuntimeError("APP_BASE_URL must not point at localhost in deployed environments")

    _require_env("APP_CORS_ORIGINS")
```

Register it before other startup handlers:

```diff
     _lifecycle_startup_handlers.extend(
         [
+            _startup_required_production_config,
             _startup_verification_secret,
             _startup_cosmos_db,
```

Expected verification:

```powershell
python -m pytest tests/security/test_standalone_admin_hardening.py tests/multi_tenant/test_magic_link_auth.py tests/multi_tenant/test_mfa_totp.py tests/unit/test_widget_otp_verification.py -q --tb=short
```

Additional tests should be added to prove production startup rejects missing or weak values.

## Patch Set 3 - Dependency Audit CVE Recovery

### Target files requiring approval

1. `requirements.txt`
2. Lock/constraints files, if this repository's package flow requires them.

### Intent

Resolve `pyOpenSSL 25.3.0` CVEs reported by `pip-audit`.

### Proposed change

Add an explicit production dependency floor if compatibility checks pass:

```diff
+# Explicit floor for transitive spiffe-tls dependency; fixes CVE-2026-27448 and CVE-2026-27459.
+pyOpenSSL>=26.0.0
```

Expected verification:

```powershell
python -m pip install -r requirements.txt
python -m pip_audit -r requirements.txt
python -m pytest -q --tb=short
```

## Patch Set 4 - Secret Manifest Remediation

### Target files requiring approval

1. `scripts/deploy/production-gateway-generated.yaml`
2. `.gitignore`
3. Any deploy-template file selected as the replacement source of truth.

### Intent

- Stop tracking secret-bearing generated manifests.
- Replace production deploy artifacts with templates or secret references only.
- Prevent recurrence.

### Required external action before patch

Rotate every exposed credential before relying on any environment, deployment, or test result.

### Proposed repository action after rotation

- Remove the generated secret-bearing manifest from tracked source.
- Add ignore rules for generated production manifests.
- Add a redacted template that uses `secretRef` placeholders only.

Exact patch depends on owner's chosen history/secret remediation policy.

## Patch Set 5 - Commercial Durability Decision

### Target files requiring approval if launch scope includes paid commerce

1. `src/integrations/shopify_billing.py`
2. `src/integrations/stripe_usage.py`
3. `src/integrations/stripe_packs.py`
4. `src/integrations/stripe_webhooks.py`
5. `src/integrations/action_executor.py`

### Intent

Replace in-memory commercial state with Cosmos/Redis-backed durable stores, or explicitly disable those features for launch.

### Decision required

Owner must choose one:

1. Include paid commerce at launch and implement durable persistence.
2. Launch without these paid/commercial flows and feature-gate the endpoints.
3. Accept documented operational risk for a limited beta only.

## Patch Set 6 - GroundTruth-KB Governance Adoption Enforcement

### Target files

1. `.gitignore`
2. `.claude/skills/release-candidate-gate/SKILL.md`
3. `memory/work_list.md`
4. `tests/scripts/test_groundtruth_governance_adoption.py`
5. `scripts/release_candidate_gate.py`

### Intent

- Make Agent Red's GroundTruth-KB adopter assets observable to source control instead of only locally present.
- Add a local release-candidate skill that requires DA/MemBase evidence and Python 3.12 proof.
- Move unimplemented GT-KB candidate skill/doctor work items to the top of the outstanding queue.
- Add a regression test that fails if adopter config, transport gate plugin config, hooks, rules, skills, release workflow lanes, or queue ordering drift.
- Include that regression test in the non-deploying release-candidate gate.

### Applied changes

- `.gitignore` now re-includes `.claude/hooks/*.py`, `.claude/rules/*.md`, and `.claude/skills/*` skill documents/reference files/scripts.
- Added `.claude/skills/release-candidate-gate/SKILL.md`.
- Added `GTKB-GOV-001`, `GTKB-GOV-002`, and `GTKB-GOV-003` to the top of `memory/work_list.md`.
- Added `tests/scripts/test_groundtruth_governance_adoption.py`.
- Added the governance adoption test to `scripts/release_candidate_gate.py`.

### Verification

```powershell
python -m pytest tests\scripts\test_groundtruth_governance_adoption.py -q --tb=short
```

Result: 8 passed locally under Python 3.14.

```powershell
python scripts\release_candidate_gate.py --skip-frontend
```

Result: PASS locally under Python 3.14. The gate ran Ruff E/F, import-cycle detection, Bandit, pip-audit, and 146 targeted tests including `tests/scripts/test_groundtruth_governance_adoption.py`.
