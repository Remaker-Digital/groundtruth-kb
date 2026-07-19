NO-GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 82426707-5f90-4ee3-9784-5300a804159e
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

bridge_kind: lo_verdict
Document: gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch
Version: 002 (NO-GO review of NEW 001)
Responds to: bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-001.md
Reviewer role: loyal-opposition (interactive session-stated via ::init gtkb lo)

# NO-GO — WI-5446 Ollama/D DeepSeek V4 Flash route switch

## Verdict Summary

NO-GO. The proposal is substantively well-built and genuinely owner-authorized,
but its **declared mutation surface exceeds the authorization granted by its
cited PAUTH**. The proposal declares `kb_mutation_in_scope: true` and lists two
`target_paths` — `groundtruth.db` and `harness-state/harness-registry.json` —
whose canonical operation-time mutation classes (`metadata` and `runtime_state`)
are not within `PAUTH-PROJECT-GTKB-OLLAMA-DIRECT-CLOUD-HARNESS-WI5446-DEEPSEEK-FLASH-20260717`'s
`allowed_mutation_classes: ["config", "source", "test"]`. The precedent this
proposal explicitly mirrors (WI-5047) was authorized by a PAUTH that granted the
matching classes (`generated_projection`, `membase_record`, `governance_evidence`);
WI-5446's PAUTH is a regression from that pattern.

This is an authorization-envelope-consistency NO-GO, not a defect in the change's
intent. The model swap itself is sound and owner-approved.

## What Verified (positive confirmations)

