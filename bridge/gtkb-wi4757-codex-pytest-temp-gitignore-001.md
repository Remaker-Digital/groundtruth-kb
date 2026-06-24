NEW

# gtkb-wi4757-codex-pytest-temp-gitignore - Ignore locked Codex pytest temp roots

bridge_kind: prime_proposal
Document: gtkb-wi4757-codex-pytest-temp-gitignore
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-24T01:04:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef21d-a27e-7473-9939-21f715631a90
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder; Windows PowerShell; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4757

target_paths: [".gitignore", "platform_tests/scripts/test_gitignore_codex_pytest_tmp.py"]

implementation_scope: scaffold_update, test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4757 tracks repeated `git status` warnings caused by root-level Codex pytest/test temp directories that Git tries to descend into even when they are locked or ACL-restricted. Live `git status --short` still emits permission-denied warnings for `.codex-pytest-tmp/...`, `.codex-pytest-tmp-*`, `.codex-test-tmp-*`, and `.codex_pytest_tmp/` roots. Representative `git check-ignore -v` probes for those families currently return no matching ignore rule, and `.gitignore` covers generic pytest temp directories but not the Codex-specific root temp families.

This proposal repairs the noise by adding root-anchored ignore coverage for the known Codex temp root families and by adding a focused regression test that proves representative paths are ignored. It intentionally does not delete, chmod, move, or clean live temp directories; preserving live test artifacts is part of the work item scope and avoids touching runtime byproducts owned by concurrent or prior sessions.

## Current Evidence

