NO-GO

# Loyal Opposition Review: gtkb-cross-harness-trigger-import-repair-001

Document: gtkb-cross-harness-trigger-import-repair
Reviewed proposal: bridge/gtkb-cross-harness-trigger-import-repair-001.md
Verdict: NO-GO
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-17 UTC

## Claim

The proposal is directionally correct on the trigger import defect, and the live
failure log supports the `ModuleNotFoundError: No module named 'groundtruth_kb'`
claim. It cannot receive GO as filed because its implementation scope and
authorization metadata do not cover one of its acceptance criteria, and its
active-session-heartbeat current-state claim is contradicted by the live source.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, from `harness-state/role-assignments.json`.
- Live bridge state at review start: `bridge/INDEX.md` listed this document
  latest status as `NEW: bridge/gtkb-cross-harness-trigger-import-repair-001.md`.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:648f2a6b892dbf1ee618e4a5bda5b6417cd458f4038b67ce454491f2e7ce1283`
- bridge_document_name: `gtkb-cross-harness-trigger-import-repair`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-cross-harness-trigger-import-repair-001.md`
- operative_file: `bridge/gtkb-cross-harness-trigger-import-repair-001.md`
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
- Operative file: `bridge\gtkb-cross-harness-trigger-import-repair-001.md`
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
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

The default Python environment could not run the MemBase CLI because `click`
is absent there, so I used the repo venv for the required read-only checks.

- Semantic search for `WI-3360 cross harness trigger import repair
  ModuleNotFoundError active session lock reliability fast lane` returned no
  direct deliberation matches.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` records the owner decision to
  build `PROJECT-GTKB-RELIABILITY-FIXES`,
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, and
  `GOV-RELIABILITY-FAST-LANE-001` for small reliability defects while keeping
  bridge review and safety gates intact.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` confirms the old OS poller
  remains retired and that the newer bridge automation is acceptable when
  functional. This proposal repairs the event-driven trigger; it does not
  revive the retired OS poller.
- `bridge/gtkb-bridge-active-session-autodrain-002.md` finding F2 directed the
  import repair and lock cleanup into a separate reliability-fast-lane thread.

## Positive Confirmations

- The live dispatch failure log contains the cited import failure:
  `.gtkb-state/bridge-poller/dispatch-failures.jsonl:16078` records
  `ModuleNotFoundError` with message `No module named 'groundtruth_kb'` at
  `2026-05-17T03:46:50+00:00`.
- The proposal cites the reliability fast-lane spec and maps the four
  fast-lane eligibility criteria.
- Read-only project checks show
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, has no expiry,
  allows `source`, `test_addition`, and `hook_upgrade`, and covers
  `PROJECT-GTKB-RELIABILITY-FIXES` by active project membership.
- Read-only project checks show `WI-3360` is an active member of
  `PROJECT-GTKB-RELIABILITY-FIXES`.
- The proposal includes Specification Links, Prior Deliberations, Owner
  Decisions / Input, Requirement Sufficiency, a spec-to-test mapping,
  acceptance criteria, and rollback notes.

## Findings

### F1 - P1 - `target_paths` omits the runtime-state cleanup path

Observation:

The proposal's `target_paths` line authorizes only
`scripts/cross_harness_bridge_trigger.py`, `scripts/active_session_heartbeat.py`,
and `platform_tests/scripts/**`. The same proposal requires IP-3 to remove
numbered active-session lock files under `.gtkb-state/bridge-poller/` and makes
that cleanup an acceptance criterion.

Evidence:

- `bridge/gtkb-cross-harness-trigger-import-repair-001.md:14` declares
  `target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/active_session_heartbeat.py", "platform_tests/scripts/**"]`.
- `bridge/gtkb-cross-harness-trigger-import-repair-001.md:77-79` requires
  removing accumulated `active-*-session (N).lock` files under
  `.gtkb-state/bridge-poller/`.
- `bridge/gtkb-cross-harness-trigger-import-repair-001.md:123` makes that
  removal an acceptance criterion.
- `.claude/rules/file-bridge-protocol.md:40-42` requires implementation
  proposals that request repository-state work to include `target_paths`
  listing the concrete files or globs authorized for implementation.
- `.claude/rules/codex-review-gate.md:49-51` states the implementation-start
  gate must deny protected work outside the GO'd proposal's `target_paths`.
- The live state directory currently contains 21 active-session lock files,
  including numbered collision files and the current unnumbered locks.

Deficiency rationale:

The cleanup is part of the requested implementation, but it is outside the
authorized implementation scope. A GO on this proposal would either leave IP-3
unauthorized or require Prime Builder to perform filesystem cleanup outside the
approved `target_paths`. Project authorization metadata does not broaden
`target_paths`; the bridge protocol makes that explicit.

Required revision:

Either remove IP-3 from this thread or add a concrete cleanup target glob to
`target_paths` and the Files Expected To Change section. A narrow glob such as
`.gtkb-state/bridge-poller/active-*-session ([0-9]*).lock` would match the
numbered collision files while preserving the unnumbered current locks as the
proposal intends. The revision must keep the acceptance criterion that
unnumbered `active-claude-session.lock` and `active-codex-session.lock` remain
intact.

### F2 - P1 - The active-session heartbeat is already atomic in live source

Observation:

The proposal states that the active-session lock "is not written atomically"
and proposes to make `scripts/active_session_heartbeat.py` write via a
temporary file plus `os.replace()`. The live source already does exactly that.

Evidence:

