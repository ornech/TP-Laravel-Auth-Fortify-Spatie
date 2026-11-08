#!/usr/bin/env python3
"""Garde-fou : vérifie les PDF générés (signets, liens internes, contenu interdit, images).

Contrôle aussi la page de garde (auteur, licence, mention de l'IA, version) et les propriétés du PDF.

Usage : python3 outils/verifier_pdf.py [dossier_du_depot] [dossier_des_pdf]
Code de sortie 1 si une vérification échoue.
"""
import re, sys, pathlib, warnings
from pypdf import PdfReader

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _commun  # configuration et informations Git

warnings.filterwarnings("ignore")
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
PDFS = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else REPO / "pdf").resolve()
TPS = ["tp1-authentification", "tp2-autorisation"]
META = _commun.charger_metadonnees(REPO)
GIT = _commun.infos_git(REPO)


def normaliser(t):
    return " ".join(t.split())
INTERDITS = ["[!NOTE]", "[!WARNING]", "Mémo —", "corrige", "corrigé", "AuthRbacTest"]  # le corrigé ne doit jamais fuiter

erreurs = []


def ko(tp, msg):
    erreurs.append(f"{tp}: {msg}")


def titres_attendus(tp):
    """Un chapitre par fichier markdown du TP (hors corrigé) : son premier titre H1."""
    out = []
    for f in sorted((REPO / tp).glob("*.md")):
        if f.name == "corrige.md":
            continue
        m = re.search(r"^# (.+)$", f.read_text(encoding="utf-8"), re.M)
        if m:
            out.append(re.sub(r"[*`]", "", m.group(1)).strip())
    return out


def images_attendues(tp):
    n = 0
    for f in (REPO / tp).glob("*.md"):
        if f.name != "corrige.md":
            n += len(re.findall(r"!\[[^\]]*\]\([^)]+\)", re.sub(r"```.*?```", "", f.read_text(encoding="utf-8"), flags=re.S)))
    return n


for tp in TPS:
    pdf = PDFS / f"{tp}.pdf"
    if not pdf.exists():
        ko(tp, "PDF absent"); continue
    r = PdfReader(str(pdf))
    pages = len(r.pages)
    if pages < 10:
        ko(tp, f"seulement {pages} pages")

    # --- signets (volet de navigation)
    titres = []
    def parcourir(noeuds):
        for x in noeuds:
            if isinstance(x, list): parcourir(x)
            else: titres.append(x.title)
    parcourir(r.outline)
    for t in titres_attendus(tp):
        if t not in titres:
            ko(tp, f"signet manquant : « {t} »")

    # --- liens internes : chaque lien doit pointer vers une page existante
    internes = 0
    for pg in r.pages:
        for a in pg.get("/Annots", []) or []:
            a = a.get_object()
            if a.get("/Subtype") != "/Link": continue
            dest = a.get("/Dest") or (a.get("/A", {}).get("/D") if a.get("/A", {}).get("/S") == "/GoTo" else None)
            if dest is None: continue
            internes += 1
            try:
                if isinstance(dest, str):
                    dest = r.named_destinations[dest]
                    num = r.get_destination_page_number(dest)
                else:
                    num = r.get_page_number(dest[0].get_object())
                if not (0 <= num < pages): raise ValueError
            except Exception:
                ko(tp, "lien interne vers une destination introuvable")
    if internes < 20:
        ko(tp, f"trop peu de liens internes ({internes})")

    # --- contenu interdit
    texte = "\n".join(p.extract_text() for p in r.pages)
    for mot in INTERDITS:
        if mot.lower() in texte.lower():
            ko(tp, f"contenu interdit dans le PDF : « {mot} »")

    # --- images
    # WeasyPrint déclare les images dans les ressources de chaque page : on compte les images DISTINCTES
    imgs = len({im.name for p in r.pages for im in p.images})
    if imgs < images_attendues(tp):
        ko(tp, f"{imgs} image(s) dans le PDF, {images_attendues(tp)} attendue(s)")

    # --- propriétés du PDF (auteur, titre, sujet, mots-clés)
    props = r.metadata or {}
    if props.get("/Author") != META["auteur"]["nom"]:
        ko(tp, f"propriété Auteur incorrecte : {props.get('/Author')!r}")
    for cle in ("/Title", "/Subject", "/Keywords"):
        if not props.get(cle):
            ko(tp, f"propriété {cle[1:]} vide")

    # --- page de garde : auteur, licence, mention de l'IA, commit (et version si un tag existe)
    garde = normaliser(r.pages[0].extract_text())
    attendus = [META["auteur"]["nom"], META["licence"]["nom"], GIT["court"], normaliser(META["ia"]["mention"])]
    if GIT["tag"]:
        attendus.append(GIT["tag"])
    for a in attendus:
        if a not in garde:
            ko(tp, f"page de garde : « {a[:50]}… » introuvable")
    # --- pied de page : le commit figure sur les pages courantes
    if pages > 3 and GIT["court"] not in normaliser(r.pages[2].extract_text()):
        ko(tp, "pied de page : commit absent")

    print(f"{tp}.pdf : {pages} pages, {len(titres)} signets, {internes} liens internes, {imgs} image(s)")

# --- la mention de l'IA du README racine doit être identique à celle de la page de garde
if normaliser(META["ia"]["mention"]) not in normaliser((REPO / "README.md").read_text(encoding="utf-8")):
    erreurs.append("README.md: la mention de l'IA est absente ou différente de celle de outils/metadonnees.toml")

if erreurs:
    print("\nÉCHEC :", *erreurs, sep="\n  - ")
    sys.exit(1)
print("Vérification des PDF : OK")
