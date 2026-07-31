NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; Prime Builder; owner-driven manual Loyal Opposition review
author_metadata_source: x-codex-turn-metadata

# WI-5718 Retired Session-Role Authority Operative-Reference Purge

bridge_kind: prime_proposal
Document: gtkb-wi5718-retired-session-role-authority-purge
Version: 001
Date: 2026-07-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-WI5718-RETIRED-ROLE-AUTHORITY-PURGE-20260728
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5718

target_paths: [".claude/rules/operating-role.md", ".claude/rules/prime-builder-role.md", "AGENTS.md", "CLAUDE.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", "config/agent-control/declarative-agent-role-manifest.yaml", "config/agent-control/gtkb-declarative-agent-role-manifest.yaml", "config/agent-control/gtkb-lo-startup-overlay.md", "config/agent-control/gtkb-operating-role.md", "config/agent-control/gtkb-prime-builder-role.md", "config/agent-control/gtkb-system-interface-map.toml", "config/agent-control/system-interface-map.toml", "dashboard/dashboard-data.json", "groundtruth-kb/docs/reference/canonical-terminology-detail.md", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml", "platform_tests/scripts/test_antigravity_startup_overlay_integration.py", "platform_tests/scripts/test_dcl_role_resolution_authority_001.py", "platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py", "platform_tests/scripts/test_harness_role_protocol_smoke.py", "platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py", "platform_tests/scripts/test_lo_startup_text.py", "platform_tests/scripts/test_modernization_authority_foundations.py", "platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py", "platform_tests/scripts/test_wi4348_rule_state_strip_phase1.py", "platform_tests/scripts/test_work_intent_role_eligibility.py", "groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-WI5718-RETIRED-ROLE-AUTHORITY-PURGE.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-AGENTS-MD.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-CLAUDE-MD.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-DCL-SESSION-ROLE-RESOLUTION-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-GOV-HARNESS-ONBOARDING-CONTRACT-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001.json", ".groundtruth/formal-artifact-approvals/2026-07-28-WI5718-SPEC-DISPATCH-ENVELOPE-ELEMENT-001.json"]

implementation_scope: configuration_documentation_governance_metadata_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
Recommended commit type: fix

KB Mutation: This proposal appends current specification and work-item versions
through governed CLI services. `groundtruth.db` is therefore intentionally in
`target_paths`. No direct SQL, schema change, row deletion, or specification
deletion is authorized.

## Structured Project Authorization Envelope

```json
{
  "project_id": "PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS",
  "id": "PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-WI5718-RETIRED-ROLE-AUTHORITY-PURGE-20260728",
  "status": "active",
  "included_work_item_ids": ["WI-5718"],
  "included_spec_ids": [
    "GOV-FILE-BRIDGE-AUTHORITY-001",
    "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
    "GOV-ARTIFACT-APPROVAL-001",
    "GOV-PLATFORM-SOT-REGISTRY-001",
    "DCL-SOT-REGISTRY-PROJECTION-PARITY-001",
    "DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001",
    "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
    "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
    "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
    "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
    "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
    "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
    "DCL-SESSION-ROLE-RESOLUTION-001",
    "DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001",
    "ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001"
  ],
  "allowed_mutation_classes": [
    "bridge",
    "configuration",
    "documentation",
    "governance_evidence",
    "metadata",
    "runtime_state",
    "source",
    "test"
  ],
  "forbidden_operations": [
    "credential_lifecycle",
    "destructive_cleanup",
    "dispatcher_mutation",
    "external_system_mutation",
    "git_history_rewrite",
    "git_push",
    "production_deployment",
    "release",
    "specification_deletion"
  ]
}
```

Owner evidence: .groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-WI5718-RETIRED-ROLE-AUTHORITY-PURGE.json

---

## Claim

The owner has retired `GOV-SESSION-ROLE-AUTHORITY-001` because its
harness-scoped worker-role framing is defective. The formal record is already
version 6 with status `retired`; prior versions and canonical audit trails are
immutable. The remaining work is to remove the retired identifier and any
claim that depends solely on it from every operative registered surface while
preserving current exact-session and dispatched-worker role requirements under
their surviving DCL/ADR authorities.

This is a deterministic decontamination, not an agent-driven recursive
find/replace. Every file occurrence is inventory-derived and preimage-counted.
Every current MemBase record is obtained through canonical CLI read surfaces.
Implementation must abort before mutation if the live scope differs from the
approved manifest.

## Retirement Rationale

Worker role authority belongs to one exact interactive session context or one
explicitly composed dispatched-worker packet. A harness has durable identity,
capabilities, and dispatch eligibility; it does not own one shared operating
role for every concurrent worker using that harness. Keeping the retired GOV in
startup text, manifests, tests, or current specifications would continue to
teach and enforce the defective model after formal retirement.

This purge does not introduce file permissions, provenance requirements for
ordinary editor saves, or content-invalidating audit gates. Owner hand edits
remain valid without notation. Missing attribution or content-observation
evidence remains a warn-and-repair condition, not a reason to reject correct
content or stop useful work.

## Current Deterministic Inventory

The canonical command
`gt admin inventory scan-strings --match GOV-SESSION-ROLE-AUTHORITY-001 --report-only --json`
was re-run on 2026-07-28 against 2,348 registry records and 16,922 expanded
registered files. It found 1,123 hits across 636 unique paths.

| Classification | Unique paths | Hits | Disposition |
| --- | ---: | ---: | --- |
| `bridge/**` | 548 | 990 | Immutable numbered audit history; preserve |
| `.groundtruth/formal-artifact-approvals/**` | 62 | 83 | Immutable approval evidence; preserve |
| `memory/pending-owner-decisions.md` | 1 | 7 | Canonical historical owner-decision audit input; preserve |
| Operative/generated registered surfaces | 25 | 43 | Exact implementation manifest below |

The scanner reports `groundtruth.db` as an active opaque container that cannot
be text-expanded. That is not accepted as a coverage substitute or silently
ignored. Separate canonical current-record queries found exactly nine specified
specifications and eleven current work-item projections containing the retired
identifier. Those records are an independent required transformation set.

The proposal itself will add an allowed occurrence under `bridge/**`; no fixed
post-filing historical count is authoritative. The postcondition is path-class
based: zero hits outside the three explicit immutable-history roots.

## Exact File Transformation Manifest

These 25 paths are the complete non-audit set from the registry-backed scan.
The expected total is 43 literal occurrences. Implementation must create an
explicit machine-readable map containing each path, expected preimage SHA-256,
expected occurrence count, and exact replacement operation. It must first
validate all 25 preimages and all 43 occurrences, then write atomically. Any
missing, added, changed, or duplicate occurrence aborts the entire file phase.

| Count | Path | Transformation class |
| ---: | --- | --- |
| 1 | `.claude/rules/operating-role.md` | Remove retired authority citation; retain exact-session role authorities |
| 1 | `.claude/rules/prime-builder-role.md` | Same |
| 1 | `AGENTS.md` | Remove retired citation from active operating-role guidance; formal packet required |
| 2 | `CLAUDE.md` | Remove active citation and retired-spec inventory row; formal packet required |
| 1 | `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md` | Remove retired startup authority |
| 1 | `config/agent-control/declarative-agent-role-manifest.yaml` | Remove retired spec list item |
| 1 | `config/agent-control/gtkb-declarative-agent-role-manifest.yaml` | Apply identical retained-destination correction |
| 1 | `config/agent-control/gtkb-lo-startup-overlay.md` | Apply identical retained-destination correction |
| 1 | `config/agent-control/gtkb-operating-role.md` | Apply identical retained-destination correction |
| 1 | `config/agent-control/gtkb-prime-builder-role.md` | Apply identical retained-destination correction |
| 2 | `config/agent-control/gtkb-system-interface-map.toml` | Remove retired related-spec entries while preserving valid TOML arrays |
| 2 | `config/agent-control/system-interface-map.toml` | Same canonical retained-source correction |
| 1 | `dashboard/dashboard-data.json` | Replace stale current-projection text from corrected MemBase records; preserve valid JSON |
| 1 | `groundtruth-kb/docs/reference/canonical-terminology-detail.md` | Replace retired source citation with surviving exact-session authorities |
| 2 | `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml` | Regenerate/correct packaged map projection from canonical source |
| 1 | `platform_tests/scripts/test_antigravity_startup_overlay_integration.py` | Replace retired authority comment with current DCL/ADR authority |
| 9 | `platform_tests/scripts/test_dcl_role_resolution_authority_001.py` | Remove obsolete GOV-presence test; add retirement and zero-operative-reference guard without embedding the full literal |
| 3 | `platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py` | Replace obsolete citations and harness-role wording with dispatch-packet/session wording |
| 3 | `platform_tests/scripts/test_harness_role_protocol_smoke.py` | Replace fixture authority text while preserving behavioral expectations |
| 2 | `platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py` | Replace retired citations with exact-session resolution authority |
| 1 | `platform_tests/scripts/test_lo_startup_text.py` | Replace retired startup authority citation |
| 1 | `platform_tests/scripts/test_modernization_authority_foundations.py` | Replace retired required-spec fixture with current authority set |
| 2 | `platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py` | Replace retired citation and durable-harness-role wording with dispatched-packet authority |
| 1 | `platform_tests/scripts/test_wi4348_rule_state_strip_phase1.py` | Replace retired citation |
| 1 | `platform_tests/scripts/test_work_intent_role_eligibility.py` | Replace retired citation with exact-session claim authority |

The paired source/destination files retained for WI-5640 are all registered and
remain temporarily load-bearing. Both sides must receive equivalent semantic
corrections. This proposal does not delete, move, rename, or un-register either
side.

## Current Specification Amendments

Nine current `specified` records contain the identifier. Each receives exactly
one append-only version through `gt spec update`, preserving its status and all
unrelated fields. Exact postimage content must be validated by the named formal
approval packet before insertion.

1. `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v2: remove the retired Authority
   bullet; retain the persistence DCL and bridge-verdict provenance.
2. `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` v1: remove the retired GOV
   from the read-together sentence; retain current DCL and ADR authorities.
3. `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` v1: replace the false
   statement that the retired GOV remains the governance boundary with the
   current exact-session persistence authorities.
4. `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v3: remove the retired GOV from
   its authority list; retain init syntax and deterministic resolution links.
5. `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` v1: remove the retired GOV from
   the relationship paragraph and preserve warn-not-override semantics.
6. `DCL-SESSION-ROLE-RESOLUTION-001` v6: remove the retired authority bullet and
   its `affected_by` entry; preserve the exact session/dispatched packet table
   and all structured assertions.
7. `GOV-HARNESS-ONBOARDING-CONTRACT-001` v1: remove the retired GOV from the
   related-artifact list; preserve identity/capability/dispatch eligibility.
8. `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3: remove the retired GOV from its
   authority list; preserve current syntax and resolution links.
9. `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` v1: replace the retired parenthetical
   with surviving dispatched-packet/session-separation authority.

No specification is deleted, status-promoted, or semantically weakened. Prior
versions remain immutable and may continue to contain the identifier as
historical MemBase evidence.

## Current Work-Item Projection Amendments

Canonical `gt backlog list --all --contains ... --json` currently returns 11
current records: ten resolved historical work items plus WI-5718 itself. Each
receives one append-only current version through `gt backlog update`; stage and
resolution status remain unchanged.

- `WI-3479`, `WI-4291`, `WI-4296`, `WI-4371`, `WI-4663`, `WI-4764`, and
  `WI-4784`: replace obsolete current descriptive/linkage text with surviving
  role-resolution authorities while preserving the prior version as history.
- `WI-4781`: replace the current title, description, and `source_spec_id`
  reference with a historical-retirement description linked to
  `DCL-SESSION-ROLE-RESOLUTION-001`; retain resolved lifecycle.
- `WI-5150` and `WI-5171`: replace current `source_spec_id` and descriptive
  references with current DCL/ADR authorities; retain resolved lifecycle.
- `WI-5718`: after verified implementation evidence is ready, update its title,
  description, status detail, and source-owner reference to cite
  `DELIB-202667220` and the generic retired record without reintroducing the
  identifier. It remains open until terminal VERIFIED and canonical resolution.

The update service must preserve every unspecified field. Direct SQL and bulk
status mutation are forbidden.

## Executable Zero-Reference Guard

`platform_tests/scripts/test_dcl_role_resolution_authority_001.py` will replace
the obsolete test that requires the old GOV body with a retirement guard that:

1. Constructs the retired identifier from non-contiguous constants so the test
   does not create a new literal scanner hit.
2. Confirms the current spec is version 6 or later and `retired`.
3. Calls the canonical registry-backed inventory scanner and rejects every hit
   outside `bridge/**`, `.groundtruth/formal-artifact-approvals/**`, and
   `memory/pending-owner-decisions.md`.
4. Reads current specification/work-item projections through supported APIs
   and rejects the identifier in every current record, including WI-5718.
5. Treats opaque-container file-scan coverage separately from current MemBase
   record coverage rather than declaring an unread binary container clean.

The guard protects semantics, not file permissions. It emits a clear list of
operative regressions; it does not require special notation for owner edits.

## In-Root Placement Evidence

Every target is under `E:/GT-KB`. The 25 file targets resolve through the
canonical registry snapshot to active exact-coverage records. The database and
approval packets are governed in-root authorities. No external file, scratchpad,
transcript, cloud path, or non-root dependency is used as implementation
authority.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` - surviving deterministic exact-session and dispatched-worker resolution authority.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - exact interactive-session persistence authority.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - owner-approved separation of interactive session role from dispatcher metadata.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO, exact claim, report, and verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - binds implementation to the WI-5718-only PAUTH.
- `GOV-ARTIFACT-APPROVAL-001` - requires exact-content packets for AGENTS/CLAUDE narrative changes.
- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` - requires exact postimage approval for all nine specification versions.
- `GOV-PLATFORM-SOT-REGISTRY-001` - makes the registered artifact inventory authoritative.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - requires coherent declaration/projection reads during scanning and observation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - governs the PAUTH/project/WI triple.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete current specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed spec-to-test evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserves append-only versions and post-VERIFIED WI resolution.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves durable owner decision, proposal, report, and verdict artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the exact transformation and recovery artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires all implementation and evidence inside the project root.
- `GOV-WORK-TREE-HYGIENE-001` - requires scoped mutation/finalization without unrelated worktree absorption.

## Prior Deliberations And Evidence

- `DELIB-202667220` - controlling owner decision to retire the defective
  harness-scoped GOV, purge every active reference, preserve immutable audit
  trails, and prove zero operative references mechanically. It is now linked
  to WI-5718 as `owner_authority`.
- `DELIB-20260710-GTKB-INTERACTIVE-KB-ATTRIBUTION-GLOBAL-MARKER-COLLISION` -
  evidence that shared harness state can misattribute another session.
- `DELIB-20263212` - owner requirement for interactive context continuity.
- `DELIB-202667477` - owner-selected WI-5679 continuity and strict
  transcript-only inheritance design; implementation remains in its own thread.
- `.gtkb-state/bridge-propose-drafts/gtkb-wi5568-retired-role-authority-reference-purge-001.md`
  - superseded non-dispatchable draft used only as investigation evidence;
  WI-5568 explicitly assigns this purge to WI-5718.

## Owner Decisions / Input

`DELIB-202667220` contains the owner's direct decision and exact boundary:
retire the version-5 harness-scoped authority, remove it from all active
references, preserve immutable history, replace worker-role authority with
exact session context/dispatched packet authority, and prove the result with a
deterministic scan. It does not claim an AskUserQuestion UI event; this proposal
relies on the substantive direct transcript decision and makes no stronger
channel-provenance claim.

The active WI-specific authorization is
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-WI5718-RETIRED-ROLE-AUTHORITY-PURGE-20260728`.
It allows only WI-5718's bridge, configuration, documentation, governance
evidence, metadata, runtime projection, source, and test classes. It permits one
bounded local terminal commit and forbids credential, destructive, dispatcher,
external-system, history-rewrite, push, deployment, release, and specification
deletion operations.

No new owner decision is required for the bounded design. Exact content for the
eleven formal/narrative mutations must still be packet-validated before those
individual writes. The project-authorization evidence packet above is the
twelfth packet in the complete validation set and is not an implementation
postimage.

## Requirement Sufficiency

**Existing requirements sufficient.** This proposal removes a retired
authority and re-homes no new policy. `DELIB-202667220` supplies owner intent;
the current DCL/ADR session authorities supply retained behavior; registry,
formal-artifact, bridge, lifecycle, and test authorities supply mechanical
controls. WI-5721 separately formalizes the broader three-worker parallelism
requirement and is not absorbed here.

## Implementation Sequence

1. Acquire an exact-session `go_implementation` claim and implementation-start
   packet after controlling GO.
2. Re-run the registry-backed file scan plus current spec/work-item queries.
   Compare exact counts and IDs to this proposal; stop on drift and return with
   a REVISED proposal if scope changed.
3. Produce all 25 exact file postimages in a transaction-local staging area
   from the preimage-bound transformation map. Parse TOML, YAML, and JSON with
   structured parsers after transformation. Do not recursively edit files by
   agent judgment.
4. Produce nine exact specification postimages and two exact narrative
   postimages; create and validate their eleven named approval packets. Recheck
   the existing project-authorization packet as the twelfth packet.
5. Apply the file postimages atomically, update the nine specifications through
   `gt spec update`, and update the eleven work items one at a time through
   `gt backlog update`. Preserve all unrelated fields and lifecycle states.
6. Refresh/regenerate the declared retained mirrors and dashboard projection;
   never copy a generated child back over its canonical source.
7. Record passive registry observations through the canonical observation
   service. Stable-path content changes do not alter registry identity rows.
8. Run both zero-reference scans, focused tests, parsers, packet validators,
   registry coherence/parity checks, and worktree-scope checks.
9. File a `NEW` implementation report. Independent LO either atomically files
   terminal VERIFIED with the exact authorized implementation set or leaves no
   terminal candidate. Only after commit-backed VERIFIED may WI-5718 resolve.

## Specification-Derived Verification Plan

| Requirement | Mechanical verification and required result |
| --- | --- |
| Formal retirement persists | `gt spec show GOV-SESSION-ROLE-AUTHORITY-001 --json`: current version >=6, status `retired`, historical versions unchanged |
| Registry file coverage | `gt admin inventory scan-strings --match ... --report-only --json`: zero hit outside the three immutable-history roots |
| Current specs clean | `gt spec list --search ... --limit 500 --json`: zero current result |
| Current work items clean | `gt backlog list --all --contains ... --limit 500 --json`: zero current result |
| File manifest exact | Recompute 25 paths/43 preimage hits before mutation; zero unclassified or changed preimage |
| Registry coherent | `gt registry inspect --no-census --json`, `gt registry validate --json`, and `gt registry sync --json`: coherent/current declaration and projection; content-observation warnings disclosed without invalidating correct bytes |
| Structured files valid | Parse all changed TOML, YAML, and JSON with repository-native parsers; zero parse error |
| Formal packets valid | Canonical packet validator passes the project-authorization packet plus all eleven named postimage packets |
| Role behavior preserved | Run all ten targeted test modules plus current WI-5679-adjacent session resolution tests; no WI-5718 regression |
| Zero guard works | New test fails on a synthetic operative hit and passes on the live allowlisted history split |
| Hand-edit contract preserved | Focused tests prove direct owner content remains valid and attribution/observation gaps are warn-and-repair, not content-invalidating |
| Worktree bounded | `git diff --name-only`, `git diff --cached --name-only`, `git diff --check`, and final commit inventory contain only authorized paths; unrelated untracked bridge work preserved |

Focused commands must include at least:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_antigravity_startup_overlay_integration.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py platform_tests/scripts/test_harness_role_protocol_smoke.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py platform_tests/scripts/test_lo_startup_text.py platform_tests/scripts/test_modernization_authority_foundations.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py platform_tests/scripts/test_wi4348_rule_state_strip_phase1.py platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_role_keying_continuity.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_workstream_focus_hook_parity.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/scripts/test_antigravity_startup_overlay_integration.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py platform_tests/scripts/test_harness_role_protocol_smoke.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py platform_tests/scripts/test_lo_startup_text.py platform_tests/scripts/test_modernization_authority_foundations.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py platform_tests/scripts/test_wi4348_rule_state_strip_phase1.py platform_tests/scripts/test_work_intent_role_eligibility.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/scripts/test_antigravity_startup_overlay_integration.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py platform_tests/scripts/test_harness_role_protocol_smoke.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py platform_tests/scripts/test_lo_startup_text.py platform_tests/scripts/test_modernization_authority_foundations.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py platform_tests/scripts/test_wi4348_rule_state_strip_phase1.py platform_tests/scripts/test_work_intent_role_eligibility.py
```

## Acceptance Criteria

1. The retired GOV remains append-only at version 6 or later with status
   `retired`; no prior specification, bridge, deliberation, approval packet, or
   historical work-item version is rewritten or deleted.
2. The registry-backed scan reports no current hit outside `bridge/**`,
   `.groundtruth/formal-artifact-approvals/**`, and
   `memory/pending-owner-decisions.md`.
3. Current-spec and current-work-item CLI searches both return zero records;
   opaque MemBase coverage is proven through those record APIs, not inferred
   from a binary file scan.
4. Exactly 25 registered files and 43 pre-change operative occurrences are
   transformed from approved preimages; any scope drift aborts before mutation.
5. Nine specifications and eleven work items receive append-only current
   versions with all unrelated fields and lifecycle states preserved.
6. The project-authorization packet and all eleven exact-content postimage
   approval packets validate; no formal/narrative artifact bypass occurs.
7. The executable zero-reference guard contains no full literal identifier,
   rejects synthetic operative recurrence, and permits only the three explicit
   immutable-history roots.
8. All targeted source/destination retention pairs remain present, registered,
   semantically equivalent where intended, and free of the retired citation.
   No WI-5640 source is deleted, moved, renamed, or unregistered.
9. Exact-session and dispatched-worker role behavior remains governed by the
   surviving DCL/ADR authorities; no active text says a harness owns the worker
   role of all sessions using it.
10. Ordinary owner text-editor changes require no notation. Audit or passive
    observation gaps remain visible repair-forward warnings and do not
    invalidate correct content or block unrelated useful work.
11. Registry declaration/projection parity and identity remain coherent; stable
    path content edits do not create, remove, or rename registry records.
12. No unrelated worktree path, dispatcher action, destructive cleanup,
    history rewrite, push, release, deployment, credential action, or external
    mutation occurs.
13. Terminal VERIFIED and its bounded local commit are atomic. WI-5718 resolves
    only after that commit and cites both the owner decision and terminal
    evidence.

## Risks And Rollback

The principal risk is a broad token deletion that leaves invalid TOML/YAML or
semantically false prose. Exact preimage hashes, occurrence counts, per-path
operations, structured parsing, and postimage packet validation constrain that
risk. A second risk is cleaning text files while leaving current MemBase rows
dirty; independent current-record searches prevent that partial success. A
third risk is accidentally rewriting immutable audit history; the transform
map excludes all three historical roots and the final diff inventory must prove
that exclusion.

Before report filing, rollback is append-only repair-forward: restore only
authorized file postimages from transaction-local preimages and append
correcting current record versions through canonical services. Never delete or
rewrite prior MemBase versions or bridge history. A failed terminal finalization
must leave no terminal verdict candidate and no staging residue.

## Files Expected To Change

Exactly the `target_paths` declaration above, except that `groundtruth.db` and
approval packets are by-reference/generated evidence governed by their own
transaction rules. No registry declaration path is expected to change because
all artifact identities and storage paths remain stable.

## Recommended Commit Type

`fix`

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
