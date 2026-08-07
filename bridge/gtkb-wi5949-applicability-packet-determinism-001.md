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

# WI-5949 Implementation Proposal — Make the applicability packet a pure function of the report it pins

bridge_kind: prime_proposal
Document: gtkb-wi5949-applicability-packet-determinism
Version: 001
Date: 2026-08-06 UTC

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

The applicability packet that a Loyal Opposition verdict embeds is not a pure function of the report it claims to describe. `build_packet` scans the whole numbered thread before it looks at the pinned report, so the packet for a **fixed report with fixed content** changes whenever any new version lands on that thread — including the verdict being written.

The finalize freshness check rebuilds the packet at commit time, correctly pinned to the `Responds to:` report, and compares. Any publication between verdict authoring and commit therefore invalidates the verdict. On a busy thread that is not a race the reviewer can win; it is the expected outcome.

This proposal makes the pinned path deterministic with respect to the report. It changes no gate, relaxes no check, and adds no configuration.

## Problem Evidence (measured 2026-08-06)

### Same report, same bytes, three different packet hashes

Thread `gtkb-wi5825-publication-capability-recovery-receipt-backfill`, report version 015, unmodified throughout:

| packet_hash | Condition |
|---|---|
| `sha256:72eb2a28…` | expected by the finalize freshness check for report 015 during the reviewer's attempt (chain held 15 versions) |
| `sha256:a9e6ec0f8b181763183708cef463ae7d2f1336c3ec7ea86b39e2beaf89877d03` | `--bridge-id` only, immediately after report 015 published |
| `sha256:0883c4c19d5a70437678ea619ac1a34b1cba9f92fe301181a7c266d3c608b1f0` | `--content-file bridge/…-015.md`, after version 016 landed (chain held 16 versions) |

The value is **deterministic for fixed inputs**: two consecutive pinned runs both returned `0883c4c1…`. So this is not nondeterminism. It is an input that moves.

### The moving input

`scripts/bridge_applicability_preflight.py` lines 1035-1036, inside `build_packet`, execute unconditionally before `content_file` is considered:

```text
versions = parse_index_for_document(bridge_dir, bridge_id)
scanned_operative = choose_operative_version(versions)
```

`content_file` is only consulted afterwards, at line 1043. The thread's version list and the scanned chain-tail therefore participate in packet construction even when the caller has explicitly pinned the report. Publishing version N+1 changes `versions`, which changes the packet for report N.

### The check is not at fault

`.claude/hooks/bridge-compliance-gate.py` rebuilds the expected packet with `content_file=responds_path`, pinned to the exact `Responds to:` artifact, and rejects a mismatch with "Verdict applicability freshness check rejected a stale packet_hash". That behavior is correct and this proposal does not change it. The producer and the checker simply do not compute the same function for the same report.

### Observed cost

Three consecutive finalization attempts on `gtkb-wi5825-publication-capability-recovery-receipt-backfill` failed with substance green each time, per versions 010, 012 and 016 ("298 passed; v012 newest capability consumed; hashes match"). `gtkb-wi5941-deterministic-release-deadline-test-004` failed with the identical stale-`packet_hash` denial. Each failure additionally strands a file-only terminal `VERIFIED` candidate that a reviewer must delete under bridge-repair authority, and leaves a `recovery_required` capability row behind when rollback cannot restore the aggregate preimage.

## Proposed Design

One slice, two files, no new configuration and no threshold.

### Change 1 — pinned mode is a pure function of the pinned report

When `content_file` is supplied, `build_packet` must construct the packet from the pinned content, the applicability configuration, and the database only. Chain-derived state must not enter the packet.

Concretely:

- Defer the `parse_index_for_document` / `choose_operative_version` scan so it does not run on the pinned path, or run it strictly for diagnostics whose values are excluded from the hashed payload.
- Keep the pinned report's own identity (document name and version) as packet inputs, since those are properties of the report itself, derived from its filename and header rather than from its siblings.
- Preserve the existing unpinned behavior exactly. A caller supplying only `--bridge-id` still resolves the operative version by scanning, because with no pinned report the chain tail *is* the subject.

