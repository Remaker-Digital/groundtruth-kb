# Agent Red Customer Engagement — Data Processing Agreement

> **Status:** DRAFT — For internal review only. Not yet published.
> **Version:** 0.1.0
> **Last Updated:** 2026-01-29
> **Legal Review Required:** Yes — must be reviewed by qualified legal counsel before publication.

---

## Data Processing Agreement (DPA)

**Effective Date:** [TO BE SET AT PUBLICATION]

This Data Processing Agreement ("DPA") forms part of the Terms of Service ("Agreement") between VanDusen & Palmeter, LLC, doing business as Remaker Digital ("Processor", "we", "us", or "our"), and you ("Controller", "Customer"), collectively referred to as the "Parties".

This DPA applies where and to the extent that the Processor processes Personal Data on behalf of the Controller in the course of providing the Agent Red Customer Engagement platform ("Service").

---

### 1. Definitions

**"Applicable Data Protection Laws"** means all laws and regulations relating to the processing of Personal Data that apply to the Parties, including but not limited to: the General Data Protection Regulation (EU) 2016/679 ("GDPR"), the UK General Data Protection Regulation ("UK GDPR"), the California Consumer Privacy Act ("CCPA"), the California Privacy Rights Act ("CPRA"), and any other applicable privacy legislation.

**"Controller"** means the entity that determines the purposes and means of the processing of Personal Data. In this DPA, the Controller is the Customer.

**"Data Subject"** means an identified or identifiable natural person whose Personal Data is processed.

**"Personal Data"** means any information relating to an identified or identifiable natural person that is processed by the Processor on behalf of the Controller through the Service.

**"Personal Data Breach"** means a breach of security leading to the accidental or unlawful destruction, loss, alteration, unauthorized disclosure of, or access to, Personal Data.

**"Processor"** means the entity that processes Personal Data on behalf of the Controller. In this DPA, the Processor is Remaker Digital.

**"Processing"** means any operation performed on Personal Data, whether automated or not, including collection, recording, organization, structuring, storage, adaptation, alteration, retrieval, consultation, use, disclosure by transmission, dissemination, alignment, combination, restriction, erasure, or destruction.

**"Sub-processor"** means any third party engaged by the Processor to process Personal Data on behalf of the Controller.

**"Standard Contractual Clauses" or "SCCs"** means the standard contractual clauses for the transfer of personal data to third countries adopted by the European Commission.

---

### 2. Scope and Roles

#### 2.1 Roles

The Customer is the Controller and Remaker Digital is the Processor with respect to Personal Data processed through the Service.

#### 2.2 Scope of Processing

The Processor processes Personal Data solely for the purposes of providing the Service as described in the Agreement and as further specified in Annex 1 (Details of Processing).

#### 2.3 Controller Obligations

The Controller shall:

- Ensure it has a lawful basis for the processing of Personal Data and for the transfer of Personal Data to the Processor
- Provide all necessary privacy notices to Data Subjects
- Ensure that its instructions to the Processor comply with Applicable Data Protection Laws
- Be responsible for the accuracy and quality of Personal Data provided to the Processor

---

### 3. Processing Instructions

#### 3.1 Instructions

The Processor shall process Personal Data only on documented instructions from the Controller, including with regard to transfers of Personal Data to a third country, unless required to do so by applicable law.

The Controller's instructions are as set forth in:
- The Agreement (including this DPA)
- The Controller's configuration and use of the Service
- Any additional written instructions agreed upon by the Parties

#### 3.2 Notification

If the Processor believes that an instruction from the Controller infringes Applicable Data Protection Laws, the Processor shall promptly notify the Controller and may suspend processing of the affected Personal Data until the Controller confirms or modifies its instructions.

---

### 4. Confidentiality

#### 4.1 Personnel

The Processor shall ensure that persons authorized to process Personal Data have committed to confidentiality or are under an appropriate statutory obligation of confidentiality.

#### 4.2 Access Limitations

Access to Personal Data is restricted to personnel who require access for the performance of the Service, on a need-to-know basis.

---

### 5. Security Measures

#### 5.1 Technical and Organizational Measures

The Processor shall implement and maintain appropriate technical and organizational measures to protect Personal Data against unauthorized or unlawful processing and against accidental loss, destruction, or damage. These measures are described in Annex 2 (Security Measures) and include:

- Encryption of Personal Data in transit (TLS 1.2+) and at rest (AES-256)
- PII tokenization before third-party AI model processing
- Access controls and authentication mechanisms
- Network security (virtual network isolation, network security groups, WAF)
- Secret management via Azure Key Vault with Managed Identity
- Regular security reviews and monitoring
- Incident detection and response procedures

