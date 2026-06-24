NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef218-0e11-7133-939d-e1d62c0025f0
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop Prime Builder resumed LO advisory routing project-retirement session
author_metadata_source: explicit Codex runtime metadata passed to bridge-propose helper

bridge_kind: prime_proposal
Document: gtkb-docs-quality-remediation-remaining-scope-wi3306
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-24 UTC
Project Authorization: PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23
Project Authorization Owner Decision: DELIB-20265586
Project: PROJECT-GTKB-LO-ADVISORY-ROUTING
Work Item: WI-3306
Source Advisory: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-07-06-39-GTKB-DOCUMENTATION-QUALITY-REVIEW.md
Source Advisory Deliberation: DELIB-1464
Prior Umbrella: bridge/gtkb-docs-quality-remediation-004.md
Prior Covered Slice: bridge/gtkb-docs-quality-remediation-slice-1-root-readme-rewrite-006.md
target_paths: ["bridge/gtkb-docs-quality-remediation-remaining-scope-wi3306-001.md", "README.md", "groundtruth-kb/README.md", "groundtruth-kb/mkdocs.yml", "groundtruth-kb/docs/reference/cli.md", "groundtruth-kb/docs/day-in-the-life.md", "groundtruth-kb/docs/method/12-file-bridge-automation.md", "groundtruth-kb/docs/known-limitations.md", "groundtruth-kb/docs/groundtruth-kb-executive-overview.md", "groundtruth-kb/docs/architecture/product-split.md", "groundtruth-kb/docs/reports/agent-red-classification.md", "groundtruth-kb/docs/reference/templates.md", "groundtruth-kb/templates/README.md", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/scripts/check_docs_cli_coverage.py", "groundtruth-kb/tests/test_docs_cli_coverage.py"]
allowed_mutation_classes: ["source", "test_addition", "cli_extension", "scaffold_update"]
implementation_scope: remaining_docs_quality_remediation_slice_for_WI_3306
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false
owner_input_required: false

---

# Prime Builder Proposal - WI-3306 Remaining Documentation Quality Remediation

## Summary

Prime Builder classifies WI-3306 as **`adopt` with remaining implementation scope**.

The source advisory (`DELIB-1464`) was partly routed already. The docs-quality umbrella reached `VERIFIED` at `bridge/gtkb-docs-quality-remediation-004.md`; the root README identity slice reached `VERIFIED` at `bridge/gtkb-docs-quality-remediation-slice-1-root-readme-rewrite-006.md`; and the later Start Here adopter rewrite reached `VERIFIED` at `bridge/gtkb-start-here-adopter-rewrite-implementation-010.md`.

Those prior threads close the original root README identity mismatch and part of the beginner-onboarding gap. They do not close the current docs-quality contract. A live probe on 2026-06-24 shows `groundtruth-kb/scripts/check_docs_cli_coverage.py` still exits 1 with 117 documentation issues, including missing `gt` command coverage, `gt project init` snippets without `PROJECT_NAME`, and an outdated ChromaDB install message in `src/groundtruth_kb/cli.py`. Current docs also still contain mixed `0.6.0`, `0.6.1`, `0.7.0-rc1`, and retired-poller language in public docs.

This proposal requests GO for one implementation slice that repairs the current objective docs-quality gates while keeping the already-verified root README slice out of scope except for narrow version/status corrections.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v2 (verified) - bridge-mediated implementation work; Prime Builder will not mutate source, docs, tests, scripts, or CLI files until a Loyal Opposition `GO` and implementation-start packet exist.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified) - this proposal cites the relevant bridge, project, advisory, source, test, lifecycle, and root-boundary requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified) - the implementation report must map every repair class to a concrete check and run the repo-native docs/test/lint gates.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified) - this filing carries Project Authorization, Project, and Work Item metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 (specified) - the PAUTH covers WI-3306 and allows source, test addition, CLI extension, and scaffold update mutation classes.
- `DCL-ADVISORY-ROUTING-001`, `.claude/rules/peer-solution-advisory-loop.md`, and `SPEC-ADVISORY-REPORT-TEMPLATE-001` - WI-3306 is an LO advisory routing item, and the source report supplies findings, evidence, impact, and proposed actions.
- `GOV-STANDING-BACKLOG-001` - this proposal does not add new WIs or mutate project membership.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the advisory, bridge chain, docs-check script, CLI reference, tests, and report remain durable project artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` - all target paths are under `E:\GT-KB`; any Agent Red or `E:\Claude-Playground` references in public docs must be archival/contextual, not live dependencies.
- `.claude/rules/file-bridge-protocol.md` - this follows the numbered bridge chain and waits for independent Loyal Opposition review.

## Project Authorization

- Authorization: `PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23`.
- Owner decision: `DELIB-20265586`.
- Project: `PROJECT-GTKB-LO-ADVISORY-ROUTING`.
- Work item: `WI-3306`.
- Snapshot scope: WI-3306 is in the PAUTH's included work item IDs.
- Allowed mutation classes used by this proposal: `source`, `test_addition`, `cli_extension`, `scaffold_update`.
- Mutations explicitly out of scope: new project work items, formal GOV/SPEC/ADR/DCL/PB/REQ mutations, credentials, deployment, CI release authorization, root-boundary exceptions, and any reliance on `E:\Claude-Playground` as a live dependency.

## Owner Decisions / Input

- `DELIB-20265586`: Owner authorized bounded implementation for the project's 19-item snapshot while preserving the ACID-invariant for future project additions.
- Current transcript direction: the owner directed this WI class to be treated as needing more implementation scope. This proposal therefore does not file a monitor-only or covered-only disposition.
- Current transcript constraints applied as implementation shape, not as new governance artifacts: keep examples copyable, keep operational examples loopback/local-only unless explicitly external, make package CLI surfaces primary, and prefer combined health/status operations to carry explicit badges when GT-KB and application health are shown together.

No new owner decision is required because the implementation scope is derived from `DELIB-1464`, verified prior bridge coverage, the live red docs checker, and the existing PAUTH.

## Requirement Sufficiency

Existing requirements are sufficient. The implementation target is the next objective repair slice for already-recorded documentation-quality requirements:

- Make docs drift checks pass again.
- Keep beginner commands copy-paste executable or explicitly mark them conceptual.
- Make version/release-state language coherent with `groundtruth_kb.__version__`.
- Replace current-looking retired OS-poller/smart-poller guidance with current cross-harness trigger and manual-scan guidance.
- Keep critical docs discoverable in MkDocs navigation.
- Prevent future drift through focused tests around the docs-check script and CLI reference coverage.

## Prior Deliberations

- `DELIB-1464` - GT-KB Documentation Quality Review source advisory.
- `bridge/gtkb-docs-quality-remediation-001.md` through `bridge/gtkb-docs-quality-remediation-004.md` - prior umbrella scoping, latest `VERIFIED`.
- `bridge/gtkb-docs-quality-remediation-slice-1-root-readme-rewrite-001.md` through `bridge/gtkb-docs-quality-remediation-slice-1-root-readme-rewrite-006.md` - root README slice, latest `VERIFIED`.
- `bridge/gtkb-start-here-adopter-rewrite-implementation-010.md` - verified adopter-facing Start Here rewrite, relevant partial coverage for beginner onboarding and MkDocs navigation.
- `DELIB-20265586` - PAUTH owner decision for snapshot-bound project implementation authority.

## Current Evidence Snapshot

Commands run from the live checkout on 2026-06-24:

- `gt bridge threads --wi WI-3306 --json` returned `match_count: 0`; WI-3306 has no WI-linked bridge thread yet.
- `show_thread_bridge.py gtkb-docs-quality-remediation --format json` returned a drift-free thread with `VERIFIED` slice 0 and root README coverage.
- `show_thread_bridge.py gtkb-docs-quality-remediation-slice-1-root-readme-rewrite --format json` returned latest `VERIFIED`.
- `show_thread_bridge.py gtkb-start-here-adopter-rewrite --format json` returned latest `VERIFIED`.
- In `E:\GT-KB\groundtruth-kb`, `.venv\Scripts\python.exe scripts\check_docs_cli_coverage.py` exited 1 with 117 documentation issues.
- In `E:\GT-KB\groundtruth-kb`, `.venv\Scripts\python.exe -m mkdocs build --strict --site-dir _site_bridge_wi3306_probe` could not run because the package-local venv has no `mkdocs` module installed.
- `groundtruth_kb.__version__` is `0.7.0rc1`.
- `rg -n "0\.6\.0|0\.6\.1|0\.7\.0rc1|0\.7\.0-rc1|OS poller|OS scheduler|smart poller|Smart Poller|retired|Retired" README.md docs mkdocs.yml` still finds stale or mixed version/retired-automation language in public docs.
- `.markdownlint.json` is absent at repo root and package root; markdownlint setup remains optional unless implemented without broad formatting churn.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Use only public docs, CLI help, and synthetic test fixtures; do not add credential-shaped strings. | Bridge helper credential scan and changed-file review. | |
| CQ-PATHS-001 | Yes | Keep all edits inside the declared in-root target paths and avoid `E:\Claude-Playground` as a live dependency. | Implementation-start packet plus final `git diff --name-only` scope review. | |
| CQ-COMPLEXITY-001 | Yes | Keep checker and CLI-reference changes small; prefer deterministic command enumeration over hand-maintained special cases. | Focused tests around docs-check command enumeration and source review. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing version and CLI command discovery sources; introduce named constants only when repeated literals would remain. | Source review plus focused tests for version and command coverage behavior. | |
| CQ-SECURITY-001 | Yes | Do not loosen docs drift gates broadly; fail closed for malformed command snippets and stale install guidance. | Negative tests for bad snippets and passing docs-check command. | |
| CQ-DOCS-001 | Yes | Repair public docs and template snippets while preserving historical context as archival where needed. | `scripts/check_docs_cli_coverage.py`, targeted `rg`, and docs build evidence. | |
| CQ-TESTS-001 | Yes | Add focused tests for docs-check and CLI reference coverage, or cite an equivalent targeted test file in the report. | Targeted pytest command listed in the implementation report. | |
| CQ-LOGGING-001 | N/A | | | No runtime logging or telemetry behavior is in scope. |
| CQ-VERIFICATION-001 | Yes | Run docs-check, targeted pytest, Ruff check, Ruff format check, bridge preflights, and docs build or exact docs-dependency blocker evidence. | Commands and outputs recorded in the implementation report. | |

## Implementation Plan

1. Keep the verified root README identity rewrite as prior coverage. Touch root `README.md` only for current version/release-state corrections if required by the docs-quality checker.
2. Repair `groundtruth-kb/scripts/check_docs_cli_coverage.py` and `groundtruth-kb/docs/reference/cli.md` so the checker gives a useful, current signal instead of 117 stale command-reference failures.
3. Add focused tests around the docs checker and CLI reference coverage, preferably `groundtruth-kb/tests/test_docs_cli_coverage.py`.
4. Fix currently failing beginner/documentation examples surfaced by the checker.
5. Normalize version/release language across root/package README and public docs touched by this slice.
6. Correct current-looking retired-poller language in public docs so active guidance describes the file bridge plus cross-harness event-driven trigger, with manual scans as fallback and retired pollers as historical only.
7. Clean MkDocs navigation only where needed for current docs discoverability and red-check repair.
8. File a post-implementation report with exact command results, touched-file list, implementation-start packet id, and a spec-derived test map.

## Target Path Rationale

- `groundtruth-kb/scripts/check_docs_cli_coverage.py`, `groundtruth-kb/docs/reference/cli.md`, and `groundtruth-kb/tests/test_docs_cli_coverage.py` are the highest-leverage mechanical drift surfaces.
- `groundtruth-kb/src/groundtruth_kb/cli.py` is in scope only for the currently failing ChromaDB install-message expectation or CLI help/reference consistency.
- README and public docs paths are in scope only for live drift-check failures, version coherence, copyable command correctness, nav discoverability, and retired-poller language.
- `groundtruth-kb/templates/README.md` is in scope because the live checker reports `gt project init` snippets without `PROJECT_NAME` there.
- This bridge file is in scope as the durable WI-linked proposal artifact.

## Spec-Derived Verification Plan

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: final report maps every touched advisory finding to one or more commands/tests actually run.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: bridge GO plus implementation-start packet before protected mutations; final report cites the packet id.
- `DELIB-1464` F2 docs CI red: `.\.venv\Scripts\python.exe scripts\check_docs_cli_coverage.py` exits 0 from `E:\GT-KB\groundtruth-kb`.
- `DELIB-1464` F3 executable beginner commands: targeted tests or script checks cover `gt project init` snippets and any rewritten beginner commands.
- `DELIB-1464` F4 version/release coherence: version-check portion of `check_docs_cli_coverage.py` passes; targeted `rg` shows no current-doc stale `0.6.0` or `0.6.1` claims outside historical/changelog contexts.
- `DELIB-1464` F5 retired-poller guidance: targeted `rg` and/or tests assert current public docs do not present retired OS/smart pollers as active automation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all touched live docs stay under `E:\GT-KB`; any `E:\Claude-Playground` references are historical/archive context only.
- Repo-native lint and format: run `.\.venv\Scripts\python.exe -m pytest <targeted tests> -q --tb=short`, `.\.venv\Scripts\ruff.exe check <touched python files/tests>`, and `.\.venv\Scripts\ruff.exe format --check <touched python files/tests>`.
- Docs build: run `python -m mkdocs build --strict` in an environment with docs dependencies, or report the dependency blocker precisely if repo-native dependencies are unavailable.

## Prior Coverage Kept Out Of Scope

- Root README identity mismatch was already verified at `bridge/gtkb-docs-quality-remediation-slice-1-root-readme-rewrite-006.md`.
- Start Here adopter rewrite was already verified at `bridge/gtkb-start-here-adopter-rewrite-implementation-010.md`.
- This proposal must not rewrite those verified surfaces broadly. It may only make narrow consistency edits required by the live docs-quality checks.

## Risks And Containment

- The CLI reference may become noisy if every internal/admin command is expanded manually. Containment: prefer deterministic generation or clear grouping, with package CLI primary as the user-facing contract.
- Docs changes can accidentally erase historical evidence. Containment: mark archival reports clearly or move them through normal file history; do not silently delete evidence.
- The package-local venv currently lacks MkDocs. Containment: the implementation report must distinguish "checker passed" from "docs build not runnable in this environment" and use the repo-native docs dependency path if available.
- Broad markdownlint adoption can create a churny formatting project. Containment: markdownlint remains optional for this slice unless implemented as high-signal config without mass reformatting.

## Pre-Filing Preflight

- Code Quality Baseline parity: PASS (`Code Quality Baseline parity clean`).
- Applicability preflight: PASS; `missing_required_specs=[]`; `missing_advisory_specs=[]`.
- Clause preflight: PASS; 5 clauses evaluated, 4 `must_apply`, 1 `may_apply`, 0 blocking gaps.
- The bridge-propose helper will rerun its governed credential scan, author-metadata injection, and bridge-compliance audit before writing the dispatchable numbered bridge file.

## Requested Loyal Opposition Review

Please review whether this remaining-scope proposal is an appropriate WI-3306 implementation bridge under the PAUTH and prior verified docs-quality coverage. A `GO` should authorize the scoped implementation slice above after Prime obtains the implementation-start packet. A `NO-GO` should identify any scope boundary that should be narrowed before implementation, especially if the CLI reference repair or nav/report cleanup is too broad for a single slice.
