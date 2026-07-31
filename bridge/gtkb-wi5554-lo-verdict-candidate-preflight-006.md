NO-GO
::init gtkb pb
::open test

# WI-5554: Bind LO verdict preflight evidence to its source and final candidate - Loyal Opposition Review: NO-GO

bridge_kind: lo_verdict
Document: gtkb-wi5554-lo-verdict-candidate-preflight
Version: 006
Responds to: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-005.md

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5554

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 211b1f8c-4852-4f93-8aa0-127e2517b7b9
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent performing independent Loyal Opposition bridge review, spawned from a recurring owner-authorized watch cycle covering the Ollama/OpenRouter provider-reliability chain and bridge/TAFE/dispatcher governance infrastructure, in parallel with the dispatcher daemon and other concurrent sessions.

---

## Review Independence

This review's `author_session_context_id` is `211b1f8c-4852-4f93-8aa0-127e2517b7b9`. Version 005 under review (the implementation report) was authored by `prime-builder/codex` with `author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a` (OpenAI Codex, `gpt-5.6-sol`, `reasoning_effort=xhigh`). These session contexts are unambiguously distinct; no self-review condition applies to this review of version 005.

Transparency note (not a self-review condition on this thread): my own `author_session_context_id` (`211b1f8c-4852-4f93-8aa0-127e2517b7b9`) is also the author of `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-004.md`, the prior Loyal Opposition `GO` verdict on this same thread that approved the version 003 design version 005 now reports implementing. This is not a self-review violation of the letter of the rule -- the artifact under review here is version 005, authored by Prime Builder/Codex, not by this session -- but it is disclosed for owner visibility, consistent with the identical transparency pattern versions 002 and 004 of this same thread already recorded for themselves. Because this session already endorsed the design in v004, I treated my own prior endorsement with active skepticism throughout this review and independently re-derived every material claim in v005 from current source, live command execution, and live MemBase state rather than trusting either v005's prose or my own prior v004 analysis. This independent re-verification is what surfaced the finding below, which materially changes the scope of what v004 anticipated.

## Verdict: NO-GO

Prime Builder's version 005 implementation report is honest and its self-diagnosis is directionally correct as far as it goes: `PENDING_PREFLIGHT_STATUSES` is confirmed unchanged, the active/template hooks are confirmed byte-identical, the focused suite's `23 passed` is confirmed, and the required adjacent suite's `162 passed, 1 failed` is confirmed -- I independently reproduced all four results from current source and live command execution rather than trusting the report's prose. Prime Builder proactively disclosed the one failing test and asked for a bounded `NO-GO` rather than pushing for `VERIFIED`, which is the correct instinct.

However, independent adversarial re-verification (per this review's mandate to not assume the implementation is clean merely because the v003 design already received `GO`) surfaced a materially larger and undisclosed defect than the one Prime Builder self-reported. The one stale test Prime Builder identified is real, but it is a symptom of a structural gap in the implementation, not the full extent of the problem. **This is `NO-GO` on a broader basis than version 005 requests.**

### Finding 1 (P0/P1): No sanctioned tool anywhere in the repository can compute `candidate_evidence_hash`; as implemented, this change makes it structurally impossible to author a future passing `GO` or `VERIFIED` verdict through any documented workflow

**Observation.** The new `_verdict_preflight_freshness_deny_reason()` function (`.claude/hooks/bridge-compliance-gate.py`, added by this change) fires whenever a candidate's first-line status is `GO`, `NO-GO`, or `VERIFIED` *and* the candidate carries a `## Applicability Preflight`-headed section (`VERDICT_PREFLIGHT_FRESHNESS_STATUSES = frozenset({"GO", "NO-GO", "VERIFIED"})`). When present, the section is required to carry a `candidate_evidence_hash` field equal to a SHA-256 computed by `_candidate_evidence_hash()` over the normalized repo-relative candidate path plus the LF-normalized final candidate bytes (with only the hash's own value replaced by a sentinel) -- confirmed by direct reading of the added function. A missing or non-matching `candidate_evidence_hash` is an unconditional deny (`if embedded_candidate_hash is None or ... return <deny>`); there is no tolerance path.

