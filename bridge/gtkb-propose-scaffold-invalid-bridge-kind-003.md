REVISED

bridge_kind: prime_proposal
Document: gtkb-propose-scaffold-invalid-bridge-kind
Version: 003
Author: Prime Builder (Codex auto-dispatch, harness A)
Date: 2026-06-19 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-19T19-01-22Z-prime-builder-A-8e7b4a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex headless bridge auto-dispatch; approval_policy=never; workspace E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4544

target_paths: ["scripts/gtkb_propose_scaffold.py", "platform_tests/scripts/test_gtkb_propose_scaffold.py", ".claude/skills/gtkb-propose/SKILL.md", ".codex/skills/gtkb-propose/SKILL.md", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "groundtruth-kb/tests/test_cli_bridge_propose.py"]

implementation_scope: source, tests, authoring guidance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

# Revised Implementation Proposal - Fix proposal scaffold bridge_kind default

## Summary

This revision addresses the NO-GO in `bridge/gtkb-propose-scaffold-invalid-bridge-kind-002.md` by expanding WI-4544 from a narrow script literal change into the full live authoring-surface repair that the work item requires.

The implementation will align both proposal composers that Prime Builder can use:

- `scripts/gtkb_propose_scaffold.py`, the `/gtkb-propose` skill helper, will default to `bridge_kind: prime_proposal`.
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`, the `gt bridge propose` deterministic draft CLI, will emit `bridge_kind: prime_proposal` instead of `implementation_proposal_draft`.
- The canonical `/gtkb-propose` skill guidance and the generated Codex adapter will say the default is `prime_proposal`.
- Regression coverage will assert that the scaffold default is a member of the live `BridgeKind` taxonomy and that the live user-facing skill guidance no longer instructs the invalid default.

All targeted files and generated artifacts remain in-root under `E:\GT-KB`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Bridge files plus dispatcher/TAFE state are the governed workflow state; this revision preserves the append-only version chain and uses the governed revision helper.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal links the governing bridge and taxonomy requirements and maps them to concrete tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This implementation-targeting revision carries project authorization, project, work item, and inline JSON `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The verification plan maps each governing surface to an executable regression or explicit command evidence.
- `GOV-STANDING-BACKLOG-001` - WI-4544 is the backlog source of truth for this defect and defines the acceptance surface.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - The bridge-kind taxonomy is a cross-cutting write/review gate; authoring helpers must emit values accepted by that gate.
- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` - The hook-enforced taxonomy requirement cited by WI-4544; implementation proposals use `prime_proposal`, not `implementation_proposal` or `implementation_proposal_draft`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The proposal and target files are in-root under `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The bridge revision preserves the decision trail and updates durable authoring artifacts rather than relying on transient operator memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - This NO-GO triggers a REVISED bridge artifact and a future implementation report before VERIFIED closure.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The work keeps the requirement, work item, proposal, tests, and verification evidence connected as governed artifacts.

## Prior Deliberations

- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-001.md` - Original proposal; NO-GO found it under-scoped.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-002.md` - Loyal Opposition NO-GO requiring the expanded target paths, explicit taxonomy link, taxonomy-backed regression, and real risk note.
- `DELIB-20261127` / `bridge/gtkb-bridge-kind-taxonomy-stabilization-004.md` - GO verdict for the canonical `BridgeKind` taxonomy stabilization proposal.
- `DELIB-20261128` / `bridge/gtkb-bridge-kind-taxonomy-stabilization-006.md` - Verification NO-GO showing the taxonomy thread's mandatory preflight and spec-to-test expectations.
- `bridge/gtkb-bridge-kind-taxonomy-stabilization-008.md` - Final VERIFIED state for the canonical `BridgeKind` enum and taxonomy-lint work this proposal now consumes.

## Owner Decisions / Input

No new owner decision is required. WI-4544 is inside `PROJECT-GTKB-RELIABILITY-FIXES`, and the standing reliability fast-lane authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers this bounded repair. No production deployment, credential lifecycle action, destructive cleanup, or formal MemBase spec mutation is in scope.

## Requirement Sufficiency

Existing requirements sufficient.

The implementation relies on the already-verified bridge-kind taxonomy work and WI-4544's acceptance summary. It does not create, promote, or mutate `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` as a formal MemBase row; it only aligns live authoring helpers and guidance to the existing hook-enforced taxonomy.

## Findings Addressed

### P1 - Target paths omit live authoring surfaces

Resolved by expanding `target_paths` beyond the original scaffold script and scaffold tests. The approved implementation scope now includes:

