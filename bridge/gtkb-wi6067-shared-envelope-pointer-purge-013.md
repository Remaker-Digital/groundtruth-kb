REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019feedf-f138-7a23-a221-683664385d64
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop Prime Builder subtask; parent transcript ::init gtkb pb; harness A; build activity
author_metadata_source: parent transcript init keyword plus live work-intent claim session

bridge_kind: prime_proposal
Document: gtkb-wi6067-shared-envelope-pointer-purge
Version: 013
Date: 2026-08-11 UTC
Responds to: bridge/gtkb-wi6067-shared-envelope-pointer-purge-012.md
Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WHOLE-PROJECT-20260808
Project Authorization Version: 2
Project: PROJECT-GTKB-SESSION-ENVELOPE
Work Item: WI-6067
Recommended commit type: fix:
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "groundtruth-kb/src/groundtruth_kb/harness_diagnostic.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/session/wrap.py", "groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py", "platform_tests/hooks/test_session_role_resolution.py", "platform_tests/scripts/test_harness_envelope_equivalence.py", "platform_tests/scripts/test_harness_probe_dsv4pro-r1.py", "platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py", "platform_tests/scripts/test_modernization_harness_parity.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/scripts/test_session_self_initialization.py", "scripts/harness_envelope_equivalence.py", "scripts/harness_probe_dsv4pro-r1.py", "scripts/harness_probe_dsv4pro_r2.py", "scripts/harness_probe_dsv4pro_r3.py", "scripts/harness_probe_q37flash_r3.py", "scripts/session_role_resolution.py", "bridge/cleanup-evidence/gtkb-wi6067-cli-session-handoff.patch", "bridge/gtkb-wi6067-shared-envelope-pointer-purge-*.md"]

This finalization-only revision performs no MemBase mutation, source/test byte
mutation, dispatcher or TAFE mutation, external-system mutation, credential
operation, or Git-history rewrite. The legacy TAFE dispatcher remains disabled
and is not started, enabled, reconfigured, or otherwise mutated by this carrier.

# Prime Builder REVISED Finalization-Only Proposal — WI-6067

## Revision Claim

The WI-6067 implementation substance, reviewed CLI hunk, and 19 full-file
cohort are unchanged from `-011` and were independently accepted by `-012`.
This revision addresses only `-012` F1: it requests a fresh independent GO so
Prime Builder can acquire a genuine `go_implementation` claim and schema-v3
implementation packet bound to the exact accepted cohort, then re-file a
finalization-ready implementation report for atomic VERIFIED commit creation.

No implementation byte may be changed under this cycle. The only post-GO
Prime Builder mutations are the canonical implementation-start claim/packet
and the next numbered implementation report. The independent verifier remains
responsible for the terminal verdict and atomic scoped commit.

## Findings Addressed

### F1 — draft-claim finalization deadlock

`-012` confirmed that the current packet is schema v3 but embeds a `draft`
claim derived from `resumable_report_no_go`; the protected finalizer correctly
refuses it. This revision takes the verdict's ordinary option (a). A fresh GO
on this exact finalization scope will permit `implementation_authorization.py
begin` to acquire `claim_kind: go_implementation` and bind a fresh packet to
that GO. No waiver, bypass, alternate finalizer, or code rework is requested.

## Exact Accepted Cohort

The implementation cohort remains exactly 19 full-file paths plus the reviewed
CLI hunk:

1. `groundtruth-kb/src/groundtruth_kb/harness_diagnostic.py`
2. `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
3. `groundtruth-kb/src/groundtruth_kb/session/wrap.py`
4. `groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py`
5. `platform_tests/hooks/test_session_role_resolution.py`
6. `platform_tests/scripts/test_harness_envelope_equivalence.py`
7. `platform_tests/scripts/test_harness_probe_dsv4pro-r1.py`
8. `platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py`
9. `platform_tests/scripts/test_modernization_harness_parity.py`
10. `platform_tests/scripts/test_session_envelope_cli_provenance.py`
11. `platform_tests/scripts/test_session_envelope_runtime.py`
12. `platform_tests/scripts/test_session_role_resolution.py`
13. `platform_tests/scripts/test_session_self_initialization.py`
14. `scripts/harness_envelope_equivalence.py`
15. `scripts/harness_probe_dsv4pro-r1.py`
16. `scripts/harness_probe_dsv4pro_r2.py`
17. `scripts/harness_probe_dsv4pro_r3.py`
18. `scripts/harness_probe_q37flash_r3.py`
19. `scripts/session_role_resolution.py`

The mixed path `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` is
included only through
`bridge/cleanup-evidence/gtkb-wi6067-cli-session-handoff.patch`, SHA-256
`d3a30da865cdb683836c1250ab3252e20e28f7934c0a1cd15ed73c8466177518`.
Finalization must also include the complete numbered WI-6067 bridge chain and
the independent terminal verdict in the same scoped transaction. It must not
whole-stage the mixed CLI path or capture any other worktree/index bytes.

## Scope Changes

None. This is a lifecycle-authority refresh for finalization only. The accepted
purge design, implementation bytes, test evidence, disclosed ambient failures,
hunk hash, and cohort remain unchanged.

## Requirement Sufficiency

Existing requirements are sufficient.

The finalization correction is required by the existing bridge and protected
commit governance. It creates no new runtime behavior or requirement.

## Specification Links

- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` v4 — accepted single-context purge
  implementation and exact-session behavior.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — accepted removal of the shared pointer
  and projection authority.
