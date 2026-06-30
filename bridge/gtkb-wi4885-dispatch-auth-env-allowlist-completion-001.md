NEW

# WI-4885 Dispatch Auth Env Allowlist Completion

bridge_kind: prime_proposal
Document: gtkb-wi4885-dispatch-auth-env-allowlist-completion
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-29 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4885

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_dispatch_env_local_auth_loader.py"]

implementation_scope: source, tests, dispatcher-runtime
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Complete the dispatcher worker credential allowlist so every harness-auth credential that may be required by a dispatcher-spawned worker is eligible for injection from `E:\GT-KB\.env.local` using the existing setdefault semantics. The immediate defect is that `OLLAMA_API_KEY` is present in `.env.local`, but `scripts/dispatcher_runtime.py` does not include it in `DISPATCH_AUTH_ENV_KEYS`.

The current local Ollama endpoint passes readiness without this key, so this is not the observed cause of the current Ollama result. It is still a release-blocking parity defect because the dispatcher should not silently omit a harness credential key when the owner has provided it in the canonical local credential file. This proposal authorizes adding `OLLAMA_API_KEY` to the dispatcher allowlist and expanding the focused regression tests so future harness credential keys cannot be accidentally excluded.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `scripts/dispatcher_runtime.py` is protected dispatcher source and requires live bridge approval before mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal links the implementation to the governing WI/project/PAUTH and exact target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal includes Project Authorization, Project, Work Item, and inline JSON `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report must carry the verification commands below for Loyal Opposition review.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — dispatcher-spawned workers must receive the centralized runtime environment required to execute selected harness work.
- `GOV-AUTOMATION-VALUE-VS-COST-001` — missing credentials create wasteful failed or retrying dispatches; the allowlist must be deterministic and low-noise.
- `GOV-ENV-LOCAL-AUTHORITY-001` — `.env.local` is the local credential authority for transient harness credentials and must be consumed without logging secret values.

## Prior Deliberations

- `INTAKE-f8bc08a3` — Intake: Dispatcher/Bridge CLI as primary mutating UI for GT-KB artifact operations
- `DELIB-20266276` — daemon-resilience program scope-lock and full-topology release-readiness authority.
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` — owner directive that all harnesses are live, unwaived, and must be dispatchable to the maximum extent each harness allows.
- `bridge/gtkb-wi4885-dispatch-topology-activation-repair-001.md` — active repair proposal that exposed the credential propagation question while verifying Cursor and provider dispatch readiness.

## Owner Decisions / Input

No new owner decision is required before Loyal Opposition review. The owner explicitly corrected the premise on 2026-06-29: `OLLAMA_API_KEY` should not be excluded from dispatcher credential priming without a reason. The existing harness-parity and dispatcher-release directives already require all harnesses to be made dispatchable and tested before release.

## Requirement Sufficiency

Existing requirements sufficient.

`WI-4885`, `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION`, `DELIB-20266276`, `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE`, and the owner's 2026-06-29 correction are sufficient to implement this allowlist completion slice.

## Spec-Derived Verification Plan

| Specification | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-ENV-LOCAL-AUTHORITY-001` | `python -m pytest platform_tests/scripts/test_dispatch_env_local_auth_loader.py -q --tb=short` | The auth env loader forwards every allowlisted harness credential key from `.env.local`, including `OLLAMA_API_KEY`, without forwarding unrelated secrets. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short -k env_local` | Dispatcher worker spawn env receives all allowlisted harness credentials through the centralized runtime path. |
| `GOV-AUTOMATION-VALUE-VS-COST-001` | `python scripts/verify_ollama_dispatch.py --recipient D --readiness-only --json` | Ollama readiness remains deterministic; missing allowlist coverage cannot become an avoidable auth-failure retry loop. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report quotes the exact command outputs above. | Loyal Opposition can verify the change against this table. |

```text
python -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatch_env_local_auth_loader.py
python -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatch_env_local_auth_loader.py
```

## Risk / Rollback

Risk: `OLLAMA_API_KEY` may be unused by the current local endpoint. Mitigation: setdefault injection is harmless when unused and prevents future false auth failures if the endpoint or provider mode requires it.

Risk: broadening the allowlist could accidentally forward unrelated secrets. Mitigation: the implementation is a single named key addition plus tests that unrelated `.env.local` keys remain excluded.

Rollback: revert the single implementation commit. Dispatcher workers then return to the prior allowlist behavior; no database migration or topology rollback is required.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4885-dispatch-auth-env-allowlist-completion`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix:

The expected diff fixes a dispatcher credential-propagation omission discovered during release-blocking harness parity verification.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
