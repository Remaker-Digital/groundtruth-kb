# Release health

**Status:** Current documentation of evidence classes, not a live release claim
**Reviewed:** 2026-09-26

Release readiness is not one green counter. A release decision must distinguish
the exact product bytes, test results, independent review, Git state,
installation, actual-host qualification, backup/recovery evidence, and remaining
known limitations.

## Evidence classes

| Evidence | What it establishes |
| --- | --- |
| Git status and exact object identities | The candidate cohort and any unrelated or uncommitted paths |
| Specification-derived test results | Behavior observed in the stated test environment |
| Independent review | The final bytes and evidence inspected by a separate review context |
| Project finalization | The complete verified project cohort and its Git result |
| Installed-service readiness | The selected installed services answered their real readiness checks |
| Restart qualification | The installation recovered after a real host restart |
| Backup and restore drill | Recovery succeeded from the copy intended for the asserted loss scenario |
| Documentation comparison | Published Wiki pages match reviewed source |

None of these substitutes for another. In particular:

- `VERIFIED` is review completion, not proof of a commit.
- A commit is not proof that the product was installed or started successfully.
- A readiness endpoint is not complete release qualification.
- A generated dashboard is not authority for the underlying product state.
- Backup creation is not proof of recovery.

## Documentation release gate

Critical installation, Get Started, troubleshooting, upgrade, backup/restore,
and uninstall pages must accurately describe the selected release. Published
Wiki content must match `groundtruth-kb/docs/wiki/` before a public release.

Use `scripts/update_wiki_pages.py compare` against a fresh Wiki clone to detect
publication drift. A zero-drift comparison proves equality of the selected text;
it does not prove that the text is behaviorally correct. Command and cold-read
qualification remain separate gates.

Current customer-impacting gaps are listed in [Known issues](Known-Issues).
