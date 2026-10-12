import requests
import sqlite3
import csv
import time
from datetime import datetime

try:
    from config import API_KEY
except ImportError:
    API_KEY = "YOUR_APOLLO_API_KEY"

BASE_URL = "https://api.apollo.io/api/v1"
HEADERS  = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

# ─────────────────────────────────────────
#  BASE DE DONNÉES
# ─────────────────────────────────────────
def init_db():
    conn   = sqlite3.connect("crm.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            genre               TEXT,
            prenom              TEXT,
            nom                 TEXT,
            entreprise          TEXT,
            pays                TEXT,
            ville               TEXT,
            titre_poste         TEXT,
            secteur             TEXT,
            telephone_perso     TEXT,
            telephone_standard  TEXT,
            email               TEXT,
            linkedin            TEXT,
            date_ajout          TEXT
        )
    """)
    conn.commit()
    return conn


# ─────────────────────────────────────────
#  EXTRAIRE LES CHAMPS
# ─────────────────────────────────────────
def extract_person(p):
    full_name = p.get("name") or ""
    parts     = full_name.strip().split(" ", 1)
    prenom    = parts[0] if len(parts) > 0 else ""
    nom       = parts[1] if len(parts) > 1 else ""

    gender_raw = (p.get("gender") or "").lower()
    genre = "M" if gender_raw == "male" else ("F" if gender_raw == "female" else "")

    org         = p.get("organization") or {}
    entreprise  = org.get("name") or p.get("organization_name") or ""
    pays        = p.get("country") or p.get("location_country") or ""
    ville       = p.get("city")    or p.get("location_city")    or ""
    titre_poste = p.get("title") or ""
    secteur     = org.get("industry") or p.get("industry") or ""

    tel_perso    = ""
    tel_standard = ""
    phones = p.get("phone_numbers") or []
    for ph in phones:
        t   = (ph.get("type") or "").lower()
        num = ph.get("sanitized_number") or ph.get("raw_number") or ""
        if "mobile" in t or "direct" in t:
            tel_perso = tel_perso or num
        elif "work" in t or "company" in t or "hq" in t:
            tel_standard = tel_standard or num
    if not tel_perso and not tel_standard:
        tel_perso = p.get("phone") or ""

    email    = p.get("email") or ""
    linkedin = p.get("linkedin_url") or ""

    return {
        "genre": genre, "prenom": prenom, "nom": nom,
        "entreprise": entreprise, "pays": pays, "ville": ville,
        "titre_poste": titre_poste, "secteur": secteur,
        "telephone_perso": tel_perso, "telephone_standard": tel_standard,
        "email": email, "linkedin": linkedin,
    }


# ─────────────────────────────────────────
#  SAUVEGARDER DANS SQLITE
# ─────────────────────────────────────────
def save_to_db(conn, people):
    cursor  = conn.cursor()
    saved   = 0
    skipped = 0
    for p in people:
        d = extract_person(p)
        if d["email"]:
            cursor.execute("SELECT id FROM leads WHERE email=?", (d["email"],))
        else:
            cursor.execute(
                "SELECT id FROM leads WHERE prenom=? AND nom=? AND entreprise=?",
                (d["prenom"], d["nom"], d["entreprise"])
            )
        if cursor.fetchone():
            skipped += 1
            continue
        cursor.execute("""
            INSERT INTO leads (
                genre, prenom, nom, entreprise, pays, ville,
                titre_poste, secteur, telephone_perso, telephone_standard,
                email, linkedin, date_ajout
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            d["genre"], d["prenom"], d["nom"], d["entreprise"],
            d["pays"], d["ville"], d["titre_poste"], d["secteur"],
            d["telephone_perso"], d["telephone_standard"],
            d["email"], d["linkedin"],
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))
        saved += 1
    conn.commit()
    return saved, skipped


