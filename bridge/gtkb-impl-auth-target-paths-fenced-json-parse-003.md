NEW

# Implementation Report — extract_target_paths fenced-JSON parsing + fail-closed guard (WI-4833)

bridge_kind: implementation_report
Document: gtkb-impl-auth-target-paths-fenced-json-parse
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-25 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: a7616e92-ccec-4d84-b80a-943090efc932
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; explanatory output style

Responds to: bridge/gtkb-impl-auth-target-paths-fenced-json-parse-002.md (GO)
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4833-TARGET-PATHS-FENCED-JSON-PARSER
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4833

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

---

## Summary

Implemented the GO'd proposal (`-001`, GO at `-002`) per
`DCL-IMPL-AUTH-EXTRACT-TARGET-PATHS-FENCED-JSON-FORMAT-001`. The
`## target_paths` heading branch of `extract_target_paths` in
`scripts/implementation_authorization.py` now recognizes the fenced-JSON form
authors write (preferring it over the bullet-first-span heuristic) and fails
closed when the only harvested tokens are bare non-path words. The scaffold
(`scripts/gtkb_propose_scaffold.py`) was not modified — it already emits the
parseable single-line form. Surface: the authorizer plus its test file only.

## Specification Links (carried forward)

- `DCL-IMPL-AUTH-EXTRACT-TARGET-PATHS-FENCED-JSON-FORMAT-001` — realized by the
  implementation; both clauses (fenced-JSON recognition; fail-closed on
  non-path tokens) are covered by tests below.
- `DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001` — sibling design precedent.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/impl-auth protocol authority.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived tests executed
  (see mapping + commands).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — linkage carried
  forward from the proposal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the work and its evidence
  are durable artifacts (WI-4833, DELIB-20266121, the DCL, this report).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — artifact-oriented stance.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — specify-on-contact: the
  governing DCL was created when the parsing contract was touched.

## Changes Implemented

`scripts/implementation_authorization.py`:
- Added `_FENCED_BLOCK_RE` (matches a json-tagged/bare triple-backtick or tilde
  fence, DOTALL + MULTILINE) and `_fenced_json_target_paths(heading_body)`, which
  returns a normalized JSON list of paths from a fenced block under the
  `## target_paths` heading (same normalization as the inline-JSON branch), or
  `None` to fall back to bullets.
- Added `_is_path_shaped(token)` — True when a token contains any of `/`, `.`,
  or `*`.
- In the `## target_paths` heading branch of `extract_target_paths`: call
  `_fenced_json_target_paths` first and return its result when present; otherwise
  run the existing bullet-first-span loop, then raise `AuthorizationError` when
  the harvested tokens are all non-path-shaped (the mutation-class-bullet
  misfire). Branch 1 (single-line `target_paths:`) and branch 2
  (`## Files Expected To Change`) are unchanged, preserving the inline-JSON
  precedence (T6).

`platform_tests/scripts/test_implementation_authorization.py`:
- Added a `scaffold_module` fixture and four tests (W1–W4) in the existing
  `extract_target_paths` block.

## Spec-to-Test Mapping

| DCL clause | Test | Result |
|---|---|---|
| Recognize fenced-JSON `## target_paths` form | `test_extract_target_paths_accepts_fenced_json_heading` (W1) | PASS |
| Prefer fenced JSON over bullet first-spans (WI-4829 regression) | `test_extract_target_paths_fenced_json_wins_over_mutation_class_bullets` (W2) | PASS |
| Fail closed on non-path tokens | `test_extract_target_paths_raises_on_bareword_only_tokens` (W3) | PASS |
| Scaffold→authorizer round-trip lock | `test_scaffold_target_paths_round_trips_through_extract` (W4) | PASS |
| No regression of existing forms (T1–T6, Files-Expected, end-to-end packet) | existing suite | PASS (102 total) |

## Verification Evidence

Commands run (repo venv interpreter):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
```

Observed results:
- pytest: `102 passed in 12.56s` (98 pre-existing + 4 new; no regressions).
- ruff check: `All checks passed!`
- ruff format --check: `2 files already formatted` (exit 0).

End-to-end incident proof: the fixed `extract_target_paths`, run against the
actual file that originally broke
(`bridge/gtkb-self-review-write-time-gate-001.md`, the WI-4829 `-001` with a
fenced-JSON `## target_paths` list followed by a "Mutation classes used" bullet
list), returns the 7 real file paths — `scripts/bridge_review_independence.py`,
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`,
`.claude/hooks/bridge-compliance-gate.py`,
`.claude/skills/verify/helpers/write_verdict.py`,
`scripts/implementation_authorization.py`,
`scripts/cross_harness_bridge_trigger.py`,
`platform_tests/scripts/test_self_review_write_time_gate.py` — with zero
mutation-class tokens (`source`/`hook_upgrade`/`test_addition`) and every entry
path-shaped. Pre-fix this returned the three mutation-class names.

## Implementation-Start Authorization

`begin` succeeded from the live GO; the packet's `target_path_globs` resolved to
exactly `scripts/implementation_authorization.py` and
`platform_tests/scripts/test_implementation_authorization.py` (parsed from the
proposal's single-line `target_paths:` form). All edits were within that scope.

## Prior Deliberations

- `DELIB-20266121` — owner AUQ scope decision and DCL formal-artifact approval;
  the implementation matches that approved scope exactly.

## Owner Decisions / Input

The implemented work was owner-approved via AskUserQuestion:
- `AUQ-TARGET-PATHS-FENCED-JSON-PARSER-SCOPE-2026-06-25` → "Parser fix + guard +
  tests + lock" (archived as `DELIB-20266121`).
- `AUQ-DCL-IMPL-AUTH-EXTRACT-TARGET-PATHS-FENCED-JSON-2026-06-25` → "Approve —
  insert the DCL" (formal-artifact approval; DCL recorded in the propose phase).

## Recommended Commit Type

`fix` — repairs the silent mis-authorization defect in `extract_target_paths`;
the added fenced-JSON branch is the repair mechanism, not a new user-facing
capability. Net change: one parser function + four regression tests.

## Files Changed

- `scripts/implementation_authorization.py` (parser fix; ~60 added lines)
- `platform_tests/scripts/test_implementation_authorization.py` (4 tests + 1 fixture)

The changes are uncommitted in the worktree for Loyal Opposition to verify and
commit as part of the VERIFIED commit-finalization transaction.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
