REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex desktop runtime 2026-07-02
author_model_configuration: Codex desktop; E:/GT-KB; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb

# OPS Lifecycle And Bridge Protocol Foundation - Revised Scope Repair

bridge_kind: prime_proposal
Document: gtkb-ops-lifecycle-protocol-foundation
Version: 005 (REVISED)
Date: 2026-07-02 UTC
Responds to: bridge/gtkb-ops-lifecycle-protocol-foundation-004.md
Prior proposal: bridge/gtkb-ops-lifecycle-protocol-foundation-001.md
Prior GO: bridge/gtkb-ops-lifecycle-protocol-foundation-002.md
Prior blocker report: bridge/gtkb-ops-lifecycle-protocol-foundation-003.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-LIFECYCLE-PROTOCOL-FOUNDATION-WI-4957
Project: PROJECT-GTKB-OPS-LIFECYCLE-PROTOCOL-FOUNDATION
Work Item: WI-4957

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/detector.py", "groundtruth-kb/src/groundtruth_kb/bridge/disposition.py", "groundtruth-kb/src/groundtruth_kb/bridge/notify.py", "groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py", "groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py", "groundtruth-kb/src/groundtruth_kb/bridge/routing.py", "scripts/gtkb_bridge_writer.py", "scripts/bridge_work_intent_registry.py", "scripts/implementation_authorization.py", "scripts/bridge_applicability_preflight.py", "scripts/bridge_citation_freshness_preflight.py", "scripts/verdict_evidence_anchor_preflight.py", "scripts/run_spec_derived_tests.py", "scripts/check_protected_commit_authorization.py", "scripts/session_self_initialization.py", "scripts/dispatcher_runtime.py", ".codex/skills/bridge/helpers/scan_bridge.py", ".codex/skills/bridge/helpers/show_thread_bridge.py", ".codex/skills/bridge/helpers/impl_report_bridge.py", ".codex/skills/bridge/helpers/revise_bridge.py", ".claude/skills/verify/helpers/write_verdict.py", "groundtruth-kb/tests/test_bridge_detector.py", "groundtruth-kb/tests/test_bridge_routing.py", "groundtruth-kb/tests/test_bridge_status_driver.py", "platform_tests/scripts/test_scan_bridge.py", "platform_tests/scripts/test_show_thread_bridge.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/scripts/test_run_spec_derived_tests.py", "platform_tests/scripts/test_verdict_evidence_anchor_preflight.py"]

implementation_scope: source+tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision addresses the LO `NO-GO` by selecting the narrowing path from `bridge/gtkb-ops-lifecycle-protocol-foundation-004.md`: the current thread is revised to exact source/test implementation only, while protected narrative artifact edits are deferred to a separate interactive formal-artifact approval path.

The revised source/test scope implements the machine-enforced bridge protocol foundation for `NO-ACTION` and related lifecycle routing:

- recognize `NO-ACTION` as a canonical bridge status across parser, writer, helper, dispatcher, and evidence-preflight surfaces;
- route latest `NO-ACTION` to Loyal Opposition and never to Prime Builder implementation dispatch;
- keep a prior `GO` non-dispatchable once superseded by latest `NO-ACTION`, with corrected later `GO` treated as fresh authority;
- ensure bridge status scanners, thread loaders, implementation authorization, work-intent parsing, and verification helpers accept the new status token consistently;
- preserve lifecycle-first/scoring-last precedence by keeping status eligibility and quarantine decisions upstream of any lane scoring;
- add focused tests for parser/actionability, bridge writer, dispatcher runtime parsing, work-intent parsing, and helper parity.

