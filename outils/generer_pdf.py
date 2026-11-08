#!/usr/bin/env python3
"""Génère un PDF par TP à partir des fichiers markdown.

Chaque PDF contient : une page de titre, un sommaire cliquable avec numéros de page,
des signets (volet de navigation du lecteur PDF) et des liens internes fonctionnels
entre les étapes. Les corrigés (corrige.md) ne sont JAMAIS inclus.

Usage : python3 outils/generer_pdf.py [dossier_du_depot] [dossier_de_sortie]
Prérequis : pip install -r outils/requirements-pdf.txt (et, sous Linux, les bibliothèques
Pango : voir le workflow .github/workflows/pdf.yml).

La génération ÉCHOUE (code de sortie 1) si un lien interne ou une image est cassé.
"""
import re, sys, html, datetime, pathlib, unicodedata, logging
from markdown_it import MarkdownIt
from pygments import highlight as pyg_highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
from weasyprint import HTML, CSS

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _commun  # configuration, informations Git, versions de référence

REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else REPO / "pdf").resolve()


class Collecteur(logging.Handler):
    """Conserve les avertissements de WeasyPrint (ancres introuvables, images manquantes…)."""
    def __init__(self):
        super().__init__(); self.messages = []
    def emit(self, record):
        self.messages.append(record.getMessage())


COLLECTEUR = Collecteur()
logging.getLogger("weasyprint").addHandler(COLLECTEUR)
logging.getLogger("weasyprint").setLevel(logging.WARNING)
GITHUB = "https://github.com/ornech/TP-Laravel-Auth-Fortify-Spatie/blob/main/"

TPS = {
    "tp1-authentification": "TP 1 : Authentification avec Laravel Fortify",
    "tp2-autorisation": "TP 2 : Autorisation avec Spatie",
}
FIN = ["contrat-de-tests.md", "depannage.md", "bilan.md"]  # corrige.md exclu volontairement


def fold(text):
    """Identifiant ASCII stable (sans accents) pour les ancres."""
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^\w\- ]", "", t.lower()).strip().replace(" ", "-")
    return re.sub(r"-+", "-", t) or "section"


def hl(code, lang, attrs):
    try:
        lexer = get_lexer_by_name(lang) if lang else TextLexer()
    except Exception:
        lexer = TextLexer()
    body = pyg_highlight(code, lexer, HtmlFormatter(nowrap=True))
    return f'<pre class="code"><code>{body}</code></pre>'


def inline_text(tok):
    return "".join(c.content for c in (tok.children or []) if c.type in ("text", "code_inline"))


def fichiers_du_tp(tp):
    d = REPO / tp
    etapes = sorted(d.glob("etape-*.md"), key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)))
    return [d / "README.md", *etapes, *[d / f for f in FIN]]


