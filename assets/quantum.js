/* ============================================================================
   Quantum Consulting — comportements partagés
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
        note.textContent = 'Formulaire pas encore connecté — écrivez-nous directement à contact@quantum-agency.fr en attendant.';
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

  /* ── Animations ── */
  if (reduce || typeof gsap === 'undefined') return;
  gsap.registerPlugin(ScrollTrigger, MotionPathPlugin);

  /* Hero : les lignes se verrouillent en place au chargement. */
  var reveals = document.querySelectorAll('.hero [data-reveal]');
  if (reveals.length) {
    gsap.from(reveals, { y: 34, opacity: 0, duration: 1, ease: 'power3.out', stagger: 0.09, delay: 0.1, clearProps: 'transform,opacity' });
  }

  /* Workflow animé : les arêtes se tracent, les nœuds s'allument, puis les
     paquets circulent en boucle. L'état « tout allumé » est celui du CSS :
     on le retire ici avant d'animer, jamais l'inverse. */
  var svg = document.getElementById('wf');
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
  function startPackets() {
    var ns = 'http://www.w3.org/2000/svg';
    edges.forEach(function (p, i) {
      var c = document.createElementNS(ns, 'circle');
      c.setAttribute('r', '4');
      c.setAttribute('class', 'wf-packet');
      svg.appendChild(c);
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
