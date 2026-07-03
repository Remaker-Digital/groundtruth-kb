NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex desktop runtime 2026-07-03
author_model_configuration: Codex desktop; E:/GT-KB; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb

# Finalization Tooling Batch Implementation Report

bridge_kind: implementation_report
Document: gtkb-finalization-tooling-batch
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-finalization-tooling-batch-002.md
Approved proposal: bridge/gtkb-finalization-tooling-batch-001.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4974-4976-FINALIZATION-TOOLING-20260702
Work Items: WI-4974, WI-4975, WI-4976
Recommended commit type: fix:

## Implementation Claim

Implemented the governed finalization-tooling repair batch authorized by the latest `GO`:

- WI-4974: bridge review-independence resolution now matches exact numbered bridge files for the active slug and accepts explicit reviewed-artifact references with trailing descriptor text.
- WI-4975: Claude, Codex, and Cursor verify helpers now preserve leading-dot repo paths such as `.codex/`, `.claude/`, `.cursor/`, `.github/`, and `.githooks/` when extracting claimed report paths.
- WI-4976: member-terminal project retirement now fails safe unless project-scoped VERIFIED bridge evidence exists; the scanner exposes the missing-evidence reason and ignores noncanonical `*-draft.md` files as terminal evidence.

No dispatcher topology, dispatcher config, credential, release/deployment, Agent Red, or out-of-root mutation was performed. The dispatcher daemon remained stopped as required by the GO.

## Authorization Evidence

- Latest bridge status before implementation and before filing: `GO` at `bridge/gtkb-finalization-tooling-batch-002.md`.
- Work-intent claim: `claim_kind=go_implementation`, `acting_role=prime-builder`, session `019f23f0-b16e-7481-8a18-9622ab564d50`, not expired, extended once to `ttl_expires_at=2026-07-03T02:18:01Z`.
- Implementation-start packet refreshed before mutation: `sha256:46b5482c96e451cd163c823b3108e59f1bf36f92a9f2efd060ed099428d4dade`, created `2026-07-03T01:11:37Z`, expires `2026-07-03T03:11:37Z`.
- PAUTH: `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4974-4976-FINALIZATION-TOOLING-20260702`, active, project `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`.
- Dispatch state after implementation: `python -m groundtruth_kb.cli bridge dispatch daemon status --json` reported `"running": false`; `python -m groundtruth_kb.cli bridge dispatch status --json` reported `health_status: WARN` with the already-known stale/failed runtime classifications and B still `can_receive_dispatch: false`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Prior Deliberations

- `bridge/gtkb-finalization-tooling-batch-001.md` - approved Prime Builder proposal for WI-4974, WI-4975, and WI-4976.
- `bridge/gtkb-finalization-tooling-batch-002.md` - Loyal Opposition GO authorizing this bounded implementation.
- `DELIB-20260702-FINALIZATION-TOOLING-BATCH-DIRECTIVE` - PAUTH owner-decision evidence carried by the project authorization.

## Implementation Details

### WI-4974 Review-Independence Resolution

- `scripts/bridge_review_independence.py` now builds an exact `<slug>-NNN.md` matcher instead of prefix-globbing `<slug>-*.md`, so prefix-superset threads such as exact-target amendments and noncanonical drafts cannot be selected as the reviewed artifact.
- `_REVIEWED_REFERENCE_RE` now captures the referenced `.md` path before descriptor prose, so lines such as `Responds to: bridge/foo-003.md (NEW implementation report)` resolve correctly.
- Added `platform_tests/scripts/test_bridge_review_independence.py` covering prefix-superset exclusion and descriptor-tolerant reviewed-artifact references.

### WI-4975 Dot-Directory Claimed Paths

- `.claude/skills/verify/helpers/write_verdict.py`, `.codex/skills/verify/helpers/write_verdict.py`, and `.cursor/skills/verify/helpers/write_verdict.py` now strip trailing punctuation with `rstrip(...)` instead of stripping leading punctuation, preserving leading-dot directories.
- `platform_tests/skills/test_verified_finalization_validation_hardening.py` now checks all three helper copies for `.codex/`, `./.claude/`, `.cursor/`, `.github/`, and `.githooks/` recognition.

### WI-4976 VERIFIED-Gated Retirement

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` now accepts `project_root` in `member_completion_status` and `member_completion_ready`; mutating auto-retirement passes the root and requires project-scoped VERIFIED bridge evidence for every active member WI.
- `scripts/project_verified_completion_scanner.py` now carries evidence-specific fields in `MemberCompletionReadiness` and prints non-VERIFIED bridge thread and missing VERIFIED bridge evidence details in `--member-completion` output.
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py` now passes the caller's configured project root to the post-update auto-retirement actuator instead of the module-global root, preserving fixture/root fidelity.
- `platform_tests/scripts/test_project_verified_completion_scanner.py` adds a regression where `gtkb-draft-thread-002-draft.md` starts with `VERIFIED` but the canonical latest numbered file is `NEW`; member-completion readiness remains false.
- `platform_tests/skills/test_auto_retire_actuation_helper_parity.py` seeds canonical VERIFIED bridge evidence in the parity fixture so all three helper copies exercise the stricter retirement gate equivalently.

## Files Changed

