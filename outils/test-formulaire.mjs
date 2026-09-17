/* Tests du Worker du formulaire, sans réseau : node outils/test-formulaire.mjs */
import worker from '../formulaire/worker.js';

const env = {
  RESEND_API_KEY: 'test_key',
  DESTINATAIRE: 'contact@quantum-agency.fr',
  EXPEDITEUR: 'Site Quantum <formulaire@quantum-agency.fr>',
  ORIGINES_AUTORISEES: 'https://quantum-agency.fr,https://www.quantum-agency.fr',
  LIEN_RENDEZ_VOUS: 'https://calendly.com/younes_mh/audit',
};

let dernierAppel = null;
let appels = [];
let resendOk = true;
globalThis.fetch = async (url, init) => {
  dernierAppel = { url, body: JSON.parse(init.body), auth: init.headers.Authorization };
  appels.push(dernierAppel);
  return resendOk
    ? new Response('{"id":"x"}', { status: 200 })
    : new Response('boom', { status: 401 });
};

const post = (body, origin = 'https://quantum-agency.fr') =>
  new Request('https://api.test/', { method: 'POST', headers: { Origin: origin, 'Content-Type': 'application/json' }, body: JSON.stringify(body) });

const valide = { nom: 'Jeanne Dupont', email: 'jeanne@entreprise.fr', entreprise: 'ACME', message: 'Les relances', source: 'quantum-agency.fr', page: '/contact.html', timestamp: '2026-09-17T08:00:00.000Z' };
let ko = 0;
const t = async (nom, fn) => { try { await fn(); console.log('  ok  ', nom); } catch (e) { ko++; console.log('  ÉCHEC', nom, '->', e.message); } };
const eq = (a, b, m) => { if (a !== b) throw new Error(`${m}: ${a} != ${b}`); };

await t('POST valide -> 200 + CORS + Resend appelé', async () => {
  const r = await worker.fetch(post(valide), env);
  eq(r.status, 200, 'statut');
  eq(r.headers.get('Access-Control-Allow-Origin'), 'https://quantum-agency.fr', 'CORS');
  eq(dernierAppel.url, 'https://api.resend.com/emails', 'url resend');
  eq(dernierAppel.body.reply_to, 'jeanne@entreprise.fr', 'reply_to');
  eq(dernierAppel.body.subject, "Demande d'audit : ACME", 'sujet');
  if (!dernierAppel.body.html.includes('Les relances')) throw new Error('message absent du corps');
});

await t('préflight OPTIONS origine connue -> 204', async () => {
  const r = await worker.fetch(new Request('https://api.test/', { method: 'OPTIONS', headers: { Origin: 'https://www.quantum-agency.fr' } }), env);
  eq(r.status, 204, 'statut');
  eq(r.headers.get('Access-Control-Allow-Origin'), 'https://www.quantum-agency.fr', 'CORS');
});

await t('origine étrangère -> 403 sans CORS', async () => {
  const r = await worker.fetch(post(valide, 'https://mechant.fr'), env);
  eq(r.status, 403, 'statut');
  eq(r.headers.get('Access-Control-Allow-Origin'), null, 'pas de CORS');
});

await t('e-mail invalide -> 400', async () => {
  const r = await worker.fetch(post({ ...valide, email: 'pasunemail' }), env);
  eq(r.status, 400, 'statut');
});

await t('champ obligatoire vide -> 400', async () => {
  const r = await worker.fetch(post({ ...valide, entreprise: '  ' }), env);
  eq(r.status, 400, 'statut');
});

await t('champ piège rempli -> 200 sans envoi', async () => {
  dernierAppel = null;
  const r = await worker.fetch(post({ ...valide, site_web: 'http://spam' }), env);
  eq(r.status, 200, 'statut');
  eq(dernierAppel, null, 'aucun e-mail envoyé');
});

await t('échappement HTML dans le corps', async () => {
  await worker.fetch(post({ ...valide, entreprise: '<script>alert(1)</script>' }), env);
  if (dernierAppel.body.html.includes('<script>')) throw new Error('balise non échappée');
});

await t('Resend en panne -> 502, pas de faux succès', async () => {
  resendOk = false;
  const r = await worker.fetch(post(valide), env);
  eq(r.status, 502, 'statut');
  resendOk = true;
});

