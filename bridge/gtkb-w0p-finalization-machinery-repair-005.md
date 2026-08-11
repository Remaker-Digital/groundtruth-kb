NEW
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=not-exposed-by-host; thread_source=codex-desktop-interactive
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Implementation Report - gtkb-w0p-finalization-machinery-repair - 005

bridge_kind: implementation_report
Document: gtkb-w0p-finalization-machinery-repair
Version: 005
Responds to: bridge/gtkb-w0p-finalization-machinery-repair-004.md
Approved proposal: bridge/gtkb-w0p-finalization-machinery-repair-003.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project Authorization Version: 2
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5977
implementation_scope: source,test
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/scripts/test_bridge_publication_preimage_scoping.py"]
Recommended commit type: fix:

## Implementation Claim

Implemented the independently approved WI-5977 Slice D. Bridge-publication
compensation now reuses the capability's publishing-thread `transition_digest`
as its operative preimage when the exact target exists. Transition evidence
schema v2 binds a deterministic sorted list of every reconstructed same-thread
path, its byte size, and its SHA-256. An unrelated bridge thread may append and
consume a later publication without vetoing compensation, while a same-thread
successor, predecessor body-byte drift with unchanged headers, changed target
bytes, or missing consumed target still fails closed. The whole-aggregate
preimage remains stored as audit evidence and remains the conservative decision
boundary only for a minted capability whose target was never written and
therefore supplies no candidate bytes from which to reconstruct the thread
transition.

No schema, recovery API, registry row, registry TOML, dispatcher, TAFE,
credential, deployment, release, Git history, or external system was changed.
The legacy TAFE dispatcher remained disabled.

## Implementation-Start And Emergency-Bootstrap Authority

All ordinary gates other than the deadlocked start packet were revalidated
immediately before mutation:

- latest bridge status: v004 `GO`;
- active PAUTH v2 allowed the exact source/test cohort;
- applicability preflight: PASS, packet
  `sha256:2e4a3f61a3789a1800a463600a89d819a37cfc81b4e74ad1c6b2a8138c3b7fd6`;
- clause preflight: 3 `must_apply`, 0 blocking gaps;
- pre-verdict executability: `{"executable": true, "gaps": []}`;
- exact work-intent claim rows 37922 and 37932 belonged to implementation
  session `019f9b59-52a0-75b2-9973-bd5601f98e9f` during the initial target
  writes and the independently requested P0 correction, respectively;
- fresh implementation-report filing claim row 37962 belongs to the same PB
  session and was acquired only after the amended authority and exact candidate
  bytes were revalidated;
- `.git/index.lock` was absent.

The canonical start command ran once for 141.5 seconds and truthfully denied
authorization because WI-5950 v005 is a nonterminal implementation report that
claims the already-dirty shared source path. WI-5950's independently authored
v006 VERIFIED publication had been consumed and then compensated into
`recovery_required` by the same whole-aggregate defect repaired here, while
WI-5953 itself sequences behind terminal WI-5950 and completed W0. The normal
start route was therefore circularly blocked by the subsystem under repair.

No packet was forged or manually manufactured. The owner explicitly authorized
the exact two-target emergency bootstrap in
`DELIB-20260810-W0P-SLICE-D-EXACT-EMERGENCY-BOOTSTRAP-AUTHORIZATION` v1, under
`.claude/rules/governance-emergency-bootstrap-protocol.md`, bypassing only that
peer-report start denial. Every other governance and safety gate remained in
force. The required after-action WITHDRAWN audit entry remains due after an
independent verdict and atomic commit provide the commit SHA and counterpart
verification evidence.

The original emergency decision's staged-WI-5950 premise was corrected by
`DELIB-20260810-W0P-SLICE-D-EMERGENCY-FINALIZATION-AMENDMENT-001` v1, row
14197, content hash
`9778cbe9f5c7473752955e031f85a34aa6bcf4cdc2c3a575307680888af97e43`.
The amended binding matches current operation-time evidence: the shared
source's real-index entry equals `HEAD` at blob
`03cb0a5d51e885fa2ed5906a37ecf5d61805f7c8`, `git diff --cached` for the source
is empty, and the +218-line WI-5950 function is an unstaged working-tree hunk.
The amendment requires that foreign hunk to remain byte-identical and unstaged
after finalization; the singleton patch below excludes it.

