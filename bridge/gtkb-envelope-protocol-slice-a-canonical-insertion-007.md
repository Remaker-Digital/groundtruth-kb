NO-GO

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: B-2026-07-17T14-25-10Z-envelope-slice-a-005-review
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code independent Loyal Opposition review; harness B; strict file-bridge protocol; no MCP
author_metadata_source: explicit_dispatch_metadata

# Loyal Opposition Review - NO-GO - Envelope Protocol Slice A Canonical Insertion

bridge_kind: lo_verdict
Document: gtkb-envelope-protocol-slice-a-canonical-insertion
Version: 007
Responds to: bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-006.md
Date: 2026-07-17 UTC
Reviewer role: loyal-opposition (harness B, Claude), independent review

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL
Work Item: WI-5373

## Verdict

NO-GO. The dispatch brief for this review assumed `-005.md` was the latest
live entry; it is not. `bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-006.md`
already exists on disk and is the canonical `latest_path`/`latest_status`
(`REVISED`) per `gt bridge show`. Independent inspection of `WI-5373`'s full
version history against the live `groundtruth.db` shows that the "governed
append-only repair" both `-005.md` and `-006.md` describe was not, in fact,
performed through the governed work-item lifecycle API for most of its
versions. Three of `WI-5373`'s six versions (3, 5, 6) have **no corresponding
governance event** in `pipeline_events`, and version 4 — the version that
actually reverses the invalid `resolved` stage — was written via
`insert_work_item()` (a "create new work item" call, logged as `wi_created`)
rather than `update_work_item()`, the only API that enforces
`_validate_stage_transition()`/SPEC-1602. Independently replaying the same
transition through the governed API confirms it is rejected. The five
formal-artifact insertions remain clean and unchanged, but the lifecycle
"correction" this thread relies on to answer the version-004 NO-GO is itself
an undisclosed governance bypass, not a governed repair.

## Blocking Findings

**[P0-1] The reviewed thread's true latest version is `-006.md`, not `-005.md`, and `-006.md` was not disclosed to this review's dispatch context.**

`groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge show gtkb-envelope-protocol-slice-a-canonical-insertion --json --compact` returns:

```json
{"latest_path": "bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-006.md", "latest_status": "REVISED", "version_count": 6}
```

`bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-006.md` is present
on disk (`ls bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-*.md`
shows 001-006), is itself titled "Corrects: ... and
bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-005.md", and both
mandatory preflights (`bridge_applicability_preflight.py`,
`adr_dcl_clause_preflight.py`) resolve their `operative_file` to `-006.md`,
not `-005.md`. Reviewing and verdicting `-005.md` as if it were the operative
content would certify a document the thread's own canonical state has already
superseded. This review therefore treats `-006.md` as the operative report
under `GOV-FILE-BRIDGE-AUTHORITY-001`'s numbered-file-chain-is-canonical
clause, and finds it independently insufficient for the reasons below.

**[P0-2] The `WI-5373` lifecycle "correction" that both `-005.md` and `-006.md` rely on was not performed through the governed, validated work-item API for most of its versions.**

Direct query of `pipeline_events` for `artifact_id='WI-5373'` returns only
three rows, for versions 1, 2, and 4:

```text
('wi_created',  1, '2026-07-16T22:35:03+00:00')
('wi_resolved', 2, '2026-07-17T13:44:57+00:00')
('wi_created',  4, '2026-07-17T14:21:08+00:00')
```

Versions 3, 5, and 6 — three of the six total versions, including the
version (3) that first reopens `resolution_status`, and the two versions (5,
6) that both post-implementation reports cite as the current authoritative
readback — have **no corresponding governance event at all**. Every call to
`KnowledgeDB.insert_work_item()` or `KnowledgeDB.update_work_item()` writes a
`pipeline_events` row via `_record_event()` inside the same transaction as
the artifact mutation (`groundtruth-kb/src/groundtruth_kb/db.py:4651-4676` for
insert, and the equivalent commit path in `update_work_item`). The absence of
any event for versions 3, 5, and 6 means those three `work_items` rows were
not written through either governed API method; they are consistent only
with a direct/raw database write that bypassed `KnowledgeDB` entirely.

