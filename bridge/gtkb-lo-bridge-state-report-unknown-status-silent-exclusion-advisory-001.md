ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: caabeb6f-ae6e-47ef-8bf3-6d2aeacf7a42
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: governance_advisory
Document: gtkb-lo-bridge-state-report-unknown-status-silent-exclusion-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28

# Loyal Opposition Advisory - `UNKNOWN` Is a Silent Exclusion Class in the Canonical Bridge Actionability Computation

## Classification Slot

**adapt** - the platform already built a malformed-status *quarantine and health-surfacing*
pattern for the dispatch path under WI-4658. The recommendation is to adapt that existing,
already-VERIFIED pattern to the state-report actionability path, not to invent a new mechanism.

Severity **P3**. **No work is currently being missed** - all nine affected threads are terminal
in substance (see Evidence). The defect is structural and latent: the exclusion is silent by
construction, so a future occurrence would be invisible rather than loud. Filed now because the
cost of surfacing it is small and the surface it protects is the one every scheduled Loyal
Opposition run depends on for correctness.

## Source

Surfaced during a scheduled Loyal Opposition bridge-queue run on 2026-07-28. The run's own
correctness question - "is `LO_ACTIONABLE = 0` trustworthy?" - could not be answered from the
report alone. The defect is outside the scope of any current bridge item and is filed here
rather than folded into a verdict.

## Claim

`gt bridge state-report` derives Loyal-Opposition actionability by exact-membership test against
the resolved latest status. A thread whose latest bridge file has an unparseable status token
resolves to the sentinel `UNKNOWN` and is therefore **excluded from the actionable list without
any error, warning, or health finding**. The only trace is an aggregate count in a separate
table. The report can truthfully print `LO_ACTIONABLE... 0: (none)` while an arbitrary number of
threads were never classified at all.

### Observation

Live output of `gt bridge state-report` at the time of this run:

```
| TOTAL_THREADS | 2276 |
| GO | 87 |
| NO-GO | 166 |
| VERIFIED | 1718 |
| ADVISORY | 61 |
| DEFERRED | 4 |
| WITHDRAWN | 231 |
| UNKNOWN | 9 |
| LO_ACTIONABLE_LATEST_NEW_REVISED_NO_ACTION | 0: (none) |
```

The nine `UNKNOWN` threads are **not enumerated** in the markdown surface. Identifying them
required parsing `--json` and filtering `threads[].latest_status`. Nothing in the report
connects the `UNKNOWN` count to the `LO_ACTIONABLE` determination printed two rows below it.

### Source evidence

`groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`:

```python
# line 103
status = helper.status_from_bridge_file(latest.path) or "UNKNOWN"
status_counts[status] += 1
...
# line 115
lo_actionable = [row for row in threads if row["latest_status"] in LOYAL_OPPOSITION_ACTIONABLE_STATUSES]
```

`status_from_bridge_file` returning falsy is coerced to a sentinel and then silently fails the
membership test at line 115. There is no branch that treats an unresolvable status as a
condition worth reporting. `_bridge_section` returns no diagnostic field for it, so no
downstream consumer - including the dispatcher health surface - can distinguish
"nothing is actionable" from "nine threads were never classified."

### The nine affected threads

All nine carry a markdown heading, not a canonical status token, on the first non-blank line:

| Thread (latest file) | First non-blank line | In-body verdict |
| --- | --- | --- |
| `gtkb-4c-ci-regression-fix-004.md` | `# GT-KB 4C CI Regression Fix Verification - VERIFIED` | `**Verdict:** VERIFIED` |
| `gtkb-credential-patterns-canonical-010.md` | `# GT-KB Canonical Credential-Patterns Module - Codex Verification of 009` | `**Verdict:** VERIFIED` |
| `gtkb-hook-scanner-safe-writer-012.md` | `# GT-KB Scanner-Safe-Writer Hook - Codex Verification of 011` | `**Verdict:** VERIFIED` |
| `gtkb-managed-artifact-registry-010.md` | `# GT-KB Managed Artifact Registry Verification` | `**Verdict: VERIFIED**` |
| `gtkb-operational-skills-tier-a-008.md` | `# GT-KB Operational Skills Tier A - Codex Verification Review of 007` | `**Verdict:** VERIFIED` |
| `gtkb-phase-a-metrics-collector-004.md` | `# GT-KB Phase A Metrics Collector - Codex Verification of 003` | `**Verdict:** VERIFIED` |
| `gtkb-skill-bridge-propose-008.md` | `# GT-KB Skill Bridge Propose - Codex Verification of 007` | `**Verdict:** VERIFIED` |
| `gtkb-skill-decision-capture-012.md` | `# GT-KB Skill Decision Capture - Codex Verification of Post-Implementation 011` | `**Verdict:** VERIFIED` |
| `gov-file-bridge-authority-001.md` | `# GOV-FILE-BRIDGE-AUTHORITY-001 - File Bridge Authority Spec` | `**Status:** active` (spec body, not a verdict) |

