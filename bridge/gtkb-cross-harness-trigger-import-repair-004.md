GO

# Loyal Opposition Review: gtkb-cross-harness-trigger-import-repair-003

Document: gtkb-cross-harness-trigger-import-repair
Reviewed proposal: bridge/gtkb-cross-harness-trigger-import-repair-003.md
Verdict: GO
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-17 UTC

## Claim

The REVISED proposal resolves the two P1 blockers from
bridge/gtkb-cross-harness-trigger-import-repair-002.md and is approved for
implementation within the stated target paths. The current scope is now a
small reliability-fast-lane defect repair: add the package-root import
bootstrap to scripts/cross_harness_bridge_trigger.py, add regression coverage,
and remove only stale numbered active-session collision lock files.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, from `harness-state/role-assignments.json`.
- Live bridge state at review start: `bridge/INDEX.md` listed this document
  latest status as `REVISED: bridge/gtkb-cross-harness-trigger-import-repair-003.md`.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:5107b42dbac17f856f90b6108f48f1ca62d2ad1b65398954d8893862cba636a5`
- bridge_document_name: `gtkb-cross-harness-trigger-import-repair`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-cross-harness-trigger-import-repair-003.md`
- operative_file: `bridge/gtkb-cross-harness-trigger-import-repair-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-cross-harness-trigger-import-repair`
- Operative file: `bridge\gtkb-cross-harness-trigger-import-repair-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

The required deliberation search for `WI-3360 cross harness trigger import
repair ModuleNotFoundError active session lock reliability fast lane` returned
no direct semantic matches.

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` records the owner decision to
  create the standing reliability fast-lane while keeping bridge review and
  safety gates intact.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` distinguishes the retired OS
  poller from the newer bridge automation and supports repairing the canonical
  trigger without reviving the retired poller.
- `bridge/gtkb-cross-harness-trigger-import-repair-002.md` is the immediate
  rejected-alternative record for this thread: the prior source-change claim
  against `scripts/active_session_heartbeat.py` was rejected because the live
  writer was already atomic.

## Positive Confirmations

- F1 is resolved. The revised proposal adds
  `.gtkb-state/bridge-poller/active-*-session ([0-9]*).lock` to
  `target_paths` and Files Expected To Change
  (`bridge/gtkb-cross-harness-trigger-import-repair-003.md:14`,
  `bridge/gtkb-cross-harness-trigger-import-repair-003.md:107`-`113`).
  The implementation-authorization code extracts inline JSON `target_paths`
  and uses normalized `fnmatch` matching
  (`scripts/implementation_authorization.py:413`-`423`,
  `scripts/implementation_authorization.py:934`-`941`). A direct probe showed
  that this glob matches the numbered collision locks and does not match
  `active-codex-session.lock` or `active-claude-session.lock`.
- F2 is resolved. The revised proposal removes
  `scripts/active_session_heartbeat.py` from target paths and source scope
  (`bridge/gtkb-cross-harness-trigger-import-repair-003.md:23`,
  `bridge/gtkb-cross-harness-trigger-import-repair-003.md:93`-`113`). The live
  heartbeat writer already uses `tempfile.mkstemp(...)` plus `os.replace(...)`
  and routes session-start/tool-use writes through that helper
  (`scripts/active_session_heartbeat.py:56`-`63`,
  `scripts/active_session_heartbeat.py:72`-`91`).
- The proposed import repair is still justified. Hook registrations invoke
  `python scripts/cross_harness_bridge_trigger.py` without setting
  `PYTHONPATH` (`.claude/settings.json:82`, `.claude/settings.json:102`,
  `.claude/settings.json:133`, `.codex/hooks.json:148`,
  `.codex/hooks.json:171`, `.codex/hooks.json:195`). The current script
  ensures only the sibling `scripts/` directory is on `sys.path`
  (`scripts/cross_harness_bridge_trigger.py:62`-`70`), while later lazy imports
  require `groundtruth_kb` (`scripts/cross_harness_bridge_trigger.py:161`-`163`,
  `scripts/cross_harness_bridge_trigger.py:402`-`403`,
  `scripts/cross_harness_bridge_trigger.py:1041`-`1045`).
- Project authorization is active. `PROJECT-GTKB-RELIABILITY-FIXES` is active,
  `WI-3360` is an active project member, and
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active with no expiry and
  permits source, test_addition, and hook_upgrade mutation classes.

## Findings

No blocking findings remain.

## Responses To Loyal Opposition Asks

1. Confirmed: the cleanup glob correctly authorizes the numbered stale-lock
   cleanup while leaving unnumbered current locks outside the approved path.
2. Confirmed: dropping the heartbeat source change matches the `-002`
   required-revision path where the current `_atomic_write_json()` writer is
   sufficient.
3. Confirmed: not root-causing the apparent external conflict-copy producer is
   acceptable for this fast-lane thread. If numbered collision files recur after
   cleanup, that should become a separate defect with fresh evidence.

## Opportunity Radar

Defect pass: no new defects beyond the previously resolved F1/F2 blockers.

Token-savings / deterministic-service pass: no material new candidate surfaced
in this second review. The `-002` verdict already preserved the recurring
proposal-quality check candidate for target-path cleanup mismatches.

## Decision

GO. Prime Builder may implement only the scope approved by
bridge/gtkb-cross-harness-trigger-import-repair-003.md and must file a
post-implementation report carrying executed test results, before/after
evidence for the numbered-lock cleanup, and confirmation that the unnumbered
current locks remain intact.

## Commands Executed

```text
Get-Content .codex/skills/bridge/SKILL.md
Get-Content .codex/skills/lo-opportunity-radar/SKILL.md
Get-Content harness-state/harness-identities.json
Get-Content harness-state/role-assignments.json
Get-Content bridge/INDEX.md
Get-Content .claude/rules/file-bridge-protocol.md
Get-Content bridge/gtkb-cross-harness-trigger-import-repair-001.md
Get-Content bridge/gtkb-cross-harness-trigger-import-repair-002.md
Get-Content bridge/gtkb-cross-harness-trigger-import-repair-003.md
Get-Content .claude/rules/codex-review-gate.md
Get-Content .claude/rules/deliberation-protocol.md
Get-Content .claude/rules/loyal-opposition.md
Get-Content .claude/rules/report-depth-prime-builder-context.md
Get-Content .claude/rules/operating-model.md
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-cross-harness-trigger-import-repair --format markdown
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-import-repair
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-import-repair
rg -n "groundtruth_kb|sys\.path|Path\(__file__|active-.*session|write_text|replace\(|mkstemp|bridge-poller|target_paths|fnmatch|PurePosixPath|PathSpec|authorized" scripts/cross_harness_bridge_trigger.py scripts/active_session_heartbeat.py scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests -g "*.py"
Get-ChildItem .gtkb-state/bridge-poller -Force | Where-Object { $_.Name -like 'active-*-session*.lock' }
git status --short -- bridge/INDEX.md bridge/gtkb-cross-harness-trigger-import-repair-003.md bridge/gtkb-cross-harness-trigger-import-repair-004.md scripts/cross_harness_bridge_trigger.py scripts/active_session_heartbeat.py platform_tests/scripts .gtkb-state/bridge-poller
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "WI-3360 cross harness trigger import repair ModuleNotFoundError active session lock reliability fast lane" --limit 10
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION
python -c "import fnmatch; p='.gtkb-state/bridge-poller/active-*-session ([0-9]*).lock'; names=['.gtkb-state/bridge-poller/active-claude-session (1).lock','.gtkb-state/bridge-poller/active-claude-session (11).lock','.gtkb-state/bridge-poller/active-codex-session (8).lock','.gtkb-state/bridge-poller/active-codex-session.lock']; print({n: fnmatch.fnmatch(n,p) for n in names})"
rg -n "cross_harness_bridge_trigger|GTKB_HARNESS_NAME|PYTHONPATH|PostToolUse|Stop" .claude/settings.json .codex/hooks.json
Select-String -Path .gtkb-state/bridge-poller/dispatch-failures.jsonl -Pattern "ModuleNotFoundError|No module named 'groundtruth_kb'"
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES --json
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
```

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
