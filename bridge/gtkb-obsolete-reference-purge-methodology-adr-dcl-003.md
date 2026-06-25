REVISED
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 03d07d0c-f6a6-4bef-96aa-9d6a06a6ba9d-prime-builder
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory; mode=auto
author_metadata_source: interactive-prime-session

bridge_kind: governance_review

# Obsolete-Reference-Purge Methodology — ADR + DCL (Proposal 1 of PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE)

Document: gtkb-obsolete-reference-purge-methodology-adr-dcl
Version: 003
Responds to: bridge/gtkb-obsolete-reference-purge-methodology-adr-dcl-002.md (self-correction; pre-LO-review)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-24 UTC
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4794

## Self-Correction Note (pre-review)

This `-003` supersedes the pre-review drafts `-001` and `-002` before any Loyal
Opposition verdict, consolidating two author self-detected preflight corrections:
`-002` added two required cross-cutting specs the applicability preflight flagged
(`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`);
`-003` adds the explicit `### Specification-Derived Verification — Spec-to-Test Mapping`
that the ADR/DCL clause preflight (`CLAUSE-SPEC-TO-TEST-MAPPING`) requires. The
substantive ADR/DCL content is unchanged from `-001`. Numbered bridge files are
append-only, so each correction advances the thread to the next version.

## Bridge-Kind Disclosure

`bridge_kind: governance_review`. This proposal requests Loyal Opposition review of
TWO proposed governance artifacts (an ADR and a DCL). It introduces **no source
code, configuration files, scripts, hooks, or work-item state changes**. The
artifacts, once GO'd, are inserted into MemBase through the governed
`kb-adr` / `kb-spec` path with `GOV-ARTIFACT-APPROVAL-001` formal-artifact-approval
packets and explicit owner content-approval. The enforcing deterministic check
(WI-4795) is a SEPARATE follow-on implementation proposal (it requires a project
authorization and real source surface); this proposal deliberately scopes to the
decision + constraint so the foundational artifacts can be reviewed on their own
merits per the GOV-20 ADR→DCL→implementation sequence.

## Summary

Formalize the owner directive of 2026-06-24 (DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624)
as a durable, mechanically-enforceable governance rule: a change that retires or
replaces a load-bearing GT-KB implementation is not complete until a paired
obsolete-reference-purge work item removes (or quarantines-with-justification) the
references to the retired implementation from load-bearing artifacts. Adding a
prohibition that merely discourages use does NOT satisfy the obligation.

