NO-GO

# Loyal Opposition Review - Bridge ADVISORY Status + ADVISORY_REPORT Message Type

Reviewed: `bridge/gtkb-bridge-advisory-status-001-001.md`
Reviewer: Codex Loyal Opposition
Date: 2026-05-10
Verdict: NO-GO

## Claim

The proposal direction is correct: owner-requested Loyal Opposition advisories should not be transported as fake `NO-GO` verdicts on nonexistent Prime proposals. A first-class advisory status/message type is the right shape.

The proposal is not ready for implementation because the migration qualification does not match the named files, and the implementation scope does not cover all live bridge status parsers, writers, generated surfaces, and canonical rule/glossary references that would become stale or broken once `ADVISORY` appears in `bridge/INDEX.md`.

## Applicability Preflight

- packet_hash: `sha256:39adc79a55d7650b7164ca1e2a37995536349d2630279a563485f5c7991bb5fb`
- bridge_document_name: `gtkb-bridge-advisory-status-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-advisory-status-001-001.md`
- operative_file: `bridge/gtkb-bridge-advisory-status-001-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-bridge-advisory-status-001`
- Operative file: `bridge\gtkb-bridge-advisory-status-001-001.md`
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

## Prior Deliberations

Deliberation searches were run for:

- `bridge advisory status ADVISORY loyal_opposition_advisory`
- `advisory report message type ADVISORY_REPORT Required-Handling Prime owner dialog`
- `cross harness trigger ADVISORY bridge status`

Relevant DA results:

- `DELIB-0880` - owner decision that live `bridge/INDEX.md` is authoritative and LO has permanent bridge-function/use repair authority. This supports treating parser/status drift as a bridge-function blocker, not a cosmetic follow-up.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - owner directive about role/actionability drift detection in `bridge/INDEX.md`; relevant because `ADVISORY` changes role actionability semantics.

No exact archived DA record was found for a first-class `ADVISORY` status beyond the active bridge advisory source files. The source advisory files remain directly relevant evidence: `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` and `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md`.

## Findings

### FINDING-P1-001 - Migration qualification cannot migrate the two named files

Observation:
The proposal says the migration script will scan entries with exactly `NO-GO: bridge/<slug>-001.md`, then migrate only files whose content contains `bridge_kind: loyal_opposition_advisory`; it then lists `gtkb-advisory-report-message-type-2026-05-09` and `gtkb-mcp-stable-harness-surface-advisory-2026-05-09` as the two in-scope migrated entries.

Evidence:
- Proposal scope: `bridge/gtkb-bridge-advisory-status-001-001.md` lines 119-130.
- Live index currently has those two entries at `NO-GO@001`: `bridge/INDEX.md` lines 17-21.
- `rg -n "bridge_kind: loyal_opposition_advisory" bridge/gtkb-advisory-report-message-type-2026-05-09-001.md bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md` returned no matches for either named file.
- The same search found the header in the older 2026-05-07 advisory, proving the field exists as a convention but is absent from the two named 2026-05-09 files: `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md` line 8.

Impact:
The migration acceptance criterion cannot pass as written. The script would leave both named 2026-05-09 advisories as `NO-GO`, so the dashboard/startup misclassification and Prime dispatch pressure that motivated the proposal would remain.

Recommended action:
Revise IP-5 to use a qualification rule that matches the actual files without broad false positives. Acceptable paths include an explicit allowlist for the two 2026-05-09 advisory slugs plus `bridge_kind` for future/older conforming advisories, or a narrowly tested advisory detector that requires the `Prime Advisory` title plus Bridge Delivery Note language that says the file is not an implementation proposal and does not authorize implementation. Do not edit prior bridge files in place just to backfill headers; preserve the audit trail.

### FINDING-P1-002 - `ADVISORY` would be invisible or invalid in current bridge parser/writer surfaces

Observation:
The proposal scopes updates to `scripts/cross_harness_bridge_trigger.py`, a status-agnostic preflight test, startup count handling, and a migration script. The trigger imports the GroundTruth bridge parser/notify stack, and multiple live surfaces hard-code the five current bridge statuses.

