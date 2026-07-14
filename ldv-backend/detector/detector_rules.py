"""
detector_rules.py — Layer 1: Rule-based legal document analysis.

No ML required. Fully deterministic. Fast on CPU.

Public API
----------
    from detector.detector_rules import layer1_analyze

    result = layer1_analyze(text, jurisdiction="Belgium")

Returns
-------
dict:
    governing_law   : str | None
    venue           : str | None
    clause_presence : list[dict]   — required/optional clauses found or missing
    red_flags       : list[dict]   — leonine, abusive, or illegal patterns
    layer1_score    : dict         — {score 0-100, label LOW|MEDIUM|HIGH,
                                      missing_required, red_flag_count}
"""
from __future__ import annotations

import re
import logging
from typing import Optional

from detector.clause_db import clause_keywords
from detector.risk_clause_db import detect_keyword_flags

logger = logging.getLogger(__name__)

# ponytail: lazy import to avoid circular during test bootstrap
_profile_registry = None

def _get_registry():
    global _profile_registry
    if _profile_registry is None:
        try:
            import detector.profile_registry as _pr
            _profile_registry = _pr
        except Exception as exc:  # pragma: no cover
            logger.warning("profile_registry unavailable: %s", exc)
    return _profile_registry


# ── Governing Law ──────────────────────────────────────────────────────────────

_GOV_LAW_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"laws?\s+of\s+(?:the\s+)?republic\s+of\s+indonesia", re.I), "Indonesia"),
    (re.compile(r"laws?\s+of\s+indonesia", re.I), "Indonesia"),
    (re.compile(r"hukum\s+(?:negara\s+)?indonesia", re.I), "Indonesia"),
    (re.compile(r"laws?\s+of\s+belgium", re.I), "Belgium"),
    (re.compile(r"droit\s+belge", re.I), "Belgium"),
    (re.compile(r"belgisch\s+recht", re.I), "Belgium"),
    (re.compile(r"laws?\s+of\s+france", re.I), "France"),
    (re.compile(r"droit\s+fran[çc]ais", re.I), "France"),
    (re.compile(r"laws?\s+of\s+the\s+netherlands", re.I), "Netherlands"),
    (re.compile(r"nederlands\s+recht", re.I), "Netherlands"),
    (re.compile(r"laws?\s+of\s+england(?:\s+and\s+wales)?", re.I), "England & Wales"),
    (re.compile(r"laws?\s+of\s+(?:the\s+)?united\s+states", re.I), "United States"),
]

_GOV_LAW_GENERIC = re.compile(
    r"\bgoverned\s+by\b|\bconstrued\s+in\s+accordance\s+with\b", re.I
)


def detect_governing_law(text: str) -> Optional[str]:
    for pat, name in _GOV_LAW_PATTERNS:
        if pat.search(text):
            return name
    if _GOV_LAW_GENERIC.search(text):
        return "Unspecified"
    return None


# ── Venue ──────────────────────────────────────────────────────────────────────

_VENUE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"arbitration\s+in\s+([A-Za-z ,]+?)(?=[.,;]|\band\b|$)", re.I), "Arbitration"),
    (re.compile(r"courts?\s+of\s+([A-Za-z ,]+?)(?=[.,;]|\band\b|$)", re.I), "Courts"),
    (re.compile(r"venue\s+(?:shall\s+be\s+)?(?:in\s+)?([A-Za-z ,]+?)(?=[.,;]|\band\b|$)", re.I), "Venue"),
    (re.compile(r"Pengadilan\s+([A-Za-z ]+)", re.I), "Courts (Indonesia)"),
    (re.compile(r"tribunal\s+(?:de\s+)?([A-Za-z ,]+?)(?=[.,;]|\band\b|$)", re.I), "Tribunal"),
    (re.compile(r"rechtbank\s+(?:te\s+)?([A-Za-z ,]+?)(?=[.,;]|\band\b|$)", re.I), "Courts (NL)"),
]


def detect_venue(text: str) -> Optional[str]:
    for pat, label in _VENUE_PATTERNS:
        m = pat.search(text)
        if m:
            location = m.group(1).strip().rstrip(" ,.")[:60]
            if location:
                return f"{label}: {location}"
    return None


# ── Clause Presence ────────────────────────────────────────────────────────────

