# Retired Bridge Artifact Runtime Source Cleanout Ledger

Generated: 2026-06-16T17:30:00Z

Bridge thread: `gtkb-retired-bridge-artifact-runtime-source-cleanout`
Implementation session: `019ed12a-6581-7683-8066-df4bfcb3b821`

## Scan Command

```powershell
$paths = @(
  'groundtruth-kb\src',
  'scripts',
  'platform_tests',
  'groundtruth-kb\tests',
  'groundtruth-kb\templates',
  'config\agent-control',
  '.claude\rules',
  '.codex\skills',
  '.claude\skills',
  '.claude\hooks',
  '.codex\gtkb-hooks'
)
rg -n --hidden -g '!**/__pycache__/**' -g '!*.pyc' `
  -e 'bridge/INDEX\.md|bridge index|bridge-index|parse_bridge_index|check_index_cites_missing_bridge_file|check_bridge_file_orphaned_from_index|bridge_reconciliation_audit|retroactive_harvest_bridge_threads|get_block' `
  @paths
```

Exit code: `0`  
Hit count: `239`

## Completion Classes

| Class | Severity | Count | Disposition |
|---|---:|---:|---|
| Authorized runtime source behavior | info | 2 | Remaining hits are negative-control wording in read-only TAFE modules: `groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py` and `groundtruth-kb/src/groundtruth_kb/tafe_stuck_flow.py`. |
| Authorized no-index tests and fixtures updated in this run | info | 67-test focused suite | Scaffold, doctor, golden-fixture, writer, harvest, MemBase-audit, and wrap-scan reconciliation tests now pass without requiring `bridge/INDEX.md`. |
| Authorized dependency tests updated in this run | info | 189-test focused suite | Applicability preflight, triad audit, standing backlog, backfill, spec mapper, and wrap-scan tests now pass against status-bearing versioned files. |
| Historical fixtures and anti-pattern tests | info | many | Remaining hits intentionally exercise retired-index blocking, old live snapshots, inventory-string scanning, command guards, or historical governance evidence. They are not live authority. |
| Template hook parity follow-up | follow-up | 1 file | `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` still exposes the legacy `_parse_bridge_index` name and retired-index wording. `implementation_authorization.py validate --target groundtruth-kb\templates\hooks\bridge-compliance-gate.py` failed closed, so this path was not edited in this implementation packet. |
| Broad hook verification | follow-up | 3 files attempted | `python -m pytest -p no:cacheprovider platform_tests\hooks\test_bridge_compliance_gate_index_exemption.py platform_tests\hooks\test_bridge_compliance_gate_body_status_token.py platform_tests\hooks\test_bridge_compliance_gate_hard_block_workspace.py -q --tb=short` timed out after 184 seconds while external bridge hooks/dispatchers were active. No pass/fail assertion was produced. |

## Remaining Highest-Count Paths

| Count | Path | Classification |
|---:|---|---|
| 14 | `platform_tests/scripts/test_check_commit_pathspec_safety.py` | Historical bridge-queue/pathspec grouping tests. |
| 12 | `groundtruth-kb/tests/fixtures/bridge_index_live_snapshot.md` | Historical live-index snapshot fixture. |
| 10 | `platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py` | Follow-up hook test requiring separate review after retired aggregate write denial. |
| 8 | `platform_tests/scripts/test_cross_harness_bridge_trigger.py` | Legacy dispatcher fixtures still named as bridge index; not touched in this packet. |
| 8 | `platform_tests/scripts/test_sweep_commit_helpers.py` | Historical co-staging evidence tests. |
| 6 | `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` | Follow-up template parity target; not authorized by this packet. |

## Verification Summary

Passing focused verification from this implementation:

```text
python -m pytest -p no:cacheprovider groundtruth-kb\tests\test_scaffold_bridge_index.py groundtruth-kb\tests\test_doctor_bridge_accuracy.py groundtruth-kb\tests\adopter\test_golden_fixture_diff_per_version.py groundtruth-kb\tests\test_scaffold_isolation.py platform_tests\scripts\test_gtkb_bridge_writer.py platform_tests\scripts\test_harvest_session_thread_level.py platform_tests\scripts\test_membase_effective_use_audit.py platform_tests\scripts\test_wrap_scan_reconciliation.py -q --tb=short
67 passed

python -m pytest -p no:cacheprovider platform_tests\scripts\test_implementation_authorization.py platform_tests\scripts\test_implementation_authorization_extract_spec_links_table.py platform_tests\scripts\test_bridge_applicability_preflight.py platform_tests\scripts\test_audit_gtkb_triad_completeness.py platform_tests\scripts\test_standing_backlog_harvest.py platform_tests\scripts\test_backfill_implements_links.py platform_tests\scripts\test_bridge_proposal_pattern_lint.py platform_tests\scripts\test_spec_to_test_mapper.py platform_tests\scripts\test_wrap_scan_consistency.py platform_tests\scripts\test_wrap_scan_consistency_allowlist.py platform_tests\scripts\test_wrap_scan_hygiene.py platform_tests\scripts\test_wrap_scan_hygiene_skip_dirs.py platform_tests\scripts\test_wrap_scan_reconciliation.py -q --tb=short
189 passed, 1 warning
```