def convertir(tp, titre_tp, meta, git, versions):
    d = REPO / tp
    files = fichiers_du_tp(tp)
    ids = {f.name: "ch-" + fold(f.stem) for f in files}  # README.md -> ch-readme
    md = MarkdownIt("commonmark", {"html": False, "highlight": hl}).enable("table").enable("strikethrough")
    chapitres, toc, liens_externes = [], [], 0

    for f in files:
        fid = ids[f.name]
        tokens = md.parse(f.read_text(encoding="utf-8"))
        if f.name == "README.md":  # le sommaire du README est remplacé par le sommaire généré
            debut = next((k for k, t in enumerate(tokens) if t.type == "heading_open"
                          and inline_text(tokens[k + 1]) == "Sommaire"), None)
            if debut is not None:
                fin = next((k for k in range(debut + 1, len(tokens)) if tokens[k].type == "heading_open"), len(tokens))
                del tokens[debut:fin]
        vus, premier_h1 = {}, True
        i = 0
        while i < len(tokens):
            t = tokens[i]
            # ---- titres : identifiants uniques par fichier, un seul H1 par chapitre
            if t.type == "heading_open":
                niveau = int(t.tag[1])
                texte = inline_text(tokens[i + 1])
                if niveau == 1 and premier_h1:
                    t.attrSet("id", fid); premier_h1 = False
                    toc.append((1, texte, fid))
                else:
                    if niveau == 1:
                        niveau = 2; t.tag = "h2"; tokens[i + 2].tag = "h2"
                    base = f"{fid}-{fold(texte)}"
                    n = vus.get(base, 0); vus[base] = n + 1
                    ident = base if n == 0 else f"{base}-{n}"
                    t.attrSet("id", ident)
                    if niveau == 2:
                        toc.append((2, texte, ident))
            # ---- encadrés GitHub : > [!NOTE] / > [!WARNING]
            if t.type == "blockquote_open" and tokens[i + 1].type == "paragraph_open":
                inl = tokens[i + 2]
                m = re.match(r"\[!(NOTE|WARNING)\]\s*", inl.content)
                if m:
                    genre = m.group(1).lower()
                    t.attrSet("class", f"alert {genre}")
                    t.attrSet("data-titre", "Note" if genre == "note" else "Attention")
                    ch = inl.children
                    while ch and (ch[0].type == "softbreak" or "[!" in ch[0].content or ch[0].content.strip() == ""):
                        ch.pop(0)
                        if ch and ch[0].type == "softbreak": ch.pop(0); break
                    inl.content = inl.content[m.end():]
            # ---- liens et images
            if t.type == "inline":
                for c in t.children:
                    if c.type == "link_open":
                        href = c.attrGet("href") or ""
                        if href.startswith("#"):
                            c.attrSet("href", "#" + fid + "-" + fold(href[1:]))
                        elif re.match(r"https?://", href):
                            liens_externes += 1
                        else:
                            chemin, _, ancre = href.partition("#")
                            cible = (d / chemin).resolve()
                            if cible.parent == d.resolve() and cible.name in ids:
                                c.attrSet("href", "#" + ids[cible.name] + (("-" + fold(ancre)) if ancre else ""))
                            elif cible.suffix == ".md":  # autre TP : lien vers GitHub
                                c.attrSet("href", GITHUB + str(cible.relative_to(REPO)))
                                liens_externes += 1
                    elif c.type == "image":
                        c.attrSet("src", (d / c.attrGet("src")).resolve().as_uri())
            i += 1
        corps = md.renderer.render(tokens, md.options, {})
        # étiquette d'encadré (Note / Attention) insérée devant le contenu
        corps = re.sub(r'<blockquote class="alert (note|warning)" data-titre="([^"]+)">',
                       lambda m: f'<blockquote class="alert {m.group(1)}"><p class="alert-titre">{m.group(2)}</p>', corps)
        chapitres.append(f'<section class="chapitre">{corps}</section>')

    sommaire = "".join(
        f'<li class="niv{n}"><a href="#{ident}">{html.escape(txt)}</a></li>' for n, txt, ident in toc
    )
    e = html.escape
    aut, doc_m, lic, ia = meta["auteur"], meta["document"], meta["licence"], meta["ia"]
    version = _commun.libelle_version(git) + (" (modifications locales non commitées)" if git["modifie"] else "")
    lien_commit = f'{doc_m["depot"]}/commit/{git["sha"]}' if git["sha"] else doc_m["depot"]
    ligne = lambda k, v: f"<tr><th>{k}</th><td>{v}</td></tr>"
    infos = "".join([
        ligne("Auteur", f'{e(aut["nom"])}, {e(aut["fonction"].lower())}'),
        ligne("Public visé", e(doc_m["public"])),
        ligne("Version", e(version)),
        ligne("Commit", f'<a href="{e(lien_commit)}">{e(git["court"])}</a>, le {e(git["date_fr"])}'),
        ligne("Versions de référence", e(" · ".join(versions))),
        ligne("Dépôt", f'<a href="{e(doc_m["depot"])}">{e(doc_m["depot"])}</a>'),
        ligne("Licence", f'<a href="{e(lic["url"])}">{e(lic["nom"])}</a> : {e(lic["resume"])}'),
    ])
    date = datetime.date.today().strftime("%d/%m/%Y")
    description = f"{titre_tp}" + (f". Version {git['tag']}" if git["tag"] and git["distance"] == 0 else "") + f". Commit {git['court']}, {git['date_fr']}."
    metas = f"""<meta name="author" content="{e(aut['nom'])}">
<meta name="description" content="{e(description)}">
<meta name="keywords" content="{e(doc_m['mots_cles'])}">
<meta name="generator" content="WeasyPrint, outils/generer_pdf.py (commit {e(git['court'])})">
<meta name="dcterms.created" content="{e(git['date_iso'])}">"""
    doc = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>{e(titre_tp)}</title>
{metas}</head><body>
<section class="couverture"><p class="serie">Authentification et autorisation avec Laravel 13</p>
<h1 class="titre-doc" style="bookmark-level:none">{e(titre_tp)}</h1>
<table class="infos">{infos}</table>
<blockquote class="alert note"><p class="alert-titre">{e(ia["titre"])}</p><p>{e(ia["mention"])}</p></blockquote>
<p class="date">PDF généré le {date}</p></section>
<section class="sommaire"><h1 style="bookmark-level:none">Sommaire</h1><nav class="toc"><ul>{sommaire}</ul></nav></section>
{''.join(chapitres)}
</body></html>"""
    return doc, d, liens_externes


CSS_TEXTE = """
@page { size: A4; margin: 20mm 17mm 20mm 17mm;
  @bottom-center { content: counter(page) " / " counter(pages); font-size: 8pt; color: #666; }
  @bottom-left { content: "__PIED__"; font-size: 8pt; color: #666; }
  @top-right { content: string(chapitre); font-size: 8pt; color: #666; } }
@page :first { @top-right { content: none; } @bottom-center { content: none; } @bottom-left { content: none; } }
html { font-family: "Liberation Sans", "DejaVu Sans", sans-serif; font-size: 10pt; line-height: 1.45; color: #1f2328; }
h1 { font-size: 20pt; margin: 0 0 10pt; border-bottom: 2px solid #d0d7de; padding-bottom: 4pt; string-set: chapitre content(text); }
h2 { font-size: 14pt; margin: 16pt 0 6pt; border-bottom: 1px solid #d0d7de; padding-bottom: 2pt; }
h3 { font-size: 12pt; margin: 12pt 0 4pt; } h1, h2, h3 { break-after: avoid; }
p { margin: 5pt 0; } a { color: #0969da; text-decoration: none; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.5pt; background: #eff1f3; padding: 0 2pt; border-radius: 2pt; }
pre.code { white-space: pre-wrap; overflow-wrap: anywhere; background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 4pt; padding: 6pt 8pt; font-size: 8pt; line-height: 1.35; margin: 6pt 0; }
pre.code code { background: none; padding: 0; font-size: 8pt; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9pt; }
th, td { border: 1px solid #d0d7de; padding: 3pt 5pt; vertical-align: top; } th { background: #f6f8fa; } tr { break-inside: avoid; }
blockquote { margin: 8pt 0; padding: 4pt 10pt; border-left: 4pt solid #d0d7de; color: #444; }
blockquote.alert { background: #f6f8fa; break-inside: avoid; color: #1f2328; }
blockquote.note { border-left-color: #0969da; background: #ddf4ff; } blockquote.warning { border-left-color: #bf8700; background: #fff8c5; }
.alert-titre { font-weight: bold; margin: 2pt 0; } blockquote.note .alert-titre { color: #0969da; } blockquote.warning .alert-titre { color: #9a6700; }
img { max-width: 100%; }
.chapitre { break-before: page; } .couverture { padding-top: 28mm; }
.serie { color: #57606a; font-size: 12pt; margin: 0 0 4pt; text-transform: uppercase; letter-spacing: 1pt; }
.titre-doc { font-size: 27pt; border: none; string-set: none; margin: 0 0 16mm; }
table.infos { width: 100%; font-size: 10pt; margin: 0 0 8mm; }
table.infos th { width: 33%; text-align: left; background: #f6f8fa; } .couverture blockquote.alert { font-size: 9.5pt; }
.date { color: #666; margin-top: 12mm; font-size: 9pt; }
.sommaire { break-before: page; } nav.toc ul { list-style: none; padding: 0; margin: 0; }
nav.toc li { margin: 2pt 0; } nav.toc li.niv1 { margin-top: 8pt; font-weight: bold; } nav.toc li.niv2 { margin-left: 14pt; font-size: 9pt; }
nav.toc a { color: #1f2328; } nav.toc a::after { content: leader('.') target-counter(attr(href), page); font-weight: normal; }
ul, ol { margin: 4pt 0; padding-left: 18pt; } li { margin: 1pt 0; }
"""

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    pyg_css = HtmlFormatter().get_style_defs("pre.code")
    meta = _commun.charger_metadonnees(REPO)
    git = _commun.infos_git(REPO)
    versions = _commun.versions_reference(REPO)
    print(f"version : {_commun.libelle_version(git)} · commit {git['court']} · {git['date_fr']}")
    for tp, titre in TPS.items():
        doc, base, ext = convertir(tp, titre, meta, git, versions)
        pdf = OUT / f"{tp}.pdf"
        court = titre.split(":")[0].strip()  # « TP 1 »
        pied = " · ".join(x for x in (court, _commun.version_courte(git), git["court"]) if x)
        css = CSS_TEXTE.replace("__PIED__", pied.replace("\\", "\\\\").replace('"', '\\"'))
        HTML(string=doc, base_url=str(base) + "/").write_pdf(str(pdf), stylesheets=[CSS(string=css + pyg_css)])
        print(f"{pdf}  ({pdf.stat().st_size // 1024} Ko, {ext} lien(s) externe(s))")
    graves = [m for m in COLLECTEUR.messages if re.search(r"anchor|image|failed|not found|URL", m, re.I)]
    autres = [m for m in COLLECTEUR.messages if m not in graves]
    for m in autres:
        print("avertissement :", m)
    if graves:
        print("\nERREUR : liens ou images cassés :", *graves, sep="\n  - ")
        sys.exit(1)