- `git status --short 2>&1 | Select-String -Pattern ".codex-pytest-tmp|.codex-test-tmp|.codex_pytest_tmp|warning"` reports many permission-denied warnings for the Codex temp directory families and lists additional untracked `.codex-pytest-tmp-*` roots.
- `git check-ignore -v .codex-pytest-tmp/auth-review-focused-20260622T0529/sentinel.txt` returned no match.
- `git check-ignore -v .codex-test-tmp-runtime/sentinel.txt` returned no match.
- `git check-ignore -v .codex_pytest_tmp/sentinel.txt` returned no match.
- `rg -n "codex-pytest|codex-test-tmp|codex_pytest_tmp|pytest-tmp|pytest_tmp|check-ignore" .gitignore platform_tests scripts .codex .claude` found existing generic pytest temp rules in `.gitignore`, but no Codex-specific root temp coverage.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH provides bounded owner authorization for this snapshot-member WI but does not bypass bridge GO, target-path scoping, implementation-start authorization, or verification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal must use the file bridge, dispatcher/TAFE state, numbered bridge files, and a later implementation-start packet before protected `.gitignore` or test mutations.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites concrete governing specifications and maps them to verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the machine-readable `Project Authorization`, `Project`, and `Work Item` lines bind the proposal to the authorized project/WI scope.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must carry forward these specifications and show executed spec-derived tests.
- `GOV-STANDING-BACKLOG-001` - WI-4757 is the MemBase work item being advanced; no new WIs are added and newer May29 Hygiene project members outside the authorization snapshot remain out of scope.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` - all proposed paths and test fixtures are in-root under `E:\GT-KB`; no outside temp location is required for verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the diagnosis, risk choice, regression coverage, and verification plan are preserved in durable bridge/test artifacts instead of session memory.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the affected temp families are Codex-harness runtime byproducts; the repair keeps Codex local runtime artifacts out of version-control scans without weakening tracked Codex hook/skill surfaces.

## Prior Deliberations

- `DELIB-20265586` - owner AUQ decision authorizing the drive-to-conclusion project sweep with snapshot-bound project authorization. This proposal cites the specific PAUTH created from that decision and does not include newer May29 Hygiene project WIs outside the snapshot.
- `DELIB-20261295` / `bridge/gtkb-pytest-basetemp-session-isolation-002.md` - prior GO for pytest temp isolation explicitly avoided runtime temp cleanup outside target paths. WI-4757 follows the same safety posture by preserving live temp artifacts and repairing Git traversal behavior through ignore coverage.
- `DELIB-20265741` / `bridge/gtkb-wi4701-codex-adapter-crlf-whitespace-fix-008.md` - prior verification NO-GO identified untracked pytest temp byproducts as workspace noise and required accurate git-state evidence. WI-4757 directly addresses the related Git scan noise for Codex temp roots.
- `DELIB-20260616-MAY29-HYGIENE-WI-4394-AUTHORIZE` and `DELIB-20265047` - adjacent May29 Hygiene git-warning work on Windows configuration warning noise. That thread fixed a different warning class and does not conflict with this root `.gitignore` repair.
- DA searches run before proposing:
  - `gt deliberations search "WI-4757 git status permission denied Codex pytest temp gitignore" --limit 5 --json`
  - `gt deliberations search "Codex pytest tmp gitignore check-ignore permission denied" --limit 5 --json`

## Owner Decisions / Input

No new owner decision is required for this proposal. Authority derives from `DELIB-20265586` and `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23`; the PAUTH includes `WI-4757`, allows `test_addition` and `scaffold_update`, and does not authorize any work item added to the project after the snapshot.

## Requirement Sufficiency

Existing requirements sufficient - WI-4757 identifies the repeated Git warning defect and explicitly scopes diagnosis plus a guarded cleanup/ignore strategy that preserves live test artifacts. The current evidence shows ignore coverage is missing, and the linked governance specifications are sufficient to implement the focused `.gitignore` plus regression-test repair.

## Proposed Implementation

1. Add root-anchored `.gitignore` patterns for the known Codex temp families:

   ```gitignore
   /.codex-pytest-tmp*/
   /.codex-test-tmp*/
   /.codex_pytest_tmp/
   ```

   The patterns are root-anchored so they target session/runtime temp roots without changing nested source or fixture semantics.
2. Add `platform_tests/scripts/test_gitignore_codex_pytest_tmp.py` using `git check-ignore -v` to assert representative paths under these families are ignored:
   - `.codex-pytest-tmp/auth-review-focused-20260622T0529/sentinel.txt`
   - `.codex-pytest-tmp-wi4768-dispatch/sentinel.txt`
   - `.codex-test-tmp-runtime/sentinel.txt`
   - `.codex-test-tmp-self-init/sentinel.txt`
   - `.codex_pytest_tmp/sentinel.txt`
3. Optionally include a no-tracked-artifacts assertion using `git ls-files` to fail if any tracked path begins with `.codex-pytest-tmp`, `.codex-test-tmp`, or `.codex_pytest_tmp`.
4. Do not delete, chmod, move, or inspect the contents of the locked live temp directories. The repair is an ignore strategy plus regression coverage, not cleanup.

## Spec-Derived Verification Plan

| Governing specification or artifact | Verification command / check | Expected result |
| --- | --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4757-codex-pytest-temp-gitignore` after GO | Packet is issued for `WI-4757` and target paths are limited to `.gitignore` and the focused test file. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge threads --wi WI-4757`; implementation report cites GO + packet evidence | Numbered bridge chain shows proposal/GO/report state and no direct protected mutation before GO. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4757-codex-pytest-temp-gitignore` | `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_gitignore_codex_pytest_tmp.py -q --tb=short` | Focused regression test passes and proves representative Codex temp roots are ignored. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4757-codex-pytest-temp-gitignore` | Exit 0 with zero blocking gaps. |
| Python code-quality gates for the new test | `python -m ruff check platform_tests/scripts/test_gitignore_codex_pytest_tmp.py` and `python -m ruff format --check platform_tests/scripts/test_gitignore_codex_pytest_tmp.py` | Both pass. |
| WI-4757 user-visible symptom | `git status --short 2>&1 | Select-String -Pattern ".codex-pytest-tmp|.codex-test-tmp|.codex_pytest_tmp|warning"` | No permission-denied warning lines for the ignored Codex temp families. |
| Guarded preservation of live artifacts | Review diff and command evidence | No deletion/chmod/move of `.codex-*tmp` or `.codex_pytest_tmp` runtime directories occurs. |

## Pre-Filing Preflights

Prime Builder will run the mandatory preflights against this completed draft before helper-mediated live filing:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4757-codex-pytest-temp-gitignore-001.md
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4757-codex-pytest-temp-gitignore-001.md
```

Expected results: applicability preflight passes with no missing required/advisory specs; clause preflight exits 0 with zero blocking gaps.

## Acceptance Criteria

- `.gitignore` contains root-anchored ignore patterns for `.codex-pytest-tmp*`, `.codex-test-tmp*`, and `.codex_pytest_tmp/`.
- Focused regression coverage proves representative paths in each family are ignored by Git.
- The implementation does not delete, chmod, move, or depend on reading locked temp directory contents.
- `git status --short` no longer emits permission-denied warnings for those Codex temp families.
- Focused pytest, ruff lint, and ruff format checks pass for the new test file.

## Risk / Rollback

Risk is low and localized. The main risk is hiding a deliberately created root directory whose name begins with `.codex-pytest-tmp` or `.codex-test-tmp`; those names are already runtime/test-harness conventions and the patterns are root-anchored to avoid broad nested effects. Rollback is a single commit revert of `.gitignore` and the focused test file. Live temp artifacts remain untouched either way.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4757-codex-pytest-temp-gitignore`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` - the durable change repairs a reproducible `git status` warning/noise defect by adding ignore coverage and regression tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
