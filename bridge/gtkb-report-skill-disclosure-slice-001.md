NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bf970d5e-9dda-4a61-bd98-41fac87d2f68
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder session (harness B); explanatory output style; skill-activation WI-4814 report-self-disclosure slice

bridge_kind: prime_proposal
Document: gtkb-report-skill-disclosure-slice
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-ACTIVATION-WI-4814-REPORT-SELF-DISCLOSURE-SLICE-BOUNDED-IMPLEMENTATION-2026-06-25
Work Item: WI-4814
Owner Decision: DELIB-20265900
Umbrella: bridge/gtkb-skill-activation-enforcement-umbrella-002 (GO; DELIB-20265883)
target_paths: ["scripts/skill_disclosure.py", ".claude/skills/verify/helpers/write_verdict.py", ".claude/skills/codex-report/SKILL.md", ".claude/skills/kb-session-wrap/SKILL.md", ".codex/skills/codex-report/SKILL.md", ".codex/skills/kb-session-wrap/SKILL.md", ".codex/skills/MANIFEST.json", "platform_tests/scripts/test_skill_disclosure.py"]
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false
owner_input_required: false

---

# Implementation Proposal — Report Self-Disclosure "Skills applied" line (WI-4814, advisory/report-only, all-3 surfaces)

## Summary

Third implemented slice of `PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT` (slice B VERIFIED;
WI-4810 router proposal filed; WI-4812 already-done and resolved). This slice makes skill
usage **observable** via a compact, machine-parseable "Skills applied" self-disclosure
line, governed by the owner-approved `SPEC-REPORT-SKILL-DISCLOSURE-001`. The line is the
input WI-4810's future `gt skills check` consumes. Advisory/report-only (no hard gate).

Deliverables:

- **D1 — Shared emitter:** `scripts/skill_disclosure.py` (deterministic; no LLM) with
  `format_skills_applied(skills)` → canonical line and `parse_skills_applied(text)` →
  list (`parse(format(x)) == x`). One emitter guarantees identical rendering across
  Claude / Codex / Antigravity.
- **D2 — Verdict surface (helper):** `write_verdict.py` calls the emitter to append the
  line to bridge verdicts when a skills list is supplied.
- **D3 — Report + wrap surfaces (agent-authored):** additive disclosure instructions in
  `.claude/skills/codex-report/SKILL.md` and `.claude/skills/kb-session-wrap/SKILL.md`
  directing the author to emit the line via the helper; the Codex adapters
  (`.codex/skills/<name>/SKILL.md` + `MANIFEST.json` hashes) are regenerated via
  `generate_codex_skill_adapters.py` and harness-parity verified.
- **D4 — Spec-derived tests:** `platform_tests/scripts/test_skill_disclosure.py` covering
  the emitter, the verdict wiring, the SKILL.md instructions, and adapter parity.

## Reconciliation With Canonical State

Due-diligence against live source (per the slice-B / WI-4812 pattern):

- **No deterministic skill-invocation signal exists** anywhere in source, so the line is
  author-reported this slice (auto-population deferred). Confirmed by content search.
- **Surfaces split by mechanism:** verdicts are helper-generated (`write_verdict.py` —
  clean code wiring); LO reports + session wraps are agent-authored (no `helpers/` dir) —
  hence the additive SKILL.md instruction approach.
- **Antigravity has no per-skill adapter:** `generate_antigravity_skill_adapters.py`
  writes `[capabilities.antigravity]` registry blocks (capability metadata, unaffected by
  SKILL.md content); Antigravity reads the canonical `.claude` skill. So the content edit
  propagates to the Codex adapter only; the registry is NOT touched (no WI-4811 overlap).

## Requirement Sufficiency

**Existing requirements sufficient.** `SPEC-REPORT-SKILL-DISCLOSURE-001` (requirement,
`specified`, owner-approved this session) governs the emitter contract, the 3-surface
integration, report-only posture, parity, and the content-boundary, and supplies AC1–AC7.
No new/revised formal requirement is needed; this proposal creates no governance and
mutates no formal artifact.

## Specification Links

