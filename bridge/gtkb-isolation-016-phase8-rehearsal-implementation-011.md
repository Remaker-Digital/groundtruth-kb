REVISED

# GTKB-ISOLATION-016 — Phase 8 Agent Red Migration Rehearsal (Implementation, Revision 5)

**Status:** REVISED (architectural correction; awaiting Codex re-review)
**Date:** 2026-04-26 (S310)
**Work item:** GTKB-ISOLATION-016
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** implementation_proposal
**Supersedes citation:** binding content remains `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-005.md` (REVISED-2) and `-009` (REVISED-3) per their prior incorporation; this `-011` revises one architectural point and one safety-rule point only.
**Addresses:** owner architectural correction during S310 (post-`-010` GO, pre-Wave 1)

bridge_kind: implementation_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: isolation_rehearsal
requires_review: true
requires_verification: true

---

## 0. What This Revision Addresses

After Codex GO at `-010` and the `§3.1` AskUserQuestion in S310, the
owner identified an architectural error in the question's option set:
all three offered candidates (`E:\agent-red-app\`,
`E:\Claude-Playground\agent-red-app\`, a different drive) treated
GT-KB and Agent Red as siblings on the filesystem. The IDP model in
`CLAUDE.md` requires applications to live inside the platform
(`<gt-kb-root>/applications/<name>/`), not as siblings.

Owner's load-bearing concern: the cross-root sibling model has not
been validated. Harness-adjacent infrastructure (`.claude/`,
`.codex/`, `groundtruth.db`, `bridge/`, dashboard, hooks, skills) all
resolve from the project root via `Path(__file__).resolve().parents[N]`.
Whether any of that works when an app runs from a path that doesn't
have GT-KB at root is untested. The first migration must not take
that bet.

This revision changes:

1. **§3.1 target child root path** — corrected from sibling
   candidates to `<gt-kb-root>/applications/Agent_Red/`. The
   AskUserQuestion's `E:\agent-red-app\` answer is superseded; the
   correct path is `E:\GT-KB\applications\Agent_Red\` on the active
   developer machine.
2. **§2.1 hard refusal logic** — refined. The original "refuse if
   target inside legacy mixed root" check would have blocked the
   IDP-correct target, since `applications/Agent_Red/` is inside
   `E:\GT-KB\`. The refusal must now distinguish the *conflated*
   legacy state (root-level Agent Red surfaces) from the *canonical*
   new namespace (`applications/<name>/`).

Strategic direction (zero-destructive rehearsal, eleven sub-script
lanes, owner-decision-by-wave sequencing) is preserved unchanged from
`-005`/`-009`.

## 1. Architectural Anchor (NEW §1.3)

The convention "adopter applications live at
`<gt-kb-root>/applications/<name>/`" is the canonical IDP model
implied by `CLAUDE.md`'s GT-KB definition and required by Phase 9
productization (`gt project init <name>` mechanically lands the new
project under `applications/<name>/`).

This revision cites the convention as **pending formal ADR**
(`ADR-ISOLATION-APPLICATION-PLACEMENT-001`). The ADR itself is
deferred to GTKB-ISOLATION-009 productization where the convention
becomes mechanically enforced via `gt project init`. Until the ADR
lands, this revision treats the convention as the binding rehearsal
target via owner-decision capture in S310.

The Agent Red rehearsal is the first conformant adopter migration.
What this rehearsal does establishes the template every future
adopter follows. Getting this right now matters more than getting it
fast.

## 2. Codex Re-Review Compliance

This revision does not introduce new finding categories. It corrects
one architectural premise and one safety-rule scope. Codex's prior
findings F1, F2, F3, F4 from `-002` remain addressed per `-003`/`-005`
and are unaffected.

## 3. CORRECTED §3.1 Target Child Root

Original `-001` §3.1 (binding via `-005` "unchanged"):

> Target child root path. Phase 2 outcome. Candidates: a sibling
> directory under `E:\Claude-Playground\` (e.g.,
> `E:\Claude-Playground\agent-red-app\`), a fresh top-level workspace,
> or an entirely different drive. Affects sandbox isolation guarantees.

**Revised §3.1:**

> Target child root path. Convention: `<gt-kb-root>/applications/<name>/`
> per pending `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.
>
> For the active Agent Red rehearsal:
> `target_root = E:\GT-KB\applications\Agent_Red\`
>
> The legacy mixed root remains `E:\GT-KB\` itself (where Agent Red
> root-level surfaces currently live conflated with GT-KB
> infrastructure). The target child root is a strict descendant of
> `<legacy-root>/applications/<name>/`, distinct from any of the
> conflated root-level Agent Red surfaces (`src/`, `admin/`,
> `bridge/`, `tests/`, etc.).
>
> Owner-decision in S310 (2026-04-26): confirmed.

The owner's prior AskUserQuestion answer (`E:\agent-red-app\`) is
**superseded** by this revision. The session-level audit trail in
`memory/pending-owner-decisions.md` will reference this `-011` as
the architectural correction.

## 4. CORRECTED §2.1 Hard Refusal Logic

Original `-001` §2.1 hard refusal conditions (binding via `-005`):

> 1. `--target-root` resolves inside the legacy mixed root.
> 2. Any output path resolves outside `--target-root` or the
>    rehearsal output directory.
> 3. Pre-run hash set of legacy root differs from a stored baseline
>    AND `--accept-drift` is not passed.

Condition 1 conflicts with the IDP-correct target (which IS inside
`<gt-kb-root>/`). **Revised condition 1:**

> 1. `--target-root` resolves to one of:
>    a. The legacy mixed root itself (`<gt-kb-root>/` exactly).
>    b. Any *conflated root-level Agent Red surface* — a directory
>       at `<gt-kb-root>/<name>/` where `<name>` matches the
>       enumerated conflated set: `src/`, `admin/`, `bridge/`,
>       `tests/`, `docs/`, `infrastructure/`, `extensions/`,
>       `tools/`, `evaluation/`, `assets/`, `branding/`, `legal/`,
>       `prototype/`, `pacts/`, `output/`, `test_host/`,
>       `test-results/`, `node_modules/`, `tmp/`, `archive/`,
>       `independent-progress-assessments/`, `drafts/`, `img/`,
>       `logs/`, `agent-red.wiki/`, `docs-site/`, `config/`,
>       `memory/`.
>    c. The `<gt-kb-root>/applications/` parent directory itself
>       (target must be a *named child* under `applications/`, not
>       the parent).
>
>    The driver MAY accept any path under
>    `<gt-kb-root>/applications/<name>/` where `<name>` is a valid
>    identifier (matches `^[A-Za-z][A-Za-z0-9_-]*$`).

Conditions 2 and 3 are unchanged from `-005`.

The conflated-surface list is encoded as a constant in
`scripts/rehearse/_common.py`:

```python
LEGACY_CONFLATED_SURFACES: frozenset[str] = frozenset({
    "src", "admin", "bridge", "tests", "docs", "infrastructure",
    "extensions", "tools", "evaluation", "assets", "branding",
    "legal", "prototype", "pacts", "output", "test_host",
    "test-results", "node_modules", "tmp", "archive",
    "independent-progress-assessments", "drafts", "img", "logs",
    "agent-red.wiki", "docs-site", "config", "memory",
})
```

The list is derived from `git ls-tree --name-only -d HEAD` against the
current working tree, restricted to directories that contain Agent Red
content mixed with or alongside GT-KB infrastructure. The list is
**explicit** rather than negative-derived (e.g., "anything except
`applications/`") so future additions don't silently expand the
allowlist.

The list itself becomes durable evidence that the migration is
needed: every directory in the set is a target for Phase 8 rehearsal
classification (move/copy/split/stay/regenerate/deprecate per the
Phase 1 authority matrix).

## 5. Test Updates

The original `-001` §2.4 test plan (binding via `-005`) covers
T-DRIVER-1 (refuse `--target-root` inside legacy mixed root) and
T-DRIVER-2 (refuse output paths outside target). Both tests must be
updated to match the revised refusal logic:

- **T-DRIVER-1**: parametric over the conflated-surface list.
  Asserts that `--target-root=<gt-kb-root>/<surface>/` exits 2 with
  the expected error message for each entry in
  `LEGACY_CONFLATED_SURFACES`. Plus assertions that
  `--target-root=<gt-kb-root>/` (root itself) and
  `--target-root=<gt-kb-root>/applications/` (parent without named
  child) both exit 2.
- **T-DRIVER-1-ALLOW** (new): asserts that
  `--target-root=<gt-kb-root>/applications/Agent_Red/` (and any other
  valid `applications/<name>/` path) does NOT exit 2 on the refusal
  check. The fixture creates a temporary `applications/<name>/`
  directory; the assertion is on the refusal check only, not on
  end-to-end rehearsal execution.
- **T-DRIVER-2**: unchanged.
- **T-DRIFT-CHECK**: unchanged.
- **T-LANE-COVERAGE**: unchanged.

## 6. Sections Unchanged

These remain authoritative from `-005` (which incorporates `-003` and
`-001`):

- §0 (NO-GO acknowledgement chain through `-002`)
- §1.1, §1.2 (Plan citations + Phase 7 Slice 2 known-gap)
- §2.2 (eleven-lane sub-script table)
- §2.3 (manifest schema)
- §2.5 (output directory)
- §2.6 (no-changes list — release-candidate gate, deploy.py, etc.)
- §3 (owner-decision sequencing — only §3.1 blocks Wave 1; §3.3 / §3.5
  / §3.6 / §3.2 / §3.4 / §3.7 surface at later wave boundaries)
- §4 (wave structure — Wave 1 scaffolding, Wave 2 sub-scripts, Wave 3
  verification matrix, Wave 4 owner-witnessed evidence)
- §5 (exit-criteria mapping)
- §6 (regression visibility)
- §7 (risk analysis)
- §10 (out-of-scope)

## 7. Implementation Order Adjustment

`-005` §4.1 Wave 1 sub-items remain identical except step 2:

> 2. Create `scripts/rehearse/_common.py` with target-root safety
>    helpers, manifest parser, hash-set walker,
>    refuse-on-out-of-scope decorator. The owner-supplied target-root
>    is a constant in `_common.py` constants module.

**Revised step 2:**

> 2. Create `scripts/rehearse/_common.py` with:
>    - `LEGACY_ROOT = Path(__file__).resolve().parents[2]` — current
>      project root, equal to `<gt-kb-root>/`
>    - `TARGET_ROOT_DEFAULT = LEGACY_ROOT / "applications" / "Agent_Red"`
>    - `LEGACY_CONFLATED_SURFACES` frozenset per §4 above
>    - `APPLICATIONS_NAMESPACE = LEGACY_ROOT / "applications"` —
>      shorthand for the canonical applications parent
>    - `validate_target_root(path: Path) -> None` — raises
>      `TargetRootError` if path matches any rejected condition per §4
>    - Manifest parser, hash-set walker, refuse-on-out-of-scope
>      decorator unchanged from `-005`

Step 1 (`__init__.py`), step 3 (`rehearse_isolation.py` skeleton),
step 4 (test skeleton), step 5 (manifest), step 6 (no
release-candidate-gate change), step 7 (post-impl report) are
unchanged.

## 8. Manifest Schema Update

`-001` §2.3 (binding via `-005`) lists `target_root` and `legacy_root`
as required manifest fields. The values are now:

```toml
target_root = "E:/GT-KB/applications/Agent_Red"
legacy_root = "E:/GT-KB"
applications_namespace = "E:/GT-KB/applications"   # NEW
```

The `applications_namespace` field is added to make the IDP convention
visible at the manifest level for downstream tooling (Phase 9
productization, dashboard rendering, adopter scaffolding).

Manifest validation in `_common.load_manifest()` asserts that
`target_root` is a strict descendant of `applications_namespace` and
that `applications_namespace` is exactly `<legacy_root>/applications`.

## 9. Codex Re-Review Asks

1. Confirm the architectural correction in §3 (target now
   `<gt-kb-root>/applications/<name>/`) aligns with the IDP model
   established in `CLAUDE.md` and the Phase 9 productization plan in
   `gtkb-isolation-009-adopter-packaging-plan-review-004`.
2. Confirm the refined refusal logic in §4 catches the legacy-mixed-
   root class without false-blocking the canonical
   `applications/<name>/` namespace. Flag any conflated surface
   missing from `LEGACY_CONFLATED_SURFACES` that should be in the
   blocklist (the list was derived from `git ls-tree --name-only -d
   HEAD` filtered by manual inspection).
3. Confirm §5's T-DRIVER-1 parameterization + T-DRIVER-1-ALLOW
   addition adequately verifies the refusal-logic refinement.
4. Confirm §8's `applications_namespace` manifest field is the right
   place to surface the IDP convention without overshooting Wave 1
   scope.
5. Confirm the deferral of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
   formal capture to GTKB-ISOLATION-009 productization is acceptable;
   the convention is owner-confirmed in S310 and treated as binding
   for this rehearsal pending formal ADR.
6. **GO / NO-GO** on this revised proposal. On GO, Wave 1 proceeds
   with the corrected target and refusal logic.

## 10. Decision Needed From Owner

None. Owner architectural confirmation captured S310 (2026-04-26) is
the load-bearing decision. Subsequent decisions §3.2 through §3.7 are
surfaced at their wave boundary per `-005` §3.

## 11. Acknowledgment

The architectural correction is owner-driven and materially improves
the rehearsal's first-conformant-adopter precedent. The original
sibling-target options in the AskUserQuestion would have established
a portability claim (apps running from non-GT-KB-root paths) that has
not been validated and should not have been encoded as the first
migration's template. Catching this before Wave 1 lands is exactly
what the bridge protocol's owner-checkpoint structure is for.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files added on Wave 1 (after Codex re-review GO + this revision):**
- `scripts/rehearse/__init__.py` (already created in this session;
  unchanged by this revision)
- `scripts/rehearse/_common.py` (per §7 step 2)
- `scripts/rehearse_isolation.py` (skeleton; unchanged from `-005`)
- `tests/scripts/test_rehearse_isolation.py` (T-DRIVER-1 parametric +
  T-DRIVER-1-ALLOW per §5)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
  (per §8)

**Implementation NOT yet authorized** until Codex re-review GO on this
revision.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
