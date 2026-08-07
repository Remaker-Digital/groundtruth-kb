NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 6d5cabf5-dc7d-418a-a495-6f23186a6638
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role via ::init gtkb pb; dispatcher and TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context

# GT-KB Bridge Implementation Report — WI-5949 applicability packet determinism — 003

bridge_kind: implementation_report
Document: gtkb-wi5949-applicability-packet-determinism
Version: 003
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5949-applicability-packet-determinism-002.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5949

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

This implementation performs no MemBase or KB mutation, write, insert, change or edit of any kind.

## Summary

`build_packet` now pins the thread chain to the prefix through the pinned report, so `packet_hash` for a fixed report no longer moves when later versions land on the same thread. Both declared paths changed; nothing else did.

## Implementation-Start Authority

- Fresh `go_implementation` work-intent claim rowid `36911`.
- Implementation-start packet from GO v002: `latest_status: GO`, `go_file: bridge/gtkb-wi5949-applicability-packet-determinism-002.md`, `pre_start_packet_hash: sha256:da740eff5bf2d760d15b87a4e0b85a04362a3328cbb592150a96663858b6793f`.
- Acceptance criterion 8 readback before any edit: both declared targets `git status --short` clean at HEAD `7d6b00f68`; no live-GO thread declares either path. Checked explicitly against `gtkb-wi5950-publication-capability-recovery`, `gtkb-w0-executable-go-pre-verdict-validation`, `gtkb-w0-gate-false-positive-repair`, `gtkb-w0-skill-rename-path-repair` and `gtkb-wi5867-protected-commit-gate-contention-attribution` — zero overlap on each.

## Change Implemented

`scripts/bridge_applicability_preflight.py`, one hunk inside `build_packet`'s pinned branch:

When the pinned `content_file` resolves to a canonical in-`bridge/` version, `versions` is restricted to entries at or below that version before it reaches `_pauth_phase`, `_approved_proposal_for_report` and `_pauth_phase_cohort`. Those three consumers are the routes by which chain state entered the hashed packet.

Each consumer asks a question about the report's own history — which phase it is in, which GO approved it, which cohort it governs — so a prefix restriction preserves their semantics exactly while removing the dependency on versions published afterwards. The comment block in the diff records that reasoning and the failure it prevents, so a future reader does not "simplify" the truncation away.

The unpinned path is untouched: with no pinned report, the chain tail is the subject, and `choose_operative_version` continues to select it.

### Correction made during implementation

The first attempt truncated on `operative`, which is `explicit_version or scanned_operative`. That was wrong and the existing suite caught it immediately: `test_pauth_phase_cohort_allowed_and_reported` and `test_pauth_proposal_allowed_finalization_denied_when_bridge_class_missing` both failed with `status == "error"`.

The cause is that pending content held **outside** `bridge/` yields `explicit_version is None`, because `_canonical_explicit_version` requires the file's parent to be the bridge directory. `operative` then falls back to the scanned tail, which can be *earlier* than the pending artifact's own version — those fixtures pin a version-3 report while the chain on disk holds 001 and 002. Truncating to the fallback discarded the approving GO at 002, so `_approved_proposal_for_report` could not resolve it.

The landed change truncates only when `explicit_version` is not `None`. Both tests pass again, unmodified. This is recorded here rather than silently corrected because it is the sharp edge of the change: the prefix is only meaningful when the pin resolved to a real chain member.

## Executed Verification

```text
python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight_gfr_slice_a.py -q --tb=line
56 passed, 1 warning in 1.25s

python -m ruff check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py
All checks passed!

python -m ruff format --check <both declared paths>
2 files already formatted

python -m py_compile scripts/bridge_applicability_preflight.py
OK
```

51 of those 56 are the pre-existing cases, passing unmodified; 5 are new.

### Live before/after on the thread that motivated this

`bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-015.md`, unmodified throughout:

| Condition | packet_hash |
|---|---|
| pinned, chain held 15 versions (measured before v016 landed, prior to this change) | `sha256:a9e6ec0f8b181763183708cef463ae7d2f1336c3ec7ea86b39e2beaf89877d03` |
| pinned, chain held 16 versions, **before** this change | `sha256:0883c4c19d5a70437678ea619ac1a34b1cba9f92fe301181a7c266d3c608b1f0` |
| pinned, chain held 16+ versions, **after** this change | `sha256:a9e6ec0f8b181763183708cef463ae7d2f1336c3ec7ea86b39e2beaf89877d03` |

The post-change value is byte-identical to the pre-v016 measurement, which is the invariant the proposal committed to. Unpinned resolution still advances with the thread and returned `sha256:f08363df1644f5bf44374ff388d019584cf4959adfbe22e968a53a8ad9a22bfd` against operative version 016.

**Scope limit, stated plainly:** this does not demonstrate that the value now equals `sha256:72eb2a28…`, the figure the finalize check expected during the reviewer's attempt on report 015. It is not claimed to. This change removes one measured drift source — later versions on the same thread — and the tests below pin that property. If a residual drift source remains, it will present as a stale-`packet_hash` denial whose value is stable across republication, which is a different and more tractable signature than the moving target observed before.

## Specification-Derived Verification

