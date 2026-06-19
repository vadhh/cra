"""
scripts/train_mlp.py — Train the Sydeco clause-risk MLP (legal_mlp.pkl).

Generates synthetic labeled clause data bootstrapped from the L1 rule patterns,
then trains a TF-IDF + MLPClassifier sklearn Pipeline and saves it to the path
expected by sydeco_engine.py.

Usage
-----
    cd ldv-backend
    python3 scripts/train_mlp.py

Output
------
    ~/Desktop/sydeco_ai_core_bundle/models/legal_mlp.pkl

Override paths:
    SYDECO_MLP_PATH=/tmp/legal_mlp.pkl python3 scripts/train_mlp.py
    SYDECO_CSV_PATH=/path/to/clauses.csv python3 scripts/train_mlp.py

CSV format (two columns, with header row):
    text,label
    "The party waives all rights.",abusive_clause
    "Payment within 30 days.",normal

Valid labels: abusive_clause | payment_risk | missing_mandatory | normal
"""
from __future__ import annotations

import csv
import os
import pickle
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline

# ── Training data ──────────────────────────────────────────────────────────────
# Labels: abusive_clause | payment_risk | missing_mandatory | normal

_DATA: list[tuple[str, str]] = [

    # ── abusive_clause ─────────────────────────────────────────────────────────
    ("The party herewith waives all legal rights to dispute this agreement.", "abusive_clause"),
    ("Client irrevocably waives all rights to seek any legal recourse.", "abusive_clause"),
    ("The signatory waives all legal rights including the right to a fair hearing.", "abusive_clause"),
    ("Party B waives any and all legal rights under applicable law.", "abusive_clause"),
    ("All legal rights are waived by the undersigned upon signing.", "abusive_clause"),
    ("The company may modify this agreement at any time without notice to the other party.", "abusive_clause"),
    ("Provider can amend these terms at any time without prior notification.", "abusive_clause"),
    ("We may change contract terms without notice at our sole discretion.", "abusive_clause"),
    ("Party A may unilaterally change the terms of this contract without consent.", "abusive_clause"),
    ("The service provider shall modify these terms whenever deemed appropriate without informing the client.", "abusive_clause"),
    ("No liability whatsoever shall be incurred by the service provider under any circumstances.", "abusive_clause"),
    ("The company bears no liability for any damages, losses, or claims of any kind.", "abusive_clause"),
    ("Provider accepts no liability whatsoever for consequential or direct damages.", "abusive_clause"),
    ("Vendor shall not be liable for any and all damages regardless of cause.", "abusive_clause"),
    ("Under no circumstances shall the company be responsible for any harm to the client.", "abusive_clause"),
    ("All profits shall be allocated exclusively to Party A regardless of Party B's contribution.", "abusive_clause"),
    ("One party receives all the benefits while the other bears all risks and losses.", "abusive_clause"),
    ("All financial benefits go to the investor; the operating partner assumes all losses.", "abusive_clause"),
    ("Investor bears no loss under any scenario while retaining all profit rights.", "abusive_clause"),
    ("Party A is entitled to all gains and is exempt from all losses arising from this contract.", "abusive_clause"),
    ("The counterparty shall have no right to challenge or contest any decision made by the company.", "abusive_clause"),
    ("Client surrenders all rights to legal proceedings relating to this agreement.", "abusive_clause"),
    ("Le prestataire peut modifier le contrat à tout moment sans préavis.", "abusive_clause"),
    ("L'investisseur ne supporte aucune perte quelle que soit la situation.", "abusive_clause"),
    ("La partie renonce à tous ses droits de recours juridiques.", "abusive_clause"),
    ("Alle winsten worden toegekend aan één partij; verliezen worden volledig gedragen door de andere partij.", "abusive_clause"),
    ("De dienstverlener is in geen enkel geval aansprakelijk voor schade.", "abusive_clause"),
    ("Pihak pertama melepaskan semua hak hukum yang dimilikinya berdasarkan perjanjian ini.", "abusive_clause"),
    ("Investor tidak menanggung kerugian dalam keadaan apapun.", "abusive_clause"),
    ("Penyedia layanan dapat mengubah perjanjian ini kapan saja tanpa pemberitahuan.", "abusive_clause"),
    ("The provider may terminate services immediately and without cause at its sole discretion.", "abusive_clause"),
    ("Company may suspend or terminate the agreement without any reason and at any time.", "abusive_clause"),
    ("Client waives any right to compensation in the event of early termination by the provider.", "abusive_clause"),
    ("The service provider bears no responsibility for acts of negligence by its employees.", "abusive_clause"),
    ("All disputes shall be resolved exclusively in favour of the service provider.", "abusive_clause"),
    ("The client forfeits all claims upon accepting these terms.", "abusive_clause"),
    ("Party A retains the right to cancel without notice and without liability.", "abusive_clause"),
    ("Doet afstand van alle juridische rechten op grond van deze overeenkomst.", "abusive_clause"),
    ("Aucune responsabilité quelle qu'en soit la cause ne peut être engagée.", "abusive_clause"),
    ("The company may at its sole discretion change pricing without prior notice.", "abusive_clause"),

    # ── payment_risk ───────────────────────────────────────────────────────────
    ("A penalty of 15% per day shall apply to all late payments.", "payment_risk"),
    ("Late payment will incur a penalty fee of 20% per day on the outstanding amount.", "payment_risk"),
    ("Interest of 25% per month shall accrue on any unpaid balance.", "payment_risk"),
    ("A surcharge of 50% per day is applied automatically upon payment default.", "payment_risk"),
    ("Client will be charged 30% interest per month on overdue invoices.", "payment_risk"),
    ("Failure to pay by the due date results in a daily penalty of 12%.", "payment_risk"),
    ("Late payment fee: 18% per day, compounded daily until settled.", "payment_risk"),
    ("All outstanding amounts attract a 40% per month interest charge.", "payment_risk"),
    ("Pénalité de 15% par jour s'applique en cas de paiement tardif.", "payment_risk"),
    ("Un intérêt de 20% par mois est dû sur tout solde impayé.", "payment_risk"),
    ("Denda 15% per hari akan dikenakan atas keterlambatan pembayaran.", "payment_risk"),
    ("Boete van 20% per dag op het uitstaande bedrag bij te late betaling.", "payment_risk"),
    ("Interest rate of 60% per annum applies on unpaid invoices past due date.", "payment_risk"),
    ("Each day of delayed payment incurs an additional charge of 10% of the invoice total.", "payment_risk"),
    ("Overdue invoices will automatically attract a 35% late payment penalty per month.", "payment_risk"),
    ("A compound late payment interest rate of 24% per month will apply without further notice.", "payment_risk"),
    ("The client must pay a daily penalty of 10% for each day beyond the payment deadline.", "payment_risk"),
    ("Failure to pay within 3 days triggers a penalty of 50% of the total amount due.", "payment_risk"),
    ("Late payment charges of 15% per week are automatically added to outstanding balances.", "payment_risk"),
    ("An immediate surcharge of 20% is applied the day after the payment due date.", "payment_risk"),
    ("Outstanding balances accrue interest at 120% per annum, charged daily.", "payment_risk"),
    ("Any delay in payment results in a penalty of 25% per month, non-negotiable.", "payment_risk"),
    ("Overdue accounts are subject to a late fee of 10% compounded monthly.", "payment_risk"),
    ("The provider reserves the right to charge 18% interest per month on unpaid amounts.", "payment_risk"),
    ("Payment received after the due date will be subject to a 45% penalty charge.", "payment_risk"),
    ("A late payment penalty of 11% per day applies automatically from the day after due date.", "payment_risk"),
    ("The interest accruing on late payments is set at 36% per annum, billed monthly.", "payment_risk"),
    ("Rente van 15% per maand wordt in rekening gebracht op achterstallige betalingen.", "payment_risk"),
    ("Bunga keterlambatan sebesar 20% per bulan akan dikenakan secara otomatis.", "payment_risk"),
    ("Tout retard de paiement entraîne une pénalité de 10% par semaine.", "payment_risk"),

    # ── missing_mandatory ──────────────────────────────────────────────────────
    ("Governing law: TBD — to be confirmed by both parties at a later stage.", "missing_mandatory"),
    ("Dispute resolution: see attached schedule [MISSING].", "missing_mandatory"),
    ("[Insert applicable jurisdiction here]", "missing_mandatory"),
    ("Payment terms: to be agreed upon separately.", "missing_mandatory"),
    ("Termination provisions: to be determined.", "missing_mandatory"),
    ("The limitation of liability clause will be inserted prior to execution.", "missing_mandatory"),
    ("Venue for disputes: [TO BE COMPLETED].", "missing_mandatory"),
    ("Confidentiality terms: refer to separate NDA not yet executed.", "missing_mandatory"),
    ("[Governing law clause to be added]", "missing_mandatory"),
    ("Force majeure: TBD.", "missing_mandatory"),
    ("Payment schedule: see Exhibit A [not attached].", "missing_mandatory"),
    ("The parties shall agree on termination conditions before contract commencement.", "missing_mandatory"),
    ("Liability cap: amount to be determined by mutual agreement.", "missing_mandatory"),
    ("[This section intentionally left blank pending legal review]", "missing_mandatory"),
    ("Jurisdiction: to be discussed and confirmed at a later date.", "missing_mandatory"),
    ("Late payment provisions: refer to addendum [draft pending].", "missing_mandatory"),
    ("Dispute resolution mechanism: to be negotiated between the parties.", "missing_mandatory"),
    ("Section 7 — Intellectual Property: [DRAFT — INCOMPLETE]", "missing_mandatory"),
    ("Terms of payment will be outlined in a side letter to be executed separately.", "missing_mandatory"),
    ("Notice provisions: [insert notice details here].", "missing_mandatory"),
    ("Warranty terms: to be finalised by the legal team.", "missing_mandatory"),
    ("The applicable law governing this agreement has not yet been determined.", "missing_mandatory"),
    ("[Termination clause pending review by counsel]", "missing_mandatory"),
    ("Indemnification: refer to Schedule B [not yet drafted].", "missing_mandatory"),
    ("The parties have not yet agreed on the venue for arbitration.", "missing_mandatory"),
    ("Limitation of liability: see separate agreement [not enclosed].", "missing_mandatory"),
    ("Governing jurisdiction: TBC prior to execution.", "missing_mandatory"),
    ("This clause is reserved for future inclusion upon mutual agreement.", "missing_mandatory"),
    ("Payment provisions: to be determined based on project scope.", "missing_mandatory"),
    ("The termination clause has not yet been agreed upon by the parties.", "missing_mandatory"),

    # ── normal ─────────────────────────────────────────────────────────────────
    ("This agreement is entered into as of the date first written above between the parties.", "normal"),
    ("Either party may terminate this agreement upon 30 days written notice to the other party.", "normal"),
    ("Payment shall be made within 30 days of the date of invoice by bank transfer.", "normal"),
    ("This agreement shall be governed by the laws of Belgium.", "normal"),
    ("Any disputes arising from this contract shall be referred to the courts of Brussels.", "normal"),
    ("Both parties agree to maintain the confidentiality of all proprietary information.", "normal"),
    ("The service provider shall deliver the agreed services within the specified timeframe.", "normal"),
    ("This contract constitutes the entire agreement between the parties on this subject.", "normal"),
    ("Intellectual property created under this agreement shall belong to the commissioning party.", "normal"),
    ("Force majeure events shall suspend the obligations of the affected party for the duration thereof.", "normal"),
    ("The parties may amend this agreement in writing with mutual consent of both parties.", "normal"),
    ("Notices shall be sent by registered mail or email to the address specified herein.", "normal"),
    ("Each party shall bear its own legal costs in connection with this agreement.", "normal"),
    ("This agreement may not be assigned without the prior written consent of both parties.", "normal"),
    ("The parties confirm that they have read and understood the terms of this agreement.", "normal"),
    ("In the event of a breach, the non-breaching party shall give written notice of the breach.", "normal"),
    ("Invoices shall be issued monthly and paid within 30 calendar days of receipt.", "normal"),
    ("The service provider warrants that the services will be performed with reasonable skill and care.", "normal"),
    ("Both parties shall comply with all applicable laws and regulations in performing this agreement.", "normal"),
    ("This agreement shall remain in force for a period of one year from the date of signing.", "normal"),
    ("Ce contrat est régi par le droit belge et tout litige sera soumis aux tribunaux de Bruxelles.", "normal"),
    ("Het contract is onderworpen aan Belgisch recht en Nederlands recht.", "normal"),
    ("Perjanjian ini tunduk pada hukum Republik Indonesia.", "normal"),
    ("The landlord agrees to maintain the property in a habitable condition throughout the lease term.", "normal"),
    ("The tenant shall pay rent on the first day of each calendar month by bank transfer.", "normal"),
    ("Rental deposit of two months shall be held in a separate escrow account.", "normal"),
    ("The property shall be returned in the same condition as received, subject to fair wear and tear.", "normal"),
    ("The lessee shall not sublet the premises without prior written consent of the lessor.", "normal"),
    ("The employer shall pay the employee a monthly gross salary as agreed in Schedule A.", "normal"),
    ("The employee is entitled to 20 days of annual paid leave per calendar year.", "normal"),
    ("Either party may terminate the employment with one month notice during the probation period.", "normal"),
    ("The parties agree to resolve disputes through mediation before initiating court proceedings.", "normal"),
    ("The contractor shall provide the services on a best-efforts basis within agreed timelines.", "normal"),
    ("All deliverables shall conform to the specifications set out in Annexe 1.", "normal"),
    ("The total contract value shall not exceed EUR 50,000 without prior written approval.", "normal"),
    ("The parties shall keep all information exchanged under this agreement strictly confidential.", "normal"),
    ("This agreement is binding on the parties and their respective successors and assigns.", "normal"),
    ("Severability: if any provision is found invalid, the remaining provisions continue in force.", "normal"),
    ("The borrower shall repay the loan in equal monthly instalments over 36 months.", "normal"),
    ("Annual indexation shall follow the official consumer price index of Belgium.", "normal"),
]


