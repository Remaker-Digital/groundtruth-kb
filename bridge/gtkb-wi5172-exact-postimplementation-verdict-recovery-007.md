NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b34d5b84-5746-4eee-bd95-b6eeb3e70715
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role prime-builder via ::init gtkb pb; CF-10 serialization leadership held per DELIB-20260730-CF10-LEADER-GRANT-B34D5B84
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: implementation_report
Document: gtkb-wi5172-exact-postimplementation-verdict-recovery
Version: 007
Date: 2026-07-31 UTC
Responds to: bridge/gtkb-wi5172-exact-postimplementation-verdict-recovery-006.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION
Work Item: WI-5172

target_paths: []
implementation_scope: none
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Zero-mutation re-observation report for the WI-5172 implementation

No KB mutation: this report performs no MemBase mutation and no
`groundtruth.db` write, insert, edit, or lifecycle change. The shared MemBase
carrier is read and hashed as evidence only. `target_paths` is therefore
intentionally empty and `kb_mutation_in_scope` is `false`.

## Scope

This is the zero-mutation observation report authorized by the GO at version
006. It performs read-only re-observation of the already-implemented WI-5172
artifact-decontamination work whose predecessor chain
(`gtkb-wi5172-canonical-carrier-nonauthority-evaluator`) ended at a
non-terminal `GO` instead of a terminal verdict. No file was created,
modified, or deleted. No MemBase row, project state, dispatcher state, Git
ref, or remote was touched.

## Step 1 — Target inventory and hashes (read-only)

All seven paths declared by the predecessor's version-015 implementation
report are present. SHA-256, first 16 hex characters:

| SHA-256 (16) | Path |
| --- | --- |
| `bbefd5cd37787094` | `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py` |
| `0f34d3c7e9642642` | `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py` |
| `8d2a02e90746e2f2` | `scripts/check_artifact_decontamination.py` |
| `526a24229f15f134` | `platform_tests/scripts/test_modernization_artifact_decontamination.py` |
| `8a45f90954cd0af9` | `config/registry/sot-artifacts.toml` |
| `8a45f90954cd0af9` | `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml` |
| `27eff8785f94b5dd` | the shared MemBase carrier at the repository root (seventh declared path) |

The seventh path is the binary MemBase carrier covered by the owner-approved
shared-carrier waiver. It was **hashed and status-checked only**. This report
declares no mutation of it, requests no write to it, and `target_paths` is
empty precisely because nothing — including that carrier — is being changed.

`git status --short` against the exact seven-path set returned no output: all
seven are clean in the worktree.

The two `sot-artifacts.toml` copies hash **identically**, which is the
source-to-packaged projection parity required by
`DCL-SOT-REGISTRY-PROJECTION-PARITY-001`.

## Step 2 — Specification-derived command matrix, re-executed

| Command | Result | v015 reported |
| --- | --- | --- |
| `scripts/check_artifact_decontamination.py` | `MOD-AD-01` … `MOD-AD-12` all `PASS`; exit 0 | PASS, MOD-AD-01..12 all PASS |
| `pytest platform_tests/scripts/test_modernization_artifact_decontamination.py -q` | **24 passed**, 1 warning, 55.03s | 24 passed in 55.12s |
| `pytest groundtruth-kb/tests/test_sot_registry.py -q` | **19 passed**, 1.29s | 19 passed in 0.51s |
| `pytest groundtruth-kb/tests/test_context_manifest.py groundtruth-kb/tests/test_wi5266_resource_routing.py -q` | **2 failed, 42 passed**, 1.17s | 44 passed in 2.12s |
| `ruff check <artifact_lifecycle, checker, focused test>` | `All checks passed!` | All checks passed! |
| `ruff format --check <same>` | `4 files already formatted` | 4 files already formatted |

Every command reproduces the version-015 result **except the fourth**, which
is reported honestly below rather than smoothed over.

## Step 3 — Investigation of the one divergence

Both failures are the same test, present in two modules:
`test_packaged_v1_snapshot_matches_source_checkout_registry_inputs`.

That test asserts byte-parity between the packaged v1 registry snapshot and
the source checkout across **seven** config files, and aborts at the first
mismatch. Per-file parity was therefore evaluated individually:

| Parity | File | In WI-5172 scope? |
| --- | --- | --- |
| OK | `config/governance/canonical-terms-sync.toml` | no |
| **DIVERGED** | `config/agent-control/activity-disposition-profiles.toml` | **no** |
| OK | `config/agent-control/activity-envelope-sharding.toml` | no |
| OK | `config/agent-control/command-surface.toml` | no |
| **OK** | `config/registry/sot-artifacts.toml` | **yes — the WI-5172 target** |
| **DIVERGED** | `config/agent-control/system-interface-map.toml` | **no** |

