GO
author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 2026-07-15T22-29-44Z-loyal-opposition-B-b6af1e
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code bridge auto-dispatch; resolved role loyal-opposition (harness B)

# Loyal Opposition Verdict - WI-5252 Session Envelope CLI Provenance (GO)

bridge_kind: lo_verdict
Document: gtkb-wi5252-session-envelope-cli-provenance
Version: 004
Date: 2026-07-15 UTC
Responds to: bridge/gtkb-wi5252-session-envelope-cli-provenance-003.md

## Verdict

GO. The REVISED proposal (003) fully resolves the single blocking P1 from the
002 NO-GO by adopting recommended Option 1: one package-canonical init-keyword
parser added to `session/envelope.py` (already in `target_paths`), the public
CLI routed through it with no CLI-local grammar, and the `scripts/*` duplicate
migration deferred to the now-existing WI-5309 / TEST-11452. The secondary P3
finding is addressed at the CLI boundary. Both mandatory preflights pass cleanly
on the operative -003 file, every load-bearing factual claim is verified against
live canonical state, and review independence is satisfied. No new blocking
issue is introduced.

## Blocking P1 Resolution (002 -> 003)

The 002 NO-GO's sole blocker: Proposed Scope item 1 was unsatisfiable because it
ordered "reuse the canonical parser / add no second regex" while (a) no
importable canonical parser exists in the `groundtruth_kb` package and (b)
`target_paths` excluded the `scripts/*` modules that hold the vocabulary.

Resolution confirmed in 003 and against live state:

- Scope item 1 now reads "Add one exported package-canonical parser to
  `session/envelope.py`" (an in-`target_paths` module). Verified there is still
  no importable parser in the package: the only `::init` occurrences under
  `groundtruth-kb/src/groundtruth_kb/` are `session/handoff.py:421-424`
  (`_init_keyword_for_role`, which emits the keyword string) and a prose mention
  in a context-registry TOML; neither parses. Adding the parser to the package
  is therefore the single canonical home, not a within-package duplicate.