- `SPEC-REPORT-SKILL-DISCLOSURE-001` — **governing implementation spec** (R1–R8 + AC1–AC7);
  the verification plan maps a test to each acceptance criterion.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; numbered append-only lifecycle.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — project carries linked specs.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` — advisory adopt-conversion; owner grilling
  evidence (`DELIB-20265900`) recorded in Owner Decisions / Input.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — slice authorized by the bounded PAUTH
  cited in the header (this spec is included in that PAUTH).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Work Item / Project
  Authorization triple present in the header.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory: report-only
  observability surface this slice (no write-time gate).
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — harness-parity discipline for the
  SKILL.md/adapter change (Claude / Codex / Antigravity consistency).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the emitter is a deterministic service.
- `DELIB-20265883` (umbrella program-scoping) and `DELIB-20265900` (this slice's grilling).
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-14-35-skill-usage-advisory.md`
  — source advisory (enforcement-model §4 "Report self-disclosure").
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — this slice preserves the umbrella,
  the grilling/spec-approval decisions, `SPEC-REPORT-SKILL-DISCLOSURE-001`, the project
  record, WI-4814, and this proposal as durable linked artifacts; no untracked-artifact
  lifecycle transition.

## Owner Decisions / Input

Advisory adopt-conversion, so per `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` the grilling
evidence is recorded here.

- `DELIB-20265900` (owner_conversation, outcome=owner_decision; AUQ
  `AUQ-WI4814-GRILLING-2026-06-25`) — the design grilling:
  - **Surfaces = all 3** (LO reports + bridge verdicts + session wraps).
  - **Mechanism = shared deterministic emitter** (`scripts/skill_disclosure.py`).
  - Prime-scoped (disclosed): author-reported population (no signal exists); report-only;
    machine-parseable format.
- `AUQ-WI4814-SPEC-APPROVAL-2026-06-25` (formal-artifact-approval for
  `SPEC-REPORT-SKILL-DISCLOSURE-001`) — owner answer "All-3 & record," made with the
  SKILL.md + adapter-regen + parity cost explicit in the spec's scope note. This
  authorizes the PAUTH scope and the filing of this proposal.
- `DELIB-20265883` (owner_conversation) — the umbrella-scoping AUQ (advisory-first posture).

No further owner decision blocks implementation. Any future hard-gate on omission is a
separate owner AUQ per the umbrella.

## Prior Deliberations

