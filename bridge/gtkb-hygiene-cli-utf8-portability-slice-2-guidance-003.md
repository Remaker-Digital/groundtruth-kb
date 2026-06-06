GO

bridge_kind: review_verdict
Document: gtkb-hygiene-cli-utf8-portability-slice-2-guidance
Version: 003
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-06 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-002.md

# Loyal Opposition Review - Hygiene CLI UTF-8 + Portability Slice 2 Guidance

## Verdict

GO.

The REVISED proposal is ready for implementation. It corrects the version 001
author-metadata mismatch, carries the active project authorization and WI-4250
owner-decision evidence, cites the relevant bridge, backlog, project
authorization, in-root, artifact-oriented, and deterministic-services
specification surfaces, and includes a focused spec-derived verification plan.

Prime Builder may implement only inside the declared target paths:

- `.claude/skills/gtkb-hygiene-sweep/SKILL.md`
- `.codex/skills/gtkb-hygiene-sweep/SKILL.md`
- `.codex/skills/MANIFEST.json`
- `platform_tests/scripts/test_hygiene_sweep_skill.py`

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:8f278f4c593d30e7337b346047298880cdf6643168ee0affc440d992c13fdbcb`
- bridge_document_name: `gtkb-hygiene-cli-utf8-portability-slice-2-guidance`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-002.md`
- operative_file: `bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-002.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-hygiene-cli-utf8-portability-slice-2-guidance`
- Operative file: `bridge\gtkb-hygiene-cli-utf8-portability-slice-2-guidance-002.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

Deliberation searches and reads were run before review:

```text
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "hygiene CLI UTF-8 portability WI-4250 Slice 2 guidance DELIB-20260630" --limit 8 --json
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations list --work-item-id WI-4250 --json
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-20260630 --json
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-20260623 --json
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE --json
```

Relevant records:

- `DELIB-20260630` - owner authorized WI-4250 Slice 2 fallback guidance and the
  doc-class PAUTH amendment covering WI-4250 and WI-4259.
- `DELIB-20260623` - owner authorized the remaining deterministic-services work
  and sequenced the hygiene cluster after the operational-load CLIs.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - supports moving repeated
  operator routing and command fallback knowledge into durable deterministic
  surfaces rather than session memory.
- `DELIB-20260737` and `DELIB-20260736` - Slice 1 GO and VERIFIED records for
  WI-4250 CLI UTF-8 and module-entrypoint fallback mechanics.

No retrieved deliberation contradicts the proposed Slice 2 guidance closure.

## Positive Confirmations

- Live `bridge/INDEX.md` showed latest `REVISED` for this document before
  filing this verdict, and `show_thread_bridge.py` reported no drift.
- The mandatory applicability preflight passed with `missing_required_specs: []`
  and `missing_advisory_specs: []`.
- The mandatory clause preflight passed with zero evidence gaps in must-apply
  clauses and zero blocking gaps.
- `gt projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` and
  `gt projects authorizations PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json`
  show active PAUTH
  `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER`; its version 2
  includes `WI-4250` and allows `documentation`, `test_addition`,
  `config_change`, and `source` while forbidding deployment, spec status
  promotion, and CLI extension.
- The revised target path list includes `.codex/skills/MANIFEST.json`, which is
  the generated adapter-manifest side effect that prior hygiene-skill review
  history showed must be explicit when the adapter generator changes manifest
  entries.
- The proposal keeps `groundtruth-kb/src/groundtruth_kb/cli.py` out of scope
  because Slice 1 already VERIFIED the runtime UTF-8 stream fix.
- Current live skill text already includes the required fallback wording in both
  the canonical `.claude` skill and generated Codex adapter.

## Focused Verification Run During Review

These commands were run as read-only review checks because the proposal states
the guidance may already exist and implementation may be a confirmation/no-op
plus regression evidence:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_hygiene_sweep_skill.py -q --tb=short
```

Observed result:

```text
9 passed, 1 warning in 0.13s
```

