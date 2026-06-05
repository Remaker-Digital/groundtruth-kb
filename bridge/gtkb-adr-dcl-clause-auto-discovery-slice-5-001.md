NEW
author_identity: Claude Prime Builder (interactive)
author_harness_id: B
author_session_context_id: d1c057c9-c466-4a8b-b821-aa7c071bce13
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session, Prime Builder, explanatory output style
author_metadata_source: prime-builder interactive session

# Implementation Proposal - ADR/DCL Clause Auto-Discovery Slice 5.1 (deterministic hybrid, advisory-first)

bridge_kind: implementation_proposal
Document: gtkb-adr-dcl-clause-auto-discovery-slice-5
Version: 001
Author: Claude Prime Builder, harness B
Date: 2026-06-05 UTC
Recipient: Loyal Opposition
Project Authorization: PAUTH-PROJECT-GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001-ADR-DCL-AUTO-DISCOVERY-SLICE-5-1-DETERMINISTIC-HYBRID-ADVISORY-FIRST
Project: PROJECT-GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001
Work Item: GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001
work_item_ids: [GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001]
target_paths: ["scripts/adr_dcl_applicability_discovery.py", "platform_tests/scripts/test_adr_dcl_applicability_discovery.py", ".claude/skills/verify/SKILL.md", ".claude/skills/bridge/SKILL.md"]
requires_verification: true
implementation_scope: slice_5_1_deterministic_advisory_discovery

Recommended commit type: feat(governance)

---

## Claim

Implement Slice 5.1 of `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001`: a
deterministic, **advisory-only** auto-discovery surface that, given a bridge
proposal/report, ranks the WHOLE ADR/DCL corpus in MemBase for candidate
applicability and emits a "Candidate Applicable ADR/DCLs" advisory section.
Declared triggers (the existing registered clauses) remain authoritative; a
deterministic heuristic surfaces additional `may_apply` candidates for records
not yet registered. The output is advisory (never gate-failing). The existing
five blocking clauses and the exit-5 mandatory gate in
`scripts/adr_dcl_clause_preflight.py` are unchanged.

