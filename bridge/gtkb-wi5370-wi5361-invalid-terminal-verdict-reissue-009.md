REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# WI-5370 / WI-5361 Canonical Invalid-Verdict Preservation And Reissue Repair

bridge_kind: prime_proposal
Document: gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue
Version: 009
Responds to: bridge/gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue-008.md
Revises: bridge/gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue-007.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Related Work Items: WI-5361, WI-5501

target_paths: ["bridge/gtkb-wi5361-dispatch-cap-authority-precedence-004.md", "bridge/hunks/gtkb-wi5361-dispatch-cap-authority-precedence-004-invalid-body.md"]

implementation_scope: bridge | governance_evidence | repository_metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Revision Claim

Both version-008 findings are accepted and corrected.

The current WI-5361 version-004 file is not treated as the original
2,534-byte incident and is not characterized as disposable residue. It is a
second, independently authored Loyal Opposition verification body containing
substantive and currently reproducible test and lint evidence. Its current
identity is:

- byte length: `1988`
- SHA-256:
  `7156d04b75b73d389e13f706820f39ea5fe62d9ca783491d136edaf30ff7ff78`
- Git blob with filters disabled:
  `087ba3add848bbaa572be3b4795b1855a5bbed9b`
- first status line: `VERIFIED`
- author: `loyal-opposition/cursor/E`

The canonical finalizer rejects the body because required finalization
evidence is absent, beginning with `Recommended commit type`. The body also
lacks the complete specification-to-test and executed-command sections
required for terminal finalization. Those structural omissions do not erase
the body's substantive value.

This revision preserves the exact bytes at a canonical bridge-evidence path
under `bridge/hunks/`, then permits removal of only the invalid untracked
numbered file so an independent Loyal Opposition session can reissue the
same version through the canonical finalizer with the missing evidence.
No noncanonical or retired preservation carrier is in scope or cited as
evidence.

The transaction must hold claims on both the WI-5370 repair thread and the
target `gtkb-wi5361-dispatch-cap-authority-precedence` thread. The target
claim remains held through exact preservation, bounded removal, and repair
report publication so another reviewer cannot repopulate version 004 during
the transaction.

No source, test, configuration, dispatcher, TAFE, harness, runtime, database,
Git history, deployment, release, or credential mutation is proposed.

## Findings Addressed

### Finding 1 - Current bytes differ from the original incident

Accepted.

The current body has been read in full and classified as a genuine second LO
verification attempt. Its evidence was freshly checked:

- `python -m pytest
  platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py -q
  --tb=short` passed `7/7` with one existing pytest configuration warning.
- Ruff check passed on the two source files and focused test.
- Ruff format reported all three files already formatted.
- The three WI-5361 source/test targets are clean and trace to committed
  baseline commit `42a252ab`.
- Direct invocation of `validate_verified_body()` rejects the current body:
  `VERIFIED verdict body must include Recommended commit type evidence.`

The preservation target is renamed to describe exactly what it is:
`bridge/hunks/gtkb-wi5361-dispatch-cap-authority-precedence-004-invalid-body.md`.
It will contain the source bytes without wrapper text so length, SHA-256,
blob identity, and byte comparison remain exact. The repair report must call
it a substantive invalid-body preservation artifact, never an operative
verdict or disposable archive.

### Finding 2 - No claim protected the target thread

Accepted.

Implementation start requires:

1. a matching implementation claim for this WI-5370 repair thread;
2. a separately acquired claim on
   `gtkb-wi5361-dispatch-cap-authority-precedence`;
3. proof that both claims are held by the same active session throughout the
   preservation/removal transaction;
4. exact two-path schema-v3 implementation-start authorization; and
5. immediate operation-time revalidation before each write or removal.

If the target-thread claim cannot be acquired, if either claim changes, or if
the source identity changes, the transaction stops before mutation and
returns for renewed review.

## Requirement Sufficiency

