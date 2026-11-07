# Étape 3: Installer Fortify

À la fin de cette étape, on sera en mesure de s'inscrire, de se connecter, de se déconnecter et l’on fera en sorte que Fortify n'expose que les routes dont l'application a besoin.

**A faire**

```bash
composer require laravel/fortify
php artisan fortify:install
php artisan migrate
```

## Limitez le nombre de routes exposées

**Avant ...**

```bash
php artisan route:list --only-vendor
```

Copiez la sortie et notez le nombre de routes dans PREUVES.md.

**A faire:** Dans config/fortify.php, ne gardez que l'inscription dans la liste des features. Commentez les autres lignes ; la liste exacte dépend de votre version de Fortify.

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

> [!NOTE]
> **Mémo:** Chaque fonctionnalité (feature) activée est une route accessible et donc une surface d'attaque et du code à maintenir. Exemple concret : resetPasswords actif sans vue déclarée, et /forgot-password répond par une erreur 500.
>
> **Règle : on n'active que ce qu'on utilise et qu'on a testé.**

**Après ...**

```bash
php artisan route:list --only-vendor
```

Copiez la sortie et comparez le nombre de routes avec la preuve « avant ».

**A faire: la page home**

Dans config/fortify.php, la clé home vaut /home par défaut. Cette route n'existe pas dans votre application : sans modification, chaque connexion aboutira à une erreur 404.

Modifiez config/fortify.php

```php
'home' => '/dashboard',
```

La page /dashboard sera créée plus bas, dans cette étape.

## **Création de la vue de connexion**

**A faire: déclarer les vues.**

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

Après une connexion réussie, Fortify redirige vers la page de la clé home (/dashboard). Cette page doit exister, et elle doit offrir un moyen de se déconnecter : sans lui, vous resteriez connecté et ne pourriez plus atteindre le formulaire de connexion (une personne déjà connectée qui demande /login est redirigée ailleurs). Vous créez ici une version minimale, que l'étape 6 complètera.

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

// Authentifié : utilisateur et administrateur
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

**A faire: Écrivez la vue d'inscription vous-même.** Créez le fichier resources/views/auth/register.blade.php sur le modèle de la connexion. Le formulaire envoie en POST vers route('register'), contient @csrf et affiche les erreurs.

| Libellé | Attribut name | Type |
| --- | --- | --- |
| Nom | name | text |
| E-mail | email | email |
| Mot de passe | password | password |
| Confirmation | password\_confirmation | password |

Le nom password\_confirmation n'est pas libre : la règle de validation confirmed cherche un champ nommé \<champ>\_confirmation.

Preuve

1. Inscrivez un nouveau compte dans le navigateur. Vous arrivez sur /dashboard, qui affiche « Bonjour » suivi de votre nom. Notez l'URL obtenue. Cliquez sur « Se déconnecter » et notez l'URL obtenue.
2. Retirez @csrf de la vue de connexion et connectez-vous dans le navigateur sur http://127.0.0.1:8000. Notez si la connexion fonctionne, remettez @csrf, puis déconnectez-vous.
3. Envoyez la même requête sans navigateur, depuis un second terminal (php artisan serve doit tourner) : curl -i -X POST http://127.0.0.1:8000/login -d "email=utilisateur@exemple.test" -d "password=password". Sous Windows PowerShell, tapez curl.exe. Notez le code HTTP de la première ligne.
4. Tentez six connexions avec un mauvais mot de passe en moins d'une minute, avec le compte admin@exemple.test. Notez ce qui s'affiche à la sixième. Une connexion réussie compte aussi dans la limite : sur un compte où vous venez de vous connecter (preuve 2), le blocage arriverait dès la cinquième tentative.

**Tests qui doivent passer :** test\_seules\_les\_fonctionnalites\_utiles\_sont\_exposees, test\_le\_mot\_de\_passe\_doit\_etre\_confirme, test\_la\_connexion\_est\_bloquee\_apres\_cinq\_echecs, test\_la\_deconnexion\_n\_accepte\_que\_post.

**Question 2.** Le limiteur de boot() compte les tentatives par couple « e-mail + adresse IP ». Quel problème poserait un comptage par adresse IP seule dans un lycée où tous les postes sortent par la même IP ? Quelle attaque ce couple ne bloque-t-il pas ?
