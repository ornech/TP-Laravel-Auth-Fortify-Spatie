# Contrat de tests : TP 1

Le TP 1 est terminé quand les 20 tests de ce fichier passent, dont les 6 cases de la matrice d'accès (le tableau de la section « Livrables » du README). Copiez-le à l'étape 1 dans tests/Feature/AuthenticationTest.php, sans le modifier.

Le fichier est abondamment commenté : le thème du TP n'est pas le test, mais ce mécanisme servira dans vos prochains projets. Lisez l'en-tête et les commentaires pour comprendre comment chaque test est construit.

Ce contrat n'est pas une recette à passer à la fin : c'est un outil de travail. À chaque étape, vous lancez le test concerné **avant** d'agir, vous lisez son message d'échec, vous agissez, puis vous relancez (la boucle de test, présentée à l'[étape 1](etape-1.md)). La colonne « Étape » indique où vous le rencontrez pour la première fois.

Ce que chaque test prouve

| Étape | Test | Ce qu'il prouve |
| --- | --- | --- |
| 1 | test\_les\_comptes\_de\_demonstration\_ne\_sont\_pas\_crees\_en\_production | DemoUserSeeder ne crée aucun compte en production |
| 2 | test\_seules\_les\_fonctionnalites\_utiles\_sont\_exposees | Fortify n'expose ni réinitialisation de mot de passe, ni double authentification, ni passkeys |
| 2 | test\_les\_fonctionnalites\_de\_profil\_et\_de\_mot\_de\_passe\_sont\_desactivees | Fortify n'expose ni modification du profil ni changement du mot de passe |
| 2 | test\_le\_mot\_de\_passe\_doit\_etre\_confirme | La règle confirmed est toujours appliquée |
| 2 | test\_une\_connexion\_valide\_ouvre\_une\_session | Une connexion réussie mène à /dashboard, et la requête suivante n'a pas besoin de se reconnecter |
| 2 | test\_un\_mauvais\_mot\_de\_passe\_est\_refuse | Un mauvais mot de passe ne connecte personne |
| 2 | test\_la\_connexion\_est\_bloquee\_apres\_cinq\_echecs | La sixième tentative en une minute reçoit une 429 |
| 2 | test\_les\_echecs\_d\_un\_compte\_ne\_bloquent\_pas\_les\_autres\_comptes | Le limiteur compte par couple « e-mail + IP » : un autre compte, depuis la même IP, peut encore se connecter |
| 2 | test\_la\_deconnexion\_n\_accepte\_que\_post | GET /logout répond 405, POST /logout déconnecte |
| 2 | test\_l\_inscription\_cree\_un\_compte\_connecte | Le formulaire d'inscription s'affiche avec son champ de confirmation ; l'inscription crée un compte, connecte la personne et ne stocke jamais le mot de passe en clair |
| 3 | test\_la\_connexion\_enregistre\_l\_utilisateur\_dans\_la\_session | Après une connexion, la session contient l'identifiant du compte : c'est cela qui signifie « connecté » |
| 3 | test\_la\_deconnexion\_detruit\_la\_session | La déconnexion vide la session, et /dashboard renvoie de nouveau vers /login |
| 2 et 4 | test\_la\_matrice\_d\_acces\_est\_respectee (6 cas) | Chaque case de la matrice d'accès (voir le README) : profil × route → code HTTP. Les cas /login et /dashboard se rencontrent à l'étape 2, les cas /accueil à l'étape 4 |
| 2 | test\_un\_visiteur\_est\_redirige\_vers\_la\_connexion | La redirection 302 du visiteur mène bien à /login |
| 4 | test\_l\_accueil\_s\_adapte\_au\_profil | /accueil affiche un contenu différent pour le visiteur et pour la personne connectée |

Pour lancer un seul test : `php artisan test --filter=<nom du test>`. Pour tout le contrat : `php artisan test --filter=AuthenticationTest`. Pour plusieurs tests : `php artisan test --filter="nom1|nom2"`. Pour un seul cas de la matrice : `php artisan test --filter='test_la_matrice_d_acces_est_respectee.*visiteur sur /login'`.

```php
<?php

namespace Tests\Feature;

use App\Models\User;
use Database\Seeders\DemoUserSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Route;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

/**
 * Contrat du TP 1 : ne modifiez pas ce fichier, faites-le passer.
 *
 * ============================================================================
 * COMMENT LIRE CE FICHIER (et vous en inspirer dans vos propres projets)
 * ============================================================================
 *
 * Un test décrit UN comportement attendu de l'application. Il suit presque
 * toujours trois temps :
 *
 *   1. PRÉPARER : créer ce dont le test a besoin (un compte, des données…).
 *   2. AGIR     : faire ce que ferait un client, ici une requête HTTP.
 *   3. VÉRIFIER : contrôler le résultat (code HTTP, session, base de données).
 *
 * Les mécanismes utilisés ici, réutilisables partout :
 *
 *   - extends TestCase + use RefreshDatabase
 *       Le test démarre l'application Laravel et repart d'une base propre :
 *       un test ne dépend jamais des données laissées par un autre.
 *   - setUp()
 *       Méthode exécutée avant CHAQUE test : c'est la préparation commune.
 *   - User::factory()->create([...])
 *       Fabrique un compte en base, sans passer par un formulaire. Le mot de
 *       passe fabriqué est « password ».
 *   - $this->get('/url') et $this->post('/url', [...])
 *       Simulent une requête HTTP, sans navigateur ni serveur lancé.
 *   - $this->actingAs($compte)
 *       Se faire passer pour une personne connectée, sans passer par le
 *       formulaire de connexion (utile quand la connexion n'est pas le sujet).
 *   - Les assertions : assertStatus(), assertRedirect(), assertOk(),
 *       assertSee(), assertSessionHasErrors(), assertAuthenticated(),
 *       assertGuest(), assertDatabaseMissing()… Chacune échoue avec un message
 *       qui dit ce qui était attendu et ce qui a été reçu.
 *   - #[DataProvider]
 *       Rejoue le même test avec plusieurs jeux de données (voir la matrice
 *       d'accès, plus bas).
 *
 * Trois habitudes à prendre :
 *
 *   - Lancer un test AVANT d'écrire le code qu'il protège. Son message d'échec
 *     dit ce qui manque, et un test déjà vert avant votre action ne prouve pas
 *     votre travail : il décrit un comportement qui existait déjà.
 *   - Nommer chaque test comme une phrase qui dit le comportement attendu :
 *     test_<sujet>_<ce_qui_doit_arriver>. Quand un test échoue, son nom doit
 *     suffire à comprendre ce qui est cassé.
 *   - Vérifier qu'un test PEUT échouer : cassez volontairement le code qu'il
 *     protège et constatez qu'il passe au rouge (c'est le principe des
 *     exercices du TP). Un test qui ne peut jamais échouer ne prouve rien.
 */
class AuthenticationTest extends TestCase
{
    use RefreshDatabase;

    // Le compte que la plupart des tests utilisent.
    private User $alice;

    /**
     * PRÉPARER (commun à tous les tests) : exécutée avant chaque test.
     */
    protected function setUp(): void
    {
        // Démarre l'application Laravel : cet appel est obligatoire.
        parent::setUp();

        // Le mot de passe créé par la factory est « password ».
        $this->alice = User::factory()->create(['email' => 'alice@exemple.test']);
    }

    // ---------- Étape 1 : comptes de démonstration ----------

    /**
     * Prouve : DemoUserSeeder ne crée aucun compte en production.
     *
     * Des comptes dont le mot de passe est connu de tous seraient une porte
     * d'entrée évidente. Le seeder doit donc refuser de s'exécuter hors des
     * environnements « local » et « testing ».
     */
    public function test_les_comptes_de_demonstration_ne_sont_pas_crees_en_production(): void
    {
        // PRÉPARER : on fait croire à l'application qu'elle tourne en production,
        // et on note le nombre de comptes existants.
        $this->app->detectEnvironment(fn () => 'production');
        $comptesAvant = User::count();

        // AGIR : on exécute le seeder directement. On n'utilise pas $this->seed() :
        // en production, la commande db:seed demande une confirmation et le test planterait.
        (new DemoUserSeeder)->run();

        // VÉRIFIER : le nombre de comptes n'a pas bougé.
        $this->assertSame($comptesAvant, User::count(), 'DemoUserSeeder a créé des comptes en production.');
    }

    // ---------- Étape 2 : Fortify ----------

    /**
     * Prouve : Fortify n'expose que ce que le TP utilise.
     *
     * Chaque fonctionnalité active est une route de plus à défendre : c'est la
     * surface d'attaque. Route::has('nom') indique si une route portant ce nom
     * existe dans l'application.
     */
    public function test_seules_les_fonctionnalites_utiles_sont_exposees(): void
    {
        // Les routes dont on a besoin existent… Le second argument d'une
        // assertion est le message affiché quand elle échoue.
        $this->assertTrue(Route::has('login'), 'La route de connexion est absente : Fortify est-il installé ?');
        $this->assertTrue(Route::has('register'), "La route d'inscription est absente : Features::registration() doit rester actif.");

        // …et celles dont on n'a pas besoin n'existent pas.
        $this->assertFalse(Route::has('password.request'), 'La réinitialisation de mot de passe doit être désactivée.');
        $this->assertFalse(Route::has('two-factor.login'), 'La double authentification doit être désactivée.');
        $this->assertFalse(Route::has('passkey.login'), 'Les passkeys (connexion sans mot de passe) doivent être désactivées.');
    }

    /**
     * Prouve : la modification du profil et du mot de passe est désactivée.
     *
     * Piège classique : un test qui vérifie une ABSENCE passe tout seul tant
     * que la chose n'existe pas encore. Avant d'installer Fortify, ces routes
     * n'existent pas non plus, et le test serait vert sans rien prouver. On
     * vérifie donc d'abord que Fortify est bien là.
     */
    public function test_les_fonctionnalites_de_profil_et_de_mot_de_passe_sont_desactivees(): void
    {
        // Garde-fou : sans Fortify, l'absence des routes ci-dessous ne prouverait rien.
        $this->assertTrue(Route::has('login'), 'Fortify doit être installé.');

        $this->assertFalse(Route::has('user-profile-information.update'), 'La modification du profil doit être désactivée.');
        $this->assertFalse(Route::has('user-password.update'), 'Le changement de mot de passe doit être désactivé.');
    }

    /**
     * Prouve : un mot de passe non confirmé est refusé à l'inscription.
     */
    public function test_le_mot_de_passe_doit_etre_confirme(): void
    {
        // AGIR : on envoie le formulaire d'inscription SANS le champ de confirmation.
        $this->post('/register', [
            'name' => 'Sans Confirmation',
            'email' => 'sans.confirmation@exemple.test',
            'password' => 'Secret123!',
        ])->assertSessionHasErrors('password'); // l'erreur est rattachée au champ « password »

        // VÉRIFIER : personne n'est connecté, et rien n'a été écrit en base.
        $this->assertGuest();
        $this->assertDatabaseMissing('users', ['email' => 'sans.confirmation@exemple.test']);
    }

    /**
     * Prouve : une connexion réussie ouvre une session qui dure d'une requête à l'autre.
     */
    public function test_une_connexion_valide_ouvre_une_session(): void
    {
        // AGIR : on envoie le formulaire de connexion avec les bons identifiants.
        $this->post('/login', ['email' => 'alice@exemple.test', 'password' => 'password'])
            ->assertRedirect('/dashboard'); // la page d'arrivée (clé « home » de Fortify)

        // VÉRIFIER : on est bien connecté en tant qu'alice…
        $this->assertAuthenticatedAs($this->alice);

        // …et la session retient la personne : la requête suivante n'a pas
        // besoin de se reconnecter (assertOk = code 200).
        $this->get('/dashboard')->assertOk();
    }

    /**
     * Prouve : un mauvais mot de passe ne connecte personne.
     */
    public function test_un_mauvais_mot_de_passe_est_refuse(): void
    {
        $this->post('/login', ['email' => 'alice@exemple.test', 'password' => 'mot-de-passe-faux'])
            ->assertSessionHasErrors('email'); // Fortify rattache l'échec au champ « email »

        $this->assertGuest();
    }

    /**
     * Prouve : le limiteur bloque la sixième tentative en une minute (code 429).
     */
    public function test_la_connexion_est_bloquee_apres_cinq_echecs(): void
    {
        $identifiants = ['email' => 'alice@exemple.test', 'password' => 'mauvais-mot-de-passe'];

        // Une boucle répète la même action : cinq échecs, chacun refusé normalement
        // (avec une erreur sur le champ « email »).
        for ($i = 1; $i <= 5; $i++) {
            $this->post('/login', $identifiants)->assertSessionHasErrors('email');
        }

        // Sixième tentative dans la même minute : bloquée avant toute vérification.
        $this->post('/login', $identifiants)->assertStatus(429);
        $this->assertGuest();
    }

    /**
     * Prouve : le limiteur compte par couple « e-mail + adresse IP », pas par IP seule.
     *
     * Dans un lycée, tous les postes sortent par la même IP. Dans un test, toutes
     * les requêtes viennent aussi de la même IP : c'est ce qui simule ce cas.
     * (Voir la question 1 de l'étape 2.)
     */
    public function test_les_echecs_d_un_compte_ne_bloquent_pas_les_autres_comptes(): void
    {
        // PRÉPARER : un second compte, qui n'a rien à voir avec les échecs d'alice.
        $bob = User::factory()->create(['email' => 'bob@exemple.test']);

        // AGIR : alice échoue cinq fois, puis se retrouve bloquée.
        for ($i = 1; $i <= 5; $i++) {
            $this->post('/login', ['email' => 'alice@exemple.test', 'password' => 'faux'])->assertSessionHasErrors('email');
        }
        $this->post('/login', ['email' => 'alice@exemple.test', 'password' => 'faux'])->assertStatus(429);

        // VÉRIFIER : bob, derrière la même adresse IP, peut toujours se connecter.
        $this->post('/login', ['email' => 'bob@exemple.test', 'password' => 'password'])
            ->assertRedirect('/dashboard');
        $this->assertAuthenticatedAs($bob);
    }

    /**
     * Prouve : la déconnexion se fait en POST, jamais en GET.
     *
     * Avec un GET, n'importe quel site pourrait déconnecter vos utilisateurs
     * avec un simple lien (voir le mémo de l'étape 2).
     */
    public function test_la_deconnexion_n_accepte_que_post(): void
    {
        // PRÉPARER : on se fait passer pour alice connectée, sans formulaire.
        $this->actingAs($this->alice);

        // GET /logout : méthode refusée (405), et alice reste connectée.
        $this->get('/logout')->assertStatus(405);
        $this->assertAuthenticated();

        // POST /logout : alice est déconnectée et renvoyée vers la page d'accueil du site.
        $this->post('/logout')->assertRedirect('/');
        $this->assertGuest();
    }

    /**
     * Prouve : le formulaire d'inscription s'affiche, puis l'inscription crée un
     * compte, connecte la personne, et ne stocke jamais le mot de passe en clair.
     */
    public function test_l_inscription_cree_un_compte_connecte(): void
    {
        // Le formulaire s'affiche (vue déclarée et fichier présent) et propose le
        // champ de confirmation que Fortify attend.
        $this->get('/register')->assertOk()->assertSee('password_confirmation');

        $this->post('/register', [
            'name' => 'Nouvel Inscrit',
            'email' => 'nouveau@exemple.test',
            'password' => 'Secret123!',
            'password_confirmation' => 'Secret123!',
        ])->assertRedirect('/dashboard');

        $this->assertAuthenticated();

        // On relit le compte en base (firstOrFail échoue s'il n'existe pas).
        $compte = User::where('email', 'nouveau@exemple.test')->firstOrFail();

        // Le mot de passe stocké n'est pas le mot de passe saisi : c'est un hash…
        $this->assertNotSame('Secret123!', $compte->password, 'Le mot de passe ne doit jamais être stocké en clair.');
        // …mais Laravel sait vérifier que le mot de passe saisi correspond à ce hash.
        $this->assertTrue(Hash::check('Secret123!', $compte->password));
    }

    // ---------- Étape 3 : la session ----------

    /**
     * Prouve : après une connexion, la session contient l'identifiant du compte.
     *
     * C'est la donnée que vous avez observée à l'étape 3 : une clé qui commence
     * par « login_web_ » et dont la valeur est l'identifiant de la personne
     * connectée. C'est elle qui signifie « cet utilisateur est connecté ».
     */
    public function test_la_connexion_enregistre_l_utilisateur_dans_la_session(): void
    {
        // AGIR : alice se connecte.
        $this->post('/login', ['email' => 'alice@exemple.test', 'password' => 'password']);

        // VÉRIFIER : session()->all() renvoie tout le contenu de la session. On en
        // garde les entrées dont la clé commence par « login_web_ ».
        $entrees = collect(session()->all())
            ->filter(fn ($valeur, $cle) => str_starts_with($cle, 'login_web_'));

        // Il y en a une seule, et sa valeur est l'identifiant d'alice.
        $this->assertCount(1, $entrees, "La session ne contient pas l'utilisateur connecté.");
        $this->assertSame($this->alice->id, $entrees->first());
    }

    /**
     * Prouve : la déconnexion détruit la session, et les pages protégées
     * redeviennent inaccessibles.
     *
     * Pour savoir si la session est vraiment détruite, on y glisse un « marqueur » :
     * s'il disparaît, c'est que toute la session a été vidée, pas seulement le
     * compte déconnecté.
     */
    public function test_la_deconnexion_detruit_la_session(): void
    {
        // PRÉPARER : alice se connecte, puis on place un marqueur dans sa session.
        $this->post('/login', ['email' => 'alice@exemple.test', 'password' => 'password']);
        session(['marqueur' => 'present']);
        $this->assertSame('present', session('marqueur'));

        // AGIR : elle se déconnecte.
        $this->post('/logout');

        // VÉRIFIER : personne n'est connecté, et le marqueur a disparu avec la session…
        $this->assertGuest();
        $this->assertNull(session('marqueur'), 'La session aurait dû être vidée à la déconnexion.');

        // …et une page protégée renvoie de nouveau vers la connexion.
        $this->get('/dashboard')->assertRedirect('/login');
    }

    // ---------- Étape 4 : pages et affichage ----------

    /**
     * La matrice d'accès : une ligne par case.
     *
     * Une matrice d'accès est un tableau « profil × route → résultat attendu »
     * (voir la section « Livrables » du README). Ici, chaque case du tableau
     * devient une ligne : [profil, URL, code HTTP attendu].
     *
     * Un « data provider » est une méthode statique qui renvoie une liste de cas.
     * Chaque cas est une ligne : [profil, URL, code HTTP attendu]. La clé de la
     * ligne (« visiteur sur /accueil »…) s'affiche quand le cas échoue.
     */
    public static function matriceDAcces(): array
    {
        return [
            'visiteur sur /accueil' => ['visiteur', '/accueil', 200],
            'visiteur sur /login' => ['visiteur', '/login', 200],
            'visiteur sur /dashboard' => ['visiteur', '/dashboard', 302],
            'connecté sur /accueil' => ['connecté', '/accueil', 200],
            'connecté sur /login' => ['connecté', '/login', 302],
            'connecté sur /dashboard' => ['connecté', '/dashboard', 200],
        ];
    }

    /**
     * Prouve : chaque case de la matrice d'accès. Le même test est rejoué une fois
     * par ligne du data provider, avec ses trois arguments.
     */
    #[DataProvider('matriceDAcces')]
    public function test_la_matrice_d_acces_est_respectee(string $profil, string $url, int $statut): void
    {
        // PRÉPARER : selon le profil, on se connecte ou non.
        match ($profil) {
            'connecté' => $this->actingAs($this->alice),
            'visiteur' => null, // personne n'est connecté
        };

        // AGIR + VÉRIFIER : le code HTTP reçu doit être celui de la matrice.
        $this->get($url)->assertStatus($statut);
    }

    /**
     * Prouve : la redirection du visiteur mène bien vers la page de connexion
     * (la matrice, elle, ne vérifie que le code 302).
     */
    public function test_un_visiteur_est_redirige_vers_la_connexion(): void
    {
        $this->get('/dashboard')->assertRedirect('/login');
    }

    /**
     * Prouve : la page d'accueil change selon que l'on est connecté ou non.
     * assertSee / assertDontSee cherchent un texte dans la page renvoyée.
     */
    public function test_l_accueil_s_adapte_au_profil(): void
    {
        // Visiteur : il voit le lien de connexion, pas le tableau de bord.
        $this->get('/accueil')
            ->assertSee('Se connecter')
            ->assertDontSee('Tableau de bord');

        // Personne connectée : l'inverse.
        $this->actingAs($this->alice)->get('/accueil')
            ->assertSee('Tableau de bord')
            ->assertDontSee('Se connecter');
    }
}
```
