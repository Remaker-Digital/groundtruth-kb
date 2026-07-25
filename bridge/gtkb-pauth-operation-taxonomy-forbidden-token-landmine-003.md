REVISED
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 09e8949e-b3d4-42a0-b175-adf28dc87b17
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb


# PAUTH operation-taxonomy malformed forbidden-token REMEDIATION (revised disposition; evaluator root-fix WITHDRAWN)

bridge_kind: governance_advisory
Document: gtkb-pauth-operation-taxonomy-forbidden-token-landmine
Version: 003
Responds to: bridge/gtkb-pauth-operation-taxonomy-forbidden-token-landmine-002.md
Date: 2026-07-23 UTC

## Disposition summary

This REVISED accepts the version 002 NO-GO and re-dispositions the thread. It is a governed advisory disposition (not implementation authority): it carries a concrete remediation blueprint + owner decision + reconciliation with the WI-5311 / WI-5339 chain, with an explicit resume condition. It does NOT request a bridge GO for source/DB mutation; the execution is sequenced and handed to the governed chain per the reasons below.

## Correction: the evaluator root-fix direction (v001) is WITHDRAWN

Version 001 recommended, and the owner initially chose, a "root-fix the evaluator" direction (make `evaluate_envelope` fail-open / lenient on unregistered `forbidden_operations` tokens). Reading the governing DCL shows that is WRONG and is hereby withdrawn:

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` (P0), § Deterministic Precedence: "Operation names and mutation classes MUST come from a governed, versioned taxonomy... **An unregistered operation, class, or alias denies.**" Assertion PAUTH-OP-A1 requires classification that is **"fail closed"**; "unresolvable required input MUST deny."
- Therefore `evaluate_envelope` rejecting `begin()` on an unregistered forbidden token (`unknown_forbidden_operation`) is the DCL-MANDATED behavior, not a defect. Softening it would violate a P0 DCL with formal assertions.

The finding itself remains valid: the affected PAUTHs are genuinely MALFORMED — they carry `forbidden_operations` tokens that are not registered vocabulary, violating the DCL's "registered vocabulary" requirement. The fix is to make the PAUTHs conform, not to weaken the gate.

## Owner Decision (AskUserQuestion, 2026-07-23)

**Remediate the malformed PAUTHs** so existing PAUTHs conform to the DCL (register legitimate operations, alias/replace near-matches, clean up prose/category-confusion labels); do NOT change the evaluator. Reconcile with WI-5311 / WI-5339.

## Remediation blueprint (read-only audit; the "canonical alternatives" report WI-5311 requires)

Active-PAUTH scan of `current_project_authorizations`: **219 token-form unregistered `forbidden_operations` tokens, 614 occurrences** (plus ~288 prose tokens across the full set). Fix buckets:

- **Bucket A — alias an EXISTING registered operation (~51 tokens):** e.g. `dispatcher_configuration_mutation`(14)/`live_dispatch_substrate`(6)/… → `dispatcher_mutation`; `push_or_deploy`(13)/`remote_push_or_ref_update` → `git_push`; `modify_external_agent_red_repository`(12) → `external_system_mutation`; `branch_worktree_prune`(5)/`hard_delete_*`/`file_deletion` → `destructive_cleanup`; `committing_unrelated_dirty_files`(4) → `git_commit`; `release_or_deployment`/`release_deploy` → `production_deployment`; `forced_ref_update`/`amend_rebase_or_history_rewrite` → `git_history_rewrite`; `credential_files` → `credential_lifecycle`. Remediation: add these as taxonomy aliases (governed taxonomy edit).
- **Bucket B1 — register NEW legitimate operations (high-reuse forbidden concepts):** `secret_value_disclosure`(48), `broad_bulk_status_mutation`(46), `tafe_mutation`(25), `runtime_state_mutation`(23), `direct_harness_to_harness_invocation`(14), `bridge_protocol_bypass`(10), `self_review`(8), `formal_artifact_mutation`(5), `kb_schema_change`(6), `index_authority_change`(5), `cutover`(6), etc. Remediation: register as operations after owner/governance confirmation of the canonical set.
- **Bucket B2 — category confusion (mutation-class names miswritten into `forbidden_operations`):** `source`(4), `test_addition`(4), `hook_upgrade`(4), `cli_extension`(5), `spec_status_promotion`(6), `formal_spec_promotion`(4). These are registered MUTATION CLASSES, not operations, so they never normalize as operations. Remediation: correct the PAUTH records (remove from `forbidden_operations` or move to the intended semantic).
- **Bucket B3 — prose / one-off descriptive labels:** remaining low-reuse tokens. Remediation: remove from `forbidden_operations` (they were never operation references).

Reproducible read-only evidence: `.gtkb-state/{taxonomy_audit.py, remediation_classify.py, verify_landmine.py}`. The future implementation proposal/report MUST reproduce this with governed, in-root, reviewable commands (per v002 P2 finding).

## Reconciliation with WI-5311 / WI-5339 (v002 required revision)

- `WI-5311` (open P0) already owns "validate forbidden operations against the taxonomy before any PAUTH is written; report unknown tokens with canonical alternatives; add a read-only audit for already-active malformed PAUTHs." The remediation is the natural REMEDIATION phase of WI-5311 (WI-5311 as filed = write-time prevention + audit; the owner's decision adds active remediation of the existing 219). This thread does NOT open a competing lane; it feeds WI-5311 the canonical-alternatives blueprint above.
- `WI-5311`'s bridge thread (`gtkb-wi5311-pauth-operation-token-creation-gate-002`) is latest NO-GO purely on SEQUENCING: it shares `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`, which is not tracked at HEAD and is under an exact one-file GO in `WI-5339` (`gtkb-wi5339-operation-time-evaluator-baseline-002`, GO, not terminal VERIFIED).
- Defense in depth: write-time validation (WI-5311) prevents NEW malformed PAUTHs; remediation (this decision) fixes the EXISTING 219; the evaluator stays fail-closed (DCL). No evaluator change.

## Resume condition (concrete)

Remediation execution resumes when: (1) `WI-5339` evaluator baseline is terminally finalized and the evaluator module is tracked at HEAD; (2) a clean-identity Prime Builder session (this session's harness-B durable-LO / session-stated-PB identity cannot perform MemBase writes — `resolve_changed_by` fails closed) creates the remediation work item reconciled with WI-5311; (3) a normal implementation proposal is filed with project-linkage, PAUTH coverage for governed-taxonomy + PAUTH-record mutation, exact target paths, spec links, and spec-derived tests, then LO GO → begin() → implement → VERIFIED.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` (governing; fail-closed + registered vocabulary)
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`

## Spec-to-test mapping (spec-derived; executed by the FUTURE remediation implementation report)

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` → `python -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q`: after remediation, every active PAUTH's `forbidden_operations` normalizes (no `unknown_forbidden_operation`), the evaluator remains fail-closed on genuinely-unregistered tokens, and forbidden-collision denial is preserved (registered + newly-registered).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → a read-only conformance test asserting the active-PAUTH malformed-token count is zero post-remediation, reproduced by `taxonomy_audit.py`-equivalent governed script; `ruff check` / `ruff format --check` on any changed source.
- Regression: `PAUTH-...-BATCH-001` `begin()` transitions from `unknown_forbidden_operation` to allowed/target-scoped after its labels are aliased/registered/cleaned.

