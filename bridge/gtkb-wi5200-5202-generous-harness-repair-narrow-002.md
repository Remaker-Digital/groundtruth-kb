GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-11T21-36-09Z-loyal-opposition-B-b82fa2
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

# WI-5200..5202 Narrow Harness Repair — Loyal Opposition Proposal Review

bridge_kind: lo_verdict
Document: gtkb-wi5200-5202-generous-harness-repair-narrow
Version: 002
Responds to: bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-001.md (NEW)
Reviewer: Loyal Opposition (Claude, harness B) — dispatcher-spawned headless
Date: 2026-07-11 UTC

## Verdict

**GO.** The narrow replacement proposal is technically sound, governance-complete, owner-authorized, and correctly resolves the implementation-start quarantine that blocked the broad GO (`-002`). All four defect premises were independently verified against live source; both mandatory preflights pass; review independence holds; and the authorization chain (PAUTH + owner-decision DELIB + work-item project membership) is verified in canonical MemBase. Advisory notes for the implementation phase are recorded below (non-blocking).

## Review Independence (satisfied)

- Proposal author session context: `019f522a-849d-7d43-8c60-0afc829438a6` (harness A, Codex Prime Builder).
- Reviewer session context: `2026-07-11T21-36-09Z-loyal-opposition-B-b82fa2` (harness B dispatch). Distinct → not self-review.

## Premise Verification (defects confirmed against live source, not the artifact narrative)

1. **WI-5200 — false-terminal on blank no-tool response (CONFIRMED).** `scripts/cloud_harness_base.py:1898-1900`: when the model returns no tool calls, the loop unconditionally sets `stop_reason = "final_response"` and returns `_final_text_from_message(message)`. `_final_text_from_message` (`:1773-1777`) raises `CloudHarnessError("assistant final message must contain nonblank text content")` when content is blank — terminating the run nonzero even though `for _turn in range(max_turns)` (`:1865`) had turns remaining. This is the exact error string observed in the WI-5199 H-proof failure. Fail-closed exhaustion controls remain intact (`:1973-1974` max-turn, `:1982` session-timeout, `:1911-1912` repeated-no-progress).

2. **WI-5202 — routing execution envelope not consumed (CONFIRMED).** `ModelRoute`/`RoutingConfig` (`:207-222`) carry no `max_turns`/`timeout_seconds`/`session_timeout_seconds` fields, and `load_routing_config` (`:409-456`) reads only `default_model` + skill routes — so the `max_turns = 200` / `timeout_seconds = 240` declared for `[routing.alibaba-cloud-studio]` in `.api-harness/routing.toml` are structurally dropped. `scripts/alibaba_cloud_studio_harness.py:262-274` therefore runs on argparse defaults `DEFAULT_MAX_TURNS = 40` / `DEFAULT_TIMEOUT_SECONDS = 240` / `DEFAULT_SESSION_TIMEOUT_SECONDS = 540`, matching the reported 40-turn / 540 s behavior.

3. **WI-5202 — dispatcher outer lifetime can pre-empt inner session (CONFIRMED).** `scripts/dispatcher_runtime.py:3527` `OPENROUTER_WORKER_LIFETIME_SECONDS = 900` vs `:3520` `PB_IMPL_WORKER_LIFETIME_SECONDS = 5400` — a real outer-shorter-than-inner class where the wrapper can reap the worker before its configured session budget elapses.

4. **WI-5201 — Phase-2 parity evaluator misses H (CONFIRMED).** `scripts/harness_parity_phase2.py` hardcodes provider maps to `ollama`/`openrouter` only (`:36-37`, `:418-419`, `:434-435`, `:450-451`); `_provider_settings_status` (`:475`) gates on `name in {"ollama", "openrouter", "cursor"}`, so alibaba/H is misclassified as "not provider-shim scoped" and trivially returns `supported` — a false green that hides H's missing provider surfaces.

## Governance Completeness

- **Root boundary:** all 16 `target_paths` are inside `E:\GT-KB`. Satisfied.
- **Specification Links:** present and substantive; applicability preflight confirms all blocking specs cited.
- **Prior Deliberations:** present (5 DELIBs); authorizing DELIB verified in MemBase (below).
- **Owner Decisions / Input:** present and substantive; owner authorization corroborated by canonical PAUTH + DELIB.
- **Requirement Sufficiency:** present — "Existing requirements sufficient."
- **Quarantine resolution:** `target_paths` correctly EXCLUDES `groundtruth.db` and `harness-state/harness-registry.json` (both dirty and owned by the still-live WI-5199 H-proof report `-003`, whose latest status is NEW). This removes the peer-implementation-report conflict that quarantined the broad GO (`-002`) and forced the `NO-ACTION` at `-003`. H-eligibility mutations are correctly reserved for the WI-5199 lifecycle, and step 5 commits to no MemBase/generated-registry mutation.

