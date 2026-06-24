REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-24T23-07-02Z-prime-builder-B-e8efa4
author_model: claude-sonnet-4-6
author_model_version: 4.6
author_model_configuration: bridge auto-dispatch Prime Builder REVISED proposal

# Implementation Proposal (REVISED) - Resolve managed-artifact drift=9: normalize EOL in doctor comparison + refresh 5 true-content-diff templates

bridge_kind: prime_proposal
Document: gtkb-managed-artifact-drift-scaffold-template-refresh
Version: 005 (REVISED)
Date: 2026-06-24 UTC
Responds to NO-GO: bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-004.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4630

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/templates/hooks/assertion-check.py", "groundtruth-kb/templates/hooks/spec-event-surfacer.py", "groundtruth-kb/templates/hooks/_delib_common.py", "groundtruth-kb/templates/hooks/gov09-capture.py", "groundtruth-kb/templates/rules/file-bridge-protocol.md", "groundtruth-kb/tests/test_doctor_registry_parity.py", "groundtruth-kb/tests/test_doctor_adoption_drift.py"]

## Claim

The previous post-GO blocker report (`-003`) and LO NO-GO (`-004`) identified two blockers that prevented the original 8-template refresh from clearing `gt project doctor` managed-artifact drift:

**F1 (CRLF/hashing):** `_check_managed_artifact_drift` uses `_hash_file` which calls `path.read_bytes()` — raw byte hashing — so CRLF vs LF end-of-line differences register as drift even when file content is semantically identical. Four artifacts (`hook.destructive-gate`, `hook.credential-scan`, `rule.bridge-essential`, `rule.deliberation-protocol`) are CRLF-only drifts: their content is byte-identical to the LF-normalized templates after EOL stripping.

**F2 (out-of-scope drift):** Two artifacts (`hook._delib_common`, `hook.gov09-capture`) have true content drift but were outside the original `target_paths`.

**REVISED approach:**

1. Fix `_check_managed_artifact_drift` in `doctor.py` to normalize EOL (replace `\r\n` → `\n`) in both live-file and template-file content before hashing. This clears the 4 CRLF-only drifts without modifying any templates or live files.

2. Refresh exactly the 5 templates that have true content differences:
   - `hook.assertion-check` (live CRLF + content changed; both factors)
   - `hook.spec-event-surfacer` (content changed)
   - `hook._delib_common` (content changed; newly in scope per F2)
   - `hook.gov09-capture` (content changed; newly in scope per F2)
   - `rule.file-bridge-protocol` (content changed)

3. Add a test for the EOL-normalized comparison to `test_doctor_adoption_drift.py` and update the byte-parity regression test in `test_doctor_registry_parity.py` to cover the 5 refreshed artifacts.

A separate drift analysis confirmed the drift classification: 4 CRLF-only and 5 true-content-diff among the 9 currently drifted artifacts. Two artifacts (`hook.spec-classifier`, `hook.owner-decision-capture`) are already current and require no changes.

## Requirement Sufficiency

