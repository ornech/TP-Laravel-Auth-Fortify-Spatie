# Étape 4 : Attribuer un rôle dès l'inscription (côté serveur)

Objectif : tout nouvel inscrit reçoit le rôle `utilisateur`, et un rôle envoyé par le client est ignoré.

Le danger : le mass assignment

Quand vous faites `User::create($request->all())`, vous passez **tout** le tableau du client directement en base. Si le modèle accepte (via `$guarded = []` ou un `$fillable` trop large), un attaquant peut ajouter un champ caché dans le formulaire et lui donner n'importe quelle valeur.

Laravel protège avec :

- **`$fillable`** (liste blanche) : seuls ces champs sont acceptés.
- **`$guarded`** (liste noire) : tous les champs sauf ceux-là sont acceptés.

Dans le squelette Laravel 13, c'est l'attribut `#[Fillable([...])]` au-dessus de la classe `User`.

**Mais avec Spatie**, le rôle n'est pas une colonne de `users`, donc `$fillable` ne sert à rien ici. Le vrai danger, c'est le code qui lit le rôle depuis la requête :

```php
$user->assignRole($input['role'] ?? 'utilisateur'); // ❌ le client décide
```

---

Comprendre le flux d'un formulaire

```
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

Laravel injecte automatiquement l'objet `$request` dans le contrôleur. Il contient **tout** ce que le client a envoyé (body du POST, query string, champs cachés, etc.) :

```php
public function store(Request $request)
{
    // $request->all() = TOUT ce que le client a envoyé
    // (y compris les champs invisibles ajoutés via F12)
}
```

### Les méthodes pour accéder aux données

| Méthode | Renvoie | Sûr ? |
| --- | --- | :-: |
| `$request->all()` | **Tout**, brut, sans filtre | ❌ |
| `$request->input('name')` | Un seul champ brut | ❌ |
| `$request->only(['name','email'])` | Seulement ces champs (mais pas validés) | ⚠️ |
| `$request->validated()` | **Seulement** les champs qui ont une règle et qui ont passé la validation | ✅ |

### Pour aller plus loin : le Form Request (la bonne pratique)

*Lecture facultative, vous pouvez passer directement à « La version sûre ». Ce Form Request n'est pas utilisé dans ce TP : avec Fortify, la validation et la création du compte passent par l'action `CreateNewUser` (voir plus bas). Le principe est exactement le même.*

Plutôt que de valider dans le contrôleur, on crée une **classe Form Request** :

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
    // ✅ Seulement name, email, password — rien d'autre
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

Si le client envoie `role=administrateur`, il est **simplement absent** de `$request->validated()` parce qu'il n'a pas de règle dans `rules()`.

### Pourquoi `validated()` est la seule option sûre

```
Client envoie : { name, email, password, role: "administrateur" }
                              │
                              ▼
                rules() = [name, email, password]
                              │
                              ▼
        validated() = { name, email, password }   ← role est EFFACÉ
```

C'est exactement le principe de la variable `$data` dans `CreateNewUser`, ci-dessous : `Validator::make(...)->validate()` ne renvoie que les champs déclarés.

---

### La version sûre (à implémenter)

Dans `app/Actions/Fortify/CreateNewUser.php`, remplacez la méthode `create()` par :

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

**Pourquoi ça marche :** `$data` ne contient que `name`, `email`, `password`. Le champ `role` envoyé par le client est simplement **absent** de `$data`. Et le rôle est fixé en dur par le serveur.

---

### Tests attendus

- `test_l_inscription_attribue_le_role_utilisateur` → passe.
- `test_un_role_injecte_a_l_inscription_est_ignore` → passe.

---

### Exercice — se faire attaquer soi-même

L'objectif : voir l'attaque réussir, puis vérifier que le test la détecte.

**Préparer l'attaque avec F12 :**

**F12** = raccourci pour ouvrir les **Developer Tools** du navigateur (`Ctrl + Shift + I` sur Chrome/Edge, `Ctrl + Shift + E` sur Firefox). L'onglet **Elements** permet de modifier le HTML de la page en temps réel.

> [!WARNING]
> Un `type="hidden"` n'est **pas** une protection. Le client peut toujours modifier tout ce qui est envoyé.

1. Remplacez `assignRole('utilisateur')` par la ligne vulnérable : `$user->assignRole($input['role'] ?? 'utilisateur')`.
2. Lancez `php artisan test --filter=test_un_role_injecte` → le test **doit échouer**. S'il passe, il ne protège rien : signalez-le.
3. Dans le navigateur, allez sur `/register`, ouvrez **F12** → onglet **Elements**. Trouvez la balise `<form>` et ajoutez à la main :

```html
<input type="hidden" name="role" value="administrateur">
```

Inscrivez un nouveau compte normalement.

4. Dans `php artisan tinker`, affichez les rôles du dernier inscrit :

```
App\Models\User::latest('id')->first()->getRoleNames()
```

→ vous devez voir `administrateur`.

5. Remettez la version sûre, rejouez les points 2 à 4 → le test passe, et le nouveau compte n'a que `utilisateur`.

**À rendre :** les deux sorties de tinker (vulnérable + sûre) et les deux résultats de test.

6. Nettoyez ensuite la base de développement :

```bash
php artisan migrate:fresh --seed
```

Cette commande supprime tous les comptes de test : celui de l'attaque, resté administrateur, et ceux créés avant cette étape, qui n'ont aucun rôle. Elle recrée les deux comptes de démonstration.

---

### Question 3

> Dans la version vulnérable, la validation n'a pas bloqué le champ `role`. Pourquoi ? Qu'est-ce qui change si le code lit `$data` au lieu de `$input` ?

---

### En résumé

| À faire | À éviter |
| --- | --- |
| `$request->validated()` / `$data` | `$request->all()` / `$input` |
| Form Request avec `rules()` explicites | `$guarded = []` sur le modèle |
| Rôle / status / prix fixés en dur côté serveur | Lire ces valeurs depuis la requête |
| Valider **avant** d'écrire en base | Écrire en base puis valider |

**Le client ne décide jamais de ce qui est sensible ; le serveur filtre et fixe.**