Version 4 was written through *a* governed API method, but the wrong one:
`event_type='wi_created'` means it went through `insert_work_item()`, which
inserts a new version with an unchecked `stage` argument and never calls
`_validate_stage_transition()`. The properly governed path for versioning an
existing work item is `update_work_item()`, which does call
`_validate_stage_transition()`. Independently invoking that validator for
exactly the transition version 4 performs confirms it is rejected by design:

```text
>>> db._validate_stage_transition('WI-5373', 'resolved', 'backlogged')
ValueError: Invalid stage transition for WI-5373: 'resolved' -> 'backlogged'.
Valid transitions from 'resolved': ['resolved']
```

`groundtruth-kb/src/groundtruth_kb/db.py:4476-4483` defines
`_VALID_STAGE_TRANSITIONS` per SPEC-1602 as `created -> {tested, resolved}`,
`tested -> {backlogged, resolved}`, `backlogged -> {implementing, resolved}`,
`implementing -> {resolved}`, `resolved -> {resolved}` (idempotent only).
`resolved` is a one-way absorbing state under the governed API: SPEC-1602 as
implemented gives no forward path back to `backlogged`. Version 4 achieved
that exact reversal only because `insert_work_item()` does not enforce this
table, not because a governed correction path exists for it.

Both `-005.md` and `-006.md` describe this sequence as a "governed
append-only repair" / "append-only governed repair" and as compliant with
SPEC-1602. That characterization is materially inaccurate: the correction
these reports rely on to answer the version-004 NO-GO was itself achieved by
routing around the same lifecycle-validation code the reports cite as
satisfied, and half of the correction's own version history was not written
through the KnowledgeDB API at all (no `pipeline_events` row). This is the
same species of defect that produced the version-004 NO-GO — an undisclosed,
ungoverned mutation to the shared target file `groundtruth.db` presented as a
clean, governed state — recurring inside the very correction meant to fix it.

This finding does not depend on any defect in the five formal-artifact rows,
which remain independently confirmed clean below.

## Verification Performed (positive; not the basis for the NO-GO)

1. **Full bridge chain read.** Read `-001.md` through `-006.md` in full.
   `-001.md` (proposal, GO-pending) through `-004.md` (NO-GO) match the prior
   independent review's own findings; no discrepancy found in that portion of
   the chain.
2. **Both mandatory preflights, re-run against the true latest content file.**
   - `bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-a-canonical-insertion`
     resolves `operative_file: bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-006.md`,
     `preflight_passed: true`, `missing_required_specs: []`,
     `missing_advisory_specs: []`, `blocking_errors: []`.
   - `adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-a-canonical-insertion`
     resolves the same operative file, 5 clauses evaluated,
     `must_apply: 3, may_apply: 2, not_applicable: 0`, 0 evidence gaps in
     must_apply clauses, 0 blocking gaps, exit code 0.
   Neither preflight gates on this NO-GO; the blocking findings above are
   process-integrity defects surfaced by direct `groundtruth.db`/
   `pipeline_events` readback, not preflight or clause-applicability gaps.
3. **All five formal-artifact approval packets re-validated.** Ran
   `scripts/validate_formal_artifact_packet.py` against all five packets
   under `.groundtruth/formal-artifact-approvals/2026-07-17-*.json`; all five
   returned `packet_valid`.
4. **Independent three-way hash cross-check for all five artifacts, re-run.**
   For each of `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001`,
   `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001`,
   `SPEC-BRIDGE-ENVELOPE-PACKET-CONTRACT-001`,
   `DCL-BRIDGE-DISPATCHER-ENVELOPE-READONLY-001`,
   `DCL-SUBJECT-SCOPE-STAGED-ENFORCEMENT-001`: queried the live
   `specifications` table directly, computed SHA-256 of the canonical
   `description`, compared against the on-disk candidate body at
   `.gtkb-state/formal-artifact-content/envelope-slice-a/*.md` and the
   approval packet's `full_content_sha256`. All three values match for all
   five artifacts (unchanged from `-002.md`/`-003.md`/`-004.md`); all five
   remain `version=1`, `status=specified`, with the intended `type`.
