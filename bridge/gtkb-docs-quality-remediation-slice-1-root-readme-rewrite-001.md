# GTKB-DOCS-QUALITY-REMEDIATION — Slice 1: Workspace-Root README Rewrite As GT-KB IDP Landing Page

**Status:** NEW
**Author:** Prime Builder (claude harness B)
**Date:** 2026-05-08
**Session:** S337
**Umbrella:** `GTKB-DOCS-QUALITY-REMEDIATION` (slice-0 VERIFIED at `bridge/gtkb-docs-quality-remediation-004.md`)

## Purpose

Rewrite the workspace-root `README.md` so it presents this repository's
identity correctly. Currently the file opens with `# Agent Red Customer
Experience` and links to badges, wiki, and issues at
`Remaker-Digital/agent-red-customer-engagement`, but the configured
`origin` remote is `Remaker-Digital/groundtruth-kb` and live operating
rules say Agent Red is a separate project not part of GT-KB. This slice
addresses Loyal Opposition finding **F1** from the originating
INSIGHTS-2026-05-07-06-39 report.

Per the S337 owner positioning AUQ, the new README leads with the
**Internal Developer Platform** framing canonically defined in
`.claude/rules/operating-model.md` §1.

## Specification Links

**Required (cross-cutting, blocking — per `config/governance/spec-applicability.toml`):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-mediated implementation work.
  Triggered by `bridge/**` path scope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposals
  must cite every relevant governing specification. Triggered by
  content ("Specification Links", "implementation proposal",
  "bridge proposal").
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must
  derive from linked specifications. Triggered by content
  ("verification", "VERIFIED").
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application/root placement
  honored. Directly governs F1: the workspace-root README is the
  primary surface presenting GT-KB identity. Triggered by content
  ("Agent Red") and by path `.claude/rules/project-root-boundary.md`.

**Required (rule-cited soft authority):**

- `.claude/rules/file-bridge-protocol.md` — proposal/review/verification
  protocol; "Mandatory Specification Linkage Gate", "Mandatory Owner
  Decisions / Input Section Gate".
- `.claude/rules/codex-review-gate.md` — no implementation without
  Codex GO.
- `.claude/rules/project-root-boundary.md` — Agent Red is a separate
  project; the GT-KB workspace-root README must not present Agent Red
  as the GT-KB landing page. The new README must not link to or treat
  Agent Red files as live GT-KB artifacts. Allowed: a single-line
  separate-project pointer to
  `https://github.com/mike-remakerdigital/agent-red` for readers
  arriving via legacy links, **only if it does not imply Agent Red is
  a GT-KB component**. The proposal's default position is **no Agent
  Red mention** in the new README.
- `.claude/rules/operating-model.md` §1 — canonical GT-KB framing as
  an IDP for AI-assisted software development; the README's lead
  paragraph is derived from this section.
- `.claude/rules/operating-model.md` §2 — canonical terminology
  ("application", "platform", "hosted application", "specification",
  "release", "MemBase", "Deliberation Archive", "dashboard"). The new
  README must use these terms consistently with §2.
- `.claude/rules/canonical-terminology.md` — full glossary; any term
  introduced in the README must align with the canonical entries
  (GT-KB, GroundTruth KB, MemBase, Deliberation Archive, Prime Builder,
  Loyal Opposition, file bridge).
- `.claude/rules/canonical-terminology.md` §"project-resource alias
  resolution" — configured GT-KB resource URL is
  `https://github.com/Remaker-Digital/groundtruth-kb`. README badges
  and links must use this URL.

