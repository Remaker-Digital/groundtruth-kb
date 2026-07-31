GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 94c9c26b-f0dd-43e9-aac0-87147bf1e18f
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code auto-dispatched loyal-opposition worker (::init gtkb lo); dispatch 2026-07-12T01-37-34Z-loyal-opposition-B-1efffa

# Loyal Opposition Review — WI-5204 Preserve H review outcomes across native Stop-hook failures

bridge_kind: lo_verdict
Document: gtkb-wi5204-h-stop-hook-completion-preservation
Version: 002
Responds to: gtkb-wi5204-h-stop-hook-completion-preservation-001 (NEW; Prime Builder, Codex harness A)
Reviewer: Loyal Opposition (Claude, harness B) — auto-dispatched worker
Date: 2026-07-12 UTC

## Verdict

GO. The proposal correctly diagnoses a reproduced native-full lifecycle defect, its
design preserves every fail-closed guarantee that matters, the specification linkage is
complete, and the spec-derived verification plan maps back to the linked specifications.
Both mandatory mechanical preflights pass with no blocking gaps.

## Review Independence

- Author session context: `019f522a-849d-7d43-8c60-0afc829438a6` (Prime Builder, Codex harness A).
- Reviewer session context: `94c9c26b-f0dd-43e9-aac0-87147bf1e18f` (Loyal Opposition, Claude harness B, dispatched worker).
- Distinct session contexts → review independence satisfied per file-bridge-protocol § Review Independence Boundary; harness-ID overlap is not the boundary and no overlap exists here.

## Premise Verified in Live Code

Claim under review: `run_tool_loop` invokes the native `Stop` hook unconditionally in its
`finally` cleanup, so any Stop-hook failure masks the pending return value or the pre-Stop
exception.

Evidence inspected — `scripts/cloud_harness_base.py`:

- The tool-loop `finally` cleanup calls `invoke_native_hooks(NATIVE_HOOK_STOP, ...)`
  unconditionally whenever `native_hooks_started` is true.
- `invoke_native_hooks` is uniformly fail-closed for the Stop event: a timed-out hook
  raises `CloudHarnessError`; a nonzero exit raises; malformed JSON raises; a non-dict
  payload raises; and (for any non-PreToolUse event) a block reason raises. Only a
  successful empty-stdout hook is a no-op (`continue`) — the WI-5198 fix.
- A raise from a `finally` block replaces any in-flight `return content` (the final-response
  path) or the original `try`-body exception. The successful 55-turn review outcome from run
  `2026-07-12T00-58-06Z-loyal-opposition-H-33480b` was therefore convertible into an exit-1
  error with the pre-Stop outcome erased — exactly the observed failure.

Assessment: premise CONFIRMED against current source. `.claude/settings.json` registers the
wrap-up Stop hook (`session_self_initialization.py --emit-wrapup --fast-hook`) at a 15-second
allowance, so the transient-latency scenario the proposal describes is real, not hypothetical.

## Design Soundness

1. Fail-closed boundary preserved where it matters. The proposal narrows the generic
   WI-5198 fail-closed rule for the `Stop` lifecycle event ONLY (timeout / non-blocking
   non-2 exit / malformed informational output → preserve the pending result or original
   exception), while explicitly keeping `PreToolUse` denials, guard-adapter empty/error
   paths, provider errors, session-timeout, and max-turn exhaustion fail-closed. This is
   correct: the Stop lifecycle hooks registered in `.claude/settings.json`
   (`session_self_initialization`, `owner-decision-tracker`, `bridge_verified_backlog_reconciler`,
   `advisory-router-scan`, `advisory_grilling_gate_lint`, `auto_finalize_sweep`) are
   fail-soft wrap-up hooks by design, whereas the mutation guards the proposal is careful
   to protect live on the `PreToolUse` / guard-adapter path. Treating Stop-hook failure as
   non-masking is aligned with those hooks' own fail-soft contracts.

2. No blanket `fail_open` switch. The Risk/Rollback section commits to dedicated Stop
   evaluation rather than a generic switch, which keeps the mutation-guard blast radius out
   of scope. Concur with this as the correct discriminator.

3. Explicit block → continue is bounded. An explicit Stop block (exit 2 or valid block JSON)
   returns the reason to the model and continues under a bounded eight-block ceiling. A
   bounded ceiling is the right safeguard against a Stop hook that blocks indefinitely; the
   specific ceiling value is an implementation detail to confirm at verification, not a
   design blocker.

4. No false-success risk. Preserving pre-Stop stdout cannot upgrade prose-only completion to
   success because the dispatcher independently requires a role-correct bridge verdict. Concur.

5. Generous-allowance policy is owner-directed. Raising the registered wrap-up allowance
   15→60s matches `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` and mirrors the existing
   60s SessionStart dispatch allowance; the ~45s worst-case addition is negligible against the
   approved 28,800s session envelope.

## Scope / target_paths Sufficiency

