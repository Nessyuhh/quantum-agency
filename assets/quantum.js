/* ============================================================================
   Quantum Consulting : comportements partagés
   Navigation, progression, FAQ, formulaire d'audit, animations (GSAP).
   Sans GSAP ou avec prefers-reduced-motion, la page reste complète : les
   états finaux sont ceux du CSS, les scripts n'ajoutent que le mouvement.
   ========================================================================== */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var anglaisPage = document.documentElement.lang === 'en';
  var racine = document.documentElement;

  /* ── Barre de navigation évolutive ──
     Trois états, posés sur <html data-nav> pour que le CSS règle d'un coup la
     barre d'ordinateur, celle du téléphone et la navigation basse :
       haut    : en tête de page, transparente, logo complet ;
       milieu  : pendant la lecture, compacte, avec le repère de section ;
       bas     : le pied de page approche, elle s'inverse et propose de
                 remonter, puisque c'est la question du visiteur à cet endroit.
     Sur téléphone, elle s'efface quand on descend et revient dès qu'on
     remonte : l'écran est trop petit pour une barre qui ne sert pas.
     Tout est calculé une fois par image, jamais à chaque évènement. */
  var bar = document.getElementById('progress-bar');
  var navbar = document.getElementById('navbar');
  var pied = document.querySelector('footer');
  var dernierY = window.scrollY;
  var enAttente = false;

  /* Bouton de retour en haut, ajouté ici plutôt que dans les 124 pages : il
     n'existe que pour l'état « bas », qui n'existe que si le script tourne. */
  document.querySelectorAll('.navbar .nav-right, .mob-top-bar .nav-right').forEach(function (zone) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'nav-haut';
    b.setAttribute('aria-label', anglaisPage ? 'Back to top' : 'Revenir en haut de la page');
    b.textContent = '↑';
    zone.appendChild(b);
  });

  function etatNav() {
    enAttente = false;
    var y = window.scrollY;
    var vue = window.innerHeight;
    var h = racine.scrollHeight - vue;
    if (bar) bar.style.transform = 'scaleX(' + (h > 0 ? Math.min(y / h, 1) : 0) + ')';

    var etat = 'milieu';
    if (y < 40) etat = 'haut';
    else if ((pied && pied.getBoundingClientRect().top < vue * 0.85) || h - y < 60) etat = 'bas';
    if (racine.dataset.nav !== etat) racine.dataset.nav = etat;

    /* Seuil de 6 px : un doigt qui tremble ne doit pas faire clignoter la barre. */
    var dy = y - dernierY;
    if (Math.abs(dy) > 6) {
      var cachee = dy > 0 && y > 240 && etat === 'milieu';
      racine.classList.toggle('nav-cachee', cachee);
      dernierY = y;
    }
    if (navbar) navbar.classList.toggle('scrolled', etat !== 'haut');
  }
  function auDefilement() {
    if (!enAttente) { enAttente = true; requestAnimationFrame(etatNav); }
  }
  window.addEventListener('scroll', auDefilement, { passive: true });
  window.addEventListener('resize', auDefilement, { passive: true });
  etatNav();

  /* ── Repère de section ──
     Dans l'état « milieu », la barre dit où l'on est : numéro et nom de la
     section lue. Le nom vient du sur-titre de la section, à défaut de son
     titre ; sur un article, des intertitres. Masqué aux lecteurs d'écran,
     qui ont déjà les titres : ce serait une annonce en double. */
  (function () {
    if (!navbar || !('IntersectionObserver' in window)) return;
    var cibles = [];
    var art = document.querySelector('.art-body');
    if (art) {
      cibles = [].slice.call(art.querySelectorAll('h2')).map(function (h) { return { el: h, nom: h.textContent }; });
    } else {
      document.querySelectorAll('main section').forEach(function (s) {
        if (s.parentElement.closest('main section')) return;
        var t = s.getAttribute('data-repere') || (s.querySelector('.eyebrow, .pg-tag') || s.querySelector('h2, h1') || {}).textContent;
        if (t) cibles.push({ el: s, nom: t });
      });
    }
    if (cibles.length < 2) return;

    var repere = document.createElement('div');
    repere.className = 'nav-repere';
    repere.setAttribute('aria-hidden', 'true');
    repere.innerHTML = '<span class="nav-repere-n"></span><span class="nav-repere-t"></span>';
    navbar.querySelector('.brand').insertAdjacentElement('afterend', repere);
    var n = repere.firstChild, t = repere.lastChild;
    var total = String(cibles.length).padStart(2, '0');

    var obs = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (e) {
        if (!e.isIntersecting) return;
        var i = cibles.findIndex(function (c) { return c.el === e.target; });
        if (i < 0) return;
        n.textContent = String(i + 1).padStart(2, '0') + ' / ' + total;
        t.textContent = cibles[i].nom.replace(/\s+/g, ' ').trim();
        repere.classList.remove('bascule');
        void repere.offsetWidth;
        repere.classList.add('bascule');
      });
    }, { rootMargin: art ? '0px 0px -70% 0px' : '-40% 0px -55% 0px' });
    cibles.forEach(function (c) { obs.observe(c.el); });
  })();

  /* ── Délégation des clics ──
     Plus aucun gestionnaire écrit dans le HTML (onclick) : c'est ce qui permet
     à la politique de sécurité du contenu d'interdire tout script en ligne,
     la protection la plus efficace contre l'injection de code. */
  document.addEventListener('click', function (e) {
    var cible = e.target.closest && e.target.closest('.faq-trigger, .nav-haut, #back-top');
    if (!cible) return;
    if (cible.classList.contains('faq-trigger')) { window.toggleFaq(cible); return; }
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
  });

  /* ── Apparitions au défilement ──
     Sans bibliothèque : un seul IntersectionObserver, et des transitions CSS
     sur l'opacité et la transformation, les deux seules propriétés que le
     navigateur anime sans recalculer la page.
     Règle qui protège la performance : rien de ce qui est visible au premier
     affichage n'est jamais masqué. Seuls les éléments sous la ligne de
     flottaison reçoivent l'état d'attente, donc le premier rendu et le plus
     grand élément affiché, que Google mesure, restent immédiats. */
  (function () {
    if (reduce || !('IntersectionObserver' in window)) return;
    var SELECTEURS = [
      'main section h2', '.sec-title', '.wf-head', '.row', '.bl-card', '.bl-pole h2',
      '.faq-item', '.svc', '.fiche', '.promesse', '.art-body h2', '.art-callout',
      '.art-cta', '.art-faq', '.lire-aussi', '.audit-form', 'main [data-reveal]',
      'main section .eyebrow', '.rows', '.bl-grid', '.faq-accordion', '.footer-grid'
    ].join(',');
    /* Les conteneurs ne s'effacent pas : seul leur filet supérieur se trace,
       leurs enfants apparaissent un à un. */
    var FILETS = '.rows, .bl-grid, .faq-accordion, .footer-grid';
    var vue = window.innerHeight;
    var retenus = [].slice.call(document.querySelectorAll(SELECTEURS)).filter(function (el) {
      if (el.closest('.hero, #intro-overlay, .offre-pop')) return false;
      return el.getBoundingClientRect().top > vue * 0.92;
    });
    /* Un élément déjà porté par un parent animé ne s'anime pas une seconde
       fois : deux fondus imbriqués se lisent comme un défaut. */
    var elements = retenus.filter(function (el) {
      if (el.matches(FILETS)) return true;
      var p = el.parentElement;
      while (p && p !== document.body) {
        if (retenus.indexOf(p) !== -1 && !p.matches(FILETS)) return false;
        p = p.parentElement;
      }
      return true;
    });
    if (!elements.length) return;

    /* Décalage en cascade entre voisins d'un même parent, plafonné : au-delà
       de six, l'attente devient une gêne plutôt qu'un rythme. */
    var rangs = new Map();
    elements.forEach(function (el) {
      var p = el.parentElement;
      var r = rangs.get(p) || 0;
      rangs.set(p, r + 1);
      el.style.setProperty('--qa-rang', Math.min(r, 6));
      if (el.matches(FILETS)) el.classList.add('qa-filet');
      else el.classList.add(/^(H1|H2)$/.test(el.tagName) || el.classList.contains('sec-title') ? 'qa-titre' : 'qa-av');
    });

    /* Un titre masqué par clip-path n'a plus de surface visible, donc
       l'observateur ne le verrait jamais entrer : on observe son parent. */
    var guetteurs = new Map();
    elements.forEach(function (el) {
      var g = el.classList.contains('qa-titre') ? el.parentElement : el;
      if (!guetteurs.has(g)) guetteurs.set(g, []);
      guetteurs.get(g).push(el);
    });
    var obs = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (e) {
        if (!e.isIntersecting) return;
        obs.unobserve(e.target);
        (guetteurs.get(e.target) || []).forEach(function (el) {
          el.classList.add('qa-vu');
          decoder(el);
        });
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0 });
    guetteurs.forEach(function (_, g) { obs.observe(g); });
  })();

  /* ── Décodage des libellés ──
     Les sur-titres et les numéros en chasse fixe se décodent à leur arrivée,
     comme une sortie de modèle qui se stabilise. 450 ms, texte exact à la fin,
     et le texte d'origine reste dans la page pour les moteurs. */
  var GLYPHES = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&/<>';
  function decoder(zone) {
    if (reduce) return;
    var cibles = zone.matches('.eyebrow, .k') ? [zone] : [].slice.call(zone.querySelectorAll('.eyebrow, .k'));
    cibles.forEach(function (el) {
      if (el.dataset.decode || el.children.length) return;
      el.dataset.decode = '1';
      var fin = el.textContent;
      var debut = performance.now();
      (function image(t) {
        var p = Math.min((t - debut) / 450, 1);
        var fixes = Math.floor(fin.length * p);
        var s = fin.slice(0, fixes);
        for (var i = fixes; i < fin.length; i++) {
          s += /\s/.test(fin[i]) ? fin[i] : GLYPHES[(Math.random() * GLYPHES.length) | 0];
        }
        el.textContent = s;
        if (p < 1) requestAnimationFrame(image); else el.textContent = fin;
      })(debut);
    });
  }

  /* ── Lueur sous le pointeur ──
     Sur les rangées et les cartes, un halo aux couleurs du logo suit la
     souris. Une variable CSS par déplacement, aucun recalcul de mise en page.
     Pointeur fin seulement : sur écran tactile, il n'y a rien à suivre. */
  if (!reduce && window.matchMedia('(pointer: fine)').matches) {
    document.addEventListener('pointermove', function (e) {
      var c = e.target.closest && e.target.closest('.row, .bl-card, .svc, .art-nav a, .art-prev, .art-next');
      if (!c) return;
      var r = c.getBoundingClientRect();
      c.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      c.style.setProperty('--my', (e.clientY - r.top) + 'px');
    }, { passive: true });
  }

  /* ── FAQ ── */
  window.toggleFaq = function (btn) {
    var item = btn.parentElement;
    var wasActive = item.classList.contains('active');
    document.querySelectorAll('.faq-item').forEach(function (el) {
      el.classList.remove('active');
      el.querySelector('.faq-content').style.maxHeight = null;
      el.querySelector('.faq-trigger').setAttribute('aria-expanded', 'false');
    });
    if (!wasActive) {
      item.classList.add('active');
      var c = item.querySelector('.faq-content');
      c.style.maxHeight = c.scrollHeight + 'px';
      btn.setAttribute('aria-expanded', 'true');
    }
  };

  /* ── Formulaire d'audit ──
     L'URL du service qui reçoit la demande est dans data-webhook du <form>.
     Les messages suivent la langue de la page : un visiteur anglophone qui
     lisait « Merci ! Votre demande a été reçue » ne savait pas si son envoi
     avait abouti. */
  var form = document.querySelector('form[data-webhook]');
  if (form) {
    var enAnglais = document.documentElement.lang === 'en';
    var messages = enAnglais ? {
      absent: 'This form is not connected yet. Write to us at contact@quantum-agency.fr in the meantime.',
      envoi: 'Sending…',
      succes: 'Thank you. We have received your request and will get back to you within one working day.',
      erreur: 'Something went wrong. Write to us at contact@quantum-agency.fr.'
    } : {
      absent: 'Formulaire pas encore connecté. Écrivez-nous directement à contact@quantum-agency.fr en attendant.',
      envoi: 'Envoi en cours…',
      succes: 'Merci ! Votre demande a été reçue. Nous vous recontactons sous 24h.',
      erreur: 'Une erreur est survenue. Écrivez-nous directement à contact@quantum-agency.fr.'
    };
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var url = form.getAttribute('data-webhook') || '';
      var btn = form.querySelector('button[type="submit"]');
      var note = form.querySelector('.form-note');
      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      data.source = 'quantum-agency.fr';
      data.page = location.pathname;
      data.timestamp = new Date().toISOString();

      if (!/^https?:\/\//.test(url)) {
        note.textContent = messages.absent;
        note.className = 'form-note error';
        console.warn('[Quantum] data-webhook non configuré sur le formulaire.');
        return;
      }

      var label = btn.textContent;
      btn.disabled = true;
      btn.textContent = messages.envoi;
      note.textContent = '';
      note.className = 'form-note';

      fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
        .then(function (res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          form.reset();
          note.textContent = messages.succes;
          note.className = 'form-note success';
          /* Conversion GA4 : ne part que si le visiteur a accepté la mesure (consent.js). */
          if (window.quantumSuivre) window.quantumSuivre('generate_lead', { form: 'audit', page: location.pathname });
        })
        .catch(function () {
          note.textContent = messages.erreur;
          note.className = 'form-note error';
        })
        .then(function () {
          btn.disabled = false;
          btn.textContent = label;
        });
    });
  }

  /* ── Écran d'entrée ──
     Le tracé du Q, le mot qui se déplie, puis le logo rejoint la barre de
     navigation. Une seule fois par session : plaisant au premier passage,
     pénible au troisième. sessionStorage et non localStorage, pour que le
     charme rejoue à la prochaine visite. */
  var entreeEnCours = false;

  (function () {
    var ov = document.getElementById('intro-overlay');
    if (!ov) return;

    var passe = reduce || window.matchMedia('(max-width: 900px)').matches;
    try {
      if (sessionStorage.getItem('quantum-entree-vue')) passe = true;
      else sessionStorage.setItem('quantum-entree-vue', '1');
    } catch (e) { /* navigation privée : l'entrée rejoue, sans conséquence */ }

    if (passe) {
      ov.remove();
      document.body.classList.remove('intro-active');
      return;
    }

    entreeEnCours = true;
    var q = document.getElementById('i-q');
    var mot = document.getElementById('i-mot');
    var minuteries = [];
    var attendre = function (ms, fn) { minuteries.push(setTimeout(fn, ms)); };

    function fermer() {
      ov.classList.add('fading');
      attendre(550, function () {
        if (ov.parentNode) ov.remove();
        document.body.classList.remove('intro-active');
        document.dispatchEvent(new CustomEvent('quantum:entree-finie'));
      });
    }

    /* Une entrée dont on ne peut pas sortir est une prison : clic, touche ou
       molette terminent la séquence immédiatement. */
    function couper() {
      minuteries.forEach(clearTimeout);
      if (q.parentNode) q.remove();
      fermer();
    }
    ov.addEventListener('click', couper);
    window.addEventListener('keydown', couper, { once: true });
    window.addEventListener('wheel', couper, { once: true, passive: true });

    attendre(180, function () { document.getElementById('i-arc').classList.add('trace'); });
    attendre(1060, function () { document.getElementById('i-tail').classList.add('trace'); });
    attendre(1300, function () { mot.classList.add('visible'); });

    attendre(2450, function () {
      var depart = q.getBoundingClientRect();
      var cible = document.querySelector('.navbar .brand svg');
      mot.style.transition = 'opacity .25s ease-out';
      mot.style.opacity = '0';

      /* Le Q est sorti de l'écran d'entrée et épinglé à sa position :
         il survit à la disparition de l'écran d'entrée pendant son trajet. */
      q.style.position = 'fixed';
      q.style.left = depart.left + 'px';
      q.style.top = depart.top + 'px';
      q.style.margin = '0';
      q.style.zIndex = '10000';
      document.body.appendChild(q);
      fermer();

      if (!cible) { attendre(400, function () { if (q.parentNode) q.remove(); }); return; }
      var arrivee = cible.getBoundingClientRect();
      var echelle = arrivee.width / depart.width;
      var dx = (arrivee.left + arrivee.width / 2) - (depart.left + depart.width / 2);
      var dy = (arrivee.top + arrivee.height / 2) - (depart.top + depart.height / 2);
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          q.style.transition = 'transform .7s cubic-bezier(.4,0,.2,1), opacity .3s ease-in .42s';
          q.style.transform = 'translate(' + dx + 'px,' + dy + 'px) scale(' + echelle + ')';
          q.style.opacity = '0';
        });
      });
      attendre(760, function () { if (q.parentNode) q.remove(); });
    });
  })();

  /* ── Fenêtre du site vitrine offert ──
     Elle s'ouvre après un délai ou à mi-page, selon ce qui arrive en premier,
     et une seule fois par visiteur tant qu'il n'a pas répondu. Réglages en tête
     de bloc, tout se change ici. */
  (function () {
    var DELAI = 45;          // secondes avant ouverture, en dernier recours
    var PROFONDEUR = 0.6;    // ou cette part de la page parcourue
    var REPOS = 14;          // jours avant de reproposer après une fermeture
    var GARDE = 8;           // secondes de grâce : personne n'est accueilli par une fenêtre

    var exclues = ['/contact.html', '/en/contact.html', '/charte/'];
    if (exclues.indexOf(location.pathname) !== -1) return;

    var anglais = document.documentElement.lang === 'en';
    var cle = 'quantum-site-offert';
    var etat = null;
    try { etat = localStorage.getItem(cle); } catch (e) { /* stockage refusé : on propose */ }
    if (etat === 'envoye') return;
    if (etat && Date.now() - Number(etat) < REPOS * 86400000) return;

    var webhook = (document.querySelector('form[data-webhook]') || {}).getAttribute
      ? document.querySelector('form[data-webhook]').getAttribute('data-webhook') : '';

    var t = anglais ? {
      sur: 'No commitment',
      titre: 'A showcase website, <span class="grad-text">on us</span>',
      texte: 'Your business, your services, how to reach you. A simple site, put online under your name, and it is yours to keep. Leave us your e-mail and we send you the details and the timeline.',
      champ: 'Your work e-mail', envoyer: 'I want my free website →', fermer: 'Close',
      mention: 'One e-mail, no mailing list, no sharing with anyone.',
      merci: 'Thank you. We send you the details within one working day.',
      erreur: 'Something went wrong. Write to us at contact@quantum-agency.fr.'
    } : {
      sur: 'Sans engagement',
      titre: 'Un site vitrine, <span class="grad-text">offert</span>',
      texte: "Votre activité, vos services, comment vous joindre. Un site simple, mis en ligne à votre nom, et il est à vous. Laissez-nous votre e-mail, nous vous envoyons le détail et les délais.",
      champ: 'Votre e-mail professionnel', envoyer: 'Je veux mon site offert →', fermer: 'Fermer',
      mention: 'Un seul e-mail, aucune liste de diffusion, aucun partage.',
      merci: 'Merci. Nous vous envoyons le détail sous 24 heures ouvrées.',
      erreur: 'Une erreur est survenue. Écrivez-nous à contact@quantum-agency.fr.'
    };

    var pop = document.createElement('div');
    pop.className = 'offre-pop';
    pop.setAttribute('role', 'dialog');
    pop.setAttribute('aria-modal', 'true');
    pop.setAttribute('aria-labelledby', 'offre-titre');
    pop.innerHTML =
      '<div class="offre-voile"></div>' +
      '<div class="offre-boite">' +
        '<button type="button" class="offre-fermer" aria-label="' + t.fermer + '">✕</button>' +
        '<p class="eyebrow">' + t.sur + '</p>' +
        '<h2 id="offre-titre">' + t.titre + '</h2>' +
        '<p class="texte">' + t.texte + '</p>' +
        '<form novalidate>' +
          '<label class="sr-only" for="offre-email">' + t.champ + '</label>' +
          '<input id="offre-email" type="email" name="email" placeholder="' + t.champ + '" required autocomplete="email">' +
          '<div class="piege" aria-hidden="true"><label for="offre-site">Ne pas remplir</label><input id="offre-site" name="site_web" type="text" tabindex="-1" autocomplete="off"></div>' +
          '<button type="submit" class="btn btn-grad">' + t.envoyer + '</button>' +
          '<p class="offre-mention">' + t.mention + '</p>' +
          '<div class="form-note" role="status" aria-live="polite"></div>' +
        '</form>' +
      '</div>';

    var minuteur, ouverte = false, dernierFocus = null;

    function memoriser(valeur) { try { localStorage.setItem(cle, valeur); } catch (e) { /* sans stockage, la fenêtre reviendra */ } }

    function ouvrir() {
      if (ouverte) return;
      /* Une sollicitation à la fois : tant que la bannière de consentement est
         affichée, la fenêtre attend quinze secondes de plus. */
      if (document.querySelector('.consent.ouverte')) {
        clearTimeout(minuteur);
        minuteur = setTimeout(ouvrir, 15000);
        return;
      }
      ouverte = true;
      clearTimeout(minuteur);
      window.removeEventListener('scroll', auScroll);
      document.body.appendChild(pop);
      requestAnimationFrame(function () { pop.classList.add('ouverte'); });
      dernierFocus = document.activeElement;
      pop.querySelector('#offre-email').focus({ preventScroll: true });
    }

    function fermer(memo) {
      pop.classList.remove('ouverte');
      if (memo !== false) memoriser(String(Date.now()));
      setTimeout(function () { if (pop.parentNode) pop.remove(); }, 320);
      if (dernierFocus && dernierFocus.focus) dernierFocus.focus();
    }

    pop.querySelector('.offre-fermer').addEventListener('click', function () { fermer(); });
    pop.querySelector('.offre-voile').addEventListener('click', function () { fermer(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && ouverte) fermer(); });

    pop.querySelector('form').addEventListener('submit', function (e) {
      e.preventDefault();
      var champ = pop.querySelector('#offre-email');
      var note = pop.querySelector('.form-note');
      var btn = pop.querySelector('button[type="submit"]');
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(champ.value.trim())) { champ.focus(); return; }
      if (!/^https?:\/\//.test(webhook)) { note.textContent = t.erreur; note.className = 'form-note error'; return; }

      var libelle = btn.textContent;
      btn.disabled = true;
      btn.textContent = anglais ? 'Sending…' : 'Envoi en cours…';
      fetch(webhook, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: champ.value.trim(),
          site_web: pop.querySelector('#offre-site').value,
          type: 'site-offert',
          source: 'quantum-agency.fr',
          page: location.pathname,
          timestamp: new Date().toISOString()
        })
      }).then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        memoriser('envoye');
        if (window.quantumSuivre) window.quantumSuivre('generate_lead', { form: 'site-offert', page: location.pathname });
        note.textContent = t.merci;
        note.className = 'form-note success';
        pop.querySelector('form').reset();
        setTimeout(function () { fermer(false); }, 2200);
      }).catch(function () {
        note.textContent = t.erreur;
        note.className = 'form-note error';
      }).then(function () {
        btn.disabled = false;
        btn.textContent = libelle;
      });
    });

    function auScroll() {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      if (h > 0 && window.scrollY / h >= PROFONDEUR) ouvrir();
    }

    /* Intention de départ : le curseur franchit le haut de la fenêtre, vers la
       barre d'adresse ou l'onglet. C'est le moment le plus utile pour proposer
       quelque chose, puisque la page allait être quittée de toute façon.
       Le pointeur fin exclut les écrans tactiles, où ce geste n'existe pas :
       là, le délai et le défilement prennent le relais. */
    var depuis = Date.now();
    if (window.matchMedia('(pointer: fine)').matches) {
      document.addEventListener('mouseout', function (e) {
        if (e.relatedTarget || e.clientY > 8) return;
        if (Date.now() - depuis < GARDE * 1000) return;
        ouvrir();
      });
    }

    minuteur = setTimeout(ouvrir, DELAI * 1000);
    window.addEventListener('scroll', auScroll, { passive: true });
  })();

  /* ── Chatbot ──
     Seul le bouton est posé au chargement : quelques centaines d'octets. La
     fenêtre de discussion (script et styles) ne se télécharge qu'au premier
     survol ou au premier clic, donc elle ne coûte rien au visiteur qui ne
     s'en sert pas, ni à la note de performance.
     À passer à true une fois le Worker muni de sa clé : voir
     formulaire/README.md, section « Chatbot ». */
  var CHATBOT_ACTIF = false;
  (function () {
    if (!CHATBOT_ACTIF && !/[?&]chat=1\b/.test(location.search)) return;
    if (/^\/(outils|apercus|archives|charte)\//.test(location.pathname)) return;
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'chat-lanceur';
    b.setAttribute('aria-haspopup', 'dialog');
    b.innerHTML = '<svg aria-hidden="true" viewBox="0 0 64 64"><use href="#qMark"/></svg><span>' + (anglaisPage ? 'Ask us' : 'Une question ?') + '</span>';
    document.body.appendChild(b);

    var charge = null;
    function charger() {
      if (charge) return charge;
      var css = document.createElement('link');
      css.rel = 'stylesheet';
      css.href = '/assets/chat.css?v=1';
      document.head.appendChild(css);
      charge = new Promise(function (ok, non) {
        var js = document.createElement('script');
        js.src = '/assets/chat.js?v=1';
        js.onload = ok;
        js.onerror = non;
        document.head.appendChild(js);
      });
      return charge;
    }
    b.addEventListener('pointerenter', charger, { once: true });
    b.addEventListener('focus', charger, { once: true });
    b.addEventListener('click', function () {
      charger().then(function () { window.quantumChat.ouvrir(b); });
    });
    /* Une conversation en cours rouvre la fenêtre d'une page à l'autre. */
    try {
      if (sessionStorage.getItem('quantum-chat-ouvert') === '1') charger().then(function () { window.quantumChat.ouvrir(b, true); });
    } catch (e) { /* stockage refusé : la fenêtre reste fermée */ }
  })();

  /* ── Animations ──
     GSAP et ses deux greffons pèsent près de 70 Ko. Ils ne servent qu'au flux
     animé : on les charge quand il approche, pas au premier affichage. */
  if (reduce) return;

  /* Servis depuis le site, comme les polices : une connexion à un tiers de
     moins, aucune dépendance à la disponibilité d'un CDN, et la politique de
     sécurité peut interdire tout script venu d'ailleurs. Version 3.12.5. */
  var CDN = '/assets/vendor/gsap/';
  function script(fichier) {
    return new Promise(function (ok, non) {
      var e = document.createElement('script');
      e.src = CDN + fichier;
      e.onload = ok;
      e.onerror = non;
      document.head.appendChild(e);
    });
  }

  function animer() {
    gsap.registerPlugin(ScrollTrigger, MotionPathPlugin);
    animations();
  }

  if (typeof gsap !== 'undefined') {
    animer();
  } else {
    /* Le conteneur, jamais l'un des deux tracés : celui qui n'est pas affiché
       est en display:none, et un élément masqué n'entre jamais dans le champ
       d'un IntersectionObserver. */
    var declencheur = document.getElementById('workflow') || document.querySelector('.hero');
    if (!declencheur) return;
    var charge = false;
    var charger = function () {
      if (charge) return;
      charge = true;
      observateur.disconnect();
      script('gsap.min.js')
        .then(function () { return Promise.all([script('ScrollTrigger.min.js'), script('MotionPathPlugin.min.js')]); })
        .then(animer)
        .catch(function () { /* réseau indisponible : la page reste entière, sans mouvement */ });
    };
    /* 250 px d'avance : assez pour télécharger avant que la section entre, pas
       assez pour se déclencher au chargement, le flux étant juste sous le
       premier écran de l'accueil. Le chargement attend en outre un moment de
       repos du navigateur, pour ne pas concurrencer le premier affichage. */
    var lancer = window.requestIdleCallback || function (fn) { setTimeout(fn, 200); };
    var observateur = new IntersectionObserver(function (entrees) {
      if (entrees.some(function (e) { return e.isIntersecting; })) lancer(charger, { timeout: 1500 });
    }, { rootMargin: '250px' });
    observateur.observe(declencheur);
  }

  function animations() {

  /* Hero : les lignes se verrouillent en place. Quand l'écran d'entrée joue,
     on attend qu'il se lève, sinon l'animation se déroulerait derrière lui et
     le visiteur ne verrait jamais que son résultat. */
  var reveals = document.querySelectorAll('.hero [data-reveal]');
  if (reveals.length) {
    var reveler = function () {
      gsap.from(reveals, { y: 34, opacity: 0, duration: 1, ease: 'power3.out', stagger: 0.09, delay: 0.1, clearProps: 'transform,opacity' });
    };
    if (entreeEnCours) {
      gsap.set(reveals, { opacity: 0 });
      document.addEventListener('quantum:entree-finie', function () {
        gsap.set(reveals, { opacity: 1 });
        reveler();
      }, { once: true });
    } else {
      reveler();
    }
  }

  /* Workflow animé : les arêtes se tracent, les nœuds s'allument, puis les
     paquets circulent en boucle. L'état « tout allumé » est celui du CSS :
     on le retire ici avant d'animer, jamais l'inverse. */
  /* Deux tracés (horizontal desktop, vertical mobile) : on anime celui que
     le CSS affiche, l'autre garde son état final. */
  var svg = Array.prototype.filter.call(document.querySelectorAll('.wf-svg'), function (el) {
    return getComputedStyle(el).display !== 'none';
  })[0];
  if (!svg) return;

  var edges = Array.prototype.slice.call(svg.querySelectorAll('.wf-edge'));
  var nodes = Array.prototype.slice.call(svg.querySelectorAll('.wf-node, .wf-out'));
  edges.forEach(function (p) {
    var L = p.getTotalLength();
    p.style.strokeDasharray = L;
    p.style.strokeDashoffset = L;
  });
  nodes.forEach(function (n) { n.classList.remove('on'); });

  var packets = gsap.timeline({ paused: true });
  /* Les paquets sont insérés juste avant le premier cadre : ils circulent
     derrière les nœuds, qui restent au premier plan. */
  var firstBox = svg.querySelector('.wf-in, .wf-node, .wf-out');
  function startPackets() {
    var ns = 'http://www.w3.org/2000/svg';
    edges.forEach(function (p, i) {
      var c = document.createElementNS(ns, 'circle');
      c.setAttribute('r', '5');
      c.setAttribute('class', 'wf-packet');
      svg.insertBefore(c, firstBox);
      packets.to(c, {
        motionPath: { path: p, align: p, alignOrigin: [0.5, 0.5] },
        duration: 1.5 + (i % 3) * 0.4,
        repeat: -1,
        repeatDelay: 0.6 + (i % 4) * 0.35,
        ease: 'none'
      }, i * 0.28);
    });
    packets.play();
  }

  var tl = gsap.timeline({
    scrollTrigger: { trigger: svg, start: 'top 78%', once: true }
  });
  var lastStep = edges.concat(nodes).reduce(function (m, el) { return Math.max(m, +el.dataset.step || 0); }, 0);
  for (var s = 1; s <= lastStep; s++) {
    (function (step) {
      var es = edges.filter(function (e) { return +e.dataset.step === step; });
      var ns = nodes.filter(function (n) { return +n.dataset.step === step; });
      if (es.length) tl.to(es, { strokeDashoffset: 0, duration: 0.55, ease: 'power2.inOut', stagger: 0.1 });
      if (ns.length) tl.add(function () { ns.forEach(function (n, i) { setTimeout(function () { n.classList.add('on'); }, i * 120); }); });
      tl.to({}, { duration: 0.12 });
    })(s);
  }
  tl.add(startPackets);

  /* Les entrées « tremblent » légèrement : le désordre avant le flux. */
  gsap.to(svg.querySelectorAll('.wf-in'), { rotation: '+=2.5', transformOrigin: '50% 50%', yoyo: true, repeat: -1, duration: 1.8, ease: 'sine.inOut', stagger: 0.25 });

  ScrollTrigger.create({
    trigger: svg, start: 'top bottom', end: 'bottom top',
    onLeave: function () { packets.pause(); },
    onLeaveBack: function () { packets.pause(); },
    onEnter: function () { if (tl.progress() === 1) packets.play(); },
    onEnterBack: function () { packets.play(); }
  });
  }
})();
