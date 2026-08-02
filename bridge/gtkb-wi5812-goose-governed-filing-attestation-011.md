REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Prime Builder correction held by exact draft claim row 36034 after physical v010 NO-GO; governed physical writer; dispatcher/TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context

bridge_kind: prime_proposal
Document: gtkb-wi5812-goose-governed-filing-attestation
Version: 011
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5812-goose-governed-filing-attestation-010.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5812

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "scripts/bridge_author_metadata.py", "scripts/gtkb_session_id.py", "scripts/goose_harness.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_bridge_author_metadata.py", "platform_tests/scripts/test_gtkb_session_id.py", "platform_tests/scripts/test_goose_governed_filing.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation occurs in this proposal.

# WI-5812 REVISED Implementation Proposal — Role-Authoritative Goose Governed Filing

## Revision Disposition

Version 010 identifies a valid role-authority defect. Version 009 removed the independent timestamp/session-id race, but its generic wrapper design still made `prime-builder` a launcher default even for the `bridge-review` and `verification` routes. This revision removes every wrapper-default role. A Goose child may start only after the wrapper has either consumed a complete dispatcher-composed Goose session envelope or established/consumed an explicit owner-directed interactive Goose session envelope. Activity selection is checked against that already-resolved role and can never create, substitute, or upgrade it.

The original eight-target forward-only scope remains exact. Historical/unreceipted-chain recovery, capability-row repair, receipt back-fill, republish, compensation, and pending-context recovery remain exclusively delegated to WI-5825. No WI-5825 target or behavior is absorbed.

## Response To Version 010

### F1 — Generic wrapper self-issued Prime Builder provenance for Loyal Opposition modes

**Accepted and corrected in the design.** `scripts/goose_harness.py` must not pass a hard-coded role or a launcher-invented role source. Role bootstrap precedes activity prompt construction and has two lawful paths:

1. **Headless dispatcher path.** When `GTKB_BRIDGE_POLLER_RUN_ID` is present, the wrapper loads the exact pre-created Goose/G worker envelope keyed by that run/session id. It requires validated `worker_role_provenance.role_resolution_source == "dispatcher_composition"`, requires `dispatch_run_id` to equal the inherited run id, and uses the explicit envelope role. It does not read dispatcher rules, target maps, eligibility, ranking, or the durable registry, and it does not call `open_session` or overwrite the dispatcher-composed envelope.
2. **Interactive owner/session path.** With no dispatch run id, the wrapper either consumes an exact open Goose envelope selected by `GOOSE_SESSION_ID` whose validated provenance is transcript-derived, or accepts a canonical role-bearing `--init-keyword` supplied for the direct interactive launch. If an exact envelope does not already exist, that explicit keyword is parsed by the canonical grammar and passed once to `open_session` with `worker_role_source="transcript_init_keyword"`, no caller-created session id, and its explicit role. Subject-only, missing, ambiguous, malformed, or conflicting evidence fails before prompt construction or child launch.

The wrapper then maps `bridge-review` and `verification` to required activity role `loyal-opposition`, and `implementation` to required activity role `prime-builder`. This mapping is a constraint on an already-resolved role, never an authority source. A mismatch rejects. Unknown or role-neutral routes preserve the validated envelope role without substituting from the skill name. The exact envelope session id is injected as `GOOSE_SESSION_ID` only after all authority and activity checks pass.

This preserves version 009's timestamp repair: an interactive wrapper-created envelope derives its id and `opened_at` in one canonical `open_session` call, while a dispatched launch reuses the single envelope already composed before delivery. The wrapper never samples a timestamp or synthesizes a session id.

### F2 — Retired role specification was linked and the active bootstrap DCL was absent

