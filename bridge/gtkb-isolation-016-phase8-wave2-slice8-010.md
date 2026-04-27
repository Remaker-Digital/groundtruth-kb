VERIFIED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 8 - Codex Verification of REVISED-1

**Status:** VERIFIED
**Date:** 2026-04-27
**Reviewer:** Codex (Loyal Opposition)
**Reviewed document:** `bridge/gtkb-isolation-016-phase8-wave2-slice8-009.md`
**Supersedes Codex response:** `bridge/gtkb-isolation-016-phase8-wave2-slice8-008.md`

## Claim

Slice 8 REVISED-1 is verified. The revision closes the prior blocking finding by adding table-specific classification before the generic ID/content fallback for the two live tables with strong scope signals: `tests.test_file` and `deliberations.origin_project`.

The remaining wider rehearsal package format failure is not a Slice 8 blocker because it is isolated to `scripts/rehearse/_chromadb_regen.py`, already identified as Slice 10 work, and the Slice 8 touched files pass focused lint and format checks.

## Evidence

- `scripts/rehearse/_membase_export.py:28` documents the type-specific override decisions and no-override scope for the other versioned tables.
- `scripts/rehearse/_membase_export.py:315` implements `_classify_test_path`, including mixed-scope, framework, named-adopter, adopter-product, and fall-through behavior.
- `scripts/rehearse/_membase_export.py:343` implements `_classify_deliberation_origin`.
- `scripts/rehearse/_membase_export.py:360` dispatches type-specific classification before generic classification.
- `scripts/rehearse/_membase_export.py:380` now enumerates versioned tables with type-specific columns when present.
- `tests/scripts/test_rehearse_membase_export.py:358` through `:588` adds regression coverage for framework test paths, adopter test paths, mixed-scope tests, NULL/outside-path fall-through, adopter deliberation origins, framework deliberation origins, and NULL-origin fallback.

Verification commands run by Codex:

```text
python -m pytest tests/scripts/test_rehearse_membase_export.py -q --tb=short --timeout=60
35 passed in 3.62s

python -m pytest tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=60
66 passed in 0.49s

python -m ruff check scripts/rehearse/_membase_export.py tests/scripts/test_rehearse_membase_export.py
All checks passed!

python -m ruff format --check scripts/rehearse/_membase_export.py tests/scripts/test_rehearse_membase_export.py
2 files already formatted

python scripts/rehearse_isolation.py --phase membase --execute --output-dir C:\temp\agent-red-rehearsal-slice8-revised1-codex-verify
-> membase ... ok
```

Live manifest evidence from `C:\temp\agent-red-rehearsal-slice8-revised1-codex-verify\membase_export\membase-partition-manifest.json`:

```text
tables_discovered: 21
tables_versioned: 12
tables_relationship: 2
tables_excluded_telemetry: 4
tables_per_session: 3
total_versioned_rows: 40034
total_unique_artifacts: 17352
adopter: 11712
framework: 40
unclassified: 5600
relationship_records: 445
per_session_records: 138
warnings: 0
```

Live `tests` classification signals:

```text
9963 test_path_adopter_product
1126 no_classification_signal
  53 agent_red_product_reference
```

Live `deliberations` classification signals:

```text
1264 deliberation_origin_project_agent_red
  12 no_classification_signal
  11 groundtruth_kb_reference
  11 mixed_scope_content
   4 agent_red_product_reference
   1 deliberation_origin_project_framework
```

The wider rehearsal glob was also rerun with PowerShell file expansion:

```text
python -m pytest @files -q --tb=line --timeout=120
1 failed, 276 passed in 7.86s
```

The only failure was `tests/scripts/test_rehearse_lint_clean.py::test_rehearse_package_passes_ruff_format_check`, which reported:

```text
Would reformat: scripts\rehearse\_chromadb_regen.py
```

That failure is outside the Slice 8 changed files and matches the already-acknowledged Slice 10 WIP formatting issue.

## Risk / Impact

The Slice 8 cutover evidence is now materially stronger than the original implementation: the large test-row population no longer depends on generic content scan behavior, and deliberation ownership now uses the origin metadata that is the stronger live ownership signal.

Residual risk remains around the broad `tests/` default-to-adopter rule. For the current Agent Red adopter KB, the rule is defensible because explicit framework and mixed-scope exceptions run first, NULL paths still fall through, and the live data shows this is the only rule that classifies the 9,963 otherwise-unclassified test-path records. If GT-KB later imports upstream framework test artifacts into this same adopter KB with non-`tests/groundtruth_kb/` paths, this rule should be revisited.

## Recommended Action

Proceed with Slice 8 as verified. Track the `_chromadb_regen.py` package-format failure under Slice 10, not Slice 8.

## Decision Needed From Owner

None.
