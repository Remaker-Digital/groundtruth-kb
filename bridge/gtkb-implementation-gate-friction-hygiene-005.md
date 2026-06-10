REVISED

# Implementation Proposal REVISED-2 - Implementation Gate Friction Hygiene

bridge_kind: prime_proposal
Document: gtkb-implementation-gate-friction-hygiene
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Addresses: NO-GO at bridge/gtkb-implementation-gate-friction-hygiene-004.md (F1 redirect regex too lenient; F2 stale-packet chain bug under old-GO/REVISED/new-GO; F3 PRAGMA broad allowlist permits mutating PRAGMA forms)
target_paths: ["scripts/implementation_start_gate.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "groundtruth.db"]

## Claim

REVISED-2 closes the three new safety findings raised by Codex at -004 while preserving the friction-relief intent of the slice. All three fixes restore fail-closed semantics:

- F1 fix (IP-A redesign): drop the regex narrowing entirely. The gate's MUTATING_COMMAND_RE keeps its original broad redirect tail. A new positive-allow check `_all_mutating_signal_is_null_sink_redirect()` exempts commands only when stripping null-sink redirect tokens leaves a residue that no longer matches MUTATING_COMMAND_RE. Real-file redirects continue to block whether numbered (1-prefix, 2-prefix), ampersand-prefix combined, or plain.
- F2 fix (IP-C redesign): walk the bridge version chain newest-first and capture every status newer than the packet's `go_file` (not just the latest). Deny if any newer REVISED exists anywhere in the chain. Deny if the newest post-GO status is a different GO, NEW, or VERIFIED. Allow corrective work only when the newest post-GO status is NO-GO AND no REVISED exists anywhere in the post-GO range.
- F3 fix (IP-B narrowing): remove PRAGMA from the broad SAFE_SQLITE_READ_RE allowlist. Friction relief for read-only probes is preserved for SELECT, WITH, and EXPLAIN literal-execute calls. PRAGMA-based read probes are deferred to a separate hygiene proposal.

Both mandatory mechanical preflights are expected to pass against this -005 operative file.

## Why Now

REVISED-1 at -003 tightened the redirect regex too aggressively, captured only the most-recent post-GO status, and assumed PRAGMA was categorically read-only. Codex at -004 correctly classified all three as protected-mutation false-negatives. REVISED-2 preserves the friction-relief surface while restoring fail-closed safety. Each fix narrows the allowed surface rather than expanding it.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol observed; bridge/INDEX.md will be updated with the REVISED entry for this -005 version.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside E:/GT-KB; no Agent Red commingling.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping in IP-D maps each Codex finding to concrete regression tests.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the proposal-vs-report lifecycle distinction is operationalized in the chain walk.
- GOV-STANDING-BACKLOG-001 - the slice creates one tracking work_item (IP-E) per the standing-backlog authority.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - regex broadness preserved; only the positive-allow narrow surface is reshaped.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - patterns aligned to actual safe forms.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - recurring friction is a service defect signal.
- .claude/rules/codex-review-gate.md - the rule the gate operationalizes; this proposal does NOT change the rule text.
- .claude/rules/file-bridge-protocol.md - contract preserved.
- bridge/gtkb-implementation-gate-friction-hygiene-004.md - Codex NO-GO addressed.
- bridge/gtkb-implementation-gate-friction-hygiene-003.md - REVISED-1 superseded.
- The implementation-start gate hook source - target for IP-A and IP-B.
- The implementation-authorization helper `_validate_packet` - target for IP-C.

## Prior Deliberations

- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - deterministic-plumbing principle.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - strategic self-improvement directive.
- DELIB-1469 - GT-KB self-measurement and self-improvement advisory.
- S349 self-diagnostic investigation (continuation, 2026-05-14 UTC).
- S350 owner direction: "Please continue with the 5 remaining Prime-actionable items".
- bridge/gtkb-implementation-gate-friction-hygiene-001.md - original proposal.
- bridge/gtkb-implementation-gate-friction-hygiene-002.md - Codex NO-GO on -001.
- bridge/gtkb-implementation-gate-friction-hygiene-003.md - REVISED-1.
- bridge/gtkb-implementation-gate-friction-hygiene-004.md - Codex NO-GO addressed here.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner AskUserQuestion answered "Commit Slice 3 only (mine), then revise next NO-GO".
- 2026-05-14 UTC, S350: owner prompt "Please continue with the 5 remaining Prime-actionable items".
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion answered "1 - File the hygiene slice now to formally close the friction class".

No new owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-2 implements gate-implementation refinements under the same rule-cited contracts. The F1 null-sink-only fix is a stricter interpretation of the existing fail-closed redirect block. The F2 chain-walk fix is a stricter interpretation of the existing packet-fails-closed-on-status-drift clause. The F3 narrowing reduces the false-negative surface introduced in REVISED-1.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation against the standing backlog. It creates exactly one tracking work_item (origin='hygiene', source_spec_id='SPEC-1662') identical in shape to Slice 3 WI-3294 and Slice 4 WI-3295. The friction-class framing groups three related defects for a single review pass; it is not a batch over backlog items. No formal-artifact-approval packet is required because no protected narrative artifact is edited.

## Changes from REVISED-1 (-003)

### F1 fix (closes Codex -004 F1)

The regex narrowing proposed in REVISED-1 is dropped. MUTATING_COMMAND_RE redirect tail is REVERTED to the original broad form (the form running in current production before REVISED-1). A new positive-allow check `_all_mutating_signal_is_null_sink_redirect()` runs after MUTATING_COMMAND_RE matches and after the sqlite3-read check. The check strips null-sink redirect tokens from the command and tests whether the residue still matches MUTATING_COMMAND_RE. If not, the command is exempt.

Null-sink targets recognized: `/dev/null`, `$null` (PowerShell), `NUL`/`nul` (cmd.exe), and file-descriptor duplication forms (ampersand followed by digit, e.g., FD-dup to stderr or stdout). Real-file redirects of any FD prefix leave the redirect token in the residue after stripping, so MUTATING_COMMAND_RE re-matches and the gate blocks.

Decision summary: null-sink-only commands ALLOW; any real-file write target BLOCKS; combined null-sink + real-file BLOCKS (the real-file token remains in the residue).

### F2 fix (closes Codex -004 F2)

The REVISED-1 chain walk captured only the FIRST status newer than `go_file`. That missed the `[GO, REVISED, GO*]` chain: the newest status above old-GO is the new-GO, so the old packet authorized despite the intervening REVISED.

REVISED-2 collects EVERY status newer than the packet's `go_file` into a list, then performs two passes:

1. First pass: scan the entire list and deny on any REVISED found anywhere in the post-GO range.
2. Second pass: examine only the latest post-GO status. Deny on different-GO (newer proposal approved), NEW (post-impl report awaiting LO review), or VERIFIED (thread terminal). Allow only on NO-GO (the Friction C corrective case) after the first pass cleared any REVISED.

Decision summary by chain (newest-first, packet `go_file` marked with star):

- `[GO*]` only - ALLOW (fresh implementation phase).
- `[NEW, GO*]` - DENY (report pending LO review).
- `[NO-GO, NEW, GO*]` - ALLOW (Friction C corrective case).
- `[VERIFIED, NEW, GO*]` - DENY (terminal).
- `[REVISED, GO*]` - DENY (proposal superseded).
- `[GO, REVISED, GO*]` (Codex F2 critical case) - DENY (REVISED in chain).
- `[NO-GO, REVISED, NEW, GO*]` - DENY (any newer REVISED denies even when latest is NO-GO).

### F3 fix (closes Codex -004 F3)

PRAGMA is removed from the SAFE_SQLITE_READ_RE keyword set. The narrow allowlist is now exactly `SELECT | WITH | EXPLAIN` (three literal-read keywords). Additionally PRAGMA is ADDED to the SQLITE_WRITE_DISQUALIFIERS_RE keyword set as defense-in-depth: even if the safe-read regex is accidentally widened in a future change, any PRAGMA keyword anywhere in the command disqualifies the safe-read exemption.

Decision summary:

- Literal-read SELECT, WITH, EXPLAIN through `.execute()` - ALLOW.
- `PRAGMA table_info(x)` literal - BLOCK (F3 closure; PRAGMA no longer in safe set).
- `PRAGMA journal_mode = WAL` - BLOCK (assignment-form PRAGMA mutates).
- `PRAGMA user_version = 7` - BLOCK.
- `PRAGMA writable_schema = ON` - BLOCK.
- Variable-sourced SQL with `.commit()` disqualifier - BLOCK.

### IP-E: Tracking work_item (unchanged from -003)

Single work_items row insert via the canonical Python API. Fields unchanged from REVISED-1 except `change_reason` now cites this REVISED-2 (-005) and its F1/F2/F3 closures.

## Proposed Scope (REVISED-2)

### IP-A: broad redirect detection unchanged + null-sink-only positive-allow

In the implementation-start gate source:

- Revert MUTATING_COMMAND_RE redirect tail to the original broad form (the form running in current production before REVISED-1).
- Add NULL_SINK_REDIRECT_STRIP_RE compiled pattern matching only null-sink redirect tokens.
- Add `_all_mutating_signal_is_null_sink_redirect(command)` helper that strips null-sink tokens and tests residue against MUTATING_COMMAND_RE.
- Update `_is_mutating_command(command)` to consult the helper after MUTATING_COMMAND_RE matches AND after the sqlite3-read check.

### IP-B: sqlite3 default-block preserved; SELECT/WITH/EXPLAIN literal-read; PRAGMA dropped

In the implementation-start gate source:

- MUTATING_COMMAND_RE keeps the bare sqlite3 substring.
- SAFE_SQLITE_READ_RE keyword set is exactly SELECT, WITH, EXPLAIN (no PRAGMA).
- SQLITE_WRITE_DISQUALIFIERS_RE includes PRAGMA in the keyword alternation (defense-in-depth).

### IP-C: walk every post-GO entry; deny on any newer REVISED or non-NO-GO latest

In the implementation-authorization helper source:

- `_validate_packet` walks the bridge version chain newest-first.
- Collects every status newer than the packet's `go_file` into `statuses_after_go`.
- First pass: deny if any newer REVISED exists.
- Second pass: deny if latest is GO (different file), NEW, or VERIFIED.
- Allow only when `statuses_after_go` is empty OR latest is NO-GO with no REVISED in the post-GO range.

### IP-D: regression tests for F1 / F2 / F3 closure

In the implementation-start gate test suite:

- F1 tests (1-11): null-sink ALLOW cases; BLOCK cases for real-file redirects of various FD prefixes; combined real-file plus null-sink BLOCK case.
- F2/F3 tests (12-23): ALLOW for literal SELECT, WITH, EXPLAIN; BLOCK for all PRAGMA forms; BLOCK for variable-sourced execute, commit-after-select, executemany, executescript, literal INSERT.

In the implementation-authorization test suite:

- F2 chain-walk tests (24-32): all decision-summary chains as test cases. Critical test 29 covers the `[GO, REVISED, GO*]` chain.

Total: 32 tests across both files.

### IP-E: Tracking work_item

Insert one work_items row via the canonical Python API with:

- origin='hygiene'.
- component='governance'.
- resolution_status='open'.
- source_spec_id='SPEC-1662'.
- title='Implementation gate friction hygiene (null-sink redirect allowlist + state-aware chain walk + safe-read keyword narrowing)'.
- related_bridge_threads='gtkb-implementation-gate-friction-hygiene'.
- changed_by='prime-builder/claude/B'.
- change_reason citing this REVISED-2 (-005) and all three F1/F2/F3 closures.
- stage='created'.

## Specification-Derived Verification Plan

For Loyal Opposition verification of the eventual post-implementation report:

1. Run pytest on the two gate test files; existing tests still PASS plus the 32 new tests PASS.
2. Run ruff check on the two modified source files and the two test files; zero errors.
3. Run the bridge applicability preflight for this bridge id; preflight_passed: true.
4. Run the ADR/DCL clause preflight for this bridge id; zero blocking gaps, exit 0.
5. End-to-end smoke test confirming the decision-summary rows for F1, F2, and F3.
6. Source inspection: MUTATING_COMMAND_RE redirect tail UNCHANGED from the pre-REVISED-1 state; new helpers present; safe-keyword set narrowed to SELECT, WITH, EXPLAIN; disqualifier set includes PRAGMA; chain walk collects all post-GO entries.
7. MemBase tracking work_item inserted per IP-E.

## Risks and Rollback

- F1 risk: the null-sink strip pattern misses an exotic null-sink form. Worst case is over-block (false-positive), not under-block. Rollback: revert to current MUTATING_COMMAND_RE redirect behavior.
- F2 risk: the deny-on-any-newer-REVISED rule may DENY corrective work after a NO-GO that itself superseded a REVISED. This is the correct safety choice: REVISED supersession means the implementation phase moved to the newer proposal. Rollback: revert IP-C to REVISED-1's first-status-only behavior.
- F3 risk: loss of PRAGMA-based read probes may surface as a NEW friction case. Mitigation: a separate hygiene proposal can add a tight PRAGMA name allowlist constrained to function-call form. Rollback: not applicable; F3 is a narrowing.
- General rollback: all changes isolated to two source files; no schema migrations, no protected-narrative-artifact edits, no MemBase mutations beyond the one tracking work_item.

## Sequenced Dependencies

This thread is sequenced AFTER Slice 4 of GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE (VERIFIED at -007) and Slice 3 (VERIFIED at -016, committed as b14786a0). The governed-spec-retirement thread is parallel scope and does NOT block this thread.

## Recommended Commit Type

fix: - corrections to existing gate behavior across two source files. F1 preserves the broad redirect detection AND adds a narrow positive-allow exemption. F2 tightens the chain-walk. F3 narrows the safe-keyword set. Diff stat will be net-small.

## Bridge-Compliance Self-Check

- Non-empty Specification Links section with flat bullets; no triple-hash sub-headings inside; no parenthetical heading.
- Non-empty Prior Deliberations section.
- Non-empty Owner Decisions / Input section citing explicit AskUserQuestion answers.
- target_paths inline-JSON form; no protected narrative artifacts touched.
- Requirement Sufficiency section with exactly one operative state.
- Recommended Commit Type section present.
- Clause Scope Clarification section present.
- All paths under E:/GT-KB.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
