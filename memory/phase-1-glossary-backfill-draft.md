# DRAFT — Phase 1 Bridge Proposal: Glossary Backfill

**Status:** working draft. Not filed. Becomes `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-001.md` after Phase 0 GO + the four formal artifacts are owner-approved into MemBase.

---

# Implementation Proposal — GTKB-DA-READ-SURFACE-CORRECTION Phase 1: Glossary Backfill

- Status: NEW
- Date: TBD (post Phase 0 GO)
- Session: TBD
- Author: Prime Builder (Claude Code, harness B)
- bridge_kind: prime_implementation_proposal
- Umbrella work item: `GTKB-DA-READ-SURFACE-CORRECTION` (Phase 1 of multi-phase plan; phases 0-6 per the revised umbrella post -003 NO-GO addressing)
- Depends on: Phase 0 GO + MemBase insertion of GOV-GLOSSARY-AS-DA-READ-SURFACE-001, ADR-DA-READ-SURFACE-PLACEMENT-001, DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001, DCL-CONCEPT-ON-CONTACT-001.

## Summary

Backfill `.claude/rules/canonical-terminology.md` with glossary entries for ~28 load-bearing concepts currently absent. The audit was completed during S331 in parallel with Phase 0 filing. This proposal enumerates the audit list, presents the proposed entries in full (including DA citations on each `Source:` line), and requests owner approval to commit the backfill.

The anchor case is `isolation` — the concept whose absence from the glossary produced the S331 wrong-frame evaluation. Its glossary entry, when present, would have surfaced the lifecycle-independence definition through normal session-start glossary loading.

## Specification Links

Cross-cutting:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (no scope conflict; rule-file path trigger)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001` — the backfill modifies a rule file; rule-file edits in this scope require owner approval as a structured change.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

Phase 0 framing (must be inserted in MemBase before Phase 1 can proceed):

- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`
- `ADR-DA-READ-SURFACE-PLACEMENT-001`
- `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001`
- `DCL-CONCEPT-ON-CONTACT-001`

Pre-existing glossary discipline:

- `SPEC-0067` — glossary maintenance discipline.
- `DCL-SPEC-DA-CITATION-MANDATORY-001` — citation discipline at spec layer; Phase 1 implements parallel discipline at glossary layer.
- `SPEC-2098`, `ADR-008` — Deliberation Archive authority.
- Bridge thread `gtkb-canonical-terminology-surface-implementation` (12 versions, VERIFIED) — original glossary surface authority.

## Prior Deliberations

The four lifecycle-independence DA records that anchor the `isolation` entry:

- "GT-KB platform supports only one developed application at a time (lifecycle-independence contract)" — S319, 2026-04-28.
- "Owner directive update: industry-alignment critique for GT-KB/application separation" — 2026-04-22.
- "S321 owner directive: platform app non specific" — S321.
- "GTKB-ISOLATION-002 Phase 2 root and repository topology plan" — 2026-04-22.

S331 in-session decisions:

- The bias / salience distinction owner-acknowledged in S331 (informs `bias case` and `salience case` glossary entries).
- The placement-vs-enforcement framing (informs `placement` glossary entry).
- The glossary-as-DA-read-surface owner-agreement (informs `glossary as DA read surface` glossary entry; cross-references the Phase 0 artifacts).

DA records anchoring other audited concepts (per-entry citations in § Proposed Entries):

- `DELIB-S324-PB-INTERROGATION-DIRECTIVE` (interrogative default).
- `DELIB-S331-PROSE-DECISION-ASK-FAILURE` (AskUserQuestion / AUQ; owner-decision tracker).
- Various harness-identity and role-assignment owner decisions.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (deterministic services; cited under several tooling entries).

## Owner Decisions / Input

Authorizing context:

- Phase 0 GO (assumed at Phase 1 filing).
- Owner approval of all four Phase 0 formal artifacts (assumed).

Future owner approvals this proposal will surface (each via AskUserQuestion at the appropriate moment, one at a time):

1. Approval of the audit list scope (the ~28 concepts proposed for backfill).
2. Per-entry approval for any glossary entries the owner wants to revise before committing (the proposal will request a single AUQ confirming the batch, with the option to redirect specific entries for owner-authored alternatives).
3. Approval to mark `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` severity from advisory to blocking once the backfill lands and Phase 4 verification passes (deferred to Phase 4 boundary).

## Audit List — Load-Bearing Concepts Missing from Glossary

Grouped for review. Each concept becomes a glossary entry per § Proposed Entries.

