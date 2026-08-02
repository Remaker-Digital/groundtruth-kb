NEW
::init gtkb pb

author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-07-31T19-46-49Z
author_model: unknown
author_model_version: unknown
author_model_configuration: Goose Desktop harness; resolved role prime-builder per ::init gtkb pb transcript keyword

bridge_kind: prime_proposal
Document: gtkb-wi584x-codex-home-harness-selector-false-positive
Version: 001
Date: 2026-07-31 UTC
Author: Prime Builder (Goose, harness G)

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5842 (to be created)

target_paths: ["scripts/bridge_work_intent_registry.py"]

implementation_scope: bug_fix
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Implementation Proposal — CODEX_HOME false-positive in _worker_harness_selector()

## Defect

`scripts/bridge_work_intent_registry.py:743`:

```python
if os.environ.get("CODEX_THREAD_ID") or os.environ.get("CODEX_HOME"):
    return "codex"
```

`CODEX_HOME` (`C:\Users\micha\.codex`) is a permanent installation path, not a
runtime session signal. It is always set on this workstation regardless of
which harness is active. The selector therefore returns `"codex"` for Goose
sessions, routing `resolve_worker_role_provenance()` into the Codex harness
envelope directory. The Goose envelope `G-2026-07-31T19-46-49Z` does not
exist under `harness-state/codex/session-envelopes/`, so the claim kernel
rejects the session with:

> Worker role provenance session id does not match the current session.

## Reproducer (Goose harness G, 2026-07-31)

```
$ set GTKB_SESSION_ID=G-2026-07-31T19-46-49Z
$ python scripts/bridge_claim_cli.py claim gtkb-wi5628-deepseek-v4-flash-route-reconciliation
ERROR: go_implementation claim requires a prime-builder harness;
session 'G-2026-07-31T19-46-49Z' resolves to worker session document rejected:
Worker role provenance session id does not match the current session.
(not prime-eligible)
```

## Root Cause Trace

1. `_worker_harness_selector()` evaluates `CODEX_HOME` (line 743) → returns `"codex"`.
2. `_resolve_worker_role("G-2026-07-31T19-46-49Z")` passes `harness_name="codex"` to
   `resolve_worker_role_provenance()`.
3. `resolve_worker_role_provenance()` looks for
   `harness-state/codex/session-envelopes/G-2026-07-31T19-46-49Z.json` —
   finds only `harness-state/codex/session-envelopes/bba2e933....json`.
4. Raises `EnvelopeError("Worker role provenance session id does not match the current session.")`.

## Fix

Remove `CODEX_HOME` from the Codex detection condition at line 743.

**Before:**
```python
    if os.environ.get("CODEX_THREAD_ID") or os.environ.get("CODEX_HOME"):
        return "codex"
```

**After:**
```python
    if os.environ.get("CODEX_THREAD_ID"):
        return "codex"
```

`CODEX_THREAD_ID` is a runtime session signal set only during active Codex
sessions. It correctly identifies a live Codex harness. `CODEX_HOME` is a
static installation path and has no session-detection value.

## Verification

- After fix, `_worker_harness_selector()` returns `None` when no harness
  session env var is present, causing `resolve_worker_role_provenance()` to
  scan all harness directories — it will find the Goose envelope.
- The `GTKB_HARNESS_NAME=goose` explicit workaround continues to work as
  before (takes highest precedence at line 740).
- No other consumer of `CODEX_HOME` is affected; this is a one-line change.
- Related test: verify `_worker_harness_selector()` returns `None` when
  `CODEX_HOME` is set but no session env var is present.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — claim role eligibility depends on correct
  harness selection.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — fix is
  specification-conformant (no spec change required).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — test coverage TBD.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.