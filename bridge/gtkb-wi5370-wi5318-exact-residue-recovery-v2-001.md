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

# WI-5370 / WI-5318 Exact Residue Recovery — Strict Controller v2

bridge_kind: prime_proposal
Document: gtkb-wi5370-wi5318-exact-residue-recovery-v2
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Related quarantined thread: gtkb-wi5370-missing-targets-wi5318-failed-verified-finalization-repair

target_paths: ["archive/bridge-terminal-verdicts/gtkb-wi5318-failed-verified-finalization-repair-007.md"]

implementation_scope: additive_exact-byte_governance-evidence_recovery_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_activation_in_scope: false
git_commit_or_push_in_scope: false

## Summary

Recover and durably preserve the original WI-5318 2,103-byte terminal-verdict
residue at one tracked in-root archive path. The exact residue still exists as
Git blob `5d58c51bdfbd5708b4006c161d69cd5036ccd654`; deterministic CRLF
reconstruction reproduces the raw size and SHA-256 independently recorded in
the original implementation report and its first review.

This is a fresh strict controller because the prior thread cannot lawfully
accept another numbered version. Its version 003 declares decorated metadata
`Version: 003 (NEW; post-implementation report)`, and the current typed bridge
publication authority fails closed with `WRONG_BRIDGE_VERSION_METADATA` before
evaluating a successor. The old chain is retained unchanged as quarantined
audit evidence. This proposal does not rewrite it, bypass the governed writer,
or depend on unapproved WI-5637/WI-5827 parser-normalization work.

No archive mutation has occurred under this proposal. After an independent
`GO`, a matching `go_implementation` claim, and a valid schema-v3
implementation-start packet, Prime Builder will write only the declared
archive target and then file a strict implementation report on this new chain
for independent verification.

## Historical Chain Quarantine And Authority Boundary

The historical thread
`gtkb-wi5370-missing-targets-wi5318-failed-verified-finalization-repair`
remains read-only. Its v006 `NO-GO` supplies the unresolved findings and review
evidence, but none of its malformed lifecycle can supply implementation-start
authority for this controller.

An attempted governed v007 filing was rejected before write. After registry
contention cleared, the deterministic error was:

```text
WRONG_BRIDGE_VERSION_METADATA: Version metadata
'003 (NEW; post-implementation report)' does not match 003
```

No historical bridge file may be edited, removed, renamed, hidden, or treated
as corrected. This clean controller is the established repair-forward pattern:
strict new authority, explicit old-chain quarantine, and additive evidence
only.

## Exact Source And Protected Live-Path Identity

The intended historical residue is mechanically identifiable without guessing
from the reused live filename:

- Git object identity: `5d58c51bdfbd5708b4006c161d69cd5036ccd654`.
- Git-object byte length: 2,060 bytes with 43 LF newline bytes.
- Git-object SHA-256: `cb9117938fd4f9baa816e4d3987033f1a9a4926ad772c8d3194e54ee51ccda36`.
- Reconstructing the 43 LF line endings as CRLF produces exactly 2,103 bytes.
- Reconstructed raw-worktree SHA-256:
  `0859be38938b488b63d8a7f586e8d530edce93a6d5b88312844c280ed1868cdb`.
- The reconstructed raw size/hash exactly match the independently recorded
  original residue evidence in historical versions 003 and 004.

The current tracked live file at
`bridge/gtkb-wi5318-failed-verified-finalization-repair-007.md` is a different,
12,041-byte governance artifact with raw SHA-256
`406e9e3e219f714397576e78861fdafd3986f35499733114db09026f6a489af3`
and index blob `980db709c666d1fc49c87ffe4cd0affbab089633`. It belongs to an
active append-only chain and is explicitly outside mutation scope.

The verified batched archive service cannot safely actuate this exceptional
case through its normal scanner because the original source pathname has been
reused by tracked live governance history. This proposal reuses only that
service's exact-byte identity, tracked-destination, fail-closed, and audit
invariants. It neither runs a new batch nor removes a `bridge/` file.

## Corrective Transaction After Independent GO

1. Reconfirm that this controller is latest `GO`, the current session holds its
   matching implementation claim, the PAUTH remains active, and the
   implementation-start packet authorizes exactly the declared archive path.
2. Fail closed if the archive target exists, is ignored, is outside `E:/GT-KB`,
   or is already tracked under a different object identity.
3. Read Git blob `5d58c51bdfbd5708b4006c161d69cd5036ccd654` through Git
   plumbing and verify object size, LF SHA-256, newline count, and the exact
   CRLF reconstruction.
4. Snapshot the protected live predecessor's raw size, raw SHA-256, and index
   blob OID. Write only the declared archive target from the recovered blob.
5. Verify that the archive path is non-ignored and its normalized Git blob
   identity is exactly `5d58c51bdfbd5708b4006c161d69cd5036ccd654`. If checkout
   newline policy materializes CRLF, also require raw worktree size 2,103 and
   the recorded raw SHA-256.
6. Recheck that the protected live predecessor retains all three pre-transaction
   identity values and that its append-only thread still resolves from its
   current live versions rather than the archive.
7. File a strict implementation report on this controller with the claim/start
   packet identifiers, exact commands/results, target identity, and full
   specification-derived evidence for independent Loyal Opposition review.

No Git commit, staging, push, dispatcher/TAFE activation or configuration,
destructive cleanup, release, deployment, external-system mutation, or KB
mutation is authorized by this proposal or the current PAUTH. The governed
writer's required bridge-state publication is not dispatcher activation.

## Requirement Sufficiency

Existing requirements sufficient.