_CLAUSE_RULES: list[dict] = [
    # ── Generic required ──────────────────────────────────────────────────────
    {
        "id": "governing_law", "title": "Governing Law",
        "required": True, "jurisdiction": "generic",
        "patterns": [
            r"governed\s+by", r"laws?\s+of\s+\w+", r"construed\s+in\s+accordance",
            r"droit\s+applicable", r"droit\s+belge", r"droit\s+fran[çc]ais",
            r"hukum\s+(?:yang\s+berlaku|(?:negara\s+)?indonesia)",
            r"toepasselijk\s+recht", r"nederlands\s+recht", r"belgisch\s+recht",
        ],
    },
    {
        "id": "jurisdiction_venue", "title": "Jurisdiction / Venue",
        "required": True, "jurisdiction": "generic",
        "patterns": [
            r"\bjurisdiction\b", r"\bvenue\b", r"seat\s+of\s+arbitration",
            r"arbitration\s+in", r"Pengadilan", r"\bcourts?\s+of\b",
            r"\brechtbank\b", r"\btribunal\b",
        ],
    },
    {
        "id": "payment_terms", "title": "Payment Terms",
        "required": True, "jurisdiction": "generic",
        "patterns": [
            r"payment\s+terms?", r"paid\s+within", r"\binvoice\b", r"due\s+date",
            r"net\s+\d+\s+days?", r"modalit[eé]s?\s+de\s+paiement", r"syarat\s+pembayaran",
            r"betalingsvoorwaarden",
        ],
    },
    {
        "id": "termination", "title": "Termination",
        "required": True, "jurisdiction": "generic",
        "patterns": [
            r"\btermination\b", r"\bterminate\b", r"r[eé]siliation", r"r[eé]silier",
            r"\bbeëindiging\b", r"pemutusan\s+(?:kontrak|perjanjian)", r"\bopzegging\b",
        ],
    },
    {
        "id": "dispute_resolution", "title": "Dispute Resolution",
        "required": True, "jurisdiction": "generic",
        "patterns": [
            r"dispute\s+resolution", r"r[eè]glement\s+des?\s+litiges?",
            r"geschillenbeslechting", r"penyelesaian\s+sengketa",
            r"resolution\s+of\s+disputes?", r"\barbitration\b", r"\bmediation\b",
        ],
    },
    {
        "id": "limitation_liability", "title": "Limitation of Liability",
        "required": True, "jurisdiction": "generic",
        "patterns": [
            r"limitation\s+of\s+liability", r"liability\s+shall\s+be\s+limited",
            r"indirect\s+damages", r"consequential\s+damages",
            r"limitation\s+de\s+responsabilit[eé]", r"aansprakelijkheidsbeperking",
        ],
    },
    # ── Generic optional ──────────────────────────────────────────────────────
    {
        "id": "confidentiality", "title": "Confidentiality",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"\bconfidential\b", r"non.?disclosure", r"\bNDA\b",
            r"\bconfidentialit[eé]\b", r"geheimhouding",
        ],
    },
    {
        "id": "force_majeure", "title": "Force Majeure",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"force\s+majeure", r"act\s+of\s+god", r"events?\s+beyond.*control",
            r"overmacht", r"keadaan\s+kahar",
        ],
    },
    {
        "id": "intellectual_property", "title": "Intellectual Property",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"intellectual\s+property", r"\bcopyright\b", r"\btrademark\b",
            r"\bpatent\b", r"propri[eé]t[eé]\s+intellectuelle", r"kekayaan\s+intelektual",
        ],
    },
    # ── Generic boilerplate (cross-cutting) ───────────────────────────────────
    # Common in many contract types; reconciled to Ilham's DB so detection,
    # guidance and severity are available.  required=False here — promote into a
    # _CONTRACT_TYPE_PROFILES list to make one mandatory for a given type.
    {
        "id": "indemnification", "title": "Indemnification",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"indemnif(?:y|ication|ies)", r"hold\s+harmless", r"legal\s+defen[cs]e",
            r"indemnis(?:er|ation)", r"ganti\s+rugi", r"tanggung\s+rugi",
        ],
    },
    {
        "id": "insurance", "title": "Insurance",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"\binsurance\b", r"professional\s+indemnity", r"insured\b",
            r"\bpolicy\b\s+of\s+insurance", r"\bassurance\b", r"\basuransi\b",
        ],
    },
    {
        "id": "assignment", "title": "Assignment",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"\bassignment\b", r"transfer\s+of\s+rights", r"\bsubcontract",
            r"\bcession\b", r"transfert\s+de\s+droits", r"\bpengalihan\b",
        ],
    },
    {
        "id": "severability", "title": "Severability",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"\bseverab", r"partial\s+invalidity", r"survival\s+of\s+(?:the\s+)?clauses",
            r"divisibilit[eé]", r"invalidit[eé]\s+partielle", r"keterpisahan",
        ],
    },
    {
        "id": "entire_agreement", "title": "Entire Agreement",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"entire\s+agreement", r"whole\s+agreement", r"merger\s+clause",
            r"int[eé]gralit[eé]\s+de\s+l.accord", r"keseluruhan\s+perjanjian",
        ],
    },
    {
        "id": "amendment", "title": "Amendment / Modification",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"\bamendment\b", r"\baddendum\b", r"change\s+order", r"in\s+writing\s+and\s+signed",
            r"\bavenant\b", r"\bamendement\b", r"perubahan\s+kontrak",
        ],
    },
    # ── Contract-type-specific clauses ─────────────────────────────────────────
    # These stay required=False at the generic level (so they never penalise a
    # document they don't belong to).  Whether they are *mandatory* is decided
    # per contract type via _CONTRACT_TYPE_PROFILES, resolved in Layer 3.
    # Employment ----------------------------------------------------------------
    {
        "id": "notice_period", "title": "Notice Period",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"notice\s+period", r"period\s+of\s+notice",
            r"\b(?:[1-9]\d?\s+)?(?:days?|weeks?|months?)['’]?\s+(?:written\s+)?notice\b",
            r"pr[eé]avis", r"opzegtermijn", r"masa\s+pemberitahuan",
        ],
    },
    {
        "id": "compensation", "title": "Compensation / Salary",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"\b(?:salary|wages?|remuneration|compensation)\b",
            r"gross\s+(?:annual\s+|monthly\s+)?salary",
            r"r[eé]mun[eé]ration", r"\bgaji\b", r"\bsalaris\b", r"\bloon\b",
        ],
    },
    {
        "id": "working_hours", "title": "Working Hours",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"working\s+hours?", r"hours?\s+of\s+work", r"\d+\s+hours?\s+per\s+week",
            r"horaires?\s+de\s+travail", r"jam\s+kerja", r"werkuren",
        ],
    },
    {
        "id": "probation_period", "title": "Probation Period",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"probation(?:ary)?\s+period", r"p[eé]riode\s+d.essai",
            r"masa\s+percobaan", r"proeftijd",
        ],
    },
    {
        "id": "non_compete", "title": "Non-Compete",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"non[\s.\-]?compete", r"not\s+to\s+compete", r"restraint\s+of\s+trade",
            r"non[\s.\-]?concurrence", r"larangan\s+bersaing", r"concurrentiebeding",
        ],
    },
    # Lease ---------------------------------------------------------------------
    {
        "id": "lease_term", "title": "Lease Term / Duration",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"lease\s+term", r"term\s+of\s+(?:the\s+)?lease", r"tenancy\s+period",
            r"dur[eé]e\s+du\s+bail", r"jangka\s+waktu\s+sewa", r"huurtermijn",
        ],
    },
    {
        "id": "rent_amount", "title": "Rent Amount",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"monthly\s+rent", r"rental\s+(?:fee|amount|payment)", r"\brent\s+of\b",
            r"\bloyer\b", r"\buang\s+sewa\b", r"\bhuurprijs\b",
        ],
    },
    {
        "id": "security_deposit", "title": "Security Deposit",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"security\s+deposit", r"\bdeposit\b", r"d[eé]p[oô]t\s+de\s+garantie",
            r"\bcaution\b", r"uang\s+jaminan", r"\bwaarborg\b",
        ],
    },
    {
        "id": "maintenance_responsibility", "title": "Maintenance Responsibility",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"maintenance\s+(?:and\s+repairs?|responsibilit|obligation)",
            r"repairs?\s+and\s+maintenance",
            r"responsible\s+for\s+(?:the\s+)?(?:maintenance|repairs?|upkeep)",
            r"entretien\s+et\s+r[eé]parations?", r"pemeliharaan\s+dan\s+perbaikan",
            r"onderhoud",
        ],
    },
    # Software licence ----------------------------------------------------------
    {
        "id": "license_grant", "title": "License Grant",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"hereby\s+grants?", r"licensor\s+grants?", r"license\s+(?:is\s+)?(?:hereby\s+)?granted",
            r"grants?\s+(?:to\s+\w+\s+)?a\s+(?:non[\s.\-]?exclusive|exclusive|limited|perpetual)\s+licen[sc]e",
            r"conc[eè]de\s+une\s+licence", r"memberikan\s+lisensi", r"verleent\s+een\s+licentie",
        ],
    },
    {
        "id": "ip_ownership", "title": "IP Ownership",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"(?:ownership|title)\s+(?:of|to|in)\s+(?:all\s+)?intellectual\s+property",
            r"intellectual\s+property\s+(?:rights?\s+)?(?:shall\s+)?(?:remain|vest|belong)",
            r"all\s+rights?,?\s+title\s+and\s+interest",
            r"propri[eé]t[eé]\s+intellectuelle\s+(?:reste|appartient)",
        ],
    },
    {
        "id": "warranty_disclaimer", "title": "Warranty Disclaimer",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"\bas\s+is\b", r"without\s+warrant(?:y|ies)",
            r"disclaim(?:s|er)?\s+(?:all\s+)?warrant", r"no\s+warrant(?:y|ies)",
            r"sans\s+(?:aucune\s+)?garantie", r"tanpa\s+jaminan",
        ],
    },
    # Services / consulting -----------------------------------------------------
    {
        "id": "scope_of_services", "title": "Scope of Services / Deliverables",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"scope\s+of\s+(?:services?|work)", r"\bdeliverables?\b",
            r"services?\s+to\s+be\s+(?:provided|performed)",
            r"\bstatement\s+of\s+work\b", r"\bSOW\b",
            r"[eé]tendue\s+des\s+services", r"ruang\s+lingkup\s+(?:pekerjaan|layanan)",
        ],
    },
    # NDA -----------------------------------------------------------------------
    {
        "id": "return_of_materials", "title": "Return / Destruction of Materials",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"return\s+(?:or\s+destroy\s+)?(?:all\s+)?(?:confidential\s+)?(?:information|materials?|documents?)",
            r"return\s+or\s+destruction",
            r"restituer\s+ou\s+d[eé]truire", r"mengembalikan\s+atau\s+memusnahkan",
        ],
    },
    # Loan ----------------------------------------------------------------------
    {
        "id": "principal_amount", "title": "Principal Amount",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"principal\s+(?:amount|sum)", r"loan\s+amount",
            r"montant\s+du\s+pr[eê]t", r"jumlah\s+pinjaman", r"hoofdsom",
        ],
    },
    {
        "id": "interest_rate", "title": "Interest Rate",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"interest\s+rate", r"rate\s+of\s+interest",
            r"\d+(?:\.\d+)?\s*%\s*(?:per\s+annum|p\.a\.|annual)",
            r"taux\s+d.int[eé]r[eê]t", r"suku\s+bunga", r"rentevoet",
        ],
    },
    {
        "id": "repayment_schedule", "title": "Repayment Schedule",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"repayment\s+(?:schedule|terms?|plan)", r"\binstall?ments?\b",
            r"repaid?\s+in\s+\d+", r"[eé]ch[eé]ancier", r"jadwal\s+pembayaran",
            r"aflossingsschema",
        ],
    },
    {
        "id": "default_provisions", "title": "Default & Acceleration",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"event\s+of\s+default", r"\bdefault\b", r"\bacceleration\b",
            r"en\s+cas\s+de\s+d[eé]faut", r"wanprestasi", r"\bverzuim\b",
        ],
    },
    # Partnership ---------------------------------------------------------------
    {
        "id": "capital_contribution", "title": "Capital Contribution",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"capital\s+contribution", r"contribut(?:e|ion)\s+(?:of\s+)?capital",
            r"initial\s+contribution", r"apport\s+(?:en\s+)?capital",
            r"setoran\s+modal", r"kapitaalinbreng",
        ],
    },
    {
        "id": "profit_sharing", "title": "Profit & Loss Sharing",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"profit\s+(?:and\s+loss\s+)?sharing", r"share\s+of\s+(?:the\s+)?profits?",
            r"distribution\s+of\s+profits?", r"partage\s+des\s+b[eé]n[eé]fices",
            r"pembagian\s+(?:keuntungan|laba)", r"winstverdeling",
        ],
    },
    {
        "id": "management_rights", "title": "Management & Decision Rights",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"management\s+(?:rights?|of\s+the\s+partnership)", r"decision[\s.\-]?making",
            r"voting\s+rights?", r"gestion\s+de\s+la\s+soci[eé]t[eé]",
            r"hak\s+pengelolaan", r"\bbestuur\b",
        ],
    },
    # Purchase / sale -----------------------------------------------------------
    {
        "id": "goods_description", "title": "Description of Goods",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"description\s+of\s+(?:the\s+)?goods?",
            r"goods?\s+to\s+be\s+(?:sold|purchased|delivered)",
            r"specifications?\s+of\s+(?:the\s+)?(?:goods?|products?)",
            r"description\s+des\s+marchandises", r"deskripsi\s+barang",
        ],
    },
    {
        "id": "delivery_terms", "title": "Delivery Terms",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"delivery\s+(?:terms?|date|schedule)", r"deliver(?:y|ed)\s+(?:within|by|on)",
            r"\bshipment\b", r"\bincoterms?\b", r"\bFOB\b", r"\bCIF\b",
            r"conditions?\s+de\s+livraison", r"syarat\s+pengiriman", r"\blevering\b",
        ],
    },
    {
        "id": "warranty", "title": "Warranty",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"\bwarrant(?:y|ies)\b", r"\bguarantees?\b", r"warrants?\s+that",
            r"\bgarantie\b", r"\bjaminan\b",
        ],
    },
    {
        "id": "title_transfer", "title": "Transfer of Title / Risk",
        "required": False, "jurisdiction": "generic",
        "patterns": [
            r"transfer\s+of\s+(?:title|ownership|risk)", r"title\s+(?:shall\s+)?pass(?:es)?",
            r"risk\s+of\s+loss", r"passing\s+of\s+(?:title|risk)",
            r"transfert\s+de\s+propri[eé]t[eé]", r"peralihan\s+(?:hak\s+milik|kepemilikan)",
            r"eigendomsoverdracht",
        ],
    },
    # ── Indonesia-specific ────────────────────────────────────────────────────
    {
        "id": "bilingual_clause", "title": "Bilingual Clause (UU 24/2009)",
        "required": False, "jurisdiction": "Indonesia",
        "patterns": [
            r"bahasa\s+indonesia", r"indonesian\s+version\s+shall\s+prevail",
            r"dwibahasa", r"versi\s+bahasa\s+indonesia",
        ],
    },
    # ── Belgium-specific ──────────────────────────────────────────────────────
    {
        "id": "consumer_withdrawal", "title": "Consumer Right of Withdrawal",
        "required": False, "jurisdiction": "Belgium",
        "patterns": [
            r"droit\s+de\s+r[eé]tractation", r"right\s+of\s+withdrawal",
            r"herroepingsrecht", r"14\s+(?:calendar\s+)?days?\s+(?:to\s+)?cancel",
        ],
    },
    # ── France-specific ───────────────────────────────────────────────────────
    {
        "id": "consumer_withdrawal_fr", "title": "Consumer Right of Withdrawal (FR)",
        "required": False, "jurisdiction": "France",
        "patterns": [
            r"droit\s+de\s+r[eé]tractation", r"d[eé]lai\s+de\s+r[eé]tractation",
            r"14\s+jours?\s+(?:pour\s+)?(?:se\s+)?r[eé]tracter",
        ],
    },
]


