NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: f60c8a1c-ab58-4887-a466-8b8444126390
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-wi6002-dispatcher-narrative-substrate-accuracy
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6002
Recommended commit type: docs:
target_paths: [".claude/rules/bridge-essential.md", "config/agent-control/gtkb-bridge-essential.md", "groundtruth-kb/templates/rules/bridge-essential.md", ".claude/rules/prime-bridge-collaboration-protocol.md", ".claude/rules/codex-session-bootstrap.md", ".claude/rules/codex-way-of-working.md", "platform_tests/governance/test_dispatcher_narrative_substrate_accuracy.py", ".groundtruth/formal-artifact-approvals/**"]

# GT-KB Bridge Implementation Proposal - WI-6002 dispatcher narrative substrate accuracy - 001

## Bridge Filing Discipline

This artifact is filed as
`bridge/gtkb-wi6002-dispatcher-narrative-substrate-accuracy-001.md`, the first
entry in a new append-only chain of numbered bridge files. Prior versions are
never deleted or rewritten; every response appends the next numbered file with
its own canonical first-line status. It is written through
`scripts.gtkb_bridge_writer.write_bridge_file`, which mints and consumes a
publication-capability receipt for the file - deliberately, because the
receipt-less direct-write path is the WI-5825 case-(b) stranding class and this
session has already observed that class grow by one member today.

## Problem

Always-loaded narrative surfaces assert that the dispatcher daemon is the live
canonical bridge automation path. Canonical state says otherwise:
`harness-state/bridge-substrate.json` has recorded `"substrate": "none"` since
`2026-08-02T22:59:42Z` (`applied_by: C`), and per
`.claude/rules/operating-role.md`, `none` means manual owner assignment only -
explicitly "not an automated fallback."

The owner standing directive of 2026-08-07, archived as
`DELIB-20260807-DISPATCHER-DISABLED-MANUAL-BRIDGE-OPERATION`, states the legacy
FE dispatcher and daemon and their guards are disabled **on purpose** pending
Dispatcher Next, that the dispatcher must not be activated, and that all Loyal
Opposition and Prime Builder work is driven manually until further notice.

Confirmed stale text (line-level, verified this session):

| Surface | Line | Nature |
| --- | --- | --- |
| `.claude/rules/bridge-essential.md` | 32 | "canonical bridge automation path while it remains healthy" |
| `config/agent-control/gtkb-bridge-essential.md` | 32 | tracked baseline mirror of the same lede |
| `groundtruth-kb/templates/rules/bridge-essential.md` | 32 | **scaffold template - every adopter inherits it** |
| `CLAUDE.md` | 219 | daemon-driven dispatch described as the operating procedure |
| `.claude/rules/prime-bridge-collaboration-protocol.md` | - | "the dispatcher daemon owns automated bridge dispatch ... manual ... is the only fallback when the daemon is unhealthy" |
| `.claude/rules/codex-session-bootstrap.md`, `codex-way-of-working.md` | - | "use the dispatcher daemon when its registrations and dispatch state are healthy" |

## Why the existing guard does not cover this

`DCL-SOT-READ-HOOK-CONTRACT-001` already registers `bridge-essential.md` as a
**forbidden substitute** for the substrate SoT, and that hook fires correctly:
it blocked a tool-call read of that file during this session, naming
`harness-state/bridge-substrate.json` as the canonical path. The guard works.

It cannot fire on the **session-start auto-load path**, where the same text is
injected into model context before any tool call occurs. A fresh session
therefore inherits the stale operating model with no mechanical correction
available to it.

## Demonstrated harm

This is observed, not hypothesised. Session `f60c8a1c` loaded the narrative at
startup, read `gt bridge dispatch status` reporting `Bridge dispatch health:
PASS` with `Selected candidates: loyal-opposition: F`, concluded that a
just-filed `REVISED` would receive an automatic verdict, and armed a background
waiter for it. The owner had to intervene to state that the dispatcher is
disabled deliberately. Time was lost and a false expectation was recorded in the
transcript before correction.

