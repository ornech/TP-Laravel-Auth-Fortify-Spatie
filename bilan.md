# Bilan — Je sais le prouver

Cochez une case seulement si la preuve correspondante figure dans PREUVES.md.

- ☐ php artisan test --filter=AuthRbacTest : les 23 tests sont verts
- ☐ Je montre en base où est stocké le rôle d'un utilisateur, et j'explique pourquoi il n'existe pas de rôle « visiteur »
- ☐ Je relance les seeders sans erreur, et j'explique pourquoi DemoUserSeeder ne s'exécute pas en production
- ☐ Je montre avec route:list les routes exposées par Fortify, et je justifie chaque fonctionnalité active (et je sais pourquoi les routes confirm-password restent présentes)
- ☐ Je montre dans la table sessions ce qui change à la connexion et à la déconnexion, et j'explique ce que contient le cookie de session
- ☐ J'ai vu l'injection de rôle réussir sur la version vulnérable, puis échouer sur la version sûre
- ☐ J'ai vu le test d'injection passer au rouge sur la version vulnérable
- ☐ J'ai retiré la protection de /admin, constaté l'accès, et identifié le cas de la matrice qui échoue
- ☐ Je montre que /accueil affiche un contenu différent pour le visiteur, l'utilisateur et l'administrateur
- ☐ Je provoque et j'explique 302, 403, 405, 419 et 429 sur mon application
- ☐ (Bonus) J'ai écrit un test qui détecte une route /admin non protégée, et je l'ai vu échouer sur une route ajoutée hors du groupe

Questions de restitution (à l'oral, sans notes)

1. Sur quelle donnée repose l'affirmation « cet utilisateur est connecté » ? Où est-elle enregistrée, et que contient le cookie envoyé au navigateur ?
2. Une 403 et une redirection 302 vers /login : laquelle signale un échec d'authentification, laquelle un échec d'autorisation ?
3. Pourquoi « visiteur » n'est-il pas un rôle en base ? Comment l'application reconnaît-elle un visiteur, côté route et côté vue ?
4. Pourquoi l'application vérifie-t-elle la permission gerer-utilisateurs plutôt que le rôle administrateur ? Que faut-il modifier pour créer un rôle « tuteur » qui gère aussi les utilisateurs ?
5. Sur /accueil, quand utiliser @role, et quand utiliser @can ?
6. @can masque le lien d'administration. Qu'est-ce qui protège réellement la page, et comment l'avez-vous prouvé ?
7. Sans @csrf, la connexion fonctionnait dans le navigateur mais pas avec curl. Pourquoi ? Pourquoi garder @csrf malgré tout ?
8. Pourquoi un Role::create dans un seeder pose-t-il problème, alors que le code fonctionne au premier lancement ?
9. Que se passe-t-il si l'on remplace toute la méthode boot() de FortifyServiceProvider par les deux lignes de déclaration des vues ?
10. Pourquoi la déconnexion est-elle en POST ?
11. Un test vert prouve-t-il que le code est correct ? Appuyez-vous sur les exercices des étapes 4 et 6.

**Limites du contrat.** Un test vert prouve ce qu'il vérifie, pas davantage. Les 23 tests du contrat resteraient verts si l'on : ajoutait une route /admin/export hors du groupe protégé, protégeait la page par role:administrateur au lieu de permission:gerer-utilisateurs, affichait le lien d'administration avec @role au lieu de @can, réactivait d'autres fonctionnalités de Fortify (modification du profil ou du mot de passe), comptait les tentatives de connexion par adresse IP seule, ou supprimait la garde d'environnement de DemoUserSeeder. Chacune de ces variantes a été essayée : aucune ne fait échouer le contrat. Savoir ce qu'un test ne couvre pas fait partie de la preuve.