def check_clause_presence(text: str, jurisdiction: Optional[str] = None) -> list[dict]:
    results = []
    for rule in _CLAUSE_RULES:
        if rule["jurisdiction"] != "generic" and rule["jurisdiction"] != jurisdiction:
            continue

        present = False
        evidence = ""
        evidence_span = None
        source = "rules"
        for pattern in rule["patterns"]:
            m = re.search(pattern, text, re.I)
            if m:
                start = max(0, m.start() - 60)
                end = min(len(text), m.end() + 60)
                evidence = text[start:end].strip().replace("\n", " ")
                evidence_span = [m.start(), m.end()]
                present = True
                break

        # ponytail: fall back to Ilham's lawyer-authored keywords only when our
        # regex missed — pure additive coverage. Plain case-insensitive substring
        # is enough for her phrase keywords; upgrade to word-boundary if it ever
        # over-matches.
        if not present:
            low = text.lower()
            for kw in clause_keywords(rule["id"]):
                idx = low.find(kw)
                if idx != -1:
                    start = max(0, idx - 60)
                    end = min(len(text), idx + len(kw) + 60)
                    evidence = text[start:end].strip().replace("\n", " ")
                    evidence_span = [idx, idx + len(kw)]
                    present = True
                    source = "kb_keywords"
                    break

        results.append({
            "clause_id": rule["id"],
            "title":     rule["title"],
            "required":  rule["required"],
            "present":   present,
            "evidence":  evidence if present else None,
            "evidence_span": evidence_span,
            "source":    source if present else None,
        })

    return results


