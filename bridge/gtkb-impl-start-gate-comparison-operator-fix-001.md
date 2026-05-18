NEW

# Implementation Proposal - implementation_start_gate MUTATING_COMMAND_RE Comparison-Operator False-Positive Fix (WI-3356)

bridge_kind: implementation_proposal
Document: gtkb-impl-start-gate-comparison-operator-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-16 UTC
Session: S357

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3356

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

This NEW proposal fixes a false-positive in `scripts/implementation_start_gate.py:MUTATING_COMMAND_RE` that misclassifies read-only commands as mutating when the command text contains a Python comparison operator (`>=`) or augmented right-shift assignment operator (`>>=`). It is a reliability-fast-lane defect fix and a direct sibling of WI-3317 (the format-spec false-positive fix, VERIFIED).

## Claim

`MUTATING_COMMAND_RE` (lines 72-79 of `scripts/implementation_start_gate.py`) detects shell file redirects through the second alternation branch of the pattern:

```
(?<![:>-])>{1,2}(?![&])
```

The trailing negative lookahead `(?![&])` excludes only the stream-merge form `>&` (e.g. `2>&1`). It does not exclude `>=`. For a Python comparison such as `i>=0`:

- the character before `>` is `i`, which satisfies the lookbehind `(?<![:>-])`;
- `>{1,2}` matches the single `>`;
- the lookahead `(?![&])` passes because the next character is `=`, not `&`.

The branch therefore matches. `_is_mutating_command()` returns `True`; `changed_paths()` returns `(paths, True)`; `gate_decision()` sets `protected = ["<unknown-mutating-target>"]` (line 313); `validate_targets()` raises `AuthorizationError`, and the gate emits a `block` decision for a genuinely read-only command.

This is the comparison-operator sibling of WI-3317. WI-3317 added the lookbehind exclusions `(?<![:>-])` for `:>` (format-spec right-align) and `->` (return annotation) - tokens disambiguated by the character that *precedes* `>`. The comparison-operator class is disambiguated by the character that *follows* `>` (an `=`), so it needs a lookahead fix, which the WI-3317 thread did not make.

### Live evidence (this session, S357, 2026-05-16)

The read-only Bash command

```
python -m groundtruth_kb backlog list --json --all 2>&1 | grep -iE 'mutating|redirect|comparison|start.gate|>=' | head -10
```

was blocked by `GTKB-IMPLEMENTATION-START-GATE` ("protected implementation mutation requires a live bridge GO authorization packet"). The command performs no mutation - it is a `grep` pipeline over read-only CLI output - but its `grep -E` pattern contains the literal substring `>=`. The blast radius is therefore not limited to `python -c` one-liners: any command string whose text contains `>=` is affected.

## Fix Analysis

The fix extends the trailing lookahead so a `>` that is part of a comparison/assignment operator is not treated as a redirect. Two candidate lookaheads were evaluated empirically (a standalone script reproduced `MUTATING_COMMAND_RE` and tested both against the full case set below):

| Command text | current `(?![&])` | `(?![&=])` | `(?![>&=])` | desired |
|---|---|---|---|---|
| `python -c "print(1 if i>=0 else 2)"` | mutating | not | not | not |
| `python -c "assert x >= 0"` | mutating | not | not | not |
| `python -c "x=8; x>>=2; print(x)"` | mutating | **mutating** | not | not |
| `python -c "print(f'{n:>2}')"` (WI-3317) | not | not | not | not |
| `python -c "def f() -> int: return 1"` (WI-3317) | not | not | not | not |
| `cmd > out.txt` | mutating | mutating | mutating | mutating |
| `cmd >> out.txt` | mutating | mutating | mutating | mutating |
| `cmd 2> err.txt` / `cmd 1> out.txt` / `cmd &> out.txt` | mutating | mutating | mutating | mutating |
| `cmd>out.txt` (no space) | mutating | mutating | mutating | mutating |
| `cmd 2>&1` | not | not | not | not |

The minimal `(?![&=])` fixes `>=` but **not** `>>=`: Python's regex engine backtracks `>{1,2}` from `>>` to a single `>`, whose following character is `>` - and `>` is not in `[&=]` - so the branch still matches. `(?![>&=])` adds `>` to the lookahead, so the backtrack path also fails; the existing lookbehind `(?<![:>-])` already blocks starting a match in the middle of a `>` run, so `>>=` no longer matches at any position. Both `>=` and `>>=` are categorically never shell redirects (shell redirects are `>`, `>>`, `N>`, `&>`), so excluding them carries no false-negative risk. This proposal adopts `(?![>&=])`.

### Residual (deliberately out of scope)

