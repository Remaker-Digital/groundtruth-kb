NEW

# WI-4744 Bridge Compliance Gate Index Exemption Regression Coverage

bridge_kind: prime_proposal
Document: gtkb-wi4744-index-exemption-reconciliation
Version: 001
Date: 2026-06-24 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-24T02-38-04Z-prime-builder-A-may29-hygiene
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop heartbeat automation; Prime Builder; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4744

target_paths: ["platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py"]
implementation_scope: test_addition
requires_review: true
requires_verification: true

---

## Claim

WI-4744 remains open in PROJECT-GTKB-MAY29-HYGIENE even though the broad failure class described by the work item no longer reproduces: the focused index-exemption test file currently passes, and the live/template bridge-compliance gates both return a concrete governance denial for a non-index versioned bridge file.

This proposal requests a narrow test-addition slice, not a direct MemBase reconciliation. The implementation will add one focused regression test to `platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py` proving that a normal versioned bridge proposal path such as `bridge/example-thread-001.md` is not treated as the retired aggregate `bridge/INDEX.md` path and does receive a concrete `_deny_reason_for_content` governance denial.

No hook source change is proposed unless the new focused test unexpectedly fails after GO. If source is required, Prime Builder must stop and file a revised proposal because the approved target path for this slice is test-only.

## Current Live Evidence

Current WI state:

- `gt backlog show WI-4744 --json` reports `resolution_status: open`, `stage: backlogged`, `project_name: PROJECT-GTKB-MAY29-HYGIENE`, and `approval_state: unapproved`.
- `gt bridge threads --wi WI-4744` reports no existing bridge threads.
- The active bounded authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23` includes `WI-4744`, cites owner decision `DELIB-20265586`, and allows `test_addition`.

Focused evidence gathered before filing:

```text
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py -q --tb=short
```

Observed result:

```text
18 passed in 0.47s
```

Scoped dirty check:

```text
git status --short -- .claude/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py groundtruth.db
```

Observed result: exit 0 with no output. The live hook, focused test file, and `groundtruth.db` were clean at proposal time.

Direct non-index denial probe:

```text
python -c "<import live/template bridge-compliance-gate modules and call _deny_reason_for_content(file_path='bridge/example-thread-001.md', content='NEW\\n\\n# Example\\n')>"
```

Observed result for both live and template hooks:

```text
[Governance] Implementation proposals must include concrete Specification Links before bridge submission. (Hard-block per DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.)
```

## Requirement Sufficiency

Existing requirements are sufficient.

WI-4744 asks to align bridge-compliance-gate tests and/or helper behavior so retired `bridge/INDEX.md` handling and non-index bridge proposal handling are deterministic and covered. The current tree already covers the retired aggregate helper and pending target-path scan behavior. The missing durable regression is a direct `_deny_reason_for_content` assertion for a normal versioned bridge proposal path, which is the exact code path the original WI says returned `None`.

This test-addition slice satisfies the work item without changing production hook behavior:

- `bridge/INDEX.md` remains denied as a retired aggregate artifact.
- A versioned bridge file such as `bridge/example-thread-001.md` remains eligible for normal proposal-governance checks.
- `_deny_reason_for_content` must return a concrete governance reason for incomplete versioned bridge proposal content.
- The test applies to both the live hook and template hook surfaces because the existing fixture parametrizes both modules.

No new requirement, spec mutation, owner decision, direct MemBase reconciliation, project membership change, or source change is needed for this slice.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - The proposal routes a protected test mutation through the bridge before any edit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The new regression asserts incomplete implementation proposals receive the concrete Specification Links governance denial.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This proposal carries project authorization, project, and work-item metadata lines.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The verification plan maps the linked governance requirements to focused pytest and lint/format evidence.
- `GOV-STANDING-BACKLOG-001` - WI-4744 is a governed backlog item whose completion evidence must be durable and discoverable.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The active bounded PAUTH authorizes only the listed snapshot WI set and mutation classes; this proposal stays inside the `test_addition` class.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - After LO verification, project completion depends on member WIs reaching terminal status through the governed lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The observed hygiene defect is preserved as bridge/test evidence rather than harness-local memory.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The work item, proposal, regression test, implementation report, and verification verdict form one artifact chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - A completed defect with durable evidence should transition through the governed lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The only target path is an in-root GT-KB platform test file.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - The regression covers both live and template hook surfaces through the existing parametrized fixture.
- `.claude/rules/file-bridge-protocol.md` - Bridge files are append-only and implementation waits for LO GO plus implementation-start authorization.
- `.claude/rules/codex-review-gate.md` - The proposal cites relevant specifications and supplies a spec-derived test plan before review.

## Prior Deliberations

- `DELIB-20263738` - Loyal Opposition verification for bridge-compliance-gate INDEX exemption coverage.
- `DELIB-2492` - Loyal Opposition review for LO file-safety PreToolUse enforcement slice 1; relevant to bridge-compliance hook testing.
- `DELIB-20263742` - Loyal Opposition review for bridge-compliance-gate SPEC_TEST_HEADING_RE multiline behavior.
- `DELIB-20264361` - Loyal Opposition review for no-index runtime tooling cleanout.
- `DELIB-20265034` - Loyal Opposition verification verdict for WI-4510 Phase 3 default-off TAFE-canonical write path.
- `DELIB-20265399` - GO precedent for a May29 Hygiene stale-open reconciliation proposal where completed bridge/test evidence remained out of sync with MemBase.
- `DELIB-2026-06-20-WI4237-RESCOPE-NO-INDEX-OPERATOR-SKILL` - Owner decision that the no-index bridge era uses dispatcher/TAFE and surviving reconciliation tooling instead of retired INDEX-centric commands.

Deliberation search executed before filing:

```text
gt deliberations search "WI-4744 bridge compliance gate index exemption stale open reconciliation" --limit 10 --json
```

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23` - Active bounded implementation authorization for the 14 snapshot member WIs, including WI-4744.
- `DELIB-20265586` - Owner decision for the bounded May29 Hygiene snapshot authorization. The authorization explicitly limits new project WIs as out of scope and allows `test_addition`, which is the mutation class used by this proposal.

