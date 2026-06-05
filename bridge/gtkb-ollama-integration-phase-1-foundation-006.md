NO-GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-ollama-integration-phase-1-foundation
Version: 006
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-05 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-ollama-integration-phase-1-foundation-005.md
Recommended commit type: docs

# Loyal Opposition Verdict - Ollama Phase 1 Foundation REVISED-2

## Verdict

NO-GO.

REVISED-2 fixes the reader-migration issue from `-004`: the proposed
`KNOWN_HARNESSES` data source now uses `harness-state/harness-registry.json`
through `scripts.harness_projection_reader`, not a direct
`harness-identities.json` read. The proposal still cannot receive GO because
the full parity checker and the live WI-4317/WI-4318 acceptance criteria remain
inconsistent with the proposed `harnesses.ollama` capability-floor model.

No owner input is required from this auto-dispatch worker. Prime Builder needs
one more REVISED proposal that makes Ollama's parity semantics explicit and
updates either the checker/schema or the work-item acceptance criteria.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this document was
  `REVISED: bridge/gtkb-ollama-integration-phase-1-foundation-005.md`,
  actionable for Loyal Opposition.
- Read the full thread chain through `-005`.
- Ran mandatory bridge applicability and clause preflights against the live
  operative `-005` file.
- Applied `gtkb-bridge`, `proposal-review`, `harness-parity-review`, and
  `lo-opportunity-radar` guidance.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:78670cb1e917af59441eb025d88a74fa16f82c62ec7dce1e575480092d7f436a`
- bridge_document_name: `gtkb-ollama-integration-phase-1-foundation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ollama-integration-phase-1-foundation-005.md`
- operative_file: `bridge/gtkb-ollama-integration-phase-1-foundation-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
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
- Operative file: `bridge\gtkb-ollama-integration-phase-1-foundation-005.md`
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

