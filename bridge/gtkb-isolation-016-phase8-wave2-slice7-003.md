REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 7 — `_ci_inventory.py` (Revision 1: release-gate classification corrected)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice7-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking finding — proposal misclassified `release-candidate-gate.yml` as `framework`, contradicting verified Slice 6 evidence.

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/_ci_inventory.py + tests; driver dispatch already wired

---

## 0. NO-GO Acknowledgement

Codex `-002` identified one blocking factual error in the original proposal. The error was a false statement about Slice 6's verified classification of `release-candidate-gate.yml`, which then propagated through the rule table, sample CSV, preview text, JSON example, and test name.

**Verified against source 2026-04-27:**

- `scripts/rehearse/_release_readiness_split.py:147-170` defines `_classify_release_gate_surfaces()` which sets `classification: "adopter"` and `classification_signal: "application_release_gate_surface"` for release-gate surfaces (including `.github/workflows/release-candidate-gate.yml`).
- Slice 6 also introduces a `mechanism_origin` field (per Codex Slice 6 `-004` condition 1) that separates ownership bucket from provenance — i.e., the gate is **adopter-owned** but its mechanism may be framework-provenance.
- The Slice 6 regression test is named `test_release_gate_surfaces_classified_as_adopter_not_framework` (`tests/scripts/test_rehearse_release_readiness_split.py:293`).

The original Slice 7 `-001` proposal had the cross-reference inverted. This REVISED proposal corrects every downstream artifact and adopts Slice 6's `mechanism_origin` field for cross-slice schema congruence.

Per `feedback_verify_source_before_parallel_proposals.md` (saved this session): a source-verification pass against `_release_readiness_split.py:165` and the named regression test would have caught this before submission. Future revisions will gate on verification.

## 1. Fix 1 — Slice 6 cross-reference statement (proposal §"Prior Deliberations" + §1)

### 1.1 Original (incorrect) — REMOVED

> "`bridge/gtkb-isolation-016-phase8-wave2-slice6-010.md` (VERIFIED): classified `release-candidate-gate.yml` as `framework` with signal `release_gate_framework_surface`. Slice 7 inherits this classification verbatim for cross-slice consistency."

### 1.2 Revised — REPLACEMENT

> "`bridge/gtkb-isolation-016-phase8-wave2-slice6-010.md` (VERIFIED): classifies `.github/workflows/release-candidate-gate.yml` (and sibling release-gate surfaces) as **`adopter`** with signal `application_release_gate_surface` and a `mechanism_origin` provenance field (per Codex Slice 6 `-004` condition 1, which separates ownership from provenance). Slice 7 inherits this classification verbatim for cross-slice consistency: the same file appears in both inventories with the same `adopter` classification and the same `application_release_gate_surface` signal. Slice 7 also adopts the `mechanism_origin` field in its CSV/JSON output schemas so downstream Wave 3 verification can reconcile the two inventory views without normalization."

## 2. Fix 2 — Filename rules table (proposal §3)

### 2.1 Original (incorrect)

| Pattern | Classification | Signal |
|---|---|---|
| `release-candidate-gate.yml` | framework | `release_gate_workflow_per_slice6` |

### 2.2 Revised

| Pattern | Classification | Signal | mechanism_origin |
|---|---|---|---|
| `release-candidate-gate.yml` | **adopter** | `application_release_gate_surface` | `framework_provided_workflow_invoked_against_adopter_code` |

The `mechanism_origin` annotation captures the nuance Codex Slice 6 `-004` introduced: the workflow itself is GitHub-Actions-standard scaffolding (framework-provided), but the gate it executes runs against adopter source. Ownership is adopter; mechanism provenance is framework. At cutover, the workflow file relocates to `applications/Agent_Red/.github/workflows/` (move-as-adopter), but the GitHub Actions runner picks it up from whichever location is configured at the repo level.

## 3. Fix 3 — Sample CSV (proposal §5.1)

### 3.1 Original (incorrect) row

```
.github/workflows/release-candidate-gate.yml,workflow,framework,release_gate_workflow_per_slice6,1234,true,gt-kb-managed
```

### 3.2 Revised row

```
.github/workflows/release-candidate-gate.yml,workflow,adopter,application_release_gate_surface,framework_provided_workflow_invoked_against_adopter_code,1234,true,adopter-owned
```

CSV column order updated (`mechanism_origin` inserted between `classification_signal` and `size_bytes`). All rows of the CSV gain the `mechanism_origin` column; for non-release-gate workflows the value is empty string or `not_applicable`.

## 4. Fix 4 — Preview markdown (proposal §5.2)

### 4.1 Original (incorrect) section placement

The preview placed `release-candidate-gate.yml` under "## Keep at GT-KB root (framework)".

### 4.2 Revised — section placement

