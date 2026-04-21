# NO-GO: WI-3166 axe-core WCAG 2.1 AA CI Enforcement Verification

## Verdict

NO-GO.

The revised implementation passes the local accessibility target and fixes the
stale-baseline cleanup issue. It still does not satisfy the prior baseline
tightening condition because the baseline remains keyed only by page, axe rule
ID, and maximum affected-node count. It does not record or compare axe node
targets/selectors, so it cannot prove that a currently passing build has not
replaced known violating nodes with different violating nodes under the same
rule and same count.

## Findings

### 1. Blocking: count-only baseline still cannot distinguish known nodes from new nodes

Claim:

The latest implementation detects new rule IDs and count increases, but it
does not detect new or changed violating nodes when the page/rule count remains
at or below the baseline.

Evidence:

- `bridge/axe-core-ci-enforcement-010.md:56` through
  `bridge/axe-core-ci-enforcement-010.md:62` required the baseline to record
  enough evidence to distinguish known nodes from new nodes, at minimum rule ID
  plus stable selectors or targets and expected counts.
- `bridge/axe-core-ci-enforcement-010.md:173` through
  `bridge/axe-core-ci-enforcement-010.md:178` made verification conditional on
  a baseline keyed tightly enough to detect new nodes for an already-baselined
  rule, plus selectors or targets.
- `bridge/axe-core-ci-enforcement-011.md:12` states the revision changed the
  baseline to `{page: {rule_id: max_node_count}}`.
- `tests/accessibility/known_violations.py:4` describes the same
  page-to-rule-to-count baseline shape.
- `tests/accessibility/known_violations.py:25` through
  `tests/accessibility/known_violations.py:60` stores only axe rule IDs and
  integer counts. It does not store node targets, selectors, or other stable
  node identifiers.
- `tests/accessibility/test_axe_ci.py:80` through
  `tests/accessibility/test_axe_ci.py:99` reads `impact`, `rule_id`, and
  `node_count`, then fails only for unknown rule IDs or count increases.
- Command result:
  `rg -n "target|selector|nodes|node_count|violating|html" tests/accessibility/known_violations.py tests/accessibility/test_axe_ci.py`
  found `node_count` usage, but no target or selector comparison. The only
  `nodes` usage is `len(violation.get("nodes", []))` at
  `tests/accessibility/test_axe_ci.py:83`.

Impact:

- A future change can remove one known `button-name` violation and add a new
  unlabeled button on the same page. If the count stays unchanged, the test
  passes even though a new critical violation exists.
- A future change can move a known `color-contrast` violation to a different
  element while preserving the same count. The baseline cannot tell whether the
  observed nodes are the reviewed nodes.
- This is materially better than the earlier rule-ID-only baseline, but it is
  still not the reviewed selector/target-level enforcement described in the
  prior conditions.

Required action:

- Store each baselined violation as rule ID plus stable axe target/selector
  evidence, with the expected affected-node count derived from those targets.
- Fail when a critical or serious violation includes a target not explicitly
  baselined for that page/rule.
- Keep the count-increase guard as an additional protection, not as the only
  node-level guard.

### 2. Blocking: owner acceptance is asserted, not evidenced

Claim:

The latest report still does not provide concrete evidence that Mike accepted
the reduced enforcement value of the temporary baseline.

Evidence:

- `bridge/axe-core-ci-enforcement-010.md:101` through
  `bridge/axe-core-ci-enforcement-010.md:104` required explicit owner
  acceptance of reduced enforcement value, including violation IDs, selectors,
  expiry criteria, and a removal plan.
- `bridge/axe-core-ci-enforcement-010.md:132` through
  `bridge/axe-core-ci-enforcement-010.md:134` repeated the required action to
  add explicit owner acceptance and selector/target evidence.
- `tests/accessibility/known_violations.py:10` through
  `tests/accessibility/known_violations.py:11` says "Work list pre-approval for
  WI-3166 covers baseline introduction," but no cited bridge entry or owner
  decision record is provided.
- `bridge/axe-core-ci-enforcement-011.md:12` through
  `bridge/axe-core-ci-enforcement-011.md:14` describes the claimed resolution,
  but again does not cite an owner acceptance artifact.

Impact:

- A temporary accessibility baseline materially weakens the CI gate by allowing
  known critical and serious violations to remain. That is an owner-level trade
  off, not an implementation detail Codex should infer from work-item
  pre-approval.

Required action:

- Add a cited owner decision record or bridge proposal showing Mike accepted
  the temporary baseline and its reduced enforcement value.
- Include the accepted expiry/removal criteria in the baseline file or bridge
  report.

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
  returned exit code 0 with `9 passed in 15.86s`.
- `.github/workflows/accessibility.yml:64` keeps the approved dependency
  filter:
  `grep -v -E '^(agntcy-app-sdk|locust|^-r )' requirements-test.txt > /tmp/test-deps.txt`.
- `.github/workflows/accessibility.yml:74` still runs
  `python -m pytest tests/accessibility/`.
- `tests/accessibility/conftest.py:79` through
  `tests/accessibility/conftest.py:85` keeps the viewport and mock auth
  pre-injection.
- `tests/accessibility/conftest.py:109` through
  `tests/accessibility/conftest.py:111` preserves tenant-aware navigation.
- `tests/accessibility/test_axe_ci.py:111` through
  `tests/accessibility/test_axe_ci.py:116` now enforces stale-baseline cleanup
  when a baselined rule no longer fires.

## Conditions For Verification

Codex can verify the next revision once:

1. The known-violations baseline records stable axe targets/selectors for each
   baselined page/rule and fails on unbaselined targets.
2. Count-increase and stale-baseline cleanup enforcement remain in place.
3. The temporary baseline includes a cited owner acceptance record for the
   reduced enforcement value and expiry/removal criteria.
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
- `bridge/axe-core-ci-enforcement-010.md`
- `bridge/axe-core-ci-enforcement-011.md`
- `tests/accessibility/__init__.py`
- `tests/accessibility/conftest.py`
- `tests/accessibility/test_axe_ci.py`
- `tests/accessibility/known_violations.py`
- `.github/workflows/accessibility.yml`
- `requirements-test.txt`
- `pyproject.toml`
