NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S378-interactive-session-role-override-slice-8-new
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3478
target_paths: ["scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py"]

# GT-KB Interactive Session Role Override - Slice 8 - Parity-Check Resolution-Table Contract Enforcement

bridge_kind: implementation_proposal

Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
Version: 001 (NEW; first Slice-8 proposal)
Date: 2026-05-30 UTC

## Summary

Upgrade `scripts/check_codex_hook_parity.py` from its current
presence/registration discipline to a resolution-table-contract enforcement
surface that compares the Claude and Codex SessionStart dispatchers
(`.claude/hooks/session_start_dispatch.py` and
`.codex/gtkb-hooks/session_start_dispatch.py`) for byte-equivalent
resolution-table primitives. Closes the last piece of the scoping `-002` F1
finding (Codex hook surface coverage) by giving Future-Drift a mechanical
gate: if either dispatcher's resolution table drifts from the other's, the
parity check fails CI rather than silently allowing role-routing divergence.

## Premise Verification (against live code; this section is the GO scope anchor)

The owner's session prompt explicitly requested premise verification because
Slices 5 and 7 both shipped with inaccurate scoping premises. Concrete reads:

### State of `scripts/check_codex_hook_parity.py` today

The current `check_project` function (lines 236-592) enforces:

- File-existence assertions for nine required paths (lines 250-262).
- Codex `[features].codex_hooks = true` (line 271).
- Claude PreToolUse formal-artifact-approval registration (lines 274-276).
- Claude SessionStart: either direct invocation of
  `scripts/session_self_initialization.py` OR dispatcher under
  `.claude/hooks/session_start_dispatch.py` (lines 278-296).
- Claude SessionStart dispatcher source must contain four substring
  tokens: `session_self_initialization.py`,
  `--emit-startup-service-payload`, `--fast-hook`, harness identifier
  (lines 298-312).
- Claude Stop hook lifecycle terms (lines 331-350).
- Codex PreToolUse formal-artifact-approval group structure + wrapper
  presence (lines 195-205, 352-375).
- Codex bridge-compliance hooks (PreToolUse + PostToolUse) (lines 377-453).
- Codex workstream-focus hooks (PreToolUse + UserPromptSubmit) (lines 455-499).
- Codex SessionStart hook dispatcher source must contain ~28 substring
  tokens (lines 135-192, `_start_wrapper_errors`).
- Codex Stop hook does NOT register wrap-up + lifecycle wrapper
  assertions (lines 525-590).

What the check does NOT enforce today:

- That `_SESSION_ROLE_MARKER_NAME = "active-session-role.json"` appears in
  BOTH dispatchers AND in `scripts/session_role_resolution.py`
  AND in `scripts/workstream_focus.py` (the Slice 2 writer).
- That both dispatchers contain the `StartupDecision` enum with the same
  five canonical members
  (`NORMAL_STARTUP`, `DISPATCH_AUTHORIZED`, `SPOOF_FALLBACK`,
  `LEGACY_FALLBACK`, `STRICT_DROP`).
- That both dispatchers contain `_invalidate_session_role_marker` and
  call it in `main()`.
- That both dispatchers contain the canonical init-keyword regex
  `^::init gtkb (pb|lo)$`.
- That both dispatchers contain identical `_LABEL_TO_CANONICAL_MODE` and
  `_MODE_TO_ROLE_PROFILE` dictionaries.
- That both dispatchers contain `_bridge_dispatch_keyword_check` and
  reference the 5-row decision table.
- That both dispatchers contain `_audit_log_misdirected_dispatch` with
  the `"misdirected_dispatch_strict_drop"` audit-record kind.

### State of the two SessionStart dispatchers today

Cross-comparing `.claude/hooks/session_start_dispatch.py` (657 lines) and
`.codex/gtkb-hooks/session_start_dispatch.py` (651 lines):

- Lines 42-53 (Claude) and lines 39-53 (Codex) define the canonical
  init-keyword regex, the run-id env-var name, the dispatch-keyword
  env-var name, the label-to-mode map, and the mode-to-role-profile map
  byte-identically.
- Lines 66-78 (Claude) and lines 60-72 (Codex) define the
  `StartupDecision` enum byte-identically.
- Lines 129-145 (Claude) and lines 123-138 (Codex) define
  `_SESSION_ROLE_MARKER_NAME`, `_session_role_marker_path`, and
  `_invalidate_session_role_marker` byte-identically.
