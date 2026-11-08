# Étape 5 : Protéger les routes et compléter les pages

À la fin de cette étape, l'application respecte la matrice d'accès de l'administration (le tableau de la section « Livrables » du README) : un visiteur est renvoyé vers la connexion, un utilisateur reçoit une 403, l'administrateur accède à la page. L'accueil et le tableau de bord affichent un contenu différent selon le rôle.

Le DashboardController, la route /dashboard, la déconnexion et la page /accueil existent déjà (TP 1) : vous les complétez.

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

// Publique : visiteur et personne connectée
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

> [!NOTE]
> **Pourquoi auth d'abord.** Les middlewares s'exécutent dans l'ordre. Si permission passait avant auth, un visiteur recevrait une 403 « accès refusé » au lieu d'une invitation à se connecter. Le message serait faux, et l'utilisateur ne saurait pas quoi faire.

**Faire — compléter le tableau de bord.** Dans resources/views/dashboard.blade.php (créé au TP 1), ajoutez ces lignes entre le titre `<h1>` et le formulaire de déconnexion :

```html
<p>Rôle(s) : {{ auth()->user()->getRoleNames()->implode(', ') }}</p>

{{-- Confort d'affichage uniquement : ce n'est PAS une protection --}}
@can('gerer-utilisateurs')
    <p><a href="{{ route('admin.users') }}">Gestion des utilisateurs</a></p>
@endcan
```

**Faire — la page d'administration.** Créez resources/views/admin/users.blade.php. Elle affiche un tableau des utilisateurs reçus dans $users, avec trois colonnes : nom, e-mail, rôles. Pour les rôles d'un utilisateur : $user->getRoleNames()->implode(', '). Ajoutez un lien de retour vers route('dashboard').

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

> [!NOTE]
> **Deux directives de Spatie pour adapter une vue.** Elles s'ajoutent à @guest et @auth, vues au TP 1.
>
> | Directive | Quand elle affiche son contenu | Exemple d'usage |
> | --- | --- | --- |
> | @role('utilisateur') | La personne connectée a ce rôle | Message propre à chaque rôle |
> | @can('gerer-utilisateurs') | La personne connectée a cette permission | Lien d'administration |
>
> @role sert à personnaliser l'affichage : un message, une mise en page. Dès qu'un élément correspond à un droit (un lien vers une page protégée, un bouton d'action), utilisez @can avec la même permission que la route. @role ne plante pas pour un visiteur : Spatie vérifie d'abord que quelqu'un est connecté.

> [!WARNING]
> **Masquer n'est pas protéger.** @can cache le lien, rien de plus : quiconque connaît l'URL peut la taper. La protection, c'est le middleware sur la route. Les deux doivent vérifier **la même permission**. Sinon, un utilisateur voit un lien qui mène à une 403, ou a accès à une page qu'aucun lien ne montre.

**Tests qui doivent passer :** test\_la\_matrice\_d\_acces\_est\_respectee (3 cas, un par profil), test\_un\_visiteur\_n\_atteint\_pas\_l\_administration, test\_la\_page\_d\_administration\_liste\_les\_utilisateurs, test\_l\_accueil\_s\_adapte\_au\_role, test\_le\_lien\_d\_administration\_suit\_la\_permission, test\_un\_autre\_role\_ayant\_la\_permission\_accede\_a\_l\_administration, test\_un\_autre\_role\_ayant\_la\_permission\_voit\_le\_lien\_d\_administration, test\_un\_compte\_sans\_role\_ne\_peut\_pas\_administrer, test\_retirer\_le\_role\_administrateur\_retire\_l\_acces. Les 20 tests du TP 1 doivent rester verts. Pour lancer les deux contrats ensemble (34 tests) : php artisan test --filter="AuthenticationTest|AuthorizationTest"

**Exercice — masquer ou protéger ?**

Cet exercice et l'observation de /accueil (plus bas) utilisent le navigateur : le serveur de développement doit tourner. S'il est arrêté, relancez php artisan serve dans un terminal dédié.

1. Retirez temporairement la protection : remplacez Route::middleware('permission:gerer-utilisateurs')->prefix('admin') par Route::prefix('admin').
2. Connectez-vous avec utilisateur@exemple.test (mot de passe password). Le lien n'apparaît pas. Tapez /admin/users dans la barre d'adresse : que voyez-vous ?
3. Lancez php artisan test --filter=AuthorizationTest. Quels tests échouent, et pourquoi ? PHPUnit affiche leurs noms, mais ils sont coupés par « … » si la fenêtre du terminal est trop étroite : agrandissez-la. Le message de chaque échec (code attendu, code reçu) aide à les comprendre.
4. Remettez la protection. Tout redevient vert.

**Preuve**

```bash
php artisan route:list --path=admin -v
```

L'option -v affiche les middlewares de chaque route. Copiez la sortie et vos observations des points 2 et 3.

Le test de la matrice a déjà vérifié les 3 cases : inutile de les refaire à la main. Il reste à voir ce que les rôles donnent à l'écran. Ouvrez /accueil connecté avec utilisateur@exemple.test, puis avec admin@exemple.test (déconnectez-vous entre les deux), et notez ce qu'affiche la page pour chacun.

> **Question 4.** Un collègue ajoute demain une route /admin/export en dehors du groupe protégé. Qu'est-ce qui empêcherait cette erreur de passer inaperçue ?

**Exercice bonus — le test qui aurait vu la faute.** Le contrat AuthorizationTest.php ne se modifie pas : créez un second fichier, tests/Feature/RoutesAdminTest.php, avec un test qui parcourt toutes les routes de l'application et vérifie que chaque route dont l'URL commence par admin porte le middleware permission:gerer-utilisateurs. Pistes : Route::getRoutes(), $route->uri(), $route->gatherMiddleware().

Vérifiez-le : ajoutez temporairement dans routes/web.php, hors du groupe protégé, la route /admin/export. Votre test doit échouer. Retirez la route : il redevient vert.
