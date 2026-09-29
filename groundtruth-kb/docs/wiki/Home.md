# GroundTruth KB documentation

GroundTruth KB (GTKB) is a local-first development platform for software work
with AI coding agents. It connects requirements, executable tests, projects,
work items, independent review, and the Git result that activates completed
work. GTKB Home is the interactive interface; `gt` is the command-line client.

**New to GTKB? Start with the path that matches your situation.**

## Explore the product

Read the [Product overview](Product-Overview) to understand what GTKB does,
then check [System requirements](System-Requirements) and
[Known issues](Known-Issues) before deciding whether it fits your environment.

GTKB is under active development. The documented installation is Windows-hosted
and uses a native PostgreSQL domain service. Installing the Python package alone
does **not** create a complete host: PostgreSQL, the GTKB service, configuration,
and GTKB Home also need setup. The current
[Windows installation procedure](Install-on-Windows) is for operators, not a
qualified one-click customer installer.

## Use an installed host

1. [Verify installation](Verify-Installation): check the selected host and its
   required components.
2. [Get started](Get-Started): open Home, choose the right workspace, and check
   the controls before a request.
3. [Core concepts](Core-Concepts): understand projects, work items, and review
   before attempting your [first governed change](First-Governed-Change).

Get Started is an orientation guide. A version-pinned, end-to-end first-session
tutorial is still a [documented gap](Known-Issues), not a completed qualification.

## Resolve a problem

Use [Troubleshooting](Troubleshooting) to find a symptom and its first safe
check. If that does not resolve it, [Support](Support) explains what to collect
and how to report a problem without exposing credentials or private content.

## Find a reference

| You need to understand... | Read... |
| --- | --- |
| The interface and everyday controls | [GTKB Home](GTKB-Home), [Settings](Settings) |
| Models, tools, and agent modes | [Models](Models), [Plugins](Plugins), [Agent presets](Agent-Presets) |
| Health indicators and background components | [Status](Status), [Services](Services) |
| Advanced operational tuning | [Controls](Controls) |
| Maintaining an installation | [Upgrade](Upgrade), [Backup and restore](Backup-and-Restore), [Uninstall](Uninstall) |
| Available learning material and planned walkthroughs | [Training](Training) |
| Current release evidence and limitations | [Release health](Release-Health), [Known issues](Known-Issues) |

## About these docs

This GitHub Wiki is the customer-facing documentation. Reviewed source lives in
`groundtruth-kb/docs/wiki/` in the
[GTKB repository](https://github.com/Remaker-Digital/groundtruth-kb).
Component READMEs are maintainer references, not prerequisites for finding an
ordinary installation, launch, or recovery step.

Page review dates describe documentation review, not product qualification.
Screenshots show captured states; illustrations explain concepts and are labeled
as such. Check the page's stated limitations against your installed version.

**Reviewed:** 2026-09-28