#### 5.2 Updates

The Processor may update its security measures from time to time, provided that such updates do not materially decrease the overall level of protection.

---

### 6. Sub-processors

#### 6.1 Authorized Sub-processors

The Controller provides general authorization for the Processor to engage Sub-processors, subject to the conditions in this section. The current list of Sub-processors is set forth in Annex 3 (Sub-processors).

#### 6.2 Obligations

The Processor shall:

- Enter into a written agreement with each Sub-processor imposing data protection obligations no less protective than those in this DPA
- Remain fully liable for the acts and omissions of its Sub-processors

#### 6.3 Changes to Sub-processors

The Processor shall notify the Controller at least 30 days in advance of any intended addition or replacement of Sub-processors by:

- Email notification to the Controller's designated contact
- Update to the Sub-processor list on the Processor's website

#### 6.4 Objection

If the Controller reasonably objects to a new Sub-processor on data protection grounds, the Controller shall notify the Processor in writing within 14 days of receiving notice. The Parties shall work in good faith to resolve the objection. If no resolution is reached within 30 days, the Controller may terminate the affected portion of the Service without penalty.

---

### 7. Data Subject Rights

#### 7.1 Assistance

The Processor shall assist the Controller in responding to requests from Data Subjects exercising their rights under Applicable Data Protection Laws, including rights of access, rectification, erasure, restriction, portability, and objection.

#### 7.2 Notification

If the Processor receives a request directly from a Data Subject, the Processor shall promptly redirect the Data Subject to the Controller, unless otherwise agreed or required by law.

#### 7.3 Tools

The Processor provides the following tools to assist the Controller in fulfilling Data Subject requests:

- Data export functionality within the Service
- Data deletion functionality within the Service
- API endpoints for programmatic data management
- Support assistance via support@remakerdigital.com

---

### 8. Personal Data Breach

#### 8.1 Notification

The Processor shall notify the Controller of any Personal Data Breach without undue delay and in any event within 72 hours of becoming aware of the breach. The notification shall include:

- A description of the nature of the breach, including the categories and approximate number of Data Subjects and records affected
- The name and contact details of the Processor's point of contact
- A description of the likely consequences of the breach
- A description of the measures taken or proposed to address the breach

#### 8.2 Cooperation

The Processor shall cooperate with the Controller and take commercially reasonable steps to assist in the investigation, mitigation, and remediation of the breach.

#### 8.3 Records

The Processor shall maintain records of all Personal Data Breaches, including the facts, effects, and remedial actions taken.

---

### 9. Data Protection Impact Assessment

The Processor shall provide reasonable assistance to the Controller in conducting data protection impact assessments and prior consultations with supervisory authorities, to the extent required by Applicable Data Protection Laws and to the extent the Controller does not otherwise have access to the relevant information.

---

### 10. International Data Transfers

#### 10.1 Transfer Mechanisms

Where Personal Data is transferred from the EEA, UK, or Switzerland to the United States (where the Service is hosted), the transfer is governed by:

- Standard Contractual Clauses (SCCs) as set forth in Annex 4
- Any other valid transfer mechanism under Applicable Data Protection Laws

#### 10.2 Additional Safeguards

The Processor implements the following additional safeguards for international transfers:

- Encryption of data in transit and at rest
- Access controls limiting data access to authorized personnel
- PII tokenization before processing by AI models
- Regular review of government access requests (to date: none received)

#### 10.3 Disclosure Requests

If the Processor receives a request from a government authority for access to Personal Data, the Processor shall:

- Notify the Controller promptly (unless prohibited by law)
- Challenge the request where there are reasonable grounds to consider it unlawful
- Disclose the minimum amount of data required

---

### 11. Audit

#### 11.1 Right to Audit

The Controller has the right to audit the Processor's compliance with this DPA. Audits may be conducted:

- By the Controller or an independent third-party auditor appointed by the Controller
- No more than once per year, unless a Personal Data Breach has occurred or a supervisory authority requires an audit
- Upon at least 30 days' written notice

#### 11.2 Cooperation

The Processor shall make available all information necessary to demonstrate compliance with this DPA and shall cooperate with audits.

#### 11.3 Certifications and Reports

In lieu of an on-site audit, the Processor may provide:

- SOC 2 Type II reports (when available)
- Penetration test summaries
- Security questionnaire responses
- Documentation of security measures and controls

---

### 12. Return and Deletion of Data

#### 12.1 During the Agreement

The Controller may request export of its Personal Data at any time during the Agreement through the Service or by contacting support@remakerdigital.com.

