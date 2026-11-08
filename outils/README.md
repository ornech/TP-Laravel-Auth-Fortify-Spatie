# Outils

Génération des PDF des deux TP. En temps normal, **vous n'avez rien à faire** : le workflow
`.github/workflows/pdf.yml` s'exécute à chaque mise à jour des TP et publie les PDF dans la release
`pdf-latest` (voir le README à la racine).

| Fichier | Rôle |
| --- | --- |
| generer_pdf.py | Convertit les fichiers markdown d'un TP en un PDF (sommaire, signets, liens internes). Les corrigés sont exclus. |
| verifier_pdf.py | Contrôle les PDF : signets présents, liens internes valides, aucun contenu interdit, images incluses. |
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