# ── Contract-type → mandatory-clause mapping ───────────────────────────────────
# THE explicit answer to "which clauses are mandatory for which contract type".
# Keys are the normalised document-type labels produced by Layer 2
# (detector_distilbert._DOC_TYPE_SPECS).  Values are the clause IDs that *must*
# be present for that contract type; a missing one is penalised in Layer 3.
# Every ID here must exist in _CLAUSE_RULES above.

_BASELINE_REQUIRED: list[str] = [
    "governing_law", "jurisdiction_venue", "payment_terms",
    "termination", "dispute_resolution", "limitation_liability",
]

_CONTRACT_TYPE_PROFILES: dict[str, list[str]] = {
    "employment contract": [
        "governing_law", "jurisdiction_venue", "termination",
        "notice_period", "compensation", "working_hours", "dispute_resolution",
    ],
    "lease agreement": [
        "governing_law", "jurisdiction_venue", "lease_term", "rent_amount",
        "security_deposit", "maintenance_responsibility", "termination",
        "dispute_resolution",
    ],
    "software license": [
        "governing_law", "jurisdiction_venue", "license_grant", "ip_ownership",
        "limitation_liability", "warranty_disclaimer", "termination",
        "dispute_resolution",
    ],
    "service agreement": [
        "governing_law", "jurisdiction_venue", "scope_of_services",
        "payment_terms", "termination", "limitation_liability",
        "dispute_resolution",
    ],
    "consulting agreement": [
        "governing_law", "jurisdiction_venue", "scope_of_services",
        "payment_terms", "confidentiality", "termination", "dispute_resolution",
    ],
    "commercial agreement": [
        "governing_law", "jurisdiction_venue", "payment_terms", "termination",
        "limitation_liability", "dispute_resolution",
    ],
    "non-disclosure agreement": [
        "governing_law", "jurisdiction_venue", "confidentiality", "termination",
        "return_of_materials", "dispute_resolution",
    ],
    "loan agreement": [
        "governing_law", "jurisdiction_venue", "principal_amount",
        "interest_rate", "repayment_schedule", "default_provisions",
        "termination", "dispute_resolution",
    ],
    "partnership agreement": [
        "governing_law", "jurisdiction_venue", "capital_contribution",
        "profit_sharing", "management_rights", "termination",
        "dispute_resolution",
    ],
    "purchase agreement": [
        "governing_law", "jurisdiction_venue", "goods_description",
        "payment_terms", "delivery_terms", "warranty", "title_transfer",
        "dispute_resolution",
    ],
    "general contract": list(_BASELINE_REQUIRED),
}

