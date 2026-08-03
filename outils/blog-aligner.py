#!/usr/bin/env python3
"""
Aligne les articles de blog sur la coquille du site officiel.

POURQUOI CE SCRIPT EXISTE
`blog-construire.py` bâtit chaque article à partir de `blog/audit-ia-guide.html`,
un article écrit AVANT la refonte. Les 105 articles ont donc hérité d'un site
qui n'existe plus : fond blanc quand le site est sombre, favicon en data-URI au
lieu du logo officiel, et une feuille de style dont une règle casse la mise en
page.

Résultat vu par un visiteur : en arrivant sur un article, le fond change, l'icône
d'onglet change, et trois blocs se superposent en haut de page. L'impression
n'est pas « une page mal réglée », c'est « je ne suis plus sur le même site ».

CE QUE ÇA CORRIGE

1. ⚠️ LA RÈGLE QUI CASSE TOUT
   `nav:not(.breadcrumb){position:fixed;top:20px;left:50%;transform:...}` visait
   la barre de navigation du site. Mais elle attrape TOUS les <nav> de la page.
   Or trois autres éléments sont des <nav> :
     · nav.art-sommaire   → le sommaire se colle par-dessus la barre
     · nav.art-prevnext   → la carte « article suivant » aussi
     · nav.q-lang         → le sélecteur de langue part au CENTRE de l'écran
                             au lieu de rester en haut à droite
   Un seul sélecteur trop large, trois symptômes sans rapport apparent.

2. LE THÈME
   Les couleurs de `:root` passent du clair au sombre du site. C'est ce qui rend
   au passage les sous-titres lisibles : `blog-mise-en-lecture.py` avait déjà
   posé des gris clairs (#e2e8f0, #cbd5e1) prévus pour un fond sombre, qui sur
   fond blanc tombaient à 1,2:1 de contraste — invisibles. Ces couleurs
   deviennent correctes une fois le fond sombre rétabli ; ce sont les couleurs
   FONCÉES du gabarit clair qu'il faut remonter.

3. LE FAVICON
   Le data-URI est remplacé par /favicon.svg, celui du reste du site.

Rejouable sans risque : chaque correction est conditionnée à sa propre présence.

    python3 outils/blog-aligner.py
"""

import pathlib
import re

RACINE = pathlib.Path(__file__).resolve().parent.parent
BLOG = RACINE / 'blog'

# ── 1. Le correctif de mise en page ──────────────────────────────────────────
# Posé APRÈS la règle fautive pour l'emporter par l'ordre, et avec une
# spécificité supérieure pour q-lang (0,2,2 contre 0,1,1) : le sélecteur de
# langue doit retrouver sa position, pas seulement perdre la mauvaise.
BALISE = '<!-- correctif:mise-en-page -->'

CORRECTIF = BALISE + """
<style>
/* ⚠️ CORRECTIF — `nav:not(.breadcrumb){position:fixed}` visait la barre du site
   mais attrape tous les <nav>. Le sommaire, la navigation d'article et le
   sélecteur de langue se retrouvaient projetés en haut au centre, empilés
   par-dessus la barre. On les remet dans le flux. */
nav.art-sommaire,
nav.art-prevnext,
nav.art-nav,
nav.breadcrumb {
  position: static;
  transform: none;
  top: auto; left: auto; right: auto;
  z-index: auto;
  width: auto;
}
/* ⚠️ Sous 640 px, `nav:not(.breadcrumb){display:none}` masque la barre du site
   au profit du menu mobile — mais il masquait AUSSI le sommaire et la
   navigation entre articles, qui disparaissaient purement et simplement sur
   téléphone. On les réaffiche explicitement. */
@media (max-width: 640px) {
  nav.art-sommaire { display: block; }
  nav.art-prevnext, nav.art-nav { display: grid; }
  nav.breadcrumb { display: flex; }
}
/* Le dernier maillon du fil d'ariane était en rgba(0,0,0,.25) : du noir à 25 %
   sur un fond quasi noir, donc invisible. */
.breadcrumb span { color: rgba(255, 255, 255, .38); }
/* Le sélecteur de langue, lui, doit RESTER fixe : en haut à droite, comme sur
   le reste du site. Spécificité volontairement plus forte que la règle fautive. */
body > nav.q-lang {
  position: fixed;
  top: 14px; right: 18px; left: auto;
  transform: none;
  z-index: 600;
}
</style>"""

# ── 2. La palette ────────────────────────────────────────────────────────────
PALETTE = [
    ('--bg:#ffffff', '--bg:#05050a'),
    ('--bg2:#f8fafc', '--bg2:#0c0c1a'),
    ('--purple-l:#7c3aed', '--purple-l:#a855f7'),
    ('--cyan:#0891b2', '--cyan:#06b6d4'),
    ('--text:#1e293b', '--text:#f1f5f9'),
    ('--muted:#64748b', '--muted:#94a3b8'),
    ('--border:rgba(0,0,0,.08)', '--border:rgba(255,255,255,.07)'),
]

# Les couleurs écrites en dur dans le gabarit clair. Sur fond sombre elles
# deviennent illisibles : #374151 sur #05050a donne 2,1:1.
EN_DUR = [
    ('background:#ffffff', 'background:#05050a'),
    ('color:#1e293b', 'color:#f1f5f9'),
    ('color:#374151', 'color:#cbd5e1'),
    ('color:#111827', 'color:#f8fafc'),
    ('color:#0f172a', 'color:#f8fafc'),
    ('color:#334155', 'color:#cbd5e1'),
]

FAVICON = re.compile(r'<link rel="icon"[^>]*href="data:image/svg\+xml[^"]*"[^>]*>')


def aligner(chemin: pathlib.Path) -> list[str]:
    s = chemin.read_text(encoding='utf-8')
    avant, faits = s, []

    # ⚠️ Le bloc est REMPLACÉ, pas seulement ajouté s'il manque. Sans ça, toute
    # correction ultérieure du correctif serait ignorée sur les pages déjà
    # traitées — et l'aligneur donnerait l'illusion d'avoir tout réglé.
    if BALISE in s:
        d = s.index(BALISE)
        f = s.index('</style>', d) + len('</style>')
        if s[d:f] != CORRECTIF:
            s = s[:d] + CORRECTIF + s[f:]
            faits.append('mise en page (mise à jour)')
    else:
        s = s.replace('</head>', CORRECTIF + '\n</head>', 1)
        faits.append('mise en page')

    if '--bg:#ffffff' in s:
        for de, vers in PALETTE + EN_DUR:
            s = s.replace(de, vers)
        faits.append('thème sombre')

    # ⚠️ Sans ce script, aucun moyen de passer en anglais depuis un article :
    # le sélecteur de langue n'existait tout simplement pas sur les 105 pages.
    if 'lang-switch.js' not in s:
        s = s.replace('</body>', '<script src="/lang-switch.js" defer></script>\n</body>', 1)
        faits.append('sélecteur de langue')

    if FAVICON.search(s):
        s = FAVICON.sub('<link rel="icon" type="image/svg+xml" href="/favicon.svg">', s)
        faits.append('favicon')

    if s != avant:
        chemin.write_text(s, encoding='utf-8')
    return faits


def main():
    total = {}
    fichiers = sorted(BLOG.glob('*.html'))
    for f in fichiers:
        for quoi in aligner(f):
            total[quoi] = total.get(quoi, 0) + 1

    print(f'  {len(fichiers)} articles parcourus')
    for quoi, n in sorted(total.items()):
        print(f'    {quoi:<16} {n}')
    if not total:
        print('    (déjà alignés)')


if __name__ == '__main__':
    main()