Existing requirements sufficient. The governing specs already require scaffold templates to be the authoritative source for `gt-kb-managed` artifacts and to remain consistent with the live framework surface. The REVISED approach adds doctor.py to scope to fix a latent correctness defect (CRLF-insensitive comparison) and expands the template refresh to include the two newly-identified out-of-scope drift artifacts. No new specification or requirement is introduced.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/templates/hooks/assertion-check.py`
- `groundtruth-kb/templates/hooks/spec-event-surfacer.py`
- `groundtruth-kb/templates/hooks/_delib_common.py`
- `groundtruth-kb/templates/hooks/gov09-capture.py`
- `groundtruth-kb/templates/rules/file-bridge-protocol.md`
- `groundtruth-kb/tests/test_doctor_registry_parity.py`
- `groundtruth-kb/tests/test_doctor_adoption_drift.py`

No live `.claude/` files are touched; all modifications remain within the GT-KB platform package.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-authorized implementation must stay inside the approved target paths.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — managed scaffold templates and live framework surfaces must not silently diverge; doctor detection must be accurate.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives tests from the cited specs (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the change is confined to the GT-KB platform package (`groundtruth-kb/src/`, `groundtruth-kb/templates/`, `groundtruth-kb/tests/`); no adopter/application subtree is touched.
- `GOV-STANDING-BACKLOG-001` — WI-4630 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — two of the five refreshed artifacts are hooks in the dual-harness boundary; refreshing their templates keeps the scaffolded hook surface consistent with the live hook contract.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the template/live reconciliation keeps the managed-artifact state artifact-backed rather than inferred or divergent.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the new EOL-normalized comparison and parity tests wire drift detection to a deterministic trigger so future divergence is caught accurately.

## Prior Deliberations

- `bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-001.md` (NEW) — original proposal to refresh 8 stale templates from live; approved scope and PAUTH linkage carried forward.
- `bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-002.md` (GO) — LO GO authorizing implementation within the original 9-path `target_paths`; confirmed specification links and test plan.
- `bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-003.md` (NEW/blocker) — Prime Builder post-GO report: found that raw-byte hashing in `_hash_file` conflates CRLF vs LF as drift; additionally, `_delib_common.py` and `gov09-capture.py` are drifted but outside original scope.
- `bridge/gtkb-managed-artifact-drift-scaffold-template-refresh-004.md` (NO-GO) — LO NO-GO confirming both blockers; directed REVISED to either fix doctor EOL comparison or establish EOL policy, and to expand `target_paths` for the two out-of-scope drifted artifacts.
- `DELIB-20265457` — owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane batch including WI-4630.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-LIVE-PLUS-TEMPLATES` — established "live plus templates" propagation discipline; this REVISED applies it to the correct artifact set after drift-class analysis.
- `bridge/gtkb-wi4672-bridge-compliance-gate-template-parity-002.md` (VERIFIED) — prior precedent for refreshing one managed hook template from live with a CRLF-normalized parity test; this REVISED applies the identical pattern to the remaining 5 true-content-diff artifacts.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` — project-scoped authorization envelope covering the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch; WI-4630 is an in-scope reliability defect/improvement under this PAUTH. Implementation is authorized once Loyal Opposition records GO on this REVISED proposal.
- `DELIB-20265457` — owner AUQ (2026-06-21) authorizing this PROJECT-GTKB-RELIABILITY-FIXES batch and directing authoring of NEW proposals for the open reliability work items; WI-4630 is one of the batch items. The REVISED scope (doctor fix + expanded template set) is a technical refinement within the same authorized work item.

## Proposed Scope

### Part 1 — Fix EOL normalization in `doctor.py` (addresses NO-GO F1)

Update `_hash_file` (line 2573–2576) to normalize EOL before hashing, or introduce a companion function `_hash_file_normalized` used exclusively by `_check_managed_artifact_drift`:

```python
def _hash_file_normalized(path: Path) -> str:
    import hashlib
    content = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()
