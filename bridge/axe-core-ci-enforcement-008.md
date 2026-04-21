# NO-GO: WI-3166 axe-core WCAG 2.1 AA CI Enforcement Verification

## Verdict

NO-GO.

The implementation cannot be verified because the enforced accessibility target
fails on all 9 Provider Console pages. The harness does collect and execute the
approved pages, and the failures occur at the axe assertion, which means the
route guards are not merely scanning the login gate or shell. The current
rendered pages contain critical and serious axe violations, so enabling this
workflow would immediately create a red CI gate.

## Findings

### 1. Blocking: the accessibility enforcement target fails 9 of 9 pages

Claim:

The implemented CI target reaches axe-core and fails every scanned page with at
least one critical or serious violation.

Evidence:

- `.github/workflows/accessibility.yml:72` defines the accessibility test step.
- `.github/workflows/accessibility.yml:74` runs
  `python -m pytest tests/accessibility/`.
- `tests/accessibility/test_axe_ci.py:27` through
  `tests/accessibility/test_axe_ci.py:36` define the 9 Provider Console routes.
- `tests/accessibility/test_axe_ci.py:59` navigates with the approved helper.
- `tests/accessibility/test_axe_ci.py:63` through
  `tests/accessibility/test_axe_ci.py:65` perform the route-specific rendered
  page guards.
- `tests/accessibility/test_axe_ci.py:71` calls
  `assert_no_critical_a11y_violations(a11y_page)`.
- Command run:
  `python -m pytest tests/accessibility/ -q --tb=short --timeout=120`
- Command result: exit code 1, `9 failed in 22.98s`.

Observed blocking violations from the command output:

| Page | Blocking axe result |
|------|---------------------|
| Dashboard | serious `aria-progressbar-name`, 5 affected elements |
| Configuration | critical `button-name`, critical `label`, serious `aria-input-field-name`, serious `color-contrast` |
| Inbox | critical `button-name`, serious `scrollable-region-focusable` |
| Analytics | serious `aria-progressbar-name`, 5 affected elements |
| Team | critical `select-name`, serious `color-contrast` |
| Knowledge Base | critical `button-name`, serious `color-contrast` |
| Integrations | serious `color-contrast` |
| Billing | serious `color-contrast` |
| Widget | critical `label`, serious `aria-input-field-name`, serious `color-contrast` |

Impact:

- The post-implementation report's "awaiting verification" state cannot be
  advanced to VERIFIED.
- The workflow objective is to fail builds on critical and serious WCAG 2.1 AA
  violations. The implemented tests demonstrate that the current UI violates
  that gate today.
- Merging this workflow without first resolving or explicitly baselining the
  failures would make affected PRs fail immediately.

Required action:

- Fix the underlying critical and serious axe violations surfaced by
  `python -m pytest tests/accessibility/ -q --tb=short --timeout=120`, then
  rerun the target until all 9 pages pass.
- If Prime wants to land CI enforcement before remediation, submit a revised
  proposal that explicitly scopes a temporary baseline or allowlist strategy,
  including owner acceptance of the reduced enforcement value, violation IDs,
  selectors, expiry criteria, and a removal plan. Without that explicit
  decision, the approved objective remains "critical and serious violations fail
  the build."

### 2. High: the new accessibility module is not ruff-clean under repo config

Claim:

The new accessibility test module has an import-order finding under the repo's
configured ruff rules.

Evidence:

- `pyproject.toml:62` through `pyproject.toml:63` include `I` in the selected
  ruff rules.
- `tests/accessibility/test_axe_ci.py:12` through
  `tests/accessibility/test_axe_ci.py:19` contain the import block.
- Command run:
  `python -m ruff check tests/accessibility/`
- Command result: exit code 1 with `I001 Import block is un-sorted or
  un-formatted` at `tests/accessibility/test_axe_ci.py:12`.
- Control command:
  `python -m ruff format --check tests/accessibility/`
- Control result: exit code 0, `3 files already formatted`.

Impact:

- Any future lint target that includes `tests/accessibility/` will fail on the
  new module.
- This is smaller than the axe failures, but it is still new-code debt in the
  implementation under verification.

Required action:

- Organize the imports in `tests/accessibility/test_axe_ci.py` so
  `python -m ruff check tests/accessibility/` passes.

## Positive Verification

These checks passed and should be preserved in the revision:

- `python -m py_compile tests/accessibility/conftest.py tests/accessibility/test_axe_ci.py`
  returned exit code 0.
- `python -m pytest tests/accessibility/ --collect-only -q --tb=short`
  collected all 9 expected tests.
- The dependency filter in `.github/workflows/accessibility.yml:64` matches the
  approved `grep -v -E '^(agntcy-app-sdk|locust|^-r )'` pattern.
- Filtering `requirements-test.txt` with that pattern leaves
  `pytest-playwright>=0.5.0` and `axe-playwright-python>=0.1.4`, and does not
  leave the recursive `-r requirements.txt` include.
- The route guards in `tests/accessibility/test_axe_ci.py:27` through
  `tests/accessibility/test_axe_ci.py:36` match current rendered source markers:
  Dashboard, Agent configuration, Search conversations..., Analytics, Team
  members, Knowledge base, Integrations, Account and billing, and Widget
  configuration.
- YAML parsing of `.github/workflows/accessibility.yml` succeeded and found the
  `accessibility` job.

## Conditions For Verification

Codex can verify the next implementation report once:

1. `python -m pytest tests/accessibility/ -q --tb=short --timeout=120` passes
   all 9 pages, or a revised owner-approved baseline proposal is submitted and
   implemented.
2. `python -m ruff check tests/accessibility/` passes for the new accessibility
   module.
3. The existing approved controls remain intact: authenticated browser context,
   tenant-aware navigation, route-specific guards, fail-closed axe behavior, and
   the fixed dependency filter.

## Reviewed Evidence

- `.claude/rules/file-bridge-protocol.md`
- `bridge/INDEX.md`
- `bridge/axe-core-ci-enforcement-001.md`
- `bridge/axe-core-ci-enforcement-002.md`
- `bridge/axe-core-ci-enforcement-003.md`
- `bridge/axe-core-ci-enforcement-004.md`
- `bridge/axe-core-ci-enforcement-005.md`
- `bridge/axe-core-ci-enforcement-006.md`
- `bridge/axe-core-ci-enforcement-007.md`
- `tests/accessibility/__init__.py`
- `tests/accessibility/conftest.py`
- `tests/accessibility/test_axe_ci.py`
- `.github/workflows/accessibility.yml`
- `tests/e2e/a11y_helpers.py`
- `tests/e2e_mock/conftest.py`
- `requirements-test.txt`
- `pyproject.toml`
- `admin/standalone/pages/Dashboard.tsx`
- `admin/standalone/pages/Configuration.tsx`
- `admin/standalone/pages/Inbox.tsx`
- `admin/standalone/pages/Analytics.tsx`
- `admin/standalone/pages/Team.tsx`
- `admin/standalone/pages/KnowledgeBase.tsx`
- `admin/standalone/pages/Integrations.tsx`
- `admin/standalone/pages/Billing.tsx`
- `admin/standalone/pages/Widget.tsx`
