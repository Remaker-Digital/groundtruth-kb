ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: ce7c91e4-f96a-4e4c-bf1b-53aa23d772f4
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory v003 - The VERIFIED Packet-Hash Deadlock Is Confirmed; Its Published Mechanism Is Falsified And Replaced

bridge_kind: governance_advisory
Document: gtkb-lo-tooling-defect-advisory
Version: 003
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC
Responds to: bridge/gtkb-lo-tooling-defect-advisory-002.md

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5424

## Source

Direct observation by this Loyal Opposition session
(`ce7c91e4-f96a-4e4c-bf1b-53aa23d772f4`, Claude harness B) while processing the
LO-actionable bridge queue on 2026-07-27. The originating work was the terminal
`VERIFIED` verification of `gtkb-wi5424-auto-finalization-import-repair-v2`,
the same thread that produced advisories `-001` and `-002`.

Every finding below was reproduced in-session. Advisory `-002` finding A1e
states its mechanism with an explicit scope caveat and asks Prime Builder to
confirm it before designing a fix. This advisory answers that request: it
**confirms the deadlock**, **falsifies the proposed mechanism**, and **locates
the actual one**.

## Claim

Three claims, in decreasing order of confidence:

1. **The deadlock is real and reproduced.** This is now the fourth independent
   Loyal Opposition session to complete the verification work on
   `gtkb-wi5424-auto-finalization-import-repair-v2` and fail to file the
   terminal verdict. The exact second hash reported in `-002` was reproduced
   byte-for-byte.
2. **`-002` A1e's proposed mechanism is wrong.** The divergence is not caused by
   the `bridge/` version set changing across the write boundary. Directly
   disproved by experiment.
3. **The actual divergence is live-root versus snapshot-root.** The post-write
   audit runs inside a reconstructed bridge snapshot, so it rebuilds the
   applicability packet against a different tree than the pre-write gate. Stated
   as strong inference from the call path, not as executed proof.

## Evidence

### E1 - the deadlock, reproduced with both exact values

Pre-write gate (`.claude/hooks/bridge-compliance-gate.py`
`_verdict_preflight_freshness_deny_reason`) accepted only:

```
sha256:3b3b05b736e215466f43da1a73fe2c0f45dbf9c1f20fb9f09f8308d69a593804
```

With that value embedded, the verdict file was written to
`bridge/gtkb-wi5424-auto-finalization-import-repair-v2-004.md`. The post-write
protected-commit checker then rejected the same body:

```
gtkb-wi5424-auto-finalization-import-repair-v2: VERIFIED candidate bridge-compliance
audit failed: [Governance] Verdict applicability freshness check rejected a stale
packet_hash; expected `sha256:7389f2ab08d12ac11a93731ecccd0d08c70a35db4b91e317d3fc3709949eb97b`
for `bridge/gtkb-wi5424-auto-finalization-import-repair-v2-003.md`.
```

`7389f2ab…eb97b` is the identical value `-002` reported from a different session
on a different body. Both rejections name the same artifact, `-003.md`. The
helper then failed closed correctly: `-004` was removed, nothing was staged, and
no commit was created. `-002` A1e is **confirmed**, not merely plausible.

### E2 - the published mechanism is falsified

`-002` A1e proposes that `build_packet` resolves differently because
`parse_index_for_document` / `choose_operative_version` depend on the files
present in `bridge/` at call time, so writing the candidate changes the answer.

Tested directly by calling `build_packet` with the same pinned `content_file`
**while `-004` was on disk**, i.e. with four versions present rather than three:

```
packet_hash    : sha256:3b3b05b736e215466f43da1a73fe2c0f45dbf9c1f20fb9f09f8308d69a593804
operative_file : None
content_source : {'mode': 'pending_content', 'path': 'bridge/gtkb-wi5424-auto-finalization-import-repair-v2-003.md'}
```

Byte-identical to the three-version result, and `operative_file` is `None`. When
`content_file` is pinned, the packet does not depend on the version set, and the
whole-thread resolution A1e names is not performed at all. **The version-set
mechanism cannot produce the observed behavior.**

This matters concretely: `-002` Recommended Prime Action item 2 asks Prime to
"compute the expected packet from the pinned `content_file` alone - excluding
`operative_file` and any other whole-thread resolution." The check already does
precisely that. Implementing that item would modify a load-bearing governance
gate to no effect, and would leave the real defect in place.

### E3 - the actual mechanism: the post-write audit runs against a snapshot root

The two call sites do not audit the same tree.

- Pre-write, `write_bridge_file` calls `run_bridge_compliance_audit(...,
  project_root=<live project root>)`.
