NEW
author_identity: claude
author_harness_id: B
author_session_context_id: init-gtkb-pb-2026-06-18-ar-readiness-phase-1-0
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive Prime Builder session

# GT-KB Implementation Proposal — Agent Red Readiness Phase 1.0: Isolation Status Reconciliation

Document: gtkb-ar-readiness-phase-1-0-status-reconciliation
Version: 001
Date: 2026-06-18
Author: Prime Builder (Claude Code, harness B)
Bridge thread: gtkb-ar-readiness-phase-1-0-status-reconciliation

Project Authorization: PAUTH-PROJECT-GTKB-AGENT-RED-READINESS-AGENT-RED-READINESS-PROGRAM-PHASE-1-ISOLATION-PARTITION-IN-PLACE
Project: PROJECT-GTKB-AGENT-RED-READINESS
Work Item: WI-4653

target_paths: ["applications/Agent_Red/.gtkb-app-isolation.json", "platform_tests/scripts/test_ar_isolation_status_reconciliation.py", "groundtruth.db"]

## Summary

Slice 1.0 (keystone-opening hygiene) of the Agent Red Readiness Program Phase 1. Two state-reconciliation corrections, no new capability and no write-gating change:

1. Correct the false "minimal placeholder" claim on the `.claude` entry in `applications/Agent_Red/.gtkb-app-isolation.json`. The directory is in fact a substantive 15-file / ~782-line Agent-Red-scoped Claude Code configuration; the registry justification asserts the opposite.
2. Reconcile the prematurely-VERIFIED `PROJECT-GTKB-ISOLATION-PROGRAM-CLOSEOUT`: record durably that the GTKB-ISOLATION-019 closeout overclaimed completion (sub-slices 5 and 6 were never built) and cross-link the remaining isolation-enforcement work to PROJECT-GTKB-AGENT-RED-READINESS Phase 1 (WI-4654…WI-4657).

A spec-derived regression test asserts both corrections.

## Problem / Context

The Phase-0 readiness census (DELIB-20265219) established that the isolation guarantee is unenforced and that two durable records misrepresent reality:

- **False placeholder claim.** `applications/Agent_Red/.gtkb-app-isolation.json` describes the `.claude` directory as a "minimal placeholder per Codex GO sub-slice 1 condition 2 (no GT-KB platform content imported)". Live read (2026-06-18): `applications/Agent_Red/.claude/` contains **15 files / ~782 lines** — 2 agents (`code-reviewer`, `security-analyzer`), 5 commands (`check-db`, `check-security`, `preflight`, `quick-review`, `refresh-creds`), `settings.json`, and 3 full skills (`deploy`, `run-tests`, `seed-tenant`) with reference docs. That is a substantive Agent-Red-scoped Claude configuration, not a placeholder. (The WI-4653 acceptance summary cites the census-time figure of 567 lines; this proposal uses the freshly-measured 782, per GOV-SOURCE-OF-TRUTH-FRESHNESS-001.) The `.codex` entry, by contrast, is genuinely minimal (9 lines: `config.toml` + `hooks.json`) — so the correction is correctly scoped to `.claude` only.
- **Premature closeout.** The `gtkb-isolation-019-program-closeout` bridge thread reached VERIFIED at version -008 (DELIB-20261916), formally closing the isolation program. But sub-slice 5 (app-root minimization validator) was never built and sub-slice 6 (writing `ADR-APPLICATION-ISOLATION-CONTRACT-001` + `DCL-APP-ROOT-MINIMIZATION-001` into MemBase) never ran — confirmed by the census and by the still-live `validator_contract.implementation_status: "pending sub-slice 5"` in the registry JSON. The closeout therefore asserts completion that did not occur.

Slice 1.0 does not build isolation enforcement (that is WI-4654…WI-4657). It makes the state claims honest so the keystone slices start from accurate ground (GOV-06 specify-on-contact / GOV-SOURCE-OF-TRUTH-FRESHNESS-001). Blast radius: low (text/record corrections; no code path, no write-gating).

## Specification Links

