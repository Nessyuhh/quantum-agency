#!/usr/bin/env python3
"""Passe l'index du blog et les articles sur la charte du site.

Pour chaque page :
- les <style> et polices de l'ancienne charte sont retirés, remplacés par
  quantum.css + article.css et les polices du site ;
- la navigation, la barre du bas et le pied de page viennent des blocs
  @nav / @mobnav / @footer de index.html (ou en/index.html) ;
- les noms de modèles obsolètes sont mis à jour et les tirets longs remplacés.

Le contenu des articles n'est pas réécrit. Idempotent : relançable sans effet.

Usage : python3 outils/blog-recharter.py
"""
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
FONTS = ('https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@500;700;800'
         '&family=Archivo:wght@400;500&family=Space+Mono:wght@400;700&display=swap')
VERSION = 'v=4'

MODELES = [
    (r'Claude 3\.7 Sonnet', 'Claude Sonnet 5'),
    (r'Claude 3\.5 Sonnet', 'Claude Sonnet 5'),
    (r'Claude 3\.5', 'Claude Sonnet 5'),
    (r'Claude 3(?![\.\d])', 'Claude Sonnet 5'),
    (r'Claude 2(?![\.\d])', 'Claude Sonnet 5'),
    (r'GPT-4o(?:[- ]mini)?', 'GPT-6'),
    (r'GPT-4(?![o\d])', 'GPT-6'),
    (r'Gemini 1\.5 (?:Pro|Flash)', 'Gemini 3'),
    (r'Llama 3(?:\.\d)?(?: \d+B)?', 'Llama 4'),
    (r'Mistral Large(?! \d)', 'Mistral Large 3'),
    (r'Mistral Small(?! \d)', 'Mistral Small 4'),
]

SPRITE = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <linearGradient id="qGrad" gradientUnits="userSpaceOnUse" x1="5" y1="5" x2="57" y2="57">
      <stop offset="0%" stop-color="#ddd6fe"/><stop offset="50%" stop-color="#a855f7"/><stop offset="100%" stop-color="#22d3ee"/>
    </linearGradient>
    <symbol id="qMark" viewBox="0 0 64 64">
      <path d="M 43.68 51.78 A 23.04 23.04 0 1 1 51.78 43.68" stroke="url(#qGrad)" stroke-width="5.5" stroke-linecap="round" fill="none"/>
      <line x1="38.4" y1="39.68" x2="56.32" y2="56.32" stroke="url(#qGrad)" stroke-width="5.5" stroke-linecap="round"/>
    </symbol>
  </defs>
