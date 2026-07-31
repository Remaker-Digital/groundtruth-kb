NEW
::init gtkb pb
::open build

# GT-KB Bridge Implementation Report - gtkb-wi5567-modernization-rc-validate-json - 003

bridge_kind: implementation_report
Document: gtkb-wi5567-modernization-rc-validate-json
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5567-modernization-rc-validate-json-002.md
Approved proposal: bridge/gtkb-wi5567-modernization-rc-validate-json-001.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5567
Recommended commit type: fix:

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 932aad8d-99df-440f-82e5-b1e122e5eb0f
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb (transcript_init_keyword); build activity envelope

target_paths: ["scripts/check_modernization_release_candidate.py", "platform_tests/scripts/test_modernization_release_candidate.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Implementation Claim

The modernization release-candidate checker's `validate` subcommand now accepts a
backward-compatible `--json` flag that emits deterministic machine-readable
validation evidence. Before this change `validate --json` was rejected by argparse
with exit 2, even though canonical RC evidence already invokes that form (see
`bridge/gtkb-wi5339-operation-time-evaluator-baseline-001.md:127`).

Governance-visible behavior change: machine-readable RC validation evidence is now
producible from the production checker. The human-readable form is byte-identical to
before, and the frozen scope digest is unchanged.

## Changes By File

1. `scripts/check_modernization_release_candidate.py`
   - Added `validate_parser.add_argument("--json", action="store_true", dest="as_json")`,
     mirroring the existing `status` subcommand's flag/dest convention rather than
     introducing a second convention.
   - The `validate` branch now binds `capability_count` and `handle_count` once and
     selects an output mode. Both modes derive from the SAME `validate_manifest`
     result, and the `if errors: raise ManifestError(...)` failure path is untouched
     and still executes BEFORE either branch, so no invalid manifest can emit a
     false `PASS` in either mode.
   - The JSON payload is emitted with `json.dumps(..., indent=2, sort_keys=True)`,
     matching the `status --json` rendering.

2. `platform_tests/scripts/test_modernization_release_candidate.py`
   - Added five focused tests under a `WI-5567 / TEST-11619` section adjacent to the
     existing CLI tests, using the module's established `checker` fixture +
     `capsys` + `checker.main([...])` conventions.

## JSON Payload Contract

```json
{
  "capability_count": 8,
  "handle_count": 94,
  "require_test_paths": false,
  "result": "PASS",
  "scope_digest": "AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240"
}
```

Every value is a pure function of the frozen manifest plus the input flag. There is
no clock, no runtime receipt, and no release evidence in the payload, satisfying the
proposal's determinism and "no fabricated release evidence" hard invariants.

**Reviewer note - one field beyond the proposal's literal list.** The proposal named
result, digest, capability count, and handle count. This implementation also emits
`require_test_paths`, because `validate` and `validate --require-test-paths` are two
different validation strictnesses that would otherwise produce indistinguishable
`PASS` evidence. The field is deterministic and is covered by a focused test. If the
reviewer prefers the strictly literal payload, removing the field is a one-line
change plus one test edit.

## Specification Links

- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release-readiness evidence is now
  deterministic and executable rather than a prose claim.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the checker's evidence
  interface fails closed and is directly evaluable.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - JSON automation added without
  impairing the human-readable command or the frozen contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent proposal review, claim/start,
  implementation reporting, and VERIFIED preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the exact checker and
  test changes are bound to these requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - two-file repair bound to
  WI-5567 and the active modernization-assurance PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - both success forms and the
  invalid-manifest failure behavior were executed; see mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-5567 and TEST-11619 remain the durable record.

## Spec-to-Test Mapping

| Specification / acceptance | Test or command | Result |
| --- | --- | --- |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` (plain form unimpaired) | `test_validate_plain_output_remains_unchanged` + live `validate` | PASS - exact string `PASS modernization acceptance manifest (8 capabilities, 94 handles)`, exit 0 |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` (executable machine-readable evidence) | `test_validate_json_emits_frozen_scope_evidence` + live `validate --json` | PASS - payload parses; result PASS; 8 capabilities; 94 handles |
| Frozen digest unchanged | Same test asserts `scope_digest == manifest["program"]["frozen_scope_digest_sha256"]`; live `digest` | PASS - `AD70C6D6...D1EB240`, identical pre- and post-change |
| Determinism hard invariant | `test_validate_json_is_deterministic_across_runs` | PASS - two consecutive runs byte-identical |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` (fail closed) | `test_validate_json_never_emits_pass_for_invalid_manifest` | PASS - exit 1, stdout empty, no `PASS`, error on stderr |
| Payload self-description of strictness | `test_validate_json_records_require_test_paths_flag` | PASS - flag reflected as `true` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (no regression) | Full module: 51 passed (was 46 pre-change) | PASS - 5 added, 0 regressions |
| `GOV-WORK-TREE-HYGIENE-001` | `git status --short` / `git diff --check` over the two targets | PASS - exactly 2 files, whitespace clean |
| Source quality | `ruff check` and `ruff format --check` on both targets | PASS - exit 0; "2 files already formatted" |

## Commands Executed

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_release_candidate.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe scripts/check_modernization_release_candidate.py validate
groundtruth-kb/.venv/Scripts/python.exe scripts/check_modernization_release_candidate.py validate --json
groundtruth-kb/.venv/Scripts/python.exe scripts/check_modernization_release_candidate.py digest
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/check_modernization_release_candidate.py platform_tests/scripts/test_modernization_release_candidate.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/check_modernization_release_candidate.py platform_tests/scripts/test_modernization_release_candidate.py
git status --short -- <two targets>
git diff --stat -- <two targets>
git diff --check -- <two targets>
python scripts/bridge_claim_cli.py claim gtkb-wi5567-modernization-rc-validate-json
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5567-modernization-rc-validate-json
```

Observed results:

- Pre-change baseline: module collected 46 tests; `validate --json` failed argparse
  with `error: unrecognized arguments: --json`, exit 2.
- Post-change: `51 passed, 1 warning`. The single warning is pre-existing and
  unrelated (unknown `asyncio_mode` pytest config option).
- `validate` -> `PASS modernization acceptance manifest (8 capabilities, 94 handles)`, exit 0.
- `validate --json` -> the payload shown above, exit 0.
- `digest` -> `AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240`, exit 0
  (unchanged; `scope_digest()` hashes the manifest only, so checker edits structurally
  cannot move it).
- `ruff check`: `All checks passed!` (exit 0).
- `ruff format --check`: `2 files already formatted` (exit 0).
- `git diff --stat`: 2 files changed, 87 insertions(+), 5 deletions(-).
- `git diff --check`: exit 0, no output.

**Disclosed intermediate failure.** The first `ruff format --check` run FAILED
(exit 1) on the checker: binding `capability_count` / `handle_count` shortened the
human-readable `print(...)` enough that ruff wanted it joined onto one line. This is
the documented separate-gate trap (code can pass `ruff check` and still fail
`ruff format --check`). It was resolved by applying exactly the single line
`ruff format --diff` proposed, entirely inside this change's own hunk - no
pre-existing code was reformatted. Both gates then passed and the full module was
re-run green.

## Acceptance Criteria Check

1. **Plain validate output and exit semantics remain compatible.** MET - byte-identical
   string, exit 0, asserted by a focused test.
2. **JSON output is deterministic and contains no runtime receipt or fabricated
   release evidence.** MET - `sort_keys=True`, values are pure functions of the
   manifest and input flag; repeat-run equality asserted.
3. **Invalid manifests still fail nonzero and never emit a false PASS.** MET - exit 1
   with empty stdout, asserted by a focused test.
4. **The frozen manifest and digest are not modified.** MET - manifest untouched
   (not in target_paths); `digest` output identical.
5. **No dispatcher, TAFE, harness, credential, deployment, release, or
   external-system state is mutated.** MET - only the two declared files changed; no
   command executed wrote RC state (`run-clean`, `attest-run`, `record-audit` were
   not invoked).

## Concurrency / Work-Tree Disclosure

This session implemented alongside a concurrently active counterpart harness session
in the same worktree. Disclosures for the reviewer:

- Work-intent claim acquired before mutation (`claim_kind: go_implementation`,
  session `932aad8d`), released after filing.
- Implementation-start packet created from the live latest-`GO`: `allowed: true`,
  PAUTH `...MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE` v3, both targets
  classified (1 `source`, 1 `test`).
- The implementation-start gate correctly BLOCKED a first edit attempt made after the
  claim but before the packet existed (scope was still bound to a prior thread's
  targets). The packet was then created and the edit proceeded. Recorded here as
  evidence the mechanical gate is functioning, not as a bypass.
- Both targets were verified clean immediately before implementation and were
  modified by no other session; final `git status --short` over the two paths shows
  exactly this change.
- Unrelated uncommitted changes from the concurrent session were neither staged,
  committed, reverted, nor otherwise disturbed.
- No commit was created by this session. Terminal `VERIFIED` finalization is reserved
  for an independent Loyal Opposition session; this author session cannot verify its
  own work.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
  (active, v3) covers WI-5567 source and test work, backed by `DELIB-202666274`.
- Owner direction in this session authorized draining PB-actionable bridge work
  restricted to threads that do not overlap the concurrent session's uncommitted work
  and do not touch shared state or live infrastructure; this thread satisfies that
  constraint.
- No new AskUserQuestion-gated decision class applies to this additive
  source/test change.

## Prior Deliberations

- `DELIB-202666274` - active project-level modernization-assurance authority,
  retaining independent bridge review, claim/start, testing, and finalization gates.
- `DELIB-20260724-DISPATCHER-QUIESCENCE-MANUAL-LO` - the TAFE dispatcher is
  deliberately quiesced in favor of manual Loyal Opposition processing. Relevant
  here only as routing context: this report will not be picked up automatically and
  requires manual LO routing. No dispatch behavior is touched by this change.
- No prior deliberation defines this CLI mismatch; WI-5567 and TEST-11619 are its
  canonical intake and executable assertion.

## Risk / Rollback

Risk is very low. The flag is purely additive, the human-readable path is unchanged
and test-pinned, and `scope_digest()` hashes only the manifest so the frozen digest
cannot move as a result of checker edits. The residual risk named by the proposal - a
JSON payload that looks successful while validation actually failed - is closed by
deriving both modes from one `validate_manifest` result and by the fail-closed test.

Rollback is a revert of the two changed files under separate authority. Bridge files
and the frozen manifest are untouched and append-only.

## Recommended Commit Type

`fix:` - as the proposal recommended. The change repairs a production RC checker
interface that canonical acceptance evidence already invokes but the CLI rejected.
The scaffold's default `feat:` was overridden because this closes a broken
already-referenced interface rather than adding a new capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
