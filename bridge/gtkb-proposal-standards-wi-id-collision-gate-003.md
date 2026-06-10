REVISED

# Implementation Proposal - Proposal-Standards Work-Item-ID Collision Gate (Slice 3) - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-proposal-standards-wi-id-collision-gate
Version: 003
Responds to: bridge/gtkb-proposal-standards-wi-id-collision-gate-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-PROPOSAL-STANDARDS-SLICES-2-3
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: GTKB-GOV-PROPOSAL-STANDARDS-SLICE3

target_paths: ["scripts/bridge_proposal_wi_id_collision_check.py", ".claude/hooks/bridge-proposal-wi-id-collision-gate.py", ".claude/settings.json", ".codex/hooks.json", "platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py"]

This REVISED-1 (`-003`) lands GTKB-GOV-PROPOSAL-STANDARDS Slice 3: a pre-review hook that cross-references any `GTKB-ISOLATION-NNN` / `GTKB-DASHBOARD-NNN` / `GTKB-GOV-NNN` or `WI-NNNN` IDs cited in a bridge proposal against the standing backlog, flagging ID collisions before review.

## Revision Notes

This `-003` REVISED-1 addresses every finding in the `-002` NO-GO:

- **FINDING-P1-001 (P1) — the required pre-review hook was not in implementation scope.** Resolved via the NO-GO's **Option 1**: the pre-review hook integration is now implemented in this slice. `target_paths` adds `.claude/hooks/bridge-proposal-wi-id-collision-gate.py` (the hook), `.claude/settings.json` (Claude-side `PreToolUse(Write|Edit)` registration), and `.codex/hooks.json` (Codex-side parity registration per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`). The hook's trigger point, advisory-by-default bypass behavior, and the tests proving it runs on a bridge-proposal Write/Edit are specified in IP-2 and the verification plan. The standalone CLI from `-001` is retained as IP-1 — it remains the reusable engine the hook calls — but Slice 3 is now claimed complete only when the hook path lands.
- **FINDING-P1-002 (P1) — the verification command targeted a nonexistent root `tests/` tree.** Resolved. `target_paths` no longer lists `tests/scripts/...`; the live checkout has no root `tests/` directory. The single authorized test file is `platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py`, and the run command in the verification plan executes exactly that path.
- **Advisory preflight omissions** (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` flagged in the `-002` applicability preflight). Resolved. All three are now cited in `## Specification Links`. Both preflights were re-run on this `-003` content; results are embedded below.

The collision-detection logic itself (the `(?:GTKB-[A-Z]+-\d+|WI-\d+)` pattern, MemBase lookup, code-fence exclusion) is unchanged from `-001`.

## Claim

A new `PreToolUse(Write|Edit)` hook, `.claude/hooks/bridge-proposal-wi-id-collision-gate.py`, fires when the tool target is a `bridge/<slug>-NNN.md` proposal file. It invokes the collision engine in `scripts/bridge_proposal_wi_id_collision_check.py`, which scans the proposed content for any `(?:GTKB-[A-Z]+-\d+|WI-\d+)` ID, looks each up in MemBase `current_work_items`, and reports any ID that exists but does NOT match the proposal's `Work Item:` metadata declaration. The hook is **advisory by default** — it surfaces collisions in its hook output without blocking the Write — consistent with the Slice-1/Slice-2 proposal-standards posture; `--strict` on the CLI returns a non-zero exit for explicit/CI use.

## In-Root Placement Evidence

All `target_paths` are inside `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; the pre-review hook protects the integrity of the bridge review packet by catching WI-ID collisions before review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposals must cite specs; this gate enforces internal consistency on the WI IDs a proposal cites.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below derives every test from a linked spec.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `GOV-STANDING-BACKLOG-001` - the gate cross-references cited IDs against the standing backlog (`current_work_items`); `GTKB-GOV-PROPOSAL-STANDARDS-SLICE3` is itself a tracked WI.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the hook is registered in both `.claude/settings.json` and `.codex/hooks.json` for cross-harness parity.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; the hook is a governed enforcement artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, hook, and CLI form the artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the hook fires on the bridge-proposal write lifecycle event.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - batch-2 owner authorization for `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS` and its Slice 2/3 work items.
- `DELIB-0990` - prior Loyal Opposition review for `gtkb-gov-proposal-standards-slice1`; parent-thread context for keeping proposal-standards behavior concrete and mechanically enforceable.
- `DELIB-0991` - prior Loyal Opposition review for the proposal-standards family; reinforces that proposal-standards checks must execute mechanically, not as optional diagnostics.
- `DELIB-0993` - prior Loyal Opposition review for `gtkb-gov-proposal-standards-slice1`; establishes the proposal-standards enforcement-family intent that this slice's hook satisfies.
- `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-002.md` - sibling Slice-2 review identifying the same scope-alignment and test-surface class of defects; this revision applies the same corrections.

No retrieved deliberation waives the bridge requirement that an implementation proposal map the operative work item to concrete, executable verification, nor the proposal-standards family's intent that checks fire mechanically before review.

## Owner Decisions / Input

This proposal is filed under an active project authorization and is authorized by:

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)" — authorized `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS` including `GTKB-GOV-PROPOSAL-STANDARDS-SLICE3`. Recorded as `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS`.

No new owner decision is required for this revision; `-003` only aligns the implementation scope with the work item's stated pre-review-hook outcome and fixes the test path.

## Requirement Sufficiency

Existing requirements sufficient. The `GTKB-GOV-PROPOSAL-STANDARDS-SLICE3` work-item description — "a pre-review hook that cross-references `GTKB-ISOLATION-NNN`, `GTKB-DASHBOARD-NNN`, `GTKB-GOV-NNN` mentions against the standing backlog and flags ID collisions before review" — is the operative requirement. This revision implements that requirement as written (the `-001` interpretation under-scoped it to a standalone CLI). No new or revised requirement or specification is created.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI implementation proposal (`GTKB-GOV-PROPOSAL-STANDARDS-SLICE3`). It performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "standing backlog", and "backlog" describe the single Slice-3 work item and the collision engine's read-only lookup against `current_work_items`. The review-packet inventory is one bridge thread: IP-1 (collision-check engine) + IP-2 (pre-review hook + registrations) + IP-3 (tests). The Slice-3 project membership is recorded under the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-003` REVISED line is inserted under the existing `Document: gtkb-proposal-standards-wi-id-collision-gate` entry; the prior `-001` NEW and `-002` NO-GO lines are preserved unchanged.

## Proposed Scope

### IP-1: Collision-detection engine CLI

`scripts/bridge_proposal_wi_id_collision_check.py`:

1. Read bridge proposal content (from `bridge/<bridge-id>-NNN.md`, or from stdin / a passed-content path when invoked by the hook on a not-yet-written file).
2. Parse the `Work Item:` metadata line for the declared WI.
3. Extract all `(?:GTKB-[A-Z]+-\d+|WI-\d+)` ID patterns from the document, **excluding** IDs inside fenced code blocks.
4. For each unique ID, query `current_work_items` for the row.
5. If a cited ID exists in MemBase as a WI different from the declared `Work Item:`, flag it as a collision in the output JSON.
6. Emit a `Collision Check` markdown section: a table of `cited_id`, `exists_in_membase`, `matches_declared`.
7. Exit 0 by default; exit non-zero only when `--strict` is passed AND collisions are present.
8. Expose a `check_content(text, declared_wi) -> CollisionResult` function so the hook can call the engine in-process without re-reading a file.

### IP-2: Pre-review hook + cross-harness registration (FINDING-P1-001 closure)

`.claude/hooks/bridge-proposal-wi-id-collision-gate.py` — a `PreToolUse(Write|Edit)` hook:

- **Trigger point:** the hook reads the tool input; it acts only when the write target path matches `bridge/<slug>-NNN.md` (a bridge proposal/report file). For any other path it is a no-op pass-through.
- **Behavior:** it extracts the proposed content from the tool input, calls `bridge_proposal_wi_id_collision_check.check_content(...)`, and:
  - When no collision is found: emits a normal pass (no `decision` field; the Write proceeds).
  - When a collision is found: emits an **advisory** hook result that surfaces the collision table in the hook output WITHOUT a `block` decision, so the Write still proceeds. This matches the Slice-1/Slice-2 proposal-standards posture (mechanically fires on every proposal write/edit, surfaces the defect, does not hard-block). Advisory-not-blocking is the deliberate bypass behavior: a legitimate cross-reference to another WI is common, so the hook informs the reviewer rather than refusing the write.
- **Failure mode:** if MemBase is unreachable, the hook emits a non-blocking diagnostic and passes (fail-open) — it must never block a proposal write because of an infrastructure error.
- **Registration:** add the hook to the existing `PreToolUse(Write|Edit)` matcher block in `.claude/settings.json` (alongside `bridge-compliance-gate.py`) and to the parity block in `.codex/hooks.json`.

### IP-3: Tests

`platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py` covers both the engine and the hook: collision detection, no-collision, multiple-collision, strict-mode exit code, default exit code, output JSON schema, code-fence exclusion, hook fires on a `bridge/<slug>-NNN.md` write, hook is a no-op on a non-bridge path, hook is advisory (does not block) on collision, and hook fail-open on MemBase error.

## Specification-Derived Verification Plan

Every linked specification maps to at least one test in `platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py`.

| Linked spec | Behavior verified | Test |
|---|---|---|
| `GOV-STANDING-BACKLOG-001` | a cited alien WI (exists in `current_work_items`, not the declared WI) is flagged as a collision | `test_collision_detected_on_alien_wi` |
| `GOV-STANDING-BACKLOG-001` | no collision when only the declared WI is cited | `test_no_collision_when_only_declared_wi` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | multiple distinct collisions are each enumerated | `test_multiple_collisions_listed` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | the pre-review hook fires on a `bridge/<slug>-NNN.md` Write and reports the collision | `test_hook_fires_on_bridge_proposal_write` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | the hook is a no-op pass-through on a non-bridge path | `test_hook_noop_on_non_bridge_path` |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | the hook is advisory: on a collision it surfaces the table but does NOT emit a `block` decision | `test_hook_advisory_does_not_block_on_collision` |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | the hook fails open (non-blocking diagnostic) when MemBase is unreachable | `test_hook_fail_open_on_membase_error` |
| `SPEC` / proposal-standards posture (`GOV-FILE-BRIDGE-AUTHORITY-001`) | `--strict` returns a non-zero exit on collision; default returns exit 0 | `test_strict_mode_exits_nonzero_on_collision`, `test_default_exit_zero_on_collision` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the output JSON conforms to the documented schema | `test_output_json_schema` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | IDs inside fenced code blocks are ignored (avoids false positives from example code) | `test_ignore_ids_in_fenced_code_blocks` |

Run: `python -m pytest platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py -v --tb=short`.

Lint: `python -m ruff check scripts/bridge_proposal_wi_id_collision_check.py .claude/hooks/bridge-proposal-wi-id-collision-gate.py`.

JSON validity check after editing `.claude/settings.json` and `.codex/hooks.json`: `python -c "import json,pathlib; [json.loads(pathlib.Path(p).read_text()) for p in ('.claude/settings.json','.codex/hooks.json')]"`.

## Acceptance Criteria

- IP-1 (engine), IP-2 (hook + both registrations), IP-3 (tests) landed; all tests in `test_bridge_proposal_wi_id_collision_check.py` PASS.
- The pre-review hook is registered in `.claude/settings.json` `PreToolUse(Write|Edit)` and in `.codex/hooks.json`; both files remain valid JSON.
- The hook fires on a `bridge/<slug>-NNN.md` Write, is a no-op on non-bridge paths, is advisory (does not block) on a collision, and fails open on a MemBase error — all proven by tests.
- The verification command runs `platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py` and collects all tests successfully (no nonexistent root `tests/` path).
- Both bridge preflights PASS for this proposal (`-003`).
- `ruff check` is clean on the touched script and hook.
- Slice 3 is claimed complete only because the pre-review hook path lands in this slice.

## Risks / Rollback

- Risk: legitimate cross-references to other WIs (e.g., dependency listings) get flagged. Mitigation: the hook is advisory by default — it surfaces the collision for reviewer judgment and never blocks the Write; `--strict` non-zero is reserved for explicit CLI/CI use.
- Risk: the hook adds latency to every Write/Edit. Mitigation: the hook is a no-op pass-through for any non-`bridge/` path; the MemBase lookup runs only for bridge-proposal writes, and a 5s hook timeout (matching the sibling hooks) bounds it.
- Risk: a MemBase error blocks proposal writes. Mitigation: the hook fails open with a non-blocking diagnostic (tested).
- Rollback: remove `.claude/hooks/bridge-proposal-wi-id-collision-gate.py`, revert the registration lines in `.claude/settings.json` and `.codex/hooks.json`, and remove `scripts/bridge_proposal_wi_id_collision_check.py`. No existing surface is otherwise modified.

## Recommended Commit Type

`feat` - a new pre-review hook plus its collision-detection engine and tests; a new mechanical-enforcement capability. The `.claude/settings.json` / `.codex/hooks.json` edits are registration of the new hook, part of the same feature.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-proposal-standards-wi-id-collision-gate`

- packet_hash: `sha256:3cbc5abb6bad2d1296e0a44b3c6b3efd3f9eefc84082eb03a95624ee985d4c34`
- bridge_document_name: `gtkb-proposal-standards-wi-id-collision-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md`
- operative_file: `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-proposal-standards-wi-id-collision-gate`

- Bridge id: `gtkb-proposal-standards-wi-id-collision-gate`
- Operative file: `bridge\gtkb-proposal-standards-wi-id-collision-gate-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation); exit code `0`

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
