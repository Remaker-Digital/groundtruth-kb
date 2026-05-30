REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-s368-platform-tests-ruff-revised-5-impl-proposal
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Platform Tests Ruff Cleanup (REVISED-5: implementation_proposal under new WI-specific PAUTH)

bridge_kind: implementation_proposal
Document: gtkb-platform-tests-ruff-cleanup
Version: 005 (REVISED)
Responds-To: bridge/gtkb-platform-tests-ruff-cleanup-004.md (Codex NO-GO)
Carries-Forward: bridge/gtkb-platform-tests-ruff-cleanup-003.md (REVISED-3)
Implements: WI-3423
Work Item: WI-3423
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001
target_paths: ["platform_tests/**/*.py"]
Recommended commit type: fix:
Date: 2026-05-28 UTC

## Revision Summary

REVISED-5 converts this thread from `bridge_kind: spec_intake` (REVISED-3) to `bridge_kind: implementation_proposal`. The conversion is now possible because the prerequisite PAUTH-creation work was split into the separate thread `gtkb-wi-3423-pauth-creation` (VERIFIED at -004), which created `PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001`. That PAUTH now exists in MemBase, so this proposal can cite it cleanly in `Project Authorization:` metadata — resolving Codex NO-GO-004's core finding (spec_intake bridge_kind cannot bind the impl-auth packet to a PAUTH).

Changes from REVISED-3:

1. **bridge_kind**: `spec_intake` → `implementation_proposal`. The proposal now binds to a real existing PAUTH.
2. **Project Authorization metadata**: now cites `PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001` (created + VERIFIED via `gtkb-wi-3423-pauth-creation` thread).
3. **target_paths**: narrowed to `["platform_tests/**/*.py"]` only. The DELIB + PAUTH creation (and their packets + groundtruth.db inserts) are DONE — they happened in the separate PAUTH-creation thread, so they are no longer in this thread's scope.
4. **Implementation Plan**: dropped Steps 0-2 (DELIB capture, PAUTH creation, impl-auth-under-new-PAUTH) — those are complete. Plan now starts at the ruff cleanup itself.
5. **Live count refreshed**: REVISED-3 cited 66 violations / 61 fixable across 42 files. Live re-probe at this filing (2026-05-28) shows **71 violations / 66 auto-fixable across 43 files** — parallel-session test additions drifted the count upward. The implementation will re-run the live count at execution time and report the actual numbers.

## Response To NO-GO -004

Codex NO-GO-004 P1-001 (the only blocking finding): REVISED-3's operative file declared `bridge_kind: spec_intake` and omitted parseable `Project Authorization:` / `Project:` metadata, so `scripts/implementation_authorization.py` could not bind the implementation-start packet to the WI-specific PAUTH. A direct parser check on `-003` returned `project_authorization = None`.

**Resolved**: This REVISED-5 is `bridge_kind: implementation_proposal` with `Project Authorization: PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001` as parseable metadata. The PAUTH exists in MemBase (VERIFIED via `gtkb-wi-3423-pauth-creation-004`). `implementation_authorization.py begin --bridge-id gtkb-platform-tests-ruff-cleanup` will now extract and bind the PAUTH. The earlier findings from NO-GO-002 (size envelope P1-001, mutation-class P1-002) were already addressed structurally by the new PAUTH: it is WI-specific (not the fast-lane standing PAUTH) and explicitly includes `test_modification`.

## Summary

