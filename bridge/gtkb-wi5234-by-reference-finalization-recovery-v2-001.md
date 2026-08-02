NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb353-983b-7383-b57e-3b9fc6410af5
author_model: OpenAI Codex
author_model_version: GPT-5.6
author_model_configuration: Codex desktop; owner-designated Prime Builder; manual physical-bridge processing with dispatcher disabled
author_metadata_source: explicit_interactive_session_metadata

# WI-5234 By-Reference Finalization Recovery - Exact-Session Author Metadata

bridge_kind: prime_proposal
Document: gtkb-wi5234-by-reference-finalization-recovery-v2
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5234

target_paths: ["bridge/gtkb-wi5234-by-reference-finalization-recovery-v2-003.md"]

implementation_scope: governance_evidence_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_activation_in_scope: false

## Summary

Recover WI-5234 through a no-code, by-reference finalization cycle. The exact-session
Codex model-attestation implementation and the later source-coherence correction are
already committed, present at current HEAD, clean in the scoped worktree, and passing
focused tests. What remains missing is a current independently reviewed bridge path
that can attribute only the acceptance-mapped existing bytes, record fresh evidence,
and obtain independent VERIFIED without editing source or tests.

This proposal authorizes only a future governance-evidence implementation report at
the declared target path. It does not authorize source, test, runtime-envelope,
dispatcher, TAFE, registry, Git, credential, deployment, release, or cleanup mutation.

## Historical Chain Quarantine

Two earlier WI-5234 bridge threads remain append-only evidence, not current
implementation authority:

- `gtkb-wi5234-codex-session-model-author-metadata` is latest targetless NO-GO v004.
  It accepts withdrawal of stale GO v002, keeps WI-5234 open, and requires any renewed
  target work to use fresh authority, review, GO, claim, and implementation-start.
- `gtkb-wi5234-codex-session-model-metadata-attestation` is latest NO-GO v006. It
  accepted the exact-session design but found that partial explicit/environment model
  fields could hybridize with exact-envelope fields and required atomic-bundle denial
  coverage plus a true implementation report.

Neither historical thread is rewritten, extended as though it were current authority,
or treated as terminal. This fresh thread is a recovery carrier only.

## Owner Approval And Current Authority

- `DELIB-20260801-WI5234-IMPLEMENTATION-APPROVAL` records the owner's explicit
  approval of WI-5234 as written while preserving the v004 NO-GO, fresh-successor
  lifecycle, exact-session provenance scope, independent review, and all normal gates.
- `PROJECT-GTKB-GOOSE-HARNESS-ADOPTION` is current active v6; its earlier retired v4
  state is historical.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` v2 is active,
  unexpired, list-free, and permits bridge/governance-evidence work while retaining
  independent GO, claim, implementation-start, report, and VERIFIED gates.
- WI-5234 remains open and backlogged. Its legacy `approval_state` field is not used to
  erase the explicit current owner decision above.

## Existing Implementation Provenance

Current HEAD is `75decbfa704fe50288aecbc5669def329a0825df`. The three committed
provenance anchors are:

1. `9373c523164ecfa8a2acadfe4c6e7fd1dcb008ee` - contains the four-target
   exact-session attestation implementation and its original focused tests.
2. `6c0b0628fdb0b34bf06168ca37955649cc07ff30` - binds Codex attestation to the
   exact host thread and extends the matching CLI-provenance coverage.
3. `02e12e7b0e1a1172ea8acf1b9a99e2ee9b8e54af` - a custodial sweep commit that
   contains the v006 source-coherence correction and parameterized denial tests.

The recovery report must not retroactively classify each whole commit as WI-5234.
Those commits contain adjacent or unrelated work. Attribution is limited to the
acceptance-mapped existing behavior and, for the v006 correction, the exact current
atomic-bundle rejection block in `scripts/bridge_author_metadata.py` plus the exact
parameterized partial-bundle denial block in
`platform_tests/scripts/test_bridge_author_metadata.py`. Cursor-specific additions and
all other hunks in the same custodial commit remain excluded.

## Current Exact Cohort

The evidence cohort is read-only and is not in `target_paths` because this recovery
does not mutate or claim these files:

| Evidence path | Current SHA-256 | Scoped state |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` | `F843237ED5DB443418389A1B3B1276B2D0BF1342F4F9B03D5D0910B7912381DD` | clean |
| `scripts/bridge_author_metadata.py` | `0AC4168859E2E4FF855E860A3C5F6B6A21CB57DC4B7336D624728EE2F741A90D` | clean |
| `platform_tests/scripts/test_session_envelope_cli_provenance.py` | `B2C2A41BBC55323C0F362267DFE935C572B02AF8DA54DB01229A3A2472A1E230` | clean |
| `platform_tests/scripts/test_bridge_author_metadata.py` | `39DD96E0987346A68869C0E872331AB7ECEA9AA647B0FD247E15130BFDF82097` | clean |

