REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 7 — Post-Implementation Report (Revision 2)

**Status:** REVISED (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice7-007.md` (NO-GO at `-008`)
**Addresses:** Codex `-008` blocking findings — implementation didn't honor `manifest['excluded_paths']`; `test_run_pytest_workflow_classifies_by_pytest_target` was missing.

**Implementation commits:**
- `7ae15c79` — original Slice 7 implementation
- `f3f2a88d` — cross-slice test rigor fix (REVISED-1)
- `5b3c6ec8` — excluded_paths consumption + python-tests classifier (this revision)

---

## 0. NO-GO Acknowledgement

Codex `-008` correctly held two contract gaps against my own approved proposal:

1. **`manifest['excluded_paths']` not consumed.** Proposal `-001` §6 listed common-contract compliance: "manifest validation precondition: lane assumes validated manifest (consumes `excluded_paths` only)". My implementation accepted `manifest` then never read it. The promised `test_run_excluded_paths_skip_workflow_files_under_excluded_top_level` was also absent.
2. **`python-tests.yml`-specific classifier missing.** Proposal `-001` §3 specified `pytest tests/groundtruth_kb` → framework, `pytest tests/<other>` → adopter, both → unclassified. Live `python-tests.yml` happened to classify as adopter via the general `src/` content-marker fallback in the smoke output, but the spec-required behavior wasn't actually implemented.

Both gaps fixed in commit `5b3c6ec8`. No proposal revision needed — the existing `-001`/`-003` proposal text is now correctly implemented.

## 1. Fix 1 — `manifest['excluded_paths']` consumption

`_is_path_excluded_by_manifest()` helper supports two match modes per the common-contract semantics observed in `_inventory.py`:

- **Top-level dir match**: `excluded_paths: [".github"]` skips all `.github/workflows/*.yml` and `.github/dependabot.yml`.
- **Full-path match**: `excluded_paths: ["sonar-project.properties"]` skips that specific config probe.

`_probe_workflows` and `_probe_ci_configs` accept `excluded_top` + `excluded_full` parameters; the `run()` entry point derives both from `manifest['excluded_paths']` and threads them through. Excluded paths are skipped before `stat()` / `read_text()` (no leakage into the inventory).

## 2. Fix 2 — `_classify_python_tests_workflow()` per proposal §3

```python
def _classify_python_tests_workflow(content: str) -> tuple[str, str, str | None]:
    pytest_calls = re.findall(r"pytest\s+tests/(\S*)", content.lower())
    framework_calls = [c for c in pytest_calls if c.startswith("groundtruth_kb")]
    adopter_calls = [c for c in pytest_calls if not c.startswith("groundtruth_kb")]
    if framework_calls and adopter_calls:
        return ("unclassified", "mixed_scope_pytest_owner_decision_required", None)
    if framework_calls:
        return ("framework", "framework_pytest_workflow", None)
    if adopter_calls:
        return ("adopter", "agent_red_pytest_workflow", None)
    return ("unclassified", "no_classification_signal", None)
```

Regex-based subpath capture distinguishes `pytest tests/groundtruth_kb/` from `pytest tests/transport/` cleanly. A sole `pytest tests/groundtruth_kb/` invocation no longer spuriously triggers mixed-scope (which it would if I'd just substring-checked `"pytest tests/"`).

`_classify_workflow()` dispatches to the python-tests-specific path before the general filename rules / content scan.

## 3. New Tests (5)

| # | Test | Coverage |
|---|---|---|
| 20 (new) | `test_run_excluded_paths_skip_workflow_files_under_excluded_top_level` | §1 top-level dir match: `.github` excluded → no workflows in inventory + no `.github/dependabot.yml` config |
| 21 (new) | `test_run_excluded_paths_full_path_match_skips_specific_config` | §1 full-path match: `sonar-project.properties` excluded → that single config skipped |
| 22 (new) | `test_run_pytest_workflow_classifies_by_pytest_target_adopter` | §2 — `pytest tests/` only → `agent_red_pytest_workflow` |
| 23 (new) | `test_run_pytest_workflow_classifies_by_pytest_target_framework` | §2 — `pytest tests/groundtruth_kb/` only → `framework_pytest_workflow` |
| 24 (new) | `test_run_pytest_workflow_classifies_no_pytest_command_as_unclassified` | §2 — placeholder body → `no_classification_signal` |

Test 23 specifically guards against the regex bug I caught during implementation: a workflow with only `pytest tests/groundtruth_kb/` was initially classified as `unclassified` (mixed-scope) because `"pytest tests/"` is a substring. The regex extraction with `pytest_calls` + prefix-check on `groundtruth_kb` resolves it.

## 4. Verification (per Codex `-008` §"Required Revision" item 4)

```bash
$ python -m pytest tests/scripts/test_rehearse_ci_inventory.py -q --tb=line --timeout=60
24 passed in 0.59s

$ python -m pytest tests/scripts/test_rehearse_*.py -q --tb=line --timeout=120
(passed; baseline preserved)

$ python -m ruff check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py
All checks passed!

$ python -m ruff format --check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py
2 files already formatted
```

### 4.1 Live smoke (per Codex `-008` evidence pattern)

```bash
$ python scripts/rehearse_isolation.py --phase ci --execute --output-dir C:/temp/agent-red-rehearsal-slice7-revised2-smoke
  -> ci ... ok
```

`release-candidate-gate.yml` still classifies `adopter` / `application_release_gate_surface` / `agent_red_local` (unchanged from REVISED-1).

## 5. Compliance Self-Check

Per `.claude/rules/codex-review-gate.md`:
- ✓ Fix scoped to the two NO-GO findings; no scope creep.
- ✓ Did not modify cross-slice consistency test (REVISED-1 already correct).
- ✓ Live smoke run before declaring complete.

Per `feedback_verify_source_before_parallel_proposals.md`: I should have caught both gaps when implementing — the proposal said `excluded_paths` consumption and the test name was explicit. Same source-verification lesson keeps recurring; will continue to apply.

## 6. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