# ── CSV loader ─────────────────────────────────────────────────────────────────

_VALID_LABELS = {"abusive_clause", "payment_risk", "missing_mandatory", "normal"}

def load_csv(csv_path: Path) -> list[tuple[str, str]]:
    """Load (text, label) pairs from a CSV file with 'text' and 'label' columns."""
    rows: list[tuple[str, str]] = []
    skipped = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not {"text", "label"}.issubset(reader.fieldnames or []):
            raise ValueError(f"CSV must have 'text' and 'label' columns, got: {reader.fieldnames}")
        for i, row in enumerate(reader, start=2):
            text  = row["text"].strip()
            label = row["label"].strip()
            if not text or label not in _VALID_LABELS:
                skipped += 1
                continue
            rows.append((text, label))
    if skipped:
        print(f"  [CSV] skipped {skipped} rows (empty text or unknown label)")
    return rows


# ── Train ──────────────────────────────────────────────────────────────────────

def train(save_path: Path, csv_path: Path | None = None) -> None:
    data = list(_DATA)

    if csv_path and csv_path.exists():
        csv_rows = load_csv(csv_path)
        print(f"CSV      : {csv_path} ({len(csv_rows)} rows loaded)")
        data.extend(csv_rows)
    elif csv_path:
        print(f"CSV      : {csv_path} not found — using synthetic data only")

    texts  = [d[0] for d in data]
    labels = [d[1] for d in data]

    label_set = sorted(set(labels))
    print(f"Classes : {label_set}")
    print(f"Samples : {len(texts)}")
    for lbl in label_set:
        print(f"  {lbl}: {labels.count(lbl)}")

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=8000,
            sublinear_tf=True,
            min_df=1,
        )),
        ("clf", MLPClassifier(
            hidden_layer_sizes=(128, 64),
            activation="relu",
            max_iter=800,
            random_state=42,
        )),
    ])

    print("\nTraining …")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print("\nValidation report:")
    print(classification_report(y_test, y_pred, labels=label_set, zero_division=0))

    train_acc = pipeline.score(X_train, y_train)
    test_acc  = pipeline.score(X_test, y_test)
    print(f"Train accuracy : {train_acc:.3f}")
    print(f"Test  accuracy : {test_acc:.3f}")

    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"\nSaved → {save_path}")


if __name__ == "__main__":
    default  = Path.home() / "Desktop/sydeco_ai_core_bundle/models/legal_mlp.pkl"
    out_path = Path(os.getenv("SYDECO_MLP_PATH", str(default)))

    default_csv = Path(__file__).parent.parent / "data" / "clause_training_data.csv"
    csv_env     = os.getenv("SYDECO_CSV_PATH")
    csv_path    = Path(csv_env) if csv_env else default_csv

    train(out_path, csv_path)