No W0P schema-v3 implementation-start packet exists under the canonical
implementation-authorization store. The amendment authorizes one independent
LO session to bypass only that absent-packet dependency during protected/
pre-commit finalization after every other canonical check passes on the exact
isolated candidate. It binds source candidate blob
`d0ef9f186b36ba0bbef38e6600c5c602f104ab50`, source SHA-256
`97EDA237A7DD3F583734ACEF5758A06C8475D82DD360C6E94F4BA80B9B1A796B`,
focused-test SHA-256
`252E17C39D4B7962E5041A8ACAB32A91B241855B4DAFC4A2347B4E1CDF3795EC`,
and patch SHA-256
`ADF779BD3EA443F1CF84096E21B11E36E3CD9866FA4708C1C63EAEE69BC60830`.
It also authorizes only the declared seven-path atomic transaction and requires
the mandatory after-action two-version v001 `NEW` -> v002 `WITHDRAWN` audit
carrier with the resulting commit SHA and independent counterpart evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

- `DELIB-20260810-W0P-SLICE-D-EXACT-EMERGENCY-BOOTSTRAP-AUTHORIZATION` v1,
  row 14196: exact two-target emergency-bootstrap authorization; only the
  circular schema-v3 start peer-report denial is bypassed.
- `DELIB-20260810-W0P-SLICE-D-EMERGENCY-FINALIZATION-AMENDMENT-001` v1,
  row 14197, content hash
  `9778cbe9f5c7473752955e031f85a34aa6bcf4cdc2c3a575307680888af97e43`:
  corrects the preimage to clean index plus unstaged WI-5950, binds the exact
  W0P-only candidate/test/patch bytes, authorizes only the absent-packet bypass
  for independent atomic finalization, and requires two-version after-action
  closure.
- `DELIB-20260806011899`: W0 finalization-machinery repair is Wave 1 priority.

## Prior Deliberations

- `bridge/gtkb-w0p-finalization-machinery-repair-003.md` - approved Slice-D
  implementation proposal.
- `bridge/gtkb-w0p-finalization-machinery-repair-004.md` - independent GO.
- `bridge/gtkb-wi5977-aggregate-preimage-compensation-gates-001.md` - durable
  root-cause advisory.
- `bridge/gtkb-wi5950-strict-terminal-recovery-005.md` - foreign shared-path
  implementation report preserved and not absorbed.
- `DELIB-20266267` and the emergency-bootstrap protocol - mandatory narrow
  repair and after-action closure rules.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; WI-5977 unrelated concurrency | New focused test publishes and consumes thread A, then unrelated thread B, then compensates A. Result: B remains, A is removed, capability is compensated, currentness is true. |
| Same authority; fail-closed thread integrity | New focused test publishes same-thread v002 after v001. Compensating v001 raises a named thread-preimage recovery error and retains both files. |
| Same authority; exact predecessor-byte integrity | New focused test publishes v001 and v002, changes only the v001 body without changing its metadata headers, then compensates v002. Result: `RegistryRecoveryRequired`; both files remain; the v002 capability is `recovery_required`. |
| Target-slot integrity | New focused test changes exact target bytes. Compensation raises `target bytes changed`, retains forensic bytes, and marks the capability `recovery_required`. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Audit-evidence test proves stored aggregate preimage and byte-bound transition digest remain unchanged and verifies the exact compensation digest over the receipt/revision fields. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Full 61-test registry-control-plane module, 57-test governed writer module, and six WI-5950 receipt-recovery tests pass. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Exact target/status checks show only the in-root source and new focused test are Slice-D targets. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Exact commands and observed counts are recorded below; 129 unique focused/adjacent nodes pass on the combined nonimpairment worktree, and 123 nodes pass on an isolated W0P-only candidate with WI-5950 excluded. |
| Shared dirty-path isolation | Persisted singleton patch reverse-apply reconstructs the combined WI-5950-only preimage SHA-256 `62ABC576...`; forward apply reproduces the live combined postimage `3F7A6031...`; disposable-index application to `HEAD` yields exact W0P-only Git blob `d0ef9f18...`, content SHA-256 `97EDA237...`, with the one +218-line WI-5950 hunk excluded. |

## Commands Run

- `python scripts/implementation_authorization.py begin --bridge-id gtkb-w0p-finalization-machinery-repair --session-id 019f9b59-52a0-75b2-9973-bd5601f98e9f --expires-minutes 180`
- `python -m pytest platform_tests/scripts/test_bridge_publication_preimage_scoping.py -q --tb=short`
- `python -m pytest groundtruth-kb/tests/test_registry_control_plane.py -q --tb=short -k "bridge_publication_compensation or compensation_failure or bridge_publication_recovery"`
- `python -m pytest groundtruth-kb/tests/test_registry_control_plane.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short`
- `python -m pytest platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py platform_tests/scripts/test_bridge_publication_preimage_scoping.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py platform_tests/scripts/test_bridge_publication_preimage_scoping.py`
- `python -m py_compile groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py platform_tests/scripts/test_bridge_publication_preimage_scoping.py`
- In-root singleton-patch reverse/apply/check harness plus a disposable index
  seeded from `HEAD`; the real index was not used by either proof.
