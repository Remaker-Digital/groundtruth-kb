# Harness Equivalence Phase 3 Evidence Freshness Boundaries

Status: IMPLEMENTED
Generated: 2026-07-06T02:45:00Z
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4971
Bridge: bridge/gtkb-wi4971-evidence-freshness-boundaries-004.md
Implementation authorization packet: sha256:fe1633198a54cbd13dd92a7283555dace7c987bb6183486f34e2dcde7cf4cc77

## Claim

WI-4971 is satisfied by a config-backed classifier that separates current-state evidence, stale evidence, archival citation-only references, justified full archival reads, and missing evidence without loading full historical state by default.

## Relationship To SoT Freshness And Read Discipline

- Relationship mode: `complements_not_supersedes`.
- SoT registry path: `config/registry/sot-artifacts.toml`.
- Duplicate SoT inventory: `false`.
- Current-state authority: `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`.
- Read-hook authority: `DCL-SOT-READ-HOOK-CONTRACT-001`.
- Forbidden substitutes policy: `deny_for_current_state_claims`.

Current-state claims require fresh canonical-reader evidence. Compact output is acceptable only when it is produced by the canonical reader for the state being claimed, or when a declared-TTL exception includes inline TTL metadata and canonical fallback. Archival/audit-trail references may be cited by stable path or ID without loading the full archived payload unless the session must verify, dispute, reproduce, or repair the archived claim.

## Evidence Classes

| Class | Routine read mode | Sufficient for current state | Rule |
| --- | --- | --- | --- |
| `current` | `compact` | true | Fresh current-state evidence from a canonical reader, including compact output when the compact output is itself produced by the canonical reader. |
| `stale` | `canonical_refresh_required` | false | Evidence that is too old, lacks freshness metadata, relies on a summary/paraphrase for a state claim, or attempts to substitute a forbidden path. |
| `archival-citation-only` | `citation_only` | false | Stable historical/audit-trail citation that can be cited as history without loading the full archived payload during routine sessions. |
| `full-read-justified` | `full` | false | A full archival read is justified by a stated verification, dispute, reproduction, or repair reason and a stable citation. |
| `missing` | `none` | false | The cited evidence cannot be resolved or the provider lane has a typed missing-evidence disposition. |

## B1-B7 Boundary Mapping

| ID | Blocker | Evidence class | Boundary rule | Evidence path |
| --- | --- | --- | --- | --- |
| `B1` | Bridge scan raw JSON included terminal VERIFIED and archived/nonterminal payloads during routine checks. | `current` | Use compact current bridge queue reads for routine state; treat terminal/archive payloads as citation-only unless a full-read justification is stated. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/session-activity-envelope-sharding-blockers-2026-07-01.md` |
| `B2` | Implementation authorization list output dumped hundreds of expired named packets. | `current` | Use compact current packet summaries for routine state; expired packet bodies are archival citation-only unless disputed or repaired. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/session-activity-envelope-sharding-blockers-2026-07-01.md` |
| `B3` | Implementation-report planning output included broad dirty-worktree and version-chain payloads when only current GO/report metadata was needed. | `current` | Use compact plan metadata for current implementation planning; load full version chains only when filing or verifying the bridge artifact. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/session-activity-envelope-sharding-blockers-2026-07-01.md` |
| `B4` | Handoff/session marker drift and archived-envelope mis-resolution could cause agents to use the wrong archived session state. | `full-read-justified` | Explicit session IDs and stable citations justify archive selection; ambiguous archived state fails closed. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/session-activity-envelope-sharding-blockers-2026-07-01.md` |
| `B5` | Broad generated/cache searches can hit runtime artifacts, wasting tokens and producing access-denied noise. | `stale` | Generated/cache surfaces are not current-state authority; use deterministic inventory/hygiene readers instead of unbounded full-tree searches. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/session-activity-envelope-sharding-blockers-2026-07-01.md` |
| `B6` | Startup glossary/terminology loading risked loading the full glossary into the base session envelope. | `current` | Base sessions use compact core terminology; activity-specific terms are loaded on demand by the relevant activity envelope. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/session-activity-envelope-sharding-blockers-2026-07-01.md` |
| `B7` | Provider harnesses lack full transcript/session archives, creating temptation to rely on synthetic state. | `missing` | Provider lanes use compact-provider projections and typed waivers; missing full transcripts are not replaced by synthetic current-state claims. | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/session-activity-envelope-sharding-blockers-2026-07-01.md` |

## Verification Notes

- The policy stores evidence-classification rules under `config/governance/`; it does not add `[[artifacts]]` rows or duplicate the SoT registry.
- The helper checks `forbidden_substitutes` from `config/registry/sot-artifacts.toml` before accepting current-state evidence.
- Full archive reads are opt-in and require a reason plus a stable citation; routine reports can cite append-only history without loading full archived payloads.
