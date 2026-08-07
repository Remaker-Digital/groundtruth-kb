NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-05T16-07-52Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb

bridge_kind: governance_review
Document: gtkb-bridge-resolver-wi5827-synonym-ordering-regression
Version: 001
Date: 2026-08-05 UTC
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5827
target_paths: []

# Bridge-Function Repair Request - WI-5827 synonym-ordering regression blocking WI-5152 / WI-5172 filings

## Summary

Two Prime Builder REVISED filings (WI-5152 v009, WI-5172 v019) are ready but
cannot be published because a pre-existing bridge-chain/resolver defect hard-
blocks every new filing on those threads. This entry routes the repair to
Loyal Opposition under its standing bridge-function/use authority
(`GOV-FILE-BRIDGE-AUTHORITY-001`; Loyal Opposition Operating Contract - standing
bridge repair lane). It is a non-implementation `governance_review` entry:
`target_paths` is empty and no protected edit is authorized by this filing.

## Root-Cause Finding 1 - WI-5827 N1 synonym-ordering regression (blocks WI-5172)

`scripts/bridge_lifecycle_resolver.py` (sweep `8bdde1431`, 2026-08-04; WI-5827
N1) added `_METADATA_KEY_SYNONYMS["Responds to"] = ("Reviewed", "Responds-To",
"Responds to GO", "Responds to NO-GO", "revised_document")`. `_metadata_values`
consults synonyms in declared order and returns the first hit.

Bridge file `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-015.md`
legitimately carries BOTH `Responds to GO: ...-012.md` and `Responds to
NO-GO: ...-014.md`. The resolver picks the GO link (012) as
`responds_values[0]`, but every version must respond to its immediate
predecessor (014), so it raises `WRONG_RESPONDS_TO_LINK`. This deterministically
blocks publication of `gtkb-wi5172-canonical-carrier-nonauthority-evaluator-019.md`
(the drafted current-state isolation report).

1,186 bridge files carry `Responds to GO:`, so this regression class affects a
broad population.

## Root-Cause Finding 2 - WI-5152 v002 missing Responds-to link (blocks WI-5152)

`bridge/gtkb-wi5152-modernization-hard-invariant-registry-002.md` (an LO
NO-GO verdict) has no `Responds to` line. The resolver expects each version to
respond to its immediate predecessor, so `WRONG_RESPONDS_TO_LINK` blocks
publication of `...-009.md` (the drafted three-file reaffirmation). v002 is an
LO-authored verdict file; the repair is LO bridge-authority scope.

## Evidence

- `python .claude/skills/gtkb-bridge/helpers/revise_bridge.py file ...` for both
  blocked threads fails with `WRONG_RESPONDS_TO_LINK` before any write.
- `bridge_lifecycle_resolver._parse_version` (lines 418-443): picks
  `responds_values[0]`, requires `responds_to == bridge/{id}-{version-1:03d}.md`.
- v015 header has two `Responds to` lines (verified at HEAD).

## Recommended Repair (Loyal Opposition bridge authority)

1. In `_METADATA_KEY_SYNONYMS`, order `Responds to NO-GO` BEFORE `Responds to
   GO`, OR prefer the canonical immediate-predecessor link when multiple
   synonym matches exist (a dual GO+NO-GO file's NO-GO link is the immediate
   predecessor for a REVISED/report version).
2. Repair the WI-5152 v002 missing-`Responds to` chain (LO-authored file).
3. After repair, Prime Builder can re-file the already-drafted WI-5152 v009 and
   WI-5172 v019.

This is not implementation approval. Protected edits to
`scripts/bridge_lifecycle_resolver.py` or historical bridge files require the
applicable bridge authority path (LO standing bridge authority for bridge-
function repair; a governed GO for the protected source change).

## Prior Deliberations / Related

- `WI-5827` - owner chose parser normalization (accept variant keys as
  synonyms) over per-thread by-reference recovery; reconciliation with WI-5636
  fail-closed stance is an open governance tension.
- `WI-5814` - surface unparseable chains.
- `WI-5636` - narrow Responds-to-GO tolerance.
- `WI-5833` - P0 governance incident origin of strictness (commit 9373c5231).
- `WI-5836` - three concurrent bridge threads collide on shared target paths.

## Owner Decisions / Input

This entry is routed to Loyal Opposition for bridge-function repair under its
standing authority. No new owner decision is requested here beyond the owner's
Option A direction to route the repair to LO.
## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge numbered-file chain is canonical; LO has standing authority to repair bridge function/use.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - linked governing specs are explicit.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project/work-item linkage is explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any follow-on implementation is independently verified.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - bridge repair must not impair other threads.
- `GOV-WORK-TREE-HYGIENE-001` - repair must not overwrite concurrent bridge bytes.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - governed artifact lifecycle applies.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact linkage preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - lifecycle states preserved.

## Specification-Derived Verification

This is a non-implementation governance_review entry; the verification below
is read-only evidence of the diagnosed defect, not implementation test results.

| Requirement | Read-only evidence | Result |
| --- | --- | --- |
| Chain-integrity diagnosis (WI-5172) | `python .claude/skills/gtkb-bridge/helpers/revise_bridge.py file gtkb-wi5172-canonical-carrier-nonauthority-evaluator ...` | fails with WRONG_RESPONDS_TO_LINK (v015 dual Responds-to) |
| Chain-integrity diagnosis (WI-5152) | `python .claude/skills/gtkb-bridge/helpers/revise_bridge.py file gtkb-wi5152-modernization-hard-invariant-registry ...` | fails with WRONG_RESPONDS_TO_LINK (v002 missing Responds-to) |
| Resolver synonym table | `grep -n "Responds to GO\|Responds to NO-GO" scripts/bridge_lifecycle_resolver.py` | `Responds to GO` precedes `Responds to NO-GO` in _METADATA_KEY_SYNONYMS |
| v015 dual-link confirmation | `findstr /C:"Responds to" bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-015.md` | two Responds-to lines (GO 012, NO-GO 014) |
| Broad population | `grep -rl "Responds to GO:" bridge | wc -l` | 1186 files |

No `python -m pytest` run is applicable to this non-implementation governance
review; the defect is diagnosed through the read-only commands above. Any
follow-on resolver fix is a separate governed implementation that will carry
its own spec-derived pytest coverage and independent verification.

---

When you are finished working, close your session envelope by invoking ::wrap.
