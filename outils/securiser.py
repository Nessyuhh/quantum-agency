#!/usr/bin/env python3
"""Durcit toutes les pages du site. Idempotent : se relance sans risque.

Ce que fait le script, page par page :

1. Retire tout gestionnaire d'évènement écrit dans le HTML (onclick,
   onload). assets/quantum.js les remplace par une délégation de clics.
   C'est la condition pour que la politique de sécurité du contenu interdise
   tout script en ligne, la parade la plus efficace contre l'injection de
   code.
2. Sort le script du filtre du blog dans assets/blog-filtre.js.
3. Pose en tête de page la politique de sécurité du contenu (CSP) et la
   politique de référent. GitHub Pages ne permet pas d'envoyer d'en-têtes :
   la balise meta est le seul moyen de les appliquer depuis le dépôt. Les
   en-têtes qu'une balise ne peut pas porter (HSTS, frame-ancestors) sont
   décrits dans outils/PROMPTS-EXTERNES.md, prompt 5, pour Cloudflare.
4. Ajoute noindex aux pages de travail qui n'en avaient pas.

Usage :
    python3 outils/securiser.py            applique
    python3 outils/securiser.py --verifier échoue s'il reste quelque chose
"""
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# Pages de travail : jamais liées, jamais indexées. On n'y pose pas de CSP,
# certaines chargent encore leurs polices chez Google, mais on s'assure
# qu'elles portent noindex.
TRAVAIL_DOSSIERS = ('archives', 'apercus', 'outils', '_animation-ref', 'charte', 'formulaire')
TRAVAIL_PAGES = {
    'business-card.html', 'email-signature.html', 'intro-preview.html',
    'quantum-logos.html', 'quantum-logos-final.html', 'quantum-logo-animation.html',
    'animation-atom.html',
}

GA = 'https://www.googletagmanager.com'
API = 'https://api.quantum-agency.fr'
CF_STATS = 'https://static.cloudflareinsights.com'
CSP = '; '.join([
    "default-src 'self'",
    # Cloudflare injecte sa balise de statistiques (Web Analytics, sans cookie)
    # dans les pages : elle est autorisée pour que ces mesures continuent.
    f"script-src 'self' {GA} {CF_STATS}",
    # Les styles en ligne restent permis : chaque page porte son bloc <style>
    # et le script pose des variables CSS. Un style ne peut pas exécuter de
    # code, le risque n'a rien de comparable avec celui d'un script.
    "style-src 'self' 'unsafe-inline'",
    f"img-src 'self' data: {GA} https://*.google-analytics.com",
    "font-src 'self'",
    f"connect-src 'self' {API} https://*.google-analytics.com https://*.analytics.google.com {GA} https://cloudflareinsights.com",
    "manifest-src 'self'",
    "frame-src 'none'",
    "worker-src 'none'",
    "object-src 'none'",
    "base-uri 'self'",
    f"form-action 'self' {API}",
    'upgrade-insecure-requests',
])
META_CSP = f'<meta http-equiv="Content-Security-Policy" content="{CSP}">'
META_REF = '<meta name="referrer" content="strict-origin-when-cross-origin">'

FILTRE_JS = RACINE / 'assets' / 'blog-filtre.js'
FILTRE_BALISE = '<script src="/assets/blog-filtre.js" defer></script>'


def travail(chemin: Path) -> bool:
    rel = chemin.relative_to(RACINE)
    return rel.parts[0] in TRAVAIL_DOSSIERS or (len(rel.parts) == 1 and rel.name in TRAVAIL_PAGES)


def nettoyer_gestionnaires(html: str) -> str:
    # Bouton de retour en haut des articles : masqué en CSS depuis la refonte,
    # la barre de navigation porte maintenant ce rôle.
    html = re.sub(r'<a href="#" id="back-top"[^>]*>.*?</a>\s*', '', html, flags=re.S)
    # Faux liens d'articles anciens : un lien qui ne mène nulle part est une
    # impasse pour le visiteur et un signal de mauvaise qualité pour Google.
    html = re.sub(r'<a href="#" onclick="return false;">(.*?)</a>', r'\1', html, flags=re.S)
    html = html.replace(' onclick="toggleFaq(this)"', '')
    return html


def sortir_filtre(html: str) -> str:
    m = re.search(r'<script>\s*/\* Filtre par thème\..*?</script>', html, flags=re.S)
    if not m:
        return html
    corps = m.group(0)[len('<script>'):-len('</script>')].strip('\n')
    if not FILTRE_JS.exists():
        FILTRE_JS.write_text(corps + '\n', encoding='utf-8')
    return html.replace(m.group(0), FILTRE_BALISE)


def poser_entetes(html: str) -> str:
    html = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>\n?', '', html)
    html = re.sub(r'<meta name="referrer"[^>]*>\n?', '', html)
    return re.sub(r'(<meta charset="[^"]*">\n?)', r'\1' + META_CSP + '\n' + META_REF + '\n', html, count=1, flags=re.I)


def poser_noindex(html: str) -> str:
    if re.search(r'<meta name="robots"[^>]*noindex', html):
        return html
    html = re.sub(r'<meta name="robots"[^>]*>\n?', '', html)
    return re.sub(r'(<meta charset="[^"]*">\n?)', r'\1<meta name="robots" content="noindex, nofollow">\n', html, count=1, flags=re.I)


def defauts(chemin: Path, html: str) -> list:
    d = []
    if travail(chemin):
        if not re.search(r'<meta name="robots"[^>]*noindex', html):
            d.append('page de travail sans noindex')
        return d
    if re.search(r'\son[a-z]+="', html):
        d.append('gestionnaire en ligne')
    for m in re.finditer(r'<script(\s[^>]*)?>', html):
        attrs = m.group(1) or ''
        if 'src=' not in attrs and 'application/ld+json' not in attrs:
            d.append('script en ligne')
    if META_CSP not in html:
        d.append('CSP absente ou périmée')
    if META_REF not in html:
        d.append('politique de référent absente')
    if re.search(r'''(src|href)="https?://(?!quantum-agency\.fr)[^"]+\.(js|css)["?]''', html):
        d.append('script ou feuille de style tiers')
    return d


def main() -> int:
    verifier = '--verifier' in sys.argv
    pages = sorted(p for p in RACINE.rglob('*.html') if '.git' not in p.parts and 'node_modules' not in p.parts)
    problemes = 0
    modifiees = 0
    for p in pages:
        html = p.read_text(encoding='utf-8')
        if not verifier:
            neuf = poser_noindex(html) if travail(p) else poser_entetes(sortir_filtre(nettoyer_gestionnaires(html)))
            if neuf != html:
                p.write_text(neuf, encoding='utf-8')
                modifiees += 1
            html = neuf
        for d in defauts(p, html):
            print(f'{p.relative_to(RACINE)} : {d}')
            problemes += 1
    if verifier:
        print(f'{len(pages)} pages contrôlées, {problemes} défaut(s).')
    else:
        print(f'{len(pages)} pages, {modifiees} modifiée(s), {problemes} défaut(s) restant(s).')
    return 1 if problemes else 0


if __name__ == '__main__':
    sys.exit(main())
