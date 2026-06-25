NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: da5d93b8-0408-4770-ad6f-00b65fe21530
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory; mode=auto
author_metadata_source: interactive-prime-session

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4798

# INDEX.md Residue Strip — Retired-Queue Tests (non-guard) Tranche (WI-4798)

Document: gtkb-index-md-strip-tests
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4798
Recommended commit type: fix

## Summary

Second strip tranche (S2) under the GO-terminal classification contract
(`gtkb-index-md-classified-inventory`). Per-test triage of all 28 `bridge/INDEX.md`
occurrences across 17 `groundtruth-kb/tests/**` files found that exactly **one** asserts
retired-queue `bridge/INDEX.md` behavior; the rest are KEEP (current post-cutover
behavior, incidental fixtures/data, or guard tests). The single STRIP target,
`test_cli_authority.py::test_authority_resolve_bridge_index_json_includes_authority_fields`,
is **currently failing** because the bridge-queue authority was already migrated off
`bridge/INDEX.md` but its test was not updated — a textbook obsolete-reference residue.

This tranche updates that one test to the current authority model and documents the
KEEP majority. It is a `fix` (repairs a failing test), not a feature.

## Specification Links

- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (v1, specified) — the STRIP set's obsolete
  reference (the stale bridge-index authority assertion) is removed for the S2 surface.
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` (v1, specified) — paired purge work for
  the `bridge/INDEX.md` retirement; this failing test is exactly the residue the obligation
  targets (a retirement that left an un-paired obsolete reference).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — links cited; verification derives.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the post-impl report runs the updated
  test green; mapping below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed as the next numbered bridge file
  (`bridge/gtkb-index-md-strip-tests-001.md`) in the append-only versioned chain; the test is
  updated to assert the canonical TAFE/dispatcher authority model this spec defines.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the updated test asserts the current authoritative
  source, not the retired aggregate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (CLAUSE-IN-ROOT) — the target path is in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — lifecycle artifact of the retirement trigger.

## Prior Deliberations

- `gtkb-index-md-classified-inventory` (GO -002, terminal) — the STRIP/KEEP/QUARANTINE contract;
  S2 is the tests surface; the per-test triage applies its decision rule.
- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` (v1) — owner authorization (AUQ Q1).
- `gtkb-obsolete-reference-purge-methodology-adr-dcl` (GO -004, terminal) — the methodology ADR/DCL.
- `gtkb-index-md-strip-docs` (-001, sibling S1 tranche) — the docs surface; this is its tests peer.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are the GO-terminal classification
contract plus the methodology ADR/DCL. No new requirement.

## Target Paths

target_paths: ["groundtruth-kb/tests/test_cli_authority.py"]

## Per-Test Triage (deterministic, per the contract's decision rule)

**STRIP/UPDATE (1):**

- `test_cli_authority.py::test_authority_resolve_bridge_index_json_includes_authority_fields`
  — asserts `gt authority resolve "bridge index"` returns `status=resolved` with
  `authoritative_source == "bridge/INDEX.md"`. Live behavior: exit 1, `status=not_found`
  ("bridge index" no longer resolves; the bridge-queue authoritative_source migrated off
  `bridge/INDEX.md`). **Currently failing.** Update to the current authority model: assert the
  current bridge-queue resolution (resolve a live candidate term, e.g. `"bridge queue"`, and
  assert its current `authoritative_source`) and that the retired `"bridge index"` term resolves
  `not_found`. Exact current values are read from the live config at implementation time.

**KEEP — assert current post-cutover behavior (stripping would break the cutover):**

- `test_scaffold_bridge_index.py`, `test_scaffold_smoke.py` — assert scaffold does NOT create
  `bridge/INDEX.md` (current no-index behavior).
- `test_doctor_bridge_accuracy.py` (×4) — assert doctor accepts absent `bridge/INDEX.md`.
- `test_preflight_checks.py` (×3) — assert `enumerate_scaffold_outputs` lists `bridge/INDEX.md`
  as a managed path for dual-agent (path enumeration, not creation — consistent with the
  scaffold-absent tests above; no inconsistency).
- `test_governance_hooks.py` — asserts the no-INDEX fallback path works.
- `test_tafe_flow_type_lifecycle.py` — docstring states the test never touches `bridge/INDEX.md`.

**KEEP — incidental fixture/test data:**

- `test_mcp_surface_foundation.py` (×2), `test_inventory_string_scan.py` (×4),
  `test_hygiene_sweep_patterns.py`, `test_operating_state.py` (TOML fixture),
  `test_bash_enforcement_parser.py` (redirection-blocking fixture), `test_project_artifacts.py`
  (VERIFIED-bridge fixture), `framework/test_dispatch_state_recovery.py` (mock fixture),
  `adopter/test_registry_entry_present_for_every_scaffolded_file.py` (managed-file registry list).

**KEEP — guard (K2):**

- `framework/test_claude_directive_adapter.py` — exercises the guard on a `bridge/INDEX.md` Write.

**Defer → WI-4799 (skill-docs/templates):**

- `test_cli.py` (×2) — asserts the scaffolded `BRIDGE-INVENTORY.md` template contains
  `bridge/INDEX.md`. The template is a scaffold/skill-doc artifact; its disposition belongs to the
  S3 templates/skill-docs tranche (WI-4799). These tests update when that template updates.

**Out of S2 scope (KEEP, K2):** all ~37 `platform_tests/**` `bridge/INDEX.md` references are guard/
regression tests (protected-mutation-guard, bridge-compliance-gate, impl-start-gate, sdk-bash-guard,
etc.). A guard must name what it forbids; none are stripped.

## Verification Plan (Specification-Derived)

### Specification-Derived Verification — Spec-to-Test Mapping

| Linked spec / clause | Spec-to-test mapping | Command |
|----------------------|----------------------|---------|
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (STRIP set updated; obsolete bridge-index authority removed) | the updated `test_authority_resolve_*` asserts the current authority model and passes | `python -m pytest groundtruth-kb/tests/test_cli_authority.py -q --tb=short` |
| KEEP intact (no current-behavior/fixture/guard test altered) | the other 16 `groundtruth-kb/tests/**` files are untouched; re-scan shows their `bridge/INDEX.md` references unchanged | `python -m pytest groundtruth-kb/tests/ -q` (no new failures) + grep diff |
| Code quality | `ruff check` + `ruff format --check` on the changed test | `python -m ruff check groundtruth-kb/tests/test_cli_authority.py` ; `python -m ruff format --check <same>` |

## Risk / Rollback

- **Risk: the updated test asserts a value that drifts.** Mitigated by reading the current
  resolution from the live config at implementation time and asserting the structural authority
  fields, not just the literal string.
- **Risk: over-strip a KEEP test.** Mitigated by the explicit per-test triage above; only one file
  is in `target_paths`.
- **Rollback:** single-file change; revert restores the prior (failing) state. No other coupling.

## Owner Decisions / Input

Proceeds under the governed PAUTH; cites the AUQ-only rule.

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` (2026-06-24) — owner directive (AUQ Q1).
- AskUserQuestion (2026-06-25, this session) — "Full project scope" + "Keep building tranches" under
  `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25`.

One judgment is surfaced for LO review: whether updating `test_cli_authority.py` to the current
authority model (vs. removing the bridge-index-specific test outright) is the preferred disposition.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