This proposal creates:
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` (the decision + context + failed
  approaches + alternatives + consequences), and
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (the machine-checkable constraint,
  whose assertions are enforced by the WI-4795 deterministic check).

## Specification Links

- `GOV-20` (Architecture Decision Governance) — governs the ADR→DCL→IPR/CVR workflow this proposal uses; the ADR is stored as `type=architecture_decision`, the DCL as `type=design_constraint` with an assertions field.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `ADR-ARTIFACT-FORMALIZATION-GATE-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — the proposed ADR + DCL are formal artifacts; insertion (post-GO) requires presentation in native review format plus a formal-artifact-approval packet and explicit owner approval. This proposal IS that native-review presentation of the full proposed text.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the directive's "remove, do not merely prohibit" requirement is a cross-cutting technical requirement; this ADR+DCL plus the WI-4795 check provide the two-layer (constraint + check) mechanical enforcement the GOV requires.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this `## Specification Links` section cites every governing spec; the proposed tests derive from the linked specs (see Verification Plan).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the post-implementation report that follows the GO on this thread will carry spec-derived verification; this proposal's `## Verification Plan (Specification-Derived)` already maps each check to a linked spec (artifact existence/typing -> `GOV-20`; formal-approval evidence -> `GOV-ARTIFACT-APPROVAL-001`; assertion run -> the DCL).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this thread is filed through the governed no-index bridge path; TAFE/dispatcher bridge state plus this status-bearing numbered file are the canonical workflow state (no aggregate queue artifact is created or required).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the methodology is itself an artifact-lifecycle trigger (a retirement triggers a purge work item); it extends the artifact-oriented stance with an active-removal obligation.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — kin constraint: forbidden-substitute reads cause divergent state claims; obsolete-reference residue is the same disease class (stale alias surfaces competing with canonical sources). Cross-references the SoT-read-discipline rationale (DELIB-20260673).
- `GOV-STANDING-BACKLOG-001` — WI-4794 and the project membership are the durable tracking surface; no markdown backlog is introduced.
- `.claude/rules/project-root-boundary.md` — all proposed artifacts live in the in-root MemBase (`E:\GT-KB\groundtruth.db`); the methodology's "load-bearing artifact" scope is in-root, and the QUARANTINE class explicitly preserves the append-only audit trail.
- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` — the authorizing owner decision and three AUQ choices (see Owner Decisions / Input).

## Prior Deliberations

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` (v1) — the authorizing owner decision; this proposal is its formalization. Includes the three AUQ choices (strip scope = residue-only-keep-guards; methodology = ADR+DCL+check; memory purge = editable-only).
- `DELIB-20260673` (v1) — parallel-session SoT fragmentation: independent sessions consulted divergent retired aliases of the same source of truth, producing state claims the owner had to reconcile by hand. Same disease class (obsolete surface contaminating session-context); motivates the active-removal obligation rather than prohibition-only.
- `DELIB-2506` (v1) — owner AUQ "Re-link to Retired Canonical (Phantom Reconciliation Disposition)": an adjacent disposition for references TO a retired canonical. This methodology generalizes the principle: references to retired implementations get a deliberate disposition (STRIP / KEEP / QUARANTINE), not silent drift.
- `DELIB-0862` (v1) — "Bridge INDEX startup comment compaction snapshot": a pre-removal snapshot was archived before removing historical comment lines from bridge/INDEX.md. Precedent for the QUARANTINE-with-justification path (snapshot/freeze before strip where auditability requires retention).
- `DELIB-S334-BOUNDED-KNOWLEDGE-COMPLEXITY-OWNER-DECISION` (v1) — owner agreement that GT-KB has a practical complexity ceiling; obsolete-reference residue inflates the effective knowledge surface an agent must reason over, so active removal serves the bounded-knowledge goal.

## Requirement Sufficiency

New requirement required before implementation. This proposal's deliverable IS the
new requirement surface: the ADR (decision) and the DCL (constraint). Per
`GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001`, spec creation from owner input has
standing authorization; the owner directive at
`DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` is the originating input.
The DCL is `specified` (not yet `implemented`) until the WI-4795 deterministic check
lands; that follow-on implementation proposal will carry its own Requirement
Sufficiency = "Existing requirements sufficient" citing this DCL.

---

## Proposed Artifact 1 — ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001

**Type:** `architecture_decision` (spec) · **Title:** Obsolete-reference purge is a standing completion obligation on significant changes.

### Decision

A change that retires or replaces a load-bearing GT-KB implementation carries a
standing obligation to REMOVE — or QUARANTINE with explicit auditability
justification — references to the retired implementation from load-bearing
artifacts. The change MUST NOT be recorded VERIFIED until a paired
obsolete-reference-purge work item exists, is linked to the retirement, classifies
the affected references as STRIP / KEEP / QUARANTINE, and has satisfied the STRIP
set. Adding a prohibition that discourages use of the retired implementation does
NOT by itself satisfy this obligation.

### Context

When GT-KB is in a good state, an agent's ability to observe surrounding artifacts
and reason from them preserves that state where explicit direction is absent.
During development/change the same property works against the platform: residual
references to a retired implementation enter session-context when an agent touches
nearby legacy artifacts and compete with the newer canonical sources. Agents
reliably reach for the obsolete information at hand rather than re-deriving from
canonical sources (a salience failure per the canonical-terminology "salience
case"). Evidence: (1) the retired `bridge/INDEX.md` aggregate (WI-4510 Phase-3
cutover, 2026-06-15) left thousands of stray operational references across docs,
tests, skill-docs, and harness memory despite a standing "do not recreate
aggregate" prohibition; (2) parallel-session SoT fragmentation where independent
sessions consulted divergent retired aliases of one source of truth
(`DELIB-20260673`); (3) the owner directive of 2026-06-24
(`DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624`).

### Failed approaches

- **Prohibition-only.** A rule discouraging recreation/use of the retired
  implementation leaves the existing distracting references in place; they keep
  contaminating session-context. (The `bridge/INDEX.md` prohibition is the
  motivating failure.)