# Title lookup so callers can render human-readable mandatory-clause lists.
_CLAUSE_TITLES: dict[str, str] = {r["id"]: r["title"] for r in _CLAUSE_RULES}


def normalize_doc_type(label: Optional[str]) -> str:
    """Lower-case / strip a Layer 2 document-type label for profile lookup."""
    return (label or "").strip().lower()


def required_clauses_for(doc_type: Optional[str]) -> list[str]:
    """Return the mandatory clause IDs for *doc_type*.

    Primary source: profile_registry (file-driven, ~56 types).
    Compat fallback: _CONTRACT_TYPE_PROFILES (kept until parity tests pass).
    Final fallback: _BASELINE_REQUIRED.
    ponytail: compat layer — remove _CONTRACT_TYPE_PROFILES after parity confirmed.
    """
    reg = _get_registry()
    if reg is not None:
        clauses, _ = reg.required_clauses_for(doc_type or "")
        return list(clauses)
    # compat shim
    return list(_CONTRACT_TYPE_PROFILES.get(normalize_doc_type(doc_type), _BASELINE_REQUIRED))


def clause_title(clause_id: str) -> str:
    """Human-readable title for a clause ID (falls back to the ID itself)."""
    return _CLAUSE_TITLES.get(clause_id, clause_id)


