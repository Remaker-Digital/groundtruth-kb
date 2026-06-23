REVISED

# WI-4683 (REVISED -003): Reconcile Activity Vocabulary to Six Members (Re-admit `ops`) — Code + Formal Router Specs

bridge_kind: prime_proposal
Document: gtkb-wi4683-activity-vocabulary-reconcile-ops
Version: 003
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
kb_mutation_in_scope: true

---

## Revision Note (-003, addressing NO-GO@-002)

Codex NO-GO@-002 correctly found that -001 changed the runtime `::open`/`::close` vocabulary (5→6) without reconciling two still-live formal specs that define the closed five-member set: `SPEC-TOPIC-ENVELOPE-ROUTER-001` (`specified`) and `DCL-TOPIC-ENVELOPE-ROUTING-001` (`specified`). The latter mandates owner-AUQ + formal-artifact approval to add a type. -001 would have created spec/code drift at exactly the surface WI-4683 reconciles. This revision brings the formal router specs into scope (F1), handles the "per-type specs" component (F2), and notes the preflight gap (F3) is already tracked.

## Summary

Reconcile the activity/topic vocabulary drift (DELIB-20265287 D10: drift is a defect → one canonical closed set) by re-admitting `ops`, across BOTH the runtime code AND the formal router specs, to the owner-decided six-member set `{ops, deliberation, build, test, spec, project}`.