</svg>'''


def bloc(html, nom):
    m = re.search(r'<!-- @%s -->.*?<!-- @/%s -->' % (nom, nom), html, re.S)
    if not m:
        raise SystemExit('bloc @%s introuvable dans la source' % nom)
    return m.group(0)


def tirets(s):
    """Tiret long : incise appariée → parenthèses, sinon virgule."""
    s = re.sub(r' — ([^—<>]{2,120}?) — ', r' (\1) ', s)
    s = s.replace(' — ', ', ').replace('— ', '').replace(' —', ',').replace('—', ', ')
    return s


def recharter(chemin, blocs):
    html = chemin.read_text(encoding='utf-8')
    orig = html

    # 1. Tête : styles et polices de l'ancienne charte
    html = re.sub(r'\n?<style>.*?</style>', '', html, flags=re.S)
    html = re.sub(r'\n?<link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]*Inter[^>]*>', '', html)
    html = re.sub(r'\n?<noscript><link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]*Inter[^>]*></noscript>', '', html)
    html = re.sub(r'\n?<link rel="stylesheet" href="/assets/(?:commun|heros)\.css">', '', html)
    html = re.sub(r'\n?<noscript>\s*</noscript>', '', html)
    html = re.sub(r'\n?<!-- correctif:mise-en-page -->', '', html)
    html = re.sub(r'\n?<!-- /?blog:style -->', '', html)
    html = re.sub(r'<meta name="theme-color" content="[^"]*">', '<meta name="theme-color" content="#F6F6F3">', html)
    ancre = '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    morceaux = [
        ('color-scheme', '<meta name="color-scheme" content="light">'),
        ('fonts.googleapis.com/css2?family=Big+Shoulders', '<link rel="stylesheet" href="%s" media="print" onload="this.media=\'all\'">\n<noscript><link rel="stylesheet" href="%s"></noscript>' % (FONTS, FONTS)),
        ('/assets/quantum.css', '<link rel="stylesheet" href="/assets/quantum.css?%s">' % VERSION),
        ('/assets/article.css', '<link rel="stylesheet" href="/assets/article.css?%s">' % VERSION),
    ]
    for cle, ligne in reversed(morceaux):
        if cle not in html:
            html = html.replace(ancre, ancre + '\n' + ligne, 1)

    # 2. Corps : navigation, barre du bas, pied de page
    # Entre la barre du haut et celle du bas, l'index du blog intercale un menu
    # mobile dépliant : on remplace l'ensemble d'un bloc.
    html = re.sub(r'<nav aria-label="Navigation principale">.*?<nav id="bb"[^>]*>.*?</nav>', lambda m: blocs['nav'], html, count=1, flags=re.S)
    html = re.sub(r'<!-- @nav -->.*?<!-- @/nav -->', lambda m: blocs['nav'], html, count=1, flags=re.S)
    html = re.sub(r'<footer role="contentinfo">.*?</footer>', lambda m: blocs['mobnav'] + '\n\n' + blocs['footer'], html, count=1, flags=re.S)
    html = re.sub(r'<!-- @mobnav -->.*?<!-- @/mobnav -->', lambda m: blocs['mobnav'], html, count=1, flags=re.S)
    html = re.sub(r'<!-- @footer -->.*?<!-- @/footer -->', lambda m: blocs['footer'], html, count=1, flags=re.S)
    if 'id="qMark"' not in html:
        html = html.replace('<div id="progress-bar" aria-hidden="true"></div>',
                            '<div id="progress-bar" aria-hidden="true"></div>\n' + SPRITE, 1)
    html = re.sub(r'<div id="back-top"[^>]*>.*?</div>\s*', '', html, flags=re.S)
    html = re.sub(r'<script>\s*var bt=document\.getElementById\(\'back-top\'\);.*?</script>\s*', '', html, flags=re.S)
    html = re.sub(r'<script>\s*function toggleMobMenu.*?</script>\s*', '', html, flags=re.S)
    html = re.sub(r'<script src="/assets/replier\.js" defer></script>\n?', '', html)
    if '/assets/quantum.js' not in html:
        html = html.replace('<script src="/lang-switch.js" defer></script>',
                            '<script src="/assets/quantum.js?%s" defer></script>\n<script src="/lang-switch.js?%s" defer></script>' % (VERSION, VERSION), 1)
    html = html.replace('href="/index.html"', 'href="/"')

    # 3. Texte : modèles et tirets
    for motif, rempl in MODELES:
        html = re.sub(motif, rempl, html)
    html = tirets(html)

    if html != orig:
        chemin.write_text(html, encoding='utf-8')
        return True
    return False


def main():
    src = (RACINE / 'index.html').read_text(encoding='utf-8')
    blocs = {b: bloc(src, b) for b in ('nav', 'mobnav', 'footer')}
    # Dans le blog, l'onglet actif est Blog.
    blocs['nav'] = blocs['nav'].replace('<li><a href="/blog.html">Blog</a></li>', '<li><a href="/blog.html" aria-current="page">Blog</a></li>')

    pages = [RACINE / 'blog.html'] + sorted((RACINE / 'blog').glob('*.html'))
    n = sum(recharter(p, blocs) for p in pages)
    print('%d page(s) rechartée(s) sur %d' % (n, len(pages)))


if __name__ == '__main__':
    main()
