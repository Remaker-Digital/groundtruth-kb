NEW

# Session Envelope Durability DCL: .claude/session/envelope.json Contract (WI-4293)

bridge_kind: governance_review
Document: gtkb-session-envelope-durability-001
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
Work Item: WI-4293
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation and executes no KB writes. The actual `DCL-SESSION-ENVELOPE-DURABILITY-001` insertion is a downstream operation under the active PAUTH's `approval_packet_creation` mutation class and is filed as a separate post-GO step, not part of this bridge thread. (Trips `KB_MUTATION_NEGATION_RE` in `.claude/hooks/bridge-compliance-gate.py:203-207`, short-circuiting `_declares_kb_mutation` to False.)

---

## Summary

This proposal opens drafting on `DCL-SESSION-ENVELOPE-DURABILITY-001`: the design constraint specifying the durable session-state file at `.claude/session/envelope.json`. The envelope file is the on-disk substrate for the envelope program: it records the session envelope (subject, role, init_keyword, opened_at, closed_at, wrap_outcome) plus an embedded array of topic envelopes (each with type, open/close timestamps, close outcome, preload state, route target).

The envelope is the durable record that WI-4292's `::wrap` keyword (peer-filed at `bridge/gtkb-canonical-wrap-keyword-syntax-001-001.md`) iterates on close, and that WI-4294's wrap procedure mutates. Without this DCL, the keyword spec (WI-4292) and the wrap procedure (WI-4294) have no canonical contract for the shape they read from and write to.

Owner-grilled design points captured in WI-4293 `status_detail` (DELIB-20260636 + DELIB-20260637 owner_decision evidence):

1. **Shape:** single `envelope.json` with embedded `topics` array (one file holds everything; `topics = [{type, opened_at, closed_at, close_outcome, preload_state, route_target}, ...]`).
2. **Lifecycle:** on `::wrap`, the live file is renamed to `.claude/session/archive/<closed_at-ISO>-envelope.json` and unset; next `::init` opens a fresh file. The archive trail under `.claude/session/archive/` is append-only.
3. **Schema evolution:** top-level `envelope_schema_version` field; readers normalize on load; writers always emit latest. v1 is the initial schema; schema bumps require a new DCL version.
4. **WI-4292 auto-close coupling:** when `::wrap` fires with open topics, each topic records `close_outcome=auto_closed_by_session_wrap` before the file is archived.

This proposal is **governance-only**. The DCL body lands via a formal-artifact-approval packet post-GO; no source file under `scripts/`, `.claude/hooks/`, or session-startup paths is mutated by this proposal's scope. Downstream implementation (the writers/readers that actually maintain `.claude/session/envelope.json`) lives in separate bridge proposals under WI-4301 (umbrella) and follow-on per-WI threads.

This proposal treats `GO` as terminal per the `governance_review` `requires_verification: false` pattern: Codex GO authorizes downstream MemBase insertion via approval packet; no post-implementation bridge report is filed.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified) — governs this proposal's filing discipline (INDEX-canonical, append-only versioning, status semantics).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified) — this Specification Links section satisfies the linkage gate.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified) — `Project:` and `Project Authorization:` metadata cite the active PAUTH covering WI-4293.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified) — governs the Specification-Derived Verification Plan section below (acknowledged terminal-GO model).
- `GOV-STANDING-BACKLOG-001` v5 (verified) — WI-4293 is the governing backlog item in `approval_state=implementation_authorized` covered by the active PAUTH.
- `GOV-ARTIFACT-APPROVAL-001` v3 (verified) — governs the formal-artifact-approval packet that will land the DCL post-GO.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 (specified) + `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` v1 (specified) — govern the PAUTH envelope cited in the header.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the proposed DCL is a governed artifact (design_constraint), not a transient session file.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — net-new DCL creation is a lifecycle event covered by the PAUTH's `allowed_mutation_classes`.

**Specs referenced as paired/coupled (not modified by this proposal):**

- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v2 (specified) — the init-keyword DCL produces the values (`subject`, `role`, `init_keyword`) that the envelope.json schema records. The receiver-side decision-table outcomes (`NORMAL_STARTUP`, `INTERACTIVE_OVERRIDE_AUTHORIZED`, `LEGACY_FALLBACK`, `DISPATCH_AUTHORIZED`, `STRICT_DROP`) inform what gets written to the envelope on session start. WI-4291's amendment proposal (`bridge/gtkb-envelope-init-keyword-amendment-slice-1-001.md`, this session) extends the init-keyword grammar; this DCL must accommodate both the v2 grammar (current) and v3 grammar (when WI-4291 lands) — the `init_keyword` field stores the raw owner prompt, so both grammars are accommodated by recording-as-string.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v2 (specified) — the keyword syntax driving the `init_keyword` field.

