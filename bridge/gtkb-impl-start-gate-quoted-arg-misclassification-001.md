NEW

# implementation_start_gate Quoted-Argument Keyword and Protected-Path Token Misclassification Fix (WI-3358)

bridge_kind: prime_proposal
Document: gtkb-impl-start-gate-quoted-arg-misclassification
Version: 001 (NEW; reliability fast-lane defect fix)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Implements: PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001; GOV-FILE-BRIDGE-AUTHORITY-001; WI-3358
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3358
target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]
Recommended commit type: fix:
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 86d7f8a9-b8da-4284-b937-60eb056adda0
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

## Claim

The implementation-start gate (`scripts/implementation_start_gate.py`) hard-blocks read-only commands when a mutating-command keyword OR a protected-path token appears **inside a quoted command argument** (a string literal, an `echo`/`Write-Output` message, or a `-Value`/`-m` argument). Two detection sites scan the raw, un-tokenized command string and so cannot tell a structural shell token from literal text inside a quoted span:

1. **Named-command signal.** `_has_mutating_signal()` (line 385) calls `MUTATING_COMMAND_RE.search(command)` against the **raw** command. The named-command alternatives in `MUTATING_COMMAND_RE` (`set-content`, `out-file`, `new-item`, `remove-item`, `move-item`, `copy-item`, `apply_patch`, `git commit|reset|...`, `python ... insert_|update_|delete_`, lines 80-87) therefore match even when the keyword is literal text inside quotes.
2. **Protected-path token detection.** `_paths_from_shell()` (lines 196-207) calls `PATH_TOKEN_RE.findall(command)` against the **raw** command (line 197) and additionally inspects `shlex.split(command, posix=False)` tokens (lines 198-207). A protected-path-shaped substring inside a quoted argument is therefore extracted as a "protected target."

### Live evidence (this session, 2026-06-01; direct read-only probe of the gate functions)

`gate_decision()` with `cwd=E:/GT-KB`:

- `echo "remember to run set-content on the file"` → `paths=[]`, `mutating=True`, **BLOCKED=True**. The quoted-argument keyword `set-content` matches `MUTATING_COMMAND_RE`; no path resolves, so `gate_decision()` substitutes `<unknown-mutating-target>` (line 602) and `validate_targets()` raises → a pure read-only `echo` is hard-blocked.
- `python -c "msg; print('edit scripts/foo.py and run remove-item')"` → `paths=['scripts/foo.py']`, `mutating=True`, **BLOCKED=True**. Both the protected-path token `scripts/foo.py` and the keyword `remove-item` are inside the quoted Python string literal.
- `Write-Output "the file scripts/bar.py needs set-content"` → `paths=['scripts/bar.py']`, `mutating=True`, **BLOCKED=True**.
- `Set-Content -Path bridge/note.md -Value "reminder: update scripts/secret.py"` → `paths=['bridge/note.md', 'scripts/secret.py']`, `mutating=True`, **BLOCKED=True**. This is a *genuine, allowed* write to `bridge/note.md` (in `ALLOWED_WRITE_PREFIXES`), but the quoted `-Value` text mentions `scripts/secret.py`, so the gate wrongly adds it as a protected target and blocks a legitimate bridge write.

`echo`, `Write-Output`, and `python -c` are not in `SAFE_COMMAND_PREFIXES`, so `_is_safe_command()` does not rescue them; the false-positive reaches a real `block` decision.

### Fix shape (reuse the existing, already-VERIFIED quote-masking helper)

`scripts/implementation_start_gate.py` already contains `_mask_quoted_spans(command, *, mask_double)` (lines 222-250), landed and VERIFIED by WI-3357. It blanks the interior of single- and double-quoted spans while preserving quote characters and failing closed on unbalanced quotes. A direct probe confirms it is exactly the right tool:

- `_mask_quoted_spans('echo "run set-content now"', mask_double=True)` → `echo "                   "`; `MUTATING_COMMAND_RE.search(...)` → no match.
- `_mask_quoted_spans('Set-Content -Path scripts/x.py -Value y', mask_double=True)` → unchanged (the genuine unquoted command has no quoted span over the keyword); `MUTATING_COMMAND_RE.search(...)` → still matches → genuine mutation preserved.
- `PATH_TOKEN_RE.findall(masked echo)` → `[]`; `PATH_TOKEN_RE.findall(masked genuine write)` → `['scripts/foo.py']` → preserved.

