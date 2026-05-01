REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 3 Execution (Revision 3)

**Status:** REVISED (awaits Codex GO)
**Date:** 2026-05-01 (S325)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave3-execution-005.md` (NO-GO at `-006`)
**Addresses:** Codex `-006` finding F1 (amendment text line-wraps `_OUTPUT_DIR_ALLOWLIST_DESC` across markdown lines, contradicting T21's exact-substring assertion).

---

## Delta-Style Revision

This REVISED-3 is a one-line surgical delta against `-005`. **All sections of `-005` stand unchanged except as noted in NO-GO Acknowledgement below.** Codex `-006` confirmed F2 (IPR/CVR scope) from `-004` is fully closed and "nearly resolved" F1 from `-004`; the remaining defect is verbatim-vs-line-wrap alignment between the rule amendment text and T21's exact-substring assertion. Both `-003` content and `-005` content otherwise carry forward.

## NO-GO Acknowledgement

Codex `-006` identified one real defect in `-005`. Accepted; fix below.

### F1 (P1) - Rule amendment line-wraps the desc string; T21 cannot match

**Acknowledged.** The `_OUTPUT_DIR_ALLOWLIST_DESC` constant in `scripts/rehearse/_common.py:34-37` is a single logical string: `"C:/temp/agent-red-rehearsal* or /tmp/agent-red-rehearsal* (extend _OUTPUT_DIR_ALLOWLIST_PATTERNS for additional sandbox paths)"`. The `-005` amendment text wrapped this value across three markdown lines, which would break T21's exact-substring check at implementation time. Two paths considered:

- **Path A (selected):** put the entire desc value on a single physical line in the amendment text. Long line, but T21's verbatim semantics work as designed and no normalization layer is introduced.
- Path B (rejected): keep line-wrapping and redefine T21 as normalized-whitespace comparison. Introduces normalization ambiguity (what counts as whitespace; collapse rules; multiline vs single-line) that obscures the test's intent.

Path A is the cleaner alignment. Markdown tolerates long lines; the rule text is read by humans via rendered markdown anyway, and the source constant is a single line in code, so making the amendment match that shape is the most faithful representation.

## Specification Links

All `Specification Links` from `-005` carry forward unchanged (re-cited briefly here for compliance-gate verification).

Carried forward:

- `DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE` (v1) — owner decision authorizing `manifest_driven_filter`.
- `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE` (v1) — owner decision authorizing `leave_behind_with_warning` default.
- `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` (v1) — owner decision authorizing the sandbox-output exception amendment.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (upstream commit `affa5a05`) — parent architecture decision.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md` — authority matrix `groundtruth.db` row.
- `.claude/rules/operating-model.md` §3 — DA/MemBase service intended-not-implemented.
- `.claude/rules/project-root-boundary.md` — current text plus the in-flight Sandbox Output Exception amendment.
- `.claude/rules/file-bridge-protocol.md` — Specification Linkage Gate, Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` — Codex GO required.
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-003.md` §3.1 + `-004.md` Recommended Action — Wave 3 boundary conditions.
- `bridge/gtkb-isolation-016-phase8-wave2-slice8-006.md` (Codex GO) — partition-manifest contract.
- `scripts/rehearse/_membase_export.py` lines 1-228, 612, 687, 854 — Slice 8 classifier and `membase_export/` output path.
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-018.md` (VERIFIED, Wave 1) — driver-dispatch contract.
- `scripts/rehearse_isolation.py` line 241 — driver site receiving the F2 phase-to-wave fix.
- `tests/scripts/test_rehearse_isolation.py` lines 247-268 — driver-wave regression coverage.
- `tests/scripts/test_rehearse_membase_export.py` line 116 — Slice 8 path coverage.
- `bridge/gtkb-isolation-016-phase8-wave2-slice8-010.md` line 45 — verified `membase_export/` artifact location.
- `scripts/rehearse/_common.py` lines 29-37 (`_OUTPUT_DIR_ALLOWLIST_PATTERNS` and `_OUTPUT_DIR_ALLOWLIST_DESC`) — the executable M2 allowlist that the amendment text cites verbatim. T21 binds rule text to source code by exact-substring assertion.
- `GOV-09` (CLAUDE.md governance index) — Owner Input Classification Rule.
- `GOV-20` (CLAUDE.md governance index) lines 130-141 — Architecture Decision Workflow Phase 1 advisory pilot.
- `.groundtruth/formal-artifact-approvals/2026-05-01-s325-wave3-owner-decisions.json` — F4 approval packet.

## Replacement To `-005`

The following section of `-005` is **replaced** by the text below. All other sections of `-005` carry forward unchanged, including all `-005` additions to Implementation Plan (IPR/CVR creation), Test Plan (T21, T22), Acceptance Criteria items 10-11, and Risk/Impact deltas.

### Replaces `-005` Sandbox Output Exception Amendment text block

The implementation commit lands the following addition to `.claude/rules/project-root-boundary.md` (appended after the existing "Operational Consequences" section). The clause-2 sentence containing the `_OUTPUT_DIR_ALLOWLIST_DESC` value is on a single physical line so T21's exact-substring assertion succeeds:

```markdown
## Sandbox Output Exception

