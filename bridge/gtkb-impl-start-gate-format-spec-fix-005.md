REVISED

# Implementation Proposal - implementation_start_gate MUTATING_COMMAND_RE Python Format-Spec False-Positive Fix - REVISED-2 (WI-3317)

bridge_kind: prime_proposal
Document: gtkb-impl-start-gate-format-spec-fix
Version: 005
Responds to: bridge/gtkb-impl-start-gate-format-spec-fix-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3317

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

This REVISED-2 is a **Prime-initiated scope correction** filed after the GO at `-004`. Implementing the GO'd REVISED-1 and running its mandated verification command surfaced a verification-blocking issue that REVISED-1 did not anticipate. `target_paths` is unchanged; this REVISED-2 adds IP-3.

## Why REVISED-2 (verification-blocking issue discovered during implementation)

GO Condition 3 at `-004` requires running `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -v`. That command currently produces **4 failures unrelated to the regex change**:

- `test_project_authorization_metadata_is_carried_in_packet`
- `test_project_authorization_load_revalidates_current_spec_exclusions`
- `test_project_authorization_does_not_broaden_target_scope`
- `test_project_authorization_requires_work_item_membership_or_inclusion`

All four fail inside the shared helper `_seed_project_authorization()`, which calls `db.insert_project_authorization(..., status="active")` without `included_spec_ids`. The **WI-3312 spec-linkage gate** (`GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`, VERIFIED at `bridge/gtkb-project-authorize-spec-linkage-gate-008.md`, committed `c7e58260`) now rejects active project authorizations that cite no approved specification. WI-3312's own verification scope was `test_db.py` + `test_cli_projects.py`, so this regression in `test_implementation_start_gate.py` was not caught at WI-3312 verification time.

`test_implementation_start_gate.py` is already an authorized WI-3317 `target_path`, and WI-3317's GO-mandated verification command runs the whole file — so WI-3317 cannot satisfy its own GO Condition 3 without making that helper WI-3312-compliant. REVISED-2 adds IP-3 for exactly that single-helper fix. This is the same coupled-test pattern handled by WI-3314 REVISED-3 and WI-3315 REVISED-3.

## Claim

Unchanged from REVISED-1: the `MUTATING_COMMAND_RE` redirect alternation becomes `(?<![:>-])>{1,2}(?![&])`, excluding Python format-spec (`:>`) and arrow (`->`) false-positives while preserving every real redirect. The only delta is IP-3 — making the predating `_seed_project_authorization()` test helper WI-3312-gate-compliant.

## In-Root Placement Evidence

Both target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected behavior; the fix narrows false-positives without weakening true-positive redirect detection.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - the WI-3312 gate whose now-live behavior IP-3 makes the test helper compliant with.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root paths only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3317 is a tracked work item.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation-start-gate is part of the authorization-enforcement surface.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive; AUQ added WI-3317 as the 6th WI.
- `bridge/gtkb-impl-start-gate-format-spec-fix-002.md` - first NO-GO (regex dropped true positives).
- `bridge/gtkb-impl-start-gate-format-spec-fix-004.md` - GO on REVISED-1; this REVISED-2 corrects the verification-blocking gap that GO did not catch.
- `bridge/gtkb-project-authorize-spec-linkage-gate-008.md` - the WI-3312 VERIFIED verdict whose gate IP-3 accommodates.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner AUQ added WI-3317 as the 6th WI of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001`.
- 2026-05-15 UTC, S350+: owner directive "Proceed with WI-3316 and WI-3317."

No new owner decision required; REVISED-2 adds a single-helper test fix to make the GO'd verification command achievable.

## Requirement Sufficiency

Existing requirements sufficient. IP-1/IP-2 carry forward unchanged; IP-3 adds no new requirement - it aligns a predating test helper with the already-VERIFIED WI-3312 gate.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (WI-3317), an active member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (regex) + IP-2 (format-spec tests) + IP-3 (test-helper fix) single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-impl-start-gate-format-spec-fix-005.md`; `REVISED:` line prepended. Prior lines (`-004` GO, `-003` REVISED-1, `-002` NO-GO, `-001` NEW) preserved.

