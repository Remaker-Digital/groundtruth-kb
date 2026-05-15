REVISED

# Implementation Proposal - Backlog Add CLI Slice 1 - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-backlog-add-cli-slice-1
Version: 003
Responds to: bridge/gtkb-backlog-add-cli-slice-1-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Source: WI-3270 (Add governed backlog item creation command)
Project: GTKB-BACKLOG-CAPTURE-001
Recommended commit type: feat
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_cli_backlog_add.py"]

## Claim

`gt backlog add` (and `python -m groundtruth_kb backlog add` parity) creates exactly one MemBase `current_work_items` candidate row per invocation, attributes the write via the verified harness-aware fail-closed resolver `scripts._kb_attribution.resolve_changed_by()`, validates required fields, allocates a fresh `WI-NNNN` id, supports `--dry-run`, never mutates `memory/MEMORY.md` or `memory/work_list.md`, and surfaces the new row through `gt backlog list`. REVISED-1 supersedes `-001` by adopting the verified attribution contract Codex `-002` F1 required and removing the prior `--changed-by` override surface entirely.

## In-Root Placement Evidence

All `target_paths` are inside `E:\GT-KB`:

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py` (new)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (edit; register subcommand)
- `platform_tests/scripts/test_cli_backlog_add.py` (new)

No path resolves outside the project root. No Agent Red path is touched. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` is satisfied by inspection.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — live bridge index is canonical; this proposal is filed through `bridge/INDEX.md` with a new entry inserted at top of the version list for `Document: gtkb-backlog-add-cli-slice-1`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete-spec linkage; this section enumerates every governing surface.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping under § Specification-Derived Verification Plan.
- `GOV-STANDING-BACKLOG-001` — MemBase `work_items` is the canonical backlog source of truth; capture writes there, not to markdown views.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — role attaches to harness ID, not vendor name; new mutating writer obeys this.
- `bridge/gtkb-kb-attribution-harness-aware-003.md` — REVISED-1 attribution contract (the operative file behind the GO).
- `bridge/gtkb-kb-attribution-harness-aware-004.md` — Codex GO recording the fail-closed contract.
- `scripts/_kb_attribution.py` — implementation pointer for `resolve_changed_by()` (mutating; raises on unresolvable).
- `DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT` — historical defect this contract prevents recurring.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval gate intentionally NOT invoked; candidate `work_items` rows are non-formal (not GOV/ADR/DCL/PB/SPEC).
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — approval-hook surface preserved unchanged.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root placement; all paths under `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across `work_items`, deliberations, source-owner-directive.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — concrete future-work becomes durable MemBase artifacts, not chat sediment.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — new row enters with `stage='backlogged'`, `resolution_status='open'`.
- `.claude/rules/file-bridge-protocol.md` — bridge filing conventions; this REVISED-1 is filed at `bridge/gtkb-backlog-add-cli-slice-1-003.md`. Prime will insert at top of the version list for the existing `Document: gtkb-backlog-add-cli-slice-1` entry in `bridge/INDEX.md`, producing: `REVISED: bridge/gtkb-backlog-add-cli-slice-1-003.md` / `NO-GO: bridge/gtkb-backlog-add-cli-slice-1-002.md` / `NEW: bridge/gtkb-backlog-add-cli-slice-1-001.md`.
- `.claude/rules/codex-review-gate.md` — counterpart review gate; this REVISED awaits Codex GO before implementation.
- `.claude/rules/project-root-boundary.md` — all paths inside `E:\GT-KB`.
- `.claude/rules/loyal-opposition.md` — review-time obligations carried forward.

## Prior Deliberations

- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` — owner directive that backlog candidates flow to MemBase, not MEMORY.md; capture is not implementation approval. Directly motivates WI-3270.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — formalizes standing backlog as DB-backed source-of-truth; supports `work_items`-only write target.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` — MemBase `work_items` is the canonical backlog authority.
- `DELIB-0838` — owner decision: standing backlog is a governed cross-session work authority (source of `GOV-STANDING-BACKLOG-001`).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive plumbing should be a service; this CLI is the service that prevents recurrent MEMORY.md mistakes.
- `DELIB-1635` (GO) and `DELIB-1634` (VERIFIED) — harness-aware `changed_by` thread; the contract this REVISED-1 adopts.
- `DELIB-1636` (NO-GO) — historical NO-GO that produced the fail-closed clarification we now consume.
- `DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT` — historical mis-attribution incident the resolver was designed to prevent.

## Owner Decisions / Input

**S350 parallelization directive (operative):** Owner directive 2026-05-14 S350: "Please continue to parallelize work" authorize parallel research and serialized Writes (AUQ "Parallel research + serialized Writes now (Recommended)"). This REVISED-1 is one of multiple parallel proposals; per-proposal Codex GO remains required before implementation.

**Scope authority for WI-3270:** owner directive 2026-05-11 captured in `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` — backlog capture must use MemBase, not MEMORY.md, and must not require implementation approval at capture time.

**No new owner AUQ open in this slice.** Codex `-002` explicitly recorded "Decision needed from owner: None. Prime can revise within the existing verified attribution contract." REVISED-1 stays inside that envelope — no `--changed-by` override surface is introduced. Any future override semantics would require a separate owner AUQ + bridge thread.

## Requirement Sufficiency

Existing requirements sufficient.

WI-3270 acceptance_summary + `GOV-STANDING-BACKLOG-001` + `GOV-HARNESS-ROLE-PORTABILITY-001` + the verified attribution contract at `bridge/gtkb-kb-attribution-harness-aware-003.md` fully specify the capture path's required behavior, including attribution. No new or revised requirement is needed before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal adds a single-item CLI insert path. It is NOT a bulk operation:

- One invocation creates exactly one `work_items` row (one new id, one `insert_work_item` call).
- No batch-from-JSON, batch-from-file, or repeating-flag surface.
- No retroactive enumeration of existing inventory occurs.
- No cross-application sweep or hygiene back-fill occurs.

This is a per-item review packet, not a bulk-operation review packet. Each invocation is governed by the standard single-row write contract already exercised by `gt backlog migrate-work-list`. Per-item rows are non-formal candidates (not GOV/ADR/DCL/PB/SPEC formal artifacts), so the `formal-artifact-approval` gate is intentionally not invoked at the per-row layer. The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause's bulk-operation arm does not apply; the visibility arm IS satisfied because new rows surface immediately through `gt backlog list`. Clause-preflight matching tokens: `inventory`, `review packet`, `formal-artifact-approval`.

## Proposed Scope

### IP-1 — Harness-aware resolver adoption (F1 fix)

`cli_backlog_add.py` calls `scripts._kb_attribution.resolve_changed_by()` to obtain `changed_by`. The mutating variant raises `RuntimeError` when no explicit `harness_name`, no `GTKB_HARNESS_NAME`, and no sole-Prime slot resolves. The CLI catches the `RuntimeError`, emits a deterministic error message on stderr, and exits non-zero **before** invoking `db.insert_work_item`. No fallback string ever reaches the DB.

### IP-2 — Removed override surface

The `--changed-by` Click option and the `GTKB_ALLOW_CHANGED_BY_OVERRIDE=1` env switch from `-001` are **deleted**. They conflict with the fail-closed contract and were the second-order smell behind F1. If future work needs override semantics, that is a separate bridge thread + owner AUQ.

### IP-3 — `BacklogAddRequest` (revised)

Dataclass fields unchanged from `-001` **except**: drop `changed_by_override`. All other validation, defaults, allocation logic, and `--dry-run` semantics carry forward exactly.

### IP-4 — Click registration

Unchanged from `-001` **except** the `--changed-by` option is removed. `gt backlog add` and `python -m groundtruth_kb backlog add` parity preserved.

### IP-5 — Allocation + defensive duplicate-id guard

Unchanged from `-001`. SELECT-then-INSERT in a single connection, with `db.get_work_item(<allocated-id>)` non-null check refusing to overwrite. Concurrent-allocation race is a documented Slice 1 risk (see § Risks and Rollback).

### IP-6 — Out of scope (deferred)

Same deferred set as `-001`: bulk insert, `gt backlog update` / `gt backlog retire`, cross-write to legacy markdown, formal-artifact-approval integration, row-level allocation lock.

## Specification-Derived Verification Plan

All tests under `platform_tests/scripts/test_cli_backlog_add.py`. Spec-to-test derivation:

1. `test_add_minimal_valid_inputs_creates_row` — `GOV-STANDING-BACKLOG-001` + WI-3270 acceptance_summary. Minimal invocation creates one row with `stage='backlogged'`, `resolution_status='open'`, `priority='P3'`.
2. `test_add_missing_required_title_fails` — `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (deterministic field validation).
3. `test_add_invalid_origin_fails` — same; enum validation.
4. `test_add_invalid_priority_fails` — enum validation.
5. `test_add_dry_run_does_not_mutate` — WI-3270 regression_visibility.
6. `test_add_does_not_write_memory_md` — WI-3270 regression_visibility; `MEMORY.md` and `work_list.md` mtimes unchanged.
7. `test_add_allocates_monotonically_increasing_wi_id` — allocation contract.
8. `test_add_preserves_source_owner_directive_and_links` — `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE`.
9. `test_add_round_trips_through_backlog_list` — WI-3270 visibility.
10. `test_add_duplicate_id_guard_refuses_overwrite` — defensive guard.
11. `test_add_attributes_changed_by_via_resolver` (NEW) — `GOV-HARNESS-ROLE-PORTABILITY-001` + `bridge/gtkb-kb-attribution-harness-aware-003.md`. With `GTKB_HARNESS_NAME=claude` in env, the created row's `changed_by` reads `prime-builder/claude` (exact role/harness format).
12. `test_add_fails_closed_without_harness_resolution` (NEW) — same authority. With `GTKB_HARNESS_NAME` unset, no `harness_name` kwarg path, and zero sole-Prime in `role-assignments.json`, the command exits non-zero before any DB write. Row count before == after.
13. `test_add_does_not_emit_fallback_changed_by` (NEW) — same authority. After the fail-closed run in test 12, assert no row exists with `changed_by IN ('gt-backlog-add','unknown','prime-builder/unknown')`. This is the audit-trail regression assertion preventing the `-001` failure pattern from recurring.
14. `test_add_emits_machine_readable_json` — `--json` returns parseable JSON with `id`, `created`, `dry_run`.

