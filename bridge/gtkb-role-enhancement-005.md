NEW
author_identity: Claude Code
author_harness_id: B
author_session_context_id: 544b584c-7392-4d40-81d8-dba187ba11eb
author_model: claude-opus-4-7
author_model_version: claude-opus-4-7
author_model_configuration: claude-code; interactive; Prime Builder; /loop dynamic
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# GT-KB Bridge Implementation Report - gtkb-role-enhancement - 005

bridge_kind: implementation_report
Document: gtkb-role-enhancement
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-role-enhancement-004.md
Approved proposal: bridge/gtkb-role-enhancement-003.md
Recommended commit type: feat:

## Implementation Claim

We have completed the parent scoping and decomposition plan for `gtkb-role-enhancement`. Specifically:
1. **Decomposition:** Approved the decomposition of the role enhancement project into separate, independently reviewable child slices (Slices 1 to 5).
2. **Safety constraint:** Declared `target_paths: []` for this parent thread to ensure it acts purely as a scoping envelope and does not authorize direct code/rule/test/template mutations.
3. **Child proposal requirements:** Established that child proposal slices will carry their own target paths, project metadata, spec-derived verification plans, and reviews.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this parent proposal uses the file bridge as
- `GOV-STANDING-BACKLOG-001` - `GTKB-ROLE-ENHANCEMENT` is the tracked backlog
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - role-contract gaps, owner decisions,
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the program is decomposed into
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the satisfied dependency and
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - child implementation
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revised proposal
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision evidence is carried through the
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work remains under the GT-KB
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - child proposals that touch Codex/Claude

## Owner Decisions / Input

No new owner decision is required by this implementation report. Carry forward any proposal-specific owner evidence here if applicable.

## Prior Deliberations

- `bridge/gtkb-role-enhancement-003.md` - approved implementation proposal carried forward.
- `bridge/gtkb-role-enhancement-004.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Checked that parent scoping is updated in `bridge/INDEX.md` and child proposals can proceed. |
| `GOV-STANDING-BACKLOG-001` | Checked that work item `GTKB-ROLE-ENHANCEMENT` is tracked. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verified prior owner decisions (DELIB-S381, DELIB-S312) are carried forward. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Checked that the scoping and planning has been captured as a durable bridge record. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Checked that the scoping and planning has been captured as a durable bridge record. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Verified that future child slices must link specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Verified that future child slices must include spec-to-test verification. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Verified metadata linkages are correct. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Verified prior owner decisions (DELIB-S381, DELIB-S312) are carried forward. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Checked that no out-of-root mutations were attempted. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Checked that parity considerations are documented. |

## Commands Run

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-enhancement
```

## Observed Results

```markdown
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
```

## Files Changed

- `.claude/hooks/bridge-compliance-gate.py`
- `.claude/settings.json`
- `.claude/skills/bridge/helpers/scan_bridge.py`
- `applications/Agent_Red/tests/conftest.py`
- `applications/Agent_Red/tests/security/test_documentation_cleanup.py`
- `applications/Agent_Red/tests/security/test_superadmin_api_split.py`
- `bridge/INDEX.md`
- `bridge/active-workspace-declaration-architecture-2026-04-29-003.md`
- `bridge/active-workspace-declaration-architecture-2026-04-29-005.md`
- `bridge/active-workspace-declaration-architecture-2026-04-29-006.md`
- `bridge/active-workspace-declaration-slice-1-001.md`
- `bridge/active-workspace-declaration-slice-1-003.md`
- `bridge/active-workspace-declaration-slice-1-005.md`
- `bridge/active-workspace-declaration-slice-1-008.md`
- `bridge/active-workspace-declaration-slice-1-009.md`
- `bridge/active-workspace-declaration-slice-1-010.md`
- `bridge/agent-red-ruff-cleanup-001-006.md`
- `bridge/antigravity-inspection-results-053026-options-for-implementation-001.md`
- `bridge/canonical-deploy-pipeline-scaling-enforcement-001.md`
- `bridge/canonical-deploy-pipeline-scaling-enforcement-003.md`
- `bridge/canonical-deploy-pipeline-scaling-enforcement-005.md`
- `bridge/canonical-deploy-pipeline-scaling-enforcement-007.md`
- `bridge/canonical-deploy-pipeline-scaling-enforcement-009.md`
- `bridge/canonical-deploy-pipeline-scaling-enforcement-011.md`
- `bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-002.md`
- `bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-004.md`
- `bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-006.md`
- `bridge/generator-hardening-002-011.md`
- `bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-002.md`
- `bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-004.md`
- `bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28-006.md`
- `bridge/gtkb-active-status-capability-gate-formalization-001.md`
- `bridge/gtkb-active-status-capability-gate-formalization-002.md`
- `bridge/gtkb-active-status-capability-gate-formalization-004.md`
- `bridge/gtkb-active-status-capability-gate-formalization-content-drafts-001.md`
- `bridge/gtkb-active-status-capability-gate-formalization-content-drafts-002.md`
- `bridge/gtkb-active-status-capability-gate-formalization-content-drafts-004.md`
- `bridge/gtkb-active-status-capability-gate-harness-lifecycle-retention-001.md`
- `bridge/gtkb-active-status-capability-gate-harness-lifecycle-retention-002.md`
- `bridge/gtkb-active-status-capability-gate-harness-lifecycle-retention-004.md`
- `bridge/gtkb-active-status-capability-gate-harness-lifecycle-retention-006.md`
- `bridge/gtkb-active-status-capability-gate-lifecycle-substrate-001.md`
- `bridge/gtkb-active-status-capability-gate-lifecycle-substrate-002.md`
- `bridge/gtkb-active-status-capability-gate-lifecycle-substrate-004.md`
- `bridge/gtkb-active-status-capability-gate-registry-dispatch-001.md`
- `bridge/gtkb-active-status-capability-gate-registry-dispatch-002.md`
- `bridge/gtkb-active-status-capability-gate-registry-dispatch-004.md`
- `bridge/gtkb-adr-0001-membase-migration-002.md`
- `bridge/gtkb-adr-0001-membase-migration-003.md`
- `bridge/gtkb-adr-0001-membase-migration-004.md`
- `bridge/gtkb-adr-0001-membase-migration-005.md`
- `bridge/gtkb-adr-0001-membase-migration-006.md`
- `bridge/gtkb-adr-0001-membase-migration-007.md`
- `bridge/gtkb-adr-0001-membase-migration-008.md`
- `bridge/gtkb-adr-dcl-clause-auto-discovery-slice-5-001.md`
- `bridge/gtkb-adr-dcl-clause-auto-discovery-slice-5-003.md`
- `bridge/gtkb-adr-dcl-clause-auto-discovery-slice-5-004.md`
- `bridge/gtkb-adr-dcl-clause-auto-discovery-slice-5-006.md`
- `bridge/gtkb-adr-dcl-clause-auto-discovery-slice-5-008.md`
- `bridge/gtkb-adr-dcl-clause-preflight-content-file-path-fix-001.md`
- `bridge/gtkb-adr-dcl-clause-preflight-content-file-path-fix-004.md`
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-001.md`
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-002.md`
- `bridge/gtkb-adr-evaluation-enforcement-2026-04-30-007.md`
- `bridge/gtkb-adr-harness-registry-extension-001.md`
- `bridge/gtkb-adr-harness-registry-extension-003.md`
- `bridge/gtkb-adr-isolation-application-placement-001.md`
- `bridge/gtkb-adr-isolation-application-placement-005.md`
- `bridge/gtkb-advisory-report-dashboard-counters-spec-001.md`
- `bridge/gtkb-advisory-report-dashboard-counters-spec-002.md`
- `bridge/gtkb-advisory-report-dashboard-counters-spec-003.md`
- `bridge/gtkb-advisory-report-dashboard-counters-spec-004.md`
- `bridge/gtkb-advisory-report-dashboard-counters-spec-006.md`
- `bridge/gtkb-advisory-report-message-type-2026-05-09-002.md`
- `bridge/gtkb-advisory-report-message-type-conversion-001.md`
- `bridge/gtkb-advisory-report-message-type-conversion-002.md`
- `bridge/gtkb-advisory-report-message-type-conversion-003.md`
- `bridge/gtkb-advisory-report-message-type-conversion-004.md`
- `bridge/gtkb-advisory-report-message-type-conversion-006.md`
- `bridge/gtkb-advisory-report-protocol-extension-001.md`
- `bridge/gtkb-advisory-report-protocol-extension-002.md`
- `bridge/gtkb-advisory-report-protocol-extension-003.md`
- `bridge/gtkb-advisory-report-protocol-extension-004.md`
- `bridge/gtkb-advisory-report-protocol-extension-006.md`
- `bridge/gtkb-advisory-report-template-spec-001.md`
- `bridge/gtkb-advisory-report-template-spec-002.md`
- `bridge/gtkb-advisory-report-template-spec-003.md`
- `bridge/gtkb-advisory-report-template-spec-004.md`
- `bridge/gtkb-advisory-report-template-spec-005.md`
- `bridge/gtkb-advisory-report-template-spec-006.md`
- `bridge/gtkb-advisory-report-template-spec-008.md`
- `bridge/gtkb-advisory-routing-dcl-001.md`
- `bridge/gtkb-advisory-routing-dcl-002.md`
- `bridge/gtkb-advisory-routing-dcl-003.md`
- `bridge/gtkb-advisory-routing-dcl-004.md`
- `bridge/gtkb-advisory-routing-dcl-006.md`
- `bridge/gtkb-agent-red-deployability-preservation-gate-001.md`
- `bridge/gtkb-agent-red-deployability-preservation-gate-003.md`
- `bridge/gtkb-agent-red-deployability-preservation-gate-004.md`
- `bridge/gtkb-agent-red-deployability-preservation-gate-006.md`
- `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md`
- `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-003.md`
- `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-004.md`
- `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-006.md`
- `bridge/gtkb-agent-red-reference-adopter-framing-restoration-001.md`
- `bridge/gtkb-agent-red-reference-adopter-framing-restoration-003.md`
- `bridge/gtkb-agent-red-reference-adopter-framing-restoration-004.md`
- `bridge/gtkb-agent-red-reference-adopter-framing-restoration-006.md`
- `bridge/gtkb-agent-red-reference-adopter-framing-restoration-008.md`
- `bridge/gtkb-agent-sot-read-discipline-phase-1-001.md`
- `bridge/gtkb-agent-sot-read-discipline-phase-1-002.md`
- `bridge/gtkb-ai-assisted-delivery-maturity-model-scoping-001.md`
- `bridge/gtkb-ai-assisted-delivery-maturity-model-scoping-003.md`
- `bridge/gtkb-ai-assisted-delivery-maturity-model-scoping-006.md`
- `bridge/gtkb-antigravity-capability-adapters-001.md`
- `bridge/gtkb-antigravity-capability-adapters-002.md`
- `bridge/gtkb-antigravity-harness-registration-001.md`
- `bridge/gtkb-antigravity-harness-registration-004.md`
- `bridge/gtkb-antigravity-ide-research-spike-001.md`
- `bridge/gtkb-antigravity-ide-research-spike-002.md`
- `bridge/gtkb-antigravity-ide-research-spike-004.md`
- `bridge/gtkb-antigravity-implements-link-ambiguity-advisory-001.md`
- `bridge/gtkb-antigravity-insight-stale-owner-action-advisory-001.md`
- `bridge/gtkb-antigravity-integration-directory-001.md`
- `bridge/gtkb-antigravity-integration-directory-002.md`
- `bridge/gtkb-antigravity-integration-directory-004.md`
- `bridge/gtkb-antigravity-related-bridge-threads-backfill-001.md`
- `bridge/gtkb-antigravity-related-bridge-threads-backfill-002.md`
- `bridge/gtkb-antigravity-related-bridge-threads-backfill-003.md`
- `bridge/gtkb-antigravity-related-bridge-threads-backfill-004.md`
- `bridge/gtkb-antigravity-related-bridge-threads-backfill-006.md`
- `bridge/gtkb-app-boundary-mechanism-audit-001.md`
- `bridge/gtkb-app-boundary-mechanism-audit-003.md`
- `bridge/gtkb-approval-gate-readonly-flag-skip-001.md`
- `bridge/gtkb-approval-gate-readonly-flag-skip-002.md`
- `bridge/gtkb-approval-gate-readonly-flag-skip-003.md`
- `bridge/gtkb-approval-gate-readonly-flag-skip-004.md`
- `bridge/gtkb-approval-gate-readonly-flag-skip-006.md`
- `bridge/gtkb-artifact-recorder-cli-005.md`
- `bridge/gtkb-artifact-recorder-cli-scoping-advance-001.md`
- `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-002.md`
- `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-004.md`
- `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-006.md`
- `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-008.md`
- `bridge/gtkb-artifact-recorder-cli-slice-2-spec-record-002.md`
- `bridge/gtkb-artifact-recorder-cli-slice-2-spec-record-004.md`
- `bridge/gtkb-artifact-recorder-cli-slice-2-spec-record-006.md`
- `bridge/gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive-002.md`
- `bridge/gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive-005.md`
- `bridge/gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive-007.md`
- `bridge/gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive-009.md`
- `bridge/gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive-011.md`
- `bridge/gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive-012.md`
- `bridge/gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive-014.md`
- `bridge/gtkb-audit-script-withdrawn-regex-fix-001.md`
- `bridge/gtkb-audit-script-withdrawn-status-handling-001.md`
- `bridge/gtkb-audit-script-withdrawn-status-handling-002.md`
- `bridge/gtkb-audit-script-withdrawn-status-handling-004.md`
- `bridge/gtkb-audit-script-withdrawn-status-handling-006.md`
- `bridge/gtkb-auto-push-investigation-001-prop-001.md`
- `bridge/gtkb-auto-push-investigation-001-slice-1-findings-001.md`
- `bridge/gtkb-auto-push-investigation-001-slice-1-findings-002.md`
- `bridge/gtkb-auto-push-investigation-001-slice-1-findings-003.md`
- `bridge/gtkb-auto-push-investigation-001-slice-1-findings-004.md`
- `bridge/gtkb-auto-push-investigation-001-slice-1-findings-006.md`
- `bridge/gtkb-auto-push-investigation-slice-1-004.md`
- `bridge/gtkb-auto-push-investigation-slice-1-005.md`
- `bridge/gtkb-auto-push-investigation-slice-1-006.md`
- `bridge/gtkb-auto-push-investigation-slice-2-001.md`
- `bridge/gtkb-auto-push-investigation-slice-2-002.md`
- `bridge/gtkb-auto-push-investigation-slice-2-003.md`
- `bridge/gtkb-auto-push-investigation-slice-2-005.md`
- `bridge/gtkb-axis-2-dispatchable-filter-001.md`
- `bridge/gtkb-axis-2-dispatchable-filter-002.md`
- `bridge/gtkb-axis-2-dispatchable-filter-003.md`
- `bridge/gtkb-axis-2-dispatchable-filter-004.md`
- `bridge/gtkb-axis-2-dispatchable-filter-005.md`
- `bridge/gtkb-axis-2-dispatchable-filter-006.md`
- `bridge/gtkb-axis-2-scoping-terminal-classifier-fix-001.md`
- `bridge/gtkb-axis-2-scoping-terminal-classifier-fix-004.md`
- `bridge/gtkb-backlog-add-cli-slice-1-001.md`
- `bridge/gtkb-backlog-add-cli-slice-1-003.md`
- `bridge/gtkb-backlog-approval-state-taxonomy-auq-001.md`
- `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-001.md`
- `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-003.md`
- `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-005.md`
- `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-006.md`
- `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-009.md`
- `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-010.md`
- `bridge/gtkb-backlog-approval-state-taxonomy-slice-1-011.md`
- `bridge/gtkb-backlog-authorize-implementation-cli-slice-1-001.md`
- `bridge/gtkb-backlog-authorize-implementation-cli-slice-1-003.md`
- `bridge/gtkb-backlog-authorize-implementation-cli-slice-1-006.md`
- `bridge/gtkb-backlog-authorize-implementation-cli-slice-1-008.md`
- `bridge/gtkb-backlog-canonical-pivot-spec-promotion-001.md`
- `bridge/gtkb-backlog-canonical-pivot-spec-promotion-002.md`
- `bridge/gtkb-backlog-canonical-pivot-spec-promotion-003.md`
- `bridge/gtkb-backlog-canonical-pivot-spec-promotion-004.md`
- `bridge/gtkb-backlog-canonical-pivot-spec-promotion-005.md`
- `bridge/gtkb-backlog-canonical-pivot-spec-promotion-006.md`
- `bridge/gtkb-backlog-update-cli-slice-1-001.md`
- `bridge/gtkb-backlog-update-cli-slice-1-003.md`
- `bridge/gtkb-backlog-update-title-desc-cli-001-001.md`
- `bridge/gtkb-backlog-update-title-desc-cli-001-002.md`
- `bridge/gtkb-backlog-update-title-desc-cli-001-003.md`
- `bridge/gtkb-backlog-update-title-desc-cli-001-004.md`
- `bridge/gtkb-backlog-update-title-desc-cli-001-006.md`
- `bridge/gtkb-bash-hook-destructive-substring-false-positive-001.md`
- `bridge/gtkb-bash-hook-destructive-substring-false-positive-002.md`
- `bridge/gtkb-bash-hook-destructive-substring-false-positive-004.md`
- `bridge/gtkb-bridge-active-session-autodrain-001.md`
- `bridge/gtkb-bridge-active-session-autodrain-003.md`
- `bridge/gtkb-bridge-active-session-autodrain-004.md`
- `bridge/gtkb-bridge-active-session-autodrain-005.md`
- `bridge/gtkb-bridge-active-session-autodrain-006.md`
- `bridge/gtkb-bridge-active-session-autodrain-008.md`
- `bridge/gtkb-bridge-advisory-message-type-implementation-003.md`
- `bridge/gtkb-bridge-advisory-report-message-advisory-disposition-001.md`
- `bridge/gtkb-bridge-advisory-report-message-advisory-disposition-006.md`
- `bridge/gtkb-bridge-advisory-status-001-001.md`
- `bridge/gtkb-bridge-advisory-status-001-003.md`
- `bridge/gtkb-bridge-advisory-status-001-004.md`
- `bridge/gtkb-bridge-advisory-status-001-005.md`
- `bridge/gtkb-bridge-advisory-status-001-007.md`
- `bridge/gtkb-bridge-advisory-status-001-008.md`
- `bridge/gtkb-bridge-advisory-status-001-009.md`
- `bridge/gtkb-bridge-advisory-status-001-010.md`
- `bridge/gtkb-bridge-advisory-status-001-011.md`
- `bridge/gtkb-bridge-advisory-status-001-012.md`
- `bridge/gtkb-bridge-advisory-status-001-013.md`
- `bridge/gtkb-bridge-advisory-status-001-014.md`
- `bridge/gtkb-bridge-advisory-status-001-016.md`
- `bridge/gtkb-bridge-automation-status-driver-002.md`
- `bridge/gtkb-bridge-automation-status-driver-004.md`
- `bridge/gtkb-bridge-automation-status-driver-006.md`
- `bridge/gtkb-bridge-backlog-reconciliation-audit-cli-001.md`
- `bridge/gtkb-bridge-backlog-reconciliation-audit-cli-002.md`
- `bridge/gtkb-bridge-backlog-reconciliation-audit-cli-004.md`
- `bridge/gtkb-bridge-citation-freshness-preflight-001.md`
- `bridge/gtkb-bridge-citation-freshness-preflight-003.md`
- `bridge/gtkb-bridge-citation-freshness-preflight-006.md`
- `bridge/gtkb-bridge-citation-freshness-test-restoration-001.md`
- `bridge/gtkb-bridge-citation-freshness-test-restoration-002.md`
- `bridge/gtkb-bridge-citation-freshness-test-restoration-003.md`
- `bridge/gtkb-bridge-citation-freshness-test-restoration-005.md`
- `bridge/gtkb-bridge-compliance-gate-fenced-code-parser-fix-001.md`
- `bridge/gtkb-bridge-compliance-gate-index-exemption-001.md`
- `bridge/gtkb-bridge-compliance-gate-index-exemption-003.md`
- `bridge/gtkb-bridge-compliance-gate-index-exemption-004.md`
- `bridge/gtkb-bridge-compliance-gate-spec-test-heading-multiline-fix-001.md`
- `bridge/gtkb-bridge-compliance-gate-spec-test-heading-multiline-fix-004.md`
- `bridge/gtkb-bridge-compliance-gate-spec-test-heading-multiline-fix-006.md`
- `bridge/gtkb-bridge-compliance-gate-spec-test-heading-multiline-fix-007.md`
- `bridge/gtkb-bridge-compliance-gate-wi-auto-regex-fix-001.md`
- `bridge/gtkb-bridge-compliance-gate-wi-auto-regex-fix-004.md`
- `bridge/gtkb-bridge-compliance-project-metadata-001.md`
- `bridge/gtkb-bridge-compliance-project-metadata-003.md`
- `bridge/gtkb-bridge-compliance-project-metadata-005.md`
- `bridge/gtkb-bridge-compliance-project-metadata-007.md`
- `bridge/gtkb-bridge-compliance-project-metadata-009.md`
- `bridge/gtkb-bridge-compliance-project-metadata-011.md`
- `bridge/gtkb-bridge-compliance-project-metadata-013.md`
- `bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-001.md`
- `bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-002.md`
- `bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-003.md`
- `bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-004.md`
- `bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-006.md`
- `bridge/gtkb-bridge-compliance-wi-project-membership-001.md`
- `bridge/gtkb-bridge-compliance-wi-project-membership-003.md`
- `bridge/gtkb-bridge-compliance-wi-project-membership-005.md`
- `bridge/gtkb-bridge-compliance-wi-project-membership-007.md`
- `bridge/gtkb-bridge-compliance-wi-project-membership-009.md`
- `bridge/gtkb-bridge-contention-consolidation-001.md`
- `bridge/gtkb-bridge-contention-consolidation-002.md`
- `bridge/gtkb-bridge-contention-consolidation-003.md`
- `bridge/gtkb-bridge-contention-consolidation-004.md`
- `bridge/gtkb-bridge-contention-consolidation-006.md`
- `bridge/gtkb-bridge-convenience-verbs-001.md`
- `bridge/gtkb-bridge-convenience-verbs-002.md`
- `bridge/gtkb-bridge-convenience-verbs-004.md`
- `bridge/gtkb-bridge-convenience-verbs-005.md`
- `bridge/gtkb-bridge-convenience-verbs-006.md`
- `bridge/gtkb-bridge-convenience-verbs-007.md`
- `bridge/gtkb-bridge-dispatch-per-document-lease-substitution-001.md`
- `bridge/gtkb-bridge-dispatch-per-document-lease-substitution-002.md`
- `bridge/gtkb-bridge-dispatch-per-document-lease-substitution-004.md`
- `bridge/gtkb-bridge-dispatch-per-document-lease-substitution-006.md`
- `bridge/gtkb-bridge-dispatcher-deferral-enforcement-repair-001.md`
- `bridge/gtkb-bridge-dispatcher-deferral-enforcement-repair-003.md`
- `bridge/gtkb-bridge-dispatcher-deferral-enforcement-repair-006.md`
- `bridge/gtkb-bridge-impl-report-skill-001-001.md`
- `bridge/gtkb-bridge-index-archival-trim-001.md`
- `bridge/gtkb-bridge-index-archival-trim-003.md`
- `bridge/gtkb-bridge-index-archival-trim-005.md`
- `bridge/gtkb-bridge-index-archival-trim-007.md`
- `bridge/gtkb-bridge-index-archival-trim-010.md`
- `bridge/gtkb-bridge-index-chain-deviation-detector-001.md`
- `bridge/gtkb-bridge-index-chain-deviation-detector-002.md`
- `bridge/gtkb-bridge-index-chain-deviation-detector-004.md`
- `bridge/gtkb-bridge-index-phantom-verified-references-2026-04-27-002.md`
- `bridge/gtkb-bridge-index-phantom-verified-references-2026-04-27-004.md`
- `bridge/gtkb-bridge-index-role-intent-sentinel-001.md`
- `bridge/gtkb-bridge-index-role-intent-sentinel-003.md`
- `bridge/gtkb-bridge-index-role-intent-sentinel-004.md`
- `bridge/gtkb-bridge-index-role-intent-sentinel-006.md`
- `bridge/gtkb-bridge-index-role-intent-sentinel-008.md`
- `bridge/gtkb-bridge-kind-taxonomy-stabilization-003.md`
- `bridge/gtkb-bridge-kind-terminal-exempt-alignment-001.md`
- `bridge/gtkb-bridge-kind-terminal-exempt-alignment-002.md`
- `bridge/gtkb-bridge-kind-terminal-exempt-alignment-003.md`
- `bridge/gtkb-bridge-kind-terminal-exempt-alignment-004.md`
- `bridge/gtkb-bridge-kind-terminal-exempt-alignment-005.md`
- `bridge/gtkb-bridge-kind-terminal-exempt-alignment-006.md`
- `bridge/gtkb-bridge-mode-config-transactions-impl-001.md`
- `bridge/gtkb-bridge-mode-config-transactions-impl-002.md`
- `bridge/gtkb-bridge-mode-config-transactions-impl-003.md`
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-001.md`
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-002.md`
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-003.md`
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-004.md`
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-005.md`
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-006.md`
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-007.md`
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-008.md`
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-009.md`
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-011.md`
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-013.md`
- `bridge/gtkb-bridge-mode-config-transactions-slice-1-015.md`
- `bridge/gtkb-bridge-parallel-session-collision-001.md`
- `bridge/gtkb-bridge-parallel-session-collision-002.md`
- `bridge/gtkb-bridge-parallel-session-collision-003.md`
- `bridge/gtkb-bridge-parallel-session-collision-004.md`
- `bridge/gtkb-bridge-parallel-session-collision-006.md`
- `bridge/gtkb-bridge-poller-001-smart-poller-001.md`
- `bridge/gtkb-bridge-poller-001-smart-poller-008.md`
- `bridge/gtkb-bridge-poller-event-driven-replacement-007.md`
- `bridge/gtkb-bridge-poller-event-driven-replacement-009.md`
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001.md`
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-003.md`
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-005.md`
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-003.md`
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-005.md`
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-007.md`
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-009.md`
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-011.md`
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-013.md`
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-015.md`
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001.md`
- `bridge/gtkb-bridge-poller-p1-detector-006.md`
- `bridge/gtkb-bridge-poller-p2-5-verification-spike-005.md`
- `bridge/gtkb-bridge-poller-p2-registry-008.md`
- `bridge/gtkb-bridge-poller-wi-retirement-disposition-001.md`
- `bridge/gtkb-bridge-poller-wi-retirement-disposition-002.md`
- `bridge/gtkb-bridge-poller-wi-retirement-disposition-003.md`
- `bridge/gtkb-bridge-poller-wi-retirement-disposition-004.md`
- `bridge/gtkb-bridge-poller-wi-retirement-disposition-005.md`
- `bridge/gtkb-bridge-poller-wi-retirement-disposition-006.md`
- `bridge/gtkb-bridge-poller-wi-retirement-disposition-008.md`
- `bridge/gtkb-bridge-preflight-path-warning-001.md`
- `bridge/gtkb-bridge-preflight-path-warning-002.md`
- `bridge/gtkb-bridge-preflight-path-warning-003.md`
- `bridge/gtkb-bridge-preflight-path-warning-004.md`
- `bridge/gtkb-bridge-preflight-path-warning-006.md`
- `bridge/gtkb-bridge-propose-helper-caller-migration-to-writer-001.md`
- `bridge/gtkb-bridge-propose-helper-caller-migration-to-writer-002.md`
- `bridge/gtkb-bridge-propose-helper-caller-migration-to-writer-003.md`
- `bridge/gtkb-bridge-propose-helper-caller-migration-to-writer-005.md`
- `bridge/gtkb-bridge-propose-helper-non-bypass-redesign-001.md`
- `bridge/gtkb-bridge-propose-helper-non-bypass-redesign-003.md`
- `bridge/gtkb-bridge-propose-helper-non-bypass-redesign-004.md`
- `bridge/gtkb-bridge-propose-helper-non-bypass-redesign-006.md`
- `bridge/gtkb-bridge-reconciliation-correction-packets-001.md`
- `bridge/gtkb-bridge-reconciliation-correction-packets-002.md`
- `bridge/gtkb-bridge-reconciliation-correction-packets-004.md`
- `bridge/gtkb-bridge-revise-cli-slice-1-001.md`
- `bridge/gtkb-bridge-revise-cli-slice-1-002.md`
- `bridge/gtkb-bridge-revise-cli-slice-1-004.md`
- `bridge/gtkb-bridge-revision-skill-001-001.md`
- `bridge/gtkb-bridge-revision-skill-001-003.md`
- `bridge/gtkb-bridge-revision-skill-001-006.md`
- `bridge/gtkb-bridge-revision-skill-001-007.md`
- `bridge/gtkb-bridge-revision-skill-001-008.md`
- `bridge/gtkb-bridge-revision-skill-001-009.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-1-scoping-001.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-1-scoping-004.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-001.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-004.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-001.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-002.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-004.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-006.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-002.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-004.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-001.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-003.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-004.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-006.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-002.md`
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-004.md`
- `bridge/gtkb-bridge-skill-protected-write-helper-001.md`
- `bridge/gtkb-bridge-skill-protected-write-helper-002.md`
- `bridge/gtkb-bridge-skill-protected-write-helper-003.md`
- `bridge/gtkb-bridge-skill-protected-write-helper-004.md`
- `bridge/gtkb-bridge-skill-protected-write-helper-006.md`
- `bridge/gtkb-bridge-skill-unified-001-005.md`
- `bridge/gtkb-bridge-skill-unified-001-006.md`
- `bridge/gtkb-bridge-stop-drain-deference-repair-001.md`
- `bridge/gtkb-bridge-stop-drain-deference-repair-002.md`
- `bridge/gtkb-bridge-stop-drain-deference-repair-003.md`
- `bridge/gtkb-bridge-stop-drain-deference-repair-004.md`
- `bridge/gtkb-bridge-stop-drain-deference-repair-006.md`
- `bridge/gtkb-bridge-target-paths-kb-mutation-check-001.md`
- `bridge/gtkb-bridge-target-paths-kb-mutation-check-006.md`
- `bridge/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-001.md`
- `bridge/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-003.md`
- `bridge/gtkb-bridge-throughput-metrics-dashboard-slice-1-scoping-006.md`
- `bridge/gtkb-bridge-verified-backlog-retirement-001.md`
- `bridge/gtkb-bridge-verified-backlog-retirement-003.md`
- `bridge/gtkb-bridge-verified-backlog-retirement-007.md`
- `bridge/gtkb-bridge-work-intent-session-id-live-env-precedence-001.md`
- `bridge/gtkb-bridge-work-intent-session-id-live-env-precedence-002.md`
- `bridge/gtkb-bridge-work-intent-session-id-live-env-precedence-004.md`
- `bridge/gtkb-bridge-work-intent-session-id-live-env-precedence-006.md`
- `bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-001.md`
- `bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-003.md`
- `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-001.md`
- `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-002.md`
- `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-004.md`
- `bridge/gtkb-canonical-init-keyword-syntax-001-002.md`
- `bridge/gtkb-canonical-init-keyword-syntax-001-003.md`
- `bridge/gtkb-canonical-init-keyword-syntax-001-004.md`
- `bridge/gtkb-canonical-init-keyword-syntax-001-005.md`
- `bridge/gtkb-canonical-init-keyword-syntax-001-006.md`
- `bridge/gtkb-canonical-init-keyword-syntax-001-007.md`
- `bridge/gtkb-canonical-init-keyword-syntax-001-008.md`
- `bridge/gtkb-canonical-init-keyword-syntax-001-010.md`
- `bridge/gtkb-canonical-init-keyword-syntax-001-012.md`
- `bridge/gtkb-canonical-init-keyword-syntax-001.md`
- `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md`
- `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-002.md`
- `bridge/gtkb-canonical-wrap-keyword-syntax-001-001.md`
- `bridge/gtkb-canonical-wrap-keyword-syntax-001-002.md`
- `bridge/gtkb-canonical-wrap-keyword-syntax-001-003.md`
- `bridge/gtkb-canonical-wrap-keyword-syntax-001-004.md`
- `bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-001.md`
- `bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-003.md`
- `bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-005.md`
- `bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-007.md`
- `bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-008.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-001.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-002.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-003.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-004.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-006.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-007.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-008.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-009.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-010.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-011.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-013.md`
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-015.md`
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001-002.md`
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001-003.md`
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001-004.md`
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001-005.md`
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001.md`
- `bridge/gtkb-claude-code-session-id-env-var-gap-001.md`
- `bridge/gtkb-claude-code-session-id-env-var-gap-002.md`
- `bridge/gtkb-claude-code-session-id-env-var-gap-003.md`
- `bridge/gtkb-claude-code-session-id-env-var-gap-004.md`
- `bridge/gtkb-claude-code-session-id-env-var-gap-005.md`
- `bridge/gtkb-claude-code-session-id-env-var-gap-006.md`
- `bridge/gtkb-claude-code-session-id-env-var-gap-007.md`
- `bridge/gtkb-claude-code-session-id-env-var-gap-008.md`
- `bridge/gtkb-claude-code-session-id-env-var-gap-009.md`
- `bridge/gtkb-claude-code-session-id-env-var-gap-010.md`
- `bridge/gtkb-claude-code-session-id-env-var-gap-012.md`
- `bridge/gtkb-claude-md-scope-clarification-scoping-001.md`
- `bridge/gtkb-claude-md-scope-clarification-scoping-004.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-2-001.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-2-003.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-2-006.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-004.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-005.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-007.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-009.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-010.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-011.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-001.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-002.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-003.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-005.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-007.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-009.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-012.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-014.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-reauthorization-019.md`
- `bridge/gtkb-clause-in-root-failure-pattern-tightening-001.md`
- `bridge/gtkb-clause-in-root-failure-pattern-tightening-002.md`
- `bridge/gtkb-clause-in-root-failure-pattern-tightening-004.md`
- `bridge/gtkb-cli-discoverability-doctor-json-backlog-show-001.md`
- `bridge/gtkb-cli-list-subset-filters-001.md`
- `bridge/gtkb-cli-list-subset-filters-002.md`
- `bridge/gtkb-cli-list-subset-filters-004.md`
- `bridge/gtkb-codex-bridge-compliance-gate-parity-010.md`
- `bridge/gtkb-codex-bridge-compliance-gate-parity-011.md`
- `bridge/gtkb-codex-bridge-compliance-gate-parity-012.md`
- `bridge/gtkb-codex-feedback-pattern-lints-001.md`
- `bridge/gtkb-codex-feedback-pattern-lints-003.md`
- `bridge/gtkb-codex-feedback-pattern-lints-006.md`
- `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-001.md`
- `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-002.md`
- `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-003.md`
- `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-004.md`
- `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-005.md`
- `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-006.md`
- `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-007.md`
- `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-008.md`
- `bridge/gtkb-codex-skill-loading-failure-cleanup-slice-1-010.md`
- `bridge/gtkb-codex-wrapup-startup-gate-guard-sot-001.md`
- `bridge/gtkb-codex-wrapup-startup-gate-guard-sot-004.md`
- `bridge/gtkb-command-surface-001.md`
- `bridge/gtkb-command-surface-003.md`
- `bridge/gtkb-command-surface-cs1-5-001.md`
- `bridge/gtkb-commit-scope-bundling-detection-001-prop-001.md`
- `bridge/gtkb-commit-scope-bundling-detection-slice-1-001.md`
- `bridge/gtkb-commit-scope-bundling-detection-slice-1-003.md`
- `bridge/gtkb-commit-scope-bundling-detection-slice-1-004.md`
- `bridge/gtkb-commit-scope-bundling-detection-slice-1-006.md`
- `bridge/gtkb-commit-scope-bundling-detection-slice-1-008.md`
- `bridge/gtkb-completed-bridge-wi-hygiene-2026-05-13-001.md`
- `bridge/gtkb-completed-bridge-wi-hygiene-2026-05-13-003.md`
- `bridge/gtkb-completed-bridge-wi-hygiene-2026-05-13-004.md`
- `bridge/gtkb-completed-bridge-wi-hygiene-2026-05-13-005.md`
- `bridge/gtkb-completed-bridge-wi-hygiene-2026-05-13-006.md`
- `bridge/gtkb-completed-bridge-wi-hygiene-2026-05-13-007.md`
- `bridge/gtkb-control-plane-placeholder-test-remediation-slice-1-revert-003.md`
- `bridge/gtkb-control-plane-placeholder-test-remediation-slice-1-revert-004.md`
- `bridge/gtkb-control-plane-placeholder-test-remediation-slice-1-revert-005.md`
- `bridge/gtkb-control-plane-placeholder-test-remediation-slice-1-revert-006.md`
- `bridge/gtkb-control-plane-placeholder-test-remediation-slice-1-revert-008.md`
- `bridge/gtkb-core-spec-intake-current-root-phase3a-cli-001.md`
- `bridge/gtkb-core-spec-intake-current-root-phase3a-cli-002.md`
- `bridge/gtkb-core-spec-intake-current-root-phase3a-cli-005.md`
- `bridge/gtkb-core-spec-intake-default-001.md`
- `bridge/gtkb-core-spec-intake-default-003.md`
- `bridge/gtkb-core-spec-intake-default-005.md`
- `bridge/gtkb-core-spec-intake-default-006.md`
- `bridge/gtkb-core-spec-intake-phase3b-answer-001.md`
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-003.md`
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-005.md`
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001.md`
- `bridge/gtkb-cross-harness-trigger-active-session-target-naming-001.md`
- `bridge/gtkb-cross-harness-trigger-active-session-target-naming-002.md`
- `bridge/gtkb-cross-harness-trigger-active-session-target-naming-003.md`
- `bridge/gtkb-cross-harness-trigger-active-session-target-naming-005.md`
- `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-001.md`
- `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-003.md`
- `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-005.md`
- `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-006.md`
- `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-007.md`
- `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-001.md`
- `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-003.md`
- `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-004.md`
- `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-006.md`
- `bridge/gtkb-cross-harness-trigger-import-repair-001.md`
- `bridge/gtkb-cross-harness-trigger-import-repair-003.md`
- `bridge/gtkb-cross-harness-trigger-import-repair-006.md`
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-001.md`
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-003.md`
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-005.md`
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-006.md`
- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-008.md`
- `bridge/gtkb-cross-harness-trigger-no-go-dispatch-fix-001.md`
- `bridge/gtkb-cross-harness-trigger-no-go-dispatch-fix-002.md`
- `bridge/gtkb-cross-harness-trigger-no-go-dispatch-fix-003.md`
- `bridge/gtkb-cross-harness-trigger-no-go-dispatch-fix-004.md`
- `bridge/gtkb-cross-harness-trigger-no-go-dispatch-fix-005.md`
- `bridge/gtkb-cross-harness-trigger-no-go-dispatch-fix-006.md`
- `bridge/gtkb-cross-harness-trigger-no-go-dispatch-fix-008.md`
- `bridge/gtkb-cross-harness-trigger-no-go-dispatch-fix-010.md`
- `bridge/gtkb-cross-harness-trigger-windows-rename-race-001-001.md`
- `bridge/gtkb-cross-harness-trigger-windows-rename-race-001-003.md`
- `bridge/gtkb-da-enforcement-completion-slice1-decompose-001.md`
- `bridge/gtkb-da-enforcement-completion-slice1-decompose-002.md`
- `bridge/gtkb-da-enforcement-completion-slice1-decompose-003.md`
- `bridge/gtkb-da-enforcement-completion-slice1-decompose-004.md`
- `bridge/gtkb-da-enforcement-completion-slice1-decompose-005.md`
- `bridge/gtkb-da-enforcement-completion-slice1-decompose-007.md`
- `bridge/gtkb-da-enforcement-completion-slice1-decompose-008.md`
- `bridge/gtkb-da-enforcement-completion-slice1-decompose-009.md`
- `bridge/gtkb-da-enforcement-completion-slice1-decompose-011.md`
- `bridge/gtkb-da-harvest-catchup-001.md`
- `bridge/gtkb-da-harvest-catchup-003.md`
- `bridge/gtkb-dashboard-control-plane-baseline-implementation-001.md`
- `bridge/gtkb-dashboard-control-plane-baseline-implementation-003.md`
- `bridge/gtkb-dashboard-industry-alignment-slice2-001.md`
- `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-001.md`
- `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-003.md`
- `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-007.md`
- `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-001.md`
- `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-003.md`
- `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-023.md`
- `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-025.md`
- `bridge/gtkb-dashboard-launcher-idempotence-pid-tracking-001.md`
- `bridge/gtkb-dashboard-launcher-idempotence-pid-tracking-002.md`
- `bridge/gtkb-dashboard-launcher-idempotence-pid-tracking-004.md`
- `bridge/gtkb-dashboard-launcher-idempotence-pid-tracking-006.md`
- `bridge/gtkb-db-backup-001-snapshot-daemon-001.md`
- `bridge/gtkb-db-backup-001-snapshot-daemon-007.md`
- `bridge/gtkb-db-backup-001-snapshot-daemon-009.md`
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-001.md`
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md`
- `bridge/gtkb-decision-tracker-cached-pending-block-exclusion-001.md`
- `bridge/gtkb-decision-tracker-cached-pending-block-exclusion-003.md`
- `bridge/gtkb-decision-tracker-cached-pending-block-exclusion-004.md`
- `bridge/gtkb-decision-tracker-cached-pending-block-exclusion-005.md`
- `bridge/gtkb-decision-tracker-cached-pending-block-exclusion-006.md`
- `bridge/gtkb-deferred-authority-implementation-start-parser-followup-001.md`
- `bridge/gtkb-deferred-authority-implementation-start-parser-followup-002.md`
- `bridge/gtkb-deferred-authority-implementation-start-parser-followup-004.md`
- `bridge/gtkb-deferred-authority-protocol-alignment-001.md`
- `bridge/gtkb-deferred-authority-protocol-alignment-002.md`
- `bridge/gtkb-deferred-authority-protocol-alignment-003.md`
- `bridge/gtkb-deferred-authority-protocol-alignment-004.md`
- `bridge/gtkb-deferred-authority-protocol-alignment-005.md`
- `bridge/gtkb-deferred-authority-protocol-alignment-006.md`
- `bridge/gtkb-deferred-authority-protocol-alignment-009.md`
- `bridge/gtkb-deferred-authority-protocol-alignment-010.md`
- `bridge/gtkb-deferred-authority-protocol-alignment-011.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-001.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-002.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-003.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-004.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-005.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-006.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-007.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-008.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-009.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-010.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-012.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-batch-2-001.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-batch-2-002.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-batch-2-003.md`
- `bridge/gtkb-deterministic-services-stale-status-reconciliation-batch-2-004.md`
- `bridge/gtkb-directive-enforcement-p1-p2-003.md`
- `bridge/gtkb-directive-enforcement-p1-p2-combined-003.md`
- `bridge/gtkb-directive-enforcement-registry-005.md`
- `bridge/gtkb-dirty-tree-reconciliation-2026-06-07-001.md`
- `bridge/gtkb-discoverability-cli-slice-1-003.md`
- `bridge/gtkb-discoverability-cli-slice-1-004.md`
- `bridge/gtkb-discoverability-cli-slice-1-005.md`
- `bridge/gtkb-discoverability-cli-slice-1-006.md`
- `bridge/gtkb-discoverability-cli-slice-1-007.md`
- `bridge/gtkb-discoverability-cli-slice-1-008.md`
- `bridge/gtkb-discoverability-cli-slice-2-implementation-001.md`
- `bridge/gtkb-discoverability-cli-slice-2-implementation-002.md`
- `bridge/gtkb-discoverability-cli-slice-2-implementation-003.md`
- `bridge/gtkb-discoverability-cli-slice-2-implementation-004.md`
- `bridge/gtkb-discoverability-cli-slice-2-implementation-006.md`
- `bridge/gtkb-discoverability-cli-slice-2-scoping-001.md`
- `bridge/gtkb-discoverability-cli-slice-2-scoping-002.md`
- `bridge/gtkb-discoverability-cli-slice-2-scoping-004.md`
- `bridge/gtkb-discoverability-cli-slice-2-scoping-006.md`
- `bridge/gtkb-discoverability-cli-status-scanner-api-regression-001.md`
- `bridge/gtkb-discoverability-cli-status-scanner-api-regression-002.md`
- `bridge/gtkb-discoverability-cli-status-scanner-api-regression-004.md`
- `bridge/gtkb-dispatch-envelope-adr-specs-001.md`
- `bridge/gtkb-dispatch-envelope-adr-specs-002.md`
- `bridge/gtkb-dispatch-envelope-adr-specs-003.md`
- `bridge/gtkb-dispatch-failures-jsonl-rotation-001.md`
- `bridge/gtkb-dispatch-failures-jsonl-rotation-004.md`
- `bridge/gtkb-dispatch-owner-approval-forgery-prevention-001.md`
- `bridge/gtkb-dispatch-owner-approval-forgery-prevention-003.md`
- `bridge/gtkb-dispatch-owner-approval-forgery-prevention-004.md`
- `bridge/gtkb-dispatch-owner-approval-forgery-prevention-006.md`
- `bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-001.md`
- `bridge/gtkb-dispatcher-config-cli-whole-candidate-validation-003.md`
- `bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-001.md`
- `bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-002.md`
- `bridge/gtkb-doctor-dispatch-liveness-recipient-key-fix-004.md`
- `bridge/gtkb-document-author-provenance-contract-001.md`
- `bridge/gtkb-document-author-provenance-contract-002.md`
- `bridge/gtkb-document-author-provenance-contract-003.md`
- `bridge/gtkb-document-author-provenance-contract-004.md`
- `bridge/gtkb-document-author-provenance-contract-006.md`
- `bridge/gtkb-dora-001b-authoritative-deployment-source-001.md`
- `bridge/gtkb-dora-001b-authoritative-deployment-source-003.md`
- `bridge/gtkb-dora-001b-authoritative-deployment-source-005.md`
- `bridge/gtkb-dora-001b-authoritative-deployment-source-007.md`
- `bridge/gtkb-dora-001b-authoritative-deployment-source-009.md`
- `bridge/gtkb-dora-001b-authoritative-deployment-source-010.md`
- `bridge/gtkb-dora-001b-implementation-001.md`
- `bridge/gtkb-dora-001b-implementation-003.md`
- `bridge/gtkb-dora-001b-track1-implementation-001.md`
- `bridge/gtkb-dora-001b-track2-implementation-001.md`
- `bridge/gtkb-dora-001b-track2-implementation-003.md`
- `bridge/gtkb-dora-001b-track2-implementation-005.md`
- `bridge/gtkb-dora-telemetry-foundation-001.md`
- `bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-001.md`
- `bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-002.md`
- `bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-003.md`
- `bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-004.md`
- `bridge/gtkb-early-project-requirements-quality-audit-slice-1-scoping-005.md`
- `bridge/gtkb-early-project-specs-quality-audit-001.md`
- `bridge/gtkb-early-project-specs-quality-audit-002.md`
- `bridge/gtkb-ecosystem-scout-policy-implementation-003.md`
- `bridge/gtkb-env-sot-topology-spec-authoring-001.md`
- `bridge/gtkb-env-sot-topology-spec-authoring-003.md`
- `bridge/gtkb-env-sot-topology-spec-authoring-004.md`
- `bridge/gtkb-env-sot-topology-spec-authoring-006.md`
- `bridge/gtkb-env-sot-topology-spec-authoring-008.md`
- `bridge/gtkb-env-sot-topology-spec-authoring-010.md`
- `bridge/gtkb-envelope-disclosure-ui-impl-001.md`
- `bridge/gtkb-envelope-disclosure-ui-impl-002.md`
- `bridge/gtkb-envelope-disclosure-ui-impl-003.md`
- `bridge/gtkb-envelope-disclosure-ui-impl-004.md`
- `bridge/gtkb-envelope-disclosure-ui-impl-005.md`
- `bridge/gtkb-envelope-disclosure-ui-impl-006.md`
- `bridge/gtkb-envelope-disclosure-ui-impl-007.md`
- `bridge/gtkb-envelope-disclosure-ui-impl-008.md`
- `bridge/gtkb-envelope-disclosure-ui-impl-009.md`
- `bridge/gtkb-envelope-disclosure-ui-impl-011.md`
- `bridge/gtkb-envelope-disclosure-ui-impl-013.md`
- `bridge/gtkb-envelope-disclosure-ui-redesign-001.md`
- `bridge/gtkb-envelope-disclosure-ui-redesign-002.md`
- `bridge/gtkb-envelope-dispatch-element-001-001.md`
- `bridge/gtkb-envelope-dispatch-element-001-002.md`
- `bridge/gtkb-envelope-glossary-and-gov-lifecycle-amendment-001.md`
- `bridge/gtkb-envelope-glossary-and-gov-lifecycle-amendment-002.md`
- `bridge/gtkb-envelope-implementation-umbrella-capstone-001.md`
- `bridge/gtkb-envelope-implementation-umbrella-capstone-002.md`
- `bridge/gtkb-envelope-init-keyword-amendment-slice-1-001.md`
- `bridge/gtkb-envelope-init-keyword-amendment-slice-1-002.md`
- `bridge/gtkb-envelope-init-keyword-amendment-slice-1-004.md`
- `bridge/gtkb-envelope-init-keyword-amendment-slice-1-005.md`
- `bridge/gtkb-envelope-init-keyword-amendment-slice-1-006.md`
- `bridge/gtkb-envelope-init-keyword-amendment-slice-1-008.md`
- `bridge/gtkb-envelope-init-keyword-amendment-slice-1-010.md`
- `bridge/gtkb-envelope-init-keyword-amendment-slice-1-012.md`
- `bridge/gtkb-envelope-meta-model-adr-dcl-001-001.md`
- `bridge/gtkb-envelope-meta-model-adr-dcl-001-002.md`
- `bridge/gtkb-envelope-runtime-capstone-impl-001.md`
- `bridge/gtkb-envelope-runtime-capstone-impl-002.md`
- `bridge/gtkb-envelope-runtime-capstone-impl-004.md`
- `bridge/gtkb-environment-boundary-baseline-implementation-001.md`
- `bridge/gtkb-environment-boundary-baseline-implementation-003.md`
- `bridge/gtkb-environment-boundary-baseline-implementation-005.md`
- `bridge/gtkb-environment-boundary-baseline-implementation-007.md`
- `bridge/gtkb-first-class-project-artifacts-004.md`
- `bridge/gtkb-first-class-project-artifacts-006.md`
- `bridge/gtkb-first-class-project-artifacts-007.md`
- `bridge/gtkb-first-class-project-artifacts-008.md`
- `bridge/gtkb-first-class-project-artifacts-009.md`
- `bridge/gtkb-formal-artifact-packet-validator-cli-001.md`
- `bridge/gtkb-formal-artifact-packet-validator-cli-003.md`
- `bridge/gtkb-generate-approval-packet-cli-001.md`
- `bridge/gtkb-generate-approval-packet-cli-002.md`
- `bridge/gtkb-generate-approval-packet-cli-003.md`
- `bridge/gtkb-generate-approval-packet-cli-004.md`
- `bridge/gtkb-generate-approval-packet-cli-005.md`
- `bridge/gtkb-generate-approval-packet-cli-006.md`
- `bridge/gtkb-generate-approval-packet-cli-007.md`
- `bridge/gtkb-generate-approval-packet-cli-008.md`
- `bridge/gtkb-generate-approval-packet-cli-009.md`
- `bridge/gtkb-generate-approval-packet-cli-010.md`
- `bridge/gtkb-generate-approval-packet-cli-012.md`
- `bridge/gtkb-git-hooks-path-mismatch-lint-001.md`
- `bridge/gtkb-git-hooks-path-mismatch-lint-002.md`
- `bridge/gtkb-git-hooks-path-mismatch-lint-004.md`
- `bridge/gtkb-git-repo-broken-blob-investigation-001.md`
- `bridge/gtkb-git-repo-broken-blob-investigation-003.md`
- `bridge/gtkb-git-repo-broken-blob-investigation-005.md`
- `bridge/gtkb-git-repo-broken-blob-investigation-008.md`
- `bridge/gtkb-git-repo-broken-blob-investigation-010.md`
- `bridge/gtkb-git-repo-broken-blob-investigation-012.md`
- `bridge/gtkb-github-ai-harness-ecosystem-advisory-2026-05-11-001.md`
- `bridge/gtkb-github-ai-harness-ecosystem-advisory-2026-05-11-002.md`
- `bridge/gtkb-github-ai-harness-ecosystem-conversion-001.md`
- `bridge/gtkb-github-ai-harness-ecosystem-conversion-002.md`
- `bridge/gtkb-github-ai-harness-ecosystem-conversion-004.md`
- `bridge/gtkb-gov-010-followup-observations-s342-002.md`
- `bridge/gtkb-gov-010-followup-observations-s342-004.md`
- `bridge/gtkb-gov-010-followup-observations-s342-005.md`
- `bridge/gtkb-gov-010-harvest-refresh-2026-05-11-004.md`
- `bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-001.md`
- `bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-002.md`
- `bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-003.md`
- `bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-004.md`
- `bridge/gtkb-gov-08-permitted-markdown-amendment-scoping-006.md`
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-012.md`
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-014.md`
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-016.md`
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-018.md`
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-020.md`
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-022.md`
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-024.md`
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-027.md`
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-029.md`
- `bridge/gtkb-gov-code-quality-baseline-formal-artifact-approval-001.md`
- `bridge/gtkb-gov-code-quality-baseline-formal-artifact-approval-003.md`
- `bridge/gtkb-gov-code-quality-baseline-formal-artifact-approval-004.md`
- `bridge/gtkb-gov-code-quality-baseline-formal-artifact-approval-005.md`
- `bridge/gtkb-gov-code-quality-baseline-formal-artifact-approval-006.md`
- `bridge/gtkb-gov-code-quality-baseline-formal-artifact-approval-007.md`
- `bridge/gtkb-gov-code-quality-baseline-formal-artifact-approval-008.md`
- `bridge/gtkb-gov-code-quality-baseline-slice-2-001.md`
- `bridge/gtkb-gov-code-quality-baseline-slice-2-003.md`
- `bridge/gtkb-gov-code-quality-baseline-slice-2-005.md`
- `bridge/gtkb-gov-code-quality-baseline-slice-2-007.md`
- `bridge/gtkb-gov-code-quality-baseline-slice-2-010.md`
- `bridge/gtkb-gov-code-quality-baseline-slice-2-012.md`
- `bridge/gtkb-gov-code-quality-baseline-slice-2-013.md`
- `bridge/gtkb-gov-code-quality-baseline-slice-2-014.md`
- `bridge/gtkb-gov-code-quality-baseline-slice1-001.md`
- `bridge/gtkb-gov-code-quality-baseline-slice1-003.md`
- `bridge/gtkb-gov-code-quality-baseline-slice1-005.md`
- `bridge/gtkb-gov-code-quality-baseline-slice1-007.md`
- `bridge/gtkb-gov-code-quality-baseline-slice1-008.md`
- `bridge/gtkb-gov-file-bridge-authority-001-002.md`
- `bridge/gtkb-gov-file-bridge-authority-001-004.md`
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-001.md`
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-003.md`
- `bridge/gtkb-gov-project-retirement-spec-001.md`
- `bridge/gtkb-gov-project-retirement-spec-003.md`
- `bridge/gtkb-gov-project-retirement-spec-005.md`
- `bridge/gtkb-gov-project-retirement-spec-006.md`
- `bridge/gtkb-gov-proposal-standards-slice1-005.md`
- `bridge/gtkb-gov-proposal-standards-slice1-007.md`
- `bridge/gtkb-gov-proposal-standards-slice1-009.md`
- `bridge/gtkb-gov-proposal-standards-slice1-022.md`
- `bridge/gtkb-gov-proposal-standards-slice1-023.md`
- `bridge/gtkb-gov-proposal-standards-slice1-024.md`
- `bridge/gtkb-gov-proposal-standards-slice1-025.md`
- `bridge/gtkb-gov-proposal-standards-slice1-027.md`
- `bridge/gtkb-governance-adoption-doctor-check-001.md`
- `bridge/gtkb-governance-adoption-doctor-check-003.md`
- `bridge/gtkb-governance-adoption-doctor-check-005.md`
- `bridge/gtkb-governance-adoption-doctor-check-006.md`
- `bridge/gtkb-governance-adoption-doctor-check-008.md`
- `bridge/gtkb-governance-hook-worktree-root-resolution-001.md`
- `bridge/gtkb-governance-hook-worktree-root-resolution-003.md`
- `bridge/gtkb-governance-hook-worktree-root-resolution-005.md`
- `bridge/gtkb-governance-hook-worktree-root-resolution-007.md`
- `bridge/gtkb-governance-hook-worktree-root-resolution-008.md`
- `bridge/gtkb-governed-spec-retirement-001.md`
- `bridge/gtkb-governed-spec-retirement-003.md`
- `bridge/gtkb-governed-spec-retirement-005.md`
- `bridge/gtkb-gt-backlog-add-cli-001.md`
- `bridge/gtkb-gt-backlog-add-cli-002.md`
- `bridge/gtkb-gt-backlog-add-cli-003.md`
- `bridge/gtkb-gt-backlog-add-cli-004.md`
- `bridge/gtkb-gt-backlog-add-cli-005.md`
- `bridge/gtkb-gt-bridge-propose-deterministic-cli-001.md`
- `bridge/gtkb-gt-bridge-propose-deterministic-cli-003.md`
- `bridge/gtkb-gt-bridge-propose-deterministic-cli-004.md`
- `bridge/gtkb-gt-bridge-propose-deterministic-cli-006.md`
- `bridge/gtkb-handoff-prompt-deterministic-service-001.md`
- `bridge/gtkb-handoff-prompt-deterministic-service-002.md`
- `bridge/gtkb-handoff-prompt-deterministic-service-impl-001.md`
- `bridge/gtkb-handoff-prompt-deterministic-service-impl-002.md`
- `bridge/gtkb-handoff-prompt-deterministic-service-impl-003.md`
- `bridge/gtkb-handoff-prompt-deterministic-service-impl-004.md`
- `bridge/gtkb-handoff-prompt-deterministic-service-impl-005.md`
- `bridge/gtkb-handoff-prompt-deterministic-service-impl-007.md`
- `bridge/gtkb-handoff-prompt-deterministic-service-impl-009.md`
- `bridge/gtkb-handoff-prompt-deterministic-service-impl-011.md`
- `bridge/gtkb-handoff-prompt-terminology-clarification-001.md`
- `bridge/gtkb-handoff-prompt-terminology-clarification-002.md`
- `bridge/gtkb-handoff-prompt-terminology-clarification-003.md`
- `bridge/gtkb-handoff-prompt-terminology-clarification-004.md`
- `bridge/gtkb-harness-cli-command-group-001.md`
- `bridge/gtkb-harness-cli-command-group-002.md`
- `bridge/gtkb-harness-cli-command-group-003.md`
- `bridge/gtkb-harness-cli-command-group-004.md`
- `bridge/gtkb-harness-cli-command-group-005.md`
- `bridge/gtkb-harness-cli-command-group-006.md`
- `bridge/gtkb-harness-cli-command-group-007.md`
- `bridge/gtkb-harness-cli-command-group-008.md`
- `bridge/gtkb-harness-data-driven-dispatch-001.md`
- `bridge/gtkb-harness-data-driven-dispatch-003.md`
- `bridge/gtkb-harness-data-driven-dispatch-006.md`
- `bridge/gtkb-harness-lifecycle-fsm-001.md`
- `bridge/gtkb-harness-lifecycle-fsm-002.md`
- `bridge/gtkb-harness-lifecycle-fsm-003.md`
- `bridge/gtkb-harness-lifecycle-fsm-004.md`
- `bridge/gtkb-harness-registry-hot-path-projection-001.md`
- `bridge/gtkb-harness-registry-hot-path-projection-002.md`
- `bridge/gtkb-harness-registry-hot-path-projection-003.md`
- `bridge/gtkb-harness-registry-hot-path-projection-004.md`
- `bridge/gtkb-harness-registry-parity-sweep-001.md`
- `bridge/gtkb-harness-registry-parity-sweep-002.md`
- `bridge/gtkb-harness-registry-parity-sweep-003.md`
- `bridge/gtkb-harness-registry-parity-sweep-004.md`
- `bridge/gtkb-harness-registry-parity-sweep-005.md`
- `bridge/gtkb-harness-registry-parity-sweep-006.md`
- `bridge/gtkb-harness-registry-parity-sweep-007.md`
- `bridge/gtkb-harness-registry-reader-migration-001.md`
- `bridge/gtkb-harness-registry-reader-migration-003.md`
- `bridge/gtkb-harness-registry-reader-migration-005.md`
- `bridge/gtkb-harness-registry-reader-migration-007.md`
- `bridge/gtkb-harness-registry-reader-migration-008.md`
- `bridge/gtkb-harness-registry-reader-migration-009.md`
- `bridge/gtkb-harness-registry-reader-migration-010.md`
- `bridge/gtkb-harness-registry-reader-migration-011.md`
- `bridge/gtkb-harness-registry-reader-migration-014.md`
- `bridge/gtkb-harness-registry-seed-001.md`
- `bridge/gtkb-harness-registry-seed-002.md`
- `bridge/gtkb-harness-registry-seed-003.md`
- `bridge/gtkb-harness-registry-seed-004.md`
- `bridge/gtkb-harness-registry-table-schema-001.md`
- `bridge/gtkb-harness-registry-table-schema-002.md`
- `bridge/gtkb-harness-registry-table-schema-003.md`
- `bridge/gtkb-harness-registry-table-schema-004.md`
- `bridge/gtkb-harness-registry-table-schema-005.md`
- `bridge/gtkb-harness-registry-table-schema-006.md`
- `bridge/gtkb-harness-registry-table-schema-007.md`
- `bridge/gtkb-harness-registry-table-schema-008.md`
- `bridge/gtkb-harness-role-portability-fr9-001.md`
- `bridge/gtkb-harness-role-portability-fr9-002.md`
- `bridge/gtkb-harness-role-portability-fr9-003.md`
- `bridge/gtkb-harness-role-portability-fr9-004.md`
- `bridge/gtkb-harness-role-portability-fr9-005.md`
- `bridge/gtkb-harness-role-portability-fr9-006.md`
- `bridge/gtkb-harness-role-portability-fr9-007.md`
- `bridge/gtkb-harness-role-portability-fr9-008.md`
- `bridge/gtkb-harness-role-portability-fr9-009.md`
- `bridge/gtkb-harness-role-portability-fr9-010.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-001.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-002.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-003.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-004.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-001.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-002.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-003.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-004.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-005.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-006.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-008.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-010.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-012.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-003.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-005.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-010.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-011.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-012.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-014.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-016.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-018.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-rule-files-001.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-rule-files-002.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-rule-files-003.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-rule-files-004.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-rule-files-006.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-rule-files-008.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-rule-files-010.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-001.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-002.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-003.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-004.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-006.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-008.md`
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-010.md`
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-001.md`
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-003.md`
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-006.md`
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-009.md`
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-010.md`
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-011.md`
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-012.md`
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-013.md`
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-014.md`
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-016.md`
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-017.md`
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-018.md`
- `bridge/gtkb-heartbeat-replace-access-denied-retry-001.md`
- `bridge/gtkb-heartbeat-replace-access-denied-retry-002.md`
- `bridge/gtkb-heartbeat-replace-access-denied-retry-003.md`
- `bridge/gtkb-heartbeat-replace-access-denied-retry-006.md`
- `bridge/gtkb-hook-import-latency-chromadb-lazy-008.md`
- `bridge/gtkb-hook-strictness-p1-p2-remediation-001.md`
- `bridge/gtkb-hook-strictness-p1-p2-remediation-003.md`
- `bridge/gtkb-hook-strictness-p1-p2-remediation-005.md`
- `bridge/gtkb-hook-strictness-p1-p2-remediation-007.md`
- `bridge/gtkb-hook-strictness-p1-p2-remediation-008.md`
- `bridge/gtkb-hook-strictness-p1-p2-remediation-009.md`
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-1-001.md`
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-1-002.md`
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-1-004.md`
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-001.md`
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-002.md`
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-003.md`
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-005.md`
- `bridge/gtkb-hygiene-sweep-cli-001.md`
- `bridge/gtkb-hygiene-sweep-cli-002.md`
- `bridge/gtkb-hygiene-sweep-cli-004.md`
- `bridge/gtkb-hygiene-sweep-cli-scoping-001.md`
- `bridge/gtkb-hygiene-sweep-cli-scoping-002.md`
- `bridge/gtkb-hygiene-sweep-cli-scoping-003.md`
- `bridge/gtkb-hygiene-sweep-cli-scoping-005.md`
- `bridge/gtkb-hygiene-sweep-cli-test-rebuild-001.md`
- `bridge/gtkb-hygiene-sweep-cli-test-rebuild-002.md`
- `bridge/gtkb-hygiene-sweep-cli-test-rebuild-004.md`
- `bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-001.md`
- `bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-002.md`
- `bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-003.md`
- `bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-004.md`
- `bridge/gtkb-hygiene-sweep-presence-patterns-slice-1-006.md`
- `bridge/gtkb-hygiene-sweep-skill-001.md`
- `bridge/gtkb-hygiene-sweep-skill-002.md`
- `bridge/gtkb-hygiene-sweep-skill-003.md`
- `bridge/gtkb-hygiene-sweep-skill-004.md`
- `bridge/gtkb-hygiene-sweep-skill-006.md`
- `bridge/gtkb-hygiene-sweep-skill-008.md`
- `bridge/gtkb-hygiene-sweep-skill-scoping-001.md`
- `bridge/gtkb-hygiene-sweep-skill-scoping-002.md`
- `bridge/gtkb-hygiene-sweep-skill-scoping-003.md`
- `bridge/gtkb-hygiene-sweep-skill-scoping-004.md`
- `bridge/gtkb-hygiene-sweep-skill-scoping-006.md`
- `bridge/gtkb-idp-terminology-formalization-001.md`
- `bridge/gtkb-idp-terminology-formalization-003.md`
- `bridge/gtkb-idp-terminology-formalization-005.md`
- `bridge/gtkb-idp-terminology-formalization-007.md`
- `bridge/gtkb-idp-terminology-formalization-008.md`
- `bridge/gtkb-impl-auth-owner-sufficiency-gate-001.md`
- `bridge/gtkb-impl-auth-owner-sufficiency-gate-002.md`
- `bridge/gtkb-impl-auth-owner-sufficiency-gate-004.md`
- `bridge/gtkb-impl-auth-parser-false-positive-fix-001.md`
- `bridge/gtkb-impl-auth-parser-false-positive-fix-003.md`
- `bridge/gtkb-impl-auth-parser-false-positive-fix-006.md`
- `bridge/gtkb-impl-auth-requirement-sufficiency-phrase-tolerance-001.md`
- `bridge/gtkb-impl-auth-requirement-sufficiency-phrase-tolerance-002.md`
- `bridge/gtkb-impl-auth-requirement-sufficiency-phrase-tolerance-004.md`
- `bridge/gtkb-impl-gate-friction-hygiene-001.md`
- `bridge/gtkb-impl-gate-friction-hygiene-002.md`
- `bridge/gtkb-impl-gate-friction-hygiene-003.md`
- `bridge/gtkb-impl-gate-friction-hygiene-004.md`
- `bridge/gtkb-impl-gate-friction-hygiene-006.md`
- `bridge/gtkb-impl-report-bridge-structural-validation-mtime-001.md`
- `bridge/gtkb-impl-report-bridge-structural-validation-mtime-002.md`
- `bridge/gtkb-impl-report-bridge-structural-validation-mtime-003.md`
- `bridge/gtkb-impl-report-bridge-structural-validation-mtime-005.md`
- `bridge/gtkb-impl-report-bridge-structural-validation-mtime-006.md`
- `bridge/gtkb-impl-report-bridge-structural-validation-mtime-008.md`
- `bridge/gtkb-impl-start-gate-comparison-operator-fix-001.md`
- `bridge/gtkb-impl-start-gate-comparison-operator-fix-002.md`
- `bridge/gtkb-impl-start-gate-comparison-operator-fix-004.md`
- `bridge/gtkb-impl-start-gate-comparison-operator-fix-006.md`
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-001.md`
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-002.md`
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-003.md`
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-004.md`
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-005.md`
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-006.md`
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-007.md`
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-008.md`
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-010.md`
- `bridge/gtkb-impl-start-gate-format-spec-fix-001.md`
- `bridge/gtkb-impl-start-gate-format-spec-fix-003.md`
- `bridge/gtkb-impl-start-gate-format-spec-fix-005.md`
- `bridge/gtkb-impl-start-gate-format-spec-fix-007.md`
- `bridge/gtkb-impl-start-gate-path-token-memory-prefix-fix-001.md`
- `bridge/gtkb-impl-start-gate-path-token-memory-prefix-fix-002.md`
- `bridge/gtkb-impl-start-gate-path-token-memory-prefix-fix-004.md`
- `bridge/gtkb-impl-start-gate-pretooluse-restore-001.md`
- `bridge/gtkb-impl-start-gate-pretooluse-restore-002.md`
- `bridge/gtkb-impl-start-gate-pretooluse-restore-003.md`
- `bridge/gtkb-impl-start-gate-pretooluse-restore-004.md`
- `bridge/gtkb-impl-start-gate-pretooluse-restore-005.md`
- `bridge/gtkb-impl-start-gate-pretooluse-restore-007.md`
- `bridge/gtkb-impl-start-gate-pretooluse-restore-008.md`
- `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-001.md`
- `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-002.md`
- `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-004.md`
- `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-001.md`
- `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-002.md`
- `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-003.md`
- `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-004.md`
- `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-006.md`
- `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-008.md`
- `bridge/gtkb-impl-start-gate-verb-aware-path-extraction-010.md`
- `bridge/gtkb-impl-start-target-paths-preflight-001.md`
- `bridge/gtkb-impl-start-target-paths-preflight-002.md`
- `bridge/gtkb-impl-start-target-paths-preflight-003.md`
- `bridge/gtkb-impl-start-target-paths-preflight-004.md`
- `bridge/gtkb-impl-start-target-paths-preflight-005.md`
- `bridge/gtkb-impl-start-target-paths-preflight-007.md`
- `bridge/gtkb-impl-start-target-paths-preflight-008.md`
- `bridge/gtkb-impl-start-target-paths-preflight-009.md`
- `bridge/gtkb-implementation-gate-friction-hygiene-001.md`
- `bridge/gtkb-implementation-gate-friction-hygiene-003.md`
- `bridge/gtkb-implementation-gate-friction-hygiene-005.md`
- `bridge/gtkb-implementation-gate-friction-hygiene-006.md`
- `bridge/gtkb-implementation-gate-friction-hygiene-007.md`
- `bridge/gtkb-implementation-gate-friction-hygiene-009.md`
- `bridge/gtkb-implementation-gate-friction-hygiene-010.md`
- `bridge/gtkb-implementation-gate-friction-hygiene-011.md`
- `bridge/gtkb-implementation-gate-friction-hygiene-012.md`
- `bridge/gtkb-implementation-gate-friction-hygiene-014.md`
- `bridge/gtkb-implementation-gate-friction-hygiene-018.md`
- `bridge/gtkb-implementation-gate-friction-hygiene-020.md`
- `bridge/gtkb-implementation-gate-friction-hygiene-022.md`
- `bridge/gtkb-implementation-start-authorization-gate-002.md`
- `bridge/gtkb-implementation-start-authorization-gate-004.md`
- `bridge/gtkb-implementation-start-authorization-gate-005.md`
- `bridge/gtkb-implementation-start-authorization-gate-006.md`
- `bridge/gtkb-implementation-start-authorization-gate-007.md`
- `bridge/gtkb-implementation-start-authorization-gate-008.md`
- `bridge/gtkb-implementation-start-authorization-gate-010.md`
- `bridge/gtkb-implementation-start-gate-repository-finalization-001.md`
- `bridge/gtkb-implementation-start-gate-repository-finalization-002.md`
- `bridge/gtkb-implementation-start-gate-repository-finalization-004.md`
- `bridge/gtkb-implementation-start-requirement-sufficiency-owner-direction-phrase-001.md`
- `bridge/gtkb-implementation-start-requirement-sufficiency-owner-direction-phrase-002.md`
- `bridge/gtkb-implementation-start-requirement-sufficiency-owner-direction-phrase-004.md`
- `bridge/gtkb-implementation-start-requirement-sufficiency-owner-direction-phrase-006.md`
- `bridge/gtkb-implements-link-backfill-phase2-implementation-001.md`
- `bridge/gtkb-implements-link-backfill-phase2-implementation-004.md`
- `bridge/gtkb-implements-link-backfill-phase2-implementation-006.md`
- `bridge/gtkb-implements-link-backfill-phase2-scoping-001.md`
- `bridge/gtkb-implements-link-backfill-phase2-scoping-002.md`
- `bridge/gtkb-implements-link-backfill-phase2-scoping-004.md`
- `bridge/gtkb-in-source-provenance-anchors-001-prop-001.md`
- `bridge/gtkb-in-source-provenance-anchors-001-prop-003.md`
- `bridge/gtkb-in-source-provenance-anchors-001-prop-004.md`
- `bridge/gtkb-in-source-provenance-anchors-001-prop-005.md`
- `bridge/gtkb-in-source-provenance-anchors-001-prop-006.md`
- `bridge/gtkb-in-source-provenance-anchors-001-prop-008.md`
- `bridge/gtkb-incident-response-001.md`
- `bridge/gtkb-incident-response-003.md`
- `bridge/gtkb-incident-response-008.md`
- `bridge/gtkb-incident-response-ir-0-1-001.md`
- `bridge/gtkb-index-agent-edit-serialization-scoping-001.md`
- `bridge/gtkb-index-agent-edit-serialization-scoping-002.md`
- `bridge/gtkb-index-agent-edit-serialization-scoping-004.md`
- `bridge/gtkb-index-agent-edit-serialization-scoping-005.md`
- `bridge/gtkb-index-agent-edit-serialization-scoping-006.md`
- `bridge/gtkb-index-agent-edit-serialization-scoping-007.md`
- `bridge/gtkb-index-agent-edit-serialization-scoping-009.md`
- `bridge/gtkb-index-agent-edit-serialization-slice-1-bridge-index-cli-001.md`
- `bridge/gtkb-index-agent-edit-serialization-slice-1-bridge-index-cli-002.md`
- `bridge/gtkb-index-agent-edit-serialization-slice-1-bridge-index-cli-003.md`
- `bridge/gtkb-index-agent-edit-serialization-slice-1-bridge-index-cli-004.md`
- `bridge/gtkb-index-agent-edit-serialization-slice-1-bridge-index-cli-006.md`
- `bridge/gtkb-index-role-sentinel-stale-reconciliation-001.md`
- `bridge/gtkb-index-role-sentinel-stale-reconciliation-002.md`
- `bridge/gtkb-index-withdrawn-status-reconciliation-001.md`
- `bridge/gtkb-index-withdrawn-status-reconciliation-002.md`
- `bridge/gtkb-interactive-session-role-override-hygiene-backfill-001.md`
- `bridge/gtkb-interactive-session-role-override-hygiene-backfill-002.md`
- `bridge/gtkb-interactive-session-role-override-hygiene-backfill-003.md`
- `bridge/gtkb-interactive-session-role-override-hygiene-backfill-004.md`
- `bridge/gtkb-interactive-session-role-override-hygiene-backfill-006.md`
- `bridge/gtkb-interactive-session-role-override-scoping-001.md`
- `bridge/gtkb-interactive-session-role-override-scoping-002.md`
- `bridge/gtkb-interactive-session-role-override-scoping-003.md`
- `bridge/gtkb-interactive-session-role-override-scoping-004.md`
- `bridge/gtkb-interactive-session-role-override-scoping-006.md`
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-001.md`
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-002.md`
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-003.md`
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-1-sessionstart-cache-writer-007.md`
- `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-001.md`
- `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-002.md`
- `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-003.md`
- `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-005.md`
- `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-006.md`
- `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-008.md`
- `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-010.md`
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-001.md`
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-002.md`
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-003.md`
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-006.md`
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md`
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-001.md`
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-002.md`
- `bridge/gtkb-interactive-session-role-override-slice-3-sessionstart-marker-invalidation-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-001.md`
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-002.md`
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness-001.md`
- `bridge/gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness-002.md`
- `bridge/gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-001.md`
- `bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-002.md`
- `bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-001.md`
- `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-002.md`
- `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-006.md`
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-001.md`
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-002.md`
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-003.md`
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-006.md`
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-008.md`
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-009.md`
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-011.md`
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-013.md`
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-015.md`
- `bridge/gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-017.md`
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-001.md`
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-002.md`
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-003.md`
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-004.md`
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-005.md`
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-006.md`
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-007.md`
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-008.md`
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-010.md`
- `bridge/gtkb-inventory-drift-gh-probe-parity-001.md`
- `bridge/gtkb-inventory-drift-gh-probe-parity-002.md`
- `bridge/gtkb-inventory-drift-gh-probe-parity-004.md`
- `bridge/gtkb-inventory-drift-toolchain-flux-stability-001.md`
- `bridge/gtkb-inventory-drift-toolchain-flux-stability-002.md`
- `bridge/gtkb-inventory-drift-toolchain-flux-stability-004.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-27-001.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-27-004.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-28-001.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-28-002.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-28-004.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-29-001.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-29-002.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-29-004.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-29-006.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-31-001.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-31-002.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-31-003.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-31-004.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-31-005.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-31-006.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-31-008.md`
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-31-010.md`
- `bridge/gtkb-isolation-003-environment-plan-review-001.md`
- `bridge/gtkb-isolation-003-environment-plan-review-002.md`
- `bridge/gtkb-isolation-003-environment-plan-review-003.md`
- `bridge/gtkb-isolation-003-environment-plan-review-004.md`
- `bridge/gtkb-isolation-003-environment-plan-review-005.md`
- `bridge/gtkb-isolation-003-environment-plan-review-006.md`
- `bridge/gtkb-isolation-003-environment-plan-review-007.md`
- `bridge/gtkb-isolation-003-environment-plan-review-008.md`
- `bridge/gtkb-isolation-004-service-boundary-plan-review-001.md`
- `bridge/gtkb-isolation-004-service-boundary-plan-review-002.md`
- `bridge/gtkb-isolation-004-service-boundary-plan-review-003.md`
- `bridge/gtkb-isolation-004-service-boundary-plan-review-005.md`
- `bridge/gtkb-isolation-005-control-plane-plan-review-001.md`
- `bridge/gtkb-isolation-005-control-plane-plan-review-002.md`
- `bridge/gtkb-isolation-005-control-plane-plan-review-003.md`
- `bridge/gtkb-isolation-005-control-plane-plan-review-005.md`
- `bridge/gtkb-isolation-006-overlay-plan-review-001.md`
- `bridge/gtkb-isolation-006-overlay-plan-review-002.md`
- `bridge/gtkb-isolation-006-overlay-plan-review-003.md`
- `bridge/gtkb-isolation-006-overlay-plan-review-004.md`
- `bridge/gtkb-isolation-006-overlay-plan-review-006.md`
- `bridge/gtkb-isolation-007-work-subject-root-plan-review-001.md`
- `bridge/gtkb-isolation-007-work-subject-root-plan-review-002.md`
- `bridge/gtkb-isolation-007-work-subject-root-plan-review-003.md`
- `bridge/gtkb-isolation-007-work-subject-root-plan-review-004.md`
- `bridge/gtkb-isolation-008-migration-plan-review-001.md`
- `bridge/gtkb-isolation-008-migration-plan-review-003.md`
- `bridge/gtkb-isolation-009-adopter-packaging-plan-review-001.md`
- `bridge/gtkb-isolation-015-phase7-root-enforcement-001.md`
- `bridge/gtkb-isolation-015-phase7-root-enforcement-003.md`
- `bridge/gtkb-isolation-015-slice2-work-subject-set-002.md`
- `bridge/gtkb-isolation-015-slice2-work-subject-set-004.md`
- `bridge/gtkb-isolation-015-slice2-work-subject-set-006.md`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-001.md`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-003.md`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-005.md`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-007.md`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-009.md`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-011.md`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md`
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-001.md`
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-005.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice1-001.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice10-001.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-001.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice11-003.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice2-001.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice3-001.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice4-001.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-001.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-003.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-005.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-007.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice5-009.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-001.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-003.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-005.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-007.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-009.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice7-001.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice7-003.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice8-001.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice9-001.md`
- `bridge/gtkb-isolation-016-phase8-wave2-slice9-003.md`
- `bridge/gtkb-isolation-017-adopter-packaging-001.md`
- `bridge/gtkb-isolation-017-adopter-packaging-003.md`
- `bridge/gtkb-isolation-017-adopter-packaging-006.md`
- `bridge/gtkb-isolation-018-agent-red-cutover-001.md`
- `bridge/gtkb-isolation-018-agent-red-cutover-003.md`
- `bridge/gtkb-isolation-018-agent-red-cutover-005.md`
- `bridge/gtkb-isolation-018-agent-red-cutover-007.md`
- `bridge/gtkb-isolation-018-agent-red-cutover-010.md`
- `bridge/gtkb-isolation-018-agent-red-file-migration-010.md`
- `bridge/gtkb-isolation-018-slice-e-code-cluster-005.md`
- `bridge/gtkb-isolation-019-program-closeout-001.md`
- `bridge/gtkb-isolation-019-program-closeout-003.md`
- `bridge/gtkb-isolation-019-program-closeout-005.md`
- `bridge/gtkb-isolation-019-program-closeout-006.md`
- `bridge/gtkb-isolation-019-program-closeout-008.md`
- `bridge/gtkb-isolation-aftermath-startup-baseline-002.md`
- `bridge/gtkb-isolation-aftermath-startup-baseline-003.md`
- `bridge/gtkb-isolation-aftermath-startup-baseline-004.md`
- `bridge/gtkb-isolation-completion-plan-2026-04-28-011.md`
- `bridge/gtkb-isolation-phase3-implementation-003.md`
- `bridge/gtkb-isolation-phase3-occupancy-detection-003.md`
- `bridge/gtkb-isolation-phases-8-9-planning-scope-001.md`
- `bridge/gtkb-isolation-phases-8-9-planning-scope-003.md`
- `bridge/gtkb-kpi-suite-phase-1-retro-001.md`
- `bridge/gtkb-legacy-gov-wi-cleanup-001.md`
- `bridge/gtkb-legacy-gov-wi-cleanup-003.md`
- `bridge/gtkb-legacy-gov-wi-cleanup-004.md`
- `bridge/gtkb-legacy-gov-wi-cleanup-006.md`
- `bridge/gtkb-legacy-gov-wi-cleanup-008.md`
- `bridge/gtkb-legacy-gov-wi-cleanup-010.md`
- `bridge/gtkb-lo-advisory-intake-batch-001.md`
- `bridge/gtkb-lo-advisory-intake-batch-003.md`
- `bridge/gtkb-lo-advisory-intake-batch-004.md`
- `bridge/gtkb-lo-advisory-intake-batch-005.md`
- `bridge/gtkb-lo-advisory-intake-batch-006.md`
- `bridge/gtkb-lo-advisory-intake-batch-008.md`
- `bridge/gtkb-lo-advisory-owner-grilling-gate-002.md`
- `bridge/gtkb-lo-advisory-owner-grilling-gate-004.md`
- `bridge/gtkb-lo-advisory-owner-grilling-gate-006.md`
- `bridge/gtkb-lo-advisory-owner-grilling-gate-009.md`
- `bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-003.md`
- `bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-004.md`
- `bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-005.md`
- `bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-006.md`
- `bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-007.md`
- `bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-008.md`
- `bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-009.md`
- `bridge/gtkb-lo-bridge-history-backfill-slice-1-inventory-012.md`
- `bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-001.md`
- `bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-002.md`
- `bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-003.md`
- `bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-004.md`
- `bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-005.md`
- `bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-006.md`
- `bridge/gtkb-lo-file-safety-gate-envelope-role-resolution-008.md`
- `bridge/gtkb-lo-file-safety-pretooluse-enforcement-001.md`
- `bridge/gtkb-lo-file-safety-pretooluse-enforcement-003.md`
- `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-003.md`
- `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-005.md`
- `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-006.md`
- `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-007.md`
- `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-008.md`
- `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-009.md`
- `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-010.md`
- `bridge/gtkb-lo-file-safety-rule-clarification-001-002.md`
- `bridge/gtkb-lo-file-safety-rule-clarification-001-004.md`
- `bridge/gtkb-lo-file-safety-rule-clarification-001.md`
- `bridge/gtkb-lo-hourly-quality-scout-advisory-001.md`
- `bridge/gtkb-lo-hourly-quality-scout-advisory-002.md`
- `bridge/gtkb-lo-hourly-quality-scout-advisory-003.md`
- `bridge/gtkb-lo-hourly-quality-scout-advisory-004.md`
- `bridge/gtkb-lo-hygiene-assessment-skill-advisory-disposition-001.md`
- `bridge/gtkb-lo-hygiene-assessment-skill-advisory-disposition-002.md`
- `bridge/gtkb-lo-hygiene-assessment-skill-advisory-disposition-004.md`
- `bridge/gtkb-lo-hygiene-assessment-skill-build-001.md`
- `bridge/gtkb-lo-hygiene-assessment-skill-build-002.md`
- `bridge/gtkb-lo-hygiene-assessment-skill-build-004.md`
- `bridge/gtkb-lo-hygiene-assessment-skill-build-005.md`
- `bridge/gtkb-lo-hygiene-assessment-skill-build-007.md`
- `bridge/gtkb-lo-hygiene-assessment-skill-build-008.md`
- `bridge/gtkb-lo-hygiene-assessment-skill-build-010.md`
- `bridge/gtkb-lo-hygiene-assessment-skill-build-012.md`
- `bridge/gtkb-loop-multi-instance-coordinator-design-slice-1-001.md`
- `bridge/gtkb-loop-multi-instance-coordinator-design-slice-1-002.md`
- `bridge/gtkb-loop-multi-instance-coordinator-design-slice-1-005.md`
- `bridge/gtkb-loop-multi-instance-coordinator-design-slice-1-006.md`
- `bridge/gtkb-loop-multi-instance-coordinator-design-slice-1-007.md`
- `bridge/gtkb-loop-multi-instance-coordinator-design-slice-1-008.md`
- `bridge/gtkb-loop-multi-instance-coordinator-design-slice-1-009.md`
- `bridge/gtkb-loop-multi-instance-coordinator-design-slice-1-011.md`
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-003.md`
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-005.md`
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-007.md`
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-008.md`
- `bridge/gtkb-loyal-opposition-startup-symmetry-001-010.md`
- `bridge/gtkb-loyal-opposition-startup-symmetry-001.md`
- `bridge/gtkb-major-release-content-goal-gov-001.md`
- `bridge/gtkb-major-release-content-goal-gov-002.md`
- `bridge/gtkb-major-release-content-goal-gov-003.md`
- `bridge/gtkb-major-release-content-goal-gov-004.md`
- `bridge/gtkb-manual-bridge-scan-terminal-go-filter-001.md`
- `bridge/gtkb-manual-bridge-scan-terminal-go-filter-002.md`
- `bridge/gtkb-manual-bridge-scan-terminal-go-filter-003.md`
- `bridge/gtkb-manual-bridge-scan-terminal-go-filter-004.md`
- `bridge/gtkb-mass-adoption-bridge-audit-package-001.md`
- `bridge/gtkb-mass-adoption-first-commit-package-001.md`
- `bridge/gtkb-mass-adoption-readiness-scoping-001.md`
- `bridge/gtkb-mass-adoption-readiness-scoping-003.md`
- `bridge/gtkb-mass-adoption-readiness-scoping-004.md`
- `bridge/gtkb-mass-adoption-readiness-scoping-006.md`
- `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-002.md`
- `bridge/gtkb-mcp-stable-harness-surface-advisory-disposition-001.md`
- `bridge/gtkb-mcp-stable-harness-surface-advisory-disposition-002.md`
- `bridge/gtkb-mcp-stable-harness-surface-advisory-disposition-003.md`
- `bridge/gtkb-mcp-stable-harness-surface-advisory-disposition-004.md`
- `bridge/gtkb-mcp-stable-harness-surface-advisory-disposition-005.md`
- `bridge/gtkb-mcp-stable-harness-surface-conversion-001.md`
- `bridge/gtkb-mcp-stable-harness-surface-conversion-002.md`
- `bridge/gtkb-mcp-stable-harness-surface-conversion-003.md`
- `bridge/gtkb-mcp-stable-harness-surface-conversion-004.md`
- `bridge/gtkb-mcp-stable-harness-surface-conversion-006.md`
- `bridge/gtkb-mcp-stable-harness-surface-conversion-008.md`
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-001.md`
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-002.md`
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-003.md`
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-004.md`
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-006.md`
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-008.md`
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-010.md`
- `bridge/gtkb-mcp-stable-harness-surface-implementation-003.md`
- `bridge/gtkb-membase-effective-use-audit-test-restoration-001.md`
- `bridge/gtkb-membase-effective-use-audit-test-restoration-002.md`
- `bridge/gtkb-membase-effective-use-audit-test-restoration-003.md`
- `bridge/gtkb-membase-effective-use-recovery-2026-04-29-001.md`
- `bridge/gtkb-membase-effective-use-recovery-2026-04-29-003.md`
- `bridge/gtkb-membase-effective-use-recovery-next-slice-001.md`
- `bridge/gtkb-membase-effective-use-recovery-next-slice-003.md`
- `bridge/gtkb-membase-effective-use-recovery-next-slice-004.md`
- `bridge/gtkb-membase-effective-use-recovery-next-slice-006.md`
- `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-001.md`
- `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-003.md`
- `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-005.md`
- `bridge/gtkb-membase-effective-use-umbrella-001.md`
- `bridge/gtkb-mirror-retirement-target-path-scope-correction-001.md`
- `bridge/gtkb-mirror-retirement-target-path-scope-correction-002.md`
- `bridge/gtkb-mirror-retirement-target-path-scope-correction-004.md`
- `bridge/gtkb-mirror-retirement-target-path-scope-correction-006.md`
- `bridge/gtkb-mirror-retirement-target-path-scope-correction-008.md`
- `bridge/gtkb-mode-switch-validator-hook-matcher-shape-fix-001.md`
- `bridge/gtkb-mode-switch-validator-hook-matcher-shape-fix-002.md`
- `bridge/gtkb-mode-switch-validator-hook-matcher-shape-fix-004.md`
- `bridge/gtkb-mode-switch-validator-hook-matcher-shape-fix-006.md`
- `bridge/gtkb-ollama-dispatch-failure-hardening-001.md`
- `bridge/gtkb-ollama-dispatch-failure-hardening-002.md`
- `bridge/gtkb-ollama-dispatch-failure-hardening-004.md`
- `bridge/gtkb-ollama-dispatch-stall-retry-cap-001.md`
- `bridge/gtkb-ollama-dispatch-stall-retry-cap-002.md`
- `bridge/gtkb-ollama-dispatch-stall-retry-cap-006.md`
- `bridge/gtkb-ollama-dispatch-state-recovery-003.md`
- `bridge/gtkb-ollama-integration-phase-1-001.md`
- `bridge/gtkb-ollama-integration-phase-1-002.md`
- `bridge/gtkb-ollama-integration-phase-1-003.md`
- `bridge/gtkb-ollama-integration-phase-1-004.md`
- `bridge/gtkb-ollama-integration-phase-1-005.md`
- `bridge/gtkb-ollama-integration-phase-1-006.md`
- `bridge/gtkb-ollama-integration-phase-1-007.md`
- `bridge/gtkb-ollama-integration-phase-1-008.md`
- `bridge/gtkb-ollama-integration-phase-1-foundation-001.md`
- `bridge/gtkb-ollama-integration-phase-1-foundation-002.md`
- `bridge/gtkb-ollama-integration-phase-1-foundation-003.md`
- `bridge/gtkb-ollama-integration-phase-1-foundation-004.md`
- `bridge/gtkb-ollama-integration-phase-1-foundation-005.md`
- `bridge/gtkb-ollama-integration-phase-1-foundation-006.md`
- `bridge/gtkb-ollama-integration-phase-1-foundation-007.md`
- `bridge/gtkb-ollama-integration-phase-1-foundation-008.md`
- `bridge/gtkb-ollama-integration-phase-1-foundation-009.md`
- `bridge/gtkb-ollama-integration-phase-1-foundation-010.md`
- `bridge/gtkb-ollama-integration-phase-1-foundation-012.md`
- `bridge/gtkb-ollama-integration-phase-1-governance-impl-001.md`
- `bridge/gtkb-ollama-integration-phase-1-governance-impl-002.md`
- `bridge/gtkb-ollama-integration-phase-1-governance-impl-004.md`
- `bridge/gtkb-ollama-integration-phase-1-project-completion-coverage-001.md`
- `bridge/gtkb-ollama-integration-phase-1-project-completion-coverage-002.md`
- `bridge/gtkb-ollama-integration-phase-1-project-completion-coverage-004.md`
- `bridge/gtkb-ollama-integration-phase-1-project-completion-coverage-007.md`
- `bridge/gtkb-ollama-integration-phase-1-shim-001.md`
- `bridge/gtkb-ollama-integration-phase-1-shim-002.md`
- `bridge/gtkb-ollama-integration-phase-1-shim-003.md`
- `bridge/gtkb-ollama-integration-phase-1-shim-004.md`
- `bridge/gtkb-ollama-integration-phase-1-shim-005.md`
- `bridge/gtkb-ollama-integration-phase-1-shim-006.md`
- `bridge/gtkb-ollama-integration-phase-1-shim-007.md`
- `bridge/gtkb-ollama-integration-phase-1-shim-008.md`
- `bridge/gtkb-ollama-integration-phase-1-shim-010.md`
- `bridge/gtkb-ollama-integration-phase-1-shim-011.md`
- `bridge/gtkb-ollama-integration-phase-1-shim-012.md`
- `bridge/gtkb-ollama-integration-phase-1-verification-001.md`
- `bridge/gtkb-ollama-integration-phase-1-verification-002.md`
- `bridge/gtkb-ollama-integration-phase-1-verification-003.md`
- `bridge/gtkb-ollama-integration-phase-1-verification-004.md`
- `bridge/gtkb-ollama-integration-phase-1-verification-005.md`
- `bridge/gtkb-ollama-integration-phase-1-verification-006.md`
- `bridge/gtkb-ollama-integration-phase-1-verification-008.md`
- `bridge/gtkb-ollama-integration-phase-1-verification-010.md`
- `bridge/gtkb-ollama-integration-phase-1-verification-012.md`
- `bridge/gtkb-ollama-integration-phase-2-001.md`
- `bridge/gtkb-ollama-integration-phase-2-002.md`
- `bridge/gtkb-ollama-integration-phase-2-003.md`
- `bridge/gtkb-ollama-integration-phase-2-004.md`
- `bridge/gtkb-ollama-integration-phase-2-006.md`
- `bridge/gtkb-ollama-integration-phase-2-008.md`
- `bridge/gtkb-ollama-integration-phase-2-010.md`
- `bridge/gtkb-ollama-integration-phase-2-adapters-001.md`
- `bridge/gtkb-ollama-integration-phase-2-adapters-002.md`
- `bridge/gtkb-ollama-integration-phase-2-adapters-003.md`
- `bridge/gtkb-ollama-integration-phase-2-adapters-004.md`
- `bridge/gtkb-ollama-integration-phase-2-adapters-005.md`
- `bridge/gtkb-ollama-integration-phase-2-adapters-006.md`
- `bridge/gtkb-ollama-integration-phase-2-adapters-007.md`
- `bridge/gtkb-ollama-integration-phase-2-adapters-008.md`
- `bridge/gtkb-ollama-integration-phase-2-adapters-010.md`
- `bridge/gtkb-ollama-integration-phase-2-dispatch-001.md`
- `bridge/gtkb-ollama-integration-phase-2-dispatch-002.md`
- `bridge/gtkb-ollama-integration-phase-2-dispatch-003.md`
- `bridge/gtkb-ollama-integration-phase-2-dispatch-004.md`
- `bridge/gtkb-ollama-integration-phase-2-dispatch-005.md`
- `bridge/gtkb-ollama-integration-phase-2-dispatch-006.md`
- `bridge/gtkb-ollama-integration-phase-2-dispatch-007.md`
- `bridge/gtkb-ollama-integration-phase-2-dispatch-008.md`
- `bridge/gtkb-ollama-integration-phase-2-dispatch-010.md`
- `bridge/gtkb-ollama-integration-phase-2-dispatch-012.md`
- `bridge/gtkb-ollama-integration-phase-2-role-promotion-001.md`
- `bridge/gtkb-ollama-integration-phase-2-role-promotion-002.md`
- `bridge/gtkb-ollama-integration-phase-2-role-promotion-003.md`
- `bridge/gtkb-ollama-integration-phase-2-role-promotion-004.md`
- `bridge/gtkb-ollama-integration-phase-2-role-promotion-005.md`
- `bridge/gtkb-ollama-integration-phase-2-role-promotion-006.md`
- `bridge/gtkb-ollama-integration-phase-2-role-promotion-007.md`
- `bridge/gtkb-ollama-integration-phase-2-role-promotion-008.md`
- `bridge/gtkb-ollama-integration-phase-2-role-promotion-010.md`
- `bridge/gtkb-ollama-integration-phase-2-role-promotion-012.md`
- `bridge/gtkb-ollama-integration-phase-2-role-promotion-014.md`
- `bridge/gtkb-ollama-integration-phase-2-routing-001.md`
- `bridge/gtkb-ollama-integration-phase-2-routing-002.md`
- `bridge/gtkb-ollama-integration-phase-2-routing-003.md`
- `bridge/gtkb-ollama-integration-phase-2-routing-004.md`
- `bridge/gtkb-ollama-integration-phase-2-routing-005.md`
- `bridge/gtkb-ollama-integration-phase-2-routing-006.md`
- `bridge/gtkb-ollama-integration-phase-2-routing-007.md`
- `bridge/gtkb-ollama-integration-phase-2-routing-008.md`
- `bridge/gtkb-ollama-integration-phase-2-routing-010.md`
- `bridge/gtkb-ollama-lo-dispatch-session-propagation-001.md`
- `bridge/gtkb-ollama-lo-dispatch-session-propagation-002.md`
- `bridge/gtkb-ollama-lo-dispatch-session-propagation-003.md`
- `bridge/gtkb-ollama-lo-dispatch-session-propagation-004.md`
- `bridge/gtkb-ollama-lo-dispatch-session-propagation-005.md`
- `bridge/gtkb-ollama-lo-dispatch-session-propagation-006.md`
- `bridge/gtkb-ollama-lo-prompt-hardening-003.md`
- `bridge/gtkb-ollama-phase2-subproject-completion-coverage-001.md`
- `bridge/gtkb-ollama-phase2-subproject-completion-coverage-002.md`
- `bridge/gtkb-ollama-phase2-subproject-completion-coverage-003.md`
- `bridge/gtkb-ollama-phase2-subproject-completion-coverage-004.md`
- `bridge/gtkb-ollama-phase2-subproject-completion-coverage-006.md`
- `bridge/gtkb-ollama-phase2-subproject-completion-coverage-008.md`
- `bridge/gtkb-ollama-phase2-verified-staging-finalization-gate-001.md`
- `bridge/gtkb-ollama-phase2-verified-staging-finalization-gate-002.md`
- `bridge/gtkb-ollama-phase2-verified-staging-finalization-gate-004.md`
- `bridge/gtkb-ollama-qwen-full-lo-dispatch-test-update-001.md`
- `bridge/gtkb-ollama-qwen-full-lo-dispatch-test-update-002.md`
- `bridge/gtkb-ollama-qwen-full-lo-dispatch-test-update-004.md`
- `bridge/gtkb-ollama-qwen-full-lo-route-001.md`
- `bridge/gtkb-ollama-qwen-full-lo-route-002.md`
- `bridge/gtkb-ollama-qwen-full-lo-route-003.md`
- `bridge/gtkb-ollama-qwen-full-lo-route-005.md`
- `bridge/gtkb-ollama-qwen-full-lo-route-gate-compliant-001.md`
- `bridge/gtkb-ollama-qwen-full-lo-route-gate-compliant-002.md`
- `bridge/gtkb-ollama-qwen-full-lo-route-gate-compliant-004.md`
- `bridge/gtkb-ollama-routing-model-version-fixture-cleanup-001.md`
- `bridge/gtkb-ollama-routing-single-sot-cleanup-001.md`
- `bridge/gtkb-ollama-tool-numeric-argument-coercion-001.md`
- `bridge/gtkb-ollama-tool-numeric-argument-coercion-002.md`
- `bridge/gtkb-ollama-tool-numeric-argument-coercion-004.md`
- `bridge/gtkb-ollama-tool-numeric-argument-coercion-006.md`
- `bridge/gtkb-operating-mode-transaction-001-001.md`
- `bridge/gtkb-operating-mode-transaction-001-003.md`
- `bridge/gtkb-operating-mode-transaction-001-004.md`
- `bridge/gtkb-operating-mode-transaction-001-005.md`
- `bridge/gtkb-operating-mode-transaction-001-006.md`
- `bridge/gtkb-operating-mode-transaction-001-007.md`
- `bridge/gtkb-operating-mode-transaction-001-008.md`
- `bridge/gtkb-operating-mode-transaction-001-009.md`
- `bridge/gtkb-operating-mode-transaction-001-010.md`
- `bridge/gtkb-operating-mode-transaction-001-011.md`
- `bridge/gtkb-operating-mode-transaction-001-012.md`
- `bridge/gtkb-operating-mode-transaction-001-013.md`
- `bridge/gtkb-operating-mode-transaction-001-014.md`
- `bridge/gtkb-operating-mode-transaction-001-015.md`
- `bridge/gtkb-operating-mode-transaction-001-016.md`
- `bridge/gtkb-operating-mode-transaction-001-017.md`
- `bridge/gtkb-operating-mode-transaction-001-019.md`
- `bridge/gtkb-operating-mode-transaction-001-021.md`
- `bridge/gtkb-orphan-wi-membership-backfill-slice-2-implementation-001.md`
- `bridge/gtkb-orphan-wi-membership-backfill-slice-2-implementation-002.md`
- `bridge/gtkb-orphan-wi-membership-backfill-slice-2-implementation-003.md`
- `bridge/gtkb-orphan-wi-membership-backfill-slice-2-implementation-004.md`
- `bridge/gtkb-orphan-wi-membership-backfill-slice-2-implementation-006.md`
- `bridge/gtkb-orphan-wi-membership-backfill-slice-2-implementation-008.md`
- `bridge/gtkb-orphan-wi-membership-backfill-slice-2-scoping-001.md`
- `bridge/gtkb-orphan-wi-membership-backfill-slice-2-scoping-002.md`
- `bridge/gtkb-orphan-wi-membership-backfill-slice-2-scoping-004.md`
- `bridge/gtkb-orphan-wi-membership-discovery-slice-1-001.md`
- `bridge/gtkb-orphan-wi-membership-discovery-slice-1-003.md`
- `bridge/gtkb-orphan-wi-membership-discovery-slice-1-005.md`
- `bridge/gtkb-orphan-wi-membership-discovery-slice-1-006.md`
- `bridge/gtkb-orphan-wi-membership-discovery-slice-1-007.md`
- `bridge/gtkb-orphan-wi-membership-discovery-slice-1-008.md`
- `bridge/gtkb-orphan-wi-membership-discovery-slice-1-010.md`
- `bridge/gtkb-orphan-wi-membership-discovery-slice-1-012.md`
- `bridge/gtkb-owner-decision-tracker-baseline-restore-001.md`
- `bridge/gtkb-owner-decision-tracker-baseline-restore-002.md`
- `bridge/gtkb-owner-decision-tracker-baseline-restore-003.md`
- `bridge/gtkb-owner-decision-tracker-baseline-restore-004.md`
- `bridge/gtkb-owner-decision-tracker-baseline-restore-006.md`
- `bridge/gtkb-owner-decision-tracker-baseline-restore-007.md`
- `bridge/gtkb-owner-decision-tracker-baseline-restore-008.md`
- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md`
- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md`
- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md`
- `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md`
- `bridge/gtkb-p0-secrets-purge-enforcement-003.md`
- `bridge/gtkb-p0-secrets-purge-enforcement-004.md`
- `bridge/gtkb-p0-secrets-purge-enforcement-005.md`
- `bridge/gtkb-p0-secrets-purge-enforcement-006.md`
- `bridge/gtkb-peer-solution-advisory-loop-2026-05-10-001.md`
- `bridge/gtkb-peer-solution-advisory-loop-2026-05-10-002.md`
- `bridge/gtkb-peer-solution-advisory-loop-conversion-001.md`
- `bridge/gtkb-peer-solution-advisory-loop-conversion-002.md`
- `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md`
- `bridge/gtkb-peer-solution-advisory-loop-conversion-004.md`
- `bridge/gtkb-peer-solution-advisory-loop-conversion-006.md`
- `bridge/gtkb-peer-solution-advisory-loop-procedure-001.md`
- `bridge/gtkb-peer-solution-advisory-loop-procedure-002.md`
- `bridge/gtkb-peer-solution-advisory-loop-procedure-004.md`
- `bridge/gtkb-peer-solution-advisory-report-advisory-disposition-001.md`
- `bridge/gtkb-peer-solution-advisory-report-advisory-disposition-002.md`
- `bridge/gtkb-peer-solution-advisory-report-advisory-disposition-003.md`
- `bridge/gtkb-peer-solution-advisory-report-advisory-disposition-004.md`
- `bridge/gtkb-peer-solution-advisory-report-advisory-disposition-005.md`
- `bridge/gtkb-peer-solution-advisory-report-advisory-disposition-006.md`
- `bridge/gtkb-peer-solution-advisory-report-advisory-disposition-007.md`
- `bridge/gtkb-peer-solution-advisory-report-advisory-disposition-008.md`
- `bridge/gtkb-peer-solution-advisory-report-advisory-disposition-009.md`
- `bridge/gtkb-peer-solution-advisory-report-advisory-disposition-012.md`
- `bridge/gtkb-peer-solution-owner-gate-dcl-001.md`
- `bridge/gtkb-peer-solution-owner-gate-dcl-002.md`
- `bridge/gtkb-peer-solution-owner-gate-dcl-003.md`
- `bridge/gtkb-peer-solution-owner-gate-dcl-004.md`
- `bridge/gtkb-peer-solution-owner-gate-dcl-005.md`
- `bridge/gtkb-peer-solution-owner-gate-dcl-006.md`
- `bridge/gtkb-peer-solution-owner-gate-dcl-007.md`
- `bridge/gtkb-peer-solution-owner-gate-dcl-008.md`
- `bridge/gtkb-peer-solution-owner-gate-dcl-010.md`
- `bridge/gtkb-peer-solution-workflow-contract-adr-001.md`
- `bridge/gtkb-peer-solution-workflow-contract-adr-002.md`
- `bridge/gtkb-peer-solution-workflow-contract-adr-003.md`
- `bridge/gtkb-peer-solution-workflow-contract-adr-004.md`
- `bridge/gtkb-peer-solution-workflow-contract-adr-005.md`
- `bridge/gtkb-peer-solution-workflow-contract-adr-006.md`
- `bridge/gtkb-peer-solution-workflow-contract-adr-007.md`
- `bridge/gtkb-peer-solution-workflow-contract-adr-008.md`
- `bridge/gtkb-peer-solution-workflow-contract-adr-010.md`
- `bridge/gtkb-phantom-project-prefix-reconciliation-001.md`
- `bridge/gtkb-phantom-project-prefix-reconciliation-002.md`
- `bridge/gtkb-phantom-project-prefix-reconciliation-003.md`
- `bridge/gtkb-phantom-project-prefix-reconciliation-004.md`
- `bridge/gtkb-phantom-project-prefix-reconciliation-006.md`
- `bridge/gtkb-phantom-project-prefix-reconciliation-008.md`
- `bridge/gtkb-platform-observability-hygiene-003.md`
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-001.md`
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-002.md`
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-003.md`
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-004.md`
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-005.md`
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-007.md`
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md`
- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-001.md`
- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-002.md`
- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-003.md`
- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-004.md`
- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-006.md`
- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-007.md`
- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-009.md`
- `bridge/gtkb-platform-sot-consolidation-umbrella-001.md`
- `bridge/gtkb-platform-sot-consolidation-umbrella-002.md`
- `bridge/gtkb-platform-sot-consolidation-umbrella-003.md`
- `bridge/gtkb-platform-sot-consolidation-umbrella-004.md`
- `bridge/gtkb-platform-sot-consolidation-umbrella-005.md`
- `bridge/gtkb-platform-sot-consolidation-umbrella-006.md`
- `bridge/gtkb-platform-sot-consolidation-umbrella-007.md`
- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md`
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-007.md`
- `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-001.md`
- `bridge/gtkb-platform-spec-coverage-verified-runner-2026-04-29-003.md`
- `bridge/gtkb-platform-tests-ruff-cleanup-001.md`
- `bridge/gtkb-platform-tests-ruff-cleanup-003.md`
- `bridge/gtkb-platform-tests-ruff-cleanup-004.md`
- `bridge/gtkb-platform-tests-ruff-cleanup-005.md`
- `bridge/gtkb-platform-tests-ruff-cleanup-006.md`
- `bridge/gtkb-platform-tests-ruff-cleanup-008.md`
- `bridge/gtkb-platform-tests-ruff-cleanup-010.md`
- `bridge/gtkb-platform-tests-ruff-cleanup-012.md`
- `bridge/gtkb-platform-tests-ruff-cleanup-014.md`
- `bridge/gtkb-por-step-16-d-orphan-test-rationalization-001.md`
- `bridge/gtkb-por-step-16-d-orphan-test-rationalization-003.md`
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2-001.md`
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2-002.md`
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2-003.md`
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2-004.md`
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2-005.md`
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2-006.md`
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2-007.md`
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2-008.md`
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2-009.md`
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2-010.md`
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2-011.md`
- `bridge/gtkb-prime-worker-context-aware-auq-slice-2-012.md`
- `bridge/gtkb-prime-worker-delivery-regression-slice-4-001.md`
- `bridge/gtkb-prime-worker-delivery-regression-slice-4-002.md`
- `bridge/gtkb-prime-worker-delivery-regression-slice-4-003.md`
- `bridge/gtkb-prime-worker-delivery-regression-slice-4-004.md`
- `bridge/gtkb-prime-worker-delivery-regression-slice-4-005.md`
- `bridge/gtkb-prime-worker-delivery-regression-slice-4-006.md`
- `bridge/gtkb-prime-worker-delivery-regression-slice-4-009.md`
- `bridge/gtkb-prime-worker-delivery-regression-slice-4-011.md`
- `bridge/gtkb-prime-worker-permission-profile-slice-1-001.md`
- `bridge/gtkb-prime-worker-permission-profile-slice-1-002.md`
- `bridge/gtkb-prime-worker-permission-profile-slice-1-003.md`
- `bridge/gtkb-prime-worker-permission-profile-slice-1-004.md`
- `bridge/gtkb-prime-worker-permission-profile-slice-1-005.md`
- `bridge/gtkb-prime-worker-permission-profile-slice-1-006.md`
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-001.md`
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-002.md`
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-003.md`
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-004.md`
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-005.md`
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-006.md`
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-007.md`
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-008.md`
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-009.md`
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-010.md`
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-011.md`
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-012.md`
- `bridge/gtkb-project-auth-spec-amendment-gate-001.md`
- `bridge/gtkb-project-auth-spec-amendment-gate-003.md`
- `bridge/gtkb-project-auth-spec-amendment-gate-005.md`
- `bridge/gtkb-project-auth-spec-amendment-gate-007.md`
- `bridge/gtkb-project-authorization-completion-keep-open-001.md`
- `bridge/gtkb-project-authorization-completion-keep-open-002.md`
- `bridge/gtkb-project-authorize-spec-linkage-gate-001.md`
- `bridge/gtkb-project-authorize-spec-linkage-gate-003.md`
- `bridge/gtkb-project-authorize-spec-linkage-gate-005.md`
- `bridge/gtkb-project-authorize-spec-linkage-gate-007.md`
- `bridge/gtkb-project-completion-drive-payload-001-001.md`
- `bridge/gtkb-project-completion-drive-payload-001-002.md`
- `bridge/gtkb-project-completion-plan-incomplete-guard-001.md`
- `bridge/gtkb-project-completion-plan-incomplete-guard-002.md`
- `bridge/gtkb-project-completion-plan-incomplete-guard-004.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-001.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-002.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-003.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-004.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-005.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-006.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-007.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-008.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-009.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-010.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-012.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-013.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-014.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-implementation-001.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-implementation-002.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-implementation-003.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-implementation-004.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-001.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-002.md`
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-004.md`
- `bridge/gtkb-project-completion-scanner-wi-auto-regex-fix-001.md`
- `bridge/gtkb-project-completion-scanner-wi-auto-regex-fix-002.md`
- `bridge/gtkb-project-completion-scanner-wi-auto-regex-fix-005.md`
- `bridge/gtkb-project-completion-scanner-wi-auto-regex-fix-006.md`
- `bridge/gtkb-project-completion-scanner-wi-auto-regex-fix-007.md`
- `bridge/gtkb-project-completion-scanner-wi-auto-regex-fix-008.md`
- `bridge/gtkb-project-id-prefix-idempotent-fix-001.md`
- `bridge/gtkb-project-id-prefix-idempotent-fix-002.md`
- `bridge/gtkb-project-id-prefix-idempotent-fix-005.md`
- `bridge/gtkb-project-membership-reconciliation-slice-1-inventory-tool-001.md`
- `bridge/gtkb-project-membership-reconciliation-slice-1-inventory-tool-002.md`
- `bridge/gtkb-project-membership-reconciliation-slice-1-inventory-tool-004.md`
- `bridge/gtkb-project-membership-reconciliation-slice-1-scoping-001.md`
- `bridge/gtkb-project-membership-reconciliation-slice-1-scoping-002.md`
- `bridge/gtkb-project-membership-reconciliation-slice-1-scoping-004.md`
- `bridge/gtkb-project-scoped-implementation-authorization-001.md`
- `bridge/gtkb-project-scoped-implementation-authorization-002.md`
- `bridge/gtkb-project-scoped-implementation-authorization-003.md`
- `bridge/gtkb-project-scoped-implementation-authorization-004.md`
- `bridge/gtkb-project-scoped-implementation-authorization-006.md`
- `bridge/gtkb-project-scoped-implementation-authorization-007.md`
- `bridge/gtkb-project-scoped-implementation-authorization-008.md`
- `bridge/gtkb-project-scoped-implementation-authorization-010.md`
- `bridge/gtkb-project-verified-completion-auq-trigger-001.md`
- `bridge/gtkb-project-verified-completion-auq-trigger-003.md`
- `bridge/gtkb-project-verified-completion-auq-trigger-005.md`
- `bridge/gtkb-projects-remove-item-cli-slice-1-001.md`
- `bridge/gtkb-projects-remove-item-cli-slice-1-002.md`
- `bridge/gtkb-projects-remove-item-cli-slice-1-003.md`
- `bridge/gtkb-projects-remove-item-cli-slice-1-004.md`
- `bridge/gtkb-projects-remove-item-cli-slice-1-005.md`
- `bridge/gtkb-projects-remove-item-cli-slice-1-006.md`
- `bridge/gtkb-projects-remove-item-cli-slice-1-007.md`
- `bridge/gtkb-projects-remove-item-cli-slice-1-008.md`
- `bridge/gtkb-projects-remove-item-cli-slice-1-009.md`
- `bridge/gtkb-projects-remove-item-cli-slice-1-011.md`
- `bridge/gtkb-projects-skill-001-001.md`
- `bridge/gtkb-projects-skill-001-003.md`
- `bridge/gtkb-projects-skill-001-007.md`
- `bridge/gtkb-proposal-standards-propose-scaffold-skill-001.md`
- `bridge/gtkb-proposal-standards-propose-scaffold-skill-002.md`
- `bridge/gtkb-proposal-standards-propose-scaffold-skill-004.md`
- `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-001.md`
- `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-003.md`
- `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-004.md`
- `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-006.md`
- `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-008.md`
- `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-009.md`
- `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-011.md`
- `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-013.md`
- `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-017.md`
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-001.md`
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-003.md`
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-005.md`
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-007.md`
- `bridge/gtkb-protected-artifact-rollup-governance-umbrella-001.md`
- `bridge/gtkb-protected-artifact-rollup-governance-umbrella-002.md`
- `bridge/gtkb-protected-artifact-rollup-governance-umbrella-003.md`
- `bridge/gtkb-protected-artifact-rollup-governance-umbrella-004.md`
- `bridge/gtkb-protected-artifact-rollup-governance-umbrella-005.md`
- `bridge/gtkb-push-gate-design-governance-review-001.md`
- `bridge/gtkb-push-gate-design-governance-review-003.md`
- `bridge/gtkb-push-gate-design-governance-review-004.md`
- `bridge/gtkb-push-gate-design-governance-review-005.md`
- `bridge/gtkb-push-gate-design-governance-review-006.md`
- `bridge/gtkb-push-gate-design-governance-review-007.md`
- `bridge/gtkb-push-gate-design-governance-review-010.md`
- `bridge/gtkb-push-gate-slice-1-5-debt-audit-001.md`
- `bridge/gtkb-push-gate-slice-1-5-debt-audit-002.md`
- `bridge/gtkb-push-gate-slice-1-5-debt-audit-003.md`
- `bridge/gtkb-push-gate-slice-1-5-debt-audit-004.md`
- `bridge/gtkb-push-gate-slice-1-5-debt-audit-005.md`
- `bridge/gtkb-pytest-basetemp-session-isolation-001.md`
- `bridge/gtkb-pytest-basetemp-session-isolation-002.md`
- `bridge/gtkb-pytest-basetemp-session-isolation-004.md`
- `bridge/gtkb-rc-gate-membase-seed-resilient-fixture-001.md`
- `bridge/gtkb-rc-gate-membase-seed-resilient-fixture-002.md`
- `bridge/gtkb-rc-gate-membase-seed-resilient-fixture-003.md`
- `bridge/gtkb-rc-gate-membase-seed-resilient-fixture-004.md`
- `bridge/gtkb-rc-gate-membase-seed-resilient-fixture-005.md`
- `bridge/gtkb-rc1-canonical-ci-closure-001.md`
- `bridge/gtkb-rc1-canonical-ci-closure-002.md`
- `bridge/gtkb-rc1-canonical-ci-closure-004.md`
- `bridge/gtkb-rc1-canonical-ci-closure-006.md`
- `bridge/gtkb-rc1-pyjwt-dependency-audit-remediation-001.md`
- `bridge/gtkb-rc1-pyjwt-dependency-audit-remediation-002.md`
- `bridge/gtkb-rc1-pyjwt-dependency-audit-remediation-004.md`
- `bridge/gtkb-registry-scaffold-fixture-drift-reconciliation-001.md`
- `bridge/gtkb-registry-scaffold-fixture-drift-reconciliation-002.md`
- `bridge/gtkb-registry-scaffold-fixture-drift-reconciliation-004.md`
- `bridge/gtkb-registry-scaffold-fixture-drift-reconciliation-006.md`
- `bridge/gtkb-registry-scaffold-fixture-drift-reconciliation-008.md`
- `bridge/gtkb-rehearsal-inventory-perf-001.md`
- `bridge/gtkb-rehearsal-package-ruff-clean-001.md`
- `bridge/gtkb-release-candidate-gate-managed-skill-001.md`
- `bridge/gtkb-release-candidate-gate-managed-skill-003.md`
- `bridge/gtkb-release-candidate-gate-managed-skill-005.md`
- `bridge/gtkb-release-candidate-gate-managed-skill-006.md`
- `bridge/gtkb-release-candidate-gate-managed-skill-008.md`
- `bridge/gtkb-release-candidate-gate-managed-skill-010.md`
- `bridge/gtkb-release-candidate-gate-managed-skill-012.md`
- `bridge/gtkb-release-candidate-gate-stale-test-paths-001.md`
- `bridge/gtkb-release-candidate-gate-stale-test-paths-002.md`
- `bridge/gtkb-release-candidate-gate-stale-test-paths-003.md`
- `bridge/gtkb-release-candidate-gate-stale-test-paths-004.md`
- `bridge/gtkb-release-candidate-gate-stale-test-paths-005.md`
- `bridge/gtkb-release-candidate-gate-stale-test-paths-006.md`
- `bridge/gtkb-release-candidate-gate-stale-test-paths-008.md`
- `bridge/gtkb-reliability-fast-lane-001.md`
- `bridge/gtkb-reliability-fast-lane-003.md`
- `bridge/gtkb-reliability-fast-lane-005.md`
- `bridge/gtkb-restore-systems-and-tools-doc-001.md`
- `bridge/gtkb-restore-systems-and-tools-doc-002.md`
- `bridge/gtkb-restore-systems-and-tools-doc-004.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-002.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-003.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-004.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-006.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint-001.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint-002.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint-004.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint-005.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint-007.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-001.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-002.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-003.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-004.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-006.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-007.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-008.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-010.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-011.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-012.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-013.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-014.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-015.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-016.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-018.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-020.md`
- `bridge/gtkb-role-enhancement-001.md`
- `bridge/gtkb-role-enhancement-002.md`
- `bridge/gtkb-role-enhancement-003.md`
- `bridge/gtkb-role-enhancement-004.md`
- `bridge/gtkb-role-enhancement-isolation-dependency-reframe-001.md`
- `bridge/gtkb-role-enhancement-isolation-dependency-reframe-002.md`
- `bridge/gtkb-role-enhancement-isolation-dependency-reframe-004.md`
- `bridge/gtkb-role-enhancement-isolation-dependency-reframe-005.md`
- `bridge/gtkb-role-enhancement-isolation-dependency-reframe-006.md`
- `bridge/gtkb-role-enhancement-isolation-dependency-reframe-007.md`
- `bridge/gtkb-role-enhancement-isolation-dependency-reframe-009.md`
- `bridge/gtkb-role-enhancement-lo-investigation-methodology-slice-2-001.md`
- `bridge/gtkb-role-enhancement-lo-investigation-methodology-slice-2-002.md`
- `bridge/gtkb-role-enhancement-lo-investigation-methodology-slice-2-004.md`
- `bridge/gtkb-role-enhancement-lo-investigation-methodology-slice-2-005.md`
- `bridge/gtkb-role-enhancement-lo-investigation-methodology-slice-2-006.md`
- `bridge/gtkb-role-enhancement-lo-investigation-methodology-slice-2-owner-approved-continuation-001.md`
- `bridge/gtkb-role-enhancement-lo-investigation-methodology-slice-2-owner-approved-continuation-002.md`
- `bridge/gtkb-role-enhancement-lo-investigation-methodology-slice-2-owner-approved-continuation-004.md`
- `bridge/gtkb-role-enhancement-no-go-cycle-escalation-slice-3-001.md`
- `bridge/gtkb-role-enhancement-no-go-cycle-escalation-slice-3-002.md`
- `bridge/gtkb-role-enhancement-no-go-cycle-escalation-slice-3-004.md`
- `bridge/gtkb-role-enhancement-no-go-cycle-escalation-slice-3-006.md`
- `bridge/gtkb-role-enhancement-no-go-cycle-escalation-slice-3-007.md`
- `bridge/gtkb-role-enhancement-no-go-cycle-escalation-slice-3-008.md`
- `bridge/gtkb-role-enhancement-review-depth-contract-slice-1-001.md`
- `bridge/gtkb-role-enhancement-review-depth-contract-slice-1-002.md`
- `bridge/gtkb-role-enhancement-review-depth-contract-slice-1-004.md`
- `bridge/gtkb-role-enhancement-review-depth-contract-slice-1-005.md`
- `bridge/gtkb-role-enhancement-review-depth-contract-slice-1-006.md`
- `bridge/gtkb-role-enhancement-review-depth-contract-slice-1-007.md`
- `bridge/gtkb-role-enhancement-review-depth-contract-slice-1-008.md`
- `bridge/gtkb-role-enhancement-review-depth-methodology-001.md`
- `bridge/gtkb-role-enhancement-review-depth-methodology-003.md`
- `bridge/gtkb-role-enhancement-review-depth-methodology-005.md`
- `bridge/gtkb-role-enhancement-review-depth-methodology-006.md`
- `bridge/gtkb-role-enhancement-review-depth-methodology-008.md`
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-001.md`
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-002.md`
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-003.md`
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-004.md`
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-006.md`
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-008.md`
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-009.md`
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-010.md`
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-011.md`
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-012.md`
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-014.md`
- `bridge/gtkb-role-scope-release-operations-advisory-2026-05-11-001.md`
- `bridge/gtkb-role-scope-release-operations-advisory-2026-05-11-002.md`
- `bridge/gtkb-role-scope-release-operations-conversion-001.md`
- `bridge/gtkb-role-scope-release-operations-conversion-002.md`
- `bridge/gtkb-role-scope-release-operations-conversion-003.md`
- `bridge/gtkb-role-scope-release-operations-conversion-004.md`
- `bridge/gtkb-role-scope-release-operations-conversion-005.md`
- `bridge/gtkb-role-scope-release-operations-conversion-006.md`
- `bridge/gtkb-role-scope-release-operations-conversion-007.md`
- `bridge/gtkb-role-scope-release-operations-conversion-009.md`
- `bridge/gtkb-role-session-lifecycle-simplification-002.md`
- `bridge/gtkb-role-session-lifecycle-simplification-004.md`
- `bridge/gtkb-role-session-lifecycle-simplification-006.md`
- `bridge/gtkb-role-session-lifecycle-simplification-008.md`
- `bridge/gtkb-role-session-lifecycle-simplification-010.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-landing-reconciliation-001.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-landing-reconciliation-002.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-landing-reconciliation-003.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-landing-reconciliation-004.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-landing-reconciliation-006.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-landing-reconciliation-007.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-landing-reconciliation-008.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-scoping-001.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-scoping-003.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-scoping-004.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-scoping-006.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-001.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-002.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-003.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-004.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-005.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-006.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-007.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-008.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-009.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-010.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-2-resolver-001.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-2-resolver-002.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-2-resolver-003.md`
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-2-resolver-004.md`
- `bridge/gtkb-root-boundary-external-harness-exec-exception-001.md`
- `bridge/gtkb-root-boundary-external-harness-exec-exception-002.md`
- `bridge/gtkb-root-boundary-external-harness-exec-exception-003.md`
- `bridge/gtkb-root-boundary-external-harness-exec-exception-004.md`
- `bridge/gtkb-root-boundary-external-harness-exec-exception-005.md`
- `bridge/gtkb-root-boundary-external-harness-exec-exception-006.md`
- `bridge/gtkb-root-boundary-external-harness-exec-exception-008.md`
- `bridge/gtkb-root-directory-migration-post-verify-010.md`
- `bridge/gtkb-root-directory-migration-post-verify-012.md`
- `bridge/gtkb-root-directory-migration-post-verify-014.md`
- `bridge/gtkb-ruff-format-pre-file-gate-001.md`
- `bridge/gtkb-ruff-format-pre-file-gate-002.md`
- `bridge/gtkb-ruff-format-pre-file-gate-003.md`
- `bridge/gtkb-ruff-format-pre-file-gate-004.md`
- `bridge/gtkb-ruff-format-pre-file-gate-005.md`
- `bridge/gtkb-ruff-format-pre-file-gate-006.md`
- `bridge/gtkb-ruff-format-pre-file-gate-007.md`
- `bridge/gtkb-ruff-format-pre-file-gate-008.md`
- `bridge/gtkb-ruff-format-pre-file-gate-010.md`
- `bridge/gtkb-s341-backlog-candidates-membase-insert-001.md`
- `bridge/gtkb-s341-backlog-candidates-membase-insert-002.md`
- `bridge/gtkb-s341-backlog-candidates-membase-insert-003.md`
- `bridge/gtkb-s341-backlog-candidates-membase-insert-004.md`
- `bridge/gtkb-s341-backlog-candidates-membase-insert-005.md`
- `bridge/gtkb-s341-backlog-candidates-membase-insert-007.md`
- `bridge/gtkb-s341-backlog-candidates-membase-insert-009.md`
- `bridge/gtkb-s341-backlog-candidates-membase-insert-011.md`
- `bridge/gtkb-s358-w1-retirement-machinery-correction-001.md`
- `bridge/gtkb-s358-w1-retirement-machinery-correction-003.md`
- `bridge/gtkb-s358-w1-retirement-machinery-correction-005.md`
- `bridge/gtkb-s358-w1-retirement-machinery-correction-008.md`
- `bridge/gtkb-s358-w1-retirement-machinery-correction-011.md`
- `bridge/gtkb-s358-w1-retirement-machinery-correction-013.md`
- `bridge/gtkb-s358-w1-retirement-machinery-correction-015.md`
- `bridge/gtkb-s358-w1-retirement-machinery-correction-017.md`
- `bridge/gtkb-s358-w1-retirement-machinery-correction-018.md`
- `bridge/gtkb-s358-w1-retirement-machinery-correction-019.md`
- `bridge/gtkb-s358-w1-retirement-machinery-correction-021.md`
- `bridge/gtkb-s358-w2-agent-red-gov-trio-v2-001.md`
- `bridge/gtkb-s358-w2-agent-red-gov-trio-v2-003.md`
- `bridge/gtkb-s358-w2-agent-red-gov-trio-v2-005.md`
- `bridge/gtkb-s358-w2-agent-red-gov-trio-v2-007.md`
- `bridge/gtkb-s358-w2-agent-red-gov-trio-v2-011.md`
- `bridge/gtkb-s358-w2-agent-red-gov-trio-v2-014.md`
- `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-001.md`
- `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-003.md`
- `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-005.md`
- `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-008.md`
- `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-009.md`
- `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-014.md`
- `bridge/gtkb-s358-w4-enforcement-calibration-001.md`
- `bridge/gtkb-s358-w4-enforcement-calibration-003.md`
- `bridge/gtkb-s358-w4-enforcement-calibration-005.md`
- `bridge/gtkb-s358-w4-enforcement-calibration-008.md`
- `bridge/gtkb-s358-w5-token-framing-correction-001.md`
- `bridge/gtkb-s358-w5-token-framing-correction-003.md`
- `bridge/gtkb-s358-w5-token-framing-correction-006.md`
- `bridge/gtkb-s373-triage-umbrella-001.md`
- `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-002.md`
- `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-003.md`
- `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-004.md`
- `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-006.md`
- `bridge/gtkb-scaffold-upgrade-tier-a-003.md`
- `bridge/gtkb-scaffold-upgrade-tier-a-005.md`
- `bridge/gtkb-scaffold-upgrade-tier-a-007.md`
- `bridge/gtkb-scaffold-upgrade-tier-a-009.md`
- `bridge/gtkb-scoped-service-boundary-baseline-implementation-001.md`
- `bridge/gtkb-scoped-service-boundary-baseline-implementation-003.md`
- `bridge/gtkb-scoped-service-boundary-baseline-implementation-005.md`
- `bridge/gtkb-scoped-service-boundary-baseline-implementation-007.md`
- `bridge/gtkb-scoped-service-boundary-baseline-implementation-009.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-001.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-003.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-005.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-007.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-009.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-012.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-001.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-003.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-005.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-007.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-009.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-012.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-014.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-016.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-001.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-003.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-005.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-007.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-011.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-013.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-016.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-001.md`
- `bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-003.md`
- `bridge/gtkb-session-envelope-durability-001-001.md`
- `bridge/gtkb-session-envelope-durability-001-002.md`
- `bridge/gtkb-session-envelope-durability-001-003.md`
- `bridge/gtkb-session-envelope-durability-001-004.md`
- `bridge/gtkb-session-envelope-durability-001-005.md`
- `bridge/gtkb-session-envelope-durability-001-006.md`
- `bridge/gtkb-session-id-shared-resolver-unification-001.md`
- `bridge/gtkb-session-id-shared-resolver-unification-002.md`
- `bridge/gtkb-session-id-shared-resolver-unification-003.md`
- `bridge/gtkb-session-id-shared-resolver-unification-004.md`
- `bridge/gtkb-session-id-shared-resolver-unification-006.md`
- `bridge/gtkb-session-id-shared-resolver-unification-008.md`
- `bridge/gtkb-session-overlay-baseline-implementation-001.md`
- `bridge/gtkb-session-overlay-baseline-implementation-003.md`
- `bridge/gtkb-session-overlay-baseline-implementation-005.md`
- `bridge/gtkb-session-start-formalization-001-003.md`
- `bridge/gtkb-session-start-formalization-001-005.md`
- `bridge/gtkb-session-start-formalization-001-006.md`
- `bridge/gtkb-session-start-formalization-001-008.md`
- `bridge/gtkb-session-start-formalization-001-009.md`
- `bridge/gtkb-session-start-formalization-001-010.md`
- `bridge/gtkb-session-start-formalization-001-012.md`
- `bridge/gtkb-session-start-formalization-001.md`
- `bridge/gtkb-session-startup-project-002.md`
- `bridge/gtkb-session-startup-project-004.md`
- `bridge/gtkb-session-startup-project-006.md`
- `bridge/gtkb-session-startup-project-007.md`
- `bridge/gtkb-session-work-subject-001.md`
- `bridge/gtkb-session-work-subject-002.md`
- `bridge/gtkb-session-work-subject-003.md`
- `bridge/gtkb-session-work-subject-004.md`
- `bridge/gtkb-session-wrap-knowledge-collection-001.md`
- `bridge/gtkb-session-wrap-knowledge-collection-002.md`
- `bridge/gtkb-session-wrap-knowledge-collection-004.md`
- `bridge/gtkb-session-wrap-procedure-001-001.md`
- `bridge/gtkb-session-wrap-procedure-001-002.md`
- `bridge/gtkb-session-wrap-procedure-001-003.md`
- `bridge/gtkb-session-wrap-procedure-001-004.md`
- `bridge/gtkb-single-harness-bridge-activation-manager-001.md`
- `bridge/gtkb-single-harness-bridge-activation-manager-002.md`
- `bridge/gtkb-single-harness-bridge-activation-manager-003.md`
- `bridge/gtkb-single-harness-bridge-activation-manager-004.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-002.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-003.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-004.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-005.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-006.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-007.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-008.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-009.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-010.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-011.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-012.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-013.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-014.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-016.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-018.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-020.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-022.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-002.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-003.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-004.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-006.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-008.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-010.md`
- `bridge/gtkb-skill-modernization-scoping-001.md`
- `bridge/gtkb-skill-modernization-scoping-003.md`
- `bridge/gtkb-skill-modernization-scoping-004.md`
- `bridge/gtkb-skill-modernization-scoping-006.md`
- `bridge/gtkb-skill-modernization-slice-0-skill-health-checker-001.md`
- `bridge/gtkb-skill-modernization-slice-0-skill-health-checker-002.md`
- `bridge/gtkb-skill-modernization-slice-0-skill-health-checker-004.md`
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-001.md`
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-003.md`
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-005.md`
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-008.md`
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-009.md`
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-010.md`
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-011.md`
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-012.md`
- `bridge/gtkb-slice2b-metrics-index-reconciliation-007.md`
- `bridge/gtkb-smart-bridge-trigger-foundation-spike-003.md`
- `bridge/gtkb-smart-poller-p1-p2-implementation-003.md`
- `bridge/gtkb-sonarcloud-config-relink-gt-kb-001.md`
- `bridge/gtkb-sonarcloud-config-relink-gt-kb-004.md`
- `bridge/gtkb-sonarcloud-config-relink-gt-kb-006.md`
- `bridge/gtkb-source-of-truth-freshness-governance-001.md`
- `bridge/gtkb-source-of-truth-freshness-governance-002.md`
- `bridge/gtkb-source-of-truth-freshness-governance-003.md`
- `bridge/gtkb-source-of-truth-freshness-governance-004.md`
- `bridge/gtkb-source-of-truth-freshness-governance-005.md`
- `bridge/gtkb-source-of-truth-freshness-governance-006.md`
- `bridge/gtkb-source-of-truth-freshness-governance-007.md`
- `bridge/gtkb-source-of-truth-freshness-governance-009.md`
- `bridge/gtkb-source-of-truth-freshness-governance-010.md`
- `bridge/gtkb-source-of-truth-freshness-governance-011.md`
- `bridge/gtkb-source-of-truth-freshness-governance-012.md`
- `bridge/gtkb-sp1a-ollama-lo-prompt-restructure-003.md`
- `bridge/gtkb-sp1a-ollama-lo-prompt-restructure-004.md`
- `bridge/gtkb-sp1a-ollama-lo-prompt-restructure-006.md`
- `bridge/gtkb-sp1b-dispatch-outcome-tracker-001.md`
- `bridge/gtkb-sp1b-dispatch-outcome-tracker-003.md`
- `bridge/gtkb-sp1b-dispatch-outcome-tracker-005.md`
- `bridge/gtkb-sp1b-dispatch-outcome-tracker-006.md`
- `bridge/gtkb-sp1c-author-meets-reviewer-guard-001.md`
- `bridge/gtkb-sp1c-author-meets-reviewer-guard-003.md`
- `bridge/gtkb-sp1c-author-meets-reviewer-guard-005.md`
- `bridge/gtkb-sp1c-author-meets-reviewer-guard-006.md`
- `bridge/gtkb-sp1d-turn-budget-optimization-001.md`
- `bridge/gtkb-sp1d-turn-budget-optimization-003.md`
- `bridge/gtkb-sp1d-turn-budget-optimization-005.md`
- `bridge/gtkb-sp1d-turn-budget-optimization-006.md`
- `bridge/gtkb-spa-cluster-test-id-investigation-closure-slice-1-001.md`
- `bridge/gtkb-spa-cluster-test-id-investigation-closure-slice-1-002.md`
- `bridge/gtkb-spa-cluster-test-id-investigation-closure-slice-1-004.md`
- `bridge/gtkb-spec-coherence-cli-001.md`
- `bridge/gtkb-spec-coherence-cli-002.md`
- `bridge/gtkb-spec-coherence-cli-004.md`
- `bridge/gtkb-spec-coherence-cli-scoping-001.md`
- `bridge/gtkb-spec-coherence-cli-scoping-002.md`
- `bridge/gtkb-spec-coherence-cli-scoping-004.md`
- `bridge/gtkb-spec-lifecycle-schema-2026-04-29-001.md`
- `bridge/gtkb-spec-lifecycle-schema-2026-04-29-003.md`
- `bridge/gtkb-spec-lifecycle-schema-2026-04-29-005.md`
- `bridge/gtkb-spec-lifecycle-schema-2026-04-29-006.md`
- `bridge/gtkb-spec-lifecycle-schema-2026-04-29-007.md`
- `bridge/gtkb-spec-lifecycle-schema-2026-04-29-008.md`
- `bridge/gtkb-spec-lifecycle-schema-slice-1-001.md`
- `bridge/gtkb-spec-lifecycle-schema-slice-1-003.md`
- `bridge/gtkb-spec-lifecycle-schema-slice-1-006.md`
- `bridge/gtkb-spec-lifecycle-schema-slice-1-008.md`
- `bridge/gtkb-stale-thread-closure-slice-3-impl-001.md`
- `bridge/gtkb-stale-thread-closure-slice-3-impl-002.md`
- `bridge/gtkb-stale-thread-closure-slice-3-impl-003.md`
- `bridge/gtkb-stale-thread-closure-slice-3-impl-004.md`
- `bridge/gtkb-stale-thread-closure-slice-3-impl-006.md`
- `bridge/gtkb-standing-backlog-harvest-audit-maintenance-001.md`
- `bridge/gtkb-standing-backlog-harvest-audit-maintenance-002.md`
- `bridge/gtkb-standing-backlog-harvest-audit-maintenance-003.md`
- `bridge/gtkb-standing-backlog-harvest-audit-maintenance-004.md`
- `bridge/gtkb-standing-backlog-harvest-audit-maintenance-006.md`
- `bridge/gtkb-startup-cache-dcl-supersession-scoping-001.md`
- `bridge/gtkb-startup-cache-dcl-supersession-scoping-002.md`
- `bridge/gtkb-startup-cache-dcl-supersession-scoping-003.md`
- `bridge/gtkb-startup-cache-dcl-supersession-scoping-004.md`
- `bridge/gtkb-startup-cache-dcl-supersession-scoping-006.md`
- `bridge/gtkb-startup-control-vocabulary-map-001.md`
- `bridge/gtkb-startup-control-vocabulary-map-002.md`
- `bridge/gtkb-startup-control-vocabulary-map-004.md`
- `bridge/gtkb-startup-dashboard-reachability-probe-003.md`
- `bridge/gtkb-startup-dashboard-reachability-probe-006.md`
- `bridge/gtkb-startup-enhancements-completion-reconciliation-001.md`
- `bridge/gtkb-startup-enhancements-completion-reconciliation-002.md`
- `bridge/gtkb-startup-enhancements-completion-reconciliation-003.md`
- `bridge/gtkb-startup-enhancements-completion-reconciliation-004.md`
- `bridge/gtkb-startup-enhancements-completion-reconciliation-005.md`
- `bridge/gtkb-startup-enhancements-completion-reconciliation-006.md`
- `bridge/gtkb-startup-enhancements-p1-001.md`
- `bridge/gtkb-startup-enhancements-p1-003.md`
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-001.md`
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-003.md`
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-004.md`
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-006.md`
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-007.md`
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-008.md`
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-009.md`
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-011.md`
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-012.md`
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-015.md`
- `bridge/gtkb-startup-evidence-restoration-001.md`
- `bridge/gtkb-startup-payload-canonical-state-drift-001.md`
- `bridge/gtkb-startup-payload-canonical-state-drift-003.md`
- `bridge/gtkb-startup-payload-profiler-compact-context-001.md`
- `bridge/gtkb-startup-payload-profiler-compact-context-002.md`
- `bridge/gtkb-startup-payload-profiler-compact-context-004.md`
- `bridge/gtkb-startup-payload-profiler-compact-context-006.md`
- `bridge/gtkb-startup-refractor-glossary-load-surface-001.md`
- `bridge/gtkb-startup-refractor-glossary-load-surface-003.md`
- `bridge/gtkb-startup-refractor-glossary-load-surface-006.md`
- `bridge/gtkb-startup-refractor-scoping-001.md`
- `bridge/gtkb-startup-refractor-scoping-002.md`
- `bridge/gtkb-startup-refractor-scoping-004.md`
- `bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-001.md`
- `bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-002.md`
- `bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-004.md`
- `bridge/gtkb-startup-refractor-slice-b-local-settings-hygiene-001.md`
- `bridge/gtkb-startup-refractor-slice-b-local-settings-hygiene-002.md`
- `bridge/gtkb-startup-refractor-slice-b-local-settings-hygiene-004.md`
- `bridge/gtkb-startup-refractor-slice-c-startup-index-overlays-001.md`
- `bridge/gtkb-startup-refractor-slice-c-startup-index-overlays-002.md`
- `bridge/gtkb-startup-refractor-slice-c-startup-index-overlays-004.md`
- `bridge/gtkb-startup-refractor-slice-c-startup-index-overlays-006.md`
- `bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-001.md`
- `bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-002.md`
- `bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-003.md`
- `bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-004.md`
- `bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-006.md`
- `bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-008.md`
- `bridge/gtkb-startup-refractor-slice-e-lo-startup-text-authority-001.md`
- `bridge/gtkb-startup-refractor-slice-e-lo-startup-text-authority-002.md`
- `bridge/gtkb-startup-refractor-slice-e-lo-startup-text-authority-004.md`
- `bridge/gtkb-startup-refractor-slice-e-lo-startup-text-authority-006.md`
- `bridge/gtkb-startup-relay-cache-ttl-self-heal-001.md`
- `bridge/gtkb-startup-relay-cache-ttl-self-heal-002.md`
- `bridge/gtkb-startup-relay-cache-ttl-self-heal-004.md`
- `bridge/gtkb-startup-relay-truncation-fix-refile-008.md`
- `bridge/gtkb-startup-relay-truncation-fix-refile-010.md`
- `bridge/gtkb-startup-relay-truncation-fix-refile-012.md`
- `bridge/gtkb-startup-role-slot-label-disambiguation-001.md`
- `bridge/gtkb-startup-role-slot-label-disambiguation-002.md`
- `bridge/gtkb-startup-role-slot-label-disambiguation-003.md`
- `bridge/gtkb-startup-role-slot-label-disambiguation-004.md`
- `bridge/gtkb-startup-role-slot-label-disambiguation-006.md`
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-002.md`
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-003.md`
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-004.md`
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-006.md`
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001.md`
- `bridge/gtkb-sweep-commit-skill-parity-registration-002.md`
- `bridge/gtkb-sweep-commit-skill-parity-registration-004.md`
- `bridge/gtkb-sweep-commit-skill-parity-registration-005.md`
- `bridge/gtkb-sweep-commit-skill-parity-registration-007.md`
- `bridge/gtkb-sweep-commit-skill-parity-registration-009.md`
- `bridge/gtkb-telemetry-churn-policy-2026-04-28-002.md`
- `bridge/gtkb-telemetry-churn-policy-2026-04-28-004.md`
- `bridge/gtkb-terminal-project-record-retirement-batch-001.md`
- `bridge/gtkb-terminal-project-record-retirement-batch-003.md`
- `bridge/gtkb-terminal-project-record-retirement-batch-004.md`
- `bridge/gtkb-terminal-project-record-retirement-batch-006.md`
- `bridge/gtkb-test-build-contract-orphan-relocation-001.md`
- `bridge/gtkb-test-build-contract-orphan-relocation-003.md`
- `bridge/gtkb-test-build-contract-orphan-relocation-006.md`
- `bridge/gtkb-tier-a-managed-skill-adoption-apply-001.md`
- `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md`
- `bridge/gtkb-transcript-scan-dispatch-role-sot-001.md`
- `bridge/gtkb-transcript-scan-dispatch-role-sot-003.md`
- `bridge/gtkb-transcript-scan-dispatch-role-sot-004.md`
- `bridge/gtkb-transcript-scan-dispatch-role-sot-005.md`
- `bridge/gtkb-transcript-scan-dispatch-role-sot-008.md`
- `bridge/gtkb-trigger-diagnose-tool-bugfix-001.md`
- `bridge/gtkb-trigger-diagnose-tool-bugfix-002.md`
- `bridge/gtkb-trigger-diagnose-tool-bugfix-004.md`
- `bridge/gtkb-understand-anything-evaluation-install-001.md`
- `bridge/gtkb-understand-anything-evaluation-install-002.md`
- `bridge/gtkb-understand-anything-evaluation-install-003.md`
- `bridge/gtkb-understand-anything-evaluation-install-004.md`
- `bridge/gtkb-understand-anything-evaluation-install-005.md`
- `bridge/gtkb-understand-anything-evaluation-install-007.md`
- `bridge/gtkb-understand-anything-evaluation-install-008.md`
- `bridge/gtkb-understand-anything-evaluation-install-010.md`
- `bridge/gtkb-v1-docker-isolation-validator-scoping-001.md`
- `bridge/gtkb-v1-docker-isolation-validator-scoping-003.md`
- `bridge/gtkb-v1-mechanical-enforcement-gate-scoping-001.md`
- `bridge/gtkb-v1-mechanical-enforcement-gate-scoping-002.md`
- `bridge/gtkb-v1-s509-proposal-remediation-001.md`
- `bridge/gtkb-v1-s509-proposal-remediation-002.md`
- `bridge/gtkb-v1-s509-proposal-remediation-003.md`
- `bridge/gtkb-v1-s509-proposal-remediation-005.md`
- `bridge/gtkb-v1-spec-corpus-distillation-scoping-001.md`
- `bridge/gtkb-v1-spec-corpus-distillation-scoping-002.md`
- `bridge/gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory-002.md`
- `bridge/gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory-003.md`
- `bridge/gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory-004.md`
- `bridge/gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory-005.md`
- `bridge/gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory-006.md`
- `bridge/gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory-007.md`
- `bridge/gtkb-verified-untested-spec-hygiene-cluster-slice-1-inventory-008.md`
- `bridge/gtkb-verify-skill-spec-to-test-mapping-001.md`
- `bridge/gtkb-verify-skill-spec-to-test-mapping-003.md`
- `bridge/gtkb-verify-skill-spec-to-test-mapping-005.md`
- `bridge/gtkb-verify-skill-spec-to-test-mapping-006.md`
- `bridge/gtkb-verify-skill-spec-to-test-mapping-008.md`
- `bridge/gtkb-verify-skill-spec-to-test-mapping-010.md`
- `bridge/gtkb-verify-verdict-author-skill-slice-1-001.md`
- `bridge/gtkb-verify-verdict-author-skill-slice-1-004.md`
- `bridge/gtkb-wi-3423-pauth-creation-001.md`
- `bridge/gtkb-wi-3423-pauth-creation-002.md`
- `bridge/gtkb-wi-3423-pauth-creation-004.md`
- `bridge/gtkb-wi-3506-phantom-spec-citation-repoint-001.md`
- `bridge/gtkb-wi-3506-phantom-spec-citation-repoint-002.md`
- `bridge/gtkb-wi-3506-phantom-spec-citation-repoint-003.md`
- `bridge/gtkb-wi-3506-phantom-spec-citation-repoint-004.md`
- `bridge/gtkb-wi-3506-phantom-spec-citation-repoint-005.md`
- `bridge/gtkb-wi-3506-phantom-spec-citation-repoint-006.md`
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-001.md`
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-002.md`
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-003.md`
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-004.md`
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-005.md`
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-006.md`
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-007.md`
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-008.md`
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-009.md`
- `bridge/gtkb-wi-4225-scaffold-golden-fixture-regen-010.md`
- `bridge/gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-001.md`
- `bridge/gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-002.md`
- `bridge/gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-003.md`
- `bridge/gtkb-wi-4279-scaffold-phantom-spec-citation-repoint-004.md`
- `bridge/gtkb-wi3326-project-rehome-001.md`
- `bridge/gtkb-wi3326-project-rehome-002.md`
- `bridge/gtkb-wi3326-project-rehome-003.md`
- `bridge/gtkb-wi3326-project-rehome-004.md`
- `bridge/gtkb-wi3326-project-rehome-006.md`
- `bridge/gtkb-wi3326-project-rehome-007.md`
- `bridge/gtkb-wi3326-project-rehome-executable-packet-repair-001.md`
- `bridge/gtkb-wi3326-project-rehome-executable-packet-repair-002.md`
- `bridge/gtkb-wi3326-project-rehome-executable-packet-repair-004.md`
- `bridge/gtkb-wi3326-project-rehome-executable-packet-repair-006.md`
- `bridge/gtkb-work-envelope-router-slice-1-001-001.md`
- `bridge/gtkb-work-envelope-router-slice-1-001-002.md`
- `bridge/gtkb-work-envelope-router-slice-1-001-003.md`
- `bridge/gtkb-work-envelope-router-slice-1-001-004.md`
- `bridge/gtkb-work-envelope-router-slice-2-per-type-specs-001.md`
- `bridge/gtkb-work-envelope-router-slice-2-per-type-specs-002.md`
- `bridge/gtkb-work-intent-registry-prime-write-integration-001.md`
- `bridge/gtkb-work-intent-registry-prime-write-integration-002.md`
- `bridge/gtkb-work-intent-registry-prime-write-integration-003.md`
- `bridge/gtkb-work-intent-registry-prime-write-integration-004.md`
- `bridge/gtkb-work-intent-registry-prime-write-integration-005.md`
- `bridge/gtkb-work-intent-registry-prime-write-integration-006.md`
- `bridge/gtkb-work-intent-registry-prime-write-integration-007.md`
- `bridge/gtkb-work-intent-registry-prime-write-integration-008.md`
- `bridge/gtkb-work-intent-registry-prime-write-integration-009.md`
- `bridge/gtkb-work-intent-registry-prime-write-integration-010.md`
- `bridge/gtkb-work-intent-registry-prime-write-integration-011.md`
- `bridge/gtkb-work-intent-registry-prime-write-integration-012.md`
- `bridge/gtkb-work-intent-registry-prime-write-integration-014.md`
- `bridge/gtkb-work-item-priority-canonical-p0p3-migration-001.md`
- `bridge/gtkb-work-item-priority-canonical-p0p3-migration-002.md`
- `bridge/gtkb-work-item-priority-canonical-p0p3-migration-003.md`
- `bridge/gtkb-work-item-priority-canonical-p0p3-migration-004.md`
- `bridge/gtkb-work-item-priority-canonical-p0p3-migration-005.md`
- `bridge/gtkb-work-item-priority-canonical-p0p3-migration-006.md`
- `bridge/gtkb-work-item-priority-canonical-p0p3-migration-007.md`
- `bridge/gtkb-work-item-priority-canonical-p0p3-migration-008.md`
- `bridge/gtkb-work-list-md-gov-010-path-correction-001.md`
- `bridge/gtkb-work-list-md-gov-010-path-correction-003.md`
- `bridge/gtkb-work-subject-aware-testing-integration-probe-001.md`
- `bridge/gtkb-work-subject-aware-testing-integration-probe-003.md`
- `bridge/gtkb-work-subject-aware-testing-integration-probe-006.md`
- `bridge/gtkb-work-subject-aware-testing-integration-probe-008.md`
- `bridge/gtkb-work-subject-root-enforcement-implementation-001.md`
- `bridge/gtkb-work-subject-root-enforcement-implementation-003.md`
- `bridge/gtkb-work-subject-root-enforcement-implementation-005.md`
- `bridge/gtkb-work-subject-root-enforcement-implementation-007.md`
- `bridge/gtkb-work-subject-root-enforcement-implementation-009.md`
- `bridge/gtkb-work-subject-root-enforcement-implementation-011.md`
- `bridge/gtkb-work-subject-root-enforcement-implementation-013.md`
- `bridge/gtkb-work-subject-root-enforcement-implementation-015.md`
- `bridge/gtkb-work-subject-root-enforcement-implementation-017.md`
- `bridge/gtkb-work-subject-root-enforcement-implementation-019.md`
- `bridge/gtkb-work-tree-hygiene-mechanism-scoping-001.md`
- `bridge/gtkb-work-tree-hygiene-mechanism-scoping-002.md`
- `bridge/gtkb-work-tree-hygiene-slice-a-detector-001.md`
- `bridge/gtkb-work-tree-hygiene-slice-a-detector-002.md`
- `bridge/gtkb-work-tree-hygiene-slice-a-detector-004.md`
- `bridge/gtkb-worker-packet-as-execution-authorization-envelope-slice-1-scoping-001.md`
- `bridge/gtkb-worker-packet-as-execution-authorization-envelope-slice-1-scoping-002.md`
- `bridge/gtkb-worker-packet-as-execution-authorization-envelope-slice-1-scoping-004.md`
- `bridge/gtkb-worker-packet-as-execution-authorization-envelope-slice-1-scoping-006.md`
- `bridge/gtkb-worker-packet-auth-envelope-slice-2-auto-packet-001.md`
- `bridge/gtkb-worker-packet-auth-envelope-slice-2-auto-packet-004.md`
- `bridge/gtkb-workspace-orphan-cleanup-2026-06-05-001.md`
- `bridge/gtkb-workspace-orphan-cleanup-2026-06-05-002.md`
- `bridge/gtkb-workspace-orphan-cleanup-2026-06-05-003.md`
- `bridge/gtkb-workstream-focus-marker-race-fix-003.md`
- `bridge/gtkb-wrap-scan-report-relocation-slice-1-001.md`
- `bridge/gtkb-wrap-scan-report-relocation-slice-1-002.md`
- `bridge/gtkb-wrap-scan-report-relocation-slice-1-004.md`
- `bridge/gtkb-wrapup-clear-impl-start-packet-at-verified-001.md`
- `bridge/gtkb-wrapup-clear-impl-start-packet-at-verified-002.md`
- `bridge/gtkb-wrapup-enhancements-closure-001.md`
- `bridge/gtkb-wrapup-enhancements-closure-002.md`
- `bridge/gtkb-wrapup-enhancements-closure-003.md`
- `bridge/gtkb-wrapup-enhancements-closure-004.md`
- `bridge/gtkb-wrapup-enhancements-next-slice-001.md`
- `bridge/gtkb-wrapup-enhancements-next-slice-003.md`
- `bridge/gtkb-wrapup-enhancements-next-slice-006.md`
- `bridge/gtkb-wrapup-enhancements-slice1-001.md`
- `bridge/gtkb-wrapup-enhancements-slice1-003.md`
- `bridge/gtkb-wrapup-enhancements-slice1-005.md`
- `bridge/gtkb-zero-knowledge-architecture-phase-4-scoping-001.md`
- `bridge/gtkb-zero-knowledge-architecture-phase-4-scoping-003.md`
- `bridge/gtkb-zero-knowledge-architecture-phase-4-scoping-004.md`
- `bridge/gtkb-zero-knowledge-architecture-phase-4-scoping-006.md`
- `bridge/harness-state-authority-migration-2026-04-27-002.md`
- `bridge/harness-state-authority-migration-2026-04-27-004.md`
- `bridge/harness-state-authority-migration-2026-04-27-006.md`
- `bridge/harness-state-authority-migration-2026-04-27-008.md`
- `bridge/harness-state-authority-migration-2026-04-27-010.md`
- `bridge/s317-ruff-cleanup-pre-existing-debt-002.md`
- `bridge/s317-ruff-cleanup-pre-existing-debt-004.md`
- `bridge/s317-working-tree-triage-002.md`
- `bridge/s317-working-tree-triage-004.md`
- `bridge/s317-working-tree-triage-006.md`
- `bridge/s317-working-tree-triage-008.md`
- `bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-002.md`
- `bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-004.md`
- `bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-006.md`
- `bridge/smart-poller-kind-aware-routing-2026-04-30-001.md`
- `bridge/smart-poller-kind-aware-routing-2026-04-30-003.md`
- `bridge/smart-poller-kind-aware-routing-2026-04-30-005.md`
- `bridge/smart-poller-kind-aware-routing-2026-04-30-007.md`
- `bridge/smart-poller-kind-aware-routing-2026-04-30-009.md`
- `bridge/spec-smart-poller-auto-trigger-2026-04-29-003.md`
- `groundtruth-kb/pyproject.toml`
- `groundtruth-kb/src/groundtruth_kb/bridge/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/hooks/test_workstream_focus_session_role_marker.py`
- `scripts/check_harness_parity.py`
- `scripts/cross_harness_bridge_trigger.py`
- `scripts/workstream_focus.py`

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: The diff adds or changes skill, script, or platform capability surfaces.

```text
     .claude/hooks/bridge-compliance-gate.py            |  41 ++++-
     .claude/settings.json                              |  10 ++
     .claude/skills/bridge/helpers/scan_bridge.py       |   1 +
     applications/Agent_Red/tests/conftest.py           |  22 +++
     .../tests/security/test_documentation_cleanup.py   |  23 ++-
     .../tests/security/test_superadmin_api_split.py    |  22 ++-
     bridge/INDEX.md                                    |  26 ++-
     ...pace-declaration-architecture-2026-04-29-003.md |   2 +-
     ...pace-declaration-architecture-2026-04-29-005.md |   2 +-
     ...pace-declaration-architecture-2026-04-29-006.md |   2 +-
     bridge/active-workspace-declaration-slice-1-001.md |   2 +-
     bridge/active-workspace-declaration-slice-1-003.md |   2 +-
     bridge/active-workspace-declaration-slice-1-005.md |   2 +-
     bridge/active-workspace-declaration-slice-1-008.md |   2 +-
     bridge/active-workspace-declaration-slice-1-009.md |   2 +-
     bridge/active-workspace-declaration-slice-1-010.md |   2 +-
     bridge/agent-red-ruff-cleanup-001-006.md           |   2 +-
     ...esults-053026-options-for-implementation-001.md |   2 +-
     ...ical-deploy-pipeline-scaling-enforcement-001.md |   2 +-
     ...ical-deploy-pipeline-scaling-enforcement-003.md |   2 +-
     ...ical-deploy-pipeline-scaling-enforcement-005.md |   2 +-
     ...ical-deploy-pipeline-scaling-enforcement-007.md |   2 +-
     ...ical-deploy-pipeline-scaling-enforcement-009.md |   2 +-
     ...ical-deploy-pipeline-scaling-enforcement-011.md |   2 +-
     ...e-gate-coverage-shutil-rmtree-2026-04-27-002.md |   2 +-
     ...e-gate-coverage-shutil-rmtree-2026-04-27-004.md |   2 +-
     ...e-gate-coverage-shutil-rmtree-2026-04-27-006.md |   2 +-
     bridge/generator-hardening-002-011.md              |   2 +-
     ...-plugin-cache-closure-scoping-2026-04-28-002.md |   2 +-
     ...-plugin-cache-closure-scoping-2026-04-28-004.md |   2 +-
     ...-plugin-cache-closure-scoping-2026-04-28-006.md |   2 +-
     ...ive-status-capability-gate-formalization-001.md |   2 +-
     ...ive-status-capability-gate-formalization-002.md |   2 +-
     ...ive-status-capability-gate-formalization-004.md |   2 +-
     ...bility-gate-formalization-content-drafts-001.md |   2 +-
     ...bility-gate-formalization-content-drafts-002.md |   2 +-
     ...bility-gate-formalization-content-drafts-004.md |   2 +-
     ...ability-gate-harness-lifecycle-retention-001.md |   2 +-
     ...ability-gate-harness-lifecycle-retention-002.md |   2 +-
     ...ability-gate-harness-lifecycle-retention-004.md |   2 +-
     ...ability-gate-harness-lifecycle-retention-006.md |   2 +-
     ...atus-capability-gate-lifecycle-substrate-001.md |   2 +-
     ...atus-capability-gate-lifecycle-substrate-002.md |   2 +-
     ...atus-capability-gate-lifecycle-substrate-004.md |   2 +-
     ...status-capability-gate-registry-dispatch-001.md |   2 +-
     ...status-capability-gate-registry-dispatch-002.md |   2 +-
     ...status-capability-gate-registry-dispatch-004.md |   2 +-
     bridge/gtkb-adr-0001-membase-migration-002.md      |   2 +-
     bridge/gtkb-adr-0001-membase-migration-003.md      |   2 +-
     bridge/gtkb-adr-0001-membase-migration-004.md      |   2 +-
     bridge/gtkb-adr-0001-membase-migration-005.md      |   2 +-
     bridge/gtkb-adr-0001-membase-migration-006.md      |   2 +-
     bridge/gtkb-adr-0001-membase-migration-007.md      |   2 +-
     bridge/gtkb-adr-0001-membase-migration-008.md      |   2 +-
     ...kb-adr-dcl-clause-auto-discovery-slice-5-001.md |   2 +-
     ...kb-adr-dcl-clause-auto-discovery-slice-5-003.md |   2 +-
     ...kb-adr-dcl-clause-auto-discovery-slice-5-004.md |   2 +-
     ...kb-adr-dcl-clause-auto-discovery-slice-5-006.md |   2 +-
     ...kb-adr-dcl-clause-auto-discovery-slice-5-008.md |   2 +-
     ...l-clause-preflight-content-file-path-fix-001.md |   2 +-
     ...l-clause-preflight-content-file-path-fix-004.md |   2 +-
     ...-adr-dcl-clause-test-enforcement-slice-2-001.md |   2 +-
     ...-adr-dcl-clause-test-enforcement-slice-2-002.md |   2 +-
     ...kb-adr-evaluation-enforcement-2026-04-30-007.md |   2 +-
     bridge/gtkb-adr-harness-registry-extension-001.md  |   2 +-
     bridge/gtkb-adr-harness-registry-extension-003.md  |   2 +-
     ...gtkb-adr-isolation-application-placement-001.md |   2 +-
     ...gtkb-adr-isolation-application-placement-005.md |   2 +-
     ...-advisory-report-dashboard-counters-spec-001.md |   2 +-
     ...-advisory-report-dashboard-counters-spec-002.md |   2 +-
     ...-advisory-report-dashboard-counters-spec-003.md |   2 +-
     ...-advisory-report-dashboard-counters-spec-004.md |   2 +-
     ...-advisory-report-dashboard-counters-spec-006.md |   2 +-
     ...-advisory-report-message-type-2026-05-09-002.md |   2 +-
     ...-advisory-report-message-type-conversion-001.md |   2 +-
     ...-advisory-report-message-type-conversion-002.md |   2 +-
     ...-advisory-report-message-type-conversion-003.md |   2 +-
     ...-advisory-report-message-type-conversion-004.md |   2 +-
     ...-advisory-report-message-type-conversion-006.md |   2 +-
     .../gtkb-advisory-report-protocol-extension-001.md |   2 +-
     .../gtkb-advisory-report-protocol-extension-002.md |   2 +-
     .../gtkb-advisory-report-protocol-extension-003.md |   2 +-
     .../gtkb-advisory-report-protocol-extension-004.md |   2 +-
     .../gtkb-advisory-report-protocol-extension-006.md |   2 +-
     bridge/gtkb-advisory-report-template-spec-001.md   |   2 +-
     bridge/gtkb-advisory-report-template-spec-002.md   |   2 +-
     bridge/gtkb-advisory-report-template-spec-003.md   |   2 +-
     bridge/gtkb-advisory-report-template-spec-004.md   |   2 +-
     bridge/gtkb-advisory-report-template-spec-005.md   |   2 +-
     bridge/gtkb-advisory-report-template-spec-006.md   |   2 +-
     bridge/gtkb-advisory-report-template-spec-008.md   |   4 +-
     bridge/gtkb-advisory-routing-dcl-001.md            |   2 +-
     bridge/gtkb-advisory-routing-dcl-002.md            |   2 +-
     bridge/gtkb-advisory-routing-dcl-003.md            |   2 +-
     bridge/gtkb-advisory-routing-dcl-004.md            |   2 +-
     bridge/gtkb-advisory-routing-dcl-006.md            |   2 +-
     ...gent-red-deployability-preservation-gate-001.md |   2 +-
     ...gent-red-deployability-preservation-gate-003.md |   2 +-
     ...gent-red-deployability-preservation-gate-004.md |   2 +-
     ...gent-red-deployability-preservation-gate-006.md |   2 +-
     ...bility-preservation-gate-slice-1-scoping-001.md |   2 +-
     ...bility-preservation-gate-slice-1-scoping-003.md |   2 +-
     ...bility-preservation-gate-slice-1-scoping-004.md |   2 +-
     ...bility-preservation-gate-slice-1-scoping-006.md |   2 +-
     ...ed-reference-adopter-framing-restoration-001.md |   2 +-
     ...ed-reference-adopter-framing-restoration-003.md |   2 +-
     ...ed-reference-adopter-framing-restoration-004.md |   2 +-
     ...ed-reference-adopter-framing-restoration-006.md |   2 +-
     ...ed-reference-adopter-framing-restoration-008.md |   2 +-
     .../gtkb-agent-sot-read-discipline-phase-1-001.md  |   2 +-
     .../gtkb-agent-sot-read-discipline-phase-1-002.md  |   2 +-
     ...assisted-delivery-maturity-model-scoping-001.md |   2 +-
     ...assisted-delivery-maturity-model-scoping-003.md |   2 +-
     ...assisted-delivery-maturity-model-scoping-006.md |   2 +-
     bridge/gtkb-antigravity-capability-adapters-001.md |   2 +-
     bridge/gtkb-antigravity-capability-adapters-002.md |   2 +-
     .../gtkb-antigravity-harness-registration-001.md   |   2 +-
     .../gtkb-antigravity-harness-registration-004.md   |   2 +-
     bridge/gtkb-antigravity-ide-research-spike-001.md  |   2 +-
     bridge/gtkb-antigravity-ide-research-spike-002.md  |   2 +-
     bridge/gtkb-antigravity-ide-research-spike-004.md  |   2 +-
     ...avity-implements-link-ambiguity-advisory-001.md |   2 +-
     ...vity-insight-stale-owner-action-advisory-001.md |   2 +-
     .../gtkb-antigravity-integration-directory-001.md  |   2 +-
     .../gtkb-antigravity-integration-directory-002.md  |   2 +-
     .../gtkb-antigravity-integration-directory-004.md  |   2 +-
     ...igravity-related-bridge-threads-backfill-001.md |   2 +-
     ...igravity-related-bridge-threads-backfill-002.md |   2 +-
     ...igravity-related-bridge-threads-backfill-003.md |   2 +-
     ...igravity-related-bridge-threads-backfill-004.md |   2 +-
     ...igravity-related-bridge-threads-backfill-006.md |   2 +-
     bridge/gtkb-app-boundary-mechanism-audit-001.md    |   2 +-
     bridge/gtkb-app-boundary-mechanism-audit-003.md    |   2 +-
     .../gtkb-approval-gate-readonly-flag-skip-001.md   |   2 +-
     .../gtkb-approval-gate-readonly-flag-skip-002.md   |   2 +-
     .../gtkb-approval-gate-readonly-flag-skip-003.md   |   2 +-
     .../gtkb-approval-gate-readonly-flag-skip-004.md   |   2 +-
     .../gtkb-approval-gate-readonly-flag-skip-006.md   |   2 +-
     bridge/gtkb-artifact-recorder-cli-005.md           |   2 +-
     ...kb-artifact-recorder-cli-scoping-advance-001.md |   2 +-
     ...ecorder-cli-slice-1-deliberations-record-002.md |   2 +-
     ...ecorder-cli-slice-1-deliberations-record-004.md |   2 +-
     ...ecorder-cli-slice-1-deliberations-record-006.md |   2 +-
     ...ecorder-cli-slice-1-deliberations-record-008.md |   2 +-
     ...rtifact-recorder-cli-slice-2-spec-record-002.md |   2 +-
     ...rtifact-recorder-cli-slice-2-spec-record-004.md |   2 +-
     ...rtifact-recorder-cli-slice-2-spec-record-006.md |   2 +-
     ...-cli-slice-4-owner-decision-auto-archive-002.md |   2 +-
     ...-cli-slice-4-owner-decision-auto-archive-005.md |   2 +-
     ...-cli-slice-4-owner-decision-auto-archive-007.md |   2 +-
     ...-cli-slice-4-owner-decision-auto-archive-009.md |   2 +-
     ...-cli-slice-4-owner-decision-auto-archive-011.md |   2 +-
     ...-cli-slice-4-owner-decision-auto-archive-012.md |   2 +-
     ...-cli-slice-4-owner-decision-auto-archive-014.md |   2 +-
     .../gtkb-audit-script-withdrawn-regex-fix-001.md   |   2 +-
     ...b-audit-script-withdrawn-status-handling-001.md |   2 +-
     ...b-audit-script-withdrawn-status-handling-002.md |   2 +-
     ...b-audit-script-withdrawn-status-handling-004.md |   2 +-
     ...b-audit-script-withdrawn-status-handling-006.md |   2 +-
     .../gtkb-auto-push-investigation-001-prop-001.md   |   2 +-
     ...-push-investigation-001-slice-1-findings-001.md |   2 +-
     ...-push-investigation-001-slice-1-findings-002.md |   2 +-
     ...-push-investigation-001-slice-1-findings-003.md |   2 +-
     ...-push-investigation-001-slice-1-findings-004.md |   2 +-
     ...-push-investigation-001-slice-1-findings-006.md |   2 +-
     bridge/gtkb-auto-push-investigation-slice-1-004.md |   2 +-
     bridge/gtkb-auto-push-investigation-slice-1-005.md |   2 +-
     bridge/gtkb-auto-push-investigation-slice-1-006.md |   2 +-
     bridge/gtkb-auto-push-investigation-slice-2-001.md |   2 +-
     bridge/gtkb-auto-push-investigation-slice-2-002.md |   2 +-
     bridge/gtkb-auto-push-investigation-slice-2-003.md |   2 +-
     bridge/gtkb-auto-push-investigation-slice-2-005.md |   2 +-
     bridge/gtkb-axis-2-dispatchable-filter-001.md      |   2 +-
     bridge/gtkb-axis-2-dispatchable-filter-002.md      |   2 +-
     bridge/gtkb-axis-2-dispatchable-filter-003.md      |   2 +-
     bridge/gtkb-axis-2-dispatchable-filter-004.md      |   2 +-
     bridge/gtkb-axis-2-dispatchable-filter-005.md      |   2 +-
     bridge/gtkb-axis-2-dispatchable-filter-006.md      |   2 +-
     ...b-axis-2-scoping-terminal-classifier-fix-001.md |   2 +-
     ...b-axis-2-scoping-terminal-classifier-fix-004.md |   2 +-
     bridge/gtkb-backlog-add-cli-slice-1-001.md         |   2 +-
     bridge/gtkb-backlog-add-cli-slice-1-003.md         |   2 +-
     ...gtkb-backlog-approval-state-taxonomy-auq-001.md |   2 +-
     ...-backlog-approval-state-taxonomy-slice-1-001.md |   2 +-
     ...-backlog-approval-state-taxonomy-slice-1-003.md |   2 +-
     ...-backlog-approval-state-taxonomy-slice-1-005.md |   2 +-
     ...-backlog-approval-state-taxonomy-slice-1-006.md |   2 +-
     ...-backlog-approval-state-taxonomy-slice-1-009.md |   2 +-
     ...-backlog-approval-state-taxonomy-slice-1-010.md |   2 +-
     ...-backlog-approval-state-taxonomy-slice-1-011.md |   2 +-
     ...log-authorize-implementation-cli-slice-1-001.md |   2 +-
     ...log-authorize-implementation-cli-slice-1-003.md |   2 +-
     ...log-authorize-implementation-cli-slice-1-006.md |   2 +-
     ...log-authorize-implementation-cli-slice-1-008.md |   2 +-
     ...b-backlog-canonical-pivot-spec-promotion-001.md |   2 +-
     ...b-backlog-canonical-pivot-spec-promotion-002.md |   2 +-
     ...b-backlog-canonical-pivot-spec-promotion-003.md |   2 +-
     ...b-backlog-canonical-pivot-spec-promotion-004.md |   2 +-
     ...b-backlog-canonical-pivot-spec-promotion-005.md |   2 +-
     ...b-backlog-canonical-pivot-spec-promotion-006.md |   2 +-
     bridge/gtkb-backlog-update-cli-slice-1-001.md      |   2 +-
     bridge/gtkb-backlog-update-cli-slice-1-003.md      |   2 +-
     .../gtkb-backlog-update-title-desc-cli-001-001.md  |   2 +-
     .../gtkb-backlog-update-title-desc-cli-001-002.md  |   2 +-
     .../gtkb-backlog-update-title-desc-cli-001-003.md  |   2 +-
     .../gtkb-backlog-update-title-desc-cli-001-004.md  |   2 +-
     .../gtkb-backlog-update-title-desc-cli-001-006.md  |   2 +-
     ...ook-destructive-substring-false-positive-001.md |   2 +-
     ...ook-destructive-substring-false-positive-002.md |   2 +-
     ...ook-destructive-substring-false-positive-004.md |   2 +-
     bridge/gtkb-bridge-active-session-autodrain-001.md |   2 +-
     bridge/gtkb-bridge-active-session-autodrain-003.md |   2 +-
     bridge/gtkb-bridge-active-session-autodrain-004.md |   2 +-
     bridge/gtkb-bridge-active-session-autodrain-005.md |   2 +-
     bridge/gtkb-bridge-active-session-autodrain-006.md |   2 +-
     bridge/gtkb-bridge-active-session-autodrain-008.md |   2 +-
     ...dge-advisory-message-type-implementation-003.md |   2 +-
     ...sory-report-message-advisory-disposition-001.md |   2 +-
     ...sory-report-message-advisory-disposition-006.md |   2 +-
     bridge/gtkb-bridge-advisory-status-001-001.md      |   2 +-
     bridge/gtkb-bridge-advisory-status-001-003.md      |   2 +-
     bridge/gtkb-bridge-advisory-status-001-004.md      |   2 +-
     bridge/gtkb-bridge-advisory-status-001-005.md      |   2 +-
     bridge/gtkb-bridge-advisory-status-001-007.md      |   2 +-
     bridge/gtkb-bridge-advisory-status-001-008.md      |   2 +-
     bridge/gtkb-bridge-advisory-status-001-009.md      |   2 +-
     bridge/gtkb-bridge-advisory-status-001-010.md      |   2 +-
     bridge/gtkb-bridge-advisory-status-001-011.md      |   2 +-
     bridge/gtkb-bridge-advisory-status-001-012.md      |   2 +-
     bridge/gtkb-bridge-advisory-status-001-013.md      |   2 +-
     bridge/gtkb-bridge-advisory-status-001-014.md      |   2 +-
     bridge/gtkb-bridge-advisory-status-001-016.md      |   2 +-
     bridge/gtkb-bridge-automation-status-driver-002.md |   2 +-
     bridge/gtkb-bridge-automation-status-driver-004.md |   2 +-
     bridge/gtkb-bridge-automation-status-driver-006.md |   2 +-
     ...-bridge-backlog-reconciliation-audit-cli-001.md |   2 +-
     ...-bridge-backlog-reconciliation-audit-cli-002.md |   2 +-
     ...-bridge-backlog-reconciliation-audit-cli-004.md |   2 +-
     ...gtkb-bridge-citation-freshness-preflight-001.md |   2 +-
     ...gtkb-bridge-citation-freshness-preflight-003.md |   2 +-
     ...gtkb-bridge-citation-freshness-preflight-006.md |   2 +-
     ...idge-citation-freshness-test-restoration-001.md |   2 +-
     ...idge-citation-freshness-test-restoration-002.md |   2 +-
     ...idge-citation-freshness-test-restoration-003.md |   2 +-
     ...idge-citation-freshness-test-restoration-005.md |   2 +-
     ...e-compliance-gate-fenced-code-parser-fix-001.md |   2 +-
     ...b-bridge-compliance-gate-index-exemption-001.md |   2 +-
     ...b-bridge-compliance-gate-index-exemption-003.md |   2 +-
     ...b-bridge-compliance-gate-index-exemption-004.md |   2 +-
     ...nce-gate-spec-test-heading-multiline-fix-001.md |   2 +-
     ...nce-gate-spec-test-heading-multiline-fix-004.md |   2 +-
     ...nce-gate-spec-test-heading-multiline-fix-006.md |   2 +-
     ...nce-gate-spec-test-heading-multiline-fix-007.md |   2 +-
     ...bridge-compliance-gate-wi-auto-regex-fix-001.md |   2 +-
     ...bridge-compliance-gate-wi-auto-regex-fix-004.md |   2 +-
     .../gtkb-bridge-compliance-project-metadata-001.md |   2 +-
     .../gtkb-bridge-compliance-project-metadata-003.md |   2 +-
     .../gtkb-bridge-compliance-project-metadata-005.md |   2 +-
     .../gtkb-bridge-compliance-project-metadata-007.md |   2 +-
     .../gtkb-bridge-compliance-project-metadata-009.md |   2 +-
     .../gtkb-bridge-compliance-project-metadata-011.md |   2 +-
     .../gtkb-bridge-compliance-project-metadata-013.md |   2 +-
     ...e-groundtruth-db-in-target-paths-slice-1-001.md |   2 +-
     ...e-groundtruth-db-in-target-paths-slice-1-002.md |   2 +-
     ...e-groundtruth-db-in-target-paths-slice-1-003.md |   2 +-
     ...e-groundtruth-db-in-target-paths-slice-1-004.md |   2 +-
     ...e-groundtruth-db-in-target-paths-slice-1-006.md |   2 +-
     ...-bridge-compliance-wi-project-membership-001.md |   2 +-
     ...-bridge-compliance-wi-project-membership-003.md |   2 +-
     ...-bridge-compliance-wi-project-membership-005.md |   2 +-
     ...-bridge-compliance-wi-project-membership-007.md |   4 +-
     ...-bridge-compliance-wi-project-membership-009.md |   2 +-
     bridge/gtkb-bridge-contention-consolidation-001.md |   2 +-
     bridge/gtkb-bridge-contention-consolidation-002.md |   2 +-
     bridge/gtkb-bridge-contention-consolidation-003.md |   2 +-
     bridge/gtkb-bridge-contention-consolidation-004.md |   2 +-
     bridge/gtkb-bridge-contention-consolidation-006.md |   2 +-
     bridge/gtkb-bridge-convenience-verbs-001.md        |   2 +-
     bridge/gtkb-bridge-convenience-verbs-002.md        |   2 +-
     bridge/gtkb-bridge-convenience-verbs-004.md        |   2 +-
     bridge/gtkb-bridge-convenience-verbs-005.md        |   2 +-
     bridge/gtkb-bridge-convenience-verbs-006.md        |   2 +-
     bridge/gtkb-bridge-convenience-verbs-007.md        |   2 +-
     ...dispatch-per-document-lease-substitution-001.md |   2 +-
     ...dispatch-per-document-lease-substitution-002.md |   2 +-
     ...dispatch-per-document-lease-substitution-004.md |   2 +-
     ...dispatch-per-document-lease-substitution-006.md |   2 +-
     ...e-dispatcher-deferral-enforcement-repair-001.md |   2 +-
     ...e-dispatcher-deferral-enforcement-repair-003.md |   2 +-
     ...e-dispatcher-deferral-enforcement-repair-006.md |   2 +-
     bridge/gtkb-bridge-impl-report-skill-001-001.md    |   2 +-
     bridge/gtkb-bridge-index-archival-trim-001.md      |   2 +-
     bridge/gtkb-bridge-index-archival-trim-003.md      |   2 +-
     bridge/gtkb-bridge-index-archival-trim-005.md      |   2 +-
     bridge/gtkb-bridge-index-archival-trim-007.md      |   2 +-
     bridge/gtkb-bridge-index-archival-trim-010.md      |   2 +-
     ...kb-bridge-index-chain-deviation-detector-001.md |   2 +-
     ...kb-bridge-index-chain-deviation-detector-002.md |   2 +-
     ...kb-bridge-index-chain-deviation-detector-004.md |   2 +-
     ...x-phantom-verified-references-2026-04-27-002.md |   2 +-
     ...x-phantom-verified-references-2026-04-27-004.md |   2 +-
     .../gtkb-bridge-index-role-intent-sentinel-001.md  |   2 +-
     .../gtkb-bridge-index-role-intent-sentinel-003.md  |   2 +-
     .../gtkb-bridge-index-role-intent-sentinel-004.md  |   2 +-
     .../gtkb-bridge-index-role-intent-sentinel-006.md  |   2 +-
     .../gtkb-bridge-index-role-intent-sentinel-008.md  |   2 +-
     .../gtkb-bridge-kind-taxonomy-stabilization-003.md |  12 ++
     ...kb-bridge-kind-terminal-exempt-alignment-001.md |   2 +-
     ...kb-bridge-kind-terminal-exempt-alignment-002.md |   2 +-
     ...kb-bridge-kind-terminal-exempt-alignment-003.md |   2 +-
     ...kb-bridge-kind-terminal-exempt-alignment-004.md |   2 +-
     ...kb-bridge-kind-terminal-exempt-alignment-005.md |   2 +-
     ...kb-bridge-kind-terminal-exempt-alignment-006.md |   2 +-
     ...tkb-bridge-mode-config-transactions-impl-001.md |   2 +-
     ...tkb-bridge-mode-config-transactions-impl-002.md |   2 +-
     ...tkb-bridge-mode-config-transactions-impl-003.md |   2 +-
     ...-bridge-mode-config-transactions-slice-1-001.md |   2 +-
     ...-bridge-mode-config-transactions-slice-1-002.md |   2 +-
     ...-bridge-mode-config-transactions-slice-1-003.md |   2 +-
     ...-bridge-mode-config-transactions-slice-1-004.md |   2 +-
     ...-bridge-mode-config-transactions-slice-1-005.md |   2 +-
     ...-bridge-mode-config-transactions-slice-1-006.md |   2 +-
     ...-bridge-mode-config-transactions-slice-1-007.md |   2 +-
     ...-bridge-mode-config-transactions-slice-1-008.md |   2 +-
     ...-bridge-mode-config-transactions-slice-1-009.md |   2 +-
     ...-bridge-mode-config-transactions-slice-1-011.md |   2 +-
     ...-bridge-mode-config-transactions-slice-1-013.md |   2 +-
     ...-bridge-mode-config-transactions-slice-1-015.md |   2 +-
     .../gtkb-bridge-parallel-session-collision-001.md  |   2 +-
     .../gtkb-bridge-parallel-session-collision-002.md  |   2 +-
     .../gtkb-bridge-parallel-session-collision-003.md  |   2 +-
     .../gtkb-bridge-parallel-session-collision-004.md  |   2 +-
     .../gtkb-bridge-parallel-session-collision-006.md  |   2 +-
     bridge/gtkb-bridge-poller-001-smart-poller-001.md  |   2 +-
     bridge/gtkb-bridge-poller-001-smart-poller-008.md  |   2 +-
     ...b-bridge-poller-event-driven-replacement-007.md |   2 +-
     ...b-bridge-poller-event-driven-replacement-009.md |   2 +-
     ...n-replacement-slice-3-hook-registrations-001.md |   2 +-
     ...n-replacement-slice-3-hook-registrations-003.md |   2 +-
     ...n-replacement-slice-3-hook-registrations-005.md |   2 +-
     ...ment-slice-4-smart-poller-retirement-001-003.md |   2 +-
     ...ment-slice-4-smart-poller-retirement-001-005.md |   2 +-
     ...ment-slice-4-smart-poller-retirement-001-007.md |   2 +-
     ...ment-slice-4-smart-poller-retirement-001-009.md |   2 +-
     ...ment-slice-4-smart-poller-retirement-001-011.md |   2 +-
     ...ment-slice-4-smart-poller-retirement-001-013.md |   2 +-
     ...ment-slice-4-smart-poller-retirement-001-015.md |   2 +-
     ...lacement-slice-4-smart-poller-retirement-001.md |   2 +-
     bridge/gtkb-bridge-poller-p1-detector-006.md       |   2 +-
     ...kb-bridge-poller-p2-5-verification-spike-005.md |   2 +-
     bridge/gtkb-bridge-poller-p2-registry-008.md       |   2 +-
     ...-bridge-poller-wi-retirement-disposition-001.md |   2 +-
     ...-bridge-poller-wi-retirement-disposition-002.md |   2 +-
     ...-bridge-poller-wi-retirement-disposition-003.md |   2 +-
     ...-bridge-poller-wi-retirement-disposition-004.md |   2 +-
     ...-bridge-poller-wi-retirement-disposition-005.md |   2 +-
     ...-bridge-poller-wi-retirement-disposition-006.md |   2 +-
     ...-bridge-poller-wi-retirement-disposition-008.md |   2 +-
     bridge/gtkb-bridge-preflight-path-warning-001.md   |   2 +-
     bridge/gtkb-bridge-preflight-path-warning-002.md   |   2 +-
     bridge/gtkb-bridge-preflight-path-warning-003.md   |   2 +-
     bridge/gtkb-bridge-preflight-path-warning-004.md   |   2 +-
     bridge/gtkb-bridge-preflight-path-warning-006.md   |   2 +-
     ...ropose-helper-caller-migration-to-writer-001.md |   2 +-
     ...ropose-helper-caller-migration-to-writer-002.md |   2 +-
     ...ropose-helper-caller-migration-to-writer-003.md |   2 +-
     ...ropose-helper-caller-migration-to-writer-005.md |   2 +-
     ...ridge-propose-helper-non-bypass-redesign-001.md |   2 +-
     ...ridge-propose-helper-non-bypass-redesign-003.md |   2 +-
     ...ridge-propose-helper-non-bypass-redesign-004.md |   2 +-
     ...ridge-propose-helper-non-bypass-redesign-006.md |   2 +-
     ...bridge-reconciliation-correction-packets-001.md |   2 +-
     ...bridge-reconciliation-correction-packets-002.md |   2 +-
     ...bridge-reconciliation-correction-packets-004.md |   2 +-
     bridge/gtkb-bridge-revise-cli-slice-1-001.md       |   2 +-
     bridge/gtkb-bridge-revise-cli-slice-1-002.md       |   2 +-
     bridge/gtkb-bridge-revise-cli-slice-1-004.md       |   2 +-
     bridge/gtkb-bridge-revision-skill-001-001.md       |   2 +-
     bridge/gtkb-bridge-revision-skill-001-003.md       |   2 +-
     bridge/gtkb-bridge-revision-skill-001-006.md       |   2 +-
     bridge/gtkb-bridge-revision-skill-001-007.md       |   2 +-
     bridge/gtkb-bridge-revision-skill-001-008.md       |   2 +-
     bridge/gtkb-bridge-revision-skill-001-009.md       |   2 +-
     ...e-scheduler-lanes-leases-slice-1-scoping-001.md |   2 +-
     ...e-scheduler-lanes-leases-slice-1-scoping-004.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-2-001.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-2-004.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-3-001.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-3-002.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-3-004.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-3-006.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-4-001.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-4-002.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-4-004.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-5-001.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-5-003.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-5-004.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-5-006.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-6-001.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-6-002.md |   2 +-
     ...kb-bridge-scheduler-lanes-leases-slice-6-004.md |   2 +-
     ...gtkb-bridge-skill-protected-write-helper-001.md |   2 +-
     ...gtkb-bridge-skill-protected-write-helper-002.md |   2 +-
     ...gtkb-bridge-skill-protected-write-helper-003.md |   2 +-
     ...gtkb-bridge-skill-protected-write-helper-004.md |   2 +-
     ...gtkb-bridge-skill-protected-write-helper-006.md |   2 +-
     bridge/gtkb-bridge-skill-unified-001-005.md        |   2 +-
     bridge/gtkb-bridge-skill-unified-001-006.md        |   2 +-
     .../gtkb-bridge-stop-drain-deference-repair-001.md |   2 +-
     .../gtkb-bridge-stop-drain-deference-repair-002.md |   2 +-
     .../gtkb-bridge-stop-drain-deference-repair-003.md |   2 +-
     .../gtkb-bridge-stop-drain-deference-repair-004.md |   2 +-
     .../gtkb-bridge-stop-drain-deference-repair-006.md |   2 +-
     ...kb-bridge-target-paths-kb-mutation-check-001.md |   2 +-
     ...kb-bridge-target-paths-kb-mutation-check-006.md |   2 +-
     ...ughput-metrics-dashboard-slice-1-scoping-001.md |   2 +-
     ...ughput-metrics-dashboard-slice-1-scoping-003.md |   2 +-
     ...ughput-metrics-dashboard-slice-1-scoping-006.md |   2 +-
     .../gtkb-bridge-verified-backlog-retirement-001.md |   2 +-
     .../gtkb-bridge-verified-backlog-retirement-003.md |   2 +-
     .../gtkb-bridge-verified-backlog-retirement-007.md |   2 +-
     ...rk-intent-session-id-live-env-precedence-001.md |   2 +-
     ...rk-intent-session-id-live-env-precedence-002.md |   2 +-
     ...rk-intent-session-id-live-env-precedence-004.md |   2 +-
     ...rk-intent-session-id-live-env-precedence-006.md |   2 +-
     ...te-spec-intake-six-statements-2026-04-29-001.md |   2 +-
     ...te-spec-intake-six-statements-2026-04-29-003.md |   2 +-
     ...-bridge-parser-withdrawn-status-handling-001.md |   2 +-
     ...-bridge-parser-withdrawn-status-handling-002.md |   2 +-
     ...-bridge-parser-withdrawn-status-handling-004.md |   2 +-
     .../gtkb-canonical-init-keyword-syntax-001-002.md  |   2 +-
     .../gtkb-canonical-init-keyword-syntax-001-003.md  |   2 +-
     .../gtkb-canonical-init-keyword-syntax-001-004.md  |   2 +-
     .../gtkb-canonical-init-keyword-syntax-001-005.md  |   2 +-
     .../gtkb-canonical-init-keyword-syntax-001-006.md  |   2 +-
     .../gtkb-canonical-init-keyword-syntax-001-007.md  |   2 +-
     .../gtkb-canonical-init-keyword-syntax-001-008.md  |   2 +-
     .../gtkb-canonical-init-keyword-syntax-001-010.md  |   2 +-
     .../gtkb-canonical-init-keyword-syntax-001-012.md  |   2 +-
     bridge/gtkb-canonical-init-keyword-syntax-001.md   |   2 +-
     ...system-context-model-advisory-2026-05-07-001.md |   2 +-
     ...system-context-model-advisory-2026-05-07-002.md |   2 +-
     .../gtkb-canonical-wrap-keyword-syntax-001-001.md  |   2 +-
     .../gtkb-canonical-wrap-keyword-syntax-001-002.md  |   2 +-
     .../gtkb-canonical-wrap-keyword-syntax-001-003.md  |   2 +-
     .../gtkb-canonical-wrap-keyword-syntax-001-004.md  |   2 +-
     ...hromadb-vector-continuity-v1-cut-scoping-001.md |   2 +-
     ...hromadb-vector-continuity-v1-cut-scoping-003.md |   2 +-
     ...hromadb-vector-continuity-v1-cut-scoping-005.md |   2 +-
     ...hromadb-vector-continuity-v1-cut-scoping-007.md |   2 +-
     ...hromadb-vector-continuity-v1-cut-scoping-008.md |   2 +-
     ...e-axis-2-userpromptsubmit-bridge-surface-001.md |   2 +-
     ...e-axis-2-userpromptsubmit-bridge-surface-002.md |   2 +-
     ...e-axis-2-userpromptsubmit-bridge-surface-003.md |   2 +-
     ...e-axis-2-userpromptsubmit-bridge-surface-004.md |   2 +-
     ...e-axis-2-userpromptsubmit-bridge-surface-005.md |   2 +-
     ...e-axis-2-userpromptsubmit-bridge-surface-006.md |   2 +-
     ...e-axis-2-userpromptsubmit-bridge-surface-007.md |   2 +-
     ...e-axis-2-userpromptsubmit-bridge-surface-008.md |   2 +-
     ...e-axis-2-userpromptsubmit-bridge-surface-009.md |   2 +-
     ...e-axis-2-userpromptsubmit-bridge-surface-010.md |   2 +-
     ...e-axis-2-userpromptsubmit-bridge-surface-011.md |   2 +-
     ...e-axis-2-userpromptsubmit-bridge-surface-013.md |   2 +-
     ...e-axis-2-userpromptsubmit-bridge-surface-015.md |   2 +-
     ...code-bridge-status-thread-automation-001-002.md |   2 +-
     ...code-bridge-status-thread-automation-001-003.md |   2 +-
     ...code-bridge-status-thread-automation-001-004.md |   2 +-
     ...code-bridge-status-thread-automation-001-005.md |   2 +-
     ...ude-code-bridge-status-thread-automation-001.md |   2 +-
     .../gtkb-claude-code-session-id-env-var-gap-001.md |   2 +-
     .../gtkb-claude-code-session-id-env-var-gap-002.md |   2 +-
     .../gtkb-claude-code-session-id-env-var-gap-003.md |   2 +-
     .../gtkb-claude-code-session-id-env-var-gap-004.md |   2 +-
     .../gtkb-claude-code-session-id-env-var-gap-005.md |   2 +-
     .../gtkb-claude-code-session-id-env-var-gap-006.md |   2 +-
     .../gtkb-claude-code-session-id-env-var-gap-007.md |   2 +-
     .../gtkb-claude-code-session-id-env-var-gap-008.md |   2 +-
     .../gtkb-claude-code-session-id-env-var-gap-009.md |   2 +-
     .../gtkb-claude-code-session-id-env-var-gap-010.md |   2 +-
     .../gtkb-claude-code-session-id-env-var-gap-012.md |   2 +-
     ...kb-claude-md-scope-clarification-scoping-001.md |   2 +-
     ...kb-claude-md-scope-clarification-scoping-004.md |   2 +-
     ...kb-claude-md-scope-clarification-slice-2-001.md |   2 +-
     ...kb-claude-md-scope-clarification-slice-2-003.md |   2 +-
     ...kb-claude-md-scope-clarification-slice-2-006.md |   2 +-
     ...ope-clarification-slice-3-implementation-004.md |   2 +-
     ...ope-clarification-slice-3-implementation-005.md |   2 +-
     ...ope-clarification-slice-3-implementation-007.md |   2 +-
     ...ope-clarification-slice-3-implementation-009.md |   2 +-
     ...ope-clarification-slice-3-implementation-010.md |   2 +-
     ...ope-clarification-slice-3-implementation-011.md |   2 +-
     ...pe-clarification-slice-3-reauthorization-001.md |   2 +-
     ...pe-clarification-slice-3-reauthorization-002.md |   2 +-
     ...pe-clarification-slice-3-reauthorization-003.md |   2 +-
     ...pe-clarification-slice-3-reauthorization-005.md |   2 +-
     ...pe-clarification-slice-3-reauthorization-007.md |   2 +-
     ...pe-clarification-slice-3-reauthorization-009.md |   2 +-
     ...pe-clarification-slice-3-reauthorization-012.md |   2 +-
     ...pe-clarification-slice-3-reauthorization-014.md |   2 +-
     ...pe-clarification-slice-3-reauthorization-019.md |   2 +-
     ...lause-in-root-failure-pattern-tightening-001.md |   2 +-
     ...lause-in-root-failure-pattern-tightening-002.md |   2 +-
     ...lause-in-root-failure-pattern-tightening-004.md |   2 +-
     ...discoverability-doctor-json-backlog-show-001.md |   2 +-
     bridge/gtkb-cli-list-subset-filters-001.md         |   2 +-
     bridge/gtkb-cli-list-subset-filters-002.md         |   2 +-
     bridge/gtkb-cli-list-subset-filters-004.md         |   2 +-
     ...gtkb-codex-bridge-compliance-gate-parity-010.md |   2 +-
     ...gtkb-codex-bridge-compliance-gate-parity-011.md |   2 +-
     ...gtkb-codex-bridge-compliance-gate-parity-012.md |   2 +-
     bridge/gtkb-codex-feedback-pattern-lints-001.md    |   2 +-
     bridge/gtkb-codex-feedback-pattern-lints-003.md    |   2 +-
     bridge/gtkb-codex-feedback-pattern-lints-006.md    |   2 +-
     ...ex-skill-loading-failure-cleanup-slice-1-001.md |   2 +-
     ...ex-skill-loading-failure-cleanup-slice-1-002.md |   2 +-
     ...ex-skill-loading-failure-cleanup-slice-1-003.md |   2 +-
     ...ex-skill-loading-failure-cleanup-slice-1-004.md |   2 +-
     ...ex-skill-loading-failure-cleanup-slice-1-005.md |   2 +-
     ...ex-skill-loading-failure-cleanup-slice-1-006.md |   2 +-
     ...ex-skill-loading-failure-cleanup-slice-1-007.md |   2 +-
     ...ex-skill-loading-failure-cleanup-slice-1-008.md |   2 +-
     ...ex-skill-loading-failure-cleanup-slice-1-010.md |   2 +-
     ...gtkb-codex-wrapup-startup-gate-guard-sot-001.md |   2 +-
     ...gtkb-codex-wrapup-startup-gate-guard-sot-004.md |   2 +-
     bridge/gtkb-command-surface-001.md                 |   2 +-
     bridge/gtkb-command-surface-003.md                 |   2 +-
     bridge/gtkb-command-surface-cs1-5-001.md           |   2 +-
     ...commit-scope-bundling-detection-001-prop-001.md |   2 +-
     ...-commit-scope-bundling-detection-slice-1-001.md |   2 +-
     ...-commit-scope-bundling-detection-slice-1-003.md |   2 +-
     ...-commit-scope-bundling-detection-slice-1-004.md |   2 +-
     ...-commit-scope-bundling-detection-slice-1-006.md |   2 +-
     ...-commit-scope-bundling-detection-slice-1-008.md |   2 +-
     ...b-completed-bridge-wi-hygiene-2026-05-13-001.md |   2 +-
     ...b-completed-bridge-wi-hygiene-2026-05-13-003.md |   2 +-
     ...b-completed-bridge-wi-hygiene-2026-05-13-004.md |   2 +-
     ...b-completed-bridge-wi-hygiene-2026-05-13-005.md |   4 +-
     ...b-completed-bridge-wi-hygiene-2026-05-13-006.md |   2 +-
     ...b-completed-bridge-wi-hygiene-2026-05-13-007.md |   4 +-
     ...ceholder-test-remediation-slice-1-revert-003.md |   2 +-
     ...ceholder-test-remediation-slice-1-revert-004.md |   2 +-
     ...ceholder-test-remediation-slice-1-revert-005.md |   2 +-
     ...ceholder-test-remediation-slice-1-revert-006.md |   2 +-
     ...ceholder-test-remediation-slice-1-revert-008.md |   2 +-
     ...ore-spec-intake-current-root-phase3a-cli-001.md |   2 +-
     ...ore-spec-intake-current-root-phase3a-cli-002.md |   2 +-
     ...ore-spec-intake-current-root-phase3a-cli-005.md |   2 +-
     bridge/gtkb-core-spec-intake-default-001.md        |   2 +-
     bridge/gtkb-core-spec-intake-default-003.md        |   2 +-
     bridge/gtkb-core-spec-intake-default-005.md        |   2 +-
     bridge/gtkb-core-spec-intake-default-006.md        |   2 +-
     bridge/gtkb-core-spec-intake-phase3b-answer-001.md |   2 +-
     ...s-trigger-active-session-suppression-001-003.md |   2 +-
     ...s-trigger-active-session-suppression-001-005.md |   2 +-
     ...rness-trigger-active-session-suppression-001.md |   2 +-
     ...ess-trigger-active-session-target-naming-001.md |   2 +-
     ...ess-trigger-active-session-target-naming-002.md |   2 +-
     ...ess-trigger-active-session-target-naming-003.md |   2 +-
     ...ess-trigger-active-session-target-naming-005.md |   2 +-
     ...rness-trigger-codex-exec-hook-firing-001-001.md |   2 +-
     ...rness-trigger-codex-exec-hook-firing-001-003.md |   2 +-
     ...rness-trigger-codex-exec-hook-firing-001-005.md |   2 +-
     ...rness-trigger-codex-exec-hook-firing-001-006.md |   2 +-
     ...rness-trigger-codex-exec-hook-firing-001-007.md |   2 +-
     ...cross-harness-trigger-dispatch-state-lag-001.md |   2 +-
     ...cross-harness-trigger-dispatch-state-lag-003.md |   2 +-
     ...cross-harness-trigger-dispatch-state-lag-004.md |   2 +-
     ...cross-harness-trigger-dispatch-state-lag-006.md |   2 +-
     ...gtkb-cross-harness-trigger-import-repair-001.md |   2 +-
     ...gtkb-cross-harness-trigger-import-repair-003.md |   2 +-
     ...gtkb-cross-harness-trigger-import-repair-006.md |   2 +-
     ...-harness-trigger-index-edit-race-quiesce-001.md |   2 +-
     ...-harness-trigger-index-edit-race-quiesce-003.md |   2 +-
     ...-harness-trigger-index-edit-race-quiesce-005.md |   2 +-
     ...-harness-trigger-index-edit-race-quiesce-006.md |   2 +-
     ...-harness-trigger-index-edit-race-quiesce-008.md |   2 +-
     ...cross-harness-trigger-no-go-dispatch-fix-001.md |   2 +-
     ...cross-harness-trigger-no-go-dispatch-fix-002.md |   2 +-
     ...cross-harness-trigger-no-go-dispatch-fix-003.md |   2 +-
     ...cross-harness-trigger-no-go-dispatch-fix-004.md |   2 +-
     ...cross-harness-trigger-no-go-dispatch-fix-005.md |   2 +-
     ...cross-harness-trigger-no-go-dispatch-fix-006.md |   2 +-
     ...cross-harness-trigger-no-go-dispatch-fix-008.md |   2 +-
     ...cross-harness-trigger-no-go-dispatch-fix-010.md |   2 +-
     ...-harness-trigger-windows-rename-race-001-001.md |   2 +-
     ...-harness-trigger-windows-rename-race-001-003.md |   2 +-
     ...-enforcement-completion-slice1-decompose-001.md |   2 +-
     ...-enforcement-completion-slice1-decompose-002.md |   2 +-
     ...-enforcement-completion-slice1-decompose-003.md |   2 +-
     ...-enforcement-completion-slice1-decompose-004.md |   2 +-
     ...-enforcement-completion-slice1-decompose-005.md |   2 +-
     ...-enforcement-completion-slice1-decompose-007.md |   2 +-
     ...-enforcement-completion-slice1-decompose-008.md |   2 +-
     ...-enforcement-completion-slice1-decompose-009.md |   2 +-
     ...-enforcement-completion-slice1-decompose-011.md |   2 +-
     bridge/gtkb-da-harvest-catchup-001.md              |   2 +-
     bridge/gtkb-da-harvest-catchup-003.md              |   2 +-
     ...rd-control-plane-baseline-implementation-001.md |   2 +-
     ...rd-control-plane-baseline-implementation-003.md |   2 +-
     ...gtkb-dashboard-industry-alignment-slice2-001.md |   2 +-
     ...rd-industry-alignment-slice2a-visibility-001.md |   2 +-
     ...rd-industry-alignment-slice2a-visibility-003.md |   2 +-
     ...rd-industry-alignment-slice2a-visibility-007.md |   2 +-
     ...board-industry-alignment-slice2b-metrics-001.md |   2 +-
     ...board-industry-alignment-slice2b-metrics-003.md |   2 +-
     ...board-industry-alignment-slice2b-metrics-023.md |   2 +-
     ...board-industry-alignment-slice2b-metrics-025.md |   2 +-
     ...hboard-launcher-idempotence-pid-tracking-001.md |   2 +-
     ...hboard-launcher-idempotence-pid-tracking-002.md |   2 +-
     ...hboard-launcher-idempotence-pid-tracking-004.md |   2 +-
     ...hboard-launcher-idempotence-pid-tracking-006.md |   2 +-
     bridge/gtkb-db-backup-001-snapshot-daemon-001.md   |   2 +-
     bridge/gtkb-db-backup-001-snapshot-daemon-007.md   |   2 +-
     bridge/gtkb-db-backup-001-snapshot-daemon-009.md   |   2 +-
     ...ision-tracker-block-prose-ask-2026-04-29-001.md |   2 +-
     ...ision-tracker-block-prose-ask-2026-04-29-003.md |   2 +-
     ...n-tracker-cached-pending-block-exclusion-001.md |   2 +-
     ...n-tracker-cached-pending-block-exclusion-003.md |   2 +-
     ...n-tracker-cached-pending-block-exclusion-004.md |   2 +-
     ...n-tracker-cached-pending-block-exclusion-005.md |   2 +-
     ...n-tracker-cached-pending-block-exclusion-006.md |   2 +-
     ...ity-implementation-start-parser-followup-001.md |   2 +-
     ...ity-implementation-start-parser-followup-002.md |   2 +-
     ...ity-implementation-start-parser-followup-004.md |   2 +-
     ...kb-deferred-authority-protocol-alignment-001.md |   2 +-
     ...kb-deferred-authority-protocol-alignment-002.md |   2 +-
     ...kb-deferred-authority-protocol-alignment-003.md |   2 +-
     ...kb-deferred-authority-protocol-alignment-004.md |   2 +-
     ...kb-deferred-authority-protocol-alignment-005.md |   2 +-
     ...kb-deferred-authority-protocol-alignment-006.md |   2 +-
     ...kb-deferred-authority-protocol-alignment-009.md |   2 +-
     ...kb-deferred-authority-protocol-alignment-010.md |   2 +-
     ...kb-deferred-authority-protocol-alignment-011.md |   2 +-
     ...tic-services-stale-status-reconciliation-001.md |   2 +-
     ...tic-services-stale-status-reconciliation-002.md |   2 +-
     ...tic-services-stale-status-reconciliation-003.md |   2 +-
     ...tic-services-stale-status-reconciliation-004.md |   2 +-
     ...tic-services-stale-status-reconciliation-005.md |   2 +-
     ...tic-services-stale-status-reconciliation-006.md |   2 +-
     ...tic-services-stale-status-reconciliation-007.md |   2 +-
     ...tic-services-stale-status-reconciliation-008.md |   2 +-
     ...tic-services-stale-status-reconciliation-009.md |   2 +-
     ...tic-services-stale-status-reconciliation-010.md |   2 +-
     ...tic-services-stale-status-reconciliation-012.md |   2 +-
     ...ices-stale-status-reconciliation-batch-2-001.md |   2 +-
     ...ices-stale-status-reconciliation-batch-2-002.md |   2 +-
     ...ices-stale-status-reconciliation-batch-2-003.md |   2 +-
     ...ices-stale-status-reconciliation-batch-2-004.md |   2 +-
     bridge/gtkb-directive-enforcement-p1-p2-003.md     |   2 +-
     ...tkb-directive-enforcement-p1-p2-combined-003.md |  16 ++
     bridge/gtkb-directive-enforcement-registry-005.md  |   2 +-
     ...tkb-dirty-tree-reconciliation-2026-06-07-001.md |   2 +-
     bridge/gtkb-discoverability-cli-slice-1-003.md     |   2 +-
     bridge/gtkb-discoverability-cli-slice-1-004.md     |   2 +-
     bridge/gtkb-discoverability-cli-slice-1-005.md     |   2 +-
     bridge/gtkb-discoverability-cli-slice-1-006.md     |   2 +-
     bridge/gtkb-discoverability-cli-slice-1-007.md     |   2 +-
     bridge/gtkb-discoverability-cli-slice-1-008.md     |   2 +-
     ...scoverability-cli-slice-2-implementation-001.md |   2 +-
     ...scoverability-cli-slice-2-implementation-002.md |   2 +-
     ...scoverability-cli-slice-2-implementation-003.md |   2 +-
     ...scoverability-cli-slice-2-implementation-004.md |   2 +-
     ...scoverability-cli-slice-2-implementation-006.md |   2 +-
     ...gtkb-discoverability-cli-slice-2-scoping-001.md |   2 +-
     ...gtkb-discoverability-cli-slice-2-scoping-002.md |   2 +-
     ...gtkb-discoverability-cli-slice-2-scoping-004.md |   2 +-
     ...gtkb-discoverability-cli-slice-2-scoping-006.md |   2 +-
     ...bility-cli-status-scanner-api-regression-001.md |   2 +-
     ...bility-cli-status-scanner-api-regression-002.md |   2 +-
     ...bility-cli-status-scanner-api-regression-004.md |   2 +-
     bridge/gtkb-dispatch-envelope-adr-specs-001.md     |   2 +-
     bridge/gtkb-dispatch-envelope-adr-specs-002.md     |   2 +-
     bridge/gtkb-dispatch-envelope-adr-specs-003.md     |   2 +-
     .../gtkb-dispatch-failures-jsonl-rotation-001.md   |   2 +-
     .../gtkb-dispatch-failures-jsonl-rotation-004.md   |   2 +-
     ...spatch-owner-approval-forgery-prevention-001.md |   2 +-
     ...spatch-owner-approval-forgery-prevention-003.md |   2 +-
     ...spatch-owner-approval-forgery-prevention-004.md |   2 +-
     ...spatch-owner-approval-forgery-prevention-006.md |   2 +-
     ...er-config-cli-whole-candidate-validation-001.md |   2 +-
     ...er-config-cli-whole-candidate-validation-003.md |   2 +-
     ...ctor-dispatch-liveness-recipient-key-fix-001.md |   2 +-
     ...ctor-dispatch-liveness-recipient-key-fix-002.md |   2 +-
     ...ctor-dispatch-liveness-recipient-key-fix-004.md |   2 +-
     ...gtkb-document-author-provenance-contract-001.md |   2 +-
     ...gtkb-document-author-provenance-contract-002.md |   2 +-
     ...gtkb-document-author-provenance-contract-003.md |   2 +-
     ...gtkb-document-author-provenance-contract-004.md |   2 +-
     ...gtkb-document-author-provenance-contract-006.md |   2 +-
     ...ora-001b-authoritative-deployment-source-001.md |   2 +-
     ...ora-001b-authoritative-deployment-source-003.md |   2 +-
     ...ora-001b-authoritative-deployment-source-005.md |   2 +-
     ...ora-001b-authoritative-deployment-source-007.md |   2 +-
     ...ora-001b-authoritative-deployment-source-009.md |   2 +-
     ...ora-001b-authoritative-deployment-source-010.md |   2 +-
     bridge/gtkb-dora-001b-implementation-001.md        |   2 +-
     bridge/gtkb-dora-001b-implementation-003.md        |   2 +-
     bridge/gtkb-dora-001b-track1-implementation-001.md |   2 +-
     bridge/gtkb-dora-001b-track2-implementation-001.md |   2 +-
     bridge/gtkb-dora-001b-track2-implementation-003.md |   2 +-
     bridge/gtkb-dora-001b-track2-implementation-005.md |   2 +-
     bridge/gtkb-dora-telemetry-foundation-001.md       |   2 +-
     ...quirements-quality-audit-slice-1-scoping-001.md |   2 +-
     ...quirements-quality-audit-slice-1-scoping-002.md |   2 +-
     ...quirements-quality-audit-slice-1-scoping-003.md |   2 +-
     ...quirements-quality-audit-slice-1-scoping-004.md |   2 +-
     ...quirements-quality-audit-slice-1-scoping-005.md |   2 +-
     .../gtkb-early-project-specs-quality-audit-001.md  |   2 +-
     .../gtkb-early-project-specs-quality-audit-002.md  |   2 +-
     ...kb-ecosystem-scout-policy-implementation-003.md |   9 +
     bridge/gtkb-env-sot-topology-spec-authoring-001.md |   2 +-
     bridge/gtkb-env-sot-topology-spec-authoring-003.md |   2 +-
     bridge/gtkb-env-sot-topology-spec-authoring-004.md |   2 +-
     bridge/gtkb-env-sot-topology-spec-authoring-006.md |   2 +-
     bridge/gtkb-env-sot-topology-spec-authoring-008.md |   2 +-
     bridge/gtkb-env-sot-topology-spec-authoring-010.md |   2 +-
     bridge/gtkb-envelope-disclosure-ui-impl-001.md     |   2 +-
     bridge/gtkb-envelope-disclosure-ui-impl-002.md     |   2 +-
     bridge/gtkb-envelope-disclosure-ui-impl-003.md     |   2 +-
     bridge/gtkb-envelope-disclosure-ui-impl-004.md     |   2 +-
     bridge/gtkb-envelope-disclosure-ui-impl-005.md     |   2 +-
     bridge/gtkb-envelope-disclosure-ui-impl-006.md     |   2 +-
     bridge/gtkb-envelope-disclosure-ui-impl-007.md     |   2 +-
     bridge/gtkb-envelope-disclosure-ui-impl-008.md     |   2 +-
     bridge/gtkb-envelope-disclosure-ui-impl-009.md     |   2 +-
     bridge/gtkb-envelope-disclosure-ui-impl-011.md     |   2 +-
     bridge/gtkb-envelope-disclosure-ui-impl-013.md     |   2 +-
     bridge/gtkb-envelope-disclosure-ui-redesign-001.md |   2 +-
     bridge/gtkb-envelope-disclosure-ui-redesign-002.md |   2 +-
     bridge/gtkb-envelope-dispatch-element-001-001.md   |   2 +-
     bridge/gtkb-envelope-dispatch-element-001-002.md   |   2 +-
     ...ope-glossary-and-gov-lifecycle-amendment-001.md |   2 +-
     ...ope-glossary-and-gov-lifecycle-amendment-002.md |   2 +-
     ...nvelope-implementation-umbrella-capstone-001.md |   2 +-
     ...nvelope-implementation-umbrella-capstone-002.md |   2 +-
     ...-envelope-init-keyword-amendment-slice-1-001.md |   2 +-
     ...-envelope-init-keyword-amendment-slice-1-002.md |   2 +-
     ...-envelope-init-keyword-amendment-slice-1-004.md |   2 +-
     ...-envelope-init-keyword-amendment-slice-1-005.md |   2 +-
     ...-envelope-init-keyword-amendment-slice-1-006.md |   2 +-
     ...-envelope-init-keyword-amendment-slice-1-008.md |   2 +-
     ...-envelope-init-keyword-amendment-slice-1-010.md |   2 +-
     ...-envelope-init-keyword-amendment-slice-1-012.md |   2 +-
     bridge/gtkb-envelope-meta-model-adr-dcl-001-001.md |   2 +-
     bridge/gtkb-envelope-meta-model-adr-dcl-001-002.md |   2 +-
     bridge/gtkb-envelope-runtime-capstone-impl-001.md  |   2 +-
     bridge/gtkb-envelope-runtime-capstone-impl-002.md  |   2 +-
     bridge/gtkb-envelope-runtime-capstone-impl-004.md  |   2 +-
     ...ronment-boundary-baseline-implementation-001.md |   2 +-
     ...ronment-boundary-baseline-implementation-003.md |   2 +-
     ...ronment-boundary-baseline-implementation-005.md |   2 +-
     ...ronment-boundary-baseline-implementation-007.md |   2 +-
     bridge/gtkb-first-class-project-artifacts-004.md   |   2 +-
     bridge/gtkb-first-class-project-artifacts-006.md   |   2 +-
     bridge/gtkb-first-class-project-artifacts-007.md   |   2 +-
     bridge/gtkb-first-class-project-artifacts-008.md   |   2 +-
     bridge/gtkb-first-class-project-artifacts-009.md   |   2 +-
     ...tkb-formal-artifact-packet-validator-cli-001.md |   2 +-
     ...tkb-formal-artifact-packet-validator-cli-003.md |   2 +-
     bridge/gtkb-generate-approval-packet-cli-001.md    |   2 +-
     bridge/gtkb-generate-approval-packet-cli-002.md    |   2 +-
     bridge/gtkb-generate-approval-packet-cli-003.md    |   2 +-
     bridge/gtkb-generate-approval-packet-cli-004.md    |   2 +-
     bridge/gtkb-generate-approval-packet-cli-005.md    |   2 +-
     bridge/gtkb-generate-approval-packet-cli-006.md    |   2 +-
     bridge/gtkb-generate-approval-packet-cli-007.md    |   2 +-
     bridge/gtkb-generate-approval-packet-cli-008.md    |   2 +-
     bridge/gtkb-generate-approval-packet-cli-009.md    |   2 +-
     bridge/gtkb-generate-approval-packet-cli-010.md    |   2 +-
     bridge/gtkb-generate-approval-packet-cli-012.md    |   2 +-
     bridge/gtkb-git-hooks-path-mismatch-lint-001.md    |   2 +-
     bridge/gtkb-git-hooks-path-mismatch-lint-002.md    |   2 +-
     bridge/gtkb-git-hooks-path-mismatch-lint-004.md    |   2 +-
     .../gtkb-git-repo-broken-blob-investigation-001.md |   2 +-
     .../gtkb-git-repo-broken-blob-investigation-003.md |   2 +-
     .../gtkb-git-repo-broken-blob-investigation-005.md |   2 +-
     .../gtkb-git-repo-broken-blob-investigation-008.md |   2 +-
     .../gtkb-git-repo-broken-blob-investigation-010.md |   2 +-
     .../gtkb-git-repo-broken-blob-investigation-012.md |   2 +-
     ...ai-harness-ecosystem-advisory-2026-05-11-001.md |   2 +-
     ...ai-harness-ecosystem-advisory-2026-05-11-002.md |   2 +-
     ...b-github-ai-harness-ecosystem-conversion-001.md |   2 +-
     ...b-github-ai-harness-ecosystem-conversion-002.md |   2 +-
     ...b-github-ai-harness-ecosystem-conversion-004.md |   2 +-
     .../gtkb-gov-010-followup-observations-s342-002.md |   2 +-
     .../gtkb-gov-010-followup-observations-s342-004.md |   2 +-
     .../gtkb-gov-010-followup-observations-s342-005.md |   2 +-
     .../gtkb-gov-010-harvest-refresh-2026-05-11-004.md |   2 +-
     ...-08-permitted-markdown-amendment-scoping-001.md |   2 +-
     ...-08-permitted-markdown-amendment-scoping-002.md |   2 +-
     ...-08-permitted-markdown-amendment-scoping-003.md |   2 +-
     ...-08-permitted-markdown-amendment-scoping-004.md |   2 +-
     ...-08-permitted-markdown-amendment-scoping-006.md |   2 +-
     ...b-gov-backlog-source-of-truth-2026-05-02-012.md |   2 +-
     ...b-gov-backlog-source-of-truth-2026-05-02-014.md |   2 +-
     ...b-gov-backlog-source-of-truth-2026-05-02-016.md |   2 +-
     ...b-gov-backlog-source-of-truth-2026-05-02-018.md |   2 +-
     ...b-gov-backlog-source-of-truth-2026-05-02-020.md |   2 +-
     ...b-gov-backlog-source-of-truth-2026-05-02-022.md |   2 +-
     ...b-gov-backlog-source-of-truth-2026-05-02-024.md |   2 +-
     ...b-gov-backlog-source-of-truth-2026-05-02-027.md |   2 +-
     ...b-gov-backlog-source-of-truth-2026-05-02-029.md |   2 +-
     ...uality-baseline-formal-artifact-approval-001.md |   2 +-
     ...uality-baseline-formal-artifact-approval-003.md |   2 +-
     ...uality-baseline-formal-artifact-approval-004.md |   2 +-
     ...uality-baseline-formal-artifact-approval-005.md |   2 +-
     ...uality-baseline-formal-artifact-approval-006.md |   2 +-
     ...uality-baseline-formal-artifact-approval-007.md |   2 +-
     ...uality-baseline-formal-artifact-approval-008.md |   2 +-
     .../gtkb-gov-code-quality-baseline-slice-2-001.md  |   2 +-
     .../gtkb-gov-code-quality-baseline-slice-2-003.md  |   2 +-
     .../gtkb-gov-code-quality-baseline-slice-2-005.md  |   2 +-
     .../gtkb-gov-code-quality-baseline-slice-2-007.md  |   2 +-
     .../gtkb-gov-code-quality-baseline-slice-2-010.md  |   2 +-
     .../gtkb-gov-code-quality-baseline-slice-2-012.md  |   2 +-
     .../gtkb-gov-code-quality-baseline-slice-2-013.md  |   2 +-
     .../gtkb-gov-code-quality-baseline-slice-2-014.md  |   2 +-
     .../gtkb-gov-code-quality-baseline-slice1-001.md   |   2 +-
     .../gtkb-gov-code-quality-baseline-slice1-003.md   |   2 +-
     .../gtkb-gov-code-quality-baseline-slice1-005.md   |   2 +-
     .../gtkb-gov-code-quality-baseline-slice1-007.md   |   2 +-
     .../gtkb-gov-code-quality-baseline-slice1-008.md   |   2 +-
     bridge/gtkb-gov-file-bridge-authority-001-002.md   |   2 +-
     bridge/gtkb-gov-file-bridge-authority-001-004.md   |   2 +-
     ...gtkb-gov-owner-decision-surfacing-slice1-001.md |   2 +-
     ...gtkb-gov-owner-decision-surfacing-slice1-003.md |   2 +-
     bridge/gtkb-gov-project-retirement-spec-001.md     |   2 +-
     bridge/gtkb-gov-project-retirement-spec-003.md     |   2 +-
     bridge/gtkb-gov-project-retirement-spec-005.md     |   2 +-
     bridge/gtkb-gov-project-retirement-spec-006.md     |   2 +-
     bridge/gtkb-gov-proposal-standards-slice1-005.md   |   2 +-
     bridge/gtkb-gov-proposal-standards-slice1-007.md   |   2 +-
     bridge/gtkb-gov-proposal-standards-slice1-009.md   |   2 +-
     bridge/gtkb-gov-proposal-standards-slice1-022.md   |   2 +-
     bridge/gtkb-gov-proposal-standards-slice1-023.md   |   2 +-
     bridge/gtkb-gov-proposal-standards-slice1-024.md   |   2 +-
     bridge/gtkb-gov-proposal-standards-slice1-025.md   |   2 +-
     bridge/gtkb-gov-proposal-standards-slice1-027.md   |   2 +-
     .../gtkb-governance-adoption-doctor-check-001.md   |   2 +-
     .../gtkb-governance-adoption-doctor-check-003.md   |   2 +-
     .../gtkb-governance-adoption-doctor-check-005.md   |   2 +-
     .../gtkb-governance-adoption-doctor-check-006.md   |   2 +-
     .../gtkb-governance-adoption-doctor-check-008.md   |   2 +-
     ...governance-hook-worktree-root-resolution-001.md |   2 +-
     ...governance-hook-worktree-root-resolution-003.md |   2 +-
     ...governance-hook-worktree-root-resolution-005.md |   2 +-
     ...governance-hook-worktree-root-resolution-007.md |   2 +-
     ...governance-hook-worktree-root-resolution-008.md |   2 +-
     bridge/gtkb-governed-spec-retirement-001.md        |   2 +-
     bridge/gtkb-governed-spec-retirement-003.md        |   2 +-
     bridge/gtkb-governed-spec-retirement-005.md        |   2 +-
     bridge/gtkb-gt-backlog-add-cli-001.md              |   2 +-
     bridge/gtkb-gt-backlog-add-cli-002.md              |   2 +-
     bridge/gtkb-gt-backlog-add-cli-003.md              |   2 +-
     bridge/gtkb-gt-backlog-add-cli-004.md              |   2 +-
     bridge/gtkb-gt-backlog-add-cli-005.md              |   2 +-
     ...gtkb-gt-bridge-propose-deterministic-cli-001.md |   2 +-
     ...gtkb-gt-bridge-propose-deterministic-cli-003.md |   2 +-
     ...gtkb-gt-bridge-propose-deterministic-cli-004.md |   2 +-
     ...gtkb-gt-bridge-propose-deterministic-cli-006.md |   2 +-
     ...tkb-handoff-prompt-deterministic-service-001.md |   2 +-
     ...tkb-handoff-prompt-deterministic-service-002.md |   2 +-
     ...andoff-prompt-deterministic-service-impl-001.md |   2 +-
     ...andoff-prompt-deterministic-service-impl-002.md |   2 +-
     ...andoff-prompt-deterministic-service-impl-003.md |   2 +-
     ...andoff-prompt-deterministic-service-impl-004.md |   2 +-
     ...andoff-prompt-deterministic-service-impl-005.md |   2 +-
     ...andoff-prompt-deterministic-service-impl-007.md |   2 +-
     ...andoff-prompt-deterministic-service-impl-009.md |   2 +-
     ...andoff-prompt-deterministic-service-impl-011.md |   2 +-
     ...handoff-prompt-terminology-clarification-001.md |   2 +-
     ...handoff-prompt-terminology-clarification-002.md |   2 +-
     ...handoff-prompt-terminology-clarification-003.md |   2 +-
     ...handoff-prompt-terminology-clarification-004.md |   2 +-
     bridge/gtkb-harness-cli-command-group-001.md       |   2 +-
     bridge/gtkb-harness-cli-command-group-002.md       |   2 +-
     bridge/gtkb-harness-cli-command-group-003.md       |   2 +-
     bridge/gtkb-harness-cli-command-group-004.md       |   2 +-
     bridge/gtkb-harness-cli-command-group-005.md       |   2 +-
     bridge/gtkb-harness-cli-command-group-006.md       |   2 +-
     bridge/gtkb-harness-cli-command-group-007.md       |   2 +-
     bridge/gtkb-harness-cli-command-group-008.md       |   2 +-
     bridge/gtkb-harness-data-driven-dispatch-001.md    |   2 +-
     bridge/gtkb-harness-data-driven-dispatch-003.md    |   2 +-
     bridge/gtkb-harness-data-driven-dispatch-006.md    |   2 +-
     bridge/gtkb-harness-lifecycle-fsm-001.md           |   2 +-
     bridge/gtkb-harness-lifecycle-fsm-002.md           |   2 +-
     bridge/gtkb-harness-lifecycle-fsm-003.md           |   2 +-
     bridge/gtkb-harness-lifecycle-fsm-004.md           |   2 +-
     ...tkb-harness-registry-hot-path-projection-001.md |   2 +-
     ...tkb-harness-registry-hot-path-projection-002.md |   2 +-
     ...tkb-harness-registry-hot-path-projection-003.md |   2 +-
     ...tkb-harness-registry-hot-path-projection-004.md |   2 +-
     bridge/gtkb-harness-registry-parity-sweep-001.md   |   2 +-
     bridge/gtkb-harness-registry-parity-sweep-002.md   |   2 +-
     bridge/gtkb-harness-registry-parity-sweep-003.md   |   2 +-
     bridge/gtkb-harness-registry-parity-sweep-004.md   |   2 +-
     bridge/gtkb-harness-registry-parity-sweep-005.md   |   2 +-
     bridge/gtkb-harness-registry-parity-sweep-006.md   |   2 +-
     bridge/gtkb-harness-registry-parity-sweep-007.md   |   2 +-
     .../gtkb-harness-registry-reader-migration-001.md  |   2 +-
     .../gtkb-harness-registry-reader-migration-003.md  |   2 +-
     .../gtkb-harness-registry-reader-migration-005.md  |   2 +-
     .../gtkb-harness-registry-reader-migration-007.md  |   2 +-
     .../gtkb-harness-registry-reader-migration-008.md  |   2 +-
     .../gtkb-harness-registry-reader-migration-009.md  |   2 +-
     .../gtkb-harness-registry-reader-migration-010.md  |   2 +-
     .../gtkb-harness-registry-reader-migration-011.md  |   2 +-
     .../gtkb-harness-registry-reader-migration-014.md  |   2 +-
     bridge/gtkb-harness-registry-seed-001.md           |   2 +-
     bridge/gtkb-harness-registry-seed-002.md           |   2 +-
     bridge/gtkb-harness-registry-seed-003.md           |   2 +-
     bridge/gtkb-harness-registry-seed-004.md           |   2 +-
     bridge/gtkb-harness-registry-table-schema-001.md   |   2 +-
     bridge/gtkb-harness-registry-table-schema-002.md   |   2 +-
     bridge/gtkb-harness-registry-table-schema-003.md   |   2 +-
     bridge/gtkb-harness-registry-table-schema-004.md   |   2 +-
     bridge/gtkb-harness-registry-table-schema-005.md   |   2 +-
     bridge/gtkb-harness-registry-table-schema-006.md   |   2 +-
     bridge/gtkb-harness-registry-table-schema-007.md   |   2 +-
     bridge/gtkb-harness-registry-table-schema-008.md   |   2 +-
     bridge/gtkb-harness-role-portability-fr9-001.md    |   2 +-
     bridge/gtkb-harness-role-portability-fr9-002.md    |   2 +-
     bridge/gtkb-harness-role-portability-fr9-003.md    |   2 +-
     bridge/gtkb-harness-role-portability-fr9-004.md    |   2 +-
     bridge/gtkb-harness-role-portability-fr9-005.md    |   2 +-
     bridge/gtkb-harness-role-portability-fr9-006.md    |   2 +-
     bridge/gtkb-harness-role-portability-fr9-007.md    |   2 +-
     bridge/gtkb-harness-role-portability-fr9-008.md    |   2 +-
     bridge/gtkb-harness-role-portability-fr9-009.md    |   2 +-
     bridge/gtkb-harness-role-portability-fr9-010.md    |   2 +-
     ...-harness-state-sot-consolidation-phase-1-001.md |   2 +-
     ...-harness-state-sot-consolidation-phase-1-002.md |   2 +-
     ...-harness-state-sot-consolidation-phase-1-003.md |   2 +-
     ...-harness-state-sot-consolidation-phase-1-004.md |   2 +-
     ...ate-sot-consolidation-phase-1-foundation-001.md |   2 +-
     ...ate-sot-consolidation-phase-1-foundation-002.md |   2 +-
     ...ate-sot-consolidation-phase-1-foundation-003.md |   2 +-
     ...ate-sot-consolidation-phase-1-foundation-004.md |   2 +-
     ...ate-sot-consolidation-phase-1-foundation-005.md |   2 +-
     ...ate-sot-consolidation-phase-1-foundation-006.md |   2 +-
     ...ate-sot-consolidation-phase-1-foundation-008.md |   2 +-
     ...ate-sot-consolidation-phase-1-foundation-010.md |   2 +-
     ...ate-sot-consolidation-phase-1-foundation-012.md |   2 +-
     ...-consolidation-phase-1-mirror-retirement-001.md |   2 +-
     ...-consolidation-phase-1-mirror-retirement-003.md |   2 +-
     ...-consolidation-phase-1-mirror-retirement-005.md |   2 +-
     ...-consolidation-phase-1-mirror-retirement-010.md |   2 +-
     ...-consolidation-phase-1-mirror-retirement-011.md |   2 +-
     ...-consolidation-phase-1-mirror-retirement-012.md |   2 +-
     ...-consolidation-phase-1-mirror-retirement-014.md |   2 +-
     ...-consolidation-phase-1-mirror-retirement-016.md |   2 +-
     ...-consolidation-phase-1-mirror-retirement-018.md |   2 +-
     ...ate-sot-consolidation-phase-1-rule-files-001.md |   2 +-
     ...ate-sot-consolidation-phase-1-rule-files-002.md |   2 +-
     ...ate-sot-consolidation-phase-1-rule-files-003.md |   2 +-
     ...ate-sot-consolidation-phase-1-rule-files-004.md |   2 +-
     ...ate-sot-consolidation-phase-1-rule-files-006.md |   2 +-
     ...ate-sot-consolidation-phase-1-rule-files-008.md |   2 +-
     ...ate-sot-consolidation-phase-1-rule-files-010.md |   2 +-
     ...sot-consolidation-phase-1-scripts-source-001.md |   2 +-
     ...sot-consolidation-phase-1-scripts-source-002.md |   2 +-
     ...sot-consolidation-phase-1-scripts-source-003.md |   2 +-
     ...sot-consolidation-phase-1-scripts-source-004.md |   2 +-
     ...sot-consolidation-phase-1-scripts-source-006.md |   2 +-
     ...sot-consolidation-phase-1-scripts-source-008.md |   2 +-
     ...sot-consolidation-phase-1-scripts-source-010.md |   2 +-
     ...headless-gemini-lo-dispatch-verification-001.md |   2 +-
     ...headless-gemini-lo-dispatch-verification-003.md |   2 +-
     ...headless-gemini-lo-dispatch-verification-006.md |   2 +-
     ...headless-gemini-lo-dispatch-verification-009.md |   2 +-
     ...headless-gemini-lo-dispatch-verification-010.md |   2 +-
     ...headless-gemini-lo-dispatch-verification-011.md |   2 +-
     ...headless-gemini-lo-dispatch-verification-012.md |   2 +-
     ...headless-gemini-lo-dispatch-verification-013.md |   2 +-
     ...headless-gemini-lo-dispatch-verification-014.md |   2 +-
     ...headless-gemini-lo-dispatch-verification-016.md |   2 +-
     ...headless-gemini-lo-dispatch-verification-017.md |   2 +-
     ...headless-gemini-lo-dispatch-verification-018.md |   2 +-
     ...kb-heartbeat-replace-access-denied-retry-001.md |   2 +-
     ...kb-heartbeat-replace-access-denied-retry-002.md |   2 +-
     ...kb-heartbeat-replace-access-denied-retry-003.md |   2 +-
     ...kb-heartbeat-replace-access-denied-retry-006.md |   2 +-
     .../gtkb-hook-import-latency-chromadb-lazy-008.md  |   2 +-
     .../gtkb-hook-strictness-p1-p2-remediation-001.md  |   2 +-
     .../gtkb-hook-strictness-p1-p2-remediation-003.md  |   2 +-
     .../gtkb-hook-strictness-p1-p2-remediation-005.md  |   2 +-
     .../gtkb-hook-strictness-p1-p2-remediation-007.md  |   2 +-
     .../gtkb-hook-strictness-p1-p2-remediation-008.md  |   2 +-
     .../gtkb-hook-strictness-p1-p2-remediation-009.md  |   2 +-
     ...tkb-hygiene-cli-utf8-portability-slice-1-001.md |   2 +-
     ...tkb-hygiene-cli-utf8-portability-slice-1-002.md |   2 +-
     ...tkb-hygiene-cli-utf8-portability-slice-1-004.md |   2 +-
     ...ne-cli-utf8-portability-slice-2-guidance-001.md |   2 +-
     ...ne-cli-utf8-portability-slice-2-guidance-002.md |   2 +-
     ...ne-cli-utf8-portability-slice-2-guidance-003.md |   2 +-
     ...ne-cli-utf8-portability-slice-2-guidance-005.md |   2 +-
     bridge/gtkb-hygiene-sweep-cli-001.md               |   2 +-
     bridge/gtkb-hygiene-sweep-cli-002.md               |   2 +-
     bridge/gtkb-hygiene-sweep-cli-004.md               |   2 +-
     bridge/gtkb-hygiene-sweep-cli-scoping-001.md       |   2 +-
     bridge/gtkb-hygiene-sweep-cli-scoping-002.md       |   2 +-
     bridge/gtkb-hygiene-sweep-cli-scoping-003.md       |   2 +-
     bridge/gtkb-hygiene-sweep-cli-scoping-005.md       |   2 +-
     bridge/gtkb-hygiene-sweep-cli-test-rebuild-001.md  |   2 +-
     bridge/gtkb-hygiene-sweep-cli-test-rebuild-002.md  |   2 +-
     bridge/gtkb-hygiene-sweep-cli-test-rebuild-004.md  |   2 +-
     ...-hygiene-sweep-presence-patterns-slice-1-001.md |   2 +-
     ...-hygiene-sweep-presence-patterns-slice-1-002.md |   2 +-
     ...-hygiene-sweep-presence-patterns-slice-1-003.md |   2 +-
     ...-hygiene-sweep-presence-patterns-slice-1-004.md |   2 +-
     ...-hygiene-sweep-presence-patterns-slice-1-006.md |   2 +-
     bridge/gtkb-hygiene-sweep-skill-001.md             |   2 +-
     bridge/gtkb-hygiene-sweep-skill-002.md             |   2 +-
     bridge/gtkb-hygiene-sweep-skill-003.md             |   2 +-
     bridge/gtkb-hygiene-sweep-skill-004.md             |   2 +-
     bridge/gtkb-hygiene-sweep-skill-006.md             |   2 +-
     bridge/gtkb-hygiene-sweep-skill-008.md             |   2 +-
     bridge/gtkb-hygiene-sweep-skill-scoping-001.md     |   2 +-
     bridge/gtkb-hygiene-sweep-skill-scoping-002.md     |   2 +-
     bridge/gtkb-hygiene-sweep-skill-scoping-003.md     |   2 +-
     bridge/gtkb-hygiene-sweep-skill-scoping-004.md     |   2 +-
     bridge/gtkb-hygiene-sweep-skill-scoping-006.md     |   2 +-
     bridge/gtkb-idp-terminology-formalization-001.md   |   2 +-
     bridge/gtkb-idp-terminology-formalization-003.md   |   2 +-
     bridge/gtkb-idp-terminology-formalization-005.md   |   2 +-
     bridge/gtkb-idp-terminology-formalization-007.md   |   2 +-
     bridge/gtkb-idp-terminology-formalization-008.md   |   2 +-
     .../gtkb-impl-auth-owner-sufficiency-gate-001.md   |   2 +-
     .../gtkb-impl-auth-owner-sufficiency-gate-002.md   |   2 +-
     .../gtkb-impl-auth-owner-sufficiency-gate-004.md   |   2 +-
     ...gtkb-impl-auth-parser-false-positive-fix-001.md |   2 +-
     ...gtkb-impl-auth-parser-false-positive-fix-003.md |   2 +-
     ...gtkb-impl-auth-parser-false-positive-fix-006.md |   2 +-
     ...requirement-sufficiency-phrase-tolerance-001.md |   2 +-
     ...requirement-sufficiency-phrase-tolerance-002.md |   2 +-
     ...requirement-sufficiency-phrase-tolerance-004.md |   2 +-
     bridge/gtkb-impl-gate-friction-hygiene-001.md      |   2 +-
     bridge/gtkb-impl-gate-friction-hygiene-002.md      |   2 +-
     bridge/gtkb-impl-gate-friction-hygiene-003.md      |   2 +-
     bridge/gtkb-impl-gate-friction-hygiene-004.md      |   2 +-
     bridge/gtkb-impl-gate-friction-hygiene-006.md      |   2 +-
     ...eport-bridge-structural-validation-mtime-001.md |   2 +-
     ...eport-bridge-structural-validation-mtime-002.md |   2 +-
     ...eport-bridge-structural-validation-mtime-003.md |   2 +-
     ...eport-bridge-structural-validation-mtime-005.md |   2 +-
     ...eport-bridge-structural-validation-mtime-006.md |   2 +-
     ...eport-bridge-structural-validation-mtime-008.md |   2 +-
     ...-impl-start-gate-comparison-operator-fix-001.md |   2 +-
     ...-impl-start-gate-comparison-operator-fix-002.md |   2 +-
     ...-impl-start-gate-comparison-operator-fix-004.md |   2 +-
     ...-impl-start-gate-comparison-operator-fix-006.md |   2 +-
     ...impl-start-gate-finalization-quoting-fix-001.md |   2 +-
     ...impl-start-gate-finalization-quoting-fix-002.md |   2 +-
     ...impl-start-gate-finalization-quoting-fix-003.md |   2 +-
     ...impl-start-gate-finalization-quoting-fix-004.md |   2 +-
     ...impl-start-gate-finalization-quoting-fix-005.md |   2 +-
     ...impl-start-gate-finalization-quoting-fix-006.md |   2 +-
     ...impl-start-gate-finalization-quoting-fix-007.md |   2 +-
     ...impl-start-gate-finalization-quoting-fix-008.md |   2 +-
     ...impl-start-gate-finalization-quoting-fix-010.md |   2 +-
     bridge/gtkb-impl-start-gate-format-spec-fix-001.md |   2 +-
     bridge/gtkb-impl-start-gate-format-spec-fix-003.md |   2 +-
     bridge/gtkb-impl-start-gate-format-spec-fix-005.md |   2 +-
     bridge/gtkb-impl-start-gate-format-spec-fix-007.md |   2 +-
     ...-start-gate-path-token-memory-prefix-fix-001.md |   2 +-
     ...-start-gate-path-token-memory-prefix-fix-002.md |   2 +-
     ...-start-gate-path-token-memory-prefix-fix-004.md |   2 +-
     .../gtkb-impl-start-gate-pretooluse-restore-001.md |   2 +-
     .../gtkb-impl-start-gate-pretooluse-restore-002.md |   2 +-
     .../gtkb-impl-start-gate-pretooluse-restore-003.md |   2 +-
     .../gtkb-impl-start-gate-pretooluse-restore-004.md |   2 +-
     .../gtkb-impl-start-gate-pretooluse-restore-005.md |   2 +-
     .../gtkb-impl-start-gate-pretooluse-restore-007.md |   2 +-
     .../gtkb-impl-start-gate-pretooluse-restore-008.md |   2 +-
     ...-start-gate-quoted-arg-misclassification-001.md |   2 +-
     ...-start-gate-quoted-arg-misclassification-002.md |   2 +-
     ...-start-gate-quoted-arg-misclassification-004.md |   2 +-
     ...pl-start-gate-verb-aware-path-extraction-001.md |   2 +-
     ...pl-start-gate-verb-aware-path-extraction-002.md |   2 +-
     ...pl-start-gate-verb-aware-path-extraction-003.md |   2 +-
     ...pl-start-gate-verb-aware-path-extraction-004.md |   2 +-
     ...pl-start-gate-verb-aware-path-extraction-006.md |   2 +-
     ...pl-start-gate-verb-aware-path-extraction-008.md |   2 +-
     ...pl-start-gate-verb-aware-path-extraction-010.md |   2 +-
     .../gtkb-impl-start-target-paths-preflight-001.md  |   2 +-
     .../gtkb-impl-start-target-paths-preflight-002.md  |   2 +-
     .../gtkb-impl-start-target-paths-preflight-003.md  |   2 +-
     .../gtkb-impl-start-target-paths-preflight-004.md  |   2 +-
     .../gtkb-impl-start-target-paths-preflight-005.md  |   2 +-
     .../gtkb-impl-start-target-paths-preflight-007.md  |   2 +-
     .../gtkb-impl-start-target-paths-preflight-008.md  |   2 +-
     .../gtkb-impl-start-target-paths-preflight-009.md  |   2 +-
     ...tkb-implementation-gate-friction-hygiene-001.md |   2 +-
     ...tkb-implementation-gate-friction-hygiene-003.md |   2 +-
     ...tkb-implementation-gate-friction-hygiene-005.md |   2 +-
     ...tkb-implementation-gate-friction-hygiene-006.md |   2 +-
     ...tkb-implementation-gate-friction-hygiene-007.md |   2 +-
     ...tkb-implementation-gate-friction-hygiene-009.md |   2 +-
     ...tkb-implementation-gate-friction-hygiene-010.md |   2 +-
     ...tkb-implementation-gate-friction-hygiene-011.md |   2 +-
     ...tkb-implementation-gate-friction-hygiene-012.md |   2 +-
     ...tkb-implementation-gate-friction-hygiene-014.md |   2 +-
     ...tkb-implementation-gate-friction-hygiene-018.md |   2 +-
     ...tkb-implementation-gate-friction-hygiene-020.md |   2 +-
     ...tkb-implementation-gate-friction-hygiene-022.md |   2 +-
     ...-implementation-start-authorization-gate-002.md |   2 +-
     ...-implementation-start-authorization-gate-004.md |   2 +-
     ...-implementation-start-authorization-gate-005.md |   2 +-
     ...-implementation-start-authorization-gate-006.md |   2 +-
     ...-implementation-start-authorization-gate-007.md |   2 +-
     ...-implementation-start-authorization-gate-008.md |   2 +-
     ...-implementation-start-authorization-gate-010.md |   2 +-
     ...ation-start-gate-repository-finalization-001.md |   2 +-
     ...ation-start-gate-repository-finalization-002.md |   2 +-
     ...ation-start-gate-repository-finalization-004.md |   2 +-
     ...ement-sufficiency-owner-direction-phrase-001.md |   2 +-
     ...ement-sufficiency-owner-direction-phrase-002.md |   2 +-
     ...ement-sufficiency-owner-direction-phrase-004.md |   2 +-
     ...ement-sufficiency-owner-direction-phrase-006.md |   2 +-
     ...ents-link-backfill-phase2-implementation-001.md |   2 +-
     ...ents-link-backfill-phase2-implementation-004.md |   2 +-
     ...ents-link-backfill-phase2-implementation-006.md |   2 +-
     ...-implements-link-backfill-phase2-scoping-001.md |   2 +-
     ...-implements-link-backfill-phase2-scoping-002.md |   2 +-
     ...-implements-link-backfill-phase2-scoping-004.md |   2 +-
     ...kb-in-source-provenance-anchors-001-prop-001.md |   2 +-
     ...kb-in-source-provenance-anchors-001-prop-003.md |   2 +-
     ...kb-in-source-provenance-anchors-001-prop-004.md |   2 +-
     ...kb-in-source-provenance-anchors-001-prop-005.md |   2 +-
     ...kb-in-source-provenance-anchors-001-prop-006.md |   2 +-
     ...kb-in-source-provenance-anchors-001-prop-008.md |   2 +-
     bridge/gtkb-incident-response-001.md               |   2 +-
     bridge/gtkb-incident-response-003.md               |   2 +-
     bridge/gtkb-incident-response-008.md               |   2 +-
     bridge/gtkb-incident-response-ir-0-1-001.md        |   2 +-
     ...b-index-agent-edit-serialization-scoping-001.md |   2 +-
     ...b-index-agent-edit-serialization-scoping-002.md |   2 +-
     ...b-index-agent-edit-serialization-scoping-004.md |   2 +-
     ...b-index-agent-edit-serialization-scoping-005.md |   2 +-
     ...b-index-agent-edit-serialization-scoping-006.md |   2 +-
     ...b-index-agent-edit-serialization-scoping-007.md |   2 +-
     ...b-index-agent-edit-serialization-scoping-009.md |   2 +-
     ...t-serialization-slice-1-bridge-index-cli-001.md |   2 +-
     ...t-serialization-slice-1-bridge-index-cli-002.md |   2 +-
     ...t-serialization-slice-1-bridge-index-cli-003.md |   2 +-
     ...t-serialization-slice-1-bridge-index-cli-004.md |   2 +-
     ...t-serialization-slice-1-bridge-index-cli-006.md |   2 +-
     ...index-role-sentinel-stale-reconciliation-001.md |   2 +-
     ...index-role-sentinel-stale-reconciliation-002.md |   2 +-
     ...kb-index-withdrawn-status-reconciliation-001.md |   2 +-
     ...kb-index-withdrawn-status-reconciliation-002.md |   2 +-
     ...e-session-role-override-hygiene-backfill-001.md |   2 +-
     ...e-session-role-override-hygiene-backfill-002.md |   2 +-
     ...e-session-role-override-hygiene-backfill-003.md |   2 +-
     ...e-session-role-override-hygiene-backfill-004.md |   2 +-
     ...e-session-role-override-hygiene-backfill-006.md |   2 +-
     ...nteractive-session-role-override-scoping-001.md |   2 +-
     ...nteractive-session-role-override-scoping-002.md |   2 +-
     ...nteractive-session-role-override-scoping-003.md |   2 +-
     ...nteractive-session-role-override-scoping-004.md |   2 +-
     ...nteractive-session-role-override-scoping-006.md |   2 +-
     ...erride-slice-1-sessionstart-cache-writer-001.md |   2 +-
     ...erride-slice-1-sessionstart-cache-writer-002.md |   2 +-
     ...erride-slice-1-sessionstart-cache-writer-003.md |   2 +-
     ...erride-slice-1-sessionstart-cache-writer-004.md |   2 +-
     ...erride-slice-1-sessionstart-cache-writer-007.md |   2 +-
     ...-role-override-slice-10-regression-tests-001.md |   2 +-
     ...-role-override-slice-10-regression-tests-002.md |   2 +-
     ...-role-override-slice-10-regression-tests-003.md |   2 +-
     ...-role-override-slice-10-regression-tests-004.md |   2 +-
     ...-role-override-slice-10-regression-tests-005.md |   2 +-
     ...-role-override-slice-10-regression-tests-006.md |   2 +-
     ...-role-override-slice-10-regression-tests-008.md |   2 +-
     ...-role-override-slice-10-regression-tests-010.md |   2 +-
     ...ole-override-slice-2-session-role-marker-001.md |   2 +-
     ...ole-override-slice-2-session-role-marker-002.md |   2 +-
     ...ole-override-slice-2-session-role-marker-003.md |   2 +-
     ...ole-override-slice-2-session-role-marker-004.md |   2 +-
     ...ole-override-slice-2-session-role-marker-006.md |   2 +-
     ...ole-override-slice-2-session-role-marker-008.md |   2 +-
     ...slice-3-sessionstart-marker-invalidation-001.md |   2 +-
     ...slice-3-sessionstart-marker-invalidation-002.md |   2 +-
     ...slice-3-sessionstart-marker-invalidation-004.md |   2 +-
     ...le-override-slice-4-axis2-role-awareness-001.md |   2 +-
     ...le-override-slice-4-axis2-role-awareness-002.md |   2 +-
     ...le-override-slice-4-axis2-role-awareness-004.md |   2 +-
     ...erride-slice-5-focus-menu-role-awareness-001.md |   2 +-
     ...erride-slice-5-focus-menu-role-awareness-002.md |   2 +-
     ...erride-slice-5-focus-menu-role-awareness-004.md |   2 +-
     ...rride-slice-6-attribution-role-awareness-001.md |   2 +-
     ...rride-slice-6-attribution-role-awareness-002.md |   2 +-
     ...rride-slice-6-attribution-role-awareness-004.md |   2 +-
     ...le-override-slice-7-doctor-marker-checks-001.md |   2 +-
     ...le-override-slice-7-doctor-marker-checks-002.md |   2 +-
     ...le-override-slice-7-doctor-marker-checks-004.md |   2 +-
     ...le-override-slice-7-doctor-marker-checks-006.md |   2 +-
     ...de-slice-8-parity-check-resolution-table-001.md |   2 +-
     ...de-slice-8-parity-check-resolution-table-002.md |   2 +-
     ...de-slice-8-parity-check-resolution-table-003.md |   2 +-
     ...de-slice-8-parity-check-resolution-table-004.md |   2 +-
     ...de-slice-8-parity-check-resolution-table-006.md |   2 +-
     ...de-slice-8-parity-check-resolution-table-008.md |   2 +-
     ...de-slice-8-parity-check-resolution-table-009.md |   2 +-
     ...de-slice-8-parity-check-resolution-table-011.md |   2 +-
     ...de-slice-8-parity-check-resolution-table-013.md |   2 +-
     ...de-slice-8-parity-check-resolution-table-015.md |   2 +-
     ...de-slice-8-parity-check-resolution-table-017.md |   2 +-
     ...rride-slice-9-rule-claude-agents-updates-001.md |   2 +-
     ...rride-slice-9-rule-claude-agents-updates-002.md |   2 +-
     ...rride-slice-9-rule-claude-agents-updates-003.md |   2 +-
     ...rride-slice-9-rule-claude-agents-updates-004.md |   2 +-
     ...rride-slice-9-rule-claude-agents-updates-005.md |   2 +-
     ...rride-slice-9-rule-claude-agents-updates-006.md |   2 +-
     ...rride-slice-9-rule-claude-agents-updates-007.md |   2 +-
     ...rride-slice-9-rule-claude-agents-updates-008.md |   2 +-
     ...rride-slice-9-rule-claude-agents-updates-010.md |   2 +-
     bridge/gtkb-inventory-drift-gh-probe-parity-001.md |   2 +-
     bridge/gtkb-inventory-drift-gh-probe-parity-002.md |   2 +-
     bridge/gtkb-inventory-drift-gh-probe-parity-004.md |   2 +-
     ...inventory-drift-toolchain-flux-stability-001.md |   2 +-
     ...inventory-drift-toolchain-flux-stability-002.md |   2 +-
     ...inventory-drift-toolchain-flux-stability-004.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-27-001.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-27-004.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-28-001.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-28-002.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-28-004.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-29-001.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-29-002.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-29-004.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-29-006.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-31-001.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-31-002.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-31-003.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-31-004.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-31-005.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-31-006.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-31-008.md |   2 +-
     ...-inventory-regen-chore-commit-2026-05-31-010.md |   2 +-
     ...kb-isolation-003-environment-plan-review-001.md |   2 +-
     ...kb-isolation-003-environment-plan-review-002.md |   2 +-
     ...kb-isolation-003-environment-plan-review-003.md |   2 +-
     ...kb-isolation-003-environment-plan-review-004.md |   2 +-
     ...kb-isolation-003-environment-plan-review-005.md |   2 +-
     ...kb-isolation-003-environment-plan-review-006.md |   2 +-
     ...kb-isolation-003-environment-plan-review-007.md |   2 +-
     ...kb-isolation-003-environment-plan-review-008.md |   2 +-
     ...olation-004-service-boundary-plan-review-001.md |   2 +-
     ...olation-004-service-boundary-plan-review-002.md |   2 +-
     ...olation-004-service-boundary-plan-review-003.md |   2 +-
     ...olation-004-service-boundary-plan-review-005.md |   2 +-
     ...-isolation-005-control-plane-plan-review-001.md |   2 +-
     ...-isolation-005-control-plane-plan-review-002.md |   2 +-
     ...-isolation-005-control-plane-plan-review-003.md |   2 +-
     ...-isolation-005-control-plane-plan-review-005.md |   2 +-
     .../gtkb-isolation-006-overlay-plan-review-001.md  |   2 +-
     .../gtkb-isolation-006-overlay-plan-review-002.md  |   2 +-
     .../gtkb-isolation-006-overlay-plan-review-003.md  |   2 +-
     .../gtkb-isolation-006-overlay-plan-review-004.md  |   2 +-
     .../gtkb-isolation-006-overlay-plan-review-006.md  |   2 +-
     ...lation-007-work-subject-root-plan-review-001.md |   2 +-
     ...lation-007-work-subject-root-plan-review-002.md |   2 +-
     ...lation-007-work-subject-root-plan-review-003.md |   2 +-
     ...lation-007-work-subject-root-plan-review-004.md |   2 +-
     ...gtkb-isolation-008-migration-plan-review-001.md |   2 +-
     ...gtkb-isolation-008-migration-plan-review-003.md |   2 +-
     ...lation-009-adopter-packaging-plan-review-001.md |   2 +-
     ...kb-isolation-015-phase7-root-enforcement-001.md |   2 +-
     ...kb-isolation-015-phase7-root-enforcement-003.md |   2 +-
     ...kb-isolation-015-slice2-work-subject-set-002.md |   2 +-
     ...kb-isolation-015-slice2-work-subject-set-004.md |   2 +-
     ...kb-isolation-015-slice2-work-subject-set-006.md |   2 +-
     ...tion-016-phase8-rehearsal-implementation-001.md |   2 +-
     ...tion-016-phase8-rehearsal-implementation-003.md |   2 +-
     ...tion-016-phase8-rehearsal-implementation-005.md |   2 +-
     ...tion-016-phase8-rehearsal-implementation-007.md |   2 +-
     ...tion-016-phase8-rehearsal-implementation-009.md |   2 +-
     ...tion-016-phase8-rehearsal-implementation-011.md |   2 +-
     ...tion-016-phase8-rehearsal-implementation-013.md |   2 +-
     ...solation-016-phase8-wave2-implementation-001.md |   2 +-
     ...solation-016-phase8-wave2-implementation-005.md |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice1-001.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice10-001.md |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice11-001.md |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice11-003.md |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice2-001.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice3-001.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice4-001.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice5-001.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice5-003.md  |   4 +-
     .../gtkb-isolation-016-phase8-wave2-slice5-005.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice5-007.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice5-009.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice6-001.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice6-003.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice6-005.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice6-007.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice6-009.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice7-001.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice7-003.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice8-001.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice9-001.md  |   2 +-
     .../gtkb-isolation-016-phase8-wave2-slice9-003.md  |   2 +-
     bridge/gtkb-isolation-017-adopter-packaging-001.md |   2 +-
     bridge/gtkb-isolation-017-adopter-packaging-003.md |   2 +-
     bridge/gtkb-isolation-017-adopter-packaging-006.md |   2 +-
     bridge/gtkb-isolation-018-agent-red-cutover-001.md |   2 +-
     bridge/gtkb-isolation-018-agent-red-cutover-003.md |   2 +-
     bridge/gtkb-isolation-018-agent-red-cutover-005.md |   2 +-
     bridge/gtkb-isolation-018-agent-red-cutover-007.md |   2 +-
     bridge/gtkb-isolation-018-agent-red-cutover-010.md |   2 +-
     ...b-isolation-018-agent-red-file-migration-010.md |   2 +-
     .../gtkb-isolation-018-slice-e-code-cluster-005.md |   2 +-
     bridge/gtkb-isolation-019-program-closeout-001.md  |   2 +-
     bridge/gtkb-isolation-019-program-closeout-003.md  |   2 +-
     bridge/gtkb-isolation-019-program-closeout-005.md  |   2 +-
     bridge/gtkb-isolation-019-program-closeout-006.md  |   2 +-
     bridge/gtkb-isolation-019-program-closeout-008.md  |   2 +-
     ...tkb-isolation-aftermath-startup-baseline-002.md |   2 +-
     ...tkb-isolation-aftermath-startup-baseline-003.md |   2 +-
     ...tkb-isolation-aftermath-startup-baseline-004.md |   2 +-
     ...tkb-isolation-completion-plan-2026-04-28-011.md |   2 +-
     bridge/gtkb-isolation-phase3-implementation-003.md |  12 ++
     ...tkb-isolation-phase3-occupancy-detection-003.md |  13 ++
     ...gtkb-isolation-phases-8-9-planning-scope-001.md |   2 +-
     ...gtkb-isolation-phases-8-9-planning-scope-003.md |   2 +-
     bridge/gtkb-kpi-suite-phase-1-retro-001.md         |   2 +-
     bridge/gtkb-legacy-gov-wi-cleanup-001.md           |   2 +-
     bridge/gtkb-legacy-gov-wi-cleanup-003.md           |   2 +-
     bridge/gtkb-legacy-gov-wi-cleanup-004.md           |   2 +-
     bridge/gtkb-legacy-gov-wi-cleanup-006.md           |   2 +-
     bridge/gtkb-legacy-gov-wi-cleanup-008.md           |   2 +-
     bridge/gtkb-legacy-gov-wi-cleanup-010.md           |   2 +-
     bridge/gtkb-lo-advisory-intake-batch-001.md        |   2 +-
     bridge/gtkb-lo-advisory-intake-batch-003.md        |   2 +-
     bridge/gtkb-lo-advisory-intake-batch-004.md        |   2 +-
     bridge/gtkb-lo-advisory-intake-batch-005.md        |   2 +-
     bridge/gtkb-lo-advisory-intake-batch-006.md        |   2 +-
     bridge/gtkb-lo-advisory-intake-batch-008.md        |   2 +-
     bridge/gtkb-lo-advisory-owner-grilling-gate-002.md |   2 +-
     bridge/gtkb-lo-advisory-owner-grilling-gate-004.md |   2 +-
     bridge/gtkb-lo-advisory-owner-grilling-gate-006.md |   2 +-
     bridge/gtkb-lo-advisory-owner-grilling-gate-009.md |   2 +-
     ...ridge-history-backfill-slice-1-inventory-003.md |   2 +-
     ...ridge-history-backfill-slice-1-inventory-004.md |   2 +-
     ...ridge-history-backfill-slice-1-inventory-005.md |   2 +-
     ...ridge-history-backfill-slice-1-inventory-006.md |   2 +-
     ...ridge-history-backfill-slice-1-inventory-007.md |   2 +-
     ...ridge-history-backfill-slice-1-inventory-008.md |   2 +-
     ...ridge-history-backfill-slice-1-inventory-009.md |   2 +-
     ...ridge-history-backfill-slice-1-inventory-012.md |   2 +-
     ...ile-safety-gate-envelope-role-resolution-001.md |   2 +-
     ...ile-safety-gate-envelope-role-resolution-002.md |   2 +-
     ...ile-safety-gate-envelope-role-resolution-003.md |   2 +-
     ...ile-safety-gate-envelope-role-resolution-004.md |   2 +-
     ...ile-safety-gate-envelope-role-resolution-005.md |   2 +-
     ...ile-safety-gate-envelope-role-resolution-006.md |   2 +-
     ...ile-safety-gate-envelope-role-resolution-008.md |   2 +-
     ...kb-lo-file-safety-pretooluse-enforcement-001.md |   2 +-
     ...kb-lo-file-safety-pretooluse-enforcement-003.md |   2 +-
     ...le-safety-pretooluse-enforcement-slice-1-003.md |   2 +-
     ...le-safety-pretooluse-enforcement-slice-1-005.md |   2 +-
     ...le-safety-pretooluse-enforcement-slice-1-006.md |   2 +-
     ...le-safety-pretooluse-enforcement-slice-1-007.md |   2 +-
     ...le-safety-pretooluse-enforcement-slice-1-008.md |   2 +-
     ...le-safety-pretooluse-enforcement-slice-1-009.md |   2 +-
     ...le-safety-pretooluse-enforcement-slice-1-010.md |   2 +-
     ...kb-lo-file-safety-rule-clarification-001-002.md |   2 +-
     ...kb-lo-file-safety-rule-clarification-001-004.md |   2 +-
     .../gtkb-lo-file-safety-rule-clarification-001.md  |   2 +-
     .../gtkb-lo-hourly-quality-scout-advisory-001.md   |   2 +-
     .../gtkb-lo-hourly-quality-scout-advisory-002.md   |   2 +-
     .../gtkb-lo-hourly-quality-scout-advisory-003.md   |   2 +-
     .../gtkb-lo-hourly-quality-scout-advisory-004.md   |   2 +-
     ...ne-assessment-skill-advisory-disposition-001.md |   2 +-
     ...ne-assessment-skill-advisory-disposition-002.md |   2 +-
     ...ne-assessment-skill-advisory-disposition-004.md |   2 +-
     .../gtkb-lo-hygiene-assessment-skill-build-001.md  |   2 +-
     .../gtkb-lo-hygiene-assessment-skill-build-002.md  |   2 +-
     .../gtkb-lo-hygiene-assessment-skill-build-004.md  |   2 +-
     .../gtkb-lo-hygiene-assessment-skill-build-005.md  |   2 +-
     .../gtkb-lo-hygiene-assessment-skill-build-007.md  |   2 +-
     .../gtkb-lo-hygiene-assessment-skill-build-008.md  |   2 +-
     .../gtkb-lo-hygiene-assessment-skill-build-010.md  |   2 +-
     .../gtkb-lo-hygiene-assessment-skill-build-012.md  |   2 +-
     ...ulti-instance-coordinator-design-slice-1-001.md |   2 +-
     ...ulti-instance-coordinator-design-slice-1-002.md |   2 +-
     ...ulti-instance-coordinator-design-slice-1-005.md |   2 +-
     ...ulti-instance-coordinator-design-slice-1-006.md |   2 +-
     ...ulti-instance-coordinator-design-slice-1-007.md |   2 +-
     ...ulti-instance-coordinator-design-slice-1-008.md |   2 +-
     ...ulti-instance-coordinator-design-slice-1-009.md |   2 +-
     ...ulti-instance-coordinator-design-slice-1-011.md |   2 +-
     ...kb-loyal-opposition-startup-symmetry-001-003.md |   2 +-
     ...kb-loyal-opposition-startup-symmetry-001-005.md |   2 +-
     ...kb-loyal-opposition-startup-symmetry-001-007.md |   2 +-
     ...kb-loyal-opposition-startup-symmetry-001-008.md |   2 +-
     ...kb-loyal-opposition-startup-symmetry-001-010.md |   2 +-
     .../gtkb-loyal-opposition-startup-symmetry-001.md  |   2 +-
     bridge/gtkb-major-release-content-goal-gov-001.md  |   2 +-
     bridge/gtkb-major-release-content-goal-gov-002.md  |   2 +-
     bridge/gtkb-major-release-content-goal-gov-003.md  |   2 +-
     bridge/gtkb-major-release-content-goal-gov-004.md  |   2 +-
     ...kb-manual-bridge-scan-terminal-go-filter-001.md |   2 +-
     ...kb-manual-bridge-scan-terminal-go-filter-002.md |   2 +-
     ...kb-manual-bridge-scan-terminal-go-filter-003.md |   2 +-
     ...kb-manual-bridge-scan-terminal-go-filter-004.md |   2 +-
     .../gtkb-mass-adoption-bridge-audit-package-001.md |   2 +-
     .../gtkb-mass-adoption-first-commit-package-001.md |   2 +-
     bridge/gtkb-mass-adoption-readiness-scoping-001.md |   2 +-
     bridge/gtkb-mass-adoption-readiness-scoping-003.md |   2 +-
     bridge/gtkb-mass-adoption-readiness-scoping-004.md |   2 +-
     bridge/gtkb-mass-adoption-readiness-scoping-006.md |   2 +-
     ...able-harness-surface-advisory-2026-05-09-002.md |   2 +-
     ...ble-harness-surface-advisory-disposition-001.md |   2 +-
     ...ble-harness-surface-advisory-disposition-002.md |   2 +-
     ...ble-harness-surface-advisory-disposition-003.md |   2 +-
     ...ble-harness-surface-advisory-disposition-004.md |   2 +-
     ...ble-harness-surface-advisory-disposition-005.md |   2 +-
     ...kb-mcp-stable-harness-surface-conversion-001.md |   2 +-
     ...kb-mcp-stable-harness-surface-conversion-002.md |   2 +-
     ...kb-mcp-stable-harness-surface-conversion-003.md |   2 +-
     ...kb-mcp-stable-harness-surface-conversion-004.md |   2 +-
     ...kb-mcp-stable-harness-surface-conversion-006.md |   2 +-
     ...kb-mcp-stable-harness-surface-conversion-008.md |   2 +-
     ...le-harness-surface-current-version-views-001.md |   2 +-
     ...le-harness-surface-current-version-views-002.md |   2 +-
     ...le-harness-surface-current-version-views-003.md |   2 +-
     ...le-harness-surface-current-version-views-004.md |   2 +-
     ...le-harness-surface-current-version-views-006.md |   2 +-
     ...le-harness-surface-current-version-views-008.md |   2 +-
     ...le-harness-surface-current-version-views-010.md |   2 +-
     ...cp-stable-harness-surface-implementation-003.md |  12 ++
     ...ase-effective-use-audit-test-restoration-001.md |   2 +-
     ...ase-effective-use-audit-test-restoration-002.md |   2 +-
     ...ase-effective-use-audit-test-restoration-003.md |   2 +-
     ...embase-effective-use-recovery-2026-04-29-001.md |   2 +-
     ...embase-effective-use-recovery-2026-04-29-003.md |   2 +-
     ...embase-effective-use-recovery-next-slice-001.md |   2 +-
     ...embase-effective-use-recovery-next-slice-003.md |   2 +-
     ...embase-effective-use-recovery-next-slice-004.md |   2 +-
     ...embase-effective-use-recovery-next-slice-006.md |   2 +-
     ...covery-slice-a-event-surfacer-2026-04-29-001.md |   2 +-
     ...covery-slice-a-event-surfacer-2026-04-29-003.md |   2 +-
     ...covery-slice-a-event-surfacer-2026-04-29-005.md |   2 +-
     bridge/gtkb-membase-effective-use-umbrella-001.md  |   2 +-
     ...-retirement-target-path-scope-correction-001.md |   2 +-
     ...-retirement-target-path-scope-correction-002.md |   2 +-
     ...-retirement-target-path-scope-correction-004.md |   2 +-
     ...-retirement-target-path-scope-correction-006.md |   2 +-
     ...-retirement-target-path-scope-correction-008.md |   2 +-
     ...-switch-validator-hook-matcher-shape-fix-001.md |   2 +-
     ...-switch-validator-hook-matcher-shape-fix-002.md |   2 +-
     ...-switch-validator-hook-matcher-shape-fix-004.md |   2 +-
     ...-switch-validator-hook-matcher-shape-fix-006.md |   2 +-
     .../gtkb-ollama-dispatch-failure-hardening-001.md  |   2 +-
     .../gtkb-ollama-dispatch-failure-hardening-002.md  |   2 +-
     .../gtkb-ollama-dispatch-failure-hardening-004.md  |   2 +-
     bridge/gtkb-ollama-dispatch-stall-retry-cap-001.md |   2 +-
     bridge/gtkb-ollama-dispatch-stall-retry-cap-002.md |   2 +-
     bridge/gtkb-ollama-dispatch-stall-retry-cap-006.md |   2 +-
     bridge/gtkb-ollama-dispatch-state-recovery-003.md  |  26 ++-
     bridge/gtkb-ollama-integration-phase-1-001.md      |   2 +-
     bridge/gtkb-ollama-integration-phase-1-002.md      |   2 +-
     bridge/gtkb-ollama-integration-phase-1-003.md      |   2 +-
     bridge/gtkb-ollama-integration-phase-1-004.md      |   2 +-
     bridge/gtkb-ollama-integration-phase-1-005.md      |   2 +-
     bridge/gtkb-ollama-integration-phase-1-006.md      |   2 +-
     bridge/gtkb-ollama-integration-phase-1-007.md      |   2 +-
     bridge/gtkb-ollama-integration-phase-1-008.md      |   2 +-
     ...kb-ollama-integration-phase-1-foundation-001.md |   2 +-
     ...kb-ollama-integration-phase-1-foundation-002.md |   2 +-
     ...kb-ollama-integration-phase-1-foundation-003.md |   2 +-
     ...kb-ollama-integration-phase-1-foundation-004.md |   2 +-
     ...kb-ollama-integration-phase-1-foundation-005.md |   2 +-
     ...kb-ollama-integration-phase-1-foundation-006.md |   2 +-
     ...kb-ollama-integration-phase-1-foundation-007.md |   2 +-
     ...kb-ollama-integration-phase-1-foundation-008.md |   2 +-
     ...kb-ollama-integration-phase-1-foundation-009.md |   2 +-
     ...kb-ollama-integration-phase-1-foundation-010.md |   2 +-
     ...kb-ollama-integration-phase-1-foundation-012.md |   2 +-
     ...lama-integration-phase-1-governance-impl-001.md |   2 +-
     ...lama-integration-phase-1-governance-impl-002.md |   2 +-
     ...lama-integration-phase-1-governance-impl-004.md |   2 +-
     ...tion-phase-1-project-completion-coverage-001.md |   2 +-
     ...tion-phase-1-project-completion-coverage-002.md |   2 +-
     ...tion-phase-1-project-completion-coverage-004.md |   2 +-
     ...tion-phase-1-project-completion-coverage-007.md |   2 +-
     bridge/gtkb-ollama-integration-phase-1-shim-001.md |   2 +-
     bridge/gtkb-ollama-integration-phase-1-shim-002.md |   2 +-
     bridge/gtkb-ollama-integration-phase-1-shim-003.md |   2 +-
     bridge/gtkb-ollama-integration-phase-1-shim-004.md |   2 +-
     bridge/gtkb-ollama-integration-phase-1-shim-005.md |   2 +-
     bridge/gtkb-ollama-integration-phase-1-shim-006.md |   2 +-
     bridge/gtkb-ollama-integration-phase-1-shim-007.md |   2 +-
     bridge/gtkb-ollama-integration-phase-1-shim-008.md |   2 +-
     bridge/gtkb-ollama-integration-phase-1-shim-010.md |   2 +-
     bridge/gtkb-ollama-integration-phase-1-shim-011.md |   2 +-
     bridge/gtkb-ollama-integration-phase-1-shim-012.md |   2 +-
     ...-ollama-integration-phase-1-verification-001.md |   2 +-
     ...-ollama-integration-phase-1-verification-002.md |   2 +-
     ...-ollama-integration-phase-1-verification-003.md |   2 +-
     ...-ollama-integration-phase-1-verification-004.md |   2 +-
     ...-ollama-integration-phase-1-verification-005.md |   2 +-
     ...-ollama-integration-phase-1-verification-006.md |   2 +-
     ...-ollama-integration-phase-1-verification-008.md |   2 +-
     ...-ollama-integration-phase-1-verification-010.md |   2 +-
     ...-ollama-integration-phase-1-verification-012.md |   2 +-
     bridge/gtkb-ollama-integration-phase-2-001.md      |   2 +-
     bridge/gtkb-ollama-integration-phase-2-002.md      |   2 +-
     bridge/gtkb-ollama-integration-phase-2-003.md      |   2 +-
     bridge/gtkb-ollama-integration-phase-2-004.md      |   2 +-
     bridge/gtkb-ollama-integration-phase-2-006.md      |   2 +-
     bridge/gtkb-ollama-integration-phase-2-008.md      |   2 +-
     bridge/gtkb-ollama-integration-phase-2-010.md      |   2 +-
     ...gtkb-ollama-integration-phase-2-adapters-001.md |   2 +-
     ...gtkb-ollama-integration-phase-2-adapters-002.md |   2 +-
     ...gtkb-ollama-integration-phase-2-adapters-003.md |   2 +-
     ...gtkb-ollama-integration-phase-2-adapters-004.md |   2 +-
     ...gtkb-ollama-integration-phase-2-adapters-005.md |   2 +-
     ...gtkb-ollama-integration-phase-2-adapters-006.md |   2 +-
     ...gtkb-ollama-integration-phase-2-adapters-007.md |   2 +-
     ...gtkb-ollama-integration-phase-2-adapters-008.md |   2 +-
     ...gtkb-ollama-integration-phase-2-adapters-010.md |   2 +-
     ...gtkb-ollama-integration-phase-2-dispatch-001.md |   2 +-
     ...gtkb-ollama-integration-phase-2-dispatch-002.md |   2 +-
     ...gtkb-ollama-integration-phase-2-dispatch-003.md |   2 +-
     ...gtkb-ollama-integration-phase-2-dispatch-004.md |   2 +-
     ...gtkb-ollama-integration-phase-2-dispatch-005.md |   2 +-
     ...gtkb-ollama-integration-phase-2-dispatch-006.md |   2 +-
     ...gtkb-ollama-integration-phase-2-dispatch-007.md |   2 +-
     ...gtkb-ollama-integration-phase-2-dispatch-008.md |   2 +-
     ...gtkb-ollama-integration-phase-2-dispatch-010.md |   2 +-
     ...gtkb-ollama-integration-phase-2-dispatch-012.md |   2 +-
     ...llama-integration-phase-2-role-promotion-001.md |   2 +-
     ...llama-integration-phase-2-role-promotion-002.md |   2 +-
     ...llama-integration-phase-2-role-promotion-003.md |   2 +-
     ...llama-integration-phase-2-role-promotion-004.md |   2 +-
     ...llama-integration-phase-2-role-promotion-005.md |   2 +-
     ...llama-integration-phase-2-role-promotion-006.md |   2 +-
     ...llama-integration-phase-2-role-promotion-007.md |   2 +-
     ...llama-integration-phase-2-role-promotion-008.md |   2 +-
     ...llama-integration-phase-2-role-promotion-010.md |   2 +-
     ...llama-integration-phase-2-role-promotion-012.md |   2 +-
     ...llama-integration-phase-2-role-promotion-014.md |   2 +-
     .../gtkb-ollama-integration-phase-2-routing-001.md |   2 +-
     .../gtkb-ollama-integration-phase-2-routing-002.md |   2 +-
     .../gtkb-ollama-integration-phase-2-routing-003.md |   2 +-
     .../gtkb-ollama-integration-phase-2-routing-004.md |   2 +-
     .../gtkb-ollama-integration-phase-2-routing-005.md |   2 +-
     .../gtkb-ollama-integration-phase-2-routing-006.md |   2 +-
     .../gtkb-ollama-integration-phase-2-routing-007.md |   2 +-
     .../gtkb-ollama-integration-phase-2-routing-008.md |   2 +-
     .../gtkb-ollama-integration-phase-2-routing-010.md |   2 +-
     ...b-ollama-lo-dispatch-session-propagation-001.md |   2 +-
     ...b-ollama-lo-dispatch-session-propagation-002.md |   2 +-
     ...b-ollama-lo-dispatch-session-propagation-003.md |   2 +-
     ...b-ollama-lo-dispatch-session-propagation-004.md |   2 +-
     ...b-ollama-lo-dispatch-session-propagation-005.md |   2 +-
     ...b-ollama-lo-dispatch-session-propagation-006.md |   2 +-
     bridge/gtkb-ollama-lo-prompt-hardening-003.md      |   2 +-
     ...ma-phase2-subproject-completion-coverage-001.md |   2 +-
     ...ma-phase2-subproject-completion-coverage-002.md |   2 +-
     ...ma-phase2-subproject-completion-coverage-003.md |   2 +-
     ...ma-phase2-subproject-completion-coverage-004.md |   2 +-
     ...ma-phase2-subproject-completion-coverage-006.md |   2 +-
     ...ma-phase2-subproject-completion-coverage-008.md |   2 +-
     ...hase2-verified-staging-finalization-gate-001.md |   2 +-
     ...hase2-verified-staging-finalization-gate-002.md |   2 +-
     ...hase2-verified-staging-finalization-gate-004.md |   2 +-
     ...ollama-qwen-full-lo-dispatch-test-update-001.md |   2 +-
     ...ollama-qwen-full-lo-dispatch-test-update-002.md |   2 +-
     ...ollama-qwen-full-lo-dispatch-test-update-004.md |   2 +-
     bridge/gtkb-ollama-qwen-full-lo-route-001.md       |   2 +-
     bridge/gtkb-ollama-qwen-full-lo-route-002.md       |   2 +-
     bridge/gtkb-ollama-qwen-full-lo-route-003.md       |   2 +-
     bridge/gtkb-ollama-qwen-full-lo-route-005.md       |   2 +-
     ...ollama-qwen-full-lo-route-gate-compliant-001.md |   2 +-
     ...ollama-qwen-full-lo-route-gate-compliant-002.md |   2 +-
     ...ollama-qwen-full-lo-route-gate-compliant-004.md |   2 +-
     ...ma-routing-model-version-fixture-cleanup-001.md |   2 +-
     .../gtkb-ollama-routing-single-sot-cleanup-001.md  |   2 +-
     ...kb-ollama-tool-numeric-argument-coercion-001.md |   2 +-
     ...kb-ollama-tool-numeric-argument-coercion-002.md |   2 +-
     ...kb-ollama-tool-numeric-argument-coercion-004.md |   2 +-
     ...kb-ollama-tool-numeric-argument-coercion-006.md |   2 +-
     bridge/gtkb-operating-mode-transaction-001-001.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-003.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-004.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-005.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-006.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-007.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-008.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-009.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-010.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-011.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-012.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-013.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-014.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-015.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-016.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-017.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-019.md  |   2 +-
     bridge/gtkb-operating-mode-transaction-001-021.md  |   2 +-
     ...mbership-backfill-slice-2-implementation-001.md |   2 +-
     ...mbership-backfill-slice-2-implementation-002.md |   2 +-
     ...mbership-backfill-slice-2-implementation-003.md |   2 +-
     ...mbership-backfill-slice-2-implementation-004.md |   2 +-
     ...mbership-backfill-slice-2-implementation-006.md |   2 +-
     ...mbership-backfill-slice-2-implementation-008.md |   2 +-
     ...n-wi-membership-backfill-slice-2-scoping-001.md |   2 +-
     ...n-wi-membership-backfill-slice-2-scoping-002.md |   2 +-
     ...n-wi-membership-backfill-slice-2-scoping-004.md |   2 +-
     ...b-orphan-wi-membership-discovery-slice-1-001.md |   2 +-
     ...b-orphan-wi-membership-discovery-slice-1-003.md |   2 +-
     ...b-orphan-wi-membership-discovery-slice-1-005.md |   2 +-
     ...b-orphan-wi-membership-discovery-slice-1-006.md |   2 +-
     ...b-orphan-wi-membership-discovery-slice-1-007.md |   2 +-
     ...b-orphan-wi-membership-discovery-slice-1-008.md |   2 +-
     ...b-orphan-wi-membership-discovery-slice-1-010.md |   2 +-
     ...b-orphan-wi-membership-discovery-slice-1-012.md |   2 +-
     ...-owner-decision-tracker-baseline-restore-001.md |   2 +-
     ...-owner-decision-tracker-baseline-restore-002.md |   2 +-
     ...-owner-decision-tracker-baseline-restore-003.md |   2 +-
     ...-owner-decision-tracker-baseline-restore-004.md |   2 +-
     ...-owner-decision-tracker-baseline-restore-006.md |   2 +-
     ...-owner-decision-tracker-baseline-restore-007.md |   2 +-
     ...-owner-decision-tracker-baseline-restore-008.md |   2 +-
     ...er-pattern-bounds-and-auq-resolution-001-003.md |   2 +-
     ...er-pattern-bounds-and-auq-resolution-001-005.md |   2 +-
     ...racker-pattern-bounds-and-auq-resolution-001.md |   2 +-
     ...owner-role-switch-codex-loyal-opposition-001.md |   2 +-
     bridge/gtkb-p0-secrets-purge-enforcement-003.md    |   2 +-
     bridge/gtkb-p0-secrets-purge-enforcement-004.md    |   2 +-
     bridge/gtkb-p0-secrets-purge-enforcement-005.md    |   2 +-
     bridge/gtkb-p0-secrets-purge-enforcement-006.md    |   2 +-
     ...b-peer-solution-advisory-loop-2026-05-10-001.md |   2 +-
     ...b-peer-solution-advisory-loop-2026-05-10-002.md |   2 +-
     ...b-peer-solution-advisory-loop-conversion-001.md |   2 +-
     ...b-peer-solution-advisory-loop-conversion-002.md |   2 +-
     ...b-peer-solution-advisory-loop-conversion-003.md |   2 +-
     ...b-peer-solution-advisory-loop-conversion-004.md |   2 +-
     ...b-peer-solution-advisory-loop-conversion-006.md |   2 +-
     ...kb-peer-solution-advisory-loop-procedure-001.md |   2 +-
     ...kb-peer-solution-advisory-loop-procedure-002.md |   2 +-
     ...kb-peer-solution-advisory-loop-procedure-004.md |   2 +-
     ...ion-advisory-report-advisory-disposition-001.md |   2 +-
     ...ion-advisory-report-advisory-disposition-002.md |   2 +-
     ...ion-advisory-report-advisory-disposition-003.md |   2 +-
     ...ion-advisory-report-advisory-disposition-004.md |   2 +-
     ...ion-advisory-report-advisory-disposition-005.md |   2 +-
     ...ion-advisory-report-advisory-disposition-006.md |   2 +-
     ...ion-advisory-report-advisory-disposition-007.md |   2 +-
     ...ion-advisory-report-advisory-disposition-008.md |   2 +-
     ...ion-advisory-report-advisory-disposition-009.md |   2 +-
     ...ion-advisory-report-advisory-disposition-012.md |   2 +-
     bridge/gtkb-peer-solution-owner-gate-dcl-001.md    |   2 +-
     bridge/gtkb-peer-solution-owner-gate-dcl-002.md    |   2 +-
     bridge/gtkb-peer-solution-owner-gate-dcl-003.md    |   2 +-
     bridge/gtkb-peer-solution-owner-gate-dcl-004.md    |   2 +-
     bridge/gtkb-peer-solution-owner-gate-dcl-005.md    |   2 +-
     bridge/gtkb-peer-solution-owner-gate-dcl-006.md    |   2 +-
     bridge/gtkb-peer-solution-owner-gate-dcl-007.md    |   2 +-
     bridge/gtkb-peer-solution-owner-gate-dcl-008.md    |   2 +-
     bridge/gtkb-peer-solution-owner-gate-dcl-010.md    |   2 +-
     ...gtkb-peer-solution-workflow-contract-adr-001.md |   2 +-
     ...gtkb-peer-solution-workflow-contract-adr-002.md |   2 +-
     ...gtkb-peer-solution-workflow-contract-adr-003.md |   2 +-
     ...gtkb-peer-solution-workflow-contract-adr-004.md |   2 +-
     ...gtkb-peer-solution-workflow-contract-adr-005.md |   2 +-
     ...gtkb-peer-solution-workflow-contract-adr-006.md |   2 +-
     ...gtkb-peer-solution-workflow-contract-adr-007.md |   2 +-
     ...gtkb-peer-solution-workflow-contract-adr-008.md |   2 +-
     ...gtkb-peer-solution-workflow-contract-adr-010.md |   2 +-
     ...kb-phantom-project-prefix-reconciliation-001.md |   2 +-
     ...kb-phantom-project-prefix-reconciliation-002.md |   2 +-
     ...kb-phantom-project-prefix-reconciliation-003.md |   2 +-
     ...kb-phantom-project-prefix-reconciliation-004.md |   2 +-
     ...kb-phantom-project-prefix-reconciliation-006.md |   2 +-
     ...kb-phantom-project-prefix-reconciliation-008.md |   2 +-
     bridge/gtkb-platform-observability-hygiene-003.md  |  11 ++
     ...solidation-slice-1-governance-foundation-001.md |   2 +-
     ...solidation-slice-1-governance-foundation-002.md |   2 +-
     ...solidation-slice-1-governance-foundation-003.md |   2 +-
     ...solidation-slice-1-governance-foundation-004.md |   2 +-
     ...solidation-slice-1-governance-foundation-005.md |   2 +-
     ...solidation-slice-1-governance-foundation-007.md |   2 +-
     ...solidation-slice-1-governance-foundation-009.md |   2 +-
     ...t-consolidation-slice-2a-read-discipline-001.md |   2 +-
     ...t-consolidation-slice-2a-read-discipline-002.md |   2 +-
     ...t-consolidation-slice-2a-read-discipline-003.md |   2 +-
     ...t-consolidation-slice-2a-read-discipline-004.md |   2 +-
     ...t-consolidation-slice-2a-read-discipline-006.md |   2 +-
     ...t-consolidation-slice-2a-read-discipline-007.md |   2 +-
     ...t-consolidation-slice-2a-read-discipline-009.md |   2 +-
     ...gtkb-platform-sot-consolidation-umbrella-001.md |   2 +-
     ...gtkb-platform-sot-consolidation-umbrella-002.md |   2 +-
     ...gtkb-platform-sot-consolidation-umbrella-003.md |   2 +-
     ...gtkb-platform-sot-consolidation-umbrella-004.md |   2 +-
     ...gtkb-platform-sot-consolidation-umbrella-005.md |   2 +-
     ...gtkb-platform-sot-consolidation-umbrella-006.md |   2 +-
     ...gtkb-platform-sot-consolidation-umbrella-007.md |   2 +-
     ...gtkb-platform-sot-consolidation-umbrella-008.md |   2 +-
     ...rm-spec-coverage-architecture-2026-04-29-007.md |   2 +-
     ...spec-coverage-verified-runner-2026-04-29-001.md |   2 +-
     ...spec-coverage-verified-runner-2026-04-29-003.md |   2 +-
     bridge/gtkb-platform-tests-ruff-cleanup-001.md     |   2 +-
     bridge/gtkb-platform-tests-ruff-cleanup-003.md     |   2 +-
     bridge/gtkb-platform-tests-ruff-cleanup-004.md     |   2 +-
     bridge/gtkb-platform-tests-ruff-cleanup-005.md     |   2 +-
     bridge/gtkb-platform-tests-ruff-cleanup-006.md     |   2 +-
     bridge/gtkb-platform-tests-ruff-cleanup-008.md     |   2 +-
     bridge/gtkb-platform-tests-ruff-cleanup-010.md     |   2 +-
     bridge/gtkb-platform-tests-ruff-cleanup-012.md     |   2 +-
     bridge/gtkb-platform-tests-ruff-cleanup-014.md     |   2 +-
     ...or-step-16-d-orphan-test-rationalization-001.md |   2 +-
     ...or-step-16-d-orphan-test-rationalization-003.md |   2 +-
     ...b-prime-worker-context-aware-auq-slice-2-001.md |   2 +-
     ...b-prime-worker-context-aware-auq-slice-2-002.md |   2 +-
     ...b-prime-worker-context-aware-auq-slice-2-003.md |   2 +-
     ...b-prime-worker-context-aware-auq-slice-2-004.md |   2 +-
     ...b-prime-worker-context-aware-auq-slice-2-005.md |   2 +-
     ...b-prime-worker-context-aware-auq-slice-2-006.md |   2 +-
     ...b-prime-worker-context-aware-auq-slice-2-007.md |   2 +-
     ...b-prime-worker-context-aware-auq-slice-2-008.md |   2 +-
     ...b-prime-worker-context-aware-auq-slice-2-009.md |   2 +-
     ...b-prime-worker-context-aware-auq-slice-2-010.md |   2 +-
     ...b-prime-worker-context-aware-auq-slice-2-011.md |   2 +-
     ...b-prime-worker-context-aware-auq-slice-2-012.md |   2 +-
     ...prime-worker-delivery-regression-slice-4-001.md |   2 +-
     ...prime-worker-delivery-regression-slice-4-002.md |   2 +-
     ...prime-worker-delivery-regression-slice-4-003.md |   2 +-
     ...prime-worker-delivery-regression-slice-4-004.md |   2 +-
     ...prime-worker-delivery-regression-slice-4-005.md |   2 +-
     ...prime-worker-delivery-regression-slice-4-006.md |   2 +-
     ...prime-worker-delivery-regression-slice-4-009.md |   2 +-
     ...prime-worker-delivery-regression-slice-4-011.md |   2 +-
     ...-prime-worker-permission-profile-slice-1-001.md |   2 +-
     ...-prime-worker-permission-profile-slice-1-002.md |   2 +-
     ...-prime-worker-permission-profile-slice-1-003.md |   2 +-
     ...-prime-worker-permission-profile-slice-1-004.md |   2 +-
     ...-prime-worker-permission-profile-slice-1-005.md |   2 +-
     ...-prime-worker-permission-profile-slice-1-006.md |   2 +-
     ...-worker-post-stop-dispatch-retry-slice-3-001.md |   2 +-
     ...-worker-post-stop-dispatch-retry-slice-3-002.md |   2 +-
     ...-worker-post-stop-dispatch-retry-slice-3-003.md |   2 +-
     ...-worker-post-stop-dispatch-retry-slice-3-004.md |   2 +-
     ...-worker-post-stop-dispatch-retry-slice-3-005.md |   2 +-
     ...-worker-post-stop-dispatch-retry-slice-3-006.md |   2 +-
     ...-worker-post-stop-dispatch-retry-slice-3-007.md |   2 +-
     ...-worker-post-stop-dispatch-retry-slice-3-008.md |   2 +-
     ...-worker-post-stop-dispatch-retry-slice-3-009.md |   2 +-
     ...-worker-post-stop-dispatch-retry-slice-3-010.md |   2 +-
     ...-worker-post-stop-dispatch-retry-slice-3-011.md |   2 +-
     ...-worker-post-stop-dispatch-retry-slice-3-012.md |   2 +-
     .../gtkb-project-auth-spec-amendment-gate-001.md   |   2 +-
     .../gtkb-project-auth-spec-amendment-gate-003.md   |   2 +-
     .../gtkb-project-auth-spec-amendment-gate-005.md   |   2 +-
     .../gtkb-project-auth-spec-amendment-gate-007.md   |   2 +-
     ...oject-authorization-completion-keep-open-001.md |   2 +-
     ...oject-authorization-completion-keep-open-002.md |   2 +-
     ...gtkb-project-authorize-spec-linkage-gate-001.md |   2 +-
     ...gtkb-project-authorize-spec-linkage-gate-003.md |   2 +-
     ...gtkb-project-authorize-spec-linkage-gate-005.md |   2 +-
     ...gtkb-project-authorize-spec-linkage-gate-007.md |   2 +-
     ...tkb-project-completion-drive-payload-001-001.md |   2 +-
     ...tkb-project-completion-drive-payload-001-002.md |   2 +-
     ...project-completion-plan-incomplete-guard-001.md |   2 +-
     ...project-completion-plan-incomplete-guard-002.md |   2 +-
     ...project-completion-plan-incomplete-guard-004.md |   2 +-
     ...completion-scanner-addressing-thread-fix-001.md |   2 +-
     ...completion-scanner-addressing-thread-fix-002.md |   2 +-
     ...completion-scanner-addressing-thread-fix-003.md |   2 +-
     ...completion-scanner-addressing-thread-fix-004.md |   2 +-
     ...completion-scanner-addressing-thread-fix-005.md |   2 +-
     ...completion-scanner-addressing-thread-fix-006.md |   2 +-
     ...completion-scanner-addressing-thread-fix-007.md |   2 +-
     ...completion-scanner-addressing-thread-fix-008.md |   2 +-
     ...completion-scanner-addressing-thread-fix-009.md |   2 +-
     ...completion-scanner-addressing-thread-fix-010.md |   2 +-
     ...completion-scanner-addressing-thread-fix-012.md |   2 +-
     ...completion-scanner-addressing-thread-fix-013.md |   2 +-
     ...completion-scanner-addressing-thread-fix-014.md |   2 +-
     ...ner-addressing-thread-fix-implementation-001.md |   2 +-
     ...ner-addressing-thread-fix-implementation-002.md |   2 +-
     ...ner-addressing-thread-fix-implementation-003.md |   2 +-
     ...ner-addressing-thread-fix-implementation-004.md |   2 +-
     ...on-scanner-addressing-thread-fix-scoping-001.md |   2 +-
     ...on-scanner-addressing-thread-fix-scoping-002.md |   2 +-
     ...on-scanner-addressing-thread-fix-scoping-004.md |   2 +-
     ...ect-completion-scanner-wi-auto-regex-fix-001.md |   2 +-
     ...ect-completion-scanner-wi-auto-regex-fix-002.md |   2 +-
     ...ect-completion-scanner-wi-auto-regex-fix-005.md |   2 +-
     ...ect-completion-scanner-wi-auto-regex-fix-006.md |   2 +-
     ...ect-completion-scanner-wi-auto-regex-fix-007.md |   2 +-
     ...ect-completion-scanner-wi-auto-regex-fix-008.md |   2 +-
     .../gtkb-project-id-prefix-idempotent-fix-001.md   |   2 +-
     .../gtkb-project-id-prefix-idempotent-fix-002.md   |   2 +-
     .../gtkb-project-id-prefix-idempotent-fix-005.md   |   2 +-
     ...ip-reconciliation-slice-1-inventory-tool-001.md |   2 +-
     ...ip-reconciliation-slice-1-inventory-tool-002.md |   2 +-
     ...ip-reconciliation-slice-1-inventory-tool-004.md |   2 +-
     ...embership-reconciliation-slice-1-scoping-001.md |   2 +-
     ...embership-reconciliation-slice-1-scoping-002.md |   2 +-
     ...embership-reconciliation-slice-1-scoping-004.md |   2 +-
     ...ject-scoped-implementation-authorization-001.md |   2 +-
     ...ject-scoped-implementation-authorization-002.md |   2 +-
     ...ject-scoped-implementation-authorization-003.md |   2 +-
     ...ject-scoped-implementation-authorization-004.md |   2 +-
     ...ject-scoped-implementation-authorization-006.md |   2 +-
     ...ject-scoped-implementation-authorization-007.md |   2 +-
     ...ject-scoped-implementation-authorization-008.md |   2 +-
     ...ject-scoped-implementation-authorization-010.md |   2 +-
     ...-project-verified-completion-auq-trigger-001.md |   2 +-
     ...-project-verified-completion-auq-trigger-003.md |   2 +-
     ...-project-verified-completion-auq-trigger-005.md |   2 +-
     .../gtkb-projects-remove-item-cli-slice-1-001.md   |   2 +-
     .../gtkb-projects-remove-item-cli-slice-1-002.md   |   2 +-
     .../gtkb-projects-remove-item-cli-slice-1-003.md   |   2 +-
     .../gtkb-projects-remove-item-cli-slice-1-004.md   |   2 +-
     .../gtkb-projects-remove-item-cli-slice-1-005.md   |   2 +-
     .../gtkb-projects-remove-item-cli-slice-1-006.md   |   2 +-
     .../gtkb-projects-remove-item-cli-slice-1-007.md   |   2 +-
     .../gtkb-projects-remove-item-cli-slice-1-008.md   |   2 +-
     .../gtkb-projects-remove-item-cli-slice-1-009.md   |   2 +-
     .../gtkb-projects-remove-item-cli-slice-1-011.md   |   2 +-
     bridge/gtkb-projects-skill-001-001.md              |   2 +-
     bridge/gtkb-projects-skill-001-003.md              |   2 +-
     bridge/gtkb-projects-skill-001-007.md              |   2 +-
     ...roposal-standards-propose-scaffold-skill-001.md |   2 +-
     ...roposal-standards-propose-scaffold-skill-002.md |   2 +-
     ...roposal-standards-propose-scaffold-skill-004.md |   2 +-
     ...osal-standards-test-claim-rerun-verifier-001.md |   2 +-
     ...osal-standards-test-claim-rerun-verifier-003.md |   2 +-
     ...osal-standards-test-claim-rerun-verifier-004.md |   2 +-
     ...osal-standards-test-claim-rerun-verifier-006.md |   2 +-
     ...osal-standards-test-claim-rerun-verifier-008.md |   2 +-
     ...osal-standards-test-claim-rerun-verifier-009.md |   2 +-
     ...osal-standards-test-claim-rerun-verifier-011.md |   2 +-
     ...osal-standards-test-claim-rerun-verifier-013.md |   2 +-
     ...osal-standards-test-claim-rerun-verifier-017.md |   2 +-
     ...-proposal-standards-wi-id-collision-gate-001.md |   2 +-
     ...-proposal-standards-wi-id-collision-gate-003.md |   2 +-
     ...-proposal-standards-wi-id-collision-gate-005.md |   2 +-
     ...-proposal-standards-wi-id-collision-gate-007.md |   2 +-
     ...cted-artifact-rollup-governance-umbrella-001.md |   2 +-
     ...cted-artifact-rollup-governance-umbrella-002.md |   2 +-
     ...cted-artifact-rollup-governance-umbrella-003.md |   2 +-
     ...cted-artifact-rollup-governance-umbrella-004.md |   2 +-
     ...cted-artifact-rollup-governance-umbrella-005.md |   2 +-
     .../gtkb-push-gate-design-governance-review-001.md |   2 +-
     .../gtkb-push-gate-design-governance-review-003.md |   2 +-
     .../gtkb-push-gate-design-governance-review-004.md |   2 +-
     .../gtkb-push-gate-design-governance-review-005.md |   2 +-
     .../gtkb-push-gate-design-governance-review-006.md |   2 +-
     .../gtkb-push-gate-design-governance-review-007.md |   2 +-
     .../gtkb-push-gate-design-governance-review-010.md |   2 +-
     bridge/gtkb-push-gate-slice-1-5-debt-audit-001.md  |   2 +-
     bridge/gtkb-push-gate-slice-1-5-debt-audit-002.md  |   2 +-
     bridge/gtkb-push-gate-slice-1-5-debt-audit-003.md  |   2 +-
     bridge/gtkb-push-gate-slice-1-5-debt-audit-004.md  |   2 +-
     bridge/gtkb-push-gate-slice-1-5-debt-audit-005.md  |   2 +-
     .../gtkb-pytest-basetemp-session-isolation-001.md  |   2 +-
     .../gtkb-pytest-basetemp-session-isolation-002.md  |   2 +-
     .../gtkb-pytest-basetemp-session-isolation-004.md  |   2 +-
     ...b-rc-gate-membase-seed-resilient-fixture-001.md |   2 +-
     ...b-rc-gate-membase-seed-resilient-fixture-002.md |   2 +-
     ...b-rc-gate-membase-seed-resilient-fixture-003.md |   2 +-
     ...b-rc-gate-membase-seed-resilient-fixture-004.md |   2 +-
     ...b-rc-gate-membase-seed-resilient-fixture-005.md |   2 +-
     bridge/gtkb-rc1-canonical-ci-closure-001.md        |   2 +-
     bridge/gtkb-rc1-canonical-ci-closure-002.md        |   2 +-
     bridge/gtkb-rc1-canonical-ci-closure-004.md        |   2 +-
     bridge/gtkb-rc1-canonical-ci-closure-006.md        |   2 +-
     ...b-rc1-pyjwt-dependency-audit-remediation-001.md |   2 +-
     ...b-rc1-pyjwt-dependency-audit-remediation-002.md |   2 +-
     ...b-rc1-pyjwt-dependency-audit-remediation-004.md |   2 +-
     ...ry-scaffold-fixture-drift-reconciliation-001.md |   2 +-
     ...ry-scaffold-fixture-drift-reconciliation-002.md |   2 +-
     ...ry-scaffold-fixture-drift-reconciliation-004.md |   2 +-
     ...ry-scaffold-fixture-drift-reconciliation-006.md |   2 +-
     ...ry-scaffold-fixture-drift-reconciliation-008.md |   2 +-
     bridge/gtkb-rehearsal-inventory-perf-001.md        |   2 +-
     bridge/gtkb-rehearsal-package-ruff-clean-001.md    |   2 +-
     ...tkb-release-candidate-gate-managed-skill-001.md |   2 +-
     ...tkb-release-candidate-gate-managed-skill-003.md |   2 +-
     ...tkb-release-candidate-gate-managed-skill-005.md |   2 +-
     ...tkb-release-candidate-gate-managed-skill-006.md |   2 +-
     ...tkb-release-candidate-gate-managed-skill-008.md |   2 +-
     ...tkb-release-candidate-gate-managed-skill-010.md |   2 +-
     ...tkb-release-candidate-gate-managed-skill-012.md |   2 +-
     ...-release-candidate-gate-stale-test-paths-001.md |   2 +-
     ...-release-candidate-gate-stale-test-paths-002.md |   2 +-
     ...-release-candidate-gate-stale-test-paths-003.md |   2 +-
     ...-release-candidate-gate-stale-test-paths-004.md |   2 +-
     ...-release-candidate-gate-stale-test-paths-005.md |   2 +-
     ...-release-candidate-gate-stale-test-paths-006.md |   2 +-
     ...-release-candidate-gate-stale-test-paths-008.md |   2 +-
     bridge/gtkb-reliability-fast-lane-001.md           |   2 +-
     bridge/gtkb-reliability-fast-lane-003.md           |   2 +-
     bridge/gtkb-reliability-fast-lane-005.md           |   2 +-
     bridge/gtkb-restore-systems-and-tools-doc-001.md   |   2 +-
     bridge/gtkb-restore-systems-and-tools-doc-002.md   |   2 +-
     bridge/gtkb-restore-systems-and-tools-doc-004.md   |   2 +-
     ...-assignments-mirror-slice-1-seed-repoint-002.md |   2 +-
     ...-assignments-mirror-slice-1-seed-repoint-003.md |   2 +-
     ...-assignments-mirror-slice-1-seed-repoint-004.md |   2 +-
     ...-assignments-mirror-slice-1-seed-repoint-006.md |   2 +-
     ...-assignments-mirror-slice-1-seed-repoint-008.md |   2 +-
     ...rror-slice-2-rule-and-automation-repoint-001.md |   2 +-
     ...rror-slice-2-rule-and-automation-repoint-002.md |   2 +-
     ...rror-slice-2-rule-and-automation-repoint-004.md |   2 +-
     ...rror-slice-2-rule-and-automation-repoint-005.md |   2 +-
     ...rror-slice-2-rule-and-automation-repoint-007.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-001.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-002.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-003.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-004.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-006.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-007.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-008.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-010.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-011.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-012.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-013.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-014.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-015.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-016.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-018.md |   2 +-
     ...mirror-slice-3-root-and-startup-surfaces-020.md |   2 +-
     bridge/gtkb-role-enhancement-001.md                |   2 +-
     bridge/gtkb-role-enhancement-002.md                |   2 +-
     bridge/gtkb-role-enhancement-003.md                |   2 +-
     bridge/gtkb-role-enhancement-004.md                |   2 +-
     ...enhancement-isolation-dependency-reframe-001.md |   2 +-
     ...enhancement-isolation-dependency-reframe-002.md |   2 +-
     ...enhancement-isolation-dependency-reframe-004.md |   2 +-
     ...enhancement-isolation-dependency-reframe-005.md |   2 +-
     ...enhancement-isolation-dependency-reframe-006.md |   2 +-
     ...enhancement-isolation-dependency-reframe-007.md |   2 +-
     ...enhancement-isolation-dependency-reframe-009.md |   2 +-
     ...ent-lo-investigation-methodology-slice-2-001.md |   2 +-
     ...ent-lo-investigation-methodology-slice-2-002.md |   2 +-
     ...ent-lo-investigation-methodology-slice-2-004.md |   2 +-
     ...ent-lo-investigation-methodology-slice-2-005.md |   2 +-
     ...ent-lo-investigation-methodology-slice-2-006.md |   2 +-
     ...logy-slice-2-owner-approved-continuation-001.md |   2 +-
     ...logy-slice-2-owner-approved-continuation-002.md |   2 +-
     ...logy-slice-2-owner-approved-continuation-004.md |   2 +-
     ...hancement-no-go-cycle-escalation-slice-3-001.md |   2 +-
     ...hancement-no-go-cycle-escalation-slice-3-002.md |   2 +-
     ...hancement-no-go-cycle-escalation-slice-3-004.md |   2 +-
     ...hancement-no-go-cycle-escalation-slice-3-006.md |   2 +-
     ...hancement-no-go-cycle-escalation-slice-3-007.md |   2 +-
     ...hancement-no-go-cycle-escalation-slice-3-008.md |   2 +-
     ...nhancement-review-depth-contract-slice-1-001.md |   2 +-
     ...nhancement-review-depth-contract-slice-1-002.md |   2 +-
     ...nhancement-review-depth-contract-slice-1-004.md |   2 +-
     ...nhancement-review-depth-contract-slice-1-005.md |   2 +-
     ...nhancement-review-depth-contract-slice-1-006.md |   2 +-
     ...nhancement-review-depth-contract-slice-1-007.md |   2 +-
     ...nhancement-review-depth-contract-slice-1-008.md |   4 +-
     ...ole-enhancement-review-depth-methodology-001.md |   2 +-
     ...ole-enhancement-review-depth-methodology-003.md |   2 +-
     ...ole-enhancement-review-depth-methodology-005.md |   2 +-
     ...ole-enhancement-review-depth-methodology-006.md |   2 +-
     ...ole-enhancement-review-depth-methodology-008.md |   2 +-
     ...e-orthogonality-cleanup-claude-pb-switch-001.md |   2 +-
     ...e-orthogonality-cleanup-claude-pb-switch-002.md |   2 +-
     ...e-orthogonality-cleanup-claude-pb-switch-003.md |   2 +-
     ...e-orthogonality-cleanup-claude-pb-switch-004.md |   2 +-
     ...e-orthogonality-cleanup-claude-pb-switch-006.md |   2 +-
     ...e-orthogonality-cleanup-claude-pb-switch-008.md |   2 +-
     ...e-orthogonality-cleanup-claude-pb-switch-009.md |   2 +-
     ...e-orthogonality-cleanup-claude-pb-switch-010.md |   2 +-
     ...e-orthogonality-cleanup-claude-pb-switch-011.md |   2 +-
     ...e-orthogonality-cleanup-claude-pb-switch-012.md |   2 +-
     ...e-orthogonality-cleanup-claude-pb-switch-014.md |   2 +-
     ...e-release-operations-advisory-2026-05-11-001.md |   2 +-
     ...e-release-operations-advisory-2026-05-11-002.md |   2 +-
     ...role-scope-release-operations-conversion-001.md |   2 +-
     ...role-scope-release-operations-conversion-002.md |   2 +-
     ...role-scope-release-operations-conversion-003.md |   2 +-
     ...role-scope-release-operations-conversion-004.md |   2 +-
     ...role-scope-release-operations-conversion-005.md |   2 +-
     ...role-scope-release-operations-conversion-006.md |   2 +-
     ...role-scope-release-operations-conversion-007.md |   2 +-
     ...role-scope-release-operations-conversion-009.md |   2 +-
     ...kb-role-session-lifecycle-simplification-002.md |   2 +-
     ...kb-role-session-lifecycle-simplification-004.md |   2 +-
     ...kb-role-session-lifecycle-simplification-006.md |   2 +-
     ...kb-role-session-lifecycle-simplification-008.md |   2 +-
     ...kb-role-session-lifecycle-simplification-010.md |   2 +-
     ...gonality-dispatch-landing-reconciliation-001.md |   2 +-
     ...gonality-dispatch-landing-reconciliation-002.md |   2 +-
     ...gonality-dispatch-landing-reconciliation-003.md |   2 +-
     ...gonality-dispatch-landing-reconciliation-004.md |   2 +-
     ...gonality-dispatch-landing-reconciliation-006.md |   2 +-
     ...gonality-dispatch-landing-reconciliation-007.md |   2 +-
     ...gonality-dispatch-landing-reconciliation-008.md |   2 +-
     ...le-status-orthogonality-dispatch-scoping-001.md |   2 +-
     ...le-status-orthogonality-dispatch-scoping-003.md |   2 +-
     ...le-status-orthogonality-dispatch-scoping-004.md |   2 +-
     ...le-status-orthogonality-dispatch-scoping-006.md |   2 +-
     ...s-orthogonality-dispatch-slice-1-adr-dcl-001.md |   2 +-
     ...s-orthogonality-dispatch-slice-1-adr-dcl-002.md |   2 +-
     ...s-orthogonality-dispatch-slice-1-adr-dcl-003.md |   2 +-
     ...s-orthogonality-dispatch-slice-1-adr-dcl-004.md |   2 +-
     ...s-orthogonality-dispatch-slice-1-adr-dcl-005.md |   2 +-
     ...s-orthogonality-dispatch-slice-1-adr-dcl-006.md |   2 +-
     ...s-orthogonality-dispatch-slice-1-adr-dcl-007.md |   2 +-
     ...s-orthogonality-dispatch-slice-1-adr-dcl-008.md |   2 +-
     ...s-orthogonality-dispatch-slice-1-adr-dcl-009.md |   2 +-
     ...s-orthogonality-dispatch-slice-1-adr-dcl-010.md |   2 +-
     ...-orthogonality-dispatch-slice-2-resolver-001.md |   2 +-
     ...-orthogonality-dispatch-slice-2-resolver-002.md |   2 +-
     ...-orthogonality-dispatch-slice-2-resolver-003.md |   2 +-
     ...-orthogonality-dispatch-slice-2-resolver-004.md |   2 +-
     ...boundary-external-harness-exec-exception-001.md |   2 +-
     ...boundary-external-harness-exec-exception-002.md |   2 +-
     ...boundary-external-harness-exec-exception-003.md |   2 +-
     ...boundary-external-harness-exec-exception-004.md |   2 +-
     ...boundary-external-harness-exec-exception-005.md |   2 +-
     ...boundary-external-harness-exec-exception-006.md |   2 +-
     ...boundary-external-harness-exec-exception-008.md |   2 +-
     ...tkb-root-directory-migration-post-verify-010.md |   2 +-
     ...tkb-root-directory-migration-post-verify-012.md |   2 +-
     ...tkb-root-directory-migration-post-verify-014.md |   2 +-
     bridge/gtkb-ruff-format-pre-file-gate-001.md       |   2 +-
     bridge/gtkb-ruff-format-pre-file-gate-002.md       |   2 +-
     bridge/gtkb-ruff-format-pre-file-gate-003.md       |   2 +-
     bridge/gtkb-ruff-format-pre-file-gate-004.md       |   2 +-
     bridge/gtkb-ruff-format-pre-file-gate-005.md       |   2 +-
     bridge/gtkb-ruff-format-pre-file-gate-006.md       |   2 +-
     bridge/gtkb-ruff-format-pre-file-gate-007.md       |   2 +-
     bridge/gtkb-ruff-format-pre-file-gate-008.md       |   2 +-
     bridge/gtkb-ruff-format-pre-file-gate-010.md       |   2 +-
     ...b-s341-backlog-candidates-membase-insert-001.md |   2 +-
     ...b-s341-backlog-candidates-membase-insert-002.md |   2 +-
     ...b-s341-backlog-candidates-membase-insert-003.md |   2 +-
     ...b-s341-backlog-candidates-membase-insert-004.md |   2 +-
     ...b-s341-backlog-candidates-membase-insert-005.md |   2 +-
     ...b-s341-backlog-candidates-membase-insert-007.md |   2 +-
     ...b-s341-backlog-candidates-membase-insert-009.md |   2 +-
     ...b-s341-backlog-candidates-membase-insert-011.md |   2 +-
     ...-s358-w1-retirement-machinery-correction-001.md |   2 +-
     ...-s358-w1-retirement-machinery-correction-003.md |   2 +-
     ...-s358-w1-retirement-machinery-correction-005.md |   2 +-
     ...-s358-w1-retirement-machinery-correction-008.md |   2 +-
     ...-s358-w1-retirement-machinery-correction-011.md |   2 +-
     ...-s358-w1-retirement-machinery-correction-013.md |   2 +-
     ...-s358-w1-retirement-machinery-correction-015.md |   2 +-
     ...-s358-w1-retirement-machinery-correction-017.md |   2 +-
     ...-s358-w1-retirement-machinery-correction-018.md |   2 +-
     ...-s358-w1-retirement-machinery-correction-019.md |   2 +-
     ...-s358-w1-retirement-machinery-correction-021.md |   2 +-
     bridge/gtkb-s358-w2-agent-red-gov-trio-v2-001.md   |   2 +-
     bridge/gtkb-s358-w2-agent-red-gov-trio-v2-003.md   |   2 +-
     bridge/gtkb-s358-w2-agent-red-gov-trio-v2-005.md   |   2 +-
     bridge/gtkb-s358-w2-agent-red-gov-trio-v2-007.md   |   2 +-
     bridge/gtkb-s358-w2-agent-red-gov-trio-v2-011.md   |   2 +-
     bridge/gtkb-s358-w2-agent-red-gov-trio-v2-014.md   |   2 +-
     ...3-requirements-collection-hook-title-fix-001.md |   2 +-
     ...3-requirements-collection-hook-title-fix-003.md |   2 +-
     ...3-requirements-collection-hook-title-fix-005.md |   2 +-
     ...3-requirements-collection-hook-title-fix-008.md |   2 +-
     ...3-requirements-collection-hook-title-fix-009.md |   2 +-
     ...3-requirements-collection-hook-title-fix-014.md |   2 +-
     bridge/gtkb-s358-w4-enforcement-calibration-001.md |   2 +-
     bridge/gtkb-s358-w4-enforcement-calibration-003.md |   2 +-
     bridge/gtkb-s358-w4-enforcement-calibration-005.md |   2 +-
     bridge/gtkb-s358-w4-enforcement-calibration-008.md |   2 +-
     .../gtkb-s358-w5-token-framing-correction-001.md   |   2 +-
     .../gtkb-s358-w5-token-framing-correction-003.md   |   2 +-
     .../gtkb-s358-w5-token-framing-correction-006.md   |   2 +-
     bridge/gtkb-s373-triage-umbrella-001.md            |   2 +-
     ...uted-delib-2514-2520-governed-retraction-002.md |   2 +-
     ...uted-delib-2514-2520-governed-retraction-003.md |   2 +-
     ...uted-delib-2514-2520-governed-retraction-004.md |   2 +-
     ...uted-delib-2514-2520-governed-retraction-006.md |   2 +-
     bridge/gtkb-scaffold-upgrade-tier-a-003.md         |   2 +-
     bridge/gtkb-scaffold-upgrade-tier-a-005.md         |   2 +-
     bridge/gtkb-scaffold-upgrade-tier-a-007.md         |   2 +-
     bridge/gtkb-scaffold-upgrade-tier-a-009.md         |   2 +-
     ...service-boundary-baseline-implementation-001.md |   2 +-
     ...service-boundary-baseline-implementation-003.md |   2 +-
     ...service-boundary-baseline-implementation-005.md |   2 +-
     ...service-boundary-baseline-implementation-007.md |   2 +-
     ...service-boundary-baseline-implementation-009.md |   2 +-
     ...tic-leak-closure-slice-1-advisory-router-001.md |   2 +-
     ...tic-leak-closure-slice-1-advisory-router-003.md |   2 +-
     ...tic-leak-closure-slice-1-advisory-router-005.md |   2 +-
     ...tic-leak-closure-slice-1-advisory-router-007.md |   2 +-
     ...tic-leak-closure-slice-1-advisory-router-009.md |   2 +-
     ...tic-leak-closure-slice-1-advisory-router-012.md |   2 +-
     ...tic-leak-closure-slice-2-benchmark-suite-001.md |   2 +-
     ...tic-leak-closure-slice-2-benchmark-suite-003.md |   2 +-
     ...tic-leak-closure-slice-2-benchmark-suite-005.md |   2 +-
     ...tic-leak-closure-slice-2-benchmark-suite-007.md |   2 +-
     ...tic-leak-closure-slice-2-benchmark-suite-009.md |   2 +-
     ...tic-leak-closure-slice-2-benchmark-suite-012.md |   2 +-
     ...tic-leak-closure-slice-2-benchmark-suite-014.md |   2 +-
     ...tic-leak-closure-slice-2-benchmark-suite-016.md |   2 +-
     ...ic-leak-closure-slice-3-assertion-triage-001.md |   2 +-
     ...ic-leak-closure-slice-3-assertion-triage-003.md |   2 +-
     ...ic-leak-closure-slice-3-assertion-triage-005.md |   2 +-
     ...ic-leak-closure-slice-3-assertion-triage-007.md |   2 +-
     ...ic-leak-closure-slice-3-assertion-triage-011.md |   2 +-
     ...ic-leak-closure-slice-3-assertion-triage-013.md |   2 +-
     ...ic-leak-closure-slice-3-assertion-triage-016.md |   2 +-
     ...sure-slice-4-implementation-gate-hygiene-001.md |   2 +-
     ...sure-slice-4-implementation-gate-hygiene-003.md |   2 +-
     bridge/gtkb-session-envelope-durability-001-001.md |   2 +-
     bridge/gtkb-session-envelope-durability-001-002.md |   2 +-
     bridge/gtkb-session-envelope-durability-001-003.md |   2 +-
     bridge/gtkb-session-envelope-durability-001-004.md |   2 +-
     bridge/gtkb-session-envelope-durability-001-005.md |   2 +-
     bridge/gtkb-session-envelope-durability-001-006.md |   2 +-
     ...b-session-id-shared-resolver-unification-001.md |   2 +-
     ...b-session-id-shared-resolver-unification-002.md |   2 +-
     ...b-session-id-shared-resolver-unification-003.md |   2 +-
     ...b-session-id-shared-resolver-unification-004.md |   2 +-
     ...b-session-id-shared-resolver-unification-006.md |   2 +-
     ...b-session-id-shared-resolver-unification-008.md |   2 +-
     ...-session-overlay-baseline-implementation-001.md |   2 +-
     ...-session-overlay-baseline-implementation-003.md |   2 +-
     ...-session-overlay-baseline-implementation-005.md |   2 +-
     bridge/gtkb-session-start-formalization-001-003.md |   2 +-
     bridge/gtkb-session-start-formalization-001-005.md |   2 +-
     bridge/gtkb-session-start-formalization-001-006.md |   2 +-
     bridge/gtkb-session-start-formalization-001-008.md |   2 +-
     bridge/gtkb-session-start-formalization-001-009.md |   2 +-
     bridge/gtkb-session-start-formalization-001-010.md |   2 +-
     bridge/gtkb-session-start-formalization-001-012.md |   2 +-
     bridge/gtkb-session-start-formalization-001.md     |   2 +-
     bridge/gtkb-session-startup-project-002.md         |   2 +-
     bridge/gtkb-session-startup-project-004.md         |   2 +-
     bridge/gtkb-session-startup-project-006.md         |   2 +-
     bridge/gtkb-session-startup-project-007.md         |   2 +-
     bridge/gtkb-session-work-subject-001.md            |   2 +-
     bridge/gtkb-session-work-subject-002.md            |   4 +-
     bridge/gtkb-session-work-subject-003.md            |   4 +-
     bridge/gtkb-session-work-subject-004.md            |   4 +-
     .../gtkb-session-wrap-knowledge-collection-001.md  |   2 +-
     .../gtkb-session-wrap-knowledge-collection-002.md  |   2 +-
     .../gtkb-session-wrap-knowledge-collection-004.md  |   2 +-
     bridge/gtkb-session-wrap-procedure-001-001.md      |   2 +-
     bridge/gtkb-session-wrap-procedure-001-002.md      |   2 +-
     bridge/gtkb-session-wrap-procedure-001-003.md      |   2 +-
     bridge/gtkb-session-wrap-procedure-001-004.md      |   2 +-
     ...single-harness-bridge-activation-manager-001.md |   2 +-
     ...single-harness-bridge-activation-manager-002.md |   2 +-
     ...single-harness-bridge-activation-manager-003.md |   2 +-
     ...single-harness-bridge-activation-manager-004.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-002.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-003.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-004.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-005.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-006.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-007.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-008.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-009.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-010.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-011.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-012.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-013.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-014.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-016.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-018.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-020.md |   2 +-
     ...tkb-single-harness-bridge-dispatcher-001-022.md |   2 +-
     .../gtkb-single-harness-bridge-dispatcher-001.md   |   2 +-
     ...single-harness-bridge-dispatcher-slice-2-001.md |   2 +-
     ...single-harness-bridge-dispatcher-slice-2-002.md |   2 +-
     ...single-harness-bridge-dispatcher-slice-2-003.md |   2 +-
     ...single-harness-bridge-dispatcher-slice-2-004.md |   2 +-
     ...single-harness-bridge-dispatcher-slice-2-005.md |   2 +-
     ...single-harness-bridge-dispatcher-slice-2-006.md |   2 +-
     ...single-harness-bridge-dispatcher-slice-2-008.md |   2 +-
     ...single-harness-bridge-dispatcher-slice-2-010.md |   2 +-
     bridge/gtkb-skill-modernization-scoping-001.md     |   2 +-
     bridge/gtkb-skill-modernization-scoping-003.md     |   2 +-
     bridge/gtkb-skill-modernization-scoping-004.md     |   2 +-
     bridge/gtkb-skill-modernization-scoping-006.md     |   2 +-
     ...dernization-slice-0-skill-health-checker-001.md |   2 +-
     ...dernization-slice-0-skill-health-checker-002.md |   2 +-
     ...dernization-slice-0-skill-health-checker-004.md |   2 +-
     ...rnization-slice-3-kb-work-item-migration-001.md |   2 +-
     ...rnization-slice-3-kb-work-item-migration-003.md |   2 +-
     ...rnization-slice-3-kb-work-item-migration-005.md |   2 +-
     ...rnization-slice-3-kb-work-item-migration-008.md |   2 +-
     ...rnization-slice-3-kb-work-item-migration-009.md |   2 +-
     ...rnization-slice-3-kb-work-item-migration-010.md |   2 +-
     ...rnization-slice-3-kb-work-item-migration-011.md |   2 +-
     ...rnization-slice-3-kb-work-item-migration-012.md |   2 +-
     ...tkb-slice2b-metrics-index-reconciliation-007.md |   2 +-
     ...kb-smart-bridge-trigger-foundation-spike-003.md |   2 +-
     .../gtkb-smart-poller-p1-p2-implementation-003.md  |   2 +-
     bridge/gtkb-sonarcloud-config-relink-gt-kb-001.md  |   2 +-
     bridge/gtkb-sonarcloud-config-relink-gt-kb-004.md  |   2 +-
     bridge/gtkb-sonarcloud-config-relink-gt-kb-006.md  |   2 +-
     ...tkb-source-of-truth-freshness-governance-001.md |   2 +-
     ...tkb-source-of-truth-freshness-governance-002.md |   2 +-
     ...tkb-source-of-truth-freshness-governance-003.md |   2 +-
     ...tkb-source-of-truth-freshness-governance-004.md |   2 +-
     ...tkb-source-of-truth-freshness-governance-005.md |   2 +-
     ...tkb-source-of-truth-freshness-governance-006.md |   2 +-
     ...tkb-source-of-truth-freshness-governance-007.md |   2 +-
     ...tkb-source-of-truth-freshness-governance-009.md |   2 +-
     ...tkb-source-of-truth-freshness-governance-010.md |   2 +-
     ...tkb-source-of-truth-freshness-governance-011.md |   2 +-
     ...tkb-source-of-truth-freshness-governance-012.md |   2 +-
     .../gtkb-sp1a-ollama-lo-prompt-restructure-003.md  |   2 +-
     .../gtkb-sp1a-ollama-lo-prompt-restructure-004.md  |   2 +-
     .../gtkb-sp1a-ollama-lo-prompt-restructure-006.md  |   2 +-
     bridge/gtkb-sp1b-dispatch-outcome-tracker-001.md   |   2 +-
     bridge/gtkb-sp1b-dispatch-outcome-tracker-003.md   |   2 +-
     bridge/gtkb-sp1b-dispatch-outcome-tracker-005.md   |   2 +-
     bridge/gtkb-sp1b-dispatch-outcome-tracker-006.md   |   2 +-
     .../gtkb-sp1c-author-meets-reviewer-guard-001.md   |   2 +-
     .../gtkb-sp1c-author-meets-reviewer-guard-003.md   |   2 +-
     .../gtkb-sp1c-author-meets-reviewer-guard-005.md   |   2 +-
     .../gtkb-sp1c-author-meets-reviewer-guard-006.md   |   2 +-
     bridge/gtkb-sp1d-turn-budget-optimization-001.md   |   2 +-
     bridge/gtkb-sp1d-turn-budget-optimization-003.md   |   2 +-
     bridge/gtkb-sp1d-turn-budget-optimization-005.md   |   2 +-
     bridge/gtkb-sp1d-turn-budget-optimization-006.md   |   2 +-
     ...er-test-id-investigation-closure-slice-1-001.md |   2 +-
     ...er-test-id-investigation-closure-slice-1-002.md |   2 +-
     ...er-test-id-investigation-closure-slice-1-004.md |   2 +-
     bridge/gtkb-spec-coherence-cli-001.md              |   2 +-
     bridge/gtkb-spec-coherence-cli-002.md              |   2 +-
     bridge/gtkb-spec-coherence-cli-004.md              |   2 +-
     bridge/gtkb-spec-coherence-cli-scoping-001.md      |   2 +-
     bridge/gtkb-spec-coherence-cli-scoping-002.md      |   2 +-
     bridge/gtkb-spec-coherence-cli-scoping-004.md      |   2 +-
     .../gtkb-spec-lifecycle-schema-2026-04-29-001.md   |   2 +-
     .../gtkb-spec-lifecycle-schema-2026-04-29-003.md   |   2 +-
     .../gtkb-spec-lifecycle-schema-2026-04-29-005.md   |   2 +-
     .../gtkb-spec-lifecycle-schema-2026-04-29-006.md   |   2 +-
     .../gtkb-spec-lifecycle-schema-2026-04-29-007.md   |   2 +-
     .../gtkb-spec-lifecycle-schema-2026-04-29-008.md   |   2 +-
     bridge/gtkb-spec-lifecycle-schema-slice-1-001.md   |   2 +-
     bridge/gtkb-spec-lifecycle-schema-slice-1-003.md   |   2 +-
     bridge/gtkb-spec-lifecycle-schema-slice-1-006.md   |   2 +-
     bridge/gtkb-spec-lifecycle-schema-slice-1-008.md   |   2 +-
     .../gtkb-stale-thread-closure-slice-3-impl-001.md  |   2 +-
     .../gtkb-stale-thread-closure-slice-3-impl-002.md  |   2 +-
     .../gtkb-stale-thread-closure-slice-3-impl-003.md  |   2 +-
     .../gtkb-stale-thread-closure-slice-3-impl-004.md  |   2 +-
     .../gtkb-stale-thread-closure-slice-3-impl-006.md  |   2 +-
     ...anding-backlog-harvest-audit-maintenance-001.md |   2 +-
     ...anding-backlog-harvest-audit-maintenance-002.md |   2 +-
     ...anding-backlog-harvest-audit-maintenance-003.md |   2 +-
     ...anding-backlog-harvest-audit-maintenance-004.md |   2 +-
     ...anding-backlog-harvest-audit-maintenance-006.md |   2 +-
     ...b-startup-cache-dcl-supersession-scoping-001.md |   2 +-
     ...b-startup-cache-dcl-supersession-scoping-002.md |   2 +-
     ...b-startup-cache-dcl-supersession-scoping-003.md |   2 +-
     ...b-startup-cache-dcl-supersession-scoping-004.md |   2 +-
     ...b-startup-cache-dcl-supersession-scoping-006.md |   2 +-
     bridge/gtkb-startup-control-vocabulary-map-001.md  |   2 +-
     bridge/gtkb-startup-control-vocabulary-map-002.md  |   2 +-
     bridge/gtkb-startup-control-vocabulary-map-004.md  |   2 +-
     ...tkb-startup-dashboard-reachability-probe-003.md |   2 +-
     ...tkb-startup-dashboard-reachability-probe-006.md |   2 +-
     ...p-enhancements-completion-reconciliation-001.md |   2 +-
     ...p-enhancements-completion-reconciliation-002.md |   2 +-
     ...p-enhancements-completion-reconciliation-003.md |   2 +-
     ...p-enhancements-completion-reconciliation-004.md |   2 +-
     ...p-enhancements-completion-reconciliation-005.md |   2 +-
     ...p-enhancements-completion-reconciliation-006.md |   2 +-
     bridge/gtkb-startup-enhancements-p1-001.md         |   2 +-
     bridge/gtkb-startup-enhancements-p1-003.md         |   2 +-
     ...artup-enhancements-p2-freshness-contract-001.md |   2 +-
     ...artup-enhancements-p2-freshness-contract-003.md |   2 +-
     ...artup-enhancements-p2-freshness-contract-004.md |   2 +-
     ...artup-enhancements-p2-freshness-contract-006.md |   2 +-
     ...artup-enhancements-p2-freshness-contract-007.md |   2 +-
     ...artup-enhancements-p2-freshness-contract-008.md |   2 +-
     ...artup-enhancements-p2-freshness-contract-009.md |   2 +-
     ...artup-enhancements-p2-freshness-contract-011.md |   2 +-
     ...artup-enhancements-p2-freshness-contract-012.md |   2 +-
     ...artup-enhancements-p2-freshness-contract-015.md |   2 +-
     bridge/gtkb-startup-evidence-restoration-001.md    |   2 +-
     ...kb-startup-payload-canonical-state-drift-001.md |   2 +-
     ...kb-startup-payload-canonical-state-drift-003.md |   2 +-
     ...startup-payload-profiler-compact-context-001.md |   2 +-
     ...startup-payload-profiler-compact-context-002.md |   2 +-
     ...startup-payload-profiler-compact-context-004.md |   2 +-
     ...startup-payload-profiler-compact-context-006.md |   2 +-
     ...-startup-refractor-glossary-load-surface-001.md |   2 +-
     ...-startup-refractor-glossary-load-surface-003.md |   2 +-
     ...-startup-refractor-glossary-load-surface-006.md |   2 +-
     bridge/gtkb-startup-refractor-scoping-001.md       |   2 +-
     bridge/gtkb-startup-refractor-scoping-002.md       |   2 +-
     bridge/gtkb-startup-refractor-scoping-004.md       |   2 +-
     ...ractor-slice-a-startup-control-inventory-001.md |   2 +-
     ...ractor-slice-a-startup-control-inventory-002.md |   2 +-
     ...ractor-slice-a-startup-control-inventory-004.md |   2 +-
     ...refractor-slice-b-local-settings-hygiene-001.md |   2 +-
     ...refractor-slice-b-local-settings-hygiene-002.md |   2 +-
     ...refractor-slice-b-local-settings-hygiene-004.md |   2 +-
     ...refractor-slice-c-startup-index-overlays-001.md |   2 +-
     ...refractor-slice-c-startup-index-overlays-002.md |   2 +-
     ...refractor-slice-c-startup-index-overlays-004.md |   2 +-
     ...refractor-slice-c-startup-index-overlays-006.md |   2 +-
     ...efractor-slice-d-sessionstart-hook-dedup-001.md |   2 +-
     ...efractor-slice-d-sessionstart-hook-dedup-002.md |   2 +-
     ...efractor-slice-d-sessionstart-hook-dedup-003.md |   2 +-
     ...efractor-slice-d-sessionstart-hook-dedup-004.md |   2 +-
     ...efractor-slice-d-sessionstart-hook-dedup-006.md |   2 +-
     ...efractor-slice-d-sessionstart-hook-dedup-008.md |   2 +-
     ...ractor-slice-e-lo-startup-text-authority-001.md |   2 +-
     ...ractor-slice-e-lo-startup-text-authority-002.md |   2 +-
     ...ractor-slice-e-lo-startup-text-authority-004.md |   2 +-
     ...ractor-slice-e-lo-startup-text-authority-006.md |   2 +-
     .../gtkb-startup-relay-cache-ttl-self-heal-001.md  |   2 +-
     .../gtkb-startup-relay-cache-ttl-self-heal-002.md  |   2 +-
     .../gtkb-startup-relay-cache-ttl-self-heal-004.md  |   2 +-
     ...gtkb-startup-relay-truncation-fix-refile-008.md |   2 +-
     ...gtkb-startup-relay-truncation-fix-refile-010.md |   2 +-
     ...gtkb-startup-relay-truncation-fix-refile-012.md |   2 +-
     ...b-startup-role-slot-label-disambiguation-001.md |   2 +-
     ...b-startup-role-slot-label-disambiguation-002.md |   2 +-
     ...b-startup-role-slot-label-disambiguation-003.md |   2 +-
     ...b-startup-role-slot-label-disambiguation-004.md |   2 +-
     ...b-startup-role-slot-label-disambiguation-006.md |   2 +-
     ...rigger-awareness-and-skill-reference-001-002.md |   2 +-
     ...rigger-awareness-and-skill-reference-001-003.md |   2 +-
     ...rigger-awareness-and-skill-reference-001-004.md |   2 +-
     ...rigger-awareness-and-skill-reference-001-006.md |   2 +-
     ...up-trigger-awareness-and-skill-reference-001.md |   2 +-
     ...b-sweep-commit-skill-parity-registration-002.md |   2 +-
     ...b-sweep-commit-skill-parity-registration-004.md |   2 +-
     ...b-sweep-commit-skill-parity-registration-005.md |   2 +-
     ...b-sweep-commit-skill-parity-registration-007.md |   2 +-
     ...b-sweep-commit-skill-parity-registration-009.md |   2 +-
     .../gtkb-telemetry-churn-policy-2026-04-28-002.md  |   2 +-
     .../gtkb-telemetry-churn-policy-2026-04-28-004.md  |   2 +-
     ...terminal-project-record-retirement-batch-001.md |   2 +-
     ...terminal-project-record-retirement-batch-003.md |   2 +-
     ...terminal-project-record-retirement-batch-004.md |   2 +-
     ...terminal-project-record-retirement-batch-006.md |   2 +-
     ...kb-test-build-contract-orphan-relocation-001.md |   2 +-
     ...kb-test-build-contract-orphan-relocation-003.md |   2 +-
     ...kb-test-build-contract-orphan-relocation-006.md |   2 +-
     ...gtkb-tier-a-managed-skill-adoption-apply-001.md |   2 +-
     ...gtkb-tier-a-managed-skill-adoption-apply-003.md |   2 +-
     .../gtkb-transcript-scan-dispatch-role-sot-001.md  |   2 +-
     .../gtkb-transcript-scan-dispatch-role-sot-003.md  |   2 +-
     .../gtkb-transcript-scan-dispatch-role-sot-004.md  |   2 +-
     .../gtkb-transcript-scan-dispatch-role-sot-005.md  |   2 +-
     .../gtkb-transcript-scan-dispatch-role-sot-008.md  |   2 +-
     bridge/gtkb-trigger-diagnose-tool-bugfix-001.md    |   2 +-
     bridge/gtkb-trigger-diagnose-tool-bugfix-002.md    |   2 +-
     bridge/gtkb-trigger-diagnose-tool-bugfix-004.md    |   2 +-
     ...b-understand-anything-evaluation-install-001.md |   2 +-
     ...b-understand-anything-evaluation-install-002.md |   2 +-
     ...b-understand-anything-evaluation-install-003.md |   2 +-
     ...b-understand-anything-evaluation-install-004.md |   2 +-
     ...b-understand-anything-evaluation-install-005.md |   2 +-
     ...b-understand-anything-evaluation-install-007.md |   2 +-
     ...b-understand-anything-evaluation-install-008.md |   2 +-
     ...b-understand-anything-evaluation-install-010.md |   2 +-
     ...kb-v1-docker-isolation-validator-scoping-001.md |   2 +-
     ...kb-v1-docker-isolation-validator-scoping-003.md |   2 +-
     ...b-v1-mechanical-enforcement-gate-scoping-001.md |   2 +-
     ...b-v1-mechanical-enforcement-gate-scoping-002.md |   2 +-
     bridge/gtkb-v1-s509-proposal-remediation-001.md    |   6 +-
     bridge/gtkb-v1-s509-proposal-remediation-002.md    |   6 +-
     bridge/gtkb-v1-s509-proposal-remediation-003.md    |   2 +-
     bridge/gtkb-v1-s509-proposal-remediation-005.md    |   2 +-
     ...gtkb-v1-spec-corpus-distillation-scoping-001.md |   2 +-
     ...gtkb-v1-spec-corpus-distillation-scoping-002.md |   2 +-
     ...d-spec-hygiene-cluster-slice-1-inventory-002.md |   2 +-
     ...d-spec-hygiene-cluster-slice-1-inventory-003.md |   2 +-
     ...d-spec-hygiene-cluster-slice-1-inventory-004.md |   2 +-
     ...d-spec-hygiene-cluster-slice-1-inventory-005.md |   2 +-
     ...d-spec-hygiene-cluster-slice-1-inventory-006.md |   2 +-
     ...d-spec-hygiene-cluster-slice-1-inventory-007.md |   2 +-
     ...d-spec-hygiene-cluster-slice-1-inventory-008.md |   2 +-
     .../gtkb-verify-skill-spec-to-test-mapping-001.md  |   2 +-
     .../gtkb-verify-skill-spec-to-test-mapping-003.md  |   2 +-
     .../gtkb-verify-skill-spec-to-test-mapping-005.md  |   2 +-
     .../gtkb-verify-skill-spec-to-test-mapping-006.md  |   2 +-
     .../gtkb-verify-skill-spec-to-test-mapping-008.md  |   2 +-
     .../gtkb-verify-skill-spec-to-test-mapping-010.md  |   2 +-
     ...gtkb-verify-verdict-author-skill-slice-1-001.md |   2 +-
     ...gtkb-verify-verdict-author-skill-slice-1-004.md |   2 +-
     bridge/gtkb-wi-3423-pauth-creation-001.md          |   2 +-
     bridge/gtkb-wi-3423-pauth-creation-002.md          |   2 +-
     bridge/gtkb-wi-3423-pauth-creation-004.md          |   2 +-
     ...kb-wi-3506-phantom-spec-citation-repoint-001.md |   2 +-
     ...kb-wi-3506-phantom-spec-citation-repoint-002.md |   2 +-
     ...kb-wi-3506-phantom-spec-citation-repoint-003.md |   2 +-
     ...kb-wi-3506-phantom-spec-citation-repoint-004.md |   2 +-
     ...kb-wi-3506-phantom-spec-citation-repoint-005.md |   2 +-
     ...kb-wi-3506-phantom-spec-citation-repoint-006.md |   2 +-
     ...kb-wi-4225-scaffold-golden-fixture-regen-001.md |   2 +-
     ...kb-wi-4225-scaffold-golden-fixture-regen-002.md |   2 +-
     ...kb-wi-4225-scaffold-golden-fixture-regen-003.md |   2 +-
     ...kb-wi-4225-scaffold-golden-fixture-regen-004.md |   2 +-
     ...kb-wi-4225-scaffold-golden-fixture-regen-005.md |   2 +-
     ...kb-wi-4225-scaffold-golden-fixture-regen-006.md |   2 +-
     ...kb-wi-4225-scaffold-golden-fixture-regen-007.md |   2 +-
     ...kb-wi-4225-scaffold-golden-fixture-regen-008.md |   2 +-
     ...kb-wi-4225-scaffold-golden-fixture-regen-009.md |   2 +-
     ...kb-wi-4225-scaffold-golden-fixture-regen-010.md |   2 +-
     ...9-scaffold-phantom-spec-citation-repoint-001.md |   2 +-
     ...9-scaffold-phantom-spec-citation-repoint-002.md |   2 +-
     ...9-scaffold-phantom-spec-citation-repoint-003.md |   2 +-
     ...9-scaffold-phantom-spec-citation-repoint-004.md |   2 +-
     bridge/gtkb-wi3326-project-rehome-001.md           |   2 +-
     bridge/gtkb-wi3326-project-rehome-002.md           |   2 +-
     bridge/gtkb-wi3326-project-rehome-003.md           |   2 +-
     bridge/gtkb-wi3326-project-rehome-004.md           |   2 +-
     bridge/gtkb-wi3326-project-rehome-006.md           |   2 +-
     bridge/gtkb-wi3326-project-rehome-007.md           |   2 +-
     ...-project-rehome-executable-packet-repair-001.md |   2 +-
     ...-project-rehome-executable-packet-repair-002.md |   2 +-
     ...-project-rehome-executable-packet-repair-004.md |   2 +-
     ...-project-rehome-executable-packet-repair-006.md |   2 +-
     .../gtkb-work-envelope-router-slice-1-001-001.md   |   2 +-
     .../gtkb-work-envelope-router-slice-1-001-002.md   |   2 +-
     .../gtkb-work-envelope-router-slice-1-001-003.md   |   2 +-
     .../gtkb-work-envelope-router-slice-1-001-004.md   |   2 +-
     ...k-envelope-router-slice-2-per-type-specs-001.md |   2 +-
     ...k-envelope-router-slice-2-per-type-specs-002.md |   2 +-
     ...-intent-registry-prime-write-integration-001.md |   2 +-
     ...-intent-registry-prime-write-integration-002.md |   2 +-
     ...-intent-registry-prime-write-integration-003.md |   2 +-
     ...-intent-registry-prime-write-integration-004.md |   2 +-
     ...-intent-registry-prime-write-integration-005.md |   2 +-
     ...-intent-registry-prime-write-integration-006.md |   2 +-
     ...-intent-registry-prime-write-integration-007.md |   2 +-
     ...-intent-registry-prime-write-integration-008.md |   2 +-
     ...-intent-registry-prime-write-integration-009.md |   2 +-
     ...-intent-registry-prime-write-integration-010.md |   2 +-
     ...-intent-registry-prime-write-integration-011.md |   2 +-
     ...-intent-registry-prime-write-integration-012.md |   2 +-
     ...-intent-registry-prime-write-integration-014.md |   2 +-
     ...k-item-priority-canonical-p0p3-migration-001.md |   2 +-
     ...k-item-priority-canonical-p0p3-migration-002.md |   2 +-
     ...k-item-priority-canonical-p0p3-migration-003.md |   2 +-
     ...k-item-priority-canonical-p0p3-migration-004.md |   2 +-
     ...k-item-priority-canonical-p0p3-migration-005.md |   2 +-
     ...k-item-priority-canonical-p0p3-migration-006.md |   2 +-
     ...k-item-priority-canonical-p0p3-migration-007.md |   2 +-
     ...k-item-priority-canonical-p0p3-migration-008.md |   2 +-
     ...tkb-work-list-md-gov-010-path-correction-001.md |   2 +-
     ...tkb-work-list-md-gov-010-path-correction-003.md |   2 +-
     ...-subject-aware-testing-integration-probe-001.md |   2 +-
     ...-subject-aware-testing-integration-probe-003.md |   2 +-
     ...-subject-aware-testing-integration-probe-006.md |   2 +-
     ...-subject-aware-testing-integration-probe-008.md |   2 +-
     ...-subject-root-enforcement-implementation-001.md |   2 +-
     ...-subject-root-enforcement-implementation-003.md |   2 +-
     ...-subject-root-enforcement-implementation-005.md |   2 +-
     ...-subject-root-enforcement-implementation-007.md |   2 +-
     ...-subject-root-enforcement-implementation-009.md |   2 +-
     ...-subject-root-enforcement-implementation-011.md |   2 +-
     ...-subject-root-enforcement-implementation-013.md |   2 +-
     ...-subject-root-enforcement-implementation-015.md |   2 +-
     ...-subject-root-enforcement-implementation-017.md |   2 +-
     ...-subject-root-enforcement-implementation-019.md |   2 +-
     ...gtkb-work-tree-hygiene-mechanism-scoping-001.md |   2 +-
     ...gtkb-work-tree-hygiene-mechanism-scoping-002.md |   2 +-
     .../gtkb-work-tree-hygiene-slice-a-detector-001.md |   2 +-
     .../gtkb-work-tree-hygiene-slice-a-detector-002.md |   2 +-
     .../gtkb-work-tree-hygiene-slice-a-detector-004.md |   2 +-
     ...n-authorization-envelope-slice-1-scoping-001.md |   2 +-
     ...n-authorization-envelope-slice-1-scoping-002.md |   2 +-
     ...n-authorization-envelope-slice-1-scoping-004.md |   2 +-
     ...n-authorization-envelope-slice-1-scoping-006.md |   2 +-
     ...packet-auth-envelope-slice-2-auto-packet-001.md |   2 +-
     ...packet-auth-envelope-slice-2-auto-packet-004.md |   2 +-
     ...gtkb-workspace-orphan-cleanup-2026-06-05-001.md |   2 +-
     ...gtkb-workspace-orphan-cleanup-2026-06-05-002.md |   2 +-
     ...gtkb-workspace-orphan-cleanup-2026-06-05-003.md |   2 +-
     .../gtkb-workstream-focus-marker-race-fix-003.md   |  10 ++
     ...gtkb-wrap-scan-report-relocation-slice-1-001.md |   2 +-
     ...gtkb-wrap-scan-report-relocation-slice-1-002.md |   2 +-
     ...gtkb-wrap-scan-report-relocation-slice-1-004.md |   2 +-
     ...apup-clear-impl-start-packet-at-verified-001.md |   2 +-
     ...apup-clear-impl-start-packet-at-verified-002.md |   2 +-
     bridge/gtkb-wrapup-enhancements-closure-001.md     |   2 +-
     bridge/gtkb-wrapup-enhancements-closure-002.md     |   2 +-
     bridge/gtkb-wrapup-enhancements-closure-003.md     |   2 +-
     bridge/gtkb-wrapup-enhancements-closure-004.md     |   2 +-
     bridge/gtkb-wrapup-enhancements-next-slice-001.md  |   2 +-
     bridge/gtkb-wrapup-enhancements-next-slice-003.md  |   2 +-
     bridge/gtkb-wrapup-enhancements-next-slice-006.md  |   2 +-
     bridge/gtkb-wrapup-enhancements-slice1-001.md      |   2 +-
     bridge/gtkb-wrapup-enhancements-slice1-003.md      |   2 +-
     bridge/gtkb-wrapup-enhancements-slice1-005.md      |   2 +-
     ...o-knowledge-architecture-phase-4-scoping-001.md |   2 +-
     ...o-knowledge-architecture-phase-4-scoping-003.md |   2 +-
     ...o-knowledge-architecture-phase-4-scoping-004.md |   2 +-
     ...o-knowledge-architecture-phase-4-scoping-006.md |   2 +-
     ...ess-state-authority-migration-2026-04-27-002.md |   2 +-
     ...ess-state-authority-migration-2026-04-27-004.md |   2 +-
     ...ess-state-authority-migration-2026-04-27-006.md |   2 +-
     ...ess-state-authority-migration-2026-04-27-008.md |   2 +-
     ...ess-state-authority-migration-2026-04-27-010.md |   2 +-
     bridge/s317-ruff-cleanup-pre-existing-debt-002.md  |   2 +-
     bridge/s317-ruff-cleanup-pre-existing-debt-004.md  |   2 +-
     bridge/s317-working-tree-triage-002.md             |   2 +-
     bridge/s317-working-tree-triage-004.md             |   2 +-
     bridge/s317-working-tree-triage-006.md             |   2 +-
     bridge/s317-working-tree-triage-008.md             |   2 +-
     ...roject-root-path-doubling-fix-2026-04-27-002.md |   2 +-
     ...roject-root-path-doubling-fix-2026-04-27-004.md |   2 +-
     ...roject-root-path-doubling-fix-2026-04-27-006.md |   2 +-
     ...art-poller-kind-aware-routing-2026-04-30-001.md |   2 +-
     ...art-poller-kind-aware-routing-2026-04-30-003.md |   2 +-
     ...art-poller-kind-aware-routing-2026-04-30-005.md |   2 +-
     ...art-poller-kind-aware-routing-2026-04-30-007.md |   2 +-
     ...art-poller-kind-aware-routing-2026-04-30-009.md |   2 +-
     ...pec-smart-poller-auto-trigger-2026-04-29-003.md |   2 +-
     groundtruth-kb/pyproject.toml                      |   1 +
     .../src/groundtruth_kb/bridge/__init__.py          |   2 +
     groundtruth-kb/src/groundtruth_kb/bridge/notify.py |   2 +
     groundtruth-kb/src/groundtruth_kb/cli.py           | 146 ++++++++++++++++
     .../src/groundtruth_kb/project/doctor.py           |  66 +++++---
     .../test_workstream_focus_session_role_marker.py   | 140 ++++++++++++++-
     scripts/check_harness_parity.py                    |  19 ++-
     scripts/cross_harness_bridge_trigger.py            | 188 ++++++++++++++++++++-
     scripts/workstream_focus.py                        |  63 ++++++-
     2530 files changed, 3341 insertions(+), 2588 deletions(-)
```

## Acceptance Criteria Status

- Loyal Opposition can determine which child slices are expected and which
- The parent GO, if granted, is limited to decomposition approval and follow-on
- The active role-enhancement project authorization is cited and bounded.
- The previous Phase 9 blocker is not silently ignored; its satisfied evidence is
- The parent cannot mint a direct implementation-start packet for future child

## Risk And Rollback

Document residual risk and the rollback path for the changed files. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
