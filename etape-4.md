# Étape 4 : Attribuer un rôle dès l'inscription (côté serveur)

À la fin de cette étape, tout nouvel inscrit reçoit le rôle `utilisateur`, et un rôle envoyé par le client est ignoré.

## Le danger : le mass assignment

Quand vous faites `User::create($request->all())`, vous passez **tout** le tableau du client directement en base. Si le modèle accepte tous les champs (via `$guarded = []` ou un `$fillable` trop large), un attaquant peut ajouter un champ caché dans le formulaire et lui donner n'importe quelle valeur.

Laravel protège avec :

- **`$fillable`** (liste blanche) : seuls ces champs sont acceptés.
- **`$guarded`** (liste noire) : tous les champs sont acceptés, sauf ceux-là.

Dans le squelette Laravel 13, c'est l'attribut `#[Fillable([...])]` au-dessus de la classe `User`.

**Mais avec Spatie**, le rôle n'est pas une colonne de `users` : `$fillable` ne sert donc à rien ici. Le vrai danger, c'est le code qui lit le rôle depuis la requête :

```php
$user->assignRole($input['role'] ?? 'utilisateur'); // DANGER : le client décide
```

## Comprendre le flux d'un formulaire

```text
Formulaire HTML (blade)
        │
        ▼
POST /register (requête HTTP)
        │
        ▼
Route → Controller (ou Action Fortify)
        │
        ▼
Validation ──► Si échec : redirect back + erreurs
        │
        ▼ (si succès)
Création du modèle
        │
        ▼
Réponse (redirect, JSON, …)
```

Laravel injecte l'objet `$request` dans le contrôleur. Il contient **tout** ce que le client a envoyé (corps du POST, paramètres de l'URL, champs cachés, etc.), y compris les champs invisibles ajoutés via les outils de développement du navigateur.

| Méthode | Renvoie | Sûr ? |
| --- | --- | :-: |
| `$request->all()` | **Tout**, brut, sans filtre | Non |
| `$request->input('name')` | Un seul champ, brut | Non |
| `$request->only(['name','email'])` | Seulement ces champs, mais non validés | Non validé |
| `$request->validated()` | **Seulement** les champs qui ont une règle et qui ont passé la validation | Oui |

## Pour aller plus loin : le Form Request

*Lecture facultative : vous pouvez passer directement à « La version sûre ». Ce Form Request n'est pas utilisé dans ce TP : avec Fortify, la validation et la création du compte passent par l'action `CreateNewUser` (voir plus bas), qui applique exactement le même principe.*

Plutôt que de valider dans le contrôleur, on crée une classe Form Request :

```bash
php artisan make:request StoreUserRequest
```

```php
// app/Http/Requests/StoreUserRequest.php
class StoreUserRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'name' => ['required', 'string', 'max:255'],
            'email' => ['required', 'string', 'email', 'max:255', 'unique:users'],
            'password' => ['required', 'confirmed', Password::defaults()],
        ];
    }
}
```

Puis dans le contrôleur :

```php
public function store(StoreUserRequest $request)
{
    // Seulement name, email, password : rien d'autre
    $data = $request->validated();

    $user = User::create([
        'name' => $data['name'],
        'email' => $data['email'],
        'password' => Hash::make($data['password']),
    ]);

    $user->assignRole('utilisateur'); // fixé en dur

    return redirect('/dashboard');
}
```

Si le client envoie `role=administrateur`, ce champ est **simplement absent** de `$request->validated()`, parce qu'il n'a pas de règle dans `rules()`.

## La version sûre

**Faire** — dans `app/Actions/Fortify/CreateNewUser.php`, remplacez la méthode `create()` par :

