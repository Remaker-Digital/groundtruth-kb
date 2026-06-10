REVISED

# Implementation Proposal — GT-KB Platform Observability and Hygiene

**Status:** REVISED
**Document name:** `gtkb-platform-observability-hygiene`
**Version:** 003
**Author:** Prime Builder (antigravity/pb)
**Session:** S509 (2026-06-09)
**Builds on:** [LOYAL-OPPOSITION-LOG.md](file:///E:/GT-KB/independent-progress-assessments/LOYAL-OPPOSITION-LOG.md) entries from 2026-06-04 ("LO autonomous /loop: empty queue + bridge_kind taxonomy drift" and "Ollama Harness Integration & Routing Investigation").

## Specification Links

- [GOV-FILE-BRIDGE-AUTHORITY-001](file:///E:/GT-KB/config/governance/gov-file-bridge-authority-001.md) — Live bridge index authority and permanent bridge repair authority.
- [DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Bridge proposal spec linkage must be relevance-complete.
- [DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Verification must execute spec-derived tests.
- [GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Sessions actively inform and engage the user.
- [GOV-SOURCE-OF-TRUTH-FRESHNESS-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — State claims derive from fresh canonical reads.
- [ADR-ISOLATION-APPLICATION-PLACEMENT-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Placement contract for application isolation.
- [DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Artifact lifecycle transitions and validation triggers.
- [GOV-ARTIFACT-ORIENTED-GOVERNANCE-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Governance over design, specification, and implementation records.

## Implementation Scope

- **Project:** `PROJECT-GTKB-PLATFORM-OBSERVABILITY-HYGIENE`
- **Work Item:** `WI-4340`
- **Project Authorization:** `PAUTH-PROJECT-GTKB-PLATFORM-OBSERVABILITY-HYGIENE-IMPL`
- **Requirement Sufficiency:** Existing requirements sufficient
- **target_paths:**
  - `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
  - `scripts/check_harness_parity.py`
  - `scripts/cross_harness_bridge_trigger.py`

All target paths and implementation artifacts reside under the project root (`E:\GT-KB`), satisfying the in-root requirement of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Proposed Design Constraints

- **DCL-DISPATCH-STATE-STALENESS-THRESHOLD-001:** The project doctor shall report a staleness warning if `.gtkb-state/bridge-poller/dispatch-state.json` is older than 1 hour during active sessions. This is derived from the fresh-canonical-read requirement of [GOV-SOURCE-OF-TRUTH-FRESHNESS-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) to prevent sessions from relying on stale dispatch states.

## Proposed Changes

### 1. Project Doctor Staleness Check
- Modify `_check_bridge_dispatch_liveness` in `groundtruth-kb/src/groundtruth_kb/project/doctor.py` to raise a `warning` if the `dispatch-state.json` file's `updated_at` timestamp is older than 1 hour.

### 2. Poller Temporary File Hygiene
- In `scripts/cross_harness_bridge_trigger.py` (and any startup cleanup code), filter `*.tmp` file deletions in `.gtkb-state/bridge-poller/` to only target files older than 5 minutes. This ensures concurrent active writes (which use `.tmp` suffixes before rename) are not disrupted.

### 3. Dynamic Harness Parity
- In `scripts/check_harness_parity.py`, query `load_harness_projection` to dynamically determine the list of known harnesses instead of using a hardcoded tuple.

## Specification-Derived Verification Plan

- **Test for Doctor Staleness Warning:** Verify that `_check_bridge_dispatch_liveness` returns a warning when `dispatch-state.json` is older than 1 hour.
- **Test for Temporary File Cleanup Safety:** Verify that trigger cleanup does not touch `.tmp` files newer than 5 minutes.
- **Test for Dynamic Harness Parity:** Verify that `scripts/check_harness_parity.py` correctly handles dynamic harnesses returned by the projection.

### Automated Tests
- Run `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short`

## target_paths

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `scripts/check_harness_parity.py`
- `scripts/cross_harness_bridge_trigger.py`

## Requirement Sufficiency

Existing requirements sufficient

