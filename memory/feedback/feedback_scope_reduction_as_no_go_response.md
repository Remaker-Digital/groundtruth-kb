---
name: Scope reduction as NO-GO response
description: When a Codex NO-GO surfaces "you're claiming more than evidence supports", the cheapest correct response is often "claim less" — not "find better evidence". Especially valuable when the omitted claims have a clear future-bridge home. S315.
type: feedback
originSessionId: fddf9153-45fe-43c8-85b2-b5b0abe4ad43
---
When Loyal Opposition issues a NO-GO that boils down to "your design rests on an asserted-but-unevidenced primitive" or "your scope crosses an architectural boundary you don't control", the instinct is to defend the proposal by adding evidence or expanding the design. **Often the better move is to scope down — remove the unevidenced claims entirely, defer them to a follow-on slice gated on the missing evidence, and ship a smaller artifact that's honest about what it can prove.**

**Why:** S315 produced two examples on consecutive Codex rounds.

**Example 1 — P2 registry REVISED-1 → REVISED-2:**

`-004` NO-GO findings:
- F1: Asserted `CLAUDE_HARNESS_PID` / `CODEX_HARNESS_PID` env vars exist. Source-verified absent in `.claude/settings.json` and `.codex/hooks.json`.
- F2: Process-name allowlist (`node`, `code`) catches wrappers, not actual harnesses.

Codex's two options:
1. Make harness-PID primitive a P2.5 prerequisite + cite captured evidence.
2. Scope P2 down to static registration only; defer live/stale classification.

I took option 2. Result: REVISED-2 dropped ~130 LOC, deleted the heartbeat module entirely, removed the `psutil` dependency, cut 26 tests to 10-12. **GO at `-006` on the first review of REVISED-2.** The deferred liveness work has a clean future-slice home gated on the P2.5 spike that's already in flight.

Had I taken option 1 (defend the env-var design with better evidence), I would have:
- Filed a sub-spike just to verify env-var existence, OR
- Added more fallback chains and process-validation logic, OR
- Argued the proposal's defaults were "good enough"

Each of those takes more cycles, more LOC, and more review surface. The scope cut shipped faster AND produced a more honest artifact.

**Example 2 — GH-002 NEW → REVISED-1:**

`-002` NO-GO finding F1: Sub-feature A's `--allowed-cross-repo-roots` argparse flag for the generator alone wouldn't help — the audit-hook RUNNER (in a different file: `_dashboard_regen_runner.py`) enforces its own path policy. Single-layer fix can't satisfy a two-layer enforcement.

Codex's two options:
1. Split §B into its own bridge so it can proceed independently.
2. Keep both bundled, but revise §A to include runner-side allowlist plumbing.

I took option 1. §A parked pending runner architecture work; §B (Type F harness-home reads) became the sole REVISED-1 scope. The bridge is now implementable without coupling to the runner-side architecture.

(Note: GH-002 §B-only REVISED-1 then got its own NO-GO at `-004` for test rigor, but that's a separate concern — the scope reduction itself was correct; the test contract needed tightening.)

**How to apply:**

When a Codex NO-GO Required-Revision section offers numbered options AND one of them is some variant of "scope down / split out / defer / static-only / read-only", treat it as the strong default unless:

1. The narrowed scope leaves the work substantively useless on its own. (Counter-example: scoping P1 detector to "parser only, no diff" would have left nothing useful.)
2. The deferred work has no clear future-bridge home — i.e., it would be parked indefinitely.
3. The owner has explicitly indicated the broader scope is a hard requirement.

Otherwise: **prefer the smaller honest artifact over the larger defended one**. The Codex review cycle is faster, the implementation surface is smaller, the audit trail is cleaner, and the deferred work is explicitly tracked.

**Anti-pattern to avoid:** Don't argue with the NO-GO when the gap is real. The reflex is "but my design is correct in principle / will work eventually / has good intent" — none of which satisfies a verification gate. If you can't satisfy the gate as written, either amend the gate explicitly (rare and requires its own justification — see GH-001 `-007` REVISED-1) or scope down.

**Related:**
- `feedback_verify_source_before_parallel_proposals.md` — the upstream lesson; would have caught the P2 env-var assertion before it reached Codex.
- `feedback_no_deferrals_ever.md` — the apparent tension; resolved by noting that scope reduction with a tracked follow-on bridge is NOT a deferral, it's an honest sequencing decision. The deferred work is captured, not dropped.
- `feedback_dont_re_elicit_on_agreement.md` — when the scope-down option is offered explicitly by Codex, take it; don't re-ask the owner to confirm.
