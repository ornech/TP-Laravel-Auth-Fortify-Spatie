# Dépannage du TP 1

Lisez d'abord le message d'erreur en entier : dans ce TP, il nomme presque toujours la cause.

| Symptôme | Cause | Correction |
| --- | --- | --- |
| php artisan test affiche du JSON au lieu du compte rendu habituel | La commande est lancée depuis un assistant IA : le package laravel/pao, présent dans le squelette Laravel 13, change le format de la sortie | Lancer la commande dans un terminal ordinaire. Sous Linux et macOS : PAO\_DISABLE=1 php artisan test |
| 419 Page Expired | Requête POST sans jeton ni en-tête Sec-Fetch-Site: same-origin : curl, autre site, ou formulaire sans @csrf dans un navigateur qui n'envoie pas cet en-tête | Ajouter @csrf dans le \<form> |
| « View \[auth.login\] not found. » | Vue absente ou mal placée | Créer resources/views/auth/login.blade.php |
| « View \[dashboard\] not found. » | Vue non créée | Étape 2 |
| « View \[accueil\] not found. » | Vue non créée | Étape 4 |
| 404 juste après la connexion | La clé home pointe vers /home | 'home' => '/dashboard' dans config/fortify.php |
| « Rate limiter \[login\] is not defined. » | boot() de FortifyServiceProvider écrasé | Restaurer RateLimiter::for('login', ...) |
| « Target \[Laravel\\Fortify\\Contracts\\CreatesNewUsers\] is not instantiable. » | createUsersUsing supprimé de boot() | Restaurer Fortify::createUsersUsing(CreateNewUser::class) |
| « Target \[Laravel\\Fortify\\Contracts\\ConfirmPasswordViewResponse\] is not instantiable. » | Visite de /user/confirm-password : Fortify enregistre toujours cette route, et aucune vue n'est déclarée | Ne pas utiliser cette route, ou déclarer Fortify::confirmPasswordView(...) dans boot() |
| Base de développement vidée après les tests | phpunit.xml pointe vers la vraie base | SQLite en mémoire (étape 1) |