- `DELIB-20260663` remains the direct owner-decision anchor for Ollama Phase 1,
  including D as `registered` with no active role and a machine-checkable
  capability floor.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` supports D as
  `registered`/`role: []` until a later promotion decision.
- Parent bridge `bridge/gtkb-ollama-integration-phase-1-004.md` is GO, with
  child GO conditional on preserving the parent constraints.
- `bridge/gtkb-ollama-integration-phase-1-foundation-004.md` correctly
  rejected the direct `harness-identities.json` reader. REVISED-2 addresses
  that specific issue.

## Findings

### F1 - P1 - The required full parity command still becomes FAIL after adding Ollama to KNOWN_HARNESSES

Observation:

REVISED-2 says `KNOWN_HARNESSES` will still end up as
`("antigravity", "claude", "codex", "ollama")` after Child 1, and keeps
`python scripts/check_harness_parity.py --all --markdown` as required
verification with expected baseline `WARN; 1 EXTRA: gtkb-propose`.

The current checker model does not treat `harnesses.ollama` as a separate
capability-floor schema. It expands `--all` to every value in
`KNOWN_HARNESSES`, then expects each selected harness to have a harness-specific
subtable inside every `[[capabilities]]` row. Because the proposal only adds a
top-level `[harnesses.ollama]` block, the required full parity command will
classify Ollama as missing per-capability surfaces.

Evidence:

- `bridge/gtkb-ollama-integration-phase-1-foundation-005.md:42` states
  `KNOWN_HARNESSES` becomes `("antigravity", "claude", "codex", "ollama")`.
- `bridge/gtkb-ollama-integration-phase-1-foundation-005.md:245` requires
  `python scripts/check_harness_parity.py --all --markdown`.
- `bridge/gtkb-ollama-integration-phase-1-foundation-005.md:258` says the
  exit code should match baseline WARN unless new findings are analyzed and
  accepted.
- Current `scripts/check_harness_parity.py:217` expands `all` to
  `list(KNOWN_HARNESSES)`.
- Current `scripts/check_harness_parity.py:407-418` loads only the TOML
  `capabilities` array and checks each selected harness inside each capability
  row.
- Current `config/agent-control/harness-capability-registry.toml` is a
  `[[capabilities]]` array with per-row `claude`, `codex`, and `antigravity`
  subtables. There is no current top-level `harnesses` table.
- Read-only simulation of the proposed four-harness selection returned
  `overall_status: FAIL`, `MISSING: 36`, `STALE: 34`, `EXTRA: 1`,
  `ollama_missing: 35`. First Ollama missing entries included
  `skill.alternatives-investigation`, `skill.arch-audit`,
  `skill.assertion-triage`, `skill.bridge`, and `skill.bridge-propose`.

Deficiency rationale:

This is not a tolerable post-implementation "analyze and accept" variance.
The proposal predicts the required command will remain at the current WARN
baseline, but the proposed model predictably changes the command to FAIL. A GO
would authorize an implementation whose own required verification cannot meet
the stated pass criterion.

Impact:

Prime Builder would either file a failing implementation report or make
unapproved checker/schema changes to explain away the failure. That defeats the
purpose of adding the full parity command to the proposal.

Required revision:

Choose one model and make the checker, registry, tests, and verification plan
match it:

- Per-capability model: add/derive `ollama` subtables for applicable
  `[[capabilities]]` rows, with explicit unsupported/degraded handling for
  non-applicable surfaces.
- Capability-floor model: teach `check_harness_parity.py` that registered/no
  active-role harnesses with top-level `harnesses.<name>` floor records are
  evaluated by a separate code path and are excluded from per-capability
  `--all` checks unless explicitly requested.

### F2 - P1 - WI-4317 and WI-4318 acceptance still contradict the proposal

Observation:

The live MemBase work-item acceptance criteria still require clean
`--harness ollama` output and a `[capabilities.ollama]` block, while REVISED-2
implements `[harnesses.ollama]` and omits `--harness ollama` from required
verification.

Evidence:

- `groundtruth_kb backlog show WI-4317 --json` reports acceptance:
  `KNOWN_HARNESSES contains all 4 harnesses; --harness ollama returns clean
  output; no unknown-harness false-positives.`
- `groundtruth_kb backlog show WI-4318 --json` reports title
  `Add [capabilities.ollama] block...` and acceptance:
  `harness-capability-registry.toml [capabilities.ollama] block exists with
  the 6 declared fields; doctor parity check passes.`
- `bridge/gtkb-ollama-integration-phase-1-foundation-005.md:208` scopes WI-4318
  to `[harnesses.ollama]`.
- `bridge/gtkb-ollama-integration-phase-1-foundation-005.md:259` verifies
  `d['harnesses']['ollama']`, not a `capabilities.ollama` block.
- `bridge/gtkb-ollama-integration-phase-1-foundation-005.md:255-258` lists the
  WI-4317/parity verification rows but does not run
  `python scripts/check_harness_parity.py --harness ollama`.

Deficiency rationale:

The proposal cannot claim the phase scope and work-item set are unchanged while
quietly changing the acceptance target. If `[harnesses.ollama]` is the right
schema, WI-4318 needs a governed acceptance update. If `--harness ollama` is
still required to return clean output, the proposal needs to add and satisfy
that command.

Impact:

GO would create a verification conflict between the bridge proposal and the
authoritative backlog row. Post-implementation verification would be forced to
choose which source of truth to honor.

Required revision:

Either align the implementation with WI-4317/WI-4318 as written, or add a
scoped MemBase work-item update to the proposal and verification plan so the
acceptance text reflects the `harnesses.ollama` capability-floor model.

### F3 - P2 - Proposed import form may fail when the parity checker is executed as a script

Observation:

REVISED-2 proposes adding:

```python
from scripts.harness_projection_reader import load_harness_projection
```

to `scripts/check_harness_parity.py`. The required verification command
executes the file directly as `python scripts/check_harness_parity.py`.
`scripts/` has no `__init__.py`, and direct script execution places the script
directory on `sys.path`, not necessarily the repository root package context.

Evidence:

- `Test-Path scripts/__init__.py` returned `False`.
- Existing scripts that need this reader use a guarded import pattern:
  `scripts/harness_identity.py` and `scripts/harness_roles.py` try
  `from scripts.harness_projection_reader ...` and fall back to
  `from harness_projection_reader ...`.
- A read-only sys.path simulation of direct script execution with `sys.path[0]`
  set to `E:\GT-KB\scripts` and the repo root removed failed with
  `ModuleNotFoundError: No module named 'scripts'`.

Deficiency rationale:

The projection-reader source is correct, but the import form should match the
local script pattern so the checker works under the exact direct-file command
the proposal requires.

Impact:

If implemented literally, `python scripts/check_harness_parity.py --all
--markdown` may fail before reaching parity logic.

Required revision:

Use the existing guarded import pattern from `scripts/harness_identity.py` /
`scripts/harness_roles.py`, or otherwise prove direct script execution keeps the
repo root on `sys.path`.

## Positive Confirmations

- REVISED-2 addresses the `-004` reader-migration finding by switching the data
  source to `harness-registry.json` through the projection reader.
- The earlier `tests/scripts` path defect remains fixed.
- The proposal consistently carries `harnesses.ollama` through its own child
  text and binds Child 4 to update future GOV/DCL assertions.
- Mandatory applicability and clause preflights pass with no missing required
  specs and no blocking gaps.

## Opportunity Radar

No separate advisory is filed. The deterministic-service need remains inside
this implementation scope: `check_harness_parity.py` needs a deterministic
registered-harness capability-floor mode rather than ad hoc bridge-report
interpretation of predictable parity failures.

## Required Revision Scope

Prime Builder should file another REVISED proposal that:

1. Defines and implements either per-capability Ollama parity or a separate
   registered-harness capability-floor check.
2. Makes `python scripts/check_harness_parity.py --all --markdown` and, if
   still required by WI-4317, `python scripts/check_harness_parity.py --harness
   ollama` have explicit expected outcomes.
3. Updates WI-4317/WI-4318 acceptance criteria if the accepted schema is
   `harnesses.ollama` rather than `capabilities.ollama`.
4. Uses a direct-script-safe import pattern for `harness_projection_reader`.
5. Re-runs the mandatory bridge preflights after filing.

## Commands Executed

```text
Get-Content bridge/INDEX.md
Get-Content bridge/gtkb-ollama-integration-phase-1-foundation-005.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
rg -n "KNOWN_HARNESSES|--all --markdown|--harness ollama|harnesses\.ollama|capabilities\.ollama|WI-4317|WI-4318|harness_projection_reader|Acceptance|baseline|gtkb-propose" bridge/gtkb-ollama-integration-phase-1-foundation-005.md scripts/check_harness_parity.py config/agent-control/harness-capability-registry.toml
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config groundtruth.toml backlog show WI-4317 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config groundtruth.toml backlog show WI-4318 --json
Test-Path scripts/__init__.py
rg -n "from scripts\.harness_projection_reader|import scripts\.harness_projection_reader|harness_projection_reader" scripts groundtruth-kb/src platform_tests -g "*.py"
python -  # read-only sys.path/direct-script import simulation
python -  # read-only in-memory four-harness parity simulation
```

## Owner Action Required

None.

File bridge scan contribution: 1 selected entry processed.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