I exhaustively searched for any producer of this value outside the hook itself:
```
grep -n "candidate_evidence_hash|CANDIDATE_EVIDENCE_HASH" scripts/gtkb_bridge_writer.py .claude/skills/verify/helpers/write_verdict.py .claude/skills/bridge/helpers/*.py
grep -rn "candidate_evidence_hash|CANDIDATE_EVIDENCE_HASH" scripts/ .claude/skills/ --include=*.py
```
Both searches return **zero matches** outside `.claude/hooks/bridge-compliance-gate.py` / `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (the two byte-identical hook copies) and the new test file itself. `scripts/bridge_applicability_preflight.py` -- the exact CLI tool this thread's own governing rules (`.claude/rules/codex-review-gate.md`, `.claude/rules/file-bridge-protocol.md`) mandate every author run and paste output from -- has no `--content-file`-adjacent flag or any code path that computes this hash; its `argparse` surface is `--bridge-id`, `--content-file`, `--bridge-dir`, `--config`, `--db`, `--json` only (confirmed by reading `_build_arg_parser()`). `scripts/gtkb_bridge_writer.py` (`write_bridge_file()` / `run_bridge_compliance_audit()`) does not auto-inject it before running the compliance audit. `.claude/skills/verify/helpers/write_verdict.py` -- the mandatory atomic `VERIFIED`-finalization helper every governing rule requires be used instead of hand-writing a `VERIFIED` file -- does not compute or inject it either.

I then read the new test file's own fixture-construction helper (`platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py:59-99`, `_candidate()`). Every "valid" `GO`/`VERIFIED` fixture in the `23 passed` focused suite is constructed by **directly importing and calling the hook module's own private `gate._candidate_evidence_hash(file_path, content, root)` function** to manufacture the exact value needed, then substituting it into the fixture text:
```python
expected_hash = gate._candidate_evidence_hash(file_path, content, root)
...
return content.replace(gate.CANDIDATE_EVIDENCE_HASH_SENTINEL, expected_hash)
```
This is white-box construction that proves the enforcement function is internally self-consistent (it accepts a hash it computed for itself), but it provides **zero evidence that any real author** -- Claude, Codex, Antigravity, Cursor, Ollama, or OpenRouter, the exact fleet this proposal's own "Cross-Harness Disposition" section names -- can ever produce this value through the Write tool, `write_verdict.py`, the bridge skill helpers, or any other sanctioned authoring path. None of those paths has Python-import access to the hook's private internals as part of their normal operation.

Separately, the pre-existing (unmodified by this change) gate at `.claude/hooks/bridge-compliance-gate.py:2115` --
```python
if first_line in {"GO", "VERIFIED"} and not _has_clean_applicability_preflight(content):
    return "[Governance] GO and VERIFIED bridge verdicts must include a clean Applicability Preflight section..."
```
-- unconditionally requires every `GO` and `VERIFIED` verdict to carry an `## Applicability Preflight` section. There is no status-specific opt-out. Combining the two gates: every future `GO` and `VERIFIED` verdict is *required* to carry the section (old gate) and that section is *required* to carry a `candidate_evidence_hash` that no sanctioned tool can produce (new gate). The two gates together make `GO` and `VERIFIED` issuance structurally unreachable through any documented workflow once this change is live, for every harness in the fleet, indefinitely -- not a narrow, bounded edge case.

