# Docstring Coverage Baseline (Phase 4A)

Generated with `interrogate 1.7.0` against `src/groundtruth_kb/`.

## Part 1: Per-file coverage (whole package)

- **Total nodes:** 566
- **Covered:** 342
- **Missing:** 224
- **Coverage:** 60.42%

### Per-file breakdown (sorted worst-first)

| File | Total | Covered | Missing | % |
|---|---:|---:|---:|---:|
| `bridge/worker.py` | 36 | 2 | 34 | 5.6% |
| `bridge/context.py` | 33 | 2 | 31 | 6.1% |
| `bootstrap.py` | 14 | 2 | 12 | 14.3% |
| `bridge/poller.py` | 23 | 4 | 19 | 17.4% |
| `bridge/launcher.py` | 12 | 3 | 9 | 25.0% |
| `web/app.py` | 18 | 5 | 13 | 27.8% |
| `bridge/handshake.py` | 7 | 2 | 5 | 28.6% |
| `bridge/runtime.py` | 50 | 21 | 29 | 42.0% |
| `project/doctor.py` | 29 | 14 | 15 | 48.3% |
| `gates.py` | 20 | 13 | 7 | 65.0% |
| `project/scaffold.py` | 15 | 10 | 5 | 66.7% |
| `db.py` | 164 | 122 | 42 | 74.4% |
| `gates_transport.py` | 9 | 7 | 2 | 77.8% |
| `intake.py` | 10 | 9 | 1 | 90.0% |
| `cli.py` | 33 | 33 | 0 | 100.0% |
| `assertions.py` | 28 | 28 | 0 | 100.0% |
| `reconciliation.py` | 12 | 12 | 0 | 100.0% |
| `spec_scaffold.py` | 10 | 10 | 0 | 100.0% |
| `impact.py` | 8 | 8 | 0 | 100.0% |
| `assertion_schema.py` | 7 | 7 | 0 | 100.0% |
| `project/upgrade.py` | 7 | 7 | 0 | 100.0% |
| `config.py` | 6 | 6 | 0 | 100.0% |
| `health.py` | 4 | 4 | 0 | 100.0% |
| `project/manifest.py` | 4 | 4 | 0 | 100.0% |
| `project/profiles.py` | 4 | 4 | 0 | 100.0% |
| `seed.py` | 3 | 3 | 0 | 100.0% |

Total files audited: **26**

## Part 2: Public API subset (Codex Condition 1)

The public API is defined by `groundtruth_kb.__init__.py::__all__`. This section audits docstring presence on every exported symbol and, for classes, every public method (non-underscore name defined on the class).

- **Public symbols + methods:** 147
- **With docstring:** 120
- **Missing docstring:** 27
- **Public API coverage:** 81.63%

### Per-symbol breakdown

