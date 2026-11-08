# Dépannage du TP 2

Lisez d'abord le message d'erreur en entier : dans ce TP, il nomme presque toujours la cause.

| Symptôme | Cause | Correction |
| --- | --- | --- |
| « Target class \[Database\\Seeders\\RoleSeeder\] does not exist. » | Le seeder n'est pas encore créé, ou son nom est faux | Étape 2 : php artisan make:seeder RoleSeeder |
| « There is no role named \`utilisateur\` for guard \`web\`. » | Seeders non lancés, ou nom de rôle mal orthographié | php artisan db:seed --class=RoleSeeder, puis comparer les noms avec php artisan permission:show |
| « A role \`utilisateur\` already exists for guard \`web\`. » | Role::create dans un seeder relancé | Role::findOrCreate |
| « Target class \[permission\] does not exist. » | Alias non déclaré | Étape 4 |
| « Target class \[Spatie...\] does not exist. » | Nom de classe faux dans l'alias | Comparer avec vendor/spatie/laravel-permission/src/Middleware |
| Permission ajoutée, accès toujours refusé | Cache de Spatie | php artisan permission:cache-reset |
| Migration de Spatie en échec | Configuration en cache | php artisan config:clear, puis php artisan migrate |
| « There is no role named \`utilisateur\` for guard \`web\`. » dans test\_l\_inscription\_cree\_un\_compte\_connecte (TP 1) | Le test d'inscription du TP 1 n'a pas été adapté à l'attribution du rôle | Étape 3 : ajouter $this->seed(RoleSeeder::class) dans setUp() de AuthenticationTest |
| Un autre test du TP 1 échoue après une modification du TP 2 | Un fichier du TP 1 (vue, route, CreateNewUser) a été écrasé au lieu d'être complété | Relire l'étape concernée : on ajoute, on ne remplace pas (sauf indication) |
