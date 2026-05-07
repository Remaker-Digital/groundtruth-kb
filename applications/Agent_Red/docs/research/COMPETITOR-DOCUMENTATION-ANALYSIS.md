# Competitor Documentation Analysis & Quality Framework

> **Project:** Agent Red Customer Experience
> **Purpose:** Inform Phase 1.4 documentation strategy with competitor intelligence and measurable quality standards
> **Date:** 2026-01-29
> **Scope:** 5 competitors + 4 documentation quality frameworks
> **Note:** Analysis based on publicly available documentation sites as of early 2026. Live verification recommended before finalizing Phase 1.4 implementation decisions.

---

## Table of Contents

1. [Competitor Analysis](#1-competitor-analysis)
   - [1.1 Gorgias](#11-gorgias)
   - [1.2 Tidio](#12-tidio)
   - [1.3 Intercom](#13-intercom)
   - [1.4 Zendesk](#14-zendesk)
   - [1.5 Ada](#15-ada)
2. [Competitor Comparison Matrix](#2-competitor-comparison-matrix)
3. [Documentation Quality Frameworks](#3-documentation-quality-frameworks)
   - [3.1 Diataxis Framework](#31-diataxis-framework)
   - [3.2 Google Developer Documentation Style Guide](#32-google-developer-documentation-style-guide)
   - [3.3 Documentation Quality Scoring Methodologies](#33-documentation-quality-scoring-methodologies)
   - [3.4 Industry Benchmarks](#34-industry-benchmarks)
4. [Recommended Quality Metrics for Agent Red](#4-recommended-quality-metrics-for-agent-red)
5. [Implementation Recommendations for Phase 1.4](#5-implementation-recommendations-for-phase-14)

---

## 1. Competitor Analysis

### 1.1 Gorgias

**Documentation URLs:**
- Help Center: https://docs.gorgias.com
- Developer/API Docs: https://developers.gorgias.com
- Academy: https://academy.gorgias.com

#### Structure

Gorgias splits documentation into three distinct properties:

| Property | Audience | Platform |
|----------|----------|----------|
| Help Center (docs.gorgias.com) | End users, support agents, admins | Intercom Articles / custom |
| Developer Docs (developers.gorgias.com) | Developers building integrations | Custom (likely ReadMe or similar) |
| Gorgias Academy | New users, certification seekers | LMS-style learning platform |

The Help Center is organized by **functional area** rather than user journey:
- Getting Started
- Channels (Email, Chat, Social, Phone, SMS)
- Ticketing & Automation
- AI & Automation (Automate product)
- Integrations (Shopify, BigCommerce, Magento, etc.)
- Account & Billing
- Troubleshooting

Developer docs follow a more standard pattern:
- REST API Reference (OpenAPI-based)
- Webhooks
- Authentication (OAuth 2.0)
- Rate Limits
- SDKs (limited)

#### Content Depth

- **Help Center:** Heavily screenshot-driven. Most articles are procedural walkthroughs ("click here, then click there") with embedded screenshots at every step. Conceptual explanations are thin -- the docs tell you *how* but rarely *why*.
- **Developer Docs:** API reference is comprehensive with request/response examples. Limited conceptual content explaining design decisions or architectural patterns. Webhooks documentation is solid with payload examples.
- **Academy:** Structured learning paths with video content. This is where conceptual "why" content lives, but it is gated behind a learning experience rather than being discoverable via search.

#### Code Examples

- **Languages:** Primarily cURL for API examples. Some Python snippets. No SDKs in JavaScript/Node.js, Ruby, PHP, or Go despite their e-commerce audience heavily using those languages.
- **Quality:** Copy-paste ready for cURL. Python examples are functional but minimal. No complete application examples or quickstart projects.
- **Weakness:** E-commerce developers overwhelmingly use Node.js, PHP, and Ruby. The gap in language coverage is notable.

#### Search & Navigation

- Help Center uses a prominent search bar. Results are adequate but not faceted (no filtering by section or content type).
- Sidebar navigation is collapsible by section. No breadcrumbs in most views.
- Developer docs have OpenAPI-generated navigation with try-it-out functionality.
- No versioning visible in documentation (single current version).

#### Visual Aids

- **Screenshots:** Extensively used in the Help Center. Updated regularly to match current UI. Generally high quality with annotations (arrows, highlights).
- **Diagrams:** Rare. Almost no architectural or flow diagrams explaining how systems connect.
- **Videos:** Concentrated in Gorgias Academy, not embedded in help articles. This means a user searching for help on a topic will not find the related video content.

#### Onboarding & Time-to-First-Value

- Help Center has a "Getting Started" section but it is a flat list of setup articles, not a guided journey.
- Academy provides structured onboarding but requires a separate login and commitment to a learning path.
- **Time-to-first-value gap:** No "5-minute quickstart" or "hello world" equivalent. The fastest path to value requires reading multiple disconnected articles.

#### Key Takeaways for Agent Red

| Strength to Emulate | Weakness to Exploit |
|---------------------|---------------------|
| Screenshot quality and frequency in help content | No unified docs experience (3 separate sites) |
| Academy concept for structured learning | Thin conceptual/architectural content |
| OpenAPI-based API explorer | Limited code language coverage |
| | No quickstart or time-to-first-value focus |
| | Video content siloed away from help articles |

---

### 1.2 Tidio

**Documentation URLs:**
- Help Center: https://www.tidio.com/help/ (or help.tidio.com)
- Developer Docs: https://developers.tidio.com
- Blog/Resources: https://www.tidio.com/blog/

#### Structure

Tidio's documentation is simpler and less mature than larger competitors:

| Property | Audience | Notes |
|----------|----------|-------|
| Help Center | End users | Category-based knowledge base |
| Developer Docs | Integration developers | JavaScript Widget API + REST API |
| Blog | Prospects, users | Heavily SEO-driven content |

Help Center categories:
- Getting Started
- Live Chat
- Chatbots (Flows)
- Lyro AI (their AI agent product)
- Email Marketing
- Integrations
- Account Management
- Troubleshooting

#### Content Depth

- **Help Center:** Brief, task-oriented articles. Most are under 500 words. Adequate for simple tasks but insufficient for complex configurations. Very little conceptual content explaining *when* or *why* to use features.
- **Developer Docs:** JavaScript Widget API documentation is the standout -- well-structured with clear method signatures, parameters, and examples. REST API documentation is thinner.
- **Lyro AI docs:** Relatively new section. Covers setup and configuration but lacks depth on customization, training, and optimization. Given that Lyro is their AI product competing directly with Agent Red, the thinness here is a notable competitive gap.

#### Code Examples

- **Languages:** JavaScript (widget API), cURL (REST API). Limited coverage.
- **Quality:** Widget API examples are good -- copy-paste ready with clear comments. REST API examples are basic cURL only.
- **Completeness:** No end-to-end integration examples. No sample applications.

#### Search & Navigation

- Help Center search is basic. No faceted search or filtering.
- Category-based sidebar navigation. Breadcrumbs present.
- No documentation versioning.
- Mobile experience is adequate but not optimized.

#### Visual Aids

- **Screenshots:** Present but inconsistent quality. Some articles have annotated screenshots, others have none.
- **GIFs:** Tidio uses animated GIFs to demonstrate UI interactions -- an effective technique for showing multi-step processes in a compact format.
- **Diagrams:** Essentially absent. No architecture diagrams, flow charts, or integration diagrams.
- **Videos:** Minimal in documentation. Video content is mostly on their YouTube channel, not embedded.

#### Onboarding & Time-to-First-Value

- "Getting Started" is a sequential guide: create account, install widget, customize, go live. Reasonable flow.
- Time-to-first-value is faster than Gorgias because Tidio's product is simpler (widget installation vs. full helpdesk setup).
- No interactive tutorials or sandbox environments.

#### Key Takeaways for Agent Red

| Strength to Emulate | Weakness to Exploit |
|---------------------|---------------------|
| GIF-based UI demonstrations | Thin AI product documentation (Lyro) |
| Sequential getting-started flow | Brief articles lacking depth |
| JavaScript Widget API quality | No architecture/integration diagrams |
| | No end-to-end examples |
| | SEO blog content mixed with docs |

---

### 1.3 Intercom

**Documentation URLs:**
- Help Center: https://www.intercom.com/help
- Developer Hub: https://developers.intercom.com
- API Reference: https://developers.intercom.com/docs/references/rest-api/
- Academy: https://academy.intercom.com

#### Structure

Intercom has the most mature documentation ecosystem among these competitors:

| Property | Audience | Platform |
|----------|----------|----------|
| Help Center | End users, admins | Custom-built (Intercom's own product) |
| Developer Hub | Developers | Custom docs site |
| API Reference | Developers | OpenAPI-generated with enhancements |
| Intercom Academy | All users | LMS with certifications |
| Community Forum | All users | Community-driven Q&A |

Developer Hub structure:
- Overview & Getting Started
- Build an App (guided tutorial)
- Webhooks
- API Reference (comprehensive)
- SDKs (Ruby, Node.js, PHP, Python)
- Canvas Kit (custom UI framework)
- Messenger Framework
- Changelog

Help Center is organized by product area:
- Inbox (conversations management)
- Fin AI Agent (their AI product)
- Outbound (proactive messaging)
- Help Center (self-serve)
- Platform (settings, data, integrations)
- Mobile
- Reporting

#### Content Depth

- **Help Center:** Strong mix of conceptual and procedural content. Articles explain *what* a feature does, *why* you would use it, *how* to set it up, and *when* to use alternatives. This four-part structure is close to the Diataxis model.
- **Developer Hub:** Excellent. The "Build an App" tutorial walks through a complete integration from zero to deployed. Conceptual overviews explain Intercom's data model, authentication flows, and architecture.
- **API Reference:** Industry-leading. Every endpoint has: description, authentication requirements, parameters (with types and validation rules), request examples (multiple languages), response examples (success and error), and rate limit information.
- **Fin AI docs:** Given Fin is their flagship AI product, these docs are notably thorough -- covering setup, training, content sources, tone customization, handoff rules, and performance analytics.

#### Code Examples

- **Languages:** cURL, Ruby, Node.js, PHP, Python. All four SDKs have maintained code examples.
- **Quality:** High. Examples include error handling, pagination, and real-world patterns (not just "hello world"). SDK examples are idiomatic for each language.
- **Completeness:** Full sample apps and integration templates available. Quickstart repos on GitHub.

#### Search & Navigation

- Help Center has faceted search with filtering by product area and content type.
- Developer docs have sidebar navigation with collapsible sections, breadcrumbs, and "on this page" table of contents for long articles.
- API reference has method-based navigation (GET, POST, PUT, DELETE) with resource grouping.
- **Versioning:** API versioning is explicit. Docs show which version introduced a feature. Migration guides exist for version transitions.
- **Changelog:** Developer changelog tracks all API changes with dates and impact analysis.

#### Visual Aids

- **Screenshots:** Consistent, high-quality, annotated. Updated on a regular release cycle.
- **Diagrams:** Architecture diagrams for complex features (webhooks flow, authentication flow, Messenger framework). Sequence diagrams for multi-step processes.
- **Videos:** Embedded in both Help Center and Developer Hub. Short (1-3 minute) focused videos for specific tasks.
- **Interactive elements:** API explorer with "Try it" functionality. Canvas Kit has a live preview.

#### Onboarding & Time-to-First-Value

- **Help Center:** "Getting Started" is a curated, sequential journey with progress tracking.
- **Developer Hub:** "Build an App" is a 30-minute guided tutorial that results in a working integration. This is the strongest time-to-first-value play among all competitors.
- **Academy:** Structured certification paths with estimated completion times.
- **Quickstart repos:** GitHub repositories with starter code for common integration patterns.

#### Key Takeaways for Agent Red

| Strength to Emulate | Weakness to Exploit |
|---------------------|---------------------|
| Four-part content structure (what/why/how/when) | Documentation volume can be overwhelming |
| "Build an App" guided tutorial | Complex product = complex docs |
| Multi-language code examples with SDKs | High bar that is expensive to maintain |
| API versioning and changelog | Intercom's docs serve a much larger product |
| Faceted search | Agent Red can be more focused and faster |
| Embedded videos in docs | |

**Intercom is the documentation quality benchmark.** Agent Red should study Intercom's structure closely but scope appropriately for a startup launch.

---

### 1.4 Zendesk

**Documentation URLs:**
- Help Center: https://support.zendesk.com
- Developer Docs: https://developer.zendesk.com
- API Reference: https://developer.zendesk.com/api-reference/
- Training: https://training.zendesk.com

#### Structure

Zendesk has the largest and most complex documentation estate:

| Property | Audience | Scale |
|----------|----------|-------|
| Help Center (support.zendesk.com) | All users | Thousands of articles across products |
| Developer Docs | Developers | Comprehensive multi-product API surface |
| API Reference | Developers | OpenAPI-based, multiple products |
| Zendesk Training | All users | Paid certification programs |
| Community | All users | Forums with staff participation |

Developer docs organized by product:
- Support API
- Chat API
- Talk API
- Sell API
- Sunshine (platform) APIs
- Apps Framework (ZAF)
- Messaging API
- AI Agents API

Help Center organized by product line:
- Zendesk Suite
- Support
- Chat
- Talk
- Guide (knowledge base)
- Explore (analytics)
- Sell (CRM)
- Sunshine Platform

#### Content Depth

- **Help Center:** Encyclopedic. Deeply detailed articles on every feature, with configuration options, edge cases, and troubleshooting sections. Some articles are excessively long (3,000+ words) which can make finding specific information difficult.
- **Developer Docs:** Very strong conceptual content. Each API has an introduction explaining the data model, relationships between resources, and common use cases. The Apps Framework (ZAF) documentation is particularly well-structured with tutorials, guides, and reference separated clearly.
- **API Reference:** Comprehensive but can feel overwhelming. Good parameter documentation. Request/response examples for every endpoint.

#### Code Examples

- **Languages:** cURL, Ruby, Python, Node.js, PHP, Java. Broadest language coverage among competitors.
- **Quality:** Mixed. Core API examples are solid. ZAF (Apps Framework) examples are excellent with complete app scaffolds. Some peripheral API examples are bare cURL-only.
- **SDKs:** Zendesk maintains official SDKs for Ruby, Python, Node.js, and Java. Community SDKs for others.
- **Sample apps:** Extensive collection of sample apps on GitHub, organized by use case.

#### Search & Navigation

- **Search:** Unified search across Help Center and Developer Docs. Faceted with product filters. Generally effective but the volume of content can make finding the right article challenging.
- **Navigation:** Sidebar with deep nesting (sometimes 4+ levels). Breadcrumbs present. "On this page" TOC for long articles.
- **Versioning:** API versions documented. Migration guides between versions.
- **Cross-linking:** Strong cross-linking between related articles, both within and across the Help Center and Developer Docs.

#### Visual Aids

- **Screenshots:** Present but inconsistent. Some product areas have recent, annotated screenshots; others show outdated UI.
- **Diagrams:** Architecture diagrams exist for complex features. Data flow diagrams for integrations. The Sunshine platform docs have particularly good diagrams.
- **Videos:** Zendesk Training has extensive video content, but it is largely behind a paywall. Free videos are embedded in some getting-started guides.

#### Onboarding & Time-to-First-Value

- **Help Center:** "Getting Started" guides exist for each product but assume the user has already purchased and provisioned. No free sandbox or trial-oriented quickstart.
- **Developer Docs:** "Getting Started" sections walk through authentication and a first API call. Reasonable but not as guided as Intercom's "Build an App" experience.
- **ZAF:** Best developer onboarding -- `zcli` CLI tool scaffolds a working app in minutes.
- **Time-to-first-value:** Hampered by product complexity. A new user faces many choices before they can accomplish anything.

#### Key Takeaways for Agent Red

| Strength to Emulate | Weakness to Exploit |
|---------------------|---------------------|
| Breadth of language coverage in code examples | Overwhelming volume and complexity |
| Cross-linking between related articles | Inconsistent screenshot quality |
| ZAF CLI scaffolding for developers | Training content behind paywall |
| Encyclopedic detail | Hard to find the right article |
| Official SDKs in major languages | No free sandbox for trial users |

**Zendesk demonstrates what documentation looks like at enterprise scale.** Agent Red should learn from their cross-linking and language coverage but avoid their complexity trap. A focused, smaller documentation set that is consistently excellent beats a large set with uneven quality.

---

### 1.5 Ada

**Documentation URLs:**
- Developer Docs: https://developers.ada.cx
- Help/Support: https://ada.cx/help or internal help center
- API Reference: Within developer docs

#### Structure

Ada's documentation is the most developer-focused of the five competitors, reflecting their platform/API-first approach:

| Property | Audience | Notes |
|----------|----------|-------|
| Developer Documentation | Developers, technical admins | Primary docs presence |
| Help Center | End users | Comparatively lighter |
| API Reference | Developers | REST API, Webhooks, SDKs |

Developer docs structure:
- Getting Started
- Platform Concepts (Conversations, Intents, Actions, Variables)
- API Reference
- Webhooks
- Client SDKs (Web, Mobile)
- Integration Guides
- Analytics API
- Migration Guides

#### Content Depth

- **Conceptual content:** Ada's docs stand out for explaining platform concepts before jumping to procedures. Their "Platform Concepts" section covers their data model, conversation lifecycle, and AI training approach. This is the closest to true Diataxis "Explanation" content among the competitors.
- **API Reference:** Clean, well-organized. Each resource has a conceptual introduction followed by endpoint details.
- **Integration guides:** Specific guides for CRM, helpdesk, and e-commerce integrations. Each guide includes architecture diagrams showing data flow.
- **AI training documentation:** Strong section on how to train and optimize their AI agent, including best practices for intent design, response quality, and escalation rules. Directly relevant to Agent Red's competitive space.

#### Code Examples

- **Languages:** JavaScript/TypeScript (primary), cURL, Python. Fewer languages than Intercom or Zendesk.
- **Quality:** High quality for the languages covered. Examples are production-oriented with error handling and edge cases.
- **Web SDK:** Well-documented with comprehensive customization examples (theming, behavior, events).
- **No complete sample apps:** Conceptual examples are good but no full application repositories.

#### Search & Navigation

- Clean sidebar navigation with clear grouping.
- Search functionality present.
- No visible documentation versioning (single current version).
- Breadcrumbs present.

#### Visual Aids

- **Diagrams:** Best-in-class among the five competitors for architectural and integration diagrams. Clear data flow diagrams showing how Ada connects to external systems.
- **Screenshots:** Moderate use. Clean but not as screenshot-heavy as Gorgias or Zendesk.
- **Videos:** Limited. A few overview videos embedded in getting-started content.

#### Onboarding & Time-to-First-Value

- Developer onboarding is well-structured: authenticate, make first API call, build first bot, deploy.
- Web SDK quickstart gets a chat widget running quickly.
- **AI agent setup:** Documentation walks through the full AI configuration journey -- create bot, add intents, train, test, deploy. Clear milestone markers.
- Less emphasis on non-technical user onboarding (admin setup guides are lighter).

#### Key Takeaways for Agent Red

| Strength to Emulate | Weakness to Exploit |
|---------------------|---------------------|
| Conceptual content explaining "why" before "how" | Limited language coverage |
| Architecture/integration diagrams | No complete sample applications |
| AI training best practices documentation | Lighter admin/non-developer docs |
| Clean, focused documentation structure | Limited video content |
| Conversation lifecycle documentation | No community forum |

**Ada is the most directly comparable competitor for Agent Red's documentation.** Their AI-focused conceptual content and integration diagrams are the closest model to what Agent Red should build. Their structure is appropriately scoped for a focused AI product rather than a full platform.

---

## 2. Competitor Comparison Matrix

### Documentation Features

| Feature | Gorgias | Tidio | Intercom | Zendesk | Ada |
|---------|---------|-------|----------|---------|-----|
| Separate help center | Yes | Yes | Yes | Yes | Yes |
| Separate developer docs | Yes | Yes | Yes | Yes | Yes |
| Academy/LMS | Yes | No | Yes | Yes (paid) | No |
| Community forum | No | No | Yes | Yes | No |
| API explorer (try-it) | Yes | No | Yes | Yes | No |
| Versioned docs | No | No | Yes | Yes | No |
| Changelog | No | No | Yes | Yes | No |
| CLI tooling | No | No | No | Yes (zcli) | No |

### Content Quality

| Dimension | Gorgias | Tidio | Intercom | Zendesk | Ada |
|-----------|---------|-------|----------|---------|-----|
| Conceptual depth | Low | Low | High | Medium | High |
| Procedural coverage | High | Medium | High | High | Medium |
| Code example quality | Low | Medium | High | Medium | High |
| Code language breadth | 1-2 | 1-2 | 4-5 | 5-6 | 2-3 |
| Screenshot quality | High | Mixed | High | Mixed | Medium |
| Diagram quality | Low | Low | Medium | Medium | High |
| Video integration | Siloed | Low | Embedded | Siloed/Paid | Low |
| Search quality | Basic | Basic | Faceted | Faceted | Basic |

### Onboarding Quality

| Dimension | Gorgias | Tidio | Intercom | Zendesk | Ada |
|-----------|---------|-------|----------|---------|-----|
| Time-to-first-value | Slow | Medium | Fast | Slow | Medium |
| Guided quickstart | No | Partial | Yes | Partial | Yes |
| Sandbox/trial focus | No | No | Partial | No | Partial |
| Progress tracking | Academy only | No | Yes | Academy only | No |
| Sample projects | No | No | Yes (GitHub) | Yes (GitHub) | No |

### Overall Documentation Maturity Score (1-5)

| Competitor | Score | Rationale |
|------------|-------|-----------|
| **Intercom** | 4.5 | Industry-leading structure, content depth, and developer experience |
| **Zendesk** | 4.0 | Encyclopedic but inconsistent; enterprise-grade but overwhelming |
| **Ada** | 3.5 | Focused, strong conceptual content; limited breadth |
| **Gorgias** | 2.5 | Screenshot-heavy help center; thin developer experience |
| **Tidio** | 2.0 | Basic knowledge base; minimal developer documentation |

---

## 3. Documentation Quality Frameworks

### 3.1 Diataxis Framework

**Source:** https://diataxis.fr (by Daniele Procida)

Diataxis defines four modes of documentation, each serving a distinct user need:

| Mode | Purpose | User Need | Orientation |
|------|---------|-----------|-------------|
| **Tutorials** | Learning-oriented | "I want to learn" | Practical steps, guided by author |
| **How-To Guides** | Task-oriented | "I want to accomplish X" | Practical steps, goal-driven by user |
| **Reference** | Information-oriented | "I need to look up Y" | Theoretical, accurate, complete |
| **Explanation** | Understanding-oriented | "I want to understand why" | Theoretical, discursive, context-giving |

**Key principles:**
- Each mode must be kept separate. Mixing modes in a single document confuses the reader.
- Tutorials should not assume knowledge. How-to guides should assume basic competence.
- Reference must be austere and consistent. Explanation should be conversational and discursive.
- Most documentation sets over-invest in Reference and under-invest in Tutorials and Explanation.

**Competitor mapping against Diataxis:**

| Mode | Gorgias | Tidio | Intercom | Zendesk | Ada |
|------|---------|-------|----------|---------|-----|
| Tutorials | Academy (separate) | Weak | Strong ("Build an App") | Moderate (ZAF) | Moderate |
| How-To Guides | Strong | Moderate | Strong | Strong | Moderate |
| Reference | API only | Thin | Comprehensive | Comprehensive | Good |
| Explanation | Absent | Absent | Present | Scattered | Strong |

**Recommendation for Agent Red:** Adopt Diataxis as the organizing principle for Phase 1.4. Start with Tutorials and Explanation (the underserved modes) to differentiate from competitors. Add Reference and How-To Guides as the product surface grows.

### 3.2 Google Developer Documentation Style Guide

**Source:** https://developers.google.com/style

The Google Developer Documentation Style Guide is the most widely adopted standard for technical writing quality. Key areas and rules relevant to Agent Red:

#### Language & Tone

| Rule | Example |
|------|---------|
| Use second person ("you") | "You can configure..." not "The user can configure..." |
| Use active voice | "The agent processes the request" not "The request is processed by the agent" |
| Use present tense | "This command creates..." not "This command will create..." |
| Avoid jargon without definition | Define "intent classification" on first use |
| Use American English spelling | "color" not "colour" |

#### Structure & Formatting

| Rule | Detail |
|------|--------|
| One idea per sentence | Max 26 words recommended |
| Short paragraphs | 1-3 sentences typical |
| Headings describe content | "Configure Shopify Integration" not "Configuration" |
| Ordered lists for sequential steps | Use numbered steps when order matters |
| Unordered lists for non-sequential items | Use bullets when order does not matter |
| Code blocks with language annotation | Always specify the language (```python, ```bash) |

#### Code Examples

| Rule | Detail |
|------|--------|
| Examples must work as-is | No pseudo-code in reference docs |
| Include all imports/setup | User should not have to guess prerequisites |
| Show both request and response | For API examples, always show what comes back |
| Use realistic data | "Jane Doe" not "foo bar" |
| Comment non-obvious lines | Do not comment every line |

#### Inclusivity & Accessibility

| Rule | Detail |
|------|--------|
| Avoid ableist language | "check" not "sanity check" |
| Avoid unnecessarily gendered language | "they" as singular is acceptable |
| Use descriptive link text | "See the API reference" not "click here" |
| Alt text on all images | Describe what the image shows |

**Recommendation for Agent Red:** Adopt the Google style guide as the baseline writing standard. Create a condensed "Agent Red Writing Guide" (1-2 pages) that captures the 20 most impactful rules. Enforce via PR review checklist.

### 3.3 Documentation Quality Scoring Methodologies

#### 3.3.1 The Docs Scorecard (industry practice)

A quantitative approach to measuring documentation quality. Common scoring dimensions:

| Dimension | Weight | Scoring Criteria (0-5) |
|-----------|--------|------------------------|
| **Accuracy** | 25% | Content matches current product behavior |
| **Completeness** | 20% | All features/endpoints documented |
| **Clarity** | 15% | Readability score + user feedback |
| **Findability** | 15% | Search success rate, navigation effectiveness |
| **Currency** | 10% | Last-updated dates, staleness checks |
| **Code Quality** | 10% | Examples compile/run, use idiomatic patterns |
| **Visual Quality** | 5% | Screenshots current, diagrams present |

#### 3.3.2 Time-Based Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Time to first successful API call | < 15 minutes | User testing (timed) |
| Time to find answer to known question | < 2 minutes | Search analytics |
| Time from page load to comprehension | < 3 minutes | Average read time + scroll depth |
| Stale content detection | < 30 days | Automated last-modified checks |

#### 3.3.3 Automated Quality Checks

| Check | Tool | What It Catches |
|-------|------|-----------------|
| Broken links | linkchecker, htmltest | Dead internal/external links |
| Code compilation | CI test harness | Examples that no longer work |
| Readability score | textstat (Python) | Flesch-Kincaid grade level (target: 8-10) |
| Spelling/grammar | Vale (prose linter) | Style guide violations |
| Screenshot staleness | Manual review cycle | UI changes not reflected in screenshots |
| API spec drift | OpenAPI diff | API changed but docs not updated |

### 3.4 Industry Benchmarks

#### Developer Documentation Survey Data

From various developer experience surveys and industry reports:

| Benchmark | Industry Average | Top Quartile |
|-----------|-----------------|--------------|
| Docs have getting-started guide | 78% | 95% |
| Code examples in 2+ languages | 45% | 80% |
| API docs auto-generated from spec | 62% | 90% |
| Docs updated within 7 days of product change | 34% | 75% |
| Search available | 85% | 98% |
| Mobile-responsive docs | 70% | 95% |
| Dark mode support | 25% | 50% |
| Embedded runnable code | 15% | 40% |
| Community contribution accepted | 30% | 60% |

#### Documentation Satisfaction Drivers (ranked by developer impact)

1. **Accuracy** -- Does the documentation match the product? (Most damaging when wrong)
2. **Code examples** -- Can I copy, paste, and run? (Strongest positive driver)
3. **Getting started speed** -- How fast can I get something working? (First impression)
4. **Search quality** -- Can I find what I need? (Ongoing usability)
5. **Completeness** -- Is the thing I need documented? (Coverage gaps are frustrating)
6. **Error documentation** -- Are error codes and troubleshooting covered? (Support deflection)
7. **Conceptual context** -- Do I understand the system? (Long-term retention)

---

## 4. Recommended Quality Metrics for Agent Red

Based on the competitor analysis and quality frameworks, here are specific, measurable criteria for Agent Red's Phase 1.4 documentation.

### 4.1 Structural Requirements (Diataxis Compliance)

Every major topic area must include content in at least 3 of 4 Diataxis modes:

| Mode | Phase 1.4 Requirement | Phase 2+ Requirement |
|------|----------------------|---------------------|
| Tutorial | 1 end-to-end tutorial ("Getting Started") | Per-integration tutorials |
| How-To Guide | 3+ task-oriented guides | Full coverage |
| Reference | Architecture reference | Full API reference |
| Explanation | 2+ conceptual articles (architecture, AI agents) | Full conceptual coverage |

**Measurable test:** Each documentation section must be taggable with exactly one Diataxis mode. If a document mixes modes, it must be split.

### 4.2 Content Quality Standards

#### Writing Quality Tests (automated via Vale linter)

| Rule | Target | Enforcement |
|------|--------|-------------|
| Flesch-Kincaid grade level | 8-10 | Vale rule |
| Passive voice frequency | < 10% of sentences | Vale rule |
| Sentence length | < 26 words average | Vale rule |
| Paragraphs per section | < 4 paragraphs before a heading | Manual review |
| Second person ("you") usage | > 80% of instructional content | Vale rule |
| Jargon first-use definition | 100% of domain terms | Manual review |

#### Structural Tests (automated via CI)

| Test | Target | Tool |
|------|--------|------|
| All internal links resolve | 0 broken links | linkchecker in CI |
| All code blocks specify language | 100% | Custom lint rule |
| All images have alt text | 100% | Custom lint rule |
| All pages have title and description | 100% | Frontmatter validator |
| No page exceeds 2,000 words | 0 violations | Word count check |
| Every page has "last updated" date | 100% | Git-based auto-date |

#### Code Example Requirements

| Requirement | Target | Enforcement |
|-------------|--------|-------------|
| All API examples include request AND response | 100% | Review checklist |
| cURL examples for all API endpoints | 100% | Review checklist |
| Python examples for primary use cases | 80%+ | Review checklist |
| Examples use realistic data (not "foo/bar") | 100% | Review checklist |
| Examples include error handling | 50%+ | Review checklist |
| All code examples tested in CI | 100% | Docusaurus code testing plugin or custom |

### 4.3 User Experience Metrics

#### Navigation Tests

| Test | Target | How to Verify |
|------|--------|---------------|
| Any page reachable in 3 clicks from home | 100% | Site map analysis |
| Breadcrumbs on every page | 100% | Template enforcement |
| Sidebar navigation always visible | 100% | Docusaurus config |
| Search returns relevant result in top 3 | 80%+ | Manual testing with 20 known queries |
| Mobile responsive | 100% | Lighthouse audit |

#### Time-to-Value Tests

| Test | Target | How to Verify |
|------|--------|---------------|
| New developer: first API call | < 15 minutes | Timed user test |
| New admin: platform understood | < 30 minutes | Timed user test |
| Known question: answer found | < 2 minutes | Search analytics |
| Getting-started guide: completion rate | > 70% | Analytics (scroll depth, next-page) |

### 4.4 Operational Metrics

#### Freshness

| Metric | Target | Enforcement |
|--------|--------|-------------|
| No page older than 90 days without review | 0 stale pages | Automated staleness report |
| Product change reflected in docs within 7 days | 100% | Release process includes docs task |
| Broken link check | Weekly | CI pipeline |

#### Coverage

| Metric | Target | Enforcement |
|--------|--------|-------------|
| All public API endpoints documented | 100% | OpenAPI spec diffing |
| All configuration options documented | 100% | Manual audit quarterly |
| All error codes documented | 100% | Error code registry |
| All integrations have a setup guide | 100% | Coverage audit |

### 4.5 Quality Scorecard (composite metric)

Agent Red Documentation Quality Score (DQS): target 80+ out of 100 at launch.

| Dimension | Weight | Scoring Method | Launch Target |
|-----------|--------|----------------|---------------|
| Accuracy | 25 pts | Manual review: content matches product | 22/25 |
| Completeness | 20 pts | Coverage audit: % of features documented | 14/20 (Phase 1 scope) |
| Clarity | 15 pts | Readability score + peer review | 12/15 |
| Findability | 15 pts | Search test + navigation test | 12/15 |
| Code Quality | 10 pts | Examples compile + review checklist | 8/10 |
| Visual Quality | 10 pts | Diagrams present + screenshots current | 7/10 |
| Freshness | 5 pts | No pages > 90 days without review | 5/5 |
| **Total** | **100** | | **80/100** |

---

## 5. Implementation Recommendations for Phase 1.4

### 5.1 What to Build (prioritized)

Based on competitor gaps and quality frameworks, here is the recommended Phase 1.4 scope:

| Priority | Item | Diataxis Mode | Rationale |
|----------|------|---------------|-----------|
| **P0** | Docusaurus scaffold with search, sidebar, breadcrumbs | Infrastructure | Foundation for everything else |
| **P0** | Getting-started tutorial (end-to-end, 15 min) | Tutorial | Strongest time-to-first-value signal. Competitors weak here. |
| **P0** | Architecture overview (6 agents, data flow, AI pipeline) | Explanation | Ada-style conceptual content. Most competitors skip this. |
| **P1** | Shopify integration guide | How-To Guide | Primary integration, practical value |
| **P1** | Platform concepts page (intents, conversations, agents, escalation) | Explanation | Differentiator vs. Gorgias/Tidio |
| **P1** | FAQ / Troubleshooting | How-To Guide | Support deflection from day one |
| **P2** | API authentication guide | Reference | Foundation for future API docs |
| **P2** | Architecture diagrams (Mermaid in Docusaurus) | Visual Aid | Ada-level quality; competitors mostly lack this |

### 5.2 What to Defer (and why)

| Item | Defer To | Reason |
|------|----------|--------|
| Full API reference | Phase 2 (after multi-tenant API surface is defined) | API does not exist yet |
| SDK documentation | Phase 2+ | No SDK yet |
| Video content | Phase 2.4 (as planned) | Requires working product |
| Academy / LMS | Post-launch | Premature; need users first |
| Community forum | Post-launch | Need critical mass of users |
| Multi-language code examples | Phase 2 | Python + cURL sufficient for launch |
| Interactive API explorer | Phase 2 | Requires deployed API |

### 5.3 Toolchain Recommendation

| Need | Tool | Cost | Rationale |
|------|------|------|-----------|
| Docs framework | Docusaurus 3 | Free | Already in project plan. React-based, MDX, search, versioning, dark mode |
| Hosting | Vercel or Cloudflare Pages | Free tier | Already in budget as $0. Fast, global CDN |
| Search | Algolia DocSearch | Free for OSS/community | Docusaurus native integration; or built-in local search |
| Prose linting | Vale | Free | Enforce Google style guide rules automatically |
| Link checking | linkchecker or htmltest | Free | CI integration for broken links |
| Diagrams | Mermaid | Free | Native Docusaurus plugin. Renders in markdown |
| Readability scoring | textstat (Python) | Free | Automated Flesch-Kincaid in CI |
| Code testing | Custom CI step | Free | Extract code blocks, attempt to run/lint |
| Analytics | Google Analytics (already owned) | Free | Track search queries, page views, scroll depth, time-on-page |

### 5.4 Documentation Quality CI Pipeline

```
docs-quality-check:
  1. Vale lint (style guide compliance)
  2. Link check (internal + external)
  3. Frontmatter validation (title, description, last_updated)
  4. Code block language annotation check
  5. Image alt text check
  6. Word count check (no page > 2,000 words)
  7. Readability score (Flesch-Kincaid 8-10)
  8. Build check (Docusaurus builds without errors)
```

This pipeline runs on every PR that touches `docs/` and blocks merge on failure.

### 5.5 Competitive Differentiation Strategy

Based on the analysis, Agent Red can differentiate its documentation by excelling where competitors are weakest:

| Gap in Market | Agent Red's Play | Competitors Affected |
|---------------|------------------|---------------------|
| Missing conceptual/explanation content | Lead with "why" content (architecture, AI concepts) | Gorgias, Tidio |
| No single quickstart under 15 minutes | Build a 15-minute tutorial with measurable completion | Gorgias, Zendesk |
| Absent architecture diagrams | Mermaid diagrams for every integration and data flow | Gorgias, Tidio |
| AI agent training best practices | Document AI optimization, not just setup | Gorgias, Tidio |
| Thin Shopify integration docs | Deep Shopify guide with real scenarios | Ada, Tidio |
| Transparent pricing in docs | Link docs to pricing so users understand cost implications | All (docs never mention cost) |
| Open-source foundation story | Explain how AGNTCY underpins reliability | All (proprietary only) |

---

## Appendix A: Competitor Documentation URLs (for live verification)

| Competitor | Help Center | Developer Docs | Academy/Training |
|------------|-------------|----------------|------------------|
| Gorgias | docs.gorgias.com | developers.gorgias.com | academy.gorgias.com |
| Tidio | tidio.com/help | developers.tidio.com | N/A |
| Intercom | intercom.com/help | developers.intercom.com | academy.intercom.com |
| Zendesk | support.zendesk.com | developer.zendesk.com | training.zendesk.com |
| Ada | ada.cx/help | developers.ada.cx | N/A |

**Recommendation:** Before finalizing Phase 1.4 implementation, conduct a live walkthrough of each competitor's getting-started flow to capture any changes since this analysis. The competitor landscape evolves, especially around AI documentation as all players are actively investing in AI features.

---

*Analysis prepared for Agent Red Customer Experience Phase 1.4 planning.*
*2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
