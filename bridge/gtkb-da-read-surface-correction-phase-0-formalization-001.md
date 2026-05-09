# Implementation Proposal — GTKB-DA-READ-SURFACE-CORRECTION Phase 0: Formalization

- Status: NEW
- Date: 2026-05-08
- Session: S331 (continuation)
- Author: Prime Builder (Claude Code, harness B)
- bridge_kind: prime_implementation_proposal
- Umbrella work item: `GTKB-DA-READ-SURFACE-CORRECTION` (Phase 0 of 5)

## Summary

S331 surfaced a procedural failure: the Deliberation Archive was not consulted before an evaluation of the concept "GT-KB isolation." The result was a wrong-frame evaluation that contradicted four prior owner-decision deliberations. Owner critique surfaced the deeper system-level problem: an archive whose value depends on agent-initiated retrieval will fail in any session where retrieval is skipped, and adding more enforcement on top of a skipped rule treats symptoms rather than causes.

This proposal formalizes the owner-approved correction as a GOV / ADR / DCL / DCL trio (four formal artifacts). The correction reframes the canonical-terminology glossary as the Deliberation Archive's primary read surface, with the DA itself becoming the substrate the glossary cites. Direct DA semantic search becomes the long-tail / audit / rationale-deep-dive path, not the canonical reach pattern.

This is Phase 0 of a five-phase plan agreed in S331. Phase 0 produces no behavior change; it establishes the artifact authority that downstream phases (1: glossary backfill; 2: bridge template pre-population; 3: UserPromptSubmit glossary-expansion hook; 4: doctor checks and regression; 5: doctrine update) cite. No MemBase mutation is performed by this proposal. MemBase writes happen at the Phase 0 closure boundary, gated on per-artifact owner approval via AskUserQuestion.

## Specification Links

Cross-cutting / always-applicable to bridge proposals and verification:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — file-bridge protocol authority for this proposal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — adopter applications live at `<gt-kb-root>/applications/<name>/`. Cited because this proposal references `.claude/rules/file-bridge-protocol.md` (a path matcher trigger). **No scope conflict**: this proposal does not modify application placement, does not touch `applications/**`, and does not introduce or change adopter-application file locations.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Phase 4 verification will derive from the DCL assertions enumerated below.
- `GOV-ARTIFACT-APPROVAL-001` — formal artifacts proposed here require owner approval before MemBase insertion.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — concrete decisions, risks, and follow-on work in this proposal are preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the proposed change preserves traceability across artifacts, deliberations, and tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Phase boundaries surface candidate, deferred, superseded, and verified states.

Topic-specific specifications and rules this proposal extends or relies upon:

- `SPEC-2098` — Deliberation archive: structured storage and semantic search for reasoning.
- `SPEC-0067` — Glossary discipline: a UI glossary MUST be maintained and Claude MUST encourage consistent use. Authority for the glossary's first-class status; this proposal extends that authority to encompass the DA-read-surface role.
- `DCL-SPEC-DA-CITATION-MANDATORY-001` — every specification must have a Deliberation Archive entry capturing origin. Existing citation discipline at the spec layer; this proposal establishes a parallel discipline at the glossary layer.
- `DCL-SPEC-ORIGIN-DELIBERATION-SUPPORT-001` — unsupported specification authority requires owner approval/rejection.
- `SPEC-DA-HARVEST-INCLUSION`, `SPEC-DA-HARVEST-EXCLUSION`, `SPEC-DA-MECHANICAL-ENFORCE`, `SPEC-DA-RETROACTIVE-SWEEP` — DA write-side governance. Preserved unchanged by this proposal.
- `ADR-008` — Deliberation archive: build in groundtruth-kb rather than adopt MemPal. Authority for the DA's place in the platform.

Rule-file authority touched by this proposal (no edits in Phase 0; cited for reference):

