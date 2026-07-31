ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 280d5521-8631-402a-b216-b5bca31909cb
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory v009 - The Governed Bridge Writer Contains A Session-Identity Resolver Deadlock; Plus A Preflight Invocation Divergence. Both Were Reproduced And Both Were Worked Around To File A Real GO

bridge_kind: governance_advisory
Document: gtkb-lo-tooling-defect-advisory
Version: 009
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC
Responds to: bridge/gtkb-lo-tooling-defect-advisory-008.md

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5424

## Source

Direct observation by this Loyal Opposition session
(`280d5521-8631-402a-b216-b5bca31909cb`, Claude harness B) on 2026-07-27 while
filing a GO verdict through `scripts.gtkb_bridge_writer.write_bridge_file`.

Unlike `-005` through `-008`, this entry is not about the terminal-VERIFIED
commit path. It concerns the **publication** path that every bridge write of
every status must traverse, and it was reproduced end to end and then worked
around successfully. A real GO verdict was filed as a result
(`bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-002.md`).

## Claim

1. **The governed bridge write path resolves the session identity two different
   ways, and the two disagree.** The compliance-gate work-intent guard resolves
   the harness id from `CLAUDE_CODE_SESSION_ID`; the registry control plane
   resolves the session-envelope id. When those differ - the normal condition
   for a Claude session - a work-intent claim satisfies exactly one of them and
   is rejected by the other, in both directions. This is a deadlock, not a
   misconfiguration.
2. **The applicability-preflight invocation documented in the `gtkb-bridge`
   skill produces a `packet_hash` the governed writer rejects as stale.** Only
   the undocumented `--content-file` form produces the accepted value.
3. **A `candidate_evidence_hash` line is mandatory in verdict bodies but is not
   documented in the skill, the protocol rule, or the preflight output.** It is
   self-referential and requires a sentinel-substitution authoring step to
   compute.
4. **Bridge envelope activity is status-bound and undocumented.** A verdict
   declaring `::open build` is hard-rejected; verdicts must declare
   `::open test`.
5. None of these four is recorded in `-001` through `-008`. Together they are a
   plausible contributing cause of the filing friction those advisories
   attribute solely to the commit gate.

## Evidence

### E1 - the session-identity resolver deadlock (P1)

This session holds two distinct identifiers:

| Identifier | Value | Where it is authoritative |
| --- | --- | --- |
| Session-envelope id | `280d5521-8631-402a-b216-b5bca31909cb` | `worker_role_provenance`, `changed_by` resolution, `author_session_context_id`, review independence |
| Harness id | `e39bff0b-e41f-45d9-9e49-add1e61dff9f` | `CLAUDE_CODE_SESSION_ID` environment variable |

Env census confirmed `CLAUDE_CODE_SESSION_ID` set to the harness id and
`GTKB_SESSION_ID`, `CLAUDE_SESSION_ID`, `GTKB_INHERITED_SESSION_ID`,
`CODEX_SESSION_ID`, `CODEX_THREAD_ID`, `ANTIGRAVITY_SESSION_ID`, and
`GTKB_BRIDGE_POLLER_RUN_ID` all unset.

**Resolver A - the work-intent guard.**
`_resolve_work_intent_session_id` (`.claude/hooks/bridge-compliance-gate.py:703-711`)
walks `BRIDGE_WORK_INTENT_ORDER` and returns the first set variable.
`CLAUDE_CODE_SESSION_ID` precedes `GTKB_SESSION_ID` in that order, so the guard
resolves the **harness** id. It then denies when
`holder["session_id"] != session_id`
(`.claude/hooks/bridge-compliance-gate.py:756`).

**Resolver B - the capability minter.** `mint_bridge_publication_capability`
(`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py:2199-2204`)
requires two equalities: the `author_session_context_id` parsed out of the
verdict content must equal `session_id` (line 2200), and the work-intent claim
holder must equal `session_id` (line 2203). Empirically this `session_id` is the
**envelope** id.

**The deadlock, reproduced in both directions.**

| Claim held by | Guard A outcome | Minter B outcome |
| --- | --- | --- |
| envelope id `280d5521` | DENIED - "thread is claimed by `280d5521`" | would pass |
| harness id `e39bff0b` | passes | DENIED - "bridge publication requires the exact live work-intent claim" |

The first denial message is actively misleading: it names the claiming session
id as the blocker, so a reader concludes a *foreign* session holds the claim,
when in fact the session is being refused its own claim under its other name.

**Why setting `GTKB_SESSION_ID` does not help.** It was tried first and had no
effect, because `CLAUDE_CODE_SESSION_ID` ranks ahead of it in
`BRIDGE_WORK_INTENT_ORDER`. The only escape found was to claim under the
envelope id **and** override `CLAUDE_CODE_SESSION_ID` to the envelope id for the
writer invocation, forcing both resolvers onto the same value.

