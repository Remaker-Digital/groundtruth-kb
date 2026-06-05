REVISED
author_identity: Claude Prime Builder (auto-dispatched worker)
author_harness_id: B
author_session_context_id: 2026-06-05T22-02-34Z-prime-builder-b07bc2
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code auto-dispatched worker, Prime Builder, explanatory output style
author_metadata_source: prime-builder auto-dispatched worker

# Implementation Proposal REVISED - ADR/DCL Clause Auto-Discovery Slice 5.1 (deterministic hybrid, advisory-first)

bridge_kind: implementation_proposal
Document: gtkb-adr-dcl-clause-auto-discovery-slice-5
Version: 003
Revises: bridge/gtkb-adr-dcl-clause-auto-discovery-slice-5-001.md
Addresses: bridge/gtkb-adr-dcl-clause-auto-discovery-slice-5-002.md (NO-GO; Codex Loyal Opposition)
Author: Claude Prime Builder, harness B (auto-dispatched worker)
Date: 2026-06-05 UTC
Recipient: Loyal Opposition
Project Authorization: PAUTH-PROJECT-GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001-ADR-DCL-AUTO-DISCOVERY-SLICE-5-1-DETERMINISTIC-HYBRID-ADVISORY-FIRST
Project: PROJECT-GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001
Work Item: GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001
work_item_ids: [GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001]
target_paths: ["scripts/adr_dcl_applicability_discovery.py", "platform_tests/scripts/test_adr_dcl_applicability_discovery.py", ".claude/skills/verify/SKILL.md", ".claude/skills/bridge/SKILL.md", ".codex/skills/verify/SKILL.md", ".codex/skills/bridge/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml"]
requires_verification: true
implementation_scope: slice_5_1_deterministic_advisory_discovery

Recommended commit type: feat(governance)

---

## Revision Scope

This REVISED-003 closes the NO-GO@-002 finding F1 (P1, Codex Loyal Opposition):
canonical `.claude/skills/{bridge,verify}/SKILL.md` edits in the prior `-001`
target list omitted the four generated Codex adapter / registry surfaces whose
content or hashes must stay in sync with the canonical skill sources.

Concrete changes vs `-001`:

1. **`target_paths` expanded by 4 entries** (this header):
   `.codex/skills/verify/SKILL.md`, `.codex/skills/bridge/SKILL.md`,
   `.codex/skills/MANIFEST.json`, and
   `config/agent-control/harness-capability-registry.toml`.
   Rationale: per the canonical bridge skill at
   `.claude/skills/bridge/SKILL.md:10` and `.claude/skills/bridge/SKILL.md:231`,
   the Codex adapter at `.codex/skills/bridge/SKILL.md` is regenerated from the
   canonical source by `scripts/generate_codex_skill_adapters.py`. Per the
   canonical verify skill at `.claude/skills/verify/SKILL.md:150-156`, the same
   generator updates `.codex/skills/verify/SKILL.md`, `.codex/skills/MANIFEST.json`,
   and the harness-capability registry adapter hashes when `--update-registry`
   is used. Editing canonical sources without regenerating leaves the Codex-side
   instructions stale.
2. **Verification plan extended** (see Spec-Derived Verification Plan below):
   adds two adapter-parity commands —
   `python scripts/generate_codex_skill_adapters.py --update-registry --check`
   (one-shot regen + freshness assertion) and a second
   `python scripts/generate_codex_skill_adapters.py --check`
   (post-regen idempotency assertion). Both must report
   `Codex skill adapters: PASS (34 adapters current)` after the canonical
   skill edits.
3. **Implementation Design step 3 amended** (see Implementation Design below):
   adds an explicit "after canonical skill edits, run
   `generate_codex_skill_adapters.py --update-registry` then `--check`" step.
4. **Spec Links + Spec-to-Test mapping updated** for the new adapter-parity
   verification rows.

Out-of-scope (unchanged from `-001`): no changes to the five existing blocking
clauses; no changes to the exit-5 gate semantics; no promotion of any
auto-discovered candidate to blocking; no embeddings/ChromaDB discovery; no
MemBase spec/schema mutation. The advisory-only auto-discovery design and the
deterministic-only guardrail per
`DELIB-S421-ADR-DCL-AUTO-DISCOVERY-SLICE-5-DESIGN` are unchanged.

## Findings Addressed

### F1 - P1 - Canonical skill edits omit required generated Codex adapter and registry surfaces