The fix masks quoted spans (mask_double=True; both quote types blanked because a mutating keyword or a path is literal inside either quote type) before the named-command scan and before the path-token scan. The redirect-operator signal is **already** quote-aware via the token-based `_shell_redirect_present()` (W4/WI-3368) and is not touched.

## Specification Links

- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 — the implementation-start gate is the mechanical enforcement surface for this protected behavior; this fix narrows a false-positive (read-only commands wrongly blocked) while preserving the gate's true-positive coverage (genuine unquoted mutations still blocked). This is the de-facto governing specification for the gate's command classifier.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol authority; this proposal is a bridge artifact and `bridge/INDEX.md` remains canonical workflow state.
- GOV-RELIABILITY-FAST-LANE-001 — the reliability fast-lane governs small single-concern defect fixes with no new behavior; this proposal claims fast-lane eligibility and maps the four criteria in the Fast-Lane Eligibility section.
- GOV-STANDING-BACKLOG-001 — WI-3358 is a single tracked standing-backlog work item; this is not a bulk operation.
- GOV-ARTIFACT-APPROVAL-001 — the gate is one enforcement surface for the protected-mutation evidence requirement; this change preserves that surface (genuine mutations still require a packet).
- SPEC-AUQ-POLICY-ENGINE-001 — the implementation-start gate is part of the deterministic policy-gate family; the fix keeps classification deterministic.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — in-root placement; both target paths are in-root under `E:\GT-KB`, no `applications/` path is involved.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan maps each linked behavior to an executed test, carried forward into the implementation report.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — the defect, decision, and verification are preserved as durable bridge and MemBase artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across WI-3358, this thread, the specs, and the tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — WI-3358 moves through open → implementing → verified lifecycle states (advisory).

No directly-governing functional specification exists for the gate's regex/classifier — the hook is its own implementation surface, as established by the sibling WI-3317/WI-3356/WI-3357 threads. The existing classifier shape is the de-facto specification; this proposal narrows the false-positive set while preserving the true-positive set, and the verification plan proves both.

## Fast-Lane Eligibility