await t('site offert : e-mail seul accepté', async () => {
  appels = [];
  const r = await worker.fetch(post({ email: 'jeanne@entreprise.fr', type: 'site-offert', page: '/services.html' }), env);
  eq(r.status, 200, 'statut');
  /* appels[0] est la notification interne, appels[1] l'accusé au visiteur. */
  eq(appels[0].body.to[0], 'contact@quantum-agency.fr', 'destinataire interne');
  eq(appels[0].body.subject, 'Site offert : jeanne@entreprise.fr', 'sujet');
  if (!appels[0].body.html.includes('site vitrine offert')) throw new Error('intitulé absent du corps');
});

await t('site offert : e-mail invalide toujours refusé', async () => {
  const r = await worker.fetch(post({ email: 'pasunemail', type: 'site-offert' }), env);
  eq(r.status, 400, 'statut');
});

await t('formulaire complet : nom et entreprise restent obligatoires', async () => {
  const r = await worker.fetch(post({ email: 'jeanne@entreprise.fr' }), env);
  eq(r.status, 400, 'statut');
});

await t('site offert : accusé envoyé au visiteur avec le lien de rendez-vous', async () => {
  appels = [];
  await worker.fetch(post({ email: 'jeanne@entreprise.fr', type: 'site-offert' }), env);
  eq(appels.length, 2, 'deux e-mails');
  const accuse = appels[1].body;
  eq(accuse.to[0], 'jeanne@entreprise.fr', 'destinataire');
  eq(accuse.reply_to, 'contact@quantum-agency.fr', 'reply_to');
  eq(accuse.subject, 'Votre site vitrine offert : ce qui vous attend', 'sujet');
  if (!accuse.html.includes('https://calendly.com/younes_mh/audit')) throw new Error('lien de rendez-vous absent');
  if (!accuse.html.includes('JOUR 3')) throw new Error('déroulé absent');
});

await t('demande d\'audit classique : aucun accusé au visiteur', async () => {
  appels = [];
  await worker.fetch(post(valide), env);
  eq(appels.length, 1, 'un seul e-mail');
});

await t('accusé en échec : la demande reste acceptée', async () => {
  let n = 0;
  globalThis.fetch = async (url, init) => {
    n++; dernierAppel = { url, body: JSON.parse(init.body) };
    return n === 1 ? new Response('{"id":"x"}', { status: 200 }) : new Response('boom', { status: 500 });
  };
  const r = await worker.fetch(post({ email: 'jeanne@entreprise.fr', type: 'site-offert' }), env);
  eq(r.status, 200, 'statut');
  globalThis.fetch = async (url, init) => { dernierAppel = { url, body: JSON.parse(init.body) }; appels.push(dernierAppel); return new Response('{"id":"x"}', { status: 200 }); };
});

await t('plafond atteint : la demande passe, sans accusé au visiteur', async () => {
  const compteurs = { 'ip:1.2.3.4': '3' };
  const envPlein = Object.assign({}, env, { COMPTEURS: {
    get: async (k) => compteurs[k] || null,
    put: async (k, v) => { compteurs[k] = v; },
  } });
  appels = [];
  const req = new Request('https://api.test/', { method: 'POST', headers: { Origin: 'https://quantum-agency.fr', 'Content-Type': 'application/json', 'CF-Connecting-IP': '1.2.3.4' }, body: JSON.stringify({ email: 'jeanne@entreprise.fr', type: 'site-offert' }) });
  const r = await worker.fetch(req, envPlein);
  eq(r.status, 200, 'statut');
  eq(appels.length, 1, 'notification interne seule');
});

await t('sous le plafond : accusé envoyé et compteurs incrémentés', async () => {
  const compteurs = {};
  const envVide = Object.assign({}, env, { COMPTEURS: {
    get: async (k) => compteurs[k] || null,
    put: async (k, v) => { compteurs[k] = v; },
  } });
  appels = [];
  const req = new Request('https://api.test/', { method: 'POST', headers: { Origin: 'https://quantum-agency.fr', 'Content-Type': 'application/json', 'CF-Connecting-IP': '5.6.7.8' }, body: JSON.stringify({ email: 'jeanne@entreprise.fr', type: 'site-offert' }) });
  await worker.fetch(req, envVide);
  eq(appels.length, 2, 'deux e-mails');
  eq(compteurs['ip:5.6.7.8'], '1', 'compteur IP');
});

await t('GET -> 405', async () => {
  const r = await worker.fetch(new Request('https://api.test/', { method: 'GET', headers: { Origin: 'https://quantum-agency.fr' } }), env);
  eq(r.status, 405, 'statut');
});

console.log(ko === 0 ? '\nTous les tests passent.' : `\n${ko} test(s) en échec.`);
process.exit(ko === 0 ? 0 : 1);
