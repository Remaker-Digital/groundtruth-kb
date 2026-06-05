NO-GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-ollama-integration-phase-1-foundation
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-05 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-ollama-integration-phase-1-foundation-001.md
Recommended commit type: docs

# Loyal Opposition Verdict - Ollama Phase 1 Foundation Child

## Verdict

NO-GO.

The proposal is directionally aligned with the owner-approved Ollama Phase 1
scope: harness D stays `registered` with role-set `[]`, source paths remain
inside `E:\GT-KB`, and the mandatory bridge preflights pass. It cannot receive
GO as filed because the verification/test path targets a retired root
`tests/scripts` surface, and the proposal changes the parent-approved
`capabilities.ollama.*` capability-floor assertion to `harnesses.ollama.*`
without revising the governing draft/spec mapping that child bridges are
supposed to preserve.

No owner input is required from this auto-dispatch worker. Prime Builder can
file a REVISED child proposal that corrects the test path and carries a
TOML-valid capability-floor namespace consistently through the child proposal,
the verification plan, and the later governance-implementation child.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this document was
  `NEW: bridge/gtkb-ollama-integration-phase-1-foundation-001.md`, actionable
  for Loyal Opposition.
- Resolved durable Codex harness `A` from `harness-state/harness-identities.json`
  and `harness-state/harness-registry.json`; current role set contains
  `loyal-opposition`.
- Read the full thread chain with
  `.claude/skills/bridge/helpers/show_thread_bridge.py`; this thread has only
  the `-001` proposal before this verdict.
- Applied the `gtkb-bridge` and `harness-parity-review` workflows.

## Mandatory Preflights

Commands:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
```

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:692a2fc44bcf8a62bcf6d59241ea61da472bc8339fe0114999e7a5f8126500f0`
- bridge_document_name: `gtkb-ollama-integration-phase-1-foundation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ollama-integration-phase-1-foundation-001.md`
- operative_file: `bridge/gtkb-ollama-integration-phase-1-foundation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["tests/scripts/test_check_harness_parity.py"]
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ollama-integration-phase-1-foundation`
- Operative file: `bridge\gtkb-ollama-integration-phase-1-foundation-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

Deliberation Archive checks were run through the repo venv:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "ollama harness D registered role-set empty capability floor guard adapter" --limit 10 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "DELIB-20260663 Ollama Phase 1 AUQ harness D capability floor" --limit 10 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-20260663 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT --json
```

Relevant records:

- `DELIB-20260663` confirms the 12-AUQ Ollama Phase 1 owner decisions, including
  AUQ#3 (`registered`, no active role), AUQ#4 (identity + registry + shim + one
  model + E2E test), AUQ#8 (one project PAUTH for Phase 1), and AUQ#11
  (procedural + machine-checkable + capability floor).
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` confirms role/status
  orthogonality and the single-ACTIVE-per-role dispatch model; D as
  `registered` with `role: []` is consistent with that model.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` remains relevant background for
  root containment and lifecycle isolation.
- Parent bridge `bridge/gtkb-ollama-integration-phase-1-004.md` records GO for
  the umbrella while requiring child bridges to preserve the parent constraints.

## Findings

### F1 - P1 - Verification targets the retired root `tests/scripts` surface

Observation:

The proposal's `target_paths` and verification plan place the new parity tests
under `tests/scripts/test_check_harness_parity.py` and run `python -m pytest
tests/scripts/test_check_harness_parity.py -q`. The mandatory applicability
preflight also warns that `tests/scripts/test_check_harness_parity.py` is a
missing parent path.

Evidence:

- `bridge/gtkb-ollama-integration-phase-1-foundation-001.md:26` lists
  `tests/scripts/test_check_harness_parity.py` in `target_paths`.
- `bridge/gtkb-ollama-integration-phase-1-foundation-001.md:150` says to add a
  unit test in `tests/scripts/test_check_harness_parity.py`.
- `bridge/gtkb-ollama-integration-phase-1-foundation-001.md:185` repeats the
  new test-file path.
- `bridge/gtkb-ollama-integration-phase-1-foundation-001.md:187-188` uses the
  same path in ruff and pytest commands.
- `bridge/gtkb-ollama-integration-phase-1-foundation-001.md:199` maps
  WI-4317 verification to test node IDs under `tests/scripts`.
- Root `pyproject.toml:9` sets pytest discovery to `["platform_tests",
  "applications/Agent_Red/tests"]`, not bare `tests`.
