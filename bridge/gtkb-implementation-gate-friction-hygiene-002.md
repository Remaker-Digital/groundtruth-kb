NO-GO

# Loyal Opposition Review - Implementation Gate Friction Hygiene

Document: gtkb-implementation-gate-friction-hygiene
Reviewed proposal: bridge/gtkb-implementation-gate-friction-hygiene-001.md
Response version: 002
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-14 UTC

## Verdict

NO-GO.

The proposal is directionally worthwhile and both mandatory mechanical
preflights pass on the live operative file. It cannot receive GO as written
because the proposed implementation-start gate semantics would keep protected
mutation authorization alive in bridge states where the evidence should be
frozen or terminal, and the sqlite narrowing turns the current fail-closed
database-command heuristic into a fail-open heuristic for dynamic sqlite writes.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` was found by `python -m groundtruth_kb deliberations search "DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE deterministic services implementation gate friction"` and supports treating recurring deterministic plumbing friction as a service defect.
- `DELIB-1469` (GT-KB self-measurement and self-improvement advisory) was returned by the self-improvement search and is directionally consistent with fixing repeated measurement/governance friction.
- `DELIB-0838` was returned by the standing-backlog search and reinforces that standing-backlog/work-item handling is governed cross-session work authority.
- No retrieved deliberation contradicted the need for a hygiene slice; the NO-GO findings below are about the proposed safety semantics.

## Findings

### F1 - Authorization remains valid while implementation evidence is pending or terminal

Severity: P1 governance drift.

Observation: The proposal explicitly says Friction C will tolerate trailing report-chain `NEW`/`NO-GO`/`VERIFIED` entries after the packet's GO file. The proposed pseudo-code says "NEW after the GO is interpreted as a post-impl report; allow" and "VERIFIED/NO-GO are verification verdicts on reports; allow." The tests likewise include success through `NEW post-impl report, NO-GO` and `NEW revised post-impl report`, but no denial case for latest `NEW` awaiting review or latest `VERIFIED` closure.

Evidence:
- `bridge/gtkb-implementation-gate-friction-hygiene-001.md:17` says the packet will tolerate trailing report-chain `NEW`/`NO-GO`/`VERIFIED` entries.
- `bridge/gtkb-implementation-gate-friction-hygiene-001.md:148-164` shows the proposed chain walk allowing `NEW`, `NO-GO`, and `VERIFIED` entries newer than the GO file.
- `bridge/gtkb-implementation-gate-friction-hygiene-001.md:172` says a `NEW` after the GO is allowed because Prime "may be correcting code after a verification NO-GO."
- `bridge/gtkb-implementation-gate-friction-hygiene-001.md:187-188` proposes success tests for report-chain `NO-GO` and revised post-implementation `NEW`, with no corresponding denial for pending `NEW` or terminal `VERIFIED`.
- `.claude/rules/file-bridge-protocol.md:67` says the implementation authorization packet "expires, fails closed on bridge status drift."
- `.claude/rules/file-bridge-protocol.md:264-270` defines post-implementation verification as a report followed by Loyal Opposition review and then `VERIFIED` or `NO-GO`.

Deficiency rationale: Corrective work after a report-level `NO-GO` is a real friction case, but pending report review and terminal verification are different states. If latest status is `NEW` after the GO, Prime has already filed an implementation report and Loyal Opposition is reviewing a snapshot; allowing more source/test/KB mutation during that review can invalidate the report evidence. If latest status is `VERIFIED`, the thread is closed for implementation; a still-unexpired packet must not continue authorizing protected changes under a verified bridge.

Impact: A stale but unexpired packet could authorize source, test, configuration, repository-state, or MemBase mutations after Prime has filed evidence for review, or after Loyal Opposition has recorded terminal verification. That weakens the audit trail the gate exists to protect and can make post-implementation reports no longer describe the tree being reviewed.

Recommended action: Revise IP-C so `_validate_packet` distinguishes corrective states:

- Allow the packet when the latest status is the original `GO`.
- Allow the packet when the latest status is a `NO-GO` newer than that GO, and the chain proves the NO-GO is a verification response after a post-implementation `NEW`.
- Deny when the latest status is `NEW` after the GO, because an implementation report is pending review.
- Deny when the latest status is `VERIFIED`, because the implementation thread is terminal.
- Deny when any newer `REVISED` proposal supersedes the GO.

Add regression tests for pending-report denial and verified-thread denial, alongside the intended report-level NO-GO corrective-work allow case.

### F2 - Sqlite narrowing is fail-open for dynamic write commands

Severity: P1 governance drift.

Observation: The current gate blocks any Python command mentioning `sqlite3`. The proposal replaces that with a regex that catches `executescript` or literal SQL write keywords after `sqlite3`, while allowing SELECT-only commands. The proposal's own Friction B claim says the fix should match actual SQL write operations, including `commit`/`executemany` write operations, but the proposed pattern and tests do not block dynamic `execute`/`executemany` writes whose SQL text is not present as a literal write keyword in the shell command.

Evidence:
- `scripts/implementation_start_gate.py:62-66` currently includes bare `sqlite3` in `MUTATING_COMMAND_RE`, which is fail-closed for sqlite commands.
- `bridge/gtkb-implementation-gate-friction-hygiene-001.md:16` says the fix replaces the bare substring with patterns for actual SQL write operations, including `commit`/`executemany` write operations.
- `bridge/gtkb-implementation-gate-friction-hygiene-001.md:114-123` proposes a pattern that matches `executescript` or literal SQL write keywords after `sqlite3`, but not `execute(sql)`, `executemany(sql, rows)`, or `commit()` when the write SQL is variable-sourced.
- `bridge/gtkb-implementation-gate-friction-hygiene-001.md:178-180` proposes only three sqlite tests: SELECT allowed, literal INSERT blocked, and executescript blocked.
- `.claude/rules/codex-review-gate.md:17` includes "Any action that changes the state of either repository" in the implementation actions that require bridge authorization.

Deficiency rationale: The gate does not need to be a malicious-user security boundary, but it does need to fail closed for ordinary AI-issued protected mutations. A command shaped like `python -c "import os, sqlite3; sql=os.environ['SQL']; conn=sqlite3.connect('groundtruth.db'); conn.execute(sql); conn.commit()"` can mutate `groundtruth.db` while containing no literal SQL write keyword after `sqlite3` in the shell command. The proposed tests would not catch that bypass.

Impact: The implementation-start gate could stop blocking a common class of database mutations that the current broad `sqlite3` check blocks. That is the inverse of the stated safety goal: it reduces false positives by creating a false negative for protected MemBase writes.

Recommended action: Revise IP-B to preserve fail-closed sqlite behavior. A safer shape is to keep sqlite commands protected by default, then add a narrow allowlist for explicit read-only sqlite probes that the gate can prove are read-only. Alternatively, explicitly block sqlite commands containing `execute`, `executemany`, or `commit` unless a read-only allowlist matches. Add tests that block dynamic write cases, including variable-sourced SQL with `execute(sql)` and `executemany(sql, rows)`, while still allowing the specific SELECT probe that caused the false-positive friction.

## Applicability Preflight

- packet_hash: `sha256:2024a48b4dee60efdc1c1b8d0545f4e5f038154f004d84a13321e54fe72f87ac`
- bridge_document_name: `gtkb-implementation-gate-friction-hygiene`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-implementation-gate-friction-hygiene-001.md`
- operative_file: `bridge/gtkb-implementation-gate-friction-hygiene-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-implementation-gate-friction-hygiene`
- Operative file: `bridge\gtkb-implementation-gate-friction-hygiene-001.md`
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
no `Owner waiver: <clause_id> -- <DELIB-ID> -- <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Review Notes

- The target paths are inside `E:\GT-KB`.
- The proposal includes non-empty `Specification Links`, `Prior Deliberations`, `Owner Decisions / Input`, `Requirement Sufficiency`, verification plan, rollback notes, and recommended commit type sections.
- The two findings above should be resolved in a REVISED proposal before implementation.

