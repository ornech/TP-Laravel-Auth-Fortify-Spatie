# Contrat de tests : TP 2

Le TP 2 est terminé quand les 14 tests de ce fichier passent, dont les 3 cases de la matrice d'accès (le tableau de la section « Livrables » du README), **et** que les 20 tests du TP 1 passent toujours, après l'adaptation décrite à l'étape 3 (34 tests au total avec php artisan test --filter="AuthenticationTest|AuthorizationTest"). Copiez-le à l'étape 1 dans tests/Feature/AuthorizationTest.php, sans le modifier.

Comme celui du TP 1, le fichier est commenté pour servir de modèle : lisez d'abord l'en-tête du [contrat du TP 1](../tp1-authentification/contrat-de-tests.md), qui présente les mécanismes de base. Celui-ci ajoute la préparation par seeders et les assertions propres aux rôles et aux permissions.

Ce que chaque test prouve

| Étape | Test | Ce qu'il prouve |
| --- | --- | --- |
| 2 | test\_les\_seeders\_sont\_rejouables | Relancer les seeders ne plante pas, ne duplique rien, et ne crée que deux rôles |
| 3 | test\_l\_inscription\_attribue\_le\_role\_utilisateur | Tout nouvel inscrit est utilisateur et arrive sur /dashboard |
| 3 | test\_un\_role\_injecte\_a\_l\_inscription\_est\_ignore | Un champ role ajouté au formulaire n'a aucun effet |
| 5 | test\_la\_matrice\_d\_acces\_est\_respectee (3 cas) | /admin/users : visiteur → 302, utilisateur → 403, administrateur → 200 |
| 5 | test\_un\_visiteur\_n\_atteint\_pas\_l\_administration | La redirection 302 du visiteur mène bien à /login |
| 5 | test\_la\_page\_d\_administration\_liste\_les\_utilisateurs | L'administrateur voit la liste des comptes |
| 5 | test\_l\_accueil\_s\_adapte\_au\_role | /accueil affiche un message différent pour l'utilisateur et pour l'administrateur |
| 5 | test\_le\_lien\_d\_administration\_suit\_la\_permission | Le lien n'apparaît que pour qui a la permission |
| 5 | test\_un\_autre\_role\_ayant\_la\_permission\_accede\_a\_l\_administration | La route vérifie la permission, pas le nom du rôle |
| 5 | test\_un\_autre\_role\_ayant\_la\_permission\_voit\_le\_lien\_d\_administration | Le lien suit la permission, pas le nom du rôle |
| 5 | test\_un\_compte\_sans\_role\_ne\_peut\_pas\_administrer | Un compte sans aucun rôle reçoit une 403 |
| 5 | test\_retirer\_le\_role\_administrateur\_retire\_l\_acces | Retirer le rôle retire l'accès à l'administration |

Pour lancer un seul test : php artisan test --filter=\<nom du test>. Pour tout le contrat : php artisan test --filter=AuthorizationTest.

