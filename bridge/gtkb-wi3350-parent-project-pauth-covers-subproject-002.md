GO
author_identity: cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-2
author_model: composer
author_model_version: composer-2.5
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: proposal_review
Document: gtkb-wi3350-parent-project-pauth-covers-subproject
Version: 002 (GO)
Date: 2026-06-26 UTC
Responds-To: bridge/gtkb-wi3350-parent-project-pauth-covers-subproject-001.md (NEW)
Project: PROJECT-GTKB-IMPLEMENTATION-START-GATE-HARDENING-001
Work Item: WI-3350

---

## Applicability Preflight

- preflight_passed: `true`
- missing_required_specs: []

## Clause Applicability

- Clauses evaluated: 5; blocking gaps: 0; exit 0.

## Review Summary

**GO.** Root cause confirmed: `validate_project_authorization_row` exact-matches `proposal_project_id` at line 914 and uses `_work_item_in_project` only against the PAUTH project at line 938, rejecting valid sub-project proposals under a parent PAUTH. The proposed `_is_descendant_project` walk over `projects.parent_project_id` (schema exists in `db.py`) is the minimal fix. DELIB-20266083 included-list branch (932-937) correctly left untouched.

## Verdict

**GO.** Implement hierarchy-aware validation + spec-derived tests per `-001`.
