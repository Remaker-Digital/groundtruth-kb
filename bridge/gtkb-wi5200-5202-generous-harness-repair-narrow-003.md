NEW

# WI-5200..5202 - Implementation Report: generous harness recovery and truthful H parity

bridge_kind: implementation_report
Document: gtkb-wi5200-5202-generous-harness-repair-narrow
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Codex, harness A)
Date: 2026-07-11 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f522a-849d-7d43-8c60-0afc829438a6
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder; owner-authorized governed implementation

Responds to GO: bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-002.md
Approved proposal: bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5200-5202-HARNESS-REPAIR-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5200
Related Work Items: WI-5201, WI-5202
Recommended commit type: fix(harness):

target_paths: [".api-harness/routing.toml", "config/agent-control/harness-capability-registry.toml", "scripts/cloud_harness_base.py", "scripts/alibaba_cloud_studio_harness.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/dispatcher_runtime.py", "scripts/harness_parity_phase2.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_lo_harness_turn_budget.py", "platform_tests/scripts/test_harness_parity_phase2.py", "platform_tests/scripts/test_check_harness_parity.py"]

implementation_scope: source, tests, governed runtime configuration, and parity evaluation
requires_verification: true
kb_mutation_in_scope: false

---

## Implementation Claim

The shared cloud-harness loop now treats a blank no-tool provider response as a
recoverable no-progress turn. It appends a corrective user turn, never appends
an empty assistant block, and continues inside the same overall envelope.
Nonblank final responses still return immediately. Overall turn exhaustion,
session timeout, repeated identical tool-loop detection, transport errors, and
guard denials remain nonzero fail-closed outcomes.

D/F/H now load validated routing values for provider-operation timeout,
distinct session timeout, and maximum turns. Explicit CLI values still win for
direct operator invocations. Dispatcher-spawned provider workers discard stale
registry runtime flags so governed routing is authoritative; this closes F's
legacy `--max-turns 200 --timeout 60 --session-timeout 5400` override without
mutating the generated registry. The dispatcher outer lifetime is 29,400
seconds for all active harnesses, longer than the 28,800-second provider
session by a 600-second completion margin.

The Phase 1 registry truthfully marks H unsupported for the one repo-local
managed-skill capability it cannot execute, rather than claiming a nonexistent
adapter. Phase 2 now recognizes H's real bridge, headless, hook, no-window,
provider, readiness, registry, and skill surfaces and separates durable receive
capability from temporary current eligibility.

## Implementation Gate Evidence

- GO work-intent claim row: `31202`, holder session
  `019f522a-849d-7d43-8c60-0afc829438a6`; extended deadline
  `2026-07-11T22:55:46Z`, grace `2026-07-11T23:05:46Z`.
- Implementation-start packet:
  `sha256:0fe2569f092d3027ae3f305d81ee32e61f689733736df67aefc0e9abca7a5f91`.
- Exact PAUTH:
  `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5200-5202-HARNESS-REPAIR-20260711`.
- Broad predecessor thread is latest `NO-ACTION`; no protected source edit was
  made under its quarantined GO.

## Exact Envelope Changes

| Harness | Before | After |
| --- | --- | --- |
| A | 5,400-second outer worker | 29,400-second outer worker |
| B | 3,600-second outer worker | 29,400-second outer worker |
| C | 3,600-second outer worker | 29,400-second outer worker |
| D | 200 turns; 3,600-second operation; derived 3,960-second outer worker | 600 turns; 900-second operation; 28,800-second session; 29,400-second outer worker |
| F | 200 turns; 60-second operation; 5,400-second session; 900-second outer worker | 600 turns; 900-second operation; 28,800-second session; 29,400-second outer worker |
| H | 40 effective turns; 240-second operation; 540-second session; 3,600-second generic outer worker | 600 turns; 900-second operation; 28,800-second session; 29,400-second outer worker |

Live profile evaluation returned A/B/C/F/H at 29,400 seconds from their
harness defaults and D at 29,400 seconds from
`routing.ollama.session_timeout_seconds` plus the 600-second margin.

## Specification Links