def reconcile_required_flags(clause_presence: list[dict], doc_type: Optional[str]) -> None:
    """Overwrite each entry's `required` flag with the contract-type-aware set, in place.

    check_clause_presence() runs before Layer 2 has classified the document, so it
    stamps `required` from the static _BASELINE_REQUIRED set. Once doc_type is known,
    the mandatory set can differ (a lease needs lease_term/rent_amount, not
    payment_terms/limitation_liability) -- callers (frontend checklist/findings,
    risk_explainer) all read this flag, so it must match required_clauses_for(doc_type),
    which is what L3 scoring and Explain Mode already use.
    """
    required_ids = set(required_clauses_for(doc_type))
    for entry in clause_presence:
        entry["required"] = entry["clause_id"] in required_ids


def evaluate_contract_type_requirements(
    clause_presence: list[dict],
    doc_type: Optional[str],
) -> dict:
    """Resolve which mandatory clauses (for this contract type) are present/missing.

    Parameters
    ----------
    clause_presence : the list returned by check_clause_presence()
    doc_type        : Layer 2 document-type label (e.g. "employment contract")

    Returns
    -------
    dict:
        contract_type   : normalised type used for the lookup
        matched_profile : True if a specific profile matched (else baseline)
        mandatory       : list[{clause_id, title, present}]
        present         : list[clause_id] present
        missing         : list[clause_id] mandatory but absent
    """
    norm = normalize_doc_type(doc_type)
    reg = _get_registry()
    if reg is not None:
        required_ids, matched_pid = reg.required_clauses_for(norm)
        matched_profile = matched_pid is not None
    else:
        required_ids = required_clauses_for(norm)
        matched_pid = norm if norm in _CONTRACT_TYPE_PROFILES else None
        matched_profile = norm in _CONTRACT_TYPE_PROFILES

    present_ids = {c["clause_id"] for c in clause_presence if c.get("present")}

    mandatory = [
        {"clause_id": cid, "title": clause_title(cid), "present": cid in present_ids}
        for cid in required_ids
    ]
    missing = [cid for cid in required_ids if cid not in present_ids]

    return {
        "contract_type":   norm or "unknown",
        "matched_profile": matched_profile,
        "profile_id":      matched_pid,
        "mandatory":       mandatory,
        "present":         [cid for cid in required_ids if cid in present_ids],
        "missing":         missing,
    }


# ── Red Flags ──────────────────────────────────────────────────────────────────