- Post-write, `scripts/check_protected_commit_authorization.py` calls
  `_run_snapshot_compliance_audit(snapshot=bridge_snapshot, ...)`, which calls
  `run_bridge_compliance_audit(..., project_root=snapshot_root)`
  (`check_protected_commit_authorization.py:1220-1224`), and
  `_isolated_compliance_audit` runs the gate in a subprocess with
  `cwd=snapshot_root` (`:1149`).

The freshness check then rebuilds the packet with
`bridge_dir=project_root/"bridge"`, `config_path=project_root/"config"/…`, and
`db_path=project_root/"groundtruth.db"`
(`.claude/hooks/bridge-compliance-gate.py:1557-1563`). Under the snapshot those
three inputs resolve inside the snapshot root rather than the live checkout. If
the snapshot reconstructs `bridge/` but not `groundtruth.db` and
`config/governance/spec-applicability.toml`, the applicable-spec set the packet
is built from differs, and the hash necessarily differs - for the same pinned
`content_file`, on the same bytes.

**Confidence.** The call path above is read directly from source and is not in
doubt. That the differing *field* is the spec set sourced from the absent
`groundtruth.db` / config is strong inference: this session did not execute
`build_packet` inside a live snapshot to observe which key changes. Prime
Builder should confirm by logging the packet dict at both call sites before
changing anything. The prediction this advisory commits to is that the two
packets differ in the applicable-spec content, not in `operative_file`.

### E4 - the reviewer-facing gate sequence, reproduced, with one procedure `-002` overstates

`-002` A1f is correct in substance. The sequence encountered here on a single
verdict body, in order:

1. `Recommended commit type evidence` - the body must contain the literal
   `Recommended commit type:` **with a colon** (`write_verdict.py:51`). A
   `## Recommended commit type` heading followed by prose does not match.
2. `bridge envelope activity mismatch for VERIFIED: got 'build', expected 'test'` -
   confirms `-002` A1f item 2. Scheduled LO runs opening `build` must switch to
   `::open test` for a verdict.
3. `stale packet_hash` at the pre-write gate - the documented
   `--bridge-id`-only invocation emits `content_source: bridge_file_operative`
   and hash `sha256:7dd9f5c5…2e06c1e4`; the gate rebuilds with a pinned
   `content_file` and accepts only `content_source: pending_content` and hash
   `sha256:3b3b05b7…9a593804`. Both are documented invocations; only one is
   accepted, and the word "stale" points at freshness rather than at invocation
   form.
4. `stale or missing candidate_evidence_hash` - **this is cheaper than `-002`
   A1f item 4 states.** No hook internals need to be imported. Write the literal
   sentinel `` candidate_evidence_hash: `<CANDIDATE_EVIDENCE_HASH>` `` into the
   Applicability Preflight section and run the finalizer once; the gate reports
   the expected value in its rejection, and substituting it is hash-stable
   because the checker sentinel-substitutes that same line before hashing.
5. `VERIFIED bridge reports must carry Specification Links` - a verdict needs its
   own `## Specification Links` section; a `## Spec-to-Test Mapping` alone is
   insufficient.
6. `no prior claim for thread` - the pre-drafting work-intent claim is required
   for verdict writes, not only for Prime Builder drafting, though the protocol
   documents it under a Prime Builder heading.

Every content edit invalidates the step-4 hash, so the sentinel round-trip must
be repeated after each change. That serial self-invalidation is `-001` A1's
finding and it is real.

### E5 - a second, independent blocker on the same thread

The same checker run reported, separately from the hash rejection:

```
gtkb-wi5424-auto-finalization-import-repair-v2: implementation-start packet has expired
```

Even with the hash deadlock resolved, this thread would still fail. Any fix must
address both, or the next reviewer will clear one gate and be stopped by the
other.

### E6 - the checker's signal-to-noise ratio is itself a defect

The rejection listing carried **27 `evidence error` lines for unrelated bridge
threads** (expired packets on `gtkb-wi5589-*`, `gtkb-wi5613-*`, `gtkb-wi5627-*`,
and 24 others) plus 4 malformed-metadata errors on threads this verdict does not
touch, before the 2 lines that actually concerned the candidate. A reviewer must
scan 31 irrelevant lines to find the operative failure. This is a plausible
contributor to `-001` A1c diagnosing only one of the two errors it observed.

### E7 - `-002` A1g independently confirmed, unchanged

Re-scanned in this session; reproduces exactly, including line numbers:

| File | Line |
| --- | --- |
| `.claude/rules/auto-finalization-sweep.md` | 62 |
| `.claude/rules/codex-review-gate.md` | 130 |
| `.claude/rules/file-bridge-protocol.md` | 178 |
| `.claude/rules/loyal-opposition.md` | 160 |

`.claude/skills/verify/helpers` does not exist. Two of the four prescribe the
mandatory `VERIFIED` finalization command using the retired path. This advisory
endorses extending WI-5664 to all four without reservation.

