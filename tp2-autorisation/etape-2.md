# Étape 2 : Créer les rôles, la permission et les comptes de démonstration

À la fin de cette étape, la base contient les rôles utilisateur et administrateur, la permission gerer-utilisateurs et deux comptes de démonstration, et les seeders peuvent être relancés sans erreur.

RoleSeeder crée les rôles et la permission : ils sont nécessaires partout, y compris en production. DemoUserSeeder, créé au TP 1, crée désormais deux comptes de démonstration **avec leur rôle**. Ces comptes ne doivent pas exister en production.

**Lancer (avant d'agir)**

```bash
php artisan test --filter=test_les_seeders_sont_rejouables
```

Le test est rouge avec `Target class [Database\Seeders\RoleSeeder] does not exist.` : le seeder n'existe pas.

## **Seeder RoleSeeder**

**Faire** — php artisan make:seeder RoleSeeder, puis complétez le fichier :

```php
<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Spatie\Permission\Models\Permission;
use Spatie\Permission\Models\Role;
use Spatie\Permission\PermissionRegistrar;

class RoleSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Spatie garde rôles et permissions en cache : on repart d'un cache vide
        app(PermissionRegistrar::class)->forgetCachedPermissions();

        // findOrCreate : crée si absent, récupère sinon
        $gererUtilisateurs = Permission::findOrCreate('gerer-utilisateurs', 'web');

        // Pas de rôle « visiteur » : un visiteur n'est pas connecté
        Role::findOrCreate('utilisateur', 'web');
        Role::findOrCreate('administrateur', 'web')->syncPermissions([$gererUtilisateurs]);
    }
}
```

**Relancer** la même commande. Le test est toujours rouge, avec un autre message : `No query results for model [App\Models\User].` Le contrat lance RoleSeeder puis DemoUserSeeder, puis cherche le compte admin@exemple.test. DemoUserSeeder est encore celui du TP 1 : il crée alice et bob, pas ce compte.

## **Seeder DemoUserSeeder**

**Faire** — le fichier database/seeders/DemoUserSeeder.php existe depuis le TP 1. **Remplacez son contenu** par celui-ci (exception à la règle d'or) : il crée désormais deux comptes, chacun avec son rôle.

```php
<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DemoUserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Des comptes au mot de passe connu n'ont rien à faire en production
        if (! app()->environment(['local', 'testing'])) {
            $this->command?->warn('DemoUserSeeder ignoré hors local/testing.');

            return;
        }

        User::firstOrCreate(
            ['email' => 'admin@exemple.test'],
            ['name' => 'Admin Démo', 'password' => Hash::make('password')]
        )->syncRoles(['administrateur']);

        User::firstOrCreate(
            ['email' => 'utilisateur@exemple.test'],
            ['name' => 'Utilisateur Démo', 'password' => Hash::make('password')]
        )->syncRoles(['utilisateur']);
    }
}
```

**Relancer** la même commande : le test est vert.

**Faire.** Dans database/seeders/DatabaseSeeder.php (modifié au TP 1), **remplacez le contenu du fichier** par celui-ci (exception à la règle d'or) : il lance maintenant RoleSeeder, puis DemoUserSeeder.

```php
<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        $this->call([
            RoleSeeder::class,
            DemoUserSeeder::class,
        ]);
    }
}
```

Les tests lancent les seeders directement : ce fichier n'a pas d'effet sur eux. Il sert aux commandes migrate:fresh --seed et db:seed.

L’ordre compte : DemoUserSeeder attribue des rôles que RoleSeeder doit avoir créés.

Les comptes alice et bob du TP 1 disparaissent au prochain migrate:fresh : ils ne servaient qu'à l'authentification. Les deux comptes de ce TP les remplacent.

> [!NOTE]
> **Un seeder doit pouvoir être rejouable.** On relance souvent un seeder, notamment après un migrate:fresh. Il doit donc décrire l’état final des données présentes dans une table, et non une simple suite d'ajouts. On dit qu'il est idempotent.
>
> Ici, findOrCreate et firstOrCreate créent ce qui manque sans toucher à ce qui existe déjà, et syncPermissions et syncRoles imposent la liste exacte des permissions et des rôles. Un compte de démonstration déjà présent garde donc son nom et son mot de passe d'origine.

**Preuve.**

```bash
php artisan migrate:fresh --seed
php artisan permission:show
php artisan db:seed
```

migrate:fresh --seed supprime toutes les tables, les recrée, puis lance DatabaseSeeder, donc RoleSeeder puis DemoUserSeeder. permission:show affiche la matrice rôles × permissions : la permission gerer-utilisateurs ne doit être cochée que pour administrateur. Le second lancement des seeders (db:seed) doit se terminer sans erreur. Copiez les sorties de permission:show et du second lancement dans PREUVES.md.

**Exercice — remplacer findOrCreate par create.** Vérifiez ce que garantit findOrCreate.

1. **Prédire** : un seeder qui crée un rôle avec `Role::create` réussit-il au premier lancement ? Au second ?
2. Dans RoleSeeder, remplacez la ligne `Role::findOrCreate('utilisateur', 'web');` par `Role::create(['name' => 'utilisateur', 'guard_name' => 'web']);`. findOrCreate renvoie le rôle s'il existe déjà. create essaie toujours de l'insérer, et Spatie refuse un second rôle de même nom (name et guard\_name sont uniques).
3. Lancez `php artisan test --filter=test_les_seeders_sont_rejouables`. Le test est rouge avec ``A role `utilisateur` already exists for guard `web`.`` : setUp() a lancé RoleSeeder une première fois, le test le relance.
4. Lancez `php artisan db:seed` : la même erreur apparaît, parce que la base contient déjà le rôle.
5. Remettez la ligne d'origine et relancez le test : il est vert.

**Preuve.** Copiez le message d'échec de l'étape 3.

> **Question 1.**
>
> 1. La table *users* contient-elle une colonne pour le rôle ?
> 2. Dans quelle table est enregistré le fait qu'un compte est administrateur ?

Indices :

```bash
php artisan db:table users
```

```bash
php artisan tinker --execute="dump(DB::table('model_has_roles')->get());"
```

```bash
php artisan tinker --execute="dump(DB::table('roles')->get());"
```

Copiez les trois sorties dans PREUVES.md. La troisième sert à traduire l'identifiant d'un rôle (role\_id) en son nom.