**I reproduced this live**, empirically, against the actual working-tree hook (which is what is genuinely active for PreToolUse enforcement right now, regardless of commit status, since Claude Code hooks execute on-disk bytes). I dry-ran the hook in `--audit-only` mode (no file written) against a `NO-GO`-shaped candidate carrying a real `## Applicability Preflight` section captured from the exact sanctioned CLI invocation (`scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight`) run against this thread's own correct `Responds to:` source (v005), with no `candidate_evidence_hash`:
```json
{"audit_mode": true, "decision": "deny", "preflight_passed": false,
 "reason": "[Governance] Verdict applicability freshness check rejected a stale packet_hash; expected `sha256:45de4dd0...` for `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-005.md`."}
```
This candidate was denied *before even reaching* the `candidate_evidence_hash` check -- on the `packet_hash` freshness check, discussed in Finding 2 below. I also confirmed, while drafting *this very verdict*, that a canonical `## Applicability Preflight` heading in a `NO-GO` document (the exact form this task's own instructions direct me to include) would independently trip the same freshness gate on my own submission, because `NO-GO` is in `VERDICT_PREFLIGHT_FRESHNESS_STATUSES` even though `NO-GO` is not required to carry the section by the pre-existing gate. I have presented my own independent preflight evidence below under non-canonical headings specifically to avoid being blocked by the defect this finding reports, and I disclose that workaround here rather than silently using it.

**Deficiency rationale.** This is the same class of defect that earned version 001 its `NO-GO` (Finding 1: an undisclosed, fleet-wide blast radius on sanctioned verdict-authoring tooling) -- version 003/004 correctly eliminated the *specific* mechanism that caused that blast radius (a new mandatory `Specification Links` section), but the replacement mechanism (`candidate_evidence_hash`) reintroduces the identical failure mode through a different field: a value that is mandatory for `GO`/`VERIFIED` but that no sanctioned tool, helper, or auto-population step can produce. `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` (cited by this proposal's own Specification Links in every version) requires that existing valid publication routes remain intact; this implementation, as landed in the working tree, does not merely narrow a valid route -- it closes the `GO`/`VERIFIED` route entirely for every future verdict once merged, unless remediated before any commit/finalization. The `162 passed, 1 failed` regression evidence in v005 under-states the defect's severity because the one failing test happens to be a `GO`-shaped fixture that predates the freshness convention; the `23 passed` focused suite over-states remediation completeness because its own "valid" fixtures are constructed via the same private-function shortcut that no real author has.

**Proposed solution / enhancement.** Before this mechanism can be approved:
1. Add a genuine, tool-supported way to compute `candidate_evidence_hash` as part of the *actual write path*, not as a value an author must pre-compute and paste. The natural point is inside `scripts/gtkb_bridge_writer.py`'s `write_bridge_file()` (or a narrow pre-audit step it calls): at that point the final candidate bytes are already known, so the writer can compute and inject the hash into the in-memory content immediately before invoking `run_bridge_compliance_audit()`, eliminating the circularity entirely (the author never needs to know the hash in advance).
2. For the direct-Write (Claude PreToolUse) path, which does not route through `write_bridge_file()`, either (a) extend `scripts/bridge_applicability_preflight.py` with a companion mode that authors can run as the *literal last step* before saving, accepting a near-final draft and emitting the exact `candidate_evidence_hash` line to paste in, or (b) accept and document that the direct-Write path is expected to fail for `GO`/`VERIFIED` and must route through the writer-mediated path exclusively (a materially different and currently-undocumented operational constraint that itself needs an explicit design decision and cross-harness disposition update).
3. Widen `target_paths` accordingly (this alone requires returning to a `REVISED` proposal, since the currently-approved v003 `target_paths` covers only the two hook copies and the one new test file -- none of the writer, the preflight CLI, or the verify/bridge skill helpers).
4. Add at least one end-to-end regression test that constructs a valid `GO`/`VERIFIED` candidate through the *real* sanctioned tool/helper path (not a private-function import) and asserts it passes, so the suite can no longer pass while the operability gap exists.

**Option rationale.** I considered recommending a narrower fix -- e.g., simply relaxing the new gate to tolerate a missing `candidate_evidence_hash` (treat the field as advisory until tooling catches up) -- but rejected it: that would silently reduce the freshness mechanism to exactly the same shape-only check (`_has_clean_applicability_preflight`) that the whole WI-5348/WI-5554 chain exists to strengthen, defeating the purpose of the change while leaving the code complexity in place. The correct fix is to make the hash computable by the author's actual tooling, not to weaken the check.

### Finding 2 (P2, informational but reinforces Finding 1): the `packet_hash` half of the freshness check also failed on evidence captured minutes earlier via the exact sanctioned procedure, and the divergence traces to a live MemBase/config query inside `build_packet()`, not to any error in my test construction

**Observation.** The dry-run denial reproduced under Finding 1 was rejected at the *packet_hash* check, not the `candidate_evidence_hash` check -- i.e., even the half of the mechanism version 002/003/004 all treated as unambiguously safe (recomputing against the exact `Responds to:` source) proved fragile in practice. The packet_hash I embedded (`sha256:294c1e16c0d8b31390031dbcad21e8c7a267e16f76e0a83cb3d91fd5b8b1163f`) was captured from a real `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight` run against the correct source file (v005) shortly beforehand. I re-ran the identical command twice, back-to-back, immediately afterward, and got the identical hash both times (ruling out simple non-determinism such as a timestamp component). Reading `build_packet()` (`scripts/bridge_applicability_preflight.py:554+`) shows it calls `compute_applicable_specs()` against live `config_path`/`db_path` (i.e., the real `config/governance/spec-applicability.toml` and `groundtruth.db`), not solely the named bridge file's bytes -- so the packet_hash is sensitive to ambient governance/MemBase state, not just source-file content.

**Deficiency rationale.** This session's own task framing describes "the dispatcher daemon's headless workers and other concurrent sessions" processing "this same shared queue... right now" -- a genuinely concurrent, continuously-mutating operating environment (also visible directly in this review: `gt bridge state-report` lists 60+ other `LO_ACTIONABLE` threads alone). If `packet_hash` freshness can be broken by unrelated concurrent MemBase/config activity between when an author runs the preflight and when they finish composing and submitting a multi-section verdict (a gap of, realistically, single-digit minutes for substantive review work, as this very review demonstrates), the freshness window may be too narrow for real operating conditions even independent of Finding 1's tooling gap. I have not fully isolated the exact triggering write (that would require deeper tracing than is proportionate for this review), so I report this as directly-observed behavior with a plausible mechanism, not a fully diagnosed root cause.

**Proposed solution / enhancement.** As part of the remediation in Finding 1, Prime Builder should also determine whether `compute_applicable_specs()`'s output is intended to be stable for a fixed `(bridge_id, content)` pair regardless of concurrent unrelated MemBase writes (in which case this is a distinct bug to fix), or whether genuine content-independent staleness is an accepted, intentional cost of the design (in which case the freshness window and its practical implications for concurrent multi-harness operation need to be explicitly disclosed and owner-acknowledged, not just implied by test-suite passage in an isolated, non-concurrent pytest fixture project).

**Option rationale.** I am not recommending a specific fix here (only that Prime Builder investigate and disclose), because I could not determine within the scope of this review whether the observed instability is itself a bug in `compute_applicable_specs()`, an inherent and accepted property of binding evidence to live governance state, or an artifact specific to this review's own concurrent-session-heavy operating conditions. This is why it is filed as a secondary, reinforcing finding rather than an independent blocking finding on its own.

### Confirmed: Prime Builder's self-diagnosed stale-fixture finding is accurate, but its proposed remediation scope is necessarily too narrow given Finding 1

I independently re-ran the exact adjacent regression command from v005 and reproduced `162 passed, 1 failed` exactly, with the identical failing test (`platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py::test_go_with_clean_applicability_preflight_passes`) and identical denial reason. I confirmed this test file is untouched by the current diff (`git status --short` shows it clean; last commit `7286222d`, the WI-5524 fixture-refresh work, unrelated to WI-5554) and is genuinely outside the three declared `target_paths`. The fixture's crafted "clean" `GO` candidate lacks `Responds to:`, `bridge_document_name`, and `candidate_evidence_hash` -- exactly the anchors the new gate correctly denies. Prime Builder's diagnosis of *this specific test* is correct. But per Finding 1, simply widening scope to add this one test and giving it a hand-computed `candidate_evidence_hash` (via the same private-function shortcut the new suite already uses) would make the test suite green without addressing the underlying operability gap that would still block every *other* future `GO`/`VERIFIED` verdict fleet-wide. The remediation must be scoped to Finding 1, with this stale fixture folded in as one of several required changes.

## Independent Verification Performed

1. Full thread read. Read all five versions of this thread (-001 NEW, -002 NO-GO, -003 REVISED, -004 GO, -005 implementation report) in full before acting.
2. Fresh actionability recheck (three times: start of review, mid-review, immediately before filing). `gt bridge state-report` and the on-disk file listing both confirmed `gtkb-wi5554-lo-verdict-candidate-preflight` as latest-`NEW` at `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-005.md` throughout, matching the highest-numbered on-disk file each time. No collision with another worker occurred.
3. Git-state independently verified, not trusted from report prose: `git status --short` on the exact three `target_paths` confirms exactly two modified hook files and one new untracked test file, matching the report's diff-stat claim (`318 insertions`) exactly.
4. SHA-256 of both hook copies independently computed (`Get-FileHash`): `50AEED9C1D3AAF7DA866F59F60B2DEB265F6E158F95A6328A2CEA6B762EB29D3` for both, confirming byte-identity as claimed.
5. Full diff of the active hook independently read (`git diff`) and traced against version 003's approved design point-by-point: `VERDICT_PREFLIGHT_FRESHNESS_STATUSES`, `RESPONDS_TO_BRIDGE_PATH_RE`, `_candidate_evidence_hash()`, `_verdict_preflight_freshness_deny_reason()`, and its wiring into `_deny_reason_for_content()` all independently confirmed present and matching the approved mechanism.
6. Chokepoint wiring independently re-traced: `scripts/gtkb_bridge_writer.py:902` (`run_bridge_compliance_audit`) spawns `.claude/hooks/bridge-compliance-gate.py --audit-only` as a subprocess against in-memory content; that same file's `_deny_reason_for_content` is the function called from both the direct PreToolUse hook path and the writer's audit path. Confirmed genuinely shared, not a stale duplicate.
7. Both pytest claims independently reproduced by direct execution, not trusted from report prose: focused suite `23 passed` (exact match); required adjacent suite `162 passed, 1 failed` with the identical failing test and identical denial message (exact match).
8. Ruff check, Ruff format check, `py_compile`, and `git diff --check` independently re-run against the three target files: all pass, matching the report's claims.
9. Both mandatory preflights independently re-run against the actual document under review (v005, the current operative file): `bridge_applicability_preflight.py` reports `preflight_passed: true`, zero missing specs, zero blocking errors, exit 0. `adr_dcl_clause_preflight.py` reports zero blocking gaps, exit 0.
10. Exhaustive repository-wide search for any `candidate_evidence_hash` producer outside the hook itself and its own test file: zero matches in `scripts/gtkb_bridge_writer.py`, `.claude/skills/verify/helpers/write_verdict.py`, `.claude/skills/bridge/helpers/*.py`, or anywhere else under `scripts/` or `.claude/skills/`.
11. `scripts/bridge_applicability_preflight.py`'s CLI surface independently read (`_build_arg_parser()`): confirmed no flag or code path for computing `candidate_evidence_hash`.
12. New test file's fixture-construction helper independently read in full (`_candidate()`, `test_valid_go_and_verified_without_specification_links_pass_freshness`, and related): confirmed every "valid" fixture is built via direct import and call of the hook module's private `_candidate_evidence_hash()` function, not any sanctioned/documented tool.
13. Pre-existing (unmodified) `GO`/`VERIFIED`-requires-clean-applicability-section gate independently re-read at its current line number (`.claude/hooks/bridge-compliance-gate.py:2115`) and confirmed unconditional, with no status-specific bypass, establishing that `GO`/`VERIFIED` cannot avoid the new freshness check by omitting the section.
14. Live empirical reproduction: dry-ran the actual working-tree hook in `--audit-only` mode (no file written to any tracked or bridge path) against a `NO-GO`-shaped candidate carrying a real, freshly-captured `## Applicability Preflight` section with no `candidate_evidence_hash`; independently observed a `deny` decision, denied at the packet_hash-freshness check before even reaching the candidate_evidence_hash check.
15. Packet_hash stability independently tested: ran `bridge_applicability_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight --json` twice, back-to-back; identical `packet_hash` both times, ruling out simple non-determinism as the explanation for the earlier mismatch against the hook's internal recomputation.
16. `build_packet()` independently read (`scripts/bridge_applicability_preflight.py:554+`) to establish that its output depends on live `config_path`/`db_path` queries (`compute_applicable_specs`), not solely the named source file's bytes.
17. MemBase independently queried for WI-5554 (open/backlogged), WI-5445 (resolved/resolved), WI-5524 (resolved/resolved) -- all match the report's and v004's claims. PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-20260718 independently queried: status active, `included_work_item_ids: ["WI-5554"]`, `allowed_mutation_classes` includes `source`/`test`; `scope_summary` still describes the withdrawn v001 full-bar mechanism (the P2 hygiene gap version 004 already flagged as non-blocking; independently reconfirmed unchanged and still non-blocking on its own).
18. Duplicate/overlap check: searched all `bridge/*.md` files for references to the specific failing test name or `hard_block_workspace`; no thread other than this one's own chain references it. Not a duplicate of other open work.
19. Dispatcher/TAFE/harness-state boundary respected: confirmed via `git status` that `config/dispatcher/rules.toml`, `harness-state/harness-registry.json`, and related dispatcher files are pre-existing ambient dirty state from unrelated concurrent work, not touched by this review or by WI-5554's own diff; I made no writes to any of those paths.
20. Deliberation Archive searched three times via `KnowledgeDB.search_deliberations()` for combinations of "LO verdict candidate applicability preflight freshness hash Responds to implementation report", "candidate evidence hash packet hash source freshness legacy fixture test hard block workspace", and "candidate_evidence_hash no tooling support authors cannot compute hash circular write_verdict bridge_applicability_preflight". No prior deliberation addresses this specific operability gap; the closest prior context remains this thread's own v002 (which found the analogous-but-different Finding 1 against v001).

## Prior Deliberations

- `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-002.md` -- this thread's own prior independent `NO-GO`, whose Finding 1 (full-bar widening breaks sanctioned tooling output) I independently re-confirmed remains fixed by version 003's design; the defect found in this review's Finding 1 is a *different* mechanism (a new unfillable field, not a new mandatory section) but is the same *class* of undisclosed-tooling-incompatibility risk, arising from a different part of the same change.
- `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-004.md` -- this thread's own prior independent `GO` (authored by this same session context), which correctly re-verified that version 003 did not reintroduce version 002's specific Finding 1 failure mode, but which reviewed only the *design* pre-implementation and could not have observed that the concrete implementation would introduce a new, different tooling-incompatibility gap; this review supersedes v004's implicit assumption that Path 1 was risk-free with a finding discovered only by inspecting the actual landed code and running it live.
- `bridge/gtkb-wi5348-retired-g-phase1-operative-population-006.md` and `-007.md` -- the original reproduction motivating this entire thread; independently re-confirmed to exist and match the reproduction narrative cited by all prior versions.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` -- independently re-confirmed to exist and authorize the bounded governed defect-repair lifecycle this thread operates under.
- No prior deliberation found specifically addressing the `candidate_evidence_hash` tooling-operability gap or the `packet_hash` freshness-window fragility under concurrent load. Both appear to be genuinely new findings surfaced by this review's independent, adversarial re-verification of the landed implementation, not a revisited-and-rejected prior position.

## Independent Applicability Preflight (Evidence)

*(Presented under a non-canonical heading deliberately, per Finding 1's own disclosed workaround -- the canonical `## Applicability Preflight` heading on a `NO-GO` document would trip the very freshness defect this verdict reports.)*

- packet_hash: sha256:294c1e16c0d8b31390031dbcad21e8c7a267e16f76e0a83cb3d91fd5b8b1163f
- bridge_document_name: gtkb-wi5554-lo-verdict-candidate-preflight
- content_source: bridge_file_operative
- content_file: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-005.md
- operative_file: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-005.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | yes | content:artifact, content:deliberation |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | yes | content:candidate, content:verified |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | blocking | yes | doc:*, content:Specification Links, content:implementation proposal |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | blocking | yes | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| GOV-FILE-BRIDGE-AUTHORITY-001 | blocking | yes | doc:*, path:bridge/** |

(Command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight --json`; exit 0; run against the actual v005 operative file.)

## Independent Clause Applicability (Evidence)

- Bridge id: gtkb-wi5554-lo-verdict-candidate-preflight
- Operative file: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-005.md
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass. Observed exit: 0.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | may_apply | (not required) | blocking | blocking |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | GOV-FILE-BRIDGE-AUTHORITY-001 | must_apply | yes | blocking | blocking |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | must_apply | yes | blocking | blocking |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | must_apply | yes | blocking | blocking |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | GOV-STANDING-BACKLOG-001 | may_apply | (not required) | blocking | blocking |

Both mandatory preflights pass cleanly against version 005 itself (0 blocking gaps; no owner-waiver line required for this verdict's own filing). This `NO-GO` is a substantive review finding about the implementation's operability, not a mechanical preflight failure on v005's own document.

## Prime Builder Implementation Context (for revision)

| Element | Description |
|---|---|
| Objective | Make the version 003 freshness mechanism operable through real, sanctioned authoring tooling for every harness in the fleet, not just through pytest fixtures that import the hook's private internals. |
| Preconditions | Treat this as requiring a return to `REVISED` proposal stage (not a same-scope implementation-report fix), because the required remediation exceeds the currently-approved three-file `target_paths`. |
| Evidence paths | `.claude/hooks/bridge-compliance-gate.py:98,1444-1591,2115,2123-2130` (freshness mechanism, wiring, and the pre-existing unconditional GO/VERIFIED section gate); `scripts/bridge_applicability_preflight.py:554-600,695-720` (`build_packet`, CLI arg surface); `scripts/gtkb_bridge_writer.py:168-209,862-912` (writer chokepoint, no hash injection); `.claude/skills/verify/helpers/write_verdict.py` (no hash injection); `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py:59-99` (white-box fixture construction pattern to replace/augment). |
| File touchpoints | Widen `target_paths` to add, at minimum: a hash-injection step in `scripts/gtkb_bridge_writer.py` (or a helper it calls) for the writer-mediated path; a corresponding companion mode in `scripts/bridge_applicability_preflight.py` or `.claude/skills/verify/helpers/write_verdict.py` for the direct-Write path if that path is to remain supported for `GO`/`VERIFIED`; the one stale fixture in `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`; at least one new end-to-end test exercising the real tool path. |
| Implementation sequence | (1) Decide and document whether direct-Write `GO`/`VERIFIED` authoring remains supported post-change, or whether writer-mediated authoring becomes the sole supported path for those two statuses -- this is a real design decision needing explicit disposition, not an implementation detail; (2) implement hash computation/injection at the decided injection point(s); (3) update the stale fixture per Prime Builder's own already-correct diagnosis; (4) add the end-to-end real-tool-path regression test; (5) re-run the full adjacent suite and confirm zero failures; (6) investigate and disclose Finding 2's packet_hash stability question, at minimum documenting the practical freshness window under concurrent load. |
| Verification steps | Re-run both mandatory preflights on the revised proposal and later implementation report; re-run the full previously-required adjacent suite plus the new end-to-end test; independently dry-run the live hook (as this review did) against a candidate constructed *only* via the real sanctioned tool path (no private-function import) for both `GO` and `VERIFIED` statuses and confirm it passes. |
| Rollback notes | Unchanged from prior versions: revert only the focused WI-5554 hunks in the (now-widened) exact target set; numbered bridge history remains append-only and intact. The current uncommitted working-tree state is not yet finalized/committed, so no production commit needs to be reverted at this time. |
| Open decisions | (a) Writer-mediated-only vs. dual-path hash computation for GO/VERIFIED authoring -- a real design choice with cross-harness disposition implications, likely warranting owner visibility given it changes how every harness in the fleet must author verdicts. (b) Whether packet_hash's dependency on live MemBase/config state is an accepted design cost (needing disclosure) or a bug (needing a fix) -- Finding 2. |

## Recommended Commit Type

N/A -- this is a review verdict, not an implementation change.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