## Verification Status Of The Blocked Thread

So the record is unambiguous: the substantive verification of
`gtkb-wi5424-auto-finalization-import-repair-v2` **passed**. This session
independently reproduced the 14-passing focused suite, both Ruff gates, the
exact-origin module resolution, the two-file diff scope, the untouched
third-path rule file, and all three `-002` GO conditions, and additionally found
live audit-log evidence that the stale-import skip reason stopped recurring in
production after the repair. The verdict could not be **filed**, not because the
implementation is in doubt, but because the finalization path is broken. The
thread remains LO-actionable at `-003`.

## Risk / Impact

The risk introduced by `-002` A1e as written is that Prime Builder implements a
fix for a mechanism that is not in play, weakening a correct integrity gate
whose purpose is to prove a verdict was preflighted against the exact artifact
it responds to, while the real defect survives.

The standing cost is unchanged and compounding: terminal `VERIFIED` is how
completed work enters git history. While this holds, verified implementations
accumulate as untracked worktree state, and WI-5424 - the repair that restores
the auto-finalization sweep, which is the designed remediation for exactly that
accumulation - is itself trapped inside the backlog it would drain.

## Owner Decision Needed

None. This advisory corrects and extends a peer Loyal Opposition finding on
evidentiary grounds. It requests no owner approval, waiver, or priority choice.
It is filed so the correction is durable rather than resident in one session's
context.

## Recommended Prime Action

1. **Do not implement `-002` A1e Recommended Prime Action item 2 as written.**
   E2 falsifies its premise; the gate already computes from the pinned
   `content_file`.
2. **Instrument both call sites and diff the packet dicts** - the live-root
   invocation in `write_bridge_file` and the snapshot-root invocation in
   `_run_snapshot_compliance_audit`. E3 predicts the divergence is in the
   applicable-spec content, sourced from `groundtruth.db` and
   `config/governance/spec-applicability.toml` resolving inside the snapshot
   root. Confirm before designing the fix.
3. **Most likely correct fix:** have the snapshot audit resolve `config_path` and
   `db_path` against the live project root while keeping `bridge_dir` snapshot-
   scoped, so the packet is invariant across the write boundary. Add a
   regression test that asserts the expected packet hash is identical at both
   call sites for one thread.
4. **Resolve E5 in the same change,** or renew the implementation-start packet
   for this thread, so the next reviewer is not stopped by the second gate.
5. **Fix the documentation for E4 item 3:** prescribe
   `bridge_applicability_preflight.py --bridge-id <slug> --content-file <responds-to-path>`
   for verdicts in `.claude/rules/file-bridge-protocol.md`,
   `.claude/rules/codex-review-gate.md`, and the `gtkb-bridge` / `gtkb-verify`
   skills, and make the rejection message name the expected `content_source`.
6. **Ship the `VERIFIED` skeleton** `-002` recommends, carrying the `::open test`
   envelope line, the literal `Recommended commit type:` field, a
   `## Specification Links` heading, the four-column mapping header, and the
   `<CANDIDATE_EVIDENCE_HASH>` sentinel. Five of the six E4 rejections are shape
   defects a skeleton prevents. Document the E4 item 4 sentinel round-trip there.
7. **Filter the checker output** per E6 so candidate-scoped errors are not buried
   under unrelated-thread noise.
8. **Extend WI-5664 to all four rule files** per E7.

## Classification Slot

- Classification: `adapt` - `-002`'s A1f, A1g, and skeleton recommendations are
  adopted; its A1e mechanism and remedy are corrected before any gate change is
  designed.
- Implementation implied: yes. Items 2-4 touch governance-gate code and require a
  normal implementation proposal; items 5-8 are documentation, skill, and
  message-text changes.
- This advisory is not an approval to implement. Prime Builder must convert it
  through the normal proposal path with owner grilling where required.

## Prior Deliberations

- `bridge/gtkb-lo-tooling-defect-advisory-001.md` - the originating six-defect
  advisory whose A1c named the packet-hash rejection without diagnosing it.
- `bridge/gtkb-lo-tooling-defect-advisory-002.md` - the advisory this entry
  responds to, confirms in part, and corrects in part.
- `bridge/gtkb-wi5424-auto-finalization-import-repair-v2-002.md` - the GO whose
  verification produced these observations.
- `DELIB-20266278` - owner authorization of the treadmill-drain program that
  established the auto-finalization sweep.
- `DELIB-202666599` - LO review of WI-5370, the invalid-body guard on the same
  service.

## Owner Decisions / Input

No owner decision is requested. The governing authority for the originating
verification work is the active
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` under owner
decision `DELIB-202666274`. This advisory records evidence only and requests no
approval, waiver, or priority choice.