```php
    public function create(array $input): User
    {
        // validate() ne renvoie QUE les champs déclarés dans les règles
        $data = Validator::make($input, [
            'name' => ['required', 'string', 'max:255'],
            'email' => ['required', 'string', 'email', 'max:255', Rule::unique(User::class)],
            'password' => $this->passwordRules(),
        ])->validate();

        $user = User::create([
            'name' => $data['name'],
            'email' => $data['email'],
            'password' => Hash::make($data['password']),
        ]);

        // Le rôle est fixé en dur, jamais lu depuis la requête
        $user->assignRole('utilisateur');

        return $user;
    }
```

**Pourquoi ça marche :** `$data` ne contient que `name`, `email` et `password`. Le champ `role` envoyé par le client est simplement **absent** de `$data`, et le rôle est fixé en dur par le serveur.

**Tests qui doivent passer :**

```bash
php artisan test --filter=test_l_inscription_attribue_le_role_utilisateur
php artisan test --filter=test_un_role_injecte_a_l_inscription_est_ignore
```

## Exercice : se faire attaquer soi-même

L'objectif : voir l'attaque réussir, puis vérifier que le test la détecte.

> [!NOTE]
> **Mémo — Les outils de développement du navigateur.** On les ouvre avec **F12**, ou avec **Ctrl + Shift + I** (Chrome, Edge et Firefox). L'onglet qui affiche et permet de modifier le HTML de la page en direct s'appelle **Elements** sous Chrome et Edge, **Inspecteur** sous Firefox. Attention : sous Firefox, Ctrl + Shift + E ouvre l'onglet Réseau, pas l'Inspecteur.

> [!WARNING]
> Un `type="hidden"` n'est **pas** une protection. Le client peut toujours modifier tout ce qui est envoyé.

Le serveur de développement doit tourner pour les points 3 et 5. S'il est arrêté, relancez `php artisan serve` dans un terminal dédié.

1. Remplacez `$user->assignRole('utilisateur');` par la ligne vulnérable : `$user->assignRole($input['role'] ?? 'utilisateur');`
2. Lancez `php artisan test --filter=test_un_role_injecte` : le test **doit échouer**. S'il passe, il ne protège rien : signalez-le.
3. Dans le navigateur, allez sur `http://127.0.0.1:8000/register` et ouvrez les outils de développement (onglet Elements, ou Inspecteur sous Firefox). Trouvez la balise `<form>` et ajoutez à la main, **à l'intérieur** du formulaire :

   ```html
   <input type="hidden" name="role" value="administrateur">
   ```

   Remplissez le formulaire avec une adresse e-mail neuve et validez.

4. Dans `php artisan tinker`, affichez les rôles du dernier inscrit :

   ```php
   App\Models\User::latest('id')->first()->getRoleNames()
   ```

   Vous devez voir `administrateur`.

5. Remettez la version sûre, puis rejouez les points 2 à 4 (avec une autre adresse e-mail) : le test passe, et le nouveau compte n'a que `utilisateur`.

6. Nettoyez ensuite la base de développement :

   ```bash
   php artisan migrate:fresh --seed
   ```

   Cette commande supprime tous les comptes de test : celui de l'attaque, resté administrateur, et ceux créés avant cette étape, qui n'ont aucun rôle. Elle recrée les deux comptes de démonstration.

**À rendre :** les deux sorties de tinker (vulnérable et sûre) et les deux résultats de test.

> **Question 3.** Dans la version vulnérable, la validation n'a pas bloqué le champ `role`. Pourquoi ? Qu'est-ce qui change si le code lit `$data` au lieu de `$input` ?

## En résumé

| À faire | À éviter |
| --- | --- |
| `$request->validated()` / `$data` | `$request->all()` / `$input` |
| Form Request avec `rules()` explicites | `$guarded = []` sur le modèle |
| Rôle, statut, prix fixés en dur côté serveur | Lire ces valeurs depuis la requête |
| Valider **avant** d'écrire en base | Écrire en base puis valider |

**Le client ne décide jamais de ce qui est sensible ; le serveur filtre et fixe.**
