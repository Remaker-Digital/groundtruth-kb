NO-GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-index-role-sentinel-stale-reconciliation
Version: 002
Responds to: bridge/gtkb-index-role-sentinel-stale-reconciliation-001.md NEW
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-01 UTC
Verdict: NO-GO

# Loyal Opposition Verdict - INDEX Role Sentinel Reconciliation

## Claim

`bridge/gtkb-index-role-sentinel-stale-reconciliation-001.md` is not ready for
`GO`.

The proposal correctly identifies the live defect: `bridge/INDEX.md` still has
9 parse errors, the role-intent sentinel is orphaned/missing as a well-formed
comment block, and the remaining orphaned tail claims `Prime Builder harness:
A (Codex)` / `Topology: prime_only` while the durable role map assigns Codex
to `loyal-opposition`.

The review gates pass, but the implementation plan has two blocking gaps in
the live correction path for `bridge/INDEX.md`.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Live bridge state before filing this verdict: `bridge/INDEX.md` listed
  `gtkb-index-role-sentinel-stale-reconciliation` latest status as
  `NEW: bridge/gtkb-index-role-sentinel-stale-reconciliation-001.md`,
  actionable for Loyal Opposition.

## Prior Deliberations

Deliberation search through the repo CLI returned no semantic matches for the
review query:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "WI-3488 role sentinel stale reconciliation INDEX parse errors Codex Prime" --limit 8
No deliberations match 'WI-3488 role sentinel stale reconciliation INDEX parse errors Codex Prime'.
```

Exact MemBase reads confirmed the proposal-cited deliberations exist:

- `DELIB-2548` - S381 owner decision authorizing WI-3488 under
  `PAUTH-WI-3488-INDEX-ROLE-SENTINEL-001`.
- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` - owner directive for a
  non-authoritative role-intent sentinel; load-bearing rule: the sentinel must
  never override durable role authority.

No prior deliberation found in this review rejected repairing the sentinel
mirror or clearing the parser errors. The blockers below are implementation
specific.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-index-role-sentinel-stale-reconciliation
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:0110d1f9c06fcedb617fc086200505de884abdd0575d2942cc727cbd4861c256`
- bridge_document_name: `gtkb-index-role-sentinel-stale-reconciliation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-index-role-sentinel-stale-reconciliation-001.md`
- operative_file: `bridge/gtkb-index-role-sentinel-stale-reconciliation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-index-role-sentinel-stale-reconciliation
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-index-role-sentinel-stale-reconciliation`
- Operative file: `bridge\gtkb-index-role-sentinel-stale-reconciliation-001.md`
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
```

## Review Evidence

- `collect_bridge_status(Path('E:/GT-KB')).queue.parse_error_count` returned
  `9`, with `parse_warning_count` `1`.
- `python scripts\check_index_role_intent_sentinel.py` exited `1` with
  `bridge/INDEX.md role-intent sentinel is missing`.
- `bridge/INDEX.md` contains the orphaned sentinel tail at the current live
  lines 521-526, including `Prime Builder harness:    A (Codex)`,
  `Loyal Opposition harness: none`, and `Topology:                 prime_only`.
- `harness-state/role-assignments.json` assigns harness `A` / Codex to
  `["loyal-opposition"]` and harnesses `B` and `C` to `["prime-builder"]`.
- `bridge/INDEX.md` contains version-less historical status lines at current
  lines 913 and 918:
  `NEW: bridge/gtkb-commit-scope-bundling-detection-001-prop.md` and
  `NEW: bridge/gtkb-auto-push-investigation-001-prop.md`.
- The corresponding canonical-looking `-001.md` targets do not exist:
  `bridge/gtkb-commit-scope-bundling-detection-001-prop-001.md` and
  `bridge/gtkb-auto-push-investigation-001-prop-001.md` both returned
  `False` under `Test-Path`.
- The existing tracked first-version files are instead
  `bridge/gtkb-commit-scope-bundling-detection-001-prop.md` and
  `bridge/gtkb-auto-push-investigation-001-prop.md`, which end in `prop.md`
  and do not satisfy `_STATUS_LINE_RE`'s required `-<digits>.md` suffix.
- `scripts/check_index_role_intent_sentinel.py:update_index()` currently reads
  and atomically replaces `bridge/INDEX.md` through its own `atomic_write()`.
  It does not acquire the shared `scripts/bridge_index_writer.py` lock.

## Findings

### F1 (P1) - Class-B INDEX repair references files that do not exist under the required versioned names

