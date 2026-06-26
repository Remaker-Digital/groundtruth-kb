GO
author_identity: cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-review
author_model: composer
author_model_version: composer-2.5
author_model_configuration: Cursor interactive; session role loyal-opposition via ::init gtkb lo

# Bridge Review — gtkb-wi4820-dispatch-eligibility-projection-regen-001

bridge_kind: proposal_review
Document: gtkb-wi4820-dispatch-eligibility-projection-regen
Version: 002 (GO)
Date: 2026-06-26 UTC
Responds-To: bridge/gtkb-wi4820-dispatch-eligibility-projection-regen-001.md (NEW)
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4820

---

## Applicability Preflight

- packet_hash: `sha256:f38ef53a634aed616f5d50d95e7e88b48f6af0732c379c68ff88a89a17adf2f9`
- bridge_document_name: `gtkb-wi4820-dispatch-eligibility-projection-regen`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4820-dispatch-eligibility-projection-regen-001.md`
- operative_file: `bridge/gtkb-wi4820-dispatch-eligibility-projection-regen-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4820-dispatch-eligibility-projection-regen`
- Operative file: `bridge/gtkb-wi4820-dispatch-eligibility-projection-regen-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Review Summary

The proposal correctly identifies a real control-plane false-green: `set-eligibility` writes `config/dispatcher/rules.toml` but leaves `harness-state/harness-registry.json` stale, while `gt bridge dispatch status` merges the overlay at read time and the cross-harness trigger reads the static projection only. Root cause, fix placement, spec linkage, verification plan, and rollback are all adequate for a fast-lane reliability fix under PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING.

## Claim-by-Claim Verification

### 1. Transaction writes rules.toml only (no projection regen)

**Verified.** `bridge_dispatch_transactions._apply_transaction()` writes the rendered TOML and audit record, then returns — no call to `generate_harness_projection()` (`bridge_dispatch_transactions.py:334-347`).

### 2. Projection generator already merges rules.toml overlay

**Verified.** `generate_harness_projection()` loads `load_bridge_dispatch_config(project_root)` and passes it into `build_projection()`, which applies `apply_dispatch_config_to_record()` per harness (`harness_projection.py:295-302`, `209-211`).

### 3. Trigger reads static projection for dispatchability

**Verified.** `_record_can_receive_dispatch()` reads `can_receive_dispatch` from the harness record loaded via `load_harness_projection()`; eligible targets are filtered at `cross_harness_bridge_trigger.py:2912-2921`, `3047`.

### 4. Status command live-merges overlay (false-green path)

**Verified.** `collect_bridge_dispatch_status()` loads the projection then applies `apply_dispatch_config_to_record()` before candidate selection (`bridge_dispatch_config.py:286-288`). Drift is surfaced but not auto-reconciled via `_dispatch_config_consistency_findings()` (`706-725`). Existing test `test_wi4768_status_surfaces_config_projection_drift` documents this asymmetry (`platform_tests/scripts/test_bridge_dispatch_config.py:714-741`).

### 5. Live repo state consistent with drift class

**Verified.** Both `config/dispatcher/rules.toml` and `harness-state/harness-registry.json` currently show harness `E` with `can_receive_dispatch = false`. The proposal's reproduction narrative matches the code path even if live values were toggled during the authoring session.

### 6. Governance metadata

**Verified.** Project Authorization, Project, Work Item, spec links, owner-decision context, and spec-to-test mapping are present and preflights pass.

## Prior Deliberations

- `DELIB-20266134` — owner decision to fix WI-4820 (control plane) first; regen-on-write approach cited in proposal.
- `DELIB-20266107` — one-time Honest-ON reconcile; this proposal systematizes write-through to prevent recurrence.
- `DELIB-20265899` — dispatcher architecture authorization context.
- `DELIB-20266132` / `DELIB-20266133` — dispatcher reliability re-scope context.

## Residual Risks / Implementation Notes (non-blocking)

1. **Centralize regen in `_apply_transaction`.** All mutators (`set_rule`, `add_harness`, `remove_harness`, not only `set_eligibility` / `set_weights` / `set_caps`) share `_apply_transaction`. A single post-write regen hook there avoids future drift on other overlay mutations and matches the "write-through cache" rationale better than three wrapper calls.
2. **Skip regen on `dry_run` and `defer_to_next_session`.** Implicit in current transaction statuses but worth enforcing in code — regen must run only when `status == "applied"` and `mutated is True`.
3. **`cli.py` likely unchanged.** Regen belongs in the transaction module; drop `cli.py` from the implementation diff unless a surfaced warning/message is added to the CLI JSON payload.
4. **Soft-fail logging.** If DB/regen is unavailable, log and extend `DispatchConfigTransactionResult.message` so operators know rules.toml changed but projection refresh failed — preserves graceful degradation without silent false-green.
5. **Trigger integration test.** `test_trigger_target_resolution_reflects_set_eligibility` is acceptable; a focused unit test against the trigger's target-resolution helper (without full spawn cycle) is sufficient if the integration test proves flaky.

## Verdict

**GO.** Implement the write-through projection regen after successful dispatcher-config transactions, with tests proving `harness-registry.json` reflects `set_eligibility` and drift warnings clear. Re-enabling dispatch for harness `E` remains a separate owner-gated step after verification.
