NEW

bridge_kind: implementation_proposal
Document: gtkb-startup-payload-budget-report
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 37191790-3efe-4e97-a707-f8d798f7f238
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-STARTUP-PAYLOAD-PROFILER-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-STARTUP-REFRACTOR-001
Work Item: WI-4360
target_paths: ["scripts/startup_payload_budget_report.py", "platform_tests/scripts/test_startup_payload_budget_report.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4360: Startup Payload Budget Report (by-harness profiler over existing profile data)

## Summary

WI-4360 ("Startup payload profiler and budget report by harness") is the paired backlog item explicitly **left open** by the VERIFIED WI-4361 thread (`bridge/gtkb-startup-payload-profiler-compact-context-006.md`): that thread shipped the compact-`additionalContext` / separate-`startupDisclosure` split plus **lightweight per-session payload-profile instrumentation**, and stated across `-001`, `-005`, and `-006` that "`WI-4360` remains a paired backlog item and is not claimed complete by this proposal." WI-4360 builds the **profiler + budget report by harness** on top of that instrumentation's output.

The WI-4361 instrumentation already writes a per-harness profile file `.gtkb-state/startup-payload-profiles/last-<harness>.json` conforming to contract `gtkb-startup-payload-profile-v1`, capturing per-section size metrics (`character_count`, `line_count`, `rough_token_estimate`, `utf8_bytes`, `sha256`) for the `additionalContext` and `startupDisclosure` sections. WI-4360 consumes those files and produces a **deterministic by-harness budget report** so startup and auto-dispatch turns can be budgeted and compared without replaying oversized context.

This proposal is **Slice A**: a self-contained consumer/report module + tests. It reads existing profile data and emits a structured report; it does **not** modify the startup service producer (`scripts/session_self_initialization.py`), the `gt` CLI (`cli.py`), or the init-keyword disclosure path. Finer hook/event-source capture (recording additional producer sections beyond the current two) is deliberately **out of scope** for Slice A and noted as a possible Slice B that would touch the producer.

## Specification Links

- **GOV-SESSION-SELF-INITIALIZATION-001** (verified) — governs the fresh-session self-initialization payload; the budget report gives the owner/operator by-harness visibility into that payload's cost, a stated self-initialization concern (token-consumption reduction).
- **DCL-SESSION-STARTUP-TOKEN-BUDGET-001** (verified) — the startup token-budget constraint; the report computes per-harness token/byte budgets and the mandatory-vs-expandable split that this DCL motivates. This is the report's primary derived-from spec.
- **DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001** (specified) — defines the compact-`additionalContext` (mandatory routing facts) vs relayed-`startupDisclosure` (expandable demand-loaded detail) split; the report's mandatory/expandable classification reflects exactly this architecture.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the report is read-only over `.gtkb-state/` runtime data and writes only a non-canonical runtime report; it touches no bridge authority surface.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — PAUTH, project, work item, target paths, and governing specs are concretely linked in the header and here.
- **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — machine-readable `Project Authorization:` / `Project:` / `Work Item:` lines are present in the header.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan below maps each linked spec/acceptance criterion to an executed test.
- **GOV-STANDING-BACKLOG-001** — WI-4360 is the backlog authority for this slice; no other WI is claimed.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001** — implementation proceeds under the active `PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-STARTUP-PAYLOAD-PROFILER-IMPLEMENTATION-AUTHORIZATION` (which includes WI-4360 and authorizes `source_file` + `test_file` mutation classes) plus this Loyal Opposition GO and an implementation-start packet.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both `target_paths` are in-root under `E:\GT-KB`; no application/adopter surface is touched.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — the work is a durable tracked artifact; the deferred Slice B is named explicitly rather than silently dropped.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`, `GOV-SESSION-SELF-INITIALIZATION-001`, and `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` define the startup-payload budgeting and compact/disclosure architecture this report measures. The PAUTH `scope_summary` explicitly states "no formal spec/GOV/ADR/DCL mutation," confirming no new or revised formal specification is required for this slice. The work is a deterministic measurement/report over an already-specified, already-VERIFIED data contract (`gtkb-startup-payload-profile-v1`).

## Prior Deliberations

- **`bridge/gtkb-startup-payload-profiler-compact-context-006.md`** (VERIFIED, WI-4361) — the foundation thread. Shipped the compact/disclosure split + per-session payload-profile instrumentation and explicitly left WI-4360 open for "a later implementation report [that] explicitly closes it with its own authorization evidence." This proposal is that closure path.
- **`bridge/gtkb-startup-payload-profiler-compact-context-001.md`** (WI-4361 NEW) — establishes the `gtkb-startup-payload-profile-v1` contract and the "lightweight payload profiling as verification instrumentation" that WI-4360 consumes.
- **`DELIB-20260605-GLOSSARY-CLI-SCAN-DELTA-APPROVAL`** — the owner decision backing both the WI-4361 COMPACT-AUTO-DISPATCH PAUTH and the WI-4360 STARTUP-PAYLOAD-PROFILER PAUTH that authorizes this work.
- **`gtkb-fab-21-startup-load-cost-reduction`** (VERIFIED) — related startup-load-cost-reduction program; motivates per-harness startup budgeting visibility.
- A deliberation search for "startup payload profiler budget report by harness" surfaced no thread proposing the by-harness comparative budget report; WI-4361 explicitly scoped it out. This is the first proposal for the WI-4360 report deliverable, not a revisit of a rejected approach.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-20260605-GLOSSARY-CLI-SCAN-DELTA-APPROVAL`** — the owner decision recorded as `owner_decision_deliberation_id` on the active `PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-STARTUP-PAYLOAD-PROFILER-IMPLEMENTATION-AUTHORIZATION`, whose `scope_summary` authorizes exactly "Implement WI-4360 startup payload profiler and budget report by harness in the startup service/tests; no formal spec/GOV/ADR/DCL mutation; preserve interactive init-keyword disclosure behavior."
- The slice stays strictly within the PAUTH's `allowed_mutation_classes` (`source_file`, `test_file`) and respects both `forbidden_operations`: it performs no `formal_artifact_mutation_without_packet` (no GOV/ADR/DCL/SPEC creation) and causes no `init_keyword_disclosure_regression` (it is a read-only consumer that never touches the disclosure-generation path). No expanded owner authorization is requested.

## Design (Slice A)

New module `scripts/startup_payload_budget_report.py`:

- **Frozen value objects** (`dataclass(frozen=True)`): `SectionMetrics` (name, utf8_bytes, rough_token_estimate, line_count, character_count, klass), `HarnessBudget` (harness_id, harness_name, role_profile, total_bytes, total_tokens, mandatory_bytes/tokens, expandable_bytes/tokens, sections), and `BudgetReport` (contract_version, generated_at, harnesses, totals, unknown_sections).
- **Pure functions:**
  - `classify_section(name) -> Literal["mandatory", "expandable"]` — maps a section name to its class via a documented `SECTION_CLASS` map: `additionalContext` → `mandatory` (compact routing facts), `startupDisclosure` → `expandable` (demand-loaded detail), reflecting `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`. Unknown section names default to `expandable` and are surfaced in `BudgetReport.unknown_sections` so a future producer section is flagged, never silently mis-bucketed.
  - `build_harness_budget(profile_dict) -> HarnessBudget` — pure; aggregates one profile record's `sections` into per-class byte/token totals.
  - `build_budget_report(profiles, *, now) -> BudgetReport` — pure; aggregates a list of profile dicts into a by-harness report sorted deterministically by `harness_name`, with cross-harness totals. `now` (UTC ISO string) is injected for determinism.
  - `render_markdown(report) -> str` — pure; renders a by-harness comparison table (bytes, tokens, mandatory/expandable split) plus an unknown-sections note when present.
- **Thin I/O wrapper:** `load_profiles(profiles_dir) -> list[dict]` reads `last-*.json`, accepts only records whose `contract_version == "gtkb-startup-payload-profile-v1"` (others skipped, reported), and never mutates inputs. `CONTRACT_VERSION = "gtkb-startup-payload-profile-v1"` is a documented module constant that must track the producer's contract (drift is detectable via the version field and asserted in tests).
- **`main(argv=None)`** entrypoint runnable via `python scripts/startup_payload_budget_report.py`: reads `.gtkb-state/startup-payload-profiles/`, builds the report, and writes `budget-report.json` + `budget-report.md` into that same gitignored runtime dir (a `generated_runtime_file`), or prints to stdout with `--stdout`. No write to any canonical/tracked path.
- **Determinism:** the compute core is pure with `now` injected; no `Date.now`/random; harnesses sorted by name; identical inputs + identical `now` produce byte-identical output.

The module imports nothing from the 7291-line `scripts/session_self_initialization.py` (decoupled consumer); it reads the stable versioned JSON contract only.

## Verification Plan (Specification-Derived)

| Spec / Acceptance criterion | Test (in `platform_tests/scripts/test_startup_payload_budget_report.py`) | Method |
|---|---|---|
| DCL-SESSION-STARTUP-TOKEN-BUDGET-001 — per-harness byte/token budgets | `test_build_report_by_harness`, `test_cross_harness_totals` | fixture profiles (claude, codex) → assert per-harness + total byte/token aggregation |
| DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 — mandatory vs expandable split | `test_mandatory_vs_expandable_classification`, `test_unknown_section_flagged_and_defaulted` | assert `additionalContext`→mandatory, `startupDisclosure`→expandable; unknown section flagged in `unknown_sections` and defaulted to expandable |
| GOV-SESSION-SELF-INITIALIZATION-001 — deterministic, replayable report | `test_determinism_same_input_same_output`, `test_render_markdown_shape` | same profiles + same `now` → byte-identical JSON+markdown; markdown has a row per harness + class columns |
| Contract integrity (`gtkb-startup-payload-profile-v1`) | `test_load_skips_non_contract_json`, `test_contract_version_constant` | non-contract JSON ignored; module `CONTRACT_VERSION` equals the value emitted in `.gtkb-state/startup-payload-profiles/last-*.json` |
| Read-only / robustness | `test_empty_profiles_dir_returns_empty_report`, `test_inputs_not_mutated` | empty dir → empty report (no crash); input dicts unchanged after compute |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on both changed files; `python -m pytest platform_tests/scripts/test_startup_payload_budget_report.py -q --tb=short`; plus a smoke run `python scripts/startup_payload_budget_report.py --stdout` against the live profiles.

## Risk / Rollback

- **Risk: low.** Slice A is additive (2 new files), read-only over `.gtkb-state/` runtime data, and writes only a gitignored runtime report. It cannot alter canonical state, the startup producer, the `gt` CLI, or the init-keyword disclosure path — so it cannot cause an `init_keyword_disclosure_regression`.
- **Contract-drift risk:** if a future producer change renames the contract or adds sections, the report flags unknown sections and the `test_contract_version_constant` test catches a version rename. Mitigation is built into the design, not deferred.
- **Concurrency:** none introduced — no producer/CLI/INDEX write-path change.
- **Rollback:** delete the two new files. No migration, no KB mutation, no canonical artifact changed. Any `budget-report.*` under `.gtkb-state/` is gitignored runtime state and may be left in place.

## Recommended Commit Type

`feat:` — adds a net-new deterministic startup-payload budget-report module plus a comprehensive test suite; no behavior change to existing commands, no canonical/producer change, no disclosure-path change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
