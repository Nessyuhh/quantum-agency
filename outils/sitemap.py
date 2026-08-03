#!/usr/bin/env python3
"""Régénère sitemap.xml depuis les fichiers réellement présents.

POURQUOI UN SCRIPT PLUTÔT QU'UN FICHIER TENU À LA MAIN
Le sitemap était écrit à la main : il déclarait 28 URLs alors que le site en
comptait 133. Un sitemap incomplet ne casse rien de visible — il se contente de
priver d'indexation tout ce qu'il omet, silencieusement. C'est le pire type de
défaut : aucun symptôme, et l'effet exact qu'on cherchait à produire en écrivant
cent articles est annulé.

⚠️ RÈGLE QUI COMMANDE LE hreflang
Une balise `alternate` ne se pose QUE si la page cible existe vraiment. Déclarer
une version anglaise absente est pire que ne rien déclarer : Google écarte la
grappe hreflang entière quand un de ses membres renvoie 404, y compris pour les
pages correctement traduites. Les articles de blog n'ayant pas de version
anglaise, ils sortent sans alternate — et c'est volontaire.

    python3 outils/sitemap.py
"""

import pathlib
import re
import datetime

RACINE = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://quantum-agency.fr'
AUJ = datetime.date.today().isoformat()

# ⚠️ Pages techniques, maquettes et outils internes : présentes sur le disque,
# jamais destinées à l'indexation. Les lister ici plutôt que de les deviner
# évite qu'une future page de test parte en production dans le sitemap.
EXCLUES = {
    '404.html',
    'animation-atom.html',
    'business-card.html',
    'email-signature.html',
    'intro-preview.html',
    'quantum-logo-animation.html',
    'quantum-logos-final.html',
    'quantum-logos.html',
}

# Priorités : l'accueil d'abord, puis les pages d'offre, puis les articles.
# Un article vaut moins qu'une page de service, mais cent articles portent
# l'autorité thématique — d'où 0.6 et non 0.3.
def priorite(chemin: str) -> str:
    if chemin in ('index.html', ''):
        return '1.0'
    if chemin.startswith('blog/'):
        return '0.6'
    if chemin == 'blog.html':
        return '0.7'
    return '0.8'


def frequence(chemin: str) -> str:
    return 'weekly' if chemin in ('index.html', 'blog.html') else 'monthly'


def url_de(chemin: str) -> str:
    """`index.html` s'écrit comme la racine : une seule URL canonique par page."""
    if chemin == 'index.html':
        return f'{BASE}/'
    if chemin == 'en/index.html':
        return f'{BASE}/en/'
    return f'{BASE}/{chemin}'


def lister():
    """Les pages FR indexables, dans un ordre stable."""
    racine = sorted(
        p.name for p in RACINE.glob('*.html')
        if p.name not in EXCLUES
    )
    articles = sorted(f'blog/{p.name}' for p in (RACINE / 'blog').glob('*.html'))
    return racine + articles


def bloc(chemin: str) -> str:
    fr = url_de(chemin)
    # L'équivalent anglais n'est déclaré que s'il existe sur le disque.
    en_chemin = f'en/{chemin}'
    a_traduction = (RACINE / en_chemin).exists()

    lignes = [
        '  <url>',
        f'    <loc>{fr}</loc>',
        f'    <lastmod>{AUJ}</lastmod>',
        f'    <changefreq>{frequence(chemin)}</changefreq>',
        f'    <priority>{priorite(chemin)}</priority>',
    ]
    if a_traduction:
        en = url_de(en_chemin)
        lignes += [
            f'    <xhtml:link rel="alternate" hreflang="fr" href="{fr}"/>',
            f'    <xhtml:link rel="alternate" hreflang="en" href="{en}"/>',
            f'    <xhtml:link rel="alternate" hreflang="x-default" href="{fr}"/>',
        ]
    lignes.append('  </url>')
    return '\n'.join(lignes)


def bloc_en(chemin: str) -> str:
    """La page anglaise a sa propre entrée, avec la grappe hreflang miroir."""
    fr_chemin = chemin[len('en/'):]
    fr, en = url_de(fr_chemin), url_de(chemin)
    return '\n'.join([
        '  <url>',
        f'    <loc>{en}</loc>',
        f'    <lastmod>{AUJ}</lastmod>',
        f'    <changefreq>{frequence(fr_chemin)}</changefreq>',
        f'    <priority>{priorite(fr_chemin)}</priority>',
        f'    <xhtml:link rel="alternate" hreflang="fr" href="{fr}"/>',
        f'    <xhtml:link rel="alternate" hreflang="en" href="{en}"/>',
        f'    <xhtml:link rel="alternate" hreflang="x-default" href="{fr}"/>',
        '  </url>',
    ])


def main():
    pages = lister()
    blocs = []
    n_en = 0
    for p in pages:
        blocs.append(bloc(p))
        if (RACINE / f'en/{p}').exists():
            blocs.append(bloc_en(f'en/{p}'))
            n_en += 1

    sortie = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + '\n'.join(blocs)
        + '\n</urlset>\n'
    )
    (RACINE / 'sitemap.xml').write_text(sortie, encoding='utf-8')

    n_articles = sum(1 for p in pages if p.startswith('blog/'))
    print(f'  sitemap.xml : {len(pages) + n_en} URLs')
    print(f'    {len(pages) - n_articles} pages FR · {n_articles} articles · {n_en} pages EN')


if __name__ == '__main__':
    main()