**Advisory (cross-cutting, advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — README is a durable artifact
  presenting the project's identity; the rewrite preserves the audit
  trail of what changed and why.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across the
  rewrite proposal, post-impl report, and the historical Agent Red
  README content (preserved in git history at commits `dbe21f94` and
  `31c51ceb`, not preserved as a live artifact).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — slice-1 lifecycle progresses
  through candidate → NEW → GO → committed → VERIFIED states; this
  proposal carries forward the same lifecycle discipline used by the
  slice-0 round-trip.

**Originating evidence:**

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-07-06-39-GTKB-DOCUMENTATION-QUALITY-REVIEW.md`
  §F1 — Workspace Root README Presents Agent Red, Not GT-KB.
- `bridge/gtkb-docs-quality-remediation-001.md` — slice-0 umbrella
  proposal listing slice 1 as the F1 remediation slice.
- `bridge/gtkb-docs-quality-remediation-004.md` — Codex VERIFIED at
  slice 0 confirming the umbrella decomposition.

## Prior Deliberations

A focused `search_deliberations()` for prior reviews on the GT-KB
workspace-root README at proposal time surfaces:

- **Repo-identity migration commits** (introduced the current Agent
  Red root README in this tree):
  - `dbe21f94` — "Migrate repo references to mike-remakerdigital/agent-red"
  - `31c51ceb` — "GitHub project refresh — README, issue templates, SECURITY.md"
  - `2bdb1b5e` — "chore: publish Agent Red governance and release artifacts"
- **S336 AUQ answer** (Mike, 2026-05-07): "Full 8-finding remediation"
  — authorized the umbrella project covering F1 through F8.
- **S337 AUQ answer** (Mike, 2026-05-08): "Internal Developer Platform
  (Recommended)" — selected the README framing.
- **Codex Slice-0 GO** (`bridge/gtkb-docs-quality-remediation-002.md`):
  "Slice 1 root README first because it is the highest first-impression
  defect, lowest risk, and unblocks evaluation of the repo-identity
  surface before any other docs work proceeds against the wrong
  identity."
- **No prior deliberations** were found that explicitly debated
  whether the workspace-root README should remain Agent Red after the
  GT-KB platform extraction. The current state appears to be drift
  rather than a deliberate choice.

## Scope

**In scope:**

- Rewrite `README.md` (workspace-root) in full as GT-KB IDP landing
  page.
- Update or remove all badges, wiki links, issue links, and quick
  links currently pointing to
  `Remaker-Digital/agent-red-customer-engagement`.

**Out of scope:**

- `groundtruth-kb/README.md` — the package-level README is slice 4
  (version coherence) territory.
- Any `docs/` files — those are slices 2, 3, 5, 6, 7.
- Any CI workflow files — slice 2 territory.
- KB MemBase writes — none required for this slice.
- Repo settings (description, topics, default branch) — owner-managed
  GitHub repo settings are out of scope; the README rewrite is the only
  in-tree artifact this slice mutates.

## Implementation Plan

The new `README.md` follows this section structure, derived from
`.claude/rules/operating-model.md` §1 framing:

1. **Title block:** `# GroundTruth KB (GT-KB)` with one-sentence IDP
   tagline.
2. **What it is:** 2–3 paragraphs naming GT-KB as an Internal Developer
   Platform for AI-assisted software development; restate the
   `operating-model.md` §1 first paragraph in README-appropriate prose;
   distinguish *application* (the lifecycle object), *platform* (GT-KB),
   and *hosted application* (deployed in service) per §2 vocabulary.
3. **Status badges:** Python tests / lint badges pointing at the
   `Remaker-Digital/groundtruth-kb` workflows (replacing the current
   `agent-red-customer-engagement` badges). License, Python version,
   PyPI version (when 0.7.x is published).
4. **Key components:** brief list naming MemBase
   (`groundtruth.db`), Deliberation Archive, file bridge protocol
   (Prime Builder ↔ Loyal Opposition), `gt` CLI, dashboard. Each
   bullet links to the canonical doc page (e.g.,
   `groundtruth-kb/docs/start-here.md`).
5. **Quick links table:** GitHub repo URL, PyPI page (when published),
   `groundtruth-kb/README.md` for package install/quick-start,
   `groundtruth-kb/docs/start-here.md` for new adopters,
   `groundtruth-kb/docs/cto-evaluation.md` for evaluators,
   `AGENTS.md` and `.claude/rules/` for harness governance, `LICENSE`,
   `SECURITY.md` if present.
6. **Adopting GT-KB:** one-paragraph pointer noting that adopters
   install the package and run `gt project init` to scaffold a
   project; defer detailed install flow to
   `groundtruth-kb/README.md` and `start-here.md`.
7. **Repository status:** brief note on current platform version
   (sourced from `groundtruth-kb/src/groundtruth_kb/__init__.py:16`
   `__version__ = "0.7.0rc1"`) with a one-line statement of the
   release-candidate posture. Slice 4 (version coherence) will
   generalize this to a single source of truth; this slice uses the
   value as-is.
8. **Contributing:** brief pointer to
   `groundtruth-kb/CONTRIBUTING.md` (if present) or the `bridge/`
   protocol.
9. **License + copyright:** AGPL-3.0-or-later, © 2026 Remaker Digital.

**No Agent Red mentions** in the rewritten README, per
`project-root-boundary.md`. If Codex review surfaces a need for a
single-line "Looking for Agent Red?" redirect for legacy URL traffic,
that can be added at -002 or as a slice-1.5 follow-up; the proposal's
default is no Agent Red text in the file.

**Historical preservation:** the current Agent Red README content is
preserved in git history (latest at `2bdb1b5e`); no separate archival
file is created in this slice. Readers who need the prior content can
`git show 2bdb1b5e:README.md`.

## Specification-Derived Verification

The post-implementation report at -003 will provide a spec-to-test
mapping. The verification surface for slice 1 is:

| Linked specification | Verification check | Command |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` + `project-root-boundary.md` | No Agent Red branding in the workspace-root README | `rg -n "Agent Red Customer Experience\|agent-red-customer-engagement" README.md` returns no matches |
| `operating-model.md` §1 | New README leads with IDP framing | `rg -n "Internal Developer Platform" README.md` returns ≥1 match in the opening paragraphs |
| `canonical-terminology.md` §"project-resource alias resolution" | Badges and links use `Remaker-Digital/groundtruth-kb` | `rg -n "github.com/Remaker-Digital/groundtruth-kb" README.md` returns ≥1 match; `rg -n "agent-red-customer-engagement" README.md` returns no matches |
| `operating-model.md` §2 canonical terminology | New README uses "MemBase", "file bridge", "Prime Builder", "Loyal Opposition" canonically (no aliases without expansion at first use) | `rg -n "MemBase\|file bridge\|Prime Builder\|Loyal Opposition" README.md` returns ≥4 matches |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal cites all triggered specs | Pre-filing applicability preflight reports `missing_required_specs: []` |

The post-impl report will execute these commands against the rewritten
file and paste outputs verbatim per
`.claude/rules/file-bridge-protocol.md` "Mandatory
Specification-Derived Verification Gate".

## Acceptance Criteria — Slice 1 GO

For Codex to issue GO on this proposal, all of the following must hold:

- The README structural outline above is acceptable, or a counter-
  structure is proposed in NO-GO.
- The "no Agent Red mention" default is acceptable, or a redirect-line
  exception is proposed in NO-GO.
- The badge/link target (`Remaker-Digital/groundtruth-kb`) is correct
  per the canonical alias entry, or a substitute target is proposed in
  NO-GO.
- The verification check set above is sufficient as the slice-1 spec-
  to-test mapping, or additional checks are proposed in NO-GO.
- Slice 1 does not require a follow-on slice 1.5 (e.g., for legacy
  URL redirects); if Codex finds the redirect concern blocking, slice
  1 should NO-GO with a redirect-line exception or a slice-1.5 plan.

## Test Plan (slice 1 implementation)

Implementation will, in order:

1. Read current `README.md` (single file, 217 lines per pre-rewrite
   `wc -l` to be confirmed at impl time).
2. Write the new `README.md` per the structural outline above.
3. Run the 5 `rg` verification commands listed in
   §"Specification-Derived Verification" against the new file.
4. Verify pre-commit hooks pass: secret scan (0 findings), inventory
   drift check (PASS), markdownlint (slice 7 will add config; for
   slice 1, only the existing minimal style discipline applies).
5. Stage and commit `README.md` only (single-file scoped commit). Bridge
   files (-002, -003 follow-ups) are not part of slice-1 production
   commits.
6. File post-impl report at
   `bridge/gtkb-docs-quality-remediation-slice-1-root-readme-rewrite-003.md`
   with the verification command outputs and the pre-impl/post-impl
   diff stat.

## Risk And Rollback

**Risk:** very low. README is a single file with no runtime dependents.
The current README content is preserved in git history. No CI, deploy,
KB write, or external system depends on the README content.

**Risk surface that does exist:**

- External links to README anchors (e.g., from blog posts or other
  repos) may break if the new README's heading IDs differ from the
  current ones. Mitigation: the current README headings (Quick Links,
  AI Assistant Guide, GT-KB Dashboard, Session Startup Guide) are
  unlikely to be linked externally because the project just rebranded
  from Agent Red. The risk is treated as accepted.
- GitHub's repo description / topics / social preview may still
  reference Agent Red. These are repo settings outside the working
  tree; the README rewrite alone does not fix them. Recommendation
  for owner: update repo settings via the GitHub web UI after slice-1
  commit lands. Out of scope for this proposal.

**Rollback:** `git revert` of the slice-1 implementation commit
restores the previous README content in one operation.

## Owner Decisions / Input

- **2026-05-07, AskUserQuestion answer (S336):** Mike selected "Full
  8-finding remediation" authorizing the umbrella scope. This
  authorization extends to slice 1 implementation per the umbrella
  acceptance contract recorded in `bridge/gtkb-docs-quality-remediation-001.md`
  §"Owner Decisions / Input": "Each slice's bridge proposal must
  obtain its own Codex GO; no implementation slice is pre-approved by
  this scoping selection." → slice 1 needs Codex GO at -002 before
  README edits.
- **2026-05-08, AskUserQuestion answer (S337):** Mike selected
  "Internal Developer Platform (Recommended)" in response to "How
  should the workspace-root README position GT-KB to a first-time
  GitHub visitor?" — directly authorizes the IDP framing chosen for
  this proposal's structural outline.
- **No further owner decision pending** for slice 1 GO. The legacy-URL
  redirect question (whether to include a one-line "Looking for Agent
  Red?" pointer) can be raised at slice-1 implementation time only if
  Codex review surfaces it as blocking; otherwise the proposal's
  default ("no Agent Red mention") stands.

## Recommended Commit Type

`docs:` — slice 1 rewrites a production documentation file
(`README.md`). Per `.claude/rules/file-bridge-protocol.md`
"Conventional Commits Type Discipline (Implementation Reports)",
`docs:` is the discipline-correct type for governance/rule/runbook-
only edits, with the README counted as a doc surface.

The slice-1 implementation commit will be:

```
docs(readme): rewrite workspace-root README as GT-KB IDP landing page (slice 1)
```

The slice-1 closing commit (post-impl + Codex VERIFIED, mirroring
slice-0) will use `chore(bridge):` since that commit only adds bridge
audit-trail artifacts.

## Files Changed (slice 1 implementation commit)

- `README.md` (modify; full rewrite).

No other files. The bridge thread files (-001 this proposal, -002
Codex GO, -003 post-impl, -004 Codex VERIFIED) commit separately on
their own bridge-protocol cadence and are not bundled into the slice-1
implementation commit.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md` "Mandatory Pre-Filing
Preflight Subsection",
`python scripts/bridge_applicability_preflight.py --bridge-id
gtkb-docs-quality-remediation-slice-1-root-readme-rewrite` will be run
after this file is saved and the INDEX entry is added. Result will be
reported in the chat turn that completes slice-1 filing; if the
preflight reports any `missing_required_specs`, the proposal will be
revised before Codex review begins.

## © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
