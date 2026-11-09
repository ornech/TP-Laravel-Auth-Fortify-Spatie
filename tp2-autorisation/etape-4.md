# Étape 4 : Déclarer les middlewares de Spatie

À la fin de cette étape, les routes peuvent utiliser permission:…, role:… et role\_or\_permission:….

> [!NOTE]
> **Où se déclarent les middlewares depuis Laravel 11.** Le fichier app/Http/Kernel.php n'existe plus. Les alias se déclarent dans bootstrap/app.php, dans withMiddleware(). Un alias est un nom court (permission) qui pointe vers une classe.

**Faire — vérifier les noms de classes à la source**, avant de les écrire. `ls` liste le contenu d'un dossier. Le dossier ci-dessous contient les classes de middleware de Spatie : le nom de chaque fichier est le nom de la classe qu'il contient.

```bash
ls vendor/spatie/laravel-permission/src/Middleware
```

Sous Windows : dir vendor\\spatie\\laravel-permission\\src\\Middleware.

**Vous devez voir** trois fichiers : `PermissionMiddleware.php`, `RoleMiddleware.php` et `RoleOrPermissionMiddleware.php`.

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
> **Une faute dans le nom de la classe n'est pas signalée au démarrage.** Écrire Role\_or\_PermissionMiddleware::class ne provoque aucune erreur : ::class produit seulement une chaîne de caractères, sans vérifier que la classe existe. Laravel ne cherche la classe qu'au moment où une route utilise l'alias. L'application plante alors avec « Target class \[...\] does not exist. », éventuellement longtemps après l'écriture de la faute. C'est pourquoi les noms sont vérifiés dans vendor, et non recopiés d'un exemple.

**Vérifier**

```bash
php artisan tinker --execute="dump(array_map('class_exists', app(Illuminate\Contracts\Http\Kernel::class)->getMiddlewareAliases()));"
```

La commande liste tous les alias de middleware de l'application, avec `true` quand la classe existe et `false` sinon. Vous retrouvez des alias de Laravel (auth, guest, throttle…) et les trois vôtres : role, permission et role\_or\_permission, tous à `true`.

**Preuve** — la sortie de la commande ls (ou dir) et celle de la commande tinker.

**Exercice — introduire une faute dans le nom d'une classe.**

1. **Prédire** : une faute dans le nom de la classe de l'alias role\_or\_permission fait-elle échouer des tests ? Aucune route du projet n'utilise encore cet alias.
2. Dans bootstrap/app.php, remplacez RoleOrPermissionMiddleware par Role\_or\_PermissionMiddleware, dans l'import et dans l'alias.
3. Relancez la commande tinker : la ligne role\_or\_permission affiche `false`. Lancez ensuite `php artisan test --filter=AuthorizationTest` : le résultat est identique à celui d'avant la faute (3 tests verts, 11 rouges, ceux des étapes 2 et 3 d'un côté, ceux de l'étape 5 de l'autre), parce qu'aucun test ne passe par cet alias.
4. Remettez le nom d'origine et relancez la commande tinker : trois `true`.

**Question 3.** La faute de l'exercice n'a fait échouer aucun test. Quel test l'aurait détectée ? Et si la faute avait porté sur l'alias permission, que se passerait-il à l'étape 5 ?