| Symbol | Kind | Module | Has docstring |
|---|---|---|:---:|
| `GTConfig` | class | `config` | yes |
| `GTConfig.load` | method | `config` | yes |
| `KnowledgeDB` | class | `db` | yes |
| `KnowledgeDB.capture_session_snapshot` | method | `db` | yes |
| `KnowledgeDB.check_constraints_for_spec` | method | `db` | yes |
| `KnowledgeDB.close` | method | `db` | no |
| `KnowledgeDB.compute_impact` | method | `db` | yes |
| `KnowledgeDB.compute_m10_defect_resolution_duration` | method | `db` | yes |
| `KnowledgeDB.compute_m11_regression_rate` | method | `db` | yes |
| `KnowledgeDB.compute_m12_spec_retirement_rate` | method | `db` | yes |
| `KnowledgeDB.compute_m16_verified_with_passing_tests_rate` | method | `db` | yes |
| `KnowledgeDB.compute_m17_stale_test_ratio` | method | `db` | yes |
| `KnowledgeDB.compute_m18_implemented_without_test_count` | method | `db` | yes |
| `KnowledgeDB.compute_m2_spec_revision_rounds` | method | `db` | yes |
| `KnowledgeDB.compute_m4_spec_to_implemented_duration` | method | `db` | yes |
| `KnowledgeDB.compute_m6_defect_injection_rate` | method | `db` | yes |
| `KnowledgeDB.compute_session_delta` | method | `db` | yes |
| `KnowledgeDB.consume_session_prompt` | method | `db` | yes |
| `KnowledgeDB.create_backlog_snapshot_from_current` | method | `db` | yes |
| `KnowledgeDB.export_json` | method | `db` | yes |
| `KnowledgeDB.get_active_test_plan` | method | `db` | yes |
| `KnowledgeDB.get_all_latest_assertion_runs` | method | `db` | yes |
| `KnowledgeDB.get_audit_directive` | method | `db` | yes |
| `KnowledgeDB.get_backlog_snapshot` | method | `db` | no |
| `KnowledgeDB.get_backlog_snapshot_history` | method | `db` | no |
| `KnowledgeDB.get_constraint_coverage` | method | `db` | yes |
| `KnowledgeDB.get_deliberation` | method | `db` | yes |
| `KnowledgeDB.get_deliberation_history` | method | `db` | yes |
| `KnowledgeDB.get_deliberations_for_spec` | method | `db` | yes |
| `KnowledgeDB.get_deliberations_for_work_item` | method | `db` | yes |
| `KnowledgeDB.get_document` | method | `db` | no |
| `KnowledgeDB.get_element_coverage_summary` | method | `db` | yes |
| `KnowledgeDB.get_env_config` | method | `db` | yes |
| `KnowledgeDB.get_env_config_history` | method | `db` | yes |
| `KnowledgeDB.get_events_for_artifact` | method | `db` | yes |
| `KnowledgeDB.get_history` | method | `db` | yes |
| `KnowledgeDB.get_latest_assertion_run` | method | `db` | no |
| `KnowledgeDB.get_lifecycle_metrics` | method | `db` | yes |
| `KnowledgeDB.get_next_session_prompt` | method | `db` | yes |
| `KnowledgeDB.get_op_procedure` | method | `db` | no |
| `KnowledgeDB.get_op_procedure_history` | method | `db` | no |
| `KnowledgeDB.get_open_work_items` | method | `db` | yes |
| `KnowledgeDB.get_provisional_specs` | method | `db` | yes |
| `KnowledgeDB.get_quality_distribution` | method | `db` | yes |
| `KnowledgeDB.get_quality_history` | method | `db` | yes |
| `KnowledgeDB.get_quality_score` | method | `db` | yes |
| `KnowledgeDB.get_quality_scores` | method | `db` | yes |
| `KnowledgeDB.get_session_prompt` | method | `db` | yes |
| `KnowledgeDB.get_session_snapshot` | method | `db` | yes |
| `KnowledgeDB.get_snapshot_history` | method | `db` | yes |
| `KnowledgeDB.get_spec` | method | `db` | yes |
| `KnowledgeDB.get_spec_history` | method | `db` | yes |
| `KnowledgeDB.get_specs_affected_by` | method | `db` | yes |
| `KnowledgeDB.get_summary` | method | `db` | no |
| `KnowledgeDB.get_test` | method | `db` | no |
| `KnowledgeDB.get_test_coverage_for_spec` | method | `db` | yes |
| `KnowledgeDB.get_test_coverage_summary` | method | `db` | yes |
| `KnowledgeDB.get_test_history` | method | `db` | no |
| `KnowledgeDB.get_test_plan` | method | `db` | no |
| `KnowledgeDB.get_test_plan_history` | method | `db` | no |
| `KnowledgeDB.get_test_plan_phase` | method | `db` | no |
| `KnowledgeDB.get_test_procedure` | method | `db` | no |
| `KnowledgeDB.get_test_procedure_history` | method | `db` | no |
| `KnowledgeDB.get_testable_element` | method | `db` | yes |
| `KnowledgeDB.get_tests_for_spec` | method | `db` | yes |
| `KnowledgeDB.get_untested_specs` | method | `db` | yes |
| `KnowledgeDB.get_work_item` | method | `db` | no |
| `KnowledgeDB.get_work_item_history` | method | `db` | no |
| `KnowledgeDB.insert_assertion_run` | method | `db` | no |
| `KnowledgeDB.insert_backlog_snapshot` | method | `db` | yes |
| `KnowledgeDB.insert_deliberation` | method | `db` | yes |
| `KnowledgeDB.insert_document` | method | `db` | yes |
| `KnowledgeDB.insert_env_config` | method | `db` | yes |
| `KnowledgeDB.insert_op_procedure` | method | `db` | no |
| `KnowledgeDB.insert_quality_score` | method | `db` | yes |
| `KnowledgeDB.insert_session_prompt` | method | `db` | yes |
| `KnowledgeDB.insert_spec` | method | `db` | yes |
| `KnowledgeDB.insert_test` | method | `db` | yes |
| `KnowledgeDB.insert_test_coverage` | method | `db` | yes |
| `KnowledgeDB.insert_test_coverage_batch` | method | `db` | yes |
| `KnowledgeDB.insert_test_plan` | method | `db` | yes |
| `KnowledgeDB.insert_test_plan_phase` | method | `db` | yes |
| `KnowledgeDB.insert_test_procedure` | method | `db` | no |
| `KnowledgeDB.insert_testable_element` | method | `db` | yes |
| `KnowledgeDB.insert_work_item` | method | `db` | yes |
| `KnowledgeDB.is_audit_session` | method | `db` | yes |
| `KnowledgeDB.link_deliberation_spec` | method | `db` | yes |
| `KnowledgeDB.link_deliberation_work_item` | method | `db` | yes |
| `KnowledgeDB.list_backlog_snapshots` | method | `db` | yes |
| `KnowledgeDB.list_children` | method | `db` | yes |
| `KnowledgeDB.list_constraint_verifications` | method | `db` | yes |
| `KnowledgeDB.list_deliberations` | method | `db` | yes |
| `KnowledgeDB.list_design_constraints` | method | `db` | yes |
| `KnowledgeDB.list_direct_children` | method | `db` | yes |
| `KnowledgeDB.list_documents` | method | `db` | no |
| `KnowledgeDB.list_env_config` | method | `db` | yes |
| `KnowledgeDB.list_events` | method | `db` | yes |
| `KnowledgeDB.list_implementation_proposals` | method | `db` | yes |
| `KnowledgeDB.list_op_procedures` | method | `db` | no |
| `KnowledgeDB.list_session_prompts` | method | `db` | yes |
| `KnowledgeDB.list_specs` | method | `db` | yes |
| `KnowledgeDB.list_test_plan_phases` | method | `db` | yes |
| `KnowledgeDB.list_test_plans` | method | `db` | no |
| `KnowledgeDB.list_test_procedures` | method | `db` | no |
| `KnowledgeDB.list_testable_elements` | method | `db` | yes |
| `KnowledgeDB.list_tests` | method | `db` | yes |
| `KnowledgeDB.list_work_items` | method | `db` | yes |
| `KnowledgeDB.parse_session_number` | method | `db` | yes |
| `KnowledgeDB.persist_quality_scores` | method | `db` | yes |
| `KnowledgeDB.propagate_constraint` | method | `db` | yes |
| `KnowledgeDB.rebuild_deliberation_index` | method | `db` | yes |
| `KnowledgeDB.record_event` | method | `db` | yes |
| `KnowledgeDB.redact_content` | method | `db` | yes |
| `KnowledgeDB.remove_constraint_link` | method | `db` | yes |
| `KnowledgeDB.score_spec_quality` | method | `db` | yes |
| `KnowledgeDB.search_deliberations` | method | `db` | yes |
| `KnowledgeDB.update_document` | method | `db` | yes |
| `KnowledgeDB.update_env_config` | method | `db` | yes |
| `KnowledgeDB.update_spec` | method | `db` | yes |
| `KnowledgeDB.update_test` | method | `db` | yes |
| `KnowledgeDB.update_test_plan` | method | `db` | yes |
| `KnowledgeDB.update_test_plan_phase` | method | `db` | yes |
| `KnowledgeDB.update_work_item` | method | `db` | yes |
| `KnowledgeDB.upsert_deliberation_source` | method | `db` | yes |
| `KnowledgeDB.validate_dcl_constraints` | method | `db` | yes |
| `GateRegistry` | class | `gates` | yes |
| `GateRegistry.from_config` | method | `gates` | yes |
| `GateRegistry.register` | method | `gates` | no |
| `GateRegistry.run_pre_promote` | method | `gates` | no |
| `GateRegistry.run_pre_resolve_work_item` | method | `gates` | no |
| `GateRegistry.run_pre_test_pass` | method | `gates` | yes |
| `GovernanceGate` | class | `gates` | yes |
| `GovernanceGate.name` | method | `gates` | yes |
| `GovernanceGate.pre_promote` | method | `gates` | yes |
| `GovernanceGate.pre_resolve_work_item` | method | `gates` | yes |
| `GovernanceGate.pre_test_pass` | method | `gates` | yes |
| `GovernanceGateError` | class | `gates` | yes |
| `format_summary` | function | `assertions` | yes |
| `run_all_assertions` | function | `assertions` | yes |
| `run_single_assertion` | function | `assertions` | yes |
| `validate_assertion` | function | `assertion_schema` | yes |
| `validate_assertion_list` | function | `assertion_schema` | yes |
| `spec_sort_key` | function | `db` | yes |
| `get_depth` | function | `db` | yes |
| `get_parent_id` | function | `db` | yes |
| `get_templates_dir` | function | `groundtruth_kb` | yes |
| `__version__` | attribute | `groundtruth_kb` | yes |

