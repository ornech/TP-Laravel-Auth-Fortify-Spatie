# Contrat de tests

Le TP est terminé quand les 23 tests de ce fichier passent, dont les 12 cases de la matrice d'accès. Copiez-le à l'étape 0 dans tests/Feature/AuthRbacTest.php, sans le modifier.

Ce que chaque test prouve

| Étape | Test | Ce qu'il prouve |
| --- | --- | --- |
| 2 | test\_les\_seeders\_sont\_rejouables | Relancer les seeders ne plante pas, ne duplique rien, et ne crée que deux rôles |
| 3 | test\_seules\_les\_fonctionnalites\_utiles\_sont\_exposees | Fortify n'expose ni réinitialisation de mot de passe ni double authentification |
| 3 | test\_le\_mot\_de\_passe\_doit\_etre\_confirme | La règle confirmed est toujours appliquée |
| 3 | test\_la\_connexion\_est\_bloquee\_apres\_cinq\_echecs | La sixième tentative en une minute reçoit une 429 |
| 3 | test\_la\_deconnexion\_n\_accepte\_que\_post | GET /logout répond 405, POST /logout déconnecte |
| 4 | test\_l\_inscription\_attribue\_le\_role\_utilisateur | Tout nouvel inscrit est utilisateur et arrive sur /dashboard |
| 4 | test\_un\_role\_injecte\_a\_l\_inscription\_est\_ignore | Un champ role ajouté au formulaire n'a aucun effet |
| 6 | test\_la\_matrice\_d\_acces\_est\_respectee (12 cas) | Chaque case de la matrice d'accès : profil × route → code HTTP |
| 6 | test\_un\_visiteur\_est\_redirige\_vers\_la\_connexion | Les redirections 302 du visiteur mènent bien à /login |
| 6 | test\_la\_page\_d\_administration\_liste\_les\_utilisateurs | L'administrateur voit la liste des comptes |
| 6 | test\_l\_accueil\_s\_adapte\_au\_profil | /accueil affiche un contenu différent pour chacun des trois profils |
| 6 | test\_le\_lien\_d\_administration\_suit\_la\_permission | Le lien n'apparaît que pour qui a la permission |

Pour lancer un seul test : php artisan test --filter=\<nom du test>. Pour tout le contrat : php artisan test --filter=AuthRbacTest.

