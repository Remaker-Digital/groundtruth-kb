NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: S-claude-opus48-2026-06-22-wi4746
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: opus-4-8-1m-context

# Bridge-compliance-gate test hygiene + `_pending_proposal_ask_reason` whole-bridge-dir scan hang fix

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-4746-BRIDGE-COMPLIANCE-GATE-TEST-HANG-FIX
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4746
target_paths: ["platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py", "platform_tests/hooks/test_bridge_compliance_gate_w4_calibration.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py"]

## Summary

Two pre-existing test failures in the bridge-compliance-gate suite are fixed, and the gate's `_pending_proposal_ask_reason` ask-checkpoint is hardened so it no longer reads the entire `bridge/` directory (7,845 files; 7,835 versioned) on every non-bridge Write/Edit. The fix is **decision-preserving**: the gate's deny/ask DECISIONS are unchanged; only the test API surface and the read pattern change. This change touches only two test files and the bridge-compliance-gate hook source (live + scaffold template); it performs no MemBase / `groundtruth.db` mutation and no spec/work-item record changes.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — legacy file-bridge compatibility + permanent bridge-repair authority; the compliance gate is the mechanical enforcement surface for this authority.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — proposal-spec-linkage contract enforced by this hook.
- DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001 — cited by the W4 calibration suite under repair.
- `.claude/rules/bridge-essential.md` — bridge integrity is the top-priority duty; the compliance gate is critical bridge infrastructure, so its tests and runtime cost are a bridge-reliability concern.
- `.claude/rules/file-bridge-protocol.md` — versioned-file status semantics and the post-cutover rule that TAFE/dispatcher state plus status-bearing versioned files are canonical (no aggregate INDEX.md).
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the VERIFIED spec-derived-testing gate; the implementation report's spec-to-test mapping and executed-test evidence must satisfy this before VERIFIED.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) — artifact-oriented development stance; this fix is captured as a durable WI with linked DELIB and tests.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) — artifact lifecycle triggers; the defect is tracked as WI-4746 under the standing backlog with verification artifacts.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) — artifact-oriented governance default; the work is represented as MemBase work-item + deliberation + spec-derived tests rather than chat-only context.

## Prior Deliberations

- DELIB-20263739 (GO) and DELIB-20263738 (VERIFIED) — the original "Bridge Compliance Gate INDEX Exemption" thread (`bridge/gtkb-bridge-compliance-gate-index-exemption-*`, WI-3334). The `index_exemption` test under repair was written against that now-superseded implementation (`_is_bridge_index_file` + the old `_pending_proposal_ask_reason` signature).
- DELIB-20262020 — records that the `gtkb-bridge-compliance-gate-index-exemption` bridge thread is now compressed/ORPHAN, confirming the tested implementation has been superseded (INDEX.md was retired at the 2026-06-15 TAFE/dispatcher cutover; `_is_retired_bridge_aggregate_file` now DENIES `bridge/INDEX.md` rather than exempting it).
- DELIB-20260621-BRIDGE-COMPLIANCE-GATE-TEST-HYGIENE-HANG-FIX-SCOPE — the owner scope decision authorizing this work (AskUserQuestion: "Tests + fix hook hang now").

## Requirement Sufficiency

Existing requirements are sufficient. This is a defect fix against the established bridge-compliance-gate contract (GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001) and the canonical-source rule in `.claude/rules/file-bridge-protocol.md`; no behavior contract is added or changed. The two test files are realigned to the current hook API, and the runtime read pattern is optimized without altering any deny/ask decision the gate produces.

## Owner Decisions / Input

