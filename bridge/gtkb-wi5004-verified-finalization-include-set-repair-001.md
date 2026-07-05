NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; reasoning=xhigh; approval_policy=never; resolved_role=prime-builder; restart-continuation
author_metadata_source: codex-interactive-env

# Implementation Proposal - WI-5004 VERIFIED Finalization Include-Set Repair

bridge_kind: prime_proposal
Document: gtkb-wi5004-verified-finalization-include-set-repair
Version: 001
Date: 2026-07-05 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5004-VERIFY-FINALIZATION-REPAIR
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5004

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the dispatched `VERIFIED` finalization helper so the include set required for atomic verification commits is derived from the implementation report's actual changed-file claim, not from the proposal/report `target_paths` authorization envelope. This prevents a dispatched Loyal Opposition finalization from sweeping unrelated dirty files that were authorized as possible scope but were not changed by the implementation report under review.

This proposal intentionally uses the active repair authorization, not the closure-only WI-5004 authorization. It authorizes a bounded source/test slice only after Loyal Opposition GO, work-intent ownership, and implementation-start authorization.

## Claim

`WI-5004` remains open because direct regression coverage still shows the finalization helper can over-require or over-stage paths that are not the implementation report's actual changed-file set. Prime Builder proposes to harden the helper copies and tests so a dispatched `VERIFIED` worker can finalize only the implementation report's actual changed files plus the bridge verdict chain, while preserving the existing by-reference waiver path and staged-set safety checks.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-5004` describes the observed 2026-07-03 four-cycle `VERIFIED` finalization loop from WI-4785. `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5004-VERIFY-FINALIZATION-REPAIR` authorizes only bridge, skill-helper, and test mutations for this repair. No production deployment, credential changes, broad dirty-worktree cleanup, or sweep commit is in scope.

## In-Root Placement Evidence

All target paths are inside the active GT-KB project root and are platform-side helper/test files:

- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `platform_tests/skills/test_verified_finalization_validation_hardening.py`

No Agent Red repository, archive checkout, deployment target, credential file, or external path is in scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires Prime to file this proposal as `NEW` and obtain Loyal Opposition `GO` before protected helper/test mutation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the active project authorization does not bypass live bridge GO, work-intent, or implementation-start gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specifications for the helper and test repair.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project authorization, project, work item, and parseable target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map each linked specification to executed tests before `VERIFIED`.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - finalization verdicts and helper-generated bridge files must carry credible author/session provenance.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - harness-surface proposal must declare cross-harness disposition and maintain parity or cite a waiver.
- `ADR-CROSS-HARNESS-PARITY-001` - equivalent helper behavior across active harnesses is required unless deliberately waived.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatched bridge verification workers must be able to finalize without cross-thread dirty-file capture.
- `ADR-DISPATCHER-ARCHITECTURE-001` - preserves daemon/headless dispatch as the coordination surface instead of requiring owner-interactive rescue for routine finalization.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - keeps Codex/Claude/Cursor helper behavior aligned where native hooks differ.
- `GOV-STANDING-BACKLOG-001` - WI-5004 is the recorded backlog defect and must be terminalized through governed evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - routes the defect and repair through durable bridge, tests, and work-item evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves artifact-first closure rather than chat-only operational knowledge.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the implementation report and verification verdict must record the lifecycle evidence for this repair.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work remains platform-side and in-root.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directive for stabilizing unattended headless bridge processing under `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`.
- `WI-5004` MemBase record - records the WI-4785 `VERIFIED` finalization loop caused by deriving the finalize include-set from broad `target_paths` rather than the implementation report's actual files changed.
- `bridge/gtkb-role-authority-boundary-implementable-correction-008.md`, `-010.md`, `-012.md`, and `-014.md` - the repeated NO-GO/REVISED verification loop cited by WI-5004.
- Commit `93061e3c` - interactive scoped finalization that broke the WI-4785 loop by including only actual changed files and required owner-approved narrative artifacts.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5004-VERIFY-FINALIZATION-REPAIR` - active repair authorization created after the closure-only assessment found direct regression risk.

## Owner Decisions / Input

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - standing owner authority for dispatcher/harness stabilization follow-up work.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5004-VERIFY-FINALIZATION-REPAIR` - active owner/project authorization for this bounded source/test repair.

No new owner decision is requested by this proposal. It does not authorize a shared-database sweep, production deployment, credential operation, or broad dirty-worktree cleanup.

## Proposed Scope

- Update the `VERIFIED` finalization helper's claimed-path parser so `target_paths` metadata is treated as an authorization envelope, not as a report claim that must be included in the finalization commit.
- Keep actual changed-file extraction from explicit implementation-report sections such as `## Files Changed` and other established report changed-file claims.
- Preserve the `## By-Reference Finalization Waiver` behavior for cases where an implementation report intentionally names an authorized path by reference but does not change it.
- Align the `.claude`, `.codex`, and `.cursor` helper copies for this behavior and for directory-target staged-child handling where the copies have drifted.
- Harden regression fixtures so finalization tests use realistic author/session metadata, predecessor `Responds to:` links, and non-self-review author/reviewer contexts.
- Add regression coverage proving `target_paths` alone no longer forces unrelated dirty paths into the include set and proving directory targets expand to staged children without sweeping unrelated staged files.

## Cross-Harness Disposition

This proposal deliberately touches verify-helper skill surfaces for Claude, Codex, and Cursor because the `VERIFIED` finalization behavior must be equivalent across those harnesses. The intended disposition is behavioral parity, not a waiver:

