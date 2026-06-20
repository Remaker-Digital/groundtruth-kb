---
name: gtkb-verify
description: Author a Loyal Opposition post-implementation VERIFIED or NO-GO verdict file that satisfies the Mandatory Specification-Derived Verification Gate. Use when a post-implementation report enters the Loyal Opposition actionable queue, when asked to verify a post-implementation report, when authoring a VERIFIED/NO-GO verdict, or when reviewing an implementation report for spec-derived testing.
allowed-tools: Read, Bash, Grep, Glob, Write
---

# /verify

This skill helps Loyal Opposition author post-implementation verdict files
(`VERIFIED` or `NO-GO`) that satisfy the **Mandatory Specification-Derived
Verification Gate** in `.claude/rules/file-bridge-protocol.md`. It scaffolds
the structural conventions of the verdict file: header metadata, prior-
deliberation citations, applicability and clause preflight output, the
spec-to-test mapping table, positive confirmations, finding structure for
`NO-GO`, the executed-commands block, and the owner-action-required footer.

The skill is **documentation and procedural orchestration only**. It is the
first slice of WI-3261 (Verification mechanics: `/verify` verdict-author skill
+ spec-to-test mapping helper). The companion spec-to-test mapping computation
helper — which would read `config/governance/spec-applicability.toml` and
`config/governance/adr-dcl-clauses.toml` to suggest candidate test commands per
cited specification — is deferred to Slice 2. This slice documents the
structural conventions only.

## Non-bypass guarantees

This skill does NOT replace any part of Loyal Opposition's judgment or the
bridge protocol. Specifically:

- It does **NOT** itself execute the applicability preflight, the clause
  preflight, or the spec-derived tests. The reviewer runs those commands and
  pastes the real output into the verdict file.
- It does **NOT** write or mutate canonical dispatcher/TAFE bridge state.
  Aggregate queue artifacts are not live queue mirrors after the verdict file
  is written.
- It does **NOT** short-circuit Loyal Opposition's verdict. `VERIFIED` versus
  `NO-GO` is the reviewer's evidence-based decision; this skill only documents
  the file shape that decision is recorded in.
- It does **NOT** allow file-only `VERIFIED` closure. A positive `VERIFIED`
  verdict must be recorded through the helper's `--finalize-verified` path so
  the verified work, implementation report, and verdict artifact are committed
  by the same local git transaction.

After the 2026-06-15 TAFE/dispatcher cutover, verdict files flow through the
normal dispatcher-backed bridge write channel like any other bridge file.

## When to invoke

Use this skill when:

- The latest status on a bridge thread is `NEW` and the latest version is a
  **post-implementation report** (the `GO` already happened in an earlier
  version of the same thread).
- The user explicitly asks `/verify <slug>`.
- A bridge scan surfaces a thread as actionable for Loyal Opposition
  verification (a post-implementation report awaiting `VERIFIED`/`NO-GO`).

Do NOT use this skill for:

- Reviewing a fresh `NEW`/`REVISED` implementation proposal (that is
  `gtkb-proposal-review`, which produces a `GO`/`NO-GO` verdict on a proposal).
- Authoring a Prime Builder implementation proposal or implementation report
  (that is `gtkb-bridge` / `gtkb-bridge-propose`).
- Writing aggregate queue entries directly; aggregate artifacts are not current
  bridge authority.

## Mandatory pre-write steps

Before writing the verdict file, the reviewer must:

1. Read the full thread version chain — every prior `bridge/<slug>-NNN.md`
   for the thread — so the verdict is grounded in the complete exchange.
2. Confirm the latest status is `NEW` on a post-`GO` thread (i.e., the latest
   version is a post-implementation report, not a fresh proposal).
3. Run `python scripts/bridge_applicability_preflight.py --bridge-id <slug>`
   and capture the full output.
4. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id <slug>` (no
   `--report-only`) and capture the full output. Treat exit `5` as a blocking
   gap unless an explicit owner-waiver line is present per blocking clause.
5. Optionally run
   `python scripts/adr_dcl_applicability_discovery.py --bridge-id <slug>` and
   use the `Candidate Applicable ADR/DCLs` output as advisory review context.
   It always exits 0 and does not replace the blocking clause preflight.
6. Run a deliberation search per `.claude/rules/deliberation-protocol.md`
   (`gt deliberations search <topic>`) for prior reviews on the same
   spec/WI/component.
7. Before writing the verdict, run
   `python .claude/skills/verify/helpers/write_verdict.py --slug <slug> --body-file <draft-body-file>`
   to seed the draft's `## Prior Deliberations` section. Review and prune the
   helper-suggested candidates; if you opt out, leave an explicit
   `_No prior deliberations: <reason>._` line in the verdict.
8. Identify the linked specifications carried forward from the `GO`'d proposal
   — the verdict must mirror the proposal's `Specification Links`.
9. Build the spec-to-test mapping table. In Slice 1 this is done manually;
   Slice 2 will provide a helper that computes candidate test commands.
10. Execute the spec-derived tests and capture the exact commands run and the
   observed results.
