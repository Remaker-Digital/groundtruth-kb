NEW
::init gtkb pb
::open build

# gtkb-wi6009-harness-parity-projection-coverage — Make the harness parity checker evaluate named harnesses unconditionally and compare adapter skill trees against canonical

bridge_kind: prime_proposal
Document: gtkb-wi6009-harness-parity-projection-coverage
Version: 001
Author: Prime Builder (Claude, harness B, interactive)
Date: 2026-08-07 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8038611d-3a31-49fb-ad15-9f00b0ef3d25
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-6009

target_paths: ["scripts/check_harness_parity.py", "platform_tests/scripts/test_check_harness_parity.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The owner directive motivating this work: all harnesses must operate from a
common baseline via projection, so that updates made to the baseline are
by-default available to every harness. Measurement on 2026-08-07 shows that
property does not currently hold, and that the detector meant to protect it
cannot observe the violation.

**Measured drift.** Canonical `.claude/skills` carries 45 skill directories.
Adapter trees carry: `.agent` 44, `.api-harness` 44, `.codex` 44, `.cursor` 44,
`.goose` 46. Two distinct conditions:

- `gtkb-skill-rollout` exists in canonical and is **missing from all five**
  adapter trees.
- `.goose` carries two directories absent from canonical — `gtkb-codex-report`
  and `gtkb-kb-work-item` — which appear to be pre-rename names surviving the
  canonical rename to `gtkb-work-item`. A projection target cannot legitimately
  exceed its source.

**Why the detector did not stop this.** `scripts/check_harness_parity.py` run on
2026-08-07 scoped explicitly to the goose harness returned `Overall status:
WARN`, exit code `0`, an **empty** `Harnesses:` line, no per-harness rows, and a
single row classifying `gtkb-skill-rollout` as `EXTRA` with the note "Project
skill exists but is not declared in the harness capability registry." Three
gaps, of which this proposal addresses two:

1. **Coverage (WI-6011).** `report_selected_harnesses` is built from
   `operative_harnesses`, the union of `active_harnesses` and
   `registered_floor_harnesses`, derived from each harness's lifecycle value
   (selection block around lines 1255-1268). The canonical projection at
   `harness-state/harness-registry.json` records goose with `status =
   suspended`, so it was filtered out before any comparison could run. Lifecycle
   is a *dispatch-oriented* axis; reusing it as a relevance proxy is safe only
   while dispatch drives the work. Under the current manual-only operating
   regime it is not: this suspended harness authored two governed Loyal
   Opposition verdicts via the legitimate interactive session-stated role
   override — the terminal `VERIFIED` at
   `bridge/gtkb-wi5823-impl-auth-spec-links-extractor-alignment-010.md`
   (2026-08-06) and the `NO-GO` at
   `bridge/gtkb-wi5823-stranded-finalization-verdict-reissue-002.md`
   (2026-08-07). Three of eight registered harnesses currently carry
   `suspended`, so the uncovered surface is substantial.
2. **Comparison (WI-6009).** The checker validates *declared* capability
   surfaces from `config/agent-control/gtkb-harness-capability-registry.toml`.
   It never compares the canonical skill-name set against what is actually
   present in each adapter tree, so an undeclared canonical skill produces one
   `EXTRA` row about registry bookkeeping rather than five rows about missing
   projections, and stale directories present only in an adapter tree produce
   nothing at all.

**Proposed change — two surgical edits to the checker plus tests.**

- **(A) Explicit harness scope is honored unconditionally.** When `--harness
  <name>` names a single harness, evaluate it regardless of lifecycle status.
  The existing `explicit_harness` concept already exists in the selection block
  (line 1261 exempts `retired`/`other` when a harness is explicitly named); this
  extends the same exemption to the lifecycle filter that currently removes
  `suspended` harnesses from `report_selected_harnesses`. Default `--all`
  behavior is unchanged.
- **(B) Canonical-versus-adapter tree comparison.** For each evaluated harness
  with a declared adapter root, compare the canonical skill-name set against the
  names present in that harness's skills tree, emitting two new row kinds:
  `MISSING_PROJECTION` (in canonical, absent from the adapter tree) and
  `UNTRACKED_SURFACE` (present in the adapter tree, absent from canonical).
  Names are compared modulo per-harness exclusions already declarable in the
  registry.

**Severity is deliberately WARN in this slice, not FAIL.** The corpus is not
clean: flipping to FAIL now would make the checker fail on arrival because
`gtkb-skill-rollout` is still undeclared and unprojected. Remediating that —
adding its `[[capabilities]]` block and regenerating adapters — is **WI-6008 and
is explicitly out of scope here**. Promotion of these rows to FAIL is a
follow-on once the corpus is clean. This mirrors the platform's own precedent:
the ADR/DCL clause preflight shipped advisory-only in Slice 1 and was promoted
to a blocking gate in Slice 2 after the trigger set had been tightened against
real feedback.

**Explicitly out of scope.** No adapter is regenerated; no stale directory is
removed; no registry entry is added; no generator is created. WI-6007 (the
harness that has no skill-adapter generator at all) and WI-6008 (the
canonical-addition remediation and its enforcement gate) remain separate work.
This proposal changes only what the detector can see and report.

## Specification Links

- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — GT-KB installs must prepare capable
  harnesses for both operating roles. A harness whose skill surface silently
  diverges from canonical is not verifiably prepared; this restores the
  measurement that backs the requirement.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the machine-checkable capability floor
  for a GT-KB harness. The floor is only meaningful if it is actually evaluated
  for the harness in question, which change (A) restores.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — roles are portable across harnesses by
  owner assignment. Portability presumes equivalent capability surfaces;
  undetected projection drift breaks that presumption silently.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — canonical `.claude/skills` is the
  source of truth (`generate_api_skill_adapters.py` declares `source_of_truth`
  as `.claude/skills/*/SKILL.md`); change (B) derives its comparison from that
  canonical set rather than from declared metadata alone.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail authority; filed as the
  append-only `-001` of a new numbered chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires citation
  of every governing specification; satisfied by this section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/PAUTH/work-item
  triple supplied in the header and validated read-only against MemBase by the
  scaffold helper.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification executes
  spec-derived tests; see the Spec-to-Test Mapping below.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation proceeds only
  under the cited active PAUTH plus a live bridge `GO` and an
  implementation-start packet.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — no bypass claimed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both target paths are inside
  `E:/GT-KB`; nothing under `applications/` is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the drift is recorded as durable work
  items (WI-6007, WI-6008, WI-6009, WI-6011) rather than as session context.
- `GOV-STANDING-BACKLOG-001` — the four captures are in the MemBase backlog and
  this proposal implements one of them without silently absorbing the rest.

## Prior Deliberations

- `DELIB-202666292` — *Loyal Opposition NO-GO Verdict, WI-5144 HP08 Semantic
  Adapter Drift*. Closest prior decision on adapter drift; surfaced by the
  deliberation search for this topic. This proposal differs in target: HP08
  concerned semantic drift within generated adapter content, whereas this
  concerns set-level presence/absence of skills and the detector's coverage.
- `DELIB-202665590`, `DELIB-202665598`, `DELIB-202665605` — prior Loyal
  Opposition `GO` verdicts surfaced by the same search on harness capability
  parity; reviewed for prior accepted approaches before proposing.
- `WI-5501` — records that on 2026-07-18 the `.claude`/`.codex`/`.cursor`
  `write_verdict.py` projections were byte-identical at SHA-256 `549e12e6…`.
  They are not identical today, dating the onset of the current drift to after
  that baseline.
- `WI-5334` — frozen `AT-HARNESS-PARITY` acceptance at 34/36, with both
  remaining failures in `test_cross_harness_protocol_parity.py` on dispatch-floor
  assertions. Distinct from this proposal's subject (skill-surface projection),
  but confirms harness parity is an actively governed acceptance surface.
- `WI-5932` — directive-enforcement parser false-positives on harness
  identifiers in prose CLI argument values. Reproduced live while gathering
  evidence for this proposal; noted so a reviewer reproducing the measurement
  is not surprised by the same block.

## Owner Decisions / Input

This proposal depends on owner approval and cites the AUQ-only owner-decision
rule. Authorizing evidence:

1. **Owner directive, 2026-08-07 (this session transcript):** "It is very
   important that all harnesses work from the common baseline via projection,
   in order to ensure that updates are made to the baseline and are by-default
   available to all harnesses." This is the standing requirement the proposal
   implements measurement for.
2. **Owner directive, 2026-08-07 (same message):** "We have already raised
   recent work items on this topic" — which directed the dedupe pass that
   produced WI-6007, WI-6008, WI-6009, and WI-6011 rather than duplicating
   existing coverage (WI-5497, WI-5501, WI-5334 were checked and are distinct).
3. **Owner directive, 2026-08-07:** "The legacy FE dispatcher and daemon (and
   related guards) are all disabled on purpose… All LO and PB work is being
   driven manually until further notice." This is load-bearing for change (A):
   manual operation is precisely the condition under which lifecycle status
   stops predicting which harnesses are doing work.