_RED_FLAGS: list[dict] = [
    # Leonine — one-sided profit allocation
    {
        "id": "leonine_profit", "severity": "HIGH", "type": "leonine",
        "description": "One-sided profit allocation",
        "patterns": [
            r"all\s+profits?\s+(?:shall\s+be\s+)?(?:allocated|given|assigned)\s+to\s+one\s+party",
            r"tous\s+les\s+b[eé]n[eé]fices\s+(?:sont\s+)?attribu[eé]s?\s+[aà]\s+une\s+(?:seule\s+)?partie",
            r"semua\s+keuntungan\s+(?:diberikan|dialokasikan)\s+kepada\s+satu\s+pihak",
            r"alle\s+winsten\s+worden\s+toegekend\s+aan\s+[eé][eé]n\s+partij",
        ],
    },
    # Leonine — investor bears no loss
    {
        "id": "leonine_no_loss", "severity": "HIGH", "type": "leonine",
        "description": "Investor bears no loss (leonine clause)",
        "patterns": [
            r"(?:investor|party)\s+bears?\s+no\s+loss",
            r"l.investisseur\s+ne\s+supporte\s+aucune\s+perte",
            r"investor\s+tidak\s+menanggung\s+kerugian",
            r"investeerder\s+draagt\s+(?:in\s+geen\s+geval\s+)?(?:geen\s+)?verlies",
        ],
    },
    # Abusive — excessive penalty rate
    {
        "id": "excessive_penalty", "severity": "HIGH", "type": "abusive",
        "description": "Excessive penalty rate (≥10% per day)",
        "patterns": [
            r"penalty\s+(?:of\s+)?(?:[1-9]\d|[1-9]\d\d)\s*%\s*per\s+day",
            r"p[eé]nalit[eé]\s+(?:de\s+)?(?:[1-9]\d|[1-9]\d\d)\s*%\s*par\s+jour",
            r"denda\s+(?:[1-9]\d|[1-9]\d\d)\s*%\s*per\s+hari",
            r"boete\s+van\s+(?:[1-9]\d|[1-9]\d\d)\s*%\s*per\s+dag",
        ],
    },
    # Abusive — blanket rights waiver
    {
        "id": "rights_waiver", "severity": "HIGH", "type": "abusive",
        "description": "Blanket waiver of all legal rights",
        "patterns": [
            r"waives?\s+all\s+(?:legal\s+)?rights?",
            r"renonce\s+[aà]\s+(?:tout|tous)\s+(?:ses\s+)?(?:droits?\s+(?:et\s+)?)?recours",
            r"melepaskan\s+semua\s+hak(?:\s+hukum)?",
            r"doet\s+afstand\s+van\s+alle\s+(?:juridische\s+)?rechten",
        ],
    },
    # Abusive — unilateral modification without notice
    {
        "id": "unilateral_modification", "severity": "MEDIUM", "type": "abusive",
        "description": "Unilateral contract modification without notice",
        "patterns": [
            r"(?:may|can|shall)\s+(?:modify|amend|change)\s+(?:this\s+)?(?:agreement|contract|terms?)\s+(?:at\s+any\s+time|without\s+notice)",
            r"peut\s+modifier\s+(?:le\s+pr[eé]sent\s+)?(?:contrat|accord)\s+(?:[aà]\s+tout\s+moment|sans\s+pr[eé]avis)",
            r"dapat\s+mengubah\s+(?:perjanjian|kontrak)\s+ini\s+kapan\s+saja\s+tanpa\s+pemberitahuan",
        ],
    },
    # Abusive — total liability exclusion
    {
        "id": "total_liability_exclusion", "severity": "MEDIUM", "type": "abusive",
        "description": "Total liability exclusion for one party",
        "patterns": [
            r"no\s+liability\s+whatsoever",
            r"shall\s+not\s+be\s+liable\s+(?:for\s+)?(?:any|all)\s+(?:damages?|losses?|claims?)\s+whatsoever",
            r"aucune\s+responsabilit[eé]\s+(?:quelle\s+qu.en\s+soit\s+la\s+cause|en\s+aucun\s+cas)",
            r"geen\s+aansprakelijkheid\s+(?:voor\s+)?(?:welke\s+)?(?:schade|verliezen)\s+dan\s+ook",
        ],
    },
    # Abusive — automatic renewal without adequate notice period
    {
        "id": "auto_renewal_no_notice", "severity": "MEDIUM", "type": "abusive",
        "description": "Automatic renewal with no or very short notice period",
        "patterns": [
            r"automatically\s+renew(?:s|ed|al)?\s+unless\s+(?:cancelled|terminated)\s+within\s+[1-7]\s+days?",
            r"renouvellement\s+automatique\s+sans\s+pr[eé]avis",
            r"otomatis\s+diperpanjang\s+tanpa\s+pemberitahuan",
        ],
    },
    # Payment risk — extremely short payment window (1–7 days)
    {
        "id": "short_payment_window_high", "severity": "HIGH", "type": "payment_risk",
        "description": "Extremely short payment window (1–7 days or within 48 hours)",
        "patterns": [
            r"\bwithin\s+[1-7]\s+(?:calendar\s+|business\s+)?days?\b",
            r"\bpay(?:ment)?\s+within\s+[1-7]\s+days?\b",
            r"\bdue\s+within\s+[1-7]\s+days?\b",
            r"\bnet\s+[1-7]\b",
            r"\bwithin\s+(?:24|48|72)\s+hours?\b",
            r"\bdalam\s+[1-7]\s+hari\b",
            r"\bdalam\s+(?:24|48|72)\s+jam\b",
            r"\bdans\s+[1-7]\s+jours?\b",
            r"\bbinnen\s+[1-7]\s+dagen\b",
        ],
    },
    # Payment risk — tight payment window (8–14 days)
    {
        "id": "short_payment_window_medium", "severity": "MEDIUM", "type": "payment_risk",
        "description": "Tight payment window (8–14 days)",
        "patterns": [
            r"\bwithin\s+(?:[89]|1[0-4])\s+(?:calendar\s+|business\s+)?days?\b",
            r"\bpay(?:ment)?\s+within\s+(?:[89]|1[0-4])\s+days?\b",
            r"\bdue\s+within\s+(?:[89]|1[0-4])\s+days?\b",
            r"\bnet\s+(?:[89]|1[0-4])\b",
            r"\bdalam\s+(?:[89]|1[0-4])\s+hari\b",
            r"\bdans\s+(?:[89]|1[0-4])\s+jours?\b",
            r"\bbinnen\s+(?:[89]|1[0-4])\s+dagen\b",
        ],
    },
    # Abusive — customer bears the cost of vendor's errors
    {
        "id": "customer_pays_vendor_errors", "severity": "HIGH", "type": "abusive",
        "description": "Customer bears cost of vendor's errors or rework",
        "patterns": [
            r"(?:customer|client)\s+(?:shall\s+)?(?:pay|bear|cover)\s+.{0,40}(?:vendor|supplier|contractor).{0,30}(?:error|mistake|rework|defect)",
            r"biaya\s+(?:perbaikan|pengerjaan\s+ulang)\s+ditanggung\s+(?:pelanggan|klien)",
            r"client\s+paie\s+(?:pour\s+)?les\s+erreurs?\s+du\s+vendeur",
            r"klant\s+betaalt\s+(?:voor\s+)?(?:de\s+)?fouten\s+van\s+de\s+leverancier",
        ],
    },
    # Abusive — fee charged to file a dispute or complaint
    {
        "id": "fee_for_dispute", "severity": "MEDIUM", "type": "abusive",
        "description": "Party charged a fee to file a complaint or dispute",
        "patterns": [
            r"\bfee\s+(?:to\s+(?:file|submit|raise)\s+a?\s+)?(?:complaint|dispute|claim)\b",
            r"\b(?:payment|charge|cost)\s+(?:required\s+)?to\s+(?:dispute|complain|challenge)\b",
            r"\bbiaya\s+(?:untuk\s+)?(?:mengadu|mengajukan\s+sengketa|komplain)\b",
            r"\bfrais\s+(?:pour\s+)?(?:se\s+plaindre|d[eé]poser\s+(?:une\s+)?plainte)\b",
            r"\bkosten\s+voor\s+(?:het\s+indienen\s+van\s+)?(?:een\s+)?klacht\b",
        ],
    },
    # Illegal — exclusion of liability for intentional breach or gross negligence
    {
        "id": "no_liability_intentional", "severity": "HIGH", "type": "illegal",
        "description": "Exclusion of liability for intentional breach or gross negligence",
        "patterns": [
            r"\bno\s+liability\s+(?:for\s+)?(?:intentional|willful|deliberate)\s+(?:breach|misconduct|act)\b",
            r"\bnot\s+(?:be\s+)?liable\s+(?:for\s+(?:any\s+)?)?(?:intentional|willful|deliberate|gross)\s+(?:breach|negligence|misconduct)\b",
            r"\btidak\s+bertanggung\s+jawab\s+(?:atas\s+)?(?:pelanggaran|kelalaian)\s+(?:yang\s+)?(?:disengaja|berat)\b",
            r"\baucune\s+responsabilit[eé]\s+(?:pour\s+)?(?:violation|manquement)\s+intentionnel",
            r"\bgeen\s+aansprakelijkheid\s+(?:voor\s+)?(?:opzettelijke|grove)\s+(?:schending|nalatigheid)\b",
        ],
    },
    # Illegal object
    {
        "id": "illegal_object", "severity": "HIGH", "type": "illegal",
        "description": "Potential illegal object in contract",
        "patterns": [
            r"\b(?:narcotic|drug\s+trafficking|arms\s+deal|money\s+launder|human\s+traffick)\b",
        ],
    },
]


