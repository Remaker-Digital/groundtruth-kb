GO

# Loyal Opposition GO Verdict - WI-4364 Codex Skill Path Prefers Repo-Local Adapters

bridge_kind: lo_verdict
Document: gtkb-codex-skill-path-prefers-repo-local-adapters
Version: 002
Author: Loyal Opposition (Codex, harness A)
Reviewer: Loyal Opposition
Date: 2026-06-21 UTC
Responds to: bridge/gtkb-codex-skill-path-prefers-repo-local-adapters-001.md
Recommended commit type: fix:

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: gtkb-reliability-fixes-review-watch-2026-06-21T10-41-45Z
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex heartbeat Loyal Opposition proposal review; PROJECT-GTKB-RELIABILITY-FIXES watch

## Verdict

GO.

The proposal is narrowly scoped and addresses a real startup-discovery gap: repo-local `.codex/skills` adapters are not preferred by `_discover_skill_files`, while the generated startup payload exposes only user-extension discovery. The bridge metadata, target paths, requirement sufficiency, owner-input evidence, and spec-derived tests are present, and both mandatory preflights pass.

Declared target paths:

- `scripts/session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization.py`

## First-Line Role Eligibility Check

- Command: `groundtruth-kb/.venv/Scripts/gt.exe harness roles`
- Result: harness `A` (`codex`) has active role `[loyal-opposition]`.
- Latest bridge state before this verdict: `NEW` at `bridge/gtkb-codex-skill-path-prefers-repo-local-adapters-001.md`.
- Status authored here: `GO`.
- Eligibility result: Loyal Opposition is authorized to respond to latest `NEW` proposals with `GO` or `NO-GO`.

## Independence Check

- Proposal author: Prime Builder / Claude harness B.
- Proposal author session: `96b4ab64-e440-47b7-8c81-cd55bc7a5c1e`.
- Reviewer session: `gtkb-reliability-fixes-review-watch-2026-06-21T10-41-45Z`.
- Result: unrelated author/reviewer session contexts; no same-session self-review risk.

## Applicability Preflight

- packet_hash: `sha256:38fd9dbde6459fde01cba90835a8234d05fffbc4a00581cd2ccfef54ffee018c`
- bridge_document_name: `gtkb-codex-skill-path-prefers-repo-local-adapters`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-codex-skill-path-prefers-repo-local-adapters-001.md`
- operative_file: `bridge/gtkb-codex-skill-path-prefers-repo-local-adapters-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability

- Bridge id: `gtkb-codex-skill-path-prefers-repo-local-adapters`
- Operative file: `bridge\gtkb-codex-skill-path-prefers-repo-local-adapters-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | â€” | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | â€” | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> â€” <DELIB-ID> â€” <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

- `DELIB-20265355` (work item WI-4544) - Loyal Opposition Review - Environment-Access Escalation - gtkb-propose-scaffold-invalid-bridge-kind - 020.
- `DELIB-20265246` (work item WI-4623) - Loyal Opposition Verification - Harness Hook Path CWD Robustness.
- `DELIB-20263210` (work item WI-4542) - Owner decision: authorize WI-4542 (bridge applicability-preflight SPEC_LINK heading-qualifier fix) under reliability-fixes PAUTH.
- Current DA search for `WI-4364 gtkb-codex-skill-path-prefers-repo-local-adapters PROJECT-GTKB-RELIABILITY-FIXES` found the above context and no contrary owner decision blocking this verdict.

## Proposal Checks

| Gate | Evidence | Result |
|---|---|---|
| Project linkage | Project Authorization / Project / Work Item metadata present near the top of the proposal | PASS |
| Parser-readable target paths | `target_paths` is present for `scripts/session_self_initialization.py` and its platform test | PASS |
| Live source fit | `scripts/session_self_initialization.py` currently scans `.claude/skills` plus opt-in home skill roots, not repo-local `.codex/skills` as a preferred adapter source | PASS |
| Spec-derived tests | Verification plan covers repo-local adapter preference and startup payload disclosure/fallback behavior | PASS |

## Findings

No blocking findings.

## GO Conditions

- Keep the change limited to startup skill discovery and its platform tests.
- Do not change global user-extension semantics beyond the declared repo-local preference/fallback behavior.

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/gt.exe harness roles
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json
Get-Content bridge/gtkb-codex-skill-path-prefers-repo-local-adapters-001.md
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-codex-skill-path-prefers-repo-local-adapters
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-codex-skill-path-prefers-repo-local-adapters
groundtruth-kb/.venv/Scripts/gt.exe deliberations search "WI-4364 gtkb-codex-skill-path-prefers-repo-local-adapters PROJECT-GTKB-RELIABILITY-FIXES" --limit 3 --json
```

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
