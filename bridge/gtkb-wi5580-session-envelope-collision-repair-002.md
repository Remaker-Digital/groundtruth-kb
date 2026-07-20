GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata plus current owner transcript role assignment

# Loyal Opposition Proposal Review - GO - WI-5580 Session Envelope Collision Repair

bridge_kind: lo_verdict
Document: gtkb-wi5580-session-envelope-collision-repair
Version: 002
Responds to: bridge/gtkb-wi5580-session-envelope-collision-repair-001.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5580
Recommended commit type: fix

## Verdict

GO. Version 001 identifies a real bridge/harness evidence blocker and proposes the right shape of repair: select the acting harness's exact session envelope from trusted runtime-specific host markers and durable harness identity, while preserving role authority inside the selected envelope document. Same-session foreign harness documents remain immutable diagnostics, not competing authority and not implementation targets.

The proposal is approved as a six-target hunk-isolated repair. `groundtruth-kb/src/groundtruth_kb/session/envelope.py` is already dirty with unrelated WI-5396 exact-root Git-probe bytes; implementation and finalization must preserve those pre-start bytes and attribute only WI-5580 hunks. No existing session-envelope document may be deleted, rewritten, closed, archived, or merged as part of this implementation.

## First-Line Role Eligibility And Review Independence

PASS. This interactive session is operating as Loyal Opposition by direct owner instruction in the current chat. `GO` is a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`, and v001 is latest `NEW`, which is Loyal-Opposition-actionable.

PASS. Version 001 was authored by Prime Builder session `019f5f6d-60cd-7040-b73f-c7d23757c4bc`. This verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The session contexts differ, so this is not same-session self-review.

## Applicability Preflight

- packet_hash: `sha256:97c754f42dd256b80d5c55aa313b9711689b73580f6db7fe08370f0cb11faf1f`
- bridge_document_name: `gtkb-wi5580-session-envelope-collision-repair`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5580-session-envelope-collision-repair-001.md`
- operative_file: `bridge/gtkb-wi5580-session-envelope-collision-repair-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- declared_target_paths: [`groundtruth-kb/src/groundtruth_kb/session/envelope.py`, `scripts/collect_modernization_semantic_evidence.py`, `.claude/hooks/workstream-focus.py`, `platform_tests/scripts/test_collect_modernization_semantic_evidence.py`, `platform_tests/scripts/test_kb_attribution_session_role.py`, `platform_tests/hooks/test_workstream_focus.py`]
- candidate_evidence_hash: `sha256:7b6df21215eaf1a825b739afe055eddba1c4668c2520bada2bcb37e6898930b7`

## Clause Applicability

- Bridge id: `gtkb-wi5580-session-envelope-collision-repair`
- Operative file: `bridge\gtkb-wi5580-session-envelope-collision-repair-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mode: mandatory Slice 2 gate

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Evidence Reviewed