### Missing-docstring list (Phase 4B targets)

- `KnowledgeDB.close` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_backlog_snapshot` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_backlog_snapshot_history` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_document` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_latest_assertion_run` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_op_procedure` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_op_procedure_history` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_summary` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_test` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_test_history` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_test_plan` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_test_plan_history` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_test_plan_phase` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_test_procedure` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_test_procedure_history` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_work_item` (method, `groundtruth_kb.db`)
- `KnowledgeDB.get_work_item_history` (method, `groundtruth_kb.db`)
- `KnowledgeDB.insert_assertion_run` (method, `groundtruth_kb.db`)
- `KnowledgeDB.insert_op_procedure` (method, `groundtruth_kb.db`)
- `KnowledgeDB.insert_test_procedure` (method, `groundtruth_kb.db`)
- `KnowledgeDB.list_documents` (method, `groundtruth_kb.db`)
- `KnowledgeDB.list_op_procedures` (method, `groundtruth_kb.db`)
- `KnowledgeDB.list_test_plans` (method, `groundtruth_kb.db`)
- `KnowledgeDB.list_test_procedures` (method, `groundtruth_kb.db`)
- `GateRegistry.register` (method, `groundtruth_kb.gates`)
- `GateRegistry.run_pre_promote` (method, `groundtruth_kb.gates`)
- `GateRegistry.run_pre_resolve_work_item` (method, `groundtruth_kb.gates`)

## Notes

- **Private modules are NOT included** in the public API subset. They still appear in Part 1's per-file table.
- **Inherited methods (from `object`/`Exception`) are skipped** in the public-API audit because they are not defined on the class itself.
- **`__version__`** is a string attribute, not a documentable symbol; marked N/A in the public API table but counted as covered to avoid false-negative.

---

*Generated by `scripts/audit_docstrings.py`. Part of the Phase 4A measurement-only audit baseline.*