- **Blanket string-strip.** Mechanically deleting every occurrence of a retired
  implementation's name is unsafe because retired and current implementations share
  vocabulary. The literal string `INDEX.md` named BOTH the retired `bridge/INDEX.md`
  AND the current `config/agent-control/SESSION-STARTUP-INDEX.md`; a blanket strip
  would have erased live startup infrastructure (~7,561 live references) and the
  guard machinery that keeps the aggregate retired.

### Alternatives considered

- (a) Manual periodic hygiene sweeps. Rejected: not change-triggered, not durable,
  relies on agent memory.
- (b) Prohibition + a lint that blocks NEW references to the retired implementation.
  Rejected: prevents regrowth but never removes the existing residue.
- (c) **[CHOSEN]** Change-triggered paired-purge obligation + mandatory
  STRIP/KEEP/QUARANTINE classification + a deterministic enforcement check.

### Consequences

- Every retirement-class change acquires a linked obsolete-reference-purge work item
  as part of its definition of done.
- The classification step is mandatory; the enforced unit is "an obsolete reference
  to a NAMED retired artifact," never "an occurrence of a string."
- "Load-bearing artifacts" = the agent reach-path: `CLAUDE.md`, `AGENTS.md`,
  `.claude/rules/*`, `config/agent-control/*`, startup overlays, skills, hooks,
  source, and editable harness memory. The append-only audit trail (`bridge/*`,
  `independent-progress-assessments/*`, `groundtruth-kb/evidence/*`, `.jsonl`
  transcripts, frozen snapshots) is QUARANTINE-by-nature and is never edited.
- Active guard/enforcement machinery that must NAME a retired artifact in order to
  block or detect its return is KEEP, not residue.
- Enforcement is mechanical (the DCL below + the WI-4795 deterministic check), with a
  two-phase WARN→FAIL ramp.

---

## Proposed Artifact 2 — DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001

**Type:** `design_constraint` (spec) · **Derived from:** ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001 · **Title:** Retirement-class changes must carry a linked, classified obsolete-reference-purge work item.

### Constraint

For every retirement-class artifact R — a spec transitioned to status
`retired`/`superseded`, a `RETIRE-SPEC-*` spec, or an ADR/DCL that supersedes a
prior load-bearing implementation — there MUST exist an obsolete-reference-purge
work item P such that:

1. P is linked to R (via project/source-directive linkage or an explicit `purges`
   reference);
2. P records a STRIP / KEEP / QUARANTINE classification of the affected reference
   set; and
3. P is not VERIFIED-complete unless the STRIP set's obsolete references have been
   removed (or individually re-justified as KEEP/QUARANTINE).

### Assertions (machine-checkable; enforced by the WI-4795 deterministic check)

- `logic` — For each retirement-class artifact in the evaluation window, a linked
  obsolete-reference-purge work item exists. (Enforced by the WI-4795 check;
  WARN in Phase 1, FAIL in Phase 2.)
- `logic` — `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` exists in MemBase with
  `type=architecture_decision`.
- `glob` — the deterministic check script exists once WI-4795 lands (path TBD in
  that proposal, e.g. `scripts/check_obsolete_reference_purge.py`).

### Enforcement mode

Phase 1 = WARN (advisory; surfaces unpaired retirements without blocking). Phase 2 =
FAIL (blocking at the cutover/verification gate). Promotion from WARN to FAIL is
gated on Slice-1 feedback, mirroring the established two-phase pattern of
`gtkb-adr-dcl-clause-test-enforcement`.

---

## Target Paths / KB Artifacts

target_paths: ["groundtruth.db#ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001", "groundtruth.db#DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001"]

KB-only mutation. Insertion uses the governed `kb-adr` / `kb-spec` path (exempt from
the implementation-start gate per the governed-CLI exemption) with
`GOV-ARTIFACT-APPROVAL-001` formal-artifact-approval packets and explicit owner
content-approval at insert time. No source/config/hook files are modified by this
proposal.

## Verification Plan (Specification-Derived)

