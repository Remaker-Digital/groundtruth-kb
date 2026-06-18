NEW

# Defect-Fix Proposal - Doctor false-positive: _check_active_legacy_root_references flags the claude-playground detection-pattern definition in hygiene-sweep-patterns.toml as a live legacy-root dependency

bridge_kind: prime_proposal
Document: gtkb-doctor-legacy-root-pattern-catalog-false-positive
Version: 001
Date: 2026-06-17 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8851dbf6-a9fe-4ab9-a49f-d13f405e8711
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; Prime Builder (session-stated ::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4627

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_legacy_root.py"]

Reliability fast-lane (GOV-RELIABILITY-FAST-LANE-001) defect-fix: reproduce, correct, and verify a single doctor-check false positive.

## Claim

The doctor check `_check_active_legacy_root_references` emits a `[FAIL]` for `config/governance/hygiene-sweep-patterns.toml` lines 200/213/214, but those lines are the `[[patterns]] id="claude-playground"` DETECTION-pattern definition — the catalog that tells `gt hygiene sweep` which retired-archive-root strings to search for. They are NOT a live dependency on the retired archive root. The check should treat the governed hygiene-sweep pattern catalog the same way it already exempts its own detector scripts, while PRESERVING the hard-fail for genuine live references (per the owner hard-fail decision DELIB-20260602).

## Defect / Reproduction

- Reproduce: `python -m groundtruth_kb project doctor` → `[FAIL] Active control surface references retired <archive-root>: config/governance/hygiene-sweep-patterns.toml:200, :213, :214`.
- Root cause: `_check_active_legacy_root_references` (doctor.py:1440) scans `config/**/*` (glob at doctor.py:197) and its allow-classifier `_legacy_root_reference_is_allowed` (doctor.py:1501-1508) only exempts three pattern-script *names* (`_LEGACY_ROOT_PATTERN_SCRIPT_NAMES`, doctor.py:214) OR a +/-2-line context window matching `_LEGACY_ROOT_ALLOWED_CONTEXT_RE` (doctor.py:221). Lines 200/213/214 escape both: line 200 ("legacy root archive path ...") does not match the regex's `legacy[-_]root` / `archive[- ]only` alternatives (space vs hyphen), and lines 213/214 (the `//e/` `//E/` alias forms) sit beyond the +/-2-line reach of the `content_patterns = [` array header (line 210), so the context window does not include the word "pattern".
- The sibling mechanism already handles this correctly: the hygiene sweep self-excludes its own catalog file via `exclusion_globs` (hygiene-sweep-patterns.toml:237). The doctor check lacks the equivalent self-exclusion, so the two mechanisms diverge and the doctor double-counts the detector definition.
- Provenance: the `claude-playground` pattern block was added in commit 258f9c504 (2026-06-11) to DETECT legacy-root drift; it is a detector definition, not a live dependency. It is on current HEAD; the working tree is clean for this file. This is a committed, current false positive (confirmed via live doctor run 2026-06-17).

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `groundtruth-kb/tests/test_doctor_legacy_root.py`.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - Governs this proposal's lighter path: WI-4627 is origin=defect, introduces no new API/CLI/behavior beyond removing the false positive, requires no new/revised requirement, and is small + single-concern (doctor.py + one test). Covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` through active project membership.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites every relevant governing specification in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The verification plan maps each acceptance criterion to an executed test (new regression test in `test_doctor_legacy_root.py`) plus the live doctor run.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Satisfied by the `Project Authorization` / `Project` / `Work Item` header lines (PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING / PROJECT-GTKB-RELIABILITY-FIXES / WI-4627).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - This change flows through the bridge protocol (proposal -> GO -> implement -> report -> VERIFIED) under bridge authority.
- `GOV-STANDING-BACKLOG-001` - WI-4627 is a standing-backlog work item captured per the strategic self-improvement directive; this proposal implements it.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The fix is delivered as durable artifacts (work item, proposal, test, report), not transient conversation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Same artifact-oriented delivery principle applied to the fix.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Touching the doctor surface triggered the standard lifecycle (WI + test + proposal); satisfied here.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The legacy-root check enforces the platform root boundary; this fix PRESERVES that enforcement for genuine out-of-root live references and only exempts a detector-definition file, so the isolation boundary is not weakened.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner authorization derives from DECISION-1272 (AUQ-class owner directive) plus the fast-lane standing authorization; this change does not alter AUQ policy or its engine.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - No hook-surface change; the doctor check is harness-agnostic. Cited for completeness; Codex/Claude hook parity is unaffected.

## Prior Deliberations

<!-- Reviewed and pruned from helper pre-population. -->

- `DELIB-20260602-GLOSSARY-CLI-SCAN-LEGACY-ROOT-HARD-FAIL` - Owner selected HARD-FAIL doctor behavior for active artifacts treating the legacy root as live. This fix PRESERVES that hard-fail for genuine live references; it only exempts the detector-definition catalog (not a live dependency), so the owner's hard-fail intent is unchanged. This is the constraint the fix must not violate.
- `DELIB-20264372` - Loyal Opposition Review - No-Index Startup And Control-Surface Cleanout (GO). Recent control-surface cleanout work adjacent to this doctor check.
- `DELIB-20263459` - Hygiene Sweep Scope Regression 2026-06-12. Concerns the hygiene-sweep catalog that this proposal stops the doctor from double-counting.
- `DELIB-20263489` - Loyal Opposition Hygiene Assessment - Advisory Report (2026-06-15). The hygiene assessment context in which the legacy-root FAIL was surfaced.

## Owner Decisions / Input

- `DECISION-1272` (S445 AskUserQuestion, owner answer "Yes") authorized fixing the trivial legacy-root reference. Recorded in `memory/pending-owner-decisions.md` (resolved 2026-06-17).
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active, "Reliability fast-lane standing authorization") covers implementation of fast-lane-eligible defect WIs in `PROJECT-GTKB-RELIABILITY-FIXES` through active project membership, per `GOV-RELIABILITY-FAST-LANE-001` — no per-fix owner-approval packet required.
- No further owner decision is required to implement this fast-lane fix.

