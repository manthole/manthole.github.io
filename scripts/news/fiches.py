"""Fiches détaillées de la page Actus : type d'attaque, déroulé type, résumé à réexpliquer.

Tout le texte explicatif est écrit ici (pas de copie d'articles). Les articles ne servent qu'à
détecter des faits : type d'attaque, CVE, noms cités, groupe d'attaquants connu de MITRE ATT&CK.
Le déroulé affiché est le schéma TYPE de cette catégorie d'attaque, présenté comme tel.

Les identifiants de techniques sont vérifiés par les tests contre scripts/news/attack_ref.json,
extrait du référentiel officiel MITRE ATT&CK (voir make_attack_ref.py).
"""
import json
import re
from pathlib import Path

REF_PATH = Path(__file__).resolve().parent / "attack_ref.json"

# --------------------------------------------------------------------------- types d'attaque
# Ordre = priorité en cas d'égalité (le plus spécifique d'abord). « intrusion » : repli.
KIND_PATTERNS = [
    ("ransomware", r"ransomware|ran[cç]ongiciel|\bransom\b|double extortion|extortion|extorsion|"
                   r"chiffrement des (?:données|serveurs|fichiers)|encrypt(?:ed|s|ing) (?:files|systems|servers|data)"),
    ("supply_chain", r"supply[\s-]?chain|cha[iî]ne d'approvisionnement|malicious (?:npm|pypi|packages?|extensions?|update)|"
                     r"\bnpm\b|\bpypi\b|trojani[sz]ed|backdoored (?:updates?|installers?|packages?|apps?)|"
                     r"compromised (?:updates?|installers?|launcher|build)|launcher (?:hacked|compromised)|"
                     r"third[\s-]party (?:vendor|provider|supplier)|prestataire|sous-traitant|\bMSPs?\b"),
    ("ot", r"\bICS\b|\bSCADA\b|\bOT\b|\bPLCs?\b|industrial control|industri(?:al|el)|automates?\b|"
           r"refrigerat|r[ée]frig[ée]r|frigos?\b|water (?:utility|utilities|facility|system)|eau potable|"
           r"power grid|r[ée]seau [ée]lectrique|\bHMIs?\b|programmable logic"),
    ("crypto", r"crypto(?:currency|currencies)?\b|cryptomonnaie|bitcoin|ethereum|\bwallets?\b|portefeuilles? (?:crypto|num)|"
               r"\bheist\b|\bDeFi\b|exchange (?:hack|breach)|stole \$|\$\d[\d.,]*\s?(?:million|billion|M\b)|vol de (?:fonds|cryptos?)"),
    ("espionage", r"espionage|espionnage|state[\s-](?:sponsored|linked|backed)|nation[\s-]state|\bAPT\s?\d+|\bAPT\b|"
                  r"(?:chinese|russian|iranian|north korean)(?:[\s-]linked)? (?:hackers|threat actors|spies|apt)|"
                  r"Typhoon|Blizzard|Sleet|Sandstorm|Tempest|Panda\b|Bear\b|Kitten\b|Chollima|zero[\s-]click|"
                  r"spyware|logiciel espion|[ée]tatique|services de renseignement"),
    ("ddos", r"\bDDoS\b|d[ée]ni de service|denial[\s-]of[\s-]service|hacktivis|NoName057"),
    ("phishing", r"phishing|hame[cç]onnage|smishing|vishing|quishing|credential (?:theft|harvest)|account takeover|"
                 r"fake (?:login|sites?|emails?)|faux (?:sites?|e-?mails?|sms|messages)|\bscams?\b|arnaques?|"
                 r"\bBEC\b|business email compromise|MFA bypass|adversary-in-the-middle|\bAiTM\b"),
    ("breach", r"data breach|\bbreach(?:ed|es)?\b|\bleak(?:ed|s)?\b|fuite|stolen data|data (?:theft|stolen)|"
               r"donn[ée]es (?:vol[ée]es|d[ée]rob[ée]es|expos[ée]es|personnelles)|vol de donn|exfiltrat|"
               r"(?:customer|personal|patient|employee) (?:data|information|records)|records exposed"),
    ("malware", r"malware|infostealer|info[\s-]?stealer|\bstealer\b|trojan|cheval de troie|botnet|\bRATs?\b|"
                r"\bloader\b|\bwiper\b|rootkit|logiciel malveillant|maliciel"),
    ("exploit", r"zero[\s-]?days?|\b0[\s-]?days?|exploit|CVE-\d|vulnerabilit|vuln[ée]rabilit|faille|\bflaws?\b|unpatched|"
                r"\bpatch"),
]
KINDS = [k for k, _ in KIND_PATTERNS] + ["intrusion"]
_COMPILED = [(k, re.compile(p, re.I)) for k, p in KIND_PATTERNS]