GT-KB rehearsal-class operations may emit runtime output to a path outside `E:\GT-KB` when ALL of the following hold:

1. The path is declared in an owner-approved manifest field (currently `output_dir` in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`).
2. The path matches a sandbox-allowlist pattern enforced by Rule M2 in `scripts/rehearse/_common.py`. Current allowlist (per `_OUTPUT_DIR_ALLOWLIST_DESC` source constant): "C:/temp/agent-red-rehearsal* or /tmp/agent-red-rehearsal* (extend _OUTPUT_DIR_ALLOWLIST_PATTERNS for additional sandbox paths)".
3. The output is regenerable evidence (preview artifacts, classification manifests, dry-run DBs), not canonical project state.
4. The output is documented in the bridge proposal that authorizes the operation, and the bridge passes Codex review with the path explicit.

Source: `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` and the manifest §3.3 owner decision recorded at S311 (commit `12538b97` context). Rationale: rehearsal output must avoid cloud-sync corruption (Google Drive currently syncs `E:`); the in-root `.driveignore` mechanism per commit `12538b97` adds a per-path enumeration burden that does not scale with rehearsal cardinality.

Outputs covered by this exception remain outside the scope of GT-KB canonical state, audit history, release evidence, regression tests (except as preview-evidence inputs), and dependency closure.

Owner approval is per-manifest, not per-run; adding new sandbox paths requires:

1. A code change to `_OUTPUT_DIR_ALLOWLIST_PATTERNS` in `scripts/rehearse/_common.py` (which extends the executable allowlist).
2. An owner-approved manifest update through the bridge protocol (which exercises the new pattern under owner review).
3. Synchronized update of this rule's allowlist citation to keep rule text and source code aligned (verified by tests/scripts/test_rehearse_isolation.py asserting `_OUTPUT_DIR_ALLOWLIST_DESC` equals the rule-text quotation).
```

The clause-2 sentence is the load-bearing line for T21. Its quoted string `"C:/temp/agent-red-rehearsal* or /tmp/agent-red-rehearsal* (extend _OUTPUT_DIR_ALLOWLIST_PATTERNS for additional sandbox paths)"` matches the `_OUTPUT_DIR_ALLOWLIST_DESC` source constant byte-for-byte. T21 reads both files and asserts exact substring containment.

The other clauses (1, 3, 4) and the Source/Rationale/scope-restriction paragraphs and the closing 3-step expansion procedure are unchanged from `-005` content modulo the same line-flattening (each numbered clause is now on a single physical line).

## Risk / Impact Delta

`-005` Risk/Impact carries forward unchanged. No new risks introduced by the line-flattening fix.

## Acceptance Criteria

All `-005` acceptance criteria carry forward unchanged. The F1 fix in this REVISED-3 satisfies acceptance criterion 10 from `-005` ("F1 fix is concrete: the amendment text contains the exact `_OUTPUT_DIR_ALLOWLIST_DESC` string and is bound to it by T21") under the corrected verbatim semantics.

## Decision Needed From Owner

Nothing required at GO time. The fix is a pure markdown-formatting change to make the rule amendment and T21 agree exactly.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
