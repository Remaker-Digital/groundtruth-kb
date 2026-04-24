NEW

# GTKB MemBase Effective Use — Umbrella (scoping + three sub-slices)

**Status:** NEW
**Date:** 2026-04-24
**Work item:** GTKB-MEMBASE-EFFECTIVE-USE (new, to be created on GO)
**Author:** Prime Builder (Claude Opus 4.7, S307)
**Owner specs this bridge serves:**
- `SPEC-INTAKE-c9e997` — Extract specifications from conversation in-session.
- `SPEC-INTAKE-2485e9` — Surface spec creation/update events in owner chat view.
- `SPEC-INTAKE-3623f1` — Aggressive foundational-requirements intake for new user projects.

bridge_kind: proposal
work_item_ids: [GTKB-MEMBASE-EFFECTIVE-USE]
spec_ids: [SPEC-INTAKE-c9e997, SPEC-INTAKE-2485e9, SPEC-INTAKE-3623f1]
target_project: groundtruth-kb
target_paths: ["templates/hooks/**", "src/groundtruth_kb/intake.py", "src/groundtruth_kb/events.py", "src/groundtruth_kb/foundational_requirements.py", "templates/skills/gtkb-foundational-intake/**", "templates/managed-artifacts.toml"]
implementation_scope: governance
requires_review: true
requires_verification: true

---

## Prior Deliberations

- `DELIB-INTAKE-c971df2d`, `DELIB-INTAKE-9a936aee`, `DELIB-INTAKE-32cc09aa` — the three owner requirements confirmed into specs on 2026-04-24. This bridge is the design pass for mechanizing them.
- `bridge/gtkb-gov-da-enforcement-slice1-004.md` GO — precedent: upstream-routed governance capability (not Agent Red-local).
- `bridge/gtkb-gov-proposal-standards-slice1-020.md` GO — precedent: managed hook family in `templates/hooks/**` consumed by adopter projects via `gt project upgrade`.
- `.claude/hooks/spec-classifier.py` (existing, 120 lines) — current state: detects spec language, emits `systemMessage` visible only to Claude, not to owner.
- `.claude/skills/spec-intake/SKILL.md` + `helpers/spec_intake.py` — existing three-step capture→confirm→reject flow. Functional but not auto-invoked during drafting.
- S307 session evidence: 6+ bridge proposals filed with requirements language, 0 KB specs written until owner explicitly asked. That gap is the motivating symptom.
- KB enumeration (2026-04-24): 8,367 spec rows across 12 `type` values; no `foundational_requirement` type; 1 match for `foundational`, 5 for `bootstrap`, 7 for `onboard` — ad-hoc, not a standardized bootstrap category.
- No prior deliberations found searching `membase-effective-use`, `foundational requirement intake`, or `spec event chat surface`.

---

## 1. Problem Statement

MemBase is used heavily as a decision log (8,367 spec rows, 12 types, rich schema including assertions / authority / constraints / testability / source_paths) but is **not used effectively for three specific workflows the owner needs**:

1. **In-session extraction.** Owner-stated requirements during a session are often captured in bridge proposals (design artifacts) rather than promoted into KB specs (decision-log artifacts). The `spec-classifier` hook nudges Claude but does not guarantee capture. Empirical: S307 produced zero KB specs until the owner explicitly asked for capture, despite multiple owner messages containing "must" / "should" / numbered-criteria language.

2. **Owner-visible spec events.** When specs are created or updated, the owner has no visible signal in the chat stream. The existing classifier's `systemMessage` is Claude-only. The owner can inspect via `localhost:8090` dashboard UI or by querying the DB, but cannot observe events as they happen during the session.

3. **Foundational bootstrap for new projects.** A new project adopting GT-KB has no standardized foundational-requirements set, no dedicated KB category, no intake procedure, no prepared-document template, and no in-session questionnaire. The owner's ask explicitly names the categories to cover (preferred technology choices, mobile UI, security posture, tenancy, external integrations, core features, deployment target, cost constraints, and related). None of those currently have first-class foundational-requirement records in KB.

---

## 2. Proposed Umbrella Structure (Three Sub-Slices)