```

Update the two call sites at lines 2634–2635 in `_check_managed_artifact_drift` to use `_hash_file_normalized` instead of `_hash_file`. The existing `_hash_file` (raw bytes) is preserved for any other callers.

This change makes 4 CRLF-only drifted artifacts pass the managed-artifact drift check without any template or live-file modification:
- `hook.destructive-gate`
- `hook.credential-scan`
- `rule.bridge-essential`
- `rule.deliberation-protocol`

### Part 2 — Refresh 5 true-content-diff templates from live (addresses NO-GO F1 partially + F2)

Copy exactly the current live `.claude/` content into each template, then LF-normalize the committed result:

| Template path | Live source | Drift class |
|---|---|---|
| `groundtruth-kb/templates/hooks/assertion-check.py` | `.claude/hooks/assertion-check.py` | True content diff (+ CRLF) |
| `groundtruth-kb/templates/hooks/spec-event-surfacer.py` | `.claude/hooks/spec-event-surfacer.py` | True content diff |
| `groundtruth-kb/templates/hooks/_delib_common.py` | `.claude/hooks/_delib_common.py` | True content diff (newly in scope) |
| `groundtruth-kb/templates/hooks/gov09-capture.py` | `.claude/hooks/gov09-capture.py` | True content diff (newly in scope) |
| `groundtruth-kb/templates/rules/file-bridge-protocol.md` | `.claude/rules/file-bridge-protocol.md` | True content diff |

Direction is strictly UP (live → template); no live file is modified. Templates are committed LF-normalized.

### Part 3 — Add/update tests

**`test_doctor_adoption_drift.py`:** Add a test verifying that `_check_managed_artifact_drift` reports `pass` when live file is CRLF and template is LF but content is semantically identical after normalization. This directly regression-tests the F1 fix.

**`test_doctor_registry_parity.py`:** Add a parametrized byte-parity regression test `test_managed_artifact_templates_match_live` asserting that for each of the 5 refreshed artifact IDs, the CRLF-normalized sha256 of the template equals that of the live `.claude/` counterpart. This prevents silent template drift re-accumulation.

### What is NOT in scope

- The 4 CRLF-only templates (`hook.destructive-gate`, `hook.credential-scan`, `rule.bridge-essential`, `rule.deliberation-protocol`) do NOT need template refresh — the doctor normalization fix in Part 1 is sufficient.
- `hook.spec-classifier` and `hook.owner-decision-capture` are already current (no drift); no changes needed.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (drift detection must be accurate and not falsely report CRLF-only differences as drift) | `test_managed_artifact_drift_crlf_normalized_passes` in `test_doctor_adoption_drift.py` | `_check_managed_artifact_drift` reports `pass` when live file is CRLF and template is LF-normalized but content is semantically identical. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (scaffold template is authoritative and consistent with the live surface) | `test_managed_artifact_templates_match_live[<artifact-id>]` (parametrized over 5 artifacts) in `test_doctor_registry_parity.py` | For each of the 5 refreshed artifacts, CRLF-normalized sha256 of `groundtruth-kb/templates/<template>` equals CRLF-normalized sha256 of `.claude/<target>`. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (live hook behavior unchanged) | `test_managed_artifact_refresh_leaves_live_files_unchanged` in `test_doctor_registry_parity.py` | The 5 live `.claude/` files are byte-identical to their pre-change `git HEAD` blobs. |

Execution commands:
```
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_adoption_drift.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_registry_parity.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_adoption_drift.py groundtruth-kb/tests/test_doctor_registry_parity.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_adoption_drift.py groundtruth-kb/tests/test_doctor_registry_parity.py
```

## Acceptance Criteria

1. `gt project doctor --profile dual-agent` no longer reports any managed-artifact `drifted` entry for the 9 artifacts (4 CRLF-only cleared by doctor normalization + 5 true-content-diff cleared by template refresh).
2. Each of the 5 refreshed templates matches its live `.claude/` counterpart (CRLF-normalized byte parity).
3. No live `.claude/` file is modified (template + doctor change only; live hook/rule behavior unchanged).
4. The new EOL-normalization test and the updated parity tests pass; `ruff check` and `ruff format --check` are clean on the changed `.py` files.

## Risks / Rollback

- Risk: EOL normalization in `_hash_file_normalized` has unintended side effects on other callers. Mitigation: the existing `_hash_file` is preserved for other callers; only `_check_managed_artifact_drift` is updated to use the normalized variant.
- Risk: a live file has a local transient edit not committed to HEAD. Mitigation: the 5 live files are tracked, committed framework surfaces; inspection of the template refresh diff is part of LO verification.
- Risk: the normalization change silently accepts file differences that include only `\r` without `\n` (classic Mac CR endings). Mitigation: the normalization targets `\r\n` (Windows CRLF) specifically, preserving `\r` detection (rare in practice; can be added in a follow-on if needed).
- Rollback: revert `doctor.py` and the 5 template files and the two test additions. The change is content-only with no schema, registry, or live-surface change and is fully reversible.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (add `_hash_file_normalized`; update `_check_managed_artifact_drift` call sites)
- `groundtruth-kb/templates/hooks/assertion-check.py` (refresh from live; LF-normalize)
- `groundtruth-kb/templates/hooks/spec-event-surfacer.py` (refresh from live; LF-normalize)
- `groundtruth-kb/templates/hooks/_delib_common.py` (refresh from live; LF-normalize)
- `groundtruth-kb/templates/hooks/gov09-capture.py` (refresh from live; LF-normalize)
- `groundtruth-kb/templates/rules/file-bridge-protocol.md` (refresh from live; LF-normalize)
- `groundtruth-kb/tests/test_doctor_adoption_drift.py` (add CRLF-normalization test)
- `groundtruth-kb/tests/test_doctor_registry_parity.py` (add parity tests for 5 refreshed artifacts)

## Recommended Commit Type

`fix`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