## Authorization Chain (verified in canonical MemBase, not the artifact)

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5200-5202-HARNESS-REPAIR-20260711`: `status=active`, `project_id=PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`, no expiry; covers the work items by project membership (`included_work_items=None`).
- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION`: exists, `outcome=owner_decision`, `source_type=owner_conversation`, title "Authorize harness recovery, parity truth, generous envelopes, and H reproof".
- WI-5200 (defect), WI-5201 (defect), WI-5202 (regression): all exist, all `resolution_status=open`, all `project_name=PROJECT-GTKB-GOOSE-HARNESS-ADOPTION` → PAUTH covers by membership. (`approval_state=unapproved` is inert historical metadata per `.claude/rules/backlog-approval-state.md`, not authority.)

## Test Derivation

The Spec-Derived Verification Plan maps each linked specification to concrete pytest/parity commands against test files enumerated in `target_paths` (`test_cloud_harness_base.py`, `test_alibaba_cloud_studio_harness.py`, `test_ollama_harness.py`, `test_openrouter_harness.py`, `test_dispatcher_runtime.py`, `test_lo_harness_turn_budget.py`, `test_harness_parity_phase2.py`, `test_check_harness_parity.py`) plus ruff check/format. Each requirement → verification → expected-result row is present. Satisfies the Mandatory Specification Linkage Gate spec-to-test derivation requirement.

## Prior Deliberations

Deliberation Archive searched ("WI-5200 generous cloud repair authorization envelope") — no prior rejected approach for this repair surfaced; the cited authorizing DELIB was verified by direct lookup. No previously-rejected approach is being revisited without acknowledgement.

## Applicability Preflight

- packet_hash: `sha256:ed65fc95b6a9c18f19d3251e2c0aedcd1d4429a80fd82aa1e8a4ca73b56190f0`
- bridge_document_name: `gtkb-wi5200-5202-generous-harness-repair-narrow`
- operative_file: `bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

| Spec | Severity | Cited |
|------|----------|-------|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes |

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4; may_apply: 1; not_applicable: 0.
- Evidence gaps in must_apply clauses: 0. Blocking gaps (gate-failing): 0. Exit 0.

| Clause | Applicability | Evidence |
|--------|---------------|----------|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | — |

## Advisory Notes for the Implementation Phase (non-blocking)

1. **openrouter routing lacks `max_turns`.** `[routing.openrouter]` currently declares only `timeout_seconds = 240` (no `max_turns`). Implementation step 3 ("configure D/F/H at 600 turns") must add the field to the openrouter routing table (or set the generous value at the provider default), or F will still fall through to the shared default. Cover it in `test_openrouter_harness.py` / `test_check_harness_parity.py`.
2. **Blank-recovery test coverage.** Explicitly test: (a) blank → corrective-user-turn → productive → final; (b) all-blank → eventual `max_turn_exhaustion`/`session_timeout` fail-closed (nonzero); (c) the corrective turn is a `user` turn and NO empty `assistant` block is appended (proposal step 2). The plan references blank-recovery + fail-closed exhaustion; ensure the empty-assistant-block negative assertion is included so the "do not append an empty assistant block" invariant is regression-guarded.
3. **Finalization will require hunk-scoping.** The tree is heavily commingled (249 dirty paths); `.api-harness/routing.toml` and `config/agent-control/harness-capability-registry.toml` already carry unrelated pre-existing hunks (routing.toml's are largely TOML reformatting). Preserve them per step 5 and hunk-scope the focused commit. I did not find another non-terminal implementation report claiming those two files, but confirm at `begin`/finalize time so a peer-report conflict does not re-quarantine this thread.

## Risk Assessment

The generous initial envelopes (600 turns / 900 s operation / 28,800 s session / 29,400 s worker) lengthen the window a non-progressing worker can stay alive. This is an owner-authorized "start generous, tune from telemetry" policy (`DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION` + `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES`). I independently confirmed the semantic fail-closed controls the proposal relies on remain intact in the shared loop (max-turn exhaustion, session-timeout, repeated-no-progress dedup, per-operation transport bounds). Accepted; not a blocker.

---

Loyal Opposition verdict: **GO**. Proceed to implementation under the cited PAUTH; run `implementation_authorization.py begin --bridge-id gtkb-wi5200-5202-generous-harness-repair-narrow` from this latest GO before protected edits.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
