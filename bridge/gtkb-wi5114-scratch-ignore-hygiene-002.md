NO-GO

# Loyal Opposition NO-GO verdict - WI-5114 scratch-ignore normalization (.gitignore EOL durability)

bridge_kind: lo_verdict
Document: gtkb-wi5114-scratch-ignore-hygiene
Version: 002
Date: 2026-07-10 UTC
Responds to: bridge/gtkb-wi5114-scratch-ignore-hygiene-001.md
Verdict: NO-GO

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T07-22-29Z-loyal-opposition-B-fa14b0
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; resolved role loyal-opposition via ::init gtkb lo

## Verdict

NO-GO. The premise is verified true and the fix direction is correct, but the
proposal as scoped produces a one-shot LF flip that git will NOT keep, so the
"normalization contract" it names is not actually durable. Two changes close the
gap; both are small and align with the repository's own established EOL
discipline.

## First-Line Role Eligibility Check

- Durable identity: `harness-state/harness-identities.json` maps `claude` to
  harness ID `B`; dispatch run id `2026-07-10T07-22-29Z-loyal-opposition-B-fa14b0`
  carries role `loyal-opposition`, harness `B`.
- Latest selected entry before review: `NEW` at
  `bridge/gtkb-wi5114-scratch-ignore-hygiene-001.md` (only version present;
  no verdict version on disk or in git history).
- Status authored here: `NO-GO` (a Loyal Opposition verdict).
- Eligibility result: Loyal Opposition is authorized to write this verdict.

## Independence Check

- Proposal author: Prime Builder, Codex harness A, session
  `019f4ace-e667-7030-b632-1cf002c1a0f7`.
- Reviewer: Loyal Opposition, Claude harness B, session
  `2026-07-10T07-22-29Z-loyal-opposition-B-fa14b0`.
- Result: unrelated harness and session contexts; no same-session self-review.

## Applicability Preflight

- packet_hash: `sha256:bc7cdce4372c660bfffc1b524992384d405024414509abbe49e220374e1f9323`
- bridge_document_name: `gtkb-wi5114-scratch-ignore-hygiene`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5114-scratch-ignore-hygiene-001.md`
- operative_file: `bridge/gtkb-wi5114-scratch-ignore-hygiene-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

Spec linkage is mechanically complete (all blocking specs cited:
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
`GOV-FILE-BRIDGE-AUTHORITY-001`). This NO-GO is on durability grounds, not on
missing spec linkage or missing authority. `GOV-WORK-TREE-HYGIENE-001` exists
(status specified) and confirms the non-destructive framing is sound.

## What the proposal gets right (do not re-litigate on revision)

1. The defect premise is real and independently confirmed. `git diff-tree
   --check fac6e892^ fac6e892 -- .gitignore` reports CR-at-EOL whitespace on the
   added hunks, and `core.whitespace` is unset (so CR-at-EOL is treated as an
   error), so the added lines carry whitespace git flags.
2. The fix DIRECTION (toward LF) matches the repository's dominant convention:
   `git ls-files --eol` over the whole tree is ~88% LF (14310 `i/lf` vs 1505
   `i/crlf`), and there is an active LF-normalization program (WI-5117, WI-5127).
3. Isolating the normalization in its own scoped `fix` commit with a focused
   test is the CORRECT way to perform an EOL change (contrast the WI-5128 class,
   where an EOL flip buried in an unrelated small-change commit was the blocker).
4. Non-destructive: no ignored/untracked/runtime-state files are deleted;
   consistent with `GOV-WORK-TREE-HYGIENE-001`.

The proposal is close. The findings below are what stand between it and a GO.

## Findings

### [P2 - blocking] F1: The LF normalization is not durable - no `.gitattributes eol=lf` pin, and `target_paths` excludes `.gitattributes`

- Observation. `.gitattributes` pins `text eol=lf` for `*.json`, `*.toml`, and
  specific skill/hook/config/template directories, but has NO rule matching
  `.gitignore` and no `*` catch-all. `git ls-files --eol .gitignore` reports
  `i/crlf w/crlf attr/` (empty attr - no EOL pin). `git config core.autocrlf`
  is unset, i.e. default `false`, so git does NOT renormalize line endings on
  `git add`. The proposal's `target_paths` are `.gitignore` and the new test
  only; `.gitattributes` is neither mentioned nor in scope.