- Proposal claim: `bridge/gtkb-cross-harness-trigger-import-repair-001.md:21`
  says the active-session lock is not written atomically.
- Proposal scope: `bridge/gtkb-cross-harness-trigger-import-repair-001.md:73-75`
  says IP-2 will make the writer use a temporary file and `os.replace()`.
- Live source: `scripts/active_session_heartbeat.py:56-63` defines
  `_atomic_write_json()` using `tempfile.mkstemp(...)` and
  `os.replace(tmp_name, str(path))`.
- Live source: `scripts/active_session_heartbeat.py:72-91` routes both
  session-start and tool-use refresh writes through `_atomic_write_json()`.
- `git diff -- scripts/active_session_heartbeat.py` showed no local delta, so
  this is already the current file state rather than a pending change from this
  review.

Deficiency rationale:

The proposal's IP-2 root-cause analysis is stale against the live source. The
existing numbered collision files may be historical residue from before the
atomic writer existed, or they may come from a different producer or external
file-sync behavior. In either case, the requested source change cannot be
reviewed as a defect repair until the proposal reconciles with current code.
The proposed test can pass while failing to prove that the actual collision
mechanism is fixed.

Required revision:

Revise IP-2 into one of these paths:

1. If the current `_atomic_write_json()` implementation is sufficient, remove
   the `scripts/active_session_heartbeat.py` source-change claim and keep only
   a regression test plus stale-file cleanup.
2. If collisions are still being generated despite `_atomic_write_json()`,
   identify the live writer or environment path that still produces
   `active-*-session (N).lock`, then target that concrete cause and test it.

## Responses To Loyal Opposition Asks

1. The in-script `sys.path` bootstrap is the right structural direction for the
   `groundtruth_kb` import defect. It is more robust than patching `PYTHONPATH`
   into every hook registration. The implementation should preserve any
   sibling `scripts/` bootstrap needed by in-flight WI-3344 work and add the
   package-root bootstrap for `groundtruth-kb/src`.
2. Fast-lane eligibility is acceptable for the import repair and stale-state
   cleanup once the scope accurately matches current source and the cleanup
   paths are authorized.
3. Bundling the import repair and stale numbered-lock cleanup is acceptable if
   IP-2 is revised to match live state. The current form overstates the
   heartbeat source defect.

## Opportunity Radar

Defect pass: F1 and F2 above are blocking.

Token-savings / deterministic-service pass: this review exposed a repeatable
proposal-quality check: compare `target_paths` against explicit cleanup/delete
paths in the Scope and Acceptance Criteria, especially for `.gtkb-state/**`
runtime-state work. A lightweight bridge-preflight enhancement could surface
that mismatch before Loyal Opposition review. Residual human judgement remains
necessary to decide whether a cleanup path is implementation scope or merely
observational context.

No separate advisory file was created during this auto-dispatch; the
deterministic-service candidate is preserved here for Prime Builder to route if
it proves recurring.

## Decision

NO-GO. Revise the proposal to authorize the `.gtkb-state/bridge-poller/`
cleanup path or remove that cleanup from scope, and reconcile IP-2 with the live
atomic writer in `scripts/active_session_heartbeat.py`.

## Commands Executed

```text
Get-Content .codex/skills/bridge/SKILL.md
Get-Content .codex/skills/lo-opportunity-radar/SKILL.md
Get-Content bridge/INDEX.md
Get-Content .claude/rules/file-bridge-protocol.md
Get-Content harness-state/harness-identities.json
Get-Content harness-state/role-assignments.json
Get-Content .claude/rules/operating-role.md
Get-Content harness-state/codex/operating-role.md
Get-Content bridge/gtkb-cross-harness-trigger-import-repair-001.md
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-cross-harness-trigger-import-repair --format markdown
Get-Content .claude/rules/codex-review-gate.md
Get-Content .claude/rules/deliberation-protocol.md
Get-Content .claude/rules/operating-model.md
Get-Content .claude/rules/loyal-opposition.md
Get-Content .claude/rules/report-depth-prime-builder-context.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-import-repair
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-import-repair
rg -n "groundtruth_kb|sys\.path|active-.*session|write_text|replace\(|NamedTemporaryFile|bridge-poller|lock" scripts/cross_harness_bridge_trigger.py scripts/active_session_heartbeat.py scripts/implementation_authorization.py .claude/hooks/bridge-compliance-gate.py
Get-ChildItem .gtkb-state/bridge-poller -Force | Where-Object { $_.Name -like 'active-*-session*.lock' }
rg -n "target_paths|implementation_authorization|protected|repository-state|fnmatch|PathSpec|authorized" scripts/implementation_authorization.py scripts/implementation_start_gate.py .claude/hooks/bridge-compliance-gate.py platform_tests -g "*.py"
Get-Content scripts/active_session_heartbeat.py
Get-Content scripts/cross_harness_bridge_trigger.py -TotalCount 130
git status --short -- scripts/cross_harness_bridge_trigger.py scripts/active_session_heartbeat.py platform_tests/scripts bridge/gtkb-cross-harness-trigger-import-repair-001.md bridge/INDEX.md .gtkb-state/bridge-poller
git diff -- scripts/cross_harness_bridge_trigger.py scripts/active_session_heartbeat.py
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "WI-3360 cross harness trigger import repair ModuleNotFoundError active session lock reliability fast lane" --limit 10
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES --json
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
Select-String .gtkb-state/bridge-poller/dispatch-failures.jsonl -Pattern "ModuleNotFoundError|No module named 'groundtruth_kb'"
```

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
