NEW

# Dispatch repair: load .env.local auth credentials into the headless-worker spawn env (WI-4707)

bridge_kind: implementation_proposal
Document: gtkb-wi4707-dispatch-credential-loader
Version: 001 (NEW)
Recommended commit type: fix:

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 6f5bd1b5-1bca-4b08-8e9f-f8e684a62d12
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4707-HEADLESS-CLAUDE-DISPATCH-CREDENTIAL-LOADER
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4707

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_dispatch_env_local_auth_loader.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Problem / Diagnosis

Headless `claude -p` workers spawned by the cross-harness dispatch fail with HTTP 401 "Invalid authentication credentials" (the 26 Prime-B failures that tripped the circuit breaker). Root cause confirmed (2026-06-20):

- The Claude OAuth access token in `~/.claude/.credentials.json` expired 2026-06-19T11:47:26Z.
- Interactive Claude refreshes that token in-memory via the refresh token, so the interactive session keeps working; but headless `claude -p` dispatch spawns read the expired access token and do not refresh it -> 401.
- The spawn already inherits the full parent env (`env = dict(os.environ)` at `scripts/cross_harness_bridge_trigger.py:2795`), but neither the Claude Code session nor the trigger loads `.env.local`, and `CLAUDE_CODE_OAUTH_TOKEN` / `ANTHROPIC_API_KEY` are unset. So the spawn has no durable token to fall back to.

The durable fix (owner AUQ, 2026-06-20) is a long-lived `CLAUDE_CODE_OAUTH_TOKEN` (minted by the owner via `claude setup-token`) placed in `.env.local` (the env source-of-truth per `GOV-ENV-LOCAL-AUTHORITY-001`). This proposal is the in-repo plumbing: make the dispatch trigger load that token from `.env.local` into the headless-worker spawn env.

## Proposed Change

In `scripts/cross_harness_bridge_trigger.py`, after the spawn env is built (`env = dict(os.environ)` in `_spawn_harness`), inject an allowlist of harness auth credentials read from `.env.local`:

1. Define a module constant `DISPATCH_AUTH_ENV_KEYS = ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")`.
2. Read `.env.local` once via the existing shared loader `scripts/_env.py::load_env_local(check_only=True)` (returns a dict, no `os.environ` side effects), wrapped in a defensive try/except so a missing/unreadable `.env.local` never blocks a spawn.
3. For each key in `DISPATCH_AUTH_ENV_KEYS`: if `.env.local` defines a non-empty value AND `env.get(key)` is empty (setdefault semantics), set `env[key] = <value>`. Never override a value already present in `os.environ`; never inject keys outside the allowlist (so unrelated `.env.local` secrets never leak into the worker).
4. Never log credential values (only key names / presence may be logged).

Effect: once the owner places `CLAUDE_CODE_OAUTH_TOKEN` in `.env.local`, headless `claude` workers receive it in their env and authenticate with the durable token instead of the expired session token.

This is the in-repo half of the fix; the owner separately mints the token and adds it to `.env.local` (credential lifecycle is the owner's). The code change is necessary-but-not-sufficient on its own and harmless when the key is absent (no-op).

## Specification Links

- `GOV-ENV-LOCAL-AUTHORITY-001` - the env source-of-truth governance this fix honors: the durable credential lives in `.env.local`; this loader reads it.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs this bridge filing and the numbered-file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization / Project / Work Item metadata present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping in the verification plan below.
- `GOV-STANDING-BACKLOG-001` - WI-4707 is the governed backlog item for this work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files are under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory); `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory); `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).

## Owner Decisions / Input