A bare `>` Python comparison (`a > b`, with or without surrounding spaces) is **not** fixed and is deliberately left classified as mutating. A space-delimited ` > ` is genuinely indistinguishable by regex from a real shell redirect (`cmd > out.txt`), and the existing test `test_gate_blocks_unnumbered_redirect_to_file` requires the bare-`>` form `cmd > out.txt` to remain classified as mutating. Excluding bare ` > ` would punch a false-negative hole in a security gate - a real mutating redirect would pass unblocked. A false-positive on a read-only command is recoverable friction (re-phrase the command); a false-negative on a real redirect is a governance gap. The same reasoning applies to the `>>` right-shift operator versus the `>>` append redirect. The unambiguous operators (`>=`, `>>=`) are fixed; the ambiguous ones (` > `, ` >> `) are out of scope by design.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`: `E:\GT-KB\scripts\implementation_start_gate.py` and `E:\GT-KB\platform_tests\scripts\test_implementation_start_gate.py`. The bridge file is at `E:\GT-KB\bridge\gtkb-impl-start-gate-comparison-operator-fix-001.md`. No `applications/` path and no path outside `E:\GT-KB` is created, read as a live dependency, or required. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` is satisfied.

## Relationship To gtkb-impl-gate-friction-hygiene

The bridge thread `gtkb-impl-gate-friction-hygiene` (latest status GO at `bridge/gtkb-impl-gate-friction-hygiene-004.md`; WI-3310; project `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS`) modifies the *same source file* `scripts/implementation_start_gate.py` and the *same test file* `platform_tests/scripts/test_implementation_start_gate.py`. This section disambiguates the two threads.

**Disjoint regex and disjoint scope.** `gtkb-impl-gate-friction-hygiene` IP-1 extends `NULL_SINK_REDIRECT_STRIP_RE` (the null-sink redirect allowlist); IP-2 changes the gate's block-reason message; IP-3 adds a `--diagnostic` CLI mode in `main()`. None of those three touches `MUTATING_COMMAND_RE`. This proposal touches *only* the trailing redirect lookahead of `MUTATING_COMMAND_RE` and adds tests. The two threads edit different, non-adjacent regions of the file; whichever lands first, the other applies cleanly without conflict.

**Why a separate thread rather than folding into `gtkb-impl-gate-friction-hygiene`.** (1) This is a `defect`-class false-positive fix, not a friction-hygiene *enhancement*. (2) The precedent for a `MUTATING_COMMAND_RE` false-positive defect fix is WI-3317's dedicated `gtkb-impl-start-gate-format-spec-fix` thread; this proposal is WI-3317's direct sibling and uses the sibling slug family `gtkb-impl-start-gate-*`. (3) `gtkb-impl-gate-friction-hygiene` is already at GO and in its implementation/verification phase; folding a new IP into it would require re-opening a near-closure thread - exactly the entanglement that `bridge/gtkb-impl-gate-friction-hygiene-003.md` itself argued against for the older thread. (4) The owner directed this work into the reliability fast-lane (`PROJECT-GTKB-RELIABILITY-FIXES`), a different project from friction-hygiene's `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS`.

