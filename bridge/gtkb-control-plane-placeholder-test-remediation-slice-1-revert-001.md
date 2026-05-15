# Control-Plane Placeholder-Test Remediation — Slice 1: Revert 10 Specs From `verified`/`implemented` to `specified`

**Status:** NEW
**Author:** prime-builder (Claude harness B, Opus 4.7)
**Date:** 2026-05-14
**Session:** S350
**Source:** WI-3184 (rowid 4365)
**Recommended commit type:** `fix:` (this corrects an inaccurate spec lifecycle status; not a new feature)
**target_paths:** ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-*-SPEC-1816*.json", ".groundtruth/formal-artifact-approvals/2026-05-*-SPEC-1818*.json", ".groundtruth/formal-artifact-approvals/2026-05-*-SPEC-1819*.json", ".groundtruth/formal-artifact-approvals/2026-05-*-SPEC-1820*.json", ".groundtruth/formal-artifact-approvals/2026-05-*-SPEC-1821*.json", ".groundtruth/formal-artifact-approvals/2026-05-*-SPEC-1822*.json", ".groundtruth/formal-artifact-approvals/2026-05-*-SPEC-1823*.json", ".groundtruth/formal-artifact-approvals/2026-05-*-SPEC-1824*.json", ".groundtruth/formal-artifact-approvals/2026-05-*-SPEC-1826*.json", ".groundtruth/formal-artifact-approvals/2026-05-*-SPEC-1827*.json", "scripts/control_plane_revert_slice_1.py", "platform_tests/scripts/test_control_plane_revert_slice_1.py"]

---

## Summary

WI-3184 tracks control-plane placeholder-test remediation for 10 specs (the SPA / superadmin control-plane cluster) that were originally promoted to `verified` in S195 on the basis of placeholder GOV-12 test rows created in S198. Per the VERIFIED investigation at `bridge/spec-hygiene-spa-investigation-008.md`, S200 recycled those placeholder TEST IDs for SPEC-1837 (Log Retention), leaving the 10 control-plane specs with **zero current KB test linkage**. The S293 remediation (`bridge/spec-hygiene-spa-remediation-006.md` VERIFIED 2026-04-15) reverted them from `verified` to `implemented`, but left WI-3184 open as the hygiene follow-up because `implemented` is also factually unsupported in the absence of test evidence proving the implementations meet the specs.

This slice (Slice 1) finishes the lifecycle correction: revert all 10 specs further from `implemented` to `specified` so the recorded lifecycle state accurately reflects the test-evidence reality (specs exist; implementations and verification evidence are pending genuine spec-derived tests). Slice 1 does NOT modify any spec body; it changes only the `status` field. Slice 1 does NOT create the missing tests; that is downstream remediation tracked separately.