- `scripts/bridge_review_independence.py`
- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `scripts/project_verified_completion_scanner.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`
- `platform_tests/scripts/test_bridge_review_independence.py`
- `platform_tests/skills/test_verified_finalization_validation_hardening.py`
- `platform_tests/skills/test_auto_retire_actuation_helper_parity.py`
- `platform_tests/scripts/test_project_verified_completion_scanner.py`

`platform_tests/hooks/test_project_completion_surface.py` was part of the verification matrix but did not require source edits. `groundtruth.db` was already dirty before this implementation slice and was not directly mutated by this slice.

## Dirty Worktree Boundary Notes

- `.claude/skills/verify/helpers/write_verdict.py` already contained an unrelated dirty hunk adding `NO-ACTION` to `STATUS_RE`; this report claims only the `_looks_like_claimed_repo_path` change in that file.
- `platform_tests/skills/test_auto_retire_actuation_helper_parity.py` already contained an unrelated dirty hunk adding author metadata to the seeded implementation report; this report claims only the canonical WI/VERIFIED bridge evidence fixture change in that file.
- `groundtruth.db` was already modified in the worktree and was not changed directly here. No broad dirty-worktree cleanup, staging, commit, or DB snapshot finalization was performed.

## Architecture Alignment Ledger

| Axis | Alignment evidence |
| --- | --- |
| OPS consolidation | The slice supports Wave 1 finalization by making bridge/report/retirement tooling fail safe instead of silently finalizing overlapping or draft evidence. It does not change the canonical OPS project family chosen by WI-4960. |
| Dispatcher daemon architecture | Dispatch remained quiesced; no daemon restart, runtime topology activation, B re-enablement, or dispatcher rules edit occurred. The repair targets finalization helpers/scanners so later dispatch can be verified against canonical bridge state. |
| Lifecycle-first/scoring-last precedence | Project retirement now requires lifecycle evidence (`VERIFIED` bridge coverage) before any terminal-status/scoring-like conclusion can close a project. Scoring/ranking activation remains outside this slice. |
| Portfolio reconciliation findings | Prefix-superset bridge matching and draft-file terminal confusion are fixed so amendment threads, stale variants, and noncanonical drafts cannot be mistaken for canonical Wave evidence. |
| Owner deliberations | The batch stays within PAUTH and GO limits, preserves headless PB/LO coordination, and records the remaining dispatch health WARN rather than overriding it. |

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -m groundtruth_kb.cli bridge show gtkb-finalization-tooling-batch --json` showed latest status `GO`; report filing uses the governed bridge helper. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-finalization-tooling-batch` returned active PAUTH and packet hash `sha256:46b5482c96e451cd163c823b3108e59f1bf36f92a9f2efd060ed099428d4dade`. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | Scanner/parity tests pass with VERIFIED-gated retirement and draft-file rejection. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | New report carries explicit author identity, harness, session, model, and model-configuration metadata. |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Helper behavior test covers Claude, Codex, and Cursor copies; all 13 validation-hardening tests and 7 parity tests passed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed paths are in-root GT-KB platform/helper/test paths; no application or Agent Red artifacts were touched. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Required pytest and ruff commands are recorded below with pass results. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_bridge_review_independence.py -q --tb=short`
- `python -m pytest platform_tests/skills/test_verified_finalization_validation_hardening.py -q --tb=short`
- `python -m pytest platform_tests/skills/test_auto_retire_actuation_helper_parity.py platform_tests/hooks/test_project_completion_surface.py platform_tests/scripts/test_project_verified_completion_scanner.py -q --tb=short`
- `python -m ruff check scripts/bridge_review_independence.py scripts/project_verified_completion_scanner.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py platform_tests/scripts/test_bridge_review_independence.py platform_tests/skills/test_verified_finalization_validation_hardening.py platform_tests/skills/test_auto_retire_actuation_helper_parity.py platform_tests/hooks/test_project_completion_surface.py platform_tests/scripts/test_project_verified_completion_scanner.py`
- `python -m ruff format --check scripts/bridge_review_independence.py scripts/project_verified_completion_scanner.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py platform_tests/scripts/test_bridge_review_independence.py platform_tests/skills/test_verified_finalization_validation_hardening.py platform_tests/skills/test_auto_retire_actuation_helper_parity.py platform_tests/hooks/test_project_completion_surface.py platform_tests/scripts/test_project_verified_completion_scanner.py`
- `python -m groundtruth_kb.cli bridge dispatch daemon status --json`
- `python -m groundtruth_kb.cli bridge dispatch status --json`

## Observed Results

- Bridge review-independence tests: 2 passed in 0.23s.
- Verified finalization validation hardening: 13 passed in 2.38s.
- Auto-retire helper parity, project-completion hook, and project verified-completion scanner: 29 passed in 18.52s with one unrelated `chromadb` deprecation warning.
- Ruff check: all checks passed.
- Ruff format check: 9 files already formatted.
- Dispatcher daemon status: `"running": false`, satisfying the GO quiescence condition.
- Dispatcher status: `health_status: WARN`, with known runtime classifications still present; B remained `can_receive_dispatch: false`.

## Remaining Follow-Up / LO Review Notes

- This report intentionally does not restart dispatch or re-enable B. Automated LO routing remains quiesced per the GO condition.
- The existing optional byte-identical helper-copy test outside this GO remains unsuitable for the current helper reality because Claude carries additional author-session hardening not present in Codex/Cursor; the required behavioral parity tests pass.
- The large dirty worktree means LO should review this report against the curated path set above rather than the scaffold helper's raw `files_changed_count`.
