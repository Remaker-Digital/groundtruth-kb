ADVISORY

author_identity: Antigravity
author_harness_id: C
author_session_context_id: ccaf0e73-2cd6-48a2-a66c-c426251fa8b5
author_model: Gemini 3.5 Flash (High)
author_model_version: 3.5
author_model_configuration: Default

bridge_kind: governance_advisory
Document: gtkb-lo-hourly-quality-scout-advisory
Version: 001
Author: Antigravity Loyal Opposition
Date: 2026-05-29 UTC

## Source

Harness-level scheduled task `ccaf0e73-2cd6-48a2-a66c-c426251fa8b5/task-54` hourly spot check of the GT-KB system.

## Summary

This read-only spot check scanned the `E:\GT-KB` repository for platform discrepancies, linter errors, and test failures. Three high-value issues affecting platform validation, developer workspace compatibility, and core linter gating were identified.

## Claim

The core platform test suite, local Windows development environments, and package-level build validation suffer from latent, easily remediable gate failures that should be resolved to prevent deployment and workflow blocks.

## Inspected Surfaces

- Git status, branch configuration, and diff statistics
- Core platform tests under `platform_tests/`
- Local Windows repository line-ending state
- Package-level style checks using `ruff check` in `groundtruth-kb/src/`
- Bridge status registry (`bridge/INDEX.md`)

---

## Detailed Findings

### Finding 1: Mode-Switch Unit Test Suite Failures (P1)

* **Claim:** The mode-switch unit tests fail because their mock dictionaries omit the `"status": "active"` key, which the newly migrated production code (`invariants.py` and `derive.py`) requires to filter active harnesses.
* **Evidence:**
  * Running the test suite produces multiple failures in:
    * `platform_tests\groundtruth_kb\test_mode_switch_derive_role_slot.py` (failures: `test_role_slot_singleton_prime`, `test_role_slot_singleton_lo`, and `test_role_slot_legacy_scalar_role`).
    * `platform_tests\groundtruth_kb\test_mode_switch_invariants.py` (failures: `test_prime_builder_ids_single` and `test_verify_role_partition_accepts_valid_partition`).
  * `prime_builder_ids` in `invariants.py` and `role_slot_from_active_harness` in `derive.py` perform `record.get("status") == "active"` lookups. Since the mock dictionaries constructed in the unit tests lack this property, the tests fail to resolve active harnesses.
* **Risk/Impact:** Blocks green CI/CD builds for any `groundtruth-kb` modifications and prevents deterministic verification of the mode-switch subsystem.
* **Recommended Action:** Update the mode-switch test dictionary fixtures in both test files to include `"status": "active"` and update the `_write_role_map` helper in `test_mode_switch_invariants.py` to add `"status": "active"` by default.
* **Owner Decision Needed:** No.

---

### Finding 2: Hard-Block Compliance Gate Test Failures on Windows Due to LF vs CRLF Byte Mismatches (P2)

* **Claim:** Byte-level SHA-256 hash comparison in `test_hook_matches_template_or_documented_divergence` fails on Windows because of automatic git line-ending conversions (`\r\n` vs `\n`).
* **Evidence:**
  * `platform_tests\hooks\test_bridge_compliance_gate_hard_block_workspace.py`'s `test_hook_matches_template_or_documented_divergence` reads raw bytes (`path.read_bytes()`) to compare the active hook with the template.
  * Git automatic replacement of LF with CRLF causes the active hook's hash to differ on Windows hosts, failing the byte-for-byte assertions.
* **Risk/Impact:** False-positive test failures on Windows machines, hindering local developer workflows and causing validation mismatches.
* **Recommended Action:** Update the assertion logic or `_file_sha256` in the test to normalize line endings (e.g., read as text using `read_text(encoding="utf-8")` and normalize `\r\n` to `\n` before hashing) instead of checking raw binary bytes.
* **Owner Decision Needed:** No.

---

### Finding 3: Failing core `groundtruth-kb` Linter Gating (`make lint` / `ruff check`) (P2)

* **Claim:** Running the linter gate `make lint` inside the `groundtruth-kb` package directory fails because of a few formatting and styling violations.
* **Evidence:**
  * Running `python -m ruff check groundtruth-kb/src/` outputs 8 style violations:
    * Line too long (122 > 120) in `cli.py:127:121` and `intake.py:280:121`.
    * `UP042 Class AuthorityLabel inherits from both str and enum.Enum` in `groundtruth_kb/mcp_surface/authority.py` (violates pyupgrade check).
    * Trailing whitespaces and unsorted imports in `hygiene/sweep.py` and `db.py`.
* **Risk/Impact:** Prevents `make check` and the CI linter gate from passing for any new pull request or release candidate within the core platform toolkit.
* **Recommended Action:**
  1. Shorten the line length of the click option in `cli.py` and the `attachment` definition in `intake.py`.
  2. Update `AuthorityLabel` in `authority.py` to inherit from `enum.StrEnum` instead of `(str, Enum)`.
  3. Format imports using `ruff check --fix` and remove trailing whitespaces.
* **Owner Decision Needed:** No.

---

## Recommended Prime Builder Disposition

The Loyal Opposition recommends that Prime Builder **convert all 3 findings to implementation proposals** in the next development cycle to ensure a green, cross-platform build pipeline. 

No owner decisions are blocking these items. They represent standard platform debt and hygiene corrections.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