- `platform_tests/governance/test_platform_tests_rename.py:134-141` explicitly
  asserts `platform_tests` is present and bare `tests` is absent from root
  pytest `testpaths`.
- `platform_tests/scripts/test_check_harness_parity.py` already exists and is
  the current repo-native parity-script test surface.

Deficiency rationale:

The proposal would create a new test under a retired root path instead of
extending the existing discovered parity-script test module. That weakens the
spec-derived verification gate because default repo pytest discovery would not
include the new root `tests/scripts` file, and it creates path drift against the
tracked `platform_tests` migration guard.

Impact:

Prime Builder could implement WI-4317 and report a targeted command pass while
the repo's normal test discovery, platform rename guard, and existing parity
test suite remain out of sync. This is exactly the kind of harness-parity drift
the child proposal is supposed to reduce.

Required revision:

Use `platform_tests/scripts/test_check_harness_parity.py` as the test target
and update `target_paths`, ruff commands, pytest commands, and the
Specification-Derived Verification Plan accordingly. If a new root `tests`
surface is intentionally desired, the proposal needs a separate governed
justification and pyproject/testpath changes, which is outside this child
scope.

### F2 - P1 - Capability-floor namespace changes the approved parent assertion

Observation:

The child proposal says WI-4318 adds a `[capabilities.ollama]` top-level block
and that AUQ#11 authorizes the `[capabilities.ollama]` capability floor. It
then switches the actual implementation plan and verification assertion to
`[harnesses.ollama]` / `d['harnesses']['ollama']`, explicitly asking Loyal
Opposition whether that disambiguation is acceptable.

Evidence:

- `bridge/gtkb-ollama-integration-phase-1-foundation-001.md:65` says this
  child declares required fields in `[capabilities.ollama]`.
- `bridge/gtkb-ollama-integration-phase-1-foundation-001.md:93` says AUQ#11
  authorizes the `[capabilities.ollama]` top-level block.
- `bridge/gtkb-ollama-integration-phase-1-foundation-001.md:152-176` describes
  the TOML naming conflict and changes the implementation/verification shape to
  `[harnesses.ollama]`.
- `bridge/gtkb-ollama-integration-phase-1-foundation-001.md:186` implements
  `[harnesses.ollama]`.
- `bridge/gtkb-ollama-integration-phase-1-foundation-001.md:200` verifies
  `d['harnesses']['ollama']`.
- Parent umbrella revision `bridge/gtkb-ollama-integration-phase-1-003.md:141`
  scopes `[capabilities.ollama]` in the capability registry.
- Parent umbrella revision `bridge/gtkb-ollama-integration-phase-1-003.md:261-263`
  requires assertions for `capabilities.ollama.tool_guard_adapter_fail_closed`
  and `capabilities.ollama.advertised_tool_subset`.
- Parent GO `bridge/gtkb-ollama-integration-phase-1-004.md:85-88` says future
  child bridge GO depends on child proposals preserving the parent constraints.

I also ran a read-only TOML parse experiment. In TOML, appending
`[capabilities.ollama]` after `[[capabilities]]` parses as a subtable on the
last array element, not as a top-level harness-floor table; placing it before
`[[capabilities]]` fails with `Cannot overwrite a value`. A separate namespace
such as `[harnesses.ollama]` is therefore structurally plausible, but the
proposal has to carry that schema choice through the governing draft/spec
contract instead of silently changing only the child implementation.

Deficiency rationale:

The issue is not that `[harnesses.ollama]` is technically wrong. It is likely
the safer TOML shape. The blocker is that the child proposal changes the
approved parent assertion and the forward-referenced GOV/DCL verification path
without revising the linked specification draft and follow-on governance child
contract. A GO here would approve an implementation whose verification target
no longer matches the parent GO's assertion language.

Impact:

Child 1 could land `harnesses.ollama.*`, while Child 4 later inserts
`GOV-HARNESS-ONBOARDING-CONTRACT-001` and `DCL-OLLAMA-TOOL-PARITY-GATE-001`
with `capabilities.ollama.*` assertions. That would produce immediate
post-implementation spec/test drift across the Phase 1 chain.

Required revision:

File a REVISED child proposal that picks one TOML-valid capability-floor
namespace and carries it consistently through:

1. WI-4318 title and scope text.
2. Specification Links and forward-reference table.
3. Implementation plan.
4. Specification-Derived Verification Plan.
5. Child 4 / governance-implementation dependency notes for the future GOV/DCL
   inserts.

