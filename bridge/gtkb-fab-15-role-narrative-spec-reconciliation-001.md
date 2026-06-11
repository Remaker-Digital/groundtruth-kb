NEW

bridge_kind: prime_proposal
Document: gtkb-fab-15-role-narrative-spec-reconciliation
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4427
Project Authorization: PAUTH-FAB15-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: d2f32e6b-5441-45b3-b355-097a2507f5f7
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth.db", "harness-state/harness-registry.json", ".codex/config.toml", "scripts/sync_canonical_terms.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "config/governance/canonical-terms-sync.toml", "platform_tests/scripts/**"]

KB mutation: YES. Three MemBase writes: (1) the registry role-topology restore via the gt mode set-role transaction component (MemBase harnesses table, audit-trailed); (2) the canonical_terms regeneration via the deterministic sync (formal-artifact-class writes); (3) the GOV-SOURCE-OF-TRUTH-FRESHNESS-001 amendment (spec version, formal-artifact packet). `groundtruth.db` is therefore in `target_paths`. No canonical specification rows are hard-deleted.

---

# FAB-15 — Role-Narrative + Spec Reconciliation

WI-4427 (FAB-15) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-036 (registry topology inversion),
HYG-032 (.codex/config.toml posture), HYG-033 (canonical_terms table freeze), HYG-064 (startup-relay-vs-
freshness spec contradiction). Source advisory: `bridge/gtkb-fable-investigation-advisory-001.md`.

Common theme: the durable governance records (the role registry, the Codex config, the canonical_terms
table, and two startup specs) have drifted away from the auto-loaded narrative, the recorded owner
decisions, and each other — so role resolution, approval posture, glossary vocabulary, and the SessionStart
relay each rest on a contradicted source.

## Summary

- **HYG-036 (registry):** the durable harness-registry (canonical role authority per CLAUDE.md Role
  precedence) records antigravity(C)=prime-builder/ACTIVE as sole active Prime, with codex(A) and claude(B)
  both prime-builder/SUSPENDED — inverting the Codex=Loyal-Opposition / Claude=Prime-Builder binding in
  every auto-loaded rule surface, and the active partition is the launch-dead set (HYG-001).
- **HYG-032 (Codex posture):** .codex/config.toml sets approval_policy='never' + sandbox network_access=true
  (most permissive), added by a 2026-05-31 settle-commit whose message admits the authoring threads are
  unrecoverable, contradicting the only AUQ-recorded posture decision (2026-05-16: on-request + network off).
- **HYG-033 (glossary SoT):** the canonical_terms MemBase table is a frozen 2026-05-08 one-shot seed (27
  rows) while the live markdown glossary has ~60+ entries; the doctor's 7 parity WARNs are symptoms; the
  markdown is the de facto SoT, inverting GOV-08.
- **HYG-064 (startup specs):** GOV-SOURCE-OF-TRUTH-FRESHNESS-001 v2 names .claude/hooks/last-user-visible-
  startup-*.md a forbidden read pattern while DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 mandates
  rendering that exact cached file at SessionStart, without invoking the GOV's declared-TTL exception.

## Specification Links

- `GOV-HARNESS-ROLE-PORTABILITY-001` — the role-topology authority restored by the registry transaction
  (HYG-036).
- `GOV-SESSION-ROLE-AUTHORITY-001` — durable-vs-session role resolution; the registry restore re-aligns the
  durable authority with the operating reality (HYG-036).