This bridge is a scoping proposal. On GO, three implementation bridges follow. The sub-slices are ordered by dependency — later sub-slices consume infrastructure from earlier ones.

### 2.1 Sub-slice A — Chat-visible spec event stream (serves `SPEC-INTAKE-2485e9`)

**Thread:** `gtkb-membase-effective-use-slice1a-event-surface`

**Deliverable:** a Stop / PostToolUse hook (upstream-owned managed hook) that watches the KB for spec-row writes in the current session and emits a chat-visible summary line per event.

**Mechanism sketch (to be refined in the implementation bridge):**

- Hook path: `templates/hooks/spec-event-surfacer.py`. Event: `PostToolUse` on `Bash` / `Write` / `Edit` (any tool that could have mutated the KB) AND `Stop` (end-of-turn sweep for anything the inline hook missed).
- State: per-session ledger at `.claude/session/spec-events-seen.jsonl` — records `(spec_id, version, seen_at)` tuples the hook has already surfaced. Prevents double-emit across PostToolUse + Stop.
- Detection: query `specifications` table for rows with `changed_at >= session_started_at` that are not in the ledger. Emit one systemMessage per new row with a compact format:
  ```
  📋 KB spec event: SPEC-XXXX-nnnnnn v1 — created — <title> [type=requirement status=specified]
  ```
- "Visible in chat" mechanic: PostToolUse systemMessage appears as a rendered box in the owner's chat stream (same mechanism as the existing bridge-essential POLLER block), not just a Claude-only injection. This is a deliberate design choice that matches existing chat-visible hook output.

**Why this sub-slice first:** it enables the other two to be observed. Without it, the owner has no real-time signal that in-session extraction (§2.2) or foundational intake (§2.3) is actually firing.

**Does NOT deliver:** automatic capture (that is §2.2). The hook observes; it does not create.

### 2.2 Sub-slice B — Reliable in-session extraction (serves `SPEC-INTAKE-c9e997`)

**Thread:** `gtkb-membase-effective-use-slice1b-auto-extract`

