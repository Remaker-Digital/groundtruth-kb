NEW

# Re-point phantom spec citations in the SessionStart payload to existing init-keyword specs (WI-3326)

bridge_kind: prime_proposal
Document: gtkb-wi3326-sessionstart-phantom-spec-citation-repoint
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-22 UTC

author_identity: Prime Builder (Claude)
author_harness_id: B
author_session_context_id: 9bf0f22e-355b-4fcc-9d1d-d3f263158b08
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: interactive Prime Builder session (gtkb_infrastructure work subject)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3326

target_paths: ["scripts/session_self_initialization.py", "scripts/workstream_focus.py", "scripts/_session_init_keyword.py", "platform_tests/scripts/test_session_self_initialization_spec_citation_existence.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The live SessionStart / UserPromptSubmit `additionalContext` cites two specification
ids that do not exist in MemBase: `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001` and
`DCL-SESSION-START-INIT-KEYWORD-MATCHING-001`. A third planned-but-uncreated id,
`DCL-SESSION-START-APP-SCOPE-BINDING-001`, appears in the init-keyword module
docstring's `Specs:` provenance block. All three were named as `(NEW)` planned specs
by the authority thread `gtkb-loyal-opposition-startup-symmetry-001`, but the specs
that were actually created for this behavior carry different ids. The result is a
phantom-citation defect: the owner-visible startup payload points at non-existent
governance records.

The fix re-points the citations to the existing init-keyword spec family that the
platform did create (verified present in `current_specifications`):

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — "Canonical Init-Keyword Syntax for
  GroundTruth-KB Session Activation" (the matching/grammar). Replaces the
  *matching* citation `DCL-SESSION-START-INIT-KEYWORD-MATCHING-001`.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` — "Init-keyword startup disclosure
  relay must be visible and cache-isolated" (the render-on-match / pass-through
  contract). Replaces the *contract* citation
  `ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001`.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — completes the real family cited in
  the module docstring's `Specs:` provenance block (replacing all three planned
  phantom ids there).

This is a citation-accuracy correction only: no behavior changes, no spec text
changes, no id-scheme changes. It mirrors the prior VERIFIED phantom-spec-citation
re-point (WI-3506).

## Scope Boundary

The matching phantom citation also appears once in
`config/agent-control/system-interface-map.toml` (`harness_caveats`, line ~425).
That is a system-interface-map config surface, not the SessionStart *payload* this WI
names, and a `config`-class edit falls outside the reliability fast-lane's
`source`/`test_addition`/`hook_upgrade` mutation classes. It is intentionally **out
of scope** here and recorded as a separable one-line config follow-on, so this WI
stays within its named "SessionStart hook payload" scope and its standing-PAUTH
authorization. (The three `.py` files in `target_paths` are the live payload
generators and the module that documents the matcher.)

## Specification Links

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — the real spec governing init-keyword
  matching/syntax; one of the re-point targets.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` — the real spec governing the
  render-on-match disclosure relay; one of the re-point targets.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — the real spec completing the
  init-keyword family cited in the module docstring.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; dispatcher/TAFE state + numbered chain canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage triple present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan maps to a named regression test.
- `GOV-RELIABILITY-FAST-LANE-001` — defect-origin source+test fix under the standing reliability authorization; creates no spec.
- `GOV-STANDING-BACKLOG-001` — WI-3326 tracked (member of PROJECT-GTKB-RELIABILITY-FIXES and the GTKB-DETERMINISTIC-SERVICES-001 umbrella).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all four target paths in-root; no application file.

## Prior Deliberations

- `gtkb-wi-3506-phantom-spec-citation-repoint` (WI-3506, VERIFIED; `DELIB-20260642`)
  — the direct precedent: a prior phantom-spec-citation re-point that reached
  VERIFIED. This proposal applies the same re-point pattern to the SessionStart
  init-keyword citations.
- `gtkb-session-start-formalization` (GO `DELIB-20264793`; revision NO-GO
  `DELIB-20264798`) and `gtkb-loyal-opposition-startup-symmetry-001` — the
  formalization work that introduced the matcher-routing additionalContext and named
  the three planned `(NEW)` specs that were never created under those exact ids.
- `DELIB-20265377` (`gtkb-startup-harness-identity-refinement` VERIFIED) — adjacent
  startup-payload canonical-state work; confirms these payload surfaces are
  actively governed and worth a regression guard.

## Owner Decisions / Input

No fresh owner approval is required. WI-3326 is a defect-origin reliability fix on the
reliability fast-lane (now a member of PROJECT-GTKB-RELIABILITY-FIXES; covered by the
active standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, classes
`source`/`test_addition`/`hook_upgrade`, coverage by membership). It creates no
specification or formal artifact. Motivating directive (context, not an approval
gate): the 2026-06-22 owner directive to drive
`PROJECT-GTKB-DETERMINISTIC-SERVICES-001` to VERIFIED/retired, of which WI-3326 is a
non-terminal member.

## Requirement Sufficiency

Existing requirements sufficient. The re-point targets already exist as governing
specs; this fix corrects inaccurate citations to point at them. No new or revised
requirement is created.

## Spec-Derived Verification Plan

A new regression guard at
`platform_tests/scripts/test_session_self_initialization_spec_citation_existence.py`
asserts that the SessionStart payload citation surfaces (the three `.py` files in
scope) (a) contain **none** of the three phantom ids
(`ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001`,
`DCL-SESSION-START-INIT-KEYWORD-MATCHING-001`,
`DCL-SESSION-START-APP-SCOPE-BINDING-001`), and (b) cite the real ids
(`SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`, `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`),
and (c) every `SPEC-/ADR-/DCL-/GOV-/PB-`pattern id cited in those surfaces exists in
the live `current_specifications` table (a general phantom-citation guard that also
catches future regressions).

| Linked spec | Verification step | Expected result |
|---|---|---|
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`, `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`, `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | new regression guard test | phantom ids absent; real ids present; all cited init-keyword ids exist in MemBase |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this mapping + executed test | every behavior change covered |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | target-path inspection | all in-root; no application file |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | numbered-chain inspection | NEW entry, LO-actionable |

Commands at implementation time (after Codex GO):

1. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization_spec_citation_existence.py -q --no-header --basetemp .gtkb-state/pytest-wi3326` — new guard passes.
2. `groundtruth-kb/.venv/Scripts/python.exe -m ruff check` and `ruff format --check` on the four target paths — zero errors.

## Risk / Rollback

- Risk: a re-point target does not actually govern the cited behavior. Mitigation:
  each target was confirmed by title against the cited behavior (syntax↔matching,
  relay↔render-on-match contract) and by existence in `current_specifications`.
- Risk: the regression guard is brittle to wording changes. Mitigation: the guard
  keys on id tokens, not prose; it tolerates rewording.
- Rollback: the change is a pure citation-string substitution plus one new test.
  Reverting restores prior text exactly in a single commit.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge
file for `gtkb-wi3326-sessionstart-phantom-spec-citation-repoint`; no prior version
is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — corrects a phantom-citation defect in owner-visible startup payload text;
no new capability surface, no spec promotion.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
