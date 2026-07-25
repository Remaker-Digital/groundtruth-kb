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


# Implementation Proposal: Deterministic full-root file-reference migration with retained safety copies

bridge_kind: prime_proposal
Document: gtkb-file-move-rename-canonicalization-v3
Version: 001
Date: 2026-07-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

target_paths: ["gtkb-file-move-and-rename-list.csv", "scripts/gtkb_file_reference_migration.py", "config/file-reference-migration/wi5640.toml", "platform_tests/scripts/test_gtkb_file_reference_migration.py", ".claude/hooks", ".claude/rules", ".claude/settings.json", ".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-send-review/SKILL.md", ".codex/config.toml", ".codex/hooks.json", ".codex/gtkb-hooks", ".codex/skills/gtkb-bridge/SKILL.md", ".codex/skills/gtkb-send-review/SKILL.md", ".agent", ".cursor", ".goose", "config/hooks", "config/agent-control", "config/registry", "groundtruth-kb/src", "groundtruth-kb/tests", "groundtruth-kb/docs", "groundtruth-kb/templates", "platform_tests", "tests", "scripts", "dashboard", "docs", ".github", "AGENTS.md", "CLAUDE.md", "README.md", "pyproject.toml", "groundtruth.toml"]
implementation_scope: source | test | configuration | documentation | governance_evidence

## Claim

The surviving WI-5640 work must be restarted through a fresh lifecycle and
completed by one deterministic, CSV-driven migration program. The program will
inventory every in-root filesystem subtree, classify every path, create or
reconcile the 90 canonical destinations, update every live load-bearing
reference within the approved mutation boundary, regenerate derived artifacts,
and independently verify zero unexplained live residuals.

The 90 obsolete source files will remain temporarily as safety copies. Their
presence is not a defect, but no live consumer may continue resolving an
obsolete hook or agent-control path. The 38 `.claude/rules` sources remain a
governed native compatibility surface and must be deterministic mirrors of the
new canonical control files. Removal of any obsolete source is outside this
proposal and requires a later owner-authorized bridge lifecycle.

This proposal supersedes the implementation authority of both prior file-move
chains. It preserves those chains as evidence and does not rely on either
terminal token, implementation report, claim, packet, or verification result.

## Requirement Sufficiency

Existing requirements and owner direction are sufficient for this bounded
implementation proposal. No new or revised requirements are required. The
operative owner decisions are the deterministic all-root migration direction
in the current session and
`DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`.

## Current-State Evidence

- The CSV parses to exactly 90 rows: 33 hooks, 38 rules, and 19 agent-control
  mappings.
- All 90 source files and all 90 destinations currently exist.
- Hash comparison shows 11/33 hook pairs equal and 22 different; 38/38 rule
  pairs equal; 16/19 agent-control pairs equal and 3 different.
- The 25 divergent pairs cannot be resolved by blind recopying. The migration
  plan must prove whether each destination equals a deterministic transform of
  its source or require an explicit per-row authority decision before apply.
- Live obsolete references remain in Codex hook wrappers, managed-artifact
  templates, SoT/context registries, tests, and generated/projected surfaces.
- The focused parity suite currently reports 203 passed and 6 failed out of 209.
- A no-ignore inventory sees more than one million filesystem entries because
  runtime/test trees dominate. A naive nested mapping-by-file scan stalls and
  cannot be completion evidence.
- `groundtruth.db` is hundreds of megabytes and must be queried structurally in
  read-only mode, not decoded or rewritten as one binary file.
- The worktree contains unrelated staged, unstaged, and untracked work. This
  implementation must preserve the live Git index and must not use broad
  staging, reset, checkout, clean, stash apply/drop, or history rewrite.

## In-Root Placement Evidence

All implementation artifacts and mutable target paths are within `E:\GT-KB`.
The scanner's inventory root is exactly `E:\GT-KB`. Paths outside the root,
reparse-point targets, and the lifecycle-independent Agent Red repository are
never followed or mutated. `applications/` is inventoried and classified; any
load-bearing residual there fails the plan and requires a separately governed
application-boundary disposition before mutation.