def kind_scores(title, summary=""):
    """Score par type : 3 si le titre le mentionne, 1 si seulement le résumé."""
    out = {}
    for k, rx in _COMPILED:
        if rx.search(title):
            out[k] = 3
        elif summary and rx.search(summary):
            out[k] = 1
    return out


def rank_kinds(total):
    """[type principal, autres types significatifs] à partir de scores cumulés."""
    ordered = sorted((k for k in total if total[k] > 0), key=lambda k: (-total[k], KINDS.index(k)))
    if not ordered:
        return ["intrusion"]
    top = total[ordered[0]]
    # « exploit » est très large (faille, patch…) : il ne l'emporte que s'il domine nettement
    if ordered[0] == "exploit" and len(ordered) > 1 and total[ordered[1]] * 2 >= top:
        ordered[0], ordered[1] = ordered[1], ordered[0]
    return [ordered[0]] + [k for k in ordered[1:] if total[k] * 3 >= top][:2]


# --------------------------------------------------------------------------- base de connaissances
# Chaque phase : (titre FR, titre EN, texte FR, texte EN, [techniques ATT&CK])
PLAYBOOKS = {
    "ransomware": {
        "label": ("Rançongiciel", "Ransomware"),
        "phrase": ("une attaque par rançongiciel", "a ransomware attack"),
        "def": ("Un groupe criminel pénètre le réseau, vole des données puis chiffre les systèmes et exige une rançon. "
                "Le vol avant chiffrement permet une « double extorsion » : payer pour déchiffrer, et payer pour que les données ne soient pas publiées.",
                "A criminal group breaks into the network, steals data, then encrypts systems and demands a ransom. "
                "Stealing before encrypting enables “double extortion”: pay to decrypt, and pay so the data is not published."),
        "phases": [
            ("Accès initial", "Initial access",
             "Par un équipement exposé non corrigé (VPN, pare-feu), des identifiants volés ou achetés à un courtier d'accès, ou un e-mail piégé.",
             "Through an unpatched exposed device (VPN, firewall), credentials stolen or bought from an access broker, or a booby-trapped email.",
             ["T1190", "T1078", "T1566", "T1650"]),
            ("Installation et privilèges", "Foothold and privileges",
             "Dépôt d'outils de prise de main à distance, obtention des droits administrateur et récupération de mots de passe en mémoire.",
             "Remote access tools are dropped, administrator rights obtained, and passwords harvested from memory.",
             ["T1219", "T1068", "T1003"]),
            ("Propagation", "Lateral movement",
             "Cartographie de l'annuaire (Active Directory) puis déplacement de machine en machine avec des comptes légitimes.",
             "The directory (Active Directory) is mapped, then the attackers move machine to machine with legitimate accounts.",
             ["T1087", "T1018", "T1021"]),
            ("Vol de données", "Data theft",
             "Avant de chiffrer, les données sensibles sont compressées et envoyées vers un stockage en ligne : c'est le moyen de pression.",
             "Before encryption, sensitive data is compressed and sent to online storage: this is the leverage.",
             ["T1560", "T1567"]),
            ("Chiffrement", "Encryption",
             "Suppression des sauvegardes et des clichés, puis chiffrement des serveurs, souvent la nuit ou le week-end.",
             "Backups and snapshots are deleted, then servers are encrypted, often at night or over a weekend.",
             ["T1490", "T1486"]),
            ("Extorsion", "Extortion",
             "Note de rançon, négociation, puis menace de publication sur le site vitrine du groupe si la victime ne paie pas.",
             "Ransom note, negotiation, then a threat to publish on the group's leak site if the victim does not pay.",
             ["T1657"]),
        ],
        "protect": [
            ("Corriger en priorité les équipements exposés à Internet et imposer la double authentification sur les accès distants.",
             "Patch internet-facing devices first and enforce multi-factor authentication on remote access."),
            ("Garder des sauvegardes hors ligne et tester régulièrement leur restauration.",
             "Keep offline backups and regularly test restoring them."),
            ("Surveiller l'annuaire et les mouvements latéraux (EDR, journaux) et segmenter le réseau.",
             "Monitor the directory and lateral movement (EDR, logs) and segment the network."),
        ],
    },
    "supply_chain": {
        "label": ("Chaîne d'approvisionnement", "Supply chain"),
        "phrase": ("une attaque de la chaîne d'approvisionnement", "a supply chain attack"),
        "def": ("Au lieu de viser la victime directement, l'attaquant compromet un fournisseur, un logiciel ou une bibliothèque qu'elle utilise. "
                "Une seule compromission atteint tous les clients, par un canal auquel ils font confiance.",
                "Instead of targeting the victim directly, the attacker compromises a supplier, software or library it uses. "
                "One compromise reaches every customer, through a channel they trust."),
        "phases": [
            ("Choix du maillon faible", "Weak link",
             "Repérage d'un éditeur, d'un prestataire ou d'un paquet open source très utilisé, souvent moins protégé que ses clients.",
             "A vendor, service provider or widely used open source package is chosen, often less protected than its customers.",
             ["T1195"]),
            ("Compromission du fournisseur", "Supplier compromise",
             "Vol d'un compte de développeur ou de publication, intrusion dans la chaîne de compilation, ou abus de l'accès d'un prestataire.",
             "A developer or publishing account is stolen, the build pipeline is breached, or a provider's access is abused.",
             ["T1078", "T1199"]),
            ("Code piégé", "Poisoned code",
             "Une mise à jour ou un paquet légitime embarque une porte dérobée, distribuée par les canaux officiels.",
             "A legitimate update or package ships a backdoor, distributed through official channels.",
             ["T1195.002", "T1554"]),
            ("Exécution chez les clients", "Execution at customers",
             "Les clients installent la mise à jour en confiance ; le code malveillant s'exécute avec les droits du logiciel.",
             "Customers install the update in good faith; the malicious code runs with the software's privileges.",
             ["T1204", "T1059"]),
            ("Exploitation", "Exploitation",
             "L'attaquant choisit ensuite ses cibles : vol de secrets et de jetons, accès aux réseaux, déploiement d'autres charges.",
             "The attacker then picks targets: theft of secrets and tokens, network access, further payloads.",
             ["T1552", "T1041"]),
        ],
        "protect": [
            ("Tenir l'inventaire des dépendances (SBOM) et figer les versions installées.",
             "Keep a dependency inventory (SBOM) and pin installed versions."),
            ("Limiter les droits des logiciels tiers et des prestataires au strict nécessaire.",
             "Give third-party software and providers only the access they strictly need."),
            ("Protéger les comptes de publication par une double authentification résistante (clé de sécurité).",
             "Protect publishing accounts with phishing-resistant MFA (security keys)."),
        ],
    },
    "ot": {
        "label": ("Systèmes industriels", "Industrial systems"),
        "phrase": ("une attaque contre des systèmes industriels", "an attack on industrial systems"),
        "def": ("L'attaque vise des équipements qui pilotent le monde physique : automates, régulation, capteurs, télémaintenance. "
                "L'impact peut être matériel (arrêt de production, produits perdus) et pas seulement informatique.",
                "The attack targets equipment that controls the physical world: controllers, regulation, sensors, remote maintenance. "
                "The impact can be physical (production stopped, goods lost), not only IT."),
        "phases": [
            ("Repérage", "Reconnaissance",
             "Recherche d'équipements industriels joignables depuis Internet : interfaces web, accès de télémaintenance.",
             "Search for industrial equipment reachable from the internet: web interfaces, remote maintenance access.",
             ["T0883", "T1595"]),
            ("Accès", "Access",
             "Mot de passe par défaut, faille non corrigée ou accès distant d'un prestataire.",
             "Default password, unpatched flaw or a provider's remote access.",
             ["T0819", "T0822"]),
            ("Découverte", "Discovery",
             "Identification des automates et de leurs paramètres de fonctionnement.",
             "Controllers and their operating parameters are identified.",
             ["T0846", "T0888"]),
            ("Manipulation", "Manipulation",
             "Modification de consignes (température, pression, débit), arrêt ou blocage du contrôle par les opérateurs.",
             "Setpoints are changed (temperature, pressure, flow), control is stopped or operators are locked out.",
             ["T0836", "T0831", "T0813"]),
            ("Impact physique", "Physical impact",
             "Arrêt de production, perte de produits, risque pour la sécurité des personnes.",
             "Production stops, goods are lost, people's safety can be at risk.",
             ["T0826", "T0879", "T0828"]),
        ],
        "protect": [
            ("Ne jamais exposer d'interface industrielle sur Internet : passer par un VPN avec double authentification.",
             "Never expose industrial interfaces to the internet: go through a VPN with MFA."),
            ("Changer les mots de passe par défaut et tenir l'inventaire des équipements connectés.",
             "Change default passwords and keep an inventory of connected equipment."),
            ("Séparer le réseau industriel du réseau bureautique et surveiller les changements de consignes.",
             "Separate the industrial network from the office network and monitor setpoint changes."),
        ],
    },
    "crypto": {
        "label": ("Vol financier", "Financial theft"),
        "phrase": ("un vol financier", "a financial theft"),
        "def": ("L'objectif est l'argent, directement : plateformes de cryptomonnaies, portefeuilles ou virements frauduleux. "
                "Ces vols sont souvent préparés pendant des semaines en ciblant les employés.",
                "The goal is money, directly: cryptocurrency platforms, wallets or fraudulent transfers. "
                "These thefts are often prepared for weeks by targeting employees."),
        "phases": [
            ("Ciblage des employés", "Targeting staff",
             "Faux recruteurs, faux projets ou messages ciblés envoyés aux développeurs et aux personnes qui valident les transactions.",
             "Fake recruiters, fake projects or targeted messages sent to developers and to the people who approve transactions.",
             ["T1566"]),
            ("Compromission d'un poste", "Workstation compromise",
             "Un fichier piégé est ouvert ; l'attaquant obtient l'accès au poste et aux comptes de l'employé.",
             "A booby-trapped file is opened; the attacker gains access to the employee's machine and accounts.",
             ["T1204.002", "T1078"]),
            ("Détournement", "Diversion",
             "Vol de clés privées ou modification d'une transaction au moment de sa signature.",
             "Private keys are stolen or a transaction is altered at signing time.",
             ["T1552", "T1565"]),
            ("Blanchiment", "Laundering",
             "Les fonds sont dispersés sur de nombreux portefeuilles, mélangeurs et ponts entre blockchains.",
             "Funds are spread across many wallets, mixers and cross-chain bridges.",
             ["T1657"]),
        ],
        "protect": [
            ("Exiger plusieurs signatures et une vérification hors ligne pour les transactions importantes.",
             "Require multiple signatures and offline verification for large transactions."),
            ("Réserver des postes dédiés et isolés à la signature.",
             "Use dedicated, isolated machines for signing."),
            ("Vérifier les offres d'emploi et ne jamais exécuter un « test technique » reçu d'un inconnu.",
             "Check job offers and never run a “technical test” received from a stranger."),
        ],
    },
    "espionage": {
        "label": ("Espionnage (APT)", "Espionage (APT)"),
        "phrase": ("une opération d'espionnage", "an espionage operation"),
        "def": ("Un groupe lié à un État cherche à rester invisible le plus longtemps possible pour collecter du renseignement. "
                "APT signifie « menace persistante avancée » : des moyens importants et de la patience.",
                "A state-linked group tries to stay invisible as long as possible to collect intelligence. "
                "APT means “advanced persistent threat”: significant resources and patience."),
        "phases": [
            ("Préparation", "Preparation",
             "Infrastructure dédiée, développement ou achat d'exploits, repérage des cibles.",
             "Dedicated infrastructure, exploits developed or bought, targets scouted.",
             ["T1583", "T1588.005", "T1595"]),
            ("Accès initial", "Initial access",
             "Hameçonnage ciblé, faille sur un équipement de bordure, ou exploit « zéro clic » qui infecte un téléphone sans action de la victime.",
             "Spear-phishing, a flaw in an edge device, or a “zero-click” exploit that infects a phone without any action from the victim.",
             ["T1566", "T1190", "T1203"]),
            ("Persistance discrète", "Stealthy persistence",
             "Portes dérobées sur mesure, comptes légitimes, implants dans des équipements peu surveillés.",
             "Custom backdoors, legitimate accounts, implants on poorly monitored devices.",
             ["T1505.003", "T1078", "T1547"]),
            ("Commande et contrôle", "Command and control",
             "Communications camouflées dans du trafic ordinaire : HTTPS, services cloud connus.",
             "Communications hidden in ordinary traffic: HTTPS, well-known cloud services.",
             ["T1071", "T1102"]),
            ("Collecte et exfiltration", "Collection and exfiltration",
             "Courriels, documents, contacts, messages ; les données sortent progressivement pour ne pas se faire remarquer.",
             "Emails, documents, contacts, messages; data leaves gradually to avoid notice.",
             ["T1114", "T1213", "T1041"]),
        ],
        "protect": [
            ("Corriger en urgence les équipements de bordure (VPN, pare-feu, passerelles).",
             "Patch edge devices urgently (VPN, firewalls, gateways)."),
            ("Mettre à jour les téléphones rapidement ; activer le mode isolement (Lockdown) pour les profils exposés.",
             "Update phones quickly; enable Lockdown Mode for high-risk profiles."),
            ("Conserver et analyser les journaux : la détection repose sur la chasse aux anomalies.",
             "Keep and analyse logs: detection relies on hunting for anomalies."),
        ],
    },
    "ddos": {
        "label": ("Déni de service", "Denial of service"),
        "phrase": ("une attaque par déni de service (DDoS)", "a denial-of-service (DDoS) attack"),
        "def": ("Saturer un service en ligne de trafic pour le rendre inaccessible. Souvent revendiqué par des groupes hacktivistes ; "
                "spectaculaire mais en général sans vol de données.",
                "Flooding an online service with traffic to make it unavailable. Often claimed by hacktivist groups; "
                "visible, but usually without data theft."),
        "phases": [
            ("Armée de machines", "Bot army",
             "Constitution ou location d'un botnet : objets connectés, serveurs piratés.",
             "A botnet is built or rented: connected devices, hacked servers.",
             ["T1583.005", "T1584"]),
            ("Choix de la cible", "Target selection",
             "Site symbolique (administration, transports, banques), souvent annoncé sur les réseaux sociaux ou Telegram.",
             "A symbolic site (government, transport, banks), often announced on social media or Telegram.",
             []),
            ("Inondation", "Flood",
             "Envoi massif de paquets réseau ou de requêtes applicatives coûteuses.",
             "Massive volumes of network packets or expensive application requests.",
             ["T1498.001", "T1499.002"]),
            ("Indisponibilité", "Outage",
             "Le service ralentit ou tombe ; l'attaque cesse généralement en quelques heures.",
             "The service slows down or goes offline; the attack usually stops within hours.",
             ["T1498", "T1499"]),
        ],
        "protect": [
            ("Utiliser la protection anti-DDoS de l'hébergeur ou d'un CDN.",
             "Use the hosting provider's or a CDN's DDoS protection."),
            ("Mettre en cache et limiter le débit des requêtes coûteuses.",
             "Cache content and rate-limit expensive requests."),
            ("Prévoir un plan de continuité et une page de secours.",
             "Have a continuity plan and a fallback page."),
        ],
    },
    "phishing": {
        "label": ("Hameçonnage", "Phishing"),
        "phrase": ("une campagne d'hameçonnage", "a phishing campaign"),
        "def": ("Tromper des personnes pour voler leurs identifiants ou leur faire lancer un fichier. "
                "Les kits modernes relaient la vraie page de connexion et contournent même les codes de double authentification.",
                "Tricking people into giving away credentials or running a file. "
                "Modern kits relay the real login page and even bypass one-time codes."),
        "phases": [
            ("Préparation", "Preparation",
             "Nom de domaine ressemblant, page de connexion copiée ou proxy qui relaie la vraie page.",
             "Look-alike domain, copied login page, or a proxy relaying the real page.",
             ["T1583", "T1608"]),
            ("Leurre", "Lure",
             "E-mail, SMS, message ou appel urgent : facture, colis, alerte de sécurité.",
             "Urgent email, text, message or call: invoice, parcel, security alert.",
             ["T1566", "T1566.002"]),
            ("Vol des accès", "Credential theft",
             "La victime saisit mot de passe et code ; l'attaquant récupère aussi le cookie de session.",
             "The victim enters password and code; the attacker also captures the session cookie.",
             ["T1557", "T1539"]),
            ("Prise de compte", "Account takeover",
             "Connexion au compte, ajout d'un appareil ou de règles de messagerie pour garder l'accès.",
             "The account is accessed, a device or mailbox rules are added to keep access.",
             ["T1078", "T1098"]),
            ("Exploitation", "Exploitation",
             "Fraude au virement, vol de données, nouvel hameçonnage lancé depuis le compte compromis.",
             "Payment fraud, data theft, new phishing sent from the compromised account.",
             ["T1534", "T1114", "T1657"]),
        ],
        "protect": [
            ("Passer à une authentification résistante à l'hameçonnage (clés de sécurité, passkeys).",
             "Move to phishing-resistant authentication (security keys, passkeys)."),
            ("Former et faciliter le signalement des messages suspects.",
             "Train people and make reporting suspicious messages easy."),
            ("Alerter sur les connexions inhabituelles et les nouvelles règles de messagerie.",
             "Alert on unusual sign-ins and new mailbox rules."),
        ],
    },
    "breach": {
        "label": ("Fuite de données", "Data breach"),
        "phrase": ("une fuite de données", "a data breach"),
        "def": ("Des données (clients, salariés, documents) sont copiées par un tiers non autorisé, puis revendues, publiées "
                "ou réutilisées pour d'autres attaques.",
                "Data (customers, employees, documents) is copied by an unauthorised party, then sold, published "
                "or reused for further attacks."),
        "phases": [
            ("Accès", "Access",
             "Identifiants volés (souvent par un infostealer), faille, ou stockage cloud mal configuré.",
             "Stolen credentials (often from an infostealer), a flaw, or misconfigured cloud storage.",
             ["T1078", "T1190", "T1530"]),
            ("Exploration", "Exploration",
             "Repérage des bases de données, des stockages et des applications métiers.",
             "Databases, storage and business applications are located.",
             ["T1046", "T1619"]),
            ("Collecte", "Collection",
             "Extraction de bases, d'exports et de documents, regroupés en archives.",
             "Databases, exports and documents are extracted and bundled into archives.",
             ["T1213", "T1560"]),
            ("Exfiltration", "Exfiltration",
             "Copie vers un serveur de l'attaquant ou un service de stockage en ligne.",
             "Copied to an attacker server or an online storage service.",
             ["T1567", "T1041"]),
            ("Monétisation", "Monetisation",
             "Revente sur des forums, chantage, ou réutilisation pour de l'hameçonnage ciblé.",
             "Sold on forums, used for blackmail, or reused for targeted phishing.",
             ["T1657"]),
        ],
        "protect": [
            ("Double authentification partout et renouvellement des identifiants exposés.",
             "MFA everywhere and rotation of exposed credentials."),
            ("Collecter moins, chiffrer et cloisonner les données sensibles.",
             "Collect less, encrypt and compartmentalise sensitive data."),
            ("Alerter sur les exports volumineux et les accès inhabituels aux bases.",
             "Alert on large exports and unusual database access."),
        ],
    },
    "malware": {
        "label": ("Logiciel malveillant", "Malware"),
        "phrase": ("une campagne de logiciel malveillant", "a malware campaign"),
        "def": ("Un programme malveillant est diffusé largement (faux logiciels, publicités piégées, pièces jointes) "
                "pour voler des informations ou prendre le contrôle des machines.",
                "Malicious software is spread widely (fake software, malicious ads, attachments) "
                "to steal information or take control of machines."),
        "phases": [
            ("Diffusion", "Delivery",
             "Faux site de téléchargement, publicité piégée, logiciel ou jeu piraté, pièce jointe.",
             "Fake download site, malicious ad, cracked software or game, attachment.",
             ["T1189", "T1566", "T1204.002"]),
            ("Exécution", "Execution",
             "L'utilisateur lance le fichier ; un « chargeur » télécharge ensuite la charge finale.",
             "The user runs the file; a “loader” then downloads the final payload.",
             ["T1204", "T1105"]),
            ("Camouflage et persistance", "Hiding and persistence",
             "Code obfusqué pour échapper aux antivirus, lancement automatique au démarrage.",
             "Obfuscated code to evade antivirus, automatic start at boot.",
             ["T1027", "T1547"]),
            ("Vol", "Theft",
             "Mots de passe enregistrés dans les navigateurs, cookies de session, portefeuilles de cryptomonnaies.",
             "Passwords saved in browsers, session cookies, cryptocurrency wallets.",
             ["T1555", "T1539"]),
            ("Exploitation", "Exploitation",
             "Les données partent vers le serveur de commande, puis sont revendues ou servent à d'autres intrusions.",
             "Data goes to the command server, then is sold or used for further intrusions.",
             ["T1041", "T1071"]),
        ],
        "protect": [
            ("Installer les logiciels uniquement depuis les sources officielles.",
             "Install software only from official sources."),
            ("Garder un antivirus ou un EDR à jour sur tous les postes.",
             "Keep antivirus or EDR up to date on every machine."),
            ("Préférer un gestionnaire de mots de passe à l'enregistrement dans le navigateur.",
             "Prefer a password manager to saving passwords in the browser."),
        ],
    },
    "exploit": {
        "label": ("Faille exploitée", "Exploited flaw"),
        "phrase": ("l'exploitation active d'une faille", "active exploitation of a flaw"),
        "def": ("Les attaquants utilisent une faille d'un logiciel ou d'un équipement. On parle de zero-day quand l'éditeur "
                "ne la connaissait pas encore : aucun correctif n'existait au début des attaques.",
                "Attackers use a flaw in software or a device. It is called a zero-day when the vendor did not know about it yet: "
                "no patch existed when the attacks began."),
        "phases": [
            ("Obtention de la faille", "Getting the flaw",
             "Recherche, analyse d'un correctif publié (pour retrouver la faille corrigée) ou achat à un courtier.",
             "Research, analysis of a released patch (to find the fixed flaw) or purchase from a broker.",
             ["T1588.006", "T1588.005"]),
            ("Recherche des cibles", "Finding targets",
             "Balayage massif d'Internet pour trouver les équipements vulnérables exposés.",
             "Mass internet scanning to find exposed vulnerable devices.",
             ["T1595"]),
            ("Exploitation", "Exploitation",
             "Une requête piégée provoque l'exécution de code ou contourne l'authentification.",
             "A crafted request triggers code execution or bypasses authentication.",
             ["T1190", "T1203"]),
            ("Installation", "Implant",
             "Dépôt d'un web shell ou d'une porte dérobée, souvent avant même la publication du correctif.",
             "A web shell or backdoor is dropped, often before the patch is even released.",
             ["T1505.003", "T1105"]),
            ("Suite de l'attaque", "Follow-up",
             "L'équipement sert de tête de pont : propagation, vol de données, revente de l'accès ou rançongiciel.",
             "The device becomes a beachhead: lateral movement, data theft, access resale or ransomware.",
             ["T1021", "T1041"]),
        ],
        "protect": [
            ("Appliquer le correctif ou la mesure de contournement dès sa publication ; le catalogue CISA donne les priorités.",
             "Apply the patch or workaround as soon as it is released; the CISA catalogue sets priorities."),
            ("Ne pas exposer les interfaces d'administration sur Internet.",
             "Do not expose admin interfaces to the internet."),
            ("Rechercher des traces de compromission : corriger ne chasse pas un intrus déjà installé.",
             "Look for signs of compromise: patching does not remove an intruder already inside."),
        ],
    },
    "intrusion": {
        "label": ("Intrusion", "Intrusion"),
        "phrase": ("une intrusion informatique", "a cyber intrusion"),
        "def": ("Un attaquant a obtenu un accès non autorisé à un système d'information. Le déroulé précis n'est pas encore public "
                "ou se trouve dans les articles ; voici le schéma général d'une intrusion.",
                "An attacker gained unauthorised access to an information system. The exact sequence is not public yet "
                "or is in the articles; here is the general pattern of an intrusion."),
        "phases": [
            ("Accès initial", "Initial access",
             "Faille sur un service exposé, identifiants volés ou hameçonnage.",
             "Flaw in an exposed service, stolen credentials or phishing.",
             ["T1190", "T1078", "T1566"]),
            ("Installation", "Foothold",
             "Dépôt d'outils et mise en place d'un accès durable.",
             "Tools are dropped and lasting access is set up.",
             ["T1105", "T1547"]),
            ("Exploration et propagation", "Discovery and spread",
             "Cartographie du réseau et déplacement vers les systèmes intéressants.",
             "The network is mapped and the attacker moves to valuable systems.",
             ["T1046", "T1021"]),
            ("Objectif", "Objective",
             "Vol de données, sabotage, ou revente de l'accès à d'autres groupes.",
             "Data theft, sabotage, or resale of the access to other groups.",
             ["T1041", "T1485"]),
        ],
        "protect": [
            ("Double authentification et correctifs à jour sur tout ce qui est exposé.",
             "MFA and up-to-date patches on everything exposed."),
            ("Journaux centralisés et alertes sur les comportements inhabituels.",
             "Centralised logs and alerts on unusual behaviour."),
            ("Plan de réponse à incident prêt et testé.",
             "An incident response plan ready and tested."),
        ],
    },
}


