#!/usr/bin/env python3
"""
Intègre les sections d'ouverture animées dans les pages du site.

CE QUI CHANGE DANS CHAQUE HÉROS
Le pavé de texte et la rangée de badges disparaissent : leur substance est déjà
DANS l'animation — « 50,9 h par semaine récupérables », « aucun outil remplacé,
aucune migration », « écarté · vos données lui appartiennent ». Il n'y a plus
rien à écrire au-dessus.

Ce qui reste : fil d'Ariane, badge, un H1 COURT, l'animation en dominante, un
seul appel à l'action.

⚠️ Le H1 reste, et ce n'est pas de la timidité : c'est le signal de
référencement le plus fort d'une page, et un lecteur d'écran ne tire rien d'une
animation au-delà de son aria-label. L'animation montre le COMMENT, le titre dit
le QUOI.
"""

import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent

# page → (fichier d'aperçu, nouveau H1)
# Les titres sont raccourcis : un titre de deux lignes se lit, un titre de
# quatre lignes se saute. Le détail vit dans l'animation.
PAGES = {
    'audit-ia.html': ('hero-audit',
        'Cartographier vos opportunités <span class="g-text">avant d\'investir</span>'),
    'integration-ia.html': ('hero-integration',
        'Brancher l\'IA sur <span class="g-text">vos outils existants</span>'),
    'automatisation-ia.html': ('hero-automatisation-noeuds',
        'Automatiser <span class="g-text">ce qui se répète</span>'),
    'agents-ia.html': ('hero-agents',
        'Des agents autonomes, <span class="g-text">vos données chez vous</span>'),
    'consulting-ia.html': ('hero-conseil',
        'Choisir la trajectoire IA <span class="g-text">qui vous convient</span>'),
    'formation-initiation-ia.html': ('hero-formations',
        'Vos équipes utilisent l\'IA <span class="g-text">sans crainte</span>'),
    'formation-maitrise-ia.html': ('hero-formations',
        'Construire vos workflows <span class="g-text">sans développeur</span>'),
    'formation-expert-ia.html': ('hero-formations',
        'Piloter une feuille de route IA <span class="g-text">sur 12 mois</span>'),
}


def morceaux(apercu):
    """Récupère le <style> propre à l'animation et ses deux tracés."""
    s = (RACINE / 'apercus' / (apercu + '.html')).read_text(encoding='utf-8')
    style = ''.join(re.findall(r'<style>(.*?)</style>', s, re.S)).strip()
    svgs = re.findall(r'(<svg class="(?:large|etroit)".*?</svg>)', s, re.S)
    return style, svgs


def integrer(page, apercu, titre):
    p = RACINE / page
    s = p.read_text(encoding='utf-8')

    deb = s.find('<header class="pg-hero"')
    if deb < 0:
        return f'{page} : pas de pg-hero'
    fin = s.find('</header>', deb) + len('</header>')
    ancien = s[deb:fin]

    fil = re.search(r'(<nav class="breadcrumb".*?</nav>)', ancien, re.S)
    tag = re.search(r'(<div class="pg-tag">.*?</div>)', ancien, re.S)
    cta = re.search(r'(<a href="[^"]+" class="btn">.*?</a>)', ancien, re.S)
    ident = re.search(r'id="([^"]+)"', ancien)

    style, svgs = morceaux(apercu)
    if len(svgs) != 2:
        return f'{page} : {len(svgs)} tracé(s) au lieu de 2'

    neuf = (
        f'<header class="pg-hero"{" id=" + chr(34) + ident.group(1) + chr(34) if ident else ""}>\n'
        '  <div class="hero-spot" id="hero-spot" aria-hidden="true"></div>\n'
        f'  {fil.group(1) if fil else ""}\n'
        f'  {tag.group(1) if tag else ""}\n'
        f'  <h1>{titre}</h1>\n'
        '  <div class="canevas hero-canevas">\n'
        + '\n'.join('    ' + x for x in svgs) + '\n'
        '  </div>\n'
        f'  {cta.group(1) if cta else ""}\n'
        '</header>'
    )

    s = s[:deb] + neuf + s[fin:]

    # La feuille des héros, une seule fois, après la feuille commune.
    if 'assets/heros.css' not in s:
        s = s.replace('<link rel="stylesheet" href="/assets/commun.css">',
                      '<link rel="stylesheet" href="/assets/commun.css">\n'
                      '<link rel="stylesheet" href="/assets/heros.css">', 1)

    # Le style propre à l'animation rejoint le <style> de la page, en tête pour
    # rester avant les règles existantes.
    if style and style[:60] not in s:
        m = re.search(r'<style[^>]*>', s[s.find('</noscript>'):])
        if m:
            pos = s.find('</noscript>') + m.end()
            s = s[:pos] + '\n/* ── section d\'ouverture animée ── */\n' + style + '\n' + s[pos:]

    p.write_text(s, encoding='utf-8')
    return f'{page} : intégrée'


if __name__ == '__main__':
    for page, (apercu, titre) in PAGES.items():
        print('  ' + integrer(page, apercu, titre))
