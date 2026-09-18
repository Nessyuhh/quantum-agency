/* ============================================================================
   Consentement et mesure d'audience (Google Analytics 4, Consent Mode v2).
   ----------------------------------------------------------------------------
   Un seul fichier, branché sur toutes les pages avant quantum.js. Il :
     1. déclare à Google que rien n'est autorisé tant que le visiteur n'a pas
        répondu (Consent Mode v2, quatre signaux refusés par défaut) ;
     2. affiche une bannière discrète, en bas, qui ne bloque pas la lecture,
        avec deux boutons de même poids : accepter ou refuser ;
     3. mémorise la réponse six mois dans le navigateur, sans cookie ;
     4. charge la balise GA4 et lui transmet la réponse.

   MODE_AVANCE : true  = la balise est chargée avant la réponse, en mode
                        refusé. Elle ne dépose alors aucun cookie et n'envoie
                        que des signaux anonymes, à partir desquels Google
                        estime la fréquentation manquante (Consent Mode avancé,
                        recommandé par Google).
                 false = rien n'est chargé avant un accord explicite (mode
                        basique). Lecture la plus stricte du droit français :
                        une ligne à changer si nous préférons cette prudence.

   Pour envoyer un événement depuis le reste du site :
     window.quantumSuivre('generate_lead', { form: 'audit' });
   Il ne part que si la mesure est autorisée, jamais avant.

   La balise elle-même est chargée après le chargement de la page, pendant un
   temps de repos du navigateur : voir quandLeNavigateurSouffle plus bas.
   ========================================================================== */
