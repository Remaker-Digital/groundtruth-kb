REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-19-hygiene-detector-expansion
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-19-hygiene-detector-expansion-002.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4431
Project Authorization: PAUTH-FAB19-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: e45ccf07-99f6-4ad6-b572-570a76a264a2
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["config/governance/hygiene-sweep-patterns.toml", "scripts/check_skill_health.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/**", ".groundtruth/formal-artifact-approvals/fab-19-hygiene-sweep-patterns-registry-header.json"]

No KB mutation: all FAB-19 changes are config (the hygiene-sweep pattern registry, under a formal-artifact-approval packet for its governed header) and doctor source (wiring the skill-health checker); no `groundtruth.db` write. `groundtruth.db` is intentionally NOT in target_paths. The approval-packet JSON is a `.groundtruth/` evidence artifact, not a MemBase write.

---

# FAB-19 — Deterministic Hygiene Detector Expansion (REVISED)

WI-4431 (FAB-19) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-051 (hygiene sweep has 3 patterns + blanket
exclusions of the high-yield drift dirs), HYG-066 (skill-health checker wired into no gate). Source advisory:
`bridge/gtkb-fable-investigation-advisory-001.md` (Q5 repeatability architecture).

## Revision Scope

Addresses the sole P1 finding in the `-002` NO-GO (Codex, harness A): the proposal promised a
formal-artifact-approval packet for the governed `hygiene-sweep-patterns.toml` registry-header revision, but
`target_paths` omitted the packet artifact, so the bridge envelope authorized the governed header revision
without the path to the artifact that proves its approval.

**Fix:** `target_paths` now includes the concrete approval-packet path
`.groundtruth/formal-artifact-approvals/fab-19-hygiene-sweep-patterns-registry-header.json`. No other scope
change. Per the `-002` Recommended Revised Scope, the doctor skill-health check stays WARN-only, and external
Agent Red repository mutation and push/deploy remain out of scope (the PAUTH already forbids them).

## Summary

- **HYG-051 (sweep patterns):** `config/governance/hygiene-sweep-patterns.toml` has exactly 3 patterns, all
  Agent-Red-residue-shaped, and its `exclusion_globs` blanket-skip `.claude/`, `.codex/`, `memory/`,
  `independent-progress-assessments/`, `archive/` — exactly where this 68-finding investigation found the
  dominant drift. The DELIB-S312 deterministic-services principle cannot detect the recurring drift classes.
- **HYG-066 (skill health):** `check_skill_health.py` exits 1 with 76 findings across 72 skills
  (fenced_python 26, db_mutation 32, index_write 18) but is wired into NO gate or doctor check, so the
  signal is produced and discarded.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the deterministic-services bias the sweep expansion realizes
  (encode recurring investigation classes into a service) (HYG-051).
- `SPEC-DSI-DOCTOR-CHECK-001` — doctor invariant reporting; the skill-health WARN wiring adds a doctor check
  (HYG-066).
- `GOV-08` (Knowledge Database is the single source of truth) — the sweep + skill-health surfaces report
  drift against canonical state.
- `GOV-17` (Automation script modification approval gate) — the sweep is automation; the pattern-registry
  revision rides the governed approval path under the cited packet (HYG-051).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-19 changes are in-root; see Isolation Placement
  Compliance below.
- `GOV-STANDING-BACKLOG-001` — WI-4431 is the governed backlog authority; absorbs the overlapping items.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the registry + doctor changes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `REVISED` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-051/066; Q5 charter).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions (Q5 = layered repeatability: CLI core +
  skill + delta mode).
- `DELIB-FAB19-REMEDIATION-20260610` — this cluster's owner expansion decision + skill-health wiring.
- `bridge/gtkb-fab-19-hygiene-detector-expansion-002.md` — the NO-GO this revision addresses (target-scope
  packet path).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the principle the sweep expansion operationalizes.
- _FAB-20 (the gtkb-hygiene-investigation skill) consumes this expanded detector core as its layer-1
  evidence pack; FAB-19 is the deterministic-core half of the Q5 layered architecture._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB19-REMEDIATION-20260610`:

1. **HYG-051 = Full expansion.** Convert this investigation's recurring finding classes into 5-8 new
   `[[patterns]]` entries (content regexes for retired-mechanism / Claude-Playground / work_list.md /
   CURSOR-* references and stale relocated paths; presence patterns for render/tmp dirs and dead-allowlist
   filenames; template-vs-live hash drift), and replace the blanket exclusion list with per-pattern
   exclusions so `.claude/.codex` content is scanned. Each batch bridge-reviewed; the registry-header
   revision uses the formal-artifact-approval packet (now path-targeted, see target_paths).
2. **HYG-066 = wire skill-health into a doctor WARN** (determined fix): surface `check_skill_health.py` on
   every doctor run as advisory (not blocking, given the 76 standing findings); promotion to a blocking gate
   is deferred until the findings are triaged.

## Requirement Sufficiency

**Existing requirements sufficient.** The disposition is fixed by `DELIB-FAB19-REMEDIATION-20260610`; the
governing specifications (`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `SPEC-DSI-DOCTOR-CHECK-001`, `GOV-08`,
`GOV-17`) already constrain the deterministic-services, doctor-check, and automation-modification surfaces.
No new requirement is needed; the expansion encodes already-verified finding classes from this investigation.