Two coordinated changes in one bridge scope:
1. **Code** (autonomous, envelope PAUTH `source`): add `ops` to `topic_router.py` `TOPIC_COMMAND_RE` and `envelope.py` `TOPIC_TYPES`/`ROUTE_TARGETS`/`PRELOAD_STATES` (5→6); `ops` route/preload is a STUB per DELIB-20265287 F1 (full `ops` handler is WI-4687).
2. **Formal router specs** (owner-gated, formal-artifact path): amend `SPEC-TOPIC-ENVELOPE-ROUTER-001` (v2) and `DCL-TOPIC-ENVELOPE-ROUTING-001` (v2) from the closed five-member vocabulary to the six-member set, adding `ops` to the command regexes and the activity-to-service routing map. These are MemBase mutations via `gt spec record`, each gated by a formal-artifact-approval packet presented to and ratified by the owner at implementation (same pattern as the ADR/DCL inserts on 2026-06-22). The owner decision basis is DEC-4 (DELIB-20260621 resolves WI-4683/D10 drift to the six-member set, superseding DELIB-20260638's five-member decision that the current router specs cite); per `DCL-TOPIC-ENVELOPE-ROUTING-001`'s own process this is the required owner-AUQ + formal amendment.

## Specification Links

- `SPEC-TOPIC-ENVELOPE-ROUTER-001` — **live five-member command-surface spec being amended to six (v2)**.
- `DCL-TOPIC-ENVELOPE-ROUTING-001` — **live five-member routing-map DCL being amended to six (v2); mandates owner-AUQ + formal approval to add a type**.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` — A1 fixes the canonical six-member set (target of reconciliation).
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` — disposition decision over the same vocabulary.
- `GOV-ARTIFACT-APPROVAL-001` — governs the two formal router-spec amendments.
- `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-STANDING-BACKLOG-001`.

## Prior Deliberations

- `DELIB-20265287` — D10 (vocabulary drift is a defect; names the diverging code list); F1 (re-admit `ops`; defines `ops` semantics).
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` — DEC-4 locks the six-member set and resolves WI-4683/D10 drift to it (the owner decision basis for the formal amendments).
- `DELIB-20260638` — the prior decision that fixed the router specs at five members; superseded for the vocabulary count by DEC-4.
- Bridge `gtkb-activity-disposition-profile-adr-dcl` GO@-002 — landed `DCL-ACTIVITY-DISPOSITION-PROFILE-001` (six-member A1).

## Owner Decisions / Input

The six-member vocabulary (incl. `ops`) is owner-decided: `DELIB-20260621` DEC-4 (AUQ-backed) explicitly resolves WI-4683 to the six-member set, superseding DELIB-20260638's five-member count. That satisfies `DCL-TOPIC-ENVELOPE-ROUTING-001`'s owner-AUQ-to-add-a-type basis. The remaining owner gate is **formal-artifact ratification of the two specific spec amendments** (`SPEC-TOPIC-ENVELOPE-ROUTER-001` v2 + `DCL-TOPIC-ENVELOPE-ROUTING-001` v2): on this proposal's GO, Prime presents each amended spec's full content to the owner via AskUserQuestion and mints a formal-artifact-approval packet before `gt spec record`, per GOV-ARTIFACT-APPROVAL-001 (same flow used for the ADR/DCL inserts this session). No new owner *requirement* is introduced.

## Requirement Sufficiency

New or revised requirement required before implementation — specifically, formal-artifact AMENDMENT (not new requirement) of `SPEC-TOPIC-ENVELOPE-ROUTER-001` and `DCL-TOPIC-ENVELOPE-ROUTING-001` to the six-member set. The substantive requirement (six-member vocabulary) already exists (DEC-4 + DCL-ACTIVITY-DISPOSITION-PROFILE-001 A1); the amendments bring the live router specs into agreement with it. Owner ratification of each amendment is via formal-artifact-approval packet at implementation.

## Design

**Code (autonomous):**
- `topic_router.py`: `TOPIC_COMMAND_RE` → add `ops` to the type alternation.
- `envelope.py`: `TOPIC_TYPES` (line 20) → six-member tuple; `ROUTE_TARGETS` (23) → add `ops` route target; `PRELOAD_STATES` (31) → add `ops` preload stub (deployed-app status + operational issues, per F1). Validators (311/339) then accept `ops`.

**Formal router specs (owner-ratified at impl):**
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` v2: change the closed vocabulary from `{spec, build, test, deliberation, project}` to `{ops, deliberation, build, test, spec, project}`; update both strict regexes (`^::open (...)$`, `^::close (...)$`) to include `ops`; cite DEC-4 as superseding DELIB-20260638's five-member count.
- `DCL-TOPIC-ENVELOPE-ROUTING-001` v2: add `ops` to the activity-to-service routing map (route target + preload recipe per F1); record the amendment provenance (DEC-4; this bridge thread).

The `ops` route/preload is a reconciliation STUB; the substantive `ops` handler is WI-4687.

## Spec-Derived Verification Plan

| Linked spec clause | Test / check | Expected |
|---|---|---|
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` A1 / `SPEC-TOPIC-ENVELOPE-ROUTER-001` v2 | `TOPIC_TYPES` equals six-member set; `TOPIC_COMMAND_RE` accepts `ops` | PASS |
| DELIB-20265287 F1 (`ops` admitted) | `::open ops` / `::close ops` accepted + routed + preloaded | PASS |
| No regression of existing five | existing `::open/::close {spec,build,test,deliberation,project}` tests | PASS |
| Cross-surface agreement (F1 required revision #4) | live `SPEC-TOPIC-ENVELOPE-ROUTER-001` v2 + `DCL-TOPIC-ENVELOPE-ROUTING-001` v2 + runtime `TOPIC_TYPES` + `config/agent-control/activity-disposition-profiles.toml` + tests all enumerate the same six-member set | PASS (cross-checked at VERIFIED) |

Commands (changed Python, before report):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/session/topic_router.py groundtruth-kb/src/groundtruth_kb/session/envelope.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/topic_router.py groundtruth-kb/src/groundtruth_kb/session/envelope.py
```

VERIFIED review must confirm both router specs are at v2 with the six-member set (live MemBase), matching code/config/tests.

## Findings Addressed

- **F1 (P1):** router SPEC + DCL added to Specification Links and brought into scope as formal amendments (v2) via the GOV-ARTIFACT-APPROVAL-001 path; `kb_mutation_in_scope: true`; verification proves cross-surface agreement.
- **F2 (P2):** the "per-type specs" component is the router SPEC/DCL amendment above (handled). Glossary exclusion carried forward with evidence: a targeted search of `.claude/rules/canonical-terminology.md` finds no enumeration of the activity closed set (the set lives in the DCL), so no glossary narrative edit is in scope.
- **F3 (P2):** the preflight gap (preflights did not surface the live router DCL) is already tracked by `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001`; no duplicate hygiene item created; this verdict stands as fresh evidence for it.

## Risk / Rollback

Moderate. The formal-spec amendments are append-only new versions (v2) gated by owner-ratified packets; code is additive (sixth member). Rollback: `git restore` the four code/test paths; the spec v2 rows remain as append-only history (a v3 could re-state five members if ever needed, but DEC-4 makes that unlikely). Opening `::open ops` yields a stub route/preload until WI-4687 lands the handler — expected incremental behavior.

## Recommended Commit Type

`fix` — reconciles a vocabulary-drift defect (DELIB-20265287 D10) across code; the coupled formal-spec amendments are governance evidence recorded via `gt spec record` (separate from the code commit).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