(function () {
  'use strict';

  var ID = 'G-2CZCESXSV6';
  var MODE_AVANCE = true;
  var CLE = 'quantum-consentement';
  var DUREE = 182 * 86400000;           /* six mois, le maximum recommandé par la CNIL */

  /* Formulation reprise de la bannière de Tesla, sans la phrase sur les
     transferts hors du pays ni la personnalisation des publicités, que nous
     ne faisons pas. Un titre, une phrase, un lien, deux boutons de même poids.
     Le détail (quoi, pourquoi, combien de temps) est sur la page de
     confidentialité. */
  var anglais = document.documentElement.lang === 'en';
  var t = anglais ? {
    titre: 'Help us improve our website with cookies',
    texte: 'We use cookies to analyze website performance and improve your experience.',
    avantLien: 'See ', lien: 'cookie settings', apresLien: ' to learn more.',
    href: '/en/confidentialite.html',
    refuser: 'Reject', accepter: 'Accept', fermer: 'Close'
  } : {
    titre: 'Aidez-nous à améliorer notre site grâce aux cookies',
    texte: 'Nous utilisons des cookies pour analyser les performances du site et améliorer votre expérience.',
    avantLien: 'Consultez les ', lien: 'paramètres relatifs aux cookies', apresLien: ' pour en savoir plus.',
    href: '/confidentialite.html',
    refuser: 'Rejeter', accepter: 'Accepter', fermer: 'Fermer'
  };

  /* ── Consent Mode : tout refusé tant que le visiteur n'a rien dit ── */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;
  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    wait_for_update: 500
  });
  gtag('set', 'ads_data_redaction', true);
  gtag('set', 'url_passthrough', false);

  /* Le script de mesure pèse 158 Ko et bloque le fil principal 270 ms quand il
     part avec le reste : il faisait à lui seul tomber toutes les pages de 100 à
     92 en performance mobile. Il attend donc la fin du chargement, puis un
     temps de repos du navigateur. Les commandes, elles, partent tout de suite :
     dataLayer les garde en file et la balise les traite à son arrivée, donc
     rien n'est perdu, la vue est seulement datée d'une seconde plus tard. */
  function quandLeNavigateurSouffle(faire) {
    var lancer = function () {
      (window.requestIdleCallback || function (f) { setTimeout(f, 200); })(faire, { timeout: 3000 });
    };
    if (document.readyState === 'complete') lancer();
    else window.addEventListener('load', lancer, { once: true });
  }

  var chargee = false;
  function chargerBalise() {
    if (chargee) return;
    chargee = true;
    gtag('js', new Date());
    gtag('config', ID, {
      anonymize_ip: true,
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    });
    quandLeNavigateurSouffle(function () {
      var s = document.createElement('script');
      s.async = true;
      s.src = 'https://www.googletagmanager.com/gtag/js?id=' + ID;
      document.head.appendChild(s);
    });
  }

  window.quantumSuivre = function (nom, params) {
    if (chargee) gtag('event', nom, params || {});
  };

  /* ── Mémoire du choix : localStorage, jamais un cookie ── */
  function lire() {
    try {
      var v = JSON.parse(localStorage.getItem(CLE));
      if (v && typeof v.analytics === 'boolean' && Date.now() - v.at < DUREE) return v;
    } catch (e) { /* stockage refusé ou valeur corrompue : on redemande */ }
    return null;
  }
  function memoriser(analytics) {
    try { localStorage.setItem(CLE, JSON.stringify({ analytics: analytics, at: Date.now() })); } catch (e) { /* sans stockage, la bannière reviendra */ }
  }
  function appliquer(analytics) {
    if (analytics) {
      gtag('consent', 'update', { analytics_storage: 'granted' });
      chargerBalise();
    } else {
      gtag('consent', 'update', { analytics_storage: 'denied' });
      if (MODE_AVANCE) chargerBalise();
    }
  }

  /* ── Bannière ── */
  var style = document.createElement('style');
  style.textContent =
    '.consent{position:fixed;left:16px;right:16px;bottom:16px;z-index:9600;max-width:440px;background:var(--bg,#F6F6F3);color:var(--ink,#111318);border:1px solid var(--line-strong,rgba(17,19,24,.45));padding:20px 22px;font-family:var(--text,system-ui,sans-serif);box-shadow:0 18px 40px rgba(17,19,24,.14);transform:translateY(12px);opacity:0;transition:transform .35s var(--ease,ease),opacity .35s var(--ease,ease)}' +
    '.consent.ouverte{transform:none;opacity:1}' +
    '.consent p{margin:0;font-size:.92rem;line-height:1.5}' +
    '.consent .consent-titre{font-weight:600;margin-bottom:4px}' +
    '.consent p a{color:inherit;text-decoration:underline;text-underline-offset:3px}' +
    '.consent-actions{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap}' +
    '.consent-actions .btn{flex:1 1 120px;padding:.75rem 1rem}' +
    '@media(max-width:768px){.consent{bottom:84px;max-width:none}}' +
    '@media(prefers-reduced-motion:reduce){.consent{transition:none}}';
  document.head.appendChild(style);

  var boite = null;
  function ouvrir() {
    if (boite) return;
    boite = document.createElement('div');
    boite.className = 'consent';
    boite.setAttribute('role', 'dialog');
    boite.setAttribute('aria-labelledby', 'consent-titre');
    boite.innerHTML =
      '<p class="consent-titre" id="consent-titre">' + t.titre + '</p>' +
      '<p>' + t.texte + ' ' + t.avantLien + '<a href="' + t.href + '">' + t.lien + '</a>' + t.apresLien + '</p>' +
      '<div class="consent-actions">' +
        '<button type="button" class="btn" data-choix="oui">' + t.accepter + '</button>' +
        '<button type="button" class="btn" data-choix="non">' + t.refuser + '</button>' +
      '</div>';
    boite.addEventListener('click', function (e) {
      var b = e.target.closest('[data-choix]');
      if (!b) return;
      var oui = b.getAttribute('data-choix') === 'oui';
      memoriser(oui);
      appliquer(oui);
      fermer();
    });
    document.body.appendChild(boite);
    /* Reflow forcé plutôt que requestAnimationFrame : la transition part même
       dans un onglet ouvert en arrière-plan, où rAF ne tourne pas. */
    void boite.offsetWidth;
    boite.classList.add('ouverte');
  }
  function fermer() {
    if (!boite) return;
    var b = boite;
    boite = null;
    b.classList.remove('ouverte');
    setTimeout(function () { if (b.parentNode) b.remove(); }, 380);
  }

  /* Le pied de page propose de revenir sur son choix : [data-consent-open]. */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-consent-open]');
    if (!a) return;
    e.preventDefault();
    ouvrir();
  });
  window.quantumConsent = { ouvrir: ouvrir, etat: lire };

  /* ── Démarrage ── */
  var choix = lire();
  if (choix) {
    appliquer(choix.analytics);
  } else if (navigator.globalPrivacyControl) {
    /* Le navigateur annonce un refus global : nous le respectons sans demander. */
    appliquer(false);
  } else {
    if (MODE_AVANCE) chargerBalise();
    ouvrir();
  }
})();