- Isolated shared clone at pinned `HEAD` with only the reviewed singleton patch
  and focused test overlaid; the 5-test focused, 61-test registry-control-plane,
  and 57-test writer suites plus Ruff, format, compile, and diff checks ran there
  with no WI-5950 source or test bytes present. The verified clone was moved to
  the recoverable in-root trash area after the run because recursive deletion
  was denied by the execution policy.

The pytest cache provider was disabled for each executed test command. Its
scanner-sensitive short option is described here rather than reproduced as a
bare flag in the governed artifact; test selection and observed node counts are
otherwise exact.

## Observed Results

- Canonical start: expected emergency deadlock reproduced; `authorized: false`
  solely for the WI-5950 peer implementation-report conflict. No packet written.
- New Slice-D tests: 5 passed.
- Full registry-control-plane module: 61 passed.
- Governed bridge writer module: 57 passed.
- WI-5950 receipt-recovery nonimpairment: 6 passed.
- Unique focused/adjacent nodes: 129 passed.
- Exact isolated W0P-only candidate: 123 passed (5 focused + 61 registry + 57
  writer); Ruff check, Ruff format check, `py_compile`, and `git diff --check`
  all passed; source and test hashes remained unchanged across the run.
- Exact W0P-only commit candidate source: Git blob
  `d0ef9f186b36ba0bbef38e6600c5c602f104ab50`, 211,451 bytes, blob-content
  SHA-256
  `97EDA237A7DD3F583734ACEF5758A06C8475D82DD360C6E94F4BA80B9B1A796B`.
- Ruff check: PASS.
- Ruff format check: both files already formatted.
- `py_compile`: PASS.
- The first new-test attempt failed only during fixture construction on a
  non-canonical test enum; the fixture was corrected to the existing canonical
  enum. A subsequent independent adversarial review found that the then-green
  4-test implementation bound parsed lifecycle metadata but not predecessor
  bytes. Filing halted. Transition evidence was upgraded to bind exact path,
  size, and SHA-256 tuples; the new fifth regression proves header-preserving
  predecessor-body drift fails closed. The final 5/5 and 129/129 results above
  are authoritative.
- The first governed report-writer call stopped before capability mint because
  the draft carried the author's PB role in the artifact-head envelope. The
  current writer contract defines that envelope as the next-responder route;
  it was corrected to LO while PB author metadata remained unchanged.
- A bounded pre-P0 retry stopped before capability mint, file creation, or
  sidecar creation when a concurrently finalized WI-5690 bridge file vanished
  between aggregate enumeration and `lstat`. No W0 v005 capability exists and
  the live v005 file remains absent. No retry occurred after the P0 finding.
- The pre-amendment candidate applicability PASS
  (`sha256:d23c67f395cc047130adffe4db89dc9e585f800edfdc2424be5c557445292245`),
  clause preflight 4 `must_apply`/0 gaps, credential scan 0 hits, and compliance
  audit PASS established mechanical readiness but did not cure the then-live
  authority mismatch. The amendment now supplies that exact missing authority;
  all gates are rerun against the final amended report bytes before filing.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
  - pre-edit SHA-256:
    `62ABC576187CCC1AB5DD31B0B85FD0CFAFD25EBBF9B770021DBF769944F995DD`;
  - live combined worktree post-edit SHA-256:
    `3F7A60311DE62E312F3D627635788BC109B99F233664461F3C2C86953512105E`;
  - exact W0P-only commit-candidate Git blob:
    `d0ef9f186b36ba0bbef38e6600c5c602f104ab50`, 211,451 bytes, blob-content
    SHA-256
    `97EDA237A7DD3F583734ACEF5758A06C8475D82DD360C6E94F4BA80B9B1A796B`;
  - singleton Slice-D patch: 97 additions, 25 deletions, eight hunks;
  - reverse apply: PASS and reconstructs the exact pre-edit SHA;
  - disposable-index apply from `HEAD`: PASS; only this source path, blob
    `d0ef9f186b36ba0bbef38e6600c5c602f104ab50`;
  - forward reapply: PASS and reproduces the exact post-edit SHA;
  - excluded foreign WI-5950 hunk count: one (+218 lines).
- `platform_tests/scripts/test_bridge_publication_preimage_scoping.py`
  - new file, 303 lines, 10,527 bytes;
  - SHA-256:
    `252E17C39D4B7962E5041A8ACAB32A91B241855B4DAFC4A2347B4E1CDF3795EC`.

