NEW

# Bridge author-metadata audit scanner (Slice 1, read-only)

bridge_kind: prime_proposal
Document: gtkb-bridge-metadata-audit-scanner
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-30 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: e36961e2-7da5-4877-9685-e12c2857fa45
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via owner direction

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-METADATA-COMPLIANCE-BRIDGE-AUTHOR-METADATA-COMPLIANCE-REMEDIATION-FORWARD-PREVENTION
Project: PROJECT-GTKB-BRIDGE-METADATA-COMPLIANCE
Work Item: WI-4938

target_paths: ["scripts/bridge_metadata_audit.py", "platform_tests/scripts/test_bridge_metadata_audit.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This is Slice 1 of the owner-authorized forward-prevention program
(`DELIB-20266647`) to remediate systemic non-compliance in bridge author
metadata. A cross-harness investigation confirmed three failure classes against
live `bridge/*.md` state: (1) missing required fields — Codex (harness A)
historical verdicts omit `author_session_context_id` (~53 files), and the corpus
shows larger gaps in `author_model_version` and `author_model_configuration`;
(2) present-but-static `author_session_context_id` — multiple harnesses stamp a
date/role-keyed constant (e.g. `openrouter-harness-f` x64,
`cursor-e-20260626-lo-autoproc-5` x84, `codex-gtkb-pb-2026-06-02` x30) that
passes `metadata_value_is_valid` while defeating review independence; (3)
present-but-inaccurate model identity from the WI-4885 interactive defaults.

This slice adds a single deterministic, **read-only** scanner,
`scripts/bridge_metadata_audit.py`, that measures the problem so the later
hardening (Slice 2), enforcement-parity (Slice 3), and grandfather-baseline
(Slice 4) slices have an objective baseline. The scanner reuses the existing
helpers in `scripts/bridge_author_metadata.py`
(`bridge_artifact_status`, `extract_author_metadata`, `author_metadata_gaps`,
`REQUIRED_AUTHOR_METADATA_FIELDS`) rather than re-implementing field logic, so
it stays definitionally aligned with the canonical contract. It iterates
status-bearing `bridge/*.md` artifacts, computes per-field / per-harness /
per-status compliance, flags static/non-unique `author_session_context_id`
values (same id reused across N or more distinct thread slugs), and emits
deterministic JSON plus a markdown summary under a runtime evidence directory
(`.gtkb-state/bridge-metadata-audit/`). It mutates no `bridge/` file and no
MemBase row.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — the Document Artifact Author Provenance
  Contract. The six `REQUIRED_AUTHOR_METADATA_FIELDS` are the provenance fields
  this contract governs; the scanner measures conformance to it. (Cited verbatim
  in `scripts/bridge_author_metadata.py` re the S389 incident.)
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail authority; the scanner
  reads the versioned `bridge/` file chain as the source of audit truth and
  never mutates it.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal carries
  Project / Work Item / Project Authorization linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  derives a test from the linked provenance contract.
- `GOV-STANDING-BACKLOG-001` — the work is tracked as WI-4938 under the program
  project.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the scanner produces a
  durable measurement artifact rather than transient analysis.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — same artifact-oriented
  framing for the audit baseline.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the scanner output is the
  lifecycle trigger input for Slice 4's grandfather audit record.

## Prior Deliberations

- `DELIB-20266647` — the owner decision authorizing this program
  (forward-prevention first; historical corpus grandfathered, no backfill). This
  proposal implements that decision's Slice 1.
- `INTAKE-b4928376` — "Bridge review eligibility is harness-agnostic; durable
  role is a fallback, not a review/verdict gate." Relevant because the
  author-metadata provenance fields (not harness id) are what the independence
  gate keys on; the scanner surfaces where those fields are absent or
  non-unique. This proposal does not change review eligibility; it measures
  provenance completeness.
- A Deliberation Archive search for prior author-metadata/provenance scanner
  work surfaced no superseding or conflicting prior decision; this scanner is
  net-new tooling.

## Owner Decisions / Input

This proposal depends on owner approval, recorded as:

- `DELIB-20266647` (AskUserQuestion, 2026-06-30): the owner selected
  **"Forward-prevention first"** for the program scope — build the deterministic
  audit scanner; harden the contract; wire write-time enforcement parity;
  grandfather the historical corpus with no rewrite/backfill of committed
  append-only files. This slice is the audit-scanner component of that decision.

No further owner decision is required to proceed with this read-only slice.

## Requirement Sufficiency

Existing requirements sufficient. The scanner measures conformance to the
already-established six-field provenance contract in
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001` and `scripts/bridge_author_metadata.py`
(`REQUIRED_AUTHOR_METADATA_FIELDS`). No new or revised requirement is needed for
a read-only measurement tool; the contract it measures already exists.

## Spec-Derived Verification Plan

| Linked spec | Derived test / evidence | Expected result |
|---|---|---|
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `test_bridge_metadata_audit.py`: fixtures with (a) a clean 6-field artifact, (b) a missing-field artifact, (c) a static-id artifact reused across distinct slugs are classified compliant / missing-field / static-id respectively | All three fixtures classified correctly |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the above test is derived directly from the provenance contract's field set and the static-id failure mode | test PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | test asserts the scanner opens files read-only and writes only under `.gtkb-state/`; no `bridge/` file mtime changes during a run | no bridge mutation |

Execution command (repo venv for reproducible evidence):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_metadata_audit.py -q --no-header
```

## Risk / Rollback

Risk surface is minimal: the artifact is a new read-only script plus its test;
it imports existing helpers, adds no new dependency, mutates no `bridge/` file
or MemBase row, and is not wired into any blocking gate in this slice (doctor/CI
consumption is a later slice). Worst case is an inaccurate report, which is
caught by the derived fixtures test. Rollback is reverting the single
implementing commit (the two new files); nothing else depends on them yet.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-bridge-metadata-audit-scanner`; no prior version is
deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat` — adds a net-new measurement capability (scanner script + test), not a
repair of existing behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