This thread claims eligibility under `GOV-RELIABILITY-FAST-LANE-001` and the standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (covers-by-membership: WI-3358 is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`). The four eligibility criteria:

1. **Origin defect/regression** — met. WI-3358 has `origin=defect` (confirmed in MemBase: title "implementation-start gate misclassifies mutating-command keywords and protected-path tokens inside quoted command arguments as real shell mutations"). The false-positive is reproduced live as a real `block` decision on read-only commands.
2. **No new API/CLI/behavior beyond removing the defect** — met. The change masks quoted spans before two existing scans, reusing the already-present `_mask_quoted_spans` helper. It adds no CLI, no API, and no behavior. Genuine unquoted mutations classify identically (the gate's true-positive coverage is unchanged and regression-tested); the gate simply stops misreading quoted text.
3. **No new requirement** — met. `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` already requires the gate to classify protected mutations; the defect is the classifier misfiring on quoted literals. No new GOV/SPEC/PB/ADR/DCL artifact is created.
4. **Small single-concern scope** — met. One concern: quote-awareness of the named-command and path-token classification paths. One source file plus its test file; no cross-cutting change.

The standing authorization's `allowed_mutation_classes` are `source`, `test_addition`, and `hook_upgrade`; IP-1 (`source`/`hook_upgrade`) and IP-2 (`test_addition`) fall within scope. Its `forbidden_operations` (`deploy`, `git_push_force`, `spec_deletion`) are not exercised.

## Prior Deliberations

This is the fourth member of the implementation-start-gate substring-misclassification defect family. The three prior members are terminal (VERIFIED); none of them fixed WI-3358's case, and this proposal revisits no rejected approach.

- `bridge/gtkb-impl-start-gate-comparison-operator-fix` (WI-3356, VERIFIED at `-006`). Fixed `MUTATING_COMMAND_RE`'s **redirect-operator** branch by extending the trailing lookahead to `(?![>&=])`, so Python `>=` / `>>=` are not misread as shell redirects. It touched only the redirect alternation's lookahead; it did not touch the **named-command** alternatives (`set-content`, `remove-item`, etc.), which are WI-3358's keyword path. **Out of scope here.**
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix` (WI-3357, VERIFIED at `-010`). Made `_is_simple_git_finalization_command()` quote-aware (the git-finalization **exemption** path) by introducing `_mask_quoted_spans()` and the HEREDOC recognizer, so control markers (`;`, `|`, `&&`, `$(`, backtick) inside a quoted `-m` commit message do not disqualify the exemption. That fix is scoped to the finalization exemption predicate only; it does **not** mask quoted spans for the general `_has_mutating_signal()` named-command scan or `_paths_from_shell()` path scan that WI-3358 targets. This proposal **reuses** the `_mask_quoted_spans()` helper WI-3357 landed, applying it to the two general-classification sites it did not cover.
- `bridge/gtkb-s358-w4-enforcement-calibration` (W4 IP-4, WI-3368) — replaced `MUTATING_COMMAND_RE`'s `>`-substring redirect detection with the punctuation-aware shlex token scan `_shell_redirect_present()`, so a `>` inside a quoted argument or embedded Python expression is not misread as a redirect. A direct probe confirms `_shell_redirect_present('echo "run set-content now"')` is already `False` — the **redirect** signal is therefore already quote-aware and is **not** touched here. But the W4 change deliberately preserved the **named-command** signal matching on raw text (its test `test_impl_start_gate_genuine_redirect_still_mutating` asserts `Set-Content -Path scripts/sample.py -Value x` stays `True`), so the quoted-**keyword** and quoted-**path-token** misclassification that WI-3358 targets remained.
- A Deliberation Archive search for the implementation-start-gate quoted-argument keyword/path-token misclassification returns no DELIB record addressing this case; the nearest prior art is the three sibling threads above. The owner-decision basis for the routing is `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` (the standing reliability fast-lane).

WI-3358's distinguishing fact: the misfiring substrings are the **named-command keywords** and **protected-path tokens** (not the redirect operator, fixed by WI-3356/WI-3368; not the finalization-exemption control markers, fixed by WI-3357), scanned on raw command text by `_has_mutating_signal()` and `_paths_from_shell()`.

## Owner Decisions / Input

No owner decision required — standing fast-lane authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING covers this by active project membership; no AskUserQuestion needed.

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active; owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) authorizes implementation on WI-3358 by active membership in `PROJECT-GTKB-RELIABILITY-FIXES`.
- The reliability fast-lane removes per-fix deliberation, per-fix project authorization, and per-fix formal-artifact-approval packets for small defect fixes; the standing authorization is the owner approval.
- No destructive action, no deployment, no spec mutation, and no protected narrative-artifact edit is requested.

## Requirement Sufficiency

Existing requirements sufficient. The gate's intent — classify protected mutations so they require a bridge GO authorization packet, without blocking read-only work — is established by `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` and `GOV-ARTIFACT-APPROVAL-001`, and the existing classifier shape carried forward by the VERIFIED WI-3356, WI-3357, and WI-3368 threads. This proposal narrows a false-positive without changing that intent. No new or revised requirement or specification is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-work-item, single-concern change to one source file plus its test file. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3358) is this proposal's own implementing work item under the mandatory project-linkage metadata. The review-packet inventory is exactly IP-1 (the classifier fix) plus IP-2 (the regression tests) in this one thread.

## Scope

### IP-1: Make the named-command and path-token classification quote-aware

In `scripts/implementation_start_gate.py`, apply the existing `_mask_quoted_spans(command, mask_double=True)` helper to the command before the two raw-text scans, so a mutating keyword or a protected-path substring inside a quoted span is not treated as a live shell mutation or a protected target:

1. **Named-command scan** — in `_has_mutating_signal()` (line 385), evaluate `MUTATING_COMMAND_RE.search(...)` against the quote-masked command rather than the raw command. The redirect signal continues to use `_shell_redirect_present()` (already token-based and quote-aware) against the original command — masking must not be allowed to weaken the redirect signal, so the redirect branch is left on the unmasked command. (Probe confirms a genuine unquoted `Set-Content -Path scripts/x.py -Value y` is unchanged by masking and still matches.)
2. **Path-token scan** — in `_paths_from_shell()` (lines 196-207), extract `PATH_TOKEN_RE` matches (line 197) from the quote-masked command, and ensure the `shlex.split(..., posix=False)` token loop (lines 198-207) does not add a protected path that exists only inside a quoted span (e.g., scan masked text, or skip tokens that are wholly quoted spans). Genuine unquoted path arguments (`-Path scripts/foo.py`) are unaffected by masking and still resolve.

