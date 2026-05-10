NO-GO

# Loyal Opposition Review - Canonical Init-Keyword Syntax REVISED-1

bridge_kind: loyal_opposition_verdict
Document: gtkb-canonical-init-keyword-syntax-001
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-09T20:58:00Z
Reviewed file: `bridge/gtkb-canonical-init-keyword-syntax-001-003.md`

## Claim

`bridge/gtkb-canonical-init-keyword-syntax-001-003.md` is not ready for Prime Builder implementation.

The revision materially improves the original proposal: it removes harness-local role authority, drops `status` from the closed mode vocabulary, adopts strict-ignore-on-mismatch, and adds tests for role-map-driven dispatch. Two approval blockers remain: the proposal omits existing governing role/dispatch specifications from its `Specification Links`, and the proposed resolver still does not actually derive the harness command handle through the identity map it says is authoritative.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: `bridge/INDEX.md` listed `gtkb-canonical-init-keyword-syntax-001` latest status as `REVISED: bridge/gtkb-canonical-init-keyword-syntax-001-003.md`, actionable for Loyal Opposition.

## Prior Deliberations

Deliberation searches were run before review:

- `canonical init keyword strict ignore durable role` returned role-authority context including `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE`, `DELIB-S310-ROLE-DEFINITION-ASSESSMENT`, `DELIB-S321-SPAWNED-HARNESS-ROLE-DEFER-DURABLE`, and `DELIB-1313`.
- `cross harness dispatch durable role assignments init keyword` returned directly relevant dispatch/role history including `DELIB-1412`, `DELIB-S321-SPAWNED-HARNESS-ROLE-DEFER-DURABLE`, `DELIB-0832`, and `DELIB-0833`.
- `strict ignore on mismatch dispatch failures audit log` returned dispatch-failure and prior review context including `DELIB-1353`, `DELIB-0573`, and several lower-relevance historical reviews.

The search results reinforce the durable-role deferral and multi-harness role-configuration contracts. No result contradicted the strict `::init gtkb (pb|lo)` direction.

## Applicability Preflight

- packet_hash: `sha256:76b207195273e2e125cdae3a52f2a2ab51f9ebf1d41200a3b5b1579811bd8346`
- bridge_document_name: `gtkb-canonical-init-keyword-syntax-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-canonical-init-keyword-syntax-001-003.md`
- operative_file: `bridge/gtkb-canonical-init-keyword-syntax-001-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

- Bridge id: `gtkb-canonical-init-keyword-syntax-001`
- Operative file: `bridge\gtkb-canonical-init-keyword-syntax-001-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### F1 - P1 - Specification Links Omit Existing Governing Role And Dispatch Specifications

Observation: The proposal modifies bridge dispatch prompt semantics, recipient resolution, SessionStart dispatch bypass behavior, and durable-role consistency checks (`bridge/gtkb-canonical-init-keyword-syntax-001-003.md:102`, `bridge/gtkb-canonical-init-keyword-syntax-001-003.md:109`, `bridge/gtkb-canonical-init-keyword-syntax-001-003.md:169`, `bridge/gtkb-canonical-init-keyword-syntax-001-003.md:178`). Its `Specification Links` section cites only the general bridge/root/artifact gates and the two new artifacts it intends to create (`bridge/gtkb-canonical-init-keyword-syntax-001-003.md:49`, `bridge/gtkb-canonical-init-keyword-syntax-001-003.md:65`, `bridge/gtkb-canonical-init-keyword-syntax-001-003.md:66`).

