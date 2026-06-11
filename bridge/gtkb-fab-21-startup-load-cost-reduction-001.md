NEW

bridge_kind: prime_proposal
Document: gtkb-fab-21-startup-load-cost-reduction
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4433
Project Authorization: PAUTH-FAB21-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: e45ccf07-99f6-4ad6-b572-570a76a264a2
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["scripts/session_self_initialization.py", "scripts/cross_harness_bridge_trigger.py", "scripts/bridge_verified_backlog_reconciler.py", "scripts/posttooluse_hook_dispatcher.py", ".claude/settings.json", ".claude/hooks/**", ".claude/rules/canonical-terminology.md", ".claude/rules/operating-model.md", ".claude/rules/acting-prime-builder.md", ".claude/rules/bridge-essential.md", ".claude/rules/project-root-boundary.md", "config/governance/canonical-terminology.toml", "platform_tests/**"]

No KB mutation: all FAB-21 changes are source (hook consolidation, session_self_initialization profiler), config (settings.json hook registration, canonical-terminology.toml required-terms), protected narrative (.claude/rules/*.md, each under a per-file narrative-approval packet), and tests; no `groundtruth.db` write. `groundtruth.db` is intentionally NOT in target_paths.

---

# FAB-21 — Startup Load-Cost Reduction

WI-4433 (FAB-21) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-008 (per-tool-call hook latency floor), HYG-025
(38 auto-loaded rule files / 336KB / ~80K tokens, 34% over the platform's own budget), HYG-028 (always-loaded
rules/glossary cite retired `.ollama/` and `tests/` paths). Source advisory:
`bridge/gtkb-fable-investigation-advisory-001.md`.

Common theme: GT-KB's own session-startup surface is the largest recurring fixed cost on the platform — a
wall-clock tax (hooks) and a token tax (rules payload) paid by every interactive session and every dispatched
worker — and parts of it actively misdirect agents with stale pointers.

## Summary

- **HYG-008 (hook wall-clock):** every Bash tool call fires 10 cold `python.exe` hook spawns (12 for
  Write/Edit), a measured ~1.05s floor; a ~500-call session pays ~8-15 min of pure hook wall-clock, and the
  same stack runs in every headless worker. **Owner decision: Partial, measure-first.**
- **HYG-025 (rules token payload):** all 38 `.claude/rules/*.md` auto-load = 335,977 bytes (~80K tokens)
  before any work, 34% over the platform's own `STARTUP_PRUNING_TOTAL_WARN_BYTES = 250,000`;
  `canonical-terminology.md` alone is 84,427 bytes and is paid by Codex sessions too. **Owner decision: Full
  program, sequenced.**
- **HYG-028 (stale always-loaded pointers):** the always-loaded rules/glossary still cite retired `.ollama/`
  (migrated to `.api-harness/`, 9 refs) and the old `tests/` tree (renamed `platform_tests/`, 4 refs); the
  glossary is the designated DA read-surface, so these misdirect every fresh session. **Owner decision: One
  batch now, all 5 files.**

## Specification Links

- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — the startup token budget the rules payload exceeds (HYG-025).
- `GOV-SESSION-SELF-INITIALIZATION-001` — requires startup token-reduction options (index-first, progressive
  disclosure, targeted loading); the glossary IA realizes them (HYG-025).
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — the glossary is the DA read-surface; the core/detail split and the
  stale-pointer sweep preserve its authority (HYG-025/028).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — always-loaded pointers must match live paths; the stale `.ollama/` and
  `tests/` citations are freshness drift (HYG-028).
- `GOV-17` (Automation script modification approval gate) — the PostToolUse hook consolidation modifies
  automation; it rides the governed approval path and weakens no enforcement (HYG-008).
- `GOV-08` (Knowledge Database is the single source of truth) — the canonical-terminology.toml required-terms
  matrix must stay green across the glossary IA change.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-21 changes are in-root; see Isolation Placement
  Compliance below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the rules/config/glossary changes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `NEW` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-008/025/028).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB21-REMEDIATION-20260610` — this cluster's 3 owner AUQ decisions (below).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — recurring fixed costs (wall-clock + tokens) are a defect to
  engineer out, not absorb.
- _Sequencing: HYG-025 explicitly lands the 4360 profiler baseline before any structural glossary change._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB21-REMEDIATION-20260610`:

1. **HYG-008 = Partial, measure-first.** Add a one-line per-hook duration log for ~a week, then consolidate
   the 4 PostToolUse spawns (heartbeat + `cross_harness_bridge_trigger` + `bridge_verified_backlog_reconciler`
   + spec-event-surfacer — they share the state-dir and the `groundtruth_kb` import) into one entrypoint
   (~40% cut). Do NOT touch the PreToolUse safety-gate stack; no enforcement weakening.
2. **HYG-025 = Full program, sequenced.** Land the 4360 profiler baseline first, THEN a glossary
   information-architecture change (always-loaded core terms + on-demand detail keyed to the doctor's
   `canonical-terminology.toml` required-terms matrix), THEN dedup + era-file archival. Each protected-narrative
   edit uses a per-file narrative-approval packet; doctor canonical-term checks stay green.
3. **HYG-028 = One batch now, all 5 files.** Per-file narrative-approval packets replacing `.ollama/` →
   `.api-harness/` and `tests/scripts/` → `platform_tests/scripts/` across `canonical-terminology.md`,
   `operating-model.md`, `acting-prime-builder.md`, `bridge-essential.md`, `project-root-boundary.md`; add a
   citation-grep line item to the restructure checklist.

## Requirement Sufficiency

**Existing requirements sufficient.** The dispositions are fixed by `DELIB-FAB21-REMEDIATION-20260610`; the
governing specifications (`DCL-SESSION-STARTUP-TOKEN-BUDGET-001`, `GOV-SESSION-SELF-INITIALIZATION-001`,
`GOV-GLOSSARY-AS-DA-READ-SURFACE-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-17`, `GOV-08`) already
constrain the startup-budget, glossary-read-surface, freshness, automation-modification, and SoT surfaces. No
new requirement is needed; HYG-008/025/028 are verified measurements with owner-chosen dispositions.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`: FAB-21 performs **no bulk backlog operation** — it
writes nothing to `work_items`. The protected-narrative edits (HYG-025/028) are gated per file by the
formal-artifact-approval / narrative-approval packet discipline, and the glossary archival produces an
inventory of archived-vs-retained entries for review. No bulk MemBase mutation is authorized by this proposal.

## Scope and Boundaries

In scope: the measure-first hook duration log + PostToolUse-spawn consolidation; the 4360 profiler baseline
+ glossary core/detail IA + dedup + era-file archival; the stale-pointer sweep across 5 always-loaded rule
files + a restructure-checklist citation-grep step. Out of scope and explicitly excluded: any change to the
PreToolUse safety-gate stack (HYG-008 is PostToolUse-only); any enforcement weakening; the broader
orphan-citation remediation stream beyond the always-loaded subset; deploy/push. This proposal absorbs the
advisory's FAB-21 overlap (the 4360/4361/4403 items) by describing them here.

## Proposed Implementation

**Area 1 — HYG-008 hook latency (measure-first, PostToolUse only).** Add a one-line per-hook duration log
(write to a `.gtkb-state/` JSONL) to the hook-running path; after a measurement window, introduce a single
`scripts/posttooluse_hook_dispatcher.py` entrypoint that in-process routes the 4 PostToolUse jobs (heartbeat,
`cross_harness_bridge_trigger`, `bridge_verified_backlog_reconciler`, spec-event-surfacer) — they already
share the state-dir and the `groundtruth_kb` import — and update `.claude/settings.json` to register the one
dispatcher in place of the 4 spawns. The PreToolUse safety-gate matrix is untouched.

**Area 2 — HYG-025 startup-payload program (sequenced).** (1) Land the 4360 profiler in
`scripts/session_self_initialization.py` to report the rules-payload byte/token baseline against the
`STARTUP_PRUNING_TOTAL_WARN_BYTES` budget. (2) Glossary IA: split `canonical-terminology.md` into an
always-loaded core-terms surface + an on-demand detail reference keyed to `canonical-terminology.toml`'s
required-terms matrix (doctor canonical-term checks stay green). (3) Dedup duplicated normative blocks +
archive era-stranded rule files. Each `.claude/rules/*.md` edit carries its per-file narrative-approval packet.

**Area 3 — HYG-028 stale-pointer sweep (one batch).** Per-file packets replacing `.ollama/` → `.api-harness/`
(9 refs across `canonical-terminology.md` + `operating-model.md`) and `tests/scripts/` →
`platform_tests/scripts/` (4 refs across `acting-prime-builder.md`, `bridge-essential.md`,
`canonical-terminology.md`, `project-root-boundary.md`); add a citation-grep line item to the restructure
checklist so the always-loaded surface is swept on future migrations.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all FAB-21 changes are in-root under `E:\GT-KB\` — the hooks/scripts
under `scripts/` and `.claude/hooks/`, the settings file at `.claude/settings.json`, the rule files under
`.claude/rules/`, the terminology matrix at `config/governance/canonical-terminology.toml`, tests under
`platform_tests/`, and this bridge file under `E:\GT-KB\bridge\`. The cluster relocates no application file,
touches no `applications/` subtree, and writes no out-of-root artifact; HYG-028 in fact REMOVES stale
references to a retired `.ollama/` path, improving in-root pointer accuracy.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-17` + HYG-008 (PostToolUse consolidation, no enforcement change) | test: the 4 PostToolUse jobs run via the single dispatcher entrypoint and produce identical effects (heartbeat write, trigger dispatch signature, reconciler pass, surfacer output); the PreToolUse safety-gate matrix in settings.json is byte-unchanged; a duration log is emitted |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` + `GOV-SESSION-SELF-INITIALIZATION-001` (HYG-025) | test: the profiler reports the rules-payload byte/token total against the 250,000 budget; after the IA change the always-loaded core surface is under an owner-set budget and the doctor canonical-term required-terms check stays green |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` (HYG-028) | test: grep of the 5 always-loaded rule files shows zero `.ollama/` and zero `tests/scripts/` references; all replaced pointers resolve to live paths (`.api-harness/routing.toml`, `platform_tests/scripts/...`) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/...`; `ruff check` AND `ruff format --check` on changed Python; each protected-narrative edit has its per-file narrative-approval packet |

## Acceptance Criteria

1. **HYG-008:** a per-hook duration log exists; the 4 PostToolUse spawns run via one dispatcher entrypoint with
   identical effects; the PreToolUse safety-gate registration is unchanged.
2. **HYG-025:** the 4360 profiler reports the payload baseline; `canonical-terminology.md` is split into an
   always-loaded core + on-demand detail with the doctor required-terms check green; dedup + era-archival
   land; per-file narrative packets recorded.
3. **HYG-028:** zero `.ollama/` and zero stale `tests/scripts/` references remain in the 5 always-loaded rule
   files; the restructure checklist gains a citation-grep step.
4. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-21-startup-load-cost-reduction-001.md` with a matching `NEW` entry at the top of
`bridge/INDEX.md`; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored; nothing implements until Loyal
Opposition records `GO`, and each protected-narrative edit additionally requires its per-file
narrative-approval packet at implementation time.

## Risk and Rollback

- **Risk — hook consolidation changes effects / hides a failure:** the verification test asserts the 4 jobs
  produce identical effects via the dispatcher; the PreToolUse safety matrix is explicitly untouched. The
  measure-first window precedes consolidation. **Rollback:** restore the 4 separate registrations in
  settings.json (config-only revert).
- **Risk — glossary IA breaks the doctor canonical-term check or loses a term:** the IA is keyed to the
  required-terms matrix and gated by the doctor check; the archival step keeps an inventory of moved entries.
  **Rollback:** restore the consolidated glossary (the moved detail is preserved in the on-demand reference).
- **Risk — a pointer sweep over-replaces a legitimate historical mention:** each replacement is per-file,
  packet-gated, and verified by grep against live paths; historical-evidence mentions are preserved.
  **Rollback:** revert the specific rule-file edit.

## Recommended Implementation Routing

**Claude/Codex (governance + protected-narrative).** HYG-025/028 edit protected `.claude/rules/*.md` with
per-file approval packets and must keep the doctor canonical-term check green — governance-finicky, not
cheap-draftable. HYG-008's PostToolUse dispatcher is source work that needs careful equivalence testing.
Sequenced per the owner decision: profiler baseline → glossary IA → dedup/era; HYG-008 measure-first;
HYG-028 as one batch.

## Recommended Commit Type

`perf:` — the dominant change is reducing the fixed per-session wall-clock (hook consolidation) and token
(rules payload) cost, with a `fix:`-class element (HYG-028 stale-pointer correction) and `docs:`-class
protected-narrative edits.
