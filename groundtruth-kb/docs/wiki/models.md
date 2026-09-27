# Models and providers

**Status:** Illustrated provider-list reference; setup and model requests untested

**Reviewed:** 2026-09-26

In [GTKB Home](GTKB-Home), open **Settings → Models**. The supplied view shows
provider-management entry points. It does not yet show the complete path from
provider setup to selecting a model and receiving a first response.

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
This capture has no model list, selected model, default-model control, capability
list, or completed response. It also does not establish whether model choice is
global, workspace-specific, or session-specific, or whether it belongs in a
different view.

The **GTKB OpenRouter** name is an example from this installation, not a
recommendation, a requirement to use that provider, or a complete list of
supported providers. Document each supported route against the selected release;
do not invent endpoint URLs, model identifiers, dropdown choices, or a
connection-test button from this image.

Model/provider configuration does not assign a governed agent role, change
session file permissions, or authorize project work. Those are separate
concepts described in [Settings](Settings) and [Core concepts](Core-Concepts).

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
4. Where to select the model and verify the intended provider/model for a new
   session, including the scope and effect of later changes.
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