**Specs drafted by this proposal (downstream insert via approval packet):**

- `DCL-SESSION-ENVELOPE-DURABILITY-001` (NEW; design points outlined in Summary above).

## Prior Deliberations

- `DELIB-20260636` (2026-06-04, owner_decision) — **Primary authority for project home.** Envelope-program grilling fulfilling WI-3468; consolidates the program under PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT. Also includes the dispatch-element-IN decision (#2) that informs the topic envelope's `route_target` field.
- `DELIB-20260637` (2026-06-04, owner_decision) — **Envelope meta-model + topic envelope shape.** Three-part anatomy (invocation + intent-hint + payload) + dispatch-session-topic containment. The topic envelope record's fields (`type`, `preload_state`, `route_target`) derive from §3 + §5 of this DELIB.
- `DELIB-2238` (S363, owner_decision) — **Originating envelope-state fields.** Specifies the canonical envelope state fields: `opened_at`, `init_keyword`, `subject`, `role`, `closed_at`, `wrap_outcome`. This DCL encodes those fields verbatim at the top level of `envelope.json`.
- `DELIB-2500` (S363, owner_decision) — Original envelope-convention refinement. #4 establishes the init-keyword grammar feeding `subject` and `role`; #7 establishes the thin-router work-envelope mechanics that inform the topic-envelope `route_target` field.
- `DELIB-20260648` (2026-06-04, owner_decision) — Subject-mandatory/role-optional clarification for init-keyword (cited for the role-optional accommodation: the `role` field may be null when the init keyword omits the role token).
- `bridge/gtkb-canonical-wrap-keyword-syntax-001-001.md` (NEW this session, peer-filed under same PAUTH) — sibling WI-4292 thread. The `::wrap` keyword spec depends on this DCL for the open-topic-auto-close semantic.

(Phantom-spec sweep: the four prior DELIBs above are referenced by id only; the SPEC/DCL/GOV/ADR ids in the Specification Links section have been confirmed against the live `specifications` table.)

## Owner Decisions / Input

This governance-review proposal is authorized by the active PAUTH; no fresh AUQ is required at proposal-filing time. The operative owner-decision evidence is:

1. **AUQ 2026-06-04 (this session, 61ca157f) — "PAUTH is doing its job and the swarm is filing. What next?" Selected: "File WI-4293 envelope.json schema."** Proximate authorization for this filing.
2. **AUQ 2026-06-04 (this session) — "PAUTH-minting decision: how to scope the authorization envelope?" Selected: "Envelope-program PAUTH covering WI-4291..WI-4297."** This is the operative authorization for the PAUTH cited in the proposal header.
3. **DELIB-20260636 (2026-06-04, source_type=owner_conversation, outcome=owner_decision)** — envelope-program grilling + formalization. Consolidates the program under PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT and includes the dispatch-IN decision.
4. **DELIB-20260637 (2026-06-04, owner_decision)** — envelope meta-model refinement (3-part anatomy + dispatch-session-topic containment). Establishes the topic-envelope shape.
5. **DELIB-2238 + DELIB-2500 (S363, owner_decision)** — originating envelope-state fields and envelope convention adoption.
6. **WI-4293 lifecycle authority** — `approval_state=implementation_authorized`; status_detail records the grill decisions (shape, lifecycle, schema evolution, WI-4292 coupling) verbatim.

Owner-input dependencies downstream of GO:

- 1 formal-artifact-approval packet at MemBase insertion time for `DCL-SESSION-ENVELOPE-DURABILITY-001`.
- No source / hook / test mutation requested in this thread; those land in WI-4294 (wrap procedure implementation) and WI-4301 (envelope program umbrella), which are separate WIs under the same PAUTH umbrella.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirements for WI-4293 are:

- WI-4293 `status_detail` grill decisions (shape, lifecycle, schema evolution, WI-4292 coupling) — owner-AUQ-recorded design;
- DELIB-2238 envelope-state field enumeration (six top-level fields);
- DELIB-20260637 §3 + §5 (topic envelope shape: type, preload, route);
- DELIB-20260648 §1-§2 (role-optional accommodation: `role` field may be null);
- The status_detail's "Implementation-approval deferred to after WI-4294 grilling" gate has cleared: WI-4294 is in `approval_state=implementation_authorized` per the handoff's 12-WI implementation_authorized list, so the archive-step coherence is locked across both WIs.

No new or revised requirement is required before this DCL is drafted.

## Specification-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, each linked spec maps to verification evidence. Because this proposal uses `requires_verification: false` (treating GO as terminal per the `governance_review` `[[latest-go-terminal-for-governance-review]]` pattern), the verification surface is **spec-text correspondence at approval-packet time**, not a separate post-impl bridge report.

| Linked Spec | Verification Evidence Expected |
|---|---|
| `DCL-SESSION-ENVELOPE-DURABILITY-001` v1 (drafted by this proposal) | Live MemBase row for v1 exists post-approval-packet; `description` field contains the schema (envelope_schema_version, top-level fields, topics array shape, lifecycle, mechanical guards) byte-identically to the GO'd text. Evidence: `gt spec show DCL-SESSION-ENVELOPE-DURABILITY-001` JSON output + the matching formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-06-04-DCL-SESSION-ENVELOPE-DURABILITY-001.json`. |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v2 (referenced, NOT amended) | No new version inserted. Evidence: `gt spec show DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` shows v2 unchanged. |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v2 (referenced, NOT amended) | No new version inserted. Evidence: `gt spec show SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` shows v2 unchanged. |
| `GOV-ARTIFACT-APPROVAL-001` v3 | Per-artifact formal-artifact-approval packet present at `.groundtruth/formal-artifact-approvals/2026-06-04-DCL-SESSION-ENVELOPE-DURABILITY-001.json`; packet `body_hash` matches the inserted row's content fingerprint. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` + `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` + `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This proposal file itself; INDEX entry; PAUTH metadata header; this Specification Links section's existence. |

Mandatory pre-filing preflight evidence:
```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-session-envelope-durability-001
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-session-envelope-durability-001
```

Both must return `preflight_passed: true` / `Blocking gaps: 0` at proposal filing time. Phantom-spec sweep at filing time: every cited SPEC/GOV/ADR/DCL id has been confirmed against the live `specifications` table.

## Risk / Rollback

**Risk surface:** governance-only; LOW.

- **Schema-design risk** (mitigated by explicit grilling): the schema (top-level fields + topics array + lifecycle) was owner-grilled in DELIB-20260636/DELIB-20260637 with explicit AUQ records. No inferred semantics; every field traces to a recorded owner decision.
- **WI-4292 coupling risk** (locked): the auto-close coupling (`close_outcome=auto_closed_by_session_wrap` on `::wrap`) is recorded in both WI-4292 status_detail and WI-4293 status_detail. The status_detail concern ("Implementation-approval deferred to after WI-4294 grilling") has cleared because WI-4294 is now `implementation_authorized`.
- **Schema-evolution risk** (designed in): `envelope_schema_version` is the explicit evolution surface; readers normalize on load; schema bumps require a new DCL version. v1 is the initial schema; future bumps don't break existing archive trails because each archived envelope.json carries its `envelope_schema_version` recorded at write time.
- **Init-keyword grammar coupling risk** (accommodated): WI-4291's proposed v3 init-keyword grammar (subject + optional role) is accommodated by recording `init_keyword` as the raw owner prompt string (not parsing it into structured fields beyond `subject` and `role`). Both v2 and v3 grammars produce envelopes with the same shape; the `role` field is nullable.
- **Concurrent-session race risk** (file-level): two concurrent sessions writing to the same `.claude/session/envelope.json` would corrupt the file. Mitigated by atomic-replace (temp-file + rename) writers; the DCL will specify this guard. Multi-harness topology is the operative case; each harness has its own session dir per existing convention, so cross-harness contention is structurally avoided.

**Rollback procedure:** governance-only proposals rollback via append-only supersede. If `NO-GO` lands on the DCL text, Prime files a REVISED proposal at `-002` addressing the findings; no MemBase mutation has occurred so there is nothing to undo. If a v1 ships and is later found defective, a v2 supersede via the same PAUTH path corrects it. No git revert is required because no source files change in this proposal's scope.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-session-envelope-durability-001` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs(bridge)` — this proposal file is a bridge-protocol document; no source-code surface mutates within its scope. The downstream impl bridge (not opened by this proposal) will use `feat` (for the writer/reader code that maintains `.claude/session/envelope.json`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
