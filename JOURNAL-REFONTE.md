# Refonte du site, septembre 2026

Ce document remplace la mémoire d'une session de travail. Il dit ce qui a été
fait, **pourquoi**, ce qui a été mesuré, et ce qui reste ouvert. Les décisions y
figurent avec leur raison : c'est la partie qu'aucun `git log` ne rend.

État à la clôture : **tout est en ligne sur quantum-agency.fr**, 26 commits
fusionnés dans `main` par la pull request 1.

---

## 1. Le point de départ

Le site était un cas d'école de ce que l'utilisateur voulait fuir : fond
`#05050a`, dégradés néon violet et cyan, verre dépoli, pastilles animées,
bandeau de mots-clés défilant, fausse fenêtre de conversation avec une IA,
grille de trois cartes, Inter partout. Trois défauts fonctionnels :

- le formulaire d'audit n'envoyait rien, `handleForm` affichait un message ;
- le pied de page portait `contact@quantum-consulting.fr` et un faux numéro
  `+33 1 00 00 00 00` ;
- les noms de modèles dataient : Claude 3.5 Sonnet, GPT-4o, Gemini 1.5 Pro,
  Llama 3, sur plus de cent fichiers.

## 2. La direction artistique

Trois directions ont été proposées, puis rejetées, avant d'aboutir. Ce chemin
compte plus que le résultat : **les descriptions écrites n'ont jamais permis de
trancher, les captures d'écran oui**. Toute nouvelle proposition visuelle doit
passer par une image.

Retenue : fond clair, **le dégradé du logo comme seule couleur**, typographie
Big Shoulders Display, Archivo et Space Mono, angles vifs, filets plutôt
qu'ombres. Tout est documenté dans `charte/`, avec les fichiers de police sous
licence ouverte et une page d'aperçu.

Deux points non négociables appris en route :

- **Le logo est conservé tel quel**, géométrie et dégradé d'origine.
- **Le dégradé du logo est illisible en petit texte sur fond clair** : la
  lavande disparaît, le cyan plafonne à 1,6 pour 1. D'où deux dégradés, `--grad`
  pour les aplats et `--grad-text` approfondi pour les lettres, et des accents
  unis assombris, `--violet` à `#6d28d9` et `--cyan` à `#0e7490`.

## 3. Ce qui a été construit

**Arborescence ramenée de treize pages à six**, parce que la cible est un
dirigeant de PME, pas un technicien : `services.html`, `formations.html`,
`cas-usage.html`, `faq-ia.html`, `contact.html` et l'accueil. Les neuf
anciennes adresses redirigent avec `canonical` et `noindex`. Textes réécrits en
langage courant, à la première personne du pluriel.

**Accueil allégé** : hero, offre d'appel, flux animé, trois offres en bref,
formulaire. Les sections Formations, Modèles et FAQ sont parties sur leurs
pages.

**Deux animations signature.** L'écran d'entrée, rétabli à la demande, où le Q
se trace puis rejoint la barre de navigation, sur fond clair, grand écran
seulement, une fois par session, interruptible au premier geste. Et le flux de
travail animé, horizontal sur ordinateur, **vertical sur mobile** parce que le
défilement horizontal a été rejeté.

**Blog recharté par script**, index et 105 articles, sans réécriture du
contenu. `outils/blog-recharter.py` et `outils/charte-sync.py` propagent la
navigation et le pied de page : une modification, un script, tout suit.

**Version anglaise** sur les six pages, bouton EN/FR intégré à la barre de
navigation. Les articles n'existent qu'en français, `/en/blog.html` le dit et
renvoie vers eux ; le bouton de langue ne s'affiche pas sur une page sans
jumelle.

## 4. Le formulaire, et pourquoi il n'est pas sous n8n

Le premier montage passait par un n8n installé **sur le Mac de l'utilisateur**.
Un formulaire de production ne peut pas dépendre d'une machine qu'on éteint le
soir. Les options ont été pesées : n8n Cloud à 24 euros par mois, un VPS à
4,50 euros, Oracle Cloud gratuit à vie mais à administrer.

Retenu : **un Cloudflare Worker qui appelle Resend**. Gratuit, usage commercial
autorisé, rien à maintenir, aucun serveur à surveiller.

`formulaire/` contient le Worker, sa configuration, le script de mise en
service et la documentation. `outils/test-formulaire.mjs` couvre seize cas sans
toucher au réseau.

Décisions à ne pas défaire :

- **La réponse part après l'envoi de l'e-mail**, jamais avant. Le montage n8n
  répondait 200 immédiatement : un visiteur lisait « demande reçue » alors que
  rien n'était parti.
