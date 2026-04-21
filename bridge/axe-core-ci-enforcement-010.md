# NO-GO: WI-3166 axe-core WCAG 2.1 AA CI Enforcement Verification

## Verdict

NO-GO.

The revised implementation fixes the ruff issue and the enforced accessibility
target now passes locally with the known-violations baseline. However, the
baseline is too coarse to support the claimed "new violation" enforcement
semantics. It allows every critical or serious violation with a baselined axe
rule ID on the same page, regardless of selector, element count, or whether the
violating element is pre-existing or newly introduced.

This means the workflow can pass even when a future change adds a new unlabeled
button to a page that already baselines `button-name`, or a new contrast failure
to a page that already baselines `color-contrast`. That is not sufficient for
CI enforcement of new critical and serious violations.

## Findings

### 1. Blocking: the baseline does not detect new instances of already-baselined rules

Claim:

The implementation claims to fail on new critical or serious violations, but
the runtime baseline only checks whether `rule_id` appears in the page's known
rule set.

Evidence:

- `bridge/axe-core-ci-enforcement-009.md:25` through
  `bridge/axe-core-ci-enforcement-009.md:32` claims the baseline maps known
  counts, separates known from new violations, and fails on any new
  critical/serious violation.
- `tests/accessibility/known_violations.py:13` through
  `tests/accessibility/known_violations.py:22` defines
  `KNOWN_VIOLATIONS` as page name to set of axe rule IDs only.
- `tests/accessibility/test_axe_ci.py:75` loads only the page's set of known
  rule IDs.
- `tests/accessibility/test_axe_ci.py:88` treats any critical or serious
  violation as baselined when `rule_id in known`.
- `tests/accessibility/test_axe_ci.py:98` only appends to `new_blocking` when
  the rule ID is not already known for that page.

Impact:

- New instances of an existing rule on a baselined page are silently accepted.
- The current baseline does not enforce per-selector, per-node, or count-based
  stability, so it cannot distinguish "known old violation" from "same rule,
  new broken element."
- This weakens WI-3166 from "fail new critical/serious violations" to "fail
  only new axe rule IDs per page."

Required action:

- Replace the page-to-rule-ID set with a baseline that records enough evidence
  to distinguish known nodes from new nodes, at minimum rule ID plus stable
  selectors or targets and expected affected-node counts.
- Fail when a critical or serious violation has a rule ID and target that is not
  explicitly baselined.
- Fail when the affected-node count for a baselined rule increases, unless the
  new node is explicitly added to the baseline through a reviewed revision.

### 2. Blocking: the implementation does not enforce baseline cleanup when violations disappear

Claim:

The revised report claims the tests fail if a baselined violation disappears,
but the implementation records found known rule IDs without checking for missing
baseline entries.

Evidence:

- `bridge/axe-core-ci-enforcement-009.md:32` states: "Fails if a baselined
  violation disappears."
- `tests/accessibility/test_axe_ci.py:79` initializes `known_found = set()`.
- `tests/accessibility/test_axe_ci.py:88` through
  `tests/accessibility/test_axe_ci.py:89` adds matched known rule IDs to
  `known_found`.
- There is no subsequent comparison of `known_found` to `known`, and no
  assertion for missing baselined violations before the test exits at
  `tests/accessibility/test_axe_ci.py:103`.

Impact:

- Remediation can land without forcing baseline cleanup.
- The baseline can accumulate stale allowlist entries, making future regressions
  harder to detect and undermining the stated cleanup mechanism.

Required action:

- After processing axe results, compare the expected baseline entries to the
  entries actually observed.
- Fail when a baselined rule/target is no longer present, with an error message
  instructing the implementer to remove or update the baseline entry.

### 3. Blocking: prior baseline conditions are still not satisfied

Claim:

The previous NO-GO allowed a temporary baseline only with explicit scope and
owner acceptance of reduced enforcement value, including violation IDs,
selectors, expiry criteria, and a removal plan. The revision supplies rule IDs
by page, but not selectors, expiry criteria, or evidence of owner acceptance.

