# Loyal Opposition Hygiene Assessment — Phase 1 & Phase 3 Synthesis

## Claim

The GroundTruth-KB repository's high hygiene anomaly counts (16,738 in Phase 1 and 705 in Phase 3) are primarily driven by false-positive parser logic in the scanner script rather than actual repository degradation; however, genuine referential gaps and legacy file structure noise exist and require disciplined remediation.

## Scope Assessed

A targeted assessment focusing on **Phase 1 (DA Harvest)** and **Phase 3 (Bridge Double-Versioning)**.
The following inputs and log files were analyzed:
- `C:\Users\micha\.gemini\antigravity\brain\c3092001-1d25-452c-a4b9-8a7e12ab6fc6\.system_generated\tasks\task-84.log` (Wrap Scan Hygiene check)
- `C:\Users\micha\.gemini\antigravity\brain\c3092001-1d25-452c-a4b9-8a7e12ab6fc6\.system_generated\tasks\task-96.log` (Wrap Scan Cross-Artifact Drift check)
- [scripts/wrap_scan_cross_artifact_drift.py](file:///e:/GT-KB/scripts/wrap_scan_cross_artifact_drift.py) (specifically the parser/regex logic for status extraction and deliberation matching)
- Legacy files under [bridge/](file:///e:/GT-KB/bridge/)

---

## Evidence Paths and Line References

- **`cross_delib_reference_missing` Parser Bug (1,367 instances):** [scripts/wrap_scan_cross_artifact_drift.py#L56](file:///e:/GT-KB/scripts/wrap_scan_cross_artifact_drift.py#L56) (`DELIB_ID_RE = re.compile(r"\bDELIB-[A-Z0-9][A-Z0-9_.-]*\b")`) matching literal text `"DELIB-ID"` in markdown headers.
- **`spec_delib_content_drift` Heuristic Flaw (14,695 instances):** [scripts/wrap_scan_cross_artifact_drift.py#L34-53](file:///e:/GT-KB/scripts/wrap_scan_cross_artifact_drift.py#L34-L53) (`STATUS_WORDS` definition), [#L125-139](file:///e:/GT-KB/scripts/wrap_scan_cross_artifact_drift.py#L125-L139) (`_extract_status_claim` window match and frozenset iteration).
- **Genuine Linkage Gaps (676 instances):** Mentions of missing deliberation keys (e.g., `DELIB-S312`, `DELIB-FABLE-GRILL-20260610-Q1..Q7`, `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE`) in the sqlite-backed `deliberations` table.
- **`bridge_files_without_status` (705 instances):** Legacy bridge files lacking line-1 status tokens. Example: [bridge/s291-phase1.5-verified-spec-audit-001.md#L1-5](file:///e:/GT-KB/bridge/s291-phase1.5-verified-spec-audit-001.md#L1-L5) (lacks a status token like `NEW` or `GO` on line 1, status is on line 5 instead).
- **`bridge_target_paths_actual_change_gap` (13 instances):** Temporary/untracked files in the root worktree not declared in target paths (e.g. `.harness-tmp/`, `.loyal-opposition/`, `.temp_verdict_body_gtkb_w5005.md`, `work_area/`).

---

## Severity-Ranked Findings

### P2: Flawed and Non-Deterministic Spec-Delib Status Drift Heuristic
- **Finding:** The `spec_delib_content_drift` check (14,695 anomalies) uses a loose 160-character search window after any spec ID mention to find status keywords. This has two critical defects:
  1. It iterates over a `frozenset` of `STATUS_WORDS`, introducing non-deterministic matching based on Python's hash randomization.
  2. It conceptually conflates chronological, immutable deliberation logs (which preserve the status *at the time of the deliberation*) with the current MemBase spec status.
- **Evidence:** [scripts/wrap_scan_cross_artifact_drift.py#L125-139](file:///e:/GT-KB/scripts/wrap_scan_cross_artifact_drift.py#L125-L139).
- **Classification:** `prime-action`

### P2: Regex Extraction Bug in Deliberation Reference Parsing
- **Finding:** The `cross_delib_reference_missing` check has 2,043 anomalies, but 1,367 (over 67%) are false positives where the scanner matches the literal string `"DELIB-ID"` (frequently used in table headers) and flags it as a missing deliberation.
- **Evidence:** [scripts/wrap_scan_cross_artifact_drift.py#L56](file:///e:/GT-KB/scripts/wrap_scan_cross_artifact_drift.py#L56) matching `DELIB-ID` in the `deliberations` table.
- **Classification:** `prime-action`

### P2: Genuine Missing Deliberation References (Linkage Gaps)
- **Finding:** Multiple active deliberations cite historical deliberations (e.g., `DELIB-S312`, `DELIB-S310`, `DELIB-FABLE-GRILL-20260610-Q1..Q7`) that are absent from the `deliberations` table in `groundtruth.db`.
- **Evidence:** `task-96.log` (cross_delib_reference_missing findings, excluding `"DELIB-ID"`).
- **Classification:** `peer-prime-candidate`

### P3: Legacy Bridge Files Lacking Line-1 Status Tokens
- **Finding:** 705 legacy bridge files (pre-dating modern status-token enforcement) trigger warnings because they do not have a lifecycle token (`NEW`, `GO`, `VERIFIED`) on the first line.
- **Evidence:** `task-84.log` (`bridge_files_without_status` findings). Example: [bridge/s291-phase1.5-verified-spec-audit-001.md](file:///e:/GT-KB/bridge/s291-phase1.5-verified-spec-audit-001.md).
- **Classification:** `peer-prime-candidate`

### P3: Worktree Clutter (Target Path Gaps)
- **Finding:** 13 untracked or modified temporary paths are left in the repository root without ignore rules, polluting local git status and triggering target-path coverage warnings.
- **Evidence:** `task-96.log` (`bridge_target_paths_actual_change_gap` list including `.harness-tmp/`, `work_area/`, `.loyal-opposition/`).
- **Classification:** `peer-prime-candidate`

---

## Phase-Ranked Action Plan

### Recommended Execution Order
1. **Phase 1 (DA Harvest & Linkage) - Parser Fixes:** Remediate scanner logic bugs (Findings 1 & 2) first to eliminate >16,000 false positives and reveal the true state of the repository.
2. **Phase 7 (Gitignore & Scripts Triage):** Standardize cleanup or exclusion of worktree temporary directories (Finding 5).
3. **Phase 1 (DA Harvest & Linkage) - Content Fixes:** Audit and resolve genuine missing deliberation citations (Finding 3).
4. **Phase 3 (Bridge Double-Versioning):** Establish a historical exemption or whitelist for legacy bridge files (Finding 4) to quiet the parser warnings without mutating old records.

---

## Prime Builder Implementation Sequence

1. **Fix `DELIB_ID_RE` regex or filter out "DELIB-ID"**: Modify `check_cross_delib_references` in [scripts/wrap_scan_cross_artifact_drift.py](file:///e:/GT-KB/scripts/wrap_scan_cross_artifact_drift.py) to explicitly discard the literal string `"DELIB-ID"`.
2. **Refactor `_extract_status_claim`**: Update the status extraction heuristic. Replace the loose `frozenset` keyword scanner with a deterministic, ordered precedence list (e.g. `list` instead of `frozenset`) or restrict matching to explicit pattern declarations (e.g. `status: <word>`). Consider deprecating `spec_delib_content_drift` or converting it to an advisory-only check that ignores deliberations with historical outcomes.
3. **Clean up worktree noise**: Add temporary test artifacts (like `.harness-tmp/`, `work_area/`, `.loyal-opposition/`) to `.gitignore` or ensure they are cleaned up programmatically at the end of runs.

---

## Peer Prime Delegation Candidates

- Bulk-adding temporary files and directories to the project `.gitignore`.
- Sourcing and backfilling missing historical deliberations (e.g., extracting `DELIB-S312` text from archive logs and inserting them).

---

## LO Verification Plan

- After the Prime Builder patches [scripts/wrap_scan_cross_artifact_drift.py](file:///e:/GT-KB/scripts/wrap_scan_cross_artifact_drift.py), run a dry-run hygiene scan to verify that total findings drop from >17,000 to below 1,000 (once the false positives are removed).
- Audit the updated regex and matching logic to ensure no regression in detecting valid deliberation references.

---

## Explicit Do-Not-Touch / Deferred Areas

- **Do not edit historical bridge files:** Do not attempt to add status tokens to the 705 legacy bridge files. These are immutable history and editing them in place violates bridge chain integrity constraints. Use a parser whitelist/exemption pattern instead.
- **Do not edit historical deliberations:** Do not rewrite old deliberation text to update status claims to match current MemBase values.

---

## Owner Decisions Required

- **None:** The suggested fixes are internal tool improvements and standard backlog maintenance.

---

## Residual Risk

- Historical logs that mention status in a way that mimics explicit declarations might still cause minor advisory-level warnings, which should be accepted as baseline noise.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
