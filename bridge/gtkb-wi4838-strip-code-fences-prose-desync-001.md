NEW

# gtkb-wi4838-strip-code-fences-prose-desync — fix _strip_code_fences in_fence desync on prose fence-marker lines (WI-4838)

bridge_kind: prime_proposal
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f95c6f19-b1a8-4602-8d22-43886dcdf659
author_model: claude-opus-4-8
author_model_version: opus-4.8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)
Document: gtkb-wi4838-strip-code-fences-prose-desync
Version: 001

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4838

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-4838 (defect): `_strip_code_fences` (`scripts/bridge_applicability_preflight.py:101`)
strips fenced code blocks from a bridge document so the residual prose can be scanned for
cross-cutting spec triggers. It tracks a single boolean `in_fence` and flips it on EVERY
line whose stripped start matches a fence-marker run (the regex `^\s*(?:` + triple-backtick
+ `|` + triple-tilde + `)`). Because it neither matches a closer to its opener nor
distinguishes a genuine fence-delimiter line from prose, two real inputs desync the state
and cause the scanner to strip (or retain) the wrong spans. This proposal replaces the
single toggle with a matched open/close parser, with no change to the function's signature
or to any other preflight behavior.

## Problem detail (for LO review)

`_strip_code_fences` at `scripts/bridge_applicability_preflight.py:101` compiles
`fence_re = re.compile(r"^\s*(?:‹backtick-run›|‹tilde-run›)")` and, for each line, flips
`in_fence` whenever `fence_re.match(line)` is truthy. Two desync classes follow:

- **Prose-wrap class (the documented WI-4838 case):** a wrapped prose line whose start is a
  fence-marker token followed by ordinary words — e.g. a sentence fragment that begins with
  a three-backtick token and then several prose words — matches `fence_re` and flips
  `in_fence`. The intended fenced blocks then pair against the wrong delimiters and the
  scanner strips real prose (or scans real code).
- **Inner-marker class:** while inside a fence, a content line that begins with a
  fence-marker run plus a language token (the kind of line that appears when a fenced block
  itself shows fenced markup) is treated as a delimiter and closes the fence early, because
  the toggle accepts any marker-prefixed line as a closer rather than requiring a bare,
  same-character, length-matched closer.

There is currently no unit-test coverage for `_strip_code_fences` (no test references the
function), so neither class is guarded today.

## Proposed change

Rewrite `_strip_code_fences` as a matched open/close parser (same signature
`(_strip_code_fences(lines: list[str]) -> list[str]`, same output contract: blanked fence
and interior lines, prose preserved):

1. When NOT inside a fence, a line is treated as a fence **opener** only when it is a run of
   three or more of the SAME fence character (backtick or tilde) optionally followed by a
   single-token info string, where for backtick fences the info string contains no backtick
   (the CommonMark info-string rule). The single-token requirement rejects the prose-wrap
   class: a marker followed by multiple whitespace-separated words is treated as prose, not
   a fence. On a valid opener, record the fence character and run length, blank the line,
   and enter the fence.
2. When inside a fence, a line is a **closer** only when it is a run of at least the opener
   length of the SAME fence character followed by only whitespace (a bare, length-matched
   closer per CommonMark). This rejects the inner-marker class: a marker-plus-language line
   inside a fence no longer closes it. Non-closer lines inside the fence are blanked.
3. Add two small private helpers (`_is_fence_opener(run, rest)` and
   `_is_fence_closer(line, fence_char, fence_len)`) so the open/close rules are independently
   testable.

Residual (documented, not fixed here): a genuinely lone marker line (a bare three-backtick
token on its own line) appearing in prose outside any fence is, per CommonMark, a valid
fence opener and is still treated as one; authors documenting a literal lone fence marker
should describe it in words. The fix targets the two desync classes above, which are the
observed WI-4838 failures.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; the applicability preflight is a load-bearing bridge gate and its prose-scan accuracy is part of bridge-state correctness.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the preflight enforces that proposals cite all relevant specs by scanning prose for triggers; a fence-stripper desync corrupts that scan, so this fix protects the spec-linkage gate's accuracy.
- `GOV-RELIABILITY-FAST-LANE-001` — eligibility basis: a small, localized defect fix routed through the reliability fast-lane under the standing PAUTH.
- `GOV-STANDING-BACKLOG-001` — WI-4838 is the governing backlog item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied by the spec-to-test mapping below.

