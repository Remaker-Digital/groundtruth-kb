---
name: gtkb-hygiene-sweep
description: Orchestrate the deterministic `gt hygiene sweep` CLI and route deterministic inventory-backed string scans to `gt admin inventory refresh` plus `gt admin inventory scan-strings` instead of ad hoc grep loops. Use when investigating config-drift class observations, inventory-wide string checks, repeated config defects, or session-start hygiene thresholds; classify findings by artifact lifecycle trigger category per DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 and guide owner-gated remediation child-bridge filing.
---

# /gtkb-hygiene-sweep

This skill orchestrates the deterministic `gt hygiene sweep` CLI (companion CLI shipped under WI-3420; VERIFIED via `bridge/gtkb-hygiene-sweep-cli-004.md`) and walks operator + owner through the classify-decide-file workflow that the CLI's deterministic enumeration enables.

This skill body presents **identical content** to both Claude Code and Codex agents via the cross-harness skill-adapter pipeline (per `config/agent-control/harness-capability-registry.toml` + `scripts/generate_codex_skill_adapters.py`). Operations described here behave the same way regardless of which harness invokes the skill.

The deterministic-services-principle split (per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`) places enumeration logic in the CLI and operator judgment + AskUserQuestion routing + remediation bridge guidance in this skill.

## When to invoke

- **Explicit owner direction** — e.g., "run a hygiene sweep" or "use the hygiene sweep skill."
- **After 2+ similar config-defect bridges in a session** — when you notice yourself filing similar small-scope config-drift bridges (stale citations, duplicate registry blocks, missing spec links), invoke this skill to enumerate them in one pass and route through one classification round rather than as ad-hoc one-off remediation.
- **At class-observation thresholds** — the session-start hook surfaces hygiene-related class observations periodically (per `GOV-SESSION-SELF-INITIALIZATION-001`). When the threshold fires, this skill is the recommended response.

This skill is NOT a replacement for owner-directed work prioritization. It surfaces opportunities; it does not auto-execute them.

## What this skill does

1. Invokes `gt hygiene sweep` (the deterministic CLI).
2. Reads the resulting findings JSON and classifies each finding by:
   - **class** — the CLI's deterministic category (e.g., stale-citation, duplicate-block, missing-spec-link).
   - **artifact lifecycle trigger category** — per `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, one of: `deferred`, `blocked`, `superseded`, `unresolved-new`, `verified-stable`.
3. Presents the owner an AskUserQuestion menu of remediation options with explicit lifecycle-state-preserving framing for each option.
4. Files child-bridges for owner-approved remediations **only** on explicit owner AUQ approval, never silently.

## Mandatory pre-flight

Before invoking the CLI:

1. **Read TAFE/dispatcher bridge state** — use the bridge dispatcher
   status/health CLI and TAFE-backed bridge-state surfaces to confirm no
   parallel session is already driving a hygiene-sweep-related thread. Do not
   consult or recreate aggregate queue artifacts as bridge authority.
2. **Confirm impl-authorization scope** — this skill files only the child-bridges it surfaces through owner AUQ; it does not invent new mutation scope.
3. **Verify role assignment** — per `harness-state/role-assignments.json`, confirm the active harness's role includes `prime-builder` (this skill is `required_for_roles = ["prime-builder"]` in the registry).

## Workflow

1. **Invoke the CLI** — run `gt hygiene sweep` per its documented invocation (see `bridge/gtkb-hygiene-sweep-cli-004.md` and the CLI `--help` output). If `gt` is unavailable on PATH in the current harness, fall back to the repo-local entrypoint `python -m groundtruth_kb hygiene sweep` (with `PYTHONPATH=groundtruth-kb/src` when needed). The CLI writes a findings JSON to a deterministic path under `.gtkb-state/hygiene-sweep/<run_id>/`.
2. **Read findings JSON** — load the deterministic finding list, including class label and source-context metadata per finding.
3. **Classify each finding by lifecycle trigger category** per `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` **before** recommending any action:
   - `deferred` — a finding tied to a topic the owner has explicitly deferred.
   - `blocked` — a finding gated on a sibling artifact that has not landed.
   - `superseded` — a finding that points to artifacts already superseded by a newer version.
   - `unresolved-new` — a finding with no prior lifecycle decision; the default category for fresh observations.
   - `verified-stable` — a finding flagging behavior the owner has already verified is acceptable.
4. **Present AskUserQuestion menu** with options framed to PRESERVE the explicit lifecycle state for each finding. Example option phrasings: "File remediation bridge for this finding now (unresolved-new -> in-flight)"; "Defer this finding (unresolved-new -> deferred; capture in Deliberation Archive)"; "Accept this finding as expected behavior (unresolved-new -> verified-stable; capture in DA)".
5. **File child-bridges** for the owner-approved options ONLY. Each child-bridge:
   - Cites this skill invocation's `run_id` in the proposal's `Prior Deliberations` section.
   - Cites the originating CLI finding's class and lifecycle trigger category in the `Specification Links` evidence.
   - Includes the standard `Specification Links`, `Owner Decisions / Input`, spec-derived verification plan, and acceptance criteria sections per `.claude/rules/file-bridge-protocol.md`.

**Per `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, this skill never silently transitions artifact lifecycle states. Every state transition (e.g., `unresolved-new -> deferred`) flows through an explicit owner-decision capture via AskUserQuestion.**

## Inventory String Scans

When the owner, a bridge proposal, or a verification plan requires an
inventory-wide string search across declared GT-KB artifacts, use the
deterministic inventory CLI rather than `rg`, grep, or hand-rolled file loops as
authoritative evidence. Ad hoc search is acceptable for local exploration, but
it must not be cited as the inventory-wide scan result when this deterministic
process is required.

1. Run `gt admin inventory refresh --json` first. If `gt` is unavailable, use
   `python -m groundtruth_kb.cli admin inventory refresh --json` from the
   project venv. Treat missing artifacts or inventory expansion errors as the
   finding to report before scanning strings.
2. Run `gt admin inventory scan-strings --match <literal> --report-only --json`
   for one-off literal checks, or
   `gt admin inventory scan-strings --match-file <path> --report-only --json`
   for a deterministic set of strings. Use `--critical-class`,
   `--warn-class`, `--critical-path`, and `--warn-path` when the evidence needs
   critical vs. warning classification.
3. Preserve the command, JSON summary, and any markdown ledger path in the
   bridge proposal, implementation report, verification, or hygiene report that
   depends on the scan. Critical hits are investigation/remediation inputs with
   `remediation_status: untriaged`; the scanner itself does not remediate.
4. For no-hit sentinels, use a fresh unique literal for each verification run.
   Do not reuse a sentinel after writing that literal into a bridge report or
   other scanned artifact, because the report itself can become the hit.

## Output

Per skill invocation, surfaces:

- **Findings count by class** — e.g., "12 stale-citation, 3 duplicate-block, 5 missing-spec-link".
- **Findings count by lifecycle trigger category** — e.g., "18 unresolved-new, 1 deferred, 1 superseded".
- **Ranked remediation options** — based on owner-selected priorities (e.g., release-blocking class first, then governance hygiene, then convenience).
- **Per-finding child-bridge slug suggestions** — kebab-case slugs like `gtkb-hygiene-stale-citation-<short-hash>-001` ready for filing via `gtkb-bridge-propose`.

## Does NOT

- **Auto-file remediation bridges.** Every child-bridge filing requires explicit owner AUQ approval. The skill is a surfacing + classifying surface, not a mutation surface.
- **Expand the pattern set.** Pattern expansion (adding new finding classes to the CLI) requires a separate bridge thread, an owner AUQ, and CLI implementation work.
- **Modify source files directly.** This skill writes ONLY child-bridge proposal files (under `bridge/`) and the AskUserQuestion-emitted decision-evidence records. It does NOT mutate any source, config, test, or rule file.
- **Silently transition artifact lifecycle states.** Per `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, lifecycle transitions are explicit owner decisions; this skill captures the decision evidence via AskUserQuestion and threads it into the child-bridge filing.

## Required reading

Before any operation:

- `.claude/rules/file-bridge-protocol.md` — protocol root contract.
- `.claude/rules/codex-review-gate.md` — review-gate constraints for child-bridge proposals.
- `.claude/rules/deliberation-protocol.md` — Deliberation Archive search obligations.
- `.claude/rules/operating-model.md` — canonical vocabulary.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (in MemBase) — lifecycle trigger category definitions and required confirmation flows.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — service-layer/skill-layer split rationale.
- For Prime Builder: `.claude/rules/prime-builder-role.md`.

## Companion CLI

The companion CLI is `gt hygiene sweep`, landed under WI-3420 (VERIFIED via `bridge/gtkb-hygiene-sweep-cli-004.md`). The CLI provides:

- Deterministic finding enumeration scoped by `exclusion_globs` (per `config/governance/hygiene-sweep-patterns.toml`).
- JSON output suitable for skill consumption.
- Read-only operation — the CLI does not mutate any source.

Refer to `bridge/gtkb-hygiene-sweep-cli-004.md` and the CLI's `--help` output for invocation details.

The inventory string-scan companion CLI is `gt admin inventory refresh` plus
`gt admin inventory scan-strings`, introduced by
`bridge/gtkb-inventory-string-scan-admin-cli-003.md`; its implementation and
verification record stays with that same bridge thread as the lifecycle
advances. It provides deterministic artifact-inventory expansion, literal
string matching, critical/warn classification, JSON output, and read-only
markdown ledger evidence for follow-on remediation work.

## Cross-harness implementation notes

- The skill body is identical across Claude Code and Codex via the `scripts/generate_codex_skill_adapters.py` adapter pipeline. The Codex adapter at `.codex/skills/gtkb-hygiene-sweep/SKILL.md` carries a `<!-- GTKB-CODEX-SKILL-ADAPTER -->` marker; do NOT edit the adapter directly. Edit the canonical at `.claude/skills/gtkb-hygiene-sweep/SKILL.md` and regenerate via `python scripts/generate_codex_skill_adapters.py --update-registry`.
- Hook-layer behavior differs between harnesses by necessity (different schemas: `.claude/settings.json` JSON vs `.codex/hooks.json` JSON). Hook handler scripts are shared regardless. This skill does not depend on hook-layer behavior; it operates entirely through CLI invocation + AskUserQuestion + bridge-proposal filing.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
