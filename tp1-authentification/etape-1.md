# Étape 1 : Créer le projet, le contrat de tests et les comptes de démonstration

À la fin de cette étape, vous avez un projet Laravel 13 neuf, un contrat de tests qui décrit ce que l'application devra faire, et deux comptes de démonstration pour vous connecter.

## Créer le projet

Trois commandes préparent le projet. `composer create-project` télécharge le squelette officiel de Laravel dans un nouveau dossier tp-auth et installe ses dépendances dans vendor/. `cd tp-auth` se place dans ce dossier : toutes les commandes suivantes se lancent depuis lui. `php artisan --version` affiche la version de Laravel installée.

**Faire**

```bash
# Projet neuf, dernière version de Laravel (13.x)
composer create-project laravel/laravel tp-auth
cd tp-auth
php artisan --version
```

**Vous devez voir :** l'installation de composer, qui se termine par `Application key set successfully.` puis la liste des migrations de base (`0001_01_01_000000_create_users_table … DONE`, etc.), et pour la dernière commande `Laravel Framework 13.x.y` (la version de référence du TP est 13.40.0).

Créez aussi à la racine du projet un fichier vide **PREUVES.md** : vous y copierez vos preuves tout au long du TP (voir le README).

## Installer le contrat de tests

Vous commencez par les tests : ils décrivent ce que l'application devra faire à la fin. Au départ, ils échouent tous. Votre travail consiste à les faire passer, sans jamais les modifier, en suivant partout dans ce TP la même boucle. Créez tests/Feature/AuthenticationTest.php et copiez-y, sans rien changer, le fichier donné dans le [Contrat de tests](contrat-de-tests.md). Ces tests utilisent une base SQLite en mémoire, déjà configurée dans phpunit.xml : ils ne touchent pas à votre base de développement.

> [!NOTE]
> **PHPUnit.** PHPUnit est l'outil de test de PHP : c'est lui qui exécute les tests, lancé par la commande php artisan test.

> [!NOTE]
> **La boucle de test.** À chaque action importante du TP, vous répétez cinq gestes :
>
> 1. **Prédire** : le test va-t-il être rouge ou vert, et pourquoi ?
> 2. **Lancer** le test concerné, avant d'agir.
> 3. **Lire** le message d'échec : il nomme presque toujours ce qui manque.
> 4. **Agir** : faire la modification demandée.
> 5. **Relancer** : le message change, puis le test passe au vert.
>
> Un test déjà vert avant votre action ne prouve pas votre travail : il décrit un comportement qui existait déjà.

> [!NOTE]
> Lancez les commandes de test dans un terminal ordinaire. Si vous les lancez depuis un assistant IA (Claude Code, Cursor…), la sortie peut s'afficher en JSON au lieu du compte rendu habituel : c'est le comportement du package laravel/pao, inclus dans le squelette Laravel 13. Voir le [dépannage](depannage.md).

## Lire un échec

**Lancer**

```bash
php artisan test --filter=AuthenticationTest
```

Les 20 tests échouent : les routes, les pages et les comptes de démonstration qu'ils utilisent n'existent pas encore. Lisez les échecs un par un : lancez le premier test seul.

```bash
php artisan test --filter=test_les_comptes_de_demonstration_ne_sont_pas_crees_en_production
```

Un échec de test se lit en trois morceaux : le **nom** du test (une phrase qui dit le comportement attendu), le **message** (ce qui était attendu et ce qui est arrivé) et la **ligne** du test qui a échoué, avec son contexte. Ici, le message est `Class "Database\Seeders\DemoUserSeeder" not found` : le test utilise une classe qui n'existe pas encore.

Les autres messages que vous allez rencontrer dans ce TP se lisent de la même façon :

| Message | Ce qu'il veut dire |
| --- | --- |
| `Expected response status code [200] but received 404` | Le test a demandé une page et l'application répond « introuvable » : la route n'existe pas encore |
| `Expected response status code [200] but received 500` | La route existe, mais elle plante : un message `The following exception occurred…` en dessous nomme la cause |
| `Session is missing expected key [errors]` | Le test attendait un refus de saisie (une erreur sur un champ) : aucune route n'a traité le formulaire |
| `Failed asserting that true is false` précédé d'une phrase | Une chose existe alors qu'elle devrait être absente ; la phrase dit laquelle |

**Preuve**

Dans PREUVES.md, copiez le message d'échec du test du seeder et, en une phrase, ce qu'il demande de faire. Relevez aussi le nombre de tests rouges de la commande complète.

## Créer les comptes de démonstration

Pour vous connecter dans le navigateur, il faut des comptes qui existent déjà. Un seeder les crée.

> [!NOTE]
> **Seeder.** Un **seeder** est une classe qui remplit la base de données avec des données de départ. On le lance avec php artisan db:seed.

**Faire** — `php artisan make:seeder DemoUserSeeder` crée le fichier database/seeders/DemoUserSeeder.php, qui contient une classe vide. **Vous devez voir :** `INFO Seeder [database/seeders/DemoUserSeeder.php] created successfully.` Complétez ensuite le fichier :

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

> [!NOTE]
> **tinker.** tinker est la console interactive de Laravel : elle exécute du code PHP dans le contexte de votre application. Avec l'option --execute, elle exécute l'instruction donnée puis rend la main ; ici, elle liste les adresses e-mail de la table users.

**Relancer le test du seeder**

```bash
php artisan test --filter=test_les_comptes_de_demonstration_ne_sont_pas_crees_en_production
```

Le message `Class "Database\Seeders\DemoUserSeeder" not found` a disparu et le test est vert : c'est le premier passage du rouge au vert du TP. Ce test fait croire à l'application qu'elle tourne en production, lance DemoUserSeeder, et vérifie qu'aucun compte n'a été créé.

**Exercice — vérifier que le test peut échouer.** Un test qui ne peut jamais échouer ne prouve rien. Pour vérifier celui-ci, supprimez la condition qu'il protège.

1. Dans DemoUserSeeder, mettez en commentaire le bloc `if (! app()->environment(['local', 'testing'])) { … }` (de la ligne du `if` jusqu'à son accolade fermante). Ce bloc interrompt le seeder quand l'environnement n'est ni local ni testing ; sans lui, les comptes sont créés dans tous les environnements.
2. Relancez le test. Le message est `DemoUserSeeder a créé des comptes en production.`, suivi de `Failed asserting that 2 is identical to 1`. Le test partait avec 1 compte (alice, créée avant chaque test) : le seeder en a ajouté un, donc 2.
3. Remettez le bloc, relancez : le test redevient vert.

**Preuve.** Dans PREUVES.md, copiez la ligne de résultat du test (`Tests: … passed`) avant l'exercice, pendant (rouge, avec son message) et après.
