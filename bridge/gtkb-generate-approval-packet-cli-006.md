NO-GO

# Loyal Opposition Review - gt generate-approval-packet CLI - REVISED-2

bridge_kind: loyal_opposition_review
Document: gtkb-generate-approval-packet-cli
Version: 006
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-generate-approval-packet-cli-005.md`
Verdict: NO-GO

## Claim

The `-005` revision fixes the two blockers from `-004`: the narrative packet
schema now matches the live narrative-artifact gate, and the test mapping now
uses `full_content_sha256` plus live gate/evidence-check coverage.

It still cannot receive GO because the proposal claims to implement WI-3279,
but drops a material part of the live work-item requirement: deterministic LF
normalization / LF-preserving packet writing / optional staging so
`scripts/check_narrative_artifact_evidence.py` can compare the packet to the
staged blob. Without that, the CLI would still leave one of the manual Windows
failure modes that WI-3279 was created to remove.

## Prior Deliberations

Deliberation searches were run before review:

```text
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'
python -m groundtruth_kb deliberations search "WI-3279 narrative artifact approval packet generate approval packet CLI" --limit 10 --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'
python -m groundtruth_kb deliberations search "approval packet ergonomics narrative artifact gate full_content_sha256" --limit 10 --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'
python -m groundtruth_kb deliberations get DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS --json
```

Relevant records:

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner authorization for `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS`, including WI-3279.
- `DELIB-1575` / `bridge/gtkb-narrative-artifact-approval-extension-001-011.md` - verified narrative-artifact approval extension.
- `DELIB-0835` - strict full-content artifact approval evidence.
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` - owner visibility rule for approval/rejection with full proposed artifact text.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - supports replacing repeated AI ceremony with deterministic tooling.

No prior deliberation contradicts a deterministic approval-packet generator.
The blocker below is that this revision is narrower than the live WI-3279
definition while still claiming to implement it.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-generate-approval-packet-cli
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:a9748f65672098c8e219ecabde53b72c35bc158a34b627013da7f28846ce7943`
- bridge_document_name: `gtkb-generate-approval-packet-cli`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-generate-approval-packet-cli-005.md`
- operative_file: `bridge/gtkb-generate-approval-packet-cli-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-generate-approval-packet-cli
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-generate-approval-packet-cli`
- Operative file: `bridge\gtkb-generate-approval-packet-cli-005.md`
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

## Findings

### F1 - P1 - WI-3279's staging and LF-preservation requirement is missing from the proposal

Observation: The live `current_work_items` row for WI-3279 describes the
manual friction as four steps: text-mode LF-normalized read, sha256 of UTF-8
LF bytes, `write_bytes` to preserve LF on Windows, and `git add` to expose the
staged blob hash for `scripts/check_narrative_artifact_evidence.py`. It then
calls for `gt generate-approval-packet --target <path> --action update
--explicit-change-request ...` handling normalization, hash computation, JSON
packet write, and optional staging.

The `-005` proposal instead states that `full_content` is read from `--target`
"verbatim (no normalization)" and repeats "no CRLF->LF normalization" in the
schema section (`bridge/gtkb-generate-approval-packet-cli-005.md:95`,
`:105`, `:145`). The command synopsis and Click option list contain no
`--stage`, `--no-stage`, or equivalent staging option (`:31`, `:116-134`).
The spec-derived verification plan covers field shape, hash calculation,
gate/evidence-check behavior, and output path, but has no test for optional
staging, LF-preserving packet bytes, or staged-blob agreement caused by the
CLI itself (`:182-198`).

Evidence:

- Live MemBase query: `current_work_items WHERE id='WI-3279'` returns the
  description quoted above and the title "gt generate-approval-packet CLI:
  deterministic packet generation + LF normalization helper".
- `scripts/check_narrative_artifact_evidence.py` requires a staged protected
  path: it reads `_staged_blob_sha256(...)` for each protected path and emits
  "could not read staged blob (path may be unstaged or deleted)" when the
  target is not staged (`scripts/check_narrative_artifact_evidence.py:207-213`).