**Deliverable:** raise the existing `spec-classifier` from "nudge" to "capture". When the classifier detects owner-stated requirement language, it captures a `deliberation` at `outcome='deferred'` via `capture_requirement()` immediately — no waiting for Claude to decide. The owner then sees the capture (via §2.1's event surface) and can confirm or reject in-session with a short command.

**Mechanism sketch:**

- Extend `templates/hooks/spec-classifier.py` (currently advisory) into an active capturer. When triggers fire, invoke `groundtruth_kb.intake.capture_requirement()` directly with `changed_by="classifier-auto-capture"` so the audit trail distinguishes auto-captures from skill-driven captures.
- Classifier triggers stay conservative: "must" / "should" / "shall" / "required" / numbered criteria / "I want" / "I would like" clauses in the prompt. The existing classifier's regex library is the starting point; it is extended to separate "informational description" from "statement of requirement" to reduce false positives. See §5.1 open question.
- On capture, §2.1's event hook sees the new `INTAKE-*` deliberation and emits a chat-visible line:
  ```
  📋 KB intake capture: INTAKE-xxxxxxxx (deferred) — <first 60 chars> [awaiting owner confirm/reject]
  ```
- Confirm/reject commands: add prompt-recognition for `"confirm intake INTAKE-xxxxxxxx"` and `"reject intake INTAKE-xxxxxxxx <reason>"` so the owner can act from chat without running scripts. A companion `UserPromptSubmit` hook or an extension of the existing one parses these.
- The existing `spec-intake` skill stays as the programmatic path; the new hook layer is the automatic path. Both flow through the same `intake.py` library.

**Why this sub-slice second:** it depends on §2.1's event surface to be owner-observable. Without §2.1, captures would happen silently.

**Does NOT deliver:** retroactive capture of specs from past conversations (explicit non-goal).

### 2.3 Sub-slice C — Foundational-requirements intake for new projects (serves `SPEC-INTAKE-3623f1`)

**Thread:** `gtkb-membase-effective-use-slice1c-foundational-intake`

**Deliverable:** three things.

**(a) A dedicated KB category.** Add `foundational_requirement` to the `specifications.type` vocabulary, plus a standard `section` taxonomy:
- `tech-stack` — preferred languages, frameworks, runtimes.
- `ui-targets` — mobile / web / desktop constraints.
- `security-posture` — auth model, data sensitivity, compliance class.
- `tenancy` — single-tenant, multi-tenant, SaaS model.
- `external-integrations` — third-party services, APIs, payment rails.
- `core-features` — the minimum feature set defining the product.
- `deployment-target` — cloud provider, region, edge posture.
- `cost-constraints` — budget envelope, cost-per-user targets.
- `operational-posture` — SLA, observability, on-call, backup.
- `compliance` — HIPAA / SOC2 / GDPR / industry-specific requirements.

(Exact final list is a Codex review question — see §5.4.)

**(b) A standard record contract** for a foundational-requirement spec:
- `type = "foundational_requirement"`
- `section ∈ {10 category list above}`
- `authority = "owner_stated"` (vs `"stated"` for regular requirements)
- `priority ∈ {"core", "important", "nice-to-have"}` (narrower vocabulary than general specs)
- `constraints` field populated with the quantitative bound if any (e.g., `"monthly cloud cost < $500"`).
- `source_paths` optional pointer to the uploaded intake document.
- Provisional flag cleared only after owner confirms the record.

**(c) An intake mechanism with two input modes:**

- **Document upload path:** new skill `gtkb-foundational-intake` (upstream, under `templates/skills/`) that accepts a prepared Markdown / YAML document. The skill parses the document into foundational-requirement candidates via pattern matching on the 10 category headings, runs each through `capture_requirement()` at `outcome='deferred'`, and summarizes via §2.1's event surface. The owner confirms en bloc or per-category.
- **In-session questionnaire path:** same skill, alternative entry, walks the owner through the 10 categories in conversational form ("What is the deployment target? Azure, AWS, other?"). Each answer becomes a candidate capture. Questions are adaptive — "single-tenant" answer skips later multi-tenancy subquestions.

**Agent Red as the seed corpus:** the skill ships with a reference foundational-requirements document extracted from Agent Red's current state (`CLAUDE-REFERENCE.md` + live specs). This serves two purposes: (1) documents how Agent Red's foundational choices are recorded so new projects have a worked example, and (2) retroactively establishes Agent Red's foundational requirements as first-class KB records, filling a gap the KB doesn't currently close.

**Why this sub-slice last:** depends on both §2.1 (event surface to show the 10-or-so candidates landing) and §2.2 (auto-capture infrastructure the questionnaire consumes). Also has the most content work (the Agent Red reference corpus).

**Does NOT deliver:** an opinionated "best practices" content layer. The skill captures what the owner says, not what the skill thinks is correct.

---

## 3. Cross-Sub-Slice Non-Goals

These remain out of scope for **all three** sub-slices under this umbrella:

- **Retroactive capture** of past bridge proposals as specs (separate backfill WI if desired).
- **Spec auto-promotion** (`specified → implemented → verified`). Stays owner-gated via existing `/kb-promote` skill.
- **Rejection-on-contradiction** — the system captures; it does not refuse contradictory requirements. Conflict surfacing is downstream work.
- **Non-English requirement handling** — English classifier only for this umbrella.
- **Multi-owner workflows** — single-owner assumption retained.
- **Cross-project foundational-requirement inheritance** — each project gets its own foundational set.

---

## 4. Files Touched (this bridge — scoping only)

**New:** (none — this is a scoping/planning proposal)

**Modified:**
- `memory/work_list.md` — add `GTKB-MEMBASE-EFFECTIVE-USE` as a top-level backlog entry with three actionable sub-slices and the three `SPEC-INTAKE-*` spec refs.

**Not touched:**
- `src/**`, `scripts/**`, `templates/**`, `docs/**`, `tests/**` — no implementation in this bridge. Each sub-slice bridge declares its own files-touched set.

---

## 5. Open Questions for Loyal Opposition Review

1. **Classifier false-positive rate tolerance.** §2.2 extends the existing regex library to separate "informational description" from "statement of requirement". False positives create noise captures the owner has to reject. False negatives miss real requirements. I propose tuning toward false positives (capture liberally; owner's reject overhead is low) but Codex may prefer the opposite. Which bias?
2. **Chat-visible emission vs dashboard-only.** §2.1 emits systemMessage lines into the chat stream. Alternative: emit only to the dashboard (`localhost:8090`) plus a summary at session-wrap. I chose chat because the owner explicitly asked to "see when these specification events happen." Codex to accept.
3. **Confirm/reject command parser location.** §2.2 adds prompt recognition for `"confirm intake INTAKE-xxxxxxxx"`. Alternative: a slash-skill `/confirm-intake`. Prompt recognition is lower friction; slash-skill is more discoverable. Codex to choose.
4. **Foundational-category list size.** §2.3 proposes 10 categories. Too many → questionnaire fatigue. Too few → missed context. The list is informed by Agent Red experience + the owner's enumeration ("preferred technology choices, mobile device UI, security posture, tenancy, external integrations, core features and functions, deployment environment target (e.g., Azure), cost constraints, and so forth"). Codex to accept the 10-category starter or propose a different cut.
5. **Upstream vs Agent Red-local routing.** I scoped to upstream `groundtruth-kb/` because these capabilities benefit all GT-KB adopters, not just Agent Red. This follows the `gtkb-gov-proposal-standards` precedent (Codex's S307 review path). If Codex prefers Agent Red-local first with upstream promotion later, scope contracts significantly. I chose upstream because SPEC-INTAKE-3623f1 explicitly frames this as "new user projects" (plural, multi-adopter scope).
6. **Agent Red retroactive foundational-requirement extraction** (under §2.3's seed-corpus work). Does this rise to a separate WI (`GTKB-AGENT-RED-FOUNDATIONAL-BACKFILL`), or is it part of §2.3's implementation bridge? I lean "part of §2.3" because it's the demonstration the skill needs. Codex to accept or redirect.

---

## 6. Verification Matrix (this bridge — scoping only)

| Risk | Test requirement |
|------|-----------------|
| Sub-slice allocation doesn't serve all three specs | Each of `SPEC-INTAKE-c9e997` / `-2485e9` / `-3623f1` maps to exactly one primary sub-slice in §2; manual cross-check at review. |
| Sub-slice dependencies wrong | 2.2 depends on 2.1 (event surface); 2.3 depends on 2.1 + 2.2; no reverse dependencies. Stated. |
| Scope creep into unrelated governance territory | §3 enumerates non-goals; §5.1 and §5.4 pin the discussion points. |
| `memory/work_list.md` drift | On this bridge VERIFIED, work-list has a single `GTKB-MEMBASE-EFFECTIVE-USE` entry with three sub-slice rows and the three `SPEC-INTAKE-*` refs. |
| Upstream scope overstated | §5.5 flags the routing decision explicitly; Codex can redirect to Agent Red-local before any implementation bridge lands. |
| Categories-list drift | §5.4 names the 10 categories; Codex to accept or replace in review before §2.3 implementation bridge. |

---

## 7. Verification Matrix (each sub-slice bridge, specified at filing)

Each sub-slice bridge will carry its own full pytest lanes, hook-registration assertions, end-to-end capture-and-emit assertions, and non-regression checks against existing classifier + intake behavior. This bridge does not pre-empt those matrices.

---

## 8. Out of Scope

- Implementation of any §2 sub-slice (that is three separate bridges on GO).
- Non-English requirement handling.
- Opinionated "best practices" foundational content layer.
- Cross-project foundational inheritance.
- Multi-owner workflows.
- Agent Red production deployment. No `src/` changes. GOV-16 not triggered.

---

## 9. Decision Needed From Owner

One decision, non-blocking for this bridge:

- **Upstream vs Agent Red-local routing** (tied to §5.5). If owner prefers Agent Red-local first (ship to Agent Red only, promote upstream later), I'll narrow the three sub-slice bridges accordingly on GO. Default: upstream, following the `gtkb-gov-proposal-standards` precedent.

All other design choices surface in the sub-slice bridges, not here.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
