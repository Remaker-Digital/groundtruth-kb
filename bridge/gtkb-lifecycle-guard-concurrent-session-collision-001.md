ADVISORY

# Advisory: Startup-Input-Gate Lifecycle Guard Is Not Session-Scoped â€” Cross-Session Blocking/Clearing Under Concurrent Multi-Worker Dispatch

bridge_kind: governance_advisory
Document: gtkb-lifecycle-guard-concurrent-session-collision
Version: 001
Author: Loyal Opposition (Claude Code, harness B)
Date: 2026-07-18 UTC

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: b7c2c4c5-cdc9-4509-9689-cbcef8014f8f
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive session; resolved role loyal-opposition via dispatcher/default registry (harness B, `harness-state/harness-registry.json`); no session-stated `::init` override observed in this session

implementation_scope: none (advisory / defect-diagnosis only; no code, test, or KB mutation proposed or performed by this document)
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

---

## Author Metadata Resolution Disclosure (read before review)

The `author_identity` / `author_harness_id` lines above were set **manually**, not accepted from the automated resolver. Invoking `scripts/bridge_author_metadata.load_author_metadata()` from this session's own shell (no explicit overrides) resolved `author_identity=prime-builder/codex` and `author_harness_id=A` -- that is, a different harness's identity, not this session's -- even though `author_session_context_id` correctly resolved to this session's real ID (`b7c2c4c5-cdc9-4509-9689-cbcef8014f8f`, confirmed independently against this session's own scratchpad path) via `CLAUDE_CODE_SESSION_ID`. Direct check of the ambient environment confirmed `GTKB_HARNESS_NAME`, `GTKB_HARNESS_ID`, `GTKB_AUTHOR_IDENTITY`, `GTKB_AUTHOR_HARNESS_ID`, `CODEX_HARNESS_ID`, and `CLAUDE_HARNESS_ID` were all unset -- so the wrong values are not coming from a stale/leaked env var; they come from some other fallback path inside `load_author_metadata()`'s harness-identity resolution that does not use the correctly-detected `CLAUDE_CODE_SESSION_ID` signal to infer which harness this is. This is not fully root-caused in this review (the exact fallback code path was not traced) and is reported here only as an honest disclosure of why the header above was hand-corrected, plus a flag that the live bridge-write path may share the same exposure for any session invoking this resolver without an explicit override. See Recommended Prime Action item 3.

## Source

Discovered during an independent Loyal Opposition review of bridge thread `gtkb-wi5389-codex-no-window-schema-contract` (2026-07-18). Out of scope for that thread; captured here per the owner's standing directive (quoted verbatim in `bridge/gtkb-role-gated-hook-envelope-fragility-advisory-002.md` section Owner Decisions / Input): "When you find an error, flaw or opportunity for enhancement, you must not allow that to be forgotten. The correct response is always to file an Advisory Proposal."

## Claim

The `PreToolUse` hook that gates Bash/PowerShell tool use behind the startup-input relay (`GTKB-STARTUP-INPUT-GATE`) reads and clears a state file that is keyed only by harness name, not by session. Under the platform's own configured concurrent-dispatch topology (multiple simultaneous interactive Loyal Opposition worker sessions of the same harness), this produces two independent, compounding failure directions: a sibling session's fresh start can spuriously block an unrelated already-running sibling's tool use, and a sibling session's routine prompt turn can prematurely clear a different sibling's genuine pending gate.

### Evidence (verified by direct source inspection, not paraphrase)

- `scripts/workstream_focus.py:134-138` -- `HARNESS_LIFECYCLE_GUARDS` maps the guard state file per harness name only: three entries, one per harness (`codex`, `claude`, `cursor`), each pointing at that harness's own `session-lifecycle-guard.json`.
- `scripts/workstream_focus.py:374-382` -- `lifecycle_guard_path()` resolves to `HARNESS_LIFECYCLE_GUARDS[harness_name]` whenever the harness name is recognized; `project_root` (and therefore any session-scoping signal) is not consulted on that branch.
- `scripts/workstream_focus.py:2279-2301` -- `guard_tool_use()` ("Phase 7 root-aware guard"). Line 2293 blocks whenever `_startup_response_pending(project_root)` is true and the call is not the one exempted startup-relay cache read. This runs on every tool-use payload the hook receives.
- `scripts/workstream_focus.py:2078-2119` -- `_startup_response_pending()`, the function `guard_tool_use()` calls to decide whether to block, reads that same shared per-harness-name file and returns true/false based only on the `startup_response_pending` boolean and elapsed time since `armed_at` / `startup_prompt_discarded_at` (30-minute expiry via `STARTUP_RESPONSE_PENDING_EXPIRY_SECONDS` at line 111). It never compares the file's `startup_guard_id` field against the identity of the session currently making the tool call.
- `scripts/workstream_focus.py:1963-1972` -- the arm event: on a fresh-session init-keyword match, `state["startup_response_pending"] = True` is written unconditionally to the shared per-harness-name file (line 1968).
- `scripts/workstream_focus.py:1931` -- the companion "discard next prompt" gate checks the same shared file's `discard_next_user_prompt` boolean with no session comparison either -- corroborating evidence that the gap is "the shared file carries no session key anywhere it is read for a live decision," not a one-off oversight in a single function.
- `scripts/workstream_focus.py:2350-2377` (`handle_user_prompt()`) -- `_clear_startup_response_pending_for_followup()` is called unconditionally at line 2375 for any prompt that reaches that point (i.e. any prompt not intercepted earlier by the discard-first-prompt gate at lines 2356-2358), regardless of which session's prompt triggered the call. A second, conditional call site exists at line 2369, reached only inside the mid-session init-keyword-role-change branch.
- The codebase already contains session-scoping infrastructure that none of the paths above use. A `startup_guard_id` field exists in the shared state schema and is populated with a real per-session value (`session_start_context_id`) at `scripts/session_start_dispatch_core.py:801-808`, whose own comment states that a missing or malformed context must not inherit a prior session's guard id. That field is read for session-identity comparison in exactly one place, `acknowledge_startup_owner_input(session_id, ...)` (`scripts/workstream_focus.py:2058-2076`, used after an explicit `AskUserQuestion` round-trip completes), which compares the caller-supplied session id against the stored `startup_guard_id` and refuses to clear on a mismatch. The two paths that matter for this defect -- the live block check (`_startup_response_pending`) and the general per-prompt clear (`_clear_startup_response_pending_for_followup`) -- do not use it. The gap is not "no session-scoping mechanism exists"; it is that the mechanism exists, is populated correctly, and is applied inconsistently.
- `harness-state/harness-registry.json` (read via `gt harness roles`, 2026-07-18) confirms concurrent multi-worker dispatch of this session's own harness (id `B`, role loyal-opposition) is a live, configured topology: up to three concurrent dispatch items are permitted for that harness. The dispatcher can and does run multiple simultaneous interactive-harness Loyal Opposition sub-agent workers against the same shared bridge queue -- this is not a hypothetical edge case.

### Empirical corroboration

The reporting session hit the block message verbatim -- "BLOCKED (GTKB-STARTUP-INPUT-GATE): startup disclosure has been emitted; awaiting owner's next message before tool use." -- while mid-review of `gtkb-wi5389-codex-no-window-schema-contract`, with no prior action by this session that should have armed the gate. A retry moments later, with no action taken, succeeded; a direct read of the guard file at that point showed the pending flag was false. This is consistent with (not independently proven to be, but strongly suggestive of, per the mechanism above) a sibling session's `handle_user_prompt()` call clearing the shared flag, unrelated to the reporting session's own state.

### Why this matters

This is a reliability/liveness defect in the coordination substrate that `.claude/rules/bridge-essential.md` calls the top-priority task, always. A spurious block can stall a concurrent Loyal Opposition reviewer against the live bridge queue (22 entries pending Loyal Opposition review at the time of this finding) for up to `STARTUP_RESPONSE_PENDING_EXPIRY_SECONDS` (30 minutes) in the worst case where no sibling happens to clear it first. It self-healed quickly in the one observed instance, but nothing in the code guarantees that -- the self-heal is an accident of some other session's unrelated prompt-handling, not designed behavior. The opposite-direction risk (a sibling's routine prompt prematurely clearing a different session's genuine pending gate) is, if anything, worse: it defeats the gate's actual purpose -- ensuring the startup disclosure was genuinely relayed before tool use, per `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` (cited in the block-reason text itself) -- silently and without any error surfaced to either session.

## Owner Decision Needed

1. Which remediation direction should Prime Builder's implementation proposal pursue: (a) make the live block-check (`_startup_response_pending`) genuinely session-scoped by resolving and comparing the calling session's own identity against `state["startup_guard_id"]` (extending the pattern already used in `acknowledge_startup_owner_input`); (b) bound worst-case impact independent of a full correctness fix (e.g. a shorter/differentiated expiry for cross-session reads); or (c) both? Option (a) is the structurally correct fix but requires cheap session-identity resolution inside a `PreToolUse` hot path with a 5-second hook timeout; option (b) is weaker (does not fix the premature-clear direction) but lower-risk if (a)'s resolution cost proves awkward.
2. Should the false-negative premature-clear risk (the unconditional `_clear_startup_response_pending_for_followup()` call) be fixed in the same work item as the false-positive blocking risk, or split into a separate work item? They share root cause (harness-name-only file keying) but are independent failure directions with independent test plans.
3. Given 22 bridge entries were pending Loyal Opposition review at the time of this finding and concurrent Loyal Opposition dispatch is live and configured for this harness, how should this rank against current backlog priority -- is the up-to-30-minute worst-case spurious-block risk urgent enough to prioritize ahead of pending bridge work, or does the empirically-observed quick self-heal make a scheduled priority level appropriate rather than urgent?
4. Should the same fix scope also cover the analogous per-harness-name-only keying for the other single-entry harnesses in `HARNESS_LIFECYCLE_GUARDS`, or should scope stay limited to this session's own harness pending a separate check of whether concurrent dispatch is similarly configured for those harnesses? (Not checked in this review.)

These questions remain open pending a dedicated `AskUserQuestion` pass; per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` they must be resolved before any implementation proposal derived from this advisory is drafted.

## Recommended Prime Action

1. Run the four Owner Decision Needed questions above via `AskUserQuestion` (one at a time) before drafting any implementation proposal.
2. Once direction is chosen, register this finding as a MemBase work item with a linked regression test per the standard GOV-12 chain. The test should simulate two concurrent guard-state interactions under the same harness name and assert that one session's tool use is unaffected by a sibling session's arm/clear events (must fail on current code, pass after the fix). Re-run the existing WI-5083 / WI-5118 / startup-relay-read-exemption regression coverage afterward, since the fix touches the same state file and functions those three threads already hardened for other cases.
3. Separately and independently of item 1/2: investigate why `scripts/bridge_author_metadata.load_author_metadata()` resolves `author_identity` / `author_harness_id` to a different harness's defaults for this confirmed session (see disclosure note above) when no harness-identifying env var is set. This is a distinct, smaller, and not-yet-root-caused finding surfaced only as a byproduct of preparing this document's own header; it may already be adjacent to the `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` incident class referenced in that module's own source comments (`scripts/bridge_author_metadata.py:37-42`) and deserves its own look, but is out of scope for this review to fully trace.
4. No action needed on the stale `bridge_kind` value referenced in `.claude/rules/canonical-terminology.md` and elsewhere -- already captured as a Recommended Prime Action item in `bridge/gtkb-role-gated-hook-envelope-fragility-advisory-002.md`. This document correctly used `governance_advisory` (verified directly against the authoritative `BridgeKind` enum that `bridge-compliance-gate.py` validates against) to avoid repeating that thread's two failed filing attempts.

## Classification Slot

adapt. The finding is real and directly confirmed against live source (not speculative) -- not a reject. It is not blocked on any milestone, so not a pure defer. The failure mode has a demonstrated instance and a verified worst-case bound (30 minutes, non-self-healing by design), so monitor alone is insufficient given the affected subsystem is the bridge protocol itself. It is not yet implementation-ready -- two candidate directions exist with different risk/effort tradeoffs, and work-item scoping/priority are open -- so full adopt is premature. Adapt is the correct slot: the core direction (extend the existing-but-underused session-identity comparison pattern to the paths that lack it) should be carried forward, but the exact design and priority await the owner-grilling answers above.

## Specification Links

- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` (governs this document's Owner Decision Needed / Recommended Prime Action structure).
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` (the mechanism the guard under review exists to enforce; cited directly in the block-reason text).
- `.claude/rules/bridge-essential.md` (the "top-priority task, always" framing for why this defect's severity is assessed as more than cosmetic).
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` (adjacent authority for the author-metadata-resolution disclosure note; not claimed as directly governing, flagged for Prime Builder's own applicability judgment).

## Prior Deliberations

`gt deliberations search` run twice this session (queries: lifecycle guard concurrent session shared harness state; startup response pending session scoping) returned related-but-distinct results (session envelope durability, startup symmetry, mid-session role-switch verification) with no exact match on cross-session guard-file collision under concurrent multi-worker dispatch.

Three related bridge threads exist, were read in full at their latest (VERIFIED, terminal) version, and are cited as related prior art -- reviewed and distinguished, not duplicates:

- `bridge/gtkb-wi5118-startup-gate-fresh-start-only-*.md` (VERIFIED) -- fresh-start-only gating; does not address cross-session file sharing.
- `bridge/gtkb-wi5083-startup-input-gate-rearm-fix-*.md` (VERIFIED) -- the belt-and-suspenders fix for mid-session-continuation (resume/compact) false arms; addresses a temporal re-arm case within one session's own lifecycle, not a cross-session collision.
- `bridge/gtkb-startup-relay-pretooluse-read-exemption-*.md` (VERIFIED) -- narrows the Bash-read exemption so the gate doesn't block the one legitimate startup-relay cache read; does not address arm/clear scoping itself.

Also directly relevant (found while resolving this document's own `bridge_kind` value): `bridge/gtkb-role-gated-hook-envelope-fragility-advisory-002.md` (thread still open as of this writing, latest version -003 not read in full) -- an unrelated defect in a different role-gated hook trusting a single static session-envelope file with no live cross-check, filed under the same owner standing-directive cited in the Source section above. Both threads share a structural theme (a `PreToolUse` gate trusting session/identity state without verifying it is current or session-specific) even though the underlying files, hooks, and mechanisms are entirely distinct -- worth Prime Builder's awareness as a possible pattern, not asserted here as one finding.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

This advisory does not itself depend on new owner approval to be filed -- advisory capture is not implementation approval, and the owner's standing directive quoted in the Source section already authorizes filing an Advisory Proposal whenever an error, flaw, or enhancement opportunity is found. The Owner Decision Needed questions above remain open pending a dedicated `AskUserQuestion` pass before any implementation proposal is drafted.

## Non-Approval Statement

This ADVISORY entry is not implementation approval. It does not authorize any code change, does not bypass the bridge, project-authorization, owner-decision, root-boundary, credential-safety, formal-artifact, or verification gates, and does not itself constitute a work item until formally registered in MemBase.

## Methodology Trail

- Confirmed current operating role via `gt harness roles` (`harness-state/harness-registry.json`): this session's harness holds the loyal-opposition role with concurrent dispatch enabled -- substantiating the concurrent-multi-worker framing as live/configured, and determining that this finding should be filed as an ADVISORY rather than a Prime Builder work item.
- Read `scripts/workstream_focus.py` lines 100-420, 1930-2005, 2000-2135, 2270-2380 directly to verify every line-number and function-name claim in this report against live source.
- Read `scripts/session_start_dispatch_core.py` lines 797-813 to confirm `GTKB_STARTUP_GUARD_ID` session-scoping intent and its non-use in the block-check path.
- Read `scripts/bridge_author_metadata.py` in full to confirm ADVISORY is a first-class bridge author-metadata status, and to resolve this document's own header -- which surfaced the disclosure noted above.
- Confirmed all three related-prior-art bridge threads exist and are VERIFIED (terminal) via direct reads of their latest versions.
- Ran `gt deliberations search` twice -- no exact duplicate found.
- Verified the `governance_advisory` bridge-kind value directly against the authoritative taxonomy module that `bridge-compliance-gate.py` validates against, and against that hook's required-section constants for the ADVISORY template shape, rather than trusting skill docs or the glossary entry that reference a stale value.

Skills applied: bridge, codex-report, advisory-proposal

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
