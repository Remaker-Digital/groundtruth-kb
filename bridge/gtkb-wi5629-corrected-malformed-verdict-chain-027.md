REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6f8b-9fd7-7142-93a8-5696dca44d85
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; owner-declared role via ::init gtkb pb; governed implementation proposal revision; approval_policy=never
author_metadata_source: explicit current-session bridge filing metadata

# Revised Implementation Proposal - WI-5629 Current-Baseline Format Normalization

bridge_kind: prime_proposal
Document: gtkb-wi5629-corrected-malformed-verdict-chain
Version: 027
Responds to: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-026.md
Date: 2026-07-21 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5629

target_paths: ["platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Resolve the live WI-5629 terminal blocker on the current repository baseline.

Version 026 withheld terminal verification because protected-commit finalization could not yet use transaction-local VERIFIED evidence for a same-transaction protected path set. That blocker is now resolved by the independent WI-5633 terminal verdict `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-018.md`, committed at `ef6ba79c`.

However, the current repository baseline no longer matches the old v023/v024 hash ledger. Later shared-chain commits changed `scripts/implementation_authorization.py` and `platform_tests/scripts/test_implementation_authorization.py`. A fresh current-baseline check shows the approved WI-5629 target again fails Ruff format only because it contains bare-LF line endings inside otherwise CRLF content. This proposal supersedes the stale v023/v024 hash and line-number ledger for the current baseline, while preserving the same one-file target and the same behavior-preserving format-only intent.

The requested mutation is restricted to running Ruff formatting on only `platform_tests/scripts/test_implementation_authorization.py`. No Python token, assertion, fixture, import, function signature, test order, text content, source file, resolver test, dispatcher configuration, routing configuration, MemBase, Git ref/index operation, credential, release, deployment, or external-system mutation is in scope.

## Finding Addressed

### F1 - Version 026 finalization blocker is resolved, but current target format is red

Version 026's protected-commit finalization blocker is answered by WI-5633 VERIFIED evidence:

- latest WI-5633 bridge state: `VERIFIED`
- terminal verdict: `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-018.md`
- finalization commit: `ef6ba79c`
- commit subject: `docs(bridge): verify WI-5633 protected commit evidence`

Current WI-5629 terminal readiness still needs one approved-target format correction before a new implementation report can honestly ask for VERIFIED. The current target file has:

```json
{
  "path": "platform_tests/scripts/test_implementation_authorization.py",
  "sha256": "E54418ADAE6A3FCB4AECD31AD66C375A5A9DD9FA6DB624303CE557194C002F44",
  "normalized_sha256": "EBF4495598397F2B736206995F6BEB4A0CD2A835532B4B49B43EF1E9A1E0CD6D",
  "bytes": 135492,
  "crlf": 2974,
  "lf": 2998,
  "bare_lf": 24
}
```

Current Ruff format evidence:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts\bridge_lifecycle_resolver.py scripts\implementation_authorization.py platform_tests\scripts\test_bridge_lifecycle_resolver.py platform_tests\scripts\test_implementation_authorization.py
# FAIL: Would reformat: platform_tests\scripts\test_implementation_authorization.py
# 1 file would be reformatted, 3 files already formatted
```

Current Ruff diff is line-ending-only in two hunks:

```text
@@ -336,20 +336,20 @@
@@ -1039,11 +1039,11 @@
```

The displayed text content in those hunks is unchanged; Ruff is converting LF-only lines to CRLF to match the file's convention.

## Scope And Boundaries

In scope:

- acquire a fresh GO-implementation claim after independent GO;
- create a fresh implementation-start packet for only `platform_tests/scripts/test_implementation_authorization.py`;
- recheck the current pre-normalization hash `E54418ADAE6A3FCB4AECD31AD66C375A5A9DD9FA6DB624303CE557194C002F44`;
- run Ruff formatting only on `platform_tests/scripts/test_implementation_authorization.py`;
- prove the resulting diff is line-ending-only and confined to the current Ruff-proposed hunks;
- rerun the WI-5629 verification matrix against the current baseline;
- file a fresh implementation report with current hashes and finalization payload stated unambiguously.

Out of scope:

- changes to `scripts/bridge_lifecycle_resolver.py`;
- changes to `platform_tests/scripts/test_bridge_lifecycle_resolver.py`;
- changes to `scripts/implementation_authorization.py`;
- changes to `scripts/check_protected_commit_authorization.py`;
- changes to `platform_tests/scripts/test_check_protected_commit_authorization.py`;
- WI-5633 source/test changes;
- WI-5636 `Responds to GO:` compatibility;
- WI-5637 decorated `Version:` compatibility;
- WI-5474 finalization;
- dispatcher configuration/runtime, capacity, ranking, routing, or claims;
- provider routing, bridge writer/provider behavior, harness registry/state, MemBase, Git refs, credentials, deployment, release, or external systems.

Read-only verification dependencies:

- `scripts/bridge_lifecycle_resolver.py`;
- `scripts/implementation_authorization.py`;
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`;
- `scripts/check_protected_commit_authorization.py`;
- `platform_tests/scripts/test_check_protected_commit_authorization.py`;
- `platform_tests/scripts/test_bridge_work_intent_registry.py`;
- `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`;
- `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-018.md`.

## Requirement Sufficiency

Existing requirements are sufficient. This proposal is a current-baseline correction under the already approved WI-5629 objective and the now-verified WI-5633 prerequisite. It does not change bridge lifecycle semantics, project authorization policy, or protected-commit authorization behavior.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-VERIFIED-BRIDGE-HISTORY-001`

## Owner Decisions / Input

`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` remains controlling. Active `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719` version 4 includes WI-5629 and permits test mutation after independent GO, exact claim, and implementation-start authorization. No waiver or additional owner decision is required.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS`
- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-023.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-024.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-025.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-026.md`
- `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-018.md`
- `bridge/gtkb-wi5636-exact-responds-to-go-history-compatibility-002.md`
- `bridge/gtkb-wi5637-bounded-decorated-version-history-compatibility-002.md`

## Current Baseline Evidence

Live bridge state:

- WI-5629 latest: `NO-GO` at `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-026.md`
- WI-5633 latest: `VERIFIED` at `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-018.md`

Current frozen read-only hashes:

| Path | SHA-256 |
| --- | --- |
| `scripts/bridge_lifecycle_resolver.py` | `9f9aaf48a0712f93db778d0934e21cc344a00c433d690b07a9ac6981a768f1f1` |
| `scripts/implementation_authorization.py` | `067b5774fd54449d97783811a8c5e856dc1cd8f5eaacb06370f8914e6acdd25d` |
| `platform_tests/scripts/test_bridge_lifecycle_resolver.py` | `247731d41a7d54641e38a57dd41a77af9b739993d8686902efcc63b0c3ce0c40` |
| `platform_tests/scripts/test_implementation_authorization.py` | `e54418adae6a3fcb4aecd31ad66c375a5a9dd9fa6db624303ce557194c002f44` |
| `scripts/check_protected_commit_authorization.py` | `2b750d9a790de41bb474c046fc846d8018671fa786d30252c1cd6078cf7e1736` |
| `platform_tests/scripts/test_check_protected_commit_authorization.py` | `8e6571b5f2113a6a13aa33e130ee97f78bbb07754838d63c28cc723c3e95f456` |

Current focused git status over the WI-5629 target/dependency set produced no output before this proposal; there are no uncommitted source/test bytes yet.

## Proposed Implementation

1. After independent GO, release any draft claim and acquire a fresh GO-implementation claim.
2. Run:
   `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5629-corrected-malformed-verdict-chain --session-id 019f6f8b-9fd7-7142-93a8-5696dca44d85 --expires-minutes 120`
3. Confirm the implementation-start packet authorizes only `platform_tests/scripts/test_implementation_authorization.py`.
4. Confirm the target preimage hash is still `E54418ADAE6A3FCB4AECD31AD66C375A5A9DD9FA6DB624303CE557194C002F44`.
5. Run:
   `E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe format platform_tests\scripts\test_implementation_authorization.py`
6. Prove the resulting normalized-text hash is unchanged and the only byte-level effect is converting the 24 bare-LF endings in the current Ruff hunks to CRLF.
7. Run the full verification matrix below.
8. File a fresh implementation report. Its `Files Changed` section must avoid the WI-5633 over-claiming trap: list actual changed implementation/report payload only, and put unchanged dependency/config paths in non-claimed evidence.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5629 v026 NO-GO plus WI-5633 VERIFIED finalization support at bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-018.md",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
  "primary_route": "Fresh REVISED proposal -> independent GO -> exact GO-implementation claim -> implementation-start packet -> one-file Ruff normalization -> fresh verification matrix -> implementation report -> independent VERIFIED",
  "before_behavior": "WI-5633 terminal support is available, but the current WI-5629 approved target has 24 bare-LF endings and fails the required Ruff format gate.",
  "after_behavior": "The approved target has consistent line endings, while Python tokens and runtime behavior remain unchanged.",
  "behavior_change": "none",
  "self_descriptive_naming": "No code identifiers or test names change; the proposal name states current-baseline format normalization.",
  "obsolete_guidance_disposition": "The stale v023/v024 hash and line-number ledger is superseded only for current-baseline evidence; the one-file format-only scope remains operative.",
  "history_preservation": "All numbered bridge files remain append-only, and WI-5633 terminal evidence is preserved by reference rather than rewritten.",
  "authorized_mutation": "Ruff line-ending normalization only in platform_tests/scripts/test_implementation_authorization.py",
  "baseline": {
    "wi5633_state": "VERIFIED at bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-018.md",
    "target_hash": "E54418ADAE6A3FCB4AECD31AD66C375A5A9DD9FA6DB624303CE557194C002F44",
    "normalized_text_hash": "EBF4495598397F2B736206995F6BEB4A0CD2A835532B4B49B43EF1E9A1E0CD6D",
    "bare_lf": 24,
    "ruff_format": "red for platform_tests/scripts/test_implementation_authorization.py only"
  },
  "expected_result": {
    "target_bare_lf": 0,
    "normalized_text_hash": "EBF4495598397F2B736206995F6BEB4A0CD2A835532B4B49B43EF1E9A1E0CD6D",
    "ruff_format": "green across the WI-5629 verification target set",
    "behavior": "unchanged"
  },
  "hard_invariants": [
    "Only platform_tests/scripts/test_implementation_authorization.py may change.",
    "The normalized text hash remains EBF4495598397F2B736206995F6BEB4A0CD2A835532B4B49B43EF1E9A1E0CD6D.",
    "The target bare-LF count moves from 24 to 0.",
    "All executable and static-quality checks pass after normalization.",
    "Dispatcher, routing, harness, MemBase, credential, deployment, release, and unrelated Git state remain untouched."
  ],
  "separate_ownership": "WI-5633 is terminal and read-only here; WI-5636, WI-5637, WI-5474, dispatcher/provider, and harness surfaces remain separate.",
  "essential_context_preservation": "Preserve WI-5629 v001-v027 history, the v026 finalization blocker, WI-5633 v018 VERIFIED evidence, PAUTH-DISPATCHER-NEXT-PROGRAM-20260719, and the current hash ledger.",
  "rollback": "Under fresh governed claim/start authority, restore only the target file's pre-normalization hash E54418ADAE6A3FCB4AECD31AD66C375A5A9DD9FA6DB624303CE557194C002F44 and rerun the same matrix.",
  "fail_closed_conditions": [
    "The preimage hash differs before mutation.",
    "Ruff proposes any non-line-ending text change.",
    "Any path outside the approved target changes.",
    "Any verification command fails.",
    "Any dispatcher/config/routing path changes."
  ]
}
```

## Specification-Derived Verification Plan

| Requirement | Command or proof | Acceptance predicate |
| --- | --- | --- |
| Exact format-only scope | Pre/post normalized SHA-256 comparison, line-ending counts, and `ruff format --diff`/`git diff` inspection | Normalized text unchanged; only the approved target file changes; only LF-to-CRLF line endings change in Ruff-proposed hunks. |
| Corrected-chain behavior | `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py -q --tb=short --timeout=120` | Resolver tests pass. |
| Authorization nonimpairment | `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short --timeout=120` | Implementation-authorization tests pass. |
| Work-intent nonimpairment | `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short --timeout=120` | Work-intent tests pass. |
| Operation-time evaluator nonimpairment | `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short --timeout=120` | Operation-time evaluator tests pass. |
| WI-5633 protected-commit prerequisite | `gt bridge show gtkb-wi5633-protected-commit-corrected-chain-evidence --json --compact` and `git show --name-only ef6ba79c --` | WI-5633 remains VERIFIED and commit `ef6ba79c` contains the terminal WI-5633 bridge artifacts. |
| Static lint | `E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe check scripts/bridge_lifecycle_resolver.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py` | PASS. |
| Static format | `E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/bridge_lifecycle_resolver.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py` | PASS after formatting the approved target. |
| Syntax | `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m py_compile scripts/bridge_lifecycle_resolver.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py` | PASS. |
| Whitespace | `git diff --check -- scripts/bridge_lifecycle_resolver.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py` | PASS. |
| Dispatcher/config nonimpairment | Focused `git status --short -- .api-harness/routing.toml .claude/settings.json config/dispatcher/rules.toml config/agent-control/harness-capability-registry.toml` | No output. |

## Acceptance Criteria

- The only mutated protected implementation path is `platform_tests/scripts/test_implementation_authorization.py`.
- The preimage hash matches `E54418ADAE6A3FCB4AECD31AD66C375A5A9DD9FA6DB624303CE557194C002F44`.
- The normalized text hash remains `EBF4495598397F2B736206995F6BEB4A0CD2A835532B4B49B43EF1E9A1E0CD6D`.
- The target's bare-LF count goes from 24 to 0.
- Python tokens, assertions, fixtures, signatures, imports, ordering, and behavior remain unchanged.
- All listed executable and static-quality checks pass.
- WI-5633 remains terminal VERIFIED at `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-018.md`.
- No dispatcher/routing/config, provider, harness, MemBase, credential, deployment, release, external-system, or unrelated Git operation occurs.

## Pre-Filing Preflight

Before filing this proposal, Prime Builder runs:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5629-corrected-malformed-verdict-chain --content-file .tmp\bridge-revisions\gtkb-wi5629-corrected-malformed-verdict-chain-027.candidate.md --json
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5629-corrected-malformed-verdict-chain --content-file .tmp\bridge-revisions\gtkb-wi5629-corrected-malformed-verdict-chain-027.candidate.md
```

Filing is valid only if applicability has no missing required/advisory specs or blocking errors, and the clause preflight reports zero blocking gaps.

## Risks And Rollback

Risk: formatting could include a token-level change. Mitigation: compare normalized hashes and inspect the diff before reporting implementation complete.

Risk: current-baseline reconciliation could accidentally hide stale v025 evidence. Mitigation: this proposal names the current hashes, cites the intervening WI-5633 terminal commit, and requires fresh post-format verification.

Rollback before VERIFIED requires fresh governed claim/start authority and restores only the test's current pre-normalization hash `E54418ADAE6A3FCB4AECD31AD66C375A5A9DD9FA6DB624303CE557194C002F44`.

## Recommended Commit Type

`test`

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
