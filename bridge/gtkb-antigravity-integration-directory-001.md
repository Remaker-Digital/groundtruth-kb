NEW

# Antigravity Onboarding WI-3346: .antigravity/ Integration Directory + ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3

bridge_kind: implementation_proposal
Document: gtkb-antigravity-integration-directory
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-19 UTC
Implements: WI-3346 (.antigravity/ harness integration directory; Antigravity Onboarding sub-project of PROJECT-ANTIGRAVITY-INTEGRATION)
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3346
target_paths: ["groundtruth.db", ".antigravity/config.toml", ".antigravity/README.md"]
Recommended commit type: feat:

## Summary

This is the first implementation proposal of the Antigravity Onboarding sub-project. It delivers two coupled things, in the order the WI-3345 research spike directed ("the Antigravity hook-parity gap ... should be recorded through the governed path ... decided when WI-3346/WI-3347/WI-3348 are scoped"):

1. The `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3 extension - generalizing the ADR from Codex-specific to harness-general and adding the Antigravity harness's categorical no-hooks fallback regime. The owner selected this disposition ("extend the Codex ADR") via AskUserQuestion on 2026-05-18.
2. The `.antigravity/` integration directory - GT-KB's in-root harness-integration directory for the Antigravity harness (identity C), the harness-C analogue of the existing `.codex/` and `.claude/` integration directories, designed around the spike's finding that Antigravity exposes no hook event surface.

WI-3346 is deliberately scoped to the integration-directory scaffold plus the governing ADR. The LO-role-scoped capability adapters in `.agent/skills/` are WI-3347; the `gt harness register` harness-C record is WI-3348; the end-to-end Gemini CLI headless dispatch verification is WI-3349.

## Specification Links

- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - the ADR this proposal extends to v3; v2 is Codex-specific, v3 generalizes it across harnesses and adds the Antigravity case.
- REQ-HARNESS-REGISTRY-001 - the governing requirement; the Antigravity Onboarding sub-project implements its harness-roster clause, and WI-3346 is the integration-directory step.
- GOV-ARTIFACT-APPROVAL-001 - the ADR v3 extension is a formal-artifact mutation; canonical insertion requires an owner formal-artifact-approval packet, collected at implementation time.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - every GT-KB integration artifact is created in-root under E:\GT-KB; the harness installation's own user-profile config directory is the harness's, not a GT-KB artifact (see In-Root Placement Evidence).
- GOV-FILE-BRIDGE-AUTHORITY-001 - this work proceeds through the file bridge; bridge/INDEX.md remains canonical workflow state.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives verification from the linked specifications.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 - the bridge dispatch automation contract; WI-3346 records (it does not yet wire) that harness C's dispatch uses the interval-driven fallback substrate, not the event-driven trigger.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 - auto-trigger contract; unchanged by this slice - WI-3346 adds no dispatch-path code.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the single-harness bridge dispatcher is the recommended fallback dispatch substrate for a hookless harness; the `.antigravity/config.toml` dispatch-model field records that.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - the dispatcher behavior contract the harness-C fallback consumes; integration is WI-3348/WI-3349, not WI-3346.
- GOV-HARNESS-ROLE-PORTABILITY-001 - the role-portability invariant; the Antigravity harness is onboarded in the loyal-opposition role per DELIB-2079 Q1.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the ADR and the integration directory are durable governed artifacts (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across the Antigravity Onboarding sub-project is preserved (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the ADR progresses to a new version through the governed update path (advisory).

## Prior Deliberations

- DELIB-2079 - the owner-decided Antigravity Integration design (3-harness model; Q1 places Antigravity at identity C in the loyal-opposition role).
- DELIB-2080 - the role-portability amendment; records the Gemini CLI headless invocation form.
- DELIB-2081 - the Antigravity project authorization amendment under which this work is authorized.
- DOC-ANTIGRAVITY-IDE-RESEARCH-001 - the WI-3345 research spike findings (RQ1: no hook config file; RQ2: a SKILL.md skill system; RQ3: no lifecycle hook events). Its section 7 "Consequences for WI-3346-3349" is the direct design input: WI-3346 must design the Antigravity integration around rules and skills, not hooks.
- bridge/gtkb-antigravity-ide-research-spike-003.md - the WI-3345 post-implementation report; its "Surfaced Governed-Decision Obligation" section flagged the hook-parity ADR for owner disposition - this proposal acts on that.
- DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08 - the empirical retest behind ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2; v3 carries v2's Codex content forward unchanged.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 (v2) - the current ADR; v3 is additive (generalizes, adds Antigravity) and retracts nothing from v2.

## Owner Decisions / Input

The Antigravity Integration project was owner-decided in the 2026-05-16 eleven-question AskUserQuestion clarification interview (DELIB-2079) and amended by DELIB-2080; the active authorization is PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION (owner decision DELIB-2081; scope includes REQ-HARNESS-REGISTRY-001). On 2026-05-18 the owner directed, via AskUserQuestion, that the Antigravity onboarding be carried out ("proceed with all work and configure GT-KB to use Gemini/Antigravity as Loyal Opposition"). On 2026-05-18 the owner answered a further AskUserQuestion on the hook-parity ADR disposition: "Extend the Codex ADR" - i.e. generalize ADR-CODEX-HOOK-PARITY-FALLBACK-001 to a new version covering the Antigravity harness, rather than create a separate ADR. This proposal implements WI-3346 within that authorized scope and per that disposition.

One owner input remains pending and is NOT requested by this proposal: the ADR v3 content itself is a formal artifact; its canonical insertion requires an owner formal-artifact-approval packet, which Prime Builder will collect via AskUserQuestion at implementation time, after Loyal Opposition GO. This proposal presents the proposed v3 content (below) for review; it does not write it.

## Requirement Sufficiency

Existing requirements sufficient. REQ-HARNESS-REGISTRY-001 plus DELIB-2079/2080 govern the Antigravity onboarding; the WI-3345 spike closed the implementation unknowns. The ADR v3 extension records an architecture decision derived from the spike findings and the owner's disposition; it asserts no new requirement. The `.antigravity/` integration directory is scaffolding within the existing harness-registry contract. No new or revised GOV/SPEC/REQ artifact is required before implementing WI-3346.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal updates one existing ADR spec to a new version and creates two new files. It does not resolve, retire, promote, or batch-mutate work items; it produces no work-item inventory. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS is not applicable. The single work item cited (WI-3346) is this proposal's own implementing work item under the mandatory project-linkage metadata. The ADR v3 mutation is a single formal-artifact update gated by its own GOV-ARTIFACT-APPROVAL-001 packet, not a bulk operation.

## In-Root Placement Evidence

Per ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT, every GT-KB artifact this proposal creates or mutates is within the E:\GT-KB project root:

- `E:\GT-KB\groundtruth.db` - the MemBase database (the ADR v3 spec row), in-root.
- `E:\GT-KB\.antigravity\config.toml` - new GT-KB integration-config file, in-root.
- `E:\GT-KB\.antigravity\README.md` - new documentation file, in-root.

The Antigravity harness installation maintains its own user-config directory under the operating-system user profile, observed read-only by the WI-3345 spike. That directory belongs to the harness installation and is outside the project root; it is NOT a GT-KB artifact and is neither created, mutated, nor required as a live dependency by this work. GT-KB's integration directory is the in-root `E:\GT-KB\.antigravity\`, exactly as `.codex\` and `.claude\` are in-root GT-KB integration directories distinct from any harness user-config. No `applications/` paths. No paths outside E:\GT-KB.

## Scope

### Deliverable 1 - ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3

The ADR is updated from v2 to v3 via the governed spec-update path (an append-only new spec version with `changed_by`, `changed_at`, and a `change_reason` citing this bridge thread, gated by a GOV-ARTIFACT-APPROVAL-001 formal-artifact-approval packet). v3 is additive: it carries v2's Codex content forward verbatim and adds the harness-general framing plus the Antigravity case. The proposed v3 content:

> This ADR governs the hook-parity fallback obligation for AI coding harnesses in the GT-KB cross-harness bridge. It is named for its origin (the Codex hook-parity question); as of v3 its scope is harness-general.
>
> v3 scope change: v1/v2 addressed only the Codex harness. v3 generalizes the ADR to all harnesses and adds the Antigravity harness, whose hook situation is categorically different from Codex's.
>
> Codex (harness A). [v2 content, carried forward unchanged.] `.codex/hooks.json` IS a live Codex interception boundary on Windows for Codex CLI versions >= 0.128.0-alpha.1, where the codex_hooks feature flag is stable, true. The fallback obligation persists for (1) older Codex CLI versions where the feature is not stable and (2) any future regression that re-disables it; in either case sessions verify via `codex features list` or empirical retest and use mechanical fallback when verification fails. Regression test: a test in tests/scripts/test_codex_hook_parity.py asserts a fixture Stop hook fires.
>
> Antigravity (harness C). Per the WI-3345 research spike (DOC-ANTIGRAVITY-IDE-RESEARCH-001, determined-with-evidence), the Antigravity IDE exposes NO hook event surface: no SessionStart, PostToolUse, or Stop event, and no hook-registration configuration file. This is not version-gated and is not a regression - it is the categorical current state of the Antigravity harness. An Antigravity harness therefore CANNOT host the cross-harness event-driven trigger, which depends on PostToolUse and Stop hooks. For harness C the standing dispatch substrate is the interval-driven single-harness bridge dispatcher / host-scheduled-task model (per ADR-SINGLE-HARNESS-OPERATING-MODE-001 and SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001), invoking the Antigravity headless surface `gemini -p "<prompt>" --yolo`. For harness C this fallback is the permanent, correct dispatch model given Antigravity's architecture - not a degraded mode. If a future Antigravity release adds a hook surface, a v4 re-evaluates.
>
> Decision. Hook availability is a per-harness property. A harness with a live hook surface uses the event-driven cross-harness trigger; a harness with no hook surface uses the interval-driven dispatcher substrate as its standing dispatch model. GT-KB bridge automation must select the dispatch substrate per the active harness's hook capability and must never assume event-driven hooks are universally available.
>
> Rationale. v1 was the cautious-defaults position when Codex hooks were disabled; v2 documented the post-restoration Codex state; v3 generalizes - hook availability varies by harness, and the bridge's dispatch substrate is chosen accordingly. The Antigravity harness makes the interval-driven fallback a first-class permanent path.

The ADR's machine-checkable surface (`assertions` / `affected_by` / `source_paths`) is extended only as needed to reference the Antigravity case; no assertion is removed. The exact field-level delta is presented with the formal-artifact-approval packet at implementation time.

### Deliverable 2 - the `.antigravity/` integration directory

`.antigravity/` is created in-root as GT-KB's harness-integration directory for the Antigravity harness, the harness-C analogue of `.codex/` and `.claude/`. WI-3346 creates two files; it deliberately does NOT create a `hooks.json` (Antigravity has no hook surface - its absence is the design, documented in the README).

`.antigravity/config.toml` - the GT-KB integration config for the Antigravity harness. It records, as static configuration data:
- harness identity `C` and operating role `loyal-opposition` (per DELIB-2079 Q1);
- the invocation surfaces: the Antigravity IDE interactive surface, and the headless surface `gemini -p "<prompt>" --yolo`;
- the dispatch model: `interval_driven_single_harness_dispatcher` - an explicit field recording that harness C uses the fallback substrate, not the event-driven trigger, because Antigravity exposes no hook events (ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3);
- the rule and skill surface locations the later slices populate (`.agent/rules/`, `.agent/skills/`) - recorded for reference; WI-3346 does not create them.
`config.toml` is declarative configuration data only - no code, no executable hook.

`.antigravity/README.md` - documents the integration model for any future session: that the Antigravity harness has no hook event surface (citing DOC-ANTIGRAVITY-IDE-RESEARCH-001), why there is therefore no `hooks.json`, that harness-C bridge dispatch uses the interval-driven fallback substrate, the in-root vs harness-user-config boundary (the in-root `.antigravity/` directory under the project root is the GT-KB integration directory; the harness installation's own user-profile config directory is not a GT-KB artifact), and that WI-3347/WI-3348/WI-3349 complete the onboarding.

Not in WI-3346: the `.agent/skills/` capability adapters (WI-3347); the `gt harness register` harness-C record (WI-3348); end-to-end Gemini CLI headless dispatch verification (WI-3349); any change to dispatch-path code. Live dispatch behavior is unchanged by this slice.

## Files Expected To Change

- `groundtruth.db` - one append-only new spec version: ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3. Gated by a GOV-ARTIFACT-APPROVAL-001 formal-artifact-approval packet collected at implementation time.
- `.antigravity/config.toml` - NEW. The GT-KB integration config described above.
- `.antigravity/README.md` - NEW. The integration-model documentation described above.

No source, test, hook, or dispatch-path file is modified.

## Spec-To-Test Mapping

WI-3346 creates configuration and documentation artifacts plus a governed ADR version; per the file-bridge protocol a test may be a logical assertion (an artifact exists / has the required content / a field equals an expected value).

| Spec / governing surface | Verification | 
| --- | --- |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3 (the extension is recorded) | A MemBase read of ADR-CODEX-HOOK-PARITY-FALLBACK-001 returns version 3, status carried from v2, content containing both the Codex case (carried forward) and the Antigravity no-hooks case. The post-impl report records the before/after version and the formal-artifact-approval packet path. |
| GOV-ARTIFACT-APPROVAL-001 (formal-artifact approval) | The post-impl report cites the formal-artifact-approval packet at .groundtruth/formal-artifact-approvals/<date>-ADR-CODEX-HOOK-PARITY-FALLBACK-001.json, with presented_to_user=true and a matching content hash. |
| DELIB-2079 Q1 / REQ-HARNESS-REGISTRY-001 (harness C = loyal-opposition) | `.antigravity/config.toml` records harness identity C and role loyal-opposition; a parse of the TOML confirms the fields. |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3 / DOC-ANTIGRAVITY-IDE-RESEARCH-001 (no-hooks design) | `.antigravity/` contains no hooks.json; `.antigravity/config.toml` dispatch-model field equals interval_driven_single_harness_dispatcher; `.antigravity/README.md` documents the no-hooks rationale. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All created files are under E:\GT-KB; path inspection confirms no path outside the root and no applications/ path. |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 / DCL-SMART-POLLER-AUTO-TRIGGER-001 | WI-3346 adds no dispatch-path code; verification is by inspection that cross_harness_bridge_trigger.py and single_harness_bridge_dispatcher.py are absent from target_paths and unmodified. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed verification commands and observed results. |

Verification commands for the post-implementation report: a MemBase read-back of ADR-CODEX-HOOK-PARITY-FALLBACK-001 (version + content); a TOML parse of `.antigravity/config.toml`; a content check of `.antigravity/README.md`; plus `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-antigravity-integration-directory` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-antigravity-integration-directory`.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] ADR-CODEX-HOOK-PARITY-FALLBACK-001 is updated to v3, carrying v2's Codex content forward unchanged and adding the harness-general framing and the Antigravity no-hooks case, under a GOV-ARTIFACT-APPROVAL-001 formal-artifact-approval packet with owner approval.
- [ ] `.antigravity/config.toml` exists in-root and records harness identity C, role loyal-opposition, the IDE + headless invocation surfaces, and the interval-driven dispatch model.
- [ ] `.antigravity/README.md` exists in-root and documents the no-hooks integration model, the fallback dispatch substrate, and the in-root vs harness-user-config boundary.
- [ ] No `.antigravity/hooks.json` is created; its absence is deliberate and documented.
- [ ] No dispatch-path code is modified; live dispatch behavior is unchanged.
- [ ] Loyal Opposition returns VERIFIED before WI-3346 is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this `-001` draft via `--content-file` before the live INDEX entry is inserted, and re-run against the indexed operative file after filing. Expected: applicability `preflight_passed: true`, `missing_required_specs: []`; clause preflight exit 0 with no blocking gaps. Any non-empty missing-specs list is a self-detected defect to be corrected before INDEX update.

