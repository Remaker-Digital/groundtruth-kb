# Implementation Proposal - Implementation Gate Friction Hygiene

bridge_kind: implementation_proposal
Document: gtkb-implementation-gate-friction-hygiene
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S349 (continuation)
target_paths: ["scripts/implementation_start_gate.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "groundtruth.db"]

## Claim

Address three implementation-discovered friction classes that have been observed repeatedly across the S349 self-diagnostic umbrella work (Slice 3 `-009`, Slice 3 `-015`, Slice 4 `-006`, S350 parallel-session observation). Each class is a deterministic-plumbing defect in `scripts/implementation_start_gate.py` or `scripts/implementation_authorization.py` that triggers gate refusals on legitimate read-only operations or on legitimate corrective work after a report-level NO-GO. The fixes preserve the gate's fail-closed contract for actual protected mutations.

- **Friction A:** `MUTATING_COMMAND_RE`'s redirect-detection pattern `(^|[^>])>{1,2}($|[^&])` matches stderr redirects like `2>/dev/null` because the leading-char alternation `(^|[^>])` accepts a digit. The fix tightens the pattern to exclude stderr/numbered redirects.
- **Friction B:** the same regex's `sqlite3` substring matches any python command that imports or mentions sqlite3, including read-only `SELECT` queries. The fix replaces the bare substring with patterns that match actual SQL write operations (`INSERT`, `UPDATE`, `DELETE`, `REPLACE`, `CREATE`, `DROP`, `ALTER`, or `commit`/`executemany` write operations) while letting SELECT-only patterns through.
- **Friction C:** `_validate_packet` in `scripts/implementation_authorization.py` checks `entry.latest_status == "GO"`, which fails after a verification NO-GO on a post-implementation report — even though the proposal-chain GO at the packet's `go_file` is still authoritative for corrective implementation work. The fix walks the version chain to validate the packet's specific `go_file` is still GO and that no REVISED proposal has superseded it, while tolerating trailing report-chain `NEW`/`NO-GO`/`VERIFIED` entries.

The slice creates one MemBase `work_item` to track its own implementation (`origin='hygiene'`, `source_spec_id='SPEC-1662'`); `groundtruth.db` is in `target_paths` to authorize the single MemBase mutation.

## Why Now

The friction classes have been observed independently in:

- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-009.md` "Implementation-Discovered Friction" section (Friction A + Friction B; first reporting).
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-015.md` "Implementation-Discovered Friction" section (Friction A + Friction B + Friction C; carried forward).
- `bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-006.md` "Implementation-Discovered Findings" section (carried forward as Slice 5 scope-input).
- 2026-05-14 04:00Z observation from parallel S350 Prime session: "Gate fires false-positive on read-only SELECT again — same friction class flagged in Slice 4 follow-ons. Recording and moving forward."

Three independent observations across two sessions and two bridge umbrellas establish the friction class as recurring real-world cost. Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, repetitive AI work-around for deterministic plumbing defects is itself a defect; the fix belongs in the gate service.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol observed. `bridge/INDEX.md` will be updated with the `NEW: bridge/gtkb-implementation-gate-friction-hygiene-001.md` entry.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths under `E:\GT-KB`; no Agent Red commingling.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification; no placeholder text.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below maps each friction class to a concrete regression test.
- GOV-STANDING-BACKLOG-001 - the slice creates one tracking `work_item` per the standing-backlog authority.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - regex tightening and packet-validation refinement preserve auditable artifact shape; only the false-positive surface narrows.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix replaces over-broad heuristics with patterns aligned to actual SQL write operations and to the proposal-vs-report bridge-chain semantic.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - three documented friction observations are a deterministic-plumbing defect signal; the fix belongs service-side.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the proposal-vs-report lifecycle distinction (Friction C) is itself an artifact-lifecycle trigger semantic that this proposal makes explicit in the gate's chain-walk logic.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-015.md - Slice 3 implementation report documenting Frictions A, B, and C as scope-input.
- bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-006.md - Slice 4 implementation report; sequenced AFTER Slice 4 lands so the named-packet cache substrate is available during this implementation.

Advisory / cross-cutting:

- `.claude/rules/codex-review-gate.md` § Mechanical Implementation-Start Gate - the rule the gate operationalizes; this proposal does NOT change the rule text, only the gate's false-positive surface.
- `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start Authorization Metadata - contract preserved; Friction C clarifies the chain-walk semantic without widening the contract.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-14 UTC).
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "Nothing for me to act on unless you want me to..." answered "1 - File the hygiene slice now" - authorizes this proposal filing.
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-009.md, `-011.md`, `-015.md` - successive recordings of the friction class.
- bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-006.md - Slice 4 report; "Implementation-Discovered Findings" section flags this slice's scope.

## Owner Decisions / Input

- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion exchange answered "1 - File the hygiene slice now to formally close the friction class (gate regex tightening for `2>/dev/null` and `python -c \"...sqlite3...\"` reads + post-NO-GO-on-report corrective-work allowance)". This is the explicit scope authorization.

No new owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

The fixes are gate-implementation refinements that preserve the rule-cited contract in `.claude/rules/codex-review-gate.md` and `.claude/rules/file-bridge-protocol.md`. No new requirements proposed.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation against the standing backlog. It creates exactly one tracking `work_item` (origin='hygiene', source_spec_id='SPEC-1662'), identical in shape to tracking WIs from prior umbrella slices. The "friction class" framing groups three related defects (inventoried in § Why Now) for a single review pass; it is not a batch over backlog items. No formal-artifact-approval packet is required for this proposal because no protected narrative artifact is edited; the single MemBase tracking-WI insert carries the standing-backlog-visibility evidence via its `origin='hygiene'` + `source_spec_id='SPEC-1662'` fields, which are the same shape used by the Slice 3 `WI-3294` and Slice 4 `WI-3295` tracking WIs.

## Current Implementation Baseline

- `scripts/implementation_start_gate.py:62-69`:
  ```python
  MUTATING_COMMAND_RE = re.compile(
      r"\b("
      r"set-content|out-file|new-item|remove-item|move-item|copy-item|"
      r"apply_patch|git\s+(?:commit|reset|checkout|merge|rebase|tag|push)|"
      r"python\s+.*(?:write_text|open\(.+,\s*['\"]w|sqlite3|insert_|update_|delete_)"
      r")\b|(^|[^>])>{1,2}($|[^&])",
      re.IGNORECASE,
  )
  ```
  The `sqlite3` substring matches any python command mentioning sqlite3 (e.g. `python -c "import sqlite3; ... SELECT ..."`). The `(^|[^>])>{1,2}($|[^&])` pattern matches `2>/dev/null` because `2` is `[^>]` and ` ` is `[^&]`.
- `scripts/implementation_authorization.py` `_validate_packet` (post Slice 4): checks `entry.latest_status == "GO"` and `entry.latest_path == packet.go_file`. Both fail after a verification NO-GO on a post-impl report, even though the packet's `go_file` is still authoritative.

## Proposed Scope

### IP-A: Fix Friction A — stderr-redirect false-positive

Modify `MUTATING_COMMAND_RE` in `scripts/implementation_start_gate.py` to exclude numbered/stderr redirects:

```python
# Old redirect tail: (^|[^>])>{1,2}($|[^&])
# New: require leading char NOT be a digit or `>`, AND exclude `&>` patterns
# Replacement: (?:^|[^>0-9&])>{1,2}(?!&)
```

The new pattern:
- `(?:^|[^>0-9&])` — match start-of-string OR a character that is not `>`, not a digit, and not `&` (so `2>`, `1>`, `&>` do not match).
- `>{1,2}` — match one or two `>` characters (data redirect or append).
- `(?!&)` — negative lookahead to exclude `>&` patterns (e.g. `>&2`).

This narrows the false-positive surface while still catching genuine data redirects (`> file`, `>> log`, `cmd > out.txt`).

### IP-B: Fix Friction B — sqlite3-substring read-only false-positive

Replace the bare `sqlite3` substring in `MUTATING_COMMAND_RE` with patterns that match actual SQL write operations. The current alternation `(?:write_text|open\(.+,\s*['"]w|sqlite3|insert_|update_|delete_)` becomes:

```python
python\s+.*(?:
    write_text
    |open\(.+,\s*['"]w
    |\.executescript\(
    |sqlite3.*\b(?:INSERT|UPDATE|DELETE|REPLACE|CREATE|DROP|ALTER)\b
    |insert_
    |update_
    |delete_
)
```

This:
- Catches direct sqlite3 write calls via `\.executescript\(` and SQL-write keywords following `sqlite3` substring.
- Allows `python -c "import sqlite3; conn.execute('SELECT ...')..."` to pass without false-positive.
- Preserves catches for `db.insert_*`, `db.update_*`, `db.delete_*` method calls on Python KnowledgeDB API wrappers.

The DB writes still trip the gate when actually writing (via `INSERT`/`UPDATE`/`DELETE`/`REPLACE`/`CREATE`/`DROP`/`ALTER` SQL keywords or `executescript`). Reads pass through.

### IP-C: Fix Friction C — proposal-GO authoritative through report-NO-GO

Modify `_validate_packet` in `scripts/implementation_authorization.py` to walk the version chain instead of checking `latest_status`:

```python
def _validate_packet(project_root: Path, packet: dict[str, Any]) -> None:
    if packet_hash(packet) != packet.get("packet_hash"):
        raise AuthorizationError("Implementation authorization packet hash mismatch")
    if parse_iso(str(packet["expires_at"])) < now_utc():
        raise AuthorizationError("Implementation authorization packet has expired")
    entry = bridge_entry(project_root, str(packet["bridge_id"]))
    go_file = packet.get("go_file")
    # Walk the chain to validate go_file is still GO and not superseded by a
    # newer REVISED proposal. Trailing report-chain entries (NEW post-impl
    # report; VERIFIED/NO-GO verification verdicts) DO NOT invalidate the
    # proposal GO.
    found_go = False
    for status, path in entry.versions:
        if path == go_file:
            if status == "GO":
                found_go = True
                break
            raise AuthorizationError(f"Bridge GO file status changed: {go_file} is now {status}")
        # Entries newer than the GO file
        if status == "REVISED":
            raise AuthorizationError(
                f"Bridge GO superseded by REVISED proposal at {path}; re-issue packet from new GO"
            )
        # NEW after the GO is interpreted as a post-impl report; allow.
        # VERIFIED/NO-GO are verification verdicts on reports; allow.
    if not found_go:
        raise AuthorizationError(f"Bridge GO file not found in chain: {go_file}")
    project_authorization = packet.get("project_authorization")
    if isinstance(project_authorization, dict):
        # ... unchanged project-authorization drift checks
```

The semantic shift: "is the packet's specific GO still authoritative" replaces "is the latest INDEX status still GO". A REVISED proposal AFTER the GO is treated as superseding (correct: Prime should re-issue from the new GO). A NEW after the GO is treated as a post-impl report (allowed: Prime is in the implementation phase and may be correcting code after a verification NO-GO).

### IP-D: Tests for each friction class

Add to `platform_tests/scripts/test_implementation_start_gate.py`:

1. `test_gate_allows_python_minus_c_sqlite_select_read` — payload with `python -c "import sqlite3; print(conn.execute('SELECT 1').fetchall())"`; gate returns `{}`.
2. `test_gate_blocks_python_minus_c_sqlite_insert_write` — payload with `python -c "...sqlite3...INSERT INTO..."`; gate blocks.
3. `test_gate_blocks_python_minus_c_sqlite_executescript` — payload with `python -c "...sqlite3...executescript(...)"`; gate blocks.
4. `test_gate_allows_stderr_redirect_to_dev_null` — payload with `python script.py 2>/dev/null`; gate returns `{}`.
5. `test_gate_allows_stderr_redirect_to_ampersand_dash` — payload with `cmd >&2`; gate returns `{}` (stderr redirect, not data redirect).
6. `test_gate_blocks_data_redirect_to_file` — payload with `cmd > .gtkb-state/out.txt` (using an in-root sandbox path to satisfy `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`); gate blocks (data redirect, no auth packet).

Add to `platform_tests/scripts/test_implementation_authorization.py`:

7. `test_validate_packet_succeeds_when_proposal_go_unchanged_despite_report_no_go` — chain: GO at proposal version, NEW post-impl report, NO-GO verification. Packet for proposal-GO validates successfully.
8. `test_validate_packet_succeeds_when_proposal_go_unchanged_despite_revised_post_impl_report` — chain: GO at proposal version, NEW post-impl report, NO-GO, NEW revised post-impl report. Packet validates.
9. `test_validate_packet_fails_when_revised_proposal_supersedes_go` — chain: GO at proposal version, then REVISED at new version. Packet for old GO fails with "superseded by REVISED".
10. `test_validate_packet_fails_when_go_file_not_in_chain` — packet references a `go_file` not present in INDEX. Packet fails with "not found in chain".

### IP-E: Tracking work_item

Insert one `work_items` row via `db.insert_work_item()`:

- id: `WI-NNNN` (next available)
- `origin='hygiene'`
- `source_spec_id='SPEC-1662'`
- `title='Implementation gate friction hygiene (regex tightening + proposal-GO chain walk)'`
- `related_bridge_threads='gtkb-implementation-gate-friction-hygiene'`
- `changed_by='prime-builder/claude/B'`
- `change_reason='S349 self-diagnostic friction-class closure; three observations across Slice 3/4 + S350 parallel session establish recurring deterministic-plumbing defect; fix tightens MUTATING_COMMAND_RE and refines _validate_packet to honor proposal-GO authority through report-NO-GO cycles'`

## Tests

Per § IP-D above. Total: 10 new tests covering:
- Friction A: 3 tests (stderr redirect, ampersand redirect, data redirect still blocks).
- Friction B: 3 tests (SELECT allowed, INSERT blocked, executescript blocked).
- Friction C: 4 tests (proposal-GO authoritative through NEW report + NO-GO verification; REVISED supersedes; missing GO file fails).

## Verification Plan

For Loyal Opposition verification:

1. `python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py -v` — all existing tests still PASS plus 10 new tests PASS.
2. `python -m ruff check scripts/implementation_start_gate.py scripts/implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py` — clean.
3. Both mandatory bridge preflights pass for this bridge id; zero blocking gaps.
4. End-to-end smoke test: invoke `python -c "import sqlite3; conn=sqlite3.connect('groundtruth.db'); print(conn.execute('SELECT COUNT(*) FROM specifications').fetchone())"` under an active slice-irrelevant packet; gate allows. Invoke `python -c "import sqlite3; ...INSERT INTO ..."` under same packet; gate blocks. Invoke `cmd 2>/dev/null` chain; gate allows.
5. Source inspection:
   - `MUTATING_COMMAND_RE` redirect tail uses `(?:^|[^>0-9&])>{1,2}(?!&)`.
   - `MUTATING_COMMAND_RE` no longer matches bare `sqlite3` substring.
   - `_validate_packet` walks `entry.versions` searching for `packet.go_file`.

## Risks and Rollback

- **IP-A risk:** the new redirect pattern may miss exotic data-redirect forms (e.g. `cmd 2>&1 > out` reorderings). Mitigation: test cases cover the common forms; remaining edge cases land as future bugs if reported. Rollback: revert to the existing redirect pattern.
- **IP-B risk:** a python command that builds a write query string but doesn't execute it (e.g. `print("SELECT * FROM x")`) — the gate would still pass since no INSERT/etc. literal matches. That's correct behavior (no mutation). Rollback: revert to the bare `sqlite3` substring.
- **IP-C risk:** the chain walk allows NEW entries after the GO without distinguishing post-impl report from accidentally-mis-filed new proposal. Mitigation: REVISED entries (which are the actual proposal-supersede status) DO invalidate the packet; NEW entries are interpreted as report-chain by default per the documented bridge protocol. If a future session files a NEW proposal without going through REVISED (incorrect bridge usage), the gate would not catch it — but that's already a protocol violation outside this proposal's scope. Rollback: revert to `entry.latest_status == "GO"` check.
- **General rollback:** all changes isolated to `scripts/implementation_start_gate.py` and `scripts/implementation_authorization.py`. No schema migrations, no protected-narrative-artifact edits, no MemBase mutations beyond the one tracking WI.

## Sequenced Dependencies

This thread is sequenced AFTER Slice 4 of GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE (VERIFIED at `-007`). Slice 4's named-packet cache + activate substrate is in place; this thread's implementation proceeds under that substrate.

## Recommended Commit Type

`fix:` — three targeted corrections to existing gate behavior; no new capability surface added (only false-positive surface narrowed). Diff stat will be net-small: regex tightening in one file, function refactor in another, plus tests.

## Bridge-Compliance Self-Check

- Non-empty `## Specification Links` with flat bullets; no `###` sub-headings inside; no parenthetical heading.
- Non-empty `## Prior Deliberations`.
- Non-empty `## Owner Decisions / Input` citing the explicit AskUserQuestion answer.
- `target_paths` consistent with all planned writes; no protected narrative artifacts touched.
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type`.
- `## Clause Scope Clarification (Not a Bulk Operation)` section.
- All paths under `E:\GT-KB`.
- Concrete IPs, concrete tests, concrete spec-to-test mapping — no placeholders or "refined later" deferrals (heeding the Codex `-002` lesson on governed-spec-retirement).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
