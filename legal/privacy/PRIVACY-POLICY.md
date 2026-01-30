# Agent Red Customer Engagement — Privacy Policy

> **Status:** DRAFT — For internal review only. Not yet published.
> **Version:** 0.1.0
> **Last Updated:** 2026-01-29
> **Legal Review Required:** Yes — must be reviewed by qualified legal counsel before publication.

---

## Privacy Policy

**Effective Date:** [TO BE SET AT PUBLICATION]

This Privacy Policy describes how VanDusen & Palmeter, LLC, doing business as Remaker Digital ("Company", "we", "us", or "our"), collects, uses, discloses, and protects information in connection with the Agent Red Customer Engagement platform ("Service").

By accessing or using the Service, you acknowledge that you have read and understood this Privacy Policy. If you do not agree with our practices, do not use the Service.

---

### 1. Scope

This Privacy Policy applies to:

- The Agent Red Customer Engagement web application and API;
- Information collected from Account holders ("Customers");
- Information collected from individuals who interact with the Service through a Customer's deployment ("End Users");
- Our marketing website at https://remakerdigital.com.

This Privacy Policy does not apply to third-party websites, products, or services, even if linked from our Service.

---

### 2. Information We Collect

#### 2.1 Account Information

When you create an Account, we collect:

- **Contact Information:** Name, email address, company name, job title
- **Account Credentials:** Email address and password (passwords are hashed and never stored in plain text)
- **Billing Information:** Payment card details are processed by our payment processor and are not stored on our servers

#### 2.2 Customer Data

Customers submit data to the Service for processing, including:

- **Customer Inquiries:** Text-based support requests from End Users
- **Product Information:** Product catalogs, pricing, and inventory data
- **Knowledge Base Content:** FAQs, policies, and reference materials
- **Order Data:** Order history and transaction details submitted for customer support purposes

We process Customer Data solely on behalf of and under the instructions of our Customers. With respect to Customer Data containing personal information of End Users, the Customer is the data controller and we are the data processor.

#### 2.3 Usage Data

We automatically collect information about how you use the Service:

- **Service Logs:** API requests, response times, error rates, conversation volumes
- **Feature Usage:** Features accessed, configuration changes, integration activity
- **Performance Metrics:** System performance data used to maintain and improve the Service

#### 2.4 Device and Connection Information

When you access our website or Service, we may collect:

- **Browser Information:** Browser type and version
- **Device Information:** Operating system, device type
- **Network Information:** IP address, general geographic location (city/region level)
- **Referral Information:** How you arrived at our website

#### 2.5 Cookies and Similar Technologies

Our website uses cookies and similar technologies for:

- **Essential Cookies:** Required for authentication and security
- **Analytics Cookies:** Used to understand how visitors interact with our website (via Google Analytics)
- **Preference Cookies:** Used to remember your settings and preferences

You can control cookie preferences through your browser settings. Disabling essential cookies may prevent you from using certain features of the Service.

---

### 3. How We Use Information

We use the information we collect for the following purposes:

#### 3.1 Service Delivery

- Processing Customer Data through our AI-powered customer engagement platform
- Providing, maintaining, and improving the Service
- Authenticating users and managing Accounts
- Processing payments and managing Subscriptions

#### 3.2 AI Processing

The Service uses artificial intelligence to process customer inquiries. When processing Customer Data:

- **AI Models:** Customer inquiries are processed by AI language models hosted on Microsoft Azure OpenAI Service
- **PII Protection:** Before sending data to AI models, we apply PII tokenization — personally identifiable information is replaced with random tokens (format: `TOKEN_[UUID]`) to prevent exposure to third-party AI services
- **Data Minimization:** Only the content necessary for generating a response is sent to AI models; metadata and Account information are not included
- **No Model Training (Default):** By default, Customer Data is not used to train, fine-tune, or improve AI models. Microsoft Azure OpenAI Service does not use customer data for model training. This is the standard behavior for all tiers.
- **Opt-In Dedicated Model Training (Enterprise):** Enterprise Customers may opt in to Dedicated Model Training, which fine-tunes a per-customer AI model using that Customer's own historical conversation data exclusively. This requires explicit written consent. Opted-in data is used only to train that Customer's dedicated model — it is never combined with other Customers' data, shared with third parties, or used to improve general-purpose models. Customers may revoke consent at any time, which halts all future training and deletes the fine-tuned model within 30 days.

#### 3.3 Communication

- Sending transactional emails (account confirmations, billing notices, security alerts)
- Sending product updates and service announcements
- Responding to support requests

