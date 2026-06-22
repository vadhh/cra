import os
import logging
import json
import time
import uuid
import chardet
import magic
from flask import Flask, request, jsonify, send_from_directory, Response, redirect, g, session
from flask_cors import CORS
import fitz
from langdetect import detect

from detector.detector_jurisdiction import detect_jurisdiction
from detector.detector_rules import layer1_analyze, required_clauses_for, clause_title
from detector.citation_db import annotate_layer1
from detector.detector_distilbert import layer2_analyze, semantic_clause_presence
from detector.detector_scorer import layer3_score
from detector.detector_explain import layer4_explain
from translator import translate_text
from sydeco_engine import classify_clauses as _sydeco_classify
import database
import auth

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = int(os.getenv("LDV_MAX_UPLOAD_MB", "10")) * 1024 * 1024
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# Document types that are not contracts — skip full clause/risk analysis for these
_NON_CONTRACT_TYPES = {"invoice", "receipt", "purchase order"}

_MIME_ALLOWLIST = {
    ".pdf":  {"application/pdf"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",
    },
    ".txt":  {"text/plain"},
}

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ldv-frontend")
)
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

app = Flask(__name__)
auth.configure_secret_key(app)

# Same-origin by default (the frontend is served by this app). Cross-origin
# access must be explicitly granted: LDV_CORS_ORIGINS="https://a.example,https://b.example"
_cors_origins = os.getenv("LDV_CORS_ORIGINS", "")
if _cors_origins:
    CORS(app, origins=[o.strip() for o in _cors_origins.split(",") if o.strip()])

# Init DB on first import
database.init_db()


# ── Error handlers ─────────────────────────────────────────────────────────────

@app.errorhandler(413)
def file_too_large(e):
    return jsonify({"error": "File exceeds the 10 MB limit"}), 413


@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled exception")
    return jsonify({"error": "Internal server error"}), 500


# ── Text extraction ────────────────────────────────────────────────────────────

def _extract_pdf(data: bytes) -> str:
    doc = fitz.open(stream=data, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def _extract_docx(data: bytes) -> str:
    import docx
    from io import BytesIO
    document = docx.Document(BytesIO(data))
    parts = []
    for para in document.paragraphs:
        if para.text.strip():
            parts.append(para.text)
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    parts.append(cell.text)
    return "\n".join(parts)


def _extract_txt(data: bytes) -> str:
    detected = chardet.detect(data)
    encoding = detected.get("encoding") or "utf-8"
    return data.decode(encoding, errors="replace")


def _validate_and_extract(file) -> tuple[bytes, str, str]:
    """Validate upload, return (data, ext, text). Raises ValueError on failure."""
    ext = os.path.splitext(file.filename.lower())[1]
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    data = file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) == 0:
        raise ValueError("File is empty")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError(f"File exceeds the {MAX_UPLOAD_BYTES // (1024*1024)} MB limit")

    detected_mime = magic.from_buffer(data[:4096], mime=True)
    allowed_mimes = _MIME_ALLOWLIST.get(ext, set())
    if detected_mime == "application/octet-stream" and ext == ".docx" and data[:2] == b"PK":
        detected_mime = "application/zip"
    if detected_mime not in allowed_mimes:
        raise ValueError(f"File content does not match extension '{ext}'")

    if ext == ".pdf":
        text = _extract_pdf(data)
    elif ext == ".docx":
        text = _extract_docx(data)
    else:
        text = _extract_txt(data)

    if not text.strip():
        raise ValueError("Could not extract text from file")

    return data, ext, text


