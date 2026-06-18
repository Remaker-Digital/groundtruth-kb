NEW
author_identity: prime-builder/Codex
author_harness_id: A
author_session_context_id: keep-working-20260618T0915Z
author_model: GPT-5
author_model_version: 2026-06-18
author_model_configuration: Codex desktop automation; PowerShell; approval_policy_never

# Root-Boundary Command Token False-Positive Fix

bridge_kind: prime_proposal
Document: gtkb-root-boundary-command-token-false-positive
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4602

target_paths: ["groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py", "config/governance/gate-fp-corpus.toml", "platform_tests/scripts/test_gate_fp_corpus.py", "platform_tests/scripts/test_fab14_directive_hook_coverage.py", "bridge/gtkb-root-boundary-command-token-false-positive-*.md"]
Recommended commit type: fix:

implementation_scope: root_boundary_command_token_false_positive
requires_review: true
requires_verification: true

## Claim

`WI-4602` records a root-boundary false positive where a proposal-filing command
was blocked even though its live artifact paths were in-root bridge paths.

Live parser inspection shows the likely class of defect: the shared
`groundtruth_kb.enforcement` command scanner treats drive-like substrings in
free-form command text as absolute Windows paths even when the substring is not
a standalone filesystem token. The same parser already owns the cross-gate
false-positive corpus and is called by the Claude directive-enforcement
adapter for PowerShell command text.

This proposal asks for a narrow parser and regression-corpus fix so escaped or
quoted in-root bridge/proposal text continues to pass, while genuine
out-of-root absolute paths remain blocked.

## Evidence

- Live MemBase state shows `WI-4602` open under
  `PROJECT-GTKB-MAY29-HYGIENE`, priority `P3`, with source spec
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.
- Exact bridge search for `WI-4602`, the title, and the phrase
  `escaped bridge path` found no existing bridge thread for this work item.
- `.claude/hooks/directive-enforcement-claude-adapter.py` delegates
  PowerShell/Bash command checks to `check_bash_command(command,
  project_root)`, then emits `root-boundary-command` denials on failure.
- `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py` defines
  `_DRIVE_ABSOLUTE` and `PATH_DELIMITER_RE`, but the drive-letter branch lacks
  the same token-boundary guard applied to rooted slash paths. A drive-shaped
  substring can therefore be matched inside arbitrary prose or regex text.
- `config/governance/gate-fp-corpus.toml` and
  `platform_tests/scripts/test_gate_fp_corpus.py` already provide the approved
  deterministic false-positive regression surface for this parser family.
- During this automation run, an otherwise read-only inline Python command that
  parsed bridge `Document:` lines was blocked because text containing
  colon-backslash regex syntax was classified as a drive path outside
  `E:\GT-KB`. That reproduces the WI-4602 failure shape without requiring any
  out-of-root artifact.

## Proposed Implementation After GO

1. Create a fresh implementation-start packet for this bridge thread.
2. Add focused pass cases to `config/governance/gate-fp-corpus.toml` for:
   - escaped or quoted in-root bridge/proposal text;
   - regex/prose snippets containing a drive-shaped substring that is not a
     standalone filesystem token.
3. Keep or extend block cases proving real out-of-root drive-letter, UNC, and
   MSYS paths remain denied.
4. Refine `groundtruth_kb.enforcement.PATH_DELIMITER_RE` or
   `_classify_path_token()` so drive-letter absolute paths require an actual
   token boundary and are not matched inside words, prose, or regex syntax.
5. Add a hook-level regression in
   `platform_tests/scripts/test_fab14_directive_hook_coverage.py` only if the
   parser-level corpus does not exercise the Claude adapter boundary strongly
   enough.
6. Run the focused parser/hook tests, ruff checks for touched files, and file a
   post-implementation report with observed results.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected source, test, and
  configuration mutations must wait for Loyal Opposition `GO` and a valid
  implementation-start packet.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active May29 Hygiene
  project authorization permits autonomous proposals for unimplemented May29
  work items without bypassing bridge review.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal, eventual report, and
  verification use the versioned bridge file chain.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes
  project authorization, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites the governing specification surfaces and concrete target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report
  must map the linked requirements to executed tests and observed results.