- `DELIB-20265883` — umbrella program-scoping owner decision (this slice's parent).
- `DELIB-20265900` — this slice's grilling + design owner decision.
- `bridge/gtkb-skill-activation-enforcement-umbrella-002.md` (GO) — carries forward
  `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` and the harness-parity residual-risk note this
  slice addresses; also flags the content-vs-routing coupling boundary this slice respects.
- `DELIB-20265895` — sibling WI-4810 router grilling; WI-4810's `check` is the downstream
  consumer of this slice's disclosure line (dependency direction: WI-4810 depends on
  WI-4814, not vice-versa — this slice is uncoupled).
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-14-35-skill-usage-advisory.md`
  — source advisory; enforcement-model §4 names this self-disclosure surface.
- A pre-filing `search_deliberations()` for the disclosure topic returned no conflicting
  prior decision (closest: the WI-4810 grilling `DELIB-20265895`).

## Deliverable detail

**D1 (`scripts/skill_disclosure.py`):** `format_skills_applied(skills: list[str]) -> str`
emits `Skills applied: <comma-separated, de-duplicated, order-preserving names>`;
`parse_skills_applied(text: str) -> list[str]` extracts the list from a body (tolerates an
absent line → `[]`). Empty list → `Skills applied: (none)`. Pure functions; no I/O beyond
the passed strings.

**D2 (`write_verdict.py`):** add an optional skills-applied parameter/CLI flag; when
supplied, append the emitter's line to the verdict body before write. Absent → no line
(report-only). No change to existing verdict structure, status token, or author metadata.

**D3 (SKILL.md instructions + Codex adapter regen):** add a short additive "Skills
applied disclosure" instruction block to `.claude/skills/codex-report/SKILL.md` and
`.claude/skills/kb-session-wrap/SKILL.md` (additive observability instruction only — no
body rewrite, preserving the MODERNIZATION boundary), then run
`generate_codex_skill_adapters.py` to regenerate `.codex/skills/codex-report/SKILL.md`,
`.codex/skills/kb-session-wrap/SKILL.md`, and `.codex/skills/MANIFEST.json` source hashes;
verify `check_harness_parity.py` passes.

## Spec-Derived Verification Plan

| Spec acceptance criterion | Deliverable | Test (spec-derived) |
|---|---|---|
| `SPEC-REPORT-SKILL-DISCLOSURE-001` AC1 | D1 | `format_skills_applied(["gtkb-bridge","verify"])` → canonical line; `parse_skills_applied` round-trips it |
| AC2 | D2 | `write_verdict.py` body includes the line when skills supplied; absent when not |
| AC3 | D3 | both `.claude/skills/{codex-report,kb-session-wrap}/SKILL.md` contain the additive instruction referencing `scripts/skill_disclosure.py` |
| AC4 | D3 | regenerated `.codex/skills/{codex-report,kb-session-wrap}/SKILL.md` + `MANIFEST.json` are parity-clean (`check_harness_parity.py` passes) |
| AC5 | D1 | emitter performs no network/LLM; identical input → identical output |
| AC6 | D1 | empty list → `Skills applied: (none)`; parser tolerates a missing line (returns `[]`, no error) |
| AC7 | D3 | no skill content beyond the additive instruction is modified (boundary guard: diff confined to the added block) |

Execution commands (run against changed files before the post-implementation report):

```
.venv/Scripts/python -m pytest platform_tests/scripts/test_skill_disclosure.py -q --tb=short
.venv/Scripts/python scripts/check_harness_parity.py --all --markdown
.venv/Scripts/python -m ruff check scripts/skill_disclosure.py platform_tests/scripts/test_skill_disclosure.py
.venv/Scripts/python -m ruff format --check scripts/skill_disclosure.py platform_tests/scripts/test_skill_disclosure.py
```

## Target Path Rationale

- `scripts/skill_disclosure.py` — D1 emitter/parser (new source).
- `.claude/skills/verify/helpers/write_verdict.py` — D2 verdict wiring (source edit).
- `.claude/skills/codex-report/SKILL.md`, `.claude/skills/kb-session-wrap/SKILL.md` — D3
  canonical additive instruction (skill_docs).
- `.codex/skills/codex-report/SKILL.md`, `.codex/skills/kb-session-wrap/SKILL.md`,
  `.codex/skills/MANIFEST.json` — D3 regenerated Codex adapters + source-hash manifest
  (generated outputs of `generate_codex_skill_adapters.py`; in `target_paths` so the regen
  writes are authorized).
- `platform_tests/scripts/test_skill_disclosure.py` — D4 spec-derived tests (new test).

All paths are tracked, in-root, and within the PAUTH's `source` + `skill_docs` +
`test_addition` classes. No `[capabilities.*]` registry block is modified (no WI-4811
overlap); no skill content beyond the additive disclosure instruction is changed (SPEC R7).

## Risk / Rollback

- **Risk:** SKILL.md edit drifts the Codex adapter out of parity. **Mitigation:**
  regenerate via the generator (never hand-edit `.codex`); AC4 asserts `check_harness_parity`
  passes; the regen is part of the change set.
- **Risk:** the additive instruction is read as content modernization (boundary).
  **Mitigation:** AC7 confines the diff to the added block; framed as observability-only.
- **Risk:** parser mis-reads a malformed line. **Mitigation:** strict canonical format
  (R2); AC6 covers empty/missing; report-only so a parse miss never blocks.
- **Rollback:** reverting the eight `target_paths` (including regenerated adapters) fully
  removes the slice; report-only, no hard gate, no residual behavior.

## Recommended Commit Type

`feat:` — net-new capability surface (emitter module, verdict wiring, report/wrap
disclosure instructions, regenerated adapters, spec-derived tests).

## Requested Loyal Opposition Review

Please review whether (1) the emitter is deterministic + the format is robustly parseable
(SPEC R1/R2); (2) the verdict wiring is additive + report-only (R5); (3) the SKILL.md edits
are confined to additive observability instructions and stay within the MODERNIZATION
boundary (R7), with the Codex adapter regen + parity correctly scoped (R6/AC4); (4) the
`target_paths` correctly include the generated adapter outputs; and (5) the spec-derived
test plan covers AC1–AC7. A `GO` authorizes implementation within the eight declared
`target_paths`. A `NO-GO` should identify a scope, spec-linkage, parity, or test-coverage
gap.
