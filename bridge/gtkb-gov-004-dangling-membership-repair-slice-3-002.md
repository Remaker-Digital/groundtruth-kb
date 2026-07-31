GO

# Loyal Opposition Verdict — GTKB-GOV-004 Dangling Membership Repair (Slice 3)

bridge_kind: lo_verdict
Document: gtkb-gov-004-dangling-membership-repair-slice-3
Version: 002
Date: 2026-07-01 UTC
Status: GO

author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: 2026-07-01T07-41-32Z-loyal-opposition-F-e56e47
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter harness shim; route deepseek-v4-pro; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

reviewed_proposal: bridge/gtkb-gov-004-dangling-membership-repair-slice-3-001.md
proposal_version: 001
proposal_author_harness: E (cursor, prime-builder)

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-GOV-004

---

## Verdict: GO

This is a bounded, two-WI membership repair slice that corrects dangling `active` PWM rows on retired projects by moving them to single-candidate active target projects. The scope discipline is correct — it avoids the ambiguous multi-candidate and zero-candidate cases — and the implementation commands are exact and verifiable. The ACID/PAUTH scope note properly distinguishes membership reconciliation from implementation authorization.

## Strengths

1. **Rigorous scope discipline.** Of 5 dangling WIs, only the 2 with exactly one weak candidate target are addressed. The 3 ambiguous cases (WI-4851 multi-candidate, two WORKLIST zero-candidate) are explicitly deferred. No bulk disposition, no WI retirement, no resolution_status changes. This is exactly how bounded membership slices should operate.

2. **Concrete live evidence anchoring.** The PWM read-back table names every affected membership row with its current status and project status. Both target projects are confirmed active via independent `gt projects show` review (PROJECT-GTKB-DASHBOARD-OBSERVABILITY status=active, GTKB-V1-RELEASE-STRATEGY-001 status=active). The `gt projects remove-item` CLI has been VERIFIED (bridge/gtkb-projects-remove-item-cli-slice-1-011.md).

3. **Exact, copy-pasteable implementation commands.** Every `gt projects remove-item` and `gt projects add-item` invocation is specified with a full `--change-reason` citing this bridge thread. The verification plan is equally precise — 7 checkpoints with explicit CLI commands and expected outcomes.

4. **Correct PAUTH framing.** The proposal explicitly acknowledges that the target projects have snapshot-bound PAUTHs that do not list these WIs, and correctly frames this slice as membership reconciliation under GTKB-GOV-004 / governance-hardening PAUTH — not as implementation authorization. This preserves the ACID-invariant on scope expansion.

5. **Clean risk/rollback analysis.** Three risks mapped to concrete mitigations. Rollback path is append-only reverse (remove from new target, add back to prior retired) — correctly noted as not recommended but available if LO directs.

6. **Preflights clean on blocking criteria.** Both applicability preflight (no missing required specs) and clause preflight (0 blocking gaps, 0 evidence gaps in must_apply clauses) pass.

## Concerns (non-blocking)

1. **Missing advisory specs.** The applicability preflight flags three advisory-severity specs as uncited: ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001. The proposal's content incidentally satisfies these through its artifact boundaries (bridge files as durable artifacts), lifecycle references (verified inventory baseline, deferred triage), and owner-decision/work-item/backlog governance content. Advisory-severity uncited specs do not block GO.

2. **Target paths is empty (target_paths: []).** This is correct for CLI-only membership mutations that operate through the `gt projects` service rather than creating or editing worktree files. The verification plan correctly focuses on PWM read-back and inventory reclassification rather than file diffs. Non-blocking observation.

## Applicability Preflight

- packet_hash: `sha256:084223116c7ddd38c7bcea3c1460e8ac1828efa856d212a60e2b517c383f4cca`
- bridge_document_name: `gtkb-gov-004-dangling-membership-repair-slice-3`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-gov-004-dangling-membership-repair-slice-3-001.md`
- operative_file: `bridge/gtkb-gov-004-dangling-membership-repair-slice-3-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability Gate

- Bridge id: `gtkb-gov-004-dangling-membership-repair-slice-3`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` — governance-hardening PAUTH batch.
- `DELIB-20260745` — `gt projects remove-item` append-only non-active membership precedent.
- `DELIB-20261322` — remove/retire must never append an `active` membership incorrectly.
- `bridge/gtkb-gov-004-inventory-evidence-slice-2-002.md` — GO deferred dangling repair to follow-on apply slice.
- `bridge/gtkb-gov-004-inventory-evidence-slice-2-004.md` — VERIFIED inventory evidence baseline.
- `bridge/gtkb-project-membership-reconciliation-slice-1-scoping-002.md` — GO for decomposed membership slices.
- `bridge/gtkb-projects-remove-item-cli-slice-1-011.md` — VERIFIED `gt projects remove-item` CLI.

## Recommended Commit Type

docs(governance): GTKB-GOV-004 dangling membership repair slice 3