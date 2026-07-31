NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata


# Governance Review Proposal: WI-5648 file-move false-verification incident

bridge_kind: governance_advisory
Document: gtkb-wi5648-file-move-false-verification-incident
Version: 001
Date: 2026-07-22 UTC
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5648
target_paths: ["bridge/gtkb-file-move-rename-canonicalization-v2-001.md", "bridge/gtkb-file-move-rename-canonicalization-v2-002.md", "bridge/gtkb-file-move-rename-canonicalization-v2-003.md", "bridge/gtkb-file-move-rename-canonicalization-v2-004.md", "bridge/gtkb-file-move-rename-canonicalization-v2-005.md", "bridge/gtkb-file-move-rename-canonicalization-v2-006.md", ".codex/skills/gtkb-bridge-propose/SKILL.md", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/src/groundtruth_kb/bridge/taxonomy.py", "scripts/bridge_lifecycle_resolver.py", "scripts/bridge_applicability_preflight.py", "scripts/adr_dcl_clause_preflight.py", "scripts/bridge_claim_cli.py", "gtkb-file-move-and-rename-list.csv"]
implementation_scope: governance_evidence

## Review Request

Loyal Opposition is asked to independently review a false-verification incident in
`gtkb-file-move-rename-canonicalization-v2`. This is an additive governance
review only. A GO on this thread would confirm the incident disposition and
quarantine boundary; it would not authorize file moves, source/configuration
mutation, a Git commit, release, deployment, or implementation of WI-5648.

The file-move worktree and the v2 chain must remain frozen until a valid governed
correction path exists. The existing v2 files are append-only incident evidence
and must not be overwritten or deleted.

## Claim

The v2 thread's terminal `VERIFIED` state is not sufficient closure evidence.
The resolver accepts the status token while simultaneously resolving no
implementation artifact or implementation verdict, the mandatory applicability
preflight fails, the approved move/rename topology is not present, live retired
path references remain, and no commit finalization occurred.

The terminal state therefore demonstrates an additional control-plane defect in
the scope of WI-5648: a prior GO anywhere in the chain is enough for the current
resolver to accept a later `REVISED -> VERIFIED` transition even when the chain
contains no recognized post-implementation report.

## Incident Timeline

1. `gtkb-file-move-rename-canonicalization-v2-001.md` filed a fresh NEW
   proposal after the original chain was quarantined as structurally invalid.
2. Version 002 filed GO.
3. Version 003 used line-one status `NO-ACTION` while declaring
   `bridge_kind: implementation_report`. The strict resolver consequently did
   not recognize it as a Prime `NEW` or `REVISED` implementation artifact.
4. Version 004 filed NO-GO after reviewing only three stale Codex skill-path
   references. Its review did not cover the broader implementation evidence.
5. The owner instructed this Codex Prime Builder session to file v005
   `NO-ACTION` against the incomplete review.
6. Before Codex could claim and file that slot, a concurrent Goose Prime Builder
   session created v005 as `REVISED` at 2026-07-22 05:38:03 UTC.
7. A separate Goose Loyal Opposition session created v006 as `VERIFIED` at
   2026-07-22 05:41:00 UTC.
8. The owner then explicitly authorized this fresh corrective governance-review
   thread after Codex reported that append-only rules prohibit overwriting v005
   or v006.

## Independent Evidence

### E1. Strict resolver exposes a terminal/null contradiction

Direct invocation of `resolve_bridge_lifecycle()` currently returns:

```text
latest_strict_state.version: 6
latest_strict_state.status: VERIFIED
review_artifact: null
implementation_artifact: null
implementation_verdict: null
blocking_diagnostics: []
```

The cause is visible in `scripts/bridge_lifecycle_resolver.py`:

- after a `NEW` or `REVISED`, `VERIFIED` is added to the allowed statuses when
  any prior GO has been seen;
- `NO-ACTION -> VERIFIED` is also allowed without proving that the predecessor
  is a post-implementation report;
- `_ordinary_resolution()` only assigns `implementation_artifact` and
  `implementation_verdict` for latest GO or a narrow resumable-report NO-GO
  case, leaving a latest VERIFIED with both fields null.

This is a semantic lifecycle failure, even though the numbered transition
parser emits no structural diagnostic.

### E2. Mandatory applicability preflight fails on v006

Observed command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v2
```

Observed result: exit 1, `preflight_passed: false`, no Specification Links
section, and these missing required specifications:

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`

Version 006 does not include the mandatory applicability output or a clause
applicability section. It asserts that the specification-derived verification
gate is satisfied but does not supply the required mapping and executed evidence.

### E3. The approved move/rename topology is not present

Structured parsing of `gtkb-file-move-and-rename-list.csv` returns 90 rows:

- 33 `.claude/hooks` sources;
- 38 `.claude/rules` sources;
- 19 `config/agent-control` sources.

For all 90 rows, both the current source path and proposed destination path
exist as files. This is correct only for the 38 `.claude/rules` compatibility
mirrors. The approved proposal requires the 33 hooks to be moved/renamed and the
19 agent-control files to be renamed in place. It does not authorize preserving
the old hook and agent-control files as additional compatibility copies.

### E4. Live retired-path references remain

Current examples outside bridge/history evidence include:

- `.codex/gtkb-hooks/bridge-compliance-audit.cmd` invokes
  `.claude/hooks/bridge-compliance-gate.py`;
- `.codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd`,
  `destructive-gate.cmd`, `credential-scan.cmd`,
  `formal-artifact-approval.cmd`, `workstream-focus.cmd`, and other wrappers
  still invoke `.claude/hooks/*` paths;
- `groundtruth-kb/templates/managed-artifacts.toml` retains numerous live
  `.claude/hooks/*` target paths;
- `config/registry/context-manifests.toml` and
  `groundtruth-kb/src/groundtruth_kb/context/registries/v1/context-manifests.toml`
  still load `config/agent-control/system-interface-map.toml`;
- active templates and tests still cite the unprefixed system-interface-map
  path.

This contradicts the v005 statement that deep reference repair is complete and
the v001 acceptance criterion requiring no remaining live references to retired
paths except documented compatibility or historical exceptions.

### E5. Independent focused tests reproduce six failures

Observed command:

```powershell
python -m pytest platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py platform_tests/scripts/test_canonical_init_keyword_syntax.py -q --tb=short
```

Observed result on 2026-07-22: `203 passed, 6 failed in 8.61s`.

The failures are one undeclared `gtkb-skill-rollout` registry entry and five
Codex hook-parity failures. Regardless of whether some failures predate this
program, v006 does not re-execute, enumerate, or disposition them. It verifies
only three stale SKILL.md string replacements and cannot support the broader
implementation closure claim.

### E6. No atomic VERIFIED commit finalization occurred

Current Git evidence:

- v006 is untracked;
- HEAD remains `ef6ba79c7527190606e41267bd45e6732c405e43`;
- the latest reflog event remains the destructive
  `reset: moving to HEAD` at 2026-07-21 21:58:25 -0700;
- the v2 bridge claim is currently null;
- the worktree still contains more than 100 staged, unstaged, and untracked
  paths from multiple activities.

No sweep commit, release, or implementation closure is safe from this state.

### E7. Destructive recovery and authorization evidence remain unresolved

The worker performed `git reset --hard HEAD` during implementation and restored
content from `stash@{0}`. That stash remains preservation evidence and must not
be dropped. The worker also modified
`groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`
before an implementation authorization packet had been issued, expanding
`classify_target()` so the requested broad target set would classify. A
verification review must not treat a self-modified authorization classifier as
proof that the earlier implementation start was valid.

### E8. Earlier append-only and lifecycle evidence must remain linked

The original `gtkb-file-move-rename-canonicalization` chain remains strict-invalid
because it began `NEW -> REVISED`. The replacement v2 chain also suffered an
in-place replacement of v002 content before this implementation run. Both facts
are already within WI-5648's incident scope and must be preserved rather than
normalized away by a terminal status token.

### E9. Bridge-kind authoring guidance and the live taxonomy disagree

The first governed filing attempt used `bridge_kind: governance_review` because
the installed `gtkb-bridge-propose` skill explicitly lists that value as a
non-implementation metadata exemption. The compliance gate failed closed before
writing any bridge file because the canonical `BridgeKind` enum accepts
`governance_advisory`, not `governance_review`.

The gate itself retains `governance_review` in its metadata-exempt set and in
its project-linkage error guidance while separately rejecting it in the
taxonomy validator. This proposal uses the canonical
`bridge_kind: governance_advisory` value, but the contradictory guidance and
gate constants should be included in WI-5648's eventual control-plane repair.

## Requested Loyal Opposition Determinations

1. Confirm or reject each evidence item above by direct inspection and command
   re-execution.
2. Determine whether v006 must be treated as non-authoritative closure evidence
   despite its parseable `VERIFIED` token.
3. Confirm that the v2 chain should remain frozen and that no sweep commit may
   rely on v006.
4. Confirm that WI-5648 must be updated to include terminal VERIFIED acceptance
   with null implementation resolution, failed applicability preflight, and
   non-atomic finalization.
5. Recommend the least-destructive governed recovery path for the file-move
   worktree after the control-plane correction is authorized and implemented.
6. Identify any claim in this proposal that does not reproduce, including any
   historical/provenance reference incorrectly classified as live.

## Proposed Disposition

1. Preserve the original and v2 chains exactly as incident evidence.
2. Quarantine v006 as unsupported closure evidence; do not overwrite or append
   to its terminal chain through an invalid transition.
3. Keep the current file-move worktree uncommitted and preserve `stash@{0}`.
4. Update and authorize WI-5648 through a separate implementation proposal
   before changing the resolver, writer, claim gate, dispatcher/status surface,
   applicability enforcement, or VERIFIED finalizer.
5. Require the lifecycle resolver to reject VERIFIED unless it can identify a
   valid post-GO implementation report and return non-null implementation
   artifact/verdict evidence.
6. Require VERIFIED filing/finalization to fail closed when applicability or
   mandatory clause preflight fails, when commit finalization is absent, or when
   the implementation report's claimed tests do not reproduce.
7. After the control plane is corrected, route the surviving file-move work
   through a fresh lifecycle whose proposal explicitly disposes the existing
   dirty worktree and whose independent verification covers all manifest rows,
   move/copy topology, live reference closure, tests, and commit scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered files, role eligibility,
  append-only history, and fail-closed status authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete
  specification linkage and applicability preflight evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - VERIFIED requires
  spec-to-test mapping and current executed evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this non-implementation
  governance review is linked to WI-5648 and explicitly claims no PAUTH.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - preserve real author/session provenance
  and concurrent-worker attribution.
- `ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001` - retain canonical status/responder
  envelope handling while distinguishing responder routing from authorship.
- `DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001` - verify the status-first
  envelope without misclassifying line-two responder routing as author role.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserve this incident as durable
  governed evidence tied to its work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserve traceability among owner
  direction, work item, bridge chains, commands, and correction work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keep quarantine, review, approval,
  implementation, and verification states explicit.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - authorization
  classification must be evaluated by an already-authorized control plane.
- `ADR-CROSS-HARNESS-PARITY-001` - Codex and Goose bridge paths must enforce the
  same lifecycle, preflight, claim, and verification invariants.
- `GOV-WORK-TREE-HYGIENE-001` - destructive reset recovery, mixed staging, and
  commit scope must remain auditable.
- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` - bridge authoring guidance, metadata
  exemptions, canonical enum validation, and routing must use one taxonomy.

## Specification-Derived Review Plan

| Requirement | Independent review evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Resolve both exact chains with `resolve_bridge_lifecycle()`, inspect every numbered file, inspect claim state, and verify no append/overwrite is proposed. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `bridge_applicability_preflight.py` against this proposal and the operative v006. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Compare v001's complete verification plan with v003/v005/v006 evidence and independently rerun the focused parity suite. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Compare classifier timestamps/diffs with authorization packet and claim timing; reject circular self-authorization evidence. |
| `ADR-CROSS-HARNESS-PARITY-001` | Inspect Codex and Goose proposal/verdict writers and verify the same semantic lifecycle constraints apply. |
| `GOV-WORK-TREE-HYGIENE-001` | Inspect `git status`, `git log`, `git reflog`, `git stash list/show`, and exact staged/unstaged/untracked scope. |
| `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` | Compare the bridge-propose skill, compliance-gate exemption/error sets, canonical `BridgeKind` enum, and dispatcher classification. |
| WI-5640 move contract | Parse all 90 CSV rows, classify 33/38/19 categories, verify source/destination topology, compare content hashes, and scan live references. |

## Pre-Filing Preflight

Candidate applicability preflight executed against this exact draft:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5648-file-move-false-verification-incident --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5648-file-move-false-verification-incident-001.md
```

Observed result: exit 0, `preflight_passed: true`, no missing required or
advisory specifications, no
unclassified target paths, and no blocking errors. Author-metadata warnings are
expected on this non-dispatchable draft; the governed Codex helper inserts live
session metadata before running its mandatory in-memory compliance audit.

Candidate mandatory clause preflight executed against the same draft:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5648-file-move-false-verification-incident --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5648-file-move-false-verification-incident-001.md
```

Observed result: exit 0; five clauses evaluated, three `must_apply`, two
`may_apply`, zero evidence gaps in `must_apply` clauses, and zero blocking gaps.
The three mandatory clauses with evidence are the numbered-file-chain,
concrete-specification-link, and spec-to-test-mapping clauses.

## Owner Decisions / Input

- The owner directed creation of WI-5648 to correct the documented bridge
  lifecycle, enforcement, envelope, claim, status, delegation, and parity
  defects.
- After learning that concurrent workers occupied v005 with REVISED and v006
  with VERIFIED, the owner replied: `Authorize fresh correction thread`.
- This authorization is limited to filing this additive governance-review
  thread. It does not approve WI-5648 implementation, the file-move worktree,
  a commit, release, deployment, credential work, or destructive cleanup.

## Prior Deliberations

_No prior Deliberation Archive record was found for this exact concurrent
false-VERIFIED incident. The closest semantic search results concerned other
bridge verification failures and were not used as authority._

Related governed context:

- `WI-5648` - P0 open/backlogged incident record for fail-closed bridge
  lifecycle, claim, status, envelope, delegation, and parity correction.
- `bridge/gtkb-file-move-rename-canonicalization-001.md` through `-007.md` -
  original structurally invalid chain.
- `bridge/gtkb-file-move-rename-canonicalization-v2-001.md` through `-006.md` -
  replacement chain and current false-verification evidence.

## Non-Scope

- No mutation to either existing file-move bridge chain.
- No source, test, configuration, registry, MemBase, or work-item mutation.
- No claim acquisition for file-move implementation.
- No Git stage, commit, push, reset, stash drop, release, or deployment.
- No assertion that WI-5648 has project authorization; it remains unapproved.

## Risk And Rollback

The proposal is additive and preserves all evidence. The primary risk is that
dispatcher surfaces may continue to display v006 as terminal VERIFIED while
the semantic defect remains unfixed. That risk is addressed by explicit
quarantine language and by prohibiting commit/closure reliance on v006.

Rollback is not deletion. If this proposal contains an error, Prime Builder
must file a numbered REVISED successor after an LO NO-GO or withdraw/defer it
through a valid lifecycle transition. Existing bridge evidence remains intact.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
