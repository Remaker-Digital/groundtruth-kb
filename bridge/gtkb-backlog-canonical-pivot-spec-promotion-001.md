NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 3822c4b2-2b4c-4021-8f5f-c4a26cbfe9fd
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning

# GTKB Backlog Canonical-Pivot Spec Promotion (Slice 2A Closure)

bridge_kind: governance_advisory
target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-30-slice-2a-closure-adr-v4.json", ".groundtruth/formal-artifact-approvals/2026-05-30-slice-2a-closure-dcl-v4.json", ".groundtruth/formal-artifact-approvals/2026-05-30-slice-2a-closure-gov-v5.json", "bridge/gtkb-backlog-canonical-pivot-spec-promotion-*.md", "bridge/INDEX.md"]

Document: gtkb-backlog-canonical-pivot-spec-promotion
Version: 001 (NEW)
Date: 2026-05-30 UTC
Slice context: Closure step for Slice 2A of the GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH program. Slice 2A was filed by `claude-prime-builder` on 2026-05-12 as the spec-supersession capturing the S342 canonical-table pivot from `backlog_items` to extended `work_items`. `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v3, `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v3, and `GOV-STANDING-BACKLOG-001` v4 were inserted at `status=specified` but the bridge cycle never closed to promote them to `verified`. This proposal closes that loop by inserting v4 / v4 / v5 with `status=verified` backed by spec-derived empirical evidence that the canonical pivot is in effect.

## Claim

Three new spec versions will be inserted into MemBase `specifications` with `status=verified`:

- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v4 (promoted from v3 `specified`)
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v4 (promoted from v3 `specified`)
- `GOV-STANDING-BACKLOG-001` v5 (promoted from v4 `specified`)

Each new version preserves its predecessor row per the append-only invariant. Each insertion is backed by:

- A formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-30-slice-2a-closure-<id>.json` per `GOV-ARTIFACT-APPROVAL-001` v3.
- Spec-derived empirical evidence proving the predecessor specification is in effect (PRAGMA + `current_work_items` query results documented under § Spec-Derived Verification Plan).
- A `change_reason` citing this bridge document, the predecessor version, the approval packet path, and `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT`.

No source code, tests, hooks, scripts, or non-MemBase artifacts are modified by this slice. `memory/work_list.md` and the dashboard/reader consumers are unchanged; subsequent slices (3+) will rewire readers and gate the file deletion.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — file bridge protocol authority; this proposal is a bridge-mediated governance change request.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal must cite every relevant governing specification (this section satisfies the mandate).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED verdict requires spec-derived test evidence; the proposal's § Spec-Derived Verification Plan maps each linked spec to an executable evidence command.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files live under `E:\GT-KB`; root-boundary compliant.
- `GOV-ARTIFACT-APPROVAL-001` v3 (rowid 8453) — extended scope covers ADR/DCL/GOV spec inserts; this slice authors 3 approval packets prior to insert.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v3 (target spec; status `specified` to be promoted to v4 `verified`).
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v3 (target spec; status `specified` to be promoted to v4 `verified`).
- `GOV-STANDING-BACKLOG-001` v4 (target spec; status `specified` to be promoted to v5 `verified`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — concrete decisions and lifecycle transitions preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — traceability across artifacts/tests/reports/decisions preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — `specified -> verified` lifecycle transition surfaced.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-008.md` (Slice 1 VERIFIED) — predecessor bridge thread; this slice continues the same program.
- `bridge/gtkb-backlog-work-list-retirement-directive-001-012.md` (VERIFIED) — sibling retirement-directive thread that supersedes earlier work-list narrative and informs the GOV v5 content.
- `.claude/rules/acting-prime-builder.md` § Formal Artifact Approval And Audit Principle — DELIB/GOV/ADR/DCL mutation requires presented-to-user + transcript-captured packet evidence; this slice provides 3 packets prior to KB insert.

## Prior Deliberations

- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` — owner directive: MemBase `work_items` is the canonical backlog source of truth (load-bearing decision for v3 / v3 / v4 supersession that this slice now ratifies as `verified`).
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` — original S327 directive motivating the program.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — owner decision: `memory/work_list.md` is deleted at migration conclusion (not persisted as generated view); this slice does not delete the file but ratifies the GOV v5 endpoint language.
- `DELIB-1788` — Loyal Opposition Verification: GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH Slice 1 (predecessor VERIFIED for the same project).
- `DELIB-1962` — archived bridge thread record for `gtkb-gov-backlog-source-of-truth-2026-05-02` (8 versions VERIFIED).
- `DELIB-0838` — owner decision establishing standing backlog as governed cross-session work authority (root governance directive).
- `DELIB-0835` — scoped auto-approval pattern (potentially used for the 3 approval packets if owner activates scope at execution-time AUQ; otherwise per-packet acknowledgement applies).
- `DELIB-1580` — Loyal Opposition Verification: Backlog Work List Retirement Directive (the verdict on the sibling thread that already updated narrative artifacts).

## Owner Decisions / Input

Session-current owner AskUserQuestion (S373 / this turn):

| Question | Answer |
|---|---|
| Which next slice should I scope and file as a bridge NEW proposal for Codex review? | "Close Slice 2A governance loop" (option A: thin proposal to promote ADR/DCL/GOV v3 / v3 / v4 -> v4 / v4 / v5 `verified`) |

This AUQ authorizes filing this bridge proposal under Prime Builder's work-selection authority per the standing backlog directive. Post-GO, the 3 individual spec-insert + 3 individual approval-packet steps require their own owner approval per `GOV-ARTIFACT-APPROVAL-001` v3. The proposed pattern is:

1. Single AUQ at execution time presenting all 3 approval packets + a "scoped auto-approval" option per `DELIB-0835` amendment, OR
2. Three separate AUQs (one per packet, no scoped batching).

The choice between (1) and (2) will be presented as an execution-time AUQ once Codex records GO. This proposal does NOT pre-commit owner to scoped-auto-approval; it commits only to filing the bridge thread for review.

Preserved from prior thread family:

- S327 owner directive (`DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`) authorizing the original program.
- S342 owner directive (`DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT`) authorizing the canonical-table pivot.
- S337 owner directive (`DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`) authorizing the deletion endpoint.

## Description And Plan

### Step 1 - Generate 3 approval packets

For each target spec version, generate a packet at `.groundtruth/formal-artifact-approvals/2026-05-30-slice-2a-closure-<id>.json`:

- Packet 1: `2026-05-30-slice-2a-closure-adr-v4.json` (for ADR-STANDING-BACKLOG-DB-AUTHORITY-001 v4)
- Packet 2: `2026-05-30-slice-2a-closure-dcl-v4.json` (for DCL-STANDING-BACKLOG-DB-SCHEMA-001 v4)
- Packet 3: `2026-05-30-slice-2a-closure-gov-v5.json` (for GOV-STANDING-BACKLOG-001 v5)

Each packet has fields per `GOV-ARTIFACT-APPROVAL-001` v3:

- `artifact_type` = `spec`
- `artifact_id` = the target spec id
- `action` = `update`
- `full_content` = the new version's full description text (markdown)
- `full_content_sha256` = SHA256 of the `full_content` UTF-8 bytes
- `presented_to_user` = true
- `transcript_captured` = true
- `explicit_change_request` = "Promote <spec-id> from v<N> specified to v<N+1> verified per Slice 2A closure"
- `changed_by` = `claude-prime-builder`
- `change_reason` = full citation chain
- `approved_by` = `owner` (or `auto` per scoped batch if owner activates)

### Step 2 - Owner AUQ for the approval packets

Owner is presented the 3 packets in transcript and chooses approval mode (per-packet or scoped batch). This is execution-time AUQ, not pre-committed by this proposal.

### Step 3 - Insert 3 new spec versions

Using `db.insert_spec(...)` with `GTKB_FORMAL_APPROVAL_PACKET=<packet-path>` env var per packet:

- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v4 (status=verified). Description carries forward v3 content with one addition: a "Verification" section citing the empirical evidence (PRAGMA result, `current_work_items` count) and this bridge document.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v4 (status=verified). Same pattern.
- `GOV-STANDING-BACKLOG-001` v5 (status=verified). Same pattern.

### Step 4 - Verify predecessors preserved

After insertion, query MemBase to confirm:

- ADR v3 row still exists with status=specified (historical evidence; append-only invariant).
- DCL v3 row still exists with status=specified.
- GOV v4 row still exists with status=specified.

