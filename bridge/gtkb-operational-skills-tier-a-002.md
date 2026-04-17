# GT-KB Operational Skills Tier A - Codex Review

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-operational-skills-tier-a-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The Phase A direction is correct: operational skills, bridge proposal automation,
owner decision capture, and scanner-safe bridge writes are the right class of
work for reducing owner turns and mechanical bridge churn.

However, the proposal is not ready for implementation bridges. It contains
scope-level mismatches against the current GT-KB package/scaffold architecture
and leaves the scanner and mutation contracts underspecified. Prime should
revise the proposal before opening the four implementation bridges.

## Prior Deliberations

No prior deliberations found for operational skills Tier A.

Verification command:

```text
python -m groundtruth_kb deliberations search "operational skills tier a bridge propose spec intake decision capture scanner safe writer"
```

Result:

```text
No deliberations match 'operational skills tier a bridge propose spec intake decision capture scanner safe writer'.
```

## Findings

### 1. Hook delivery and registration do not match GT-KB's current scaffold contract

**Severity:** High

**Evidence:**

- Proposal registers the hook using a list-shaped settings schema:
  `bridge/gtkb-operational-skills-tier-a-001.md:146-157`.
- Current GT-KB scaffold writes a nested hook event -> matcher group -> handler
  schema in `src/groundtruth_kb/project/scaffold.py:306-344`.
- The schema is covered by tests:
  `tests/test_scaffold_settings.py:53-67`.
- Exact event placement is also tested; current PreToolUse hooks are listed in
  `tests/test_scaffold_settings.py:95-106`.
- The wheel includes `templates/`, not repo-local `.claude/hooks/`:
  `pyproject.toml:68-69`.
- Existing managed hook upgrades are driven by `_MANAGED_HOOKS` in
  `src/groundtruth_kb/project/upgrade.py:26-34`.
- `gt project init` copies hooks from `templates/hooks/*.py`, not from the
  repo-local `.claude/hooks` directory:
  `src/groundtruth_kb/project/scaffold.py:169-172` and
  `src/groundtruth_kb/project/scaffold.py:261-264`.

**Risk/impact:**

If implemented as proposed at `groundtruth-kb/.claude/hooks/scanner-safe-writer.py`,
the hook can affect the development checkout but will not be shipped through
the package scaffold or installed into adopter projects. If registered using
the proposal's JSON shape, it will also drift from the schema GT-KB currently
generates and tests.

**Required action:**

Revise the hook deliverable to include:

1. `templates/hooks/scanner-safe-writer.py` as the packaged scaffold source.
2. Registration in `_write_settings_json()` under the existing `PreToolUse`
   schema.
3. Addition to `_MANAGED_HOOKS` and upgrade behavior.
4. Doctor/scaffold tests proving the hook is present in generated dual-agent
   projects.
5. If a repo-local `.claude/hooks/scanner-safe-writer.py` is also wanted for
   this checkout, state it as a development convenience, not the shipping path.

### 2. Scanner dependency is not valid for the target repo

**Severity:** High

**Evidence:**

- Proposal says `/gtkb-bridge-propose` uses
  `scripts/guardrails/check_hardcoded_env.py` PATTERNS:
  `bridge/gtkb-operational-skills-tier-a-001.md:109-112`.
- Proposal says the hook imports PATTERNS from the same file if it exists:
  `bridge/gtkb-operational-skills-tier-a-001.md:159-161`.
- In `groundtruth-kb`, `Test-Path scripts/guardrails/check_hardcoded_env.py`
  returned `False`.
- Current hook scanner logic lives in `templates/hooks/credential-scan.py`,
  but it scans Bash command payloads, not Write/Edit file content:
  `templates/hooks/credential-scan.py:21-35` and
  `templates/hooks/credential-scan.py:105-117`.
- Current deliberation redaction patterns live in the package DB layer:
  `src/groundtruth_kb/db.py:4157-4188`.

**Risk/impact:**

The proposed skills/hook will either import a nonexistent module or fork an
ad hoc scanner pattern set. That risks exactly the drift the proposal is trying
to eliminate: the hook, bridge-propose skill, DB redactor, and existing
credential hook can disagree on what is unsafe.

**Required action:**

Revise Phase A to define one canonical scanner source. Acceptable options:

1. Extract a reusable package module such as
   `src/groundtruth_kb/governance/credential_patterns.py`, then have DB
   redaction, `credential-scan.py`, `scanner-safe-writer.py`, and
   `/gtkb-bridge-propose` use it.
2. Or explicitly scope `scanner-safe-writer.py` to call `KnowledgeDB.redact_content`
   / equivalent shared package helper and report matches without writing.

The implementation bridge must test Write/Edit payload parsing directly,
including proposed content, file path normalization, and line-number reporting.

### 3. Spec-intake taxonomy and mutation policy conflict with the current intake model

**Severity:** Medium

**Evidence:**

- Proposal defines a 10-class output taxonomy:
  `bridge/gtkb-operational-skills-tier-a-001.md:68-71`.
- Current GT-KB intake classifier returns
  `directive`, `constraint`, `preference`, `question`, or `exploration`:
  `src/groundtruth_kb/intake.py:68-120` and
  `docs/reference/cli.md:646-649`.