- Lines 305-422 (Claude) and lines 299-416 (Codex) define
  `_audit_log_misdirected_dispatch` and `_bridge_dispatch_keyword_check`
  byte-identically.

The only intentional differences between the two dispatchers (per code
comments) are: `HARNESS_NAME` (`"claude"` vs `"codex"`), `OUT_DIR`
(`.claude/hooks` vs `.codex/gtkb-hooks`), and the dispatcher-specific
parity-marker comment line.

### State of the resolver

`scripts/session_role_resolution.py` (Slice 4; Codex GO at
`bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-002.md`,
VERIFIED at `-004`) is the SINGLE deterministic implementation of the
interactive rows of `DCL-SESSION-ROLE-RESOLUTION-001`. It exposes
`resolve_interactive_session_role(...) -> (role_profile, source)` with
five canonical `source` values. The dispatchers own the headless rows
(env-var-present case). The marker constant
`_SESSION_ROLE_MARKER_NAME = "active-session-role.json"` is shared with
both dispatchers (line 53 of the resolver, with the parity expectation
documented in lines 49-52).

### Scoping -004 GO scope anchor

`bridge/gtkb-interactive-session-role-override-scoping-004.md` (Codex GO,
2026-05-29):

- F1 explicitly resolved: "The revised proposal adds
  `.codex/gtkb-hooks/session_start_dispatch.py` to Slices 1 and 3,
  adds `scripts/check_codex_hook_parity.py` as Slice 8" (line 117).
- Slice 8 charter confirmed: "Current `scripts/check_codex_hook_parity.py`
  passes on the current codebase, and the proposal's Slice 8 explicitly
  upgrades that check to enforce the new resolution-table contract after
  implementation." (line 124).
- Owner-AUQ-backed: the scoping carried owner-decision evidence for the
  six S371 AskUserQuestion decisions; Slice 8 inherits that approval
  envelope through `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`
  v3.

### In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
`.claude/rules/project-root-boundary.md`: both target files are in-root.
No `applications/<name>/` paths, no Agent Red live dependency, no
out-of-root path. The script touches only in-root sources (the two
dispatchers under `.claude/hooks/` and `.codex/gtkb-hooks/`, the resolver
under `scripts/`, and the writer under `scripts/`).

## Plan

### `scripts/check_codex_hook_parity.py` (modify)

Add a new top-level helper `_resolution_table_parity_errors(project_root)`
called from `check_project` after the existing assertions. The helper
performs eight assertion classes:

1. **Marker constant parity (assertion 1).** Read
   `.claude/hooks/session_start_dispatch.py`,
   `.codex/gtkb-hooks/session_start_dispatch.py`,
   `scripts/session_role_resolution.py`, and
   `scripts/workstream_focus.py`. Assert each contains the exact literal
   `_SESSION_ROLE_MARKER_NAME = "active-session-role.json"`. Report a
   distinct error per missing site.

2. **StartupDecision enum parity (assertion 2).** Assert both dispatchers
   contain a `class StartupDecision(Enum):` declaration AND the five
   value lines (`NORMAL_STARTUP = "normal_startup"` etc.) byte-equal
   between the two dispatchers. Report missing-enum errors per
   dispatcher and a single mismatch error if values diverge.

3. **Canonical init-keyword regex parity (assertion 3).** Assert both
   dispatchers contain the exact line
   `_CANONICAL_KEYWORD_RE = re.compile(r"^::init gtkb (pb|lo)$")`.

4. **Label and profile map parity (assertion 4).** Assert both
   dispatchers contain identical `_LABEL_TO_CANONICAL_MODE` and
   `_MODE_TO_ROLE_PROFILE` dictionary literals (compared as
   normalized text after `ast.parse`).

5. **Marker invalidation parity (assertion 5).** Assert both
   dispatchers contain `_invalidate_session_role_marker` defined AND
   called from `main()` before the IP-4 dispatch fork. Assert
   `_session_role_marker_path` resolves to
   `.claude/session/active-session-role.json` in both dispatchers
   (the marker location is harness-name-agnostic per Slice 3 VERIFIED).

