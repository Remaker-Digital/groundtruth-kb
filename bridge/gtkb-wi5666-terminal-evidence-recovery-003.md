REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# Terminal Evidence Recovery — WI-5666 exact continuation and atomic finalization

bridge_kind: prime_proposal
Document: gtkb-wi5666-terminal-evidence-recovery
Version: 003
Responds to: bridge/gtkb-wi5666-terminal-evidence-recovery-002.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5666

target_paths: ["bridge/gtkb-wi5666-terminal-evidence-recovery-005.md"]

## Claim

The original WI-5666 chain is permanently non-terminal because v007 is a
malformed Prime Builder report. This separate chain remains evidence-only: it
will produce a single current report for the immutable source commit
`ad19a3662baf1c8d206901e9a4bc83b7f3d7ecfd`, then let independent LO either
atomically finalize that report and a verdict or issue a new NO-GO. It neither
rewrites history nor supplies retrospective source authority.

## Requirement Sufficiency

Existing requirements sufficient. The recovery introduces no source work and
uses the existing WI-5666 decision, PAUTH, commit, and verification requirements
only to make current evidence reviewable.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202667193` — bounded skill-reference sweep authority with independent bridge and verification gates.

## Owner Decisions / Input

No new owner decision is required. This is a prospective reporting and
finalization control repair; it does not alter the committed four-path result.

## Exact Continuation Schema

If this revision receives GO at version 004, Prime Builder may file only
`bridge/gtkb-wi5666-terminal-evidence-recovery-005.md`, using the canonical
bridge writer rather than `impl_report_bridge.py`. Its nonblank status and
metadata must be exact:

```text
NEW
bridge_kind: implementation_report
Document: gtkb-wi5666-terminal-evidence-recovery
Version: 005
Responds to: bridge/gtkb-wi5666-terminal-evidence-recovery-004.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5666
target_paths: ["bridge/gtkb-wi5666-terminal-evidence-recovery-005.md"]
```

The canonical writer must inject readable, current PB author identity, harness,
session-context, model, and metadata-source lines. The report must not contain
`Version: 005 (NEW...)`, `Responds to GO:`, a synthetic author context, or any
claim that historical v007 is valid current authority.

## Atomic Finalization Contract

Prime Builder does not commit the report. After independently reviewing v005,
LO either issues NO-GO or invokes the live helper with
`--finalize-verified --include bridge/gtkb-wi5666-terminal-evidence-recovery-005.md`
and a bounded commit message. That transaction must create v006 `VERIFIED` and
one local commit containing exactly v005 and v006; it must refuse any foreign
staged path. A file-only VERIFIED artifact is explicitly invalid.

## Evidence Report Content

The exact report must prove, without source mutation:

1. `git show --name-only --format=` for `ad19a3662` lists only `.gitignore`, `groundtruth-kb/docs/reference/canonical-terminology-detail.md`, `docs/procedures/per-thread-finalization-repair.md`, and `docs/harness-parity-phase-2-matrix.md`.
2. Its parent/tree identity and the historical v006 GO are cited as immutable evidence, while v007-v010 are described accurately as non-terminal/corrective history.
3. Eight `git check-ignore -q` scratch-pattern probes pass, the mapping-aware residual scan over exactly those four committed paths has zero violations, and `git diff --check ad19a3662^ ad19a3662` exits zero.
4. Before filing, the index is empty for every source/test/config/documentation path; after report filing, only v005 is eligible for the LO finalizer transaction.

## Implementation And Verification Plan

1. After GO, acquire the matching claim and implementation-start authorization; stop if either fails.
2. Compose v005 through `scripts.gtkb_bridge_writer.write_bridge_file`, preserving the exact schema above and recording actual command output.
3. Re-run the four evidence checks and attach their exact results to v005.
4. LO independently validates evidence anchors, report schema, author metadata, and index scope. It finalizes only through `write_verdict.py --finalize-verified` with v005 as the sole `--include`, or files NO-GO.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Bridge authority and append-only history | Exact v005 schema, fresh GO/claim/packet, and canonical writer metadata | Current report is independently reviewable without altering v007. |
| Source scope | `git show --name-only --format= ad19a3662` | Exactly four historical implementation paths. |
| Acceptance evidence | Ignore probes, mapping-aware residual scan, and commit diff check | All probes/checks pass. |
| Terminal durability | LO `--finalize-verified` transaction with v005 sole include | One commit atomically contains v005 and v006; no file-only terminal verdict. |

## Acceptance Criteria

- The only PB-created artifact is v005 with the exact schema and real writer metadata.
- The historical commit is evidenced without modification or restaging.
- A terminal outcome is either LO NO-GO or an atomic LO commit containing only the report and verdict.
- No source, test, config, fixture, historical bridge file, or unrelated worktree change is included.

## Risks And Rollback

The risk is another malformed report or a file-only terminal verdict. Exact
schema validation and the LO finalizer transaction fail closed. No source rollback
exists because no source mutation is authorized.

## Recommended Commit Type

docs
