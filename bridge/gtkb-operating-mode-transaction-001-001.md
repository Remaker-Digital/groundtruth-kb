NEW

# Operating-Mode Transaction Component — Slice 1

bridge_kind: implementation_proposal
Document: gtkb-operating-mode-transaction-001
Version: 001
Author: Claude Code (harness B, Prime Builder)
Date: 2026-05-14 UTC

## Source

Owner AUQ answer on 2026-05-14 selecting **Option A — "Project + impl proposal now (Recommended)"** in response to the investigation of the topology-misreport defect. The investigation surfaced that:

- Two harnesses are installed (`harness-state/harness-identities.json`: Codex=A, Claude=B).
- Both hold singleton role sets in `harness-state/role-assignments.json` (A=`["loyal-opposition"]`, B=`["prime-builder"]`) — that is the canonical multi-harness topology per `ADR-SINGLE-HARNESS-OPERATING-MODE-001`.
- `.claude/session/work-subject.json` stores `topology_mode: "single_harness"` (stale value left over from a prior single-harness configuration).
- `scripts/session_self_initialization.py:4129` reads `topology_mode` from `work-subject.json` as stored state rather than deriving it from the role-map.
- The 2026-05-13 role switch (recorded by `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md` ADVISORY) updated `role-assignments.json` but not `work-subject.json`, illustrating exactly the ad-hoc-file-edit anti-pattern that `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` was approved 2026-05-13 to prevent.

This proposal implements Slice 1 of a project that closes that gap.

## target_paths

Slice 1 authorized scope:

