# Direction artistique, Quantum Consulting

Tout ce qui définit l'identité du site, en un seul endroit. Les valeurs de ce
document sont celles réellement utilisées : elles vivent dans
`assets/quantum.css`, sous forme de variables CSS.

Un aperçu visuel est disponible en ouvrant `charte/index.html` dans un
navigateur.

## Le principe

Le dégradé du logo est la seule couleur du site. Tout le reste est du noir
d'encre sur un blanc cassé. Cette retenue est volontaire : une palette réduite
et un accent unique produisent une impression de sérieux qu'aucune accumulation
de couleurs ne donne.

## Couleurs

| Rôle | Variable CSS | Valeur | Usage |
|---|---|---|---|
| Fond principal | `--bg` | `#F6F6F3` | Fond de toutes les pages |
| Fond secondaire | `--bg-2` | `#ECECE8` | Une section sur deux, pour séparer sans trait |
| Encre | `--ink` | `#111318` | Texte courant, titres, bordures fortes |
| Encre atténuée | `--ink-2` | `rgba(17, 19, 24, .64)` | Texte secondaire, légendes |
| Encre faible | `--ink-3` | `rgba(17, 19, 24, .42)` | Mentions, marges |
| Filet | `--line` | `rgba(17, 19, 24, .14)` | Séparateurs discrets |
| Filet marqué | `--line-strong` | `rgba(17, 19, 24, .45)` | Contours de champs et d'encadrés |

### Le dégradé du logo

```
#ddd6fe  →  #a855f7  →  #22d3ee
lavande     violet       cyan
```

- `--grad` : `linear-gradient(135deg, #ddd6fe 0%, #a855f7 50%, #22d3ee 100%)`
  Boutons principaux, logo, barre de progression, contours des nœuds animés.
- `--grad-h` : même dégradé à l'horizontale, pour les filets.
- `--grad-text` : `linear-gradient(135deg, #6d28d9 0%, #a855f7 45%, #0891b2 100%)`
  Version approfondie, réservée au **texte**.

### Pourquoi deux dégradés

Sur fond clair, la lavande `#ddd6fe` disparaît et le cyan `#22d3ee` plafonne à
1,6 pour 1 de contraste, très loin du minimum de 4,5 exigé pour du texte. Le
dégradé d'origine reste donc pour les aplats et les traits, où le contraste ne
se mesure pas de la même façon ; une version assombrie sert dès qu'il s'agit de
lettres à lire.

Même raison pour les accents unis :

| Variable | Valeur | Usage |
|---|---|---|
| `--violet` | `#6d28d9` | Petits libellés, liens, numéros. Lisible sur fond clair |
| `--cyan` | `#0e7490` | Second niveau de libellé |
| `--violet-bright` | `#a855f7` | Aplats, puces, surlignages. Jamais pour du petit texte |
| `--cyan-bright` | `#22d3ee` | Idem, décoratif seulement |

## Typographie

Trois familles, toutes sous licence libre (SIL Open Font License), fichiers
dans `polices/`.

### Big Shoulders Display, titres

Grotesque condensée, industrielle, issue de la signalétique. Elle porte
l'impact. Toujours en capitales, interlignage serré (0.88 à 1), graisse 700 en
général et 800 pour les titres de page.

```css
font-family: 'Big Shoulders Display', 'Arial Narrow', sans-serif;
```

### Archivo, texte courant

Grotesque neutre et très lisible en petits corps. Tout ce qui se lit en
paragraphe. Graisses 400 et 500, interlignage 1,55 à 1,75.

```css
font-family: 'Archivo', system-ui, sans-serif;
```

### Space Mono, données et interface

Chasse fixe. Réservée à ce qui relève de la mesure ou de l'interface :
navigation, boutons, libellés de champ, numéros, étiquettes de section.
Toujours en petit corps, en capitales, avec un interlettrage large
(0,1 à 0,14 em).

```css
font-family: 'Space Mono', ui-monospace, monospace;
```

### Règle d'emploi

Un bloc de texte n'utilise jamais plus de deux familles. La mono ne sert jamais
à un paragraphe, la display jamais à autre chose qu'un titre ou un chiffre.

## Le logo

La marque est un Q dont la queue forme une loupe. Géométrie inchangée depuis
l'origine, dégradé d'origine conservé.

```svg
<path d="M 43.68 51.78 A 23.04 23.04 0 1 1 51.78 43.68" stroke="url(#qGrad)" stroke-width="5.5" stroke-linecap="round" fill="none"/>
<line x1="38.4" y1="39.68" x2="56.32" y2="56.32" stroke="url(#qGrad)" stroke-width="5.5" stroke-linecap="round"/>
```

Le bloc typographique qui l'accompagne : **QUANTUM** en Big Shoulders Display
700, interlettrage 0,12 em, et **CONSULTING** en Space Mono, corps deux fois
plus petit, interlettrage 0,32 em.

Zone de protection : la hauteur du Q de chaque côté. Taille minimale : 24 px de
haut pour le signe seul.

## Formes et mouvement

- **Angles vifs.** Aucun arrondi sur les boutons, les champs, les encadrés. Le
  seul cercle du site est celui du logo.
- **Traits, pas d'ombres.** Les blocs se séparent par un filet d'un pixel. Une
  ombre portée n'apparaît que sur les menus déroulants.
- **Courbe d'accélération** unique : `cubic-bezier(0.22, 1, 0.36, 1)`,
  variable `--ease`. Les objets décélèrent comme des objets réels.
- **Deux animations signature** : l'écran d'entrée où le Q se trace puis rejoint
  la barre de navigation, et le flux de travail qui s'allume au défilement.
- Tout mouvement s'efface sous `prefers-reduced-motion`, et l'état final reste
  celui du CSS : sans JavaScript, la page est complète.

## Polices fournies

Fichiers `.woff2`, sous-ensembles latin et latin étendu, téléchargés depuis
Google Fonts. Les familles Archivo et Big Shoulders Display sont des fontes
variables : un seul fichier couvre toutes les graisses.

| Fichier | Famille | Poids couverts |
|---|---|---|
| `Archivo-variable-latin.woff2` | Archivo | 100 à 900 |
| `Archivo-variable-latin-ext.woff2` | Archivo | 100 à 900 |
| `BigShouldersDisplay-variable-latin.woff2` | Big Shoulders Display | 100 à 900 |
| `BigShouldersDisplay-variable-latin-ext.woff2` | Big Shoulders Display | 100 à 900 |
| `SpaceMono-400-latin.woff2` | Space Mono | 400 |
| `SpaceMono-400-latin-ext.woff2` | Space Mono | 400 |
| `SpaceMono-700-latin.woff2` | Space Mono | 700 |
| `SpaceMono-700-latin-ext.woff2` | Space Mono | 700 |

Les trois familles sont publiées sous SIL Open Font License 1.1 : usage
commercial, modification et intégration dans un produit autorisés. La licence
doit accompagner les fichiers en cas de redistribution.

Le site charge aujourd'hui ces polices depuis Google Fonts. Les héberger
nous-mêmes à partir de ce dossier supprimerait une requête vers un tiers et
l'envoi de l'adresse IP des visiteurs à Google, ce qui est cohérent avec ce que
nous conseillons à nos clients en matière de données personnelles.
