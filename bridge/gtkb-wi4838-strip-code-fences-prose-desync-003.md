NEW

# GT-KB Bridge Implementation Report — gtkb-wi4838-strip-code-fences-prose-desync — 003

bridge_kind: implementation_report
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f95c6f19-b1a8-4602-8d22-43886dcdf659
author_model: claude-opus-4-8
author_model_version: opus-4.8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)
Document: gtkb-wi4838-strip-code-fences-prose-desync
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4838-strip-code-fences-prose-desync-002.md
Approved proposal: bridge/gtkb-wi4838-strip-code-fences-prose-desync-001.md
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4838
Recommended commit type: fix

## Implementation Claim

The GO'd `-001` scope is implemented and committed in `8a3d5920c`
(`fix(bridge): matched open/close parser in _strip_code_fences (WI-4838)`).
`_strip_code_fences` (`scripts/bridge_applicability_preflight.py`) previously flipped a
single `in_fence` boolean on any line whose start matched a fence-marker run, which
desynced on two real inputs. It is now a matched open/close parser:

- A new module regex matches a leading run of three-or-more of the same fence character
  plus the remainder of the line.
- `_is_fence_opener(run, rest)` accepts an opener only when the info string is a single
  token (and, for backtick fences, contains no backtick) — rejecting wrapped prose lines
  that merely begin with a fence marker followed by several words.
- `_is_fence_closer(line, fence_char, fence_len)` accepts a closer only when the line is a
  bare run of at least the opener length of the SAME fence character followed by only
  whitespace — so a marker-plus-language line inside a fence no longer closes it early.
- `_strip_code_fences` tracks the opener's fence character and length and uses those
  helpers; the signature and blank-the-fence output contract are unchanged.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the applicability preflight is a load-bearing bridge gate; its prose-scan accuracy is part of bridge-state correctness.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the preflight enforces spec-link citation by scanning prose; this fix protects that scan from fence-stripper desync.
- `GOV-RELIABILITY-FAST-LANE-001` — eligibility basis (small defect fix under the standing PAUTH).
- `GOV-STANDING-BACKLOG-001` — WI-4838 is the governing backlog item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied by the spec-to-test mapping below.
- Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Owner Decisions / Input

Carried forward from the approved proposal `-001`:

- `DELIB-20266139` (AskUserQuestion, interactive PB session 2026-06-26): the owner chose
  **"Reliability fast-lane"** — WI-4838 was added to PROJECT-GTKB-RELIABILITY-FIXES
  (membership `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-4838`, active), so the standing
  membership-based `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (source + test_addition)
  covers this change. The implementation-start packet (`packet_hash sha256:d214b151…`)
  validated that authorization before any source edit. No new owner decision is required.

## Prior Deliberations

- `bridge/gtkb-wi4838-strip-code-fences-prose-desync-001.md` — approved proposal carried forward.
- `bridge/gtkb-wi4838-strip-code-fences-prose-desync-002.md` — LO GO verdict (Cursor, harness E, session `cursor-lo-autoproc-2026-06-27-queue`).
- `DELIB-20266139` — owner fast-lane authorization.

## Specification-Derived Verification Plan

| Requirement clause | Test | Result |
| --- | --- | --- |
| Prose-wrap class no longer desyncs (WI-4838 core) | `test_strip_code_fences_ignores_prose_marker_line` | PASS |
| Inner-marker class no longer closes early | `test_strip_code_fences_inner_marker_does_not_close` | PASS |
| Genuine paired fence still fully stripped (no regression) | `test_strip_code_fences_strips_paired_block` | PASS |
| Single-info-token opener still recognized | `test_strip_code_fences_opener_with_single_info_token` | PASS |
| Closer char + length matching | `test_strip_code_fences_closer_must_match_char_and_length` | PASS |
| No regression in the preflight suite | full `test_bridge_applicability_preflight.py` | PASS (21 passed) |
| End-to-end: preflight on the real WI-4838 proposal with the fixed stripper | `bridge_applicability_preflight.py --bridge-id gtkb-wi4838-strip-code-fences-prose-desync` | `preflight_passed: true`, `missing_required_specs: []` |

## Commands Run

Interpreter: `groundtruth-kb/.venv/Scripts/python.exe` (Python 3.14.0).

- `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -k "strip_code_fences" -q --tb=short`
- `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short`
- `python -m ruff check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py`
- `python -m ruff format --check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4838-strip-code-fences-prose-desync`

## Observed Results

- New WI-4838 tests: `5 passed, 16 deselected`.
- Full `test_bridge_applicability_preflight.py` suite: `21 passed` (16 pre-existing + 5 new; no regression).
- `ruff check`: `All checks passed!`  `ruff format --check`: `2 files already formatted`.
- End-to-end preflight on the real proposal: `preflight_passed: true`, `missing_required_specs: []`.

## Files Changed

Scoped to the GO'd `target_paths`; committed in `8a3d5920c` (2 files changed, +121 / -5):

- `scripts/bridge_applicability_preflight.py` — `_FENCE_OPEN_RE` constant, `_is_fence_opener`, `_is_fence_closer`, and the matched open/close `_strip_code_fences`.
- `platform_tests/scripts/test_bridge_applicability_preflight.py` — 5 spec-derived tests (first coverage for `_strip_code_fences`).

No other files were changed by this work.

## Recommended Commit Type

- Recommended commit type: `fix:` — repairs a fence-stripper state desync that corrupts the applicability preflight's prose scan. Function signature and output contract unchanged; no new capability surface. (Landed under this exact `fix:` commit `8a3d5920c`.)

## Acceptance Criteria Status

1. A prose line that is a fence marker followed by multiple words does not toggle the fence state. — MET (`*_ignores_prose_marker_line`).
2. Inside a fence, only a bare, same-character, length-matched closer ends it. — MET (`*_inner_marker_does_not_close`, `*_closer_must_match_char_and_length`).
3. Genuine paired blocks are still fully stripped; bare and single-info-token openers are still recognized. — MET (`*_strips_paired_block`, `*_opener_with_single_info_token`).
4. The full `test_bridge_applicability_preflight.py` suite passes. — MET (21 passed).
5. `ruff check` and `ruff format --check` pass on both files. — MET.

## Risk And Rollback

- Risk: a real multi-word info string is now treated as prose rather than a fence opener (documented residual; rare in bridge proposals where openers are bare or a single language token). Mitigation: the opener/paired tests lock the recognized forms; the full suite guards integration.
- Rollback: revert commit `8a3d5920c` (the helpers + rewritten `_strip_code_fences` + 5 tests); the prior single-toggle form returns. No schema change; no other preflight surface touched.

## Loyal Opposition Asks

1. Verify the implementation against the linked specs and the executed command evidence above (report author session `f95c6f19-b1a8-4602-8d22-43886dcdf659`; the GO author was the independent Cursor LO session `cursor-lo-autoproc-2026-06-27-queue`).
2. Return VERIFIED if the report and implementation (commit `8a3d5920c`) satisfy the approved proposal `-001`; otherwise NO-GO with findings.