11. For a positive `VERIFIED` verdict, run the reviewed final body through the
    atomic finalization helper instead of writing the verdict file directly:

    ```text
    python .claude/skills/verify/helpers/write_verdict.py --slug <slug> --body-file <reviewed-verdict-body> --finalize-verified --no-prepopulate --commit-message "<type(scope): message>" --include <verified-path> [--include <verified-path> ...]
    ```

    Repeat `--include` for every verified implementation/report path that must
    be in the final commit. The helper automatically includes the new
    `VERIFIED` verdict file. If the helper fails, do not leave or manually
    recreate a terminal `VERIFIED` bridge file.

## Verdict file template

Author the verdict file at `bridge/<slug>-<next>.md` where `<next>` is the next
zero-padded version number for the thread. Structure:

- **Line 1:** the verdict word — `VERIFIED` or `NO-GO` — alone on its own line.
- **Header block** (immediately after a blank line):
  - `bridge_kind: verification_verdict`
  - `Document: <slug>`
  - `Version: <NNN>`
  - `Author: Loyal Opposition (<harness>, harness <id>)`
  - `Date: <YYYY-MM-DD> UTC`
  - `Reviewer: Loyal Opposition`
  - `Responds to: bridge/<slug>-<post-impl-report-version>.md`
  - `Recommended commit type: <feat|fix|...>` — include this line only for a
    `VERIFIED` verdict (it validates the implementation report's recommended
    Conventional Commits type).
- `## Applicability Preflight` — the verbatim output from
  `scripts/bridge_applicability_preflight.py`.
- `## Clause Applicability` — the verbatim output from
  `scripts/adr_dcl_clause_preflight.py`, including a `## Blocking Gaps`
  subsection when the clause preflight exited 5.
- `## Prior Deliberations` — `DELIB-*` citations from the deliberation search,
  or an explicit `_No prior deliberations: <reason>._` line for a novel topic.
- `## Specifications Carried Forward` — the list of linked specifications,
  mirroring the `GO`'d proposal's `Specification Links` section.
- `## Spec-to-Test Mapping` — a table with exactly these four columns:
  `| Specification | Test or Verification Command | Executed | Result |`.
  Every carried-forward specification needs at least one row.
- `## Positive Confirmations` — a bullet list of what was inspected and passed.
- `## Findings` — for a `NO-GO` verdict only; each finding structured per
  `.claude/rules/report-depth.md` and
  `.claude/rules/report-depth-prime-builder-context.md` (observation,
  deficiency rationale, proposed solution, option rationale, Prime Builder
  implementation context).
- `## Required Revisions` — for a `NO-GO` verdict only; the finding-by-finding
  required changes Prime Builder must address before resubmitting.
- `## Commands Executed` — the exact shell commands run during the review with
  observed output excerpts.
- `## Commit Finalization Evidence` — for a `VERIFIED` verdict only; the
  helper appends this section when absent, recording the intended commit
  subject and same-transaction path set. The final commit SHA is printed by the
  helper after success and is intentionally not embedded in the committed
  verdict file.
- `## Owner Action Required` — optional; any owner decision the verdict
  surfaces (waiver request, blocking-gap disposition, scope clarification).
- Copyright footer.

## Gate enforcement

The verdict must honor these gates before `VERIFIED` is recorded:

- **Spec-derived testing.** `VERIFIED` requires every linked specification to
  have at least one row in the `Spec-to-Test Mapping` table whose `Executed`
  column is `yes`. A linked specification with no executed test coverage means
  `NO-GO` unless the owner explicitly approves a documented waiver for that
  specific specification and risk
  (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`).
- **Untested specifications.** An untested linked specification requires an
  explicit owner-waiver line in the verdict; otherwise issue `NO-GO`.
- **Clause preflight.** A clause-preflight exit `5` with no owner-waiver line
  for the offending blocking clause is a `NO-GO`.
- **Missing cross-cutting specs.** If the applicability preflight reports a
  non-empty `missing_required_specs` list, issue `NO-GO` until the proposal or
  implementation report is revised to cite and satisfy those specifications.
- **Commit finalization.** `VERIFIED` requires the atomic helper transaction.
  The staging area must be clean before finalization, and the helper must commit
  exactly the declared verified path set plus the new verdict artifact. Any
  staging or commit failure means the review fails closed without terminal
  bridge state.

## Cross-harness implementation notes

The skill body is identical between Claude Code and Codex. The canonical file
is `.claude/skills/verify/SKILL.md`; the Codex adapter is
`.codex/skills/verify/SKILL.md` and carries the generated adapter marker. Do
NOT edit the adapter directly — edit the canonical file and regenerate with
`python scripts/generate_codex_skill_adapters.py --update-registry` per
`ADR-CODEX-HOOK-PARITY-FALLBACK-001`. The adapter's stored SHA in
`.codex/skills/MANIFEST.json` and the harness-capability registry is the
normalized-body SHA computed by the generator.

## Companion skills

- `gtkb-bridge` — operate the full bridge protocol across its lifecycle.
- `gtkb-proposal-review` — review a fresh `NEW`/`REVISED` implementation
  proposal (the pre-implementation counterpart to this post-implementation
  skill).
- `gtkb-send-review` — create an implementation proposal and add it to the
  bridge INDEX for Loyal Opposition review.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