#### 3.4 Analytics and Improvement

- Analyzing aggregate usage patterns to improve the Service
- Monitoring system performance and reliability
- Identifying and fixing technical issues

#### 3.6 Personalization Processing

The Service provides Persistent Customer Memory, which processes Customer Data to personalize support interactions:

- **Customer Context Profiles (All Tiers):** We assemble structured profiles from integration data (e.g., Shopify customer records), account metadata, and communication preferences. These profiles are injected into each conversation to enable personalized responses. Legal basis: legitimate interest in providing the contracted service.
- **Conversation Memory (All Tiers):** After each conversation, transcripts are cleansed of personally identifiable information and transient data, then converted into vector embeddings stored in Cosmos DB. These embeddings enable semantic search across a customer's prior conversations so they do not need to repeat themselves. Legal basis: legitimate interest in providing the contracted service.
- **Cross-Session Learning (Professional and Enterprise Tiers):** A memory framework analyzes accumulated conversation transcripts to extract durable patterns such as communication preferences, recurring issues, and product interests. These extracted insights are stored as structured data in the customer's profile. Legal basis: legitimate interest in providing the contracted service.
- **Dedicated Model Training (Enterprise Tier, Opt-In Only):** As described in Section 3.2, Enterprise Customers may opt in to fine-tuning a dedicated AI model. Legal basis: explicit consent.

All personalization data is tenant-isolated — one Customer's data is never accessible to another Customer. End Users may request deletion of their personalization data through the Customer who deployed the Service (see Section 7).

#### 3.5 Legal and Safety

- Complying with legal obligations
- Enforcing our Terms of Service
- Protecting against fraud, abuse, and security threats

---

### 4. How We Share Information

We do not sell personal information. We share information only in the following circumstances:

#### 4.1 Service Providers

We use third-party service providers to help operate the Service:

| Provider | Purpose | Data Shared | Location |
|----------|---------|-------------|----------|
| Microsoft Azure | Cloud hosting, compute, storage | Customer Data (encrypted), Account data | United States (East US 2) |
| Microsoft Azure OpenAI Service | AI language model processing | PII-tokenized inquiry content | United States (Azure region) |
| Payment Processor (TBD) | Payment processing | Billing information | United States |
| Google Analytics | Website analytics | Anonymized browsing data | United States |

All service providers are contractually required to protect information and use it only for the purposes we specify.

#### 4.2 Customer-Directed Integrations

When a Customer connects third-party integrations (e.g., Shopify, Zendesk, Mailchimp), data flows between the Service and those platforms as directed by the Customer. These integrations are governed by the third party's own privacy policy.

#### 4.3 Legal Requirements

We may disclose information if required by law, regulation, legal process, or governmental request, including:

- Responding to lawful subpoenas, court orders, or search warrants
- Complying with regulatory requirements
- Protecting the rights, property, or safety of the Company, our users, or the public

#### 4.4 Business Transfers

In the event of a merger, acquisition, reorganization, or sale of assets, information may be transferred as part of that transaction. We will notify affected users of any change in ownership or control of their information.

---

### 5. Data Storage and Security

#### 5.1 Data Location

All Customer Data is processed and stored in Microsoft Azure data centers located in the United States (East US 2 region, Virginia).

#### 5.2 Security Measures

We implement industry-standard security measures, including:

- **Encryption in Transit:** All data transmitted to and from the Service is encrypted using TLS 1.2 or higher
- **Encryption at Rest:** Customer Data stored in our databases is encrypted at rest using AES-256
- **Access Controls:** Role-based access controls and the principle of least privilege for all system access
- **Secret Management:** API keys and credentials are stored in Azure Key Vault with Managed Identity access
- **Network Security:** Virtual network isolation, network security groups, and application gateway with WAF
- **Monitoring:** Application Insights and OpenTelemetry for security event monitoring
- **PII Tokenization:** Personally identifiable information is tokenized before processing by third-party AI services

#### 5.3 Incident Response

In the event of a data breach that affects your personal information, we will:

- Notify affected users without unreasonable delay
- Notify applicable regulatory authorities as required by law
- Provide details about the nature of the breach and steps taken to address it

---

### 6. Data Retention

#### 6.1 Customer Data

- **During Subscription:** Customer Data is retained for the duration of your active Subscription
- **After Termination:** Customer Data is available for export for 30 days after Account termination, after which it is permanently deleted
- **Backups:** Backup copies are purged within 90 days of deletion

#### 6.2 Account Information