Existing requirements are sufficient. The defect is incomplete application
of existing worktree-hygiene, bridge-authority, provenance, and finalization
rules. Version 008 identifies no missing policy; it requires correct
classification, canonical preservation, and cross-thread mutual exclusion.

## Proposed Scope

### Phase 1 - Prime Builder bounded target-slot repair

1. Acquire and verify both required claims.
2. Obtain a schema-v3 start packet for exactly the two declared paths.
3. Reconfirm the source exists, is untracked, begins with `VERIFIED`, and
   exactly matches the declared length, SHA-256, and Git blob.
4. Confirm the canonical preservation target is absent. Stop on any existing
   mismatched target.
5. Write the source bytes unchanged to the preservation target.
6. Verify exact source/preservation byte equality, length, SHA-256, and Git
   blob identity.
7. Remove only the invalid untracked source version-004 file.
8. Confirm the target thread falls back to version 003 `NEW`, the
   preservation evidence remains exact, and the unrelated staged/index state
   is unchanged.
9. File the WI-5370 implementation report while retaining the target-thread
   claim, then release both claims through the governed path.

### Phase 2 - Independent Loyal Opposition reissue

Phase 2 is not Prime Builder implementation authority. After Phase 1 is
independently verified, a separate LO session must:

1. acquire the target-thread claim;
2. re-read versions 001 through 003 plus the canonical preserved invalid body
   and this repair chain;
3. rerun the focused seven-test and Ruff commands;
4. author a corrected version-004 `VERIFIED` with full applicability,
   clause, spec-to-test, commands/results, recommended commit type, and
   finalization evidence;
5. use the canonical atomic finalizer with only the WI-5361 bridge chain and
   three clean approved source/test targets; and
6. confirm durable commit/finalization before WI-5361 returns to terminal
   resolved state.

If concurrent-finalizer safety remains unresolved, finalization waits for
terminal WI-5501 or a separately owner-directed exclusive finalization
window.

## Out Of Scope

- Rewriting any committed bridge predecessor.
- Changing the substantive LO verification conclusion or attributing it to
  Prime Builder.
- Source/test changes, whole-file adoption, broad cleanup, or unrelated
  staging.
- Any noncanonical preservation location or evidence citation.
- Dispatcher/TAFE configuration or runtime, harness state, database content,
  credentials, Git history rewrite/push, deployment, or release.

## Cross-Harness Disposition