## Proposed Scope

### 1. One governed migration engine

Create `scripts/gtkb_file_reference_migration.py` using Python standard-library
APIs and structured parsers where available. It must expose five deterministic
modes:

```text
preflight  Validate manifest, policy, root boundary, source/destination state,
           Git tracking, encodings, and complete path classification.
plan       Produce an immutable, sorted operation plan with preimage hashes,
           replacements, generator actions, exclusions, and inventory hash.
apply      Validate plan/preimages, then perform only plan-listed atomic writes.
verify     Re-enumerate independently and fail on residual or unclassified data.
rollback   Restore only plan-recorded preimages without broad Git/stash actions.
```

`apply` must refuse to run unless supplied the exact plan hash produced after
GO, claim acquisition, and implementation-start authorization. A changed
manifest, policy, source preimage, destination preimage, inventory boundary, or
Git index hash invalidates the plan and requires a new `plan` run before apply.

### 2. Declarative policy and exclusion ledger

Create `config/file-reference-migration/wi5640.toml` as the canonical policy for
this migration. It must declare:

- repository root and CSV path;
- every mapping category and compatibility mode;
- mutable path roots and exact root-file allowlist;
- canonical authority and projection/generator rules;
- encoding/newline preservation policy;
- immutable audit exclusions;
- runtime/cache/tooling exclusions;
- structured read-only data sources such as SQLite;
- application/reparse/external boundary behavior;
- residual classification and exception schema;
- repeated verification and idempotency requirements.

Every discovered path must receive exactly one recorded classification. At
minimum the inventory distinguishes mutable text, generated text, retained
obsolete source, canonical destination, immutable audit, runtime
non-authoritative, binary, structured SQLite, reparse point, application
boundary, unreadable, and unclassified. Unreadable, multiply classified, or
unclassified paths fail preflight/verify. Exclusions are never silent: reports
must include rule ID, path count, total bytes, sorted inventory hash, and
representative paths.

`bridge/**` is immutable canonical audit history and is inventoried but excluded
from correction and residual-failure counts. `.git/**`, `.gtkb-state/**`,
`.pytest-tmp/**`, virtual environments, package caches, build outputs, bytecode,
logs, and other runtime/tooling trees may be excluded only through explicit
policy rules and inventory evidence. The CSV itself is input authority and is
not rewritten by its own mappings.

### 3. Efficient full-root enumeration

Walk the root once per phase with sorted `os.scandir()` traversal, without
following reparse points. Stream each candidate file once. Compile a
multi-pattern matcher or equivalent deterministic index so complexity is based
on total text size plus matches, not `files x mappings` repeated reads.

Binary detection, encoding selection, and text decoding must be deterministic.
Support at minimum UTF-8, UTF-8 with BOM, UTF-16 LE/BE with BOM, and explicitly
declared legacy text encodings. Preserve the original BOM, encoding, newline
convention, file attributes/permissions, and every unrelated byte. A file that
cannot be decoded under policy is classified, not silently skipped.

Query configured SQLite sources through read-only SQLite connections. Report
table, column, row identity, mapping, and variant for any text-field residual.
No raw SQLite mutation is authorized. A live database residual requiring change
stops apply and routes to a separately governed API-level correction.

### 4. Mapping variants and ambiguity policy

For each old/new mapping, generate deterministic variants including:

- canonical repository-relative POSIX paths;
- repository-relative Windows paths;
- absolute Windows paths under `E:\GT-KB`;
- JSON/Python/shell escaped backslash forms;
- file URI forms when present in the repository;
- drive-letter case variants;
- valid per-referring-file relative paths.

Replace only exact, unambiguous path tokens. Bare filenames, stems, Python
module stems, natural-language names, and substring overlaps are evidence for
classification; they are never blindly replaced. Every ambiguous hit is
reported with file/line or structured-cell location and must be resolved by a
machine-readable policy entry or an amended proposal before apply.

### 5. Destination reconciliation and temporary retention

