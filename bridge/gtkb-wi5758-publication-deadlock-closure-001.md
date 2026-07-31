NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 08ab8a9d-bc19-4278-b81f-a8b3a488700c
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code headless proposal worker; manual dispatch per DELIB-202667523; resolved role prime-builder for this filing

# Implementation Proposal - Close The Bridge-Publication Deadlock Class: Writer Self-Observation And Crash-Surviving Pending-Publication State (WI-5758)

Document: gtkb-wi5758-publication-deadlock-closure
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-07-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5758

target_paths: ["scripts/gtkb_bridge_writer.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge/state_report.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py", "platform_tests/groundtruth_kb/cli/test_registry_observe_cli.py"]

Scope confirmation: this proposal performs no MemBase mutation and no groundtruth.db write during filing. This filing performs no approval-evidence work; it requires no approval packets. All eight target_paths are in-root; the first seven exist at HEAD (each verified with Test-Path before filing) and the eighth (`platform_tests/groundtruth_kb/cli/test_registry_observe_cli.py`) is a new test module created by the implementation.

---

## Problem

Source advisory: `bridge/gtkb-lo-bridge-publication-registry-currentness-deadlock-advisory-001.md` (adapt; read in full).
Source advisory: `bridge/gtkb-bridge-aggregate-drift-publication-lockout-001.md` (adopt; F1 + F2; read in full).

The bridge-publication control loop can deadlock the whole platform. `mint_bridge_publication_capability` (`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py:2559`) refuses every governed bridge publication unless the `bridge-versioned-files` aggregate is registry-current (:2602-2611) and its latest recorded revision equals the live digest (:2651-2656). The aggregate is a glob over `bridge/*-NNN.md`, so ANY unobserved change under `bridge/` - a crash between create and consume, a compensation failure that retains the file, a harness Write-tool file with no observation capability, an editor, a git checkout/stash - strands the registry stale. Once stale, every publication (including terminal `VERIFIED` finalization) is refused platform-wide, and no reviewer-reachable command restores currentness: `append_passive_observation` (:2298) has no CLI surface, the PostToolUse observation hook requires a capability minted by the implementation-start gate for a real tool event, `recover_registry` (:1576) covers transaction-journal states only, and the one-time WI-5441 bootstrap is retired and raises (:3130). Both advisories observed the lockout live (2026-07-26 and 2026-07-28); WI-5758 records it as a twice-recurred convergence-run blocker.

Current-state accuracy note (verified at HEAD for this proposal; the Loyal Opposition reviewer can re-verify each anchor): the fully-successful governed path is ALREADY self-observing. `write_bridge_file` (`scripts/gtkb_bridge_writer.py:998`) mints (:1065), exclusively creates (:1085), re-reads (:1107), then consumes (:1137); `consume_bridge_publication_capability` appends the post-image aggregate revision inside its own BEGIN IMMEDIATE control-plane transaction (:2784-2798) and asserts final currentness (:2830-2839). The deadlock class therefore survives not on the happy path but through four windows:

- W1 - process death between exclusive create (:1085) and consume (:1137): the file is on disk, the capability row expires in state `minted`->`expired`, no post-image revision exists, the aggregate is stale.
- W2 - consume failure whose compensation ALSO fails: `_compensate_publication` (:936) raises `BRIDGE_PUBLICATION_REPAIR_REQUIRED` and the file is retained (`compensate_bridge_publication` retained-file branches, registry_control_plane.py:2906-2915) - an unobserved on-disk mutation, silently stale.
- W3 - deferred finalization (`release_claim=False`, the VERIFIED-finalizer window): the pending publication is recorded ONLY in the module-level in-memory dict `_PENDING_BRIDGE_PUBLICATIONS` (:888, stored :1154). After process death `rollback_pending_bridge_publication` (:977) raises `BRIDGE_PUBLICATION_REPAIR_REQUIRED: pending capability context is unavailable` (:991-993) because `compensate_bridge_publication` requires the raw capability secret (:2863-2871) and the secret died with the process; the DB row retains only `capability_hash`. This is advisory-2 Finding F2, observed live.
- W4 - out-of-band drift (git operations, editors, harness-tool files without observation capabilities, manual deletion of W1/W2 strands): stale with no in-band re-observation path at all. This is advisory-2 Finding F1; its live repair depended on still holding the exact pre-incident bytes, which will not generally be true.