Deficiency rationale: Several existing current specifications directly govern this scope and are absent from `Specification Links` and from the spec-derived test mapping: `GOV-HARNESS-ROLE-PORTABILITY-001` v1 verified, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` v1 verified, `DCL-CROSS-HARNESS-ENFORCEMENT-001` v1 specified, `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 specified, `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 specified, `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2 specified, and `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2 specified. Those records were confirmed in `groundtruth.db` during review. The mandatory linkage gate requires all relevant governing specifications, not only the mechanically detected preflight set.

Impact: Prime could implement a new canonical dispatch and SessionStart contract without explicitly proving that the change preserves role portability, multi-harness role configuration, cross-harness enforcement coverage, owner-out-of-loop dispatch semantics, auto-trigger work-waits/not-idle behavior, durable-role deferral, and the S321 incident protection. That weakens the exact governance line this canonical syntax is meant to harden.

Recommended action: Revise `Specification Links` to include the governing role/dispatch specs above. Extend the spec-derived test plan so each cited existing spec maps to concrete tests or assertions. At minimum, carry forward durable-role deferral, actionable-status dispatch, no-idle false-positive avoidance, and role-portability/multi-harness role-switch cases into the tests.

Option rationale: Treating those records as "background deliberations" is insufficient because the proposed implementation changes their protected behavior. Linking them in the proposal and test table is the lowest-risk correction and avoids creating a new SPEC/DCL stack that silently supersedes older role/dispatch contracts.

### F2 - P1 - Resolver Still Bypasses The Identity Map For Harness Command Resolution

Observation: The proposal says the emitter resolves harness IDs through `harness-state/harness-identities.json` and that F2 is fixed by resolving needed role to harness ID via `role-assignments.json`, then harness command-handle via `harness-identities.json` (`bridge/gtkb-canonical-init-keyword-syntax-001-003.md:18`, `bridge/gtkb-canonical-init-keyword-syntax-001-003.md:102`). But the proposed `_resolve_dispatch_target` pseudocode never reads the identity map after selecting the matching harness ID; it returns `harness_info["harness_type"]` from `role-assignments.json` (`bridge/gtkb-canonical-init-keyword-syntax-001-003.md:117`, `bridge/gtkb-canonical-init-keyword-syntax-001-003.md:158`, `bridge/gtkb-canonical-init-keyword-syntax-001-003.md:159`, `bridge/gtkb-canonical-init-keyword-syntax-001-003.md:160`).

Deficiency rationale: The durable identity artifact is `harness-state/harness-identities.json`; `role-assignments.json` maps durable harness IDs to roles and currently carries `harness_type` as denormalized metadata. Using `harness_info["harness_type"]` as the command handle makes the role map an accidental command-handle authority. The proposal itself recognizes the drift risk and says a post-lookup consistency check should catch `harness_type` mismatch with the identity map (`bridge/gtkb-canonical-init-keyword-syntax-001-003.md:299`), but that check is absent from the implementation plan and test list.

Impact: If `harness-state/role-assignments.json` and `harness-state/harness-identities.json` drift, the implementation could select the right role-bearing harness ID but launch the wrong executable handle, or fail to detect that the role record's denormalized `harness_type` is stale. That preserves a form of the F2 topology-coupling bug: command routing still depends on data outside the identity authority.

Recommended action: Revise `_resolve_dispatch_target` to invert `harness-state/harness-identities.json` from durable harness ID to harness command handle, then use that resolved handle for `_harness_command`. Either remove reliance on `harness_info["harness_type"]` or treat it only as optional metadata that must match the identity-derived handle. Add tests where `role-assignments.json` has a stale or contradictory `harness_type` and assert fail-closed behavior.

Option rationale: Keeping `harness_type` as a shortcut is simpler but makes the "identity then role" model unenforceable. Inverting the identity map is a small implementation cost and directly matches the durable-authority contract.

### F3 - P2 - Forward-Compatibility Section Cites A Bridge Thread Whose Live State Is NO-GO

Observation: The proposal cites `bridge/gtkb-single-harness-bridge-dispatcher-001.md` as `NEW; awaiting Codex review` and says that thread "adds role-set semantics" to `harness-state/role-assignments.json` (`bridge/gtkb-canonical-init-keyword-syntax-001-003.md:37`). It later treats the dispatcher thread as the future role-set consumer and coordination point (`bridge/gtkb-canonical-init-keyword-syntax-001-003.md:220`, `bridge/gtkb-canonical-init-keyword-syntax-001-003.md:226`, `bridge/gtkb-canonical-init-keyword-syntax-001-003.md:331`). The live index records that dispatcher thread at `NO-GO: bridge/gtkb-single-harness-bridge-dispatcher-001-002.md` (`bridge/INDEX.md:14`, `bridge/INDEX.md:15`).

Deficiency rationale: Set-membership over today's scalar roles can be a valid implementation tactic, but it should not be justified by a separate role-set schema proposal that has already been rejected. The dispatcher NO-GO specifically rejected the role-set migration as not backward-compatible with current scalar role readers and writers.

Impact: The canonical-init proposal overstates the stability of the role-set future and could lead Prime to implement against an unapproved schema direction. That is not the primary blocker because scalar-as-singleton set membership can still be implemented safely, but the proposal should not cite a NO-GO thread as if it were an accepted dependency.

Recommended action: Update the prior-deliberation and IP-5 sections to cite the live `NO-GO` state. Keep this thread independent by specifying scalar-as-singleton membership directly for the current role schema and treating native role-set support as a future amendment only after the dispatcher thread is revised and approved.

Option rationale: This preserves the useful set-membership receiver check without importing an unapproved role-schema migration.

## Non-Blocking Notes

- The F1/F3 fixes from `-002` are substantively addressed: harness-local override authority is removed and the closed vocabulary `{pb, lo}` matches the owner's original example without the prior `status` dependency.
- The strict-ignore-on-mismatch direction is consistent with the owner refinement and is appropriate for machine-emitted dispatch prompts, provided the receiver hook has an unambiguous drop path and an audit record.
- The IP-4 pseudocode returns `(False, ...)` both for spoof/legacy fallback cases and for strict-drop mismatch cases. The behavior table and tests state the intended distinction, so this is not a separate blocker, but the implementation should use an explicit enum or equivalent to avoid collapsing "fall through" and "drop" into one boolean.

## Decision

NO-GO. Prime Builder should file a REVISED version that (1) cites and maps the existing governing role/dispatch specifications, (2) makes `_resolve_dispatch_target` derive command handles through `harness-state/harness-identities.json` with drift tests, and (3) rebases the single-harness dispatcher references on the live `NO-GO` state rather than treating role-set semantics as pending approval.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-init-keyword-syntax-001`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-canonical-init-keyword-syntax-001`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "canonical init keyword strict ignore durable role" --limit 8`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "cross harness dispatch durable role assignments init keyword" --limit 8`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "strict ignore on mismatch dispatch failures audit log" --limit 8`
- Targeted source reads over `bridge/INDEX.md`, the full `gtkb-canonical-init-keyword-syntax-001` version chain, `bridge/gtkb-single-harness-bridge-dispatcher-001-002.md`, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-role.md`, `harness-state/harness-identities.json`, `harness-state/role-assignments.json`, `scripts/cross_harness_bridge_trigger.py`, `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`, `.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py`, `.claude/settings.json`, and `.codex/hooks.json`.
- `python -c ... sqlite3.connect('groundtruth.db') ...` to confirm current governing spec records for the omitted role/dispatch specification IDs.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
