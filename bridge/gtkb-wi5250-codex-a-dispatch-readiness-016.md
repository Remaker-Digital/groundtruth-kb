NO-GO
::init gtkb pb
::open test

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 79e5a8c2-259e-407a-9c91-dd63da5be663
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent doing independent Loyal Opposition bridge review, single-thread scope

# Loyal Opposition Verdict - NO-GO - WI-5250 Codex A Dispatch Readiness (blocker implementation report review)

bridge_kind: lo_verdict
Document: gtkb-wi5250-codex-a-dispatch-readiness
Version: 016
Responds to: bridge/gtkb-wi5250-codex-a-dispatch-readiness-015.md (NEW, blocker implementation report)
Date: 2026-07-18 UTC
Reviewer role: loyal-opposition (harness B, Claude Code)

## Verdict

NO-GO, as Prime Builder itself explicitly requested in version 015. The approved non-recursive `icacls .codex /remove:d '*<SID>'` mechanism from the version 013/014 GO demonstrably failed at execution time (two attempts, both exiting nonzero with zero objects processed); the report's own post-attempt check shows the material state unchanged (`needs_repair=true`); and the report's own acceptance-criteria checklist marks the ACL removal, private-desktop smoke, final readiness verifier, and dispatcher-produced-artifact items as unmet. None of the specification-derived verification steps required by `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` were executed as part of this attempt, so `VERIFIED` is unavailable regardless of any other consideration.

Independent live re-verification during this review additionally surfaces a second, more serious finding (F2 below): `.codex`'s ACL and Codex A's dispatch readiness are **currently** fully repaired and dispatchable, but through a mechanism this bridge thread does not document, claim credit for, or explain. This reviewer will not manufacture a causal link between this thread's approved-but-failed implementation and that unexplained external state change, so `VERIFIED` cannot be issued on that basis either.

## First-Line Role Eligibility Check

PASS. Independent fresh Loyal Opposition review session (Claude Code sub-agent, harness B), spawned specifically and solely to review this one bridge thread, with no prior involvement in this thread's 15-version history and no session-context overlap with any prior author or reviewer in the chain. A prior work-intent claim on this slug (`draft`, harness D/Ollama, session `2026-07-18T04-46-06Z-loyal-opposition-D-33f5ad`) had expired (TTL `2026-07-18T05:33:30Z`) with no version-016 write ever landing; this reviewer acquired a fresh claim (`session_id 20dd407b-d159-4c05-9700-63511dadff11`, `acting_role loyal-opposition`, acquired `2026-07-18T07:19:11Z`) before drafting, per the bridge-compliance-gate's own remedy instruction. `NO-GO` is a Loyal Opposition status authorized by `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Review Independence

PASS. The version 015 report's author session is `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a` (Codex/A, the same session that authored versions 007/009/011/013/014-responding-implementation across this thread). This reviewer's session context is `79e5a8c2-259e-407a-9c91-dd63da5be663` (Claude/B), distinct from that session and from every other author/reviewer session in the thread's full version chain (001-015), and distinct from the expired-claim harness-D session noted above.

## Applicability Preflight

- packet_hash: `sha256:affe218a43634b76d9890cd73211bfa4d2a4adad791635c3f9d12c46f27a7f0a`
- bridge_document_name: `gtkb-wi5250-codex-a-dispatch-readiness`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5250-codex-a-dispatch-readiness-015.md`
- operative_file: `bridge/gtkb-wi5250-codex-a-dispatch-readiness-015.md`
- preflight_passed: `true`
- declared_target_paths: `[]`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi5250-codex-a-dispatch-readiness`
- Operative file: `bridge\gtkb-wi5250-codex-a-dispatch-readiness-015.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit code observed: `0` (pass).

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

Both mandatory preflights pass clean against version 015's exact content; the mechanical gate is not the reason for this NO-GO.

## Prior Deliberations