- `GOV-08` (Knowledge Database is the single source of truth) — the canonical_terms table must mirror, not
  contradict, the glossary SoT (HYG-033).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the spec amended to carve the relay cache under its declared-TTL
  exception (HYG-064); also governs the canonical_terms freshness (HYG-033).
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` — the spec mandating the relay read (HYG-064).
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — the glossary-as-read-surface architecture the canonical_terms sync
  supports (HYG-033).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-15 changes are in-root; see Isolation Placement
  Compliance below.
- `GOV-STANDING-BACKLOG-001` — WI-4427 is the governed backlog authority; absorbs the overlapping items.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the registry/spec/table writes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `NEW` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-032/033/036/064).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB15-REMEDIATION-20260610` — this cluster's four owner dispositions (below).
- _The 2026-05-16 AUQ recorded the on-request + network-off Codex posture this cluster realigns toward._
- _The vendor-de-binding narrative sweep (12 codex-* files, glossary 'embodied by' pointers) is a deferred
  follow-on, NOT in FAB-15 scope._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB15-REMEDIATION-20260610`:

1. **HYG-036 = Registry is residue; restore + audit.** Restore the Claude=Prime-Builder / Codex=Loyal-
   Opposition topology via the gt mode set-role transaction component (audit-trailed) and audit how it
   drifted. The vendor-de-binding narrative sweep is a separately-scoped follow-on, NOT in FAB-15 scope.
2. **HYG-032 = Split posture.** approval_policy='on-request' interactive, 'never' for headless dispatched
   workers (which cannot answer approvals), network_access=false; record a DELIB + a config citation comment.
3. **HYG-033 = Glossary markdown SoT + deterministic sync.** A parser keyed on the stable '### term' + field
   convention regenerates canonical_terms rows at wrap; the doctor parity check verifies generator freshness.
4. **HYG-064 = Carve the relay file under the declared-TTL exception.** Amend GOV-SOURCE-OF-TRUTH-FRESHNESS-001
   to place the SessionStart relay cache under its existing declared-TTL exception (formal-artifact packet).

## Requirement Sufficiency

**Existing requirements sufficient.** The dispositions are fixed by `DELIB-FAB15-REMEDIATION-20260610`; the
governing specifications (`GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, `GOV-08`,
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`,
`GOV-GLOSSARY-AS-DA-READ-SURFACE-001`) already constrain the role-authority, source-of-truth, and
glossary-read-surface surfaces. No new requirement is needed. The GOV-SOURCE-OF-TRUTH-FRESHNESS-001
amendment is a clarifying exception recorded via the formal-artifact-approval packet at implementation time.

## Scope and Boundaries

In scope: the four reconciliations. Out of scope and explicitly excluded: the vendor-de-binding narrative
sweep (the 12 codex-* rule files, the glossary 'embodied by Codex/Claude CLI' pointers, the LO-definition
consolidation across 8 surfaces) — a separately-scoped follow-on; any topology change beyond restoring the
recorded Claude=PB/Codex=LO intent; deploy/push. This proposal absorbs the advisory's overlap for FAB-15
(the role-assignment glossary update item 4338, the durable-vs-session role split item 3479, the role-term
item 4362) by describing them here; backlog-state reconciliation is a post-VERIFIED operational step.

## Proposed Implementation

**Area 1 — HYG-036 registry restore.** Use `gt mode set-role` transactions to set the active topology to
Claude(B)=prime-builder and Codex(A)=loyal-opposition (and reconcile the suspended/active status per the
intended operating partition), via the audit-trailed mode-switch transaction component. Capture an audit
note of the drift origin (the 2026-06-09 regen). No narrative-file edits — the narrative already describes
this topology correctly.

**Area 2 — HYG-032 Codex posture.** Edit `.codex/config.toml`: approval_policy='on-request' for interactive
sessions; document the headless-dispatch 'never' carve-out; network_access=false. Add a one-line citation
comment pointing at `DELIB-FAB15-REMEDIATION-20260610` so a future settle-commit cannot silently flip it.

**Area 3 — HYG-033 canonical_terms sync.** Add `scripts/sync_canonical_terms.py` (a deterministic parser
keyed on the glossary's '### term' + field convention) that regenerates canonical_terms rows from the
markdown glossary; wire it into session wrap; update the doctor parity check
(`doctor.py`) to verify generator freshness rather than hand parity. Regenerate the table once to clear the
7 WARNs. Table writes are formal-artifact-class (approval evidence at implementation).

**Area 4 — HYG-064 spec carve-out.** Amend GOV-SOURCE-OF-TRUTH-FRESHNESS-001 to add the SessionStart relay
cache (.claude/hooks/last-user-visible-startup-*.md) to its declared-TTL exception, so the
DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 mandated read is consistent. Formal-artifact-approval packet.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all FAB-15 changes are in-root under `E:\GT-KB\`. The new sync
service is at `scripts/sync_canonical_terms.py`, its config under `config/governance/`, tests under
`platform_tests/`, the doctor update in the in-root `groundtruth-kb/src/groundtruth_kb/` tree, the registry
under `harness-state/`, the Codex config at `.codex/config.toml`, and this bridge file under
`E:\GT-KB\bridge\`. The cluster relocates no file, touches no `applications/` subtree, and writes no
out-of-root artifact.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-HARNESS-ROLE-PORTABILITY-001` + `GOV-SESSION-ROLE-AUTHORITY-001` (HYG-036) | test: after the transaction, the active partition resolves Claude=prime-builder + Codex=loyal-opposition; the change is audit-trailed by the mode-switch component; doctor role-set topology check passes |
| recorded owner posture (HYG-032) | test: .codex/config.toml interactive approval_policy='on-request', network_access=false; a citation comment references the DELIB; a headless-dispatch 'never' path is documented |
| `GOV-08` + `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` (HYG-033) | test: the sync regenerates canonical_terms from the glossary deterministically (idempotent); the 7 parity WARNs clear; the doctor check verifies generator freshness |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` (HYG-064) | test: the amended GOV lists the relay cache under the declared-TTL exception; the mandated relay read is no longer a forbidden-substitute violation (the two specs agree) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` + `ruff check` AND `ruff format --check` on changed Python |

