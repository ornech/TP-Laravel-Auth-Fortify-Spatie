# Étape 4 : Protéger une page et adapter l'affichage

À la fin de cette étape, l'application respecte la matrice d'accès (le tableau de la section « Livrables » du README) pour les deux profils : 
- le visiteur (non connecté) sera renvoyé vers la page de connexion s'il demande un page réservée
- la page d'accueil affichera un contenu différent selon qu'on est connecté ou non

Le DashboardController, la route /dashboard (dans un groupe protégé par le middleware auth) et la déconnexion existent déjà (étape 2).

**Lancer les tests**

```bash
php artisan test --filter=AuthenticationTest
```

Vous retrouvez normalement 3 tests qui échouent qui concernae /accueil. 

Lisez-les :
- les deux cas de la matrice (« visiteur sur /accueil » et « connecté sur /accueil ») disent `Expected response status code [200] but received 404` : la page n'existe pas ;
- `test_l_accueil_s_adapte_au_profil` n'affiche qu'un long bloc de HTML, celui de la page d'erreur. Ne le lisez pas : un message de test n'est pas toujours le plus parlant, les cas de la matrice nomment le code.

Les 4 autres cases de la matrice (/login et /dashboard, pour les deux profils) sont déjà vertes : ce sont vos routes de l'étape 2.

**Faire — la route de la page d'accueil.** Dans routes/web.php, ajoutez la route /accueil, qui est publique. Les routes existantes restent en place. `Route::view('/accueil', 'accueil')` associe directement l'URL /accueil à la vue resources/views/accueil.blade.php, sans contrôleur ; `->name('accueil')` donne un nom à la route. La ligne est placée hors du groupe auth : elle n'a pas de middleware, donc tout le monde y accède (200). Voici ce que le fichier contient à la fin de l'étape (la ligne ajoutée est signalée) :

```php
<?php

use App\Http\Controllers\DashboardController;
use Illuminate\Support\Facades\Route;

// Racine : affiche la vue accueil.blade.php directement (closure)
Route::get('/', function () {
    return view('accueil');
});

// Raccourci équivalent à Route::get('/accueil', fn() => view('accueil'))
// ->name() permet d'utiliser route('accueil') dans les vues
Route::view('/accueil', 'accueil')->name('accueil');

// Groupe protégé : le middleware 'auth' redirige vers /login si non connecté
Route::middleware('auth')->group(function () {

    // Appelle la méthode index() de DashboardController
    Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');
});   
```

Avant de créer la vue relancer le test: 
``` php
php artisan test --filter='test_la_matrice_d_acces_est_respectee.*/accueil'
``` 
Les deux tests échouent, mais notez que le message a changé : `received 500`, avec pour cause `View [accueil] not found`. La route existe (on a plus le code 404), mainteant il manque la vue `accueil`.  

**Créez la blade accueil:** resources/views/accueil.blade.php :

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

**Vous devez maintenant voir** depuis le navigateur : 
- pour un visiteur, le titre « Accueil », le texte « Vous naviguez en visiteur. » et les liens « Se connecter » et « Créer un compte » ; 
- pour une personne connectée, « Vous êtes identifié : » suivi de son nom et le lien « Tableau de bord », sans le texte du visiteur.

> [!NOTE]
> **Deux directives pour adapter une vue.**
>
> | Directive | Quand elle affiche son contenu | Exemple d'usage |
> | --- | --- | --- |
> | @guest | Personne n'est connecté | Message et liens du visiteur |
> | @auth | Quelqu'un est connecté | Lien vers le tableau de bord, nom de la personne |
>
> Elles servent à adapter l'affichage, rien de plus : elles ne protègent aucune page.


**Relancer les test**

```bash
php artisan test --filter=AuthenticationTest
```

Le contrat entier devrait passer : **20 tests sur 20**. Copiez le résultat dans PREUVES.md.


**Exercice — masquer ou protéger ?**

Dans ce TP, « protéger une route » signifie lui associer un middleware qui vérifie une condition avant l'exécution du contrôleur. Pour /dashboard, c'est le middleware auth : il vérifie que la personne est connectée et, sinon, la renvoie vers /login. Dans cet exercice nous allons supprimer cette vérification, puis compare ce que montre l'écran (le lien masqué par @auth) et ce que fait la route.

