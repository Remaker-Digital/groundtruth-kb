NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e8a66-8f02-7780-b1ee-a1234796d729
author_model: GPT-5 Codex
author_model_version: 2026-06-02 runtime
author_model_configuration: Codex Desktop default reasoning
author_metadata_source: explicit Codex proposal filing metadata

# Implementation Proposal - DEFERRED Authority And Protocol Alignment

bridge_kind: prime_proposal
Document: gtkb-deferred-authority-protocol-alignment
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-02 UTC
Session: 019e8a66-8f02-7780-b1ee-a1234796d729

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-008

target_paths: [".claude/rules/file-bridge-protocol.md", ".claude/rules/bridge-essential.md", ".claude/rules/canonical-terminology.md", ".claude/rules/operating-model.md", ".claude/hooks/bridge-compliance-gate.py", ".claude/hooks/lo-file-safety-gate.py", ".claude/skills/bridge/helpers/show_thread_bridge.py", ".claude/skills/bridge/helpers/scan_bridge.py", ".claude/skills/bridge/helpers/revise_bridge.py", ".claude/skills/bridge/helpers/impl_report_bridge.py", ".groundtruth/formal-artifact-approvals/2026-06-02-claude-rules-file-bridge-protocol-md.json", ".groundtruth/formal-artifact-approvals/2026-06-02-claude-rules-bridge-essential-md.json", ".groundtruth/formal-artifact-approvals/2026-06-02-claude-rules-canonical-terminology-md.json", ".groundtruth/formal-artifact-approvals/2026-06-02-claude-rules-operating-model-md.json", "config/agent-control/system-interface-map.toml", "groundtruth-kb/src/groundtruth_kb/bridge/index_mutation.py", "groundtruth-kb/src/groundtruth_kb/project/preflight.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/membase_effective_use_audit.py", "groundtruth-kb/src/groundtruth_kb/reporting/harvest_coverage.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/authority.py", "groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "groundtruth-kb/templates/rules/file-bridge-protocol.md", "groundtruth-kb/templates/rules/bridge-essential.md", "groundtruth-kb/templates/rules/canonical-terminology.md", "groundtruth-kb/templates/skills/bridge/helpers/show_thread_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/bridge/INDEX.md", "groundtruth-kb/tests/fixtures/bridge_index_live_snapshot.md", "scripts/bridge_author_metadata.py", "scripts/gtkb_bridge_writer.py", "scripts/bridge_applicability_preflight.py", "scripts/adr_dcl_clause_preflight.py", "scripts/bridge_index_chain_audit.py", "scripts/bridge_reconciliation_audit.py", "scripts/bridge_work_intent_registry.py", "scripts/check_index_role_intent_sentinel.py", "scripts/bridge_citation_freshness_preflight.py", "scripts/bridge_proposal_pattern_lint.py", "scripts/bridge_proposal_wi_id_collision_check.py", "scripts/backfill_approval_state.py", "scripts/harvest_session_deliberations.py", "scripts/retroactive_harvest_bridge_threads.py", "scripts/session_self_initialization.py", "scripts/spec_to_test_mapper.py", "scripts/run_spec_derived_tests.py", "scripts/rehearse/_bridge_split.py", "platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py", "platform_tests/hooks/test_bridge_author_metadata_gate.py", "platform_tests/hooks/test_lo_file_safety_gate.py", "platform_tests/scripts/test_bridge_author_metadata.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_bridge_index_chain_audit.py", "groundtruth-kb/tests/test_cli_bridge_index.py", "groundtruth-kb/tests/test_cli_authority.py", "groundtruth-kb/tests/test_doctor_legacy_root.py", "groundtruth-kb/tests/test_preflight_checks.py", "groundtruth-kb/tests/test_project_scaffold_bridge_statuses.py"]

## Claim

The verified parser/actionability repair for `DEFERRED` was necessary but incomplete. `BridgeStatus.DEFERRED` now exists in the canonical bridge parser, yet live protocol text, status-token gates, helper parsers, scaffold templates, preflight tooling, index mutation, and authority-discovery surfaces still disagree about whether `DEFERRED` is a real bridge status and who may use it.

This proposal completes Project 1 from `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-02-GLOSSARY-CLI-SCAN.md`: align `DEFERRED` semantics across live plus package-template surfaces, make owner-only set and clear authority explicit and testable, add `gt authority resolve`, and hard-fail active artifacts that treat `E:\Claude-Playground` as live GT-KB authority. It deliberately does not add a separate slug-mute registry or sidecar. Suppression occurs only through owner-approved versioned `DEFERRED` bridge files.

## Scope Boundary

In scope:

1. Treat `DEFERRED` as a first-class `bridge/INDEX.md` status with versioned file syntax: `DEFERRED: bridge/<slug>-NNN.md` and a version file whose first non-blank line is `DEFERRED`.
2. Define split semantics: indexed `DEFERRED` is a bridge queue state; parked drafts remain non-indexed draft files under their existing draft conventions.
3. Enforce owner-only set and clear authority for `DEFERRED`: agents may propose or request deferral, but a live `DEFERRED` status or a transition out of a latest `DEFERRED` state must cite explicit owner decision evidence.
4. Update live bridge/protocol/helpers/hooks/preflight/parser surfaces so `DEFERRED` is parsed, visible, non-actionable, and accepted as a canonical body status token where appropriate.
5. Update package templates, scaffold output, and golden fixtures so future GT-KB installs inherit the same behavior.
6. Add `gt authority resolve <subject>` as a read-only CLI that resolves owner-facing system/artifact terms to canonical live authority using `config/agent-control/system-interface-map.toml` as the source.
7. Add a doctor check that hard-fails active artifacts that treat `E:\Claude-Playground` as live GT-KB authority while preserving historical/reference evidence in archives and bridge history.

Out of scope:

- No slug-mute registry, sidecar, `.gtkb-state` mute file, or cached suppression table.
- No automatic deferral based on agent judgment.
- No second bridge queue or alternate queue runtime.
- No broad remediation of existing bridge reconciliation findings from `gt bridge reconcile index-chain`; this proposal only ensures the status vocabulary and authority surfaces can represent `DEFERRED` correctly.
- No new Deliberation Archive records during implementation; owner decisions for this proposal have already been captured and are cited below.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` remains the canonical bridge queue state; versioned bridge files are the audit trail for status transitions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live GT-KB artifacts and authority dependencies remain inside `E:\GT-KB`; `E:\Claude-Playground` is archive-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites relevant governing specifications and owner decisions.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map linked specifications to tests and executed command evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner decisions, bridge proposal, implementation report, and verification report form the durable governance record.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability across owner decisions, status semantics, source changes, tests, and bridge review is required.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - `DEFERRED` is an explicit artifact lifecycle state and must not be confused with terminal verification or withdrawal.
- `GOV-STANDING-BACKLOG-001` - `GTKB-GOV-008` is the tracked work item; this proposal is a single-WI review packet, not a bulk backlog operation.
- `GOV-ARTIFACT-APPROVAL-001` - protected narrative rule-file updates require approval packets before writes.
- `PB-ARTIFACT-APPROVAL-001` - Prime Builder implementation authority does not waive protected narrative-artifact approval evidence.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - protected narrative-artifact writes must satisfy the narrative/formal approval hook and universal pre-commit floor.

## Prior Deliberations

- `DELIB-0873` - prior GO for a scoped bridge dispatcher deferral-enforcement repair. It required a follow-on implementation bridge to state selected design, cover dispatch/actionability, define authority, and add suppression tests.
- `DELIB-2363` - GO for `bridge/gtkb-bridge-dispatcher-deferral-enforcement-repair-003.md`; it approved only parser/actionability repair and explicitly excluded broader status tooling and owner-mute authority.
- `DELIB-2364` - NO-GO on an earlier stale deferral proposal; it highlighted missing owner authority decisions.
- `bridge/gtkb-bridge-dispatcher-deferral-enforcement-repair-006.md` - VERIFIED the canonical parser/actionability repair for `DEFERRED`; this proposal is a follow-on, not a revision of that terminal thread.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-PROJECT1-SCOPE` - owner selected Project 1 only for this plan.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-SPLIT-SEMANTICS` - owner selected split semantics between indexed `DEFERRED` status and non-indexed parked drafts.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-OWNER-ONLY-DEFERRAL-AUTHORITY` - owner selected owner-only set and clear authority.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-LEGACY-ROOT-HARD-FAIL` - owner selected hard-fail for active artifacts that treat `E:\Claude-Playground` as live authority.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-AUTHORITY-RESOLVE-CLI` - owner selected adding `gt authority resolve`.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-VERSIONED-DEFERRED-FILE` - owner selected versioned `DEFERRED` bridge files as the audit-trail shape.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-LIVE-PLUS-TEMPLATES` - owner selected updating live surfaces plus package templates/golden fixtures in the same slice.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-DEFERRED-ONLY-NO-SLUG-MUTE` - owner selected `DEFERRED` only, with no separate slug-mute registry.

## Owner Decisions / Input

This proposal depends on explicit owner decisions captured in the current session:

1. Scope is Project 1 only: `DELIB-20260602-GLOSSARY-CLI-SCAN-PROJECT1-SCOPE`.
2. Vocabulary uses split semantics: indexed `DEFERRED` bridge status vs non-indexed parked draft files: `DELIB-20260602-GLOSSARY-CLI-SCAN-SPLIT-SEMANTICS`.
3. `DEFERRED` set and clear are owner-only: `DELIB-20260602-GLOSSARY-CLI-SCAN-OWNER-ONLY-DEFERRAL-AUTHORITY`.
4. Active legacy-root references are hard failures in doctor: `DELIB-20260602-GLOSSARY-CLI-SCAN-LEGACY-ROOT-HARD-FAIL`.
5. Add `gt authority resolve`: `DELIB-20260602-GLOSSARY-CLI-SCAN-AUTHORITY-RESOLVE-CLI`.
6. Audit trail is a versioned `DEFERRED` bridge file: `DELIB-20260602-GLOSSARY-CLI-SCAN-VERSIONED-DEFERRED-FILE`.
7. Update live plus templates/golden surfaces: `DELIB-20260602-GLOSSARY-CLI-SCAN-LIVE-PLUS-TEMPLATES`.
8. Suppression uses `DEFERRED` only, with no sidecar mute registry: `DELIB-20260602-GLOSSARY-CLI-SCAN-DEFERRED-ONLY-NO-SLUG-MUTE`.

No additional owner decision is requested for this proposal filing. Implementation must still obtain protected narrative-artifact approval packets before editing `.claude/rules/*.md` files, because the owner has approved the direction and semantics but has not yet been shown the exact full replacement content for those protected files.

## Requirement Sufficiency

Existing requirements plus the eight cited owner decisions are sufficient for this implementation. No new specification artifact is required before implementation because the work is a protocol/tooling alignment of the already-verified `DEFERRED` parser status and the owner-selected authority model. The protected narrative rule-file edits are governed by existing approval-packet requirements rather than new policy.

## DEFERRED Semantics To Implement

1. `DEFERRED` is an indexed bridge queue status, not a draft marker.
2. A live deferral is represented by both an INDEX line and a versioned bridge file:
   - INDEX line: `DEFERRED: bridge/<slug>-NNN.md`.
   - Body token: first non-blank line of `bridge/<slug>-NNN.md` is `DEFERRED`.
3. The `DEFERRED` body must include an `Owner Decisions / Input` section citing the owner decision that sets the deferral, a reason, and the condition or owner action required to clear it.
4. `DEFERRED` is non-actionable for both Prime Builder and Loyal Opposition. It suppresses bridge dispatch because `compute_actionable_pending` must exclude it for both role queues.
5. `DEFERRED` is reversible but owner-controlled. A later version may supersede it only when the later version cites explicit owner clear/reactivation evidence in `Owner Decisions / Input`.
6. Normal `NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, `WITHDRAWN`, and `ADVISORY` semantics remain unchanged.
7. Parked drafts remain unindexed draft files under `.gtkb-state/bridge-revisions/drafts/`, `.gtkb-state/bridge-impl-reports/drafts/`, or equivalent helper-owned draft locations. A parked draft does not suppress dispatch unless a live versioned `DEFERRED` status exists in `bridge/INDEX.md`.
8. No separate mute state exists. There is no sidecar, registry, or cached suppression table.

## Proposed Implementation Plan

### IP-1: Live protocol and glossary alignment

Update live rule/protocol surfaces so they enumerate `DEFERRED` consistently:

- `.claude/rules/file-bridge-protocol.md`: add `DEFERRED` to the status table, role/actionability rules, body status-token rule, and version-chain examples. Define owner-only set/clear authority, versioned file requirement, non-actionability, and split semantics from parked drafts.
- `.claude/rules/bridge-essential.md`: align compact bridge guidance and role-actionability summary.
- `.claude/rules/canonical-terminology.md`: add or update glossary entry for `DEFERRED` as a bridge status and distinguish it from deferred decisions, parked drafts, and ordinary backlog deferral.
- `.claude/rules/operating-model.md`: update status vocabulary only if it enumerates bridge statuses.
- `config/agent-control/system-interface-map.toml`: add authority-resolve subjects/aliases for file bridge, bridge queue, bridge status, parked draft, project root, role assignment, canonical glossary, and doctor.

Protected narrative writes under `.claude/rules/*.md` require approval packets at implementation time. The four packet target paths listed in `target_paths` are planned packet locations; implementation must populate them with full proposed content and owner approval evidence before protected writes.

### IP-2: Live bridge parser, writer, hook, and helper alignment

Update every live surface that parses or validates bridge status lines so `DEFERRED` is canonical:

- `scripts/bridge_author_metadata.py`: add `DEFERRED` to `BRIDGE_AUTHOR_METADATA_STATUSES` so versioned `DEFERRED` bridge files receive required author metadata.
- `.claude/hooks/bridge-compliance-gate.py`: recognize `DEFERRED` as a canonical body status token, include it in error text, include it in latest-status parsing, and require non-empty `Owner Decisions / Input` for `DEFERRED` files.
- `.claude/hooks/lo-file-safety-gate.py`: parse `DEFERRED` status lines so bridge safety checks do not fall through to stale older statuses.
- `.claude/skills/bridge/helpers/show_thread_bridge.py`, `scan_bridge.py`, `revise_bridge.py`, and `impl_report_bridge.py`: parse and display `DEFERRED`; never classify it as role-actionable.
- `groundtruth-kb/src/groundtruth_kb/bridge/index_mutation.py`: allow `DEFERRED` as a valid status token but require owner-decision evidence when setting `DEFERRED` or when prepending any active status over a latest `DEFERRED` entry.
- `scripts/gtkb_bridge_writer.py`: add `DEFERRED` to valid status parsing but reject it through normal Prime/LO role transitions unless explicit owner-decision evidence is supplied. Also require owner-decision evidence when clearing a latest `DEFERRED` state.
- Preflight/audit/parser tooling listed in `target_paths`: update status regexes to include `DEFERRED` so they do not ignore a live top status and accidentally evaluate an older actionable line below it.

### IP-3: Owner-only deferral checks

Add deterministic checks that make owner-only set/clear mechanically visible:

- A `DEFERRED` bridge file without an `Owner Decisions / Input` section citing a `DELIB-*` owner decision must fail the bridge-compliance gate.
- A `gt bridge index set-status --status DEFERRED ...` call must fail unless an owner decision id/reason is supplied and the referenced bridge file starts with `DEFERRED` and includes owner-decision evidence.
- A transition from latest `DEFERRED` to `NEW`, `REVISED`, `ADVISORY`, `WITHDRAWN`, or any other status must require owner clear/reactivation evidence. Ordinary role authority alone is insufficient.
- Tests must cover both denial and allowed cases.

### IP-4: Add `gt authority resolve`

Add a read-only CLI group/command:

```text
gt authority resolve <subject> [--json]
```

Behavior:

- Resolves `<subject>` by canonical id, canonical name, or accepted alias in `config/agent-control/system-interface-map.toml`.
- Prints canonical name, concept/artifact class, authoritative source, generated-vs-authoritative classification, read method, mutation method, role permissions, related specs, and caveats.
- Fails clearly for unknown subjects and suggests nearest known aliases when possible.
- Does not create a second authority registry. The system-interface map remains the source for this command.

Minimum subjects/aliases that must resolve in tests: `bridge`, `bridge index`, `bridge status`, `parked draft`, `project root`, `role assignment`, `canonical glossary`, `doctor`, `work item`, and `MemBase`.

### IP-5: Hard-fail active legacy-root authority references

Add a doctor check that scans active artifact surfaces for `E:\Claude-Playground` or equivalent legacy-root references used as live authority/dependency paths.

Hard-fail active surfaces include:

- `.claude/rules/*.md`, `AGENTS.md`, and startup/role rule surfaces.
- `.claude/hooks/*.py`, `.codex/hooks.json`, `.claude/settings.json`, and bridge/helper scripts.
- `config/**`, `scripts/**`, `groundtruth-kb/src/**`, `groundtruth-kb/templates/**`, and scaffold golden fixtures.
- Current generated dashboard/startup source files when they name live authority sources.

Allowed historical/reference surfaces include:

- Existing versioned `bridge/*.md` history when the path is cited as evidence of an old decision or defect.
- `independent-progress-assessments/**` reports and archive evidence, unless the text instructs agents to treat the legacy root as live.
- Explicit archive directories and generated historical logs.

The doctor finding must report file path, line, matched legacy path, and why the path was classified as active vs historical. Active findings exit non-zero. Historical findings may be informational.

### IP-6: Package templates, scaffold, and golden fixtures

Update the package-side surfaces so fresh scaffolded adopters inherit the same bridge contract:

- `groundtruth-kb/templates/rules/file-bridge-protocol.md`
- `groundtruth-kb/templates/rules/bridge-essential.md`
- `groundtruth-kb/templates/rules/canonical-terminology.md`
- `groundtruth-kb/templates/skills/bridge/helpers/*.py` listed in `target_paths`
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/bridge/INDEX.md`
- `groundtruth-kb/tests/fixtures/bridge_index_live_snapshot.md`

The package fixture changes must prove that `DEFERRED` is present in generated bridge protocol text and parsed consistently by packaged helpers.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not add credentials; bridge helper credential scan remains abort mode. | Run helper credential scan and normal scanner-safe writer/pre-commit gates; inspect no secrets in diff. | No waiver. |
| CQ-PATHS-001 | Yes | Keep all live references under `E:\GT-KB`; doctor hard-fail covers legacy-root drift. | Run doctor legacy-root tests and project-root boundary checks. | No waiver. |
| CQ-COMPLEXITY-001 | Yes | Keep new authority resolver and doctor scanner as small pure functions with focused CLI wrappers. | Review source scan output and targeted pytest coverage. | No waiver. |
| CQ-CONSTANTS-001 | Yes | Centralize status tokens and legacy-root patterns in named constants or existing enums. | Ruff plus tests exercise constants through public commands. | No waiver. |
| CQ-SECURITY-001 | Yes | Keep authority command read-only; avoid subprocess shelling and unmanaged path writes. | CLI tests cover JSON output and invalid subject handling; credential scan remains clean. | No waiver. |
| CQ-DOCS-001 | Yes | Update live rules and package templates with matching semantics and approval packets for protected rules. | Template/scaffold tests and narrative artifact evidence check. | No waiver. |
| CQ-TESTS-001 | Yes | Add denial and allowed-path tests for deferral set/clear, resolver, doctor, and helper parsing. | Run pytest commands listed in the verification plan. | No waiver. |
| CQ-LOGGING-001 | Yes | Diagnostics report subject, file, line, and reason without noisy stack traces. | Assert CLI/doctor error payloads include structured fields. | No waiver. |
| CQ-VERIFICATION-001 | Yes | Implementation report carries command evidence and spec-to-test mapping. | Run preflight, clause preflight, pytest, ruff, and narrative evidence checks. | No waiver. |

## Specification-Derived Verification Plan

Tests to add or update:

- T1 body token gate: `DEFERRED` is accepted as a canonical first-line status token and missing owner-decision evidence is rejected. Linked specs: `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`. Target tests: `platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py`, `platform_tests/hooks/test_bridge_author_metadata_gate.py`.
- T2 helper parsing: live bridge helpers parse `DEFERRED` and classify it as non-actionable. Linked spec: `GOV-FILE-BRIDGE-AUTHORITY-001`. Target tests: existing or new helper tests under `platform_tests/skills/`.
- T3 index mutation owner gate: `gt bridge index set-status` rejects `DEFERRED` without owner evidence and accepts a valid versioned `DEFERRED` file with owner evidence. Linked specs: `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`. Target test: `groundtruth-kb/tests/test_cli_bridge_index.py`.
- T4 clear owner gate: transitions away from latest `DEFERRED` fail without owner clear evidence and pass with owner evidence. Linked specs: `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`. Target tests: `platform_tests/scripts/test_gtkb_bridge_writer.py`, `groundtruth-kb/tests/test_cli_bridge_index.py`.
- T5 parser/preflight drift: preflight and audit scripts recognize `DEFERRED` as the latest status and do not inspect an older line as current. Linked specs: `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. Target tests: `groundtruth-kb/tests/test_preflight_checks.py`, `platform_tests/scripts/test_bridge_index_chain_audit.py`.
- T6 authority resolve: `gt authority resolve` returns canonical authority records for bridge, status, project root, role assignment, glossary, doctor, work item, and MemBase aliases. Linked specs: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`. Target test: `groundtruth-kb/tests/test_cli_authority.py`.
- T7 legacy-root doctor: active `E:\Claude-Playground` live-authority references fail doctor; historical/archive references are allowed or informational. Linked spec: `ADR-ISOLATION-APPLICATION-PLACEMENT-001`. Target test: `groundtruth-kb/tests/test_doctor_legacy_root.py`.
- T8 scaffold/template propagation: scaffolded rules/helpers/golden fixtures include and parse `DEFERRED`. Linked specs: `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`. Target test: `groundtruth-kb/tests/test_project_scaffold_bridge_statuses.py`.
- T9 protected narrative approval floor: protected `.claude/rules/*.md` changes cannot be committed without matching approval packets; packets pass when content hash and owner evidence match. Linked specs: `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`. Verification command: `scripts/check_narrative_artifact_evidence.py --staged`.

Commands to run in the implementation report:

```text
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py platform_tests/hooks/test_bridge_author_metadata_gate.py platform_tests/hooks/test_lo_file_safety_gate.py -q --tb=short
python -m pytest platform_tests/scripts/test_bridge_author_metadata.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_bridge_index_chain_audit.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_cli_bridge_index.py groundtruth-kb/tests/test_cli_authority.py groundtruth-kb/tests/test_doctor_legacy_root.py groundtruth-kb/tests/test_preflight_checks.py groundtruth-kb/tests/test_project_scaffold_bridge_statuses.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-deferred-authority-protocol-alignment
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-deferred-authority-protocol-alignment
python scripts/check_narrative_artifact_evidence.py --staged
python -m ruff check .claude/hooks scripts groundtruth-kb/src groundtruth-kb/tests platform_tests
python -m ruff format --check .claude/hooks scripts groundtruth-kb/src groundtruth-kb/tests platform_tests
```

## Acceptance Criteria

1. `DEFERRED` is accepted by all live bridge INDEX/status-line parsers in scope and never falls through to older actionable lines.
2. Versioned `DEFERRED` files start with `DEFERRED`, carry author metadata, and include non-placeholder owner decision evidence.
3. `DEFERRED` remains non-actionable for both Prime Builder and Loyal Opposition.
4. Normal agents cannot set or clear `DEFERRED` through writer/index commands without owner decision evidence.
5. No sidecar mute registry or cached suppression state is created.
6. `gt authority resolve` reads from `config/agent-control/system-interface-map.toml` and resolves required aliases with JSON and human-readable output.
7. `gt project doctor` or the relevant doctor path hard-fails active legacy-root authority references and does not fail historical evidence solely for mentioning `E:\Claude-Playground`.
8. Package templates, scaffold output, and golden fixtures match live `DEFERRED` semantics.
9. Protected narrative rule-file writes have matching approval packets and pass `scripts/check_narrative_artifact_evidence.py --staged`.
10. Spec-derived tests and ruff checks listed above pass.

## Risks / Rollback

- Risk: broad parser updates could miss an obscure ad hoc regex. Mitigation: implementation must start with an inventory scan for status alternations and include the inventory in the implementation report. Any discovered live parser outside `target_paths` must stop implementation and require a revised proposal.
- Risk: owner-only clear enforcement could block legitimate role transitions after a deferral. Mitigation: tests must cover a valid owner-clear path, and the error message must identify the missing owner decision evidence.
- Risk: protected rule-file edits stall on approval packets. Mitigation: implementation can complete code/test/template work first, then present exact rule-file diffs for owner approval packets before protected writes.
- Risk: `gt authority resolve` could become a second authority. Mitigation: it is read-only and resolves from `config/agent-control/system-interface-map.toml`; it does not maintain its own registry.
- Rollback: revert code/template/parser changes and remove the `gt authority resolve` CLI registration. If protected rule files were updated, revert them with matching approval evidence. No database rollback is needed because implementation writes no new DB records.

## Clause Scope Clarification (Not A Bulk Operation)

This is one review packet for one work item, `GTKB-GOV-008`, under one active project authorization. It is not a bulk standing-backlog operation, batch promotion, batch retirement, or batch work-item update. Evidence tokens for clause visibility: inventory, review packet, formal-artifact-approval, approval_packet, work_item, owner decision, specification, ADR, DCL, bridge protocol, versioned DEFERRED file.

## Pre-Filing Preflight

The Codex helper-mediated bridge write path runs `scripts/bridge_applicability_preflight.py --content-file <scratch>` before writing the proposal. Prime Builder must also run the indexed applicability and clause preflights after filing and report the observed outputs to Loyal Opposition.

## Bridge INDEX Maintenance

This proposal is filed as a fresh `Document: gtkb-deferred-authority-protocol-alignment` entry because the prior `gtkb-bridge-dispatcher-deferral-enforcement-repair` thread is VERIFIED. The previous thread remains historical evidence for the parser/actionability repair; this proposal handles the follow-on alignment and authority work.
