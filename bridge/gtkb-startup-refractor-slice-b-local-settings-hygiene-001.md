NEW

# GTKB-STARTUP-REFRACTOR-001 Slice B — Machine-Local Settings Hygiene

bridge_kind: prime_proposal
Document: gtkb-startup-refractor-slice-b-local-settings-hygiene
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC

author_identity: Claude Code Prime Builder (PAUTH-authorized implementation)
author_harness_id: B
author_session_context_id: 2026-06-03-gtkb-startup-refractor-slice-b
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-STARTUP-REFRACTOR-001-GTKB-STARTUP-REFRACTOR-001-SLICES-A-E-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-GTKB-STARTUP-REFRACTOR-001
Work Item: WI-4269

target_paths: ["scripts/check_local_settings_hygiene.py", "platform_tests/scripts/test_check_local_settings_hygiene.py", ".claude/settings.local.json"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice B of GTKB-STARTUP-REFRACTOR-001 (WI-4269), covering advisory finding **F3**:
`.claude/settings.local.json` carries obsolete legacy-archive (`E:\Claude-Playground`)
read/`rm`/`rmdir` allowances and at least one literal credential-bearing command
allowance, in conflict with the project-root-boundary and credential-safety
posture. This slice does two things:

1. **Local cleanup (machine-local, in-root):** remove from `.claude/settings.local.json`
   (a) all legacy-archive path allowances — per the owner decision (2026-06-03
   AUQ) **remove all archive-path access**, retaining none; (b) any literal
   credential-bearing command allowance; (c) destructive (`rm`/`rmdir`)
   allowances scoped to the archive path. `.claude/settings.local.json` is
   git-ignored machine-local state, so this edit is the live-runtime security
   fix and is not itself a committed artifact.
2. **Durable guard (committed):** add `scripts/check_local_settings_hygiene.py`
   — a deterministic, read-only check that scans `.claude/settings.local.json`
   for the forbidden pattern classes (legacy-archive path references,
   credential-shaped literals, archive-scoped destructive allowances) and exits
   non-zero with a clear report when any are found — plus a test. This prevents
   silent re-introduction of the cleaned-up patterns.

A standalone guard script (rather than a new `doctor.py` check) is proposed to
keep blast radius minimal for this hygiene slice; promoting it into the doctor
aggregate is a candidate follow-on, not required here. The slice separates
Prime Builder vs Loyal Opposition permission posture only to the extent of
removing the forbidden allowances; a full PB/LO permission split is deferred.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` — settings.local.json is part of the
  effective startup/runtime environment inventoried by Slice A. PAUTH-linked.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — PAUTH-linked governing spec.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking. The legacy-archive path
  is out-of-root; removing its live allowances enforces the in-root boundary.
  All target paths are in-root.
- `GOV-ARTIFACT-APPROVAL-001` — credential-safety discipline; this slice removes
  credential literals from the allowlist.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage compliance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + WI + PAUTH linkage.
- `GOV-STANDING-BACKLOG-001` — WI-4269 linkage.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory); `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory); `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).

## Prior Deliberations

- `DELIB-20260622` — owner PAUTH decision (covers WI-4269).
- `bridge/gtkb-startup-refractor-scoping-002.md` — scoping GO defining Slice B.
- `bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-004.md` — Slice A VERIFIED (the control-map classifies settings.local.json as a local-only active surface).
- `DELIB-0687` — VERIFIED credential-scan narrowing (canonical credential pattern set informing the credential-literal detector).

## Owner Decisions / Input

- **Owner AUQ (2026-06-03)** — "Remove all archive-path access" (no legacy-archive
  retention). This proposal implements that choice: no archive-path allowance is
  retained.
- Implementation authority: project PAUTH (active), owner decision `DELIB-20260622`,
  allowed mutation classes include `config`, `source`, `test`.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirements are advisory F3,
`.claude/rules/project-root-boundary.md` (archive-only prohibition), and the
credential-safety discipline of `GOV-ARTIFACT-APPROVAL-001`. No new specification
is required; this slice enforces existing constraints on a machine-local surface.

## Spec-Derived Verification Plan

| Specification / Finding | Spec-to-test mapping | Command | Expected |
|---|---|---|---|
| F3 / `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `test_check_local_settings_hygiene.py` asserts the guard flags legacy-archive path references and exits non-zero on a fixture containing them | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_local_settings_hygiene.py -q --no-header -p no:cacheprovider` | PASS |
| `GOV-ARTIFACT-APPROVAL-001` (credential safety) | same test asserts the guard flags a credential-shaped literal allowance | (same pytest) | PASS |
| cleaned live file | run the guard against the post-cleanup `.claude/settings.local.json` | `groundtruth-kb/.venv/Scripts/python.exe scripts/check_local_settings_hygiene.py` | exit 0 (no findings) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | lint + format on the new files | `ruff check` / `ruff format --check` on the two new Python files | clean |

The implementation report will carry observed results, including a redacted
before/after summary of the settings.local.json cleanup (no credential values
reproduced).

## Risk / Rollback

The committed deliverables are a read-only guard script + a test — no behavior
change to any runtime path. The settings.local.json cleanup is a local edit; if
it removed an allowance the owner later wants, it is re-addable. Rollback of the
committed parts is a single-commit revert.

## Recommended Commit Type

`feat` — adds a new deterministic guard script (net-new capability) plus its
test. (The local settings.local.json cleanup is not a committed artifact.)

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