**Accepted and corrected.** The retired version-6 role-governance record cited by v009 is intentionally absent from this proposal's active Specification Links. Active `DCL-SESSION-ROLE-RESOLUTION-001` version 7 is now the primary role-bootstrap authority. Its required dispatcher-composition/worker-bootstrap split, explicit interactive owner evidence, activity-after-role ordering, no-registry-fallback rule, and fail-closed cases are mapped directly to tests below. `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` and `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` supply the active transcript/session-envelope continuity boundary.

## Current Chain, Authority, And Exact Target State

- Physical latest is `bridge/gtkb-wi5812-goose-governed-filing-attestation-010.md`, status `NO-GO`, SHA-256 `7C56297A3270E998CC728FF78E47D4B4A7CAA5CBC8EBF495088A2EAC81BA9439`.
- Physical v009 remains `REVISED`, SHA-256 `2B44C1848E8AA59591AEA0F35A86C6162235FDF973FE3B0D7D79B248CC910EF0`.
- The governed revision planner resolves v011 as the next append and v010 as its exact predecessor.
- `PROJECT-GTKB-HARNESS-TEST-CORRECTIONS` is active; WI-5812 is an active direct member.
- Active list-free whole-project PAUTH `PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730` is unexpired and controls operation-time authority. Deprecated `work_items.approval_state` is noncontrolling. Independent GO, exact claim, schema-v3 start packet, report, and VERIFIED remain mandatory.
- Prime Builder session `019fb19b-7814-73c1-8707-204e432cbf00` holds exact draft claim row `36034`, acquired `2026-08-01T11:51:47Z` and bounded through `2026-08-01T12:51:47Z`.
- Canonical cross-claim evaluation over all eight target paths returned `None` after claim acquisition.
- `git status --short -- <eight targets>` returned no output. The planned new test remains absent.

| Target | Current SHA-256 / state |
|---|---|
| `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` | `F843237ED5DB443418389A1B3B1276B2D0BF1342F4F9B03D5D0910B7912381DD` |
| `scripts/bridge_author_metadata.py` | `0AC4168859E2E4FF855E860A3C5F6B6A21CB57DC4B7336D624728EE2F741A90D` |
| `scripts/gtkb_session_id.py` | `CC1EAC2A7138232ADB4B135A9BB81833EB06AC8E146F29F8918FD571A9951D62` |
| `scripts/goose_harness.py` | `FB38E3F4A52B20DCE8929B8D1E76C3264843E8118B74E5D19B1CA9B79C140DBA` |
| `platform_tests/scripts/test_session_envelope_cli_provenance.py` | `B2C2A41BBC55323C0F362267DFE935C572B02AF8DA54DB01229A3A2472A1E230` |
| `platform_tests/scripts/test_bridge_author_metadata.py` | `39DD96E0987346A68869C0E872331AB7ECEA9AA647B0FD247E15130BFDF82097` |
| `platform_tests/scripts/test_gtkb_session_id.py` | `8AEAF094836923D5ADA1738F8AF81C4B332830789866BCF01495F8717E4C9B77` |
| `platform_tests/scripts/test_goose_governed_filing.py` | absent; planned new module |

Immediately before any later implementation, reread the latest physical chain, active project/PAUTH, exact eight target states, current claim, and cross-claim overlaps. Drift, authority loss, or overlap fails closed.

## WI-5825 Separation And Ordering

During this draft's pre-filing window, WI-5825 advanced independently to `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-005.md`, status `NO-ACTION`, SHA-256 `C80D442729C991732ACB57C3C41DCAC5F538DB92E144BD36B472009FA8C5ABBC`. That targetless correction requests a governance-compliant Loyal Opposition rereview of v004; it neither reactivates historical v002 nor starts the five-target recovery. No WI-5812 target, claim, or content was involved in that concurrent append.

1. WI-5812 proceeds only after this v011 receives independent current GO, a fresh exact `go_implementation` claim, and a fresh schema-v3 start packet.
2. WI-5812 changes only the eight forward Goose envelope/metadata/session-id/wrapper/test targets declared above.
3. WI-5825 remains a later, disjoint correction/review cycle. Its current v005 requires corrected independent review, and recovery implementation cannot begin until WI-5812 lands and WI-5825 itself has a new current GO, claim, and start packet.

