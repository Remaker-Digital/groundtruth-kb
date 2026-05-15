NO-GO

# Loyal Opposition Review - `gt bridge propose` Deterministic CLI

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-gt-bridge-propose-deterministic-cli-001.md`
Verdict: NO-GO

## Claim

The owner-approved Option C pivot is directionally correct: repetitive bridge
proposal scaffolding should move into deterministic tooling, with AI filling
only judgment-required sections. `WI-3318` is active and authorized, and the
proposal's token-reduction goal aligns with the deterministic-services
principle.

The proposal cannot receive GO yet because the listed implementation surface
does not cover the files needed to expose the command, the rendering/search
plan relies on optional dependencies that are not available to the base `gt`
CLI, and the proposed write path would create bridge files outside the existing
helper-mediated credential-scan and INDEX-control path.

## Prior Deliberations

Deliberation searches executed:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI WI-3318 gt bridge propose deterministic CLI" --limit 5
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "bridge propose helper INDEX credential scan helper-mediated bridge write" --limit 5
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE bridge proposal scaffolding deterministic service" --limit 5
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations get DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI --json
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations get DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE --json
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations get DELIB-1842 --json
```

Relevant records:

- `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` directly authorizes `WI-3318`
  and records the owner directive to build `gt bridge propose --kind <type>`
  as the deterministic-services pivot.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports moving repetitive
  artifact plumbing into services, and specifically lists bridge proposal
  scaffolding as a candidate.
- `DELIB-1552` verifies the prior DA read-surface/template pre-population work;
  this is relevant to the proposal's auto-populated Prior Deliberations claim.
- `DELIB-1842` is a prior bridge-helper NO-GO establishing that bridge helper
  improvements must preserve role authority, file existence checks, and safe
  INDEX behavior instead of introducing a governance-bypass mutation surface.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gt-bridge-propose-deterministic-cli
```

Observed:

- packet_hash: `sha256:e4c4684032657a4805b8e893850e9c65d3190e47495ce634ac61ad003852c3ac`
- bridge_document_name: `gtkb-gt-bridge-propose-deterministic-cli`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-gt-bridge-propose-deterministic-cli-001.md`
- operative_file: `bridge/gtkb-gt-bridge-propose-deterministic-cli-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gt-bridge-propose-deterministic-cli
```

Observed:

- Bridge id: `gtkb-gt-bridge-propose-deterministic-cli`
- Operative file: `bridge\gtkb-gt-bridge-propose-deterministic-cli-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory default invocation; exit code `0`

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Positive Confirmations

- `WI-3318` exists in `current_work_items` with `resolution_status=open` and
  `stage=created`.
- The active project authorization
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI`
  includes `WI-3318`, is active, and cites
  `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI`.
- The proposal includes `Specification Links`, `Requirement Sufficiency`,
  project/work-item metadata, target paths, and a specification-derived
  verification table.
- Both mandatory preflights report no missing required specs and no blocking
  clause gaps.

## Findings

### F1 - P1 - The target_paths list does not authorize the files needed to expose the CLI

Evidence:

- The proposal's `target_paths` list includes
  `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`,
  `groundtruth-kb/src/groundtruth_kb/bridge/proposal_templates/`,
  `groundtruth-kb/tests/test_cli_bridge_propose.py`, and
  `.claude/skills/bridge-propose/SKILL.md`
  (`bridge/gtkb-gt-bridge-propose-deterministic-cli-001.md:16`).
- The package exposes the installed `gt` command through
  `groundtruth_kb.cli:main` (`groundtruth-kb/pyproject.toml:54-55`).
- `groundtruth-kb/src/groundtruth_kb/cli.py` is the current command registry;
  a search of that file found no existing `bridge` group or `bridge propose`
  registration.
- The proposal also introduces
  `groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py`
  (`bridge/gtkb-gt-bridge-propose-deterministic-cli-001.md:108`), but that file
  is not included in `target_paths`.

Risk / impact:

Prime Builder would have to edit files outside the approved implementation
surface to make `gt bridge propose` reachable, or the implementation could pass
module-level tests while the actual `gt bridge propose` command is unavailable.
The omitted `proposal_autoload.py` path also creates an authorization mismatch
between the stated IP-3 helper module and the authorized file list.

Required revision:

Revise `target_paths` to include every required integration file, at minimum
`groundtruth-kb/src/groundtruth_kb/cli.py` and
`groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py`, or change the
implementation design so no hidden edits are needed. Add a verification case
that invokes the real console entrypoint path and proves
`gt bridge propose --help` resolves.

### F2 - P1 - The template/search plan relies on optional dependencies that the base `gt` CLI does not have

Evidence:

- The proposal states that templates use Jinja2 placeholders
  (`bridge/gtkb-gt-bridge-propose-deterministic-cli-001.md:76`).
- The base package dependencies contain only `click>=8.1`
  (`groundtruth-kb/pyproject.toml:26-28`).
- `jinja2>=3.1` is currently under the optional `web` extra, not the base CLI
  dependency set (`groundtruth-kb/pyproject.toml:30-35`).
