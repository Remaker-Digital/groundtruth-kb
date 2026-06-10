REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S378-interactive-session-role-override-slice-8-revised
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3478
target_paths: ["scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py"]

# GT-KB Interactive Session Role Override - Slice 8 - Parity-Check Resolution-Table Contract Enforcement (REVISED addressing NO-GO -002 F1 + F2)

bridge_kind: prime_proposal

Document: gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table
Version: 003 (REVISED; supersedes -001 after Codex NO-GO -002 F1 + F2)
Date: 2026-05-30 UTC

## Response to NO-GO -002 (F1 + F2 Resolution)

Codex NO-GO -002 raised two P1 findings against `-001`. Both are real;
both are addressed in this REVISED.

### F1 resolution (Mandatory Requirement Sufficiency subsection)

Added the `## Requirement Sufficiency` subsection below with the
operative state `Existing requirements sufficient` and explicit
citations to the governing requirements per
`.claude/rules/file-bridge-protocol.md` lines 39-48 and
`.claude/rules/codex-review-gate.md` lines 53-57.

### F2 resolution (Charter alignment + as-shipped contract)

Codex offered two paths in F2:

> If keeping `SPOOF_FALLBACK` is now the intended shipped equivalent because
> interactive owner-typed keywords are handled by `scripts/workstream_focus.py`,
> cite the exact successor bridge evidence that supersedes the parent
> scoping wording and make the parity assertion test that equivalent
> contract directly. If no successor evidence exists, revise the plan to
> enforce the parent `INTERACTIVE_OVERRIDE_AUTHORIZED` requirement.

This REVISED takes the first path. Successor evidence:

**The as-shipped architecture** (post-Slices 1-7) split the
interactive-override mechanism in two pieces, both VERIFIED:

1. **SessionStart side (both dispatchers):** keeps the IP-4 five-value
   enum vocabulary `{NORMAL_STARTUP, DISPATCH_AUTHORIZED, SPOOF_FALLBACK,
   LEGACY_FALLBACK, STRICT_DROP}`. `SPOOF_FALLBACK` is intentionally
   preserved as the defense-in-depth path for a keyword-without-env-var
   case (an unverified owner-typed keyword at SessionStart cannot safely
   bypass normal startup; spoof defense is the right semantic).
2. **UserPromptSubmit side:** `scripts/workstream_focus.py` (Slice 2)
   is the interactive-override entry point. When the owner types
   `::init gtkb (pb|lo)` as the first prompt of an interactive session,
   the init-keyword matcher writes the ephemeral session-state role
   marker at `.claude/session/active-session-role.json`, and the
   role-keyed startup-disclosure cache is rendered from whichever of
   `last-user-visible-startup-pb.md` or `last-user-visible-startup-lo.md`
   matches the keyword. **Both caches are generated unconditionally at
   SessionStart time** by the post-Slice-1 cache-writer fix, so the
   keyword-keyed cache lookup always succeeds regardless of this
   harness's durable role set.

**Successor bridge evidence** (the bridge threads whose GO/VERIFIED
verdicts establish the as-shipped contract):