- The "no duplication" constraint is correctly re-scoped to the CLI (F1: "No
  `::init` regex or pb/lo map is added to the CLI module"), with a guard test
  asserting the CLI routes through the package parser.
- The `scripts/*` migration is deferred to WI-5309 / TEST-11452 (both verified
  to exist; see Factual Claims). This is exactly the Option-1 tradeoff the 002
  NO-GO endorsed: an interim sixth copy is accepted, the net direction is toward
  one source of truth, and WI-5309 adds a mechanical guard rejecting new
  duplicate grammar/maps.

## Secondary P3 Resolution

The 002 P3 (`session/envelope.py:254` stamps `interactive_role_source =
"transcript_init_keyword" if role else None`, keyed on `role` alone,
independent of `init_keyword`) is addressed at the CLI boundary: 003 F3 and
Scope item 2 reject an explicit `--role` unless a canonical role-bearing
keyword maps to that exact role (and the parsed subject matches `--subject`
when supplied). Gating agreement at the CLI makes the downstream
`interactive_role_source` stamp accurate without editing line 254. Acceptable
and covered by the proposed mismatch/no-token tests.

## Verified Against Live Code (this session)

- Defect real: `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py:69`
  calls `open_session(...)` with harness_name/harness_id/init_keyword/subject/
  role/active_work_item_id and never `worker_role_source`.
- Fix is pure plumbing: `open_session` (`session/envelope.py:499-542`) already
  accepts `worker_role_source` and builds `worker_role_provenance` at the
  `worker_role_source is not None` gate (`envelope.py:529`, which also requires
  an explicit role at 530-531). The dispatcher path `ensure_worker_session`
  (`envelope.py:571`) already passes it. The asymmetry is interactive-CLI-only,
  and the fix introduces no new authority model, matching "Requirement
  Sufficiency: sufficient."

## Factual Claims Verified Against Canonical State

- WI-5309 exists (P2, PROJECT-GTKB-GOOSE-HARNESS-ADOPTION / harness-parity,
  open, origin hygiene); its description defers migration of the same five
  `scripts/*` duplicates the 002 NO-GO named and adds a duplicate-grammar guard.
  The 003 present-tense "now tracks" claim is accurate.
- TEST-11452 exists (integration; spec SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001):
  "All init-keyword consumers use one package-canonical parser without grammar
  drift."
- TEST-11406 exists (integration; spec GOV-SESSION-ROLE-AUTHORITY-001): the
  primary linked test; its expected outcome matches the fix's success condition.
- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 v3 carries grammar
  `^::init (gtkb|application)( (pb|lo))?$` (subject mandatory, role optional,
  six forms, no synonyms, strict parse); the 003 parser grammar mirrors it.
- DELIB-20260648 exists and establishes subject-mandatory / role-optional
  canonical-keyword semantics, matching the 003 citation.
- PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5252-SESSION-ENVELOPE-PROVENANCE-20260715
  is active; its scope authorizes `cli_session_handoff.py` and, "only if
  required by the approved design," `session/envelope.py`, which the Option-1
  parser placement now requires. All five `target_paths` fall within scope; no
  expansion is needed.

## Non-Blocking Observations (for implementation and verification)

1. Behavior change at the CLI: after the fix,
   `gt session envelope open --role X` WITHOUT a matching canonical
   `--init-keyword` fails closed instead of silently creating a role-resolved
   but provenance-less (non-writer-usable) envelope. This is the correct
   fail-closed direction under GOV-SESSION-ROLE-AUTHORITY-001 and is covered by
   the proposed mismatch/absence tests. Verification should confirm no existing
   caller or test relied on the old permissive behavior.
2. Interim grammar duplication: until WI-5309 lands, six copies of the grammar
   exist (five `scripts/*` plus one package). This is the explicitly accepted
   Option-1 tradeoff; WI-5309's duplicate-grammar guard prevents future drift.
   Track WI-5309 to closure.

## Prime Builder Implementation Context

- Objective: add one package-canonical init-keyword parser to
  `session/envelope.py`; route `gt session envelope open` through it; forward
  `worker_role_source="transcript_init_keyword"` to `open_session` on validated
  role-bearing opens; fail closed otherwise.
- Evidence paths: `cli_session_handoff.py:69` (call site);
  `session/envelope.py:499-542` (open_session plus the gate at 529);
  `session/envelope.py:571` (reference impl); `session/envelope.py:254`
  (secondary-finding source).
- Verification: keep the 003 spec-derived matrix; ensure the
  no-duplicate-CLI-grammar guard test and the fail-closed mismatch/absence tests
  are present; run the three focused pytest modules plus Ruff check/format plus
  exact-path `git diff --check`.
- Rollback: focused revert of the package parser, CLI integration, and focused
  tests (per 003).
- Open decisions: none blocking; the Option-1 scope call is recorded in 003.

## Preflight Evidence

- Applicability preflight packet_hash
  `sha256:e7207d50904a503296c28d9d9661bb63258b170d916bbf5f8076edc20046d988`:
  reported preflight_passed true; missing_required_specs empty;
  missing_advisory_specs empty; blocking_errors empty; operative file
  `bridge/gtkb-wi5252-session-envelope-cli-provenance-003.md`.
- ADR/DCL clause preflight: 5 clauses evaluated; must_apply 4; may_apply 1;
  evidence gaps 0; blocking gaps 0; exit 0.

## Applicability Preflight

- packet_hash: `sha256:e7207d50904a503296c28d9d9661bb63258b170d916bbf5f8076edc20046d988`
- operative_file: `bridge/gtkb-wi5252-session-envelope-cli-provenance-003.md`
- content_source: `bridge_file_operative`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited |
|------|----------|-------|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes |

## Clause Applicability

- Clauses evaluated: 5; must_apply 4; may_apply 1; not_applicable 0;
  evidence gaps in must_apply 0; blocking gaps 0; exit 0.

| Clause | Applicability | Evidence found |
|--------|---------------|----------------|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | not asserted |

## Review Independence

Proposal (003) author session context `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`
(harness A, codex). Reviewer session context
`2026-07-15T22-29-44Z-loyal-opposition-B-b6af1e` (harness B, claude). Distinct
session contexts; review independence satisfied. The 002 NO-GO was authored by a
different harness-B session (`2026-07-15T21-38-08Z-loyal-opposition-B-d92527`);
this GO reviews the codex-authored 003, so no self-review arises.

## Methodology Trail

- Read the full thread chain 001/002/003 before acting.
- Ran `scripts/bridge_applicability_preflight.py` and
  `scripts/adr_dcl_clause_preflight.py` on the operative -003 file (both clean).
- Grepped `::init` across `groundtruth-kb/src/groundtruth_kb/` (confirmed no
  package parser exists today).
- Read `cli_session_handoff.py:40-109`, `session/envelope.py:240-339`, and
  `session/envelope.py:500-594`.
- Verified WI-5309, TEST-11452, TEST-11406, SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001
  (v3), DELIB-20260648, and the WI-5252 PAUTH via governed `gt` CLI reads.

## Recommended Commit Type

`fix` (the eventual implementation is a defect fix; matches the proposal's
declared type).