Eight are terminal Codex verification verdicts. The ninth is a specification body occupying a
bridge path; it is already the subject of a separate advisory filed earlier today
(`gtkb-lo-gov-file-bridge-authority-spec-body-path-orphaned-advisory`, ADVISORY v001).

**This is why the finding is P3 and not higher: the current exclusion set is inert.** The risk
is the mechanism, not today's contents.

### Why new occurrences are unlikely but not prevented

Two guards exist, and both have gaps:

1. **The governed writer validates.** `scripts/gtkb_bridge_writer.py` defines
   `VALID_STATUSES` (line 59), extracts `_first_status(content)` (line 241), and
   `validate_bridge_envelope_head` raises when `status not in VALID_STATUSES` (lines 338-339).
   Any file written through `write_bridge_file` therefore carries a canonical token. This is
   the primary reason severity is low.
2. **The compliance gate has documented, deliberate gaps.**
   `.claude/rules/file-bridge-protocol.md` § "Body Status-Token Rule" states the rule "fires
   only on the `Write` tool (full file content); `Edit` operations are not subject to it," and
   that "files that already exist on disk with a non-canonical first line are grandfathered, so
   the rule never retroactively breaks historical bridge files on overwrite."

So the residual exposure is a bridge file that reaches disk through neither the Claude `Write`
tool nor `write_bridge_file` - an `Edit` to an existing file, or a direct filesystem write from
a helper or a non-Claude harness. That is narrow. It is not closed, and if it happens the
failure mode is a thread that quietly stops appearing in any queue.

## Deficiency rationale

**The failure mode is silence, and silence is the wrong default for a routing surface.** A
scheduled Loyal Opposition worker's entire correctness argument reduces to trusting
`LO_ACTIONABLE`. When that list is computed by exact-membership against a field that can hold an
unparseable sentinel, an empty list is ambiguous between "queue is clear" and "queue could not
be read." Those two states demand opposite responses - stand down versus escalate - and the
report does not distinguish them.

**The platform has already ruled on this hazard class, in the adjacent path.** WI-4658
(`gtkb-dispatch-malformed-status-token-quarantine`, VERIFIED at v004) established that malformed
bridge status in the *dispatch* path must produce an explicit quarantine record, a persisted
`quarantined_threads` state, and a dispatch-health `WARN` finding. The follow-on advisory
`gtkb-dispatch-malformed-status-token-packet-gap-advisory` then extended the same reasoning to
the authorization-packet parser. The governing judgment - malformed status must be *loud* - is
settled. The state-report actionability path simply never received it.

**Observability, not correctness, is the gap.** The membership test at line 115 is correct: an
unclassifiable thread genuinely should not be handed to a reviewer as actionable. The defect is
that the exclusion produces no signal. Fail-closed is right; fail-silent is not.

**Tracked Surface Bias.** `.claude/rules/codex-way-of-working.md` § Tracked Surface Bias favors
machine-checkable invariants over conventions an agent must remember. "Nine threads are
unclassified" is exactly the kind of invariant that should be asserted mechanically rather than
rediscovered by each session that thinks to parse the JSON.

## Recommended Prime Action

File a normal `NEW` implementation proposal citing this advisory, **after** completing the
owner-grilling gate below. Proposed scope, smallest-first:

1. **Enumerate, don't just count.** When `UNKNOWN > 0`, list the affected slugs and paths in the
   markdown surface of `gt bridge state-report`, adjacent to the `LO_ACTIONABLE` row, so the
   exclusion is visible at the point the actionability claim is made.
2. **Add a health finding.** Surface `UNKNOWN > 0` as a `WARN` in the dispatcher/bridge health
   output, mirroring the WI-4658 dispatch-health treatment of malformed status.
3. **Add a regression test** asserting that a thread whose latest file has a non-canonical first
   line (a) does not appear in `lo_actionable`, and (b) *does* appear in an explicit
   unclassified/quarantined collection returned by `_bridge_section`.
4. **Optionally add a doctor check** so the condition is caught outside the report path.

Likely target paths:

- `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py` (exists today)
- optionally `groundtruth-kb/src/groundtruth_kb/project/doctor.py`

**Remediation of the nine legacy files is deliberately excluded from this recommendation.**
Prepending canonical status tokens would mutate historical append-only bridge artifacts, which
is governance-sensitive and needs its own owner decision. Surfacing the condition does not
require touching them.

### Option rationale

Rejected: *back-fill a canonical token into the nine legacy files.* It would zero the `UNKNOWN`
count and appear to solve the problem, but it edits the append-only audit chain to satisfy a
reporting surface, and it leaves the silent-exclusion mechanism intact for the next occurrence.
Treating the symptom would also remove the evidence that motivates the real fix.

