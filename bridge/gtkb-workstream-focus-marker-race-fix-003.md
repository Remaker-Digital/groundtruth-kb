REVISED

# Implementation Proposal — GT-KB Workstream Focus Marker Race Fix

**Status:** REVISED
**Document name:** `gtkb-workstream-focus-marker-race-fix`
**Version:** 003
**Author:** Prime Builder (antigravity/pb)
**Session:** S509 (2026-06-09)
**Builds on:** LO finding 2026-06-04 (Parallel Session Marker Race); no formal Deliberation Archive record exists for this finding.

## Specification Links

- [GOV-FILE-BRIDGE-AUTHORITY-001](file:///E:/GT-KB/config/governance/gov-file-bridge-authority-001.md) — Live bridge index authority and permanent bridge repair authority.
- [DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Bridge proposal spec linkage must be relevance-complete.
- [DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Verification must execute spec-derived tests.
- [ADR-ISOLATION-APPLICATION-PLACEMENT-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Placement contract for application isolation.
- [DCL-SESSION-ROLE-RESOLUTION-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Deterministic resolution table for interactive session role.
- [GOV-SESSION-ROLE-AUTHORITY-001](file:///E:/GT-KB/config/governance/adr-dcl-clauses.toml) — Session role authority split (durable registry vs interactive stated override).

## Implementation Scope

- **Project:** `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE`
- **Work Item:** `WI-3458` (remediation of Slice 2)
- **Project Authorization:** `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`
- **Requirement Sufficiency:** Existing requirements sufficient
- **target_paths:**
  - `scripts/workstream_focus.py`
  - `platform_tests/hooks/test_workstream_focus_session_role_marker.py`

All target paths and implementation artifacts reside under the project root (`E:\GT-KB`), satisfying the in-root requirement of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Proposed Design Constraints

- **DCL-SESSION-ROLE-MARKER-TTL-001:** The session-role marker file (`.claude/session/active-session-role.json`) is ephemeral. Its lifetime is restricted to the current interactive session: it is invalidated at any subsequent SessionStart event, and it is considered expired if its `written_at` timestamp is older than 30 minutes (1800 seconds).
- **DCL-MARKER-WRITE-CONCURRENCY-LOCK-001:** To prevent clobbering by concurrent active harness processes (e.g., in multi-harness topologies), writing to the session role marker MUST use an atomic filesystem-based lock file (`.claude/session/active-session-role.lock`) created exclusively. The write is rejected if an unexpired marker from a different `session_id` is present.

## Proposed Changes

### 1. Atomic Marker Write & Clobber Rejection
- Update `_write_session_role_marker` in `scripts/workstream_focus.py` to:
  1. Define a session marker lock path: `.claude/session/active-session-role.lock`.
  2. Implement a lock acquisition retry loop (e.g., up to 5 attempts, sleeping 0.1s between retries) using exclusive file creation (`open(lock_path, 'x')` or `os.O_CREAT | os.O_EXCL`).
  3. If lock is acquired:
     - Read the existing marker file `.claude/session/active-session-role.json` if present.
     - Parse its `written_at` timestamp and `session_id`.
     - Reject the new write (return `False`) if a valid, unexpired (age ≤ 1800s) marker from a different `session_id` already exists.
     - Otherwise, write the new marker file.
     - Finally, delete the lock file in a `finally` block.
  4. If lock acquisition fails after all retries, fail soft and return `False`.

### 2. Verify scripts/workstream_focus.py Presence
- `scripts/workstream_focus.py` is verified to exist in the repository as a shared utility module.

## Specification-Derived Verification Plan

- **Test for Atomic Lock Acquisition:** Verify that `_write_session_role_marker` waits/retries when the lock file exists.
- **Test for Clobber Rejection:** Verify that `_write_session_role_marker` rejects writing if a valid, unexpired marker from a different session id exists, but accepts it if the marker is expired, absent, or matches the same session id.
- **Test for Lock File Cleanup:** Verify that the lock file is deleted even if writing the marker throws an unexpected exception.

### Automated Tests
- Run `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/hooks/test_workstream_focus_session_role_marker.py -q --tb=short`

## target_paths

- `scripts/workstream_focus.py`
- `platform_tests/hooks/test_workstream_focus_session_role_marker.py`

## Requirement Sufficiency

Existing requirements sufficient

