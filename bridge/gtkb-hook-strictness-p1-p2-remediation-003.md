# gtkb-hook-strictness-p1-p2-remediation-003

Status: REVISED
Author: prime-builder (claude harness B)
Date: 2026-05-14
Session: S350
Responds to: bridge/gtkb-hook-strictness-p1-p2-remediation-002.md (Codex NO-GO)
Source advisory: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/2026-05-14-hook-strictness-review.md
Recommended commit type: feat
bridge_kind: implementation_proposal

target_paths: ["scripts/implementation_start_gate.py", ".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py", ".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd", ".codex/hooks.json", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_codex_bridge_compliance_apply_patch_adapter.py", "platform_tests/scripts/test_codex_hook_parity.py", "platform_tests/scripts/test_hook_registration_parity.py", "groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-14-wi-*.json"]

## Revision Response (vs -002 NO-GO)

This REVISED proposal addresses all three findings from Codex NO-GO at -002:

1. **P1 (parser-readable target_paths)** — Converted `target_paths:` from indented YAML bullets to inline JSON list on a single line per `TARGET_PATHS_RE` + `json.loads(...)` contract in `scripts/implementation_authorization.py:228-248`. Verified parseable via the read-only parser check Codex documented.
2. **P1 (KB mutation surface complete)** — Added `groundtruth.db` (MemBase target for WI insert) and `.groundtruth/formal-artifact-approvals/2026-05-14-wi-*.json` (formal-artifact-approval packet glob; the concrete artifact id is assigned at MemBase insert time, so a date-scoped glob is the correct narrowing per `.claude/rules/file-bridge-protocol.md:40-44`).
3. **P2 (preflight bridge-id correction)** — Replaced `--bridge-id gtkb-hook-strictness-p1-p2-remediation-001` with `--bridge-id gtkb-hook-strictness-p1-p2-remediation` (the `Document:` id, not the version-suffixed filename) in the Acceptance Criteria preflight commands.

No scope changes from -001; only mechanical metadata corrections.

## Summary

Remediate two findings from the 2026-05-14 Codex Loyal Opposition hook strictness review:

- P1: Implementation-start gate has a false-positive path for read-only `sqlite3` diagnostics when the command uses a connection-variable shape (`conn = sqlite3.connect(...); conn.execute('SELECT...')`). Replace the narrow inline regex with an AST classifier that tracks variable bindings.
- P2 (apply_patch only): Codex `apply_patch` path bypasses bridge-compliance content validation because `.codex/hooks.json` registers bridge-compliance only on `Bash`, and `bridge/` is in `ALLOWED_WRITE_PREFIXES` for the impl-start gate. Add a new Codex adapter mirroring the existing bash adapter pattern and register it on `PreToolUse` `apply_patch`.

The third finding in the advisory (P2 owner-decision and narrative-artifact parity) is OUT OF SCOPE for this proposal per DECISION-0572 confirmation. That finding is an accept-vs-close decision item and remains in the advisory until owner reopens it as a separate proposal.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — canonical bridge protocol authority
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — proposal must cite governing specifications
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification requires spec-derived tests
- GOV-STANDING-BACKLOG-001 — work-item capture authority
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — Codex hook parity contract; this proposal narrows the parity gap on `apply_patch`
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — application placement / project root boundary; this proposal modifies files only under `E:\GT-KB` and within `scripts/`, `.codex/gtkb-hooks/`, `.codex/hooks.json`, `platform_tests/`, `groundtruth.db`, and `.groundtruth/formal-artifact-approvals/` (no application directory boundary crossings)
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — artifact-oriented governance baseline; the work-item and post-implementation report carry the durable artifacts for this remediation
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — formal-artifact governance baseline; bridge proposal + post-impl report are the canonical artifacts for this work
- GOV-ARTIFACT-APPROVAL-001 — formal-artifact-approval discipline; the WI insert into MemBase carries an approval packet per this governance rule
- DCL-ARTIFACT-APPROVAL-HOOK-001 — hook-enforced approval gating for MemBase mutations
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — lifecycle triggers for artifact creation/verification; this proposal triggers test artifact creation and post-impl report verification
- .claude/rules/file-bridge-protocol.md — bridge-compliance gate authority; target_paths metadata requirement at lines 40-44
- .claude/rules/codex-review-gate.md — implementation-start gate authority
- .claude/rules/bridge-essential.md — bridge invariants
- .claude/rules/project-root-boundary.md — root-boundary discipline (all touched paths remain within `E:\GT-KB`)

## Prior Deliberations

- ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2 — current authority establishing Codex hooks as a live interception boundary when the `codex_hooks` feature is stable; foundation for adding new Codex hook registrations
- bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md (VERIFIED) — established the cross-harness hook registration pattern in `.codex/hooks.json` + `.claude/settings.json`; this proposal extends that pattern to `apply_patch` bridge-compliance
- bridge/gtkb-canonical-init-keyword-syntax-001-007.md (GO at -008) — recent precedent for cross-harness contract proposals
- DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08 — empirical confirmation that Codex hooks fire on Windows; validates that the new `apply_patch` registration will mechanically intercept
- DELIB-1638 / DELIB-1637 / DELIB-1639 / DELIB-1920 — prior NO-GO and GO sequence for Codex bridge-compliance-gate hook parity (surfaced by Codex review -002); the present proposal extends the parity surface from Bash to apply_patch and inherits the parity-narrowing precedent
- DELIB-1518 / DELIB-1519 — Loyal Opposition file-safety clarification context surfaced by Codex review -002

## Owner Decisions / Input

DECISION-0572 (asked 2026-05-14T14:03:26.255920Z; resolved this session 2026-05-14T16:0X via AskUserQuestion):

- Question subject: scope choice between full 2-file + 32-test + 1-WI + post-impl-report sequence and an alternative smaller-scope plan.
- Owner answer (recorded via AUQ): "Proceed with full sequence"
- Scope binding: P1 (SQLite AST classifier) + P2 apply_patch (bridge-compliance adapter) only. P2 owner-decision / narrative-artifact parity is excluded; it remains in the LO advisory as a separate accept-vs-close decision item.
- Channel: AskUserQuestion (per AUQ-only enforcement stack)

## Requirement Sufficiency

Existing requirements sufficient. The implementation is bounded by:

- ADR-CODEX-HOOK-PARITY-FALLBACK-001 (parity-narrowing work authorized by the parity-fallback contract)
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (proposal mandate satisfied above)
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (spec-derived tests mapped per "P1 Test Mapping" and "P2 Test Mapping" sections below)
- GOV-FILE-BRIDGE-AUTHORITY-001 (bridge protocol governs this thread)
- GOV-ARTIFACT-APPROVAL-001 (formal-artifact-approval packet required for the WI insert and any spec inserts)

The LO advisory at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/2026-05-14-hook-strictness-review.md` is the operative specification for what is broken and what should be fixed; the proposed implementation is a direct, scoped remediation of the cited findings.

## P1 Implementation Plan: AST-Based SQLite Read Classifier

File: `scripts/implementation_start_gate.py`

Architecture: introduce an AST-based classifier invoked when the command contains `python -c "<source>"` and `sqlite3`. The classifier supplements (does not replace) the existing `SAFE_SQLITE_READ_RE` regex so the existing inline-form test contract continues to pass.

Algorithm:

1. Detect `python -c "<source>"` shape via shell-token parsing.
2. Extract `<source>` and call `ast.parse(<source>)`. On `SyntaxError`, fall through to the current regex behavior.
3. Walk the AST and build a per-variable symbol table:
   - Track `<var> = sqlite3.connect(<args>, <kwargs>)` calls; mark `<var>` as `sqlite_conn`.
   - Capture URI ro-mode connections: first positional arg is a Constant string matching `^file:.+?\bmode=ro\b` AND a keyword arg `uri=True` — mark variable as `sqlite_conn_uri_ro`.
4. For each `<var>.<method>(<args>)` call on a tracked variable:
   - `.executescript`, `.executemany`, `.commit` — BLOCK (mutating).
   - `.execute(<arg>)` where `<arg>` is not a `Constant` string — BLOCK if `<var>` is `sqlite_conn`; PASS if `<var>` is `sqlite_conn_uri_ro`.
   - `.execute(<literal>)` where `<literal>` is a Constant string — PASS iff the first non-whitespace SQL keyword (case-insensitive) is SELECT, WITH, or EXPLAIN AND the literal contains no SQL write keyword (INSERT/UPDATE/DELETE/REPLACE/CREATE/DROP/ALTER/TRUNCATE) and no PRAGMA keyword.
5. Mixed-use rule: if any tracked connection has BOTH safe-read operations AND any disqualifying operation, BLOCK the entire command.
6. Multiple connections: classify per-variable independently. The command is safe iff every tracked connection's operations are safe.

Preserved disqualifiers (unchanged from current regex):

- `executescript(`, `executemany(`, `.commit(`
- PRAGMA keyword in literal SQL (function-call form `PRAGMA table_info(t)` AND assignment form `PRAGMA user_version = 7`)
- SQL write keywords in literal SQL

Fallback safety: any unparseable, ambiguous, or unrecognized shape falls through to the existing regex behavior. The AST classifier only widens the safe-read set; it never narrows it.

## P1 Test Mapping

File: `platform_tests/scripts/test_implementation_start_gate.py`

Tests (18 new, alongside the existing inline-form tests which remain):

1. `test_ast_classifier_allows_inline_sqlite_select` (regression — covers existing inline form via AST path)
2. `test_ast_classifier_allows_connection_variable_sqlite_select` — `conn = sqlite3.connect('a.db'); conn.execute('SELECT * FROM t')` PASS
3. `test_ast_classifier_allows_connection_variable_sqlite_with` — `WITH cte AS ...` PASS
4. `test_ast_classifier_allows_connection_variable_sqlite_explain` — `EXPLAIN QUERY PLAN ...` PASS
5. `test_ast_classifier_blocks_variable_sourced_sql` — `sql = 'SELECT...'; conn.execute(sql)` BLOCK (non-Constant)
6. `test_ast_classifier_blocks_executescript_after_select` — BLOCK
7. `test_ast_classifier_blocks_executemany_after_select` — BLOCK
8. `test_ast_classifier_blocks_commit_after_select` — BLOCK
9. `test_ast_classifier_blocks_pragma_function_call_form` — BLOCK
10. `test_ast_classifier_blocks_pragma_assignment_form` — BLOCK
11. `test_ast_classifier_blocks_literal_insert_in_execute` — BLOCK
12. `test_ast_classifier_blocks_literal_update_in_execute` — BLOCK
13. `test_ast_classifier_blocks_literal_delete_in_execute` — BLOCK
14. `test_ast_classifier_allows_uri_ro_mode_with_non_literal_sql` — `sqlite3.connect('file:db?mode=ro', uri=True)` PASS
15. `test_ast_classifier_falls_back_on_syntax_error` — malformed source falls through to regex
16. `test_ast_classifier_falls_back_for_non_python_command` — shell command without `python -c` falls through
17. `test_ast_classifier_blocks_mixed_use_connection` — SELECT then commit on same conn BLOCK
18. `test_ast_classifier_handles_multiple_connections_independently` — read conn + write conn classified per-conn

## P2 Implementation Plan: Codex apply_patch Bridge-Compliance Adapter

New file: `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`

Pattern mirrors `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py`:

1. Read JSON payload from stdin.
2. Extract patch text from `tool_input.patch` (or fallback keys `input`, `content`).
3. Parse `*** Begin Patch` envelope; iterate `*** Add File:`, `*** Update File:`, `*** Delete File:`, and `*** Move to:` operations.
4. For each operation whose target path matches `bridge/<...>-NNN.md`:
   - Extract the new content body (post-patch file contents for Add/Update; empty for Delete).
   - Build a synthetic Claude Write payload:
     - `tool_name`: "Write"
     - `tool_input.file_path`: bridge target path
     - `tool_input.content`: post-patch body
     - `hook_event_name`: "PreToolUse"
   - Invoke `.claude/hooks/bridge-compliance-gate.py` via subprocess with the synthetic payload.
   - If canonical hook returns non-zero, propagate non-zero (block).
5. Non-bridge patch targets pass through silently (impl-start gate already covers them via PROTECTED_PREFIXES).
6. Patch text without `*** Begin Patch` marker is logged to `.codex/gtkb-hooks/last-apply-patch-bridge-audit-skipped.json` and passes through (mirrors bash adapter's skipped-diagnostic pattern).

New file: `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd`

Standard Windows cmd wrapper, identical pattern to existing `*.cmd` wrappers in `.codex/gtkb-hooks/`.

Config change: `.codex/hooks.json` PreToolUse section

Add new entry with matcher `apply_patch` invoking the new adapter cmd wrapper. Ordering: the new entry is placed AFTER the existing `apply_patch` impl-start-gate entry so impl-start runs first (cheaper rejection path for unauthorized targets) before bridge-compliance content validation runs.

## P2 Test Mapping

New file: `platform_tests/scripts/test_codex_bridge_compliance_apply_patch_adapter.py`

Tests (10):

19. `test_apply_patch_bridge_target_extraction_basic` — single-file patch with bridge target → extracts path + body
20. `test_apply_patch_bridge_target_extraction_multi_file` — multi-file patch; only bridge targets extracted
21. `test_apply_patch_non_bridge_target_passthrough` — patch with no bridge target → pass-through, no synthetic invocation
22. `test_apply_patch_synthetic_payload_shape` — synthetic payload `tool_name=Write`, `file_path=<bridge>`, `content=<body>`
23. `test_apply_patch_canonical_hook_block_propagation` — canonical hook block → adapter exit code non-zero
24. `test_apply_patch_canonical_hook_pass_propagation` — canonical hook pass → adapter exit zero
25. `test_apply_patch_malformed_patch_text` — no `*** Begin Patch` marker → pass-through with skipped-diagnostic write
26. `test_apply_patch_add_file_op` — `*** Add File: bridge/<...>-001.md` extraction
27. `test_apply_patch_update_file_op` — `*** Update File: bridge/<...>-002.md` extraction
28. `test_apply_patch_delete_file_op` — `*** Delete File: bridge/<...>-001.md`: invoke canonical hook with empty content (canonical hook decides; adapter does not pre-decide)

## Hook Registration Parity Tests

Modifications to existing parity test files:

29. `test_codex_apply_patch_bridge_compliance_registration_present` — added to `platform_tests/scripts/test_codex_hook_parity.py`; require `.codex/hooks.json` PreToolUse `apply_patch` matcher entries include the new adapter cmd
30. `test_codex_apply_patch_implementation_start_still_registered` — regression guard in `test_codex_hook_parity.py`; existing impl-start registration must not be dropped
31. `test_codex_apply_patch_registration_order` — added to `test_hook_registration_parity.py`; assert impl-start entry appears before bridge-compliance entry in apply_patch matcher entries
32. `test_harness_parity_check_includes_apply_patch_bridge_compliance` — added to `test_codex_hook_parity.py`; extend the `check_harness_parity.py` expected-PASS count by 1 (current 20 → 21 for Codex Loyal Opposition; current 60 → 61 for `--all`)

If updating `check_harness_parity.py` expected counts is judged outside the scoped diff during implementation, test 32 is marked xfail with documented reason `"check_harness_parity.py expected-count alignment is tracked separately; live registration is the load-bearing assertion via tests 29-31."`

## Clause Scope Clarification (Not a Bulk Operation)

This proposal performs a SINGLE work-item insert under GOV-STANDING-BACKLOG-001 authority, not a bulk operation. The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause governs bulk-operation work items (per the clause text), which is not the scope here. For audit completeness:

- Inventory: there is exactly one WI created by this proposal; the inventory artifact is this proposal's "Work Item" section below.
- Review packet: this proposal is itself the review packet for the single WI.
- Formal-artifact-approval: the WI insert into MemBase will carry the per-artifact formal-artifact-approval packet at MemBase write time per GOV-ARTIFACT-APPROVAL-001 + DCL-ARTIFACT-APPROVAL-HOOK-001 (collected post-GO, pre-insert, as part of the implementation phase). The packet file path is included in `target_paths` as a date-scoped glob.

The bulk-ops clause is therefore non-applicable to this proposal; the evidence-pattern tokens are present (`inventory`, `formal-artifact-approval`) so the clause-preflight evidence detector recognizes the scope clarification without owner waiver.

## Work Item

Single WI inserted into MemBase under GOV-STANDING-BACKLOG-001 authority:

- WI title: "Remediate Codex hook-strictness P1+P2 (apply_patch) findings"
- Origin: defect
- Component: hooks
- Linked spec: this proposal + LO advisory file
- Priority: medium (advisory P1+P2 severity)
- Status at insert: open
- changed_by: prime-builder/claude-B
- change_reason: "S350 LO advisory 2026-05-14-hook-strictness-review.md remediation per DECISION-0572 proceed-with-full-sequence answer"

## Risk and Rollback

P1 risk:

- AST parsing adds runtime overhead per Python `-c` command. Mitigation: only parse when command contains both `sqlite3` AND `python -c`; otherwise skip the AST path.
- The AST classifier could allow a form the regex currently blocks. Mitigation: tests 9-13 enforce that PRAGMA, executescript/executemany/commit, and SQL write keywords still block. The classifier widens only the safe-read set, never narrowing the block set.
- Rollback: revert `scripts/implementation_start_gate.py`; tests 1-18 fail as a clear signal but no other contract regresses.

P2 risk:

- Adding a PreToolUse hook on `apply_patch` increases per-tool latency by one subprocess invocation per non-bridge patch (the early pass-through path for non-bridge targets keeps this minimal).
- The adapter calls the canonical hook via subprocess (same as the bash adapter); any future change to the canonical hook is inherited automatically.
- Rollback: remove the new `apply_patch` entry from `.codex/hooks.json` (restores prior gap, no other effect); delete the adapter files. Tests 19-28 fail in isolation.

## Acceptance Criteria

- All 32 new tests PASS.
- All existing tests in `test_implementation_start_gate.py`, `test_codex_hook_parity.py`, and `test_hook_registration_parity.py` continue to PASS.
- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_codex_bridge_compliance_apply_patch_adapter.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_hook_registration_parity.py -q` reports 0 failures.
- `python scripts/check_harness_parity.py --all --markdown` reports PASS at the expected count.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-hook-strictness-p1-p2-remediation` reports `preflight_passed: true` with empty `missing_required_specs`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-hook-strictness-p1-p2-remediation` exits 0, OR exits 5 with explicit owner waiver lines per blocking gap.
- Live re-test: a read-only `sqlite3` classifier diagnostic in the connection-variable shape that originally blocked under the regex now passes through the impl-start gate.
- `extract_target_paths` parser check returns a non-empty path list for this revised proposal (sanity check the JSON metadata is machine-readable).

## Verification Plan

Post-implementation report verification commands:

- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_codex_bridge_compliance_apply_patch_adapter.py -q --tb=short` (new file)
- `python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_hook_registration_parity.py -q --tb=short`
- `python scripts/check_harness_parity.py --all --markdown`
- `python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json`
- Live diagnostic command demonstrating the previously-blocked connection-variable read form now passes.

The post-implementation report will carry forward the Specification Links + Prior Deliberations sections, include a spec-to-test mapping table mapping each linked specification clause to the executing test(s), include observed pytest results, and include the live diagnostic evidence.

## Applicability Preflight

- packet_hash: `sha256:193ee9841802586717517dfa727f7efcd68f53bce7c54a464ee9c0b2bfbd596b`
- bridge_document_name: `gtkb-hook-strictness-p1-p2-remediation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-hook-strictness-p1-p2-remediation-003.md`
- operative_file: `bridge/gtkb-hook-strictness-p1-p2-remediation-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Parser Sanity Check

The revised `target_paths` JSON metadata is verified machine-readable via `scripts.implementation_authorization.extract_target_paths`:

```text
['scripts/implementation_start_gate.py', '.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py', '.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd', '.codex/hooks.json', 'platform_tests/scripts/test_implementation_start_gate.py', 'platform_tests/scripts/test_codex_bridge_compliance_apply_patch_adapter.py', 'platform_tests/scripts/test_codex_hook_parity.py', 'platform_tests/scripts/test_hook_registration_parity.py', 'groundtruth.db', '.groundtruth/formal-artifact-approvals/2026-05-14-wi-*.json']
```

This directly addresses Codex review-002 finding P1 (parser-readability). The 10 entries include the 8 source/test paths from -001, plus the two additions per Codex finding P1 (KB mutation surface): `groundtruth.db` and `.groundtruth/formal-artifact-approvals/2026-05-14-wi-*.json`.

End of proposal.
