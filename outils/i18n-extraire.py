#!/usr/bin/env python3
"""
Extrait toutes les chaînes traduisibles du site.

POURQUOI CE FICHIER EXISTE
Le dictionnaire de i18n.js est indexé sur le texte français EXACT. Il en
comptait 278 entrées pour un site qui en demande plus de mille : trois quarts du
contenu restaient en français quand on cliquait sur EN.

Un dictionnaire complet ne suffit pas — il faut qu'il le RESTE. D'où un
extracteur rejouable : à chaque modification de texte, on relance et on voit
immédiatement ce qui manque.

CE QUI EST EXTRAIT
  · les nœuds de texte visibles
  · placeholder, aria-label, alt, title
  · <title> et <meta name="description">
Ce qui est ignoré : script, style, noscript, et tout ce qui n'a aucune lettre.
"""

import html
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

RACINE = pathlib.Path(__file__).resolve().parent.parent

# ⚠️ Un motif naïf `'([^']+)'` perd toute clé contenant une apostrophe échappée
# — « Initiation à l\'IA » et 363 autres. Il faut autoriser \. à traverser
# l'échappement, PUIS déséchapper pour comparer au texte réel de la page.
MOTIF_CLE = r"""^[ \t]*(?:"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)'|`([^`]*)`)[ \t]*:"""


def desechappe(s):
    return s.replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')


# Pages de travail interne, hors site public.
EXCLUES = {
    'quantum-logos.html', 'quantum-logos-final.html', 'email-signature.html',
    'business-card.html', 'intro-preview.html', 'animation-atom.html',
    'quantum-logo-animation.html', 'sonde.html',
}

ATTRS = ('placeholder', 'aria-label', 'alt', 'title', 'content')
IGNORE = {'script', 'style', 'noscript'}


class Extracteur(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pile = []
        self.chaines = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag not in ('meta', 'link', 'br', 'img', 'input', 'hr'):
            self.pile.append(tag)
        # <meta name="description"> uniquement : les autres content= sont techniques
        if tag == 'meta':
            if d.get('name') in ('description', 'twitter:title',
                                 'twitter:description') or d.get('property') in (
                    'og:title', 'og:description'):
                self._ajoute(d.get('content', ''))
            return
        for a in ATTRS:
            if a == 'content':
                continue
            if a in d:
                self._ajoute(d[a])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if self.pile and tag in self.pile:
            while self.pile and self.pile.pop() != tag:
                pass

    def handle_data(self, texte):
        if any(t in IGNORE for t in self.pile):
            return
        self._ajoute(texte)

    def _ajoute(self, brut):
        s = re.sub(r'\s+', ' ', html.unescape(brut or '')).strip()
        if len(s) < 2:
            return
        # Il faut au moins une lettre : on ne traduit ni « 24/7 » ni « → ».
        if not re.search(r'[a-zà-ÿ]', s, re.I):
            return
        self.chaines.append(s)


def pages():
    """Pages du site public.

    ⚠️ La variante de `variantes/` est incluse : elle est destinée à devenir
    l'accueil, et 82 % de son contenu était absent du dictionnaire. L'intégrer
    maintenant évite de casser la couverture le jour de la bascule.
    """
    p = [x for x in RACINE.glob('*.html') if x.name not in EXCLUES]
    p += [x for x in RACINE.glob('variantes/*/*.html') if x.name not in EXCLUES]
    return sorted(p, key=lambda x: str(x))


def extraire():
    par_page, toutes = {}, {}
    for p in pages():
        e = Extracteur()
        e.feed(p.read_text(encoding='utf-8'))
        cle = p.name if p.parent == RACINE else f'{p.parent.name}/{p.name}'
        par_page[cle] = e.chaines
        for s in e.chaines:
            toutes.setdefault(s, []).append(cle)
    return par_page, toutes


def dictionnaire_actuel():
    """Clés déjà présentes dans i18n.js."""
    f = RACINE / 'i18n.js'
    if not f.exists():
        return set()
    s = f.read_text(encoding='utf-8')
    return {
        desechappe(next(g for g in m.groups() if g is not None)).strip()
        for m in re.finditer(MOTIF_CLE, s, re.M)
    }


if __name__ == '__main__':
    par_page, toutes = extraire()
    connues = dictionnaire_actuel()
    manquantes = {s: v for s, v in toutes.items() if s not in connues}

    print(f'  {len(par_page)} pages · {len(toutes)} chaînes uniques')
    print(f'  déjà traduites : {len(toutes) - len(manquantes)}')
    print(f'  MANQUANTES     : {len(manquantes)}')
    print()
    print(f"  {'page':32} {'total':>6} {'manque':>7} {'couverture':>11}")
    for nom, ch in sorted(par_page.items()):
        u = set(ch)
        m = len(u - connues)
        taux = f'{round((len(u)-m)/len(u)*100)}%' if u else '—'
        print(f'  {nom:32} {len(u):>6} {m:>7} {taux:>11}')

    sortie = RACINE / 'outils' / 'i18n-manquantes.json'
    sortie.write_text(json.dumps(
        sorted(manquantes.keys(), key=lambda s: (-len(toutes[s]), s)),
        ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\n  → {sortie.relative_to(RACINE)}')