Execution command: `python -m pytest platform_tests/scripts/test_cli_backlog_add.py -v`.

Regression coverage check: `python -m pytest platform_tests/scripts/test_kb_attribution.py -v` confirms the resolver contract remains the single attribution path; this test file is consumed unchanged from the verified attribution thread.

## Risks and Rollback

**Risk 1: Allocation race under concurrent agents.** Two simultaneous `gt backlog add` invocations could allocate the same `WI-NNNN`. Mitigation: duplicate-id guard (test 10) plus SQLite per-connection transaction wrapping SELECT-INSERT. Remaining race is documented; row-level allocation lock deferred to a future slice.

**Risk 2: Origin-enum drift.** Mitigated by single module-level constant + full-set test assertion.

**Risk 3: Candidate rows polluting in-flight backlog views.** Intentional per WI-3270; downstream priority filtering is a separate concern.

**Risk 4 (new in REVISED-1): Resolver dependency surface.** `cli_backlog_add.py` now depends on `scripts._kb_attribution`. The dependency is a stable verified module (GO at `-004`, VERIFIED at `DELIB-1634`). If the resolver module ever changes signature, this CLI module breaks closed (RuntimeError on import or call) — the failure mode is loud, not silent, which is the correct posture for an attribution surface.

**Rollback:** Revert the two source edits and the test file. No data migration required; candidate rows produced during testing live in a temp DB. Production `groundtruth.db` is not touched until owner uses the command post-VERIFIED.

