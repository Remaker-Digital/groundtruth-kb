GO

# WI-4991 Headless-Ineligible Dispatch Suppression -- Proposal Review Verdict

bridge_kind: lo_verdict
Document: gtkb-wi4991-headless-ineligible-dispatch-suppression
Version: 002
Author: Loyal Opposition (Ollama, harness D)
Date: 2026-07-03 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4991-headless-ineligible-dispatch-suppression-001.md (NEW)
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-03T10-01-29Z-loyal-opposition-D-b0c0d1
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash
Recommended commit type: fix

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4991-HEADLESS-INELIGIBLE-SUPPRESSION
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4991

---

## Verdict Summary

**GO.** The `-001` NEW proposal correctly identifies a live dispatcher-selection defect: the daemon dispatched Codex A to `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-010.md` despite that latest NO-GO explicitly stating the dispatch loop must be broken. The proposed fix -- extending the existing owner-hold dispatchability pattern to cover explicit headless-ineligibility language in latest verdicts -- is well-scoped, follows established precedent (WI-4885 owner-hold suppression), and targets the correct source files. Both mandatory preflights pass. Prime Builder is authorized to implement within the approved `target_paths`.

## Review Independence

- Proposal (`-001`) author session context: `019f247b-4dc8-7b32-a2ab-25839614d33f` (Codex, harness A, prime-builder).
- Review session context: `2026-07-03T10-01-29Z-loyal-opposition-D-b0c0d1` (Ollama, harness D, loyal-opposition).
- Distinct harnesses (A vs D) and distinct session contexts. Review independence satisfied.

## Applicability Preflight

- packet_hash: `sha256:ba5fb8ed714ad9aa90ab97ff489f33a7151fd98d6a98b88215ff4ca792055785`
- bridge_document_name: `gtkb-wi4991-headless-ineligible-dispatch-suppression`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4991-headless-ineligible-dispatch-suppression-001.md`
- operative_file: `bridge/gtkb-wi4991-headless-ineligible-dispatch-suppression-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4991-headless-ineligible-dispatch-suppression`
- Operative file: `bridge/gtkb-wi4991-headless-ineligible-dispatch-suppression-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 0 (pass).

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | -- | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | -- | blocking | blocking |

## Findings

### Positive Confirmations

1. **Live defect correctly identified.** The `-010` NO-GO for WI-4929 (Claude B, 2026-07-02) explicitly states "The dispatch loop must be broken. Every headless Codex auto-dispatch for this thread produces a REVISED entry documenting the same ACL deny; every LO review issues NO-GO; the dispatcher re-queues for Codex; the cycle repeats." The daemon nonetheless selected this thread for Codex A dispatch. The proposal's problem statement is accurate and evidenced.

2. **Approach follows established precedent.** WI-4885 (VERIFIED at `-004`) implemented owner-hold dispatch suppression using the same mechanism: a regex pattern match in `notify.py` -> `CLASSIFICATION_OWNER_HOLD` -> `dispatchable=False` in `disposition.py`. This proposal extends that pattern with a new classification for headless-ineligibility language. The implementation surface is well-understood and the risk of regression is low.

3. **Target paths are correct.** The five target files are the same core files modified for WI-4885, plus the dispatcher runtime test. No new architectural surfaces are introduced.

4. **Scope is appropriately bounded.** The proposal explicitly preserves manual Prime visibility (same as owner-hold) and only suppresses unattended headless auto-dispatch. It does not change topology, credentials, or harness boundaries.

5. **Specification linkage is comprehensive.** All mandatory specs are cited with concrete relevance. The proposal correctly links to the governing bridge-authority, implementation-proposal, and verified-testing specs.

### Observations (non-blocking)

1. **Pattern-match fragility.** Like the existing owner-hold mechanism, the proposed headless-ineligibility detection relies on natural-language pattern matching in verdict bodies. This is inherently less robust than a structured metadata field. However, the proposal follows the established WI-4885 pattern, and a structured-field approach would be a separate architectural change. The implementation should include a clear docstring enumerating the exact patterns matched so future maintainers can audit the match surface.

2. **Test coverage should include the live incident.** The implementation report should include a test case that reproduces the exact WI-4929 `-010` scenario: a NO-GO verdict containing "dispatch loop must be broken" language should result in `dispatchable=False` for that thread.

## Prior Deliberations

- `bridge/gtkb-wi4885-owner-hold-dispatch-suppression-001.md` through `-004.md` -- verified precedent for the owner-hold dispatch-suppression mechanism this proposal extends.
- `bridge/gtkb-wi4929-codex-sessionstart-timeout-alignment-010.md` -- the live NO-GO that triggered this WI; contains the exact "dispatch loop must be broken" language the proposal targets.
- `bridge/gtkb-wi4977-headless-dispatch-stability-008.md` -- verified exact-thread/LO-lease/Ollama advancement repair; this proposal is a follow-on selector-classification defect, not a duplicate.
- `bridge/gtkb-wi4988-direct-harness-launch-guard-006.md` -- verified direct harness launch guard; this proposal preserves the same no-direct-fallback rule.
- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` -- owner directive for stable unattended headless bridge processing.
- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` -- owner prohibition on direct harness-to-harness interaction.

## Specifications Carried Forward

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Implementation Guidance (post-GO)

After this GO, Prime Builder should:

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4991-headless-ineligible-dispatch-suppression` and confirm the packet shows `-001` (NEW) and the WI-4991 PAUTH.
2. Implement in `disposition.py`: add a new classification constant (e.g., `CLASSIFICATION_HEADLESS_INELIGIBLE = "headless_ineligible"`) and update `dispatchable_for_status` to return `False` when `classification == CLASSIFICATION_HEADLESS_INELIGIBLE` for GO/NO-GO statuses.
3. Implement in `notify.py`: add a new regex (e.g., `_HEADLESS_INELIGIBLE_RE`) matching explicit headless-ineligibility language patterns such as "dispatch loop must be broken", "do not re-dispatch to Codex headless", and equivalent phrasings. Wire it into the classification derivation so that matching verdicts receive `CLASSIFICATION_HEADLESS_INELIGIBLE`.
4. Add tests in `test_bridge_notify.py` covering: (a) detection of headless-ineligibility language, (b) resulting `dispatchable=False`, (c) non-interference with normal NO-GO dispatch, (d) the exact WI-4929 `-010` reproduction case.
5. Add integration tests in `test_gtkb_dispatcher_daemon.py` and `test_dispatcher_runtime.py` confirming the daemon/runtime do not select headless-ineligible threads for dispatch.
6. Run `ruff check` AND `ruff format --check` separately on all changed Python before filing the implementation report.

## Commands Executed

```
python scripts/bridge_claim_cli.py claim gtkb-wi4991-headless-ineligible-dispatch-suppression
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4991-headless-ineligible-dispatch-suppression
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4991-headless-ineligible-dispatch-suppression
```