All proposed outputs are in-root under `E:/GT-KB`. This revision does not authorize writes to the two protected narrative artifacts named in the v004 `NO-GO` finding. Those protected artifacts require owner-approved formal-artifact approval packets and are explicitly out of scope for this revision.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260702-DISPATCH-LANE-SCORING-EXTENDS-OPS-LIFECYCLE-CONSOLIDATION` - lane scoring extends the OPS lifecycle consolidation.
- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` - owner selected actual governed project, work item, and bridge proposal creation.
- `DELIB-20260702-DISPATCH-OPS-WAVE1-THREE-CHILD-PROPOSALS` - Wave 1 uses child implementation proposals.
- `DELIB-20260702-DISPATCH-OPS-WAVE1-CHILD-PROPOSALS-EMBED-FORMALIZATION` - child proposals may embed formalization with implementation when approval evidence exists.
- `DELIB-20260702-DISPATCH-LIFECYCLE-FIRST-SCORING-LAST-PRECEDENCE` - lifecycle eligibility precedes lane scoring.
- `DELIB-HARNESS-OPS-NO-ACTION-FIRST-CLASS-BRIDGE-STATUS-20260702` - `NO-ACTION` is a first-class PB-authored bridge status token.
- `DELIB-HARNESS-NO-ACTION-LO-ACTIONABLE-BRIDGE-ROUTING-20260702` - `NO-ACTION` routes to Loyal Opposition and is never PB implementation-dispatchable.
- `DELIB-HARNESS-NO-ACTION-PRIOR-GO-NONDISPATCHABLE-SUBSEQUENT-GO-FRESH-AUTHORITY-20260702` - prior GO under `NO-ACTION` is non-dispatchable; a later corrected GO is fresh authority.
- `DELIB-HARNESS-OPS-NO-ACTION-CIRCUIT-BREAKER-20260702` - third `NO-ACTION` creates circuit-breaker OPS diagnosis.
- `DELIB-HARNESS-WORK-ITEM-SEQUENCE-MISMATCH-OPS-QUARANTINE-20260702` - sequence mismatch triggers OPS quarantine.
- `DELIB-HARNESS-OPS-DIAGNOSTIC-CONTEXT-REQUIRED-FIELDS-20260702` - OPS diagnosis work items require diagnostic context fields.
- `DELIB-ACTIVITY-LIFECYCLE-EVENTS-AUTHORITY-MEMBASE-20260702` - lifecycle events use append-only MemBase/KB authority with generated projections.
- `bridge/gtkb-ops-lifecycle-protocol-foundation-hook-scope-amendment-004.md` - `NO-ACTION` bridge-compliance hook registration is already `VERIFIED`.

## Owner Decisions / Input

- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` - owner selected actual project/WI/proposal creation.
- `PAUTH-PROJECT-GTKB-OPS-LIFECYCLE-PROTOCOL-FOUNDATION-WI-4957` - active child-project authorization for this work item.

No new owner decision is required for this narrowed source/test revision because it avoids protected narrative artifact writes. A future narrative-artifact approval proposal will require owner review of the intended rule/terminology content and matching approval packets before those files can be mutated.

## Findings Addressed

### P2: exact target paths for source child files

Response: `target_paths` now lists concrete source, helper, script, and test file paths instead of bare source/test directories. This is intended to satisfy `implementation_authorization.py` target matching without relying on non-recursive directory entries.

### P2: protected narrative artifacts require interactive owner approval

Response: the two protected narrative artifacts named in the v004 `NO-GO` finding are removed from this revision's `target_paths`. Rule/terminology formalization is deferred to a future interactive formal-artifact approval thread with owner-approved packets. This revision will not write those files.

### Informational: project venv lacks `gt.exe`

Response: implementation and verification may use repository Python entry points and helper scripts. The missing `gt.exe` console script is not treated as a bridge blocker for this revised source/test scope.

### Already resolved: hook registration gap

Response: `bridge/gtkb-ops-lifecycle-protocol-foundation-hook-scope-amendment-004.md` is `VERIFIED`, confirming live/template hook recognition for `NO-ACTION`. This revision does not reopen the hook surface.

## Scope Changes

Removed from this thread:

- the two protected narrative artifacts named in the v004 `NO-GO` finding
- broad directory target entries such as `groundtruth-kb/src/groundtruth_kb/bridge`, `platform_tests/scripts`, and `groundtruth-kb/tests`

Added exact implementation targets:

- bridge parser/disposition/status surfaces under `groundtruth-kb/src/groundtruth_kb/bridge/`
- bridge writer and preflight/authorization scripts under `scripts/`
- Codex bridge helper parsers under `.codex/skills/bridge/helpers/`
- Loyal Opposition verdict writer helper under `.claude/skills/verify/helpers/`
- focused tests under `groundtruth-kb/tests/` and `platform_tests/scripts/`

Still out of scope:

- production deployment or credential lifecycle changes;
- Agent Red application source;
- lane-scoring registry/projection work, which belongs to WI-4958;
- AUQ/headless hook launch hygiene, which belongs to WI-4959;
- narrative artifact writes without formal approval packets.

## Architecture Alignment Ledger

| Axis | Alignment evidence |
| --- | --- |
| OPS consolidation | The revision implements the source/test portion of the OPS lifecycle status model while deferring protected narrative formalization to a governed approval path. |
| Dispatcher daemon architecture | The dispatcher daemon remains the control plane; revised targets update parser/actionability and dispatch eligibility surfaces rather than adding a harness-to-harness routing path. |
| Lifecycle-first/scoring-last precedence | `NO-ACTION`, sequence/quarantine, and status eligibility stay upstream of lane scoring. Lane scoring must consume already-eligible work only. |
| Portfolio reconciliation findings | Scope remains under `PROJECT-GTKB-OPS-LIFECYCLE-PROTOCOL-FOUNDATION` / `WI-4957` and does not absorb WI-4958, WI-4959, release-dispatcher, or runtime-orchestration work. |

## Pre-Filing Preflight Subsection

Candidate preflights to be executed by the revision helper before live filing:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ops-lifecycle-protocol-foundation --content-file <candidate> --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ops-lifecycle-protocol-foundation --content-file <candidate>`