- `ADR-CLOUD-HARNESS-TEMPLATE-001`
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION` records
  authorization for WI-5200, WI-5201, WI-5202, generous initial envelopes,
  independent verification, and genuine H reproof.
- Mike explicitly required generous allowances because some normal models need
  400-plus turns and hundreds of tool actions. Envelope reductions are deferred
  until sufficient telemetry can distinguish true non-progress from slow work.
- No new owner decision is required by this report.

## Prior Deliberations

- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES`
- `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS`
- `DELIB-20260711-WI5198-BOUNDED-IMPLEMENTATION-AUTHORIZATION`
- `DELIB-202666172`
- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION`
- `bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-001.md`
- `bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-002.md`

## Specification-Derived Verification

| Governing surface | Executed evidence | Result |
| --- | --- | --- |
| Shared cloud runtime and Alibaba adoption | Cloud base, Alibaba, OpenRouter tests | Blank-to-correction-to-final, all-blank exhaustion, no empty assistant block, routing precedence, and H limits pass. |
| Ollama guard parity | Ollama and LO turn-budget tests | Distinct session routing and 600-turn behavior pass; mutating tool guard assertions remain green. |
| Central dispatcher | Dispatcher runtime tests | All active outer lifetimes are generous; D session derivation and F stale-flag stripping pass. |
| Harness onboarding truth | Phase 1/2 tests and live evaluators | Phase 1 has zero MISSING; H has zero release-blocking Phase 2 gaps. |
| Bridge and artifact governance | GO, claim, packet, staged target-path review | Role-correct chain and exact target scope preserved; no DB, registry, credential, or deployment mutation. |

## Commands Run And Results

1. `python -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_lo_harness_turn_budget.py platform_tests/scripts/test_harness_parity_phase2.py platform_tests/scripts/test_check_harness_parity.py -q --tb=short`
   - `378 passed in 23.39s`.
2. `python -m ruff check <14 scoped Python paths>`
   - `All checks passed!`
3. `python -m ruff format --check <14 scoped Python paths>`
   - `14 files already formatted`.
4. `python scripts/check_harness_parity.py --all --json`
   - Overall `WARN`: `PASS=302`, `DEGRADED=3`, `UNSUPPORTED=123`,
     `MISSING=0`, errors `0`.
5. `python scripts/harness_parity_phase2.py --format json --include-supported`
   - Overall fleet result remains honestly `FAIL` because suspended Goose/Cursor
     and nonblocking fleet gaps remain; H itself has all nine release-blocking
     dimensions `supported`, one nonblocking `event_source=needs_adapter`, and
     zero release-blocking gaps.
6. Live `worker_lifetime_profile` evaluation for A/B/C/D/F/H
   - Every active harness resolves to `29400` seconds; D retains routing timeout,
     session-timeout, source, and margin telemetry.

## Files Changed

- `.api-harness/routing.toml`
- `config/agent-control/harness-capability-registry.toml`
- `scripts/cloud_harness_base.py`
- `scripts/alibaba_cloud_studio_harness.py`
- `scripts/ollama_harness.py`
- `scripts/openrouter_harness.py`
- `scripts/dispatcher_runtime.py`
- `scripts/harness_parity_phase2.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_lo_harness_turn_budget.py`
- `platform_tests/scripts/test_harness_parity_phase2.py`
- `platform_tests/scripts/test_check_harness_parity.py`

The staged implementation is exactly these 16 paths: 515 insertions and 84
deletions. Only the three D/F/H routing tables are staged from the commingled
routing file, and only H's truthful capability block is staged from the
commingled capability registry. Unrelated TOML formatting, Goose routing, and
capability hash changes remain unstaged. The two Ollama Python files retain
their repository-existing CRLF blob convention; Ruff confirms their content is
clean even though `git diff --cached --check` reports CR as trailing whitespace
on newly added lines.

## Acceptance Criteria Status

- [x] Blank final responses recover through a user correction and preserve
  fail-closed overall exhaustion.
- [x] D/F/H consume 600-turn, 900-second operation, and 28,800-second session
  routing profiles.
- [x] Dispatcher workers cannot pre-empt those sessions before 29,400 seconds.
- [x] Direct CLI precedence remains intact; dispatcher stale overrides do not.
- [x] H parity evidence is truthful and has no release-blocking evaluator gap.
- [x] Config staging excludes unrelated pre-existing hunks.
- [ ] Independent Loyal Opposition reruns the mapped checks and publishes
  VERIFIED.
- [ ] After VERIFIED and focused commit, H performs the genuine dispatcher-only
  WI-5199 reproof and commits its reserved verdict; B/H routing is then restored
  to B=true/H=false.

## Risk And Rollback

The larger envelopes allow a truly unproductive worker to remain alive longer.
Concurrency caps, per-operation timeout, session deadline, max turns, repeated
tool-loop detection, tool guards, and dispatcher telemetry still bound the
risk. The focused staged patch can be reverted as one commit. Bridge evidence
remains append-only. No envelope should be reduced until retained telemetry
supports a data-based threshold.

## Loyal Opposition Asks

1. Rerun the 378-test scoped suite and Ruff checks.
2. Inspect blank recovery, routing precedence, dispatcher stale-flag stripping,
   exact before/after envelopes, H parity truth, and hunk-isolated staging.
3. Return VERIFIED only if the repair is sound. The later H functional proof is
   intentionally a separate WI-5199 post-VERIFIED obligation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