No new owner decision is required to review this proposal. The severity
question — whether the new rows should eventually FAIL rather than WARN — is
deferred to the follow-on and will require its own owner decision at that time.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised requirement is needed
before implementation. `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`,
`GOV-HARNESS-ONBOARDING-CONTRACT-001`, and `GOV-HARNESS-ROLE-PORTABILITY-001`
already require harnesses to carry equivalent, verifiable capability surfaces;
this proposal restores the measurement that makes those requirements checkable
rather than adding new policy. The FAIL-promotion decision deferred above would
be a policy change and is therefore explicitly not proposed here.

## Spec-Derived Verification Plan

| Linked specification | Verification | Expected result |
| --- | --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` (change A) | `groundtruth-kb/.venv/Scripts/python.exe scripts/check_harness_parity.py --harness goose --markdown` | non-empty `Harnesses:` line naming the harness, and per-harness rows present — versus the current empty line and zero rows |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (change B) | same command | reports `MISSING_PROJECTION` for `gtkb-skill-rollout` and `UNTRACKED_SURFACE` for `gtkb-codex-report` and `gtkb-kb-work-item` |
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` (change B, breadth) | `groundtruth-kb/.venv/Scripts/python.exe scripts/check_harness_parity.py --all --markdown` | `MISSING_PROJECTION` for `gtkb-skill-rollout` reported against all five adapter trees, not one aggregate `EXTRA` row |
| severity discipline (deliberate WARN) | same commands, check exit status | exit code remains `0` and overall status remains `WARN`; this slice adds visibility without introducing a gate that would fail on arrival |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --stat` after implementation | only the two declared target paths change; both inside the project root |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi6009-harness-parity-projection-coverage` after `GO` | `authorized: true`, scoped to the two declared target paths only |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi6009-harness-parity-projection-coverage` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6009-harness-parity-projection-coverage` | `preflight_passed: true`, `missing_required_specs: []`, blocking gaps `0` |

