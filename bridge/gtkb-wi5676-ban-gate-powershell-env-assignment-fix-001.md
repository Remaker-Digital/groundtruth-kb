NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: dbc5c1cd-13f2-4ff8-81a5-a80c06799bae
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal
Document: gtkb-wi5676-ban-gate-powershell-env-assignment-fix
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5676

target_paths: ["groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py", "groundtruth-kb/tests/framework/test_bash_enforcement_parser.py"]

# Defect-Fix Proposal — DIRECT-HARNESS-INVOKE-BAN false-positive on PowerShell env assignments

## Claim

`_drop_leading_assignments` in `groundtruth_kb/enforcement/__init__.py` recognizes
only POSIX-form environment assignments (`VAR=value`). PowerShell's assignment
form (`$env:VAR='value'`) is not recognized, so the assignment token is never
stripped. `_command_name` then derives the command head from that token's last
`/`-delimited segment, so any assignment whose VALUE ends in a harness name is
misread as a direct harness launch and denied.

## Defect / Reproduction

Root cause chain (verified by reading the code path, session dbc5c1cd 2026-07-24):

1. `_COMMAND_SEGMENT_RE` splits on `;`, yielding the segment
   `$env:GTKB_AUTHOR_IDENTITY='prime-builder/claude'`.
2. `_COMMAND_TOKEN_RE` keeps that whole run as one token (it starts with `$`, so
   neither quoted alternative matches at position 0).
3. `_drop_leading_assignments` (L136-144) tests
   `_ENV_ASSIGNMENT_RE = ^[A-Za-z_][A-Za-z0-9_]*=...` against the token. The token
   starts with `$`, so there is no match and the token is NOT dropped.
4. `head = _command_name(tokens[0])` → `_token_basename` strips the trailing
   quote, replaces `\` with `/`, and takes `rsplit("/", 1)[-1].lower()` → **`claude`**.
5. `claude` is in `_DIRECT_HARNESS_COMMANDS` (L39-51) → `_DIRECT_HARNESS_DENIAL`.

Observed probe matrix (session dbc5c1cd) — consistent with the chain above:

| Command | Basename derived | Result |
| --- | --- | --- |
| `$env:GTKB_AUTHOR_IDENTITY='prime-builder/claude'; ...` | `claude` | DENIED (false positive) |
| `$env:GTKB_AUTHOR_HARNESS_ID='B'; ...` | `b` | allowed |
| `$env:GTKB_SESSION_ID='dbc5c1cd-...'; ...` | (no harness name) | allowed |
| `$env:GTKB_BRIDGE_DISPATCH_KEYWORD='::init gtkb pb'; ...` | `pb` | allowed |

The trigger is NOT the variable name; it is any PowerShell assignment whose value's
final path segment matches a harness name. `prime-builder/claude` is the value
mandated by the documented bridge-write flow, so the defect blocks that flow on
the PowerShell surface.

## Proposed Scope

1. Add a PowerShell env-assignment pattern beside `_ENV_ASSIGNMENT_RE`:

   `_PS_ENV_ASSIGNMENT_RE = re.compile(r"^\$env:[A-Za-z_][A-Za-z0-9_]*\s*=\s*(?:\"[^\"]*\"|'[^']*'|\S+)$", re.IGNORECASE)`

2. In `_drop_leading_assignments`, drop leading tokens matching EITHER
   `_ENV_ASSIGNMENT_RE` or `_PS_ENV_ASSIGNMENT_RE`.

No change to `_DIRECT_HARNESS_COMMANDS`, the denial strings, or any other
detection branch. The ban's actual protection is unchanged: a real harness launch
following an assignment is still detected, because only the assignment tokens are
stripped and the following command head is still evaluated.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`:
`groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`,
`groundtruth-kb/tests/framework/test_bash_enforcement_parser.py`.

## Specification Links

- `SPEC-INTAKE-21c5b3` — the direct-harness-invoke ban this gate enforces; the fix must preserve its protection.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge authority; the defect blocks the governed bridge-write flow.
- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane eligibility basis for this small, bounded defect fix.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied by the verification plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied by the project-linkage triple above.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable capture of the defect and its fix.

## Prior Deliberations

- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` — the owner ban this gate enforces (protection must be preserved).
- `DELIB-202666312` — inter-harness isolation restriction; per-access owner approval supplied by `DELIB-202667470`.
- `DELIB-202667470` — owner authorization to implement WI-5676.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — standing reliability fast-lane authorization basis.
- Prior false-positive threads in the same matcher: `bridge/gtkb-wi5037-invoke-ban-false-positive-004.md` (VERIFIED) and `bridge/gtkb-direct-harness-invoke-ban-newline-segment-false-positive-001.md` (ADVISORY, open). This proposal is a THIRD false-positive class in the same code path; the reviewer may wish to consider whether a systemic tokenizer review is warranted as follow-on work.

## Owner Decisions / Input

- `DELIB-202667470` (owner authorization, 2026-07-24): "I authorize these: WI-5676, WI-5677, WI-5678. Please proceed with implementation." Authorization permits autonomous progress through the bridge protocol; it does not waive LO `GO`, the implementation-start packet, the report, or `VERIFIED`.
- `DELIB-202666312` per-access owner approval for touching change-controlled governance artifacts during the modernization program.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-21c5b3` and
`DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` already define the intended
behavior: deny direct harness-to-harness launches. This fix corrects a matcher
defect that denies commands the ban was never intended to cover (PowerShell
environment assignments). It restores the specified behavior rather than
changing or extending it, so no new or revised requirement is needed before
implementation.

## Specification-Derived Verification Plan

| Requirement (linked spec) | Test / command | Expected |
| --- | --- | --- |
| PowerShell assignment no longer false-positives (`GOV-FILE-BRIDGE-AUTHORITY-001`) | new test: `$env:GTKB_AUTHOR_IDENTITY='prime-builder/claude'; python x.py` | allowed |
| Ban protection preserved (`SPEC-INTAKE-21c5b3`) | new test: `$env:FOO='bar'; claude` | DENIED |
| Bare harness launch still denied (`SPEC-INTAKE-21c5b3`) | existing tests for `claude`, `codex exec`, harness shims | DENIED (unchanged) |
| POSIX assignments unaffected | existing `_ENV_ASSIGNMENT_RE` tests | unchanged |
| No regression | `python -m pytest groundtruth-kb/tests/framework/test_bash_enforcement_parser.py -q` | all pass |
| Code quality | `ruff check` AND `ruff format --check` on both target paths | pass |

## Acceptance Criteria

- PowerShell env assignments whose values end in a harness name no longer produce a denial.
- Every existing direct-harness-launch denial still fires (no weakening of the ban).
- Focused test suite passes; ruff check and ruff format --check both pass.
- Scoped commit contains only the two declared target paths.

## Risks / Rollback

Risk: an over-broad assignment regex could let a crafted token slip past the head
check. Mitigated by anchoring the pattern (`^\$env:` ... `$`) and by the
explicit "ban preserved" tests above. Rollback: revert the scoped commit; the
gate returns to current behavior.

## Recommended Commit Type

Recommended commit type: `fix`