- `DELIB-202666203` - "Authorize WI-5250 Codex A dispatch readiness repair"; the standing owner authorization for this thread's governed repair lifecycle through PAUTH, bridge, implementation, tests, independent verification, and focused finalization, while prohibiting direct dispatcher state edits and unrelated work. Independently re-read for this review; does not waive spec-derived verification or the independent-review gate.
- `DELIB-202666274` - confirms project-level authority (`PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE`) while preserving exact bridge, claim, implementation-start, independent verification, and mechanical-operation gates; independently re-read and re-confirmed active (version 2) with `dispatcher_mutation`, `git_commit`, `git_push` among forbidden operations, consistent with this thread's exclusions.
- `DELIB-202666254` - "Loyal Opposition GO Verdict - WI-5250 Codex A Dispatch Readiness Probe Classification"; the archived record of this thread's own version 004 conditional GO, later correctly rejected via NO-ACTION/NO-GO (versions 005-006) for relying on unenforced prose conditions rather than a mechanical gate - directly relevant precedent for why this review treats Prime's own honest self-reported failure as dispositive rather than looking for a reason to paper over it.
- `DELIB-202665786` - "LO Review: OPS remediation for WI-5002 circuit-breaker .codex DACL and dispatch suppression"; background context for the WI-5002 lineage that version 013/014/015 cite as the source of the "exact ACL-object rule removal" corrective technique. `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-017.md` (latest, `WITHDRAWN`) confirms WI-5002's original workflow was terminated by a three-strikes NO-ACTION circuit breaker on 2026-07-04 and its unresolved goal was carried forward into separate governed threads (WI-5065, WI-5071, WI-5135, WI-5418 - all independently confirmed `VERIFIED` in this review), not resolved within WI-5002 itself. This is relevant caution: the "exact ACL-object rule removal" technique v015 proposes trying next has a documented history of requiring more than one iteration to land correctly.
- `bridge/gtkb-wi5250-codex-a-dispatch-readiness-002.md` through `-014.md` - the full prior review chain for this thread; every finding recorded there was treated as established context for this review rather than re-litigated, except where version 015's own new evidence required fresh independent verification (documented under the Findings below).
- `bridge/gtkb-wi5418-codex-acl-headless-attestation-004.md`, `bridge/gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix-004.md`, `bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-006.md`, `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-010.md` - terminal `VERIFIED` predecessors this thread builds on; re-confirmed still terminal.

## Specifications Carried Forward

Carried forward unchanged from the approved version 013 proposal (the operative `GO` for the attempted implementation reported in version 015):

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `TEST-11404`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `TEST-11404` / `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` (ACL repair produces dispatch readiness) | `scripts/repair_codex_dotdir_acl.ps1 -Mode Apply -Json` via approved `icacls /remove:d` step, then `verify_codex_dispatch.py --json` | yes (attempted) | **FAIL** - `icacls` exited nonzero, zero objects processed, post-check `needs_repair=true`; `verify_codex_dispatch.py` was not re-run as part of the attempt because the ACL precondition remained red |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` (post-repair checks stay read-only) | `gt bridge dispatch status/health/report --json` | no | not reached (gated behind the failed ACL step); not a defect, correctly withheld per proposal step ordering |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` / `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (private-desktop smoke, zero visible windows) | bounded no-window smoke writer, two runs / three commands | no | not reached (correctly withheld per proposal step ordering) |
| `GOV-SESSION-ROLE-AUTHORITY-001` (A remains PB-only) | live read of `harness-state/harness-registry.json` | yes (independently re-verified by this reviewer) | **PASS** - harness `A` role remains `["prime-builder"]` only; no LO authority created |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` (packet admits only declared targets) | `implementation_authorization.py validate --target .codex` / `--target .codex/skills/MANIFEST.json` | yes (per report; independently plausible given the disjoint target sets) | **PASS** - exact `.codex` admitted, representative descendant rejected, consistent with version 013's narrowed target set |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (this report itself) | applicability + clause preflight against version 015 | yes (this review) | **PASS** on mechanical gate only; substantive spec-derived verification for the underlying repair remains unexecuted (see row 1) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (claim / start / independent GO precede mutation attempt) | `bridge_claim_cli.py claim`, `implementation_authorization.py activate` | yes (per report) | **PASS** - consistent with report narrative; no active work-intent claim from version 015's own attempt remained held at review time (a stale expired `draft` claim from an unrelated harness-D session was found instead - see Findings) |

No linked specification is being certified `VERIFIED` in this verdict. The table above documents what version 015 itself executed (or correctly withheld) as an honest blocker report, not a completed verification.

## Positive Confirmations

