NO-GO

# Loyal Opposition Review - GTKB-GOV-TERM-DISAMBIGUATION-MECHANICAL Scoping Proposal

Reviewer: Codex (Loyal Opposition)
Date: 2026-05-02
Reviewed proposal: `bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-001.md`
Verdict: NO-GO

## Claim

The owner problem is real and the proposed direction is broadly aligned with GT-KB's deterministic-services principle. The proposal is not ready for GO because it is built on an incorrect live path for the canonical terminology config, omits the prior canonical-terminology bridge history that settled that path, depends on a sibling term-primer proposal that is currently NO-GO, and leaves implementation-critical policy choices unresolved.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched the Deliberation Archive before review for term disambiguation, canonical terminology, backlog, `DELIB-S327`, and `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.

Relevant results:

- No existing deliberation rows were found for `TERM DISAMBIGUATION` or `DELIB-S327`; those S327 owner-directive records appear to still be candidates, as the proposal states.
- `DELIB-1180`, `DELIB-1179`, `DELIB-1018`, `DELIB-1017`, `DELIB-0804`, and `DELIB-0722` reference the earlier canonical-terminology bridge threads.
- `DELIB-S324-OM-DELTA-0004-CHOICE` confirms backlog ordering semantics.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` flags MemBase/backlog/bridge source fragmentation.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports converting repetitive AI recall/plumbing into deterministic services.
- `DELIB-1404` is related to candidate-vs-approved specification wording, as Prime noted.

The proposal's cited deliberations are relevant, but the prior canonical-terminology bridge thread is materially relevant and missing from the proposal's analysis.

## Findings

### F1 - Blocking: proposal cites and extends the wrong canonical terminology config path

Evidence:

- The proposal cites `groundtruth-kb/templates/project/canonical-terminology.toml` as the scaffolded required-terms matrix and proposes extending it in Slice 1 (`bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-001.md:32`, `:187`, `:263`).
- Live file check: `groundtruth-kb/templates/project/canonical-terminology.toml` does not exist.
- The live managed template paths are `groundtruth-kb/templates/rules/canonical-terminology.md` and `groundtruth-kb/templates/rules/canonical-terminology.toml`.
- The live TOML file is a profile-aware doctor config with `[config.profiles.*]` and `required_startup_terms`, not a `[term."..."]` table schema (`groundtruth-kb/templates/rules/canonical-terminology.toml:1` through `:50`).
- The earlier verified canonical-terminology implementation explicitly settled the registry-backed Option B path under `.claude/rules/` and templates/rules, not `templates/project`: `bridge/gtkb-canonical-terminology-surface-implementation-012.md`.

Risk/impact:

Implementing against the proposed path would either fail immediately or create a parallel terminology configuration surface outside the managed template contract. That would worsen the fragmentation this proposal is trying to fix.

Recommended action:

Revise the proposal to use the existing managed surface:

- template source: `groundtruth-kb/templates/rules/canonical-terminology.toml`;
- scaffold target: `.claude/rules/canonical-terminology.toml`;
- managed registry record: `rule.canonical-terminology-config`;
- doctor/check integration that composes with the existing profile-aware config instead of replacing it with an incompatible `[term.*]` schema.

If a new term-policy schema is still needed, specify it as an explicit schema migration or sibling config file and explain how it avoids parallel authority.

Decision needed from owner:

None. This is Prime-fixable.

### F2 - Blocking: prior canonical-terminology bridge history is omitted

Evidence:

- The proposal's `Prior Deliberations` section cites backlog, MemBase, candidate-spec, and S327 primer records (`-001.md:36` through `:53`).
- It does not cite the existing canonical-terminology bridge work, despite live Deliberation Archive rows for that topic and existing bridge files `bridge/gtkb-canonical-terminology-surface-*.md`.
- `bridge/gtkb-canonical-terminology-surface-002.md` approved a governed terminology record plus startup, template, doctor, and bridge-gate propagation.
- `bridge/gtkb-canonical-terminology-surface-implementation-012.md` verified the Option B implementation and records the current managed-rule architecture.

Risk/impact:

The proposal reopens a terminology-governance surface without carrying forward the already-verified architecture. That is how the wrong `templates/project` path entered the design, and it could lead to duplicate doctor checks, duplicate TOML schemas, or stale startup surfaces.

Recommended action:

Add a prior-deliberations subsection for the canonical-terminology surface thread. State which parts are preserved, which parts are extended, and which parts are superseded. In particular, reconcile this proposal with the Option B registry-backed contract from `gtkb-canonical-terminology-surface-implementation-012.md`.

Decision needed from owner:

None. This is Prime-fixable.

### F3 - Blocking: dependency on the term-primer sibling is not currently safe

Evidence:

- The proposal says it is coupled with `DELIB-S327-TERM-PRIMER-STARTUP` and that the primer is "necessary input" (`-001.md:52`).
- It maps the primer proposal to "all" tests (`-001.md:261`) and uses the primer's 22+ owner-required terms as an acceptance criterion (`-001.md:188`).
- The live bridge index currently shows `gtkb-gov-term-primer-startup-2026-05-02` latest status is `NO-GO`, not `GO`.

Risk/impact:

This disambiguation proposal may implement enforcement against a primer shape that has not been approved. If the primer revision changes term coverage, file paths, loading path, or source-of-truth rules, this proposal's tests and acceptance criteria can become stale before implementation begins.

Recommended action:

Either:

1. make the term-primer GO an explicit precondition for this proposal, then resubmit after the primer revision is approved; or
2. make this proposal self-contained by defining the minimum term set, source path, and schema contract independently of the unresolved sibling.

Decision needed from owner:

None yet. Prime can choose either revision path.

### F4 - Blocking: implementation-critical open decisions are not pinned

Evidence:

- Open Decision A controls Tier B severity and whether bridge proposals block or warn (`-001.md:221`).
- Open Decision B controls the override syntax that tests T7 and the hook behavior depend on (`-001.md:223` through `:227`).
- Open Decision C controls Tier C strictness (`-001.md:229`).
- Open Decision D controls whether forbidden-use matches always block (`-001.md:231`).
- Open Decision F controls sentence-initial capitalization behavior (`-001.md:239`).
- Open Decision G controls file-level disable behavior (`-001.md:241`).
- The proposed tests and acceptance criteria require these choices to be implemented (`-001.md:176`, `:178`, `:180`, `:191`, `:194`).

Risk/impact:

A GO would authorize implementation while core behavior is still undefined. Different implementers could reasonably choose different severity, override, heuristic, and file-disable semantics, making the eventual verification target unstable.

Recommended action:

Revise the proposal to pin defaults for A, B, C, D, F, and G in the proposal itself, or mark the unresolved choices as a single required owner decision before GO. Suggested defaults in the proposal can be adopted, but they need to become proposed requirements rather than open questions.

Decision needed from owner:

Only if Prime cannot pin defaults under existing owner direction. If owner input is needed, ask one decision at a time before resubmitting.

## Verification

Commands and checks performed:

- Read harness-local role record: `harness-state/codex/operating-role.md`; active role is `loyal-opposition`.
- Read live `bridge/INDEX.md`; selected entry's latest status was `NEW`, actionable for Loyal Opposition.
- Read `.claude/rules/file-bridge-protocol.md`, `.claude/rules/project-root-boundary.md`, `.claude/rules/deliberation-protocol.md`, and `.claude/rules/operating-model.md`.
- Read the selected proposal in full: `bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-001.md`.
- Queried `groundtruth.db` deliberations for term disambiguation, canonical terminology, backlog, `DELIB-S327`, and `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.
- Searched live files for canonical terminology config paths and read the existing template files under `groundtruth-kb/templates/rules/`.
- Read prior canonical-terminology bridge review/verification files.
- Read the latest NO-GO for the sibling backlog proposal and the sibling term-primer proposal to confirm dependency state.

I did not run pytest or ruff because this is a scoping/design proposal with no implementation changes to verify.

## Required Revision

Resubmit as `bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-003.md` with:

1. The correct canonical terminology config path and schema strategy.
2. Explicit reconciliation with the verified canonical-terminology surface bridge thread.
3. A safe dependency model for the currently NO-GO term-primer sibling.
4. Pinned implementation defaults or a pre-GO owner decision path for the open policy choices.

After those changes, the proposal is likely reviewable for GO.

