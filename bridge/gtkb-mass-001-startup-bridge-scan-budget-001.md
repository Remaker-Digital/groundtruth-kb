NEW

# GTKB-MASS-001 Startup Bridge-Scan Budget (Slice 1)

bridge_kind: prime_proposal
Document: gtkb-mass-001-startup-bridge-scan-budget
Version: 001
Author: Prime Builder (Codex Desktop)
Date: 2026-06-28 UTC

author_identity: Prime Builder / Codex Desktop
author_harness_id: A
author_session_context_id: 019f0cf7-9439-7cc3-8b58-cdad991c5890
author_model: GPT-5 via Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop, Windows PowerShell, danger-full-access workspace, network enabled

Project Authorization: PAUTH-PROJECT-GTKB-MASS-001-MASS-001-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-MASS-001
Work Item: GTKB-MASS-001

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization_disclosure_shape.py", "platform_tests/scripts/test_session_self_initialization_canonical_consistency.py", "platform_tests/scripts/test_groundtruth_governance_adoption.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal processes the next active backlog item for `GTKB-MASS-001` after
the isolation-program blocker cleared. It implements a narrow startup/dashboard
acceptance slice: keep the fresh-session startup model responsive when the
bridge directory contains thousands of versioned files.

The immediate evidence is a focused acceptance sweep run on 2026-06-28:
`python -m pytest platform_tests/scripts/test_session_self_initialization.py
platform_tests/scripts/test_session_self_initialization_disclosure_shape.py
platform_tests/scripts/test_session_self_initialization_canonical_consistency.py
platform_tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short`
timed out in `test_startup_disclosure_includes_harness_launchability_alert`.
The stack shows `build_startup_model()` calling `_backlog_metrics()`, then
`_bridge_latest_status()`, then `_bridge_entries_from_version_files()`, which
reads every `bridge/*-NNN.md` file to compute latest status. That is now too
expensive for the startup acceptance path.

The proposed implementation keeps the same startup/backlog semantics but
optimizes the hot path: compute latest bridge status by grouping versioned
bridge filenames per document and reading only the latest candidate file needed
for each document, preserving canonical first-line status parsing and not
reintroducing aggregate queue artifacts. This slice does not claim GT-KB is
mass-adoption ready and does not authorize staging, commit, push, merge,
deployment, credential work, scaffold apply, release publication, or public
adoption.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — The bridge file chain remains the live authority; this change may optimize how startup reads latest statuses, but it must not create or depend on an aggregate queue artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — This proposal carries explicit specification links and must pass applicability preflight before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — This proposal includes `Project Authorization`, `Project`, and `Work Item` metadata for the implementation-targeting bridge entry.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — The implementation report must map each governing spec to concrete verification evidence and await Loyal Opposition verification.
- `GOV-STANDING-BACKLOG-001` — `GTKB-MASS-001` is selected from the governed MemBase project backlog after higher-priority work is either blocked or waiting on Loyal Opposition.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — The bounded authorization `PAUTH-PROJECT-GTKB-MASS-001-MASS-001-BOUNDED-IMPLEMENTATION-2026-06-23` covers this work item but does not bypass the bridge GO or implementation-start packet.
- `GOV-SESSION-SELF-INITIALIZATION-001` — Fresh-session startup must present current role/governance/dashboard/backlog context from live project sources without becoming unusably slow.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` — The startup disclosure shape and governance stance must remain intact after the optimization.
- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` — The dashboard/startup model must continue to expose the project dashboard and KPI context.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — Startup should avoid avoidable high-cost scans; the observed all-version bridge-file scan violates the budget intent as the bridge history grows.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — This slice produces local readiness evidence for the startup acceptance gate while withholding any release-readiness claim.
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` — Adoption readiness remains gated by governed evidence; this proposal fixes one local gate and does not authorize external adoption.

## Prior Deliberations

- `DELIB-20265586` — Owner-directed bounded project authorization for the 2026-06-23 mass project batch; this proposal stays within the snapshot-bound `GTKB-MASS-001` authorization.
- `DELIB-0758` — Broader mass-adoption readiness context carried by prior verified mass-adoption bridge threads.
- `DELIB-1207` and `DELIB-1208` — Prior readiness-status context cited by the verified scoping thread; this proposal advances the next local evidence gate after isolation-program completion.
- `DELIB-0633` — Product posture remains developer-preview/alpha territory; this proposal explicitly avoids claiming public or external mass-adoption readiness.
- `DELIB-0840` — Session self-initialization decision; the startup surface must disclose role, dashboard, and top-priority context without stale or unusable behavior.
- Prior bridge history: `bridge/gtkb-mass-adoption-readiness-012.md` verified the developer-preview MVP only; `bridge/gtkb-mass-adoption-readiness-scoping-006.md` verified a status report that kept `GTKB-MASS-001` deferred until isolation/release-readiness evidence cleared; `bridge/gtkb-mass-adoption-first-commit-package-019.md` closed only a filing-scoped package decision and preserved separate approval for any staging mechanics.
- Plan source: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-MASS-ADOPTION-READINESS-PLAN-2026-04-20.md` identifies the next-session startup acceptance test as the first gate.

