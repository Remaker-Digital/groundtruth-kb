NEW
::init gtkb lo
::open build

# gtkb-d3-generator-surfaces-purge — Implementation Report

bridge_kind: implementation_report
Document: gtkb-d3-generator-surfaces-purge
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-08-15 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: c9a56647-1070-42be-b4f0-ae55fcc8c8c5
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via `::init gtkb pb`

Responds to: bridge/gtkb-d3-generator-surfaces-purge-002.md

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

All four declared sites are edited and the generators no longer emit
retired-substrate wording into governed bridge artifacts. Verified end-to-end:
a freshly generated draft contains **zero** retired-substrate references.

Implementation-start packet created from the `-002` `GO`; claim kind
`go_implementation`; packet expires 2026-08-15T06:01:12Z.

## Specification Links

Carried forward from `-001` in full; no link was added or dropped.

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` — a generator that re-emits the
  obsolete reference prevents the purge obligation from ever being discharged;
  this slice closes that loop.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` — the four-site classification is
  carried forward and each site is individually verified below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the emitted text made a claim about bridge
  state authority, which this spec governs.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the emitted claim named a retired
  substrate as the live workflow state, propagating a stale claim into every new
  artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied by this
  section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied by the
  project/authorization/work-item triple in the metadata block.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied by
  § Specification-Derived Verification below.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — satisfied by the specs
  linked into this slice's PAUTH at issuance.

## Changes Made

All four sites edited, applying `DELIB-20260807011969` B1 (`→ bridge state`):

| Site | Before | After |
| --- | --- | --- |
| `gtkb_propose_scaffold.py:13` | `...write and dispatcher` / `publication.` | `...write and bridge-state` / `publication.` |
| `gtkb_propose_scaffold.py:233` | `Dispatcher/TAFE state plus the numbered file chain...` | `Bridge state plus the numbered file chain...` |
| `gtkb_propose_scaffold.py:265` | `...write and dispatcher publication (do NOT write...` | `...write and bridge-state publication (do NOT write...` |
| `gtkb_bridge_writer.py:3` | `The current bridge model uses dispatcher/TAFE state...` | `The current bridge model uses bridge state...` |

Line 233 is the operative site: it sits inside the emitted `## Bridge Filing`
template, so its wording was written into every draft the scaffold produced.

No control flow, validation, routing, status, claim, credential-scan, or
publication behavior was touched. The diff is docstring, printed checklist
string, and emitted template text only.

## Response To `-002` Finding F1 (P2)

**F1 is accepted in full and closed.** The `-001` acceptance criterion keyed on
the token `TAFE` and therefore guarded only sites 233 and 3; sites 13 and 265
carry `dispatcher publication` with no `TAFE` token and would have landed
unguarded.

The reviewer's supporting observation is also accepted and acted on: with
dispatch disabled and manual advancement in force, a checklist instructing
authors to use the helper for "dispatcher publication" describes a substrate
that is not running. Those two sites are live direction, not documentation, and
their replacement text says `bridge-state publication` rather than merely
dropping the qualifier.

Remedy implemented: `RETIRED_SUBSTRATE_RE` in the new test matches any
retired-substrate reference — `TAFE`, `dispatcher/TAFE`, `TAFE/dispatcher`,
`dispatcher daemon`, `dispatcher publication`, `smart poller`, `OS poller` —
case-insensitively, so all four sites are guarded.

The guard is itself guarded: `test_pattern_would_have_caught_the_untokened_sites`
asserts the pattern matches a `dispatcher publication` string that contains no
`TAFE` token. If a later change narrows the pattern back to `TAFE`-only
matching, that test fails rather than silently re-opening the gap F1 identified.

## Specification-Derived Verification

| Linked specification | Test | Result |
| --- | --- | --- |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`, `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | `test_generator_module_has_no_retired_substrate_wording` ×2 | **PASS** — 0 offenses in both modules |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_scaffold_emitted_template_is_clean` | **PASS** — emitted template clean and still names the store |
| `DELIB-20260807011969` B1 | `test_no_competing_replacement_term` ×2 | **PASS** — `canonical bridge state` absent |
| `-002` F1 closure | `test_pattern_would_have_caught_the_untokened_sites` | **PASS** |
| Behavior preservation | `platform_tests/scripts/test_gtkb_propose_scaffold.py` | **PASS** — 15 tests, unchanged |

### Commands executed and observed results

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_generator_surfaces_no_legacy_wording.py platform_tests/scripts/test_gtkb_propose_scaffold.py -q --no-header
  -> 21 passed, 1 warning in 0.26s

groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_generator_surfaces_no_legacy_wording.py
  -> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_generator_surfaces_no_legacy_wording.py
  -> 1 file left unchanged
```

### End-to-end evidence

A throwaway draft was generated through the live scaffold and scanned:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/gtkb_propose_scaffold.py scaffold \
    --slug gtkb-d3-scaffold-output-probe --work-item WI-6002 \
    --project PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY --pauth <this slice's PAUTH>

  -> retired_substrate_refs_in_generated_draft: 0
  -> emitted block reads:
     "(append-only). Bridge state plus the numbered file chain are the live
      workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`."
```

The probe draft was deleted after inspection; no artifact was left behind.
This is the criterion that matters for this slice: the defect was that generated
output carried the wording, so generated output is what was measured.

## Test-Authoring Correction Made During Implementation

`test_scaffold_emitted_template_is_clean` failed on first run. The cause was the
test's locator, not the implementation: it anchored on the `## Bridge Filing`
heading, whose first occurrence in the module is inside the required-sections
tuple rather than the emitted template, so the scan window landed on the wrong
region. A module-wide scan confirmed zero retired-substrate matches at that
point — the edits were already correct.

The locator now anchors on the emitted body text (`This proposal is filed
under`). Recorded here because the first-run failure is in the evidence trail and
a reviewer should be able to see it was a test defect rather than a masked
implementation defect.

## Files Changed

- `scripts/gtkb_propose_scaffold.py` — 3 sites (docstring, emitted template,
  printed checklist).
- `scripts/gtkb_bridge_writer.py` — 1 site (module docstring).
- `platform_tests/scripts/test_generator_surfaces_no_legacy_wording.py` — new,
  6 tests.

## Relationship To Sibling Slices

No file overlap with `gtkb-d3-baseline-rules-b-c1-purge` (rules tree) or
`gtkb-d3-baseline-rules-a-class-purge` (rules tree). This slice may be verified
in any order relative to them.

Worth noting for the verifier: the B+C1 implementation report
(`gtkb-d3-baseline-rules-b-c1-purge-005`) discloses that
`scripts/generate_rule_compatibility_projections.py` is inoperable, so the
`.claude/rules/` projections still carry legacy wording. That blocker is
independent of this slice — these two generator modules are edited directly and
are not projections.

## Recommended Commit Type

`fix:` — this repairs a defect with a live propagating effect: the generator
wrote obsolete authority claims into every new governed artifact. Not `docs:`,
because the primary change is to program output rather than documentation about
the program; not `refactor:`, because observable output changes. The added
regression test accompanies the fix rather than constituting it.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