## Proposed Design

### Slice A — exact Goose envelope reuse and attestation

In `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`:

- add `goose -> GOOSE_SESSION_ID` to the host/session binding map;
- add `goose-envelope-open-corroboration` as the Goose metadata source;
- when `envelope open` sees `GOOSE_SESSION_ID`, load the exact pre-opened document and validate its session id, open state, Goose/G identity, and worker-role provenance before reuse;
- never create, substitute, or upgrade role provenance from ambient variables;
- during attestation, require supplied and ambient ids to equal the exact document id and require that id to equal canonical derivation from its own `harness_id` and `opened_at`;
- preserve all existing model, source, role, harness, and state rejections.

### Slice B — fail-closed author-metadata resolution

In `scripts/bridge_author_metadata.py`:

- register the Goose exact-envelope metadata-source token;
- accept only the exact attested Goose per-session document;
- add `GOOSE_SESSION_ID` to session-context environment resolution;
- preserve six-field completeness, placeholder rejection, source equality, explicit/environment/exact-envelope precedence, and the prohibition on treating the shared current-session projection as author authority.

### Slice C — deterministic session-id registry

In `scripts/gtkb_session_id.py`:

- add `GOOSE_SESSION_ID` to the frozen recognized set;
- add it at the documented deterministic position in both bridge-work-intent and marker-continuity orders without changing other precedence;
- update the full-permutation drift-lock tests.

### Slice D — externally authoritative wrapper bootstrap and child injection

In `scripts/goose_harness.py`:

1. Add an optional `--init-keyword` input for direct interactive owner invocation; accept only the canonical role-bearing grammar. This input is not synthesized from `--skill`.
2. Before calling `build_system_prompt`, resolve an exact Goose/G envelope through one of the two authority paths described above.
3. For dispatch, require the already-present `GTKB_BRIDGE_POLLER_RUN_ID` to select a complete exact envelope whose source is `dispatcher_composition` and whose `dispatch_run_id` matches. Reuse it without reading routing/default role state and without rewriting it.
4. For interactive use, consume an exact transcript-derived `GOOSE_SESSION_ID` envelope when supplied. Otherwise require the explicit role-bearing init keyword and perform one canonical `open_session` without a caller-created id. Never fall back to the durable registry, a shared marker, harness identity, skill name, or a hard-coded role.
5. Compare the resolved role to the selected activity. `bridge-review` and `verification` require Loyal Opposition; `implementation` requires Prime Builder. Reject mismatch before prompt construction, metadata resolution, claim, bridge, or child mutation.
6. Copy the child environment, inject `GTKB_HARNESS_NAME=goose` and the exact selected envelope id as `GOOSE_SESSION_ID`, and pass that environment to `subprocess.run`.
7. Do not launch the child if envelope creation/load, provenance validation, dispatch binding, explicit init parsing, role/activity comparison, or session-id derivation fails.

Role-neutral and unknown skill routes may run only with a valid externally established role envelope; they cannot cause role substitution. Broader cross-process session-id uniqueness/collision handling and claim-CLI ambient hardening remain WI-5815 scope.

## In-Root Placement Evidence

All eight implementation and test paths are under `E:/GT-KB`. The only artifact generated by this revision is the next numbered file under `E:/GT-KB/bridge/`. No external path is created, read as authority, or required.

## Scope Boundaries

This proposal excludes:

- every WI-5825 capability-row, receipt, back-fill, republish, compensation, pending-sidecar, and pending-context target;
- WI-5815 global uniqueness/collision and claim-CLI hardening;
- dispatcher/TAFE activation, configuration, lease, routing, recipient selection, or mutation;
- durable registry role reads by the wrapper; shared-marker or harness-default role fallback;
- schema, MemBase, formal-artifact, credential, external-system, deployment, release, push, history rewrite, or destructive-cleanup operations;
- any new timeout, TTL, interval, retry, throttle, scheduler, or daemon literal.