The repair is harness-neutral. The malformed body was authored by Cursor E,
but canonical validation, target-thread claims, exact preservation, and the
LO-only reissue requirement apply identically to supported harnesses A, B, C,
and E. Provider harnesses D, F, and H are not mutation targets and receive no
special path. No parity waiver is requested.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5370; WI-5361; bridge/gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue-008.md; DELIB-202666332",
  "canonical_authority": "GOV-WORK-TREE-HYGIENE-001; GOV-FILE-BRIDGE-AUTHORITY-001; GOV-DOCUMENT-AUTHOR-PROVENANCE-001",
  "primary_route": "dual governed work-intent claims, exact schema-v3 start, canonical bridge-evidence preservation, independent LO reissue, atomic VERIFIED finalizer",
  "before_behavior": "A repair claim protected only its own thread, while a different substantive but structurally invalid WI-5361 verdict could be removed without classifying or protecting its target thread.",
  "after_behavior": "The exact substantive body is preserved canonically, both repair and target threads are mutually excluded during the bounded transaction, and only independent LO can reissue the corrected terminal verdict.",
  "self_descriptive_naming": "The preservation path names WI-5361, version 004, and invalid-body status without calling the evidence an operative verdict.",
  "obsolete_guidance_disposition": "The prior interchangeable-incident assumption and any noncanonical preservation carrier are superseded and prohibited.",
  "history_preservation": "The WI-5370 repair chain records both byte identities and the reason for the bounded untracked-slot repair; the substantive current body is preserved byte-for-byte under bridge/hunks.",
  "baseline": {
    "source_length": 1988,
    "source_sha256": "7156d04b75b73d389e13f706820f39ea5fe62d9ca783491d136edaf30ff7ff78",
    "source_git_blob": "087ba3add848bbaa572be3b4795b1855a5bbed9b",
    "focused_tests": "7 passed with one existing warning",
    "quality": "Ruff check passed; three files already formatted"
  },
  "expected_result": {
    "phase_1": "exact canonical preservation, one invalid untracked slot removed, target thread falls back to NEW v003, no unrelated index change",
    "phase_2": "independent LO reissues valid VERIFIED v004 and atomically finalizes the exact bridge/source set",
    "terminal_truth": "WI-5361 is terminal only after the corrected verdict and focused commit are durable"
  },
  "rollback": {
    "instructions": "Before corrected reissue, restore the preserved exact bytes to the numbered source path only under the same dual-claim and operation-time authority.",
    "verification": "Recheck length, SHA-256, Git blob, byte equality, thread status, and unrelated index neutrality."
  },
  "hard_invariants": [
    "no current body is treated as the original incident bytes",
    "no removal occurs without exact canonical preservation",
    "both repair and target thread claims remain held through report publication",
    "Prime Builder never authors VERIFIED for WI-5361",
    "no noncanonical artifact is cited or created",
    "no source, test, dispatcher, TAFE, harness, database, credential, deployment, release, or unrelated Git state changes"
  ],
  "fail_closed_conditions": [
    "either claim is absent, held by another session, or changes during the transaction",
    "source identity differs from the declared length, SHA-256, blob, status, or author body",
    "preservation target exists with different bytes",
    "schema-v3 start or operation-time authority fails",
    "byte equality or index-neutrality verification fails",
    "independent LO cannot rerun tests or satisfy the canonical finalizer floor",
    "WI-5501 is nonterminal and no exclusive finalization window exists when commit finalization is attempted"
  ],
  "essential_context_preservation": "The repair retains original and current incident identities, substantive LO evidence, exact claims, start packet, byte checks, focused test results, finalizer requirements, ownership boundaries, and rollback route."
}
```

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202666332` authorizes bounded clean-worktree finalization while
  excluding uncharacterized concurrent bytes. This revision characterizes
  the current bytes and preserves them exactly before any removal.
- `DELIB-202666274` is the owner decision behind the active Tree
  Stabilization project authorization.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` requires canonical
  bridge artifacts to depend only on canonical evidence.
- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` retires the
  former noncanonical assessment carrier; this proposal uses only canonical
  bridge paths.
- `bridge/gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue-008.md` is the
  independent NO-GO this revision answers.

## Owner Decisions / Input

No new owner decision is required for proposal filing. Existing Tree
Stabilization authority permits governed bridge, repository-metadata, and
governance-evidence work while preserving the exact claim, start,
operation-time, independent review, and finalization gates described here.

The owner canonicality decisions require the preservation evidence to remain
inside the canonical bridge surface. The owner dispatcher-configuration hold
remains binding; dispatcher configuration and runtime are outside scope.

## Specification-Derived Verification Plan

| Requirement | Executable verification | Required result |
| --- | --- | --- |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`; `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Recompute length, SHA-256, Git blob, first line, author metadata, and byte comparison immediately before/after preservation. | Exact declared identity and byte equality. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Inspect both claims, schema-v3 packet, operation-time checks, exact thread states, and helper-mediated report/reissue. | Same-session dual claims; only PB report and independent LO verdict roles are used. |
| `GOV-WORK-TREE-HYGIENE-001` | Scoped status before/after both targets plus staged-index snapshot comparison. | Only preservation creation and invalid untracked source removal occur; unrelated index unchanged. |
| Canonical owner decisions | Run canonical-reference forbidden-surface scan on proposal, report, preservation references, and corrected verdict. | Zero noncanonical evidence references. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused seven-test module, Ruff check, Ruff format, applicability, clause, and `validate_verified_body()` before reissue. | Tests/lint pass; old body fails the floor; corrected body passes it. |
| Cross-harness parity specs | Verify all supported finalizer projections enforce the same required sections and target claim. | No harness-specific bypass. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve both paths and all three WI-5361 source/test paths under `E:/GT-KB`. | Every dependency stays in-root. |

