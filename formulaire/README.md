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

## Chatbot

Le même Worker sert l'assistant du site sur la route `/chat`
(`formulaire/chat.js`). Le navigateur envoie la conversation, le Worker
ajoute le texte intégral du site (`/llms-full.txt`, relu au plus une fois par
heure) et interroge Claude, puis renvoie la réponse en flux.

```
Navigateur  ──POST /chat──▶  Worker  ──▶  API Claude (claude-opus-5)
            ◀──── flux SSE ────┘
```

Garde-fous en place :

- **Origine** : seules nos deux adresses de site sont servies, comme pour le formulaire.
- **Coût** : 40 messages par adresse IP et par heure, 1 500 par jour pour
  tout le site. Si le compteur est indisponible, le chat refuse plutôt que de
  dépenser sans compter. Le préfixe (consignes et contenu du site) est mis en
  cache côté Claude : relu à un dixième du prix.
- **Conversation** : 16 messages au plus, 1 200 caractères par message,
  12 000 au total ; au-delà, les plus anciens sont oubliés.
- **Contenu** : le modèle ne répond qu'à partir du site, n'invente ni prix ni
  engagement, et renvoie vers l'audit pour le reste. Les consignes sont en
  tête de `chat.js`.
- **Refus** : en cas de refus de sécurité du modèle, la requête est rejouée
  automatiquement sur un modèle de repli (`fallbacks: "default"`), sinon le
  visiteur reçoit un message poli avec l'adresse de contact.
- **Page** : la réponse n'est jamais insérée comme du HTML, seuls nos propres
  liens deviennent cliquables.

Tests, sans réseau :

```bash
cd formulaire && npm ci && cd .. && node outils/test-chat.mjs
```

### Mise en service

Le bouton du chat est masqué tant que `CHATBOT_ACTIF` vaut `false` en tête du
bloc « Chatbot » de `assets/quantum.js`. On peut l'essayer sur n'importe
quelle page en ajoutant `?chat=1` à l'adresse.

Prompt à transmettre à une session connectée aux comptes Anthropic et
Cloudflare :

> Contexte. Le site https://quantum-agency.fr (dépôt Nessyuhh/quantum-agency)
> a un chatbot servi par le Cloudflare Worker `quantum-formulaire`, sur
> `https://api.quantum-agency.fr/chat`. Le code est dans `formulaire/`. Il
> manque la clé d'API Claude et le déploiement.
>
> 1. Sur https://platform.claude.com, dans l'organisation de Quantum
>    Consulting, crée une clé d'API nommée `quantum-agency-chatbot`, dans un
>    espace de travail dédié au site, avec une limite de dépense mensuelle que
>    tu me proposes avant de la fixer (point de départ suggéré : 50 dollars).
>    Montre-moi chaque écran avant de valider. Ne colle jamais la clé dans un
>    fichier ni dans la conversation.
> 2. Depuis `formulaire/` : `npm ci`, puis `npx wrangler secret put
>    ANTHROPIC_API_KEY` en me laissant coller la clé moi-même, puis
>    `npx wrangler deploy`.
> 3. Vérifie avec :
>    `curl -N -X POST https://api.quantum-agency.fr/chat -H 'Origin: https://quantum-agency.fr' -H 'Content-Type: application/json' -d '{"langue":"fr","messages":[{"role":"user","content":"Que contient l audit gratuit ?"}]}'`
>    Attendu : une suite de lignes `data: {"t":...}` puis `data: {"fin":true}`.
>    Une origine étrangère doit répondre 403.
> 4. Dans `assets/quantum.js`, passe `CHATBOT_ACTIF` à `true`, commite avec un
>    message en français sans tiret long, et pousse.
> 5. Ouvre le site sur ordinateur et sur téléphone, pose deux questions au
>    chat, et envoie-moi une capture de chaque.
>
> Ne modifie aucun autre fichier. Si une étape demande un paiement ou
> l'acceptation de conditions, arrête-toi et demande-moi.