- the deterministic `/gtkb-propose` scaffold helper;
- the scaffold regression tests;
- the canonical `/gtkb-propose` skill guidance;
- the generated Codex `/gtkb-propose` adapter;
- the live `gt bridge propose` deterministic draft template; and
- the CLI template regression tests.

`groundtruth-kb/src/groundtruth_kb/bridge/taxonomy.py` remains evidence, not an implementation target. The repair should consume that canonical enum, not change it.

### P2 - Taxonomy requirement not linked or mapped to regression

Resolved by citing `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` and adding verification that the emitted default is accepted by `groundtruth_kb.bridge.taxonomy.BridgeKind`. The regression should not only assert one literal string; it should prove that the default belongs to the authoritative enum.

## Scope Changes From Version 001

Added implementation authority for:

- `.claude/skills/gtkb-propose/SKILL.md`
- `.codex/skills/gtkb-propose/SKILL.md`
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `groundtruth-kb/tests/test_cli_bridge_propose.py`

Explicitly out of scope:

- changing the canonical `BridgeKind` enum;
- changing the bridge compliance hook;
- migrating historical bridge files;
- creating or promoting formal MemBase specifications;
- broad cleanup of legacy `implementation_proposal` test fixtures outside these two authoring surfaces.

## Pre-Filing Preflight Subsection

This REVISED file is filed only after the candidate content passes:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind --content-file .gtkb-tmp/gtkb-propose-scaffold-invalid-bridge-kind-003.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind --content-file .gtkb-tmp/gtkb-propose-scaffold-invalid-bridge-kind-003.md
```

The governed revision helper repeats those candidate preflights before writing `bridge/gtkb-propose-scaffold-invalid-bridge-kind-003.md` and publishing dispatcher/TAFE state.

## Spec-Derived Verification Plan

| Specification / governing surface | Test or verification command | Expected evidence |
| --- | --- | --- |
| `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`; `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Add or update `platform_tests/scripts/test_gtkb_propose_scaffold.py` so the default emitted by `build_scaffold()` is `BridgeKind.PRIME_PROPOSAL.value` and is in `{kind.value for kind in BridgeKind}`. | The scaffold default is both `prime_proposal` and taxonomy-valid. |
| `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`; `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Add or update `groundtruth-kb/tests/test_cli_bridge_propose.py` so the deterministic `gt bridge propose` template emits `bridge_kind: prime_proposal` and no longer emits `implementation_proposal_draft`. | Both live proposal composers emit a taxonomy-valid implementation proposal kind. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind` after filing the implementation report. | No missing required specs; target paths remain the approved in-root paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_propose_scaffold.py groundtruth-kb/tests/test_cli_bridge_propose.py -q --tb=short` | The spec-derived scaffold and CLI template regressions pass. |
| `/gtkb-propose` user-facing guidance acceptance from WI-4544 | Add or update a regression in `platform_tests/scripts/test_gtkb_propose_scaffold.py` that reads `.claude/skills/gtkb-propose/SKILL.md` and `.codex/skills/gtkb-propose/SKILL.md`, asserting the documented default is `prime_proposal` and not `implementation_proposal`. | User-facing guidance no longer instructs the invalid default. |
| Python code quality gate from `.claude/rules/file-bridge-protocol.md` | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_propose_scaffold.py platform_tests/scripts/test_gtkb_propose_scaffold.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py groundtruth-kb/tests/test_cli_bridge_propose.py` | Lint passes for the changed Python files. |
| Python formatting gate from `.claude/rules/file-bridge-protocol.md` | `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_propose_scaffold.py platform_tests/scripts/test_gtkb_propose_scaffold.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py groundtruth-kb/tests/test_cli_bridge_propose.py` | Formatting check passes for the changed Python files. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; project-root boundary | Manual check via `git diff --name-only --` and the implementation report's files-changed list. | Every changed path is under `E:\GT-KB` and within this proposal's `target_paths`. |

## Risk / Rollback

Bridge-kind vocabulary sits on the authoring, compliance-gate, and dispatch-classification boundary. A careless change could make new proposals non-dispatchable, leave one harness's guidance stale, or make a draft template look compliant while still requiring manual correction before filing.

Risk is bounded because the change is limited to authoring defaults and guidance, not the taxonomy enum or compliance hook. Rollback is a single commit revert of the six target paths listed in this proposal.

## Bridge Filing

This revision is filed as `bridge/gtkb-propose-scaffold-invalid-bridge-kind-003.md`, preserving the append-only chain:

- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-001.md` - NEW
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-002.md` - NO-GO
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-003.md` - REVISED

Dispatcher/TAFE bridge state plus the numbered file chain are the live workflow state.

## Recommended Commit Type

fix

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
