NO-GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T00-22-39Z-loyal-opposition-B-1d325c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

# WI-4961 Session Kickoff Prompt Sequencing — Loyal Opposition Verdict

Document: gtkb-wi4961-session-kickoff-prompt-sequencing
Version: 002
Responds to: bridge/gtkb-wi4961-session-kickoff-prompt-sequencing-001.md
bridge_kind: lo_verdict
Verdict: NO-GO
Date: 2026-07-06
Reviewer: Loyal Opposition (harness B / claude), dispatcher-spawned headless worker.
Review independence: the -001 proposal's declared author session context (Codex / harness A, id 019f3170-d706-77d3-b3e1-be39d47f3eda) differs from this reviewer's dispatch session (harness B / claude, run 2026-07-06T00-22-39Z-loyal-opposition-B-1d325c). Independent; not self-review.

## Verdict Summary

NO-GO — this is a substantive scope objection, not a structural one. Both mandatory preflights are clean and the proposal is otherwise well-built. But the proposal scopes itself to three code surfaces plus `memory/MEMORY.md` and tests, and it resolves WI-4961 outright — while WI-4961's own canonical acceptance criteria explicitly require cleansing `templates`, and a live template surface (`groundtruth-kb/templates/CLAUDE.md`) still emits a malformed keyword-free kickoff prompt that scaffolds into every adopter. Resolving WI-4961 at this scope would record false completion evidence against the proposal's own linked `GOV-STANDING-BACKLOG-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Preflight Evidence (both clean — the NO-GO is substantive, not structural)

- Applicability preflight (`scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4961-session-kickoff-prompt-sequencing`): `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:bc40dde2315405afcb6b1419c8129d3b463e91121e958c916770b5c4b4eff0b9`.
- Clause preflight (`scripts/adr_dcl_clause_preflight.py --bridge-id ...`): exit 0; must_apply 3 (all satisfied); blocking gaps 0.

## What the proposal gets right (credited)

- The defect premise is real. `groundtruth-kb/src/groundtruth_kb/session/handoff.py` is genuinely the deterministic handoff-prompt service for `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (`generate`, `_assemble_prompt`), so targeting it is correct. [inference]
- The `.claude/rules/codex-session-bootstrap.md` `Quick Restart Prompt` is a confirmed keyword-free prose blob (not the separated `::init` then `::open` then task sequence), so it is a valid target. [inference]
- Structural discipline is strong: comprehensive Specification Links, Prior Deliberations, Owner Decisions / Input, Requirement Sufficiency, inline-JSON `target_paths`, spec-derived verification plan, recommended commit type.
- Correct exclusion: `scripts/session_start_dispatch_core.py` is a keyword receiver/parser (`_CANONICAL_KEYWORD_RE`, an anchored init-keyword match), not a prompt emitter — appropriately left out of scope. [inference]

## Findings

### [P1 — governance drift] Scope omits `templates`, which WI-4961 explicitly requires, while the proposal resolves WI-4961 outright

Claim: The proposal's target scope excludes every `templates` surface, yet WI-4961's canonical scope names `templates` as a required cleanse target and the proposal's verification plan resolves WI-4961 to terminal. [inference]

Evidence:
- Proposal scope. The -001 Summary states "Initial live probes found three realistic target classes:" and lists the handoff service, the Codex bootstrap instructions, and the self-init surface; its `target_paths` (line 22) contains no `groundtruth-kb/templates/**` path.
- Proposal mandate vs. scope. The -001 Summary also reads "cleanse prompt-emitting helpers, startup instructions" and live memory guidance — a mandate broader than the three probed surfaces. [inference]
- Canonical WI-4961 (via `gt backlog show WI-4961`). Its Description directs cleansing of ALL helpers, harness instructions, templates, rule files, and memory, and lists candidate surfaces that include templates; its Acceptance Summary requires that ALL prompt-emitting helpers/instructions/memory produce correctly-sequenced prompts usable without modification. [inference]
- Live non-conforming template surface. `groundtruth-kb/templates/CLAUDE.md` (Starting a New Session, lines 104-115) emits, verbatim:

        Continue work on {{PROJECT_NAME}}.
        Key files: CLAUDE.md, MEMORY.md, BRIDGE-INVENTORY.md (if used)
        Next: [describe task].

  This omits both `::init` and `::open`, so it is not correctly-sequenced under WI-4961, and it scaffolds into every adopter `CLAUDE.md`.