The invariant this establishes: for a fixed report file, fixed `spec-applicability.toml` and fixed database, `build_packet(content_file=<report>)` returns the same `packet_hash` regardless of how many other versions exist in the thread.

### Change 2 — the emitted section must not reintroduce chain state

`operative_file` and `content_file` are both emitted into the `Applicability Preflight` section that verdicts copy. On the pinned path both must name the pinned report, so a verdict's section cannot disagree with the value the checker will rebuild. The checker already requires `content_file`/`operative_file` to equal the `Responds to:` artifact; this makes the producer satisfy that requirement by construction rather than by the caller remembering to pass the right flag.

### Explicitly out of scope

- **No change to `.claude/hooks/bridge-compliance-gate.py`** or to any gate, threshold, or fail-closed behavior. The freshness check stays exactly as it is.
- **No change to the unpinned diagnostic path** beyond what Change 1 requires to keep it working.
- **No new configuration key and no timer literal.**
- No repair of the stranded `recovery_required` rows or the compensation path; those are WI-5825 Change A and remain deferred.
- No dispatcher or TAFE activation, configuration, or mutation.
- No overlap with the Wave 0 cohort: `gtkb-w0-executable-go-pre-verdict-validation` (WI-5889), `gtkb-w0-gate-false-positive-repair` (WI-5480), `gtkb-w0-skill-rename-path-repair` (WI-5640) and `gtkb-w0-worker-enablement-plumbing` were each checked at filing time and **none declares `scripts/bridge_applicability_preflight.py`** in its `target_paths`. WI-5889 references `packet_hash` in prose but does not target this module.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge publication authority and the commit-finalization durability contract this defect breaks.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the freshness principle the check enforces; this proposal makes the producer compute the same fresh value the checker does.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the applicability surface whose packet is at issue, and this proposal's own linkage obligation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — executed spec-derived evidence required before VERIFIED; mapping below.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the two-layer enforcement model whose write-time and review-time layers must agree on one computed value.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — the active list-free PAUTH cited in this header, operation-time gated.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH, project, work item and exact target linkage.
- `GOV-17` — automation script modification approval gate; the preflight is governance automation modified under this thread's future GO.
- `GOV-10` — tests exercise the exposed `build_packet` interface rather than a private re-implementation.
- `SPEC-1830` and `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — a deterministic service must be deterministic in its declared inputs.
- `GOV-STANDING-BACKLOG-001` — WI-5867, WI-5889, WI-5948 and WI-5480 remain separate carriers; no duplicate carrier is created here.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both targets are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable traceability of the defect capture and its remedy.

## Prior Deliberations

- `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-016.md` — the third consecutive finalization failure, quoting the stale-`packet_hash` denial and the compensation failure that followed.
- `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-012.md` — the repaired non-terminal verdict enumerating packet, GO-linkage and manifest blockers.
- `bridge/gtkb-wi5941-deterministic-release-deadline-test-004.md` — the same stale-`packet_hash` denial on an unrelated thread, establishing this is not thread-specific.
- `bridge/gtkb-w0-executable-go-pre-verdict-validation-001.md` — the Wave 0 pre-verdict executability work, which addresses the same livelock from the verdict-authoring side and is complementary rather than overlapping.
- `bridge/gtkb-wi5867-protected-commit-gate-contention-attribution-001.md` — GO'd proposal to attribute finalization failure causes; this defect is one of the causes it would have named.
- `DELIB-202667722` — timer and throttle governance; no timer literal is introduced here.

## Owner Decisions / Input

1. **AskUserQuestion, 2026-08-06, finalization.** Owner answer: **"Fix WI-5949, the packet race"** — stop filing revisions against the symptom and fix the cause. This is the authority for filing this proposal.
2. **AskUserQuestion, 2026-08-06, priority.** Owner answer: **"File the WI-5949 proposal"** — file the bounded proposal rather than starting a large Wave 0 implementation in the remaining session budget.
3. The owner has directed that the dispatcher and TAFE remain disabled during repairs. This proposal does not activate, dispatch through, configure, or mutate either.

No new owner decision is requested by this filing.

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`, `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`, the existing freshness check contract, and the measured evidence above fully determine this change. No new or revised specification is required before implementation.

