# Sydeco Contract Risk Analyzer (CRA) / Legal Doc Verifier (LDV)
## Privacy Policy & Data Protection Declaration

**Effective Date:** July 24, 2026  
**Version:** 1.0  
**Compliance Standards:** Indonesian Personal Data Protection Law (UU PDP No. 27/2022) & GDPR Principles  

---

### 1. Introduction

Sydeco ("We", "Us", or "Our") is committed to safeguarding the privacy and security of personal data and confidential document content processed through the Sydeco Contract Risk Analyzer (CRA) / Legal Doc Verifier (LDV) platform. This Privacy Policy details our technical data protection practices, encryption standards, retention policies, and compliance with **Indonesian Law No. 27 of 2022 concerning Personal Data Protection (UU PDP)** and global data protection standards (GDPR).

---

### 2. Principles of Data Processing

We process personal data and document text in accordance with the following core principles:
1. **Lawfulness, Fairness, and Transparency:** Processing is conducted pursuant to user consent and legitimate contractual processing obligations.
2. **Purpose Limitation:** Data is collected solely to perform automated contract risk analysis, clause extraction, and compliance reporting requested by the user.
3. **Data Minimization:** Only text and metadata necessary for contract risk evaluation are extracted and processed.
4. **Accuracy & Confidentiality:** Data is kept secure and protected against unauthorized access, loss, or leak.

---

### 3. Key Guarantees & Technical Safeguards

#### 3.1. Strict Non-Training Guarantee for AI/LLM Models
- **No Public LLM Training:** All uploaded contract files, extracted text snippets, and JSON analysis results are **STRICTLY CONFIDENTIAL**.
- **No Model Fine-tuning:** Customer documents are **NEVER** used to train, re-train, fine-tune, or update public LLMs, open-source models (such as DistilBERT or Qwen), or any third-party AI repositories.
- **Airgapped / Local Processing:** In production mode (`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`), all model inferences (L1-L4) execute 100% locally on sovereign infrastructure without outbound network connections.

#### 3.2. Data Encryption At-Rest & In-Transit
- **At-Rest Encryption:** Document binary payload, extracted contract text, and JSON analysis output tables are encrypted on-disk using **Fernet (AES-128 symmetric key encryption in CBC mode with PKCS7 padding and HMAC-SHA256 authentication)** managed by `crypto.py`.
- **Key Isolation & Rotation:** Encryption keys (`LDV_ENCRYPTION_KEY`) are managed separately from database storage, with support for zero-downtime key rotation (`MultiFernet`).
- **In-Transit Protection:** All web traffic and API endpoints require HTTPS/TLS 1.2 or TLS 1.3 with HSTS headers.

#### 3.3. Document Retention & Purge Policy
- **Default Retention Window:** Uploaded documents and analysis results are assigned a default retention lifecycle of **30 days** (or customized per-organization via `LDV_RETENTION_DAYS` / `organizations.retention_days`).
- **Automated Retention Purge:** Nightly automated cron jobs execute `manage.py purge` to permanently delete expired document bytes, extracted text, and DB records.
- **On-Demand Deletion:** Users may issue a `DELETE /api/v1/result/<uuid>` API call to immediately hard-delete a document payload and its associated analysis results.

---

### 4. Data Subject Rights (UU PDP & GDPR)

Under Indonesian Law No. 27 of 2022 (UU PDP) and GDPR, Data Subjects possess the following rights:
- **Right to Access & Information:** Right to view stored document metadata, analysis logs, and active session tokens.
- **Right to Erasure (Right to be Forgotten):** Right to trigger immediate manual purge of uploaded contracts and historical analysis results.
- **Right to Data Portability:** Right to export analysis results in standardized JSON format via authenticated API endpoints (`/api/v1/result/<uuid>`).
- **Right to Consent Revocation:** Right to withdraw consent to processing via user account management settings.

---

### 5. Multi-Tenant Isolation & Audit Logging

- **Tenant Isolation:** Access to analysis records is strictly scoped to the uploading user's organization (`org_id`). Cross-tenant access is blocked at the database and API layer (returning HTTP 403 Forbidden).
- **Audit Trails:** Security actions (login, logout, file upload, document deletion, citation verification, rate limiting) are recorded in an immutable `audit_log` SQLite table (`database.write_audit()`).

---

### 6. Security Incident Response & Contact

For privacy requests, data subject right exercises, or security vulnerability notifications, please contact:
- **Data Protection Officer (DPO):** `dpo@sydeco.internal`
- **Security & Compliance Team:** `security@sydeco.internal`
