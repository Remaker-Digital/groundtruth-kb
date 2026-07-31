GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Loyal Opposition; transcript-defined LO role; CODEX_THREAD_ID=019f7815-a565-78d3-a599-dec8388086ff; sandbox=danger-full-access; approval_policy=never
author_metadata_source: x-codex-turn-metadata plus current owner transcript role assignment

# Loyal Opposition Proposal Review - GO - WI-5639 Scan Helper Exact Numbered Chain Fallback

bridge_kind: lo_verdict
Document: gtkb-wi5639-scan-helper-exact-numbered-chain-fallback
Version: 002
Responds to: bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-001.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5639

## Verdict

GO for the narrow scan-helper compatibility repair proposed in `bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-001.md`.

The proposal is appropriately scoped to the two managed scan-helper copies and addresses a live regression in the synthetic inline-GO compatibility path: the current helpers recognize only `Bridge document not found as versioned files`, while the live resolver now reports `Bridge document not found as exact numbered files`. The implementation authority remains limited to:

- `.claude/skills/bridge/helpers/scan_bridge.py`
- `.codex/skills/bridge/helpers/scan_bridge.py`

This GO does not authorize changes to `scripts/implementation_authorization.py`, `scripts/bridge_lifecycle_resolver.py`, protected-commit authorization, dispatcher/TAFE configuration, Git/index/ref state, provider runtime, harness runtime, MemBase, or tests. The implementation report must show both managed helper copies remain byte-identical after the change.

## First-Line Role Eligibility And Review Independence

PASS. This interactive session is explicitly operating as Loyal Opposition by owner instruction in the current chat. `GO` is a Loyal Opposition verdict status under `GOV-FILE-BRIDGE-AUTHORITY-001`, and version 001 is latest `NEW`, which is Loyal-Opposition-actionable as a proposal awaiting review.

PASS. Version 001 was authored by Prime Builder session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`. This verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The session contexts differ, so this is not same-session self-review.

## Applicability Preflight

- packet_hash: `sha256:5a83eba7c452a80732292f5cb1e0c6c52c6b219c3c08f82cfabd30416e3824da`
- bridge_document_name: `gtkb-wi5639-scan-helper-exact-numbered-chain-fallback`
- declared_target_paths: [".claude/skills/bridge/helpers/scan_bridge.py", ".codex/skills/bridge/helpers/scan_bridge.py"]
- applicability_path_evidence: [".claude/skills/bridge/helpers/scan_bridge.py", ".claude/skills/bridge/helpers/scan_bridge.py`", ".claude/skills/bridge/helpers/scan_bridge.py`,", ".codex/skills/bridge/helpers/scan_bridge.py", ".codex/skills/bridge/helpers/scan_bridge.py`", ".codex/skills/bridge/helpers/scan_bridge.py`.", "platform_tests/scripts/test_scan_bridge.py"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-001.md`
- operative_file: `bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- candidate_evidence_hash: `sha256:7201019fb9cb2018563896bbdb3ef186241a1895373877199c6cd6b28ad60eb4`

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability

- Bridge id: `gtkb-wi5639-scan-helper-exact-numbered-chain-fallback`
- Operative file: `bridge\gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Prior Deliberations

- `DELIB-2503` - S373 Scanner-Fix Vehicle + PAUTH Owner-Decision Chain. Relevant because the WI-5639 proposal cites project authorization and scanner-fix vehicle context.
- `DELIB-20265389` - Verdict for `gtkb-wi4618-non-activatable-go-scan-reconciliation`. Relevant because WI-5639 preserves the WI-4618 synthetic inline-GO compatibility behavior.
- `DELIB-202666024` - Verification Verdict for `gtkb-wi5068-no-action-scan-helper-parser`. Relevant because it concerns scan-helper parser behavior and bridge actionability.

## Evidence Reviewed

- Live LO scan at `2026-07-19T17:43:58Z` listed `gtkb-wi5639-scan-helper-exact-numbered-chain-fallback` latest `NEW` at `bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-001.md`.
- `gt bridge show gtkb-wi5639-scan-helper-exact-numbered-chain-fallback --json --compact` reported latest status `NEW`, latest path `bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-001.md`, version count 1, and no drift.
- `bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-001.md` lines 19-24 declare PAUTH, project, work item, and exact target paths.
- `bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-001.md` lines 76-80 limit scope to adding the current missing-chain message to the synthetic compatibility predicate, keeping both managed helper copies identical, and preserving fail-closed behavior for real malformed or unauthorized GO chains.
- `bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-001.md` lines 154-175 provide the spec-derived verification plan and acceptance criteria.
- `.claude/skills/bridge/helpers/scan_bridge.py` and `.codex/skills/bridge/helpers/scan_bridge.py` currently contain the legacy fallback predicate at lines 423-433, including `Bridge document not found as versioned files` and fail-open handling only for the narrow synthetic missing-chain/inline-GO cases.
- `certutil -hashfile` reported both managed helper copies at SHA256 `19c809bd2e47003577451121e9bc6830c2dd14c8043d16a26d1a77c52d143f47`, confirming current byte parity.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_scan_bridge.py -q --tb=short --timeout=120` currently fails 5 scan-helper tests and passes 27, matching the proposal's claimed regression shape.

## Implementation Constraints

1. Add only the exact current resolver wording needed for synthetic missing-numbered-chain compatibility, while retaining the legacy wording during migration.
2. Do not broad-match arbitrary authorization failures; real malformed, unauthorized, stale, or protected-path-denied GO chains must remain `blocked_non_activatable`.
3. Keep `.claude/skills/bridge/helpers/scan_bridge.py` and `.codex/skills/bridge/helpers/scan_bridge.py` byte-identical.
4. Do not mutate tests, dispatcher/TAFE configuration, `scripts/implementation_authorization.py`, `scripts/bridge_lifecycle_resolver.py`, protected-commit authorization, Git/index/ref state, provider runtime, harness runtime, or MemBase under this GO.
5. The post-implementation report should use recommended commit type `fix`, not `feat`, because this is a regression repair with no new user-facing capability surface.

## Verification Expectations

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_scan_bridge.py -q --tb=short --timeout=120`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check .claude\skills\bridge\helpers\scan_bridge.py .codex\skills\bridge\helpers\scan_bridge.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check .claude\skills\bridge\helpers\scan_bridge.py .codex\skills\bridge\helpers\scan_bridge.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m py_compile .claude\skills\bridge\helpers\scan_bridge.py .codex\skills\bridge\helpers\scan_bridge.py`
- Hash or `git diff --no-index -- .claude\skills\bridge\helpers\scan_bridge.py .codex\skills\bridge\helpers\scan_bridge.py` evidence proving byte-identical managed helpers.

## Owner Action Required

None.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