- `bridge/gtkb-canonical-init-keyword-syntax-001-005.md` (IP-4; Codex
  GO at `-006`; subsequent VERIFIED at `-009`) - the IP-4 enum cleanup
  formally defines the five-value `StartupDecision` vocabulary as the
  receiver-side decision-table contract. `INTERACTIVE_OVERRIDE_AUTHORIZED`
  was NOT shipped; the parent scoping-003 line 344 term is superseded
  by IP-4's enum cleanup. Reference: `-005.md` line 21 ("hook decision
  now uses an explicit `StartupDecision` enum with five distinct values
  (`NORMAL_STARTUP`, `DISPATCH_AUTHORIZED`, `SPOOF_FALLBACK`,
  `LEGACY_FALLBACK`, `STRICT_DROP`). No more boolean collapsing of
  'fall through' and 'drop' semantics.") and `-005.md` line 326 ("Codex
  confirms IP-4 enum cleanup: `StartupDecision` enum has five distinct
  values; no boolean collapsing of `SPOOF_FALLBACK`/`LEGACY_FALLBACK`/
  `STRICT_DROP`.").
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md`
  (Slice 1 VERIFIED) - landed the cache-writer fix in BOTH dispatchers.
  Per scoping-003 line 71, the pre-Slice-1 cache-writer iterated
  `_resolve_own_role_set()` and would fail to write the alternate-role
  cache. The post-Slice-1 shape (live today) iterates
  `_MODE_TO_ROLE_PROFILE` and skips `primary_mode`, writing BOTH
  `-pb.md` and `-lo.md` caches unconditionally. The byte-equivalent
  implementation is at
  `.claude/hooks/session_start_dispatch.py:530-552` and
  `.codex/gtkb-hooks/session_start_dispatch.py:524-545`.
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md`
  (Slice 2 VERIFIED) - the UserPromptSubmit init-keyword matcher in
  `scripts/workstream_focus.py` is the live interactive-override entry
  point. The session-state marker at
  `.claude/session/active-session-role.json` is the durable carrier of
  the interactive override.
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md`
  (Slice 4 VERIFIED) - `scripts/session_role_resolution.py` is the
  single deterministic implementation of the interactive rows of
  `DCL-SESSION-ROLE-RESOLUTION-001`. Both dispatchers' headless rows +
  the resolver's interactive rows together form the complete
  resolution table.

**Direct text consequence:** the parent scoping-003 line 344
requirement ("BOTH dispatchers define a `StartupDecision.INTERACTIVE_OVERRIDE_AUTHORIZED`
enum value OR equivalent symbol per the spec revision") resolves to the
five-value enum vocabulary. The IP-4 successor evidence is the "spec
revision" the parent charter anticipated; the parity check therefore
asserts the IP-4 enum, not an unshipped `INTERACTIVE_OVERRIDE_AUTHORIZED`.

**Cache-writer parity assertion (newly added in this REVISED):** the
parent scoping-003 line 345 explicitly requires this assertion, and
`-001` omitted it. Assertion 9 below closes that gap.

## Requirement Sufficiency

**Existing requirements sufficient.**

Citation of governing requirements that make the Slice 8 parity-check
scope complete:

- `DCL-SESSION-ROLE-RESOLUTION-001` v1 - the deterministic resolution
  table whose byte-equivalent enforcement is the slice's central goal.
  The contract is fully specified in the resolver module's docstring
  and assertions; Slice 8 promotes byte-parity from convention to
  mechanical assertion.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 - the architectural
  decision authorizing the durable-vs-session split; the parity check
  guards the dispatch-side invariants that flow from this decision.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v1 - the canonical init
  keyword regex whose two-site presence is asserted by assertion 3.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v1 - the receiver-side
  enforcement contract whose set-membership and audit-log shapes are
  asserted by assertions 6 and 7.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` - the parent governance
  parity authority that `scripts/check_codex_hook_parity.py` already
  serves. This slice extends its enforcement surface.
- IP-4 successor evidence chain
  (`bridge/gtkb-canonical-init-keyword-syntax-001-005.md` through `-009.md`)
  formally records the five-value `StartupDecision` enum as the
  as-shipped equivalent of the parent scoping-003 line 344
  `INTERACTIVE_OVERRIDE_AUTHORIZED` term.
- Slice 1 VERIFIED + Slice 2 VERIFIED + Slice 4 VERIFIED establish the
  cache-writer parity, UserPromptSubmit override entry point, and
  shared resolver respectively. All three are the as-shipped invariants
  Slice 8's parity check enforces.

No new or revised specification is required before implementation. The
existing governing artifacts cover the assertion scope; the
implementation task is to extend `scripts/check_codex_hook_parity.py`
with mechanical assertions that the dispatchers' current byte-equivalent
implementation stays byte-equivalent under future drift.

## Summary

Upgrade `scripts/check_codex_hook_parity.py` from its current
presence/registration discipline to a resolution-table-contract
enforcement surface that compares the Claude and Codex SessionStart
dispatchers (`.claude/hooks/session_start_dispatch.py` and
`.codex/gtkb-hooks/session_start_dispatch.py`) for byte-equivalent
resolution-table primitives. Closes the last piece of the scoping-002
F1 finding (Codex hook surface coverage) by giving future drift a
mechanical gate.

## Premise Verification (against live code; this section is the GO scope anchor)

