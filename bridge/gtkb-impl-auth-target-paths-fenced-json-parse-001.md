NEW

# extract_target_paths: parse the fenced-JSON target_paths heading form and fail closed on non-path tokens (WI-4833)

bridge_kind: prime_proposal
Document: gtkb-impl-auth-target-paths-fenced-json-parse
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-25 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: a7616e92-ccec-4d84-b80a-943090efc932
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4833-TARGET-PATHS-FENCED-JSON-PARSER
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4833

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`scripts/implementation_authorization.py` `extract_target_paths(markdown)` is the
authorizer that turns a GO'd proposal's declared `target_paths` into the
`target_path_globs` written into the implementation-start packet. It silently
mis-parses the **fenced-JSON `## target_paths` form** that authors naturally
write, mis-authorizing implementation scope.

The function tries three branches in order (current code, L596-638):

1. `TARGET_PATHS_RE` (L80) — a **single-line** metadata regex
   `target_paths\s*:\s*(\[[^\n]+\])`. The `[^\n]+` forces the whole list onto
   one line; a heading has no `:`, and a fenced block spans lines. No match.
2. `## Files Expected To Change` section — a different section name. No match.
3. `## target_paths` heading body — takes the **first backtick span of each
   bullet line**. The fenced-JSON lines (`  "scripts/foo.py",`) are not bullets,
   so they are skipped; but a **"Mutation classes used" bullet list**
   (`` - `source` — … ``, `` - `hook_upgrade` — … ``) IS bullets, so the parser
   harvests `source`, `hook_upgrade`, `test_addition` as if they were file paths.

`begin` then succeeds, but the packet's `target_path_globs` are the mutation-class
tokens. `scripts/implementation_start_gate.py` authorizes nothing matching the
real files and blocks every existing-file edit after GO (new-file creation slips
through, since the gate only guards existing files). The failure is silent until
an edit is attempted — well after GO. This is exactly what WI-4829 hit; its
`-001` used the fenced form and it had to be re-filed `-003` with a single-line
`target_paths:` workaround (primary-source evidence:
`bridge/gtkb-self-review-write-time-gate-001.md` and `-003.md`).

**This proposal** (scope per owner AUQ, DELIB-20266121):

1. **Fenced-JSON-first in the heading branch.** Inside the `## target_paths`
   heading branch, parse a fenced code block (a json-tagged or bare
   triple-backtick fence) whose content is a JSON list of non-empty strings, and
   return it. Only fall back to the bullet-first-span heuristic when no fenced
   JSON list exists. This makes the explicit JSON list always win over a "Mutation classes
   used" bullet list in the same section. Existing single-line precedence
   (branch 1) and the `## Files Expected To Change` branch (branch 2) are
   unchanged — the new logic lives entirely inside branch 3, which only runs when
   branch 1 misses, so the inline-JSON precedence test (T6) still holds.

2. **Fail closed on non-path tokens.** Add a path-shape guard: if the parsed
   target list contains only bareword tokens that are not path-shaped (no `/`,
   no `.`, and no `*`) — the signature of a mutation-class-bullet misfire —
   `extract_target_paths` raises `AuthorizationError` instead of returning them,
   so `begin` fails loudly and diagnosably rather than silently authorizing
   nothing. (Conservative by construction: every real target path/glob contains
   at least one of `/`, `.`, or `*`.)

3. **Spec-derived regression tests** in
   `platform_tests/scripts/test_implementation_authorization.py`.

4. **Scaffold→authorizer round-trip lock test.** A test that feeds
   `scripts/gtkb_propose_scaffold.py` output through `extract_target_paths` and
   asserts the file list round-trips. This locks the (already-correct) scaffold
   single-line emission against future drift.

