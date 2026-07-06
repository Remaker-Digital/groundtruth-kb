NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

# WI-3430/WI-3431 Env SoT Migration CLI Slice

bridge_kind: prime_proposal
Document: gtkb-wi3430-3431-env-sot-migration-cli-slice
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-05 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ENV-SOT-TOPOLOGY-ENV-SOT-TOPOLOGY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENV-SOT-TOPOLOGY
Work Item: WI-3430
Work Item: WI-3431

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/env_sot.py", "groundtruth-kb/tests/test_env_sot_cli.py", "platform_tests/groundtruth_kb/cli/test_env_sot_cli.py", "applications/Agent_Red/.env.local", "applications/Agent_Red/admin/shopify/.env.local", "applications/Agent_Red/admin/standalone/.env.local", "applications/Agent_Red/admin/provider/.env.local", ".env.local"]

implementation_scope: cli_extension/tests/local_env_migration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-3430 and WI-3431 are paired by the July 5 backlog disposition. The desired end state is one Agent Red application env source-of-truth at `applications/Agent_Red/.env.local`, generated per-admin app views under `applications/Agent_Red/admin/{shopify,standalone,provider}/.env.local`, and root `.env.local` retaining platform-level GT-KB values rather than mixing application-level Agent Red values.

Because `.env.local` files can contain credentials, this proposal makes the migration CLI-driven and test-first. Implementation should add a `gt env` migration/check surface that can classify, plan, dry-run, and apply the migration without printing secret values. The live local `.env.local` rewrite is included in the target envelope because it is the work item's terminal outcome, but it must preserve values opaquely, must not disclose secrets in logs or reports, and must not rotate credentials.

## Specification Links

- `ADR-ENV-SOT-TOPOLOGY-001` - GT-KB platform and hosted applications have separate env SoT artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the migration must preserve the platform/application boundary and keep Agent Red application env authority inside `applications/Agent_Red/`.
- `DCL-ENV-CLI-ENFORCEMENT-001` - per-application env views must be generated/enforced by CLI rather than maintained as independent SoTs.
- `GOV-ENV-LOCAL-AUTHORITY-001` - `.env.local` is owner-managed local credential/config authority; implementation must not serialize or disclose secret values.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation requires LO GO and numbered bridge evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, and WI metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all governing env and bridge specs are cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include tests derived from the env SoT specs.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH authorizes the bounded work but does not bypass LO GO or implementation-start authorization.
- `GOV-CREDENTIAL-SAFETY-001` and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - migration must preserve credential safety and inspect current live files rather than relying on stale inventory.

## Prior Deliberations