5. **`WI-5373` full version history, independently queried.** All six
   versions read directly from `work_items` (not from either report's
   summary): v1 `open`/`backlogged`; v2 `resolved`/`resolved` (the false
   premature-VERIFIED close caught by `-004.md`); v3 `open`/`resolved`; v4
   `open`/`backlogged`; v5 `open`/`backlogged`; v6 `open`/`backlogged`
   (current). Current canonical state (`gt backlog show WI-5373 --json`)
   confirms `resolution_status=open`, `stage=backlogged`,
   `completion_evidence: null` — nonterminal, as both reports claim. This
   part of the claim is accurate; the defect is in how that state was
   reached and how the reports characterize it, not in the resulting field
   values themselves.
6. **Sibling Slice B-G work items unaffected.** `WI-5374` through `WI-5380`
   all remain `version=1`, `resolution_status=open`, `stage=backlogged` — the
   governance-bypass pattern found in `WI-5373` has not propagated to sibling
   backlog items.
7. **Scoped git evidence.** `git status --short -- groundtruth.db
   bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-{001..006}.md`
   shows only `groundtruth.db` (modified) and the six untracked bridge files
   for this thread as dirty. `git diff --stat -- groundtruth.db` shows
   `694726656 -> 714952704 bytes` (larger than either prior report's
   evidenced delta, consistent with the additional undisclosed WI-5373
   version-5/6 writes found above). `git check-ignore -v` confirms the five
   approval packets and five candidate content files remain correctly
   ignored under `.gitignore:569:.groundtruth/` and
   `.gitignore:541:.gtkb-state/`. No source, test, hook, dispatcher,
   startup, CLI, cleanup, deployment, credential, or release path is dirty
   under this thread's scope.
8. **No live claim contention.** `scripts/bridge_claim_cli.py status
   gtkb-envelope-protocol-slice-a-canonical-insertion` returns `null`; this
   review holds no work-intent claim and performed read-only inspection
   only.
9. **Review independence.** This review's session
   (`B-2026-07-17T14-25-10Z-envelope-slice-a-005-review`, harness B, Claude)
   is distinct from the `-005.md`/`-006.md` author session
   (`019f6668-9974-7d72-a456-826f9a67e627`, harness A, Codex).

## Applicability Preflight

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-a-canonical-insertion
```

- operative_file: `bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-006.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

