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

1. ⚠️ LA RÈGLE QUI CASSAIT TOUT — corrigée à la source depuis
   `nav:not(.breadcrumb){position:fixed;top:20px;left:50%;transform:...}` visait
   la barre du site, mais attrapait TOUS les <nav> : sommaire, navigation entre
   articles, filtres de thème du blog, sélecteur de langue. Chacun se retrouvait
   projeté en haut au centre, empilé sur la barre.

   Exclure `.breadcrumb` nommément ne réglait qu'un cas : tout <nav> ajouté
   ensuite retombait dans le piège. Le critère réel est structurel — la barre du
   site et la barre mobile sont les seuls <nav> SANS classe. Le sélecteur est
   donc devenu `nav:not([class])` dans les 131 pages, ce qui décrit l'intention
   d'origine et se protège des ajouts futurs.

   Ce script n'a donc plus à remettre ces éléments dans le flux.

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
/* Le dernier maillon du fil d'ariane était en rgba(0,0,0,.25) — hérité du
   gabarit clair. Sur le fond sombre du site, du noir à 25 % est invisible. */
.breadcrumb span { color: rgba(255, 255, 255, .38); }
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


# ── 4. Le logo ───────────────────────────────────────────────────────────────
# ⚠️ Les articles portaient `<a class="n-logo">Quantum Consulting</a>` — du
# texte brut là où le reste du site affiche le logo. Encore un héritage du
# gabarit : un visiteur arrivant sur un article ne voyait pas la marque.
#
# Le logo est LU depuis blog.html plutôt que recopié ici : une signature dupliquée
# dans un script finit toujours par diverger de celle du site.
def logo_officiel() -> str:
    t = (RACINE / 'blog.html').read_text(encoding='utf-8')
    m = re.search(r'<a[^>]*class="n-logo"[^>]*>.*?</a>', t, re.S)
    if not m:
        return ''
    # Depuis /blog/, un href relatif « index.html » viserait /blog/index.html.
    return m.group(0).replace('href="index.html"', 'href="/"')


LOGO_TEXTE = re.compile(r'<a[^>]*class="n-logo"[^>]*>\s*Quantum Consulting\s*</a>')

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

    if LOGO_TEXTE.search(s):
        officiel = logo_officiel()
        if officiel:
            s = LOGO_TEXTE.sub(lambda _: officiel, s)
            faits.append('logo')

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