### Step 5 - File post-implementation report

A new bridge version (`-003` after Codex's GO at `-002`) is filed as the post-impl report carrying:

- KB row evidence (rowids of new spec versions)
- Packet hash evidence
- Spec-derived verification results (re-run of the PRAGMA + view queries proving the schema is still in effect)
- Bridge applicability preflight output
- ADR/DCL clause preflight output
- Recommended commit type: `feat(governance):` per S333 audit FINDING-P0-001 discipline

### Step 6 - Codex VERIFIED

After Codex records VERIFIED on the post-impl report, the slice is closed. The 3 promoted specs become the governance authority for all subsequent migration-completion-path slices.

## Requirement Sufficiency

**Existing requirements sufficient.** The S342 owner directive captured at `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` provides the requirement basis for the spec content. The Slice 2A pivot specs (v3 / v3 / v4) already capture the requirement; this slice promotes their lifecycle status, not their substantive content. No new requirement work, no requirement disambiguation needed.

The governing specifications are:

- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` (the requirement)
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v3 (the architecture decision implementing the requirement)
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v3 (the design constraint implementing the requirement)
- `GOV-STANDING-BACKLOG-001` v4 (the governance contract implementing the requirement)

## Spec-Derived Verification Plan

| Linked clause | Spec | Verification command | Expected result |
|---|---|---|---|
| Schema in effect (25-column backlog schema present in work_items) | `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v3 | `python -c "import sqlite3; con=sqlite3.connect('groundtruth.db'); cur=con.cursor(); cols={r[1] for r in cur.execute('PRAGMA table_info(work_items)')}; expected={'id','version','title','description','origin','component','status_detail','changed_by','changed_at','change_reason','project_name','subproject_name','implementation_order','source_owner_directive','source_deliberation_query','related_deliberation_ids','related_spec_ids_at_creation','related_bridge_threads','depends_on_work_items','blocks_work_items','acceptance_summary','regression_visibility','completion_evidence','supersedes','superseded_by'}; print('MISSING:', expected - cols)"` | `MISSING: set()` (all 25 columns present; already proven this turn) |
| Authority in effect (`current_work_items` view returns rows) | `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v3 | `python -c "import sqlite3; con=sqlite3.connect('groundtruth.db'); print(con.execute('SELECT COUNT(*) FROM current_work_items').fetchone()[0])"` | >= 250 (proven 274 this turn) |
| Governance authority text matches MemBase-canonical claim | `GOV-STANDING-BACKLOG-001` v4 | direct read of `db.get_spec('GOV-STANDING-BACKLOG-001').description` should contain "MemBase work_items" and "deleted at migration conclusion" | PASS (proven this turn via direct SQL query showing v4 status=specified content includes both phrases) |
| 3 new spec versions inserted with status=verified | `GOV-ARTIFACT-APPROVAL-001` v3 | `db.get_spec(...)` returns ADR v4 verified, DCL v4 verified, GOV v5 verified | All 3 specs at expected new version + status=verified |
| 3 predecessor versions preserved | append-only invariant | `SELECT id, version, status FROM specifications WHERE (id, version) IN (('ADR-STANDING-BACKLOG-DB-AUTHORITY-001',3), ('DCL-STANDING-BACKLOG-DB-SCHEMA-001',3), ('GOV-STANDING-BACKLOG-001',4))` returns 3 rows each with status=specified | PASS |
| 3 approval packets have valid SHA256 | `GOV-ARTIFACT-APPROVAL-001` v3 | For each packet, `hashlib.sha256(full_content.encode('utf-8')).hexdigest() == full_content_sha256` | PASS |
| Bridge applicability preflight | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-canonical-pivot-spec-promotion` | `preflight_passed: true`, `missing_required_specs: []` |
| ADR/DCL clause preflight | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-canonical-pivot-spec-promotion` | exit code 0, blocking gaps 0 |
| Root-boundary compliance | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All touched paths under `E:\GT-KB` | PASS (verified by manual path inspection) |
| Code-quality gates (no Python source changes) | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | N/A - no Python files added or modified | N/A |
| Cross-thread linkage | `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) | Slice 1 VERIFIED + retirement-directive VERIFIED both cited in Spec Links | PASS |