If Prime Builder keeps `[harnesses.ollama]`, explicitly state that Child 4 must
update the formal GOV/DCL draft assertions from `capabilities.ollama.*` to
`harnesses.ollama.*` or another TOML-valid namespace before insertion.

### F3 - P2 - Harness-parity verification omits the full parity checker

Observation:

WI-4317 generalizes `KNOWN_HARNESSES`, and the proposal acknowledges that
including Antigravity and Ollama in the parity set may surface cascade
findings. The implementation plan and spec-derived mapping do not make
`python scripts/check_harness_parity.py --all --markdown` or an equivalent
full-parity check a required post-implementation command.

Evidence:

- `bridge/gtkb-ollama-integration-phase-1-foundation-001.md:184-203` lists the
  implementation and verification commands, but the parity-checker command is
  absent.
- `bridge/gtkb-ollama-integration-phase-1-foundation-001.md:213` says full
  parity may reveal new findings and should be surfaced if cascade is too broad,
  but this is only in the risk section.
- The harness-parity review workflow verifies with
  `scripts/check_harness_parity.py --all --markdown`.
- Current baseline command
  `groundtruth-kb\.venv\Scripts\python.exe scripts\check_harness_parity.py --all --markdown`
  returns WARN with one pre-existing undeclared project skill
  (`gtkb-propose`), demonstrating that this check is the canonical signal and
  has known baseline output that an implementation report can compare against.

Deficiency rationale:

Changing the harness enumeration without requiring the harness parity checker
itself to run leaves the most direct regression signal outside the
spec-derived verification gate.

Impact:

Prime could make `KNOWN_HARNESSES` data-driven and pass the new unit tests
while missing newly surfaced MISSING/STALE/EXTRA results for Antigravity or
Ollama in the actual parity report.

Required revision:

Add `python scripts/check_harness_parity.py --all --markdown` to the required
verification commands and require the implementation report to explain the
expected baseline WARN/EXTRA state versus any new findings introduced by the
change. A targeted `--harness ollama` command can be added after the script
supports D, but the full all-harness command is the minimum.

## Positive Confirmations

- The proposal has substantive `## Specification Links`, `## Prior
  Deliberations`, and `## Owner Decisions / Input` sections.
- `DELIB-20260663` supports D as `registered` with no active role and supports
  the Phase 1 foundation cluster under the project PAUTH.
- The target source/config paths are in-root and do not touch `applications/`.
- The mechanical applicability and clause preflights pass with no missing
  required specs and no blocking gaps.
- The proposal correctly excludes shim, routing, doctor, dispatch-substrate,
  formal-spec insert, and protected narrative edits from this child.

## Required Revision Scope

Prime Builder should revise the child proposal before implementation GO:

1. Replace all root `tests/scripts` target and command references with
   `platform_tests/scripts/test_check_harness_parity.py` unless the proposal is
   deliberately expanded to govern a root testpath reversal.
2. Make the Ollama capability-floor TOML namespace internally consistent and
   carry the chosen namespace into the governance-implementation child
   obligations.
3. Add the full harness parity command to required verification and specify how
   to compare its output against the current baseline WARN/EXTRA state.
4. Re-run the mandatory bridge applicability and clause preflights after filing
   the REVISED version.

## Commands Executed

```text
Get-Content bridge\INDEX.md
Get-Content .claude\rules\operating-role.md
Get-Content harness-state\harness-identities.json
Get-Content harness-state\harness-registry.json
Get-Content .claude\rules\file-bridge-protocol.md
Get-Content .claude\rules\codex-review-gate.md
Get-Content .claude\rules\deliberation-protocol.md
Get-Content .claude\rules\loyal-opposition.md
Get-Content .claude\rules\report-depth-prime-builder-context.md
Get-Content .claude\rules\operating-model.md
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-ollama-integration-phase-1-foundation --format markdown --preview-lines 260
python .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "ollama harness D registered role-set empty capability floor guard adapter" --limit 10 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "DELIB-20260663 Ollama Phase 1 AUQ harness D capability floor" --limit 10 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-20260663 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT --json
rg -n "testpaths|python_files|platform_tests|tests/scripts|test_check_harness_parity|check_harness_parity" pyproject.toml groundtruth-kb\pyproject.toml platform_tests groundtruth-kb\tests scripts
groundtruth-kb\.venv\Scripts\python.exe scripts\check_harness_parity.py --all --markdown
groundtruth-kb\.venv\Scripts\python.exe scripts\check_harness_parity.py --harness codex --role loyal-opposition --json
```

## Owner Action Required

None.

File bridge scan contribution: 1 entry processed.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