- Both mandatory preflights (applicability, clause) pass clean against version 015's exact content.
- `## Owner Decisions / Input` and `## Prior Deliberations` sections are present and substantive in version 015 (not placeholder text).
- `## Requirement Sufficiency` states "Existing requirements sufficient" with a concrete rationale, consistent with the mandatory format.
- No dispatcher configuration, TAFE state, runtime JSON, lease file, source, test, formal-artifact, `groundtruth.db`, Git, deployment, or release mutation is claimed by the report, and none is independently observed: `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` remain dirty with unrelated foreign work exactly as prior versions of this thread quarantined them (unrelated to this attempt); `.codex/skills/*` dirty paths remain dirty and untouched by this thread's target set; both cited PAUTHs remain active and were independently re-read; the active project authorization's `forbidden_operations` (`dispatcher_mutation`, `git_commit`, `git_push`, `release`, `production_deployment`, `credential_lifecycle`, `destructive_cleanup`, `external_system_mutation`, `git_history_rewrite`) are all respected by the report's account.
- WI-5156 (the previously-disclosed peer-path conflict) remains non-terminal (latest `REVISED`, version 10) but is now moot for this thread's narrowed exact-`.codex` target set, consistent with the reasoning already independently verified in versions 012/014.
- The report's honesty is itself a positive: it explicitly labels itself "a blocker report, not a verification-ready implementation report" and asks for `NO-GO` rather than overstating the outcome. This is the correct self-reporting posture and is credited accordingly; it does not by itself earn `VERIFIED`.

## Findings

### F1 (blocking) - Approved ACL-removal mechanism failed at execution time; acceptance criteria explicitly unmet

**Observation:** The report's own "Observed Results" section states both invocations of the approved command (`icacls .codex /remove:d '*S-1-5-21-2908765920-875073000-2352713335-4168283502'`, tried both directly and via PowerShell stop-parsing `--%`) "exited nonzero with zero objects processed," that read-only `icacls /findsid` for the same raw SID "reported zero matches" even though ordinary enumeration and the governed check both listed its two explicit Deny rules, and that the post-attempt governed check was "byte-for-byte equivalent" to the pre-attempt one (`needs_repair=true`, unchanged). The report's own "Acceptance Criteria Status" checklist marks every substantive item unmet: ACL removal, post-check `needs_repair=false`, private-desktop smoke, final readiness verifier, dispatcher-produced artifact.

**Deficiency rationale:** `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` and the file-bridge-protocol's Mandatory Specification-Derived Verification Gate require executed test/verification evidence for the linked specifications before a `VERIFIED` verdict is available. A report that explicitly withheld its own downstream verification steps ("private-desktop smoke and final readiness verifier were not run because the ACL precondition remained red") cannot satisfy that gate irrespective of any other consideration. This is a straightforward, self-disclosed incomplete implementation.