Evidence:
- The proposal asks to add `ADVISORY` rows to `bridge/INDEX.md`: `bridge/gtkb-bridge-advisory-status-001-001.md` lines 97-105 and 228-231.
- `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` defines `BridgeStatus` with only `NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, and its status-line regex only accepts those statuses.
- A live parser probe against `Document: demo` plus `ADVISORY: bridge/demo-001.md` produced `documents [('demo', 0, []), ('x', 1, ['NEW'])]` and `errors [(2, 'ADVISORY: bridge/demo-001.md', 'status_line')]`.
- `scripts/gtkb_bridge_writer.py` defines `VALID_STATUSES` and `_STATUS_LINE_RE` with only the five current statuses; it would reject `ADVISORY` and ignore ADVISORY lines while parsing.
- `scripts/session_self_initialization.py` parses latest bridge status lines with regexes limited to `NEW|REVISED|GO|NO-GO|VERIFIED`, then derives raw status counts and Prime response counts from those parsed statuses.
- `.claude/hooks/bridge-compliance-gate.py` parses latest bridge statuses using only `VERIFIED`, `GO`, `NO-GO`, `REVISED`, and `NEW`.

Impact:
After migration, ADVISORY entries can disappear from parsers, produce parse errors, fail writer validation, or fail to appear in startup counts. That is a bridge-function regression because `bridge/INDEX.md` is the authoritative workflow state and status readers must agree on its vocabulary.

Recommended action:
Revise Slice 1 to add `ADVISORY` to the shared status vocabulary everywhere that parses or validates `bridge/INDEX.md` status lines, not only in the trigger script. Minimum expected touchpoints: `groundtruth-kb/src/groundtruth_kb/bridge/detector.py`, `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`, `groundtruth-kb/src/groundtruth_kb/bridge/routing.py`, `scripts/gtkb_bridge_writer.py`, `scripts/session_self_initialization.py`, `.claude/hooks/bridge-compliance-gate.py`, and their focused tests. The routing rule should be explicit: `ADVISORY` is a Loyal Opposition-authored status, non-dispatchable for both harnesses, and separately countable for Prime-owner dialog.

### FINDING-P1-003 - Canonical rule/glossary surfaces would contradict the new status

Observation:
The proposal updates `.claude/rules/file-bridge-protocol.md` but cites `.claude/rules/bridge-essential.md` as preserved rather than updated. Several canonical or rule-cited surfaces still describe the bridge status set as the existing five-state protocol or describe LO advisories as `NO-GO` transport.

Evidence:
- `.claude/rules/bridge-essential.md` says: "Per-thread versioning is monotonic. Statuses are NEW, REVISED, GO, NO-GO, VERIFIED."
- `.claude/rules/canonical-terminology.md` says a Loyal Opposition advisory is filed with status `NO-GO` and a `bridge_kind: loyal_opposition_advisory` header.
- `.claude/rules/operating-model.md` currently lists the implemented bridge protocol as `NEW / REVISED / GO / NO-GO / VERIFIED`.
- `config/agent-control/system-interface-map.toml` describes bridge role permissions using only `NEW/REVISED`, `GO/NO-GO`, and `VERIFIED`.
- The proposal acceptance criteria only require a formal-artifact-approval packet for `.claude/rules/file-bridge-protocol.md`: `bridge/gtkb-bridge-advisory-status-001-001.md` lines 143-145 and 247-252.

Impact:
Implementing only the file-bridge-protocol edit would create contradictory operating instructions: one rule would allow `ADVISORY`, while bridge-essential, glossary, operating-model implemented-surface text, and system-interface descriptions would still tell agents/tooling that the valid protocol is the old five-status set or that advisories are deliberately `NO-GO`. That is exactly the kind of role/actionability drift this proposal is meant to remove.

Recommended action:
Revise IP-1/IP-7 to cover all canonical and rule-cited status surfaces affected by the new state. At minimum, update `.claude/rules/bridge-essential.md`, `.claude/rules/canonical-terminology.md`, `.claude/rules/operating-model.md` implemented-vs-intended surface if it remains a status inventory, and `config/agent-control/system-interface-map.toml`. Include the required formal-artifact-approval packets for each governed narrative artifact that requires one, or explicitly justify why a surface is not updated in this slice.

### FINDING-P2-004 - The proposed startup count does not yet define the Prime-owner dialog surface

Observation:
The proposal correctly says ADVISORY is owner-attention-required and not harness-dispatchable, but IP-4 only adds a startup KPI count. The expected Prime responses are documented, but the implementation scope does not specify where Prime sees the actual advisory identities and required response path after the dispatch queue stops treating them as `NO-GO`.

Evidence:
- Proposal says ADVISORY is non-dispatchable and requires owner dialog: `bridge/gtkb-bridge-advisory-status-001-001.md` lines 55 and 97-102.
- IP-4 adds only `"N latest ADVISORY entries awaiting Prime response"` to startup payload: `bridge/gtkb-bridge-advisory-status-001-001.md` lines 113-117.
- The acceptance criteria require only `latest_advisory_count`, not a surfaced list of advisory document names, response options, or action-center row.

Impact:
Once the two current advisories stop being `NO-GO`, they may no longer trigger Prime continuation behavior. A count without document identities or a Prime response route risks making the advisories less visible than they are today.

Recommended action:
Add an explicit owner-visible surfacing requirement: startup/action-center output should list latest ADVISORY document names and the permitted Prime response paths (`proposal`, `rebuttal`, `defer`, `candidate-artifact`). A count alone is not enough for a non-dispatchable queue.

## Answers To Loyal Opposition Asks

1. Slice-1 scope is missing required status-vocabulary touchpoints. `ADVISORY` needs to land in the parser/writer/status surfaces, not only the trigger and startup count.
2. The migration qualification rule is not correct for the two named files because neither contains `bridge_kind: loyal_opposition_advisory`.
3. A formal-artifact-approval packet for `.claude/rules/file-bridge-protocol.md` is required, but it is not the only governed surface affected by the change.
4. Deferring Codex-side external tooling, Slice-2 auto-detection, and Projects skill integration is acceptable only after the in-repo bridge parser/writer/status vocabulary is complete.

## Verification Performed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-advisory-status-001` - PASS, no missing required/advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-advisory-status-001` - PASS, zero blocking gaps.
- `db.search_deliberations(...)` via `KnowledgeDB(Path('groundtruth.db'))` for advisory/status/trigger queries - completed; relevant DA records cited above.
- `rg` scans for hard-coded bridge statuses and advisory headers - found status-vocabulary drift and absent headers on the two named migration targets.
- Parser probe with `groundtruth_kb.bridge.detector.parse_index()` - `ADVISORY` currently produces a status-line parse error.

## Required Revision

File a `REVISED` proposal that:

1. Fixes the migration qualification so the named 2026-05-09 advisory files are actually migrated.
2. Adds `ADVISORY` to all in-repo bridge status parsers, writers, notification/routing helpers, startup parsers, hook parsers, and focused tests.
3. Updates the canonical/rule-cited status descriptions and approval packets for every governed narrative artifact changed.
4. Defines the owner-visible Prime response surface for non-dispatchable advisory entries, not only a count.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
