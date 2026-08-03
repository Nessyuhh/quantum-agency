/* ============================================================================
   Sélecteur de langue — deux liens, rien de plus.
   ----------------------------------------------------------------------------
   REMPLACE i18n.js ET SON DICTIONNAIRE DE 229 Ko.

   La traduction était refaite dans chaque navigateur, à chaque visite, à partir
   d'un dictionnaire de 1 721 entrées. Deux conséquences :
     · 229 Ko téléchargés et parcourus avant que le texte anglais apparaisse
     · une seule URL pour les deux langues, donc Google n'indexait que le
       français : tout le travail de traduction était invisible

   Les pages anglaises sont désormais générées une fois, dans /en/. Ce fichier
   ne fait plus qu'une chose : proposer l'autre version, par un vrai lien. Un
   moteur de recherche le suit, un lecteur d'écran l'annonce, et l'utilisateur
   peut le mettre en favori.
   ========================================================================== */

(function () {
  'use strict';

  var chemin = location.pathname;
  var enAnglais = /^\/en(\/|$)/.test(chemin);

  /* Page jumelle : /a-propos.html ↔ /en/a-propos.html */
  var jumelle = enAnglais
    ? chemin.replace(/^\/en(\/|$)/, '/')
    : '/en' + (chemin === '/' ? '/' : chemin);
  if (jumelle === '') jumelle = '/';

  var actuelle = enAnglais ? 'EN' : 'FR';
  var autre = enAnglais ? 'FR' : 'EN';
  var libelle = enAnglais ? 'Voir cette page en français' : 'View this page in English';

  var css = document.createElement('style');
  css.textContent =
    '.q-lang{position:fixed;top:14px;right:18px;z-index:600;display:flex;align-items:center;' +
    'gap:2px;font:700 11px/1 Inter,system-ui,sans-serif;letter-spacing:.12em}' +
    /* ⚠️ 44 px de haut minimum : c'est la cible tactile exigée par WCAG 2.2 et
       les recommandations Apple. Le repère visuel reste petit, la zone
       cliquable ne l'est pas. */
    '.q-lang a,.q-lang span{display:inline-flex;align-items:center;justify-content:center;' +
    'min-width:44px;min-height:44px;text-decoration:none}' +
    '.q-lang .q-actuelle{color:rgba(255,255,255,.9)}' +
    '.q-lang a{color:rgba(255,255,255,.72);transition:color .25s}' +
    '.q-lang a:hover,.q-lang a:focus-visible{color:rgba(255,255,255,.95)}' +
    '.q-lang .q-sep{min-width:0;opacity:.45;color:#fff}' +
    '@media(max-width:900px){.q-lang{top:auto;bottom:calc(env(safe-area-inset-bottom,0px) + 66px);' +
    'right:10px;background:rgba(8,4,22,.72);backdrop-filter:blur(12px);border-radius:99px;padding:0 4px}}';
  document.head.appendChild(css);

  var nav = document.createElement('nav');
  nav.className = 'q-lang';
  nav.setAttribute('aria-label', enAnglais ? 'Language' : 'Langue');
  nav.innerHTML =
    '<span class="q-actuelle" aria-current="true">' + actuelle + '</span>' +
    '<span class="q-sep" aria-hidden="true">|</span>' +
    '<a href="' + jumelle + '" hreflang="' + autre.toLowerCase() + '" ' +
    'lang="' + autre.toLowerCase() + '" title="' + libelle + '">' + autre + '</a>';
  document.body.appendChild(nav);
})();
