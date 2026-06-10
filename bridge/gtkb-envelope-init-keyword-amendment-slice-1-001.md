NEW

# Envelope Init-Keyword Amendment: Subject Vocabulary Expansion + Role Optionality (WI-4291)

bridge_kind: governance_advisory
Document: gtkb-envelope-init-keyword-amendment-slice-1
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-04 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 61ca157f-cc93-49fa-95e3-40d76e7908db
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, interactive session, durable role prime-builder per harness-state/harness-registry.json

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297
Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-4291

target_paths: []

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal opens the envelope-program spec-amendment series with WI-4291: amending `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (v2 -> v3) and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (v2 -> v3) so the canonical init-keyword grammar fits the envelope meta-model established by DELIB-2500 and refined by DELIB-20260637 + DELIB-20260648.

Two coupled amendments:

1. **Subject vocabulary expansion.** The current canonical regex `^::init gtkb (pb|lo)$` accepts only the single subject token `gtkb`. The amendment expands the closed subject vocabulary to `{gtkb, application}` per DELIB-2500 #4 (refined by DELIB-20260637 #2). The specific application (when `subject = application`) is resolved from the work-subject configuration at `.claude/session/work-subject.json`, NOT hardcoded in the keyword. This preserves the Agent Red separateness boundary (Agent Red is one possible application; others are not foreclosed).

2. **Role-token optionality.** The role token (`pb`/`lo`) becomes optional per DELIB-20260648. When absent, the receiver uses the durable harness role from `harness-state/harness-registry.json` for all in-session surfaces; no session-stated override marker is written. When present, the existing `DCL-SESSION-ROLE-RESOLUTION-001` ephemeral-override semantic is unchanged. Bridge dispatch routing remains keyed to the durable harness role + active/suspended status per `GOV-SESSION-ROLE-AUTHORITY-001` (DELIB-20260648 §3 explicit preservation).

Proposed revised regex (canonical, both SPEC and DCL): `^::init (gtkb|application)( (pb|lo))?$`. Six valid forms result (2 subjects x 3 role variants: `pb`/`lo`/absent). Migration is fully additive: the prior forms `::init gtkb pb` and `::init gtkb lo` parse unchanged.

This proposal is **governance-only**. It revises the SPEC + DCL **text**. The downstream parser change (the strict canonical regex lives in dispatcher code per `scripts/workstream_focus.py` and the `STRICT_DROP`-gated receivers in `.claude/hooks/session_start_dispatch.py` + `.codex/gtkb-hooks/session_start_dispatch.py`) is OUT OF SCOPE for this proposal and will be addressed in a separate implementation bridge after this governance amendment receives `VERIFIED`. This separation reflects the handoff direction that the seven envelope-program spec WIs (WI-4291..WI-4297) must reach `VERIFIED` before implementation bridges open.

## Specification Links

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v2 (existing, `specified`) — the spec being amended. v3 will carry the revised regex `^::init (gtkb|application)( (pb|lo))?$` plus receiver-side normalization rules for the new subject + optional-role cases.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v2 (existing, `specified`) — the DCL being amended. v3 will extend the receiver decision table with the role-absent row (durable role applies; no session-stated marker written).
- `DCL-SESSION-ROLE-RESOLUTION-001` v1 (existing, `specified`) — **referenced, not amended**. The ephemeral-role-override semantic is preserved unchanged for the role-present case (DELIB-20260648 §2 explicit preservation).
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 (existing, `specified`) — **referenced, not amended**. The bridge-dispatch-routing-by-durable-role authority is preserved unchanged (DELIB-20260648 §3 explicit preservation).
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 (existing, `specified`) — **referenced, not amended**. The interactive-override decision survives; this amendment refines its grammar surface (subject + optional-role) without changing the override mechanism itself.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified) — governs this bridge proposal's filing discipline (INDEX-canonical, append-only versioning, status semantics).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified) — governs this section's completeness obligation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified) — governs the project/PAUTH/WI metadata header above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified) — governs the Spec-Derived Verification Plan section below.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 (specified) + `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` v1 (specified) — govern the PAUTH envelope cited in the header.
- `GOV-ARTIFACT-APPROVAL-001` v3 (verified) — governs the formal-artifact-approval packets that will land the SPEC + DCL v3 inserts post-GO.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 (specified) — **referenced for placement-contract compliance only.** The proposal mentions Agent Red as an example application to preserve the closed `{gtkb, application}` subject vocabulary's framing (Agent Red is one possible application; the subject token resolves the specific application via work-subject configuration, not via the keyword). This proposal does NOT mutate any path under `applications/` and does NOT propose changes to the application-placement contract. The ADR is cited for citation-completeness and to acknowledge that any Agent-Red-related reference is in scope of the placement contract even when the work itself is governance-only.

## Prior Deliberations

- `DELIB-20260648` (2026-06-04, owner_decision) — **Primary authority for this proposal.** Subject-mandatory/role-optional clarification refining DELIB-2500 #4 and DELIB-20260637 #2. The proposal text above quotes the decision verbatim where applicable: subject vocabulary, role optionality, durable-role default when role absent, bridge dispatch authority unchanged. WI-4291 status_detail captures the regex `^::init (gtkb|application)( (pb|lo))?$` derived from this DELIB.
- `DELIB-20260637` (2026-06-04, owner_decision) — Envelope meta-model refinement: three-part anatomy (invocation + intent-hint + payload) + dispatch-session-topic containment. The `<subject>` token in `::init` is the session-envelope's intent-hint per §2 of this DELIB. This proposal preserves that role: `<subject>` informs the agent about the session envelope's scope; it is NOT a project token.
- `DELIB-2500` (S363, owner_decision) — Original envelope-convention refinement. #4 established the `::init <area> <role>` form and the "role asserts, does not set" semantic. DELIB-20260648 refines #4's "asserts, does not set" wording into the clarified `role token present -> override; role token absent -> durable role applies` semantic this proposal encodes.
- `DELIB-S371` and follow-on architecture work — established the SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 v2 wording (regex + receiver-side scope split). This proposal extends v2 to v3 along the subject + role-optionality axes without touching v2's headless-vs-interactive split or the first-line-only constraint.

(Phantom-spec sweep: the four prior DELIBs above are referenced by id only; the SPEC/DCL/GOV/ADR ids in the Specification Links section have been confirmed against the live `specifications` table.)

## Owner Decisions / Input

This proposal depends on owner approval. The AUQ-only enforcement stack requires explicit AskUserQuestion evidence; the following durable owner-decision evidence authorizes this proposal:

1. **AUQ 2026-06-04 (this session, c136b772 handoff context resumed in 61ca157f) — "Which path should this session take first?" Selected: "Kick off envelope WI-4291 (Recommended)."** This is the proximate authorization to begin envelope-program implementation. Verbatim option label: "File NEW bridge proposal for spec-set #1 (init-keyword regex amendment per DELIB-2500/20260637/20260648, smallest envelope scope). Toward WI-4301 umbrella; first of 7 spec WIs that must reach VERIFIED."
2. **AUQ 2026-06-04 (this session) — "PAUTH-minting decision: how to scope the authorization envelope?" Selected: "Envelope-program PAUTH covering WI-4291..WI-4297 (Recommended)."** This is the owner authorization for the PAUTH cited in the proposal header. Verbatim option: "Single PAUTH for the 7 spec-amendment WIs ... owner_decision_deliberation_id=DELIB-20260648."
3. **DELIB-20260648 (2026-06-04, source_type=owner_conversation, outcome=owner_decision)** — durable owner-decision evidence for the substantive amendment text. Captured during the 2026-06-04 envelope-project per-WI grill sequence prior to this session. Refines DELIB-2500 #4 + DELIB-20260637 #2.
4. **WI-4291 lifecycle authority** — `approval_state=implementation_authorized`; `source_owner_directive=S-2026-06-04 owner grilling: formalize envelope program (WI-3468)`. The status_detail records the exact regex this proposal advances.

No new owner decision is requested in this proposal. Codex `GO` authorizes Prime to proceed with formal-artifact-approval packets for the SPEC + DCL v3 inserts; the packets themselves require the standard per-artifact owner-approval evidence per `GOV-ARTIFACT-APPROVAL-001`.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirements for the WI-4291 amendment are:

- DELIB-20260648 (primary), which captures owner intent on subject mandatory, role optional, durable-role default, and bridge-dispatch-routing preservation;
- DELIB-20260637 #2, which preserves the closed `{gtkb, application}` subject vocabulary as intent-hint within the envelope meta-model;
- DELIB-2500 #4, which originally established the `::init <area> <role>` grammar that DELIB-20260648 refines;
- WI-4291 status_detail, which records the regex form and migration property (fully additive; existing `::init gtkb pb` / `::init gtkb lo` parse unchanged).

No new or revised requirement is required before implementation. The proposal authorizes spec-text revisions that encode the existing durable owner-decision evidence.

## Specification-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, each linked spec maps to verification evidence the post-implementation report must carry forward. Because the implementation scope is governance (MemBase spec revisions via formal-artifact-approval packets), the verification surface is **spec-text correspondence + structural integrity**, not test execution against source code (the parser/dispatcher changes are out of scope per the Summary).

| Linked Spec | Verification Evidence Expected at Post-Impl Report |
|---|---|
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 | Live MemBase row for v3 exists; `description` field contains the canonical regex `^::init (gtkb|application)( (pb|lo))?$` byte-identically; v3 retains the v2 first-line-only + headless-vs-interactive structure unchanged for the gtkb subject + present-role rows. Evidence: `gt spec show SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` JSON output. |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v3 | Live MemBase row for v3 exists; decision table includes a NEW row for `init keyword present, role token absent` -> `DURABLE_ROLE_APPLIES` (or canonical equivalent); the `STRICT_DROP` row is unchanged (headless safety preserved). Evidence: `gt spec show DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` JSON output. |
| `DCL-SESSION-ROLE-RESOLUTION-001` v1 (referenced, NOT amended) | No new version inserted. Evidence: `gt spec show DCL-SESSION-ROLE-RESOLUTION-001` JSON output shows v1 unchanged. |
| `GOV-SESSION-ROLE-AUTHORITY-001` v1 (referenced, NOT amended) | No new version inserted. Evidence: `gt spec show GOV-SESSION-ROLE-AUTHORITY-001` JSON output shows v1 unchanged. |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 (referenced, NOT amended) | No new version inserted. Evidence: `gt spec show ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` JSON output shows v1 unchanged. |
| `GOV-ARTIFACT-APPROVAL-001` v3 | Per-artifact formal-artifact-approval-packet evidence exists at `.groundtruth/formal-artifact-approvals/<date>-<spec-id>.json` for each spec inserted; packet `body_hash` matches the inserted row. Evidence: `ls .groundtruth/formal-artifact-approvals/2026-06-04-*-INIT-KEYWORD-*.json` plus packet inspection. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` v1 / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 | This proposal file itself; INDEX entry; PAUTH metadata header; this section's existence. |