- **Le Worker écrit à une adresse fournie par l'appelant**, donc il pourrait
  servir à envoyer des e-mails en notre nom à n'importe qui. Le filtrage
  d'origine ne protège de rien, il se falsifie en une ligne de commande. La
  limite de débit native de Cloudflare **ne fonctionne pas sur ce compte**,
  vérifié : réglée à une requête par minute, elle laissait tout passer. D'où un
  compteur explicite en KV, trois accusés par adresse IP et par heure, soixante
  par jour. Dépasser un plafond ne perd jamais un prospect : la demande est
  enregistrée et la notification part, seul l'accusé automatique est retenu.
- **Champ piège anti-robot** sur les douze formulaires et dans la fenêtre.

## 5. La fenêtre du site offert

Objectif commercial, formulé par l'utilisateur : **le site vitrine est un
produit d'appel pour l'audit et le consulting**. La fenêtre retient le visiteur
et récolte une adresse, sans l'engager à passer du temps avec un consultant.
Elle ne mentionne donc **jamais l'audit**, et ne demande qu'un e-mail.

Conséquence traitée : la page Services et la FAQ conditionnaient le site à la
réalisation de l'audit. Un visiteur venu par la fenêtre aurait découvert une
condition dont personne ne lui avait parlé. Le site est désormais présenté
comme offert sans condition, l'audit devenant la suite naturelle.

Déclenchement : **sortie du curseur par le haut** sur ordinateur, avec huit
secondes de grâce, plus un filet de sécurité à 45 secondes ou 60 % de la page.
Sur téléphone, le geste n'existe pas, donc temps et défilement seulement. Une
fois par visiteur, jamais sur la page Contact, quatorze jours de repos après
une fermeture.

**Sur mobile, c'est un bandeau bas et non une fenêtre modale** : Google
déclasse les pages dont un encart recouvre le contenu à l'arrivée depuis la
recherche. La conversion ne vaut pas le référencement.

Le visiteur reçoit dans la seconde un accusé automatique, version détaillée
avec le déroulé en trois jours et un bouton vers `calendly.com/younes_mh/audit`.
L'e-mail vient de la société, le rendez-vous se prend avec une personne : c'est
voulu.

## 6. Performance et accessibilité, mesuré

Lighthouse sur le site en production, mobile.

| Page | Avant | Après | Premier affichage |
|---|---|---|---|
| Accueil | 96 | 98 | 2,0 s puis 1,2 s |
| Services | 68 | 100 | 3,7 s puis 0,9 s |
| Article de blog | 56 | 100 | **9,0 s puis 1,1 s** |
| Accueil, ordinateur | 100 | 100 | 0,3 s |

Accessibilité, bonnes pratiques et référencement à **100 partout**, contre 96
et 92 avant.

Trois causes, trois corrections :

1. **Deux feuilles de style bloquantes et deux connexions à Google** pour les
   polices, sur le chemin critique, 2,1 secondes perdues à elles seules. Les
   huit fichiers de police sont maintenant servis depuis le site, préchargement
   des deux familles du premier écran, `article.css` fusionnée dans
   `quantum.css`. Bénéfice secondaire : plus aucune adresse IP de visiteur
   envoyée à Google, cohérent avec ce que le cabinet conseille à ses clients.
2. **GSAP et ses greffons, 58 Ko**, chargés partout alors qu'ils ne servent
   qu'au flux animé. Ils partent maintenant à 250 px de son approche, pendant
   un temps de repos du navigateur. Piège rencontré : l'observateur visait un
   tracé masqué en CSS, et un élément en `display:none` n'entre jamais dans le
   champ d'un `IntersectionObserver`.
3. **Quatre défauts de contraste** à 2,7 pour 1, dont les libellés du
   formulaire. `--ink-3` passe de 42 à 62 % d'opacité, soit 4,7 pour 1, avec
   une variable dédiée pour le grand mot atténué du titre.

Défaut corrigé au passage : `.btn:hover` posait le raccourci
`background: var(--ink)`, qui effaçait l'image de fond des boutons dégradés.
Ils devenaient noirs avec un libellé presque noir.

## 7. Noms de modèles

Mis à jour sur tout le site, après vérification sur les sites des éditeurs et
non de mémoire : **GPT-6**, **Claude Sonnet 5**, **Gemini 3**, **Llama 4**,
**Mistral Large 3**, **Mistral Small 4**. Les anciens noms ne subsistent que
dans `archives/`, qui n'est pas indexé.

## 8. Fait après la première clôture

