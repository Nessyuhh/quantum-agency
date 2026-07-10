// i18n.js — Quantum Consulting · Bilingual FR ↔ EN
(function () {
  'use strict';

  // ──────────────────────────────────────────────────────────────────
  //  DICTIONARY  (keys = FR trimmed text, values = EN translation)
  // ──────────────────────────────────────────────────────────────────
  const EN = {

    // ── Skip link ─────────────────────────────────────────────────
    'Aller au contenu principal': 'Skip to main content',

    // ── SHARED NAVIGATION ─────────────────────────────────────────
    'Nos services': 'Our Services',
    'Formations': 'Training',
    'Audit gratuit →': 'Free Audit →',
    'RDV gratuit →': 'Free Meeting →',

    // Nav dropdown — Services
    'Audit IA': 'AI Audit',
    'Priorité': 'Priority',
    'Intégration IA': 'AI Integration',
    'Automatisation': 'Automation',
    'Agents IA & LLM privés': 'AI Agents & Private LLMs',
    'Conseil stratégique →': 'Strategic Advisory →',
    'Diagnostic': 'Diagnostic',

    // Nav dropdown — Formations
    'Initiation à l\'IA': 'AI Introduction',
    'Niv. 1': 'Level 1',
    'Maîtrise & Automatisation': 'Mastery & Automation',
    'Niv. 2': 'Level 2',
    'Expert & Stratégie IA': 'Expert & AI Strategy',
    'Niv. 3': 'Level 3',
    'Voir toutes les formations →': 'View all training →',

    // Secondary pages — nav full-text variants
    'Audit IA Diagnostic': 'AI Audit',
    'Agents IA LLM privé': 'AI Agents & Private LLMs',
    'Initiation à l\'IA Niv. 1': 'AI Introduction Level 1',
    'Maîtrise & Automatisation Niv. 2': 'Mastery & Automation Level 2',
    'Expert & Stratégie IA Niv. 3': 'Expert & AI Strategy Level 3',
    'Conseil stratégique': 'Strategic Advisory',
    'Consulting': 'Consulting',
    'Blog': 'Blog',
    'Contact': 'Contact',
    'FAQ': 'FAQ',

    // Mobile menu
    'Accueil': 'Home',
    'Services': 'Services',
    'Demander un audit gratuit →': 'Request a free audit →',
    'Demander un devis gratuit →': 'Request a free quote →',
    'Démarrer le programme →': 'Start the program →',

    // Bottom tab bar
    'Audit': 'Audit',
    'Audit →': 'Audit →',
    'Formation': 'Training',

    // Breadcrumbs
    'Accueil›': 'Home›',
    'Formations›': 'Training›',
    'Services›': 'Services›',
    'Conseil': 'Advisory',
    'Consulting IA': 'AI Consulting',
    'Cas d\'usage IA par secteur': 'AI Use Cases by Sector',
    'Comparatif modèles LLM': 'LLM Model Comparison',
    'FAQ IA': 'AI FAQ',

    // ── INDEX — Hero ──────────────────────────────────────────────
    'Cabinet de conseil IA · Transformation des entreprises':
      'AI Consulting Firm · Business Transformation',
    'Transformez': 'Transform',
    'vos': 'your',
    'processus.': 'business.',
    'Libérez': 'Unlock',
    'votre': 'your',
    'potentiel IA.': 'AI potential.',
    'De l\'audit de vos opportunités à l\'intégration des meilleurs modèles. Une approche sur mesure pour PME, ETI et grands groupes. Résultats mesurables en 6 semaines.':
      'From auditing your AI opportunities to integrating the best models. A tailored approach for SMBs, mid-market companies and large enterprises. Measurable results in 6 weeks.',
    'Découvrir notre approche': 'Discover our approach',
    'Scroller': 'Scroll',

    // Hero chat widget
    'Identifie nos 3 processus à automatiser en priorité':
      'Identify our 3 priority processes to automate',
    'Analyse terminée : 3 leviers identifiés :': 'Analysis complete: 3 levers identified:',
    '1. Qualification leads → +22% taux transfo': '1. Lead qualification → +22% conversion rate',
    '2. Reporting mensuel → −85% temps manuel':   '2. Monthly reporting → −85% manual time',
    '3. SAV tier-1 → agent IA autonome 24/7':     '3. Tier-1 support → autonomous AI agent 24/7',
    'Génère la feuille de route et le ROI estimé': 'Generate the roadmap and estimated ROI',

    // ── INDEX — Trust bar ─────────────────────────────────────────
    '15 000€ d\'économies identifiées en audit moyen': '€15,000 avg. savings identified per audit',
    'Commerce & Distribution':          'Retail & Distribution',
    '−40% de tâches répétitives automatisables': '−40% repetitive tasks automatable',
    'Industrie & Production':           'Industry & Manufacturing',
    'ROI mesurable en 6 semaines':      'Measurable ROI in 6 weeks',
    'Finance & Comptabilité':           'Finance & Accounting',
    'Neutralité multi-modèles (10+ LLMs maîtrisés)': 'Multi-model neutrality (10+ LLMs mastered)',
    'Santé & Juridique':                'Healthcare & Legal',
    'PME · ETI · Grands groupes':       'SMBs · Mid-market · Large enterprises',
    'RH · Logistique · Marketing':      'HR · Logistics · Marketing',

    // ── INDEX — Expertises ────────────────────────────────────────
    'Nos expertises': 'Our Expertise',
    'Un accompagnement complet,': 'End-to-end support,',
    'de l\'audit à la production': 'from audit to production',
    'Nous intervenons sur l\'ensemble de la chaîne de transformation IA - de la cartographie de vos processus jusqu\'au déploiement en production et la formation de vos équipes.':
      'We cover the entire AI transformation chain — from mapping your processes to production deployment and team training.',
    'Agents IA': 'AI Agents',
    'Formation executive': 'Executive Training',
    'En savoir plus →': 'Learn more →',
    'Découvrir →': 'Discover →',
    'Diagnostic complet de vos processus métier, cartographie des opportunités d\'automatisation et feuille de route ROI sur 12 mois.':
      'Complete diagnostic of your business processes, mapping of automation opportunities and 12-month ROI roadmap.',
    'Accompagnement des dirigeants et comités de direction pour construire et piloter une stratégie IA cohérente avec vos objectifs business.':
      'Support for executives and boards to build and steer an AI strategy aligned with your business objectives.',
    'Déploiement d\'assistants, copilotes, bases documentaires RAG et connecteurs dans vos outils existants (CRM, ERP, Drive, Teams).':
      'Deployment of assistants, copilots, RAG document bases and connectors into your existing tools (CRM, ERP, Drive, Teams).',
    'Automatisation de vos workflows via Make, n8n, API et protocoles MCP. Compatible avec l\'ensemble de vos outils métier.':
      'Workflow automation via Make, n8n, APIs and MCP protocols. Compatible with your entire business toolset.',
    'Conception et déploiement d\'agents IA autonomes et de LLM privés hébergés selon vos contraintes de confidentialité et de souveraineté.':
      'Design and deployment of autonomous AI agents and private LLMs hosted to your privacy and sovereignty requirements.',
    'Formations sur mesure pour dirigeants, managers et équipes métier, organisées en partenariat avec nos organismes de formation certifiés.':
      'Tailored training for executives, managers and business teams, organized in partnership with our certified training organizations.',

    // ── INDEX — Stats ─────────────────────────────────────────────
    'd\'économies identifiées en audit moyen':   'avg. savings identified per audit',
    'de tâches répétitives automatisables':       'repetitive tasks automatable',
    'pour un premier ROI mesurable':              'to first measurable ROI',
    'modèles IA maîtrisés et déployés':           'AI models mastered and deployed',

    // ── INDEX — LLM matrix ────────────────────────────────────────
    'Ecosystème IA': 'AI Ecosystem',
    'Nous sélectionnons le': 'We select the',
    'meilleur modèle': 'best model',
    'pour chaque besoin': 'for every use case',
    'Chaque LLM excelle dans sa zone d\'action. Notre expertise multi-modèles vous garantit le choix optimal selon vos contraintes techniques, budgétaires et réglementaires.':
      'Every LLM excels in its zone. Our multi-model expertise guarantees the optimal choice for your technical, budget and regulatory constraints.',
    'Raisonnement & Analyse':         'Reasoning & Analysis',
    'Analyse complexe & audit':       'Complex analysis & audit',
    'Synthèse de documents, audit de processus, raisonnement multi-étapes, génération de rapports.':
      'Document synthesis, process audit, multi-step reasoning, report generation.',
    'Génération de code':             'Code Generation',
    'Intégrations & automatisation':  'Integrations & automation',
    'Développement d\'API, scripts d\'automatisation, connecteurs métier, tests et débogage.':
      'API development, automation scripts, business connectors, testing and debugging.',
    'Recherche & RAG':                'Search & RAG',
    'Bases documentaires & veille':   'Document bases & monitoring',
    'Recherche temps réel, bases documentaires RAG, FAQ IA, veille concurrentielle et réglementaire.':
      'Real-time search, RAG document bases, AI FAQ, competitive and regulatory monitoring.',
    'Souveraineté on-premise':        'On-premise Sovereignty',
    'Déploiement local & RGPD':       'Local deployment & GDPR',
    'Données sensibles, hébergement on-premise, conformité RGPD, secteurs régulés (santé, finance, défense).':
      'Sensitive data, on-premise hosting, GDPR compliance, regulated sectors (healthcare, finance, defense).',
    'Multimodal':                     'Multimodal',
    'Image, audio & vidéo':           'Image, audio & video',
    'Analyse d\'images produits, transcription, traitement multimodal, génération visuelle pour les équipes.':
      'Product image analysis, transcription, multimodal processing, visual generation for teams.',
    'Agents autonomes':               'Autonomous Agents',
    'Orchestration & workflows':      'Orchestration & workflows',
    'Agents autonomes, chaînes d\'actions complexes, orchestration multi-agents, tâches longue durée.':
      'Autonomous agents, complex action chains, multi-agent orchestration, long-running tasks.',
    'Copilote métier':                'Business Copilot',
    'Office, CRM & ERP':              'Office, CRM & ERP',
    'Intégration native dans l\'écosystème Microsoft 365, Google Workspace, Salesforce et autres suites métier.':
      'Native integration into Microsoft 365, Google Workspace, Salesforce and other business suites.',
    'Volume & coût optimisé':         'Volume & cost optimized',
    'Traitement massif & scale':      'Bulk processing & scale',
    'Classification à grande échelle, traitement de volumes, tâches répétitives, optimisation du coût par token.':
      'Large-scale classification, volume processing, repetitive tasks, per-token cost optimization.',

    // ── INDEX — Consulting teaser ─────────────────────────────────
    'Notre processus': 'Our Process',
    'Un accompagnement structuré,': 'Structured support,',
    'de l\'audit aux résultats': 'from audit to results',
    'Chaque mission commence par comprendre vos processus. Nous identifions les leviers IA à fort ROI, sélectionnons les modèles adaptés et assurons l\'intégration jusqu\'à l\'adoption complète par vos équipes.':
      'Every engagement starts by understanding your processes. We identify high-ROI AI levers, select the right models and ensure integration through full team adoption.',
    'Audit & cartographie IA': 'AI Audit & mapping',
    'Analyse de vos processus pour identifier les gains rapides, les leviers d\'automatisation et les opportunités à fort ROI. Livrable : feuille de route priorisée.':
      'Analysis of your processes to identify quick wins, automation levers and high-ROI opportunities. Deliverable: prioritized roadmap.',
    'Sélection & intégration des modèles': 'Model selection & integration',
    'Choix du ou des modèles adaptés à vos besoins, déploiement en production et connexion à vos outils métier existants.':
      'Selecting the right model(s) for your needs, production deployment and connection to your existing business tools.',
    'Conduite du changement': 'Change management',
    'Accompagnement de l\'adoption par vos équipes : formation, documentation, suivi des résultats et optimisation continue.':
      'Supporting your teams\' adoption: training, documentation, results monitoring and continuous optimization.',
    'En savoir plus sur notre approche →': 'Learn more about our approach →',
    'Voir nos cas clients →': 'View our client cases →',

    // ── INDEX — Formations section ────────────────────────────────
    'Nos formations': 'Our Training Programs',
    'Initiation': 'Introduction',
    'Niv. 1 · Débutant': 'Level 1 · Beginner',
    'Maîtrise': 'Mastery',
    'Niv. 2 · Intermédiaire': 'Level 2 · Intermediate',
    'Expert': 'Expert',
    'Niv. 3 · Avancé': 'Level 3 · Advanced',
    'Demander un devis →': 'Request a quote →',
    'Journée complète': 'Full day',
    'Demi-journée': 'Half-day',
    '2 à 3 jours': '2 to 3 days',
    'Programme sur mesure': 'Custom program',

    // ── INDEX — Testimonials ──────────────────────────────────────
    'Vérifié ✓': 'Verified ✓',
    'Ce que nos clients disent': 'What our clients say',

    // ── INDEX — FAQ ───────────────────────────────────────────────
    'Vos questions,': 'Your questions,',
    'nos réponses': 'our answers',
    'Qu\'est-ce qu\'un audit IA et que couvre-t-il concrètement ?':
      'What is an AI audit and what does it actually cover?',
    'L\'audit IA est une analyse complète de vos processus métier pour identifier les opportunités d\'automatisation et les leviers à fort ROI. Il couvre : cartographie des tâches répétitives, évaluation des outils IA adaptés, analyse de vos données et systèmes existants, et livraison d\'une feuille de route priorisée sur 12 mois avec estimations de ROI.':
      'An AI audit is a comprehensive analysis of your business processes to identify automation opportunities and high-ROI levers. It covers: mapping repetitive tasks, evaluating suitable AI tools, analyzing your existing data and systems, and delivering a prioritized 12-month roadmap with ROI estimates.',
    'Quels modèles d\'IA utilisez-vous et pourquoi cette approche multi-modèles ?':
      'Which AI models do you use and why this multi-model approach?',
    'Nous travaillons avec l\'ensemble de l\'écosystème IA : Claude (Anthropic) et GPT-4o (OpenAI) pour le raisonnement complexe, Mistral AI et Meta Llama pour les déploiements souverains on-premise, Google Gemini et Perplexity pour la recherche documentaire, Microsoft Copilot pour les environnements Microsoft. Chaque modèle a ses zones d\'excellence. Notre valeur ajoutée est de sélectionner le bon outil pour le bon usage, sans dépendance à un fournisseur unique.':
      'We work across the full AI ecosystem: Claude (Anthropic) and GPT-4o (OpenAI) for complex reasoning, Mistral AI and Meta Llama for sovereign on-premise deployments, Google Gemini and Perplexity for document research, Microsoft Copilot for Microsoft environments. Each model has its zones of excellence. Our value is selecting the right tool for the right use case, with no single-vendor dependency.',
    'Quelle est la durée d\'une mission et comment se déroule-t-elle ?':
      'How long does an engagement last and how does it work?',
    'Un audit IA complet se déroule en 2 à 4 semaines selon la taille de votre organisation. Les missions d\'intégration et d\'automatisation durent 1 à 3 mois. Nos accompagnements stratégiques sur 12 mois incluent des comités mensuels. Chaque mission commence par un appel de découverte gratuit de 30 minutes pour évaluer votre situation avant tout engagement.':
      'A full AI audit runs 2 to 4 weeks depending on your organization\'s size. Integration and automation engagements last 1 to 3 months. Our 12-month strategic programs include monthly steering committees. Every engagement begins with a free 30-minute discovery call to assess your situation before any commitment.',
    'Proposez-vous des formations IA pour nos équipes ?':
      'Do you offer AI training for our teams?',
    'Oui. Nos formations executive (initiation, maîtrise et expert) sont organisées en intra-entreprise en partenariat avec nos organismes de formation certifiés. Elles sont conçues pour les dirigeants, managers et équipes opérationnelles, avec des cas pratiques adaptés à votre secteur. Les formations peuvent être intégrées dans une mission d\'accompagnement ou commandées séparément via vos OF partenaires.':
      'Yes. Our executive training (introduction, mastery and expert) is organized in-company in partnership with our certified training organizations. Designed for executives, managers and operational teams, with sector-specific practical cases. Training can be integrated into a consulting engagement or ordered separately through your partner training organizations.',

    // ── INDEX — CTA ───────────────────────────────────────────────
    'Passez à l\'action': 'Take action',
    'Prêt à identifier vos opportunités IA ?': 'Ready to identify your AI opportunities?',
    'Réservez un audit de découverte gratuit de 30 minutes. Nous analysons ensemble vos processus clés et vous présentons les leviers d\'optimisation IA les plus pertinents, sans engagement.':
      'Book a free 30-minute discovery audit. We analyze your key processes together and present the most relevant AI optimization levers, with no commitment.',
    'Nous écrire': 'Email us',

    // ── FOOTER ────────────────────────────────────────────────────
    'Cabinet de conseil spécialisé dans la transformation des entreprises par l\'Intelligence Artificielle. Audit, intégration, automatisation, agents IA et formation executive.':
      'Consulting firm specializing in business transformation through Artificial Intelligence. Audit, integration, automation, AI agents and executive training.',
    'Blog IA': 'AI Blog',
    'Expert & Stratégie': 'Expert & Strategy',
    'Prendre RDV': 'Book a call',
    '© 2026 Quantum Consulting. Tous droits réservés.': '© 2026 Quantum Consulting. All rights reserved.',
    'Conseil IA · Intégration · Automatisation · Paris': 'AI Advisory · Integration · Automation · Paris',
    '© 2026 Quantum Consulting · Cabinet de conseil IA · Transformation des entreprises · Paris, France':
      '© 2026 Quantum Consulting · AI Consulting Firm · Business Transformation · Paris, France',

    // ── CONSULTING-IA ─────────────────────────────────────────────
    'Cabinet de Conseil IA pour PME, ETI et Groupes': 'AI Consulting Firm for SMBs, Mid-market and Large Enterprises',
    'Audit Flash': 'Flash Audit',
    'Mission Implémentation': 'Implementation Mission',
    'Retainer Stratégique': 'Strategic Retainer',
    'Résultats en 2 jours': 'Results in 2 days',
    'ROI dès 4 semaines': 'ROI from 4 weeks',
    'Partenaire sur 12 mois': '12-month partner',
    '2 processus audités': '2 audited processes',
    'Diagnostic de maturité IA': 'AI maturity diagnostic',
    'Feuille de route priorisée': 'Prioritized roadmap',
    'Restitution dirigeants': 'Executive debriefing',
    'Recommandation de modèles': 'Model recommendation',
    'Analyse complète des processus': 'Complete process analysis',
    'Déploiement d\'une solution IA': 'Deployment of one AI solution',
    'Formation des équipes métier': 'Business team training',
    'Suivi et ajustements 30j': 'Follow-up and adjustments 30d',
    'Documentation et transfert de compétences': 'Documentation and skills transfer',

    // ── AUDIT-IA ──────────────────────────────────────────────────
    'Identifier vos opportunités IA à fort ROI': 'Identify your high-ROI AI opportunities',
    'Audit Flash 2j': 'Flash Audit 2d',
    'Audit Complet 2sem': 'Full Audit 2w',
    'Audit Technique DSI': 'Technical IT Audit',
    '2 jours': '2 days',
    '2 semaines': '2 weeks',
    '3 à 4 semaines': '3 to 4 weeks',

    // ── INTEGRATION-IA ────────────────────────────────────────────
    'Intégrer l\'IA dans vos outils métier': 'Integrate AI into your business tools',
    'Microsoft 365 & Copilot': 'Microsoft 365 & Copilot',
    'Google Workspace & Gemini': 'Google Workspace & Gemini',
    'CRM, ERP & outils métier': 'CRM, ERP & business tools',

    // ── AUTOMATISATION-IA ─────────────────────────────────────────
    'Automatiser vos processus avec l\'IA': 'Automate your processes with AI',
    'Workflows IA': 'AI Workflows',
    'RPA augmentée': 'Augmented RPA',
    'APIs custom': 'Custom APIs',

    // ── AGENTS-IA ─────────────────────────────────────────────────
    'Déployer des agents IA et LLM privés': 'Deploy AI agents and private LLMs',
    'Copilote RAG': 'RAG Copilot',
    'Agent autonome': 'Autonomous Agent',
    'Multi-agents': 'Multi-agent',
    'LLM privé souverain': 'Sovereign Private LLM',

    // ── FORMATIONS — Shared ───────────────────────────────────────
    'Jusqu\'à 15 participants': 'Up to 15 participants',
    'Jusqu\'à 10 participants': 'Up to 10 participants',
    'Présentiel ou distanciel': 'In-person or remote',
    'Aucun prérequis': 'No prerequisites',
    'Niveau 1 recommandé': 'Level 1 recommended',
    'Niveau 1 · Débutant': 'Level 1 · Beginner',
    'Niveau 2 · Intermédiaire': 'Level 2 · Intermediate',
    'Niveau 3 · Expert / Dirigeant': 'Level 3 · Expert / Executive',
    'Ce que couvre la formation': 'What the training covers',
    'Thèmes couverts': 'Topics covered',
    'À qui s\'adresse cette formation ?': 'Who is this training for?',
    'À qui s\'adresse ce programme ?': 'Who is this program for?',
    'Prérequis et à qui s\'adresse cette formation': 'Prerequisites and who this training is for',
    'Demander un devis gratuit →': 'Request a free quote →',

    // ── FORMATION INITIATION ──────────────────────────────────────
    'Pourquoi former vos équipes à l\'IA maintenant ?': 'Why train your teams on AI now?',
    'Gagnées en moyenne par jour par participant': 'saved per day per participant on average',
    'Taux d\'application dès la première semaine': 'Application rate from week one',
    'Résultats applicables dès le lendemain': 'Results applicable from the next day',
    'Comprendre l\'IA sans jargon technique': 'Understanding AI without technical jargon',
    'Maîtriser le prompt : l\'art de parler à l\'IA': 'Mastering prompts: the art of talking to AI',
    'Cas d\'usage pratiques selon votre métier': 'Practical use cases for your sector',
    'Atelier appliqué : vos vrais sujets': 'Applied workshop: your real topics',

    // ── FORMATION MAITRISE ────────────────────────────────────────
    'De l\'utilisation à la maîtrise : franchir le palier suivant': 'From using to mastering: crossing the next threshold',
    'Temps sur tâches répétitives en moyenne': 'time on repetitive tasks on average',
    'Plus rapide que ChatGPT basique sur les workflows': 'faster than basic ChatGPT on workflows',
    'Automatisées par jour par participant actif': 'automated per day per active participant',
    'Prompt engineering avancé': 'Advanced prompt engineering',
    'Agents IA et assistants personnalisés': 'AI agents and custom assistants',
    'Automatisation no-code avec Make et Zapier': 'No-code automation with Make and Zapier',
    'Intégration IA dans vos outils métier': 'AI integration into your business tools',
    'Mesure du ROI et déploiement': 'ROI measurement and deployment',

    // ── FORMATION EXPERT ──────────────────────────────────────────
    'La stratégie IA : un enjeu de survie pour les dirigeants de PME': 'AI strategy: a survival issue for SMB executives',
    'Mois de suivi et d\'accompagnement': 'months of monitoring and support',
    'Sessions de coaching dirigeant individuel': 'Individual executive coaching sessions',
    'Mesuré et documenté à 6 et 12 mois': 'Measured and documented at 6 and 12 months',
    'Le programme sur 12 mois': 'The 12-month program',
    'Audit & Cartographie IA': 'AI Audit & Mapping',
    'Construction de la Roadmap IA': 'Building the AI Roadmap',
    'Phase de déploiement accéléré': 'Accelerated deployment phase',
    'Consolidation & montée en puissance': 'Consolidation & scale-up',
    'ROI & Pérennisation': 'ROI & Sustainability',
    'Gouvernance, éthique & conformité RGPD': 'Governance, ethics & GDPR compliance',
    'Dirigeants & DG': 'CEOs & MDs',

    // ── CAS D'USAGE ───────────────────────────────────────────────
    'L\'IA en entreprise : cas d\'usage concrets par secteur d\'activité':
      'AI in Business: Concrete Use Cases by Industry',
    '11 secteurs · ROI mesuré': '11 sectors · Measured ROI',
    'Des exemples réels, des gains mesurés, les bons outils. Explorez comment l\'intelligence artificielle transforme chaque métier - du commerce à l\'industrie, de la santé aux ressources humaines.':
      'Real examples, measured gains, the right tools. Explore how artificial intelligence transforms every sector — from retail to industry, from healthcare to HR.',
    'Tous les secteurs': 'All sectors',
    'Commerce': 'Retail',
    'Industrie': 'Industry',
    'Services B2B': 'B2B Services',
    'Santé': 'Healthcare',
    'Finance': 'Finance',
    'Juridique': 'Legal',
    'Commerce & Retail': 'Retail & E-commerce',
    'Distribution · E-commerce · Points de vente · Marques': 'Distribution · E-commerce · POS · Brands',
    'Applications concrètes': 'Concrete applications',
    'Services aux entreprises (B2B)': 'Business Services (B2B)',
    'Cabinets conseil · Agences · ESN · BPO': 'Consulting firms · Agencies · IT services · BPO',
    'Industrie & Fabrication': 'Industry & Manufacturing',
    'Manufacturing · Supply chain · Maintenance · Qualité': 'Manufacturing · Supply chain · Maintenance · Quality',
    'Voir agents IA →': 'See AI agents →',
    'Voir automatisation →': 'See automation →',

    // ── MODELES-IA ────────────────────────────────────────────────
    'Comparatif des modèles LLM : quel IA pour quel usage en entreprise ?':
      'LLM Model Comparison: which AI for which business use case?',
    'Guide indépendant 2026': 'Independent guide 2026',
    'Notre approche : neutralité et pragmatisme': 'Our approach: neutrality and pragmatism',
    'Points forts': 'Strengths',
    'Limites à connaître': 'Limitations',

    // ── FAQ-IA ────────────────────────────────────────────────────
    'FAQ : tout comprendre sur l\'IA en entreprise': 'FAQ: Everything about AI in business',
    '40 questions, réponses d\'experts': '40 questions, expert answers',
    'Nos consultants répondent aux 40 questions les plus fréquentes sur l\'audit IA, les modèles LLM, l\'automatisation, les agents, la conformité RGPD et le ROI.':
      'Our consultants answer the 40 most frequent questions about AI audit, LLM models, automation, agents, GDPR compliance and ROI.',
    'Comprendre l\'IA en entreprise': 'Understanding AI in business',
    'Modèles LLM : choisir le bon modèle IA': 'LLM Models: choosing the right AI model',

    // ── BLOG ─────────────────────────────────────────────────────
    'Insights & Conseils IA': 'AI Insights & Advice',
    'Le blog Quantum Consulting': 'The Quantum Consulting Blog',
    'Conseils pratiques, guides et analyses sur l\'IA en entreprise, pour les décideurs et équipes opérationnelles.':
      'Practical advice, guides and analysis on AI in business, for decision-makers and operational teams.',
    'Article phare': 'Featured article',
    'Comparatif LLM': 'LLM Comparison',
    'Conformité & Souveraineté': 'Compliance & Sovereignty',
    'Stratégie IA': 'AI Strategy',
    'Lire l\'article →': 'Read the article →',
    'Lire →': 'Read →',
    'min de lecture': 'min read',

    // ── CONTACT ───────────────────────────────────────────────────
    'Appel gratuit': 'Free call',
    'Parlons de votre': 'Let\'s talk about your',
    'projet IA': 'AI project',
    '30 minutes sans engagement pour analyser votre situation, identifier vos priorités et vous proposer le parcours adapté formation, consulting ou les deux.':
      '30 minutes with no commitment to analyze your situation, identify your priorities and propose the right path — training, consulting, or both.',
    'Ce qu\'on couvrira ensemble': 'What we\'ll cover together',
    'Votre situation actuelle': 'Your current situation',
    'Vos outils, vos équipes, ce que vous avez déjà essayé avec l\'IA':
      'Your tools, your teams, what you\'ve already tried with AI',
    'Vos objectifs prioritaires': 'Your priority goals',
    'Productivité, automatisation, stratégie : on identifie ensemble ce qui compte vraiment':
      'Productivity, automation, strategy: we identify together what really matters',
    'Un plan d\'action concret': 'A concrete action plan',
    'À l\'issue de l\'appel, vous repartez avec une direction claire, même si on ne travaille pas ensemble':
      'After the call, you leave with a clear direction, even if we don\'t work together',
    'Ou directement par email': 'Or directly by email',
    'Ou par téléphone': 'Or by phone',
    'Réserver un appel de 30 min →': 'Book a 30-min call →',

    // Contact form
    'Votre email professionnel': 'Your professional email',
    'Téléphone (optionnel)': 'Phone (optional)',
    'Secteur d\'activité': 'Industry',
    'Votre besoin principal': 'Your main need',
    'Audit IA (diagnostic)': 'AI Audit (diagnostic)',
    'Mission d\'implémentation IA': 'AI implementation mission',
    'Formation IA équipes': 'AI team training',
    'Je ne sais pas encore': 'Not sure yet',
    'Message ou contexte (optionnel)': 'Message or context (optional)',
    'Réserver mon appel gratuit': 'Book my free call',
    'Réponse sous 24h · Sans engagement': 'Reply within 24h · No commitment',
    'Voici le formulaire de contact.': 'Here is the contact form.',
    'Demande envoyée avec succès !': 'Request sent successfully!',
    'On vous rappelle dans les 24h pour fixer votre appel de découverte.':
      'We\'ll call you back within 24h to schedule your discovery call.',

    // ── 404 ───────────────────────────────────────────────────────
    'Cette page n\'existe pas ou a été déplacée.': 'This page doesn\'t exist or has been moved.',
    'Retour à l\'accueil →': 'Back to home →',

    // ── SHARED TAGS & LABELS ──────────────────────────────────────
    'Voir les cas d\'usage →': 'View use cases →',
    'Voir le comparatif →': 'View comparison →',
    'Prendre RDV →': 'Book a call →',
    'Retour en haut': 'Back to top',
    'Ouvrir le menu': 'Open menu',
    'Fermer le menu': 'Close menu',
    'Pourquoi nous ?': 'Why us?',
    'Notre approche': 'Our approach',
    'Ce que vous obtenez': 'What you get',
    'Inclus': 'Included',
    'À partir de': 'Starting from',
    'par mois': 'per month',
    'Cas d\'usage': 'Use cases',
    'Secteurs': 'Sectors',
    'Voir nos services →': 'View our services →',
  };

  // ──────────────────────────────────────────────────────────────────
  //  PAGE TITLES
  // ──────────────────────────────────────────────────────────────────
  const TITLES = {
    'Quantum Consulting | Cabinet de Conseil IA : transformation des entreprises':
      'Quantum Consulting | AI Consulting Firm: Business Transformation',
    'Conseil et Audit IA pour PME et ETI | Quantum Consulting':
      'AI Consulting and Audit for SMBs | Quantum Consulting',
    'Audit IA pour PME : Diagnostic & Roadmap | Quantum Consulting':
      'AI Audit for SMBs: Diagnostic & Roadmap | Quantum Consulting',
    'Intégration IA dans vos Outils Métier : CRM, ERP, Microsoft 365 | Quantum Consulting':
      'AI Integration into Business Tools: CRM, ERP, Microsoft 365 | Quantum Consulting',
    'Automatisation des Processus avec IA, Make, n8n et Agents | Quantum Consulting':
      'Process Automation with AI, Make, n8n and Agents | Quantum Consulting',
    'Agents IA et LLM Privés : Déploiement Souverain en Entreprise | Quantum Consulting':
      'AI Agents and Private LLMs: Sovereign Enterprise Deployment | Quantum Consulting',
    'Formation Initiation à l\'IA en Entreprise | Quantum Consulting':
      'AI Introduction Training for Business | Quantum Consulting',
    'Formation Maîtrise & Automatisation IA | Quantum Consulting':
      'AI Mastery & Automation Training | Quantum Consulting',
    'Formation Stratégie IA Dirigeant PME | Quantum Consulting':
      'Expert AI & Strategy Training for Executives | Quantum Consulting',
    'Cas d\'Usage IA par Secteur : commerce, industrie, santé, finance, RH | Quantum Consulting':
      'AI Use Cases by Industry: retail, manufacturing, healthcare, finance, HR | Quantum Consulting',
    'Comparatif Modèles LLM 2026 : Claude, GPT-4o, Mistral, Gemini, Llama | Quantum Consulting':
      'LLM Model Comparison 2026: Claude, GPT-4o, Mistral, Gemini, Llama | Quantum Consulting',
    'FAQ Intelligence Artificielle en Entreprise : 40 questions et réponses | Quantum Consulting':
      'AI for Business FAQ: 40 Questions and Answers | Quantum Consulting',
    'Blog IA : conseils et insights | Quantum Consulting':
      'AI Blog: insights and advice | Quantum Consulting',
    'Contact : réserver un appel gratuit | Quantum Consulting':
      'Contact: book a free call | Quantum Consulting',
    'Page introuvable | Quantum Consulting':
      'Page Not Found | Quantum Consulting',
  };

  // ──────────────────────────────────────────────────────────────────
  //  ENGINE
  // ──────────────────────────────────────────────────────────────────

  let NODES   = [];   // { node, orig }
  let ATTRS   = [];   // { el, attr, orig }
  let INITED  = false;
  let LANG    = localStorage.getItem('q_lang') || 'fr';
  const _origTitle = document.title;

  function trimAll(s) {
    return s.replace(/^[\s\u00a0]+|[\s\u00a0]+$/g, '');
  }

  // Normalize key for dict lookup: trim + replace internal NBSP with regular space
  function normKey(s) {
    return trimAll(s).replace(/\u00a0/g, ' ');
  }

  function buildMap() {
    const SKIP = new Set(['SCRIPT','STYLE','NOSCRIPT','META','LINK','CODE','PRE','SVG','MATH']);

    const walker = document.createTreeWalker(
      document.body, NodeFilter.SHOW_TEXT, {
        acceptNode(n) {
          const p = n.parentElement;
          if (!p) return NodeFilter.FILTER_REJECT;
          if (SKIP.has(p.tagName)) return NodeFilter.FILTER_REJECT;
          if (p.closest('script,style,noscript')) return NodeFilter.FILTER_REJECT;
          return NodeFilter.FILTER_ACCEPT;
        }
      }
    );

    let n;
    while ((n = walker.nextNode())) {
      const key = normKey(n.textContent);
      if (key && EN[key] !== undefined) {
        NODES.push({ node: n, orig: n.textContent, key, trimmed: trimAll(n.textContent) });
      }
    }

    // Attributes: placeholder on form fields
    document.querySelectorAll('input[placeholder],textarea[placeholder]').forEach(el => {
      const v = el.getAttribute('placeholder');
      if (v) {
        const key = trimAll(v);
        if (EN[key] !== undefined) ATTRS.push({ el, attr: 'placeholder', orig: v });
      }
    });

    INITED = true;
  }

  function syncBtns() {
    document.querySelectorAll('.q-lang-btn').forEach(b => {
      b.textContent = LANG === 'fr' ? 'EN' : 'FR';
    });
  }

  function apply(l) {
    if (!INITED) buildMap();

    NODES.forEach(({ node, orig, key, trimmed }) => {
      node.textContent = (l === 'en' && EN[key] !== undefined)
        ? orig.replace(trimmed, EN[key])
        : orig;
    });

    ATTRS.forEach(({ el, attr, orig }) => {
      const key = trimAll(orig);
      el.setAttribute(attr, (l === 'en' && EN[key] !== undefined)
        ? orig.replace(key, EN[key])
        : orig);
    });

    // Page title
    const titleKey = trimAll(_origTitle);
    document.title = (l === 'en' && TITLES[titleKey]) ? TITLES[titleKey] : _origTitle;

    // html[lang] attribute
    document.documentElement.lang = l;

    LANG = l;
    localStorage.setItem('q_lang', l);
    syncBtns();
  }

  // ──────────────────────────────────────────────────────────────────
  //  BUTTON INJECTION
  // ──────────────────────────────────────────────────────────────────

  function injectStyles() {
    const s = document.createElement('style');
    s.textContent = `
.q-lang-btn{
  font-family:inherit;font-size:11px;font-weight:700;letter-spacing:.1em;
  text-transform:uppercase;cursor:pointer;transition:all .2s;border-radius:100px;
  padding:5px 13px;border:1px solid rgba(255,255,255,.2);
  background:rgba(255,255,255,.08);color:rgba(255,255,255,.85);
  white-space:nowrap;line-height:1;
}
.q-lang-btn:hover{background:rgba(255,255,255,.18);color:#fff;border-color:rgba(255,255,255,.35)}
#q-lang-desk{margin-right:6px}
@media(max-width:640px){
  #q-lang-desk{display:none!important}
  #q-lang-mob{display:flex!important;align-items:center}
}
@media(min-width:641px){
  #q-lang-mob{display:none!important}
}`;
    document.head.appendChild(s);
  }

  function makeBtn(id, lightBg) {
    const b = document.createElement('button');
    b.className = 'q-lang-btn';
    b.id = id;
    b.setAttribute('aria-label', 'Switch language / Changer de langue');
    b.textContent = LANG === 'fr' ? 'EN' : 'FR';
    if (lightBg) {
      b.style.cssText = 'color:rgba(10,5,28,.7);background:rgba(0,0,0,.06);border-color:rgba(0,0,0,.15)';
    }
    b.addEventListener('click', () => apply(LANG === 'fr' ? 'en' : 'fr'));
    return b;
  }

  function init() {
    injectStyles();

    // Desktop: before .island-cta (index.html) or .n-cta (other pages)
    const deskTarget = document.querySelector('.island-cta, .n-cta');
    if (deskTarget && deskTarget.parentElement) {
      const btn = makeBtn('q-lang-desk', false);
      deskTarget.parentElement.insertBefore(btn, deskTarget);
    }

    // Mobile
    const mobBar = document.getElementById('mob-logo-bar');
    if (mobBar) {
      // index.html: append to mob-logo-bar right side
      mobBar.style.justifyContent = 'space-between';
      mobBar.appendChild(makeBtn('q-lang-mob', true));
    } else {
      // Other pages: fixed top-right pill
      const btn = makeBtn('q-lang-mob', false);
      Object.assign(btn.style, {
        position: 'fixed', top: '10px', right: '5%', zIndex: '260',
        backdropFilter: 'blur(14px)',
        webkitBackdropFilter: 'blur(14px)',
        background: 'rgba(10,5,28,.75)',
        border: '1px solid rgba(255,255,255,.18)',
        color: 'rgba(255,255,255,.9)',
      });
      document.body.appendChild(btn);
    }

    // Apply stored preference
    if (LANG === 'en') apply('en');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
