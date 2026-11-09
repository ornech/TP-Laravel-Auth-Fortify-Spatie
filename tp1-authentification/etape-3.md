# Étape 3 : Comprendre la connexion : la session

À la fin de cette étape, vous saurez expliquer sur quelle donnée repose la phrase « cet utilisateur est connecté ».

HTTP n'a pas de mémoire : chaque requête arrive seule, sans lien avec la précédente. Pour répondre 200 à une personne connectée et 302 à un visiteur sur /dashboard, le serveur s'appuie sur deux éléments : une **session**, enregistrée côté serveur, et un **cookie**, conservé par le navigateur. Cette étape les montre dans la base et dans les en-têtes HTTP.

![Diagramme de séquence UML : la personne se connecte, le serveur crée la session et envoie le cookie, puis la personne ouvre une page protégée](images/sequence-connexion.png)

> [!NOTE]
> **Lire un diagramme de séquence.** Un **diagramme de séquence** (UML) montre des échanges dans l'ordre, de haut en bas. Chaque colonne est un acteur (ici le navigateur, Laravel et la base de données). Une flèche pleine est une demande, une flèche en pointillés une réponse.

Le serveur de développement (étape 2) doit tourner, et vous devez être déconnecté.

**Observation 1 — Le mot de passe en base.**

```bash
php artisan tinker --execute="dump(DB::table('users')->get(['id', 'email', 'password']));"
```

La colonne `password` contient un hash (60 caractères, qui commence par `$2y$`), jamais le mot de passe. À la connexion, Laravel vérifie le mot de passe saisi contre ce hash : on ne « déchiffre » jamais le hash. Les deux comptes de démonstration ont le même mot de passe (`password`) et des hashes différents (voir le mémo ci-dessous).

> [!NOTE]
> **Hash, bcrypt et sel.** Un **hash** est l'empreinte irréversible d'un mot de passe : on peut vérifier qu'un mot de passe correspond à son hash, mais on ne peut pas retrouver le mot de passe à partir du hash. **bcrypt** est l'algorithme de hachage utilisé par Laravel. Le **sel** est une valeur aléatoire ajoutée au mot de passe avant le calcul et inscrite dans le hash : c'est pourquoi deux mots de passe identiques donnent deux hashes différents.

**Observation 2 — Ce que le serveur remet à un nouveau visiteur.**

```bash
curl -I http://127.0.0.1:8000/login
```

Sous Windows PowerShell, tapez `curl.exe`. L'option `-I` n'affiche que les en-têtes de la réponse. Repérez les deux lignes `Set-Cookie` :

- `laravel-session` : le cookie de session. Sa valeur est chiffrée et ne contient aucune information sur vous (ni nom, ni rôle) : seulement de quoi retrouver votre session sur le serveur. L'attribut `httponly` interdit à JavaScript de le lire.
- `XSRF-TOKEN` : un second cookie, lié à la protection CSRF.

**Observation 3 — La session d'un visiteur.** Videz d'abord la table des sessions (cela déconnecte tout le monde, c'est voulu) :

```bash
php artisan tinker --execute="DB::table('sessions')->truncate();"
```

Dans le navigateur, ouvrez http://127.0.0.1:8000/login sans vous connecter, puis affichez la table :

```bash
php artisan tinker --execute="dump(DB::table('sessions')->get(['id', 'user_id']));"
```

Vous devez voir **une seule ligne**, avec `user_id` vide : un visiteur a déjà une session, que Laravel crée dès la première visite. Notez le début de son `id`. Si plusieurs lignes apparaissent, d'autres onglets ou d'autres clients (`curl`) ont visité le site : fermez-les, videz la table et rechargez /login.

**Observation 4 — La connexion.** Connectez-vous avec alice@exemple.test (mot de passe password), puis relancez la commande qui affiche la table. Vous devez voir **une seule ligne**, dont `user_id` vaut l'identifiant de alice@exemple.test (colonne `id` de l'observation 1) et dont l'`id` a **changé** : à la connexion, Laravel renouvelle l'identifiant de session.

Facultatif : voir ce que la session retient.

```bash
php artisan tinker --execute="dump(json_decode(base64_decode(DB::table('sessions')->value('payload')), true));"
```

On y trouve le jeton CSRF (`_token`, celui que `@csrf` place dans les formulaires, étape 2) et une clé qui commence par `login_web_`, dont la valeur est l'identifiant de l'utilisateur : c'est cette donnée qui signifie « connecté ».

