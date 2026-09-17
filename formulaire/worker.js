/* ============================================================================
   Formulaire d'audit : réception des demandes et envoi par e-mail.
   Cloudflare Worker, appelé par assets/quantum.js (POST JSON).

   Secrets attendus (wrangler secret put) :
     RESEND_API_KEY   clé Resend dédiée à ce site
   Variables (wrangler.toml) :
     DESTINATAIRE, EXPEDITEUR, ORIGINES_AUTORISEES
   ========================================================================== */

const CHAMPS = ['nom', 'email', 'entreprise', 'message', 'source', 'page', 'timestamp'];

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
  return `<div style="font-family:system-ui,sans-serif;max-width:560px">
  <p style="font:13px monospace;letter-spacing:.1em;text-transform:uppercase;color:#6d28d9;margin:0 0 4px">Nouvelle demande d'audit</p>
  <h1 style="font-size:22px;margin:0 0 20px;color:#111318">${echappe(d.entreprise) || 'Entreprise non précisée'}</h1>
  <table style="border-collapse:collapse">
    ${ligne('Nom', d.nom)}${ligne('E-mail', d.email)}${ligne('Entreprise', d.entreprise)}
    ${ligne('Besoin', d.message)}${ligne('Page', d.page)}${ligne('Envoyé le', d.timestamp)}
  </table>
  <p style="margin:24px 0 0;color:#6b7280;font-size:13px">Répondre à ce message écrit directement au visiteur.</p>
</div>`;
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
    if (!nom || !entreprise || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      return reponse({ erreur: 'Champs manquants ou e-mail invalide' }, 400, origine);
    }
    if (nom.length > 120 || email.length > 160 || entreprise.length > 160 || String(data.message || '').length > 2000) {
      return reponse({ erreur: 'Champ trop long' }, 400, origine);
    }

    const propre = {};
    for (const c of CHAMPS) propre[c] = typeof data[c] === 'string' ? data[c].slice(0, 2000) : '';

    /* L'e-mail part avant la réponse : le visiteur ne lit « demande reçue »
       que si la demande est réellement partie. */
    const envoi = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: env.EXPEDITEUR,
        to: [env.DESTINATAIRE],
        reply_to: propre.email,
        subject: `Demande d'audit : ${propre.entreprise || propre.nom}`,
        html: corpsEmail(propre),
      }),
    });

    if (!envoi.ok) {
      console.error('Resend', envoi.status, await envoi.text());
      return reponse({ erreur: "L'envoi a échoué" }, 502, origine);
    }
    return reponse({ ok: true }, 200, origine);
  },
};
