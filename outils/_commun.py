"""Fonctions partagées par generer_pdf.py et verifier_pdf.py : configuration, informations Git,
versions de référence."""
import re, subprocess, pathlib

try:  # Python 3.11 et plus
    import tomllib
except ModuleNotFoundError:  # Python 3.10 : paquet « tomli », même interface
    import tomli as tomllib


def charger_metadonnees(repo):
    """Lit outils/metadonnees.toml (auteur, licence, mention de l'IA…)."""
    return tomllib.loads((pathlib.Path(repo) / "outils" / "metadonnees.toml").read_text(encoding="utf-8"))


def _git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def infos_git(repo):
    """Commit, date et version du dépôt. La version est le dernier tag « vX.Y » : le tag
    « pdf-latest » de la release est volontairement ignoré (--match 'v[0-9]*')."""
    tag = _git(repo, "describe", "--tags", "--match", "v[0-9]*", "--abbrev=0")
    distance = int(_git(repo, "rev-list", "--count", f"{tag}..HEAD") or 0) if tag else 0
    return {
        "sha": _git(repo, "rev-parse", "HEAD"),
        "court": _git(repo, "rev-parse", "--short=7", "HEAD") or "inconnu",
        "date_iso": _git(repo, "show", "-s", "--format=%cI", "HEAD"),
        "date_fr": _git(repo, "show", "-s", "--format=%cd", "--date=format:%d/%m/%Y", "HEAD"),
        "tag": tag,
        "distance": distance,
        "modifie": bool(_git(repo, "status", "--porcelain", "--untracked-files=no")),  # seulement hors CI
    }


def libelle_version(g):
    """Texte complet de la version, pour la page de garde."""
    if not g["tag"]:
        return "non numérotée (aucun tag de version pour l'instant)"
    if g["distance"] == 0:
        return g["tag"]
    s = "s" if g["distance"] > 1 else ""
    return f"{g['tag']} + {g['distance']} commit{s}"


def version_courte(g):
    """Version compacte, pour le pied de page."""
    if not g["tag"]:
        return ""
    return g["tag"] if g["distance"] == 0 else f"{g['tag']}+{g['distance']}"


def versions_reference(repo):
    """Versions de référence lues dans le README racine (une seule source de vérité)."""
    txt = (pathlib.Path(repo) / "README.md").read_text(encoding="utf-8")
    bloc = txt.split("Versions de référence", 1)[1]
    out = []
    for nom, ver in re.findall(r"^- (.+?) : (\S+)\s*$", bloc, re.M):
        out.append(f"{nom.replace('Laravel Framework', 'Laravel')} {ver}")
    return out