`target_paths` covers the described change coherently:
- `.claude/settings.json` — the 15→60 Stop allowance.
- `scripts/cloud_harness_base.py` — event-specific Stop handling in the tool loop.
- `scripts/check_codex_hook_parity.py` + `platform_tests/scripts/test_codex_hook_parity.py` —
  the Claude Stop-hook parity assertions currently validate presence/flags but NOT a timeout
  value, so adding a 60s allowance assertion (paralleling the existing Codex SessionStart
  `>= 60` check) is the natural home for verification-plan item 2. Justified inclusion.
- `platform_tests/scripts/test_cloud_harness_base.py`,
  `platform_tests/scripts/test_alibaba_cloud_studio_harness.py` — shared-base and H
  registration/parity regressions.

## Supersession Framing Verified

The proposal states it supersedes the WI-5198 fail-closed statement for the `Stop` event only
while preserving WI-5198's PreToolUse and guard protections. WI-5198-001 explicitly scoped its
fix to empty-output-continuation and kept "Nonzero exits, timeouts, malformed non-empty JSON,
explicit block decisions ... fail-closed." The narrowing is coherent and correctly scoped; it
does not reopen WI-5198's PreToolUse/guard guarantees.

## Cross-Harness Disposition

Required (target_paths touches `.claude/settings.json`, a harness surface) and present. The
A/B/C/D/F/H table is accurate: Codex A does not consume Claude Stop registrations (parity test
must keep the non-native disposition and not invent a Codex Stop command); B receives the same
60s registered allowance natively; C has no Claude Stop registration; D/F run the shared base at
the guard-adapter floor (event-specific Stop code unreachable); H is the affected native-full
adopter. No typed waiver requested. Concur.

## Backlog / Prior Deliberations

- No backlog conflict. `WI-5206` ("make emit-wrapup fast-hook bypass full startup and dashboard
  generation") is the complementary ROOT-CAUSE performance item; WI-5204 is the DEFENSIVE layer
  (do not mask a completed outcome even when a lifecycle hook is slow). They are layered, not
  duplicative — no need to fold WI-5206 into this scope.
- Deliberation search run (`gt deliberations search "Stop hook completion preservation cloud
  harness native"`): surfaced DELIB-202666095 (GO Alibaba H slice 4b), DELIB-202665950/951
  (VERIFIED/GO), DELIB-20260709 (slice-4 split), DELIB-20260708 (Goose GOV-bypass incident).
  None is a prior rejection of the Stop-preservation approach; no revisit-of-rejected-approach
  concern. The proposal's cited DELIBs (DELIB-202666173, DELIB-20260703, DELIB-20260711,
  WI-5198 bridge, INTAKE-6308b73f) are consistent with committed git history (WI-5198 and
  WI-5200..5202 are VERIFIED and committed).

## Applicability Preflight

- packet_hash: `sha256:6364b11c4fa25e63c51d7b2019eac6c3d3de69d61068c91f381cfb95f37ed326`
- bridge_document_name: `gtkb-wi5204-h-stop-hook-completion-preservation`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5204-h-stop-hook-completion-preservation-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

The three uncited entries are `advisory` severity only (matched on generic governance
vocabulary, not substantively relevant to a Stop-hook lifecycle code fix); they do not gate GO.

## Clause Applicability

- Clauses evaluated: 5; must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- adr_dcl_clause_preflight exit code: 0 (mandatory mode)

| Clause | Applicability | Evidence | Enforcement |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes | blocking |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | may_apply | — | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | — | blocking |

## Verification Expectations (post-implementation)

At post-implementation verification the implementation report must demonstrate:

1. Shared-base regressions proving Stop timeout / non-blocking non-2 exit / malformed
   informational output preserve a candidate result or the original exception, and that an
   explicit exit-2/JSON block continues the loop and fails closed after the bounded repeated-
   block ceiling.
2. `PreToolUse` timeout/block/nonzero/malformed AND guard-adapter empty/error paths remain
   fail-closed (regression evidence, not just assertion).
3. The parity assertion proving the wrap-up Stop allowance is 60s and H still uses the
   native-full hook runner (no hook bypass); the Codex parity path still reports the
   non-native Stop disposition without inventing a Codex Stop command.
4. Per GOV-HARNESS-ONBOARDING-CONTRACT-001, a genuine dispatcher-produced H run performing
   real tool work AND writing a role-correct committed bridge verdict after re-enable.
5. `ruff check` AND `ruff format --check` (separate gates) clean on all changed Python.

## Recommended Commit Type

`fix` — concur. Corrects a reproduced native-full lifecycle failure without adding a new
capability surface.

---

Evidence trail: read `bridge/gtkb-wi5204-h-stop-hook-completion-preservation-001.md`,
`scripts/cloud_harness_base.py` (`run_tool_loop`, `invoke_native_hooks`), `.claude/settings.json`
(Stop registration), `scripts/check_codex_hook_parity.py` (Claude Stop parity block),
`bridge/gtkb-wi5198-native-hook-empty-allow-001.md`; ran `bridge_applicability_preflight.py`
and `adr_dcl_clause_preflight.py` (exit 0); `gt backlog list --project
PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`; `gt deliberations search`.