`DELIB-202666766` supplies the owner's operative decision to preserve this
defect class through tracked in-root exact-byte archival.
`DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` supplies the disposition
contract. Historical v006 narrows the remaining requirement to exact source
identity, durable tracking, non-impairment of the reused live path, and
specification-derived evidence. This proposal makes each condition mechanical
and fail-closed; no new or revised requirement is needed.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`

## Prior Deliberations

- `DELIB-202666766` — owner selected tracked in-root exact-byte archive
  preservation and explicitly rejected gitignored per-file archives.
- `DELIB-202667001` — structurally identical WI-5316 finding that a gitignored
  archive is not durable evidence.
- `DELIB-202667150` — archive preservation must retain live bridge semantics
  and be finalization-ready; archive presence alone is insufficient.
- Historical versions 003 and 004 of the quarantined thread — independent
  observations of the original residue's exact raw size and SHA-256.
- Historical version 006 of the quarantined thread — current unresolved
  findings requiring exact source identity and an evidence-bearing correction.

## Owner Decisions / Input

No new owner decision is required. `DELIB-202666766` already authorizes and
directs the tracked archive-preservation remedy. WI-5370 is resolved project
work, and the active project PAUTH has no per-work-item inclusion limit.

WI-5637 and WI-5827 remain unapproved, open backlog work and are not consumed
as authority or dependencies by this proposal. Their eventual disposition can
improve general compatibility but is not required for this exact repair-forward
controller.

## Specification-Derived Verification Plan

| Specification / invariant | Command or check | Execution state and required result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Resolve this new thread after every filed version; inspect the quarantined thread without mutation | New controller resolves strictly from v001; the historical chain remains unchanged and supplies no implementation authority. |
| `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` | `git cat-file -e/-s 5d58c51...`; deterministic SHA/newline reconstruction | Executed read-only: blob exists; 2,060 object bytes; 43 LF bytes; CRLF reconstruction is 2,103 bytes and SHA-256 `0859...8cdb`. Repeat after GO with identical results. |
| `GOV-WORK-TREE-HYGIENE-001` | `git check-ignore -v -- <archive-target>`; scoped status before/after | Destination is absent and non-ignored before work; after implementation, only the exact intended archive addition is attributable to this controller. |
| Exact normalized archive identity | `git hash-object -- <archive-target>` | After GO, output must equal `5d58c51bdfbd5708b4006c161d69cd5036ccd654`. |
| Non-impairment of reused live history | Raw byte count/SHA-256 and `git ls-files -s -- bridge/gtkb-wi5318-failed-verified-finalization-repair-007.md` before/after | Baseline is 12,041 bytes, SHA `406e...af3`, index blob `980db...633`; all remain unchanged. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | PAUTH operation-time check; claim status; `implementation_authorization.py begin/validate` | Active PAUTH, current-session `go_implementation` claim, independent GO, schema-v3 packet, exact one-path target coverage before mutation. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate and live `bridge_applicability_preflight.py` | `preflight_passed: true`; no missing required/advisory specifications or blockers. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Candidate and live `adr_dcl_clause_preflight.py`; report command/result table | Mandatory gate exit 0 and zero blocking gaps; report records actually executed post-change evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve every target/evidence path against `E:/GT-KB` | No out-of-root dependency or artifact. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Inspect GO/claim/start/report/verdict order and artifact linkage | Every transition follows its trigger; evidence remains additive, concrete, and reviewable. |

## Acceptance Criteria

1. This controller resolves strictly from v001 and the quarantined historical
   thread remains byte-for-byte unchanged.
2. Implementation starts only after independent GO, a matching claim, active
   operation-time PAUTH, and exact one-path schema-v3 packet.
3. The recovered target has normalized Git blob identity `5d58c51...654` and,
   when materialized as CRLF, raw size/hash 2,103 / `0859...8cdb`.
4. The reused live `bridge/...-007.md` retains its recorded size, raw hash, and
   index blob before and after the additive archive write.
5. The archive target is in-root and non-ignored; no batch, live-source removal,
   broad staging, Git operation, dispatcher activation, or unrelated mutation
   occurs.
6. A substantive implementation report carries the exact authority, identity,
   command, and observed-result evidence for independent verification.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "intuitiveness": {
    "pass": true,
    "reason": "The original bytes are preserved under their original filename in the canonical tracked terminal-verdict archive, while the current same-named live bridge history remains untouched."
  },
  "non_impairment": {
    "pass": true,
    "protected_surfaces": [
      "all files in the quarantined historical controller",
      "bridge/gtkb-wi5318-failed-verified-finalization-repair-007.md",
      "current bridge routing and append-only history",
      "Git index and unrelated worktree bytes",
      "TAFE/dispatcher activation and configuration"
    ],
    "enforcement": "Fail closed before mutation on any identity, occupancy, authorization, or path mismatch; verify the protected live predecessor before and after the one-path addition."
  }
}
```

## Risk / Rollback

The principal risks are laundering malformed history into new authority and
confusing the recovered historical blob with the reused live filename. The
strict fresh controller, explicit quarantine, exact object/hash/size proof, and
pre/post live-path checks prevent those failures.

Destination occupancy, missing object, identity mismatch, authority drift, or
a lost bridge race causes a no-op and a new bridge report; it never authorizes
substitution. Before the single additive write, rollback is a no-op. After a
successful write, the artifact is retained for independent review rather than
deleted or broadly staged; any correction uses a new governed append-only
artifact.

## Bridge Filing

This proposal is filed as v001 for the fresh strict controller. No prior bridge
version is deleted or rewritten. The governed writer may publish the required
thread state, but it must not enable, start, reconfigure, or dispatch the
deliberately disabled dispatcher/TAFE runtime.

## Recommended Commit Type

`chore` if a separately authorized terminal-finalization transaction later
permits a commit. No commit is authorized by this proposal or current PAUTH.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