def _run_analysis(text: str, jurisdiction: str, lang: str) -> dict:
    """Run L1–L3 analysis and return result dict.

    For non-contract documents (invoice, receipt, purchase order) the pipeline
    stops after L2: no clause-risk scoring or MLP tagging is performed.
    """
    layer1 = layer1_analyze(text, jurisdiction)
    annotate_layer1(layer1, jurisdiction)  # attach legal citations to each finding

    analysis_text = text
    if lang not in ("en", "unknown"):
        try:
            analysis_text = translate_text(text, "en")
        except Exception as e:
            logger.warning("Translation failed, using original: %s", e)

    layer2 = layer2_analyze(analysis_text)

    doc_type_label = ((layer2.get("document_type") or {}).get("label") or "").lower()
    if doc_type_label in _NON_CONTRACT_TYPES:
        logger.info("Document type '%s' — skipping clause analysis", doc_type_label)
        return {
            "language":          lang,
            "jurisdiction":      jurisdiction,
            "document_type_note": (
                f"This document appears to be {_article(doc_type_label)} {doc_type_label}. "
                "Full contractual clause analysis is not applicable. "
                "Payment-term rules were still evaluated."
            ),
            "layer1":    layer1,
            "layer2":    layer2,
            "layer3":    {"available": False, "skipped": True, "reason": "non_contract_document"},
            "layer4":    {"available": False, "skipped": True},
            "clause_tags": [],
        }

    _semantic_backfill(layer1, doc_type_label, analysis_text)

    layer3 = layer3_score(layer1, layer2, lang=lang)
    clause_tags = _sydeco_classify(analysis_text)

    return {
        "language":     lang,
        "jurisdiction": jurisdiction,
        "layer1":       layer1,
        "layer2":       layer2,
        "layer3":       layer3,
        "layer4":       {"available": False, "skipped": True},
        "clause_tags":  clause_tags,
    }


def _semantic_backfill(layer1: dict, doc_type_label: str, text: str) -> None:
    """Re-check keyword-missing *required* clauses with semantic NLI, in place.

    Keyword/regex detection misses clauses worded unusually.  Before scoring, we
    run an NLI presence check (reusing the loaded DistilBERT model) on the
    required clauses L1 marked absent; any that are semantically present get
    flipped to present with source="semantic_nli", so L3's missing-clause logic
    needs no change.  Pure recovery — it only ever turns a False into True.
    """
    presence = layer1.get("clause_presence") or []
    required = set(required_clauses_for(doc_type_label))
    missing = [
        (c["clause_id"], c.get("title") or clause_title(c["clause_id"]))
        for c in presence
        if c["clause_id"] in required and not c.get("present")
    ]
    if not missing:
        return

    recovered = semantic_clause_presence(text, missing)
    for c in presence:
        conf = recovered.get(c["clause_id"])
        if conf is not None:
            c["present"] = True
            c["source"] = "semantic_nli"
            c["evidence"] = c.get("evidence") or f"semantic match (NLI {conf})"


def _article(word: str) -> str:
    return "an" if word[:1].lower() in "aeiou" else "a"


# ── Auth routes ────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return send_from_directory(FRONTEND_DIR, "login.html")
    data = request.get_json(silent=True) or request.form
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = auth.verify_login(email, password)
    if user is None:
        return jsonify({"error": "Invalid credentials"}), 401
    session["uid"] = user["id"]
    return jsonify({"ok": True, "role": user["role"]})


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


# ── Upload & analyse (primary endpoint) ───────────────────────────────────────

