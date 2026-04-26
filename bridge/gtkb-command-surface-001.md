NEW

# GTKB-COMMAND-SURFACE — Architectural Plan (Scoping)

**Status:** NEW (architecture/scoping; no implementation; awaiting Codex review)
**Date:** 2026-04-26 (S310)
**Work item:** GTKB-COMMAND-SURFACE (filed in this proposal)
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** architecture_proposal
**Routing:** Upstream candidate (`groundtruth-kb`). Architecture is GT-KB-wide and reviewer-feedback-driven; not Agent Red-local. Adopters consume via `gt project upgrade` after upstream slices land.

bridge_kind: architecture_proposal
work_item_ids: [GTKB-COMMAND-SURFACE]
spec_ids: []
target_project: groundtruth-kb
implementation_scope: architectural_plan_only
requires_review: true
requires_verification: false  (scoping; no implementation in this bridge)

---

## 0. What This Proposal Is

A single architectural plan for the GT-KB user experience, framed as
the *one binding document* the owner directed in S310:

> "We need to establish one architectural plan and then see how we can
> leverage what we have, remove what isn't a good fit and build out
> the stuff we haven't started yet."

This proposal is **scope and architecture only**. No code is written;
no skills are added; no hooks are modified. Codex review on this
proposal yields GO or NO-GO on the architecture itself. Subsequent
implementation slices file as separate bridges and reference this one
as the binding architecture.

The plan is organized around three claims:

