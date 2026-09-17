# Passer le DNS de quantum-agency.fr chez Cloudflare

Gratuit, réversible, et sans toucher ni à l'hébergement du site ni à vos
e-mails. Le domaine reste acheté chez Hostinger : seuls les serveurs de noms
changent.

**Ce que vous y gagnez**

- Le cache de dix minutes imposé par GitHub Pages disparaît, soit 97 Ko en
  moins à retélécharger à chaque visite répétée.
- Un temps de réponse serveur meilleur que l'actuel, mesuré à 1,1 seconde sur
  un article de blog.
- Le formulaire peut passer sur `api.quantum-agency.fr` au lieu de l'adresse
  en `workers.dev`.

**Le risque, et il est réel.** Si un seul enregistrement MX ou TXT manque à la
bascule, vous cessez de recevoir vos e-mails, ou les messages du formulaire
partent en indésirables, et vous vous en apercevez plusieurs jours plus tard.
Cloudflare importe la zone automatiquement, mais l'import est parfois
incomplet. D'où l'étape 3, qui n'est pas facultative.

---

## Avant de commencer

Prenez la photo de référence de la zone actuelle :

```bash
./outils/verifier-dns.sh > /tmp/dns-avant.txt && cat /tmp/dns-avant.txt
```

Les contrôles doivent être au vert. C'est l'état à retrouver à l'identique
après la bascule.

Pendant une bascule, un résolveur local garde l'ancienne délégation en cache
jusqu'à une journée et affiche donc un résultat périmé. Interroger un résolveur
public pour voir l'état réel : `./outils/verifier-dns.sh 1.1.1.1`

---

## 1. Créer le compte et ajouter le domaine

Sur `dash.cloudflare.com`, connectez-vous avec le compte qui héberge déjà le
Worker du formulaire, puis **Add a site**, saisissez `quantum-agency.fr` et
choisissez l'offre **Free**. Cloudflare lit la zone existante et propose une
liste d'enregistrements importés.

## 2. Ne validez pas encore

Cloudflare affiche les serveurs de noms à renseigner chez Hostinger.
**Ne les changez pas tout de suite.** Vérifiez d'abord la zone importée.

## 3. Contrôler les douze enregistrements, un par un

Dans l'onglet **DNS** de Cloudflare, la zone doit contenir exactement ceci :

| Type | Nom | Valeur | Proxy |
|---|---|---|---|
| A | `quantum-agency.fr` | 185.199.108.153 | **Proxied** (nuage orange) |
| A | `quantum-agency.fr` | 185.199.109.153 | **Proxied** |
| A | `quantum-agency.fr` | 185.199.110.153 | **Proxied** |
| A | `quantum-agency.fr` | 185.199.111.153 | **Proxied** |
| CNAME | `www` | nessyuhh.github.io | **Proxied** |
| MX | `quantum-agency.fr` | mx1.improvmx.com, priorité 10 | **DNS only** (nuage gris) |
| MX | `quantum-agency.fr` | mx2.improvmx.com, priorité 20 | **DNS only** |
| TXT | `quantum-agency.fr` | `v=spf1 include:spf.improvmx.com ~all` | sans objet |
| TXT | `resend._domainkey` | la clé publique Resend, en entier | sans objet |
| TXT | `_dmarc` | `v=DMARC1; p=none; rua=mailto:contact@quantum-agency.fr; fo=1; adkim=r; aspf=r` | sans objet |
| MX | `send` | feedback-smtp.eu-west-1.amazonses.com, priorité 10 | **DNS only** |
| TXT | `send` | `v=spf1 include:amazonses.com ~all` | sans objet |

Trois pièges à éviter :

1. **Les MX ne doivent jamais être en Proxied.** Cloudflare ne relaie pas le
   courrier : un MX derrière le nuage orange casse la réception. Le nuage doit
   être gris.
2. **La clé DKIM de Resend est longue et se laisse tronquer** au copier-coller.
   Comparez-la avec la valeur relevée par le script de vérification.
3. **Le CNAME `www` doit rester `nessyuhh.github.io`**, pas une adresse IP.
4. **Les deux enregistrements sur `send` sont ceux des retours de Resend.** Ils
   ne sautent pas aux yeux dans un inventaire de la zone racine, et les oublier
   ne casse rien tout de suite : les rejets et les plaintes cessent simplement
   de revenir, et la réputation du domaine se dégrade en silence.

## 4. Vérifier avant de basculer

Cloudflare affiche deux serveurs de noms qui vous sont propres. Interrogez-les
directement, la zone doit répondre correctement avant même le changement :

```bash
./outils/verifier-dns.sh nom-du-serveur-cloudflare.ns.cloudflare.com
```

Les contrôles doivent être au vert. **Si un seul est rouge, corrigez chez
Cloudflare et relancez.** Ne passez pas à l'étape suivante avant.

## 5. Changer les serveurs de noms chez Hostinger

Dans Hostinger, section DNS du domaine, remplacez
`ns1.dns-parking.com` et `ns2.dns-parking.com` par les deux serveurs fournis
par Cloudflare. La propagation prend de quelques minutes à quelques heures.

## 6. Contrôler après la bascule

```bash
./outils/verifier-dns.sh
```

Puis, dans l'ordre :

- Ouvrir `https://quantum-agency.fr` et vérifier que le site s'affiche.
- **S'envoyer un e-mail à `contact@quantum-agency.fr`** depuis une adresse
  extérieure et vérifier qu'il arrive. C'est le contrôle le plus important.
- Envoyer le formulaire du site et vérifier que les deux e-mails partent.

## 7. Réglages utiles, une fois la zone active

- **SSL/TLS → Overview** : mode **Full**. En `Flexible`, GitHub Pages boucle.
- **Speed → Optimization** : activer Brotli.
- **Caching → Configuration** : Browser Cache TTL sur 4 heures au moins. C'est
  ce réglage qui supprime la limite des dix minutes de GitHub Pages.
- **Rules → Page Rules** : facultatif. Trois règles gratuites.

## En cas de problème : revenir en arrière

Remettez `ns1.dns-parking.com` et `ns2.dns-parking.com` chez Hostinger. La zone
d'origine n'a pas été modifiée, elle reprend la main en quelques minutes à
quelques heures. Rien n'est perdu.

---

## Après la bascule, si vous voulez l'adresse propre pour le formulaire

Une fois la zone active chez Cloudflare :

1. Dans `formulaire/wrangler.toml`, ajouter la route du Worker sur
   `api.quantum-agency.fr/*`.
2. Redéployer : `cd formulaire && wrangler deploy`.
3. Rebrancher le site : `./formulaire/brancher.sh https://api.quantum-agency.fr`.
4. Ajouter la nouvelle origine dans `ORIGINES_AUTORISEES` si nécessaire, puis
   valider et pousser.

Dites-le-moi à ce moment-là, je m'en charge.