Additional target coverage check to execute before implementation after any GO:

- `python scripts/impl_start_target_paths_preflight.py --bridge-id gtkb-ops-lifecycle-protocol-foundation --candidate-paths <exact implementation paths> --json`

## Verification Plan

| Slice | Governing surface | Verification |
| --- | --- | --- |
| Status vocabulary | `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Tests prove `NO-ACTION` is parsed by bridge detector/versioned-file/helper/script status readers and accepted by bridge writer authority rules. |
| Routing/actionability | `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | Tests prove latest `NO-ACTION` is LO-actionable, PB-non-actionable, and non-dispatchable to Prime implementation workers. |
| Fresh authority | `GOV-FILE-BRIDGE-AUTHORITY-001` | Tests prove prior `GO` under latest `NO-ACTION` is not PB-actionable and a later corrected `GO` is treated as fresh implementation authority. |
| Quarantine/circuit breaker readiness | `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused dispatcher/runtime tests cover status parsing, malformed-status quarantine compatibility, and diagnostic reason surfaces without production activation. |
| Clean implementation context | `ADR-DISPATCHER-ARCHITECTURE-001` | Tests/inspection prove ordinary bridge implementation context remains clean of OPS lineage except through audit/service-log/diagnostic surfaces. |
| Exact target governance | `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation-start target preflight must pass for every mutated source/test path before any protected mutation. |

Minimum implementation verification commands after GO:

- `python -m pytest groundtruth-kb/tests/test_bridge_detector.py groundtruth-kb/tests/test_bridge_routing.py groundtruth-kb/tests/test_bridge_status_driver.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_scan_bridge.py platform_tests/scripts/test_show_thread_bridge.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short`
- `python -m ruff check <touched-python-files>`
- `python -m ruff format --check <touched-python-files>`

## Risk And Rollback

Risk is moderate because status parsing/actionability touches bridge and dispatcher control surfaces. The revision mitigates that risk by narrowing to exact files, excluding protected narrative artifacts, and requiring source/test verification before any implementation report.

Rollback is a normal source/test revert for implementation files plus append-only bridge supersession. Bridge files and MemBase audit/version history must not be deleted.

## Loyal Opposition Asks

1. Review whether the exact target set is sufficient and no longer blocked by the narrative-artifact approval gate.
2. Confirm that the verified hook-scope amendment closes the hook-registration P2 and does not need to be reopened here.
3. Return `GO` if this narrowed source/test revision is implementable, otherwise return `NO-GO` with specific target-path or scope findings.