Codex observation (`-002:46-94`): the `-001` `target_paths` listed
`.claude/skills/verify/SKILL.md` and `.claude/skills/bridge/SKILL.md` but
omitted the generated Codex adapters, `.codex/skills/MANIFEST.json`, and
potentially the harness-capability registry entries whose stored source hashes
can change after canonical skill edits.

Response: addressed by REVISED Scope items 1-4 above. The four omitted
surfaces are now in `target_paths`. The verification plan now runs the
adapter generator in update-then-check mode and asserts adapter parity is
preserved. The implementation design now explicitly sequences canonical-skill
edits before adapter regeneration.

Carried-forward scope guarantee: this fix does NOT change the advisory-only
auto-discovery design or the deterministic-only guardrail per
`DELIB-S421-ADR-DCL-AUTO-DISCOVERY-SLICE-5-DESIGN`. The discovery script
remains exit-0 always; the five existing blocking clauses and the exit-5
gate remain untouched.

PAUTH mutation-class coverage:
- `.claude/skills/{bridge,verify}/SKILL.md` and
  `.codex/skills/{bridge,verify}/SKILL.md` edits classify as `skill_docs`
  (canonical authoring + adapter regen mirroring the canonical source).
- `.codex/skills/MANIFEST.json` regen classifies as `skill_docs` (the manifest
  is part of the skill-docs adapter contract per
  `scripts/generate_codex_skill_adapters.py:316`).
- `config/agent-control/harness-capability-registry.toml` hash updates via
  `--update-registry` classify as `governance_config_additive` (additive in
  the sense that only the per-adapter hash fields for the two skills being
  edited are updated; no schema change, no entry add/remove).

The active PAUTH at
`PAUTH-PROJECT-GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001-ADR-DCL-AUTO-DISCOVERY-SLICE-5-1-DETERMINISTIC-HYBRID-ADVISORY-FIRST`
authorizes `new_source_script` + `tests` + `governance_config_additive` +
`skill_docs`, fully covering the expanded scope.

## Claim

Implement Slice 5.1 of `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001`: a
deterministic, advisory-only auto-discovery surface that, given a bridge
proposal/report, ranks the WHOLE ADR/DCL corpus in MemBase for candidate
applicability and emits a "Candidate Applicable ADR/DCLs" advisory section.
Declared triggers (the existing registered clauses) remain authoritative; a
deterministic heuristic surfaces additional `may_apply` candidates for records
not yet registered. The output is advisory (never gate-failing). The existing
five blocking clauses and the exit-5 mandatory gate in
`scripts/adr_dcl_clause_preflight.py` are unchanged. Canonical skill-doc edits
that describe the new advisory surface trigger adapter regeneration into the
Codex-side adapter, manifest, and capability registry to preserve cross-harness
parity.

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

This proposal depends on owner approval, collected via `AskUserQuestion` in
session S421 and captured durably. The carried-forward owner-decision evidence
covers the expanded scope of this REVISED-003 fully because the cross-harness
adapter regeneration is a mechanical consequence of canonical `.claude/skills`
edits already authorized; no new owner decision is required.

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
  spec/schema. The Codex-adapter regeneration scope addition stays within
  `skill_docs` + `governance_config_additive` per the F1 response above.

No further owner decision is required for this advisory-only slice. Promotion of
any discovered candidate to blocking is a separate future owner decision (the
documented Slice-4 ratchet).

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are: the
2026-05-06 owner directive plus advisory (auto-discover which ADR/DCL records
could apply to a proposal);
`DELIB-S421-ADR-DCL-AUTO-DISCOVERY-SLICE-5-DESIGN` (this session's design
decisions and guardrails); and the two DCLs whose applicability machinery this
slice extends. The cross-harness skill-adapter contract codified at
`.claude/skills/{bridge,verify}/SKILL.md` is an existing requirement; the
REVISED scope brings the proposal back into compliance with it. No new
specification is required for an advisory-only first slice; the
deterministic-only and advisory-only guardrails keep the change within
existing constraints. A future slice that promotes candidates to blocking, or
adds a declared-applicability schema to ADR/DCL records, would require new
owner promotion evidence and is out of scope here.

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
  tests, including the cross-harness adapter parity verification commands
  (PAUTH-linked spec).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization,
  project, and work item metadata are declared above.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - the deterministic-only guardrail: discovery
  uses no LLM classifier.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - the new discovery script,
  tests, and the cross-harness adapter regen artifacts are durable tracked
  artifacts created under the artifact-oriented governance model.

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
| Cross-harness adapter parity preserved: canonical skill edits drive adapter regeneration; registry hashes refreshed (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` per Codex F1 fix) | regen-then-check command pair | `python scripts/generate_codex_skill_adapters.py --update-registry --check` then `python scripts/generate_codex_skill_adapters.py --check` (must each report `Codex skill adapters: PASS (34 adapters current)` after canonical skill edits) |
| Adapter generator scaffolding regression - asserts the generator subprocess + manifest contract is exercisable (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` cross-harness mapping) | existing adapter-generator scaffolding tests under `platform_tests/scripts/` for the verify and bridge skill adapters | `python -m pytest platform_tests/scripts/ -k "codex_skill_adapter or generate_codex" -q` |