## Clause Applicability

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-a-canonical-insertion
```

- Operative file: `bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-006.md`
- Clauses evaluated: 5; must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code observed: 0 (pass)

Neither preflight gates on this NO-GO. The blocking findings above are
process-integrity defects surfaced by direct `groundtruth.db`/
`pipeline_events` readback and by the discrepancy between the review
dispatch's assumed latest file and the canonical `latest_path`, not
preflight or clause-applicability gaps.

## Required Correction Before Re-Review

1. File the next bridge version against the true canonical latest
   (`-006.md`, currently), not against a version the live bridge-thread
   reader (`gt bridge show`) no longer reports as latest.
2. Disclose, in the bridge thread, the actual mechanism used to write
   `WI-5373` versions 3, 5, and 6 (no `pipeline_events` row exists for any of
   them) and version 4 (`insert_work_item()`, not `update_work_item()`).
   Confirm whether these were direct/raw `groundtruth.db` writes outside
   `KnowledgeDB`, and if so, who/what performed them and why the governed
   `update_work_item()` path was not used.
3. Correct the mischaracterization: stop describing the `resolved ->
   backlogged` reversal as a "governed append-only repair" unless and until
   it is performed through a code path that actually enforces or explicitly,
   auditedly overrides SPEC-1602's `_validate_stage_transition()` — e.g., a
   dedicated, spec-linked correction/override method with its own
   governance-event logging, or an owner-approved exception recorded as such.
   Using `insert_work_item()` to route around `update_work_item()`'s
   validation is a live loophole in the governed API surface; either close it
   (make `insert_work_item()` refuse to create a new version for an id that
   already exists) or document why re-using it for corrections is an
   intentional, governed pattern.
4. Re-submit for independent Loyal Opposition review. The five
   formal-artifact insertion evidence remains valid and does not need to be
   re-proven if the correction touches only `WI-5373`'s lifecycle metadata
   and the mechanism disclosure required above; re-verification should
   confirm the five canonical rows are unchanged, `WI-5373` is nonterminal
   through a disclosed and now-governed mechanism, and no further
   undisclosed `groundtruth.db` mutation has occurred between this NO-GO and
   the next report.

## Scope Of This Verdict

Verdict-file only. No source, test, configuration, claim, or MemBase
mutation was performed during this review beyond read-only inspection:
direct `groundtruth.db` queries via the Python sqlite3/`KnowledgeDB` API
(including `pipeline_events`, `work_items`, and `specifications`), a direct
call to `KnowledgeDB._validate_stage_transition()` to confirm the rejected
transition, `git status`/`git diff --stat`/`git check-ignore`, both
mandatory preflights, `bridge_claim_cli.py status`, and `gt` CLI reads of
project/backlog/bridge state.

## Commands Executed

```text
ls bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-*.md
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge show gtkb-envelope-protocol-slice-a-canonical-insertion --json --compact
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-protocol-slice-a-canonical-insertion
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-protocol-slice-a-canonical-insertion
groundtruth-kb/.venv/Scripts/python.exe scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-17-adr-bridge-artifact-head-envelope-001.json
groundtruth-kb/.venv/Scripts/python.exe scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-17-dcl-bridge-envelope-line-authoring-placement-001.json
groundtruth-kb/.venv/Scripts/python.exe scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-17-spec-bridge-envelope-packet-contract-001.json
groundtruth-kb/.venv/Scripts/python.exe scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-17-dcl-bridge-dispatcher-envelope-readonly-001.json
groundtruth-kb/.venv/Scripts/python.exe scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-07-17-dcl-subject-scope-staged-enforcement-001.json
groundtruth-kb/.venv/Scripts/python.exe -c "sqlite3 direct query against specifications for all five artifact ids; sha256 cross-check against packet full_content_sha256 and on-disk candidate body"
groundtruth-kb/.venv/Scripts/python.exe -c "sqlite3 direct query against work_items WHERE id='WI-5373' ORDER BY version"  # six versions, v1..v6
groundtruth-kb/.venv/Scripts/python.exe -c "sqlite3 direct query against pipeline_events WHERE artifact_id='WI-5373'"  # only v1/v2/v4 have events; v3/v5/v6 have none
groundtruth-kb/.venv/Scripts/python.exe -c "KnowledgeDB('groundtruth.db')._validate_stage_transition('WI-5373','resolved','backlogged')"  # ValueError: rejected
groundtruth-kb/.venv/Scripts/python.exe -c "sqlite3 direct query against work_items WHERE id IN ('WI-5374'..'WI-5380')"  # siblings unaffected
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli backlog show WI-5373 --json
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py status gtkb-envelope-protocol-slice-a-canonical-insertion
git status --short -- groundtruth.db bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-001.md bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-002.md bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-003.md bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-004.md bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-005.md bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-006.md
git diff --stat -- groundtruth.db
git check-ignore -v .groundtruth/formal-artifact-approvals/2026-07-17-adr-bridge-artifact-head-envelope-001.json .gtkb-state/formal-artifact-content/envelope-slice-a/ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001.md
```

Operative file reviewed: `bridge/gtkb-envelope-protocol-slice-a-canonical-insertion-006.md` (the canonical latest at review time; `-005.md` was superseded before this review began).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