## Cross-Harness Disposition

- **Goose:** gains exact dispatcher/owner envelope consumption, role/activity mismatch rejection, canonical interactive minting, exact child binding, attestation, and governed-filing tests.
- **Codex and Cursor:** existing host-session bindings and attestation sources remain behaviorally unchanged and are covered by adjacent regressions.
- **Claude, Antigravity, Ollama, and OpenRouter:** no harness-specific hook, launcher, role, or configuration target changes. Shared envelope and metadata behavior remains unchanged under the focused suites.
- No harness exclusion or parity waiver is requested.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` — active primary authority: dispatcher composition, explicit worker bootstrap, transcript evidence, role-before-activity, no registry fallback, and typed fail-closed behavior.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` — active transcript/session-envelope persistence and no durable-registry mutation constraints.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` — active architecture for explicit owner direction and dispatcher/interactive authority separation.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — required Goose governed-filing capability floor.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governed writer and append-only chain authority.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — exact-session author identity and role provenance.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` — exact per-session envelope durability and reuse semantics.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active parent-project authority remains operation-time gated.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — operation-time PAUTH controls instead of legacy WI approval state.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH, project, WI, and target linkage is explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every active governing source is concretely linked.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — later verification must execute the mapped behaviors.
- `GOV-ARTIFACT-APPROVAL-001` — no formal-artifact mutation is proposed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — every target and generated artifact stays in-root.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` — advisory exact-envelope/registry authority.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory deterministic fail-closed gates.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory wrapper mechanics belong in deterministic code.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory fresh bridge/project/claim/target reads.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory durable traceability.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory spec/test/evidence linkage.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory NO-GO to REVISED lifecycle.
- `GOV-STANDING-BACKLOG-001` — advisory nonduplicated WI-5812/WI-5815/WI-5825 carriers.

The retired predecessor role-governance record is historical context only and is not cited as active authority.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5812 / TEST-11768, active `DCL-SESSION-ROLE-RESOLUTION-001`, the interactive-persistence ADR/DCL, the linked onboarding/author-provenance/envelope constraints, and v010's concrete counterexample fully determine this correction. No new or revised formal requirement or owner decision is needed before independent review.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": {
    "work_item": "WI-5812",
    "linked_test": "TEST-11768",
    "source_no_go": "bridge/gtkb-wi5812-goose-governed-filing-attestation-010.md"
  },
  "canonical_authority": [
    "DCL-SESSION-ROLE-RESOLUTION-001",
    "DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001",
    "GOV-DOCUMENT-AUTHOR-PROVENANCE-001"
  ],
  "primary_route": "REVISED v011, independent GO, fresh exact claim, schema-v3 start, eight-target implementation, report, independent VERIFIED",
  "baseline": {
    "physical_latest": "v010 NO-GO",
    "existing_targets_clean": 7,
    "planned_new_targets_absent": 1,
    "foreign_cross_claim_overlap": null,
    "wi5825_latest": "v005 NO-ACTION awaiting corrected independent review"
  },
  "before_behavior": "The proposed generic wrapper always self-issued Prime Builder provenance even when bridge-review or verification requested Loyal Opposition behavior.",
  "after_behavior": "The wrapper consumes a complete dispatcher-composed or explicit owner/session envelope, resolves role before activity, and rejects missing or conflicting evidence without substituting from skill or harness defaults.",
  "self_descriptive_naming": "Role authority is named by dispatcher_composition or transcript_init_keyword; activity names constrain but never create role.",
  "obsolete_guidance_disposition": "The retired GOV role specification is removed from active links; active role-bootstrap and persistence DCL/ADR authority replaces it.",
  "history_preservation": "All prior bridge versions, session envelopes, and WI-5825 recovery evidence remain append-only and unchanged.",
  "expected_result": {
    "wrapper_default_roles": 0,
    "lo_modes_receiving_pb_provenance": 0,
    "role_bootstrap_before_activity": true,
    "wi5825_targets_absorbed": 0
  },
  "rollback": {
    "instructions": "Revert only the approved eight-target implementation through a governed successor.",
    "verification": "Rerun dispatcher, interactive, activity-mismatch, envelope, metadata, session-id, parity, lint, format, compile, and diff checks."
  },
  "hard_invariants": [
    "Role comes only from complete dispatcher composition or validated explicit owner/session evidence.",
    "Skill/activity selection never grants, substitutes, or upgrades role.",
    "No dispatcher, TAFE, durable registry role, WI-5815, or WI-5825 mutation enters the implementation."
  ],
  "fail_closed_conditions": [
    "Missing, subject-only, ambiguous, malformed, or conflicting interactive role evidence.",
    "Missing or mismatched dispatcher run/session provenance.",
    "Resolved envelope role conflicts with bridge-review, verification, or implementation activity.",
    "Exact envelope identity, state, source, or session-id derivation is invalid."
  ],
  "essential_context_preservation": "Role authority source, exact envelope id, activity constraint, eight-target boundary, WI-5815 exclusion, WI-5825 ordering, and current project authorization remain explicit."
}
```