- `DELIB-S365-ENV-SOT-FORMALIZATION-TRACK` - owner selected formal ADR/DCL/GOV treatment for env SoT topology.
- `DELIB-S365-ENV-SOT-AGENT-RED-DEFERRAL` - Agent Red application-specific SoT layout was deferred until this scoped application migration work.
- `DELIB-S365-ENV-SOT-SINGLE-PER-APPLICATION-BINDING` - supports single SoT per application.
- `DELIB-S365-ENV-SOT-PROJECT-AUTHORIZATION-PATH` - created the dedicated env SoT project path.
- `DELIB-20265586` and `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner authorized continuing the remaining paired WI-3430/WI-3431 implementation work.
- `bridge/gtkb-env-sot-topology-spec-authoring-010.md` - VERIFIED env SoT formalization thread.

## Owner Decisions / Input

No additional owner decision is required for LO review of the CLI/test implementation plan. The project authorization includes WI-3430 and WI-3431.

However, implementation must not rotate, reveal, or invent credential values. If live apply finds ambiguous key ownership that cannot be classified by rules or tests, Prime Builder must fail closed and report the ambiguity rather than asking for secret values in chat.

## Requirement Sufficiency

Existing requirements are mostly sufficient for the CLI and migration behavior. The proposal explicitly narrows the implementation strategy:

- Add deterministic env classification and generation.
- Use dry-run and apply modes.
- Preserve values as opaque strings.
- Do not print secret values.
- Fail closed on ambiguous ownership.

No new specification is needed unless LO determines that live local env file rewriting requires a narrower credential-safety DCL before implementation.

## Proposed Implementation

1. Add `groundtruth_kb.env_sot` helpers to parse dotenv-style files while preserving comments, ordering where practical, and opaque values.
2. Add a `gt env` CLI surface in `groundtruth-kb/src/groundtruth_kb/cli.py` with at least:
   - `gt env plan --app agent-red` to show counts/classification without values;
   - `gt env check --app agent-red` to fail when multiple SoT-class app env files exist;
   - `gt env migrate --app agent-red --dry-run` to report planned moves/generation without mutation;
   - `gt env migrate --app agent-red --apply` to perform the local migration after GO.
3. Classify platform-level keys versus Agent Red application-level keys with explicit allowlists/prefix rules, tested against synthetic fixtures. Unknown or ambiguous keys fail closed in apply mode.
4. Generate admin app `.env.local` views from `applications/Agent_Red/.env.local` rather than treating the three admin files as independent SoTs.
5. When applying to live files, preserve values opaquely and do not echo them in stdout, bridge reports, tests, or logs.
6. Add tests for parsing, classification, dry-run redaction, generated view content, ambiguous-key failure, and idempotent apply on fixture trees.
7. If GO explicitly allows live local env migration, run the apply mode once and report only path/count/hash-style evidence, never raw values.

## Spec-Derived Verification Plan

| Governing surface | Required behavior | Verification |
| --- | --- | --- |
| `ADR-ENV-SOT-TOPOLOGY-001` | Platform and application env SoTs are separate. | Tests assert platform keys remain in root fixture and application keys move to app fixture. |
| `DCL-ENV-CLI-ENFORCEMENT-001` | Per-admin app env files are generated views, not independent SoTs. | Tests assert generated admin views derive from app SoT and are idempotent. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Values are owner-managed and must not be disclosed or fabricated. | Tests assert dry-run/apply output redacts values and fail closed on ambiguous keys. |
| `GOV-CREDENTIAL-SAFETY-001` | No secret values appear in output/report evidence. | Verification captures stdout/stderr and asserts synthetic secret values are absent. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | LO can verify with executed tests. | Implementation report includes pytest plus ruff command evidence. |

Minimum verification after GO:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_env_sot_cli.py platform_tests/groundtruth_kb/cli/test_env_sot_cli.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/env_sot.py groundtruth-kb/tests/test_env_sot_cli.py platform_tests/groundtruth_kb/cli/test_env_sot_cli.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/env_sot.py groundtruth-kb/tests/test_env_sot_cli.py platform_tests/groundtruth_kb/cli/test_env_sot_cli.py
```

Live apply evidence, if performed, must be limited to filenames, key counts, non-secret hashes, and idempotency checks.

## Acceptance Criteria

- `gt env plan/check/migrate` exists for the Agent Red env SoT topology.
- Dry-run output never prints secret values.
- Fixture tests prove platform keys and application keys are separated correctly.
- Fixture tests prove admin app env files are generated views from the application SoT.
- Ambiguous ownership fails closed before live apply.
- Live apply, if included in implementation, leaves root `.env.local` as platform-level and `applications/Agent_Red/.env.local` as the Agent Red application SoT.
- No credential rotation, external upload, production deployment, or secret disclosure occurs.

## Risk / Rollback

Risk is high because live `.env.local` files may contain owner-managed credentials. Mitigation: tests first, dry-run first, opaque value preservation, no secret output, fail-closed ambiguity handling, and optional live apply only inside the GO-approved envelope. Rollback is restoring the pre-apply env files from the local worktree/backup copy created by the migration command; the command must not delete original values without a recovery path.

## Bridge Filing

This proposal is filed as the paired WI-3430/WI-3431 implementation path. It does not revise the already VERIFIED env SoT formalization thread.

## Recommended Commit Type

`feat:` because the primary implementation adds a new governed env migration CLI.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
