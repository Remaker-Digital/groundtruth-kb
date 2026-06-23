NEW

# WI-4683: Reconcile Activity Vocabulary to the Six-Member Set (Re-admit `ops`)

bridge_kind: prime_proposal
Document: gtkb-wi4683-activity-vocabulary-reconcile-ops
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-22 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: d209f895-a107-4379-be37-d4ecf5e8ea00
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, autonomous /loop dynamic mode, Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4683

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/topic_router.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_wrapup_trigger_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Reconcile the activity/topic vocabulary drift (DELIB-20265287 D10: "activity-vocabulary drift is a defect → reconcile to one canonical closed set") by **re-admitting `ops`** to the runtime vocabulary. The canonical closed set is the six-member `{ops, deliberation, build, test, spec, project}` (owner-decided DELIB-20260621 DEC-4; formalized in the now-canonical `DCL-ACTIVITY-DISPOSITION-PROFILE-001` A1; already enumerated by the Slice-1 `config/agent-control/activity-disposition-profiles.toml`). The session runtime is the divergent surface: `groundtruth_kb/session/topic_router.py` (`TOPIC_COMMAND_RE`) and `groundtruth_kb/session/envelope.py` (`TOPIC_TYPES`, `ROUTE_TARGETS`, `PRELOAD_STATES`) still carry the old five-member set `{spec, build, test, deliberation, project}`, missing `ops`.

This slice adds `ops` to those enumerations so the runtime vocabulary matches the DCL + disposition config, and updates the two tests that assert the vocabulary.

**Scope boundary.** This is vocabulary reconciliation only — it adds the `ops` *slot* with a route-target + preload-state stub consistent with DELIB-20265287 F1 (`::open ops` acquires deployed-app status, applies decision criteria, emits prioritized AUQ options). The full `ops` activity handler (status acquisition + decision criteria + AUQ emission) is **WI-4687** and is out of scope here. The glossary (`.claude/rules/canonical-terminology.md`) does **not** enumerate the closed set (verified: no enumeration present; the closed set lives in the DCL), so no narrative-artifact edit is in scope.

## Specification Links

- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` — A1 fixes the canonical six-member activity set this reconciliation targets.
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` — the disposition decision over the same closed-but-extensible vocabulary.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all governing specs cited.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project/WI/PAUTH linkage present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derives tests from the linked vocabulary spec.
- `GOV-STANDING-BACKLOG-001` — WI-4683 is the governing backlog item.

## Prior Deliberations

- `DELIB-20265287` — D10 ("activity-vocabulary drift is a defect → reconcile to one canonical closed set"; explicitly names the diverging lists incl. code `{spec,build,test,deliberation,project}`) and F1 (`ops` re-admitted as an activity type; reverses WI-4295's drop of `{ops, push, upgrade}`; defines `ops` semantics).
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` — DEC-4 locks the six-member vocabulary `{ops, deliberation, build, test, spec, project}` and states it resolves the WI-4683 / D10 drift to this closed set.
- `DELIB-20260612-EXPLICIT-HINT-LAYER-DECISION-SET` — closed-but-extensible vocabulary basis.
- Bridge `gtkb-activity-disposition-profile-adr-dcl` GO@-002 — landed the DCL whose A1 is the reconciliation target.

## Owner Decisions / Input

PAUTH-covered implementation of an already-owner-decided vocabulary; no new owner approval required. The six-member set is owner-decided (DELIB-20260621 DEC-4) and formalized (DCL-ACTIVITY-DISPOSITION-PROFILE-001). Implementation authority is the active envelope PAUTH (covers WI-4683; `allowed_mutation_classes` include `source`, `test`). No glossary/narrative edit is in scope (the glossary does not enumerate the set), so no narrative-artifact-approval packet is required.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-ACTIVITY-DISPOSITION-PROFILE-001` A1 + `DELIB-20265287` D10/F1 + `DELIB-20260621` DEC-4 define the canonical six-member set and `ops` semantics. No new or revised requirement is needed.

## Design

**1. `groundtruth_kb/session/topic_router.py`** — extend `TOPIC_COMMAND_RE` (currently `^::(?P<action>open|close) (?P<topic>spec|build|test|deliberation|project)$`) to include `ops` in the topic alternation.

**2. `groundtruth_kb/session/envelope.py`** —
- `TOPIC_TYPES` (line 20): add `"ops"` → six-member tuple matching the DCL.
- `ROUTE_TARGETS` (line 23): add an `ops` route target consistent with the existing per-topic service-routing pattern and DELIB-20265287 F1 (an operations/ops route target; exact value matched to the existing naming convention at implementation time).
- `PRELOAD_STATES` (line 31): add an `ops` preload-state stub per F1 (deployed-app status + operational issues acquisition recipe). The `open_topic`/`close_topic` validators (lines 311, 339, `topic_type not in TOPIC_TYPES`) then accept `ops` with no further change.

The `ops` route/preload values are a reconciliation **stub** (vocabulary slot); WI-4687 implements the substantive `ops` handler.

**3. Tests** — `platform_tests/scripts/test_session_envelope_runtime.py` and `platform_tests/scripts/test_session_wrapup_trigger_dispatch.py`: update any five-member assertions to the six-member set and add coverage that `::open ops` / `::close ops` are accepted, routed, and preloaded, and that the existing five types are unaffected.

## Spec-Derived Verification Plan

| Linked spec clause | Test | Expected |
|---|---|---|
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` A1 (six-member set) | new assertion: `TOPIC_TYPES` equals the six-member set `{ops, deliberation, build, test, spec, project}` | PASS |
| DELIB-20265287 F1 (`ops` admitted) | `::open ops` accepted + routed + preloaded (envelope `open_topic`) | PASS |
| No regression of the existing five | existing `::open {spec,build,test,deliberation,project}` tests | PASS |
| Wrap-up dispatch over six types | `test_session_wrapup_trigger_dispatch.py` updated assertions | PASS |

Commands (run on changed Python before the implementation report):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/session/topic_router.py groundtruth-kb/src/groundtruth_kb/session/envelope.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/topic_router.py groundtruth-kb/src/groundtruth_kb/session/envelope.py
```

## Risk / Rollback

Moderate-low. `TOPIC_TYPES` is consumed across the session runtime; adding a sixth member is additive (existing five-type code paths are unaffected), but any code or test with a hard five-element assumption must be updated — the two identified test files bound that surface, and the verification run will surface any missed consumer. Rollback is a single-commit `git restore` of the four target paths. Opening `::open ops` yields an envelope with a stub route/preload until WI-4687 lands its handler; this is expected incremental behavior, not a defect.

## Recommended Commit Type

`fix` — reconciles a vocabulary-drift defect (DELIB-20265287 D10 classifies the drift as a defect); additive `ops` slot with no new standalone capability surface (the `ops` handler is WI-4687).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
