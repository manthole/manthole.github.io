"""Génère /redteam/ : pense-bête de méthodologie offensive (kill chain / MITRE ATT&CK) pour CTF et
labos autorisés. Contenu pédagogique : phases, techniques ATT&CK et noms d'outils connus ; aucune
instruction opérationnelle, aucun payload. Exécuté une fois, écrit redteam/index.html."""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
SITE = "https://manthole.github.io"
ATTACK = "https://attack.mitre.org/tactics/"


def L(fr, en, es, pt, de):
    return (f'<span lang="fr">{fr}</span><span lang="en">{en}</span><span lang="es">{es}</span>'
            f'<span lang="pt">{pt}</span><span lang="de">{de}</span>')


def chips(names):
    lis = "".join(f'<li><span class="x-chip x-chip--muted x-chip--plain">{n}</span></li>' for n in names)
    return f'<ul class="x-chips">{lis}</ul>'


# (clé couleur, titre, tactique ATT&CK [id, nom 5 langues], objectif 5 langues, outils)
PHASES = [
    ("TA0043", ("Reconnaissance", "Reconnaissance", "Reconocimiento", "Reconhecimento", "Aufklärung"),
     L("Cartographier la cible : OSINT, domaines et sous-domaines, adresses IP et services exposés, employés et technologies.",
       "Map the target: OSINT, domains and subdomains, IP addresses and exposed services, employees and technologies.",
       "Cartografiar el objetivo: OSINT, dominios y subdominios, direcciones IP y servicios expuestos, empleados y tecnologías.",
       "Mapear o alvo: OSINT, domínios e subdomínios, endereços IP e serviços expostos, funcionários e tecnologias.",
       "Das Ziel kartieren: OSINT, Domains und Subdomains, IP-Adressen und exponierte Dienste, Mitarbeitende und Technologien."),
     ["Nmap", "Masscan", "Amass", "Subfinder", "theHarvester", "Shodan", "Censys", "crt.sh", "ffuf", "Gobuster", "WhatWeb", "Maltego"]),
    ("TA0042", ("Armement & infrastructure", "Weaponization & infrastructure", "Armamento e infraestructura", "Armamento e infraestrutura", "Bewaffnung & Infrastruktur"),
     L("Préparer l'outillage de l'opération : charges, redirecteurs et serveurs de commande (C2), domaines et certificats.",
       "Prepare the operation's tooling: payloads, redirectors and command-and-control (C2) servers, domains and certificates.",
       "Preparar las herramientas de la operación: cargas, redirectores y servidores de mando (C2), dominios y certificados.",
       "Preparar as ferramentas da operação: cargas, redirecionadores e servidores de comando (C2), domínios e certificados.",
       "Das Werkzeug der Operation vorbereiten: Payloads, Redirectoren und Command-and-Control-Server (C2), Domains und Zertifikate."),
     ["Metasploit", "Sliver", "Mythic", "Havoc", "GoPhish", "Evilginx"]),
    ("TA0001", ("Accès initial", "Initial access", "Acceso inicial", "Acesso inicial", "Erstzugriff"),
     L("Obtenir le premier pied dans la place : hameçonnage ciblé, faille d'une application web, service exposé ou VPN mal configuré.",
       "Get the first foothold: spear-phishing, a web application flaw, an exposed service or a misconfigured VPN.",
       "Conseguir el primer punto de apoyo: spear-phishing, fallo de una aplicación web, servicio expuesto o VPN mal configurada.",
       "Conseguir o primeiro ponto de apoio: spear-phishing, falha de uma aplicação web, serviço exposto ou VPN mal configurada.",
       "Den ersten Fuß in die Tür bekommen: Spear-Phishing, eine Web-Schwachstelle, ein exponierter Dienst oder ein falsch konfiguriertes VPN."),
     ["Burp Suite", "sqlmap", "GoPhish", "Evilginx", "searchsploit", "Hydra"]),
    ("TA0002", ("Exécution & persistance", "Execution & persistence", "Ejecución y persistencia", "Execução e persistência", "Ausführung & Persistenz"),
     L("Exécuter du code sur le poste compromis et s'y maintenir : tâches planifiées, services, clés de démarrage.",
       "Run code on the compromised host and stay there: scheduled tasks, services, run keys.",
       "Ejecutar código en el equipo comprometido y mantenerse: tareas programadas, servicios, claves de inicio.",
       "Executar código no posto comprometido e manter-se: tarefas agendadas, serviços, chaves de arranque.",
       "Code auf dem kompromittierten Rechner ausführen und dort bleiben: geplante Aufgaben, Dienste, Autostart-Schlüssel."),
     ["PowerShell", "Impacket", "NetExec", "Evil-WinRM", "WMI"]),
    ("TA0004", ("Élévation de privilèges", "Privilege escalation", "Escalada de privilegios", "Elevação de privilégios", "Rechteausweitung"),
     L("Passer d'un compte standard à administrateur : mauvaises configurations, binaires détournables, failles locales.",
       "Move from a standard account to administrator: misconfigurations, abusable binaries, local flaws.",
       "Pasar de una cuenta estándar a administrador: malas configuraciones, binarios abusables, fallos locales.",
       "Passar de uma conta padrão a administrador: más configurações, binários abusáveis, falhas locais.",
       "Von einem Standardkonto zum Administrator: Fehlkonfigurationen, missbrauchbare Binärdateien, lokale Lücken."),
     ["WinPEAS", "LinPEAS", "GTFOBins", "LOLBAS", "PowerUp", "Seatbelt", "pspy"]),
    ("TA0005", ("Évasion des défenses", "Defense evasion", "Evasión de defensas", "Evasão das defesas", "Umgehung der Abwehr"),
     L("Rester discret face aux antivirus et à l'EDR : obfuscation, binaires légitimes détournés, nettoyage des traces.",
       "Stay quiet against antivirus and EDR: obfuscation, abused legitimate binaries, cleaning up traces.",
       "Pasar desapercibido ante antivirus y EDR: ofuscación, binarios legítimos abusados, limpieza de rastros.",
       "Passar despercebido perante antivírus e EDR: ofuscação, binários legítimos abusados, limpeza de rastos.",
       "Gegenüber Virenschutz und EDR unauffällig bleiben: Verschleierung, missbrauchte legitime Binärdateien, Spuren beseitigen."),
     ["LOLBins", "obfuscation", "Sysmon-aware", "timestomp"]),
    ("TA0006", ("Accès aux identifiants", "Credential access", "Acceso a credenciales", "Acesso a credenciais", "Zugang zu Anmeldedaten"),
     L("Récupérer des secrets : mots de passe en mémoire, empreintes, tickets Kerberos, puis cassage hors ligne.",
       "Harvest secrets: passwords in memory, hashes, Kerberos tickets, then offline cracking.",
       "Obtener secretos: contraseñas en memoria, hashes, tickets Kerberos, y luego cracking sin conexión.",
       "Obter segredos: palavras-passe em memória, hashes, tickets Kerberos, e depois cracking offline.",
       "Geheimnisse ernten: Passwörter im Speicher, Hashes, Kerberos-Tickets, danach Offline-Cracking."),
     ["Mimikatz", "Impacket (secretsdump)", "Responder", "Rubeus", "hashcat", "John"]),
    ("TA0007", ("Découverte", "Discovery", "Descubrimiento", "Descoberta", "Erkundung"),
     L("Cartographier l'intérieur : utilisateurs, machines, partages et surtout les chemins d'attaque de l'Active Directory.",
       "Map the inside: users, machines, shares and above all the Active Directory attack paths.",
       "Cartografiar el interior: usuarios, máquinas, recursos compartidos y sobre todo las rutas de ataque de Active Directory.",
       "Cartografar o interior: utilizadores, máquinas, partilhas e sobretudo os caminhos de ataque do Active Directory.",
       "Das Innere kartieren: Benutzer, Rechner, Freigaben und vor allem die Active-Directory-Angriffspfade."),
     ["BloodHound", "SharpHound", "PowerView", "ldapsearch", "NetExec", "enum4linux-ng"]),
    ("TA0008", ("Mouvement latéral", "Lateral movement", "Movimiento lateral", "Movimento lateral", "Lateral Movement"),
     L("Rebondir de machine en machine vers la cible et pivoter à travers le réseau interne.",
       "Hop from machine to machine toward the target and pivot through the internal network.",
       "Saltar de máquina en máquina hacia el objetivo y pivotar por la red interna.",
       "Saltar de máquina em máquina até ao alvo e pivotar pela rede interna.",
       "Von Rechner zu Rechner zum Ziel springen und durch das interne Netz pivotieren."),
     ["PsExec", "wmiexec", "Evil-WinRM", "NetExec", "ligolo-ng", "chisel"]),
    ("TA0011", ("Command & Control", "Command & control", "Mando y control", "Comando e controlo", "Command & Control"),
     L("Piloter les machines compromises de façon furtive : canaux camouflés dans du trafic ordinaire (HTTPS, DNS).",
       "Drive the compromised machines stealthily: channels hidden in ordinary traffic (HTTPS, DNS).",
       "Controlar las máquinas comprometidas de forma furtiva: canales camuflados en tráfico ordinario (HTTPS, DNS).",
       "Controlar as máquinas comprometidas de forma furtiva: canais camuflados em tráfego comum (HTTPS, DNS).",
       "Die kompromittierten Rechner unauffällig steuern: Kanäle, getarnt im normalen Verkehr (HTTPS, DNS)."),
     ["Cobalt Strike", "Sliver", "Mythic", "Havoc", "Metasploit"]),
    ("TA0040", ("Exfiltration & impact", "Exfiltration & impact", "Exfiltración e impacto", "Exfiltração e impacto", "Exfiltration & Auswirkung"),
     L("Atteindre l'objectif de la mission : exfiltrer les données ciblées ou démontrer l'impact, puis rédiger le rapport.",
       "Reach the engagement's goal: exfiltrate the targeted data or demonstrate impact, then write the report.",
       "Alcanzar el objetivo de la misión: exfiltrar los datos objetivo o demostrar el impacto, y luego redactar el informe.",
       "Atingir o objetivo da missão: exfiltrar os dados-alvo ou demonstrar o impacto, e depois redigir o relatório.",
       "Das Ziel des Auftrags erreichen: die Zieldaten exfiltrieren oder die Auswirkung nachweisen, dann den Bericht schreiben."),
     ["rclone", "Impacket", "7-Zip", "DNS/HTTPS"]),
]