## Risk And Rollback

- R1 (low): bundling the ADR v3 extension with the integration-directory scaffold widens the proposal. Mitigation: the WI-3345 spike explicitly directed that the ADR be "decided when WI-3346 ... is scoped"; the two are coupled by design - the directory's no-hooks shape is the concrete consequence the ADR governs. If Loyal Opposition judges they should be split, NO-GO with that direction and Prime will re-file the ADR as a separate thread.
- R2 (low): the proposed ADR v3 text is refined during owner formal-artifact approval. Mitigation: this proposal presents the v3 content for review but does not write it; the owner-approved packet content is authoritative at implementation time, and any wording change is captured there.
- R3 (low): `.antigravity/config.toml` schema diverges from a future `gt harness` expectation. Mitigation: WI-3346's config.toml is declarative and minimal; WI-3348 (`gt harness register`) is the authority for the harness record and may extend the config; WI-3346 records only what the spike determined.
- R4 (very low): a reader assumes the absent hooks.json is an omission. Mitigation: `.antigravity/README.md` documents the deliberate no-hooks design and cites DOC-ANTIGRAVITY-IDE-RESEARCH-001.

Rollback: the ADR spec is append-only-versioned - a corrective new version supersedes v3 if needed. The two new files are deletable with no residue; no existing file is modified.

## Loyal Opposition Asks

1. Confirm the bundling of the ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3 extension with the `.antigravity/` integration-directory scaffold in one WI-3346 thread is the correct disposition (per the WI-3345 spike's "decided when WI-3346 is scoped" direction), or NO-GO with direction to split the ADR into a separate thread.
2. Confirm the proposed ADR v3 content correctly carries v2's Codex case forward unchanged and correctly characterizes the Antigravity harness's no-hooks state as categorical (not version-gated), with the interval-driven dispatcher as the standing fallback substrate.
3. Confirm the `.antigravity/` directory design - config.toml + README, no hooks.json - is the right WI-3346 scope, with `.agent/skills/` adapters correctly deferred to WI-3347 and the `gt harness` record to WI-3348.
4. Confirm the in-root placement boundary (GT-KB integration in the in-root `.antigravity/` directory under the project root; the harness installation's own user-profile config directory out of scope) is correctly drawn.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
