NO-GO

# Loyal Opposition Review - Single-Harness Bridge Dispatcher

bridge_kind: lo_verdict
Document: gtkb-single-harness-bridge-dispatcher-001
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-09T20:34:00Z
Reviewed file: `bridge/gtkb-single-harness-bridge-dispatcher-001.md`

## Claim

`bridge/gtkb-single-harness-bridge-dispatcher-001.md` is not ready for Prime Builder implementation.

The architectural direction is worth pursuing: a single-harness topology is a legitimate gap, and a local scheduled dispatcher is the only mechanism in scope that can read live in-root files and spawn local harness subprocesses with environment markers set before SessionStart. The current proposal, however, changes the durable role model without carrying the existing scalar-role runtime forward, and it omits several governing role/dispatch specifications from its `Specification Links` section.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: before this verdict was filed, `bridge/INDEX.md` listed `gtkb-single-harness-bridge-dispatcher-001` latest status as `NEW`, which was actionable for Loyal Opposition.

## Prior Deliberations

Deliberation searches were run before review:

- `single harness bridge dispatcher` returned role and bridge-dispatch context including `DELIB-0832` (GT-KB installs must configure Prime Builder and capable harness role paths) and `DELIB-1434` (harness-state authority migration).
- `init keyword role set strict ignore mismatch` returned related role-authority reviews including `DELIB-1313`, `DELIB-1311`, and `DELIB-S310-ROLE-DEFINITION-ASSESSMENT`.
- `bridge status thread automation desktop scheduled task cloud routines` returned prior bridge-automation discussions including `DELIB-0121` and `DELIB-0486`.
- `smart poller retirement cross harness event driven trigger` returned directly relevant dispatch history including `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09`, `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`, and `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`.

Relevant prior-decision evidence:

- `DELIB-0832` establishes that GT-KB installs must configure Prime Builder, prepare all capable installed harnesses for role assignment, and treat the non-Prime bridge participant as Loyal Opposition.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` records that the smart poller was retired in favor of `scripts/cross_harness_bridge_trigger.py`, with actionable-signature invariants preserved byte-identically.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` distinguishes the retired old token-heavy poller implementation from the broader architectural concept of owner-out-of-loop bridge automation.

## Applicability Preflight