Three aggravating properties (advisory 1): the failure is silent until it is total (staleness accumulates unwarned, then blocks everything at once); the default diagnostic disagrees with the gate (`gt registry sync`, cli.py:5689, is diagnostic-only and reports healthy while mint refuses); and the only unblock available to a reviewer who fully understands the mechanism would be capability forgery, which correctly fails closed - leaving no legitimate action.

## Proposed Changes

Four changes, mapped one-to-one onto the WI-5758 scope letters. All changes are confined to the eight target_paths. Design authority: AT-01 (`DELIB-202667533`) - commit-first ordering; no pending-then-promote lifecycle state.

### Change A (scope a, primary) - every write_bridge_file exit path leaves the aggregate current or durably recorded

The invariant "a governed publication leaves the registry current by construction" already holds on the success path (consume's in-transaction post-image revision, :2784-2798). Change A extends it to the failure exits so the writer can never strand a silently-unobserved aggregate mutation:

- A1. Retained-file self-observation. In the branches where a failed publication RETAINS the on-disk file - `compensate_bridge_publication`'s retained-file failure branches (:2906-2915) and `write_bridge_file`'s consume-failure handler when compensation itself raises (:1156-1163) - append a passive content observation of the aggregate's live post-state within the same control-plane locked scope (existing `append_passive_observation` machinery; `operation='direct_in_place_content_change'`; `evidence_source_reference=capability_hash`; actor_session from the publication context). The capability row keeps `recovery_required` and its `failure_reason`: the observation restores registry truthfulness (currentness reflects what is actually on disk) while the anomaly remains fully audit-visible. This adopts WI-5696's ratified warn-and-repair posture - observe truthfully, keep audit debt, never convert staleness into a platform-wide stoppage.
- A2. The success-path invariant is pinned by a new sequential-writes regression test (T1): after each of N=3 consecutive governed publications in a fixture project, `registry_currentness(record_ids={'bridge-versioned-files'})` reports current and the next mint succeeds with no manual observation step.

### Change B (scope b) - crash-durable pending-publication state with secret-free finalize/rollback recovery

- B1. Durable pending record. When `write_bridge_file` mints a capability it writes a sidecar record at `.gtkb-state/bridge-publication-pending/<document>-<NNN>.json` containing `capability_hash` (never the raw secret), `document_name`, `version`, `status`, `target_path`, `claim_session`, `content_digest`, `created_at`. The record is deleted on successful consume+claim-release, successful deferred finalize, successful rollback, or successful compensation. The in-memory `_PENDING_BRIDGE_PUBLICATIONS` dict remains the fast path; the sidecar exists so a LATER process can reach the compensation state machine.
- B2. Secret-free recovery entrypoint. New control-plane function `recover_bridge_publication(target_path, session_id, mode='finalize'|'rollback', ...)` that authenticates WITHOUT the raw secret: it locates the capability row by `target_path` + `claim_session`, requires an exact byte match between the on-disk file and the row's `content_digest`, and drives the single-use state machine: (i) row `minted` (or `expired` with byte-matching file - the W1 crash artifact) + finalize mode -> complete the observation leg exactly as consume would (append post-image revision, mark `consumed`); (ii) row `minted`/`expired` + rollback mode -> compensate (remove the exact file, restore preimage evidence, mark `compensated`) with the same retained-file observation fallback as A1; (iii) row `consumed` + finalize mode -> registry side is already complete; release the claim only. Secret-free recovery is sound because the secret's one purpose - binding consume to the exact minted bytes and session - is preserved by the byte-exact `content_digest` match, the claim-session match, and the single-use state transitions; the entrypoint can only complete or revert the exact publication that was minted, never author a new one.
- B3. `finalize_pending_bridge_publication` (:960) and `rollback_pending_bridge_publication` (:977) fall back to the durable sidecar + `recover_bridge_publication` when the in-memory dict misses, eliminating the `BRIDGE_PUBLICATION_REPAIR_REQUIRED` dead-end for the process-death class while preserving it for genuinely unidentifiable states.
- B4. AT-01 conformance (explicit design constraint from `DELIB-202667533`): this persistence is compensation bookkeeping for an interrupted WRITE, not workflow state. It introduces NO pending-then-promote lifecycle: the bridge file carries its final first-line status token from the moment of creation; no new status token is added (`VALID_STATUSES` unchanged); no dispatcher/TAFE state is written; queue actionability derivations never read the sidecar. It is compatible with commit-first ordering: whichever side of the git commit the publication write lands on under the AT-01 finalizer redesign (separately owned by the WI-5666 recovery lane and WI-5742), the sidecar covers exactly the interrupted-write window and nothing else. This proposal does not re-order the finalizer.

### Change C (scope c) - `gt registry observe` operator escape hatch

New subcommand in the existing `gt registry` group (`groundtruth-kb/src/groundtruth_kb/cli.py`, group at :5292): `gt registry observe (--artifact <entry-id> | --path <relative-path>)... --change-reason <text> [--changed-by <id>] [--json]`. It wraps `append_passive_observation` (extended with an optional `record_ids` parameter so glob-aggregate artifacts such as `bridge-versioned-files` can be observed by registry id, not only by member path). Provenance is honest operator provenance: `actor_session` resolves from the open session envelope when available, else `unattributed_external`; `changed_by` defaults to `registry-observer/cli`; no synthetic tool event is fabricated or implied. Observation-only invariants are preserved and tested: an unregistered target errors, a missing path errors (`passive observation cannot record a missing identity transition`), and no declaration, identity, lifecycle, or membership row is amended - the command records present content at already-registered locators, exactly the boundary `append_passive_observation`'s contract states (:2311-2316). This is advisory-1 recommendation 2 and the WI's designated escape hatch for W4 drift that Change A cannot see (out-of-band mutations with no capability context at all).

### Change D (scope d) - stale-observation surfacing before the cliff

`gt bridge state-report` (`groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`) gains a `registry_publication` block: `{enabled, aggregate_current, stale_count, stale_record_ids}` computed via `registry_currentness` scoped to the bridge aggregate record (one glob digest - deliberately cheap; no deep audit, which is WI-5724's separately-owned output-scale territory), plus a single warning line when stale: the bridge publication gate will refuse ALL publications until the aggregate is re-observed, naming `gt registry observe --artifact bridge-versioned-files` as the remedy. Reporting-only: exit codes and queue semantics are unchanged. This converts the total-outage cliff into a visible margin on the canonical bridge read surface and makes the gate's own view visible where `gt registry sync`'s diagnostic-only output misled the advisory-1 reviewer.

## WI-5696 Boundary Delineation (No Duplication)

WI-5696 (P0, PROJECT-GTKB-HOUSEKEEPING-HARDENING, "Automatically admit new load-bearing artifacts and observe registered edits without notation") and this item share the observation vocabulary but own disjoint surfaces. Read against `gt backlog show WI-5696 --json` (v5) before filing:

WI-5696 OWNS (and this proposal does NOT touch):
- The production registry-admission path and deterministic admission candidates for newly created, unregistered load-bearing artifacts.
- General automatic observation across EVERY registered harness mutation surface (Write/Edit/apply_patch tool events, the observation hook, implementation-start-gate capability flow) - "governed worker paths must leave attributable observations automatically when available".
- Hand-edit tolerance semantics: ordinary Notepad/bypass edits require no notation, remain immediately valid, produce non-blocking audit debt; unknown actors remain `unattributed_external`; no content rejected or reverted for absent provenance.
- Classification of the stale registered-test references named in its status detail, and the acceptance requirement to isolate stale-content impact to the affected identity or thread instead of platform-wide stoppage (the general failure-posture change).

WI-5758 (this proposal) ADDS, strictly scoped to the bridge-publication control loop - the one surface where the mutator and the gate consumer are the same component and staleness is a hard platform-wide deadlock rather than repairable audit debt:
- (a) closure of the writer<->gate circularity so a governed bridge publication leaves the registry current by construction on every exit path (Change A);
- (b) crash-durable pending-publication compensation state and secret-free finalize/rollback recovery for interrupted bridge writes (Change B);
- (c) the operator-invoked `gt registry observe` escape hatch - manual re-observation is not part of 5696's automatic-observation pipeline (Change C);
- (d) pre-cliff staleness surfacing on the bridge state-report read surface (Change D).

Composition contract: Change A adopts 5696's warn-and-repair posture (observe truthfully, retain audit debt) so the two items compose rather than conflict; if WI-5696 later generalizes writer-side observation into a shared helper, Change A's two call sites migrate onto it without semantic change. `gt registry observe` records observations only for already-registered artifacts; admission of unregistered artifacts remains entirely 5696's. Change D reports; it does not implement 5696's per-identity blast-radius isolation.

## Explicitly Out Of Scope

- The `gt registry sync` diagnostic redesign (advisory-1 recommendation 3) beyond what Change D surfaces; the state-report block makes the gate's own verdict visible, which removes the operational misdirection without reworking `sync`.
- Doctor severity promotion for staleness (reporting-first per the WI scope; promotion to WARN/FAIL doctor checks is a future owner decision).
- The AT-01 commit-first finalizer re-ordering itself (WI-5666 recovery lane / WI-5742; this proposal only guarantees its compensation state survives process death under either ordering).
- General mutation-surface observation coverage, admission candidates, and failure-posture generalization (WI-5696, delineated above).
- The advisory-1 secondary observations (stray `$null`/`-p` artifacts; `.gtkb-state` staging-directory proliferation) - separately dispositioned in the 2026-07-29 triage.
- Deep-audit output scale (WI-5724).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge audit trail and publication discipline this whole loop serves; the deadlock blocks terminal `VERIFIED` finalization platform-wide, and Changes A/B restore publication durability without weakening the gate.
- `GOV-PLATFORM-SOT-REGISTRY-001` - the SoT artifact registry whose `bridge-versioned-files` record is the gated aggregate; Changes A/C append truthful observations to it through its own control plane.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - state claims derive from fresh canonical reads; the registry's observed state must track reality (Changes A/C) and the staleness margin must be visible on a canonical read surface (Change D).
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - observation is not mutation authority: every new write path added here is observation-or-compensation only, capability-bounded or explicitly operator-attributed; no declaration/identity/lifecycle amendment is added.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - canonical/packaged registry parity is untouched; all changes operate on revision/observation rows and never fork the projection.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - this work proceeds under the cited active program authorization plus this proposal's bridge `GO`; PAUTH metadata does not broaden `target_paths` and does not replace the live latest-`GO` requirement.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` - both source advisories carried owner-grilling gates; the Owner Decisions section below records how the 2026-07-29 triage resolved them before this derived proposal was filed.
- `GOV-17` - automation script modification approval gate: `scripts/gtkb_bridge_writer.py` is commit/publication automation; this proposal plus Loyal Opposition `GO` under the cited project authorization is the approval evidence for modifying it.
- `GOV-10` - tests exercise exposed production interfaces: `write_bridge_file`, the pending finalize/rollback helpers, `recover_bridge_publication`, the `gt registry observe` and `gt bridge state-report` CLI surfaces (CliRunner/subprocess), never private re-implementations.
- `SPEC-1662` (GOV-18) - assertion quality: crash tests assert recoverability outcomes (revision content, capability states, currentness verdicts), not structure; T1 pins the invariant behaviorally.
- `SPEC-1830` - operational procedures must be code: the recovery path becomes `recover_bridge_publication` + CLI-reachable observation, not conversational repair lore; the state-report warning names the exact remedial command.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - the escape hatch and recovery entrypoints are deterministic services replacing per-incident ad-hoc operator judgement (advisory-2's byte-restoration repair).
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - the currentness gate stays mechanically enforced (write-time); Change D adds the review-time visibility layer instead of weakening the write-time layer.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the correction lands as a durable artifact chain (two advisories -> owner triage decisions -> WI-5758 -> this proposal -> spec-derived tests), preserving traceability across the graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - lifecycle states stay explicit; B4 guarantees no implicit new lifecycle state is introduced by the pending sidecar.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section satisfies the mandatory proposal spec-linkage constraint; the verification plan maps each link to derived tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the eventual `VERIFIED` is conditional on creation and execution of the spec-derived tests T1-T8; the implementation report will carry the executed commands and observed results.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - root/application placement boundary: every target path is platform-side and in-root under `E:\GT-KB`; no `applications/` surface, no out-of-root live dependency, and the `.gtkb-state` sidecar directory is in-root runtime state.
- `.claude/rules/file-bridge-protocol.md` § Mandatory VERIFIED Commit-Finalization Gate and § Bridge State Publication - the rule surfaces whose finalization path the deadlock was blocking; the fix preserves their contracts.

Tests derive from these links as mapped in the verification plan below.

## Prior Deliberations

Mandatory search executed: `gt deliberations search "publication registry currentness deadlock" --limit 5` returned `DELIB-202667544`, `DELIB-202665665`, `DELIB-202667543`, `DELIB-202667580`, `DELIB-202667556`:

- `DELIB-202667556` - Loyal Opposition GO, WI-5441 Bridge-Publication Commit Clearance: the adjacent thread that landed the mint/consume/compensate machinery this proposal's current-state analysis is anchored to; this proposal extends its invariant to failure exits rather than re-litigating it.
- `DELIB-202667544` / `DELIB-202667543` - WI-5640 registry-admission NO-GOs: the admission/preflight lane is adjacent but separately owned (WI-5640/WI-5696 track); cited for the boundary drawn above.
- `DELIB-202665665` - WI-4971 evidence-freshness NO-GO: precedent that freshness claims require executed evidence, mirrored in this plan's executed-currentness assertions.
- `DELIB-202667580` - adjacent registry-currentness NO-GO verdict surfaced by semantic search; no controlling prior decision on this exact failure mode.

Program and design authority:

- `DELIB-202667526` - live concurrency evidence (control-plane lock convoying, platform-wide single active publication capability, session-triple binding): design constraints honored by Changes A/B (short transactions under the existing single lock; no new lock; no second capability class) and the reason this filing itself retries on lock/capability contention.
- `DELIB-202667531` - owner advisory-triage decision: fix-class first, corrective WIs created AND authorized; WI-5758 is in that set.
- `DELIB-202667532` - program north star (harmonize, simplify, legacy-cleanse, dependency-sequence) under which WI-5758 was scored and sequenced (convergence order 110).
- `DELIB-202667533` - AT-01..04 synthesis decisions; AT-01 (commit-first, pending-then-promote REJECTED) is a binding design constraint on Change B; AT-04 issued the program PAUTH this thread runs under.
- `DELIB-202667534` - advisory corpus disposition table rows 2-3: both source advisories dispositioned as fix WI `WI-5758` (order 110, merged); this thread implements that disposition.
- `DELIB-202667523` - integrated parallel-operation program mandate and manual-dispatch operating model (this filing is a fan-out worker product).
- `bridge/gtkb-lo-bridge-publication-registry-currentness-deadlock-advisory-001.md` - source advisory (adapt): recommendations 1, 2, and 4 map to Changes A, C, and D; recommendation 3 is scoped out as stated.
- `bridge/gtkb-bridge-aggregate-drift-publication-lockout-001.md` - source advisory (adopt): F1 maps to Changes C/D plus A's strand-prevention; F2 maps to Change B.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md` - the VERIFIED verdict during which advisory-2's findings were discovered live.

## Owner Decisions / Input

- `DELIB-202667531` - owner authorization of the fix-class advisory-correction work set including WI-5758 (advisory triage 2026-07-29). Recorded owner decision; per CLAUDE.md session-start rules, items already authorized by recorded owner decision need no fresh approval to enter the bridge protocol. The decision explicitly does NOT waive the bridge protocol - this proposal is that protocol step.
- `DELIB-202667533` (AskUserQuestion evidence: `AUQ-20260729-ADVISORY-TRIAGE-SYNTHESIS`) - AT-01 design authority: commit-first finalization ratified and pending-then-promote intermediate publication state REJECTED; Change B4 records conformance. AT-04: program PAUTH `PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM` issued with mutation classes `source`, `test_addition`, `governance_evidence`, `bridge` (verified current via `gt projects show-authorization` before filing); its forbidden operations (no dispatcher mutation, no push, no deployment/release, no destructive cleanup) are all honored by this scope.
- `DELIB-202667534` - owner-ratified disposition: both source advisories -> WI-5758 (merged, order 110).
- Advisory owner-grilling gates (per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`): resolved by the recorded triage rather than left dangling. Advisory-1 Q1 (restoration mechanism) -> writer self-observation is primary and the operator command is the secondary escape hatch (WI scope letters a and c). Advisory-1 Q2 (observation without tool-event provenance) -> acceptable, recorded as honest writer/operator observation provenance, never a synthetic tool event (Change C). Advisory-1 Q3 and advisory-2 Q2 (severity/failure posture) -> surfacing lands reporting-first (Change D); the gate's fail-closed posture is unchanged in this thread, and the general per-identity blast-radius posture remains WI-5696 acceptance territory. Advisory-2 Q1 (recovery authority model) -> standing governed command (`gt registry observe`), not per-incident authorization. Advisory-2 Q3 (scope/sequencing) -> one work item, WI-5758, order 110.
- No further owner decision is required to review this proposal; implementation proceeds only on bridge `GO` plus an implementation-start authorization packet (`python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5758-publication-deadlock-closure`).

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` (publication discipline and audit-trail durability), `GOV-PLATFORM-SOT-REGISTRY-001` + `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` (registry authority and the observation/mutation boundary), `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (observed state tracks reality), the AT-01 owner decision (`DELIB-202667533`, ordering and lifecycle constraints), and the WI-5758 scope text fully determine the required behavior; both source advisories supply mechanically re-verified defect evidence. No new or revised requirement is needed before implementation.

## Verification Plan (Spec-Derived Test Mapping)

All tests run against disposable fixture project roots (the existing fixture harnesses in `platform_tests/scripts/test_gtkb_bridge_writer.py` and `groundtruth-kb/tests/test_registry_control_plane.py`); the live repository registry and live `groundtruth.db` are never touched by the test suite.

| # | Test | Derives from |
|---|------|--------------|
| T1 | Sequential-writes currentness (Change A2): three consecutive governed `write_bridge_file` publications in one fixture; after EACH write, `registry_currentness(record_ids={'bridge-versioned-files'})` is current and the next mint succeeds with no manual observation. | GOV-SOURCE-OF-TRUTH-FRESHNESS-001; GOV-FILE-BRIDGE-AUTHORITY-001; advisory-1 recommendation 1 |
| T2 | Retained-file self-observation (Change A1): force a consume failure whose compensation hits a retained-file branch (bytes-changed injection); assert the file is retained, the capability row is `recovery_required` with its failure reason, the aggregate is CURRENT via the appended passive observation (`operation='direct_in_place_content_change'`, `evidence_source_reference=capability_hash`), and a subsequent mint for a different slug succeeds. | GOV-FILE-BRIDGE-AUTHORITY-001; DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001; SPEC-1662 |
| T3 | Crash injection, finalize path (Change B): child venv process mints + exclusively creates the bridge file then hard-exits before consume (`os._exit`); parent process (fresh module state, empty in-memory dict) finds the durable sidecar, runs the recovery finalize path, and asserts: post-image revision appended, capability row `consumed`, currentness current, no stranded half-publication, claim releasable. | GOV-FILE-BRIDGE-AUTHORITY-001; DELIB-202667533 AT-01; advisory-2 F2 |
| T4 | Crash injection, rollback path + expired-row handling (Change B): same kill window; recovery rollback removes the exact file, restores preimage evidence, marks the row terminal; an `expired` row with a byte-matching on-disk file is recovery-eligible; `rollback_pending_bridge_publication` no longer raises `BRIDGE_PUBLICATION_REPAIR_REQUIRED` for this class; byte-mismatched files REFUSE secret-free recovery (fail closed). | GOV-FILE-BRIDGE-AUTHORITY-001; SPEC-1662; advisory-2 F2 |
| T5 | Observe escape hatch, happy path (Change C): stale the fixture aggregate out-of-band (write an extra bridge-shaped file directly), run `gt registry observe --artifact bridge-versioned-files --change-reason ...` via the CLI runner; exit 0, revision appended with operator provenance, currentness restored, mint succeeds afterward. | GOV-PLATFORM-SOT-REGISTRY-001; DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001; SPEC-1830; advisory-1 recommendation 2 |
| T6 | Observe escape hatch, boundaries (Change C): unregistered path errors; missing-file target errors (`cannot record a missing identity transition`); no declaration/identity/lifecycle/membership row changes across the call (registry snapshot digests unchanged except revision rows); `--change-reason` is required. | DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001; DCL-SOT-REGISTRY-PROJECTION-PARITY-001; GOV-10 |
| T7 | Pre-cliff surfacing (Change D): state-report block shows `aggregate_current: true, stale_count: 0` on a current fixture; after out-of-band drift it shows `aggregate_current: false`, a non-zero stale count, and the warning line naming the observe remedy; exit code and queue fields unchanged in both states. | GOV-SOURCE-OF-TRUTH-FRESHNESS-001; SPEC-1830; advisory-1 recommendation 4 |
| T8 | AT-01 / lifecycle conformance (Change B4): `VALID_STATUSES` is byte-identical to pre-change; the pending sidecar never appears in any queue/actionability derivation; recovery paths never rewrite a bridge file's first-line status; no dispatcher/TAFE state is written by any new path. | DELIB-202667533 AT-01; DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001; GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 |

Commands (the implementation report will carry observed output):

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py groundtruth-kb/tests/test_registry_control_plane.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py platform_tests/groundtruth_kb/cli/test_registry_observe_cli.py -q`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check <all eight target files>`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <all eight target files>`

## Acceptance Criteria

1. Three sequential governed publications leave the aggregate current after each write; no manual observation step exists anywhere in the governed path (T1).
2. A publication hard-killed between create and consume is recoverable by a later process in BOTH directions - finalize completes the observation leg, rollback restores the preimage - with no `BRIDGE_PUBLICATION_REPAIR_REQUIRED` dead-end for the crash class and no silently-unobserved on-disk strand (T3, T4).
3. Compensation-failure retained files leave the registry current with the anomaly preserved as `recovery_required` audit evidence (T2).
4. `gt registry observe` restores currentness after out-of-band drift under honest operator provenance, and refuses unregistered targets, missing files, and any identity-class amendment (T5, T6).
5. `gt bridge state-report` surfaces aggregate currentness, stale count, and the remedial command before the cliff, reporting-only (T7).
6. No new bridge status token, no pending-then-promote lifecycle state, no dispatcher/TAFE writes (T8).
7. `ruff check` and `ruff format --check` pass on all changed files.

## Risk and Rollback

- Risk: observing a retained failure file could be misread as laundering drift. Mitigated: the observation records the true on-disk state while the capability row keeps `recovery_required` + failure reason and the revision row carries `evidence_source_reference=capability_hash`; audit evidence is strengthened, never erased (and this is the WI-5696-ratified posture: audit debt, not stoppage).
- Risk: secret-free recovery weakens the capability discipline. Mitigated: recovery authenticates by exact `content_digest` byte match + claim-session match + single-use state transitions, and can only complete or revert the exact minted publication; mismatched bytes fail closed (T4). No new minting authority exists.
- Risk: control-plane lock contention (`DELIB-202667526` lock convoy). Mitigated: every new operation is a short transaction under the EXISTING single lock; no new lock, no long holds, no second capability class.
- Risk: sidecar orphans in `.gtkb-state/bridge-publication-pending/`. Mitigated: the capability table remains the authoritative state machine; sidecars are pointers, deleted on every terminal transition and harmless (recovery re-verifies everything against the row and the bytes).
- Risk: state-report cost. Mitigated: scoped to one glob digest for the single bridge aggregate record; no deep audit (WI-5724's territory).
- Rollback: single-commit revert of the eight target files restores current behavior. The sidecar directory and any new table column additions are additive; no migration of existing rows; no hook re-registration; no configuration change.

Recommended commit type: fix

## Review Questions for Loyal Opposition

1. Change B treats an `expired` capability row with a byte-matching on-disk file as finalize-eligible (the TTL bounds the mint-to-create window, not the recovery window). Is finalize-by-completion acceptable there, or should expired rows be rollback-only?
2. Is the `.gtkb-state` JSON sidecar the right durability substrate for the pending record, or should pending context live exclusively in the capabilities table (SQL-queryable, at the cost of coupling the writer's fast path to a DB read on every finalize/rollback)?
3. Change A1 observes within the same locked scope as the failure disposition but in a separate SQLite transaction from the failed consume. Is same-lock-scope sufficient, or should the observation share the compensation transaction where one exists?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
