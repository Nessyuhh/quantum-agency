/* ============================================================================
   Lecture d'article — sommaire, progression, navigation
   ----------------------------------------------------------------------------
   POURQUOI CE FICHIER EXISTE, CHIFFRES À L'APPUI
   · 73 % des visiteurs quittent une page en moins de dix secondes si elle est
     difficile à lire.
   · 79 % balaient une nouvelle page, 16 % seulement lisent mot à mot
     (Nielsen Norman).

   On n'écrit donc pas pour un lecteur, on écrit pour un BALAYEUR. Ce script
   fournit les trois repères qui retiennent : où j'en suis, ce qu'il reste, où
   aller ensuite.

   Aucune dépendance. Tout se dégrade proprement sans JavaScript : le sommaire
   et la barre n'apparaissent pas, l'article reste entier.
   ========================================================================== */

(function () {
  'use strict';

  var corps = document.querySelector('.art-body');
  if (!corps) return;

  var REDUIT = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── Barre de progression ────────────────────────────────────────────────
     Elle augmente le taux d'achèvement et réduit le rebond. Purement
     décorative : aucune information n'en dépend, d'où aria-hidden. */
  var barre = document.createElement('div');
  barre.className = 'art-progres';
  barre.setAttribute('aria-hidden', 'true');
  document.body.appendChild(barre);

  /* ── Sommaire ────────────────────────────────────────────────────────────
     Utile à partir de QUATRE sections. En dessous il encombre plus qu'il
     n'aide — c'est le seuil retenu par les études d'usage. */
  var titres = [].slice.call(corps.querySelectorAll('h2'))
    .filter(function (h) { return !h.closest('.art-faq'); });

  var liens = [];
  if (titres.length >= 4) {
    var nav = document.createElement('nav');
    nav.className = 'art-sommaire';
    nav.setAttribute('aria-label', 'Sommaire de l’article');
    var html = '<p class="art-sommaire-t">Dans cet article</p><ol>';
    titres.forEach(function (h, i) {
      if (!h.id) h.id = 'sec-' + (i + 1);
      html += '<li><a href="#' + h.id + '">' + h.textContent.trim() + '</a></li>';
    });
    nav.innerHTML = html + '</ol>';
    var apres = corps.querySelector('.art-reponse');
    if (apres && apres.parentNode) apres.parentNode.insertBefore(nav, apres.nextSibling);
    else corps.insertBefore(nav, corps.firstChild);
    liens = [].slice.call(nav.querySelectorAll('a'));
  }

  /* ── Suivi ───────────────────────────────────────────────────────────────
     Une seule fonction pour la barre et la section active : deux écouteurs de
     défilement séparés se désynchronisent visiblement. */
  var actif = -1;
  function suivre() {
    var h = document.documentElement;
    var course = h.scrollHeight - window.innerHeight;
    var p = course > 0 ? Math.min(1, Math.max(0, window.scrollY / course)) : 0;
    barre.style.transform = 'scaleX(' + p.toFixed(4) + ')';

    if (!liens.length) return;
    /* La section active est la dernière dont le haut est passé sous la barre
       de navigation. Prendre « la plus proche du centre » fait clignoter le
       surlignage sur les sections courtes. */
    var i = 0;
    for (var k = 0; k < titres.length; k++) {
      if (titres[k].getBoundingClientRect().top <= 120) i = k;
    }
    if (i !== actif) {
      if (liens[actif]) liens[actif].removeAttribute('aria-current');
      liens[i].setAttribute('aria-current', 'true');
      actif = i;
    }
  }

  window.addEventListener('scroll', suivre, { passive: true });
  window.addEventListener('resize', suivre, { passive: true });
  suivre();

  /* ── Défilement doux vers une section ──────────────────────────────────── */
  liens.forEach(function (a) {
    a.addEventListener('click', function (e) {
      var cible = document.getElementById(a.getAttribute('href').slice(1));
      if (!cible) return;
      e.preventDefault();
      var y = cible.getBoundingClientRect().top + window.scrollY - 96;
      window.scrollTo({ top: y, behavior: REDUIT ? 'auto' : 'smooth' });
      history.replaceState(null, '', a.getAttribute('href'));
      cible.setAttribute('tabindex', '-1');
      cible.focus({ preventScroll: true });
    });
  });
})();
