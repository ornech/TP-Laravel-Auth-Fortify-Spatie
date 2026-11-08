# Étape 2 : Installer Fortify

À la fin de cette étape, on sera en mesure de s'inscrire, de se connecter, de se déconnecter et l’on fera en sorte que Fortify n'expose que les routes dont l'application a besoin.

**Faire**

```bash
composer require laravel/fortify
php artisan fortify:install
php artisan migrate
```

Cette migration ajoute à la table users les colonnes de la double authentification (two\_factor\_\*) et crée une table passkeys. Ces fonctionnalités seront désactivées plus bas : les colonnes et la table existeront, mais resteront vides et inutilisées.

## Limitez le nombre de routes exposées

Une fois installé, Fortify expose environ trente routes : réinitialisation de mot de passe, double authentification, passkeys, modification du profil… Ce TP n'en utilise que quelques-unes.

**Faire :** Dans config/fortify.php, ne gardez que l'inscription dans la liste des features. Commentez les autres lignes ; la liste exacte dépend de votre version de Fortify.

```php
'features' => [
    Features::registration(),
    // Features::resetPasswords(),
    // Features::emailVerification(),
    // Features::updateProfileInformation(),
    // Features::updatePasswords(),
    // Features::twoFactorAuthentication([...]),
    // Features::passkeys([...]),
],
```

Dans le fichier généré, twoFactorAuthentication([...]) et passkeys([...]) s'étendent sur plusieurs lignes. Commentez **toutes** les lignes de chaque entrée, jusqu'au ]), inclus (sélectionnez-les et utilisez Ctrl+/). Si vous ne commentez que la première, le fichier n'est plus du PHP valide et l'application plante.

> [!NOTE]
> **Mémo:** Chaque fonctionnalité (feature) activée est une route accessible et donc une surface d'attaque et du code à maintenir. Exemple concret : resetPasswords actif sans vue déclarée, et /forgot-password répond par une erreur 500.
>
> **Règle : on n'active que ce qu'on utilise et qu'on a testé.**

**Vérifier**

```bash
php artisan route:list --only-vendor
```

Copiez la sortie dans PREUVES.md. Vous devez y retrouver les routes que ce TP utilise : GET et POST /login, POST /logout, GET et POST /register. Les autres lignes ne sont pas des fonctionnalités que vous avez activées : up (contrôle de santé) et storage/{path} viennent de Laravel, et les trois routes user/confirm-password et user/confirmed-password-status viennent de Fortify, qui les enregistre toujours. Le TP ne les utilise pas et aucune vue n'est déclarée pour elles : une personne connectée qui demande GET /user/confirm-password obtient une erreur 500. Désactiver les features réduit donc la surface exposée, sans la ramener à zéro.

**Faire : la page home**

Dans config/fortify.php, la clé home vaut /home par défaut. Cette route n'existe pas dans votre application : sans modification, chaque connexion aboutira à une erreur 404.

Modifiez config/fortify.php

```php
'home' => '/dashboard',
```

La page /dashboard sera créée plus bas, dans cette étape.

## **Création de la vue de connexion**

**Faire : déclarer les vues.**

Dans app/Providers/FortifyServiceProvider.php, ajoutez ces deux lignes à la fin de la méthode boot(). Ne supprimez rien de ce qui s'y trouve.

```php
        Fortify::loginView(fn () => view('auth.login'));
        Fortify::registerView(fn () => view('auth.register'));
```

> [!WARNING]
> **Mémo — Ce que boot() contient déjà, et pourquoi il ne faut pas l'écraser.**
>
> | Ligne de boot() | Si vous la supprimez |
> | --- | --- |
> | Fortify::createUsersUsing(CreateNewUser::class) | L'inscription plante : Fortify ne sait plus quelle classe crée les comptes |
> | RateLimiter::for('login', ...) | Toute connexion renvoie une 500 « Rate limiter \[login\] is not defined. » |
> | RateLimiter::for('two-factor', ...) | Les routes de double authentification plantent, si cette fonctionnalité est active |
>
> Les autres lignes de boot() (updateUserProfileInformationUsing, updateUserPasswordsUsing, resetUserPasswordsUsing, redirectUserForTwoFactorAuthenticationUsing et le limiteur passkeys) servent aux fonctionnalités désactivées à cette étape. Elles ne gênent pas : laissez-les en place et ne supprimez rien.