## Scope boundary - this is narrative accuracy, not re-enablement

No change to `harness-state/bridge-substrate.json`, harness lifecycle status,
`can_receive_dispatch`, either disable guard, or any scheduled task is in scope.
Nothing in this proposal moves the platform toward activating dispatch. The
change makes the narrative agree with the canonical substrate value and teaches
the reader where to look, which reduces rather than increases the chance that a
future session "repairs" the intentional disable.

## Relationship to adjacent owned work

- **WI-5992** owns the **CLI reporting** surfaces: the `status`/`health` label
  collision and substrate invisibility. Independent live reproduction was added
  to that item by this session. This proposal does not touch those surfaces.
- **WI-5991** owns the substrate gate failing open and an orphaned daemon loop.
- **WI-5986 v3** records the same owner directive from the capturing session.
- **WI-5664** covers stale *skill-rename* references in `.claude/rules` and the
  `config/agent-control` mirrors - a different subject in overlapping files.
  Sequencing note for review: if WI-5664 lands first, this change rebases onto
  its text; the two edits do not target the same paragraphs.

## Proposed Change

1. In each `bridge-essential.md` copy (`.claude/rules`, the
   `config/agent-control` tracked baseline, and the scaffold template), replace
   the daemon-is-canonical lede with text that (a) names
   `harness-state/bridge-substrate.json` as the authority for which substrate is
   live, (b) states that `substrate: none` means manual operation, and (c)
   preserves the existing do-not-re-enable prohibitions for the retired pollers.
2. In `prime-bridge-collaboration-protocol.md`, `codex-session-bootstrap.md` and
   `codex-way-of-working.md`, replace "use the daemon when healthy / manual is
   the fallback" with a substrate-conditional statement pointing at the same SoT.
3. Add `platform_tests/governance/test_dispatcher_narrative_substrate_accuracy.py`:
   a deterministic check asserting no narrative surface claims an active or
   canonical daemon without also directing the reader to the substrate SoT. The
   test must fail against the current pre-remediation text.

`CLAUDE.md` line 219 is deliberately **excluded** from `target_paths`. It is
GOV-01 length-constrained and carries its own approval surface; a separate
follow-on should carry it so this change is not blocked behind that constraint.
Review should confirm that exclusion is the right call.

### KB / MemBase mutation scope

This implementation performs no MemBase mutation. The change edits narrative
files and adds one test; it inserts, updates and retires nothing in
`groundtruth.db`, and `groundtruth.db` is correctly absent from `target_paths`.
WI-6002, TEST-11844 and the cited deliberation were created before this proposal
and are inputs to it, not outputs of the implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
already requires state claims to derive from fresh canonical reads; this work
brings narrative surfaces into conformance with it. No new requirement is needed.

## Specification Links

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - state claims derive from fresh canonical reads; the governing requirement, and the source spec on WI-6002.
- `DCL-SOT-READ-HOOK-CONTRACT-001` - registers this file as a forbidden substitute for the substrate SoT; establishes that the mechanical guard exists and where its coverage ends.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; the narrative being corrected is the bridge operating-mode narrative.
- `GOV-ARTIFACT-APPROVAL-001` - these are protected narrative artifacts; approval-packet evidence is required per path before any write.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the drift was preserved as durable artifacts (WI-6002, the deliberation, WI-5992 evidence) rather than left in session context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development decision underlying that stance.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - discovering that an always-loaded surface contradicts canonical state is a capture-threshold event, discharged by WI-6002 and this proposal.

## Owner Decisions / Input

- Owner standing directive 2026-08-07 (session `f60c8a1c`), archived as
  `DELIB-20260807-DISPATCHER-DISABLED-MANUAL-BRIDGE-OPERATION`: dispatcher and
  daemon disabled on purpose; do not activate; all LO and PB work manual until
  Dispatcher Next is complete and tested.
