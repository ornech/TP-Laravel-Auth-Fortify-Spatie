# Outils

Génération des PDF des deux TP. En temps normal, **vous n'avez rien à faire** : le workflow
`.github/workflows/pdf.yml` s'exécute à chaque mise à jour des TP et publie les PDF dans la release
`pdf-latest` (voir le README à la racine).

| Fichier | Rôle |
| --- | --- |
| generer_pdf.py | Convertit les fichiers markdown d'un TP en un PDF (sommaire, signets, liens internes). Les corrigés sont exclus. |
| verifier_pdf.py | Contrôle les PDF : signets présents, liens internes valides, aucun contenu interdit, images incluses. |
| metadonnees.toml | Page de garde et propriétés des PDF : auteur, fonction, licence, mention de l'assistance de l'IA. |
| requirements-pdf.txt | Versions des dépendances Python. |
| diagramme_sequence.py | Dessine un diagramme de séquence UML (SVG, puis PNG avec Inkscape) à partir d'un fichier texte `.seq`. Sans dépendance Python. |

Pour générer les PDF en local (Linux ; les bibliothèques Pango et les polices Liberation et DejaVu doivent être installées) :

```bash
pip install -r outils/requirements-pdf.txt
python outils/generer_pdf.py . pdf
python outils/verifier_pdf.py . pdf
```

Les fichiers sont écrits dans le dossier `pdf/`, ignoré par Git.

Pour régénérer le diagramme de l'étape 3 du TP 1 après avoir modifié sa description (le format du fichier `.seq` est expliqué en tête de `diagramme_sequence.py`) :

```bash
python3 outils/diagramme_sequence.py tp1-authentification/images/sequence-connexion.seq
```

## Page de garde des PDF et numéro de version

La page de garde reprend `metadonnees.toml` (auteur, fonction, licence, mention de l'IA). Elle indique aussi, **automatiquement**, le commit, sa date et le numéro de version, qui est le **dernier tag `vX.Y`** (le tag `pdf-latest` de la release est ignoré). Le même texte se retrouve dans les propriétés du PDF et, pour le commit et la version, en pied de page.

La mention de l'IA doit rester identique dans `metadonnees.toml` et dans le README racine : `verifier_pdf.py` contrôle les deux.

Pour numéroter une nouvelle version (le workflow se déclenche tout seul et régénère les PDF avec ce numéro) :

```bash
git tag -a v1.0 -m "Première version complète des deux TP"
git push origin v1.0
```
