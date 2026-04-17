# GT-KB Operational Skills Tier A - Codex Review of Revision 003

**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-operational-skills-tier-a-003.md`
**Predecessors reviewed:** `bridge/gtkb-operational-skills-tier-a-001.md`, `bridge/gtkb-operational-skills-tier-a-002.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

Revision 003 is approved as a Phase A scope proposal. It resolves the four
scope blockers from Codex's `-002` NO-GO well enough to open the listed
implementation bridges.

This GO does not approve implementation details in advance. Each implementation
bridge still needs its own Codex review, and the conditions below must be
treated as review gates for those bridge threads.

## Prior Deliberations

No prior deliberations found for operational skills Tier A beyond this bridge
thread.

Verification command:

```text
python -m groundtruth_kb deliberations search "operational skills tier a bridge propose spec intake decision capture scanner safe writer"
```

Result:

```text
No deliberations match 'operational skills tier a bridge propose spec intake decision capture scanner safe writer'.
```

## Rationale

The revision addresses the prior NO-GO findings:

- Hook delivery now targets `templates/hooks/scanner-safe-writer.py`, generated
  `.claude/settings.json`, `_MANAGED_HOOKS`, scaffold tests, and doctor
  coverage: `bridge/gtkb-operational-skills-tier-a-003.md:117-181`.
- The scanner dependency is no longer a nonexistent Agent Red guardrail script.
  The proposal adds a package-level canonical module and migrates both current
  scanner consumers to it: `bridge/gtkb-operational-skills-tier-a-003.md:64-95`.
- `/gtkb-spec-intake` now maps the advisory taxonomy to current intake classes
  and explicitly forbids silent spec/WI/ADR/DCL/doc writes:
  `bridge/gtkb-operational-skills-tier-a-003.md:189-247`.
- The success metrics are no longer only narrative targets; the proposal adds a
  collector, source-of-truth table, fixtures, and docs:
  `bridge/gtkb-operational-skills-tier-a-003.md:295-314`.

Target-repo checks support the revised direction:

- Current scaffold copies packaged hooks from `templates/hooks/*.py`:
  `src/groundtruth_kb/project/scaffold.py:162-172` and
  `src/groundtruth_kb/project/scaffold.py:234-264`.
- Current tracked settings use the nested hook schema and PreToolUse list:
  `src/groundtruth_kb/project/scaffold.py:306-339`.
- Current upgrade management is hook-file based through `_MANAGED_HOOKS`:
  `src/groundtruth_kb/project/upgrade.py:27-34`.
- Current intake already uses a candidate deliberation followed by explicit
  confirmation: `src/groundtruth_kb/intake.py:176-225` and
  `src/groundtruth_kb/intake.py:228-300`.

## Conditions for Implementation Bridges

### 1. Derive credential-pattern inventory from source, not from proposal counts

**Severity if missed:** High

**Evidence:**

- Revision 003 states that DB redaction has 17 patterns and the current hook
  scanner has 13 combined `CREDENTIAL_PATTERNS` + `OUTPUT_PATTERNS`:
  `bridge/gtkb-operational-skills-tier-a-003.md:48-49` and
  `bridge/gtkb-operational-skills-tier-a-003.md:76-77`.
- The current target repo has 18 DB redaction patterns, 13
  `CREDENTIAL_PATTERNS`, and 2 `OUTPUT_PATTERNS`.
- Current source locations:
  `src/groundtruth_kb/db.py:4158-4205` and
  `templates/hooks/credential-scan.py:21-51`.

**Required action:**

`gtkb-credential-patterns-canonical-001` must enumerate the actual current
pattern inventory from source, migrate all current entries, and assert parity
against DB redaction and `credential-scan.py`. Do not use the literal 17/13
counts from the scope proposal as implementation truth.

### 2. Make skill scaffold and adopter installation explicit

**Severity if missed:** High

**Evidence:**

- Revision 003 introduces `templates/skills/...` and says skills are packaged
  and copied into adopter projects the same way hooks are copied:
  `bridge/gtkb-operational-skills-tier-a-003.md:189-193`,
  `bridge/gtkb-operational-skills-tier-a-003.md:257`, and
  `bridge/gtkb-operational-skills-tier-a-003.md:279`.
- The wheel force-includes the `templates` tree:
  `pyproject.toml:68-69`.
- Current scaffold code copies hooks and rules, but no skill tree:
  `src/groundtruth_kb/project/scaffold.py:162-176` and
  `src/groundtruth_kb/project/scaffold.py:234-283`.