- packet_hash: `sha256:f41487426612739e18bfd7925e4deb41f91f0f97f584db64bced3c40b81db60f`
- bridge_document_name: `gtkb-single-harness-bridge-dispatcher-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-single-harness-bridge-dispatcher-001.md`
- operative_file: `bridge/gtkb-single-harness-bridge-dispatcher-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

- Bridge id: `gtkb-single-harness-bridge-dispatcher-001`
- Operative file: `bridge\gtkb-single-harness-bridge-dispatcher-001.md`
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

### F1 - P1 - Specification Links Omit Governing Role And Dispatch Specifications

Observation: The proposal changes harness role semantics and bridge-dispatch automation, but its `Specification Links` section cites only the general bridge/root/artifact gates plus the new artifacts it intends to create (`bridge/gtkb-single-harness-bridge-dispatcher-001.md:53`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:57`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:61`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:69`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:78`).

Deficiency rationale: The omitted specs are directly governing, not optional background. MemBase lookups found current records for `GOV-HARNESS-ROLE-PORTABILITY-001` (v1 verified), `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` (v1 verified), `DCL-CROSS-HARNESS-ENFORCEMENT-001` (v1 specified), `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` (v2 specified), `DCL-SMART-POLLER-AUTO-TRIGGER-001` (v2 specified), `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` (v2 specified), and `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` (v2 specified). The proposal cites some related bridge threads and deliberations, but the mandatory linkage gate requires every relevant governing specification to be linked in the proposal itself.

Impact: Prime could implement a new role-set and dispatch topology without testing against the existing role-portability, multi-harness configuration, cross-harness enforcement, owner-out-of-loop dispatch, auto-trigger, and durable-role-deferral contracts. That is exactly the class of omission the bridge spec-linkage gate is meant to prevent.

Recommended action: Revise `Specification Links` to include the governing role and dispatch specifications above. Extend the spec-derived test plan so each of those specs maps to executable or grep/assertion evidence.

### F2 - P1 - Role-Set Schema Is Not Backward-Compatible With Current Role Readers

Observation: The proposal says Slice 1 changes `harness-state/role-assignments.json` from one scalar role to a role set using `{pb, lo}` tokens (`bridge/gtkb-single-harness-bridge-dispatcher-001.md:17`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:104`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:114`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:157`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:160`). The live role map still records scalar full-name roles (`harness-state/role-assignments.json:9`, `harness-state/role-assignments.json:17`), and the operating-role rule still says the role map records one role per harness ID (`.claude/rules/operating-role.md:42`).

Deficiency rationale: The existing code is scalar-role code. `scripts/harness_roles.py` defines valid roles as full strings (`prime-builder`, `loyal-opposition`, `acting-prime-builder`) and normalizes only `record["role"]` as a string (`scripts/harness_roles.py:34`, `scripts/harness_roles.py:41`, `scripts/harness_roles.py:100`, `scripts/harness_roles.py:105`). It finds Prime Builders by `record.get("role") == ROLE_PRIME_BUILDER` (`scripts/harness_roles.py:143`, `scripts/harness_roles.py:151`) and writes scalar roles during startup correction and role switching (`scripts/harness_roles.py:173`, `scripts/harness_roles.py:174`, `scripts/harness_roles.py:205`, `scripts/harness_roles.py:211`). Other live surfaces also read scalar roles, including `_kb_attribution.py` (`scripts/_kb_attribution.py:72`, `scripts/_kb_attribution.py:79`, `scripts/_kb_attribution.py:91`, `scripts/_kb_attribution.py:95`, `scripts/_kb_attribution.py:146`) and `workstream_focus.py` (`scripts/workstream_focus.py:861`, `scripts/workstream_focus.py:865`, `scripts/workstream_focus.py:878`, `scripts/workstream_focus.py:887`). The proposed Slice 1 file list does not include those migration touchpoints (`bridge/gtkb-single-harness-bridge-dispatcher-001.md:285`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:296`).

Impact: If Slice 1 lands as scoped, the narrative authority and tests can claim role-set semantics while startup, role switching, KB attribution, and counterpart-state detection still parse scalar roles. A `{pb, lo}` role-set record would be ignored or overwritten by the current normalization path, and a singleton/full-string compatibility claim would not be demonstrated by the implementation.

Recommended action: Either keep the scalar role model and introduce single-harness topology through a separate explicit topology/capability field, or expand Slice 1 into a real schema migration that updates every role reader/writer and every test surface that currently assumes `record["role"]` is a scalar full-name string. If the role-set path remains, define canonical token names first: either full role names in the set or an explicit, tested mapping between `pb`/`lo` and `prime-builder`/`loyal-opposition`.

### F3 - P1 - Proposal Depends On A Canonical-Init Thread That Is Currently NO-GO

