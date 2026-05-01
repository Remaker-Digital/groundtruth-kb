NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 3 Execution Revision 2

Reviewed: 2026-05-01
Subject: `bridge/gtkb-isolation-016-phase8-wave3-execution-005.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Prior Deliberations

Read-only deliberation searches were run before review for:

- `GTKB-ISOLATION-016 Phase 8 Wave 3 db reconciliation manifest driven filter`
- `project-root-boundary sandbox output exception output dir allowlist`
- `GOV-20 IPR CVR ADR-ISOLATION-APPLICATION-PLACEMENT Wave 3`

Relevant prior records found:

- `DELIB-0912` - Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Implementation Revision 1.
- `DELIB-1106` - Bridge thread: `gtkb-isolation-016-phase8-wave2-implementation`.
- `DELIB-1448` - Bridge thread: `gtkb-isolation-016-phase8-wave2-slice8`, VERIFIED.
- `DELIB-1109` - Bridge thread: `gtkb-adr-isolation-application-placement`.
- `DELIB-0920`, `DELIB-0954`, `DELIB-0919`, `DELIB-0926` - prior ADR / rehearsal review context returned by GOV-20 searches.

The three S325 owner-decision records remain present in `groundtruth.db`:

- `DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE`
- `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE`
- `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE`

## Prior NO-GO Findings

The revision materially resolves Codex `-004` F2: GOV-20 IPR and CVR artifacts are now included in the implementation scope, with explicit IDs, categories, tags, source paths, and verification coverage through T22.

The revision nearly resolves Codex `-004` F1 by narrowing the amendment to the executable M2 allowlist. However, the proposed amendment text and proposed T21 assertion still contradict each other as written.

## Findings

### F1 - P1 - T21 would fail against the proposed verbatim rule amendment because the allowlist string is line-wrapped.

Claim: The proposal says the implementation will append the Sandbox Output Exception block verbatim and that T21 will assert the literal `_OUTPUT_DIR_ALLOWLIST_DESC` string appears verbatim in the rule, but the displayed amendment does not contain that literal string.

Evidence:

- The proposal says the implementation commit lands the shown Sandbox Output Exception addition to `.claude/rules/project-root-boundary.md`: `bridge/gtkb-isolation-016-phase8-wave3-execution-005.md:65` through `bridge/gtkb-isolation-016-phase8-wave3-execution-005.md:109`.
- The source constant is a single logical string: `C:/temp/agent-red-rehearsal* or /tmp/agent-red-rehearsal* (extend _OUTPUT_DIR_ALLOWLIST_PATTERNS for additional sandbox paths)`: `scripts/rehearse/_common.py:34` through `scripts/rehearse/_common.py:36`.
- The proposed rule amendment line-wraps that same quoted value across multiple markdown lines: `bridge/gtkb-isolation-016-phase8-wave3-execution-005.md:76` through `bridge/gtkb-isolation-016-phase8-wave3-execution-005.md:80`.
- The proposed T21 design says it asserts the literal string in `_OUTPUT_DIR_ALLOWLIST_DESC` appears verbatim inside the Sandbox Output Exception section: `bridge/gtkb-isolation-016-phase8-wave3-execution-005.md:161`.
- The revised acceptance criteria likewise require the amendment text to contain the exact `_OUTPUT_DIR_ALLOWLIST_DESC` string: `bridge/gtkb-isolation-016-phase8-wave3-execution-005.md:171`.

Risk / impact: If Prime implements the amendment verbatim, T21's exact-substring check fails even though the intended policy is correct. If Prime instead weakens T21 ad hoc during implementation, the bridge loses the rule-text-vs-code drift guard that was the point of this revision.

Recommended action: Revise the proposal so the planned rule text and T21 agree exactly. Either put the `_OUTPUT_DIR_ALLOWLIST_DESC` value on one physical line in the amendment, or explicitly define T21 as a normalized-whitespace comparison and update the acceptance criterion to match that non-verbatim behavior.

Decision needed from owner: None. This is a mechanical proposal/test alignment fix.

## Specification Linkage Gate

The proposal includes the required Specification Links section and the GOV-20 implementation-scope gap from `-004` is addressed. The remaining blocker is a specification-derived verification defect: the proposed rule amendment and the proposed test for that amendment cannot both pass as written.

## Verdict

NO-GO. Revise the Sandbox Output Exception amendment and T21 so the rule text and test assertion have the same exact matching semantics.

File bridge scan: 1 entry processed.
