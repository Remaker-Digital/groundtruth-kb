NO-GO

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 4 Post-Implementation

Status: NO-GO

## Claim

Slice 4 is not verified yet. The implementation satisfies the core functional GO conditions around the `classify-tree` entrypoint, bounded smoke coverage, manifest-derived namespace, and warning treatment, but two blocking verification issues remain.

## Evidence

Targeted pytest verification passes:

```text
PYTHONIOENCODING=utf-8 python -m pytest tests/scripts/test_rehearse_path_rewrite.py tests/scripts/test_rehearse_isolation.py tests/scripts/test_rehearse_inventory.py tests/scripts/test_rehearse_common_validation.py -q --tb=short
112 passed in 2.05s
```

Functional checks observed in code:

- `_build_classify_tree_command()` uses `sys.executable`, `-c`, and `from groundtruth_kb.cli import main; main()` rather than `python -m groundtruth_kb.cli` (`scripts/rehearse/_path_rewrite.py:56`).
- `run()` checks `classification_path.exists()` after a zero-exit subprocess before parsing JSON (`scripts/rehearse/_path_rewrite.py:234`).
- `_derive_target_namespace()` derives `target_root.relative_to(legacy_root)` from the manifest and normalizes separators (`scripts/rehearse/_path_rewrite.py:89`).
- `legacy-exception`, `owner_decision_pending`, and unknown ownership labels produce warnings/lists without changing the successful lane status (`scripts/rehearse/_path_rewrite.py:276`, `:283`, `:290`).

## Blocking Findings

### F1 - Blocking: focused quality gates fail

The implementation report claims the pre-commit quality gates are expected to pass, but focused checks on the new/touched Python files currently fail:

```text
python -m ruff check scripts/rehearse/_path_rewrite.py tests/scripts/test_rehearse_path_rewrite.py tests/scripts/test_rehearse_isolation.py
```

Result:

```text
I001 scripts\rehearse\_path_rewrite.py:22 Import block is un-sorted or un-formatted
I001 tests\scripts\test_rehearse_isolation.py:21 Import block is un-sorted or un-formatted
I001 tests\scripts\test_rehearse_isolation.py:217 Import block is un-sorted or un-formatted
I001 tests\scripts\test_rehearse_path_rewrite.py:26 Import block is un-sorted or un-formatted
F401 tests\scripts\test_rehearse_path_rewrite.py:27 `rehearse._common.LEGACY_ROOT` imported but unused
```

The paired format gate also fails:

```text
python -m ruff format --check scripts/rehearse/_path_rewrite.py tests/scripts/test_rehearse_path_rewrite.py tests/scripts/test_rehearse_isolation.py
```

Result:

```text
Would reformat: scripts\rehearse\_path_rewrite.py
Would reformat: tests\scripts\test_rehearse_isolation.py
Would reformat: tests\scripts\test_rehearse_path_rewrite.py
3 files would be reformatted
```

This blocks verification because the local repo-native quality gates do not pass for the files in the slice.

### F2 - Blocking: approved output contract omits `result.json`

The approved Slice 4 proposal retained the common output layout and explicitly required `{output_dir}/path_rewrite/result.json` as the standard sub-script result artifact (`gtkb-isolation-016-phase8-wave2-slice4-003.md:168`, `:169`, `:170`, `:171`). The umbrella Wave 2 common contract also says each sub-script writes `result.json` under its lane output directory (`gtkb-isolation-016-phase8-wave2-implementation-001.md:109`, `:111`, `:112`, `:113`).

The implementation writes `path_rewrite.json` and `git_filter_args.txt`, then returns the result dict with `output_files` containing only `classification.json`, `path_rewrite.json`, and `git_filter_args.txt` (`scripts/rehearse/_path_rewrite.py:328`, `:333`, `:338`, `:340`, `:341`, `:342`, `:343`). It does not write `result.json` or include it in `output_files`.

This blocks verification because the implemented lane output is narrower than the approved contract and would leave the operator without the per-lane structured result artifact described by the proposal.

## Risk / Impact

- F1 prevents confidence that the slice would pass the expected quality gates at commit time.
- F2 creates a contract drift between the approved lane design and the operator-facing artifacts emitted by the implementation.

## Recommended Action

1. Run `ruff check --fix` and `ruff format` or make equivalent manual edits for the new/touched Python files, then rerun the focused `ruff check` and `ruff format --check` commands above.
2. Write `{output_dir}/path_rewrite/result.json` for non-dry-run executions after composing the final result dict, include it in `output_files`, and add a test asserting the file exists and contains the returned structured result.
3. Rerun the 112-test pytest target and the focused ruff gates.

## Decision Needed From Owner

None.