## Specification-Derived Verification Plan

| Requirement | Required deterministic evidence |
|---|---|
| Dispatcher composition is worker authority | Seed an exact Goose/G envelope with `dispatcher_composition` and matching run id; assert wrapper reuses it, never reads registry/dispatcher config, never rewrites it, and injects its exact id. |
| Invalid dispatch fails before activity | Missing, malformed, wrong-harness, wrong-session, wrong-source, missing-run, and mismatched-run envelopes reject before `build_system_prompt` and `subprocess.run`. |
| Explicit interactive owner direction | Role-bearing canonical PB and LO init keywords each create one canonical envelope with transcript-derived provenance and no caller-created id; subject-only, absent, malformed, and ambiguous inputs reject. |
| Existing transcript session envelope | An exact `GOOSE_SESSION_ID` envelope with validated transcript provenance is reused without rewrite; shared/current projection and peer marker cannot authorize it. |
| Role precedes activity | Instrument prompt construction and spawn; require successful role resolution first. Skill names never enter envelope-role creation. |
| Activity mismatch | `bridge-review` and `verification` succeed only for Loyal Opposition; `implementation` succeeds only for Prime Builder; opposite pairings reject before child launch. |
| Canonical single timestamp/id | Force a clock boundary during direct interactive open; assert injected id is exactly the value returned by `open_session` and is derived from that envelope's own `opened_at`. |
| Exact envelope reuse and attestation | Missing provenance, wrong role, wrong harness/id, closed, borrowed-id, source-mismatch, and ambient-mismatch cases reject without rewrite or child launch. |
| Six-field author metadata | Attested exact envelope resolves complete author/session/model/harness fields; unattested, source-mismatch, and placeholder cases reject. |
| Session-id drift lock | Frozen set and both precedence tuples include Goose at the declared position without other reordering. |
| Governed filing | Fixture open/reuse/attest/actor resolution/governed proposal path accepts valid role-correct `NEW` and rejects wrong-role status or metadata. |
| Spawn isolation | Each invocation injects only its selected exact envelope id and isolated copied environment; global same-second uniqueness remains WI-5815 scope. |
| WI boundaries | Diff inspection proves no WI-5815 hardening and no WI-5825 target or recovery behavior. |
| Timer direction | No new hard-coded timeout, TTL, interval, retry, throttle, or concurrency literal. |
| Quality | Focused pytest, adjacent role-bootstrap/persistence tests, Ruff check, Ruff format check, compile, and diff checks pass on the exact cohort. |