> [!NOTE]
> **La colonne payload.** La colonne `payload` de la table `sessions` contient le contenu de la session, écrit en JSON puis encodé en base64 : la commande ci-dessus le décode pour vous.

**Observation 5 — La déconnexion.** Cliquez sur « Se déconnecter », puis relancez la commande qui affiche la table. Vous devez voir **une seule ligne**, avec `user_id` vide et un nouvel `id` : la session de l'utilisateur a été détruite côté serveur, et un cookie copié avant la déconnexion ne mène plus nulle part.

> [!NOTE]
> **« Rester connecté ».** Si la case est cochée, Laravel pose en plus un cookie `remember_web_…`, valable plus d'un an, et enregistre un jeton dans la colonne `users.remember_token`. Il permet de rouvrir une session une fois la précédente expirée (120 minutes d'inactivité par défaut, réglage `SESSION_LIFETIME`).

**Preuve**

Copiez dans PREUVES.md la sortie de l'observation 1 et les trois affichages de la table `sessions` (observations 3, 4 et 5) : visiteur, connecté, déconnecté.

## Ce que les tests protègent

**Lancer**

```bash
php artisan test --filter="test_la_connexion_enregistre_l_utilisateur_dans_la_session|test_la_deconnexion_detruit_la_session"
```

Les deux tests de cette étape sont **déjà verts**, depuis l'étape 2 : c'est Fortify qui ouvre et détruit la session, vous n'avez rien écrit pour cela. Ils ne guident donc pas votre travail, ils le gardent : ils reprennent automatiquement ce que vous venez d'observer dans la table sessions. Lisez-les dans le contrat, ils montrent comment tester une session, puis reliez chaque observation à l'assertion qui la reprend :

| Ce que vous avez observé | Ce que le test vérifie |
| --- | --- |
| Observation 4 : `user_id` vaut l'identifiant d'alice ; le payload contient une clé `login_web_…` | `test_la_connexion_enregistre_l_utilisateur_dans_la_session` : une seule entrée dont la clé commence par `login_web_`, et sa valeur est l'identifiant d'alice |
| Observation 5 : la session de l'utilisateur est détruite | `test_la_deconnexion_detruit_la_session` : un marqueur placé dans la session disparaît, puis /dashboard renvoie de nouveau vers /login |
| Observation 4 : l'identifiant de session **a changé** | Aucun test. Si Laravel ne renouvelait plus l'identifiant à la connexion, les 20 tests resteraient verts |

La dernière ligne rappelle qu'un test vert prouve ce qu'il vérifie, pas davantage : c'est pourquoi vous avez aussi regardé la table sessions. La question 2.3 ci-dessous explique pourquoi ce renouvellement compte.

**Exercice — remplacer la déconnexion de Fortify.** Un test ne vaut que s'il peut échouer. Cet exercice remplace la déconnexion de Fortify par une version qui retire l'utilisateur de la session sans détruire la session, puis observe les tests.

1. **Prédire** : quel test va passer au rouge ?
2. À la fin de routes/web.php, ajoutez ce bloc. Il porte le même nom et la même méthode que la route de Fortify : la dernière déclarée l'emporte.

   ```php
   // À RETIRER APRÈS L'EXERCICE : déconnexion « maison »
   Route::post('/logout', function () {
       \Illuminate\Support\Facades\Auth::logout();

       return redirect('/');
   })->name('logout');
   ```

3. Lancez le contrat. Vous obtenez 4 rouges au lieu de 3 : le nouveau est `test_la_deconnexion_detruit_la_session`, avec le message `La session aurait dû être vidée à la déconnexion.` Auth::logout() retire seulement l'utilisateur de la session ; le reste de la session survit (ici le marqueur du test, dans une application réelle tout ce qu'elle y a rangé). Fortify, lui, détruit toute la session.
4. `test_la_deconnexion_n_accepte_que_post` reste vert : votre route est bien en POST. Ce test porte sur la méthode HTTP, pas sur la session.
5. Retirez le bloc et relancez : 17 verts, 3 rouges.

**Preuve.** Dans PREUVES.md, copiez le message d'échec de l'étape 3 (rouge) et la ligne de résultat avant et après.

> **Question 2.** Vous êtes connecté. Quelqu'un copie la valeur de votre cookie `laravel-session` dans son propre navigateur.
>
> 1. Que peut-il faire sans connaître votre mot de passe ?
> 2. Que devient ce cookie si vous cliquez ensuite sur « Se déconnecter » ?
> 3. Pourquoi l'identifiant de session change-t-il à la connexion ?
>
> Appuyez-vous sur ce que vous avez observé dans la table `sessions`.