Note on WI-3184 description text: the WI title and description say "revert from verified to implemented," reflecting the S293 work. Current MemBase state for all 10 specs is already `implemented` (confirmed by version-history inspection of `groundtruth.db`). This proposal interprets the operative intent (per session direction and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`) as "revert to a lifecycle state consistent with zero test evidence," which is `specified`, not `implemented`. The WI's open hygiene-follow-up status is the authority for further reversion; the proposal records this interpretation explicitly so Codex can confirm or NO-GO with a different target status.

---

## Specification Links

- GOV-15 — Test fix approval gate; no autonomous fixes for failed tests. Spec-status revert is the conservative-fix path that avoids introducing unbacked test artifacts, satisfying the gate.
- GOV-FILE-BRIDGE-AUTHORITY-001 — Live bridge index authority; this proposal lives under the active bridge protocol.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — Implementation proposals must cite all relevant specifications; satisfied by this section.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — VERIFIED is conditional on test creation + execution derived from linked specs. The 10 specs violate this DCL at their previous `verified` status and continue to overstate evidence at `implemented`; reverting to `specified` aligns lifecycle to reality.
- GOV-STANDING-BACKLOG-001 — Standing backlog is the durable cross-session work authority. WI-3184 is the standing-backlog item authorizing this work.
- GOV-ARTIFACT-APPROVAL-001 — Formal artifact approval gate; status changes are governed mutations requiring per-spec approval packets.
- DCL-ARTIFACT-APPROVAL-HOOK-001 — Artifact approval hook must display full native proposal; implementation must generate packets that include each spec's full current row plus the proposed status field delta.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — Adopter applications live at `<gt-kb-root>/applications/<name>/`; the 10 affected specs are GT-KB-scoped governance for SPA control plane, satisfying root-boundary.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — Model project memory as a durable artifact graph; spec lifecycle accuracy is foundational to that graph.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — Artifact-oriented governance is the default project interpretation stance; spec-status accuracy is non-negotiable under this stance.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — Artifact lifecycle triggers require thresholds, states, and confirmation flows; the trigger here is "zero test linkage on a spec at `implemented`/`verified`" and the confirmation flow is the formal-artifact-approval packet per spec.
- SPEC-1816 — Superadmin Entitlement Management API (target).
- SPEC-1818 — SPA Console: Full Service Management (target).
- SPEC-1819 — SPA Console: Code-Free Runtime Configuration (target).
- SPEC-1820 — Allow/Block List Management (target).
- SPEC-1821 — Back-off and Retry Configuration (target).
- SPEC-1822 — Alert Threshold Configuration (target).
- SPEC-1823 — Notification Channel Configuration (target).
- SPEC-1824 — Feature Flag System (target).
- SPEC-1826 — SPA Test Execution Trigger (target).
- SPEC-1827 — Diagnostic Data Export for Claude Code (target).
- `.claude/rules/file-bridge-protocol.md` — Bridge protocol; this proposal conforms to its Mandatory Specification Linkage Gate and Mandatory Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` — Counterpart Review Gate; this proposal seeks Codex GO before implementation.
- `.claude/rules/project-root-boundary.md` — Project root boundary; all paths in `target_paths` are within `E:\GT-KB`.

---

## Prior Deliberations

- DELIB-0770 — Bridge thread: spec-hygiene-spa-remediation (6 versions, VERIFIED). Source DA record for the S293 verified→implemented revert and the standing WI-3184 follow-up.
- DELIB-0772 — Bridge thread: spec-hygiene-spa-investigation (8 versions, VERIFIED). Root-cause investigation establishing that S198 placeholder TEST IDs were recycled by S200 for SPEC-1837.
- DELIB-0775 — Bridge thread: spec-hygiene-untested-verified (8 versions, VERIFIED). Parallel hygiene track for untested-`verified` specs; provides the lifecycle-accuracy framing this slice extends.
- DELIB-1282 / DELIB-1283 / DELIB-1284 — Orphan-tagged duplicates of the above bridge-thread harvest records; cited for completeness so future sessions surface the original chain.
- `bridge/spec-hygiene-spa-investigation-001..008.md` — VERIFIED investigation; primary source for affected-spec inventory.
- `bridge/spec-hygiene-spa-remediation-001..006.md` — VERIFIED prior remediation closing the verified→implemented step; the present slice continues to `specified`.
- `independent-progress-assessments/spec-hygiene/S291-test-artifact-integrity-investigation.md` — S291 evidence cited in WI-3184 description.

No prior DA record proposes revert-to-`specified`; this slice is the first such proposal and the rationale is captured under §Summary and §Implementation Plan below.

---

## Owner Decisions / Input

Owner direction 2026-05-14 S350: "Please parallelize work and start as many priority backlog projects as possible" + "Please continue filing more backlog work" authorizes batch NEW filing of priority backlog proposals. Per-proposal Codex GO required before implementation. Channel: AskUserQuestion (DECISION-0583 — AUQ-resolved batch authorization). The 10 spec reverts will each require their own formal-artifact-approval packet at implementation time per `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`; that owner approval is not pre-collected here and is a per-implementation-step gate.

---

## Clause Scope Clarification (Bulk-Adjacent Operation)

This proposal touches 10 MemBase rows (`specifications` table, one new version per spec). That cardinality is bulk-adjacent and the `GOV-STANDING-BACKLOG-001 / CLAUSE-VISIBILITY-BULK-OPS` clause MAY apply. The proposal carries the evidence the clause expects:

1. **Inventory of affected items** — see §Affected Specs Inventory below. The inventory is the visibility artifact required by the clause and lists each spec's current status, proposed status, and per-spec rationale.
2. **Per-spec formal-artifact-approval packets at implementation time** — see `target_paths` `.groundtruth/formal-artifact-approvals/2026-05-*-SPEC-*.json` globs. Each spec status change is its own approval packet; no single bulk packet covers all 10. This decomposes the operation into 10 individually-reviewable mutations under `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`.
3. **This proposal is the review packet for the 10 reverts** — Loyal Opposition reviews the inventory, rationale, mechanics, and test plan in this single bridge document; Codex GO authorizes the script `scripts/control_plane_revert_slice_1.py` to execute, gated per-spec by the approval packets.

The operation is **not** an indiscriminate bulk update. It is a closed-set, individually-justified status correction with full per-item audit-trail and per-item approval gating. Cited evidence patterns: `inventory`, `formal-artifact-approval`.

---

## Affected Specs Inventory

| Spec ID    | Title                                              | Current status | Proposed status | Rationale                                                                                              |
|------------|----------------------------------------------------|----------------|-----------------|--------------------------------------------------------------------------------------------------------|
| SPEC-1816  | Superadmin Entitlement Management API              | implemented    | specified       | Zero current KB test linkage; S198 placeholder recycled by S200; `implemented` overstates evidence.    |
| SPEC-1818  | SPA Console: Full Service Management               | implemented    | specified       | Zero current KB test linkage; same root cause as above.                                                |
| SPEC-1819  | SPA Console: Code-Free Runtime Configuration       | implemented    | specified       | Zero current KB test linkage; same root cause.                                                         |
| SPEC-1820  | Allow/Block List Management                        | implemented    | specified       | Zero current KB test linkage; same root cause.                                                         |
| SPEC-1821  | Back-off and Retry Configuration                   | implemented    | specified       | Zero current KB test linkage; same root cause.                                                         |
| SPEC-1822  | Alert Threshold Configuration                      | implemented    | specified       | Zero current KB test linkage; same root cause.                                                         |
| SPEC-1823  | Notification Channel Configuration                 | implemented    | specified       | Zero current KB test linkage; same root cause.                                                         |
| SPEC-1824  | Feature Flag System                                | implemented    | specified       | Zero current KB test linkage; same root cause.                                                         |
| SPEC-1826  | SPA Test Execution Trigger                         | implemented    | specified       | Zero current KB test linkage; same root cause.                                                         |
| SPEC-1827  | Diagnostic Data Export for Claude Code             | implemented    | specified       | Zero current KB test linkage; same root cause.                                                         |

Current-status evidence: read-only inspection of `groundtruth.db` via `sqlite3.connect('groundtruth.db').execute('SELECT id, version, status FROM specifications WHERE id = ?', (spec_id,))` confirms every target at version 4 or 5 with `status='implemented'` and `changed_by='Claude/S293'`. Zero current test linkage: confirmed in `bridge/spec-hygiene-spa-remediation-006.md` §Evidence ("Current test-link count remains zero for each target").

---

## Requirement Sufficiency

`Existing requirements sufficient.` The governing specifications (GOV-15, GOV-ARTIFACT-APPROVAL-001, DCL-ARTIFACT-APPROVAL-HOOK-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-STANDING-BACKLOG-001, and the 10 target SPEC bodies themselves) fully constrain this slice. No new or revised requirements are required; the proposal is lifecycle-correction work under existing rules.

---

## Implementation Plan

**Bridge protocol invariants:** This proposal will be filed at `bridge/gtkb-control-plane-placeholder-test-remediation-slice-1-revert-001.md` with a corresponding INDEX update inserting `NEW: bridge/gtkb-control-plane-placeholder-test-remediation-slice-1-revert-001.md` at the top of a new `Document: gtkb-control-plane-placeholder-test-remediation-slice-1-revert` entry in `bridge/INDEX.md`. The INDEX entry is the canonical workflow-state record per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`. No prior bridge versions exist for this thread (this is `-001`); no deletion or rewrite of prior versions is involved. Subsequent versions (REVISED / NO-GO / GO / post-implementation report / VERIFIED) will be filed as new numbered files with INDEX updates inserting the new status line at the top of this entry's version list.

1. **Pre-flight read** — `scripts/control_plane_revert_slice_1.py` connects read-only to `groundtruth.db` and confirms each of the 10 target specs is currently at `status='implemented'` (fail-closed if any spec is at an unexpected status; Codex revisit required if the world moved).

2. **Per-spec approval packet generation** — For each spec, generate `.groundtruth/formal-artifact-approvals/2026-05-<DD>-<SPEC-ID>-status-revert.json` containing:
   - `artifact_type: "specification"`, `artifact_id: <SPEC-ID>`, `action: "update_status"`.
   - `full_content`: complete current spec row (all columns) plus the proposed status delta (`status: "implemented" → "specified"`).
   - `full_content_sha256`: computed over the JSON-serialized current row.
   - `presented_to_user: true`, `transcript_captured: true` (filled in after the AUQ-mediated owner approval at packet-collection time).
   - `explicit_change_request`: the exact owner approval text from the AUQ answer.
   - `changed_by: "prime-builder/claude-harness-B/S350"`.
   - `change_reason: "WI-3184 Slice 1: revert to specified pending real spec-derived test creation per DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001; bridge gtkb-control-plane-placeholder-test-remediation-slice-1-revert"`.
   - `approved_by: "owner"`.

3. **Per-spec status revert via MemBase API** — For each spec, call:
   ```python
   db = KnowledgeDB("groundtruth.db")
   db.update_spec(
       id="<SPEC-ID>",
       changed_by="prime-builder/claude-harness-B/S350",
       change_reason="WI-3184 Slice 1: revert to specified per bridge gtkb-control-plane-placeholder-test-remediation-slice-1-revert (Codex GO at -NNN); no current KB test linkage; aligns lifecycle with DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.",
       status="specified",
   )
   ```
   The `update_spec` call creates a new version row carrying forward all other fields unchanged (description, title, assertions, etc.). The hook chain (`formal-artifact-approval-gate.py`) enforces packet presence + matching SHA-256 at write time.

4. **Audit-trail recording** — Each `update_spec` call already writes the new version row with `changed_by` + `changed_at` + `change_reason` + version + status delta. The script collects (`spec_id`, `prior_version`, `new_version`, `prior_status`, `new_status`, `change_reason`, `packet_path`) into a single audit-summary JSON at `.gtkb-state/slice-1-revert/audit-summary-<run-id>.json` for the post-implementation report.

5. **Spec-body invariance check** — After all 10 updates, the script re-reads each spec and asserts that every column except `version`, `status`, `changed_by`, `changed_at`, `change_reason` is byte-identical to the prior version. Any mismatch fails the run and triggers rollback authorization request (NOT an autonomous rollback; the operation is append-only and `update_spec` cannot be undone except by another forward update).

6. **WI-3184 update** — After successful 10/10 revert, the script appends a `resolution_status: open → resolved` candidate update to the audit summary. The actual WI resolution is a separate governed operation NOT performed by this slice; Codex GO + an owner-approved packet is required to close WI-3184. This slice's success enables that downstream closure.

MemBase API path: `groundtruth-kb/src/groundtruth_kb/db.py` `KnowledgeDB.update_spec()` (line 1245). Confirmed read-write-capable for status fields with carry-forward of unmodified columns.

---

## Test Mapping

Spec-derived tests under `platform_tests/scripts/test_control_plane_revert_slice_1.py`:

| Test                                                            | Derives from                                                                              | Asserts                                                                                              |
|-----------------------------------------------------------------|-------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| `test_pre_flight_detects_unexpected_status`                     | GOV-15 (no autonomous fix without checking state)                                         | Script aborts when any of the 10 specs is NOT at `implemented`.                                      |
| `test_per_spec_packet_generated_with_required_fields`           | GOV-ARTIFACT-APPROVAL-001, DCL-ARTIFACT-APPROVAL-HOOK-001                                 | All 10 packets exist with required keys + full current row + correct SHA-256.                        |
| `test_packet_sha256_matches_current_row`                        | DCL-ARTIFACT-APPROVAL-HOOK-001 (hook validates full-content hash)                         | Each packet's `full_content_sha256` matches the actual SHA-256 of the serialized current spec row.   |
| `test_update_spec_creates_new_version_for_each_target`          | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001                                           | After run, each of the 10 specs has version = previous_version + 1 with `status='specified'`.        |
| `test_status_field_transitions_from_implemented_to_specified`   | WI-3184 description + this proposal's §Affected Specs Inventory                           | New version's `status='specified'` and prior version's `status='implemented'`.                       |
| `test_no_spec_body_modification`                                | Slice-1 scope discipline + GOV-ARTIFACT-APPROVAL-001 (no scope creep)                     | For every spec, prior vs new version differ only in `version`, `status`, `changed_by`, `changed_at`, `change_reason`. All other columns byte-identical. |
| `test_changed_by_attributes_to_prime_builder_harness_b`         | `.claude/rules/operating-role.md` (durable role attribution)                              | Every new row's `changed_by` matches `prime-builder/claude-harness-B/S350`.                          |
| `test_change_reason_cites_bridge_and_wi`                        | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001                                    | Every new row's `change_reason` substring-includes `WI-3184` AND `gtkb-control-plane-placeholder-test-remediation-slice-1-revert`. |
| `test_idempotent_rerun_is_noop`                                 | Script-correctness invariant                                                              | Running the script twice produces exactly one new version per spec (not two); second run aborts pre-flight because the state is now `specified`. |
| `test_audit_summary_records_all_ten_specs`                      | GOV-STANDING-BACKLOG-001 (durable evidence)                                               | `.gtkb-state/slice-1-revert/audit-summary-*.json` lists all 10 spec IDs with prior/new version+status. |
| `test_zero_test_linkage_remains_zero`                           | `bridge/spec-hygiene-spa-remediation-006.md` §Evidence baseline                           | Test count linked to each of the 10 specs is unchanged (0) before and after the run.                 |
| `test_protected_spec_1837_test_baseline_unchanged`              | `bridge/spec-hygiene-spa-remediation-003.md` §Preservation Constraint                     | The 35 SPEC-1837 test rows (TEST-10452..TEST-10506) are unchanged after the run.                     |
| `test_wi_3184_unchanged_by_slice_1`                             | WI-3184 closure is downstream (not in scope)                                              | WI-3184's `resolution_status='open'` and `version` are unchanged by Slice 1 itself.                  |

All 13 tests must PASS before the implementation report can request VERIFIED.

---

## Risk and Rollback

**Risk: low.** Append-only versioning means the prior `implemented` versions remain in `specifications`; no historical state is lost. The lifecycle correction is reversible by another forward `update_spec` call (which itself would require its own bridge proposal + approval packet under the same governance).

**Failure modes:**

- Approval packet generation fails partway through — script halts with first-N-of-10 packets written; no `update_spec` calls have run yet. Recovery: resume from N+1 after fixing the failure mode.
- `update_spec` fails mid-run (e.g., on spec 6 of 10) — first 5 specs are now at `specified`; remaining 5 still at `implemented`. State is consistent (each spec is at one valid status); recovery: resume from spec 6 after fixing failure. Tests `test_pre_flight_detects_unexpected_status` catches the resume case.
- Hook chain rejects a packet — `update_spec` raises; same recovery as above.
- Concurrent session writes — `update_spec` uses MemBase's normal versioning; conflicting updates produce a higher version that this script's pre-flight will detect on rerun.

**Rollback:** Per-spec forward-update back to `implemented` is the supported rollback if Codex VERIFIED is rescinded by owner directive. Each rollback step would itself require its own bridge proposal + approval packet.

---

## Acceptance Criteria

1. All 10 affected specs have a new version row with `status='specified'`, `changed_by='prime-builder/claude-harness-B/S350'`, and `change_reason` citing WI-3184 + this bridge thread.
2. All 10 per-spec formal-artifact-approval packets exist at `.groundtruth/formal-artifact-approvals/2026-05-*-SPEC-*-status-revert.json` with hook-validatable SHA-256.
3. No spec body modified (only `version`, `status`, `changed_by`, `changed_at`, `change_reason` differ between prior and new versions).
4. SPEC-1837 test baseline (35 test rows TEST-10452..TEST-10506) unchanged.
5. Audit summary JSON exists at `.gtkb-state/slice-1-revert/audit-summary-<run-id>.json` with all 10 entries.
6. All 13 tests in `platform_tests/scripts/test_control_plane_revert_slice_1.py` PASS.
7. WI-3184 itself remains untouched by Slice 1 (closure is downstream).

---

## Verification Plan

Codex VERIFIED gate requires:

1. Read-only inspection of `groundtruth.db` confirming each of the 10 specs has a new `version = prior + 1` row with `status='specified'`.
2. Read-only inspection confirming prior `implemented` version row is still present (append-only invariant).
3. Read-only inspection confirming SPEC-1837 test rows unchanged.
4. Inspection of all 10 formal-artifact-approval packets confirming required keys + SHA-256 match.
5. Pytest execution of `platform_tests/scripts/test_control_plane_revert_slice_1.py` — all 13 PASS.
6. Inspection of `.gtkb-state/slice-1-revert/audit-summary-<run-id>.json` confirming completeness.

Commands:

```text
python -m pytest platform_tests/scripts/test_control_plane_revert_slice_1.py -v
python scripts/control_plane_revert_slice_1.py --verify-only
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-control-plane-placeholder-test-remediation-slice-1-revert
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-control-plane-placeholder-test-remediation-slice-1-revert
```

---

## Applicability Preflight

- packet_hash: `sha256:08d31044fdb61b931dd72ee124d57f96628d58abcc666af899a86c56789e5a43`
- bridge_document_name: `gtkb-control-plane-placeholder-test-remediation-slice-1-revert`
- content_source: `pending_content`
- content_file: `bridge/gtkb-control-plane-placeholder-test-remediation-slice-1-revert-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, content:applications/, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

**Clause preflight:** `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-control-plane-placeholder-test-remediation-slice-1-revert --content-file bridge/gtkb-control-plane-placeholder-test-remediation-slice-1-revert-001.md` returns EXIT=0 (no blocking gaps; 5/5 must_apply clauses satisfied: `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`, `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`).

---

End of proposal.
