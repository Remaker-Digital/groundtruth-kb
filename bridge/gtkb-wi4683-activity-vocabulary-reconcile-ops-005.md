REVISED

# WI-4683 (REVISED -005): Formal Amendment of Router SPEC + Routing DCL to Six Members (Re-admit `ops`) — Governance-Review Cycle

bridge_kind: governance_review
Document: gtkb-wi4683-activity-vocabulary-reconcile-ops
Version: 005
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-22 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: d209f895-a107-4379-be37-d4ecf5e8ea00
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, autonomous /loop dynamic mode, Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4683

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

---

## Revision Note (-005, addressing NO-GO@-004)

NO-GO@-004 (correct) found that -003 mixed a formal SPEC/DCL amendment with source/test in one envelope: (F1) formal mutations were outside the source/test `target_paths`; (F2) `Requirement Sufficiency` declared a requirement amendment is required *before* implementation while also asking to authorize source/test, which the codex-review-gate forbids. Per F2's prescribed split, this revision makes THIS thread the **formal-artifact amendment cycle only**, modeled exactly on the GO'd ADR/DCL precedent (`gtkb-activity-disposition-profile-adr-dcl`): a `governance_review` that DRAFTS the two amended specs, is **terminal at GO**, with the amendments landing **downstream via owner-ratified formal-artifact-approval packets** (`kb_mutation_in_scope: false`, `target_paths: []`). The source/test code reconciliation (`topic_router.py` + `envelope.py` + tests) is a **separate follow-on bridge** filed after these v2 rows are live. Owner direction: AskUserQuestion 2026-06-22 "Proceed: formal amendment now."

## KB-Mutation Negation (self-demonstration)

This bridge thread performs no MemBase mutation and writes no protected narrative files. The two amended specs drafted below (`SPEC-TOPIC-ENVELOPE-ROUTER-001` v2 and `DCL-TOPIC-ENVELOPE-ROUTING-001` v2) land downstream via formal-artifact-approval packets, each gated by `GOV-ARTIFACT-APPROVAL-001` (owner presents + ratifies each v2 via AskUserQuestion, then `gt spec record` writes the packet + the new spec version). GO is terminal for THIS thread. This resolves F1 (no formal mutation inside an impl-start envelope — the amendments are packet-gated, the ADR/DCL precedent) and F2 (no source/test in this cycle).

## Summary

