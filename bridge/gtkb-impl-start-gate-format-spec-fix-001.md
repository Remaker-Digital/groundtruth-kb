NEW

# Implementation Proposal - implementation_start_gate MUTATING_COMMAND_RE Python Format-Spec False-Positive Fix (WI-3317)

bridge_kind: implementation_proposal
Document: gtkb-impl-start-gate-format-spec-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3317

target_paths: ["scripts/implementation_start_gate.py", "tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

This NEW proposal fixes a known false-positive in `scripts/implementation_start_gate.py:MUTATING_COMMAND_RE` that misclassifies Python format-spec syntax (e.g., `:>2}`, `:<20}`, `:^10}`) as shell file redirects, blocking read-only `python -c "..."` queries that use simple alignment format specs.

## Claim

`MUTATING_COMMAND_RE`'s second alternation, `(^|[^>])>{1,2}($|[^&])`, intends to detect shell file redirects (`> file`, `>> file`). It incorrectly matches Python format-spec syntax within `python -c` quoted strings (e.g., `f"{value:>2d}"` produces command-text `:>2d}` which satisfies the regex). The fix is a tighter redirect regex that requires whitespace and a redirect target context, plus exemption for `:` followed by `>{1,2}` (format-spec alignment).

Observed at S350 (2026-05-14): query `python -c "print(f'{s[\"version\"]:>2}')"` (a read-only spec verification) was blocked as a mutating command.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-impl-start-gate-format-spec-fix-001.md`. Targets at `E:\GT-KB\scripts\implementation_start_gate.py`, `E:\GT-KB\tests\scripts\test_implementation_start_gate.py`, `E:\GT-KB\platform_tests\scripts\test_implementation_start_gate.py`. No `applications/` paths. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root paths only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping in Specification-Derived Verification Plan.
- `GOV-STANDING-BACKLOG-001` - WI-3317 is a tracked work_item; not a bulk operation.
- `GOV-ARTIFACT-APPROVAL-001` - no protected narrative artifact mutation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation-start-gate is the very hook that enforces this; fix narrows false-positives without weakening the gate's true-positive coverage.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence for this WI.

No directly-governing functional spec exists for the hook's regex (the hook is its own implementation surface). This proposal is a defect fix: the existing regex shape is the de-facto spec, and the change narrows the false-positive set while preserving the true-positive set. Test coverage proves both.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive establishing this project; AUQ "MUTATING_COMMAND_RE Python-format-spec false-positive" answered "Add as 6th WI in this project" (2026-05-14).

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner AUQ "MUTATING_COMMAND_RE Python-format-spec false-positive: add it to this project or track separately?" answered "Add as 6th WI in this project" - authorizes inclusion of WI-3317 in project `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001`.
- 2026-05-14 UTC, S350+: owner AUQ "Bridge dispatch sequencing for the 6 work items" answered "Dispatch WI-3312 + WI-3317 (independent low-priority) in parallel" - explicit authorization to file this NEW now.

No new owner decision required. Fix is mechanical defect-class with preserved true-positive coverage.

## Requirement Sufficiency

Existing requirements sufficient. The hook's intent (block mutating shell redirects on protected paths) is well-established by `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` and the existing regex shape. This proposal narrows the regex without changing intent.

## Clause Scope Clarification (Not a Bulk Operation)

This is NOT a bulk operation. Exactly one work item (WI-3317) is the operative target. WI is an active member of project `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. No spec status mutations, no narrative-artifact edits, no MemBase row additions beyond the optional WI stage transition to `implementing`. Review-packet inventory: IP-1 (regex fix) + IP-2 + IP-3 (tests) scoped to a single thread file.

## Bridge INDEX Update Evidence

This NEW is filed at `bridge/gtkb-impl-start-gate-format-spec-fix-001.md` with a new top-of-file `Document:` entry prepended to `bridge/INDEX.md`.

## Proposed Scope

### IP-1: Tighten MUTATING_COMMAND_RE redirect detection

In `E:\GT-KB\scripts\implementation_start_gate.py`, replace the second alternation of `MUTATING_COMMAND_RE`:

Old: `(^|[^>])>{1,2}($|[^&])`

New: `(?<![:\w])>{1,2}(?![&\w])\s` plus additional anchor: require either whitespace before `>` (true shell redirect) or end-of-token after, AND require the character before `>` is NOT a colon (which precedes Python format-spec alignment) or word character (which is unusual in shell redirects).

Concrete proposed regex (subject to revision per Codex feedback):

```python
r"(?:^|\s)>{1,2}\s*[^\s&>]"
```

This requires:
- whitespace (or BOL) before the `>` (rules out `:>2` format specs and `s>=` operators).
- 1-2 consecutive `>` (preserves `>` and `>>` redirect detection).
- optional whitespace then a non-whitespace, non-`&`, non-`>` token (i.e., a file destination).

The null-sink redirect strip (`NULL_SINK_REDIRECT_STRIP_RE`) is independent and still applies.

### IP-2: Add format-spec regression tests

In `E:\GT-KB\tests\scripts\test_implementation_start_gate.py` (and platform_tests mirror if present):

Add tests covering both false-positive elimination and true-positive preservation. Tests in IP-3 below.

### IP-3: WI completion

Promote WI-3317 from `open` to `verified` after Codex VERIFIED.

## Specification-Derived Verification Plan

Tests derived from the regex narrowing intent:

| Test case | Command | Expected behavior |
|---|---|---|
| Format-spec `:>2}` | `python -c "print(f'{x:>2}')"` | NOT mutating (was mutating) |
| Format-spec `:<20}` | `python -c "print(f'{x:<20}')"` | NOT mutating (was mutating) |
| Format-spec `:^10}` | `python -c "print(f'{x:^10}')"` | NOT mutating (was mutating) |
| Shell redirect `> file` | `echo hi > out.txt` | mutating (preserved) |
| Shell redirect `>> file` | `echo hi >> out.txt` | mutating (preserved) |
| Shell redirect with leading space `cmd > x` | `cat foo > out.txt` | mutating (preserved) |
| Null-sink redirect | `cmd 2>/dev/null` | NOT mutating (preserved exemption) |
| Format-spec with multiple `>` (e.g., `:>>2`) | (rare; Python rejects this) | NOT mutating |
| Heredoc-like `<<EOF` | `cat <<EOF` | NOT mutating (already exempt) |

Test execution: `python -m pytest tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py -v` per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

Implementation reaches `VERIFIED` only when all 9 test cases PASS.

## Acceptance Criteria

- IP-1 regex landed; MUTATING_COMMAND_RE returns False for the 3 format-spec cases.
- IP-1 regex preserves True for the 3 redirect cases.
- IP-2 + IP-3 tests added and all PASS.
- No regression in any other test_implementation_start_gate.py case.
- Bridge applicability preflight and clause preflight both PASS for this bridge ID.

## Risks / Rollback

- Risk: tighter regex might miss exotic redirect forms (e.g., `>&2`, `&>file`). Mitigation: keep null-sink-redirect-strip and add explicit `>&` test in IP-3. If exotic forms surface post-deploy, regex can be widened incrementally.
- Risk: shell tokenizer treats `cmd2>file` (no space) as redirect-from-stderr. Verify with test case.
- Rollback: revert IP-1 single-line regex change. Tests in IP-2 stay (they document the desired behavior).

## Recommended Commit Type

`fix` - corrects a defect in existing regex; no new capability surface. ~10 LOC net.