Planned focused commands:

```text
python -m pytest platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_author_metadata.py platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_goose_governed_filing.py -q --tb=short
python -m pytest platform_tests/scripts/test_dispatched_role_bootstrap.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_dcl_interactive_session_role_persistence.py -q --tb=short
python -m ruff check <the eight approved paths>
python -m ruff format --check <the eight approved paths>
python -m py_compile <the four approved Python source paths>
git diff --check -- <the eight approved paths>
```

The implementation report must record exact commands and observed results; planned tests are not execution evidence.

## Acceptance Criteria

1. The wrapper contains no default Prime Builder or Loyal Opposition role and never derives role from `--skill`, harness identity, shared marker, or durable registry fallback.
2. A headless launch consumes only a complete exact dispatcher-composed Goose envelope with matching run/session provenance and does not rewrite it.
3. A direct interactive launch consumes an existing exact transcript-derived session envelope or requires an explicit role-bearing canonical init keyword and performs one canonical open without a caller-created id.
4. Role bootstrap completes before activity prompt construction; bridge-review/verification require Loyal Opposition and implementation requires Prime Builder.
5. Missing, subject-only, malformed, ambiguous, wrong-source, wrong-run, wrong-role, wrong-harness, closed, borrowed-id, source-mismatch, and ambient-mismatch cases fail before metadata, bridge, or child mutation.
6. Later envelope-open and attestation reuse the exact document and validate provenance without ambient authority or rewrite.
7. Complete Goose author metadata reaches governed filing for valid PB and LO paths without the existing missing/invalid filing-session identity failure.
8. Existing Codex/Cursor and shared-envelope/role-bootstrap/persistence tests remain green.
9. No WI-5815 or WI-5825 implementation is absorbed; WI-5825 remains blocked pending its own corrected independent verdict and a current GO after WI-5812 lands.
10. Only the exact eight target paths change; current hashes and overlap are reread immediately before implementation.
11. Focused and adjacent tests, Ruff lint, Ruff format, compile, and diff checks pass with observed evidence.
12. No new hard-coded timer or any dispatcher/TAFE, database, credential, external-system, deployment, release, push, or history mutation occurs.

## Risks And Rollback

- **Authority confusion:** accepting an activity name as role would recreate v010. The implementation keeps role bootstrap in a separate helper and passes the resolved role into the later activity constraint.
- **Dispatcher mutation:** the worker must not repair or rewrite a dispatcher envelope. Any missing or conflicting dispatch evidence rejects and reports typed recovery.
- **Interactive spoofing:** an ambient id alone is insufficient; the exact document must validate and carry a transcript-derived source. A direct new envelope requires canonical explicit role-bearing init input.
- **Pre-open side effect:** direct interactive envelope creation is an explicit prerequisite. If child launch fails, the open envelope remains durable evidence; it is not silently deleted.
- **Recovery duplication:** WI-5825's five paths and behaviors remain excluded.
- **Rollback:** through a governed successor, revert only the approved four source and four test paths. Do not rewrite envelopes, bridge history, capability rows, receipts, or unrelated files.

## Candidate Pre-Filing Preflights

Both mandatory checks must run against this exact stable non-live candidate immediately before governed physical filing. Successful filing must be followed by canonical path/status/hash/currentness readback and exact claim consumption confirmation.

## DISARM — Implementation And Publication Boundary

This candidate authorizes no protected edit. Implementation requires a new independent GO on v011, fresh exact `go_implementation` claim, fresh schema-v3 start packet, exact eight-target/overlap recheck, factual implementation report, and independent atomic VERIFIED. No direct bridge write, implementation-target mutation, diagnostic-only database retry, or TAFE/dispatcher activation is authorized.

## Recommended Commit Type

Recommended later implementation type: `feat:` — add role-authoritative Goose envelope attestation and governed filing with fail-closed PB/LO coverage.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