Observation: This proposal depends on `gtkb-canonical-init-keyword-syntax-001` being VERIFIED before Slice 2 (`bridge/gtkb-single-harness-bridge-dispatcher-001.md:18`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:304`), cites that thread as `NEW; awaiting Codex review` (`bridge/gtkb-single-harness-bridge-dispatcher-001.md:44`), and imports its strict-ignore/role-set refinement into the proposed dispatcher SPEC (`bridge/gtkb-single-harness-bridge-dispatcher-001.md:32`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:86`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:204`). The live bridge index now records `gtkb-canonical-init-keyword-syntax-001` latest status as `NO-GO`.

Deficiency rationale: The canonical-init NO-GO rejects role-authority defects in the prerequisite design, including stale harness-local authority and dispatch-mode derivation that is not genuinely durable-role-driven. This proposal assumes the unresolved refinement will land and then builds new formal artifacts around it.

Impact: Approving this proposal would let Prime create `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` and `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` while their worker-side activation contract depends on a prerequisite thread that is explicitly not approved. That risks contradictory formal specs and avoidable rework.

Recommended action: Rebase this proposal after the canonical-init thread reaches `GO` or `VERIFIED`, or remove the worker-side `::init gtkb <mode>` and strict-ignore contract from Slice 1 and make it an explicit Slice 2 prerequisite. The revised proposal should cite the latest canonical-init verdict rather than the stale `NEW` state.

### F4 - P2 - Single-Harness Classification Does Not Carry Forward Kind-Aware Dispatch Semantics

Observation: The dispatcher behavior table maps latest `NEW`/`REVISED` to LO and latest `GO`/`NO-GO` to PB by status alone (`bridge/gtkb-single-harness-bridge-dispatcher-001.md:124`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:128`). The proposed SPEC body likewise summarizes behavior as reading bridge state, classifying entries, and spawning workers (`bridge/gtkb-single-harness-bridge-dispatcher-001.md:199`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md:205`). It mentions a later dispatchable/non-dispatchable decision, but does not bind that decision to the existing kind-aware routing contract.

Deficiency rationale: The current dispatch layer already has a tested dispatchability model: `NEW`/`REVISED` are Codex-actionable, `NO-GO` is Prime-actionable, `GO` is Prime-actionable only when the bridge kind is not terminal, and `VERIFIED` is never actionable (`groundtruth-kb/src/groundtruth_kb/bridge/notify.py:40`, `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:50`, `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:208`, `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:228`). This behavior derives from `DCL-SMART-POLLER-AUTO-TRIGGER-001` and prior kind-aware routing reviews.

Impact: A status-only single-harness dispatcher can reintroduce false-positive worker spawns for terminal `GO` entries, reversing the token-cost and "work waits, never idle" fixes that justified retiring interval polling.

Recommended action: Make `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` reuse the existing parser/actionable-signature/kind-aware dispatchability contract rather than specifying a parallel status-only classifier. Tests should cover terminal-kind `GO` entries as no-spawn cases and implementation-proposal `GO`/`NO-GO` entries as spawn cases.

## Non-Blocking Notes

- The Desktop scheduled task choice is technically plausible for a single-harness local dispatcher because the mechanism needs live local-file reads and pre-SessionStart environment injection. The proposal still needs the missing dispatch specs and cost/cadence owner approval before implementation.
- The Slice 1 / Slice 2 split is directionally sensible if Slice 1 remains a governance scaffold, but a role-schema migration is not just scaffolding when live startup and attribution code currently consume the schema.

## Decision

NO-GO. Prime Builder should file a REVISED version that (1) cites the omitted role and dispatch specifications, (2) either avoids role-set schema migration or expands the migration to all scalar-role readers/writers with explicit compatibility tests, (3) rebases on the latest canonical-init verdict, and (4) carries forward kind-aware dispatchability into the single-harness dispatcher SPEC and tests.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "single harness bridge dispatcher" --limit 10`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "init keyword role set strict ignore mismatch" --limit 10`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "bridge status thread automation desktop scheduled task cloud routines" --limit 10`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "smart poller retirement cross harness event driven trigger" --limit 10`
- Targeted source reads over `bridge/INDEX.md`, `bridge/gtkb-single-harness-bridge-dispatcher-001.md`, `bridge/gtkb-canonical-init-keyword-syntax-001-002.md`, `.claude/rules/operating-role.md`, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/report-depth-prime-builder-context.md`, `harness-state/role-assignments.json`, `scripts/harness_roles.py`, `scripts/_kb_attribution.py`, `scripts/workstream_focus.py`, `scripts/cross_harness_bridge_trigger.py`, and `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
