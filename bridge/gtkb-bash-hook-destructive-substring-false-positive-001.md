NEW

# Quote-Aware Destructive-Command Bash Gate: Stop False-Blocking on Incidental Verb Substrings in Quoted/Scope Text (WI-3493)

bridge_kind: implementation_proposal
Document: gtkb-bash-hook-destructive-substring-false-positive
Version: 001 (NEW; reliability fast-lane defect fix)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Implements: GOV-FILE-BRIDGE-AUTHORITY-001; WI-3493
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3493
target_paths: [".claude/hooks/destructive-gate.py", "platform_tests/unit/test_destructive_gate_hook.py"]
Recommended commit type: fix:
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 86d7f8a9-b8da-4284-b937-60eb056adda0
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

## Claim

The destructive-command Bash PreToolUse gate (`.claude/hooks/destructive-gate.py`) hard-blocks read-only / non-destructive `Bash` commands when a destructive **verb token** appears as an incidental substring inside a quoted argument or descriptive scope text, rather than as a real command invocation. The gate scans the **raw, un-tokenized** command string, so it cannot distinguish a structural shell token from literal text inside a quoted span.

### Evidence (file:line)

- `.claude/hooks/destructive-gate.py:149` — `_check_destructive(command)` receives the raw command and every pattern family below calls `pattern.search(command)` against that raw string; there is no quote/token masking step.
- `.claude/hooks/destructive-gate.py:68` — the version-control remove pattern (member of `_GIT_DESTRUCTIVE`, lines 63-72) matches the 5-character remove verb anywhere in the command, including inside a quoted argument or scope sentence. The match drives the `_GIT_DESTRUCTIVE` loop at lines 187-193, which returns a `block` reason with **no exceptions** — so a command that merely *mentions* the remove verb in quoted/scope text is blocked.
- The same raw-scan exposure exists for the other token-shaped verb families that can legitimately appear as literal words inside a quoted message or scope description:
  - `_GIT_DESTRUCTIVE` (lines 63-72): force-push, hard-reset, clean, the remove verb, checkout-discard, restore-staged, branch-delete — loop at lines 187-193.
  - `_HOOK_BYPASS` (lines 75-80): commit/push/merge with verify-skipping flags — loop at lines 155-162.
  - `_DB_DESTRUCTIVE` (lines 83-87): drop-table/database, truncate-table, delete-from — loop at lines 196-202.

### Concrete false-positive (the WI-3493 reported case)

A `Bash` command whose **only** occurrence of the version-control remove verb is inside a quoted argument or a descriptive scope sentence — for example a verbatim instruction-quoting string, a commit-message body, an `echo`/diagnostic line, or a bridge-scope description that names the verb as text — is classified destructive and blocked by the remove pattern at line 68, even though no removal is invoked. This is precisely the defect WI-3493 records (MemBase title names the remove-verb substring false-positive in scope text; `origin=defect`, `component=hooks`, `resolution_status=open`, `project_name=GTKB-RELIABILITY-FIXES`, confirmed live in the `work_items` table this session).

### Fix shape (token/quote-aware masking; preserve every genuine block)

Add a small, self-contained quote-masking step inside `.claude/hooks/destructive-gate.py` (mirroring the already-landed-and-VERIFIED `_mask_quoted_spans` approach from `scripts/implementation_start_gate.py` per the WI-3357 thread, but reimplemented locally so the hook stays import-free and standalone as it is today). The helper blanks the **interior** of single- and double-quoted spans while preserving the quote characters, and fails closed on an unbalanced quote (an unbalanced quote masks to end-of-string, so structural text is never *hidden* — at worst more text is exposed). The token-shaped verb families that can collide with quoted/scope text — `_HOOK_BYPASS`, `_GIT_DESTRUCTIVE`, and (per the Ask) `_DB_DESTRUCTIVE` — are evaluated against the **quote-masked** command instead of the raw command. A genuine destructive invocation (the verb appears as an actual unquoted command token) is unchanged by masking and still blocks.

The fix is deliberately narrow:

- The `_DELETE_PATTERNS_ALWAYS_BLOCKED` family (lines 50-57, e.g. recursive-tree deletion, removedirs, subprocess deletion wrappers) keeps scanning the **raw** command. These were intentionally made raw-scanning and safe-path-bypassing per `bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-004.md` NO-GO, because inline-Python deletion targets must not be suppressible by unrelated substrings. Masking is NOT applied to them, so the two critical bypass tests (`test_blocks_shutil_rmtree_with_unrelated_safe_path_substring`, `test_blocks_shutil_rmtree_with_safe_path_in_comment`) remain green.
- The `_DELETE_PATTERNS_WITH_SAFE_EXCEPTION` family (lines 34-41) and its `_is_safe_path` check (lines 144-146) are unchanged — they already have their own (raw) safe-path semantics and are not the WI-3493 token-collision class.
- The `_AZURE_DESTRUCTIVE`, `_PROD_ENV_PATTERNS`, and `_EXFIL_PATTERNS` families (lines 90-124) are unchanged. These intentionally match production identifiers / exfiltration shapes that are dangerous even when they appear inside quotes (e.g. a production FQDN or DB name in a Python string literal), and their existing tests (`test_blocks_production_cosmos_db_name`, `test_blocks_cosmos_delete_item`) assert that quoted-literal matching. Masking them would regress those true-positives, so they stay raw.

This is a genuine small single-concern defect fix with no new API, CLI, requirement, or externally visible behavior beyond removing the fail-closed false-positive; genuine destructive commands continue to block identically.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol authority; this proposal is a bridge artifact and `bridge/INDEX.md` remains canonical workflow state. The destructive-gate hook is safety infrastructure adjacent to the bridge-governed reliability surface.
- GOV-RELIABILITY-FAST-LANE-001 — the reliability fast-lane governs small single-concern defect fixes with no new behavior; this proposal claims fast-lane eligibility and maps the four criteria in the Fast-Lane Eligibility section.
- GOV-ARTIFACT-APPROVAL-001 — the destructive-gate hook is one credential/safety enforcement surface in the formal-artifact-approval discipline; this change preserves that surface (every genuine destructive verb, credential-exfil shape, and production-targeting pattern still blocks) while narrowing a false-positive.
- SPEC-AUQ-POLICY-ENGINE-001 — the destructive-gate is part of the deterministic policy-gate family; the fix keeps classification deterministic (regex over a deterministically-masked string, no LLM).
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 — the fix uses a deterministic quote-masking + regex classifier; no LLM classification is introduced.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — in-root placement; both target paths are in-root under `E:\GT-KB`, no `applications/` path is involved.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan maps each linked behavior to an executed test, carried forward into the implementation report.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — the defect, decision, and verification are preserved as durable bridge and MemBase artifacts (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across WI-3493, this thread, the specs, and the tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — WI-3493 moves through open to implementing to verified lifecycle states (advisory).

No directly-governing functional specification exists for the destructive-gate hook's regex/classifier — the hook is its own implementation surface. The existing classifier shape — and its documented prior decision in `bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-004.md` — is the de-facto specification; this proposal narrows the false-positive set while preserving the true-positive set, and the verification plan proves both, exactly as the sibling implementation-start-gate substring-misclassification threads did.

## Fast-Lane Eligibility

This thread claims eligibility under `GOV-RELIABILITY-FAST-LANE-001` and the standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active; `project_id=PROJECT-GTKB-RELIABILITY-FIXES`; owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`; covers-by-membership: WI-3493 is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`). The four eligibility criteria:

1. **Origin defect/regression** — met. WI-3493 has `origin=defect` (confirmed live in the `work_items` table; title names the remove-verb substring false-positive in scope text). The false-positive is a defect in the destructive-gate's command classifier.
2. **No new API/CLI/behavior beyond removing the defect** — met. The change adds a self-contained quote-masking step before three existing scans. It adds no CLI, no API, and no behavior. Genuine destructive commands classify identically (the gate's true-positive coverage is unchanged and regression-tested); the gate simply stops misreading quoted/scope text as a command token.
3. **No new requirement** — met. The hook's intent — block genuine destructive operations without blocking non-destructive work — is the existing requirement; the defect is the classifier misfiring on quoted literals. No new GOV/SPEC/PB/ADR/DCL artifact is created.
4. **Small single-concern scope** — met. One concern: quote-awareness of the token-shaped destructive verb families. One hook source file plus its test file; no cross-cutting change.

The standing authorization's `allowed_mutation_classes` are `source`, `test_addition`, and `hook_upgrade` (confirmed live this session); IP-1 (`hook_upgrade`/`source`) and IP-2 (`test_addition`) fall within scope. Its `forbidden_operations` (`deploy`, `git_push_force`, `spec_deletion`) are not exercised.

## Prior Deliberations

- `bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-004.md` (NO-GO, cited in the hook source at lines 44-49 and 165-167) established that the **Python recursive-deletion** family must scan raw command text and bypass safe-path substrings, because inline-Python deletion targets must not be suppressible by unrelated substrings. This proposal explicitly preserves that decision: it does NOT mask the `_DELETE_PATTERNS_ALWAYS_BLOCKED` family, so the two critical bypass tests remain green. The WI-3493 fix targets a disjoint family (token-shaped verb families), so it does not revisit or weaken that prior NO-GO.
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-010.md` (WI-3357, VERIFIED) introduced `_mask_quoted_spans()` in `scripts/implementation_start_gate.py` to make a quoted commit message not trip control-marker detection. This proposal adopts the same quote-masking technique for a *different* hook (the destructive-gate Bash PreToolUse hook) and a *different* false-positive class (incidental destructive-verb substrings). The technique is reused conceptually; the destructive-gate keeps its own local, import-free implementation rather than coupling to the impl-start-gate module.
- `bridge/gtkb-impl-start-gate-quoted-arg-misclassification-001.md` (WI-3358, NEW) is the structural sibling for the same kind of quoted-argument substring false-positive, but in `scripts/implementation_start_gate.py` (the implementation-start authorization gate), NOT in `.claude/hooks/destructive-gate.py` (this Bash PreToolUse destructive gate). The two hooks are distinct files, distinct mechanisms, and distinct defects; this proposal does not overlap WI-3358's target paths.
- The reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`, `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`) is VERIFIED at `bridge/gtkb-reliability-fast-lane-006.md`; its owner-decision record is `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`. This proposal uses that standing authorization.