**Scope refinement (surfaced to and approved by owner, DELIB-20266121).** The
original directive's item "make the helper emit a parseable single-line
`target_paths:` line" is **already satisfied at source**:
`scripts/gtkb_propose_scaffold.py` L185 already emits `target_paths: {tp_json}`
(single-line JSON). The WI-4829 break came from a *hand-authored* fenced block,
not the scaffold. So this proposal does NOT modify the scaffold; it locks the
existing behavior with the round-trip test (item 4) instead. Surface is
`scripts/implementation_authorization.py` + the test file only.

## Specification Links

- `DCL-IMPL-AUTH-EXTRACT-TARGET-PATHS-FENCED-JSON-FORMAT-001` — the governing
  constraint created for this work; mandates fenced-JSON recognition (preferring
  it over bullet-first-spans) and the fail-closed-on-non-path-tokens behavior.
  The implementation realizes this DCL.
- `DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001` — sibling
  additive-format-recognition constraint for the same authorizer module
  (`extract_spec_links`); the design precedent this fix parallels.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/impl-auth protocol authority; the
  authorizer parses the implementation-start metadata the protocol mandates.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the tests below derive
  from the DCL clauses; verification requires executing them.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the linkage section
  this proposal itself satisfies; `target_paths` is a sibling impl-start metadata
  element the same authorizer consumes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
  — project-linkage of this proposal (PAUTH/Project/WI metadata above).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the defect, owner decision,
  and governing DCL were captured as durable artifacts (WI-4833, DELIB-20266121,
  the new DCL) rather than chat-only context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — artifact-oriented
  development stance under which the propose-phase artifacts were created.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — specify-on-contact: touching
  the previously-implicit `extract_target_paths` parsing contract triggered the
  governing DCL's creation.

## Prior Deliberations

