#!/usr/bin/env python3
"""Construit la base de connaissance de l'assistant du site.

L'assistant tourne entièrement dans le navigateur du visiteur : aucun
serveur, aucun modèle payant, aucune donnée qui quitte la page. Il cherche la
meilleure réponse parmi ce que le site publie déjà :

- les questions fréquentes, lues dans les blocs FAQPage (FAQ, page métier,
  et plus de 480 questions des articles du blog) ;
- les sections des pages de services, formations, exemples et contact.

La page reste la source unique : relancer après toute modification de texte.

    python3 outils/chat-index.py             écrit assets/chat-index-fr.json et -en.json
    python3 outils/chat-index.py --verifier  échoue s'ils sont périmés
"""
import json
import re
import sys
from html import unescape
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SITE = 'https://quantum-agency.fr'
MAX_REPONSE = 900

PAGES = {
    'fr': {
        'sections': ['services.html', 'formations.html', 'cas-usage.html', 'expertise-comptable.html', 'contact.html'],
        'faq': ['faq-ia.html', 'expertise-comptable.html'] + sorted(p.relative_to(RACINE).as_posix() for p in (RACINE / 'blog').glob('*.html')),
    },
    'en': {
        'sections': ['en/services.html', 'en/formations.html', 'en/cas-usage.html', 'en/contact.html'],
        'faq': ['en/faq-ia.html'],
    },
}


def texte(html):
    html = re.sub(r'<(script|style|svg)[^>]*>.*?</\1>', ' ', html, flags=re.S)
    html = re.sub(r'<h3[^>]*>(.*?)</h3>', r' \1 : ', html, flags=re.S)
    html = re.sub(r'<li[^>]*>', ' ; ', html)
    html = re.sub(r'<[^>]+>', ' ', html)
    t = re.sub(r'\s+', ' ', unescape(html)).strip()
    return re.sub(r'\s+([,.;:])', r'\1', t).replace(': ;', ':').strip(' ;')


def couper(t):
    if len(t) <= MAX_REPONSE:
        return t
    t = t[:MAX_REPONSE]
    fin = max(t.rfind('. '), t.rfind('.'))
    return t[:fin + 1] if fin > MAX_REPONSE // 2 else t.rstrip() + '…'


def adresse(chemin, ancre=''):
    base = SITE + '/' + ('' if chemin == 'index.html' else chemin)
    return base + ('#' + ancre if ancre else '')


def titre_page(html):
    return unescape(re.search(r'<title>(.*?)</title>', html, re.S).group(1)).split(' | ')[0].strip()


def indexable(html):
    return not re.search(r'<meta name="robots"[^>]*noindex', html)


def faqs(chemin):
    html = (RACINE / chemin).read_text(encoding='utf-8')
    if not indexable(html):
        return []
    sortie = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            d = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        for it in d.get('@graph', [d]) if isinstance(d, dict) else d:
            if it.get('@type') != 'FAQPage':
                continue
            for q in it.get('mainEntity', []):
                reponse = texte(q.get('acceptedAnswer', {}).get('text', ''))
                if q.get('name') and reponse:
                    sortie.append({'q': unescape(q['name']).strip(), 'r': couper(reponse), 'u': adresse(chemin), 't': titre_page(html)})
    return sortie


def sections(chemin):
    html = (RACINE / chemin).read_text(encoding='utf-8')
    main = re.search(r'<main[^>]*>(.*?)</main>', html, re.S).group(1)
    main = re.sub(r'<form.*?</form>', ' ', main, flags=re.S)
    titre = titre_page(html)
    morceaux = re.split(r'(?=<h2[\s>])', main)
    sortie = []
    ancre = ''
    for i, bloc in enumerate(morceaux):
        ids = re.findall(r'<section[^>]*\bid="([^"]+)"', morceaux[i - 1] if i else '') + re.findall(r'<section[^>]*\bid="([^"]+)"', bloc)
        m = re.match(r'<h2[^>]*>(.*?)</h2>(.*)', bloc, re.S)
        if not m:
            continue
        precedent = re.findall(r'<section[^>]*\bid="([^"]+)"', morceaux[i - 1]) if i else []
        if precedent:
            ancre = precedent[-1]
        q = texte(m.group(1))
        r = texte(m.group(2))
        if len(r) < 40:
            continue
        # Le titre de la page complète celui de la section : « Découvrir » seul
        # ne dit pas qu'il s'agit d'une formation.
        sortie.append({'q': f'{q} ({titre})', 'r': couper(r), 'u': adresse(chemin, ancre), 't': titre})
    return sortie


def construire(langue):
    conf = PAGES[langue]
    entrees = []
    for p in conf['sections']:
        entrees += sections(p)
    for p in conf['faq']:
        entrees += faqs(p)
    vues = set()
    uniques = []
    for e in entrees:
        cle = e['q'].lower()
        if cle not in vues:
            vues.add(cle)
            uniques.append(e)
    return json.dumps(uniques, ensure_ascii=False, separators=(',', ':')) + '\n'


def main():
    verifier = '--verifier' in sys.argv
    perime = False
    for langue in PAGES:
        cible = RACINE / 'assets' / f'chat-index-{langue}.json'
        contenu = construire(langue)
        if verifier:
            if not cible.exists() or cible.read_text(encoding='utf-8') != contenu:
                print(f'{cible.name} est périmé : python3 outils/chat-index.py')
                perime = True
        else:
            cible.write_text(contenu, encoding='utf-8')
            print(f'{cible.name} : {len(json.loads(contenu))} entrées, {len(contenu.encode()) // 1024} Ko')
    if verifier and not perime:
        print('base de connaissance de l’assistant à jour')
    return 1 if perime else 0


if __name__ == '__main__':
    sys.exit(main())
