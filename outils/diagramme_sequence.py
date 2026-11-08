#!/usr/bin/env python3
"""Génère un diagramme de séquence UML (SVG, puis PNG si Inkscape est installé) à partir
d'une description textuelle. Aucune dépendance Python.

Usage : python3 outils/diagramme_sequence.py chemin/vers/diagramme.seq

Format du fichier .seq (une instruction par ligne, « # » pour un commentaire) :

    titre: Texte du titre
    participant N = Navigateur              # un acteur (boîte)
    participant B = Base de données [base]  # [base] : dessiné comme une base de données
    N -> L : Texte du message               # demande (flèche pleine)
    L --> N : Texte de la réponse           # réponse (flèche en pointillés)
    L -> L : Texte d'un traitement interne  # message à soi-même
    == Texte du séparateur ==               # coupure horizontale
    note over N,L : Texte de la note        # note en travers de un ou deux acteurs
"""
import re, sys, shutil, subprocess, pathlib
from xml.sax.saxutils import escape

POLICE = "DejaVu Sans, Liberation Sans, Arial, sans-serif"
TAILLE = 12
LARGEUR_CAR = 6.9           # largeur moyenne d'un caractère à 12 px (estimation pour le retour à la ligne)
INTERLIGNE = 15
ESPACE = 380                # distance entre deux lignes de vie
MARGE = 40
LARGEUR_BOITE = 190
HAUTEUR_BOITE = 40


def couper(texte, largeur_px):
    """Retour à la ligne par mots, d'après une largeur estimée."""
    maxi = max(8, int(largeur_px / LARGEUR_CAR))
    lignes, cour = [], ""
    for mot in texte.split():
        if cour and len(cour) + 1 + len(mot) > maxi:
            lignes.append(cour); cour = mot
        else:
            cour = (cour + " " + mot).strip()
    return lignes + ([cour] if cour else [])


def lire(chemin):
    titre, parts, ordre, evts = "", {}, [], []
    for brut in pathlib.Path(chemin).read_text(encoding="utf-8").splitlines():
        l = brut.split("  #")[0].strip()
        if not l or l.startswith("#"):
            continue
        if l.startswith("titre:"):
            titre = l[6:].strip()
        elif l.startswith("participant "):
            m = re.match(r"participant (\w+) = (.+?)(?: \[(base)\])?$", l)
            parts[m.group(1)] = (m.group(2), m.group(3) or "acteur"); ordre.append(m.group(1))
        elif l.startswith("=="):
            evts.append(("sep", l.strip("= ").strip()))
        elif l.startswith("note over"):
            m = re.match(r"note over (\w+)(?:,(\w+))? : (.+)", l)
            evts.append(("note", m.group(1), m.group(2) or m.group(1), m.group(3)))
        else:
            m = re.match(r"(\w+) (-->|->) (\w+) : (.+)", l)
            if not m: raise SystemExit(f"Ligne non comprise : {brut!r}")
            evts.append(("msg", m.group(1), m.group(3), m.group(4), m.group(2) == "-->"))
    return titre, parts, ordre, evts