The warning was an existing pytest cache path creation warning:
`PytestCacheWarning: could not create cache path ... .pytest_cache ... [WinError 183]`.
It does not affect the focused test result.

```text
python scripts\generate_codex_skill_adapters.py --update-registry --check
```

Observed result:

```text
Codex skill adapters: PASS (34 adapters current)
```

## Findings

No blocking findings.

## Advisory Notes

- `gt backlog show WI-4250 --json` still reports `approval_state: unapproved`,
  while the active PAUTH and owner-decision DELIB authorize this implementation
  slice. Prime Builder should cite the PAUTH and owner-decision evidence, not the
  backlog `approval_state`, as implementation authority.
- If implementation is a no-op or near-no-op because the guidance and regression
  already exist, the post-implementation report should say that plainly and
  still provide the exact spec-derived command evidence from this proposal's
  verification plan.

## Opportunity Radar

No separate advisory is needed. This proposal is itself a small
deterministic-services/read-surface closure: it moves recurring command fallback
knowledge into the hygiene skill and pins it with tests. The remaining human
judgment is only whether the post-implementation report proves the linked
specifications against live commands.

## Prime Builder Implementation Context

Prime Builder may implement the approved plan after opening an implementation
authorization packet from this live latest `GO` entry:

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance
```

The implementation report must carry forward the linked specifications and run
the planned checks, at minimum:

```text
python -m pytest platform_tests/scripts/test_hygiene_sweep_skill.py -q --tb=short
python scripts/generate_codex_skill_adapters.py --update-registry --check
python -m pytest groundtruth-kb/tests/test_cli_utf8_portability.py -q --tb=short
python -m pytest platform_tests/scripts/test_hygiene_sweep_cli.py groundtruth-kb/tests/test_hygiene_sweep_patterns.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance
```

## Commands Executed

```text
Get-Content -Raw bridge\INDEX.md
Get-Content -Raw harness-state\harness-identities.json
Get-Content -Raw harness-state\harness-registry.json
Get-Content -Raw .codex\skills\bridge\SKILL.md
Get-Content -Raw .codex\skills\proposal-review\SKILL.md
Get-Content -Raw .codex\skills\lo-opportunity-radar\SKILL.md
Get-Content -Raw .claude\rules\file-bridge-protocol.md
Get-Content -Raw .claude\rules\codex-review-gate.md
Get-Content -Raw .claude\rules\deliberation-protocol.md
Get-Content -Raw .claude\rules\operating-model.md
Get-Content -Raw .claude\rules\loyal-opposition.md
Get-Content -Raw .claude\rules\report-depth-prime-builder-context.md
Get-Content -Raw bridge\gtkb-hygiene-cli-utf8-portability-slice-2-guidance-002.md
Get-Content -Raw bridge\gtkb-hygiene-cli-utf8-portability-slice-2-guidance-001.md
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-hygiene-cli-utf8-portability-slice-2-guidance --format json --preview-lines 1000
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "hygiene CLI UTF-8 portability WI-4250 Slice 2 guidance DELIB-20260630" --limit 8 --json
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations list --work-item-id WI-4250 --json
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-20260630 --json
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-20260623 --json
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE --json
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-4250 --json
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects authorizations PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json
rg -n "python -m groundtruth_kb hygiene sweep|PYTHONPATH=groundtruth-kb/src|gt hygiene sweep|test_hygiene_sweep_skill" .claude\skills\gtkb-hygiene-sweep\SKILL.md .codex\skills\gtkb-hygiene-sweep\SKILL.md platform_tests\scripts\test_hygiene_sweep_skill.py .codex\skills\MANIFEST.json
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_hygiene_sweep_skill.py -q --tb=short
python scripts\generate_codex_skill_adapters.py --update-registry --check
```

Selected-entry handling note: `gtkb-startup-control-vocabulary-map` became latest
`GO` while this review was in progress, so this auto-dispatch skipped it as
stale for Loyal Opposition and processed only this still-actionable `REVISED`
entry.

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
