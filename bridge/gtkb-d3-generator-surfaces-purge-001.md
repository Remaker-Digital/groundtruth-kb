NEW
::init gtkb lo
::open build

# gtkb-d3-generator-surfaces-purge — Stop the proposal generators from re-emitting purged TAFE wording

bridge_kind: prime_proposal
Document: gtkb-d3-generator-surfaces-purge
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-08-14 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: c9a56647-1070-42be-b4f0-ae55fcc8c8c5
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via `::init gtkb pb`

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-6002-D3-GENERATOR-SURFACES-PURGE
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6002

target_paths: ["scripts/gtkb_propose_scaffold.py", "scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_generator_surfaces_no_legacy_wording.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The D3 purge is self-undoing while the proposal generators keep emitting the
wording being purged. `scripts/gtkb_propose_scaffold.py` writes this into the
`## Bridge Filing` section of **every draft it generates**, verified at line 233:

```text
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.
```

Because that text sits inside the emitted template rather than in a comment,
each newly authored proposal inherits Category-B phrasing and enlarges the purge
surface. The defect was found empirically: the scaffold produced exactly this
line into the draft for `gtkb-d3-baseline-rules-b-c1-purge`, a proposal whose
subject is removing that phrasing.

Three further sites carry the same class of wording:

| Site | Nature |
| --- | --- |
| `scripts/gtkb_propose_scaffold.py:233` | **Emitted into every generated draft** — the operative defect |
| `scripts/gtkb_propose_scaffold.py:13` | Module docstring, "dispatcher publication" |
| `scripts/gtkb_propose_scaffold.py:265` | Printed self-review checklist text |
| `scripts/gtkb_bridge_writer.py:3` | Module docstring, "The current bridge model uses dispatcher/TAFE state…" |

The replacement follows the term already settled by `DELIB-20260807011969` B1:
`dispatcher/TAFE state` becomes `bridge state`. No new term is introduced.

This slice changes emitted and documentary text only. It does not touch bridge
routing, status semantics, credential scanning, claim handling, or publication
behavior.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` — obsolete-reference purge is a
  standing completion obligation; a generator that re-emits the obsolete
  reference prevents that obligation from ever being discharged.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` — requires retirement-class changes
  to carry a linked, classified purge; this slice classifies all four sites.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the emitted text makes a claim about bridge
  state authority, which this spec governs.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the emitted claim names a retired
  substrate as the live workflow state, which is the stale-claim defect this
  spec addresses, propagated into every new artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this
  proposal to cite every governing specification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the
  project/authorization/work-item triple in the metadata block.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the spec-derived
  verification plan below before `VERIFIED`.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — satisfied by the four specs
  linked into this slice's PAUTH at issuance.

## Prior Deliberations

- `DELIB-20260813010011` — the owner sequencing decision placing this slice
  immediately after the A-class purge, on the stated rationale that it is the
  only follow-on that actively regenerates the defect being purged.
- `DELIB-20260807011969` — D3 Category B replacement term. This slice applies
  B1 (`→ bridge state`) rather than choosing a term; the gate that settled it
  is closed and is not reopened here.
- `DELIB-20260807011937` — D3 purge scope: live agent-facing direction only.
  Generator-emitted proposal text is live agent-facing direction, since it
  becomes the content of governed bridge artifacts.
- `DELIB-20260807011968` — standing directive: the legacy TAFE dispatcher is
  obsolete and being purged, not paused.
- `DELIB-20260813010009` and `DELIB-20260813010010` — the companion baseline
  rules slices. This slice is the generator-side counterpart: those purge the
  existing corpus, this one stops the corpus from being re-polluted.

## Owner Decisions / Input

This proposal depends on owner approval and cites the owner instruction
archived at `DELIB-20260813010011` (`source_type=owner_conversation`,
`outcome=owner_decision`, ref `OWNER-20260814-c9a56647-D3-FOLLOWON-SEQUENCING`):

1. **Work ordering** — owner verbatim: *"Next do A1 and A2. Then resolve 2 -
   scripts/gtkb_propose_scaffold.py, then 1 - D3 program binding gap, then 3 -
   Templates."* Item 2 of that queue is this slice, named by file path.

The slice's PAUTH cites `DELIB-20260813010011` as its
`owner_decision_deliberation_id`.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement is needed.
`ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` establishes the purge obligation,
`DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` requires the classification, and
`DELIB-20260807011969` B1 already fixes the replacement term. This slice applies
existing requirements to a surface the earlier slices did not cover.

## Spec-Derived Verification Plan

| Linked specification | Test / command | Expected result |
| --- | --- | --- |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`, `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | `test_generators_emit_no_legacy_wording` | Zero `TAFE` / `dispatcher/TAFE` occurrences in `gtkb_propose_scaffold.py` and `gtkb_bridge_writer.py` |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_scaffold_output_is_clean` — generate a throwaway draft and scan it | Generated draft contains `bridge state`, and no `dispatcher/TAFE` / `TAFE-backed` phrasing |
| `DELIB-20260807011969` B1 (term uniformity) | same test | `bridge state` present; `canonical bridge state` absent — no competing term |
| Behavior preservation | `platform_tests/scripts/test_gtkb_propose_scaffold.py` | Passes unchanged; scaffold structure, section set, and validation behavior unaltered |
| Behavior preservation | existing bridge-writer suites | Routing, status, claim, and credential-scan behavior unchanged |

Commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_generator_surfaces_no_legacy_wording.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_propose_scaffold.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_propose_scaffold.py scripts/gtkb_bridge_writer.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_propose_scaffold.py scripts/gtkb_bridge_writer.py
```

`ruff check` and `ruff format --check` are listed separately and deliberately:
they are distinct gates, and code passing the former can still fail the latter,
which is a recurring cause of verification-time `NO-GO`.

## Risk / Rollback

**Risk 1 — scaffold-output test drift.** `test_gtkb_propose_scaffold.py` may
assert on emitted section text. If it pins the old wording, that assertion is
updated in the same change; no test is deleted, preserving the `CLAUDE.md`
Protected Behaviors invariant.

**Risk 2 — behavior change mistaken for text change.** Both files are live
bridge infrastructure. The edit is confined to a docstring, a printed checklist
string, and one line of emitted template text. No control flow, validation, or
publication path is touched, and the existing scaffold suite passing unchanged
is the evidence for that.

**Risk 3 — ordering against the sibling slices.** This slice touches only
`scripts/`, which neither the B+C1 nor the A-class slice includes in
`target_paths`, so there is no file overlap and no rebase dependency. It may
land before or after them.

**Rollback.** Single-commit revert. Text-only diff across two modules plus one
added test; no schema, interface, or state-format change.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-d3-generator-surfaces-purge`; no prior version is deleted
or rewritten (append-only). Bridge state plus the numbered file chain are the
live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — this repairs a defect with a live propagating effect: the generator
writes obsolete authority claims into every new governed artifact. It is not
`docs:`, because the primary change is to program output rather than to
documentation about the program, and it is not `refactor:`, because observable
output changes. One added regression test accompanies the fix rather than
constituting it.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
