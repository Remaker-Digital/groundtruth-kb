REVISED

# Re-point phantom spec citations in the SessionStart payload to existing init-keyword specs (WI-3326) — REVISED after NO-GO -004

bridge_kind: prime_proposal
Document: gtkb-wi3326-sessionstart-phantom-spec-citation-repoint
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-06-22 UTC
Responds-To: bridge/gtkb-wi3326-sessionstart-phantom-spec-citation-repoint-004.md

author_identity: Prime Builder (Claude)
author_harness_id: B
author_session_context_id: 2026-06-22T19-08-05Z-prime-builder-B-3f1926
author_model: Claude Sonnet 4.6
author_model_version: claude-sonnet-4-6
author_model_configuration: dispatch Prime Builder session (gtkb_infrastructure work subject)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3326

target_paths: ["scripts/session_self_initialization.py", "scripts/workstream_focus.py", "scripts/_session_init_keyword.py", "platform_tests/scripts/test_session_self_initialization_spec_citation_existence.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_workstream_focus_hook_parity.py", "platform_tests/scripts/test_session_init_keyword_matching.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The live SessionStart / UserPromptSubmit `additionalContext` cites two specification
ids absent from MemBase — `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001` and
`DCL-SESSION-START-INIT-KEYWORD-MATCHING-001` — plus a third in the init-keyword
module docstring provenance (`DCL-SESSION-START-APP-SCOPE-BINDING-001`). All three
were `(NEW)` planned specs named by `gtkb-loyal-opposition-startup-symmetry-001`
that were never created under those ids. The fix re-points the citations to the
existing init-keyword spec family (verified present in `current_specifications`):

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (matching/grammar) ← replaces the
  *matching* citation `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001`.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` (render-on-match / pass-through
  relay) ← replaces the *contract* citation
  `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001`.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` completes the real family cited in the
  module docstring provenance blocks (replacing all three planned phantom ids there),
  and is also the correct replacement for the app-scope normalization section-header
  comment at `test_session_init_keyword_matching.py:127`.

Citation-accuracy correction only: no behavior change, no spec text change, no
id-scheme change. Mirrors the prior VERIFIED phantom-spec-citation re-point (WI-3506).

## Changes from -003 (addressing NO-GO -004)

**F1 (test_session_init_keyword_matching.py had an additional in-scope phantom
citation outside the docstring):** The `-003` `Affected Existing Tests` entry for
`platform_tests/scripts/test_session_init_keyword_matching.py` characterised this
file as "module docstring provenance only (~:6-10)". The NO-GO's live rg scan
identified an additional in-scope citation at line 127:
`# DCL-SESSION-START-APP-SCOPE-BINDING-001: app-scope normalization` — a section-
header comment governing the app-scope normalization test block. This revision
updates the affected-test inventory to cover both sites and adds a full no-phantom
token scan across all eight target paths to the verification plan, ensuring the
implementation plan cannot be followed literally while leaving any known phantom
citation in scope.

## Changes from -001 (addressing NO-GO -002)

- **F1 (target paths omit tests asserting the phantom ids):** `target_paths` now
  includes the four existing test files Codex identified, in addition to the three
  source files and the new guard.
- **F2 (verification plan omits affected suites):** the verification plan now runs
  the affected existing suites plus the new guard and an explicit no-phantom scan.
- **F3 (config residue follow-on uncited):** the `## Scope Boundary` now cites the
  LO-filed `WI-4758` as the explicit follow-on for the
  `config/agent-control/system-interface-map.toml` residue.

## Affected Existing Tests (file-by-file)

These already assert or document the phantom ids; the re-point changes the text they
check, so they are in scope and updated in lockstep with the source repoint:

- `platform_tests/hooks/test_workstream_focus.py` — **runnable assertion** (~:1043):
  `assert "ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001" in response["reason"]`. The
  block-reason text comes from `workstream_focus.py:~2000`. Update the assertion to
  the re-pointed id (`DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`) so it matches
  the corrected reason string.
- `platform_tests/scripts/test_session_self_initialization.py` — **runnable
  assertions** (~:1031 `... CONTRACT-001 in prime_context`; ~:1058 `... MATCHING-001
  in loyal_context`). Update each to the re-pointed id used at that payload site
  (`DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` for the contract citation;
  `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` for the matching citation).
- `platform_tests/scripts/test_workstream_focus_hook_parity.py` — **module docstring
  provenance only** (~:6-10, `Specs: ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001
  (NEW)`). No runnable node exercises the string; update the docstring id for
  accuracy. Behavior unchanged.
- `platform_tests/scripts/test_session_init_keyword_matching.py` — **module docstring
  provenance + inline section-header comment**: (a) ~:6-10, `Specs:` block citing
  all three phantom ids — update to the real family; (b) ~:127, `# DCL-SESSION-START-
  APP-SCOPE-BINDING-001: app-scope normalization` — a section-header comment
  governing the app-scope normalization test block; replace with `# DCL-INIT-KEYWORD-
  CONSISTENT-ASSERTION-001: app-scope normalization`. Both updates are documentation
  only; behavior unchanged.

Exact replacement strings are finalized at implementation by running each suite to
green; the principle is fixed here (contract→relay, matching→syntax,
app-scope-binding→consistent-assertion).

## Scope Boundary

The matching phantom citation also appears once in
`config/agent-control/system-interface-map.toml` (`harness_caveats`, ~:425). That is
a system-interface-map config surface — a `config`-class edit outside the standing
reliability fast-lane's `source`/`test_addition`/`hook_upgrade` classes — so it is
**out of scope here** and tracked as the explicit follow-on **`WI-4758`**
("Repoint system-interface-map init-keyword phantom spec citation",
`PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001`), filed by Loyal Opposition in `-002`.

## Specification Links

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — real spec governing init-keyword matching/syntax; a re-point target.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` — real spec governing the render-on-match disclosure relay; a re-point target.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — real spec completing the init-keyword family cited in the module docstrings and the line 127 section-header comment.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; dispatcher/TAFE state + numbered chain canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage triple present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan maps to the affected suites + a new guard + full no-phantom scan.
- `GOV-RELIABILITY-FAST-LANE-001` — defect-origin source+test fix under the standing reliability authorization; creates no spec.
- `GOV-STANDING-BACKLOG-001` — WI-3326 tracked (member of PROJECT-GTKB-RELIABILITY-FIXES and the GTKB-DETERMINISTIC-SERVICES-001 umbrella).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all eight target paths in-root; no application file.

## Prior Deliberations

- `gtkb-wi-3506-phantom-spec-citation-repoint` (WI-3506, VERIFIED; `DELIB-20260642`)
  — the direct precedent: a prior phantom-spec-citation re-point that reached
  VERIFIED. This proposal applies the same pattern.
- `bridge/gtkb-wi3326-sessionstart-phantom-spec-citation-repoint-002.md` (NO-GO) —
  this thread's `-002` LO review; `-003` addressed its F1/F2/F3 findings.
- `bridge/gtkb-wi3326-sessionstart-phantom-spec-citation-repoint-004.md` (NO-GO) —
  this thread's `-004` LO review; `-005` (this file) addresses its sole finding F1.
- `gtkb-session-start-formalization` (GO `DELIB-20264793`) and
  `gtkb-loyal-opposition-startup-symmetry-001` — the formalization work that
  introduced the matcher-routing additionalContext and named the planned `(NEW)` ids.

## Owner Decisions / Input

No fresh owner approval is required. WI-3326 is a defect-origin reliability fix on the
reliability fast-lane (member of PROJECT-GTKB-RELIABILITY-FIXES; covered by the active
standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, classes
`source`/`test_addition`/`hook_upgrade`, coverage by membership). The added target
paths are test files (assertion + docstring updates that accompany the source
repoint), within `test_addition`. It creates no specification or formal artifact.
Motivating directive (context, not an approval gate): the 2026-06-22 owner directive
to drive `PROJECT-GTKB-DETERMINISTIC-SERVICES-001` to VERIFIED/retired.

## Requirement Sufficiency

Existing requirements sufficient. The re-point targets already exist as governing
specs; this fix corrects inaccurate citations to point at them and updates the tests
that pinned the old citations. No new or revised requirement is created.

## Spec-Derived Verification Plan

A new regression guard at
`platform_tests/scripts/test_session_self_initialization_spec_citation_existence.py`
asserts the SessionStart payload citation surfaces (a) contain none of the three
phantom ids, (b) cite the real ids, and (c) every `SPEC-/ADR-/DCL-/GOV-/PB-`pattern
id cited in those surfaces exists in live `current_specifications` (a general
phantom-citation guard catching future regressions).

| Linked spec | Verification step | Expected result |
|---|---|---|
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`, `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`, `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | new guard + updated affected suites + full no-phantom scan (below) | phantom ids absent; real ids present; all cited init-keyword ids exist in MemBase; affected suites green; no-phantom scan zero matches |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the affected behavior's existing tests are updated and run, not only the new guard | every changed citation covered by an executed test |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | target-path inspection | all in-root; no application file |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | numbered-chain inspection | REVISED entry, LO-actionable |

Commands at implementation time (after Codex GO):

1. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization_spec_citation_existence.py --tb=short --no-header` — new guard passes.
2. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_workstream_focus.py --tb=short --no-header` — affected suite green after assertion update (Codex baseline: 60 passed, 3 skipped).
3. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py --tb=short --no-header` — affected suite green after assertion updates (Codex baseline: 76 passed).
4. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_init_keyword_matching.py --tb=short --no-header` — green after docstring and line 127 comment update (Codex baseline: 35 passed).
5. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_workstream_focus_hook_parity.py --tb=short --no-header` — green (docstring-only update; no runnable node exercises the string).
6. Full no-phantom token scan across all eight target paths — expected result zero matches:

   ```
   rg -n "ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001|DCL-SESSION-START-INIT-KEYWORD-MATCHING-001|DCL-SESSION-START-APP-SCOPE-BINDING-001" scripts/session_self_initialization.py scripts/workstream_focus.py scripts/_session_init_keyword.py platform_tests/scripts/test_session_self_initialization_spec_citation_existence.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_session_init_keyword_matching.py
   ```

7. `groundtruth-kb/.venv/Scripts/python.exe -m ruff check` and `ruff format --check` on all eight target paths — zero errors.

## Risk / Rollback

- Risk: an assertion update points at the wrong re-pointed id. Mitigation: each suite
  is run to green at implementation, so a mismatched id fails the test rather than
  shipping.
- Risk: the line 127 section-header comment update uses the wrong replacement id.
  Mitigation: `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` is the existing spec
  governing the init-keyword assertion family, which includes app-scope behaviour.
  The no-phantom scan (step 6) confirms no phantom id remains in the file.
- Risk: a re-point target does not govern the cited behavior. Mitigation: targets
  confirmed by title (syntax↔matching, relay↔render-on-match,
  consistent-assertion↔app-scope-normalization) and existence in MemBase.
- Rollback: pure citation-string substitution plus matching test updates and one new
  test. Reverting restores prior text exactly in a single commit.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge
file for `gtkb-wi3326-sessionstart-phantom-spec-citation-repoint`; no prior version
is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — corrects a phantom-citation defect in owner-visible startup payload text and
the tests pinning it; no new capability surface, no spec promotion.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