- Account information is retained for the duration of your Account plus 30 days after termination
- Billing records may be retained for up to 7 years as required for tax and accounting purposes

#### 6.3 Personalization Data

- **Customer Context Profiles:** Retained for the duration of the Subscription; deleted within 30 days of Account termination
- **Conversation Memory Vectors:** Retained for 24 months from the date of the originating conversation, then automatically purged; all vectors deleted within 30 days of Account termination
- **Cross-Session Learning Data:** Retained for the duration of the Subscription; deleted within 30 days of Account termination
- **Fine-Tuned Models (Dedicated Model Training):** Retained for the duration of the add-on Subscription; deleted within 30 days of add-on cancellation or consent revocation

#### 6.4 Usage Data

- Service logs and usage data are retained for 7 days in Application Insights
- Aggregated, anonymized analytics data may be retained indefinitely

#### 6.5 Marketing Website Data

- Website analytics data is retained according to Google Analytics' standard retention settings
- Cookie data expires according to the cookie types described in Section 2.5

---

### 7. Your Rights

Depending on your jurisdiction, you may have the following rights regarding your personal information:

#### 7.1 Access and Portability

You have the right to request a copy of the personal information we hold about you. Customers can export their Customer Data at any time through the Service.

#### 7.2 Correction

You have the right to request correction of inaccurate personal information. You can update your Account information through your Account settings.

#### 7.3 Deletion

You have the right to request deletion of your personal information. You can delete your Account through your Account settings, or contact us at privacy@remakerdigital.com. Deletion includes all Persistent Customer Memory data associated with your Account, including customer context profiles, conversation memory vectors, cross-session learning data, and any fine-tuned models created under Dedicated Model Training.

#### 7.4 Restriction and Objection

You may have the right to restrict or object to certain processing of your personal information.

#### 7.5 Exercising Your Rights

To exercise any of these rights, contact us at privacy@remakerdigital.com. We will respond to requests within 30 days. We may ask you to verify your identity before processing your request.

---

### 8. End User Privacy

#### 8.1 Customer Responsibility

Customers are responsible for providing appropriate privacy notices to their End Users regarding the collection and processing of End User data through the Service.

#### 8.2 End User Rights

End Users who wish to exercise privacy rights regarding their data should contact the Customer who deployed the Service. Customers can fulfill End User requests using the data export and deletion features available in the Service.

#### 8.3 Children's Privacy

The Service is not directed to children under 16. We do not knowingly collect personal information from children. Customers must not use the Service to process data from children under 16 without appropriate parental consent and compliance with applicable children's privacy laws (including COPPA).

---

### 9. International Data Transfers

The Service is hosted in the United States. If you access the Service from outside the United States, your information will be transferred to and processed in the United States.

For users in the European Economic Area (EEA), United Kingdom, or Switzerland, we rely on:

- Standard Contractual Clauses (SCCs) approved by the European Commission
- Our Data Processing Agreement, which incorporates appropriate safeguards

For more information about international transfers, see our [Data Processing Agreement](/dpa).

---

### 10. California Privacy Rights

If you are a California resident, the California Consumer Privacy Act (CCPA) and California Privacy Rights Act (CPRA) provide you with additional rights:

- **Right to Know:** You may request information about the categories and specific pieces of personal information we have collected
- **Right to Delete:** You may request deletion of your personal information
- **Right to Opt-Out of Sale:** We do not sell personal information
- **Right to Non-Discrimination:** We will not discriminate against you for exercising your privacy rights

To exercise these rights, contact us at privacy@remakerdigital.com or use the mechanisms described in Section 7.

---

### 11. Changes to This Privacy Policy

We may update this Privacy Policy from time to time. We will notify you of material changes by:

- Posting the updated Privacy Policy on our website
- Sending an email to the address associated with your Account
- Providing notice through the Service

We will provide at least 30 days' notice before material changes take effect. Your continued use of the Service after the effective date constitutes acceptance of the updated Privacy Policy.

---

### 12. Contact Us

If you have questions about this Privacy Policy or our privacy practices, contact us at:

**VanDusen & Palmeter, LLC (DBA Remaker Digital)**
Email: privacy@remakerdigital.com
Website: https://remakerdigital.com

For data protection inquiries specific to the EU/EEA, you may also contact us at: dpo@remakerdigital.com

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

> **IMPORTANT NOTICE:** This document is an AI-generated draft provided for internal planning purposes only. It is NOT legal advice. This document must be reviewed and approved by qualified legal counsel before publication or use. Do not rely on this draft as a binding legal document.
