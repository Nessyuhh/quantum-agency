#!/usr/bin/env python3
"""Génère /llms-full.txt : le texte intégral des pages clés, en Markdown.

/llms.txt est le sommaire, celui-ci est le contenu. Un assistant qui veut
répondre à une question sur le cabinet lit un seul fichier propre au lieu de
reconstituer le texte à partir du HTML, et cite ce que la page dit vraiment.
Le fichier est aussi la base de connaissance du chatbot (formulaire/).

La page reste la source unique : relancer après toute modification de texte.

    python3 outils/llms-full.py             écrit le fichier
    python3 outils/llms-full.py --verifier  échoue s'il est périmé
"""
import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SITE = 'https://quantum-agency.fr'
PAGES = ['index.html', 'services.html', 'formations.html', 'cas-usage.html',
         'faq-ia.html', 'expertise-comptable.html', 'contact.html']


class Extracteur(HTMLParser):
    """Garde le texte de <main>, titres en Markdown, sans scripts ni SVG."""
    BLOCS = {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'dt', 'dd', 'td', 'th', 'blockquote', 'button', 'summary'}
    IGNORES = {'script', 'style', 'svg', 'form', 'noscript'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.dans_main = 0
        self.ignore = 0
        self.pile = []
        self.lignes = []
        self.courant = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'main':
            self.dans_main += 1
        if not self.dans_main:
            return
        if tag in self.IGNORES:
            self.ignore += 1
        elif tag in self.BLOCS:
            self.vider()
            self.pile.append(tag)
        elif tag == 'br':
            self.courant += ' '

    def handle_endtag(self, tag):
        if not self.dans_main:
            return
        if tag == 'main':
            self.vider()
            self.dans_main -= 1
        elif tag in self.IGNORES:
            self.ignore = max(0, self.ignore - 1)
        elif tag in self.BLOCS:
            self.vider(tag)
            if self.pile:
                self.pile.pop()

    def handle_data(self, data):
        if self.dans_main and not self.ignore:
            self.courant += data

    def vider(self, tag=None):
        texte = re.sub(r'\s+', ' ', self.courant).strip()
        self.courant = ''
        # Libellés de boutons et numéros d'ordre : du bruit pour un lecteur de texte.
        texte = re.sub(r'(\S[^→]{0,40}→\s*)+$', '', texte).strip()
        if not texte or re.fullmatch(r'[\d\s]+', texte):
            return
        tag = tag or (self.pile[-1] if self.pile else 'p')
        if tag in ('h1', 'h2', 'h3', 'h4'):
            niveau = {'h1': '##', 'h2': '###', 'h3': '####', 'h4': '####'}[tag]
            self.lignes.append(f'\n{niveau} {texte.rstrip("+").strip()}\n')
        elif tag == 'button':
            self.lignes.append(f'\n**{texte.rstrip("+").strip()}**\n')
        elif tag == 'li':
            self.lignes.append(f'- {texte}')
        else:
            self.lignes.append(texte + '\n')


def page(chemin):
    html = (RACINE / chemin).read_text(encoding='utf-8')
    titre = unescape(re.search(r'<title>(.*?)</title>', html, re.S).group(1))
    e = Extracteur()
    e.feed(html)
    corps = re.sub(r'\n{3,}', '\n\n', '\n'.join(e.lignes)).strip()
    url = SITE + ('/' if chemin == 'index.html' else '/' + chemin)
    return f'# {titre}\n\nSource : {url}\n\n{corps}\n'


def articles():
    lignes = []
    for f in sorted((RACINE / 'blog').glob('*.html')):
        html = f.read_text(encoding='utf-8')
        if 'noindex' in html[:3000]:
            continue
        t = unescape(re.search(r'<title>(.*?)</title>', html, re.S).group(1)).split(' | ')[0]
        d = re.search(r'<meta name="description" content="(.*?)"', html)
        lignes.append(f'- [{t}]({SITE}/blog/{f.name}) : {unescape(d.group(1)) if d else ""}')
    return '# Articles du blog\n\n' + '\n'.join(lignes) + '\n'


def generer():
    tete = ('# Quantum Consulting, texte intégral\n\n'
            '> Texte des pages principales de https://quantum-agency.fr, extrait des pages\n'
            '> publiées. Sommaire : https://quantum-agency.fr/llms.txt\n')
    return '\n\n'.join([tete] + [page(p) for p in PAGES] + [articles()])


def main():
    cible = RACINE / 'llms-full.txt'
    contenu = generer()
    if '--verifier' in sys.argv:
        if not cible.exists() or cible.read_text(encoding='utf-8') != contenu:
            print('llms-full.txt est périmé : python3 outils/llms-full.py')
            return 1
        print('llms-full.txt à jour')
        return 0
    cible.write_text(contenu, encoding='utf-8')
    print(f'llms-full.txt : {len(contenu) // 1024} Ko, {len(PAGES)} pages')
    return 0


if __name__ == '__main__':
    sys.exit(main())
