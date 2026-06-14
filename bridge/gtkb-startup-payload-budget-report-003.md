NEW

bridge_kind: implementation_report
Document: gtkb-startup-payload-budget-report
Version: 003
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-13T21-19-28Z-prime-builder-B-3b53d5
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code dispatched bridge worker; Prime Builder (durable role, harness B); explanatory output style; cross-harness auto-dispatch
Date: 2026-06-13 UTC
related_proposal: bridge/gtkb-startup-payload-budget-report-001.md
related_verdict: bridge/gtkb-startup-payload-budget-report-002.md

Project Authorization: PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-STARTUP-PAYLOAD-PROFILER-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-STARTUP-REFRACTOR-001
Work Item: WI-4360
target_paths: ["scripts/startup_payload_budget_report.py", "platform_tests/scripts/test_startup_payload_budget_report.py"]
implementation_scope: source, test
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4360 Slice A — Implementation Report: Startup Payload Budget Report

## Summary

Implemented exactly the GO'd Slice A design from
`bridge/gtkb-startup-payload-budget-report-001.md` (Loyal Opposition GO at
`-002`). Two new files, both within the proposal's `target_paths`:

- `scripts/startup_payload_budget_report.py` — a deterministic, read-only
  consumer of the `gtkb-startup-payload-profile-v1` profile files that emits a
  by-harness startup-payload budget report (per-harness byte/token totals split
  into a mandatory tier — `additionalContext` — and an expandable tier —
  `startupDisclosure` — plus cross-harness totals).
- `platform_tests/scripts/test_startup_payload_budget_report.py` — the
  spec-derived test suite (10 tests, all passing).

No other file was modified. The module imports nothing from the startup
producer `scripts/session_self_initialization.py`; it reads only the versioned
JSON contract. The startup producer, the `gt` CLI, and the init-keyword
disclosure path were not touched, so no `init_keyword_disclosure_regression`
is possible. The only runtime writes are `budget-report.json` /
`budget-report.md` into the gitignored `.gtkb-state/startup-payload-profiles/`
dir (confirmed gitignored via `git check-ignore`).

## GO Condition Compliance

The `-002` GO was conditional on three points; each is satisfied:

1. **"Implementation report must include actual results of the pre-file quality
   gates."** — Done; see the executed commands and observed results below
   (`ruff check`, `ruff format --check`, pytest, and two smoke runs).
2. **"Avoid silently expanding scope into Slice B territory."** — No producer /
   hook / event-source capture was added. Scope is strictly the read-only
   consumer + tests. Slice B remains explicitly deferred.
3. **"The module imports nothing from `session_self_initialization.py`."** —
   Held. The module's only imports are stdlib (`argparse`, `json`, `sys`,
   `dataclasses`, `datetime`, `pathlib`, `typing`). It consumes the stable
   `gtkb-startup-payload-profile-v1` JSON contract only.

## Specification Links

Carried forward from the proposal `-001` and exercised by the executed tests
below:

- **DCL-SESSION-STARTUP-TOKEN-BUDGET-001** (verified) — per-harness byte/token
  budgets; the report's primary derived-from spec.
- **DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001** (specified) — mandatory
  (`additionalContext`) vs expandable (`startupDisclosure`) tier split.
- **GOV-SESSION-SELF-INITIALIZATION-001** (verified) — deterministic,
  replayable report giving by-harness visibility into startup-payload cost.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — read-only over `.gtkb-state/` runtime
  data; writes only a non-canonical runtime report; touches no bridge authority
  surface.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — PAUTH, project,
  work item, target paths, and governing specs are concretely linked.
- **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — machine-readable
  `Project Authorization:` / `Project:` / `Work Item:` lines present.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the spec-to-test
  mapping below maps each linked spec/acceptance criterion to an executed test.
- **GOV-STANDING-BACKLOG-001** — WI-4360 is the backlog authority for this
  slice; no other WI is claimed.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001** — implemented under the
  active PAUTH (`source_file` + `test_file` mutation classes) plus the `-002`
  GO plus an implementation-start packet (`sha256:f2047781...`).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both files are in-root under
  `E:\GT-KB`; no application/adopter surface touched.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** / **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001**
  / **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable tracked
  artifact; the deferred Slice B is named, not silently dropped.

## Spec-to-Test Mapping (Specification-Derived Verification Gate)

| Spec / Acceptance criterion | Test(s) | Result |
|---|---|---|
| DCL-SESSION-STARTUP-TOKEN-BUDGET-001 — per-harness byte/token budgets | `test_build_report_by_harness`, `test_cross_harness_totals` | PASS |
| DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 — mandatory vs expandable split | `test_mandatory_vs_expandable_classification`, `test_unknown_section_flagged_and_defaulted` | PASS |
| GOV-SESSION-SELF-INITIALIZATION-001 — deterministic, replayable report | `test_determinism_same_input_same_output`, `test_render_markdown_shape` | PASS |
| Contract integrity (`gtkb-startup-payload-profile-v1`) | `test_load_skips_non_contract_json`, `test_contract_version_constant` | PASS |
| Read-only / robustness | `test_empty_profiles_dir_returns_empty_report`, `test_inputs_not_mutated` | PASS |

`test_contract_version_constant` cross-checks the module `CONTRACT_VERSION`
against the live `last-*.json` profile records (both `last-claude.json` and
`last-codex.json` emit `gtkb-startup-payload-profile-v1`; the assertion held).

## Executed Verification Commands and Observed Results

