GO

# WI-5206 - Dedicated minimal fast-wrapup path - Loyal Opposition Proposal Review

bridge_kind: lo_verdict
Document: gtkb-wi5206-fast-wrapup-minimal-path
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-12 UTC

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 2026-07-12T01-39-37Z-loyal-opposition-B-0d5e00
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless auto-dispatch; resolved role loyal-opposition (harness B); max reasoning effort

Responds to: bridge/gtkb-wi5206-fast-wrapup-minimal-path-001.md (NEW; author session 019f522a-849d-7d43-8c60-0afc829438a6, prime-builder/codex/A)
Reviewer session: 2026-07-12T01-39-37Z-loyal-opposition-B-0d5e00 (independent; differs from author session)

Verdict: GO

---

## Summary

This is a pre-implementation proposal review. The proposal adds a dedicated minimal fast-wrapup collector to `scripts/session_self_initialization.py` so that `--emit-wrapup --fast-hook` computes only the fields consumed by `render_wrapup_notice`, writes the wrap-up report, and bypasses the full startup/dashboard model build, dashboard-data write, dashboard-history append, startup-report render, reachability/compilation, and PDF work. Ordinary startup, ordinary non-fast wrap-up, dashboard generation, and the WI-5204 60-second Stop allowance are declared out of scope and unchanged.

Verdict is GO. The optimization premise is verified against live code, both mandatory preflights are clean, specification linkage is complete, the test plan derives from the linked specs and covers both named risks, and the slice is cleanly separable from sibling WI-5204 with independent rollback. Four non-blocking recommendations are attached for the implementation and verification phases; none block GO.

## Review Independence

Author session context `019f522a-849d-7d43-8c60-0afc829438a6` (prime-builder/codex/A). Reviewer session context `2026-07-12T01-39-37Z-loyal-opposition-B-0d5e00` (loyal-opposition/claude/B, dispatcher-routed). The sessions are unrelated, so the review-independence boundary in `config/agent-control/SESSION-STARTUP-INDEX.md` and `file-bridge-protocol.md` is satisfied.

## Premise Verification (against live source at HEAD)

The proposal's core premise was verified against the current code rather than accepted from the proposal text.

1. Fast-hook wrap-up still builds the full model. `scripts/session_self_initialization.py:6568` shows the `--emit-wrapup` handler (`write_dashboard_and_report`) unconditionally calls `build_startup_model(..., fast_hook=fast_hook)`. The `fast_hook` flag only short-circuits a few sub-probes (`_dashboard_reachability_probes`, `_gtkb_upgrade_posture`, `_testing_service_integrations`, PDF, historical backfill); the remaining heavy collectors still run: `_database_metrics`, `_backlog_metrics`, `_release_blockers`, skill/rule/hook globs, a full `tests/**/test_*.py` rglob (`scripts/session_self_initialization.py:3512`), `_harness_parity_status`, `_harness_launchability_status`, `_plugin_inventory`, `_dev_environment_inventory_status`, `_git_drift`, `_bridge_metrics`, `_delivery_timeline`, and `_dashboard_intelligence`.

2. The fast-hook wrap-up run also performs unrelated writes. `scripts/session_self_initialization.py:6595` appends dashboard history, `:6603` writes `dashboard-data.json`, `:6606` renders the full startup report, and `:6608` writes `session-startup-report.md` - during a wrap-up. At `:7734` only `result["wrapup_text"]` is emitted, so all of that startup/dashboard/report work is discarded output for the fast-hook Stop path.

3. The wrap-up notice consumes a narrow field set. `render_wrapup_notice` (`scripts/session_self_initialization.py:5211-5256`) reads only `metrics['backlog']`, `metrics['membase']` (via `_format_open_work_items_count`), `metrics['regression'].release_blocker_count`, `metrics['contention'].actionable_count`, `metrics['drift'].changed_path_count`, `model['top_priority_actions']`, and `model['generated_at']`.

4. `top_priority_actions` is cheap. `scripts/session_self_initialization.py:3651` sets `"top_priority_actions": top_actions`, and `top_actions` comes from `_backlog_metrics(project_root)` at `:3507` - NOT from `_dashboard_intelligence`. This is the crux: computing the wrap-up notice does not transitively require the expensive dashboard-intelligence path, so a minimal collector calling `_backlog_metrics`, `_database_metrics` (membase), `_release_blockers`, `_bridge_metrics`, `_git_drift`, and `_now_iso` is genuinely and substantially cheaper. All those collectors are module-level functions in the single target file, so `target_paths` are sufficient.

Conclusion: the premise holds in full. The described optimization removes real, measurable work.

## Specification Linkage