(Carried forward from -001 with the cache-writer parity finding added.)

### State of `scripts/check_codex_hook_parity.py` today

The current `check_project` function (lines 236-592) enforces
presence/registration assertions, lifecycle-term presence in the Codex
dispatcher (lines 142-170: ~28 substring tokens), and forbidden-legacy-
string assertions. It does NOT yet enforce the resolution-table contract
items enumerated under "Plan" below.

### State of the two SessionStart dispatchers today (cross-comparison evidence)

`.claude/hooks/session_start_dispatch.py` (657 lines) and
`.codex/gtkb-hooks/session_start_dispatch.py` (651 lines) share these
resolution-table primitives byte-equivalently:

- Lines 42-53 (Claude) / 39-53 (Codex): canonical init-keyword regex,
  run-id env-var, dispatch-keyword env-var, label-to-mode map,
  mode-to-role-profile map.
- Lines 66-78 (Claude) / 60-72 (Codex): `StartupDecision` enum with
  five canonical members.
- Lines 129-145 (Claude) / 123-138 (Codex): `_SESSION_ROLE_MARKER_NAME`,
  `_session_role_marker_path`, `_invalidate_session_role_marker`.
- Lines 305-422 (Claude) / 299-416 (Codex): `_audit_log_misdirected_dispatch`
  and `_bridge_dispatch_keyword_check`.
- **Lines 530-552 (Claude) / 524-545 (Codex): `_write_role_scoped_startup_relay_caches`**
  byte-equivalent; iterates `_MODE_TO_ROLE_PROFILE` and skips
  `primary_mode` (writes BOTH `-pb.md` and `-lo.md` caches
  unconditionally per Slice 1 VERIFIED fix).

The only intentional differences are `HARNESS_NAME` (`"claude"` vs
`"codex"`) and `OUT_DIR` (`.claude/hooks` vs `.codex/gtkb-hooks`).

### In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
`.claude/rules/project-root-boundary.md`: both target files are in-root.
No `applications/<name>/` paths, no Agent Red live dependency, no
out-of-root path.

## Plan

### `scripts/check_codex_hook_parity.py` (modify)

Add a new top-level helper `_resolution_table_parity_errors(project_root)`
called from `check_project` after the existing assertions. The helper
performs NINE assertion classes:

1. **Marker constant parity (assertion 1).** Both dispatchers,
   `scripts/session_role_resolution.py`, and `scripts/workstream_focus.py`
   contain the exact literal
   `_SESSION_ROLE_MARKER_NAME = "active-session-role.json"`.

2. **StartupDecision enum parity (assertion 2; IP-4 as-shipped vocabulary).**
   Both dispatchers contain `class StartupDecision(Enum):` AND the five
   value lines (`NORMAL_STARTUP = "normal_startup"`,
   `DISPATCH_AUTHORIZED = "dispatch_authorized"`,
   `SPOOF_FALLBACK = "spoof_fallback"`,
   `LEGACY_FALLBACK = "legacy_fallback"`,
   `STRICT_DROP = "strict_drop"`) byte-equal between the two
   dispatchers. Explicitly cites the IP-4 successor evidence in the
   error message so future readers see why the assertion uses this
   vocabulary rather than the parent scoping-003 `INTERACTIVE_OVERRIDE_AUTHORIZED`.

3. **Canonical init-keyword regex parity (assertion 3).** Both
   dispatchers contain the exact line
   `_CANONICAL_KEYWORD_RE = re.compile(r"^::init gtkb (pb|lo)$")`.

4. **Label and profile map parity (assertion 4).** Both dispatchers
   contain identical `_LABEL_TO_CANONICAL_MODE` and
   `_MODE_TO_ROLE_PROFILE` dictionary literals (compared via
   `ast.parse` + `ast.dump` normalization).

5. **Marker invalidation parity (assertion 5).** Both dispatchers
   contain `_invalidate_session_role_marker` AND call it from `main()`
   before the IP-4 dispatch fork. `_session_role_marker_path` resolves
   to `.claude/session/active-session-role.json` in both (the marker
   location is harness-name-agnostic per Slice 3 VERIFIED).

