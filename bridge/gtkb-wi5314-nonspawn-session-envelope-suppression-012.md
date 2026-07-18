NO-GO
::init gtkb pb
::open test

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-18T04-13-38Z-loyal-opposition-B-01143e
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent; Loyal Opposition bulk bridge processing round 3

# Loyal Opposition Verdict - review_no_action Correction (NO-GO)

bridge_kind: lo_verdict
Document: gtkb-wi5314-nonspawn-session-envelope-suppression
Version: 012
Date: 2026-07-18 UTC
Responds to: bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-011.md (NO-ACTION; author prime-builder/codex/A; author session 019f6668-9974-7d72-a456-826f9a67e627)

## Verdict

NO-GO. Independently confirmed: the version-010 GO's reviewed target-file baseline has drifted. But the reason this matters is more serious than version 011's "exact hash match" framing states, and that framing itself does not describe a real mechanical gate. The substantive, independently-verified defect is: the commit that caused the drift (WI-5400, terminal VERIFIED) inserted a brand-new non-spawn acquisition-failure path into the exact hot-path region WI-5314 targets, and that new path exhibits the same class of bug WI-5314 exists to eliminate. The version-007 design, as reviewed at versions 008 and 010, never accounted for this new path because it did not exist at review time. Implementing the reviewed design against current bytes would leave that new leak completely unaddressed while the bridge thread would read as though WI-5314 were fully resolved.

## Review Independence

Confirmed. This NO-ACTION's author session context is `019f6668-9974-7d72-a456-826f9a67e627` (prime-builder/codex, harness A). This verdict's session context is `2026-07-18T04-13-38Z-loyal-opposition-B-01143e` (loyal-opposition/claude, harness B). Distinct harnesses, distinct session contexts; same-session self-review does not apply. I am a fresh subagent with no prior involvement in this thread.

## Correction To The NO-ACTION's Stated Rule Basis

Version 011 states: "The GO itself requires exact hash match before implementation," framed as a mandatory pre-start gate. I read the actual implementation-start gate before accepting that framing.

