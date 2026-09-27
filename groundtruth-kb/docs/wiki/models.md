# Models and providers

**Status:** Illustrated provider list and Home Model popover; setup and requests untested

**Reviewed:** 2026-09-26

In [GTKB Home](GTKB-Home), open **Settings → Models** for provider-management
entry points. Home also has a separate composer control whose open popover is
labeled **Model**, illustrated below. The supplied views do not yet show the
complete path from provider setup to choosing a model and receiving a response.

Use this page with [Get started](Get-Started). A visible provider entry is not
an installation-health check, a selected model, or proof that a request will
succeed.

## Read the Models pane

![Models selected in GTKB Home Settings, with API-key guidance, one entry named GTKB OpenRouter marked Custom with a green dot and Edit button, and separate Add provider and Add a custom provider buttons. No API key or selected model is visible.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-models.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged. The exact
build/version is not visible. No API key is visible in this capture. The review
did not open Edit or either Add dialog, inspect stored credentials, change a
provider, or make a model request.

| Visible element | What the capture establishes | What remains unverified |
| --- | --- | --- |
| **Models** heading and API-key helper text | The pane directs users toward provider credentials. | The credential-entry fields, supported authentication methods, and complete setup procedure are not shown. |
| **GTKB OpenRouter** | One provider entry appears with this display name. | Its endpoint, account, saved credential state, available models, and whether the name is a shipped default are not established. |
| **Custom** badge | This entry carries the Custom label. | The label does not establish an API protocol, supported feature set, or compatibility with every custom endpoint. |
| Green dot beside the entry | A green indicator is visible. | No text explanation of its meaning or last-check time is visible. Do not treat it as proof of valid credentials, connectivity, model availability, or a successful request. |
| **Edit** | An editing entry point is shown for this provider. | Its fields, save/cancel behavior, credential masking, and effect on existing sessions have not been inspected. |
| **Add provider** and **Add a custom provider** | Two distinct creation entry points are available. | Their supported choices, required fields, differences, and validation behavior are not shown. |

The shared **Open configuration file** button is also visible. Its target and
the supported credential-storage route have not been established; see
[Settings](Settings#configuration-file-access-and-saving). Do not infer that a
configuration file is the correct place to paste a secret.

## Provider setup is not model selection

The visible entry is a provider configuration label, not a model identifier.
This Settings capture has no model list, selected model, default-model control,
capability list, or completed response. Later Home captures show a separate
composer reference and explicitly label its popover **Model**, as described
below. A further [Commands capture](GTKB-Home#commands-menu) labels `model` as
selecting the model **for this conversation**. That establishes the scope stated
by the UI, not tested inheritance, persistence, or effects on an active request.

The **GTKB OpenRouter** name is an example from this installation, not a
recommendation, a requirement to use that provider, or a complete list of
supported providers. Document each supported route against the selected release;
do not invent endpoint URLs, model identifiers, dropdown choices, or a
connection-test button from this image.

Model/provider configuration does not assign a governed agent role, change
session file permissions, or authorize project work. Those are separate
concepts described in [Settings](Settings) and [Core concepts](Core-Concepts).

## Read the Home composer reference

In the [selected-workspace Home screenshot](Get-Started#home-with-a-selected-workspace),
the right-hand composer control displays
`@preset/gtkb-openrouter-deepseek-v4-flash` while the separate **Standard mode**
menu is open. The following capture opens the right-hand control itself. Its
popover explicitly labels the displayed reference **Model**. This establishes
the control's model-related purpose; that is no longer an inference from the
reference's name.

![GTKB Home with the right-hand composer control open. Its popover contains a Model row showing @preset/gtkb-openrouter-deepseek-v4-flash and a right-facing chevron; the same reference remains on the trigger below. Standard mode, Workspace Write, and the GT-KB workspace are visible. No model alternatives, prompt, or response are shown.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-home-model-popover.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged; exact
build/version not shown. The reference and workspace name are examples from
this installation, not required defaults. The reviewer did not open a model
submenu, select or change a model, inspect credentials, or send a request.

| Visible element | What the capture establishes | What it does not establish |
| --- | --- | --- |
| Right-hand composer control | It displays `@preset/gtkb-openrouter-deepseek-v4-flash`, with its popover open. | The reference's definition, persistence, or effect on a running session. |
| **Model** row with the same reference | The UI explicitly identifies this as a model-related setting, separate from Standard mode and Workspace Write. | A resolved API model identifier, provider endpoint/account, valid credential, available balance, or a successful request. The matching text is not two different model entries. |
| Right-facing chevron on the Model row | A further navigation affordance is visible. | Its destination, alternative models, filtering/search, supported inventory, or selection behavior. One visible row is not proof that only one model is available. |

To locate this setting, use the reference-labeled control at the lower right of
the composer and identify its **Model** row. The capture stops there; it does
not show the next view or a completed model change. The next walkthrough must
inspect the row's destination, record actual choices and reference resolution,
then verify the effective provider/model before the first request.

The Commands menu also advertises a `model` entry. Its destination and
relationship to the Model popover have not been exercised. Verify that both
routes expose the same effective conversation selection and explain any
differences; do not infer identical dialogs from their related labels.

Do not derive an endpoint, account, API model ID, or price by splitting the
reference label, assume it is a shipped default, or paste the full `@preset/...`
text into a provider's model-ID field. The shared word *preset* still needs a
plain-language explanation: the agent-mode preset describes tools, prompt, and
capabilities, while this reference is displayed under **Model** and its exact
schema and resolution remain unverified. It does not change permission scope
or authorize project work.

Document dismissal/back navigation, keyboard use, focus, change timing,
persistence, unavailable or unresolved references, and useful recovery before
recommending model switches. The example label is not a provider/model
recommendation or a successful-connection indicator.

## Credentials, usage, and data destination

Keep API keys out of screenshots, prompts, Wiki pages, Git commits, public
issues, and diagnostic output. A setup walkthrough should use non-secret
placeholders and keep any real credential entry off-camera.

Before a model-request test, confirm the intended provider, account, endpoint,
model, data destination, and any usage charges or limits. Do not infer included
API usage from the provider entry or a green dot. Likewise, a locally hosted
GTKB interface is not a promise that a selected model processes data locally.
Use non-sensitive sample content for the first-response demonstration.

The documentation still needs verified credential storage/protection, masking,
redaction, replacement, and removal guidance. Removing a provider entry must not
be assumed to revoke a credential at its issuing provider. No storage-security,
retention, or revocation behavior was tested in this pass.

## Complete the setup walkthrough

The next illustrated procedure should establish, in a separate test installation:

1. When to use **Add provider** versus **Add a custom provider**, with the actual
   supported choices and required fields.
2. How to obtain and enter the required credential through the provider's
   official guidance and the product's supported interface, without exposing it.
3. How changes are saved, what the status indicator means, and how errors are
   distinguished from an untested configuration.
4. How the illustrated Home **Model** row leads to the actual choices, and how
   named references resolve to the intended provider/model for a new session,
   including scope and the effect of later changes.
5. A bounded, non-sensitive first request and expected response, followed by
   recovery guidance for authentication, endpoint, model, and usage-limit errors.

This is a coverage checklist, not a claim that these exact screens or a test
button already exist. Until the route is verified, use the installed release's
supported provider procedure and [Support](Support) when a step is unclear.
Do not paste credentials into a conversation or edit generated harness files
to work around a missing setup instruction.

See the [Models review checklist](Known-Issues#models-review) for the remaining
documentation, usability, and verification work, and [Training](Training) for
the planned first-session walkthrough.