RESOURCES = [
    ("https://attack.mitre.org/", "MITRE ATT&CK",
     L("La matrice de référence des tactiques et techniques d'attaque.", "The reference matrix of attack tactics and techniques.",
       "La matriz de referencia de tácticas y técnicas de ataque.", "A matriz de referência das táticas e técnicas de ataque.",
       "Die Referenzmatrix der Angriffstaktiken und -techniken.")),
    ("https://www.thehacker.recipes/", "The Hacker Recipes",
     L("Méthodologie offensive, très complète sur l'Active Directory.", "Offensive methodology, very thorough on Active Directory.",
       "Metodología ofensiva, muy completa sobre Active Directory.", "Metodologia ofensiva, muito completa sobre Active Directory.",
       "Offensive Methodik, sehr ausführlich zu Active Directory.")),
    ("https://book.hacktricks.wiki/", "HackTricks",
     L("Notes d'exploitation par service, port et système.", "Exploitation notes by service, port and system.",
       "Notas de explotación por servicio, puerto y sistema.", "Notas de exploração por serviço, porta e sistema.",
       "Exploitation-Notizen nach Dienst, Port und System.")),
    ("https://github.com/swisskyrepo/PayloadsAllTheThings", "PayloadsAllTheThings",
     L("Recueil de techniques et de contournements par catégorie.", "A collection of techniques and bypasses by category.",
       "Recopilación de técnicas y evasiones por categoría.", "Coletânea de técnicas e contornos por categoria.",
       "Sammlung von Techniken und Umgehungen nach Kategorie.")),
    ("https://gtfobins.github.io/", "GTFOBins",
     L("Binaires Unix légitimes détournables pour l'escalade.", "Legitimate Unix binaries abusable for escalation.",
       "Binarios Unix legítimos abusables para la escalada.", "Binários Unix legítimos abusáveis para a escalada.",
       "Legitime Unix-Binärdateien, missbrauchbar zur Rechteausweitung.")),
    ("https://lolbas-project.github.io/", "LOLBAS",
     L("L'équivalent côté Windows (binaires et scripts signés).", "The Windows equivalent (signed binaries and scripts).",
       "El equivalente en Windows (binarios y scripts firmados).", "O equivalente no Windows (binários e scripts assinados).",
       "Das Windows-Pendant (signierte Binärdateien und Skripte).")),
    ("https://owasp.org/www-project-web-security-testing-guide/", "OWASP WSTG",
     L("Le guide de test de sécurité des applications web.", "The web application security testing guide.",
       "La guía de pruebas de seguridad de aplicaciones web.", "O guia de testes de segurança de aplicações web.",
       "Der Leitfaden zum Sicherheitstest von Webanwendungen.")),
    ("http://www.pentest-standard.org/", "PTES",
     L("Le standard de déroulé d'un test d'intrusion.", "The standard for the flow of a penetration test.",
       "El estándar del desarrollo de una prueba de intrusión.", "O padrão do desenrolar de um teste de intrusão.",
       "Der Standard für den Ablauf eines Penetrationstests.")),
    ("https://tryhackme.com/", "TryHackMe",
     L("Des labos guidés pour s'entraîner légalement.", "Guided labs to practise legally.",
       "Laboratorios guiados para practicar legalmente.", "Laboratórios guiados para praticar legalmente.",
       "Angeleitete Labore zum legalen Üben.")),
    ("https://www.hackthebox.com/", "Hack The Box",
     L("Des machines et des CTF pour mettre en pratique.", "Machines and CTFs to put it into practice.",
       "Máquinas y CTF para ponerlo en práctica.", "Máquinas e CTF para pôr em prática.",
       "Maschinen und CTFs zum Üben.")),
]


