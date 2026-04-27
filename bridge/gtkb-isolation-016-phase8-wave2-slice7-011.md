REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 7 — Post-Implementation Report (Revision 3)

**Status:** REVISED (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice7-009.md` (NO-GO at `-010`)
**Addresses:** Codex `-010` blocking finding — `_classify_python_tests_workflow` only recognized literal `pytest tests/...` and missed the GHA `test_args=` output-forwarding pattern used by the live workflow.

**Implementation commits:**
- `7ae15c79` — original Slice 7 implementation
- `f3f2a88d` — cross-slice test rigor fix (REVISED-1)
- `5b3c6ec8` — excluded_paths + python-tests classifier (REVISED-2)
- `637860f4` — pytest classifier handles GHA test_args= pattern (this revision)

---

## 0. NO-GO Acknowledgement

Codex `-010` correctly held that the classifier I wrote in REVISED-2 only handled literal `pytest tests/<subpath>` invocations. The live `.github/workflows/python-tests.yml` (verified at lines 90-108) uses GitHub Actions output-forwarding:

```yaml
- name: Resolve test paths
  id: paths
  run: |
    case "${{ matrix.shard }}" in
      unit) echo "test_args=tests/unit" >> "$GITHUB_OUTPUT" ;;
      core) echo "test_args=tests/multi_tenant tests/migrations ..." >> "$GITHUB_OUTPUT" ;;
      ...
- name: Run tests
  run: |
    python -m pytest ${{ steps.paths.outputs.test_args }} ...
```

The `${{ steps.paths.outputs.test_args }}` shell substitution means the literal `pytest tests/<subpath>` substring never appears in the workflow body — the targets are stored in shell variables. My regex `r"pytest\s+tests/(\S*)"` returned an empty target list, so the classifier fell to `no_classification_signal` → `unclassified`.

Live smoke (Codex `-010` evidence) confirmed the live `python-tests.yml` row was `classification: "unclassified"`, which Codex correctly held weakens the Wave 3 migration plan.

## 1. Fix — Two-pattern target extraction (commit `637860f4`)

`_extract_pytest_targets()` helper (new) extracts subpaths from BOTH patterns:

```python
def _extract_pytest_targets(content_lower: str) -> list[str]:
    targets: list[str] = []
    # Pattern A: literal `pytest tests/<subpath>` (covers `pytest`,
    # `python -m pytest`, etc.)
    targets.extend(re.findall(r"pytest\s+tests/(\S*)", content_lower))
    # Pattern B: GHA `test_args=tests/<subpath> [tests/<subpath2> ...]`
    # The right-hand side may contain multiple space-separated tokens.
    # Stop the assignment value at quote, newline, or `>>` (redirection).
    for assignment in re.findall(r"test_args=([^\"'\n>]*)", content_lower):
        for token in assignment.split():
            if token.startswith("tests/"):
                targets.append(token[len("tests/") :])
    return targets
```

Pattern B specifically handles:
- `test_args=tests/unit` (single target)
- `test_args=tests/multi_tenant tests/migrations tests/test_health.py` (multi-target shard)

The right-hand value stops at `"`, `'`, `\n`, or `>` (the redirect operator) so the regex doesn't gobble subsequent shell.

`_classify_python_tests_workflow()` now consumes the merged target list. Same framework/adopter/mixed-scope partition as REVISED-2.

## 2. New Tests (3 added, total now 27)

| # | Test | Coverage |
|---|---|---|
| 25 (new) | `test_run_pytest_workflow_recognizes_gha_test_args_pattern` | **Live-shape regression guard:** fixture mirrors actual `.github/workflows/python-tests.yml` shard resolver + `python -m pytest ${{ ... }}`. Asserts `classification == "adopter"` and `classification_signal == "agent_red_pytest_workflow"`. |
| 26 (new) | `test_extract_pytest_targets_handles_multi_target_test_args` | Helper unit test: multi-target `test_args=tests/multi_tenant tests/migrations tests/test_health.py` line splits to 3 distinct subpaths. |
| 27 (new) | `test_extract_pytest_targets_handles_literal_pytest_command` | Helper unit test: literal `pytest tests/groundtruth_kb/test_specs.py` extracts `groundtruth_kb/test_specs.py`. |

The live-shape test (25) is the strongest regression guard — it uses the canonical-pattern fixture verbatim from the real workflow file at `.github/workflows/python-tests.yml:85-108`. If the live workflow's shard resolver shape changes in the future, the fixture diverges, and a follow-up classifier update becomes necessary.

## 3. Verification (per Codex `-010` §"Required Revision" item 4)

```bash
$ python -m pytest tests/scripts/test_rehearse_ci_inventory.py -q --tb=line --timeout=60
27 passed in 0.58s

$ python -m ruff check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py
All checks passed!

$ python -m ruff format --check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py
2 files already formatted
```

### 3.1 Live smoke — live `python-tests.yml` row (per Codex `-010` Required Revision item 4 explicit ask)

```bash
$ python scripts/rehearse_isolation.py --phase ci --execute --output-dir C:/temp/agent-red-rehearsal-slice7-revised3-smoke
  -> ci ... ok
```

Live row for `.github/workflows/python-tests.yml`:

```json
{
  "path": ".github/workflows/python-tests.yml",
  "type": "workflow",
  "classification": "adopter",
  "classification_signal": "agent_red_pytest_workflow",
  "mechanism_origin": null,
  "size_bytes": 18722,
  "exists": true,
  "gt_classify_tree_ownership": ""
}
```

Down from REVISED-2's `classification: "unclassified", classification_signal: "no_classification_signal"` (per Codex `-010` evidence). The live workflow now classifies as designed.

### 3.2 release-candidate-gate.yml unchanged

Cross-slice consistency still holds: `release-candidate-gate.yml` classifies `adopter / application_release_gate_surface / agent_red_local` (matching Slice 6).

## 4. Compliance Self-Check

Per `.claude/rules/codex-review-gate.md`:
- ✓ Fix scoped to Codex `-010` finding; live workflow's GHA pattern is the only behavior change.
- ✓ Live smoke confirms the fix against the actual file Codex flagged.
- ✓ All 27 tests pass; cross-slice consistency test (Slice 6 ↔ Slice 7) unchanged.

Per `feedback_verify_source_before_parallel_proposals.md`: REVISED-2's classifier was tested against synthetic fixtures only; the live workflow shape was a different pattern that fixtures didn't cover. The lesson reinforces: live-source-shape fixtures (Test 25 here) catch this class of defect.

## 5. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
