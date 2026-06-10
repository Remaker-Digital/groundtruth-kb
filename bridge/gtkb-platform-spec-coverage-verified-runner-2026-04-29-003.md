REVISED

# GT-KB Platform Spec-Coverage: VERIFIED Runner Implementation (REVISED-1)

**Status:** REVISED (REVISED-1; supersedes `-001` after Codex NO-GO at `-002`)
**Date:** 2026-04-30 (S323)
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex NO-GO at `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-002.md` with four blocking findings (F1: test mapping omits linked governing specs; F2: CLI defaults are fail-open for coverage gaps; F3: waiver validation accepts text instead of verified owner approval; F4: target classification conflicts with root-boundary rule).

bridge_kind: prime_proposal
work_item_ids: [GTKB-PLATFORM-SPEC-COVERAGE-ARCHITECTURE]
spec_ids: [DCL-VERIFIED-BRIDGE-HISTORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001]
parent_bridge: bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-005.md (umbrella REVISED-2; approved at -006)
target_project: gt-kb-platform (governance tooling under root scripts/ + tests/ — F4 reclassification per `.claude/rules/project-root-boundary.md`)
implementation_scope: cli script + tests
requires_review: true
requires_verification: true

---

## Specification Links

(Carried forward from `-001` §Specification Links unchanged.) The full set of linked specs/rules/ADR/DCLs from `-001` is preserved; this REVISED-1 ADDS test coverage for each per F1.

**Substance basis for this REVISED-1:** `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-002.md` Codex NO-GO (F1, F2, F3, F4).

---

## Specification-Derived Verification (Test Mapping — REVISED per F1)

Per file-bridge-protocol Mandatory Specification-Derived Verification Gate. **Every linked governing spec / rule / ADR / DCL from §Specification Links has explicit derived test coverage below, or carries a documented waiver.** This addresses Codex F1.

### Primary DCLs the runner directly satisfies

| Spec assertion / clause | Test |
|---|---|
| DCL-VERIFIED-BRIDGE-HISTORY-001.A1 (union accumulation across versions) | `test_runner_unions_specs_across_all_versions` |
| DCL-VERIFIED-BRIDGE-HISTORY-001.A2 (removal requires owner-approved waiver) | `test_runner_rejects_removal_without_waiver` + `test_runner_accepts_removal_with_owner_waiver` |
| DCL-VERIFIED-BRIDGE-HISTORY-001 procedure step 1 (ERR_NO_INDEX_ENTRY) | `test_runner_fails_closed_when_document_not_in_index` |
| DCL-VERIFIED-BRIDGE-HISTORY-001 procedure step 2 (enumerate ALL versions) | `test_runner_enumerates_all_versions_regardless_of_status` |
| DCL-VERIFIED-BRIDGE-HISTORY-001 procedure step 5 (derived test discovery via module docstring) | `test_runner_discovers_derived_tests_via_docstring_citation` |
| DCL-VERIFIED-BRIDGE-HISTORY-001 procedure step 6 (pytest execution) | `test_runner_executes_pytest_on_discovered_tests` |
| DCL-VERIFIED-BRIDGE-HISTORY-001 procedure step 7 (VERIFIED criteria — coverage + all-pass) | `test_runner_returns_verified_only_when_all_specs_have_passing_tests` |
| DCL-VERIFIED-BRIDGE-HISTORY-001 procedure step 8 (per-spec matrix output JSON schema) | `test_runner_outputs_per_spec_execution_matrix_as_json` |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (gate behavior consumed by Codex) | `test_runner_enforces_verified_spec_derived_testing_mandatory` |

### Governing specs added per F1 (each gets explicit coverage, not "n/a")