def build_body():
    banner = (f'<div class="rt-warning" role="note">⚠ ' + L(
        "À des fins pédagogiques et pour des tests <strong>autorisés</strong> uniquement (CTF, labos, missions avec accord écrit). Mener ces actions sur un système sans autorisation est illégal (en France, articles 323-1 et suivants du Code pénal).",
        "For educational use and <strong>authorised</strong> testing only (CTF, labs, engagements with written consent). Carrying out these actions on a system without authorisation is illegal (in France, articles 323-1 et seq. of the Criminal Code).",
        "Con fines educativos y para pruebas <strong>autorizadas</strong> únicamente (CTF, laboratorios, auditorías con acuerdo por escrito). Realizar estas acciones sobre un sistema sin autorización es ilegal (en Francia, artículos 323-1 y siguientes del Código Penal).",
        "Para fins pedagógicos e para testes <strong>autorizados</strong> apenas (CTF, laboratórios, missões com acordo escrito). Realizar estas ações sobre um sistema sem autorização é ilegal (em França, artigos 323-1 e seguintes do Código Penal).",
        "Nur zu Bildungszwecken und für <strong>autorisierte</strong> Tests (CTF, Labore, Einsätze mit schriftlicher Zustimmung). Diese Handlungen ohne Erlaubnis an einem System auszuführen ist illegal (in Frankreich Artikel 323-1 ff. des Strafgesetzbuchs).") + "</div>")

    steps = []
    for i, (ta, title, goal, tools) in enumerate(PHASES, 1):
        tac = L(*title)
        link = (f'<span class="x-step__meta"><a href="{ATTACK}{ta}/" rel="noopener" target="_blank">'
                f'MITRE ATT&amp;CK · {ta}</a></span>')
        steps.append(f'<li data-reveal><span class="x-step__node" aria-hidden="true">{i}</span>'
                     f'<div class="x-step__body"><h4>{tac}</h4>{link}<p>{goal}</p>{chips(tools)}</div></li>')
    chain = '<ol class="x-steps k-red" data-reveal>' + "".join(steps) + "</ol>"

    res_rows = "".join(
        f'<li data-reveal><a class="x-row" href="{url}" rel="noopener" target="_blank">'
        f'<span class="x-row__title">{name}</span> <span class="rt-res__desc">{desc}</span></a></li>'
        for url, name, desc in RESOURCES)

    intro = L(
        "Un pense-bête des grandes étapes d'une opération offensive (la « kill chain »), reliées aux tactiques MITRE ATT&amp;CK, avec les familles d'outils de chaque phase. Pensé comme un rappel quand on bloque sur un CTF ou un labo : « où j'en suis, qu'est-ce que je n'ai pas encore essayé ? »",
        "A reminder of the main stages of an offensive operation (the “kill chain”), mapped to MITRE ATT&amp;CK tactics, with the tool families of each phase. Meant as a prompt when you're stuck on a CTF or a lab: “where am I, what haven't I tried yet?”",
        "Un recordatorio de las grandes etapas de una operación ofensiva (la «kill chain»), vinculadas a las tácticas MITRE ATT&amp;CK, con las familias de herramientas de cada fase. Pensado como recordatorio cuando te atascas en un CTF o un laboratorio: «¿dónde estoy, qué no he probado todavía?»",
        "Um lembrete das grandes etapas de uma operação ofensiva (a «kill chain»), ligadas às táticas MITRE ATT&amp;CK, com as famílias de ferramentas de cada fase. Pensado como lembrete quando se encrava num CTF ou num laboratório: «onde estou, o que ainda não experimentei?»",
        "Eine Gedächtnisstütze zu den Hauptphasen einer offensiven Operation (der „Kill Chain“), verknüpft mit MITRE-ATT&amp;CK-Taktiken, mit den Werkzeugfamilien jeder Phase. Gedacht als Anstoß, wenn man bei einem CTF oder Labor feststeckt: „Wo stehe ich, was habe ich noch nicht probiert?“")

    tools_note = L(
        "Les outils sont cités comme repères : à utiliser dans un cadre légal, sur des cibles dont on a l'autorisation. La page ne contient ni commande d'exploitation ni payload.",
        "The tools are named as pointers: use them legally, on targets you are authorised to test. This page contains no exploitation command and no payload.",
        "Las herramientas se citan como referencia: úsalas en un marco legal, sobre objetivos con autorización. La página no contiene ningún comando de explotación ni payload.",
        "As ferramentas são citadas como referência: usa-as num quadro legal, sobre alvos com autorização. A página não contém nenhum comando de exploração nem payload.",
        "Die Werkzeuge werden als Wegweiser genannt: Nutze sie legal, an Zielen, für die du autorisiert bist. Diese Seite enthält keinen Exploitation-Befehl und kein Payload.")

    return f"""<p class="x-kicker k-red">{chip_dot(L("Méthodologie", "Methodology", "Metodología", "Metodologia", "Methodik"))} {chip_plain(L("CTF & labos autorisés", "CTF & authorised labs", "CTF y labos autorizados", "CTF e labos autorizados", "CTF & autorisierte Labore"))} {chip_plain("MITRE ATT&amp;CK")}</p>
{banner}
<p class="x-lead">{intro}</p>

<h3 class="x-h k-red">{L("Les phases de l'attaque", "The attack phases", "Las fases del ataque", "As fases do ataque", "Die Angriffsphasen")}</h3>
<p class="x-step-note">{tools_note}</p>
{chain}

<h3 class="x-h k-red">{L("Ressources de référence", "Reference resources", "Recursos de referencia", "Recursos de referência", "Referenzmaterial")}</h3>
<ul class="x-rows rt-res k-red">{res_rows}</ul>

<p class="fiche__legal">{L(
    "Comprendre comment une attaque s'organise, c'est aussi savoir la détecter et la bloquer. Voir aussi la page Actus (déroulé type de chaque attaque réelle) et les outils du site.",
    "Understanding how an attack unfolds is also knowing how to detect and block it. See also the News page (the typical sequence of each real attack) and the site's tools.",
    "Entender cómo se organiza un ataque es también saber detectarlo y bloquearlo. Véase también la página de Noticias (el desarrollo típico de cada ataque real) y las herramientas del sitio.",
    "Compreender como se organiza um ataque é também saber detetá-lo e bloqueá-lo. Ver também a página de Notícias (o desenrolar típico de cada ataque real) e as ferramentas do site.",
    "Zu verstehen, wie ein Angriff abläuft, heißt auch, ihn erkennen und blockieren zu können. Siehe auch die News-Seite (der typische Ablauf jedes realen Angriffs) und die Tools der Website.")}</p>"""