### Spec-to-Test Mapping

| Specification | Test (spec-derived) | Command | Expected |
| --- | --- | --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` | `platform_tests/scripts/test_check_harness_parity.py` — the checker's own suite; extended in this slice with cases for explicit-harness lifecycle exemption and for the two new row kinds | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_harness_parity.py -q --no-header` | all pass, including the new cases |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | `platform_tests/scripts/test_cross_harness_parity_schema.py` — schema contract for cross-harness parity records; guards the new row kinds against schema drift | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_parity_schema.py -q --no-header` | all pass |
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` | `platform_tests/groundtruth_kb/test_cross_harness_parity_foundation.py` — foundation-level parity contract | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_cross_harness_parity_foundation.py -q --no-header` | all pass |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `platform_tests/scripts/test_check_harness_parity_entrypoint_import.py` — import-surface guard on the modified module | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_harness_parity_entrypoint_import.py -q --no-header` | all pass |

Baselines for all four suites are captured before implementation and re-run
after, so any delta is attributable to this change rather than to pre-existing
tree state. That discipline is adopted deliberately: earlier in this session six
failures in adjacent implementation-authorization suites were shown to be
pre-existing only by re-running them against `HEAD`.

Pre-file code-quality gates on the changed Python, per the file-bridge protocol:
`ruff check` and `ruff format --check` are run separately on both target paths
before the implementation report is filed.

## Risk / Rollback

**Risk surface.** Two files, one of them a test. The checker is a read-only
diagnostic: it reports state and does not mutate adapters, registry, MemBase,
dispatcher/TAFE state, or git. A defect in it therefore produces wrong reporting
rather than wrong repository state.

**Principal risk — reporting-volume increase.** Change (B) will surface rows
that were previously invisible, including against harnesses nobody has looked at
recently. This is intended, but it means the parity summary in the session-start
payload may grow. Mitigated by keeping severity at WARN so no gate flips, and by
scoping the new comparison to skill names rather than content.

**Secondary risk — explicit-harness exemption breadth.** Change (A) makes an
explicitly named harness evaluate regardless of lifecycle, including `retired`.
That is consistent with the existing exemption at line 1261, but a reviewer
should confirm evaluating a retired harness is desirable rather than merely
harmless. If not, the exemption can be narrowed to `suspended` only; the
proposal accepts either disposition and will follow the reviewer's direction.

**Tertiary risk — false drift on legitimate per-harness differences.** Some
harnesses may intentionally omit a skill they cannot support. The comparison
honors per-harness exclusions already declarable in the registry; if the current
registry lacks an exclusion vocabulary rich enough to express a legitimate
omission, that gap surfaces as a `MISSING_PROJECTION` row at WARN rather than as
a failure, which is the safe direction.

**Rollback.** Single-commit `git revert <sha>` restores prior checker behavior
exactly. No database, dispatcher, registry, or adapter state changes, so there
is no non-git rollback component.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi6009-harness-parity-projection-coverage`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — this repairs a diagnostic that fails to observe a condition it exists
to detect. It adds no new capability surface to the platform and restructures
nothing, so `feat:` would overstate and `refactor:` would misdescribe it; the
change is behavioral correction to a checker, not maintenance, so `chore:` would
understate it.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
