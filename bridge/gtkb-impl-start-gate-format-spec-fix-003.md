REVISED

# Implementation Proposal - implementation_start_gate MUTATING_COMMAND_RE Python Format-Spec False-Positive Fix - REVISED-1 (WI-3317)

bridge_kind: implementation_proposal
Document: gtkb-impl-start-gate-format-spec-fix
Version: 003
Responds to: bridge/gtkb-impl-start-gate-format-spec-fix-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3317

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

This REVISED-1 addresses the NO-GO at `bridge/gtkb-impl-start-gate-format-spec-fix-002.md`:

- **F1 (P1/blocking)** - the REVISED-0 regex `(?:^|\s)>{1,2}\s*[^\s&>]` required whitespace/BOL immediately before `>`, dropping numbered and combined real-file redirects (`1>`, `2>`, `&>`) that the existing test suite asserts as mutating -> **closed** by replacing the redirect alternation with a negative-lookbehind design that preserves every real redirect form and excludes only the Python format-spec / arrow cases.
- **F2 (P2)** - `target_paths` named a non-existent top-level `tests/scripts/test_implementation_start_gate.py` -> **closed**: `target_paths` and the verification command now reference only the existing `platform_tests/scripts/test_implementation_start_gate.py`.

## Claim

`MUTATING_COMMAND_RE`'s redirect alternation is currently `(^|[^>])>{1,2}($|[^&])`. The `(^|[^>])` group accepts ANY non-`>` character before the redirect operator, so it matches Python format-spec alignment (`{x:>2}` -> command text `:>2}`) and arrow tokens (`->`) inside read-only `python -c` strings. The fix replaces the leading group with a negative lookbehind that excludes exactly the false-positive contexts (`:` format-spec colon, `-` arrow, `>` mid-run) while still matching every real shell redirect.

## In-Root Placement Evidence

Both target paths in-root under `E:\GT-KB`: `scripts/implementation_start_gate.py`, `platform_tests/scripts/test_implementation_start_gate.py`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected behavior; this fix narrows false-positives without weakening true-positive redirect detection.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root paths only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3317 is a tracked work item.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation-start-gate is part of the authorization-enforcement surface.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

The hook's regex is its own implementation surface; this is a defect fix. The existing regex shape is the de-facto spec, and the change narrows the false-positive set while preserving the true-positive set, proven by tests.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive; AUQ "MUTATING_COMMAND_RE format-spec false-positive -> Add as 6th WI" (2026-05-14).
- `bridge/gtkb-impl-start-gate-format-spec-fix-002.md` - NO-GO under remediation by this REVISED-1.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner AUQ added WI-3317 as the 6th WI of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001`.
- 2026-05-15 UTC, S350+: owner directive "Proceed with WI-3316 and WI-3317."

No new owner decision required; this REVISED-1 is a mechanical defect-fix correction.

## Requirement Sufficiency

Existing requirements sufficient. The hook's intent (block mutating shell redirects on protected paths) is established by `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` and the existing regex shape. This REVISED-1 narrows the regex without changing intent and proves preservation of every redirect true-positive by test.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (WI-3317), an active member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (regex fix) + IP-2 (tests) single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-impl-start-gate-format-spec-fix-003.md`; `REVISED:` line prepended. Prior `NO-GO: -002` and `NEW: -001` lines preserved. Append-only audit trail intact.

## Proposed Scope

### IP-1: Replace the MUTATING_COMMAND_RE redirect alternation

In `scripts/implementation_start_gate.py`, the redirect alternation of `MUTATING_COMMAND_RE` changes:

- Old: `(^|[^>])>{1,2}($|[^&])`
- New: `(?<![:>-])>{1,2}(?![&])`

`(?<![:>-])` is a fixed-width negative lookbehind: the redirect operator must NOT be immediately preceded by `:` (Python format-spec alignment colon), `-` (the `->` arrow), or `>` (a position inside a `>` run). `>{1,2}` preserves single and append redirects. `(?![&])` preserves the existing behavior of not flagging the stderr/stdout dup form `>&`.

This preserves every real redirect form, because the lookbehind only excludes `:`/`-`/`>`:

- `cmd > out.txt` - `>` preceded by space -> matched.
- `cmd >> out.txt` - matched.
- `cmd 1> out.txt` - `>` preceded by `1` -> matched.
- `cmd 2> err.txt` - `>` preceded by `2` -> matched.
- `cmd &> out.txt` - `>` preceded by `&` -> matched.
- `cmd>out.txt` (no space) - `>` preceded by `d` (word char) -> matched.

And it excludes the false-positive cases:

- `python -c "print(f'{x:>2}')"` - `>` preceded by `:` -> NOT matched.
- arrow `->` (e.g. in a type annotation or comment inside `python -c`) - `>` preceded by `-` -> NOT matched.
- `2>&1` (stderr-to-stdout dup, not a file write) - excluded by `(?![&])`, unchanged from current behavior.

`NULL_SINK_REDIRECT_STRIP_RE` is independent and unchanged.

### IP-2: Format-spec and redirect-preservation regression tests

In `platform_tests/scripts/test_implementation_start_gate.py`, add regression tests covering BOTH the false-positive elimination AND the true-positive preservation (per F1).

### IP-3: WI completion

No spec status promotion (no functional spec governs the hook regex). WI-3317 stage advances on Codex VERIFIED.

## Specification-Derived Verification Plan

Tests in `platform_tests/scripts/test_implementation_start_gate.py`:

| Test case | Command | Expected |
|---|---|---|
| Format-spec `:>` | `python -c "print(f'{x:>2}')"` | NOT mutating (was a false positive) |
| Format-spec ` :>` after fill char | `python -c "print(f'{x:>>2}')"` style colon-led | NOT mutating |
| Arrow token `->` | `python -c "x = lambda a: a->None"` style text | NOT mutating |
| Redirect `>` | `echo hi > out.txt` | mutating (preserved) |
| Redirect `>>` | `echo hi >> out.txt` | mutating (preserved) |
| Numbered redirect `1>` | `cmd 1> out.txt` | mutating (preserved) |
| Numbered redirect `2>` | `cmd 2> err.txt` | mutating (preserved) |
| Combined redirect `&>` | `cmd &> out.txt` | mutating (preserved) |
| No-space redirect | `cmd>out.txt` | mutating (preserved) |
| stderr dup `2>&1` | `cmd 2>&1` | NOT mutating (preserved exemption) |
| Null-sink redirect | `cmd 2>/dev/null` | NOT mutating (preserved exemption) |

Verification command:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -v
```

## Acceptance Criteria

- IP-1: the redirect alternation is `(?<![:>-])>{1,2}(?![&])`; format-spec/arrow cases are NOT mutating; all of `>`, `>>`, `1>`, `2>`, `&>`, no-space `cmd>file` remain mutating.
- IP-2: regression tests for every row of the table land; all PASS.
- No regression in any other `test_implementation_start_gate.py` case.
- Both preflights PASS.

## Risks / Rollback

- Risk: an exotic redirect form not in the test matrix could be missed. Mitigation: the new regex only EXCLUDES `:`/`-`/`>`-preceded operators; every other prefix (including word chars) still matches, so the change strictly shrinks the false-positive set and cannot drop a true positive that the current regex catches except `:`/`-`-preceded ones (which are the intended exclusions).
- Rollback: revert the single-alternation regex change; the IP-2 tests stay as behavior documentation.

## Recommended Commit Type

`fix` - corrects a defect in an existing regex; no new capability surface. ~1 line of regex + regression tests.