This is the mechanical 42-file (currently 43-file) ruff lint cleanup of `platform_tests/`, now authorized under `PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001` (WI-3423, `test_modification` class included). The cleanup auto-fixes the bulk of violations via `ruff check --fix` and manually resolves the remainder. No MemBase mutations, no governance-artifact creation — those completed in the prerequisite thread.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this REVISED-5 filed at the next version of the thread.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the sole target path glob `platform_tests/**/*.py` is within `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below maps verification to ruff + pytest commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, Project Authorization, Work Item, Implements lines present in header.
- `GOV-STANDING-BACKLOG-001` - WI-3423 active under PROJECT-GTKB-RELIABILITY-FIXES.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - cleanup runs under PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001 (the framework's WI-specific authorization).
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the cited PAUTH satisfied envelope requirements (verified in the PAUTH-creation thread).
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the cited PAUTH was created through the bridge protocol (gtkb-wi-3423-pauth-creation, VERIFIED).
- `GOV-RELIABILITY-FAST-LANE-001` - cited with explicit statement: this work is NOT fast-lane eligible (43-file scope exceeds the size envelope); it runs under the dedicated WI-specific PAUTH, preserving the fast-lane standing PAUTH envelope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - traceability between WI-3423, the PAUTH-creation thread, this cleanup thread, and the commit; WI-3423 lifecycle advances to resolved post-VERIFIED.

## Requirement Sufficiency

Existing requirements sufficient. WI-3423 is approved and now has a dedicated PAUTH (VERIFIED). No new requirements. No new specifications.

## KB Mutation Scope

This thread performs NO MemBase mutations during implementation. `groundtruth.db` is intentionally NOT in `target_paths`.

The DELIB + PAUTH inserts associated with WI-3423's authorization were completed in the separate `gtkb-wi-3423-pauth-creation` thread (VERIFIED at -004) and are not part of this thread's scope. The only optional post-VERIFIED MemBase touch is a WI-3423 lifecycle transition (`backlogged` → `resolved`), which is a standard post-completion bookkeeping step handled outside the cleanup commit.

The only file-system mutations are `platform_tests/**/*.py` (the ruff cleanup), all covered by the PAUTH's `source` / `test_modification` / `test_addition` mutation classes.

## Prior Deliberations

- `bridge/gtkb-platform-tests-ruff-cleanup-004.md` (Codex NO-GO on REVISED-3): impl-auth packet cannot bind spec_intake bridge_kind to a PAUTH. Resolved here by converting to implementation_proposal citing the now-existing PAUTH.
- `bridge/gtkb-platform-tests-ruff-cleanup-003.md` (REVISED-3): tried to create PAUTH + run cleanup in one spec_intake thread; superseded by the split.
- `bridge/gtkb-platform-tests-ruff-cleanup-002.md` (Codex NO-GO): original size-envelope + mutation-class findings; addressed structurally by the WI-specific PAUTH.
- `bridge/gtkb-wi-3423-pauth-creation-004.md` (Codex VERIFIED): the prerequisite thread that created PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001. This REVISED-5 is the companion-refile step that thread's plan anticipated.
- `DELIB-S366-PLATFORM-TESTS-RUFF-PAUTH-PATH`: the owner-decision deliberation (S366 AUQ: WI-specific PAUTH path) that authorized the dedicated PAUTH; cited as the PAUTH's owner_decision_deliberation_id.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`: standing reliability fast-lane direction; explicitly contrasted (this work is non-fast-lane).

## Owner Decisions / Input

- **S366 AUQ (prior session)**: "WI-specific PAUTH for WI-3423 (Recommended)" — authorized the dedicated PAUTH path. Captured in DELIB-S366-PLATFORM-TESTS-RUFF-PAUTH-PATH, which the PAUTH cites.

No additional owner decisions are required for this REVISED-5. The cleanup runs under the already-approved-and-VERIFIED PAUTH; the ruff cleanup itself is mechanical and does not require per-file owner approval. No protected narrative-artifact paths are touched (target is `platform_tests/**/*.py` only — test source, not narrative authority).

## Implementation Plan

### Step 1 — Refresh impl-auth packet under the new PAUTH

`python scripts/implementation_authorization.py begin --bridge-id gtkb-platform-tests-ruff-cleanup`

