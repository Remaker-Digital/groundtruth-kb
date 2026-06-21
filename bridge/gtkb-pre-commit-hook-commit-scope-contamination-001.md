NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Pre-commit hook auto-stages files outside the verified staged set (commit-scope contamination)

bridge_kind: prime_proposal
Document: gtkb-pre-commit-hook-commit-scope-contamination
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3497

target_paths: ["scripts/guardrails/check_assertion_ratchet.py", "platform_tests/scripts/test_check_assertion_ratchet.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The guardrails pre-commit check `scripts/guardrails/check_assertion_ratchet.py` mutates and **auto-stages** `scripts/guardrails/assertion-baseline.json` via `git add` (lines 101-108) during a commit whenever any staged `tests/**/test_*.py` file's assertion count INCREASED. Because this `git add` runs inside the pre-commit phase, it injects the baseline file into the in-progress commit's staged set even though the committer never staged it. The result is commit-scope contamination: a scoped commit (for example, a Loyal Opposition `VERIFIED` finalization that deliberately stages only its declared verified path set) silently acquires an extra unrelated file. This contradicts the scoped-commit discipline in `.claude/rules/file-bridge-protocol.md` and the exact-staged-set guarantee enforced by the VERIFIED finalization helper.

## Defect / Reproduction

The active hooks chain is `core.hooksPath = .githooks` (set by `.githooks/setup-hooks.sh`); the guardrails chain at `scripts/guardrails/pre-commit` is the secondary pre-commit hook (its header documents "Install: copy to .git/hooks/pre-commit or symlink") and invokes the ratchet at line 35. The ratchet's auto-update branch is the defect:

```text
# scripts/guardrails/check_assertion_ratchet.py:101-108
        with open(BASELINE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        # Stage the updated baseline
        subprocess.run(
            ["git", "add", str(BASELINE_PATH)],
            cwd=PROJECT_ROOT,
        )
```

Reproduction (deterministic, in a throwaway temp git repo so live state is untouched):
1. Initialize a temp repo containing a `scripts/guardrails/assertion-baseline.json` whose `baselines` map records `tests/foo/test_a.py: 1` and a `tests/foo/test_a.py` with a single assertion; create one initial commit.
2. Edit `tests/foo/test_a.py` to add a second assertion and `git add` ONLY that test file.
3. Invoke `check_assertion_ratchet.main()` with the temp repo as `PROJECT_ROOT`.
4. Observe: the baseline file is rewritten AND `git diff --cached --name-only` now lists `scripts/guardrails/assertion-baseline.json` in addition to the one test file the committer staged.

Expected: the ratchet may rewrite the baseline on the working tree (or, preferably, leave the working tree untouched and only report the needed increase), but it MUST NOT add the baseline to the staged set; the staged set after the check must equal the staged set before the check.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/guardrails/check_assertion_ratchet.py`, `platform_tests/scripts/test_check_assertion_ratchet.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge `VERIFIED` is a commit-finalization outcome whose committed scope must equal the declared verified path set; a pre-commit hook that auto-stages an extra file corrupts that authoritative scope, so removing the auto-stage defends the bridge's scoped-commit contract.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable artifacts (commits) must accurately reflect the change they represent; silently bundling an unrelated baseline file degrades the artifact's traceability, which this fix prevents.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every governing spec for the change (mandatory linkage); satisfied by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives each test from a cited spec clause (mandatory spec-to-test mapping).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries the Project Authorization / Project / Work Item linkage lines (mandatory); satisfied in the header.
- `SPEC-AUQ-POLICY-ENGINE-001` - the change adds no owner-decision surface and triggers no AUQ policy class; this defect fix removes behavior rather than adding any policy-gated path, so no AUQ-policy obligation is introduced (linkage retained because the applicability matrix flags hook-touching changes for AUQ-policy review and this proposal explicitly clears that review).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to a GT-KB platform guardrail script and platform tests under `scripts/` and `platform_tests/`; no application/adopter surface is touched and the in-root placement boundary is respected.
- `GOV-STANDING-BACKLOG-001` - WI-3497 is a standing-backlog work item (P2, origin=defect) under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the touched surface is a git pre-commit guardrail, which is harness-agnostic (it runs at `git commit` regardless of which AI harness produced the staged change); the fix preserves that harness parity by removing only the staging side effect, leaving the ratchet's pass/fail gate identical for both harnesses.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - commit scope is an artifact-backed boundary; the fix keeps commit composition under deliberate committer control rather than mutated by a side-effecting check.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - regenerating the assertion baseline is a lifecycle action that should be a deliberate, separately-committed step, not an implicit pre-commit side effect; the fix aligns the trigger boundary accordingly.

## Prior Deliberations

- `DELIB-2394` - Loyal Opposition Review, gtkb-commit-scope-bundling-detection-001-prop - prior LO review of commit-scope bundling detection; the same class of concern (extra paths leaking into a commit's scope) that this defect causes at the auto-stage boundary.
- `DELIB-20264744` - Loyal Opposition Review, Ruff Format Pre-File Gate - prior decision establishing that pre-commit/pre-file gates are checks, not auto-stagers; supports the fix's posture that a guardrail must not silently restage.
- `DELIB-20265419` - Verdict - sibling verification-verdict context for the scoped-commit / staged-set discipline this fix protects.
- `DELIB-20261599` - Verification Verdict, gt generate-approval-packet CLI - prior precedent that artifact-generating helpers stage only their declared output set (e.g., the packet helper's explicit `--stage` opt-in), reinforcing that implicit staging is the defect.
- `DELIB-20265338` - Applicability Preflight - the preflight context that gates this proposal's spec linkage.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (standing authorization, backed by `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-3497 is origin=defect, single-concern, introduces no new public API/CLI/behavior beyond removing the defect, and is bounded to 1 source file + 1 test (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active PROJECT-GTKB-RELIABILITY-FIXES membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work items; WI-3497 (P2 defect) is in that authorized batch.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing reliability fast-lane direction (the basis for PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING) authorizing small, single-concern defect fixes to proceed under the fast lane.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` and the scoped-commit discipline in `.claude/rules/file-bridge-protocol.md` already require a commit's scope to equal its deliberately-staged path set; this fix enforces that contract by removing the pre-commit auto-stage side effect. No new or revised requirement/specification is introduced.

## Proposed Scope

IP-1. In `scripts/guardrails/check_assertion_ratchet.py`, remove the `subprocess.run(["git", "add", str(BASELINE_PATH)], ...)` call in the `if updates:` branch (lines 104-108) so the ratchet never adds the regenerated baseline to the staged set. The baseline rewrite on the working tree may remain (it is regenerable, idempotent state), but the file is left UNSTAGED. Replace the staging side effect with an informational message instructing the developer to stage the baseline deliberately and amend/recommit if they intend the increase to be part of this commit (e.g., "Assertion baseline updated on disk (N file(s) increased) but NOT staged; stage scripts/guardrails/assertion-baseline.json deliberately if you want it in this commit."). The check continues to return exit 0 in this branch (no behavior change to the pass/fail gate).
   - The decrease-detection path (violations -> exit 1) is unchanged; the ratchet still blocks assertion weakening.
   - No new import, no new CLI flag, and no change to `get_staged_test_files()` or the counting logic.

IP-2. Add a regression test module `platform_tests/scripts/test_check_assertion_ratchet.py` (see verification plan). The test imports `scripts/guardrails/check_assertion_ratchet` and exercises it against an isolated temporary git repository (created with `git init` in a `tmp_path`), so the live `E:\GT-KB` staging area and baseline are never touched.

This is the defect-removal path. The WI's implied alternative (teaching the committer-facing tooling to model an "expected baseline regeneration" so the file can be auto-staged safely) is a behavior/contract change requiring a new requirement and is explicitly out of scope for this fast-lane defect fix.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (committed scope equals the deliberately-staged set) | `test_ratchet_does_not_stage_baseline_on_increase` | After running the ratchet against a temp repo where a staged test file's assertion count increased, `git diff --cached --name-only` equals the pre-check staged set (the baseline path is NOT added). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (no contamination of an unrelated scoped commit) | `test_ratchet_leaves_unrelated_staged_set_unchanged` | When the staged set contains a single non-baseline test file with an increased count, the staged set after the check is byte-identical (no extra paths), confirming no commit-scope contamination. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (no behavior regression in the gate) | `test_ratchet_still_blocks_assertion_decrease` | A staged test file whose assertion count DECREASED still causes the ratchet to return exit 1 (the weakening-prevention behavior is preserved). |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (baseline regeneration is a deliberate, non-side-effecting step) | `test_ratchet_increase_returns_zero_and_baseline_unstaged` | An increased count returns exit 0 and leaves the regenerated baseline on disk but unstaged, so the lifecycle action is surfaced to the committer rather than silently bundled. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_check_assertion_ratchet.py -q --tb=short`
- `python -m ruff check scripts/guardrails/check_assertion_ratchet.py platform_tests/scripts/test_check_assertion_ratchet.py`
- `python -m ruff format --check scripts/guardrails/check_assertion_ratchet.py platform_tests/scripts/test_check_assertion_ratchet.py`

## Acceptance Criteria

1. `check_assertion_ratchet.py` never invokes `git add` (no `subprocess.run([..., "add", ...])`) in any branch; the staged set after the check equals the staged set before the check for all inputs.
2. The ratchet's decrease-detection gate is unchanged: a decreased assertion count still returns exit 1 with the existing failure message.
3. An increased assertion count still returns exit 0; the baseline is regenerated on disk but left unstaged, with an informational message telling the committer to stage it deliberately if desired.
4. The four derived tests pass; `ruff check` and `ruff format --check` are clean on both changed files.

## Risks / Rollback

- Risk: developers who relied on the implicit auto-stage now have to stage the regenerated baseline manually, so a baseline increase could land one commit later than before. Mitigation: the new informational message names the exact file to stage; this is the correct, deliberate-control posture and matches the precedent (`DELIB-20261599`) that artifact generators stage only their declared output.
- Risk: a future caller assumed the ratchet stages the baseline as a side effect. Mitigation: the only invoker is `scripts/guardrails/pre-commit` (line 35), which does not depend on the file being staged; the regression suite locks the no-stage contract.
- Rollback: revert the single edited branch in `check_assertion_ratchet.py`; the change is the removal of one `subprocess.run` call plus a print and an added test module, fully reversible with no migration and no data change.

## Files Expected To Change

- `scripts/guardrails/check_assertion_ratchet.py`
- `platform_tests/scripts/test_check_assertion_ratchet.py`

## Recommended Commit Type

`fix`
