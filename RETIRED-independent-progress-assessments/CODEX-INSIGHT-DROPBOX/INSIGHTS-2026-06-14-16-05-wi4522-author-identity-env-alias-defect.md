# WI-4522 Author Identity Env Alias Defect

Generated: 2026-06-14 16:05 UTC
Reviewer: Codex Loyal Opposition, harness A
Specs: GOV-DOCUMENT-AUTHOR-PROVENANCE-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001
WIs: WI-4522, WI-4468
Bridge thread: `gtkb-wi4522-author-metadata-per-harness-resolution`

## Claim

WI-4522's verified implementation still has a reachable provenance defect:
`GTKB_HARNESS_NAME` is both the selector for durable harness lookup and an
environment alias for `author_identity`. When a filing environment supplies
`GTKB_HARNESS_NAME=claude` and the four runtime fields, `load_author_metadata()`
returns `author_identity: claude` instead of the registry-derived
`prime-builder/claude`.

This was found while verifying the latest `NEW` implementation report at
`bridge/gtkb-wi4522-author-metadata-per-harness-resolution-005.md`. A concurrent
worker filed `bridge/gtkb-wi4522-author-metadata-per-harness-resolution-006.md`
as `VERIFIED` before this finding could be recorded as a bridge NO-GO, so this
report preserves the evidence without rewriting the existing bridge artifact.

## Evidence

- `scripts/bridge_author_metadata.py:47` maps `GTKB_HARNESS_NAME` as an alias for
  `author_identity`.
- `scripts/bridge_author_metadata.py:339` merges
  `_resolve_durable_identity_fields(...)`, then
  `scripts/bridge_author_metadata.py:340` merges `_metadata_from_env(...)` over
  it.
- `GTKB_HARNESS_NAME` is a normal harness-name selector, not a canonical author
  identity string. Examples: `.codex/gtkb-hooks/session-start.cmd:2` sets
  `GTKB_HARNESS_NAME=codex`; `.claude/hooks/workstream-focus.py:24` defaults it
  to `claude`.

Live reproduction:

```powershell
@'
from pathlib import Path
from scripts.bridge_author_metadata import load_author_metadata
runtime={
 'GTKB_HARNESS_NAME':'claude',
 'GTKB_AUTHOR_SESSION_CONTEXT_ID':'ctx',
 'GTKB_AUTHOR_MODEL':'model',
 'GTKB_AUTHOR_MODEL_VERSION':'1',
 'GTKB_AUTHOR_MODEL_CONFIGURATION':'config',
}
print(load_author_metadata(Path(r'E:\GT-KB'), env=runtime))
'@ | python -
```

Observed result:

```text
{'author_identity': 'claude', 'author_harness_id': 'B', 'author_session_context_id': 'ctx', 'author_model': 'model', 'author_model_version': '1', 'author_model_configuration': 'config'}
```

Expected result under the GO'd WI-4522 design:

```text
author_identity: prime-builder/claude
author_harness_id: B
```

## Risk / Impact

The implementation removes the stale `current.json` baseline, but it still lets
a generic harness-name environment variable overwrite the durable
role-qualified author identity. Because `claude` is non-placeholder,
`validate_author_metadata()` accepts the value and the bridge artifact can be
stamped with a non-canonical author identity.

That weakens `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` and can confuse same-harness
review separation, provenance audits, and later bridge-author reconciliation.

## Recommended Action

Open a narrow follow-up bridge proposal or revise the current implementation
before relying on WI-4522 as closed:

1. Remove `GTKB_HARNESS_NAME` from `FIELD_ENV_NAMES["author_identity"]`, or make
   `_metadata_from_env()` ignore it for `author_identity` after durable identity
   resolution.
2. Preserve intentional explicit author identity overrides through
   `GTKB_AUTHOR_IDENTITY` / `GTKB_AUTHOR_NAME` if compatibility requires them.
3. Add a regression test that sets `GTKB_HARNESS_NAME=claude` plus the four
   runtime fields and asserts `author_identity == "prime-builder/claude"`.
4. Re-run:
   - `python -m pytest platform_tests/scripts/test_bridge_author_metadata.py -q --tb=short`
   - `python -m pytest platform_tests/scripts/test_bridge_author_metadata.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short`
   - `python -m ruff check scripts/bridge_author_metadata.py platform_tests/scripts/test_bridge_author_metadata.py`
   - `python -m ruff format --check scripts/bridge_author_metadata.py platform_tests/scripts/test_bridge_author_metadata.py`

## Decision Needed From Owner

None. This is a repair candidate for Prime Builder or bridge-function work.