# ─────────────────────────────────────────
#  ÉTAPE 1 : trouver l'ID de l'entreprise
# ─────────────────────────────────────────
def get_org_id(nom_entreprise):
    r = requests.post(
        f"{BASE_URL}/mixed_companies/search",
        headers=HEADERS,
        json={"q_organization_name": nom_entreprise, "per_page": 5}
    )
    if r.status_code != 200:
        print(f"  [ERREUR {r.status_code}] {r.text[:300]}")
        return None, None

    orgs = r.json().get("organizations", [])
    if not orgs:
        print(f"  Entreprise '{nom_entreprise}' introuvable sur Apollo.")
        return None, None

    # afficher les choix si plusieurs résultats
    if len(orgs) > 1:
        print(f"\n  Plusieurs entreprises trouvées :")
        for i, o in enumerate(orgs):
            print(f"  {i+1}. {o.get('name')} — {o.get('primary_domain','?')} — {o.get('country','?')}")
        choix = input("\n  Laquelle ? (numéro) : ").strip()
        try:
            org = orgs[int(choix)-1]
        except:
            org = orgs[0]
    else:
        org = orgs[0]

    print(f"\n  Entreprise sélectionnée : {org.get('name')} ({org.get('primary_domain','?')})")
    return org.get("id"), org.get("name")


# ─────────────────────────────────────────
#  ÉTAPE 2 : scraper les contacts via people/search
#  endpoint accessible sur plan gratuit
# ─────────────────────────────────────────
def scrape_by_org_id(conn, org_id, org_name, keywords=None):
    print(f"\n  Scraping de '{org_name}' en cours...\n")

    page        = 1
    total_saved = 0
    total_skip  = 0
    total_found = 0

    while True:
        payload = {
            "organization_ids": [org_id],
            "per_page": 100,
            "page": page
        }
        # filtre métier optionnel (ex: "regulatory affairs")
        if keywords:
            payload["q_keywords"] = keywords

        r = requests.post(
            f"{BASE_URL}/people/search",
            headers=HEADERS,
            json=payload
        )

        if r.status_code == 403:
            print(f"  [PLAN GRATUIT] L'endpoint people/search nécessite un plan payant.")
            print(f"  → Bascule sur la méthode alternative (enrichissement individuel)...\n")
            scrape_via_enrich(conn, org_name, keywords)
            return

        if r.status_code != 200:
            print(f"  [ERREUR {r.status_code}] {r.text[:300]}")
            break

        data          = r.json()
        people        = data.get("people", [])
        pagination    = data.get("pagination", {})
        total_entries = pagination.get("total_entries", 0)

        if not people:
            break

        total_found = total_entries
        print(f"  Page {page} — {len(people)} contacts "
              f"(total : {total_entries})")

        saved, skipped = save_to_db(conn, people)
        total_saved += saved
        total_skip  += skipped
        print(f"         → {saved} ajouté(s), {skipped} doublon(s)")

        total_pages = pagination.get("total_pages", 1)
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.5)

    print(f"\n  ✓ Scraping terminé.")
    print(f"    Contacts Apollo  : {total_found}")
    print(f"    Ajoutés CRM      : {total_saved}")
    print(f"    Doublons ignorés : {total_skip}\n")


# ─────────────────────────────────────────
#  MÉTHODE ALTERNATIVE — endpoint /people/match
#  fonctionne sur plan gratuit pour enrichir
#  un contact connu (nom + entreprise)
# ─────────────────────────────────────────
def scrape_via_enrich(conn, org_name, keywords=None):
    print(f"  Méthode enrichissement — recherche Google + Apollo /people/match\n")
    print(f"  Entre les noms des personnes à enrichir (un par ligne).")
    print(f"  Laisse vide et appuie Entrée pour terminer.\n")

    saved_total = 0
    while True:
        full_name = input("  Nom complet (ex: Jean Dupont) : ").strip()
        if not full_name:
            break

        parts  = full_name.split(" ", 1)
        prenom = parts[0]
        nom    = parts[1] if len(parts) > 1 else ""

        payload = {
            "first_name":        prenom,
            "last_name":         nom,
            "organization_name": org_name,
            "reveal_personal_emails": False
        }

        r = requests.post(
            f"{BASE_URL}/people/match",
            headers=HEADERS,
            json=payload
        )

        if r.status_code == 200:
            person = r.json().get("person")
            if person:
                saved, _ = save_to_db(conn, [person])
                d = extract_person(person)
                print(f"  ✓ Trouvé : {d['prenom']} {d['nom']} | {d['titre_poste']} | {d['email'] or 'email non dispo'}")
                saved_total += saved
            else:
                print(f"  — Aucun profil trouvé pour '{full_name}' chez {org_name}")
        else:
            print(f"  [ERREUR {r.status_code}] {r.text[:200]}")

        time.sleep(0.3)

    print(f"\n  ✓ {saved_total} contact(s) ajouté(s) au CRM.\n")


