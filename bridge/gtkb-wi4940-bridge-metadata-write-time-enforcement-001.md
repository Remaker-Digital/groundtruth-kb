NEW

# Defect-Fix Proposal — Slice 3: write-time author metadata enforcement parity

bridge_kind: prime_proposal
Document: gtkb-wi4940-bridge-metadata-write-time-enforcement
Version: 001
Author: Prime Builder Cursor
Date: 2026-06-30T22:25:00Z

author_identity: Prime Builder Cursor
author_harness_id: E
author_session_context_id: cursor-pb-s522-metadata-compliance-wi4940
author_model: Composer
author_model_version: 2.5
author_model_configuration: Cursor interactive; session role Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-METADATA-COMPLIANCE-BRIDGE-AUTHOR-METADATA-COMPLIANCE-REMEDIATION-FORWARD-PREVENTION
Project: PROJECT-GTKB-BRIDGE-METADATA-COMPLIANCE
Work Item: WI-4940

target_paths: ["groundtruth-kb/templates/hooks/bridge-compliance-gate.py", ".claude/hooks/bridge-compliance-gate.py", "scripts/gtkb_bridge_writer.py", ".claude/skills/verify/helpers/write_verdict.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Claim

Write-time gates check metadata **presence** but accept synthetic session ids, so corrupt
verdicts reach disk and block impl-start later. WI-4940 adds synthetic-session rejection
to `bridge-compliance-gate.py`, `gtkb_bridge_writer.py`, and `write_verdict.py` finalization
with harness-parity byte-sync for template/activated hook copies.

## Defect / Reproduction

- `bridge-compliance-gate.py` `_deny_reason_for_content` blocks missing fields but accepts `openrouter-harness-f`.
- Model-written complete metadata bypasses `ensure_author_metadata()` override (WI-4939).
- `write_verdict.py` bypasses PreToolUse hook; self-review check passes when ids differ synthetically but impl-start fails on missing ids.

## In-Root Placement Evidence

All targets in-root under GT-KB platform tree.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20266647`, `DELIB-20266105`
- `bridge/gtkb-wi4829-self-review-write-time-gate-005.md`
- `bridge/gtkb-antigravity-lo-hallucination-prevention-005.md`

## Owner Decisions / Input

Authorized by project PAUTH (DELIB-20266647). No new owner decision.

## Requirement Sufficiency

Existing requirements sufficient.

## Proposed Scope

1. Shared `synthetic_session_context_id()` in `scripts/bridge_author_metadata.py` (from WI-4939).
2. Hard-block synthetic session ids in bridge-compliance-gate for status-bearing writes.
3. Same check in `write_verdict.py` before finalization.
4. Extend `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`.
5. Byte-sync template → `.claude/hooks/bridge-compliance-gate.py`.

Out of scope: historical bridge backfill (WI-4941).

## Cross-Harness Disposition

- **Claude (B):** `.claude/hooks/bridge-compliance-gate.py` and `.claude/skills/verify/helpers/write_verdict.py` are in scope; template byte-sync required. Behavioral parity with write-time synthetic-id denial.
- **Codex (A):** `.codex/skills/verify/helpers/write_verdict.py` adapter must mirror Claude helper changes per harness-parity MANIFEST; compliance gate invoked via `.codex/gtkb-hooks/` cmd wrappers — no separate Python copy; parity via shared `scripts/bridge_author_metadata.py` helper.
- **Cursor (E):** `.cursor/skills/verify/helpers/write_verdict.py` adapter sync from canonical `.claude/skills/verify/helpers/write_verdict.py` per MANIFEST.
- **Antigravity (C):** hook-less path documented residual; write-time gate applies when using guarded writer or Claude Write path only. No typed waiver for hook surfaces in scope.
- **Ollama (D) / OpenRouter (F):** benefit from WI-4939 harness fixes; this slice adds gate parity on shared writer/hook paths. No harness-specific waiver.

## Specification-Derived Verification Plan

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py -q --no-header
```

## Risks / Rollback

Hook change risk — additive deny path only for synthetic ids. Revert single commit.

## Recommended Commit Type

fix — WI-4940 write-time metadata enforcement.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