## Proposed Scope

IP-1 (redirect alternation -> `(?<![:>-])>{1,2}(?![&])`) and IP-2 (format-spec / arrow false-positive regression tests plus explicit `>>` and no-space `cmd>file` true-positive tests) are **unchanged from REVISED-1** (`bridge/gtkb-impl-start-gate-format-spec-fix-003.md`).

### IP-3 (NEW in REVISED-2): Make the `_seed_project_authorization()` helper WI-3312-compliant

In `platform_tests/scripts/test_implementation_start_gate.py`, the shared helper `_seed_project_authorization()` calls `db.insert_project_authorization(..., status="active")` without `included_spec_ids`. IP-3 updates that single helper to (a) insert an approved specification (e.g. `db.insert_spec(id="SPEC-AUTH-SEED", status="verified", ...)`) and (b) pass `included_spec_ids=["SPEC-AUTH-SEED"]` to the `insert_project_authorization` call, so the fixture authorization satisfies the WI-3312 spec-linkage gate. No assertion logic in the 4 affected tests changes; only the shared fixture helper is made gate-compliant.

## Specification-Derived Verification Plan

Tests in `platform_tests/scripts/test_implementation_start_gate.py`:

| Test case | Command | Expected |
|---|---|---|
| Format-spec `:>` | `python -c "print(f'{n:>2}')"` | NOT mutating |
| Arrow token `->` | `python -c "def f() -> int: return 1"` | NOT mutating |
| Redirect `>` | `cmd > out.txt` | mutating (preserved) |
| Append redirect `>>` | `cmd >> out.txt` | mutating (preserved) |
| Numbered redirect `1>` | `cmd 1> out.txt` | mutating (preserved) |
| Numbered redirect `2>` | `cmd 2> err.txt` | mutating (preserved) |
| Combined redirect `&>` | `cmd &> out.txt` | mutating (preserved) |
| No-space redirect | `cmd>out.txt` | mutating (preserved) |
| Null-sink redirects | `cmd 2>/dev/null`, `2>$null`, `2>NUL` | NOT mutating (preserved) |
| IP-3: the 4 `test_project_authorization_*` tests | (helper made WI-3312-compliant) | all PASS |

Verification command:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -v
```

ALL tests in the file must pass (per GO Condition 3).

## Acceptance Criteria

- IP-1: the redirect alternation is `(?<![:>-])>{1,2}(?![&])`; format-spec/arrow NOT mutating; `>`, `>>`, `1>`, `2>`, `&>`, no-space `cmd>file` remain mutating.
- IP-2: format-spec/arrow false-positive tests and `>>`/no-space true-positive tests land and pass.
- IP-3: `_seed_project_authorization()` is WI-3312-compliant; the 4 `test_project_authorization_*` tests pass.
- The full `platform_tests/scripts/test_implementation_start_gate.py` suite passes.
- Both preflights PASS.

## Non-Blocking Note Carry-Forward (REVISED-1 `-004`)

Codex's `-004` GO noted that fill-character format specs (`:0>2`, `:*>10`, `: >2`) still match because the char before `>` is not `:`. This is intentionally out of scope: a 2-character lookbehind to also exclude fill-char specs would false-NEGATIVE on legitimate redirects after a colon-containing token (e.g. `dir C: > out.txt`, where the two chars before `>` are `: `). The GO'd regex deliberately fixes the common observed defect (`:>`, `->`) without introducing that false-negative risk; the rarer fill-char form is left for a separate proposal if it is observed in practice.

## Risks / Rollback

- Risk: REVISED-2 expands an already-GO'd thread by one helper edit. Mitigation: the edit is exactly one shared fixture helper, required to make the GO's own verification command pass.
- Rollback: revert the single-alternation regex change and the helper edit; IP-2 tests stay as behavior documentation.

## Recommended Commit Type

`fix` - corrects a regex defect plus a predating-test-helper fix to the now-live WI-3312 gate. No new capability surface.
