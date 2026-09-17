#!/usr/bin/env python3
"""Synchronise les blocs partagés de la nouvelle charte entre les pages.

Source de vérité : index.html (FR) et en/index.html (EN). Les blocs délimités
par <!-- @nav --> … <!-- @/nav -->, @mobnav et @footer y sont copiés dans
chaque page qui porte les mêmes marqueurs. L'onglet de la page courante reçoit
aria-current="page" (et la classe active dans la barre du bas).

Usage : python3 outils/charte-sync.py
"""
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
BLOCS = ('nav', 'mobnav', 'footer')

PAGES = {
    'index.html': ['services.html', 'formations.html', 'cas-usage.html', 'faq-ia.html', 'contact.html', 'blog.html'],
    'en/index.html': ['en/services.html', 'en/formations.html', 'en/cas-usage.html', 'en/faq-ia.html', 'en/contact.html', 'en/blog.html'],
}


def bloc(html, nom):
    m = re.search(r'<!-- @%s -->.*?<!-- @/%s -->' % (nom, nom), html, re.S)
    return m.group(0) if m else None


def marquer_actif(html, chemin):
    """aria-current sur le lien dont le href correspond à la page."""
    href = '/' + chemin
    html = html.replace('aria-current="page"', '')
    html = re.sub(r'class="mob-tab-item active', 'class="mob-tab-item', html)
    html = re.sub(r'<a href="%s"( class="mob-tab-item[^"]*")' % re.escape(href),
                  lambda m: '<a href="%s" aria-current="page"%s' % (href, m.group(1).replace('mob-tab-item', 'mob-tab-item active', 1)), html)
    # Uniquement dans la liste de navigation : le pied de page reprend les
    # mêmes adresses et ne doit pas être marqué.
    html = re.sub(r'<ul class="nav-links">.*?</ul>',
                  lambda m: m.group(0).replace('<li><a href="%s">' % href, '<li><a href="%s" aria-current="page">' % href),
                  html, count=1, flags=re.S)
    return html


def main():
    modifies = 0
    for source, cibles in PAGES.items():
        src = (RACINE / source).read_text(encoding='utf-8')
        blocs = {b: bloc(src, b) for b in BLOCS}
        manquants = [b for b, v in blocs.items() if v is None]
        if manquants:
            print('source ignorée (pas encore sur la charte) :', source, manquants)
            continue
        for cible in cibles:
            f = RACINE / cible
            if not f.exists():
                continue
            html = f.read_text(encoding='utf-8')
            if any(bloc(html, b) is None for b in BLOCS):
                print('ignoré (pas encore sur la charte) :', cible)
                continue
            nouveau = html
            for b, contenu in blocs.items():
                nouveau = re.sub(r'<!-- @%s -->.*?<!-- @/%s -->' % (b, b), lambda m: contenu, nouveau, flags=re.S)
            nouveau = marquer_actif(nouveau, cible)
            if nouveau != html:
                f.write_text(nouveau, encoding='utf-8')
                modifies += 1
                print('synchronisé :', cible)
    print('%d page(s) mise(s) à jour' % modifies)


if __name__ == '__main__':
    main()
