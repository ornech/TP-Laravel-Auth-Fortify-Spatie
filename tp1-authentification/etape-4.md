# Étape 4 : Protéger une page et adapter l'affichage

À la fin de cette étape, l'application respecte la matrice d'accès (le tableau de la section « Livrables » du README) pour les deux profils : le visiteur (non connecté) et la personne connectée. Un visiteur qui demande une page réservée est renvoyé vers la connexion, et la page d'accueil affiche un contenu différent selon qu'on est connecté ou non.

Le DashboardController, la route /dashboard (dans un groupe protégé par le middleware auth) et la déconnexion existent déjà (étape 2).

**Lancer (avant d'agir)**

```bash
php artisan test --filter=AuthenticationTest
```

Vous retrouvez 17 tests verts et 3 rouges. Les trois rouges sont ceux qui concernent /accueil. Lisez-les :

- les deux cas de la matrice (« visiteur sur /accueil » et « connecté sur /accueil ») disent `Expected response status code [200] but received 404` : la page n'existe pas ;
- `test_l_accueil_s_adapte_au_profil` n'affiche qu'un long bloc de HTML, celui de la page d'erreur. Ne le lisez pas : un message de test n'est pas toujours le plus parlant, les cas de la matrice nomment le code.

Les 4 autres cases de la matrice (/login et /dashboard, pour les deux profils) sont déjà vertes : ce sont vos routes de l'étape 2.

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

**Relancer**, avant de créer la vue : `php artisan test --filter='test_la_matrice_d_acces_est_respectee.*/accueil'`. Les deux cas restent rouges, mais le message a changé : `received 500`, avec la cause en dessous, `View [accueil] not found`. La route existe (plus de 404), il manque la vue.

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

**Relancer**

```bash
php artisan test --filter=AuthenticationTest
```

Le contrat entier est vert : **20 tests sur 20**. Sur les 3 rouges du début de l'étape, ce sont les trois que vous venez de faire passer ; les 17 autres étaient déjà verts. Copiez la ligne de résultat dans PREUVES.md.

La redirection du visiteur (`test_un_visiteur_est_redirige_vers_la_connexion`) et la matrice sont vertes depuis l'étape 2 : ce que vous ajoutez ici, c'est surtout l'**exercice** ci-dessous, qui vérifie que ces tests savent échouer.

**Exercice — masquer ou protéger ?**

Dans ce TP, « protéger une route » signifie lui associer un middleware qui vérifie une condition avant l'exécution du contrôleur. Pour /dashboard, c'est le middleware auth : il vérifie que la personne est connectée et, sinon, la renvoie vers /login. L'exercice supprime cette vérification, puis compare ce que montre l'écran (le lien masqué par @auth) et ce que fait la route.

Cet exercice et l'observation de /accueil (plus bas) utilisent le navigateur : le serveur de développement doit tourner. S'il est arrêté, relancez php artisan serve dans un terminal dédié.

1. Dans routes/web.php, la route /dashboard est déclarée dans un groupe créé par la ligne `Route::middleware('auth')->group(function () {`. L'appel `middleware('auth')` attache le middleware auth à toutes les routes du groupe. Remplacez cette ligne par `Route::group([], function () {` : le groupe existe toujours, avec les mêmes routes, mais sans middleware. Seule la vérification « la personne est connectée » disparaît.
2. Ouvrez une fenêtre de navigation privée (vous y êtes visiteur). Sur /accueil, le lien « Tableau de bord » n'est pas affiché à un visiteur. Tapez ensuite /dashboard dans la barre d'adresse et notez ce que vous voyez.
3. **Prédisez** d'abord quels tests vont échouer : écrivez votre liste dans PREUVES.md. Puis lancez php artisan test --filter=AuthenticationTest. Quels cas échouent, et votre liste était-elle juste ? PHPUnit affiche leur nom, mais il est coupé par « … » si la fenêtre du terminal est trop étroite : agrandissez-la. Le message de l'échec (code attendu, code reçu) aide aussi à les identifier.
4. Remettez la ligne d'origine, `Route::middleware('auth')->group(function () {`, et relancez les tests : 20 verts.

**Preuve**

```bash
php artisan route:list --path=dashboard -v
```

L'option -v affiche les middlewares de chaque route. Copiez la sortie et vos observations des points 2 et 3.

Le test de la matrice a déjà vérifié les 6 cases : inutile de les refaire à la main. Il reste à observer l'affichage de /accueil. Ouvrez /accueil en visiteur (fenêtre de navigation privée), puis connecté avec alice@exemple.test, et notez ce qu'affiche la page pour chacun.

> **Question 3.** Sur /accueil, le lien « Tableau de bord » est masqué aux visiteurs par @auth. Qu'est-ce qui empêche réellement un visiteur d'ouvrir /dashboard ? Comment l'avez-vous prouvé ?
