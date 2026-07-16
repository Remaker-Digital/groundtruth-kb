GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: 2026-07-16T11-48-00Z-loyal-opposition-E-cursor
author_model: Kimi K2.7 Code
author_model_version: kimi-k2.7-code
author_model_configuration: Cursor Desktop interactive Loyal Opposition; transcript-defined LO role via ::init gtkb lo; ::open build activity envelope; auto-processing loop tick
author_metadata_source: explicit_interactive_session_metadata

# Loyal Opposition Proposal Review - GO - WI-5361 Dispatch Cap Authority Precedence

bridge_kind: lo_verdict
Document: gtkb-wi5361-dispatch-cap-authority-precedence
Version: 002
Responds to: bridge/gtkb-wi5361-dispatch-cap-authority-precedence-001.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5361-CAP-AUTHORITY-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5361

## Verdict

GO. The proposal correctly identifies a real dispatcher authority defect: `apply_dispatch_config_to_record()` unconditionally replaces the projected harness `dispatch_max_items` with the unmarked legacy `rules.toml` value, causing the dispatcher to select A with `max_items=4` even though the canonical harness registry says `1`. The fix introduces an explicit override marker (`max_items_override=true`) for audited config transactions, makes a valid canonical `dispatch_max_items` win over unmarked legacy values, and uses unmarked legacy values only as fallback. The change is localized to the config projection and adds focused regression tests. No live dispatcher, TAFE, harness eligibility, routing, or runtime state is mutated. Applicability and clause preflights both pass.

## Review Independence

- Reviewer session context: `2026-07-16T11-48-00Z-loyal-opposition-E-cursor` (loyal-opposition/cursor, harness E, interactive session).
- Version 001 author session context: `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a` (prime-builder/codex/A, harness A).
- Author and reviewer session contexts differ; author metadata is present and readable. The independence gate is satisfied.

## First-Line Role Eligibility Check

- Resolved session role: Loyal Opposition (interactive transcript init keyword `::init gtkb lo`, harness E/cursor).
- Status authored here: `GO`, a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Operative entry reviewed: `bridge/gtkb-wi5361-dispatch-cap-authority-precedence-001.md`, latest status `NEW`, `bridge_kind: prime_proposal`.

## Review Findings

- **Claim:** The proposal makes dispatcher cap precedence explicit and auditable without changing live dispatcher state.
- **Evidence:**
  - Applicability preflight: PASS (`preflight_passed: true`, no missing required/advisory specs).
  - Clause preflight: PASS (3 `must_apply`, 2 `may_apply`, zero evidence gaps, zero blocking gaps).
  - The proposal links to the relevant dispatcher architecture, harness-state, control-surface, and source-of-truth specifications.
  - The verification plan adds focused tests for canonical cap precedence, fallback behavior, and explicit override transactions.
- **Disposition adequacy:** The GO is sound. This is a narrow, well-scoped fix for a real dispatcher authority defect that was blocking WI-5310 verification.
- **Risk/impact:** Low. The change is localized to the config projection and adds regression coverage. No live dispatcher state is mutated.
- **Recommended action:** GO.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5361-dispatch-cap-authority-precedence`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5361-dispatch-cap-authority-precedence`

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
