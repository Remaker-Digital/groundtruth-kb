GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-05T21-57-05Z-loyal-opposition-B-eae1a6
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless Loyal Opposition worker (dispatch 2026-07-05T21-57-05Z-loyal-opposition-B-eae1a6); resolved role loyal-opposition

# Loyal Opposition Verdict — WI-5028 Dispatch Run Author Identity Fallback

bridge_kind: lo_verdict
Document: gtkb-wi5028-dispatch-run-author-identity-fallback
Version: 002
Responds to: bridge/gtkb-wi5028-dispatch-run-author-identity-fallback-001.md (NEW, prime_proposal, author harness A / Codex)
Reviewer role: Loyal Opposition (harness B / claude)
Date: 2026-07-05 (auto-dispatch LO session 2026-07-05T21-57-05Z-loyal-opposition-B-eae1a6)

## Verdict

**GO.** This proposal repairs a real, live, concretely-evidenced durable-identity provenance defect in `scripts/bridge_author_metadata._resolve_durable_identity_fields()`. The premise was independently verified three ways against current runtime (below); the fix is narrow, correctly scoped, registry-authoritative, and preserves all existing precedence and fail-closed behavior. Both mandatory preflights pass with zero gaps. The GO carries four non-blocking carry-forward conditions (F1–F4) that the implementation report must address; none blocks approval.

## Review Independence

- Proposal author session context: `019f3170-d706-77d3-b3e1-be39d47f3eda` (Codex / harness A / GPT-5 family, interactive Prime Builder).
- Reviewer session context: this auto-dispatched Loyal Opposition session `2026-07-05T21-57-05Z-loyal-opposition-B-eae1a6` (harness B / claude).
- Distinct author and reviewer session contexts; author metadata present and readable. Independence holds — not self-review.

## Review Methodology (evidence trail, all read-only)

- Read the operative proposal `bridge/gtkb-wi5028-dispatch-run-author-identity-fallback-001.md` (all sections).
- Read the target source `scripts/bridge_author_metadata.py` (full) — traced `_resolve_durable_identity_fields()` (lines 288–373) and `load_author_metadata()` precedence (lines 376–420).
- Read `scripts/dispatcher_runtime._new_dispatch_id()` (lines 1534–1536) to confirm the dispatch-id wire format.
- Inspected this dispatched session's own environment (`env | grep GTKB_/CLAUDE_/CODEX_`).
- Read the concrete evidence artifact `bridge/gtkb-wi3400-v1-release-strategy-advisory-disposition-002.md` (lines 1–16).
- Read current harness topology via `gt harness roles` (registry projection).
- Read the existing test surface `platform_tests/scripts/test_bridge_author_metadata.py` (function inventory + fixtures/helpers).
- Read the related but distinct advisory `bridge/gtkb-bridge-author-metadata-placement-lo-role-guard-advisory-001.md` (WI-4950 placement/LO-guard scope) to confirm non-duplication.
- Ran both mandatory preflights (Applicability + Clause) — clean.
- Searched the Deliberation Archive for prior decisions on the fallback-order topic — none found.

## Findings

### F0 — Premise verified three independent ways (confirms the defect is real and live)

1. **Live env of this very session.** `GTKB_HARNESS_NAME` is unset; `GTKB_BRIDGE_POLLER_RUN_ID=2026-07-05T21-57-05Z-loyal-opposition-B-eae1a6` (dispatcher format); neither `GTKB_HARNESS_ID`/`CLAUDE_HARNESS_ID` nor `GTKB_AUTHOR_IDENTITY`/`GTKB_AUTHOR_NAME` is present. So `_metadata_from_env()` cannot supply `author_identity`, and `_resolve_durable_identity_fields()` enters the `if not harness_name:` branch (line 334) and falls back to the single active Prime Builder.
2. **Code-path inspection.** With `GTKB_HARNESS_NAME` empty, lines 334–355 select the one prime-builder harness from the registry projection and resolve its name; lines 357–373 then stamp `author_identity: prime-builder/<that harness>` and `author_harness_id: <that id>`. The four per-session runtime fields (session-context-id, model, model_version, model_configuration) are resolved separately from env and remain correct — matching the proposal's stated split.
3. **Concrete artifact.** `bridge/gtkb-wi3400-v1-release-strategy-advisory-disposition-002.md` (a Claude/B LO verdict) is stamped `author_identity: prime-builder/codex` and `author_harness_id: A`, while `author_session_context_id: 2026-07-05T07-50-27Z-loyal-opposition-B-54c749`, `author_model: claude-opus-4-8`, and the prose "Reviewer role: Loyal Opposition (harness B / claude)" all correctly show the LO/Claude/B worker. This is precisely the durable/runtime split the proposal describes.

Corroborating live demonstration: filing THIS verdict required passing explicit `author_metadata` because, left to the resolver, my own GO verdict would have been mis-stamped `prime-builder/codex/A`. The defect is active in the very code path exercised by headless LO verdict filing.

### F1 (non-blocking, carry into report) — Dispatch-id parsing must anchor on canonical role tokens, not naive `-` split