- The proposal also says Prior Deliberations are generated by semantic DA
  search (`bridge/gtkb-gt-bridge-propose-deterministic-cli-001.md:110`), while
  `chromadb` is in the optional `search` extra
  (`groundtruth-kb/pyproject.toml:38-40`).
- The target paths do not include `groundtruth-kb/pyproject.toml`
  (`bridge/gtkb-gt-bridge-propose-deterministic-cli-001.md:16`).

Risk / impact:

The implemented command can work in a dev environment with extras installed
while failing for the base installed `gt` CLI with `ModuleNotFoundError`, or
silently degrading semantic-search behavior without tests that define the
fallback contract.

Required revision:

Choose and specify one dependency strategy:

1. Use stdlib-only rendering and existing `KnowledgeDB.search_deliberations`
   fallback behavior so the base CLI remains dependency-light.
2. Move required runtime dependencies into the base package and include
   `groundtruth-kb/pyproject.toml` in `target_paths`.

The revised verification plan must include a base-install smoke test or a
mocked/import-boundary test that proves `gt bridge propose --help` and
`--dry-run` work without installing the unrelated `web` extra.

### F3 - P1 - The proposed bridge file write path bypasses the existing helper-mediated safety path

Evidence:

- The proposal's implementation sketch writes directly to
  `bridge/<slug>-001.md`, then tells the author to fill placeholders before an
  INDEX update (`bridge/gtkb-gt-bridge-propose-deterministic-cli-001.md:96-103`).
- The canonical bridge skill says proposal filing must delegate file write plus
  INDEX update to the helper-mediated path, and that the helper performs
  credential scanning before writing `bridge/<topic-slug>-<version>.md` and
  inserting the INDEX entry (`.codex/skills/bridge/SKILL.md:56-60`).
- The helper skill exists specifically to avoid non-Write code paths bypassing
  the scanner-safe-writer hook; it scans `CREDENTIAL_PATTERNS + BASH_EXTRAS`,
  refuses force writes, never overwrites, and performs file-first plus atomic
  INDEX insertion (`.claude/skills/bridge-propose/SKILL.md:6-34`,
  `:140-157`).
- The bridge-propose helper's description is to write the proposal file and
  insert its `Document:`/`NEW:` entry under governance-safe credential scan and
  concurrency controls (`.claude/skills/bridge-propose/SKILL.md:1-19`).

Risk / impact:

The new CLI would create live-looking unindexed bridge files under `bridge/`
without the credential-scan, no-force, overwrite-refusal, and atomic INDEX
semantics that the existing helper was built to preserve. That repeats the
bridge-helper risk class covered by `DELIB-1842`: deterministic convenience is
valuable only if it preserves the bridge authority and safety invariants.

Required revision:

Revise the write model before implementation. Acceptable shapes include:

1. Generate drafts outside dispatchable bridge state, for example under a
   clearly non-dispatchable `.gtkb-state/bridge-propose-drafts/` location, then
   require the existing helper-mediated filing path after the judgment
   placeholders are filled.
2. Integrate with the existing bridge-propose helper for final write and INDEX
   update, with explicit credential-hit, duplicate-file, INDEX-conflict, and
   dry-run tests.

If direct `bridge/` draft creation remains in scope, the revised proposal must
define its non-dispatchable lifecycle, credential-scan behavior, overwrite
policy, preflight behavior, and cleanup semantics, and explain why it is not a
bypass of the current helper mandate.

### F4 - P2 - The proposal should clear its advisory preflight omissions before refiling

Evidence:

- The applicability preflight reported `missing_advisory_specs` for
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.
- The file-bridge pre-filing section says the expected result is
  `missing_required_specs: []` and `missing_advisory_specs: []`; any non-empty
  `missing_*_specs` list is a self-detected defect that should be revised
  before filing (`.claude/rules/file-bridge-protocol.md:84-92`).

Risk / impact:

This is not the main reason for the NO-GO, but it leaves the proposal short of
the bridge pre-filing standard and weakens the claim that generated proposals
will auto-populate all relevant Specification Links.

Required revision:

Add the missing advisory specs to `Specification Links`, or add explicit
nonapplicability rationale if Prime believes the applicability trigger is too
broad. Then rerun both preflights and include the fresh results.

## Required Revision

File a revised proposal that:

1. Expands `target_paths` to cover every integration file actually needed to
   expose and implement `gt bridge propose`.
2. Specifies a base-CLI dependency strategy for template rendering and
   deliberation search.
3. Routes final bridge writes through the existing helper-mediated safety path,
   or generates drafts in a non-dispatchable location with an explicit filing
   handoff.
4. Adds tests for real CLI registration, base dependency behavior,
   credential-scan refusal, duplicate target refusal, dry-run no-write
   behavior, and helper-mediated INDEX handling.
5. Clears the advisory preflight omissions or justifies them explicitly.

## Decision

NO-GO. The work item is worth prioritizing, but the current proposal needs a
revision before it is safe to implement.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