```php
<?php

namespace Tests\Feature;

use App\Models\User;
use Database\Seeders\DemoUserSeeder;
use Database\Seeders\RoleSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Route;
use PHPUnit\Framework\Attributes\DataProvider;
use Spatie\Permission\Models\Role;
use Tests\TestCase;

/**
 * Contrat du TP : ne modifiez pas ce fichier, faites-le passer.
 */
class AuthRbacTest extends TestCase
{
    use RefreshDatabase;

    private User $admin;
    private User $utilisateur;

    protected function setUp(): void
    {
        parent::setUp();

        $this->seed([RoleSeeder::class, DemoUserSeeder::class]);

        $this->admin = User::where('email', 'admin@exemple.test')->firstOrFail();
        $this->utilisateur = User::where('email', 'utilisateur@exemple.test')->firstOrFail();
    }

    // ---------- Étape 2 : seeders ----------

    public function test_les_seeders_sont_rejouables(): void
    {
        // Un second passage ne doit ni planter ni dupliquer
        $this->seed([RoleSeeder::class, DemoUserSeeder::class]);

        // Deux rôles seulement : « visiteur » n'est pas un rôle en base
        $this->assertSame(2, Role::count());
        $this->assertSame(1, User::where('email', 'admin@exemple.test')->count());
        $this->assertTrue($this->admin->fresh()->can('gerer-utilisateurs'));
        $this->assertFalse($this->utilisateur->fresh()->can('gerer-utilisateurs'));
    }

    // ---------- Étape 3 : Fortify ----------

    public function test_seules_les_fonctionnalites_utiles_sont_exposees(): void
    {
        $this->assertTrue(Route::has('login'));
        $this->assertTrue(Route::has('register'));
        $this->assertFalse(Route::has('password.request'), 'La réinitialisation de mot de passe doit être désactivée.');
        $this->assertFalse(Route::has('two-factor.login'), 'La double authentification doit être désactivée.');
    }

    public function test_le_mot_de_passe_doit_etre_confirme(): void
    {
        $this->post('/register', [
            'name' => 'Sans Confirmation',
            'email' => 'sans.confirmation@exemple.test',
            'password' => 'Secret123!',
        ])->assertSessionHasErrors('password');

        $this->assertGuest();
        $this->assertDatabaseMissing('users', ['email' => 'sans.confirmation@exemple.test']);
    }

    public function test_la_connexion_est_bloquee_apres_cinq_echecs(): void
    {
        $identifiants = ['email' => 'utilisateur@exemple.test', 'password' => 'mauvais-mot-de-passe'];

        for ($i = 1; $i <= 5; $i++) {
            $this->post('/login', $identifiants)->assertSessionHasErrors('email');
        }

        // Sixième tentative dans la même minute : bloquée avant toute vérification
        $this->post('/login', $identifiants)->assertStatus(429);
        $this->assertGuest();
    }

    // ---------- Étape 4 : inscription ----------

    public function test_l_inscription_attribue_le_role_utilisateur(): void
    {
        $this->post('/register', $this->inscription('nouveau@exemple.test'))
            ->assertRedirect('/dashboard');

        $this->assertAuthenticated();
        $nouveau = User::where('email', 'nouveau@exemple.test')->firstOrFail();
        $this->assertTrue($nouveau->hasRole('utilisateur'));
    }

    public function test_un_role_injecte_a_l_inscription_est_ignore(): void
    {
        // L'attaquant ajoute un champ « role » au formulaire
        $this->post('/register', $this->inscription('attaquant@exemple.test') + ['role' => 'administrateur']);

        $attaquant = User::where('email', 'attaquant@exemple.test')->firstOrFail();
        $this->assertFalse($attaquant->hasRole('administrateur'), 'Le rôle envoyé par le client a été accepté.');
        $this->assertFalse($attaquant->can('gerer-utilisateurs'));
        $this->assertTrue($attaquant->hasRole('utilisateur'));
    }

    // ---------- Étape 6 : routes et vues ----------

    /**
     * La matrice d'accès : une ligne par case.
     */
    public static function matriceDAcces(): array
    {
        return [
            'visiteur sur /accueil' => ['visiteur', '/accueil', 200],
            'visiteur sur /login' => ['visiteur', '/login', 200],
            'visiteur sur /dashboard' => ['visiteur', '/dashboard', 302],
            'visiteur sur /admin/users' => ['visiteur', '/admin/users', 302],
            'utilisateur sur /accueil' => ['utilisateur', '/accueil', 200],
            'utilisateur sur /login' => ['utilisateur', '/login', 302],
            'utilisateur sur /dashboard' => ['utilisateur', '/dashboard', 200],
            'utilisateur sur /admin/users' => ['utilisateur', '/admin/users', 403],
            'administrateur sur /accueil' => ['administrateur', '/accueil', 200],
            'administrateur sur /login' => ['administrateur', '/login', 302],
            'administrateur sur /dashboard' => ['administrateur', '/dashboard', 200],
            'administrateur sur /admin/users' => ['administrateur', '/admin/users', 200],
        ];
    }

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

    public function test_un_visiteur_est_redirige_vers_la_connexion(): void
    {
        $this->get('/dashboard')->assertRedirect('/login');
        $this->get('/admin/users')->assertRedirect('/login');
    }

    public function test_la_page_d_administration_liste_les_utilisateurs(): void
    {
        $this->actingAs($this->admin)
            ->get('/admin/users')
            ->assertOk()
            ->assertSee('utilisateur@exemple.test');
    }

    public function test_l_accueil_s_adapte_au_profil(): void
    {
        // Visiteur
        $this->get('/accueil')
            ->assertSee('Se connecter')
            ->assertDontSee('Espace utilisateur')
            ->assertDontSee('Espace administrateur');

        // Utilisateur
        $this->actingAs($this->utilisateur)->get('/accueil')
            ->assertSee('Espace utilisateur')
            ->assertDontSee('Espace administrateur')
            ->assertDontSee('Se connecter');

        // Administrateur
        $this->actingAs($this->admin)->get('/accueil')
            ->assertSee('Espace administrateur')
            ->assertDontSee('Espace utilisateur')
            ->assertDontSee('Se connecter');
    }

    public function test_le_lien_d_administration_suit_la_permission(): void
    {
        $this->actingAs($this->utilisateur)->get('/dashboard')
            ->assertOk()
            ->assertDontSee('Gestion des utilisateurs');

        $this->actingAs($this->admin)->get('/dashboard')
            ->assertOk()
            ->assertSee('Gestion des utilisateurs');
    }

    // ---------- Étape 3 : déconnexion (tableau de bord minimal) ----------

    public function test_la_deconnexion_n_accepte_que_post(): void
    {
        $this->actingAs($this->utilisateur);

        $this->get('/logout')->assertStatus(405);
        $this->assertAuthenticated();

        $this->post('/logout')->assertRedirect('/');
        $this->assertGuest();
    }

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