**What this proposal does not do.** It does not modify `NULL_SINK_REDIRECT_STRIP_RE`, the block-reason message, or `main()`. It does not close, narrow, satisfy, or waive any obligation of `gtkb-impl-gate-friction-hygiene` or the older `gtkb-implementation-gate-friction-hygiene` thread; those threads' INDEX statuses are left intact.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this proposal as a bridge artifact.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all target paths are in-root under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting; this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting; the verification plan maps each linked behavior to an executed test.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the implementation-start gate is the mechanical enforcement surface for this protected behavior; the fix narrows a false-positive while preserving the gate's true-positive (real-redirect) coverage.
- `GOV-ARTIFACT-APPROVAL-001` - protected-mutation evidence requirement; the gate is one enforcement surface for it and this change preserves that surface.
- `SPEC-AUQ-POLICY-ENGINE-001` - the implementation-start gate is part of the deterministic policy-gate family; the fix keeps the gate's classification deterministic.
- `GOV-STANDING-BACKLOG-001` - WI-3356 is a single tracked standing-backlog work item; this is not a bulk operation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; WI-3356, this bridge thread, and the linked specs form the artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; WI-3356 triggers this proposal and its spec-derived tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; the work is captured as a governed WI with a bridge artifact and spec-derived tests.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-decision evidence: owner approved the standing reliability fast-lane (project `PROJECT-GTKB-RELIABILITY-FIXES` plus standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`) that covers WI-3356.

No directly-governing functional specification exists for the hook's regex - the hook is its own implementation surface, as established by the WI-3317 thread. The existing regex shape is the de-facto specification; this proposal narrows the false-positive set while preserving the true-positive set, and the verification plan proves both.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner direction establishing the standing reliability fast-lane for small defect fixes; authorizes the project and standing authorization that cover WI-3356.
- `gtkb-impl-start-gate-format-spec-fix` bridge thread (WI-3317) - the prior `MUTATING_COMMAND_RE` defect fix, VERIFIED at `bridge/gtkb-impl-start-gate-format-spec-fix-008.md`. It replaced the old `(^|[^>])>{1,2}($|[^&])` redirect branch with the current `(?<![:>-])>{1,2}(?![&])`, adding the `:>` and `->` lookbehind exclusions. This proposal is its direct sibling: the same regex, a distinct false-positive class (comparison operators), fixed via the trailing lookahead. No rejected approach is revisited - the WI-3317 thread never considered the comparison-operator class.
- Deliberation Archive search `implementation start gate MUTATING_COMMAND_RE redirect false positive comparison operator` (limit 8) returned no deliberation addressing the `>=`/`>>=` comparison-operator false-positive; the nearest prior art is the WI-3317 thread above.
- `gtkb-impl-gate-friction-hygiene` bridge thread (WI-3310) - touches the same source and test files but a disjoint regex and scope; see `## Relationship To gtkb-impl-gate-friction-hygiene`.

## Owner Decisions / Input

This proposal proceeds under standing owner authorization; it requires no new owner AskUserQuestion decision.

- The standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active; owner-approved per `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` and formal-artifact-approval packet `2026-05-15-gov-reliability-fast-lane.json`) covers WI-3356 through active project membership in `PROJECT-GTKB-RELIABILITY-FIXES`. Its `allowed_mutation_classes` are `source`, `test_addition`, and `hook_upgrade`; IP-1 (`source`) and IP-2 (`test_addition`) fall within scope. Its `forbidden_operations` (`deploy`, `git_push_force`, `spec_deletion`) are not exercised.
- The reliability fast-lane explicitly removes per-fix deliberation, per-fix project authorization, and per-fix formal-artifact-approval packets for small defect fixes; the standing authorization is the owner approval.
- Owner directive, 2026-05-16 (S357): the owner directed this specific defect fix routed through the standard bridge protocol under the reliability fast-lane; WI-3356 was captured as a backlog candidate accordingly.
- No destructive action, no deployment, no spec mutation, and no protected narrative-artifact edit is requested. This is a mechanical defect-class fix with preserved true-positive coverage.

## Requirement Sufficiency

Existing requirements sufficient. The gate's intent - classify mutating shell redirects on protected paths so protected mutations require a bridge GO authorization packet - is established by `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, `GOV-ARTIFACT-APPROVAL-001`, and the existing regex shape carried forward by the VERIFIED WI-3317 thread. This proposal narrows a false-positive without changing that intent. No new or revised requirement or specification is created.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-work-item, single-regex, single-test-file change. It is not a bulk backlog operation: it performs no batch resolve, promote, or retire of work items or specifications, and it adds no MemBase rows beyond the optional WI-3356 stage transition at completion. WI-3356 is an active member of `PROJECT-GTKB-RELIABILITY-FIXES` (linked S357); the covering owner authorization is the standing reliability fast-lane authorization whose evidence is the formal-artifact-approval packet `2026-05-15-gov-reliability-fast-lane.json`. References to "work item", "backlog", and "standing backlog" in this proposal describe only this single WI and its governed filing path. The review-packet inventory is exactly IP-1 (regex) plus IP-2 (tests) within this one thread file.

## Bridge INDEX Update Evidence

`bridge/INDEX.md` is the canonical bridge workflow state. This NEW is filed at `bridge/gtkb-impl-start-gate-comparison-operator-fix-001.md` with a new `Document: gtkb-impl-start-gate-comparison-operator-fix` entry prepended to the top of `bridge/INDEX.md` (after the header comments), carrying a single `NEW:` line. No other `Document:` entry is edited, reordered, or removed.

## Proposed Scope

### IP-1: Fix the MUTATING_COMMAND_RE redirect lookahead

In `scripts/implementation_start_gate.py`, in `MUTATING_COMMAND_RE` (the redirect alternation, line 77), change the trailing lookahead:

Old: `(?<![:>-])>{1,2}(?![&])`

New: `(?<![:>-])>{1,2}(?![>&=])`

This is the single operative change - one character class extended from `[&]` to `[>&=]`. It excludes `>=` and `>>=` from the redirect branch while preserving every real redirect form and the existing `2>&1` exclusion (see `## Fix Analysis`). `NULL_SINK_REDIRECT_STRIP_RE`, the block-reason message, and `main()` are not touched (those are `gtkb-impl-gate-friction-hygiene` scope).