```php
<?php

namespace Tests\Feature;

use App\Models\User;
use Database\Seeders\DemoUserSeeder;
use Database\Seeders\RoleSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use PHPUnit\Framework\Attributes\DataProvider;
use Spatie\Permission\Models\Role;
use Tests\TestCase;

/**
 * Contrat du TP 2 : ne modifiez pas ce fichier, faites-le passer.
 *
 * ============================================================================
 * COMMENT LIRE CE FICHIER (et vous en inspirer dans vos propres projets)
 * ============================================================================
 *
 * Même construction que le contrat du TP 1 : chaque test PRÉPARE, AGIT, puis
 * VÉRIFIE, et son nom est une phrase qui dit le comportement attendu.
 *
 * Ce qui s'ajoute ici :
 *
 *   - $this->seed([...])
 *       Lance des seeders pour remplir la base avant le test. Ici, les rôles,
 *       la permission et deux comptes : l'administrateur et l'utilisateur.
 *   - $compte->assignRole('...') / removeRole('...') / hasRole('...')
 *       Donner, retirer ou tester un rôle (méthodes fournies par Spatie).
 *   - $compte->can('permission')
 *       Teste une PERMISSION, quel que soit le rôle qui la porte.
 *   - Role::findOrCreate('nom', 'web')->givePermissionTo('permission')
 *       Crée un rôle, ou le retrouve s'il existe, et lui accorde une permission.
 *   - assertForbidden()
 *       Le code HTTP reçu est 403 : authentifié, mais non autorisé.
 *   - $compte->fresh()
 *       Recharge le compte depuis la base, pour ne pas réutiliser des données
 *       restées en mémoire.
 *
 * Un test vaut surtout par ce qu'il peut détecter. Plusieurs tests de ce
 * fichier existent pour qu'une erreur classique devienne visible : protéger
 * une page par le NOM d'un rôle au lieu de sa permission, ou oublier qu'un
 * compte peut n'avoir aucun rôle.
 */
class AuthorizationTest extends TestCase
{
    use RefreshDatabase;

    private User $admin;
    private User $utilisateur;

    /**
     * PRÉPARER (commun à tous les tests) : exécutée avant chaque test.
     */
    protected function setUp(): void
    {
        parent::setUp();

        // On remplit la base comme le ferait php artisan db:seed.
        $this->seed([RoleSeeder::class, DemoUserSeeder::class]);

        // On retrouve les deux comptes créés par DemoUserSeeder.
        $this->admin = User::where('email', 'admin@exemple.test')->firstOrFail();
        $this->utilisateur = User::where('email', 'utilisateur@exemple.test')->firstOrFail();
    }

    // ---------- Étape 2 : seeders ----------

    /**
     * Prouve : les seeders sont rejouables (on dit « idempotents »).
     */
    public function test_les_seeders_sont_rejouables(): void
    {
        // AGIR : un second passage ne doit ni planter ni dupliquer.
        $this->seed([RoleSeeder::class, DemoUserSeeder::class]);

        // VÉRIFIER : deux rôles seulement (« visiteur » n'est pas un rôle en base),
        // un seul compte admin, et les permissions sont celles attendues.
        $this->assertSame(2, Role::count());
        $this->assertSame(1, User::where('email', 'admin@exemple.test')->count());
        $this->assertTrue($this->admin->fresh()->can('gerer-utilisateurs'));
        $this->assertFalse($this->utilisateur->fresh()->can('gerer-utilisateurs'));
    }

    // ---------- Étape 3 : inscription ----------

    /**
     * Prouve : tout nouvel inscrit reçoit le rôle « utilisateur ».
     */
    public function test_l_inscription_attribue_le_role_utilisateur(): void
    {
        $this->post('/register', $this->inscription('nouveau@exemple.test'))
            ->assertRedirect('/dashboard');

        $this->assertAuthenticated();
        $nouveau = User::where('email', 'nouveau@exemple.test')->firstOrFail();
        $this->assertTrue($nouveau->hasRole('utilisateur'));
    }

    /**
     * Prouve : un rôle envoyé par le client est ignoré (attaque par champ caché).
     */
    public function test_un_role_injecte_a_l_inscription_est_ignore(): void
    {
        // AGIR : l'attaquant ajoute un champ « role » au formulaire. L'opérateur +
        // fusionne les deux tableaux : le champ « role » s'ajoute aux champs normaux.
        $this->post('/register', $this->inscription('attaquant@exemple.test') + ['role' => 'administrateur']);

        // VÉRIFIER : il n'est pas devenu administrateur, il est simple utilisateur.
        $attaquant = User::where('email', 'attaquant@exemple.test')->firstOrFail();
        $this->assertFalse($attaquant->hasRole('administrateur'), 'Le rôle envoyé par le client a été accepté.');
        $this->assertFalse($attaquant->can('gerer-utilisateurs'));
        $this->assertTrue($attaquant->hasRole('utilisateur'));
    }

    // ---------- Étape 5 : routes et vues ----------

    /**
     * La matrice d'accès de l'administration : une ligne par profil.
     * C'est le tableau « profil × route → résultat attendu » de la section
     * « Livrables » du README. (Un data provider : voir le contrat du TP 1.)
     */
    public static function matriceDAcces(): array
    {
        return [
            'visiteur sur /admin/users' => ['visiteur', '/admin/users', 302],
            'utilisateur sur /admin/users' => ['utilisateur', '/admin/users', 403],
            'administrateur sur /admin/users' => ['administrateur', '/admin/users', 200],
        ];
    }

    /**
     * Prouve : chaque case de la matrice. 302 = « connectez-vous » (authentification),
     * 403 = « vous n'avez pas le droit » (autorisation).
     */
    #[DataProvider('matriceDAcces')]
    public function test_la_matrice_d_acces_est_respectee(string $profil, string $url, int $statut): void
    {
        match ($profil) {
            'utilisateur' => $this->actingAs($this->utilisateur),
            'administrateur' => $this->actingAs($this->admin),
            'visiteur' => null, // personne n'est connecté
        };

        $this->get($url)->assertStatus($statut);
    }

    /**
     * Prouve : le visiteur est renvoyé vers la connexion, pas vers une erreur 403.
     * (Le middleware auth passe avant le middleware permission.)
     */
    public function test_un_visiteur_n_atteint_pas_l_administration(): void
    {
        $this->get('/admin/users')->assertRedirect('/login');
    }

    /**
     * Prouve : l'administrateur voit la liste des comptes.
     */
    public function test_la_page_d_administration_liste_les_utilisateurs(): void
    {
        $this->actingAs($this->admin)
            ->get('/admin/users')
            ->assertOk()
            ->assertSee('utilisateur@exemple.test');
    }

    /**
     * Prouve : l'accueil affiche un message propre à chaque rôle.
     */
    public function test_l_accueil_s_adapte_au_role(): void
    {
        // Utilisateur : il voit son message, pas celui de l'administrateur.
        $this->actingAs($this->utilisateur)->get('/accueil')
            ->assertSee('Espace utilisateur')
            ->assertDontSee('Espace administrateur');

        // Administrateur : l'inverse.
        $this->actingAs($this->admin)->get('/accueil')
            ->assertSee('Espace administrateur')
            ->assertDontSee('Espace utilisateur');
    }

    /**
     * Prouve : le lien d'administration n'apparaît que pour qui a la permission.
     * (Le masquer n'est qu'un confort : la protection est sur la route.)
     */
    public function test_le_lien_d_administration_suit_la_permission(): void
    {
        $this->actingAs($this->utilisateur)->get('/dashboard')
            ->assertOk()
            ->assertDontSee('Gestion des utilisateurs');

        $this->actingAs($this->admin)->get('/dashboard')
            ->assertOk()
            ->assertSee('Gestion des utilisateurs');
    }

    /**
     * Prouve : la route vérifie la PERMISSION, pas le nom du rôle.
     *
     * On crée un rôle « tuteur » inconnu du reste de l'application, et on lui
     * accorde la permission. Il doit accéder à l'administration sans qu'on ait
     * modifié la moindre route. Si la route était protégée par
     * role:administrateur, ce test échouerait.
     */
    public function test_un_autre_role_ayant_la_permission_accede_a_l_administration(): void
    {
        // PRÉPARER : un nouveau rôle qui porte la permission, et un compte qui a ce rôle.
        Role::findOrCreate('tuteur', 'web')->givePermissionTo('gerer-utilisateurs');
        $tuteur = User::factory()->create();
        $tuteur->assignRole('tuteur');

        // AGIR + VÉRIFIER : la page d'administration lui est ouverte.
        $this->actingAs($tuteur)->get('/admin/users')->assertOk();
    }

    /**
     * Prouve : le lien d'administration suit la permission, pas le nom du rôle.
     * Si la vue testait @role('administrateur') au lieu de @can, ce test échouerait.
     */
    public function test_un_autre_role_ayant_la_permission_voit_le_lien_d_administration(): void
    {
        Role::findOrCreate('tuteur', 'web')->givePermissionTo('gerer-utilisateurs');
        $tuteur = User::factory()->create();
        $tuteur->assignRole('tuteur');

        $this->actingAs($tuteur)->get('/dashboard')->assertSee('Gestion des utilisateurs');
    }

    /**
     * Prouve : un compte qui n'a aucun rôle ne peut pas administrer.
     *
     * Un compte peut très bien n'avoir aucun rôle (créé avant l'installation de
     * Spatie, par exemple) : il est authentifié, mais sans aucun droit.
     */
    public function test_un_compte_sans_role_ne_peut_pas_administrer(): void
    {
        // PRÉPARER : un compte fabriqué sans aucun rôle.
        $sansRole = User::factory()->create();

        // AGIR + VÉRIFIER : connecté, mais refusé (403).
        $this->actingAs($sansRole)->get('/admin/users')->assertForbidden();
    }

    /**
     * Prouve : les droits suivent le rôle. Retirer le rôle retire l'accès.
     */
    public function test_retirer_le_role_administrateur_retire_l_acces(): void
    {
        // PRÉPARER : un administrateur de plus, qui a accès à la page.
        $admin = User::factory()->create();
        $admin->assignRole('administrateur');
        $this->actingAs($admin)->get('/admin/users')->assertOk();

        // AGIR : on lui retire son rôle.
        $admin->removeRole('administrateur');

        // VÉRIFIER : fresh() recharge le compte depuis la base ; il est refusé.
        $this->actingAs($admin->fresh())->get('/admin/users')->assertForbidden();
    }

    /**
     * Fabrique les champs d'un formulaire d'inscription valide.
     * Une méthode privée évite de répéter le même tableau dans chaque test.
     */
    private function inscription(string $email): array
    {
        return [
            'name' => 'Nouvel Inscrit',
            'email' => $email,
            'password' => 'Secret123!',
            'password_confirmation' => 'Secret123!',
        ];
    }
}
```
