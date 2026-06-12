---
name: Weight multi-harness peer review by demonstrated reliability
description: Relayed peer-review input (especially from lower-reliability or non-registered harnesses such as Gemini) is a hypothesis, not a finding — canon-verify every load-bearing claim against MemBase/specs/rules/git before adoption. Convergence across reasoners is not correctness; multiple reasoners diverging from the spec the same way may be a shared prior/anchor/verification-miss, not a better design. Owner: "Gemini is less capable" (2026-06-12).
type: feedback
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 46dbd0f7-6e3d-42b4-81bf-2c2432324069
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style, interactive Prime Builder session
---

Treat multi-harness peer review as evidence weighted by demonstrated reliability, and gate lower-capability or relayed input through canon-verification before adopting any load-bearing claim.

**Why:** The 2026-06-12 skill-naming + explicit-hint-layer analysis ran the same task past Prime (Claude), Codex, and Gemini. Owner: "Gemini is less capable." Evidence bore it out:

- **Gemini** required correcting three false premises against canon: an invented `config/agent-control/topic-envelopes.toml` (canon stores topics in the session-envelope JSON `topics array` per `DCL-SESSION-ENVELOPE-DURABILITY-001`); free-form `::open Fable/FAB-01` (canon vocabulary is the closed `{spec,build,test,deliberation,project}` per `SPEC-TOPIC-ENVELOPE-ROUTER-001`); and a flat-vs-stack nesting binary that ignored the canonical type-keyed one-per-type model.
- **Codex** was mostly accurate refinement and caught a real defect Prime had missed: the init-keyword `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 regex `^::init (gtkb|application)( (pb|lo))?$` vs the stale glossary form `^::init gtkb (pb|lo)$`.
- Gemini is **not** a registered GT-KB harness (`harness-state/harness-registry.json` = Claude B, Codex A, Antigravity C, Ollama D) and holds no bridge verdict authority; relayed Gemini/peer input is advisory only, never a `GO`/`NO-GO`.

**How to apply:**

1. Treat relayed peer-review — especially from lower-reliability or non-registered harnesses — as **hypotheses, not findings.** Canon-verify every load-bearing claim against MemBase/specs/rules/git before adoption (the interrogative default, applied to peers as well as to the owner).
2. **Convergence ≠ correctness.** When multiple reasoners diverge from the spec the same way, do not conclude the spec is wrong by vote. Canon-verify: it may be a shared linguistic prior, a shared anchor (one reasoner's illustrative example anchoring the others), or a shared verification-miss — OR a genuine spec-*surface* defect. Only canon-verification distinguishes "agents mis-keyed" from "spec mis-signals." (Here: three reasoners collapsed the *type* and *subject* axes into one `::open` token because "topic" reads as "subject"; the spec actually models subject as a payload field on a typed open — substance sound, surface misleading.)
3. **Weight by demonstrated reliability, not by source, confidence, or count.** On this task Codex > Gemini by evidence, not by default standing.
4. **Keep the value.** A low-reliability peer still earns its place by forcing implicit decisions into the open (Gemini forced the topic-envelope interception-model decision to be made explicit). Extract the question; discard the flawed framing.

Related: `feedback_verify_source_before_parallel_proposals.md` (same family — verify against the canonical source before acting).