### IP-2: Add spec-derived regression tests

In `platform_tests/scripts/test_implementation_start_gate.py`, alongside the existing `WI-3317` section (`test_gate_allows_python_format_spec_right_align`, `test_gate_allows_python_arrow_token`), add a `WI-3356` section with:

- `test_gate_allows_python_ge_comparison` - asserts `_is_mutating_command('python -c "print(1 if i>=0 else 2)"')` is `False`.
- `test_gate_allows_python_ge_comparison_with_spaces` - asserts `_is_mutating_command('python -c "assert x >= 0"')` is `False`.
- `test_gate_allows_python_rshift_augmented_assignment` - asserts `_is_mutating_command('python -c "x=8; x>>=2; print(x)"')` is `False`.

True-positive preservation is covered by the existing redirect-blocks tests in the same file (`test_gate_blocks_unnumbered_redirect_to_file`, `test_gate_blocks_append_redirect_to_file`, `test_gate_blocks_stdout_numbered_redirect_to_file`, `test_gate_blocks_stderr_numbered_redirect_to_real_file`, `test_gate_blocks_combined_redirect_to_file`, `test_gate_blocks_no_space_redirect_to_file`); the verification command runs the whole file, so a regression in any of them fails the suite.

## Specification-Derived Verification Plan

Every linked behavioral specification maps to at least one executed test in `platform_tests/scripts/test_implementation_start_gate.py`.

| Behavior / spec clause | Test | Covers |
|---|---|---|
| `>=` comparison (no space) not classified mutating | `test_gate_allows_python_ge_comparison` (new) | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 |
| `>=` comparison (spaced) not classified mutating | `test_gate_allows_python_ge_comparison_with_spaces` (new) | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 |
| `>>=` augmented right-shift assignment not classified mutating | `test_gate_allows_python_rshift_augmented_assignment` (new) | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 |
| Real shell redirects (`>`, `>>`, `2>`, `1>`, `&>`, no-space `>`) still classified mutating | existing `test_gate_blocks_*` redirect tests | PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001, GOV-ARTIFACT-APPROVAL-001 |
| WI-3317 exclusions (`:>`, `->`) still hold | existing `test_gate_allows_python_format_spec_right_align`, `test_gate_allows_python_arrow_token` | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 |
| Gate classification remains deterministic | full `platform_tests/scripts/test_implementation_start_gate.py` run | SPEC-AUQ-POLICY-ENGINE-001 |

Verification commands:

```
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
python -m ruff format --check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
```

`platform_tests/scripts/test_implementation_start_gate.py` is the live canonical implementation-start-gate test file (recorded as the verification method in `config/agent-control/system-interface-map.toml`). The implementation reaches `VERIFIED` only when the existing suite plus the three new `WI-3356` tests all pass and both ruff checks are clean for the touched files.

## Acceptance Criteria

- IP-1 landed: `MUTATING_COMMAND_RE`'s redirect lookahead is `(?![>&=])`; `_is_mutating_command()` returns `False` for `>=` and `>>=` command text and `True` for every real redirect form.
- IP-2 landed: the three new `WI-3356` tests are present and pass.
- No regression in any other `platform_tests/scripts/test_implementation_start_gate.py` test; `ruff check` and `ruff format --check` clean for both touched files.
- Bridge applicability preflight and ADR/DCL clause preflight both pass for bridge id `gtkb-impl-start-gate-comparison-operator-fix`.
- No file outside `target_paths` is modified.

## Risks / Rollback

- Risk: `(?![>&=])` over-narrows and misses an exotic redirect form. Mitigation: the six existing `test_gate_blocks_*` redirect tests pin every real redirect form (`>`, `>>`, `N>`, `&>`, no-space); `(?![>&=])` only ever suppresses a `>` followed by `>`, `&`, or `=`, and a real redirect's `>` is never followed by `>` or `=`.
- Risk: interaction with `gtkb-impl-gate-friction-hygiene` on the shared file. Mitigation: the two threads edit non-adjacent regions (`MUTATING_COMMAND_RE` line 77 versus `NULL_SINK_REDIRECT_STRIP_RE` / block-reason / `main()`); see `## Relationship To gtkb-impl-gate-friction-hygiene`. Whichever lands first, the other rebases without conflict.
- Residual (accepted, see `## Fix Analysis`): bare ` > ` and ` >> ` Python comparisons remain classified as mutating. This is deliberate - those forms are indistinguishable from real redirects and a security gate must err toward false-positives, not false-negatives.
- Rollback: revert the single-line IP-1 regex change. The IP-2 tests document the desired behavior and may stay.

## Recommended Commit Type

`fix` - corrects a defect in an existing regex; no new capability surface. Net change is one character class in one regex plus three regression tests.
