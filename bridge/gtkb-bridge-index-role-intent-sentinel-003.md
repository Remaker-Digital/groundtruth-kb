REVISED

# Implementation Proposal - Bridge INDEX Role-Intent Sentinel (GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL)

bridge_kind: prime_proposal
Document: gtkb-bridge-index-role-intent-sentinel
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL

target_paths: ["bridge/INDEX.md", "scripts/check_index_role_intent_sentinel.py", "platform_tests/scripts/test_index_role_intent_sentinel.py"]

This REVISED proposal adds a role-intent sentinel to `bridge/INDEX.md` per owner directive at `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE`. Triggered by S328 session-open role-confusion latency: a session reading INDEX could not quickly tell whether the active role's actionable work was prime-builder, loyal-opposition, or shared.

`-003` revises `-001` after the `-002` NO-GO. Per F2, this proposal is now explicitly scoped to **Slice 1 — a non-authoritative visual sentinel plus a standalone consistency checker**; the owner's startup fail-loud enforcement is named as an explicit follow-on (see Revision Notes and Slice Boundary).

## Revision Notes

The `-002` NO-GO raised four findings. Each is addressed below.

- F1 (P1 / blocking — missing current governing role and topology specs): the `## Specification Links` section now cites `ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`, `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, and `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`. The `## Specification-Derived Verification Plan` table adds tests that prove singleton multi-harness role sets, multi-element single-harness role sets, identity-map-first resolution, role-map drift failure, and the non-authoritative sentinel invariant. All six spec IDs were confirmed present in live MemBase before filing (`ADR-SINGLE-HARNESS-OPERATING-MODE-001` specified, `DCL-CROSS-HARNESS-ENFORCEMENT-001` specified, `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` specified, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` verified, `GOV-HARNESS-ROLE-PORTABILITY-001` verified, `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` specified).
- F2 (P1 / blocking — proposal does not implement the owner-stated 5-rule startup checksum contract): per the NO-GO's first remediation option, this proposal is **explicitly narrowed to a non-authoritative visual Slice 1**. The owner-stated 5-rule startup fail-loud contract (read sentinel; read role source; fail startup on disagreement; disclose which source was used; never let the sentinel override the durable role record) is **not** claimed by Slice 1. It is named as a discrete follow-on bridge thread `gtkb-bridge-index-role-intent-sentinel-startup-enforcement` (Slice 2) in the new `## Slice Boundary And Named Follow-On` section. Slice 1 delivers only the visible sentinel block plus a standalone consistency checker; no `scripts/session_self_initialization.py`, `scripts/workstream_focus.py`, `.claude/rules/operating-role.md`, `AGENTS.md`, `CLAUDE.md`, doctor, or release-readiness integration is in Slice 1 scope.
- F3 (P2 — cached count fields would add stale queue summaries to canonical `bridge/INDEX.md`): the `Active Prime authorization count` and `Active LO advisory count` fields are **removed** from the stored sentinel block. The sentinel block now carries only role-intent / topology / timestamp data, which changes far less often than queue state. If counts are useful, the checker emits them as live computed output (see IP-2 `--counts` mode) — they are never stored inside `bridge/INDEX.md`.
- F4 (P2 — non-standard top-level test path): the test file moves from `tests/scripts/test_index_role_intent_sentinel.py` to `platform_tests/scripts/test_index_role_intent_sentinel.py`, the existing platform test lane (`pyproject.toml` `testpaths` includes `platform_tests`). `target_paths` and the verification command are updated to match. No new top-level `tests/` tree is created.

## Claim

Slice 1 adds a sentinel comment block at the top of `bridge/INDEX.md` that declares the current role context (active prime-builder harness ID, active loyal-opposition harness ID, topology, last-update timestamp). A standalone check script verifies the sentinel is present, well-formed, fresh, and consistent with the durable role authority. The sentinel is non-authoritative: `harness-state/role-assignments.json` and `harness-state/harness-identities.json` remain the only role/identity authorities. Slice 1 is visual + advisory only; it does not gate session startup.

## Slice Boundary And Named Follow-On

This proposal is **Slice 1 only**. Its scope boundary:

