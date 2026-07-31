# Arborescence — trois activités, deux publics

Arrêtée le 31 juillet 2026.

## Le principe qui commande tout

Le risque n'est pas le nombre d'entrées, c'est le **mélange des publics**. Un artisan du BTP n'a
rien à faire dans « Agents IA & LLM privés » ; un dirigeant de PME n'a rien à faire dans
« montage de dossiers de candidature ». Le fouillis vient de là.

Or les trois activités ne se répartissent pas à égalité :

```
PUBLIC 1 — dirigeants de PME, tous secteurs
   ├── Consulting IA     « je le fais pour vous »
   └── Formation IA      « je vous apprends à le faire »
        └─ intrinsèquement liés : on audite puis on forme, ou on forme puis on construit

PUBLIC 2 — artisans et entreprises du BTP
   └── Marchés publics BTP
        └─ le chiffrage y sera un OUTIL, pas une offre distincte
```

**Consulting et Formation restent deux entrées séparées** — ce sont deux propositions
commerciales différentes, à des prix différents. Mais elles partagent un public, donc elles
cohabitent sans friction.

## Ce que l'accueil fait

L'accueil **parle au public IA**, avec une porte BTP claire et permanente.

La raison est une réalité de trafic, pas une hiérarchie de valeur : **les prospects BTP arrivent
par la prospection directe** — un e-mail de Thibault les amène sur la page marchés publics, ils ne
voient jamais l'accueil. Imposer une page d'aiguillage à la majorité, pour une minorité qui ne la
verrait pas, serait un mauvais calcul. Une page d'aiguillage a en outre presque rien à indexer,
ce qui pénaliserait le référencement de la page la mieux placée du site.

## Navigation

```
Consulting  ·  Formation  ·  │  ·  Marchés publics BTP        [Audit gratuit →]
                             ↑
                    séparateur visuel : on change de territoire
```

Le séparateur n'est pas décoratif : il signale qu'on quitte le pôle IA. C'est ce qui remplace la
page d'aiguillage sans en payer le coût.

## Signature visuelle par pôle

Le pôle BTP prend l'**ambre** `#f59e0b`, déjà présent dans la palette du site — et déjà apparu
naturellement dans l'animation des appels d'offres, où il porte le compte à rebours. L'ambre dit
l'échéance ; c'est exactement le sujet de ce pôle.

| | Pôle IA | Pôle Marchés publics BTP |
|---|---|---|
| Accent | violet `#7c3aed → #a855f7` | ambre `#f59e0b` |
| Registre | transformation, capacité | échéance, conformité |
| Public | dirigeants de PME | artisans et entreprises du BTP |

On ne change ni la marque, ni la typographie, ni le fond : **seul l'accent bascule**. On doit
savoir où l'on est sans y penser, pas avoir l'impression d'avoir changé de site.

## Pages

### Pôle IA — Consulting *(existe)*
`consulting-ia.html` · `audit-ia.html` · `integration-ia.html` · `automatisation-ia.html` ·
`agents-ia.html`

### Pôle IA — Formation *(existe)*
`formation-initiation-ia.html` · `formation-maitrise-ia.html` · `formation-expert-ia.html`

### Pôle BTP — Marchés publics *(à créer)*
- `marches-publics.html` — la page pilier du pôle, celle où atterrit la prospection
- `marches-publics-methode.html` — comment on procède, du repérage au dépôt
- `marches-publics-resultats.html` — preuves : dossiers déposés, taux de conformité

Le **chiffrage** n'aura pas d'entrée de navigation : il apparaîtra dans la méthode, comme une
capacité de l'accompagnement. Cohérent avec ce qu'a montré la recherche — le **DQE d'un marché
public *est* un chiffrage**.

### Transverses *(existent)*
`index.html` · `contact.html` · `faq-ia.html` · `cas-usage.html` · `blog.html` · `modeles-ia.html`

⚠️ `faq-ia.html` et `cas-usage.html` sont aujourd'hui **implicitement rattachés au pôle IA** alors
que leur nom ne le dit pas. À trancher : soit on les marque comme tels, soit on y ajoute une
section BTP. Ne pas laisser l'ambiguïté — c'est exactement par là que le fouillis revient.

### À retirer de la navigation publique
`quantum-logos.html` · `quantum-logos-final.html` · `email-signature.html` ·
`business-card.html` · `intro-preview.html` · `animation-atom.html` ·
`quantum-logo-animation.html`

Ce sont des pages de travail interne, périmées depuis le kit de marque du 30 juillet. Elles n'ont
rien à faire dans un site public et diluent le référencement.

## Ordre d'exécution

1. **Extraire le CSS commun.** Mesuré : 123 Ko dupliqués, soit 45 % du CSS du site, sur 88 règles
   présentes dans 10 pages ou plus. C'est la cause du bug de menu qui a touché 13 pages sur 14 —
   toucher la navigation sans corriger ça, c'est reproduire le défaut.
2. **Poser la nouvelle navigation**, séparateur et accent de pôle compris.
3. **Créer les trois pages du pôle BTP.**
4. **Intégrer les sections d'ouverture animées** (`apercus/`), une mécanique par page.
5. **Sortir les pages de travail** de la navigation publique.