- Deficiency rationale. With no attribute pin AND autocrlf=false, a rewrite of
  `.gitignore` to LF is committed verbatim, but the next edit made by a
  CRLF-writing tool on this workstation is ALSO committed verbatim - re-CRLFing
  the file silently. That is not hypothetical: commit `fac6e892` itself is the
  demonstrated failure mode - `git diff --numstat` shows 62/30 raw vs 32/0 with
  `--ignore-cr-at-eol`, i.e. it added 32 lines AND flipped 30 previously-LF
  lines to CRLF. A one-shot LF flip with no pin leaves `.gitignore` exposed to
  the exact regression this WI is cleaning up. The repository's own durable-EOL
  mechanism for churn-prone paths is a `.gitattributes` pin (that is precisely
  why json/toml/skills/hooks/config/templates are pinned). A `text eol=lf` pin
  would additionally cause git to renormalize any future CRLF back to LF at
  `git add`, making the fix self-healing rather than one-time. The proposal's
  own title ("Normalize the Scratch Ignore Contract") and its "focused contract
  test" framing promise a durable contract; as scoped, the EOL half of that
  contract is not enforced.

- Proposed solution. Add `.gitattributes` to `target_paths` and add an entry
  pinning `.gitignore` to LF, e.g. `/.gitignore text eol=lf` (matching the
  existing `/.gitattributes text eol=lf` and `*.toml text eol=lf` style already
  in that file). Land the pin in the same scoped commit as the LF rewrite so
  the index blob and the attribute agree from the first commit. `.gitignore`
  parses identically under LF, so there is no functional risk.

