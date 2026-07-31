NO-GO
::init gtkb lo
::open test

bridge_kind: lo_verdict
Document: gtkb-wi5664-provenance-valid-config-baseline-capture
Version: 004
Date: 2026-07-25 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5664-provenance-valid-config-baseline-capture-003.md
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f96b3-87b3-7af2-a7e6-06443b2ab0b3
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop

# Loyal Opposition Verdict — WI-5664 Configuration Baseline

## Verdict

NO-GO. The five-file capture proposal conflicts with the owner’s governing isolation decision and does not prove the actual WI-5664 skill-reference correction.

## First-Line Role Eligibility Check

- The current Codex A session envelope resolves as `loyal-opposition`, with readable worker-role provenance and session context `019f96b3-87b3-7af2-a7e6-06443b2ab0b3`.
- The latest live state was rechecked as `REVISED` version 003 immediately before claim/publication.
- `GOV-FILE-BRIDGE-AUTHORITY-001` authorizes Loyal Opposition to issue this NO-GO through the governed publisher.

## Review Independence

- Revision author context: `019f9329-a174-7763-8f7e-29679f39e6bd`.
- Reviewer context: `019f96b3-87b3-7af2-a7e6-06443b2ab0b3`.
- Both are readable and distinct; the session-context independence gate passes.

## Applicability Preflight

Executed `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5664-provenance-valid-config-baseline-capture`.

- packet_hash: `sha256:cee78d00105ca645cbf6151b08d3399488e274b31f443933fa1144255dc6ea36`
- bridge_document_name: `gtkb-wi5664-provenance-valid-config-baseline-capture`
- content_file: `bridge/gtkb-wi5664-provenance-valid-config-baseline-capture-003.md`
- operative_file: `bridge/gtkb-wi5664-provenance-valid-config-baseline-capture-003.md`
- candidate_evidence_hash: `sha256:8642301f238b2bc37898d7317c797b1eaf1af758db180b67a7eb711e70e5e0c1`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

## Clause Applicability

Executed `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5664-provenance-valid-config-baseline-capture`.

- Bridge id: `gtkb-wi5664-provenance-valid-config-baseline-capture`; operative file: `bridge/gtkb-wi5664-provenance-valid-config-baseline-capture-003.md`.
- must_apply: 3; evidence gaps: 0; blocking gaps: 0; exit: 0.

## Prior Deliberations

- `DELIB-202667193` — authorizes the skill-rename reference sweep but preserves each per-slice gate.
- `DELIB-202667194` — requires exact isolation of skill-rename changes and explicitly excludes the un-GO’d WI-5640 `.claude/rules` to `config/agent-control/gtkb-*` file-move apply from sweep commits.

## Positive Confirmations

- Version 003's author metadata is readable and its full three-version chain was reviewed.
- The recorded preflights pass: no required specification is missing and no mandatory clause gap is reported.
- The proposal's five hashes, three-copy command-surface comparison, 38 projection checks, and 14 focused tests are reproducible as baseline observations.

## Findings

### F1 — P1 — Proposed commit conflicts with the controlling owner isolation decision

**Observation.** `DELIB-202667194` says the un-GO’d WI-5640 file-move apply must be excluded and left uncommitted; it specifically identifies the `.claude/rules/*` to `config/agent-control/gtkb-*` migration as commingled work. Version 003 names precisely five untracked `config/agent-control/gtkb-*` targets, cites only `DELIB-202667193`, and offers no bounded preimage/hunk proof that excludes the WI-5640 migration.

**Impact.** WI-5664 could commit excluded, unverified WI-5640 apply under a skill-rename authorization, violating the owner’s explicit isolation constraint.

**Required revision.** Either route this configuration migration through a separately authorized WI-5640 lifecycle, or exclude these five file-move targets from WI-5664. A revised skill-rename slice must cite `DELIB-202667194` and provide a reproducible old-to-new reference inventory plus a post-commit assertion that no excluded `config/agent-control/gtkb-*` migration line enters the commit.

### F2 — P1 — The proposal does not verify the requested skill-reference correction

**Observation.** The candidate baseline files retain bare skill references, including `verify` references in the auto-finalization, review-gate, file-bridge-protocol, and LO rule candidates and a `bridge-propose` reference in the command-surface candidate. Version 003 checks byte equality and projections but defines no old-to-`gtkb-*` inventory or zero-match assertion.

**Impact.** The proposal can pass all stated gates while preserving the stale references that WI-5664 exists to repair.

**Required revision.** Name every intended bare-to-prefixed substitution, add an absence/inventory assertion across canonical, mirror, and command-surface files, and execute it before requesting GO.

### F3 — P2 — Working-byte equality does not prove staged/blob equality

**Observation.** The five candidates are `text eol=lf`, while at least the auto-finalization and file-bridge candidates contain CRLF working bytes. Git can normalize them to LF on staging, but version 003 compares only working-byte hashes.

**Impact.** The claimed exact-byte acceptance criterion is ambiguous at commit time.

**Required revision.** Define the acceptance hash over the staged Git blob (or explicitly over LF-normalized canonical bytes) and include a staged/blob-level equality check.

## Required Revisions

1. Respect and cite `DELIB-202667194`; do not commit WI-5640 file-move apply under WI-5664.
2. Provide an exact skill-reference old-to-new inventory with zero-match assertions for retired bare names.
3. Make byte-integrity verification use staged blobs or documented LF-normalized bytes.

## Commands Executed

```text
gt bridge show gtkb-wi5664-provenance-valid-config-baseline-capture --json --compact
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5664-provenance-valid-config-baseline-capture
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5664-provenance-valid-config-baseline-capture
gt deliberations get DELIB-202667193 --json
gt deliberations get DELIB-202667194 --json
```

## Owner Action Required

None.

Skills applied: gtkb-bridge, gtkb-proposal-review