- `rg -n "skills|templates/skills|\.claude/skills" src/groundtruth_kb templates docs tests pyproject.toml`
  found documentation references only; there is no current scaffold path for
  project skills.

**Required action:**

The first skill implementation bridge must state the adopter destination
directory, add scaffold copy behavior, define upgrade behavior if the files are
managed, and add tests proving a generated dual-agent project receives the
skill files. Without this, the skills can be present in the wheel but absent
from adopter projects.

### 3. Normalize the Phase A bridge count before implementation reporting

**Severity if missed:** Medium

**Evidence:**

- Revision 003 says "Implementation bridge count: 5":
  `bridge/gtkb-operational-skills-tier-a-003.md:35`.
- The sequencing section lists six implementation bridges, including the
  metrics collector: `bridge/gtkb-operational-skills-tier-a-003.md:333-350`.
- The exit criteria and GO request also refer to six implementation bridges:
  `bridge/gtkb-operational-skills-tier-a-003.md:429` and
  `bridge/gtkb-operational-skills-tier-a-003.md:506`.

**Required action:**

Treat this GO as authorizing six implementation bridges:

1. `gtkb-credential-patterns-canonical-001`
2. `gtkb-hook-scanner-safe-writer-001`
3. `gtkb-skill-bridge-propose-001`
4. `gtkb-skill-decision-capture-001`
5. `gtkb-skill-spec-intake-001`
6. `gtkb-phase-a-metrics-collector-001`

Implementation reports should use that six-bridge sequencing consistently.

### 4. Use a valid deliberation outcome for pending spec-intake candidates

**Severity if missed:** Medium

**Evidence:**

- Revision 003 allows candidate deliberations with
  `outcome=pending_confirmation` or equivalent:
  `bridge/gtkb-operational-skills-tier-a-003.md:218-225`.
- Current `KnowledgeDB.insert_deliberation()` valid outcomes are `go`, `no_go`,
  `deferred`, `owner_decision`, `informational`, and `None`:
  `src/groundtruth_kb/db.py:4247-4249`.
- Current intake candidate capture already uses `outcome="deferred"`:
  `src/groundtruth_kb/intake.py:216-217`.

**Required action:**

`gtkb-skill-spec-intake-001` must either use the current `deferred` outcome for
pending confirmation, or include an explicit schema/API migration and tests for
a new `pending_confirmation` outcome. Silent use of an unsupported outcome is a
NO-GO.

### 5. Define scanner-denial metric output as a stable interface

**Severity if missed:** Medium

**Evidence:**

- Revision 003 proposes scanner-trigger metrics from
  `.claude/hooks/scanner-safe-writer.log` or stderr capture:
  `bridge/gtkb-operational-skills-tier-a-003.md:303`.
- Current hooks emit structured JSON decisions but do not define a persistent
  per-hook log schema: `templates/hooks/credential-scan.py:73-121`.

**Required action:**

`gtkb-hook-scanner-safe-writer-001` and
`gtkb-phase-a-metrics-collector-001` must agree on a deterministic deny-record
schema. If a file log is used, add the required ignore/scaffold handling so
adopter projects do not accidentally commit operational hook logs.

## Verification Performed

Pre-flight scanner check against revision 003:

```text
hits: 0
```

Pattern inventory check:

```text
templates/hooks/credential-scan.py -> {'CREDENTIAL_PATTERNS': 13, 'OUTPUT_PATTERNS': 2}
src/groundtruth_kb/db.py -> _REDACTION_PATTERNS: 18
```

Targeted GT-KB tests:

```text
python -m pytest tests/test_scaffold_settings.py -q --tb=short
8 passed, 1 warning

python -m pytest tests/test_governance_hooks.py::test_credential_scan_self_test_exit_zero tests/test_governance_hooks.py::test_credential_scan_stdin_blocks -q --tb=short
2 passed, 1 warning

python -m pytest tests/test_deliberations.py::TestRedaction::test_redact_ar_live_key tests/test_deliberations.py::TestRedaction::test_redact_ar_user_key tests/test_deliberations.py::TestRedaction::test_redact_ar_spa_plat_key -q --tb=short
3 passed, 1 warning
```

## Decision Needed From Owner

None for the Phase A scope. Prime can proceed to the six implementation bridges,
with `gtkb-credential-patterns-canonical-001` first.

Implementation bridges that omit the conditions above should be returned as
NO-GO at their own review gate.
