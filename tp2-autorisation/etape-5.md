# Étape 5 : Protéger les routes et compléter les pages

À la fin de cette étape, l'application respecte la matrice d'accès de l'administration (le tableau de la section « Livrables » du README) : un visiteur est renvoyé vers la connexion, un utilisateur reçoit une 403, l'administrateur accède à la page. L'accueil et le tableau de bord affichent un contenu différent selon le rôle.

Le DashboardController, la route /dashboard, la déconnexion et la page /accueil existent déjà (TP 1) : vous les complétez.

**Lancer (avant d'agir)**

```bash
php artisan test --filter=AuthorizationTest
```

Vous obtenez 3 tests verts (les seeders et les deux tests d'inscription, étapes 2 et 3) et 11 rouges, tous liés à l'administration. Les cas qui demandent /admin/users disent `Expected response status code … but received 404` : la route n'existe pas. Les tests de l'accueil et du tableau de bord affichent un long bloc de HTML : ne le lisez pas, ils attendent un contenu qui n'existe pas encore.

**Faire** — le contrôleur d'administration.

```bash
php artisan make:controller AdminController
```

Ajoutez une méthode index() dans AdminController, avec l'import use App\\Models\\User; :

```php
public function index()
{
    return view('admin.users', [
        // with('roles') charge les rôles en une requête, et non une par utilisateur
        'users' => User::with('roles')->orderBy('name')->get(),
    ]);
}
```

**Faire — les routes.** Dans routes/web.php, ajoutez l'import de AdminController et le groupe protégé par permission **à l'intérieur** du groupe auth déjà présent. Les routes existantes restent en place. Voici ce que le fichier contient à la fin de l'étape (les lignes ajoutées sont signalées) :

```php
use App\Http\Controllers\AdminController;
use App\Http\Controllers\DashboardController;

// Publique : visiteur et personne connectée (ajouté à l'étape 4)
Route::view('/accueil', 'accueil')->name('accueil');

// Réservé aux personnes connectées
Route::middleware('auth')->group(function () {
    Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');

    // Ajouté à l'étape 5.
    // Imbriqué dans 'auth' : on vérifie l'identité AVANT les droits.
    // 'role:administrateur' fonctionnerait aussi ; la permission est préférable.
    Route::middleware('permission:gerer-utilisateurs')
        ->prefix('admin')
        ->name('admin.')
        ->group(function () {
            Route::get('/users', [AdminController::class, 'index'])->name('users');
        });
});
```

Ces lignes font trois choses : Route::middleware('permission:gerer-utilisateurs') attache à toutes les routes du groupe le middleware permission (alias de PermissionMiddleware) avec le paramètre gerer-utilisateurs ; ->prefix('admin') ajoute /admin devant leurs URL ; ->name('admin.') ajoute admin. devant leurs noms. Le middleware permission s'exécute avant le contrôleur : il répond 403 si la personne connectée n'a pas la permission.

> [!NOTE]
> **Pourquoi auth d'abord.** Les middlewares s'exécutent dans l'ordre. Le middleware permission répond 403 (« User is not logged in ») quand il n'y a pas de compte dont vérifier les permissions. Si permission passait avant auth, un visiteur recevrait donc une 403 « accès refusé » au lieu d'être renvoyé vers /login.

**Relancer** la même commande, avant de créer les vues. Vous obtenez 7 verts et 7 rouges. Quatre tests sont passés au vert sans qu'aucune vue n'existe : le cas « visiteur » (302) et le cas « utilisateur » (403) de la matrice, `test_un_visiteur_n_atteint_pas_l_administration` et `test_un_compte_sans_role_ne_peut_pas_administrer`. Dans ces cas, la requête s'arrête dans un middleware, avant le contrôleur et avant la vue. Les cas où l'administrateur passe sont rouges avec `received 500` et la cause en dessous : `View [admin.users] not found`.

**Faire — la page d'administration.** Créez resources/views/admin/users.blade.php. Elle affiche un tableau des utilisateurs reçus dans $users, avec trois colonnes : nom, e-mail, rôles. Pour les rôles d'un utilisateur : $user->getRoleNames()->implode(', '). Ajoutez un lien de retour vers route('dashboard').

**Relancer** : 11 verts, 3 rouges. Les trois rouges restants (`test_l_accueil_s_adapte_au_role`, `test_le_lien_d_administration_suit_la_permission`, `test_un_autre_role_ayant_la_permission_voit_le_lien_d_administration`) concernent le contenu des pages /accueil et /dashboard.

**Faire — compléter le tableau de bord.** Dans resources/views/dashboard.blade.php (créé au TP 1), ajoutez ces lignes entre le titre `<h1>` et le formulaire de déconnexion :

```html
<p>Rôle(s) : {{ auth()->user()->getRoleNames()->implode(', ') }}</p>

{{-- Confort d'affichage uniquement : ce n'est PAS une protection --}}
@can('gerer-utilisateurs')
    <p><a href="{{ route('admin.users') }}">Gestion des utilisateurs</a></p>
@endcan
```

**Relancer** : 13 verts, 1 rouge (`test_l_accueil_s_adapte_au_role`).

**Faire — compléter la page d'accueil, qui change selon le rôle.** Dans resources/views/accueil.blade.php (créé au TP 1), ajoutez ces lignes entre le bloc `@endguest` et le bloc `@auth` :

```html
    {{-- Utilisateur connecté, droits limités --}}
    @role('utilisateur')
        <p>Espace utilisateur : retrouvez votre tableau de bord.</p>
    @endrole

    {{-- Administrateur --}}
    @role('administrateur')
        <p>Espace administrateur : vous gérez les comptes.</p>
    @endrole
```

**Relancer** :

```bash
php artisan test --filter="AuthenticationTest|AuthorizationTest"
```

Les 34 tests sont verts (14 du TP 2 et 20 du TP 1). Copiez la ligne de résultat dans PREUVES.md.

> [!NOTE]
> **Deux directives pour adapter une vue.** Elles s'ajoutent à @guest et @auth, vues au TP 1. Elles n'ont pas la même origine.
>
> | Directive | Origine | Quand elle affiche son contenu | Exemple d'usage |
> | --- | --- | --- | --- |
> | @role('utilisateur') | Spatie | La personne connectée a ce rôle | Message propre à chaque rôle |
> | @can('gerer-utilisateurs') | Laravel | La personne connectée a cette permission | Lien d'administration |
>
> @can interroge le Gate de Laravel. Le contrôle préalable que Spatie ajoute au Gate (étape 1) lui fait prendre en compte les permissions des rôles : c'est ce qui permet à @can et à can() de répondre pour une permission Spatie.
>
> @role sert à personnaliser l'affichage : un message, une mise en page. Dès qu'un élément correspond à un droit (un lien vers une page protégée, un bouton d'action), utilisez @can avec la même permission que la route. @role ne plante pas pour un visiteur : Spatie vérifie d'abord que quelqu'un est connecté.

> [!WARNING]
> **Masquer n'est pas protéger.** @can cache le lien, rien de plus : quiconque connaît l'URL peut la taper. La protection, c'est le middleware sur la route. Les deux doivent vérifier **la même permission**. Sinon, un utilisateur voit un lien qui mène à une 403, ou a accès à une page qu'aucun lien ne montre.

## Exercices : modifier volontairement le code

Un test ne vaut que par ce qu'il peut détecter. Chaque exercice remplace une ligne par une variante fautive et indique quels tests la détectent. Dans ce TP, « protéger une route » signifie lui associer un middleware qui vérifie une condition avant l'exécution du contrôleur : auth vérifie que la personne est connectée, permission vérifie qu'elle a la permission.

Pour chaque exercice, la démarche est la même :

1. **Prédire** les tests qui vont échouer et notez la liste dans PREUVES.md.
2. Faire la modification.
3. Lancer `php artisan test --filter="AuthenticationTest|AuthorizationTest"`. Noter les tests rouges et leur message. PHPUnit affiche leurs noms, mais ils sont coupés par « … » si la fenêtre du terminal est trop étroite : agrandissez-la.
4. Remettre le code d'origine et relancer : 34 verts.

L'exercice A et l'observation de /accueil (plus bas) utilisent le navigateur : le serveur de développement doit tourner. S'il est arrêté, relancez php artisan serve dans un terminal dédié.

**Exercice A — retirer le middleware permission.** Dans routes/web.php, remplacez `Route::middleware('permission:gerer-utilisateurs')->prefix('admin')` (écrit sur deux lignes dans le fichier) par `Route::prefix('admin')`. Cette modification supprime l'appel qui attache le middleware permission au groupe. Les URL, les noms de routes et le contrôleur sont inchangés, et le groupe auth qui englobe le tout reste en place : seule la vérification de la permission disparaît.

Après les points 1 à 3 de la démarche, connectez-vous dans le navigateur avec utilisateur@exemple.test (mot de passe password). Le lien « Gestion des utilisateurs » n'apparaît pas sur /dashboard, parce que @can le masque. Tapez /admin/users dans la barre d'adresse et notez ce que vous voyez. Expliquez pourquoi chaque test rouge échoue : quelle réponse il attend, laquelle il reçoit.

**Exercice B — la permission ou le nom du rôle.** Le contrat crée un rôle « tuteur », qui a la permission gerer-utilisateurs sans être administrateur. Deux variantes fautives, à essayer l'une après l'autre (remettre le code d'origine entre les deux) :

- dans routes/web.php, remplacez `permission:gerer-utilisateurs` par `role:administrateur`. Le middleware role vérifie le nom du rôle, et non la permission ;
- dans resources/views/dashboard.blade.php, remplacez `@can('gerer-utilisateurs')` par `@role('administrateur')`, et `@endcan` par `@endrole`. La directive teste alors le nom du rôle.

Pour chaque variante, un test est rouge. Identifiez-le et expliquez ce qu'il montre sur la différence entre vérifier un rôle et vérifier une permission.

**Exercice C — inverser l'ordre des vérifications.** Dans routes/web.php, déplacez le bloc `Route::middleware('permission:gerer-utilisateurs')->prefix('admin')->name('admin.')->group(…)` hors du groupe `Route::middleware('auth')->group(…)`, en le plaçant après l'accolade fermante de ce dernier. Les routes sont les mêmes ; le middleware auth ne s'applique plus à /admin/users. Deux tests sont rouges. Identifiez-les et notez le code reçu à la place de la redirection 302.

**Exercice D — faute dans le nom de la classe de l'alias permission.** Dans bootstrap/app.php, remplacez PermissionMiddleware par PermisionMiddleware, dans l'import et dans l'alias. Contrairement à la faute de l'étape 4, celle-ci touche un alias que des routes utilisent. Relevez le nombre de tests rouges et le message commun : il reprend le nom de la classe fautive.

**Preuve**

```bash
php artisan route:list --path=admin -v
```

L'option -v affiche les middlewares de chaque route, dans l'ordre où ils s'exécutent : web, auth, puis permission:gerer-utilisateurs. Copiez la sortie et, pour les exercices A à D, la liste des tests rouges et leur message.

Le test de la matrice a déjà vérifié les 3 cases : inutile de les refaire à la main. Il reste à observer l'affichage de /accueil. Ouvrez /accueil connecté avec utilisateur@exemple.test, puis avec admin@exemple.test (déconnectez-vous entre les deux), et notez ce qu'affiche la page pour chacun.

> **Question 4.** Un collègue ajoute demain une route /admin/export en dehors du groupe protégé. Qu'est-ce qui empêcherait cette erreur de passer inaperçue ?

**Exercice bonus — un test qui détecte la route non protégée.** Le contrat AuthorizationTest.php ne se modifie pas : créez un second fichier, tests/Feature/RoutesAdminTest.php, avec un test qui parcourt toutes les routes de l'application et vérifie que chaque route dont l'URL commence par admin porte le middleware permission:gerer-utilisateurs. Pistes : Route::getRoutes(), $route->uri(), $route->gatherMiddleware().

Pour vérifier que ce test détecte la faute, ajoutez à la fin de routes/web.php, en dehors de tout groupe, la route `Route::get('/admin/export', fn () => 'export');`. Elle répond à n'importe quel visiteur. Lancez les 34 tests du contrat : ils restent verts. Lancez votre test : il doit échouer. Retirez la route : il redevient vert.
