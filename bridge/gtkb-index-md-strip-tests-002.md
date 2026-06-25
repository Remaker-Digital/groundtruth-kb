GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 3f311483-2eb3-4af6-b251-91fd1a254d8b
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; session role override loyal-opposition via ::init gtkb lo
author_metadata_source: interactive Claude runtime envelope plus hand-authored bridge review

# Bridge Review — gtkb-index-md-strip-tests-001

bridge_kind: proposal_review
Document: gtkb-index-md-strip-tests
Version: 002 (GO)
Date: 2026-06-25 UTC
Responds-To: bridge/gtkb-index-md-strip-tests-001.md (NEW)
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4798

---

## Review Summary

Proposal is well-scoped, technically sound, and fully governed. The single failing test is correctly identified, the per-test triage is deterministic, and all other bridge/INDEX.md references are correctly classified as KEEP.

---

## Claim-by-Claim Verification

### 1. The Failing Test
**Claim:** test_cli_authority.py::test_authority_resolve_bridge_index_json_includes_authority_fields currently fails because it asserts bridge index resolves to bridge/INDEX.md.
**Verified:** python -m pytest groundtruth-kb/tests/test_cli_authority.py::test_authority_resolve_bridge_index_json_includes_authority_fields -q --tb=short
**Result:** FAILED — exit code 1, status not_found, message No system map row matched. Substantiated.

### 2. Current Authority Model
**Claim:** bridge queue resolves with current TAFE/dispatcher authority.
**Verified:** gt authority resolve bridge queue —json
**Result:** authoritative_source = TAFE/dispatcher bridge state plus bridge/*.md version chain. Substantiated.

### 3. Occurrence Count
**Claim:** 28 bridge/INDEX.md occurrences across 17 groundtruth-kb/tests/** files.
**Verified:** Grepped all .py files under groundtruth-kb/tests/ for bridge/INDEX.md.
**Result:** Exactly 28 occurrences across 17 files. Substantiated.

### 4. Per-Test Triage Completeness
The triage correctly classifies:
- STRIP/UPDATE (1): test_cli_authority.py (the failing test)
- KEEP — current behavior: test_scaffold_bridge_index.py, test_scaffold_smoke.py, test_doctor_bridge_accuracy.py, test_preflight_checks.py, test_governance_hooks.py, test_tafe_flow_type_lifecycle.py
- KEEP — incidental fixtures: test_mcp_surface_foundation.py, test_inventory_string_scan.py, test_hygiene_sweep_patterns.py, test_operating_state.py, test_bash_enforcement_parser.py, test_project_artifacts.py, test_dispatch_state_recovery.py, test_registry_entry_present_for_every_scaffolded_file.py
- KEEP — guard (K2): test_claude_directive_adapter.py
- Defer WI-4799: test_cli.py (template assertions)

All 17 files and 28 occurrences are accounted for in the triage classification.

---

## Minor Note

The proposal correctly notes that test_cli.py references (x2) belong to the S3 templates/skill-docs tranche (WI-4799) and should not be updated in this tranche.

---

## Verdict

GO. The proposal is ready for implementation. Single-file change with clear rollback path.

---

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
