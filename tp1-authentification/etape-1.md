# Étape 1 : Créer le projet, le contrat de tests et les comptes de démonstration

À la fin de cette étape, vous avez un projet Laravel 13 neuf, un contrat de tests qui décrit ce que l'application devra faire, et deux comptes de démonstration pour vous connecter.

## Créer le projet

**Faire**

```bash
# Projet neuf, dernière version de Laravel (13.x)
composer create-project laravel/laravel tp-auth
cd tp-auth
php artisan --version
```

Créez aussi à la racine du projet un fichier vide **PREUVES.md** : vous y copierez vos preuves tout au long du TP (voir le README).

## Installer le contrat de tests

Vous commencez par les tests : ils décrivent ce que l'application devra faire à la fin. Au départ, ils échouent tous. Votre travail consiste à les faire passer un par un, sans jamais les modifier. Créez tests/Feature/AuthenticationTest.php et copiez-y, sans rien changer, le fichier donné dans le [Contrat de tests](contrat-de-tests.md). Ces tests utilisent une base SQLite en mémoire, déjà configurée dans phpunit.xml : ils ne touchent pas à votre base de développement.

**Preuve**

```bash
php artisan test --filter=AuthenticationTest
```

Les 20 tests échouent : les routes, les pages et le seeder qu'ils utilisent n'existent pas encore.

> [!NOTE]
> Lancez les commandes de test dans un terminal ordinaire. Si vous les lancez depuis un assistant IA (Claude Code, Cursor…), la sortie peut s'afficher en JSON au lieu du compte rendu habituel : c'est le comportement du package laravel/pao, inclus dans le squelette Laravel 13. Voir le [dépannage](depannage.md).

## Créer les comptes de démonstration

Pour vous connecter dans le navigateur, il faut des comptes qui existent déjà. Un seeder les crée.

**Faire** — php artisan make:seeder DemoUserSeeder, puis complétez le fichier :

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
            ['email' => 'alice@exemple.test'],
            ['name' => 'Alice Démo', 'password' => Hash::make('password')]
        );

        User::firstOrCreate(
            ['email' => 'bob@exemple.test'],
            ['name' => 'Bob Démo', 'password' => Hash::make('password')]
        );
    }
}
```

`firstOrCreate` crée le compte s'il manque et ne touche pas à un compte existant : le seeder peut être relancé sans créer de doublon.

**Faire.** Dans database/seeders/DatabaseSeeder.php, **remplacez le contenu du fichier** par celui-ci (exception à la règle d'or, car le fichier généré n'est qu'un exemple : le compte `test@example.com` qu'il créait n'est pas un des comptes du TP) :

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
            DemoUserSeeder::class,
        ]);
    }
}
```

**Preuve**

```bash
php artisan migrate:fresh --seed
php artisan db:seed
php artisan tinker --execute="dump(DB::table('users')->pluck('email'));"
```

migrate:fresh --seed supprime toutes les tables, les recrée, puis lance les seeders. Le second lancement (db:seed) ne doit ni échouer ni créer de doublon : vous devez voir exactement deux adresses, alice@exemple.test et bob@exemple.test. Copiez la dernière sortie dans PREUVES.md.

**Test qui doit passer :**

```bash
php artisan test --filter=test_les_comptes_de_demonstration_ne_sont_pas_crees_en_production
```

Ce test fait croire à l'application qu'elle tourne en production, lance DemoUserSeeder, et vérifie qu'aucun compte n'a été créé.