- Option rationale. Alternatives considered and rejected: (a) rely on
  autocrlf - rejected: it is off, and turning it on repo-wide is a far larger,
  out-of-scope change with broad side effects; (b) leave `.gitignore` uniformly
  CRLF (fac6e892's current state) and drop the WI - rejected: the repo flags
  CR-at-EOL as a whitespace error and prefers LF, so the cleanup is worth doing;
  (c) normalize to LF without a pin (the proposal as written) - rejected: not
  durable, as shown above. The pin is the minimal change that makes the
  normalization stick and is consistent with the file's existing pattern.

### [P2 - blocking] F2: The "contract test" does not cover the behavior the WI exists to fix (EOL), only ignore-matching

- Observation. The proposed
  `platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py` asserts
  that the WI-5114 scratch roots/patterns are ignored. The proposal's own
  verification plan covers the EOL cleanliness only with a one-time
  `git diff --check` / `git diff-tree --check HEAD^ HEAD -- .gitignore` run at
  commit time - there is no standing assertion that `.gitignore` is (and stays)
  LF.

- Deficiency rationale. The core behavior this WI introduces is the EOL
  normalization; a point-in-time `git diff --check` verifies the normalizing
  commit but leaves NO regression guard. Under
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (which this proposal links),
  each linked behavior needs executed, spec-derived test coverage; the EOL
  behavior currently has a one-shot manual check, not a durable test. A future
  re-CRLF (see F1) would pass the ignore-matching test unchanged and go
  undetected.

- Proposed solution. Add a standing assertion to the focused test that the
  committed/working `.gitignore` contains no CR bytes (equivalently, that
  `git ls-files --eol .gitignore` reports `i/lf`). This detects regression even
  if, in some environment, the F1 pin is not honored, and it makes the EOL the
  linked-DCL test actually covers.

- Option rationale. A test that only checks ignore-matching would let the EOL
  regress silently; asserting no-CR is the smallest addition that makes the
  "contract test" cover the contract's EOL half. Prevention (F1 pin) and
  detection (F2 assertion) are complementary and are the repo's established
  paired pattern (pins + EOL-aware tests); at minimum one is required, and both
  together are the low-regret result.

### [P3 - advisory] F3: "the repository's LF form" slightly overstates `.gitignore`'s history

- Observation / rationale. The Summary calls LF "the repository's LF form" for
  `.gitignore`. That is true by dominant convention (~88% LF) but `.gitignore`
  itself had no LF pin and was historically mixed/predominantly CRLF (its parent
  blob at `fac6e892^` had 628 CR bytes across a 658-line file). The claim
  becomes accurate precisely once F1 adds the pin.
- Proposed solution. Non-blocking: adjust the Summary wording to "the
  repository's dominant LF convention, pinned here for `.gitignore`" once F1 is
  incorporated. No revision needed beyond F1/F2.

## Prior Deliberations

- `DELIB-20265496` (Loyal Opposition NO-GO - WI-4701 Codex adapter CRLF
  whitespace fix). Directly on point: a prior LO NO-GO on a near-identical CRLF
  whitespace fix, on the grounds that the fix's implementation scope did not
  fully match what the fix would touch and "a GO must not leave that scope
  decision to the implementation session." WI-4701 then cycled NO-GO ->
  REVISED (through -009) -> VERIFIED. The same scope-completeness principle
  drives F1 here: the durable fix touches `.gitattributes`, which the proposal
  omits from scope.
- `DELIB-20260710-FIRST-STABILIZATION-BATCH-APPROVAL` and
  `DELIB-20260710-BACKLOG-DRIVE-AUTHORIZATION` are cited by the proposal as the
  owner-approval and project-authorization basis; the applicability preflight
  passed and the PAUTH/project linkage is present. Authority is not the basis
  for this NO-GO.

## Prime Builder Implementation Context

| Element | Detail |
| --- | --- |
| Objective | Make the WI-5114 `.gitignore` LF normalization durable and self-verifying, not a one-shot flip. |
| Preconditions | Latest bridge status returns to actionable for Prime (REVISED); scope covers `.gitignore`, `.gitattributes`, and the new test. |
| Evidence paths | `.gitattributes` (no `.gitignore` pin); `.gitignore` (`i/crlf` per `git ls-files --eol`); `git config core.autocrlf` (unset/false); `git diff --numstat[ --ignore-cr-at-eol] fac6e892^ fac6e892 -- .gitignore` (62/30 vs 32/0). |
| File touchpoints | `.gitignore` (rewrite to LF), `.gitattributes` (add `/.gitignore text eol=lf`), `platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py` (ignore-matching + no-CR EOL assertion). |
| Implementation sequence | (1) Add the `.gitattributes` pin; (2) rewrite `.gitignore` to LF (byte-equivalent ignore rules); (3) add the test (ignore-matching + no-CR); (4) stage all three; (5) confirm `git diff --check` and `git diff-tree --check HEAD^ HEAD -- .gitignore` are clean in the scoped commit. |
| Verification steps | `git ls-files --eol .gitignore` reports `i/lf`; focused pytest passes; `git diff-tree --check` clean; ignore behavior unchanged via `git check-ignore` probes on `.harness-tmp/`, `work_area/`, `.loyal-opposition/`, and the helper-scratch globs. |
| Rollback | One scoped revert of `.gitignore`, `.gitattributes`, and the test; no local scratch files are touched. |
| Open decisions | None required from the owner - F1/F2 are mechanical scope/coverage completions within the already-approved non-destructive stabilization scope. |

## Required changes for GO

1. F1 - add `.gitattributes` to `target_paths` and pin `.gitignore` to LF
   (e.g. `/.gitignore text eol=lf`), landed in the same scoped commit.
2. F2 - add a standing no-CR / `i/lf` EOL assertion for `.gitignore` to the
   focused test so the linked `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
   actually covers the EOL behavior.
3. F3 (optional) - adjust the "repository's LF form" wording once F1 lands.

## Verification methodology trail

Commands run for this review (read-only): `git log/show/diff-tree/diff
--numstat[ --ignore-cr-at-eol]` on `fac6e892`; `git ls-files --eol` (single
files and whole-tree distribution); CR-byte counts via `git show <blob> | tr -cd
'\r' | wc -c` on parent/fac6e892/HEAD/worktree; `git config core.autocrlf|eol|
whitespace`; `cat .gitattributes`; `scripts/bridge_applicability_preflight.py
--bridge-id gtkb-wi5114-scratch-ignore-hygiene` (passed); `gt deliberations
search` (surfaced `DELIB-20265496`); `gt spec show GOV-WORK-TREE-HYGIENE-001`
(exists); sibling-thread check via `grep -rl 'WI-5114' bridge/` (no duplicate
thread).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
