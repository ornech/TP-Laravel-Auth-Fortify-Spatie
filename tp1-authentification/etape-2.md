# Étape 2 : Installer Fortify

À la fin de cette étape, on sera en mesure de s'inscrire, de se connecter, de se déconnecter et l’on fera en sorte que Fortify n'expose que les routes dont l'application a besoin.

Cette étape suit la boucle de test de l'étape 1 : avant chaque action, vous lancez le test concerné, vous lisez son message d'échec, vous agissez, puis vous relancez. Les messages indiqués dans l'énoncé sont ceux que vous devez obtenir : s'ils diffèrent, relisez l'action précédente.

**Faire**

```bash
composer require laravel/fortify
php artisan fortify:install
php artisan migrate
```

| Commande | Effet |
| --- | --- |
| composer require laravel/fortify | Télécharge le package dans vendor/. |
| php artisan fortify:install | Copie dans votre projet config/fortify.php (liste des fonctionnalités), app/Providers/FortifyServiceProvider.php (enregistré dans bootstrap/providers.php), les actions de app/Actions/Fortify (dont CreateNewUser) et deux migrations. |
| php artisan migrate | Exécute les migrations. |

Ces migrations ajoutent à la table users les colonnes de la double authentification (two\_factor\_\*) et créent une table passkeys. Ces fonctionnalités seront désactivées plus bas : les colonnes et la table existeront, mais resteront vides et inutilisées.

> [!NOTE]
> **Double authentification et passkeys.** La **double authentification** demande un second code en plus du mot de passe (colonnes two\_factor\_\*). Les **passkeys** sont une connexion sans mot de passe, par clé cryptographique de l'appareil (table passkeys).

## Avant de configurer quoi que ce soit

Fortify est installé, mais vous n'avez rien configuré : pas de fonctionnalité réduite, pas de vue, pas de page d'arrivée.

**Prédire.** Sur les 20 tests, combien passent déjà ? Notez votre pari dans PREUVES.md.

**Lancer**

```bash
php artisan test --filter=AuthenticationTest
```

Vous obtenez **7 tests verts et 13 rouges** (le test du seeder, vert depuis l'étape 1, est l'un des 7). Notez la ligne de résultat et la liste des tests verts dans PREUVES.md.

**Question A.** Aucun des autres verts ne dépend d'une ligne que vous avez écrite. Qu'est-ce qui les rend verts ? Un test vert avant votre action prouve-t-il votre travail ? À quoi sert-il alors ?

## Limitez le nombre de routes exposées

Une fois installé, Fortify expose environ trente routes : réinitialisation de mot de passe, double authentification, passkeys, modification du profil… Ce TP n'en utilise que quelques-unes.

**Lancer (avant d'agir)**

```bash
php artisan test --filter="test_seules_les_fonctionnalites_utiles_sont_exposees|test_les_fonctionnalites_de_profil_et_de_mot_de_passe_sont_desactivees"
```

Les deux tests sont rouges, et chaque message nomme ce qui est en trop : `La réinitialisation de mot de passe doit être désactivée.` et `La modification du profil doit être désactivée.` Le test s'arrête à la première assertion qui échoue : un autre message peut apparaître une fois ce premier point réglé.

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
> Chaque fonctionnalité (feature) activée est une route accessible et donc une **surface d'attaque** (l'ensemble des points par où une attaque peut entrer) et du code à maintenir. Exemple concret : resetPasswords actif sans vue déclarée, et /forgot-password répond par une erreur 500.
>
> **Règle : on n'active que ce qu'on utilise et qu'on a testé.**

**Relancer** la même commande. Les deux tests sont verts. Si le premier reste rouge avec le message `Les passkeys (connexion sans mot de passe) doivent être désactivées.`, il reste des lignes de Features::passkeys non commentées.

**Vérifier**

```bash
php artisan route:list --only-vendor
```

L'option --only-vendor ne liste que les routes qui viennent d'un package. Vous devez obtenir **exactement 11 lignes** : si vous en avez 18, des routes passkeys y figurent encore. Copiez la sortie dans PREUVES.md. Vous devez y retrouver les routes que ce TP utilise : GET et POST /login, POST /logout, GET et POST /register. Les autres lignes ne sont pas des fonctionnalités que vous avez activées : up (contrôle de santé) et storage/{path} viennent de Laravel, et les trois routes user/confirm-password et user/confirmed-password-status viennent de Fortify, qui les enregistre toujours. Le TP ne les utilise pas et aucune vue n'est déclarée pour elles : une personne connectée qui demande GET /user/confirm-password obtient une erreur 500. Désactiver les features réduit donc la surface exposée, sans la ramener à zéro.