- Claude: update `.claude/skills/verify/helpers/write_verdict.py` as the canonical helper surface used by LO finalization.
- Codex: update `.codex/skills/verify/helpers/write_verdict.py` to match the finalization behavior and staged-child directory handling required by the canonical helper.
- Cursor: update `.cursor/skills/verify/helpers/write_verdict.py` to match the same behavior because Cursor has an active helper copy and must not regress if enabled for equivalent review work.
- Antigravity, Ollama, and OpenRouter: no direct helper file is in scope for this slice; their dispatcher participation remains governed by the shared bridge state and harness registry. No owner waiver is requested or relied on for those harnesses.

Parity verification must include the helper-copy parametrized tests in `platform_tests/skills/test_verified_finalization_validation_hardening.py` and the atomic finalization tests in `platform_tests/scripts/test_lo_verified_commit_atomicity.py`.

## Explicit Non-Scope

- Do not resolve WI-5004 as closure-only in this slice.
- Do not commit or sweep `groundtruth.db`.
- Do not perform broad dirty-worktree cleanup or unrelated helper parity rewrites.
- Do not alter dispatcher selection, bridge state, project authorization tables, credentials, deployment files, or production services.
- Do not restore retired pollers or alternate queue authority.

## Current Worktree Coordination Note

The target helper files already have uncommitted edits from other governed outage/harness work in this shared workspace. This proposal does not claim those existing edits as WI-5004 implementation. After GO, Prime must inspect and preserve unrelated existing edits, make only the WI-5004 delta needed for this repair, and report the exact changed-file set. If the existing dirty state makes scoped implementation impossible, Prime must pause and file a bridge/report disposition rather than silently bundling unrelated work.

## Architecture Alignment Ledger

- OPS consolidation: the repair reduces owner-interactive rescue loops and lets governed bridge verification progress through the consolidated dispatcher/harness workflow.
- Dispatcher daemon architecture: the fix supports headless LO finalization launched by the daemon without forcing unrelated target-path files into the verification commit.
- Lifecycle-first/scoring-last precedence: lifecycle truth comes from the implementation report's actual changed-file claim and bridge status chain; target scoring/authorization scope does not override report lifecycle evidence.
- Portfolio reconciliation: WI-5004 remains a distinct finalization-helper defect and is not conflated with closure-only PAUTH records or shared database finalization policy decisions.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Candidate and live bridge preflights pass; implementation starts only after LO `GO` plus work-intent and implementation authorization. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5004-verified-finalization-include-set-repair` issues a packet only after this proposal receives `GO`; protected helper/test writes stay inside target paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight shows no missing required specs for the proposal/report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge compliance and applicability preflight parse the PAUTH/project/WI/target_paths metadata. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps these specs to executed helper and atomicity tests with observed results. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Existing and new tests reject synthetic/self-review metadata where finalization requires real author/reviewer contexts. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Cross-harness disposition is present and helper-copy parametrized tests cover `.claude`, `.codex`, and `.cursor`. |
| `ADR-CROSS-HARNESS-PARITY-001` | Helper behavior is equivalent across Claude, Codex, and Cursor copies or the implementation report explains any deliberate non-equivalence. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/skills/test_verified_finalization_validation_hardening.py -q --tb=short` passes. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | The helper continues to support daemon-dispatched verification without retired queue/poller dependencies; `gt bridge dispatch status --json` remains routing-healthy after implementation. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `.claude`, `.codex`, and `.cursor` helper copies share the targeted finalization behavior and regression tests cover all helper copies. |
| `GOV-STANDING-BACKLOG-001` | WI-5004 remains open until implementation report and LO verification provide terminal evidence; no raw SQL or unreviewed backlog mutation. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All mutations are confined to in-root platform helper/test paths. |

## Acceptance Criteria

- `target_paths` metadata in a post-implementation report no longer causes `_assert_include_set_covers_report_claims` to require every authorized target in the `--include` set.
- Explicit actual changed-file sections still require those changed files to be covered by the include set unless a valid by-reference waiver applies.
- Directory include targets expand to their staged children consistently across `.claude`, `.codex`, and `.cursor` helper copies.
- Regression fixtures use credible author/session metadata and predecessor chain links so self-review and provenance checks exercise real finalization conditions.
- Focused tests pass for all helper copies and the atomic finalization path.
- Implementation report lists only files actually changed by WI-5004 and does not bundle unrelated dirty worktree changes.

## Pre-Filing Preflight Subsection

Candidate preflights are executed against this final proposal content immediately before the governed bridge writer files `bridge/gtkb-wi5004-verified-finalization-include-set-repair-001.md`:

- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5004-verified-finalization-include-set-repair --content-file .tmp/gtkb-wi5004-verified-finalization-include-set-repair-001.candidate.md --json`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5004-verified-finalization-include-set-repair --content-file .tmp/gtkb-wi5004-verified-finalization-include-set-repair-001.candidate.md`

Observed gate expectation for filing: applicability `preflight_passed: true`, `missing_required_specs: []`, and clause preflight exit 0 with no blocking gaps. If either command fails, this proposal must not be filed.

## Risks / Rollback

Risk is moderate because finalization code is shared across harness helper copies. The main risks are over-narrowing changed-file extraction, weakening by-reference waiver behavior, or allowing unscoped staged files into a `VERIFIED` commit. Rollback is a source/test revert of the helper and regression-test changes, followed by a new bridge disposition if WI-5004 remains unresolved. Bridge files remain append-only audit artifacts.

## Files Expected To Change

- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `platform_tests/skills/test_verified_finalization_validation_hardening.py`

## Recommended Commit Type

`fix`