def dessiner(titre, parts, ordre, evts):
    x = {p: MARGE + LARGEUR_BOITE / 2 + i * ESPACE for i, p in enumerate(ordre)}
    largeur = MARGE * 2 + LARGEUR_BOITE + (len(ordre) - 1) * ESPACE
    y = MARGE + (28 if titre else 0)
    haut_boites = y
    y += HAUTEUR_BOITE + 22
    corps = []

    for e in evts:
        if e[0] == "msg":
            _, a, b, texte, retour = e
            if a == b:  # message à soi-même : boucle à droite de la ligne de vie
                lignes = couper(texte, ESPACE - 50)
                h = max(26, len(lignes) * INTERLIGNE + 8)
                xa = x[a]
                corps.append(f'<path d="M{xa},{y} h46 v{h - 8} h-46" fill="none" stroke="#24292f" stroke-width="1.4" marker-end="url(#fleche)"/>')
                for k, ln in enumerate(lignes):
                    corps.append(f'<text x="{xa + 54}" y="{y + 12 + k * INTERLIGNE}" font-size="{TAILLE}">{escape(ln)}</text>')
                y += h + 22
            else:
                gauche, droite = sorted((x[a], x[b]))
                lignes = couper(texte, droite - gauche - 24)
                for k, ln in enumerate(lignes):
                    corps.append(f'<text x="{(gauche + droite) / 2}" y="{y + 11 + k * INTERLIGNE}" font-size="{TAILLE}" text-anchor="middle">{escape(ln)}</text>')
                ya = y + len(lignes) * INTERLIGNE + 8
                x1, x2 = (x[a] + (0 if a == ordre[0] else 0), x[b])
                dash = ' stroke-dasharray="7,5"' if retour else ""
                marque = "ouverte" if retour else "fleche"
                corps.append(f'<line x1="{x1}" y1="{ya}" x2="{x2}" y2="{ya}" stroke="#24292f" stroke-width="1.4"{dash} marker-end="url(#{marque})"/>')
                y = ya + 24
        elif e[0] == "sep":
            lignes = couper(e[1], 560)
            larg_txt = max(len(l) for l in lignes) * LARGEUR_CAR + 28
            corps.append(f'<line x1="{MARGE / 2}" y1="{y + 10}" x2="{largeur - MARGE / 2}" y2="{y + 10}" stroke="#8c959f" stroke-width="1" stroke-dasharray="2,3"/>')
            corps.append(f'<rect x="{largeur / 2 - larg_txt / 2}" y="{y - 2}" width="{larg_txt}" height="24" rx="4" fill="#eaeef2" stroke="#8c959f"/>')
            corps.append(f'<text x="{largeur / 2}" y="{y + 15}" font-size="{TAILLE}" font-weight="bold" text-anchor="middle">{escape(e[1])}</text>')
            y += 44
        elif e[0] == "note":
            _, a, b, texte = e
            gauche, droite = sorted((x[a], x[b]))
            gauche -= 70 if a == b else 0; droite += 70 if a == b else 0
            lignes = couper(texte, droite - gauche - 24)
            h = len(lignes) * INTERLIGNE + 14
            corps.append(f'<rect x="{gauche}" y="{y}" width="{droite - gauche}" height="{h}" fill="#fff8c5" stroke="#bf8700" rx="3"/>')
            for k, ln in enumerate(lignes):
                corps.append(f'<text x="{(gauche + droite) / 2}" y="{y + 18 + k * INTERLIGNE}" font-size="{TAILLE}" text-anchor="middle">{escape(ln)}</text>')
            y += h + 22

    bas = y
    entete = []
    if titre:
        entete.append(f'<text x="{largeur / 2}" y="{MARGE - 6}" font-size="15" font-weight="bold" text-anchor="middle">{escape(titre)}</text>')
    for p in ordre:
        nom, genre = parts[p]
        cx, lignes = x[p], couper(nom, LARGEUR_BOITE - 16)
        entete.append(f'<line x1="{cx}" y1="{haut_boites + HAUTEUR_BOITE}" x2="{cx}" y2="{bas}" stroke="#8c959f" stroke-width="1.2" stroke-dasharray="6,5"/>')
        gx = cx - LARGEUR_BOITE / 2
        if genre == "base":  # cylindre
            h, r = HAUTEUR_BOITE, 7
            entete.append(f'<path d="M{gx},{haut_boites + r} v{h - 2 * r} a{LARGEUR_BOITE / 2},{r} 0 0 0 {LARGEUR_BOITE},0 v{-(h - 2 * r)} a{LARGEUR_BOITE / 2},{r} 0 0 0 {-LARGEUR_BOITE},0 z" fill="#f6f8fa" stroke="#57606a" stroke-width="1.4"/>')
            entete.append(f'<path d="M{gx},{haut_boites + r} a{LARGEUR_BOITE / 2},{r} 0 0 0 {LARGEUR_BOITE},0" fill="none" stroke="#57606a" stroke-width="1.4"/>')
        else:
            entete.append(f'<rect x="{gx}" y="{haut_boites}" width="{LARGEUR_BOITE}" height="{HAUTEUR_BOITE}" rx="5" fill="#ddf4ff" stroke="#0969da" stroke-width="1.4"/>')
        decal = haut_boites + HAUTEUR_BOITE / 2 + 4 - (len(lignes) - 1) * INTERLIGNE / 2 + (4 if genre == "base" else 0)
        for k, ln in enumerate(lignes):
            entete.append(f'<text x="{cx}" y="{decal + k * INTERLIGNE}" font-size="13" font-weight="bold" text-anchor="middle">{escape(ln)}</text>')

    hauteur = bas + MARGE
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{largeur}" height="{hauteur}" viewBox="0 0 {largeur} {hauteur}" font-family="{POLICE}" fill="#24292f">
<defs>
<marker id="fleche" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#24292f"/></marker>
<marker id="ouverte" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10" fill="none" stroke="#24292f" stroke-width="1.5"/></marker>
</defs>
<rect width="100%" height="100%" fill="#ffffff"/>
{chr(10).join(entete)}
{chr(10).join(corps)}
</svg>
'''


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    src = pathlib.Path(sys.argv[1])
    svg = src.with_suffix(".svg")
    svg.write_text(dessiner(*lire(src)), encoding="utf-8")
    print("SVG :", svg)
    png = src.with_suffix(".png")
    ink = shutil.which("inkscape")
    if ink:
        subprocess.run([ink, str(svg), "--export-type=png", "--export-dpi=192", f"--export-filename={png}"],
                       check=True, capture_output=True)
        print("PNG :", png)
    else:
        print("Inkscape absent : seul le SVG a été produit.")