## Acceptance Criteria

1. **Area 1:** the active role partition is Claude=PB / Codex=LO via an audit-trailed transaction; drift
   origin noted; doctor role-set topology check passes.
2. **Area 2:** .codex/config.toml posture is on-request interactive + network off, with the headless carve-out
   documented and a DELIB citation comment.
3. **Area 3:** the deterministic sync regenerates canonical_terms; the 7 parity WARNs clear; the doctor check
   verifies generator freshness.
4. **Area 4:** GOV-SOURCE-OF-TRUTH-FRESHNESS-001 is amended (with packet) so the relay read is consistent.
5. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-15-role-narrative-spec-reconciliation-001.md` with a matching `NEW` entry at the
top of `bridge/INDEX.md`; append-only. The registry restore uses the governed mode-switch transaction
component (not an ad-hoc edit), preserving the audit trail. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored;
nothing implements until Loyal Opposition records `GO`.

## Risk and Rollback

- **Risk — restoring the registry mis-sets a role / breaks active dispatch:** the gt mode set-role
  transaction validates the active dispatcher partition (≥1 active PB + ≥1 active LO) and fails closed; the
  change is audit-trailed and reversible via another transaction. **Rollback:** re-run set-role to the prior
  topology.
- **Risk — Codex posture change blocks headless dispatch:** the split posture preserves 'never' for headless
  workers precisely to avoid stalling dispatch. **Rollback:** revert the config (2-line change).
- **Risk — canonical_terms sync mis-parses the glossary:** the parser is keyed on the documented '### term'
  + field convention with an idempotency test; table writes are formal-artifact-gated. **Rollback:**
  append-only re-version; the glossary remains the SoT.
- **Risk — amending GOV-SOURCE-OF-TRUTH-FRESHNESS-001 weakens the read discipline:** the amendment only
  carves the declared-TTL relay cache (already a known-TTL generated file), not the broader forbidden set.
  **Rollback:** re-version the GOV.

## Recommended Implementation Routing

**Opus/Codex-supervised** — role-resolution, approval posture, and source-of-truth specs are the highest-
authority surfaces in the platform; a wrong registry write or a too-broad GOV carve-out re-opens a
governance hole. Not cheap-model candidates. Area 3 (the sync parser) is the most script-mechanical once GO'd.

## Recommended Commit Type

`fix:` — reconciles four drifted governance records (registry topology, Codex posture, canonical_terms
table, startup specs) with the recorded owner decisions and each other, with a `feat:`-class addition (the
deterministic canonical_terms sync service).