1. **Owner authorization is real.** `DELIB-202666767` confirmed in the
   Deliberation Archive as the owner decision ("switch D reviewer model to the
   DeepSeek V4 flash tier via governed bridge"). The cited PAUTH is
   `status: active`, active-check `True`, `owner_decision_deliberation_id:
   DELIB-202666767`, `included_work_item_ids: ["WI-5446"]`, no expiry;
   `scope_summary` matches the proposal.
2. **Both mandatory gates PASS.** Applicability preflight `preflight_passed:
   true`, `missing_required_specs: []`; clause preflight exit `0`, 0 blocking
   gaps (sections reproduced below).
3. **Premise verified against live config.** `.api-harness/routing.toml`
   confirms D's current route is `kimi-k2-7-code-cloud`
   (`[routing.ollama].default_model` + all three skill routes). The flagged
   provider-confusion risk is real — `[models.deepseek-v4-flash]` already exists
   bound to provider `openrouter` — and the proposal correctly avoids a TOML key
   collision by using the distinct key `deepseek-v4-flash-cloud`. Model-existence
   risk (`deepseek-v4-flash:cloud` resolving on the Ollama cloud endpoint) is
   appropriately deferred to the readiness probe in the verification plan.
4. **WI-5446 is a real tracked defect** whose backlog description independently
   corroborates the motivation (D/kimi emits governance-non-compliant VERIFIED
   bodies; C handles the same VERIFY class cleanly).
5. **Review independence holds.** Proposal author session
   `2d31ebb3-7f0c-4987-94a1-d56cd7a388ed` (prime-builder/claude) differs from
   this reviewer's session context. Same harness ID (B) alone is not a review
   boundary per `.claude/rules/file-bridge-protocol.md` § Review Independence.

## Blocking Finding [P1] — Declared mutation surface exceeds PAUTH allowed_mutation_classes

**Claim.** The proposal's `target_paths` + `kb_mutation_in_scope: true` declare a
mutation surface the cited PAUTH does not authorize by mutation class.

**Evidence.** Running the canonical operation-time classifier
(`groundtruth_kb.governance.project_authorization_operation_time.classify_target`
+ `mutation_class_families`) against each declared target under both PAUTHs:

| target_path | operation-time class | WI-5446 PAUTH {config, source, test} | WI-5047 PAUTH (cited precedent) |
| --- | --- | --- | --- |
| `.api-harness/routing.toml` | `configuration` | OK | OK |
| `config/dispatcher/rules.toml` | `configuration` | OK | OK |
| `platform_tests/scripts/test_verify_ollama_dispatch.py` | `test` | OK | OK |
| `groundtruth-kb/tests/test_doctor_ollama.py` | `test` | OK | OK |
| `harness-state/harness-registry.json` | `runtime_state` | **DENY** | OK (`generated_projection`) |
| `groundtruth.db` | `metadata` | **DENY** | DENY* |

- WI-5446 PAUTH `allowed_mutation_classes` (raw) = `["config", "source", "test"]`
  -> families `{configuration, source, test}`.
- WI-5047 PAUTH `allowed_mutation_classes` (raw) =
  `["config", "test", "generated_projection", "membase_record", "governance_evidence"]`
  -> families `{configuration, governance_evidence, runtime_state, test}`.
- The proposal additionally declares `kb_mutation_in_scope: true`, but the
  WI-5446 PAUTH grants **no** knowledge-base mutation class. The WI-5047 PAUTH
  backed the identical `kb_mutation_in_scope: true` declaration with
  `membase_record` + `governance_evidence`.

(*`groundtruth.db` -> `metadata` is denied even under WI-5047's broader PAUTH, and
WI-5047 still listed it — so the `groundtruth.db` line reflects a broader
tolerated target_paths convention rather than a WI-5446-specific defect. The
**specific, precedent-backed deltas** are the uncovered `runtime_state` target
`harness-state/harness-registry.json` and the unbacked `kb_mutation_in_scope: true`.)

**Impact.** The authorization of record (the PAUTH) does not cover the declared
implementation scope. The operation-time authority enforcement being wired under
WI-5178 classifies these targets into classes the PAUTH excludes; the mismatch
is latent now but will surface at verification (and at operation-time enforcement
once fully wired), and it leaves an audit inconsistency: a proposal declaring KB
mutation under an authorization that grants none.

**Recommended action (either path resolves the NO-GO):**

1. **(Recommended) Amend the PAUTH** to align `allowed_mutation_classes` with its
   own `scope_summary` (which explicitly authorizes repointing D's headless argv
   and dispatcher label) and the WI-5047 precedent: add `generated_projection`
   (authorizes `harness-state/harness-registry.json`) and a KB-mutation class
   (`membase_record` / `governance_evidence`) to back `kb_mutation_in_scope:
   true`. Create the new PAUTH version via `gt projects`, then refile REVISED
   citing the amended PAUTH.
2. **Or narrow the declared scope.** If the registry/dispatcher/DB writes occur
   solely through governed CLIs (`gt harness set-invocation-surface`, `gt bridge
   dispatch`) that are exempt from the implementation-start gate and produce no
   direct edits to those paths, set `kb_mutation_in_scope: false` and reduce
   `target_paths` to `[".api-harness/routing.toml", "config/dispatcher/rules.toml",
   "platform_tests/scripts/test_verify_ollama_dispatch.py",
   "groundtruth-kb/tests/test_doctor_ollama.py"]` — all within the current PAUTH's
   `{config, source, test}`.

## Secondary Findings (non-blocking)

- **[P3] Leftover template placeholder** (lines 92–94). The
  `### Helper-suggested candidates` subsection still contains the literal
  `_No prior deliberations: <fill in reason before filing>._`. This does NOT
  independently trigger the Prior-Deliberations NO-GO obligation (the main
  `## Prior Deliberations` section is substantively populated with five
  author-supplied entries), but the unfilled placeholder should be removed in
  the REVISED.
- **[P3] Commit type `chore`.** Acceptable and justified per the WI-5047
  precedent (config-only route selection, no capability surface). `fix:` would
  also be arguable since it remediates defect WI-5446, but the declared-and-
  justified discipline is satisfied — no change required.

## Prime Builder Remediation Context

| Element | Detail |
| --- | --- |
| Objective | Make the declared implementation scope consistent with the owner authorization before implementation. |
| Preconditions | Owner decision `DELIB-202666767` and the active PAUTH already exist. |
| Evidence paths | `bridge/gtkb-wi5446-...-001.md` (target_paths line 22, `kb_mutation_in_scope` line 27); `bridge/gtkb-wi5047-...-001.md` (precedent target_paths); PAUTH records in MemBase. |
| Remediation sequence | (Path 1) `gt projects` amend PAUTH `allowed_mutation_classes` -> refile REVISED citing the new version; OR (Path 2) narrow `target_paths` + set `kb_mutation_in_scope: false` -> refile REVISED. Remove the line 92–94 placeholder in either case. |
| Verification | Re-run both preflights on the REVISED; confirm `classify_target` on every declared target resolves to a class in the (possibly amended) PAUTH's allowed families. |
| Open decisions | Whether the registry/dispatcher/DB writes are governed-CLI-only (Path 2) or genuinely in scope as declared targets (Path 1). Path 1 matches the WI-5047 precedent and preserves honest disclosure of the touched surface. |

## Prior Deliberations

- `DELIB-202666767` — owner decision authorizing the swap to DeepSeek V4 Flash
  via the governed bridge path (verified present in the Deliberation Archive; the
  authorizing decision for this proposal). Not in dispute.
- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` — prior owner decision switching D
  to the current kimi route; superseded by `DELIB-202666767` for future D
  dispatch.
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` — earlier owner decision pinning D
  to DeepSeek V4 Pro; historical. This proposal returns D to the DeepSeek family
  at the flash tier.
- `bridge/gtkb-wi5047-ollama-kimi-k2-7-code-cloud-route-switch-001.md` — the
  immediate precedent whose target_paths + `kb_mutation_in_scope: true` this
  proposal mirrors; its PAUTH (`PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5047-OLLAMA-KIMI-K2-7-CLOUD-20260706`)
  granted the `generated_projection` / `membase_record` / `governance_evidence`
  classes this NO-GO cites as the correct scope. (Thread latest status:
  `WITHDRAWN`.)

## Applicability Preflight

- packet_hash: `sha256:873b8b13747058042c21eb8cf56a68cad9f1ac3312a3dc27bb5ccf30e7f15bdf`
- bridge_document_name: `gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5446-ollama-d-deepseek-v4-flash-route-switch-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

(Advisory specs `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` all cited.)

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code: `0` (pass)

| Clause | Applicability | Evidence found | Severity |
|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | — | blocking |

Neither preflight is the basis for this NO-GO; both pass. The blocker is the
PAUTH mutation-class / declared-scope inconsistency above.

## Methodology Trail

- Read: proposal `-001`; `.api-harness/routing.toml`; `project_authorization_operation_time.py` (classifier lines 163–217, `evaluate_envelope` 258–328); `implementation_authorization.py` (validation path 1092–1153, 2176–2212); WI-5047 `-001`.
- Ran: `bridge_applicability_preflight.py`, `adr_dcl_clause_preflight.py`, `gt deliberations search`, `gt backlog list` (WI-5446), `classify_target`/`mutation_class_families` against both PAUTHs, `get_project_authorization` + `is_project_authorization_active` for both PAUTHs.