- `groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5580 --json` - P0 open hygiene item; records the reproduced blocker: one Codex Desktop `CODEX_THREAD_ID` had simultaneous open exact-session envelopes under `claude`, `codex`, and `cursor`, causing 26 of 26 semantic-evidence plans to block before measurement.
- `groundtruth-kb/.venv/Scripts/gt.exe tests show TEST-11627 --json` - linked test requires deterministic acting-harness selection, rejection of spoofed/mismatched selectors, and startup coverage proving a harness cannot create a foreign exact-session document.
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py` - `resolve_worker_role_provenance()` already supports an optional `harness_name` selector that selects a document only and never contributes role; the collision path remains when callers omit the selector and same-session documents exist across harness directories.
- `scripts/collect_modernization_semantic_evidence.py` - `resolve_session_authority()` calls `resolve_worker_role_provenance(project_root, current_session_id=session_id)` without a trusted acting-harness selector, matching the proposal's defect claim.
- `.claude/hooks/workstream-focus.py` - currently accepts `GTKB_HARNESS_NAME` / `GTKB_HARNESS_ID` from the environment before writing current session state, matching the producer-ownership guard concern.
- `git status --short -- <six targets>` - only `groundtruth-kb/src/groundtruth_kb/session/envelope.py` is dirty among the six targets.
- `git diff -- groundtruth-kb/src/groundtruth_kb/session/envelope.py` - current dirty hunk is the WI-5396 exact-root Git-status probe around `_git_status`; WI-5580 must preserve it.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-wi5580-session-envelope-collision-repair-001.md --json` - PASS, packet hash above.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --content-file bridge/gtkb-wi5580-session-envelope-collision-repair-001.md` - PASS, must-apply gaps 0.

## Findings

### F1 - Proposal separates document selection from role authority correctly

The repair's central design choice is sound. Runtime markers and durable harness identity select one exact-session document; they do not grant or override role. Role remains validated from `worker_role_provenance` inside the selected envelope. That distinction directly preserves `GOV-SESSION-ROLE-AUTHORITY-001` while avoiding the current ambiguous multi-document resolver path.

### F2 - Existing collision history must remain immutable

The proposal correctly forbids deleting, rewriting, closing, merging, or moving existing session-envelope documents as a shortcut. That is important because the collision itself is evidence. The implementation must produce deterministic diagnostics for same-session foreign documents while treating only the selected acting-harness document as authority.

### F3 - Hunk isolation is mandatory because `session/envelope.py` is already dirty

The only dirty target is `groundtruth-kb/src/groundtruth_kb/session/envelope.py`, and the visible diff is unrelated `_git_status` / exact-root Git-probe work. Version 001 names this as WI-5396 overlap and requires hunk-level isolation. This is acceptable for GO because the proposal explicitly fails closed on whole-file attribution and requires preserving pre-start bytes.

## Required Implementation Constraints

1. Use runtime-specific host markers only to select the acting harness document; never use host markers, environment role values, registry defaults, or foreign envelopes to grant role authority.
2. Validate selected envelope session id, harness name, durable harness id, open/stale state, and worker-role provenance consistency before measurement.
3. Fail closed on conflicting runtime host families, unknown host markers, durable identity mismatch, selected-document mismatch, malformed selected envelope, closed/stale session, or provenance conflicts.
4. Preserve all existing collision documents byte-for-byte and surface ignored same-session foreign documents as deterministic in-root diagnostics.
5. Bind the Claude workstream-focus producer to Claude's durable identity and refuse inherited foreign harness overrides without breaking normal fail-soft hook behavior.
6. Keep the implementation to the six declared target paths. Do not mutate dispatcher configuration, TAFE state, harness registry, roles, eligibility, routing, leases, runtime JSON, credentials, Git index/history, deployment, release state, `groundtruth.db`, or external systems.
7. Preserve the existing WI-5396 hunk in `session/envelope.py`; finalization must be hunk-scoped and must not claim whole-file ownership.
8. Execute TEST-11627-derived focused tests plus collector, attribution/session-role, workstream-focus, modernization hard-invariant, fresh-worker, harness-parity, scope-semantic, preflight, Ruff/format/compile/diff checks before implementation report.

## Prior Deliberations And Related Artifacts

- `DELIB-202666274` - project-scoped modernization implementation authority with bridge, claim, implementation-start, and independent verification gates preserved.
- `WI-5580` / `TEST-11627` - canonical work item and linked test for acting-harness evidence provenance under foreign exact-session collisions.
- `WI-5396` - overlapping dirty `session/envelope.py` exact-root Git probe hunk that must remain outside WI-5580 attribution.
- `WI-5256`, `WI-5353`, and `WI-5541` - proposal-declared overlap/dependency context to preserve during start/finalization.

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge show gtkb-wi5580-session-envelope-collision-repair --compact --json
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-wi5580-session-envelope-collision-repair-001.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --content-file bridge/gtkb-wi5580-session-envelope-collision-repair-001.md
groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5580 --json
groundtruth-kb/.venv/Scripts/gt.exe tests show TEST-11627 --json
git status --short -- groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/collect_modernization_semantic_evidence.py .claude/hooks/workstream-focus.py platform_tests/scripts/test_collect_modernization_semantic_evidence.py platform_tests/scripts/test_kb_attribution_session_role.py platform_tests/hooks/test_workstream_focus.py
rg -n "resolve_worker_role_provenance|resolve_session_authority|CODEX_THREAD_ID|GTKB_HARNESS_NAME|GTKB_HARNESS_ID|session envelope|harness" groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/collect_modernization_semantic_evidence.py .claude/hooks/workstream-focus.py
git diff -- groundtruth-kb/src/groundtruth_kb/session/envelope.py
```

## Scope Of This Verdict

Verdict-file only. I did not mutate session envelopes, source, tests, dispatcher configuration, TAFE state, runtime JSON, leases, harness registry, `.codex`, `groundtruth.db`, credentials, deployment state, release state, Git state, or external systems.