**Lint gate (`ruff check`):**

```
$ python -m ruff check scripts/startup_payload_budget_report.py platform_tests/scripts/test_startup_payload_budget_report.py
All checks passed!   (exit 0)
```

**Format gate (`ruff format --check`) — separate gate, run after applying `ruff format`:**

```
$ python -m ruff format --check scripts/startup_payload_budget_report.py platform_tests/scripts/test_startup_payload_budget_report.py
2 files already formatted   (exit 0)
```

**Test suite (`pytest`):**

```
$ python -m pytest platform_tests/scripts/test_startup_payload_budget_report.py -q --tb=short
10 passed in 0.86s
```

**Smoke run (`--stdout`, against live profiles):**

```
$ python scripts/startup_payload_budget_report.py --stdout
# Startup Payload Budget Report
- contract_version: `gtkb-startup-payload-profile-v1`
- generated_at: `2026-06-13T21:27:08Z`
- harness_count: 2
| Harness | Role | Total bytes | Total tokens | Mandatory bytes | Mandatory tokens | Expandable bytes | Expandable tokens |
| claude | prime-builder | 14201 | 3549 | 5973 | 1494 | 8228 | 2055 |
| codex  | loyal-opposition | 26998 | 6747 | 10174 | 2543 | 16824 | 4204 |
| **TOTAL** | — | 41199 | 10296 | 16147 | 4037 | 25052 | 6259 |
```

**Smoke run (file-write path):**

```
$ python scripts/startup_payload_budget_report.py
Wrote .gtkb-state\startup-payload-profiles\budget-report.json and .gtkb-state\startup-payload-profiles\budget-report.md (2 harness profile(s)).
$ git check-ignore .gtkb-state/startup-payload-profiles/budget-report.json .gtkb-state/startup-payload-profiles/budget-report.md
(both paths returned; exit 0 — gitignored runtime output, not canonical state)
```

Note: the `—` (em-dash) in the `--stdout` TOTAL row renders as a replacement
glyph on the Windows console (cp1252 display only); the written `.md` file is
correct UTF-8 (`'**TOTAL** | —' in file == True`).

## Implementation Note (test-loader fix during implementation)

The test loader registers the path-loaded module in `sys.modules` before
`exec_module`. Under `from __future__ import annotations` (Python 3.14),
`dataclasses` resolves a class's string annotations via
`sys.modules[cls.__module__].__dict__`; an unregistered path-loaded module
resolves to `None` and raises `AttributeError` at class-definition time. This
is a test-harness concern only — the production module is unaffected. The fix
is the standard `sys.modules[spec.name] = module` idiom and is contained in the
test file (within `target_paths`).

## Requirement Sufficiency

Existing requirements sufficient. No new or revised formal specification was
required or created; the PAUTH `scope_summary` explicitly excludes formal
spec/GOV/ADR/DCL mutation. The work is a deterministic measurement/report over
the already-VERIFIED `gtkb-startup-payload-profile-v1` data contract.

## Prior Deliberations

- **`bridge/gtkb-startup-payload-profiler-compact-context-006.md`** (VERIFIED,
  WI-4361) — the foundation thread that shipped the compact/disclosure split +
  per-session payload-profile instrumentation and explicitly left WI-4360 open
  for this closure path.
- **`bridge/gtkb-startup-payload-budget-report-002.md`** (GO, WI-4360) — the
  Loyal Opposition GO whose three conditions this report satisfies.
- **`DELIB-20260605-GLOSSARY-CLI-SCAN-DELTA-APPROVAL`** — the owner decision
  backing the active PAUTH.

## Owner Decisions / Input

This implementation is authorized by durable owner-decision evidence; no new
owner AskUserQuestion was required for this slice.

- **`DELIB-20260605-GLOSSARY-CLI-SCAN-DELTA-APPROVAL`** — recorded as the
  `owner_decision_deliberation_id` on the active
  `PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-STARTUP-PAYLOAD-PROFILER-IMPLEMENTATION-AUTHORIZATION`,
  whose `scope_summary` authorizes exactly "Implement WI-4360 startup payload
  profiler and budget report by harness in the startup service/tests; no formal
  spec/GOV/ADR/DCL mutation; preserve interactive init-keyword disclosure
  behavior." The slice stayed within `allowed_mutation_classes` (`source_file`,
  `test_file`) and violated neither `forbidden_operation`
  (`formal_artifact_mutation_without_packet`, `init_keyword_disclosure_regression`).

## Risk / Rollback

- **Risk: low.** Two additive files; read-only over `.gtkb-state/` runtime
  data; writes only gitignored runtime output. Cannot alter canonical state,
  the startup producer, the `gt` CLI, or the init-keyword disclosure path.
- **Rollback:** delete the two new files. No migration, no KB mutation, no
  canonical artifact changed. Any `budget-report.*` under `.gtkb-state/` is
  gitignored runtime state and may be left in place.

## Recommended Commit Type

`feat:` — adds a net-new deterministic startup-payload budget-report module
plus a comprehensive test suite; no behavior change to existing commands, no
canonical/producer change, no disclosure-path change. Diff stat: 2 new files
(1 source module, 1 test module); 0 modified tracked files.

## WI / Backlog Follow-On (out of report scope)

WI-4360 MemBase stage resolution to a completion state is a separate
operational step performed after this report reaches `VERIFIED`; it is not
claimed by this report. Slice B (producer-side capture of additional sections
beyond the current two) remains an explicitly deferred backlog candidate.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
