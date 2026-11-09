# Dépannage du TP 1

Lisez d'abord le message d'erreur en entier : dans ce TP, il nomme presque toujours la cause.

| Symptôme | Cause | Correction |
| --- | --- | --- |
| php artisan test affiche du JSON au lieu du compte rendu habituel | La commande est lancée depuis un assistant IA : le package laravel/pao, présent dans le squelette Laravel 13, change le format de la sortie | Lancer la commande dans un terminal ordinaire. Sous Linux et macOS : PAO\_DISABLE=1 php artisan test |
| 419 Page Expired | Requête POST sans jeton ni en-tête Sec-Fetch-Site: same-origin : curl, autre site, ou formulaire sans @csrf dans un navigateur qui n'envoie pas cet en-tête | Ajouter @csrf dans le \<form> |
| « Class "Database\\Seeders\\DemoUserSeeder" not found » | Seeder pas encore créé | Étape 1 |
| « Failed asserting that two strings are equal » avec /dashboard d'un côté et /home de l'autre | La clé home de config/fortify.php n'a pas été modifiée | 'home' => '/dashboard' (étape 2) |
| « Target \[Laravel\\Fortify\\Contracts\\LoginViewResponse\] is not instantiable. » (ou RegisterViewResponse) | Les vues ne sont pas déclarées dans boot() | Ajouter Fortify::loginView(...) et Fortify::registerView(...) (étape 2) |
| « View \[auth.login\] not found. » | Vue absente ou mal placée | Créer resources/views/auth/login.blade.php |
| « View \[auth.register\] not found. » | Vue d'inscription absente ou mal placée | Créer resources/views/auth/register.blade.php |
| Test d'inscription : « To contain: password\_confirmation » | Le champ de confirmation manque ou porte un autre nom dans register.blade.php | name="password\_confirmation" |
| « Les passkeys (connexion sans mot de passe) doivent être désactivées. », ou route:list affiche 18 lignes au lieu de 11 | Features::passkeys n'est pas entièrement commenté | Commenter toutes ses lignes, jusqu'au \]), inclus |
| Test d'accueil : long bloc HTML terminé par « To contain: Se connecter » | /accueil n'existe pas, ou sa vue manque : le bloc est la page d'erreur | Lire plutôt les cas /accueil de la matrice (étape 4) |
| « View \[dashboard\] not found. » | Vue non créée | Étape 2 |
| « View \[accueil\] not found. » | Vue non créée | Étape 4 |
| 404 juste après la connexion | La clé home pointe vers /home | 'home' => '/dashboard' dans config/fortify.php |
| « Rate limiter \[login\] is not defined. » | boot() de FortifyServiceProvider écrasé | Restaurer RateLimiter::for('login', ...) |
| « Target \[Laravel\\Fortify\\Contracts\\CreatesNewUsers\] is not instantiable. » | createUsersUsing supprimé de boot() | Restaurer Fortify::createUsersUsing(CreateNewUser::class) |
| « Target \[Laravel\\Fortify\\Contracts\\ConfirmPasswordViewResponse\] is not instantiable. » | Visite de /user/confirm-password : Fortify enregistre toujours cette route, et aucune vue n'est déclarée | Ne pas utiliser cette route, ou déclarer Fortify::confirmPasswordView(...) dans boot() |
| Base de développement vidée après les tests | phpunit.xml pointe vers la vraie base | SQLite en mémoire (étape 1) |