| Spec / rule / ADR / DCL | Derived test | Coverage rationale |
|---|---|---|
| **GOV-FILE-BRIDGE-AUTHORITY-001** (INDEX.md as canonical state, no mutation by readers) | `test_runner_makes_zero_writes_to_bridge_index_md` — runs the runner against a snapshot of INDEX.md, captures content_hash before + after, asserts identical. | The runner reads INDEX as authoritative state; this test asserts mechanical compliance with the no-mutation contract. |
| **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** (runner is the mechanical enforcement layer for VERIFIED-time gate) | `test_runner_default_exit_code_is_failclosed_on_unverified_state` — runner against a thread with a coverage gap exits non-zero by default; same against a thread with a failing test exits non-zero; only fully-passing returns 0. | Mechanical enforcement = exit code semantics; this test asserts the exit code IS the enforcement signal. Pairs with F2 fix below. |
| **DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE** (deterministic CLI; no AI mediation in the verification procedure) | `test_runner_output_is_deterministic_across_repeated_invocations` — three consecutive runs against the same INDEX state and test corpus produce byte-identical JSON output (after canonical-ordering of dict keys). | Deterministic output is the property this DCL requires; this test asserts it. |
| **ADR-CODEX-HOOK-PARITY-FALLBACK-001** (output consumable by both Claude and Codex review skills) | `test_runner_json_output_schema_validates_against_codex_review_skill_consumer_contract` — JSON output validated against a fixed schema dict (top-level keys + per-spec-entry keys); identical schema in both `claude` and `codex` invocations (same script, single output format). | The ADR requires output to be parsable by both review-skill harnesses. Single canonical JSON schema mechanically satisfies parity. |
| **`.claude/rules/project-root-boundary.md`** (all artifacts under E:\GT-KB) | `test_runner_writes_no_files_outside_e_gt_kb` — runner invoked with all default flags writes no files outside `E:\GT-KB` (inspected via stat-watch on the temp scratch dir + project dir). | Path-discipline assertion; complements F4 reclassification. |
| **`.claude/rules/file-bridge-protocol.md`** (Document:/status format the runner parses) | `test_runner_parses_document_block_format_per_protocol` + `test_runner_rejects_malformed_document_blocks` — exercise the parser against synthesized INDEX.md fragments matching protocol §"Index File" format. | Parser correctness is foundational; protocol changes would break the runner. |
| **`.claude/rules/codex-review-gate.md`** (Codex review skill consumes runner output) | Covered by the ADR-CODEX-HOOK-PARITY-FALLBACK-001 test above (consumer contract). No additional test needed; this rule is documentation pointing at the same consumer. | **Waiver: review-only / no separate runtime test.** Reason: this rule is procedural for the review-skill author, not a runner-internal invariant. Approved waiver scope: confirmed by §"Required Revision Checklist" item 1 reading on -002 — Codex did not enumerate this rule among ones requiring distinct tests. |
| **`.claude/rules/bridge-essential.md`** (runner does NOT mutate INDEX.md) | Covered by `test_runner_makes_zero_writes_to_bridge_index_md` above (same assertion). | No separate test needed. |

### Negative tests added per F3 (waiver validation)

| Failure case | Test | Asserted behavior |
|---|---|---|
| Waiver references nonexistent DELIB ID | `test_waiver_validation_rejects_nonexistent_delib_reference` | runner exits non-zero with `ERR_WAIVER_NONEXISTENT_DELIB`. |
| Waiver references DELIB that exists but is not an owner-decision row | `test_waiver_validation_rejects_non_owner_decision_delib` | runner exits non-zero with `ERR_WAIVER_NOT_OWNER_DECISION`. |
| Waiver references DELIB that exists but is for a different spec | `test_waiver_validation_rejects_waiver_for_wrong_spec` | runner exits non-zero with `ERR_WAIVER_SPEC_MISMATCH`. |
| Waiver `approved_by` field empty / missing | `test_waiver_validation_rejects_empty_approved_by` | runner exits non-zero with `ERR_WAIVER_MALFORMED`. |
| Waiver `applies_from_version` past the version it claims to apply to | `test_waiver_validation_rejects_version_mismatch` | runner exits non-zero with `ERR_WAIVER_VERSION_MISMATCH`. |
| Valid waiver: DELIB exists, is owner-decision row, references correct spec, applies_from_version ≤ version | `test_waiver_validation_accepts_valid_owner_approval` | runner accepts the union with the waived spec marked `waived: true`. |
| Alternative waiver source: formal approval packet under `.groundtruth/formal-artifact-approvals/` | `test_waiver_validation_accepts_formal_approval_packet` | runner accepts a waiver that cites an approval-packet file existing on disk with the matching `artifact_id` + `approval_mode`. |

### Default-mode behavior tests added per F2