`mask_double=True` is correct for both: a mutating keyword and a path are literal inside either single or double quotes (unlike the WI-3357 execution-marker case, which needed `mask_double=False` because `$(`/backtick still execute inside double quotes). The marker constants, the regexes, and the redirect detection are unchanged and stay single-sourced. The exact construct (helper extraction vs. inline masking at each site) is an implementation detail; the behavior contract is: quoted-span keywords/paths do not flag, unquoted keywords/paths/redirects flag exactly as before.

### IP-2: Add spec-derived regression tests

In `platform_tests/scripts/test_implementation_start_gate.py`, add a `# WI-3358` section:

False-positive removed (each asserts the command is no longer classified mutating / no longer blocked):
- `_is_mutating_command('echo "remember to run set-content on the file"')` is `False`.
- `_is_mutating_command('Write-Output "the file scripts/bar.py needs set-content"')` is `False`.
- `_is_mutating_command` for a `python -c` command whose quoted string literal mentions `edit scripts/foo.py and run remove-item` is `False` (keyword and path inside the quoted string literal).
- `_paths_from_shell(root, 'echo "see scripts/foo.py for details"')` is `[]`.
- `gate_decision` for `echo "remember to run set-content on the file"` returns `{}` (not blocked).
- `gate_decision` for `Set-Content -Path bridge/note.md -Value "reminder: update scripts/secret.py"` returns `{}` — the genuine write targets the allowed `bridge/` path and the quoted protected-path mention no longer adds a protected target.

True-positive preserved (regression guards; some already exist in the file and are re-asserted for WI-3358 context):
- `_is_mutating_command('Set-Content -Path scripts/sample.py -Value x')` is `True` (genuine unquoted mutating command).
- `_is_mutating_command('echo data > out.txt')` is `True` (genuine unquoted redirect; the redirect path is untouched).
- `_paths_from_shell(root, 'Set-Content -Path scripts/foo.py -Value x')` contains `scripts/foo.py` (genuine unquoted protected target still resolves).
- A genuine protected write that IS missing a packet (e.g. `gate_decision` for `Set-Content -Path scripts/foo.py -Value x`) still returns a `block` decision.

The whole file is run in verification, so any regression in the existing finalization, redirect, format-spec, or sqlite-read tests fails the suite.

## Out Of Scope

- The WI-3356 comparison-operator (`>=` / `>>=`) redirect-lookahead fix — already VERIFIED at `bridge/gtkb-impl-start-gate-comparison-operator-fix-006.md`. Not touched.
- The WI-3357 git-finalization-exemption quoted-control-marker fix — already VERIFIED at `bridge/gtkb-impl-start-gate-finalization-quoting-fix-010.md`. Not touched; this proposal only **reuses** the `_mask_quoted_spans()` helper it landed.
- The WI-3368/W4 redirect-operator token-scan replacement (`_shell_redirect_present()`) — already landed; the redirect signal is already quote-aware and is not modified.
- Adding new safe-command prefixes, changing `SAFE_COMMAND_PREFIXES`, `NULL_SINK_REDIRECT_STRIP_RE`, the sqlite-read AST classifier, the block-reason message, or `main()`.
- Any file outside `E:\GT-KB`. Both target paths are within the project root.

## Files Expected To Change

- `scripts/implementation_start_gate.py` — apply quote-masking (via the existing `_mask_quoted_spans`) before the `MUTATING_COMMAND_RE` named-command scan in `_has_mutating_signal()` (line 385) and before the `PATH_TOKEN_RE` / shlex-token path scan in `_paths_from_shell()` (lines 196-207). Redirect detection is unchanged (IP-1).
- `platform_tests/scripts/test_implementation_start_gate.py` — the `# WI-3358` regression section (IP-2).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 (false-positive removed) | Tests: quoted-argument keyword / protected-path-token commands (`echo`, `Write-Output`, `python -c`, the allowed-`bridge/`-write-with-quoted-protected-mention) are no longer classified mutating and `gate_decision()` returns `{}`. |
| PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 / GOV-ARTIFACT-APPROVAL-001 (true-positive preserved) | Tests: genuine unquoted mutating commands (`Set-Content -Path scripts/sample.py ...`), genuine unquoted redirects (`echo data > out.txt`), and genuine unquoted protected-path targets still classify mutating / resolve / block. |
| SPEC-AUQ-POLICY-ENGINE-001 | Full `platform_tests/scripts/test_implementation_start_gate.py` run confirms deterministic classifier behavior with no regression. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | `bridge/INDEX.md` remains canonical; live INDEX read + bridge-thread drift check at review/verify time. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Target-path inspection: both files under `E:\GT-KB`. |
| GOV-RELIABILITY-FAST-LANE-001 | The Fast-Lane Eligibility section maps the four criteria; Loyal Opposition confirms eligibility. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus executed test commands and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short`
- `python -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py`
- `python -m ruff format --check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-quoted-arg-misclassification`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-gate-quoted-arg-misclassification`