| Requirement (proposal criterion) | Behavior verified | Evidence |
|---|---|---|
| 1 — pinned packet chain-invariant | Publishing versions 002 and 003 to a fixture thread leaves report 001's pinned packet unchanged | `test_pinned_packet_is_invariant_to_later_chain_versions` — passed |
| 2 — still content-sensitive | Editing the pinned report's own bytes changes the packet | `test_pinned_packet_still_tracks_the_pinned_report_content` — passed |
| 2 — still identity-sensitive | Two different pinned versions of one thread yield different packets | `test_pinned_packet_distinguishes_different_reports_in_one_thread` — passed |
| 3 — emitted anchors name the pinned report | `operative_version.path` is the pinned report and `content_source.mode` is `pending_content` | `test_pinned_packet_names_the_pinned_report_as_operative` — passed |
| 5 — unpinned unchanged | A verdict alone does not move the operative version; a later Prime-authored version does | `test_unpinned_packet_still_follows_the_chain_tail` — passed |
| 5 — existing behavior preserved | All 51 pre-existing cases in the two suites pass unmodified | suite run above |
| 6 — no gate changed | `.claude/hooks/bridge-compliance-gate.py` is not in `target_paths` and was not modified | diff scope below |
| 7 — quality gates | ruff check, ruff format --check, py_compile all clean | commands above |
| 8 — cohort exclusivity | Only the two declared paths changed | diff scope below |

Criterion 4 of the proposal (producer and checker agree across an intervening publication) is **partially evidenced**. The producer side is proven by criterion 1's test. A single end-to-end case driving `bridge-compliance-gate`'s rebuild against the same fixture is **not** included, because that surface is outside this thread's `target_paths` and adding a case that imports it would have widened the cohort. The live before/after above is the closest available evidence. Reviewers may reasonably treat this as a gap; if so, the remedy is a follow-on thread that declares both surfaces rather than a widening of this one.

## Files Changed

```text
scripts/bridge_applicability_preflight.py                          |  27 ++
platform_tests/scripts/test_bridge_applicability_preflight.py      | 147 ++++++
2 files changed, 174 insertions(+)
```

One hunk in the source file; no deletions anywhere.

| Target | Live SHA-256 | State |
|---|---|---|
| `scripts/bridge_applicability_preflight.py` | `EF9379455419F31F6A0DB3B0553B43F6D7D98F5AEA48A5285BCABFE6EB644FE3` | modified |
| `platform_tests/scripts/test_bridge_applicability_preflight.py` | `8FEC2EF863D5896A6E380DF14D0EB6B5853C0637AA9720C9B681C35E2DB3EE5E` | modified |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge publication authority and the finalization durability contract this defect broke.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — producer and checker must derive the same fresh value for the same report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the applicability surface changed here, and this report's own linkage obligation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — executed spec-derived evidence presented above.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the two-layer enforcement model whose layers must agree on one computed value.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — active list-free PAUTH cited in this header, operation-time gated.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH, project, work item and exact target linkage.
- `GOV-17` — automation script modification approval gate; the preflight is governance automation modified under this thread's GO.
- `GOV-10` — tests exercise the exposed `build_packet` interface, not a private re-implementation.
- `SPEC-1830` and `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — a deterministic service is now deterministic in its declared inputs.
- `GOV-WORK-TREE-HYGIENE-001` — no path outside the declared set was modified.
- `GOV-STANDING-BACKLOG-001` — WI-5867, WI-5889, WI-5948, WI-5480 and WI-5950 remain separate carriers; no duplicate carrier was created.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both targets are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable traceability and the GO to post-implementation transition.

## Prior Deliberations

- `bridge/gtkb-wi5949-applicability-packet-determinism-002.md` — the GO authorizing this implementation.
- `bridge/gtkb-wi5949-applicability-packet-determinism-001.md` — the approved design and the measured evidence it rests on.
- `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-016.md` — the third consecutive finalization failure that motivated this work.
- `bridge/gtkb-wi5941-deterministic-release-deadline-test-004.md` — the same stale-`packet_hash` denial on an unrelated thread.
- `bridge/gtkb-w0-executable-go-pre-verdict-validation-001.md` — Wave 0 work on the same livelock from the verdict-authoring side; complementary, non-overlapping cohort.
- `DELIB-202667722` — timer and throttle governance; no timer literal was introduced.

## Owner Decisions / Input

1. **AskUserQuestion, 2026-08-06, finalization.** Owner answer: **"Fix WI-5949, the packet race"** — the authority for this line of work.
2. **AskUserQuestion, 2026-08-06, priority.** Owner answer: **"File the WI-5949 proposal"** — the authority for the proposal this report implements.
3. The owner has directed that the dispatcher and TAFE remain disabled during repairs. This implementation does not activate, dispatch through, configure, or mutate either.

No new owner decision is requested by this filing.

## Requested Loyal Opposition Action

Verify against the evidence above and record **VERIFIED**, or **NO-GO** with concrete findings. Reviewers are specifically asked to check:

1. That restricting `versions` to the prefix does not weaken `_pauth_phase`, `_approved_proposal_for_report` or `_pauth_phase_cohort` for any case where the pin resolved to a real chain member.
2. That gating the truncation on `explicit_version` rather than `operative` is the correct boundary, given the out-of-`bridge/` pending-content fixtures.
3. Whether the partially-evidenced criterion 4 is acceptable as scoped, or should block VERIFIED pending a follow-on thread that declares both the producer and the compliance-gate surfaces.

Note for the verdict artifact: the canonical `bridge_kind` for a Loyal Opposition verdict is `lo_verdict` per `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`. If finalization fails, please leave the thread non-terminal rather than writing a file-only VERIFIED.

## Recommended Commit Type

Recommended commit type: `fix` — repairs a producer/checker disagreement that denied valid terminal verdicts. No capability surface is added and no gate behavior changes.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
