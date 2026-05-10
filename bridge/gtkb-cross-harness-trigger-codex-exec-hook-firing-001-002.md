NO-GO: Cross-Harness Trigger Codex-Exec Hook Firing Proposal Review

Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-10 UTC
Reviewed: `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-001.md`
Thread: `gtkb-cross-harness-trigger-codex-exec-hook-firing-001`

## Verdict

NO-GO.

The investigation-first shape is directionally right, but the proposal needs revision before implementation. The current draft misstates the prior Codex hook evidence, describes a live-state probe as read-only while depending on live state mutation, omits the current hook-parity ADR from the required specification surface, and includes a fallback path that does not satisfy the stated "dispatch-state stays current after Codex completes" acceptance target.

## Prior Deliberations

Deliberation searches run before review:

- `codex exec hooks cross harness trigger dispatch state`
- `Codex hooks Windows retest cross harness event driven trigger`
- `smart poller retirement cross harness trigger codex exec dispatch`

Relevant results:

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - empirical Codex hooks retest on Windows using `codex exec`.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - owner decision refreshing the hook-parity stance: `.codex/hooks.json` is live on supported Codex CLI versions.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - owner decision retiring the smart poller in favor of the cross-harness event-driven trigger.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - historical owner clarification separating retired token-heavy pollers from acceptable bridge automation.

## Findings

### F1 - P1 - Prior hook evidence is framed incorrectly

Observation: The proposal says the S337 retest covered "interactive Codex CLI sessions" and "NOT `codex exec` cross-harness dispatch invocations" (`-001.md:46-47`).

Evidence: The current role rule states that `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 and `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` establish `.codex/hooks.json` as a live Windows interception boundary for Codex CLI versions with `codex_hooks stable true`, and that SessionStart, UserPromptSubmit, and Stop hooks fired during a `codex exec` invocation (`.claude/rules/acting-prime-builder.md:99-110`). The DA search for `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` also reports the test invocation as `codex exec --skip-git-repo-check ...`.

Impact: The proposal is diagnosing the wrong delta. The real untested gap is not "interactive vs `codex exec`"; it is "isolated temp-project `codex exec` hook firing vs real GT-KB cross-harness dispatch-session hook behavior, with the production `.codex/hooks.json`, `GTKB_BRIDGE_POLLER_RUN_ID`, current cwd/root resolution, tool matchers, and bridge-state side effects."

Required revision: Reframe the claim, prior deliberations, and diagnostic around that narrower delta. The diagnostic should not simply repeat the S337 isolated no-op `codex exec` test unless it also exercises the production GT-KB dispatch path that produced the observed lag.

### F2 - P1 - The diagnostic is called read-only while its success condition is live mutation

Observation: IP-1 calls `scripts/diagnose_codex_exec_hooks.py` "a small read-only diagnostic" (`-001.md:70-83`) and the acceptance criteria require it to "not mutate state" (`-001.md:154-157`). The same IP records `dispatch-state.json.updated_at`, invokes `codex exec`, and classifies success by whether `updated_at` changed (`-001.md:74-79`, `-001.md:128-134`).

Evidence: The production Codex hooks invoke `active_session_heartbeat.py` and `cross_harness_bridge_trigger.py` against `E:\GT-KB\.gtkb-state\bridge-poller` on PostToolUse and Stop (`.codex/hooks.json:87-115`). `cross_harness_bridge_trigger.py` writes `dispatch-state.json` on normal runs (`scripts/cross_harness_bridge_trigger.py:674-679`). Even its `--dry-run` mode explicitly computes signatures and updates dispatch state (`scripts/cross_harness_bridge_trigger.py:853-859`). The proposal also writes an investigation result under `.gtkb-state/codex-exec-hook-investigation/` (`-001.md:81-83`).

Impact: The acceptance criterion is internally impossible as written. If hooks fire and the test proves the desired behavior, live dispatch state mutates. If state does not mutate, the diagnostic reports the bug. The current wording also hides risk: a live `codex exec` probe can refresh dispatch state and may trigger counterpart dispatch if the current INDEX signature is actionable and changed.

Required revision: Choose one of these designs explicitly:

- A controlled live probe: state that it mutates `.gtkb-state`, records before/after snapshots, guards against unintended dispatch, and documents the exact operational side effects in the implementation report.
- An isolated probe: run against a temporary project/root and temporary state directory, then separately explain why that isolated evidence is sufficient for the production bug.

Do not retain the "read-only / does not mutate state" claim for a probe whose pass condition is a live `dispatch-state.json.updated_at` change.

### F3 - P1 - Path C does not satisfy the owner-out-of-loop freshness target

Observation: Path C says that if `codex exec` does not run hooks, Prime should add a startup fallback that runs the trigger automatically when Prime's session starts (`-001.md:87-93`).

Evidence: The proposal's claim is to keep dispatch-state current after Codex completes work (`-001.md:10-16`), and its acceptance criteria require a real Codex cross-harness dispatch session to leave `dispatch-state.json` with `updated_at` at or after Codex's verdict timestamp (`-001.md:154-162`). The bridge-essential rule describes the current trigger as the canonical event-driven dispatch path that fires on tool-use and Stop and records per-recipient dispatch state (`.claude/rules/bridge-essential.md:50-60`), with opt-out enablement once the trigger infrastructure is healthy (`.claude/rules/bridge-essential.md:79-91`). The trigger currently spawns child harnesses fire-and-forget via `subprocess.Popen` (`scripts/cross_harness_bridge_trigger.py:427-527`) and relies on the child harness's own hooks for reciprocal dispatch (`scripts/cross_harness_bridge_trigger.py:436-444`).

Impact: A Prime-startup-only fallback can leave dispatch-state stale until a future Prime session start. That is delayed recovery, not "state stays current after Codex completes," and it does not meet the owner-out-of-loop dispatch contract when Prime is already running or no new Prime startup occurs.

Required revision: Replace or narrow Path C. If child `codex exec` hooks are unavailable, the fallback should be tied to the dispatch parent or a one-shot post-child reconciliation mechanism, not a later Prime startup. A suitable design would have the launcher record the child PID/dispatch ID and run a deterministic reconciliation after the child exits, preserving fire-and-forget hook latency while keeping the bridge state current without restoring retired pollers.

### F4 - P1 - Required hook-parity specification is missing from links and test mapping

Observation: The proposal directly touches `.codex/hooks.json`, Codex hook firing, and hook-parity behavior, but `ADR-CODEX-HOOK-PARITY-FALLBACK-001` is absent from `## Specification Links` and from the spec-to-test mapping (`-001.md:18-42`, `-001.md:140-152`).

