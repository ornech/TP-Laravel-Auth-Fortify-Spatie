# TP 1 : Authentification avec Laravel Fortify

Qui êtes-vous ? Inscription, connexion, session.

## Sommaire

- [Présentation](#présentation)
- [Étape 1 : Créer le projet, le contrat de tests et les comptes de démonstration](etape-1.md)
- [Étape 2 : Installer Fortify](etape-2.md)
- [Étape 3 : Comprendre la connexion : la session](etape-3.md)
- [Étape 4 : Protéger une page et adapter l'affichage](etape-4.md)
- [Contrat de tests](contrat-de-tests.md) (commenté : à lire aussi comme un modèle de test pour vos futurs projets)
- [Dépannage](depannage.md)
- [Bilan — Je sais le prouver](bilan.md)
- Suite : [TP 2 : Autorisation avec Spatie](../tp2-autorisation/README.md)

# Présentation

À la fin de ce TP, votre application sait **qui est connecté** : on peut s'inscrire, se connecter, se déconnecter, et certaines pages sont réservées aux personnes connectées. Chaque étape se termine par une preuve à produire.

Vous saurez :

1. Mettre en place l'authentification avec Laravel Fortify, sans interface fournie, en n'exposant que les fonctionnalités utiles.
2. Expliquer ce qui rend un utilisateur « connecté » : une session enregistrée côté serveur et un cookie côté navigateur, et le montrer dans la base.
3. Protéger une page avec le middleware auth, et adapter le contenu d'une vue selon que la personne est connectée ou non.
4. Expliquer et provoquer les réponses 302, 405, 419 et 429 de votre application.
5. Travailler en boucle avec les tests : en lancer un avant d'agir, lire son message d'échec, agir, relancer. Puis vérifier qu'ils détectent bien une faille, en cassant volontairement le code.

**Contexte.** Vous partez d'un dossier vide et créez un projet Laravel 13 neuf à l'étape 1. Prérequis : PHP 8.3 ou plus récent, Composer, et l'extension PHP pdo\_sqlite.

Versions de référence :

- Laravel Framework : 13.40.0
- Fortify : 1.41.0

**Règle d'or.** Quand un extrait montre un fichier qui existe déjà, vous **ajoutez** ce qui est indiqué. Vous ne remplacez jamais un fichier entier par un extrait : les fichiers générés contiennent des éléments dont l'application a besoin. Les rares exceptions sont signalées dans l'énoncé.

**Vos preuves.** Vous créez à l'étape 1, à la racine de votre projet (tp-auth), un fichier PREUVES.md. Vous y copiez, étape après étape, les sorties de commandes et vos observations demandées dans les rubriques « Preuve » : c'est ce fichier que le bilan vous demande de relire. Vous y copiez aussi, pour chaque étape, au moins un test **rouge** (son message, et la cause en une phrase) puis le même test **vert** : les tests ne sont pas là pour valider à la fin, ils guident chaque action.

## Vocabulaire Laravel

Aucune connaissance préalable de Laravel n'est supposée. Les termes ci-dessous sont utilisés dans les deux TP.

| Terme | Définition | Où il apparaît |
| --- | --- | --- |
| Composer | Gestionnaire de dépendances de PHP. `composer require nom/package` télécharge un package dans le dossier vendor/ du projet. | Étapes 1 et 2 |
| Artisan | Outil en ligne de commande de Laravel. `php artisan <commande>` exécute une commande du projet ; `php artisan list` les liste toutes. | Toutes les étapes |
| Route | Lien entre une URL (avec sa méthode HTTP : GET, POST…) et le code qui y répond. Les routes de l'application sont déclarées dans routes/web.php, par exemple `Route::get('/dashboard', …)`. | Étapes 2 et 4 |
| Contrôleur | Classe du dossier app/Http/Controllers dont une méthode construit la réponse d'une route. Ici, `DashboardController::index()` renvoie une vue. | Étape 2 |
| Vue (Blade) | Fichier du dossier resources/views, nommé `….blade.php`, qui produit la page HTML. `{{ … }}` affiche une valeur ; `@auth`, `@guest` et les autres directives commencent par @. | Étapes 2 et 4 |
| Middleware | Code placé devant une route : il examine la requête avant le contrôleur, puis la laisse passer ou la refuse (voir « Rappel » ci-dessous). | Étapes 2 et 4 |
| Service provider | Classe qui configure un composant de l'application au démarrage. Sa méthode `boot()` s'exécute à chaque démarrage. Fortify ajoute app/Providers/FortifyServiceProvider.php. | Étape 2 |
| Modèle | Classe qui représente une table de la base de données. `User` représente la table users. | TP 2 |
| Migration | Fichier qui crée ou modifie des tables. `php artisan migrate` exécute les migrations pas encore appliquées. | Étapes 1 et 2 |

**Le trajet d'une requête.** Quand le navigateur demande une page, Laravel exécute, dans cet ordre : les middlewares de la route (par exemple auth), puis le contrôleur, puis la vue. Si un middleware refuse la requête, il répond lui-même (par exemple une redirection 302) et le contrôleur n'est pas exécuté.

## Rappel : l'authentification et les codes HTTP

L'authentification répond à une seule question : « qui êtes-vous ? ». Dans Laravel, c'est le travail de **Fortify** (connexion, inscription, session), et le middleware **auth** protège les pages réservées aux personnes connectées. Un visiteur qui demande une telle page reçoit une redirection 302 vers /login.

> [!NOTE]
> **Middleware et visiteur.** Un **middleware** est un code placé devant une route : il examine chaque requête avant que la page ne soit construite, puis la laisse passer ou la refuse. Un **visiteur** est une personne qui n'est pas connectée.

Une seconde question, « avez-vous le droit de faire ceci ? », relève de l'**autorisation** : c'est l'objet du [TP 2](../tp2-autorisation/README.md).

**Les codes HTTP couramment rencontrés :**

| Code | Signification | Exemple |
| --- | --- | --- |
| 302 | Redirection : non authentifié | Un visiteur demande /dashboard |
| 405 | Méthode HTTP refusée par la route | GET /logout : la route n'accepte que POST |
| 419 | Requête POST sans origine vérifiable ni jeton CSRF | Un POST /login envoyé avec curl |
| 429 | Trop de requêtes | Sixième tentative de connexion en moins d'une minute |

> [!NOTE]
> **CSRF.** CSRF (*Cross-Site Request Forgery*) désigne une attaque où un site tiers fait envoyer à votre insu un formulaire à votre application, en profitant de la session de la personne connectée. Laravel s'en protège en exigeant un jeton secret dans chaque formulaire : l'étape 2 y revient en détail.

## Livrables : la matrice d'accès

Voici ce qui est attendu en termes de protection des routes, sous la forme d'une matrice d'accès :

> [!NOTE]
> **Lire une matrice d'accès.** Une **matrice d'accès** est un tableau qui croise des **profils** (en colonnes : qui fait la demande) et des **routes** (en lignes : ce qui est demandé). Chaque case indique ce que l'application doit répondre à ce profil pour cette route. C'est le cahier des charges de la protection de l'application : on l'écrit avant de coder, puis on la vérifie par un test.
>
> Pour lire une case, croisez la ligne et la colonne. Par exemple, la ligne /dashboard et la colonne Visiteur donnent « 302 vers /login » : un visiteur qui demande /dashboard est redirigé vers la page de connexion. Les codes sont ceux du rappel ci-dessus, plus le 200 : la page s'affiche normalement.

| Route | Visiteur | Personne connectée |
| --- | --- | --- |
| /accueil | 200 | 200 |
| /login | 200 | 302 vers /dashboard |
| /dashboard | 302 vers /login | 200 |

Les 6 cases (3 routes × 2 profils) deviennent les 6 cas du test test\_la\_matrice\_d\_acces\_est\_respectee, à l'étape 4.

## Qui fait quoi : Fortify et vous

Fortify fait le travail d'authentification côté serveur, mais ne fournit aucune page.

| Fortify fournit | Vous décidez ou écrivez |
| --- | --- |
| Les routes (/login, /register, /logout…) et leurs contrôleurs | Les vues Blade des formulaires |
| La vérification des identifiants et la session | Le choix des fonctionnalités actives, dans config/fortify.php |
| La limitation des tentatives de connexion | La page d'arrivée après connexion (clé home) |
| Des actions modifiables dans app/Actions/Fortify | Les pages réservées aux personnes connectées, et ce qu'elles affichent |
