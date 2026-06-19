REVISED

bridge_kind: prime_proposal
Document: gtkb-propose-scaffold-invalid-bridge-kind
Version: 005
Author: Prime Builder (Codex auto-dispatch, harness A)
Date: 2026-06-19 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-19T19-30-36Z-prime-builder-A-67d9fa
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex headless bridge auto-dispatch; approval_policy=never; workspace E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4544

target_paths: ["scripts/gtkb_propose_scaffold.py", "platform_tests/scripts/test_gtkb_propose_scaffold.py", ".claude/skills/gtkb-propose/SKILL.md", ".codex/skills/gtkb-propose/SKILL.md", ".codex/skills/MANIFEST.json", ".agent/skills/gtkb-propose/SKILL.md", ".agent/skills/MANIFEST.json", ".api-harness/skills/gtkb-propose/SKILL.md", ".api-harness/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "groundtruth-kb/tests/test_cli_bridge_propose.py"]

implementation_scope: source, tests, canonical skill guidance, generated skill adapters, generated adapter metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

# Revised Implementation Proposal - Fix proposal scaffold bridge_kind default and generated adapter parity

## Summary

This revision addresses the NO-GO in `bridge/gtkb-propose-scaffold-invalid-bridge-kind-004.md`.

WI-4544 is not only a script literal repair. Its acceptance summary requires the scaffold default, `/gtkb-propose` docs/templates, and regression coverage to align with `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`. Version 003 expanded from the original script-only scope but still authorized a direct edit to one generated Codex adapter while omitting the live Antigravity adapter and generated metadata surfaces.

The corrected implementation will:

- change `scripts/gtkb_propose_scaffold.py` so default proposal scaffolds emit `bridge_kind: prime_proposal`;
- change `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` so deterministic `gt bridge propose` draft content emits `bridge_kind: prime_proposal`, not `implementation_proposal_draft`;
- update the canonical `/gtkb-propose` skill guidance at `.claude/skills/gtkb-propose/SKILL.md`;
- regenerate, rather than manually edit, the Codex, Antigravity, and API harness generated skill-adapter outputs and their manifest or registry metadata;
- add regression coverage for taxonomy membership and all live body-bearing `/gtkb-propose` guidance surfaces that can repeat the stale default.

All targeted files are under `E:\GT-KB`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Bridge files plus dispatcher/TAFE state are the governed workflow state; this revision preserves the append-only version chain and uses the governed revision helper.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal links the governing bridge, taxonomy, backlog, and generated-surface requirements and maps them to concrete tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This implementation-targeting revision carries project authorization, project, work item, and inline JSON `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The verification plan maps each governing surface to an executable regression or command evidence.
- `GOV-STANDING-BACKLOG-001` - WI-4544 is the backlog source of truth for this defect and defines the acceptance surface.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - The bridge-kind taxonomy is a cross-cutting write/review gate; authoring helpers must emit values accepted by that gate.
- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` - The hook-enforced taxonomy requirement cited by WI-4544; implementation proposals use `prime_proposal`, not `implementation_proposal` or `implementation_proposal_draft`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The proposal and target files are in-root under `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The bridge revision preserves the decision trail and updates durable authoring artifacts rather than relying on transient operator memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - This NO-GO triggers a REVISED bridge artifact and a future implementation report before VERIFIED closure.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The work keeps the requirement, work item, proposal, tests, and verification evidence connected as governed artifacts.

## Prior Deliberations

- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-001.md` - Original proposal; NO-GO found it under-scoped.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-002.md` - Loyal Opposition NO-GO requiring broader authoring-surface scope and taxonomy-backed regression coverage.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-003.md` - Prior revision; broadened scope but still omitted generated adapter parity surfaces.
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-004.md` - Current NO-GO requiring generated adapter and metadata coverage plus generator-based regeneration.
- `DELIB-20261658` / `bridge/gtkb-bridge-kind-taxonomy-stabilization` - VERIFIED taxonomy stabilization thread; relevant to the canonical `BridgeKind` enum consumed by this proposal.
- `DELIB-20261127` - GO verdict for the bridge-kind taxonomy stabilization proposal.
- `DELIB-2183` / `DELIB-20263646` - Antigravity capability adapter review context; relevant because `.agent/skills/gtkb-propose/SKILL.md` is a live generated adapter.
- `DELIB-20263645` - Loyal Opposition verification for Antigravity capability adapters; relevant to generated adapter parity.

## Owner Decisions / Input

No new owner input is required. WI-4544 is inside `PROJECT-GTKB-RELIABILITY-FIXES`, and the standing reliability fast-lane authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers this bounded repair. No production deployment, credential lifecycle action, destructive cleanup, or formal MemBase specification mutation is in scope.

## Requirement Sufficiency

Existing requirements sufficient.

The implementation relies on the already-verified bridge-kind taxonomy work, WI-4544's acceptance summary, and the existing generated-adapter parity workflow. It does not create, promote, or mutate `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`; it aligns live authoring helpers, guidance, generated adapters, metadata, and tests to that existing taxonomy.

## Findings Addressed

### P1 - Revised target paths still omit a live generated `/gtkb-propose` adapter surface

Resolved by adding `.agent/skills/gtkb-propose/SKILL.md` and `.agent/skills/MANIFEST.json` to `target_paths`. The Antigravity adapter is a live generated `/gtkb-propose` guidance surface and currently repeats the stale default. It will be regenerated from the canonical `.claude/skills/gtkb-propose/SKILL.md` source after the canonical guidance is fixed.

The revision also includes `.api-harness/skills/gtkb-propose/SKILL.md` and `.api-harness/skills/MANIFEST.json`. The API adapter is a compact pointer rather than a full copy of the skill body, so it is not expected to contain the stale guidance line. It still carries canonical-source SHA metadata and must remain synchronized when the canonical skill changes.

### P2 - The proposal scopes a direct edit to a generated adapter instead of the generator/parity workflow

Resolved by making generated-surface writes explicit generator outputs, not manual edits. The implementation path is:

1. Edit canonical source and source templates only: `.claude/skills/gtkb-propose/SKILL.md`, `scripts/gtkb_propose_scaffold.py`, and `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`.
2. Update the two regression test files.
3. Run the Codex, Antigravity, and API adapter generators to update generated adapters, manifests, and registry metadata.
4. Run generator `--check` commands as verification that the generated outputs are current.

The generated target files are listed because the generator writes them. The proposal does not authorize hand-editing generated adapters as the implementation method.

## Scope Changes From Version 003

Added implementation authority for:

- `.agent/skills/gtkb-propose/SKILL.md`
- `.agent/skills/MANIFEST.json`
- `.api-harness/skills/gtkb-propose/SKILL.md`
- `.api-harness/skills/MANIFEST.json`
- `.codex/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`

Clarified that `.codex/skills/gtkb-propose/SKILL.md`, `.agent/skills/gtkb-propose/SKILL.md`, and `.api-harness/skills/gtkb-propose/SKILL.md` are generated outputs. They are in scope for generator output changes only.

Explicitly out of scope:

- changing the canonical `BridgeKind` enum;
- changing the bridge compliance hook;
- changing adapter generator behavior;
- migrating historical bridge files;
- creating or promoting formal MemBase specifications;
- broad cleanup of legacy `implementation_proposal` references outside the live `/gtkb-propose` authoring surfaces and deterministic `gt bridge propose` draft template named here.

## Pre-Filing Preflight Subsection

This REVISED file is filed only after the candidate content passes:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind --content-file .gtkb-tmp/gtkb-propose-scaffold-invalid-bridge-kind-005.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind --content-file .gtkb-tmp/gtkb-propose-scaffold-invalid-bridge-kind-005.md
```

The governed revision helper repeats candidate preflights before writing `bridge/gtkb-propose-scaffold-invalid-bridge-kind-005.md` and publishing dispatcher/TAFE state.

## Spec-Derived Verification Plan

| Specification / governing surface | Test or verification command | Expected evidence |
| --- | --- | --- |
| `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`; `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Update `platform_tests/scripts/test_gtkb_propose_scaffold.py` so the default emitted by `build_scaffold()` is `BridgeKind.PRIME_PROPOSAL.value` and is in `{kind.value for kind in BridgeKind}`. | The scaffold default is both `prime_proposal` and taxonomy-valid. |
| `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`; `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Update `groundtruth-kb/tests/test_cli_bridge_propose.py` so the deterministic `gt bridge propose` template emits `bridge_kind: prime_proposal` and no longer emits `implementation_proposal_draft`. | Both live proposal composers emit a taxonomy-valid implementation proposal kind. |
| WI-4544 `/gtkb-propose` guidance acceptance | Update `platform_tests/scripts/test_gtkb_propose_scaffold.py` so it reads `.claude/skills/gtkb-propose/SKILL.md`, `.codex/skills/gtkb-propose/SKILL.md`, and `.agent/skills/gtkb-propose/SKILL.md`, asserting the documented default is `prime_proposal` and not `implementation_proposal`. | Every live body-bearing `/gtkb-propose` guidance surface no longer instructs the invalid default. |
| Generated adapter source-of-truth discipline | `groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --check --update-registry` | Codex generated adapter body, manifest, and registry metadata are current. |
| Generated adapter source-of-truth discipline | `groundtruth-kb/.venv/Scripts/python.exe scripts/generate_antigravity_skill_adapters.py --check --update-registry` | Antigravity generated adapter body, manifest, and registry metadata are current. |
| Generated adapter source-of-truth discipline | `groundtruth-kb/.venv/Scripts/python.exe scripts/generate_api_skill_adapters.py --check` | API compact pointer adapter and manifest metadata are current. |
| `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`; WI-4544 stale-template sweep | `rg -n "implementation_proposal|implementation_proposal_draft" scripts/gtkb_propose_scaffold.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py .claude/skills/gtkb-propose/SKILL.md .codex/skills/gtkb-propose/SKILL.md .agent/skills/gtkb-propose/SKILL.md groundtruth-kb/tests/test_cli_bridge_propose.py platform_tests/scripts/test_gtkb_propose_scaffold.py` | No live target authoring surface still emits or documents the invalid default, except test assertions that intentionally prove absence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_propose_scaffold.py groundtruth-kb/tests/test_cli_bridge_propose.py -q --tb=short` | The spec-derived scaffold, CLI template, guidance, and adapter parity regressions pass. |
| Python code quality gate from `.claude/rules/file-bridge-protocol.md` | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_propose_scaffold.py platform_tests/scripts/test_gtkb_propose_scaffold.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py groundtruth-kb/tests/test_cli_bridge_propose.py` | Lint passes for changed Python files. |
| Python formatting gate from `.claude/rules/file-bridge-protocol.md` | `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_propose_scaffold.py platform_tests/scripts/test_gtkb_propose_scaffold.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py groundtruth-kb/tests/test_cli_bridge_propose.py` | Formatting check passes for changed Python files. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; implementation report preflight | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-propose-scaffold-invalid-bridge-kind` after filing the implementation report. | No missing required specs; target paths remain approved in-root paths. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; project-root boundary | Manual check via `git diff --name-only --` and the implementation report's files-changed list. | Every changed path is under `E:\GT-KB` and within this proposal's `target_paths`. |

## Risk / Rollback

Bridge-kind vocabulary sits on the authoring, compliance-gate, and dispatch-classification boundary. A careless change could make new proposals non-dispatchable, leave one harness guidance surface stale, or make generated adapter metadata drift from the canonical skill source.

Risk is bounded because the implementation changes authoring defaults, guidance, generated adapter outputs, and tests only. It does not change the canonical `BridgeKind` enum, compliance hook behavior, dispatcher routing, or historical bridge files.

Rollback is a single commit revert of the target paths listed in this proposal.

## Bridge Filing

This revision is filed as `bridge/gtkb-propose-scaffold-invalid-bridge-kind-005.md`, preserving the append-only chain:

- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-001.md` - NEW
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-002.md` - NO-GO
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-003.md` - REVISED
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-004.md` - NO-GO
- `bridge/gtkb-propose-scaffold-invalid-bridge-kind-005.md` - REVISED

Dispatcher/TAFE bridge state plus the numbered file chain are the live workflow state.

## Recommended Commit Type

fix

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
