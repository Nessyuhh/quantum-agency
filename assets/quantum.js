/* ============================================================================
   Quantum Consulting : comportements partagés
   Navigation, progression, FAQ, formulaire d'audit, animations (GSAP).
   Sans GSAP ou avec prefers-reduced-motion, la page reste complète : les
   états finaux sont ceux du CSS, les scripts n'ajoutent que le mouvement.
   ========================================================================== */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── Progression + fond de la barre de navigation ── */
  var bar = document.getElementById('progress-bar');
  var navbar = document.getElementById('navbar');
  function onScroll() {
    var h = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    if (bar) bar.style.transform = 'scaleX(' + (h > 0 ? window.scrollY / h : 0) + ')';
    if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 40);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

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

  /* ── Formulaire d'audit → webhook n8n (URL dans data-webhook du <form>) ── */
  var form = document.querySelector('form[data-webhook]');
  if (form) {
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
        note.textContent = 'Formulaire pas encore connecté. Écrivez-nous directement à contact@quantum-agency.fr en attendant.';
        note.className = 'form-note error';
        console.warn('[Quantum] data-webhook non configuré sur le formulaire.');
        return;
      }

      var label = btn.textContent;
      btn.disabled = true;
      btn.textContent = 'Envoi en cours…';
      note.textContent = '';
      note.className = 'form-note';

      fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
        .then(function (res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          form.reset();
          note.textContent = 'Merci ! Votre demande a été reçue. Nous vous recontactons sous 24h.';
          note.className = 'form-note success';
        })
        .catch(function () {
          note.textContent = 'Une erreur est survenue. Écrivez-nous directement à contact@quantum-agency.fr.';
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
    var DELAI = 30;          // secondes avant ouverture
    var PROFONDEUR = 0.5;    // ou cette part de la page parcourue
    var REPOS = 14;          // jours avant de reproposer après une fermeture

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

    minuteur = setTimeout(ouvrir, DELAI * 1000);
    window.addEventListener('scroll', auScroll, { passive: true });
  })();

  /* ── Animations ── */
  if (reduce || typeof gsap === 'undefined') return;
  gsap.registerPlugin(ScrollTrigger, MotionPathPlugin);

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
})();