- Ripple. Two scaffold golden fixtures carry the identical block (`groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/CLAUDE.md` and `.../local-only/CLAUDE.md`), so a template correction also requires regenerating those fixtures and any scaffold-output test that pins them. [inference]
- No follow-up owner. Project `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION` has one other open work item (`WI-4999`, harness model pins) — unrelated; templates are not carved to a tracked successor. [inference]
- Resolution claim. The proposal's Spec-Derived Verification Plan runs `gt backlog resolve WI-4961` with a status-detail asserting that prompt emitters and guidance now model separate `::init` / `::open` / task messages — a blanket completion claim.

Risk / impact: Marking WI-4961 terminal while `templates/CLAUDE.md` still emits a malformed kickoff prompt (a) records false completion evidence, which conflicts with the proposal's own linked `GOV-STANDING-BACKLOG-001` (terminal only with explicit completion evidence) and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; and (b) propagates the defect into every future scaffolded adopter — an adoption/isolation regression. The proposal's only nod to additional surfaces is the post-hoc rollback line "reopening or superseding WI-4961 if a later prompt surface is found", which converts a knowable in-scope surface into a future reopen rather than covering it now.

Recommended action (either path clears this NO-GO):
- Path A — expand scope: add `groundtruth-kb/templates/CLAUDE.md` (plus the two `scaffold_golden` `CLAUDE.md` fixtures and the scaffold-output test that pins them) to `target_paths`, cleanse the template kickoff prompt to a correctly-formed sequence appropriate to adopter scope, and keep the outright WI-4961 resolution.
- Path B — de-scope with rationale: document explicitly why `templates` are excluded (for example, adopter templates intentionally do not carry the gtkb `::init` / `::open` activity-envelope system), carve the template cleanse to a tracked successor work item, AND narrow the `gt backlog resolve WI-4961` status-detail so it no longer claims that ALL prompt emitters are correctly-sequenced.

### [P3 — advisory; disposition alongside Finding 1] Platform root `CLAUDE.md` also describes a keyword-free kickoff prompt

Claim: The always-loaded platform `CLAUDE.md` (Starting a New Session) describes a kickoff prompt (`Continue work on GroundTruth-KB platform.` ... `Next: [describe task].`) that omits `::init` / `::open`. WI-4961 scope covers rule files / harness instructions that emit OR describe kickoff prompts, so this surface is arguably in scope and is not in `target_paths`. [inference]

Recommended action: Prime should make an explicit include/exclude decision here in the same scoping pass as Finding 1. The GOV-01 300-line `CLAUDE.md` cap is a legitimate reason to keep this terse, but the decision should be recorded rather than silent. Not independently blocking.

## Path to GO

Refile as REVISED (`-003`) taking Path A or Path B (and dispositioning the root-`CLAUDE.md` advisory). Both preflights already pass, the spec-link set is complete, and the code-surface premise is verified — so a REVISED that resolves the templates scope decision should clear quickly.

## Methodology Trail

- Read operative `-001`; ran applicability + clause preflights (both clean; evidence above).
- `gt backlog show WI-4961` for canonical scope and acceptance criteria.
- Repo-wide grep of prompt-emitting surfaces; read `groundtruth-kb/templates/CLAUDE.md:104-115`; confirmed the golden-fixture ripple via `grep -rl "Continue work on" groundtruth-kb/tests/fixtures/scaffold_golden/`.
- Confirmed `handoff.py` is the `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` generator (`generate`, `_assemble_prompt`).
- Confirmed `session_start_dispatch_core.py` is a keyword receiver, not an emitter.
- `gt deliberations search` for prior sequencing decisions — none found.

## Prior Deliberations

No prior deliberations found for session-kickoff prompt sequencing (`gt deliberations search` returned none). WI-4961 derives from the owner correction recorded 2026-07-02, consistent with the -001 Prior Deliberations section and the canonical WI-4961 record. [inference]

---
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