# ─────────────────────────────────────────
#  SCRAPER UNE ENTREPRISE COMPLÈTE
# ─────────────────────────────────────────
def scrape_entreprise(conn):
    nom = input("\n  Nom de l'entreprise : ").strip()
    if not nom:
        print("  Nom vide, annulé.\n")
        return

    kw = input("  Filtre métier (ex: regulatory affairs) [Entrée pour ignorer] : ").strip()
    keywords = kw or None

    org_id, org_name = get_org_id(nom)
    if not org_id:
        return

    scrape_by_org_id(conn, org_id, org_name, keywords)


# ─────────────────────────────────────────
#  AFFICHER LE CRM
# ─────────────────────────────────────────
def show_crm(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT genre, prenom, nom, entreprise, pays, ville,
               titre_poste, secteur, telephone_perso, telephone_standard,
               email, linkedin
        FROM leads ORDER BY entreprise, nom
    """)
    rows = cursor.fetchall()
    if not rows:
        print("\n  CRM vide.\n")
        return

    sep    = "─" * 72
    labels = ["Genre","Prénom","Nom","Entreprise","Pays","Ville",
              "Poste","Secteur","Tél perso","Tél standard","Email","LinkedIn"]
    print(f"\n{sep}")
    for r in rows:
        for label, val in zip(labels, r):
            print(f"  {label:<14}: {val or '—'}")
        print(sep)

    cursor.execute("SELECT COUNT(*) FROM leads")
    print(f"  Total : {cursor.fetchone()[0]} contact(s)\n")


# ─────────────────────────────────────────
#  EXPORT CSV
# ─────────────────────────────────────────
def export_csv(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT genre, prenom, nom, entreprise, pays, ville,
               titre_poste, secteur, telephone_perso, telephone_standard,
               email, linkedin, date_ajout
        FROM leads ORDER BY entreprise, nom
    """)
    rows = cursor.fetchall()
    if not rows:
        print("\n  CRM vide, rien à exporter.\n")
        return

    filename = f"export_crm_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "Genre","Prénom","Nom","Entreprise","Pays","Ville",
            "Titre du poste","Secteur d'activité",
            "Téléphone personnel (06)","Téléphone standard entreprise",
            "Email entreprise","Lien LinkedIn","Date ajout"
        ])
        writer.writerows(rows)
    print(f"\n  [OK] {len(rows)} contact(s) → {filename}\n")


# ─────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────
def menu():
    conn = init_db()
    print("\n" + "="*52)
    print("    APOLLO CRM — Affaires Réglementaires")
    print("="*52 + "\n")

    while True:
        print("1. Scraper une entreprise complète")
        print("2. Enrichir un contact (nom + entreprise)")
        print("3. Voir le CRM local")
        print("4. Exporter en CSV")
        print("5. Quitter")
        choix = input("\nChoix : ").strip()

        if choix == "1":
            scrape_entreprise(conn)
        elif choix == "2":
            org = input("\n  Nom de l'entreprise : ").strip()
            scrape_via_enrich(conn, org)
        elif choix == "3":
            show_crm(conn)
        elif choix == "4":
            export_csv(conn)
        elif choix == "5":
            print("\n  Au revoir !\n")
            conn.close()
            break
        else:
            print("  Choix invalide.\n")

if __name__ == "__main__":
    menu()