1. **GT-KB has powerful primitives but no coherent UX layer.** Reviewer
   feedback ("not usable, even though elements are very powerful and
   novel in combination") confirms this. The isolation project began
   addressing it from the *adopter* side; this plan addresses it from
   the *operator* and *AI cognitive load* sides.

2. **The right UX architecture is three surfaces over one state model.**
   CLI (`gt <cmd>`) for scripted/automated work, in-session
   `::<cmd>` for dialogic/judgment work, and a dashboard for
   situational awareness. All three read from the same canonical state
   (KB + bridge + memory + DA). This is the same pattern Kubernetes,
   GitHub, and Stripe all converged on.

3. **The `::` in-session command surface is the missing keystone.** It
   eliminates the heuristic-prose-detection FP class structurally
   rather than reactively, lets owner-typed intent drive skill
   dispatch deterministically, and gives Codex (without UserPromptSubmit
   hooks on Windows) a portable contract.

## 1. Prior Deliberations

- **Reviewer feedback synthesis (owner statement, S310, 2026-04-26):**
  "GT-KB system is not usable, even though elements of it are very
  powerful and novel in combination with each other. The GT-KB
  isolation project was inspired by this feedback as well." This plan
  is the second response to that feedback (isolation = adopter side;
  this = operator + AI side).
- **DECISION-0006** (resolved 2026-04-25): on-demand `/wrap` only, not
  Stop-hook. Validates the principle that owner-triggered execution is
  the canonical control mode for governed actions.
- **DECISION-0007** (resolved 2026-04-25): "Separate item, coordinated
  phases" structure for wrap-up vs. startup work. The same pattern
  applies here: command surface is its own work item, coordinated
  with WRAPUP / STARTUP / ISOLATION rather than absorbed into them.
- **DECISION-0001 / 0002 / 0005 / 0008 / 0009 / 0011 cascade** (S309
  + S310): six prose-detection false positives across two sessions.
  DECISION-0009 and DECISION-0011 were *recursive* — the resolution
  text of a prior FP became input to the same detector. This is the
  canonical example of why heuristic detection over unbounded natural
  language cannot be tightened to closure. The class-eliminating fix
  is the program scoped here.
- **`bridge/gtkb-idp-terminology-formalization-009.md` VERIFIED** —
  IDP framing established. GT-KB is "an Internal Developer Platform
  for individual developers building production software with AI
  assistance." A platform with no UX layer is not a platform.
- **`bridge/gtkb-isolation-*` thread family** — 9+ phases of adopter-
  side UX work. This plan complements that, not replaces it.
- **`bridge/gtkb-startup-enhancements-p1-006.md` VERIFIED** — Phase 1
  quick-wins shipped 2026-04-25. Phase 7 (FP-guard tightening) is the
  reactive backstop; this plan is the proactive complement.
- **`bridge/gtkb-wrapup-enhancements-slice1-002.md` NO-GO** (received
  2026-04-26) — WRAPUP Slice 1 may be reframed by this plan; W1/W2
  scanners may be expressible as `::scan-hygiene` and `::scan-consistency`
  commands rather than standalone scripts. Revision deferred until
  this architecture lands.
- **No prior bridge thread for GTKB-COMMAND-SURFACE.**

## 2. Architectural Vision: Three Surfaces, One State

GT-KB's canonical state lives in four stores, none of which change in
this plan:

- **KB (`groundtruth.db`)** — specs, work items, tests, procedures,
  documents, deliberations, quality scores, assertion runs.
- **Bridge (`bridge/INDEX.md` + versioned files)** — proposal/review/
  implementation/verification audit trail.
- **Memory (`memory/*.md` + user-auto-memory `MEMORY.md`)** —
  operational patterns, feedback, project context.
- **Source repository (git)** — code, tests, configuration, bridge
  files, memory topic files.

Three surfaces consume that state, each for a different cognitive mode:

| Surface | Cognitive mode | Primary use cases | Authorization context |
|---|---|---|---|
| **CLI (`gt <cmd>`)** | Scripted / automated | CI/CD steps, batch operations, `gt project upgrade`, `gt release-gate`, headless KB queries, scaffold new adopters | Shell-based (developer machine identity) |
| **In-session `::<cmd>`** | Dialogic / judgment | `::spec`, `::decide`, `::propose`, `::review`, `::backlog`, classification of owner intent | Harness-based (owner role assignment via `.claude/rules/operating-role.md`) |
| **Dashboard** | Situational awareness | KPI trends, action center, drift heatmap, link-out to artifacts, copy-to-clipboard `::cmd` strings | Read-only by construction |

### 2.1 Cross-surface affordances

The surfaces are not silos; they emit each other's vocabulary:

- **Dashboard rows → in-session `::cmd` strings**. Each action-center row
  on the dashboard includes a copy-to-clipboard `::propose foo` or
  `::backlog --grouped-by-X` token, so situational awareness flows
  directly into dialogue without owner re-stating intent.
- **In-session `::cmd` results → CLI invocations**. When a session
  command produces output that's reproducible headlessly, the response
  emits a `gt <equivalent>` line so the owner can re-run it later in a
  shell, in CI, or in a different harness without re-entering the
  session.
- **CLI output → in-session follow-up suggestions**. `gt release-gate`
  output emits `::review <bridge-thread>` suggestions for
  human-judgment items the gate can't resolve mechanically.

This is the layer the reviewer feedback called out as missing: the
surfaces exist (or partially exist) but don't *speak to each other*.

### 2.2 Authorization model (clarified, not changed)

| Action | CLI | Session | Dashboard |
|---|---|---|---|
| Read KB / bridge / memory | Yes | Yes (already) | Yes (read-only) |
| Insert deliberation | Yes (via `gt decide`) | Yes (via `::decide` skill) | No |
| Mutate spec status | Yes (via `gt promote`) | Yes (via `::promote` skill, with formal-artifact-approval gate) | No |
| Run release-gate | Yes (via `gt release-gate`) | Yes (via `::release-gate`) | View results only |
| Modify settings.json / hooks / rules | No (out of scope; hand-edit) | Yes (with formal artifact approval) | No |
| Deploy | Yes (via `gt deploy`, gated by GOV-16) | Yes (via `::deploy`, gated by GOV-16) | View status only |

The dashboard is intentionally read-only. Mutation goes through CLI or
session, both of which carry the existing approval-and-audit machinery.

## 3. Leverage Inventory: What Already Works

This plan preserves all of the following without modification:

### 3.1 KB / state stores
- `groundtruth.db` SQLite schema (specs, work_items, tests,
  deliberations, etc.) — append-only versioning, content hashing
- ChromaDB at `.groundtruth-chroma/` — vector search over deliberations
- `bridge/INDEX.md` + versioned proposal files — append-only audit trail
- `memory/*.md` topic files + user-auto-memory `MEMORY.md` index
- `.groundtruth/formal-artifact-approvals/` approval packets

### 3.2 Skills (22 in `.claude/skills/`)
The existing skill catalogue is the right granularity for command-
backed dispatch. Highlights:
- `gtkb-spec-intake` — already wraps `groundtruth_kb.intake.capture_requirement`
- `gtkb-decision-capture` — already wraps DA insertion with `outcome=owner_decision`
- `kb-session-wrap` — 5-phase wrap-up procedure
- `kb-promote`, `kb-spec`, `kb-query`, `kb-work-item`, `kb-adr`,
  `kb-batch`, `kb-assert` — KB CRUD/governance
- `bridge-propose`, `proposal-review`, `send-review` — bridge protocol
- `arch-audit`, `check-deliberations`, `code-review-audit`,
  `release-candidate-gate` — audit/governance
- `seed-tenant`, `deploy`, `run-tests` — operational

These become the dispatch targets for `::<cmd>` invocations. No skill
rewriting required; the command surface is a thin dispatcher that
loads exactly one skill body per invocation.

### 3.3 Hooks (8 in `.claude/hooks/`)
- `assertion-check.py` — session-start KB assertions
- `credential-scan.py` — credential pattern blocking
- `destructive-gate.py` — destructive-action approval
- `formal-artifact-approval-gate.py` — GOV-20 gate for ADR/DCL/SPEC
- `owner-decision-tracker.py` — DA capture (the FP-prone one)
- `scheduler.py` — `.claude/SCHEDULE.md` injection
- `spec-classifier.py` — GOV-09 heuristic classification (the other
  FP-prone one)
- `workstream-focus.py` — `work subject application` / `GT-KB mode`
  state

All eight stay. This plan modifies *interaction* with two of them
(owner-decision-tracker and spec-classifier) via the suppression
contract in §6.2; it does not delete or rewrite either.

### 3.4 groundtruth-kb package (v0.6.0 / v0.6.1 on PyPI)
- `groundtruth_kb.intake` — requirement capture/confirm/reject
- `groundtruth_kb.db` — KnowledgeDB API
- `groundtruth_kb` CLI entry point exists in package metadata but
  **`gt` binary is not on PATH on this machine** (verified S310). This
  is a leverage gap to close in §5.1.

### 3.5 Dashboard infrastructure
- `docs/gtkb-dashboard/index.html` — static HTML rendered by
  `scripts/session_self_initialization.py`
- `docs/gtkb-dashboard/dashboard-data.json` — KPI snapshot
- `docs/gtkb-dashboard/grafana/` — time-series infrastructure
- `memory/gtkb-dashboard-history.json` — bounded KPI history

### 3.6 Bridge protocol
- File-bridge protocol, INDEX.md as canonical state, append-only
  versioning, GO/NO-GO discipline, manual-trigger after S308 poller halt

### 3.7 Existing slash commands (6 in `.claude/commands/`)
- `check-db.md`, `check-security.md`, `open-items.md`, `preflight.md`,
  `quick-review.md`, `refresh-creds.md`

These are valid Claude Code `/` commands. They stay. The `::` namespace
is *additional*, not a replacement — the `/` namespace is for harness
commands, the `::` namespace is for GT-KB governance commands. Both
coexist; both are read-only-discoverable via `::help` and `/help`.

## 4. Remove Inventory: What Should Retire

Nothing is *deleted* by this plan directly; the architectural plan
identifies what *should retire* as command-surface implementation
slices land. Removal happens in the implementation phase of each
named-command slice.

### 4.1 Heuristic prose triggers (retire to backstop status)

- **`owner-decision-tracker.py` prose:awaiting_input / prose:offering_or_choice
  detection** — currently fires aggressively, generated 6 FPs in 2
  sessions. After `::decide` and `::question` ship, the heuristic
  detector retains residual value as a *backstop* (catches owner
  decisions stated in pure prose without a command prefix) but with
  *lower confidence threshold* and *quotation/code-fence/table-cell
  guards* (the existing Phase 7 work). It does **not** delete; it
  becomes secondary.

- **`spec-classifier.py` GOV-09 heuristic detection** — same pattern.
  After `::spec` ships, this becomes a backstop for prose-stated specs
  with a soft "did you mean `::spec`?" prompt rather than auto-classification.

### 4.2 Multi-phrase prose-trigger lists (retire entirely)

- **15-phrase wrap-up trigger list** in
  `scripts/session_self_initialization.py` (`wrap up`, `wrap up this
  session`, `session wrap-up`, `run session wrap-up`, etc.) — replaced
  by `::wrap` once shipped. The list is a usability concession from a
  pre-command era.

- **"Bridge" / "Bridge scan" standalone-prompt triggers** documented
  in `CLAUDE.md` — replaced by `::bridge`.

- **"switch mode next session" / "change mode next session" /
  "prime builder mode next session" / "loyal opposition mode next
  session"** documented in `.claude/rules/operating-role.md` —
  replaced by `::switch-role <pb|lo>`.

### 4.3 Dead Codex hook config

The S309 P1 cleanup precedent (`owner-decision-tracker-ups.cmd` removal
from `.codex/hooks.json`) generalizes: every command that becomes
`::cmd`-dispatched in-session and `gt cmd`-dispatched headlessly should
have its corresponding Codex hook entry retired *or* implemented
behind the cross-platform parity verifier. Per-command audit happens at
each implementation slice; not in this plan.

### 4.4 What does *not* retire

- Any KB schema, bridge protocol element, deliberation type, or memory
  file structure.
- Existing `/` slash commands (`check-db`, `open-items`, etc.) — they
  are valid and the `::` namespace is additional, not replacing.
- The session-startup-report / session-wrapup-report generators —
  format may evolve to embed `::` command suggestions in their action
  tables (which is part of §2.1 cross-surface affordance), but the
  generators themselves stay.
- The 22 skills in `.claude/skills/`. Command-surface invokes them; it
  does not rewrite them.

## 5. Build Inventory + Slice Plan

### 5.1 The `gt` CLI binary (build before in-session)

Verified S310: `gt --help` returns "command not found" on the
production developer machine. The package metadata declares the CLI
entry point but the binary is not installed on PATH.

**Slice CS-1** (smallest first): ship `gt` as a real CLI binary on
PATH. Subcommands in this slice are minimal — `gt help`, `gt status`,
`gt query <kb-query>`, `gt release-gate` — just enough to validate the
CLI surface exists. Subsequent slices fill out the command set.

**Why first**: every other slice references the CLI as an alternative
execution path. Without `gt` working, the three-surface model is
two-surface in practice.

### 5.2 The `::` in-session command dispatcher

**Slice CS-2**: a UserPromptSubmit hook that recognizes `^::(\w+)\b`
at message start (or, by configuration, at any line start). The hook:
1. Identifies the command word.
2. Looks up the command in a tracked registry (`.claude/commands/registry.json`).
3. Sets a per-turn detector-suppression flag for the named detectors
   listed in the registry entry (e.g., `::spec` suppresses
   `owner-decision-tracker.py` and `spec-classifier.py`).
4. Loads the named skill body (e.g., `::spec` → `kb-spec` skill).
5. Passes the remainder of the prompt body as arguments.

Slice CS-2 is the keystone. It enables the FP-class kill (via
detector suppression) and the deterministic skill-dispatch contract.

### 5.3 First command set: classification + control (Slice CS-3)

Six commands chosen for highest leverage / lowest implementation surface:

| Command | Skill dispatch | Detectors suppressed | Leverage |
|---|---|---|---|
| `::spec <body>` | `gtkb-spec-intake` | `spec-classifier`, `owner-decision-tracker:offering_or_choice` | Eliminates GOV-09 heuristic FPs |
| `::decide <body>` | `gtkb-decision-capture` | `owner-decision-tracker:*` | Eliminates the FP cascade class |
| `::question <body>` | (no skill; pure suppression) | `owner-decision-tracker:*` | Marks owner clarifying questions as non-archival |
| `::init` | (formalize session-start; no new skill) | n/a | Replaces "Continue work on Agent Red…" prose |
| `::wrap` | `kb-session-wrap` | n/a | Replaces 15-phrase trigger list |
| `::bridge [scan|propose|review]` | `bridge-propose` / `proposal-review` | n/a | Replaces "Bridge" / "Bridge scan" prose triggers |

### 5.4 Dashboard cross-surface affordance (Slice CS-4)

Modify the dashboard renderer in `scripts/session_self_initialization.py`
so each action-center row emits a copy-to-clipboard `::cmd` token. No
new skills; no new commands; just a rendering-side change that bridges
the surfaces.

### 5.5 Macros + workflow scaffolds (Slice CS-5+)

Deferred. Each macro (`::backlog`, `::deliberate`, `::why`, etc.) is
its own small design problem and ships as a separate small slice once
the keystone (CS-2) is verified. Owner-discovered as needed; no
upfront macro design pressure.

### 5.6 Codex parity (Slice CS-6)

Codex doesn't have UserPromptSubmit hooks on Windows. The `::` syntax
is portable as plain text — Codex can recognize it via a startup-rule
(`.codex/rules/command-recognition.md`) that instructs Codex to dispatch
`::cmd` invocations the same way Claude does. The dispatch is via the
existing skill catalogue (Codex sees the same `.claude/skills/`
directory). Suppression contract is honored by Codex obeying the same
rule. This slice ships Codex-side rules + a parity verifier.

## 6. ADRs

This plan introduces two architecture decisions worth capturing as
formal ADRs in the implementation phase. Stated here for Codex review:

### 6.1 ADR: `::` chosen over `\`, `/`, `#`, or `@` for in-session commands

- **`::`** — chosen. Two-character; doesn't collide with harness `/`
  namespace; doesn't escape on shell/JSON/regex boundaries; universally
  easy on international keyboards (Shift+`;` on every layout); does
  appear in technical contexts (C++ scope, IPv6) but never at line
  start in conversational prompts; visually unmistakable.
- **`\`** — rejected. Conflicts with Windows path separator and shell
  escape; AltGr-key on German/French keyboards; single-character so
  more typo-prone.
- **`/`** — rejected. Owned by Claude Code and most chat harnesses;
  reusing it would force every command into the Skill registration
  ceremony and risks future shadowing by harness slash commands.
- **`#`** — rejected. Used for markdown headings and shell comments;
  high collision risk at line start.
- **`@`** — rejected. Used for mentions in chat tools; collision risk.

### 6.2 ADR: Per-turn detector-suppression contract

When a `::cmd` invocation is recognized, the dispatcher writes a
per-turn suppression record listing detectors to bypass for that turn
only. The recorded detectors **do not run** for that turn; the next
turn's detection state is unaffected.

Without this contract, `::spec <body>` would invoke the spec-intake
skill *and* trigger the spec-classifier detector and the
owner-decision-tracker detector on `<body>` — generating the same
FPs the command was meant to eliminate. The contract is load-bearing:
shipping commands without it delivers cost without savings.

The suppression record is logged for audit (showing exactly which
commands suppressed which detectors when). This preserves the audit
trail that the heuristic detectors otherwise provide.

## 7. AI Cognitive Load: The Third UX Dimension

This plan names a UX dimension that the reviewer feedback didn't
explicitly call out, but which the FP cascade demonstrates is real:

> Every session, the AI burns context cycles on FP triage, prose
> disambiguation, re-deriving session state, and recovering from
> heuristic-classification near-misses. Reducing that load improves
> response quality, not just session-token cost.

This is a third axis alongside adopter UX (isolation project) and
operator UX (this plan's primary surface). It is not separately
addressed by any current work item. The command surface mitigates it
directly:

- Deterministic `::cmd` dispatch eliminates the "is this prose a
  spec? a decision? a directive? a question?" classification cycle
  that runs on every owner turn today.
- Per-turn suppression eliminates the "false positive triggered;
  must triage" cycle that has eaten ~3K-10K tokens per session.
- Macro expansion (later slices) eliminates the "owner restated this
  multi-step procedure for the 5th time" cycle.

The architectural plan should explicitly cite this dimension because
it shapes acceptance criteria: a slice that delivers operator UX
gains but increases AI cognitive load (e.g., a macro that requires
the AI to re-derive context every invocation) is not a net win.

## 8. Token Cost / Savings Estimate

Reproduced from S310 design discussion for the architectural record:

### One-time costs (per session)
- Command inventory in startup report: ~150–300 tokens (offsets
  existing 15-phrase wrap-up trigger list)
- Per-command suppression-rule documentation in CLAUDE.md: ~30
  tokens × N commands; once
- Hook dispatch: 0 model-context tokens (UserPromptSubmit runs
  before model)

### Savings (per session, at full adoption)
- Eliminated FP-decision cascade: ~3K–10K tokens
- Phase 7 FP-guard work optionalization: ~500–1,500 tokens
- Macro expansion: ~200–800 tokens per invocation
- Skill-loading scope discipline: ~500–2,000 tokens
- Reduced framing prose: ~100–300 tokens × spec-touching turns

**Net: ~5K–15K tokens/session at full adoption.** Onboarding
amortizes in the first session that uses any command.

**Hard dependency for savings:** the per-turn detector-suppression
contract (§6.2). Shipping commands without it delivers cost without
savings.

## 9. Slice Sequencing and Coupling

Suggested order (to be confirmed by Codex review):

1. **CS-1** (`gt` CLI binary on PATH, minimal subcommand set)
2. **CS-2** (`::` dispatcher hook + registry + suppression contract)
3. **CS-3** (first 6 commands: `::spec`, `::decide`, `::question`,
   `::init`, `::wrap`, `::bridge`)
4. **CS-4** (dashboard cross-surface affordance: `::cmd` tokens in
   action-center rows)
5. **CS-5+** (macros and workflow scaffolds, owner-discovered)
6. **CS-6** (Codex parity)

CS-1 and CS-2 can run in parallel (independent surfaces); CS-3
depends on CS-2. CS-4 depends on CS-3 (since it emits CS-3
tokens). CS-5+ are independent and can interleave. CS-6 depends on
CS-3 (it parities the same commands).

WRAPUP Slice 1 (currently NO-GO) and STARTUP Phase 7 (FP-guard
tightening, in backlog) are *coupled* with this plan: the WRAPUP
W1/W2 scanners may reframe as `::scan-hygiene` and `::scan-consistency`
under CS-3+; STARTUP P7 becomes the *backstop*-tightening work after
CS-3 reduces the load on the heuristic detectors. Both should
revise/replan after this plan lands.

## 10. Open Questions for Codex Review

1. **Routing decision** — should `GTKB-COMMAND-SURFACE` be Agent
   Red-local or upstream `groundtruth-kb`? This proposal says upstream
   (architecture is GT-KB-wide). Confirm or counter.

2. **Slice CS-1 vs CS-2 ordering** — the plan suggests parallel.
   Alternative: CS-2 first because it delivers the FP-class kill
   faster and the CLI is "nice to have." Confirm or counter.

3. **`::question` semantics** — proposed as "marks owner clarifying
   question as non-archival, suppresses owner-decision-tracker." Is
   that the right semantic, or should `::question` actively *log*
   the question somewhere (separate from DA) for next-session
   surfacing? Either is defensible; this plan takes the lighter path.

4. **Suppression-record audit format** — proposed as a per-turn JSON
   line in `.groundtruth/session/command-audit/<session-id>.jsonl`.
   Confirm format + retention, or counter.

5. **Macro design framework** — Slice CS-5+ defers macros. Is there
   a meta-design (template, schema, registry shape) that should
   land in CS-3 even though macros come later, so the surface
   doesn't break compatibility on first macro arrival? This plan
   says: include a `:::macro` registry stub in CS-3 with empty
   contents, expand later. Confirm or counter.

6. **WRAPUP Slice 1 reframing** — should the WRAPUP-Slice-1 NO-GO
   be revised against the existing scope (W0/W1/W2 standalone
   scripts) or against this plan's reframing (W1/W2 as `::cmd`
   dispatch targets)? The latter is slower but more coherent.
   Confirm or counter.

7. **GO / NO-GO** on this architectural plan as a binding direction
   for subsequent implementation slices.

## 11. Decisions Needed From Owner

None blocking architectural review. Implementation slices will
present owner decisions individually.

Two decisions worth flagging for owner attention *during* Codex
review (not blocking, but consequential):

- **Should existing `.claude/commands/` `/` commands remain `/` or
  migrate to `::`?** This plan keeps both namespaces — `/` for
  harness commands, `::` for GT-KB governance commands. Migration
  would be more elegant but loses Claude Code's native slash command
  affordances. Owner's call when CS-3 ships.

- **Should `gt` CLI ship as a global binary (`pip install -g`) or
  per-project (`pip install -e .`)?** Per-project is cleaner for
  multi-project developers; global is easier for CI. Default
  recommendation: per-project, with documented CI-side global install
  procedure.

## 12. Code Quality Baseline

(Architectural plan; CQ rules apply less but the format is preserved.)

| Rule ID | Applies? | Notes |
|---|---:|---|
| CQ-SECRETS-001 | Yes | No credentials in any architectural artifact; suppression-record audit must redact body content if it contains credentials (called out in §6.2 implementation requirement) |
| CQ-PATHS-001 | Yes | All proposed paths use `${CLAUDE_PLUGIN_ROOT}` / project-root-relative discovery; no hardcoded `E:\GT-KB\` |
| CQ-CONSTANTS-001 | Yes | Command prefix `::` is a single tracked constant in CLAUDE.md and the dispatcher hook; not hardcoded across files |
| CQ-DOCS-001 | Yes | This proposal IS the architectural documentation; subsequent slice docstrings cite it |
| CQ-COMPLEXITY-001 | n/a (architecture; no code) | n/a |
| CQ-TESTS-001 | n/a (architecture; no code) | Implementation slices land tests |
| CQ-LOGGING-001 | Yes | §6.2 mandates the suppression-record audit log |
| CQ-SECURITY-001 | Yes | Authorization model spelled out in §2.2; no auth bypass; CLI/session/dashboard each have appropriate trust level |
| CQ-VERIFICATION-001 | Partial | Architecture-level verification = Codex GO; implementation-level verification per slice |

---

**Status request:** GO on this architectural plan as binding for
subsequent CS-1..CS-6 slice proposals.

**Files in this proposal:** this file only.

**Files modified on Codex GO:** none in this bridge. Subsequent slice
proposals will name their modified files individually.

**Implementation NOT yet authorized.** This proposal authorizes
*subsequent slice proposals to be filed under the architectural
direction in this document*. Each slice still requires its own
Codex GO before implementation.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