**La bascule du DNS vers Cloudflare est faite.** Les serveurs de noms sont
`walt` et `yolanda.ns.cloudflare.com`. Le temps de réponse serveur est passé de
1110 ms à 190 ou 260 ms, et `api.quantum-agency.fr` sert le formulaire. Piège
rencontré ensuite : `verifier-dns.sh` contrôlait les adresses IP de GitHub, qui
ne sont plus visibles derrière le proxy ; il interroge maintenant le site en
HTTP et garde le DNS pour le courrier. Il lui manquait aussi les deux
enregistrements de retour de Resend sur `send.quantum-agency.fr`, absents de
l'inventaire d'origine parce qu'il ne regardait que la racine de la zone.

**Soumission à Gemini** faite, en trois passes. Sa première réponse était
entièrement fabriquée : sept affirmations données pour observées, toutes
fausses, et une autre entreprise décrite à la place de la nôtre. La deuxième
était honnête, la troisième inventait encore deux liens internes et proposait
des adresses de page déjà prises par des articles du blog. Règle qui en
découle : **toute recommandation d'un modèle externe se vérifie fichier en main
avant d'être appliquée.** Ce qui a été retenu et appliqué : titres tournés vers
le dirigeant sur sept articles, bloc « En bref » et questions fréquentes sur
les cinq articles qui en manquaient.

**Mesure d'audience** GA4 avec Consent Mode v2, page de confidentialité en deux
langues, propriété de domaine validée dans Search Console et plan du site de
119 adresses déclaré. Ajouts d'une autre session, commit `e3eab17`.

**Messages du formulaire dans la langue de la page.** Les quatre messages
étaient écrits en français en dur : un visiteur anglophone lisait « Merci !
Votre demande a été reçue ». Ils suivent maintenant l'attribut `lang` de la
page, comme le faisait déjà la fenêtre du site offert.

## 9. Trois défauts que personne n'avait vus

Trouvés en balayant le site plutôt qu'en cherchant un symptôme. Aucun ne se
voyait depuis le site lui-même, et c'est précisément ce qui les rendait
durables.

**Aucun article n'avait de vignette de partage.** Les 105 articles désignaient
`og-image.svg` comme image de partage. Aucun réseau social n'accepte le SVG :
ni LinkedIn, ni X, ni WhatsApp, ni Slack. Ils déclaraient pourtant
`twitter:card = summary_large_image`, donc promettaient une grande vignette
sans en livrer aucune, et ce fichier datait d'avant la refonte. L'adresse
passait en plus par `www`, qui répond 301. Corrigé par
`outils/normaliser-partage.py`, avec les dimensions et le texte de
remplacement. **Le cache des réseaux garde l'ancienne réponse plusieurs
semaines** : la revalidation est le prompt 1 de `outils/PROMPTS-EXTERNES.md`.

**Trois articles affichaient une question sans réponse**, à chaque fois une
balise fermante mal écrite (`</j3>`, `</p>` à la place de `</h3>`). Sur l'un
d'eux, deux questions s'étaient fondues en une seule avec un retour à la ligne
au milieu d'une chaîne JSON, ce qui invalidait le bloc FAQPage entier et le
faisait ignorer par les moteurs. La réponse manquante a été écrite, et
`outils/resynchroniser-faq.py` régénère désormais le bloc depuis le texte
affiché : la page est la source unique.

**Le fil d'Ariane était coupé au milieu d'un mot** sur 75 pages, à soixante
caractères, alors qu'il passe à la ligne tout seul. Et les sept articles
retitrés gardaient l'ancien titre dans leurs données structurées, oubli de
`reecrire-titres.py`. Corrigé dans les pages et dans le script.

Deux pièges d'outillage découverts en réparant : `charte-sync.py` effaçait tous
les `aria-current` de la page pour replacer l'onglet actif, y compris celui du
fil d'Ariane ; et faire suivre le fil d'Ariane structuré au h1 convient à un
article mais pas à une page de métier, où le fil nomme la catégorie et le titre
porte une promesse. **C'est le fil affiché qui fait foi.**

## 10. La page métier

`expertise-comptable.html`, première page de métier. Le blog traitait déjà le
sujet deux fois, mais sous l'angle informatif ; il manquait la page que cherche
un associé qui veut savoir ce que nous faisons chez lui. Les cabinets sont le
métier où le volume documentaire est le plus lourd et la tolérance à l'erreur
la plus basse, donc le meilleur premier candidat.

Trois choix à garder si d'autres métiers suivent :

- **Une section entière dit ce que nous n'automatisons pas.** Sur une
  profession réglementée, c'est le bloc qui fait la différence, pas la liste
  des gains.
