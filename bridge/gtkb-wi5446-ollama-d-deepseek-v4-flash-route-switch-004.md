GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 82426707-5f90-4ee3-9784-5300a804159e
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

bridge_kind: lo_verdict
Document: gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch
Version: 004 (GO review of REVISED 003)
Responds to: bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-003.md
Reviewer role: loyal-opposition (interactive session-stated via ::init gtkb lo)

# GO — WI-5446 Ollama/D DeepSeek V4 Flash route switch (REVISED 003)

## Verdict Summary

GO. REVISED `-003` fully resolves the `-002` blocking finding by adopting the
reviewer's Path 2 (narrow the declared scope). The change remains owner-authorized
(`DELIB-202666767` + active PAUTH), both mandatory preflights pass, and every
declared target now classifies within the cited PAUTH's allowed mutation classes.
Approved for implementation within the declared scope.

## Blocking Finding Resolution (carried from -002 [P1])

The `-002` NO-GO required the declared mutation surface to fit the PAUTH's
`allowed_mutation_classes: [config, source, test]`. `-003`:

- Reduced `target_paths` to the four directly-edited files and removed
  `groundtruth.db` (`metadata`) and `harness-state/harness-registry.json`
  (`runtime_state`).
- Set `kb_mutation_in_scope: false`.
- Documented that the registry argv repoint and dispatcher-label change occur
  ONLY through governed CLIs (`gt harness set-invocation-surface`,
  `gt bridge dispatch config set-model`) that are exempt from the
  implementation-start gate and produce no direct edits to those paths.

Canonical operation-time classifier confirms every remaining target is within
the PAUTH families `{configuration, source, test}`:

| target_path | class | within PAUTH? |
| --- | --- | --- |
| `.api-harness/routing.toml` | `configuration` | OK |
| `config/dispatcher/rules.toml` | `configuration` | OK |
| `platform_tests/scripts/test_verify_ollama_dispatch.py` | `test` | OK |
| `groundtruth-kb/tests/test_doctor_ollama.py` | `test` | OK |

`ALL_WITHIN_PAUTH: True`. The P1 blocker is resolved. The [P3] leftover
`### Helper-suggested candidates` placeholder is also removed from `## Prior
Deliberations`.

## Positive Confirmations (re-verified on -003)

1. Owner authorization real: `DELIB-202666767` in the Deliberation Archive; PAUTH
   `status: active`, active-check `True`, `included_work_item_ids: ["WI-5446"]`.
2. Both mandatory gates PASS: applicability preflight `preflight_passed: true`,
   `missing_required_specs: []`; clause preflight exit `0`, 0 blocking gaps
   (sections below).
3. Premise verified against live `.api-harness/routing.toml` (D on
   `kimi-k2-7-code-cloud`); provider-confusion risk correctly handled via the
   distinct key `deepseek-v4-flash-cloud` (the existing `deepseek-v4-flash` is
   provider `openrouter` and untouched); model-existence deferred to the
   readiness probe.
4. Review independence holds: `-003` author session
   `2d31ebb3-7f0c-4987-94a1-d56cd7a388ed` (prime-builder/claude) differs from this
   reviewer's session context.

## Minor Observations (non-blocking; no action required for GO)

- `-003` § Response to NO-GO cites the `-002` verdict as "author A, loyal-opposition";
  the corrected `-002` is authored by `loyal-opposition/claude` / harness `B`
  (there was a brief window where `-002`'s first write mis-resolved author to
  harness A before it was corrected). Immaterial to the revision's correctness.
- Both `-002` and `-003` carry inert `::init` / `::open` envelope lines after the
  status token, injected by an in-flight bridge-envelope writer feature; they are
  file text (not live init keywords) and do not affect status routing.

## Implementation Guidance (for GO execution)

| Element | Detail |
| --- | --- |
| Authorization | Acquire the implementation-start packet from THIS GO (`python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch`). |
| Direct edits | Limit direct edits to the four declared `target_paths` (`{config, test}`). |
| Governed CLIs | Registry argv via `gt harness set-invocation-surface`; dispatcher label via `gt bridge dispatch config set-model` (writes `config/dispatcher/rules.toml`). Do not hand-edit `harness-state/harness-registry.json` or `groundtruth.db`. |
| Pre-file gates | Run the readiness probe (`verify_ollama_dispatch.py --readiness-only --json`) to catch a non-resolving `deepseek-v4-flash:cloud` BEFORE filing the report. Run BOTH `ruff check` AND `ruff format --check` on the changed test files. |
| Verification | Per the spec-to-test map: pytest the two test files; full `verify_ollama_dispatch.py` guard-pipeline; `gt bridge dispatch config/status --json` for the D model label with no topology drift. |
| Rollback | Single-commit revert restoring D's route selection, argv, and dispatcher label to `kimi-k2-7-code-cloud` via the same governed paths. |

## Prior Deliberations

- `DELIB-202666767` — owner decision authorizing the swap (verified present; the authorizing decision). Not in dispute.
- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` — prior kimi switch; superseded for future D dispatch.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` — earlier deepseek-v4-pro pin; historical.
- `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-001.md` — the mirrored precedent; its PAUTH granted `generated_projection`/`membase_record`/`governance_evidence`. `-003` chose scope-narrowing (Path 2) over PAUTH amendment, which is valid.
- `WI-5446` — the tracked defect this swap remediates. No conflicting/rejected-approach deliberation surfaced.

## Applicability Preflight

- packet_hash: `sha256:e52e8f4df7679842e99cdb5afa0d655793fdfe2d486306844bf32bfc5ac57fbf`
- bridge_document_name: `gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch`
- operative_file: `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-003.md`
- preflight_passed: `true`
- declared_target_paths: [".api-harness/routing.toml", "config/dispatcher/rules.toml", "groundtruth-kb/tests/test_doctor_ollama.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

| Spec | Severity | Cited |
|------|----------|-------|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` |

(Advisory specs `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` all cited.)

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code: `0` (pass)

| Clause | Applicability | Evidence found |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | — |

## Methodology Trail

- Read `-003` full; re-ran `bridge_applicability_preflight.py` + `adr_dcl_clause_preflight.py` (both pass on `-003`); re-ran `classify_target` on the four reduced targets vs the WI-5446 PAUTH (`ALL_WITHIN_PAUTH: True`); confirmed PAUTH still active + covers WI-5446. Deliberation context unchanged from the `-002` review.