1. Dans routes/web.php, la route /dashboard est déclarée dans un groupe créé par la ligne `Route::middleware('auth')->group(function () {`. L'appel `middleware('auth')` attache le middleware auth à toutes les routes du groupe. Remplacez cette ligne par `Route::group([], function () {` : le groupe existe toujours, avec les mêmes routes, mais sans middleware. Seule la vérification « la personne est connectée » disparaît.

```php
<?php

use App\Http\Controllers\DashboardController;
use Illuminate\Support\Facades\Route;

// Racine : affiche la vue accueil.blade.php directement (closure)
Route::get('/', function () {
    return view('accueil');
});

// Raccourci équivalent à Route::get('/accueil', fn() => view('accueil'))
// ->name() permet d'utiliser route('accueil') dans les vues
Route::view('/accueil', 'accueil')->name('accueil');

// Groupe protégé : le middleware 'auth' redirige vers /login si non connecté
// Route::middleware('auth')->group(function () {
Route::group([], function () {
    // Appelle la méthode index() de DashboardController
    Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');
});   
```

2. Ouvrez une fenêtre de navigation privée (vous y êtes visiteur). Sur /accueil, le lien « Tableau de bord » n'est pas affiché à un visiteur. Tapez ensuite /dashboard dans la barre d'adresse et notez ce que vous voyez.
3. **Prédisez** d'abord quels tests vont échouer : écrivez votre liste dans PREUVES.md. Puis lancez php artisan test --filter=AuthenticationTest. Quels cas échouent, et votre liste était-elle juste ? PHPUnit affiche leur nom, mais il est coupé par « … » si la fenêtre du terminal est trop étroite : agrandissez-la. Le message de l'échec (code attendu, code reçu) aide aussi à les identifier.
4. Remettez la ligne d'origine, `Route::middleware('auth')->group(function () {`, et relancez les tests : 20 verts.

Résultat attendu, à comparer avec votre observation :

- point 2 : une page d'erreur 500 dont le message est `Attempt to read property "name" on null`.![alt text](image.png)
  Sans le middleware `auth`, la requête atteint le contrôleur et la vue, a qui l'on demande de récupérer la propriété `name` d'un compte qui n'est pas connecté mais surtout il n'y a pas de redirection vers /login ;
- point 3 : 3 tests échouent
  ![alt text](image-1.png)
  , le cas « visiteur sur /dashboard » de la matrice (302 attendu, 500 reçu), `test_un_visiteur_est_redirige_vers_la_connexion` et `test_la_deconnexion_detruit_la_session`.

**Preuve**

```bash
php artisan route:list --path=dashboard -v
```

L'option -v affiche les middlewares de chaque route, dans l'ordre où ils s'exécutent.

**Vous devez voir :**

```text
GET|HEAD  dashboard … dashboard › DashboardController@index
          ⇂ web
```

web est le groupe de middlewares commun à toutes les routes web (session, cookies, protection CSRF) ;

Réactiver le middleware auth pour les routes protégées :

fichier `routes/web.php`

```php
<?php
use App\Http\Controllers\DashboardController;
use Illuminate\Support\Facades\Route;

// Racine : affiche la vue accueil.blade.php directement (closure)
Route::get('/', function () {
    return view('accueil');
});

// Raccourci équivalent à Route::get('/accueil', fn() => view('accueil'))
// ->name() permet d'utiliser route('accueil') dans les vues
Route::view('/accueil', 'accueil')->name('accueil');

// Groupe protégé : le middleware 'auth' redirige vers /login si non connecté
Route::middleware('auth')->group(function () {

    // Appelle la méthode index() de DashboardController
    Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');
});   
```
Affihez de nouveau les middlewares de la route dashboard: 
```bash
php artisan route:list --path=dashboard -v

  GET|HEAD       dashboard ........................................................................... dashboard › DashboardController@index
                 ⇂ web
                 ⇂ auth
```
On retrouve bien le middleware auth qui vérifie si l'utilisateur est connecté et le redirige vers /login si ce n'est pas le cas.


> **Question 3.** Sur /accueil, le lien « Tableau de bord » est masqué aux visiteurs par @auth. Qu'est-ce qui empêche réellement un visiteur d'ouvrir /dashboard ? Comment l'avez-vous prouvé ?