The assertion aborts on `activity-disposition-profiles.toml`, which is the
third entry in the tuple; `sot-artifacts.toml` is the sixth and is therefore
never reached by the failing run. Evaluated directly, WI-5172's own file
passes parity, consistent with the identical hashes in Step 1.

**Conclusion:** the divergence is foreign drift in two configuration files
that are not WI-5172 targets and were not modified by the WI-5172
implementation. It does not indicate a regression in the artifact-
decontamination work under review. It is nonetheless a real live-suite
failure and is surfaced below as a separate concern rather than absorbed
into this thread.

## Step 4 — Authorization and lifecycle state (fresh reads)

- `PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION`: `active`.
- `PAUTH-…-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE`: version 2,
  `active`. Its `forbidden_operations` include `git_commit`; this report
  requests no commit, consistent with that envelope.
- `WI-5172` membership in that project: `active`.
- `WI-5172`: `open` / `backlogged` — not resolved, not superseded.
- Owner-approved shared-carrier waiver
  `DELIB-20260716-WI5172-SHARED-CARRIER-FINALIZATION-WAIVER` remains the
  governing finalization waiver.

## Step 5 — Contradictory historical evidence, recorded not resolved

The predecessor thread's version 016 begins with the status token `GO` and is
non-terminal, while later governed records describe that same path as
`VERIFIED` and the WI-5370 terminal-archive pilot records a different SHA-256
for it. This report does not attempt to adjudicate that contradiction; it
records it as the reason a fresh, independently re-observed terminal verdict
is required rather than trusting either cached description. The predecessor
files remain unmodified.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised requirement is needed;
this report supplies the executed evidence that the linked specifications
already demand.

## Specification-Derived Verification

| Requirement | Evidence in this report | Result |
| --- | --- | --- |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | `check_artifact_decontamination.py` MOD-AD-01..12; 24-test focused suite | PASS |
| `GOV-PLATFORM-SOT-REGISTRY-001` | `test_sot_registry.py` 19 passed | PASS |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | identical SHA-256 for both `sot-artifacts.toml` copies; direct per-file parity check | PASS for the WI-5172 target |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | filed as the next numbered file in this append-only chain; no prior versioned bridge file deleted, rewritten, or renumbered | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | fresh project/PAUTH/membership reads in Step 4 | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | full command matrix re-executed, results reported verbatim including the divergence | PASS with one out-of-scope failure disclosed |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | every claim derives from a read performed for this report, not from v015 narrative | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | all observed paths in-root | PASS |

## Specification Links

- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260716-WI5172-SHARED-CARRIER-FINALIZATION-WAIVER` — owner-approved finalization waiver.
- `DELIB-202666274` — artifact-decontamination project authorization history.
- `DELIB-202667712` — Envelope Protocol reactivation preserving the WI-5172 terminal-or-release dependency hold.
- `DELIB-20260730-CF10-LEADER-GRANT-B34D5B84` — CF-10 leadership under which this session operates.
- `bridge/gtkb-wi5172-exact-postimplementation-verdict-recovery-005.md` / `-006.md` — the corrected proposal and the GO authorizing this report.
- `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-015.md` / `-016.md` — the implementation report being re-observed and the non-terminal GO that stranded it.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner selection, 2026-07-31, session `b34d5b84-…`: "WI-5172 observation report" chosen as the next work item to execute.
- Implementation authority inherited from the active project-scope PAUTH cited above; no new owner decision is requested by this report.

## Separate Concern Raised — Not For This Thread

The packaged v1 registry snapshot has drifted from the source checkout for
`config/agent-control/activity-disposition-profiles.toml` and
`config/agent-control/system-interface-map.toml`, causing two live test
failures in `test_context_manifest.py` and `test_wi5266_resource_routing.py`.
Neither file is a WI-5172 target. A backlog search found no carrier squarely
covering this drift instance; the nearest candidates are `WI-5379` (Envelope
Protocol Slice G SoT reconciliation), `WI-5596` (canonicalize harness-context
registries), and `WI-5700` (registry parity self-test tooling). Assigning it
is deliberately left to the owner or Loyal Opposition rather than resolved
unilaterally here.

## Requested Loyal Opposition Action

Return `VERIFIED` if the re-observed evidence satisfies the linked
specifications for WI-5172's declared scope, noting that the sole failing
command is provably attributable to two non-WI-5172 configuration files.
Return `NO-GO` with concrete findings otherwise — in particular if Loyal
Opposition judges that a terminal verdict must wait until the foreign
packaged-registry drift is resolved.

## Recommended Commit Type

N/A — this report requests no git operation. It creates no source change and
stages nothing. `git_commit` remains in the active PAUTH's
`forbidden_operations` and is neither requested nor performed by this filing.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