## Requirement Sufficiency

Existing requirements sufficient. The legacy-root hard-fail behavior is already specified by the owner decision `DELIB-20260602` and `.claude/rules/project-root-boundary.md`. This change corrects a detector false-positive to align the doctor check with that existing intent (and with the hygiene sweep's existing self-exclusion). It introduces no new or revised requirement; the verification proves the existing hard-fail behavior is preserved for genuine live references.

## Proposed Scope

IP-1 - `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (Option A, narrowest):
- Add a module-level constant `_LEGACY_ROOT_PATTERN_FILE_NAMES = frozenset({"hygiene-sweep-patterns.toml"})` adjacent to `_LEGACY_ROOT_PATTERN_SCRIPT_NAMES` (~doctor.py:214).
- In `_legacy_root_reference_is_allowed` (~doctor.py:1501-1508), add an early `return True` when `relative_path.name in _LEGACY_ROOT_PATTERN_FILE_NAMES`. This exempts the governed hygiene-sweep pattern catalog (a detector definition) exactly as the sweep already self-excludes it (hygiene-sweep-patterns.toml:237).
- No other behavior changes: genuine live references (e.g., a live `settings.local` path, a live script dependency) still hard-FAIL.

IP-2 - `groundtruth-kb/tests/test_doctor_legacy_root.py`:
- Add a regression test that writes a tmp `config/governance/hygiene-sweep-patterns.toml` containing the `[[patterns]] id="claude-playground"` block (description line plus the `content_patterns` array with the `//e` / `//E` alias forms) and asserts `_check_active_legacy_root_references(tmp).status == "pass"`.
- Preserve the existing FAIL-case tests unchanged (live settings.local path, live script use) to prove the hard-fail is preserved.

Rejected alternative: Option B (broaden `_LEGACY_ROOT_ALLOWED_CONTEXT_RE`) — wider regression surface; a broader regex could exempt a genuine live reference whose surrounding lines happen to contain "archive"/"alias". Option A is narrower and lower-risk and mirrors the sweep's existing self-exclusion.

## Specification-Derived Verification Plan

| Spec / Acceptance criterion | Derived test / command | Expected result |
|---|---|---|
| `GOV-RELIABILITY-FAST-LANE-001` eligibility | Manual: WI-4627 origin=defect, 2 files, no new spec, single-concern | Eligible |
| Catalog exempted (fix works) | `python -m pytest groundtruth-kb/tests/test_doctor_legacy_root.py -q` (new `test_hygiene_sweep_pattern_catalog_is_allowed`) | PASS — `_check_active_legacy_root_references(...).status == "pass"` for the catalog |
| Hard-fail preserved (`DELIB-20260602`) | Same pytest run, existing FAIL-case tests (live settings.local; live script use) | Those tests still observe FAIL for genuine live refs |
| Whole-check flips | `python -m groundtruth_kb project doctor` | Active legacy-root references check -> PASS; no other surface newly flagged |
| Sweep still functions | `gt hygiene sweep` (or the sweep module) | `claude-playground` pattern still self-excludes its own file and would still catch a planted live reference elsewhere |
| Lint / format | `ruff check <changed.py>` and `ruff format --check <changed.py>` | Clean (both gates) |

## Acceptance Criteria

1. `_check_active_legacy_root_references` returns PASS for the `claude-playground` pattern catalog in `hygiene-sweep-patterns.toml`.
2. Existing FAIL-case tests (genuine live references) still FAIL — the `DELIB-20260602` hard-fail is preserved.
3. `python -m groundtruth_kb project doctor` legacy-root check flips FAIL -> PASS with no new false negatives on other surfaces.
4. `gt hygiene sweep` `claude-playground` pattern remains functional.
5. `ruff check` and `ruff format --check` are clean on both changed files.

## Risks / Rollback

- Risk: LOW. Scope is a single allow-classifier addition plus one regression test. Option A whitelists exactly one governed config file (the detector catalog) that already self-excludes from its sibling sweep; it cannot mask a live reference because that file's only purpose is to DEFINE detection patterns.
- The owner hard-fail decision (`DELIB-20260602`) is preserved for all genuine live references; this is asserted by keeping the existing FAIL-case tests green-as-FAIL.
- Rollback: `git revert` / restore the two changed files. No data, schema, or runtime-state migration; the only runtime effect is turning a doctor FAIL into PASS.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor_legacy_root.py`

## Recommended Commit Type

`fix`
