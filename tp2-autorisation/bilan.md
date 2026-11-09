# Bilan du TP 2 — Je sais le prouver

Cochez une case seulement si la preuve correspondante figure dans PREUVES.md.

- ☐ php artisan test --filter="AuthenticationTest|AuthorizationTest" : les 34 tests sont verts (14 du TP 2 et 20 du TP 1)
- ☐ Pour chaque étape, PREUVES.md contient un test rouge (message copié, cause expliquée en une phrase) puis le même test vert
- ☐ Je montre en base où est stocké le rôle d'un utilisateur, et j'explique pourquoi il n'existe pas de rôle « visiteur »
- ☐ Je relance les seeders sans erreur, et j'explique ce qui se passe avec Role::create à la place de findOrCreate
- ☐ J'ai vu l'injection de rôle réussir sur la version vulnérable, puis échouer sur la version sûre
- ☐ J'ai vu le test d'injection passer au rouge sur la version vulnérable
- ☐ J'ai retiré le middleware permission de la route /admin/users, constaté l'accès d'un utilisateur, et identifié les tests qui échouent
- ☐ J'ai essayé role:administrateur à la place de permission:gerer-utilisateurs, @role à la place de @can, l'ordre permission puis auth, et une faute dans l'alias permission : pour chaque variante, je sais quels tests échouent et pourquoi
- ☐ Je montre que /accueil affiche un contenu différent pour l'utilisateur et pour l'administrateur
- ☐ Je provoque et j'explique la 403 sur mon application, et je la distingue de la redirection 302
- ☐ (Bonus) J'ai écrit un test qui détecte une route /admin non protégée, et je l'ai vu échouer sur une route ajoutée hors du groupe

Questions de restitution (à l'oral, sans notes)

1. Une 403 et une redirection 302 vers /login : laquelle signale un échec d'authentification, laquelle un échec d'autorisation ?
2. Pourquoi « visiteur » n'est-il pas un rôle en base ? Comment l'application reconnaît-elle un visiteur, côté route et côté vue ?
3. Pourquoi l'application vérifie-t-elle la permission gerer-utilisateurs plutôt que le rôle administrateur ? Que faut-il modifier pour créer un rôle « tuteur » qui gère aussi les utilisateurs ?
4. Sur /accueil, quand utiliser @role, et quand utiliser @can ?
5. @can masque le lien d'administration. Qu'est-ce qui protège réellement la page, et comment l'avez-vous prouvé ?
6. Pourquoi un Role::create dans un seeder pose-t-il problème, alors que le code fonctionne au premier lancement ?
7. Un test vert prouve-t-il que le code est correct ? Appuyez-vous sur les exercices des étapes 3, 4 et 5.
8. À l'étape 5, quatre tests (deux cas de la matrice, la redirection du visiteur, le compte sans rôle) deviennent verts avant que la vue d'administration existe. Qu'est-ce que cela montre sur l'ordre d'exécution des middlewares, du contrôleur et de la vue ?
9. Avant l'ajout du trait HasRoles, un appel à hasRole() échoue avec un message, alors que can() répond false sans erreur. Pourquoi cette différence, et en quoi est-elle un risque ?

**Limites du contrat.** Un test vert prouve ce qu'il vérifie, pas davantage. Les 14 tests du contrat resteraient verts si l'on : ajoutait une route /admin/export hors du groupe protégé, ou faisait une faute dans le nom de la classe de l'alias role\_or\_permission (aucune route du contrat ne l'utilise). Chacune de ces variantes a été essayée : aucune ne fait échouer le contrat. La première est l'objet de l'exercice bonus de l'étape 5, la seconde de l'exercice de l'étape 4. À l'inverse, plusieurs erreurs sont détectées : protéger la page par role:administrateur au lieu de permission:gerer-utilisateurs, ou afficher le lien avec @role au lieu de @can (tests du rôle « tuteur »), retirer le middleware permission de la route, placer permission avant auth, faire une faute dans l'alias permission, utiliser Role::create dans un seeder, ou lire le rôle dans la requête à l'inscription. Savoir ce qu'un test ne couvre pas fait partie de la preuve.