6. **Behavior-table parity (assertion 6).** Both dispatchers contain
   `_bridge_dispatch_keyword_check` AND a 5-row behavior table comment
   header (`env-var`, `keyword`, `mode-in-role-set`, `Decision`,
   `Effect`). Function body contains the 5 decision-return statements
   matching the assertion 2 vocabulary.

7. **Audit-log parity (assertion 7).** Both dispatchers contain
   `_audit_log_misdirected_dispatch` AND the audit-record kind literal
   `"misdirected_dispatch_strict_drop"`. Both write to
   `.gtkb-state/bridge-poller/dispatch-failures.jsonl`.

8. **Intentional-difference catalogue (assertion 8).** Each dispatcher
   contains its OWN harness name (`HARNESS_NAME = "claude"` in Claude;
   `HARNESS_NAME = "codex"` in Codex) and only its own `OUT_DIR` path
   token (`.claude/hooks` in Claude; `.codex/gtkb-hooks` in Codex).
   Guards against copy-paste-of-harness-name drift.

9. **Cache-writer parity (assertion 9; NEW in REVISED-003; addresses
   F2 charter requirement).** Both dispatchers contain
   `def _write_role_scoped_startup_relay_caches`. Each function body
   contains the literal line `for mode in sorted(_MODE_TO_ROLE_PROFILE):`
   AND `if mode == primary_mode:` AND `continue` (the unconditional-
   both-caches loop shape per Slice 1 VERIFIED). Neither function body
   references `_resolve_own_role_set` (the pre-Slice-1 defective shape
   that conditioned cache writes on the durable role set). This
   assertion guards against regression to the pre-Slice-1 cache-writer
   shape, which would re-introduce the defect where an interactive
   session whose owner declared the opposite role would receive a
   degraded disclosure.

Each assertion class extends the existing `errors` list. No new
external dependencies (`pathlib`, `ast`, `re` already in scope).

### `platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py` (new)

A new test module covering the nine assertion classes via the
mutate-and-test pattern. Module-level fixture stages a copy of the
canonical repo state in a `tmp_path`-rooted minimal project skeleton;
per test, the fixture mutates one specific resolution-table primitive
and asserts that `check_project` returns a list containing the specific
error for that mutation.

Planned tests (N=16 minimum):

| #  | Test                                                                  | Behavior covered                             |
|----|-----------------------------------------------------------------------|----------------------------------------------|
| 1  | `test_resolution_table_clean_state_passes`                            | baseline: no resolution-table errors today    |
| 2  | `test_marker_constant_missing_from_claude_dispatcher`                 | assertion 1, Claude site                      |
| 3  | `test_marker_constant_missing_from_codex_dispatcher`                  | assertion 1, Codex site                       |
| 4  | `test_marker_constant_missing_from_resolver`                          | assertion 1, resolver site                    |
| 5  | `test_startup_decision_enum_missing_member_in_claude`                 | assertion 2, missing member                   |
| 6  | `test_startup_decision_enum_value_diverges_between_dispatchers`       | assertion 2, value mismatch                   |
| 7  | `test_canonical_init_keyword_regex_diverges`                          | assertion 3                                   |
| 8  | `test_label_to_canonical_mode_dict_diverges`                          | assertion 4                                   |
| 9  | `test_invalidate_marker_not_called_in_main`                           | assertion 5, missing call                     |
| 10 | `test_bridge_dispatch_keyword_check_decision_missing`                 | assertion 6, missing branch                   |
| 11 | `test_audit_log_kind_literal_missing`                                 | assertion 7                                   |
| 12 | `test_claude_harness_name_appears_in_codex_dispatcher`                | assertion 8, intentional-difference guard     |
| 13 | `test_codex_out_dir_appears_in_claude_dispatcher`                     | assertion 8, intentional-difference guard     |
| 14 | `test_cache_writer_iterates_role_set_instead_of_mode_map_claude`      | assertion 9, F2: pre-Slice-1 defective shape  |
| 15 | `test_cache_writer_iterates_role_set_instead_of_mode_map_codex`       | assertion 9, F2: pre-Slice-1 defective shape  |
| 16 | `test_clean_state_still_passes_after_test_module_addition`            | regression: no false-positive on this PR      |

