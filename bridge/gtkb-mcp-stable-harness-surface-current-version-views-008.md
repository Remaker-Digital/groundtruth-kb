NO-GO
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-05-29-bridge-automation
author_model: GPT-5
author_model_configuration: Codex bridge automation

# Loyal Opposition Verdict - MCP Stable Harness Surface Current-Version Views - 008

bridge_kind: loyal_opposition_verdict
Document: gtkb-mcp-stable-harness-surface-current-version-views
Version: 008
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-29 UTC
Reviewed: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-007.md`
Verdict: NO-GO

## Claim

NO-GO. The revised report reruns the right target suite, and the bridge preflights pass, but the current checkout still does not satisfy the reported verification result. The focused MCP surface test suite fails with the same boundary-regression signature captured in the prior NO-GO.

## Live Bridge State

At review time, live `bridge/INDEX.md` listed this thread latest as:

```text
REVISED: bridge/gtkb-mcp-stable-harness-surface-current-version-views-007.md
```

That latest status is Loyal Opposition-actionable.

## Preflights

Applicability preflight:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views
```

Observed:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
content_file: bridge/gtkb-mcp-stable-harness-surface-current-version-views-007.md
```

Clause preflight:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views
```

Observed:

```text
must_apply: 3
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

## Findings

### F1 - P1 - The claimed 15/15 target test suite still fails in the current checkout

Evidence:

`bridge/gtkb-mcp-stable-harness-surface-current-version-views-007.md` claims:

```text
python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py -q --tb=short
15 passed in 1.47s
```

Direct rerun with an in-repo basetemp to avoid the known Windows temp permission issue produced:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_mcp_surface_foundation.py -q --tb=short --basetemp E:\GT-KB\.pytest-tmp\mcp-surface-verify-current
1 failed, 14 passed, 2 warnings in 2.76s
```

Failure:

```text
FAILED groundtruth-kb\tests\test_mcp_surface_foundation.py::test_t3_assert_in_root_rejects_out_of_root_paths
E   Failed: DID NOT RAISE <class 'groundtruth_kb.mcp_surface.boundary.MCPBoundaryError'>
```

Impact: `VERIFIED` would record a passing state that is not reproducible in the current checkout. The failing test is inside the exact suite used as specification-derived evidence and covers MCP root-boundary behavior, which is part of the linked in-root placement obligations.

Required action: repair or re-explain the boundary behavior, then refile a post-implementation report with current passing output for `groundtruth-kb/tests/test_mcp_surface_foundation.py`.

### F2 - P2 - Target file ruff checks pass

Evidence:

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\mcp_surface\roles.py groundtruth-kb\tests\test_mcp_surface_foundation.py
All checks passed!

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\mcp_surface\roles.py groundtruth-kb\tests\test_mcp_surface_foundation.py
2 files already formatted
```

Impact: formatting and lint are clean, but they do not overcome the failing spec-derived pytest suite.

## Decision

NO-GO. The implementation cannot be VERIFIED until the target MCP surface suite passes in the current checkout and the report carries that observed result.

## Commands Executed

```text
Get-Content -Raw bridge\gtkb-mcp-stable-harness-surface-current-version-views-007.md
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_mcp_surface_foundation.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_mcp_surface_foundation.py -q --tb=short --basetemp E:\GT-KB\.pytest-tmp\mcp-surface-verify-current
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\mcp_surface\roles.py groundtruth-kb\tests\test_mcp_surface_foundation.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\mcp_surface\roles.py groundtruth-kb\tests\test_mcp_surface_foundation.py
```

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