- `DELIB-20266121` — the owner AUQ scope decision for WI-4833 ("Parser fix +
  guard + tests + lock"), and the formal-artifact approval of the new DCL. This
  proposal implements exactly that approved scope.
- Sibling precedent: `DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001` (created
  for the analogous `extract_spec_links` markdown-table fix) establishes the
  per-behavior-DCL pattern for "teach the impl-auth parser an additive author
  format"; this proposal follows it for `target_paths`.
- No other on-point prior deliberation was found via
  `gt deliberations search "extract_target_paths target_paths implementation authorization parser"`
  (top hit was DELIB-20266121 itself); the existing parser-family work items
  (WI-3499 annotated-headings, WI-3333 false-positives, WI-4809 scope-auditor)
  addressed adjacent defects, not the fenced-JSON form.

## Owner Decisions / Input

This proposal depends on owner approval, recorded via AskUserQuestion:

- `AUQ-TARGET-PATHS-FENCED-JSON-PARSER-SCOPE-2026-06-25` → owner answer **"Parser
  fix + guard + tests + lock"** — approved the scope (items 1-4 above) and the
  refinement that the scaffold is not modified (it already emits the parseable
  form). Archived as `DELIB-20266121` (`source_type=owner_conversation`,
  `outcome=owner_decision`).
- `AUQ-DCL-IMPL-AUTH-EXTRACT-TARGET-PATHS-FENCED-JSON-2026-06-25` → owner answer
  **"Approve — insert the DCL"** — formal-artifact approval
  (`GOV-ARTIFACT-APPROVAL-001`) under which
  `DCL-IMPL-AUTH-EXTRACT-TARGET-PATHS-FENCED-JSON-FORMAT-001` was already recorded
  to MemBase during the propose phase (its approval packet is on disk). This
  approval evidence is complete; the implementation phase performs NO
  approval-evidence work and touches only the two `target_paths` files above, so
  no approval-packet path is included in `target_paths`.

Origin directive: owner spawned task 2026-06-25 ("Resolve a silent format
contract mismatch between bridge-proposal authoring and the implementation-start
authorizer that mis-authorizes implementation scope").

## Requirement Sufficiency

Existing requirements are sufficient for this scope. The governing constraint
`DCL-IMPL-AUTH-EXTRACT-TARGET-PATHS-FENCED-JSON-FORMAT-001` (owner-approved and
recorded in MemBase during the propose phase) plus its authority chain
(`DCL-IMPL-AUTH-EXTRACT-SPEC-LINKS-TABLE-FORMAT-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`)
fully specify the required behavior. No new or revised requirement is required
before implementation.

## Spec-Derived Verification Plan

Tests are added to `platform_tests/scripts/test_implementation_authorization.py`
in the existing `WI-3333 Bug 1: ## target_paths heading recognition` block (the
home of the current `extract_target_paths` tests), each mapped to a DCL clause:

| DCL clause | Test |
|---|---|
| Recognize fenced-JSON `## target_paths` form | `test_extract_target_paths_accepts_fenced_json_heading` — a `## target_paths` heading whose body is a json-tagged fenced code block returns the file list. |
| Prefer fenced JSON over bullet first-spans | `test_extract_target_paths_fenced_json_wins_over_mutation_class_bullets` — a section with BOTH a fenced-JSON list AND a "Mutation classes used" bullet list returns the file list, NOT `source`/`hook_upgrade`/`test_addition`. (Direct WI-4829 regression.) |
| Fail closed on non-path tokens | `test_extract_target_paths_raises_on_bareword_only_tokens` — a `## target_paths` heading whose only bullets are bareword mutation-class tokens raises `AuthorizationError`. |
| Scaffold round-trip lock | `test_scaffold_target_paths_round_trips_through_extract` — `gtkb_propose_scaffold` emitted body → `extract_target_paths` returns the same path list. |
| No regression of existing forms | Existing T1-T6 + `## Files Expected To Change` + end-to-end packet tests (`test_create_authorization_packet_accepts_target_paths_heading_proposal`) continue to pass unchanged. |

Verification commands (repo venv interpreter for reproducible evidence):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
```

Expected: all tests pass (including the existing suite); ruff lint and format clean.

## Implementation Notes (for the implementer)

- Add a small helper, e.g. `_fenced_json_list(body: str) -> list[str] | None`,
  that scans the `## target_paths` heading body for a fenced block, attempts
  `json.loads`, and returns a normalized non-empty `list[str]` (mirroring the
  existing inline-JSON validation at L604-606: list of non-empty strings,
  `.strip().replace("\\", "/")`) or `None`.
- In the branch-3 block (L626-636), call the helper first; if it returns a list,
  return it. Otherwise run the existing bullet-first-span loop.
- Add the path-shape guard as a single predicate (e.g.
  `_is_path_shaped(token)` = contains any of `/`, `.`, `*`) applied to the
  bullet-branch result: if non-empty and none are path-shaped, raise
  `AuthorizationError` with a message naming the likely cause (mutation-class
  bullets mistaken for paths). Keep the guard on the bullet branch so the
  inline-JSON and `Files Expected To Change` branches are untouched.
- Do not modify `scripts/gtkb_propose_scaffold.py`.

## Risk / Rollback

Low risk. The change is additive inside branch 3 (only reached when the
single-line form is absent) plus a fail-closed guard whose trigger condition
(all-bareword tokens) no real proposal hits. Existing parser tests pin every
current form. Rollback is a single-commit revert of
`scripts/implementation_authorization.py` + the test additions. The fail-closed
guard could in principle reject a hypothetical legitimate bare-word target with
no `/`, `.`, or `*` (e.g. a top-level extensionless file referenced only as a
bare bullet); this is vanishingly rare, is surfaced loudly (not silently), and
the author can use the single-line `target_paths:` form or a path-shaped entry.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge
file for `gtkb-impl-auth-target-paths-fenced-json-parse`; no prior version is
deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs the silent mis-authorization defect in `extract_target_paths`.
The added fenced-JSON branch is the repair mechanism for the broken
authoring↔authorizer contract, not a new user-facing capability; the change set
is one parser function plus its regression tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
