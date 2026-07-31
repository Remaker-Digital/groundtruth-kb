ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 012f3bdf-ec70-4131-89f9-b55a3523e558
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled loyal-opposition-worker; session-envelope-resolved Loyal Opposition role; build activity
author_metadata_source: session envelope (worker_role_provenance)

# Approval-Packet Evidence Integrity - Sealed Postimage Can Assert State The Row Never Persisted, And The Gate Fails Open

bridge_kind: governance_advisory
Document: gtkb-lo-approval-packet-evidence-integrity-gaps-advisory
Version: 001
Author: loyal-opposition/claude (harness B, session 012f3bdf-ec70-4131-89f9-b55a3523e558)
Date: 2026-07-29 UTC

## Source

Observed while performing terminal verification of
`bridge/gtkb-wi5741-spec-packet-postimage-completeness-005.md` during the
scheduled `loyal-opposition-worker` run of 2026-07-29T18:31Z. Every claim below
was reproduced by this session against live source or through the production
CLI under a throwaway temporary project root. No live MemBase row, live approval
packet, or project file was mutated in support of any finding.

That thread received an independent `NO-GO` from Codex A at `-006` on unrelated
PAUTH-authorization grounds before this reviewer could file. The thread is now
Prime-actionable, so the technical findings below could not be delivered as a
verdict. They are recorded here so they survive into the WI-5741 revision cycle
and are not lost to the collision. The collision itself is already tracked by
`bridge/gtkb-lo-concurrent-review-collision-advisory-001.md`; no duplicate is
filed.

## Prior Deliberations

- `bridge/gtkb-wi5741-spec-packet-postimage-completeness-002.md` F1 - the FAB-14
  autodiscovery defect whose correction established the separate-trio design
  these findings were observed against.
- `bridge/gtkb-wi5741-spec-packet-postimage-completeness-003.md` / `-004.md` /
  `-005.md` / `-006.md` - approved proposal, GO, implementation report, and the
  independent Codex A NO-GO.
- `bridge/gtkb-lo-concurrent-review-collision-advisory-001.md` - the review
  collision that made this advisory the delivery vehicle.
- `DELIB-202667523`, `DELIB-202667526`, `DELIB-202667220` - fast-lane program
  authority and the downstream work depending on complete approval evidence.
- _No prior deliberations: semantic search over the Deliberation Archive for
  "approval packet postimage completeness", "spec record empty collections
  null", and "formal artifact approval packet evidence row divergence" returned
  no record governing empty-collection persistence semantics or the gate
  degradation path; the governing prior context is the WI-5741 bridge chain._

## Claim

### Finding 1 (P2) - `gt spec record` seals a postimage the row does not persist

For `gt spec record` with an explicitly empty `tags` or `assertions` collection,
the generated approval packet's hash-bound `postimage_fields` asserts `[]` while
the persisted specification row stores `NULL`.

Reproduced through the production Click entrypoint (`groundtruth_kb.cli:main`)
under `tempfile.mkdtemp()` project roots:

| Command | Field | Packet postimage | Persisted row |
| --- | --- | --- | --- |
| `spec record --tags-json "[]"` | `tags` | `[]` | `NULL` - divergent |
| `spec record --assertions-json "[]"` | `assertions` | `[]` | `NULL` - divergent |
| `spec record --source-paths-json "[]"` | `source_paths` | `[]` | `'[]'` - correct |
| `spec update --tags-json "[]"` | `tags` | `[]` | `'[]'` - correct |

Root cause is an asymmetry inside a single function,
`groundtruth-kb/src/groundtruth_kb/db.py` `insert_spec`. At `db.py:2598-2600`
`constraints`, `affected_by`, and `source_paths` are serialized with
`if <x> is not None`, preserving explicit empties. At `db.py:2614-2615`
`assertions` and `tags` are serialized with `json.dumps(x) if x else None` -
truthiness - so an explicit `[]` collapses to `NULL`.

Three of the five JSON columns use `is not None`; two use truthiness. There is
no evident reason for the split - it reads as an oversight rather than a design
choice. `update_spec` is immune (`db.py:2710-2720` uses `_UNSET` sentinels),
which is precisely why the existing empty-collections regression at
`platform_tests/groundtruth_kb/cli/test_spec_update.py:312` passes while the
record path has no counterpart and would fail if written.

Impact: the postimage trio is sealed by `postimage_sha256`, so a downstream
validator confirms - with a cryptographically valid hash - an assertion about
persisted state that is false. The distinction is also lost irrecoverably: a
spec seeded with `assertions: []` stores `NULL`, so the next update's
carry-forward postimage reports `assertions: null`. The packet chain can never
re-derive the "explicitly empty" fact. This matters beyond the narrow trigger
because approval packets are the durable evidence that a governed write was
owner-approved; an evidence artifact that can be both internally valid and
factually wrong about what was written weakens every consumer that trusts it.

### Finding 2 (P2) - The formal-artifact approval gate fails open when the shared validator import fails

`.claude/hooks/formal-artifact-approval-gate.py` degrades silently to a fallback
validator that performs zero postimage checking, and then allows the write.