For each of the 90 rows, plan records source hash, destination hash, transformed
source hash, chosen canonical content hash, and compatibility mode.

- Equal source/destination pairs may proceed without content arbitration.
- A destination equal to the deterministic transformed source is accepted with
  evidence.
- Any other divergence fails planning until an explicit per-row content
  authority/resolution is recorded and independently reviewed. Blind source to
  destination or destination to source copying is forbidden.
- All obsolete sources remain present after apply.
- Old hook and agent-control paths become inert safety copies: launchers,
  registries, templates, docs, tests, and generators must resolve canonical
  destinations.
- `.claude/rules/<old>` remains a native compatibility projection. Its content
  must be generated or verified from canonical `config/agent-control/gtkb-*`
  content with deterministic parity; it is not an independent authority.

No deletion, cleanup, or retirement of an obsolete file is in scope.

### 6. Generator-first repair

The policy declares canonical generator/registry relationships. When a residual
occurs in generated output, apply must change the canonical source or registry,
run the declared generator, and verify the output. Direct edits to generated
files are forbidden unless the policy proves there is no generator and the
proposal explicitly lists the file as authoritative.

At minimum inspect and correctly disposition managed-artifact templates, SoT
registries, context-manifest projections, harness capability registries, Codex
hook wrappers/configuration, skill adapters, and all supported harness
projections under `.agent`, `.cursor`, `.codex`, and `.goose`.

### 7. Immutable plan, atomic writes, and bounded rollback

The runtime plan and reports live under
`.gtkb-state/file-reference-migration/wi5640/` and are non-authoritative runtime
evidence until summarized in the implementation report. The plan uses a stable
schema, sorted operations, SHA-256 hashes, and LF-normalized JSON serialization.

Apply uses same-directory temporary files plus atomic replace where supported.
Before each write it verifies the expected preimage hash. On failure it stops,
restores only already-written files from plan-recorded preimages, and emits a
partial-transaction report. It never invokes `git reset`, `git checkout`,
`git clean`, broad `git add`, stash operations, or deletion of retained sources.
The live Git index byte hash and staged-path set must be unchanged by the tool.

### 8. Independent verification

`verify` does not trust apply's replacement log. It re-parses the CSV and policy,
re-enumerates the root, re-queries structured data, re-hashes projections, and
recomputes residuals from scratch. Each residual record includes mapping ID,
variant, classification, file and line/column or database cell, load-bearing
status, exception ID, and evidence.