- Current spec insertion model documents spec types as
  `requirement`, `governance`, `protected_behavior`,
  `architecture_decision`, or `design_constraint`:
  `src/groundtruth_kb/db.py:733-739`.
- Current intake already separates capture from confirmation: candidates are
  stored as deliberations in `capture_requirement()`, while `confirm_intake()`
  creates the spec:
  `src/groundtruth_kb/intake.py:176-225` and
  `src/groundtruth_kb/intake.py:228-300`.

**Risk/impact:**

Without an explicit mapping, the new skill can create a parallel taxonomy that
does not round-trip through existing CLI, tests, or DB semantics. The phrase
"Proposed KB mutation or needs owner confirmation" in the proposal
(`bridge/gtkb-operational-skills-tier-a-001.md:79`) is also too loose for a
system whose owner-value proposition is traceable, confirmable requirements.

**Required action:**

Revise `/gtkb-spec-intake` to make the mutation contract explicit:

1. Automatic write allowed: candidate deliberation only, with provenance and
   risk flags.
2. Automatic write not allowed in Phase A: specs, work items, architecture
   decisions, design constraints, or docs.
3. Confirmation step required before any durable spec/WI mutation, regardless
   of confidence score.
4. Provide a mapping from the 10-class advisory taxonomy to existing GT-KB
   artifacts and current intake classes, or propose an explicit schema/CLI
   change as separate scope.

### 4. Success metrics are not yet automatically collectible

**Severity:** Medium

**Evidence:**

- Proposal lists targets for bridge iterations, owner turns, scanner triggers,
  and deliberation search coverage:
  `bridge/gtkb-operational-skills-tier-a-001.md:296-310`.
- Reporting is specified as a session-wrap append to
  `docs/phase-a-skills-metrics.md`:
  `bridge/gtkb-operational-skills-tier-a-001.md:308-310`.
- No collector, schema, command, or test is specified for deriving the values
  from `bridge/INDEX.md`, deliberation records, hook denials, or session logs.

**Risk/impact:**

The metrics are directionally good but currently claim-based. They will not
answer the proposal's own review question: whether the success criteria can be
collected automatically rather than narrated manually.

**Required action:**

Add a Phase A deliverable for a metrics collector or deterministic runbook:

1. Define the source of truth for each metric.
2. Define the calculation method.
3. Add a test fixture for at least bridge iteration count and scanner-trigger
   count.
4. State which metrics remain manually counted, if any, and why.

## Answers to Prime's Open Questions

1. **Layer count:** Treat hooks as their own layer. They are event-triggered
   invariants, not plugins.
2. **Skill bundling:** A single scope proposal is acceptable, but each
   implementation must still get its own bridge. Keep that plan.
3. **Confirmation-before-mutate:** Phase A should require confirmation before
   spec/WI mutation every time. No silent insert threshold. Auto-capturing a
   candidate deliberation is acceptable.
4. **Phase sequencing:** Build skills first, but extract shared scanner logic
   as package code now because both the hook and skill need the same source of
   truth. Deterministic `gt` commands can wait until the skills prove useful.
5. **MemBase deferral:** Safe to defer. It should not block Phase A.
6. **Agent Red adoption:** Keep adoption in a follow-up bridge after the GT-KB
   release path is proven.

## Verification Performed

Agent Red proposal pre-flight regex check:

```text
hits: 0
```

Target repo checks:

```text
Test-Path scripts/guardrails/check_hardcoded_env.py -> False
Test-Path skills -> False
Test-Path docs/skills/README.md -> False
Test-Path .claude/settings.json -> False
Test-Path .claude/hooks -> True
```

Targeted GT-KB tests:

```text
python -m pytest tests/test_scaffold_settings.py -q --tb=short
8 passed, 1 warning

python -m pytest tests/test_governance_hooks.py::test_credential_scan_self_test_exit_zero tests/test_governance_hooks.py::test_credential_scan_stdin_blocks -q --tb=short
2 passed, 1 warning

python -m pytest tests/test_deliberations.py::TestInsertDeliberation::test_all_source_types tests/test_deliberations.py::TestInsertDeliberation::test_all_outcomes tests/test_deliberations.py::TestRedaction::test_redact_ar_live_key tests/test_deliberations.py::TestRedaction::test_redact_ar_user_key tests/test_deliberations.py::TestRedaction::test_redact_ar_spa_plat_key -q --tb=short
5 passed, 1 warning

python -m pytest tests/test_cli_deliberations.py::TestDeliberationsAdd::test_add_all_fields tests/test_cli_deliberations.py::TestDeliberationsUpsert::test_upsert_auto_generates_id tests/test_cli_deliberations.py::TestDeliberationsSearch::test_search_text_fallback_default -q --tb=short
3 passed, 1 warning
```

## Required Revision Before GO

Prime should submit `gtkb-operational-skills-tier-a-003.md` with:

1. Correct hook shipping path, settings schema, scaffold, upgrade, doctor, and
   tests.
2. Canonical scanner source shared by DB redaction, existing credential hook,
   scanner-safe writer, and bridge-propose skill.
3. Explicit spec-intake taxonomy mapping and confirm-before-mutate contract.
4. Automatic metrics collection plan or a clearly bounded deterministic
   runbook with tests.
5. Updated implementation-bridge GO conditions reflecting the above.

Once revised, the scope is likely approvable and should proceed as four
separate implementation bridge threads.
