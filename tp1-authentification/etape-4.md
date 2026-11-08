# Étape 4 : Protéger une page et adapter l'affichage

À la fin de cette étape, l'application respecte la matrice d'accès (le tableau de la section « Livrables » du README) pour les deux profils : le visiteur (non connecté) et la personne connectée. Un visiteur qui demande une page réservée est renvoyé vers la connexion, et la page d'accueil affiche un contenu différent selon qu'on est connecté ou non.

Le DashboardController, la route /dashboard (dans un groupe protégé par le middleware auth) et la déconnexion existent déjà (étape 2).

**Faire — la route de la page d'accueil.** Dans routes/web.php, ajoutez la route /accueil, qui est publique. Les routes existantes restent en place. Voici ce que le fichier contient à la fin de l'étape (la ligne ajoutée est signalée) :

```php
use App\Http\Controllers\DashboardController;

// Publique : visiteur et personne connectée (ajouté à l'étape 4)
Route::view('/accueil', 'accueil')->name('accueil');

// Réservé aux personnes connectées
Route::middleware('auth')->group(function () {
    Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');
});
```

**Faire — la page d'accueil, qui change selon que l'on est connecté.** Créez resources/views/accueil.blade.php :

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

    {{-- Toute personne connectée --}}
    @auth
        <p>Vous êtes identifié : {{ auth()->user()->name }}.</p>
        <p><a href="{{ route('dashboard') }}">Tableau de bord</a></p>
    @endauth
</body>
</html>
```

> [!NOTE]
> **Deux directives pour adapter une vue.**
>
> | Directive | Quand elle affiche son contenu | Exemple d'usage |
> | --- | --- | --- |
> | @guest | Personne n'est connecté | Message et liens du visiteur |
> | @auth | Quelqu'un est connecté | Lien vers le tableau de bord, nom de la personne |
>
> Elles servent à adapter l'affichage, rien de plus : elles ne protègent aucune page.

> [!NOTE]
> **Pourquoi /login renvoie vers /dashboard.** La matrice d'accès annonce qu'une personne déjà connectée qui demande /login reçoit une 302 vers /dashboard. Ce n'est pas la clé home de Fortify qui décide : elle ne sert qu'après une connexion ou une inscription réussie. C'est le middleware guest de Laravel : il cherche d'abord une route **nommée** dashboard, puis home. À défaut, il cherche une route dont l'**URI** est /dashboard, puis /home, et sinon renvoie vers /. Votre route /dashboard répond aux deux critères : son nom et son URI. Pour que /login ne renvoie plus vers /dashboard, il faudrait changer les deux. Notez enfin que le test ne vérifie que le code 302 de /login, pas la destination de la redirection.

**Tests qui doivent passer :** test\_la\_matrice\_d\_acces\_est\_respectee (6 cas, un par case de la matrice), test\_un\_visiteur\_est\_redirige\_vers\_la\_connexion, test\_l\_accueil\_s\_adapte\_au\_profil. Le contrat entier (20 tests) doit maintenant être vert.

**Exercice — masquer ou protéger ?**

Cet exercice et l'observation de /accueil (plus bas) utilisent le navigateur : le serveur de développement doit tourner. S'il est arrêté, relancez php artisan serve dans un terminal dédié.

1. Retirez temporairement la protection : remplacez Route::middleware('auth')->group(function () { par Route::group([], function () {.
2. Ouvrez une fenêtre de navigation privée (vous y êtes visiteur) et tapez /dashboard dans la barre d'adresse : que voyez-vous ? Le lien « Tableau de bord » reste invisible pour un visiteur sur /accueil, mais l'adresse, elle, répond.
3. Lancez php artisan test --filter=AuthenticationTest. Quels cas échouent ? PHPUnit affiche leur nom, mais il est coupé par « … » si la fenêtre du terminal est trop étroite : agrandissez-la. Le message de l'échec (code attendu, code reçu) aide aussi à les identifier.
4. Remettez la protection. Tout redevient vert.

**Preuve**

```bash
php artisan route:list --path=dashboard -v
```

L'option -v affiche les middlewares de chaque route. Copiez la sortie et vos observations des points 2 et 3.

Le test de la matrice a déjà vérifié les 6 cases : inutile de les refaire à la main. Il reste à voir ce que la matrice donne à l'écran. Ouvrez /accueil en visiteur (fenêtre de navigation privée), puis connecté avec alice@exemple.test, et notez ce qu'affiche la page pour chacun.

> **Question 3.** Sur /accueil, le lien « Tableau de bord » est masqué aux visiteurs par @auth. Qu'est-ce qui empêche réellement un visiteur d'ouvrir /dashboard ? Comment l'avez-vous prouvé ?