## Scope and Boundaries

In scope: the pattern-registry full expansion + the skill-health doctor WARN + the registry-header
formal-artifact-approval packet (now in target_paths). Out of scope and explicitly excluded: promoting the
skill-health check to a blocking gate (deferred until triage); the gtkb-hygiene-investigation skill + delta
mode (FAB-20); any per-finding remediation the expanded sweep surfaces (those become their own backlog
items); external Agent Red repository mutation; deploy/push.

## Proposed Implementation

**Area 1 — HYG-051 pattern expansion.** Add 5-8 `[[patterns]]` blocks to
`config/governance/hygiene-sweep-patterns.toml`: content regexes for retired-poller / Claude-Playground
path / `work_list.md` anchor / `CURSOR-*` references and stale relocated paths; presence patterns for
render/tmp dirs and dead-allowlist filenames; template-vs-live hash drift between `.claude/hooks` /
`.codex/gtkb-hooks` / templates. Replace the blanket `exclusion_globs` with per-pattern exclusions so
`.claude/`/`.codex/`/`memory/`/IPA content is scanned for content patterns. The registry-header revision is
gated by a formal-artifact-approval packet recorded at
`.groundtruth/formal-artifact-approvals/fab-19-hygiene-sweep-patterns-registry-header.json`.

**Area 2 — HYG-066 skill-health WARN.** Add a doctor check that runs `check_skill_health.py` and reports its
findings at WARN severity (advisory), so skill health is surfaced on every doctor run without blocking work;
record the triage-to-blocking promotion as a follow-on.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all FAB-19 changes are in-root under `E:\GT-KB\` — the pattern
registry at `config/governance/hygiene-sweep-patterns.toml`, the skill-health checker at
`scripts/check_skill_health.py`, the doctor check in the in-root `groundtruth-kb/src/groundtruth_kb/` tree,
the approval packet under in-root `.groundtruth/formal-artifact-approvals/`, tests under `platform_tests/`,
and this bridge file under `E:\GT-KB\bridge\`. The cluster relocates no file, touches no `applications/`
subtree, and writes no out-of-root artifact; the new patterns DETECT out-of-root references (e.g.
Claude-Playground) without creating any.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` + `GOV-17` (HYG-051) | test: the expanded sweep DETECTS seeded instances of each new pattern class (a retired-poller reference, a Claude-Playground path, a CURSOR-* reference, a render dir) in `.claude/`/`.codex/`/IPA — i.e., the formerly-excluded dirs are now scanned for content patterns; the registry-header revision carries an approval packet at the targeted path |
| `SPEC-DSI-DOCTOR-CHECK-001` (HYG-066) | test: the doctor runs `check_skill_health.py` and reports its findings at WARN severity (not FAIL/blocking); a healthy-skill fixture produces no WARN |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` + `ruff check` AND `ruff format --check` on changed Python |

## Acceptance Criteria

1. **Area 1:** the pattern registry has 5-8 new pattern classes; per-pattern exclusions replace the blanket
   list; the sweep detects seeded instances in the formerly-excluded high-yield directories; the
   registry-header revision is approval-packet-gated and the packet exists at the targeted path.
2. **Area 2:** the doctor surfaces `check_skill_health.py` findings at WARN; promotion-to-blocking is recorded
   as a follow-on.
3. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-19-hygiene-detector-expansion-003.md` with a matching `REVISED` entry at the top of
`bridge/INDEX.md`; append-only (the `-001` NEW and `-002` NO-GO remain). `GOV-FILE-BRIDGE-AUTHORITY-001` is
honored; nothing implements until Loyal Opposition records `GO`.

## Risk and Rollback

- **Risk — a new content pattern false-positives on legitimate text:** each pattern ships with a seeded
  fixture test asserting it matches the drift instance and not a benign mention; per-pattern exclusions scope
  the match. **Rollback:** remove the offending `[[patterns]]` block (config-only).
- **Risk — un-blanketing exclusions scans large dirs and slows the sweep:** content patterns are scoped to
  text-file globs; the sweep remains a read-only census. **Rollback:** restore the prior exclusions.
- **Risk — skill-health WARN adds doctor noise:** it is advisory (WARN), not blocking; promotion to a gate
  is explicitly deferred until the 76 findings are triaged. **Rollback:** revert the doctor check.

## Recommended Implementation Routing

**Cheap-model-draftable once GO'd** — Area 1 is config (pattern regexes seeded from this report's verified
instances) and Area 2 is a small doctor-check wiring; **Opus/Codex finalizes** the pattern-registry approval
packet and confirms the seeded-fixture tests. Pairs with FAB-20 (the investigation skill that consumes this
core).

## Recommended Commit Type

`feat:` — expands the deterministic hygiene detector with new pattern classes + un-blanketed exclusions and
wires the previously-unused skill-health checker into the doctor (net-new detection capability), with a
`fix:`-class element (the sweep was blind to its own high-yield dirs).