6. **Behavior-table parity (assertion 6).** Assert both dispatchers
   contain `_bridge_dispatch_keyword_check` AND a comment block matching
   the 5-row behavior table header
   (`env-var`, `keyword`, `mode-in-role-set`, `Decision`, `Effect`).
   Assert the function body contains the 5 decision-return statements
   (`NORMAL_STARTUP`, `SPOOF_FALLBACK`, `LEGACY_FALLBACK`,
   `DISPATCH_AUTHORIZED`, `STRICT_DROP`).

7. **Audit-log parity (assertion 7).** Assert both dispatchers contain
   `_audit_log_misdirected_dispatch` AND the audit-record kind literal
   `"misdirected_dispatch_strict_drop"`. Assert both write to
   `.gtkb-state/bridge-poller/dispatch-failures.jsonl`.

8. **Intentional-difference catalogue (assertion 8).** Assert each
   dispatcher contains its OWN harness name (`HARNESS_NAME = "claude"`
   in Claude; `HARNESS_NAME = "codex"` in Codex) and only its own
   `OUT_DIR` path token (`.claude/hooks` in Claude; `.codex/gtkb-hooks`
   in Codex). This guard prevents accidental copy-paste of the harness
   name during a future drift event.

Each assertion class extends the existing `errors` list. The existing
`main()` printer prints them under the same `Codex hook parity: FAIL`
banner so CI / doctor consumers see them in the same channel.

