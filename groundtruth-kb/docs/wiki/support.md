# Support and documentation feedback

**Status:** Current public routes
**Reviewed:** 2026-09-26

Use the [GTKB GitHub repository](https://github.com/Remaker-Digital/groundtruth-kb)
for public product feedback.

## Report a product defect

Open a [GitHub issue](https://github.com/Remaker-Digital/groundtruth-kb/issues)
and include:

- GTKB version;
- supported host and relevant prerequisite versions;
- exact reproduction steps;
- expected and actual results;
- exact exit code;
- redacted diagnostics; and
- whether the issue reproduces after a controlled restart.

## Report a documentation defect

State the Wiki page, heading, incorrect or missing instruction, product version,
and the consequence for the user. Documentation that teaches retired authority,
status, path, or installation behavior is a correctness defect, not merely an
editorial preference.

## Feedback and session-log export in Home

The [Home Commands menu](GTKB-Home#commands-menu) advertises `feedback` to record
feedback about the session and `export` to download its log as a ZIP archive.
These entry points exist in the supplied capture; neither was executed for this
review. The feedback destination, included data, submission confirmation, and
failure/retry behavior still need qualification. Do not assume it files a
GitHub issue or a canonical GTKB defect record.

A session-log export is not a verified redacted support bundle. Its contents,
credential handling, destination, and restoration/import capability have not
been inspected. Do not upload an unreviewed ZIP to a public issue: inspect and
redact diagnostic material through a supported safe route, and provide only
what the report requires. Follow [Backup and restore](Backup-And-Restore) for
platform recovery; a conversation archive does not replace it.

## Security reports

Use the repository's current security reporting route rather than a public issue
when disclosure could expose a vulnerability or credential. Do not include
secrets, private application content, browser launch URLs, database copies, or
unredacted logs in public reports.

## Support expectations

A formal response-time or commercial support policy is not yet published. Do not
infer an SLA from repository visibility or activity. The eventual policy should
identify supported releases, response targets, security handling, and end-of-life
rules.