- `.claude/rules/canonical-terminology.md` — current glossary surface. Phase 1 backfills missing entries; Phase 5 doctrine update reflects the new role.
- `.claude/rules/deliberation-protocol.md` — current consultation rules. Doctrine update lands in Phase 5 after mechanics are verified, not earlier (avoids capability overclaim).
- `.claude/rules/operating-model.md` — §4 alignment test gains a glossary-promotion criterion in Phase 5.
- `.claude/rules/file-bridge-protocol.md` — Prior Deliberations section authority; extended in Phase 2 (template pre-population).

Adjacent open work, NOT superseded by this proposal:

- `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md` — Codex Loyal Opposition advisory at NO-GO status, tasking Prime with a broader Canonical Terminology System / Bounded Context Model proposal. Phase 0 here is intentionally narrower, addressing only the DA-read-surface placement specifically. The broader advisory remains an open separate Prime proposal track. See § Subsumption Statement.

## Prior Deliberations

The following Deliberation Archive records anchor the framing. Each is captured at `source_type='owner_conversation'` with `outcome='owner_decision'` unless noted.

The four DA records that the S331 wrong-frame evaluation contradicted (anchor cases for the Phase 1 backfill of "isolation"):

- "GT-KB platform supports only one developed application at a time (lifecycle-independence contract)" — S319, 2026-04-28. Owner verbatim: *"We want GT-KB and the applications that are built using it to be isolated for lifecycle reasons (the platform should be able to evolve independently of the applications, on its own release cadence)."*
- "Owner directive update: industry-alignment critique for GT-KB/application separation" — 2026-04-22. Asymmetric safety model: application-subject sessions cannot mutate GT-KB; GT-KB-subject sessions retain broader authority.
- "S321 owner directive: platform app non specific" — *"All work on the GT-KB project must be implemented in a fashion that is application non-specific."*
- "GTKB-ISOLATION-002 Phase 2 root and repository topology plan" — 2026-04-22. Industry-aligned topology = separate repositories with package/service consumption.

DA records establishing the Canonical Terminology System framing:

- "Canonical Terminology System accepted as GT-KB feature framing" — 2026-05-07. Established Canonical Terminology System as the preferred product framing.
- "Agents must initialize with core terminology, services, artifacts, and access methods" — owner directive establishing startup-time glossary loading.
- "Bridge thread: gtkb-canonical-terminology-surface-implementation (12 versions, VERIFIED)" — established `.claude/rules/canonical-terminology.md` as the live glossary surface.

DA records establishing the DA itself:

- `SPEC-2098` deliberation thread — Deliberation Archive feature inception.
- `ADR-008` deliberation thread — build DA in groundtruth-kb.
- "Deliberation Archive Completion Advisory" — informational; harvest-pipeline maturation context.

S331 in-session decisions authorizing this proposal:

- 2026-05-08 owner agreement (S331): "proceed with placements that ride existing reach-patterns instead of fighting them."
- 2026-05-08 owner direction (S331): plan accepted; "Please begin. Please parallelize this work to the extent possible."
- 2026-05-08 owner framing (S331): prioritization is by impact and dependencies; cost/effort is irrelevant. Quality and completeness are the only valid concerns.
- 2026-05-08 owner diagnostic (S331): the bias / salience distinction; aware-but-unused resources usually indicate a placement problem rather than a discipline problem.

## Owner Decisions / Input

This proposal's authorizing context is captured above in § Prior Deliberations under "S331 in-session decisions". Those owner decisions were collected through chat-thread agreement during S331; the durable record is this bridge file plus the conversation transcript that will be DA-harvested at session wrap.

Future owner approvals this proposal will surface (each via AskUserQuestion at the appropriate moment, one at a time, per durable owner preference for sequential decision presentation):

1. Approval to insert `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` into MemBase as drafted.
2. Approval to insert `ADR-DA-READ-SURFACE-PLACEMENT-001` into MemBase as drafted.
3. Approval to insert `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` into MemBase as drafted.
4. Approval to insert `DCL-CONCEPT-ON-CONTACT-001` into MemBase as drafted.
5. Confirmation that the 2026-05-07 advisory remains an open separate track (not superseded by this proposal).
6. Approval of the load-bearing-concept audit list (Phase 1 boundary; surfaced when Phase 1 proposal is filed).