- **GOV-SOURCE-OF-TRUTH-FRESHNESS-001** — state claims must derive from fresh canonical reads. The "minimal placeholder" justification and the VERIFIED closeout are stale/inaccurate state claims; this slice restores them to match fresh reality. Primary governing spec.
- **GOV-AGENT-RED-GTKB-CONFORMANCE-001** — Agent Red is a conformant adopter supported by GT-KB; its isolation-contract registry (`.gtkb-app-isolation.json`) must accurately describe the application root.
- **GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001** — Agent Red lives at `applications/Agent_Red/`; the registry governing that root must be accurate. The edit stays in-root (`applications/Agent_Red/.gtkb-app-isolation.json`), satisfying `.claude/rules/project-root-boundary.md`.
- **GOV-STANDING-BACKLOG-001** — WI-4653 is the governed work authority for this slice.
- **`.claude/rules/file-bridge-protocol.md`** — bridge protocol authority observed (propose → GO → implement → report → VERIFIED).
- The `.gtkb-app-isolation.json` `validator_contract` rule "Registry entries with bucket=B require non-empty `tool` and `justification`" — the rewrite preserves a non-empty `justification`, so the (currently-unbuilt, sub-slice-5) validator contract is not weakened.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — application placement under `applications/`. The slice edits the application-root isolation registry and reconciles the isolation program; the `.gtkb-app-isolation.json` edit and the new test both stay in-root, satisfying the in-root placement clause (CLAUSE-IN-ROOT).
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — this proposal cites every relevant governing specification (this section); satisfied by concrete links (no TBD/placeholder).
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — VERIFIED requires spec-derived test coverage; satisfied by the §Spec-Derived Verification Plan spec-to-test mapping and the executed pytest/ruff commands.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — file-bridge authority; the numbered versioned bridge file chain is canonical. Observed: this proposal is filed through the governed no-index bridge writer.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — the slice reconciles durable artifacts (the MemBase project record and the isolation registry) rather than leaving the drift in chat/context.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — same artifact-oriented family; reconciliation produces durable corrected records.
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — correcting a prematurely-closed program record is an artifact-lifecycle state correction.

## Prior Deliberations

- **DELIB-20265219** (Owner ratification: Agent Red readiness program) — Phase-0 census established both findings (premature closeout; false `.claude` placeholder). Program ratification + authority artifact.
- **DELIB-20265220** (Phase 1 scoping; slice plan + D-P1a) — defines Slice 1.0 as the no-dependency, low-blast-radius opener: "reconcile premature PROJECT-GTKB-ISOLATION-PROGRAM-CLOSEOUT; correct `.gtkb-app-isolation.json` false 'minimal placeholder' `.claude` claim."
- **DELIB-20261916** (Bridge thread: gtkb-isolation-019-program-closeout, 8 versions, VERIFIED) — the closeout record being reconciled (overclaimed completion).
- **DELIB-20264272** (ISOLATION-018 cutover VERIFIED) — prior isolation-program milestone referenced by the ratification's prior-deliberation chain.
- **DELIB-1402** (AR specs may now apply to GT-KB) — relevant to the partition reclassification in the downstream Slice 1.4, cited here for continuity.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20264326` — seed=search; bridge_thread; Loyal Opposition Verification - GT-KB Mass Adoption Readiness Phase A
- DA: `DELIB-20264624` — seed=search; bridge_thread; VERIFIED: GroundTruth-KB Production Readiness Phase 1 Verification
- DA: `DELIB-20264691` — seed=search; bridge_thread; VERIFIED: gtkb-release-readiness Closeout Acknowledgement
- DA: `DELIB-20264328` — seed=search; bridge_thread; Loyal Opposition Verification - Mass-Adoption Readiness Status Report
- DA: `DELIB-1207` — seed=search; bridge_thread; Bridge thread: gtkb-mass-adoption-readiness (12 versions, ORPHAN)

## Owner Decisions / Input

- **DELIB-20265219** — owner approved the program structure via AskUserQuestion ("Approve both as shown"): D1 program shape, D2 evidence-first census, D3 partition-in-place, D4 isolation-first-then-parallel. Authorizes the program structure and the bridge-protocol pathway (not unreviewed implementation).
- **DELIB-20265220** — owner approved via AskUserQuestion ("Persist Phase 1 scoping, then pause"): the Phase 1 slice plan and the D-P1a write block-list policy. Slice 1.0 carries no open owner decision (D-P1b gates Slice 1.1; D-P1c gates Slice 1.4).
- **2026-06-18, this session** — owner directive via AskUserQuestion (session-focus answer): "Continue the Agent Red Readiness Program — execute Phase 1 through to VERIFIED… WI-4653 Slice 1.0 — isolation status reconciliation (start here; low risk)." Authorizes filing this NEW proposal and running the slice through the bridge protocol.
- **No new owner decision is required for Slice 1.0.** The reconciliation mechanism (registry-JSON edit + append-only MemBase project-record note + spec-derived test) is an implementation-design choice within Prime Builder authority, subject to this Codex review.

## Requirement Sufficiency

Existing requirements sufficient. The governing specifications (GOV-SOURCE-OF-TRUTH-FRESHNESS-001, GOV-AGENT-RED-GTKB-CONFORMANCE-001, GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001, GOV-STANDING-BACKLOG-001) plus the owner decisions DELIB-20265219 / DELIB-20265220 fully constrain this slice. No new or revised requirement is required before implementation; no formal GOV/ADR/DCL/SPEC artifact is created or mutated by Slice 1.0 (those land in Slice 1.1 via formal-artifact-approval packets).

## Proposed Changes

### Change 1 — Correct the `.claude` justification (`applications/Agent_Red/.gtkb-app-isolation.json`)

Replace the `.claude` `top_level_artifacts` entry `justification`:

- **From:** "CWD-rooted rule/agent/skill/hook/plugin discovery for Agent-Red-scoped Claude Code sessions; minimal placeholder per Codex GO sub-slice 1 condition 2 (no GT-KB platform content imported)"
- **To (accurate):** a justification stating that the directory holds a substantive Agent-Red-scoped Claude Code configuration — CWD-rooted rule/agent/skill/command/hook discovery comprising 15 files / ~782 lines (agents `code-reviewer`, `security-analyzer`; commands `check-db`, `check-security`, `preflight`, `quick-review`, `refresh-creds`; `settings.json`; skills `deploy`, `run-tests`, `seed-tenant` with references) — and preserving the still-true and isolation-relevant invariant that NO GT-KB platform content is imported (the configuration is Agent-Red-scoped). Remove the inaccurate "minimal placeholder" characterization.

`.codex` (9 lines) is left unchanged — it is genuinely minimal; correcting it is out of scope per the WI/census. The bucket=B `justification` non-emptiness validator rule is preserved. The edit is a JSON-text correction only; `schema_version`, structure, and all other entries are unchanged. `last_updated` is refreshed to 2026-06-18.

### Change 2 — Reconcile the premature closeout (MemBase)

Append a new project-record version to `PROJECT-GTKB-ISOLATION-PROGRAM-CLOSEOUT` (via `gt projects update`) recording that the GTKB-ISOLATION-019 closeout (DELIB-20261916; bridge thread VERIFIED at -008) overclaimed completion: sub-slice 5 (app-root validator) and sub-slice 6 (ADR/DCL into MemBase) were never built, and the remaining isolation-enforcement work is now carried by PROJECT-GTKB-AGENT-RED-READINESS Phase 1 — WI-4654 (sub-slice 6 ADR/DCL), WI-4655 (sub-slice 5 validator), WI-4656 (write-guard activation), WI-4657 (partition-in-place). The update is append-only (prior version retained); `changed_by=prime-builder-claude-harness-b`, `change_reason` cites WI-4653 + DELIB-20265219/20265220. No project status flip is proposed (the project remains `active`); the reconciliation is a durable continuation note plus cross-link. A `gt projects link-bridge` cross-link from PROJECT-GTKB-ISOLATION-PROGRAM-CLOSEOUT to this bridge thread is included.

### Change 3 — Spec-derived regression test (`platform_tests/scripts/test_ar_isolation_status_reconciliation.py`)

New pytest module asserting both corrections (see verification plan).

## Spec-Derived Verification Plan

| Linked spec | Test assertion (in `test_ar_isolation_status_reconciliation.py`) |
|---|---|
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 | `.claude` entry `justification` does NOT contain "minimal placeholder"; contains an accurate content descriptor (e.g., references the skills/agents); `.gtkb-app-isolation.json` parses and the `.claude` entry is still present (type=DIR, bucket=B). |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 | `PROJECT-GTKB-ISOLATION-PROGRAM-CLOSEOUT` latest version carries the reconciliation note text (records sub-slices 5/6 unbuilt) and references PROJECT-GTKB-AGENT-RED-READINESS (queried via the Python API / projects reader). |
| GOV-AGENT-RED-GTKB-CONFORMANCE-001, GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 | `.gtkb-app-isolation.json` is valid JSON; `schema_version` present; every bucket=B `top_level_artifacts` entry retains non-empty `tool` and `justification` (validator-contract rule preserved); `application == "Agent_Red"`. |

Commands:
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_ar_isolation_status_reconciliation.py -q`
- `groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/scripts/test_ar_isolation_status_reconciliation.py`
- `groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/scripts/test_ar_isolation_status_reconciliation.py`