## La page d'arrivée après connexion

Dans config/fortify.php, la clé home vaut /home par défaut. Cette route n'existe pas dans votre application.

**Lancer (avant d'agir)**

```bash
php artisan test --filter="test_une_connexion_valide_ouvre_une_session|test_les_echecs_d_un_compte_ne_bloquent_pas_les_autres_comptes"
```

Les deux tests sont rouges avec le même message :

```text
Failed asserting that two strings are equal.
-'http://localhost:8000/dashboard'
+'http://localhost:8000/home'
```

La ligne `-` est ce que le test attendait, la ligne `+` ce que l'application a fait : la connexion a réussi, mais Fortify a redirigé vers /home. Dans le navigateur, le même défaut se voit autrement : chaque connexion aboutit à une erreur 404.

**Faire.** Modifiez config/fortify.php

```php
'home' => '/dashboard',
```

**Relancer** la même commande. Le test des échecs est vert. Celui de la connexion valide reste rouge, mais son message a changé : `Expected response status code [200] but received 404.` La connexion redirige maintenant vers la bonne adresse, et le test demande ensuite cette page, qui n'existe pas encore. Elle sera créée plus bas, dans cette étape.

## **Création de la vue de connexion**

**Lancer (avant d'agir)**

```bash
php artisan test --filter='test_la_matrice_d_acces_est_respectee.*visiteur sur /login'
```

Ce cas de la matrice d'accès demande la page /login à un visiteur. Il est rouge : `Expected response status code [200] but received 500`. Sous ce message, la cause : `Target [Laravel\Fortify\Contracts\LoginViewResponse] is not instantiable`. Fortify ne fournit pas de page : la vue à afficher se déclare dans la méthode boot() de FortifyServiceProvider.

**Faire : déclarer les vues.**

Dans app/Providers/FortifyServiceProvider.php, ajoutez ces deux lignes à la fin de la méthode boot(). Ne supprimez rien de ce qui s'y trouve.

```php
        Fortify::loginView(fn () => view('auth.login'));
        Fortify::registerView(fn () => view('auth.register'));
```

**Relancer** la même commande. Le test est toujours rouge, mais la cause a changé : `View [auth.login] not found`. Fortify sait maintenant quelle vue afficher ; le fichier n'existe pas.

> [!WARNING]
> **Ce que boot() contient déjà, et pourquoi il ne faut pas l'écraser.**
>
> | Ligne de boot() | Si vous la supprimez |
> | --- | --- |
> | Fortify::createUsersUsing(CreateNewUser::class) | L'inscription plante : Fortify ne sait plus quelle classe crée les comptes |
> | RateLimiter::for('login', ...) | Toute connexion renvoie une 500 « Rate limiter \[login\] is not defined. » |
> | RateLimiter::for('two-factor', ...) | Les routes de double authentification plantent, si cette fonctionnalité est active |
>
> Le **limiteur** défini par RateLimiter::for('login', ...) est la règle qui limite les tentatives de connexion : au-delà de cinq par minute pour un même couple « e-mail + adresse IP », Fortify répond 429 (« Too Many Requests »).
>
> Les autres lignes de boot() (updateUserProfileInformationUsing, updateUserPasswordsUsing, resetUserPasswordsUsing, redirectUserForTwoFactorAuthenticationUsing et le limiteur passkeys) servent aux fonctionnalités désactivées à cette étape. Elles ne gênent pas : laissez-les en place et ne supprimez rien.
>
> Vous le vérifierez vous-même à la fin de l'étape (exercice « supprimer le contenu de boot() »).

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

**Relancer** la commande du cas « visiteur sur /login » : il est vert.

**Ce qui compte dans ce formulaire.**

| Élément | Rôle |
| --- | --- |
| **@csrf** | Ajoute un jeton de protection contre la falsification de requêtes (voir le mémo ci-dessous) |
| **old('email')** | Réaffiche l'e-mail saisi après une erreur. On ne réaffiche jamais un mot de passe. |
| **$errors** | Contient les messages d'erreur renvoyés par Fortify |
| **name="email", name="password"** | Les noms que Fortify attend. Un autre nom, et la connexion échoue. |

> [!NOTE]
> **La protection CSRF de Laravel.**
>
> Laravel 13 vérifie qu'un POST vient bien de votre site en deux temps :
>
> - **Origine** : si l'en-tête Sec-Fetch-Site vaut same-origin, la requête est acceptée sans vérification du jeton. Cet en-tête est ajouté par le navigateur, pas par Laravel : les navigateurs ne l'envoient que vers des adresses jugées sûres (HTTPS, mais aussi localhost et 127.0.0.1, même en HTTP). Un outil comme curl ne l'envoie pas.
> - **Jeton** : si l'en-tête est absent (curl, ancien navigateur, adresse HTTP non sûre) ou ne vaut pas same-origin, Laravel compare le jeton \_token à celui de la session.
>
> Si les deux échouent → 419 page expired ou 403 en mode originOnly.
>
> Conseil : gardez **@csrf** dans vos formulaires: c'est gratuit, simple et couvre les cas où Sec-Fetch-Site serait absent.
>
> Les tests, eux, ne vérifient pas le jeton CSRF : Laravel le désactive pendant les tests. Seules les preuves faites dans le navigateur et avec curl (plus bas) le montrent.

## **Création du tableau de bord minimal et de la déconnexion**

Après une connexion réussie, Fortify redirige vers la page de la clé home (/dashboard). Cette page doit exister, et elle doit offrir un moyen de se déconnecter : sans lui, vous resteriez connecté et ne pourriez plus atteindre le formulaire de connexion (une personne déjà connectée qui demande /login est redirigée ailleurs). Vous créez ici une version minimale.

**Lancer (avant d'agir)**

```bash
php artisan test --filter="test_une_connexion_valide_ouvre_une_session|test_un_visiteur_est_redirige_vers_la_connexion"
```

Les deux tests sont rouges avec `Expected response status code … but received 404` : la route /dashboard n'existe pas.

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

**Relancer** la même commande, avant de créer la vue. Le test du visiteur est vert : le middleware auth renvoie le visiteur vers /login, la vue n'est pas nécessaire pour cela. Celui de la connexion reste rouge, mais le message est maintenant `received 500`, avec la cause en dessous : `View [dashboard] not found`. La route et le contrôleur existent, il manque la vue. Le test `test_la_deconnexion_detruit_la_session` est lui aussi passé au vert avec cette route.

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

**Relancer** la même commande : les deux tests sont verts.

La route POST /logout est fournie par Fortify : vous n'avez rien à écrire côté serveur. Après la déconnexion, Fortify redirige vers /.

> [!NOTE]
> **Pourquoi la déconnexion est un POST ?**
>
> Une action qui modifie l’état ne doit pas être déclenchable par une simple URL. Avec un GET, n’importe quel site pourrait déconnecter vos utilisateurs, avec un lien vers https://votresite/logout ou en redirigeant vers cette adresse : le navigateur suit le lien en envoyant le cookie de session. Un POST avec la protection CSRF de Laravel refusera la requête venue d’un autre site.

## **Création de la vue d'inscription**

**Lancer (avant d'agir)**

```bash
php artisan test --filter=test_l_inscription_cree_un_compte_connecte
```

Le test commence par demander la page /register. Il est rouge : `Expected response status code [200] but received 500`, avec la cause en dessous : `View [auth.register] not found`. Fortify connaît la vue (vous l'avez déclarée plus haut), mais le fichier n'existe pas.

**Faire : écrivez la vue d'inscription vous-même.** Créez le fichier resources/views/auth/register.blade.php sur le modèle de la connexion. Le formulaire envoie en POST vers route('register'), contient @csrf et affiche les erreurs.

| Libellé | Attribut name | Type |
| --- | --- | --- |
| Nom | name | text |
| E-mail | email | email |
| Mot de passe | password | password |
| Confirmation | password\_confirmation | password |

Le nom password\_confirmation n'est pas libre : la règle de validation confirmed cherche un champ nommé \<champ>\_confirmation.

**Relancer** la même commande. Si le message devient `Expected: <!DOCTYPE html> … To contain: password_confirmation`, le test a bien reçu votre page mais n'y a pas trouvé le champ de confirmation : le texte affiché est le code HTML reçu, cherchez-y ce qui manque. Quand le champ est bien nommé, le test est vert : il a aussi envoyé le formulaire et vérifié que le compte est créé, la personne connectée et le mot de passe haché.

L'inscription est traitée par l'action app/Actions/Fortify/CreateNewUser.php, générée par fortify:install : elle valide les champs, puis crée le compte avec un mot de passe **haché**. Ouvrez-la et lisez-la.

> [!NOTE]
> **Mot de passe haché.** On ne stocke jamais un mot de passe tel quel : on stocke son **hash**, une empreinte qu'on ne peut pas inverser. L'étape 3 le montre dans la base.

## Bilan de la boucle

**Lancer**

```bash
php artisan test --filter=AuthenticationTest
```

Vous devez obtenir **17 tests verts et 3 rouges**. Les trois rouges sont les deux cas « /accueil » de la matrice d'accès et `test_l_accueil_s_adapte_au_profil` : la page /accueil sera créée à l'étape 4. Copiez la ligne de résultat dans PREUVES.md.

Souvenez-vous du premier lancement de l'étape : 7 verts, 13 rouges. Sur les 10 tests qui ont changé d'état depuis, chacun correspond à une action précise de cette étape : les features, la clé home, les vues, le tableau de bord.

**Exercice — supprimer le contenu de boot().** Le tableau d'avertissement plus haut décrit des symptômes. Vérifiez-les.

1. Mettez en commentaire (Ctrl+/) toutes les lignes de la méthode boot() de FortifyServiceProvider, sauf les deux lignes de déclaration des vues.
2. **Prédire** : combien de tests de plus deviennent rouges ? Puis lancez le contrat.
3. Il y a 11 rouges : les 3 de /accueil, et 8 nouveaux. Repérez leurs messages et comparez-les avec le tableau :
   - `Target [Laravel\Fortify\Contracts\CreatesNewUsers] is not instantiable` : 2 tests, ceux qui s'inscrivent ;
   - `Rate limiter [login] is not defined.` : 4 tests, ceux qui envoient une connexion et contrôlent la réponse ;
   - pour les 2 derniers (`test_la_connexion_enregistre_l_utilisateur_dans_la_session` et `test_la_deconnexion_detruit_la_session`), le message est celui du test lui-même (« La session ne contient pas l'utilisateur connecté. »). Il dit ce qui n'est pas arrivé, pas pourquoi : la cause est la même, la connexion plante. Un message de test ne nomme pas toujours la cause ; l'exception n'est affichée que lorsque le test contrôle un code HTTP.
4. Décommentez les lignes et relancez : 17 verts, 3 rouges.

Notez dans PREUVES.md les trois sortes de messages et le nombre de tests concernés par chacune.

## Preuves dans le navigateur et avec curl

Les tests ne voient ni le navigateur, ni le jeton CSRF, ni les cookies : ces points se prouvent à la main.

Lancez le serveur de développement dans un terminal dédié et laissez-le tourner jusqu'à la fin de l'étape (arrêt avec Ctrl+C). Vous le relancerez de la même façon aux étapes 3 et 4, qui utilisent le navigateur :

```bash
php artisan serve
```

Le TP utilise l'adresse http://127.0.0.1:8000, affichée par la commande.

1. Inscrivez un nouveau compte dans le navigateur, sur http://127.0.0.1:8000/register (mot de passe d'au moins 8 caractères). Vous arrivez sur /dashboard, qui affiche « Bonjour » suivi de votre nom. Notez l'URL obtenue. Cliquez sur « Se déconnecter » et notez l'URL obtenue. Les messages d'erreur de Laravel (mot de passe trop court, confirmation différente…) s'affichent en anglais : c'est normal, la langue de l'application est l'anglais par défaut.
2. Retirez @csrf de la vue de connexion (la directive qui ajoute au formulaire le champ caché \_token) et connectez-vous avec alice@exemple.test (mot de passe password) dans le navigateur, sur http://127.0.0.1:8000 (la page d'accueil de Laravel propose un lien « Log in »). Notez si la connexion fonctionne et, d'après le mémo sur la protection CSRF, par quel mécanisme. Remettez @csrf, puis déconnectez-vous.
3. Envoyez la même requête sans navigateur, avec curl, depuis un second terminal (le serveur lancé plus haut doit tourner) : curl -i -X POST http://127.0.0.1:8000/login -d "email=alice@exemple.test" -d "password=password". Sous Windows PowerShell, tapez curl.exe. Notez le code HTTP de la première ligne. Vous lirez « HTTP/1.1 419 unknown status » : « unknown status » est le libellé du serveur de développement PHP, le code est bien 419.
4. Tentez six connexions avec un mauvais mot de passe en moins d'une minute, avec le compte bob@exemple.test, sur lequel vous ne vous êtes pas encore connecté. Notez ce qui s'affiche à la sixième. Une connexion réussie compte aussi dans la limite : sur un compte où vous venez de vous connecter (alice@exemple.test à la preuve 2), le blocage arriverait dès la cinquième tentative avec un mauvais mot de passe.

> [!NOTE]
> **curl.** curl est un outil en ligne de commande qui envoie des requêtes HTTP sans navigateur. L'option -i affiche les en-têtes de la réponse, -X choisit la méthode (ici POST) et -d envoie des champs de formulaire.

**Question 1.** Le limiteur de boot() compte les tentatives par couple « e-mail + adresse IP ». Quel problème poserait un comptage par adresse IP seule dans un lycée où tous les postes sortent par la même IP ? Quelle attaque ce couple ne bloque-t-il pas ?

Suite : l'étape 3 regarde ce qui s'est passé dans la base et dans les cookies pendant ces connexions.
