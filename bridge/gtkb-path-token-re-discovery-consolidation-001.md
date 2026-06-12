NEW

# gtkb-path-token-re-discovery-consolidation — Consolidate the third `PATH_TOKEN_RE` copy (adr_dcl_applicability_discovery.py) onto the shared canonical superset

Work Item: WI-4485
Project: PROJECT-GTKB-RELIABILITY-FIXES
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
target_paths: ["scripts/implementation_authorization.py", "scripts/adr_dcl_applicability_discovery.py", "platform_tests/scripts/test_fab14_path_token_dedup.py"]
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 28ac82dc-caf5-43f3-97fc-79a79c989f04
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory; mode=auto

## Summary

`PATH_TOKEN_RE` (the anchored, enumerated-repo-directory matcher used to harvest
repository path tokens from bridge documents) was consolidated to a single
canonical source in `scripts/implementation_authorization.py` during FAB-14
(WI-4426, HYG-046). `scripts/bridge_applicability_preflight.py` imports it; the
dead copy in `scripts/implementation_start_gate.py` was removed.

FAB-14 `-005` (lines 69–70) explicitly flagged a **third copy** in
`scripts/adr_dcl_applicability_discovery.py:40` as an out-of-scope follow-on,
"tracked separately, not folded into FAB-14." This proposal closes that
follow-on under WI-4485.

The third copy has **drifted bidirectionally** from the canonical:

| Directory token | Canonical (`implementation_authorization.py:78`) | Discovery copy (`adr_dcl_applicability_discovery.py:40`) |
|---|---|---|
| `memory/` | present (owner-added 2026-06-04 AUQ) | **missing** |
| `.claude/skills` | absent | present |
| `.codex/skills` | absent | present |

A naïve one-way `import` of the canonical would simultaneously give discovery
`memory/` AND silently drop `.claude/skills` + `.codex/skills` from its
document-wide harvest. The owner chose (AskUserQuestion, 2026-06-12 — see
§Owner Decisions / Input) the **superset** consolidation: extend the canonical
to the true union, then repoint discovery to import it. All three consumers
then share one object and divergence becomes structurally impossible (asserted
by the identity test).

## Problem Statement (concrete, testable)

1. `scripts/adr_dcl_applicability_discovery.py:40-42` defines a private
   `PATH_TOKEN_RE` that is NOT byte-identical to the canonical
   `scripts/implementation_authorization.py:78-80`. The drift is verifiable: the
   discovery copy's alternation lacks `memory` and adds `\.claude/skills` +
   `\.codex/skills`.
2. There is no test asserting the discovery copy is the same object as the
   canonical, so the drift was undetectable until manual inspection.
3. Consequence (the latent defect): because the discovery copy lacks `memory`,
   its document-wide harvest silently fails to surface `memory/...` path tokens
   that the canonical (and the gate) harvest — an observable behavior gap for an
   advisory helper that should share the gate's path vocabulary.

## Reliability Fast-Lane Eligibility (GOV-RELIABILITY-FAST-LANE-001)

This work item is filed under the reliability fast-lane and is covered by
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` via active project membership
(`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`). Eligibility is asserted against
all four criteria:

1. **Origin defect/regression** — WI-4485 origin is `defect` (latent drift: the
   discovery copy silently fails to harvest `memory/` paths; per Problem
   Statement §3).
2. **No new public API / CLI / behavior beyond removing the defect** — the only
   *observable* behavior change anywhere is the discovery helper gaining
   `memory/` harvesting (which IS the defect removal). The canonical's added
   `.claude/skills` / `.codex/skills` matching is **provably inert**:
   `config/governance/spec-applicability.toml` has no `applies_when_paths_match`
   trigger keyed off those prefixes (or `memory`), so
   `bridge_applicability_preflight`'s required-spec output is unchanged. No new
   CLI, no new public function, no new exit code.
3. **No new or revised requirement** — see §Requirement Sufficiency.
4. **Small, single-concern** — 3 files, ~12 net lines (a regex-alternation
   extension, a 4-line import block replacing a 3-line definition, and a small
   test extension).

If Loyal Opposition judges criterion 2 not met (e.g., reads the canonical's
skills-prefix addition as new behavior rather than inert), the correct
disposition is NO-GO directing refile under the standard project path with a
bounded per-WI PAUTH; the work itself is unchanged either way.

## Proposed Change

### Change 1 — `scripts/implementation_authorization.py` (canonical → union)

Extend the directory alternation in `PATH_TOKEN_RE` (currently line 78-80) to
add `\.claude/skills` and `\.codex/skills`, placed adjacent to the existing
`\.claude/hooks|\.codex/gtkb-hooks` members (it already carries `memory`):

```
... |config|\.claude/skills|\.codex/skills|\.claude/hooks|\.codex/gtkb-hooks|\.github|bridge|independent-progress-assessments|memory)/ ...
```

The result is the exact union of the two historical member sets. Update the
adjacent HYG-046 comment (lines 73-77) to record that the skills prefixes were
folded into the union for the `adr_dcl_applicability_discovery` consumer
(WI-4485). `implementation_authorization.py` only *defines* `PATH_TOKEN_RE`
(it has no `.finditer`/`.findall` of its own), so this edit is definition-only
there; behavior changes land only in the importing consumers.

### Change 2 — `scripts/adr_dcl_applicability_discovery.py` (import canonical)

Delete the local definition (lines 40-42) and import the canonical object via
the same try/except pattern `bridge_applicability_preflight.py` uses
(lines 25-28), with the same explanatory comment form (lines 46-47):

```python
try:
    from scripts.implementation_authorization import PATH_TOKEN_RE
