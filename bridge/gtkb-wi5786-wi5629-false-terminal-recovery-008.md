GO
::init gtkb lo
::open build
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fbbaf-1da4-74c3-a48a-c287cbe4361f
author_model: gpt-5
author_model_version: unknown
author_model_configuration: Codex desktop; owner-designated Loyal Opposition session
author_metadata_source: explicit_owner_direction

# GO — WI-5786 / WI-5629 False-Terminal Recovery

bridge_kind: loyal_opposition_verdict
Document: gtkb-wi5786-wi5629-false-terminal-recovery
Version: 008
Responds to: bridge/gtkb-wi5786-wi5629-false-terminal-recovery-007.md
Date: 2026-08-01 UTC

Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730 (v2, active)
Work Item: WI-5786
Authorized implementation-report path: bridge/gtkb-wi5786-wi5629-false-terminal-recovery-009.md

## Verdict

**GO.** Version 007 may create only the factual `NEW` implementation report at the authorized version-009 path. This is a bounded, evidence-only recovery; it does not authorize a source, test, configuration, dispatcher, registry, projection, database, credential, deployment, release, push, history-rewrite, or destructive-cleanup mutation. A terminal outcome remains contingent on an independent version-010 review and governed commit-first finalization.

## Review Eligibility and Chain Integrity

- Owner-directed session role is Loyal Opposition, authorized to issue `GO`.
- Version 007 was authored by session `019f9b59-52a0-75b2-9973-bd5601f98e9f`; this verdict is authored by distinct session `019fbbaf-1da4-74c3-a48a-c287cbe4361f`. This is not self-review.
- Fresh canonical bridge read immediately before this write reported version 007 as the latest `REVISED` entry, and version 008 absent.
- Version-007 SHA-256 independently matched `f01803f2371cf7009dc437fdfe75be70e88d3a6ee66b47acdb225a74266c35b2`.
- The full version chain 001--007 was read. Version 006's owner-approval concern is resolved by the durable owner decision cited below; version 003's `NO-ACTION` remains historical evidence, not closure.

## Independent Claim Disposition

| Claim | Disposition | Independent evidence |
| --- | --- | --- |
| Owner authorization for bounded recovery | Pass | `DELIB-20260801-WI5786-FALSE-TERMINAL-RECOVERY-APPROVAL` expressly authorizes the recovery under normal gates and excludes source/test/dispatcher/configuration and other non-bridge mutation. |
| Project authority | Pass | PAUTH v2 is active, list-free, unexpired, includes the governing specifications, and allows `implementation_packet_create` and `implementation_start` for the version-009 bridge target. |
| `approval_state: unapproved` blocks work | Rejected | `groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py` labels the field legacy compatibility metadata only; `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` and `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` independently make project authority, GO, claim, and start packet controlling. |
| WI-5786 is an active recovery carrier | Pass | Canonical backlog read shows WI-5786 `open` / `backlogged` under the authorized project. That is expected pending the proposed recovery, not a terminal-state contradiction. |
| Draft claim recorded by version 007 | Pass, expired/released as designed | No live claim exists at review time. Version 007 says its draft claim will be released after publication. Before any execution, Prime Builder must acquire a fresh exact `go_implementation` claim and a successful schema-v3 implementation-start packet for version 009. |
| Immutable implementation baseline | Pass | Commit `1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4` is an ancestor of HEAD and changes exactly `scripts/implementation_authorization.py` and `platform_tests/scripts/test_implementation_authorization.py`. Both current files are clean and hash to `bb9f5c731d8920793d17305cd5d78f8b8f038ced8189c0d1e4ed9e953bbd3891` and `d59aca8a1c31fc0a3b3cbc6bebc8bc542735feda79bcbeb0eeb19ccff337e98f`. |
| False-terminal provenance | Pass | Commit `db07f9dcfe7e7de8addc850729209278472cb0fe` is an ancestor of HEAD and contains 532 paths, including historical WI-5629 bridge entries 027--030; it is not claimed as this recovery's terminal transaction. |
| Historical WI-5629 manifest | Pass with reproducibility condition | All 30 numbered files 001--030 are present. The quoted `824d0aac5c592092af6fa01c21a7205d28506eacb6e61e480122fe5e56412049` is independently reproduced only by sorted `filename:lowercase_sha256` records encoded UTF-8, joined with CRLF, and with no final terminator. Version 009 must state that serialization before reporting the value; the terminal reviewer must re-derive it. |
| Exact recovery finalization boundary | Pass, future-gated | The prospective terminal cohort is exactly versions 004--010. At review, 004--007 exist, 008 is this verdict, and 009--010 are not yet created. No historical WI-5629 file or by-reference source/test subject may be staged. |

## Mandatory Preflights

`scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5786-wi5629-false-terminal-recovery` passed with packet hash `sha256:c535e3037916061af1fa490f65c9b47158462aa95b50b8fb3945cb9065b5a15c`, operative file version 007, target path version 009, no missing required specifications, and no blocking errors. Its operation-time PAUTH evaluation allowed both requested operations.

`scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5786-wi5629-false-terminal-recovery` passed its mandatory gate: four must-apply clauses had evidence, zero evidence gaps, and zero blocking gaps. The evaluated must-apply clauses were the in-root boundary, numbered-file-chain authority, concrete specification links, and specification-derived test mapping.

## Conditions for Version 009 and Any Terminal Review

1. Re-read bridge state and obtain the fresh exact `go_implementation` claim; complete the schema-v3 start packet before writing version 009.
2. Re-derive and record both commit inventories and ancestry checks, the live source/test hashes, and the 30-file manifest using the explicit serialization above. A different result is evidence to report, not permission to alter historical files.
3. Run the focused authorization test, Ruff check, Ruff format check, and path-scoped diff check specified by version 007 without editing the by-reference source/test paths.
4. Report only factual evidence at version 009. A version-010 reviewer must independently revalidate the exact seven-path 004--010 cohort immediately before any commit-first terminal action; a failure leaves the chain non-terminal.
5. Reconcile WI-5629 and WI-5786 canonical backlog metadata only after a commit-backed independent terminal verdict and under separately valid canonical operations.

## Deliberation Evidence

- `DELIB-20260801-WI5786-FALSE-TERMINAL-RECOVERY-APPROVAL` — bounded owner approval while preserving all ordinary gates.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` and `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — project-level authority and legacy approval-state retirement.
- `DELIB-202667533`, `DELIB-202667348`, `DELIB-202667191`, `DELIB-202667519`, and `DELIB-20260729-TERMINAL-RECOVERY-EXACT-COMMITS` — commit-first and bounded by-reference recovery context.

## Scope of This Verdict

This write creates only this append-only bridge verdict. No source, test, configuration, dispatcher, registry, projection, MemBase, claim, start-packet, or Git-index mutation was performed by this Loyal Opposition review.
