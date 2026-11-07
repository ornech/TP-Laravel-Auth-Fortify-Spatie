# Étape 0 : Créer le projet et installer le contrat de tests

**Faire**

```bash
# Projet neuf, dernière version de Laravel (13.x)
composer create-project laravel/laravel tp-auth
cd tp-auth
php artisan --version
```

Puis le dépôt Git et la branche de travail, **une commande par ligne** (l'enchaînement avec && ne fonctionne pas dans toutes les versions de PowerShell) :

```bash
git init
git add -A
git commit -m "Squelette Laravel 13"
git switch -c feat/auth-rbac
```

> [!NOTE]
> Si `git commit` répond « Identité d'auteur inconnue », Git ne sait pas qui signe le commit (poste jamais configuré). Déclarez votre identité **pour ce projet seulement**, sans `--global` : sur un poste partagé, vous ne devez pas modifier l'identité des autres utilisateurs. Puis relancez `git commit`.
>
> ```bash
> git config user.name "Prénom Nom"
> git config user.email "prenom.nom@exemple.fr"
> ```

Créez dès maintenant, à la racine du projet, un fichier vide **PREUVES.md** : vous y copierez vos preuves tout au long du TP (voir le README).

Vous commencez par les tests : ils décrivent ce que l'application devra faire à la fin. Au départ, ils échouent tous. Votre travail consiste à les faire passer un par un, sans jamais les modifier.

Créez tests/Feature/AuthRbacTest.php et copiez-y le fichier donné dans la section « Contrat de tests », plus bas, sans rien changer.

Ces tests s'appuient sur RefreshDatabase : la migration est exécutée une seule fois, puis chaque test tourne dans une transaction qui est annulée en fin de test, garantissant un état propre sans re-migrer. La base SQLite en mémoire (:memory:) est déjà configurée dans le phpunit.xml, donc aucun fichier n'est créé sur le disque.

**Preuve**

```bash
php artisan test --filter=AuthRbacTest
```

Tous les tests échouent : les classes qu'ils utilisent n'existent pas encore.

![](images/etape0-tests-en-echec.png)

> [!NOTE]
> Lancez les commandes de test dans un terminal ordinaire. Si vous les lancez depuis un assistant IA (Claude Code, Cursor…), la sortie peut s'afficher en JSON au lieu de ressembler à la capture : c'est le comportement du package laravel/pao, inclus dans le squelette Laravel 13. Voir le dépannage.