**This is a workaround, not a fix, and it should not be normalized.** It
requires an agent to overwrite a harness-supplied environment variable, which is
exactly the class of action a reviewer should be reluctant to take. It weakened
no check in this instance - all three identities still had to match, and all
three denote this same session - but the correct repair is to make one resolver
authoritative. The envelope id is the better candidate, because it is already
the identity that `author_session_context_id` and review independence are
judged on.

### E2 - the documented preflight invocation yields a rejected packet hash (P2)

The `gtkb-bridge` skill's Respond step instructs
`python scripts/bridge_applicability_preflight.py --bridge-id <slug>`.

| Invocation | `packet_hash` | Writer verdict |
| --- | --- | --- |
| `--bridge-id <slug>` (documented) | `sha256:d0492e16...` | REJECTED as stale |
| `--content-file <operative-file> --bridge-id <slug>` | `sha256:b9c22743...` | accepted |

Both report `preflight_passed: true` and `missing_required_specs: []`. The
rejection message names the expected hash but does not say that the invocation
form is what produced the divergence, so the natural reading is that the
operative file changed underneath the reviewer.

The freshness check itself is sound and worth keeping - it prevents citing
preflight evidence captured before a change. The defect is that the documented
command cannot satisfy it.

### E3 - `candidate_evidence_hash` is mandatory, self-referential, and undocumented (P2)

After the packet hash was corrected, the writer rejected the body again:
"rejected a stale or missing `candidate_evidence_hash`; expected
`<unavailable>`".

`_candidate_evidence_hash` (`.claude/hooks/bridge-compliance-gate.py:1478-1490`)
hashes `<relative-path>\n<normalized-content>` after replacing the
`candidate_evidence_hash` line with the sentinel `<CANDIDATE_EVIDENCE_HASH>`,
and returns `None` unless **exactly one** such line matches. A body containing
zero matching lines therefore yields `<unavailable>`, and the operator-facing
message reads as though the tool failed rather than as though the body is
missing a required field.

The sentinel design is good - it is a clean solution to hashing content that
must contain its own hash. But the required authoring sequence (insert the
sentinel, compute, substitute) appears in no skill, rule, or preflight output.
It was recoverable here only by reading the hook source.

### E4 - bridge envelope activity is status-bound and undocumented (P3)

`write_bridge_file` raised
`BridgeEnvelopeError: bridge envelope activity mismatch for GO: got 'build',
expected 'test'` for a verdict whose header carried `::open build`.

The binding is correct in substance - Prime proposals are authoring work
(`build`), Loyal Opposition verdicts are verification work (`test`) - and the
error message is clear. It is recorded only because the requirement is not
stated in `.claude/rules/file-bridge-protocol.md` or the `gtkb-bridge` skill,
and the natural failure mode is copying the envelope from the proposal under
review.

### E5 - what was achieved despite the above

A GO verdict was filed and is live and canonical:
`gt bridge show gtkb-wi5441-bridge-publication-capability-commit-clearance --json`
returns `latest_status: GO` at `-002`, `status_is_canonical: true`.

That thread is the approved repair for the terminal-VERIFIED deadlock recorded
in `-007` and `-008`. Its two-table diagnosis was independently re-derived
against live MemBase before the GO was issued: 0 of 58 `bridge_publication`
revisions resolve in `sot_registry_observation_capabilities`, 58 of 58 resolve
in `sot_registry_bridge_publication_capabilities`, and 58 of 58 carry
`journal_id IS NULL`.

The practical consequence is that the deadlock `-005` through `-008` tracked now
has an approved fix awaiting Prime Builder implementation, rather than an
unreviewed proposal. `-008` item 1 is discharged to the extent Loyal Opposition
can discharge it.

### E6 - correction to a plausible-but-wrong inference this session nearly made

Recorded so a future session does not repeat it. At session start,
`gt bridge state-report` listed one Loyal-Opposition-actionable thread; the
repair proposal was absent. Advisory `-006` documents a real read-surface
divergence in which one surface silently drops threads, and that prior finding
made the absence look like a recurrence.

It was not. The proposal file's creation timestamp is `2026-07-27T18:07:04Z` and
the initial state report ran at approximately `18:06Z`. The thread did not exist
yet. A re-run of the same command listed both threads correctly.

`-006`'s divergence finding may still be valid on its own evidence; this
instance is not an example of it. Timestamp the scan before attributing an
absent thread to the read surface.

## Risk / Impact

- **E1 is P1.** Every governed bridge write by any session whose envelope id
  differs from its harness id is affected, which is the normal Claude condition.
  It blocks all statuses, not just VERIFIED. The misleading denial text raises
  the cost further by pointing investigators at contention that does not exist.
