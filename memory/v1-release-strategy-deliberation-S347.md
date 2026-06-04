# GT-KB v1.0 Release Strategy — Deliberation Snapshot

**Session:** S347
**Date captured:** 2026-05-24
**Status:** RESOLVED. The owner selected Option B (Hybrid Variant - Spec-Driven Progressive Refactor) in Session S405. Captured in the Deliberation Archive as **DELIB-2234**.
**Authority class:** Operational topic file (`memory/*.md`), per CLAUDE.md
"Permitted markdown" list. NOT canonical; canonical knowledge lives in MemBase.
**Related artifacts:**
- [bridge/gtkb-agent-red-reference-adopter-framing-restoration-001.md](../bridge/gtkb-agent-red-reference-adopter-framing-restoration-001.md) (NEW; LO review pending) — the prototype remediation that exposed the broader question.
- [.claude/rules/operating-model.md](../.claude/rules/operating-model.md) §3 — current "implemented vs. intended" inventory.
- [applications/Agent_Red/.gtkb-app-isolation.json](../applications/Agent_Red/.gtkb-app-isolation.json) — live isolation contract.

---

## Table of Contents

1. [Background](#1-background)
2. [Core question](#2-core-question)
3. [Current state assessment](#3-current-state-assessment)
4. [Strategic options](#4-strategic-options)
5. [Spec corpus design sketch](#5-spec-corpus-design-sketch)
6. [Comparison: Option A vs. Hybrid](#6-comparison-option-a-vs-hybrid)
7. [The fundamental tradeoff](#7-the-fundamental-tradeoff)
8. [Additional considerations, tips, and warnings](#8-additional-considerations-tips-and-warnings)
9. [Open questions for the owner](#9-open-questions-for-the-owner)
10. [Suggested actions independent of option choice](#10-suggested-actions-independent-of-option-choice)
11. [How to resume this deliberation](#11-how-to-resume-this-deliberation)

---

## 1. Background

The deliberation began with the owner being asked externally whether GT-KB is a
**platform** (an Internal Developer Platform — IDP) or a **suite of
interdependent patterns** for AI-assisted application development. The
distinction matters because:

- An IDP must provide binary compatibility / portability guarantees across
  versions. Its lifecycle is independent from the applications built on it.
- A pattern suite gets forked at adoption time. Future evolution may or may not
  be backportable to any given application that adopted earlier.

The owner asked whether GT-KB could credibly be released as an IDP with
backward-compatibility guarantees, i.e., "Is GT-KB truly release-able as a
software product?"

Verification work in this session surfaced a load-bearing example of
rule-corpus drift (Agent Red severance language across four rule files
contradicting Agent Red's actual role as the reference adopter application).
The owner authorized a remediation for that specific drift (filed as
[bridge/gtkb-agent-red-reference-adopter-framing-restoration-001.md](../bridge/gtkb-agent-red-reference-adopter-framing-restoration-001.md))
and observed that the underlying cause was likely a mechanical-enforcement gap
that allowed contradictory language to persist in specifications and
directives. The owner indicated other rule-corpus regions may carry similar
drift, to be addressed in follow-up work.

This deliberation extends that finding to the strategic question: **how should
GT-KB cross the threshold from "pattern suite aspiring to be IDP" to "shippable
IDP with stability commitments"?**

---

## 2. Core question

> Can GT-KB project artifacts serve as the basis for a set of markdown
> documents which Claude Code could then use to create a clean-sheet version
> of GT-KB? That new clean-sheet version would be v1.0 — a stable
> binary-compatible distribution derived from everything we have learned and
> implemented so far.

**Short answer:** Yes, the artifacts you'd most want to distill
(`.claude/rules/operating-model.md`, `.claude/rules/canonical-terminology.md`,
the GOV/ADR/DCL index, the bridge-protocol rules, schema definitions, hook
contracts, the deployability-preservation-gate's scope) are already mostly
written. The distillation is curation + reconciliation, not invention.

**The substantive question** is which release-strategy path to pursue —
clean-sheet, progressive refactor, or stay-as-pattern-suite — each of which
has different costs, different end-states, and different risk profiles.

---

## 3. Current state assessment

GT-KB is currently closer to a **pattern suite aspiring to be an IDP** than to
an IDP itself. Evidence from the project's own artifacts:

1. **The operating-model artifact admits the gap.** `.claude/rules/operating-model.md`
   §3 lists several capabilities as "intended-but-partial": comprehensive
   release manifest + two-stage release validation, cross-harness enforcement
   of bridge protocol, dashboard interactive surfaces, recurring hygiene
   automation. The release-manifest specs (`GOV-RELEASE-MANIFEST-README-001`,
   `GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-001`) are candidates awaiting
   implementation bridges.

2. **Zero live adopters that aren't GT-KB itself.** The "isolation" concept
   (lifecycle independence between platform and application) is theoretical
   because there is no second application that has been ported across GT-KB
   versions. Agent Red is the *reference* adopter but shares a repository,
   git history, and development cadence with GT-KB — making portability a
   claim, not a tested invariant.

3. **Recent breaking mechanism changes.** OS poller halted 2026-04-25, smart
   poller retired 2026-05-09, role-set schema migrated from scalar to list
   form per `ADR-SINGLE-HARNESS-OPERATING-MODE-001`. Any hypothetical adopter
   installed on those mechanisms would have needed a migration story. The
   READ-accepts-legacy / WRITE-upgrades pattern is the *kind* of discipline
   an IDP needs, but it's being applied per-incident inside one repo, not as
   a versioned platform contract.

4. **The schemas underneath are still mutating.** `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH`
   ends with `memory/work_list.md` being deleted per
   `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`. The
   source-of-truth for known work is mid-migration. That's not a frozen
   schema you can ship.

5. **The rule corpus itself contained contradictions until S347.** The Agent
   Red severance-vs-reference-adopter framing inconsistency had persisted
   across four rule files and was not detected by any mechanical gate. This
   class of defect is itself a v1.0 blocker.

**What it would take to credibly release as an IDP:**

- Frozen, versioned schemas (MemBase tables, bridge file format, hook
  payloads) with migration tooling that runs on adopter upgrade.
- A release manifest + reproducible install + upgrade test matrix exercised
  on every release candidate.
- At least one external adopter (not GT-KB itself) — the platform/app
  boundary becomes real only when there's something on the other side.
- A documented stability-tier model (core surfaces guaranteed; experimental
  surfaces explicitly not).
- An explicit deprecation policy with version windows.
- A mechanical enforcement gate that prevents rule-corpus drift from
  recurring (the S347 gap).

---

## 4. Strategic options

### Option A: Full clean-sheet

1. Distill the spec corpus from current GT-KB artifacts.
2. Claude Code generates v1.0 from the spec, from scratch.
3. Agent Red ports onto v1.0; declare release.

**Headline:** maximum coherence, maximum upfront cost, identifier reset.

### Hybrid: Spec-driven progressive migration

1. Distill the spec corpus.
2. Land a mechanical enforcement gate that requires every Write/Edit
   touching a spec-governed surface to be spec-conformant.
3. Progressively refactor existing modules against the spec, one at a time.
4. v1.0 = "every module passes its spec."

**Headline:** preserves audit trail and identifiers, lower per-session cost,
longer wall-clock, sustained discipline required.

### Hybrid Variant: Platform progressive + release-layer clean-sheet

The platform internals (schemas, hooks, bridge protocol, CLI surface) refactor
progressively. The release-and-distribution layer (release manifest, stability
tiers, scaffold templates, adopter-onboarding artifacts, doctor checks for
v1.0 readiness) is built fresh against the spec, because it's new capability
anyway, not legacy code that needs preserving.

**Headline:** combines progressive safety on the existing surface with
clean-sheet design on the new surface.

### The unstated option: stay as a pattern suite

Don't ship v1.0 as an IDP. Continue developing GT-KB as a fork-at-adoption
pattern suite (Rails-generator model, Next.js create-next-app model). The
spec corpus is still produced and shipped as the canonical *pattern
description*, but the implementation remains a single moving target that
adopters fork.

**Headline:** honest about what GT-KB currently is. Loses the binary-stability
story but gains the freedom to evolve without backward-compatibility
constraints.

---

## 5. Spec corpus design sketch

Proposed structure for `gtkb-spec/` (would live in its own repo or directory,
versioned separately from any one implementation):

```
gtkb-spec/
├── README.md                              (entry point, version, reading order)
│
├── 00-overview/
│   ├── operating-model.md                 (what GT-KB does and why)
│   ├── glossary.md                        (canonical terminology)
│   ├── architecture-tiers.md              (MemBase / MEMORY.md / DA)
│   ├── implemented-vs-intended.md         (v1.0 capability state)
│   └── design-principles.md               (artifact-orientation, append-only, ...)
│
├── 10-roles-and-governance/
│   ├── roles.md                           (Owner / Prime Builder / Loyal Opposition)
│   ├── role-assignment-and-harness-identity.md
│   ├── governance-index.md                (GOV-01..N table + rationale)
│   ├── adr-dcl-protocol.md                (architecture decision discipline)
│   ├── owner-decision-channel.md          (AskUserQuestion-only enforcement)
│   ├── formal-artifact-approval.md
│   └── deliberation-protocol.md
│
├── 20-artifacts/
│   ├── artifact-taxonomy.md               (the 9+2 types, when to use each)
│   ├── append-only-versioning.md
│   ├── specification-schema.md
│   ├── work-item-schema.md
│   ├── test-schema.md
│   ├── deliberation-schema.md
│   ├── procedure-schema.md
│   ├── document-schema.md
│   ├── environment-config-schema.md
│   ├── backlog-snapshot-schema.md
│   └── assertion-run-schema.md
│
├── 30-bridge-protocol/
│   ├── file-bridge-protocol.md            (NEW/REVISED/GO/NO-GO/VERIFIED state machine)
│   ├── proposal-format.md                 (required headers, sections, target_paths)
│   ├── verdict-format.md
│   ├── prior-deliberations-section.md     (helper-pre-population contract)
│   ├── owner-decisions-section.md
│   ├── applicability-preflight.md
│   ├── clause-preflight.md
│   ├── bridge-index-format.md
│   └── dispatch-automation.md             (event-driven trigger contract)
│
├── 40-application-lifecycle/
│   ├── application-vs-platform.md
│   ├── application-isolation-contract.md
│   ├── reference-adopter.md               (the role Agent Red plays)
│   ├── application-scaffold.md            (`gt project init` contract)
│   ├── portability-validation.md
│   └── project-and-backlog.md
│
├── 50-mechanical-enforcement/
│   ├── hooks-catalog.md                   (SessionStart, PreToolUse, Stop, etc.)
│   ├── credential-scanner-catalog.md
│   ├── owner-decision-tracker.md          (prose-ask detection patterns)
│   ├── bridge-compliance-gate.md
│   ├── formal-artifact-approval-gate.md
│   ├── narrative-artifact-approval-gate.md
│   ├── implementation-start-gate.md
│   └── enforcement-vs-placement.md        (when to use which)
│
├── 60-tooling/
│   ├── gt-cli-surface.md                  (every subcommand + contract)
│   ├── python-api.md                      (KnowledgeDB class + query surface)
│   ├── doctor-contract.md
│   ├── benchmark-suite-contract.md
│   └── assertion-runtime.md
│
├── 70-release-and-distribution/
│   ├── release-manifest.md
│   ├── stability-tiers.md                 (core stable vs scaffold layer)
│   ├── deprecation-policy.md
│   ├── upgrade-path.md
│   ├── adopter-deployability-gate.md
│   └── release-candidate-gate.md
│
├── 80-session-lifecycle/
│   ├── session-startup.md
│   ├── session-wrap.md
│   ├── session-scope-and-work-subject.md
│   └── continuation-context.md
│
├── 90-test-suite/
│   ├── platform-test-discipline.md
│   ├── doctor-checks.md
│   ├── assertion-categories.md
│   └── benchmarks.md
│
├── 95-reference-adopter/
│   ├── agent-red-contract.md              (what Agent Red provides to GT-KB)
│   ├── isolation-validator-tests.md       (actual portability tests)
│   └── agent-red-binding-evidence.md      (CI bindings, deployability proofs)
│
└── 99-history/
    ├── rejected-alternatives.md           (OS poller, smart poller, prose asks, ...)
    ├── design-deltas-from-pre-1-0.md      (what changed and why)
    └── decision-archive-snapshot.md       (frozen DELIB references at 1.0 cut)
```

**Size estimate.** ~50 files, ~15K-40K lines, ~1.5M-4M tokens. Sections 30
(bridge protocol), 50 (enforcement), and 60 (tooling) carry most weight;
section 99 (rejected alternatives) is the lowest-volume but highest-leverage
section — it prevents the clean-sheet from rediscovering past failures.

**Curation cost.** First complete pass: 2-4 weeks of focused work, mostly
extraction + reconciliation from existing artifacts. The expensive part is
`99-history/rejected-alternatives.md` — that requires DA semantic search
across all sessions to surface what was tried and dropped.

**What this corpus does NOT contain:**

- Schema column orderings, regex patterns, hash algorithms, kebab-case slug
  rules, sort orders — these are *contract specifications* (behavior under
  input X is output Y), not literal source. Implementations choose their own
  representations.
- Specific DELIB-IDs / SPEC-IDs / ADR-IDs from the current implementation.
  The corpus describes *types* and *contracts*; identifier sequences reset.
- `applications/Agent_Red/` source. Agent Red itself stays separate; the
  corpus describes the *contract* between platform and reference adopter.

---

## 6. Comparison: Option A vs. Hybrid

| Dimension | **Option A: Full Clean-Sheet** | **Hybrid: Spec-Driven Progressive** |
|---|---|---|
| Phase 1 | Distill spec corpus | Distill spec corpus |
| Phase 2 | Claude Code generates v1.0 from spec | Refactor existing modules against spec, one at a time |
| Phase 3 | Agent Red ports onto v1.0; release | Each refactored module ships incrementally; v1.0 = "every module passes its spec" |
| Wall-clock to v1.0 | 8-16 weeks (estimate) | 16-32 weeks (estimate, but capability grows continuously) |
| Token/credit cost | Concentrated burst, higher peak | Distributed, lower per-session, similar or higher cumulative |
| Audit trail | Reset (DELIB-IDs become historical) | Preserved (existing IDs survive intact) |
| Active development during | Forks: parallel maintenance of legacy + v1.0 | Continuous: every change made spec-conformant first |
| Drift elimination | Total at cutover | Progressive (each module's drift cleared when refactored) |
| Agent Red migration | Big-bang dependency on v1.0 release | Each adopter benefit lands as the relevant platform module stabilizes |
| Risk of canonized accidents | Higher (everything frozen in one event) | Lower (each refactor scoped + reviewed individually) |
| Spec-implementation drift prevention | Single event then enforced afterward | Required from day 1; needs enforcement gate to land first (the S347 gap) |
| Release surface | A coherent from-scratch system, untested in the wild | A stabilized existing system that's been exercised in real use |
| Rollback semantics | All-or-nothing (1.0 ships or doesn't) | Per-module (each refactor can revert independently) |
| Owner decision load | Concentrated burst (many AUQs during cut) | Distributed across modules (fewer per session, spread across more sessions) |
| Maturity at 1.0 | Greenfield — zero adopter time on new code | Battle-tested — current implementation has been exercised in real sessions |
| Typical failure mode | "We built v1.0 and it doesn't quite work the way the spec intended" | "We never finished migration because new work outpaced refactor" |
| Reversibility if it goes wrong | Hard — once cut, going back means re-rebuilding on legacy | Easy — at any point you can stop refactoring and still have a working system |
| Strategic message to adopters | "Here's GT-KB v1.0, designed deliberately" | "GT-KB has matured into v1.0 through continuous spec-driven evolution" |

---

## 7. The fundamental tradeoff

It is NOT "clean implementation vs. accumulated technical debt." Both options
clean up technical debt; both produce a coherent v1.0.

It IS: **binary-stable IDP with reset identifiers and a one-shot release
event** vs. **continuous spec-driven evolution with full audit trail and
incremental stabilization.**

Frame the choice by asking: **does a clean v1.0 baseline matter more than
continuity with the decision history you've accumulated?**

- If clean baseline: **Option A**. Pay the upfront cost, accept the identifier
  reset, ship a deliberate v1.0.
- If continuity: **Hybrid**. Land the enforcement gate first, then progressively
  refactor.

---

## 8. Additional considerations, tips, and warnings

### 8.1 The mechanical-enforcement gate is a prerequisite to either path

S347 surfaced that contradictory rule-corpus language can persist undetected
across many rule files for an extended period. Both Option A and Hybrid
require a gate that prevents this from recurring:

- **Option A** needs it post-cutover so v1.0 doesn't drift from spec.
- **Hybrid** needs it from day 1 so every change to legacy code is
  spec-conformant.

The gate concept: a `PreToolUse` Write/Edit hook that, for any file declared
spec-governed, validates the proposed write against the spec's contract
assertions. Failure → block the write with a structured remediation message.

**Suggested first concrete action regardless of A/Hybrid choice:** scope a
bridge proposal for this gate. Until it exists, drift accumulates whether or
not v1.0 work proceeds.

### 8.2 Model evolution between v1.0 cut and later maintenance

The Claude model that builds v1.0 in 2026-05 is not the same model that will
maintain it in 2027-02. Choices that feel natural to one model generation may
feel awkward to another. **Mitigations:**

- Lean on the spec corpus, not on what feels natural to the current model.
  The spec is the contract; the model is one of many possible implementations.
- Keep the spec corpus model-agnostic. Avoid prose like "Claude prefers..."
  or "Codex tends to..." — those are observations, not specifications.
- Include explicit model-independence tests: can a different model (or the
  same model in a different session) produce verified output from the spec?

### 8.3 The "perpetual rc1" risk under Hybrid

Hybrid's failure mode is that new work outpaces refactoring, and v1.0 never
quite ships because some module isn't done. **Mitigations:**

- Define v1.0 acceptance criteria explicitly and early — a concrete checklist
  of modules and their spec-conformance state.
- Cap the refactor backlog: no new feature work that doesn't either pass its
  spec OR have a spec-conformance refactor scheduled within N sessions.
- Treat the v1.0 cut as a release event, not a state of being. Pick a date,
  ship what's spec-conformant, declare the rest experimental.

### 8.4 Identifier reset blast radius (Option A specific)

If you choose Option A, DELIB-IDs / SPEC-IDs / ADR-IDs / bridge thread
numbering all reset. Things that break:

- Any commit message that cites a current ID (`git log --grep` to find them
  before the cut).
- Any external documentation, training material, or owner-shared notes that
  reference current IDs.
- Agent Red's `.gtkb-app-isolation.json` and bridge thread history that cite
  current DELIB-IDs as authority.
- The Deliberation Archive's role transitions from "live system" to "frozen
  provenance store at v1.0 cut."

**Mitigation:** publish a one-time **identifier-translation manifest** at the
v1.0 cut: mapping old IDs to new IDs (or to "retired without replacement").
Keep the manifest discoverable from the spec corpus's `99-history/`.

### 8.5 Reference adopter cadence post-v1.0

For Agent Red to genuinely validate isolation, it needs to:

1. Stay on a release behind the platform's `develop` (so the platform can
   evolve without breaking the adopter immediately).
2. Periodically upgrade to a new platform version (exercising the upgrade
   path that adopters will use).
3. Re-validate isolation after every platform schema or contract change.

**Without this cadence, the isolation validator role is theoretical.** Define
the cadence explicitly in the spec corpus's `95-reference-adopter/` section.

### 8.6 Corpus governance after v1.0

Once the spec corpus exists, who owns changes to it? Some options:

- **Bridge protocol governs spec changes** — clean but creates a bootstrap
  dependency (specs about the bridge protocol governed by the bridge protocol
  they specify).
- **Parallel governance** — separate approval system for spec changes. Splits
  governance and creates risk of divergence.
- **Promotion model** — spec changes start as bridge proposals, get approved,
  get committed to a separate spec-corpus repo with its own versioning. Bridge
  protocol governs the proposal; spec-corpus repo governs the artifact.

The promotion model is probably right but needs to be deliberated explicitly
before v1.0.

### 8.7 Stability tiers — not all of GT-KB needs the same compatibility commitment

A useful pattern: separate the v1.0 surface into stability tiers:

- **Stable core**: schemas, bridge file format, hook payload contracts, `gt`
  CLI surface, Python API. Backward-compatibility guarantees apply.
- **Scaffold layer**: templates, rules, skills, named hooks. Adopters fork
  these at `gt project init` and own them from that point forward. No
  cross-version compatibility commitment.
- **Experimental**: explicitly marked surfaces (e.g., dashboard interactive
  features, single-harness operating mode). Can change freely between versions.

This pattern (used by Rust nightly/stable channels, Kubernetes API versioning,
Next.js stable/experimental) gives you a credible v1.0 without committing to
backward-compat on everything.

### 8.8 The "specs as aspiration" anti-pattern

A real risk under Option A: the spec corpus encodes things the implementation
*should* do but currently doesn't, in language that reads as if they're done.
Then Claude Code builds an implementation that claims to do them, but doesn't.

**Mitigation:** every contract assertion in the spec corpus has a verifiable
test in the test-suite section. If you can't write a test that fails when the
contract is violated, the contract isn't specified — it's aspiration. Mark
aspirational surfaces explicitly and section them off in
`00-overview/implemented-vs-intended.md`.

### 8.9 The Loyal Opposition role during transition

Under either option, Loyal Opposition reviews the spec corpus + the
implementation work. Decide explicitly:

- Does LO use the spec corpus as its review authority? (probably yes)
- What happens if LO finds the spec is wrong, not the implementation?
- Does LO have authority to NO-GO an implementation that satisfies the spec
  but does so badly?

Without these decisions, the bridge protocol becomes ambiguous during the
transition.

### 8.10 What "isolation validator" actually validates

Agent Red's role as the isolation validator is only meaningful if there's a
concrete test of the form: "Install GT-KB version V on fresh environment E,
install Agent Red on top, verify Agent Red still operates correctly."

This test does not currently exist. Building it is itself v1.0 prerequisite
work. The test forces every implicit cross-cutting dependency (Python version,
OS expectations, file paths, environment variables, third-party services) to
become explicit in the spec corpus.

### 8.11 Cost visibility — what does this actually cost?

Rough order-of-magnitude estimates (very approximate):

| Activity | Token cost | Calendar cost |
|---|---|---|
| Spec corpus distillation, first pass | 5-15M tokens | 2-4 weeks |
| Option A: clean-sheet generation | 30-100M tokens | 8-16 weeks |
| Option A: convergence iteration | 20-50M tokens | additional 4-8 weeks |
| Hybrid: per-module refactor | 2-5M tokens per module | 1-3 weeks per module |
| Hybrid: enforcement gate + initial framework | 5-10M tokens | 2-4 weeks |
| Agent Red v1.0 port (Option A only) | 10-30M tokens | 4-8 weeks |

Both options are significant resource commitments. Hybrid is lower per-event
but longer overall. Option A is higher per-event but produces a definite end
state.

### 8.12 Lessons from prior systems

Examples worth studying when continuing this deliberation:

- **Rails generators (clean-sheet at adoption + stable runtime)**: the
  `rails new` generator scaffolds; the Rails runtime gets upgraded. Adopters
  customize the scaffold and own it. Stable core + scaffold-fork pattern.
- **Next.js create-next-app**: same pattern. Templates fork; framework
  upgrades.
- **Kubernetes API versioning**: alpha/beta/stable tiers; explicit
  deprecation windows; conversion webhooks for schema migrations. Heavy but
  proven IDP discipline.
- **Rust edition system**: backward compatibility across editions; opt-in
  migration. Demonstrates that "binary compatible across versions" and
  "language continues evolving" are not mutually exclusive — you just need
  the discipline.
- **Postgres major-version upgrades**: full dump+restore between major
  versions. Demonstrates that perfect online migration is not always
  required — a documented offline migration path can be acceptable for an
  IDP.

### 8.13 The "stay as pattern suite" option is not failure

Releasing GT-KB as a versioned pattern suite (no binary-compatibility
guarantees, adopters fork at adoption time, future evolution is informational
not required) is a legitimate end-state. It is honest about what GT-KB
currently is, removes the constraint of cross-version compatibility, and lets
the project continue to evolve freely.

The cost: no commercial "IDP" framing, no adopter portability story, no
release-as-product narrative.

Reframing decision: it is not "ship v1.0 or fail." It is "choose the
distribution model that matches what GT-KB is and what you want it to be."

### 8.14 Spec-corpus distribution shape

The spec corpus could be distributed in multiple forms:

- **As a separate repository** (e.g., `groundtruth-spec`) — adopters and
  alternative implementations consume it directly.
- **As a documentation site** — published HTML, browseable.
- **As a versioned PyPI package** — installable alongside `groundtruth-kb`
  to provide spec lookups and validation tooling.
- **As an MCP server** — queryable by AI agents at runtime.

The choice affects how implementations reference the spec. The MCP-server
option is interesting because it would allow Claude Code to query the spec
during implementation work, but it's also v1.0+ work.

### 8.15 Warning: do not start clean-sheet generation before the spec corpus is stable

The most common failure mode in this kind of work is that generation begins
before the spec is solid. The result: Claude Code implements something, the
spec catches up to describe what was built, and the spec becomes a
post-hoc rationalization rather than a contract.

**Discipline:** complete the spec corpus first pass, then have it reviewed
(by Loyal Opposition, by the owner, ideally by a third party), then
generate. The temptation to "start coding and write the spec as we go" is
strong. Resist.

### 8.16 The cleanse-of-historical-artifacts question (deferred, but related)

The owner identified in S347 that there are likely other rule-corpus regions
contaminated by language that wasn't explicitly approved. A systematic cleanse
is implied as follow-up work.

This cleanse is **strongly related** to the spec corpus production: the
distillation process necessarily surfaces all rule-corpus contradictions
because the spec corpus must reconcile them. Treating "produce the spec
corpus" and "cleanse the rule corpus" as overlapping work streams is
probably more efficient than treating them as sequential.

**Suggestion:** the spec corpus distillation IS the cleanse. Don't run them
separately.

---

## 9. Open questions for the owner

The following decisions are unresolved as of this snapshot. Resuming the
deliberation should start by answering these:

1. **Strategic priority — clean baseline vs. continuity?**
   Which matters more for what you intend GT-KB to become?

2. **Is there an external commitment that forces a date?**
   Commercial commitments, partner integrations, public release deadline,
   demos? If yes, that may force Option A timing or Hybrid pace.

3. **Agent Red lifecycle synchronization to GT-KB v1.0?**
   Should Agent Red migrate as a v1.0 release-gate dependency, or
   independently after v1.0 is stable?

4. **Resource availability?**
   The token costs are real; both options are significant. Is the budget
   bounded?

5. **Stay-as-pattern-suite as a serious option?**
   Is releasing GT-KB as a versioned pattern suite (no binary-compatibility
   guarantees) an acceptable end-state, or is the IDP framing essential to
   what GT-KB is meant to become?

6. **Spec corpus distribution shape?**
   Separate repo, doc site, PyPI package, MCP server, or some combination?

7. **Corpus governance after v1.0 — who approves spec changes?**
   Bridge protocol governs, parallel governance, or promotion model?

8. **Stability tiers — explicit?**
   Adopt the stable-core / scaffold-fork / experimental three-tier model, or
   commit to backward compatibility on a flatter surface?

---

## 10. Suggested actions independent of option choice

These actions have value regardless of the eventual A / Hybrid / pattern-suite
decision. Consider executing them as preparation:

1. **Scope and land the mechanical-enforcement gate.** Bridge proposal for a
   PreToolUse hook that validates Write/Edit operations against
   spec-governed surfaces. Prerequisite to both options; would have prevented
   the S347 Agent Red drift.

2. **Begin the spec corpus distillation NOW.** First pass on
   `00-overview/`, `10-roles-and-governance/`, `30-bridge-protocol/`, and
   `99-history/rejected-alternatives.md`. These are valuable as
   documentation even if v1.0 never ships.

3. **Define v1.0 acceptance criteria explicitly.** A concrete checklist:
   "v1.0 ships when all of the following are true." Without this, both options
   can drift indefinitely.

4. **Build the isolation validator test.** "Install GT-KB version V on fresh
   environment E, install Agent Red on top, verify Agent Red operates
   correctly." This test is the operative measure of portability.

5. **Audit the rule corpus for other contradictions like the Agent Red one.**
   Systematic search for: drift between rules and implementation, severance
   language that may not have been explicitly approved, mechanism references
   to retired infrastructure, terminology variants that may indicate
   conceptual confusion. Treat this as the start of the cleanse work the
   owner deferred in S347.

6. **Decide stability-tier model.** Even before v1.0, knowing which surfaces
   are intended-stable vs intended-experimental shapes day-to-day decisions.

---

## 11. How to resume this deliberation

When picking this up later:

1. **Read this document.** It captures the full deliberation state as of
   2026-05-24 (S347).

2. **Check the related bridge thread.** [bridge/gtkb-agent-red-reference-adopter-framing-restoration-001.md](../bridge/gtkb-agent-red-reference-adopter-framing-restoration-001.md)
   should have a Loyal Opposition verdict (GO or NO-GO) by then. The outcome
   may inform the broader cleanse strategy.

3. **Check for new evidence of drift.** Run a fresh audit of rule files
   against implementation. New contradictions since S347 inform the urgency
   of the enforcement gate.

4. **Answer the open questions in §9.** The strategic-priority question
   (§9.1) is the highest-leverage; most of the other questions become
   tractable once that one is answered.

5. **Decide first concrete action.** Options:
   - Land the enforcement gate (suggested as first action regardless of path).
   - Begin spec corpus distillation (suggested in parallel).
   - File a v1.0-acceptance-criteria bridge proposal.
   - Reject all of the above; defer indefinitely; continue current development.

6. **If proceeding, file the relevant bridge proposal.** Per
   `.claude/rules/codex-review-gate.md`, no implementation work begins
   without a bridge GO. The spec corpus distillation work, the enforcement
   gate work, and any v1.0 milestone work all need bridge proposals before
   implementation.

---

## Appendix A: Source conversation summary

This deliberation spanned six conversational turns in session S347:

1. **Owner asked** whether a markdown spec set could be sufficient for
   Claude Code to implement GT-KB clean-sheet without other artifacts.
2. **Owner asked** whether GT-KB is truly release-able as a software product
   (IDP vs. pattern suite framing).
3. **Owner challenged** the Agent Red severance framing as inconsistent with
   stated intent; requested verification.
4. **Verification surfaced** rule-corpus contradiction across four rule files;
   owner authorized remediation; bridge proposal filed at
   [bridge/gtkb-agent-red-reference-adopter-framing-restoration-001.md](../bridge/gtkb-agent-red-reference-adopter-framing-restoration-001.md).
5. **Owner asked** about clean-sheet derivation from current artifacts;
   advantages/limitations comparison requested.
6. **Owner requested** the spec corpus sketch and the Option A vs. Hybrid
   comparison.
7. **Owner requested this document** to enable later resumption.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