- **Le secret professionnel est traité comme point de départ**, pas comme une
  contrainte à contourner.
- **Elle n'entre pas dans la barre de navigation.** Un lien dans le pied de
  page, propagé aux 114 pages par `charte-sync.py`, plus deux liens depuis les
  articles concernés. Si d'autres métiers arrivent, transformer cette ligne en
  colonne « Secteurs » plutôt que de rallonger le menu.

## 11. Ce qui reste ouvert

**Les liens entrants sont le frein principal.** Le contenu, la technique et la
vitesse sont au maximum de ce que le site peut faire seul ; ce qui manque pour
se classer est la citation par d'autres sites. Prompt 4 de
`outils/PROMPTS-EXTERNES.md`.

**Fiche d'établissement Google** pour les recherches locales parisiennes, non
créée. Prompt 3, bloqué sur une décision : quelle adresse déclarer. Une adresse
fausse fait suspendre la fiche, et la suspension est difficile à lever.

**Indexation réelle** à contrôler dans Search Console : la propriété est
validée et le plan du site déclaré, mais rien n'a encore été relevé sur le
nombre de pages effectivement indexées. Prompt 2.

**Tirets longs résiduels** dans treize scripts d'outillage anciens et sept
maquettes de développement en `noindex`. Volontairement laissés : deux des
occurrences de `blog-recharter.py` sont le motif de recherche qui sert
justement à retirer les tirets longs du contenu, et les remplacer casserait la
règle qu'elles font respecter.

Pistes non traitées, par ordre d'intérêt décroissant : sous-ensemble des
polices aux seuls caractères utilisés, minification de `quantum.js` (2 Ko),
transitions entre pages, pôle Marchés publics BTP prévu dans
`ARBORESCENCE.md` et jamais construit.

## 12. Règles de travail, à respecter par la suite

- **Aucun tiret long**, nulle part : contenu, code, commentaires, messages de
  commit. C'est une marque de rédaction automatique pour l'utilisateur.
- **Première personne du pluriel** pour la voix de l'entreprise. Les questions
  de FAQ et les boutons restent à la voix du visiteur.
- **Cible non technique** : pas de sigle sans explication, le bénéfice avant
  l'outil, 400 à 600 mots par page.
- **Valider sur captures d'écran**, jamais sur des descriptions.
- **L'utilisateur n'exécute pas les manipulations externes lui-même.** Tout ce
  qui sort de la portée de l'agent, comptes tiers, OAuth, DNS, clés d'API,
  part sous forme de prompt autonome destiné à une autre session.
- **Vérifier en production**, pas seulement en local. Plusieurs défauts ne sont
  apparus que sur le site réel, dont le cache de dix minutes qui sert l'ancien
  fichier quelques minutes après une publication.

## 13. Repères de fichiers

| Chemin | Rôle |
|---|---|
| `assets/quantum.css` | Design system, variables, composants, blog |
| `assets/quantum.js` | Navigation, FAQ, formulaire, écran d'entrée, fenêtre, animations |
| `charte/` | Direction artistique, polices, page d'aperçu |
| `formulaire/` | Worker Cloudflare, configuration, scripts de mise en service |
| `outils/charte-sync.py` | Propage navigation et pied de page aux pages |
| `outils/blog-recharter.py` | Recharte l'index et les 105 articles |
| `outils/test-formulaire.mjs` | Seize tests du Worker, sans réseau |
| `outils/verifier-dns.sh` | Contrôle les dix enregistrements DNS |
| `outils/normaliser-partage.py` | Images de partage et domaine nu, en contrôle avec `--verifier` |
| `outils/resynchroniser-faq.py` | Régénère les blocs FAQPage depuis les questions affichées |
| `outils/resynchroniser-schema.py` | Aligne titre, description et fil d'Ariane du schéma sur la page |
| `outils/PROMPTS-EXTERNES.md` | Les quatre tâches qui demandent un compte tiers |
| `outils/BASCULE-CLOUDFLARE.md` | Procédure de bascule du DNS |
| `outils/sitemap.py` | Régénère `sitemap.xml` |

Après toute modification de la navigation ou du pied de page :

```bash
python3 outils/charte-sync.py && python3 outils/blog-recharter.py && python3 outils/sitemap.py
```

Et avant chaque mise en ligne, trois contrôles qui échouent s'il reste quelque
chose à corriger :

```bash
python3 outils/normaliser-partage.py --verifier && python3 outils/resynchroniser-faq.py --verifier && python3 outils/resynchroniser-schema.py --verifier
```
