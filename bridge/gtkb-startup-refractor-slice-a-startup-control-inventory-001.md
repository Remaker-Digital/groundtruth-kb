NEW

# GTKB-STARTUP-REFRACTOR-001 Slice A — Startup-Control Inventory + Role-Capability Manifest

bridge_kind: implementation_proposal
Document: gtkb-startup-refractor-slice-a-startup-control-inventory
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC

author_identity: Claude Code Prime Builder (interactive, session-stated PB)
author_harness_id: B
author_session_context_id: 2026-06-03-gtkb-startup-refractor-slice-a
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style, interactive session-stated PB (::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-GTKB-STARTUP-REFRACTOR-001-SLICES-A-E-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-STARTUP-REFRACTOR-001
Work Item: WI-4268

target_paths: ["config/agent-control/SESSION-STARTUP-CONTROL-MAP.md", "config/agent-control/ROLE-CAPABILITY-MANIFEST.md", "platform_tests/scripts/test_session_startup_control_map.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice A of the GTKB-STARTUP-REFRACTOR-001 umbrella (scoping GO at `bridge/gtkb-startup-refractor-scoping-002.md`). It is the low-risk, additive-documentation slice that covers advisory findings **F2** (no single startup-control inventory; `config/agent-control/CONTROL-MAP.md` and `REVIEW-MODE-SETUP.md` are stale relative to the live startup set), **F8** (skills/commands/agents installed but no role-capability manifest), and the **F9 classification** half (retired/legacy startup surfaces are discoverable but unclassified).

It creates two new in-root documentation artifacts plus one structural test:

1. `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md` — a single role-neutral source-of-truth inventory of startup control surfaces: required startup files, role overlays, the generated startup service, live settings files, skills/commands/agents, plugin/MCP assumptions, and known local-only surfaces; each entry tagged with a lifecycle classification (`active` / `deprecated` / `archive` / `generated`).
2. `config/agent-control/ROLE-CAPABILITY-MANIFEST.md` — a manifest of installed capabilities grouped as Prime Builder / Loyal Opposition / shared / owner-gated, covering skills, agents, commands, and plugin/MCP assumptions, with a verification command per capability where one exists.
3. `platform_tests/scripts/test_session_startup_control_map.py` — a structural test asserting the control-map enumerates the canonical required startup files and that the manifest carries the four role sections.

Slice A is **classify-only**: it does not delete or relocate any surface (advisory F9 *deletion* remains a separately owner-gated follow-on), does not edit protected narrative (that is Slice C), and does not touch machine-local settings (that is Slice B). No MemBase mutation is in scope.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` — governs the fresh-session self-initialization/startup-disclosure experience; the control-map is the inventory of the surfaces that experience loads. PAUTH-linked spec.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — startup token-budget constraint; a single authoritative inventory is the precondition for the later de-duplication slices that reduce startup token load. PAUTH-linked spec.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the bridge protocol used to file this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal's spec-linkage compliance.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item + Project Authorization linkage (cited in metadata above).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-to-test mapping below derives the structural test from the linked specs.
- `GOV-STANDING-BACKLOG-001` — WI-4268 backlog linkage and single-WI visibility.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking. All three target paths are in-root under `E:\GT-KB`; no out-of-root mutation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory. The inventory + manifest are durable governed artifacts, not transient notes.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory. The control-map's per-surface classification uses lifecycle states (active/deprecated/archive/generated).

## Prior Deliberations

- `DELIB-2743` — bridge thread `gtkb-startup-refractor-glossary-load-surface` (6 versions, VERIFIED): the F1 glossary-load slice. Slice A builds on it (the glossary loader is one inventoried surface) and does not re-do it.
- `DELIB-20260622` — owner decision (2026-06-03 AUQ) authorizing the project PAUTH that covers this slice's implementation.
- `DELIB-2078` — owner approval for the init-keyword startup-disclosure relay specification; the control-map inventories the disclosure-relay surfaces so the relay contract stays visible.
- `DELIB-1081` — Startup First-Response Directive Repair; historical context for the generated startup service that the inventory must enumerate.
- Scoping authority: `bridge/gtkb-startup-refractor-scoping-002.md` (Loyal Opposition GO on the umbrella decomposition that defined Slice A).

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § "Mandatory Owner Decisions / Input Section Gate". This proposal's implementation authority comes from owner approval, cited here:

1. **Owner AskUserQuestion (2026-06-03)** — "Create a project PAUTH (A–E)" — archived as `DELIB-20260622` (`source_type=owner_conversation`, `outcome=owner_decision`). It minted `PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-...-SLICES-A-E-IMPLEMENTATION-AUTHORIZATION` (active), which includes WI-4268 and links `GOV-SESSION-SELF-INITIALIZATION-001` + `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`.
2. **Owner AskUserQuestion (2026-06-03)** — "Scoping proposal first" then "Record the five sub-WIs and start Slice A" — authorized decomposition and this slice's filing.
3. **Scoping GO** — `bridge/gtkb-startup-refractor-scoping-002.md` (Loyal Opposition GO) authorized per-slice proposals.

No further owner decision is required to implement Slice A: it is additive documentation + one test, fully within the PAUTH's allowed mutation classes (`documentation`, `test`) and within `target_paths`. The PAUTH forbids stale-surface deletion (F9), which this slice honors (classify-only).

## Requirement Sufficiency

**Existing requirements sufficient.**

The governing requirements are advisory findings F2/F8/F9-classify (acceptance criteria 3, 6, 7 of the `STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02` backlog definition) together with `GOV-SESSION-SELF-INITIALIZATION-001`. Slice A is additive inventory/manifest documentation that records existing state; it creates no new behavior contract and therefore needs no new or revised specification.

## Spec-Derived Verification Plan

Each linked specification maps to the structural test or check below. Reproducible evidence uses the repo venv interpreter.

| Specification / Finding | Spec-to-test mapping | Command | Expected |
|---|---|---|---|
| `GOV-SESSION-SELF-INITIALIZATION-001` / F2 | `test_session_startup_control_map.py` asserts the control-map enumerates the canonical required startup files (CLAUDE.md, AGENTS.md, `.claude/rules/canonical-terminology.md`, `.claude/rules/operating-role.md`, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/deliberation-protocol.md`, and the generated startup service) | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_startup_control_map.py -q --no-header -p no:cacheprovider` | PASS |
| F8 (role-capability manifest) | same test asserts `ROLE-CAPABILITY-MANIFEST.md` carries the four role sections (Prime Builder / Loyal Opposition / shared / owner-gated) | (same pytest command) | PASS |
| F9-classify | same test asserts every control-map surface row carries one of the four lifecycle classifications (`active`/`deprecated`/`archive`/`generated`) | (same pytest command) | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the spec-to-test mapping above is the derivation; the test is the executed evidence | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_session_startup_control_map.py` and `ruff format --check` (same path) | All checks passed; formatted |

The implementation report will carry the observed results of these commands.

## Risk / Rollback

Risk surface is minimal: two new documentation artifacts and one new test, no runtime/behavior change, no protected-narrative edit, no settings change, no MemBase mutation. The main risk is the inventory being incomplete or drifting from the live set; the structural test mitigates drift for the canonical required files. Rollback is a single-commit revert of the three added files.

## Bridge Filing (INDEX-Canonical)

Filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-startup-refractor-slice-a-startup-control-inventory` document list in `bridge/INDEX.md` via the serialized `gt bridge index` writer; append-only. `bridge/INDEX.md` remains canonical per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs` — the substantive deliverables are two documentation artifacts (control-map + role-capability manifest); the accompanying `test_session_startup_control_map.py` is a structural guard for those docs, not a new code capability. No `feat`/`fix` behavior change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