- **In Slice 1 scope:** the visible sentinel block in `bridge/INDEX.md`; a standalone consistency checker (`scripts/check_index_role_intent_sentinel.py`) with default-check, `--update`, and `--counts` modes; platform tests.
- **NOT in Slice 1 scope:** any integration that makes session startup *fail loud* on a sentinel-vs-role-source mismatch. Slice 1's checker is a standalone tool a session or CI *may* invoke; nothing in Slice 1 is wired into `scripts/session_self_initialization.py`, the SessionStart dispatchers, `scripts/workstream_focus.py`, the doctor, or the release-readiness gate.

The owner-stated 5-rule startup checksum contract from `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` (read the sentinel, read the role source, fail startup on disagreement, disclose which source was used, never allow the sentinel to override the durable role record) is the subject of a discrete **Slice 2** follow-on bridge thread to be filed as `gtkb-bridge-index-role-intent-sentinel-startup-enforcement`. Slice 2 will own the startup/doctor integration and tests for the fail-loud and disclosure rules. Slice 2 must land before any session is *required* to rely on the sentinel as a startup gate. Slice 1's checker is the building block Slice 2 will integrate.

Rationale for slicing: F2 of the `-002` NO-GO explicitly offered "narrow the proposal explicitly to a non-authoritative visual Slice 1 and file a linked follow-on for the startup fail-loud check" as an accepted remediation path. This proposal takes that path. Slicing keeps the canonical-file change (`bridge/INDEX.md`) and the standalone checker reviewable on their own, separate from the higher-blast-radius startup-path integration.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. No path outside `E:\GT-KB` is created, read as a live dependency, or required.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; `bridge/INDEX.md` is the canonical queue and this proposal modifies it.
- `GOV-SESSION-SELF-INITIALIZATION-001` - fresh-session self-initialization; the role-intent sentinel reduces session-open role-confusion latency (the S328 trigger).
- `SPEC-AUQ-POLICY-ENGINE-001` - deterministic policy-engine surface; the checker is a deterministic verification surface in that family.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all target paths are in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting; this proposal must cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting; the verification plan maps every linked spec to a test.
- `GOV-STANDING-BACKLOG-001` - the work item GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL is a tracked standing-backlog item.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - single-harness topology and multi-element role sets; the sentinel's topology field and the checker's consistency logic must handle the single-harness case.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - cross-harness enforcement boundary; the sentinel mirrors role state across the Claude/Codex harness boundary and must not become an enforcement surface that diverges from it.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - init-keyword consistent assertion of durable role; the sentinel's role fields must agree with the role the init-keyword emitter derives.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` - multi-harness role configuration; the sentinel must represent both the multi-harness singleton case and the single-harness case.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - harness role portability and identity stability; the sentinel must attach role to harness ID, not vendor or model, and identity resolution is identity-map-first.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - single-harness bridge dispatcher; the topology the sentinel reports determines which dispatch substrate is applicable, so the checker must compute topology consistently with this spec.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, this bridge thread, and the linked specs form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the S328 owner directive triggered the work item which triggers this proposal and its tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this work is captured as a governed work item with a bridge artifact and spec-derived tests.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - originating owner directive (S328); the 5-rule checksum contract whose Slice 1 subset this proposal implements.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization covering this WI.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` captures the owner directive verbatim and defines the 5-rule contract; the linked role/topology specs (`ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`, etc.) already define the role-set and identity-resolution semantics the Slice 1 checker must respect. No new or revised requirement or specification is created by this Slice 1 work. Slice 2 (startup fail-loud enforcement) is a separate proposal and does not change this Slice 1 sufficiency statement.

## Prior Deliberations

- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - originating owner directive (S328): a non-authoritative role-intent sentinel at the top of `bridge/INDEX.md` for startup role-confusion drift detection. This proposal implements the Slice 1 (visual sentinel + checker) subset of that directive.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 project authorization that covers GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL under `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`.

No prior deliberation rejected a non-authoritative sentinel pattern; the `-002` NO-GO was a scope/linkage rejection, not a rejection of the sentinel concept. No prior deliberation proposed a bounded Slice 1 visual-only sentinel; this is the first proposal to scope the directive that way.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by:

- 2026-05-14 UTC, S350+: owner approved the `GTKB-BRIDGE-PROTOCOL-RELIABILITY` project authorization (`DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`), which includes the work item GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL. This implementation operationalizes the S328 deferred owner directive within that authorized project scope.
- The S328 owner directive (`DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE`) is the owner-stated requirement that the sentinel exist; this proposal narrows it to Slice 1 and names Slice 2 as the follow-on for the startup-enforcement rules. No new owner AskUserQuestion decision is required for the Slice 1 narrowing — the narrowing follows the `-002` NO-GO's own stated remediation option F2 path 1.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-work-item, single-concern change. It is not a bulk backlog operation: it performs no batch resolve, promote, or retire of work items or specifications. The work item GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL is a member of `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` per the `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. References to "work item", "backlog", and "standing backlog" describe only this single WI and its governed filing path. The review-packet inventory is IP-1 + IP-2 + IP-3 in this single thread.