- `groundtruth-kb/src/groundtruth_kb/mode_switch/__init__.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py` (NEW)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py` (NEW — pure topology derivation logic, isolated from I/O for testability)
- `groundtruth-kb/src/groundtruth_kb/mode_switch/audit.py` (NEW — transaction-record write/read)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (MODIFY — register `gt mode` Click group with `set-role` subcommand)
- `scripts/session_self_initialization.py` (MODIFY — derive topology from live role-map at the call site near line 4129; preserve stored value as input but override with derived value when they disagree, emitting an in-payload corrective note)
- `scripts/workstream_focus.py` (MODIFY — `save_state` derives `topology_mode` from live role-map structure instead of inheriting the canonical-default value)
- `scripts/single_harness_bridge_dispatcher.py` (MODIFY — `_is_single_harness_topology_applicable` calls the shared derivation function so dispatcher and startup share one algorithm)
- `tests/groundtruth_kb/test_mode_switch_transaction.py` (NEW)
- `tests/scripts/test_session_self_initialization_topology_derive.py` (NEW)
- `.gtkb-state/mode-switches/.gitkeep` (NEW — audit-trail directory placeholder; transaction records land at `.gtkb-state/mode-switches/<YYYYMMDD-HHMMSSZ>-<txid>.json`)
- `.claude/rules/operating-role.md` (MODIFY — document `gt mode set-role` as the canonical write path; mark direct edits to `role-assignments.json` and `work-subject.json` as deprecated/non-conformant unless invoking the transaction component)

All paths are in-root under `E:\GT-KB\`. No `applications/**` paths and no Agent Red files are touched.

Out-of-scope for Slice 1 (deferred to future slices in the same project):

- Slice 2: SessionStart hook reads `.gtkb-state/mode-switches/pending/` and applies pending transactions at next-session-initialization (the spec's next-session-effectiveness requirement; Slice 1 applies transactions immediately, which is the spec's "MAY" path).
- Slice 3: Wrap existing imperative role-management call sites (e.g., `scripts/harness_roles.set_harness_role`) to invoke the transaction component internally rather than write directly.
- Slice 4: Migrate `topology_mode` storage out of `work-subject.json` entirely (currently we keep it but always overwrite with the derived value).

## Specification Links

- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — primary spec being implemented (approved 2026-05-13 via owner AUQ; packet at `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json`; `full_content_sha256` `f5311c8844a89b17e906cc022415aa39fd1b48eeaa9f7ea774bd068f736c99b5`).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — GT-KB root boundary. Cited because the proposal text contrasts this GT-KB-platform work with the separate Agent Red project to clarify scope. All Slice 1 paths are in-root; audit-trail directory `.gtkb-state/mode-switches/` is in-root; no `applications/**` paths touched; no Agent Red files referenced as live artifacts.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — topology decision; defines that role-set cardinality determines topology (singleton → multi-harness, multi-element → single-harness).
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` — single-harness dispatcher behavior contract; depends on correct topology classification.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — wake-substrate constraint; doctor reports applicability based on topology.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — roles attach to harness IDs, not vendor names.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — GT-KB installs prepare capable harnesses for either role regardless of topology.
- `GOV-ACTING-PRIME-BUILDER-001` — legacy `acting-prime-builder` value READ-accepted, SET-rejected; transaction component must enforce SET vocabulary.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal is filed under the live bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal must cite governing specs (this section).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must execute spec-derived tests against implementation (see Specification-Derived Test Plan below).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — work, decisions, and outcomes preserved as durable artifacts; audit records are the artifact form for mode-switch transactions.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across artifacts; transaction records link to the role-map state they produced.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle visibility; transaction records carry effective-at timestamps.
- `.claude/rules/operating-role.md` — durable operating-role assignment; role-set schema is the active runtime schema this proposal honors.
- `.claude/rules/operating-model.md` — operating model §1 (operating-mode terminology) and §2 (canonical terminology); the transaction component is the deterministic path the operating model anticipates.
- `.claude/rules/canonical-terminology.md` — load-bearing topology terms (`single-harness operating mode`, `harness identity`, `role assignment`, `role set`).
- `.claude/rules/file-bridge-protocol.md` — bridge file naming, INDEX entry placement, and mandatory subsections honored by this proposal.
- `.claude/rules/codex-review-gate.md` — review gate this proposal must pass before implementation.
- `.claude/rules/project-root-boundary.md` — root boundary rule; all Slice 1 paths comply.

## Prior Deliberations

- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` (S347, 2026-05-13) — owner-approved project-scoped implementation authorization model. This proposal honors that model: it proposes a named project (`PROJECT-GTKB-OPERATING-MODE-TRANSACTION-001`) that owner may separately authorize, while per-proposal Loyal Opposition review, target-path scoping, and spec-derived testing remain required.
- `DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION` (S346, 2026-05-13) — clarified that prior spec-creation pre-authorization was scoped, not standing. `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` was approved under this clarified scope.
- `DELIB-0877` (2026-04-22) — owner directive establishing harness topology awareness as a first-class concern in GT-KB. Originating decision for the topology framing this proposal completes.
- `DELIB-1511` [no_go, S310] — Loyal Opposition Review history for the single-harness bridge dispatcher work. NO-GO trail informs the test surface this proposal must cover (the dispatcher already correctly derives topology from role-set cardinality at `scripts/single_harness_bridge_dispatcher.py:162`; this proposal extends the same derivation logic to the startup payload + adds the missing transaction surface).
- `DELIB-1405` / `DELIB-1406` (VERIFIED bridge threads for operating-model slice-0 and slice-1) — established the canonical operating-model artifact (`.claude/rules/operating-model.md`) whose terminology this proposal honors.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330) — separate-but-related topology decision; cited for vocabulary continuity (project root boundary preserved; this work is GT-KB platform, not the Agent Red application).
- ADVISORY `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md` (2026-05-13) — records the role switch that produced the current drifted state. Classification `monitor`; remains in place as audit evidence and is the concrete defect this proposal closes by providing a deterministic write path for future switches.

## Owner Decisions / Input

- 2026-05-13 owner AUQ approving `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` — approval packet at `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json` (`approval_mode: approve`, `approved_by: owner`, `presented_to_user: true`, `transcript_captured: true`). This is the standing authority for implementing the spec.
- 2026-05-14 owner AUQ in this session — "How should I proceed with the topology-misreport flaw and SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 implementation?" answered "Project + impl proposal now (Recommended)". This authorizes filing this proposal and creating the implementing project. It does NOT authorize implementation work itself; that requires Codex `GO` and a current implementation-start authorization packet (`python scripts/implementation_authorization.py begin --bridge-id gtkb-operating-mode-transaction-001`) before any protected mutation.
- No further owner approval is requested by this proposal. Owner-directed protected-artifact mutations during implementation (e.g., `.claude/rules/operating-role.md` edits) will collect per-artifact formal-artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001` at implementation time.

## Requirement Sufficiency

**Existing requirements sufficient.** `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` was approved 2026-05-13 with an explicit acceptance-criteria list (six bullets). The companion specs (`ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `.claude/rules/operating-role.md` § Role Set Schema, `.claude/rules/operating-role.md` § Backward Compatibility) provide the topology-derivation algorithm and the SET/READ vocabulary the transaction component must enforce. No new or revised requirement is required before implementation.

## Claim

`SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` mandates a deterministic component or service API for bridge-configuration and operating-mode switch requests; the component must validate against authoritative role/bridge/session-state artifacts; record auditable transaction evidence; and apply at session initialization. The spec also directs agents to use the component rather than ad-hoc direct edits.

This proposal implements Slice 1 of that requirement: a Click-registered `gt mode set-role` CLI surface backed by a pure-Python `groundtruth_kb.mode_switch` module that performs the validated atomic write of `harness-state/role-assignments.json` and `.claude/session/work-subject.json` plus an audit record under `.gtkb-state/mode-switches/`. Topology is computed by a single source of derivation (`mode_switch.derive.topology_from_role_map`) which the startup payload also consumes, eliminating the stored-vs-derived drift class. The Slice 1 implementation applies transactions immediately (mid-session); Slice 2 will add next-session-initialization application (the spec's explicit MUST path) once the immediate-apply path is stable.

All changed active GT-KB artifacts are under `E:\GT-KB`. This bridge file is filed under `E:\GT-KB\bridge\`, and the matching `Document:` / `NEW:` entry is added at the top of `bridge/INDEX.md`. The audit-trail directory `.gtkb-state/mode-switches/` is in-root.

## Slice 1 Scope

Five deliverables:

1. **Pure derivation function** at `groundtruth_kb.mode_switch.derive.topology_from_role_map(role_map: dict) -> str`. Returns one of `{"single_harness", "multi_harness"}`. Single-harness iff the role map has exactly one harness ID whose role-set contains BOTH `prime-builder` AND `loyal-opposition`. Anything else (including the empty role map, malformed role map, or any record with a singleton role-set) returns `multi_harness`. This mirrors the existing logic at `scripts/single_harness_bridge_dispatcher.py:162` (`_is_single_harness_topology_applicable`) — the proposal does NOT duplicate the dispatcher's logic; instead, it extracts the shared algorithm into the new module and refactors the dispatcher to call it, keeping byte-identical applicability semantics that `tests/scripts/test_cross_harness_bridge_trigger.py` already exercises.

2. **Transaction component** at `groundtruth_kb.mode_switch.transaction.apply_role_switch(harness_id_or_name: str, role: str, *, change_reason: str, applied_at: datetime | None = None) -> TransactionResult`. Steps:
   - Validate `role` against `VALID_ROLES_FOR_WRITE` (rejects `acting-prime-builder`).
   - Resolve harness ID from name via `scripts.harness_identity.resolved_harness_id`.
   - Read current `role-assignments.json` and `work-subject.json`.
   - Compute new role-map applying the same demotion semantics as `harness_roles.set_harness_role` (assigning Prime to one harness demotes all others to LO).
   - Derive new topology via `derive.topology_from_role_map`.
   - Write audit record at `.gtkb-state/mode-switches/<timestamp>-<uuid>.json` FIRST (failure-leaves-no-state-mutation invariant).
   - Atomically write `role-assignments.json` (via `harness_roles.write_role_assignments`).
   - Atomically write `work-subject.json` with derived `topology_mode` (via a new helper that writes the canonical fields directly, bypassing `workstream_focus.save_state`'s focus-only semantic).
   - Return `TransactionResult(audit_path, role_map_after, work_subject_after)`.

3. **Click CLI** at `gt mode set-role --harness <name|id> --role <prime-builder|loyal-opposition> [--reason <text>]`. Calls `transaction.apply_role_switch`. Exit code 0 on success; non-zero with stderr explanation on validation failure or any I/O error. Prints the audit-record path to stdout on success for the caller to record.

4. **Startup topology derivation** in `scripts/session_self_initialization.py` at the line currently reading `topology_mode = str(workstream.get("topology_mode") or "single_harness")` (around line 4129): replace with a call to `groundtruth_kb.mode_switch.derive.topology_from_role_map(role_map)` where `role_map` is loaded via `scripts.harness_roles.load_role_assignments`. When the derived value disagrees with the stored value in `workstream`, emit a one-line corrective note in the startup payload's `### Configuration` section (`"- Stored topology_mode was X; derived topology from live role-map is Y; using derived."`) and use the derived value. This makes the misreport self-correcting at next session-init even before Slice 2 lands.

5. **`workstream_focus.save_state` topology recompute**. `save_state` writes the canonical default `topology_mode` value rather than the role-map-derived value. Modify to call `derive.topology_from_role_map` on the live role-map and persist the derived value. Keeps `save_state`'s focus-only API surface intact (no signature change), but eliminates the silent topology-mode reset class.

## Implementation Plan

Ordered steps, each independently testable:

1. Create `groundtruth-kb/src/groundtruth_kb/mode_switch/` package with `__init__.py`, `derive.py`, `audit.py`, `transaction.py` (skeletons + docstrings). Unit-test `derive.topology_from_role_map` against the role-map fixtures used by `test_cross_harness_bridge_trigger.py` to prove byte-identical applicability semantics.
2. Implement `audit.write_transaction_record` returning the path. Test: writes valid JSON with required fields; refuses overwrite; uses UTC timestamps.
3. Implement `transaction.apply_role_switch`. Test: validation rejections; demotion semantics; atomic-write ordering (audit-first then state files); idempotency on same-role re-application.
4. Add `gt mode set-role` Click subcommand to `groundtruth-kb/src/groundtruth_kb/cli.py`. Test via `CliRunner`.
5. Refactor `scripts/single_harness_bridge_dispatcher.py:_is_single_harness_topology_applicable` to call `derive.topology_from_role_map` for the shared algorithm. Regression-test against the existing dispatcher tests at `tests/scripts/test_single_harness_bridge_dispatcher.py` and the cross-harness trigger tests.
6. Modify `scripts/session_self_initialization.py` to derive topology at the call site near line 4129. Test: when role-map and stored topology agree, payload matches today; when they disagree (deliberately mismatched fixture), payload uses derived value and shows the corrective note.
7. Modify `scripts/workstream_focus.save_state` to write derived topology. Test: round-trip; legacy-stored-mismatch is overwritten.
8. Update `.claude/rules/operating-role.md` to document `gt mode set-role` as the canonical write path and mark direct edits as deprecated. This is a protected narrative artifact — implementation will collect a formal-artifact-approval packet per `GOV-ARTIFACT-APPROVAL-001` and route the Write through `narrative-artifact-approval-gate.py`.
9. Create project `PROJECT-GTKB-OPERATING-MODE-TRANSACTION-001` in MemBase via the projects skill and link `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` as the implementing work item (resolves the WI orphan flagged in `gtkb-backlog-hygiene-bundle-s349` Finding 4).
10. File implementation report; Codex VERIFIES against the spec-to-test mapping below.

## Specification-Derived Test Plan

Mapping from `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` acceptance criteria to executable tests:

| Acceptance criterion (verbatim from spec) | Test file | Test function | Command |
|---|---|---|---|
| "There is a deterministic component or service API for bridge-configuration and operating-mode switch requests." | `tests/groundtruth_kb/test_mode_switch_transaction.py` | `test_apply_role_switch_returns_transaction_result` | `python -m pytest tests/groundtruth_kb/test_mode_switch_transaction.py::test_apply_role_switch_returns_transaction_result -v` |
| "The component validates the requested switch against the authoritative role, bridge, and session-state artifacts before writing durable state." | `tests/groundtruth_kb/test_mode_switch_transaction.py` | `test_apply_role_switch_rejects_acting_prime_builder`, `test_apply_role_switch_rejects_unknown_role`, `test_apply_role_switch_rejects_unknown_harness` | `python -m pytest tests/groundtruth_kb/test_mode_switch_transaction.py -v -k "rejects"` |
| "The component records enough transaction evidence to audit who requested the switch, what changed, when it was requested, and when it becomes effective." | `tests/groundtruth_kb/test_mode_switch_transaction.py` | `test_audit_record_contains_required_fields` | `python -m pytest tests/groundtruth_kb/test_mode_switch_transaction.py::test_audit_record_contains_required_fields -v` |
| "Agent instructions direct agents to use the transaction component or service, not ad hoc direct edits, when switching bridge configurations or operating modes." | `tests/scripts/test_operating_role_rule.py` (NEW or extend existing) | `test_operating_role_md_documents_gt_mode_set_role` | `python -m pytest tests/scripts/test_operating_role_rule.py::test_operating_role_md_documents_gt_mode_set_role -v` |
| "Session initialization reads the authoritative transaction result or current configuration artifact and applies the effective bridge/operating-mode state." | `tests/scripts/test_session_self_initialization_topology_derive.py` | `test_startup_derives_topology_from_role_map`, `test_startup_overrides_stale_stored_topology_with_corrective_note` | `python -m pytest tests/scripts/test_session_self_initialization_topology_derive.py -v` |
| "The implementation explicitly supports next-session effectiveness; immediate mid-session state replacement is optional unless separately specified." | DEFERRED to Slice 2 (next-session-effectiveness via SessionStart hook). Slice 1 implements the OPTIONAL mid-session immediate-apply path; Slice 2 implements the MUST next-session path. Both are required by the spec; Slice 1 establishes the deterministic component the spec MUSTs first. Owner waiver line if Codex disagrees with the slice split: "Owner waiver: SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001/next-session-application — DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION — Slice 1 establishes the deterministic component required by the spec's first acceptance criterion; next-session-effectiveness is staged to Slice 2 of the same project under DELIB-S347's project-scoped authorization model." |

Additional regression coverage:

| Risk | Test |
|---|---|
| Refactored `_is_single_harness_topology_applicable` changes dispatcher behavior | `python -m pytest tests/scripts/test_single_harness_bridge_dispatcher.py tests/scripts/test_cross_harness_bridge_trigger.py -v` (existing tests; must remain green) |
| Topology derivation breaks `single_harness_bridge_automation` | `python -m pytest tests/scripts/test_single_harness_bridge_automation.py -v` |
| `workstream_focus.save_state` regression | `python -m pytest tests/scripts/test_workstream_focus.py -v` |

Final full-bank regression at implementation-report time: `python -m pytest tests/` (selected suites pinned in the post-impl report).

## Clause Scope Clarification (Not a Bulk Operation)

This proposal does not perform a bulk standing-backlog transition. The clause-preflight rule `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` may flag this proposal because the content mentions `work item` (linking the single orphan WI to the project) and references the standing-backlog inventory in `gtkb-backlog-hygiene-bundle-s349` Finding 4. The scope is:

- One project creation (`PROJECT-GTKB-OPERATING-MODE-TRANSACTION-001`) covered by `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION`.
- One existing work-item membership link (`WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` joins the project as its implementing WI). This is the inventory.
- No bulk state transitions, no bulk WI mutations, no backlog-cleanup pattern.
- Owner-approval evidence already on disk: `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json` (formal-artifact-approval packet for the implementing spec) plus the 2026-05-14 in-session AUQ recorded in `memory/pending-owner-decisions.md`.

## Applicability Preflight

To be run after the INDEX entry is added (catch-22: preflight requires INDEX to resolve operative file). Required-spec citations expected per `config/governance/spec-applicability.toml`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always; bridge proposal) — cited above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (content matches "Specification Links", "implementation proposal") — cited above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (content matches "verification", "spec-to-test") — cited above; spec-to-test mapping provided.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (content matches "Agent Red" — proposal contrasts GT-KB platform work with the separate Agent Red project) — cited above with in-root compliance evidence.

Expected advisory-spec citations:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — all cited above.

Preflight execution will be captured in this section after INDEX update; if it surfaces additional triggered specs, the proposal is revised to a REVISED-1 -003 before Codex review begins in earnest.

## Risk and Rollback

**Risks:**

- R1 (P1): Refactoring `_is_single_harness_topology_applicable` to call the new derivation function changes single-harness applicability behavior under malformed role-map. Mitigation: byte-identical fixture parity test against `tests/scripts/test_cross_harness_bridge_trigger.py`; pin the derived-function's empty/malformed-input return path to match the dispatcher's fail-closed semantic.
- R2 (P2): Startup payload corrective note adds a new line that breaks downstream parsers reading the payload structure. Mitigation: add the note as a bulleted line under an existing section (`### Configuration`), not as a new top-level section; check the startup-payload golden tests at `tests/scripts/test_session_self_initialization*` for snapshot tolerance.
- R3 (P2): `workstream_focus.save_state` writing derived topology could surprise callers that explicitly want to set topology_mode. Mitigation: `save_state` already has a focus-only API surface (no topology parameter) — there are no callers passing topology to it today. Document the change in the module docstring; flag any future callers wanting topology control to use `mode_switch.transaction` instead.
- R4 (P3): Audit-record directory growth. Mitigation: file naming pattern allows trivial archival; no retention enforcement in Slice 1 (deferred to Slice 4 cleanup design).

**Rollback procedure:** All Slice 1 changes are additive (new module, new CLI subcommand, new test files, new audit directory) except items #5–#8 which modify existing files. Per change:

- `scripts/session_self_initialization.py` topology-derivation patch: revert the single block (~5 lines) and the derived value falls back to the stored value (today's behavior).
- `scripts/workstream_focus.py` `save_state` patch: revert the single block (~3 lines).
- `scripts/single_harness_bridge_dispatcher.py` shared-derivation refactor: revert the function body to inline logic (the original code is preserved in git history).
- `.claude/rules/operating-role.md` documentation update: revert the appended section via `git revert` on the implementation commit.

Audit records under `.gtkb-state/mode-switches/` are append-only by design; rollback does not delete them. They remain valid audit trail of any switches performed during Slice 1.

## Recommended Codex Review Sequence

1. Confirm `Specification Links` lists every spec/rule applicable per `config/governance/spec-applicability.toml` against this proposal's paths and content. Apply `bridge_applicability_preflight.py` + `adr_dcl_clause_preflight.py` mechanically.
2. Confirm `Prior Deliberations` cites at least the load-bearing prior decisions (`DELIB-S347`, `DELIB-0877`, `DELIB-1511`, `DELIB-1405`/`1406`). Helper-suggested seeding has been reviewed; novel-topic justification is not used because prior deliberations are abundant.
3. Confirm spec-to-test mapping covers each of the six acceptance criteria of `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`. Slice 1 explicitly defers the sixth criterion (next-session effectiveness) to Slice 2 with a stated owner-waiver line if Codex needs the spec covered in full now.
4. Confirm `target_paths` exhaustively lists implementation touch points and that no out-of-root paths are present.
5. Confirm `Owner Decisions / Input` substantively records the 2026-05-13 spec-approval packet and the 2026-05-14 in-session AUQ.

GO authorizes Prime Builder to:
- Generate the implementation-start authorization packet via `python scripts/implementation_authorization.py begin --bridge-id gtkb-operating-mode-transaction-001`.
- Execute the implementation per the Implementation Plan above.
- File the post-implementation report as -002.

NO-GO returns the proposal to Prime for revision; mechanical preflight failures are addressable in a REVISED-1 -003.

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