No new owner decision is required because this proposal does not add project WIs, does not mutate formal GOV/SPEC/ADR/DCL/PB/REQ artifacts, does not request direct backlog resolution, and stays within the authorized snapshot and allowed mutation class.

## Proposed Scope

After LO returns GO and Prime Builder acquires the implementation-start packet:

1. Add one focused regression test to `platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py`.
2. The test must call `gate._deny_reason_for_content(...)` using `file_path="bridge/example-thread-001.md"` and incomplete `NEW` proposal content.
3. The assertion must require a non-empty governance denial containing `Specification Links`.
4. The assertion must also prove the reason is not the retired aggregate denial, so normal versioned bridge files remain distinct from `bridge/INDEX.md`.
5. Run the focused pytest, ruff check, and ruff format check on the touched test file.
6. File a post-implementation report carrying the executed command output and spec-to-test mapping.

Out of scope:

- Editing `.claude/hooks/bridge-compliance-gate.py`.
- Editing `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`.
- Directly mutating `groundtruth.db` or resolving WI-4744 in MemBase.
- Adding new work items or expanding project authorization scope.
- Formal GOV/SPEC/ADR/DCL/PB/REQ mutation.

## Specification-Derived Verification Plan

| Specification | Verification Evidence Required |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show LO GO and implementation-start packet before editing the test file. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Focused regression asserts incomplete versioned bridge proposal content gets the concrete Specification Links denial. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Post-implementation report keeps PAUTH/project/WI metadata. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Report maps every linked spec to executed focused pytest/lint/format evidence. |
| `GOV-STANDING-BACKLOG-001` | Read back WI-4744 and cite this bridge chain as durable completion evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Re-query the active PAUTH and confirm WI-4744 remains in the included snapshot. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | Show the implementation report is ready for LO verification so the WI can reach terminal lifecycle state by the governed path. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Preserve the hygiene finding as a durable regression test plus bridge evidence. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Demonstrate the work item, bridge thread, and test evidence agree. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Show the completed defect has a lifecycle transition path through VERIFIED evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm the touched path is in-root. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Focused pytest runs the existing live/template parametrization. |

Commands to execute after GO:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4744-index-exemption-reconciliation
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py -q --tb=short
python -m ruff check platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py
python -m ruff format --check platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py
gt backlog show WI-4744 --json
gt projects show PROJECT-GTKB-MAY29-HYGIENE --json
```

## Pre-Filing Preflight Results

Applicability preflight:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4744-index-exemption-reconciliation --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi4744-index-exemption-reconciliation-001.md
```

Observed result:

- content_source: `pending_content`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

Clause preflight:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4744-index-exemption-reconciliation --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi4744-index-exemption-reconciliation-001.md
```

Observed result:

- Clauses evaluated: `5`
- must_apply: `4`
- may_apply: `1`
- Evidence gaps in must_apply clauses: `0`
- Blocking gaps (gate-failing): `0`
- Exit code: `0`

## Acceptance Criteria

- `platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py` contains a focused non-index `_deny_reason_for_content` regression test.
- The test passes for both live and template hook modules through the existing parametrized fixture.
- Focused pytest passes.
- `ruff check` and `ruff format --check` pass on the touched test file.
- No source, hook, template, CLI, scaffold, formal artifact, project membership, or MemBase mutation occurs in this slice.
- Post-implementation report includes before/after evidence and waits for LO VERIFIED.

## Risks / Rollback

Risk is low. The implementation adds a focused regression test for behavior already observed in the live and template hooks. If the test proves redundant or poorly framed, rollback is removal of the added test before the implementation report is filed, or a follow-up REVISED proposal if LO requests a different assertion.

## Files Expected To Change

- `platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py`

## Recommended Commit Type

`test`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