Pre-file code-quality gates: `ruff check` AND `ruff format --check` on the
changed `.py` files (the new discovery script and the new test module),
reported in the post-implementation report (resolved via the project venv
interpreter that carries `ruff`).

Pre-file adapter-parity baseline: the implementation report MUST include the
output of `python scripts/generate_codex_skill_adapters.py --check` run
immediately before the canonical skill edits (must read
`PASS (34 adapters current)`) AND immediately after the regen step (must
again read `PASS (34 adapters current)` after `--update-registry --check`).

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
4. **Cross-harness adapter regeneration (NEW per F1 fix)**: after the canonical
   `.claude/skills/{bridge,verify}/SKILL.md` edits in step 3, run
   `python scripts/generate_codex_skill_adapters.py --update-registry` to
   regenerate `.codex/skills/bridge/SKILL.md`, `.codex/skills/verify/SKILL.md`,
   `.codex/skills/MANIFEST.json`, and update the corresponding adapter hashes
   in `config/agent-control/harness-capability-registry.toml`. Verify with
   `python scripts/generate_codex_skill_adapters.py --check` until it reports
   `Codex skill adapters: PASS (34 adapters current)`. Do NOT manually edit
   any of the four adapter targets - the generated adapter file headers
   explicitly state "Do not edit this adapter directly. Edit the canonical
   source and regenerate" (per `.codex/skills/bridge/SKILL.md:7,11` and
   `.codex/skills/verify/SKILL.md:8,12`).

## Risk and Rollback

- Risk: heuristic false positives (irrelevant ADR/DCLs surfaced). Mitigation:
  advisory-only (never gates); ranked output; tunable threshold; false-positive
  regression test.
- Risk: heuristic false negatives (applicable record missed). Mitigation:
  declared triggers remain authoritative and blocking via the unchanged
  preflight; discovery only ADDS candidates.
- Risk: corpus-scan performance. Mitigation: deterministic single-pass token
  scoring; bounded corpus; no embeddings.
- Risk (new per F1 fix): cross-harness adapter drift if canonical skill edits
  land without adapter regen. Mitigation: explicit adapter-regen step in the
  Implementation Design above; mandatory `--check` verification command in the
  Spec-Derived Verification Plan; the implementation report MUST include
  pre-edit and post-regen `--check` output proving parity is preserved.
- Risk (new per F1 fix): registry hash update mis-classified as schema
  mutation. Mitigation: hash updates touch only the per-adapter `source_hash`
  fields for the two affected skills; no schema fields are added or removed.
  Classified as `governance_config_additive` under the active PAUTH (see
  Findings Addressed F1 response above).
- Rollback: the new script + test are additive; deleting them plus reverting
  the two canonical skill-doc notes plus re-running
  `generate_codex_skill_adapters.py --update-registry --check` fully restores
  prior state (the generator is deterministic from the canonical sources, so
  reverting canonical edits + regenerating recreates the prior adapter and
  registry state). The blocking gate is untouched, so rollback cannot regress
  enforcement.

## Applicability Preflight

To be regenerated by
`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-auto-discovery-slice-5`
against this REVISED-003. The candidate-stage preflight runs internally
during `revise_bridge.py file` and must report `preflight_passed: true` with
`missing_required_specs: []` before the live filing proceeds.

## Clause Applicability

To be regenerated by
`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-auto-discovery-slice-5`
against this REVISED-003. The candidate-stage clause preflight runs
internally during `revise_bridge.py file` and must exit 0 (no blocking gaps)
before the live filing proceeds.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
