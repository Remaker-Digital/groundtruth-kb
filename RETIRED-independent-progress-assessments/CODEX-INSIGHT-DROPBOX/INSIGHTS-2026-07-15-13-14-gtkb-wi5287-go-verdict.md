# INSIGHTS - WI-5287 DORA Track 2 Reconciliation Tests Self-Contained Proposal Review GO

**Date:** 2026-07-15 UTC
**Session:** 019f5f6d-60cd-7040-b73f-c7d23757c4bc
**Reviewer:** Loyal Opposition (antigravity, harness C)
**Verdict:** GO
**Target:** `bridge/gtkb-wi5287-dora-track2-self-contained-tests-001.md`

## Executive Summary

The Loyal Opposition reviewed the Prime Builder's proposal `gtkb-wi5287-dora-track2-self-contained-tests-001.md` to resolve six test failures in `platform_tests/scripts/test_dora_001b_track2_ingest.py`. The failures occur because production reconciliation guards check for the presence of `GTKB_DASHBOARD_AZURE_CONTAINER_APP_MAP` and `GTKB_DASHBOARD_AZURE_RESOURCE_GROUP` environment variables, which the test environment does not currently provide.

We reproduced the failures, verified that setting dummy env variables resolves the failures, and reviewed the proposed test-only scope. The proposal is sound, links correctly to governing specifications, and does not pose a regression risk to production code. We issued a `GO` verdict to authorize the Prime Builder's implementation.

## Review of Findings

### 1. Observation
Six unit tests (T8, T9, T10, T11, T13, and T14) in `test_dora_001b_track2_ingest.py` fail under clean environments because the production helper `_reconcile_against_azure_revisions` exits early with zero counts and prints a warning when two application-owned environment variables (`GTKB_DASHBOARD_AZURE_CONTAINER_APP_MAP` and `GTKB_DASHBOARD_AZURE_RESOURCE_GROUP`) are missing.

### 2. Deficiency Rationale
The tests do not establish the production environment preconditions before exercising the mocked CLI behavior, meaning they fail before reaching the logic they claim to assert. This violates `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` (tests must reach and mechanically exercise the named behavior).

### 3. Proposed Solution/Enhancement
We approved the proposed solution of introducing a pytest `monkeypatch` fixture in `test_dora_001b_track2_ingest.py` to supply mock environment mapping values. This ensures that the mock/stub tests can execute without requiring real Azure environment configurations or credentials.

### 4. Option Rationale
Adding local mock environment variables in the test fixture is the standard pattern for self-contained testing. Alternative approaches (such as changing production code to allow empty variables under test mode) would weaken the fail-closed production safety guards and violate non-impairment guidelines.

## Prime Builder Implementation Context

- **Objective:** Fix the six failing tests in `test_dora_001b_track2_ingest.py` by configuring env variables in test setup.
- **Touchpoints:** `platform_tests/scripts/test_dora_001b_track2_ingest.py`
- **Ordered sequence:**
  1. Define a pytest autouse fixture or add `monkeypatch` environment setting lines to `test_dora_001b_track2_ingest.py`.
  2. Run `pytest platform_tests/scripts/test_dora_001b_track2_ingest.py` to confirm all 18 tests pass.
  3. Validate using ruff check and formatting.
- **Rollback:** Revert modifications to `test_dora_001b_track2_ingest.py`.

Skills applied: proposal-review, lo-opportunity-radar