def detect_red_flags(text: str) -> list[dict]:
    found = []
    for flag in _RED_FLAGS:
        for pattern in flag["patterns"]:
            m = re.search(pattern, text, re.I)
            if m:
                start = max(0, m.start() - 50)
                end = min(len(text), m.end() + 50)
                snippet = text[start:end].strip().replace("\n", " ")
                found.append({
                    "id":          flag["id"],
                    "type":        flag["type"],
                    "severity":    flag["severity"],
                    "description": flag["description"],
                    "evidence":    snippet,
                    "evidence_span": [m.start(), m.end()],
                    "source":      "regex",
                })
                break  # one match per rule is enough

    # Second pass: keyword-based risky-clause detection from the lawyer-authored
    # category CSVs (abusive/dangerous/illegal/leonine). Suppresses concepts the
    # regex rules already fired, so the two passes don't double-count.
    fired = {f["id"] for f in found}
    found.extend(detect_keyword_flags(text, exclude_ids=fired))
    return found


# ── Scoring ────────────────────────────────────────────────────────────────────

def _layer1_score(clause_checks: list[dict], red_flags: list[dict]) -> dict:
    missing_required = [c["clause_id"] for c in clause_checks if c["required"] and not c["present"]]
    high_flags   = sum(1 for f in red_flags if f["severity"] == "HIGH")
    medium_flags = sum(1 for f in red_flags if f["severity"] == "MEDIUM")

    score = 100
    score -= len(missing_required) * 15
    score -= high_flags * 25
    score -= medium_flags * 10
    score = max(0, min(100, score))

    label = "LOW" if score >= 75 else "MEDIUM" if score >= 45 else "HIGH"

    return {
        "score":            score,
        "label":            label,
        "missing_required": missing_required,
        "red_flag_count":   len(red_flags),
    }


# ── Public API ─────────────────────────────────────────────────────────────────

def layer1_analyze(text: str, jurisdiction: Optional[str] = None) -> dict:
    """
    Run all Layer 1 (rule-based) checks on *text*.

    Uses original document text (not translated) so that multilingual
    patterns match against the native language content.

    Parameters
    ----------
    text         : extracted contract text (original language)
    jurisdiction : jurisdiction string from detect_jurisdiction(), or None

    Returns
    -------
    dict with keys:
        governing_law, venue, clause_presence, red_flags, layer1_score
    """
    governing_law   = detect_governing_law(text)
    venue           = detect_venue(text)
    clause_presence = check_clause_presence(text, jurisdiction)
    red_flags       = detect_red_flags(text)
    score           = _layer1_score(clause_presence, red_flags)

    logger.info(
        "Layer 1: governing_law=%s venue=%s missing_required=%d red_flags=%d score=%d (%s)",
        governing_law, venue,
        len(score["missing_required"]), score["red_flag_count"],
        score["score"], score["label"],
    )

    return {
        "governing_law":   governing_law,
        "venue":           venue,
        "clause_presence": clause_presence,
        "red_flags":       red_flags,
        "layer1_score":    score,
    }