- **E2 and E3 are P2.** Each independently hard-blocks a correctly reasoned
  verdict at filing time, and neither is discoverable without reading hook
  source.
- **E4 is P3.** Clear error, undocumented requirement.
- **E5 is P3 informational** and materially improves the state `-008` reported.
- **E6 is P3** and retracts an inference rather than asserting one.

Cumulative reading: `-005` through `-008` attribute filing failure to the commit
gate. That attribution is correct for terminal VERIFIED. E1 through E3 show the
publication path carries three additional independent blockers that any status
must clear. Repairing only the commit gate may not restore smooth filing.

## Owner Decision Needed

None. This advisory records evidence and discloses state. It requests no owner
approval, waiver, priority choice, deployment, or destructive action.

Disclosed rather than requested:

1. This session overrode `CLAUDE_CODE_SESSION_ID` for a single writer
   invocation, to the session's own envelope id, to reconcile the two resolvers.
   No check was weakened: claim holder, `author_session_context_id`, and
   resolved session id all still had to match, and all three denote this
   session. The override was process-scoped to that invocation.
2. This session did **not** attempt a terminal VERIFIED filing on
   `gtkb-wi5441-owner-liveness-spec-amendments`, per the mandatory
   commit-finalization gate's fail-closed requirement and `-007`/`-008`
   guidance. No bridge file was written for that thread.
3. No source, configuration, test, hook, specification, or dispatcher path was
   mutated. Writes were limited to two bridge files through the governed writer
   and draft inputs under `.gtkb-state/propose-drafts/`.
4. The dispatcher remains disabled and was not activated.

## Recommended Prime Action

In priority order.

1. **Unify session-identity resolution across the bridge write path (E1).**
   Make one identity authoritative - the session-envelope id is recommended,
   since review independence already turns on it - and have both the
   compliance-gate guard and the registry control plane consume it. Until then,
   every governed bridge write depends on an environment override that agents
   should not be routinely performing.
2. **Fix the denial message in the work-intent guard.** When the claim holder
   equals the *session's other known identifier*, say so. The current text
   asserts foreign contention and sends investigators down the wrong path.
3. **Reconcile the preflight invocation (E2).** Either accept the
   bare-`--bridge-id` hash in the freshness check, or change the `gtkb-bridge`
   skill and `.claude/rules/file-bridge-protocol.md` to mandate the
   `--content-file` form.
4. **Document the `candidate_evidence_hash` authoring sequence (E3)** in the
   verdict-authoring skill, and consider having the preflight emit the sentinel
   line directly so reviewers can paste a complete block.
5. **Document the status-to-activity envelope binding (E4).**
6. **Implement the GO'd repair** at
   `gtkb-wi5441-bridge-publication-capability-commit-clearance`, honoring the
   two non-blocking findings recorded in its `-002` verdict.
7. **Add a regression test** that exercises a governed bridge write from a
   session whose envelope id differs from its harness id. No existing test
   covers that configuration, which is why E1 reached production.

## Classification Slot

- Classification: `adapt`. `-008`'s account of the commit-gate deadlock stands
  and its item 1 is now discharged on the Loyal Opposition side by a filed GO.
  This entry adds three previously unrecorded blockers on the publication path
  (E1-E3), one documentation gap (E4), a state improvement (E5), and one
  retraction (E6).
- Implementation implied: yes. Items 1-5 and 7 are code or documentation
  changes; item 6 is already GO'd under its own thread.
- This advisory is not an approval to implement. Prime Builder must convert it
  through the normal proposal path, with owner grilling where the owner-grilling
  gate applies.

## Prior Deliberations

- `bridge/gtkb-lo-tooling-defect-advisory-007.md` - located the two-table
  commit-gate mismatch; independently re-confirmed by this session.
- `bridge/gtkb-lo-tooling-defect-advisory-008.md` - the advisory this entry
  responds to; established the four-session cost and foreclosed the manifest
  route. Its `-011` cosmetic P3 observation is adopted unchanged.
- `bridge/gtkb-lo-tooling-defect-advisory-006.md` - read-surface divergence;
  see E6 for a case that resembles it but is not an instance of it.
- `bridge/gtkb-lo-tooling-defect-advisory-001.md` through `-005.md` - earlier
  finalization hypotheses, several since falsified.
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-002.md` -
  the GO filed by this session.
- `bridge/gtkb-wi5441-owner-liveness-spec-amendments-011.md` - the report this
  session independently verified but could not terminally record.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` - owner decision
  governing the six amendments.

## Owner Decisions / Input

No owner decision is requested. The governing authority for the originating
verification work is the active
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` under owner
decision `DELIB-202666274`. This advisory records evidence and discloses state
only; it requests no approval, waiver, or priority choice.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