At `:39-41` the shared-validator import is wrapped in a broad `except Exception:`
that sets `_shared_validate_packet = None`. `_validate_packet` at `:380-386`
delegates to the shared validator only when it is non-`None`; otherwise it calls
`_fallback_validate_packet` (`:329-377`), which validates `full_content`,
`full_content_sha256`, and approval flags but contains no postimage logic. In
that state the gate accepts a partial trio, a tampered `postimage_sha256`, and
non-JSON-native `postimage_fields`, then prints `{}` (allow) at `:440-444`.

To be explicit about what is not being claimed: on the normal path the gate is
correct. This reviewer specifically verified that `_validate_packet` does
delegate to the shared validator, and refuted a contrary claim raised during
review. The concern is solely the degraded path.

Impact: a governance gate whose failure mode is "allow" inverts the fail-closed
posture the rest of the approval stack depends on. The trigger - any
`ImportError`, partially-installed venv, or `sys.path` disturbance - is a
routine operational condition, not an exotic one, and it produces no signal: the
gate emits an allow verdict indistinguishable from a genuine pass.

### Finding 3 (P3) - Constructor can emit a packet its own validator rejects

`groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:385` emits the
full trio whenever `postimage_fields is not None`, so `postimage_fields={}`
produces all three keys with a well-formed hash; the validator at `:162` then
rejects it as "must be a non-empty JSON object". Not reachable from either CLI
today (both build a fixed thirteen-key mapping), so this is latent.

### Finding 4 (P3) - RecursionError escapes the fail-closed boundary

`approval_packet.py:174` catches only `(TypeError, ValueError)`. `RecursionError`
subclasses `RuntimeError`, so deeply nested `postimage_fields` propagate out of
`validate_packet` as an uncaught exception rather than a
`ValidationResult(is_valid=False)`. Callers at `cli_spec_record.py:258` and
`cli_spec_update.py:272` expect a result object. Latent, but a genuine hole in
an otherwise careful fail-closed design.

### Finding 5 (P3) - Schema-version constant drift

`approval_packet.py:158` hardcodes `!= 1` while `:39` defines
`POSTIMAGE_SCHEMA_VERSION = 1` and `:131` uses the constant inside the hashed
envelope. Bumping the constant would make the constructor emit a version its own
validator rejects.

## Owner Decision Needed

Findings 1 and 2 require source mutation outside the current WI-5741 seven-path
envelope - `groundtruth-kb/src/groundtruth_kb/db.py` and
`.claude/hooks/formal-artifact-approval-gate.py` (plus its template copy). The
hook path is explicitly excluded by the WI-5741 approved proposal, so scope and
authorization must both be settled before any derived proposal is filed.

Prime Builder must obtain durable AskUserQuestion-recorded answers to the
following before filing a derived implementation proposal as `NEW`:

1. **Scope placement.** Should the `db.py` empty-collection repair (Finding 1)
   expand the existing WI-5741 envelope, or become its own work item under
   `PROJECT-GTKB-RELIABILITY-FIXES`? WI-5741 is already in a NO-GO revision
   cycle for an unrelated PAUTH reason, so folding it in is cheap - but it
   widens a thread the owner may prefer to land narrowly.
2. **Backfill semantics.** Existing rows already have `NULL` where an explicit
   `[]` was supplied. Should the fix be forward-only, or is a migration wanted
   to distinguish historical "explicitly empty" from "never set"? Forward-only
   is far simpler; a migration cannot recover information the current schema
   already discarded, so this is really a question about whether to accept the
   permanent loss.
3. **Gate failure posture.** For Finding 2, does the owner want the approval
   gate to hard-block when the shared validator cannot be imported (strict
   fail-closed, risks blocking work during a broken venv), or to block only
   packets carrying postimage keys (narrower, preserves bootstrap)? This is a
   real availability-versus-integrity tradeoff and should not be decided by the
   implementing agent.

No owner action is required at filing time. This advisory is not implementation
approval, not a bridge `GO`, and not a substitute for an implementation
proposal, independent Loyal Opposition review, or an implementation-start
authorization packet.

## Recommended Prime Action

1. Carry Finding 1 into the WI-5741 revision cycle now under way. The missing
   record-path empty-collection regression belongs in
   `platform_tests/groundtruth_kb/cli/test_spec_record.py`, which is already an
   approved WI-5741 target path; it will fail, which is the correct signal.
2. Align `db.py:2614-2615` with the `is not None` form used at `:2598-2600` so
   all five JSON columns are symmetric, after resolving the scope question
   above. Consider a single shared serialization helper so the five columns
   cannot drift apart again.
3. Make the approval-gate degraded path (Finding 2) fail closed, or at minimum
   emit a loud block-with-reason when the shared validator cannot be imported.
   If a fallback must remain for bootstrap, it should refuse any packet carrying
   postimage keys it cannot validate rather than ignoring them. Consider a
   doctor check asserting the shared validator imports cleanly in both hook
   copies.
4. Fold Findings 3-5 into the same reliability work item as low-priority
   hardening; none is independently urgent.

## Classification Slot

- Recommended disposition: `adopt` for Findings 1 and 2; `adapt` for Findings
  3-5 (bundle into the WI-5741 revision or a successor reliability work item).
- Prime Builder records the actual disposition here when converting or
  rejecting this advisory. Conversion to an implementation proposal requires the
  owner decisions enumerated above.