## Acceptance Criteria

1. Three new spec versions (ADR v4, DCL v4, GOV v5) exist in MemBase `specifications` with `status='verified'`.
2. Each new version's `change_reason` field cites: this bridge document, the predecessor version, the approval-packet path, `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT`.
3. Three approval-packet JSON files exist on disk at `.groundtruth/formal-artifact-approvals/2026-05-30-slice-2a-closure-<id>.json`; each has `presented_to_user=true`, `transcript_captured=true`, and valid SHA256 matching `full_content`.
4. Predecessor specs (ADR v3, DCL v3, GOV v4) still exist with `status='specified'` (append-only invariant).
5. No source/test/hook/script/config files modified outside the 3 packet files and the new spec rows.
6. Bridge applicability preflight passes (no missing required cross-cutting specs).
7. ADR/DCL clause preflight exits 0 with no blocking gaps.
8. The post-implementation report cites all evidence above and follows the conventional commits discipline (`feat(governance):`).

## Risk And Rollback

### Risk surface

- **Owner over-batching**: if owner picks scoped-auto-approval (DELIB-0835 mode) and the 3 packets fail validation post-insert (e.g., content/hash mismatch), all three rollbacks must happen together. Mitigation: pre-validate hash on packet write before any insert; if any hash mismatches, abort the batch.
- **Spec content drift between v3 (`specified`) and v4 (`verified`)**: the v4 content should largely carry forward v3's substantive description, adding only the verification-evidence subsection. Mitigation: diff v3 vs v4 content during draft review; reviewer (Codex) is asked to confirm no semantic change beyond verification-evidence addition.
- **Cross-platform LF/CRLF for packets**: SHA256 must match staged blob bytes. Mitigation: helper computes `hashlib.sha256(content.encode('utf-8'))` on the literal content string, matching how Slice A.1+C packet validation works.

### Rollback per artifact

- **Approval packets**: gitignored; deletable. Rollback = `del .groundtruth/formal-artifact-approvals/2026-05-30-slice-2a-closure-*.json`.
- **Spec rows**: append-only; rollback = insert v5 / v5 / v6 with `status='specified'` and `change_reason` citing the rollback rationale. Predecessor v3 / v4 rows remain.
- **Bridge file**: append-only; no rollback applies. A NO-GO verdict from Codex requires a REVISED next version, not file deletion.

## Pre-Filing Preflight

- bridge_document_name: `gtkb-backlog-canonical-pivot-spec-promotion`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-backlog-canonical-pivot-spec-promotion-001.md`
- operative_file: `bridge/gtkb-backlog-canonical-pivot-spec-promotion-001.md`
- preflight_passed: to be confirmed by mechanical `.claude/hooks/bridge-compliance-gate.py` on Write; reviewer to re-run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-canonical-pivot-spec-promotion` as part of GO review.
- triggered cross-cutting specs (from `config/governance/spec-applicability.toml`):
  - blocking: `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
  - advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- All triggered specs cited in § Specification Links above.

## Requested Loyal Opposition Action

Review this `-001` for GO / NO-GO. Specific reviewer questions for Codex:

1. Is the proposed pattern (close Slice 2A loop via 3 spec version promotions with empirical evidence) sufficient to discharge the unclosed Slice 2A debt, or should the proposal be REVISED to also include something else (e.g., a doctor check that asserts the verified versions exist; a regression test against the schema)?
2. Are the 3 spec-derived verification commands (PRAGMA, COUNT, `get_spec().description`) sufficient evidence per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, or should an additional formal pytest suite be added to the implementation slice?
3. The proposal exempts itself from project-linkage triple via `bridge_kind: governance_review` (per `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` exempt set). Is this classification correct given the slice mutates 3 spec rows + 3 approval packet files? Or should it be reclassified as an implementation proposal with project linkage to a yet-to-be-created project authorization (e.g., adding to `PROJECT-GTKB-RELIABILITY-FIXES` if approved)?
4. Spec-derived evidence for the ADR/DCL is empirical (PRAGMA + COUNT); spec-derived evidence for GOV is textual (description contains specific phrases). Is the textual evidence acceptable for the governance spec, or should it be supplemented with a deterministic-test alternative?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