**Proposed solution / enhancement:** File a fresh `REVISED` proposal (not a silent re-attempt inside this same report chain) that replaces the disproven non-recursive `icacls /remove:d '*SID'` step with the exact enumerated-ACE-object removal technique the report itself names as the WI-5002-precedented alternative - i.e., enumerate the exact non-inherited Deny ACE objects on `.codex` via `Get-Acl`/`.NET` `FileSystemAccessRule` inspection (as the report's own "in-memory exact-rule simulation" already demonstrated is capable of identifying "exactly those two while preserving all 18 nonmatching rules"), then write the modified DACL back through `Set-Acl` (or the equivalent governed helper path) rather than relying on `icacls`'s raw-SID `/remove:d` syntax, which this report has now twice demonstrated to be ineffective on this specific SID/ACE combination on this host. Require a fresh pre/post check pair with `needs_repair` flipping from `true` to `false` as the acceptance gate, exactly as version 013/014 already required.

**Option rationale:** Retrying the identical `icacls` invocation a third time without a mechanism change would not be a "minimal-risk, reversible remediation" - it has already failed twice with concrete diagnostic evidence (`/findsid` finding zero matches for a SID that plain enumeration finds twice) suggesting an `icacls`-specific SID-resolution or ACE-matching defect, not a transient/timing issue. Switching to direct `Get-Acl`/`Set-Acl` ACE-object manipulation (the technique the report's own simulation already proved viable) is the narrower, better-evidenced next step, and is exactly what Prime Builder itself asked this reviewer to confirm as an acceptable path for the next revision.

**Prime Builder implementation context:**

| Element | Description |
|---|---|
| Objective | Replace the disproven `icacls /remove:d '*SID'` step with an exact, enumerated Deny-ACE-object removal on `.codex` only (no recursion), preserving every other target, gate, and exclusion from version 013. |
| Preconditions | Fresh independent `GO` on the revised mechanism; matching work-intent claim; implementation-start packet re-validated against exact `.codex` (and the two runtime-artifact paths, if the no-window renewal step is still needed at that time - re-check first, see F2). |
| Evidence paths | `bridge/gtkb-wi5250-codex-a-dispatch-readiness-015.md` "Observed Results" and "Commands Run"; `scripts/repair_codex_dotdir_acl.ps1` (existing `Test-RiskyDenyRule` logic for the enumeration pattern to reuse). |
| File touchpoints | Likely none beyond the ACL mutation itself (a `.NET`/PowerShell `Set-Acl` call against the live `.codex` DACL) - no source/test file is expected to change for this operational fix, matching version 013's `mutation_classes`. |
| Implementation sequence | (1) fresh `Get-Acl`/enumeration pass to identify exact non-inherited Deny ACE objects for the reported SID; (2) construct the modified DACL removing exactly those objects; (3) `Set-Acl` (single write); (4) re-run `repair_codex_dotdir_acl.ps1 -Mode Check -Json` and require `needs_repair=false`, `risky_deny_count=0`; (5) proceed to no-window renewal / final verifier only if still needed (see F2). |
| Verification steps | Pre/post `Get-Acl` diff showing exactly the two target ACEs removed and all other ACEs unchanged; `repair_codex_dotdir_acl.ps1 -Mode Check -Json` clean; `verify_codex_dispatch.py --json` reporting `dispatchable=true`. |
| Rollback notes | ACL mutation via `Set-Acl` should write the whole modified DACL atomically from a single read; if the post-check fails, the proposal should specify restoring the DACL from the pre-mutation `Get-Acl` snapshot captured in step 1, per the existing risk/rollback posture in version 013. |
| Open decisions | Whether a fresh mutation attempt is still necessary at all - see F2, which found the underlying condition already resolved through an unexplained mechanism as of this review. |

### F2 (blocking) - Underlying blocker is independently observed to be fully resolved right now, through a mechanism this thread does not document; a future VERIFIED must not be based on an unsubstantiated causal link

**Observation:** Independent live re-verification performed during this review (not accepted from version 015's prose, and re-checked by more than one method) shows:

- `icacls .codex` (raw command) currently shows no `(DENY)`-class entries at all; every listed permission grant is a Modify/DeleteSubdirectoriesAndFiles Allow.
- `Get-Acl -LiteralPath .codex | Format-List` confirms this at the SDDL level: the full DACL (`D:AI(A;...)...`) contains eighteen ACEs and every single one begins with `(A;` (Allow); there is no `(D;` (Deny) ACE anywhere on the object, including for the previously-reported-risky SID `S-1-5-21-2908765920-875073000-2352713335-4168283502`, which now appears once as an inherited Allow (`A;OICIID;0x1301ff;;;S-1-5-21-2908765920-875073000-2352713335-4168283502`).
- The governed helper itself, run fresh (`scripts/repair_codex_dotdir_acl.ps1 -Mode Check -Json`), reports `checked_count=218`, `risky_deny_count=0`, `errors=[]`, `needs_repair=false`, `repaired=false` - the same helper that reported `needs_repair=true` in version 015's own post-attempt check roughly ten hours earlier now reports the opposite.
- `python scripts/verify_codex_dispatch.py --json` reports `codex_dotdir_acl_ok=true`, `live_headless_ready=true` with `live_headless_reason=codex_no_window_verification_current` (verification window `2026-07-18T06:16:30Z`-`06:17:54Z`, `expires_at=2026-07-18T10:17:54Z`), and `dispatchable=true`.
- File-timestamp cross-check rules out this reviewer's own diagnostic command as the cause: `.gtkb-state/bridge-poller/codex-no-window-verification.json` has `LastWriteTimeUtc = 2026-07-18 06:17:54 AM`, roughly 46 minutes *before* this reviewer's own invocation of `verify_codex_dispatch.py --json` at `2026-07-18T07:03:34Z` (confirmed via `date -u`). The verifier's own source (`_load_codex_no_window_verification`) only reads this cached file; it does not itself trigger a fresh smoke run. So this reviewer's read-only diagnostic did not create the state being described here - the state already existed before this review began. It also predates this reviewer's own work-intent claim acquisition (`07:19:11Z`).
- A separate, unrelated Loyal Opposition session (harness D / Ollama) held a `draft` work-intent claim on this exact thread from `2026-07-18T05:23:30Z` until it expired at `2026-07-18T05:33:30Z` with no version-016 write ever landing. That window sits *between* version 015's filing (`04:42:22Z`) and the no-window proof's timestamp (`06:16:30-06:17:54Z`) and the ACL fix (observed clean by this review, exact time unknown). This reviewer cannot determine from bridge state alone whether that session's activity is related to the fix; it is noted as a directly relevant, independently-checkable fact for Prime Builder's reconciliation rather than a conclusion.

**Deficiency rationale:** No version of this bridge thread (001-015) documents this repair. Version 015 explicitly reports that its own approved mechanism failed and made zero changes. No `REVISED` version 016+ proposal exists for this thread (confirmed via a fresh directory listing and a fresh TAFE `bridge show` call, both immediately before drafting this verdict). This reviewer's scope is strictly limited to this one bridge thread and this reviewer will not investigate or act on any other thread to explain the discrepancy. Regardless of the explanation, certifying `VERIFIED` for *this* thread on the strength of an external state change this thread cannot causally account for would fabricate an audit-trail link between the approved implementation and an outcome it explicitly disclaims - the same class of evidentiary integrity problem `loyal-opposition.md`'s "Reviewer-Evidence-Preparation vs Speculative Source Modification" section exists to prevent, applied here to an unexplained *external* mutation rather than a reviewer-authored one. On an active `P0` regression work item, an unexplained state change that happens to match the exact target of an actively-failing governed repair effort also deserves scrutiny in its own right, independent of whether it turns out to be benign (a properly governed but differently-slugged fix, or the same harness-D session doing off-thread work) or a governance gap (an out-of-band mutation outside `GOV-FILE-BRIDGE-AUTHORITY-001`).

**Proposed solution / enhancement:** Before filing any further revision of this thread, Prime Builder should re-run the same three checks this review used (`icacls .codex`, `repair_codex_dotdir_acl.ps1 -Mode Check -Json`, `verify_codex_dispatch.py --json`) to confirm the current state is durable (not transient), then explicitly reconcile the discrepancy in the revision's "Revision Claim": either (a) identify and cite the actual governed thread or operator action that performed the repair - including checking whether the expired harness-D `draft` claim noted above correlates with any other bridge/OPS record - so this WI-5250 thread can request `VERIFIED` on the strength of that cited, independently-checkable evidence plus this thread's own confirmation that the state is now correct and durable, or (b) if no governed explanation is found, say so plainly and flag it to the owner as a possible out-of-band mutation, separate from (and without blocking) closing WI-5250's readiness goal on the merits of the now-passing live checks.

**Option rationale:** The alternative - simply issuing `VERIFIED` now because the live checks happen to pass - was considered and rejected. It would end this thread's audit trail without ever explaining why the previously-approved mechanism failed and yet the same-day outcome appeared anyway, which is exactly the kind of silent gap the artifact-oriented-governance directives (`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) ask reviewers not to create. Surfacing it now, while the timestamps and version-015 evidence are still fresh and specific, gives Prime Builder the best chance of tracing the actual cause.

**Prime Builder implementation context:**

| Element | Description |
|---|---|
| Objective | Reconcile the "already fixed, cause unknown" discrepancy before requesting `VERIFIED`, without this reviewer or Prime Builder acting on any other bridge thread to do so. |
| Preconditions | None beyond ordinary read-only diagnostics; no claim or implementation-start packet is required merely to re-run `icacls`, the governed Check-mode helper, or `verify_codex_dispatch.py --json`, since none of those mutate state. |
| Evidence paths | `bridge/gtkb-wi5250-codex-a-dispatch-readiness-016.md` (this verdict) F2; `WI-5250` `status_detail` (currently stale - still describes the pre-fix two-Deny-ACE state as of its `2026-07-17T10:40:17Z` version-4 update); `scripts/bridge_claim_cli.py status gtkb-wi5250-codex-a-dispatch-readiness` for claim-history correlation. |
| File touchpoints | None expected; this is an investigative/reconciliation step, not a mutation. |
| Implementation sequence | (1) re-run the three diagnostic commands above; (2) if state is durable and clean, search for any other recently-touched bridge thread, OPS record, or owner-conversation deliberation that plausibly explains the fix (read-only search only, no action on that thread); (3) file a `REVISED` version 017 (or later) documenting the finding either way; (4) only then request `VERIFIED`, or proceed with F1's corrected-mechanism re-attempt if the state has since regressed. |
| Verification steps | The revision's own citations should be independently checkable exactly as this verdict's were. |
| Rollback notes | Not applicable; this is a read-only reconciliation step. |
| Open decisions | Whether the fix source is a legitimate governed thread (in which case citation suffices) or requires an owner-facing out-of-band-mutation flag. |

## Required Revisions

1. Do not claim `VERIFIED` for this thread based on the current live all-clear state alone. Reconcile F2 first.
2. If reconciliation in F2 finds no governed explanation and the state remains durable, file a `REVISED` proposal citing the live-clean evidence plus an explicit statement that the causal mechanism is unknown, and let the owner decide (via `AskUserQuestion`, not prose) whether to accept the outcome as-is or require a fresh governed repair pass for audit-trail completeness.
3. If the state has regressed (Deny ACEs reappear) by the time Prime Builder re-checks, file a `REVISED` proposal implementing F1's exact-ACE-object `Set-Acl` mechanism in place of the disproven `icacls /remove:d` step, keeping every other target, gate, and exclusion from version 013 unchanged.
4. Either path should also correct `WI-5250`'s `status_detail`, which currently still describes the pre-repair two-Deny-ACE state.

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge show gtkb-wi5250-codex-a-dispatch-readiness --json --compact
groundtruth-kb/.venv/Scripts/python.exe -c "from groundtruth_kb.db import KnowledgeDB; KnowledgeDB().get_work_item('WI-5250')"
icacls .codex
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/repair_codex_dotdir_acl.ps1 -Mode Check -Json
powershell -NoProfile -Command "Get-Acl -LiteralPath .codex | Format-List | Out-String -Width 300"
git log -3 --format="%H %cI %s" -- scripts/repair_codex_dotdir_acl.ps1
git status --porcelain -- scripts/repair_codex_dotdir_acl.ps1 scripts/verify_codex_dispatch.py .codex
git status --porcelain -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py
python scripts/verify_codex_dispatch.py --json
date -u +"%Y-%m-%dT%H:%M:%SZ"
powershell -NoProfile -Command "Get-Item .gtkb-state/bridge-poller/codex-no-window-verification.json | Select-Object LastWriteTimeUtc, CreationTimeUtc"
powershell -NoProfile -Command "Get-Item .gtkb-state/bridge-poller/codex-no-window-smoke/20260718T061631Z-814622d0.stdout.log | Select-Object LastWriteTimeUtc"
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5250-codex-a-dispatch-readiness
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5250-codex-a-dispatch-readiness
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge show gtkb-wi5156-governed-project-dependency-ordering-cli --json --compact
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge show gtkb-wi5002-codex-dotdir-sandbox-acl-correction --json --compact
groundtruth-kb/.venv/Scripts/gt.exe projects show-authorization PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE --json
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py status gtkb-wi5250-codex-a-dispatch-readiness
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi5250-codex-a-dispatch-readiness
groundtruth-kb/.venv/Scripts/python.exe -c "from groundtruth_kb.db import KnowledgeDB; KnowledgeDB().search_deliberations('codex A dispatch readiness ACL', limit=8)"
groundtruth-kb/.venv/Scripts/python.exe -c "from groundtruth_kb.db import KnowledgeDB; KnowledgeDB().search_deliberations('codex dotdir ACL risky deny removal', limit=4)"
groundtruth-kb/.venv/Scripts/python.exe -c "from groundtruth_kb.db import KnowledgeDB; KnowledgeDB().search_deliberations('icacls remove deny SID .codex', limit=4)"
powershell -NoProfile -Command "Get-ChildItem bridge/*.md | Where-Object { $_.LastWriteTimeUtc -gt (Get-Date '2026-07-17T20:00:00Z') } | Sort-Object LastWriteTimeUtc"
```

## Owner Action Required

None immediately. If Prime Builder's F2 reconciliation (Required Revision 2) finds no governed explanation for the state change, that revision should route the disposition question to the owner via `AskUserQuestion` at that time; this verdict does not itself require owner input to be recorded.

## Scope of this verdict

Verdict-file only. No source, test, configuration, database, ACL, or Git changes were performed by this review. This review did not touch dispatcher rules configuration, the harness registry, harness identities, or any dispatch-eligibility/routing setting; the one read of the harness registry was read-only, used solely to confirm the "A remains Prime-Builder-only" claim carried forward from prior versions. The only mutating action this reviewer performed anywhere in the system was acquiring its own work-intent claim on this exact thread (a concurrency-safety precondition the bridge-compliance-gate hook itself required before allowing this verdict file to be written) and writing this verdict file. This reviewer did not act on, modify, or file anything against any bridge thread other than `gtkb-wi5250-codex-a-dispatch-readiness`.

## Skills Applied

- proposal-review
- code-review-audit
- lo-opportunity-radar

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
