NEW
::init gtkb pb
::open build

# GT-KB Bridge Implementation Report - gtkb-wi5676-ban-gate-powershell-env-assignment-fix - 003

bridge_kind: implementation_report
Document: gtkb-wi5676-ban-gate-powershell-env-assignment-fix
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5676-ban-gate-powershell-env-assignment-fix-002.md
Approved proposal: bridge/gtkb-wi5676-ban-gate-powershell-env-assignment-fix-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5676
Recommended commit type: fix:

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 932aad8d-99df-440f-82e5-b1e122e5eb0f
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb (transcript_init_keyword); build activity envelope

target_paths: ["groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py", "groundtruth-kb/tests/framework/test_bash_enforcement_parser.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Implementation Claim

The DIRECT-HARNESS-INVOKE-BAN gate no longer false-positives on PowerShell
environment assignments. `_drop_leading_assignments` now recognizes the
PowerShell form `$env:VAR='value'` in addition to the POSIX form `VAR=value`,
so the assignment token is stripped before the command head is derived.

Governance-visible behavior change: the mandated bridge-write flow value
`prime-builder/claude` (and any other assignment value whose final path segment
matches a harness name) is no longer misread as a direct harness launch. The
ban's protection is unchanged - only leading assignment tokens are dropped, and
the following command head is still evaluated.

## Root Cause (confirmed against HEAD 7c033d11c)

1. `_COMMAND_SEGMENT_RE` splits on `;`, yielding `$env:GTKB_AUTHOR_IDENTITY='prime-builder/claude'`.
2. `_COMMAND_TOKEN_RE` keeps that whole run as one token (it starts with `$`,
   so neither quoted alternative matches at position 0).
3. `_drop_leading_assignments` tested only `_ENV_ASSIGNMENT_RE`
   (`^[A-Za-z_][A-Za-z0-9_]*=...`). The token starts with `$`, so it was NOT dropped.
4. `head = _command_name(tokens[0])` -> `_token_basename` strips the trailing
   quote, normalizes `\` to `/`, and takes `rsplit("/", 1)[-1].lower()` -> `claude`.
5. `claude` is in `_DIRECT_HARNESS_COMMANDS` -> `_DIRECT_HARNESS_DENIAL`.

## Changes By File

1. `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`
   - Added `_PS_ENV_ASSIGNMENT_RE` beside `_ENV_ASSIGNMENT_RE`, exactly as the
     approved proposal specified, with a comment recording the defect chain.
   - `_drop_leading_assignments` now drops leading tokens matching EITHER
     pattern. No change to `_DIRECT_HARNESS_COMMANDS`, the denial strings, or
     any other detection branch.

2. `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py`
   - `test_bash_parser_allows_powershell_env_assignment_with_harness_valued_name`
     (5 cases: single-quoted and double-quoted `prime-builder/claude`,
     `loyal-opposition/codex`, a session UUID, and an init-keyword value).
   - `test_bash_parser_still_blocks_harness_launch_after_powershell_assignment`
     (4 cases proving the ban is preserved behind an assignment).

## Reviewer Note - one proposal detail found inert

The approved regex includes `\s*=\s*`. Those `\s*` groups are unreachable in
practice: `_COMMAND_TOKEN_RE` splits on whitespace, so a spaced form
(`$env:FOO = 'bar'`) never arrives as a single token. The regex was implemented
verbatim as GO'd because it is harmless and matches the approved text, but the
spaced PowerShell form is NOT covered by this fix. If the reviewer wants it
covered, that is a tokenizer change and belongs in a separate thread - see the
systemic note below.

## Systemic Observation (no action taken)

This is the THIRD false-positive class found in this same tokenizer:

- `bridge/gtkb-wi5037-invoke-ban-false-positive-004.md` (VERIFIED)
- `bridge/gtkb-direct-harness-invoke-ban-newline-segment-false-positive-001.md` (ADVISORY, open)
- this thread (WI-5676)

The approved proposal itself raised this and suggested the reviewer consider
whether a systemic tokenizer review is warranted as follow-on work. No such work
was performed here; the implemented change is exactly the GO'd scope.

## Specification Links

- `SPEC-INTAKE-21c5b3` - the direct-harness-invoke ban this gate enforces;
  protection preserved and proven by the blocked-case tests.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the defect blocked the governed bridge-write flow.
- `GOV-RELIABILITY-FAST-LANE-001` - fast-lane basis for this bounded defect fix.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - carried forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - see mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project-linkage triple declared above.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - defect and fix captured durably.

## Spec-to-Test Mapping

| Requirement (linked spec) | Test / command | Executed | Result |
| --- | --- | --- | --- |
| PowerShell assignment no longer false-positives (`GOV-FILE-BRIDGE-AUTHORITY-001`) | `test_bash_parser_allows_powershell_env_assignment_with_harness_valued_name` (5 cases) | yes | PASS - all allowed |
| Ban protection preserved (`SPEC-INTAKE-21c5b3`) | `test_bash_parser_still_blocks_harness_launch_after_powershell_assignment` (4 cases) | yes | PASS - all denied with both required strings |
| Bare harness launch still denied (`SPEC-INTAKE-21c5b3`) | existing `test_bash_parser_blocks_direct_harness_launches` (11 cases, including the pre-existing PowerShell-assignment spoof case that prefixes a harness launch with `$env:GTKB_DISPATCHER_MEDIATED=1;`) | yes | PASS - unchanged |
| Helper-script association still denied | existing `test_bash_parser_blocks_direct_gtkb_helper_script_file_association` | yes | PASS - unchanged |
| POSIX assignments unaffected | existing allow/block cases incl. `FOO=bar claude` (deny) and `FOO=bar python x.py` (allow) | yes | PASS - unchanged |
| No regression (`GOV-RELIABILITY-FAST-LANE-001`) | full focused module | yes | PASS - 8 passed (was 6; +2 new, 0 regressions) |
| No security-corpus regression | `platform_tests/scripts/test_gate_fp_corpus.py` (the governed false-positive/blocked corpus) | yes | PASS - 34 passed |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this mapping plus the commands below | yes | PASS |
| Code quality | `ruff check` and `ruff format --check` on both targets | yes | PASS - exit 0; "2 files already formatted" |
| Scoped diff | `git diff --stat` over the two targets | yes | PASS - 2 files, +49/-1 |

## Commands Executed

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/framework/test_bash_enforcement_parser.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gate_fp_corpus.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py groundtruth-kb/tests/framework/test_bash_enforcement_parser.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py groundtruth-kb/tests/framework/test_bash_enforcement_parser.py
git diff --stat -- <two targets>
python scripts/bridge_claim_cli.py claim gtkb-wi5676-ban-gate-powershell-env-assignment-fix
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5676-ban-gate-powershell-env-assignment-fix
```

A direct 9-case behavior probe was also run against `check_bash_command` before
writing the tests, covering the proposal's full matrix. All 9 matched
expectations: the PowerShell-assignment false positives now ALLOW, and every
harness-launch form (bare, flagged, behind a PowerShell assignment, behind a
POSIX assignment, and `codex exec`) still DENIES.

Observed results:

- Pre-change baseline: focused module collected 6 tests; the probe reproduced the
  false-positive denial for `$env:GTKB_AUTHOR_IDENTITY='prime-builder/claude'; python x.py`.
- Post-change: `8 passed in 0.08s`; `34 passed, 1 warning` on the gate FP corpus
  (the single warning is pre-existing and unrelated).
- `ruff check`: `All checks passed!` (exit 0).
- `ruff format --check`: `2 files already formatted` (exit 0).
- `git diff --stat`: 2 files changed, 49 insertions(+), 1 deletion(-).

**Disclosed intermediate failure.** The first `ruff format --check` run FAILED
(exit 1) while `ruff check` passed - the documented separate-gate trap. The
multi-line `re.compile(...)` I wrote was short enough for ruff to want joined onto
one line. Resolved by applying exactly the single-line diff `ruff format --diff`
proposed, entirely inside this change's own hunk; no pre-existing code was
reformatted. Both gates then passed and the module plus corpus were re-run green.

## Acceptance Criteria Check

1. **PowerShell env assignments whose values end in a harness name no longer
   produce a denial.** MET - 5 allowed cases asserted, probe confirmed.
2. **Every existing direct-harness-launch denial still fires (no weakening of
   the ban).** MET - existing 11-case blocked test unchanged and green, 4 new
   blocked cases added, and the 34-case governed FP corpus passes.
3. **Focused test suite passes; ruff check and ruff format --check both pass.**
   MET.
4. **Scoped commit contains only the two declared target paths.** MET at the
   diff level - 2 files. No commit was created (see disclosure below).

## Concurrency / Work-Tree Disclosure

- Work-intent claim acquired before mutation (`claim_kind: go_implementation`,
  session `932aad8d`); released after filing.
- Implementation-start packet created from the live latest-`GO`: `allowed: true`,
  PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` v1, both targets
  classified (1 `source`, 1 `test`).
- Both targets were clean immediately before implementation and were modified by
  no other session.
- The wider worktree carries a large volume of unrelated uncommitted changes from
  a concurrently active counterpart harness session. None were staged, committed,
  reverted, or otherwise disturbed.
- **No commit was created.** VERIFIED commit-finalization is currently broken
  platform-wide: the `verify` -> `gtkb-verify` skill rename left the rule-cited
  helper path `.claude/skills/verify/helpers/write_verdict.py` non-existent (only
  `.claude/skills/gtkb-verify/helpers/write_verdict.py` exists), and the
  auto-finalization sweep logs `canonical finalizer validation unavailable: No
  module named 'write_verdict'`. Nine terminal VERIFIED verdicts are currently
  untracked in `bridge/`. The owner has been informed and directed that
  implementation continue with commits deferred. Terminal finalization for this
  thread is therefore expected to wait on the WI-5661..WI-5668 repair cluster.
- Terminal `VERIFIED` remains reserved for an independent Loyal Opposition
  session; this author session cannot verify its own work.

## Owner Decisions / Input

- `DELIB-202667470` (owner authorization, 2026-07-24): "I authorize these:
  WI-5676, WI-5677, WI-5678. Please proceed with implementation." This authorizes
  autonomous progress through the bridge protocol; it does not waive LO `GO`, the
  implementation-start packet, this report, or `VERIFIED`.
- `DELIB-202666312` - per-access owner approval for touching change-controlled
  governance artifacts during the modernization program.
- Owner direction in this session authorized draining PB-actionable bridge work
  restricted to threads not overlapping the concurrent session's uncommitted work,
  and subsequently directed that draining continue with commits deferred while
  finalization is broken.

## Prior Deliberations

- `DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN` - the owner ban this gate enforces;
  protection preserved and test-pinned.
- `DELIB-202667470` - owner authorization to implement WI-5676.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane basis.
- `DELIB-202666312` - inter-harness isolation restriction.
- `DELIB-20260724-DISPATCHER-QUIESCENCE-MANUAL-LO` - the TAFE dispatcher is
  deliberately quiesced in favor of manual Loyal Opposition processing. Relevant
  as routing context only: this report will not be picked up automatically. No
  dispatch behavior is touched by this change.
- Prior false-positive threads in the same matcher:
  `bridge/gtkb-wi5037-invoke-ban-false-positive-004.md` (VERIFIED) and
  `bridge/gtkb-direct-harness-invoke-ban-newline-segment-false-positive-001.md`
  (ADVISORY, open).

## Risk / Rollback

Risk is low and bounded. The stated risk - an over-broad assignment regex letting
a crafted token slip past the head check - is mitigated by anchoring the pattern
(`^\$env:` ... `$`), by the four explicit ban-preserved tests, and by the 34-case
governed FP corpus passing unchanged. The fix strips only leading tokens that
fully match an anchored assignment form; anything else still reaches the head
check.

Rollback is a revert of the two changed files under separate authority. Bridge
files are append-only and untouched.

## Recommended Commit Type

`fix:` - as the proposal recommended. This repairs a matcher defect that denied
commands the ban was never intended to cover. The scaffold's default `feat:` was
overridden because no new capability is added; specified behavior is restored.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