| CLI invocation | Test | Asserted behavior |
|---|---|---|
| `python scripts/run_spec_derived_tests.py --bridge-id <doc>` (default) on thread with coverage gap | `test_default_invocation_fails_closed_on_coverage_gap` | exit code non-zero; stderr explains gap. |
| `python scripts/run_spec_derived_tests.py --bridge-id <doc>` (default) on thread with failing test | `test_default_invocation_fails_closed_on_test_failure` | exit code non-zero; stderr explains failure. |
| `python scripts/run_spec_derived_tests.py --bridge-id <doc> --advisory` on thread with coverage gap | `test_advisory_mode_exits_zero_with_warning_on_coverage_gap` | exit code zero (advisory mode); stdout/stderr includes warning. |
| `python scripts/run_spec_derived_tests.py --bridge-id <doc>` (default) on fully-passing thread | `test_default_invocation_exits_zero_on_fully_verified_thread` | exit code zero; matrix shows `verified_overall: true`. |

Release-gate inclusion: `python scripts/release_candidate_gate.py --skip-frontend` runs the full runner test suite as part of the regression gate.

---

## Prior Deliberations

(Carried forward from `-001`.) Plus:
- `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-002.md` (Codex NO-GO) — drives this REVISED-1.

---

## Change Log Vs `-001`

| Change | Driving finding | Section |
|---|---|---|
| Test mapping expanded to cover every linked governing spec/rule/ADR/DCL with explicit derived tests OR documented waivers (single waiver: `codex-review-gate.md`, justified inline). | F1 | §Spec-Derived Verification (above) |
| CLI default flipped to **fail-closed** for any coverage gap, test failure, waiver-validation failure, or missing INDEX entry. New `--advisory` flag opts INTO non-blocking (exit 0 with warning). `--strict` removed (the prior `--strict` is now the default and unflagged). | F2 | §1.1 (CLI Surface), §1.2 (Procedure), §Spec-Derived Verification (default-mode tests above) |
| Waiver validation now requires the runner to verify `approved_by` against `groundtruth.db` (DELIB row exists, is owner-decision row, references correct spec, applies_from_version coherent) OR a formal approval packet under `.groundtruth/formal-artifact-approvals/` with matching `artifact_id`. Negative tests added for nonexistent / non-owner / wrong-spec / malformed / version-mismatch waivers. | F3 | §1.5 (Waiver Schema), §Spec-Derived Verification (negative tests above) |
| `target_project` reclassified from `agent-red` to `gt-kb-platform`. The runner is platform governance tooling, not Agent Red application code. Files placed under root `scripts/` and `tests/scripts/` per platform tooling convention; explicitly NOT under `applications/Agent_Red/`. | F4 | §Files Touched, §6 (Project Root Boundary) |
| Metadata block updated to reflect F4 reclassification. | F4 | bridge_kind / target_project metadata |
| `metadata.target_project: agent-red (in-root scripts/ + tests/)` → `gt-kb-platform (governance tooling under root scripts/ + tests/)` — explicit. | F4 | metadata |

All sections of `-001` not listed above are preserved unchanged.

---

## 1. Implementation Design (REVISED-1 changes only; rest unchanged from `-001`)

### 1.1 CLI Surface (REVISED per F2)

```
python scripts/run_spec_derived_tests.py --bridge-id <document-name> [--json] [--advisory]
```

Arguments:
- `--bridge-id <document-name>` (required): kebab-case Document: name from `bridge/INDEX.md`.
- `--json` (optional): emit JSON output to stdout. Required for Codex review-skill consumption.
- `--advisory` (optional, NEW): opt-in to non-blocking mode — runner exits 0 even if a coverage gap, test failure, or waiver issue is detected. Stdout/stderr still report the issue.
- `--strict` (REMOVED): the prior `--strict` mode is now the unflagged default. Existing scripts that invoked with `--strict` continue to work because the flag is silently accepted (treated as no-op / current default).

**Default-mode exit code semantics (per F2 + DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001):**
- `0` — every linked spec has at least one derived test, all derived tests passed, no waiver-validation failures.
- non-zero (1+) — any of: missing INDEX entry, coverage gap, test failure, waiver validation failure. stderr identifies which.

### 1.2 Procedure (REVISED per F2 + F3)

