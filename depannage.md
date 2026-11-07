# Dépannage

Lisez d'abord le message d'erreur en entier : dans ce TP, il nomme presque toujours la cause.

| Symptôme | Cause | Correction |
| --- | --- | --- |
| 419 Page Expired | Requête POST sans jeton ni en-tête Sec-Fetch-Site: same-origin : curl, autre site, ou formulaire sans @csrf dans un navigateur qui n'envoie pas cet en-tête | Ajouter @csrf dans le \<form> |
| « View \[auth.login\] not found. » | Vue absente ou mal placée | Créer resources/views/auth/login.blade.php |
| « View \[dashboard\] not found. » | Vue non créée | Étape 3 |
| « View \[accueil\] not found. » | Vue non créée | Étape 6 |
| 404 juste après la connexion | La clé home pointe vers /home | 'home' => '/dashboard' dans config/fortify.php |
| « Rate limiter \[login\] is not defined. » | boot() de FortifyServiceProvider écrasé | Restaurer RateLimiter::for('login', ...) |
| « Target \[Laravel\\Fortify\\Contracts\\CreatesNewUsers\] is not instantiable. » | createUsersUsing supprimé de boot() | Restaurer Fortify::createUsersUsing(CreateNewUser::class) |
| « Target \[Laravel\\Fortify\\Contracts\\ConfirmPasswordViewResponse\] is not instantiable. » | Visite de /user/confirm-password : Fortify enregistre toujours cette route, et aucune vue n'est déclarée | Ne pas utiliser cette route, ou déclarer Fortify::confirmPasswordView(...) dans boot() |
| « There is no role named \`utilisateur\` for guard \`web\`. » | Seeders non lancés, ou nom de rôle mal orthographié | php artisan db:seed --class=RoleSeeder, puis comparer les noms avec php artisan permission:show |
| « A role \`utilisateur\` already exists for guard \`web\`. » | Role::create dans un seeder relancé | Role::findOrCreate |
| « Target class \[permission\] does not exist. » | Alias non déclaré | Étape 5 |
| « Target class \[Spatie...\] does not exist. » | Nom de classe faux dans l'alias | Comparer avec vendor/spatie/laravel-permission/src/Middleware |
| Permission ajoutée, accès toujours refusé | Cache de Spatie | php artisan permission:cache-reset |
| Migration de Spatie en échec | Configuration en cache | php artisan config:clear, puis php artisan migrate |
| Base de développement vidée après les tests | phpunit.xml pointe vers la vraie base | SQLite en mémoire (étape 0) |