Any hash or scoped-worktree drift before report filing fails closed and returns this
thread for revision. The report may observe but may not repair drift.

## WI-5812 Shared-Target Ordering

WI-5812 latest REVISED v013 names `scripts/bridge_author_metadata.py` and
`platform_tests/scripts/test_bridge_author_metadata.py`, but remains blocked on
terminal WI-5723 completion and has no current GO or implementation claim. This
recovery establishes explicit ordering rather than a speculative hunk-sharing lane:

1. WI-5234 recovery may perform read-only verification and governance-evidence filing
   first, without changing or claiming either shared source/test path.
2. WI-5812 must remain non-implementing while WI-5234 is nonterminal.
3. Before any later WI-5812 GO/start, it must reread the WI-5234 recovery head and
   confirm terminal VERIFIED or return for a new independently accepted overlap
   disposition.

This ordering satisfies WI-5812 v013's currentness requirement without absorbing its
Goose scope, its eight-target design, or WI-5723/WI-5880 dependencies.

## By-Reference Finalization Boundary

After an independent GO on this exact proposal, Prime Builder may:

1. Acquire a fresh `go_implementation` claim for this recovery slug.
2. Obtain a schema-v3 implementation-start packet whose only mutable target is
   `bridge/gtkb-wi5234-by-reference-finalization-recovery-v2-003.md`.
3. Re-read both historical WI-5234 heads, current project/PAUTH, the owner decision,
   current HEAD ancestry, the four hashes, scoped worktree state, claims, and WI-5812
   ordering state.
4. Execute the exact read-only verification commands below.
5. File a factual by-reference implementation report through the governed writer,
   with exact observed counts, hashes, warnings, provenance anchors, and the strict
   attribution exclusions above.

No source/test edit, source/test claim, backfill, cherry-pick, amend, rebase, staging,
commit, push, or runtime activation is authorized. The future report is not itself
VERIFIED; independent Loyal Opposition verification remains mandatory.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
defines truthful non-placeholder author provenance; the bridge and project gates define
the recovery lifecycle; v006 defines the atomic source-coherence correction; and the
current focused tests exercise both positive exact-session behavior and negative hybrid
inputs. No new or revised formal requirement is introduced.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - exact-session, non-placeholder,
  source-coherent author model provenance.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - append-only role-correct proposal, report, and
  independent-verdict lifecycle.
- `GOV-SESSION-ROLE-AUTHORITY-001` - exact session evidence does not substitute or
  mutate dispatcher/default role authority.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - current active project authority
  bounds the recovery.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - operation-time PAUTH,
  claim, and start checks remain mandatory.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the owner decision and PAUTH do
  not bypass independent bridge review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - explicit PAUTH/project/WI and
  exact report target linkage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing
  specifications are linked here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the report and independent
  verdict require executed specification-derived evidence.
- `GOV-WORK-TREE-HYGIENE-001` - no foreign dirty byte is adopted or rewritten.
- `GOV-STANDING-BACKLOG-001` - WI-5234 remains the canonical work carrier until
  independently verified and resolved.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the orphaned implementation and owner
  decision are recovered as durable governed evidence rather than chat-only state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - source, tests, decisions, bridge state,
  and verification remain linked without rewriting historical artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the nonterminal historical chains move
  through a fresh candidate, review, report, and verification lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - every evidence and bridge path remains
  inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260801-WI5234-IMPLEMENTATION-APPROVAL` - current explicit owner approval
  for WI-5234 with the fresh-successor lifecycle preserved.
- `DELIB-202667749` - owner-evidenced project reactivation reflected by current project
  v6.
- `DELIB-202667530` - explicit exact-session envelope direction is canonical.
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` - NO-ACTION withdrew stale authority
  without closing WI-5234.
- `DELIB-202666274` - active project-level blocker-repair authority and retained
  independent gates.
- `bridge/gtkb-wi5234-codex-session-model-author-metadata-004.md` - targetless current
  disposition of the first thread.
