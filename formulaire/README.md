# Formulaire d'audit : mise en service

Le formulaire du site envoie un POST JSON à un Cloudflare Worker, qui envoie
l'e-mail par Resend. Rien à héberger, rien à maintenir, gratuit à ce volume
(100 000 requêtes par jour sur l'offre gratuite, usage commercial autorisé).

```
Navigateur  ──POST JSON──▶  Worker Cloudflare  ──API──▶  Resend  ──▶  contact@quantum-agency.fr
```

L'e-mail part **avant** la réponse au navigateur : le visiteur ne lit
« demande reçue » que si la demande est réellement partie.

## 1. Clé Resend dédiée

Dans Resend, créer une clé nommée `quantum-agency-site`, avec la permission
d'envoi seule. Ne pas réutiliser la clé d'un autre projet : une révocation ou
un dépassement de quota ailleurs couperait le formulaire.

Vérifier que `quantum-agency.fr` est bien un domaine vérifié dans Resend, et
que `formulaire@quantum-agency.fr` peut servir d'expéditeur.

## 2. Déploiement, branchement et vérification

Une seule commande, depuis ce dossier :

```bash
./deployer.sh
```

Le script enchaîne les cinq étapes : authentification Cloudflare (une page
s'ouvre dans le navigateur), saisie de la clé Resend, déploiement, branchement
des douze formulaires sur l'URL obtenue, et test d'envoi réel. Il s'arrête avec
un message clair si une étape échoue.

Si le Worker est déjà déployé et qu'il ne reste qu'à brancher le site :

```bash
./brancher.sh https://quantum-formulaire.VOTRE-SOUS-DOMAINE.workers.dev
```

## 3. Vérifier à la main, si besoin

```bash
curl -i -X POST https://quantum-formulaire.VOTRE-SOUS-DOMAINE.workers.dev \
  -H 'Content-Type: application/json' -H 'Origin: https://quantum-agency.fr' \
  -d '{"nom":"Essai","email":"vous@exemple.fr","entreprise":"Essai","message":"Test","page":"/contact.html","timestamp":"2026-09-17T08:00:00.000Z"}'
```

Attendu : `HTTP/2 200`, un en-tête `access-control-allow-origin`, et l'e-mail
dans la boîte. Une origine absente ou étrangère doit renvoyer `403`.

Le formulaire ne fonctionne depuis un serveur local qu'en ajoutant
temporairement `http://127.0.0.1:8765` à `ORIGINES_AUTORISEES` dans
`wrangler.toml`, puis en redéployant. Penser à le retirer ensuite.

## 4. Domaine propre (facultatif)

Pour servir le Worker sur `api.quantum-agency.fr` plutôt que `workers.dev`, il
faut que le DNS du domaine soit géré par Cloudflare. Il est aujourd'hui chez
Hostinger : c'est une migration de DNS, à faire séparément et sans urgence.
L'adresse `workers.dev` fonctionne parfaitement en attendant.

## Ce que fait le Worker

- N'accepte que `POST` depuis `quantum-agency.fr` et `www.quantum-agency.fr`.
  Toute autre origine reçoit `403`, sans en-tête CORS.
- Refuse une demande sans nom, sans entreprise ou avec un e-mail mal formé, et
  tronque les champs trop longs.
- Ignore silencieusement les robots qui remplissent le champ piège `site_web`,
  invisible dans la page et injoignable au clavier.
- Échappe le HTML des champs avant de composer l'e-mail.
- Renvoie `502` si Resend échoue, pour que le site affiche une vraie erreur au
  lieu d'un faux succès.

## Tests

Le fichier de tests couvre les neuf cas ci-dessus sans appeler le réseau :

```bash
node ../outils/test-formulaire.mjs
```
