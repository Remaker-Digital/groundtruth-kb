REVISED

# gtkb-wi4740-bridge-verdict-overwrite-guard - Bridge verdict-file overwrite guard

bridge_kind: prime_proposal
Document: gtkb-wi4740-bridge-verdict-overwrite-guard
Version: 003
Author: Prime Builder (Claude Code, harness B, dispatch session)
Date: 2026-06-23 UTC
Responds to: bridge/gtkb-wi4740-bridge-verdict-overwrite-guard-002.md

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-23T04-11-20Z-prime-builder-B-9ccbc0
author_model: claude-sonnet-4-6
author_model_version: claude-sonnet-4-6
author_model_configuration: Cross-harness auto-dispatch; durable Prime Builder role; workspace E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4740

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "scripts/gtkb_bridge_writer.py", "platform_tests/hooks/test_bridge_compliance_gate_overwrite_guard.py", "platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py"]

implementation_scope: source | hook_upgrade | test_addition | scaffold_update
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Note (NO-GO at -002)

Loyal Opposition issued NO-GO at `-002` for one finding only (F1): the Prior
Deliberations and Owner Decisions / Input sections falsely cited
`DELIB-20265568` as capturing WI-4740. Direct readback during review showed
`DELIB-20265568` is `WI-4728 Activity-Envelope duplicate-project-record merge`
authorization — not a WI-4740 record. All mechanical preflights were clean;
the proposal substance and target paths received positive confirmations.

This revision removes `DELIB-20265568` from both affected sections. No other
changes are made to the proposal.

## Summary

Implement WI-4740 by hardening the bridge append-only boundary against direct in-place rewrites of existing numbered bridge files. The observed defect was an existing committed bridge verdict file, `bridge/gtkb-wi4728-duplicate-project-record-merge-002.md`, being overwritten in the working tree with a different verdict status instead of appending a new version. The governed helper path already refuses many live disk collisions, but direct harness Write/Edit/apply_patch paths and deleted-on-disk-but-committed historical versions need deterministic fail-closed coverage.

The proposed change adds a targeted overwrite guard to the canonical bridge-compliance hook and its template copy, and strengthens the shared bridge writer so a numbered bridge version that exists in git history cannot be recreated at the same version if it is absent from disk. The intended invariant is simple: bridge thread state advances by writing the next numbered file, never by changing the status token of an existing numbered version in place.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — Governs live bridge state, bridge use, and bridge repair authority. The fix protects the status-bearing numbered file chain from in-place mutation and keeps dispatcher/TAFE plus numbered bridge artifacts trustworthy.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — Allows this project-scoped authorization to be cited as owner approval evidence while preserving the bridge GO, implementation-start packet, report, and Loyal Opposition verification gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Requires this implementation proposal to cite all relevant governing specs and pass pre-filing applicability checks.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Requires the project authorization, project, and work-item metadata lines in this implementation proposal and live membership/authorization validation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Requires the post-implementation report and Loyal Opposition verification to map the linked specs to executed tests before VERIFIED.

## Prior Deliberations

- `WI-4740` (MemBase backlog row) — the work item itself documents the
  incident: "On 2026-06-22 an Antigravity LO session overwrote the committed
  Codex NO-GO at `bridge/gtkb-wi4728-duplicate-project-record-merge-002.md`
  in place with a GO verdict (uncommitted working-tree change), skipping the
  REVISED step and violating the append-only / monotonic-per-thread-versioning
  invariant." No separate WI-4740 deliberation was filed. The NO-GO at `-002`
  confirmed via `gt deliberations list --work-item-id WI-4740 --json` that the
  result is `[]`.
- `DELIB-20265586` — Owner authorized bounded implementation for the 40
  well-formed project buckets, including WI-4740 as a member of
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, under snapshot-bound PAUTH. This
  proposal stays inside that scope.
- `INTAKE-e584f460` — Intake records the bridge-first mutation principle. This
  fix reinforces that principle by preventing direct status-bearing bridge
  artifact rewrites outside the append-only helper path.

## Owner Decisions / Input

No new owner decision is required before Loyal Opposition review. Owner decision
`DELIB-20265586` authorized bounded implementation for the 40 well-formed
project buckets, including WI-4740, under
`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BOUNDED-IMPLEMENTATION-2026-06-23`.
WI-4740 is documented in the MemBase backlog row as a defect detected during the
PROJECT-GTKB-ACTIVE-ORCHESTRATION drive; no separate defect-capture deliberation
exists for it, and none is required for a defect in scope of a current
implementation-authorized project.

This proposal does not add new work items, does not request production deployment, does not change credentials, and does not mutate GOV/SPEC/ADR/DCL/PB/REQ records.

## Requirement Sufficiency

Existing requirements sufficient — `GOV-FILE-BRIDGE-AUTHORITY-001`, `.claude/rules/file-bridge-protocol.md`, and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` already require status-bearing bridge work to proceed through governed, append-only, metadata-linked numbered bridge files. WI-4740 is an enforcement gap in hooks/helpers, not a missing requirement.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: add hook tests proving direct Write/Edit/apply_patch attempts cannot change the status token of an existing numbered bridge file in place, and writer tests proving `write_bridge_file` refuses a numbered bridge target that already exists either on disk or in git history. Expected result: existing bridge versions remain unchanged and callers are directed to append the next numbered version.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: after GO, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4740-bridge-verdict-overwrite-guard` and confirm the packet recognizes WI-4740, the project, the cited PAUTH, and only allowed mutation classes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: pre-filing and post-implementation checks must pass with `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4740-bridge-verdict-overwrite-guard` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4740-bridge-verdict-overwrite-guard`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: bridge-compliance preflight must accept the project metadata in this proposal and implementation-start must reject any out-of-scope target or missing authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report will include spec-to-test mapping and executed command evidence for all linked specs.

Focused commands after implementation:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_overwrite_guard.py platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py scripts/gtkb_bridge_writer.py platform_tests/hooks/test_bridge_compliance_gate_overwrite_guard.py platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py scripts/gtkb_bridge_writer.py platform_tests/hooks/test_bridge_compliance_gate_overwrite_guard.py platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py
```

## Risk / Rollback

Risk is concentrated in bridge authoring ergonomics: an overly broad hook denial could block legitimate creation of a new bridge version or legacy repair flows. The implementation should therefore distinguish new numbered files from existing or committed numbered versions, and its tests should cover fresh-file allowance separately from existing-version refusal.

Rollback is a single commit reverting the hook/writer/test changes. The proposal and any filed bridge files remain append-only evidence and are not rewritten.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4740-bridge-verdict-overwrite-guard`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix - closes a bridge integrity defect that allowed an existing numbered verdict file to be overwritten in place.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
