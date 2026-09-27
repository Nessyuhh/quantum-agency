# Déploiement continu du Worker

Depuis le 27 septembre 2026, le Worker `quantum-formulaire` est relié à ce dépôt
par Workers Builds. Il n'y a donc plus de déploiement manuel à lancer.

| Réglage | Valeur |
|---|---|
| Dépôt | `Nessyuhh/quantum-agency` |
| Branche de production | `main` |
| Répertoire racine | `/formulaire` |
| Commande de déploiement | `npx wrangler deploy` |
| Constructions de prévisualisation | désactivées |

Chaque envoi sur `main` reconstruit et redéploie le Worker, routes `/` (formulaire
de contact) et `/chat` (l'assistant Jarvis) comprises.

Rappel de l'incident qui a motivé cette mise en place : le Worker en ligne était
resté à une version antérieure à l'ajout de `chat.js`. La route `/chat` répondait
donc avec la logique du formulaire, et l'assistant du site basculait en silence
sur la recherche locale. Un déploiement oublié ne se voit pas, sauf à tester la
route elle-même.

Les secrets restent hors du dépôt et se posent toujours à la main :

```
npx wrangler secret put RESEND_API_KEY
npx wrangler secret put GROQ_API_KEY
```