## Owner Decisions / Input

No new owner decision is required before Loyal Opposition review. Owner
authorization for this backlog project is recorded in `DELIB-20265586` and
the active PAUTH listed above. Implementation still requires a live bridge
`GO` and a successful implementation-start packet before protected source/test
mutation.

## Requirement Sufficiency

Existing requirements sufficient. The work is a narrow implementation defect
within the already-governed startup acceptance surface (`GOV-SESSION-SELF-
INITIALIZATION-001`, `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`,
`SPEC-PROJECT-DASHBOARD-KPI-LINK-001`, and `DCL-SESSION-STARTUP-TOKEN-BUDGET-
001`) and the active `GTKB-MASS-001` readiness plan. No new or revised
requirement is needed.

## Spec-Derived Verification Plan

Expected implementation evidence:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-mass-001-startup-bridge-scan-budget
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-mass-001-startup-bridge-scan-budget
python -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py platform_tests/scripts/test_session_self_initialization_canonical_consistency.py platform_tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short
```

Spec-to-evidence mapping:

| Specification | Verification |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Add or update tests proving bridge latest-status semantics still derive from versioned bridge files and preserve canonical status parsing while avoiding aggregate queue artifacts. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability preflight passes with no missing required specs; project linkage metadata remains in this proposal and the implementation report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report includes this spec-derived verification table and the commands above; Loyal Opposition verifies after implementation. |
| `GOV-STANDING-BACKLOG-001` / `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start packet confirms `GTKB-MASS-001`, `PROJECT-GTKB-MASS-001`, and the active PAUTH before protected edits. |
| `GOV-SESSION-SELF-INITIALIZATION-001` / `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` | Existing startup disclosure tests pass; no role/governance/dashboard/focus-choice disclosure regression. |
| `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` | Existing dashboard/startup model assertions in the focused test suite continue to pass. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | A new or updated regression test demonstrates `_bridge_latest_status()` no longer reads every historical version file for every bridge thread when only latest status is needed. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` / `GOV-GTKB-ADOPTION-ENFORCEMENT-001` | Implementation report states the slice is local readiness evidence only and makes no mass-adoption, release, staging, commit, push, merge, or deployment claim. |

## Risk / Rollback

Primary risk is accidentally changing stale-backlog filtering by losing support
for older bridge files whose first line embeds a canonical status inside a
Markdown heading, such as `# VERIFIED: ...`. The implementation must preserve
that parsing. Secondary risk is leaning on dispatcher/TAFE state in a startup
path that currently depends on bridge version files; the intended fix is a
bounded read optimization, not an authority change.

Rollback is a single-commit revert restoring the prior all-version scan and
tests. The change is local to startup/report generation and its regression
tests; no MemBase migration, release operation, deployment, or external state
mutation is in scope.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-mass-001-startup-bridge-scan-budget`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix — this repairs a startup acceptance performance regression exposed by the
current bridge-history volume.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
