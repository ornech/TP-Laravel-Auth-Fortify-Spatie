# Étape 5 : Déclarer les middlewares de Spatie

À la fin de cette étape, les routes peuvent utiliser permission:…, role:… et role\_or\_permission:….

> [!NOTE]
> **Mémo — Où se déclarent les middlewares depuis Laravel 11.** Le fichier app/Http/Kernel.php n'existe plus. Les alias se déclarent dans bootstrap/app.php, dans withMiddleware(). Un alias est un nom court (permission) qui pointe vers une classe.

**Faire — vérifier les noms de classes à la source**, avant de les écrire :

```bash
ls vendor/spatie/laravel-permission/src/Middleware
```

Sous Windows : dir vendor\\spatie\\laravel-permission\\src\\Middleware.

**Faire** — dans bootstrap/app.php, ajoutez les imports en haut du fichier :

```php
use Spatie\Permission\Middleware\PermissionMiddleware;
use Spatie\Permission\Middleware\RoleMiddleware;
use Spatie\Permission\Middleware\RoleOrPermissionMiddleware;
```

Puis ajoutez cet appel **à l'intérieur** de la fonction déjà passée à withMiddleware() :

```php
$middleware->alias([
    'role' => RoleMiddleware::class,
    'permission' => PermissionMiddleware::class,
    'role_or_permission' => RoleOrPermissionMiddleware::class,
]);
```

> [!WARNING]
> **Mémo — Une faute de frappe qui ne se voit pas.** Écrire Role\_or\_PermissionMiddleware::class ne provoque aucune erreur au démarrage : ::class produit seulement une chaîne de caractères, sans vérifier que la classe existe. Laravel ne cherche la classe qu'au moment où une route utilise l'alias. L'application plante alors avec « Target class \[...\] does not exist. », parfois des semaines plus tard. D'où la vérification dans vendor, plutôt que la confiance dans un exemple trouvé en ligne.

**Preuve** — la sortie de la commande ls (ou dir) ci-dessus.

**Question 4.** Si vous n'aviez pas regardé dans vendor, comment auriez-vous découvert une faute dans le nom d'une classe de middleware ? Quel type de test l'aurait révélée ?