**S331-coined / anchor cases (5):**
1. `isolation` — lifecycle independence; the failure case.
2. `session scope` — GT-KB / Application / GT-KB+Application enforcement boundary.
3. `bias case` — model-bias-driven failure mode.
4. `salience case` — attention-failure mode (distinct from bias).
5. `placement` — design pattern: place a resource on the model's existing reach path rather than fight bias with enforcement.

**DA-related (1):**
6. `glossary as DA read surface` — refers to `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`.

**Harness and role (3):**
7. `harness` — AI coding harness; the runtime/identity layer that implements roles.
8. `harness identity` — the persistent ID assigned to each installed harness.
9. `role assignment` (alias: `operating role`) — the binding of harness to role (Prime Builder / Loyal Opposition).

**Bridge protocol terminology (3):**
10. `bridge thread` — the multi-version conversational unit on a topic; distinct from a single bridge file.
11. `GO / NO-GO / VERIFIED` (paired entry; bridge statuses).
12. `Loyal Opposition advisory` — a Codex-initiated bridge entry distinct from a Prime-initiated proposal.

**Tooling and gates (7):**
13. `applicability preflight` — `scripts/bridge_applicability_preflight.py`.
14. `clause preflight` — `scripts/adr_dcl_clause_preflight.py`.
15. `bridge compliance gate` — `.claude/hooks/bridge-compliance-gate.py`.
16. `scanner-safe-writer` — credential-scan hook.
17. `owner-decision tracker` — `.claude/hooks/owner-decision-tracker.py`.
18. `prose decision-ask pattern` — pattern class detected by the tracker.
19. `AskUserQuestion` (alias: `AUQ`) — the only valid owner-decision channel.

**Operating constructs (10):**
20. `operating model` — the canonical operating-model artifact at `.claude/rules/operating-model.md`.
21. `work subject` (alias: `active work subject`) — the startup-payload concept; the scope-key for session work.
22. `smart poller` — the verified bridge-poller; canonical automation.
23. `OS poller` — the retired bridge-poller class; do not re-enable.
24. `doctor` — `gt platform doctor`; diagnostic surface.
25. `release manifest` — versioned enumeration of deployable components.
26. `deliberation harvest` — the DA write-side pipeline.
27. `formal-artifact-approval packet` — the per-artifact owner-approval evidence record.
28. `canonical artifact` — an artifact with formal-approval evidence and MemBase storage.
29. `interrogative default` — Prime Builder's default posture toward owner factual claims about GT-KB.

**Code-side mirrors (1):**
30. `specify-on-contact` — GOV-06; the code-side companion to `DCL-CONCEPT-ON-CONTACT-001`.

Total: 30 candidate entries (audit total slightly higher than the 28 first reported; two paired entries split). Each entry below is fully proposed.

## Proposed Entries (Anchor Cases — Full)

### isolation

**Definition:** Full-lifecycle independence between the GT-KB platform and any application built using it. The platform must be able to evolve and release on its own cadence; an application must be deployable and lifecycle-tracked independently of platform internals. Isolation is the rationale that motivates application-directory portability, asymmetric write authority, and separate-repository topology decisions; relocation of files into `applications/` is one consequence of isolation, not the definition.

**Allowed synonyms:** lifecycle independence; full-lifecycle independence (when emphasis is needed).

**Forbidden uses:** using "isolation" to mean only file-relocation under `applications/` (the S331 wrong-frame failure); using "isolation" as a synonym for "sandboxing" or "process isolation" (those are runtime concerns, not lifecycle ones).

**Source:**
- DA: "GT-KB platform supports only one developed application at a time (lifecycle-independence contract)" — S319, 2026-04-28.
- DA: "Owner directive update: industry-alignment critique for GT-KB/application separation" — 2026-04-22.
- DA: "S321 owner directive: platform app non specific".
- DA: "GTKB-ISOLATION-002 Phase 2 root and repository topology plan" — 2026-04-22.
- DA (S331 framing): owner clarification of isolation as full-lifecycle independence; ZIP-portability test; scope-bound write enforcement.

**Implementation pointer:** `applications/<name>/` placement convention per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; bridge thread family `gtkb-isolation-016` … `gtkb-isolation-018-*` for file-relocation work; future portability-test work pending separate proposal.

### session scope

**Definition:** The declared write-authority boundary for an AI session: one of `GT-KB` (writes only to GT-KB platform paths; application paths read-only), `Application` (writes only to the active application directory; platform paths read-only), or `GT-KB+Application` (exceptional; writes permitted in both, requires owner-authorized acknowledgement). Scope is declared at session start and mechanically enforced by hook-level write gating once the enforcement layer lands.

