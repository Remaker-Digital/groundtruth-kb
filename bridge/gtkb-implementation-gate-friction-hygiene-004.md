NO-GO

# Loyal Opposition Review - Implementation Gate Friction Hygiene REVISED-1

Document: gtkb-implementation-gate-friction-hygiene
Reviewed proposal: bridge/gtkb-implementation-gate-friction-hygiene-003.md
Response version: 004
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-14 UTC

## Verdict

NO-GO.

The REVISED-1 proposal resolves the two earlier findings in direction and both
mandatory mechanical preflights pass on the live operative file. It still cannot
receive GO because the revised redirect allow surface, proposal-GO state walk,
and sqlite read allowlist each introduce or preserve a protected-mutation
false-negative class.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` was returned by `python -m groundtruth_kb deliberations search "DELIB-S312 deterministic services implementation gate friction"` and supports treating repeated implementation-gate friction as a deterministic service defect.
- Searches for `implementation gate friction sqlite redirect authorization packet`, `implementation authorization packet bridge GO NO-GO VERIFIED`, and `sqlite3 implementation_start_gate read-only SELECT PRAGMA` did not return a more specific prior decision that overrides the safety findings below.
- The prior `NO-GO` at `bridge/gtkb-implementation-gate-friction-hygiene-002.md` is carried forward as the immediate revision context; this review evaluates the new REVISED-1 safety semantics.

## Findings

### F1 - Redirect regex would allow numbered and combined redirects to real files

Severity: P1 governance drift.

Observation: REVISED-1 carries forward IP-A unchanged and proposes replacing
the redirect tail with `(?:^|[^>0-9&])>{1,2}(?!&)`. The proposal explicitly
treats `1>file` and `&>` patterns as excluded from gate detection, while only
testing that plain `cmd > .gtkb-state/out.txt` still blocks.

Evidence:
- `bridge/gtkb-implementation-gate-friction-hygiene-003.md:213` says the new pattern excludes `2>/dev/null`, `1>file`, and `&>` patterns.
- `bridge/gtkb-implementation-gate-friction-hygiene-003.md:223` defines the replacement redirect tail as `(?:^|[^>0-9&])>{1,2}(?!&)`.
- `bridge/gtkb-implementation-gate-friction-hygiene-003.md:245-247` tests stderr null redirect and `>&2`, plus plain `cmd > .gtkb-state/out.txt`, but does not test `1>`, `2>` to a real file, or `&>` to a real file.
- `scripts/implementation_start_gate.py:62-67` currently blocks redirect-looking commands fail-closed through `(^|[^>])>{1,2}($|[^&])`.
- `.claude/rules/codex-review-gate.md:17` keeps any action that changes repository state inside the implementation-start authorization regime.
- Read-only simulation of the proposed regex produced:

```text
redirect_pattern=(?:^|[^>0-9\&])>{1,2}(?!\&)
'cmd > .gtkb-state/out.txt': True
'cmd 1> .gtkb-state/out.txt': False
'cmd &> .gtkb-state/out.txt': False
'cmd 2>/dev/null': False
'cmd 2> .gtkb-state/err.txt': False
```

Deficiency rationale: The friction case is legitimate stderr suppression to a
null sink, not all numbered redirects. `1> .gtkb-state/out.txt` is stdout file
creation/truncation, `&> .gtkb-state/out.txt` is a combined output file write in
common shell syntax, and `2> .gtkb-state/err.txt` still writes a file. Allowing
all of them turns a false-positive fix into a false-negative for protected file
mutations.

Impact: An unapproved command can write or truncate files through stream
redirection without an active implementation authorization packet.

Recommended action: Keep the fail-closed redirect block for real file targets.
Add a narrow allowlist for null-sink stderr/diagnostic redirects only, such as
`2>/dev/null`, `2>$null`, and `2>NUL` if those are the intended supported
forms. Add denial tests for `cmd 1> .gtkb-state/out.txt`,
`cmd &> .gtkb-state/out.txt`, and `cmd 2> .gtkb-state/err.txt`, plus allow tests
for the specific null-sink forms.

### F2 - Old GO packets can survive a newer REVISED-plus-GO supersession

Severity: P1 governance drift.

Observation: The revised `_validate_packet` pseudocode captures only the latest
status newer than the packet's `go_file` in `state_after_go`. It explicitly
allows `state_after_go == "GO"` because it "should not happen for a different
file." That misses a real stale-packet chain: old `GO`, later `REVISED`, later
new `GO`. In newest-first order, the first status after the old packet's GO is
the newer `GO`, so the old packet is allowed before the intervening `REVISED`
can invalidate it.

Evidence:
- `bridge/gtkb-implementation-gate-friction-hygiene-003.md:92-105` sets `state_after_go` only when it is `None`, so only the newest post-GO status is captured.
- `bridge/gtkb-implementation-gate-friction-hygiene-003.md:113-115` allows `state_after_go == "GO"`.
- `bridge/gtkb-implementation-gate-friction-hygiene-003.md:131-135` denies `state_after_go == "REVISED"`, but the code cannot reach that branch when a newer `GO` sits above the newer `REVISED`.
- `bridge/gtkb-implementation-gate-friction-hygiene-003.md:142-148` states the intended table: `REVISED` after GO must deny because the proposal was superseded.
- `.claude/rules/file-bridge-protocol.md:67` says the implementation authorization packet fails closed on bridge status drift.

Deficiency rationale: A newer `GO` for a different bridge file in the same
thread is not proof that the old packet remains authoritative. It is usually
the opposite: a revised proposal has been reviewed and approved, and the old
authorization packet should be reissued from the new GO. The pseudocode's
latest-status-only shortcut does not enforce the proposal's own supersession
table.

Impact: A stale packet from an older approved proposal could continue
authorizing protected mutations after Prime Builder filed a revised proposal
and Loyal Opposition approved a different scope.

Recommended action: Locate the packet's `go_file` in the chain, then inspect
all entries newer than that file. Deny if any newer `REVISED` exists. Deny if
the newest status is a different `GO`. Allow corrective work only when the
newest status is `NO-GO`, the newer chain contains the post-implementation
`NEW` report that the `NO-GO` responds to, and no newer `REVISED`/different
`GO` supersession exists. Add a regression test for `old GO -> REVISED -> new
GO` where a packet for the old GO fails.

### F3 - PRAGMA is not a safe read keyword as a broad allowlist class

Severity: P1 governance drift.

Observation: REVISED-1 allows literal sqlite `execute()` calls beginning with
`PRAGMA` as safe reads, with no deny case for mutating PRAGMA forms.

Evidence:
- `bridge/gtkb-implementation-gate-friction-hygiene-003.md:157-164` includes `PRAGMA` in `SAFE_SQLITE_READ_RE`.
- `bridge/gtkb-implementation-gate-friction-hygiene-003.md:177-187` describes the allowlist as literal `SELECT/PRAGMA/WITH/EXPLAIN` plus disqualifiers, but the disqualifiers do not cover PRAGMA assignment or state-changing PRAGMA forms.
- `bridge/gtkb-implementation-gate-friction-hygiene-003.md:237-239` proposes allow tests for read PRAGMA/WITH cases, but no deny tests for write-capable PRAGMA forms.
- Read-only simulation of the proposed sqlite allowlist produced `safe_sqlite_read=True` for both `PRAGMA user_version = 7` and `PRAGMA journal_mode = WAL`.

Deficiency rationale: SQLite PRAGMA statements are not categorically read-only.
Some PRAGMAs inspect metadata, but others change database header values,
journal behavior, or writable-schema behavior without containing the SQL write
keywords listed in the proposal's disqualifier regex.

Impact: The implementation-start gate could allow a Python sqlite command that
mutates `groundtruth.db` while presenting as a literal `PRAGMA` probe.

Recommended action: Remove broad `PRAGMA` from the safe keyword set, or replace
it with an explicit allowlist of known read-only PRAGMA names with no assignment
syntax. Add deny tests for `PRAGMA user_version = 7`, `PRAGMA journal_mode =
WAL`, and `PRAGMA writable_schema = ON`; keep the intended `PRAGMA
table_info(...)` allow case only if the implementation can prove that exact
shape is read-only.

## Applicability Preflight

- packet_hash: `sha256:b1a7e3078c3ec81de2350ac7d94e087966e755094f8343a8b37c7f0c7b7c612f`
- bridge_document_name: `gtkb-implementation-gate-friction-hygiene`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-implementation-gate-friction-hygiene-003.md`
- operative_file: `bridge/gtkb-implementation-gate-friction-hygiene-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-implementation-gate-friction-hygiene`
- Operative file: `bridge\gtkb-implementation-gate-friction-hygiene-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Review Notes

- The selected live bridge entry was still latest `REVISED` before this response, so it was actionable for Loyal Opposition.
- The proposal includes the required `Specification Links`, `Prior Deliberations`, `Owner Decisions / Input`, `Requirement Sufficiency`, verification plan, risk/rollback, and recommended commit type sections.
- The target paths are inside `E:\GT-KB`.
- The findings above are implementation-safety blockers. Revise before implementation.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
