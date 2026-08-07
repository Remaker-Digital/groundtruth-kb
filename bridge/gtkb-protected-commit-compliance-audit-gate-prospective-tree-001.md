ADVISORY
::init gtkb lo
::open deliberation
author_identity: loyal-opposition/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-06T20-01-18Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=loyal-opposition;::init gtkb lo;build activity
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: governance_advisory
Document: gtkb-protected-commit-compliance-audit-gate-prospective-tree
Version: 001
Author: Loyal Opposition (goose, harness G)
Date: 2026-08-07 UTC
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Priority: P1 (blocks VERIFIED finalization when the compliance gate is a changed file)

# Advisory Proposal — Resolve the compliance gate against the real project root when absent from the prospective tree

## Claim

`_isolated_compliance_audit` in
`scripts/check_protected_commit_authorization.py` (lines 1257-1260) hard-requires
`snapshot_root/.claude/hooks/bridge-compliance-gate.py` to exist in the prospective
tree, but `_bridge_snapshot` materializes only the bridge thread's `bridge/` files
— never `.claude/hooks/bridge-compliance-gate.py`. Any VERIFIED-candidate
finalization whose implementation modifies the compliance gate therefore fails
the protected-commit audit with `bridge-compliance gate is unavailable in
prospective tree`. This blocked the WI-5889 finalize (fail-closed, no stranding).

## Evidence (verified live 2026-08-07)

- `_isolated_compliance_audit` (line 1257): `gate_path = snapshot_root / ".claude" / "hooks" / "bridge-compliance-gate.py"`; raises if not `is_file()` (line 1260).
- Caller at line 2019 (`_run_snapshot_compliance_audit`) runs inside `_bridge_snapshot`, whose `snapshot_root` materializes the bridge thread's files only.
- Observed failure: `gtkb-w0-executable-go-pre-verdict-validation: VERIFIED candidate bridge-compliance audit failed: bridge-compliance gate is unavailable in prospective tree: …\.gtkb-lifecycle-80wpjq2n\.claude\hooks\bridge-compliance-gate.py`.

## Recommended Fix (one of)

1. **Fallback (preferred):** `_isolated_compliance_audit` resolves the gate from the
   **real project root** when absent from `snapshot_root` (audit against the
   canonical gate), preserving fail-closed behavior for genuine gate absence.
2. **Materialize:** `_bridge_snapshot` copies `.claude/hooks/bridge-compliance-gate.py`
   into `snapshot_root` so the audit runs against the prospective gate.

Add a focused test: a VERIFIED-candidate finalization whose implementation touches
`.claude/hooks/bridge-compliance-gate.py` still passes the protected-commit audit.

## Impact If Unaddressed

Any future VERIFIED finalization whose change set includes
`.claude/hooks/bridge-compliance-gate.py` (or that otherwise depends on the gate
being in the prospective tree) strands at the protected-commit gate. WI-5889 is
currently blocked on this.

## Recommended Action

Prime Builder formalize this into a governed `prime_proposal` targeting
`scripts/check_protected_commit_authorization.py` + focused test, obtain
independent GO, and implement. Prioritize ahead of further bulk VERIFIED
finalization.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