**Faire — la vue de connexion.** Créez resources/views/auth/login.blade.php à partir de ce modèle commenté :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>Connexion</title>
</head>
<body>
    <h1>Connexion</h1>

    {{-- Erreurs renvoyées par Fortify, par exemple des identifiants incorrects --}}
    @if ($errors->any())
        <ul>
            @foreach ($errors->all() as $message)
                <li>{{ $message }}</li>
            @endforeach
        </ul>
    @endif

    {{-- Même URL que la page (/login), mais en POST : c'est Fortify qui traite --}}
    <form method="POST" action="{{ route('login') }}">
        @csrf

        <label for="email">E-mail</label>
        <input id="email" type="email" name="email" value="{{ old('email') }}" required autofocus>

        <label for="password">Mot de passe</label>
        <input id="password" type="password" name="password" required>

        <label><input type="checkbox" name="remember"> Rester connecté</label>

        <button type="submit">Se connecter</button>
    </form>

    <p><a href="{{ route('register') }}">Créer un compte</a></p>
</body>
</html>
```

**Ce qui compte dans ce formulaire.**

| Élément | Rôle |
| --- | --- |
| **@csrf** | Ajoute un jeton de protection contre la falsification de requêtes (voir le mémo ci-dessous) |
| **old('email')** | Réaffiche l'e-mail saisi après une erreur. On ne réaffiche jamais un mot de passe. |
| **$errors** | Contient les messages d'erreur renvoyés par Fortify |
| **name="email", name="password"** | Les noms que Fortify attend. Un autre nom, et la connexion échoue. |

> [!NOTE]
> **Mémo: La protection CSRF de Laravel.**
>
> Laravel 13 vérifie qu'un POST vient bien de votre site en deux temps :
>
> - **Origine** : si l'en-tête Sec-Fetch-Site vaut same-origin, la requête est acceptée sans vérification du jeton. Cet en-tête est ajouté par le navigateur, pas par Laravel : les navigateurs ne l'envoient que vers des adresses jugées sûres (HTTPS, mais aussi localhost et 127.0.0.1, même en HTTP). Un outil comme curl ne l'envoie pas.
> - **Jeton** : si l'en-tête est absent (curl, ancien navigateur, adresse HTTP non sûre) ou ne vaut pas same-origin, Laravel compare le jeton \_token à celui de la session.
>
> Si les deux échouent → 419 page expired ou 403 en mode originOnly.
>
> Conseil : gardez **@csrf** dans vos formulaires: c'est gratuit, simple et couvre les cas où Sec-Fetch-Site serait absent.

## **Création du tableau de bord minimal et de la déconnexion**

Après une connexion réussie, Fortify redirige vers la page de la clé home (/dashboard). Cette page doit exister, et elle doit offrir un moyen de se déconnecter : sans lui, vous resteriez connecté et ne pourriez plus atteindre le formulaire de connexion (une personne déjà connectée qui demande /login est redirigée ailleurs). Vous créez ici une version minimale.

**Faire — le contrôleur.**

```bash
php artisan make:controller DashboardController
```

Ajoutez une méthode index() dans DashboardController :

```php
public function index()
{
    return view('dashboard');
}
```

**Faire — la route.** Dans routes/web.php, ajoutez l'import et ce bloc. Les routes existantes restent en place.

```php
use App\Http\Controllers\DashboardController;

// Réservé aux personnes connectées
Route::middleware('auth')->group(function () {
    Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');
});
```

**Faire — la vue.** Créez resources/views/dashboard.blade.php :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>Tableau de bord</title>
</head>
<body>
    <h1>Bonjour {{ auth()->user()->name }}</h1>

    {{-- Déconnexion en POST, avec jeton CSRF --}}
    <form method="POST" action="{{ route('logout') }}">
        @csrf
        <button type="submit">Se déconnecter</button>
    </form>
</body>
</html>
```

La route POST /logout est fournie par Fortify : vous n'avez rien à écrire côté serveur. Après la déconnexion, Fortify redirige vers /.

> [!NOTE]
> **Mémo — Pourquoi la déconnexion est un POST ?**
>
> Une action qui modifie l’état ne doit pas être déclenchable par une simple URL. Avec un GET, n’importe quel site pourrait déconnecter vos utilisateurs, avec un lien vers https://votresite/logout ou en redirigeant vers cette adresse : le navigateur suit le lien en envoyant le cookie de session. Un POST avec la protection CSRF de Laravel refusera la requête venue d’un autre site.

## **Création de la vue d'inscription**

**Faire : écrivez la vue d'inscription vous-même.** Créez le fichier resources/views/auth/register.blade.php sur le modèle de la connexion. Le formulaire envoie en POST vers route('register'), contient @csrf et affiche les erreurs.

| Libellé | Attribut name | Type |
| --- | --- | --- |
| Nom | name | text |
| E-mail | email | email |
| Mot de passe | password | password |
| Confirmation | password\_confirmation | password |

Le nom password\_confirmation n'est pas libre : la règle de validation confirmed cherche un champ nommé \<champ>\_confirmation.

L'inscription est traitée par l'action app/Actions/Fortify/CreateNewUser.php, générée par fortify:install : elle valide les champs, puis crée le compte avec un mot de passe **haché**. Ouvrez-la et lisez-la.

**Preuve**

Lancez le serveur de développement dans un terminal dédié et laissez-le tourner jusqu'à la fin de l'étape (arrêt avec Ctrl+C). Vous le relancerez de la même façon aux étapes 3 et 4, qui utilisent le navigateur :

```bash
php artisan serve
```

Le TP utilise l'adresse http://127.0.0.1:8000, affichée par la commande.

1. Inscrivez un nouveau compte dans le navigateur, sur http://127.0.0.1:8000/register (mot de passe d'au moins 8 caractères). Vous arrivez sur /dashboard, qui affiche « Bonjour » suivi de votre nom. Notez l'URL obtenue. Cliquez sur « Se déconnecter » et notez l'URL obtenue. Les messages d'erreur de Laravel (mot de passe trop court, confirmation différente…) s'affichent en anglais : c'est normal, la langue de l'application est l'anglais par défaut.
2. Retirez @csrf de la vue de connexion et connectez-vous avec alice@exemple.test (mot de passe password) dans le navigateur, sur http://127.0.0.1:8000 (la page d'accueil de Laravel propose un lien « Log in »). Notez si la connexion fonctionne, remettez @csrf, puis déconnectez-vous.
3. Envoyez la même requête sans navigateur, depuis un second terminal (le serveur lancé plus haut doit tourner) : curl -i -X POST http://127.0.0.1:8000/login -d "email=alice@exemple.test" -d "password=password". Sous Windows PowerShell, tapez curl.exe. Notez le code HTTP de la première ligne. Vous lirez « HTTP/1.1 419 unknown status » : « unknown status » est le libellé du serveur de développement PHP, le code est bien 419.
4. Tentez six connexions avec un mauvais mot de passe en moins d'une minute, avec le compte bob@exemple.test, sur lequel vous ne vous êtes pas encore connecté. Notez ce qui s'affiche à la sixième. Une connexion réussie compte aussi dans la limite : sur un compte où vous venez de vous connecter (alice@exemple.test à la preuve 2), le blocage arriverait dès la cinquième tentative.

**Tests qui doivent passer :** test\_seules\_les\_fonctionnalites\_utiles\_sont\_exposees, test\_les\_fonctionnalites\_de\_profil\_et\_de\_mot\_de\_passe\_sont\_desactivees, test\_le\_mot\_de\_passe\_doit\_etre\_confirme, test\_une\_connexion\_valide\_ouvre\_une\_session, test\_un\_mauvais\_mot\_de\_passe\_est\_refuse, test\_la\_connexion\_est\_bloquee\_apres\_cinq\_echecs, test\_les\_echecs\_d\_un\_compte\_ne\_bloquent\_pas\_les\_autres\_comptes, test\_la\_deconnexion\_n\_accepte\_que\_post, test\_l\_inscription\_cree\_un\_compte\_connecte.

**Question 1.** Le limiteur de boot() compte les tentatives par couple « e-mail + adresse IP ». Quel problème poserait un comptage par adresse IP seule dans un lycée où tous les postes sortent par la même IP ? Quelle attaque ce couple ne bloque-t-il pas ?

Suite : l'étape 3 regarde ce qui s'est passé dans la base et dans les cookies pendant ces connexions.
