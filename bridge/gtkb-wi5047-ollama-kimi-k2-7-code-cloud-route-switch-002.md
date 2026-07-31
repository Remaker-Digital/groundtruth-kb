GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T16-16-02Z-loyal-opposition-B-07b796
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; role loyal-opposition; effort max

bridge_kind: lo_verdict
Document: gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch
Version: 002
Date: 2026-07-06 UTC
Responds to: bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-001.md

# Loyal Opposition Review — WI-5047 Ollama/D → Kimi K2.7 Code cloud route switch (GO)

## Verdict

`GO`. The proposal is well-formed, correctly authorized, and its premise is verified against live runtime state. Every load-bearing claim was independently confirmed against canonical MemBase and on-disk config rather than trusted from the proposal's own evidence sections. Target-path scope is complete for the surfaces that would actually break, and both mandatory preflights pass clean. Implementation may proceed within the PAUTH scope; see the non-blocking implementation-phase notes below.

## Reviewer independence

Reviewer harness B (claude), session context `2026-07-06T16-16-02Z-loyal-opposition-B-07b796`. Author harness A (codex), session context `2026-07-06-codex-pb-ollama-kimi-switch`. Distinct session contexts; independence gate satisfied. Latest thread status was NEW with a single version (`-001`) on disk — no peer verdict race.

## Review methodology / evidence inspected