The implementation uses `pathlib.Path.read_text` + `in` substring checks
(matching the existing helpers' style); the dict-literal comparison uses
`ast.parse` + `ast.dump` for normalization. No new external dependencies.

### `platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py` (new)

A new test module covering the eight assertion classes via the
mutate-and-test pattern. Module-level fixture stages a copy of the
canonical repo state in a `tmp_path`-rooted minimal project skeleton; per
test, the fixture mutates one specific resolution-table primitive and
asserts that `check_project` returns a list containing the specific error
for that mutation.

Planned tests (N=14 minimum):

| # | Test                                                                  | Behavior covered                             |
|---|-----------------------------------------------------------------------|----------------------------------------------|
| 1 | `test_resolution_table_clean_state_passes`                            | baseline: no resolution-table errors today    |
| 2 | `test_marker_constant_missing_from_claude_dispatcher`                 | assertion 1, Claude site                      |
| 3 | `test_marker_constant_missing_from_codex_dispatcher`                  | assertion 1, Codex site                       |
| 4 | `test_marker_constant_missing_from_resolver`                          | assertion 1, resolver site                    |
| 5 | `test_startup_decision_enum_missing_member_in_claude`                 | assertion 2, missing member                   |
| 6 | `test_startup_decision_enum_value_diverges_between_dispatchers`       | assertion 2, value mismatch                   |
| 7 | `test_canonical_init_keyword_regex_diverges`                          | assertion 3                                   |
| 8 | `test_label_to_canonical_mode_dict_diverges`                          | assertion 4                                   |
| 9 | `test_invalidate_marker_not_called_in_main`                           | assertion 5, missing call                     |
| 10 | `test_bridge_dispatch_keyword_check_decision_missing`                | assertion 6, missing branch                   |
| 11 | `test_audit_log_kind_literal_missing`                                | assertion 7                                   |
| 12 | `test_claude_harness_name_appears_in_codex_dispatcher`                | assertion 8, intentional-difference guard     |
| 13 | `test_codex_out_dir_appears_in_claude_dispatcher`                     | assertion 8, intentional-difference guard     |
| 14 | `test_clean_state_still_passes_after_test_module_addition`            | regression: no false-positive on this PR      |

The test module uses the repo venv (`groundtruth-kb/.venv/Scripts/`) per
session feedback for `ruff format --check` + `ruff check` and pins
`pytest --basetemp E:\GT-KB\.pytest-tmp\slice8-NNN`.

## Acceptance Criteria

1. `python scripts/check_codex_hook_parity.py` exits 0 on the current
   codebase (no false positives introduced).
2. The new test module passes (14/14 minimum) with the repo venv.
3. Each new error message is deterministic (no timestamps, no path
   ordering jitter).
4. The eight assertion classes ALL detect at least one mutation each in
   the new tests (proves the assertion is load-bearing, not a dead
   `errors.extend([])`).
5. The check_project function's error list grows by at most ~24 lines of
   new error strings, keeping the existing call sites stable.
6. The new test module follows the same style as
   `platform_tests/scripts/test_doctor_session_role_marker.py` (the
   recent peer test from Slice 7).

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` v1 - the resolution table whose
  byte-equivalent enforcement Slice 8 elevates from convention to
  mechanical assertion.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 - the parent decision
  authorizing the cross-dispatcher symmetry being enforced.
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 - the session-stated role surface
  whose dispatch fidelity the assertions protect.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v1 - the init-keyword regex
  whose two-site parity is asserted by assertion 3.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v1 - the receiver-side
  enforcement contract whose set-membership and audit-log shapes are
  asserted by assertions 6 and 7.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` - the parent governance
  parity authority that `check_codex_hook_parity.py` already serves
  (line 387 of the script). This slice extends its enforcement surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root boundary affirmed
  for both target files.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed at `-001`;
  `bridge/INDEX.md` will be updated with `Document:` + `NEW:` lines.
  No prior bridge version is deleted or rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - linkage
  table above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test
  mapping is the table under "`test_check_codex_hook_parity_resolution_table.py`
  (new)" above; the spec-derived verification gate is satisfied by
  the eight assertion classes mapping to the eight blocks of the
  resolution-table contract.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project triple
  in header.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`,
  `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - covered by
  `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active v3;
  covers WI-3478).
- `GOV-ARTIFACT-APPROVAL-001` - this slice inserts no canonical
  artifact (no MemBase spec/GOV/ADR/DCL/PB insert; no
  `.claude/rules/*.md` mutation; the script is non-canonical helper
  code). No formal-artifact-approval packet required.
- `GOV-STANDING-BACKLOG-001` - single feature slice; not a bulk
  operation. See Clause Scope Clarification below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory),
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory),
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `bridge/gtkb-interactive-session-role-override-scoping-004.md`
  (parent scoping GO; the Slice 8 charter source).
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md`
  (Slice 1 VERIFIED; Codex SessionStart dispatcher landed here).
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md`
  (Slice 3 VERIFIED; the marker-invalidation primitive both dispatchers
  share).
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md`
  (Slice 4 VERIFIED; the resolver and its single-source-of-truth
  expectation).
- `bridge/gtkb-canonical-init-keyword-syntax-001-008.md` (IP-4 GO that
  introduced the StartupDecision enum and the dispatch-keyword
  contract).

## Prior Deliberations

- `bridge/gtkb-interactive-session-role-override-scoping-004.md` -
  parent scoping GO; line 124 explicitly defines this slice's charter.
- `bridge/gtkb-interactive-session-role-override-scoping-002.md` -
  the original NO-GO whose F1 finding required Codex hook surface
  coverage; Slice 8 is the final piece of that F1 closure.
- `bridge/gtkb-canonical-init-keyword-syntax-001-007.md` and `-008.md` -
  the IP-4 thread that introduced the canonical keyword regex,
  StartupDecision enum, and `_bridge_dispatch_keyword_check`
  decision-table contract.
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md` -
  Slice 1 VERIFIED; introduced the Codex SessionStart dispatcher
  whose parity with the Claude side is the subject of this slice.
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md` -
  Slice 3 VERIFIED; established the marker-invalidation primitive
  parity that assertion 5 enforces.
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md` -
  Slice 4 VERIFIED; established the resolver as the single
  authoritative source for interactive resolution, which Slice 8's
  assertion 1 extends to the marker constant parity.
- `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-006.md` -
  Slice 7 VERIFIED (just committed at `71f81d96`); established the
  pattern of marker-related assertions that this slice generalizes
  to the dispatch surface.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-014.md` -
  proposal-cited prior bridge chain for role-set wire form (a
  resolution input the dispatchers consume).

## Owner Decisions / Input

This slice operates within the approval envelope established by these
durable owner-decision records. No new AskUserQuestion is required for
this proposal; the implementation cycle follows the standard
propose -> Codex GO -> implement -> post-impl -> VERIFIED pattern
authorized by the parent scoping.

- `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v3 (active)
  - covers `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE` including
  `WI-3478` (this slice's work item). The PAUTH satisfies the
  owner-approval evidence layer for Slices 1-10 under the project.
- `DELIB-2507` - the original owner directive that mandated interactive
  `::init gtkb (pb|lo)` overrides the durable role for interactive
  surfaces while keeping durable as the headless-dispatch authority.
  Slice 8 protects this contract at the dispatch-routing layer.
- S371 owner AskUserQuestion decisions captured in the scoping
  thread - six AUQ answers establishing the 10-slice decomposition,
  artifact framing (ADR + DCL + GOV), and the role-vs-session split.
  Per the scoping `-004` review-asks `1-6`, all six are confirmed.
- Session-S378 owner AskUserQuestion - this session's owner AUQ
  approved committing Slices 5-7 as a single bundled commit (now
  landed at `71f81d96`). This AUQ does not directly authorize Slice
  8 work but confirms the project is progressing through the
  pre-bound WI sequence the owner set in the session prompt.

No owner AUQ is required to file this NEW proposal. The proposal
itself is the bridge protocol's authoring step; Codex GO / NO-GO is
the next event in the cycle and does not require fresh owner input
either (PAUTH covers it).

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` bulk-ops clause-scope clarification:
this slice modifies one non-canonical script (the parity-check helper)
and adds one new test module. No backlog bulk operation, no
`work_items` insert/update/retire/supersede, no project create/retire,
no authorization change, no inventory artifact, no review-packet, no
formal-artifact-approval packet, no MemBase mutation. Evidence pattern
tokens: single script upgrade, one new test module, no bulk, no
backlog mutation, no canonical artifact insert.

## Spec-Derived Verification (Plan)

### Spec-to-assertion-to-test mapping

| Spec / behavior                                                            | Assertion       | Tests          |
|----------------------------------------------------------------------------|-----------------|----------------|
| Marker constant single-value invariant (`DCL-SESSION-ROLE-RESOLUTION-001`) | 1               | 2, 3, 4        |
| StartupDecision 5-vocabulary closed set (IP-4 SPEC + DCL)                  | 2               | 5, 6           |
| Init-keyword regex single-form contract (`SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`) | 3       | 7              |
| Label-to-canonical-mode mapping closed dict (DCL receiver clause)          | 4               | 8              |
| Marker-invalidation pre-dispatch contract (Slice 3 spec)                   | 5               | 9              |
| Decision-table 5-row behavior contract (DCL receiver clause)               | 6               | 10             |
| Audit-log misdirected-drop record-kind (PB-INCIDENT-S321-DAEMON-...-001 v2)| 7               | 11             |
| Intentional-difference guard (cross-dispatcher copy-paste prevention)      | 8               | 12, 13         |
| Baseline + regression cleanliness                                          | n/a             | 1, 14          |

### Commands the post-impl report will execute (repo venv; explicit basetemp)

```text
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/check_codex_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py

groundtruth-kb/.venv/Scripts/ruff.exe check scripts/check_codex_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py -q --basetemp E:\GT-KB\.pytest-tmp\slice8-impl-basetemp

# Regression: the upgrade must not introduce false positives on the current codebase.
groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py
```

## Risk and Rollback

### Risk classes

- **R1: false positive on current codebase.** Mitigation: test 1 + test
  14 establish the no-regression baseline; the post-impl report will
  re-run the standalone parity check after the upgrade to confirm exit 0.
- **R2: assertion drift coverage gap.** Mitigation: assertion 8's
  intentional-difference guard prevents the copy-paste-of-harness-name
  drift class (a Codex dispatcher accidentally inheriting Claude's
  `HARNESS_NAME = "claude"` would silently misroute every Codex
  SessionStart).
- **R3: brittle string-matching.** Mitigation: assertion 4 uses
  `ast.parse` + `ast.dump` to normalize the dict-literal comparison
  rather than raw-string-equals (which would break on a comment edit
  or whitespace change). The other assertions check substring or
  byte-equal literal lines that are stable per the dispatcher
  cross-comparison evidence in the Premise Verification section.

### Rollback

If the upgrade is found defective after implementation, rollback is one
commit revert of the (single) implementation commit. The current
parity-check behavior is preserved verbatim; the assertions are
additive. No data, state, or canonical artifact is affected by the
change or its rollback.

## Recommended Commit Type

`feat` - the slice adds a new mechanical-assertion surface
(resolution-table contract enforcement) that did not exist before.
Not `fix` (no pre-existing broken behavior was repaired; the existing
parity check was correct for its scoped concerns) and not `test`
alone (the test module accompanies a source upgrade).

## target_paths Note

The machine-readable `target_paths` metadata is the inline-JSON header
line. The two files match the bridge-proposal-target convention exactly.
No KB/MemBase mutation occurs (the script is helper code; the test
module exercises it via `tmp_path` skeletons; no `groundtruth.db`
write occurs anywhere in the new code paths).
