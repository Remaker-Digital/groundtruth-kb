NEW
::init gtkb lo
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f77f8-0931-75e2-a78d-7dea7037f743
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Report - WI-5629 Corrected-Chain Lifecycle Continuation

bridge_kind: implementation_report
Document: gtkb-wi5629-corrected-malformed-verdict-chain
Version: 021
Responds to: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-020.md
Approved proposal: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-019.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5629

target_paths: ["scripts/bridge_lifecycle_resolver.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Implementation Claim

The exact version 019 corrected-chain continuation is implemented. WI-5629
terminal functional readiness is claimed.

After the strict correction handshake, the resolver now:

1. preserves every physical numbered version in `audit_versions`;
2. removes only the malformed verdict and administrative `NO-ACTION` from
   logical transition evaluation;
3. delegates every later transition and public projection to the existing
   ordinary strict resolver;
4. preserves exactly the malformed path in `quarantined_paths`;
5. fails versions after corrected `VERIFIED` with the ordinary terminal code;
6. keeps `Responds to GO:` and decorated `Version:` compatibility rejected for
   the separate WI-5636 and WI-5637 lanes.

The public foundation chain now resolves through report/verdict state:

```json
{
  "audit_versions": [1, 2, 3, 4, 5, 6],
  "blocking_diagnostics": [],
  "implementation_artifact": 1,
  "implementation_verdict": 4,
  "latest_status": "NO-GO",
  "latest_version": 6,
  "quarantined_paths": [
    "bridge/gtkb-dispatcher-next-foundation-spike-002.md"
  ],
  "review_artifact": null
}
```

One static-formatting conflict is disclosed below. It is not in either file
changed by version 019: the v017-approved, v020-frozen authorization test has a
pre-existing LF block inside a CRLF file. Version 020 simultaneously requires
that exact hash remain unchanged and asks for a four-target Ruff format pass.
No mutation can satisfy both conditions. The changed resolver files pass Ruff
format, all 252 executable tests pass, and `git diff --check` exits zero.

## Files Changed

Changed by version 019:

- `scripts/bridge_lifecycle_resolver.py`
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`

Final SHA256:

- `scripts/bridge_lifecycle_resolver.py`:
  `9F9AAF48A0712F93DB778D0934E21CC344A00C433D690B07A9AC6981A768F1F1`
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`:
  `247731D41A7D54641E38A57DD41A77AF9B739993D8686902EFCC63B0C3CE0C40`

Verification-only files preserved byte-identical to v017/v020:

- `scripts/implementation_authorization.py`:
  `A13B6CDE9DEA029996E8E8B724C20BB71168C074078835894733BA55DDF07371`
- `platform_tests/scripts/test_implementation_authorization.py`:
  `D7C3597096175694F2DD442894954E6C5BF301F95A805E07E6EC152D3A4F18CB`

## Implementation Start Evidence

Fresh exact claim:

- row: `33657`
- session: `019f77f8-0931-75e2-a78d-7dea7037f743`
- acquired: `2026-07-19T14:34:42Z`
- claim kind: `go_implementation`
- extension used: one governed self-service extension
- implementation deadline: `2026-07-19T15:34:42Z`
- grace expiry: `2026-07-19T15:44:42Z`

Fresh schema-v3 implementation-start packet:

- created/finalized: `2026-07-19T14:35:24Z`
- packet hash:
  `sha256:f7390093b5529d1968d7d1652a41d5ee0bec3597c97124d4e94170c1fa87f94a`
- pre-start packet hash:
  `sha256:c8bab64a1e68e87b064c5c129a7da71aba70a86e591bca29de627ab347fe1f2e`
- normalized PAUTH envelope:
  `194E95A1B99DFD0B9238A0373769FAE29E1032DC13603F4177B5EE4F9755120D`
- evaluator SHA256:
  `5EAB50B26F0EAC3E99C1670007983D7DFFF071B758D062B215FBDDBF3379A9CA`
- taxonomy SHA256:
  `E726688AC19484CB1105EC4965C53F3F1CC4E6198E28F71D66D79838878387D8`
- create decision: `allowed`
- start decision: `allowed`
- exact classifications: two `source` and two `test` targets.

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

## Owner Decisions / Input

`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` remains controlling.
No waiver is requested. The formatting conflict is presented for independent
contract interpretation because version 020 itself freezes the only file Ruff
would normalize.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-017.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-018.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-019.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-020.md`
- `bridge/gtkb-wi5636-exact-responds-to-go-history-compatibility-002.md`

## Implementation Details

`_correction_resolution()` still performs the exact malformed-shape,
predecessor, `NO-ACTION`, corrected-status, and role checks. Pending correction
and completed corrections with no later version retain their existing
projections.

When later versions exist:

- corrected `VERIFIED` rejects the first later version as terminal drift;
- other corrected verdicts compose:
  `strict_prefix + corrected_verdict + later_strict_versions`;
- `_ordinary_resolution()` validates that logical sequence and computes the
  latest, review, and implementation views;
- the returned public resolution restores the full physical audit tuple and
  the single malformed-path quarantine.

No second transition table, fallback resolver, metadata alias, or compatibility
parser was introduced.

## Specification-Derived Verification Results

| Requirement | Executed command or proof | Observed result |
| --- | --- | --- |
| Existing and new corrected-chain behavior | `python -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py -q --tb=short --timeout=120` | PASS: 44 passed in 2.02s |
| Exact public continuation | Direct `resolve_bridge_lifecycle(..., "gtkb-dispatcher-next-foundation-spike")` read | PASS: v006 `NO-GO`, pair v001/v004, audit v001-v006, only v002 quarantined |
| Full authorization nonimpairment | `python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short --timeout=120` | PASS: 161 passed in 1213.59s; JUnit `.gtkb-state/wi5629-v020-implementation-authorization.junit.xml` |
| Work-intent nonimpairment | `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short --timeout=120` | PASS: 34 passed in 21.88s |
| Evaluator nonimpairment | `python -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short --timeout=120` | PASS: 13 passed in 0.17s |
| Static lint | `ruff check` on all four declared targets | PASS |
| Changed-file formatting | `ruff format --check` on resolver and resolver test | PASS: two files already formatted |
| Full declared-target formatting | `ruff format --check` on all four targets | FAIL: only frozen `test_implementation_authorization.py` would reformat |
| Syntax | `py_compile` on all four declared targets | PASS |
| Diff whitespace | `git diff --check --` on all four declared targets | PASS, exit 0; warning identifies the same frozen LF/CRLF baseline |
| Verification-only byte preservation | Final SHA256 comparison | PASS: both v017/v020 hashes exact |

The Ruff diff for the sole formatting finding changes only line endings on
lines 984-998 of the frozen test. It proposes no token or behavior change.

## Acceptance Criteria Status

- Exact public foundation through v006: PASS.
- Complete physical audit order: PASS.
- Single malformed-path quarantine: PASS.
- Ordinary strict resolver as sole post-correction authority: PASS.
- Review/implementation projections: PASS.
- Existing malformed-chain denials: PASS.
- WI-5636 and WI-5637 strict negative boundaries: PASS.
- Authorization target byte preservation: PASS.
- All executable regression and syntax/lint checks: PASS.
- Changed-file Ruff format: PASS.
- Four-target Ruff format: BASELINE CONFLICT, disclosed; v020 forbids the only
  normalizing mutation.
- Dispatcher/provider/harness/Git state mutation: NONE.
- MemBase/credential/deployment/release/external-system mutation: NONE.

WI-5629 terminal functional readiness is claimed. If the full-format baseline
conflict is treated as blocking, the next governed action is a format-only
revision that explicitly permits normalization of the already-declared
verification test; it is not a resolver or PAUTH redesign.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "before_behavior": "A corrected GO authorized the first implementation but the same thread became unreadable when its report and verdict were appended.",
  "after_behavior": "The correction handshake composes into the existing ordinary strict lifecycle; the full physical chain remains auditable and only the malformed verdict is quarantined.",
  "history_preservation": "No numbered bridge file is rewritten, renumbered, deleted, or normalized.",
  "separate_compatibility": "Responds-to-GO and decorated-Version behavior remains denied and separately owned by WI-5636 and WI-5637.",
  "nonimpairment": "Both authorization targets remain byte-identical; all 208 authorization/work-intent/evaluator tests pass in addition to 44 resolver tests.",
  "rollback": "Under fresh GO, claim, and start authority, reverse only the resolver and resolver-test hunks to their v020 hashes.",
  "fail_closed_conditions": [
    "The malformed version is missing, duplicated, wrong-shaped, or has the wrong predecessor.",
    "NO-ACTION or corrected verdict is missing, non-adjacent, wrong-status, or wrong-role.",
    "Any later strict metadata or ordinary transition is invalid.",
    "Any version follows terminal VERIFIED.",
    "Any change requires a target outside WI-5629's four-file boundary."
  ]
}
```

## Risks And Rollback

The shared resolver has broad read consumers. Risk is bounded by reusing the
ordinary resolver, preserving immutable public projections, and passing all 44
focused tests plus the 208 downstream authorization/work-intent/evaluator
tests.

Rollback before VERIFIED requires fresh governed claim/start authority and
restores only:

- resolver hash
  `0AEE86CFA377CAEDEDA7D57914891C63A2415F766FD4D93003EC8FBFC95C6854`;
- resolver-test hash
  `539894A7B406C3D9E76A43B7252F593BA93A75CAAC5C38E40A04D8F786E504A4`.

Preserve both authorization files, evaluator, taxonomy, public history,
WI-5636, WI-5637, and all foreign worktree bytes.

Recommended commit type: `fix`
