REVISED
::init gtkb lo
::open build

# gtkb-d3-baseline-rules-b-c1-purge — D3 Category B+C1 purge of legacy TAFE wording from the canonical baseline rules tree (REVISED-1)

bridge_kind: prime_proposal
Document: gtkb-d3-baseline-rules-b-c1-purge
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-08-15 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: c9a56647-1070-42be-b4f0-ae55fcc8c8c5
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via `::init gtkb pb`

Responds to: bridge/gtkb-d3-baseline-rules-b-c1-purge-002.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-6002-D3-BASELINE-RULES-CATEGORY-B-C1-PURGE
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6002

target_paths: [".harness-baseline-configuration/rules/*.md", "config/agent-control/gtkb-*.md", ".claude/rules/*.md", "platform_tests/scripts/test_d3_baseline_rules_purge_census.py", ".groundtruth/formal-artifact-approvals/**"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Response To NO-GO At `-002`

**F1 is accepted in full. The reviewer's count is correct and mine was wrong.**

The reviewer measured 57 B-class occurrences tree-wide against my declared edit
scope of 46 lines, and corroborated with 116 matching lines across 17 files
against my reported 111 across 13. This revision reproduces the reviewer's
numbers exactly and widens the edit scope accordingly.

### Root cause, confirmed by direct measurement

I measured with `git grep`. **`git grep` searches tracked files only.** In a
worktree carrying 587 untracked and 774 modified files, that is a material blind
spot. Direct A/B comparison on the identical pattern set:

| Method | Lines | Files |
| --- | ---: | ---: |
| `git grep` (used in `-001`) | 111 | 16 |
| Filesystem scan (used here, and by the reviewer) | **116** | **17** |

The single invisible file is
`.harness-baseline-configuration/rules/decision-ledger.md`, which is untracked
and carries 3 B-class lines. The arithmetic closes to the line.

A second, independent error compounded it: `-001` reported "13 files" when
`git grep` had itself found 16. That number was read off a per-file table I had
truncated to its top 12 rows. An aggregate must never be read from a truncated
display.

Both errors are captured as `WI-6327` so the remaining D3 slices, which all
carry census-based acceptance criteria, do not repeat them.

### What changed in this revision

1. Census re-measured by filesystem scan; all counts below are the corrected
   figures.
2. Edit scope widened from 46 lines to **62 lines across 15 files**.
3. Acceptance criterion restated so scope is derived from a census run **at
   implementation time**, not from a census frozen at authoring time.
4. The three advisory specs the `-001` preflight reported as missing are now
   cited.

Per the reviewer's own scoping, the design, categorization method, projection
handling, and owner-settled dispositions are unchanged and were not re-analyzed.

## Summary

The always-loaded rule surfaces still name the retired legacy TAFE dispatcher as
the canonical bridge state authority. Because these files auto-load into every
session, they steer workers toward a substrate that is disabled and being purged.
This slice executes the D3 Category B and C1 purge on the canonical baseline
rules tree, limited to the two categories whose disposition prior owner decisions
already settled.

**Corrected census (filesystem scan, `.harness-baseline-configuration/rules/**`,
38 files scanned, pattern set `TAFE|dispatcher[ _-]daemon|smart poller|OS
poller`): 116 matching lines across 17 files.**

| Category | Lines | Disposition | Settled by |
| --- | ---: | --- | --- |
| B — names the canonical bridge state store | 49 | rename to `bridge state` | `DELIB-20260807011969` B1 |
| C1 — dated cutover references | 13 | rewrite present-tense, drop the event | `DELIB-20260807011969` B2 |
| A1 — live-dispatcher claims | 48 | **deferred** to the A-class slice | — |
| A2 — retired/historical narrative | 6 | **deferred** to the A-class slice | — |

**Edit scope: 62 lines (49 B + 13 C1) across 15 files.**

Reconciliation with the reviewer's figure: the reviewer counted **57 B-phrase
occurrences**; this table counts **49 lines classified B**. The two are
consistent. A line carrying a dated construction is classified C1 even when it
also contains B phrasing, and a single line may carry more than one B
occurrence. All 57 occurrences fall inside the 62-line edit scope, because that
scope covers all 15 files in which any B or C1 line appears — a superset of the
14 files containing B occurrences.

### Complete edit scope, per file (untruncated)

| File | B | C1 | Total |
| --- | ---: | ---: | ---: |
| `file-bridge-protocol.md` | 11 | 2 | 13 |
| `bridge-essential.md` | 8 | 5 | 13 |
| `session-bootstrap.md` | 6 | 1 | 7 |
| `canonical-terminology.md` | 4 | 1 | 5 |
| `way-of-working.md` | 4 | 1 | 5 |
| `decision-ledger.md` | 3 | 0 | 3 |
| `prime-bridge-collaboration-protocol.md` | 3 | 0 | 3 |
| `review-operating-contract.md` | 2 | 1 | 3 |
| `standing-priorities.md` | 2 | 1 | 3 |
| `loyal-opposition-runbook.md` | 2 | 0 | 2 |
| `bridge-permanent-operations-runbook.md` | 1 | 0 | 1 |
| `counterpart-review-gate.md` | 1 | 0 | 1 |
| `dispatcher-daemon-substrate-rollback-runbook.md` | 1 | 0 | 1 |
| `operating-model.md` | 1 | 0 | 1 |
| `bridge-poller-canonical.md` | 0 | 1 | 1 |
| **Total** | **49** | **13** | **62** |

Nine of these files were absent from `-001`'s scope table. `decision-ledger.md`
was invisible to the census method entirely; the other eight fell below the
display truncation.

`.harness-baseline-configuration/rules/**` is the canonical edit target.
`config/agent-control/gtkb-*.md` and `.claude/rules/*.md` are one-way projections
regenerated from it by `scripts/generate_rule_compatibility_projections.py`,
whose module docstring states the generator "never reads a retained projection as
authority and never mutates a canonical file." They appear in `target_paths` only
as regeneration output.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` — establishes obsolete-reference
  purge as a standing completion obligation; this slice discharges the
  Category B and C1 portion for the retired TAFE dispatcher.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` — requires retirement-class changes
  to carry a linked, classified purge; the corrected classification above is
  that classification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs bridge audit-trail discipline and is
  the surface most affected: `file-bridge-protocol.md` and `bridge-essential.md`
  carry 26 of the 62 in-scope lines between them.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — state claims must derive from fresh
  canonical reads; rule text naming a retired store as canonical authority
  directs workers to a stale substitute. The `-001` census defect was itself an
  instance of this spec's concern, applied to measurement.
- `GOV-ARTIFACT-APPROVAL-001` — `.harness-baseline-configuration/rules/*.md` are
  protected narrative artifacts; each file touched requires a
  formal-artifact-approval packet before its write.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory spec reported missing by the
  `-001` preflight; the purge is artifact-lifecycle work and is governed by the
  artifact-oriented stance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory spec reported missing by the
  `-001` preflight.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory spec reported missing by the
  `-001` preflight; the retirement-class trigger is what places these lines in
  scope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this
  proposal to cite every relevant governing specification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the
  project/authorization/work-item triple in the metadata block.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the
  specification-derived verification plan below before `VERIFIED`.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — satisfied by the specs
  linked into the PAUTH at issuance.

## Prior Deliberations

- `DELIB-20260813010009` — the owner AUQ decisions of 2026-08-14 scoping this
  slice to B+C1 and routing its authorization through `WI-6002`. Unchanged by
  this revision; the scope decision was about categories, not counts.
- `DELIB-20260807011969` — D3 Category B replacement term. This revision applies
  B1 (`→ bridge state`) and B2 (dated references rewritten present-tense) to a
  wider line set; it does not reopen the term.
- `DELIB-20260807011937` — D3 purge scope: live agent-facing direction only,
  explicitly including `.claude/rules/**` and `config/agent-control/**`. The nine
  newly-included files are all inside that boundary.
- `DELIB-20260807011940` — D3 scope amendments; amendment 2 is why projections
  are regenerated rather than hand-edited.
- `DELIB-20260806011917` — owner standing directive: purge at the source rather
  than layering counter-instructions.
- `DELIB-20260807011968` — standing directive that the legacy TAFE dispatcher is
  obsolete and being purged, not paused.
- `DELIB-20260813010011` — owner sequencing decision for the D3 follow-on queue.

## Owner Decisions / Input

This proposal depends on owner approval and cites the AskUserQuestion evidence
archived at `DELIB-20260813010009` (`source_type=owner_conversation`,
`outcome=owner_decision`, AUQ id
`AUQ-2026-08-14-c9a56647-d3-baseline-rules-b-c1`):

1. **Slice scope** — owner answered *"B + C1 only — 58 pre-decided edits"*,
   deferring A-class judgment lines to a separate slice. The corrected census
   raises the count from 58 to 62; the **categories are unchanged**, so the
   owner's decision is applied as given and no fresh owner decision is required.
   The figure in the owner's option label was Prime Builder's estimate at ask
   time, not an owner-chosen quantity.
2. **Authorization route** — owner answered *"Route via WI-6002 + narrow
   PAUTH"*.
3. **Standing directive** — the owner directed that the purge proceed now, and
   confirmed `.harness-baseline-configuration/rules/` as the tree to edit.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement is needed.
`ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` and
`DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` govern the purge obligation, and
`DELIB-20260807011969` B1/B2 settle the disposition of both categories in scope.
The correction in this revision is to measurement, not to requirements.

## Specification-Derived Verification Plan

The acceptance criterion is the one `WI-6035` states: *a census showing zero
legacy-phrasing matches in the touched surfaces and no competing replacement
term introduced.* A new deterministic guard test encodes it.

**Scope is derived at implementation time, not frozen here.** Per the reviewer's
remedy, the implementation re-runs the census immediately before editing and
widens the edit list to whatever it reports. The 62-line table above is the
expected scope, not a cap. Any divergence between the implementation-time census
and that table is reported in the implementation report rather than silently
absorbed.

| Linked specification | Test / command | Expected result |
| --- | --- | --- |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`, `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | `test_no_b_class_state_store_wording` | Zero occurrences of `TAFE-backed`, `dispatcher/TAFE`, `TAFE/dispatcher`, `TAFE state`, `TAFE bridge state` across `.harness-baseline-configuration/rules/**` |
| `DELIB-20260807011969` B1 | `test_no_competing_replacement_term` | `bridge state` is the only replacement form; `canonical bridge state` absent |
| `DELIB-20260807011969` B2 | `test_no_dated_cutover_references` | Zero dated-cutover constructions in the tree |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (census integrity) | `test_census_uses_filesystem_scan` | The census helper enumerates via filesystem walk, not `git grep`; a fixture untracked file is counted |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (projection parity) | `scripts/generate_rule_compatibility_projections.py --check` | Projections regenerate clean from the edited baseline with no manual divergence |
| `GOV-ARTIFACT-APPROVAL-001` | approval-packet presence check | One packet per protected narrative file touched, each with matching content hash |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | bridge chain inspection | Thread chain append-only; no prior version rewritten |
| Regression floor | existing suites | `test_fab05_rule_file_retirement.py`, `test_no_active_smart_poller_wording.py`, `test_groundtruth_governance_adoption.py` pass |

The census-integrity row is new in this revision and exists specifically to
prevent the `-001` defect from recurring: it fails if the census helper is
implemented on a tracked-only scan.

Commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_d3_baseline_rules_purge_census.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_fab05_rule_file_retirement.py platform_tests/test_no_active_smart_poller_wording.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe scripts/generate_rule_compatibility_projections.py --check
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_d3_baseline_rules_purge_census.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_d3_baseline_rules_purge_census.py
```

**Pre-existing CI risk reassessed.** No test asserts the B-class wording as
required text. Every occurrence inside `platform_tests` and
`groundtruth-kb/tests` lives under
`groundtruth-kb/tests/fixtures/scaffold_golden/`, which are expected-output
snapshots for the adopter scaffold, out of scope here and handled by the
`gtkb-d3-adopter-templates-purge` slice. This assessment was re-run by
filesystem scan for this revision rather than carried forward from `-001`.

## Risk / Rollback

**Risk 1 — census drift between authoring and implementation.** The tree is
under active change. Mitigated by deriving the edit list from an
implementation-time census and reporting any divergence from the table above.

**Risk 2 — untracked files missed again.** Mitigated by the census-integrity
test, which fails if the helper is implemented on a tracked-only scan.

**Risk 3 — projection drift.** Editing the baseline without regenerating
projections leaves the three trees disagreeing. Mitigated by the
projection-parity check.

**Risk 4 — scope creep into A-class.** Nine newly-included files raise the
chance of touching adjacent A-class lines. Mitigated by the PAUTH forbidding
A-class edits and by the category-classified line list.

**Risk 5 — sibling-thread interaction.** `gtkb-d3-baseline-rules-a-class-purge`
was `NO-GO`'d at `-002` precisely because it depends on this thread reaching
`GO`. That slice rebases onto this one; nothing here depends on it.

**Rollback.** Single-commit revert. Text-only across rule narrative plus one
added test; no runtime behavior, schema, or state-format change.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-d3-baseline-rules-b-c1-purge`; no prior version is deleted
or rewritten (append-only). `NO-GO → REVISED` is the lawful transition per the
post-verdict transition table. Bridge state plus the numbered file chain are the
live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs:` — the diff is governance and rule narrative text plus one acceptance
census guard test. No new capability surface, no runtime behavior change, and no
repair of broken behavior, so `feat:` and `fix:` are both wrong per the
Conventional Commits type discipline in `file-bridge-protocol.md`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