This will extract `Project Authorization: PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001` from this operative file and bind the implementation-start packet to it. (REVISED-3's spec_intake form returned `project_authorization = None`; this implementation_proposal form binds correctly.)

### Step 2 — Capture pre-cleanup baseline

1. `ruff check platform_tests/ --output-format json` — record the live violation count and affected-file list at execution time (filing-time snapshot: 71 violations / 66 auto-fixable across 43 files; will re-measure at execution).
2. `ruff check platform_tests/ --statistics` — record the rule-code breakdown.

### Step 3 — Execute the auto-fix

1. `ruff check --fix platform_tests/` — auto-fix the auto-fixable violations (filing-time: 66 of 71).
2. `ruff format platform_tests/` — apply format consistency.

### Step 4 — Resolve remaining non-auto-fixable violations manually

1. `ruff check platform_tests/` — list residual violations (filing-time estimate: ~5, predominantly SIM117 multiple-with-statements and SIM103 needless-bool, which are judgment calls).
2. Manually fix each, recording per-violation rationale in the post-impl report.

### Step 5 — Verification

1. `ruff check platform_tests/` → 0 errors.
2. `ruff format --check platform_tests/` → no diff.
3. `python -m pytest platform_tests/ -q` → all tests pass; any regression introduced by an import-reorder or with-statement-merge explicitly identified and triaged in the post-impl report.

### Step 6 — Scoped commit

1. Inspect the staged index (`git diff --cached --name-only`) — confirm only `platform_tests/**/*.py` files are staged (per the parallel-session staging-contamination hazard; explicit pathspec staging).
2. Commit with `fix:` type referencing WI-3423 and this thread.

### Step 7 — Post-impl report + INDEX

File post-impl report with: pre/post ruff counts, the rule-code breakdown, per-manual-fix rationale, pytest summary, and the scoped-commit evidence.

## Spec-to-Test Mapping

| Specification | Verification Command Or Artifact | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This REVISED-5 filed at bridge path; INDEX updated. | PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Sole target glob `platform_tests/**/*.py` in-root. | PASS. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-platform-tests-ruff-cleanup` | `preflight_passed: true`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping + post-impl observed results. | PASS - mapping present. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header Project / Project Authorization / Work Item / Implements lines present. | PASS. |
| `GOV-STANDING-BACKLOG-001` | WI-3423 active under PROJECT-GTKB-RELIABILITY-FIXES. | PASS. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `implementation_authorization.py begin` binds the PAUTH (Step 1). | PASS at impl. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | PAUTH created via bridge (gtkb-wi-3423-pauth-creation VERIFIED). | PASS. |
| `GOV-RELIABILITY-FAST-LANE-001` | Explicit non-eligibility; dedicated WI-specific PAUTH used. | PASS - documented. |
| Ruff cleanup verification | `ruff check platform_tests/` after Step 4. | PASS - 0 errors. |
| Ruff format consistency | `ruff format --check platform_tests/` after Step 3. | PASS - no diff. |
| Pytest non-regression | `python -m pytest platform_tests/ -q` after Step 4. | PASS - all tests pass or regressions explicitly triaged. |

## Acceptance Criteria

- [ ] Codex returns GO on this REVISED-5.
- [ ] `implementation_authorization.py begin --bridge-id gtkb-platform-tests-ruff-cleanup` produces a packet citing PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001 (Step 1).
- [ ] `ruff check platform_tests/` returns 0 errors after Step 4.
- [ ] `ruff format --check platform_tests/` returns no diff after Step 3.
- [ ] `python -m pytest platform_tests/ -q` passes (or regressions explicitly identified) after Step 5.
- [ ] Scoped commit contains only `platform_tests/**/*.py` files (Step 6 staged-index inspection).
- [ ] WI-3423 transitions to `resolved` post-VERIFIED (bookkeeping; outside the cleanup commit).
- [ ] Codex returns VERIFIED on post-impl.

## Risk and Rollback

Risk: low to moderate. The bulk of violations are ruff-auto-fixable (mechanical); a handful require manual review. The mutation surface is bounded to `platform_tests/**/*.py`.

Risks:
- **Test regressions from auto-fix**: An import reorder (I001, 31 instances) or with-statement merge (SIM117, 14 instances) could change behavior or break a test that depends on import side-effect ordering. Mitigation: Step 5 runs the full `platform_tests/` pytest suite; any regression is triaged before commit.
- **Count drift**: parallel sessions keep adding test files; the live count drifted from 66 (REVISED-3) to 71 (this filing). Mitigation: implementation re-measures at execution and the post-impl reports actual pre/post numbers, not the filing-time estimate.
- **Staging contamination**: ~500 unrelated working-tree files from parallel sessions. Mitigation: Step 6 explicit-pathspec staging + `git diff --cached --name-only` verification.
- **SIM117 unsafe-fix**: the 14 multiple-with-statements include a hidden unsafe-fix; these are addressed manually (Step 4), not via `--unsafe-fixes`.

Rollback: `git revert` the cleanup commit; mass-revert is safe because the cleanup is mechanical and bounded to test files.

## Verification Limitations Anticipated

- The verification scope is the cleanup result (0 ruff errors + green pytest). The Codex NO-GO-002 opportunity-radar finding (a deterministic check mapping target_paths × mutation_classes to flag ambiguous existing-test modification) is a separate follow-on improvement, not addressed here.

## Files Touched (target_paths recap)

- `platform_tests/**/*.py` — the ruff-cleanup mutations (filing-time: 43 affected files).

Bridge filing artifacts (workflow infrastructure, not implementation scope):
- `bridge/gtkb-platform-tests-ruff-cleanup-005.md` (this file)
- `bridge/INDEX.md` (entry update)
- Next post-impl report (at `-NNN`)

## Loyal Opposition Asks

1. Confirm the conversion from `spec_intake` (REVISED-3) to `implementation_proposal` (this REVISED-5) correctly closes NO-GO-004 P1-001 now that PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001 exists and is VERIFIED.
2. Confirm the narrowed `target_paths: ["platform_tests/**/*.py"]` correctly excludes the already-completed governance work (DELIB + PAUTH inserts done in the separate thread).
3. Confirm the impl-auth packet will bind correctly to the cited PAUTH (a parser check on this operative file should return `project_authorization = PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001`, not None).
4. Confirm the live-count-drift handling (re-measure at execution, report actuals in post-impl) is the right approach vs. pinning a fixed count.
5. Issue GO if findings 1-4 hold; or NO-GO with specific revision asks.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