- `GOV-STANDING-BACKLOG-001` - `WI-4602` is the governed backlog authority for
  this defect.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - root-boundary enforcement must
  preserve the `E:\GT-KB` boundary without false-blocking in-root work.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - the gate classifier remains deterministic
  and regression-tested, not LLM-interpreted.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy enforcement must be precise enough to
  avoid blocking authorized in-root work while continuing to block genuine
  violations.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the shared parser and hook coverage
  keep root-boundary behavior aligned across harness surfaces.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the observed defect, proposal,
  regression corpus, and report remain linked as durable lifecycle artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the regression corpus captures the
  behavior as executable artifact evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the work item remains open until the
  post-implementation report is VERIFIED.

## Requirement Sufficiency

Existing requirements are sufficient. The root-boundary directive, deterministic
classifier specs, cross-harness enforcement decision, and FAB-14 false-positive
corpus already define the needed behavior. No new GOV/SPEC/PB/ADR/DCL artifact
is required before this source/test/config fix.

## Owner Decisions / Input

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` authorizes autonomous
  proposal work for all unimplemented work items linked to
  `PROJECT-GTKB-MAY29-HYGIENE` through
  `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`.
- No new owner decision is required. This proposal does not request a waiver,
  production deployment, credential action, destructive cleanup, or formal
  artifact mutation.

## Prior Deliberations

- `bridge/gtkb-fab-14-gate-fp-feedback-loop-013.md` - REVISED FAB-14 report
  showing the current gate false-positive corpus, parser target, and
  cross-harness directive hook coverage as the accepted maintenance surface for
  gate parser precision.
- `bridge/gtkb-implementation-start-authorization-gate-005.md` - REVISED
  implementation-start report establishing precedent for escaped bridge patch
  payload regression coverage while retaining protected-path denials.
- `WI-4602` live work-item record - owner-directed May29 Hygiene capture of
  the escaped bridge path false-positive.
- Focused bridge search for `WI-4602` and `escaped bridge path` returned no
  prior bridge thread for this exact May29 Hygiene work item.

## Specification-Derived Verification Plan

This is the spec-to-test mapping for the proposed change. The
post-implementation report will include executed commands and observed results.

| Requirement / specification | Verification evidence |
|---|---|
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation-start packet created before source/test/config edits. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | New pass cases show in-root bridge/proposal text is not false-blocked; block cases still deny genuine out-of-root paths. |
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` and `SPEC-AUQ-POLICY-ENGINE-001` | `python -m pytest platform_tests/scripts/test_gate_fp_corpus.py -q --tb=short` passes with the new false-positive and true-negative cases. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | If hook coverage is changed, `python -m pytest platform_tests/scripts/test_fab14_directive_hook_coverage.py -q --tb=short` passes. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability preflight passes for this proposal and report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps each linked requirement to executed parser/hook tests and ruff output. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `show_thread_bridge.py gtkb-root-boundary-command-token-false-positive` shows no drift after report filing. |

## Acceptance Criteria

- In-root bridge/proposal command text that includes escaped or quoted path
  snippets is allowed by `check_bash_command`.
- Regex/prose snippets containing non-token drive-shaped substrings are not
  classified as filesystem paths.
- Genuine out-of-root Windows drive-letter, UNC, and MSYS paths remain blocked.
- Focused parser tests pass, with hook-level tests included if touched.
- Ruff check and format pass for all touched source/test files.
- No production deployment, credential action, destructive cleanup, or formal
  artifact mutation is included.

## Risk And Rollback

Risk is moderate because this code protects the project root boundary. The
implementation must bias toward small token-boundary refinement plus regression
coverage, not broad parser rewrites. Rollback would revert the parser and
corpus/test changes, but doing so would restore the WI-4602 false-positive and
should go through a follow-up bridge review.