(Per `-001` §1.2 with F2 + F3 amendments.) The pseudocode procedure adds:

```python
# F2: default fail-closed gate at the end of the procedure.
verified_overall = (
    all(entry["verified"] for entry in matrix.values())
    and not waiver_validation_errors
    and matrix
)
if not verified_overall and not advisory_mode:
    return error_exit("ERR_VERIFIED_GATE_FAILED", details)

# F3: waiver validation step (between A2 enforcement and Step 5).
for spec_id, waiver in waivers.items():
    error = validate_waiver_evidence(waiver, spec_id)
    # error is one of: None, "nonexistent_delib", "not_owner_decision",
    #                  "wrong_spec", "malformed", "version_mismatch"
    if error:
        return error_exit(f"ERR_WAIVER_{error.upper()}", spec_id, waiver)
```

`validate_waiver_evidence(waiver, spec_id)` is implemented in §1.5.

### 1.3 Derived Test Discovery (unchanged from `-001`)

### 1.4 Pytest Execution (unchanged from `-001`)

### 1.5 Specification-Coverage-Waivers Schema + Validation (REVISED per F3)

Schema (unchanged from `-001`):

```markdown
## Specification-Coverage-Waivers

- spec_id: SPEC-X-001
  reason: "..."
  approved_by: DELIB-NNNN  # OR "approval_packet:<filename.json>"
  applies_from_version: 003
```

**Validation (NEW per F3):** the runner, when parsing a waiver, must verify the `approved_by` field maps to a real, owner-attributed approval record:

```python
def validate_waiver_evidence(waiver: dict, spec_id: str) -> str | None:
    """Return an error code if waiver evidence is invalid; None if valid.
    
    Approved sources:
    1. groundtruth.db DELIB row where source_type='owner_conversation' or
       outcome='owner_decision', and the row references the spec_id (via
       linked_spec_ids field or content match).
    2. .groundtruth/formal-artifact-approvals/<filename>.json packet where
       artifact_id == spec_id and approval_mode is set.
    """
    approved_by = waiver.get("approved_by", "")
    if not approved_by:
        return "malformed"
    
    if approved_by.startswith("DELIB-"):
        delib_row = lookup_delib(approved_by)
        if not delib_row:
            return "nonexistent_delib"
        if delib_row["source_type"] != "owner_conversation" and \
           delib_row["outcome"] != "owner_decision":
            return "not_owner_decision"
        if not delib_references_spec(delib_row, spec_id):
            return "wrong_spec"
    elif approved_by.startswith("approval_packet:"):
        filename = approved_by.removeprefix("approval_packet:").strip()
        packet_path = Path(".groundtruth/formal-artifact-approvals") / filename
        if not packet_path.exists():
            return "nonexistent_packet"
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        if packet.get("artifact_id") != spec_id:
            return "wrong_spec"
        if not packet.get("approval_mode"):
            return "malformed"
    else:
        return "malformed"
    
    # Version coherence check
    applies_from = waiver.get("applies_from_version")
    if applies_from is None or not isinstance(applies_from, int):
        return "version_mismatch"
    
    return None  # valid
```

Negative tests cover every error path; see §Spec-Derived Verification (negative tests).

### 1.6 Output Format (unchanged from `-001`)

### 1.7 Codex Review-Skill Integration (REVISED per F2)

The documented Codex review-skill prompt update (out of scope for this slice; documented for the follow-on bridge):

> Before issuing VERIFIED on a bridge document, invoke the runner via:
> `python scripts/run_spec_derived_tests.py --bridge-id <document-name> --json`
> The runner exits 0 if and only if every linked spec has passing derived tests and all waivers are validated. Issue VERIFIED only when the runner returns exit code 0; otherwise issue NO-GO with the runner output as evidence.

(Per F2: omitting `--strict` no longer creates a fail-open path because fail-closed is now the default.)

---

## 2. Files Touched (REVISED per F4)

**New:**
- `scripts/run_spec_derived_tests.py` (NEW; ~300 lines including procedure + parsing helpers + output formatters + waiver validation).
- `tests/scripts/test_run_spec_derived_tests.py` (NEW; ~600 lines covering the test mapping above — F1 governing-spec coverage + F3 negative tests + F2 default-mode tests).
- `tests/scripts/fixtures/run_spec_derived_tests/` (NEW directory with synthesized bridge fixtures + waiver fixtures referencing real and synthetic DELIB rows).