Run verify twice in separate processes after all generators and tests. Both
passes must produce identical inventory and residual hashes, zero unexplained
live residuals, zero unreadable/unclassified paths, and no proposed writes.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "CSV manifest plus owner decisions and fresh incident-disposition GO",
  "canonical_authority": "config/hooks and config/agent-control gtkb-prefixed destinations",
  "primary_route": "deterministic preflight-plan-apply-verify CLI",
  "before_behavior": "mixed old/new authority, live obsolete references, manual partial repairs",
  "after_behavior": "canonical consumers use new paths; obsolete files remain as classified safety copies",
  "self_descriptive_naming": "gtkb_file_reference_migration and wi5640 policy identify purpose and scope",
  "obsolete_guidance_disposition": "live obsolete guidance is replaced; audit history is retained and excluded",
  "history_preservation": "both prior bridge chains, Git history, stash evidence, and obsolete files are preserved",
  "baseline": "90 mappings; 25 divergent pairs; focused suite 203/209; residual closure unproven",
  "expected_result": "two identical zero-live-residual verification passes with all paths classified",
  "rollback": "plan-scoped preimage restoration only; no broad Git or deletion action",
  "hard_invariants": ["no obsolete-file deletion", "no audit-history mutation", "no raw DB mutation", "no Git index mutation"],
  "fail_closed_conditions": ["unreadable or unclassified path", "ambiguous residual", "preimage drift", "generator drift", "inventory mismatch", "test failure"],
  "essential_context_preservation": "native Claude rules remain deterministic compatibility projections while canonical control moves to config"
}
```

## Cross-Harness Disposition

No parity waiver is requested. The migration applies the same canonical-path
contract to every supported harness and must preserve each harness's native
delivery mechanism:

| Harness surface | Disposition |
| --- | --- |
| Claude (`.claude/hooks`, `.claude/rules`, `.claude/settings.json`, `.claude/skills`) | Behavioral parity required. Canonical hook paths move to `config/hooks`; `.claude/rules` remains a deterministic native compatibility projection of `config/agent-control`; managed skills and settings must resolve only canonical live targets. |
| Codex (`.codex/gtkb-hooks`, `.codex/hooks.json`, `.codex/config.toml`, `.codex/skills`) | Behavioral parity required. Wrapper/config references must resolve canonical hook and control paths; generated skill adapters must be regenerated from canonical sources and pass parity checks. |
| Cursor (`.cursor`) | Behavioral parity required. Cursor projections and references must resolve the same canonical control artifacts, with generator-first repair where the surface is generated. |
| Antigravity (`.agent`) | Behavioral parity required. Antigravity projections and references must resolve the same canonical control artifacts, with generator-first repair where the surface is generated. |
| Goose (`.goose`) | Behavioral parity required. Goose projections and references must resolve the same canonical control artifacts and pass the applicable manifest/parity checks. |
| Ollama, OpenRouter, and Alibaba Cloud Studio shared/configured surfaces | Behavioral parity required. Their registry, manifest, prompt, and shared managed-artifact references discovered by the deterministic scan must resolve canonical paths and pass their applicable generator/parity checks. |

The implementation report must give a per-harness disposition and executed
evidence. Any harness that cannot be brought to parity is a blocking result;
the Prime Builder may not invent or infer a waiver during implementation.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - all supported harness projections and
  fallback paths must resolve equivalent canonical control surfaces.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - migration evidence must cover every
  governed harness delivery mechanism.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - parity assertions and generated
  adapters must be regenerated and tested rather than manually patched.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook wrappers and configuration
  must resolve the canonical hooks without weakening fallback enforcement.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - GT-KB must remain functional;
  retained safety copies and repeated verification prevent premature breakage.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this fresh chain, independent GO, exact
  claim, packet, report, and VERIFIED are mandatory.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the active PAUTH,
  project, WI-5640, and target boundary are declared above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section links
  every relevant governing specification before review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - final verification must
  derive from these requirements and include current executed evidence.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - claim and packet
  checks must use an already-authorized classifier and the exact v3 chain.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - proposal, plan, report, and verdict
  retain real harness/session/model attribution.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-question and approval surfaces moved by
  the manifest must remain load-bearing and discoverable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - traversal remains in-root and
  application-boundary hits fail closed instead of mutating Agent Red.
- `GOV-WORK-TREE-HYGIENE-001` - unrelated dirty work and the Git index are
  preserved; rollback is file-scoped and auditable.
- `GOV-STANDING-BACKLOG-001` - newly discovered out-of-scope defects are
  recorded rather than silently absorbed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - decisions, exceptions, plans, tests,
  reports, and later deletion remain durable lifecycle artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - manifest, plan, source changes,
  verification, and owner decisions retain traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - retained, migrated, blocked,
  verified, and deletion-candidate states remain explicit.

## Specification-Derived Verification Plan

| Requirement | Executed verification required in implementation report |
| --- | --- |
| Manifest integrity | Run `preflight`; prove 90 rows, 33/38/19 categories, no duplicate/no-op/out-of-root/directory rows, all sources/destinations classified, and stable manifest hash. |
| Full-root classification | Prove every discovered path belongs to exactly one policy class; report counts/bytes/hashes; fail on unreadable, multiply classified, or unclassified paths. |
| Reference closure | Run independent `verify` twice in separate processes; require identical inventory/residual hashes and zero unexplained live residuals across every mapping variant and structured SQLite query. |
| Content reconciliation | Report all 90 source/destination/transformed hashes and the disposition of all 25 current divergent pairs; no blind overwrite. |
| Compatibility retention | Prove all obsolete files remain; prove old hooks/agent-control files are not live dependencies; prove all 38 `.claude/rules` mirrors match canonical content under policy. |
| Generator integrity | Run every policy-declared generator and its `--check` or parity test; prove generated files were not hand-edited. |
| Migration engine | Run `python -m pytest platform_tests/scripts/test_gtkb_file_reference_migration.py -q --tb=short`. Cover preflight, plan determinism, variants, encodings, exclusions, SQLite, ambiguity, atomic failure, rollback, and idempotency. |
| Cross-harness behavior | Run the 209-test focused parity command from the incident review and require 209/209 PASS. |
| Governance behavior | Run `python -m pytest groundtruth-kb/tests/test_governance_mutation.py -q --tb=short` and the complete implementation-authorization suite; require PASS. |
| Worktree nonimpairment | Hash the Git index and enumerate staged/unstaged/untracked paths before and after; require unchanged index bytes/staged set except ordinary worktree modifications explicitly in the plan. |
| Root/application boundary | Prove traversal never follows reparse points or paths outside `E:\GT-KB`; report any `applications/` residual without mutating it. |
| No deletion | Compare all 90 source paths before/after and require every source still present; no cleanup command may run. |

## Acceptance Criteria

1. A single deterministic engine and policy implement all five modes with
   focused tests; `preflight-validation.ps1`, `temp_path_fixer.py`, ad hoc
   search/replace, and agent-authored recursive edits are not execution paths.
2. The immutable plan completely classifies the root and records all exclusions,
   structured data, mappings, variants, generators, hashes, and proposed writes.
3. Every one of the 25 divergent pairs receives a reproducible transform proof
   or explicit reviewed authority decision before apply.
4. Apply changes only plan-listed paths, preserves encoding/newlines/attributes
   and unrelated bytes, and leaves the Git index/staged set unchanged.
5. All live consumers resolve canonical destinations. Historical bridge text,
   runtime state, inert retained sources, and declared native compatibility
   projections are separately classified and never disguised as live closure.
6. Two independent verify passes produce identical hashes, no pending writes,
   zero unexplained live residuals, and zero unreadable/unclassified paths.
7. All 90 obsolete source files remain present. No deletion, cleanup, stash
   drop, broad reset, commit, push, release, deployment, or credential work occurs.
8. Migration-specific, cross-harness, generator, governance, and authorization
   tests pass with current observed commands and results in the report.
9. The implementation report includes exact commands, plan/inventory hashes,
   classification counts, exclusion ledger, 90-row reconciliation table,
   residual/exception ledger, generator evidence, test results, Git-index
   evidence, rollback evidence, and worker-quality observations.
10. An unrelated Codex LO session must independently rerun the verification and
    file VERIFIED through the atomic finalization path before any commit is
    considered. Commit remains outside the active PAUTH.

## Files Expected To Change

- `scripts/gtkb_file_reference_migration.py`
- `config/file-reference-migration/wi5640.toml`
- `platform_tests/scripts/test_gtkb_file_reference_migration.py`
- Only plan-listed reference consumers within the declared `target_paths`.
- Canonical registries/templates and their generated projections when required
  to eliminate live obsolete references.
- No file under `bridge/` except future append-only artifacts in this v3 thread.
- No obsolete source file is deleted.

## Pre-Filing Preflight

The following checks were executed against this exact non-dispatchable draft:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v3 --content-file .gtkb-state/bridge-propose-drafts/gtkb-file-move-rename-canonicalization-v3-001.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v3 --content-file .gtkb-state/bridge-propose-drafts/gtkb-file-move-rename-canonicalization-v3-001.md
python scripts/proposal_target_paths_coverage_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-file-move-rename-canonicalization-v3-001.md --strict --json
```

