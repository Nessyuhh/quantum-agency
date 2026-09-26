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

## Jarvis, l'assistant du site, gratuit

Le même Worker sert Jarvis sur la route `/chat` (`formulaire/chat.js`).
**Tout est gratuit, et le reste par construction.**

```
Navigateur ──POST /chat──▶ Worker ──▶ Groq : Llama 3.3 70B, puis Qwen 3.8, puis GPT-OSS 120B
                             │  └──▶ Z.ai : GLM-4.7-Flash (seulement si la clé est posée)
                             │  └──▶ Workers AI : Mistral Small 3.1
           ◀── flux SSE ─────┘
           sinon 503 : la fenêtre répond seule, recherche dans le site (navigateur)
```

1. Le Worker cherche dans `assets/chat-index-fr.json` (ou `-en`) les passages
   du site qui répondent à la question, avec le moteur partagé
   `assets/chat-recherche.js`.
2. Il fait rédiger la réponse par le premier modèle gratuit disponible de la
   chaîne (`CHAINE` en tête de `chat.js`), à partir de ces passages seulement.
   Dès qu'un modèle atteint son quota, le suivant prend le relais. Le
   raisonnement que certains modèles écrivent entre `<think>` et `</think>`
   est retiré avant d'arriver au visiteur.
3. Si aucun modèle ne répond, la fenêtre du site cherche elle-même la
   meilleure question-réponse du site et la cite, ou oriente vers le contact.

Pourquoi c'est gratuit :

- **Groq**, offre gratuite sans carte bancaire : au-delà du quota, l'API
  répond 429, elle ne facture pas. Trois modèles, dont Qwen (Alibaba),
  hébergés aux États-Unis. Ne jamais ajouter de moyen de paiement au compte.
- **Z.ai**, GLM-4.7-Flash, gratuit sans plafond journalier publié. Les
  messages sortent de l'Union européenne vers un prestataire chinois :
  facultatif, activé seulement si la clé `ZAI_API_KEY` est posée.
- **Workers AI**, offre gratuite du compte Cloudflare, 10 000 unités par
  jour : au-delà, la requête échoue, elle n'est pas facturée sur l'offre
  gratuite de Workers.
- Nos plafonds restent en dessous des quotas, au cas où un compte passerait
  un jour sur une offre payante : voir `CHAINE`, et 25 messages par adresse
  IP et par heure.

Tests, sans réseau : `node outils/test-chat.mjs`.

La base de connaissance se régénère depuis les pages :
`python3 outils/chat-index.py`.

### Mise en service

Le bouton de Jarvis est déjà actif sur le site. Tant que le Worker n'est pas
redéployé, la route `/chat` n'existe pas et Jarvis répond par la recherche
locale : il fonctionne, mais il cite au lieu de rédiger. Pour qu'il rédige :

> Contexte. Le site https://quantum-agency.fr (dépôt Nessyuhh/quantum-agency)
> a un assistant, Jarvis, servi par le Cloudflare Worker `quantum-formulaire`,
> route `https://api.quantum-agency.fr/chat`, code dans `formulaire/`. Tout
> doit rester gratuit : aucun moyen de paiement, nulle part.
>
> 1. Crée un compte gratuit sur https://console.groq.com, sans carte
>    bancaire, et une clé d'API nommée `quantum-agency-site`. Montre-moi
>    chaque écran avant de valider. Si une étape demande un paiement,
>    arrête-toi. Ne colle jamais la clé dans un fichier ni dans la
>    conversation.
> 2. Facultatif, seulement si je te le confirme après t'avoir rappelé que les
>    messages des visiteurs partiraient alors vers un prestataire chinois :
>    même chose sur https://z.ai pour une clé d'API, en n'utilisant que le
>    modèle gratuit GLM-4.7-Flash.
> 3. Depuis `formulaire/` : `npx wrangler secret put GROQ_API_KEY` (et
>    `ZAI_API_KEY` si l'étape 2 a été faite), en me laissant coller chaque clé
>    moi-même, puis `npx wrangler deploy`. Le fichier `wrangler.toml` déclare
>    déjà la liaison Workers AI. Vérifie dans le tableau de bord Cloudflare que
>    le compte est sur l'offre gratuite de Workers (« Workers Free ») et
>    dis-le-moi.
> 4. Vérifie :
>    `curl -N -X POST https://api.quantum-agency.fr/chat -H 'Origin: https://quantum-agency.fr' -H 'Content-Type: application/json' -d '{"langue":"fr","messages":[{"role":"user","content":"Que contient le site vitrine offert ?"}]}'`
>    Attendu : des lignes `data: {"t":...}` puis `data: {"fin":true,...}`.
>    Une origine étrangère doit répondre 403.
> 5. Ouvre le site sur ordinateur et sur téléphone, pose deux questions à
>    Jarvis, et envoie-moi une capture de chaque.
>
> Ne modifie aucun fichier du dépôt.
