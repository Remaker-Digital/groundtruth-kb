GO

bridge_kind: lo_verdict
Document: gtkb-wi5100-work-subject-config-platform-classification
Version: 002
Author: Loyal Opposition (antigravity, harness C)
Date: 2026-07-09 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5100-work-subject-config-platform-classification-001.md

author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 6147bb18-d9cc-41a7-8702-1ca4a8b977cf
author_model: Claude Opus 4.6 (Thinking)
author_model_version: claude-opus-4-6
author_model_configuration: Antigravity harness, Loyal Opposition role

## Verdict: GO

Loyal Opposition grants GO for WI-5100: work-subject `config/` platform-classification carve-out. The proposal correctly identifies the misclassification defect (blanket `config/` in `APPLICATION_PREFIXES` without governance carve-outs), the fix is narrowly scoped to the six existing platform subdirectories, the carve-out precision is explicitly tested (out-of-carve-out `config/<other>` still classifies as `application_product`), and all preflights pass. No blocking findings.

## Applicability Preflight

- packet_hash: `sha256:953e30256faa7cad3634e5c4d13610b1fa11e1e277fb7befcb716cf278c1c890`
- bridge_document_name: `gtkb-wi5100-work-subject-config-platform-classification`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5100-work-subject-config-platform-classification-001.md`
- operative_file: `bridge/gtkb-wi5100-work-subject-config-platform-classification-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0; Blocking gaps: 0

## Review Analysis

**Root cause correctness:** The blanket `config/` entry in `APPLICATION_PREFIXES` without any governance-prefix carve-out for the six platform config subdirectories is a genuine classification defect. Because `classify_root` checks governance prefixes before application prefixes, adding the six subdirectory prefixes to `CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES` is the correct fix — it lets the governance match win for platform config while preserving the app-config fallback for any future `config/<other>` path.

**Carve-out precision:** The proposal explicitly tests that an out-of-carve-out `config/` path still classifies as `application_product`, which guards against over-broadening. This is the right conservative approach — enumerate the known platform subdirectories rather than flipping the blanket `config/` entry.

**Impact assessment:** This is a real live blocker — it blocked an authorized WI-4841 registry edit and would block WI-5040/5041 dispatcher-config work. The fix is urgently needed.

**Scope:** Minimal — two files only (`scripts/workstream_focus.py` and `platform_tests/hooks/test_workstream_focus.py`). No risk of collateral damage.

## Conditions / Required Actions

None — unconditional GO.

## Owner Action Required

None.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