Observed results:

- Applicability: exit 0, `preflight_passed: true`, no missing required or
  advisory specs, no blocking errors, and no unclassified target paths.
- Clause gate: exit 0; five clauses evaluated, four `must_apply`, one
  `may_apply`, zero must-apply evidence gaps, and zero blocking gaps.
- Target coverage: exit 0, verdict `clean`, with all implied prose and
  integration paths covered.
- The applicability preflight reports one expected future-parent warning for
  `config/file-reference-migration/wi5640.toml`. The new directory is itself an
  approved target and must not be created before GO; implementation creates it
  only after claim and packet authorization.
- Draft author-metadata warnings are expected on the non-dispatchable draft.
  The governed Codex writer inserts live author/session/model metadata before
  its in-memory compliance audit.
- `gt projects show-authorization` independently confirms the cited PAUTH is
  active, has no per-work-item inclusion restriction, covers source, test,
  configuration, documentation, metadata, runtime-state, governance-evidence,
  and bridge mutation classes, and forbids destructive cleanup, commit, push,
  release, deployment, dispatcher mutation, credential work, external-system
  mutation, and history rewrite.
- `gt projects show` confirms WI-5640 is an active project member.

No implementation claim or authorization packet was requested or created.

## Owner Decisions / Input

- `DELIB-202666274` authorizes the active Harness Parity project PAUTH while
  preserving independent review, exact claim, packet, nonimpairment, and no
  commit/destructive-cleanup boundaries.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` requires temporary retention
  of obsolete sources, repeated deterministic scans and functional checks, and
  a later separately authorized deletion phase.
- The owner directed that all `E:\GT-KB` files be deterministically inventoried
  and that every live obsolete reference be corrected except immutable audit
  trails such as `bridge/`; manual recursive find/replace is prohibited.
- The owner assigned all Prime Builder work for this program to Codex A and will
  use independent Codex interactive sessions for formal LO review.

## Prior Deliberations And Bridge Evidence

- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - controlling retention and
  deletion-phase decision.
- `DELIB-202666274` - active project authorization owner decision.
- `DELIB-202667106` - prior Loyal Opposition review of the canonical skill
  renaming rollout.
- `bridge/gtkb-wi5648-file-move-false-verification-incident-001.md` and `-002.md`
  - independent incident/quarantine proposal and non-implementation GO.
- `bridge/gtkb-file-move-rename-canonicalization-001.md` through `-007.md` -
  preserved structurally invalid original chain; evidence only.
- `bridge/gtkb-file-move-rename-canonicalization-v2-001.md` through `-006.md` -
  preserved replacement chain with unsupported VERIFIED; evidence only.

No prior decision authorizes deletion, blind recopying, raw database mutation,
or reliance on either historical chain for implementation.

## Risks / Rollback

- **Incomplete enumeration:** fail on unreadable/unclassified paths and record
  every exclusion with inventory evidence.
- **Performance collapse:** single-pass streaming and indexed patterns replace
  nested mapping-by-file scans; large structured data uses native read APIs.
- **Corrupt encoding or unrelated bytes:** preimage hashes, explicit decoding,
  byte-preserving reconstruction, and atomic writes fail closed.
- **Divergent pair data loss:** no blind copy; transform proof or reviewed
  per-row authority is mandatory.
- **Generated drift recreation:** canonical registry/template changes precede
  generator execution and independent output scans.
- **Premature breakage:** obsolete sources remain until a later lifecycle after
  repeated verification.
- **Mixed-worktree damage:** no index mutation or broad Git/stash operation;
  rollback restores only plan-recorded preimages.
- **False zero-residual claim:** verify is independent of apply and must pass
  twice with identical hashes and zero unexplained live residuals.

Rollback restores only files written by the immutable plan to their exact
preimage bytes and attributes, leaves every obsolete source in place, and emits
an auditable partial-transaction report. It does not delete evidence or invoke
broad repository operations.

## Explicit Non-Authority

This NEW proposal does not authorize implementation. Prime Builder must wait for
an independent LO GO on this exact v3 document, then acquire a matching claim
and implementation-start packet. It does not authorize commit, staging, push,
release, deployment, credentials, deletion, dispatcher/TAFE mutation, raw DB
mutation, or any action against the two historical file-move chains.

## Recommended Commit Type

`feat(migration):`

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
