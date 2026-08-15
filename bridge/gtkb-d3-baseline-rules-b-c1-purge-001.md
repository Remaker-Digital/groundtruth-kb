NEW
::init gtkb lo
::open build

# gtkb-d3-baseline-rules-b-c1-purge — D3 Category B+C1 purge of legacy TAFE wording from the canonical baseline rules tree

bridge_kind: prime_proposal
Document: gtkb-d3-baseline-rules-b-c1-purge
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-08-14 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: c9a56647-1070-42be-b4f0-ae55fcc8c8c5
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via `::init gtkb pb`

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-6002-D3-BASELINE-RULES-CATEGORY-B-C1-PURGE
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6002

target_paths: [".harness-baseline-configuration/rules/*.md", "config/agent-control/gtkb-*.md", ".claude/rules/*.md", "platform_tests/scripts/test_d3_baseline_rules_purge_census.py", ".groundtruth/formal-artifact-approvals/**"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The always-loaded rule surfaces still name the retired legacy TAFE dispatcher as
the canonical bridge state authority. Because these files auto-load into every
session, they actively steer workers toward a substrate that is disabled and
being purged, and they invite repair proposals against a component slated for
deletion. This proposal executes the D3 Category B and C1 purge on the canonical
baseline rules tree.

Scope is deliberately limited to the two categories whose disposition prior
owner decisions already settled, so the slice carries no judgment calls. A
categorization pass performed in session `c9a56647` measured the canonical tree
`.harness-baseline-configuration/rules/**` at **111 matching lines across 13
files** for the pattern set `TAFE|dispatcher[ _-]daemon|smart poller|OS poller`:

| Category | Count | Disposition | Settled by |
| --- | ---: | --- | --- |
| B — names the canonical bridge state store | 46 | rename to `bridge state` | `DELIB-20260807011969` B1 |
| C1 — dated cutover references | 12 | rewrite present-tense, drop the event | `DELIB-20260807011969` B2 |
| A1 — live-dispatcher claims | 47 | **deferred** to a later slice | — |
| A2 — retired/historical narrative | 6 | **deferred** to a later slice | — |

Concentration: `bridge-essential.md` 34, `canonical-terminology.md` 19,
`file-bridge-protocol.md` 14, `session-bootstrap.md` 9,
`prime-bridge-collaboration-protocol.md` 6, `way-of-working.md` 6.

`.harness-baseline-configuration/rules/**` is the canonical edit target.
`config/agent-control/gtkb-*.md` and `.claude/rules/*.md` are one-way
projections regenerated from it by
`scripts/generate_rule_compatibility_projections.py`, whose module docstring
states the generator "never reads a retained projection as authority and never
mutates a canonical file." They appear in `target_paths` only as regeneration
output. Editing a projection directly would be undone by the next generator
run — the failure mode `DELIB-20260807011940` amendment 2 records for the
skills trees.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` — establishes obsolete-reference
  purge as a standing completion obligation; this slice discharges part of that
  obligation for the retired TAFE dispatcher.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` — requires retirement-class changes
  to carry a linked, classified obsolete-reference purge; the B/C1/A1/A2
  classification above is that classification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs bridge audit-trail discipline and is
  the surface most affected: `bridge-essential.md` and `file-bridge-protocol.md`
  carry 48 of the 111 measured lines between them.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — state claims must derive from fresh
  canonical reads; rule text naming a retired store as canonical authority
  directs workers to a stale substitute.
- `GOV-ARTIFACT-APPROVAL-001` — `.harness-baseline-configuration/rules/*.md` are
  protected narrative artifacts, so each file touched requires a
  formal-artifact-approval packet before its write.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this
  proposal to cite every relevant governing specification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the
  project/authorization/work-item triple carried in the metadata block above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the
  spec-derived verification plan below before `VERIFIED`.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — satisfied by the five
  specs linked into the PAUTH at issuance.

## Prior Deliberations

- `DELIB-20260807011968` — owner standing directive: the legacy TAFE dispatcher
  is obsolete and being purged, not paused. This proposal is purge work under
  that directive; it does not repair, restore, or re-enable the substrate.
- `DELIB-20260807011937` — D3 purge scope: live agent-facing direction only,
  explicitly including `.claude/rules/**` and `config/agent-control/**` and
  explicitly excluding append-only bridge/deliberation/MemBase history. This
  slice stays inside that boundary and touches no audit history.
- `DELIB-20260807011969` — D3 Category B replacement term. This proposal applies
  B1 (`→ bridge state`) and B2 (dated references rewritten present-tense) rather
  than choosing a term, which the gate forbids reopening. It introduces no
  competing name.
- `DELIB-20260807011940` — D3 scope amendments; amendment 2 is why projections
  are regenerated rather than hand-edited.
- `DELIB-20260806011917` — owner standing directive on correcting direction:
  purge at the source rather than layering counter-instructions. This slice
  deletes and rewrites the obsolete wording; it adds no "ignore TAFE" clause.
- `DELIB-20260813010009` — the owner AUQ decisions of 2026-08-14 that scope this
  slice to B+C1 and route its authorization through `WI-6002`.

## Owner Decisions / Input

This proposal depends on owner approval and cites the following AskUserQuestion
evidence, archived at `DELIB-20260813010009`
(`source_type=owner_conversation`, `outcome=owner_decision`,
AUQ id `AUQ-2026-08-14-c9a56647-d3-baseline-rules-b-c1`):

1. **Slice scope** — asked which categories the slice should cover. Owner
   answered *"B + C1 only — 58 pre-decided edits"*, deferring the 53 A-class
   judgment lines to a separate slice.
2. **Authorization route** — asked how the slice should be authorized given
   that every D3 work item carries `project = None`. Owner answered *"Route via
   WI-6002 + narrow PAUTH"*, directing issuance of one narrow authorization
   scoped to `WI-6002`.
3. **Standing directive, this session** — the owner directed that the purge
   proceed now, "before these erroneous fixes related to the obsolete
   dispatcher take root," and confirmed
   `E:\GT-KB\.harness-baseline-configuration/rules/` as the tree to edit.

The PAUTH issued from decision 2 cites `DELIB-20260813010009` as its
`owner_decision_deliberation_id`.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement is needed.
The governing requirements are `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`
and `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` for the purge obligation, and
`DELIB-20260807011969` B1/B2 for the disposition of both categories in scope.
Both dispositions are already settled by owner decision, so this slice applies
existing requirements rather than establishing new ones.

## Spec-Derived Verification Plan

The acceptance criterion is the one `WI-6035` already states: *a census showing
zero legacy-phrasing matches in the touched surfaces and no competing
replacement term introduced.* A new deterministic guard test encodes it.

| Linked specification | Test / command | Expected result |
| --- | --- | --- |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`, `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | `test_no_b_class_state_store_wording` in the new census module | Zero occurrences of `TAFE-backed`, `dispatcher/TAFE`, `TAFE/dispatcher`, `TAFE state`, `TAFE bridge state` across `.harness-baseline-configuration/rules/**` |
| `DELIB-20260807011969` B1 (term uniformity) | `test_no_competing_replacement_term` | `bridge state` is the only replacement form present; `canonical bridge state` absent |
| `DELIB-20260807011969` B2 (dated references) | `test_no_dated_cutover_references` | Zero `2026-06-15 cutover` / `WI-4510 Phase-3 cutover` constructions in the tree |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | projection-parity check | `config/agent-control/gtkb-*.md` and `.claude/rules/*.md` regenerate clean from the edited baseline with no manual divergence |
| `GOV-ARTIFACT-APPROVAL-001` | approval-packet presence check | One packet per protected narrative file touched, each with matching content hash |
| Regression floor (no collateral breakage) | existing rule/governance suites | `test_fab05_rule_file_retirement.py`, `test_no_active_smart_poller_wording.py`, `test_groundtruth_governance_adoption.py` all pass unchanged |

Commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_d3_baseline_rules_purge_census.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_fab05_rule_file_retirement.py platform_tests/test_no_active_smart_poller_wording.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe scripts/generate_rule_compatibility_projections.py --check
```

**Pre-existing CI risk assessed and found absent.** No test asserts the B-class
wording as required text. Every occurrence inside `platform_tests` and
`groundtruth-kb/tests` lives under
`groundtruth-kb/tests/fixtures/scaffold_golden/`, which are expected-output
snapshots for the adopter scaffold rather than assertions about the baseline
tree. Those fixtures are out of scope here (see Risk / Rollback).

## Risk / Rollback

**Risk 1 — projection drift.** Editing the baseline without regenerating
projections leaves the three trees disagreeing. Mitigated by running the
generator in the same change and by the projection-parity check above.

**Risk 2 — scope creep into A-class.** `bridge-essential.md` carries both
B/C1 lines and its Incident History (A2). The edit must not touch the
S290–S339 poller lessons; deleting them would remove agent-visible knowledge
not recoverable from another loaded surface. The PAUTH forbids A-class edits,
making this mechanically bounded.

**Risk 3 — adopter-facing divergence, accepted.**
`groundtruth-kb/templates/rules/**` and the scaffold golden fixtures retain the
legacy wording after this slice, so newly scaffolded adopter projects still
receive it. Purging templates requires regenerating the golden fixtures in
lockstep — a different risk profile and a separate reviewer question. Recorded
as a named follow-on, not silently dropped.

**Risk 4 — template self-reference.** The proposal scaffold at
`scripts/gtkb_propose_scaffold.py` emits Category-B wording into every draft it
generates ("Dispatcher/TAFE state plus the numbered file chain are the live
workflow state"). It is outside this slice's `target_paths` and is recorded as a
follow-on target so the generator stops reintroducing purged language.

**Rollback.** Single-commit revert. The change is text-only across rule
narrative plus one added test; no runtime behavior, schema, or state format
changes, so revert restores the prior tree exactly.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-d3-baseline-rules-b-c1-purge`; no prior version is deleted
or rewritten (append-only). Bridge state plus the numbered file chain are the
live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs:` — the diff is governance and rule narrative text plus one acceptance
census guard test. No new capability surface, no runtime behavior change, and
no repair of broken behavior, so `feat:` and `fix:` are both wrong per the
Conventional Commits type discipline in `file-bridge-protocol.md`. The added
test is a guard for the documentation change rather than the change itself, so
`test:` would understate the diff.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