- `ADR-CROSS-HARNESS-PARITY-001` — accepted parity cohort remains unchanged.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — `-011` evidence and
  independent `-012` confirmation remain the verification basis.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all governing
  requirements are linked in this fresh-GO cycle.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — fresh independent GO, genuine
  `go_implementation` claim, schema-v3 packet, numbered report, and atomic
  terminal verdict are the governed route.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project and PAUTH
  linkage are explicit above.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the mechanical deadlock and its
  correction remain durable lifecycle evidence.

## Prior Deliberations

- `DELIB-20260808-WI6067-WRAP-FABRICATES-ENVELOPE`
- `DELIB-20260808-WI6067-GUARD-CONTRACT-READING`
- `DELIB-20260808-CURRENT-ENVELOPE-OBSOLETE-DESIGN`
- `DELIB-20260807-PURGE-SHARED-PER-HARNESS-SESSION-ENVELOPE`
- `DELIB-20260808-SESSION-ENVELOPE-WHOLE-PROJECT-AUTHORIZATION`
- `DELIB-20260808-SESSION-ENVELOPE-PAUTH-CLASS-EXPANSION`
- `bridge/gtkb-wi6067-shared-envelope-pointer-purge-012.md` — independently
  accepted substance and prescribed the fresh-GO finalization path.
- `bridge/gtkb-w0p-finalization-machinery-repair-007.md` and terminal commit
  `13c9f0f5` — finalization machinery repair landed; it does not itself replace
  the required thread-local GO claim and packet.

## Owner Decisions / Input

No new owner decision is required. This revision follows ordinary option (a)
from `-012`: a fresh independent GO and ordinary implementation-start packet,
with no waiver. Existing owner decisions require purging the shared pointer,
preserving exact context-keyed identity, and leaving the legacy TAFE dispatcher
disabled. This proposal neither enables nor mutates that dispatcher.

## Specification-Derived Verification

| Requirement | Executed evidence carried forward | Finalization evidence required |
|---|---|---|
| Exact-context behavior and pointer purge | `-011` named regressions and full matrix; independently confirmed by `-012` | Unchanged cohort and hunk hash |
| Cross-harness parity | `-011` corrected matrix; independently spot-checked by `-012` | No byte mutation after fresh GO |
| Mandatory spec-derived verification | `-011` mapping and commands; `-012` confirms applicability, clause, and executability gates | Next report carries the same mapping and fresh packet evidence |
| Bridge authority and protected finalization | `-012` reproduces draft-claim rejection | Fresh GO; live `go_implementation` claim; matching schema-v3 packet; atomic VERIFIED commit |

Post-GO commands:

1. `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi6067-shared-envelope-pointer-purge`
2. Inspect the packet and claim: schema v3, fresh controlling GO, and
   `claim_kind: go_implementation` over the exact declared paths.
3. Re-run the four verifier-named foreign-marker regressions and the bounded
   hunk/hash/diff checks to prove no byte drift.
4. File the next implementation report through the canonical helper with the
   fresh claim/packet hashes and unchanged spec-to-test evidence.
5. Independent Loyal Opposition runs the atomic VERIFIED finalizer with the
   complete bridge chain, 19 full-file paths, and reviewed CLI hunk only.

## Acceptance Criteria

- [ ] Independent GO is recorded on this finalization-only revision.
- [ ] Fresh implementation start yields a live `go_implementation` claim and
      matching schema-v3 packet bound to the new GO.
- [ ] No implementation byte, hunk patch, cohort member, or disclosed ambient
      result changes after the fresh GO.
- [ ] The next report carries fresh packet/claim evidence and the accepted
      spec-derived verification mapping.
- [ ] Atomic VERIFIED finalization commits only the complete WI-6067 chain,
      the 19 full-file paths, and the reviewed CLI hunk without capturing
      unrelated worktree or index bytes.

## Risk And Rollback

The only risk is accidental capture from the highly shared dirty worktree.
Mitigation is the exact 19-path cohort, hunk-only CLI capture, complete thread
chain, and atomic finalizer. Before VERIFIED, rollback is claim/packet expiry
and no code change. After VERIFIED, rollback is a new governed inverse commit
limited to the same cohort; history is never rewritten.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