Cross-cutting artifact-governance specs (advisory):

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact-network framing.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development decision.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — this is a reliability fix to an existing module, not a new artifact-lifecycle surface.

## Prior Deliberations

- `DELIB-20266139` — owner decision (AskUserQuestion, 2026-06-26): authorize WI-4838 via the reliability fast-lane (add to PROJECT-GTKB-RELIABILITY-FIXES; the standing membership-based PAUTH covers source + test_addition).
- Deliberation search ("code fence stripper desync applicability preflight triple backtick prose") found no on-point precedent deciding the fence-parser mechanism; closest results are generic Applicability-Preflight verification records, not the stripper logic.

## Owner Decisions / Input

- `DELIB-20266139` (AskUserQuestion, interactive PB session 2026-06-26): the owner chose
  **"Reliability fast-lane"** — WI-4838 was added to PROJECT-GTKB-RELIABILITY-FIXES
  (membership `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-4838`, active), so the standing
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (allowed_mutation_classes: source,
  test_addition, hook_upgrade) now covers this source + test_addition change. No further
  owner decision is required; implementation remains gated behind Loyal Opposition GO and an
  implementation-start packet.

## Requirement Sufficiency

Existing requirements sufficient. The preflight's contract (strip fenced code so prose can
be accurately scanned for spec triggers, per `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`)
is unchanged; this fix repairs the implementation so it honors that contract on the two
desync inputs. No new or revised requirement is needed.

## Spec-Derived Verification Plan

New tests in `platform_tests/scripts/test_bridge_applicability_preflight.py`, executed with
`groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py`:

| Requirement clause | Test | Assertion |
|---|---|---|
| Prose-wrap class no longer desyncs (WI-4838 core; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` scan accuracy) | `test_strip_code_fences_ignores_prose_marker_line` | A line that is a fence-marker run followed by multiple prose words does NOT enter a fence; following prose is preserved. |
| Inner-marker class no longer closes early | `test_strip_code_fences_inner_marker_does_not_close` | Inside a fence, a marker-plus-language line is blanked (treated as interior), not treated as a closer; only a bare matched closer ends the fence. |
| Genuine paired fence still fully stripped (no regression) | `test_strip_code_fences_strips_paired_block` | A normal opener/interior/bare-closer block is blanked and surrounding prose preserved. |
| Language-info opener still recognized | `test_strip_code_fences_opener_with_single_info_token` | A marker run plus a single language token opens a fence. |
| Closer length + char matching | `test_strip_code_fences_closer_must_match_char_and_length` | A different fence character, or a shorter run, does not close the fence. |
| No regression in the preflight suite | full `test_bridge_applicability_preflight.py` | green |

Commands (run pre-report): the pytest target above; `ruff check` then `ruff format --check`
on the two changed files.

## Acceptance Criteria

1. A prose line that is a fence-marker run followed by multiple words does not toggle `in_fence` (prose-wrap class fixed).
2. Inside a fence, only a bare, same-character, length-matched closer ends it (inner-marker class fixed).
3. Genuine paired fenced blocks are still fully stripped; bare and single-info-token openers are still recognized.
4. The full `test_bridge_applicability_preflight.py` suite passes (no regression).
5. `ruff check` and `ruff format --check` pass on both changed files.

## Risk / Rollback

- Risk: a real multi-word info string (rare in bridge proposals) is now treated as prose rather than a fence opener. Mitigation: bridge fenced blocks use bare or single-language-token openers; the documented residual is noted; the change is confined to `_strip_code_fences` and its helpers.
- Risk: over-stripping regression. Mitigation: the paired-block and opener tests (criteria 3) lock the happy path; the full preflight suite guards integration.
- Rollback: revert `_strip_code_fences` to the single-toggle form and remove the new tests. No schema change; no other preflight surface touched; append-only KB untouched.

## Recommended Commit Type

`fix:` — repairs a fence-stripper state desync that corrupts the applicability preflight's prose scan. No new capability surface; the function signature and output contract are unchanged.