- AskUserQuestion (2026-06-20): owner selected ".env.local + I add the loader" for the WI-4707 headless-Claude 401: the owner mints `CLAUDE_CODE_OAUTH_TOKEN` via `claude setup-token` and adds it to `.env.local`; Prime Builder implements the dispatch loader. Recorded as `DELIB-S20260620-WI4707-CREDENTIAL-LOADER-AUTH` (source_type=owner_conversation, outcome=owner_decision) and authorized by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4707-HEADLESS-CLAUDE-DISPATCH-CREDENTIAL-LOADER` (bounded source/test scope).

## Prior Deliberations

- `DELIB-S20260620-WI4707-CREDENTIAL-LOADER-AUTH` - the owner-decision authorization for this work item.
- Deliberation search `gt deliberations search "dispatch spawn env credential .env.local headless worker authentication" --limit 5` returned no directly-governing prior decision on dispatch credential loading (closest matches were unrelated role-authority/sessionstart verdicts); this proposal does not revisit a previously-rejected approach.
- `bridge/gtkb-wi4703-dispatch-non-transient-fast-trip-001.md` - sibling dispatch-resilience work (WI-4703); see Dependency Disposition.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20265277` — seed=search; bridge_thread; Loyal Opposition Review - Closure of Duplicate Fail-Soft Registry Thread
- DA: `DELIB-0738` — seed=search; bridge_thread; Bridge thread: gtkb-credential-patterns-canonical (10 versions, VERIFIED)
- DA: `DELIB-20263272` — seed=search; bridge_thread; Loyal Opposition GO Verdict: WI-4480 Dispatch-Starvation Telemetry
- DA: `DELIB-1185` — seed=search; bridge_thread; Bridge thread: gtkb-credential-patterns-canonical (10 versions, ORPHAN)
- DA: `DELIB-20265336` — seed=search; bridge_thread; Verdict

## Dependency Disposition (WI-4703)

WI-4707 was filed with `depends_on: [WI-4703]`, but the two are independent, complementary slices and neither blocks the other:

- WI-4703 (fast-trip breaker) stops the dispatcher from WASTING spawns on non-transient failures (including this 401). It is correctness-of-resilience.
- WI-4707 (this item) RESTORES headless Claude dispatch by giving the spawn a valid durable token. It is correctness-of-auth.

They touch the same file (`scripts/cross_harness_bridge_trigger.py`) in different regions (WI-4703 in the failure-classification/breaker logic ~L193-3203; WI-4707 in `_spawn_harness` env construction ~L2795) and can land in either order. This proposal proceeds independently; it does not require WI-4703 to land first.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-ENV-LOCAL-AUTHORITY-001` is the governing requirement (the env SoT); this proposal derives a concrete loader behavior from it. No new specification is required before implementation.

## Specification-Derived Verification Plan

New unit tests in `platform_tests/scripts/test_dispatch_env_local_auth_loader.py` (spec-to-test mapping):

| Specification / behavior | Test | Expected |
| --- | --- | --- |
| `GOV-ENV-LOCAL-AUTHORITY-001` - durable token in .env.local reaches the spawn | build the spawn env with a temp `.env.local` defining `CLAUDE_CODE_OAUTH_TOKEN` and no such key in `os.environ` | spawn env contains `CLAUDE_CODE_OAUTH_TOKEN` with the .env.local value |
| Setdefault: never override existing env | `os.environ` already has `CLAUDE_CODE_OAUTH_TOKEN`; `.env.local` has a different value | spawn env keeps the `os.environ` value (no override) |
| Allowlist scoping: no unrelated leakage | `.env.local` defines a non-allowlisted secret key | that key is NOT injected into the spawn env |
| Robustness: missing/unreadable .env.local | no `.env.local` present | loader is a no-op; spawn env construction succeeds; no exception |
| No credential logging | inspect the loader code path | credential VALUES never written to logs/stdout (only key names) |

Commands: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatch_env_local_auth_loader.py -q --tb=short`; regression `... -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q`; `ruff check` + `ruff format --check` on changed files.

## Risk And Rollback

- Risk: injecting a wrong/stale token. Mitigation: setdefault semantics never override an explicit `os.environ` value; the owner controls the `.env.local` value; an absent key is a clean no-op.
- Risk: credential leakage into logs. Mitigation: allowlist-only injection, no value logging; tests assert no unrelated keys are injected.
- Risk: `.env.local` read failure blocks spawns. Mitigation: defensive try/except so any loader error degrades to "no injection," never a failed spawn.
- Rollback: revert the single source commit; the new test file is additive. No state migration; no schema change.

## Acceptance Criteria

- [ ] `DISPATCH_AUTH_ENV_KEYS` allowlist added; `.env.local` auth values injected into the spawn env via `scripts/_env.py` with setdefault semantics.
- [ ] Existing `os.environ` auth values are never overridden; non-allowlisted `.env.local` keys are never injected.
- [ ] Missing/unreadable `.env.local` is a safe no-op (no exception, spawn proceeds).
- [ ] No credential values are logged.
- [ ] New unit tests pass; existing `test_cross_harness_bridge_trigger.py` regression passes; ruff check + format clean.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