#### 12.2 Upon Termination

Upon termination of the Agreement:

- The Processor shall make Personal Data available for export for 30 days
- After 30 days, the Processor shall delete all Personal Data, including copies, unless retention is required by applicable law
- Backup copies shall be purged within 90 days of deletion
- The Processor shall certify deletion upon the Controller's request

---

### 13. Term and Termination

This DPA shall remain in effect for the duration of the Agreement. Sections that by their nature should survive termination shall survive, including sections related to confidentiality, data deletion, and audit rights.

---

### 14. Liability

Each Party's liability under this DPA shall be subject to the limitations of liability set forth in the Agreement.

---

### 15. Conflict

In the event of any conflict between this DPA and the Agreement, this DPA shall prevail with respect to the processing of Personal Data.

---

### 16. Contact

For DPA-related inquiries:

**VanDusen & Palmeter, LLC (DBA Remaker Digital)**
Data Protection Contact: dpo@remakerdigital.com
General: legal@remakerdigital.com

---

## Annex 1: Details of Processing

| Element | Description |
|---------|-------------|
| **Subject Matter** | Processing of Personal Data to provide the Agent Red Customer Engagement platform |
| **Duration** | For the term of the Agreement |
| **Nature and Purpose** | AI-powered customer engagement: receiving customer inquiries, processing them through AI models, generating responses, managing escalations, providing analytics |
| **Categories of Data Subjects** | Customer's employees (Account users); Customer's end users (individuals submitting inquiries) |
| **Categories of Personal Data** | Names, email addresses, support inquiry content, order information, product preferences, IP addresses, device information, conversation history |
| **Sensitive Data** | None intentionally processed. Customers must not submit sensitive/special category data unless they have implemented appropriate safeguards. |

---

## Annex 2: Security Measures

| Category | Measures |
|----------|----------|
| **Encryption** | TLS 1.2+ in transit; AES-256 at rest (Azure-managed keys) |
| **Access Control** | Role-based access control (RBAC); Azure Managed Identity; principle of least privilege |
| **Network Security** | Azure Virtual Network isolation; Network Security Groups; Application Gateway with WAF |
| **Secret Management** | Azure Key Vault with Managed Identity access |
| **PII Protection** | PII tokenization (UUID-based tokens) before third-party AI processing |
| **Monitoring** | Application Insights; OpenTelemetry; security event logging |
| **Data Isolation** | Logical tenant isolation in Cosmos DB |
| **Backup** | Daily automated backups; 30-day retention; point-in-time restore |
| **Incident Response** | Documented incident response procedures; 72-hour breach notification |
| **Personnel** | Confidentiality obligations; access on need-to-know basis |

---

## Annex 3: Sub-processors

| Sub-processor | Purpose | Data Processed | Location |
|---------------|---------|---------------|----------|
| Microsoft Azure | Cloud infrastructure (compute, storage, networking) | All Customer Data (encrypted) | United States (East US 2) |
| Microsoft Azure OpenAI Service | AI language model processing | PII-tokenized inquiry content only | United States |
| Payment Processor (TBD) | Payment processing | Billing information only | United States |
| Google Analytics | Website analytics | Anonymized browsing data | United States |

---

## Annex 4: Standard Contractual Clauses

For transfers of Personal Data from the EEA to the United States, the Parties agree to the Standard Contractual Clauses adopted by the European Commission in Decision 2021/914 (Module Two: Controller to Processor), which are incorporated by reference.

The following selections apply:

| Clause | Selection |
|--------|-----------|
| **Clause 7** (Docking clause) | Included |
| **Clause 9** (Sub-processors) | Option 2: General written authorization with 30-day notice |
| **Clause 11** (Redress) | Optional language not included |
| **Clause 13** (Supervision) | Competent supervisory authority per Clause 13(a) |
| **Clause 17** (Governing law) | Option 1: Law of an EU Member State (Ireland) |
| **Clause 18** (Forum) | Courts of Ireland |

For transfers from the UK, the International Data Transfer Addendum to the EU SCCs (issued by the UK Information Commissioner) is incorporated by reference.

For transfers from Switzerland, the SCCs apply with the modifications required by the Swiss Federal Data Protection Act.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

> **IMPORTANT NOTICE:** This document is an AI-generated draft provided for internal planning purposes only. It is NOT legal advice. This document must be reviewed and approved by qualified legal counsel before publication or use. Do not rely on this draft as a binding legal document. In particular, the Standard Contractual Clauses referenced in Annex 4 require careful legal review to ensure correct implementation.
