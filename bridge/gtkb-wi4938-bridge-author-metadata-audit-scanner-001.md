NEW

# Defect-Fix Proposal — Slice 1: deterministic bridge author-metadata audit scanner (read-only)

bridge_kind: prime_proposal
Document: gtkb-wi4938-bridge-author-metadata-audit-scanner
Version: 001
Author: Prime Builder Cursor
Date: 2026-06-30T22:15:00Z

author_identity: Prime Builder Cursor
author_harness_id: E
author_session_context_id: cursor-pb-s522-metadata-compliance-wi4938
author_model: Composer
author_model_version: 2.5
author_model_configuration: Cursor interactive; session role Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-METADATA-COMPLIANCE-BRIDGE-AUTHOR-METADATA-COMPLIANCE-REMEDIATION-FORWARD-PREVENTION
Project: PROJECT-GTKB-BRIDGE-METADATA-COMPLIANCE
Work Item: WI-4938

target_paths: ["scripts/bridge_metadata_audit.py", "platform_tests/scripts/test_bridge_metadata_audit.py", "groundtruth-kb/src/groundtruth_kb/cli.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Claim

Bridge verdicts and proposals across harnesses carry inconsistent or corrupt
author metadata (missing `author_session_context_id`, static harness slugs like
`openrouter-harness-f`, inaccurate model defaults). This corrupts review
independence checks, blocks impl-start authorization, and produces false-positive
GO threads. WI-4938 delivers a **read-only** deterministic audit scanner as the
regression baseline and repair-queue input before write-time hardening (WI-4939–4940).

## Defect / Reproduction

Live audit (2026-06-30) of latest status-bearing bridge threads:

- **748** latest GO/VERIFIED threads missing `author_session_context_id`
- **127** latest GO/VERIFIED with synthetic/static session ids
- **49** active latest **GO** threads with bad metadata (blocking PB)
- Harness F: system prompt instructs `author_session_context_id: openrouter-harness-f`
  (`scripts/openrouter_harness.py` ~349–355); 19/19 recent F artifacts synthetic
- Harness D: same pattern with `ollama-harness-d`

Reproduction command (ad-hoc audit used in investigation):

```text
python .tmp/audit_bridge_meta.py
```

Impl-start fails with `author_session_context_missing` when GO lacks parseable session id
(`bridge/gtkb-project-level-approval-state-retirement-003.md` documents non-operative GO).

## In-Root Placement Evidence

All targets are in-root: `scripts/bridge_metadata_audit.py`,
`platform_tests/scripts/test_bridge_metadata_audit.py`,
`groundtruth-kb/src/groundtruth_kb/cli.py` (`gt bridge audit metadata` subcommand).

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — six required author metadata fields; audit verifies compliance.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge artifacts are audit records; scanner supports queue hygiene.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH/Project/WI linkage present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — tests map to scanner behavior.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all paths remain under GT-KB platform root.
- `GOV-STANDING-BACKLOG-001` — WI-4938 is the authorized slice-1 backlog item.

## Prior Deliberations

- `DELIB-20266647` — Owner decision: forward-prevention metadata compliance program (WI-4938–4941).
- `DELIB-20266105` — Defense-in-depth review-independence / write-time gates (WI-4829).
- `bridge/gtkb-wi4522-author-metadata-per-harness-resolution-006.md` — Prior per-harness resolution work; static slug regression remains.
- `bridge/gtkb-wi4829-self-review-write-time-gate-005.md` — Self-review gate relies on parseable session ids.

## Owner Decisions / Input

No new owner decision required. `PAUTH-PROJECT-GTKB-BRIDGE-METADATA-COMPLIANCE-BRIDGE-AUTHOR-METADATA-COMPLIANCE-REMEDIATION-FORWARD-PREVENTION` (DELIB-20266647) authorizes WI-4938 source/test implementation. Forbidden: rewrite/backfill of historical committed bridge files.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` and WI-4938 acceptance criteria define the audit contract. No new specification required before this read-only slice.

## Proposed Scope

1. Add `scripts/bridge_metadata_audit.py` — scan `bridge/*.md` status-bearing files; classify:
   - missing required author metadata fields
   - placeholder/invalid values
   - synthetic session id patterns (`*-harness-*`, `*-autoproc*`, constant slugs)
   - per-harness/per-status aggregates
2. Emit deterministic JSON + markdown reports (stable sort order).
3. Add `gt bridge audit metadata` CLI wrapper (`--json`, `--write-report`).
4. Tests in `platform_tests/scripts/test_bridge_metadata_audit.py` using fixture bridge files.

Out of scope (later slices): write-time rejection (WI-4940), harness prompt fixes (WI-4939), grandfather record (WI-4941).

## Specification-Derived Verification Plan

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_metadata_audit.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_metadata_audit.py --json
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_metadata_audit.py groundtruth-kb/src/groundtruth_kb/cli.py
```

Expected: tests PASS; scanner flags fixture files with missing/synthetic ids; CLI exits 0 on scan.

## Acceptance Criteria

- Scanner covers all six `REQUIRED_AUTHOR_METADATA_FIELDS` from `scripts/bridge_author_metadata.py`.
- Detects synthetic session id class used by F/D harness prompts.
- Deterministic output (same tree → same JSON).
- No mutation of bridge files.
- CLI subcommand documented in `--help`.

## Risks / Rollback

Low risk (read-only). Rollback: revert single commit; no bridge or MemBase mutation.

## Recommended Commit Type

fix — closes metadata audit gap (WI-4938 defect).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
