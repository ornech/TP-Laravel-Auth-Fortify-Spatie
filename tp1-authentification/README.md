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

À la fin de ce TP, votre application sait **qui est connecté** : on peut s'inscrire, se connecter, se déconnecter, et certaines pages sont réservées aux personnes connectées. Surtout, vous savez le prouver : chaque étape se termine par une preuve à produire, pas par « ça marche ».

Vous saurez :

1. Mettre en place l'authentification avec Laravel Fortify, sans interface fournie, en n'exposant que les fonctionnalités utiles.
2. Expliquer ce qui rend un utilisateur « connecté » : une session enregistrée côté serveur et un cookie côté navigateur, et le montrer dans la base.
3. Protéger une page avec le middleware auth, et adapter le contenu d'une vue selon que la personne est connectée ou non.
4. Expliquer et provoquer les réponses 302, 405, 419 et 429 de votre application.
5. Faire passer des tests qui servent de preuve, et vérifier qu'ils détectent bien une faille.

**Contexte.** Vous partez d'un dossier vide et créez un projet Laravel 13 neuf à l'étape 1. Prérequis : PHP 8.3 ou plus récent, Composer, et l'extension PHP pdo\_sqlite.

Versions de référence :

- Laravel Framework : 13.40.0
- Fortify : 1.41.0

**Règle d'or.** Quand un extrait montre un fichier qui existe déjà, vous **ajoutez** ce qui est indiqué. Vous ne remplacez jamais un fichier entier par un extrait : les fichiers générés contiennent des éléments dont l'application a besoin. Les rares exceptions sont signalées dans l'énoncé.

**Vos preuves.** Vous créez à l'étape 1, à la racine de votre projet (tp-auth), un fichier PREUVES.md. Vous y copiez, étape après étape, les sorties de commandes et vos observations demandées dans les rubriques « Preuve » : c'est ce fichier que le bilan vous demande de relire.

## Rappel : l'authentification et les codes HTTP

L'authentification répond à une seule question : « qui êtes-vous ? ». Dans Laravel, c'est le travail de **Fortify** (connexion, inscription, session), et le middleware **auth** protège les pages réservées aux personnes connectées. Un visiteur qui demande une telle page reçoit une redirection 302 vers /login.

Une seconde question, « avez-vous le droit de faire ceci ? », relève de l'**autorisation** : c'est l'objet du [TP 2](../tp2-autorisation/README.md).

**Les codes HTTP couramment rencontrés :**

| Code | Signification | Exemple |
| --- | --- | --- |
| 302 | Redirection : non authentifié | Un visiteur demande /dashboard |
| 405 | Méthode HTTP refusée par la route | GET /logout : la route n'accepte que POST |
| 419 | Requête POST sans origine vérifiable ni jeton CSRF | Un POST /login envoyé avec curl |
| 429 | Trop de requêtes | Sixième tentative de connexion en moins d'une minute |

## Livrables

Voici ce qui est attendu en termes de protection des routes. Ces cas devront être vérifiés par un test (étape 4).

| Route | Visiteur | Personne connectée |
| --- | --- | --- |
| /accueil | 200 | 200 |
| /login | 200 | 302 vers /dashboard |
| /dashboard | 302 vers /login | 200 |

## Qui fait quoi : Fortify et vous

Fortify fait le travail d'authentification côté serveur, mais ne fournit aucune page.

| Fortify fournit | Vous décidez ou écrivez |
| --- | --- |
| Les routes (/login, /register, /logout…) et leurs contrôleurs | Les vues Blade des formulaires |
| La vérification des identifiants et la session | Le choix des fonctionnalités actives, dans config/fortify.php |
| La limitation des tentatives de connexion | La page d'arrivée après connexion (clé home) |
| Des actions modifiables dans app/Actions/Fortify | Les pages réservées aux personnes connectées, et ce qu'elles affichent |
