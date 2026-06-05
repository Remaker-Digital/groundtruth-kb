NO-GO

# Loyal Opposition Review - Envelope Open Disclosure Refactor (NO-GO)

bridge_kind: loyal_opposition_verdict
Document: gtkb-envelope-disclosure-ui-impl
Version: 002
Reviewer: Loyal Opposition (Codex, harness A, durable role per registry: `[loyal-opposition]`)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-envelope-disclosure-ui-impl-001.md
Verdict: NO-GO
Work Item: WI-4298
Recommended commit type: docs(bridge)

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-06-04T20-56-13Z-loyal-opposition-d73be9

## Verdict

NO-GO.

The mandatory bridge applicability and clause preflights pass, and the live project authorization covers WI-4298 with the required `source` and `test_addition` mutation classes. The proposal still cannot receive GO because it claims to implement `SPEC-ENVELOPE-DISCLOSURE-UI-001`'s open-disclosure section in full while explicitly preserving the inline `Wrap-Up Trigger Commands` section that the spec says must move out of the startup disclosure. The spec-derived verification plan also omits any test for that move requirement.

This is a proposal-correctness and test-mapping defect under `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, not a mechanical preflight failure.

## Prior Deliberations

- `DELIB-20260872` - owner approved envelope PAUTH v2, adding WI-4298/WI-4299/WI-4301 and `source`/`test_addition`/`hook_upgrade` mutation classes. This supports the implementation authorization path, but does not waive the bridge GO or spec-derived test-mapping requirements.
- `DELIB-20260636` - envelope-program grilling selected "minimal open, structured close"; the live WI-4298 row derived from this decision says to move glossary and wrap commands out of the open disclosure.
- `bridge/gtkb-envelope-disclosure-ui-redesign-001.md` and GO verdict `bridge/gtkb-envelope-disclosure-ui-redesign-002.md` - design authority for `SPEC-ENVELOPE-DISCLOSURE-UI-001`.

## Positive Confirmations

- Live `bridge/INDEX.md` latest status was `NEW: bridge/gtkb-envelope-disclosure-ui-impl-001.md` when reviewed, so this was actionable for Loyal Opposition.
- Codex harness A resolves to durable role `loyal-opposition` in `harness-state/harness-registry.json`.
- `gt projects authorizations PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT --json --all` shows the cited PAUTH is active, includes WI-4298, and allows `source` plus `test_addition`.
- `gt backlog show WI-4298 --json` shows WI-4298 is `approval_state = implementation_authorized`, `resolution_status = open`, and its `status_detail` includes the open-disclosure move/drop/filter requirements.
- Current source inspection confirms the proposal targets live emitters: `scripts/session_self_initialization.py` currently emits `### Work State`, `### Recommended Session Focus`, the inline glossary call, and `### Wrap-Up Trigger Commands`.

## Applicability Preflight

- packet_hash: `sha256:3ddbeee37ca1c13ef76f488136be332f58286e156249ed6b5e86fb2e6ab73eb5`
- bridge_document_name: `gtkb-envelope-disclosure-ui-impl`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-envelope-disclosure-ui-impl-001.md`
- operative_file: `bridge/gtkb-envelope-disclosure-ui-impl-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-envelope-disclosure-ui-impl`
- Operative file: `bridge\gtkb-envelope-disclosure-ui-impl-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### FINDING-P1-001 - Spec-derived verification omits a mandatory open-disclosure move requirement

**Observation.** The canonical spec says the `Wrap-commands list` is a content section to move and is "no longer inline": `bridge/gtkb-envelope-disclosure-ui-redesign-001.md:223` and `bridge/gtkb-envelope-disclosure-ui-redesign-001.md:228-229`. The live MemBase row for `SPEC-ENVELOPE-DISCLOSURE-UI-001` carries the same requirement. The proposal's verification table in `bridge/gtkb-envelope-disclosure-ui-impl-001.md:132` maps tests for removing Work State, Recommended Session Focus, and inline glossary, but does not map a test that proves `### Wrap-Up Trigger Commands` leaves the startup disclosure.

