NEW

# Implementation Report - implementation_start_gate MUTATING_COMMAND_RE Python Format-Spec False-Positive Fix (WI-3317)

bridge_kind: prime_proposal
Document: gtkb-impl-start-gate-format-spec-fix
Version: 007
Responds to: bridge/gtkb-impl-start-gate-format-spec-fix-006.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3317

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

This is the post-implementation report for WI-3317. REVISED-2 was GO'd at `-006`; IP-1, IP-2, and IP-3 are implemented and the verification command passes.

## Claim

The `MUTATING_COMMAND_RE` redirect alternation no longer false-positives on Python format-spec right-alignment (`:>`) or arrow tokens (`->`), while preserving every real shell redirect form. `DELIB-S350`-tracked defect closed; no governing spec status change (the hook regex is its own implementation surface).

## In-Root Placement Evidence

Both target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected behavior; the fix narrows false-positives without weakening true-positive redirect detection.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - the WI-3312 gate IP-3's helper fix accommodates.
- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` - the WI-3313 gate IP-3's amendment-packet fixture fix accommodates.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root paths only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3317 is a tracked work item.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation-start-gate is part of the authorization-enforcement surface.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive; AUQ added WI-3317 as the 6th WI.
- `bridge/gtkb-impl-start-gate-format-spec-fix-002.md` - first NO-GO (regex dropped true positives).
- `bridge/gtkb-impl-start-gate-format-spec-fix-004.md` - GO on REVISED-1.
- `bridge/gtkb-impl-start-gate-format-spec-fix-006.md` - GO on REVISED-2 (helper-scope correction).

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner AUQ added WI-3317 as the 6th WI of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001`.
- 2026-05-15 UTC, S350+: owner directive "Proceed with WI-3316 and WI-3317."

No new owner decision required; the work is within the GO'd `target_paths`.

## Clause Scope Clarification (Not a Bulk Operation)

WI-3317 is not a bulk operation. One work item, an active member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per the owner-approved `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 + IP-2 + IP-3 single thread. No backlog-wide sweep.

## Implemented Changes

IP-1: `scripts/implementation_start_gate.py` - the `MUTATING_COMMAND_RE` redirect alternation changed from `(^|[^>])>{1,2}($|[^&])` to `(?<![:>-])>{1,2}(?![&])`. The negative lookbehind excludes only `:` (format-spec colon), `-` (arrow), and `>` (mid-run), so Python format-spec `:>` and arrow `->` are no longer flagged, while every real redirect (`>`, `>>`, `1>`, `2>`, `&>`, no-space `cmd>file`) and the existing `>&` dup exemption are preserved.

IP-2: `platform_tests/scripts/test_implementation_start_gate.py` - added false-positive regression tests (`:>` format spec, `->` arrow) and explicit true-positive tests for append `>>` and no-space `cmd>out.txt`.

IP-3: `platform_tests/scripts/test_implementation_start_gate.py` - made the project-authorization test fixtures compliant with the now-live governance-chain gates. Two parts: (a) the shared `_seed_project_authorization()` helper now seeds an approved spec and passes `included_spec_ids`, satisfying the WI-3312 spec-linkage gate; (b) `test_project_authorization_load_revalidates_current_spec_exclusions`, whose v2 `update_project_authorization` performs a spec-set amendment, now writes an owner-approved covering formal-artifact-approval packet (via a new `_write_amendment_packet` helper) and cites it in `change_reason`, satisfying the WI-3313 amendment gate.

## Scope Disclosure (IP-3 covered two gates, not one)

REVISED-2's IP-3 text anticipated only the WI-3312 gate (the `_seed_project_authorization` helper). Running the GO-mandated verification command surfaced that `test_project_authorization_load_revalidates_current_spec_exclusions` ALSO trips the WI-3313 amendment gate on its v2 `update_project_authorization` call. That additional fixture-setup fix was applied under the same `-006` GO: GO Implementation Condition #2 explicitly permits fixture-setup changes to the four project-authorization tests ("Do not change the assertion logic ... except as required by the fixture setup"), and GO Condition #3 requires the full file to pass. The assertion logic of all four tests is unchanged; only fixture setup was adjusted. Both target paths remain as approved.

## Specification-Derived Verification

| Behavior | Test |
|---|---|
| Format-spec `:>` not mutating | `test_gate_allows_python_format_spec_right_align` |
| Arrow `->` not mutating | `test_gate_allows_python_arrow_token` |
| Redirect `>` mutating | `test_gate_blocks_unnumbered_redirect_to_file` |
| Append `>>` mutating | `test_gate_blocks_append_redirect_to_file` |
| Numbered `1>` mutating | `test_gate_blocks_stdout_numbered_redirect_to_file` |
| Numbered `2>` mutating | `test_gate_blocks_stderr_numbered_redirect_to_real_file` |
| Combined `&>` mutating | `test_gate_blocks_combined_redirect_to_file` |
| No-space `cmd>file` mutating | `test_gate_blocks_no_space_redirect_to_file` |
| Null-sink redirects exempt | `test_gate_allows_stderr_redirect_to_dev_null`, `..._powershell_null`, `..._windows_nul` |
| IP-3: project-authorization fixtures gate-compliant | `test_project_authorization_metadata_is_carried_in_packet`, `..._load_revalidates_current_spec_exclusions`, `..._does_not_broaden_target_scope`, `..._requires_work_item_membership_or_inclusion` |

Command executed and observed result:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q
```

Result: **40 passed**. The 4 `test_project_authorization_*` tests that failed at REVISED-2 filing time (WI-3312 gate) and the additional WI-3313-gate failure all pass after IP-3; the new IP-2 false-positive/true-positive tests pass.

## Acceptance Criteria Check

- IP-1: redirect alternation is `(?<![:>-])>{1,2}(?![&])`; format-spec/arrow NOT mutating; all real redirect forms mutating. PASS.
- IP-2: false-positive + true-positive regression tests land and pass. PASS.
- IP-3: `_seed_project_authorization()` WI-3312-compliant; the spec-exclusion test WI-3313-compliant; the 4 `test_project_authorization_*` tests pass. PASS.
- Full `test_implementation_start_gate.py` suite passes (40 passed). PASS.
- Changes scoped to the two approved target paths. PASS.
- Both preflights PASS (recorded in the REVISED-2 GO at `-006`).

## Non-Blocking Note Carry-Forward

Per the `-004`/`-006` GO non-blocking note, fill-character format specs (`:0>2`, `:*>10`, `: >2`) still match because the char before `>` is not `:`/`-`/`>`. This is deliberately out of scope: a 2-character lookbehind to also exclude them would false-negative on legitimate redirects after a colon-containing token (e.g. `dir C: > out.txt`). The GO'd regex fixes the common observed defect without that risk; the rarer fill-char form is left for a separate proposal if observed.

## Risks / Rollback

- Risk: an exotic redirect form outside the test matrix. Mitigation: the new regex only EXCLUDES `:`/`-`/`>`-preceded operators; every other prefix still matches, so the change strictly shrinks the false-positive set.
- Rollback: revert the single-alternation regex change and the test-fixture edits.

## Recommended Commit Type

`fix` - corrects a defect in an existing regex plus predating-test-fixture fixes to the now-live WI-3312 and WI-3313 governance gates. No new capability surface.
