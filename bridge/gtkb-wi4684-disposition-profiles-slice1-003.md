REVISED

# WI-4684 Slice 1: Activity-Disposition Profile Schema, Data & Loader (REVISED)

bridge_kind: prime_proposal
Document: gtkb-wi4684-disposition-profiles-slice1
Version: 003
Responds-To: bridge/gtkb-wi4684-disposition-profiles-slice1-002.md (NO-GO)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-22 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-22T04-35-15Z-prime-builder-B-562ffc
author_model: Claude Sonnet 4.6
author_model_version: claude-sonnet-4-6
author_model_configuration: Claude Code CLI, auto-dispatched Prime Builder, session 2026-06-22T04-35-15Z

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4684

target_paths: ["config/agent-control/activity-disposition-profiles.toml", "groundtruth-kb/src/groundtruth_kb/activity/__init__.py", "groundtruth-kb/src/groundtruth_kb/activity/profiles.py", "platform_tests/scripts/test_activity_disposition_profiles.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Summary

REVISED to address NO-GO@-002. The sole blocking finding was that three advisory governance specs were missing from the `Specification Links` section. No design, scope, or implementation change is required. This revision adds those three citations with applicability justification.

## Summary

This is Slice 1 of WI-4684 (the activity-disposition runtime), implementing the **data + loader foundation** for the disposition-profile model formalized in `DCL-ACTIVITY-DISPOSITION-PROFILE-001` (inserted to MemBase 2026-06-22 under owner formal-artifact approval; bridge `gtkb-activity-disposition-profile-adr-dcl` GO@-002).

Slice 1 delivers three artifacts: (1) a TOML config holding one disposition-profile record for each of the six canonical activities `{ops, deliberation, build, test, spec, project}`, each carrying the four payload classes (`skills`, `terminology`, `history_state`, `direction`) plus a `headless_eligibility` attribute; (2) a loader/validator module exposing a canonical reader entrypoint that loads and fail-closed-validates the config against the DCL schema; (3) a pytest suite mapping directly to DCL assertions A1–A3.

**Scope boundary.** Slice 1 is the standalone data + loader foundation only. It deliberately does NOT wire the `::open <activity>` interception hook (Slice 2 / DCL A4) or the non-blocking soft-reminder gate (Slice 3 / DCL A5); nothing consumes the profiles yet. It establishes structurally-complete profile records (sufficient to satisfy A1–A3) with reasonable first-pass class content; **substantive per-activity content refinement is deferred to WI-4730** (owner-driven AUQ, do-not-headless-drive). The existing `topic_router.py` 5-member vocabulary (`{spec, build, test, deliberation, project}`, missing `ops`) is reconciled to the six-member set under WI-4683 and is out of scope here — this config defines all six profiles independently of whether `topic_router` routes `ops` yet.

## Specification Links

- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` — the normative schema this slice implements. Assertions A1 (each of the six activities has a profile record), A2 (each profile defines all four classes), and A3 (each profile carries a `headless_eligibility` consistent with DELIB-20265287 D4) are this slice's acceptance criteria. A4/A5 (interception surface, soft-reminder gate) are out of Slice-1 scope.
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` — the architecture decision this realizes (per-activity context-load profile at the intent_hint leg).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal is filed as a status-bearing numbered bridge file.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project/Work-Item/PAUTH linkage metadata present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives tests from the linked DCL assertions.
- `GOV-STANDING-BACKLOG-001` — WI-4684 is the governing backlog item (envelope project, active PAUTH).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — (advisory) The `activity-disposition-profiles.toml` is itself a new durable governed artifact entering the GT-KB platform's artifact graph. The design decision to store profiles in a schema-versioned, git-tracked TOML rather than hard-coded defaults follows this governance principle; future content revisions to the config are governed lifecycle events (owner-driven WI-4730), not ad-hoc edits.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — (advisory) This ADR established the decision to model project memory as a durable artifact graph. The disposition-profile config and loader are new nodes in that graph: the TOML carries `schema_version` and per-profile `version` fields, the loader provides the canonical reader entrypoint, and artifact-lifecycle discipline (versioned change, owner-reserved content refinement) is built into the design from Slice 1.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — (advisory) The `headless_eligibility` attribute on each profile is an artifact lifecycle trigger signal: it determines whether a session context proceeds headlessly or requires interactive engagement, which is precisely the kind of lifecycle-threshold decision this DCL governs. Slice 1 encodes the D4-specified eligibility values; Slices 2–3 will wire the interception and soft-reminder gate that actuate those triggers.

## Prior Deliberations

- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` — owner decision set DEC-1..5: the 4-class context-load profile (DEC-2), injection + non-blocking soft-reminder enforcement (DEC-3), and the six-member vocabulary (DEC-4) this slice's data encodes.
- `DELIB-20265287` — D2 (named, versioned disposition profile per activity), D4 (per-activity headless-eligibility: deliberation+project interactive-only, spec+build+test headless-eligible, ops interactive-primary — the exact `headless_eligibility` values this slice encodes), F2 (the profile enriches the intent_hint leg).
- `DELIB-20260612-EXPLICIT-HINT-LAYER-DECISION-SET` — closed-but-extensible vocabulary basis.
- Bridge `gtkb-activity-disposition-profile-adr-dcl` GO@-002 (terminal) — the ADR/DCL pair this slice implements; both landed in MemBase 2026-06-22.

The seeded scaffold candidates (proposal-standards, skill-modernization, opportunity-radar, impl-auth-verification, Phase-B disposition) are not relevant to the disposition-profile data model and were pruned.

## Owner Decisions / Input

This slice is PAUTH-covered implementation of an already-owner-approved schema; it does **not** depend on a new owner approval. The governing owner decisions are `DELIB-20260621` (DEC-1..5) and `DELIB-20265287` (D2/D4/F2), realized as the now-canonical `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` + `DCL-ACTIVITY-DISPOSITION-PROFILE-001` (owner formal-artifact approval captured via AskUserQuestion 2026-06-22). Implementation authority is the active envelope PAUTH (covers WI-4684; `allowed_mutation_classes` include `source`, `test`, `config`).

The one owner-reserved follow-on — the substantive per-activity profile **content** — is intentionally deferred to **WI-4730** (owner-driven AUQ). Slice 1 seeds structurally-valid first-pass content only; no owner decision is required to land the schema/loader/tests.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-ACTIVITY-DISPOSITION-PROFILE-001` (assertions A1–A3) defines the acceptance criteria for the data + loader; `DELIB-20265287` D4 fixes the `headless_eligibility` values. No new or revised requirement is needed before implementation.

## Design

**1. `config/agent-control/activity-disposition-profiles.toml`** (config home per existing `config/agent-control/` convention — sibling to `harness-capability-registry.toml`, `system-interface-map.toml`):

```toml
schema_version = 1

[activities.ops]
version = 1
headless_eligibility = "interactive_primary"   # DELIB-20265287 D4
skills = [...]            # first-pass; refined by WI-4730
terminology = [...]
[activities.ops.history_state]
sources = [...]          # acquisition recipe
[activities.ops.direction]
stance = "..."
guardrails = [...]
manipulates = [...]
# ... repeated for deliberation, build, test, spec, project
```

`headless_eligibility` ∈ `{headless_eligible, interactive_only, interactive_primary}`. D4 mapping: `spec/build/test = headless_eligible`; `deliberation/project = interactive_only`; `ops = interactive_primary`.

**2. `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`** (+ `activity/__init__.py` for the new package). A pure-Python loader exposing the canonical reader entrypoint:
- `load_activity_profiles(path: Path | None = None) -> dict[str, ActivityProfile]` — default path resolves to `config/agent-control/activity-disposition-profiles.toml` via the project-root config resolver; reads with `tomllib`.
- An `ActivityProfile` dataclass (frozen) carrying `name`, `version`, `headless_eligibility`, and the four class fields.
- Fail-closed validation: raises a typed `ActivityProfileError` when any of the six activities is missing (A1), when any profile omits one of the four classes (A2), or when `headless_eligibility` is invalid or D4-inconsistent (A3). No filesystem mutation; read-only.

**3. `platform_tests/scripts/test_activity_disposition_profiles.py`** — see verification plan.

DCL assertion-object grep/glob wiring (the machine-checkable form recorded on the DCL row) is deferred to the slice that lands the consuming runtime, when concrete artifact paths exist; Slice 1's pytest suite is the spec-derived test surface for A1–A3 in the interim (the DCL remains `status=specified` until A4/A5 land in Slices 2–3).

## Spec-Derived Verification Plan

| Linked spec clause | Test | Expected |
|---|---|---|
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` A1 (six activity profiles) | `test_all_six_activities_present` | PASS |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` A2 (four classes each) | `test_each_profile_defines_four_classes` | PASS |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` A3 (`headless_eligibility` D4-consistent) | `test_headless_eligibility_valid_and_d4_consistent` | PASS |
| Loader fail-closed (A1/A2/A3 enforcement) | `test_loader_rejects_missing_activity`, `test_loader_rejects_missing_class`, `test_loader_rejects_invalid_eligibility` | PASS (raises `ActivityProfileError`) |
| Default-path resolution | `test_default_path_loads_shipped_config` | PASS |

Commands (run on the changed Python before filing the implementation report):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_activity_disposition_profiles.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/activity/profiles.py platform_tests/scripts/test_activity_disposition_profiles.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/activity/profiles.py platform_tests/scripts/test_activity_disposition_profiles.py
```

## Risk / Rollback

Low blast radius: all four target paths are net-new files; no existing surface is modified and nothing consumes the profiles yet (Slice 2 wires consumption). Rollback is a single-commit `git restore` plus deletion of the new `activity/` package, config, and test. The loader is read-only (no filesystem or MemBase mutation). Forward risk is limited to first-pass profile content being refined later by WI-4730 — which is expected and owner-reserved, not a defect.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4684-disposition-profiles-slice1`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat` — net-new capability surface (new `activity` package + config + test suite); no existing behavior is modified.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