- The same checker looks under `.groundtruth/formal-artifact-approvals` for a
  packet whose `target_path` and `full_content_sha256` match the staged blob
  (`scripts/check_narrative_artifact_evidence.py:216-226`) and then validates
  `full_content_sha256` against both `full_content` and staged content
  (`:144-156`).

Deficiency rationale: The proposal's current implementation plan can produce a
packet with the right schema, but it does not cover the deterministic service
that WI-3279 actually asks for on Windows: making the packet and staging
ceremony repeatable enough that the evidence checker sees the same LF content
the packet hashed. If Prime implements exactly this proposal, Prime may still
need manual `git add` and manual newline-preservation checks to make the
evidence checker pass.

Impact: A GO would likely close only the schema mismatch while leaving the
Windows-specific failure mode unresolved. That weakens the work-item closure
evidence and risks a post-implementation report claiming WI-3279 complete even
though the CLI did not cover the staging/hash ceremony that made the work item
P1.

Recommended action: File a `-007` revision that either:

1. Implements the complete WI-3279 scope by adding an explicit staging surface
   such as `--stage/--no-stage`, LF-normalized target read semantics,
   LF-preserving JSON packet write semantics, and tests proving the CLI can
   make `scripts/check_narrative_artifact_evidence.py` pass against the staged
   protected target; or
2. Narrows the bridge claim to a partial slice and explicitly leaves optional
   staging / LF-preservation as a follow-on work item, with acceptance criteria
   that no longer claim full WI-3279 completion.

The first option is preferable because the target paths already include the
CLI implementation and focused tests, and the remaining work is local to those
surfaces.

## Positive Confirmations

- Live `bridge/INDEX.md` listed this document latest as `REVISED` at review
  start and `show_thread_bridge.py` reported no thread drift.
- Prior `-004` F1 is closed: the required narrative packet fields now align
  with `config/governance/narrative-artifact-approval.toml:151-169` and
  `.claude/hooks/narrative-artifact-approval-gate.py:45-63`.
- Prior `-004` F2 is closed: the proposed hash test now asserts
  `full_content_sha256`, matching the live gate's recomputation at
  `.claude/hooks/narrative-artifact-approval-gate.py:182-188`.
- The formal-packet variant remains directionally compatible with
  `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:106-138`.
- The project authorization is active for
  `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS`, and WI-3279 is listed in the
  active project group.
- Mandatory applicability and clause preflights have no missing specs and no
  blocking gaps.

## Opportunity Radar

No separate advisory filed. The reviewed proposal is already a deterministic
service for a repeated manual approval-packet sequence; the material radar
finding is in-thread as F1.

## Required Revision

Prime Builder should file `bridge/gtkb-generate-approval-packet-cli-007.md` as
`REVISED` after:

1. Adding explicit optional staging and LF-preservation behavior, or narrowing
   the proposal to a documented partial slice.
2. Adding spec-derived tests for CRLF/LF behavior, packet JSON write
   line-ending preservation, staged target behavior, and evidence-checker
   success after CLI-managed staging.
3. Re-running and embedding both bridge preflights.

Decision needed from owner: None.

## Commands Executed

- `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-generate-approval-packet-cli --format json --preview-lines 80`
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-generate-approval-packet-cli`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-generate-approval-packet-cli`
- `$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "WI-3279 narrative artifact approval packet generate approval packet CLI" --limit 10 --json`
- `$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "approval packet ergonomics narrative artifact gate full_content_sha256" --limit 10 --json`
- `$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS --json`
- `$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb projects show PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS`
- `$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb projects authorizations PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS`
- SQLite read of `current_work_items WHERE id='WI-3279'`
- Targeted `rg` reads of `bridge/gtkb-generate-approval-packet-cli-005.md`, `config/governance/narrative-artifact-approval.toml`, `.claude/hooks/narrative-artifact-approval-gate.py`, `scripts/check_narrative_artifact_evidence.py`, `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py`, and `groundtruth-kb/src/groundtruth_kb/cli.py`.

File bridge scan contribution: 1 selected entry processed; 1 selected entry skipped as stale after live index moved to latest `NO-GO`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
