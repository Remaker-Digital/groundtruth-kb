# VERIFIED: WI-3166 axe-core WCAG 2.1 AA CI Enforcement Verification

## Verdict

VERIFIED.

Revision `013` records the owner decision accepting the count-based baseline
tradeoff for WI-3166. With that owner decision treated as the controlling
decision record for this bridge item, the implemented accessibility workflow
and test module satisfy the verification conditions.

## Rationale

The implemented target runs the 9 Provider Console accessibility tests, keeps
the previously approved auth, tenant, page guard, and dependency-filter
controls, and passes the repo-native validation commands used for this scope.
The known-violations baseline now enforces the owner-accepted count-based
semantics: new critical/serious rule IDs fail, count increases fail, and stale
baseline rules fail when a baselined rule no longer appears.

I did not find a separate repository artifact for the owner decision beyond
`bridge/axe-core-ci-enforcement-013.md` and the baseline file header pointing
back to it. Because the file bridge is the authoritative coordination channel
for this item, I treated the explicit owner decision recorded in `013` as
sufficient for this verification.

## Findings

### 1. Verification target passes

Claim:

The accessibility target runs all 9 intended Provider Console scans and passes.

Evidence:

- `tests/accessibility/test_axe_ci.py:31` through
  `tests/accessibility/test_axe_ci.py:40` define the 9 approved Provider
  Console routes.
- `tests/accessibility/test_axe_ci.py:63` navigates each route with the shared
  accessibility helper.
- `tests/accessibility/test_axe_ci.py:65` through
  `tests/accessibility/test_axe_ci.py:72` keep route-specific rendered-page
  guards before axe runs.
- Command run:
  `python -m pytest tests/accessibility/ --collect-only -q --tb=short`
- Command result: exit code 0, 9 tests collected.
- Command run:
  `python -m pytest tests/accessibility/ -q --tb=short --timeout=120`
- Command result: exit code 0, `9 passed in 16.04s`.

Impact:

- The post-implementation accessibility gate is executable and green in the
  local verification environment.

Required action:

- None for verification.

### 2. Approved harness controls remain intact

Claim:

The implementation retains the controls from the original GO and later
verification conditions.

Evidence:

- `tests/accessibility/conftest.py:79` through
  `tests/accessibility/conftest.py:87` creates the browser context with a
  1280 x 800 viewport and pre-injects `sessionStorage.agentred_api_key`.
- `tests/accessibility/conftest.py:106` through
  `tests/accessibility/conftest.py:111` appends the mock tenant parameter
  during navigation.
- `tests/accessibility/test_axe_ci.py:18` imports `Axe` at module import time,
  preserving fail-closed behavior if `axe-playwright-python` is unavailable.
- `.github/workflows/accessibility.yml:64` keeps the approved dependency
  filter: `grep -v -E '^(agntcy-app-sdk|locust|^-r )' requirements-test.txt`.
- Command result for that filter left `pytest-playwright>=0.5.0` and
  `axe-playwright-python>=0.1.4`, and did not leave the recursive
  `-r requirements.txt` include.

Impact:

- The test harness is still scanning authenticated tenant pages rather than the
  login gate or shell, and CI still installs the intended accessibility
  dependencies without reintroducing the excluded recursive requirements path.

Required action:

- None for verification.

### 3. Count-based baseline enforcement matches the recorded owner decision

Claim:

The baseline does not implement selector-level tracking, but it now matches the
count-based approach accepted in the latest owner decision record.

Evidence:

- `bridge/axe-core-ci-enforcement-013.md:7` through
  `bridge/axe-core-ci-enforcement-013.md:10` record that Mike accepted the
  count-based baseline approach on 2026-04-12.
- `bridge/axe-core-ci-enforcement-013.md:20` through
  `bridge/axe-core-ci-enforcement-013.md:28` explicitly accepts the remaining
  same-rule/same-count swap risk instead of selector-level tracking.
- `bridge/axe-core-ci-enforcement-013.md:30` through
  `bridge/axe-core-ci-enforcement-013.md:35` define the expiry/removal
  criteria.
- `tests/accessibility/known_violations.py:10` through
  `tests/accessibility/known_violations.py:15` records the same owner
  acceptance and expiry criteria in the baseline file.
- `tests/accessibility/known_violations.py:26` through
  `tests/accessibility/known_violations.py:62` stores the page/rule/count
  baseline.
- `tests/accessibility/test_axe_ci.py:89` through
  `tests/accessibility/test_axe_ci.py:99` fail on unknown critical/serious rule
  IDs and count increases.
- `tests/accessibility/test_axe_ci.py:110` through
  `tests/accessibility/test_axe_ci.py:115` fail stale baseline entries when a
  baselined rule no longer fires.

Impact:

- The prior selector-level concern is not technically eliminated; it is an
  explicitly accepted owner tradeoff for WI-3166. Under that accepted scope, the
  implementation is sufficient to verify.

Required action:

- Do not expand the baseline or raise counts without another reviewed bridge
  revision.
- Remove all baseline entries before the next production release, per the
  expiry criterion recorded in `bridge/axe-core-ci-enforcement-013.md`.

### 4. Static checks pass

Claim:

The new accessibility module is clean under the local Python checks used for
this verification.

Evidence:

- Command run:
  `python -m py_compile tests/accessibility/conftest.py tests/accessibility/test_axe_ci.py tests/accessibility/known_violations.py`
- Command result: exit code 0.
- Command run:
  `python -m ruff check tests/accessibility/`
- Command result: exit code 0, `All checks passed!`
- Command run:
  `python -m ruff format --check tests/accessibility/`
- Command result: exit code 0, `4 files already formatted`.

Impact:

- The prior ruff blocker remains resolved.

Required action:

- None for verification.

## Conditions

Verification is granted under these continuing conditions:

1. The count-based baseline remains an owner-accepted temporary baseline, not a
   permanent accessibility exemption.
2. Baseline counts must not be increased without a new reviewed bridge
   revision.
3. All baseline entries must be removed before the next production release, as
   recorded in `bridge/axe-core-ci-enforcement-013.md`.

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
- `bridge/axe-core-ci-enforcement-008.md`
- `bridge/axe-core-ci-enforcement-009.md`
- `bridge/axe-core-ci-enforcement-010.md`
- `bridge/axe-core-ci-enforcement-011.md`
- `bridge/axe-core-ci-enforcement-012.md`
- `bridge/axe-core-ci-enforcement-013.md`
- `tests/accessibility/__init__.py`
- `tests/accessibility/conftest.py`
- `tests/accessibility/test_axe_ci.py`
- `tests/accessibility/known_violations.py`
- `.github/workflows/accessibility.yml`
- `requirements-test.txt`
- `pyproject.toml`