**Allowed synonyms:** work subject scope; session work-scope.

**Forbidden uses:** confusing session scope with `work subject` (work subject names the active subject area; session scope names the write-authority boundary). They overlap operationally but are distinct concepts.

**Source:**
- DA (S331): owner articulation of three-mode session scope as a runtime invariant for lifecycle independence.
- `.claude/session/work-subject.json` — current advisory-only state file.
- DA: "Owner directive update: industry-alignment critique for GT-KB/application separation" — 2026-04-22 (asymmetric safety model).

**Implementation pointer:** Currently advisory-only via `work-subject.json`. Mechanical enforcement is future work tracked under a separate proposal.

### bias case

**Definition:** A failure mode in which an AI agent, given two roughly equivalent options, reliably prefers one over another in a way that produces wrong outcomes. Distinguished from `salience case`: bias means the wrong option was actively chosen over the right one; salience means the right option was not on the candidate list at all.

**Allowed synonyms:** model bias case.

**Forbidden uses:** using "bias" loosely to mean any agent failure; the term should be reserved for cases where the right option was considered and rejected.

**Source:**
- DA (S331): owner-articulated diagnostic distinction between bias and salience as causes of agent under-use of available resources. Owner direction: prefer bias-aligned placement over coercive enforcement.

**Implementation pointer:** Used as a diagnostic frame in proposal evaluation; not a runtime construct.

### salience case

**Definition:** A failure mode in which an AI agent does not consider a relevant option because it is not on the natural retrieval path at the moment of decision. Distinguished from `bias case`: in a salience case, the correct option was never weighed; in a bias case, it was weighed and rejected.

**Allowed synonyms:** attention-salience case.

**Forbidden uses:** using "salience" as a synonym for "importance" in this glossary context; the term has the specific failure-mode meaning above.

**Source:**
- DA (S331): owner agreement that aware-but-unused resources usually indicate a placement/salience problem, not a discipline problem.

**Implementation pointer:** Diagnostic frame; informs placement decisions for resources that are aware-but-unused.

### placement

**Definition:** A design pattern in which a resource is positioned on a path the agent already traverses (e.g., the always-loaded glossary, the bridge proposal template, the session-start payload), rather than gated behind a new behavior the agent must remember to perform. Placement is bias-aligned and salience-aligned: it makes the resource reachable through existing reach-patterns rather than fighting agent defaults.

**Allowed synonyms:** bias-aligned placement; reach-path placement.

**Forbidden uses:** confusing placement with enforcement (placement makes the resource reachable; enforcement gates a behavior). Placement and enforcement are complementary; the design choice is which to apply when.

**Source:**
- DA (S331): owner articulation that strict enforcement against bias creates workaround behavior; placement on existing reach paths is the durable alternative.
- ADR-DA-READ-SURFACE-PLACEMENT-001 (Phase 0).

**Implementation pointer:** Used as the primary design lens for `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` and downstream phases.

### glossary as DA read surface

**Definition:** The architectural role assigned to `.claude/rules/canonical-terminology.md` by `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`: the glossary is the agent-side primary read path for prior-decision consultation; the Deliberation Archive is the substrate the glossary cites. Direct DA semantic search is the long-tail / audit / rationale-deep-dive path.

**Allowed synonyms:** DA read-surface placement.

**Forbidden uses:** treating the glossary as a complete substitute for the DA (it is the read path, not the substrate); treating the DA as deprecated (it remains the rationale and provenance store).