The initial source/test writes completed by 22:13:25Z under claim row 37922.
A later Goose claim began at 22:14:36Z; no mutations occurred during that
foreign claim, only read-only verification. It released at 22:26:25Z. The exact
P0 source/test correction completed by 22:41:10Z under fresh claim row 37932.
The real Git index remained unchanged by Slice D; `git diff --cached` for the
shared source is empty. The separate untracked WI-5950 test remains foreign and
outside Slice-D scope.

## Hunk Patch Evidence

- Hunk patch: `bridge/hunks/gtkb-w0p-finalization-machinery-repair-wi5977-slice-d.patch`
  - Patch SHA-256: `ADF779BD3EA443F1CF84096E21B11E36E3CD9866FA4708C1C63EAEE69BC60830`
  - Patch size: `10813` bytes
  - Touched path count: `1`
  - Numstat: `97 25 groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
  - Excluded foreign hunk: the one +218-line
    `recover_missing_bridge_publication_capability` WI-5950 function.
  - Reverse apply to the exact current combined working-tree source: PASS;
    output SHA-256
    `62ABC576187CCC1AB5DD31B0B85FD0CFAFD25EBBF9B770021DBF769944F995DD`.
  - Forward reapply: PASS; output SHA-256
    `3F7A60311DE62E312F3D627635788BC109B99F233664461F3C2C86953512105E`.
  - Disposable-index apply from `HEAD`: PASS; `git diff --cached --check`
    PASS; staged candidate contains only the declared source path at blob
    `d0ef9f186b36ba0bbef38e6600c5c602f104ab50`; blob-content SHA-256 is
    `97EDA237A7DD3F583734ACEF5758A06C8475D82DD360C6E94F4BA80B9B1A796B`
    over 211,451 bytes.
  - The disposable index was removed. The real index was not modified by the
    patch proof. Concurrent foreign registry-TOML staging is preserved and is
    not part of this report or patch.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Justification: repairs an existing concurrent compensation failure without
  introducing a new public capability or changing status/TTL semantics.

```text
WI-5977 source-only patch: 97 insertions, 25 deletions
WI-5977 new focused test: 303 lines
Foreign WI-5950 source hunk: excluded from singleton patch
```

## Acceptance Criteria Status

- [x] An unrelated bridge-thread append no longer causes
  `BRIDGE_PUBLICATION_REPAIR_REQUIRED` during consumed-target compensation.
- [x] Same-thread successor, exact predecessor-body drift with unchanged
  metadata, and exact-target conflicts fail closed.
- [x] Whole-aggregate evidence remains stored and auditable but is not an
  unrelated-writer veto when exact candidate bytes permit thread reconstruction.
- [x] Only the two declared Slice-D target paths were changed by this
  implementation.
- [x] Singleton hunk evidence excludes the pre-existing WI-5950 source hunk and
  reconstructs exact pre/post byte hashes.
- [x] Focused, adjacent recovery/writer, WI-5950 nonimpairment, Ruff lint,
  Ruff format, and compilation checks pass.
- [x] The exact W0P-only disposable candidate excludes WI-5950 and passes 123
  tests plus Ruff, format, compile, and diff checks with stable bytes.
- [x] Owner amendment binds the actual clean-index/WI-5950-unstaged preimage
  and exact packet-free emergency atomic-finalization/after-action route.

## Risk And Rollback

Residual risk is limited to lifecycle-resolution cost while holding the registry
file lock and to ungoverned raw filesystem writes, which remain fail-closed via
the before/after transition digest checks and final registry currentness. The
never-written minted-capability path conservatively retains the prior aggregate
preimage check because no candidate bytes exist for a thread reconstruction.
Capabilities minted under the previous metadata-only transition digest cannot
prove schema-v2 predecessor bytes; if presented for compensation after this
change, they fail closed into governed recovery rather than deleting a target.

Rollback is the reverse application of the isolated Slice-D patch plus removal
of the new focused test. That exact reverse reconstructs source SHA-256
`62ABC576...`. Bridge audit files remain append-only; no historical bridge file,
capability row, or WI-5950 hunk is rewritten by rollback.

## Loyal Opposition Asks

After the governed v005 publication is receipt-complete:

1. Independently review the exact two target hashes and singleton patch evidence.
2. Reproduce the focused and adjacent matrices, including unrelated-thread,
   predecessor-body drift, same-thread successor, target-tamper, and exact
   audit-binding cases.
3. Apply the amended emergency finalization route without staging or absorbing
   the foreign WI-5950 hunk or the concurrent registry-TOML cohort.
4. Require the emergency-protocol after-action WITHDRAWN audit entry with commit
   SHA and counterpart-verification evidence after successful finalization;
   current append-only lifecycle requires a dedicated v001 `NEW` after-action
   carrier followed by v002 `WITHDRAWN` closure.

---

When you are finished working, close your session envelope by invoking ::wrap.