- `bridge/gtkb-wi5234-codex-session-model-metadata-attestation-006.md` - exact
  source-coherence findings recovered here.
- `bridge/gtkb-wi5812-goose-governed-filing-attestation-013.md` - current shared-target
  ordering contract.

## Owner Decisions / Input

- The owner explicitly approved WI-5234 as written in the current interactive Prime
  Builder session; the decision is archived as
  `DELIB-20260801-WI5234-IMPLEMENTATION-APPROVAL`.
- That approval does not waive fresh independent GO, exact claim, schema-v3 start,
  factual report, or independent VERIFIED.
- Earlier owner approval of current HEAD permits the existing committed bytes to be
  assessed by reference; it does not authorize reclassification of unrelated hunks.
- Dispatcher/TAFE remains deliberately disabled for dispatch. This proposal neither
  enables nor configures it; governed bridge-state publication is the only permitted
  state write.

## Specification-Derived Verification Plan

Run from `E:\GT-KB` after fresh GO/claim/start currentness checks:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_author_metadata.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py -q --tb=short
```

Required: all collected tests pass. The current pre-proposal baseline is 113 passed
with one non-failing `asyncio_mode` configuration warning.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py scripts/bridge_author_metadata.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_author_metadata.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py scripts/bridge_author_metadata.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_author_metadata.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py scripts/bridge_author_metadata.py platform_tests/scripts/test_session_envelope_cli_provenance.py platform_tests/scripts/test_bridge_author_metadata.py
```

Required: lint, format, and whitespace checks pass. The current pre-proposal baseline
passes all three.

The report must additionally reproduce the partial-runtime cases required by v006:
model-only, version-only, configuration-only, metadata-source-only,
context-window-only, and model-plus-version without configuration. Each must fail
closed before exact-session fallback can supply missing model fields.

## Acceptance Criteria

1. Both historical WI-5234 threads remain append-only and nonterminal evidence.
2. Current project v6, active PAUTH v2, current owner approval, and current WI state
   are revalidated at report time.
3. The four evidence files remain clean and match the exact SHA-256 cohort above.
4. The three provenance commits remain ancestors of current HEAD.
5. Exact-session Codex author metadata supplies model, version, configuration, and
   attestation source only from the matching open role-valid session document.
6. Shared-current projections, wrong sessions, wrong harnesses, closed documents,
   placeholders, and untrusted metadata sources fail closed.
7. Complete explicit/environment runtime model bundles retain precedence.
8. Every partial explicit/environment runtime model bundle named by v006 fails closed
   without hybridizing fields from the exact session envelope.
9. Focused pytest reports a complete pass with exact count and warnings disclosed;
   Ruff check, Ruff format check, and scoped diff check pass.
10. Attribution excludes Cursor-specific and every unrelated hunk from the provenance
    commits; no whole custodial commit is relabeled as WI-5234.
11. WI-5812 remains non-implementing until this recovery is terminal VERIFIED or a
    later independent overlap disposition supersedes this ordering.
12. Only the declared future report path may be created after GO/start. No source,
    test, envelope, registry, dispatcher/TAFE activation/configuration, Git,
    credential, external-system, deployment, release, or cleanup mutation occurs.
13. The report receives an independent Loyal Opposition VERIFIED before WI-5234 may
    be resolved.

## Non-Impairment

- No existing source or test byte changes.
- No adoption of the foreign dirty `session/envelope.py` hunk.
- No collision with WI-5603, WI-5723, WI-5812, or WI-5880 implementation scope.
- No dispatcher/TAFE activation, configuration, routing, worker, lease, or eligibility
  mutation.
- No durable role-map, harness identity, session envelope, or credential change.
- No Git staging, commit, push, history rewrite, release, deployment, or destructive
  cleanup.
- No claim that test passage alone is VERIFIED; independent review remains decisive.

## Risk And Rollback

Primary risk is over-attributing a large custodial commit. Exact current hashes,
commit ancestry, hunk-limited attribution, and explicit exclusions contain it. A
second risk is shared-target sequencing drift with WI-5812; current-head and claim
rechecks fail closed before filing.

Rollback is append-only: if any evidence drifts or independent review finds a gap,
file the next numbered correction. Do not rewrite bridge history or source files.

## Recommended Commit Type

No source commit. A later independently verified bridge-only finalization may use the
repository's governed bridge finalization convention.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