- Owner AskUserQuestion 2026-08-07 (session `f60c8a1c`), "Next": selected
  **"Propose reconciling the stale dispatcher rules"** in preference to wrapping,
  capturing a work item only, or picking up other bridge work. That answer is the
  direct authority for filing this proposal.
- **Owner approval still outstanding:** per `GOV-ARTIFACT-APPROVAL-001`, each
  protected narrative path requires its own approval packet with the full
  proposed content presented before the write. This proposal requests GO on the
  approach; it does not claim that per-path approval evidence exists yet.

## Prior Deliberations

- `DELIB-20260807-DISPATCHER-DISABLED-MANUAL-BRIDGE-OPERATION` - the owner directive this work makes the narrative agree with; linked to WI-5992, WI-5986, WI-5991, WI-5942.
- `DELIB-20266272` - PHASE-Y dispatcher-daemon go-live, the decision whose narrative is now superseded by the deliberate disable.
- `DELIB-20266278` - owner authorization of the dispatch-treadmill-drain program.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - the prior substrate retirement, which is the precedent for how a retired substrate's narrative was previously reconciled.
- WI-5992 / WI-5991 / WI-5986 - adjacent owned work, delineated above.

## Specification-Derived Verification Plan

| Specification / requirement | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (TEST-11844) | `pytest platform_tests/governance/test_dispatcher_narrative_substrate_accuracy.py -q` | fails on current text; passes after correction |
| `DCL-SOT-READ-HOOK-CONTRACT-001` coverage boundary | confirm the hook still blocks a tool-call read of `bridge-essential.md` after the edit | block preserved; the edit must not de-register the forbidden substitute |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | confirm do-not-re-enable prohibitions for retired pollers survive the rewrite | prohibitions present and unweakened |
| `GOV-ARTIFACT-APPROVAL-001` | approval packet present per protected path before write | packet exists with matching content hash |
| Scaffold parity | template copy carries the corrected text | adopters inherit substrate-conditional narrative |

## Cross-Harness Disposition

`target_paths` do not touch the harness-surface marker set
(`.claude/settings.json`, `.codex/hooks.json`, `.claude/hooks/**`,
`.codex/gtkb-hooks/**`, `.claude/skills/**`, `.codex/skills/**`), so the gate is
not triggered. The section is retained because two of the corrected files are
Codex-role runbooks.

| Harness / surface | Disposition |
| --- | --- |
| Claude | Behavioural parity. `.claude/rules/bridge-essential.md` and `prime-bridge-collaboration-protocol.md` corrected. |
| Codex | Behavioural parity. `codex-session-bootstrap.md` and `codex-way-of-working.md` corrected in the same change so the Codex role narrative does not diverge. |
| `config/agent-control` tracked baseline | Behavioural parity. Mirror corrected in lockstep so the tracked baseline and the loaded rule do not disagree. |
| Scaffold template / adopters | Behavioural parity. Template corrected so adopters do not inherit a stale operating model. |
| Cursor, Goose, Antigravity, Ollama, OpenRouter, Alibaba | Not applicable. No harness-specific copy of these narrative files exists for those surfaces. |

## Risk / Rollback

- **Risk: reads as an invitation to re-enable dispatch.** Mitigated by the
  explicit scope boundary above and by preserving every existing do-not-re-enable
  prohibition verbatim. Reviewers should treat any weakening of those
  prohibitions as a blocking defect.
- **Risk: protected-artifact approval friction.** Real and accepted: each path
  needs its own approval packet. If the owner prefers a narrower first tranche
  (for example the three `bridge-essential.md` copies only), that is a reasonable
  NO-GO or scope-reduction outcome.
- **Risk: collision with WI-5664** in the same files. Sequencing note provided
  above; the edits target different paragraphs.
- **Rollback:** revert the narrative paths and delete the added test. No runtime
  behaviour, substrate state, or dispatch configuration is touched, so rollback
  carries no operational risk.

## Recommended Commit Type

- Recommended commit type: `docs:` - governance/rule narrative correction plus
  one governance test. No production behaviour changes.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