Derived from the linked specs (`GOV-20`, `GOV-ARTIFACT-APPROVAL-001`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`):

1. **Artifact existence + typing.** `db.get_spec("ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001")`
   returns a row with `type=architecture_decision`; `db.get_spec("DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001")`
   returns a row with `type=design_constraint` and a non-empty assertions field.
   (Spec-derived test maps to `GOV-20` storage contract.)
2. **Formal-approval evidence.** A formal-artifact-approval packet exists at
   `.groundtruth/formal-artifact-approvals/<date>-adr-obsolete-reference-purge-obligation-001.json`
   (and the DCL counterpart) whose `full_content_sha256` matches the inserted row body.
   (Maps to `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001`.)
3. **Assertion run.** `gt assert` over the new DCL records its assertions; the
   `logic` assertion that depends on the WI-4795 check is expected `specified`-failing
   until that check lands (informational, not a regression), and this expected state
   is documented in the implementation report.
4. **Cross-reference integrity.** The DCL's `derived_from` cites the ADR; the ADR's
   consequences cite the DCL. `bridge_applicability_preflight.py` on this thread
   reports `missing_required_specs: []`.

### Specification-Derived Verification — Spec-to-Test Mapping

This is a governance-artifact-creation proposal; no source or tests execute at
proposal time. The spec-to-test mapping below is the plan the post-GO implementation
report will execute and carry forward as Specification-Derived Verification. Each
linked spec maps to a concrete, named test:

| Linked spec | Spec-to-test mapping | Command |
|-------------|----------------------|---------|
| `GOV-20` (ADR/DCL storage contract) | `test_obsolete_reference_purge_artifacts_typed` asserts `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` has `type=architecture_decision` and `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` has `type=design_constraint` with a non-empty assertions field | `python -m pytest platform_tests/governance/test_obsolete_reference_purge_methodology.py -q` |
| `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | `test_obsolete_reference_purge_approval_packets` asserts a formal-artifact-approval packet exists per artifact with `full_content_sha256` matching the inserted row body | `python -m pytest platform_tests/governance/test_obsolete_reference_purge_methodology.py -q` |
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (assertions) | the DCL's assertions are recorded via `gt assert`; the WI-4795-dependent `logic` assertion is expected `specified`-failing until that check lands (documented as expected, not a regression) | `gt assert --spec DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` |

`ruff check` and `ruff format --check` apply at the WI-4795 check-implementation stage
(this proposal adds no Python source). The post-GO implementation report will carry
executed-command output for each row above; this proposal records the mapping so the
verification is spec-derived rather than test-pass-only.

## Risk / Rollback

- **Risk:** the DCL is `specified`-not-`implemented` until WI-4795 lands, so the
  obligation is documented but not yet mechanically blocking. Mitigation: Phase-1
  WARN is acceptable; the owner directive explicitly sequences ADR+DCL before the
  check, and the project tracks WI-4795 as the immediate follow-on.
- **Risk:** mis-scoping "retirement-class artifact" could over- or under-fire the
  future check. Mitigation: the DCL fixes the trigger set explicitly (retired/
  superseded specs, RETIRE-SPEC-*, superseding ADR/DCL) and the check ships WARN-first
  for a feedback window.
- **Rollback:** ADR/DCL are append-only MemBase rows; a superseding version with
  status `retired` reverses the decision without deleting history. No source is
  touched, so there is no code rollback surface.

## Owner Decisions / Input

This proposal depends on owner approval and cites the AUQ-only owner-decision rule.
Authorizing evidence (AskUserQuestion, 2026-06-24, archived as
`DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624`):

- **Q1 Strip scope → "Residue only, keep guards."** The ADR's Consequences encode
  this: guard machinery that names a retired artifact to block it is KEEP; the
  append-only audit trail is QUARANTINE; only obsolete operational framing is STRIP.
- **Q2 Methodology → "ADR + DCL + deterministic check."** This proposal delivers the
  ADR + DCL; WI-4795 delivers the check. Directly authorizes this artifact set.
- **Q3 Memory purge → "Editable memory only; transcripts stay."** Reflected in the
  ADR's load-bearing-artifact scope (editable harness memory in scope; `.jsonl`
  transcripts QUARANTINE).
- **"Please proceed"** (2026-06-24) — owner authorized autonomous progress on the
  project, with AUQ/grill reserved for genuine input needs.

A formal-artifact-approval packet presenting the full ADR and DCL body for explicit
content-approval will be produced at insertion time (post-GO), per
`GOV-ARTIFACT-APPROVAL-001`; this proposal is the native-review presentation that
precedes that packet.