def chip_dot(inner):
    return f'<span class="x-chip"><span class="x-dot" aria-hidden="true"></span>{inner}</span>'


def chip_plain(inner):
    return f'<span class="x-chip x-chip--muted x-chip--plain">{inner}</span>'


def main():
    tpl = (ROOT / "about" / "index.html").read_text(encoding="utf-8")
    url = SITE + "/redteam/"
    desc = "Red team methodology cheat-sheet for CTFs and authorised labs: the attack kill chain mapped to MITRE ATT&CK tactics, with the tool families and reference resources of each phase."
    s = re.sub(r"<title[^>]*>.*?</title>",
               '<title data-fr="Red Team :: Manthole — Blog" data-es="Red Team :: Manthole — Blog" data-pt="Red Team :: Manthole — Blog" data-de="Red Team :: Manthole — Blog">Red Team :: Manthole — Blog</title>',
               tpl, count=1, flags=re.S)
    for attr in ['name="description"', 'itemprop="description"', 'name="twitter:description"', 'property="og:description"']:
        s = re.sub(rf'(<meta {attr} content=")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), s, count=1)
    for attr in ['itemprop="name"', 'name="twitter:title"', 'property="og:title"']:
        s = re.sub(rf'(<meta {attr} content=")[^"]*(")', lambda m: m.group(1) + "Red Team" + m.group(2), s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*" />', f'<link rel="canonical" href="{url}" />', s, count=1)
    s = re.sub(r'<meta property="og:url" content="[^"]*" />', f'<meta property="og:url" content="{url}" />', s, count=1)
    title = L("Red Team", "Red Team", "Red Team", "Red Team", "Red Team")
    main_html = (f'<main class="post">\n        <article>\n'
                 f'            <h2 class="post-title"><a href="{url}">{title}</a></h2>\n'
                 f'            <div class="post-content">\n{build_body()}\n            </div>\n'
                 f'        </article>\n    </main>')
    s = re.sub(r'<main class="post"[^>]*>.*?</main>', lambda m: main_html, s, count=1, flags=re.S)
    (ROOT / "redteam").mkdir(exist_ok=True)
    (ROOT / "redteam" / "index.html").write_text(s, encoding="utf-8")
    print("redteam/index.html écrit")


if __name__ == "__main__":
    main()