@app.route("/upload", methods=["POST"])
@auth.login_required
def upload():
    """Save file to disk, extract text, run analysis, persist to DB."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    try:
        data, ext, text = _validate_and_extract(file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Save file to disk
    stored_name = f"{uuid.uuid4().hex}{ext}"
    file_path   = os.path.join(UPLOADS_DIR, stored_name)
    with open(file_path, "wb") as f:
        f.write(data)

    # Detect language
    try:
        lang = detect(text)
    except Exception:
        lang = "unknown"

    # Save document record
    doc_id = database.save_document(
        original_filename=file.filename,
        stored_filename=stored_name,
        file_path=file_path,
        file_size=len(data),
        file_type=ext,
        language=lang,
        extracted_text=text,
        org_id=g.user["org_id"],
        owner_id=g.user["id"],
    )

    t_start = time.monotonic()
    jurisdiction = detect_jurisdiction(text)
    result = _run_analysis(text, jurisdiction, lang)
    elapsed = round(time.monotonic() - t_start, 2)

    layer3 = result.get("layer3", {})
    layer2 = result.get("layer2", {}) or {}

    dt = layer2.get("document_type")
    doc_type_str = dt.get("label") if isinstance(dt, dict) else dt

    # Save analysis record
    analysis_id = database.save_analysis(
        document_id=doc_id,
        jurisdiction=jurisdiction,
        document_type=doc_type_str,
        risk_score=layer3.get("score"),
        risk_label=layer3.get("label"),
        result=result,
    )

    logger.info(
        "UPLOAD: file=%s lang=%s jurisdiction=%s risk=%s/%s time=%.2fs id=%s",
        file.filename, lang, jurisdiction,
        layer3.get("score"), layer3.get("label"), elapsed, analysis_id,
    )

    return jsonify({"id": analysis_id})


# ── Result API ─────────────────────────────────────────────────────────────────

@app.route("/api/result/<analysis_id>")
@auth.login_required
def api_result(analysis_id: str):
    row = database.get_result(analysis_id)
    if row is None:
        return jsonify({"error": "Not found"}), 404
    user = g.user
    if user["role"] != "admin" and row.get("org_id") != user["org_id"]:
        return jsonify({"error": "Forbidden"}), 403
    row.pop("org_id", None)  # internal field, not part of the API response
    row["result"] = json.loads(row["result_json"])
    del row["result_json"]
    return jsonify(row)


# ── Admin API ──────────────────────────────────────────────────────────────────

@app.route("/api/stats")
@auth.admin_required
def api_stats():
    return jsonify(database.get_stats())


@app.route("/api/recent")
@auth.admin_required
def api_recent():
    limit = min(int(request.args.get("limit", 10)), 50)
    return jsonify(database.get_recent(limit))


# ── PDF report ─────────────────────────────────────────────────────────────────

@app.route("/report", methods=["POST"])
@auth.login_required
def report():
    from pdf_report import generate_pdf
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Expected JSON body with analysis result"}), 400
    try:
        pdf_bytes = generate_pdf(data)
    except Exception as e:
        logger.exception("PDF generation failed")
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=contract_risk_report.pdf"},
    )


# ── Legacy /analyze (kept for curl/API access) ────────────────────────────────

@app.route("/analyze", methods=["POST"])
@auth.login_required
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    try:
        data, ext, text = _validate_and_extract(file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        lang = detect(text)
    except Exception:
        lang = "unknown"

    jurisdiction = detect_jurisdiction(text)
    result = _run_analysis(text, jurisdiction, lang)

    want_explain = request.args.get("explain", "0") == "1"
    if want_explain:
        layer1 = result["layer1"]
        layer2 = result["layer2"]
        layer3 = result["layer3"]
        analysis_text = text
        if lang not in ("en", "unknown"):
            try:
                analysis_text = translate_text(text, "en")
            except Exception:
                pass
        result["layer4"] = layer4_explain(
            analysis_text, jurisdiction=jurisdiction,
            layer1=layer1, layer2=layer2, layer3=layer3,
        )

    return jsonify(result)


# ── Health ─────────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    from detector.detector_distilbert import is_available as l2_available
    from sydeco_engine import is_available as mlp_available
    try:
        from send_prompt import _model as qwen_model
        qwen_loaded = qwen_model is not None
    except Exception:
        qwen_loaded = False
    return jsonify({
        "status":            "ok",
        "layer1":            "ready",
        "layer2_distilbert": l2_available(),
        "layer3_scorer":     "ready",
        "layer4_qwen":       qwen_loaded,
        "sydeco_mlp":        mlp_available(),
    })


# ── Frontend pages ─────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/result")
@app.route("/result/<analysis_id>")
def result_page(analysis_id=None):
    return send_from_directory(FRONTEND_DIR, "result.html")


@app.route("/admin")
def admin_page():
    user = auth.current_user()
    if user is None or user["role"] != "admin":
        return redirect("/login")
    return send_from_directory(FRONTEND_DIR, "admin.html")


@app.route("/<path:filename>")
def frontend_files(filename):
    filepath = os.path.join(FRONTEND_DIR, filename)
    if os.path.isfile(filepath):
        return send_from_directory(FRONTEND_DIR, filename)
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    # Debug mode exposes the Werkzeug debugger (remote code execution if the
    # port is reachable) — opt-in only. Production: gunicorn -w 2 app:app
    app.run(debug=os.getenv("LDV_DEBUG", "0") == "1")
