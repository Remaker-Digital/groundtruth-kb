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

The later [in-progress Chat view](GTKB-Home#read-an-in-progress-session) also
shows a **Session log** control with a download icon at the upper right. Its
format and equivalence to Commands `export` have not been tested. Context
injection and shell activity labels are visible in the conversation, but the
underlying content and tool outputs were not opened. Treat those details as
potentially sensitive; do not request a full environment-variable dump or
private prompt/context disclosure just to reproduce the screenshot.

The [expanded System prompt reference](GTKB-Home#read-the-expanded-system-prompt)
now describes supplied images showing partial prompt text in a bounded scroll
region and a later supplied text snapshot; no live panel was opened by the
reviewer. Raw prompt text, private paths, and surrounding identifiers are
withheld. For a panel or navigation issue,
report the build/version, expansion state, affected scroll region or control,
input method, and a synthetic reproduction. Do not request the full prompt or
assume collapse/clipping removes content from copying, exports, or recordings.
Neither a displayed excerpt nor a supplied text snapshot proves the complete
input sent to a provider or the enforcement of its described behavior.

The [Trajectory reference](GTKB-Home#read-the-trajectory-view) describes a later
view that does expose instruction, context, and tool-payload previews. Its raw
capture is deliberately not published. Before sharing a diagnostic view or
log, use synthetic data or a supported concealment/redaction route if one is
available, review the resulting artifact, and include only what is needed.
Otherwise provide a minimal, redacted text report instead. Do not assume clipped
text is removed from copying or export, and do not run a command merely because
it appears in a recorded tool row. The view's Search field is not the sidebar's
session search; neither establishes a safe support export.

The later [rendered response reference](GTKB-Home#read-a-rendered-response-and-turn-statistics)
also withholds its raw capture: sensitive identifiers and bridge details can
appear in ordinary answer text, not only expanded prompts or tool rows. Before
sharing a screenshot or copied answer, remove details unnecessary to the issue
through a supported safe route or use a synthetic reproduction. Distinguish
what the assistant reported from the expected and independently observed result;
do not publish a full private session merely to substantiate its summary.

The lower-response view exposes overlapping-sheets, thumbs-up/down, and
branching-line icons. No tooltip, accessible name, or action result was captured.
Their exact functions and data handling have not been qualified; do not assume
they copy only visible text, send private feedback, file an issue, share a link,
or fork a session. Use the established support route until each intended action
and its included data/destination are documented. The Commands `feedback` route
and response ratings are not established as equivalent.

For a statistics issue, report the version, relevant counter/metric, full value
only if safely obtainable, reproduction steps, and whether the display is
truncated. The visible ten-call summary and eight-step footer use different
labels and are not by themselves proof of a discrepancy. Identify whether the
issue concerns the response row (**Usage**, **Ran for**, or its timestamp),
sidebar age, or the footer, since matching scope has not been established. Do
not reconstruct clipped Output from Usage minus Input, sum LLM/tool times into
wall-clock time, or provide private logs or provider credentials to explain a
number. A reported wait for an assignment is not by itself a runtime failure;
state the expected next step without publishing private dispatch content.

The [context-usage popover](GTKB-Home#read-the-context-usage-popover) is a separate
composer display, not a demonstrated expansion of the response Usage label.
For a context-accounting issue, identify the installed version and selected
model/reference, the displayed used/capacity values, category estimates, and the
action after which they were observed. Use a synthetic reproduction rather than
dumping system prompts, tool definitions/results, or private messages. The
displayed category estimates do not exactly sum to the headline; report that
observation without guessing its cause. Context occupancy, usage totals, cache
figures, and provider quota should not be treated as interchangeable. A low
percentage does not establish that a run succeeded or that billing has stopped.

A session-log export is not a verified redacted support bundle. Its contents,
credential handling, destination, and restoration/import capability have not
been inspected. Do not upload an unreviewed ZIP to a public issue: inspect and
redact diagnostic material through a supported safe route, and provide only
what the report requires. Follow [Backup and restore](Backup-And-Restore) for
platform recovery; a conversation archive does not replace it.

## Agent tools, cancellation, and task controls

For a behavior described in the [supplied-prompt reference](GTKB-Home#behavior-described-by-the-supplied-prompt),
report the release, selected preset, operation, expected result, and a minimal
synthetic reproduction. Include only the relevant observations:

- For a GUI-context issue, state which screenshot, route information, or other
  permitted evidence was explicitly supplied. Do not assume the agent saw the
  same browser state merely because the conversation occurred in Home.
- For file/search behavior, distinguish path discovery, content search, file
  reads, targeted edits, and replacement writes. Use disposable sample files
  and note omitted/truncated results or unintended changes; do not attach real
  hidden/ignored files or an entire workspace to prove search scope.
- For interruption, identify the affected job through an approved private
  support route or a synthetic label, the stop request and observed confirmation,
  final status/exit code, and any observed remaining process or partial file
  effect. A bare exit code 1 does not by itself distinguish cancellation from
  command failure. Do not stop unrelated work or promise rollback to gather a report.
- For goals, delegation, workflows, or iterative rounds, distinguish the human
  request from the reported outcome and note resume/fork/reload, unexpected
  continuation, or cancellation behavior. Use synthetic context and do not
  post private child prompts, job/session identifiers, or unreviewed output.

The [qualification checklist](Known-Issues#prompt-described-behavior-review)
records the remaining tests. Supplying a prompt for review does not authorize
the reviewer to run its tools or reproduce its side effects.

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