These approvals are NOT requested in this Phase 0 proposal turn. They are surfaced at the moment Prime is ready to write to MemBase, after Codex GO on this proposal authorizes MemBase mutation.

## Proposed Formal Artifacts (Drafts)

### Artifact 1 — `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` (governance principle)

**Statement.** The canonical-terminology glossary at `.claude/rules/canonical-terminology.md` is the Deliberation Archive's primary read surface for live consultation by AI agents. The DA itself is the substrate the glossary cites: agents reach the DA through glossary entries' `Source:` lines, not through direct DA queries by default. Direct DA semantic search remains available as a long-tail / audit / rationale-deep-dive path; it is not the canonical reach pattern.

**Authority extension.** Extends `DCL-SPEC-DA-CITATION-MANDATORY-001` (specs must cite DA) by establishing a parallel discipline at the glossary layer. Extends `SPEC-0067` (maintained glossary) by establishing the glossary's role as the DA's read surface.

**Rationale.** The S331 wrong-frame evaluation occurred because the agent did not search the DA before responding to an owner clarification. Procedural rules already mandated the search; the rule was skipped under task focus. Owner-articulated diagnosis (S331): aware-but-unused resources typically indicate a placement problem (the resource is not on the model's natural reach path) rather than a discipline problem (the agent is unwilling to follow the rule). The model is already reading the glossary at every session start; placing DA pointers on glossary entries rides existing reach without introducing a new ritual.

**Acceptance signal.** Routine prior-decision consultation by AI agents is served by glossary entries in the majority of cases; direct DA queries are reserved for audit, rationale deep-dive, and long-tail cases where the glossary has not yet absorbed a concept.

### Artifact 2 — `ADR-DA-READ-SURFACE-PLACEMENT-001` (architecture decision)

**Decision.** Place DA pointers on glossary entries. The glossary is the agent-side read surface for prior decisions; the DA is the substrate the glossary cites.

**Context.** S331 demonstrated a reliable failure mode: agent-initiated DA retrieval is skipped under task focus. The choice presented to the owner was to correct the system or remove the DA. Owner direction (S331): correct via placement that rides existing reach-patterns rather than via stricter enforcement.

**Alternatives considered.**

- *Path A — auto-inject DA matches on every owner prompt* (UserPromptSubmit hook with semantic match). Considered as primary placement; demoted to long-tail catch (Phase 3) because it is heavier than glossary-first and depends on similarity-threshold tuning. Retained for residual cases.
- *Path B — gate clarification/proposal responses on a DA-search-done artifact* (Stop or PreToolUse hook). Rejected: pushes the failure mode from "not searching" to "searching badly" — a brittle classifier produces false positives that create busywork without information. Strict enforcement against a behavior the model skips reliably tends to produce workaround behavior (precedent: S331 owner-decision-tracker regex-recursion failure when AskUserQuestion enforcement triggered on prose discussion of itself).
- *Path C — Loyal Opposition-only DA enforcement at bridge review boundary*. Rejected: scope is narrow; only catches failures that traverse the bridge. The S331 failure was a conversational evaluation that never became a bridge entry. LO diligence is the same variable as Prime Builder diligence; the failure mode moves rather than disappearing.
- *Path D — glossary as primary read surface; DA cited from glossary entries; auto-injection as long-tail; bridge templates pre-populated.* **Chosen.**

**Rationale for Path D.** Bias-aligned design. The model is already traversing the glossary; placement there rides existing reach. The S331 failure is removed at the source: with `isolation` as a glossary entry citing the four lifecycle-independence DA records, glossary auto-load surfaces the canonical meaning before any tool call. No new agent behavior is required.

**Consequences.**

- The glossary becomes a higher-discipline artifact. Concepts are added on first use rather than at audit time (codified in Artifact 4: `DCL-CONCEPT-ON-CONTACT-001`).
- The DA's value model changes from "actively consulted" to "passively cited." This is the intended structural change.
- Glossary-to-DA citation integrity becomes load-bearing. Broken citations are a new failure surface; addressed by Artifact 3's machine-checkable assertion and by Phase 4 doctor checks.
- The DA harvest pipeline remains unchanged. Read-side correction only.

### Artifact 3 — `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` (machine-checkable design constraint)

**Constraint.** Every glossary entry in `.claude/rules/canonical-terminology.md` MUST have a `Source:` line that resolves to at least one of: (a) a Deliberation Archive record (by DELIB-ID, deliberation title, or harvested capture file path), (b) a rule file that itself resolves to a DA record, or (c) a MemBase specification (`SPEC-NNNN`, `GOV-NNN`, `ADR-NNN`, `DCL-NNN`, `PB-NNN`, `REQ-NNN`).

**Assertions** (implemented as doctor checks in Phase 4):

- *grep_present*: every `### ` heading within `## Canonical Terms` or `## GT-KB Platform & Lifecycle Terms` sections has a `Source:` line within 30 lines of the heading.
- *resolution_check*: each `Source:` line's referenced DELIB-ID, file path, or specification ID is resolvable. Broken references produce ERROR-level doctor findings.
- *minimum_threshold*: at least N glossary entries cite DA records (sanity floor; catches accidental wholesale removal). N to be set during Phase 4.

**Severity.** Advisory during Phase 1 (backfill in progress). Promoted to blocking once Phase 4 verification lands.

**Rationale for staged severity.** Promoting to blocking before Phase 1 backfill completes would hard-fail every existing session. Staged severity allows the backfill to land without breakage, then locks the discipline once content coverage is sufficient.

### Artifact 4 — `DCL-CONCEPT-ON-CONTACT-001` (machine-checkable design constraint)

**Constraint.** When a load-bearing concept appears in (a) owner conversation that produces a decision, (b) a bridge proposal or review, or (c) a rule-file edit, AND the concept is not already present in `.claude/rules/canonical-terminology.md`, the concept MUST be added to the glossary before the conversation closes / the bridge proposal files / the rule edit commits.

This mirrors `GOV-06` (specify-on-contact, codified for code) at the terminology layer.

**Assertions** (implemented in Phases 3 and 4):

- *Phase 3 hook*: the UserPromptSubmit glossary-expansion hook flags terms in the owner prompt that match concept-shaped patterns but lack glossary entries, marking them as "candidate for promotion." The flagged term list is surfaced as session context.
- *Phase 4 wrap-up check*: any term the hook flagged during a session must be either (i) added to the glossary, (ii) explicitly marked deferred with owner acknowledgement, or (iii) explicitly rejected with rationale before session wrap-up succeeds.

**Severity.** Advisory during Phases 1-3. Promoted to blocking at Phase 4 wrap-up integration.

**Definition of "load-bearing concept."** A noun or noun phrase that (a) has GT-KB-specific meaning distinct from common usage, OR (b) appears as a citation target in two or more rule files, owner decisions, specs, or bridge proposals, OR (c) is named in an owner decision as a concept whose definition matters. Edge cases resolved by owner decision through normal `AskUserQuestion` channel.

## Subsumption Statement

This proposal does NOT supersede `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md`. That advisory's broader scope — the full Canonical Terminology System with Bounded Context Model — remains an open separate Prime proposal track.

The relationship is complementary, not competing:

- This Phase 0 proposal is narrow: DA-read-surface placement, four formal artifacts.
- The 2026-05-07 advisory is broader: protected core terms vs user terms, accepted/discouraged synonyms, collision handling, Agent Operating Context, Bounded Knowledge Principle, fresh-agent documentation.
- The two scopes share the canonical-terminology glossary as their substrate but address different failures. The 2026-05-07 advisory addresses startup-context bounding and term-collision governance; this proposal addresses the prior-decision consultation failure mode demonstrated in S331.

If the 2026-05-07 advisory's broader work eventually lands, this Phase 0's GOV/ADR/DCLs remain compatible: they specify *what* the glossary's role is for the DA, not *how* term collisions are resolved or *how* the broader Canonical Terminology System is structured.

## Test Plan / Verification

Phase 0 produces only formal-artifact drafts. No behavior change. Verification scope:

- *Per-artifact existence*: each of the four artifacts is insertable in MemBase via the Python API (`db.insert_spec()` for ADR/DCL/GOV with appropriate `type` field). Verifiable by `db.get_spec(id)` returning the inserted row.
- *Authority chain*: each artifact's MemBase row's `change_reason` field cites the formal-artifact-approval packet path, and the approval packet's `body_hash` matches the inserted row's body fingerprint, per the LO KB-write approval-packet pathway in `.claude/rules/loyal-opposition.md` and `GOV-ARTIFACT-APPROVAL-001`.
- *Phase 1 readiness*: the four artifacts' assertions become Phase 4's machine-checkable doctor inputs. Phase 1 cannot proceed until the four artifacts are at status `specified` in MemBase.

**Spec-to-test mapping for Phase 0:**

| Linked specification | Phase 0 test |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge proposal file exists at `bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md`; INDEX entry points at it. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal's `Specification Links` section is non-empty and cites the relevant cross-cutting and topic-specific specs. Verified by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-0-formalization` returning `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This `Test Plan / Verification` section maps each linked spec to its test. Phase 4 will execute these tests. |
| `GOV-ARTIFACT-APPROVAL-001` | No MemBase mutation occurs in Phase 0. Approval AskUserQuestions are surfaced at the closure boundary. |
| `SPEC-2098`, `SPEC-0067`, `DCL-SPEC-DA-CITATION-MANDATORY-001`, `ADR-008` | Verified by reference; this proposal extends rather than modifies them. No behavioral test in Phase 0. |

The `Applicability Preflight` and `Clause Applicability` sections below will be populated by the relevant tools and revised before submission for Codex review.

## Risk and Rollback

**Risks.**

- *Owner rejects one or more of the four artifacts.* Mitigation: resubmit as REVISED with owner-directed changes. Phase 1 waits.
- *Cited DA records or specifications are themselves found stale during Phase 1 backfill.* Mitigation: Phase 1 audit includes a DA-citation freshness check and surfaces stale citations to the owner via AskUserQuestion before backfill proceeds.
- *The 2026-05-07 advisory's broader work, when it lands, conflicts with this Phase 0's narrow framing.* Mitigation: the four artifacts here specify what the glossary's role is for the DA, leaving the broader Canonical Terminology System questions (collision handling, term governance, bounded context) to the separate track. Conflict surface is small by design.

**Rollback.** Phase 0 has no behavior side effects. Rollback = mark MemBase artifacts as `superseded` if approved-then-reverted; bridge files remain as audit trail (append-only per protocol).

## Recommended Commit Type

`feat:` — net-new governance principle, ADR, and two DCLs. Introduces new governance authority for downstream phases. Not a refactor (no restructuring), not a fix (no broken behavior repaired), not a docs change (introduces formal artifacts, not narrative).

## Files Changed

- `bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md` (this file; new)
- `bridge/INDEX.md` (new entry inserted at top: `Document: gtkb-da-read-surface-correction-phase-0-formalization` + `NEW: bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md`)

No code changes. No rule-file changes. No MemBase mutation. The four formal artifacts are drafts in this proposal text; their MemBase insertion is gated on the per-artifact AskUserQuestion approvals enumerated in § Owner Decisions / Input.

## Applicability Preflight

Self-check via `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-0-formalization --json` (run after INDEX entry is in place):

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `packet_hash: sha256:7a4dead94be9abd391b8a0039a4ea110d19586b3c895c3df9ef8934110bc27ff`

Recorded as Prime self-check evidence per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight Subsection step 5. Codex's authoritative preflight at review time should produce the same packet hash unless the proposal text is modified.

## Clause Applicability

Self-check via `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-0-formalization` (default invocation; mandatory gate):

- Exit code: `0` (pass)
- Clauses evaluated: 5
- must_apply: 4 (all with satisfying evidence found)
- may_apply: 1 (`ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`; no evidence required for may_apply)
- not_applicable: 0
- Blocking gaps: 0

| Clause | Applicability | Evidence found |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | must_apply | yes |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | may_apply | — |

No owner-waiver lines required. Codex's authoritative clause preflight at review time should produce the same result unless the proposal text is modified.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