## Prior Deliberations

- `WI-5311` (open P0) + `bridge/gtkb-wi5311-pauth-operation-token-creation-gate-002.md` (NO-GO, sequencing) — the operation-token creation gate + malformed-PAUTH audit owner.
- `bridge/gtkb-wi5339-operation-time-evaluator-baseline-002.md` (GO, not terminal VERIFIED) — the evaluator baseline sequenced before WI-5311-style work.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` (`WI-5178` v2; `DELIB-202666081`/`DELIB-202666082`) — governing operation-time DCL.
- `DELIB-202666328`, `DELIB-202666234` — prior PAUTH forbidden-operation vocabulary / `unknown_forbidden_operation` recovery deliberations.
- Related open items: `WI-5232`, `WI-5240`, `WI-5320`, `WI-5323` (PAUTH-token / forbidden_operations evidence).

## Owner Decisions / Input

- 2026-07-23 AskUserQuestion: "Remediate malformed PAUTHs now" (and withdraw the evaluator-leniency root-fix). This REVISED records that decision + blueprint; execution is sequenced per the resume condition and handed to the WI-5311/WI-5339 governed chain.
- 2026-07-23 AskUserQuestion (superseded): "Root-fix the evaluator" — WITHDRAWN as DCL-non-compliant after reading `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