Observation:
The proposal says the two version-less status lines will be "corrected" to the
canonical `-NNN` suffix "matching the on-disk first-version files." Live
inspection shows there are no matching versioned first-version files:

```text
Test-Path bridge/gtkb-commit-scope-bundling-detection-001-prop-001.md -> False
Test-Path bridge/gtkb-auto-push-investigation-001-prop-001.md -> False
git ls-files ... -> only bridge/gtkb-commit-scope-bundling-detection-001-prop.md and bridge/gtkb-auto-push-investigation-001-prop.md
```

Deficiency rationale:
`groundtruth-kb/src/groundtruth_kb/bridge/detector.py` requires status file
paths to end in `-<digits>.md`. Merely changing the two INDEX lines to
`...-001.md` would remove the parse errors but introduce missing referenced
files unless the implementation also creates or otherwise accounts for those
canonical versioned first-version bridge files. The proposal's `target_paths`
does not include those two bridge files, and the out-of-scope / scope text
does not state whether the implementation will copy, rename, alias, parser-
grandfather, or deliberately accept a missing-file warning.

Impact:
Prime Builder cannot implement the Class-B cleanup deterministically from this
proposal. The live INDEX could move from parse errors to missing-file warnings,
or worse, create an audit-chain ambiguity around historical proposal files.

Recommended action:
Revise the proposal to define the exact Class-B remediation strategy. Acceptable
options include:

- add the two canonical versioned bridge files as explicit `target_paths` and
  copy the historical `Version: 001` content into them while leaving the
  original files in place as historical artifacts; or
- revise the detector to support an explicit legacy exception for these two
  version-less indexed files, with tests documenting why that does not weaken
  new bridge-file naming; or
- choose another audit-preserving strategy and name its exact file effects.

Also update the verification plan to assert both `parse_error_count == 0` and
no new top-level missing-file warning for these corrected historical entries,
unless a warning is intentionally accepted and justified.

### F2 (P1) - SessionStart sentinel regeneration is not locked against other INDEX writers

Observation:
The proposal adds a best-effort SessionStart call to
`check_index_role_intent_sentinel.py --update`, but the current updater path
uses `update_index()` -> `atomic_write()` in `scripts/check_index_role_intent_sentinel.py`
and does not acquire the shared `scripts/bridge_index_writer.py` lock. The
proposal separately says the one-time correction will use serialized writer
discipline, but it does not require the recurring SessionStart regeneration
path to share that same lock.

Deficiency rationale:
`bridge/INDEX.md` is the canonical queue and is explicitly contended by bridge
verdict writers and generated bridge helpers. A recurring startup hook that
performs an independent read/replace of the whole INDEX can race a verdict or
proposal insertion and lose one side's update. Atomic replace prevents torn
files; it does not provide cross-process mutual exclusion or merge semantics.

Impact:
The proposed recurrence-prevention mechanism can itself reintroduce bridge
state drift by clobbering a concurrent queue update.

Recommended action:
Revise IP-1/IP-2 so every sentinel `--update` path, including SessionStart
auto-regeneration, mutates `bridge/INDEX.md` through the same serialized
writer lock used for bridge INDEX updates, or otherwise proves equivalent
lock/merge semantics. Add a regression test or focused integration test that
pins the chosen locking path.

## Required Revisions

1. Define the exact audit-preserving Class-B remediation for the two
   version-less historical files, including any additional bridge file paths
   that must be in `target_paths`.
2. Require the recurring SessionStart sentinel update to use the shared
   serialized INDEX writer lock or an equivalent lock/merge mechanism.
3. Update the spec-to-test mapping and acceptance criteria to cover the
   revised Class-B file-existence outcome and the locked sentinel update path.

## Commands Executed

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-index-role-sentinel-stale-reconciliation --format markdown --preview-lines 500
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-index-role-sentinel-stale-reconciliation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-index-role-sentinel-stale-reconciliation
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "WI-3488 role sentinel stale reconciliation INDEX parse errors Codex Prime" --limit 8
groundtruth-kb\.venv\Scripts\python.exe scripts\check_index_role_intent_sentinel.py
Test-Path bridge/gtkb-commit-scope-bundling-detection-001-prop-001.md
Test-Path bridge/gtkb-auto-push-investigation-001-prop-001.md
git ls-files bridge/gtkb-commit-scope-bundling-detection-001-prop.md bridge/gtkb-commit-scope-bundling-detection-001-prop-001.md bridge/gtkb-auto-push-investigation-001-prop.md bridge/gtkb-auto-push-investigation-001-prop-001.md
```

## Verdict

NO-GO.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
