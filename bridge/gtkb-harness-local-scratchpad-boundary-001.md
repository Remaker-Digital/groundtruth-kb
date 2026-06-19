NEW

# gtkb-harness-local-scratchpad-boundary - Harness-Local Scratchpads Are Non-Authoritative

bridge_kind: prime_proposal
Document: gtkb-harness-local-scratchpad-boundary
Version: 001
Author: Loyal Opposition / Codex
Date: 2026-06-19 UTC

author_identity: codex-loyal-opposition
author_harness_id: A
author_session_context_id: codex-lo-harness-local-scratchpad-boundary-20260619
author_model: GPT-5
author_model_version: GPT-5 Codex desktop
author_model_configuration: Codex desktop API session, owner-declared Loyal Opposition

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-WI-4681-HARNESS-SCRATCHPAD-BOUNDARY
Project: PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION
Work Item: WI-4681

target_paths: ["AGENTS.md", ".claude/rules/project-root-boundary.md", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_harness_local_scratchpad_boundary.py"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Clarify the GT-KB root-boundary and source-of-truth rules so harness-local
scratchpads cannot become formal GT-KB artifacts, evidence, or live
dependencies. This closes the newly visible class of drift where Antigravity
planning files, Codex automation memory, Claude Code auto-memory, or the
`MEMORY.md` hierarchy may look useful enough to cite even though they are not
under reliable GT-KB change control.

The implementation must make the distinction explicit: harness-native scratch
and memory surfaces may exist as runtime byproducts or operational notes, but
they are non-authoritative. Any project-relevant information originating there
must be promoted into governed in-root artifacts such as MemBase, the
Deliberation Archive, specifications, ADR/DCL/GOV records, bridge files,
source, tests, or approved reports before it can be cited, verified, or treated
as a dependency.

This slice does not authorize disabling harness memory systems, deleting the
existing `MEMORY.md` hierarchy, changing credential handling, restoring retired
pollers, or creating new out-of-root dependencies.

## Specification Links

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - governs the central requirement that current-state and authoritative reads go to the canonical SoT, not convenient substitute files.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps platform, adopter application, and harness-runtime surfaces distinct; this proposal must not route GT-KB artifacts into app or harness-local locations.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires this implementation proposal and subsequent verdicts to use the versioned bridge file chain and dispatcher/TAFE state as workflow authority.
- `GOV-ARTIFACT-APPROVAL-001` - governs the owner-decision and approval-packet evidence used to authorize this policy/rule clarification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded project authorization before protected implementation work proceeds.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - constrains the PAUTH envelope: only WI-4681, only listed mutation classes, and no forbidden operations.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to map implementation scope to governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires machine-readable project authorization, project, work item, and target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the eventual implementation report to provide spec-derived verification evidence, not prose-only claims.

## Prior Deliberations

- `DELIB-20260619-HARNESS-SCRATCHPAD-NON-AUTHORITY` - owner directive for this slice: harness-local scratchpads, auto-memory systems, and the `MEMORY.md` hierarchy are non-authoritative and cannot be reliable change-control surfaces.
- `DELIB-20260670` - empirical SoT-fragmentation survey that found agents using non-SoT files as current-state substitutes.
- `DELIB-20260671` / `DELIB-20260672` / `DELIB-20260673` - Platform SoT Consolidation authority chain that absorbed the Agent SoT Read Discipline work and established the read-discipline umbrella.
- `DELIB-20260879` - owner authorization for the existing Slice 2A read-discipline implementation envelope; WI-4681 is a narrower follow-on because the existing envelope did not explicitly cover harness-local scratchpad authority.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` - existing root-boundary exception for invoking external harness executables; this proposal preserves that narrow executable-only exception and does not extend it to harness-local files, memory, planning documents, or evidence.

## Owner Decisions / Input

Owner decision captured as `DELIB-20260619-HARNESS-SCRATCHPAD-NON-AUTHORITY`
with formal approval packet:
`.groundtruth/formal-artifact-approvals/2026-06-19-DELIB-20260619-HARNESS-SCRATCHPAD-NON-AUTHORITY.json`.

The bounded implementation authorization is
`PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-WI-4681-HARNESS-SCRATCHPAD-BOUNDARY`.
It authorizes only WI-4681 and only the protected narrative/source/test
mutation classes needed to declare and test this boundary.

## Requirement Sufficiency

Existing requirements are sufficient when combined with the new owner decision.
This implementation is a clarification and enforcement slice inside the
Platform SoT Consolidation program, not a new source-of-truth registry design.

Implementation must satisfy these operative requirements:

1. `AGENTS.md` and `.claude/rules/project-root-boundary.md` explicitly classify harness-local scratchpads as non-authoritative.
2. The classification includes Antigravity planning/brain files, Codex automation memory, Claude Code auto-memory, and the `MEMORY.md` hierarchy.
3. Formal GT-KB artifacts, implementation reports, verification verdicts, tests, doctor checks, bridge evidence, governed decisions, release evidence, and dependency closure must not read from or depend on harness-local scratchpads as authority.
4. Project-relevant information originating in a scratchpad must be promoted into a governed in-root artifact before citation or dependency.
5. The existing external-harness executable resolution exception remains executable-only and must not be broadened to out-of-root harness files or memory.
6. The implementation must include deterministic tests that fail if the rule text regresses back to allowing scratchpad authority.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not add credential material, environment values, or private host paths as formal dependencies. | Helper credential scan on the filed bridge body plus targeted review of changed rule/test text. | No waiver. |
| CQ-PATHS-001 | Yes | Keep all canonical artifacts and tests inside the GT-KB root and describe user-profile harness storage only as non-authoritative runtime scratch. | Bridge preflight, target-path parsing, and the new pytest boundary assertions. | No waiver. |
| CQ-COMPLEXITY-001 | Yes | Keep the implementation as rule text plus focused deterministic assertions unless doctor enforcement needs a small helper. | Focused pytest and reviewer inspection of any doctor change. | No waiver. |
| CQ-CONSTANTS-001 | Yes | Use named assertion fixtures and constants in the new test module rather than repeated ad hoc strings. | Ruff lint and focused pytest. | No waiver. |
| CQ-SECURITY-001 | Yes | Preserve credential lifecycle boundaries and avoid reading harness-local memory as a trusted input. | Review target diff against PAUTH forbids and focused tests. | No waiver. |
| CQ-DOCS-001 | Yes | Update the canonical operator-facing rule surfaces, not scattered session notes. | Pytest asserts both `AGENTS.md` and `.claude/rules/project-root-boundary.md` carry the boundary. | No waiver. |
| CQ-TESTS-001 | Yes | Add deterministic assertions for scratchpad non-authority and executable-exception non-expansion. | `python -m pytest platform_tests/scripts/test_harness_local_scratchpad_boundary.py -q --tb=short`. | No waiver. |
| CQ-LOGGING-001 | Yes | If doctor code changes, emit ordinary deterministic doctor findings only; no new runtime monitor or poller logging. | Focused doctor test or reviewer confirmation when doctor is unchanged. | No waiver. |
| CQ-VERIFICATION-001 | Yes | Require bridge preflights, focused pytest, and ruff lint/format on modified Python files before implementation report filing. | Commands listed in the Spec-Derived Verification Plan. | No waiver. |

No new code-quality degradation is authorized. The implementation report must
state the pre-change baseline for any targeted checks it runs, distinguish
pre-existing unrelated failures from new failures, and leave all modified Python
files passing ruff lint and format checks.

## Spec-Derived Verification Plan

Expected implementation checks:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-local-scratchpad-boundary --content-file bridge/gtkb-harness-local-scratchpad-boundary-001.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-local-scratchpad-boundary --content-file bridge/gtkb-harness-local-scratchpad-boundary-001.md
python -m pytest platform_tests/scripts/test_harness_local_scratchpad_boundary.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_harness_local_scratchpad_boundary.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_harness_local_scratchpad_boundary.py
```

Expected PASS criteria:

- Applicability preflight passes with no missing required specs and with the PAUTH/project/WI triple resolving to active records.
- Clause preflight reports zero blocking gaps.
- The new pytest module asserts the required phrases and semantics in `AGENTS.md` and `.claude/rules/project-root-boundary.md`.
- If `doctor.py` is changed, focused doctor coverage proves the boundary is machine-checkable and does not confuse historical references or the executable-only harness exception with formal scratchpad authority.
- Ruff lint and format checks pass for any modified Python files.

## Risk / Rollback

Primary risk is overbroad wording that accidentally forbids legitimate harness
runtime behavior or the existing external-harness executable resolution
exception. Keep the rule focused on authority, evidence, dependencies, and
promotion into governed artifacts; do not ban scratchpad existence.

Secondary risk is making `memory/MEMORY.md` look canonical by naming it. Avoid
that by calling the hierarchy operational scratch/notepad unless a specific
artifact is explicitly governed elsewhere, and by requiring promotion to MemBase,
Deliberation Archive, specs, bridge files, source, tests, or approved reports
before formal citation.

Rollback is a single revert of the implementation commit plus withdrawal or
revision of this bridge thread. Because this proposal does not authorize
deleting memory systems or changing credentials/deployments, rollback has low
operational blast radius.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-harness-local-scratchpad-boundary`; no prior version is
deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs` if the implementation only updates rule text and markdown-boundary tests;
`fix` if it also adds or changes doctor enforcement code.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*