This work is authorized by owner decision **DELIB-20260621-BRIDGE-COMPLIANCE-GATE-TEST-HYGIENE-HANG-FIX-SCOPE**, captured from an AskUserQuestion in this session. The owner was shown the corrected diagnosis (the original "import cost / opentelemetry exceeds 15s" hypothesis was falsified by measurement: imports ~1s; the hook hangs >120s; no opentelemetry in the chain) and selected the option **"Tests + fix hook hang now"** over the recommended "test-only rewrite + backlog the hang separately" and over "retire the stale tests". The owner constraint recorded with that decision: the hook fix must be **decision-preserving** (must not change the gate's deny/ask decisions).

## Root-Cause Analysis (evidence)

### Failure 1 — `test_bridge_compliance_gate_index_exemption.py` (8/14 fail; rest pass vacuously)

The test targets a superseded hook API:
- `gate._is_bridge_index_file(...)` raises `AttributeError` — the function was removed. Its role moved to `_is_retired_bridge_aggregate_file`, which recognizes `bridge/INDEX.md` but now produces a DENY (`"Retired bridge aggregate files are not live or writable"`), not an exemption. INDEX.md was retired at the 2026-06-15 cutover.
- `_pending_proposal_ask_reason` was rewritten from an INDEX-aggregate parser to the signature `_pending_proposal_ask_reason(project_root, file_path)` that scans versioned `bridge/*.md` files. The test calls it with an INDEX.md path as the first arg, so the `non_index_target` cases fail `assert None is not None`, and the `is_exempt` cases pass *vacuously* (the function globs a nonsense path and returns None).

Validated current-API behavior (live hook): `_is_retired_bridge_aggregate_file("bridge/INDEX.md")` → True (decoys → False); `_deny_reason_for_content(file_path="bridge/INDEX.md", ...)` returns the retired-aggregate deny; `_pending_proposal_ask_reason(tmp_root, "scripts/feature.py")` with a versioned `NEW` fixture → `"pending Codex review (NEW)"`; with a `NO-GO@002` over `NEW@001` → `"NO-GO status"`.

### Failure 2 — `test_bridge_compliance_gate_w4_calibration.py` (4/4 fail with `subprocess.TimeoutExpired`)

Measured: `groundtruth_kb.governance.output` imports in ~0.99s; no opentelemetry/protobuf in the import chain; the hook subprocess hangs **>120s** (not slow imports). The W4 fixtures use **non-versioned** paths (`bridge/test-w4-*.md`) on the old assumption that `_is_bridge_markdown_file` routes them through the spec-links gate. That contract tightened to require the `-NNN.md` suffix (`BRIDGE_VERSIONED_FILE_RE`), so the fixtures fall through `main()` to `_pending_proposal_ask_reason(_canonical_project_root(cwd), file_path)`, which globs and `read_text()`s **all 7,835 versioned files** in the real cloud-synced `E:/GT-KB/bridge/` directory. That scan is the hang. "Raise the subprocess timeout" cannot work — pytest caps every test at 30s (`timeout: 30.0s`); "defer imports" fixes nothing (~1s). `os.scandir` of `bridge/` (names only) is 2.83s, so the cost is dominated by the ~7,800 file opens, not bytes or imports.

The same root cause (the tightened `_is_bridge_markdown_file` contract) breaks both suites and exposes a **production latency risk**: `_pending_proposal_ask_reason` runs on every non-bridge Write/Edit at the repo root, so the gate can hang for minutes whenever the OS cache is cold.

## Proposed Changes

### A. Rewrite both test files to the current hook API (unit-level; no subprocess scan of the real `bridge/` dir)

- `test_bridge_compliance_gate_index_exemption.py`: replace the `_is_bridge_index_file` unit cases with `_is_retired_bridge_aggregate_file` cases (recognizes `bridge/INDEX.md`, rejects decoys) plus a `_deny_reason_for_content` case asserting `bridge/INDEX.md` is now DENIED — preserving "INDEX.md is special" coverage under the current model. Replace the obsolete `is_exempt` cases accordingly. Rewrite the `_pending_proposal_ask_reason` cases to the current `(project_root, file_path)` signature using **versioned** bridge-file fixtures under `tmp_path` (`<slug>-001.md` first line `NEW`/`REVISED` + `target_paths:` line; `<slug>-002.md` first line `NO-GO` for the NO-GO case), passing `tmp_path` as `project_root`. Keep the live+template parametrization.
- `test_bridge_compliance_gate_w4_calibration.py`: replace the subprocess `_run_hook` calls with direct unit-function assertions on the IP-3/IP-5 predicates (`_specification_links_heading_misdetected`, `_has_concrete_spec_links`, `_ask_reason_for_content`, `_deny_reason_for_content(run_pending_preflight=False)`), parametrized over live+template. This exercises the exact IP-3/IP-5 calibration logic without the real-bridge-dir scan and without the layered status-gate interactions that a versioned subprocess fixture would trip. (Tradeoff: drops the end-to-end `main()` JSON-emission assertion; that wiring is covered by the existing body-status-token subprocess suite and a single retained smoke check.)

All rewritten assertions were validated against the live hook in this session.

### B. Harden `_pending_proposal_ask_reason` (decision-preserving), applied to live + scaffold template in parity

1. **Highest-version-only status read.** `_versioned_bridge_entries` currently opens every version of every slug to take the highest-version status after sorting. Group versioned files by slug from filenames (scandir; no opens), then open only the max-version file per slug to determine latest status. Decision-identical (latest status lives in the highest-version file); ~4x fewer opens. `target_paths` for the few pending (NEW/REVISED/NO-GO) slugs are still read from their NEW/REVISED file exactly as today.
2. **Lighter first-line read.** Replace `path.read_text()` (entire file) with a streamed read of only the first non-blank line for status detection. Decision-identical; fewer bytes per open.
3. **Signature-keyed cache (fail-soft).** Cache the pending-proposal target-path map under `.gtkb-state/bridge-compliance/` keyed on a cheap `os.scandir` signature (file count + max mtime; no file opens). On a signature match, reuse the cache (no per-file opens). On any miss or error, fall back to the full (now highest-version-only) scan and rebuild the cache atomically. The append-only bridge protocol guarantees a signature change whenever a new version is added, so a cache hit yields exactly the result a full scan would. Worst case equals today's behavior (correct, slower).

No deny/ask DECISION changes: the same statuses, the same target-path matching, the same returned reasons. Only the I/O path changes. A follow-on backlog item is proposed for the deeper fix (a pre-warmed / incrementally-maintained status index, the architectural successor to the retired aggregate INDEX) — out of scope here.

## Specification-Derived Verification

Spec-to-test mapping and executed commands:

- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 / GOV-FILE-BRIDGE-AUTHORITY-001 → the rewritten `index_exemption` + `w4_calibration` suites assert the gate's current spec-links / retired-aggregate / pending-proposal behavior. Command: `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py platform_tests/hooks/test_bridge_compliance_gate_w4_calibration.py -v`.
- Decision-preservation (the load-bearing constraint) → a new test asserts `_pending_proposal_ask_reason` returns byte-identical reasons via the cache path and the full-scan path for a battery of fixtures (NEW / REVISED / NO-GO / unmatched), and that cache-miss falls back correctly. Command: same pytest invocation.
- Regression floor → the full hook suite stays green: `python -m pytest platform_tests/hooks/ -q`.
- Lint + format gates → `ruff check` and `ruff format --check` on the changed files (separate gates).

Acceptance: all targeted tests pass; no subprocess reads the real `bridge/` directory; `_pending_proposal_ask_reason` performs no full versioned-file read on a cache hit; gate deny/ask decisions unchanged; live and template hooks remain in parity.

## Risk and Rollback

- Risk: a cache staleness bug could change an ask decision. Mitigated by append-only signature invariance + fail-soft fallback to the full scan + an explicit decision-preservation test. Rollback: revert the four files; the cache is regenerable runtime state under `.gtkb-state/`.
- Risk: the unit-level W4 rewrite drops end-to-end `main()` coverage. Mitigated by a retained smoke check and the existing body-status-token subprocess suite.
- Scope guard: no enforcement-decision change; no MemBase mutation; live + template parity verified.

## Recommended Commit Type

`fix:` — repairs two broken test suites and a latent runtime hang in critical bridge infrastructure; no new capability surface.
