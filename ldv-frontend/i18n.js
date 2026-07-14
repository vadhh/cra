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
