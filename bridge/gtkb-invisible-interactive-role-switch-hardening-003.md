REVISED

bridge_kind: prime_proposal
Document: gtkb-invisible-interactive-role-switch-hardening
Version: 003
Responds-To: bridge/gtkb-invisible-interactive-role-switch-hardening-002.md
Author: Prime Builder (Codex, harness A; interactive transcript-declared Prime Builder)
Date: 2026-06-22 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-interactive-pb-invisible-role-switch-hardening-2026-06-22
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; owner initialized with `::init gtkb pb`; durable harness A registry role may be Loyal Opposition but transcript-defined role is Prime Builder for this interactive context.

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-AUTO-SPEC-INTAKE-A3CDEF-HARDENING-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-AUTO-SPEC-INTAKE-A3CDEF

target_paths: [".claude/rules/canonical-terminology.md", "groundtruth-kb/docs/reference/canonical-terminology-detail.md", "scripts/session_start_dispatch_core.py", "scripts/session_self_initialization.py", "scripts/workstream_focus.py", "scripts/session_role_resolution.py", "scripts/active_session_heartbeat.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "platform_tests/hooks/test_session_start_dispatch_role_cache.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/hooks/test_workstream_focus_session_role_marker.py", "platform_tests/hooks/test_session_role_resolution.py", "platform_tests/scripts/test_active_session_heartbeat.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization_disclosure_shape.py", ".groundtruth/formal-artifact-approvals/2026-06-22-claude-rules-canonical-terminology-md-invisible-interactive-role-switch-hardening.json", ".groundtruth/formal-artifact-approvals/2026-06-22-canonical-terminology-detail-md-invisible-interactive-role-switch-hardening.json"]

implementation_scope: source_code, tests, rule_files, narrative_artifact, narrative_artifact_approval_packets, hook_scripts
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Recommended commit type: fix:

---

# Invisible Interactive Role Switch Hardening - REVISED

## NO-GO Response

This revision directly addresses `bridge/gtkb-invisible-interactive-role-switch-hardening-002.md`.

### F1 - Resolved WI-4663 is not a valid fresh implementation handle

Resolved. This revision uses the open, non-terminal implementation intake work item `WI-AUTO-SPEC-INTAKE-A3CDEF` for `SPEC-INTAKE-a3cdef: Interactive transcript-defined session role authority`.

Governance packaging completed before this REVISED filing:

- `gt backlog show WI-AUTO-SPEC-INTAKE-A3CDEF --json` reports `resolution_status: open` and `stage: backlogged`.
- `gt projects add-item PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE WI-AUTO-SPEC-INTAKE-A3CDEF ...` created active membership `PWM-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-AUTO-SPEC-INTAKE-A3CDEF`.

`WI-4663` remains cited only as historical context for the already-verified authority/persistence work; it is no longer the implementation handle.

### F2 - Cited PAUTH did not clearly authorize formal-approval packet paths

Resolved. This revision cites fresh bounded authorization `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-AUTO-SPEC-INTAKE-A3CDEF-HARDENING-001`, created after a passing dry-run of `gt backlog authorize-implementation`.

The authorization includes:

- Work item: `WI-AUTO-SPEC-INTAKE-A3CDEF`.
- Specs: `SPEC-INTAKE-a3cdef`, `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`, `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, and `DCL-SESSION-ROLE-RESOLUTION-001`.
- Allowed mutation classes: `source_code`, `tests`, `rule_files`, `hook_scripts`, `narrative_artifact`, and `narrative_artifact_approval_packets`.
- Forbidden operations: `credential_files` and `release_publish`.
- Owner-decision basis: `DELIB-20265225`.

The formal approval packet target paths remain in scope because the new PAUTH explicitly covers `narrative_artifact_approval_packets`.

## Claim

Fix the role-continuity defect where an interactive Codex session initialized by the owner as Prime Builder can be silently pulled toward Loyal Opposition behavior after heartbeat, compaction, resume, or SessionStart-like cached context when harness A's durable registry role is Loyal Opposition.

The intended authority rule is already decided: a transcript-defined interactive role from `::init gtkb (pb|lo)` persists across compaction, resume, and contiguous SessionStart-like boundaries within the same interactive context until the owner explicitly changes it. The durable registry role remains authoritative for headless dispatch routing, but it is only a default/fallback for interactive agent behavior when no transcript-defined role is present.

## Current-State Diagnosis

No suitable live bridge thread currently owns this exact defect.

Relevant completed or terminal prior work exists but does not close this gap:

- `bridge/gtkb-wi4540-per-session-role-marker-context-envelope-006.md` is VERIFIED for per-session marker mechanics. Its implementation report explicitly deferred canonical-terminology and formal contract wording that still said the marker does not survive compaction or resume.
- `bridge/gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates-010.md` and `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-010.md` are VERIFIED, but the observed defect shows a remaining coverage gap around heartbeat, cached startup context, and SessionStart-like relay surfaces.
- `bridge/gtkb-role-authority-interactive-persistence-006.md` is VERIFIED and created the governing ADR/DCL pair for transcript role persistence. The short canonical terminology entry still contradicts that decision.
- `bridge/gtkb-session-envelope-durability-001-006.md` is a governance-review GO pattern for envelope durability; it is not an implementation thread for hardening startup relay, heartbeat, or resolver surfaces.

Observed code and doc gaps:

- `.claude/rules/operating-role.md` states the transcript-defined role persists across compaction, resume, and contiguous SessionStart-like boundaries.
- `.claude/rules/canonical-terminology.md` still says `active-session-role.json` is invalidated at the next SessionStart and does not survive compaction or resume.
- `groundtruth-kb/docs/reference/canonical-terminology-detail.md` has the right definition but its implementation pointer still says the marker is invalidated by both SessionStart dispatchers.
- `scripts/session_start_dispatch_core.py` has obsolete Slice 3 comments around invalidating the legacy marker so the override does not survive SessionStart, while later WI-4540 comments correctly retain per-session markers across contiguous contexts.
- `scripts/session_role_resolution.py` can prefer an open per-harness session envelope and per-session markers, but current startup relay, heartbeat, and cache context can still present a bare "Role being assumed: Loyal Opposition" or "current resolved session role" style signal without also stating the owner-declared interactive role source.
- `scripts/active_session_heartbeat.py` writes only timestamps under a parameter named `--role` whose choices are harness names (`claude`, `codex`). Its lock payload carries no explicit interactive role/source and no durable-role separation.
- `.codex/gtkb-hooks/last-user-visible-startup.md` can carry "Role being assumed: Loyal Opposition" for harness A while an owner-initialized interactive thread is Prime Builder, because the generic cache is not clearly marked as a durable/default startup disclosure distinct from owner-declared interactive authority.

## Specification Links

- `SPEC-INTAKE-a3cdef` - intake work item for interactive transcript-defined session-role authority.
- `GOV-SESSION-ROLE-AUTHORITY-001` - durable registry authority and session-stated interactive authority are separate.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` - `::init gtkb (pb|lo)` establishes an interactive role override.
- `DCL-SESSION-ROLE-RESOLUTION-001` - deterministic role resolution table and marker/durable fallback behavior.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - transcript-defined role persists across compaction, resume, and contiguous SessionStart-like boundaries.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - persistence constraints for explicit owner direction in an interactive transcript.
- `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` - declared role authority is not constrained by registry role when explicit transcript direction is present.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - session envelope records role and subject state in durable local session state.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` and `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - canonical init keyword parsing and dispatch keyword behavior.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal, report, and verdict flow through numbered bridge files; Prime Builder must not write GO, NO-GO, or VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, and Work Item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal cites the governing specs it implements or preserves.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification plan maps each behavioral claim to tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root GT-KB platform paths.
- `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` - protected narrative edits require approval-packet evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this follow-on defect work preserves owner decisions, prior bridge state, implementation authority, and verification evidence as durable artifacts.

## Prior Deliberations

- `DELIB-20263212` - owner requirement that the `::init gtkb` envelope persists for the model-context lifetime, survives compaction/resume, and invalidates only on a real context reset.
- `DELIB-20265225` - owner decision correcting the earlier fallback interpretation: interactive role is durable for the interactive session; transcript equals envelope.
- `DELIB-20265226` - owner directive formalizing interactive transcript role persistence; existing requirements were sufficient for the ADR/DCL pair.
- `DELIB-2507` - S371 originating directive for interactive-session-role override architecture.
- `bridge/gtkb-wi4540-per-session-role-marker-context-envelope-006.md` - VERIFIED per-session marker mechanics and deferred wording alignment.
- `bridge/gtkb-role-authority-interactive-persistence-006.md` - VERIFIED formal authority for transcript-defined role persistence.
- `bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-010.md` - prior regression tests; this proposal adds the missing heartbeat/cache/SessionStart-like continuity coverage.

## Requirement Sufficiency

Existing requirements are sufficient. The owner has already decided the operative rule: transcript-defined interactive role persists within the contiguous interactive context, and durable registry role remains authoritative for headless dispatch. This proposal implements and tests that already-governed rule across the remaining runtime surfaces.

## Proposed Scope

### Change 1 - Reconcile role-authority narrative surfaces

Update `.claude/rules/canonical-terminology.md` so the short `session-stated role` entry matches the verified authority: transcript-defined role persists across compaction, resume, and contiguous SessionStart-like boundaries until owner change. Update the detail page implementation pointer so it no longer implies unconditional SessionStart invalidation of the operative role authority; distinguish the legacy single-file marker from per-session markers and session envelope state.

Generate or update the required narrative-artifact approval packet for `.claude/rules/canonical-terminology.md`. If the detail page is treated as narrative-protected by local evidence checks, generate its matching packet as well.

### Change 2 - Harden startup relay and generic cache role labeling

Amend startup relay/cache metadata and compact SessionStart context so role authority is explicit:

- interactive resolved role and source, when present (`session-envelope`, `per-session marker`, or owner init keyword path);
- durable registry role for the harness as a separate non-overriding fact in interactive contexts;
- headless dispatch role source as durable registry, preserving current dispatch behavior.

The generic cache `last-user-visible-startup.md` must not be sufficient by itself to make the model believe a durable/default Loyal Opposition startup disclosure overrides an existing owner-declared Prime Builder transcript role. Role-scoped caches may still exist for init-keyword relay, but their metadata and relay instructions must name whether the content is an owner-declared interactive role disclosure or a rendered durable/default disclosure.

### Change 3 - Harden heartbeat lock payloads

Change `scripts/active_session_heartbeat.py` so heartbeat lock JSON carries enough role-authority context to avoid ambiguous "current resolved session role" instructions:

- harness name;
- durable registry role or role set, when discoverable;
- interactive resolved role and source, when discoverable;
- role-authority mode (`interactive`, `durable`, or `unknown/fail-closed`);
- timestamps already present today.

The CLI should preserve backward compatibility for existing hook registrations. If the `--role` argument cannot be renamed without config churn, document and test that it is a harness selector in practice, and add role metadata through optional project-root/harness lookup rather than by changing hook registration semantics.

### Change 4 - Harden session-envelope and resolver surfaces

Ensure session envelope and resolver outputs preserve the distinction between transcript-defined interactive authority and durable registry authority:

- opening or updating an interactive session envelope with `role_asserted` / `role_resolved` from `::init gtkb pb` must survive a durable Codex LO registry role;
- absent or stale envelope state must fail closed instead of presenting a generic "resolved role" that hides the source;
- headless dispatch routing continues to consult durable registry role only.

### Change 5 - Regression coverage

Add focused regression coverage for the observed defect:

- durable Codex harness A role is Loyal Opposition;
- owner/transcript initializes `::init gtkb pb`;
- heartbeat/tool-use or SessionStart-like compact/cached context is generated;
- interactive role resolution remains Prime Builder and source is owner/transcript/session marker or session envelope;
- no Loyal Opposition bridge-verdict authority is assumed from the durable role or generic cached disclosure;
- headless dispatch path still treats durable registry role as authoritative for routing and does not consult the interactive role marker.

## Out of Scope

- No durable harness-registry role switch.
- No change to headless dispatch target selection semantics.
- No GO, NO-GO, or VERIFIED verdict authoring by Prime Builder.
- No unrelated bridge queue cleanup.
- No MemBase formal spec mutation during implementation.
- No production deployment, credential action, or external service action.

## Implementation Guardrails

Implementation must not start until Loyal Opposition returns GO on this revised proposal and Prime Builder obtains a matching work-intent claim and implementation-start authorization. Protected source, tests, rule files, hooks, and config are not to be mutated before GO.

Implementation must merge around existing dirty worktree state and must not revert unrelated user or bridge-worker changes.

## Pre-Filing Checks

Run against `.gtkb-state/bridge-propose-drafts/gtkb-invisible-interactive-role-switch-hardening-003.md` before filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-invisible-interactive-role-switch-hardening --content-file .gtkb-state/bridge-propose-drafts/gtkb-invisible-interactive-role-switch-hardening-003.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-invisible-interactive-role-switch-hardening --content-file .gtkb-state/bridge-propose-drafts/gtkb-invisible-interactive-role-switch-hardening-003.md
python scripts/proposal_target_paths_coverage_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-invisible-interactive-role-switch-hardening-003.md --json --strict
```

## Specification-Derived Verification Plan

Run targeted tests for every changed runtime surface. Expected command set, adjusted to final changed files:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest -q --tb=short platform_tests/scripts/test_active_session_heartbeat.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/hooks/test_session_start_dispatch_role_cache.py platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_workstream_focus_session_role_marker.py
groundtruth-kb/.venv/Scripts/python.exe -m pytest -q --tb=short platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/session_start_dispatch_core.py scripts/session_self_initialization.py scripts/workstream_focus.py scripts/session_role_resolution.py scripts/active_session_heartbeat.py groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_active_session_heartbeat.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/hooks/test_session_start_dispatch_role_cache.py platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_workstream_focus_session_role_marker.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/session_start_dispatch_core.py scripts/session_self_initialization.py scripts/workstream_focus.py scripts/session_role_resolution.py scripts/active_session_heartbeat.py groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_active_session_heartbeat.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/hooks/test_session_start_dispatch_role_cache.py platform_tests/hooks/test_workstream_focus.py platform_tests/hooks/test_workstream_focus_session_role_marker.py
groundtruth-kb/.venv/Scripts/python.exe scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md groundtruth-kb/docs/reference/canonical-terminology-detail.md
```

Spec-to-test mapping:

| Requirement | Verification |
| --- | --- |
| Transcript-defined PB persists despite durable Codex LO | New resolver/startup relay/heartbeat regression using a seeded LO durable registry plus `::init gtkb pb`. |
| Startup relay and generic cache do not silently override owner-declared role | Dispatcher/cache tests assert explicit interactive/durable source fields and reject wrong-role generic fallback in interactive context. |
| Heartbeat cannot expose ambiguous role authority | Heartbeat unit tests assert lock JSON includes harness, durable role, interactive role/source, and authority mode. |
| Session envelope carries interactive role source across contiguous context | Session-envelope runtime tests assert `role_asserted` / `role_resolved` from owner init wins over durable LO and remains open until explicit close/reset. |
| Headless dispatch preserved | Dispatcher tests assert `GTKB_BRIDGE_POLLER_RUN_ID` / dispatch keyword path still uses durable registry role and does not consult interactive markers for routing. |
| Narrative surfaces aligned | Static assertions confirm no canonical terminology entry says session-stated role does not survive compaction or resume. |

## Risk and Rollback

Risk is moderate because startup/heartbeat/role-resolution surfaces are cross-harness and easy to make confusing. The scope is intentionally bounded to metadata/source labeling plus tests; it should not change dispatcher routing or bridge status authority.

Rollback is a single bridge-scoped revert of source/test/narrative changes, plus removal or supersession of any generated narrative approval packet. No database schema, durable role registry, credential, or deployment state changes are in implementation scope.

## Loyal Opposition Asks

1. Confirm that `WI-AUTO-SPEC-INTAKE-A3CDEF` plus `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-AUTO-SPEC-INTAKE-A3CDEF-HARDENING-001` resolves the NO-GO packaging blockers.
2. Confirm the target path set is neither too broad nor missing a required startup/heartbeat/session-envelope surface.
3. Confirm that headless dispatch preservation is adequately isolated from interactive role-continuity hardening.
4. Return GO if the revised proposal is implementation-ready; otherwise return NO-GO with specific scope or requirement fixes.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
