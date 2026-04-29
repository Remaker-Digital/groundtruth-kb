NO-GO

# Loyal Opposition Review - GTKB Spec Lifecycle Schema Migration

**Document:** `gtkb-spec-lifecycle-schema-2026-04-29`
**Reviewed version:** `bridge/gtkb-spec-lifecycle-schema-2026-04-29-001.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-29

## Verdict

NO-GO. The proposal is aligned with the owner-directed lifecycle correction and correctly keeps implementation in later slice bridges, but the current scoping plan has three blocking defects that would make the migration unsafe: the `parent` column ordering is mechanically unbuildable against the populated SQLite table, the proposed `parent` backfill rules silently misclassify governance specs by the proposal's own examples, and the `implementation_verified_at` backfill depends on a bridge timestamp field that the file bridge protocol does not define.

## Prior Deliberations

I searched deliberations before review with:

```text
python -m groundtruth_kb deliberations search "spec lifecycle schema migration parent attribute verified retired status priority authority provisional_until" --limit 8
```

Relevant hit:

- `DELIB-0707` - Owner decision that existing specs must be migrated to the enriched schema using implementation as reference. This supports doing a real migration rather than a forward-only model, but it also increases the burden on the backfill rules to avoid silent corpus-wide misclassification.

The reviewed proposal cites `DELIB-0707`, `DELIB-0636`, `DELIB-0791`, `DELIB-0808`, `DELIB-1196`, `DELIB-1245`, and `DELIB-1403`; I found no prior deliberation that reverses the lifecycle-date direction.

## Blocking Findings

### F1 - `parent NOT NULL` is sequenced before `parent` backfill

**Claim:** Slice 1 cannot safely add `parent TEXT NOT NULL` with no default while deferring existing-row classification to Slice 4.

**Evidence:**
- The current schema has a populated `specifications` table with `status TEXT NOT NULL` and no `parent` column at `groundtruth-kb/src/groundtruth_kb/db.py:57` and `groundtruth-kb/src/groundtruth_kb/db.py:68`; the current view simply selects `s.*` at `groundtruth-kb/src/groundtruth_kb/db.py:413`.
- The proposal's Slice 1 adds `parent TEXT NOT NULL CHECK (parent IN ('gtkb', 'application', 'all'))` with "No default" at `bridge/gtkb-spec-lifecycle-schema-2026-04-29-001.md:98`.
- The proposal defers write-path changes that require `parent` to Slice 4 at `bridge/gtkb-spec-lifecycle-schema-2026-04-29-001.md:166` and `bridge/gtkb-spec-lifecycle-schema-2026-04-29-001.md:170`.
- The one-time `parent` backfill is also described under the later backfill phase at `bridge/gtkb-spec-lifecycle-schema-2026-04-29-001.md:227` through `bridge/gtkb-spec-lifecycle-schema-2026-04-29-001.md:231`.

**Risk/impact:** On SQLite, adding a `NOT NULL` column with no default to an existing populated table is not an ordinary compatibility-window addition. Prime would either fail the migration or have to rebuild/backfill the table inside Slice 1, contradicting the slice contract and bypassing the later classification safeguards.

**Required revision:** Pick one explicit migration shape:

- Add `parent` nullable in Slice 1, backfill it before any read path depends on it, then enforce `NOT NULL`/`CHECK` with a table rebuild after zero ambiguous rows remain; or
- Move `parent` classification/backfill into Slice 1 and include the table-rebuild mechanics, populated-fixture tests, and owner-review triage output in that slice.

Whichever shape is chosen, the first implementation bridge must test against a populated fixture, not only an empty schema.

### F2 - The `parent` backfill rules silently misclassify cited governance specs

**Claim:** The broad `type='governance'` / `GOV-*` rule conflicts with the proposal's own `parent` semantics and examples.

**Evidence:**
- The proposal says every `type='governance'` spec or `GOV-*` id backfills to `parent='all'` at `bridge/gtkb-spec-lifecycle-schema-2026-04-29-001.md:182`.
- The verification matrix asserts that `GOV-*` to `all` is correct because governance specs are cross-workspace at `bridge/gtkb-spec-lifecycle-schema-2026-04-29-001.md:306`.
- The detailed design then lists `GOV-FILE-BRIDGE-AUTHORITY-001` as a `gtkb` example at `bridge/gtkb-spec-lifecycle-schema-2026-04-29-001.md:333`, while listing `GOV-ARTIFACT-APPROVAL-001` as an `all` example at `bridge/gtkb-spec-lifecycle-schema-2026-04-29-001.md:335`.
- Live KB inspection shows `GOV-FILE-BRIDGE-AUTHORITY-001` is `type=governance`, `section=file_bridge_governance`, and `status=verified`; under the proposed rule it would be auto-classified `all`, not `gtkb`.

**Risk/impact:** This violates acceptance criterion 14's "zero silent misclassifications" requirement at `bridge/gtkb-spec-lifecycle-schema-2026-04-29-001.md:261`. A broad prefix/type rule would stamp thousands of durable artifacts with workspace scope before the ambiguity is surfaced.

**Required revision:** Replace the broad governance/prefix auto-rule with a conflict-aware classifier:

- classify only rules that are demonstrably non-conflicting;
- emit a dry-run report of every classified and ambiguous spec before mutation;
- send governance records whose scope cannot be proven from section/id/content to owner-review triage rather than defaulting to `all`;
- add regression cases for `GOV-FILE-BRIDGE-AUTHORITY-001` and `GOV-ARTIFACT-APPROVAL-001` or equivalent fixtures that prove platform-only governance and cross-workspace governance are distinguished.

### F3 - `implementation_verified_at` backfill depends on a non-protocol bridge timestamp

**Claim:** The proposal says to backfill from the first verified bridge version's `changed_at` timestamp, but the file bridge protocol does not define a `changed_at` field for bridge versions.

**Evidence:**
- The proposal says `implementation_verified_at` should be backfilled from existing bridge `VERIFIED` evidence and "the first `verified` version's `changed_at` timestamp" at `bridge/gtkb-spec-lifecycle-schema-2026-04-29-001.md:187`.
- The bridge protocol defines the index as `Document:` plus `{STATUS}: bridge/{name}-{NNN}.md` lines at `.claude/rules/file-bridge-protocol.md:68` through `.claude/rules/file-bridge-protocol.md:83`.
- The protocol's statuses table defines `VERIFIED` as a status, not a dated event with a canonical timestamp, at `.claude/rules/file-bridge-protocol.md:85` through `.claude/rules/file-bridge-protocol.md:93`.

**Risk/impact:** The migration could produce non-reproducible dates by guessing from file headers, filesystem metadata, or git history, and different harnesses could derive different `implementation_verified_at` values. That would undermine the goal of replacing ambiguous status strings with durable lifecycle facts.

**Required revision:** Define the exact timestamp authority before implementation. Acceptable options include a KB deliberation `changed_at` for the harvested bridge thread, a git commit timestamp with a deterministic lookup rule, or a migration timestamp with the original bridge file stored as evidence. The revised proposal must state fallback behavior when no authoritative timestamp can be derived.

## Additional Required Revisions

- Decouple the spec-level `parent` vocabulary from the unresolved active-workspace proposal, or explicitly state that this bridge uses the owner-requested spec values independently. The adjacent active-workspace thread is currently `NO-GO` and its required state vocabulary is `gt-kb` / `hosted-application`, not `gtkb` / `application` / `all`.
- For Open Question 1, default ambiguous legacy specs to owner-review triage, not `parent='all'`.
- For Open Question 2, the separate `set_spec_parent(...)` operation is the safer shape because it preserves change rationale and avoids silent generic updates.
- For Open Question 4, use a structured machine-readable triage artifact or a Markdown file with a stable table schema plus generated summary. The implementation bridge should specify the exact format and tests.
- For Open Question 6, define `all` metrics explicitly. My recommendation: count `all` once in total corpus counts, and include it in both workspace-filtered views only when the filter asks "applicable to this workspace."

## GO Conditions

A revised scoping proposal can receive GO when it:

1. Provides a mechanically valid SQLite migration sequence for `parent` on the populated `specifications` table.
2. Replaces the broad governance/prefix backfill rule with conflict-aware classification and owner-review triage.
3. Defines an authoritative, reproducible timestamp source for `implementation_verified_at` backfill.
4. Updates the slice boundaries and acceptance criteria so Slice 1 cannot land a non-null required field before existing rows and insert paths can satisfy it.
5. Carries the same specification linkage and spec-derived verification discipline into each follow-on slice bridge.

## Decision Needed From Owner

None for this review. Prime Builder can revise within the owner-stated lifecycle and `parent` requirements already captured in the proposal.

## Scan Result

File bridge scan: 1 entry processed.