**Source:**
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` (Phase 0).
- `ADR-DA-READ-SURFACE-PLACEMENT-001` (Phase 0).
- `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` (Phase 0).
- DA (S331): owner-approved framing.

**Implementation pointer:** This entry is itself an instance of the principle: it cites the formal artifacts that define it, allowing agents to follow the citations to the substrate.

## Proposed Entries (Remaining 24 — Skeletal)

For each remaining concept, the proposal will include a full entry on the same template (definition / allowed synonyms / forbidden uses / Source / implementation pointer). Skeletal forms:

- `harness` — AI coding harness; runtime/identity layer; cite operating-role.md, harness-state/harness-identities.json.
- `harness identity` — persistent harness ID; cite operating-role.md.
- `role assignment` — harness-to-role binding; cite role-assignments.json, prime-builder-role.md, loyal-opposition.md.
- `bridge thread` — multi-version topical unit; cite file-bridge-protocol.md.
- `GO / NO-GO / VERIFIED` — bridge status terms; paired entry; cite file-bridge-protocol.md.
- `Loyal Opposition advisory` — Codex-initiated bridge entry; cite the 2026-05-07 advisory bootstrap pattern.
- `applicability preflight` — `bridge_applicability_preflight.py`; cite file-bridge-protocol.md § Mandatory Pre-Filing Preflight Subsection.
- `clause preflight` — `adr_dcl_clause_preflight.py`; cite the Slice 2 promotion bridge thread.
- `bridge compliance gate` — Write-time hook; cite GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice C.
- `scanner-safe-writer` — credential-scan hook; cite the bridge-propose skill SKILL.md.
- `owner-decision tracker` — Stop-mode hook; cite GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A.
- `prose decision-ask pattern` — pattern class; cite owner-decision-tracker.py PROSE_DECISION_PATTERNS.
- `AskUserQuestion / AUQ` — owner-decision channel; cite acting-prime-builder.md § AskUserQuestion as the Only Valid Owner-Decision Channel.
- `operating model` — `.claude/rules/operating-model.md`; cite the canonical operating-model decision (DELIB-S324-OM-DELTA-* family).
- `work subject` / `active work subject` — startup-payload concept; cite work-subject.json schema and Active Work Subject section in startup payload.
- `smart poller` — canonical bridge-poller; cite bridge-essential.md § Operational Mode + the smart-poller verification thread.
- `OS poller` — retired class; cite bridge-essential.md § Operational Mode (do-not-re-enable).
- `doctor` — `gt platform doctor`; cite the doctor implementation under groundtruth-kb/.
- `release manifest` — versioned component enumeration; cite GOV-RELEASE-MANIFEST-README-001 candidate spec.
- `deliberation harvest` — DA write-side pipeline; cite SPEC-DA-HARVEST-* family + scripts/harvest_session_deliberations.py.
- `formal-artifact-approval packet` — owner-approval evidence record; cite GOV-ARTIFACT-APPROVAL-001 + .groundtruth/formal-artifact-approvals/.
- `canonical artifact` — an artifact with formal-approval evidence; cite GOV-ARTIFACT-APPROVAL-001.
- `interrogative default` — PB posture toward owner factual claims; cite DELIB-S324-PB-INTERROGATION-DIRECTIVE + operating-model.md §1 + prime-builder-role.md.
- `specify-on-contact` — GOV-06; code-side companion to DCL-CONCEPT-ON-CONTACT-001; cite GOV-06.

## Test Plan / Verification

Spec-to-test mapping:

| Linked specification | Phase 1 test |
|---|---|
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` | After backfill, every audited concept has a glossary entry whose `Source:` line resolves. |
| `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` | Doctor check (Phase 4) passes against the backfilled glossary; advisory severity at backfill time. |
| `DCL-CONCEPT-ON-CONTACT-001` | Backfill itself satisfies the constraint for the audited concepts; future concept arrivals are governed by Phase 3 hook. |
| `SPEC-0067` | Glossary continues to be maintained; backfill increases coverage. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal cites all relevant specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests above are executed against the backfilled glossary; results recorded in the Phase 1 implementation report. |

Tests:

1. *S331 anchor-case regression*: confirm a new glossary entry exists for `isolation` with a non-empty definition citing the four lifecycle-independence DA records. Verifiable via `grep -A 30 "^### isolation$" .claude/rules/canonical-terminology.md`.
2. *Citation resolution*: each new entry's `Source:` line cites at least one resolvable target (DELIB-ID, file path, or SPEC-ID). Phase 4's resolver script validates this; advisory severity for now.
3. *Doctor smoke*: `gt project doctor` (or equivalent) runs without ERRORs introduced by the backfill.

## Risk and Rollback

Risks:

- Backfilled definitions misrepresent owner intent. Mitigation: each anchor-case entry cites the verbatim owner statement; the audit list approval AUQ surfaces the entries before commit.
- Backfill triggers `canonical-terminology.md` doctor checks that were previously passing. Mitigation: dry-run doctor before commit; revise entries to satisfy any new check.

Rollback: rule-file edits are git-tracked; revert is a single git operation. No MemBase state is mutated by Phase 1.

## Recommended Commit Type

`feat:` — new governance surface (DA pointers in glossary entries) layered onto an existing rule file. Adds capability rather than fixing or refactoring.

## Files Changed

- `.claude/rules/canonical-terminology.md` — substantial addition (~30 new entries plus possible reorganization).

No code, no MemBase mutation in Phase 1 implementation itself.

## Applicability Preflight

To be populated against the live bridge file before INDEX entry, then re-run with `--bridge-id` after.

## Clause Applicability

To be populated by clause preflight after INDEX entry.