- Read the operative proposal `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-001.md` (all sections).
- Confirmed live current-state (NOT trusting the proposal's Current State Evidence):
  - `.api-harness/routing.toml`: `[routing.ollama].default_model = "deepseek-v4-pro-cloud"`; all three `[routing.ollama.skills]` (bridge-review, verification, implementation) = `deepseek-v4-pro-cloud`; both route keys `kimi-k2-7-code-cloud` (`kimi-k2.7-code:cloud`) and `deepseek-v4-pro-cloud` (`deepseek-v4-pro:cloud`) defined.
  - `harness-state/harness-registry.json`: harness D headless argv contains `--model deepseek-v4-pro-cloud`; role `loyal-opposition`; status `active`.
  - `config/dispatcher/rules.toml`: `[budget.harnesses.D] model = "deepseek-v4-pro-cloud"`.
  - `groundtruth-kb/.venv/Scripts/gt.exe harness roles`: A=prime-builder, B=loyal-opposition, D=ollama/loyal-opposition (argv still deepseek). Topology consistent with the proposal.
  - NOTE: the session-start canonical-terminology context described the current Ollama route as `kimi-k2-7-code-cloud`; that narrative surface is STALE. Live config is deepseek, so the switch is a real, non-no-op change. (Flagged as a hygiene observation below.)
- Verified the authorization chain in MemBase (`groundtruth.db`, read-only):
  - `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD`: outcome=`owner_decision`, source_type=`owner_conversation`; content states "Mike confirmed: switch Ollama/D headless dispatch to the Ollama cloud model slug `kimi-k2.7-code:cloud` and create the governed follow-on proposal." Explicitly supersedes the prior DeepSeek decision without deleting it.
  - `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD`: exists, outcome=`owner_decision` (prior, properly superseded).
  - `WI-5047`: exists, resolution_status=`open`, project=`PROJECT-HARNESS-EQUIVALENCE-PHASE-3`, source_deliberation=the owner decision.
  - `TEST-11290`: exists, spec_id=`ADR-CROSS-HARNESS-PARITY-001` (auto-created stub; `test_file` is None — see implementation note 1).
  - `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5047-OLLAMA-KIMI-K2-7-CLOUD-20260706`: status=`active`, expires_at=None, `included_work_item_ids=["WI-5047"]`, owner_decision_deliberation_id matches the owner decision, allowed_mutation_classes=`[config, test, generated_projection, membase_record, governance_evidence]`, scope_summary matches the proposal.
  - `PROJECT-HARNESS-EQUIVALENCE-PHASE-3`: status=`active`.
  - Cited specs all exist: `ADR-CROSS-HARNESS-PARITY-001` (accepted), `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (all present).
  - Prior deliberations cited (`DELIB-202665282`, `DELIB-202665283` for WI-4964) both exist.
- Ran the two mandatory preflights against the operative file (both clean; sections below).

## PAUTH mutation-class ↔ target_paths coverage

Every target_path maps to an allowed mutation class, so the implementation-start gate will admit the whole set:

| target_path | mutation class |
| --- | --- |
| `.api-harness/routing.toml` | config |
| `config/dispatcher/rules.toml` | config |
| `harness-state/harness-registry.json` | generated_projection |
| `groundtruth.db` | membase_record |
| `platform_tests/scripts/test_verify_ollama_dispatch.py` | test |
| `groundtruth-kb/tests/test_doctor.py` | test |
| `groundtruth-kb/tests/test_doctor_ollama.py` | test |

## Target-paths completeness (adversarial blast-radius check)

I grepped the full repository for `deepseek-v4-pro-cloud` / `deepseek-v4-pro:cloud` (124 files, mostly bridge audit-trail / `.harness-tmp` scratch). Live production surfaces referencing the deepseek route that are NOT in target_paths were each examined to confirm they will not break after the switch:

- `platform_tests/scripts/test_dispatcher_runtime.py` (~line 4247, 4267, 4278, 4437): writes its OWN inline routing.toml + registry fixtures and asserts `model_hint == "deepseek-v4-pro-cloud"` against that self-built fixture. Hermetic (does not read live config) → will not break. Correctly omitted.
- `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py` (lines 31-35, 105-109, 163): builds inline `[budget.harnesses.D]` + registry fixtures and asserts against them. Hermetic → will not break. Correctly omitted.
- `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py` (line 40) and `config/governance/gate-fp-corpus.toml` (lines 78/106/134): use `ollama run deepseek-v4-pro:cloud` as an example BLOCKED-launch string testing the launch-block pattern; unrelated to the active route selection → will not break; correctly left unchanged.

Reverse direction (files in target_paths that did NOT match the deepseek grep, confirming they need no deepseek→kimi text edit):
- `groundtruth-kb/tests/test_doctor_ollama.py` already uses `kimi-k2-7-code-cloud`/`kimi-k2.7-code:cloud` in its hermetic `_write_clean_ollama_fixtures` (lines 124-140, 306). Including it in target_paths is harmless conservative scoping.
- `doctor.py` `_check_harness_metadata_freshness` (WI-4700, a doctor `fail` condition) is correctly NOT in target_paths: it flags any `:cloud` route whose description makes a stale-local claim; both deepseek and kimi are `:cloud` routes, so applicability is unchanged, and freshness is proven by marker PHRASES (`cloud-routed`, `current route`, and the literal `kimi-k2-7-code-cloud` is already in `fresh_markers`, lines 1174-1180), not by the specific model name. The switch keeps this check green provided scope item 4 keeps the harness D description referencing a fresh marker (naturally satisfied by pointing it at the kimi route).

Conclusion: target_paths are complete for every live surface that would break.

## Specification linkage

Specification Links section is present and cites the relevant governing surface (cross-harness parity, centralized dispatch, dispatcher control, project-authorization, bridge authority, spec-linkage/spec-derived-testing DCLs, artifact-oriented governance, isolation placement, standing backlog). The Specification-Derived Verification Plan maps each cited spec to a concrete verification. Prior Deliberations and Owner Decisions / Input sections are both present and substantive.

## Applicability Preflight

- packet_hash: `sha256:638861696cf7539007bd7d129e8da8794a395eb97fe9667eff58c4eca0776fba`
- bridge_document_name: `gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch`
- operative_file: `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0; Blocking gaps (gate-failing): 0 (exit 0 = pass)

| Clause | Applicability | Evidence found | Severity |
|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | — | blocking |

## Prior deliberations

The relevant prior-decision history is the two Ollama/D model-selection owner decisions (`DELIB-20260706` current, `DELIB-20260702` prior/superseded) plus the WI-4964 pinning GO/VERIFIED records (`DELIB-202665283`, `DELIB-202665282`). No prior deliberation rejected switching Ollama/D to Kimi; this is the owner's explicit forward decision, properly superseding the earlier DeepSeek pin. No revisit-of-a-rejected-approach concern.

## Non-blocking notes for the implementation phase (NOT GO conditions)

1. TEST-11290 is an auto-created stub with `test_file = None`. The Specification-Derived Verification Gate (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`) will require a concrete executed test at VERIFIED time. Bind TEST-11290 to a real assertion (e.g., a case in `platform_tests/scripts/test_verify_ollama_dispatch.py` asserting the DEFAULT Ollama bridge-review route resolves to `kimi-k2-7-code-cloud`/`kimi-k2.7-code:cloud`), and include the exact command + output in the implementation report, or the report risks a NO-GO on spec-derived coverage.
2. `groundtruth.db` is in target_paths (the harness-registry.json is a projection of the MemBase harnesses table, so updating harness D argv requires a `membase_record` mutation, then regenerating the projection). This is legitimate at GO. Be aware of the known commingled-shared-DB VERIFIED-finalization friction: keep the DB mutation minimal and scoped to harness D, and prefer the governed harness writer/projection path (scope item 3) plus the governed dispatcher-control path (scope item 4) so the change is auditable and the eventual finalize is clean.
3. After the switch, confirm `groundtruth-kb/.venv/Scripts/python.exe -m pytest` on the doctor and dispatch-runtime test modules still passes, and run `gt project doctor` to confirm `_check_harness_metadata_freshness` stays green (it should, since the harness D description will reference the kimi fresh-marker). Include that evidence in the report.
4. Hygiene-only (optional, out of this WI's scope; do not expand target_paths for it): the two hermetic test fixtures noted above (`test_dispatcher_runtime.py`, `test_bridge_state_report_cli.py`) use `deepseek-v4-pro-cloud` as their example fixture value and the canonical-terminology.md narrative surface describes the current route as kimi (currently stale vs live deepseek). These will self-correct in narrative once kimi is the live default, but a future hygiene pass could align the example fixture values. Capturing as a backlog observation, not a change request here.

## Owner Decisions / Input

This verdict depends on no new owner decision. Owner authorization for the change itself is `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` (verified above), carried by the active PAUTH; no further owner input is required for implementation to proceed within that scope.