Rejected: *infer status from in-body `**Verdict:** X` lines when the first-line token is
absent.* Eight of the nine files would resolve correctly. But it re-introduces exactly the
multi-parser ambiguity that WI-4658 and WI-5475 ("Consolidate ~19 duplicate copies of the
bridge-status-token regex") are working to eliminate, and it would silently promote a
heuristic guess into a routing decision. Fail-closed-and-loud is the safer contract.

Preferred: **surface the exclusion, change no classification logic.** The membership test stays
as-is; only the reporting and health surfaces gain the missing signal. Small, additive,
test-covered, and consistent with the settled WI-4658 judgment.

## Owner Decision Needed

Yes. This advisory recommends `adapt`, which implies changes to the bridge state-report module,
a health/doctor surface, and tests. **No implementation is authorized by this advisory.**

### Required Prime Builder Owner-Grilling Gate

**Implementation implied:** Yes - see Recommended Prime Action.

**Grill-the-owner questions.** Prime Builder must obtain durable `AskUserQuestion`-recorded
answers to:

1. **Severity posture.** Should `UNKNOWN > 0` be a `WARN` (consistent with the WI-4658
   dispatch-health treatment) or a `FAIL` that blocks automated actionability claims? `WARN`
   preserves current operation; `FAIL` forces resolution but would immediately trip on the nine
   inert legacy files.
2. **Scope of the surface.** Is enumeration in `gt bridge state-report` sufficient, or should
   the condition also raise a `gt project doctor` check? The doctor path catches it outside the
   report; it is also one more check to maintain.
3. **Legacy-file disposition.** Are the nine existing `UNKNOWN` files to be left as historical
   residue (preferred here), or normalized by prepending canonical tokens? Normalization mutates
   append-only bridge artifacts and requires explicit separate authorization.
4. **Interaction with WI-5092.** WI-5092 already covers a misleading `state-report` health
   surface. Should this work be folded into WI-5092 as an additional acceptance item, or tracked
   as its own work item?

**Required durable owner decisions** before an implementation proposal may be filed: the
severity posture (Q1), the surface scope (Q2), and - only if normalization is chosen - an
explicit, separate authorization for mutating the nine historical bridge files (Q3).

## Prior Deliberations

Searched `gt deliberations search` on bridge status-token, `UNKNOWN` status, and state-report
actionability terms; reviewed `gt backlog list` filtered on `UNKNOWN`, status-token,
state-report, and actionability titles; and read the two adjacent bridge threads directly.

- `gtkb-dispatch-malformed-status-token-quarantine` (VERIFIED v004, WI-4658) - established
  quarantine semantics, persisted `quarantined_threads` state, and a dispatch-health `WARN` for
  malformed bridge status **in the dispatch path**. This advisory asks for the same treatment in
  the state-report path. Directly on point as precedent; does not cover this surface.
- `gtkb-dispatch-malformed-status-token-packet-gap-advisory` (ADVISORY v001) - extended the
  WI-4658 reasoning to `scripts/implementation_authorization.py` packet creation. Same hazard
  class, third distinct path, still not the state-report path.
- **WI-5092** - "state-report DISPATCHER 'Health: PASS' is misleading while the daemon is
  dead/disabled." Closest open item in spirit: both concern the state report presenting a
  falsely reassuring surface. **Different subject** - WI-5092 is about the DISPATCHER health
  row; this is about the BRIDGE actionability computation. Q4 of the grilling gate asks the
  owner whether to merge them.
- **WI-5475** - "Consolidate ~19 duplicate copies of the bridge-status-token regex missing
  NO-ACTION." Concerns parser *duplication and drift*; would reduce the chance of divergent
  parse results but would not make an unresolvable status visible. Complementary, not
  overlapping.
- **WI-5693** - "Make bridge state reports generation-current before actionable routing."
  Concerns report *staleness* before routing; orthogonal to unparseable status. Not a duplicate.
- `DELIB-20265429`, `DELIB-20263730`, `DELIB-20263732` - bridge automation status-driver
  reviews. Adjacent to bridge status handling; none addresses the `UNKNOWN` sentinel or its
  effect on actionability.

**No duplicate found.** The three adjacent work items each touch the same report or the same
parser family, but none asserts that an unresolvable status is silently dropped from the
actionable computation.

## Non-Approval Semantics

This advisory is not implementation approval and creates no implementation authority. It
recommends that Prime Builder conduct the owner-grilling pass above, capture the resulting
decisions, and only then file a normal `NEW` implementation proposal citing this advisory as its
source. Nothing here authorizes source, configuration, hook, CLI, rule, test, or bridge-file
mutation. In particular, nothing here authorizes editing the nine historical bridge files named
in the Evidence section.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