The proposal cites `GOV-SESSION-SELF-INITIALIZATION-001` (owns the startup/wrap-up model, generated reports, and fast-hook behavior - the governing spec), `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-STANDING-BACKLOG-001`, and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`. The applicability preflight confirms `missing_required_specs: []`. Linkage is complete for the required set.

## Prior Deliberations

Nearest prior deliberation is `DELIB-1078` (Session Initialization Defects - Fast Hook Repair), the earlier fast-hook work on this same file; it does not conflict with a minimal-collector optimization and does not represent a previously-rejected approach that this proposal silently revisits. `DELIB-1077` (Session Hook Dispatcher Repair) and `DELIB-1083` (Startup Token And Premature Wrap-Up Feedback) are adjacent but non-conflicting. The proposal's own cited deliberations (`DELIB-202666173`, `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES`) are the directly governing owner/policy records. No revisiting of a rejected approach detected.

## Test Plan Assessment

The Spec-Derived Verification Plan maps to `GOV-SESSION-SELF-INITIALIZATION-001` (branch selection + minimal-collector call assertions), to the ordinary-path preservation contract, to a cold/contention timing check against the 60-second allowance (no reintroduced micro-budget), and to `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (independent LO execution + ruff). The two named risks (omitting a renderer-consumed field; routing ordinary startup through the reduced model) are each covered by the proposed tests (output equivalence + branch selection). The target test file `platform_tests/scripts/test_session_self_initialization.py` exists and is the correct location.

## Backlog / Sibling Conflict Check

Sibling WI-5204 (Stop-hook correctness + 15->60s allowance) touches `.claude/settings.json`, `scripts/cloud_harness_base.py`, `scripts/check_codex_hook_parity.py`, and their tests. WI-5206 touches `scripts/session_self_initialization.py` and its test. The two `target_paths` sets do not intersect, so the rollback-independence claim is structurally sound: WI-5206 can be reverted without disturbing WI-5204's Stop semantics or the 60-second allowance, and vice versa. No duplicate-work or interference conflict found in the active backlog for this slice.

## Findings and Recommendations (non-blocking; for implementation and verification)

R1 (medium - required confirmation in the implementation report). The current fast-hook wrap-up run, as a side effect, refreshes `dashboard-data.json` (`:6603`), appends dashboard history (`:6595`), and writes `session-startup-report.md` (`:6606`/`:6608`). The minimal path will stop producing these on the fast-hook Stop. This is very likely benign (the preceding SessionStart run already refreshed them, and writing a startup report during wrap-up is arguably incorrect), but the implementation report must explicitly confirm that no downstream consumer depends on the fast-hook wrap-up run to refresh dashboard-data, history, or the startup report. If any consumer does, either preserve that specific write in the fast path or document the accepted KPI-history granularity reduction.

R2 (recommended). The equivalence test should assert that the minimal collector's `render_wrapup_notice` output is byte-identical to the full-model wrap-up notice output for a shared fixture (proving no consumed field is dropped or reshaped), not merely that the minimal collector is called. The proposal already commits to "output equivalence"; make it a direct notice-text comparison.

R3 (minor; pre-existing; out of scope). `scripts/session_self_initialization.py:3547` sets `startup_self_initialization_test` to `tests/scripts/test_session_self_initialization.py`, which does not exist; the real path is `platform_tests/scripts/test_session_self_initialization.py`. This stale string predates WI-5206 and is not in scope, but since the implementation edits this file, it is a low-cost opportunistic correction or a standing-backlog capture candidate. Not a condition of GO.

R4 (advisory only). The applicability preflight lists two uncited advisory specs (`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`). Advisory-severity and non-blocking; the closely-related `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` is already cited. Optional to add.

## Applicability Preflight

- packet_hash: `sha256:81337b955d5302c95536fbd61bfcf8e63808befc4c862f692051ef3ec2d4b5e0`
- bridge_document_name: `gtkb-wi5206-fast-wrapup-minimal-path`
- operative_file: `bridge/gtkb-wi5206-fast-wrapup-minimal-path-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

## Clause Applicability

- Bridge id: `gtkb-wi5206-fast-wrapup-minimal-path`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation); exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | may_apply | - | blocking | blocking |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | GOV-FILE-BRIDGE-AUTHORITY-001 | must_apply | yes | blocking | blocking |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | must_apply | yes | blocking | blocking |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | must_apply | yes | blocking | blocking |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | GOV-STANDING-BACKLOG-001 | may_apply | - | blocking | blocking |

## Verdict

GO. The proposal is spec-linked, preflight-clean, premise-verified against live source, testable against its linked specs, and cleanly separable from WI-5204 with independent rollback. Recommendations R1-R4 are non-blocking; R1 (downstream-consumer confirmation for the dropped dashboard-data/history/startup-report writes) and R2 (notice-text equivalence assertion) should be resolved in the implementation report so post-implementation verification can confirm them. Prime Builder is clear to run the implementation-start authorization from this GO and implement within the declared `target_paths`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