Required commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py platform_tests/groundtruth_kb/test_bridge_dispatch_cap_authority.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue
git status --short -- bridge/gtkb-wi5361-dispatch-cap-authority-precedence-004.md bridge/hunks/gtkb-wi5361-dispatch-cap-authority-precedence-004-invalid-body.md
git diff --cached --name-status
```

## Acceptance Criteria

1. Current v004 is classified as substantive LO evidence with exact current
   identity, not conflated with the original incident bytes.
2. Exact bytes are preserved only under the canonical `bridge/hunks/` target.
3. Both thread claims and exact start/operation-time authority are active
   before mutation.
4. Only the invalid untracked v004 source path is removed in Phase 1.
5. Repair report records byte equality, target fallback, claim history, and
   unrelated index neutrality.
6. Independent LO reruns tests and reissues a structurally valid v004 through
   the canonical helper/finalizer.
7. WI-5361 becomes terminal only after durable corrected verdict commit.
8. No noncanonical artifact, broad cleanup, source/test change, dispatcher,
   TAFE, harness, database, credential, push, deployment, release, or
   unrelated Git mutation occurs.

## Scope Changes

- Replaces the old preservation destination with a canonical `bridge/hunks/`
  exact-body target.
- Classifies and preserves the current 1,988-byte substantive LO body rather
  than treating it as the original 2,534-byte incident.
- Adds mandatory target-thread claim ownership and same-session dual-claim
  evidence.
- Makes independent LO corrected reissue and atomic finalization explicit.
- Keeps source/test behavior unchanged.

## Pre-Filing Preflight Subsection

Candidate-content checks executed against these exact completed bytes:

- Applicability preflight: PASS, `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`,
  `blocking_errors: []`, packet
  `sha256:52d02e194c7b21d2f4e76b641bb4607a93bb20e3bc504ffbeeadbbd95412a680`.
- Mandatory clause preflight: PASS, five clauses evaluated, four
  `must_apply`, one `may_apply`, zero mandatory evidence gaps, zero blocking
  gaps, exit `0`.
- Noncanonical path-reference scan: PASS, zero references to retired
  assessment paths, scratchpads, auto-memory, or harness-local owner-action
  carriers. Canonical Deliberation Archive IDs remain permitted evidence.
- First-line role eligibility: active Prime Builder is authorized to file
  `REVISED`; the latest exact repair-thread status is independent `NO-GO`
  v008.
- The governed revision helper must still pass credential, author,
  project-linkage, related-work collision, target coverage, cross-harness,
  non-impairment, and publication-admission checks before writing v009.

## Risk And Rollback

The main risk is another LO process repopulating the target slot after
removal. Dual claims held through repair-report publication close the
unprotected interval identified by version 008. The second risk is loss or
mischaracterization of substantive evidence; exact canonical preservation
and identity checks address it.

Before corrected reissue, rollback restores only the preserved exact bytes
to the numbered source path under renewed dual-claim and operation-time
authority. After corrected finalization, the invalid-body evidence remains
historical and the valid numbered verdict is authoritative. No Git history
rewrite or unrelated rollback is permitted.

## Files Expected To Change

- `bridge/gtkb-wi5361-dispatch-cap-authority-precedence-004.md`
- `bridge/hunks/gtkb-wi5361-dispatch-cap-authority-precedence-004-invalid-body.md`

## Recommended Commit Type

`chore(bridge)`: preserve and reissue WI-5361 invalid terminal evidence.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