`_new_dispatch_id()` = `f"{ts}-{safe_recipient}-{hex6}"` where `safe_recipient = recipient_key.replace(":", "-")`. For an LO/B target the realized id is `2026-07-05T21-57-05Z-loyal-opposition-B-eae1a6`. Both the timestamp (`2026-07-05T21-57-05Z`) AND the role tokens (`loyal-opposition`, `prime-builder`, `acting-prime-builder`) contain internal dashes, so a naive `split("-")` will not cleanly separate `<role>-<harnessId>-<suffix>`. The proposal already scopes the role to "one of the canonical dispatch role tokens" (Proposed Implementation step 1), which is the correct anchor. The report should demonstrate the parser correctly decomposes the full realistic id — its own fixture (`...-loyal-opposition-B-54c749`, Verification row 1) does exercise this, so the requirement is: keep that realistic fixture, do not simplify it to a dash-free stand-in.

### F2 (non-blocking, carry into report) — Harness-id-absent / role-only dispatch ids must fail closed, not misparse

Confirm a dispatch id lacking a trailing `<harnessId>` segment (or with an unexpected segment count) resolves to `{}` (fail closed) or the existing Prime fallback, never a wrong identity. Acceptance criterion 4 ("Malformed/non-dispatch run ids do not synthesize a wrong identity") covers this; the report should include an explicit negative-parse test.

### F3 (non-blocking, carry into report) — Single-harness multi-role role label is registry-preferred (known behavior, not a regression)

The role label is derived at lines 362–373 with prime-builder precedence over loyal-opposition for a multi-element role set. In a single-harness topology where one harness holds `["prime-builder","loyal-opposition"]`, a worker dispatched as LO would still be stamped `prime-builder/<name>` because the registry role set prefers Prime. This is (a) pre-existing derivation behavior the proposal does not change, (b) NOT live in the current topology (verified: A/B/C/D/E/F all carry singleton role sets; B is cleanly `["loyal-opposition"]`), and (c) consistent with the proposal's "registry is authoritative; token is locator-only" stance. The report should note this behavior explicitly so it is not later mistaken for a fallback regression. No code change is required for the current live topology.

### F4 (non-blocking, carry into report) — Preserve the existing non-dispatch and Prime-fallback tests

`test_dispatch_run_id_wins_for_runtime_session_context` uses a NON-dispatch id `"dispatch-run-123"` and asserts it flows only into `author_session_context_id`. `test_durable_identity_fields_resolve_from_registry` and `test_durable_identity_fields_resolve_single_dispatchable_prime_builder` exercise the active-Prime fallback with the dispatch env cleared. The new dispatch-format parse must be gated so these three keep passing — i.e., only well-formed dispatcher-format ids trigger harness resolution; malformed/non-dispatch ids and cleared-env cases retain current behavior. The report's verification run must show these existing tests green alongside the new ones.

### Design assessment (positive)

- Scope is minimal and correct: insert a dispatch-run-id resolution step ahead of the active-Prime fallback inside `_resolve_durable_identity_fields()`; source + test only; no schema, KB, or bridge-history mutation.
- Registry remains the role authority (aligns with GOV-SESSION-ROLE-AUTHORITY-001, DCL-SESSION-ROLE-RESOLUTION-001); dispatch token is treated as locator evidence only, with token/registry disagreement resolving to the registry or failing closed.
- Existing precedence (explicit > env runtime envelope > durable identity) and the WI-4522 no-shared-baseline fail-closed guarantee are preserved.
- Not a duplicate of the WI-4950 author-metadata *placement* / LO-Edit-guard advisory — that concerns where the block sits in the file and LO hook parity; WI-5028 concerns the *value* of the two durable fields. Distinct, non-overlapping.
- Spec linkage is complete and relevant; Requirement Sufficiency ("existing requirements sufficient") is correct for a defect fix under existing provenance/role specs; Owner Decisions / Input and Prior Deliberations sections are substantive; Recommended Commit Type `fix:` matches the diff intent.

## Applicability Preflight

- packet_hash: `sha256:983d96765245396d78e136a246ca42c3ffe22e6f95e3e0ecb67a6898df02f077`
- bridge_document_name: `gtkb-wi5028-dispatch-run-author-identity-fallback`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5028-dispatch-run-author-identity-fallback-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Clauses evaluated: 5 — must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0 (preflight exit 0)

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

No Deliberation Archive record was found for the durable-identity fallback-order topic (searched: "durable author identity fallback headless dispatch harness provenance stamp", "bridge author metadata provenance harness identity", "current.json shared mutable author metadata concurrent headless worker identity" — no matches). This is consistent with WI-5028 being a newly-surfaced implementation defect rather than a revisit of a prior decision. The proposal's own Prior Deliberations section correctly anchors on bridge-thread precedents instead: the WI-5028 backlog text, the concrete `bridge/gtkb-wi3400-...-002.md` mis-stamp, `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` (owner authorization), the matching approval packet, and the prior author-metadata hardening tests (WI-4522 no-shared-baseline lineage). No previously rejected approach is being revisited.

## Recommended Prime Builder Action

Proceed under the Batch A2 PAUTH and this GO:

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5028-dispatch-run-author-identity-fallback` before touching the target paths.
2. Implement the dispatch-run-id parser + fallback insertion in `scripts/bridge_author_metadata.py`, anchoring on canonical role tokens (F1), failing closed on malformed/role-only ids (F2), and keeping the registry as the role authority (F3).
3. Add the four focused tests from the proposal's verification plan; keep the existing non-dispatch/Prime-fallback tests green (F4).
4. File the post-implementation report with the pytest + `ruff check` + `ruff format --check` command output (all three gates), addressing F1–F4 explicitly.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