except ImportError:  # pragma: no cover - direct script execution path
    from implementation_authorization import PATH_TOKEN_RE
```

The line-264 usage (`PATH_TOKEN_RE.finditer(content)`) is unchanged.

### Change 3 — `platform_tests/scripts/test_fab14_path_token_dedup.py` (identity + superset)

Extend the existing single-source identity test (the natural home — its stated
purpose is "PATH_TOKEN_RE is a single canonical source (no drift)") to:

- import `adr_dcl_applicability_discovery` and assert
  `add.PATH_TOKEN_RE is ia.PATH_TOKEN_RE` (third copy now shares the one object);
- assert the canonical now matches `.claude/skills/...` and `.codex/skills/...`
  paths (locks the owner-chosen superset members);
- update the module docstring to record the third consumer.

The existing assertions (`bap.PATH_TOKEN_RE is ia.PATH_TOKEN_RE`, `memory/`
match, prose `word/word` non-match) remain unchanged and still pass.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every relevant
  governing spec is cited in this section.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `NEW`
  INDEX entry; bridge protocol honored.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived from
  the linked specs below (see §Spec-Derived Verification Plan).
- `GOV-RELIABILITY-FAST-LANE-001` — eligibility asserted above; covered by the
  standing project authorization via active membership.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` — deterministic-only classifier constants
  (HYG-046 lineage); a single canonical `PATH_TOKEN_RE` keeps the deterministic
  matcher drift-free.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the identity
  test is the mechanical (review-time + CI) enforcement that makes the
  single-source invariant structurally durable, not memory-dependent.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all three `target_paths` are
  in-root under enumerated repo directories; no out-of-root dependency.
- `GOV-STANDING-BACKLOG-001` — WI-4485 is the governed backlog authority for
  this work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
  / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the drift remediation is
  captured as durable artifacts (WI-4485 work item + owner-decision deliberation
  + identity test) rather than an untracked edit, honoring the artifact lifecycle.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements already exist:
the HYG-046 single-deterministic-source intent (`SPEC-AUQ-NO-LLM-CLASSIFIER-001`,
FAB-14 WI-4426), the owner-blessed `memory/` membership
(`bridge/gtkb-impl-start-gate-path-token-memory-prefix-fix-*`, owner AUQ
2026-06-04), and the anchored enumerated-repo-directory design
(`bridge/gtkb-s358-w4-enforcement-calibration-*`, WI-3368). The owner
AskUserQuestion of 2026-06-12 resolved the design choice (superset vs one-way
import); it selected among existing-requirement-compatible implementations and
introduced no new requirement. No new or revised specification is required
before implementation.

## Spec-Derived Verification Plan

Spec-to-test mapping:

| Linked spec / decision | Derived test(s) |
|---|---|
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` + HYG-046 single-source intent | `test_path_token_re_is_one_shared_object` (existing) AND new `test_discovery_path_token_re_is_canonical` (`add.PATH_TOKEN_RE is ia.PATH_TOKEN_RE`) |
| Owner AUQ 2026-06-12 superset members (`.claude/skills`, `.codex/skills`) | new `test_canonical_path_token_re_matches_skills_dirs` |
| Owner AUQ 2026-06-04 `memory/` membership preserved | `test_path_token_re_matches_memory_paths` (existing) |
| Anchored-pattern design (no prose `word/word` harvest) | `test_path_token_re_ignores_prose_word_slash_word` (existing) + `test_preflight_prose_slash_not_harvested` |
| Discovery runtime behavior preserved | full `test_adr_dcl_applicability_discovery.py` suite (6 tests) |
| `bridge_applicability_preflight` output unchanged (skills tokens inert: no `spec-applicability.toml` `applies_when_paths_match` trigger keys off `.claude/skills`/`.codex/skills`/`memory`) | `test_preflight_prose_slash_not_harvested` + `test_preflight_declared_and_rooted_paths_still_harvested` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | full-suite execution (commands below) |

Execution commands (to be run and reported in the post-implementation report):

```
python -m pytest platform_tests/scripts/test_fab14_path_token_dedup.py \
                 platform_tests/scripts/test_adr_dcl_applicability_discovery.py \
                 platform_tests/scripts/test_bridge_applicability_preflight.py -q
