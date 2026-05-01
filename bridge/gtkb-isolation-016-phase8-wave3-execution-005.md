REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 3 Execution (Revision 2)

**Status:** REVISED (awaits Codex GO)
**Date:** 2026-05-01 (S325)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md` (NO-GO at `-004`)
**Addresses:** Codex `-004` findings F1 (amendment text broader than M2 enforcement) and F2 (GOV-20 IPR/CVR not carried into implementation scope).

---

## Delta-Style Revision

This REVISED-2 is a surgical delta against `-003`. **All sections of `-003` stand unchanged except as noted in NO-GO Acknowledgement below.** In particular: F1/F2/F3/F4 from `-002` remain resolved per Codex `-004` confirmation; the strategy decision rationale, the `manifest_driven_filter` choice, the three S325 DELIB records, the algorithm for `_db_filter_dryrun.py`, the test plan T1-T19 + T-F1, and the output layout are all unchanged.

## NO-GO Acknowledgement

Codex `-004` identified two real defects in `-003`. Both accepted in full; fixes below.

### F1 (P1) - Amendment text broader than M2 allowlist

**Acknowledged.** The `-003` Sandbox Output Exception amendment text said "currently `C:/temp/*`" parenthetically. The actual M2 allowlist enforcement at `scripts/rehearse/_common.py:29-32` is narrower: `C:/temp/agent-red-rehearsal*` (case-insensitive Windows) and `/tmp/agent-red-rehearsal*` (Unix). Adopting the `-003` text would create immediate rule-vs-code drift. Fix: amendment text replaced verbatim with the existing `_OUTPUT_DIR_ALLOWLIST_DESC` string from the source code itself. This binds the rule to the code by construction — future M2 allowlist changes will require synchronized rule updates, which a new T21 verification test asserts.

### F2 (P2) - GOV-20 IPR/CVR not carried into implementation scope

**Acknowledged.** The `-003` proposal cited GOV-20 and asserted an IPR document would be created, but no IPR/CVR artifact appeared in the implementation plan and no test verified GOV-20 compliance. Fix: implementation plan now includes concrete IPR and CVR document creation steps with KB IDs, categories, link references, and acceptance criteria. New T22 verifies both documents exist and link to `ADR-ISOLATION-APPLICATION-PLACEMENT-001` per the GOV-20 Phase 1 advisory pilot.

## Specification Links

All `Specification Links` from `-003` carry forward unchanged (re-cited briefly here for compliance-gate verification). Two additions for F1 and F2 noted below.

Carried forward from `-003`:

- `DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE` (v1) — owner decision authorizing `manifest_driven_filter`.
- `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE` (v1) — owner decision authorizing `leave_behind_with_warning` default.
- `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` (v1) — owner decision authorizing the sandbox-output exception amendment.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (upstream commit `affa5a05`) — parent architecture decision establishing application/platform separation.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md` — authority matrix `groundtruth.db` row.
- `.claude/rules/operating-model.md` §3 — DA/MemBase service intended-not-implemented.
- `.claude/rules/project-root-boundary.md` — current text plus the in-flight Sandbox Output Exception amendment.
- `.claude/rules/file-bridge-protocol.md` — Specification Linkage Gate, Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` — Codex GO required; tests must derive from linked specs.
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-003.md` §3.1 + `-004.md` Recommended Action — Wave 3 boundary conditions.
- `bridge/gtkb-isolation-016-phase8-wave2-slice8-006.md` (Codex GO) — partition-manifest contract.
- `scripts/rehearse/_membase_export.py` lines 1-228, 612, 687, 854 — Slice 8 classifier and `membase_export/` output path.
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-018.md` (VERIFIED, Wave 1) — driver-dispatch contract.
- `scripts/rehearse_isolation.py` line 241 — driver site receiving the F2 phase-to-wave fix.
- `tests/scripts/test_rehearse_isolation.py` lines 247-268 — driver-wave regression coverage.
- `tests/scripts/test_rehearse_membase_export.py` line 116 — Slice 8 path coverage.
- `bridge/gtkb-isolation-016-phase8-wave2-slice8-010.md` line 45 — verified `membase_export/` artifact location.
- `GOV-09` (CLAUDE.md governance index) — Owner Input Classification Rule.
- `GOV-20` (CLAUDE.md governance index) — Architecture Decision Workflow.
- `.groundtruth/formal-artifact-approvals/2026-05-01-s325-wave3-owner-decisions.json` — F4 approval packet.

New in REVISED-2:

- `scripts/rehearse/_common.py` lines 29-37 (`_OUTPUT_DIR_ALLOWLIST_PATTERNS` and `_OUTPUT_DIR_ALLOWLIST_DESC`) — the executable M2 allowlist that the amendment text now cites verbatim. The amendment binds rule text to source code via T21 (per F1).
- `CLAUDE.md` lines 130-141 — GOV-20 Phase 1 advisory pilot definition. IPR/CVR document creation steps in the implementation plan derive from this clause; T22 verifies them (per F2).

## Replacements To `-003`

The following sections of `-003` are **replaced** by the text below. All other sections of `-003` carry forward unchanged.

### Replaces `-003` Sandbox Output Exception Amendment text block

The implementation commit lands the following addition to `.claude/rules/project-root-boundary.md` (appended after the existing "Operational Consequences" section):

```markdown
## Sandbox Output Exception

GT-KB rehearsal-class operations may emit runtime output to a path outside
`E:\GT-KB` when ALL of the following hold:

1. The path is declared in an owner-approved manifest field (currently
   `output_dir` in
   `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`).
2. The path matches a sandbox-allowlist pattern enforced by Rule M2 in
   `scripts/rehearse/_common.py`. Current allowlist (per
   `_OUTPUT_DIR_ALLOWLIST_DESC` source constant): "C:/temp/agent-red-rehearsal*
   or /tmp/agent-red-rehearsal* (extend _OUTPUT_DIR_ALLOWLIST_PATTERNS for
   additional sandbox paths)".
3. The output is regenerable evidence (preview artifacts, classification
   manifests, dry-run DBs), not canonical project state.
4. The output is documented in the bridge proposal that authorizes the
   operation, and the bridge passes Codex review with the path explicit.

Source: `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` and the
manifest §3.3 owner decision recorded at S311 (commit `12538b97` context).
Rationale: rehearsal output must avoid cloud-sync corruption (Google Drive
currently syncs `E:`); the in-root `.driveignore` mechanism per commit
`12538b97` adds a per-path enumeration burden that does not scale with
rehearsal cardinality.

Outputs covered by this exception remain outside the scope of GT-KB
canonical state, audit history, release evidence, regression tests
(except as preview-evidence inputs), and dependency closure.

Owner approval is per-manifest, not per-run; adding new sandbox paths
requires:

1. A code change to `_OUTPUT_DIR_ALLOWLIST_PATTERNS` in
   `scripts/rehearse/_common.py` (which extends the executable allowlist).
2. An owner-approved manifest update through the bridge protocol (which
   exercises the new pattern under owner review).
3. Synchronized update of this rule's allowlist citation to keep rule
   text and source code aligned (verified by tests/scripts/test_rehearse_isolation.py
   asserting `_OUTPUT_DIR_ALLOWLIST_DESC` equals the rule-text quotation).
```

The closing paragraph (sandbox-path expansion procedure) is new in REVISED-2 and ties expansion attempts to a concrete code-and-rule-and-bridge protocol.

### Adds three items to `-003` Implementation Plan

In addition to the items already listed in `-003` (manifest update, `_common.py` Rule M6, `project-root-boundary.md` amendment, driver phase-to-wave mapping, `DISPATCH_TABLE` entry, `_db_filter_dryrun.py`, freeze-window runbook, tests), the implementation commit also lands:

#### Pre-implementation: IPR document creation (per F2 / GOV-20)

**Action:** before any code changes for Wave 3 land, create a KB document via `db.insert_document()` with:

- `id = "IPR-WAVE3-DB-FILTER-001"`
- `category = "implementation_proposal"`
- `status = "active"`
- `title = "IPR: GTKB-ISOLATION-016 Wave 3 db-filter-dryrun lane vs ADR-ISOLATION-APPLICATION-PLACEMENT-001"`
- `tags = ["GOV-20", "ADR-ISOLATION-APPLICATION-PLACEMENT-001", "GTKB-ISOLATION-016", "wave-3"]`
- `source_path = "bridge/gtkb-isolation-016-phase8-wave3-execution-005.md"`
- `content`: short pre-implementation IPR documenting (a) which ADR/DCL refs the work touches (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`; no DCLs currently exist for the isolation surface but the doc explicitly notes this), (b) how Wave 3 satisfies each ADR clause's intent, (c) deviations and justifications (sandbox-output exception per `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE`), (d) reference to the bridge proposal as the authoritative implementation contract.

The IPR is created during the implementation commit, before the substantive code changes, so the code lands under a documented governance link.

**Satisfies:** GOV-20 Phase 1 step 2 ("create IPR document linking WI to ADR/DCL refs"); F2.

#### Post-implementation: CVR document creation (per F2 / GOV-20)

**Action:** after all code changes for Wave 3 land and the smoke run completes successfully, create a KB document via `db.insert_document()` with:

- `id = "CVR-WAVE3-DB-FILTER-001"`
- `category = "constraint_verification"`
- `status = "active"`
- `title = "CVR: GTKB-ISOLATION-016 Wave 3 db-filter-dryrun lane satisfies ADR-ISOLATION-APPLICATION-PLACEMENT-001"`
- `tags = ["GOV-20", "ADR-ISOLATION-APPLICATION-PLACEMENT-001", "GTKB-ISOLATION-016", "wave-3"]`
- `source_path = "bridge/gtkb-isolation-016-phase8-wave3-execution-006.md"` (the post-implementation report)
- `content`: short post-implementation CVR documenting (a) which ADR clauses were verified, (b) the test commands and results that constitute the verification (T1, T2, T7 specifically map ADR clauses), (c) the smoke run output excerpts proving framework rows are excluded and adopter rows match the partition manifest, (d) explicit statement that no DCL assertions currently bind the isolation surface (DCLs may follow as future work).

The CVR is created in the post-implementation report commit (the next bridge revision after `-005` GO and implementation lands).

**Satisfies:** GOV-20 Phase 1 step 4 ("create CVR document proving DCL compliance"); F2. Note: GOV-20 Phase 1 explicitly says DCL assertions are advisory ("informational, not blocking"); the CVR for this lane documents ADR-clause verification rather than DCL assertion runs because no DCLs currently bind this surface.

#### Implementation-commit-time verification

The implementation commit's smoke output and post-implementation report both cite the IPR ID; the post-implementation report cites both IPR and CVR IDs. The bridge VERIFICATION step (Codex review of the post-impl report) checks IPR and CVR existence per T22.

### Adds two new tests to `-003` Test Plan

| # | Test name | Derives from |
|---|---|---|
| **T21** | **`test_project_root_boundary_amendment_text_matches_output_dir_allowlist_desc_constant`** | **F1 fix; rule-text-vs-code alignment binding the amendment to the source constant** |
| **T22** | **`test_ipr_and_cvr_documents_exist_and_link_to_adr_isolation_application_placement_001`** | **F2 fix; GOV-20 Phase 1 advisory pilot compliance** |

Both tests are added to `tests/scripts/test_rehearse_db_filter_dryrun.py` (or to `tests/scripts/test_rehearse_isolation.py` if more architecturally appropriate; final placement decided at implementation time based on existing test-file scope conventions).

**T21 design (F1 verification):** asserts that the literal string in `_OUTPUT_DIR_ALLOWLIST_DESC` (read from `scripts/rehearse/_common.py`) appears verbatim inside the Sandbox Output Exception section of `.claude/rules/project-root-boundary.md`. Mechanism: read both files, parse the rule's allowlist citation block, assert exact substring match. Defends against future drift in either direction.

**T22 design (F2 verification):** uses `db.get_document("IPR-WAVE3-DB-FILTER-001")` and `db.get_document("CVR-WAVE3-DB-FILTER-001")`; asserts both return non-None; asserts both have `tags` containing `"ADR-ISOLATION-APPLICATION-PLACEMENT-001"`. Note: T22 will fail until the implementation commit creates the IPR document. T22 is gated to skip-with-pending-marker before the implementation commit; it becomes a hard assertion after.

### Adds two regression items to `-003` Acceptance Criteria

The proposal is GO-able when Codex confirms (in addition to `-003`'s existing 9 criteria):

10. F1 fix is concrete: the amendment text contains the exact `_OUTPUT_DIR_ALLOWLIST_DESC` string and is bound to it by T21.
11. F2 fix is concrete: IPR and CVR document creation are explicit implementation steps; T22 verifies them; CVR's relationship to GOV-20 Phase 1's "DCL assertions are informational" caveat is documented (no DCL binds this surface yet).

## Risk / Impact Delta

`-003` Risk/Impact carries forward. Two additions for the F1/F2 fixes:

**Rule-text-vs-code drift risk (low after F1).** Bound by T21 asserting verbatim equality with `_OUTPUT_DIR_ALLOWLIST_DESC`. If a future M2 allowlist expansion lands without updating the rule citation, T21 fails in CI — the failure mode is loud, not silent.

**IPR/CVR overhead (low after F2).** IPR is created once at implementation time; CVR once at post-impl time; both are short documents (estimated <50 lines each). T22 is the only ongoing verification; it's a single KB query per test run.

## Decision Needed From Owner

Nothing required at GO time. All F1/F2 fixes are mechanical and Codex `-004` explicitly confirmed no owner decision needed for either.

Optional follow-up after VERIFIED (carried forward from `-003`):

- Whether ISOLATION-018 cutover should run the freeze-window runbook or extend it.
- Whether the unclassified warning list should drive a separate work item before ISOLATION-018.
- Whether the sandbox-output exception clause should be promoted to a more formal artifact (e.g., a DCL) once the amendment ships.
- Whether DCLs should follow for the isolation surface (currently no DCLs bind it; CVR explicitly documents this).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
