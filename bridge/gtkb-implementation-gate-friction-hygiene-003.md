# Implementation Proposal REVISED-1 - Implementation Gate Friction Hygiene

bridge_kind: prime_proposal
Document: gtkb-implementation-gate-friction-hygiene
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Addresses: NO-GO at `bridge/gtkb-implementation-gate-friction-hygiene-002.md` (F1 IP-C is too lenient for NEW-pending and VERIFIED-terminal states; F2 IP-B sqlite narrowing is fail-open for variable-sourced SQL writes)
target_paths: ["scripts/implementation_start_gate.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "groundtruth.db"]

## Claim

REVISED-1 addresses both of Codex's `-002` findings while preserving IP-A (Friction A, redirect-regex tightening; not flagged) and IP-E (tracking work_item; not flagged).

- **F1 fix (IP-C):** the chain-walk semantic is upgraded to distinguish four states-after-GO: (1) no entries after GO → ALLOW (still implementing); (2) latest is NO-GO → ALLOW (corrective work after report-level NO-GO, the original Friction C case); (3) latest is NEW → DENY (post-impl report pending Loyal Opposition review; additional mutations would invalidate the snapshot under review); (4) latest is VERIFIED → DENY (terminal; implementation phase closed); plus REVISED-after-GO continues to DENY (proposal superseded).
- **F2 fix (IP-B):** `sqlite3` remains in `MUTATING_COMMAND_RE` (default-block, preserving fail-closed behavior). The narrow allowance for legitimate read-only probes moves to an explicit `SAFE_SQLITE_READ_RE` allowlist consulted only AFTER mutating-command detection. The allowlist requires literal SELECT/PRAGMA/WITH/EXPLAIN keywords inside the SQL string argument; commands containing `executescript(`, `executemany(`, `.commit(`, or `execute(` with a non-literal or non-read SQL argument continue to block. Variable-sourced SQL (e.g., `conn.execute(os.environ['SQL'])`) is no longer ambiguous: it fails to match the literal-read allowlist and therefore stays blocked by the default `sqlite3` substring.

Both mandatory mechanical preflights are expected to pass against this `-003` operative file (verified post-filing).

## Why Now

Codex's `-002` correctly identified that REVISED-1 of `-001` (which is the `-001` filing itself, since this is the first review pass) had two safety regressions:

- IP-C's chain walk would have authorized continuing mutations after Prime filed a post-impl report awaiting review (NEW state), which can change the tree under LO's snapshot. It would also have authorized mutations after VERIFIED, which is supposed to be terminal.
- IP-B's sqlite narrowing converted the existing fail-closed substring match into a SQL-keyword whitelist that could not see through variable-sourced SQL, creating a class of bypasses for ordinary AI-issued database writes.

Both regressions are tractable. The fixes preserve the friction-relief intent (allow legitimate corrective work after report-level NO-GO; allow ad-hoc read-only SELECT probes) while restoring fail-closed semantics for the gate's protected blast radius.

## Specification Links

Carried forward from `-001`; one entry added explicitly noting the state-after-GO distinction operationalized in IP-C.

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol observed. `bridge/INDEX.md` will be updated with the `REVISED: bridge/gtkb-implementation-gate-friction-hygiene-003.md` entry at the top of the document's version list.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside `E:\GT-KB`; no Agent Red commingling.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping in IP-D maps each Codex finding to concrete regression tests.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the proposal-vs-report lifecycle distinction (NEW after GO is a report, REVISED after GO is a superseded proposal) is itself an artifact-lifecycle trigger semantic; this proposal makes it mechanically explicit in the gate's chain walk.
- GOV-STANDING-BACKLOG-001 - the slice creates one tracking `work_item` (IP-E) per the standing-backlog authority.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - regex narrowing and packet-validation refinement preserve auditable artifact shape; only the false-positive surface narrows. The fail-closed contract is preserved.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix replaces over-broad heuristics with patterns aligned to actual SQL write operations AND to the proposal-vs-report bridge-chain semantic, AND to the proposal-vs-report-pending-vs-terminal state machine.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - three documented friction observations are a deterministic-plumbing defect signal; the fix belongs service-side, with conservative fail-closed defaults.
- `.claude/rules/codex-review-gate.md` § Mechanical Implementation-Start Gate - the rule the gate operationalizes; this proposal does NOT change the rule text, only the gate's false-positive surface AND the chain-walk state machine.
- `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start Authorization Metadata - contract preserved; IP-C clarifies the chain-walk semantic without widening the contract.
- bridge/gtkb-implementation-gate-friction-hygiene-002.md - Codex NO-GO addressed by this REVISED-1.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-015.md - Slice 3 implementation report documenting Frictions A, B, and C; carries forward as scope-input.
- bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-006.md - Slice 4 implementation report; "Implementation-Discovered Findings" section flags this slice's scope.
- `scripts/implementation_start_gate.py:62-69` - the live `MUTATING_COMMAND_RE` regex (target for IP-A and IP-B).
- `scripts/implementation_authorization.py` `_validate_packet` post-Slice-4 - target for IP-C.

## Prior Deliberations

- S349 self-diagnostic investigation (continuation, 2026-05-14 UTC).
- S350 owner direction: "Please continue with the 5 remaining Prime-actionable items" — this thread is the gate-friction-hygiene item.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion exchange answered "1 - File the hygiene slice now to formally close the friction class..." — the upstream scope authorization for this thread.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- DELIB-1469 - GT-KB self-measurement and self-improvement advisory.
- bridge/gtkb-implementation-gate-friction-hygiene-001.md - the proposal being revised.
- bridge/gtkb-implementation-gate-friction-hygiene-002.md - Codex NO-GO addressed here.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner AskUserQuestion answered "Commit Slice 3 only (mine), then revise next NO-GO" (Slice 3 commit complete; this REVISED-1 is the next NO-GO revision after governed-spec-retirement REVISED-2).
- 2026-05-14 UTC, S350: owner prompt "Please continue with the 5 remaining Prime-actionable items" — directs continuing the queue, of which the gate-friction-hygiene NO-GO is a member.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion answered "1 - File the hygiene slice now..." — upstream scope authorization.

No new owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-1 implements gate-implementation refinements under the same `.claude/rules/codex-review-gate.md` and `.claude/rules/file-bridge-protocol.md` rule-cited contracts. The F1 state-distinction fix is a stricter interpretation of the existing "packet fails closed on bridge status drift" clause; the F2 fail-closed sqlite restoration is a literal preservation of the existing fail-closed posture. No new requirements proposed.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation against the standing backlog. It creates exactly one tracking `work_item` (origin='hygiene', source_spec_id='SPEC-1662') identical in shape to Slice 3's `WI-3294` and Slice 4's `WI-3295`. The "friction class" framing groups three related defects (A, B, C) for a single review pass; it is not a batch over backlog items. No formal-artifact-approval packet is required for this proposal because no protected narrative artifact is edited; the single MemBase tracking-WI insert carries standing-backlog-visibility evidence via its `origin='hygiene'` + `source_spec_id='SPEC-1662'` fields.

## Changes from -001

### F1 fix (closes Codex `-002` F1): State-aware chain walk in IP-C

The IP-C `_validate_packet` chain walk now distinguishes four states-after-GO. Pseudocode:

```python
def _validate_packet(project_root, packet):
    # ... unchanged: hash check, expiry check ...
    entry = bridge_entry(project_root, str(packet["bridge_id"]))
    go_file = packet.get("go_file")

    found_go = False
    state_after_go = None  # first status seen while walking newest-first

    for status, path in entry.versions:  # newest-first order
        if path == go_file:
            if status == "GO":
                found_go = True
                break
            raise AuthorizationError(
                f"Bridge GO file status changed: {go_file} is now {status}"
            )
        # Entries newer than go_file in the chain
        if state_after_go is None:
            state_after_go = status  # capture the LATEST post-GO status only

    if not found_go:
        raise AuthorizationError(f"Bridge GO file not found in chain: {go_file}")

    # State-after-GO discrimination (F1 fix)
    if state_after_go is None:
        pass  # ALLOW: no post-GO entries; fresh implementation phase.
    elif state_after_go == "GO":
        pass  # Should not happen for a different file (would be Prime mis-filing);
              # ALLOW because the packet's go_file is still authoritative.
    elif state_after_go == "NO-GO":
        pass  # ALLOW: Loyal Opposition rejected a report; Prime may correct.
              # This is the original Friction C case Codex agreed is legitimate.
    elif state_after_go == "NEW":
        raise AuthorizationError(
            f"Post-implementation report at {entry.latest_path} is awaiting Loyal "
            f"Opposition review; additional mutations during review would invalidate "
            f"the report snapshot. Wait for VERIFIED or NO-GO before resuming work."
        )
    elif state_after_go == "VERIFIED":
        raise AuthorizationError(
            f"Bridge thread is VERIFIED (terminal at {entry.latest_path}); the "
            f"implementation phase for this proposal is closed. File a new bridge "
            f"proposal for further work on this surface."
        )
    elif state_after_go == "REVISED":
        raise AuthorizationError(
            f"Bridge GO superseded by REVISED proposal at {entry.latest_path}; "
            f"re-issue the implementation-authorization packet from the new GO."
        )

    # ... unchanged: project_authorization drift checks ...
```

The state-machine semantics:

| Latest status after GO | Decision | Rationale |
|---|---|---|
| (none / GO is latest) | ALLOW | Fresh implementation phase; packet authoritative. |
| NEW | DENY | Post-impl report pending LO review. Mutations would invalidate snapshot. |
| NO-GO | ALLOW | Verification NO-GO; Prime needs to correct. Original Friction C case. |
| VERIFIED | DENY | Terminal; implementation phase closed. |
| REVISED | DENY | Proposal superseded; packet's GO no longer authoritative. |

### F2 fix (closes Codex `-002` F2): sqlite stays default-block; narrow positive allowlist for literal-read SQL

IP-B is restructured. The `sqlite3` substring REMAINS in `MUTATING_COMMAND_RE` (no narrowing). A NEW positive-allow check is added that runs AFTER `_is_mutating_command` detects sqlite3 but BEFORE the gate decides to block:

```python
# In scripts/implementation_start_gate.py

SAFE_SQLITE_READ_RE = re.compile(
    # Match python sqlite3 invocations whose execute(...) argument is a literal
    # string starting with a read-only keyword (SELECT, PRAGMA, WITH, EXPLAIN).
    # Negative requirement: no executescript, executemany, .commit, or
    # write-keyword (INSERT/UPDATE/DELETE/REPLACE/CREATE/DROP/ALTER/TRUNCATE)
    # appears anywhere in the command.
    r"sqlite3\b.*?\.execute\(\s*['\"](?:SELECT|PRAGMA|WITH|EXPLAIN)\b[^'\"]*?['\"]",
    re.IGNORECASE | re.DOTALL,
)

SQLITE_WRITE_DISQUALIFIERS_RE = re.compile(
    r"\.executescript\(|\.executemany\(|\.commit\(|"
    r"\b(?:INSERT|UPDATE|DELETE|REPLACE|CREATE|DROP|ALTER|TRUNCATE)\b",
    re.IGNORECASE,
)


def _is_safe_sqlite_read(command: str) -> bool:
    """Return True iff the command is a literal-read sqlite probe.

    Required: matches SAFE_SQLITE_READ_RE (literal SELECT/PRAGMA/WITH/EXPLAIN
    inside an execute() call after a `sqlite3` reference).

    Disqualifying: any of executescript(, executemany(, .commit(, or a SQL
    write keyword appears anywhere in the command. A variable-sourced
    execute(sql) call does not match SAFE_SQLITE_READ_RE because its argument
    is not a literal string starting with a read keyword.
    """
    if not SAFE_SQLITE_READ_RE.search(command):
        return False
    return not SQLITE_WRITE_DISQUALIFIERS_RE.search(command)
```

In `_is_mutating_command`:

```python
def _is_mutating_command(command: str) -> bool:
    if not MUTATING_COMMAND_RE.search(command or ""):
        return False
    # sqlite3 default-block exemption: literal-read SELECT/PRAGMA/WITH/EXPLAIN
    # without any write disqualifier.
    if "sqlite3" in (command or "").lower() and _is_safe_sqlite_read(command):
        return False
    return True
```

The fail-closed posture:

- `python -c "import sqlite3; conn.execute('SELECT COUNT(*) FROM specifications').fetchone()"` → MUTATING_COMMAND_RE matches sqlite3; `_is_safe_sqlite_read` matches (literal SELECT, no disqualifier) → NOT mutating → ALLOW.
- `python -c "import sqlite3; sql=os.environ['SQL']; conn.execute(sql); conn.commit()"` → MUTATING_COMMAND_RE matches; `_is_safe_sqlite_read` finds no literal-read execute and finds `.commit(` disqualifier → MUTATING → BLOCK.
- `python -c "import sqlite3; conn.execute('INSERT INTO x VALUES (1)'); conn.commit()"` → MUTATING_COMMAND_RE matches sqlite3 AND `insert_` (via the `python\s+.*INSERT` alternation if INSERT keyword matches; even if not, the `.commit(` disqualifier blocks `_is_safe_sqlite_read`) → MUTATING → BLOCK.
- `python -c "import sqlite3; conn.executescript(create_sql)"` → `.executescript(` disqualifier blocks → MUTATING → BLOCK.
- `python -c "import sqlite3; conn.executemany(sql, rows)"` → `.executemany(` disqualifier blocks → MUTATING → BLOCK.

### IP-A: Unchanged (Codex did not flag)

The Friction A redirect-regex tightening from `-001` lands as-is. The new pattern `(?:^|[^>0-9&])>{1,2}(?!&)` correctly excludes stderr redirects (`2>/dev/null`, `1>file`) and `&>` patterns.

### IP-E: Unchanged (Codex did not flag)

The single tracking `work_item` insert lands as-is per `-001` IP-E.

## Proposed Scope (REVISED)

### IP-A: Friction A — redirect-tail tightening (unchanged from `-001`)

Modify `MUTATING_COMMAND_RE` in `scripts/implementation_start_gate.py`. Replace the redirect tail `(^|[^>])>{1,2}($|[^&])` with `(?:^|[^>0-9&])>{1,2}(?!&)`.

### IP-B (REVISED for F2): sqlite default-block preserved + literal-read allowlist

`MUTATING_COMMAND_RE` keeps the bare `sqlite3` substring (no narrowing). Add `SAFE_SQLITE_READ_RE`, `SQLITE_WRITE_DISQUALIFIERS_RE`, and `_is_safe_sqlite_read(command)` per F2 fix code above. `_is_mutating_command(command)` consults `_is_safe_sqlite_read` to exempt literal-read patterns.

### IP-C (REVISED for F1): state-aware chain walk

`_validate_packet` in `scripts/implementation_authorization.py` walks `entry.versions` newest-first, captures `state_after_go` as the FIRST post-GO status seen, then applies the discrimination table in the F1 fix section. The unchanged hash/expiry checks happen before the walk; the unchanged project_authorization drift checks happen after.

### IP-D (REVISED): Tests for each friction class with F1/F2 closure cases

In `platform_tests/scripts/test_implementation_start_gate.py`:

1. `test_gate_allows_python_minus_c_sqlite_select_read` — literal SELECT in execute(); gate returns `{}`.
2. `test_gate_allows_python_minus_c_sqlite_pragma_read` — literal `execute('PRAGMA table_info(x)')`; gate returns `{}`.
3. `test_gate_allows_python_minus_c_sqlite_with_read` — `execute('WITH cte AS (SELECT ...) SELECT ...')`; gate returns `{}`.
4. `test_gate_blocks_python_minus_c_sqlite_variable_sourced_execute` — `sql=os.environ['SQL']; conn.execute(sql)`; no literal-read match; gate blocks.
5. `test_gate_blocks_python_minus_c_sqlite_commit_after_select` — literal SELECT but also `.commit()` disqualifier present; gate blocks.
6. `test_gate_blocks_python_minus_c_sqlite_executemany` — `.executemany(sql, rows)`; gate blocks.
7. `test_gate_blocks_python_minus_c_sqlite_executescript` — `.executescript(sql)`; gate blocks.
8. `test_gate_blocks_python_minus_c_sqlite_literal_insert` — literal INSERT keyword; gate blocks.
9. `test_gate_allows_stderr_redirect_to_dev_null` — `python script.py 2>/dev/null`; gate returns `{}`.
10. `test_gate_allows_stderr_redirect_to_ampersand_two` — `cmd >&2`; gate returns `{}`.
11. `test_gate_blocks_data_redirect_to_file` — `cmd > .gtkb-state/out.txt` (in-root sandbox path); gate blocks.

In `platform_tests/scripts/test_implementation_authorization.py`:

12. `test_validate_packet_succeeds_with_no_post_go_entries` — chain: only GO at packet's go_file. Packet validates.
13. `test_validate_packet_succeeds_after_report_no_go` — chain: GO, NEW post-impl, NO-GO verification. `state_after_go="NO-GO"`. Packet validates (Friction C corrective case).
14. `test_validate_packet_fails_with_pending_new_after_go` — chain: GO, NEW post-impl. `state_after_go="NEW"`. Packet fails with "awaiting Loyal Opposition review".
15. `test_validate_packet_fails_with_verified_after_go` — chain: GO, NEW post-impl, VERIFIED. `state_after_go="VERIFIED"`. Packet fails with "VERIFIED (terminal)".
16. `test_validate_packet_fails_when_revised_supersedes_go` — chain: GO at proposal version, REVISED. Packet fails with "superseded by REVISED".
17. `test_validate_packet_fails_when_go_file_status_changed` — chain has the go_file as a non-GO status. Packet fails with "status changed".
18. `test_validate_packet_fails_when_go_file_not_in_chain` — packet references a `go_file` not present. Packet fails with "not found in chain".

Total: 18 tests covering Frictions A (3), B (5), C (7), plus 3 environment/structure tests. The 4 prior tests from `-001` IP-D §1-4 are kept conceptually; tests 5+ are the new F1/F2 closure cases.

### IP-E: Tracking work_item (unchanged from `-001`)

Insert one `work_items` row via `db.insert_work_item()`:

- id: `WI-NNNN` (next available; minted by querying `MAX(rowid)` or by the standard `_next_work_item_version`-adjacent helper).
- `origin='hygiene'`.
- `component='governance'` (the gate is governance infrastructure).
- `resolution_status='open'` (lifecycle just starting).
- `source_spec_id='SPEC-1662'`.
- `title='Implementation gate friction hygiene (regex tightening + proposal-GO chain walk + sqlite read allowlist)'`.
- `related_bridge_threads='gtkb-implementation-gate-friction-hygiene'`.
- `changed_by='prime-builder/claude/B'`.
- `change_reason='S349/S350 self-diagnostic friction-class closure; observations across Slice 3/4 + S350 parallel session establish recurring deterministic-plumbing defect; fix tightens MUTATING_COMMAND_RE redirect tail (Friction A), preserves sqlite default-block with literal-read allowlist for SELECT/PRAGMA/WITH/EXPLAIN (Friction B per Codex F2), and refines _validate_packet with state-aware chain walk distinguishing NEW-pending and VERIFIED-terminal from corrective NO-GO (Friction C per Codex F1)'`.
- `stage='created'` (default per docstring).

## Verification Plan

For Loyal Opposition verification of the eventual post-implementation report:

1. `python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py -v` — all existing tests still PASS plus the 18 new tests above PASS.
2. `python -m ruff check scripts/implementation_start_gate.py scripts/implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py` — zero errors.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-implementation-gate-friction-hygiene` — `preflight_passed: true`, `missing_required_specs: []`.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-implementation-gate-friction-hygiene` — zero blocking gaps, exit 0.
5. End-to-end smoke test:
   - Friction A: `python script.py 2>/dev/null` (in-root) under any active packet → gate allows.
   - Friction B safe: `python -c "import sqlite3; conn=sqlite3.connect('groundtruth.db'); print(conn.execute('SELECT COUNT(*) FROM specifications').fetchone())"` → gate allows.
   - Friction B unsafe: `python -c "import sqlite3; conn=sqlite3.connect('groundtruth.db'); conn.execute('INSERT INTO specifications (id, version) VALUES (?, ?)', ('X', 1)); conn.commit()"` → gate blocks.
   - Friction C corrective: simulate chain `GO, NEW, NO-GO`; packet validates.
   - Friction C pending-deny: simulate chain `GO, NEW`; packet fails with "awaiting Loyal Opposition review".
   - Friction C terminal-deny: simulate chain `GO, NEW, VERIFIED`; packet fails with "VERIFIED (terminal)".
6. Source inspection:
   - `MUTATING_COMMAND_RE` redirect tail uses `(?:^|[^>0-9&])>{1,2}(?!&)`.
   - `MUTATING_COMMAND_RE` still contains the bare `sqlite3` substring (default-block preserved).
   - `SAFE_SQLITE_READ_RE` and `SQLITE_WRITE_DISQUALIFIERS_RE` and `_is_safe_sqlite_read(command)` exist in `scripts/implementation_start_gate.py`.
   - `_is_mutating_command` consults `_is_safe_sqlite_read` to exempt literal-read sqlite commands.
   - `_validate_packet` in `scripts/implementation_authorization.py` walks `entry.versions` and applies the state-after-GO discrimination table.
7. MemBase tracking WI inserted with exact fields per IP-E.

## Risks and Rollback

- **F1 risk:** the state-machine assumes the bridge protocol's convention that NEW after GO is a post-impl report. If Prime mis-files a NEW that is actually a fresh proposal (not a report), the gate would DENY further mutation when it should ALLOW — but mis-filing is itself a protocol violation. Mitigation: protocol training + bridge-compliance-gate enforcement of section headings; this gate stays correct under correct protocol use. Rollback: revert IP-C to the prior `latest_status == "GO"` check.
- **F2 risk:** the literal-read allowlist is regex-based and may not see through some encodings (e.g., string concatenation `'SE' + 'LECT'`); the worst-case behavior is over-block (false-positive) rather than under-block (security regression). Mitigation: documented intent is "if in doubt, write the SELECT as a single literal string"; this is the dominant idiom in the GT-KB codebase. Rollback: revert IP-B to the prior bare-`sqlite3` substring without allowlist.
- **IP-A risk:** the redirect pattern may miss exotic data-redirect forms (e.g., `cmd 2>&1 > out`). Mitigation: test cases cover the common forms; remaining edge cases land as future bugs if reported. Rollback: revert IP-A to the existing redirect pattern.
- **General rollback:** all changes isolated to `scripts/implementation_start_gate.py` and `scripts/implementation_authorization.py`. No schema migrations, no protected-narrative-artifact edits, no MemBase mutations beyond the one tracking WI (which can also be retired via the upcoming governed-spec-retirement path when that lands).

## Sequenced Dependencies

This thread is sequenced AFTER Slice 4 of GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE (VERIFIED at `-007`) and Slice 3 (VERIFIED at `-016`, committed as `b14786a0` this session). Slice 4's named-packet cache + activate substrate is in place; this thread's implementation proceeds under that substrate. The governed-spec-retirement thread (REVISED-2 at `-005` filed concurrently) is parallel scope and does NOT block this thread.

## Recommended Commit Type

`fix:` — five targeted corrections to existing gate behavior across two source files; no new capability surface added (the friction-relief is achieved by narrowing the false-positive surface AND tightening the state-after-GO denial semantic). Diff stat will be net-small: regex tightening + new helper functions in one file, function refactor in another, plus expanded test coverage.

## Bridge-Compliance Self-Check

- Non-empty `## Specification Links` with flat bullets; no `###` sub-headings inside; no parenthetical heading.
- Non-empty `## Prior Deliberations`.
- Non-empty `## Owner Decisions / Input` citing the explicit AskUserQuestion answers and S350 directive.
- `target_paths` consistent with all planned writes; no protected narrative artifacts touched; `groundtruth.db` retained for the single MemBase tracking-WI insert.
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type` present.
- `## Clause Scope Clarification (Not a Bulk Operation)` section.
- Explicit `## Changes from -001` section with both F1 and F2 closures documented in detail.
- All paths under `E:\GT-KB`.
- F1 closure: state-aware chain walk distinguishes pending-NEW (DENY) and terminal-VERIFIED (DENY) from corrective-NO-GO (ALLOW). Explicit tests at IP-D §14-15.
- F2 closure: sqlite default-block preserved; literal-read allowlist via `SAFE_SQLITE_READ_RE` requires actual literal SELECT/PRAGMA/WITH/EXPLAIN AND no executescript/executemany/commit/write-keyword disqualifier. Variable-sourced SQL writes stay blocked. Explicit tests at IP-D §4-8.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
