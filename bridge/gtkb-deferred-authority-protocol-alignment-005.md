REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-2026-06-03T00-30Z
author_model: GPT-5 Codex
author_model_version: 2026-06-02 runtime
author_model_configuration: Codex Desktop default reasoning
author_metadata_source: explicit Codex proposal filing metadata

# Implementation Proposal - DEFERRED Authority And Protocol Alignment - Revision 005

bridge_kind: implementation_proposal
Document: gtkb-deferred-authority-protocol-alignment
Version: 005
Author: Prime Builder (Codex, harness A)
Date: 2026-06-03 UTC
Responds-To: `bridge/gtkb-deferred-authority-protocol-alignment-004.md`
Recommended commit type: `feat:`

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-008

target_paths: [".claude/rules/file-bridge-protocol.md", ".claude/rules/bridge-essential.md", ".claude/rules/canonical-terminology.md", ".claude/rules/operating-model.md", ".claude/settings.local.json", ".claude/hooks/bridge-compliance-gate.py", ".claude/hooks/lo-file-safety-gate.py", ".claude/skills/bridge/helpers/show_thread_bridge.py", ".claude/skills/bridge/helpers/scan_bridge.py", ".claude/skills/bridge/helpers/revise_bridge.py", ".claude/skills/bridge/helpers/impl_report_bridge.py", ".groundtruth/formal-artifact-approvals/2026-06-02-claude-rules-file-bridge-protocol-md.json", ".groundtruth/formal-artifact-approvals/2026-06-02-claude-rules-bridge-essential-md.json", ".groundtruth/formal-artifact-approvals/2026-06-02-claude-rules-canonical-terminology-md.json", ".groundtruth/formal-artifact-approvals/2026-06-02-claude-rules-operating-model-md.json", "config/agent-control/system-interface-map.toml", "groundtruth-kb/src/groundtruth_kb/bridge/index_mutation.py", "groundtruth-kb/src/groundtruth_kb/project/preflight.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/membase_effective_use_audit.py", "groundtruth-kb/src/groundtruth_kb/reporting/harvest_coverage.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/authority.py", "groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "groundtruth-kb/templates/rules/file-bridge-protocol.md", "groundtruth-kb/templates/rules/bridge-essential.md", "groundtruth-kb/templates/rules/canonical-terminology.md", "groundtruth-kb/templates/skills/bridge/helpers/show_thread_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/bridge/INDEX.md", "groundtruth-kb/tests/fixtures/bridge_index_live_snapshot.md", "scripts/bridge_author_metadata.py", "scripts/gtkb_bridge_writer.py", "scripts/bridge_applicability_preflight.py", "scripts/adr_dcl_clause_preflight.py", "scripts/bridge_index_chain_audit.py", "scripts/bridge_reconciliation_audit.py", "scripts/bridge_work_intent_registry.py", "scripts/check_index_role_intent_sentinel.py", "scripts/bridge_citation_freshness_preflight.py", "scripts/bridge_proposal_pattern_lint.py", "scripts/bridge_proposal_wi_id_collision_check.py", "scripts/backfill_approval_state.py", "scripts/harvest_session_deliberations.py", "scripts/retroactive_harvest_bridge_threads.py", "scripts/session_self_initialization.py", "scripts/spec_to_test_mapper.py", "scripts/run_spec_derived_tests.py", "scripts/rehearse/_bridge_split.py", "platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py", "platform_tests/hooks/test_bridge_author_metadata_gate.py", "platform_tests/hooks/test_lo_file_safety_gate.py", "platform_tests/scripts/test_bridge_author_metadata.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_bridge_index_chain_audit.py", "groundtruth-kb/tests/test_cli_bridge_index.py", "groundtruth-kb/tests/test_cli_authority.py", "groundtruth-kb/tests/test_doctor_legacy_root.py", "groundtruth-kb/tests/test_preflight_checks.py", "groundtruth-kb/tests/test_project_scaffold_bridge_statuses.py"]

## Revision Claim

This revision addresses the sole blocking finding in `bridge/gtkb-deferred-authority-protocol-alignment-004.md`: the `## Requirement Sufficiency` section in `-003` used a free-form sufficient-state sentence that the implementation-start parser classifies as `missing`.

The revision changes the operative sentence to the parser-recognized phrase `Existing requirements sufficient.` and keeps the owner-decision rationale as explanatory text. It carries forward `-003` unchanged on the substantive `-002` correction: `.claude/settings.local.json` remains in `target_paths`, active legacy-root scan scope, remediation requirements, and current-repo doctor smoke evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` remains the canonical bridge queue state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live GT-KB artifacts and authority dependencies remain inside `E:\GT-KB`; `E:\Claude-Playground` is archive-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals must cite relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation reports must map linked specs to executed verification evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decisions, proposals, implementation reports, and verification reports form the durable governance record.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability across owner decisions, status semantics, source changes, tests, and bridge review is required.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - `DEFERRED` is an explicit artifact lifecycle state.
- `GOV-STANDING-BACKLOG-001` - `GTKB-GOV-008` is the tracked single work item; this is not a bulk backlog operation.
- `GOV-ARTIFACT-APPROVAL-001` - protected narrative rule-file updates require approval packets before writes.
- `PB-ARTIFACT-APPROVAL-001` - Prime Builder authority does not waive protected narrative-artifact approval evidence.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - protected narrative-artifact writes must satisfy the narrative/formal approval hook and universal floor.
- `AGENTS.md` Mandatory Project Root Boundary - identifies `E:\Claude-Playground` as archive-only and not a live GT-KB authority location.
- `.claude/rules/project-root-boundary.md` - applies the same mandatory boundary to bridge, dashboard, harness, source, verification, and dependency locations.

## Prior Deliberations

- `DELIB-0873` - prior GO for scoped bridge dispatcher deferral-enforcement repair.
- `DELIB-2363` - GO for `bridge/gtkb-bridge-dispatcher-deferral-enforcement-repair-003.md`; it approved only parser/actionability repair and excluded broader status tooling and owner-mute authority.
- `DELIB-2364` - NO-GO on an earlier stale deferral proposal; it highlighted missing owner authority decisions.
- `bridge/gtkb-bridge-dispatcher-deferral-enforcement-repair-006.md` - VERIFIED the canonical parser/actionability repair for `DEFERRED`.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-PROJECT1-SCOPE` - owner selected Project 1 only.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-SPLIT-SEMANTICS` - owner selected split semantics between indexed `DEFERRED` status and parked drafts.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-OWNER-ONLY-DEFERRAL-AUTHORITY` - owner selected owner-only set and clear authority.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-LEGACY-ROOT-HARD-FAIL` - owner selected hard-fail treatment for active legacy-root live-authority references.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-AUTHORITY-RESOLVE-CLI` - owner selected adding `gt authority resolve`.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-VERSIONED-DEFERRED-FILE` - owner selected versioned `DEFERRED` bridge files.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-LIVE-PLUS-TEMPLATES` - owner selected updating live plus package-template surfaces.
- `DELIB-20260602-GLOSSARY-CLI-SCAN-DEFERRED-ONLY-NO-SLUG-MUTE` - owner selected `DEFERRED` only, with no sidecar mute registry.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02-23-52.md` - prior advisory evidence that `.claude/settings.local.json` is part of the effective startup/runtime environment and contains stale `E:\Claude-Playground` control-surface entries.

## Owner Decisions / Input

This revision uses the same owner-decision basis as `bridge/gtkb-deferred-authority-protocol-alignment-001.md`. No new owner decision is required: the owner already selected hard-fail treatment for active legacy-root references, and this revision applies that decision to a known active local control surface instead of carving out an undocumented exception.

Carried-forward owner decision records: `DELIB-20260602-GLOSSARY-CLI-SCAN-PROJECT1-SCOPE`, `DELIB-20260602-GLOSSARY-CLI-SCAN-SPLIT-SEMANTICS`, `DELIB-20260602-GLOSSARY-CLI-SCAN-OWNER-ONLY-DEFERRAL-AUTHORITY`, `DELIB-20260602-GLOSSARY-CLI-SCAN-LEGACY-ROOT-HARD-FAIL`, `DELIB-20260602-GLOSSARY-CLI-SCAN-AUTHORITY-RESOLVE-CLI`, `DELIB-20260602-GLOSSARY-CLI-SCAN-VERSIONED-DEFERRED-FILE`, `DELIB-20260602-GLOSSARY-CLI-SCAN-LIVE-PLUS-TEMPLATES`, and `DELIB-20260602-GLOSSARY-CLI-SCAN-DEFERRED-ONLY-NO-SLUG-MUTE`.

## Requirement Sufficiency

Existing requirements sufficient.

The cited owner decisions remain sufficient. The `.claude/settings.local.json` issue is not a new policy question; it is a proposal coverage correction required by `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `AGENTS.md`, `.claude/rules/project-root-boundary.md`, and `DELIB-20260602-GLOSSARY-CLI-SCAN-LEGACY-ROOT-HARD-FAIL`.

## Findings Addressed

### F1 - P1: Requirement Sufficiency wording is not parser-recognized

Response: the `## Requirement Sufficiency` section now begins with `Existing requirements sufficient.`, an accepted operative phrase in `scripts/implementation_authorization.py`. The explanatory owner-decision rationale remains after the accepted phrase instead of replacing it.

### F1 - P1: Legacy-root hard-fail scope omits a known active settings surface

Response: `.claude/settings.local.json` is now explicitly in scope.

Implementation must treat `.claude/settings.local.json` as an active local control surface because it influences effective harness permissions and command allowlists. The legacy-root doctor check must scan it, classify current `E:\Claude-Playground` entries as active live-authority references, and report file path, line, matched legacy path, and active-surface rationale.

Implementation must remediate the current `.claude/settings.local.json` entries before filing the implementation report. Acceptable remediation is removal of obsolete legacy-root allowlist/read/destructive command entries, or replacement with in-root `E:\GT-KB` references only when the replacement is still necessary and does not create broader permission than the old entry.

This revision does not choose an exemption and does not authorize an intentional doctor-red state. If implementation discovers an entry that cannot be removed or safely rewritten without owner input, implementation must stop and file a narrower revised bridge proposal rather than leaving the current repo expected-failing.

## Scope Changes

Changed from `-001`: added `.claude/settings.local.json` to `target_paths`; added it to active legacy-root scan scope; required remediation of known `E:\Claude-Playground` entries; added current-repo doctor smoke evidence; coordinated the startup-refactor advisory finding.

Unchanged from `-001`: native indexed `DEFERRED` status semantics, owner-only set and clear authority, no sidecar mute registry, `gt authority resolve`, live plus template/golden propagation, protected narrative-artifact approval requirements, and no new Deliberation Archive record during implementation.

## Proposed Implementation Plan

All implementation plan items from `bridge/gtkb-deferred-authority-protocol-alignment-001.md` remain in scope, with these corrections:

1. In IP-5, include `.claude/settings.local.json` in hard-fail active surfaces along with `.claude/settings.json`, `.codex/hooks.json`, hooks, config, scripts, package source, templates, and fixtures.
2. Before or alongside implementing the doctor check, remediate current `.claude/settings.local.json` legacy-root entries found by:

```text
rg -n "Claude-Playground|//e/Claude-Playground|E:/Claude-Playground|E:\\\\Claude-Playground" .claude/settings.local.json
```

3. Add current-repo doctor smoke evidence, or the narrow legacy-root doctor subcheck, to the implementation report. The observed result after remediation must pass for active legacy-root references in the current checkout.
4. Add focused tests proving `.claude/settings.local.json` is classified as active, not historical/reference, when it contains legacy-root live-authority entries.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not add credentials; do not quote sensitive local setting values beyond path-pattern evidence. | Staged secret scan and bridge credential scan. | No waiver. |
| CQ-PATHS-001 | Yes | Keep live authority paths under `E:\GT-KB`; remove active `E:\Claude-Playground` settings-local references. | Legacy-root doctor tests plus current-repo doctor smoke or subcheck. | No waiver. |
| CQ-COMPLEXITY-001 | Yes | Keep status/parser/doctor/authority logic in small pure helpers where possible. | Focused pytest and review of touched functions. | No waiver. |
| CQ-CONSTANTS-001 | Yes | Centralize status tokens and legacy-root patterns in named constants or existing enums. | Ruff plus tests exercising constants through public commands. | No waiver. |
| CQ-SECURITY-001 | Yes | `gt authority resolve` remains read-only; settings-local remediation removes stale permission surface instead of broadening it. | CLI tests, doctor smoke, and diff review. | No waiver. |
| CQ-DOCS-001 | Yes | Update live rules and package templates with matching semantics and approval packets. | Template/scaffold tests and narrative artifact evidence check. | No waiver. |
| CQ-TESTS-001 | Yes | Add denial/allow tests for deferral set/clear, resolver, doctor, helper parsing, and settings-local active-surface classification. | Pytest targets listed below. | No waiver. |
| CQ-LOGGING-001 | Yes | Diagnostics report subject, file, line, and reason without noisy stack traces. | Assert CLI/doctor error payloads include structured fields. | No waiver. |
| CQ-VERIFICATION-001 | Yes | Implementation report carries command evidence and spec-to-test mapping for every linked surface. | Preflight, clause preflight, pytest, ruff, doctor smoke, and staged checks. | No waiver. |

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001` and indexed `DEFERRED` semantics: run parser/writer/helper tests from `-001`, including body-token, author metadata, bridge writer, bridge index CLI, preflight, and scaffold status tests.
- Owner-only set/clear authority: tests reject setting or clearing `DEFERRED` without owner decision evidence and pass with owner evidence.
- Legacy-root boundary in `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `AGENTS.md`, and `.claude/rules/project-root-boundary.md`: `groundtruth-kb/tests/test_doctor_legacy_root.py` includes `.claude/settings.local.json` active-surface coverage, and current-repo doctor smoke or subcheck passes after remediation.
- NO-GO F1 known surface coverage: pre-remediation `rg` evidence shows known settings-local legacy-root entries; post-remediation `rg` evidence shows no active `.claude/settings.local.json` legacy-root entries.
- Startup-refactor advisory coordination: implementation report cites `STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02-23-52.md` and states this slice resolves the legacy-root portion of that advisory for `.claude/settings.local.json`.
- Protected narrative rule-file floor: rule-file writes are backed by formal approval packets and pass `scripts/check_narrative_artifact_evidence.py --staged`.
- Code quality: run repo-native pytest targets, ruff check, ruff format check, staged secret scan, inventory/narrative/diff checks as applicable to the implemented diff.

Commands to add to the implementation report, in addition to commands from `-001`:

```text
rg -n "Claude-Playground|//e/Claude-Playground|E:/Claude-Playground|E:\\\\Claude-Playground" .claude/settings.local.json
groundtruth-kb\.venv\Scripts\gt.exe project doctor --profile harness-memory
```

If the full doctor command is not the right invocation for this checkout, the implementation may run the narrow legacy-root doctor subcheck, but it must explain the command choice and include a current-repo smoke result for `.claude/settings.local.json`.

## Acceptance Criteria

All acceptance criteria from `-001` remain, with these additions:

1. `.claude/settings.local.json` is included in active legacy-root scan scope and `target_paths`.
2. The implementation removes or safely rewrites current `.claude/settings.local.json` `E:\Claude-Playground` live-authority entries before filing the report.
3. The implementation report includes before/after `rg` evidence for `.claude/settings.local.json`.
4. The current-repo doctor smoke or narrow legacy-root doctor subcheck passes after remediation.
5. The implementation report cites the startup-refactor advisory and states whether its `.claude/settings.local.json` legacy-root finding is resolved fully or whether residual non-legacy-root settings-local risk remains tracked elsewhere.

## Risk And Rollback

- Risk: `.claude/settings.local.json` is local-only and may contain user-specific allowances. Mitigation: remove obsolete legacy-root entries rather than broaden permissions; any non-obvious replacement stops for a revised proposal.
- Risk: the doctor check could flag historical bridge/report evidence. Mitigation: tests preserve the distinction between active surfaces and historical/reference surfaces.
- Risk: the settings-local edit changes effective local harness permissions. Mitigation: the implementation report lists exactly which entries were removed or rewritten and why each was obsolete under the project-root-boundary rule.
- Rollback: restore previous `.claude/settings.local.json` lines only if the owner explicitly requests that local-permission rollback; otherwise rollback source/tooling changes by reverting the implementation commit. No database rollback is required.

## Clause Scope Clarification (Not A Bulk Operation)

This remains one review packet for one work item, `GTKB-GOV-008`, under one active project authorization. It is not a bulk standing-backlog operation, batch promotion, batch retirement, or batch work-item update. Evidence tokens for clause visibility: inventory, review packet, formal-artifact-approval, approval_packet, work_item, owner decision, specification, ADR, DCL, bridge protocol, versioned DEFERRED file.

## Pre-Filing Preflight Subsection

Candidate-content preflights must be run against this completed revision before live filing:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-deferred-authority-protocol-alignment-005.md --bridge-id gtkb-deferred-authority-protocol-alignment
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-deferred-authority-protocol-alignment-005.md --bridge-id gtkb-deferred-authority-protocol-alignment
```

Prime Builder must also run the indexed applicability and clause preflights after filing and report the observed outputs to Loyal Opposition.

## Bridge INDEX Maintenance

This revision is filed as `REVISED: bridge/gtkb-deferred-authority-protocol-alignment-005.md` at the top of the existing `Document: gtkb-deferred-authority-protocol-alignment` entry.
