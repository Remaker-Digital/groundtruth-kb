GO

# Loyal Opposition Review - Seed the Harnesses Registry Table (WI-3342 Slice A)

bridge_kind: lo_verdict
Document: gtkb-harness-registry-seed
Version: 002 (GO)
Author: Codex Loyal Opposition (harness A)
Date: 2026-05-16 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-harness-registry-seed-001.md

## Decision

GO. The proposal is approved for Prime Builder implementation within the
declared scope: add the deterministic seed migration, add the focused
spec-derived tests, regenerate `harness-state/harness-registry.json`, and run
the migration once against the live in-root MemBase so current harnesses `A`
and `B` appear in the `harnesses` table as `active`.

This approval is bounded to the proposal's authority boundary. It does not
approve the WI-3342 Slice B reader migration, retirement of
`harness-state/harness-identities.json` or
`harness-state/role-assignments.json`, FR9 `set-role` implementation, FR7
reviewer precedence, FR8 dispatch invocation surfaces, or any change that flips
role/identity authority from the legacy JSON files to the DB/projection.

## Applicability Preflight

- packet_hash: `sha256:609526047248631863cfb12daf31570e333b15c24d2ea092b53626d0cae33a4c`
- bridge_document_name: `gtkb-harness-registry-seed`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-registry-seed-001.md`
- operative_file: `bridge/gtkb-harness-registry-seed-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-harness-registry-seed`
- Operative file: `bridge\gtkb-harness-registry-seed-001.md`
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
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-2079` - owner-decided Antigravity Integration design, including the
  DB-backed `harnesses` registry table and generated SessionStart projection.
- `DELIB-2080` - role-portability amendment. Relevant because this seed is the
  prerequisite for enforcing FR9's active-harness eligibility against the
  registry rather than role-map membership alone.
- Owner AskUserQuestion of 2026-05-16, recorded in
  `memory/pending-owner-decisions.md`: the owner selected "Seed the harnesses
  table first" to resolve the dependency inversion found in the WI-3341 and
  WI-3340 NO-GOs.
- `bridge/gtkb-harness-role-portability-fr9-002.md` - prior NO-GO F1 requiring
  a registry-backed active-harness substrate before FR9 `set-role` can claim
  active-harness eligibility.
- Verified sibling threads:
  `bridge/gtkb-harness-registry-table-schema-008.md`,
  `bridge/gtkb-harness-registry-hot-path-projection-004.md`,
  `bridge/gtkb-harness-lifecycle-fsm-004.md`, and
  `bridge/gtkb-harness-cli-command-group-008.md`.

Deliberation search note: `python -m groundtruth_kb deliberations search
"Antigravity"` returned `DELIB-2080` and `DELIB-2079`; search for
`harnesses table` returned `DELIB-2079`. Direct retrieval confirmed
`DELIB-2079` and `DELIB-2080`. No conflicting prior deliberation was found.

## Review Findings

No blocking findings.

## Positive Confirmations

- Live `bridge/INDEX.md` showed latest status `NEW` for
  `gtkb-harness-registry-seed` before this verdict; the entry was actionable
  for Loyal Opposition review.
- The full bridge thread was loaded with `show_thread_bridge.py`; only version
  `001` existed and no thread drift was reported.
- Mandatory applicability preflight passed with `missing_required_specs: []`
  and `missing_advisory_specs: []`.
- Mandatory clause preflight passed with zero evidence gaps and zero blocking
  gaps.
- The proposal includes required implementation-start metadata: `target_paths`,
  Project Authorization, Project, Work Item, Requirement Sufficiency, and a
  spec-derived verification plan.
- The cited project authorization is active for
  `PROJECT-HARNESS-REGISTRY-REFACTOR`, includes
  `REQ-HARNESS-REGISTRY-001`, has no expiry, and the project membership list
  includes `WI-3342`.
- Current live DB inspection reported `KnowledgeDB.list_harnesses() == []`,
  and `harness-state/harness-registry.json` currently contains an empty
  `harnesses` array. The proposal's seed premise matches current state.
- Target paths are in `E:\GT-KB` and do not touch `applications/` or any
  out-of-root live dependency.
- The proposed tests map to `REQ-HARNESS-REGISTRY-001` FR1 table population
  and FR5 projection regeneration, and include idempotence/skipped-harness
  behavior for reruns.

## Implementation Notes for Prime

- The post-implementation report should record the exact command/interpreter
  used to run the one-time seed. In this dispatch shell, the bare `gt` command
  is not on PATH and the root/global `python` cannot import `groundtruth_kb`;
  the repo package was available through `groundtruth-kb/.venv`. This is not a
  GO blocker, but verification will need reproducible command evidence.
- If the implemented root-level script depends on package imports, it should be
  runnable by the command the report claims, either by using the project venv
  command explicitly or by bootstrapping `groundtruth-kb/src` consistently with
  other root `scripts/` utilities.
- The live seed evidence should include both the `harnesses` table state and
  the regenerated projection state showing `A` and `B` at `status = active`.

## Opportunity Radar

No new material deterministic-service candidate. This proposal itself converts
manual table seeding into a deterministic, idempotent migration, which is the
appropriate automation surface for the work.

## Commands Executed

```text
Get-Content bridge/INDEX.md
Result: live latest status for gtkb-harness-registry-seed was NEW.

python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-harness-registry-seed --format markdown
Result: full thread loaded; status chain NEW -> bridge/gtkb-harness-registry-seed-001.md.

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-seed
Result: preflight_passed true; missing_required_specs []; missing_advisory_specs [].

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-seed
Result: exit 0; evidence gaps 0; blocking gaps 0.

gt deliberations search "harness registry seed WI-3342 REQ-HARNESS-REGISTRY-001 DELIB-2079 DELIB-2080"
Result: not executable in this shell because gt is not on PATH.

groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations search "Antigravity"
Result: DELIB-2080 and DELIB-2079.

groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations search "harnesses table"
Result: DELIB-2079.

groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations get DELIB-2079
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations get DELIB-2080
Result: direct owner-decision records found. DELIB-2079 output hit a Windows
cp1252 Unicode display error after printing the relevant title/summary; direct
retrieval still confirmed the record.

groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb projects authorizations PROJECT-HARNESS-REGISTRY-REFACTOR --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb projects show PROJECT-HARNESS-REGISTRY-REFACTOR --json
Result: active project authorization found; project membership includes WI-3342.

groundtruth-kb/.venv/Scripts/python.exe -c "from groundtruth_kb.config import GTConfig; from groundtruth_kb.db import KnowledgeDB; c=GTConfig.load(); db=KnowledgeDB(db_path=c.db_path); print(c.db_path); print(db.list_harnesses())"
Result: db path E:\GT-KB\groundtruth.db; current harness list [].

Get-Content harness-state/harness-registry.json
Result: projection file exists and currently has "harnesses": [].

groundtruth-kb/.venv/Scripts/python.exe -X utf8 -c "<read REQ-HARNESS-REGISTRY-001>"
Result: REQ-HARNESS-REGISTRY-001 v2 status specified; FR1 and FR5 support this seed/projection slice; FR9 explains the downstream active-harness role-portability dependency.
```

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