Amend the two live `specified` router specs from the closed five-member vocabulary `{spec, build, test, deliberation, project}` to the six-member set `{ops, deliberation, build, test, spec, project}`, re-admitting `ops`, per the owner-decided vocabulary (DELIB-20260621 DEC-4, superseding DELIB-20260638's five-member count; re-admission per DELIB-20265287 F1). `DCL-TOPIC-ENVELOPE-ROUTING-001` clause #4's process is satisfied: (a) per-type handler → WI-4687 (deferred); (b) DCL amendment → this thread; (c) owner-AUQ → DEC-4 + the ratification AUQ at implementation.

## Specification Links

- `SPEC-TOPIC-ENVELOPE-ROUTER-001` — amended to v2 (six-member command surface).
- `DCL-TOPIC-ENVELOPE-ROUTING-001` — amended to v2 (six-member routing map; clause #4 governs this amendment).
- `GOV-ARTIFACT-APPROVAL-001` — governs the two formal amendments (owner-ratified packets).
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` — A1 six-member set (reconciliation target).
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` — disposition decision over the vocabulary.
- `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-STANDING-BACKLOG-001`.
- Advisory (F3): `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

## Prior Deliberations

- `DELIB-20265287` — D10 (vocabulary drift is a defect); F1 (re-admit `ops`).
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` — DEC-4 locks the six-member set; resolves WI-4683/D10 to it (owner decision basis; supersedes DELIB-20260638's five-member count).
- `DELIB-20260638` — the prior five-member topic-envelope decision the current specs cite; superseded for vocabulary count by DEC-4.
- Bridge `gtkb-activity-disposition-profile-adr-dcl` GO@-002 — the governance_review formal-artifact precedent this thread mirrors; landed `DCL-ACTIVITY-DISPOSITION-PROFILE-001`.

## Owner Decisions / Input

- AskUserQuestion 2026-06-22: "Proceed: formal amendment now" — owner go-ahead for the two router-spec amendments as a sequenced formal-artifact cycle before the code.
- `DELIB-20260621` DEC-4 (AUQ-backed) — the six-member vocabulary decision satisfying `DCL-TOPIC-ENVELOPE-ROUTING-001` #4's owner-AUQ-to-add-a-type basis.
- Downstream owner step (after GO): present each v2 spec's full content via AskUserQuestion and mint a formal-artifact-approval packet (`presented_to_user=true`, `approved_by=owner`) before `gt spec record`, per GOV-ARTIFACT-APPROVAL-001.

## Requirement Sufficiency

Existing requirements sufficient for THIS governance_review cycle. The substantive requirement (six-member vocabulary) already exists (DEC-4 + DCL-ACTIVITY-DISPOSITION-PROFILE-001 A1); this thread drafts the two spec amendments that bring the live router specs into agreement, landing them via owner-ratified formal-artifact packets. No source/config/test implementation is authorized by this thread; the code reconciliation is a separate follow-on bridge filed after these v2 rows are live.

## Proposed v2 Content — SPEC-TOPIC-ENVELOPE-ROUTER-001 (full native format)

Title: Topic-Envelope Router Umbrella: `::open <type>` / `::close <type>` Command Surface and Closed Type Vocabulary. Type: requirement. Status: specified.

Body: A topic envelope is one of the three elements in the GroundTruth-KB envelope anatomy (dispatch / session / topic). It scopes an owner-initiated unit of work — a "topic" — within an active session, with a typed routing target that maps to an existing GT-KB service.

Historical note: formerly "work envelope" (DELIB-2500); renamed "topic envelope" by DELIB-20260637 decision 4. All current spec text uses "topic envelope" exclusively.

Open keyword: `::open <type>` where `<type>` is drawn from the closed **6-element** vocabulary (per DELIB-20260638, **expanded by DELIB-20260621 DEC-4 to re-admit `ops` per DELIB-20265287 F1**): `{ops, deliberation, build, test, spec, project}`. Strict parse: regex `^::open (ops|deliberation|build|test|spec|project)$`.

Close keyword: typed `::close <type>` with the same 6-element vocabulary. Strict parse: regex `^::close (ops|deliberation|build|test|spec|project)$`. Bare `::close` (no arg) not recognized.

One-topic-per-type invariant (preserved). MEDIUM auto-close (per DELIB-2500 #2/#3/#7): closing auto-executes dispatch; no owner-approval gate.

`ops` handler note: `ops` is admitted to the vocabulary here; its substantive per-type handler (acquire deployed-app status, apply decision criteria, emit prioritized AUQ options per DELIB-20265287 F1) is WI-4687. Until WI-4687, `ops` routes to the stub target in `DCL-TOPIC-ENVELOPE-ROUTING-001` v2.

No synonyms; per-type harness routing override (Slice 2); topic-envelope state (WI-4293) — unchanged from v1.

Assertions (machine-checkable; status=specified): (1) glossary entry for "topic envelope"; (2) `grep_absent` no current-text "work envelope" except DELIB-20260637 historical notes; (3) `grep_absent` no competing `::open`/`::close` parser. Amendment provenance: DEC-4; DELIB-20265287 F1; bridge gtkb-wi4683-activity-vocabulary-reconcile-ops; owner ratification packet.

## Proposed v2 Content — DCL-TOPIC-ENVELOPE-ROUTING-001 (full native format)

Title: Topic-Envelope Routing: Activity-Type to Existing-Service Dispatch Map. Type: design_constraint. Status: specified.

Constraint — the topic-envelope router MUST conform to:

1. Activity-type to service dispatch map (closed; amended via formal-artifact-approval only) — **6 rows**:
   - `ops` → operations status-and-decision surface (deployed-app status acquisition + decision criteria + prioritized AUQ emission); **per-type handler deferred to WI-4687** (DELIB-20265287 F1).
   - `spec` → spec-intake pipeline (`gt intake ...`); per-type SPEC body Slice 2.
   - `build` → build / packaging / scaffold service; Slice 2.
   - `test` → test execution + assertion-run service; Slice 2.
   - `deliberation` → Deliberation Archive write path (`gt deliberations record`); Slice 2.
   - `project` → project lifecycle service (`gt projects` family); Slice 2.
2. No new services: route to existing GT-KB services (the `ops` target is the existing operations/status surface).
3. MEDIUM auto-close (per DELIB-2500 #2/#3/#7): closing IS dispatching.
4. Dispatch map amendment requires (a) a per-type SPEC/slice, (b) a formal-artifact-approval amendment to this DCL, (c) owner-AUQ. **This v2 records the `ops` addition: (a) → WI-4687; (b) → this amendment; (c) → DELIB-20260621 DEC-4 + the ratification AUQ.**
5. Per-type harness routing override (Slice 2) — unchanged.
6. No bare "envelope" — unchanged.
7. Typed close grammar: `^::close (ops|deliberation|build|test|spec|project)$`. Bare `::close` rejected.

Assertions (machine-checkable; status=specified): (1) `grep` — the topic-router implementation references the **6-element** type vocabulary verbatim (expected-failing until the WI-4683 code follow-on bridge lands); (2) `grep` — the typed-close regex `^::close (ops|deliberation|build|test|spec|project)$` appears in the implementation (expected-failing until the code follow-on).

Related deliberations (`DELIB-2238`, `DELIB-2500`, `DELIB-20260635/6/7/8`, `DELIB-20260648`) — unchanged; amendment provenance adds `DELIB-20260621` DEC-4 + `DELIB-20265287` F1 + this bridge.

## Specification-Derived Verification Plan (governance-review-terminal)

GO is terminal for this thread; the two amendments are verified at their own downstream gates, not via a follow-on post-impl report on this thread. This is a spec-to-test mapping in which each amended spec's machine-checkable assertions ARE the spec-derived tests (the same maturation model as the ADR/DCL precedent):

| Amended spec | Spec-derived tests (assertions) | Verification command | Expected |
|---|---|---|---|
| `SPEC-TOPIC-ENVELOPE-ROUTER-001` v2 | assertions 1–3 (glossary entry; `grep_absent` "work envelope"; `grep_absent` competing parser) | `gt assert SPEC-TOPIC-ENVELOPE-ROUTER-001` ; `gt spec show ...` confirms v2 + six-member vocab/regexes | assertions run; status=specified (assertions tied to the code follow-on expected-failing until it lands, per GOV-04) |
| `DCL-TOPIC-ENVELOPE-ROUTING-001` v2 | assertions 1–2 (`grep` six-element vocab in impl; `grep` six-member typed-close regex) | `gt assert DCL-TOPIC-ENVELOPE-ROUTING-001` ; `gt spec show ...` confirms v2 + `ops` row | assertions run; expected-failing until the code follow-on lands (GOV-04 maturation) |
| `GOV-ARTIFACT-APPROVAL-001` | each amendment's packet has `presented_to_user=true`, `approved_by=owner`, `full_content_sha256` == inserted v2 content | inspect `.groundtruth/formal-artifact-approvals/*-{SPEC,DCL}-...json` | PASS |

The amended specs' assertions are deliberately expected-failing at `status=specified` (they assert the six-member set in the *implementation*, which the follow-on code bridge lands) — GOV-04 maturation, identical to how the ADR/DCL pair shipped with `status=specified` assertions.

## Findings Addressed

- **F1 (P1):** resolved via the F2 split — THIS thread is now the formal-artifact bridge only (`governance_review`, terminal at GO; amendments packet-gated downstream per GOV-ARTIFACT-APPROVAL-001, `target_paths: []`, `kb_mutation_in_scope: false` — the GO'd ADR/DCL precedent). No formal mutation sits inside an impl-start source/test envelope.
- **F2 (P1):** no source/test in this cycle; the code reconciliation is a separate follow-on bridge filed only after these v2 rows are live. `Requirement Sufficiency` no longer mixes phases.
- **F3 (P2):** the three artifact-oriented advisory specs are added to Specification Links.

## Risk / Rollback

Low. This thread writes one bridge file; the amendments are append-only new versions (v2) gated by owner-ratified packets at implementation. Rollback of THIS thread is git restore + deletion of the bridge file. The runtime stays five-member until the follow-on code bridge lands; `::open ops` is not yet runnable as a topic during that window (low impact — the disposition config already enumerates six independently).

## Recommended Commit Type

`docs` — governance formal-artifact drafting (the two spec amendments land via `gt spec record` downstream); the code follow-on bridge will be `fix`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