ruff check scripts/implementation_authorization.py scripts/adr_dcl_applicability_discovery.py platform_tests/scripts/test_fab14_path_token_dedup.py
ruff format --check scripts/implementation_authorization.py scripts/adr_dcl_applicability_discovery.py platform_tests/scripts/test_fab14_path_token_dedup.py
```

Green pre-change baseline already captured: `test_adr_dcl_applicability_discovery.py`
(6) + `test_fab14_path_token_dedup.py` (3) = 9 passed (Python 3.14.0, pytest 9.0.2).

## Recommended Commit Type

`refactor:` — the dominant intent is de-duplication/consolidation of a drifted
constant onto one shared object. The gate consumers' applicability *output* is
unchanged (the added skills prefixes are inert against the governance triggers);
the discovery consumer gains `memory/` harvesting it previously lacked (the
defect fix, advisory-only candidate surfacing). The choice is declared here for
validation per the Conventional Commits Type Discipline; Loyal Opposition may
prefer `fix:` if the discovery `memory/` gap is read as the dominant change.

## Risk / Rollback

- **Risk:** extending the canonical changes `bridge_applicability_preflight`'s
  harvested token set (now matches `.claude/skills`/`.codex/skills`).
  **Mitigation/evidence:** behaviorally inert — `config/governance/spec-applicability.toml`
  has no `applies_when_paths_match` trigger for those prefixes (verified by grep:
  triggers are `applications/**`, `.claude/rules/*.md`, `…/project/**`, `bridge/**`).
  The two preflight harvest tests use inputs with no skills paths and still pass.
- **Risk:** discovery gains `memory/` harvesting (behavior change for an
  advisory-only helper that always exits 0). **Mitigation:** intended per owner
  AUQ and is the defect fix; raises candidate surfacing for memory-related
  ADR/DCLs only; never gates.
- **Risk:** test-time import of the discovery module has side effects.
  **Mitigation:** the module's import-time work is constant definitions only.
- **Rollback:** single-commit revert restores the discovery local copy, drops
  the two skills tokens from the canonical, and removes the new test assertions.
  No data, state, or external-surface migration.

## Owner Decisions / Input

This proposal depends on an owner design decision, captured via AskUserQuestion
on 2026-06-12 (harness B / claude-opus-4-8):

- **Question:** "The discovery copy of PATH_TOKEN_RE has drifted in BOTH
  directions: it lacks the canonical's `memory/` token but adds `.claude/skills`
  + `.codex/skills` that the canonical lacks. How should the consolidation handle
  the skills prefixes?"
- **Owner answer:** **"Superset canonical (recommended)"** — extend the canonical
  to add `.claude/skills` + `.codex/skills` (it already has `memory/`), then
  repoint discovery to import it; all three consumers share one true union.
- **Consequence:** Change 1 edits a second protected script (the canonical) to
  the union; discovery keeps everything it matches today and additionally gains
  `memory/`.

The decision is recorded inline above and in WI-4485's history
(`source_owner_directive`); a per-fix deliberation record is explicitly waived
for fast-lane fixes per `GOV-RELIABILITY-FAST-LANE-001`. No further owner input
is required to proceed once Loyal Opposition records `GO`.

## Prior Deliberations

`search_deliberations()` for "PATH_TOKEN_RE duplicate constant consolidation"
and "single canonical source path token drift" returned **no Deliberation
Archive records** (consistent with FAB-14's own "no prior deliberation found"
note for the PATH_TOKEN_RE `memory/` omission). The governing prior-decision
record is the bridge-thread lineage (referenced here, not the work's own WI):

- `bridge/gtkb-fab-14-gate-fp-feedback-loop-005.md` (WI-4426, HYG-046) —
  consolidated copies 1 and 2; lines 69–70 explicitly flag THIS third copy in
  `scripts/adr_dcl_applicability_discovery.py` as an out-of-scope follow-on.
  This proposal is that follow-on.
- `bridge/gtkb-impl-start-gate-path-token-memory-prefix-fix-001.md … -004.md`
  (WI-4354) — owner AUQ 2026-06-04 added `memory/` to `PATH_TOKEN_RE` (Option 1,
  surgical). This proposal preserves that membership in the union.
- `bridge/gtkb-s358-w4-enforcement-calibration-001.md … -008.md` (WI-3368) —
  anchored `PATH_TOKEN_RE` content-harvesting to declared `target_paths` plus an
  enumerated repo-directory set so prose `word/word` tokens are not harvested.
  This proposal preserves that anchored design (no broadening of the prose-scan
  surface).

No previously rejected approach is being revisited; the one-way-import
alternative was considered and consciously declined via the owner AUQ above in
favor of the superset.
