/* ============================================================================
   Formulaire d'audit : réception des demandes et envoi par e-mail.
   Cloudflare Worker, appelé par assets/quantum.js (POST JSON).

   Secrets attendus (wrangler secret put) :
     RESEND_API_KEY   clé Resend dédiée à ce site
   Variables (wrangler.toml) :
     DESTINATAIRE, EXPEDITEUR, ORIGINES_AUTORISEES
   ========================================================================== */

const CHAMPS = ['nom', 'email', 'entreprise', 'message', 'source', 'page', 'timestamp', 'type'];

/* Le Worker répond à des navigateurs sur nos deux domaines uniquement. Une
   origine inconnue ne reçoit aucun en-tête CORS, donc le navigateur bloque. */
function origineAutorisee(request, env) {
  const origine = request.headers.get('Origin') || '';
  const liste = (env.ORIGINES_AUTORISEES || '').split(',').map((o) => o.trim()).filter(Boolean);
  return liste.includes(origine) ? origine : null;
}

function entetes(origine) {
  return {
    'Access-Control-Allow-Origin': origine,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

function reponse(objet, statut, origine) {
  return new Response(JSON.stringify(objet), {
    status: statut,
    headers: { 'Content-Type': 'application/json', ...(origine ? entetes(origine) : {}) },
  });
}

function echappe(valeur) {
  return String(valeur == null ? '' : valeur)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function corpsEmail(d) {
  const ligne = (label, valeur) => valeur
    ? `<tr><td style="padding:6px 16px 6px 0;color:#6b7280;font:12px monospace;text-transform:uppercase;letter-spacing:.08em;vertical-align:top">${label}</td><td style="padding:6px 0;color:#111318;font:15px system-ui">${echappe(valeur)}</td></tr>`
    : '';
  var siteOffert = d.type === 'site-offert';
  return `<div style="font-family:system-ui,sans-serif;max-width:560px">
  <p style="font:13px monospace;letter-spacing:.1em;text-transform:uppercase;color:#6d28d9;margin:0 0 4px">${siteOffert ? 'Demande de site vitrine offert' : "Nouvelle demande d'audit"}</p>
  <h1 style="font-size:22px;margin:0 0 20px;color:#111318">${echappe(d.entreprise) || echappe(d.email) || 'Entreprise non précisée'}</h1>
  <table style="border-collapse:collapse">
    ${ligne('Nom', d.nom)}${ligne('E-mail', d.email)}${ligne('Entreprise', d.entreprise)}
    ${ligne('Besoin', d.message)}${ligne('Page', d.page)}${ligne('Envoyé le', d.timestamp)}
  </table>
  <p style="margin:24px 0 0;color:#6b7280;font-size:13px">Répondre à ce message écrit directement au visiteur.</p>
</div>`;
}

/* Accusé envoyé au visiteur qui demande le site offert. Il décrit le déroulé
   et propose l'audit en fin de message, par un lien de réservation, sans en
   faire une contrepartie. */
function corpsAccuse(env) {
  const etape = (jour, texte) =>
    `<tr><td style="padding:0 16px 11px 0;font:11px monospace;letter-spacing:.08em;color:#6d28d9;white-space:nowrap;vertical-align:top">${jour}</td><td style="padding:0 0 11px;color:#111318;font:15px/1.6 system-ui">${texte}</td></tr>`;
  return `<div style="font-family:system-ui,sans-serif;max-width:560px;color:#111318;font-size:15px;line-height:1.62">
  <p>Bonjour,</p>
  <p>Merci pour votre demande. Voici précisément ce que nous offrons et comment cela se déroule.</p>
  <p><b>Ce que contient le site</b><br>Une page claire qui présente votre entreprise : votre activité, vos services, vos coordonnées, et un formulaire de contact qui vous écrit directement. Lisible sur téléphone, rapide, à votre nom de domaine si vous en avez un.</p>
  <p><b>Le déroulé</b></p>
  <table style="border-collapse:collapse;margin-bottom:13px">
    ${etape('JOUR 1', 'Vous répondez à ce message avec le nom de votre entreprise, ce que vous faites et vos coordonnées.')}
    ${etape('JOUR 3', 'Nous vous envoyons une première version. Vous demandez les corrections que vous voulez.')}
    ${etape('JOUR 5', 'Le site est en ligne. Vous en gardez la propriété, sans abonnement ni contrepartie.')}
  </table>
  <p style="font-size:13.5px;color:rgba(17,19,24,.62)">Vous n'avez rien à installer, rien à signer, et vous pouvez arrêter à n'importe quel moment.</p>
  <p style="margin-top:22px;font-size:13.5px;line-height:1.5"><b>Quantum Consulting</b><br><span style="color:rgba(17,19,24,.55)">Conseil et formation en intelligence artificielle<br>Paris · ${env.DESTINATAIRE}</span></p>
  <div style="border-top:1px solid rgba(17,19,24,.14);margin-top:22px;padding-top:16px;font-size:13.5px;color:rgba(17,19,24,.72)">
    <p style="margin:0 0 12px">Nous aidons aussi les PME à automatiser les tâches qui reviennent chaque semaine : factures, relances, devis, comptes rendus. Si le sujet vous intéresse, réservez trente minutes au moment qui vous arrange, sans engagement.</p>
    <a href="${env.LIEN_RENDEZ_VOUS}" style="display:inline-block;background:#6d28d9;color:#ffffff;text-decoration:none;font:700 12.5px monospace;padding:12px 18px">Réserver un créneau →</a>
  </div>
</div>`;
}

/* Plafonds de l'accusé au visiteur. Le Worker écrit à une adresse fournie par
   l'appelant : sans plafond, il servirait à envoyer des e-mails en notre nom à
   n'importe qui. L'en-tête d'origine ne protège de rien, il se falsifie en une
   ligne de commande.
   Dépasser un plafond n'échoue jamais la demande : le prospect est enregistré
   et nous sommes prévenus, seul l'accusé automatique est retenu. */
const PLAFOND_IP = 3;      // accusés par adresse IP et par heure
const PLAFOND_JOUR = 60;   // accusés pour l'ensemble du site et par jour

async function accuseAutorise(env, ip) {
  if (!env.COMPTEURS) return true;
  const jour = 'jour:' + new Date().toISOString().slice(0, 10);
  const cleIp = 'ip:' + ip;
  try {
    const [nJour, nIp] = await Promise.all([env.COMPTEURS.get(jour), env.COMPTEURS.get(cleIp)]);
    if (Number(nJour || 0) >= PLAFOND_JOUR || Number(nIp || 0) >= PLAFOND_IP) return false;
    await Promise.all([
      env.COMPTEURS.put(jour, String(Number(nJour || 0) + 1), { expirationTtl: 172800 }),
      env.COMPTEURS.put(cleIp, String(Number(nIp || 0) + 1), { expirationTtl: 3600 }),
    ]);
    return true;
  } catch (e) {
    /* Compteur indisponible : on écrit quand même au visiteur, une demande
       légitime ne doit pas rester sans réponse à cause de notre plomberie. */
    console.error('Compteurs', e);
    return true;
  }
}

function envoyer(env, message) {
  return fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(message),
  });
}

export default {
  async fetch(request, env) {
    const origine = origineAutorisee(request, env);

    if (request.method === 'OPTIONS') {
      return origine
        ? new Response(null, { status: 204, headers: entetes(origine) })
        : new Response(null, { status: 403 });
    }
    if (request.method !== 'POST') return new Response('Méthode non autorisée', { status: 405 });
    if (!origine) return new Response('Origine non autorisée', { status: 403 });

    let data;
    try {
      data = await request.json();
    } catch {
      return reponse({ erreur: 'JSON invalide' }, 400, origine);
    }

    /* Champ piège : invisible pour un visiteur, rempli par les robots. On
       répond 200 pour ne pas leur indiquer qu'ils ont été repérés. */
    if (data.site_web) return reponse({ ok: true }, 200, origine);

    const nom = String(data.nom || '').trim();
    const email = String(data.email || '').trim();
    const entreprise = String(data.entreprise || '').trim();
    /* La fenêtre du site offert ne demande qu'une adresse : exiger le nom et
       l'entreprise la rendrait inutilisable. Le formulaire complet, lui, garde
       ses trois champs obligatoires. */
    const siteOffert = data.type === 'site-offert';
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || (!siteOffert && (!nom || !entreprise))) {
      return reponse({ erreur: 'Champs manquants ou e-mail invalide' }, 400, origine);
    }
    if (nom.length > 120 || email.length > 160 || entreprise.length > 160 || String(data.message || '').length > 2000) {
      return reponse({ erreur: 'Champ trop long' }, 400, origine);
    }

    const propre = {};
    for (const c of CHAMPS) propre[c] = typeof data[c] === 'string' ? data[c].slice(0, 2000) : '';

    /* L'e-mail part avant la réponse : le visiteur ne lit « demande reçue »
       que si la demande est réellement partie. */
    const envoi = await envoyer(env, {
      from: env.EXPEDITEUR,
      to: [env.DESTINATAIRE],
      reply_to: propre.email,
      subject: siteOffert
        ? `Site offert : ${propre.email}`
        : `Demande d'audit : ${propre.entreprise || propre.nom}`,
      html: corpsEmail(propre),
    });

    if (!envoi.ok) {
      console.error('Resend', envoi.status, await envoi.text());
      return reponse({ erreur: "L'envoi a échoué" }, 502, origine);
    }

    /* L'accusé au visiteur ne conditionne pas la réponse : la demande est
       déjà entre nos mains, un échec ici ne doit pas la faire réessayer. */
    if (siteOffert && await accuseAutorise(env, request.headers.get('CF-Connecting-IP') || 'inconnue')) {
      const accuse = await envoyer(env, {
        from: env.EXPEDITEUR,
        to: [propre.email],
        reply_to: env.DESTINATAIRE,
        subject: 'Votre site vitrine offert : ce qui vous attend',
        html: corpsAccuse(env),
      });
      if (!accuse.ok) console.error('Accusé', accuse.status, await accuse.text());
    }

    return reponse({ ok: true }, 200, origine);
  },
};