Tests 14 and 15 are new in REVISED-003 and directly satisfy F2 required
revision 3 ("Extend the test table so at least one mutation test fails
when one dispatcher loses the role-cache parity behavior").

The test module uses the repo venv (`groundtruth-kb/.venv/Scripts/`)
for `ruff format --check` + `ruff check` and pins
`pytest --basetemp E:\GT-KB\.pytest-tmp\slice8-revise-basetemp`.

## Acceptance Criteria

1. `python scripts/check_codex_hook_parity.py` exits 0 on the current
   codebase (no false positives introduced).
2. The new test module passes (16/16 minimum) with the repo venv.
3. Each new error message is deterministic (no timestamps, no path
   ordering jitter).
4. The NINE assertion classes ALL detect at least one mutation each in
   the new tests.
5. The check_project function's error list grows by at most ~27 lines
   of new error strings.
6. The new test module follows the same style as
   `platform_tests/scripts/test_doctor_session_role_marker.py` (the
   recent peer test from Slice 7).
7. Cache-writer parity assertion (assertion 9) detects the
   pre-Slice-1 cache-writer shape (iterates `_resolve_own_role_set()`)
   in either dispatcher (F2 charter requirement).

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` v1 - the resolution table whose
  byte-equivalent enforcement Slice 8 elevates from convention to
  mechanical assertion.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 - the parent decision
  authorizing the cross-dispatcher symmetry being enforced; Decision 2
  is the specific clause that requires both `-pb.md` and `-lo.md`
  caches unconditional (assertion 9 source).
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 - the session-stated role surface
  whose dispatch fidelity the assertions protect.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v1 - the init-keyword regex
  whose two-site parity is asserted by assertion 3.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v1 - the receiver-side
  enforcement contract whose set-membership and audit-log shapes are
  asserted by assertions 6 and 7.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` - the parent governance
  parity authority that `check_codex_hook_parity.py` already serves.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root boundary affirmed.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this REVISED is filed at `-003`;
  `bridge/INDEX.md` will be updated with `REVISED:` at the top.
  No prior bridge version (`-001`, `-002`) is deleted or rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test
  mapping under "Spec-Derived Verification (Plan)" below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project triple
  in header.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`,
  `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - covered by
  `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active v3;
  covers WI-3478).
- `GOV-ARTIFACT-APPROVAL-001` - no canonical artifact insertion.
- `GOV-STANDING-BACKLOG-001` - single feature slice; not a bulk
  operation. See Clause Scope Clarification below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory),
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory),
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `bridge/gtkb-interactive-session-role-override-scoping-003.md` -
  parent scoping REVISED-1 carrying the Slice 8 charter at lines 338-350.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` -
  parent scoping GO.
- `bridge/gtkb-canonical-init-keyword-syntax-001-005.md` - IP-4 enum
  cleanup landed the as-shipped five-value `StartupDecision` vocabulary
  (the F2 successor evidence for assertion 2).
- `bridge/gtkb-canonical-init-keyword-syntax-001-006.md` - Codex GO
  confirming the IP-4 enum cleanup direction.
- `bridge/gtkb-canonical-init-keyword-syntax-001-009.md` - IP-4
  VERIFIED.
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md` -
  Slice 1 VERIFIED; landed the cache-writer fix in both dispatchers
  (the F2 successor evidence for assertion 9).
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md` -
  Slice 2 VERIFIED; the UserPromptSubmit init-keyword matcher in
  `scripts/workstream_focus.py` is the live interactive-override entry
  point.
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md` -
  Slice 3 VERIFIED; established marker-invalidation parity (assertion 5
  source).
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md` -
  Slice 4 VERIFIED; established the resolver as the single
  authoritative source for interactive resolution.

## Prior Deliberations

- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-001.md` -
  this thread's NEW-001 (this REVISED supersedes it).
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-002.md` -
  Codex NO-GO -002 with F1 + F2; addressed in this REVISED.
- `bridge/gtkb-interactive-session-role-override-scoping-003.md` -
  parent scoping REVISED-1; Slice 8 charter at lines 338-350.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` -
  parent scoping GO.
- `bridge/gtkb-canonical-init-keyword-syntax-001-005.md` through `-009.md` -
  the IP-4 thread that defined the as-shipped five-value
  `StartupDecision` vocabulary, superseding the parent scoping-003 line
  344 `INTERACTIVE_OVERRIDE_AUTHORIZED` term.
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md` -
  Slice 1 VERIFIED.
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md` -
  Slice 3 VERIFIED.
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md` -
  Slice 4 VERIFIED.
- `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-006.md` -
  Slice 7 VERIFIED (committed at `71f81d96` 2026-05-30).

## Owner Decisions / Input

This REVISED operates within the same approval envelope as -001.

- `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v3 (active)
  - covers `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE` including
  `WI-3478`.
- `DELIB-2507` - the original owner directive that mandated interactive
  `::init gtkb (pb|lo)` overrides the durable role for interactive
  surfaces while keeping durable as the headless-dispatch authority.
- S371 owner AskUserQuestion decisions captured in the scoping thread
  (six AUQ answers establishing the 10-slice decomposition, artifact
  framing, and the role-vs-session split).
- Session-S378 owner AskUserQuestion - approved bundled commit of
  Slices 5-7 (landed at `71f81d96`).

No new owner AUQ is required for this REVISED. F1 and F2 are addressable
through the bridge protocol's normal NO-GO -> REVISED loop; both findings
have evidence-grounded resolutions and do not surface new owner
decisions.

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

| Spec / behavior                                                                       | Assertion       | Tests          |
|---------------------------------------------------------------------------------------|-----------------|----------------|
| Marker constant single-value invariant (`DCL-SESSION-ROLE-RESOLUTION-001`)            | 1               | 2, 3, 4        |
| IP-4 five-value `StartupDecision` enum closed set (IP-4 successor SPEC + DCL)         | 2               | 5, 6           |
| Init-keyword regex single-form contract (`SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`)    | 3               | 7              |
| Label-to-canonical-mode mapping closed dict (DCL receiver clause)                     | 4               | 8              |
| Marker-invalidation pre-dispatch contract (Slice 3 VERIFIED)                          | 5               | 9              |
| Decision-table 5-row behavior contract (DCL receiver clause)                          | 6               | 10             |
| Audit-log misdirected-drop record-kind (PB-INCIDENT-S321-DAEMON-...-001 v2)           | 7               | 11             |
| Intentional-difference guard (cross-dispatcher copy-paste prevention)                 | 8               | 12, 13         |
| **Cache-writer both-caches-unconditional invariant (`ADR-INTERACTIVE-...-001` Decision 2; Slice 1 VERIFIED)** | **9** | **14, 15**     |
| Baseline + regression cleanliness                                                     | n/a             | 1, 16          |

### Commands the post-impl report will execute (repo venv; explicit basetemp)

```text
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/check_codex_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py

groundtruth-kb/.venv/Scripts/ruff.exe check scripts/check_codex_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py -q --basetemp E:\GT-KB\.pytest-tmp\slice8-revise-basetemp

# Regression: the upgrade must not introduce false positives on the current codebase.
groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py
```

## Risk and Rollback

### Risk classes

- **R1: false positive on current codebase.** Mitigation: test 1 +
  test 16 establish the no-regression baseline; the post-impl report
  will re-run the standalone parity check after the upgrade to confirm
  exit 0.
- **R2: assertion drift coverage gap.** Mitigation: assertion 8's
  intentional-difference guard prevents the copy-paste-of-harness-name
  drift class; assertion 9 prevents the cache-writer regression class
  scoping-003 line 71 originally flagged.
- **R3: brittle string-matching.** Mitigation: assertion 4 uses
  `ast.parse` + `ast.dump` for dict-literal normalization; the other
  assertions check substring or byte-equal literal lines that are
  stable per the dispatcher cross-comparison evidence.

### Rollback

If the upgrade is found defective after implementation, rollback is one
commit revert. The current parity-check behavior is preserved verbatim;
the assertions are additive. No data, state, or canonical artifact is
affected.

## Recommended Commit Type

`feat` - the slice adds a new mechanical-assertion surface
(resolution-table contract enforcement) that did not exist before.
Not `fix` and not `test` alone.

## target_paths Note

The machine-readable `target_paths` metadata is the inline-JSON header
line. The two files match the bridge-proposal-target convention exactly.
No KB/MemBase mutation occurs.