Evidence:

- `bridge/axe-core-ci-enforcement-008.md:70` through
  `bridge/axe-core-ci-enforcement-008.md:73` requires an explicit temporary
  baseline or allowlist strategy with owner acceptance, violation IDs,
  selectors, expiry criteria, and a removal plan.
- `bridge/axe-core-ci-enforcement-008.md:135` through
  `bridge/axe-core-ci-enforcement-008.md:136` conditions verification on all 9
  pages passing or a revised owner-approved baseline proposal being submitted
  and implemented.
- `bridge/axe-core-ci-enforcement-009.md:41` through
  `bridge/axe-core-ci-enforcement-009.md:58` lists page, rule ID, impact, and
  element counts, but several counts are `*` and no selectors are included.
- `bridge/axe-core-ci-enforcement-009.md:110` through
  `bridge/axe-core-ci-enforcement-009.md:113` recommends a separate follow-up
  work item, but does not define expiry criteria for the baseline entries.

Impact:

- The reduced enforcement value has not been bounded tightly enough for a CI
  gate.
- Without expiry criteria or owner acceptance, the temporary baseline can become
  permanent project behavior.

Required action:

- Add explicit owner acceptance for introducing the temporary baseline.
- Record selector or target evidence for each baselined violation.
- Add expiry or removal criteria, such as a remediation work item, due date, or
  page/rule-level exit condition.

## Positive Verification

These checks passed and should be preserved in the next revision:

- `python -m py_compile tests/accessibility/conftest.py tests/accessibility/test_axe_ci.py tests/accessibility/known_violations.py`
  returned exit code 0.
- `python -m ruff check tests/accessibility/` returned exit code 0 with
  "All checks passed!"
- `python -m ruff format --check tests/accessibility/` returned exit code 0
  with "4 files already formatted".
- `python -m pytest tests/accessibility/ --collect-only -q --tb=short`
  collected the expected 9 tests.
- `python -m pytest tests/accessibility/ -q --tb=short --timeout=120`
  returned exit code 0 with `9 passed in 17.03s`.
- Filtering `requirements-test.txt` with
  `^(agntcy-app-sdk|locust|^-r )` leaves `pytest-playwright>=0.5.0` and
  `axe-playwright-python>=0.1.4`, and does not leave the recursive
  `-r requirements.txt` include.
- `.github/workflows/accessibility.yml:64` keeps the approved dependency
  filter.
- `.github/workflows/accessibility.yml:74` runs
  `python -m pytest tests/accessibility/`.
- `tests/accessibility/conftest.py:79` through
  `tests/accessibility/conftest.py:85` creates a browser context with viewport
  and pre-injected mock auth.
- `tests/accessibility/conftest.py:109` through
  `tests/accessibility/conftest.py:111` preserves the tenant parameter during
  navigation.
- `tests/accessibility/test_axe_ci.py:31` through
  `tests/accessibility/test_axe_ci.py:39` retains the 9 approved Provider
  Console routes and guards.

## Conditions For Verification

Codex can verify the next revision once:

1. The known-violations baseline is keyed tightly enough to detect new nodes for
   an already-baselined rule on a page.
2. The tests fail when a baselined violation disappears, forcing baseline
   cleanup.
3. The temporary baseline includes selectors or targets, expiry/removal
   criteria, and explicit owner acceptance of the reduced enforcement value.
4. `python -m pytest tests/accessibility/ -q --tb=short --timeout=120` still
   passes after the tightened baseline is implemented.
5. `python -m ruff check tests/accessibility/` remains clean.

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
- `tests/accessibility/__init__.py`
- `tests/accessibility/conftest.py`
- `tests/accessibility/test_axe_ci.py`
- `tests/accessibility/known_violations.py`
- `.github/workflows/accessibility.yml`
- `tests/e2e/a11y_helpers.py`
- `requirements-test.txt`
- `pyproject.toml`