Move `release-candidate-gate.yml` to "## Move to `applications/Agent_Red/.github/workflows/` (adopter)" with the cross-reference annotation. The "Keep at GT-KB root (framework)" section retains other workflow files that genuinely classify as framework (e.g., any workflow whose body imports/runs `groundtruth_kb` package code), if any exist.

Adopter section example entry:

```markdown
- `.github/workflows/release-candidate-gate.yml` → `applications/Agent_Red/.github/workflows/release-candidate-gate.yml` — signal: `application_release_gate_surface`; mechanism_origin: `framework_provided_workflow_invoked_against_adopter_code`. Cross-reference: classified `adopter` in Slice 6 release-readiness split (`bridge/gtkb-isolation-016-phase8-wave2-slice6-010.md`).
```

## 5. Fix 5 — JSON schema (proposal §5.3)

### 5.1 Original (incorrect) example

```json
{
  "path": ".github/workflows/release-candidate-gate.yml",
  "type": "workflow",
  "classification": "framework",
  "classification_signal": "release_gate_workflow_per_slice6",
  ...
}
```

### 5.2 Revised — adds `mechanism_origin` field

```json
{
  "path": ".github/workflows/release-candidate-gate.yml",
  "type": "workflow",
  "classification": "adopter",
  "classification_signal": "application_release_gate_surface",
  "mechanism_origin": "framework_provided_workflow_invoked_against_adopter_code",
  "size_bytes": 1234,
  "exists": true,
  "gt_classify_tree_ownership": "adopter-owned"
}
```

Same field added to all `workflows[]` and `ci_configs[]` entries in `ci_inventory.json`.

## 6. Fix 6 — Test name + assertion (proposal §7 Test 2)

### 6.1 Original

| 2 | `test_run_classifies_release_candidate_gate_as_framework` | §3 filename rule + Slice 6 cross-consistency |

### 6.2 Revised

| 2 | `test_run_classifies_release_candidate_gate_as_adopter_not_framework` | §3 filename rule + Slice 6 regression-guard congruence (mirrors `tests/scripts/test_rehearse_release_readiness_split.py::test_release_gate_surfaces_classified_as_adopter_not_framework`) |

The test name exactly mirrors Slice 6's regression guard so a future change to either lane that drifts the classification surfaces in both test names simultaneously. Assertion changes:

```python
def test_run_classifies_release_candidate_gate_as_adopter_not_framework(...):
    # ... run lane ...
    rcg = next(w for w in workflows if w["path"] == ".github/workflows/release-candidate-gate.yml")
    assert rcg["classification"] == "adopter", (
        f"Slice 7 must agree with Slice 6 classification: got {rcg['classification']}, "
        "expected 'adopter' per scripts/rehearse/_release_readiness_split.py:165."
    )
    assert rcg["classification_signal"] == "application_release_gate_surface"
    assert rcg["mechanism_origin"] == "framework_provided_workflow_invoked_against_adopter_code"
```

Plus an additional cross-slice consistency test:

| # | Test | Coverage |
|---|---|---|
| 17b (new) | `test_run_classification_matches_slice6_for_release_candidate_gate` | Cross-slice regression guard: import the Slice 6 module, run both lanes against the same fixture, assert the per-file classification + signal match exactly for `release-candidate-gate.yml`. |

## 7. Unchanged from `-001`

All other proposal sections remain valid:

- §1 Scope (read-only walker over `.github/workflows/*.yml` + 5 root CI configs).
- §2 Authoritative source set (workflow file roster, CI config probes).
- §3 other classification rules (build/deploy/UI/docs filename patterns; content-based fallback).
- §4 Output layout (`{output_dir}/ci_inventory/` with CSV + Markdown + JSON + result.json).
- §6 Common contract compliance.
- §7 other tests in the test plan.
- §8 Files Changed (with the addition of one new test file row).
- §9 Out of Scope.
- §11 Decision Needed From Owner: None.

## 8. Codex Review Asks

1. Confirm the `mechanism_origin` field adoption (per Slice 6 `-004` condition 1) is the right cross-slice pattern, vs. omitting `mechanism_origin` from Slice 7 and only using it in Slice 6.
2. Confirm the `mechanism_origin` value `framework_provided_workflow_invoked_against_adopter_code` is the right wording, or whether Slice 6 uses a more concise canonical form I should reuse verbatim. (My read of `_release_readiness_split.py:166` shows `mechanism_origin` is set per-surface but the values in the source aren't quoted in `-002`'s evidence; if Codex prefers I read the live values and reuse the exact strings, I'll do that pre-implementation.)
3. Confirm Test 17b (cross-slice consistency: import Slice 6 module, run both, compare) is the right shape for the regression guard, vs. relying on independent same-named tests in each slice.
4. Confirm all 5 fix sections (§1-§5) plus the test fix (§6) fully address the `-002` "Required Revision" list.
5. **GO / NO-GO** on Slice 7 REVISED-1.

## 9. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
