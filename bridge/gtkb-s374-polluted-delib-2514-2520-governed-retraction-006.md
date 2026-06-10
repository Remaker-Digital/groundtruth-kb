# S374 Governed Retraction of Polluted DELIB-2514..2520 — Post-Implementation Report

bridge_kind: governance_advisory

Document: gtkb-s374-polluted-delib-2514-2520-governed-retraction
Version: 006
Date: 2026-05-30
Author: Prime Builder / Claude / harness B
Implements: GO at bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-004.md

## Implementation Note (incident + correction)

This report (`-006`) is the authoritative post-implementation report for this thread. There is no `-005` operative file: an earlier post-implementation report draft was attempted during a tool-output anomaly (interleaved/scrambled results) and did not persist to disk; INDEX never referenced it. During that same anomaly the first batch of seven `gt deliberations add` invocations was issued **missing the required `--summary` option** and therefore **failed** ("Missing option '--summary'"); no v2 rows were inserted by that attempt, and a `memory/MEMORY.md` line briefly asserted success before being corrected.

The retraction was then redone correctly: each insert was run as a single, individually-gated command (with `--summary`), and the results below were observed from a clean read-only channel. No data was lost — the failed first attempt left the DB unchanged at all-v1, and the append-only design has no destructive path. The owner was informed and authorized the redo via AUQ (S374, 2026-05-30, "Fix it now").

## Summary

The governed retraction approved at `-004` is implemented and verified. Seven append-only v2 deliberation rows were inserted for `DELIB-2514` through `DELIB-2520`, each superseding its v1 fixture-shape-contamination row. All seven v1 rows are preserved; all ten pre-existing v1 packet files (`DELIB-2511`..`DELIB-2520`) are byte-identical to their pre-implementation baseline; and the three legitimate records `DELIB-2511`..`DELIB-2513` were not touched. Seven per-record formal-artifact-approval packets gated the inserts; each inserted row's `content_hash` equals its packet's `full_content_sha256`.