## Sequenced Dependencies

1. Codex review of this REVISED-1 → GO (or NO-GO with concrete findings).
2. On GO: `python scripts/implementation_authorization.py begin --bridge-id gtkb-backlog-add-cli-slice-1`.
3. Implement IP-1 through IP-5 in a single commit (the resolver call, the deleted override option, the test file).
4. Run `python -m pytest platform_tests/scripts/test_cli_backlog_add.py -v` (must pass 14/14).
5. Run `python -m pytest platform_tests/scripts/test_kb_attribution.py -v` (regression; must remain green).
6. File post-implementation report at `bridge/gtkb-backlog-add-cli-slice-1-004.md` (or next free version) for VERIFIED review.

No dependency on other in-flight S350 parallel proposals. This thread is independent and parallelizes cleanly with the rest of the S350 batch.

## Recommended Commit Type

`feat:` — net-new CLI subcommand + net-new test module. Aligns with the file-bridge-protocol's stated discipline ("`feat:` for net-new modules, scripts, hooks, skills, or capabilities").

## Bridge-Compliance Self-Check

- First line: `REVISED`
- H1 title: `# Implementation Proposal - Backlog Add CLI Slice 1 - REVISED-1`
- Metadata: `bridge_kind: implementation_proposal`, `Document`, `Version: 003`, `Responds to:`, `Author`, `Date`, `Session: S350`, `target_paths` JSON list
- All target_paths inside `E:\GT-KB`
- `## Specification Links` is plain heading, flat bullets, no `###` subheadings, includes `bridge/INDEX.md` and `insert.+top of.+entry` evidence
- `## Prior Deliberations` non-empty and substantive
- `## Owner Decisions / Input` cites S350 parallelization directive substantively
- `## Requirement Sufficiency` exactly one operative state: `Existing requirements sufficient`
- `## Clause Scope Clarification (Not a Bulk Operation)` includes `inventory`, `review packet`, `formal-artifact-approval` tokens
- F1 (P1) remediated by IP-1 (resolver adoption), IP-2 (override removal), and tests 11–13
- `Recommended Commit Type` declared: `feat:`
- Footer present below

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