## Specification-Derived Verification Plan

| Requirement | Behavior under test | Planned coverage |
|---|---|---|
| Pinned packet is chain-invariant | Build a fixture thread, compute the pinned packet for report N, publish version N+1, recompute for report N unchanged — hashes must be equal | new case in `test_bridge_applicability_preflight.py` |
| Pinned packet is content-sensitive | Modifying the pinned report's bytes changes the packet | new case |
| Pinned identity preserved | The packet still binds the pinned report's document name and version; a different report yields a different packet | new case |
| Producer and checker agree | The packet emitted for report N equals the value `bridge-compliance-gate` rebuilds with `content_file=<report N>`, after an intervening publication | new case exercising both surfaces |
| Emitted section names the pinned report | On the pinned path, `content_file` and `operative_file` both name the pinned report | new case |
| Unpinned behavior unchanged | With `--bridge-id` only, the operative version is still the scanned chain tail | existing cases must stay green unmodified |
| No new configuration or timer literal | Diff introduces no config key, timeout, TTL, interval, retry or throttle literal | diff inspection |

Planned commands after implementation:

```text
python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight_gfr_slice_a.py -q --tb=short
python -m ruff check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py
python -m ruff format --check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py
python -m py_compile scripts/bridge_applicability_preflight.py
git diff --check -- scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py
```

## Acceptance Criteria

1. For a fixed report file, fixed applicability configuration and fixed database, `build_packet(content_file=<report>)` returns an identical `packet_hash` before and after unrelated versions are published to the same thread.
2. The packet remains sensitive to the pinned report's own content and identity; different content or a different report yields a different packet.
3. On the pinned path, the emitted `content_file` and `operative_file` both name the pinned report.
4. The value the producer emits for report N equals the value the compliance gate rebuilds for report N, verified across an intervening publication.
5. Unpinned `--bridge-id` behavior is unchanged and its existing tests pass unmodified.
6. No gate, threshold, fail-closed behavior, or configuration key is changed; `.claude/hooks/bridge-compliance-gate.py` is not modified.
7. `ruff check`, `ruff format --check`, `py_compile` and `git diff --check` pass on both declared paths.
8. Only the two declared paths change; at implementation-start, fresh readback confirms both clean with matching hashes and no live GO from another thread overlapping them, including the Wave 0 cohort.

## Risks And Rollback

- **Risk: the chain scan is load-bearing for something unnoticed.** Mitigated: the unpinned path retains it unchanged, and criterion 5 requires the existing suite to pass unmodified. If a pinned-path consumer genuinely needs chain context, it can be emitted as an unhashed diagnostic field rather than a packet input.
- **Risk: changing the packet invalidates verdicts already in flight.** Mitigated and disclosed: packet values will change once for pinned callers. Any verdict computed before this lands and finalized after it will need its packet regenerated, which is the same regeneration those verdicts already require today for a different reason. No committed evidence is invalidated, because a consumed capability records its own digest rather than the packet.
- **Risk: overlap with the Wave 0 cohort.** Mitigated: none of the four W0 threads declares this module; criterion 8 re-checks at implementation-start.
- **Rollback:** revert the two file diffs. The change is confined to which values participate in packet construction on one code path; the pre-change behavior re-emerges on revert.

## Recommended Commit Type

Recommended later implementation type: `fix` — repairs a producer/checker disagreement that denies valid terminal verdicts. No capability surface is added.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