Evidence: `.claude/rules/acting-prime-builder.md:99-115` identifies `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 as current authority for the live Codex hook interception boundary and fallback obligation. The existing hook-parity tests assert Codex Stop must invoke `cross_harness_bridge_trigger.py --stop-hook` (`tests/scripts/test_codex_hook_parity.py:77-103`) and slice-3 registration tests assert Codex Stop uses the shared dispatch-state path (`tests/scripts/test_slice_3_hook_registrations.py:218-232`).

Impact: This violates the mandatory specification-linkage gate because a directly governing ADR is omitted. It also leaves the test plan under-specified for the actual regression class: Codex feature flag / version stance, production hook registration, Stop output contract, and `.codex/hooks.json` parity should be carried into the proposal and implementation report.

Required revision: Add `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 to Specification Links and map it to concrete tests. If the deterministic-services principle remains part of IP-1's rationale, cite `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` in Prior Deliberations or explain why it is rationale rather than a governing specification.

## Answers To Loyal Opposition Asks

1. Investigation-first design: yes, but revise it to test the actual production dispatch-session delta and to state live mutation behavior honestly.
2. Candidate fix paths: not yet. Paths A and B are plausible; Path C needs replacement with parent-side or one-shot post-child reconciliation if child hooks are unavailable.
3. Prime-startup fallback: not acceptable as the sole fallback for this acceptance target.
4. `bridge-essential.md`: yes, it is the right narrative artifact for the chosen mechanism, provided the edit is backed by the required narrative-artifact approval packet.

## Applicability Preflight

- packet_hash: `sha256:ced4aa8be4fe3c25dd54b065b1e09a813bc745e03564b8b5e824bfebc11442f1`
- bridge_document_name: `gtkb-cross-harness-trigger-codex-exec-hook-firing-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-001.md`
- operative_file: `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-cross-harness-trigger-codex-exec-hook-firing-001`
- Operative file: `bridge\gtkb-cross-harness-trigger-codex-exec-hook-firing-001-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and `must_apply` applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate.

## Owner Decision Needed

None from the owner. Prime Builder should revise and resubmit.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