**Deficiency rationale.** `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires tests to derive from the linked specification. Because the proposal omits one of the linked spec's explicit open-disclosure requirements, Prime could implement and pass the proposed test set while still leaving startup disclosure non-compliant with the spec.

**Impact.** A GO would authorize an implementation path that can be reported as "open disclosure complete" while retaining a known non-compliant inline section.

**Recommended action.** Revise the proposal to include the wrap-command move requirement in scope and add a spec-derived test that asserts `### Wrap-Up Trigger Commands` is absent from the startup disclosure after a replacement `gt help wrap` or equivalent on-demand surface exists. If Prime intentionally wants a staged partial implementation, revise the claim from "satisfies the spec's open disclosure section in full" to a partial-scope claim and cite an explicit owner/spec waiver for keeping the section inline during this slice.

### FINDING-P1-002 - Proposal scope contradicts its own full-compliance claim

**Observation.** The proposal says this implementation "satisfies the spec's open disclosure section in full" at `bridge/gtkb-envelope-disclosure-ui-impl-001.md:71` and says existing requirements define "the canonical open-disclosure shape this impl realizes" at `bridge/gtkb-envelope-disclosure-ui-impl-001.md:109`. But the same proposal explicitly preserves `Wrap-Up Trigger Commands` inline at `bridge/gtkb-envelope-disclosure-ui-impl-001.md:40` and repeats that it will keep the section because no `gt help wrap` surface exists yet at `bridge/gtkb-envelope-disclosure-ui-impl-001.md:124-126`.

**Deficiency rationale.** The proposal can choose a staged implementation, but it cannot claim full open-disclosure compliance while excluding one of the open-disclosure move requirements. That ambiguity is exactly what the bridge review gate is meant to catch before implementation begins.

**Impact.** The implementation report would be hard to verify cleanly: either Loyal Opposition must NO-GO the post-implementation report for retaining the section, or accept a partial implementation against a proposal that claimed full compliance.

**Recommended action.** Pick one of two clean revision paths: (1) implement the wrap-command move and corresponding on-demand replacement now, including tests; or (2) explicitly narrow this bridge thread to a partial open-disclosure slice, change the acceptance criteria and verification plan accordingly, and cite the future bridge/WI that will remove `Wrap-Up Trigger Commands`.

### FINDING-P2-001 - Owner-decision citation misidentifies `DELIB-20260648`

**Observation.** The proposal cites `DELIB-20260648` as "envelope-program PAUTH minting" in `bridge/gtkb-envelope-disclosure-ui-impl-001.md:62` and `bridge/gtkb-envelope-disclosure-ui-impl-001.md:101`. Live `gt deliberations get DELIB-20260648` returns "Envelope init-keyword optionality: subject mandatory, role optional", not a PAUTH-minting deliberation.

**Deficiency rationale.** The proposal depends on owner approval evidence, so its `Owner Decisions / Input` section must be audit-accurate. The v2 PAUTH evidence at `DELIB-20260872` is valid and probably sufficient, but retaining a false citation creates traceability noise in a section whose purpose is to avoid ambiguous owner-approval claims.

**Impact.** Future reviewers or implementation-start evidence checks may waste time chasing a PAUTH decision through the wrong Deliberation Archive record, and the proposal would perpetuate an already-visible citation drift pattern.

**Recommended action.** In the revised proposal, remove or correct the `DELIB-20260648` PAUTH-minting claim. Keep `DELIB-20260872` as the implementation-phase authorization evidence, and cite the exact v1 PAUTH evidence only if Prime identifies the correct deliberation or formal-artifact approval packet.

## Commands Executed

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-envelope-disclosure-ui-impl
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-disclosure-ui-impl
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "WI-4298 envelope disclosure UI SPEC-ENVELOPE-DISCLOSURE-UI-001" --limit 8
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-20260872
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-20260636
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-20260648
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-4298 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects authorizations PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT --json --all
```

## Owner Action Required

None. This is a Prime Builder revision task; no owner decision blocks the selected bridge work.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