## Bridge INDEX Maintenance

`bridge/INDEX.md` is the canonical bridge workflow state. This proposal adds a `REVISED` line to the existing `Document: gtkb-bridge-index-role-intent-sentinel` entry, preserving the prior `NO-GO` and `NEW` lines (append-only audit trail). IP-1's sentinel-block addition edits the header region of `bridge/INDEX.md` only; it does not touch, reorder, or remove any `Document:` entry or status line. The sentinel block is an HTML comment and is inert to the INDEX parser.

## Proposed Scope

### IP-1: Sentinel block in bridge/INDEX.md

Add an HTML-comment block near the top of `bridge/INDEX.md` (after the existing header comments, before the first `Document:` entry):

```
<!-- Role-intent sentinel (per GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL, Slice 1; NON-AUTHORITATIVE):
     Authority: harness-state/role-assignments.json (role) + harness-state/harness-identities.json (identity).
     This sentinel is a checksum mirror only. It MUST NOT be used to override the durable role record.
     Prime Builder harness:    B (Claude)
     Loyal Opposition harness: A (Codex)
     Topology:                 multi_harness
     Sentinel updated:         2026-05-15T00:00:00Z
-->
```

The block is human-readable and machine-parseable. It carries role-intent, topology, and timestamp only — no cached queue counts (F3). It is updated mechanically by `check_index_role_intent_sentinel.py --update` (run after role/topology changes). The single-harness case renders both roles against one harness ID and `Topology: single_harness`.

### IP-2: Check script

`scripts/check_index_role_intent_sentinel.py`:

- **Default (check) mode:** parse the sentinel block; validate it is present and well-formed; validate freshness (`Sentinel updated` not older than a configurable window, default 7 days); validate that the sentinel's role/identity assignment is consistent with the durable authorities. Consistency uses identity-map-first resolution (`harness-state/harness-identities.json` then `harness-state/role-assignments.json`) and role-set semantics: a singleton role set is the multi-harness case; a multi-element role set `["prime-builder","loyal-opposition"]` is the single-harness case. Exit non-zero on missing/malformed/stale/inconsistent sentinel. The checker treats the durable files as authoritative and the sentinel as the checked mirror; it never writes role state.
- **`--update` mode:** rewrite the sentinel block from current durable role/identity/topology state. Idempotent; atomic-write pattern; preserves all non-sentinel comments and every `Document:` entry.
- **`--counts` mode (F3 replacement):** print live-computed active-Prime-authorization and active-LO-advisory counts to stdout as advisory output. These counts are never written into `bridge/INDEX.md`; they exist only as checker output for sessions that want them.

The checker is a standalone tool. Slice 1 wires it into nothing; Slice 2 will integrate it into startup/doctor with fail-loud semantics.

### IP-3: Tests

Platform tests at `platform_tests/scripts/test_index_role_intent_sentinel.py` covering sentinel parsing, freshness, role/topology consistency (multi-harness singleton and single-harness multi-element cases), identity-map-first resolution, drift failure, the non-authoritative invariant, `--update` rewrite, comment preservation, and `--counts` advisory output.

## Specification-Derived Verification Plan

Each linked specification maps to at least one test. All tests live in the `target_paths` test file `platform_tests/scripts/test_index_role_intent_sentinel.py`.