Mandatory pre-filing preflight evidence (recorded in the post-impl report):
```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-init-keyword-amendment-slice-1
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-init-keyword-amendment-slice-1
```

Both must return `preflight_passed: true` / `Blocking gaps: 0` at proposal filing AND at post-impl report filing. Phantom-spec sweep at filing time: every cited SPEC/GOV/ADR/DCL id has been confirmed against the live `specifications` table (recorded above).

## Risk / Rollback

**Risk surface:** governance-only; LOW.

- **Phantom-divergence risk** (eliminated at filing): the proposed v3 text is constructed verbatim from DELIB-20260648 §1-§3 plus WI-4291 status_detail; no inferred semantics. The phantom-spec sweep above confirms no spec id divergence at filing time. Recurrence risk at post-impl is mitigated by the formal-artifact-approval-packet `body_hash` discipline.
- **Subject-vocabulary-creep risk** (bounded by closed vocab): the spec amendment EXPLICITLY enumerates `{gtkb, application}` and rejects any other token. DELIB-20260648 §1 establishes that the specific application is resolved from work-subject config, not from the keyword token; this proposal preserves that resolution path. No follow-on amendment is implied for `application` -> `agent_red` mapping (Agent Red is one possible application).
- **Receiver-side ambiguity risk** (mitigated): the DCL v3 decision table adds exactly one row (role-absent case); all other rows are preserved byte-identically. The `STRICT_DROP` row is explicitly preserved to maintain headless safety; this is called out in DELIB-20260648 §3.
- **Downstream-parser-coupling risk** (out of scope): this proposal does NOT mutate `scripts/workstream_focus.py`, `scripts/cross_harness_bridge_trigger.py`, `.claude/hooks/session_start_dispatch.py`, or `.codex/gtkb-hooks/session_start_dispatch.py`. Until the downstream impl bridge lands, the existing parser will continue to enforce `^::init gtkb (pb|lo)$` strictly; new forms (`::init application`, `::init gtkb`, etc.) will not parse. This intentional decoupling allows the spec-amendment cycle to complete before any runtime behavior shifts.

**Rollback procedure:** governance-only proposals rollback via append-only supersede. If `NO-GO` lands on the SPEC v3 or DCL v3 text, Prime files a REVISED proposal at `-002` addressing the findings; the v2 versions remain in MemBase and continue to govern until v3 is GO'd. If a v3 ships and is later found defective, a v4 supersede via the same PAUTH path corrects it. No git revert is required because no source files change in this proposal's scope.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-envelope-init-keyword-amendment-slice-1` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs(bridge)` — this proposal file is a bridge-protocol document; no source-code surface mutates within its scope. The downstream impl bridge (not opened by this proposal) will use `feat` or `refactor` depending on the parser-change shape.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
