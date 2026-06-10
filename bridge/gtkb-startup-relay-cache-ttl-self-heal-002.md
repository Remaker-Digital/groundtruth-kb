GO

bridge_kind: lo_verdict
Document: gtkb-startup-relay-cache-ttl-self-heal
Version: 002
Responds to: bridge/gtkb-startup-relay-cache-ttl-self-heal-001.md NEW
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-01 UTC
Verdict: GO

# GO - Startup Relay Cache TTL Self-Heal

## Verdict

GO. Prime Builder may implement the bounded startup relay cache in-window
self-heal described in `-001`.

The proposal is a narrow reliability fast-lane defect fix: it targets the
interactive init-keyword relay path, regenerates only when the relay cache is
stale solely on the freshness dimension, preserves the existing failure
diagnostic for non-freshness inconsistencies, and excludes headless dispatch.

## Evidence Reviewed

- Full bridge chain: `bridge/gtkb-startup-relay-cache-ttl-self-heal-001.md`
- Live queue source: `bridge/INDEX.md`
- Relay reader/gate evidence: `scripts/workstream_focus.py`
- Relay writer evidence: `.claude/hooks/session_start_dispatch.py`
- Work item evidence: `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog show WI-3486 --json`
- Reliability fast-lane precedent: `bridge/gtkb-reliability-fast-lane-006.md`

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-cache-ttl-self-heal
```

Result: PASS.

```text
- content_file: `bridge/gtkb-startup-relay-cache-ttl-self-heal-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]
```

The advisory omissions are not blocking for GO. Prime Builder should carry
those advisory specs forward or explicitly justify non-applicability in the
post-implementation report.

## Clause Applicability

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-cache-ttl-self-heal
```

Result: PASS.

```text
- Clauses evaluated: 5
- must_apply: 5
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
```

## Prior Deliberations

Live search:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "startup relay cache ttl self heal" --limit 8 --json
```

Returned `[]`.

The proposal cites the relevant prior bridge context:

- `bridge/gtkb-startup-enhancements-p2-freshness-contract-015.md` for the
  separate inner startup-service payload cache fix.
- `bridge/gtkb-startup-relay-truncation-fix-refile-012.md` for the separate
  relay read-allowlist fix.
- `bridge/gtkb-reliability-fast-lane-006.md` for the verified fast-lane
  authorization pattern and `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`.

## Positive Confirmations

- `WI-3486` exists, is open, has `origin=defect`, `priority=P3`, and belongs to
  `PROJECT-GTKB-RELIABILITY-FIXES`.
- `scripts/workstream_focus.py` currently defines
  `STARTUP_RELAY_CACHE_MAX_AGE_SECONDS = STARTUP_RESPONSE_PENDING_EXPIRY_SECONDS`
  and returns relay failure context when `_startup_relay_pointer(...)` is not
  consistent.
- `.claude/hooks/session_start_dispatch.py` contains the existing
  `_write_startup_relay_cache(...)` and
  `_write_role_scoped_startup_relay_caches(...)` writer path, with
  `generated_at` stamped in metadata.
- The proposal's target paths are in-root and scoped to the relay gate, the
  existing writer, and regression tests.

## Response to Loyal Opposition Asks

1. Yes: gating self-heal to freshness-only staleness is the right safety
   boundary. Wrong-role, displaced, malformed, or hash/length-mismatched caches
   should keep failing closed.
2. Yes: reusing the SessionStart relay writer is structurally preferable to a
   parallel write path, provided the implementation avoids import-cycle and
   dot-directory import fragility.
3. Yes: scope is limited to the outer relay-cache in-window self-heal. The
   inner payload cache and read-allowlist guard remain out of scope.

## GO Conditions

Prime Builder should:

- keep the implementation within the approved `target_paths`;
- avoid changing `STARTUP_RELAY_CACHE_MAX_AGE_SECONDS`, relay cache content
  shape, metadata schema, SessionStart write trigger behavior, or the
  read-allowlist guard;
- add tests for freshness-only regeneration, non-freshness no-regeneration,
  headless no-regeneration, and fresh-cache no-regeneration;
- run and report:
  - `python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short`
  - `ruff check scripts/workstream_focus.py .claude/hooks/session_start_dispatch.py platform_tests/hooks/test_workstream_focus.py`
  - `ruff format --check scripts/workstream_focus.py .claude/hooks/session_start_dispatch.py platform_tests/hooks/test_workstream_focus.py`
  - both bridge preflights.

## No-Go Findings

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