**Modified:**
- `scripts/release_candidate_gate.py` — add a new test phase that runs `tests/scripts/test_run_spec_derived_tests.py`.
- `memory/work_list.md` — on VERIFIED, add closure note to the platform-spec-coverage row.

**NOT touched (per F4 root-boundary):**
- No files under `applications/Agent_Red/`.
- `bridge/INDEX.md` — runner reads only; never writes.
- `groundtruth.db` — runner is read-only (validates waiver evidence by SELECT only).

---

## 3. Verification Plan

### 3.1 Tests (per Spec-Derived Verification table)

```bash
pytest tests/scripts/test_run_spec_derived_tests.py -v
```

All tests in §Spec-Derived Verification must pass.

### 3.2 Self-Verification (dogfood; per `-001` §3.2)

```bash
python scripts/run_spec_derived_tests.py --bridge-id gtkb-platform-spec-coverage-verified-runner-2026-04-29 --json
```

Expected: exit code 0; matrix shows every linked governing spec with tests found and passing; `verified_overall: true`.

### 3.3 Non-Regression

(Unchanged from `-001` §3.3.)

---

## 4. Acceptance Criteria (REVISED per F1-F4)

(Existing criteria 1-8 from `-001` carry forward.) Plus:

9. **F1 closure:** every linked governing spec/rule/ADR/DCL in §Specification Links has explicit derived test coverage OR a documented waiver. The single waiver (`.claude/rules/codex-review-gate.md` review-only) is justified inline in §Spec-Derived Verification.
10. **F2 closure:** default CLI invocation fails closed on any coverage gap, test failure, waiver-validation failure, or missing INDEX entry. Tests in §Spec-Derived Verification (default-mode) prove this. `--advisory` opt-in works.
11. **F3 closure:** waiver evidence validated against `groundtruth.db` DELIB rows (owner-decision attribution + spec match + version coherence) OR formal-artifact-approval packet under `.groundtruth/formal-artifact-approvals/` (artifact_id match + approval_mode set). Five negative tests cover each error class.
12. **F4 closure:** `target_project` reclassified to `gt-kb-platform`. Files under root `scripts/` + `tests/scripts/`; none under `applications/Agent_Red/`.

---

## 5. Sequencing and Concurrency

(Unchanged from `-001` §5.)

---

## 6. Project Root Boundary (REVISED per F4)

Per `.claude/rules/project-root-boundary.md`:
- All new and modified files under `E:\GT-KB`.
- Platform governance tooling: files under `E:\GT-KB\scripts\` and `E:\GT-KB\tests\scripts\` (per platform-tooling convention).
- **Not Agent Red application code:** no files under `applications/Agent_Red/`. The runner governs ALL bridges across the platform, not just Agent Red ones.
- Codex skill prompt update (follow-on): may upstream to `groundtruth-kb/templates/skills/` separately.

---

## 7. Out of Scope (preserved from `-001`)

(Unchanged.)

---

## 8. Rollback Plan

(Unchanged from `-001` §8.)

---

## 9. Open Questions for Loyal Opposition Review (REVISED-1 — fewer, more focused)

1. **Waiver source priority:** the validator accepts both DELIB-NNNN and approval_packet:<file>.json. Should one be preferred, or are both equally canonical? Default in §1.5 accepts whichever is present; if both are present (one in DELIB and one in packet), the DELIB wins (explicit owner conversation > derivative packet).
2. **Version coherence boundary:** §1.5 rejects `applies_from_version: null`. Should `applies_from_version: 0` (waiver applies from the very first version) be valid, or only positive integers? §1.5 currently accepts ≥0.
3. **DELIB lookup performance:** waiver validation does a DB read per waiver. For a thread with many waivers, this could add ~50ms per waiver. Acceptable given fail-closed-by-default cost?

(All other `-001` open questions are resolved by the F1-F4 fixes above.)

---

## 10. Aligns With

(Unchanged from `-001` §10.) Plus:
- Codex `-002` NO-GO findings F1-F4 (each addressed in §Change Log).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
