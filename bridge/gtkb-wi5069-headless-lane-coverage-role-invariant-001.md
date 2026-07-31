NEW

# gtkb-wi5069-headless-lane-coverage-role-invariant - Replace durable role partition with lane coverage validation

bridge_kind: prime_proposal
Document: gtkb-wi5069-headless-lane-coverage-role-invariant
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-07T23:05:56Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3ddf-359c-7fa3-8885-2d1f9179d884
author_model: GPT-5 Codex
author_model_version: 2026-07-07
author_model_configuration: Codex Desktop interactive session; owner init `::init gtkb pb`; protected implementation remains bridge-gated

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5069

target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py", ".claude/rules/operating-role.md", ".claude/rules/prime-builder-role.md", "platform_tests/groundtruth_kb/test_mode_switch_invariants.py", "platform_tests/groundtruth_kb/test_mode_switch_transaction.py"]

implementation_scope: source, governance, protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The current mode-switch validator requires the active durable registry partition to contain at least one active `prime-builder` and at least one active `loyal-opposition`. That is now too broad: GT-KB already recognizes that an interactive owner-declared Prime Builder session can remain PB while the same harness's dispatcher/default role is assigned to Loyal Opposition for headless dispatch routing.

This proposal replaces the absolute durable PB/LO partition invariant with lane-coverage validation. The new rule should fail closed when neither durable PB coverage nor owner-declared interactive PB coverage exists, but it should allow an owner-authorized LO-only headless surge when an interactive PB session anchors Prime Builder responsibility. The implementation must preserve bridge self-review protection through author/reviewer session-context checks and must not allow a headless worker to review its own proposal merely because durable roles were reassigned.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` - Current active-role partition source; this change revises how its active dispatch partition is validated in the interactive/headless split model.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - Prime Builder and Loyal Opposition are portable harness-assigned roles; the implementation must preserve portability while separating interactive authority from headless routing.
- `GOV-SESSION-ROLE-AUTHORITY-001` - Interactive owner-declared role evidence may govern in-session surfaces without mutating dispatcher/default assignments.
- `DCL-SESSION-ROLE-RESOLUTION-001` - Session role resolution distinguishes transcript-defined interactive role from durable registry fallback.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - Interactive session role persists across contiguous interactive context and can remain PB while registry/default routing changes.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - The implementation must not treat a durable/default role switch as changing this interactive PB session.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Source/config mutation remains bridge-gated; this proposal is the PB NEW artifact for LO review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal carries concrete specification links and target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This proposal carries Project Authorization, Project, and Work Item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification must map the role invariant change to focused tests.
- `GOV-STANDING-BACKLOG-001` - The owner decision was captured as `WI-5069` before implementation.

## Prior Deliberations

- `DELIB-20260707-HEADLESS-LANE-COVERAGE` - Owner agreed the durable active PB/LO partition validator is over-broad for interactive PB plus LO-default headless routing; direct authority for this proposal.
- `DELIB-20264148` - Prior LO review of harness role portability required a full durable role partition for the earlier FR9 model; this proposal intentionally revises that earlier assumption for the newer interactive/headless split.
- `DELIB-1466` - Role and session lifecycle review recommended keeping PB/LO as authority-bearing operating roles while treating other work as session lanes; relevant to separating operating role authority from session lane/coverage.
- `DELIB-20265152` - Prior verification that spawned headless harness prompts defer to the durable role record; this proposal preserves that for headless workers while adding explicit interactive PB anchor handling for topology validation.
- `DELIB-20264030` - Prior GO on whole-candidate mode-switch validation; this change should keep whole-candidate validation, but update the candidate invariant from durable partition symmetry to lane coverage plus session-context protection.

## Owner Decisions / Input

- `DELIB-20260707-HEADLESS-LANE-COVERAGE` captures the owner decision: replace the absolute durable PB/LO partition requirement with lane-coverage validation that permits LO-only headless surge routing when an interactive PB session is owner-declared and remains PB.
- The owner also stated in this session: "If necessary, switch Codex to LO in order to clear the LO queue. This will not change the role of any interactive session." This proposal preserves that instruction without treating it as approval to edit protected source before LO GO.

## Requirement Sufficiency

Existing requirements sufficient - the governing requirements already distinguish interactive session role from dispatcher/default role metadata and require bridge self-review protection. The implementation should update the validator and rule text to align those existing requirements with the current headless-dispatch capacity goal; no new specification is required before implementation.

## Cross-Harness Disposition

This proposal touches harness role and headless-dispatch behavior. Cross-harness effects are intended and bounded:

- Codex/A may remain an interactive Prime Builder session while its durable/default headless role is reassigned to Loyal Opposition for LO queue drain, when owner-authorized.
- OpenRouter/F and Ollama/D remain LO dispatch candidates; this change must not reduce their LO eligibility or suppress their queues.
- Antigravity/C has no available budget and must not be assumed as live LO capacity.
- Claude/B and Cursor/E remain unavailable/suspended for current capacity planning.
- The implementation must keep same-session/self-review denial intact by session context and bridge metadata, not by assuming a durable PB holder exists.

## Spec-Derived Verification Plan

| Linked specification | Verification command | Expected result |
|---|---|---|
| `REQ-HARNESS-REGISTRY-001`, `GOV-HARNESS-ROLE-PORTABILITY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_mode_switch_invariants.py -q --no-header` | Tests show invalid no-coverage maps still fail closed, while owner-declared interactive PB coverage permits a durable LO-only active headless partition. |
| `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`, `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/hooks/test_session_role_resolution.py -q --no-header` | Transaction tests prove the durable role switch does not mutate interactive role markers and session-role resolver tests still pass. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5069-headless-lane-coverage-role-invariant` and `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5069-headless-lane-coverage-role-invariant` | Applicability reports `preflight_passed: true` with `missing_required_specs: []`; clause preflight reports zero blocking gaps. |
| Dispatch capacity goal | `groundtruth-kb/.venv/Scripts/python.exe -c "from pathlib import Path; from scripts.gtkb_dispatcher_daemon import run_tick; import json; print(json.dumps(run_tick(Path(r'E:/GT-KB'), max_items=20, dry_run=True)['decisions'], default=str))"` | Dry-run selection can route LO-actionable work to LO-default Codex/OpenRouter/Ollama according to eligibility without requiring a durable PB holder when an interactive PB anchor exists. |

## Risk / Rollback

The main risk is weakening the old safety invariant too far and allowing no real Prime Builder coverage. The implementation must avoid that by requiring explicit interactive PB anchor evidence, or another concrete PB coverage source, whenever no active durable PB remains.

Rollback is a single-commit revert of the validator/rule/test changes. Durable registry state changes made after the implementation should remain governed by `gt mode set-role`; if needed, they can be reversed through the same transaction CLI after rollback.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi5069-headless-lane-coverage-role-invariant`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

All implementation outputs and generated evidence for this work remain in-root under `E:/GT-KB`; the bridge file itself is filed under `E:/GT-KB/bridge/`, and no live GT-KB artifact outside the project root is an input or output.

## Recommended Commit Type

fix - the change corrects an over-broad validator that blocks owner-authorized headless LO dispatch under the current interactive/headless role model.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