# --------------------------------------------------------------------------- référentiel MITRE
_REF = None


def ref():
    global _REF
    if _REF is None:
        try:
            _REF = json.loads(REF_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _REF = {"techniques": {}, "actors": []}
        actors = []
        for a in _REF.get("actors", []):
            names = sorted({n for n in a.get("names", []) if isinstance(n, str) and n}, key=len, reverse=True)
            if names:
                rx = re.compile(r"(?<![\w-])(?:" + "|".join(re.escape(n) for n in names) + r")(?![\w])")
                actors.append((rx, a))
        _REF["_actors"] = actors
    return _REF


def find_actors(texts):
    """Groupes et logiciels malveillants connus de MITRE ATT&CK cités (sensible à la casse)."""
    found = []
    for rx, a in ref()["_actors"]:
        for t in texts:
            m = rx.search(t)
            if m:
                found.append((m.group(0), a))
                break
    return found[:4]


def actor_by_id(aid):
    for _, a in ref()["_actors"]:
        if a["id"] == aid:
            return a
    return None


STATE_ACTOR = re.compile(r"attributed to|state[\s-](?:sponsored|backed|linked)|espionage|intelligence|military unit", re.I)


def actor_kind_bonus(actor_ids):
    """Un groupe connu oriente le type : groupe étatique → espionnage, rançongiciel → rançongiciel."""
    bonus = {}
    for aid in actor_ids:
        a = actor_by_id(aid)
        if not a:
            continue
        if "ransomware" in a["desc"].lower():
            bonus["ransomware"] = 3
        elif a["kind"] == "group" and STATE_ACTOR.search(a["desc"]):
            bonus["espionage"] = 3
    return bonus