This is a fresh follow-on thread per the WITHDRAWN slice-2 packet's instruction
(`bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-003.md`): the
blocking-promotion core (Slices 1-3) is already VERIFIED, and this slice
delivers the genuine remaining delta - coverage via auto-discovery - from the
`config/governance/adr-dcl-clauses.toml` header roadmap ("Slice 5 may add
semantic discovery").

## Scope Boundaries (explicit out-of-scope)

Out of scope for Slice 5.1: changing the five existing blocking clauses;
changing the exit-5 gate semantics; promoting any auto-discovered candidate to
blocking; embeddings/ChromaDB-assisted discovery (deterministic-only this
slice); declared-applicability schema fields on ADR/DCL MemBase records (later
slice); any MemBase spec/schema mutation.

## Owner Decisions / Input

This proposal depends on owner approval, collected via `AskUserQuestion` this
session (S421) and captured durably:

- `DELIB-S421-ADR-DCL-AUTO-DISCOVERY-SLICE-5-DESIGN` (`outcome=owner_decision`)
  records the four AUQ selections: (1) advance
  `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001`; (2) Slice 5 deterministic
  auto-discovery; (3) Hybrid (declared + heuristic) discovery model; (4)
  Advisory-first (ratchet) enforcement posture; plus the explicit authorization
  to file Slice 5.1 as scoped.
- `PAUTH-PROJECT-GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001-ADR-DCL-AUTO-DISCOVERY-SLICE-5-1-DETERMINISTIC-HYBRID-ADVISORY-FIRST`
  authorizes implementation under the bounded scope above (owner-decision
  `DELIB-S421-ADR-DCL-AUTO-DISCOVERY-SLICE-5-DESIGN`); allowed mutation classes
  `new_source_script` / `tests` / `governance_config_additive` / `skill_docs`;
  forbids changes to the 5 blocking clauses, the exit-5 gate, and MemBase
  spec/schema.

No further owner decision is required for this advisory-only slice. Promotion of
any discovered candidate to blocking is a separate future owner decision (the
documented Slice-4 ratchet).

## Requirement Sufficiency

Existing requirements are sufficient. The governing requirements are: the
2026-05-06 owner directive + advisory (auto-discover which ADR/DCL records could
apply to a proposal); `DELIB-S421-ADR-DCL-AUTO-DISCOVERY-SLICE-5-DESIGN` (this
session's design decisions and guardrails); and the two DCLs whose applicability
machinery this slice extends. No new specification is required for an
advisory-only first slice; the deterministic-only and advisory-only guardrails
keep the change within existing constraints. A future slice that promotes
candidates to blocking, or adds a declared-applicability schema to ADR/DCL
records, would require new owner promotion evidence and is out of scope here.

## Prior Deliberations

- `DELIB-S421-ADR-DCL-AUTO-DISCOVERY-SLICE-5-DESIGN` - this session's owner
  design decisions (hybrid + advisory-first) and the authorization to file.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/ADR-DCL-CLAUSE-TEST-ENFORCEMENT-ADVISORY-2026-05-06.md`
  - the originating Loyal Opposition advisory; point 2 (candidate applicability
  discovery; deterministic triggers authoritative, embeddings assist-only) and
  the anticipated owner decisions (lines 139-142) directly scope this slice.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-001.md` (Slice 1, GO at `-002`)
  - advisory clause-preflight precedent.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-008.md`
  (VERIFIED) - the blocking-promotion core this slice builds atop; cited as
  precedent per the WITHDRAWN `-003` instruction.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-003.md` (WITHDRAWN) -
  established that the core is done and a genuine follow-on must be a fresh
  thread.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - filed through the bridge index as a
  versioned proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the constraint the
  existing applicability preflight enforces; auto-discovery extends
  candidate-applicability surfacing for this constraint (PAUTH-linked spec).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the constraint the clause
  preflight enforces; the verification plan below maps requirements to concrete
  tests (PAUTH-linked spec).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization,
  project, and work item metadata are declared above.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - the deterministic-only guardrail: discovery
  uses no LLM classifier.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - the new discovery script and
  tests are durable tracked artifacts created under the artifact-oriented
  governance model.

## Spec-Derived Verification Plan

Tests live in `platform_tests/scripts/test_adr_dcl_applicability_discovery.py`
unless noted.

| Requirement / spec clause | Test | Command |
|---|---|---|
| Advisory-only: discovery NEVER changes exit code, even with high-overlap candidates (DELIB-S421 advisory-first guardrail) | `test_discovery_always_exits_zero` | `python -m pytest platform_tests/scripts/test_adr_dcl_applicability_discovery.py -q` |
| Known-applicable ADR/DCL surfaced as candidate - don't miss applicable records (`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`) | `test_known_applicable_record_surfaced` | (same) |
| Deterministic/stable output for fixed input - no LLM classifier (`SPEC-AUQ-NO-LLM-CLASSIFIER-001`) | `test_output_is_deterministic_for_fixed_input` | (same) |
| False-positive fixture stays not-applicable / not must_apply (advisory-first risk control) | `test_non_overlapping_record_not_flagged` | (same) |
| Existing exit-5 gate + 5 blocking clauses untouched (scope boundary) | `test_existing_clause_preflight_unchanged` (regression) | `python -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py -q` |

Pre-file code-quality gates: `ruff check` AND `ruff format --check` on the
changed `.py` files, reported in the post-implementation report (resolved via
the project venv interpreter that carries `ruff`).

## Implementation Design

1. `scripts/adr_dcl_applicability_discovery.py` (new):
   - `--bridge-id <id>`: resolve the operative bridge file via INDEX (reuse the
     resolution pattern in `scripts/adr_dcl_clause_preflight.py`); read
     `target_paths` + content tokens.
   - Load current-version ADR/DCL records from MemBase (`KnowledgeDB`; type in
     `{architecture_decision, design_constraint}`).
   - Deterministic applicability scoring per record:
     - Declared-authoritative: if the record's `spec_id` is a registered clause
       in `config/governance/adr-dcl-clauses.toml`, defer to that clause's
       trigger result (authoritative; not re-scored by heuristic).
     - Heuristic candidate signals (deterministic weighted token overlap):
       record title / spec-id tokens vs proposal content; path-like tokens in
       the record body vs `target_paths`; spec IDs co-cited by the proposal;
       DCL assertion-target tokens.
   - Classify each record: `declared` (already handled by the blocking
     preflight) | `candidate_may_apply` (score >= threshold) | `not_applicable`.
   - Emit a ranked "Candidate Applicable ADR/DCLs" advisory markdown section.
     Exit code ALWAYS 0.
2. `platform_tests/scripts/test_adr_dcl_applicability_discovery.py` (new): the
   tests in the verification plan, using fixture records / a temp MemBase for
   determinism.
3. `.claude/skills/verify/SKILL.md` and `.claude/skills/bridge/SKILL.md`: add an
   informational note that reviewers MAY run the advisory discovery to surface
   candidate ADR/DCLs beyond the registered clauses (advisory; does not change
   GO/VERIFIED gating). Doc-only.

## Risk and Rollback

- Risk: heuristic false positives (irrelevant ADR/DCLs surfaced). Mitigation:
  advisory-only (never gates); ranked output; tunable threshold; false-positive
  regression test.
- Risk: heuristic false negatives (applicable record missed). Mitigation:
  declared triggers remain authoritative and blocking via the unchanged
  preflight; discovery only ADDS candidates.
- Risk: corpus-scan performance. Mitigation: deterministic single-pass token
  scoring; bounded corpus; no embeddings.
- Rollback: the new script + test are additive; deleting them and reverting the
  two doc notes fully restores prior state. The blocking gate is untouched, so
  rollback cannot regress enforcement.

## Applicability Preflight

Generated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-auto-discovery-slice-5`:

- packet_hash: `sha256:35c2be2810b785ee9a5aaab404a6585bcf00827afe320a4270351f22906e78dc`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]` (now cited in Specification Links above)

## Clause Applicability

Generated by `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-auto-discovery-slice-5` (mandatory gate, default invocation):

- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit: 0 (pass)

| Clause | Applicability | Evidence found | Enforcement |
| --- | --- | --- | --- |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes | blocking |

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
