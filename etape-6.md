# Étape 6 — Protéger les routes et créer les pages

À la fin de cette étape, l'application respecte la matrice d'accès pour les trois profils. Un visiteur est renvoyé vers la connexion, un utilisateur reçoit une 403 sur l'administration, l'administrateur y accède. La page d'accueil affiche un contenu différent pour chaque profil.

Le DashboardController, la route /dashboard et la déconnexion existent déjà (étape 3) : vous les complétez.

Faire — le contrôleur d'administration.

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

**Faire — les routes.** Dans routes/web.php, ajoutez l'import de AdminController, la route /accueil et le groupe protégé par permission **à l'intérieur** du groupe auth déjà présent. Les routes existantes restent en place. Voici ce que le fichier contient à la fin de l'étape (les lignes ajoutées sont signalées) :

```php
use App\Http\Controllers\AdminController;
use App\Http\Controllers\DashboardController;

// Publique : visiteur, utilisateur, administrateur (ajouté à l'étape 6)
Route::view('/accueil', 'accueil')->name('accueil');

// Authentifié : utilisateur et administrateur
Route::middleware('auth')->group(function () {
    Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');

    // Ajouté à l'étape 6.
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

**Mémo — Pourquoi auth d'abord.** Les middlewares s'exécutent dans l'ordre. Si permission passait avant auth, un visiteur recevrait une 403 « accès refusé » au lieu d'une invitation à se connecter. Le message serait faux, et l'utilisateur ne saurait pas quoi faire.

**Mémo — Pourquoi /login renvoie vers /dashboard.** La matrice annonce qu'une personne déjà connectée qui demande /login reçoit une 302 vers /dashboard. Ce n'est pas la clé home de Fortify qui décide : elle ne sert qu'après une connexion ou une inscription réussie. C'est le middleware guest de Laravel : il cherche une route **nommée** dashboard, puis home, et à défaut renvoie vers /. Cela fonctionne donc grâce au ->name('dashboard') de la route /dashboard. Si vous renommiez cette route, /login renverrait vers / et le test, qui ne vérifie que le code 302, resterait vert.

**Faire — compléter le tableau de bord.** Dans resources/views/dashboard.blade.php (créé à l'étape 3), ajoutez ces lignes entre le titre `<h1>` et le formulaire de déconnexion :

```html
<p>Rôle(s) : {{ auth()->user()->getRoleNames()->implode(', ') }}</p>

{{-- Confort d'affichage uniquement : ce n'est PAS une protection --}}
@can('gerer-utilisateurs')
    <p><a href="{{ route('admin.users') }}">Gestion des utilisateurs</a></p>
@endcan
```

Créez resources/views/admin/users.blade.php. Elle affiche un tableau des utilisateurs reçus dans $users, avec trois colonnes : nom, e-mail, rôles. Pour les rôles d'un utilisateur : $user->getRoleNames()->implode(', '). Ajoutez un lien de retour vers route('dashboard').

**Faire — la page d'accueil, qui change selon le profil.** Créez resources/views/accueil.blade.php :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>Accueil</title>
</head>
<body>
    <h1>Accueil</h1>

    {{-- Visiteur : personne n'est connecté --}}
    @guest
        <p>Vous naviguez en visiteur.</p>
        <p><a href="{{ route('login') }}">Se connecter</a> · <a href="{{ route('register') }}">Créer un compte</a></p>
    @endguest

    {{-- Utilisateur connecté, droits limités --}}
    @role('utilisateur')
        <p>Espace utilisateur : retrouvez votre tableau de bord.</p>
    @endrole

    {{-- Administrateur --}}
    @role('administrateur')
        <p>Espace administrateur : vous gérez les comptes.</p>
    @endrole

    {{-- Toute personne connectée, quel que soit son rôle --}}
    @auth
        <p><a href="{{ route('dashboard') }}">Tableau de bord</a></p>
    @endauth
</body>
</html>
```

Mémo — Quatre directives pour adapter une vue.

| Directive | Quand elle affiche son contenu | Exemple d'usage |
| --- | --- | --- |
| @guest | Personne n'est connecté | Profil visiteur |
| @auth | Quelqu'un est connecté, quel que soit son rôle | Lien vers le tableau de bord |
| @role('utilisateur') | La personne connectée a ce rôle | Message propre à chaque rôle |
| @can('gerer-utilisateurs') | La personne connectée a cette permission | Lien d'administration |

@role sert à personnaliser l'affichage : un message, une mise en page. Dès qu'un élément correspond à un droit (un lien vers une page protégée, un bouton d'action), utilisez @can avec la même permission que la route. @role ne plante pas pour un visiteur : Spatie vérifie d'abord que quelqu'un est connecté.

**Mémo — Masquer n'est pas protéger.** @can cache le lien, rien de plus : quiconque connaît l'URL peut la taper. La protection, c'est le middleware sur la route. Les deux doivent vérifier **la même permission**. Sinon, un utilisateur voit un lien qui mène à une 403, ou a accès à une page qu'aucun lien ne montre.

**Tests qui doivent passer :** test\_la\_matrice\_d\_acces\_est\_respectee (12 cas, un par case de la matrice), test\_un\_visiteur\_est\_redirige\_vers\_la\_connexion, test\_la\_page\_d\_administration\_liste\_les\_utilisateurs, test\_l\_accueil\_s\_adapte\_au\_profil, test\_le\_lien\_d\_administration\_suit\_la\_permission. Le test de déconnexion a déjà été validé à l'étape 3.

Exercice — masquer ou protéger ?

1. Retirez temporairement la protection : remplacez Route::middleware('permission:gerer-utilisateurs')->prefix('admin') par Route::prefix('admin').
2. Connectez-vous avec utilisateur@exemple.test (mot de passe password). Le lien n'apparaît pas. Tapez /admin/users dans la barre d'adresse : que voyez-vous ?
3. Lancez php artisan test --filter=AuthRbacTest. Quel cas de la matrice échoue ? PHPUnit affiche son nom.
4. Remettez la protection. Tout redevient vert.

Preuve

```bash
php artisan route:list --path=admin -v
```

L'option -v affiche les middlewares de chaque route. Copiez la sortie et vos observations des points 2 et 3. Vérifiez enfin à la main les 12 cases de la matrice d'accès avec les trois profils (fenêtre de navigation privée pour le visiteur), et notez ce qu'affiche /accueil pour chacun.

**Question 5.** Un collègue ajoute demain une route /admin/export en dehors du groupe protégé. Qu'est-ce qui empêcherait cette erreur de passer inaperçue ?

**Exercice bonus — le test qui aurait vu la faute.** Le contrat AuthRbacTest.php ne se modifie pas : créez un second fichier, tests/Feature/RoutesAdminTest.php, avec un test qui parcourt toutes les routes de l'application et vérifie que chaque route dont l'URL commence par admin porte le middleware permission:gerer-utilisateurs. Pistes : Route::getRoutes(), $route->uri(), $route->gatherMiddleware().

Vérifiez-le : ajoutez temporairement dans routes/web.php, hors du groupe protégé, la route /admin/export. Votre test doit échouer. Retirez la route : il redevient vert.