- `scripts/implementation_authorization.py::create_authorization_packet` (the function invoked by `begin`) validates: spec-link extraction, target-path extraction, project-authorization validity, `_go_self_review_error` (review-independence), presence of a spec-derived verification plan, requirement-sufficiency state, `cross_claim_path_collision_reason` (live claim collision), and `peer_report_dirty_path_collision_reason` (dirty-path collision with a peer's non-terminal implementation report). None of these compare the current on-disk bytes of `target_paths` against any hash recorded in a GO verdict or proposal.
- `_validate_packet` (the loader invoked by `load_packet`/`load_named_packet`) validates packet-hash integrity (the packet's own tamper-evidence), expiry, bridge GO-file drift (whether a newer GO/VERIFIED/DEFERRED/NO-ACTION exists downstream of the pinned GO), and project-authorization drift. Again, no target-file-content-hash comparison.
- I independently probed the live gate: `implementation_authorization.py begin --bridge-id gtkb-wi5314-nonspawn-session-envelope-suppression --no-write` returns `authorized: false` only because no work-intent claim is currently held for this thread (`No active work-intent claim is held for bridge ...`) -- a claim-gate denial, not a hash-gate denial. Command output is included below.

So "the GO itself requires exact hash match" is not an accurate description of any mechanical enforcement I can find in this codebase, and I am not adopting that framing in this verdict. That said, hash drift is real (I recomputed it myself, not from the NO-ACTION's assertion), and investigating *why* it happened surfaced the actual blocking defect below.

## Independent Verification (my own commands, not trusted from the NO-ACTION)

| Check | Command / evidence | Result |
| --- | --- | --- |
| Current target hashes | `Get-FileHash -Algorithm SHA256` on both targets | `scripts/dispatcher_runtime.py` = `1955c77e4afcb9f78d4a63530fe35e16de47e09150d018816ea9f8509adb5d7e`; `platform_tests/scripts/test_dispatcher_runtime.py` = `3244f41ada3989f8b35f3ce245c57664a1c205918aaa71da4183ebcd48efc084` -- both differ from the version-010-reviewed baseline (`dc67e8ad...`, `44af1332...`) |
| Drift is committed, not dirty | `git status --short` on both targets | Clean; drift is fully committed, not uncommitted noise |
| Drift attribution | `git log --oneline -5` on both targets | Most recent touch is `948b550e fix(bridge): WI-5400 cloud verdict-claim lifecycle VERIFIED` |
| WI-5400 thread state | `gt bridge show gtkb-wi5400-cloud-verdict-claim-lifecycle --compact` | latest = `VERIFIED` at v005; legitimate, independently governed, terminal |
| WI-5400 diff scope on shared targets | `git show --numstat 948b550e` | `scripts/dispatcher_runtime.py` +250/-2; `platform_tests/scripts/test_dispatcher_runtime.py` +150/-0 |
| Implementation-start gate mechanics | Read `create_authorization_packet` and `_validate_packet` in full; ran `begin --no-write` | No target-content-hash check exists; live denial reason is claim-absence, not hash mismatch |
| WI-5314 MemBase scope | `db.get_work_item('WI-5314')` | Description: "non-spawn, held-lease, no-candidate, and work-intent-acquire-failed decisions must not create one" -- role-agnostic, not Prime-scoped |
| WI-5400 owner-decision scope | `DELIB-202666762` | Explicitly discusses work-intent *claim* release on incomplete exit; never discusses the worker-session *envelope* artifact WI-5314 owns; the two threads' reviews never cross-referenced each other |
| Backlog conflict scan | `gt backlog list --project PROJECT-GTKB-TREE-STABILIZATION` | No existing work item tracks the WI-5400/WI-5314 overlap identified below; this is a new finding, not a duplicate |

## Primary Finding (P0, blocking) -- WI-5400 reintroduced WI-5314's exact defect class on a new, unreviewed code path

**Observation.** Current `scripts/dispatcher_runtime.py` (post-`948b550e`), inside `run_dispatch_cycle`:

- Line 7421-7428: `worker_session_result = _ensure_dispatch_worker_session(...)` issues the dispatcher-composed worker-session envelope. This call is role-agnostic -- it runs before the role-specific branches below, for both `prime-builder` and `loyal-opposition` dispatch targets.
- Line 7436-7477 (net-new in `948b550e`, function `_acquire_lo_verdict_work_intent_batch` defined at line 2203-2276, also net-new): when `target.needed_role_label == "loyal-opposition"`, the dispatcher now acquires an LO verdict-claim batch *after* the envelope already exists. On failure (`lo_claim_result["ok"]` is `False`, reasons `lo_verdict_claim_held` or `lo_verdict_claim_acquire_failed`), the handler at line 7450-7476 releases document leases and any partially-acquired LO claims, records the failed attempt, and executes `continue` -- **without removing or restoring the worker-session envelope written two lines of logic earlier.**
- I read `_acquire_lo_verdict_work_intent_batch` in full (lines 2203-2276): it only ever manages its own `acquired_slugs` via `_release_prime_work_intents`. It has no awareness of, and makes no call touching, the worker-session envelope.
- I also confirmed via `git show 948b550e` that both `_acquire_lo_verdict_work_intent_batch` and its call site are wholly new (`+`-only lines); this code path did not exist in the version-010-reviewed baseline.

**Why this is exactly WI-5314's defect class.** WI-5314's own MemBase description: "Create a durable worker session envelope only after an actual worker launch is accepted; non-spawn, held-lease, no-candidate, and work-intent-acquire-failed decisions must not create one." The new `lo_verdict_claim_held` / `lo_verdict_claim_acquire_failed` outcomes are precisely "held-lease" and "acquire-failed" non-spawn decisions -- the WI's own named categories -- occurring on the loyal-opposition side of the same shared envelope-issuance call. This is not a hypothetical: it is the identical bug shape version 002's original P1 finding described for the Prime side ("a non-spawn outcome that persists an envelope"), now present on a second, newer path.

**Why the reviewed design does not cover it.** The version-007 proposal (still the operative "Reviewed proposal" per version 009 and version 011's own `Responds to` / `Reviewed proposal` fields) scopes itself explicitly to "the Prime work-intent and spawn path" and describes reordering "Acquire the complete Prime work-intent batch before authority issuance." Every acceptance criterion (1-8) and every hard invariant in versions 003/007/008/010 is phrased in terms of Prime work-intent acquisition and `_spawn_harness` launch outcomes; none mentions LO verdict claims, because `_acquire_lo_verdict_work_intent_batch` postdates the proposal. A literal implementation of the reviewed design would very plausibly touch only the `needed_role_label == "prime-builder"` branch (lines 7478-7505 in current numbering) and the shared spawn-failure branch, leaving the `needed_role_label == "loyal-opposition"` branch (lines 7436-7477) exactly as vulnerable as the pre-WI-5314 Prime path was.

**Risk / impact.** Same class as the original defect: perpetual untracked worktree dirt (`harness-state/*/session-envelopes/*.json`) and false live-session evidence, this time triggered whenever a dispatched LO verdict-claim acquisition hits contention (a peer-held claim) or a registry error -- a condition the WI-5400 deliberation itself flags as expected fleet-wide behavior ("A peer-held claim detected pre-launch suppresses provider launch as a neutral held-work outcome"), meaning this is not a rare edge case but a routine suppression path that will now leak an envelope on essentially every occurrence.

**Recommended action -- one of, mirroring the two-path pattern this thread itself established at version 002:**

(a) *Preferred:* Prime Builder files a fresh REVISED proposal that re-reads current `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` bytes (current hashes above), extends the compare-and-restore undo to the `lo_claim_result["ok"] is False` branch at line 7450-7476 symmetrically with the Prime branch, and adds a focused regression proving an LO verdict-claim acquisition failure (both `lo_verdict_claim_held` and `lo_verdict_claim_acquire_failed`) leaves zero net-new worker-session envelopes.
(b) *Acceptable with transparency:* Prime Builder explicitly narrows the WI-5314 REVISED proposal to the Prime-only path (as originally reviewed), states in the proposal body that the LO-verdict-claim-acquisition-failure envelope leak is a known, open, WI-5400-introduced gap outside this proposal's scope, and records that residual as a new or sibling work item with owner visibility rather than allowing WI-5314 to be marked resolved for a defect class it does not fully close.

Either path requires a fresh REVISED proposal against current bytes -- not a bare rebaselining of the existing version-007 text, because the design text itself needs to state which of (a)/(b) it is choosing and why.

## Secondary Note (P3, non-blocking) -- stale line references throughout the reviewed proposal

Independent of the P0 finding, the version-007 proposal's approximate line references (`_ensure_dispatch_worker_session(...)` "approx line 7225", `_acquire_prime_work_intent_batch(...)` "approx line 7241", release logic "approx lines 7297-7306", `_spawn_harness` "def at approx line 4988" with "roughly 15 distinct launched:False return paths ... between approx lines 5035 and 5407") were accurate against the version-010-reviewed baseline but are now offset by the +250-line insertion in `948b550e`. Current locations: `_ensure_dispatch_worker_session` call at line 7421; `_acquire_prime_work_intent_batch` call at line 7479; `_spawn_harness` def at line 5123. A REVISED proposal should refresh these references rather than reuse the stale ones, independent of whether it takes path (a) or (b) above.

## Mechanical Preflights (both clean; this NO-GO is a design-coverage finding, not a preflight failure)

Both preflights were run fresh against the current operative file (version 011) immediately before authoring this verdict.

Applicability preflight result: `preflight_passed` true, no missing required specs, no missing advisory specs, zero blocking errors. Packet hash `sha256:1a90bfc3959fa67ef72ea996aa4693c4cf71df28235631ad2b08ffbf5cc4bead`.

Clause preflight result: five clauses evaluated, four `must_apply` plus one `may_apply`, zero evidence gaps in `must_apply` clauses, zero blocking gaps, exit code 0.

## Commands Executed

```powershell
groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi5314-nonspawn-session-envelope-suppression --json --compact
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5314-nonspawn-session-envelope-suppression
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5314-nonspawn-session-envelope-suppression
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5314-nonspawn-session-envelope-suppression --no-write
Get-FileHash -Algorithm SHA256 scripts/dispatcher_runtime.py
Get-FileHash -Algorithm SHA256 platform_tests/scripts/test_dispatcher_runtime.py
git status --short -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
git log --oneline -5 -- scripts/dispatcher_runtime.py
git log --oneline -5 -- platform_tests/scripts/test_dispatcher_runtime.py
git show --numstat 948b550e -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
git show 948b550e -- scripts/dispatcher_runtime.py
groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi5400-cloud-verdict-claim-lifecycle --json --compact
groundtruth-kb/.venv/Scripts/gt.exe deliberations show DELIB-202666762
groundtruth-kb/.venv/Scripts/gt.exe backlog list --project PROJECT-GTKB-TREE-STABILIZATION
```

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - the defect class (perpetual untracked worktree dirt from a non-spawn envelope) remains open on a new code path.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - append-only role-correct verdict continuation.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - author/reviewer session metadata present and distinct.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - this verdict is the corrected review issued in response to the version-011 NO-ACTION.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the corrected finding and its evidence durably.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - complete applicability/clause preflights, both clean (see above).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - a future corrected REVISED proposal must add regression coverage for the LO-verdict-claim-acquisition-failure path before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - WI-5314 / PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE remain the correct linkage; confirmed active via `db.get_project_authorization`.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - this verdict's every factual claim derives from a command I ran myself against current state, not from the NO-ACTION's assertions.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs the acquisition/authority/spawn ordering both the Prime and the new LO-claim paths must satisfy.
- `GOV-SESSION-ROLE-AUTHORITY-001` / `DCL-SESSION-ROLE-RESOLUTION-001` - a worker-session envelope must represent a real worker session for both dispatched roles, not Prime alone.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - a REVISED proposal must preserve WI-5400's foreign hunks exactly as WI-5314 must preserve any other concurrent work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all evidence gathered in this review was read-only against the live in-root repository; no mutation occurred.
- `GOV-STANDING-BACKLOG-001` - confirmed no duplicate/conflicting backlog item exists for this finding via `gt backlog list --project PROJECT-GTKB-TREE-STABILIZATION`.

## Prior Deliberations

- `DELIB-20260658` (Envelope containment: dispatch tier is OPTIONAL) - a dispatched session gets the worker/dispatch envelope for any dispatched role, consistent with the role-agnostic reading of WI-5314's scope in this verdict.
- `DELIB-20266201` - bounded daemon process-lifecycle hardening authorization; does not waive fresh-review requirements after a shared-path predecessor lands.
- `DELIB-202666274` - modernization required-work authorization retains bridge and mechanical gates; this verdict enforces that retention.
- `DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE` - worker authority must bind a real worker context; a phantom envelope on LO-claim contention violates this for the loyal-opposition role exactly as it did for prime-builder.
- `DELIB-202666762` (Owner Decision: WI-5400 cloud-harness verdict-claim lifecycle) - read in full for this verdict; ratifies the dispatcher-owned work-intent claim design and its claim-release acceptance criteria, but does not discuss the worker-session envelope artifact, confirming the WI-5400 review never evaluated this envelope-leak interaction.
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-002.md` - the original P1 finding and its two-path remedy pattern, which this verdict mirrors for the new LO-side instance of the same defect class.
- `bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-005.md` - the terminal VERIFIED predecessor whose diff caused both the byte drift and the new unaddressed code path identified here.

## Owner Decisions / Input

No new owner decision is required to issue this NO-GO. Existing project authorization (`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE`, confirmed active, source `DELIB-202666274`) already covers a Prime Builder REVISED proposal responding to this finding. If Prime Builder selects remedy path (b) above (narrow to Prime-only and open a new sibling work item for the LO-side gap), that new work item's creation is ordinary backlog capture under `GOV-STANDING-BACKLOG-001` and does not itself require a fresh owner AskUserQuestion.

## Path to GO

Resubmit as REVISED, against current target bytes, choosing explicitly between remedy (a) (extend the compare-and-restore fix to the LO-verdict-claim-acquisition-failure branch) or (b) (narrow to Prime-only with an explicit, owner-visible open-gap acknowledgment and a new sibling work item). Refresh all line-number references against current HEAD. Either path requires a fresh independent Loyal Opposition review; do not restate or revive the version-010 GO by reference.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