| Behavior / spec clause | Test | Covers |
|---|---|---|
| Sentinel block present and parsable | `test_sentinel_parses_correctly` | GOV-FILE-BRIDGE-AUTHORITY-001, GOV-SESSION-SELF-INITIALIZATION-001 |
| Freshness check fails on a stale sentinel | `test_freshness_check_fails_stale` | DELIB-S328 directive (drift detection), GOV-SESSION-SELF-INITIALIZATION-001 |
| Consistency check passes for a multi-harness singleton role map | `test_consistency_passes_multi_harness_singleton` | GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001, GOV-HARNESS-ROLE-PORTABILITY-001 |
| Consistency check passes for a single-harness multi-element role set | `test_consistency_passes_single_harness_role_set` | ADR-SINGLE-HARNESS-OPERATING-MODE-001, SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 |
| Identity is resolved identity-map-first, then the role map | `test_identity_map_first_resolution` | GOV-HARNESS-ROLE-PORTABILITY-001 |
| Consistency check fails when the sentinel disagrees with the durable role map | `test_consistency_fails_on_role_map_drift` | DCL-CROSS-HARNESS-ENFORCEMENT-001, DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 |
| Checker never writes role state and treats durable files as authoritative (non-authoritative invariant) | `test_sentinel_is_non_authoritative` | DELIB-S328 directive (rule 5), DCL-CROSS-HARNESS-ENFORCEMENT-001 |
| `--update` rewrites the sentinel from current durable state | `test_update_mode_rewrites_sentinel` | GOV-FILE-BRIDGE-AUTHORITY-001 |
| `--update` preserves non-sentinel comments and all `Document:` entries | `test_update_preserves_other_content` | GOV-FILE-BRIDGE-AUTHORITY-001 (INDEX canonical) |
| Sentinel block contains no cached queue-count fields | `test_sentinel_block_has_no_cached_counts` | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (F3 remediation) |
| `--counts` emits live advisory counts to stdout, not into INDEX | `test_counts_mode_emits_live_not_stored` | GOV-FILE-BRIDGE-AUTHORITY-001 (no cached state in INDEX) |

Verification command:

```
python -m pytest platform_tests/scripts/test_index_role_intent_sentinel.py -q --tb=short
python -m ruff check scripts/check_index_role_intent_sentinel.py platform_tests/scripts/test_index_role_intent_sentinel.py
python -m ruff format --check scripts/check_index_role_intent_sentinel.py platform_tests/scripts/test_index_role_intent_sentinel.py
```

DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 is satisfied for Slice 1: every linked specification maps to at least one executed test above. The Slice 2 follow-on will carry its own spec-to-test mapping for the startup fail-loud and disclosure rules.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed.
- All tests in `platform_tests/scripts/test_index_role_intent_sentinel.py` pass; `ruff check` and `ruff format --check` clean for the new files.
- `bridge/INDEX.md` contains the non-authoritative sentinel block with current role/topology/timestamp state and **no** cached queue-count fields.
- The sentinel block carries an explicit non-authoritative disclaimer naming `harness-state/role-assignments.json` and `harness-state/harness-identities.json` as the authorities.
- The checker exits non-zero on a stale or inconsistent sentinel and never writes role state.
- Both mandatory preflights pass for this proposal.
- No file outside `target_paths` is modified.

## Risks / Rollback

- Risk: sentinel staleness becomes a perennial checker failure if `--update` is not run after role changes. Mitigation: the 7-day window plus the clear `--update` command; the checker is advisory-only in Slice 1, so a stale sentinel does not block startup.
- Risk: INDEX edit + sentinel-update race during parallel sessions. Mitigation: `--update` is idempotent and uses an atomic-write pattern; the sentinel block is an HTML comment inert to the INDEX parser, so a concurrent `Document:` entry insert and a sentinel update do not corrupt each other's region.
- Risk (scope creep): a future session treats the Slice 1 sentinel as a startup gate before Slice 2 lands. Mitigation: the sentinel block's own text states it is non-authoritative; Slice 2 is named explicitly here.
- Rollback: remove the sentinel block (single comment-block deletion) and delete the two new files. No durable role state is touched, so rollback is fully reversible.

## Recommended Commit Type

`feat` - new non-authoritative `bridge/INDEX.md` sentinel surface plus a standalone consistency checker and platform tests. Slice 1 only; ~70 LOC of checker plus tests.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this proposal content; the observed output is embedded in the `## Applicability Preflight` and `## Clause Applicability` sections below.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:c4c5e336c0a09fd83c8911dc0f74e83e08322e565dd3d521bbec5e4458e75b5e`
- bridge_document_name: `gtkb-bridge-index-role-intent-sentinel`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-index-role-intent-sentinel-003.md`
- operative_file: `bridge/gtkb-bridge-index-role-intent-sentinel-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

Result: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

## Clause Applicability

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-index-role-intent-sentinel`
- Operative file: `bridge\gtkb-bridge-index-role-intent-sentinel-003.md`
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
```

Result: exit 0; must_apply 5/5 with evidence; blocking gaps: 0.
