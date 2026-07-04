GO

# Loyal Opposition Review — GO

bridge_kind: lo_verdict
Document: gtkb-wi4983-prime-no-go-dispatch-routing
Version: 002
Date: 2026-07-04 UTC
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-04T06-27-27Z-loyal-opposition-D-86d74c
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

## Verdict: GO

The proposal correctly identifies a real defect: the Prime Builder dispatcher rule in `config/dispatcher/rules.toml` was narrowed from `["GO", "NO-GO"]` to `["GO"]` during the WI-5006 NO-ACTION commit, leaving latest `NO-GO` bridge entries unreachable by headless Codex/A PB dispatch. The proposed fix — restoring `["GO", "NO-GO"]` to the Prime rule while preserving `NO-ACTION` as LO-only — is minimal, correct, and well-scoped.

## Evidence Confirmed

1. **Live config drift confirmed.** `config/dispatcher/rules.toml` line 101 reads `statuses = ["GO"]` for the `bridge-prime-builder-default` rule. The LO rule correctly has `["NEW", "REVISED", "NO-ACTION"]`.

2. **Live NO-GO backlog confirmed.** `scan_bridge.py --role prime-builder` reports two live latest `NO-GO` threads: `gtkb-wi4975-claimed-path-subpath-overmatch` (010) and `gtkb-wi5002-codex-dotdir-sandbox-acl-correction` (012). These are Prime-actionable by role contract but unreachable by the current dispatcher rule.

3. **Role contract confirmed.** `.claude/rules/prime-builder-role.md` states "Prime Builder acts only on latest `GO` or `NO-GO` entries for its harness." `.claude/rules/file-bridge-protocol.md` line 365 states "Periodically scan TAFE/dispatcher bridge state for GO, NO-GO, or ADVISORY." The PRIME-BUILDER-STARTUP-OVERLAY.md confirms "Prime Builder acts only on latest `GO` or `NO-GO` entries." The dispatcher rule is out of sync with these authoritative role contracts.

4. **Test parity gap confirmed.** `platform_tests/scripts/test_cross_harness_protocol_parity.py` line 92 asserts `prime_rule["statuses"] == ["GO"]`, which encodes the current broken state rather than the correct contract. This test must be updated as part of the fix.

## Applicability Preflight

- packet_hash: `sha256:35e6bfebb52cadaea7cbbab0f92588ea5c61ccc155451266a5d1e5aeff2fffa0`
- bridge_document_name: `gtkb-wi4983-prime-no-go-dispatch-routing`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability (Slice 2)

- Clauses evaluated: 5
- must_apply: 4, may_apply: 1
- Blocking gaps: 0
- Mode: mandatory — PASS

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — The dispatcher must select role-correct bridge work from governed config.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — Latest bridge status determines role actionability; Prime may act on `GO` and `NO-GO`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — The live routing defect is preserved as a governed work item with PAUTH, proposal, tests, and verification evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Proposal links concrete config repair to bridge/dispatcher specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verification must prove the role/status matrix, not merely that `rules.toml` changed.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Proposal carries machine-readable PAUTH, project, work-item, and target-path metadata.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — All changes remain in GT-KB platform config/tests.
- `GOV-STANDING-BACKLOG-001` — WI-4983 remains the governing backlog record.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex/A remains the Prime dispatch target; no direct harness fallback.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Regression triggered by lifecycle status addition; repaired as lifecycle-aware dispatch behavior.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` — Fix preserves prohibition on direct harness-to-harness invocation.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` — Owner-directed goal to keep testing and fixing until bridge/headless dispatch is stable with Codex/A as PB and Claude/B, Antigravity/C, and Ollama/D as LO targets.
- `DELIB-HARNESS-OPS-NO-ACTION-FIRST-CLASS-BRIDGE-STATUS-20260702` — Establishes `NO-ACTION` as a first-class bridge status.
- `DELIB-HARNESS-NO-ACTION-LO-ACTIONABLE-BRIDGE-ROUTING-20260702` — Establishes latest `NO-ACTION` as LO-actionable and not Prime-actionable.

## Review Notes

- The fix is a one-line config change plus test assertion updates. Risk is minimal.
- The proposal correctly preserves `NO-ACTION` as LO-only — the LO rule already has `["NEW", "REVISED", "NO-ACTION"]` and is not being changed.
- The test at `test_cross_harness_protocol_parity.py:92` currently asserts the broken state; the implementation must update this assertion to `["GO", "NO-GO"]`.
- The `test_bridge_dispatch_config.py:1386` already tests `set_rule` with `("GO", "NO-GO")` — this test will pass once the config is corrected.
- No new specifications are needed; the existing role contracts already define the correct behavior.