## Owner Decisions / Input

No owner decision required — standing fast-lane authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING covers this by active project membership; no AskUserQuestion needed.

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active; owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) authorizes implementation on WI-3493 by active membership in `PROJECT-GTKB-RELIABILITY-FIXES`.
- The reliability fast-lane removes per-fix deliberation, per-fix project authorization, and per-fix formal-artifact-approval packets for small defect fixes; the standing authorization is the owner approval.
- No destructive action, no deployment, no spec mutation, and no protected narrative-artifact edit is requested.

## Requirement Sufficiency

Existing requirements sufficient. The destructive-gate hook's intent — block genuine destructive Bash operations (deletion, history rewriting, force pushes, DB drops, Azure resource deletion, production targeting, credential exfiltration) while not blocking non-destructive work — is established by `GOV-ARTIFACT-APPROVAL-001` (credential/safety enforcement surface) and the existing classifier shape, including the prior decision recorded in `bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-004.md`. This proposal narrows a false-positive without changing that intent. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-work-item, single-concern change to one hook source file plus its test file. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3493) is this proposal's own implementing work item under the mandatory project-linkage metadata. The review-packet inventory is exactly IP-1 (the classifier fix) plus IP-2 (the regression tests) in this one thread.

## Scope

### IP-1: Make the token-shaped destructive verb families quote-aware

In `.claude/hooks/destructive-gate.py`:

1. Add a small, self-contained `_mask_quoted_spans(command)` helper (no new imports beyond the already-imported `re`) that blanks the interior of single- and double-quoted spans while preserving the quote characters, and fails closed on an unbalanced quote (mask to end-of-string). The helper masks both quote types, because a destructive verb is literal text inside either quote type. It is a pure string transform with no side effects.
2. In `_check_destructive()` (line 149), compute `masked = _mask_quoted_spans(command)` once, and evaluate the `_HOOK_BYPASS` loop (lines 155-162), the `_GIT_DESTRUCTIVE` loop (lines 187-193) — this is the family containing the remove pattern at line 68 that produced the WI-3493 false-positive — and (subject to Loyal Opposition Ask #3) the `_DB_DESTRUCTIVE` loop (lines 196-202) against `masked` instead of the raw `command`.
3. Leave every other family scanning the **raw** `command`, unchanged: `_DELETE_PATTERNS_ALWAYS_BLOCKED` (lines 168-175), `_DELETE_PATTERNS_WITH_SAFE_EXCEPTION` + `_is_safe_path` (lines 178-184), `_AZURE_DESTRUCTIVE` (lines 205-212), `_PROD_ENV_PATTERNS` (lines 215-222), `_EXFIL_PATTERNS` (lines 225-231).

The pattern constants, the block-reason messages, the family ordering/priority, the fail-closed `except` path in `_check_destructive` (lines 264-266), and `main()` are all unchanged. The behavior contract is: a destructive verb that appears only inside a quoted span or scope text no longer blocks; a destructive verb that appears as a genuine unquoted command token blocks exactly as before; and every production/exfil/inline-Python-deletion true-positive is untouched. The default disposition for `_DB_DESTRUCTIVE` is option (b) in Risk R3 (mask only `_GIT_DESTRUCTIVE` and `_HOOK_BYPASS`); the implementation follows Loyal Opposition's choice.

### IP-2: Add spec-derived regression tests

In `platform_tests/unit/test_destructive_gate_hook.py`, add a `# WI-3493` section using the existing `check_destructive` fixture (which loads `_check_destructive` from the hook):

False-positive removed (each asserts the command is no longer blocked):
- A read-only `echo` whose quoted scope sentence names the version-control remove verb returns `None`.
- A `python -c` whose quoted Python string literal contains a hard-reset history-rewrite phrase returns `None`.
- A command whose quoted argument contains a verify-skipping commit phrase as descriptive text returns `None`.
- A command whose quoted argument mentions a drop-table SQL phrase as descriptive text returns `None` (only if the chosen R3 disposition masks `_DB_DESTRUCTIVE`).

True-positive preserved (regression guards):
- A genuine unquoted version-control remove command (cached-file removal) still blocks with a "Destructive git" reason.
- A genuine unquoted hard-reset still blocks.
- A genuine unquoted verify-skipping commit (the flag is an actual unquoted flag, not inside the quoted message value) still blocks.
- The existing production / Azure / inline-Python-deletion tests remain green: `test_blocks_production_cosmos_db_name`, `test_blocks_cosmos_delete_item`, `test_blocks_shutil_rmtree_with_unrelated_safe_path_substring`, `test_blocks_shutil_rmtree_with_safe_path_in_comment`, and the rest of the file.

The whole file is run in verification, so any regression in the existing production, Azure, exfil, or Python-deletion-parity tests fails the suite.

## Out Of Scope

- `scripts/implementation_start_gate.py` and its WI-3358 quoted-argument fix (`bridge/gtkb-impl-start-gate-quoted-arg-misclassification`) — a different hook and a different defect; not touched.
- The `_DELETE_PATTERNS_ALWAYS_BLOCKED` inline-Python-deletion family and its raw-scan / safe-path-bypass semantics (per the 2026-04-27-004 NO-GO) — preserved exactly; not masked.
- The `_AZURE_DESTRUCTIVE`, `_PROD_ENV_PATTERNS`, and `_EXFIL_PATTERNS` families — preserved exactly; not masked (they must match quoted literals).
- Adding new destructive patterns, new safe-path exceptions, changing block-reason text, changing family ordering, or altering `main()` / the JSON I/O contract / the fail-closed `except` behavior.
- Any file outside `E:\GT-KB`. Both target paths are within the project root.

## Files Expected To Change

- `.claude/hooks/destructive-gate.py` — add a self-contained `_mask_quoted_spans()` helper and evaluate the `_HOOK_BYPASS`, `_GIT_DESTRUCTIVE`, and (per Ask #3) `_DB_DESTRUCTIVE` families against the masked command in `_check_destructive()`; all other families and `main()` unchanged (IP-1).
- `platform_tests/unit/test_destructive_gate_hook.py` — the `# WI-3493` regression section (IP-2).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| GOV-ARTIFACT-APPROVAL-001 (false-positive removed) | Tests: quoted-argument / scope-text destructive-verb commands return `None` from `_check_destructive` (no longer blocked). |
| GOV-ARTIFACT-APPROVAL-001 (true-positive preserved) | Tests: genuine unquoted destructive commands (remove, hard-reset, genuine verify-skipping flag) still return a `block` reason. |
| SPEC-AUQ-POLICY-ENGINE-001 / SPEC-AUQ-NO-LLM-CLASSIFIER-001 | Full `platform_tests/unit/test_destructive_gate_hook.py` run confirms deterministic classifier behavior (regex over a deterministically-masked string) with no regression. |
| GOV-ARTIFACT-APPROVAL-001 (orthogonal families untouched) | Existing tests `test_blocks_production_cosmos_db_name`, `test_blocks_cosmos_delete_item`, `test_blocks_shutil_rmtree_with_unrelated_safe_path_substring`, `test_blocks_shutil_rmtree_with_safe_path_in_comment` remain green (production / Azure / inline-Python-deletion families are not masked). |
| GOV-FILE-BRIDGE-AUTHORITY-001 | `bridge/INDEX.md` remains canonical; live INDEX read + bridge-thread drift check at review/verify time. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Target-path inspection: both files under `E:\GT-KB`. |
| GOV-RELIABILITY-FAST-LANE-001 | The Fast-Lane Eligibility section maps the four criteria; Loyal Opposition confirms eligibility. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus executed test commands and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/unit/test_destructive_gate_hook.py -q --tb=short`
- `python -m ruff check .claude/hooks/destructive-gate.py platform_tests/unit/test_destructive_gate_hook.py`
- `python -m ruff format --check .claude/hooks/destructive-gate.py platform_tests/unit/test_destructive_gate_hook.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bash-hook-destructive-substring-false-positive`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bash-hook-destructive-substring-false-positive`

(If the default interpreter lacks `pytest`/`ruff`, resolve the repo venv at `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe` for the pytest and ruff lanes, per the sibling reliability-fast-lane verification evidence.)

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] IP-1 landed: `_check_destructive()` evaluates the `_HOOK_BYPASS`, `_GIT_DESTRUCTIVE`, and (per the R3 choice) `_DB_DESTRUCTIVE` families against a quote-masked command; the production / Azure / exfil / inline-Python-deletion families still scan the raw command.
- [ ] `_check_destructive` returns `None` for destructive-verb-in-quoted-span / scope-text commands; covered by tests.
- [ ] `_check_destructive` still returns a `block` reason for every genuine unquoted destructive command; covered by tests.
- [ ] The existing production / Azure / inline-Python-deletion / exfil tests remain green (orthogonal families untouched); full-file run is clean.
- [ ] `ruff check` and `ruff format --check` clean for both touched files.
- [ ] Bridge applicability preflight and ADR/DCL clause preflight both pass for bridge id `gtkb-bash-hook-destructive-substring-false-positive`.
- [ ] No file outside `target_paths` is modified.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Risk And Rollback

**Risk R1 (low): masking weakens a genuine destructive signal.** Mitigation: masking blanks only the *interior* of balanced quoted spans; a genuine destructive command's verb token is unquoted (outside any span) and is therefore unaffected — the genuine-command true-positive tests pin every form. An unbalanced quote masks to end-of-string, which can only *expose more* structural text, never hide an unquoted verb (fail-closed). Masking is applied to exactly the token-shaped families and explicitly not to the production / Azure / exfil / inline-Python-deletion families.

**Risk R2 (low): regression in the inline-Python-deletion bypass class.** Mitigation: the `_DELETE_PATTERNS_ALWAYS_BLOCKED` family is left scanning the raw command, exactly as the 2026-04-27-004 NO-GO required; the two critical bypass tests (`test_blocks_shutil_rmtree_with_unrelated_safe_path_substring`, `test_blocks_shutil_rmtree_with_safe_path_in_comment`) are part of the verification suite and must stay green.

**Risk R3 (low): a genuine destructive SQL/command whose payload is quoted no longer matches its masked family.** A real drop-table issued through a quoted SQL argument puts the destructive SQL inside the quoted argument, and masking `_DB_DESTRUCTIVE` would make that specific shape no longer match. This is the inherent tension of quote-awareness. The chosen disposition is Loyal Opposition Ask #3: (a) accept the narrowing for `_DB_DESTRUCTIVE`, or (b) keep `_DB_DESTRUCTIVE` raw and mask only `_GIT_DESTRUCTIVE` + `_HOOK_BYPASS` (which is sufficient to fix the reported WI-3493 case). The default in this proposal is (b) — mask only `_GIT_DESTRUCTIVE` and `_HOOK_BYPASS`, leaving `_DB_DESTRUCTIVE` raw — because it fixes the reported defect with the smallest true-positive surface change. The Spec-To-Test Mapping and IP-1 family list will be tightened to match the chosen option at GO.

Rollback: revert the IP-1 masking and helper; `_check_destructive` returns to raw-text scanning for all families. The IP-2 tests document the desired behavior and may remain. No data migration and no canonical-artifact mutation are involved.

## Loyal Opposition Asks

1. Confirm that masking quoted spans for the `_GIT_DESTRUCTIVE` and `_HOOK_BYPASS` families (the token-shaped verbs that produced the WI-3493 false-positive) while leaving the production / Azure / exfil / inline-Python-deletion families on the raw command is the correct split.
2. Confirm that a local, import-free `_mask_quoted_spans()` in `.claude/hooks/destructive-gate.py` (rather than importing the impl-start-gate helper) is the right structural choice to keep the PreToolUse hook standalone, while adopting the same already-VERIFIED masking technique.
3. **Decide R3:** mask `_DB_DESTRUCTIVE` too (option a — broader false-positive removal, but a quoted genuine drop-table no longer matches that family), or leave `_DB_DESTRUCTIVE` raw (option b — default; fixes the reported case with the smallest true-positive change). The implementation and tests will follow your choice.
4. Confirm the scope boundary: this fix is disjoint from WI-3358 (the implementation-start gate) and from the 2026-04-27-004 inline-Python-deletion NO-GO, and reuses the WI-3357 masking technique without re-opening those threads.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
