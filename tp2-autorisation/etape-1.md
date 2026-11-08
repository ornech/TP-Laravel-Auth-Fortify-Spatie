# Étape 1 : Installer Spatie et préparer le modèle User

Ce TP continue le projet tp-auth du [TP 1](../tp1-authentification/README.md) : placez-vous dans son dossier. Avant de commencer, les 20 tests du TP 1 doivent être verts (php artisan test --filter=AuthenticationTest).

## Installer le contrat de tests

Comme au TP 1, vous commencez par les tests. Créez tests/Feature/AuthorizationTest.php et copiez-y, sans rien changer, le fichier donné dans le [Contrat de tests](contrat-de-tests.md).

**Preuve**

```bash
php artisan test --filter=AuthorizationTest
```

Les 14 tests échouent, avec le message « Target class [`Database\Seeders\RoleSeeder`] does not exist. » : les seeders et Spatie n'existent pas encore. Les 20 tests du TP 1 doivent, eux, rester verts tout au long du TP 2. Une seule adaptation de leur préparation sera nécessaire, à l'étape 3, et elle y est expliquée.

## Installer Spatie

Le package spatie/laravel-permission crée cinq tables en base via une migration unique (2 tables de définition + 3 tables de liaison).

| Table | Rôle |
| --- | --- |
| permissions | Catalogue des permissions (ex. edit posts, delete users). Clé unique : name + guard\_name. |
| roles | Définition des rôles (ex. admin, editor). Chaque rôle regroupe un ensemble de permissions. |
| role\_has\_permissions | Pivot N-to-N entre rôles et permissions : Un rôle contient quel droit ? |
| model\_has\_roles | Pivot polymorphe : quel modèle (User, ApiClient…) a quel rôle. Colonnes : role\_id, model\_type, model\_id. |
| model\_has\_permissions | Pivot polymorphe : permissions attribuées directement à un modèle, sans passer par un rôle (cas rare). |

**Pourquoi cette architecture ?**

Les permissions ne sont pas stockées sur le modèle User, afin de permettre de réutiliser le même système pour n'importe quel modèle Eloquent (utilisateurs, API clients, service accounts…).

Le check ($user->can('edit posts')) vérifie à la fois les permissions directes (model\_has\_permissions) et celles héritées via les rôles (model\_has\_roles → role\_has\_permissions).

Le tout est mis en cache : Spatie charge les permissions en mémoire à la première vérification et invalide le cache à chaque création/modification de rôle ou permission.

**En résumé (le flux)**

```text
User ──(model_has_roles)──► Role ──(role_has_permissions)──► Permission
  │
  └──(model_has_permissions)──► Permission (direct, rare)
```

L'utilisateur hérite de toutes les permissions de ses rôles, plus celles qu'on lui a accordées directement. C'est le pattern RBAC classique, implémenté en N-to-N polymorphe pour rester découplé du modèle utilisateur.

**Faire**

```bash
composer require spatie/laravel-permission
php artisan vendor:publish --provider="Spatie\Permission\PermissionServiceProvider"
php artisan config:clear
php artisan migrate
```

Dans app/Models/User.php, ajoutez **l'import** et le **trait** HasRoles.

![](images/etape1-user-hasroles.png)

Le trait HasRoles ajoute au modèle les méthodes de Spatie : assignRole(), hasRole(), syncRoles()… La méthode can(), déjà présente, se met à tenir compte des permissions Spatie (voir le mémo).

> [!NOTE]
> **Mémo:** Le trait ***HasRoles***
>
> En PHP, une classe n’hérite que d’**une seule** classe parente. *User* hérite déjà de *Authenticatable* : on ne peut pas lui ajouter un second *extends*.
>
> Le **trait** contourne cette limite. C’est un bloc de méthodes que PHP recopie dans la classe qui l’utilise. En écrivant *use HasRoles;* dans *User*, le modèle reçoit *roles()*, *assignRole()*, *hasRole()*, *syncRoles()*, *givePermissionTo()*… sans qu’on réécrive une ligne.
>
> *can()*, lui, existe déjà dans *User* : il vient du trait *Authorizable*, inclus dans *Authenticatable*. Spatie se branche sur ce système d’autorisation de Laravel, en s’appuyant sur les méthodes de *HasRoles*. Sans le trait, *can()* répond *false* pour les permissions Spatie, **sans aucune erreur**.

> [!WARNING]
> Attention aux deux *use* : celui en haut du fichier **importe un nom** (permet d’écrire ***HasRoles*** au lieu de ***\\Spatie\\Permission\\Traits\\HasRoles***), celui dans la classe **inclut le trait** **à la classe User**.

**Test**

```bash
php artisan db:table model_has_roles
```

Copiez la liste des colonnes dans PREUVES.md.