## Acceptance Criteria (from WI-4653)

1. CLOSEOUT status reflects actual unbuilt sub-slice 5/6 state — reconciliation note recorded in `PROJECT-GTKB-ISOLATION-PROGRAM-CLOSEOUT`, cross-linked to the readiness program.
2. `.claude` justification matches the real content — no "minimal placeholder"; accurate descriptor; freshly-measured size cited.
3. `.gtkb-app-isolation.json` remains schema-valid; bucket=B non-emptiness validator rule preserved; `.codex` unchanged.
4. New spec-derived test passes; `ruff check` and `ruff format --check` clean.

## Risk and Rollback

- **Risk: LOW.** Change 1 is a JSON-text correction (no behavior path; validator non-emptiness preserved). Change 2 is an append-only MemBase update (prior version retained). Change 3 is additive test coverage. No write-gating, hook, or code-path behavior changes.
- **Rollback.** Revert the `.gtkb-app-isolation.json` edit and the test via git; supersede the project-record note with a corrective append-only version if its wording needs adjustment (append-only history means no destructive rollback is required).
- **Boundary.** All target paths are in-root under `E:\GT-KB`; the JSON edit stays within `applications/Agent_Red/`. No out-of-root dependency.

## Recommended Commit Type

`chore:` — governance/state hygiene (reconciling an inaccurate registry justification and a prematurely-closed program record, plus the verifying test). No new capability and no behavior change; WI origin is `hygiene`. (`fix:` is a defensible alternative since it corrects an inaccurate record; `chore:` is recommended as the dominant character.)