(If the default interpreter lacks `pytest`/`ruff`, resolve the repo venv at `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe` for the pytest and ruff lanes, per the sibling WI-3356/WI-3357 verification evidence.)

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] IP-1 landed: `_has_mutating_signal()` evaluates `MUTATING_COMMAND_RE` against the quote-masked command; `_paths_from_shell()` extracts paths from the quote-masked command; redirect detection (`_shell_redirect_present()`) is unchanged.
- [ ] `_is_mutating_command()` returns `False` for quoted-argument keyword commands (`echo`/`Write-Output`/`python -c` literals) and `True` for every genuine unquoted mutating command and redirect; covered by tests.
- [ ] `_paths_from_shell()` does not add a protected path that exists only inside a quoted span, and still resolves genuine unquoted protected-path targets; covered by tests.
- [ ] `gate_decision()` returns `{}` for the four live-evidence false-positive commands and still returns a `block` decision for a genuine unpacketed protected write; covered by tests.
- [ ] No regression in any other `platform_tests/scripts/test_implementation_start_gate.py` test; `ruff check` and `ruff format --check` clean for both touched files.
- [ ] Bridge applicability preflight and ADR/DCL clause preflight both pass for bridge id `gtkb-impl-start-gate-quoted-arg-misclassification`.
- [ ] No file outside `target_paths` is modified.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Risk And Rollback

**Risk R1 (low): masking weakens a genuine mutating signal.** Mitigation: only the **named-command** scan and the **path-token** scan are masked; the **redirect** signal stays on the unmasked command via the already-token-based `_shell_redirect_present()`. A direct probe confirms genuine unquoted commands (`Set-Content -Path scripts/x.py -Value y`, `echo data > out.txt`) are unaffected by masking, and the existing true-positive tests (`test_impl_start_gate_genuine_redirect_still_mutating`, plus the WI-3358 preservation tests) pin every genuine form. Masking can only ever *expose more* structural text (a mis-segmented span ends early), never hide an unquoted operator — fail-closed, consistent with the documented `_mask_quoted_spans` contract.

**Risk R2 (low): a command with an unbalanced quote.** Mitigation: `_mask_quoted_spans` blanks an unbalanced trailing quote to end-of-string, and the downstream `shlex.split` raises `ValueError` on the unbalanced quote (already handled with a conservative fallback at lines 198-201 and 346-348). Net effect for that shape is unchanged from current behavior. A test may be added if Loyal Opposition requests.

**Risk R3 (low): a protected path smuggled inside a quoted argument of a genuinely-mutating command escapes path attribution.** This is the intended behavior of the fix — a quoted string is data, not a target. The genuine mutation target (the unquoted `-Path`/redirect target) is still resolved and gated; only the spurious quoted mention is dropped. The threat model for the gate is unreviewed protected *writes*, and a quoted mention performs no write.

Rollback: revert the IP-1 masking at the two call sites; the gate returns to raw-text scanning. The IP-2 tests document the desired behavior and may remain.

## Loyal Opposition Asks

1. Confirm that masking quoted spans for the named-command scan (`_has_mutating_signal` line 385) while leaving the redirect scan on the unmasked command is the correct split — i.e., reusing `_shell_redirect_present()` unchanged preserves redirect true-positives.
2. Confirm `mask_double=True` is the right choice for both sites (keywords and paths are literal inside either quote type), distinct from WI-3357's `mask_double=False` execution-marker case.
3. Confirm the scope boundary: this fix is disjoint from WI-3356 (redirect lookahead), WI-3357 (finalization exemption), and WI-3368/W4 (redirect-token replacement), and reuses the WI-3357 `_mask_quoted_spans` helper without re-opening those terminal threads.
4. Confirm the `_paths_from_shell` change adequately covers both the `PATH_TOKEN_RE.findall` site (line 197) and the `shlex.split` token loop (lines 198-207) for wholly-quoted-span tokens.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
