# Bilan du TP 1 — Je sais le prouver

Cochez une case seulement si la preuve correspondante figure dans PREUVES.md.

- ☐ php artisan test --filter=AuthenticationTest : les 20 tests sont verts
- ☐ Je relance les seeders sans erreur, et j'explique pourquoi DemoUserSeeder ne s'exécute pas en production
- ☐ Je montre avec route:list les routes exposées par Fortify, et je justifie chaque fonctionnalité active (et je sais pourquoi les routes confirm-password restent présentes)
- ☐ Je montre dans la table sessions ce qui change à la connexion et à la déconnexion, et j'explique ce que contient le cookie de session
- ☐ J'ai retiré le middleware auth de /dashboard, constaté ce qu'obtient un visiteur, et identifié les tests qui échouent
- ☐ Je montre que /accueil affiche un contenu différent pour le visiteur et pour la personne connectée
- ☐ Je provoque et j'explique 302, 405, 419 et 429 sur mon application

Questions de restitution (à l'oral, sans notes)

1. Sur quelle donnée repose l'affirmation « cet utilisateur est connecté » ? Où est-elle enregistrée, et que contient le cookie envoyé au navigateur ?
2. Pourquoi le mot de passe n'est-il jamais stocké en clair ? Deux comptes ayant le même mot de passe ont pourtant des hashes différents : pourquoi ?
3. Que signifie une redirection 302 vers /login, et quel middleware la décide ?
4. Sans @csrf, la connexion fonctionnait dans le navigateur mais pas avec curl. Pourquoi ? Pourquoi garder @csrf malgré tout ?
5. Pourquoi la déconnexion est-elle en POST ?
6. Que se passe-t-il si l'on remplace toute la méthode boot() de FortifyServiceProvider par les deux lignes de déclaration des vues ?
7. @auth masque le lien vers le tableau de bord. Qu'est-ce qui protège réellement la page, et comment l'avez-vous prouvé ?
8. Pourquoi des comptes de démonstration au mot de passe connu ne doivent-ils pas exister en production ? Comment DemoUserSeeder s'en protège-t-il ?
9. Un test vert prouve-t-il que le code est correct ? Appuyez-vous sur l'exercice de l'étape 4.

**Limites du contrat.** Un test vert prouve ce qu'il vérifie, pas davantage. Les 20 tests du contrat resteraient verts si l'on : retirait l'attribut HttpOnly du cookie de session, allongeait la durée de vie de la session à plusieurs mois, ou supprimait les règles de complexité du mot de passe. Chacune de ces variantes a été essayée : aucune ne fait échouer le contrat. À l'inverse, trois erreurs plausibles sont détectées, parce qu'un test a été écrit pour chacune : compter les tentatives de connexion par adresse IP seule, réactiver la modification du profil ou du mot de passe, ou supprimer la garde d'environnement de DemoUserSeeder. Savoir ce qu'un test ne couvre pas fait partie de la preuve.

La suite : le [TP 2](../tp2-autorisation/README.md) ajoute la question « avez-vous le droit ? ».
