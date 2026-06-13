NEW

# Advisory Grilling Gate Lint - Post-Implementation Report

bridge_kind: implementation_report
Document: gtkb-lo-advisory-owner-grilling-gate-slice3-lint
Version: 003
Responds to: bridge/gtkb-lo-advisory-owner-grilling-gate-slice3-lint-002.md
GO-Verdict: bridge/gtkb-lo-advisory-owner-grilling-gate-slice3-lint-002.md
Author: Claude Prime Builder
Date: 2026-06-13T07:40:00Z

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 4ce5ba60-40de-4937-a1c5-f2bc97b00475
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; Prime Builder; fast mode

Project Authorization: PAUTH-PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001-LO-ADVISORY-OWNER-GRILLING-GATE-IMPLEMENTATION
Project: PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001
Work Item: WI-3446

target_paths: ["scripts/advisory_grilling_gate_lint.py", "platform_tests/scripts/test_advisory_grilling_gate_lint.py", ".claude/settings.json", ".codex/hooks.json"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Recommended Commit Type

`feat`: adds a new deterministic warning-phase lint surface plus dual-harness Stop-hook registration and a focused test suite. No prior behavior is changed; the lint is fail-open.

---

## Implementation Claim

Slice 3 of the LO Advisory Owner-Grilling Gate project (`WI-3446`) is implemented as proposed in `bridge/gtkb-lo-advisory-owner-grilling-gate-slice3-lint-001.md` (GO at `-002`):

1. `scripts/advisory_grilling_gate_lint.py` was created. It deterministically implements the `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` contract: advisory-shape detection (filename + `Mode: advisory[ report]` header in the first 20 lines + exactly one of `adopt`/`adapt`/`reject`/`defer`/`monitor` declared inside a `## Classification` / `## Recommended Prime Builder Disposition` / `## Disposition` section), gate-presence warning for `adopt`/`adapt`, gate-content warning (`< 3` enumerations), and the `Grilling-gate waiver: <reason>` suppression path with append-only logging to `.gtkb-state/advisory-grilling-gate/waivers.jsonl`.
2. The lint is **Phase 1 (warning-only) and fail-open**: it never returns a blocking exit code, and any internal error degrades to a clean pass. Phase 2 (blocking) is explicitly out of scope per the DCL's two-phase progression.
3. The script is registered as a warning-phase `Stop` hook for **both harnesses**: `.claude/settings.json` (Claude, `$CLAUDE_PROJECT_DIR` form) and `.codex/hooks.json` (Codex, absolute-path form), each invoking `--stop-hook`.
4. `platform_tests/scripts/test_advisory_grilling_gate_lint.py` was created with 31 tests (via `parametrize`) covering all five classifications, adopt/adapt pass/fail, non-advisory false positives, the waiver path, ledger logging, and CLI/Stop-hook fail-open behavior.

Implementation-start authorization packet: `sha256:f95a4322c09a5b7900b6880619f443d1f04e93deebcdd50011b5adc504a0a7d1`, derived from the live `GO` at `-002`, active PAUTH `PAUTH-PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001-LO-ADVISORY-OWNER-GRILLING-GATE-IMPLEMENTATION` (`WI-3446`). All four edited paths are within the authorized `target_path_globs`.

## Specification Links

(Carried forward from the GO'd proposal `-001`.)

- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` - the owner-grilling gate principle for `adopt`/`adapt` advisories.
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` - the deterministic machine-checkable contract this slice implements.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the work proceeded through bridge `NEW` -> `GO` -> implementation-start -> this report; `bridge/INDEX.md` remains canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - links carried forward from the proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - header carries PAUTH, project, work item, inline JSON `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping plus executed-test evidence below.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation bounded by the active PAUTH.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the PAUTH allows `script_create`, `hook_config_registration`, `test_create`; this report mutates only those classes.
- `GOV-STANDING-BACKLOG-001` - `WI-3446` is the canonical Slice 3 backlog item.

## Prior Deliberations

- `DELIB-S364-LO-ADVISORY-GRILLING-GATE-PROJECT-AUTH` - owner-authorized the project and PAUTH covering all three slices, including `WI-3446`.
- `INTAKE-e226b05a` - original requirement intake for the LO Advisory Owner-Grilling Gate.
- `DELIB-20263159` - current-session owner directive/pacing record (continue PB-actionable bridge/backlog work with a 3-minute inter-project pause); included for session context.

## Owner Decisions / Input

No new owner decision was required. The governing owner authorization already exists in `DELIB-S364-LO-ADVISORY-GRILLING-GATE-PROJECT-AUTH`, and the active PAUTH includes `WI-3446`, `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`, and `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001`. The current interactive-session owner directive (AskUserQuestion answer "Implement fresh GO items now", 2026-06-13) authorized continuing implementation of PB-actionable `GO` items through the bridge protocol.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` defines the policy, `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` defines the machine-checkable contract, and `WI-3446` defines the Slice 3 implementation surface (script + warning-phase hook registration + tests). No new or revised requirement was needed.

## Spec-to-Test Mapping

| Specification / contract clause | Tests / verification |
| --- | --- |
| `DCL-...` advisory-shape (filename + Mode header + single classification) | `test_mode_header_report_variant_detected`, `test_mode_header_short_variant_detected`, `test_mode_header_case_insensitive`, `test_mode_header_only_in_first_20_lines`, `test_non_advisory_no_mode_header_is_not_shaped`, `test_wrong_filename_is_not_shaped`, `test_ambiguous_classification_is_not_shaped`, `test_each_classification_extracted` (5), `test_classification_under_disposition_heading_variant` |
| `DCL-...` gate-presence (adopt/adapt) + `GOV-...` adopt/adapt require gate | `test_gate_required_missing_warns` (adopt, adapt) |
| `DCL-...` gate-content (>= 3 enumerations) | `test_gate_named_subsections_passes` (adopt, adapt), `test_gate_numbered_list_passes`, `test_gate_present_but_insufficient_content_warns`, `test_count_gate_enumerations_complete` |
| `GOV-...` reject/defer/monitor need no gate | `test_terminal_classifications_need_no_gate` (reject, defer, monitor) |
| `DCL-...` waiver suppression + ledger | `test_waiver_suppresses_gate_warning`, `test_waiver_recorded_to_ledger` |
| `DCL-...` Phase 1 warning-only / fail-open | `test_main_returns_zero_even_with_warnings`, `test_main_json_output_reports_warning`, `test_stop_hook_emits_empty_json_and_exits_zero`, `test_stop_hook_fail_open_on_bad_project_root`, `test_lint_file_unreadable_is_fail_open`, `test_discover_finds_dropbox_files` |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | impl-start packet `sha256:f95a4322...`; all `target_paths` within authorized globs |
| Code quality | `ruff check` + `ruff format --check` (below) |

## Verification Evidence (executed)

- `python -m pytest platform_tests/scripts/test_advisory_grilling_gate_lint.py -q` -> **31 passed** in ~1.1s.
- `python -m ruff check scripts/advisory_grilling_gate_lint.py platform_tests/scripts/test_advisory_grilling_gate_lint.py` -> **All checks passed!**
- `python -m ruff format --check scripts/advisory_grilling_gate_lint.py platform_tests/scripts/test_advisory_grilling_gate_lint.py` -> **2 files already formatted**.
- Stop-hook smoke (real dropbox): `'{}' | python scripts/advisory_grilling_gate_lint.py --stop-hook` -> stdout `{}`, **exit 0** (fail-open, non-blocking).
- Real-dropbox scan: `python scripts/advisory_grilling_gate_lint.py --json` -> `advisory_files=0, warnings=0, phase=warning` (the 100+ historical `INSIGHTS-*.md` files correctly skipped: they predate the `Mode:` header convention).
- JSON validity: both `.claude/settings.json` and `.codex/hooks.json` parse cleanly after the Stop-hook registration edits.

## DCL `gt assert` Diagnostic (expected RED; NOT a lint defect)

`python -m groundtruth_kb.cli assert --spec DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` reports **0/4 passed (4 failed)**:

```
[FAIL] Detects LO advisory-shape files via Mode header: Found 0 match(es) across 778 file(s), need >= 1
[FAIL] Detects classification declaration section: Found 0 match(es) across 778 file(s), need >= 1
[FAIL] Blocking: gate heading required when classification is adopt or adapt: Found 0 match(es) across 778 file(s), need >= 1
[FAIL] Warning: gate section must contain at least 3 enumerations ...
```

This is the limitation explicitly flagged in the GO'd proposal (`-001`, "Important limitation for LO review" and "Risk / Rollback"). The DCL's four assertions are **shallow repository-content greps over the live `INSIGHTS-*.md` corpus** that require at least one *real* compliant advisory report to exist. No advisory authored in the new `Mode: advisory report` format exists yet, so they find 0 matches. **These assertions verify the existence of a compliant advisory, not the correctness of the lint script.** The lint's behavioral correctness is proven by the 31-test suite above. Making the `gt assert` definitions green is out of scope for this slice and would require either an authentic compliant advisory fixture/report or a separate formal-artifact bridge to amend the DCL assertions to target the lint surface.

## Files Changed

- `scripts/advisory_grilling_gate_lint.py` (new, ~290 lines).
- `platform_tests/scripts/test_advisory_grilling_gate_lint.py` (new, 31 tests).
- `.claude/settings.json` (one Stop-hook entry appended).
- `.codex/hooks.json` (one Stop-hook entry appended).

## Risk / Rollback

Risk is low. The lint is warning-phase and fail-open; a defect surfaces as a stderr warning and never blocks a write or a turn. Stop-hook additions are append-only and isolated. Rollback is a single revert of the four target files. The waiver ledger is append-only runtime evidence under `.gtkb-state/` and is not canonical project state.

## Bridge Filing (INDEX-Canonical)

This report is filed as `bridge/gtkb-lo-advisory-owner-grilling-gate-slice3-lint-003.md` with a `NEW` entry inserted at the top of the document's version list in `bridge/INDEX.md` (append-only; no prior version rewritten). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