This thread is `bridge_kind: governance_review`; no `scripts/implementation_authorization.py` packet was required (the per-record formal-artifact-approval packets are the mutation authorization, and the target paths are outside the implementation-start gate's protected prefixes).

## Specification Links

- GOV-ARTIFACT-APPROVAL-001 v3
- DCL-ARTIFACT-APPROVAL-HOOK-001 v3
- ADR-ARTIFACT-FORMALIZATION-GATE-001 v3
- PB-ARTIFACT-APPROVAL-001 v2
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 v1
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 v1
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 v1
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 v1
- SPEC-AUQ-POLICY-ENGINE-001
- SPEC-AUQ-NO-LLM-CLASSIFIER-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v3
- DELIB-0835

## Owner Decisions / Input

Authorization chain recorded in `memory/pending-owner-decisions.md` with `detected_via: ask_user_question`:

- DECISION-0834 — retraction mechanism ("Governed retraction: new DELIB versions + per-record approval packets").
- DECISION-0842 — S374 workflow follow-on path.
- DECISION-0843 — narrowed scope to DELIB-2514..2520, preserving DELIB-2511..2513.
- DECISION-0845 — governance_review classification.
- Grouped per-record formal-artifact approval (S374, 2026-05-30): owner answered "Approve all 7 as grouped retraction" to the AUQ presenting the complete v2 record content for all seven ids (the `presented_to_user=true` / `transcript_captured=true` evidence in each packet's `explicit_change_request`).
- Correction authorization (S374, 2026-05-30): owner answered "Fix it now (redo + supersede the premature draft)" authorizing this report and the redone inserts.

Auto-approval was not used. The owner-decision ids for the grouped approval and the correction authorization are allocated at session Stop by the owner-decision-tracker; the verbatim answers are the binding evidence.

## Implementation Performed

1. Deterministic generator (`.gtkb-state/s374-retraction/gen_packets.py`, gitignored ephemeral tooling) produced, per id 2514..2520: a v2 body file and a formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-25NN-v2.json`. Packet `full_content` equals the body bytes; `full_content_sha256` computed over those bytes.
2. All seven packets validated: `python scripts/validate_formal_artifact_packet.py <packet>` → `packet_valid` (exit 0) for each.
3. Seven inserts (one per command, sequential, each individually gated), with `--summary`: `GTKB_FORMAL_APPROVAL_PACKET=<packet> python -m groundtruth_kb deliberations add --id DELIB-25NN --source-type bridge_thread --source-ref bridge/...-004.md --title "..." --summary "..." --content-file <body> --outcome informational --changed-by prime-builder/claude/B --change-reason "..." --session-id S374 --json`. Each returned `{"version": 2, "status": "ok"}`. `insert_deliberation()` computed each v2 version via `_next_deliberation_version(id)`.
4. No v1 row, v1 packet file, or DELIB-2511..2513 record was modified or deleted.

## Spec-to-Test Mapping and Verification Evidence

Observed from a clean read-only channel (SQLite `mode=ro` + SHA-256) after the corrected inserts. All checks PASS:

| Spec(s) | Check | Observed result |
|---|---|---|
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, DCL-PROJECT-AUTHORIZATION-ENVELOPE-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (append-only) | Version census (rowid-deduped): DELIB-2514..2520 each have versions [1,2]; no v1 removed | PASS (7/7 = [1,2]) |
| Scope boundary (DECISION-0843) | DELIB-2511..2513 remain versions [1] with original source_ref | PASS (2511=`S-2026-05-30-pauth-agent-red-hygiene-cluster`, 2512=`...grill-suppression-per-document-lease`, 2513=`...lease-substitution-asap-directive`) |
| GOV-ARTIFACT-APPROVAL-001, DCL-ARTIFACT-APPROVAL-HOOK-001, ADR-ARTIFACT-FORMALIZATION-GATE-001, PB-ARTIFACT-APPROVAL-001 | Each v2 row `content_hash` == packet `full_content_sha256`; `changed_by=prime-builder/claude/B`; `source_ref`=GO file | PASS (7/7 match=True) |
| Append-only retention | All 10 pre-existing v1 packet files byte-identical to pre-implementation SHA-256 baseline | PASS (10/10 baseline match) |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This table is the spec-to-test mapping; observed results recorded | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | INDEX updated; this report filed; bridge files append-only | PASS |

Real per-id v2 `content_hash` (== packet `full_content_sha256`): 2514=`7c3e5524…`, 2515=`7b95cf04…`, 2516=`25759764…`, 2517=`558ae091…`, 2518=`55e14bf7…`, 2519=`6d6a52bd…`, 2520=`58ba8cf9…`. (DB rowids 2682–2688; changed_at 2026-05-31T00:49–00:50Z.)

v1 packet baseline (unchanged post-implementation): 2511=`3344cb5a…`, 2512=`2ecab6f1…`, 2513=`bffb0549…`, 2514=`983e11e4…`, 2515=`59f4eb85…`, 2516=`8cd67739…`, 2517=`eb8b66f3…`, 2518=`639b6798…`, 2519=`88fed0f0…`, 2520=`eca98958…`.

## Preflight Re-run

Applicability and clause preflights are re-run against this operative report after INDEX update; observed results presented in the session transcript at filing time. Loyal Opposition re-runs both at verification per `.claude/rules/codex-review-gate.md`. The Specification Links set is unchanged from the GO'd `-003`.

## Files Changed / Commit Scope

Committable change set:

- `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2514-v2.json` .. `-2520-v2.json` (7 approval packets)
- `memory/MEMORY.md` (S374 addendum, corrected to accurate completed state)
- `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-006.md` (this report) + `bridge/INDEX.md`

Not committed (by design): `groundtruth.db` is gitignored runtime state (the 7 v2 rows are live in MemBase); `.gtkb-state/s374-retraction/` is gitignored ephemeral tooling.

## Recommended Commit Type

`fix:` — repairs bug-produced polluted MemBase records via append-only supersession. No Python source under tracked paths was modified (the generator is gitignored ephemeral tooling), so ruff gates do not apply to the committable set.

## Open Follow-On (OUT of this thread's scope)

1. Root-cause fix: the Slice 4 auto-archive path allowed fixture-shape `decision_id=DECISION-0001` source_refs to reach a production insert. Recommend follow-on WI: "Fix auto-archive root-cause: reject fixture-shape DECISION-0001 source_refs; fail-closed on placeholder decision_ids."
2. Provenance DELIB (`DELIB-S374-SLICE-4-FIXTURE-CONTAMINATION-PROVENANCE`) per S358 IP-8 precedent — deferred per DECISION-0843.
3. Process lesson (this session): sequence evidence-claiming artifacts AFTER observing the evidence; never co-batch mutations with the report that asserts their results; one protected mutation per message on contended/flaky channels.
