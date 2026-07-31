NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: de7aad12-9b24-41c8-849c-de48e349ff62
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code interactive leader session; resolved role prime-builder via ::init gtkb pb; manual-dispatcher program DELIB-202667523

bridge_kind: prime_proposal
Document: gtkb-wi5741-spec-packet-postimage-completeness
Version: 001
Date: 2026-07-29 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5741

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_spec_update.py", "groundtruth-kb/src/groundtruth_kb/cli_spec_record.py", "platform_tests/groundtruth_kb/cli/test_spec_update.py", "platform_tests/groundtruth_kb/cli/test_spec_record.py", ".groundtruth/formal-artifact-approvals/**"]

# WI-5741 — Spec Approval Packets Must Carry the Complete Postimage (Fast Lane)

Scope confirmation: this proposal performs no MemBase mutation and no
groundtruth.db write. The implementation changes only the two CLI modules and
two test files listed in target_paths; tests run against fixture databases
and temporary packet paths. The `.groundtruth/formal-artifact-approvals/**`
envelope appears in target_paths declaratively because this proposal's
subject is approval-packet generation; the implementation itself creates or
edits no live packet under that envelope, and reviewers should treat the
entry as scope declaration, not authorization exercised.
References to DCL versions below are evidence citations, not mutations
performed by this work.

## Problem

`gt spec update` and `gt spec record` generate formal-artifact approval
packets whose `full_content` is exactly the `--content-file` text (the
description). Structured mutation fields supplied on the same invocation —
`--assertions-json`, `--constraints-json`, `--tags-json`,
`--affected-by-json`, `--source-paths-json` — mutate the MemBase row but
never enter the approval evidence. Defect site: `_build_packet`,
`groundtruth-kb/src/groundtruth_kb/cli_spec_update.py:133-154` (packet built
from `full_content` param) versus `_merged_fields` `:157-174` (row built from
the same text PLUS the structured fields). `cli_spec_record.py` shares the
pattern via the same `construct_approval_packet` call shape.

Live consequence, independently found by two Loyal Opposition verdicts: the
`DCL-SESSION-ROLE-RESOLUTION-001` v7 packet
(`.groundtruth/formal-artifact-approvals/2026-07-29-DCL-SESSION-ROLE-RESOLUTION-001-v7.json`)
carries only the 10,409-char description while the approved-in-the-same-write
`assertions` field is 7,061 chars — so the packet cannot prove owner approval
of the complete postimage required by `GOV-ARTIFACT-APPROVAL-001`
(`bridge/gtkb-wi5679-session-role-keying-continuity-016.md` F1;
`bridge/gtkb-wi5718-retired-session-role-authority-purge-012.md` F2).
Reproduced 2026-07-29 on the owner-directed v8 re-derivation dry-run: the
proposed v8 packet `full_content` is 11,161 chars (new description alone)
despite `--assertions-json` carrying the ten-assertion inventory. The
re-derivation is therefore BLOCKED on this fix: running it now would
recommit the exact defect the re-derivation exists to repair.

## Proposed Change

1. Add a deterministic postimage serializer in `cli_spec_update.py`:
   `_postimage_full_content(description, *, assertions=None, constraints=None,
   tags=None, affected_by=None, source_paths=None) -> str`.
   - Returns `description` byte-unchanged when no structured field is
     supplied (backward compatibility: description-only packets, which are
     the overwhelming majority, keep identical hashes).
   - For each supplied field, appends a canonical block:
     `\n\n---\n\n## Approved Postimage: <field>\n\n```json\n` +
     `json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)` +
     `\n```\n`, LF-normalized, fields in a fixed order (assertions,
     constraints, tags, affected_by, source_paths).
2. `_build_packet` (update path) consumes the serializer output so packet
   `full_content` and `full_content_sha256` cover the complete postimage.
3. `cli_spec_record.py` imports and applies the same serializer for creates
   that supply structured fields.
4. The MemBase row shape is UNCHANGED: `description` remains the
   content-file text; structured fields remain structured. Only the approval
   EVIDENCE gains the serialized blocks.

## Spec-Derived Test Plan

In `platform_tests/groundtruth_kb/cli/test_spec_update.py`:
1. `test_update_packet_carries_assertions_postimage` — update with
   `--assertions-json`; assert packet `full_content` contains the canonical
   JSON block with the supplied assertion ids, `full_content_sha256` matches
   the serialized content, and the row's `assertions` equals the supplied
   JSON (no dual-drift). Derives from GOV-ARTIFACT-APPROVAL-001
   (complete-postimage approval evidence).
2. `test_update_packet_description_only_unchanged` — update without
   structured fields; assert packet `full_content` is byte-identical to the
   content-file text (backward compatibility; hash stability). Derives from
   GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (evidence must reflect exactly what
   changed).
3. `test_update_packet_validates_against_live_gate` — generated packet
   passes `scripts/validate_formal_artifact_packet.py` (the live gate
   schema authority). Derives from DCL-ARTIFACT-APPROVAL-HOOK-001.

In `platform_tests/groundtruth_kb/cli/test_spec_record.py`:
4. `test_record_packet_carries_structured_postimage` — same assertion for
   the create path.

## Specification Links

- GOV-ARTIFACT-APPROVAL-001 — the formal artifact approval gate this defect undermines; packets must preserve the full postimage.
- GOV-RELIABILITY-FAST-LANE-001 — governing fast-lane spec: small, scoped defect fix with regression tests.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 — approval evidence must derive from the actual complete change, not a partial projection.
- SPEC-1662 (GOV-18) — meaningful assertions over coverage; the new tests assert semantic packet content, not shape only.
- GOV-10 — tests exercise the exposed production interface (`gt spec update` / `gt spec record`).
- GOV-12 — work item creation triggers test creation (four new regression tests).
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge audit-trail discipline governing this thread.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — all four target paths are in-root platform surfaces under groundtruth-kb/** and platform_tests/**; no application-subtree output.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this section satisfies the concrete-links clause.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the test plan maps every linked requirement to executed tests.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) — approval evidence is a durable artifact; this fix restores its integrity.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) — append-only versioning discipline preserved; no packet rewrites.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) — reviewer findings triggered this governed defect artifact.

## Prior Deliberations

- DELIB-202667528 — owner routing/authority context for the blocked DCL v8 re-derivation.
- DELIB-202667526 — live concurrency/evidence record including the session-triple enforcement this packet evidence feeds.
- DELIB-202667220 — the retired-authority purge order whose completion the blocked v8 also serves.
- bridge/gtkb-wi5679-session-role-keying-continuity-016.md (F1) and bridge/gtkb-wi5718-retired-session-role-authority-purge-012.md (F2) — the independent reviewer findings this fix answers at the tooling root.
- DELIB-202667523 — program mandate under which the leader files this fast-lane proposal.

## Owner Decisions / Input

- AUQ-20260729-DCL-V8-REDERIVATION: owner directed the leader to re-derive
  DCL v8 with a complete-postimage packet. Dry-run inspection proved the CLI
  cannot currently produce one; this fix is the instrumental prerequisite of
  that owner-directed repair. No new owner preference is introduced.
- PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING — standing authorization
  covering WI-5741 by active membership in PROJECT-GTKB-RELIABILITY-FIXES
  (source + test_addition classes). Full bridge protocol retained: this NEW
  awaits independent LO GO; implementation requires the exact-session claim
  and implementation-start packet; report and independent VERIFIED follow.

## Requirement Sufficiency

Existing requirements sufficient. GOV-ARTIFACT-APPROVAL-001 already mandates
complete-postimage approval evidence; this change makes the CLI comply. No
new or revised requirement is needed.

## Risk and Rollback

Risk: LOW. Serializer is additive and deterministic; description-only packets
are byte-unchanged (test 2 guards this); row schema untouched. Rollback:
revert one commit; packets return to description-only (current defective
behavior, visibly tracked by WI-5741). Downstream consumers of packets read
`full_content` as opaque approved text plus hash; appended blocks cannot
break hash-verification consumers because hash and content change together.

Recommended commit type: fix

## Verification Plan

1. `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/cli/test_spec_update.py platform_tests/groundtruth_kb/cli/test_spec_record.py -v` — all existing plus four new tests pass.
2. `ruff check` and `ruff format --check` on the four target files — clean.
3. Live acceptance: `gt spec update --dry-run` for the DCL v8 re-derivation shows packet `full_content` containing both the corrected description and the ten-assertion inventory with matching sha256.
