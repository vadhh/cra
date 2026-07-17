(function () {
  "use strict";
  const STORAGE_KEY = "ldv_lang";
  const DEFAULT_LANG = "en";
  const SUPPORTED = ["en", "id"];

  // Every later task appends its page's keys here (both en and id).
  const DICT = {
    en: {
      "nav.new_analysis": "New Analysis",
      "nav.dashboard": "Dashboard",
      "nav.citation_library": "Citation Library",
      "nav.secure_logout": "Secure Logout",
      "nav.sign_in": "Sign In",
      "brand.name": "Sydeco CRA",

      // index.html — MFA warning banner
      "index.mfa_warning.title": "Security Notice:",
      "index.mfa_warning.body": "Multi-Factor Authentication (MFA) is not enabled on your account.",
      "index.mfa_warning.link": "Activate it in your security settings",
      "index.mfa_warning.suffix": "to secure institutional assets.",

      // index.html — stepper
      "index.stepper.step1_label": "1. Ingestion",
      "index.stepper.step2_label": "2. Details",
      "index.stepper.step3_label": "3. Options",
      "index.stepper.step4_label": "4. Review",

      // index.html — Step 1: Ingestion
      "index.step1.title": "Document Ingestion",
      "index.step1.subtitle": "Choose a contract asset to queue into the sovereign parsing pipeline.",
      "index.step1.dropzone_title": "Drag and drop legal assets here",
      "index.step1.dropzone_subtitle": "or click to browse local secure storage",
      "index.step1.select_file_button": "SELECT FILE",
      "index.step1.confirm_continue": "CONFIRM & CONTINUE",
      "index.step1.clear_button": "Clear",

      // index.html — Step 2: Document Details
      "index.step2.title": "Document context",
      "index.step2.subtitle": "Calibrate context metrics to ensure correct rule sets apply.",
      "index.step2.display_name_label": "Display Name",
      "index.step2.display_name_placeholder": "Document Name",
      "index.step2.contract_type_label": "Contract Type Context",
      "index.step2.contract_type_auto": "Auto-Detect via NLI Classifier (Recommended)",
      "index.step2.contract_type_service": "Service Agreement",
      "index.step2.contract_type_nda": "Non-Disclosure Agreement (NDA)",
      "index.step2.contract_type_employment": "Employment Contract",
      "index.step2.contract_type_software": "Software License",
      "index.step2.contract_type_generic": "Other / Generic Contract",
      "index.step2.jurisdiction_label": "Jurisdiction Context",
      "index.step2.jurisdiction_auto": "Auto-Detect Governed Juris (Recommended)",
      "index.step2.jurisdiction_fr": "France (FR)",
      "index.step2.jurisdiction_be": "Belgium (BE)",
      "index.step2.jurisdiction_id": "Indonesia (ID)",
      "index.step2.jurisdiction_nl": "Netherlands (NL)",
      "index.step2.jurisdiction_enw": "England & Wales (EN&W)",
      "index.step2.jurisdiction_us": "United States (US)",
      "index.step2.jurisdiction_generic": "Generic / International",
      "index.step2.language_label": "Language Context",
      "index.step2.language_auto": "Auto-Detect Language (Recommended)",
      "index.step2.language_en": "English (EN)",
      "index.step2.language_fr": "French (FR)",
      "index.step2.language_id": "Indonesian (ID)",
      "index.step2.language_nl": "Dutch (NL)",
      "index.step2.client_ref_label": "Client Reference",
      "index.step2.optional_suffix": "(Optional)",
      "index.step2.client_ref_placeholder": "e.g. Acme Corp",
      "index.step2.case_folder_label": "Case Folder / Project",
      "index.step2.case_folder_placeholder": "e.g. Q3 NDAs",
      "index.step2.back_button": "Back to Ingestion",
      "index.step2.proceed_button": "PROCEED TO OPTIONS",

      // index.html — Step 3: Analysis Options
      "index.step3.title": "Analysis configuration",
      "index.step3.subtitle": "Customize package depth, scope, and validation parameters.",
      "index.step3.depth_label": "Analysis Scope Depth",
      "index.step3.standard_title": "Standard Analysis",
      "index.step3.standard_desc": "L1 Rule Checks + L2 DistilBERT Classifier + L3 Scorer. Quick completion (typically 2-10s).",
      "index.step3.comprehensive_title": "Comprehensive Analysis",
      "index.step3.comprehensive_desc": "Includes L4 Qwen LLM Explanations & commentary loops. High system load (takes several minutes).",
      "index.step3.policy_version_label": "Scoring Policy Version",
      "index.step3.policy_default": "default_v1 (June 2026 calibrated baseline)",
      "index.step3.policy_sandbox": "sandbox_beta (experimental rules)",
      "index.step3.reviewer_label": "Default Reviewer",
      "index.step3.reviewer_auto": "Auto-Assign (Based on availability)",
      "index.step3.reviewer_lead": "Lead Analyst Team",
      "index.step3.reviewer_senior": "Senior Corporate Reviewer",
      "index.step3.back_button": "Back to Details",
      "index.step3.proceed_button": "PROCEED TO CONFIRMATION",

      // index.html — Step 4: Review and Confirmation
      "index.step4.title": "Sovereign Compliance Review",
      "index.step4.subtitle": "Acknowledge storage retention and execute the local analysis pipeline.",
      "index.step4.summary_title": "Analysis Spec Summary",
      "index.step4.file_asset_label": "File Asset:",
      "index.step4.display_identity_label": "Display Identity:",
      "index.step4.contract_profile_label": "Contract Profile:",
      "index.step4.target_jurisdiction_label": "Target Jurisdiction:",
      "index.step4.language_mode_label": "Language Mode:",
      "index.step4.analysis_depth_label": "Analysis Depth:",
      "index.step4.encryption_title": "AES-256 Storage Encryption",
      "index.step4.encryption_desc": "The encryption node is operational. File text outputs and pipeline results are encrypted at rest with keys held strictly in localized server memory.",
      "index.step4.purge_title": "30-Day Auto-Purge Policy",
      "index.step4.purge_desc": "This analysis session is assigned a hard retention schedule. The document, text extracts, and reports will be deleted in 30 days.",
      "index.step4.consent_label": "I confirm that I possess corporate authorization and security clearance to upload this asset to the PT SYDECO LightML pipeline. I consent to automatic processing and transient text extraction.",
      "index.step4.back_button": "Back to Options",
      "index.step4.initiate_button": "INITIATE PIPELINE ANALYSIS",

      // index.html — Step 5: Processing Dashboard
      "index.step5.description": "Your document is executing locally inside the secure partition. This process runs synchronously.",
      "index.step5.elapsed_time_label": "Elapsed Time:",
      "index.step5.seconds_suffix": "seconds",
      "index.step5.overall_progress_label": "Overall Progress",
      "index.step5.stage_uploading_label": "1. Document Ingestion",
      "index.step5.stage_extracting_label": "2. Structural Parsing & Text Extraction",
      "index.step5.stage_classifying_label": "3. Language, Juris, & Type Classification",
      "index.step5.stage_analyzing_label": "4. Mandatory & Risky Clause Screening",
      "index.step5.stage_scoring_label": "5. Risk Matrix Scoring",
      "index.step5.stage_reasoning_label": "6. AI Reasoning & Explanation (LLM)",
      "index.step5.notice_title": "Notice:",
      "index.step5.notice_body": "High-volume files or NLI/LLM reasoning blocks require processing time. You can safely close or navigate away from this screen; the analysis runs securely in the background.",
      "index.step5.cancel_button": "Cancel Analysis",
      "index.step5.retry_button": "Retry Analysis",
      "index.step5.background_button": "Run in Background",

      // index.html — Telemetry sidebar
      "index.sidebar.title": "Pipeline Telemetry",
      "index.sidebar.step1_formats_title": "Supported formats",
      "index.sidebar.step1_formats_desc": "Ingests standard structured TXT, raw DOCX binaries, and clean text-based PDFs (up to 10 MB in size).",
      "index.sidebar.step1_sovereignty_title": "Sovereignty Notice",
      "index.sidebar.step1_sovereignty_desc": "All extraction algorithms and classification scripts run locally. Your documents do not traverse external servers.",
      "index.sidebar.step2_context_title": "Why Context Matters",
      "index.sidebar.step2_context_desc": "Correct jurisdiction filters apply relevant local legal codes (e.g. Code civil articles in France). Contract categories assign custom mandatory clause lists to identify omissions accurately.",
      "index.sidebar.step2_fallback_title": "Auto-Detection Fallback",
      "index.sidebar.step2_fallback_desc": "If set to auto, the pipeline scans headings and governing clauses to identify parameters during Step 3 processing.",
      "index.sidebar.step3_latency_title": "L4 LLM Layer Latency",
      "index.sidebar.step3_latency_desc": "Selecting Comprehensive mode engages local Qwen Transformers to output rationale explanations. This requires extensive local GPU/CPU cycles.",
      "index.sidebar.step3_routing_title": "Review Routing",
      "index.sidebar.step3_routing_desc": "Directing findings to specific analysts expedites reporting validation times inside the case queue.",
      "index.sidebar.step4_audit_title": "Audit Trail Compliance",
      "index.sidebar.step4_audit_desc": "Under sovereign directives, this upload action is logged as a secure audit event containing user credentials, IP address, and hash sums.",
      "index.sidebar.step4_retention_title": "Retention Lock",
      "index.sidebar.step4_retention_desc": "Purges cannot be delayed. Once the 30-day window expires, files are scrubbed in compliance with corporate privacy standards.",
      "index.sidebar.node_label": "Local Processing Node",
      "index.sidebar.node_online": "Online",
      "index.sidebar.encryption_core_label": "Encryption Core",

      // index.html — Logged-out landing
      "index.landing.badge": "Enterprise Security Partition Active",
      "index.landing.hero_title_line1": "Sovereign Contract",
      "index.landing.hero_title_line2": "Risk Intelligence",
      "index.landing.hero_description": "Sydeco Contract Risk Analyzer (CRA) provides multi-layered deep legal analysis on agreement documents. Audits governing law, venue, missing provisions, and risky clauses locally using LightML—without data leaving your network.",
      "index.landing.authenticate_button": "Authenticate to Begin",
      "index.landing.view_docs_button": "View API Docs",
      "index.landing.pillar1_title": "100% Local Sovereignty",
      "index.landing.pillar1_desc": "Your documents never traverse external networks. Ingestion, OCR parsing, NLI classification, and LLM explanation tasks execute fully locally on isolated hardware cores.",
      "index.landing.pillar2_title": "LightML Layered Audit",
      "index.landing.pillar2_desc": "Leverages a 4-layer inspection pipeline: rule-based compliance, DistilBERT classification models, structured score validation policies, and localized Qwen summary commentary.",
      "index.landing.pillar3_title": "Integrated Citations",
      "index.landing.pillar3_desc": "Every identified risk is automatically linked to matching citations from the system legal library. Reviewers can cross-reference, audit, and approve findings inside the interactive editor.",
      "index.landing.readiness_node_label": "Security Node Node-01:",
      "index.landing.readiness_status": "Ready",
      "index.landing.readiness_distilbert": "DistilBERT Classifier Active",
      "index.landing.readiness_qwen": "Qwen-3 Engine Available",
      "index.landing.readiness_encryption": "AES-256 Storage Encrypted",

      // index.html — Footer
      "index.footer.copyright": "© 2026 PT SYDECO. Contract Risk Analyzer.",
      "index.footer.privacy": "Privacy",
      "index.footer.terms": "Terms",
      "index.footer.compliance": "Compliance",

      // result.html — Loading / Error / Processing states
      "result.loading.message": "Decrypting and loading assessment data…",
      "result.error.title": "Assessment Error",
      "result.error.retry_link": "← Run New Analysis",
      "result.processing.title": "Sovereign Pipeline Processing…",
      "result.processing.description": "Your document is executing inside the secure partition. This report will automatically load upon completion.",
      "result.processing.overall_progress": "Overall Progress",

      // result.html — Case header
      "result.case_header.new_scan_button": "+ New Scan",

      // result.html — Risk score hero panel
      "result.risk.score_label": "Risk Score",
      "result.risk.confidence_label": "Pipeline Confidence:",
      "result.risk.confidence_footnote": "Calibrated against doc type NLI classifier telemetry.",
      "result.risk.disclaimer": "Decision support only — not legal advice. Does not guarantee validity or enforceability.",

      // result.html — Next Actions card
      "result.next_actions.title": "Next Actions",
      "result.next_actions.current_assignee_label": "Current Assignee",
      "result.next_actions.assign_reviewer_button": "Assign Reviewer",
      "result.next_actions.compare_versions_label": "Compare Versions",
      "result.next_actions.no_previous_versions": "No previous versions",

      // result.html — Professional Review card
      "result.professional_review.title": "Professional Review",
      "result.professional_review.status_label": "Status",
      "result.professional_review.reviewer_label": "Reviewer",
      "result.professional_review.review_date_label": "Review Date",
      "result.professional_review.comments_label": "Comments",
      "result.professional_review.review_status_select_label": "Review Status",
      "result.professional_review.status_unreviewed": "Unreviewed",
      "result.professional_review.status_confirmed": "Confirmed (Verified Correct)",
      "result.professional_review.status_edited": "Edited (Adjusted/Corrected)",
      "result.professional_review.status_rejected": "Rejected (Flawed Analysis)",
      "result.professional_review.status_escalated": "Escalated (Higher-level Review Needed)",
      "result.professional_review.review_comments_label": "Review Comments",
      "result.professional_review.comment_placeholder": "Add legal assessment notes, overrides, or instructions...",
      "result.professional_review.submit_button": "Submit Review",
      "result.professional_review.not_reviewed_notice": "This assessment has not been reviewed by a qualified lawyer.",

      // result.html — Priority Actions section
      "result.priority_actions.title": "Priority Actions",
      "result.priority_actions.empty": "No priority actions — no actionable findings detected.",

      // result.html — Detected Findings & Anomalies section
      "result.findings.title": "Detected Findings & Anomalies",
      "result.findings.search_placeholder": "Search evidence or categories…",
      "result.findings.severity_all": "All Severities",
      "result.findings.severity_critical": "Critical Severity",
      "result.findings.severity_high": "High Severity",
      "result.findings.severity_medium": "Medium Severity",
      "result.findings.severity_low": "Low Severity",
      "result.findings.category_all": "All Categories",
      "result.findings.category_unfair": "Unfair Clauses",
      "result.findings.category_ai_classifier": "AI Classifier Findings",
      "result.findings.category_missing_clause": "Missing Required Clauses",
      "result.findings.status_all": "All Statuses",
      "result.findings.status_unreviewed": "Unreviewed",
      "result.findings.status_confirmed": "Confirmed",
      "result.findings.status_rejected": "Rejected",
      "result.findings.why_matters_label": "Why This Matters:",
      "result.findings.suggested_replacement_label": "Suggested Replacement Clause:",
      "result.findings.verified_citations_label": "Verified Citations:",
      "result.findings.view_excerpt_button": "View Excerpt",
      "result.findings.confirm_button": "Confirm",
      "result.findings.reject_button": "Reject",
      "result.findings.edit_spec_button": "Edit Spec",
      "result.findings.empty_title": "No findings match the current filter matrix",
      "result.findings.empty_note": "Note: Automated screening is a decision support tool and may not detect all compliance violations. Obtain professional legal review before final signature.",

      // result.html — Mandatory Clause Checklist section
      "result.checklist.title": "Mandatory Clause Checklist",
      "result.checklist.required_badge": "REQUIRED",

      // result.html — AI Explanation section (Layer 4)
      "result.ai_explanation.title": "AI Explanation",
      "result.ai_explanation.summary_label": "SUMMARY",
      "result.ai_explanation.clause_commentary_label": "CLAUSE COMMENTARY",
      "result.ai_explanation.compliance_notes_label": "COMPLIANCE NOTES",
      "result.ai_explanation.recommendations_label": "RECOMMENDATIONS",

      // result.html — Extracted Agreement Text & Evidence Viewer section
      "result.evidence.title": "Extracted Agreement Text & Evidence Viewer",
      "result.evidence.note": "matched evidence phrases are highlighted in the document scroll panel below.",

      // result.html — Scoring Penalty Audit section
      "result.scoring.title": "Scoring Penalty Audit",

      // result.html — Analysis Limitations section
      "result.limitations.title": "Analysis Limitations",

      // result.html — Shared modal chrome
      "result.modal.cancel_button": "Cancel",

      // result.html — Edit Recommendation modal
      "result.edit_modal.title": "Edit Finding specification",
      "result.edit_modal.label": "Revision Recommendation Wording",
      "result.edit_modal.save_button": "Save Changes",

      // result.html — Reject Finding modal
      "result.reject_modal.title": "Reject Finding",
      "result.reject_modal.reason_label": "Reason for Rejection",
      "result.reject_modal.reason_placeholder": "e.g. False positive — clause is present in section 4.2",
      "result.reject_modal.confirm_button": "Reject Finding",

      // result.html — Assign Reviewer modal
      "result.assign_modal.title": "Assign Case Reviewer",
      "result.assign_modal.description": "Select an active reviewer to delegate legal verification.",
      "result.assign_modal.select_label": "Select Reviewer",
      "result.assign_modal.option_auto": "System Default / Auto-Assign",
      "result.assign_modal.option_lead": "Lead Analyst Team",
      "result.assign_modal.option_senior": "Senior Corporate Reviewer",
      "result.assign_modal.assign_button": "Assign Case",

      // result.html — Footer
      "result.footer.copyright": "© 2026 PT SYDECO — Contract Risk Analyzer",

      // login.html — Branding & login form (shared header)
      "login.brand.title": "Access Gate",
      "login.brand.subtitle": "Sovereign Intelligence Protocol",
      "login.form.title": "Secure Identity Verification",
      "login.form.subtitle": "Authorized personnel only.",
      "login.form.email_label": "Institutional Email",
      "login.form.email_placeholder": "name@sydeco.legal",
      "login.form.password_label": "Access Key",
      "login.form.forgot_password_link": "Forgot Password?",
      "login.form.org_label": "Organization Context",
      "login.form.optional_suffix": "(Optional)",
      "login.form.org_placeholder": "Default Organization",
      "login.form.remember_label": "Grant persistent session (24h)",
      "login.form.footer_security": "Connection secured via AES-256 Sovereign Protocol.",
      "login.form.footer_help": "Need assistance?",
      "login.form.footer_contact_admin": "Contact System Admin",

      // login.html — Shared chrome (reused across MFA/recovery states)
      "login.common.cancel_button": "Cancel",

      // login.html — MFA Verification Challenge
      "login.mfa_challenge.trust_label": "Trust this device for 30 days",
      "login.mfa_challenge.policy_title": "Trusted Device Policy:",
      "login.mfa_challenge.policy_body": "Do not select this option on shared or public terminals. Selecting this will bypass multi-factor enrollment checks on this browser session for the next 30 days.",

      // login.html — MFA Enrollment Setup
      "login.mfa_enroll.title": "MFA Enrollment Required",
      "login.mfa_enroll.subtitle": "Multi-Factor Authentication is mandatory for your corporate account security.",
      "login.mfa_enroll.step1_title": "1. Scan QR Code",
      "login.mfa_enroll.step1_desc": "Scan this QR code using Google Authenticator, Duo, or any TOTP application on your secure mobile device.",
      "login.mfa_enroll.manual_key_label": "Manual entry key:",
      "login.mfa_enroll.step2_title": "2. Secure Recovery Codes",
      "login.mfa_enroll.step2_desc": "These recovery keys allow access if you lose your authentication device. Store them in a secure physical vault.",
      "login.mfa_enroll.step3_title": "3. Verify TOTP Code",
      "login.mfa_enroll.step3_desc": "Enter the generated 6-digit code from your authenticator app to enable MFA and sign in.",
      "login.mfa_enroll.skip_button": "Skip for now",

      // login.html — Recover Access (Forgot Password)
      "login.forgot.title": "Recover Access coordinates",
      "login.forgot.subtitle": "Submit your institutional email to request a security key reset.",
      "login.forgot.email_label": "Institutional Email",
      "login.forgot.email_placeholder": "name@sydeco.legal",
      "login.forgot.policy_title": "Sovereign Policy Note:",
      "login.forgot.policy_body": "In compliance with secure corporate identity directives, password credentials cannot be self-reset. Submitting this form issues an audit event and alerts your organization's security administrator to release a temporary access token.",
      "login.forgot.success_title": "Access Request Initiated",
      "login.forgot.success_desc": "Coordination alert dispatched to your system security officers.",
      "login.forgot.success_contact": "Please contact your organization's designated administrator or internal IT Help Desk to authorize the credential release for",
      "login.forgot.return_button": "Return to Sign In",

      // login.html — Session Expired
      "login.session_expired.title": "Security Session Expired",
      "login.session_expired.subtitle": "Inactivity Limit Reached",
      "login.session_expired.description": "To protect proprietary legal assets and institutional configurations, your sovereign access session has been terminated. Any unsaved contract analysis progress has been safely wiped from the browser viewport.",
      "login.session_expired.reauth_button": "Re-Authenticate Portal",
      "login.session_expired.footer_note": "Secure Endpoint: PT SYDECO LightML Contract Risk Analyzer v1.0",

      // login.html — Footer
      "login.footer.copyright": "© 2026 PT SYDECO. Contract Risk Analyzer.",
      "login.footer.privacy": "Privacy Policy",
      "login.footer.terms": "Terms of Use",
      "login.footer.compliance": "Compliance",

      // account.html — Header
      "account.header.back_link": "Back to Sydeco CRA",
      "account.header.title": "Account & Security",

      // account.html — MFA status section
      "account.mfa.title": "Multi-Factor Authentication",
      "account.mfa.mandatory_note": "Mandatory for your organization or role.",
      "account.mfa.optional_note": "Optional — recommended for institutional accounts.",
      "account.mfa.enabled": "Enabled",
      "account.mfa.disabled": "Disabled",
      "account.mfa.enable_button": "Enable MFA",
      "account.mfa.disable_button": "Disable MFA",

      // account.html — Corporate Subscription & Usage section
      "account.usage.title": "Corporate Subscription & Usage",
      "account.usage.subtitle": "Real-time resource utilization for your tenant organization.",
      "account.usage.contracts_label": "Contracts Processed",
      "account.usage.pages_label": "Total Pages Extracted",
      "account.usage.reports_label": "Professional PDF Downloads",
      "account.usage.loading": "Loading subscription usage details…",

      // account.html — Shared chrome (reused across password/enroll states)
      "account.common.password_placeholder": "Password",
      "account.common.cancel_button": "Cancel",

      // account.html — Confirm Password (enable MFA) section
      "account.enable_password.title": "Confirm Password",
      "account.enable_password.subtitle": "Re-enter your password to begin MFA setup.",
      "account.enable_password.verifying": "Verifying…",
      "account.enable_password.continue_button": "Continue",

      // account.html — MFA Enrollment section
      "account.enroll.title": "Set Up MFA",
      "account.enroll.step1_title": "1. Scan QR Code",
      "account.enroll.step1_desc": "Scan with Google Authenticator, Duo, or any TOTP app.",
      "account.enroll.manual_key_label": "Manual entry key:",
      "account.enroll.step2_title": "2. Save Recovery Codes",
      "account.enroll.step2_desc": "Store these somewhere safe — they won't be shown again.",
      "account.enroll.step3_title": "3. Verify TOTP Code",
      "account.enroll.enabling": "Enabling…",

      // account.html — Disable MFA section
      "account.disable_password.title": "Disable MFA",
      "account.disable_password.subtitle": "Re-enter your password to confirm. This removes your authenticator enrollment and recovery codes.",
      "account.disable_password.disabling": "Disabling…",
      "account.disable_password.confirm_button": "Confirm Disable",

      // account.html — Error / success banners (hardcoded client-side copy only;
      // server-provided data.error text is displayed verbatim, untranslated)
      "account.errors.load_failed": "Failed to load account status.",
      "account.errors.mfa_setup_failed": "MFA setup failed.",
      "account.errors.mfa_setup_server_error": "Server error during MFA setup.",
      "account.errors.mfa_verify_failed": "Verification code failed.",
      "account.errors.mfa_verify_server_error": "Server error during MFA verification.",
      "account.errors.mfa_disable_failed": "Failed to disable MFA.",
      "account.errors.mfa_disable_server_error": "Server error while disabling MFA.",
      "account.success.mfa_enabled": "MFA enabled successfully.",
      "account.success.mfa_disabled": "MFA disabled.",

      // admin.html — Shared sidebar (byte-identical markup reused by citations.html — Task 7)
      "nav.sidebar.admin_portal": "Admin Portal",
      "nav.sidebar.core_operations": "Core Operations",
      "nav.sidebar.overview": "Overview",
      "nav.sidebar.case_history": "Case History",
      "nav.sidebar.management": "Management",
      "nav.sidebar.team_management": "Team Management",
      "nav.sidebar.organizations": "Organizations",
      "nav.sidebar.compliance_health": "Compliance & Health",
      "nav.sidebar.audit_logs": "Audit Logs",
      "nav.sidebar.system_health": "System Health",
      "nav.sidebar.account_security": "Account & Security",

      // admin.html — Top header chrome
      "admin.header.new_analysis_prefix": "+ New",
      "admin.header.new_analysis_suffix": " Analysis",

      // admin.html — Breadcrumb-only tab title (not part of the shared sidebar)
      "admin.tab_titles.citation_verification": "Citation Library Verification",

      // admin.html — Loading state
      "admin.loading.aggregating": "Aggregating system statistics…",

      // admin.html — Overview tab
      "admin.overview.title": "System Overview",
      "admin.overview.subtitle": "Monitor historical document assessments, risk ratings, and pipeline operations.",
      "admin.overview.stat_documents_label": "Stored Documents",
      "admin.overview.stat_documents_desc": "Retained active agreements",
      "admin.overview.stat_analyses_label": "Analyses Executed",
      "admin.overview.stat_analyses_desc": "Completed model jobs",
      "admin.overview.stat_risk_label": "Average Risk Index",
      "admin.overview.stat_risk_desc": "Combined L3 score metric",
      "admin.overview.stat_risky_label": "Risky Agreements",
      "admin.overview.stat_risky_desc": "Flagged HIGH or CRITICAL",
      "admin.overview.distribution_title": "Risk Class Distribution",
      "admin.overview.recent_title": "Recent Risk Reports",
      "admin.overview.col_ref_id": "Ref ID",
      "admin.overview.col_filename": "Filename",
      "admin.overview.col_type": "Type",
      "admin.overview.col_jurisdiction": "Jurisdiction",
      "admin.overview.col_score": "Score",
      "admin.overview.col_risk_rating": "Risk Rating",
      "admin.overview.col_analyzed": "Analyzed",
      "admin.overview.empty_reports": "No legal reports processed in history.",

      // admin.html — Case History tab
      "admin.history.title": "Case History",
      "admin.history.subtitle": "Search, filter, and organize historical contract risk reports.",
      "admin.history.filter_title": "Filter Documents",
      "admin.history.search_label": "General Search",
      "admin.history.search_placeholder": "Filename, error...",
      "admin.history.client_label": "Client Name",
      "admin.history.client_placeholder": "e.g. Acme Corp",
      "admin.history.folder_label": "Case / Folder",
      "admin.history.folder_placeholder": "e.g. Q3 NDA",
      "admin.history.doc_type_label": "Document Type",
      "admin.history.type_all": "All Types",
      "admin.history.type_nda": "Non-Disclosure Agreement",
      "admin.history.type_employment": "Employment Contract",
      "admin.history.type_service": "Service Agreement",
      "admin.history.type_software": "Software Licensing",
      "admin.history.type_generic": "Generic/Other",
      "admin.history.status_label": "Job Status",
      "admin.history.status_all": "All Statuses",
      "admin.history.status_completed": "Completed",
      "admin.history.status_processing": "Processing",
      "admin.history.status_queued": "Queued",
      "admin.history.status_failed": "Failed",
      "admin.history.min_score_label": "Min Score",
      "admin.history.max_score_label": "Max Score",
      "admin.history.clear_button": "Clear Filters",
      "admin.history.search_button": "Search",
      "admin.history.col_ref_id": "Ref ID",
      "admin.history.col_filename": "Filename",
      "admin.history.col_client": "Client",
      "admin.history.col_folder": "Folder/Case",
      "admin.history.col_score": "Score",
      "admin.history.col_status": "Status",
      "admin.history.col_reviewed": "Reviewed",
      "admin.history.col_analyzed": "Analyzed",
      "admin.history.empty": "No historical analyses match your query.",
      "admin.history.prev_page": "Previous Page",
      "admin.history.next_page": "Next Page",

      // admin.html — Team Management tab
      "admin.team.title": "Team Management",
      "admin.team.subtitle": "Provision users, assign organizational access roles, and audit security credentials.",
      "admin.team.create_button": "Create User",
      "admin.team.col_id": "ID",
      "admin.team.col_email": "Email / Identity",
      "admin.team.col_role": "Role",
      "admin.team.col_org_id": "Org ID",
      "admin.team.col_mfa_setup": "MFA Setup",
      "admin.team.col_downloads": "Downloads",
      "admin.team.col_status": "Status",
      "admin.team.col_actions": "Actions",
      "admin.team.role_analyst": "Analyst",
      "admin.team.role_reviewer": "Reviewer",
      "admin.team.role_manager": "Manager",
      "admin.team.role_viewer": "Viewer",
      "admin.team.role_admin": "Administrator",
      "admin.team.mfa_active": "Active",
      "admin.team.mfa_unset": "Unset",
      "admin.team.download_enabled": "Enabled",
      "admin.team.download_disabled": "Disabled",
      "admin.team.status_active": "Active",
      "admin.team.status_suspended": "Suspended",
      "admin.team.reset_mfa_button": "Reset MFA",
      "admin.team.revoke_session_button": "Revoke Session",
      "admin.team.suspend_button": "Suspend",
      "admin.team.activate_button": "Activate",

      // admin.html — Organizations tab
      "admin.orgs.title": "Organizations",
      "admin.orgs.subtitle": "Provision corporate tenants, check storage retention rules, and define scan limitations.",
      "admin.orgs.create_button": "Create Org",
      "admin.orgs.col_org_id": "Org ID",
      "admin.orgs.col_name": "Corporate Tenant Name",
      "admin.orgs.col_retention": "Data Retention Policy",
      "admin.orgs.col_mfa_enforcement": "MFA Enforcement",
      "admin.orgs.col_scan_limits": "Monthly Scan Limits",
      "admin.orgs.col_status": "Status",
      "admin.orgs.col_save": "Save Configurations",
      "admin.orgs.retention_7": "7-Day Ephemeral Purge",
      "admin.orgs.retention_15": "15-Day Auto-Purge",
      "admin.orgs.retention_30": "30-Day Storage Lock",
      "admin.orgs.retention_90": "90-Day Standard Log",
      "admin.orgs.mfa_enforced": "Enforced",
      "admin.orgs.mfa_optional": "Optional",
      "admin.orgs.scan_50": "50 scans / mo",
      "admin.orgs.scan_100": "100 scans / mo",
      "admin.orgs.scan_500": "500 scans / mo",
      "admin.orgs.scan_unlimited": "Unlimited Scans",
      "admin.orgs.status_active": "Active",
      "admin.orgs.update_button": "Update Policy",

      // admin.html — Citation Library tab
      "admin.citations.title": "Citation Library workspace",
      "admin.citations.subtitle": "Review, verify, reject, or supersede draft legal source citations mapped by standard rules.",
      "admin.citations.pending_title": "Pending Draft Citations",
      "admin.citations.col_finding_id": "Finding ID",
      "admin.citations.col_jurisdiction": "Jurisdiction",
      "admin.citations.col_article_ref": "Article Reference",
      "admin.citations.col_source_desc": "Legal Source Description",
      "admin.citations.col_verifier_note": "Verifier Note",
      "admin.citations.col_status": "Status",
      "admin.citations.col_decision": "Decision Workspace",
      "admin.citations.verify_button": "Verify",
      "admin.citations.reject_button": "Reject",
      "admin.citations.supersede_button": "Supersede",
      "admin.citations.history_button": "History",
      "admin.citations.empty_draft": "No draft citations pending verification.",
      "admin.citations.verified_title": "Verified Citation Index",
      "admin.citations.col_article": "Article",
      "admin.citations.col_legal_code_ref": "Legal Code Reference",
      "admin.citations.status_verified": "Verified",

      // admin.html — Audit Logs tab
      "admin.audits.title": "System Audit Log",
      "admin.audits.subtitle": "Filter, search, and export security event records for local institutional auditing.",
      "admin.audits.export_button": "Export Log (CSV)",
      "admin.audits.search_placeholder": "Search logs by action or details…",
      "admin.audits.action_all": "All Actions",
      "admin.audits.reset_button": "Reset",
      "admin.audits.col_timestamp": "Timestamp",
      "admin.audits.col_action": "Action",
      "admin.audits.col_operator_id": "Operator ID",
      "admin.audits.col_org_id": "Org ID",
      "admin.audits.col_resource_target": "Resource Target",
      "admin.audits.col_ip": "IP Address",
      "admin.audits.col_detail": "Detail Summary",
      "admin.audits.empty": "No matching audit events logged.",

      // admin.html — System Health tab
      "admin.status.title": "System Health status",
      "admin.status.subtitle": "Monitor local encryption cores, rate limit configs, backup schedules, and active ML models.",
      "admin.status.overview_title": "Status overview",
      "admin.status.sovereign_health_label": "Sovereign health:",
      "admin.status.database_label": "Localized Database:",
      "admin.status.datasets_label": "Datasets verification:",
      "admin.status.encryption_title": "Encryption Core",
      "admin.status.aes_label": "AES-256 state:",
      "admin.status.aes_configured": "Configured",
      "admin.status.aes_not_configured": "Warning: Not Configured",
      "admin.status.storage_node_label": "Storage Encryption Node:",
      "admin.status.storage_node_value": "PT SYDECO Sovereign Memory Module",
      "admin.status.models_title": "Active PyTorch Models",
      "admin.status.l2_label": "L2 DistilBERT Classifier:",
      "admin.status.l2_ready": "Ready (Cached)",
      "admin.status.l2_unavailable": "Unavailable",
      "admin.status.l4_label": "L4 Qwen Reasoning:",
      "admin.status.l4_available": "Available",
      "admin.status.l4_disabled": "Disabled (Lite)",
      "admin.status.mlp_label": "Sydeco MLP Network:",
      "admin.status.mlp_online": "Online",
      "admin.status.mlp_offline": "Offline",
      "admin.status.limits_title": "Limits & Backups",
      "admin.status.rate_limiter_label": "API Rate Limiter:",
      "admin.status.rate_limiter_value": "Active (Max 20 req/min)",
      "admin.status.last_backup_label": "Last System Backup:",
      "admin.status.backup_sync_label": "Backup Node Sync:",
      "admin.status.backup_sync_value": "Synced",

      // admin.html — Create User modal
      "admin.modals.create_user.title": "Create User Account",
      "admin.modals.create_user.subtitle": "Configure credentials, roles, and corporate tenant associations.",
      "admin.modals.create_user.email_label": "Email Identity",
      "admin.modals.create_user.email_placeholder": "user@company.com",
      "admin.modals.create_user.password_label": "Secure password",
      "admin.modals.create_user.password_placeholder": "••••••••",
      "admin.modals.create_user.role_label": "Assign Role",
      "admin.modals.create_user.org_id_label": "Corporate Organization ID",
      "admin.modals.create_user.org_id_placeholder": "1",
      "admin.modals.create_user.cancel_button": "Cancel",
      "admin.modals.create_user.submit_button": "Create User",

      // admin.html — Create Org modal
      "admin.modals.create_org.title": "Create Corporate Tenant",
      "admin.modals.create_org.subtitle": "Register a new sovereign corporate organization domain.",
      "admin.modals.create_org.name_label": "Corporate Tenant Name",
      "admin.modals.create_org.name_placeholder": "Company Name Inc.",
      "admin.modals.create_org.cancel_button": "Cancel",
      "admin.modals.create_org.submit_button": "Create Tenant",

      // admin.html — Citation History modal
      "admin.modals.citation_history.title": "Citation Revision History",
      "admin.modals.citation_history.status_verified": "Status: verified",
      "admin.modals.citation_history.verified_note": "Transitioned to verified baseline by System Administrator.",
      "admin.modals.citation_history.status_draft": "Status: draft",
      "admin.modals.citation_history.draft_note": "Draft provision parsed via machine extraction.",
      "admin.modals.citation_history.close_button": "Close History",

      // citations.html — Page header
      "citations.header.title_prefix": "Legal Authority",
      "citations.header.title_suffix": "Verification",
      "citations.header.subtitle": "A secure protocol for reviewing, verifying, and versioning legal citations within the sovereign intelligence architecture.",

      // citations.html — Tabs
      "citations.tabs.queue": "Queue & Verification",
      "citations.tabs.history": "History & Versioning",

      // citations.html — Stats grid
      "citations.stats.total_verified": "Total Verified",
      "citations.stats.awaiting_review": "Awaiting Review",
      "citations.stats.superseded": "Superseded",
      "citations.stats.integrity_score": "Integrity Score",

      // citations.html — Filters
      "citations.filters.search_label": "Search Findings",
      "citations.filters.search_placeholder": "Search by ID, article or source…",
      "citations.filters.jurisdiction_label": "Jurisdiction",
      "citations.filters.jurisdiction_all": "All Jurisdictions",
      "citations.filters.jurisdiction_id": "Indonesia (ID)",
      "citations.filters.jurisdiction_be": "Belgium (BE)",
      "citations.filters.jurisdiction_fr": "France (FR)",
      "citations.filters.jurisdiction_nl": "Netherlands (NL)",
      "citations.filters.jurisdiction_enw": "England & Wales (EN&W)",
      "citations.filters.jurisdiction_us": "United States (US)",
      "citations.filters.jurisdiction_generic": "Generic (Cross-Border)",
      "citations.filters.status_label": "Status",
      "citations.filters.status_all": "All Statuses",
      "citations.filters.status_draft_only": "Drafts Only",
      "citations.filters.status_verified_only": "Verified Only",

      // citations.html — Main queue table
      "citations.table.col_finding_id": "Finding ID",
      "citations.table.col_jurisdiction": "Jurisdiction",
      "citations.table.col_proposed_article": "Proposed Article",
      "citations.table.col_legal_source": "Legal Source",
      "citations.table.col_notes": "Notes",
      "citations.table.col_status": "Status",
      "citations.table.col_action": "Action",
      "citations.table.empty": "No matching citations found.",
      "citations.table.verify_button": "Verify",
      "citations.table.ready_label": "Ready",

      // citations.html — History & Versioning tab
      "citations.history.timeline_title": "Authority Versioning Timeline",
      "citations.history.verified_by_label": "Verified By",

      // citations.html — Loading state
      "citations.loading.message": "Loading citation database…",
    },
    id: {
      "nav.new_analysis": "Analisis Baru",
      "nav.dashboard": "Dasbor",
      "nav.citation_library": "Pustaka Sitasi",
      "nav.secure_logout": "Keluar Aman",
      "nav.sign_in": "Masuk",
      "brand.name": "Sydeco CRA",

      // index.html — MFA warning banner
      "index.mfa_warning.title": "Pemberitahuan Keamanan:",
      "index.mfa_warning.body": "Autentikasi Multi-Faktor (MFA) belum diaktifkan pada akun Anda.",
      "index.mfa_warning.link": "Aktifkan di pengaturan keamanan Anda",
      "index.mfa_warning.suffix": "untuk mengamankan aset institusional.",

      // index.html — stepper
      "index.stepper.step1_label": "1. Pengunggahan",
      "index.stepper.step2_label": "2. Detail",
      "index.stepper.step3_label": "3. Opsi",
      "index.stepper.step4_label": "4. Tinjauan",

      // index.html — Step 1: Ingestion
      "index.step1.title": "Pengunggahan Dokumen",
      "index.step1.subtitle": "Pilih aset kontrak untuk diantrekan ke jalur pemrosesan sovereign.",
      "index.step1.dropzone_title": "Seret dan lepas aset hukum di sini",
      "index.step1.dropzone_subtitle": "atau klik untuk menelusuri penyimpanan aman lokal",
      "index.step1.select_file_button": "PILIH BERKAS",
      "index.step1.confirm_continue": "KONFIRMASI & LANJUTKAN",
      "index.step1.clear_button": "Hapus",

      // index.html — Step 2: Document Details
      "index.step2.title": "Konteks dokumen",
      "index.step2.subtitle": "Kalibrasi metrik konteks untuk memastikan penerapan aturan yang tepat.",
      "index.step2.display_name_label": "Nama Tampilan",
      "index.step2.display_name_placeholder": "Nama Dokumen",
      "index.step2.contract_type_label": "Konteks Jenis Kontrak",
      "index.step2.contract_type_auto": "Deteksi Otomatis via Pengklasifikasi NLI (Disarankan)",
      "index.step2.contract_type_service": "Perjanjian Jasa",
      "index.step2.contract_type_nda": "Perjanjian Kerahasiaan (NDA)",
      "index.step2.contract_type_employment": "Kontrak Kerja",
      "index.step2.contract_type_software": "Lisensi Perangkat Lunak",
      "index.step2.contract_type_generic": "Kontrak Lain / Umum",
      "index.step2.jurisdiction_label": "Konteks Yurisdiksi",
      "index.step2.jurisdiction_auto": "Deteksi Otomatis Yurisdiksi Berlaku (Disarankan)",
      "index.step2.jurisdiction_fr": "Prancis (FR)",
      "index.step2.jurisdiction_be": "Belgia (BE)",
      "index.step2.jurisdiction_id": "Indonesia (ID)",
      "index.step2.jurisdiction_nl": "Belanda (NL)",
      "index.step2.jurisdiction_enw": "Inggris & Wales (EN&W)",
      "index.step2.jurisdiction_us": "Amerika Serikat (US)",
      "index.step2.jurisdiction_generic": "Umum / Internasional",
      "index.step2.language_label": "Konteks Bahasa",
      "index.step2.language_auto": "Deteksi Otomatis Bahasa (Disarankan)",
      "index.step2.language_en": "Inggris (EN)",
      "index.step2.language_fr": "Prancis (FR)",
      "index.step2.language_id": "Indonesia (ID)",
      "index.step2.language_nl": "Belanda (NL)",
      "index.step2.client_ref_label": "Referensi Klien",
      "index.step2.optional_suffix": "(Opsional)",
      "index.step2.client_ref_placeholder": "cth. PT Acme Corp",
      "index.step2.case_folder_label": "Folder Kasus / Proyek",
      "index.step2.case_folder_placeholder": "cth. NDA Kuartal 3",
      "index.step2.back_button": "Kembali ke Pengunggahan",
      "index.step2.proceed_button": "LANJUT KE OPSI",

      // index.html — Step 3: Analysis Options
      "index.step3.title": "Konfigurasi analisis",
      "index.step3.subtitle": "Sesuaikan kedalaman paket, cakupan, dan parameter validasi.",
      "index.step3.depth_label": "Kedalaman Cakupan Analisis",
      "index.step3.standard_title": "Analisis Standar",
      "index.step3.standard_desc": "Pemeriksaan Aturan L1 + Pengklasifikasi DistilBERT L2 + Penilai L3. Selesai cepat (biasanya 2-10 detik).",
      "index.step3.comprehensive_title": "Analisis Komprehensif",
      "index.step3.comprehensive_desc": "Termasuk Penjelasan LLM Qwen L4 & putaran komentar. Beban sistem tinggi (memakan beberapa menit).",
      "index.step3.policy_version_label": "Versi Kebijakan Penilaian",
      "index.step3.policy_default": "default_v1 (baseline terkalibrasi Juni 2026)",
      "index.step3.policy_sandbox": "sandbox_beta (aturan eksperimental)",
      "index.step3.reviewer_label": "Peninjau Default",
      "index.step3.reviewer_auto": "Penetapan Otomatis (Berdasarkan ketersediaan)",
      "index.step3.reviewer_lead": "Tim Analis Utama",
      "index.step3.reviewer_senior": "Peninjau Korporat Senior",
      "index.step3.back_button": "Kembali ke Detail",
      "index.step3.proceed_button": "LANJUT KE KONFIRMASI",

      // index.html — Step 4: Review and Confirmation
      "index.step4.title": "Tinjauan Kepatuhan Sovereign",
      "index.step4.subtitle": "Konfirmasi kebijakan retensi penyimpanan dan jalankan jalur analisis lokal.",
      "index.step4.summary_title": "Ringkasan Spesifikasi Analisis",
      "index.step4.file_asset_label": "Aset Berkas:",
      "index.step4.display_identity_label": "Identitas Tampilan:",
      "index.step4.contract_profile_label": "Profil Kontrak:",
      "index.step4.target_jurisdiction_label": "Yurisdiksi Target:",
      "index.step4.language_mode_label": "Mode Bahasa:",
      "index.step4.analysis_depth_label": "Kedalaman Analisis:",
      "index.step4.encryption_title": "Enkripsi Penyimpanan AES-256",
      "index.step4.encryption_desc": "Node enkripsi beroperasi normal. Hasil ekstraksi teks dan keluaran jalur pemrosesan dienkripsi saat disimpan, dengan kunci yang disimpan ketat dalam memori server lokal.",
      "index.step4.purge_title": "Kebijakan Penghapusan Otomatis 30 Hari",
      "index.step4.purge_desc": "Sesi analisis ini ditetapkan jadwal retensi tetap. Dokumen, ekstrak teks, dan laporan akan dihapus dalam 30 hari.",
      "index.step4.consent_label": "Saya menyatakan memiliki otorisasi korporat dan izin keamanan untuk mengunggah aset ini ke jalur pemrosesan PT SYDECO LightML. Saya menyetujui pemrosesan otomatis dan ekstraksi teks sementara.",
      "index.step4.back_button": "Kembali ke Opsi",
      "index.step4.initiate_button": "MULAI ANALISIS PIPELINE",

      // index.html — Step 5: Processing Dashboard
      "index.step5.description": "Dokumen Anda sedang diproses secara lokal di dalam partisi aman. Proses ini berjalan secara sinkron.",
      "index.step5.elapsed_time_label": "Waktu Berjalan:",
      "index.step5.seconds_suffix": "detik",
      "index.step5.overall_progress_label": "Progres Keseluruhan",
      "index.step5.stage_uploading_label": "1. Pengunggahan Dokumen",
      "index.step5.stage_extracting_label": "2. Penguraian Struktur & Ekstraksi Teks",
      "index.step5.stage_classifying_label": "3. Klasifikasi Bahasa, Yurisdiksi, & Jenis",
      "index.step5.stage_analyzing_label": "4. Pemeriksaan Klausul Wajib & Berisiko",
      "index.step5.stage_scoring_label": "5. Penilaian Matriks Risiko",
      "index.step5.stage_reasoning_label": "6. Penalaran & Penjelasan AI (LLM)",
      "index.step5.notice_title": "Catatan:",
      "index.step5.notice_body": "Berkas berukuran besar atau proses penalaran NLI/LLM memerlukan waktu pemrosesan. Anda dapat menutup atau meninggalkan layar ini dengan aman; analisis tetap berjalan secara aman di latar belakang.",
      "index.step5.cancel_button": "Batalkan Analisis",
      "index.step5.retry_button": "Coba Lagi Analisis",
      "index.step5.background_button": "Jalankan di Latar Belakang",

      // index.html — Telemetry sidebar
      "index.sidebar.title": "Telemetri Pipeline",
      "index.sidebar.step1_formats_title": "Format yang didukung",
      "index.sidebar.step1_formats_desc": "Mendukung TXT terstruktur standar, biner DOCX mentah, dan PDF berbasis teks bersih (hingga 10 MB).",
      "index.sidebar.step1_sovereignty_title": "Pemberitahuan Sovereignty",
      "index.sidebar.step1_sovereignty_desc": "Semua algoritma ekstraksi dan skrip klasifikasi berjalan secara lokal. Dokumen Anda tidak melintasi server eksternal.",
      "index.sidebar.step2_context_title": "Mengapa Konteks Penting",
      "index.sidebar.step2_context_desc": "Filter yurisdiksi yang tepat menerapkan kode hukum lokal yang relevan (mis. pasal Code civil di Prancis). Kategori kontrak menetapkan daftar klausul wajib khusus untuk mengidentifikasi kekurangan secara akurat.",
      "index.sidebar.step2_fallback_title": "Fallback Deteksi Otomatis",
      "index.sidebar.step2_fallback_desc": "Jika diatur ke otomatis, jalur pemrosesan memindai judul dan klausul yang berlaku untuk mengidentifikasi parameter pada pemrosesan Langkah 3.",
      "index.sidebar.step3_latency_title": "Latensi Lapisan LLM L4",
      "index.sidebar.step3_latency_desc": "Memilih mode Komprehensif mengaktifkan Qwen Transformers lokal untuk menghasilkan penjelasan rasional. Ini memerlukan siklus GPU/CPU lokal yang ekstensif.",
      "index.sidebar.step3_routing_title": "Perutean Peninjauan",
      "index.sidebar.step3_routing_desc": "Mengarahkan temuan ke analis tertentu mempercepat waktu validasi pelaporan di dalam antrean kasus.",
      "index.sidebar.step4_audit_title": "Kepatuhan Jejak Audit",
      "index.sidebar.step4_audit_desc": "Berdasarkan arahan sovereign, tindakan pengunggahan ini dicatat sebagai peristiwa audit aman yang berisi kredensial pengguna, alamat IP, dan checksum hash.",
      "index.sidebar.step4_retention_title": "Kunci Retensi",
      "index.sidebar.step4_retention_desc": "Penghapusan tidak dapat ditunda. Setelah jendela 30 hari berakhir, berkas akan dihapus sesuai standar privasi korporat.",
      "index.sidebar.node_label": "Node Pemrosesan Lokal",
      "index.sidebar.node_online": "Online",
      "index.sidebar.encryption_core_label": "Inti Enkripsi",

      // index.html — Logged-out landing
      "index.landing.badge": "Partisi Keamanan Enterprise Aktif",
      "index.landing.hero_title_line1": "Kontrak Sovereign",
      "index.landing.hero_title_line2": "Intelijen Risiko",
      "index.landing.hero_description": "Sydeco Contract Risk Analyzer (CRA) menyediakan analisis hukum mendalam berlapis pada dokumen perjanjian. Mengaudit hukum yang berlaku, yurisdiksi, ketentuan yang hilang, dan klausul berisiko secara lokal menggunakan LightML—tanpa data meninggalkan jaringan Anda.",
      "index.landing.authenticate_button": "Autentikasi untuk Memulai",
      "index.landing.view_docs_button": "Lihat Dokumentasi API",
      "index.landing.pillar1_title": "Sovereignty Lokal 100%",
      "index.landing.pillar1_desc": "Dokumen Anda tidak pernah melintasi jaringan eksternal. Pengunggahan, penguraian OCR, klasifikasi NLI, dan tugas penjelasan LLM sepenuhnya berjalan lokal pada inti perangkat keras terisolasi.",
      "index.landing.pillar2_title": "Audit Berlapis LightML",
      "index.landing.pillar2_desc": "Memanfaatkan jalur pemeriksaan 4 lapis: kepatuhan berbasis aturan, model klasifikasi DistilBERT, kebijakan validasi skor terstruktur, dan komentar ringkasan Qwen lokal.",
      "index.landing.pillar3_title": "Sitasi Terintegrasi",
      "index.landing.pillar3_desc": "Setiap risiko yang teridentifikasi otomatis ditautkan ke sitasi yang cocok dari pustaka hukum sistem. Peninjau dapat melakukan referensi silang, audit, dan menyetujui temuan di dalam editor interaktif.",
      "index.landing.readiness_node_label": "Node Keamanan Node-01:",
      "index.landing.readiness_status": "Siap",
      "index.landing.readiness_distilbert": "Pengklasifikasi DistilBERT Aktif",
      "index.landing.readiness_qwen": "Mesin Qwen-3 Tersedia",
      "index.landing.readiness_encryption": "Penyimpanan Terenkripsi AES-256",

      // index.html — Footer
      "index.footer.copyright": "© 2026 PT SYDECO. Contract Risk Analyzer.",
      "index.footer.privacy": "Privasi",
      "index.footer.terms": "Ketentuan",
      "index.footer.compliance": "Kepatuhan",

      // result.html — Loading / Error / Processing states
      "result.loading.message": "Mendekripsi dan memuat data penilaian…",
      "result.error.title": "Kesalahan Penilaian",
      "result.error.retry_link": "← Jalankan Analisis Baru",
      "result.processing.title": "Pipeline Berdaulat Sedang Diproses…",
      "result.processing.description": "Dokumen Anda sedang diproses di dalam partisi aman. Laporan ini akan otomatis dimuat setelah selesai.",
      "result.processing.overall_progress": "Progres Keseluruhan",

      // result.html — Case header
      "result.case_header.new_scan_button": "+ Pemindaian Baru",

      // result.html — Risk score hero panel
      "result.risk.score_label": "Skor Risiko",
      "result.risk.confidence_label": "Keyakinan Pipeline:",
      "result.risk.confidence_footnote": "Dikalibrasi terhadap telemetri pengklasifikasi NLI jenis dokumen.",
      "result.risk.disclaimer": "Dukungan keputusan semata — bukan nasihat hukum. Tidak menjamin keabsahan atau keberlakuan.",

      // result.html — Next Actions card
      "result.next_actions.title": "Tindakan Selanjutnya",
      "result.next_actions.current_assignee_label": "Penerima Tugas Saat Ini",
      "result.next_actions.assign_reviewer_button": "Tetapkan Peninjau",
      "result.next_actions.compare_versions_label": "Bandingkan Versi",
      "result.next_actions.no_previous_versions": "Tidak ada versi sebelumnya",

      // result.html — Professional Review card
      "result.professional_review.title": "Tinjauan Profesional",
      "result.professional_review.status_label": "Status",
      "result.professional_review.reviewer_label": "Peninjau",
      "result.professional_review.review_date_label": "Tanggal Tinjauan",
      "result.professional_review.comments_label": "Komentar",
      "result.professional_review.review_status_select_label": "Status Tinjauan",
      "result.professional_review.status_unreviewed": "Belum Ditinjau",
      "result.professional_review.status_confirmed": "Dikonfirmasi (Terverifikasi Benar)",
      "result.professional_review.status_edited": "Diedit (Disesuaikan/Dikoreksi)",
      "result.professional_review.status_rejected": "Ditolak (Analisis Keliru)",
      "result.professional_review.status_escalated": "Dieskalasi (Perlu Tinjauan Tingkat Lebih Tinggi)",
      "result.professional_review.review_comments_label": "Komentar Tinjauan",
      "result.professional_review.comment_placeholder": "Tambahkan catatan penilaian hukum, koreksi, atau instruksi...",
      "result.professional_review.submit_button": "Kirim Tinjauan",
      "result.professional_review.not_reviewed_notice": "Penilaian ini belum ditinjau oleh pengacara yang berkualifikasi.",

      // result.html — Priority Actions section
      "result.priority_actions.title": "Tindakan Prioritas",
      "result.priority_actions.empty": "Tidak ada tindakan prioritas — tidak ada temuan yang dapat ditindaklanjuti terdeteksi.",

      // result.html — Detected Findings & Anomalies section
      "result.findings.title": "Temuan & Anomali Terdeteksi",
      "result.findings.search_placeholder": "Cari bukti atau kategori…",
      "result.findings.severity_all": "Semua Tingkat Keparahan",
      "result.findings.severity_critical": "Tingkat Keparahan Kritis",
      "result.findings.severity_high": "Tingkat Keparahan Tinggi",
      "result.findings.severity_medium": "Tingkat Keparahan Sedang",
      "result.findings.severity_low": "Tingkat Keparahan Rendah",
      "result.findings.category_all": "Semua Kategori",
      "result.findings.category_unfair": "Klausul Tidak Adil",
      "result.findings.category_ai_classifier": "Temuan Pengklasifikasi AI",
      "result.findings.category_missing_clause": "Klausul Wajib yang Hilang",
      "result.findings.status_all": "Semua Status",
      "result.findings.status_unreviewed": "Belum Ditinjau",
      "result.findings.status_confirmed": "Dikonfirmasi",
      "result.findings.status_rejected": "Ditolak",
      "result.findings.why_matters_label": "Mengapa Ini Penting:",
      "result.findings.suggested_replacement_label": "Klausul Pengganti yang Disarankan:",
      "result.findings.verified_citations_label": "Sitasi Terverifikasi:",
      "result.findings.view_excerpt_button": "Lihat Kutipan",
      "result.findings.confirm_button": "Konfirmasi",
      "result.findings.reject_button": "Tolak",
      "result.findings.edit_spec_button": "Edit Spesifikasi",
      "result.findings.empty_title": "Tidak ada temuan yang cocok dengan filter saat ini",
      "result.findings.empty_note": "Catatan: Pemeriksaan otomatis adalah alat dukungan keputusan dan mungkin tidak mendeteksi semua pelanggaran kepatuhan. Dapatkan tinjauan hukum profesional sebelum penandatanganan akhir.",

      // result.html — Mandatory Clause Checklist section
      "result.checklist.title": "Daftar Periksa Klausul Wajib",
      "result.checklist.required_badge": "WAJIB",

      // result.html — AI Explanation section (Layer 4)
      "result.ai_explanation.title": "Penjelasan AI",
      "result.ai_explanation.summary_label": "RINGKASAN",
      "result.ai_explanation.clause_commentary_label": "KOMENTAR KLAUSUL",
      "result.ai_explanation.compliance_notes_label": "CATATAN KEPATUHAN",
      "result.ai_explanation.recommendations_label": "REKOMENDASI",

      // result.html — Extracted Agreement Text & Evidence Viewer section
      "result.evidence.title": "Teks Perjanjian Terekstrak & Penampil Bukti",
      "result.evidence.note": "frasa bukti yang cocok disorot pada panel gulir dokumen di bawah ini.",

      // result.html — Scoring Penalty Audit section
      "result.scoring.title": "Audit Penalti Penilaian",

      // result.html — Analysis Limitations section
      "result.limitations.title": "Keterbatasan Analisis",

      // result.html — Shared modal chrome
      "result.modal.cancel_button": "Batal",

      // result.html — Edit Recommendation modal
      "result.edit_modal.title": "Edit Spesifikasi Temuan",
      "result.edit_modal.label": "Redaksi Revisi Rekomendasi",
      "result.edit_modal.save_button": "Simpan Perubahan",

      // result.html — Reject Finding modal
      "result.reject_modal.title": "Tolak Temuan",
      "result.reject_modal.reason_label": "Alasan Penolakan",
      "result.reject_modal.reason_placeholder": "cth. Positif palsu — klausul ada di bagian 4.2",
      "result.reject_modal.confirm_button": "Tolak Temuan",

      // result.html — Assign Reviewer modal
      "result.assign_modal.title": "Tetapkan Peninjau Kasus",
      "result.assign_modal.description": "Pilih peninjau aktif untuk mendelegasikan verifikasi hukum.",
      "result.assign_modal.select_label": "Pilih Peninjau",
      "result.assign_modal.option_auto": "Default Sistem / Penetapan Otomatis",
      "result.assign_modal.option_lead": "Tim Analis Utama",
      "result.assign_modal.option_senior": "Peninjau Korporat Senior",
      "result.assign_modal.assign_button": "Tetapkan Kasus",

      // result.html — Footer
      "result.footer.copyright": "© 2026 PT SYDECO — Penganalisis Risiko Kontrak",

      // login.html — Branding & login form (shared header)
      "login.brand.title": "Gerbang Akses",
      "login.brand.subtitle": "Protokol Intelijen Berdaulat",
      "login.form.title": "Verifikasi Identitas Aman",
      "login.form.subtitle": "Khusus personel yang berwenang.",
      "login.form.email_label": "Email Institusi",
      "login.form.email_placeholder": "nama@sydeco.legal",
      "login.form.password_label": "Kunci Akses",
      "login.form.forgot_password_link": "Lupa Kata Sandi?",
      "login.form.org_label": "Konteks Organisasi",
      "login.form.optional_suffix": "(Opsional)",
      "login.form.org_placeholder": "Organisasi Default",
      "login.form.remember_label": "Berikan sesi persisten (24 jam)",
      "login.form.footer_security": "Koneksi diamankan melalui Protokol Sovereign AES-256.",
      "login.form.footer_help": "Butuh bantuan?",
      "login.form.footer_contact_admin": "Hubungi Admin Sistem",

      // login.html — Shared chrome (reused across MFA/recovery states)
      "login.common.cancel_button": "Batal",

      // login.html — MFA Verification Challenge
      "login.mfa_challenge.trust_label": "Percayai perangkat ini selama 30 hari",
      "login.mfa_challenge.policy_title": "Kebijakan Perangkat Tepercaya:",
      "login.mfa_challenge.policy_body": "Jangan pilih opsi ini pada terminal bersama atau publik. Memilih ini akan melewati pemeriksaan pendaftaran multi-faktor pada sesi peramban ini selama 30 hari ke depan.",

      // login.html — MFA Enrollment Setup
      "login.mfa_enroll.title": "Pendaftaran MFA Diperlukan",
      "login.mfa_enroll.subtitle": "Autentikasi Multi-Faktor wajib untuk keamanan akun korporat Anda.",
      "login.mfa_enroll.step1_title": "1. Pindai Kode QR",
      "login.mfa_enroll.step1_desc": "Pindai kode QR ini menggunakan Google Authenticator, Duo, atau aplikasi TOTP apa pun di perangkat seluler aman Anda.",
      "login.mfa_enroll.manual_key_label": "Kunci entri manual:",
      "login.mfa_enroll.step2_title": "2. Kode Pemulihan Aman",
      "login.mfa_enroll.step2_desc": "Kunci pemulihan ini memungkinkan akses jika Anda kehilangan perangkat autentikasi. Simpan di brankas fisik yang aman.",
      "login.mfa_enroll.step3_title": "3. Verifikasi Kode TOTP",
      "login.mfa_enroll.step3_desc": "Masukkan kode 6 digit yang dihasilkan dari aplikasi autentikator Anda untuk mengaktifkan MFA dan masuk.",
      "login.mfa_enroll.skip_button": "Lewati untuk saat ini",

      // login.html — Recover Access (Forgot Password)
      "login.forgot.title": "Pulihkan koordinat akses",
      "login.forgot.subtitle": "Kirimkan email institusi Anda untuk meminta pengaturan ulang kunci keamanan.",
      "login.forgot.email_label": "Email Institusi",
      "login.forgot.email_placeholder": "nama@sydeco.legal",
      "login.forgot.policy_title": "Catatan Kebijakan Sovereign:",
      "login.forgot.policy_body": "Sesuai dengan arahan identitas korporat yang aman, kredensial kata sandi tidak dapat direset sendiri. Mengirimkan formulir ini akan menghasilkan peristiwa audit dan memberi tahu administrator keamanan organisasi Anda untuk merilis token akses sementara.",
      "login.forgot.success_title": "Permintaan Akses Dimulai",
      "login.forgot.success_desc": "Peringatan koordinasi telah dikirim ke petugas keamanan sistem Anda.",
      "login.forgot.success_contact": "Silakan hubungi administrator yang ditunjuk oleh organisasi Anda atau Help Desk IT internal untuk mengotorisasi pelepasan kredensial untuk",
      "login.forgot.return_button": "Kembali ke Halaman Masuk",

      // login.html — Session Expired
      "login.session_expired.title": "Sesi Keamanan Berakhir",
      "login.session_expired.subtitle": "Batas Tidak Aktif Tercapai",
      "login.session_expired.description": "Untuk melindungi aset hukum eksklusif dan konfigurasi institusional, sesi akses sovereign Anda telah diakhiri. Progres analisis kontrak yang belum disimpan telah dihapus dengan aman dari tampilan peramban.",
      "login.session_expired.reauth_button": "Autentikasi Ulang Portal",
      "login.session_expired.footer_note": "Endpoint Aman: PT SYDECO LightML Contract Risk Analyzer v1.0",

      // login.html — Footer
      "login.footer.copyright": "© 2026 PT SYDECO. Contract Risk Analyzer.",
      "login.footer.privacy": "Kebijakan Privasi",
      "login.footer.terms": "Ketentuan Penggunaan",
      "login.footer.compliance": "Kepatuhan",

      // account.html — Header
      "account.header.back_link": "Kembali ke Sydeco CRA",
      "account.header.title": "Akun & Keamanan",

      // account.html — MFA status section
      "account.mfa.title": "Autentikasi Multi-Faktor",
      "account.mfa.mandatory_note": "Wajib untuk organisasi atau peran Anda.",
      "account.mfa.optional_note": "Opsional — direkomendasikan untuk akun institusi.",
      "account.mfa.enabled": "Aktif",
      "account.mfa.disabled": "Nonaktif",
      "account.mfa.enable_button": "Aktifkan MFA",
      "account.mfa.disable_button": "Nonaktifkan MFA",

      // account.html — Corporate Subscription & Usage section
      "account.usage.title": "Langganan & Penggunaan Korporat",
      "account.usage.subtitle": "Penggunaan sumber daya real-time untuk organisasi tenant Anda.",
      "account.usage.contracts_label": "Kontrak Diproses",
      "account.usage.pages_label": "Total Halaman Diekstrak",
      "account.usage.reports_label": "Unduhan PDF Profesional",
      "account.usage.loading": "Memuat detail penggunaan langganan…",

      // account.html — Shared chrome (reused across password/enroll states)
      "account.common.password_placeholder": "Kata Sandi",
      "account.common.cancel_button": "Batal",

      // account.html — Confirm Password (enable MFA) section
      "account.enable_password.title": "Konfirmasi Kata Sandi",
      "account.enable_password.subtitle": "Masukkan kembali kata sandi Anda untuk memulai pengaturan MFA.",
      "account.enable_password.verifying": "Memverifikasi…",
      "account.enable_password.continue_button": "Lanjutkan",

      // account.html — MFA Enrollment section
      "account.enroll.title": "Siapkan MFA",
      "account.enroll.step1_title": "1. Pindai Kode QR",
      "account.enroll.step1_desc": "Pindai dengan Google Authenticator, Duo, atau aplikasi TOTP apa pun.",
      "account.enroll.manual_key_label": "Kunci entri manual:",
      "account.enroll.step2_title": "2. Simpan Kode Pemulihan",
      "account.enroll.step2_desc": "Simpan ini di tempat yang aman — kode ini tidak akan ditampilkan lagi.",
      "account.enroll.step3_title": "3. Verifikasi Kode TOTP",
      "account.enroll.enabling": "Mengaktifkan…",

      // account.html — Disable MFA section
      "account.disable_password.title": "Nonaktifkan MFA",
      "account.disable_password.subtitle": "Masukkan kembali kata sandi Anda untuk konfirmasi. Ini akan menghapus pendaftaran autentikator dan kode pemulihan Anda.",
      "account.disable_password.disabling": "Menonaktifkan…",
      "account.disable_password.confirm_button": "Konfirmasi Nonaktifkan",

      // account.html — Error / success banners (hardcoded client-side copy only;
      // server-provided data.error text is displayed verbatim, untranslated)
      "account.errors.load_failed": "Gagal memuat status akun.",
      "account.errors.mfa_setup_failed": "Pengaturan MFA gagal.",
      "account.errors.mfa_setup_server_error": "Kesalahan server saat pengaturan MFA.",
      "account.errors.mfa_verify_failed": "Kode verifikasi gagal.",
      "account.errors.mfa_verify_server_error": "Kesalahan server saat verifikasi MFA.",
      "account.errors.mfa_disable_failed": "Gagal menonaktifkan MFA.",
      "account.errors.mfa_disable_server_error": "Kesalahan server saat menonaktifkan MFA.",
      "account.success.mfa_enabled": "MFA berhasil diaktifkan.",
      "account.success.mfa_disabled": "MFA dinonaktifkan.",

      // admin.html — Shared sidebar (byte-identical markup reused by citations.html — Task 7)
      "nav.sidebar.admin_portal": "Portal Admin",
      "nav.sidebar.core_operations": "Operasi Inti",
      "nav.sidebar.overview": "Ikhtisar",
      "nav.sidebar.case_history": "Riwayat Kasus",
      "nav.sidebar.management": "Manajemen",
      "nav.sidebar.team_management": "Manajemen Tim",
      "nav.sidebar.organizations": "Organisasi",
      "nav.sidebar.compliance_health": "Kepatuhan & Kesehatan",
      "nav.sidebar.audit_logs": "Log Audit",
      "nav.sidebar.system_health": "Kesehatan Sistem",
      "nav.sidebar.account_security": "Akun & Keamanan",

      // admin.html — Top header chrome
      "admin.header.new_analysis_prefix": "+ Baru",
      "admin.header.new_analysis_suffix": " Analisis",

      // admin.html — Breadcrumb-only tab title (not part of the shared sidebar)
      "admin.tab_titles.citation_verification": "Verifikasi Pustaka Sitasi",

      // admin.html — Loading state
      "admin.loading.aggregating": "Mengumpulkan statistik sistem…",

      // admin.html — Overview tab
      "admin.overview.title": "Ikhtisar Sistem",
      "admin.overview.subtitle": "Pantau penilaian dokumen historis, peringkat risiko, dan operasi pipeline.",
      "admin.overview.stat_documents_label": "Dokumen Tersimpan",
      "admin.overview.stat_documents_desc": "Perjanjian aktif yang dipertahankan",
      "admin.overview.stat_analyses_label": "Analisis Dijalankan",
      "admin.overview.stat_analyses_desc": "Pekerjaan model yang selesai",
      "admin.overview.stat_risk_label": "Indeks Risiko Rata-rata",
      "admin.overview.stat_risk_desc": "Metrik skor L3 gabungan",
      "admin.overview.stat_risky_label": "Perjanjian Berisiko",
      "admin.overview.stat_risky_desc": "Ditandai TINGGI atau KRITIS",
      "admin.overview.distribution_title": "Distribusi Kelas Risiko",
      "admin.overview.recent_title": "Laporan Risiko Terbaru",
      "admin.overview.col_ref_id": "ID Referensi",
      "admin.overview.col_filename": "Nama Berkas",
      "admin.overview.col_type": "Jenis",
      "admin.overview.col_jurisdiction": "Yurisdiksi",
      "admin.overview.col_score": "Skor",
      "admin.overview.col_risk_rating": "Peringkat Risiko",
      "admin.overview.col_analyzed": "Dianalisis",
      "admin.overview.empty_reports": "Tidak ada laporan hukum yang diproses dalam riwayat.",

      // admin.html — Case History tab
      "admin.history.title": "Riwayat Kasus",
      "admin.history.subtitle": "Cari, saring, dan atur laporan risiko kontrak historis.",
      "admin.history.filter_title": "Saring Dokumen",
      "admin.history.search_label": "Pencarian Umum",
      "admin.history.search_placeholder": "Nama berkas, kesalahan...",
      "admin.history.client_label": "Nama Klien",
      "admin.history.client_placeholder": "cth. PT Acme Corp",
      "admin.history.folder_label": "Kasus / Folder",
      "admin.history.folder_placeholder": "cth. NDA Kuartal 3",
      "admin.history.doc_type_label": "Jenis Dokumen",
      "admin.history.type_all": "Semua Jenis",
      "admin.history.type_nda": "Perjanjian Kerahasiaan",
      "admin.history.type_employment": "Kontrak Kerja",
      "admin.history.type_service": "Perjanjian Jasa",
      "admin.history.type_software": "Lisensi Perangkat Lunak",
      "admin.history.type_generic": "Umum/Lainnya",
      "admin.history.status_label": "Status Pekerjaan",
      "admin.history.status_all": "Semua Status",
      "admin.history.status_completed": "Selesai",
      "admin.history.status_processing": "Diproses",
      "admin.history.status_queued": "Dalam Antrean",
      "admin.history.status_failed": "Gagal",
      "admin.history.min_score_label": "Skor Minimum",
      "admin.history.max_score_label": "Skor Maksimum",
      "admin.history.clear_button": "Hapus Saringan",
      "admin.history.search_button": "Cari",
      "admin.history.col_ref_id": "ID Referensi",
      "admin.history.col_filename": "Nama Berkas",
      "admin.history.col_client": "Klien",
      "admin.history.col_folder": "Folder/Kasus",
      "admin.history.col_score": "Skor",
      "admin.history.col_status": "Status",
      "admin.history.col_reviewed": "Ditinjau",
      "admin.history.col_analyzed": "Dianalisis",
      "admin.history.empty": "Tidak ada analisis historis yang cocok dengan pencarian Anda.",
      "admin.history.prev_page": "Halaman Sebelumnya",
      "admin.history.next_page": "Halaman Berikutnya",

      // admin.html — Team Management tab
      "admin.team.title": "Manajemen Tim",
      "admin.team.subtitle": "Sediakan pengguna, tetapkan peran akses organisasi, dan audit kredensial keamanan.",
      "admin.team.create_button": "Buat Pengguna",
      "admin.team.col_id": "ID",
      "admin.team.col_email": "Email / Identitas",
      "admin.team.col_role": "Peran",
      "admin.team.col_org_id": "ID Organisasi",
      "admin.team.col_mfa_setup": "Pengaturan MFA",
      "admin.team.col_downloads": "Unduhan",
      "admin.team.col_status": "Status",
      "admin.team.col_actions": "Tindakan",
      "admin.team.role_analyst": "Analis",
      "admin.team.role_reviewer": "Peninjau",
      "admin.team.role_manager": "Manajer",
      "admin.team.role_viewer": "Pengamat",
      "admin.team.role_admin": "Administrator",
      "admin.team.mfa_active": "Aktif",
      "admin.team.mfa_unset": "Belum Diatur",
      "admin.team.download_enabled": "Diaktifkan",
      "admin.team.download_disabled": "Dinonaktifkan",
      "admin.team.status_active": "Aktif",
      "admin.team.status_suspended": "Ditangguhkan",
      "admin.team.reset_mfa_button": "Reset MFA",
      "admin.team.revoke_session_button": "Cabut Sesi",
      "admin.team.suspend_button": "Tangguhkan",
      "admin.team.activate_button": "Aktifkan",

      // admin.html — Organizations tab
      "admin.orgs.title": "Organisasi",
      "admin.orgs.subtitle": "Sediakan penyewa korporat, periksa aturan retensi penyimpanan, dan tetapkan batas pemindaian.",
      "admin.orgs.create_button": "Buat Organisasi",
      "admin.orgs.col_org_id": "ID Organisasi",
      "admin.orgs.col_name": "Nama Penyewa Korporat",
      "admin.orgs.col_retention": "Kebijakan Retensi Data",
      "admin.orgs.col_mfa_enforcement": "Penegakan MFA",
      "admin.orgs.col_scan_limits": "Batas Pemindaian Bulanan",
      "admin.orgs.col_status": "Status",
      "admin.orgs.col_save": "Simpan Konfigurasi",
      "admin.orgs.retention_7": "Penghapusan Efemeral 7 Hari",
      "admin.orgs.retention_15": "Penghapusan Otomatis 15 Hari",
      "admin.orgs.retention_30": "Kunci Penyimpanan 30 Hari",
      "admin.orgs.retention_90": "Log Standar 90 Hari",
      "admin.orgs.mfa_enforced": "Diwajibkan",
      "admin.orgs.mfa_optional": "Opsional",
      "admin.orgs.scan_50": "50 pemindaian / bln",
      "admin.orgs.scan_100": "100 pemindaian / bln",
      "admin.orgs.scan_500": "500 pemindaian / bln",
      "admin.orgs.scan_unlimited": "Pemindaian Tanpa Batas",
      "admin.orgs.status_active": "Aktif",
      "admin.orgs.update_button": "Perbarui Kebijakan",

      // admin.html — Citation Library tab
      "admin.citations.title": "Ruang Kerja Pustaka Sitasi",
      "admin.citations.subtitle": "Tinjau, verifikasi, tolak, atau gantikan sitasi sumber hukum draf yang dipetakan oleh aturan standar.",
      "admin.citations.pending_title": "Sitasi Draf Tertunda",
      "admin.citations.col_finding_id": "ID Temuan",
      "admin.citations.col_jurisdiction": "Yurisdiksi",
      "admin.citations.col_article_ref": "Referensi Pasal",
      "admin.citations.col_source_desc": "Deskripsi Sumber Hukum",
      "admin.citations.col_verifier_note": "Catatan Verifikator",
      "admin.citations.col_status": "Status",
      "admin.citations.col_decision": "Ruang Kerja Keputusan",
      "admin.citations.verify_button": "Verifikasi",
      "admin.citations.reject_button": "Tolak",
      "admin.citations.supersede_button": "Gantikan",
      "admin.citations.history_button": "Riwayat",
      "admin.citations.empty_draft": "Tidak ada sitasi draf yang menunggu verifikasi.",
      "admin.citations.verified_title": "Indeks Sitasi Terverifikasi",
      "admin.citations.col_article": "Pasal",
      "admin.citations.col_legal_code_ref": "Referensi Kode Hukum",
      "admin.citations.status_verified": "Terverifikasi",

      // admin.html — Audit Logs tab
      "admin.audits.title": "Log Audit Sistem",
      "admin.audits.subtitle": "Saring, cari, dan ekspor catatan peristiwa keamanan untuk audit institusional lokal.",
      "admin.audits.export_button": "Ekspor Log (CSV)",
      "admin.audits.search_placeholder": "Cari log berdasarkan tindakan atau detail…",
      "admin.audits.action_all": "Semua Tindakan",
      "admin.audits.reset_button": "Reset",
      "admin.audits.col_timestamp": "Stempel Waktu",
      "admin.audits.col_action": "Tindakan",
      "admin.audits.col_operator_id": "ID Operator",
      "admin.audits.col_org_id": "ID Organisasi",
      "admin.audits.col_resource_target": "Target Sumber Daya",
      "admin.audits.col_ip": "Alamat IP",
      "admin.audits.col_detail": "Ringkasan Detail",
      "admin.audits.empty": "Tidak ada peristiwa audit yang cocok tercatat.",

      // admin.html — System Health tab
      "admin.status.title": "Status Kesehatan Sistem",
      "admin.status.subtitle": "Pantau inti enkripsi lokal, konfigurasi batas laju, jadwal pencadangan, dan model ML aktif.",
      "admin.status.overview_title": "Ikhtisar status",
      "admin.status.sovereign_health_label": "Kesehatan sovereign:",
      "admin.status.database_label": "Basis Data Lokal:",
      "admin.status.datasets_label": "Verifikasi dataset:",
      "admin.status.encryption_title": "Inti Enkripsi",
      "admin.status.aes_label": "Status AES-256:",
      "admin.status.aes_configured": "Terkonfigurasi",
      "admin.status.aes_not_configured": "Peringatan: Belum Dikonfigurasi",
      "admin.status.storage_node_label": "Node Enkripsi Penyimpanan:",
      "admin.status.storage_node_value": "Modul Memori Sovereign PT SYDECO",
      "admin.status.models_title": "Model PyTorch Aktif",
      "admin.status.l2_label": "Pengklasifikasi L2 DistilBERT:",
      "admin.status.l2_ready": "Siap (Tersimpan Cache)",
      "admin.status.l2_unavailable": "Tidak Tersedia",
      "admin.status.l4_label": "Penalaran L4 Qwen:",
      "admin.status.l4_available": "Tersedia",
      "admin.status.l4_disabled": "Dinonaktifkan (Lite)",
      "admin.status.mlp_label": "Jaringan MLP Sydeco:",
      "admin.status.mlp_online": "Online",
      "admin.status.mlp_offline": "Offline",
      "admin.status.limits_title": "Batas & Pencadangan",
      "admin.status.rate_limiter_label": "Pembatas Laju API:",
      "admin.status.rate_limiter_value": "Aktif (Maks 20 req/mnt)",
      "admin.status.last_backup_label": "Pencadangan Sistem Terakhir:",
      "admin.status.backup_sync_label": "Sinkronisasi Node Cadangan:",
      "admin.status.backup_sync_value": "Tersinkronisasi",

      // admin.html — Create User modal
      "admin.modals.create_user.title": "Buat Akun Pengguna",
      "admin.modals.create_user.subtitle": "Konfigurasikan kredensial, peran, dan asosiasi penyewa korporat.",
      "admin.modals.create_user.email_label": "Identitas Email",
      "admin.modals.create_user.email_placeholder": "user@company.com",
      "admin.modals.create_user.password_label": "Kata sandi aman",
      "admin.modals.create_user.password_placeholder": "••••••••",
      "admin.modals.create_user.role_label": "Tetapkan Peran",
      "admin.modals.create_user.org_id_label": "ID Organisasi Korporat",
      "admin.modals.create_user.org_id_placeholder": "1",
      "admin.modals.create_user.cancel_button": "Batal",
      "admin.modals.create_user.submit_button": "Buat Pengguna",

      // admin.html — Create Org modal
      "admin.modals.create_org.title": "Buat Penyewa Korporat",
      "admin.modals.create_org.subtitle": "Daftarkan domain organisasi korporat sovereign baru.",
      "admin.modals.create_org.name_label": "Nama Penyewa Korporat",
      "admin.modals.create_org.name_placeholder": "PT Company Name",
      "admin.modals.create_org.cancel_button": "Batal",
      "admin.modals.create_org.submit_button": "Buat Penyewa",

      // admin.html — Citation History modal
      "admin.modals.citation_history.title": "Riwayat Revisi Sitasi",
      "admin.modals.citation_history.status_verified": "Status: terverifikasi",
      "admin.modals.citation_history.verified_note": "Dialihkan ke garis dasar terverifikasi oleh Administrator Sistem.",
      "admin.modals.citation_history.status_draft": "Status: draf",
      "admin.modals.citation_history.draft_note": "Ketentuan draf diuraikan melalui ekstraksi mesin.",
      "admin.modals.citation_history.close_button": "Tutup Riwayat",

      // citations.html — Page header
      "citations.header.title_prefix": "Otoritas Hukum",
      "citations.header.title_suffix": "Verifikasi",
      "citations.header.subtitle": "Protokol aman untuk meninjau, memverifikasi, dan mengelola versi sitasi hukum dalam arsitektur intelijen berdaulat.",

      // citations.html — Tabs
      "citations.tabs.queue": "Antrean & Verifikasi",
      "citations.tabs.history": "Riwayat & Versi",

      // citations.html — Stats grid
      "citations.stats.total_verified": "Total Terverifikasi",
      "citations.stats.awaiting_review": "Menunggu Tinjauan",
      "citations.stats.superseded": "Digantikan",
      "citations.stats.integrity_score": "Skor Integritas",

      // citations.html — Filters
      "citations.filters.search_label": "Cari Temuan",
      "citations.filters.search_placeholder": "Cari berdasarkan ID, pasal, atau sumber…",
      "citations.filters.jurisdiction_label": "Yurisdiksi",
      "citations.filters.jurisdiction_all": "Semua Yurisdiksi",
      "citations.filters.jurisdiction_id": "Indonesia (ID)",
      "citations.filters.jurisdiction_be": "Belgia (BE)",
      "citations.filters.jurisdiction_fr": "Prancis (FR)",
      "citations.filters.jurisdiction_nl": "Belanda (NL)",
      "citations.filters.jurisdiction_enw": "Inggris & Wales (EN&W)",
      "citations.filters.jurisdiction_us": "Amerika Serikat (US)",
      "citations.filters.jurisdiction_generic": "Umum (Lintas Batas)",
      "citations.filters.status_label": "Status",
      "citations.filters.status_all": "Semua Status",
      "citations.filters.status_draft_only": "Hanya Draf",
      "citations.filters.status_verified_only": "Hanya Terverifikasi",

      // citations.html — Main queue table
      "citations.table.col_finding_id": "ID Temuan",
      "citations.table.col_jurisdiction": "Yurisdiksi",
      "citations.table.col_proposed_article": "Pasal yang Diusulkan",
      "citations.table.col_legal_source": "Sumber Hukum",
      "citations.table.col_notes": "Catatan",
      "citations.table.col_status": "Status",
      "citations.table.col_action": "Tindakan",
      "citations.table.empty": "Tidak ada sitasi yang cocok ditemukan.",
      "citations.table.verify_button": "Verifikasi",
      "citations.table.ready_label": "Siap",

      // citations.html — History & Versioning tab
      "citations.history.timeline_title": "Linimasa Versi Otoritas",
      "citations.history.verified_by_label": "Diverifikasi Oleh",

      // citations.html — Loading state
      "citations.loading.message": "Memuat basis data sitasi…",
    },
  };

  function getLang() {
    const stored = localStorage.getItem(STORAGE_KEY);
    return SUPPORTED.indexOf(stored) !== -1 ? stored : DEFAULT_LANG;
  }

  function t(key) {
    return (DICT[getLang()] && DICT[getLang()][key]) || DICT[DEFAULT_LANG][key] || key;
  }

  function applyLang() {
    const lang = getLang();
    document.documentElement.lang = lang;

    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      const value = DICT[lang][el.dataset.i18n];
      if (value) el.textContent = value;
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
      const value = DICT[lang][el.dataset.i18nPlaceholder];
      if (value) el.setAttribute("placeholder", value);
    });

    document.querySelectorAll("[data-lang-toggle]").forEach(function (el) {
      el.textContent = lang === "en" ? "ID" : "EN";
    });

    if (window.Alpine && typeof window.Alpine.store === "function") {
      window.Alpine.store("lang", lang);
    }
  }

  function setLang(lang) {
    localStorage.setItem(STORAGE_KEY, SUPPORTED.indexOf(lang) !== -1 ? lang : DEFAULT_LANG);
    applyLang();
  }

  function toggleLang() {
    setLang(getLang() === "en" ? "id" : "en");
  }

  // Browser-only wiring — skipped when this file is `require()`-d from Node
  // (e.g. by i18n.selfcheck.js), since `document`/`window` don't exist there.
  if (typeof document !== "undefined") {
    document.addEventListener("alpine:init", function () {
      window.Alpine.store("lang", getLang());
    });
    document.addEventListener("DOMContentLoaded", applyLang);
  }
  if (typeof window !== "undefined") {
    window.i18n = { getLang, setLang, toggleLang, t, applyLang, DICT };
  }
  // Node-side export so i18n.selfcheck.js can `require()` this file directly
  // instead of evaluating it as a string (avoids new Function()/eval entirely).
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { getLang, setLang, toggleLang, t, applyLang, DICT };
  }
})();
